"""Per-stratum reductions of the dev margin sweep (checklist A4, B9, C3, E4, E5, E6, H1). Rules declared here BEFORE the
sweep's rows are read; the numbers they yield are frozen into the prereg.

For a stratum (family x level x generator) with a frozen arm set (FROZEN_SELECTION.json; an EMPTY stratum is UNTESTED):
  MARGIN      97.5th percentile of |AC_a - AC_b| over worlds x families (the replicate pair: learner seed + test
              bootstrap). "Matched" = |difference| <= MARGIN; a WIN needs > 2 x MARGIN (H1).
  N_MIN       the smallest test size n in {16, 32, 64, 128, 256} with 1.96 x median bootstrap SD(n) <= MARGIN / 2 (E4),
              where the median is over arms x worlds. The stratum is ELIGIBLE iff N_MIN exists and the median never-seen
              test count >= N_MIN; otherwise UNTESTED.
  X (gate)    = MARGIN. LEARNABLE iff the median over worlds of max_arm(AC_a) - N1 > X (arm-symmetric, E5); otherwise
              UNTESTED.
  B*          the smallest reservoir rung (random eviction) whose median AC >= median AC(full) - MARGIN (C3). "none" if
              only the full store qualifies. END_OK iff |median AC(random, full) - median AC(L-R)| <= MARGIN.
  POSCTL      PASS iff median(oracle - random) at B = c/2 > MARGIN (E6). Otherwise INDISCRIMINATE reads UNRESOLVED there.
  CAP         the max over rungs of the median cap-hit fraction. A rung with median cap_frac > 0.1 is flagged as a lower
              bound (B9).
  VISITS      the median visits/cell, reported beside every verdict (E6)."""
import glob
import json
import os

import numpy as np

HERE = os.path.dirname(__file__)
RUNG_ORDER = ["c/8", "c/4", "c/2", "c", "2c", "full"]
SIZES = [16, 32, 64, 128, 256]


def reduce_stratum(rows, frozen):
    ok = [r for r in rows if r["status"] == "OK" and r.get("arms")]
    out = dict(n_rows=len(rows), n_ok=len(ok), status_counts={s: sum(r["status"] == s for r in rows)
                                                              for s in set(r["status"] for r in rows)})
    out["visits_per_cell"] = float(np.median([r["visits_per_cell"] for r in rows])) if rows else None
    if frozen.get("n_worlds", 0) == 0 or not ok:
        return dict(out, verdict_frame="UNTESTED", reason="no frozen arms (EMPTY stratum) or no OK rows")
    diffs = [abs(v["AC_a"] - v["AC_b"]) for r in ok for v in r["arms"].values()]
    margin = float(np.percentile(diffs, 97.5))
    sd_n = {}
    for n in SIZES:
        v = [a["ci_sd"][str(n)] for r in ok for a in r["arms"].values() if str(n) in a["ci_sd"]]
        sd_n[n] = float(np.median(v)) if v else None
    n_min = next((n for n in SIZES if sd_n[n] is not None and 1.96 * sd_n[n] <= margin / 2), None)
    med_test = float(np.median([r["n_test"] for r in ok]))
    eligible = n_min is not None and med_test >= n_min
    gains = [max(a["AC_a"] for a in r["arms"].values()) - r["N1"] for r in ok]
    learnable = float(np.median(gains)) > margin
    lad = {}
    for rung in RUNG_ORDER + ["L-R"]:
        key = "L-R|full" if rung == "L-R" else f"random|{rung}"
        v = [r["ladder"][key]["AC"] for r in ok if key in r["ladder"]]
        cf = [r["ladder"][key]["iters"]["cap_frac"] for r in ok if key in r["ladder"] and r["ladder"][key]["iters"]["cap_frac"] is not None]
        lad[rung] = dict(median_AC=float(np.median(v)) if v else None, n=len(v),
                         median_cap_frac=float(np.median(cf)) if cf else None)
    full = lad["full"]["median_AC"]
    bstar = next((rg for rg in RUNG_ORDER if lad[rg]["median_AC"] is not None and full is not None
                  and lad[rg]["median_AC"] >= full - margin), None)
    end_ok = full is not None and lad["L-R"]["median_AC"] is not None and abs(full - lad["L-R"]["median_AC"]) <= margin
    pcd = [r["posctl"]["oracle"] - r["posctl"]["random"] for r in ok if r.get("posctl")]
    posctl = (float(np.median(pcd)) > margin) if pcd else None
    capflags = [rg for rg in RUNG_ORDER if (lad[rg]["median_cap_frac"] or 0) > 0.1]
    return dict(out, margin=margin, win_threshold=2 * margin, sd_by_n=sd_n, n_min=n_min, median_n_test=med_test,
                eligible=eligible, gate_X=margin, median_gain_over_N1=float(np.median(gains)), learnable=learnable,
                ladder=lad, B_star=bstar if bstar != "full" else "none", end_matches_LR=end_ok,
                posctl_median_gap=float(np.median(pcd)) if pcd else None, posctl_pass=posctl, cap_bound_rungs=capflags,
                verdict_frame=("TESTABLE" if eligible and learnable else "UNTESTED"))


def main():
    fz = json.load(open(os.path.join(HERE, "FROZEN_SELECTION.json")))["choices"]
    res = {}
    for key, fr in fz.items():
        f, l, g = key.split("|")
        fn = os.path.join(HERE, "dev", "margins", f"{f}__{l}__{g}.jsonl")
        rows = [json.loads(x) for x in open(fn)] if os.path.exists(fn) else []
        res[key] = reduce_stratum(rows, fr)
    with open(os.path.join(HERE, "dev", "margins_reduced.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    return res


if __name__ == "__main__":
    r = main()
    for k, v in r.items():
        if v.get("margin") is None:
            print(k.ljust(28), v["verdict_frame"], v.get("reason", ""), "rows", v["n_rows"])
            continue
        print(k.ljust(28), v["verdict_frame"].ljust(9), "m %.2f" % v["margin"], "nmin", v["n_min"], "ntest %d" % v["median_n_test"],
              "gain %.2f" % v["median_gain_over_N1"], "B*", v["B_star"], "endOK", v["end_matches_LR"],
              "pc", v["posctl_pass"], "vis %.1f" % v["visits_per_cell"], "cap", v["cap_bound_rungs"])
