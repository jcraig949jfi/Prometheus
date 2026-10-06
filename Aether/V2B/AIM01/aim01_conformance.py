"""AIM01 Flight-1 qualification checks (order s19, s24). Writes one JSON receipt; exit 1 on any failure.

 C1 L0 continuity: aim01 L0 D50 seed k == ER01 runner R0 P0 seed k (state digests at every checkpoint,
    and late turnover / ever_changed / frozen_strict equal) -- also proves the observer instrumentation
    does not change dynamics (ER01's runner runs the kernel without the observer).
 C2 CPU/GPU equality for L0 and L1 at every density (digests every checkpoint + full summary + series).
 C3 paired initialization: per seed, densities differ ONLY in opcode, only at sites WRITE in the
    denser world, WRITE sets nested D25 <= D50 <= D75.
 C4 RAW/EFFECT: L0 RAW == EFFECT exactly; L1 subset_violations == 0 (no EFFECT change without an
    executed write) and RAW turnover > EFFECT turnover.
 C5 reaim changes target-support behaviour at all (L1 ever_targeted > L0 at matched seed/density).
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ER01"))
import aim01_run as A  # noqa: E402
import er01_run as E  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402

IGN = {"wall_seconds", "backend", "gpu", "host_rss_bytes"}


def strip(r):
    return {k: v for k, v in r.items() if k not in IGN}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--ticks", type=int, default=300)
    ap.add_argument("--late", type=int, default=100)
    ap.add_argument("--bin", type=int, default=50)
    ap.add_argument("--every", type=int, default=10)
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(",")]
    rec, ok = {"n": a.n, "ticks": a.ticks, "table_hash": A.table_hash()}, True

    c1 = []
    for k in seeds:
        er = E.run_unit("gpu", "R0", "P0", k, a.n, a.ticks, a.bin, a.late, a.every)
        am = A.run_unit("gpu", "L0", "D50", k, a.n, a.ticks, a.bin, a.late, a.every)
        s = am["summary"]
        lw = er["late_window"]
        row = {"seed": k,
               "digests_equal": er["digests"] == am["digests"] and er["final_digest"] == am["final_digest"],
               "late_turnover_equal": lw["tmpl_change_site_per_tick"] == s["late_turnover_eff"],
               "frozen_strict_equal": lw["frozen_strict"] == s["frozen_strict_eff"],
               "ever_changed_equal": er["series"][-1]["ever_changed"] == s["ever_changed_eff"],
               "frozen_net64_equal": lw["frozen_net64"] == s["frozen_net64_eff"]}
        c1.append(row)
        ok &= all(v for kk, v in row.items() if kk != "seed")
    rec["C1_L0_equals_ER01"] = c1

    c2, units = [], {}
    for law in sorted(A.LAWS):
        for d in sorted(A.DENSITIES):
            for k in seeds:
                g = A.run_unit("gpu", law, d, k, a.n, a.ticks, a.bin, a.late, a.every)
                c = A.run_unit("cpu", law, d, k, a.n, a.ticks, a.bin, a.late, a.every)
                eq = strip(g) == strip(c)
                c2.append({"law": law, "dens": d, "seed": k, "equal": eq, "final": g["final_digest"]})
                ok &= eq
                units[(law, d, k)] = g
    rec["C2_cpu_gpu"] = c2

    c3 = []
    for k in seeds:
        w = {d: R.build_initial(R.SPARSE_SOUP, a.n, a.n, A.RNG_SEED_BASE + k, write_density=v)[0]
             for d, v in A.DENSITIES.items()}
        others_equal = all(np.array_equal(w["D25"][i], w[d][i]) for d in w for i in range(1, 5))
        iw = {d: w[d][0] == 1 for d in w}
        nested = bool((~iw["D25"] | iw["D50"]).all() and (~iw["D50"] | iw["D75"]).all())
        diff_only_new_write = all(bool(((w["D25"][0] != w[d][0]) <= (iw[d] & ~iw["D25"])).all())
                                  for d in ("D50", "D75"))
        row = {"seed": k, "non_opcode_fields_identical": others_equal, "write_sets_nested": nested,
               "opcode_differs_only_at_added_writers": diff_only_new_write,
               "write_frac": {d: float(iw[d].mean()) for d in iw}}
        c3.append(row)
        ok &= others_equal and nested and diff_only_new_write
    rec["C3_paired_init"] = c3

    c4, c5 = [], []
    for (law, d, k), u in units.items():
        s = u["summary"]
        if law == "L0":
            eq = (s["late_turnover_raw"] == s["late_turnover_eff"] and s["ever_changed_raw"] == s["ever_changed_eff"]
                  and all(r["raw_turnover"] == r["eff_turnover"] and r["reaim_rate"] == 0 for r in u["series"]))
            c4.append({"law": law, "dens": d, "seed": k, "raw_equals_eff": eq, "subset_violations": s["subset_violations"]})
            ok &= eq and s["subset_violations"] == 0
            l1 = units[("L1", d, k)]["summary"]
            c5.append({"dens": d, "seed": k, "ever_targeted_site_L0": s["ever_targeted_site"],
                       "ever_targeted_site_L1": l1["ever_targeted_site"],
                       "L1_targets_more": l1["ever_targeted_site"] > s["ever_targeted_site"]})
            ok &= l1["ever_targeted_site"] > s["ever_targeted_site"]
        else:
            good = s["subset_violations"] == 0 and s["late_turnover_raw"] > s["late_turnover_eff"]
            c4.append({"law": law, "dens": d, "seed": k, "subset_violations": s["subset_violations"],
                       "raw_gt_eff": s["late_turnover_raw"] > s["late_turnover_eff"],
                       "mean_reaim_rate": float(np.mean([r["reaim_rate"] for r in u["series"]]))})
            ok &= good
    rec["C4_raw_effect"] = c4
    rec["C5_reaim_changes_targeting"] = c5
    rec["all_ok"] = bool(ok)
    json.dump(rec, open(a.out, "w"), indent=1)
    print("ALL_OK" if ok else "FAILED", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
