"""
Sha–Fricke Obstruction Tensor (Gemini #11)

Compute effective tensor rank of the trilinear map linking:
  - Sha (analytic) sizes
  - Elliptic curve ranks
  - Fricke eigenvalues (from weight-2 newforms)

across isogeny classes in the LMFDB elliptic curve database.

Data: 31K elliptic curves from charon DuckDB, joined with mf_newforms
via conductor + isogeny class label -> weight-2 newform label.
"""
import json
import numpy as np
import duckdb
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "sha_fricke_tensor_results.json"

# --1. Load joined data --───────────────────────────────────────────────
con = duckdb.connect(str(BASE.parent / "charon/data/charon.duckdb"), read_only=True)

df = con.execute("""
    SELECT ec.rank, ec.sha, mf.fricke_eigenval AS fricke
    FROM elliptic_curves ec
    JOIN modular_forms mf
      ON mf.lmfdb_label = ec.conductor || '.2.a.' || SPLIT_PART(ec.lmfdb_iso, '.', 2)
    WHERE ec.sha IS NOT NULL
      AND mf.fricke_eigenval IS NOT NULL
""").fetchnumpy()
con.close()

ranks = np.array(df["rank"], dtype=int)
sha_vals = np.array(df["sha"], dtype=int)
fricke_vals = np.array(df["fricke"], dtype=int)

n_total = len(ranks)
print(f"Loaded {n_total} curves with (rank, sha, fricke)")

# --2. Bin sha values --─────────────────────────────────────────────────
# sha bins: {1, 4, 9, 16+}
SHA_BINS = {1: 0, 4: 1, 9: 2}  # exact -> index
N_SHA = 4  # 0=1, 1=4, 2=9, 3=16+

def sha_bin(v):
    if v in SHA_BINS:
        return SHA_BINS[v]
    return 3  # 16+

sha_idx = np.array([sha_bin(v) for v in sha_vals])

# rank bins: {0, 1, 2}
RANK_BINS = {0: 0, 1: 1, 2: 2}
N_RANK = 3
rank_idx = np.array([RANK_BINS.get(v, 2) for v in ranks])  # rank >= 2 -> bin 2

