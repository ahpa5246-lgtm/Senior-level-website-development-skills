"""Deterministic discovery tests. No GitHub requests or repo code execution."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("github_reference_research", ROOT / "scripts" / "github_reference_research.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class FakeGitHub:
    def __init__(self, license_ids=None):
        self.license_ids = license_ids or {"acme/events": "MIT", "acme/unlicensed": None}
        self.called = []

    def __call__(self, path, params=None):
        self.called.append(path)
        if path == "/search/repositories":
            return {"items": [
                {"full_name": "acme/events"}, {"full_name": "acme/unlicensed"},
                {"full_name": "acme/events"}, {"full_name": "acme/archived"},
            ]}
        name = "/".join(path.split("/")[2:4])
        if path == "/repos/" + name:
            return {"full_name": name, "default_branch": "main", "archived": name == "acme/archived",
                    "description": "Sample events", "pushed_at": "2026-09-30T12:00:00Z"}
        if path.endswith("/license"):
            spdx = self.license_ids.get(name)
            return {"license": {"spdx_id": spdx}, "path": "LICENSE"} if spdx else None
        if path.endswith("/contents"):
            return [{"name": n} for n in ("README.md", "pyproject.toml", "tests", ".github")]
        if path.endswith("/commits/main"):
            return {"sha": "a" * 40}
        raise AssertionError(path)


class ResearchTests(unittest.TestCase):
    def test_license_and_commit_evidence(self):
        api = FakeGitHub()
        report = mod.research("workshop management", api, 2)
        self.assertEqual(len(report["candidates"]), 2)
        licensed = next(x for x in report["candidates"] if x["repository"] == "acme/events")
        self.assertEqual(licensed["license"]["spdx_id"], "MIT")
        self.assertEqual(licensed["ref"]["commit_sha"], "a" * 40)
        self.assertEqual(licensed["reuse_status"], "LICENSE_REVIEW_REQUIRED")
        self.assertFalse(licensed["economics"]["hosting_cost_verified"])
        self.assertFalse(licensed["security"]["audited"])

    def test_unknown_license_never_approved(self):
        result = mod.research("event", FakeGitHub(), 2)
        item = next(x for x in result["candidates"] if x["repository"] == "acme/unlicensed")
        self.assertEqual(item["reuse_status"], "STUDY_ONLY")
        self.assertIsNone(item["license"]["spdx_id"])

    def test_archived_project_rejected(self):
        result = mod.research("event", FakeGitHub(), 4)
        self.assertEqual(len(result["candidates"]), 2)
        self.assertEqual(result["discarded"], [{"repository": "acme/archived", "reason": "archived"}])

    def test_invalid_user_input(self):
        for query in ("", "x" * 151, "search\nGET /admin"):
            with self.assertRaises(mod.ResearchError):
                mod.research(query, FakeGitHub())
        with self.assertRaises(mod.ResearchError):
            mod.research("events", FakeGitHub(), 99)
        for repo in ("foo", "acme/../admin", "https://elsewhere.example/a/b"):
            with self.assertRaises(mod.ResearchError):
                mod.safe_name(repo)

    def test_no_sources_claimed_as_test_proof(self):
        report = mod.research("events", FakeGitHub())
        self.assertTrue(any("do not prove" in note for note in report["caveats"]))
        self.assertEqual(len(set(x["repository"] for x in report["candidates"])), len(report["candidates"]))


if __name__ == "__main__":
    unittest.main()
