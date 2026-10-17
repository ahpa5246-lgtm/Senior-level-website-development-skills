#!/usr/bin/env python3
"""Scenario-based hosting cost and hard-limit analysis, stdlib only.

Takes manually verified dated quotes; it DOES NOT fetch provider prices or verify
their accuracy. No quote may be treated as proof of free hosting. No secrets.
"""
import argparse
import json
import math
import re
from datetime import date
from pathlib import Path

SCENARIOS = ("normal", "peak", "recovery")
CURRENCY = re.compile(r"^[A-Z]{3}$")


class BudgetError(ValueError):
    pass


def amount(value, field):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value < 1e12:
        raise BudgetError("Invalid nonnegative finite number: " + field)
    return float(value)


def evaluate(data, today=None):
    today = today or date.today()
    if not isinstance(data, dict):
        raise BudgetError("Input must be a JSON object")
    currency = data.get("currency")
    if not isinstance(currency, str) or not CURRENCY.fullmatch(currency):
        raise BudgetError("Use one 3-letter currency and quote all amounts in that currency")
    ceiling = amount(data.get("monthly_budget"), "monthly_budget")
    initial_budget = amount(data.get("one_time_budget", 0), "one_time_budget")
    wants = data.get("required_components", [])
    quotes = data.get("quotes", [])
    if not isinstance(wants, list) or not wants or any(not isinstance(x, str) or not x for x in wants):
        raise BudgetError("List required_components explicitly")
    if not isinstance(quotes, list):
        raise BudgetError("quotes must be a list")
    indexed, stale = {}, []
    for quote in quotes:
        if not isinstance(quote, dict):
            raise BudgetError("Every quote must be an object")
        key = quote.get("component")
        if not isinstance(key, str) or key not in wants or key in indexed:
            raise BudgetError("Quoted components must be unique and required")
        if quote.get("currency") != currency:
            raise BudgetError("Quote currencies differ; an actual cited conversion is required")
        source = quote.get("source_url")
        if not isinstance(source, str) or not source.startswith("https://"):
            raise BudgetError("Quote needs an HTTPS original source")
        try:
            checked = date.fromisoformat(quote["checked_on"])
        except (KeyError, ValueError, TypeError):
            raise BudgetError("Quote checked_on must be YYYY-MM-DD") from None
        if checked > today:
            raise BudgetError("Future provider evidence is invalid")
        if (today - checked).days > 90:
            stale.append(key)
        policy = quote.get("limit_policy")
        if policy not in ("hard_cap", "billable", "unknown"):
            raise BudgetError("Specify provider over-limit policy: hard_cap/billable/unknown")
        annual = amount(quote.get("annual_fixed", 0), key + ".annual_fixed")
        monthly = amount(quote.get("fixed_monthly", 0), key + ".fixed_monthly")
        included = amount(quote.get("included_units"), key + ".included_units")
        unit_cost = amount(quote.get("unit_cost"), key + ".unit_cost") if policy == "billable" else None
        setup = amount(quote.get("one_time", 0), key + ".one_time")
        forecast = quote.get("usage_forecast")
        if not isinstance(forecast, dict) or set(forecast) != set(SCENARIOS):
            raise BudgetError("Each quote must specify normal/peak/recovery forecast units")
        units = {name: amount(forecast[name], key + "." + name) for name in SCENARIOS}
        indexed[key] = {"monthly": monthly, "annual": annual, "included": included,
                        "unit_cost": unit_cost, "setup": setup, "forecast": units,
                        "policy": policy, "source_url": source, "checked_on": checked.isoformat(),
                        "unit_name": quote.get("unit", "usage units")}
    unpriced = sorted(set(wants) - set(indexed))
    results = {}
    for scenario in SCENARIOS:
        baseline = 0.0
        details, capped, unknown = [], [], []
        for key, quote in indexed.items():
            units = quote["forecast"][scenario]
            extra = max(0, units - quote["included"])
            fixed = quote["monthly"] + quote["annual"] / 12
            if extra and quote["policy"] == "hard_cap":
                capped.append(key)
                variable = None
            elif extra and quote["policy"] == "unknown":
                unknown.append(key)
                variable = None
            else:
                variable = extra * quote["unit_cost"] if extra and quote["policy"] == "billable" else 0.0
            charge = None if variable is None else round(fixed + variable, 2)
            if charge is not None:
                baseline += charge
            details.append({
                "component": key, "units": units, "unit": quote["unit_name"], "limit_policy": quote["policy"],
                "included": quote["included"], "monthly_cost": charge, "source_url": quote["source_url"]
            })
        complete = not (unpriced or capped or unknown or stale)
        amount_total = round(baseline, 2) if not (unpriced or unknown or capped) else None
        results[scenario] = {
            "quoted_total": amount_total,
            "total_is_complete": complete,
            "over_budget": amount_total is not None and amount_total > ceiling,
            "exceeded_hard_limits": capped,
            "unknown_overage": unknown,
            "items": details,
        }
    one_time_total = round(sum(p["setup"] for p in indexed.values()), 2)
    alerts = []
    if unpriced:
        alerts.append("Unpriced required components: " + ", ".join(unpriced))
    if stale:
        alerts.append("Provider quotes older than 90 days require recheck: " + ", ".join(stale))
    for label, scenario in results.items():
        if scenario["exceeded_hard_limits"]:
            alerts.append(label + ": provider hard limits exceeded")
        if scenario["unknown_overage"]:
            alerts.append(label + ": unknown overage policy")
        if scenario["over_budget"]:
            alerts.append(label + ": quoted cost exceeds owner budget")
    if one_time_total > initial_budget:
        alerts.append("One-time setup exceeds owner budget")
    return {
        "schema_version": "1.0", "currency": currency, "monthly_budget": ceiling,
        "one_time_budget": initial_budget, "quoted_one_time": one_time_total,
        "unpriced": unpriced, "stale_quotes": stale, "scenarios": results,
        "status": "NEEDS_COST_EVIDENCE_OR_REDESIGN" if alerts else "QUOTES_WITHIN_DECLARED_BUDGET",
        "alerts": alerts,
        "caveat": "This is arithmetic on user-supplied quotes, not independently verified provider pricing, tested capacity, or deployment approval.",
        "launch_authorized": False, "provider_prices_verified": False
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Normal/peak/recovery costs under verified provider limits")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        path = Path(args.out)
        if path.exists() or path.is_symlink():
            raise BudgetError("Never overwrite an earlier cost report")
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = evaluate(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "report": str(path), "alerts": report["alerts"]}))
        return 0 if report["status"] == "QUOTES_WITHIN_DECLARED_BUDGET" else 1
    except (ValueError, OSError, BudgetError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)[:200]}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
