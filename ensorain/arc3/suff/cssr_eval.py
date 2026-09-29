"""T25 CSSR evaluation on the frozen EVAL seeds 1..16 (debug used seeds 1001-1002 only). Writes results/cssr_eval.json."""
import json, pathlib, sys, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff import worlds as W
from ensorain.arc3.suff.cssr import CSSR

def nll(P, x): return -np.log2(np.clip(P[np.arange(len(x)), x], 1e-12, 1))
WORLDS = [("even", W.even_process), ("golden", W.golden_mean), ("w2_3", lambda: W.W2(3)),
          ("sns", W.simple_nonunifilar_source)]
out = {}
for mode in ("split", "vote"):
    for name, mk in WORLDS:
        rows = []
        for seed in range(1, 17):
            w = mk(); x = w.sample(4000, np.random.default_rng(seed)); B = w.bayes(x)
            m = CSSR(Lmax=6, alpha=1e-3, refit=500, mode=mode); P, info = m.run(x)
            h = len(x) // 2
            rows.append(dict(seed=seed, states=info["states"], excess2nd=float((nll(P, x) - nll(B, x))[h:].mean())))
        ex = [r["excess2nd"] for r in rows]; st = [r["states"] for r in rows]
        out[f"{mode}/{name}"] = dict(mean_excess2nd=float(np.mean(ex)), states=st, rows=rows)
        print(f"{mode:5s} {name:7s} mean_excess2nd={np.mean(ex):.4f} min={min(ex):.4f} max={max(ex):.4f} states={st}")
p = pathlib.Path(__file__).parent / "results" / "cssr_eval.json"
p.write_text(json.dumps(out, indent=1) + "\n")
