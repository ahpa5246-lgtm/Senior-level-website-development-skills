"""Executable checks for the project intake safety boundary."""
import copy
import hashlib
import tempfile
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("portfolio_intake", ROOT / "scripts" / "portfolio_intake.py")
intake = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = intake
spec.loader.exec_module(intake)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / "examples" / "zero-budget-demo.intake.json").read_text(encoding="utf-8"))

    def attach_real_reviews(self):
        self.evidence_temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.evidence_temp.cleanup)
        root = Path(self.evidence_temp.name)
        self.doc["review_signoffs"] = {}
        for role in ("feasibility", "architecture", "security", "design"):
            value = (role + ": independently reviewed\n").encode()
            (root / (role + ".md")).write_bytes(value)
            self.doc["review_signoffs"][role] = {
                "passed": True, "reviewer": role + "_reviewer",
                "artifact_url": "https://github.com/example/private-review",
                "artifact_path": role + ".md",
                "artifact_sha256": hashlib.sha256(value).hexdigest()
            }
        return root

    def test_twenty_unique_questions(self):
        qs = intake.questionnaire()
        self.assertEqual(len(qs), 20)
        self.assertEqual([q["id"] for q in qs], [f"Q{x:02d}" for x in range(1, 21)])

    def test_private_preview_explicitly_unpriced(self):
        result = intake.assess(self.doc)
        self.assertEqual(result["status"], "READY_FOR_PLANNING")
        self.assertIsNone(result["estimate"]["monthly_quoted_subtotal"])
        self.assertTrue(result["estimate"]["unpriced_components"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["implementation_authorized"])

    def test_public_release_requires_provider_evidence(self):
        self.doc["release_mode"] = "public_launch"
        result = intake.assess(self.doc)
        self.assertEqual(result["status"], "NEEDS_EVIDENCE")
        self.assertIn("NO_COST_EVIDENCE", {b["code"] for b in result["blockers"]})

    def test_unanswered_critical_questions_block(self):
        self.doc["answers"]["Q08"] = "unknown"
        self.doc["answers"]["Q12"] = "مدري"
        result = intake.assess(self.doc)
        self.assertEqual(result["status"], "NEEDS_INPUT")
        self.assertEqual(set(result["clarify"]), {"Q08", "Q12"})

    def test_unknown_price_is_not_zero(self):
        self.doc["provider_quotes"] = [{"component": "static_host", "currency": "USD",
           "fixed_monthly": 0, "unit_cost": 0.1, "forecast_units": 100, "included_units": 5,
           "checked_on": "2026-10-01", "source_url": "https://example.com/pricing"}]
        result = intake.assess(self.doc)
        self.assertEqual(result["estimate"]["monthly_quoted_subtotal"], 9.5)
        self.assertEqual(set(result["estimate"]["unpriced_components"]), {"database", "transactional_email"})
        self.assertIn("BUDGET_EXCEEDED", {b["code"] for b in result["blockers"]})

    def test_wrong_currency_quote_fails(self):
        self.doc["provider_quotes"] = [{"component": "static_host", "currency": "IQD",
          "source_url": "https://example.com/pricing", "checked_on": "2026-10-01"}]
        with self.assertRaises(intake.IntakeError):
            intake.assess(self.doc)

    def test_unlicensed_reference_study_only(self):
        self.doc["reference_repositories"] = [{"url": "https://github.com/example/project",
                                                "license_checked": False}]
        result = intake.assess(self.doc)
        self.assertIn("REFERENCE_NOT_APPROVED_FOR_REUSE", {w["code"] for w in result["warnings"]})

    def test_packet_rejects_missing_signed_reviews(self):
        assessment = intake.assess(self.doc)
        self.doc["execution_tasks"] = [{"id": "T1", "objective": "Implement registration",
          "acceptance": "Persist a real registration", "verification": "Run Playwright after database integration"}]
        with self.assertRaises(intake.IntakeError):
            intake.manager_packet(self.doc, assessment)

    def test_packet_rejects_duplicate_or_forward_tasks(self):
        self.doc["review_signoffs"] = {
           role: {"passed": True, "reviewer": role + "_reviewer",
                  "artifact_url": "https://github.com/example/private-review",
                  "artifact_sha256": "a"*64}
           for role in ("feasibility", "architecture", "security", "design")
        }
        self.doc["execution_tasks"] = [
          {"id": "T1", "objective": "UI", "acceptance": "Loads", "verification": "Playwright", "depends_on": ["T2"]},
          {"id": "T2", "objective": "DB", "acceptance": "Persists", "verification": "DB integration"}]
        with self.assertRaises(intake.IntakeError):
            intake.manager_packet(self.doc, intake.assess(self.doc))

    def test_valid_packet_keeps_mutation_gate_closed(self):
        directory = self.attach_real_reviews()
        self.doc["execution_tasks"] = [
           {"id": "T1", "objective": "Build real registration flow",
            "acceptance": "User can register once and see confirmation after refresh",
            "verification": "DB integration plus browser smoke", "depends_on": []}]
        p = intake.manager_packet(self.doc, intake.assess(self.doc), directory)
        self.assertEqual(len(p["tasks"]), 1)
        self.assertTrue(p["execution"]["draft_pr_only"])
        self.assertFalse(p["release_authorized"])

    def test_packet_denies_tampered_review_evidence(self):
        directory = self.attach_real_reviews()
        self.doc["execution_tasks"] = [
            {"id": "T1", "objective": "Something", "acceptance": "Observable action",
             "verification": "Test", "depends_on": []}
        ]
        (directory / "security.md").write_text("changed after approval")
        with self.assertRaises(intake.IntakeError):
            intake.manager_packet(self.doc, intake.assess(self.doc), directory)

    def test_packet_denies_missing_review_directory(self):
        self.attach_real_reviews()
        self.doc["execution_tasks"] = [
            {"id": "T1", "objective": "Something", "acceptance": "Observable action",
             "verification": "Test", "depends_on": []}
        ]
        with self.assertRaises(intake.IntakeError):
            intake.manager_packet(self.doc, intake.assess(self.doc))

    def test_public_risk_classification_is_required_even_if_price_is_known(self):
        self.doc["release_mode"] = "public_launch"
        self.doc.pop("risk_flags")
        result = intake.assess(self.doc)
        self.assertIn("RISK_UNCLASSIFIED", {b["code"] for b in result["blockers"]})

    def test_sensitive_public_launch_requires_specialist_record(self):
        self.doc["release_mode"] = "public_launch"
        self.doc["risk_flags"]["real_sensitive_data"] = True
        result = intake.assess(self.doc)
        self.assertIn("RISK_EVIDENCE_MISSING", {b["code"] for b in result["blockers"]})

    def test_distinct_reviewers_mandatory(self):
        self.doc["review_signoffs"] = {
           role: {"passed": True, "reviewer": "same-reviewer",
                  "artifact_url": "https://github.com/example/private-review",
                  "artifact_sha256": "a"*64}
           for role in ("feasibility", "architecture", "security", "design")
        }
        self.doc["execution_tasks"] = [
           {"id": "T1", "objective": "Deliver real flow", "acceptance": "Persist",
            "verification": "DB integration", "depends_on": []}]
        with self.assertRaises(intake.IntakeError):
            intake.manager_packet(self.doc, intake.assess(self.doc))

if __name__ == "__main__":
    unittest.main()
