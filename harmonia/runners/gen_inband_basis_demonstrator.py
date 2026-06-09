"""Step-1 of the corrected experiment ladder (re-audit of the rank-1 KillVector
finding, Harmonia C, 2026-05-27).

WHAT THIS IS
------------
The 2026-05-27 audit concluded the KillVector basis is "rank-1 / a single ruler
in a 12-D costume." The re-audit showed that verdict is an *instrumentation
artifact*: every vector in `_native_kill_vector_pilot.json` carries exactly ONE
component (out_of_band), because the pilot emitted phase-0 short-circuit vectors
for all 24k episodes — including the in-band Lehmer hit (ep 622, M=1.17628,
reward 100). The basis was therefore UNMEASURED, not measured-as-1.

This runner produces the FIRST in-band basis measurement: it generates a
population of in-band candidates (the band-restricted control arm) and records
ALL locally-computable falsifier components per candidate, then measures the
basis (eigenspectrum + participation ratio + max off-diagonal correlation).

HONEST SCOPE / WHAT THIS IS NOT
-------------------------------
- Reference battery, not production. `prometheus_math`'s real battery cannot
  import on this machine (`cypari` missing — env finding). The local falsifiers
  here are faithful reimplementations of discovery_pipeline.py:208-306 logic,
  validated against the Lehmer anchor and the test_native_kill_vector_pilot F6
  case. Catalog (5 comps) and F11 are NOT evaluated here (need data/identical M
  path); F1 margin is deferred (None) per KILL_VECTOR_SPEC.md.
- Control arm, not the thesis test. Candidates are random reciprocal polys
  (band-restricted), NOT an LLM-hallucination operator. This is exactly the
  control the thesis must beat (ladder step 3): if the LLM arm gives the same
  in-band basis as this, hallucination adds nothing.

The production version must run on a cypari machine, wire native_kill_vector_
pilot.emit_kill_vector_for_episode to a real process_candidate record for
in-band episodes, and add the catalog components.
"""
from __future__ import annotations
import json, math, os
import numpy as np
from sympy import Poly, symbols, ZZ

OUT = r"D:\Prometheus\harmonia\tmp\_inband_basis_demonstrator_pilot.json"
DEG = 14
COEFF_RANGE = (-2, -1, 0, 1, 2)
BAND = (1.001, 1.18)
TARGET_INBAND = 2000
MAX_DRAWS = 4_000_000
SEED = 20260527

x = symbols("x")

def mahler(coeffs):
    """Cypari-free Mahler measure via numpy roots (monic integer poly,
    coeffs high->low). Validated against Lehmer below."""
    r = np.roots(coeffs)
    return float(abs(coeffs[0]) * np.prod(np.maximum(1.0, np.abs(r))))

# --- calibration gate: refuse to run if the instrument is off (anchor) ---
LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
_lm = mahler(LEHMER)
assert abs(_lm - 1.17628081826) < 1e-7, f"Mahler instrument off-anchor: {_lm}"

# --- faithful local falsifiers (discovery_pipeline.py:208-306 semantics) ---
def f_out_of_band(M):
    trig = not (BAND[0] < M < BAND[1])
    return trig, M - BAND[1], "absolute"          # margin = M - 1.18 (signed)

