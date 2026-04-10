#!/usr/bin/env python3
"""
F10: OEIS Spectral Clustering Dimension
========================================
Build a similarity graph on 5000 OEIS sequences using FFT spectral signatures.
Compute the normalized graph Laplacian eigenvalue spectrum to measure the
intrinsic dimension of OEIS sequence space.

Method:
  1. Parse 5000 OEIS sequences (50+ terms) from stripped_new.txt
  2. Compute 32-dim FFT power spectrum for each sequence
  3. Build cosine similarity graph, keep top-5% edges (k=250 nearest neighbors)
  4. Compute normalized graph Laplacian eigenvalues
  5. Fit spectral decay lambda_i ~ i^(-2/d) to extract effective dimension d
  6. Compare eigenvalue spectrum to Marchenko-Pastur (random matrix) prediction
"""

import json
import numpy as np
from pathlib import Path
from scipy.spatial.distance import cdist
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
from scipy.optimize import curve_fit
import time

DATA_FILE = Path(__file__).parent.parent / "oeis" / "data" / "stripped_new.txt"
OUT_FILE = Path(__file__).parent / "oeis_spectral_dimension_results.json"

MIN_TERMS = 50
N_SEQUENCES = 5000
FFT_DIM = 32
K_NN = 250  # top-5% of 5000
N_EIGENVALUES = 300  # enough to fit decay


def parse_oeis(path, min_terms=MIN_TERMS, max_seqs=N_SEQUENCES):
    """Parse OEIS stripped file, return sequences with 50+ terms."""
    sequences = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: A000001 ,val1,val2,...,
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue
            seq_id = parts[0]
            vals_str = parts[1].strip().strip(",")
            if not vals_str:
                continue
            try:
                vals = [int(x) for x in vals_str.split(",") if x.strip()]
            except ValueError:
                continue
            if len(vals) >= min_terms:
                sequences[seq_id] = vals
                if len(sequences) >= max_seqs:
                    break
    return sequences


def compute_fft_signature(values, dim=FFT_DIM):
    """Compute normalized FFT power spectrum signature."""
    arr = np.array(values, dtype=np.float64)
    # Log-transform to handle wide dynamic range (shift by 1 to handle zeros)
    arr = np.sign(arr) * np.log1p(np.abs(arr))
    # Zero-mean
    arr = arr - arr.mean()
    # FFT
    fft_vals = np.fft.rfft(arr)
    power = np.abs(fft_vals) ** 2
    # Take first `dim` components (skip DC which is ~0 after centering)
    if len(power) > dim + 1:
        sig = power[1:dim + 1]
    else:
        sig = np.zeros(dim)
        n = min(len(power) - 1, dim)
        sig[:n] = power[1:1 + n]
    # Normalize to unit vector for cosine similarity
    norm = np.linalg.norm(sig)
    if norm > 0:
        sig = sig / norm
    return sig


def build_knn_graph(signatures, k=K_NN):
    """Build k-NN graph using cosine similarity."""
    n = len(signatures)
    print(f"  Computing pairwise cosine distances for {n} sequences...")
    # cosine distance = 1 - cosine_similarity
    dist_matrix = cdist(signatures, signatures, metric="cosine")

    # Build symmetric k-NN adjacency
    rows, cols, weights = [], [], []
    for i in range(n):
        # Get k nearest neighbors (excluding self)
        dists = dist_matrix[i].copy()
        dists[i] = np.inf  # exclude self
        nn_idx = np.argpartition(dists, k)[:k]
        for j in nn_idx:
            sim = 1.0 - dist_matrix[i, j]
            if sim > 0:
                rows.append(i)
                cols.append(j)
                weights.append(sim)

    # Symmetrize: W = max(W, W^T)
    W = csr_matrix((weights, (rows, cols)), shape=(n, n))
    W = W.maximum(W.T)
    return W


