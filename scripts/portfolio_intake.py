#!/usr/bin/env python3
"""Fail-closed, stdlib-only intake verifier and supervisor handoff builder.

This tool checks evidence and constraints; it does NOT estimate provider prices,
authorize spending, produce designs, or dispatch Codex. Keep owner answers private.
"""
import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "config" / "20-questions-ar.json"
UNKNOWN = {"", "unknown", "unsure", "not sure", "tbd", "?", "لا اعرف", "ما اعرف", "غير معروف", "غير محدد", "مدري"}
SENSITIVE = ("patient", "medical", "health", "child", "minor", "payment", "credit card", "صحي", "طبي", "اطفال", "أطفال", "حساس")
LIVE = ("live", "stream", "video call", "conference", "webrtc", "بث", "مكالمة", "اتصال فيديو", "ورشة مباشرة")
CURRENCY = re.compile(r"^[A-Z]{3}$")
REPO = re.compile(r"^https://github\.com/[^/\s]+/[^/\s#?]+/?$")
SLUG = re.compile(r"^[a-zA-Z][a-zA-Z0-9._-]{1,63}$")


class IntakeError(ValueError):
    pass


def questionnaire():
    data = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    questions = data["questions"]
    if len(questions) != 20 or [q["id"] for q in questions] != [f"Q{i:02}" for i in range(1, 21)]:
        raise IntakeError("Questionnaire must contain exactly Q01...Q20")
    return questions


def unknown(v):
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip().lower().replace("أ", "ا") in UNKNOWN
    return False


def money(entry, name):
    if not isinstance(entry, dict):
        raise IntakeError(f"{name} must be a money object")
    amount = entry.get("amount")
    unit = entry.get("currency")
    if type(amount) not in (int, float) or not 0 <= amount < 1e10:
        raise IntakeError(f"{name}.amount must be a finite nonnegative number")
    if not isinstance(unit, str) or not CURRENCY.fullmatch(unit):
        raise IntakeError(f"{name}.currency must be an ISO 4217-like three-letter code")
    return {"amount": amount, "currency": unit}


def nonnegative(entry, label):
    if type(entry) not in (int, float) or not 0 <= entry < 1e12:
        raise IntakeError(f"{label} must be a finite nonnegative number")
    return entry


def provider_costs(doc, currency):
    """A quote is a user-verified input. Missing categories remain unpriced."""
    total = 0.0
    receipts = []
    for i, raw in enumerate(doc.get("provider_quotes", [])):
        if not isinstance(raw, dict):
            raise IntakeError("Provider quote must be an object")
        for k in ("component", "currency", "source_url", "checked_on"):
            if not raw.get(k):
                raise IntakeError(f"Quote {i+1} missing {k}")
        if raw["currency"] != currency:
            raise IntakeError("Convert quote currency externally using a cited dated rate; never guess")
        if not str(raw["source_url"]).startswith("https://"):
            raise IntakeError("Provider quotes need an HTTPS source URL")
        try:
            checked = date.fromisoformat(raw["checked_on"])
        except (ValueError, TypeError):
            raise IntakeError("Quote checked_on must be YYYY-MM-DD") from None
        if checked > date.today():
            raise IntakeError("Future-dated quote is invalid")
        fixed = nonnegative(raw.get("fixed_monthly", 0), "fixed_monthly")
        included = nonnegative(raw.get("included_units", 0), "included_units")
        units = nonnegative(raw.get("forecast_units", 0), "forecast_units")
        unit_rate = nonnegative(raw.get("unit_cost", 0), "unit_cost")
        item = round(fixed + max(units - included, 0) * unit_rate, 2)
        total += item
        receipts.append({
            "component": raw["component"],
            "estimate": item,
            "usage_formula": "fixed_monthly + max(forecast_units - included_units, 0) * unit_cost",
            "assumptions": {"forecast_units": units, "included_units": included, "unit_cost": unit_rate},
            "source_url": raw["source_url"], "checked_on": checked.isoformat()
        })
    # No provider price or consumption is invented.
    return round(total, 2), receipts


