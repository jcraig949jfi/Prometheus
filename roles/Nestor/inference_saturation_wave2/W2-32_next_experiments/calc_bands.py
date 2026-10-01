"""W2-32 design-only calculator (no world code, no world runs). Pure arithmetic + numpy branching.

Produces calc_bands.json:
  1. static lifetime proxies per genome from W2-24's register-level trace table (N = 1000 bank panel);
  2. predicted P(B >= 27), P(B >= 163), P(B >= 163 | B >= 27) per Exp-1 arm under three frozen
     mappings from static law to lifetime law (M1 N18-native, M2 per-call ratio, M3 keep-leveraged),
     each calibrated on the founder against X-TICKET (4/128 on both B >= 27 and B >= 163);
  3. binomial acceptance bands and discrimination power at n = 128 / 192 / 256 seeds per arm;
  4. Exp-2 beta precision (cloglog, two-arm in-batch joint fit) at several n;
  5. Exp-3 power for the epoch-1-loss contrast.
B = cumulative births in the lineage (matched to the world's B: causal births in the founder's causal set).
Generation cap G stands in for the 300-epoch horizon (founder generation time 5-10 epochs -> 30-60 gens).
python -B calc_bands.py  -> calc_bands.json
"""
import json, math, pathlib, time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
T0 = time.process_time()

# ---------------------------------------------------------------- 1. static law (W2-24 REPORT trace table)
# side-0 / side-1 keep and conversion; random side per call -> average.
TRACE = {  # genome: (keep0, conv0, keep1, conv1, m_base_bank)
    "F":     (0.52, 0.002, 0.907, 0.874, 1.172),
    "AC":    (1.00, 1.000, 0.52, 0.021, 1.248),
    "C3":    (0.973, 0.002, 0.907, 0.870, 1.389),
    "C3AC":  (1.00, 1.000, 0.961, 0.010, 1.469),
}
STATIC = {}
for g, (k0, c0, k1, c1, mb) in TRACE.items():
    c, k = (c0 + c1) / 2, (k0 + k1) / 2
    STATIC[g] = {"conv": round(c, 4), "keep": round(k, 4), "L_geom": round(c / (1 - k), 3), "m_call": mb}
for g in STATIC:
    STATIC[g]["ratio_call"] = round(STATIC[g]["m_call"] / STATIC["F"]["m_call"], 4)
    STATIC[g]["ratio_geom"] = round(STATIC[g]["L_geom"] / STATIC["F"]["L_geom"], 4)

# ---------------------------------------------------------------- 2. two-type NB branching, vectorised
B_HI, B_LO = 163, 27


def nb_sum(rng, n, mean, V):
    """sum of n iid NB(mean, V) draws (exact: NB is closed under iid sums with common p)."""
    out = np.zeros(n.shape, dtype=np.int64)
    pos = n > 0
    if not pos.any() or mean <= 0:
        return out
    if V <= mean:
        out[pos] = rng.poisson(mean * n[pos])
        return out
    r = mean * mean / (V - mean)
    p = r / (r + mean)
    out[pos] = rng.negative_binomial(r * n[pos], p)
    return out


def simulate(mA, mB, V, s, b, start, G, N, seed):
    """type A = side-1 (F or C3), type B = side-0 (AC or C3+AC). A->B switch s per birth, B->A b.
    Returns P(B>=27), P(B>=163)."""
    rng = np.random.default_rng(seed)
    nA = np.full(N, 1 if start == "A" else 0, dtype=np.int64)
    nB = np.full(N, 1 if start == "B" else 0, dtype=np.int64)
    Bc = np.zeros(N, dtype=np.int64)
    hit27 = np.zeros(N, bool)
    hit163 = np.zeros(N, bool)
    live = np.ones(N, bool)
    for _ in range(G):
        idx = np.nonzero(live)[0]
        if idx.size == 0:
            break
        kA = nb_sum(rng, nA[idx], mA, V)
        kB = nb_sum(rng, nB[idx], mB, V)
        sAB = rng.binomial(kA, s) if s > 0 else np.zeros_like(kA)
        sBA = rng.binomial(kB, b) if b > 0 else np.zeros_like(kB)
        nA[idx] = kA - sAB + sBA
        nB[idx] = kB - sBA + sAB
        Bc[idx] += kA + kB
        hit27[idx] |= Bc[idx] >= B_LO
        h = Bc[idx] >= B_HI
        hit163[idx] |= h
        dead = (nA[idx] + nB[idx]) == 0
        live[idx[h | dead]] = False
    return float(hit27.mean()), float(hit163.mean())


