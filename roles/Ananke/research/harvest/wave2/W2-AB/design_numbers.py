"""W2-AB: design arithmetic for the PTE-C2 draft (no engine, no torch). Prints every number the memo cites."""
import math, itertools, json
from scipy import stats as st

out = {}
# 1. replication-gate margins: keep = Phi(d/(sqrt2*f))
for f in (1.0, 1.12):
    for keep in (0.90, 0.95, 0.99):
        out[f"margin_f{f}_keep{keep}"] = round(st.norm.ppf(keep) * math.sqrt(2) * f, 3)

# 2. Clopper-Pearson 95% two-sided intervals for k/n search seeds
def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else st.beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else st.beta.ppf(1 - a / 2, k + 1, n - k)
    return round(lo, 3), round(hi, 3)
out["cp"] = {f"{k}/{n}": cp(k, n) for n in (4, 8, 12, 16) for k in (0, 1, 2, 4, n - 1, n)}

# 3. one-sided exact power: two independent arms of n seeds, Fisher one-sided alpha .05,
#    probability of rejecting when true rates are (p0, p1)
def fisher_power(n, p0, p1, alpha=0.05):
    pw = 0.0
    for a in range(n + 1):
        for b in range(n + 1):
            p = st.fisher_exact([[b, n - b], [a, n - a]], alternative="greater")[1]
            if p <= alpha:
                pw += st.binom.pmf(a, n, p0) * st.binom.pmf(b, n, p1)
    return round(pw, 3)
out["fisher_power"] = {f"n{n}_{p0}->{p1}": fisher_power(n, p0, p1)
                       for n in (8, 12, 16) for (p0, p1) in ((0.0, 0.5), (0.1, 0.5), (0.1, 0.6), (0.25, 0.75), (0.0, 0.3))}
# smallest b (successes in treated arm of n) that is significant against a = 0 in control
out["min_b_vs_0"] = {n: next(b for b in range(n + 1)
                             if st.fisher_exact([[b, n - b], [0, n]], alternative="greater")[1] <= 0.05)
                     for n in (4, 8, 12, 16)}

# 4. family-level rule: P(>=3 of 4 cells S-LOCATED) when per-cell P(S-LOCATED) = q
out["family_3of4"] = {q: round(sum(st.binom.pmf(k, 4, q) for k in (3, 4)), 3) for q in (0.2, 0.5, 0.8, 0.9)}

# 5. per-cell classification error at n = 8: P(BASE <= 1/8 | true rate r) and P(BASE >= 4/8 | r)
out["cell_rule_n8"] = {r: {"le1": round(st.binom.cdf(1, 8, r), 3), "ge4": round(1 - st.binom.cdf(3, 8, r), 3)}
                       for r in (0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7)}

# 6. selector-ceiling scaling (noise part ~ 1/sqrt(M)), anchored at the W2-D F7 observation .55-.58 @ M=8
out["selector_ceiling"] = {M: [round(0.5 + (c - 0.5) * math.sqrt(8 / M), 3) for c in (0.55, 0.58)] for M in (8, 16, 32)}

# 7. compute units (1 unit = one C1-scale search: pop 96, 36 gens, M 8, + held eval)
arms = {"BASE": (8, 1), "W0": (8, 1), "M32": (8, 4), "B4X": (8, 4), "PSEED": (4, 1), "KSEED": (12, 1), "STEP": (8, 1)}
full = sum(n * c for n, c in arms.values())
tier1 = sum(arms[a][0] * arms[a][1] for a in ("BASE", "W0", "M32", "PSEED", "KSEED"))
ctrl = 8 + 8 + 4
out["units"] = {"per_full_cell": full, "per_tier1_cell": tier1, "per_control_cell": ctrl}
for name, ncore, nxor, nctrl in (("core12", 12, 0, 4), ("core12+xor4", 12, 4, 4)):
    u_full = (ncore + nxor) * full + nctrl * ctrl
    u_t1 = (ncore + nxor) * tier1 + nctrl * ctrl
    out["units"][name] = {"full": u_full, "tier1": u_t1,
                          "gpu_h_full@37-60s": [round(u_full * s / 3600, 1) for s in (37, 60)],
                          "gpu_h_tier1@37-60s": [round(u_t1 * s / 3600, 1) for s in (37, 60)],
                          "cpu_core_h_full@20-80min": [round(u_full * m / 60) for m in (20, 80)]}
print(json.dumps(out, indent=1, default=str))
json.dump(out, open("design_numbers.json", "w"), indent=1, default=str)
