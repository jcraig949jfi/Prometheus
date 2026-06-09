"""Phase 0 experiment (EXPERIMENTAL) — does a NEAR-MISS population raise the
effective dimensionality of the Mahler/Lehmer kill-space above 1?

Background: kv_basis_dim.py measured the live KillVector basis at effective
dim = 1.0 on the native pilot (a population of GROSS misses — random/RL
polynomials whose Mahler measure M is far outside the Salem band (1.001, 1.18),
so only `out_of_band` ever fires). The doctrine
(harmonia/memory/architecture/topological_falsification_engine.md) predicts the
collapse is "by population, not by design": a NEAR-MISS population (M near the
band) should reach the downstream falsifiers and light up more axes.

This script tests that prediction, fully offline & deterministic. Two
populations of degree-10 {-1,0,1} polynomials:
  RANDOM    : a uniform sample of random polynomials (the gross-miss baseline).
  NEAR-MISS : the lowest-M tail of a large random pool (+ Lehmer/Salem seeds) —
              i.e. the candidates that got CLOSEST to the survival band. This is
              a mathematically natural near-miss population, NOT one engineered
              to be multi-dimensional.

For each polynomial we compute a MULTI-GATE KillVector (every falsifier fires,
continuous margin each), faithfully replicating the falsifier logic in
prometheus_math/discovery_pipeline.py. We then compare, RANDOM vs NEAR-MISS:
  - per-component liveness (trigger rate, margin std)
  - correlation matrix of margins over alive components
  - participation ratio (effective dimensionality)
  - confound-residual eff-dim: after partialling out `out_of_band` (the M axis)

Success metric (Phase-0 gate, per spec §4.1): NEAR-MISS eff-dim > 1, ideally
with a confound-residual eff-dim > 1 (a real SECOND axis after removing M).
"""
from __future__ import annotations
import math
import numpy as np

SEED = 20260527
DEGREE = 10
N_POOL = 12000
N_POP = 1500
rng = np.random.default_rng(SEED)

# --- Mahler measure: reuse the canonical implementation (Track-D discipline) ---
_MM_SOURCE = None
try:
    from techne.lib.mahler_measure import mahler_measure as _techne_mm
    def mahler(coeffs):
        return float(_techne_mm(list(coeffs)))
    _MM_SOURCE = "techne.lib.mahler_measure"
except Exception:
    def mahler(coeffs):
        # Fallback: M(p)=|lead|*prod(max(1,|root|)). Reversal-invariant.
        r = np.roots(coeffs)
        if r.size == 0:
            return 1.0
        lead = abs(coeffs[0]) if coeffs[0] != 0 else 1.0
        return float(lead * np.prod(np.maximum(1.0, np.abs(r))))
    _MM_SOURCE = "numpy-roots fallback"

try:
    import sympy
    from sympy import symbols, Poly
    _x = symbols("x")
    _HAVE_SYMPY = True
except Exception:
    _HAVE_SYMPY = False


def n_irreducible_factors(coeffs):
    """Number of irreducible factors over QQ (margin = count-1; 0 => irreducible)."""
    if not _HAVE_SYMPY:
        return None
    try:
        p = Poly(list(coeffs), _x)  # coeffs highest-degree first
        _, facs = p.factor_list()
        return int(sum(mult for _f, mult in facs))
    except Exception:
        return None


# --- Multi-gate KillVector (continuous margins), faithful to discovery_pipeline ---
COMPONENTS = ["out_of_band", "reciprocity", "irreducibility",
              "F6_base_rate", "F9_cyclotomic", "F1_perm_null", "F11_cross_val"]

