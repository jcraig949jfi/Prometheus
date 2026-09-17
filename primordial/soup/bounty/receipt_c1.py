"""File the lane-B C1 bounty receipt from committed rows. Run AFTER rebase.

usage: python -m primordial.soup.bounty.receipt_c1 --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B"
MAIN = "B-bounty-C1-cpu-d64r64.jsonl"
H2H = "B-bounty-C1-cpu-d64r64-h2h.jsonl"
C_REC = {"numba_par": 101505.1, "np_bucket": 91777.8, "torch_gpu_e2e": 179408.3}
CLAIM = ("Lane-B bounty on C1 (C's bait: beat numba_par at d64 r64 B4096 on CPU). Same cell, same policy seed "
         "and RNG stream, C's time_cell + compare + ref64 oracle, baselines re-measured in the same process. "
         "Predicted: nb_bucket (per-core counting sort by digit, contiguous saxpy runs) >= 1.5x numba_par; "
         "np_bucket_shard3 >= 1.2x; no CPU form reaches torch_gpu_e2e's 179k.")


def _jsonl(name):
    p = ROWS / name
    return [json.loads(x) for x in open(p, encoding="utf-8")] if p.exists() else []


def med(cells, impl):
    xs = [c["obs_per_s_wall"] for c in cells if c["impl"] == impl]
    return float(np.median(xs)) if xs else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = _jsonl(MAIN)
    cells = [r for r in rows if r["kind"] == "cell"]
    h2h = [r for r in _jsonl(H2H) if r["kind"] == "cell"]
    pos = [r for r in rows if r["kind"] == "positive_control"]
    lc = [r for r in rows if r["kind"] == "logit_check"]
    impls = sorted({c["impl"] for c in cells})
    honest = [i for i in impls if not i.startswith("cheat")]
    best = max(honest, key=lambda i: med(cells, i))
    nb, sh = med(cells, "nb_bucket_c3"), med(cells, "np_bucket_shard3")
    npar = med(cells, "numba_par")
    h_nb, h_np = med(h2h, "nb_bucket_c3"), med(h2h, "numba_par")
    valid_all = all(c["valid"] and not c["timer_flag"] for c in cells if not c["cheat"])
    valid_h2h = all(c["valid"] and not c["timer_flag"] for c in h2h)
    cheat = [c for c in cells if c["cheat"]]
    cheat_caught = bool(cheat) and all(not c["valid"] for c in cheat)
    pos_ok = bool(pos) and all(r["exact"] for r in pos)
    best_cpu = med(cells, best)

    def verdict(x, bar):
        return "CONFIRMED" if x >= bar else "WRONG"

    rec = {
        "lane": "B", "exp_id": "B-bounty-C1-cpu-d64r64", "claim": CLAIM,
        "status": "PASS" if (valid_all and valid_h2h and cheat_caught and pos_ok and best_cpu > C_REC["numba_par"])
        else "FAIL",
        "refutes": "C1-tt-policy-crossover: numba_par as best CPU at d64 r64 B4096 (and the GPU/CPU ratio there)",
        "engineering": {
            "cell": {"d": 64, "r": 64, "A": 8, "B": 4096, "threads": 3},
            "median_obs_per_s_wall_main": {i: round(med(cells, i)) for i in impls},
            "median_obs_per_s_wall_h2h": {"nb_bucket_c3": round(h_nb) if h_nb else None,
                                          "numba_par": round(h_np) if h_np else None},
            "c_recorded_obs_per_s_wall": C_REC,
            "best_cpu_impl": best,
            "best_cpu_x_c_recorded_numba_par": round(best_cpu / C_REC["numba_par"], 3),
            "best_cpu_x_same_process_numba_par": round(best_cpu / npar, 3),
            "gpu_e2e_over_best_cpu_was": round(C_REC["torch_gpu_e2e"] / C_REC["numba_par"], 3),
            "gpu_e2e_over_best_cpu_now": round(C_REC["torch_gpu_e2e"] / best_cpu, 3),
            "caveats": ["numba_par re-measured BELOW C's recorded value in this session; the conservative ratio "
                        "uses C's recorded 101.5k", "GPU numbers are C's recorded ones, not re-measured",
                        "only B=4096 at d64 r64 measured; smaller B not claimed"],
        },
        "science": {
            "hypothesis_scoring": {
                "nb_bucket_ge_1.5x_numba_par": (f"same-process {verdict(nb / npar, 1.5)} ({nb / npar:.2f}x); "
                                                f"vs C recorded {verdict(nb / C_REC['numba_par'], 1.5)} "
                                                f"({nb / C_REC['numba_par']:.2f}x)"),
                "np_bucket_shard3_ge_1.2x": (f"same-process {verdict(sh / npar, 1.2)} ({sh / npar:.2f}x); "
                                             f"vs C recorded {verdict(sh / C_REC['numba_par'], 1.2)} "
                                             f"({sh / C_REC['numba_par']:.2f}x)"),
                "no_cpu_reaches_gpu_e2e_179k": ("CONFIRMED" if best_cpu < C_REC["torch_gpu_e2e"] else "WRONG")
                                               + f" (best CPU median {best_cpu:.0f})",
            },
            "mechanism": ("grouping rows by digit keeps one 64x64 core hot in cache per run of rows; "
                          "numba_par touches a different core matrix for every sample at every step"),
            "mechanism_status": "hypothesis: locality not measured directly (no cache counters)",
        },
        "controls": {
            "cheat": (f"cheat_nb_bucket_skip_half invalid {sum(not c['valid'] for c in cheat)}/{len(cheat)} rounds; "
                      f"logit check diff {next((r['max_abs_logit_diff'] for r in lc if r['impl'].startswith('cheat')), None):.3f}"),
            "positive": f"C additive TT exact for {sum(r['exact'] for r in pos)}/{len(pos)} honest impls",
            "logit_check": {r["impl"]: r["max_abs_logit_diff"] for r in lc},
        },
        "rows": f"primordial/ledger/rows/B/{MAIN} + {H2H}",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "refutes", "science")}, indent=1))
    print(json.dumps(rec["engineering"], indent=1)[:1500])
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
