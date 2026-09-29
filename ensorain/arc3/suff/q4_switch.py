"""T25 reviewer Q4: is the 3-expert fixed-share gain SWITCHING or AVERAGING? Same experts as mix3_eval (T = 4000,
24-world family). The mixture uses share in {0 (Bayes mixture), 1e-4, 1e-3 (the reported MIX3_FS), 1e-2, 1 (static
uniform average)}. share = 1 resets the weights to uniform every step, so it is pure averaging with no adaptation.
The script writes results/q4_switch.json itself."""
import json, pathlib, sys, time, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff.worlds_unifilar import random_unifilar
from ensorain.arc3.suff.cssr import CSSR
from ensorain.arc3.suff.cssr_em import CSSR_EM, RAND_EM
from ensorain.arc3.suff.mix3_eval import fixed_share, lp

SHARES = [0.0, 1e-4, 1e-3, 1e-2, 1.0]
out = {}; t0 = time.time()
for S in (3, 4, 5):
    for ws in range(1, 9):
        w = random_unifilar(S, ws); x = w.sample(4000, np.random.default_rng(ws + 100)); B = lp(w.bayes(x), x)
        kw = dict(Lmax=6, alpha=1e-3, refit=1000)
        E = [CSSR(mode="split", **kw).run(x)[0], CSSR_EM(n_iter=50, eps=0.01, **kw).run(x)[0],
             RAND_EM(n_iter=50, eps=0.01, **kw).run(x)[0]]
        out[w.name] = {str(s): float((lp(fixed_share(E, x, s), x) - B)[2000:].mean()) for s in SHARES}
print({s: round(float(np.mean([r[str(s)] for r in out.values()])), 4) for s in SHARES}, "%.0fs" % (time.time() - t0))
(pathlib.Path(__file__).parent / "results" / "q4_switch.json").write_text(json.dumps(out, indent=1) + "\n")
