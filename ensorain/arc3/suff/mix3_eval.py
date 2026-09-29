"""T25: K-expert fixed-share over {split-CSSR, CSSR_EM, RAND_EM} (rate 1e-3) on the 24-world held-out family and on W2_3
(eval seeds 1..16), T = 4000. The script writes results/mix3_eval.json itself."""
import json, pathlib, sys, time, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff import worlds as W
from ensorain.arc3.suff.worlds_unifilar import random_unifilar
from ensorain.arc3.suff.cssr import CSSR
from ensorain.arc3.suff.cssr_em import CSSR_EM, RAND_EM

def lp(P, x): return -np.log2(np.clip(P[np.arange(len(x)), x], 1e-12, 1))

def fixed_share(Ps, x, share=1e-3):
    K = len(Ps); w = np.full(K, 1.0 / K); out = np.zeros_like(Ps[0])
    for t in range(len(x)):
        out[t] = sum(w[k] * Ps[k][t] for k in range(K))
        post = w * np.array([P[t, x[t]] for P in Ps]); post = post / max(post.sum(), 1e-300)
        w = (1 - share) * post + share / K
    return out

def run(x, B):
    kw = dict(Lmax=6, alpha=1e-3, refit=1000)
    Ps = {"split": CSSR(mode="split", **kw).run(x)[0], "cssr_em": CSSR_EM(n_iter=50, eps=0.01, **kw).run(x)[0],
          "rand_em": RAND_EM(n_iter=50, eps=0.01, **kw).run(x)[0]}
    Ps["mix2_fs"] = fixed_share([Ps["split"], Ps["cssr_em"]], x)
    Ps["mix3_fs"] = fixed_share([Ps["split"], Ps["cssr_em"], Ps["rand_em"]], x)
    return {k: float((lp(P, x) - B)[len(x) // 2:].mean()) for k, P in Ps.items()}

out = {"family": {}, "w2_3": {}}; t0 = time.time()
for S in (3, 4, 5):
    for ws in range(1, 9):
        w = random_unifilar(S, ws); x = w.sample(4000, np.random.default_rng(ws + 100)); B = lp(w.bayes(x), x)
        out["family"][w.name] = run(x, B)
for seed in range(1, 17):
    w = W.W2(3); x = w.sample(4000, np.random.default_rng(seed)); B = lp(w.bayes(x), x)
    out["w2_3"][seed] = run(x, B)
for g in ("family", "w2_3"):
    print(g, {k: round(float(np.mean([r[k] for r in out[g].values()])), 4) for k in next(iter(out[g].values()))}, flush=True)
print("%.0fs" % (time.time() - t0))
(pathlib.Path(__file__).parent / "results" / "mix3_eval.json").write_text(json.dumps(out, indent=1) + "\n")
