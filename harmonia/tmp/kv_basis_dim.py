"""Phase 2 — effective dimensionality of the KillVector basis.

On the native pilot's 24k per-record kill_vectors, ask: is the 12-component
basis genuinely multi-dimensional, or rank-1-but-continuous? Pearson
correlation is unit-free, so we can correlate raw margins across components
directly. Headline metrics: how many components are 'alive' (non-constant),
the top-eigenvalue fraction of the correlation matrix, and the participation
ratio (effective dimensionality).
"""
import json, math
import numpy as np

P = r"D:\Prometheus\prometheus_math\_native_kill_vector_pilot.json"
with open(P, "r", encoding="utf-8") as f:
    d = json.load(f)
eps = d["pilot"]["episodes"]
print(f"n_episodes = {len(eps)}")

# Inspect one kill_vector
kv0 = eps[0]["kill_vector"]
print("kill_vector top keys:", list(kv0.keys()) if isinstance(kv0, dict) else type(kv0))
comps0 = kv0["components"] if isinstance(kv0, dict) and "components" in kv0 else kv0
print("component[0]:", json.dumps(comps0[0], default=str)[:300])

CANON = ["out_of_band","reciprocity","irreducibility",
         "catalog:Mossinghoff","catalog:lehmer_literature","catalog:LMFDB",
         "catalog:OEIS","catalog:arXiv","F1_permutation_null","F6_base_rate",
         "F9_simpler_explanation","F11_cross_validation"]
idx = {c: i for i, c in enumerate(CANON)}

def comp_name(c):
    return c.get("falsifier_name") or c.get("name") or c.get("falsifier") or ""

n = len(eps)
X = np.full((n, len(CANON)), np.nan)        # raw margins
T = np.zeros((n, len(CANON)))               # triggered 0/1
for r, e in enumerate(eps):
    kv = e["kill_vector"]
    comps = kv["components"] if isinstance(kv, dict) and "components" in kv else kv
    for c in comps:
        nm = comp_name(c)
        if nm not in idx:
            continue
        j = idx[nm]
        T[r, j] = 1.0 if c.get("triggered") else 0.0
        m = c.get("margin")
        if m is None:
            continue
        try:
            mv = float(m)
        except (TypeError, ValueError):
            continue
        if math.isfinite(mv):
            X[r, j] = mv

print("\n=== per-component liveness ===")
print(f"{'component':28s} trig_rate  n_finite_margin   margin_std")
alive_margin, alive_trig = [], []
for c in CANON:
    j = idx[c]
    tr = T[:, j].mean()
    col = X[:, j]
    fin = np.isfinite(col)
    nfin = int(fin.sum())
    std = float(np.nanstd(col)) if nfin > 1 else 0.0
    if nfin > 1 and std > 1e-12:
        alive_margin.append(c)
    if 0.0 < tr < 1.0:
        alive_trig.append(c)
    print(f"{c:28s} {tr:8.4f}  {nfin:14d}   {std:.4g}")

print(f"\nalive (margin variance) : {alive_margin}")
print(f"alive (triggered varies): {alive_trig}")

def eff_dim(corr):
    w = np.linalg.eigvalsh(corr)
    w = np.clip(w, 0, None)
    s = w.sum()
    if s <= 0:
        return None, None, None
    top = w.max() / s
    pr = (s * s) / (np.square(w).sum())
    return top, pr, np.sort(w)[::-1]

# --- Effective dim on the MARGIN basis (alive margin columns, pairwise corr) ---
def corr_matrix(cols, mat):
    k = len(cols)
    C = np.eye(k)
    for a in range(k):
        for b in range(a + 1, k):
            xa, xb = mat[:, idx[cols[a]]], mat[:, idx[cols[b]]]
            ok = np.isfinite(xa) & np.isfinite(xb)
            if ok.sum() > 2 and np.std(xa[ok]) > 1e-12 and np.std(xb[ok]) > 1e-12:
                r = np.corrcoef(xa[ok], xb[ok])[0, 1]
            else:
                r = 0.0
            C[a, b] = C[b, a] = r
    return C

if len(alive_margin) >= 2:
    Cm = corr_matrix(alive_margin, X)
    top, pr, spec = eff_dim(Cm)
    print(f"\n=== MARGIN basis ({len(alive_margin)} alive cols) ===")
    print("corr matrix:")
    print("        " + " ".join(f"{c[:7]:>8s}" for c in alive_margin))
    for a, c in enumerate(alive_margin):
        print(f"{c[:7]:>7s} " + " ".join(f"{Cm[a,b]:8.3f}" for b in range(len(alive_margin))))
    print(f"eigenvalues: {np.round(spec,3)}")
    print(f"top-eigenvalue fraction: {top:.3f}   participation-ratio (eff dim): {pr:.2f}  of {len(alive_margin)}")

# --- Effective dim on the TRIGGERED (categorical) basis for contrast ---
if len(alive_trig) >= 2:
    Ct = corr_matrix(alive_trig, T)
    top, pr, spec = eff_dim(Ct)
    print(f"\n=== TRIGGERED basis ({len(alive_trig)} alive cols) ===")
    print(f"eigenvalues: {np.round(spec,3)}")
    print(f"top-eigenvalue fraction: {top:.3f}   participation-ratio (eff dim): {pr:.2f}  of {len(alive_trig)}")
else:
    print(f"\nTRIGGERED basis: only {len(alive_trig)} column(s) vary -> categorical basis is rank <=1")
