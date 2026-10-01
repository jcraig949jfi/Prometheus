"""W2-40: re-derive W2-32's X-IMPLANT-MORPH bands with keep/conv/m on the CLASS and EXACT rulers.

Part A (static reuse, no world run): per-side keep/conv for F, AC, C3, C3AC on the W2-30 T1 panel
  (N=1000 W2-14 BASE bank partners, random side, ZERO donor ctx, copy errors off), scored three ways on
  the SAME calls: FID>=0.9 (W2-24 trace ruler), CLASS (FID>=0.9 AND bytes 43,44,45,49 == parent; W2-30 T1c),
  EXACT (byte-identical; W2-30 T1). Checked against W2-24 TRACE (FID) and W2-30 json (class m, exact).
Part B: W2-32 calc_bands.py arithmetic COPIED verbatim (nb_sum, simulate, cp, band, model loop, seed scheme;
  the W2-32 file is not imported because importing it would rewrite its json). Only STATIC changes per ruler.
  The FID ruler uses W2-32's literal TRACE and must reproduce calc_bands.json exactly (regression check).
Part C: bands at the prereg n (F 256, AC 384, C3 64, C3AC 64) and 128; disjointness + power.
python -B c3_bands.py -> c3_bands.json
"""
import json, sys, pathlib, time
import numpy as np
from scipy.stats import binom, beta

HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
T0 = time.process_time()

# ---------------------------------------------------------------- Part A: per-side class keep/conv
sys.path.insert(0, str(W2 / "W2-30_double_mutant"))
sys.path.insert(0, str(W2 / "W2-24_keep_variant"))
from q1_trace import panel  # noqa: E402
from tvm import C  # noqa: E402
from t1_exact_m import G  # noqa: E402
from t1b_near_children import halves  # noqa: E402

CLS = (43, 44, 45, 49)
RULE = {"FID": lambda x, h: C.FID(x, h) >= 0.9,
        "class": lambda x, h: C.FID(x, h) >= 0.9 and all(h[i] == x[i] for i in CLS),
        "exact": lambda x, h: h == x}
NAMEMAP = {"F": "F", "AC": "AC", "C3": "C3", "C3AC": "C3+AC"}
pan = panel()
measured = {}
for g, gname in NAMEMAP.items():
    x = G[gname]
    t = {(ru, s, k): 0 for ru in RULE for s in (0, 1) for k in ("keep", "conv")}
    ns = [0, 0]
    for y, cy, cx, s in pan:
        (nx, ny), _ = halves(x, y, s, C.ZERO, cy)
        ns[s] += 1
        for ru, f in RULE.items():
            t[(ru, s, "keep")] += f(x, nx)
            t[(ru, s, "conv")] += f(x, ny)
    measured[g] = {}
    for ru in RULE:
        k0, c0 = t[(ru, 0, "keep")] / ns[0], t[(ru, 0, "conv")] / ns[0]
        k1, c1 = t[(ru, 1, "keep")] / ns[1], t[(ru, 1, "conv")] / ns[1]
        m = sum(t[(ru, s, k)] for s in (0, 1) for k in ("keep", "conv")) / len(pan)
        measured[g][ru] = {"keep0": round(k0, 4), "conv0": round(c0, 4), "keep1": round(k1, 4),
                           "conv1": round(c1, 4), "m_call": round(m, 4)}
    print(g, json.dumps(measured[g]), flush=True)
A_CPU = round(time.process_time() - T0, 1)

# cross-checks against the published numbers
TRACE_W232 = {  # W2-32 calc_bands.py literal (from W2-24 trace table)
    "F":     (0.52, 0.002, 0.907, 0.874, 1.172),
    "AC":    (1.00, 1.000, 0.52, 0.021, 1.248),
    "C3":    (0.973, 0.002, 0.907, 0.870, 1.389),
    "C3AC":  (1.00, 1.000, 0.961, 0.010, 1.469),
}
t1 = json.loads((W2 / "W2-30_double_mutant" / "t1_exact_m.json").read_text())
t1c = json.loads((W2 / "W2-30_double_mutant" / "t1c_class_m.json").read_text())
checks = {}
for g, gname in NAMEMAP.items():
    mf = measured[g]["FID"]
    checks[g] = {
        "FID_vs_TRACE_maxdiff": round(max(abs(a - b) for a, b in zip(
            (mf["keep0"], mf["conv0"], mf["keep1"], mf["conv1"], mf["m_call"]), TRACE_W232[g])), 4),
        "class_m_vs_t1c": round(measured[g]["class"]["m_call"] - t1c[gname]["m_base_class"], 4),
        "exact_m_vs_t1": round(measured[g]["exact"]["m_call"] - t1[gname]["ZERO"]["m_base_exact"], 4),
        "exact_keep0_vs_t1": round(measured[g]["exact"]["keep0"] - t1[gname]["ZERO"]["side0"]["keep_exact"], 4),
    }
