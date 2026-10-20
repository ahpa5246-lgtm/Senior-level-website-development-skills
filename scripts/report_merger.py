"""Join reference/cost tool results into a proposal; never authorize source reuse or a bill."""
import re
import math

REPO = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$")


def combine_evidence(blueprint, references=None, cost=None):
    report = dict(blueprint)
    if references is not None:
        if not isinstance(references, dict) or not isinstance(references.get("candidates"), list):
            raise ValueError("GitHub discovery must be a candidates report")
        if len(references["candidates"]) > 4:
            raise ValueError("Review at most four source candidates per pass")
        candidates = []
        for raw in references["candidates"]:
            if not isinstance(raw, dict):
                raise ValueError("Invalid GitHub candidate")
            url = raw.get("url")
            ref = raw.get("ref")
            sha = ref.get("commit_sha") if isinstance(ref, dict) else None
            if not isinstance(url, str) or not REPO.fullmatch(url):
                raise ValueError("Repository reference has malformed GitHub URL")
            if not isinstance(sha, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", sha):
                raise ValueError("Repository reference lacks immutable 40-character SHA")
            lic = raw.get("license")
            candidates.append({
                "url": url, "commit_sha": sha,
                "claimed_license": str(lic.get("spdx_id"))[:80] if isinstance(lic, dict) else "UNKNOWN",
                "reuse_decision": "STUDY_ONLY_PENDING_REVIEW",
                "functional_match_verified": False,
                "security_audited": False,
                "assets_reviewed": False,
                "real_operational_cost_verified": False
            })
        report["researched_candidates"] = candidates
        if not candidates:
            report["skeptical_findings"] = list(report["skeptical_findings"]) + [
                {"code":"NO_REFERENCE_CANDIDATES","reason":"The supplied repository research found no usable candidates"}]
    if cost is not None:
        owner = report["owner_safe_summary"].get("budget")
        if not isinstance(cost, dict) or not isinstance(cost.get("scenarios"), dict):
            raise ValueError("Pricing report requires normal, peak and recovery scenarios")
        budget = cost.get("monthly_budget")
        if (not isinstance(owner, dict) or type(budget) not in (int, float)
                or not math.isfinite(budget) or budget < 0
                or cost.get("currency") != owner.get("currency") or budget != owner.get("amount")):
            raise ValueError("Pricing report disagrees with owner monthly budget/currency")
        if set(cost["scenarios"]) != {"normal", "peak", "recovery"}:
            raise ValueError("Missing required pricing scenarios")
        items = {}
        for name, raw in cost["scenarios"].items():
            if not isinstance(raw, dict) or type(raw.get("total_is_complete")) is not bool or type(raw.get("over_budget")) is not bool:
                raise ValueError("Incomplete pricing fields for "+name)
            amount = raw.get("quoted_total")
            if amount is not None and (type(amount) not in (float, int) or not 0 <= amount < 1e12):
                raise ValueError("Bad pricing value in "+name)
            if raw["total_is_complete"] and amount is None:
                raise ValueError("A complete pricing scenario needs a total: " + name)
            if amount is not None and raw["over_budget"] != (amount > budget):
                raise ValueError("Pricing over_budget flag contradicts the declared budget: " + name)
            items[name] = {"quoted_total":amount, "complete":raw["total_is_complete"],
                           "over_budget":raw["over_budget"]}
        report["cost_scenarios"] = {
            "status":cost.get("status","UNKNOWN"),"scenarios":items,
            "unpriced":cost.get("unpriced",[]),"alerts":cost.get("alerts",[]),
            "provider_prices_independently_verified":False,
            "release_authorized":False}
        if (cost.get("status") != "QUOTES_WITHIN_DECLARED_BUDGET"
                or cost.get("unpriced")
                or any(not item["complete"] or item["over_budget"] for item in items.values())):
            report["skeptical_findings"] = list(report["skeptical_findings"]) + [
                {"code":"COST_SCENARIO_BLOCKER", "reason":"Cost forecast exceeds budget or is incomplete"}]
    return report


def describe_evidence(report):
    lines=[]
    if "researched_candidates" in report:
        lines.extend(["", "## مستودعات GitHub المقارنة (ليست موافقة على النسخ)"])
        if not report["researched_candidates"]:
            lines.append("- لم نجد مرجعًا صالحًا؛ البحث والاختبار مطلوبان")
        for r in report["researched_candidates"]:
            lines.append("- "+r["url"]+" — نسخة "+r["commit_sha"]+
                         "، ترخيص معلن: "+r["claimed_license"]+
                         "؛ الملاءمة والرخصة والأصول والأمان والتشغيل غير معتمدة.")
    if "cost_scenarios" in report:
        data=report["cost_scenarios"]
        lines.extend(["", "## أسعار الاستضافة الواردة في التقرير (غير مؤكدة مستقلاً)"])
        for name in ("normal","peak","recovery"):
            case=data["scenarios"][name]
            amount=case["quoted_total"]
            lines.append("- "+name+": "+("غير قابل للحساب" if amount is None else str(amount))+
                         "؛ حساب مكتمل: "+str(case["complete"])+
                         "؛ تجاوز الميزانية: "+str(case["over_budget"]))
        lines.append("- حالة التقرير: "+str(data["status"])[:100])
        lines.append("- تحذيرات: "+str(data["alerts"])[:500])
        lines.append("- لا يوجد في هذا التقرير تصريح بدفع الأموال أو الإطلاق التجاري.")
    return "\n".join(lines)
