"""W2-N: are groups in one namespace independent? All W-Z groups use the SAME 512 world seeds (0x680), and
envs.build draws task geometry/cues from H_int(lead_seed, ENV, family, variant) -- shared across specimens of a
family/variant. Test: correlation across groups of the per-pair normal accuracy a_i (pair index = world seed).
Under independence the mean cross-group correlation is 0 (+- 1/sqrt(P) per pair of groups)."""
import collections, csv, itertools, json, math
import numpy as np
import n_decomp as N

arms = N.load_arms()
gt = {r["gid"]: r for r in csv.DictReader(open(N.WK / "W-Z" / "out" / "group_table.csv"))}
A = {}
for (g, arm), x in arms.items():
    if g in A:
        continue
    A[g] = (x["a"], x["ok"])
fam = {g: gt[g]["family"] for g in A}
spec = {g: gt[g]["specimen"] for g in A}
res = collections.defaultdict(list)
for g1, g2 in itertools.combinations(sorted(A), 2):
    a1, o1 = A[g1]; a2, o2 = A[g2]
    ok = o1 & o2
    if ok.sum() < 64 or a1[ok].std() == 0 or a2[ok].std() == 0:
        continue
    r = float(np.corrcoef(a1[ok], a2[ok])[0, 1])
    same_f = fam[g1] == fam[g2]
    same_s = spec[g1] == spec[g2]
    key = "same_specimen" if same_s else ("same_family" if same_f else "diff_family")
    res[key].append(r)
out = {}
for k, v in res.items():
    v = np.array(v)
    out[k] = {"n_pairs": len(v), "mean_r": round(float(v.mean()), 4), "median_r": round(float(np.median(v)), 4),
              "frac_r_gt_0.2": round(float(np.mean(v > 0.2)), 3)}
# design effect for a population mean over G groups: var factor 1 + (G-1) rbar
print(json.dumps(out, indent=1))
# by family: mean a per pair index averaged over groups of a family -> variance vs independent expectation
for f in sorted(set(fam.values())):
    gs = [g for g in A if fam[g] == f and A[g][1].all()]
    if len(gs) < 3: continue
    Z = np.stack([(A[g][0] - A[g][0].mean()) / A[g][0].std(ddof=1) for g in gs])
    m = Z.mean(0)
    print(f, "groups", len(gs), "var(mean of standardized a over groups) =", round(float(m.var(ddof=1)), 4),
          "independent expectation", round(1 / len(gs), 4))
    out[f"var_ratio_{f}"] = {"groups": len(gs), "ratio": round(float(m.var(ddof=1) * len(gs)), 2)}
json.dump(out, open(N.OUT / "xcorr.json", "w"), indent=1)
