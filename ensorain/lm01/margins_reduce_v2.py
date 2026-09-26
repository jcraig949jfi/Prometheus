"""Per-stratum dev reductions under the OPERATOR RULINGS of 2026-09-26 (roles/Ensorain/prompts/2026-09-26_lm01_operator_rulings/).
The v1 rules (margins_reduce.py, noise-derived margin, size grid capped at 256) are kept as the record and NOT used.

GOVERNING TOLERANCE DELTA = 0.30 AC (item 2). No margin is derived from any arm's own instability; noise enters only
through the confidence interval. CI = 90% two-sided over worlds (Student t), equivalent to one-sided alpha .05 per
direction (TOST).
  EQUIVALENT   CI of the paired difference lies inside (-DELTA, +DELTA)
  WIN          CI lies entirely beyond +DELTA (or beyond -DELTA for the other direction)
SENSITIVITY at 0.15 and 0.60 AC: descriptive only; never replaces 0.30.

Per stratum:
  N_MIN (item 1 / D9)  the smallest n among {16, 32, 64, 128, 256, the stratum's median n_test} with
                       1.96 x median bootstrap SD(n) <= DELTA / 2. ELIGIBLE iff N_MIN exists and median n_test >= N_MIN.
  LEARNABLE (gate)     lower CI bound of mean(max_arm AC - N1) > DELTA (arm-symmetric).
  TESTABLE             ELIGIBLE and LEARNABLE; otherwise UNTESTED.
  POSCTL (E6)          lower CI bound of mean(oracle - random eviction at B = c/2) > DELTA -> PASS.
  END                  mean(warm full reservoir - L-R) with its CI. Both endpoints are REPORTED (item 4).
  B*_preview           the smallest random rung with (full - rung) EQUIVALENT (dev preview only; not a result).
  N_REP                the replication block (s6.7): ceil(((1.645 + 0.842) x sd_d / DELTA)^2), 80% power at a true
                       effect of 2 x DELTA (floor REP_MIN = 8), where sd_d = max between-world SD of the headline (full - c) and eviction
                       (selective - random at c/4) paired differences. UNREPLICATED if N_REP > 64.
  STABILITY            per family: replicate p97.5 and the fraction of worlds with |a - b| > 1.0 AC (seed-mode
                       indicator); REPORTED only.
F5 rows are read from dev/margins_f5real/ (item 3, the repaired scale). The all_cells F5 rows remain the record of the old
interpretation."""
import json
import math
import os

import numpy as np
from scipy import stats

HERE = os.path.dirname(__file__)
DELTA = 0.30
SENS = (0.15, 0.60)
SIZES = [16, 32, 64, 128, 256]
RUNGS = ["c/8", "c/4", "c/2", "c", "2c"]
REP_CAP = 64
REP_MIN = 8                     # declared floor: a replication block smaller than 8 worlds is not a meaningful t-interval


def ci(x, level=0.90):
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    if len(x) < 3:
        return None
    m, se = float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x)))
    h = float(stats.t.ppf(0.5 + level / 2, len(x) - 1)) * se
    return dict(mean=m, lo=m - h, hi=m + h, n=len(x), sd=float(x.std(ddof=1)))


def equivalent(c, d):
    return c is not None and -d < c["lo"] and c["hi"] < d


def _rows(key):
    f = key.split("|")[0]
    sub = "margins_f5real" if f == "F5_nuisance" else "margins"
    fn = os.path.join(HERE, "dev", sub, key.replace("|", "__") + ".jsonl")
    return ([json.loads(x) for x in open(fn)] if os.path.exists(fn) else []), sub


