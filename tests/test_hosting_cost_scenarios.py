"""Deterministic cost mathematics, no paid service lookups."""
import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hosting_costs", ROOT / "scripts" / "hosting_cost_scenarios.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class HostingEconomicsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples" / "fictional-hosting-costs.json").read_text(encoding="utf-8"))
        self.today = date(2026, 10, 17)

    def test_missing_email_and_peak_cap_block(self):
        report = mod.evaluate(self.data, self.today)
        self.assertEqual(report["status"], "NEEDS_COST_EVIDENCE_OR_REDESIGN")
        self.assertEqual(report["unpriced"], ["transactional_email"])
        self.assertIsNone(report["scenarios"]["normal"]["quoted_total"])
        self.assertEqual(set(report["scenarios"]["peak"]["exceeded_hard_limits"]),
                         {"static_pages", "workshop_registrations"})
        self.assertFalse(report["provider_prices_verified"])

    def test_billable_overage_and_annual_domain_math(self):
        doc = {
            "currency": "USD", "monthly_budget": 50, "one_time_budget": 0,
            "required_components": ["domain"],
            "quotes": [{
                "component": "domain", "currency": "USD", "source_url": "https://example.com/fictional",
                "checked_on": "2026-10-17", "unit": "requests",
                "fixed_monthly": 2, "annual_fixed": 12, "one_time": 0,
                "included_units": 100, "limit_policy": "billable", "unit_cost": .1,
                "usage_forecast": {"normal": 50, "peak": 130, "recovery": 200}
            }]
        }
        report = mod.evaluate(doc, self.today)
        self.assertEqual(report["status"], "QUOTES_WITHIN_DECLARED_BUDGET")
        self.assertEqual(report["scenarios"]["normal"]["quoted_total"], 3)
        self.assertEqual(report["scenarios"]["peak"]["quoted_total"], 6)
        self.assertEqual(report["scenarios"]["recovery"]["quoted_total"], 13)
        self.assertFalse(report["launch_authorized"])

    def test_unknown_overage_blocks(self):
        self.data["required_components"] = ["static_pages", "workshop_registrations"]
        self.data["quotes"][0]["limit_policy"] = "unknown"
        report = mod.evaluate(self.data, self.today)
        self.assertIn("static_pages", report["scenarios"]["peak"]["unknown_overage"])

    def test_stale_quote_requires_recheck(self):
        self.data["required_components"] = ["static_pages", "workshop_registrations"]
        self.data["quotes"][0]["checked_on"] = "2026-01-01"
        report = mod.evaluate(self.data, self.today)
        self.assertIn("static_pages", report["stale_quotes"])

    def test_invalid_money_and_forecast(self):
        self.data["quotes"][0]["fixed_monthly"] = -5
        with self.assertRaises(mod.BudgetError):
            mod.evaluate(self.data, self.today)
        self.data["quotes"][0]["fixed_monthly"] = 0
        del self.data["quotes"][0]["usage_forecast"]["peak"]
        with self.assertRaises(mod.BudgetError):
            mod.evaluate(self.data, self.today)

    def test_duplicate_quotes_rejected(self):
        self.data["quotes"].append(self.data["quotes"][0].copy())
        with self.assertRaises(mod.BudgetError):
            mod.evaluate(self.data, self.today)


if __name__ == "__main__":
    unittest.main()
