"""Substrate-Tester Fire #37 harness — Lane 17 (mutation testing on
prometheus_math/kill_vector.py — OUTSIDE the audit's sigma_kernel/
scope) + Lane 13 (canon-fuzz fresh seed).

Coordination: my fire #36 was last; no new parallel.

Lane 17 probe: the Tier 2 audit at sigma_kernel/tests/test_frozen_invariance.py
walks ONLY sigma_kernel/* via pkgutil.walk_packages. prometheus_math/
frozen dataclasses (KillComponent, KillVector, etc.) are NOT auto-
enrolled. This fire mutation-tests prometheus_math/kill_vector.py to
determine whether the existing test_kill_vector*.py suites catch
frozen-flips on those classes WITHOUT relying on the audit. If
survivors appear, the audit's scope-limitation is a real gap; if all
killed, the existing per-class tests are sufficient (and the audit's
scope-restriction is fine).

Lane 13 probe: standard canon-fuzz smoke with fresh seed. Cumulative
seed coverage adds reliability evidence.

Outputs:
  charon/diagnostics/substrate_tester_fire_37_results.json
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 17 — mutation testing OUTSIDE the sigma_kernel/ audit scope
# ---------------------------------------------------------------------------


def lane_17_mutation_outside_audit_scope() -> Dict[str, Any]:
    target = "prometheus_math/kill_vector.py"
    test_cmd = (
        "python -m pytest "
        "prometheus_math/tests/test_kill_vector.py "
        "prometheus_math/tests/test_kill_vector_v2.py "
        "prometheus_math/tests/test_kill_vector_precision.py "
        "-q --tb=no"
    )
    max_mutations = 8

    t0 = time.time()
    proc = subprocess.run(
        [
            "python", "-m", "prometheus_math.mutation_testing",
            "--target", target,
            "--test-cmd", test_cmd,
            "--max-mutations", str(max_mutations),
            "--timeout", "120",
        ],
        cwd=str(REPO),
        capture_output=True, text=True, timeout=1500,
        env={"PYTHONPATH": str(REPO), **os.environ},
    )
    elapsed = time.time() - t0

    progress_lines = [
        line for line in (proc.stderr or "").splitlines()
        if "[mutation" in line
    ]

    summary_line = ""
    score = None
    n_killed = n_survived = n_errored = n_skipped = 0
    for line in progress_lines:
        if "score=" in line:
            summary_line = line
            try:
                m = re.search(r"score=([\d.]+)", line)
                if m: score = float(m.group(1))
                m = re.search(r"killed=(\d+)", line)
                if m: n_killed = int(m.group(1))
                m = re.search(r"survived=(\d+)", line)
                if m: n_survived = int(m.group(1))
                m = re.search(r"errored=(\d+)", line)
                if m: n_errored = int(m.group(1))
                m = re.search(r"skipped=(\d+)", line)
                if m: n_skipped = int(m.group(1))
            except Exception:
                pass

    mutations: List[Dict[str, str]] = []
    for line in progress_lines:
        if "/" in line and "@" in line and "(" in line and "s)" in line:
            try:
                parts = line.split()
                idx_part = parts[1].rstrip("]")
                idx = idx_part.split("/")[0]
                verdict = parts[2]
                site = parts[4] if len(parts) > 4 else ""
                mutations.append({"idx": idx, "verdict": verdict, "site": site})
            except Exception:
                continue

    # Identify frozen-dataclass survivors specifically (sister to fire #25
    # / #15 / #7 pattern but on a module outside the audit's scope)
    frozen_dataclass_outcomes = []
    for m in mutations:
        if "boolean_not" in m["site"]:
            line_no = int(m["site"].split(":")[1]) if ":" in m["site"] else 0
            if line_no > 0:
                try:
                    src_text = (REPO / target).read_text(encoding="utf-8")
                    src_lines = src_text.splitlines()
                    if line_no <= len(src_lines):
                        src_line = src_lines[line_no - 1]
                        if "@dataclass(frozen=True)" in src_line:
                            frozen_dataclass_outcomes.append({
                                "site": m["site"],
                                "verdict": m["verdict"],
                                "src_line": src_line.strip(),
                            })
                except Exception:
                    pass

    return {
        "lane": "17_mutation_outside_audit_scope",
        "target": target,
        "test_cmd": test_cmd,
        "wall_clock_seconds": elapsed,
        "rc": proc.returncode,
        "summary_line": summary_line,
        "score": score,
        "n_killed": n_killed,
        "n_survived": n_survived,
        "n_errored": n_errored,
        "n_skipped": n_skipped,
        "mutations": mutations,
        "frozen_dataclass_outcomes": frozen_dataclass_outcomes,
        "frozen_survivors_count": sum(
            1 for o in frozen_dataclass_outcomes if o["verdict"] == "survived"
        ),
    }


# ---------------------------------------------------------------------------
# Lane 13 — canonicalization-fuzz smoke with fresh seed
# ---------------------------------------------------------------------------


def lane_13_canon_fuzz_fresh_seed() -> Dict[str, Any]:
    fuzz_test_path = REPO / "prometheus_math" / "tests" / "test_canonicalization_fuzz.py"
    if not fuzz_test_path.exists():
        return {
            "lane": "13_canon_fuzz",
            "status": "DORMANT",
            "reason": f"test missing at {fuzz_test_path}",
        }
    seed = "20260508_05"
    t0 = time.time()
    proc = subprocess.run(
        [
            "python", "-m", "pytest", str(fuzz_test_path),
            f"--hypothesis-seed={seed}",
            "-q", "--tb=short",
        ],
        cwd=str(REPO), capture_output=True, text=True, timeout=300,
        env={"PYTHONPATH": str(REPO), **os.environ},
    )
    elapsed = time.time() - t0
    rc = proc.returncode
    stdout = proc.stdout

    summary_line = ""
    n_passed = n_failed = 0
    for line in stdout.splitlines():
        if ("passed" in line or "failed" in line) and " in " in line:
            summary_line = line.strip()
        tokens = line.replace(",", "").split()
        for i, tok in enumerate(tokens):
            if tok == "passed" and i > 0:
                try: n_passed = int(tokens[i - 1])
                except (ValueError, IndexError): pass
            if tok == "failed" and i > 0:
                try: n_failed = int(tokens[i - 1])
                except (ValueError, IndexError): pass
    verdict = "PASS" if (rc == 0 and n_failed == 0 and n_passed > 0) else "FAIL"
    return {
        "lane": "13_canon_fuzz",
        "status": "LIVE",
        "hypothesis_seed": seed,
        "wall_clock_seconds": elapsed,
        "rc": rc,
        "n_passed": n_passed,
        "n_failed": n_failed,
        "summary_line": summary_line,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 37,
        "lanes": [17, 13],
        "lane_17": lane_17_mutation_outside_audit_scope(),
        "lane_13": lane_13_canon_fuzz_fresh_seed(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_37_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    l17 = summary["lane_17"]
    print(f"Lane 17: score={l17.get('score')}, killed={l17.get('n_killed')}, "
          f"survived={l17.get('n_survived')}")
    print(f"  Frozen-dataclass survivors: {l17.get('frozen_survivors_count', 0)}")
    l13 = summary["lane_13"]
    print(f"Lane 13: verdict={l13.get('verdict')}, passed={l13.get('n_passed')}")
    return summary


if __name__ == "__main__":
    run()
