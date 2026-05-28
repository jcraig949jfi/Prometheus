"""
Per-cycle decorative-code ablation (Q12), tied to the blind holdout (Q9).

The Apollo gen-3551 lesson per-cycle: prove the cycle's code is not decorative.
We define genuine capability operationally and non-gameably:

    capability gain  <=>  candidate passes MORE blind holdout tests than parent.

If the candidate passes the same (or fewer) holdout tests as the parent it was
cloned from, the diff added no blind-verified capability -- it is decorative or
metric-shaped, regardless of what the visible tests say.

This couples improvement_kind to an oracle the Generator cannot see, closing
the write-your-own-test Goodhart loop.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_HOLDOUT_DIR = Path(r"D:\Prometheus\agents\icarus\holdout")
_HOLDOUT_BY_TIER = {
    "R0": ["test_holdout_R1.py"],
    "R1": ["test_holdout_R1.py"],
    "R2": ["test_holdout_R1.py", "test_holdout_R2.py"],
    "R3": ["test_holdout_R1.py", "test_holdout_R2.py"],
}


def _holdout_passed(code_dir: Path, tier_target: str) -> dict:
    """Run the blind holdout against a given code dir; return pass/fail counts."""
    suites = _HOLDOUT_BY_TIER.get(tier_target, ["test_holdout_R1.py"])
    files = [str(_HOLDOUT_DIR / s) for s in suites if (_HOLDOUT_DIR / s).exists()]
    if not files or not code_dir.exists():
        return {"passed": 0, "failed": 0, "skipped": 0, "ran": False}
    args = ["python", "-m", "pytest", "-q", "--tb=no", "--no-header",
            "--import-mode=importlib"] + files
    env = dict(os.environ)
    env["ICARUS_CANDIDATE_DIR"] = str(code_dir)
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=120,
                              cwd=str(_HOLDOUT_DIR), env=env)
        out = proc.stdout + proc.stderr
        return {
            "passed": _count(out, "passed"),
            "failed": _count(out, "failed"),
            "skipped": _count(out, "skipped"),
            "ran": True,
        }
    except Exception as e:
        return {"passed": 0, "failed": 0, "skipped": 0, "ran": False, "error": str(e)}


def _count(output: str, kind: str) -> int:
    import re
    m = re.search(rf"(\d+) {kind}", output)
    return int(m.group(1)) if m else 0


def check_decorative(
    candidate_dir: Path,
    parent_dir: Path,
    tier_target: str,
) -> dict:
    """Compare blind-holdout pass counts: candidate vs its parent.

    Returns:
      {
        "decorative": bool,        # candidate did not beat parent on holdout
        "capability_gain": bool,   # candidate passed strictly more holdout tests
        "candidate_holdout_passed": int,
        "parent_holdout_passed": int,
        "delta": int,
        "improvement_kind": "capability" | "metric_shaped" | "none",
        "detail": str,
      }
    """
    cand = _holdout_passed(candidate_dir, tier_target)
    parent = _holdout_passed(parent_dir, tier_target)
    c_pass, p_pass = cand["passed"], parent["passed"]
    delta = c_pass - p_pass

    if delta > 0:
        kind = "capability"
        decorative = False
        detail = (f"candidate passes {c_pass} blind-holdout tests vs parent's "
                  f"{p_pass} (+{delta}) -- genuine, oracle-verified capability gain")
    elif delta == 0 and c_pass > 0:
        kind = "metric_shaped"
        decorative = True
        detail = (f"candidate passes the same {c_pass} blind-holdout tests as "
                  f"parent -- no oracle-verified gain; likely decorative/metric-shaped")
    else:
        kind = "none" if c_pass == 0 else "metric_shaped"
        decorative = True
        detail = (f"candidate holdout pass={c_pass}, parent={p_pass}, delta={delta} "
                  f"-- no capability gain (possible regression)")

    return {
        "decorative": decorative,
        "capability_gain": delta > 0,
        "candidate_holdout_passed": c_pass,
        "parent_holdout_passed": p_pass,
        "delta": delta,
        "improvement_kind": kind,
        "detail": detail,
    }
