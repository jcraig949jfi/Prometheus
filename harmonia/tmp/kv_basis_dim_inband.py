"""Falsifier re-audit of the 2026-05-27 rank-1 KillVector finding.

Claim under test (Harmonia C, attacking the FLIP in topological_falsification_engine.md
§6.2): the headline "effective dimensionality = 1.0 on 24,000 vectors" measures the
candidate POPULATION's band-pass rate, not the BASIS's intrinsic dimensionality,
because the Phase-0 short-circuit (discovery_pipeline.py:341-368) emits a 1-component
vector for every out-of-band candidate. The intrinsic-rank question lives only in the
in-band subset, where Phase 1 computes all 12 components.

So: split phase0-only vs full-vector records; report n_in_band; re-run participation
ratio + eigenspectrum + off-diagonal correlations on the IN-BAND subset only.

This probe attacks my own kill too: if the in-band subset shows the 11 firing and
mutually decorrelated, my critique is wrong and the basis may be real. Run to ground.
"""
import json, math
import numpy as np

P = r"D:\Prometheus\prometheus_math\_native_kill_vector_pilot.json"
with open(P, "r", encoding="utf-8") as f:
    d = json.load(f)
eps = d["pilot"]["episodes"]
print(f"n_episodes = {len(eps)}")

CANON = ["out_of_band","reciprocity","irreducibility",
         "catalog:Mossinghoff","catalog:lehmer_literature","catalog:LMFDB",
         "catalog:OEIS","catalog:arXiv","F1_permutation_null","F6_base_rate",
         "F9_simpler_explanation","F11_cross_validation"]
idx = {c: i for i, c in enumerate(CANON)}

def comp_name(c):
    return c.get("falsifier_name") or c.get("name") or c.get("falsifier") or ""

def comps_of(e):
    kv = e["kill_vector"]
    return kv["components"] if isinstance(kv, dict) and "components" in kv else kv

# --- classify each record by how many distinct canonical components it carries ---
present_counts = []          # how many canonical components appear at all per record
oob_triggered = []           # did out_of_band trigger?
for e in eps:
    names = set()
    oob = False
    for c in comps_of(e):
        nm = comp_name(c)
        if nm in idx:
            names.add(nm)
            if nm == "out_of_band" and c.get("triggered"):
                oob = True
    present_counts.append(len(names))
    oob_triggered.append(oob)

present_counts = np.array(present_counts)
oob_triggered = np.array(oob_triggered)

import collections
hist = collections.Counter(present_counts.tolist())
print("\n=== records by #canonical-components present ===")
for k in sorted(hist):
    print(f"  {k:2d} components present : {hist[k]:7d}  ({100*hist[k]/len(eps):.3f}%)")
print(f"out_of_band triggered: {oob_triggered.sum()}/{len(eps)} = {100*oob_triggered.mean():.3f}%")

# IN-BAND = records that carry MORE than just out_of_band (Phase-1 ran all 12)
in_band = present_counts > 1
n_in = int(in_band.sum())
print(f"\nIN-BAND (>1 component computed) records: {n_in}  ({100*in_band.mean():.4f}%)")
print(f"  -> the rank of a 12-dim basis can be estimated from at most these {n_in} points")

# --- build margin + triggered matrices on the IN-BAND subset only ---
sub = [e for e, ib in zip(eps, in_band) if ib]
n = len(sub)
if n == 0:
    print("\nNo in-band records; basis dimensionality is UNMEASURED, not rank-1.")
    raise SystemExit

X = np.full((n, len(CANON)), np.nan)
T = np.zeros((n, len(CANON)))
for r, e in enumerate(sub):
    for c in comps_of(e):
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

print(f"\n=== per-component liveness on IN-BAND subset (n={n}) ===")
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
    return w.max()/s, (s*s)/(np.square(w).sum()), np.sort(w)[::-1]

def corr_matrix(cols, mat):
    k = len(cols)
    C = np.eye(k)
    for a in range(k):
        for b in range(a+1, k):
            xa, xb = mat[:, idx[cols[a]]], mat[:, idx[cols[b]]]
            ok = np.isfinite(xa) & np.isfinite(xb)
            if ok.sum() > 2 and np.std(xa[ok]) > 1e-12 and np.std(xb[ok]) > 1e-12:
                r = np.corrcoef(xa[ok], xb[ok])[0,1]
            else:
                r = 0.0
            C[a,b] = C[b,a] = r
    return C

if len(alive_margin) >= 2:
    Cm = corr_matrix(alive_margin, X)
    top, pr, spec = eff_dim(Cm)
    print(f"\n=== IN-BAND MARGIN basis ({len(alive_margin)} alive cols) ===")
    print("        " + " ".join(f"{c[:7]:>8s}" for c in alive_margin))
    for a, c in enumerate(alive_margin):
        print(f"{c[:7]:>7s} " + " ".join(f"{Cm[a,b]:8.3f}" for b in range(len(alive_margin))))
    print(f"eigenvalues: {np.round(spec,3)}")
    print(f"top-eig frac: {top:.3f}   participation-ratio (eff dim): {pr:.2f} of {len(alive_margin)}")
    print(f"max |off-diagonal corr|: {np.max(np.abs(Cm - np.eye(len(alive_margin)))):.3f}")
else:
    print(f"\nIN-BAND MARGIN basis: only {len(alive_margin)} alive col(s) even among in-band "
          f"-> basis is genuinely rank<=1 on the data that reaches the deep falsifiers.")
