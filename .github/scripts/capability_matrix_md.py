"""Render `capability_matrix.json` as a markdown table for $GITHUB_STEP_SUMMARY.

Usage: python capability_matrix_md.py capability_matrix.json
"""
from __future__ import annotations

import json
import pathlib
import sys


def main() -> int:
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "capability_matrix.json")
    if not src.exists():
        print(f"_(capability matrix file `{src}` not found — skipping)_")
        return 0
    raw = src.read_text().strip()
    if not raw:
        print("_(capability matrix file is empty — registry print step likely failed; skipping)_")
        return 0
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"_(capability matrix file is not valid JSON: {exc}; skipping)_")
        return 0
    rows = ["| backend | category | available | version | error |", "|---|---|---|---|---|"]
    for name, info in sorted(data.items()):
        avail = ":white_check_mark:" if info["available"] else ":x:"
        ver = info.get("version") or ""
        err = (info.get("error") or "").replace("|", "\\|")
        rows.append(f'| `{name}` | {info["category"]} | {avail} | {ver} | {err} |')
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
