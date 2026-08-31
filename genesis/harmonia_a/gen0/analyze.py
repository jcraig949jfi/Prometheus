#!/usr/bin/env python
"""
HARMONIA A GEN-0 -- frozen analysis. Endpoints and gates are defined in
HARMONIA_A_GEN0_FREEZE.txt; this script implements them and nothing else.
Run AFTER bench.py. Bootstrap seed 20260831, 5000 resamples.
"""

import json
from collections import defaultdict

import numpy as np

LOCAL_BAND = 0.25
EPS_PRIMARY = 0.5
BOOT_N = 5000
BOOT_SEED = 20260831
MASTER_SEEDS = (11, 22, 33, 44, 55)
ANF_FORCED_LM = 1.0 - 11.0 / 1024.0          # P(deg >= 2), deg~Bin(10,.5)
DYADIC_EDGES = [0.0] + [2.0 ** -k for k in range(10, -1, -1)]


def band(d):
    if d == 0.0:
        return "NEUTRAL"
    if d <= LOCAL_BAND:
        return "LOCAL"
    return "FAR"


def load_rows():
    rows = []
    with open("results/rows.jsonl") as fh:
        for line in fh:
            rows.append(json.loads(line))
    return rows


def arm_key(r):
    a = r["arm"]
    if a in ("TT", "TT_SCR"):
        return f"{a}@{r['eps']}"
    return a


def masses(sub):
    ds = np.array([r["d"] for r in sub])
    return dict(n=len(ds),
                NEUTRAL=float(np.mean(ds == 0.0)),
                LOCAL=float(np.mean((ds > 0) & (ds <= LOCAL_BAND))),
                FAR=float(np.mean(ds > LOCAL_BAND)),
                d_median_nonzero=float(np.median(ds[ds > 0]))
                if (ds > 0).any() else None)


def bootstrap_lm(sub, rng):
    """Cluster bootstrap over objects (the unit of independence)."""
    by_obj = defaultdict(list)
    for r in sub:
        by_obj[(r["seed"], r["obj"])].append(
            1.0 if 0 < r["d"] <= LOCAL_BAND else 0.0)
    keys = sorted(by_obj)
    per_obj = [np.mean(by_obj[k]) for k in keys]
    stats = []
    for _ in range(BOOT_N):
        pick = rng.integers(len(keys), size=len(keys))
        stats.append(np.mean([per_obj[i] for i in pick]))
    return (float(np.percentile(stats, 2.5)),
            float(np.percentile(stats, 97.5)))


