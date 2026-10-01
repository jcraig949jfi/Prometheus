"""W2-42 a5: summaries of a4_panel.json (no sims).
Keep bands on static side-0 FID keep k0 (F = 0.55, F+byte1 = 0.71, C3 = 0.985 on this panel):
  STRONG k0 >= 0.85 | PARTIAL 0.62 <= k0 < 0.85 | F-LEVEL 0.45 <= k0 < 0.62 | LOW k0 < 0.45
  side-0 converter (morph) := convF0 >= 0.5; non-copier := max(convF0, convF1) < 0.5.
(a) the three replays: births-weighted band shares and mean m_class per 10-epoch window, for all B and for Bxk;
(b) the 55 conditioned W2-29 runs: births-weighted mean m_class, k0, band shares; success (B_xk >= 163) vs failure,
    all runs and morph-free runs (side-0 share < 0.1); Mann-Whitney one-sided."""
import json, pathlib, collections, statistics
from scipy.stats import mannwhitneyu, fisher_exact
HERE = pathlib.Path(__file__).resolve().parent


def band(s):
    if s["convF0"] >= 0.5:
        return "MORPH"
    if max(s["convF0"], s["convF1"]) < 0.5:
        return "NONCOPIER"
    k = s["keepF0"]
    return "STRONG" if k >= 0.85 else "PARTIAL" if k >= 0.62 else "F-LEVEL" if k >= 0.45 else "LOW"


BANDS = ("STRONG", "PARTIAL", "F-LEVEL", "LOW", "MORPH", "NONCOPIER")


def agg(hs, S):
    c = collections.Counter(band(S[h]) for h in hs)
    n = len(hs)
    return {"n": n, **{b: round(c[b] / n, 2) for b in BANDS},
            "m_class": round(statistics.mean(S[h]["m_class"] for h in hs), 3),
            "k0": round(statistics.mean(S[h]["keepF0"] for h in hs), 3)}


if __name__ == "__main__":
    D = json.loads((HERE / "a4_panel.json").read_text())
    S = D["scores"]
    out = {"a": {}, "b": {}}
    for name, rows in D["donors"].items():
        tc = []
        E = max(r[0] for r in rows) + 1
        for w in range(0, E, 10):
            hs = [r[1] for r in rows if w <= r[0] < w + 10]
            if hs:
                tc.append({"ep": "%d-%d" % (w, w + 9), **agg(hs, S)})
        out["a"][name] = {"all": agg([r[1] for r in rows], S), "bxk": agg([r[1] for r in rows if r[2]], S),
                          "timecourse": tc}
    per = {}
    for k, v in D["samples"].items():
        hs = [x[0] for x in v["sample"]]
        per[k] = {"succ": v["succ"][0], "B": v["succ"][2], "Bxk": v["succ"][3], **agg(hs, S)}
    out["b"]["per_run"] = per

    def cmp(sel, key):
        a = [per[k][key] for k in per if sel(k) and per[k]["succ"]]
        b = [per[k][key] for k in per if sel(k) and not per[k]["succ"]]
        p = mannwhitneyu(a, b, alternative="greater")[1] if a and b else None
        return {"succ_n": len(a), "fail_n": len(b), "succ_median": round(statistics.median(a), 3) if a else None,
                "fail_median": round(statistics.median(b), 3) if b else None, "MW_p_greater": p}
    for lab, sel in (("all", lambda k: True), ("morphfree", lambda k: per[k]["MORPH"] < 0.1),
                     ("FULL", lambda k: k.startswith("FULL")), ("BANK", lambda k: k.startswith("BANK"))):
        out["b"][lab] = {key: cmp(sel, key) for key in ("m_class", "k0", "STRONG", "PARTIAL", "MORPH")}
    # strong-keep presence (>= 0.3 of sampled births STRONG) vs success, morph-free runs
    mf = [k for k in per if per[k]["MORPH"] < 0.1]
    t = [[sum(per[k]["STRONG"] >= 0.3 and per[k]["succ"] for k in mf), sum(per[k]["STRONG"] >= 0.3 and not per[k]["succ"] for k in mf)],
         [sum(per[k]["STRONG"] < 0.3 and per[k]["succ"] for k in mf), sum(per[k]["STRONG"] < 0.3 and not per[k]["succ"] for k in mf)]]
    out["b"]["morphfree_strong30_table"] = {"table[[strong&succ, strong&fail],[weak&succ, weak&fail]]": t,
                                            "fisher_p_greater": fisher_exact(t, alternative="greater")[1]}
    (HERE / "a5_summary.json").write_text(json.dumps(out, indent=1))
    for name, v in out["a"].items():
        print(name, "ALL", v["all"], "\n   BXK", v["bxk"])
        for t_ in v["timecourse"]:
            print("   ", t_)
    for k in sorted(per, key=lambda k: (not per[k]["succ"], k)):
        print(k, per[k])
    for lab in ("all", "morphfree", "FULL", "BANK"):
        print(lab, out["b"][lab])
    print(out["b"]["morphfree_strong30_table"])
