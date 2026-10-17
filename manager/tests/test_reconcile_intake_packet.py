"""Smoke tests for private manager packet reconciliation (stdlib only)."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reconcile", ROOT / "scripts" / "reconcile_intake_packet.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "manager"
        self.root.mkdir()
        self.evidence = Path(self.temp.name) / "evidence"
        self.evidence.mkdir()
        tick = chr(96)
        (self.root / "PROJECT_QUEUE.md").write_text(
          "| 1 | [Valid](https://github.com/acme/valid) | Web | " + tick + "READY" + tick + " | audit |\n", encoding="utf8"
        )
        for file in ("AUTONOMOUS_TASK_QUEUES.md", "CURRENT_TASK.md", "FACTORY_POLICY.md"):
            (self.root / file).write_text("# fixture\n", encoding="utf8")
        signoffs = {}
        for role in mod.ROLES:
            value = (role + ": reviewed artifact\n").encode()
            (self.evidence / (role + ".md")).write_bytes(value)
            signoffs[role] = {
                "passed": True, "reviewer": role, "artifact_path": role + ".md",
                "artifact_sha256": hashlib.sha256(value).hexdigest()}
        self.packet = {
            "schema_version": "1.0", "project_id": "my-test",
            "target_repo": "https://github.com/acme/valid",
            "intake_status": "READY_FOR_PLANNING", "release_authorized": False,
            "release_mode": "private_preview", "cost_scenarios_evidence": None,
            "execution": {"no_auto_merge": True, "no_auto_deploy": True,
                          "no_spending": True, "draft_pr_only": True},
            "review_signoffs": signoffs,
            "tasks": [{"id": "WEB-T001", "objective": "Persist a workshop signup",
                       "acceptance": "Returns confirmation after refresh",
                       "verification": "DB plus browser test", "depends_on": []}]
        }

    def test_valid_review_only(self):
        report = mod.reconcile(self.packet, self.root, self.evidence)
        self.assertEqual(report["status"], "READY_FOR_MANAGER_REVIEW")
        self.assertFalse(report["automatic_dispatch"])
        self.assertFalse(report["automatic_deploy"])
        self.assertEqual(len(report["review_evidence_checked"]), 4)

    def test_public_launch_needs_cost_scenario_evidence(self):
        self.packet["release_mode"] = "public_launch"
        with self.assertRaises(mod.PacketError):
            mod.reconcile(self.packet, self.root, self.evidence)

    def test_public_launch_rejects_stale_report_hash(self):
        self.packet["release_mode"] = "public_launch"
        self.packet["cost_scenarios_evidence"] = {
            "artifact_path": "cost.json", "artifact_sha256": "b"*64}
        (self.evidence / "cost.json").write_text("{}")
        with self.assertRaises(mod.PacketError):
            mod.reconcile(self.packet, self.root, self.evidence)

    def test_unregistered_repo_never_dispatched(self):
        self.packet["target_repo"] = "https://github.com/acme/new"
        report = mod.reconcile(self.packet, self.root, self.evidence)
        self.assertEqual(report["status"], "REQUIRES_MANAGER_RECONCILIATION")

    def test_existing_waiting_repo_not_overridden(self):
        tick = chr(96)
        (self.root / "PROJECT_QUEUE.md").write_text(
           "| 1 | [Valid](https://github.com/acme/valid) | Web | " + tick + "AWAITING_HUMAN_REVIEW" + tick + " | wait |\n")
        report = mod.reconcile(self.packet, self.root, self.evidence)
        self.assertIn("AWAITING_HUMAN_REVIEW", report["reasons"][0])

    def test_tampered_review_rejected(self):
        (self.evidence / "security.md").write_text("approved but content changed")
        with self.assertRaises(mod.PacketError):
            mod.reconcile(self.packet, self.root, self.evidence)

    def test_symlink_escape_rejected(self):
        original = self.evidence / "design.md"
        original.unlink()
        original.symlink_to(self.root / "CURRENT_TASK.md")
        with self.assertRaises(mod.PacketError):
            mod.reconcile(self.packet, self.root, self.evidence)

    def test_duplicate_task_id_from_queue_rejected(self):
        (self.root / "AUTONOMOUS_TASK_QUEUES.md").write_text("# Past work\nMilestone WEB-T001 has already been assigned.\n")
        with self.assertRaises(mod.PacketError):
            mod.reconcile(self.packet, self.root, self.evidence)

    def test_reviewers_must_be_distinct(self):
        self.packet["review_signoffs"]["security"]["reviewer"] = "architecture"
        with self.assertRaises(mod.PacketError):
            mod.reconcile(self.packet, self.root, self.evidence)

    def test_unknown_dependency_rejected(self):
        self.packet["tasks"][0]["depends_on"] = ["T2"]
        with self.assertRaises(mod.PacketError):
            mod.reconcile(self.packet, self.root, self.evidence)


if __name__ == "__main__":
    unittest.main()
