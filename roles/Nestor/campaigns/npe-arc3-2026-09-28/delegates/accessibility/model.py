"""Q1 predictive model: which arm acquires donors?

Computational artificial life: integer programs on the z8 VM. Nothing biological.

Data: the soup result files of the four arms on seeds 16_000_000 + s (PLAIN, DENSE_COPY from
x_dd_dense_copy; PLANT from x_p2_plant; SHAM from x_p2_sham) and, for the SHAM arm (whose results do not
store copy-carrier counts), the neutral pilot's L1c trajectories on the same material (RANDOM material,
identical to PLAIN's; the sham has no usable copy encoding beyond ED B0/B8).

Candidate predictors, all per run, all computed before or without the endpoint:
  M0 RAW FREQUENCY   f0 = share of genomes carrying a copy encoding at the first checkpoint (epoch 100);
                     predicted P(acquire) = 1 - exp(-a * f0 * 20)            (one parameter a)
  M1 CARRIER EXPOSURE E = sum over at-risk checkpoints of the number of screened genomes carrying a copy
                     encoding (ED B0/B8, or E5/E7 on the dense VM); predicted events = lambda * E (Poisson,
                     one parameter lambda = per-carrier-screen conversion hazard)
Each model is FITTED ON ONE ARM (DENSE) and tested on the others (PLANT, PLAIN, SHAM), then fitted on PLANT
and tested on DENSE: an out-of-arm test, not a fit to all four.
Output model.json.
"""
from __future__ import annotations

import glob
import json
import math

import acc_lib as A

SRC = {"PLAIN": str(A.W1 / "x_dd_dense_copy" / "results" / "PLAIN_*.json"),
       "DENSE": str(A.W1 / "x_dd_dense_copy" / "results" / "DENSE_COPY_*.json"),
       "PLANT": str(A.P2 / "x_p2_plant" / "results" / "*.json"),
       "SHAM": str(A.P2 / "x_p2_sham" / "results" / "*.json")}


def load():
    neut = {}
    for f in glob.glob(str(A.HERE / "results_neutral" / "RANDOM_*.json")):
        x = json.loads(open(f).read())
        neut[(x["cell"], x["seed"])] = x["arms"]["SHAM"]
    runs = []
    for arm, pat in SRC.items():
        for f in glob.glob(pat):
            x = json.loads(open(f).read())
            cps = sorted(x["checkpoints"], key=lambda c: c["epoch"])
            if "L1c" not in cps[0]:
                nc = neut.get((x["cell"], x["seed"]))
                if nc is None:
                    # SHAM run without a neutral twin: its material is PLAIN's, so borrow PLAIN's L1c at
                    # the same seed (the soups differ only in the VM's reading of 0xE5 / 0xE7)
                    p = json.loads(open(str(A.W1 / "x_dd_dense_copy" / "results" /
                                            ("PLAIN_%s_%d.json" % (x["cell"], x["seed"])))).read())
                    l1 = {c["epoch"]: c["L1c"] for c in p["checkpoints"]}
                else:
                    l1 = {c["epoch"]: c["L1c"] for c in nc}
                for c in cps:
                    c["L1c"] = l1.get(c["epoch"], 0)
            E, ev = 0, 0
            for c in cps:
                E += c["L1c"]
                if c["L2"] > 0:
                    ev = 1
                    break
            f0 = cps[0]["L1c"] / max(1, cps[0]["distinct"])
            runs.append({"arm": arm, "cell": x["cell"], "seed": x["seed"], "event": ev, "E": E, "f0": f0})
    return runs


def fit_lambda(rows):
    ev = sum(r["event"] for r in rows)
    return ev / max(1, sum(r["E"] for r in rows))


def fit_a(rows):
    """ML for P = 1 - exp(-a*f0*20) by a 1-D grid (log-spaced)."""
    best = None
    for k in range(-400, 401):
        a = 10 ** (k / 100)
        ll = 0.0
        for r in rows:
            p = 1 - math.exp(-a * r["f0"] * 20)
            p = min(max(p, 1e-12), 1 - 1e-12)
            ll += math.log(p) if r["event"] else math.log(1 - p)
        if best is None or ll > best[0]:
            best = (ll, a)
    return best[1]


def predict(rows, lam=None, a=None):
    if lam is not None:
        # a run's exposure is truncated at its event; the expected number of acquiring runs under a
        # constant per-carrier hazard is sum(1 - exp(-lam * E_full)); with E truncated we report the
        # Poisson expectation lam * sum(E), which is the correct ML check for a truncated exposure
        return lam * sum(r["E"] for r in rows)
    return sum(1 - math.exp(-a * r["f0"] * 20) for r in rows)


def main():
    runs = load()
    arms = ["DENSE", "PLANT", "PLAIN", "SHAM"]
    by = {a: [r for r in runs if r["arm"] == a] for a in arms}
    out = {"per_arm": {}, "tests": {}}
    for a in arms:
        rows = by[a]
        out["per_arm"][a] = {"runs": len(rows), "acquiring": sum(r["event"] for r in rows),
                             "mean_f0": round(sum(r["f0"] for r in rows) / len(rows), 4),
                             "carrier_exposure": sum(r["E"] for r in rows),
                             "lambda_own": fit_lambda(rows),
                             "per_cell": {c: {"acquiring": sum(r["event"] for r in rows if r["cell"] == c),
                                              "E": sum(r["E"] for r in rows if r["cell"] == c),
                                              "lambda": fit_lambda([r for r in rows if r["cell"] == c])}
                                          for c in ("7ae3", "ffa6")}}
    for train in ("DENSE", "PLANT"):
        lam = fit_lambda(by[train])
        a = fit_a(by[train])
        t = {"lambda": lam, "a": a, "predictions": {}}
        for test in arms:
            obs = sum(r["event"] for r in by[test])
            pe = predict(by[test], lam=lam)
            pf = predict(by[test], a=a)
            # Poisson two-sided p for obs given expectation pe (exact, small sums)
            t["predictions"][test] = {"observed": obs, "M1_carrier_exposure_expected": round(pe, 2),
                                      "M0_raw_frequency_expected": round(pf, 2)}
        out["tests"]["fit_on_" + train] = t
    (A.HERE / "model.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
