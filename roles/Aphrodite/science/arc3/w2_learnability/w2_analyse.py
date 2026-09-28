"""W2 stage 4: joins stages 1-3 and writes w2_summary.json (no engine calls)."""
import json, math, glob
from collections import Counter, defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
N_COV, NG5, NF = 151920, 465954, 180
FB0 = N_COV + NF
BLOCK = NG5 * NF
ESCROW = 250_000

cov = {r["name"]: r for r in json.load(open(HERE / "w2_coverage_ALL.json"))}
fb = {r["name"]: r for r in json.load(open(HERE / "w2_fallback_ALL.json"))}
e16 = {}
for p in glob.glob(str(HERE / "w2_escrow16_NAT_s*.jsonl")):
    for l in open(p):
        r = json.loads(l); e16[r["name"]] = r


def grp(r):
    return "NAT" if r["source"] == "NAT" else "CON"


def first_equiv(name, k):
    c = cov[name]["cells"][k]
    if c["first_equiv_charge"] is not None:
        return c["first_equiv_charge"]
    return fb[name]["cells"][k]["fallback_equiv_charge"]


S = {}
for g in ("NAT", "CON"):
    names = [n for n in cov if grp(cov[n]) == g]
    tab = Counter((cov[n]["k_cov"] > 0, cov[n]["p_PRISTINE"]) for n in names)
    S[g] = {"n": len(names), "in_cov_vs_p": {"%s|%s" % k: v for k, v in sorted(tab.items())}}
    # charge distribution (analytic first-equivalent charge; per cell)
    ch = [first_equiv(n, k) for n in names for k in range(4)]
    bins = Counter(int(math.floor(math.log10(c))) for c in ch)
    S[g]["log10_first_equiv_charge_hist"] = dict(sorted(bins.items()))
    S[g]["cells_in_cov"] = sum(c <= N_COV for c in ch)
    S[g]["cells_leq_escrow"] = sum(c <= ESCROW for c in ch)
    S[g]["cells_in_first_init_block"] = sum(FB0 < c <= FB0 + BLOCK for c in ch)
    S[g]["cells_beyond_first_block"] = sum(c > FB0 + BLOCK for c in ch)
    # solve curve vs escrow (analytic, equivalence lower bound)
    grid = [1e3, 1e4, 3e4, 1e5, 151920, 2.5e5, 1e6, 4e6, 1e7, 3e7, 8.4e7, 1e8, 1e9, 1e10]
    S[g]["analytic_solve_curve"] = {"%g" % E: round(sum(c <= E for c in ch) / len(ch), 3) for E in grid}
    # escrow16 empirical (NAT only)
    if g == "NAT" and e16:
        cells = [(n, k, c) for n in names if n in e16 for k, c in enumerate(e16[n]["cells"])]
        emp = {}
        for E in [5e4, 1e5, 151920, 2.5e5, 5e5, 1e6, 2e6, 4e6]:
            emp["%g" % E] = round(sum(c["T4"] and c["charge"] <= E for _, _, c in cells) / len(cells), 3)
        S[g]["empirical_T4_solve_curve"] = emp
        S[g]["empirical_n_cells"] = len(cells)
        fbh = [c for _, _, c in cells if c["segment"] == "fallback"]
        S[g]["fallback_first_hits"] = len(fbh)
        S[g]["fallback_first_hits_T4"] = sum(c["T4"] for c in fbh)
        S[g]["expr_first_hits"] = sum(c["segment"] == "expr" for _, _, c in cells)
        # per family p at escrow E (4 cells) -> window fraction
        fam = defaultdict(list)
        for n, k, c in cells:
            fam[n].append(c)
        pw = {}
        for E in [2e4, 5e4, 1e5, 2.5e5, 1e6, 4e6]:
            ps = [sum(c["T4"] and c["charge"] <= E for c in cs) / 4 for cs in fam.values()]
            pw["%g" % E] = {"p0": sum(p == 0 for p in ps), "window": sum(0 < p < 1 for p in ps), "p1": sum(p == 1 for p in ps)}
        S[g]["p_distribution_vs_escrow"] = pw
        # out-of-coverage families only: p at 4M
        oc = [n for n in fam if cov[n]["k_cov"] == 0]
        S[g]["outcov_p_at_4M"] = dict(Counter(sum(c["T4"] for c in fam[n]) / 4 for n in oc))
        # predictors of the fallback first-hit charge (out of coverage)
        rows = []
        for n in oc:
            f = fb[n]
            first_T4 = [c["charge"] for c in fam[n] if c["T4"]]
            rows.append({"name": n, "k_body_G5": f["k_body_G5"], "k_final": f["k_final"], "k_init": f["k_init"],
                         "foreign": cov[n]["foreign_atoms"], "depth": cov[n]["depth"],
                         "dep_first": cov[n]["dep_first"], "dep_query": cov[n]["dep_query"],
                         "p4M": len(first_T4) / 4, "Q2": cov[n]["Q2_size"],
                         "analytic_min": min(first_equiv(n, k) for k in range(4))})
        S[g]["outcov_rows"] = rows

