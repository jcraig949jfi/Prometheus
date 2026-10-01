"""W2-53 a2: preregistered analysis (PREREG.md). No sims.
Per run (sample of a1): k0 = mean keepF0 (primary), median keepF0, W2-42 band shares, mean m_class, jump share
(JP-type C3/C2/CA/D2/DA at p in 0..51 with (g[p+1] & 0x7F) >= 64), first epoch of a jump-carrying birth (all births).
Classes: success Bxk >= 163; failure Bxk < 163; FREE cap256 with B < 163 and Bxk < 163 = CENSORED (primary: excluded;
sensitivity SENS: failure).
Tests: per-arm one-sided MW; pooled van Elteren (strata FIELD/FREE, w = 1/(N+1), tie-corrected, normal, one-sided)
+ stratified permutation check; pooled AUC of STRONG share. Verdict rule from PREREG.
python -B a2_analyze.py -> a2_analysis.json"""
import json, pathlib, statistics, random, collections, math, sys
import numpy as np
from scipy.stats import mannwhitneyu, rankdata, norm
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
JP = {0xC3, 0xC2, 0xCA, 0xD2, 0xDA}
BANDS = ("STRONG", "PARTIAL", "F-LEVEL", "LOW", "MORPH", "NONCOPIER")


def band(s):   # W2-42 a5_summarize.band, verbatim logic
    if s["convF0"] >= 0.5:
        return "MORPH"
    if max(s["convF0"], s["convF1"]) < 0.5:
        return "NONCOPIER"
    k = s["keepF0"]
    return "STRONG" if k >= 0.85 else "PARTIAL" if k >= 0.62 else "F-LEVEL" if k >= 0.45 else "LOW"


def jf(h):
    g = bytes.fromhex(h)
    return any(g[p] in JP and (g[p + 1] & 0x7F) >= 64 for p in range(52))


def van_elteren(groups):
    """groups: list of (succ_values, fail_values) per stratum. One-sided (succ greater)."""
    num, var = 0.0, 0.0
    for a, b in groups:
        if not a or not b:
            continue
        x = np.array(a + b, float)
        N, n1, n2 = len(x), len(a), len(b)
        rk = rankdata(x)
        W = rk[:n1].sum()
        _, t = np.unique(x, return_counts=True)
        v = n1 * n2 / 12.0 * ((N + 1) - (t ** 3 - t).sum() / (N * (N - 1)))
        w = 1.0 / (N + 1)
        num += w * (W - n1 * (N + 1) / 2.0)
        var += w * w * v
    z = num / math.sqrt(var) if var > 0 else float("nan")
    return {"z": z, "p_greater": float(norm.sf(z)), "stat": num}


def strat_perm(groups, n=20000, seed="W2-53|perm"):
    rng = random.Random(seed)
    obs = van_elteren(groups)["stat"]
    prep = [(a + b, len(a)) for a, b in groups if a and b]
    ge = 0
    for _ in range(n):
        g2 = []
        for vals, n1 in prep:
            v = vals[:]
            rng.shuffle(v)
            g2.append((v[:n1], v[n1:]))
        ge += van_elteren(g2)["stat"] >= obs - 1e-12
    return (ge + 1) / (n + 1)


def mw(a, b):
    if not a or not b:
        return {"n_S": len(a), "n_F": len(b), "p_greater": None, "AUC": None}
    U, p = mannwhitneyu(a, b, alternative="greater")
    return {"n_S": len(a), "n_F": len(b), "med_S": round(statistics.median(a), 3),
            "med_F": round(statistics.median(b), 3), "p_greater": float(p), "AUC": round(U / (len(a) * len(b)), 3)}


def verdict(p, auc):
    if p < 0.05 and auc > 0.7:
        return "SUPPORTED"
    if p > 0.5:
        return "REFUTED"
    return "UNRESOLVED"


