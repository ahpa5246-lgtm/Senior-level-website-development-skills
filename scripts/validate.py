"""Validate documentation structure, matrix coverage and local Markdown links.
Does not audit an application or check remote URLs.
"""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
rows = json.loads((root / "docs/100-error-matrix.json").read_text())
assert [r["id"] for r in rows] == list(range(1, 101)), "Missing/duplicate matrix IDs"
assert len({r["error"] for r in rows}) == 100, "Duplicate errors"
ledger = (root / "docs/sources.md").read_text()
for row in rows:
    assert all(row[k] for k in ("category", "error", "alternative", "verification", "sources"))
    for source in row["sources"]:
        assert re.search(r"\| " + re.escape(source) + r" \|", ledger), source
markdown = (root / "docs/100-error-matrix.md").read_text()
assert [int(n) for n in re.findall(r"^\| (\d+) \|", markdown, re.M)] == list(range(1, 101))
errors = []
for file in root.rglob("*.md"):
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", file.read_text()):
        if "://" in target or target.startswith("#"):
            continue
        dest = file.parent / target.split("#")[0]
        if not dest.exists():
            errors.append(f"{file.relative_to(root)} -> {target}")
assert not errors, "Broken local links: " + repr(errors)
assert len({r["category"] for r in rows}) == 10
paired = (root / "docs/500-senior-pairs-ar.md").read_text(encoding="utf-8")
paired_ids = [int(n) for n in re.findall(r"^\\|\\s*(\\d+)\\s*\\|", paired, re.M)]
assert paired_ids == list(range(1, 501)), "500-item paired matrix has missing/duplicate IDs"
groups = re.findall(r"^###\\s+\\d{2}\\s+—", paired, re.M)
assert len(groups) == 25, "Expected 25 topic sections"
questions = json.loads((root / "config/20-questions-ar.json").read_text(encoding="utf-8"))["questions"]
assert [q["id"] for q in questions] == [f"Q{i:02}" for i in range(1, 21)]
assert all(q.get("prompt") and q.get("reason") and q.get("key") for q in questions)
print(f"PASS: 100 legacy items + 500 ordered paired errors in 25 sections, 20 interview questions, source IDs and local links; {len(list(root.rglob('*.md')))} Markdown files")
