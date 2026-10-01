"""W2-12 supplementary analyses (read-only over run_table.json).

1. Threshold scan: depth is a record statistic (world max over chains). Under independent founders
   S_k(d) = 1 - (1 - S_1(d))^k at EVERY threshold d. Fit beta (cloglog slope on log k, block fixed
   effects) at each d, with LRT vs beta = 1.
2. Banded (multinomial) test: outcomes {<5, 5-19, >=20}; independence predicts the band
   probabilities at k from the k=1 band probabilities of the same block. Tests whether any k-excess is
   confined to the MID band (5-19) -- the "copies meeting copies early raise depth >= 5 but not runaway"
   reading.
3. Seed pairing within dose blocks: k arms share seed numbers. Is the outcome correlated across k
   within a seed (permutation test)?
4. Batch heterogeneity of p1 among k=1 arms: exact (Monte-Carlo) contingency test, splice OFF and ON.
5. Directional check: does the k=4 excess sit in the blocks with high or low own p1?
"""
import json
import math
import pathlib
import random
from collections import defaultdict

import numpy as np
from scipy import optimize, stats

HERE = pathlib.Path(__file__).resolve().parent
T = json.loads((HERE / "run_table.json").read_text())
ROWS = [r for r in T if r["comparable"]]
DOSE = sorted({r["block"] for r in ROWS if r["k"] > 1})


def ll_binom(x, n, P):
    P = np.clip(P, 1e-12, 1 - 1e-12)
    return x * np.log(P) + (n - x) * np.log1p(-P)


def cells(thr, rows=ROWS):
    c = defaultdict(lambda: [0, 0])
    for r in rows:
        c[(r["block"], r["k"])][0] += r["depth"] >= thr
        c[(r["block"], r["k"])][1] += 1
    return c


def fit_fe(c, beta_free):
    blocks = sorted({b for b, k in c})
    idx = {b: i for i, b in enumerate(blocks)}

    def nll(th):
        beta = th[-1] if beta_free else 1.0
        s = 0.0
        for (b, k), (x, n) in c.items():
            P = -math.expm1(-math.exp(th[idx[b]]) * k ** beta)
            s += float(ll_binom(x, n, P))
        return -s
    x0 = []
    for b in blocks:
        x, n = c.get((b, 1), (0, 0))
        p = min(max(x / n if n else 0.1, 0.003), 0.9)
        x0.append(math.log(-math.log1p(-p)))
    if beta_free:
        x0.append(1.0)
    r = optimize.minimize(nll, x0, method="L-BFGS-B")
    return -float(r.fun), [float(v) for v in r.x]


def threshold_scan():
    out = {}
    for d in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 30, 50, 100, 150, 200, 300):
        c = cells(d)
        if sum(x for x, n in c.values()) < 5:
            continue
        l0, _ = fit_fe(c, False)
        l1, th = fit_fe(c, True)
        G = 2 * (l1 - l0)
        x1 = sum(c[(b, 1)][0] for b in {b for b, k in c})
        n1 = sum(c[(b, 1)][1] for b in {b for b, k in c})
        p1 = x1 / n1
        k4 = [(c[(b, 4)]) for b in DOSE if (b, 4) in c]
        x4, n4 = sum(x for x, n in k4), sum(n for x, n in k4)
        out[d] = {"beta_hat": round(th[-1], 3), "G": round(G, 3), "p_beta_ne_1": round(float(stats.chi2.sf(max(G, 0), 1)), 5),
                  "pooled_k1": [x1, n1], "k4_obs": x4, "k4_exp_pooledp1": round(n4 * (1 - (1 - p1) ** 4), 1)}
    return out


