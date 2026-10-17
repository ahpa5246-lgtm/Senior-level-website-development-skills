"""Real read-only manager day-plan validation against hashed review evidence."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from plan_reviewed_day import build_day_plan, PacketError, start_utc, status_table

class DayPlannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base=Path(self.tmp.name)
        self.root=base/"manager"
        self.evidence=base/"evidence"
        self.root.mkdir()
        self.evidence.mkdir()
        self._state("READY")
        for filename in ("AUTONOMOUS_TASK_QUEUES.md","CURRENT_TASK.md","FACTORY_POLICY.md"):
            (self.root/filename).write_text("# fixture\n",encoding="utf8")
        signoffs={}
        for role in ("feasibility","architecture","security","design"):
            value=("Synthetic review proof: "+role).encode()
            (self.evidence/(role+".md")).write_bytes(value)
            signoffs[role]={"passed":True,"reviewer":role,"artifact_path":role+".md",
                            "artifact_sha256":hashlib.sha256(value).hexdigest()}
        self.packet={
            "schema_version":"1.0","project_id":"workshops",
            "target_repo":"https://github.com/test-owner/workshops",
            "intake_status":"READY_FOR_PLANNING",
            "release_mode":"private_preview","release_authorized":False,
            "execution":{"no_auto_merge":True,"no_auto_deploy":True,"no_spending":True,
                         "draft_pr_only":True,"max_active_implementations":1},
            "review_signoffs":signoffs,
            "tasks":[
              {"id":"WS-01","objective":"Audit current repo","acceptance":"GitHub baseline and PR audit",
               "verification":"Actual branch + CI evidence","depends_on":[]},
              {"id":"WS-02","objective":"Implement consented test registration",
               "acceptance":"Persists and reloads","verification":"DB and browser tests","depends_on":["WS-01"]},
              {"id":"WS-03","objective":"Review safe rollback",
               "acceptance":"Restored synthetic data","verification":"Recovery drill","depends_on":["WS-02"]}]
        }
    def _state(self,status):
        (self.root/"PROJECT_QUEUE.md").write_text(
          "| 1 | [Workshops](https://github.com/test-owner/workshops) | Web | `"+status+"` | next |\n"
          "| 2 | [Another](https://github.com/test-owner/another) | Web | `READY` | next |\n"
          "| 3 | [Stopped](https://github.com/test-owner/paused) | Web | `PAUSED_BY_OWNER` | stopped |\n",
          encoding="utf8")
    def run_plan(self,minutes=180):
        return build_day_plan(self.packet,self.root,self.evidence,
                              "2026-10-18T09:00:00+03:00",minutes,60,15)
    def test_safe_slots_and_timezone_and_dependency_order(self):
        result=self.run_plan()
        self.assertEqual(result["status"],"REVIEW_ONLY")
        self.assertEqual(result["planned_minutes"],150)
        self.assertEqual(result["start_utc"],"2026-10-18T06:00:00Z")
        self.assertEqual([x["id"] for x in result["slots"]],["WS-01","WS-02"])
        self.assertEqual(result["slots"][1]["proposed_start_utc"],"2026-10-18T07:15:00Z")
        self.assertEqual(result["unscheduled_task_count"],1)
        self.assertFalse(result["automatic_dispatch"])
        self.assertFalse(result["automatic_deploy"])
        self.assertFalse(result["billing_changes"])
        self.assertEqual(result["next_eligible_queues_for_read_only_reinspection"][0]["repository"],"test-owner/another")
        self.assertEqual(result["protected_queues_not_auto_reopened"][0]["state"],"PAUSED_BY_OWNER")
    def test_no_unauthorized_worker_parallelism(self):
        self.packet["execution"]["max_active_implementations"]=2
        with self.assertRaises(PacketError):
            self.run_plan()
    def test_no_automatic_worker_when_pending_human_review(self):
        self._state("AWAITING_HUMAN_REVIEW")
        with self.assertRaisesRegex(PacketError,"blockers"):
            self.run_plan()
    def test_no_duplication_of_existing_task_ids(self):
        (self.root/"AUTONOMOUS_TASK_QUEUES.md").write_text("WS-02 already active")
        with self.assertRaisesRegex(PacketError,"(?i)duplicate"):
            self.run_plan()
    def test_fake_review_hash_blocks_plan(self):
        (self.evidence/"security.md").write_text("tampered")
        with self.assertRaises(PacketError):
            self.run_plan()
    def test_no_partial_first_slot(self):
        with self.assertRaisesRegex(PacketError,"cannot fit"):
            self.run_plan(60)
    def test_invalid_start_timezone(self):
        with self.assertRaises(PacketError):
            start_utc("2026-10-18T09:00")
    def test_weird_state_not_treated_ready(self):
        self._state("IN_PROGRESS")
        with self.assertRaises(PacketError):
            self.run_plan()
    def test_no_spending_with_false_flag(self):
        self.packet["execution"]["no_spending"]=False
        with self.assertRaises(PacketError):
            self.run_plan()
    def test_status_table_not_regex_alone_executable_authority(self):
        rows=status_table("| 1 | https://github.com/test-owner/wow | a | `READY` | x |\n")
        self.assertEqual(rows,[{"repository":"test-owner/wow","state":"READY"}])

if __name__=="__main__":
    unittest.main()