def normalized_laplacian_eigenvalues(W, n_eigs=N_EIGENVALUES):
    """Compute smallest eigenvalues of normalized graph Laplacian."""
    n = W.shape[0]
    # Degree matrix
    degrees = np.array(W.sum(axis=1)).flatten()
    # Avoid division by zero
    degrees[degrees == 0] = 1.0
    D_inv_sqrt = csr_matrix((1.0 / np.sqrt(degrees), (range(n), range(n))), shape=(n, n))

    # Normalized Laplacian: L = I - D^{-1/2} W D^{-1/2}
    # We compute D^{-1/2} W D^{-1/2} and then eigenvalues of L = I - that
    normalized_W = D_inv_sqrt @ W @ D_inv_sqrt

    # Compute largest eigenvalues of normalized_W (= smallest of L)
    # Request n_eigs + 1 to account for the trivial eigenvalue
    k = min(n_eigs + 1, n - 2)
    print(f"  Computing {k} eigenvalues of normalized adjacency ({n}x{n})...")
    eigvals = eigsh(normalized_W, k=k, which="LM", return_eigenvectors=False)
    eigvals = np.sort(eigvals)[::-1]  # descending

    # Convert to Laplacian eigenvalues: lambda_L = 1 - lambda_W
    laplacian_eigs = 1.0 - eigvals
    laplacian_eigs = np.sort(laplacian_eigs)  # ascending
    return laplacian_eigs