def assess(doc):
    questions = questionnaire()
    if not isinstance(doc, dict) or not SLUG.fullmatch(str(doc.get("project_id", ""))):
        raise IntakeError("project_id must be a short stable ASCII identifier")
    answers = doc.get("answers", {})
    if not isinstance(answers, dict):
        raise IntakeError("answers must be a Q01...Q20 mapping")
    allowed = {q["id"] for q in questions}
    if set(answers) - allowed:
        raise IntakeError("Unrecognized question IDs")
    missing = [q["id"] for q in questions if unknown(answers.get(q["id"]))]
    critical_missing = [q["id"] for q in questions if q["critical"] and q["id"] in missing]
    blockers = []
    warnings = []
    for qid in critical_missing:
        blockers.append({"code": "CRITICAL_ANSWER_MISSING", "field": qid, "reason": "Owner clarification required"})
    for qid in missing:
        if qid not in critical_missing:
            warnings.append({"code": "NONCRITICAL_UNKNOWN", "field": qid})
    exposure = str(doc.get("release_mode", "")).lower()
    preview = exposure == "private_preview"
    if exposure not in ("private_preview", "public_launch", "internal_production"):
        blockers.append({"code": "RELEASE_MODE_UNRESOLVED", "reason": "Set release_mode"})
    budget = None
    try:
        budget = money(doc.get("monthly_budget"), "monthly_budget")
        setup = money(doc.get("one_time_budget"), "one_time_budget")
        if budget["currency"] != setup["currency"]:
            raise IntakeError("Budget currencies must match or be converted with evidenced rate")
    except IntakeError as exc:
        blockers.append({"code": "BUDGET_UNRESOLVED", "reason": str(exc)})
        setup = None
    expected = doc.get("expected", {})
    if not isinstance(expected, dict):
        raise IntakeError("expected must be an object")
    for key in ("monthly_users", "peak_concurrent"):
        if key not in expected:
            blockers.append({"code": "LOAD_UNRESOLVED", "field": key, "reason": "Use an approximate range or conservative assumption"})
        else:
            nonnegative(expected[key], key)
    refs = doc.get("reference_repositories", [])
    if not isinstance(refs, list):
        raise IntakeError("reference_repositories must be a list")
    for repo in refs:
        if not isinstance(repo, dict) or not REPO.fullmatch(str(repo.get("url", ""))):
            raise IntakeError("Reference repositories require a standard GitHub URL")
        if repo.get("license_checked") is not True or not repo.get("version_checked"):
            warnings.append({"code": "REFERENCE_NOT_APPROVED_FOR_REUSE", "repository": repo["url"], "action": "study only; do not copy code"})
    total, receipts = (0, [])
    if budget is not None:
        total, receipts = provider_costs(doc, budget["currency"])
        needs = set(doc.get("cost_components", []))
        quoted = {r["component"] for r in receipts}
        unpriced = sorted(needs - quoted)
        if unpriced:
            warnings.append({"code": "UNPRICED_COMPONENTS", "components": unpriced,
                             "reason": "A missing quote does NOT have a zero price"})
            if not preview:
                blockers.append({"code": "COST_EVIDENCE_MISSING", "components": unpriced})
        if not receipts:
            warnings.append({"code": "NO_VERIFIED_PRICES", "reason": "Cannot claim zero cost or any hosting price"})
            if not preview:
                blockers.append({"code": "NO_COST_EVIDENCE"})
        if receipts and total > budget["amount"]:
            blockers.append({"code": "BUDGET_EXCEEDED", "quoted_monthly": total, "budget": budget["amount"]})
    else:
        unpriced = list(doc.get("cost_components", []))
    # Natural-language keyword checks are not reliable classifiers of sensitive data.
    # A separate agent/owner must explicitly classify these risks; production fails closed.
    flags = doc.get("risk_flags", {})
    if not isinstance(flags, dict):
        raise IntakeError("risk_flags must be a structured object")
    for key in ("real_sensitive_data", "live_media", "payments", "physical_control"):
        value = flags.get(key)
        if type(value) is not bool:
            if preview:
                warnings.append({"code": "RISK_UNCLASSIFIED", "field": key})
            else:
                blockers.append({"code": "RISK_UNCLASSIFIED", "field": key})
    for key, record in (
        ("real_sensitive_data", "specialist_review_record"),
        ("live_media", "media_capacity_evidence"),
        ("payments", "payment_integrity_evidence"),
        ("physical_control", "physical_safety_review")
    ):
        if flags.get(key) is True:
            warnings.append({"code": "HIGH_RISK_FEATURE", "field": key})
            if not preview and not doc.get(record):
                blockers.append({"code": "RISK_EVIDENCE_MISSING", "field": key, "evidence": record})
    features = answers.get("Q05", "")
    status = "NEEDS_INPUT" if critical_missing or exposure not in ("private_preview", "public_launch", "internal_production") or budget is None else ("NEEDS_EVIDENCE" if blockers else "READY_FOR_PLANNING")
    # READY_FOR_PLANNING is NOT permission to release, spend, merge or deploy.
    return {
        "schema_version": "1.0", "project_id": doc["project_id"],
        "status": status, "kind": doc.get("kind", "web"),
        "complete_questions": 20 - len(missing), "total_questions": 20,
        "clarify": missing, "blockers": blockers, "warnings": warnings,
        "business_outcome": answers.get("Q04", ""), "declared_features": features,
        "reference_repositories": refs,
        "budget": budget, "one_time_budget": setup,
        "estimate": {
            "monthly_quoted_subtotal": total if receipts else None,
            "currency": budget["currency"] if budget else None,
            "priced_components": receipts, "unpriced_components": unpriced,
            "not_included": ["uncited infrastructure", "taxes", "overages", "domain renewal if unquoted", "support labor", "incident recovery"],
            "policy": "Estimate from owner-supplied dated verified quotes only; test normal and burst scenarios before approving production."
        },
        "discovery": {"expected": expected, "preview_only": preview, "release_mode": exposure},
        "next_action": "Clarify and collect missing evidence" if blockers else "Independent skeptic + design + engineering review",
        "implementation_authorized": False, "release_authorized": False
    }