def reduce_stratum(key, frozen, delta=DELTA):
    rows, src = _rows(key)
    ok = [r for r in rows if r["status"] == "OK" and r.get("arms")]
    out = dict(source=src, n_rows=len(rows), n_ok=len(ok),
               visits_per_cell=float(np.median([r["visits_per_cell"] for r in rows])) if rows else None)
    if frozen.get("n_worlds", 0) == 0 or not ok:
        return dict(out, frame="UNTESTED", reason="EMPTY stratum (no frozen arms) or no OK rows")
    if len(ok) < 3:                                   # declared: a CI needs >= 3 usable dev worlds
        return dict(out, frame="UNTESTED", reason=f"only {len(ok)} usable dev worlds (< 3; too few never-seen cells)")
    med_test = float(np.median([r["n_test"] for r in ok]))
    sizes = sorted(set(SIZES + [int(med_test)]))
    sd_n = {}
    for n in sizes:
        v = [a["ci_sd"][str(n)] for r in ok for a in r["arms"].values() if str(n) in a["ci_sd"]]
        if n == int(med_test):
            v += [a["ci_sd"][str(r["n_test"])] for r in ok for a in r["arms"].values() if str(r["n_test"]) in a["ci_sd"]]
        sd_n[n] = float(np.median(v)) if v else None
    n_min = next((n for n in sizes if sd_n[n] is not None and 1.96 * sd_n[n] <= delta / 2), None)
    eligible = n_min is not None and med_test >= n_min
    gain = ci([max(a["AC_a"] for a in r["arms"].values()) - r["N1"] for r in ok])
    learnable = gain is not None and gain["lo"] > delta
    full = [r["ladder"].get("random|full", {}).get("AC") for r in ok]
    lr = [r["ladder"].get("L-R|full", {}).get("AC") for r in ok]
    end = ci([a - b for a, b in zip(full, lr) if a is not None and b is not None])
    bstar = None
    for rg in RUNGS:
        d = ci([r["ladder"]["random|full"]["AC"] - r["ladder"][f"random|{rg}"]["AC"] for r in ok
                if f"random|{rg}" in r["ladder"]])
        if equivalent(d, delta):
            bstar = rg
            break
    pc = ci([r["posctl"]["oracle"] - r["posctl"]["random"] for r in ok if r.get("posctl")])
    posctl = (pc["lo"] > delta) if pc else None
    sds = []
    d1 = ci([r["ladder"]["random|full"]["AC"] - r["ladder"]["random|c"]["AC"] for r in ok if "random|c" in r["ladder"]])
    if d1:
        sds.append(d1["sd"])
    ev = [k.split("|")[0] for k in ok[0]["ladder"] if not k.startswith(("random|", "L-R|"))]
    if ev:
        d2 = ci([r["ladder"][f"{ev[0]}|c/4"]["AC"] - r["ladder"]["random|c/4"]["AC"] for r in ok
                 if f"{ev[0]}|c/4" in r["ladder"]])
        if d2:
            sds.append(d2["sd"])
    n_rep = max(REP_MIN, math.ceil(((1.645 + 0.842) * max(sds) / delta) ** 2)) if sds else None
    stab = {}
    for fam in ("SELECTIVE", "LOSSLESS", "HYBRID"):
        d = [abs(r["arms"][fam]["AC_a"] - r["arms"][fam]["AC_b"]) for r in ok if fam in r["arms"]]
        if d:
            stab[fam] = dict(p975=float(np.percentile(d, 97.5)), frac_gt1=float(np.mean(np.array(d) > 1.0)))
    cap = [rg for rg in RUNGS if np.median([r["ladder"][f"random|{rg}"]["iters"]["cap_frac"] or 0 for r in ok
                                            if f"random|{rg}" in r["ladder"]] or [0]) > 0.1]
    return dict(out, delta=delta, median_n_test=med_test, sd_by_n=sd_n, n_min=n_min, eligible=eligible, gain_ci=gain,
                learnable=learnable, frame="TESTABLE" if (eligible and learnable) else "UNTESTED",
                end_warm_minus_LR=end, B_star_preview=bstar, posctl_ci=pc, posctl_pass=posctl, n_rep=n_rep,
                replicable=(n_rep is not None and n_rep <= REP_CAP), stability=stab, cap_bound_rungs=cap)


def main():
    fz = json.load(open(os.path.join(HERE, "FROZEN_SELECTION.json")))["choices"]
    res = {}
    for key, fr in fz.items():
        r = reduce_stratum(key, fr, DELTA)
        r["sensitivity"] = {str(d): {k: reduce_stratum(key, fr, d).get(k) for k in ("frame", "posctl_pass", "n_min")}
                            for d in SENS}
        res[key] = r
    with open(os.path.join(HERE, "dev", "margins_reduced_v2.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    return res


if __name__ == "__main__":
    R = main()
    for k, v in R.items():
        if v.get("delta") is None:
            print(k.ljust(26), v["frame"], v.get("reason", ""))
            continue
        s = v["sensitivity"]
        print(k.ljust(26), v["frame"].ljust(9), "nmin", str(v["n_min"]).ljust(4), "ntest %3d" % v["median_n_test"],
              "gainlo %.2f" % v["gain_ci"]["lo"], "pc", v["posctl_pass"], "nrep", v["n_rep"],
              "| .15:", s["0.15"]["frame"][:4], s["0.15"]["posctl_pass"], ".60:", s["0.6"]["frame"][:4], s["0.6"]["posctl_pass"])
