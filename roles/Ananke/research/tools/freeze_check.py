"""freeze_check (BX-1): is a plan's freeze provable from git?

PASS iff the plan file's first-add commit is a strict ancestor of the first commit that adds any
result file matching the given pathspec(s), AND the plan blob at HEAD equals the blob it was added with.
Reads git only; never edits anything.

    python roles/Ananke/research/tools/freeze_check.py <plan_path> <result_pathspec> [...]
Exit 0 = PASS, 1 = FAIL, 2 = cannot evaluate (e.g. plan or results never committed).
"""
from __future__ import annotations

import subprocess
import sys


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout.strip()


def first_add(pathspecs: list[str]) -> str | None:
    """Oldest commit (topological) that adds any path matching the pathspecs."""
    out = _git("log", "--diff-filter=A", "--format=%H", "--topo-order", "--reverse", "--", *pathspecs)
    return out.splitlines()[0] if out else None


def check(plan: str, results: list[str]) -> dict:
    p_add = first_add([plan])
    r_add = first_add(results)
    if p_add is None or r_add is None:
        return {"verdict": "CANNOT_EVALUATE", "plan_add": p_add, "result_add": r_add}
    before = p_add != r_add and subprocess.run(
        ["git", "merge-base", "--is-ancestor", p_add, r_add]).returncode == 0
    blob_add = _git("rev-parse", f"{p_add}:{plan}")
    blob_head = _git("rev-parse", f"HEAD:{plan}")
    ok = before and blob_add == blob_head
    return {"verdict": "PASS" if ok else "FAIL", "plan_add": p_add[:9], "result_add": r_add[:9],
            "plan_before_results": before, "plan_unchanged": blob_add == blob_head}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    r = check(sys.argv[1], sys.argv[2:])
    print(r)
    sys.exit({"PASS": 0, "FAIL": 1}.get(r["verdict"], 2))
