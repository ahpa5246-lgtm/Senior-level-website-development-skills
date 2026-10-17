#!/usr/bin/env python3
"""Evidence-oriented GitHub repository research. No cloning or executing code.

Offline tests use an injected API callable. Live mode only fetches api.github.com
JSON, with a fixed request budget. Signals guide human inspection, not approval.
"""
import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
NAME = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
QUERY_LIMIT = 150


class ResearchError(Exception):
    pass


def safe_name(value):
    if not isinstance(value, str) or not NAME.fullmatch(value) or ".." in value:
        raise ResearchError("Invalid repository owner/name")
    return value


class PublicGitHub:
    """No user URL is ever used as a fetch destination."""

    def __init__(self, max_requests=19):
        self.remaining = max_requests

    def __call__(self, path, params=None):
        if self.remaining <= 0:
            raise ResearchError("Request budget exhausted")
        if not path.startswith("/") or "://" in path or ".." in path:
            raise ResearchError("Non-GitHub path prohibited")
        self.remaining -= 1
        uri = API + path
        if params:
            uri += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(uri, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Senior-Engineering-Reference-Research/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        try:
            with urllib.request.urlopen(req, timeout=9) as response:
                if urllib.parse.urlsplit(response.geturl()).netloc != "api.github.com":
                    raise ResearchError("Unexpected API redirect")
                body = response.read(700000)
                if len(body) >= 700000:
                    raise ResearchError("GitHub payload size limit")
                return json.loads(body.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            # Missing license is a known research result; API rate limits are not.
            if exc.code == 404:
                return None
            if exc.code in (403, 429):
                raise ResearchError("GitHub rate limit or access denied") from None
            raise ResearchError(f"GitHub HTTP {exc.code}") from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ResearchError("GitHub API unavailable: " + type(exc).__name__) from None


def assess_candidate(record, api):
    full = safe_name(record.get("full_name", ""))
    repo = api("/repos/" + full)
    if not isinstance(repo, dict):
        raise ResearchError("Missing repository metadata")
    branch = repo.get("default_branch")
    if not isinstance(branch, str) or not branch:
        raise ResearchError("Default branch missing")
    prefix = "/repos/" + full
    # Never infer a license from a README or a search result tag.
    license_info = api(prefix + "/license")
    explicit = (isinstance(license_info, dict)
                and isinstance(license_info.get("license"), dict)
                and license_info["license"].get("spdx_id") not in (None, "NOASSERTION"))
    license_id = license_info["license"]["spdx_id"] if explicit else None
    root = api(prefix + "/contents", {"ref": branch})
    if not isinstance(root, list):
        root = []
    files = {x["name"].lower() for x in root if isinstance(x, dict) and isinstance(x.get("name"), str)}
    sha = None
    commit = api(prefix + "/commits/" + urllib.parse.quote(branch, safe=""))
    if isinstance(commit, dict) and isinstance(commit.get("sha"), str):
        sha = commit["sha"]
    indicators = {
        "documentation": "readme.md" in files or "readme.rst" in files,
        "tests_likely": bool(files.intersection({"tests", "test", "__tests__", "e2e"})),
        "ci_likely": ".github" in files or ".gitlab-ci.yml" in files,
        "container_setup": bool(files.intersection({"dockerfile", "docker-compose.yml", "compose.yaml", "compose.yml"})),
        "dependency_manifest": bool(files.intersection({
            "package.json", "pyproject.toml", "requirements.txt", "go.mod", "cargo.toml", "pom.xml"
        })),
    }
    archived = repo.get("archived") is True or repo.get("disabled") is True
    # These are hints for inspection, NOT automated proof of security or function.
    score = sum(int(v) for v in indicators.values()) + (2 if explicit else 0) - (5 if archived else 0)
    return {
        "repository": full,
        "url": "https://github.com/" + full,
        "ref": {"branch": branch, "commit_sha": sha},
        "description": repo.get("description") or "",
        "archived": archived,
        "updated_at": repo.get("pushed_at"),
        "license": {"spdx_id": license_id, "file": license_info.get("path") if isinstance(license_info, dict) else None,
                    "source": "https://api.github.com/repos/" + full + "/license",
                    "needs_human_compatibility_review": True},
        "indicators": indicators,
        "review_score_not_quality": score,
        "reuse_status": "STUDY_ONLY" if archived or not explicit else "LICENSE_REVIEW_REQUIRED",
        "economics": {"hosting_cost_verified": False, "operations_cost_verified": False,
                      "notes": "Assess runtime, storage, backups, deployment and third-party costs."},
        "security": {"audited": False},
        "functional_match": {"verified": False, "notes": "Inspect the real target workflow and backend."},
        "sources": ["https://api.github.com/repos/" + full,
                    "https://api.github.com/repos/" + full + "/contents?ref=" + urllib.parse.quote(branch, safe="")],
    }


def research(query, api, limit=3):
    query = str(query).strip()
    if not query or len(query) > QUERY_LIMIT or any(ord(ch) < 32 for ch in query):
        raise ResearchError("Query length or characters invalid")
    if not isinstance(limit, int) or not 1 <= limit <= 4:
        raise ResearchError("Candidate limit 1–4")
    search = api("/search/repositories", {"q": query + " archived:false", "per_page": min(12, limit * 4)})
    if not isinstance(search, dict) or not isinstance(search.get("items"), list):
        raise ResearchError("Invalid GitHub search result")
    candidates, discarded = [], []
    seen = set()
    for item in search["items"]:
        if len(candidates) >= limit:
            break
        name = item.get("full_name") if isinstance(item, dict) else None
        try:
            full = safe_name(name)
        except ResearchError:
            continue
        if full.lower() in seen:
            continue
        seen.add(full.lower())
        try:
            result = assess_candidate(item, api)
            if result["archived"]:
                discarded.append({"repository": full, "reason": "archived"})
                continue
            candidates.append(result)
        except ResearchError as exc:
            discarded.append({"repository": full, "reason": str(exc)})
    candidates.sort(key=lambda x: x["review_score_not_quality"], reverse=True)
    return {
        "schema_version": "1.0", "mode": "public-github-research",
        "query": query, "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "search_url": "https://github.com/search?q=" + urllib.parse.quote(query) + "&type=repositories",
        "candidates": candidates, "discarded": discarded,
        "caveats": [
            "Search rank, metadata, stars and top-level filenames do not prove that a feature works.",
            "A reported SPDX identifier still needs compatibility, asset license and provenance review.",
            "Neither security nor operational costs were verified; no repository is approved to clone.",
            "No untrusted repository code was downloaded or executed.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="GitHub project references with license and uncertainty checks")
    parser.add_argument("--query", required=True, help="Search phrase (not repository URL)")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--out", required=True, help="New local JSON report")
    parser.add_argument("--live", action="store_true", help="Explicitly permit public GitHub API requests")
    args = parser.parse_args(argv)
    if not args.live:
        parser.error("Network disabled by default: pass --live after reviewing the requested search")
    try:
        report = research(args.query, PublicGitHub(), args.limit)
        target = Path(args.out)
        if target.exists() or target.is_symlink():
            raise ResearchError("Do not overwrite an existing report")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "researched", "count": len(report["candidates"]), "report": str(target)}))
        return 0 if report["candidates"] else 1
    except (ResearchError, OSError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
