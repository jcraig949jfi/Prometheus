"""V0.6 section 4: sampling-power calibration. Precision ONLY -- no current is computed here.

    python proteus/v0_6/run_pilot.py

Duplicated samples from a frozen subset of live states at several sample counts, measuring the
row-wise total-variation distance between two independent estimates of the SAME kernel. This
estimates measurement precision so the production sample count can be frozen prospectively.

Nothing in this file inspects a current, a stationary distribution, or any direction. The frozen
subset is every 20th state in the canonical ordering, chosen by position and not by content.
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.v0_6 import livekernel as LK  # noqa: E402
from proteus.v0_6 import space  # noqa: E402

LADDER = [1000, 2000, 4000, 8000]
STRIDE = 20


def main():
    states, _tapes, _rules = space.regenerate_states()
    subset = states[::STRIDE]
    print(f"pilot on {len(subset)} of {len(states)} states (stride {STRIDE}); "
          f"precision only, no current computed")
    rows = []
    t0 = time.time()
    for n in LADDER:
        PA, _o, _no, _e = LK.measure_kernel_parallel(subset, n, seed=0x9101,
                                                     tag=f"pilot.A.{n}")
        PB, _o2, _n2, _e2 = LK.measure_kernel_parallel(subset, n, seed=0x9102, tag=f"pilot.B.{n}")
        tv = sorted(LK.compare(PA, PB, subset))
        m = len(tv)
        rec = {"samples": n, "median": tv[m // 2], "mean": statistics.fmean(tv),
               "p90": tv[int(0.90 * m)], "p95": tv[int(0.95 * m)],
               "p99": tv[min(m - 1, int(0.99 * m))], "max": tv[-1],
               "wall_s": time.time() - t0}
        rows.append(rec)
        print(f"  n={n:>6}: median {rec['median']:.5f}  p95 {rec['p95']:.5f}  "
              f"max {rec['max']:.5f}  ({rec['wall_s']:.0f}s cumulative)")

    # fit TV ~ c / sqrt(n) on the median and the 95th percentile
    def fit(key):
        cs = [r[key] * (r["samples"] ** 0.5) for r in rows]
        return statistics.fmean(cs)
    c_med, c_p95 = fit("median"), fit("p95")

    def required(target, c):
        return int((c / target) ** 2) + 1

    out = {
        "schema_version": "proteus.v0_6_pilot.v1",
        "subset_size": len(subset), "stride": STRIDE, "ladder": LADDER,
        "rows": rows,
        "fit": {"median_c": c_med, "p95_c": c_p95,
                "model": "TV = c / sqrt(n)"},
        "required_n": {
            "median_le_0.020": required(0.020, c_med),
            "median_le_0.010": required(0.010, c_med),
            "median_le_0.005": required(0.005, c_med),
            "p95_le_0.030": required(0.030, c_p95),
            "p95_le_0.020": required(0.020, c_p95),
            "p95_le_0.015": required(0.015, c_p95),
        },
        "throughput_states_x_samples_per_s": (sum(LADDER) * 2 * len(subset)) / (time.time() - t0),
        "wall_s": time.time() - t0,
    }
    with open(os.path.join(HERE, "RESULT_PILOT.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"  fit: median TV = {c_med:.4f}/sqrt(n), p95 TV = {c_p95:.4f}/sqrt(n)")
    print(f"  required n: median<=0.02 -> {out['required_n']['median_le_0.020']:,}; "
          f"median<=0.01 -> {out['required_n']['median_le_0.010']:,}; "
          f"p95<=0.02 -> {out['required_n']['p95_le_0.020']:,}")
    print(f"  aggregate throughput {out['throughput_states_x_samples_per_s']:,.0f} "
          f"state-samples/s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
