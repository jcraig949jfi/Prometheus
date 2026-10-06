"""ER01 CPU/GPU conformance on the exact production path.

For every regime x perturbation arm, run er01_run.run_unit on the CuPy kernel
(runpod/aeth01_canary/aeth01_gpu_kernel.py) and on the independent NumPy text
(test/reference/gpu_aeth01.py) from the same seeds, and require:
  - identical state digest every --digest-every ticks and at the end;
  - identical measurement output (series + late window), excluding wall time
    and backend-identity fields.
Writes one JSON receipt. Exit 1 on any mismatch.

    python Aether/V2B/ER01/er01_conformance.py --n 64 --ticks 300 --out X.json
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import er01_run as E  # noqa: E402

IGNORE = {"wall_seconds", "backend", "gpu", "host_rss_bytes"}


def strip(res):
    return {k: v for k, v in res.items() if k not in IGNORE}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--ticks", type=int, default=300)
    ap.add_argument("--late", type=int, default=100)
    ap.add_argument("--bin", type=int, default=50)
    ap.add_argument("--digest-every", type=int, default=10)
    ap.add_argument("--seeds", default="0,-1")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cells, ok = [], True
    for regime in sorted(E.REGIMES):
        for pert in sorted(E.PERTURBATION):
            for s in [int(x) for x in a.seeds.split(",")]:
                t0 = time.time()
                g = E.run_unit("gpu", regime, pert, s, a.n, a.ticks, a.bin, a.late, a.digest_every)
                c = E.run_unit("cpu", regime, pert, s, a.n, a.ticks, a.bin, a.late, a.digest_every)
                same_dig = g["digests"] == c["digests"] and g["final_digest"] == c["final_digest"]
                same_all = strip(g) == strip(c)
                ok &= same_dig and same_all
                cells.append({"regime": regime, "pert": pert, "seed_index": s,
                              "digests_compared": len(g["digests"]) + 1,
                              "digest_equal": same_dig, "measurements_equal": same_all,
                              "final_digest": g["final_digest"],
                              "late_tmpl_change": g["late_window"]["tmpl_change_site_per_tick"],
                              "seconds": round(time.time() - t0, 2)})
                print(json.dumps(cells[-1]), file=sys.stderr, flush=True)
    out = {"schema": "aether.er01.conformance.v1", "n": a.n, "ticks": a.ticks,
           "regime_table_hash": E.regime_table_hash(), "all_equal": ok, "cells": cells}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("ALL_EQUAL" if ok else "MISMATCH", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
