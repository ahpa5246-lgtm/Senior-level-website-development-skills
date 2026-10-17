"""Adversarial contract tests, using synthetic proof, never a certified UX score."""
import copy
from datetime import date, timedelta
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from visual_quality_gate import check, check_screenshot


def fixture():
    seen=date.today().isoformat()
    return {
      "project":"synthetic-demo", "stage":"planning", "kind":"desktop", "complex_app":True,
      "journeys":[
        {"id":x, "goal":"Complete a real task for "+x+" and verify saved outcome", "surface":x,
         "states":["empty","loading","success","failure"]}
        for x in ("focus","rules","schedule","analytics")],
      "screens":[{"id":x,"purpose":"Separate primary journey "+x,"navigation":"persistent named section"}
                 for x in ("focus","rules","schedule","analytics")],
      "references":[
       {"name":name,"category":cat,"release_status":"released_product",
        "official_url":url,"visual_source_url":url,"observed_on":seen,
        "pattern":"A real user workflow with a clear hierarchy and a secondary settings surface.",
        "tradeoff":"May require a paid tier or a different platform to reproduce."}
       for name,cat,url in [
           ("Cold Turkey","direct","https://getcoldturkey.com/features/"),
           ("Freedom","direct","https://freedom.to/features"),
           ("Opal","aspirational","https://brandkit.opal.so/")]],
      "comparisons":[
         {"journey_id":x,"benchmark":"Cold Turkey",
          "gap":"The primary task currently has too many interspersed unrelated settings.",
          "improvement":"Give this journey a dedicated navigable screen and test navigation.",
          "not_copied":"Use our own brand assets and task vocabulary rather than their artwork."}
         for x in ("focus","rules","schedule","analytics")],
      "design_system":{
         "body_font":"System UI","arabic_font":"system sans Arabic fallback",
         "body_font_license_checked":True, "illustrations_license_checked":True,
         "type_hierarchy":["body","section","title"],"spacing_scale":[4,8,12,16,24],
         "color_roles":{"canvas":"#F9F9FA","surface":"#FFFFFF","text":"#202020",
                        "muted":"#545454","action":"#633CCD","focus":"#513CAB"},
         "illustration_policy":"Use an original 2D illustration only to explain the empty focus state; provide alt text and motion limits.",
         "density_rationale":"Primary focus UI has a single action; analytics and advanced rules are in named secondary destinations."},
      "review":{"design_directions":[
           {"id":"quiet","layout":"Priority content first; sparse active focus screen and named nav."},
           {"id":"editorial","layout":"Editorial layout with strong headings and progressive disclosure."}],
           "selected_direction":"quiet",
           "decision_reason":"Focus users need an obvious primary task and secondary configuration away from timer."}
    }


class CompetitiveGateTests(unittest.TestCase):
    def setUp(self):
        self.d=fixture()
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def run_check(self,data=None):
        return check(data or self.d, evidence_root=self.root)

    def test_structurally_complete_planning_contract(self):
        r=self.run_check()
        self.assertEqual(r["status"],"PASS_EVIDENCE_STRUCTURE")
        self.assertEqual(r["findings"],[])
        self.assertIn("cannot certify",r["limits"])

    def test_screenshot_bypass_and_one_giant_page_blocked(self):
        self.d["screens"]=[{"id":"one"}]
        for j in self.d["journeys"]:
            j["surface"]="one"
        result=self.run_check()
        self.assertIn("ONE_SCREEN_OVERLOAD",{x["code"] for x in result["findings"]})

    def test_two_color_only_directions_do_not_suffice(self):
        self.d["review"]["design_directions"]=[{"id":"same","layout":"Only swap the accent blue"}]
        self.assertIn("ONE_DESIGN_DIRECTION",{x["code"] for x in self.run_check()["findings"]})

    def test_missing_benchmark_and_repeated_fake_website_block(self):
        self.d["references"]=[self.d["references"][0]]
        self.d["references"][0]["release_status"]="portfolio_mockup"
        self.d["references"][0]["official_url"]="http://localhost:8000"
        codes={x["code"] for x in self.run_check()["findings"]}
        self.assertIn("TOO_FEW_REAL_BENCHMARKS",codes)
        self.assertIn("NOT_REAL_PRODUCT",codes)
        self.assertIn("MISSING_OFFICIAL_VISUAL",codes)
        self.assertIn("NOT_ENOUGH_DIRECT_COMPARATORS",codes)

    def test_stale_competitor_research_blocks_new_ui_delivery(self):
        self.d["references"][0]["observed_on"]=(date.today()-timedelta(days=121)).isoformat()
        self.assertIn("STALE_BENCHMARK",{x["code"] for x in self.run_check()["findings"]})

    def test_requires_comparison_for_every_real_journey(self):
        self.d["comparisons"].pop()
        self.assertIn("UNCOMPARED_JOURNEY",{x["code"] for x in self.run_check()["findings"]})

    def test_bad_illustration_policy_cannot_pass(self):
        self.d["design_system"]["illustration_policy"]="cat"
        self.assertIn("DECORATIVE_SLOP",{x["code"] for x in self.run_check()["findings"]})

    def test_no_evidence_cannot_pass_release(self):
        self.d["stage"]="release_review"
        codes={x["code"] for x in self.run_check()["findings"]}
        self.assertIn("NO_IMPLEMENTATION_COMMIT",codes)
        self.assertIn("NO_VERIFIED_SCREENSHOTS",codes)
        self.assertIn("UNTESTED_BREAKPOINTS",codes)
        self.assertIn("NO_USABILITY_TASK_EVIDENCE",codes)

    def test_actual_screenshot_path_proof_stays_within_root(self):
        p=self.root/"artifacts"
        p.mkdir()
        (p/"desktop.png").write_bytes(b"X"*200)
        self.assertTrue(check_screenshot(self.root,"artifacts/desktop.png"))
        self.assertFalse(check_screenshot(self.root,"../secret.png"))
        self.assertFalse(check_screenshot(self.root,"/tmp/secret.png"))
        secret=p/"loop.png"
        secret.symlink_to(p/"desktop.png")
        self.assertFalse(check_screenshot(self.root,"artifacts/loop.png"))

    def test_release_requires_traceable_commit_user_tests_and_screenshots(self):
        self.d["stage"]="implementation"
        screenshot=self.root/"artifacts"
        screenshot.mkdir()
        (screenshot/"focus.png").write_bytes(b"x"*200)
        self.d["review"].update({
          "implemented_commit":"a"*40,"screenshots":["artifacts/focus.png"],
          "tested_surfaces":["desktop","narrow_window"],
          "keyboard_tested":True,"empty_and_error_tested":True,
          "comparison_rechecked_at_commit":True,"arabic_ui":True,"rtl_tested":True,
          "task_test_evidence":"Browser: focus saved, reload persisted. This is a synthetic test-only claim."
        })
        self.assertEqual(self.run_check()["status"],"PASS_EVIDENCE_STRUCTURE")
        self.d["review"]["rtl_tested"]=False
        self.assertIn("RTL_UNVERIFIED",{x["code"] for x in self.run_check()["findings"]})

    def test_corrupt_and_symlink_inputs_rejected(self):
        from visual_quality_gate import safe_read
        p=self.root/"intake.json"
        p.write_text(json.dumps(self.d),encoding="utf-8")
        self.assertEqual(safe_read(p)["project"],"synthetic-demo")
        link=self.root/"linked.json"
        link.symlink_to(p)
        with self.assertRaises(ValueError):
            safe_read(link)


if __name__=="__main__":
    unittest.main()