if __name__ == "__main__":
    S = json.loads((HERE / "a1_scores.json").read_text())["scores"]
    D = json.loads((HERE / "a1_samples.json").read_text())["samples"]
    first_jump = {}
    for arm in ("FIELD", "FREE"):
        for l in open(HERE / ("r1_%s.jsonl" % arm)):
            d = json.loads(l)
            J = [jf(h) for h in d["gid"]]
            first_jump["%s_%d" % (arm, d["s"])] = next((b[0] for b in d["births"] if b[1] is not None and J[b[1]]), None)
    out = {"per_run": {}, "tests": {}}
    for win in ("PRIM", "ALL"):
        per = {}
        for k, r in D.items():
            hs = r[win]["sample"]
            ks = [S[h]["keepF0"] for h in hs]
            c = collections.Counter(band(S[h]) for h in hs)
            cls = "S" if r["Bxk"] >= 163 else ("CENS" if r["stop"] == "free_cap256" and r["B"] < 163 else "F")
            per[k] = {"arm": r["arm"], "s": r["s"], "cls": cls, "B": r["B"], "Bxk": r["Bxk"], "stop": r["stop"],
                      "e163": r["e163"], "n_pool": r[win]["n_pool"], "n_smp": len(hs),
                      "k0": round(statistics.mean(ks), 4), "k0_med": round(statistics.median(ks), 4),
                      **{b: round(c[b] / len(hs), 3) for b in BANDS},
                      "m_class": round(statistics.mean(S[h]["m_class"] for h in hs), 4),
                      "jump_share": round(sum(jf(h) for h in hs) / len(hs), 3), "first_jump_ep": first_jump[k]}
        out["per_run"][win] = per
        for treat in ("PRIM", "SENS"):
            def grp(arm, key):
                a = [v[key] for v in per.values() if v["arm"] == arm and v["cls"] == "S"]
                b = [v[key] for v in per.values() if v["arm"] == arm and
                     (v["cls"] == "F" or (treat == "SENS" and v["cls"] == "CENS"))]
                return a, b
            T = {}
            for key in ("k0", "k0_med", "STRONG", "m_class", "jump_share", "MORPH"):
                gs = {arm: grp(arm, key) for arm in ("FIELD", "FREE")}
                pa = gs["FIELD"][0] + gs["FREE"][0]
                pb = gs["FIELD"][1] + gs["FREE"][1]
                T[key] = {"FIELD": mw(*gs["FIELD"]), "FREE": mw(*gs["FREE"]), "pooled_raw": mw(pa, pb),
                          "vanElteren": van_elteren([gs["FIELD"], gs["FREE"]])}
            T["k0"]["vanElteren"]["perm_p"] = strat_perm([grp("FIELD", "k0"), grp("FREE", "k0")])
            p = T["k0"]["vanElteren"]["p_greater"]
            auc = T["STRONG"]["pooled_raw"]["AUC"]
            T["VERDICT"] = {"pooled_vE_p_k0": p, "pooled_AUC_STRONG": auc, "verdict": verdict(p, auc)}
            out["tests"]["%s|%s" % (win, treat)] = T
    (HERE / "a2_analysis.json").write_text(json.dumps(out, indent=1))
    for k, T in out["tests"].items():
        print("==", k, T["VERDICT"])
        for key in ("k0", "k0_med", "STRONG", "m_class", "jump_share", "MORPH"):
            t = T[key]
            print("  %-10s FIELD %s\n             FREE  %s\n             pool  %s\n             vE %s" %
                  (key, t["FIELD"], t["FREE"], t["pooled_raw"], t["vanElteren"]))
    per = out["per_run"]["PRIM"]
    for k in sorted(per, key=lambda k: (per[k]["arm"], per[k]["cls"], -per[k]["k0"])):
        v = per[k]
        print("%-12s %-4s B%4d xk%4d %-15s pool%5d k0 %.3f med %.3f STR %.2f PAR %.2f MOR %.2f m %.3f J %.2f fJ %s" %
              (k, v["cls"], v["B"], v["Bxk"], v["stop"], v["n_pool"], v["k0"], v["k0_med"], v["STRONG"],
               v["PARTIAL"], v["MORPH"], v["m_class"], v["jump_share"], v["first_jump_ep"]))
