"""W2-22 a1: pre-registered primary/secondary readouts, censoring treatments C+/C-, Fisher one-sided, Koopman ratio CI.
python -B a1_analyze.py [TAG ...] -> a1_analysis.json"""
import json, sys, math
from scipy.stats import fisher_exact, chi2
from scipy.optimize import minimize_scalar
import w22

def koopman_ci(x1, n1, x2, n2, alpha=0.05):
    """Koopman score CI for p1/p2 by inversion on a log grid."""
    crit = chi2.ppf(1 - alpha, 1)
    def stat(phi):
        def nll(p2):
            p1 = phi * p2
            if not (0 < p1 < 1 and 0 < p2 < 1): return 1e18
            return -(x1 * math.log(p1) + (n1 - x1) * math.log(1 - p1) + x2 * math.log(p2) + (n2 - x2) * math.log(1 - p2))
        hi = min(1.0, 1.0 / phi) - 1e-12
        p2 = minimize_scalar(nll, bounds=(1e-12, hi), method="bounded", options={"xatol": 1e-12}).x
        p1 = phi * p2
        return (x1 - n1 * p1) ** 2 / (n1 * p1 * (1 - p1)) + (x2 - n2 * p2) ** 2 / (n2 * p2 * (1 - p2))
    grid = [10 ** (k / 400) for k in range(-1600, 1601)]
    ok = [g for g in grid if stat(g) <= crit]
    return (min(ok) if ok else None, max(ok) if ok else None)

def load(tag):
    return [json.loads(l) for l in open(w22.HERE / ("runs_%s.jsonl" % tag))]

def readouts(R, censor):
    cond = [r for r in R if r["B"] >= 27]
    def succ(r):
        if r["B"] >= 163: return True
        if r["stop"] == "free_cap256": return censor == "C+"
        return False
    condx = [r for r in R if r["Bxk"] >= 27]
    def succx(r):
        if r["Bxk"] >= 163: return True
        if r["stop"] == "free_cap256": return censor == "C+"
        return False
    return {"n": len(R), "E27": len(cond), "cond_succ": sum(map(succ, cond)),
            "P_B163": sum(map(succ, R)) / len(R), "P_E27": len(cond) / len(R),
            "xk_E27": len(condx), "xk_cond_succ": sum(map(succx, condx)),
            "maxA_ge128": sum(r["maxA"] >= 128 for r in R),
            "cap256_in_cond_below163": sum(1 for r in cond if r["stop"] == "free_cap256" and r["B"] < 163),
            "stops_cond": {s: sum(1 for r in cond if r["stop"] == s) for s in {r["stop"] for r in cond}},
            "cpu_s": round(sum(r["cpu_s"] for r in R), 1)}

def compare(a, b, key_n="E27", key_s="cond_succ"):
    x1, n1, x2, n2 = a[key_s], a[key_n], b[key_s], b[key_n]
    p = fisher_exact([[x1, n1 - x1], [x2, n2 - x2]], alternative="greater")[1]
    p2s = fisher_exact([[x1, n1 - x1], [x2, n2 - x2]])[1]
    r1, r2 = x1 / n1, x2 / n2
    return {"x1/n1": "%d/%d" % (x1, n1), "x2/n2": "%d/%d" % (x2, n2), "rate1": round(r1, 3), "rate2": round(r2, 3),
            "ratio": (round(r1 / r2, 3) if r2 else float("inf")), "fisher_1s": p, "fisher_2s": p2s,
            "koopman95": koopman_ci(x1, n1, x2, n2), "diff": round(r1 - r2, 3)}

if __name__ == "__main__":
    out = {}
    D = {t: load(t) for t in ["FIELD", "FREE"] + sys.argv[1:]}
    for c in ("C+", "C-"):
        ro = {t: readouts(R, c) for t, R in D.items()}
        out[c] = {"readouts": ro, "primary_FIELD_vs_FREE": compare(ro["FIELD"], ro["FREE"]),
                  "diag_xk_FIELD_vs_FREE": compare(ro["FIELD"], ro["FREE"], "xk_E27", "xk_cond_succ")}
        for t in sys.argv[1:]:
            out[c]["mech_FIELD_vs_" + t] = compare(ro["FIELD"], ro[t], "xk_E27", "xk_cond_succ")
            out[c]["mech_B_FIELD_vs_" + t] = compare(ro["FIELD"], ro[t])
    P, M = out["C+"]["primary_FIELD_vs_FREE"], out["C-"]["primary_FIELD_vs_FREE"]
    sup = P["fisher_1s"] < 0.01 and (P["rate2"] == 0 and P["rate1"] > 0 or P["rate1"] >= 3 * P["rate2"])
    no = M["koopman95"][1] is not None and M["koopman95"][1] < 3
    elig = all(out["C+"]["readouts"][t]["E27"] >= 10 for t in ("FIELD", "FREE"))
    out["verdict"] = "INELIGIBLE" if not elig else ("SECOND REGIME SUPPORTED" if sup and not no else
                     "NO SECOND REGIME" if no and not sup else "UNRESOLVED")
    json.dump(out, open(w22.HERE / "a1_analysis.json", "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))
