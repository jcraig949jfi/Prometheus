"""
Koios Rank Analyst — SVD of the Harmonia invariance tensor.

Tests Geometry 1: is the invariance tensor low-rank (effective rank <= 5)?

Three versions:
  A (naive): treat 0 cells as zero; run np.linalg.svd directly
  B (SVT):   nuclear-norm completion (Singular Value Thresholding)
             on 0 cells (they're missing, not zero)
  C (agreement): feature-feature correlation on shared projections only
                  (no imputation — purely observed data)

Output:
  - cartography/docs/tensor_rank_analysis.md
  - cartography/docs/tensor_rank_analysis.json
  - cartography/plots/singular_values.png
  - cartography/plots/variance_explained.png
  - cartography/plots/top3_left_vectors.png
  - cartography/plots/top3_right_vectors.png
"""
import json
import sys
import io
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harmonia" / "memory"))

# Import first — it wraps stdout
import build_landscape_tensor
from build_landscape_tensor import build_tensor, FEATURES, PROJECTIONS

# Fix stdout if build_landscape_tensor closed it
if sys.stdout.closed:
    sys.stdout = io.TextIOWrapper(
        sys.__stdout__.buffer if sys.__stdout__ and not sys.__stdout__.closed
        else open(os.devnull, 'w'),
        encoding='utf-8', errors='replace'
    )

PLOTS = ROOT / "cartography" / "plots"
DOCS = ROOT / "cartography" / "docs"
PLOTS.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)


def effective_rank(singular_values, threshold):
    """Minimum k such that cumulative variance >= (1 - threshold)."""
    total = np.sum(singular_values ** 2)
    if total == 0:
        return 0
    cumvar = np.cumsum(singular_values ** 2) / total
    idx = np.searchsorted(cumvar, 1.0 - threshold)
    return int(idx + 1)


def svt_completion(M_obs, mask, tau=5.0, delta=1.2, max_iter=1000, tol=1e-6):
    """Singular Value Thresholding for nuclear-norm matrix completion.
    Cai, Candes, Shen (2010). More principled than iterative SVD imputation
    for very sparse matrices."""
    Y = np.zeros_like(M_obs, dtype=float)
    for it in range(max_iter):
        U, S, Vt = np.linalg.svd(Y, full_matrices=False)
        S_thresh = np.maximum(S - tau, 0)
        X = U @ np.diag(S_thresh) @ Vt
        residual = np.zeros_like(M_obs, dtype=float)
        residual[mask] = M_obs[mask] - X[mask]
        Y = Y + delta * residual
        err = np.linalg.norm(residual) / max(1, np.linalg.norm(M_obs[mask]))
        if err < tol:
            break
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    return X, U, S, Vt, it + 1


def feature_agreement_matrix(M, mask):
    """Compute feature-feature correlation using only shared observed projections."""
    n = M.shape[0]
    agreement = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            shared = mask[i] & mask[j]
            if shared.sum() > 1:
                r = np.corrcoef(M[i, shared], M[j, shared])[0, 1]
                agreement[i, j] = r if np.isfinite(r) else 0
    return agreement