def f_reciprocity(coeffs):
    n = len(coeffs)
    margin = max(abs(coeffs[i] - coeffs[n - 1 - i]) for i in range(n // 2)) if n > 1 else 0
    return (margin != 0), float(margin), "absolute"

def f_irreducibility(coeffs):
    try:
        p = Poly(coeffs, x, domain=ZZ)
        factors = p.factor_list()[1]
        nfac = sum(mult for _f, mult in factors)
        return (nfac > 1), float(nfac), "absolute"
    except Exception:
        return None, None, "absolute"

def f1_permutation_null(coeffs, M):
    if not math.isfinite(M):
        return True, None, "p_value"
    rng = np.random.default_rng(20260503)           # matches source seed
    perm_ms = []
    for _ in range(30):
        perm = list(coeffs); rng.shuffle(perm)
        try:
            v = mahler(perm)
            if math.isfinite(v):
                perm_ms.append(v)
        except Exception:
            continue
    if not perm_ms:
        return True, None, "p_value"
    survived = M < float(np.median(perm_ms))
    return (not survived), None, "p_value"          # margin deferred per spec

def f6_base_rate(coeffs, M):
    nz = [c for c in coeffs if c != 0]
    distinct = len(set(nz)) if nz else 0
    trig = distinct < 2
    return trig, float(distinct - 2), "z_score"      # margin = #distinct - 2

def f9_simpler_explanation(M):
    return False, float(M - 1.001), "absolute"       # in-band: never cyclotomic

def components_for(coeffs, M):
    comps = []
    for name, (trig, margin, unit) in {
        "out_of_band": f_out_of_band(M),
        "reciprocity": f_reciprocity(coeffs),
        "irreducibility": f_irreducibility(coeffs),
        "F1_permutation_null": f1_permutation_null(coeffs, M),
        "F6_base_rate": f6_base_rate(coeffs, M),
        "F9_simpler_explanation": f9_simpler_explanation(M),
    }.items():
        comps.append({"falsifier_name": name, "triggered": trig,
                      "margin": margin, "margin_unit": unit})
    return comps

# --- generate band-restricted reciprocal candidates (control arm) ---
def gen_inband(rng):
    seen, eps = set(), []
    draws = 0
    while len(eps) < TARGET_INBAND and draws < MAX_DRAWS:
        draws += 1
        free = rng.integers(low=0, high=len(COEFF_RANGE), size=7)
        c = [COEFF_RANGE[i] for i in free]            # c_1..c_7
        coeffs = [1] + c + c[::-1] + [1]              # palindromic deg-14, monic
        key = tuple(coeffs)
        if key in seen:
            continue
        try:
            M = mahler(coeffs)
        except Exception:
            continue
        if not (BAND[0] < M < BAND[1]):
            continue
        seen.add(key)
        eps.append({"kill_vector": {
            "components": components_for(coeffs, M),
            "operator_class": "band_restricted_reciprocal@control",
            "region_meta": {"env": "demonstrator", "degree": DEG,
                            "alphabet_width": 5, "M": M},
        }, "coeffs": coeffs, "mahler_measure": M})
    return eps, draws

def main():
    rng = np.random.default_rng(SEED)
    eps, draws = gen_inband(rng)
    print(f"in-band candidates: {len(eps)}  (from {draws} draws; "
          f"yield {100*len(eps)/max(draws,1):.4f}%)")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"pilot": {"episodes": eps}}, f)
    print(f"wrote {OUT}")

    # --- inline basis measurement on the in-band population ---
    CANON = ["out_of_band","reciprocity","irreducibility",
             "F1_permutation_null","F6_base_rate","F9_simpler_explanation"]
    idx = {c:i for i,c in enumerate(CANON)}
    n = len(eps)
    X = np.full((n, len(CANON)), np.nan)
    T = np.zeros((n, len(CANON)))
    for r,e in enumerate(eps):
        for c in e["kill_vector"]["components"]:
            j = idx.get(c["falsifier_name"])
            if j is None: continue
            T[r,j] = 1.0 if c["triggered"] else 0.0
            m = c["margin"]
            if m is not None and math.isfinite(float(m)):
                X[r,j] = float(m)

    print("\n=== per-component liveness (IN-BAND population) ===")
    print(f"{'component':24s} trig_rate  n_finite   margin_std")
    alive = []
    for c in CANON:
        j = idx[c]; col = X[:,j]; fin = np.isfinite(col); nfin = int(fin.sum())
        std = float(np.nanstd(col)) if nfin>1 else 0.0
        if nfin>1 and std>1e-12: alive.append(c)
        print(f"{c:24s} {T[:,j].mean():8.4f}  {nfin:8d}   {std:.4g}")
    print(f"\nalive margin components: {alive}")

    if len(alive) >= 2:
        k = len(alive); C = np.eye(k)
        for a in range(k):
            for b in range(a+1,k):
                xa,xb = X[:,idx[alive[a]]], X[:,idx[alive[b]]]
                ok = np.isfinite(xa)&np.isfinite(xb)
                if ok.sum()>2 and np.std(xa[ok])>1e-12 and np.std(xb[ok])>1e-12:
                    C[a,b]=C[b,a]=np.corrcoef(xa[ok],xb[ok])[0,1]
        w = np.clip(np.linalg.eigvalsh(C),0,None); s=w.sum()
        pr = (s*s)/np.square(w).sum(); top=w.max()/s
        print(f"\n=== IN-BAND MARGIN basis ({k} alive cols) ===")
        print("        " + " ".join(f"{c[:7]:>8s}" for c in alive))
        for a,c in enumerate(alive):
            print(f"{c[:7]:>7s} " + " ".join(f"{C[a,b]:8.3f}" for b in range(k)))
        print(f"eigenvalues: {np.round(np.sort(w)[::-1],3)}")
        print(f"top-eig frac: {top:.3f}   participation-ratio (EFF DIM): {pr:.2f} of {k}")
        print(f"max |off-diagonal corr|: {np.max(np.abs(C-np.eye(k))):.3f}")
        print("\nINTERPRETATION: eff-dim > 1 refutes 'rank-1 basis' as a basis claim; "
              "but read the off-diagonals — any |corr|~1.0 block is collinear rulers "
              "(the 'costume' failure pole), NOT independent niches.")

if __name__ == "__main__":
    main()
