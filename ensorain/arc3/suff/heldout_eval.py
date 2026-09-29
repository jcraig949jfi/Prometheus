"""T25 held-out evaluation: random unifilar machines (S in {3,4,5} x world seeds 1..8; stream seed = world seed + 100;
T = 4000), plus fixed-share on the Even eval seeds 1..16. Writes results/heldout_eval.json."""
import json, pathlib, sys, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff import worlds as W
from ensorain.arc3.suff.worlds_unifilar import random_unifilar
from ensorain.arc3.suff.learners import STAT
from ensorain.arc3.suff.cssr import CSSR
from ensorain.arc3.suff.cssr_em import CSSR_EM

def lp(P, x): return -np.log2(np.clip(P[np.arange(len(x)), x], 1e-12, 1))

def mix(Pa, Pb, x, share=0.0):
    """Two-expert Bayes mixture (share = 0) or fixed-share (Herbster-Warmuth) with switching rate `share`."""
    pa, pb = Pa[np.arange(len(x)), x], Pb[np.arange(len(x)), x]
    w = 0.5; out = np.zeros_like(Pa)
    for t in range(len(x)):
        out[t] = w * Pa[t] + (1 - w) * Pb[t]
        post = w * pa[t] / (w * pa[t] + (1 - w) * pb[t] + 1e-300)
        w = (1 - share) * post + share * 0.5
    return out

def learners(x):
    Ps = CSSR(Lmax=6, alpha=1e-3, refit=1000, mode="split").run(x)[0]
    Pe = CSSR_EM(Lmax=6, alpha=1e-3, refit=1000, n_iter=50, eps=0.01).run(x)[0]
    return {"stat3": STAT(3).run(x)[0], "stat6": STAT(6).run(x)[0], "split": Ps, "em": Pe,
            "mix": mix(Ps, Pe, x), "mix_fs": mix(Ps, Pe, x, share=1e-3)}

if __name__ == "__main__":
    out = {"family": {}, "even_fs": {}}
    for S in (3, 4, 5):
        for ws in range(1, 9):
            w = random_unifilar(S, ws); x = w.sample(4000, np.random.default_rng(ws + 100)); B = lp(w.bayes(x), x)
            r = {k: float((lp(P, x) - B)[2000:].mean()) for k, P in learners(x).items()}
            out["family"][w.name] = r
            print(w.name, " ".join(f"{k}={v:.4f}" for k, v in r.items()), flush=True)
    for seed in range(1, 17):
        w = W.even_process(); x = w.sample(4000, np.random.default_rng(seed)); B = lp(w.bayes(x), x)
        r = {k: float((lp(P, x) - B)[2000:].mean()) for k, P in learners(x).items() if k in ("mix", "mix_fs")}
        out["even_fs"][seed] = r
    fam = out["family"]
    print("FAMILY MEANS", {k: round(float(np.mean([r[k] for r in fam.values()])), 4) for k in next(iter(fam.values()))})
    print("EVEN", {k: (round(float(np.mean([r[k] for r in out['even_fs'].values()])), 4),
                       round(float(max(r[k] for r in out['even_fs'].values())), 4)) for k in ("mix", "mix_fs")})
    (pathlib.Path(__file__).parent / "results" / "heldout_eval.json").write_text(json.dumps(out, indent=1) + "\n")