print("checks", json.dumps(checks), flush=True)

RULERS = {"FID_W232": TRACE_W232}
for ru in ("class", "exact"):
    RULERS[ru] = {g: tuple(measured[g][ru][k] for k in ("keep0", "conv0", "keep1", "conv1", "m_call"))
                  for g in NAMEMAP}

# ---------------------------------------------------------------- Part B: W2-32 arithmetic (copied verbatim)
B_HI, B_LO = 163, 27


def nb_sum(rng, n, mean, V):
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


def simulate(mA, mB, V, s, b, start, G_, N, seed):
    rng = np.random.default_rng(seed)
    nA = np.full(N, 1 if start == "A" else 0, dtype=np.int64)
    nB = np.full(N, 1 if start == "B" else 0, dtype=np.int64)
    Bc = np.zeros(N, dtype=np.int64)
    hit27 = np.zeros(N, bool)
    hit163 = np.zeros(N, bool)
    live = np.ones(N, bool)
    for _ in range(G_):
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
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return lo, hi


def band(plo, phi, n, a=0.05):
    lo = int(binom.ppf(a / 2, n, plo))
    hi = int(binom.isf(a / 2, n, phi))
    return lo, hi


F_LO, F_HI = cp(4, 128)
NSIM = 20000
ARMS = {"F": ("F", "A"), "AC": ("F", "B"), "C3": ("C3", "A"), "C3AC": ("C3", "B")}
n18 = json.loads((W2 / "N18_two_type_fit" / "twotype.json").read_text())["fits_sorted"]
n18 = [f for f in n18 if f["dev_bins"] <= 4.0 and f["s"] > 0]


def run_ruler(TRACE):
    STATIC = {}
    for g, (k0, c0, k1, c1, mb) in TRACE.items():
        c, k = (c0 + c1) / 2, (k0 + k1) / 2
        STATIC[g] = {"conv": round(c, 4), "keep": round(k, 4), "L_geom": round(c / (1 - k), 3), "m_call": mb}
    for g in STATIC:
        STATIC[g]["ratio_call"] = round(STATIC[g]["m_call"] / STATIC["F"]["m_call"], 4)
        STATIC[g]["ratio_geom"] = round(STATIC[g]["L_geom"] / STATIC["F"]["L_geom"], 4)
    res = {"static": STATIC, "models": {}}
    seed = 1
    for model in ("M1", "M2", "M3"):
        rows = []
        if model == "M1":
            psets = [(f["m0"], f["m1"], f["V"], f["s"]) for f in n18]
        else:
            psets = [(m0, None, V, s) for m0 in np.round(np.arange(0.70, 1.001, 0.02), 2)
                     for V in (3.0, 7.0, 12.0) for s in (7.5e-4, 0.01, 0.035)]
        for G_ in (40, 60):
            for (m0, m1, V, s) in psets:
                if model == "M1":
                    mt = {"F": m0, "AC": m1,
                          "C3": m0 * STATIC["C3"]["ratio_geom"], "C3AC": m0 * STATIC["C3AC"]["ratio_geom"]}
                else:
                    key = "ratio_call" if model == "M2" else "ratio_geom"
                    mt = {g: m0 * STATIC[g][key] for g in STATIC}
                seed += 1
                p27F, p163F = simulate(mt["F"], mt["AC"], V, s, 0.07, "A", G_, NSIM, seed)
                ok = bool((F_LO <= p163F <= F_HI) and (F_LO <= p27F <= F_HI))
                row = {"m0": float(m0), "V": V, "s": s, "G": G_, "m": {g: round(v, 3) for g, v in mt.items()},
                       "F": [round(p27F, 4), round(p163F, 4)], "calibrated": ok}
                if ok:
                    for arm, (pair, start) in ARMS.items():
                        if arm == "F":
                            continue
                        mA = mt["F"] if pair == "F" else mt["C3"]
                        mB = mt["AC"] if pair == "F" else mt["C3AC"]
                        seed += 1
                        p27, p163 = simulate(mA, mB, V, s, 0.07, start, G_, NSIM, seed)
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
                                "calibrated_m_range": {g: [round(min(r["m"][g] for r in cal), 3),
                                                           round(max(r["m"][g] for r in cal), 3)] for g in ARMS}
                                if cal else None}
    return res


