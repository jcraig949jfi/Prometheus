"""W2-6 check C1 (T3 vs T4(c)): re-read the finished S3 pairwise-knockout data by single-KO stratum.

Read-only over ../../inference_harvest_2026-09-30/forensics/s3_pairs.json (no VM calls).
Question: the frozen S3 rule fired "T4(c) DEAD" on a pooled excess that mixes strata whose additive null is
mis-calibrated in opposite directions (null = 0 when both singles were 0/3; inflated when a single was 1/3).
Does the verdict survive a stratum-matched comparison of state-free (SF) vs state-dependent (SD) genomes,
and does the 16000006 walk cluster (T4's one residue) carry excess synthetic lethality?
Output: c1_t3_t4_s3_strata.json
"""
import json
import math
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
d = json.load(open(FOR / "s3_pairs.json"))


def stratum(nu):
    return "0/3+0/3" if nu == 0 else ("1/3+1/3" if nu > 0.4 else "0/3+1/3")


def tally(rows):
    out = {}
    for r in rows:
        for i, j, leth, conf, nu in r["pairs"]:
            s = stratum(nu)
            o = out.setdefault(s, [0, 0])
            o[0] += 1
            o[1] += bool(leth and conf)
    return {k: {"pairs": v[0], "lethal": v[1], "rate": round(v[1] / v[0], 4)} for k, v in sorted(out.items())}


def fisher_two_sided(a, b, c, d_):
    """2x2 [[a,b],[c,d]] two-sided Fisher exact p via hypergeometric enumeration (log space)."""
    n1, n2, k = a + b, c + d_, a + c
    lf = lambda n: math.lgamma(n + 1)
    def lp(x):
        return lf(n1) - lf(x) - lf(n1 - x) + lf(n2) - lf(k - x) - lf(n2 - k + x) - (lf(n1 + n2) - lf(k) - lf(n1 + n2 - k))
    lo, hi = max(0, k - n2), min(k, n1)
    p0 = lp(a)
    return min(1.0, sum(math.exp(lp(x)) for x in range(lo, hi + 1) if lp(x) <= p0 + 1e-9))


SF, SD = d["panel"], d["comparators"]
e700 = [r for r in SF if r["src"] == "16000006_e700"]
sf_rest = [r for r in SF if r["src"] != "16000006_e700"]
res = {"SF": tally(SF), "SD": tally(SD), "SF_16000006_e700": tally(e700), "SF_other": tally(sf_rest)}
tests = {}
for s in ("0/3+0/3", "0/3+1/3", "1/3+1/3"):
    a, n1 = res["SF"][s]["lethal"], res["SF"][s]["pairs"]
    c, n2 = res["SD"][s]["lethal"], res["SD"][s]["pairs"]
    tests[s] = {"SF_rate": round(a / n1, 4), "SD_rate": round(c / n2, 4), "ratio_SF_SD": round((a / n1) / (c / n2), 3),
                "fisher_p": fisher_two_sided(a, n1 - a, c, n2 - c)}
# genome-level cluster bootstrap of the stratum-matched ratio in the null-0 stratum (genomes resampled)
def g_rate(rows, s):
    t = [0, 0]
    for r in rows:
        for i, j, leth, conf, nu in r["pairs"]:
            if stratum(nu) == s:
                t[0] += 1
                t[1] += bool(leth and conf)
    return t
rng = random.Random(20260930)
boots = []
for _ in range(2000):
    a = [rng.choice(SF) for _ in SF]
    b = [rng.choice(SD) for _ in SD]
    ta, tb = g_rate(a, "0/3+0/3"), g_rate(b, "0/3+0/3")
    if ta[0] and tb[0] and tb[1]:
        boots.append((ta[1] / ta[0]) / (tb[1] / tb[0]))
boots.sort()
tests["0/3+0/3"]["ratio_cluster_boot95"] = [round(boots[int(0.025 * len(boots))], 3), round(boots[int(0.975 * len(boots))], 3)]
# 16000006 cluster vs other SF in the null-0 stratum
a, n1 = res["SF_16000006_e700"]["0/3+0/3"]["lethal"], res["SF_16000006_e700"]["0/3+0/3"]["pairs"]
c, n2 = res["SF_other"]["0/3+0/3"]["lethal"], res["SF_other"]["0/3+0/3"]["pairs"]
tests["e700_vs_otherSF_null0"] = {"e700_rate": round(a / n1, 4), "other_rate": round(c / n2, 4),
                                  "fisher_p": fisher_two_sided(a, n1 - a, c, n2 - c)}
out = {"strata": res, "tests": tests,
       "negative_control_passenger_rate": 0.0,
       "reading": "see REPORT.md C1"}
(HERE / "c1_t3_t4_s3_strata.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