# features vs coverage (all T4 rows)
feat = defaultdict(Counter)
for n, r in cov.items():
    ic = r["k_cov"] > 0
    feat["foreign_atoms=" + (",".join(r["foreign_atoms"]) or "none")][ic] += 1
    feat["depth=%d" % r["depth"]][ic] += 1
    feat["dep_first=%s" % r["dep_first"]][ic] += 1
    feat["dep_query=%s" % r["dep_query"]][ic] += 1
    feat["dep_first_or_query=%s" % (r["dep_first"] or r["dep_query"])][ic] += 1
    feat["Q2=%s" % r["Q2_size"]][ic] += 1
    feat["final_has_first_or_last=%s" % any(a in r["final"] for a in ("first", "last"))][ic] += 1
S["features_vs_in_cov"] = {k: {"in": v[True], "out": v[False]} for k, v in sorted(feat.items())}

# within coverage: multiplicity m (distinct (init,body) pairs) vs first-equivalent charge
mm = defaultdict(list)
for n, r in cov.items():
    if r["k_cov"] > 0:
        for c in r["cells"]:
            mm[r["m_cov_pairs"]].append(c["first_equiv_charge"])
S["in_cov_multiplicity"] = {str(m): {"cells": len(v), "mean_charge": round(sum(v) / len(v)),
                                     "pred_N_over_m_plus_1": round(N_COV / (m + 1))} for m, v in sorted(mm.items())}
# fallback: class size vs analytic first-equiv charge
kk = defaultdict(list)
for n, r in fb.items():
    if cov[n]["k_cov"] == 0:
        kb = r["k_body_G5"]
        b = 0 if kb == 0 else int(math.floor(math.log2(kb)))
        for c in r["cells"]:
            kk[b].append(c["r_body"])
S["outcov_log2_kbodyG5_vs_mean_body_rank"] = {str(b): {"cells": len(v), "mean_r_body": round(sum(v) / len(v)),
                                                          "pred_NG5_over_k": round(NG5 / (2 ** b + 1))}
                                              for b, v in sorted(kk.items())}
(HERE / "w2_summary.json").write_text(json.dumps(S, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in S.items() if k not in ("features_vs_in_cov",)}, indent=1)[:6000])

# ---- calibration: analytic first-equivalent charge (per cell) vs empirical first T4 hit (NAT, 4M)
cal = Counter()
fam_pts = []
for n, r in e16.items():
    a_s = []
    for k, c in enumerate(r["cells"]):
        a = first_equiv(n, k)
        cal[(a <= 4e6, bool(c["T4"]))] += 1
        a_s.append(a)
    fam_pts.append((sum(math.log10(x) for x in a_s) / 4, sum(c["T4"] for c in r["cells"]) / 4, cov[n]["k_cov"] > 0))
S["calibration_cells_analytic_leq4M_vs_empirical_T4"] = {"%s|%s" % k: v for k, v in sorted(cal.items())}
# difficulty index D = mean log10 analytic charge; p at 4M by D bin
db = defaultdict(list)
for d, p, ic in fam_pts:
    db[round(d * 2) / 2].append(p)
S["p4M_by_difficulty_index_D"] = {str(k): {"families": len(v), "mean_p4M": round(sum(v) / len(v), 3)} for k, v in sorted(db.items())}


