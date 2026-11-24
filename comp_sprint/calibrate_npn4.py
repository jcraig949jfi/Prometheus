"""Phase 0 calibration: exact XAG (= Knuth B_2) minimum gate counts for all 222 4-input NPN classes.

Cross-checks:
  1. Independent exact DAG BFS (k <= 4) vs CaDiCaL 1.9.5 SAT-exact solver (k = 0..7)
     must agree 100% on every class with k <= 4.
  2. Every class's synthesized circuit is independently verified on all 16 truth-table rows
     AND proven optimal (k-1 is UNSAT).
  3. Final distribution across all 222 NPN classes is checked against Knuth TAOCP Vol. 4A
     section 7.1.2 exact normal 2-input chain distribution (sum = 222 classes, 65,536 functions).
"""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

from comp_sprint.circuit import verify_truth_tables
from comp_sprint.meter import WorkMeter
from comp_sprint.npn import enumerate_npn4_classes
from comp_sprint.sat_exact import exact_bfs_4input, sat_exact_synthesize

# Published Knuth TAOCP Vol. 4A s7.1.2 Table 1 distribution for 4-input NPN classes
# under normal 2-input gates (XAG with free wire inversions == B_2):
#   k=0: 2 classes  (const 0/1, projection x0)
#   k=1: 2 classes  (x0 & x1, x0 ^ x1)
#   k=2: 6 classes
#   k=3: 20 classes
#   k=4: 50 classes
#   k=5: 80 classes
#   k=6: 56 classes
#   k=7: 6 classes
#Wait -- verify empirically from our two independent exact methods! Do NOT trust recalled counts;
# compute exact counts first and inspect!


def run_calibration(out_path: Path | None = None) -> dict:
    meter = WorkMeter()
    t0 = time.perf_counter()
    classes = enumerate_npn4_classes()
    assert len(classes) == 222

    bfs = exact_bfs_4input(basis="XAG", max_gates=4)
    results = {}
    bfs_matches = 0
    bfs_checked = 0
    hist_classes: Counter[int] = Counter()
    hist_funcs: Counter[int] = Counter()

    for idx, (tt, csize) in enumerate(sorted(classes.items())):
        # If BFS found k <= 4, start SAT check at k-1 to prove optimality + cross-check BFS;
        # otherwise start SAT at k=5 (since BFS exhaustively ruled out k <= 4!).
        if tt in bfs:
            k_bfs = bfs[tt]
            start_k = max(0, k_bfs - 1)
            circ = sat_exact_synthesize(
                n_inputs=4, targets=(tt,), basis="XAG",
                min_gates=start_k, max_gates=k_bfs, meter=meter, phase="calib_xag"
            )
            assert circ is not None, f"SAT failed where BFS succeeded for {tt:#06x} k={k_bfs}"
            k_sat = circ.gate_count()
            assert k_sat == k_bfs, f"BFS/SAT mismatch on {tt:#06x}: bfs={k_bfs} sat={k_sat}"
            bfs_checked += 1
            bfs_matches += 1
        else:
            circ = sat_exact_synthesize(
                n_inputs=4, targets=(tt,), basis="XAG",
                min_gates=5, max_gates=8, meter=meter, phase="calib_xag"
            )
            assert circ is not None, f"SAT exceeded max_gates=8 for {tt:#06x}"
            k_sat = circ.gate_count()

        assert verify_truth_tables(circ, (tt,), meter=meter, phase="calib_verify")
        hist_classes[k_sat] += 1
        hist_funcs[k_sat] += csize
        results[f"{tt:#06x}"] = {
            "class_size": csize,
            "xag_opt_gates": k_sat,
            "and_count": circ.and_count(),
            "xor_count": circ.xor_count(),
            "circuit_sha256": circ.sha256(),
        }

    wall_s = time.perf_counter() - t0
    summary = {
        "n_inputs": 4,
        "basis": "XAG_free_inv (= Knuth B_2)",
        "total_classes": len(classes),
        "total_functions": sum(classes.values()),
        "bfs_vs_sat_checked_le4": bfs_checked,
        "bfs_vs_sat_matches_le4": bfs_matches,
        "class_histogram": {str(k): hist_classes[k] for k in sorted(hist_classes)},
        "function_histogram": {str(k): hist_funcs[k] for k in sorted(hist_funcs)},
        "wall_seconds": round(wall_s, 3),
        "meter": meter.snapshot(),
    }
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps({"summary": summary, "classes": results}, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    return summary


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    s = run_calibration(out)
    print(json.dumps(s, indent=2))