def check_review_bytes(doc, evidence_dir):
    """Verify recorded review files, not self-declared hash strings alone."""
    import hashlib
    if evidence_dir is None:
        raise IntakeError("Packet requires --evidence-dir with real reviewer files")
    root = Path(evidence_dir)
    if root.is_symlink() or not root.is_dir():
        raise IntakeError("Evidence directory missing or symlinked")
    resolved = root.resolve()
    for role in ("feasibility", "architecture", "security", "design"):
        entry = doc["review_signoffs"][role]
        relative = entry.get("artifact_path")
        if not isinstance(relative, str) or not relative or "\\\\" in relative:
            raise IntakeError("Review requires a relative artifact_path")
        rel = Path(relative)
        if rel.is_absolute() or ".." in rel.parts:
            raise IntakeError("Review file path escapes evidence directory")
        path = root / rel
        if any(p.is_symlink() for p in (path, *path.parents) if p != root.parent):
            raise IntakeError("Symlinked review files are forbidden")
        if not path.resolve().is_relative_to(resolved) or not path.is_file() or path.stat().st_size > 500000:
            raise IntakeError("Review file missing, too large or outside evidence directory")
        evidence = path.read_bytes()
        if not evidence or hashlib.sha256(evidence).hexdigest() != entry["artifact_sha256"]:
            raise IntakeError("Review artifact hash mismatch: " + role)


