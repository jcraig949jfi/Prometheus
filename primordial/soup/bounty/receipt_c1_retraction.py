"""File the retraction of lane B's C1 bounty (B-bounty-C1-cpu-d64r64). Run only after the rows are pushed.

usage: python -m primordial.soup.bounty.receipt_c1_retraction --git <pushed sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
RECHECK = ROOT / "ledger" / "rows" / "B" / "B-bounty-C1-recheck.jsonl"
ORIG = ROOT / "ledger" / "rows" / "B" / "B-bounty-C1-cpu-d64r64.jsonl"
H2H = ROOT / "ledger" / "rows" / "B" / "B-bounty-C1-cpu-d64r64-h2h.jsonl"
CLAIM = ("Retraction test of B-bounty-C1-cpu-d64r64 (which claimed nb_bucket_c3 beats C's numba_par at d64 r64 B4096, "
         "1.43x C's recorded 101.5k). Lane C's C1b (04ee00aa6) re-measured both interleaved under controlled load and "
         "found nb_bucket/numba_par 1.01 idle, 0.98 burn4, 0.93 burn8. Re-run in B's own harness and process (C's oracle, "
         "seed, RNG stream, time_cell; 5 interleaved rounds). The bounty claim stands only if nb_bucket_c3 is >= 1.2x "
         "numba_par here; otherwise it is retracted.")


def _jsonl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")] if p.exists() else []


def med(cells, impl):
    xs = [c["obs_per_s_wall"] for c in cells if c["impl"] == impl]
    return float(np.median(xs)) if xs else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    re_cells = [r for r in _jsonl(RECHECK) if r["kind"] == "cell"]
    orig_cells = [r for r in _jsonl(ORIG) if r["kind"] == "cell"]
    h2h_cells = [r for r in _jsonl(H2H) if r["kind"] == "cell"]
    nb, npar = med(re_cells, "nb_bucket_c3"), med(re_cells, "numba_par")
    ratio = nb / npar
    valid = all(c["valid"] and not c["timer_flag"] for c in re_cells)
    stands = ratio >= 1.2
    orig_np = [round(c["obs_per_s_wall"]) for c in orig_cells + h2h_cells if c["impl"] == "numba_par"]
    status = "INDETERMINATE" if not valid else ("PASS" if stands else "KILL")
    rec = {
        "lane": "B", "exp_id": "B-bounty-C1-retraction", "claim": CLAIM, "status": status,
        "refutes": "B-bounty-C1-cpu-d64r64 (lane B's own bounty; self-correction, not a bounty, no self-scoring)",
        "engineering": {
            "recheck_median_obs_per_s": {"nb_bucket_c3": round(nb), "numba_par": round(npar)},
            "recheck_ratio_nb_bucket_over_numba_par": round(ratio, 3),
            "recheck_rounds": len(re_cells) // 2,
            "recheck_host_cpu_per_cell": [c["host_cpu_pct"] for c in re_cells],
            "c1b_ratios": {"idle": 1.01, "sham8": 1.00, "burn4": 0.98, "burn8": 0.93},
            "original_bounty_numba_par_obs_per_s": orig_np,
        },
        "science": {
            "verdict": ("RETRACTED: nb_bucket_c3 has no CPU speed advantage over numba_par at d64 r64 B4096 on 3 threads "
                        f"(B recheck {ratio:.3f}x; C1b 0.93-1.01x)" if not stands else "claim reproduced"),
            "what_went_wrong": ("the bounty's 1.43x headline compared against C1's recorded numba_par 101.5k, which C1b "
                                "showed is pessimistic (idle 137-145k); B's same-process 2.1-2.6x came from numba_par "
                                f"running at {min(orig_np)}-{max(orig_np)} obs/s in that session versus "
                                f"~{round(npar / 1000)}k now in the same harness -- cause not established (threading layer "
                                "now omp, 3 threads; host load then ~30%, now ~30% during cells)"),
            "what_still_stands": ["nb_bucket is exact on C's oracle (all cells valid, additive control exact)",
                                  "C1c's GPU bucket kernel result is C's own measurement against its gather kernel",
                                  "B6/B6b fused-rollout speedups are vs a different baseline, interleaved, exact"],
            "lesson": ("a same-process ratio is not enough when the baseline runs far below its own history: a baseline "
                       "that slow is a signal to re-measure on another day or host before claiming"),
        },
        "controls": {
            "cheat": ("original bounty run: cheat_nb_bucket_skip_half invalid 5/5 rounds; recheck cells validated on C's "
                      f"float64 oracle: {sum(c['valid'] for c in re_cells)}/{len(re_cells)} valid"),
            "independent_replication": "lane C's C1b (04ee00aa6), 3 rounds x 4 load levels, reached the same conclusion first",
        },
        "rows": "primordial/ledger/rows/B/B-bounty-C1-recheck.jsonl (+ the original bounty rows for comparison)",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "refutes", "engineering", "science")}, indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
