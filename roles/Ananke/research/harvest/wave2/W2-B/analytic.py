"""W2-B analytic attainability (numpy + swap_rel; no engine). usage: python analytic.py
A. MAJ k-sensor ceilings; B. CI-gate eligibility (min true accuracy to cross) for SIGNAL, INTEGRATION,
absolute swap FLIP, C1b T/kills/drops/predictors; C. swap_rel ideal outcomes (attainable iff ident) and
the no-op arm (NO_EFFECT_REL forced); D. AUDIT3 / W-Z arms whose swap scores equal normal exactly;
E. XOR: agreement of every 2-input boolean readout with x1*x2; F. FLIP: info structure."""
import itertools
import json
import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
from prometheus.ananke import swap_rel as sr  # noqa: E402
import attain as A  # noqa: E402

out = {}
# ---- A. MAJ: best accuracy using k of the 5 sensors (flip p = .3; ties score .5)
p = 0.7
maj = {}
for k in range(1, 6):
    acc = 0.0
    for c in range(k + 1):
        pr = math.comb(k, c) * p ** c * (1 - p) ** (k - c)
        acc += pr * (1.0 if 2 * c > k else 0.5 if 2 * c == k else 0.0)
    maj[k] = round(acc, 4)
out["A_MAJ_k_sensor_ceiling"] = maj
# pivotality of each sensor under exact 5-majority: other 4 split 2-2
out["A_MAJ_majority_pivotality"] = round(math.comb(4, 2) * p ** 2 * (1 - p) ** 2, 4)
# ---- B. CI gates: min true accuracy for P(cross) >= .5 / .9 (twin_corr 1 = mirror-equivariant program)
B = {}
for name, thr, side in (("SIGNAL lo99>.55", 0.55, "lo_gt"), ("INTEGRATION lo99>.70", 0.70, "lo_gt"),
                        ("C1b T intact lo99>=.62", 0.62, "lo_gt"), ("C1b predictor lo99>.60", 0.60, "lo_gt")):
    for P, K in ((32, 12), (64, 12), (128, 12), (256, 11)):
        B[f"{name} P{P} K{K}"] = {"p50": round(A.min_true_to_cross(thr, P, K, side, .5), 4),
                                  "p90": round(A.min_true_to_cross(thr, P, K, side, .9), 4)}
# absolute swap FLIP: hi99(swap) < .40 with the IDEAL swap s = 1 - normal  -> normal >= 1 - bound
for P, K in ((32, 12), (64, 12), (128, 12), (256, 11)):
    s50 = A.min_true_to_cross(0.40, P, K, "hi_lt", .5)
    s90 = A.min_true_to_cross(0.40, P, K, "hi_lt", .9)
    B[f"absolute swap FLIP (ideal follow) P{P} K{K}"] = {"normal_p50": round(1 - s50, 4), "normal_p90": round(1 - s90, 4)}
# INTEGRATION false positive for a reader at the 2-sensor/1-sensor ceiling .70
B["INTEGRATION FP at p=.70 (P32 K12)"] = round(A.ci_gate_power(0.70, 0.70, 32, 12, "lo_gt"), 4)
B["INTEGRATION power at p=.784 (3 sensors, P32 K12)"] = round(A.ci_gate_power(0.784, 0.70, 32, 12, "lo_gt"), 4)
B["INTEGRATION power at p=.837 (5 sensors, P32 K12)"] = round(A.ci_gate_power(0.837, 0.70, 32, 12, "lo_gt"), 4)
B["XOR one-flag (.75) crosses SIGNAL (P32 K12)"] = round(A.ci_gate_power(0.75, 0.55, 32, 12, "lo_gt"), 4)
B["XOR one-flag (.75) crosses INTEGRATION-.70 (P32 K12)"] = round(A.ci_gate_power(0.75, 0.70, 32, 12, "lo_gt"), 4)
out["B_ci_gates"] = B
# ---- C. swap_rel ideal outcomes on synthetic pair data
rng = np.random.default_rng(7)
C = {}
for a_true in (0.52, 0.55, 0.6, 0.7, 0.9):
    for P, K in ((32, 11), (64, 11), (256, 11)):
        a = rng.binomial(K, a_true, size=P) / K                  # mirror-equivariant: pair mean = world mean
        nlo = sr.interval(a, K)[1]
        r = {"ident": bool(nlo > 0.5)}
        for nm, s in (("noop(s=a)", a), ("follow(s=1-a)", 1 - a), ("chance(s=.5)", np.full(P, 0.5))):
            r[nm] = sr.from_pairs(a, s, K)["label"]
        C[f"a{a_true} P{P}"] = r
out["C_swap_rel_ideal"] = C
# ---- D. AUDIT3 (W-Z) arms whose swap per-trial scores equal the normal exactly (no-op signature)
D = {"arms": 0, "identical_arms": 0, "identical_by_label": {}, "label_counts": {}}
pdir = ROOT / "roles/Ananke/research/workers/W-Z/out/pairs"
for f in sorted(pdir.glob("*.npz")):
    z = np.load(f)
    for k in z.files:
        if not k.startswith("a__"):
            continue
        lab = k[3:]
        at, st = z[k].astype(float), z["s__" + lab].astype(float)
        m = (at != 255) & (st != 255)
        if m.sum() == 0:
            continue
        at, st = np.where(m, at / 4, np.nan), np.where(m, st / 4, np.nan)
        a = np.nanmean(at, 1)
        s = np.nanmean(st, 1)
        g = ~np.isnan(a) & ~np.isnan(s)
        if g.sum() < 32:
            continue
        K = int(round(m.sum() / max(1, g.sum())))     # scored trials per pair-row (pair means already)
        res = sr.from_pairs(a[g], s[g], max(1, K))
        D["arms"] += 1
        D["label_counts"][res["label"]] = D["label_counts"].get(res["label"], 0) + 1
        if np.array_equal(np.nan_to_num(at, nan=-1), np.nan_to_num(st, nan=-1)):
            D["identical_arms"] += 1
            D["identical_by_label"][res["label"]] = D["identical_by_label"].get(res["label"], 0) + 1
out["D_W-Z_noop_arms"] = D
# ---- E. XOR: agreement with x1*x2 of all 16 boolean readouts f(x1, x2) in {-1, +1}
combos = list(itertools.product((-1, 1), repeat=2))
agree = {}
for bits in itertools.product((-1, 1), repeat=4):
    f = dict(zip(combos, bits))
    a = np.mean([f[c] == c[0] * c[1] for c in combos])
    piv = [np.mean([f[c] != f[(-c[0], c[1])] for c in combos]), np.mean([f[c] != f[(c[0], -c[1])] for c in combos])]
    agree.setdefault(float(a), []).append({"f": bits, "pivotality": piv})
out["E_XOR_boolean_agreement"] = {k: {"n": len(v), "pivotality_sets": sorted({tuple(x["pivotality"]) for x in v})}
                                  for k, v in sorted(agree.items())}
# odd readouts f(-x) = -f(x) agree with parity on exactly half the combos
odd = [b for b in itertools.product((-1, 1), repeat=4)
       if all(dict(zip(combos, b))[c] == -dict(zip(combos, b))[(-c[0], -c[1])] for c in combos)]
out["E_XOR_odd_readouts_agreement"] = sorted({float(np.mean([dict(zip(combos, b))[c] == c[0] * c[1] for c in combos]))
                                              for b in odd})
(HERE / "out").mkdir(exist_ok=True)
(HERE / "out/analytic.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