def kill_vector(coeffs, m=None):
    c = list(coeffs)
    if m is None:
        m = mahler(c)
    out = {}
    # 1. out_of_band: signed margin to upper band edge (continuous in M)
    out["out_of_band"] = m - 1.18
    # 2. reciprocity: palindrome distance (0 == palindromic)
    n = len(c)
    out["reciprocity"] = max(abs(c[i] - c[n - 1 - i]) for i in range(n))
    # 3. irreducibility: (#factors - 1); 0 == irreducible
    nf = n_irreducible_factors(c)
    out["irreducibility"] = (nf - 1) if nf is not None else np.nan
    # 4. F6 base-rate: (distinct nonzero values - 2); negative == trivial/killed
    nz = [v for v in c if v != 0]
    out["F6_base_rate"] = (len(set(nz)) - 2) if nz else np.nan
    # 5. F9 cyclotomic gap: M - 1.001
    out["F9_cyclotomic"] = m - 1.001
    # 6. F1 perm-null: median(perm M) - M  (positive == survives)
    perms = []
    for _ in range(20):
        p = list(c); rng.shuffle(p)
        v = mahler(p)
        if math.isfinite(v):
            perms.append(v)
    out["F1_perm_null"] = (float(np.median(perms)) - m) if perms else np.nan
    # 7. F11 cross-val: |M(c) - M(reversed)| (reversal-invariant -> ~0)
    out["F11_cross_val"] = abs(mahler(c) - mahler(list(reversed(c))))
    return out, m


def random_poly():
    # degree exactly DEGREE, nonzero constant + leading (Salem/reciprocal-relevant)
    mid = rng.integers(-1, 2, size=DEGREE - 1)
    lead = rng.choice([-1, 1]); const = rng.choice([-1, 1])
    return [int(lead)] + [int(v) for v in mid] + [int(const)]


# Lehmer's polynomial (M ~ 1.17628) + two small reciprocal seeds for near-miss anchoring
LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
SEEDS = [LEHMER,
         [1, 0, 0, 0, -1, -1, -1, 0, 0, 0, 1],
         [1, -1, 0, 0, 0, 0, 0, 0, 0, -1, 1]]


def build_matrix(polys_with_m):
    rows = []
    for c, m in polys_with_m:
        kv, _ = kill_vector(c, m)
        rows.append([kv[k] for k in COMPONENTS])
    return np.array(rows, dtype=float)


def eff_dim(X):
    """Participation ratio of the correlation matrix over alive (non-constant,
    sufficiently-observed) columns. Returns (eff_dim, alive_cols, top_frac, corr)."""
    alive = []
    for j, name in enumerate(COMPONENTS):
        col = X[:, j]
        fin = np.isfinite(col)
        if fin.sum() > 2 and np.nanstd(col) > 1e-6:   # 1e-6 excludes float-noise axes (F11)
            alive.append(j)
    if len(alive) < 2:
        return 1.0, [COMPONENTS[j] for j in alive], 1.0, None
    k = len(alive)
    C = np.eye(k)
    for a in range(k):
        for b in range(a + 1, k):
            xa, xb = X[:, alive[a]], X[:, alive[b]]
            ok = np.isfinite(xa) & np.isfinite(xb)
            if ok.sum() > 2 and np.std(xa[ok]) > 1e-9 and np.std(xb[ok]) > 1e-9:
                C[a, b] = C[b, a] = np.corrcoef(xa[ok], xb[ok])[0, 1]
    w = np.clip(np.linalg.eigvalsh(C), 0, None)
    pr = (w.sum() ** 2) / (np.square(w).sum())
    return float(pr), [COMPONENTS[j] for j in alive], float(w.max() / w.sum()), C


def confound_residual_dim(X):
    """Regress every component on out_of_band (the M axis), recompute eff-dim on
    residuals. Tests for a REAL second axis after removing the dominant one."""
    j_band = COMPONENTS.index("out_of_band")
    band = X[:, j_band]
    R = np.full_like(X, np.nan)
    for j in range(X.shape[1]):
        if j == j_band:
            continue
        y = X[:, j]
        ok = np.isfinite(y) & np.isfinite(band)
        if ok.sum() < 5 or np.std(band[ok]) < 1e-9:
            continue
        A = np.vstack([band[ok], np.ones(ok.sum())]).T
        coef, *_ = np.linalg.lstsq(A, y[ok], rcond=None)
        R[ok, j] = y[ok] - A @ coef
    return eff_dim(R)


