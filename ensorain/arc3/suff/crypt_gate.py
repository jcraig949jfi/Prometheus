"""Model-quality gate for learned crypticity (LM02 design rule). Fit on the FIRST half (T = 4000 streams), evaluate on
the second half. A learned D6 is admissible iff the model's 2nd-half full-past log-loss < STAT6's 2nd-half prequential
log-loss; otherwise D6 is UNKNOWN. Estimators: HMM8 (3 random restarts x 50 EM; the precommitted subject) and CSSR_EM
(exploratory comparison). Silent failure := true D6 > .02 and learned D6 < true D6 / 3. The script writes
results/crypt_gate.json itself."""
import json, pathlib, sys, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff.worlds_unifilar import random_unifilar
from ensorain.arc3.suff.learners import STAT
from ensorain.arc3.suff.cssr import CSSR
from ensorain.arc3.suff.cssr_em import CSSR_EM
from ensorain.arc3.suff.hmm_learner import _em, _normalize_rows
from ensorain.arc3.suff.crypt_learned import D6, stationary

def lp(P, x): return -np.log2(np.clip(P[np.arange(len(x)), x], 1e-12, 1))

def model_loss2(Tm, x):
    b = stationary(Tm); h = len(x) // 2; out = []
    for t, s in enumerate(x):
        pe = np.array([b @ Tm[0].sum(1), b @ Tm[1].sum(1)])
        if t >= h: out.append(-np.log2(max(pe[s] / pe.sum(), 1e-12)))
        b = b @ Tm[s]; b = b / max(b.sum(), 1e-300)
    return float(np.mean(out))

if __name__ == "__main__":
    cl = json.loads((pathlib.Path(__file__).parent / "results" / "crypt_learned.json").read_text())
    out = {}
    for S in (3, 4, 5):
        for ws in range(1, 9):
            w = random_unifilar(S, ws); x = w.sample(4000, np.random.default_rng(ws + 100)); h = len(x) // 2; x1 = x[:h]
            stat6 = float(lp(STAT(6).run(x)[0], x)[h:].mean())
            rng = np.random.default_rng(777); best = None
            for _ in range(3):
                c = _em(x1, 8, _normalize_rows([rng.random((8, 8)), rng.random((8, 8))]), 50)
                if best is None or c[1] > best[1]: best = c
            m = CSSR(Lmax=6, alpha=1e-3, mode="split").fit([int(v) for v in x1]); k, T0 = CSSR_EM(n_iter=50, eps=0.01)._init(m)
            ce = _em(x1, k, T0, 50)[0]
            r = dict(true_D6=cl[w.name]["true_D6"], stat6_loss2=stat6)
            for name, Tm in (("hmm8", best[0]), ("cssr_em", ce)):
                r[name + "_D6"] = D6(Tm, x); r[name + "_loss2"] = model_loss2(Tm, x); r[name + "_pass"] = r[name + "_loss2"] < stat6
            out[w.name] = r
            print(w.name, {a: (round(v, 4) if isinstance(v, float) else v) for a, v in r.items()}, flush=True)
    from scipy.stats import spearmanr
    for name in ("hmm8", "cssr_em"):
        silent = [n for n, r in out.items() if r["true_D6"] > .02 and r[name + "_D6"] < r["true_D6"] / 3]
        caught = [n for n in silent if not out[n][name + "_pass"]]
        passed = [n for n, r in out.items() if r[name + "_pass"]]
        rho = spearmanr([out[n][name + "_D6"] for n in passed], [out[n]["true_D6"] for n in passed]).correlation if len(passed) > 2 else float("nan")
        print(f"{name}: silent failures {silent}; caught by gate {len(caught)}/{len(silent)}; pass {len(passed)}/24; gated spearman {rho:.3f}")
    (pathlib.Path(__file__).parent / "results" / "crypt_gate.json").write_text(json.dumps(out, indent=1) + "\n")
