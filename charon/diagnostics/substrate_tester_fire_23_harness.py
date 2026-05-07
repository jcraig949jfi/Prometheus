"""Substrate-Tester Fire #23 harness — Lane 14 (replay-determinism, fresh
seed smoke) + Lane 7 (precision-gradient on INCONCLUSIVE entry #5).

Coordination: parallel fire #22 (commit 9b9ce4f8) covered lanes 11 + 10
with 0 tickets. P0 ticket T-ST-fire17-001 still OPEN; deferred re-probe.

Lane 14: smoke-test the replay-determinism pytest harness with a fresh
Hypothesis seed. Last covered fire #12 (5 fires ago).

Lane 7: continue the deg-14 ±5 INCONCLUSIVE classification series. Fires
covered entries:
  #1 (fire #1): [1,-4,5,0,-5,4,-1,0] -> M=1.0 (cyclotomic)
  #2 (fire #9): [1,-3,1,5,-5,-1,3,-2] -> M=1.0 (cyclotomic)
  #3 (fire #17): [1,-3,2,1,0,-2,1,0] -> M=1.17628 (Lehmer × cyclotomic)
  #4 (fire #18): [1,1,-1,0,0,1,-1,-1] -> M=1.7433 (Salem cluster)
This fire covers entry #5: [1,0,1,-1,1,-1,0,1].

Outputs:
  charon/diagnostics/substrate_tester_fire_23_results.json
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 14 — replay-determinism fresh-seed smoke
# ---------------------------------------------------------------------------


def lane_14_replay_determinism_smoke() -> Dict[str, Any]:
    fuzz_test_path = REPO / "prometheus_math" / "tests" / "test_replay_capsule_determinism.py"
    if not fuzz_test_path.exists():
        return {
            "lane": "14_replay_determinism",
            "status": "DORMANT",
            "reason": f"test missing at {fuzz_test_path}",
            "tests": [],
        }
    seed = "20260507_23"
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
    for line in stdout.splitlines():
        if ("passed" in line or "failed" in line) and " in " in line:
            summary_line = line.strip()
    n_passed = 0
    n_failed = 0
    for line in stdout.splitlines():
        if "passed" in line and "in" in line:
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
        "lane": "14_replay_determinism",
        "status": "LIVE",
        "hypothesis_seed": seed,
        "wall_clock_seconds": elapsed,
        "rc": rc,
        "n_passed": n_passed,
        "n_failed": n_failed,
        "summary_line": summary_line,
        "verdict": verdict,
        "stdout_tail": stdout[-1200:] if rc != 0 else "",
    }


# ---------------------------------------------------------------------------
# Lane 7 — precision-gradient on INCONCLUSIVE entry #5
# ---------------------------------------------------------------------------


def lane_7_inconclusive_entry_5() -> Dict[str, Any]:
    from prometheus_math.lehmer_path_a import high_precision_M_via_factor

    half = [1, 0, 1, -1, 1, -1, 0, 1]
    coeffs_ascending = list(half) + list(reversed(half[:-1]))

    dps_ladder = [10, 30, 60, 100, 200]
    results = []
    for dps in dps_ladder:
        t0 = time.time()
        try:
            out = high_precision_M_via_factor(
                coeffs_ascending=coeffs_ascending,
                nroots_precision=dps,
            )
            elapsed = time.time() - t0
            results.append({
                "dps": dps,
                "elapsed_s": elapsed,
                "status": out.get("status"),
                "M": str(out.get("M_clean") or out.get("M") or "n/a"),
                "method": out.get("method"),
                "factorization_label": out.get("factorization_label"),
            })
        except Exception as exc:  # noqa: BLE001
            results.append({"dps": dps, "error": repr(exc)[:200]})

    M_floats: List[Any] = []
    for r in results:
        if "error" in r:
            M_floats.append(None); continue
        v = r.get("M")
        try:
            M_floats.append(None if v in (None, "n/a") else float(str(v)))
        except (TypeError, ValueError):
            M_floats.append(None)
    M_finite = [v for v in M_floats if v is not None]
    M_spread = (max(M_finite) - min(M_finite)) if M_finite else 0.0
    band_status_per_dps = [
        ("in_band" if (v is not None and 1.001 <= v <= 1.18)
         else "out_of_band" if v is not None
         else "no_value")
        for v in M_floats
    ]
    verdict_oscillates = len(set(band_status_per_dps)) > 1

    # Classify: cyclotomic (M=1), Lehmer (M=1.17628...), Salem (M>1.18), other
    classification = "unknown"
    if M_finite:
        max_M = max(M_finite)
        if abs(max_M - 1.0) < 1e-6:
            classification = "cyclotomic_product"
        elif abs(max_M - 1.17628081826) < 1e-6:
            classification = "lehmer_class"
        elif max_M > 1.18:
            classification = "salem_cluster"
        elif 1.001 <= max_M <= 1.18:
            classification = "novel_in_band"
        else:
            classification = f"other_M={max_M:.6f}"

    return {
        "lane": "7_precision_gradient_entry_5",
        "coeffs_ascending": coeffs_ascending,
        "dps_ladder": dps_ladder,
        "results": results,
        "M_values_at_each_dps": M_floats,
        "M_spread": M_spread,
        "band_status_at_each_dps": band_status_per_dps,
        "verdict_oscillates": verdict_oscillates,
        "classification": classification,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run() -> Dict[str, Any]:
    summary = {
        "fire": 23,
        "lanes": [14, 7],
        "lane_14": lane_14_replay_determinism_smoke(),
        "lane_7": lane_7_inconclusive_entry_5(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_23_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    l14 = summary["lane_14"]
    print(f"Lane 14: verdict={l14.get('verdict')}, passed={l14.get('n_passed')}, failed={l14.get('n_failed')}")
    l7 = summary["lane_7"]
    print(f"Lane 7: classification={l7['classification']}, M_spread={l7['M_spread']:.6e}, oscillates={l7['verdict_oscillates']}")
    print(f"  M values: {l7['M_values_at_each_dps']}")
    return summary


if __name__ == "__main__":
    run()
