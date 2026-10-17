#!/usr/bin/env python3
"""Competitive UI quality contract, NOT an AI aesthetic judge or web scraper.

Checks project-specific evidence against stable formal gates. All external
reference claims still need human examination. No benchmark screenshots are
copied, downloaded, scraped or published by this tool.
"""
import argparse
from datetime import date, datetime
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

SLUG = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{1,45}$")
HEX = re.compile(r"^#[A-Fa-f0-9]{6}$")
GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
REQUIRED_STATES = {"empty", "loading", "success", "failure"}
CATEGORY = {"direct", "adjacent", "aspirational"}
ALLOWED_STAGE = {"planning", "implementation", "release_review"}
WANTED_SURFACES = {"desktop", "narrow_window", "mobile"}
MAX_BYTES = 150_000


def safe_read(path):
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_BYTES:
        raise ValueError("Missing, symlinked or oversized design evidence input")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Expected one JSON object")
    return data


def valid_url(url):
    if not isinstance(url, str) or len(url) > 1024:
        return False
    try:
        u = urlparse(url)
        return (u.scheme == "https" and bool(u.hostname)
                and "." in u.hostname and not u.username and not u.password
                and not u.hostname.endswith(".example") and not u.hostname.endswith(".localhost"))
    except ValueError:
        return False


def check_screenshot(root, name):
    if not isinstance(name, str) or not name or "\\" in name or len(name) > 240:
        return False
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or relative.parts[0] == ".":
        return False
    root = Path(root).resolve()
    path = root / relative
    if root not in path.parents or any(x.is_symlink() for x in (path, *path.parents) if x != root):
        return False
    if path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
        return False
    return path.is_file() and 100 <= path.stat().st_size < 15_000_000


