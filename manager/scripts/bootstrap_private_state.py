#!/usr/bin/env python3
"""Initialize a PRIVATE local supervisor state for the unified public codebase.

No GitHub calls, Codex actions, secrets, project discovery, or paid services.
Never overwrites an existing state directory, including symlink directories.
"""
import argparse
from pathlib import Path
import shutil
import sys

MANAGER = Path(__file__).resolve().parents[1]
TEMPLATES = MANAGER / "state-templates"
REQUIRED = (
    "PROJECT_QUEUE.md", "CURRENT_TASK.md", "AUTONOMOUS_TASK_QUEUES.md",
    "BLOCKERS.md", "WORK_LOG.md", "CONTINUOUS_IMPROVEMENT_BACKLOG.md"
)


def bootstrap(destination):
    target = Path(destination).expanduser().absolute()
    if target.exists() or target.is_symlink():
        raise ValueError("Private state destination already exists; refusing to overwrite it")
    for name in REQUIRED:
        path = TEMPLATES / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing or unsafe template: " + name)
    policy = MANAGER / "FACTORY_POLICY.md"
    if not policy.is_file() or policy.is_symlink():
        raise ValueError("Missing manager factory policy")
    target.mkdir(parents=True, exist_ok=False)
    for name in REQUIRED:
        shutil.copyfile(TEMPLATES / name, target / name)
    shutil.copyfile(policy, target / "FACTORY_POLICY.md")
    (target / "README_PRIVATE.md").write_text(
        "# Your local, unpublished supervisor state\n"
        "This directory is NOT synced to GitHub. Do not commit these files.\n"
        "Add only your authorized repositories to PROJECT_QUEUE.md after live verification.\n"
        "All milestones require current PR/CI evidence and an approved packet.\n"
        "If you need cross-device persistence, choose an access-controlled private storage system;\n"
        "never turn the public source repository into a store of customer secrets.\n",
        encoding="utf-8"
    )
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create never-overwriting local manager state")
    parser.add_argument("--destination", default=str(MANAGER / ".state"))
    args = parser.parse_args(argv)
    try:
        directory = bootstrap(args.destination)
        print(f"CREATED_PRIVATE_STATE {directory}; no project authorized or Codex started")
        return 0
    except (OSError, ValueError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