def main():
    rows = load_rows()
    rng = np.random.default_rng(BOOT_SEED)
    by_arm = defaultdict(list)
    for r in rows:
        by_arm[arm_key(r)].append(r)

    report = {"per_arm": {}, "per_arm_per_seed": {}, "gates": {},
              "histograms": {}}
    for arm in sorted(by_arm):
        sub = by_arm[arm]
        m = masses(sub)
        m["LOCAL_CI95"] = bootstrap_lm(sub, rng)
        report["per_arm"][arm] = m
        report["per_arm_per_seed"][arm] = {
            str(s): masses([r for r in sub if r["seed"] == s])
            for s in MASTER_SEEDS}
        ds = np.array([r["d"] for r in sub])
        hist, _ = np.histogram(ds, bins=DYADIC_EDGES)
        zero = int(np.sum(ds == 0.0))
        report["histograms"][arm] = dict(
            edges=DYADIC_EDGES, counts=[zero] + hist.tolist(),
            note="first bin is exact zero (NEUTRAL)")

    pa = report["per_arm"]
    g = report["gates"]

    # G_HARNESS: machine-implemented sham check (D-13 B4)
    dn = abs(pa["SHAM"]["LOCAL"] - pa["NAT"]["LOCAL"])
    dz = abs(pa["SHAM"]["NEUTRAL"] - pa["NAT"]["NEUTRAL"])
    g["G_HARNESS"] = dict(d_local=dn, d_neutral=dz, tol=0.03,
                          verdict="PASS" if dn <= 0.03 and dz <= 0.03
                          else "HARNESS_SUSPECT")

    # G_ANALYTIC: forced values must reproduce empirically
    checks = {
        "ANF_lm_vs_forced": abs(pa["ANF"]["LOCAL"] - ANF_FORCED_LM),
        "ANF_SCR_vs_ANF": abs(pa["ANF_SCR"]["LOCAL"] - pa["ANF"]["LOCAL"]),
        "VT_lm_vs_1": abs(pa["VT"]["LOCAL"] - 1.0)}
    g["G_ANALYTIC"] = dict(checks=checks, tol=0.02,
                           verdict="PASS" if max(checks.values()) <= 0.02
                           else "FAIL")

    # G_DOSE: TT eps knob non-inertness (D-13 B5)
    tt = [r for r in rows if r["arm"] == "TT"]
    by_pert = defaultdict(dict)
    for r in tt:
        by_pert[(r["seed"], r["obj"], r["edit"])][r["eps"]] = r["fhash"]
    ident = sum(1 for v in by_pert.values()
                if len(set(v.values())) == 1)
    frac_ident = ident / max(len(by_pert), 1)
    g["G_DOSE"] = dict(frac_identical_children=frac_ident, cap=0.95,
                       verdict="PASS" if frac_ident <= 0.95 else "INERT")

    # G1: the target phenomenon (frozen)
    nat_lm = pa["NAT"]["LOCAL"]
    tt_arm = f"TT@{EPS_PRIMARY}"
    tt_lm = pa[tt_arm]["LOCAL"]
    per_seed_ok = all(
        report["per_arm_per_seed"][tt_arm][str(s)]["LOCAL"] >
        report["per_arm_per_seed"]["NAT"][str(s)]["LOCAL"]
        for s in MASTER_SEEDS)
    ci_sep = pa[tt_arm]["LOCAL_CI95"][0] > pa["NAT"]["LOCAL_CI95"][1]
    if nat_lm <= 0.05 and tt_lm >= 0.25 and per_seed_ok and ci_sep:
        verdict = "REACHABLE"
    elif nat_lm <= 0.05:
        verdict = "REACHABLE_ANALYTIC_ONLY"   # gap exists; only forced
        # reps fill it; TT did not clear its bar
    else:
        verdict = "NO_REPRESENTATIONAL_REACHABILITY_EFFECT"
    g["G1_PHENOMENON"] = dict(
        NAT_LOCAL=nat_lm, TT_PRIMARY_LOCAL=tt_lm,
        per_seed_consistent=per_seed_ok, ci_separated=ci_sep,
        nat_gap_threshold=0.05, tt_local_threshold=0.25,
        verdict=verdict)

    # structure question: TT vs TT_SCR at primary eps
    g["G2_STRUCTURE"] = dict(
        TT=pa[tt_arm]["LOCAL"], TT_SCR=pa[f"TT_SCR@{EPS_PRIMARY}"]["LOCAL"],
        note="difference indicates variable-order structure matters "
             "for TT local reachability; descriptive, no frozen gate")

    with open("results/analysis.json", "w") as fh:
        json.dump(report, fh, indent=1)

    print(f"{'arm':14s} {'n':>6s} {'NEUTRAL':>8s} {'LOCAL':>8s} "
          f"{'FAR':>8s}  LOCAL_CI95")
    for arm in sorted(pa):
        m = pa[arm]
        print(f"{arm:14s} {m['n']:6d} {m['NEUTRAL']:8.4f} "
              f"{m['LOCAL']:8.4f} {m['FAR']:8.4f}  "
              f"[{m['LOCAL_CI95'][0]:.4f}, {m['LOCAL_CI95'][1]:.4f}]")
    print()
    for name, gate in g.items():
        print(f"{name}: {gate.get('verdict', gate)}")


if __name__ == "__main__":
    main()