def fit_spectral_dimension(eigenvalues):
    """
    Fit spectral dimension from the eigenvalue counting function.

    For a d-dimensional space, the integrated density of states (eigenvalue
    counting function) satisfies Weyl's law: N(lambda) ~ lambda^{d/2}.

    Equivalently, if we order eigenvalues lambda_1 <= lambda_2 <= ...,
    then lambda_i ~ i^{2/d} (eigenvalues GROW as a power of index).

    We fit: log(lambda_i) = beta * log(i) + c, where beta = 2/d.

    Also fit via heat kernel: K(t) = sum_i exp(-lambda_i * t) ~ t^{-d/2}.
    """
    # Skip zero eigenvalue(s)
    eigs = eigenvalues[eigenvalues > 1e-10]
    n = len(eigs)
    if n < 10:
        return None, None, None, None

    indices = np.arange(1, n + 1, dtype=np.float64)
    log_i = np.log(indices)
    log_eig = np.log(eigs)

    # === Method 1: Weyl's law (counting function) ===
    # Fit: log(lambda) = beta * log(i) + c, where beta = 2/d
    def power_law(log_x, beta, c):
        return beta * log_x + c

    weyl_result = {}
    try:
        start = max(1, n // 20)
        end = min(n, int(0.8 * n))
        popt, pcov = curve_fit(power_law, log_i[start:end], log_eig[start:end])
        beta = popt[0]
        d_weyl = 2.0 / beta if beta > 0 else np.inf

        predicted = power_law(log_i[start:end], *popt)
        ss_res = np.sum((log_eig[start:end] - predicted) ** 2)
        ss_tot = np.sum((log_eig[start:end] - np.mean(log_eig[start:end])) ** 2)
        r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

        weyl_result = {"d": d_weyl, "beta": beta, "r_squared": r_squared}
    except Exception as e:
        print(f"  Weyl fit failed: {e}")

    # === Method 2: Heat kernel return probability ===
    # K(t) = sum exp(-lambda_i * t), fit K(t) ~ C * t^{-d/2}
    t_vals = np.logspace(-2, 2, 200)
    K_vals = np.array([np.sum(np.exp(-eigs * t)) for t in t_vals])
    # Only fit where K(t) is in a reasonable range
    valid = (K_vals > 1) & (K_vals < 0.9 * n)
    heat_result = {}
    if np.sum(valid) > 20:
        log_t = np.log(t_vals[valid])
        log_K = np.log(K_vals[valid])
        try:
            def heat_model(lt, gamma, c):
                return -gamma * lt + c
            popt, _ = curve_fit(heat_model, log_t, log_K)
            gamma_fit = popt[0]
            d_heat = 2.0 * gamma_fit

            predicted = heat_model(log_t, *popt)
            ss_res = np.sum((log_K - predicted) ** 2)
            ss_tot = np.sum((log_K - np.mean(log_K)) ** 2)
            r2_heat = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

            heat_result = {"d": d_heat, "gamma": gamma_fit, "r_squared": r2_heat}
        except Exception as e:
            print(f"  Heat kernel fit failed: {e}")

    # Best estimate: prefer heat kernel if good fit, else Weyl
    d_best = None
    method_best = None
    if heat_result and heat_result.get("r_squared", 0) > 0.9:
        d_best = heat_result["d"]
        method_best = "heat_kernel"
    elif weyl_result and weyl_result.get("r_squared", 0) > 0.7:
        d_best = weyl_result["d"]
        method_best = "weyl_law"

    return d_best, method_best, weyl_result, heat_result


def marchenko_pastur_test(eigenvalues, n_sequences, n_features):
    """
    Compare eigenvalue distribution to Marchenko-Pastur law.
    MP applies to random matrices: bulk in [lambda_-, lambda_+].
    """
    gamma = n_features / n_sequences  # aspect ratio
    lambda_plus = (1 + np.sqrt(gamma)) ** 2
    lambda_minus = (1 - np.sqrt(gamma)) ** 2

    # Normalize eigenvalues to compare with MP
    eigs = eigenvalues[eigenvalues > 1e-10]
    if len(eigs) == 0:
        return {}

    eig_mean = np.mean(eigs)
    eig_normalized = eigs / eig_mean if eig_mean > 0 else eigs

    # Fraction of eigenvalues inside MP bulk
    in_bulk = np.sum((eig_normalized >= lambda_minus) & (eig_normalized <= lambda_plus))
    frac_in_bulk = float(in_bulk) / len(eig_normalized)

    # Fraction above MP edge (structured / signal)
    above_edge = np.sum(eig_normalized > lambda_plus)
    frac_above = float(above_edge) / len(eig_normalized)

    # Tracy-Widom: largest eigenvalue vs MP edge
    tw_ratio = float(np.max(eig_normalized) / lambda_plus) if lambda_plus > 0 else 0

    return {
        "gamma": float(gamma),
        "mp_lambda_minus": float(lambda_minus),
        "mp_lambda_plus": float(lambda_plus),
        "frac_in_mp_bulk": round(frac_in_bulk, 4),
        "frac_above_mp_edge": round(frac_above, 4),
        "n_above_mp_edge": int(above_edge),
        "tw_ratio_largest_to_edge": round(tw_ratio, 4),
        "verdict": "STRUCTURED" if frac_above > 0.1 else "RANDOM-LIKE"
    }


def main():
    t0 = time.time()
    print("F10: OEIS Spectral Clustering Dimension")
    print("=" * 50)

    # 1. Parse sequences
    print(f"\n[1] Parsing OEIS sequences (min {MIN_TERMS} terms, max {N_SEQUENCES})...")
    sequences = parse_oeis(DATA_FILE, MIN_TERMS, N_SEQUENCES)
    print(f"  Loaded {len(sequences)} sequences")

    seq_ids = list(sequences.keys())
    seq_vals = [sequences[s] for s in seq_ids]
    term_counts = [len(v) for v in seq_vals]
    print(f"  Term counts: min={min(term_counts)}, median={int(np.median(term_counts))}, max={max(term_counts)}")

    # 2. Compute FFT signatures
    print(f"\n[2] Computing {FFT_DIM}-dim FFT power spectra...")
    signatures = np.array([compute_fft_signature(v, FFT_DIM) for v in seq_vals])
    print(f"  Signature matrix: {signatures.shape}")

    # Check for degenerate signatures (all-zero)
    zero_sigs = np.sum(np.all(signatures == 0, axis=1))
    print(f"  Zero signatures: {zero_sigs} / {len(signatures)}")

    # 3. Build k-NN graph
    print(f"\n[3] Building k-NN graph (k={K_NN})...")
    W = build_knn_graph(signatures, K_NN)
    n_edges = W.nnz // 2  # symmetric
    print(f"  Edges: {n_edges}, density: {n_edges / (len(seq_ids) * (len(seq_ids) - 1) / 2):.4f}")

    # 4. Compute Laplacian eigenvalues
    print(f"\n[4] Computing normalized Laplacian eigenvalues...")
    eigenvalues = normalized_laplacian_eigenvalues(W, N_EIGENVALUES)
    print(f"  Eigenvalue range: [{eigenvalues[0]:.6f}, {eigenvalues[-1]:.6f}]")
    print(f"  Near-zero eigenvalues (<1e-6): {np.sum(eigenvalues < 1e-6)}")

    # 5. Fit spectral dimension
    print(f"\n[5] Fitting spectral dimension...")
    d_best, method_best, weyl_result, heat_result = fit_spectral_dimension(eigenvalues)
    if weyl_result:
        print(f"  Weyl's law: d = {weyl_result['d']:.3f}, beta = {weyl_result['beta']:.4f}, R^2 = {weyl_result['r_squared']:.4f}")
    if heat_result:
        print(f"  Heat kernel: d = {heat_result['d']:.3f}, gamma = {heat_result['gamma']:.4f}, R^2 = {heat_result['r_squared']:.4f}")
    if d_best is not None:
        print(f"  Best estimate: d = {d_best:.3f} (via {method_best})")
    else:
        print("  No reliable fit.")

    # 6. Marchenko-Pastur test
    print(f"\n[6] Marchenko-Pastur (random matrix) test...")
    mp_result = marchenko_pastur_test(eigenvalues, N_SEQUENCES, FFT_DIM)
    for k, v in mp_result.items():
        print(f"  {k}: {v}")

    # 6b. Local slope analysis (scale-dependent dimension)
    print(f"\n[6b] Local spectral dimension (sliding window)...")
    eigs_nz = eigenvalues[eigenvalues > 1e-10]
    local_dims = []
    window = 30
    for i in range(0, len(eigs_nz) - window, window // 2):
        chunk = eigs_nz[i:i + window]
        idx = np.arange(i + 1, i + 1 + len(chunk), dtype=np.float64)
        log_i = np.log(idx)
        log_e = np.log(chunk)
        # Local slope beta = d(log lambda)/d(log i) => d_local = 2/beta
        if np.std(log_i) > 0:
            beta_local = np.polyfit(log_i, log_e, 1)[0]
            d_local = 2.0 / beta_local if beta_local > 0.01 else np.inf
            local_dims.append({"eigenvalue_index": int(i + window // 2),
                               "d_local": round(float(d_local), 2),
                               "beta_local": round(float(beta_local), 4)})
    if local_dims:
        d_locals = [x["d_local"] for x in local_dims if x["d_local"] < 100]
        if d_locals:
            print(f"  Local d range: [{min(d_locals):.1f}, {max(d_locals):.1f}]")
            print(f"  Local d median: {float(np.median(d_locals)):.1f}")

    # 7. Additional structure analysis
    print(f"\n[7] Eigenvalue structure analysis...")
    eigs_nz = eigenvalues[eigenvalues > 1e-10]

    # Spectral gap
    spectral_gap = float(eigs_nz[0]) if len(eigs_nz) > 0 else 0.0
    print(f"  Spectral gap (smallest nonzero): {spectral_gap:.6f}")

    # Eigenvalue spacing statistics
    spacings = np.diff(eigs_nz)
    mean_spacing = float(np.mean(spacings))
    normalized_spacings = spacings / mean_spacing if mean_spacing > 0 else spacings
    # Level repulsion: Wigner-Dyson has <s> ~ pi/2 * s * exp(-pi/4 * s^2)
    # Poisson (uncorrelated) has <s> ~ exp(-s)
    # Ratio of variance to mean^2: Poisson = 1, GUE ~ 0.178
    spacing_var_ratio = float(np.var(normalized_spacings))
    print(f"  Spacing variance ratio: {spacing_var_ratio:.4f} (Poisson=1.0, GUE~0.178)")

    # Number of clusters (eigenvalues near zero)
    n_clusters_01 = int(np.sum(eigenvalues < 0.1))
    n_clusters_001 = int(np.sum(eigenvalues < 0.01))
    print(f"  Eigenvalues < 0.1: {n_clusters_01} (proxy for cluster count)")
    print(f"  Eigenvalues < 0.01: {n_clusters_001}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Eigenvalue percentiles for the report
    eig_percentiles = {}
    for p in [10, 25, 50, 75, 90]:
        eig_percentiles[f"p{p}"] = round(float(np.percentile(eigs_nz, p)), 6) if len(eigs_nz) > 0 else None

    # Assemble results
    results = {
        "problem": "F10: OEIS Spectral Clustering Dimension",
        "method": {
            "n_sequences": len(sequences),
            "min_terms": MIN_TERMS,
            "fft_dim": FFT_DIM,
            "k_nn": K_NN,
            "n_eigenvalues_computed": len(eigenvalues),
            "zero_signatures": int(zero_sigs),
            "term_count_stats": {
                "min": int(min(term_counts)),
                "median": int(np.median(term_counts)),
                "max": int(max(term_counts))
            }
        },
        "spectral_dimension": {
            "d_effective": round(d_best, 4) if d_best is not None else None,
            "best_method": method_best,
            "weyl_law_fit": {k: round(v, 6) if isinstance(v, float) else v for k, v in weyl_result.items()} if weyl_result else None,
            "heat_kernel_fit": {k: round(v, 6) if isinstance(v, float) else v for k, v in heat_result.items()} if heat_result else None,
            "interpretation": (
                f"Eigenvalue spectrum consistent with d ~ {d_best:.1f} effective dimensions (via {method_best})"
                if d_best is not None else "No reliable power-law fit"
            )
        },
        "graph_stats": {
            "n_edges": n_edges,
            "density": round(n_edges / (len(seq_ids) * (len(seq_ids) - 1) / 2), 6),
            "spectral_gap": round(spectral_gap, 8),
            "n_near_zero_eigenvalues": int(np.sum(eigenvalues < 1e-6)),
            "eigenvalue_range": [round(float(eigenvalues[0]), 8), round(float(eigenvalues[-1]), 8)]
        },
        "marchenko_pastur": mp_result,
        "eigenvalue_structure": {
            "spacing_variance_ratio": round(spacing_var_ratio, 4),
            "spacing_interpretation": (
                "Wigner-Dyson (correlated)" if spacing_var_ratio < 0.5
                else "Poisson-like (uncorrelated)" if spacing_var_ratio > 0.8
                else "Intermediate"
            ),
            "n_eigenvalues_below_0.1": n_clusters_01,
            "n_eigenvalues_below_0.01": n_clusters_001,
            "percentiles": eig_percentiles
        },
        "comparison_to_battery": {
            "battery_effective_dim": "3-4 (from R4-2 PCA/MDS analysis)",
            "oeis_spectral_dim": round(d_best, 1) if d_best is not None else None,
            "assessment": (
                f"OEIS spectral dimension d={d_best:.1f} vs battery d=3-4: "
                + ("CONSISTENT — similar effective dimensionality"
                   if d_best is not None and 2 <= d_best <= 6
                   else "HIGHER — OEIS sequence space is richer than battery feature space"
                   if d_best is not None and d_best > 6
                   else "LOWER — surprising compression"
                   if d_best is not None and d_best < 2
                   else "inconclusive")
            ) if d_best is not None else "inconclusive"
        },
        "local_spectral_dimension": local_dims if local_dims else None,
        "eigenvalues_first_50": [round(float(e), 8) for e in eigenvalues[:50]],
        "elapsed_seconds": round(elapsed, 1)
    }

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")

    return results


if __name__ == "__main__":
    main()
