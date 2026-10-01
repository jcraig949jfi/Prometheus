"""K2b (frames A/E): shape of the depth distribution of single-implant 7ae3 runs, BASE write-back.

Ring-medium / interacting-particle frame: a single-sided copy op makes the per-interaction offspring
mean m_BASE ~= 1 structurally (K2: median 1.00 over 128 copiers). A (near-)critical process predicts a
parameter-free heavy tail S(d) = P(D >= d | D >= 1) ~ 1/d at small d (before the field saturates).
The 'erosion brake' reading (subcritical) predicts a geometric tail q^(d-1). Splice ON lowers m
further, so the frame predicts a geometric (thin) tail there.
Data: existing per-run max_causal_replication_depth (P-11) records; nothing is run.
Censoring: d >= DCAP is treated as right-censored (saturation regime is a different process).
"""
import json
import math
import pathlib

import common as C

C9X = C.CAMP / "c9x-explore-2026-09-24"
DCAP = 20


def load():
    off, on = [], []
    for f in (C9X / "c_atomic" / "results").glob("7ae3*_BASE.json"):
        off.append(json.loads(f.read_text())["depth"])
    off += [r["depth"] for r in json.loads((C9X / "x_atomic" / "RESULTS.json").read_text()) if r["arm"] == "BASE"]
    for r in json.loads((C9X / "c_norecomb_confirm" / "RESULTS.json").read_text()):
        if r["spec"].startswith("7ae3"):
            (off if r["arm"] == "NO_RECOMB" else on).append(r["depth"])
    for name in ("c_runaway_confirm", "x_h2_norecomb"):
        for r in json.loads((C9X / name / "RESULTS.json").read_text()):
            (off if r["arm"] == "NO_RECOMB" else on).append(r["depth"])
    for name in ("c_critical_mass", "x_critical_mass"):
        off += [r["depth"] for r in json.loads((C9X / name / "RESULTS.json").read_text()) if r["k"] == 1]
    off += [json.loads(f.read_text())["depth"] for f in (C9X / "x_dose_curve" / "results").glob("*_k1.json")]
    off += [json.loads(f.read_text())["depth"] for f in (C9X / "x_ticket" / "results").glob("*.json")]
    return off, on


def loglik(ds, S):
    ll = 0.0
    for d in ds:
        if d >= DCAP:
            ll += math.log(max(S(DCAP), 1e-300))
        else:
            ll += math.log(max(S(d) - S(d + 1), 1e-300))
    return ll


def fit(ds):
    ds = [d for d in ds if d >= 1]
    out = {"n_pos": len(ds)}
    out["critical_1/d"] = {"ll": loglik(ds, lambda d: 1.0 / d), "k": 0}
    best = None
    for i in range(1, 1000):
        q = i / 1000
        ll = loglik(ds, lambda d, q=q: q ** (d - 1))
        if best is None or ll > best[0]:
            best = (ll, q)
    out["geometric"] = {"ll": best[0], "q": best[1], "k": 1}
    best = None
    for i in range(1, 400):
        a = i / 100
        ll = loglik(ds, lambda d, a=a: d ** (-a))
        if best is None or ll > best[0]:
            best = (ll, a)
    out["power"] = {"ll": best[0], "alpha": best[1], "k": 1}
    for m in ("critical_1/d", "geometric", "power"):
        out[m]["aic"] = round(2 * out[m]["k"] - 2 * out[m]["ll"], 2)
        out[m]["ll"] = round(out[m]["ll"], 2)
    return out


def surv(ds):
    n = len(ds)
    return {d: round(sum(x >= d for x in ds) / n, 4) for d in (1, 2, 3, 4, 6, 8, 12, 16, 20, 22, 50, 161)}


def main():
    off, on = load()
    res = {}
    for name, ds in (("splice_off", off), ("splice_on", on)):
        pos = [d for d in ds if d >= 1]
        res[name] = {"n": len(ds), "S_all": surv(ds),
                     "S_given_pos": {d: round(sum(x >= d for x in pos) / len(pos), 4) for d in (1, 2, 4, 8, 16, 20)},
                     "pred_critical_given_pos": {d: round(1 / d, 4) for d in (1, 2, 4, 8, 16, 20)},
                     "n_in_gap_22_160": sum(22 <= x < 161 for x in ds), "n_ge_161": sum(x >= 161 for x in ds),
                     "fit": fit(ds)}
    (C.HERE / "k2b_depth_tail.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
