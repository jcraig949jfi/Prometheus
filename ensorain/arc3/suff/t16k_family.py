"""T25: the held-out family at T = 16000 (2nd-half excess) for one state count S (argv[1] in {3, 4, 5}).
Learners: STAT6, split-CSSR, CSSR_EM, RAND_EM, 3-expert fixed-share (rate 1e-3). Refit every 1000 (same as T = 4000).
Designed for the Fabric script executor. It writes t16k_S<S>.json to $FABRIC_OUT_DIR if set, else to results/."""
import json, os, pathlib, sys, time, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff.worlds_unifilar import random_unifilar
from ensorain.arc3.suff.learners import STAT
from ensorain.arc3.suff.cssr import CSSR
from ensorain.arc3.suff.cssr_em import CSSR_EM, RAND_EM
from ensorain.arc3.suff.mix3_eval import fixed_share, lp

S = int(sys.argv[1]); T = 16000; out = {}; t0 = time.time()
for ws in range(1, 9):
    w = random_unifilar(S, ws); x = w.sample(T, np.random.default_rng(ws + 100)); B = lp(w.bayes(x), x)
    kw = dict(Lmax=6, alpha=1e-3, refit=1000)
    Ps = {"stat6": STAT(6).run(x)[0], "split": CSSR(mode="split", **kw).run(x)[0],
          "cssr_em": CSSR_EM(n_iter=50, eps=0.01, **kw).run(x)[0], "rand_em": RAND_EM(n_iter=50, eps=0.01, **kw).run(x)[0]}
    Ps["mix3_fs"] = fixed_share([Ps["split"], Ps["cssr_em"], Ps["rand_em"]], x)
    out[w.name] = {k: float((lp(P, x) - B)[T // 2:].mean()) for k, P in Ps.items()}
    print(w.name, {k: round(v, 4) for k, v in out[w.name].items()}, "%.0fs" % (time.time() - t0), flush=True)
d = pathlib.Path(os.environ.get("FABRIC_OUT_DIR") or pathlib.Path(__file__).parent / "results")
(d / f"t16k_S{S}.json").write_text(json.dumps(out, indent=1) + "\n")
