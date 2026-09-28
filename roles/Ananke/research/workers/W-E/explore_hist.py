"""Addendum B (post-hoc, exploratory): history-aware single-world decoder."""
import json, sys, pathlib, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ret_census as rc

def hist_decoder(X, H, Yk_perm, train, test):
    """X [F,W]; H [W,q0] other-cue columns (shared); Yk_perm [P,W] cue-k labels."""
    P = Yk_perm.shape[0]; F = X.shape[0]
    tr = np.zeros((F, P)); te = np.zeros((F, P))
    Htr = H[train]; W = len(train)
    for P0 in range(0, P, 4000):
        Yk = Yk_perm[P0:P0 + 4000]; p = len(Yk)
        D = np.concatenate([np.ones((p, W, 1)), Yk[:, train, None], np.broadcast_to(Htr, (p, *Htr.shape))], 2)
        A = np.einsum('pwi,pwj->pij', D, D) + 1e-6 * np.eye(D.shape[2])
        for f in range(F):
            b = np.linalg.solve(A, np.einsum('pwi,w->pi', D, X[f, train])[..., None])[..., 0]
            def pred(idx):
                r = X[f, idx][None] - b[:, :1] - (H[idx] @ b[:, 2:].T).T
                return np.sign(b[:, 1:2] * r)
            tr[f, P0:P0 + p] = rc._score(pred(train), Yk[:, train]).mean(-1)
            te[f, P0:P0 + p] = rc._score(pred(test), Yk[:, test]).mean(-1)
    sel = tr.argmax(0)
    return te[sel, np.arange(P)], sel

out = {}
for sp in rc.specimens() + rc.control_specs():
    t0 = time.time()
    tw = rc.twin_setup(sp["ph"], sp["env"])
    rec = rc.run_twins(sp, tw)
    c = tw["ylead"][:, rc.K].astype(np.int64)
    signs = rc.perm_signs(20000, rc.NS + 1)
    res = {}
    for j in rc.LAGS:
        names, X = rec["feat"][rc.K + j]
        others = [m for m in range(rc.K + j + 1) if m != rc.K]
        H = np.repeat(tw["ylead"][:, others].astype(float), 2, axis=0)        # [64, q0]
        Yk = np.stack([signs * c, -signs * c], 2).reshape(len(signs), -1).astype(float)
        A = np.zeros(len(signs)); sel0 = None
        for trp, tep in rc.FOLDS:
            a, sel = hist_decoder(X, H, Yk, rc.w_of(trp), rc.w_of(tep))
            A += a / 2; sel0 = sel0 if sel0 is not None else int(sel[0])
        res[j] = {"acc": float(A[0]), "p": float((1 + (A[1:] >= A[0]).sum()) / len(A)), "feature": names[sel0]}
    out[sp["name"]] = res
    print(sp["name"], {j: (round(v["acc"], 3), v["p"], v["feature"]) for j, v in res.items()}, round(time.time() - t0), flush=True)
(HERE / "out/explore_hist.json").write_text(json.dumps(out, indent=1))
