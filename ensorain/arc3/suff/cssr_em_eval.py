"""T25: split-CSSR vs CSSR_EM (n_iter 50) vs their prequential Bayes mixture, on eval seeds 1..16, T = 4000.
Writes results/cssr_em_eval.json."""
import json, pathlib, sys, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff import worlds as W
from ensorain.arc3.suff.cssr import CSSR
from ensorain.arc3.suff.cssr_em import CSSR_EM

def lp(P, x): return -np.log2(np.clip(P[np.arange(len(x)), x], 1e-12, 1))

def mix(Pa, Pb, x):
    """Bayes mixture, prior 1/2 each: weights proportional to 2^-(cumulative log-loss before t)."""
    la, lb = lp(Pa, x), lp(Pb, x)
    ca = np.concatenate([[0], np.cumsum(la)[:-1]]); cb = np.concatenate([[0], np.cumsum(lb)[:-1]])
    d = np.clip(ca - cb, -500, 500)
    wa = 1 / (1 + 2.0 ** d)          # weight of a = 2^-ca / (2^-ca + 2^-cb)
    return wa[:, None] * Pa + (1 - wa)[:, None] * Pb

WORLDS = [("even", W.even_process), ("golden", W.golden_mean), ("w2_3", lambda: W.W2(3)),
          ("sns", W.simple_nonunifilar_source)]
out = {}
for name, mk in WORLDS:
    res = {"split": [], "em": [], "mix": []}
    for seed in range(1, 17):
        w = mk(); x = w.sample(4000, np.random.default_rng(seed)); B = lp(w.bayes(x), x)
        Ps = CSSR(Lmax=6, alpha=1e-3, refit=1000, mode="split").run(x)[0]
        Pe = CSSR_EM(Lmax=6, alpha=1e-3, refit=1000, n_iter=50, eps=0.01).run(x)[0]
        for k, P in (("split", Ps), ("em", Pe), ("mix", mix(Ps, Pe, x))):
            res[k].append(float((lp(P, x) - B)[2000:].mean()))
    out[name] = res
    print(name, " ".join(f"{k}={np.mean(v):.4f}[{min(v):.4f},{max(v):.4f}]" for k, v in res.items()), flush=True)
(pathlib.Path(__file__).parent / "results" / "cssr_em_eval.json").write_text(json.dumps(out, indent=1) + "\n")