def check(data, *, evidence_root, today=None, max_age_days=120):
    now = today or date.today()
    findings = []
    def fault(code, detail):
        findings.append({"code": code, "detail": detail})
    project = data.get("project")
    if not isinstance(project, str) or not SLUG.fullmatch(project):
        fault("PROJECT_ID", "Use a project slug")
    stage = data.get("stage")
    if stage not in ALLOWED_STAGE:
        fault("STAGE", "Explicit planning, implementation or release_review stage required")
    complex_app = data.get("complex_app")
    if type(complex_app) is not bool:
        fault("COMPLEXITY_UNCLASSIFIED", "Explicitly classify whether several distinct workflows exist")
        complex_app = True

    journeys = data.get("journeys", [])
    screens = data.get("screens", [])
    if not isinstance(journeys, list) or not isinstance(screens, list):
        journeys, screens = [], []
    if not journeys:
        fault("NO_JOURNEYS", "List real user goals rather than component counts")
    if not screens:
        fault("NO_SURFACES", "Define where each primary workflow lives")
    ids = set()
    for item in journeys:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            fault("INVALID_JOURNEY", "Malformed journey item")
            continue
        key = item["id"]
        if key in ids:
            fault("DUPLICATE_JOURNEY", key)
        ids.add(key)
        if not isinstance(item.get("goal"), str) or len(item["goal"].strip()) < 15:
            fault("VAGUE_GOAL", key + " must say what a user accomplishes")
        if not isinstance(item.get("surface"), str) or not item["surface"]:
            fault("UNMAPPED_JOURNEY", key + " needs a destination")
        states = item.get("states", [])
        if not isinstance(states, list) or not REQUIRED_STATES.issubset(set(str(v) for v in states)):
            fault("MISSING_INTERACTION_STATES", key + " needs empty/loading/success/failure cases")
    surface_ids = [s.get("id") for s in screens if isinstance(s, dict)]
    if len(surface_ids) != len(set(surface_ids)) or any(not isinstance(x, str) or not x for x in surface_ids):
        fault("DUPLICATE_SCREEN", "Every named workspace must have a distinct ID")
    if any(j.get("surface") not in surface_ids for j in journeys if isinstance(j, dict)):
        fault("BROKEN_NAVIGATION_MAP", "Every journey needs an existing workspace ID")
    if complex_app and len(ids) >= 4 and len(set(surface_ids)) == 1:
        rationale = data.get("single_surface_justification")
        if not isinstance(rationale, str) or len(rationale.strip()) < 90:
            fault("ONE_SCREEN_OVERLOAD", "4+ distinct workflows need justified navigation separation, not one giant form")
        # Even with a rationale, task evidence must still be checked later.

    references = data.get("references")
    if not isinstance(references, list):
        references = []
    required = 3 if complex_app else 2
    if len(references) < required:
        fault("TOO_FEW_REAL_BENCHMARKS", f"Need {required} different real released product references")
    names = set()
    direct = 0
    for item in references:
        if not isinstance(item, dict):
            fault("INVALID_BENCHMARK", "Malformed competitor reference")
            continue
        name = item.get("name")
        if not isinstance(name, str) or len(name.strip()) < 3 or name.casefold() in names:
            fault("BENCHMARK_NAME", "References must be distinct named products")
        else:
            names.add(name.casefold())
        if item.get("category") not in CATEGORY:
            fault("BENCHMARK_CATEGORY", "Record direct / adjacent / aspirational")
        elif item.get("category") == "direct":
            direct += 1
        if item.get("release_status") != "released_product":
            fault("NOT_REAL_PRODUCT", str(name) + ": not confirmed released; a vibe-coding demo alone is insufficient")
        if not valid_url(item.get("official_url")) or not valid_url(item.get("visual_source_url")):
            fault("MISSING_OFFICIAL_VISUAL", str(name) + ": provide an official product page and visual evidence URL")
        if not isinstance(item.get("pattern"), str) or len(item["pattern"].strip()) < 35:
            fault("NO_TRANSFERABLE_PATTERN", str(name) + ": explain a specific workflow/layout convention")
        if not isinstance(item.get("tradeoff"), str) or len(item["tradeoff"].strip()) < 20:
            fault("BENCHMARK_NO_TRADEOFF", str(name) + ": mention a weakness/constraint, not blind imitation")
        try:
            seen = date.fromisoformat(item.get("observed_on", ""))
            if seen > now or (now - seen).days > max_age_days:
                fault("STALE_BENCHMARK", str(name) + ": revisit official product and visuals")
        except (ValueError, TypeError):
            fault("BENCHMARK_DATE", str(name) + ": ISO 8601 observation date required")
    if direct < (2 if complex_app else 1):
        fault("NOT_ENOUGH_DIRECT_COMPARATORS", "Include relevant, released direct competitors")
    comparisons = data.get("comparisons", [])
    if not isinstance(comparisons, list):
        comparisons = []
    compared = set()
    for comp in comparisons:
        if not isinstance(comp, dict):
            fault("MALFORMED_COMPARISON", "Comparison item must be an object")
            continue
        jid = comp.get("journey_id")
        compared.add(jid)
        if jid not in ids:
            fault("UNKNOWN_COMPARED_JOURNEY", str(jid))
        if not isinstance(comp.get("benchmark"), str) or comp["benchmark"].casefold() not in names:
            fault("UNKNOWN_COMPARATOR", str(jid))
        for field in ("gap", "improvement", "not_copied"):
            if not isinstance(comp.get(field), str) or len(comp[field].strip()) < 25:
                fault("SHALLOW_COMPARISON", str(jid) + ": " + field + " needs a meaningful comparison")
    for jid in ids - compared:
        fault("UNCOMPARED_JOURNEY", jid + ": compare its user outcome against a real product")

    ds = data.get("design_system", {})
    if not isinstance(ds, dict):
        ds = {}
    for field in ("body_font", "arabic_font", "type_hierarchy", "spacing_scale",
                  "color_roles", "illustration_policy", "density_rationale"):
        if not ds.get(field):
            fault("DESIGN_SYSTEM_GAP", "Missing " + field)
    for fld in ("body_font_license_checked", "illustrations_license_checked"):
        if type(ds.get(fld)) is not bool or not ds.get(fld):
            fault("UNVERIFIED_ASSET_LICENSE", fld)
    palette = ds.get("color_roles", {})
    if not isinstance(palette, dict):
        palette = {}
    for role in ("canvas", "surface", "text", "muted", "action", "focus"):
        if not isinstance(palette.get(role), str) or not HEX.fullmatch(palette[role]):
            fault("PALETTE_ROLE", role + ": use a tested semantic 6-digit color")
    scale = ds.get("spacing_scale", [])
    if not isinstance(scale, list) or len(scale) < 4 or any(type(x) is not int or x <= 0 for x in scale) or scale != sorted(set(scale)):
        fault("SPACING_SCALE", "Use ordered reusable numeric CSS spacing values")
    roles = ds.get("type_hierarchy", [])
    if not isinstance(roles, list) or len(roles) < 3:
        fault("TYPE_HIERARCHY", "Use at least body, section heading and page title roles")
    if not isinstance(ds.get("illustration_policy"), str) or len(ds["illustration_policy"].strip()) < 40:
        fault("DECORATIVE_SLOP", "What does the illustration explain? Where is it used? What is its performance cost?")
    if not isinstance(ds.get("density_rationale"), str) or len(ds["density_rationale"].strip()) < 45:
        fault("UNREVIEWED_DENSITY", "Explain what is on primary screen vs progressive detail")

    review = data.get("review", {})
    if not isinstance(review, dict):
        review = {}
    directions = review.get("design_directions", [])
    if not isinstance(directions, list) or len(directions) < 2:
        fault("ONE_DESIGN_DIRECTION", "Compare at least two distinct layouts, not two color variations")
    else:
        for direction in directions:
            if not isinstance(direction, dict) or len(str(direction.get("layout", "")).strip()) < 20:
                fault("VAGUE_LAYOUT_OPTION", "Each direction must specify a distinct navigation/content approach")
    if not review.get("selected_direction") or not isinstance(review.get("decision_reason"), str) or len(review["decision_reason"].strip()) < 40:
        fault("NO_RATIONALE_FOR_DESIGN", "Choose and explain a layout decision")
    if stage in ("implementation", "release_review"):
        if not GIT_SHA.fullmatch(str(review.get("implemented_commit", ""))):
            fault("NO_IMPLEMENTATION_COMMIT", "Link report to the actual target application commit")
        shots = review.get("screenshots", [])
        if not isinstance(shots, list) or not shots or any(not check_screenshot(evidence_root, x) for x in shots):
            fault("NO_VERIFIED_SCREENSHOTS", "Screenshots of the actual build must exist under the evidence root")
        expected = {"desktop", "narrow_window"} if data.get("kind") == "desktop" else {"desktop", "mobile"}
        tested = set(review.get("tested_surfaces", [])) if isinstance(review.get("tested_surfaces"), list) else set()
        if not expected.issubset(tested):
            fault("UNTESTED_BREAKPOINTS", "Test real tasks on " + ", ".join(sorted(expected)))
        for fld in ("keyboard_tested", "empty_and_error_tested", "comparison_rechecked_at_commit"):
            if review.get(fld) is not True:
                fault("REVIEW_INCOMPLETE", fld + " needs real exercised evidence")
        if review.get("arabic_ui") is True and review.get("rtl_tested") is not True:
            fault("RTL_UNVERIFIED", "Test Arabic and mixed script in actual application")
        if not isinstance(review.get("task_test_evidence"), str) or len(review["task_test_evidence"].strip()) < 25:
            fault("NO_USABILITY_TASK_EVIDENCE", "Prove the primary journey by observation, not screenshots alone")
    return {
        "project": project, "stage": stage, "status": "PASS_EVIDENCE_STRUCTURE" if not findings else "BLOCKED_UNVERIFIED_DESIGN",
        "findings": findings,
        "limits": "Structural evidence validation only; cannot certify taste, source authenticity, accessibility or real implementation."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare a UI against released products with explicit evidence")
    parser.add_argument("--input", required=True)
    parser.add_argument("--evidence-root", default=".")
    parser.add_argument("--max-age-days", type=int, default=120)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.max_age_days <= 365:
            raise ValueError("Max age outside 1-365 days")
        report = check(safe_read(args.input), evidence_root=args.evidence_root,
                       max_age_days=args.max_age_days)
        if args.out:
            path = Path(args.out)
            if path.exists() or path.is_symlink():
                raise ValueError("Refusing to overwrite an existing report")
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        print(json.dumps(report, ensure_ascii=False))
        return 0 if report["status"] == "PASS_EVIDENCE_STRUCTURE" else 2
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status":"BLOCKED_INVALID_INPUT", "reason":str(exc)[:250]},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
