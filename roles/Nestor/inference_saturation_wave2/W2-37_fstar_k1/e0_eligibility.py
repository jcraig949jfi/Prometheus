"""W2-37 e0: eligibility/power from W2-22's rates (pre-run). Expected Newcombe half-width and P(PASS)/P(KILL)
by exact enumeration over binomial outcomes, per candidate (n_FIELD, n_FREE), under C- and C+ FREE rates;
plus W2-22 per-seed CPU cost bootstrap. Writes e0_eligibility.json."""
import json, math, random, pathlib
from newcombe import newcombe, verdict
HERE = pathlib.Path(__file__).resolve().parent
W22 = HERE.parent / "W2-22_second_regime"
F = [json.loads(l) for l in open(W22 / "runs_FIELD.jsonl")]
R = [json.loads(l) for l in open(W22 / "runs_FREE.jsonl")]
pF = sum(r["maxA"] >= 40 and r["B"] >= 27 for r in F) / len(F)
pRm = sum(r["maxA"] >= 40 and r["B"] >= 27 for r in R) / len(R)
pRp = sum((r["maxA"] >= 40 and r["B"] >= 27) or r["stop"] == "free_cap256" for r in R) / len(R)


def binpmf(n, p, eps=1e-9):
    out, lg = [], math.lgamma
    for k in range(n + 1):
        v = math.exp(lg(n + 1) - lg(k + 1) - lg(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p))
        if v > eps:
            out.append((k, v))
    return out


def power(n1, p1, n2, p2):
    a, b = binpmf(n1, p1), binpmf(n2, p2)
    hw = pp = pk = 0.0
    for x1, w1 in a:
        for x2, w2 in b:
            d, lo, hi = newcombe(x1, n1, x2, n2)
            w = w1 * w2
            hw += w * (hi - lo) / 2
            v = verdict(lo, hi)
            pp += w * (v == "PASSED"); pk += w * (v == "KILLED")
    return round(hw, 4), round(pp, 3), round(pk, 3)


def joint_pass(n1, n2):
    """P(PASS under both C- and C+): C+ adds cap-censored B<27 FREE runs (rate pRp - pRm) as successes."""
    pc = pRp - pRm
    a = binpmf(n1, pF)
    # FREE outcomes: multinomial (success, censored-B<27, other)
    tot = 0.0
    for x1, w1 in a:
        for xs, ws in binpmf(n2, pRm):
            for xc, wc in binpmf(n2 - xs, pc / (1 - pRm)):
                w = w1 * ws * wc
                if w < 1e-10:
                    continue
                _, l1, h1 = newcombe(x1, n1, xs, n2)
                _, l2, h2 = newcombe(x1, n1, xs + xc, n2)
                tot += w * (verdict(l1, h1) == "PASSED" and verdict(l2, h2) == "PASSED")
    return round(tot, 3)


cpuF = [r["cpu_s"] for r in F]; cpuR = [r["cpu_s"] for r in R]
rng = random.Random(37)


def cost_q(n1, n2, q=(0.5, 0.95), B=2000):
    xs = sorted(sum(rng.choice(cpuF) for _ in range(n1)) + sum(rng.choice(cpuR) for _ in range(n2)) for _ in range(B))
    return [round(xs[int(qq * B) - 1] / 60, 1) for qq in q]


out = {"rates_W2-22": {"R2_FIELD": pF, "R2_FREE_Cminus": pRm, "R2_FREE_Cplus": pRp,
                       "cap256_B_lt_27": sum(r["stop"] == "free_cap256" and r["B"] < 27 for r in R), "n_FREE": len(R)},
       "cpu_s_per_seed": {"FIELD_mean": sum(cpuF) / len(cpuF), "FIELD_max": max(cpuF),
                          "FREE_mean": sum(cpuR) / len(cpuR), "FREE_max": max(cpuR)},
       "normal_approx_n_equal_for_hw_0.035": 2 * pF * (1 - pF) * (1.959964 / 0.035) ** 2, "candidates": []}
for n1, n2 in [(230, 230), (300, 300), (400, 400), (400, 800), (500, 1000), (600, 1200), (700, 1400)]:
    row = {"n_FIELD": n1, "n_FREE": n2,
           "Cminus_hw_Ppass_Pkill": power(n1, pF, n2, pRm), "Cplus_hw_Ppass_Pkill": power(n1, pF, n2, pRp),
           "P_pass_both": joint_pass(n1, n2), "cpu_min_median_p95": cost_q(n1, n2)}
    out["candidates"].append(row); print(row, flush=True)
json.dump(out, open(HERE / "e0_eligibility.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "candidates"}, indent=1))