def cp(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return lo, hi


F_LO, F_HI = cp(4, 128)       # X-TICKET founder: 4/128 on B>=27 and on B>=163
NSIM = 20000
res = {"static": STATIC, "founder_CI_4_of_128": [round(F_LO, 4), round(F_HI, 4)], "models": {}}

ARMS = {"F": ("F", "A"), "AC": ("F", "B"), "C3": ("C3", "A"), "C3AC": ("C3", "B")}
# M1: N18-native fits with binned deviance <= 4 (twotype.json) -> AC is N18's morph; C3 arms get M3 factors
n18 = json.loads((HERE.parent / "N18_two_type_fit" / "twotype.json").read_text())["fits_sorted"]
n18 = [f for f in n18 if f["dev_bins"] <= 4.0 and f["s"] > 0]

seed = 1
for model in ("M1", "M2", "M3"):
    rows = []
    if model == "M1":
        psets = [(f["m0"], f["m1"], f["V"], f["s"]) for f in n18]
    else:
        psets = [(m0, None, V, s) for m0 in np.round(np.arange(0.70, 1.001, 0.02), 2)
                 for V in (3.0, 7.0, 12.0) for s in (7.5e-4, 0.01, 0.035)]
    for G in (40, 60):
        for (m0, m1, V, s) in psets:
            if model == "M1":
                mt = {"F": m0, "AC": m1,
                      "C3": m0 * STATIC["C3"]["ratio_geom"], "C3AC": m0 * STATIC["C3AC"]["ratio_geom"]}
            else:
                key = "ratio_call" if model == "M2" else "ratio_geom"
                mt = {g: m0 * STATIC[g][key] for g in STATIC}
            seed += 1
            p27F, p163F = simulate(mt["F"], mt["AC"], V, s, 0.07, "A", G, NSIM, seed)
            ok = bool((F_LO <= p163F <= F_HI) and (F_LO <= p27F <= F_HI))
            row = {"m0": float(m0), "V": V, "s": s, "G": G, "m": {g: round(v, 3) for g, v in mt.items()},
                   "F": [round(p27F, 4), round(p163F, 4)], "calibrated": ok}
            if ok:
                for arm, (pair, start) in ARMS.items():
                    if arm == "F":
                        continue
                    mA = mt["F"] if pair == "F" else mt["C3"]
                    mB = mt["AC"] if pair == "F" else mt["C3AC"]
                    seed += 1
                    p27, p163 = simulate(mA, mB, V, s, 0.07, start, G, NSIM, seed)
                    row[arm] = [round(p27, 4), round(p163, 4)]
            rows.append(row)
    cal = [r for r in rows if r["calibrated"]]
    summ = {}
    for arm in ARMS:
        v163 = [r[arm][1] for r in cal]
        v27 = [r[arm][0] for r in cal]
        cond = [r[arm][1] / r[arm][0] for r in cal if r[arm][0] > 0]
        if v163:
            summ[arm] = {"P163_range": [round(min(v163), 4), round(max(v163), 4)],
                         "P27_range": [round(min(v27), 4), round(max(v27), 4)],
                         "P163_given_27_range": [round(min(cond), 3), round(max(cond), 3)] if cond else None}
    res["models"][model] = {"n_param_sets": len(rows), "n_calibrated": len(cal), "summary": summ,
                            "calibrated_rows": cal}

# ---------------------------------------------------------------- 3. bands and discrimination
from scipy.stats import binom


def band(plo, phi, n, a=0.05):
    """union of central (1-a) binomial intervals over p in [plo, phi] -> integer [lo, hi]."""
    lo = int(binom.ppf(a / 2, n, plo))
    hi = int(binom.isf(a / 2, n, phi))
    return lo, hi


disc = {}
for n in (128, 192, 256):
    d = {}
    for arm in ARMS:
        d[arm] = {}
        for m in ("M1", "M2", "M3"):
            sm = res["models"][m]["summary"].get(arm)
            if sm:
                d[arm][m] = band(*sm["P163_range"], n)
        # power: P(count from model X lands outside band of model Y), using X's central p
        pw = {}
        for x in d[arm]:
            px = float(np.mean(res["models"][x]["summary"][arm]["P163_range"]))
            for y in d[arm]:
                if x == y:
                    continue
                lo, hi = d[arm][y]
                pw[x + "_kills_" + y] = round(float(binom.cdf(lo - 1, n, px) + binom.sf(hi, n, px)), 3)
        d[arm]["power_at_mid_p"] = pw
    disc[str(n)] = d
res["bands_B163_counts"] = disc

# ---------------------------------------------------------------- 4. Exp-2 beta precision
# two arms, in-batch: P_k = 1 - (1 - p1)^(k^beta). beta_hat = log(log(1-P_k)/log(1-P_1))/log k. Delta-method SE.
def beta_se(p1, k, beta, n1, nk):
    Pk = 1 - (1 - p1) ** (k ** beta)
    l1, lk = math.log(1 - p1), math.log(1 - Pk)
    # d beta / d P1 = (1/log k) * (1/l1) * (1/(1-p1)) ; d beta / d Pk = -(1/log k) * (1/lk) * (1/(1-Pk))
    g1 = 1 / (math.log(k) * l1 * (1 - p1))
    gk = -1 / (math.log(k) * lk * (1 - Pk))
    var = g1 ** 2 * p1 * (1 - p1) / n1 + gk ** 2 * Pk * (1 - Pk) / nk
    return round(Pk, 4), round(math.sqrt(var), 4)


def beta_power(p1, k, beta_true, n1, nk, lo_band, hi_band, reps=4000, seed=7):
    """MC: fraction of replicate batches whose beta_hat 95% Wald CI lies wholly inside [lo_band, hi_band]
    (independence call) or wholly above hi_band (superadditive call)."""
    rng = np.random.default_rng(seed)
    Pk = 1 - (1 - p1) ** (k ** beta_true)
    x1 = rng.binomial(n1, p1, reps)
    xk = rng.binomial(nk, Pk, reps)
    ind = sup = 0
    for a, c in zip(x1, xk):
        q1, qk = (a + 0.5) / (n1 + 1), (c + 0.5) / (nk + 1)
        bh = math.log(math.log(1 - qk) / math.log(1 - q1)) / math.log(k)
        _, se = beta_se(q1, k, bh, n1, nk)
        if bh - 1.96 * se >= lo_band and bh + 1.96 * se <= hi_band:
            ind += 1
        if bh - 1.96 * se > SUP_LB:
            sup += 1
    return round(ind / reps, 3), round(sup / reps, 3)


SUP_LB = 1.05   # superadditive call: 95% CI lower bound above the static kin-route ceiling (W2-12: beta 1.02-1.05)
ex2 = {}
for p1 in (0.08, 0.11, 0.13):
    for k in (4, 8):
        for n1, nk in ((320, 160), (480, 240), (600, 300), (800, 400), (1000, 500)):
            for bt in (1.0, 1.15, 1.3):
                Pk, se = beta_se(p1, k, bt, n1, nk)
                ind, sup = beta_power(p1, k, bt, n1, nk, 0.80, 1.20)  # independence: CI inside [0.80, 1.20]
                ex2["p1=%.2f k=%d n=%d/%d beta=%.2f" % (p1, k, n1, nk, bt)] = {
                    "Pk": Pk, "se_beta": se, "P_call_independent": ind, "P_call_superadditive": sup}
res["exp2_beta"] = ex2

# ---------------------------------------------------------------- 5. Exp-3 epoch-1 loss power
# stock 36/128 = 0.28; N2 hijack share 0.5 x 0.43 = 0.21 (zero ctx) or 0.5 x 0.32 (random ctx, 242/750)
ex3 = {}
for n in (128, 192, 256, 384):
    for p_stock, p_harv in ((0.28, 0.07), (0.28, 0.12), (0.28, 0.17), (0.28, 0.28)):
        # Fisher-ish power via normal approx, one-sided alpha 0.01
        se = math.sqrt(p_stock * (1 - p_stock) / n + p_harv * (1 - p_harv) / n)
        z = (p_stock - p_harv) / se if se else 0
        from scipy.stats import norm
        ex3["n=%d stock=%.2f harv=%.2f" % (n, p_stock, p_harv)] = {
            "power_one_sided_0.01": round(float(norm.sf(2.326 - z)), 3),
            "harv_95band": [int(binom.ppf(0.025, n, p_harv)), int(binom.isf(0.025, n, p_harv))]}
res["exp3_epoch1"] = ex3
res["cpu_s"] = round(time.process_time() - T0, 1)
(HERE / "calc_bands.json").write_text(json.dumps(res, indent=1))
for m in ("M1", "M2", "M3"):
    print(m, res["models"][m]["n_calibrated"], "/", res["models"][m]["n_param_sets"],
          json.dumps(res["models"][m]["summary"]))
print(json.dumps(res["bands_B163_counts"], indent=0)[:3000])
print("cpu_s", res["cpu_s"])
