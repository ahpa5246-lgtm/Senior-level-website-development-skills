"""Integration checks for independent GitHub and cost report attachment."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import project_conductor as conductor
from report_merger import combine_evidence,describe_evidence

class MergerTests(unittest.TestCase):
    def setUp(self):
        self.owner=json.loads((ROOT/"examples/zero-budget-demo.intake.json").read_text(encoding="utf-8"))
        self.base=conductor.evaluate(self.owner)
        self.refs={"candidates":[{"url":"https://github.com/example/well-documented",
                     "ref":{"commit_sha":"a"*40},
                     "license":{"spdx_id":"MIT"},
                     "functional_match":{"verified":False},
                     "economics":{"hosting_cost_verified":False}}]}
        self.cost={"currency":"USD","monthly_budget":0,
          "status":"QUOTES_WITHIN_DECLARED_BUDGET","unpriced":[],"alerts":[],
          "scenarios":{x:{"quoted_total":0.0,"total_is_complete":True,"over_budget":False}
                       for x in ("normal","peak","recovery")}}
    def test_good_documents_do_not_grant_source_reuse_or_spend(self):
        r=combine_evidence(self.base,self.refs,self.cost)
        self.assertFalse(r["researched_candidates"][0]["functional_match_verified"])
        self.assertFalse(r["researched_candidates"][0]["security_audited"])
        self.assertEqual(r["researched_candidates"][0]["reuse_decision"],"STUDY_ONLY_PENDING_REVIEW")
        self.assertFalse(r["cost_scenarios"]["provider_prices_independently_verified"])
        self.assertFalse(r["cost_scenarios"]["release_authorized"])
        self.assertFalse(r["implementation_authorized"])
        self.assertIn("GitHub",describe_evidence(r))
        self.assertIn("normal",conductor.markdown_owner_report(r))
    def test_missing_price_has_named_blocker_not_zero(self):
        self.cost["scenarios"]["peak"]["quoted_total"]=None
        self.cost["scenarios"]["peak"]["total_is_complete"]=False
        self.cost["status"]="NEEDS_COST_EVIDENCE_OR_REDESIGN"
        r=combine_evidence(self.base,None,self.cost)
        self.assertIn("COST_SCENARIO_BLOCKER",{x["code"] for x in r["skeptical_findings"]})
        self.assertIn("غير قابل للحساب",describe_evidence(r))
    def test_budget_mismatch_fails_closed(self):
        self.cost["monthly_budget"]=25
        with self.assertRaisesRegex(ValueError,"budget"):
            combine_evidence(self.base,None,self.cost)
    def test_repository_missing_commit_not_approved(self):
        self.refs["candidates"][0]["ref"]["commit_sha"]="main"
        with self.assertRaises(ValueError):
            combine_evidence(self.base,self.refs)
    def test_command_attaches_both_reports_and_markdown(self):
        with tempfile.TemporaryDirectory() as p:
            folder=Path(p)
            for name,obj in (("intake",self.owner),("references",self.refs),("cost",self.cost)):
                (folder/(name+".json")).write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")
            out=folder/"merged.json"
            md=folder/"merged.md"
            code=conductor.main(["blueprint","--input",str(folder/"intake.json"),
              "--references-file",str(folder/"references.json"),"--cost-file",str(folder/"cost.json"),
              "--out",str(out),"--markdown-out",str(md)])
            self.assertEqual(code,0)
            self.assertIn("cost_scenarios",json.loads(out.read_text()))
            self.assertIn("GitHub",md.read_text(encoding="utf-8"))
if __name__=="__main__":
    unittest.main()
