"""T25 Q2 ablation: CSSR_EM (EM initialized from the split-CSSR machine) vs RAND_EM (same S, 3 random restarts x 50
iterations). Eval seeds 1..16 on Even and W2_3, plus the 24-world held-out family. T = 4000. The script writes
results/q2_ablation.json itself."""
import json, pathlib, sys, time, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff import worlds as W
from ensorain.arc3.suff.worlds_unifilar import random_unifilar
from ensorain.arc3.suff.cssr_em import RAND_EM

def lp(P, x): return -np.log2(np.clip(P[np.arange(len(x)), x], 1e-12, 1))
ev = json.loads((pathlib.Path(__file__).parent / "results" / "heldout_eval.json").read_text())["family"]
emeval = json.loads((pathlib.Path(__file__).parent / "results" / "cssr_em_eval.json").read_text())
out = {"ladder": {}, "family": {}, "ref": {"cssr_em_ladder": {k: emeval[k]["em"] for k in ("even", "w2_3")}}}
t0 = time.time()
for name, mk in (("even", W.even_process), ("w2_3", lambda: W.W2(3))):
    r = []
    for seed in range(1, 17):
        w = mk(); x = w.sample(4000, np.random.default_rng(seed)); B = lp(w.bayes(x), x)
        P = RAND_EM(Lmax=6, alpha=1e-3, refit=1000, n_iter=50, eps=0.01).run(x)[0]
        r.append(float((lp(P, x) - B)[2000:].mean()))
    out["ladder"][name] = r
    print(name, "RAND_EM mean %.4f  CSSR_EM mean %.4f  (%.0fs)" % (np.mean(r), np.mean(emeval[name]["em"]), time.time() - t0), flush=True)
for S in (3, 4, 5):
    for ws in range(1, 9):
        w = random_unifilar(S, ws); x = w.sample(4000, np.random.default_rng(ws + 100)); B = lp(w.bayes(x), x)
        P = RAND_EM(Lmax=6, alpha=1e-3, refit=1000, n_iter=50, eps=0.01).run(x)[0]
        out["family"][w.name] = dict(rand_em=float((lp(P, x) - B)[2000:].mean()), cssr_em=ev[w.name]["em"])
fam = out["family"]
print("family RAND_EM mean %.4f  CSSR_EM mean %.4f  (%.0fs)" % (np.mean([v["rand_em"] for v in fam.values()]),
      np.mean([v["cssr_em"] for v in fam.values()]), time.time() - t0), flush=True)
(pathlib.Path(__file__).parent / "results" / "q2_ablation.json").write_text(json.dumps(out, indent=1) + "\n")
