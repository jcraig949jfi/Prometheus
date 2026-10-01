"""W2-9 add-on: exact null pass-probabilities (maximised over the nuisance base rate) and posterior P(H0 | CONFIRMED) for
the two knife-edge CONFIRMED verdicts (C-RUNAWAY, C-ABLATE SEARCH) and the knife-edge NOT_CONFIRMED C-SWAP-ACQUIRE.
Read-only; no campaign file is opened.   python -B fdr_marginal.py -> fdr_marginal.json"""
import json, math, pathlib
from scipy import stats
HERE = pathlib.Path(__file__).resolve().parent
out = {}
# C-RUNAWAY: pass iff X_NO>=7 (p<0.01 bar binds) and X_BASE==0, n=150 each; under H0 both ~ Bin(150, r)
best = max(((stats.binom(150, r).sf(6) * stats.binom(150, r).pmf(0)), r) for r in [i / 2000 for i in range(1, 400)])
out["C-RUNAWAY_null_pass_max_over_r"] = {"P": best[0], "r": best[1]}
for prior in (0.5, 0.2):
    for power in (0.05, 0.23, 0.56):
        a = best[0]
        out.setdefault("C-RUNAWAY_P(H0|confirm)", {})["prior_H1=%.1f_power=%.2f" % (prior, power)] = round(a * (1 - prior) / (a * (1 - prior) + power * prior), 4)
# C-ABLATE SEARCH: sign test 10/1 on discordant pairs, alpha attained
def sign_p(u, d):
    n = u + d
    return sum(math.comb(n, x) for x in range(u, n + 1)) / 2 ** n
out["C-ABLATE_SEARCH_attained_p"] = sign_p(10, 1)
for prior in (0.5, 0.2):
    a = 0.01
    out.setdefault("C-ABLATE_SEARCH_P(H0|confirm)_power0.98", {})["prior_H1=%.1f" % prior] = round(a * (1 - prior) / (a * (1 - prior) + 0.98 * prior), 4)
# C-SWAP-ACQUIRE: P(NOT_CONFIRMED) under true rates 3.75% (observed) with RANDOM 0
out["C-SWAP-ACQUIRE_P(GENOME>=10 | rate 9/240)"] = float(stats.binom(240, 9 / 240).sf(9))
(HERE / "fdr_marginal.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
