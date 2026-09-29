"""Circularity check for learned crypticity (CRYPT_LEARNED.md). Two estimators outside the CSSR_EM family:
(a) D6 from a fixed-S = 8 HMM fitted by EM from 3 random restarts x 50 iterations (no CSSR proposal);
(b) D_seq = 2nd-half log-loss(STAT6) - min over k in {8, 10, 12} of log-loss(STAT_k): model-free, prequential. It is
    confounded by estimation cost, which is why its prediction below is weaker.
Same 24 worlds and streams (T = 4000). The script writes results/crypt_crossfamily.json itself."""
import json, pathlib, sys, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff.worlds_unifilar import random_unifilar
from ensorain.arc3.suff.learners import STAT
from ensorain.arc3.suff.hmm_learner import _em, _normalize_rows
from ensorain.arc3.suff.crypt_learned import D6

def lp(P, x): return -np.log2(np.clip(P[np.arange(len(x)), x], 1e-12, 1))

if __name__ == "__main__":
    cl = json.loads((pathlib.Path(__file__).parent / "results" / "crypt_learned.json").read_text())
    t16 = {}
    for S in (3, 4, 5):
        t16.update(json.loads((pathlib.Path(__file__).parent / "results" / "fabric_t16k" / f"t16k_S{S}.json").read_text()))
    out = {}
    for S in (3, 4, 5):
        for ws in range(1, 9):
            w = random_unifilar(S, ws); x = w.sample(4000, np.random.default_rng(ws + 100)); h = len(x) // 2
            rng = np.random.default_rng(777); best = None
            for _ in range(3):
                cand = _em(x, 8, _normalize_rows([rng.random((8, 8)), rng.random((8, 8))]), 50)
                if best is None or cand[1] > best[1]: best = cand
            d_hmm = D6(best[0], x)
            L = {k: float(lp(STAT(k).run(x)[0], x)[h:].mean()) for k in (6, 8, 10, 12)}
            d_seq = L[6] - min(L[8], L[10], L[12])
            out[w.name] = dict(true_D6=cl[w.name]["true_D6"], hmm8_D6=d_hmm, seq_D=d_seq, gap16=t16[w.name]["stat6"] - t16[w.name]["mix3_fs"])
            print(w.name, {a: round(v, 4) for a, v in out[w.name].items()}, flush=True)
    from scipy.stats import spearmanr
    col = lambda k: [o[k] for o in out.values()]
    print("X1 spearman(hmm8 D6, true D6) = %.3f" % spearmanr(col("hmm8_D6"), col("true_D6")).correlation)
    print("X2 spearman(seq D, gap16)     = %.3f" % spearmanr(col("seq_D"), col("gap16")).correlation)
    print("X3 spearman(hmm8 D6, gap16)   = %.3f" % spearmanr(col("hmm8_D6"), col("gap16")).correlation)
    (pathlib.Path(__file__).parent / "results" / "crypt_crossfamily.json").write_text(json.dumps(out, indent=1) + "\n")