def report(name, polys_with_m):
    print(f"\n{'='*70}\n{name}  (n={len(polys_with_m)})\n{'='*70}")
    Ms = np.array([m for _, m in polys_with_m])
    in_band = np.mean((Ms > 1.001) & (Ms < 1.18))
    print(f"M: min={Ms.min():.4f} median={np.median(Ms):.4f} max={Ms.max():.2f} "
          f"| in-band fraction={in_band:.3f}")
    X = build_matrix(polys_with_m)
    print(f"{'component':16s} trig_rate  margin_std")
    for j, k in enumerate(COMPONENTS):
        col = X[:, j]
        # 'triggered' = margin on the kill side of 0 (component-specific sign)
        if k in ("out_of_band",):
            trig = np.nanmean((col > 0) | (Ms < 1.001))
        elif k in ("reciprocity", "irreducibility", "F11_cross_val"):
            trig = np.nanmean(col > 0)
        elif k == "F6_base_rate":
            trig = np.nanmean(col < 0)
        elif k == "F9_cyclotomic":
            trig = np.nanmean(col <= 0)
        elif k == "F1_perm_null":
            trig = np.nanmean(col <= 0)
        else:
            trig = float("nan")
        print(f"{k:16s} {trig:8.4f}   {np.nanstd(col):.4g}")
    pr, alive, top, C = eff_dim(X)
    if C is not None:
        print("corr(margins) over alive components:")
        short = [a[:7] for a in alive]
        print("        " + " ".join(f"{s:>7s}" for s in short))
        for i, s in enumerate(short):
            print(f"{s:>7s} " + " ".join(f"{C[i, j]:7.2f}" for j in range(len(alive))))
    print(f"alive components: {alive}")
    print(f">> participation ratio (EFFECTIVE DIM): {pr:.2f}   "
          f"(top-eigenvalue frac {top:.3f}) of {len(alive)} alive")
    rpr, ralive, rtop, _ = confound_residual_dim(X)
    print(f">> confound-residual eff-dim (after removing out_of_band/M): {rpr:.2f}  "
          f"alive residual axes: {ralive}")
    return pr, rpr


def main():
    print(f"Mahler source: {_MM_SOURCE} | sympy irreducibility: {_HAVE_SYMPY}")
    print(f"degree={DEGREE} pool={N_POOL} pop={N_POP} seed={SEED}")
    pool = [random_poly() for _ in range(N_POOL)]
    pool_m = [(c, mahler(c)) for c in pool]
    pool_m = [(c, m) for c, m in pool_m if math.isfinite(m)]
    pool_m.sort(key=lambda t: t[1])

    random_idx = rng.choice(len(pool_m), size=min(N_POP, len(pool_m)), replace=False)
    random_pop = [pool_m[i] for i in random_idx]
    near_miss = [(c, mahler(c)) for c in SEEDS] + pool_m[:N_POP]

    pr_r, rpr_r = report("RANDOM (gross-miss baseline)", random_pop)
    pr_n, rpr_n = report("NEAR-MISS (lowest-M tail + seeds)", near_miss)

    print(f"\n{'#'*70}\nPHASE-0 VERDICT\n{'#'*70}")
    print(f"RANDOM    eff-dim={pr_r:.2f}  confound-residual={rpr_r:.2f}")
    print(f"NEAR-MISS eff-dim={pr_n:.2f}  confound-residual={rpr_n:.2f}")
    gate = (pr_n > 1.3) and (rpr_n > 1.0)
    print(f"\nK2 GATE (near-miss eff-dim>1 with a real 2nd axis): "
          f"{'PASS' if gate else 'FAIL'}")
    print("Interpretation: if NEAR-MISS lifts eff-dim above RANDOM and the "
          "confound-residual stays >1, the rank-1 collapse is population-driven "
          "(near-misses light up the deeper falsifiers) -> the masterstroke has "
          "empirical legs. If both stay ~1, the basis is degenerate by design.")


if __name__ == "__main__":
    main()