OUT = {"measured_per_side": measured, "checks": checks, "partA_cpu_s": A_CPU, "rulers": {}}
for ru, TR in RULERS.items():
    OUT["rulers"][ru] = run_ruler(TR)
    print(ru, json.dumps({m: OUT["rulers"][ru]["models"][m]["summary"] for m in ("M1", "M2", "M3")}), flush=True)

# regression: FID ruler must reproduce W2-32 calc_bands.json summaries exactly
w232 = json.loads((W2 / "W2-32_next_experiments" / "calc_bands.json").read_text())
OUT["regression_FID_reproduces_W232"] = all(
    OUT["rulers"]["FID_W232"]["models"][m]["summary"] == w232["models"][m]["summary"] for m in ("M1", "M2", "M3"))
print("regression", OUT["regression_FID_reproduces_W232"], flush=True)

# ---------------------------------------------------------------- Part C: bands, disjointness, power
NARM = {"F": 256, "AC": 384, "C3": 64, "C3AC": 64}
FLOOR_FACTOR = 0.75 / 0.8652   # W2-32 allowance: M3 C3-arm floor 0.865 -> 0.75 (applied proportionally)


def power(px, bandy, n):
    lo, hi = bandy
    return round(float(binom.cdf(lo - 1, n, px) + binom.sf(hi, n, px)), 3)


bands = {}
for ru in RULERS:
    bands[ru] = {}
    for arm in ARMS:
        d = {}
        for n in sorted({NARM[arm], 128}):
            dn = {}
            for m in ("M1", "M2", "M3"):
                sm = OUT["rulers"][ru]["models"][m]["summary"].get(arm)
                if not sm:
                    continue
                plo, phi = sm["P163_range"]
                dn[m] = {"p": [plo, phi], "band": band(plo, phi, n)}
                if m == "M3" and arm in ("C3", "C3AC"):
                    dn[m]["band_with_allowance"] = band(plo * FLOOR_FACTOR, phi, n)
            pw = {}
            for x in [k for k in dn]:
                px = float(np.mean(dn[x]["p"]))
                xlo, xhi = dn[x]["p"]
                for y in [k for k in dn]:
                    if x == y:
                        continue
                    ylo, yhi = dn[y]["p"]
                    pw[x + "_outside_" + y + "_mid"] = power(px, dn[y]["band"], n)
                    # worst case: x at the end of its range nearest y's range
                    pxw = xlo if xlo > yhi else (xhi if xhi < ylo else px)
                    pw[x + "_outside_" + y + "_worst"] = power(pxw, dn[y]["band"], n)
            if "M2" in dn and "M3" in dn:
                b2 = dn["M2"]["band"]
                b3 = dn["M3"].get("band_with_allowance", dn["M3"]["band"])
                dn["M2_M3_disjoint"] = bool(b2[1] < b3[0] or b3[1] < b2[0])
                dn["M2_M3_gap"] = [b2[1] + 1, b3[0] - 1] if b2[1] < b3[0] else None
            dn["power"] = pw
            d[str(n)] = dn
        bands[ru][arm] = d
OUT["bands_B163"] = bands
OUT["cpu_s"] = round(time.process_time() - T0, 1)
(HERE / "c3_bands.json").write_text(json.dumps(OUT, indent=1))
for ru in RULERS:
    print("==", ru, json.dumps(OUT["rulers"][ru]["static"]))
    for arm in ARMS:
        print(" ", arm, json.dumps(bands[ru][arm][str(NARM[arm])]))
print("cpu_s", OUT["cpu_s"])