def manager_packet(doc, assessment, evidence_dir=None):
    if assessment["status"] != "READY_FOR_PLANNING":
        raise IntakeError("Fail closed: owner constraints not resolved; cannot prepare manager packet")
    signoffs = doc.get("review_signoffs")
    if not isinstance(signoffs, dict):
        raise IntakeError("Four evidence-backed reviews required")
    for role in ("feasibility", "architecture", "security", "design"):
        item = signoffs.get(role)
        if not isinstance(item, dict) or item.get("passed") is not True:
            raise IntakeError("Missing review signoff: " + role)
        if not isinstance(item.get("artifact_url"), str) or not item["artifact_url"].startswith("https://"):
            raise IntakeError("Review artifact HTTPS link required: " + role)
        if not re.fullmatch(r"[a-f0-9]{64}", str(item.get("artifact_sha256", ""))):
            raise IntakeError("Review artifact SHA256 required: " + role)
        if not str(item.get("reviewer", "")).strip():
            raise IntakeError("Reviewer identity required: " + role)
    target_repo = doc.get("target_repo")
    if not isinstance(target_repo, str) or not REPO.fullmatch(target_repo):
        raise IntakeError("A reviewed concrete target GitHub repository is required")
    reviewers = [signoffs[role]["reviewer"] for role in ("feasibility", "architecture", "security", "design")]
    if len(set(reviewers)) != 4:
        raise IntakeError("Reviews require distinct declared reviewer identities")
    check_review_bytes(doc, evidence_dir)
    plan = doc.get("execution_tasks")
    if not isinstance(plan, list) or not plan:
        raise IntakeError("Planner must supply actual specific acceptance-tested tasks; no generic auto-generated task queue")
    seen = set()
    for task in plan:
        if not isinstance(task, dict) or any(not isinstance(task.get(k), str) or not task[k].strip() for k in ("id", "objective", "acceptance", "verification")):
            raise IntakeError("Each task needs id, objective, acceptance and verification")
        if task["id"] in seen:
            raise IntakeError("Duplicate task ID")
        if not set(task.get("depends_on", [])).issubset(seen):
            raise IntakeError("Dependencies must appear earlier; no cycles or unknown IDs")
        seen.add(task["id"])
    return {
        "schema_version": "1.0", "project_id": doc["project_id"],
        "target_repo": doc.get("target_repo"),
        "intake_status": assessment["status"],
        "monthly_budget": assessment["budget"], "cost_basis": assessment["estimate"],
        "review_signoffs": doc["review_signoffs"], "tasks": plan,
        "execution": {
            "max_active_implementations": 1,
            "no_auto_merge": True, "no_auto_deploy": True,
            "no_spending": True, "no_secret_access": True,
            "draft_pr_only": True,
            "blocked_task_failover": True,
            "schedule_is_not_a_guarantee_of_completion": True
        },
        "human_approval_needed": ["production deployment", "cost commitments", "merge", "secrets", "data migrations", "external publication"],
        "release_authorized": False
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Project intake and fail-closed manager handoff")
    cmd = parser.add_subparsers(dest="command", required=True)
    questions = cmd.add_parser("questions")
    questions.add_argument("--json", action="store_true")
    for op in ("assess", "packet"):
        sub = cmd.add_parser(op)
        sub.add_argument("--input", required=True)
        sub.add_argument("--output")
        if op == "packet":
            sub.add_argument("--evidence-dir", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "questions":
            qs = questionnaire()
            if args.json:
                print(json.dumps(qs, ensure_ascii=False, indent=2))
            else:
                for q in qs:
                    print(f'{q["id"]}: {q["prompt"]}')
            return 0
        path = Path(args.input)
        doc = json.loads(path.read_text(encoding="utf-8"))
        decision = assess(doc)
        result = decision if args.command == "assess" else manager_packet(doc, decision, args.evidence_dir)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            target = Path(args.output)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(payload, encoding="utf-8")
        else:
            print(payload)
        return 0 if args.command == "packet" or result["status"] == "READY_FOR_PLANNING" else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        # Avoid echoing user answers or file contents into CI logs.
        print(json.dumps({"status": "ERROR", "error_type": type(exc).__name__, "reason": str(exc)[:300]}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
