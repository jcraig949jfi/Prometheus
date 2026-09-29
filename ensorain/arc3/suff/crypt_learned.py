"""LM02 open question: can a LEARNED model estimate window crypticity without an answer key?
D6 = mean over 2nd-half positions of [-log2 p(x_t | last 6 symbols, model) + log2 p(x_t | full past, model)]
   = the model's estimate of the window-6 truncation cost (invariant to redundant/split states).
learned D6: model = the CSSR_EM fit (split-CSSR proposal + 50 EM iterations) on the whole T = 4000 stream.
true D6:    model = the known generating machine.
24 held-out unifilar worlds (same stream seeds as heldout_eval). The script writes results/crypt_learned.json itself."""
import json, pathlib, sys, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from ensorain.arc3.suff.worlds_unifilar import random_unifilar
from ensorain.arc3.suff.cssr import CSSR
from ensorain.arc3.suff.cssr_em import CSSR_EM
from ensorain.arc3.suff.hmm_learner import _em

def stationary(Tm):
    w, v = np.linalg.eig((Tm[0] + Tm[1]).T)
    s = np.abs(np.real(v[:, np.argmin(np.abs(w - 1))])); return s / s.sum()

def D6(Tm, x, L=6):
    st = stationary(Tm); b = st.copy(); full = np.zeros(len(x))
    for t, s in enumerate(x):
        pe = np.array([b @ Tm[0].sum(1), b @ Tm[1].sum(1)]); full[t] = pe[s] / pe.sum()
        b = b @ Tm[s]; b = b / max(b.sum(), 1e-300)
    h = len(x) // 2; win = []
    for t in range(h, len(x)):
        b = st.copy()
        for s in x[t - L:t]:
            b = b @ Tm[s]; b = b / max(b.sum(), 1e-300)
        pe = np.array([b @ Tm[0].sum(1), b @ Tm[1].sum(1)]); win.append(pe[x[t]] / pe.sum())
    return float(np.mean(-np.log2(np.clip(win, 1e-12, 1)) + np.log2(np.clip(full[h:], 1e-12, 1))))

if __name__ == "__main__":
    diag = json.loads((pathlib.Path(__file__).parent / "results" / "heldout_diag.json").read_text())
    out = {}
    for S in (3, 4, 5):
        for ws in range(1, 9):
            w = random_unifilar(S, ws); x = w.sample(4000, np.random.default_rng(ws + 100))
            ce = CSSR_EM(Lmax=6, alpha=1e-3, n_iter=50, eps=0.01)
            m = CSSR(Lmax=6, alpha=1e-3, mode="split").fit([int(v) for v in x])
            k, Tm = ce._init(m); Tm = _em(x, k, Tm, 50)[0]
            out[w.name] = dict(true_D6=D6([np.asarray(a) for a in w.Tm], x), learned_D6=D6(Tm, x), H6=diag[w.name]["H6"])
            print(w.name, {a: round(v, 4) for a, v in out[w.name].items()}, flush=True)
    from scipy.stats import spearmanr
    tr = [o["true_D6"] for o in out.values()]; le = [o["learned_D6"] for o in out.values()]; h6 = [o["H6"] for o in out.values()]
    print("C1 spearman(learned, true) = %.3f" % spearmanr(le, tr).correlation)
    print("C2 learned D6: U3_s7 %.4f  U4_s7 %.4f" % (out["U3_s7"]["learned_D6"], out["U4_s7"]["learned_D6"]))
    print("C3 spearman(true D6, H6) = %.3f" % spearmanr(tr, h6).correlation)
    (pathlib.Path(__file__).parent / "results" / "crypt_learned.json").write_text(json.dumps(out, indent=1) + "\n")
