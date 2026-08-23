"""Report the arsenal's red count WITH the command that produced it.

Cycle 049's retrospective audit (HITL #286) found that 48 cycles reported an "arsenal red"
count — 28, 29, 30 — and **not one recorded the invocation that produced it**. A number a
later cycle diffs against is only as good as an unrecorded command, so this script makes the
scope explicit and emits it alongside the count.

It also emits the sorted failing node ids, because the loop's postcondition discipline is a
NAME-diff, not a count-diff: a count that stays at 29 while one test goes green and another
goes red reads as "no change" and is not.

    python -m techne.scripts.arsenal_red --out pivot/arsenal_red_049.json
    python -m techne.scripts.arsenal_red --compare pivot/arsenal_red_048.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

# The scope, stated once, so it stops being folklore.
SCOPE = ["prometheus_math"]
PYTEST_ARGS = ["-q", "--continue-on-collection-errors", "-p", "no:cacheprovider"]


def command() -> list[str]:
    return [sys.executable, "-m", "pytest", *SCOPE, *PYTEST_ARGS]


def run() -> dict:
    cmd = command()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = proc.stdout or ""
    failed = sorted(
        line.split(" ", 1)[1].strip()
        for line in out.splitlines()
        if line.startswith("FAILED ")
    )
    errors = sorted(
        line.split(" ", 1)[1].strip()
        for line in out.splitlines()
        if line.startswith("ERROR ")
    )
    tail = [l for l in out.splitlines() if " passed" in l or " failed" in l]
    return {
        "command": " ".join(cmd[1:]),  # sys.executable varies by machine; the args do not
        "scope": SCOPE,
        "red": len(failed),
        "collection_errors": len(errors),
        "failed": failed,
        "errors": errors,
        "summary_line": tail[-1] if tail else "",
    }


def name_diff(prior: dict, current: dict) -> dict:
    was, now = set(prior.get("failed", [])), set(current.get("failed", []))
    return {
        "red_before": prior.get("red"),
        "red_after": current.get("red"),
        "NEW": sorted(now - was),
        "GONE": sorted(was - now),
        "unchanged": len(now & was),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path)
    ap.add_argument("--compare", type=pathlib.Path,
                    help="prior report json; emits the NAME-diff, not just the count")
    a = ap.parse_args()

    report = run()
    if a.compare and a.compare.exists():
        report["name_diff"] = name_diff(json.loads(a.compare.read_text(encoding="utf-8")), report)
    text = json.dumps(report, indent=2)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