# fricke bins: {-1, +1} -> indices {0, 1}
N_FRICKE = 2
fricke_idx = np.array([(f + 1) // 2 for f in fricke_vals])  # -1->0, +1->1

# --3. Build 3D contingency tensor T[sha_bin, rank, fricke] --───────────
T = np.zeros((N_SHA, N_RANK, N_FRICKE), dtype=np.float64)
for i in range(n_total):
    T[sha_idx[i], rank_idx[i], fricke_idx[i]] += 1

print(f"\nTensor shape: {T.shape}")
print(f"Total entries: {T.sum():.0f}")
print(f"\nContingency tensor T[sha_bin, rank, fricke]:")
sha_labels = ["sha=1", "sha=4", "sha=9", "sha>=16"]
rank_labels = ["rank=0", "rank=1", "rank=2"]
fricke_labels = ["fricke=-1", "fricke=+1"]

for s in range(N_SHA):
    for r in range(N_RANK):
        for f in range(N_FRICKE):
            if T[s, r, f] > 0:
                print(f"  T[{sha_labels[s]}, {rank_labels[r]}, {fricke_labels[f]}] = {T[s,r,f]:.0f}")

# --4. Mode unfoldings + SVD --──────────────────────────────────────────
def mode_unfold(tensor, mode):
    """Unfold tensor along given mode (0, 1, or 2)."""
    return np.moveaxis(tensor, mode, 0).reshape(tensor.shape[mode], -1)

def effective_rank_svd(matrix, threshold=0.95):
    """Effective rank at given variance threshold."""
    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    if s.sum() < 1e-12:
        return 0, s.tolist(), []
    cumvar = np.cumsum(s**2) / np.sum(s**2)
    eff_rank = int(np.searchsorted(cumvar, threshold)) + 1
    return eff_rank, s.tolist(), cumvar.tolist()

print("\n-- Mode Unfoldings (SVD) --")
unfolding_results = {}
mode_names = ["sha_bin", "rank", "fricke"]

for mode in range(3):
    M = mode_unfold(T, mode)
    eff_rank, svals, cumvar = effective_rank_svd(M, threshold=0.95)
    print(f"\n  Mode-{mode} ({mode_names[mode]}): matrix shape {M.shape}")
    print(f"    Singular values: {[f'{v:.2f}' for v in svals]}")
    print(f"    Cumulative variance: {[f'{v:.4f}' for v in cumvar]}")
    print(f"    Effective rank (95%): {eff_rank}")
    unfolding_results[mode_names[mode]] = {
        "matrix_shape": list(M.shape),
        "singular_values": [round(v, 4) for v in svals],
        "cumulative_variance": [round(v, 6) for v in cumvar],
        "effective_rank_95pct": eff_rank,
    }

# --5. CP decomposition via ALS (successive rank-1 approximation) --─────
def als_rank1(tensor, max_iter=200, tol=1e-8):
    """Find best rank-1 approximation via ALS."""
    dims = tensor.shape
    # Initialize factor vectors randomly
    rng = np.random.RandomState(42)
    factors = [rng.randn(d) for d in dims]
    # Normalize
    for i in range(len(factors)):
        factors[i] /= np.linalg.norm(factors[i]) + 1e-12

    for iteration in range(max_iter):
        old_factors = [f.copy() for f in factors]
        for mode in range(len(dims)):
            # Contract tensor with all other factor vectors
            result = tensor.copy()
            for m in range(len(dims) - 1, -1, -1):
                if m != mode:
                    result = np.tensordot(result, factors[m], axes=([m if m < mode or m == mode else m], [0]))
                    # Simpler: just do sequential contraction
            # Redo cleanly
            result = tensor
            contracted_modes = sorted([m for m in range(len(dims)) if m != mode], reverse=True)
            for m in contracted_modes:
                result = np.tensordot(result, factors[m], axes=([m], [0]))
            factors[mode] = result / (np.linalg.norm(result) + 1e-12)

        # Check convergence
        delta = max(np.linalg.norm(factors[i] - old_factors[i]) for i in range(len(dims)))
        if delta < tol:
            break

    # Compute the scalar weight
    approx = factors[0]
    for f in factors[1:]:
        approx = np.outer(approx, f).reshape([len(factors[i]) for i in range(len(factors))][:len(approx.shape)+1])

    # Weight = <T, a (x) b (x) c>
    weight = tensor
    for f in factors:
        weight = np.tensordot(weight, f, axes=([0], [0]))
    weight = float(weight)

    return weight, factors

def cp_rank_greedy(tensor, max_rank=10, tol_frac=0.01):
    """
    Estimate CP rank by greedy successive rank-1 extraction.
    Stop when residual norm < tol_frac * original norm.
    """
    residual = tensor.copy()
    orig_norm = np.linalg.norm(tensor)
    components = []

    for r in range(max_rank):
        weight, factors = als_rank1(residual)
        # Build rank-1 term
        term = weight
        outer = factors[0]
        for f in factors[1:]:
            outer = np.multiply.outer(outer, f)
        term = weight * outer

        residual = residual - term
        res_norm = np.linalg.norm(residual)
        frac = res_norm / orig_norm
        components.append({
            "component": r + 1,
            "weight": round(float(weight), 4),
            "residual_norm": round(float(res_norm), 4),
            "residual_fraction": round(float(frac), 6),
        })
        print(f"    Component {r+1}: weight={weight:.2f}, residual={frac:.6f}")
        if frac < tol_frac:
            break

    return len(components), components

print("\n-- CP Decomposition (Greedy ALS) --")
cp_rank, cp_components = cp_rank_greedy(T, max_rank=10, tol_frac=0.001)
print(f"\n  Estimated CP rank: {cp_rank}")

# --6. Nuclear norm rank bound --────────────────────────────────────────
# Also compute multilinear rank = tuple of mode unfolding ranks
multilinear_rank = []
for mode in range(3):
    M = mode_unfold(T, mode)
    r = int(np.linalg.matrix_rank(M, tol=1e-6))
    multilinear_rank.append(r)
print(f"\n  Multilinear rank: {tuple(multilinear_rank)}")

# --7. Structural analysis: parity constraint --─────────────────────────
# The functional equation forces: rank even <=> fricke = -1 (sign = +1 means odd functional equation)
# This means the tensor is extremely structured
print("\n--Structural Analysis --")
print("  Parity constraint (functional equation):")
print("    rank even (0,2) => fricke = -1")
print("    rank odd  (1)   => fricke = +1")
nonzero_entries = []
for s in range(N_SHA):
    for r in range(N_RANK):
        for f in range(N_FRICKE):
            if T[s, r, f] > 0:
                nonzero_entries.append({
                    "sha_bin": sha_labels[s],
                    "rank": rank_labels[r],
                    "fricke": fricke_labels[f],
                    "count": int(T[s, r, f]),
                })
n_nonzero = len(nonzero_entries)
print(f"  Non-zero entries: {n_nonzero} / {N_SHA * N_RANK * N_FRICKE}")
print(f"  Sparsity: {1 - n_nonzero / (N_SHA * N_RANK * N_FRICKE):.2%}")

# The parity constraint reduces effective dimensionality
# Check: does rank perfectly predict fricke?
parity_perfect = True
for entry in nonzero_entries:
    r_val = int(entry["rank"].split("=")[1])
    f_val = int(entry["fricke"].split("=")[1])
    expected_fricke = -1 if r_val % 2 == 0 else 1
    if f_val != expected_fricke:
        parity_perfect = False
        print(f"    VIOLATION: {entry}")
print(f"  Parity constraint perfectly satisfied: {parity_perfect}")

# --8. Independence test: is sha independent of rank given fricke? --────
# Under the parity constraint, fricke is determined by rank, so
# the real question is: what is the sha distribution across ranks?
print("\n--Sha distribution by rank --")
for r in range(N_RANK):
    total = T[:, r, :].sum()
    if total > 0:
        sha_dist = T[:, r, :].sum(axis=1) / total
        print(f"  {rank_labels[r]}: sha_dist = {[f'{v:.4f}' for v in sha_dist]} (n={total:.0f})")

# --9. Compile results --────────────────────────────────────────────────
results = {
    "challenge": "Gemini #11: Sha-Fricke Obstruction Tensor Rank",
    "description": "Trilinear map T[sha_bin, rank, fricke_sign] across EC isogeny classes",
    "data": {
        "n_curves": int(n_total),
        "tensor_shape": list(T.shape),
        "sha_bins": ["1", "4", "9", "16+"],
        "rank_bins": ["0", "1", "2"],
        "fricke_bins": ["-1", "+1"],
    },
    "tensor_raw": T.tolist(),
    "nonzero_entries": nonzero_entries,
    "sparsity": round(1 - n_nonzero / (N_SHA * N_RANK * N_FRICKE), 4),
    "mode_unfoldings": unfolding_results,
    "multilinear_rank": multilinear_rank,
    "cp_decomposition": {
        "estimated_rank": cp_rank,
        "components": cp_components,
    },
    "parity_constraint_perfect": parity_perfect,
    "structural_note": (
        "The functional equation forces fricke = (-1)^rank, making the fricke "
        "mode fully determined by rank. The tensor is supported on only "
        f"{n_nonzero}/{N_SHA * N_RANK * N_FRICKE} entries. "
        "Effective tensor rank reflects sha-rank interaction under this constraint."
    ),
    "effective_rank_summary": {
        "mode_sha_95pct": unfolding_results["sha_bin"]["effective_rank_95pct"],
        "mode_rank_95pct": unfolding_results["rank"]["effective_rank_95pct"],
        "mode_fricke_95pct": unfolding_results["fricke"]["effective_rank_95pct"],
        "multilinear_rank": multilinear_rank,
        "cp_rank": cp_rank,
    },
}

with open(OUT, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUT}")
print(f"\n--Summary --")
print(f"  Multilinear rank: {tuple(multilinear_rank)}")
print(f"  CP rank: {cp_rank}")
print(f"  Mode effective ranks (95%): sha={unfolding_results['sha_bin']['effective_rank_95pct']}, "
      f"rank={unfolding_results['rank']['effective_rank_95pct']}, "
      f"fricke={unfolding_results['fricke']['effective_rank_95pct']}")
