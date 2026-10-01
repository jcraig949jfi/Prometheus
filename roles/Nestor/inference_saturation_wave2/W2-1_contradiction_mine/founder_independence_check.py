"""W2-1 check J: are 7ae3 single-founder (k=1, splice off, BASE) depth>=5 rates homogeneous across batches, and is k=4
superadditive against the pooled p1? Also: the depth-gap (22-161) census including arms the 630-run pool omitted.
Read-only over c9x RESULTS.json files (same pool as dossier A s6.1 plus X-ATOMIC / C-ATOMIC BASE arms)."""
import json, pathlib, math, glob
C = pathlib.Path(__file__).resolve().parents[2] / "campaigns/c9x-explore-2026-09-24"
def rows(f): 
    d = json.loads((C / f).read_text()); return d if isinstance(d, list) else next(v for v in d.values() if isinstance(v, list))
k1 = {
 "c_runaway_confirm NO_RECOMB": [r["depth"] for r in rows("c_runaway_confirm/RESULTS.json") if r["arm"] == "NO_RECOMB"],
 "x_h2_norecomb NO_RECOMB": [r["depth"] for r in rows("x_h2_norecomb/RESULTS.json") if r["arm"] == "NO_RECOMB"],
 "x_critical_mass k1": [r["depth"] for r in rows("x_critical_mass/RESULTS.json") if r["k"] == 1],
 "c_critical_mass k1": [r["depth"] for r in rows("c_critical_mass/RESULTS.json") if r["k"] == 1],
 "x_dose_curve k1": [r["depth"] for r in rows("x_dose_curve/RESULTS.json") if r["k"] == 1],
 "x_ticket": [json.loads(pathlib.Path(p).read_text())["depth"] for p in sorted(glob.glob(str(C / "x_ticket/results/*.json")))],
 "x_decay f1.0": [r["depth"] for r in rows("x_decay/RESULTS.json") if r["f"] == 1.0],
 "x_sterile g1.0": [r["depth"] for r in rows("x_sterile/RESULTS.json") if r["g"] == 1.0],
}
N = sum(len(v) for v in k1.values()); X = sum(sum(d >= 5 for d in v) for v in k1.values()); p = X / N
chi = 0.0
for name, v in k1.items():
    n, x = len(v), sum(d >= 5 for d in v); e = n * p
    chi += (x - e) ** 2 / (e * (1 - p)); print("%-28s n=%3d d>=5=%3d (%.3f) d>=20=%2d gap22-161=%s" % (name, n, x, x / n, sum(d >= 20 for d in v), [d for d in v if 22 <= d <= 161]))
df = len(k1) - 1
# chi-square survival via regularized gamma (series)
def chi2_sf(x, k):
    a = k / 2.0; x2 = x / 2.0; s = term = 1.0 / a; n = 1
    while term > 1e-12: term *= x2 / (a + n); s += term; n += 1
    return 1 - math.exp(-x2 + a * math.log(x2) - math.lgamma(a)) * s
print("pooled k=1: n=%d d>=5=%d p1=%.4f ; heterogeneity chi2=%.2f df=%d p=%.3f" % (N, X, p, chi, df, chi2_sf(chi, df)))
def binom_sf(x, n, q): return sum(math.comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(x, n + 1))
for f, sel in (("x_dose_curve/RESULTS.json", "k"), ("c_critical_mass/RESULTS.json", "k"), ("x_critical_mass/RESULTS.json", "k")):
    for k in (2, 4, 8):
        v = [r["depth"] for r in rows(f) if r[sel] == k]
        if not v: continue
        q = 1 - (1 - p) ** k; x = sum(d >= 5 for d in v)
        print("  %s k=%d: d>=5 %d/%d vs indep(pooled p1) %.1f, upper-tail p=%.4g" % (f.split('/')[0], k, x, len(v), q * len(v), binom_sf(x, len(v), q)))
# omitted BASE arms
for f in ("x_atomic/RESULTS.json", "c_atomic/RESULTS.json"):
    v = [r["depth"] for r in rows(f) if r.get("arm") == "BASE"]
    print("omitted %s BASE: n=%d d>=20=%d gap22-161=%s max=%d" % (f.split('/')[0], len(v), sum(d >= 20 for d in v), [d for d in v if 22 <= d <= 161], max(v)))
