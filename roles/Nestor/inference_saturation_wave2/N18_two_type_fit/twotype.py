"""N18: does a two-type branching process (subcritical founder type + rare heritable supercritical side-0
morph, W2-17) reproduce the K2b depth distribution (670 BASE splice-off 7ae3 runs; 367 with depth >= 1):
24 at depth 8-13, only 3 at 14-21, 19 at >= 22 of which 16 reach >= 161, S(d|D>=1) at d=2,4,8,16,20 =
.580 .278 .125 .060 .055 (W2-17 a1, W2-3 K2b)?
Offspring: negative binomial with mean m_type and variance V (W2-17's best single-type GW had sigma^2 ~7).
Each birth switches founder-type -> morph with prob s (W2-17 a4: ~3.5% of causal births in controls switch
1->0; heritability of side 0.93 so morph->founder back-switch b = 0.07). A lineage whose alive count reaches
CAP is counted a runaway (depth >= 161; it saturates the 256-site field). Depth = deepest generation.
Pure arithmetic, no world code."""
import json, math, pathlib, random
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
OBS = {"n_pos": 367, "n_8_13": 24, "n_14_21": 3, "n_ge22": 19, "P161_given_22": 0.842,
       "S": [0.5804, 0.2779, 0.1253, 0.0599, 0.0545]}
CAP = 60
GMAX = 400


def nb(rng, mean, V, size):
    if size == 0:
        return np.zeros(0, dtype=int)
    if V <= mean:
        return rng.poisson(mean, size)
    r = mean * mean / (V - mean)
    p = r / (r + mean)
    return rng.negative_binomial(r, p, size)


def lineage(rng, m0, m1, V, s, b):
    n0, n1, g = 1, 0, 0
    while True:
        if n0 + n1 == 0:
            return g - 1, False          # deepest generation that existed
        if n0 + n1 >= CAP:
            return 10 ** 6, True
        if g >= GMAX:
            return g, (n1 > 0)
        k0 = int(nb(rng, m0, V, n0).sum())
        k1 = int(nb(rng, m1, V, n1).sum())
        sw01 = rng.binomial(k0, s) if k0 else 0
        sw10 = rng.binomial(k1, b) if k1 else 0
        n0, n1 = k0 - sw01 + sw10, k1 - sw10 + sw01
        g += 1


def predict(m0, m1, V, s, b, N, seed):
    rng = np.random.default_rng(seed)
    D = []
    run = 0
    for _ in range(N):
        d, r = lineage(rng, m0, m1, V, s, b)
        D.append(d)
        run += r
    D = np.array(D)
    pos = D >= 1
    Dp = D[pos]
    npos = pos.sum()
    scale = OBS["n_pos"] / npos
    S = [float((Dp >= d).mean()) for d in (2, 4, 8, 16, 20)]
    ge22 = (Dp >= 22).sum()
    ge161 = (Dp >= 161).sum()
    out = {"m0": m0, "m1": m1, "V": V, "s": s, "b": b,
           "pred_n_8_13": float(((Dp >= 8) & (Dp <= 13)).sum() * scale),
           "pred_n_14_21": float(((Dp >= 14) & (Dp <= 21)).sum() * scale),
           "pred_n_ge22": float(ge22 * scale),
           "pred_P161_given_22": float(ge161 / ge22) if ge22 else None,
           "S": [round(x, 4) for x in S]}
    # score: Poisson deviance on the 4 binned counts + squared S error
    obs_bins = [OBS["n_pos"] - OBS["n_8_13"] - OBS["n_14_21"] - OBS["n_ge22"], OBS["n_8_13"], OBS["n_14_21"], OBS["n_ge22"]]
    pb = [out["pred_n_8_13"], out["pred_n_14_21"], out["pred_n_ge22"]]
    pred_bins = [OBS["n_pos"] - sum(pb)] + pb
    dev = 0.0
    for o, e in zip(obs_bins, pred_bins):
        e = max(e, 1e-6)
        dev += 2 * ((o * math.log(o / e) if o > 0 else 0) - (o - e))
    out["dev_bins"] = round(dev, 2)
    out["S_sse"] = round(sum((a - b_) ** 2 for a, b_ in zip(S, OBS["S"])), 5)
    return out


if __name__ == "__main__":
    res = []
    grid = [(m0, m1, V, s) for m0 in (0.8, 0.85, 0.9, 0.95) for m1 in (1.05, 1.1, 1.2)
            for V in (3.0, 7.0, 12.0) for s in (0.01, 0.035)]
    for i, (m0, m1, V, s) in enumerate(grid):
        res.append(predict(m0, m1, V, s, 0.07, 40000, 1000 + i))
    # single-type comparators (no morph)
    for m0 in (0.95, 0.99, 1.0, 1.02):
        for V in (3.0, 7.0, 12.0):
            res.append(predict(m0, m0, V, 0.0, 0.0, 40000, 5000 + int(m0 * 100) + int(V)))
    res.sort(key=lambda r: r["dev_bins"] + 200 * r["S_sse"])
    (HERE / "twotype.json").write_text(json.dumps({"observed": OBS, "fits_sorted": res}, indent=1))
    for r in res[:8]:
        print(r)
    print("best single-type:", next(r for r in res if r["s"] == 0.0))
