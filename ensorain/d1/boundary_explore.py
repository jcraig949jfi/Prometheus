"""EXPLORATORY (not preregistered; nominates for Round 3 only): is the
DIVERGED / not-diverged split -- the dominant structure in Round 1 --
predicted better with dial couplings than with main effects? Same
discovery/validation split as analyze.py. Diverged := held-out R^2 <= -1
before clipping (the memory predicts worse than zero by more than the
field's own variance)."""
import itertools
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from .analyze import load, col, CONT, CAT

rows = load("ensorain/runs/d1_round1.jsonl")
disc = [r for r in rows if r["life"] % 2 == 0]
val = [r for r in rows if r["life"] % 2 == 1]


def X(rs, inter, ref):
    cols, names = [], []
    for k in CONT:
        x, xr = col(rs, k), col(ref, k)
        cols.append((x - xr.mean()) / (xr.std() + 1e-12)); names.append(k)
    for k in CAT:
        x = col(rs, k)
        for v in sorted(set(col(ref, k)))[1:]:
            cols.append((x == v).astype(float)); names.append(f"{k}={v}")
    B = np.column_stack(cols)
    if inter:
        pairs = list(itertools.combinations(range(B.shape[1]), 2))
        B = np.column_stack([B] + [B[:, i] * B[:, j] for i, j in pairs])
        names += [f"{names[i]}*{names[j]}" for i, j in pairs]
    return B, names


y = lambda rs: np.array([r["r2_ho"] <= -1.0 for r in rs])
out = dict(frac_diverged=float(np.mean(y(rows))))
for C in (0.1, 1.0):
    for inter in (False, True):
        Xd, names = X(disc, inter, disc)
        Xv, _ = X(val, inter, disc)
        m = LogisticRegression(C=C, max_iter=10000).fit(Xd, y(disc))
        p = m.predict_proba(Xv)[:, 1]
        out[f"C{C}_{'coupled' if inter else 'main'}"] = dict(logloss=float(log_loss(y(val), p)), auc=float(roc_auc_score(y(val), p)))
        if inter and C == 0.1:
            coef = m.coef_[0]
            top = np.argsort(-np.abs(coef))[:15]
            out["top_terms_coupled_C0.1"] = [(names[i], round(float(coef[i]), 3)) for i in top]
        if not inter and C == 0.1:
            coef = m.coef_[0]
            top = np.argsort(-np.abs(coef))[:10]
            out["top_terms_main_C0.1"] = [(names[i], round(float(coef[i]), 3)) for i in top]
json.dump(out, open("ensorain/runs/d1_boundary_explore.json", "w"), indent=1)
print(json.dumps(out, indent=1))
