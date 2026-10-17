#!/usr/bin/env python3
"""Read-only daily work plan from an already reviewed PRIVATE senior intake packet.

No Codex dispatch, no billing, no timestamps promised as executed, no GitHub
writes, no scheduler installation and no automatic change of PROJECT_QUEUE.
Only a verified private manager may later authorize bounded implementation.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from reconcile_intake_packet import PacketError, reconcile, _read_limited

MAX_DAY_MINUTES = 8 * 60
REVIEW_BUFFER_MINUTES = 15
ELIGIBLE = {"NEEDS_AUDIT", "AUDITED", "READY"}
FORBIDDEN = {"PAUSED_BY_OWNER", "BLOCKED", "MANUAL_CLOUD_DELIVERY_REQUIRED",
             "AWAITING_HUMAN_REVIEW", "IN_PROGRESS", "OWNER_SUBMISSION", "DONE"}


def start_utc(value):
    try:
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError):
        raise PacketError("Use an ISO8601 offset-aware --start (e.g. 2026-10-18T08:00:00+03:00)") from None
    if value.tzinfo is None or value.utcoffset() is None:
        raise PacketError("Start time needs an explicit timezone")
    return value.astimezone(timezone.utc)


def bounded_int(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise PacketError(name + " out of safe range")
    return value


def status_table(text):
    """Parse only exactly shaped GitHub-URL queue rows; never assign paused work."""
    result = []
    for line in text.splitlines():
        if not line.strip().startswith("|") or "https://github.com/" not in line:
            continue
        repo = re.search(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?![A-Za-z0-9_.-])", line)
        states = re.findall(r"\`(NEEDS_AUDIT|AUDITING|AUDITED|READY|IN_PROGRESS|BLOCKED|MANUAL_CLOUD_DELIVERY_REQUIRED|PAUSED_BY_OWNER|AWAITING_HUMAN_REVIEW|OWNER_SUBMISSION|DONE)\`", line)
        if repo and len(states) == 1 and repo.group(1) not in {x["repository"] for x in result}:
            result.append({"repository": repo.group(1), "state": states[0]})
    return result


def build_day_plan(packet, root, evidence_dir, start, available_minutes=240,
                   milestone_minutes=60, review_minutes=15):
    bounded_int(available_minutes, "available_minutes", 30, MAX_DAY_MINUTES)
    bounded_int(milestone_minutes, "milestone_minutes", 15, 180)
    bounded_int(review_minutes, "review_minutes", 5, 60)
    start = start_utc(start)
    proof = reconcile(packet, root, evidence_dir)  # digest/queue/duplicate checks
    if proof["status"] != "READY_FOR_MANAGER_REVIEW":
        raise PacketError("Manager reconciliation has blockers; cannot propose a daily run")
    if proof["queue_state"] not in ELIGIBLE:
        raise PacketError("Target state not eligible for work")
    if packet.get("release_authorized") is not False or packet.get("execution", {}).get("no_spending") is not True:
        raise PacketError("Missing negative execution rights")
    if packet.get("execution", {}).get("max_active_implementations") != 1:
        raise PacketError("Manager supports exactly one global implementation")
    queue = status_table(_read_limited(root / "PROJECT_QUEUE.md").decode("utf-8"))
    allocated = 0
    planned = []
    planned_ids = set()
    for task in proof["requested_tasks"]:
        dependencies = set(task.get("depends_on", []))
        if not dependencies.issubset(planned_ids):
            # Earlier unscheduled task blocks this task (no dependency skipping).
            continue
        cost = milestone_minutes + review_minutes
        if cost + allocated > available_minutes:
            break
        at = start + timedelta(minutes=allocated)
        planned.append({
            "id": task["id"], "objective": task["objective"],
            "acceptance": task["acceptance"], "verification": task["verification"],
            "depends_on": task["depends_on"],
            "proposed_start_utc": at.isoformat().replace("+00:00", "Z"),
            "proposed_finish_utc": (at + timedelta(minutes=cost)).isoformat().replace("+00:00", "Z"),
            "implementation_minutes_budget": milestone_minutes,
            "review_minutes_budget": review_minutes,
            "state": "PROPOSAL_ONLY_NOT_DISPATCHED",
            "handoff_when_blocked": "Checkpoint; preserve exact failure and CI evidence; do not repeat equivalent Codex start"
        })
        allocated += cost
        planned_ids.add(task["id"])
    # A failover suggestion is NOT queue mutation/owner authorization.
    eligible_elsewhere = [q for q in queue
                          if q["repository"] != proof["target_repository"] and q["state"] in ELIGIBLE]
    forbidden = [q for q in queue if q["state"] in FORBIDDEN]
    if not planned:
        raise PacketError("Time budget cannot fit first milestone plus review; no safe plan")
    return {
        "schema_version": "1.0", "status": "REVIEW_ONLY",
        "target_repository": proof["target_repository"],
        "queue_state_observed_offline": proof["queue_state"],
        "packet_project_id": packet.get("project_id"),
        "start_utc": start.isoformat().replace("+00:00", "Z"),
        "available_minutes": available_minutes,
        "planned_minutes": allocated,
        "unassigned_minutes": available_minutes - allocated,
        "slots": planned, "unscheduled_task_count": len(proof["requested_tasks"]) - len(planned),
        "next_eligible_queues_for_read_only_reinspection": eligible_elsewhere,
        "protected_queues_not_auto_reopened": forbidden,
        "limits": ["Times are illustrative, not scheduled events",
                   "Real GitHub state, Codex quotas, PRs, CI and reviewer approvals MUST be checked at dispatch",
                   "Never start a second concurrent Codex implementation",
                   "Do not merge, deploy, purchase, reveal secrets or bypass usage limits",
                   "No automatic project switch without live authorization/queue reconciliation"],
        "automatic_dispatch": False, "automatic_merge": False,
        "automatic_deploy": False, "billing_changes": False
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Propose safe day slots for reviewed private packet; never dispatches")
    parser.add_argument("--packet", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--manager-root", default=".")
    parser.add_argument("--start", required=True, help="ISO8601 with offset, e.g. 2026-10-18T09:00+03:00")
    parser.add_argument("--minutes", type=int, default=240)
    parser.add_argument("--milestone-minutes", type=int, default=60)
    parser.add_argument("--review-minutes", type=int, default=15)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        target = Path(args.out)
        if target.exists() or target.is_symlink():
            raise PacketError("Output already exists, refusing overwrite")
        packet = json.loads(_read_limited(Path(args.packet)))
        result = build_day_plan(packet, Path(args.manager_root), Path(args.evidence_dir),
                                args.start, args.minutes, args.milestone_minutes, args.review_minutes)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as out:
            json.dump(result, out, ensure_ascii=False, indent=2)
            out.write("\n")
        print(json.dumps({"status":result["status"], "proposed_slots":len(result["slots"]),
                          "planned_minutes":result["planned_minutes"], "output":str(target)},
                         ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status":"BLOCKED", "type":type(exc).__name__,
                          "reason":str(exc)[:170]}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