def spearman(x, y):
    def rk(a):
        o = sorted(range(len(a)), key=lambda i: a[i]); r = [0] * len(a)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and a[o[j + 1]] == a[o[i]]:
                j += 1
            for t in range(i, j + 1):
                r[o[t]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rk(x), rk(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den
oc = [(d, p) for d, p, ic in fam_pts if not ic]
S["spearman_D_vs_p4M_outcov"] = round(spearman([d for d, p in oc], [p for d, p in oc]), 3) if len(oc) > 3 else None
S["spearman_D_vs_p4M_all"] = round(spearman([d for d, p, ic in fam_pts], [p for d, p, ic in fam_pts]), 3)
(HERE / "w2_summary.json").write_text(json.dumps(S, indent=1), encoding="utf-8")
print({k: S[k] for k in ("calibration_cells_analytic_leq4M_vs_empirical_T4", "p4M_by_difficulty_index_D", "spearman_D_vs_p4M_outcov", "spearman_D_vs_p4M_all")})

# ---- is syntactic 'distance from coverage' a difficulty variable? (all 283 T4 rows, out of coverage)
oc_all = [n for n in cov if cov[n]["k_cov"] == 0]
Dn = {n: sum(math.log10(first_equiv(n, k)) for k in range(4)) / 4 for n in cov}
nf = [len(cov[n]["foreign_atoms"]) for n in oc_all]
dp = [cov[n]["depth"] for n in oc_all]
kc = [math.log10(max(1, fb[n]["k_body_G5"] * fb[n]["k_final"])) for n in oc_all]
S["outcov_all_spearman"] = {"n": len(oc_all),
                            "n_foreign_atoms_vs_D": round(spearman(nf, [Dn[n] for n in oc_all]), 3),
                            "paren_depth_vs_D": round(spearman(dp, [Dn[n] for n in oc_all]), 3),
                            "log_class_size_vs_D": round(spearman(kc, [Dn[n] for n in oc_all]), 3),
                            "k_init_vs_D": round(spearman([fb[n]["k_init"] for n in oc_all], [Dn[n] for n in oc_all]), 3)}
Dh = Counter(round(Dn[n] * 2) / 2 for n in cov)
S["family_D_hist_all283"] = {str(k): v for k, v in sorted(Dh.items())}
(HERE / "w2_summary.json").write_text(json.dumps(S, indent=1), encoding="utf-8")
print(S["outcov_all_spearman"], S["family_D_hist_all283"])

# ---- closed-form model: P(solve by escrow E) from class multiplicities (no search run)
#   in coverage : 1 (E >= N_COV); else fraction of cells from exact ranks
#   beyond      : (k_init/116) * (1 - (1 - (E - FB0)/(NF*NG5))**k_body)   [first init block only]
def p_model(n, E):
    if cov[n]["k_cov"] > 0:
        return 1.0 if E >= N_COV else None
    f = fb[n]
    if E <= FB0:
        return 0.0
    x = min(1.0, (E - FB0) / (NF * NG5))
    return (f["k_init"] / 116) * (1 - (1 - x) ** f["k_body_G5"])

KAP = {}
for n in e16:
    if cov[n]["k_cov"] == 0:
        pm = p_model(n, 4e6)
        pe = sum(c["T4"] for c in e16[n]["cells"]) / 4
        KAP[n] = (pm, pe)
bins = defaultdict(list)
for n, (pm, pe) in KAP.items():
    b = "<0.02" if pm < 0.02 else "0.02-0.05" if pm < 0.05 else "0.05-0.10" if pm < 0.10 else "0.10-0.20" if pm < 0.2 else ">=0.20"
    bins[b].append((pm, pe))
S["closed_form_model_4M_outcov_NAT"] = {b: {"families": len(v), "mean_pred": round(sum(x for x, _ in v) / len(v), 3),
                                              "mean_emp": round(sum(y for _, y in v) / len(v), 3)} for b, v in bins.items()}
S["closed_form_model_4M_total"] = {"families": len(KAP), "sum_pred": round(sum(x for x, _ in KAP.values()), 2),
                                   "sum_emp": round(sum(y for _, y in KAP.values()), 2),
                                   "spearman": round(spearman([x for x, _ in KAP.values()], [y for _, y in KAP.values()]), 3)}
(HERE / "w2_summary.json").write_text(json.dumps(S, indent=1), encoding="utf-8")
print(S["closed_form_model_4M_outcov_NAT"], S["closed_form_model_4M_total"])