def plot_singular_values(sv_a, sv_svt, path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    k = min(15, len(sv_a))
    x = np.arange(1, k + 1)

    ax1.bar(x - 0.15, sv_a[:k], 0.3, label='A (0=zero)', color='#4C72B0', alpha=0.8)
    ax1.bar(x + 0.15, sv_svt[:k], 0.3, label='B (SVT completion)', color='#DD8452', alpha=0.8)
    ax1.set_xlabel('Singular value index')
    ax1.set_ylabel('Singular value')
    ax1.set_title('Singular Values (linear)')
    ax1.legend()
    ax1.set_xticks(x)

    sv_a_pos = sv_a[:k][sv_a[:k] > 1e-10]
    sv_svt_pos = sv_svt[:k][sv_svt[:k] > 1e-10]
    ax2.bar(np.arange(1, len(sv_a_pos) + 1) - 0.15, sv_a_pos, 0.3,
            label='A (0=zero)', color='#4C72B0', alpha=0.8)
    ax2.bar(np.arange(1, len(sv_svt_pos) + 1) + 0.15, sv_svt_pos, 0.3,
            label='B (SVT)', color='#DD8452', alpha=0.8)
    ax2.set_yscale('log')
    ax2.set_xlabel('Singular value index')
    ax2.set_ylabel('Singular value (log)')
    ax2.set_title('Singular Values (log scale)')
    ax2.legend()
    ax2.set_xticks(x)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_variance_explained(sv_a, sv_svt, sv_agree, path):
    fig, ax = plt.subplots(figsize=(10, 6))
    k = 15

    for sv, label, color, marker in [
        (sv_a, 'A (0=zero)', '#4C72B0', 'o'),
        (sv_svt, 'B (SVT completion)', '#DD8452', 's'),
        (sv_agree, 'C (agreement matrix)', '#55A868', '^'),
    ]:
        n = min(k, len(sv))
        x = np.arange(1, n + 1)
        total = np.sum(sv ** 2)
        cum = np.cumsum(sv[:n] ** 2) / total * 100 if total > 0 else np.zeros(n)
        ax.plot(x, cum, f'{marker}-', label=label, linewidth=2)

    ax.axhline(y=95, color='gray', linestyle='--', alpha=0.5, label='95%')
    ax.axhline(y=99, color='gray', linestyle=':', alpha=0.5, label='99%')
    ax.set_xlabel('Number of components (k)')
    ax.set_ylabel('Cumulative variance explained (%)')
    ax.set_title('Cumulative Variance Explained — Three Methods')
    ax.legend()
    ax.set_xticks(range(1, k + 1))
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_top_vectors(vectors, labels, title, path, top_n=3):
    fig, axes = plt.subplots(top_n, 1, figsize=(14, 4 * top_n))
    if top_n == 1:
        axes = [axes]

    for i in range(top_n):
        ax = axes[i]
        v = vectors[i]
        order = np.argsort(-np.abs(v))
        v_sorted = v[order]
        labels_sorted = [labels[j] for j in order]

        sig_mask = np.abs(v_sorted) > 0.05
        if sig_mask.sum() == 0:
            sig_mask[:5] = True

        v_show = v_sorted[sig_mask]
        l_show = [labels_sorted[j] for j in range(len(sig_mask)) if sig_mask[j]]

        colors = ['#C44E52' if x < 0 else '#4C72B0' for x in v_show]
        ax.barh(range(len(v_show)), v_show, color=colors, alpha=0.8)
        ax.set_yticks(range(len(v_show)))
        ax.set_yticklabels(l_show, fontsize=8)
        ax.set_xlabel('Component weight')
        ax.set_title(f'Singular vector {i+1} (|weight| > 0.05)')
        ax.axvline(x=0, color='black', linewidth=0.5)
        ax.invert_yaxis()
        ax.grid(True, alpha=0.2, axis='x')

    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


def format_vector(vec, ids, metadata_list, id_key="id", label_key="label"):
    """Format a singular vector as list of {id, weight, label} for significant components."""
    order = np.argsort(-np.abs(vec))
    result = []
    for j in order:
        if abs(vec[j]) > 0.05:
            meta = next((m for m in metadata_list if m[id_key] == ids[j]), None)
            label = meta[label_key][:70] if meta else ids[j]
            result.append({"id": ids[j], "weight": round(float(vec[j]), 4), "label": label})
    return result


def main():
    T, feature_ids, proj_ids = build_tensor()
    M = T.astype(float)
    mask = (T != 0)
    n_obs = int(mask.sum())
    n_total = int(M.size)

    print(f"Matrix shape: {M.shape}")
    print(f"Observed cells: {n_obs} / {n_total} ({n_obs/n_total*100:.1f}%)")
    print(f"Missing-to-observed ratio: {(n_total - n_obs)/n_obs:.1f}:1")
    print()

    # ================================================================
    # VERSION A: treat 0 as zero
    # ================================================================
    print("=" * 60)
    print("VERSION A: 0 cells treated as zero")
    print("=" * 60)

    U_a, S_a, Vt_a = np.linalg.svd(M, full_matrices=False)
    total_a = np.sum(S_a ** 2)
    cumvar_a = np.cumsum(S_a ** 2) / total_a

    rank_95_a = effective_rank(S_a, 0.05)
    rank_99_a = effective_rank(S_a, 0.01)

    print(f"Top-10 singular values: {S_a[:10].round(4)}")
    print(f"Cumulative variance (top 10):")
    for k in range(min(10, len(S_a))):
        print(f"  k={k+1}: {cumvar_a[k]*100:.2f}%")
    print(f"Effective rank (95%): {rank_95_a}")
    print(f"Effective rank (99%): {rank_99_a}")

    # ================================================================
    # VERSION B: SVT nuclear-norm completion (tau sweep)
    # ================================================================
    print()
    print("=" * 60)
    print("VERSION B: Nuclear-norm completion (SVT, tau sweep)")
    print("=" * 60)

    svt_results = {}
    for tau in [1.0, 2.0, 3.0, 5.0]:
        X, U, S, Vt, nit = svt_completion(M, mask, tau=tau)
        total = np.sum(S ** 2)
        cumvar = np.cumsum(S ** 2) / total if total > 0 else np.zeros(len(S))
        r95 = effective_rank(S, 0.05)
        r99 = effective_rank(S, 0.01)
        rmse = float(np.sqrt(np.mean((X[mask] - M[mask])**2)))
        svt_results[tau] = {
            "S": S, "U": U, "Vt": Vt, "X": X,
            "rank_95": r95, "rank_99": r99, "rmse": rmse, "nit": nit,
            "cumvar": cumvar,
        }
        print(f"tau={tau:.1f}: rank(95%)={r95}, rank(99%)={r99}, "
              f"RMSE_obs={rmse:.6f}, iters={nit}")
        print(f"  Top-5 SVs: {S[:5].round(3)}")

    # Use tau=3.0 as the reference (moderate regularization)
    ref_tau = 3.0
    svt_ref = svt_results[ref_tau]
    S_b = svt_ref["S"]
    U_b = svt_ref["U"]
    Vt_b = svt_ref["Vt"]
    rank_95_b = svt_ref["rank_95"]
    rank_99_b = svt_ref["rank_99"]
    cumvar_b = svt_ref["cumvar"]

    # ================================================================
    # VERSION C: Feature agreement matrix (observed-only)
    # ================================================================
    print()
    print("=" * 60)
    print("VERSION C: Feature agreement matrix (observed-only)")
    print("=" * 60)

    A = feature_agreement_matrix(M, mask)
    U_c, S_c, Vt_c = np.linalg.svd(A, full_matrices=False)
    total_c = np.sum(S_c ** 2)
    cumvar_c = np.cumsum(S_c ** 2) / total_c

    rank_95_c = effective_rank(S_c, 0.05)
    rank_99_c = effective_rank(S_c, 0.01)

    print(f"Top-10 singular values: {S_c[:10].round(3)}")
    print(f"Cumulative variance (top 10):")
    for k in range(min(10, len(S_c))):
        print(f"  k={k+1}: {cumvar_c[k]*100:.2f}%")
    print(f"Effective rank (95%): {rank_95_c}")
    print(f"Effective rank (99%): {rank_99_c}")

    # ================================================================
    # PLOTS
    # ================================================================
    plot_singular_values(S_a, S_b, PLOTS / "singular_values.png")
    plot_variance_explained(S_a, S_b, S_c, PLOTS / "variance_explained.png")

    f_labels = list(feature_ids)
    p_labels = list(proj_ids)

    # Use Version A vectors (most conservative) for the component plots
    plot_top_vectors(U_a.T[:3], f_labels,
                     'Top 3 Left Singular Vectors (Feature Axis) — Version A',
                     PLOTS / "top3_left_vectors.png")
    plot_top_vectors(Vt_a[:3], p_labels,
                     'Top 3 Right Singular Vectors (Projection Axis) — Version A',
                     PLOTS / "top3_right_vectors.png")

    # ================================================================
    # TOP 3 VECTORS (Version A — most trustworthy with sparse data)
    # ================================================================
    print()
    print("=" * 60)
    print("TOP 3 LEFT SINGULAR VECTORS (Feature axis) — Version A")
    print("=" * 60)

    left_vectors = []
    for i in range(3):
        vec = U_a[:, i]
        components = format_vector(vec, feature_ids, FEATURES)
        left_vectors.append({"index": i+1, "sigma": round(float(S_a[i]), 4), "components": components})
        print(f"\nLeft vector {i+1} (sigma={S_a[i]:.4f}):")
        for c in components:
            print(f"  {c['id']:6s} {c['weight']:+.4f}  {c['label']}")

    print()
    print("=" * 60)
    print("TOP 3 RIGHT SINGULAR VECTORS (Projection axis) — Version A")
    print("=" * 60)

    right_vectors = []
    for i in range(3):
        vec = Vt_a[i, :]
        components = format_vector(vec, proj_ids, PROJECTIONS)
        right_vectors.append({"index": i+1, "sigma": round(float(S_a[i]), 4), "components": components})
        print(f"\nRight vector {i+1} (sigma={S_a[i]:.4f}):")
        for c in components:
            print(f"  {c['id']:6s} {c['weight']:+.4f}  {c['label']}")

    # ================================================================
    # MPS NOTE
    # ================================================================
    print()
    print("MPS: The invariance object is a 2-index matrix. MPS bond dimension")
    print("= SVD effective rank. The SVD IS the decomposition; no separate")
    print("MPS computation needed.")

    # ================================================================
    # INTERPRETATION
    # ================================================================
    print()
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    # Consensus rank: take the range across methods
    ranks_95 = [rank_95_a, rank_95_b, rank_95_c]
    min_r, max_r = min(ranks_95), max(ranks_95)

    print(f"Rank estimates at 95%: A={rank_95_a}, B(SVT tau=3)={rank_95_b}, C(agreement)={rank_95_c}")
    print(f"Rank estimates at 99%: A={rank_99_a}, B(SVT tau=3)={rank_99_b}, C(agreement)={rank_99_c}")
    print()

    if max_r <= 5:
        verdict = "VALIDATED"
        interp = "strong"
    elif min_r <= 5:
        verdict = "INCONCLUSIVE"
        interp = "method-dependent"
    elif max_r <= 15:
        verdict = "PARTIAL"
        interp = "structure exists but more than 5 independent axes"
    else:
        verdict = "FALSIFIED"
        interp = "many independent axes"

    print(f"Geometry 1 verdict: {verdict} ({interp})")
    print()

    # Key diagnostic
    print("SPARSITY WARNING: 89% of cells are untested. Matrix completion")
    print("methods are unreliable at this density (need ~O(n*r*log n) observations,")
    print(f"have {n_obs}, need ~250+ for r=5). Version A (zeros) is biased toward")
    print("higher rank; Version B (completion) may be biased toward lower rank.")
    print("Version C (agreement on shared observations) is the most honest but")
    print("operates on a derived quantity, not the raw matrix.")
    print()
    print("RECOMMENDATION: Fill the tensor. Every untested cell that gets a")
    print("verdict tightens the rank estimate. At 30%+ density the methods")
    print("will converge.")

    # ================================================================
    # JSON
    # ================================================================
    result = {
        "analysis": "Koios rank analysis of Harmonia invariance tensor",
        "date": "2026-04-18",
        "matrix_shape": list(M.shape),
        "observed_cells": n_obs,
        "total_cells": n_total,
        "density_pct": round(n_obs / n_total * 100, 1),
        "version_A": {
            "description": "0 cells treated as zero",
            "singular_values": [round(float(s), 4) for s in S_a],
            "cumulative_variance_pct": [round(float(c * 100), 2) for c in cumvar_a[:15]],
            "effective_rank_95pct": rank_95_a,
            "effective_rank_99pct": rank_99_a,
            "top3_left_vectors": left_vectors,
            "top3_right_vectors": right_vectors,
        },
        "version_B_svt": {
            "description": "Nuclear-norm SVT completion (tau=3.0)",
            "tau": ref_tau,
            "iterations": svt_ref["nit"],
            "rmse_observed": round(svt_ref["rmse"], 6),
            "singular_values": [round(float(s), 4) for s in S_b[:15]],
            "cumulative_variance_pct": [round(float(c * 100), 2) for c in cumvar_b[:15]],
            "effective_rank_95pct": rank_95_b,
            "effective_rank_99pct": rank_99_b,
            "tau_sweep": {
                str(tau): {
                    "rank_95": r["rank_95"], "rank_99": r["rank_99"],
                    "rmse": round(r["rmse"], 6),
                    "top5_sv": [round(float(s), 3) for s in r["S"][:5]],
                }
                for tau, r in svt_results.items()
            },
        },
        "version_C_agreement": {
            "description": "Feature agreement matrix on shared observed projections",
            "singular_values": [round(float(s), 3) for s in S_c[:15]],
            "cumulative_variance_pct": [round(float(c * 100), 2) for c in cumvar_c[:15]],
            "effective_rank_95pct": rank_95_c,
            "effective_rank_99pct": rank_99_c,
        },
        "geometry_1_verdict": verdict,
        "headline": f"A rank(95%)={rank_95_a}, B(SVT) rank(95%)={rank_95_b}, C(agreement) rank(95%)={rank_95_c}",
        "sparsity_warning": f"{100 - round(n_obs/n_total*100, 1)}% missing — completion unreliable at this density",
    }

    with open(DOCS / "tensor_rank_analysis.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nJSON: {DOCS / 'tensor_rank_analysis.json'}")
    print(f"Plots: {PLOTS}")

    return result


if __name__ == "__main__":
    main()
