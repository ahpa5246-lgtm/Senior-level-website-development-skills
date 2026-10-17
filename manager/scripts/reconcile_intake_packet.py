#!/usr/bin/env python3
"""Review a senior intake handoff against the existing PRIVATE portfolio queue.

No GitHub writes. No Codex dispatch. No model calls. Never logs packet content.
Requires actual local immutable review artifacts matching declared SHA-256.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROLES = ("feasibility", "architecture", "security", "design")
REPO = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/?$")


class PacketError(ValueError):
    pass


def _read_limited(path, max_bytes=500000):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > max_bytes:
        raise PacketError("Missing, symlinked or oversized input")
    return path.read_bytes()


def _artifact(evidence_dir, name, expected):
    if not isinstance(name, str) or not name or "\\" in name:
        raise PacketError("Invalid evidence path")
    rel = Path(name)
    if rel.is_absolute() or ".." in rel.parts:
        raise PacketError("Evidence path escapes its directory")
    root = evidence_dir.resolve(strict=True)
    path = evidence_dir / rel
    for part in (path, *path.parents):
        if part == evidence_dir.parent:
            break
        if part.is_symlink():
            raise PacketError("Symlink in evidence")
    if not path.resolve().is_relative_to(root):
        raise PacketError("Evidence must remain inside evidence folder")
    actual = hashlib.sha256(_read_limited(path)).hexdigest()
    if not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected):
        raise PacketError("Evidence hash missing or malformed")
    if actual != expected:
        raise PacketError("Review evidence hash mismatch")
    return name


def _queue_state(repo, queue):
    # Verify exact GitHub owner/repository boundary in a table row.
    matching = []
    for line in queue.splitlines():
        if not line.lstrip().startswith("|") or f"https://github.com/{repo}" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if any("https://github.com/" + repo + "/" in c for c in cells):
            continue
        if f"https://github.com/{repo}" not in line:
            continue
        found = re.findall(r"\`(NEEDS_AUDIT|AUDITING|AUDITED|READY|IN_PROGRESS|BLOCKED|MANUAL_CLOUD_DELIVERY_REQUIRED|PAUSED_BY_OWNER|AWAITING_HUMAN_REVIEW|OWNER_SUBMISSION|DONE)\`", line)
        if found:
            matching.append(found[0])
    if not matching:
        return None
    if len(matching) > 1:
        raise PacketError("Target repo has ambiguous duplicate queue entries")
    return matching[0]


def reconcile(packet, root, evidence_dir):
    if not isinstance(packet, dict) or packet.get("schema_version") != "1.0":
        raise PacketError("Unsupported packet schema")
    if packet.get("intake_status") != "READY_FOR_PLANNING" or packet.get("release_authorized") is not False:
        raise PacketError("Packet is not review/launch safe")
    permission = packet.get("execution")
    if not isinstance(permission, dict) or any(permission.get(k) is not True for k in (
            "no_auto_merge", "no_auto_deploy", "no_spending", "draft_pr_only")):
        raise PacketError("Missing negative authority controls")
    target = packet.get("target_repo")
    match = REPO.fullmatch(target if isinstance(target, str) else "")
    if not match:
        raise PacketError("Target must be a GitHub repository URL")
    name = match.group(1) + "/" + match.group(2)
    required = ("PROJECT_QUEUE.md", "AUTONOMOUS_TASK_QUEUES.md", "CURRENT_TASK.md", "FACTORY_POLICY.md")
    for f in required:
        if not (root / f).is_file():
            raise PacketError("Missing live private-manager state: " + f)
    queue_text = _read_limited(root / "PROJECT_QUEUE.md").decode("utf-8")
    state = _queue_state(name, queue_text)
    signoffs = packet.get("review_signoffs")
    if not isinstance(signoffs, dict):
        raise PacketError("Four real review files required")
    reviewer_identities = []
    files = []
    for role in ROLES:
        entry = signoffs.get(role)
        if not isinstance(entry, dict) or entry.get("passed") is not True:
            raise PacketError("Reviewer approval missing: " + role)
        reviewer = entry.get("reviewer")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise PacketError("Reviewer identity missing: " + role)
        reviewer_identities.append(reviewer.strip())
        filename = _artifact(evidence_dir, entry.get("artifact_path"), entry.get("artifact_sha256"))
        files.append({"role": role, "file": filename, "sha256": entry["artifact_sha256"]})
    if len(set(reviewer_identities)) != 4:
        raise PacketError("Distinct reviewer identities required")
    # Revalidate the cost report digest in the private manager as well.
    release_mode = packet.get("release_mode")
    if release_mode not in ("private_preview", "public_launch", "internal_production"):
        raise PacketError("Release mode missing or malformed")
    if release_mode != "private_preview":
        cost = packet.get("cost_scenarios_evidence")
        if not isinstance(cost, dict):
            raise PacketError("Public handoff needs actual normal/peak/recovery cost evidence")
        filename = _artifact(evidence_dir, cost.get("artifact_path"), cost.get("artifact_sha256"))
        try:
            report = json.loads(_read_limited(evidence_dir / filename))
        except (ValueError, TypeError):
            raise PacketError("Invalid cost report JSON") from None
        if not isinstance(report, dict) or report.get("status") != "QUOTES_WITHIN_DECLARED_BUDGET":
            raise PacketError("Public cost scenarios not within budget")
        scenarios = report.get("scenarios")
        if (not isinstance(scenarios, dict) or set(scenarios) != {"normal", "peak", "recovery"} or
            any(not isinstance(scenarios[k], dict) or not scenarios[k].get("total_is_complete")
                or scenarios[k].get("over_budget") for k in scenarios)):
            raise PacketError("Cost scenarios missing or incomplete")
        budget = packet.get("monthly_budget")
        if (not isinstance(budget, dict) or report.get("monthly_budget") != budget.get("amount") or
            report.get("currency") != budget.get("currency")):
            raise PacketError("Cost report disagrees with owner budget")
    tasks = packet.get("tasks")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 100:
        raise PacketError("Tasks must be a bounded list")
    seen = set()
    accepted = []
    for item in tasks:
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k].strip()
                                            for k in ("id", "objective", "acceptance", "verification")):
            raise PacketError("Task missing observable acceptance and evidence")
        ident = item["id"]
        if ident in seen or not re.fullmatch(r"[A-Za-z0-9_.-]{2,64}", ident):
            raise PacketError("Duplicate or invalid task ID")
        depends = item.get("depends_on", [])
        if not isinstance(depends, list) or not set(depends).issubset(seen):
            raise PacketError("Unknown or forward/cyclic task dependencies")
        seen.add(ident)
        accepted.append({"id": ident, "objective": item["objective"],
                         "acceptance": item["acceptance"], "verification": item["verification"],
                         "depends_on": depends})
    old_queues = _read_limited(root / "AUTONOMOUS_TASK_QUEUES.md").decode("utf-8")
    for task in accepted:
        if re.search(r"(?<![A-Za-z0-9_.-])" + re.escape(task["id"]) + r"(?![A-Za-z0-9_.-])", old_queues):
            raise PacketError("Potential duplicate milestone ID: " + task["id"])
    # This tool does NOT edit queue, open issue, or enqueue work.
    allowed = state in ("NEEDS_AUDIT", "AUDITED", "READY")
    reasons = []
    if state is None:
        reasons.append("Target not registered; run owner-authorized intake and read-only audit first")
    elif not allowed:
        reasons.append("Current queue status " + state + " requires live supervisor reconciliation or owner decision")
    return {
        "schema_version": "1.0", "project_id": packet.get("project_id"), "target_repository": name,
        "queue_state": state, "status": "READY_FOR_MANAGER_REVIEW" if allowed else "REQUIRES_MANAGER_RECONCILIATION",
        "review_evidence_checked": files, "requested_tasks": accepted, "reasons": reasons,
        "observed_offline_only": True,
        "automatic_dispatch": False, "automatic_merge": False, "automatic_deploy": False,
        "next_step": "Review current live issues/PRs, budget, permissions and protected data before adding to queue.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only packet reconciliation in private manager")
    parser.add_argument("--packet", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--manager-root", default=".")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        target = Path(args.out)
        if target.exists() or target.is_symlink():
            raise PacketError("Output already exists; never overwrite")
        packet = json.loads(_read_limited(Path(args.packet)).decode("utf-8"))
        result = reconcile(packet, Path(args.manager_root), Path(args.evidence_dir))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": result["status"], "tasks": len(result["requested_tasks"]),
                          "report_path": str(target)}, ensure_ascii=False))
        return 0 if result["status"] == "READY_FOR_MANAGER_REVIEW" else 1
    except (OSError, PacketError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)[:250]}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