def banded():
    """Per dose block, band probs at k=1 (MLE) -> predicted bands at k: P(D<5)=F5^k, P(D<20)=F20^k.
    Joint fit: per block (F5_b, F20_b) shared across k, independence through F^k. LRT vs saturated
    multinomial per (block,k). Also report observed vs expected per band at k>1."""
    res = {}
    tot_G, tot_df = 0.0, 0
    for b in DOSE:
        arms = defaultdict(lambda: [0, 0, 0])
        for r in ROWS:
            if r["block"] != b:
                continue
            band = 0 if r["depth"] < 5 else (1 if r["depth"] < 20 else 2)
            arms[r["k"]][band] += 1

        def nll(th):
            F20 = 1 / (1 + math.exp(-th[0]))          # P(D1 < 20)
            F5 = F20 / (1 + math.exp(-th[1]))         # P(D1 < 5) < F20
            s = 0.0
            for k, cnt in arms.items():
                p = [F5 ** k, F20 ** k - F5 ** k, 1 - F20 ** k]
                s += sum(c * math.log(max(q, 1e-12)) for c, q in zip(cnt, p))
            return -s
        r = optimize.minimize(nll, [3.0, 2.0], method="Nelder-Mead", options={"xatol": 1e-9, "fatol": 1e-11})
        F20 = 1 / (1 + math.exp(-r.x[0]))
        F5 = F20 / (1 + math.exp(-r.x[1]))
        lsat = sum(sum(c * math.log(c / sum(cnt)) for c in cnt if c) for cnt in arms.values())
        G = 2 * (lsat + r.fun)
        df = 2 * len(arms) - 2
        tot_G += G
        tot_df += df
        exp = {}
        for k, cnt in sorted(arms.items()):
            n = sum(cnt)
            p = [F5 ** k, F20 ** k - F5 ** k, 1 - F20 ** k]
            exp[k] = {"obs(<5,5-19,>=20)": cnt, "exp": [round(n * q, 1) for q in p]}
        res[b] = {"F5": round(F5, 4), "F20": round(F20, 4), "G": round(G, 3), "df": df,
                  "p": round(float(stats.chi2.sf(G, df)), 5), "arms": exp}
    # pooled across dose blocks, observed vs expected per band at each k>1
    pooled = defaultdict(lambda: [[0, 0, 0], [0.0, 0.0, 0.0]])
    for b in DOSE:
        for k, v in res[b]["arms"].items():
            if k == 1:
                continue
            for j in range(3):
                pooled[k][0][j] += v["obs(<5,5-19,>=20)"][j]
                pooled[k][1][j] += v["exp"][j]
    return {"per_block": res, "total": {"G": round(tot_G, 3), "df": tot_df, "p": round(float(stats.chi2.sf(tot_G, tot_df)), 5)},
            "pooled_k_gt1_obs_vs_exp_own_block_fit": {k: {"obs": v[0], "exp": [round(x, 1) for x in v[1]]}
                                                      for k, v in sorted(pooled.items())}}


def seed_pairing(thr=5, perms=20000):
    out = {}
    rng = random.Random(12)
    for b in DOSE:
        by = defaultdict(dict)
        for r in ROWS:
            if r["block"] == b:
                by[r["seed"]][r["k"]] = int(r["depth"] >= thr)
        ks = sorted({k for s in by.values() for k in s})
        seeds = sorted(by)
        cols = {k: [by[s][k] for s in seeds] for k in ks}

        def stat(cs):
            # sum over k-pairs of #seeds with both successes
            t = 0
            for i, a in enumerate(ks):
                for bk in ks[i + 1:]:
                    t += sum(x & y for x, y in zip(cs[a], cs[bk]))
            return t
        obs = stat(cols)
        ge = 0
        null = []
        for _ in range(perms):
            cs = {k: rng.sample(v, len(v)) for k, v in cols.items()}
            s = stat(cs)
            null.append(s)
            ge += s >= obs
        out[b] = {"thr": thr, "obs_both_success_pairs": obs, "null_mean": round(sum(null) / perms, 2),
                  "p_upper": round((ge + 1) / (perms + 1), 4),
                  "p_lower": round((sum(1 for s in null if s <= obs) + 1) / (perms + 1), 4)}
    return out


