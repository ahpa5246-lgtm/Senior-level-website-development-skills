"""Behavioral checks: uncertainty, expense gates and safe review-only outputs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import project_conductor as c

class ConductorTests(unittest.TestCase):
    def setUp(self):
        self.doc=json.loads((ROOT/"examples/zero-budget-demo.intake.json").read_text(encoding="utf-8"))

    def test_books_and_sketches_are_gates_not_copyrighted_reprints(self):
        d=json.loads((ROOT/"config/senior-gates.json").read_text())
        self.assertGreaterEqual(len(d["gates"]),15)
        self.assertEqual(len(set(x["id"] for x in d["gates"])),len(d["gates"]))
        refs="/".join(x["source"] for x in d["gates"])
        for name in ("D","G","H","M","A"):
            self.assertIn(name,refs)
        for row in d["gates"]:
            self.assertIn(row["when"],("always","accounts","persistence","media","payments","sensitive","physical"))
            self.assertTrue(all(row.get(k) for k in ("test","failure","evidence","pitfalls")))
            self.assertRegex(row["pitfalls"],r"^\d{1,3}-\d{1,3}$")

    def test_incomplete_uncertain_capability_never_authorizes_work(self):
        out=c.evaluate(self.doc)
        self.assertEqual(out["assessment_status"],"READY_FOR_PLANNING")
        self.assertEqual(out["architecture"]["provisional_direction"],"UNDECIDED")
        self.assertFalse(out["spending_authorized"])
        self.assertFalse(out["deployment_authorized"])
        self.assertFalse(out["manager_packet_issued"])
        self.assertTrue(any(x["code"]=="UNCLASSIFIED_TRUST_BOUNDARY" for x in out["skeptical_findings"]))
        self.assertIsNone(out["owner_safe_summary"]["quoted_total"])
        self.assertTrue(any(g["applicability"]=="CONDITIONAL_UNKNOWN" for g in out["conditional_gates"]))
        self.assertTrue(all(t["state"]=="DRAFT_NOT_AUTHORIZED" for t in out["plan_draft"]))

    def test_static_no_accounts_or_persistence_reduces_tasks(self):
        self.doc["capabilities"]={"accounts":False,"persistence":False}
        self.doc["risk_flags"]={"real_sensitive_data":False,"live_media":False,"payments":False,"physical_control":False}
        out=c.evaluate(self.doc)
        self.assertEqual(out["architecture"]["provisional_direction"],"STATIC_FIRST")
        keys=[t["id"] for t in out["plan_draft"]]
        self.assertFalse(any(x.endswith("-AUTH") or x.endswith("-DATA") for x in keys))
        self.assertEqual(len(out["plan_draft"]),9)
        self.assertEqual(len(out["conditional_gates"]),9)

    def test_sensitive_real_time_plan_adds_security_and_data_work(self):
        self.doc["capabilities"]={"accounts":True,"persistence":True}
        self.doc["risk_flags"]={"real_sensitive_data":True,"live_media":True,"payments":True,"physical_control":False}
        out=c.evaluate(self.doc)
        labels={g["id"] for g in out["conditional_gates"]}
        for item in ("G07","G08","G09","G10","G11"):
            self.assertIn(item,labels)
        self.assertIn("VIDEO_BUILD_OR_INTEGRATE",{p["code"] for p in out["question_followups"]})
        self.assertTrue(any(x["code"]=="ZERO_BUDGET" for x in out["question_followups"]))
        self.assertTrue(any(x["id"].endswith("-AUTH") for x in out["plan_draft"]))
        self.assertTrue(any(x["id"].endswith("-DATA") for x in out["plan_draft"]))

    def test_task_draft_depends_only_on_prior_ids_and_is_packet_compatible(self):
        rows=c.evaluate(self.doc)["plan_draft"]
        seen=set()
        for row in rows:
            self.assertTrue(set(row["depends_on"]).issubset(seen))
            self.assertTrue(all(isinstance(row[x],str) and row[x] for x in ("id","objective","acceptance","verification")))
            seen.add(row["id"])

    def test_invalid_unknown_capability_never_guessed(self):
        self.doc["capabilities"]={"accounts":"sure","persistence":True}
        with self.assertRaisesRegex(ValueError,"Capability"):
            c.evaluate(self.doc)

    def test_book_gates_do_not_claim_passed(self):
        self.assertTrue(all(g["status"]=="NOT_TESTED" for g in c.evaluate(self.doc)["conditional_gates"]))

    def test_wizard_collects_exactly_twenty_and_keeps_private_data_outside_repo(self):
        answers=iter(["موقع ورشات","مشروع لفريق طلابي","طلاب","التسجيل وتأكيده","حجز وحضور",
          "100","10","0 USD","0 USD","شهر","بلا حساب","اسم وبريد","لا",
          "رابط ورشة خارجي","ثلاثة أشهر","مسؤول الفريق","هاتف","عربي","عضو الفريق","تجريبي"])
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"private-intake.json"
            doc=c.interactive("sample-workshop",path,lambda prompt:next(answers),lambda msg:None)
            self.assertEqual(len(doc["answers"]),20)
            self.assertEqual(doc["expected"]["monthly_users"],100)
            self.assertEqual(doc["monthly_budget"]["amount"],0)
            self.assertEqual(doc["release_mode"],"private_preview")
            self.assertIsNone(doc["risk_flags"]["payments"])
            self.assertTrue(path.exists())
            with self.assertRaises(ValueError):
                c.write_new(path,doc)

    def test_inside_public_repository_is_denied(self):
        with self.assertRaisesRegex(ValueError,"OUTSIDE"):
            c.safe_output(ROOT/"private-secrets.json")

    def test_ranges_not_silently_guessed(self):
        self.assertIsNone(c.try_load("100-300"))
        self.assertIsNone(c.try_amount("اربعين دولار"))
        self.assertEqual(c.try_amount("0 IQD")["currency"],"IQD")

if __name__=="__main__":
    unittest.main()
