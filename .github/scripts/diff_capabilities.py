"""Diff old vs new capability snapshots; print key=value lines for $GITHUB_OUTPUT.

Usage: python diff_capabilities.py OLD.json NEW.json

Outputs (to stdout):
    changed=true|false
    summary=<single-line summary>

Both lines are appended to $GITHUB_OUTPUT by the workflow. The summary
deliberately stays single-line because GitHub Actions' GITHUB_OUTPUT
mechanism mishandles raw newlines.
"""
from __future__ import annotations

import json
import pathlib
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("changed=false")
        print("summary=usage: diff_capabilities.py OLD NEW")
        return 2

    old_path = pathlib.Path(sys.argv[1])
    new_path = pathlib.Path(sys.argv[2])

    if not old_path.exists():
        print("changed=true")
        print("summary=Initial capability snapshot population.")
        return 0

    old = json.loads(old_path.read_text())
    new = json.loads(new_path.read_text())
    old_b = old.get("backends", old)
    new_b = new.get("backends", new)

    gained, lost, version_changed = [], [], []

    for name, info in new_b.items():
        prev = old_b.get(name)
        if prev is None:
            gained.append(name)
            continue
        if info.get("available") and not prev.get("available"):
            gained.append(name)
        elif prev.get("available") and not info.get("available"):
            lost.append(name)
        elif (
            info.get("available")
            and prev.get("available")
            and info.get("version") != prev.get("version")
        ):
            version_changed.append(
                f'{name}: {prev.get("version")} -> {info.get("version")}'
            )

    for name in old_b:
        if name not in new_b:
            lost.append(name)

    changed = bool(gained or lost or version_changed)
    parts = []
    if gained:
        parts.append("gained=" + ",".join(sorted(gained)))
    if lost:
        parts.append("lost=" + ",".join(sorted(lost)))
    if version_changed:
        parts.append("versions=" + "; ".join(version_changed))
    summary = " | ".join(parts) if parts else "no change"

    print(f"changed={'true' if changed else 'false'}")
    print(f"summary={summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
