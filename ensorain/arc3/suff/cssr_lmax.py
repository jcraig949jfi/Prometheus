"""T25: split-CSSR vs Lmax and T on eval seeds 1..16. Writes results/cssr_lmax.json."""
import json, pathlib, sys, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff import worlds as W
from ensorain.arc3.suff.cssr import CSSR

def nll(P, x): return -np.log2(np.clip(P[np.arange(len(x)), x], 1e-12, 1))
WORLDS = [("even", W.even_process), ("golden", W.golden_mean), ("w2_3", lambda: W.W2(3))]
out = {}
for T in (4000, 16000):
    for name, mk in WORLDS:
        for L in (6, 8, 10):
            ex, st = [], []
            for seed in range(1, 17):
                w = mk(); x = w.sample(T, np.random.default_rng(seed)); B = w.bayes(x)
                P, info = CSSR(Lmax=L, alpha=1e-3, refit=1000, mode="split").run(x)
                ex.append(float((nll(P, x) - nll(B, x))[T // 2:].mean())); st.append(info["states"])
            out[f"T{T}/{name}/L{L}"] = dict(mean_excess2nd=float(np.mean(ex)), excess=ex, states=st)
            print(f"T={T:5d} {name:6s} L={L:2d} mean={np.mean(ex):.4f} min={min(ex):.4f} max={max(ex):.4f} states={st}", flush=True)
(pathlib.Path(__file__).parent / "results" / "cssr_lmax.json").write_text(json.dumps(out, indent=1) + "\n")