def heterogeneity(rows, thr, sims=50000):
    """Monte-Carlo exact test of homogeneity across blocks (k=1 rows): chi-square statistic,
    null by permuting outcomes across blocks (hypergeometric)."""
    blocks = defaultdict(list)
    for r in rows:
        blocks[r["block"]].append(int(r["depth"] >= thr))
    names = sorted(blocks)
    ys = [y for b in names for y in blocks[b]]
    sizes = [len(blocks[b]) for b in names]
    N, X = len(ys), sum(ys)
    p = X / N

    def chi(counts):
        return sum((x - n * p) ** 2 / (n * p * (1 - p)) for x, n in zip(counts, sizes)) if 0 < p < 1 else 0.0
    obs_counts = [sum(blocks[b]) for b in names]
    obs = chi(obs_counts)
    rng = random.Random(3)
    ge = 0
    for _ in range(sims):
        rng.shuffle(ys)
        i, cnt = 0, []
        for n in sizes:
            cnt.append(sum(ys[i:i + n]))
            i += n
        ge += chi(cnt) >= obs - 1e-12
    return {"thr": thr, "blocks": {b: [x, n, round(x / n, 3)] for b, x, n in zip(names, obs_counts, sizes)},
            "pooled": [X, N, round(p, 4)], "chi2": round(obs, 3), "df": len(names) - 1,
            "p_asymptotic": round(float(stats.chi2.sf(obs, len(names) - 1)), 5),
            "p_exact_mc": round((ge + 1) / (sims + 1), 5)}


def fisher2(a, n1, b, n2):
    t = stats.fisher_exact([[a, n1 - a], [b, n2 - b]])
    return float(t[1])


if __name__ == "__main__":
    out = {}
    out["threshold_scan"] = threshold_scan()
    out["banded"] = banded()
    out["seed_pairing_d5"] = seed_pairing(5)
    out["seed_pairing_d20"] = seed_pairing(20)
    k1 = [r for r in ROWS if r["k"] == 1]
    out["heterogeneity_k1_splice_off_d5"] = heterogeneity(k1, 5)
    out["heterogeneity_k1_splice_off_d20"] = heterogeneity(k1, 20)
    on = [r for r in T if r["splice"] == "ON" and r["k"] == 1 and r["writeback"] == "BASE"]
    out["heterogeneity_k1_splice_on_d5"] = heterogeneity(on, 5)
    on_noc9 = [r for r in on if r["block"] != "c9_h2_frozen"]
    out["heterogeneity_k1_splice_on_d5_without_C9"] = heterogeneity(on_noc9, 5)
    out["splice_on_gap_cnorecomb_vs_crunaway_d5_fisher_two_sided"] = fisher2(5, 24, 4, 150)
    # selection-adjusted: the 5/24 vs 4/150 pair is the max-vs-min of 4-5 blocks; the MC homogeneity
    # p above is the multiplicity-honest number.
    # 5. per dose block: own k=1 rate vs k=4 excess against pooled p1
    E = lambda d: d >= 5
    p1 = sum(E(r["depth"]) for r in k1) / len(k1)
    per = {}
    for b in DOSE:
        rr = [r for r in ROWS if r["block"] == b]
        x1 = sum(E(r["depth"]) for r in rr if r["k"] == 1)
        n1 = sum(1 for r in rr if r["k"] == 1)
        x4 = sum(E(r["depth"]) for r in rr if r["k"] == 4)
        n4 = sum(1 for r in rr if r["k"] == 4)
        per[b] = {"k1": [x1, n1], "k4": [x4, n4], "k4_exp_pooled": round(n4 * (1 - (1 - p1) ** 4), 1),
                  "k4_exp_own_k1": round(n4 * (1 - (1 - x1 / n1) ** 4), 1),
                  "k4_tail_p_pooled": round(float(stats.binom.sf(x4 - 1, n4, 1 - (1 - p1) ** 4)), 5)}
    out["dose_blocks_vs_pooled_p1_d5"] = {"pooled_p1": round(p1, 4), "blocks": per}
    (HERE / "extra.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
