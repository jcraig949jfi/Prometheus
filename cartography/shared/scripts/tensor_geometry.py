"""
Tensor Geometry — intrinsic geometry of the dissection tensor.

Distinguishes genuine cross-domain structure from projection artifacts
by applying six geometric analyses:

  1. Intrinsic dimensionality estimation (PCA + TWO-NN)
  2. Independent Component Analysis (FastICA)
  3. Random rotation invariance test
  4. Persistent homology (topological features)
  5. Per-domain subspace analysis (Grassmannian principal angles)
  6. Curvature estimation (local PCA)

Reads: cartography/convergence/data/dissection_tensor.pt
Saves: cartography/convergence/data/geometry_results/

Machine: M1 (Skullport), RTX 5060 Ti 17GB VRAM
"""
import sys
import json
import time
import warnings
import numpy as np
import torch
from pathlib import Path
from collections import defaultdict

# Suppress convergence warnings from ICA
warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_DIR = DATA_DIR / "geometry_results"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Strategy groups — mirrors dissection_tensor.py
STRATEGY_GROUPS = {
    "complex":     ["s1_alex", "s1_jones", "s1_ap"],
    "mod_p":       ["s3_alex", "s3_jones", "s3_ap"],
    "spectral":    ["s5_alex", "s5_jones", "s5_ap", "s5_oeis"],
    "padic":       ["s7_det", "s7_disc", "s7_cond"],
    "symmetry":    ["s9_st", "s9_endo"],
    "galois":      ["s10", "s10_galrep"],
    "zeta":        ["s12_ec", "s12_oeis", "s12_nf"],
    "disc_cond":   ["s13"],
    "operadic":    ["s22"],
    "entropy":     ["s24_alex", "s24_arith", "s24_ap", "s24_sym", "s24_oeis"],
    "attractor":   ["s6_oeis"],
    "automorphic": ["s21_auto"],
    "monodromy":   ["s11_mono"],
    "ade":         ["s19_ade"],
}


def load_tensor():
    """Load the dissection tensor and metadata."""
    path = DATA_DIR / "dissection_tensor.pt"
    if not path.exists():
        print(f"ERROR: Tensor not found at {path}")
        print("Run dissection_tensor.py first to build it.")
        sys.exit(1)

    data = torch.load(path, map_location="cpu", weights_only=False)
    tensor = data["tensor"]        # [N, D] float32
    mask = data["mask"]            # [N, D] bool
    labels = data["labels"]        # list of obj_id
    domains = data["domains"]      # list of domain strings
    strategy_slices = data["strategy_slices"]  # name -> (start, end)

    print(f"Loaded tensor: {tensor.shape[0]} objects x {tensor.shape[1]} dims")
    print(f"  Fill rate: {mask.sum().item() / mask.numel() * 100:.1f}%")
    unique_domains = sorted(set(domains))
    print(f"  Domains ({len(unique_domains)}): {', '.join(unique_domains)}")

    # Build domain index
    domain_indices = defaultdict(list)
    for i, d in enumerate(domains):
        domain_indices[d].append(i)

    # Build group slices from strategy slices (or use saved ones)
    if "group_slices" in data and data["group_slices"]:
        group_slices = data["group_slices"]
    else:
        group_slices = {}
        for gname, slist in STRATEGY_GROUPS.items():
            starts = [strategy_slices[s][0] for s in slist if s in strategy_slices]
            ends = [strategy_slices[s][1] for s in slist if s in strategy_slices]
            if starts:
                group_slices[gname] = (min(starts), max(ends))

    return tensor, mask, labels, domains, domain_indices, strategy_slices, group_slices


def compute_group_means(tensor, mask, group_slices):
    """Compute per-object group-level means (masked). Returns [N, G] tensor and validity mask."""
    N = tensor.shape[0]
    group_names = list(group_slices.keys())
    G = len(group_names)
    means = torch.zeros(N, G)
    valid = torch.zeros(N, G, dtype=torch.bool)

    for gi, gname in enumerate(group_names):
        start, end = group_slices[gname]
        vals = tensor[:, start:end]
        m = mask[:, start:end].float()
        has_data = m.sum(dim=1) > 0
        denom = m.sum(dim=1).clamp(min=1)
        means[:, gi] = (vals * m).sum(dim=1) / denom
        valid[:, gi] = has_data

    return means, valid, group_names


def compute_strategy_corr(tensor, mask, group_slices):
    """Compute the strategy-group correlation matrix."""
    means, valid, group_names = compute_group_means(tensor, mask, group_slices)
    G = len(group_names)
    corr = np.zeros((G, G))

    for i in range(G):
        for j in range(i, G):
            shared = valid[:, i] & valid[:, j]
            n = shared.sum().item()
            if n < 10:
                continue
            x = means[shared, i]
            y = means[shared, j]
            mx = x - x.mean()
            my = y - y.mean()
            num = (mx * my).sum()
            den = (mx.norm() * my.norm()).clamp(min=1e-12)
            r = (num / den).item()
            corr[i, j] = r
            corr[j, i] = r

    return corr, group_names


# ============================================================
# Analysis 1: Intrinsic Dimensionality
# ============================================================
def analysis_intrinsic_dim(tensor, mask, domain_indices):
    """PCA + TWO-NN intrinsic dimensionality estimation."""
    print("\n" + "=" * 60)
    print("ANALYSIS 1: INTRINSIC DIMENSIONALITY")
    print("=" * 60)
    results = {}

    # --- Global PCA ---
    print("\n--- Global PCA ---")
    # Use masked tensor (NaN->0 already done)
    T = tensor.numpy()
    N, D = T.shape

    # Subsample if very large for speed
    max_pca = min(N, 50000)
    if N > max_pca:
        idx = np.random.choice(N, max_pca, replace=False)
        T_sub = T[idx]
    else:
        T_sub = T

    # Center
    T_centered = T_sub - T_sub.mean(axis=0)

    # SVD (truncated via numpy for speed — full matrix is 179 dims, very manageable)
    U, S, Vt = np.linalg.svd(T_centered, full_matrices=False)
    var_explained = S ** 2
    var_total = var_explained.sum()
    cumvar = np.cumsum(var_explained) / var_total

    dims_90 = int(np.searchsorted(cumvar, 0.90)) + 1
    dims_95 = int(np.searchsorted(cumvar, 0.95)) + 1
    dims_99 = int(np.searchsorted(cumvar, 0.99)) + 1

    print(f"  Components for 90% variance: {dims_90} / {D}")
    print(f"  Components for 95% variance: {dims_95} / {D}")
    print(f"  Components for 99% variance: {dims_99} / {D}")
    print(f"  Top 10 singular values: {S[:10].round(1)}")

    results["pca_global"] = {
        "dims_90": dims_90, "dims_95": dims_95, "dims_99": dims_99,
        "total_dims": D,
        "top_10_singular_values": S[:10].tolist(),
        "cumulative_variance": cumvar[:30].tolist(),
    }

    # --- TWO-NN estimator (Facco et al. 2017) ---
    print("\n--- TWO-NN Local Intrinsic Dimensionality ---")
    # GPU-accelerated: compute 2nd/1st NN distance ratios
    max_twonn = min(N, 30000)
    if N > max_twonn:
        idx = np.random.choice(N, max_twonn, replace=False)
        T_gpu = tensor[idx].to(DEVICE)
    else:
        T_gpu = tensor.to(DEVICE)

    # Compute pairwise distances in batches to fit in VRAM
    n = T_gpu.shape[0]
    batch_size = min(2000, n)
    mus = []  # distance ratios r2/r1

    print(f"  Computing TWO-NN on {n} points (batched)...")
    for i in range(0, n, batch_size):
        end_i = min(i + batch_size, n)
        batch = T_gpu[i:end_i]  # [B, D]
        # Distances to all other points
        dists = torch.cdist(batch, T_gpu)  # [B, n]
        # Set self-distance to inf
        for bi in range(end_i - i):
            dists[bi, i + bi] = float("inf")
        # Top-2 nearest
        top2, _ = dists.topk(2, dim=1, largest=False)
        r1 = top2[:, 0]
        r2 = top2[:, 1]
        # Avoid division by zero
        valid = r1 > 1e-10
        mu = r2[valid] / r1[valid]
        mus.append(mu.cpu())

    mus = torch.cat(mus).numpy()
    # TWO-NN: mu follows Pareto(d) where d = intrinsic dim
    # MLE for Pareto exponent: d = n / sum(log(mu))
    log_mus = np.log(mus[mus > 1.0])  # mu > 1 by construction for non-degenerate
    if len(log_mus) > 100:
        d_twonn = len(log_mus) / log_mus.sum()
        print(f"  TWO-NN intrinsic dimension: {d_twonn:.2f}")
        print(f"    (from {len(log_mus)} valid distance ratios)")
    else:
        d_twonn = float("nan")
        print(f"  TWO-NN: insufficient valid ratios ({len(log_mus)})")

    results["twonn_global"] = {"intrinsic_dim": float(d_twonn), "n_ratios": len(log_mus)}

    # --- Per-domain PCA ---
    print("\n--- Per-Domain Dimensionality ---")
    domain_dims = {}
    for dname, indices in sorted(domain_indices.items()):
        if len(indices) < 20:
            continue
        T_dom = T[indices]
        T_dom_c = T_dom - T_dom.mean(axis=0)
        _, S_dom, _ = np.linalg.svd(T_dom_c, full_matrices=False)
        var_dom = S_dom ** 2
        cumvar_dom = np.cumsum(var_dom) / var_dom.sum()
        d90 = int(np.searchsorted(cumvar_dom, 0.90)) + 1
        d95 = int(np.searchsorted(cumvar_dom, 0.95)) + 1
        print(f"  {dname:12s}: 90%={d90:3d}, 95%={d95:3d}  (n={len(indices)})")
        domain_dims[dname] = {"dims_90": d90, "dims_95": d95, "n_objects": len(indices)}

    results["per_domain"] = domain_dims

    # --- Interpretation ---
    collapse_ratio = dims_95 / D
    print(f"\n  Collapse ratio (95% dims / total): {collapse_ratio:.3f}")
    if collapse_ratio < 0.15:
        print("  INTERPRETATION: Severe collapse. Most strategies are redundant projections.")
    elif collapse_ratio < 0.35:
        print("  INTERPRETATION: Moderate collapse. Many strategies share information,")
        print("    but some independent structure exists.")
    else:
        print("  INTERPRETATION: Mild collapse. Strategies carry largely independent information.")

    return results


# ============================================================
# Analysis 2: Independent Component Analysis
# ============================================================
def analysis_ica(tensor, mask, group_slices):
    """FastICA to find independent sources among strategy groups."""
    print("\n" + "=" * 60)
    print("ANALYSIS 2: INDEPENDENT COMPONENT ANALYSIS")
    print("=" * 60)

    from sklearn.decomposition import FastICA
    from sklearn.preprocessing import StandardScaler

    # Use group means for ICA (more interpretable than raw 179 dims)
    means, valid, group_names = compute_group_means(tensor, mask, group_slices)

    # Filter to objects with data in at least 5 groups
    min_groups = 5
    n_valid = valid.sum(dim=1)
    good = n_valid >= min_groups
    X = means[good].numpy()
    print(f"  Objects with >= {min_groups} strategy groups: {X.shape[0]}")

    if X.shape[0] < 100:
        print("  ERROR: Too few objects for ICA. Skipping.")
        return {"error": "too_few_objects"}

    # Subsample for speed
    max_ica = min(X.shape[0], 10000)
    if X.shape[0] > max_ica:
        idx = np.random.choice(X.shape[0], max_ica, replace=False)
        X = X[idx]

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Try increasing numbers of components and track reconstruction error
    G = len(group_names)
    max_comp = min(G, X.shape[0] - 1)

    results = {}

    # Run ICA for a range of component counts
    print(f"\n  Testing ICA with 2..{max_comp} components:")
    best_n = None
    for n_comp in range(2, max_comp + 1):
        try:
            ica = FastICA(n_components=n_comp, max_iter=500, tol=0.01,
                          random_state=42, whiten="unit-variance")
            S = ica.fit_transform(X_scaled)
            A = ica.mixing_  # [G, n_comp] mixing matrix

            # Measure: fraction of variance explained by reconstruction
            X_recon = S @ A.T
            recon_var = 1.0 - np.var(X_scaled - X_recon) / np.var(X_scaled)
            converged = ica.n_iter_ < 500

            tag = "*" if converged else "?"
            print(f"    n={n_comp:2d}: recon_var={recon_var:.4f}, iters={ica.n_iter_:3d} {tag}")

            if converged and best_n is None and recon_var > 0.95:
                best_n = n_comp

        except Exception as e:
            print(f"    n={n_comp:2d}: FAILED ({e})")

    # Run final ICA at best component count
    if best_n is None:
        best_n = max_comp
    print(f"\n  Selected {best_n} independent components (first to exceed 95% recon variance)")

    ica_final = FastICA(n_components=best_n, max_iter=1000, tol=0.001,
                        random_state=42, whiten="unit-variance")
    S_final = ica_final.fit_transform(X_scaled)
    A_final = ica_final.mixing_  # [G, best_n]

    # Analyze which groups load on which component
    print(f"\n  Mixing matrix (strategy group -> independent component):")
    print(f"  {'Group':14s}" + "".join(f"  IC{c+1:2d}" for c in range(best_n)))
    loadings = {}
    for gi, gname in enumerate(group_names):
        row = A_final[gi, :]
        row_str = "".join(f"{v:7.3f}" for v in row)
        # Mark dominant component
        dom_ic = int(np.argmax(np.abs(row))) + 1
        print(f"  {gname:14s}{row_str}  <- IC{dom_ic}")
        loadings[gname] = {"dominant_ic": dom_ic, "weights": row.tolist()}

    # Group strategy groups by dominant IC
    ic_groups = defaultdict(list)
    for gname, info in loadings.items():
        ic_groups[info["dominant_ic"]].append(gname)

    print(f"\n  Independent sources ({best_n}):")
    for ic_num in sorted(ic_groups.keys()):
        members = ic_groups[ic_num]
        print(f"    IC{ic_num}: {', '.join(members)}")

    results = {
        "n_independent_components": best_n,
        "n_strategy_groups": G,
        "loadings": loadings,
        "ic_groups": {str(k): v for k, v in ic_groups.items()},
    }

    if best_n < G * 0.5:
        print(f"\n  INTERPRETATION: {G} strategy groups decompose into {best_n} independent sources.")
        print(f"    The 'phonemes' are partially redundant — real independent dimensions = {best_n}.")
    else:
        print(f"\n  INTERPRETATION: {best_n}/{G} independent components needed — most groups carry")
        print(f"    distinct information. The strategy decomposition is largely non-redundant.")

    return results


# ============================================================
# Analysis 3: Random Rotation Invariance Test
# ============================================================
def analysis_rotation_invariance(tensor, mask, group_slices, n_rotations=100):
    """Test if correlation structure survives random rotation."""
    print("\n" + "=" * 60)
    print("ANALYSIS 3: RANDOM ROTATION INVARIANCE")
    print("=" * 60)
    print(f"  Generating {n_rotations} random orthogonal rotations...")

    N, D = tensor.shape

    # Subsample for speed (correlation on 397K x 100 rotations is slow)
    max_rot_sample = 30000
    if N > max_rot_sample:
        sub_idx = np.random.choice(N, max_rot_sample, replace=False)
        T_sub = tensor[sub_idx]
        M_sub = mask[sub_idx]
        print(f"  Subsampled to {max_rot_sample} objects for rotation test")
    else:
        T_sub = tensor
        M_sub = mask

    # Compute original correlation matrix
    orig_corr, group_names = compute_strategy_corr(T_sub, M_sub, group_slices)
    print(f"  Original correlation matrix computed ({len(group_names)}x{len(group_names)})")

    # Generate random rotations and measure correlation change
    frob_norms = []

    # Work on GPU for rotation, CPU for correlation
    T_gpu = T_sub.to(DEVICE)

    for rot_i in range(n_rotations):
        # Random orthogonal matrix via QR on random Gaussian
        Z = torch.randn(D, D, device=DEVICE)
        Q, R = torch.linalg.qr(Z)
        # Ensure proper rotation (det = +1)
        diag_sign = torch.sign(torch.diag(R))
        Q = Q * diag_sign.unsqueeze(0)

        # Rotate the tensor
        T_rot = T_gpu @ Q  # [N, D] @ [D, D] -> [N, D]

        # Recompute correlation on CPU
        T_rot_cpu = T_rot.cpu()
        # Mask doesn't change structure — same entries are "valid"
        rot_corr, _ = compute_strategy_corr(T_rot_cpu, M_sub, group_slices)

        # Frobenius distance
        diff = orig_corr - rot_corr
        frob = np.sqrt((diff ** 2).sum())
        frob_norms.append(frob)

        if (rot_i + 1) % 20 == 0:
            print(f"    Rotation {rot_i + 1}/{n_rotations}: Frobenius = {frob:.4f}")

    frob_norms = np.array(frob_norms)

    print(f"\n  Frobenius distance statistics ({n_rotations} rotations):")
    print(f"    Mean:   {frob_norms.mean():.4f}")
    print(f"    Std:    {frob_norms.std():.4f}")
    print(f"    Min:    {frob_norms.min():.4f}")
    print(f"    Max:    {frob_norms.max():.4f}")
    print(f"    Median: {np.median(frob_norms):.4f}")

    # For reference: max possible Frobenius of a GxG correlation matrix
    G = len(group_names)
    max_frob = np.sqrt(2 * G * (G - 1))  # all off-diagonal change from +1 to -1
    orig_frob = np.sqrt((orig_corr ** 2).sum())

    relative_change = frob_norms.mean() / orig_frob if orig_frob > 0 else float("inf")
    print(f"\n    Original corr Frobenius norm: {orig_frob:.4f}")
    print(f"    Mean change / original:      {relative_change:.4f} ({relative_change*100:.1f}%)")

    results = {
        "n_rotations": n_rotations,
        "frob_mean": float(frob_norms.mean()),
        "frob_std": float(frob_norms.std()),
        "frob_min": float(frob_norms.min()),
        "frob_max": float(frob_norms.max()),
        "original_frob": float(orig_frob),
        "relative_change": float(relative_change),
    }

    if relative_change < 0.1:
        print(f"\n  INTERPRETATION: Correlation structure SURVIVES rotation (<10% change).")
        print(f"    This is GENUINE intrinsic structure, not a coordinate artifact.")
        results["verdict"] = "genuine"
    elif relative_change < 0.5:
        print(f"\n  INTERPRETATION: Correlation structure PARTIALLY survives rotation.")
        print(f"    Some structure is intrinsic, some is coordinate-dependent.")
        results["verdict"] = "mixed"
    else:
        print(f"\n  INTERPRETATION: Correlation structure DESTROYED by rotation (>{relative_change*100:.0f}% change).")
        print(f"    This is a PROJECTION ARTIFACT of the particular coordinate system.")
        results["verdict"] = "artifact"

    return results


# ============================================================
# Analysis 4: Persistent Homology
# ============================================================
def analysis_persistent_homology(tensor, mask, n_sample=3000):
    """Compute persistent homology to find topological features."""
    print("\n" + "=" * 60)
    print("ANALYSIS 4: PERSISTENT HOMOLOGY")
    print("=" * 60)

    N = tensor.shape[0]

    # Sample points (keep moderate for ripser memory/time)
    if N > n_sample:
        idx = np.random.choice(N, n_sample, replace=False)
        T_sample = tensor[idx]
    else:
        T_sample = tensor
        n_sample = N

    print(f"  Sampling {n_sample} points for topology...")

    # Compute pairwise distances on GPU
    T_gpu = T_sample.to(DEVICE)
    print(f"  Computing pairwise distances on GPU...")
    dist_matrix = torch.cdist(T_gpu, T_gpu).cpu().numpy().astype(np.float32)
    del T_gpu
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    # Try ripser
    try:
        import ripser
        # H2 on large point clouds can be expensive; try H0+H1 first, then H2 if fast
        print(f"  Running ripser (H0, H1)...")
        t0 = time.time()
        result = ripser.ripser(dist_matrix, maxdim=1, distance_matrix=True)
        elapsed_h1 = time.time() - t0
        print(f"  H0+H1 completed in {elapsed_h1:.1f}s")

        # If H1 was fast enough, try H2
        if elapsed_h1 < 120 and n_sample <= 3000:
            try:
                print(f"  Running ripser H2...")
                t0 = time.time()
                result = ripser.ripser(dist_matrix, maxdim=2, distance_matrix=True)
                print(f"  H2 completed in {time.time() - t0:.1f}s")
            except Exception as e2:
                print(f"  H2 failed ({e2}), using H0+H1 only")

        diagrams = result["dgms"]
        betti = {}
        persistence_stats = {}

        for dim_i, dgm in enumerate(diagrams):
            if len(dgm) == 0:
                betti[dim_i] = 0
                continue

            # Filter out infinite-death features for stats
            finite = dgm[dgm[:, 1] < np.inf]
            infinite = dgm[dgm[:, 1] == np.inf]

            # Persistence = death - birth
            if len(finite) > 0:
                pers = finite[:, 1] - finite[:, 0]
                # Significant features: persistence > median
                median_pers = np.median(pers) if len(pers) > 0 else 0
                significant = int((pers > 2 * median_pers).sum())
            else:
                pers = np.array([])
                significant = 0

            label = {0: "components", 1: "loops", 2: "voids"}.get(dim_i, f"H{dim_i}")
            n_feat = len(finite) + len(infinite)
            print(f"\n  H{dim_i} ({label}):")
            print(f"    Total features: {n_feat}")
            print(f"    Finite features: {len(finite)}")
            if len(finite) > 0:
                print(f"    Persistence: mean={pers.mean():.4f}, max={pers.max():.4f}, median={np.median(pers):.4f}")
                print(f"    Significant (>2x median): {significant}")

            # Long-lived features are the topological signature
            betti[dim_i] = significant
            persistence_stats[f"H{dim_i}"] = {
                "total": n_feat,
                "finite": len(finite),
                "significant": significant,
                "mean_persistence": float(pers.mean()) if len(pers) > 0 else 0,
                "max_persistence": float(pers.max()) if len(pers) > 0 else 0,
            }

        results = {
            "method": "ripser",
            "n_points": n_sample,
            "betti_significant": betti,
            "persistence": persistence_stats,
        }

        print(f"\n  Significant Betti numbers: b0={betti.get(0,0)}, b1={betti.get(1,0)}, b2={betti.get(2,0)}")
        if betti.get(1, 0) > 0 or betti.get(2, 0) > 0:
            print(f"  INTERPRETATION: Non-trivial topology detected (loops/voids).")
            print(f"    These are REAL structural features that survive any rotation.")
            results["verdict"] = "genuine_topology"
        else:
            print(f"  INTERPRETATION: No persistent loops or voids. Topology is trivial.")
            print(f"    Structure (if any) is metric, not topological.")
            results["verdict"] = "trivial_topology"

        return results

    except Exception as e:
        print(f"  Ripser failed: {e}")
        print(f"  Falling back to manual Vietoris-Rips filtration (H0 only)...")
        return _manual_vr_filtration(dist_matrix, n_sample)


def _manual_vr_filtration(dist_matrix, n_sample):
    """Manual connected-component tracking as fallback for topology."""
    # Union-Find for H0
    parent = list(range(n_sample))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            return True
        return False

    # Get all pairwise distances sorted
    triu_idx = np.triu_indices(n_sample, k=1)
    dists = dist_matrix[triu_idx]
    order = np.argsort(dists)

    # Track component merges
    birth_death = []
    n_components = n_sample
    thresholds = np.linspace(0, np.percentile(dists, 50), 100)

    components_at_threshold = []
    for t in thresholds:
        # Count edges at this threshold
        edges_below = dists <= t
        # Use union-find (reset each time for simplicity)
        p = list(range(n_sample))

        def find2(x):
            while p[x] != x:
                p[x] = p[p[x]]
                x = p[x]
            return x

        for idx in np.where(edges_below)[0]:
            i, j = triu_idx[0][idx], triu_idx[1][idx]
            ri, rj = find2(i), find2(j)
            if ri != rj:
                p[ri] = rj

        n_comp = len(set(find2(x) for x in range(n_sample)))
        components_at_threshold.append((float(t), n_comp))

    print(f"  Components at threshold 0: {n_sample}")
    for t, nc in components_at_threshold[::20]:
        print(f"  Components at threshold {t:.4f}: {nc}")

    return {
        "method": "manual_vr",
        "n_points": n_sample,
        "filtration": components_at_threshold,
        "verdict": "h0_only",
    }


# ============================================================
# Analysis 5: Per-Domain Subspace Analysis (Grassmannian)
# ============================================================
def analysis_grassmannian(tensor, mask, domain_indices):
    """Compute principal angles between domain subspaces."""
    print("\n" + "=" * 60)
    print("ANALYSIS 5: GRASSMANNIAN SUBSPACE ANALYSIS")
    print("=" * 60)

    domains = sorted([d for d, idx in domain_indices.items() if len(idx) >= 20])
    print(f"  Domains with >= 20 objects: {len(domains)}")

    T = tensor.numpy()

    # For each domain, compute principal subspace (top-k PCA capturing 90% variance)
    domain_subspaces = {}
    domain_k = {}
    for dname in domains:
        indices = domain_indices[dname]
        T_dom = T[indices]
        T_dom_c = T_dom - T_dom.mean(axis=0)
        U, S, Vt = np.linalg.svd(T_dom_c, full_matrices=False)
        var = S ** 2
        cumvar = np.cumsum(var) / var.sum()
        k = int(np.searchsorted(cumvar, 0.90)) + 1
        k = min(k, len(S))
        # Principal subspace = first k rows of Vt
        domain_subspaces[dname] = Vt[:k, :]  # [k, D]
        domain_k[dname] = k
        print(f"  {dname:12s}: subspace dim = {k} (for 90% variance, n={len(indices)})")

    # Compute principal angles between all domain pairs
    n_domains = len(domains)
    # Store minimum principal angle (most aligned direction) for each pair
    min_angle_matrix = np.full((n_domains, n_domains), np.pi / 2)
    mean_angle_matrix = np.full((n_domains, n_domains), np.pi / 2)

    print(f"\n  Computing principal angles between {n_domains} domain pairs...")
    for i in range(n_domains):
        min_angle_matrix[i, i] = 0.0
        mean_angle_matrix[i, i] = 0.0
        for j in range(i + 1, n_domains):
            A = domain_subspaces[domains[i]]  # [k_i, D]
            B = domain_subspaces[domains[j]]  # [k_j, D]

            # Principal angles via SVD of A @ B^T
            # Singular values = cos(principal angles)
            M = A @ B.T  # [k_i, k_j]
            _, sigmas, _ = np.linalg.svd(M, full_matrices=False)
            # Clamp to [0, 1] for numerical safety
            sigmas = np.clip(sigmas, 0, 1)
            angles = np.arccos(sigmas)  # principal angles in radians

            min_angle = float(angles.min()) if len(angles) > 0 else np.pi / 2
            mean_angle = float(angles.mean()) if len(angles) > 0 else np.pi / 2

            min_angle_matrix[i, j] = min_angle
            min_angle_matrix[j, i] = min_angle
            mean_angle_matrix[i, j] = mean_angle
            mean_angle_matrix[j, i] = mean_angle

    # Print minimum angle matrix (degrees)
    print(f"\n  Minimum principal angle between domain subspaces (degrees):")
    print(f"  {'':12s}" + "".join(f"{d:>8s}" for d in domains))
    for i, di in enumerate(domains):
        row = "".join(f"{np.degrees(min_angle_matrix[i, j]):8.1f}" for j in range(n_domains))
        print(f"  {di:12s}{row}")

    # Identify overlapping subspaces (angle < 15 degrees)
    print(f"\n  Domain pairs with smallest principal angle < 15 degrees (high overlap):")
    bridges = []
    for i in range(n_domains):
        for j in range(i + 1, n_domains):
            angle_deg = np.degrees(min_angle_matrix[i, j])
            if angle_deg < 15:
                bridges.append((domains[i], domains[j], angle_deg))
                print(f"    {domains[i]:12s} <-> {domains[j]:12s}: {angle_deg:.1f} deg  ** BRIDGE")

    if not bridges:
        print(f"    (none)")

    # Orthogonal pairs (angle > 75 degrees)
    print(f"\n  Domain pairs with minimum angle > 75 degrees (orthogonal / no bridge):")
    ortho_pairs = []
    for i in range(n_domains):
        for j in range(i + 1, n_domains):
            angle_deg = np.degrees(min_angle_matrix[i, j])
            if angle_deg > 75:
                ortho_pairs.append((domains[i], domains[j], angle_deg))
                print(f"    {domains[i]:12s} <-> {domains[j]:12s}: {angle_deg:.1f} deg")

    if not ortho_pairs:
        print(f"    (none)")

    results = {
        "domains": domains,
        "subspace_dims": domain_k,
        "min_angle_matrix_deg": np.degrees(min_angle_matrix).tolist(),
        "mean_angle_matrix_deg": np.degrees(mean_angle_matrix).tolist(),
        "bridges_lt_15deg": [(a, b, float(ang)) for a, b, ang in bridges],
        "orthogonal_gt_75deg": [(a, b, float(ang)) for a, b, ang in ortho_pairs],
    }

    n_bridges = len(bridges)
    n_ortho = len(ortho_pairs)
    total_pairs = n_domains * (n_domains - 1) // 2
    print(f"\n  Summary: {n_bridges} bridges, {n_ortho} orthogonal, out of {total_pairs} pairs")

    if n_bridges > total_pairs * 0.3:
        print(f"  INTERPRETATION: Many overlapping subspaces. Domains share geometric structure.")
        results["verdict"] = "shared_subspaces"
    elif n_bridges > 0:
        print(f"  INTERPRETATION: Selective overlap. Some domain bridges are geometrically real,")
        print(f"    others are orthogonal (independent structure, not projections of each other).")
        results["verdict"] = "selective_bridges"
    else:
        print(f"  INTERPRETATION: All domains occupy orthogonal subspaces.")
        print(f"    Any apparent proximity is a projection artifact.")
        results["verdict"] = "orthogonal_domains"

    return results


# ============================================================
# Analysis 6: Curvature Estimation
# ============================================================
def analysis_curvature(tensor, mask, domain_indices, n_points=1000, k_neighbors=50):
    """Estimate local dimensionality and curvature via local PCA."""
    print("\n" + "=" * 60)
    print("ANALYSIS 6: CURVATURE ESTIMATION")
    print("=" * 60)

    N, D = tensor.shape
    n_points = min(n_points, N)

    # Random sample of center points
    centers_idx = np.random.choice(N, n_points, replace=False)

    T_gpu = tensor.to(DEVICE)
    k = min(k_neighbors, N - 1)

    print(f"  Estimating local dimension at {n_points} points (k={k} neighbors)...")

    local_dims = []
    local_dims_90 = []
    domain_of_center = []

    # Process in batches
    batch_size = 200
    domains_arr = np.array([domain_indices])  # won't use directly

    for bi in range(0, n_points, batch_size):
        end_bi = min(bi + batch_size, n_points)
        batch_idx = centers_idx[bi:end_bi]
        batch_points = T_gpu[batch_idx]  # [B, D]

        # Find k nearest neighbors
        dists = torch.cdist(batch_points, T_gpu)  # [B, N]
        # Exclude self
        for local_i, global_i in enumerate(batch_idx):
            dists[local_i, global_i] = float("inf")

        _, nn_idx = dists.topk(k, dim=1, largest=False)  # [B, k]

        for local_i in range(end_bi - bi):
            neighbors = T_gpu[nn_idx[local_i]].cpu().numpy()  # [k, D]
            center = batch_points[local_i].cpu().numpy()  # [D]

            # Local PCA
            local_data = neighbors - center
            try:
                _, S_local, _ = np.linalg.svd(local_data, full_matrices=False)
                var_local = S_local ** 2
                cumvar = np.cumsum(var_local) / var_local.sum()
                d90 = int(np.searchsorted(cumvar, 0.90)) + 1
                d95 = int(np.searchsorted(cumvar, 0.95)) + 1
                local_dims.append(d95)
                local_dims_90.append(d90)
            except Exception:
                pass

    local_dims = np.array(local_dims)
    local_dims_90 = np.array(local_dims_90)

    if len(local_dims) == 0:
        print("  ERROR: Could not compute any local dimensions.")
        return {"error": "no_local_dims"}

    print(f"\n  Local dimension statistics (95% variance threshold):")
    print(f"    Mean:   {local_dims.mean():.1f}")
    print(f"    Median: {np.median(local_dims):.1f}")
    print(f"    Std:    {local_dims.std():.1f}")
    print(f"    Min:    {local_dims.min()}")
    print(f"    Max:    {local_dims.max()}")

    print(f"\n  Local dimension statistics (90% variance threshold):")
    print(f"    Mean:   {local_dims_90.mean():.1f}")
    print(f"    Median: {np.median(local_dims_90):.1f}")

    # Histogram
    bins = np.arange(0, local_dims.max() + 2) - 0.5
    hist, edges = np.histogram(local_dims, bins=bins)
    print(f"\n  Local dimension histogram (95%):")
    for i, count in enumerate(hist):
        if count > 0:
            bar = "#" * min(count * 50 // n_points, 50)
            print(f"    dim={i:3d}: {count:5d} ({count/len(local_dims)*100:5.1f}%) {bar}")

    # Compare local vs global
    global_dim = D
    ratio = local_dims.mean() / global_dim

    results = {
        "n_points": n_points,
        "k_neighbors": k,
        "local_dim_95_mean": float(local_dims.mean()),
        "local_dim_95_median": float(np.median(local_dims)),
        "local_dim_95_std": float(local_dims.std()),
        "local_dim_90_mean": float(local_dims_90.mean()),
        "local_dim_90_median": float(np.median(local_dims_90)),
        "global_dim": global_dim,
        "ratio_local_global": float(ratio),
        "histogram": {str(int(edges[i]+0.5)): int(hist[i]) for i in range(len(hist)) if hist[i] > 0},
    }

    # Per-domain curvature (using the domains of the center points)
    # Build reverse lookup: object index -> domain
    idx_to_domain = {}
    for dname, indices in domain_indices.items():
        for idx in indices:
            idx_to_domain[idx] = dname

    all_domains_arr = [idx_to_domain.get(ci, "unknown") for ci in centers_idx[:len(local_dims)]]

    print(f"\n  Per-domain local dimension (95% threshold):")
    domain_local_dims = defaultdict(list)
    for d, ld in zip(all_domains_arr, local_dims):
        domain_local_dims[d].append(ld)

    for dname in sorted(domain_local_dims.keys()):
        vals = np.array(domain_local_dims[dname])
        if len(vals) >= 5:
            print(f"    {dname:12s}: mean={vals.mean():.1f}, median={np.median(vals):.1f} (n={len(vals)})")

    if ratio < 0.3:
        print(f"\n  INTERPRETATION: Local dim << global dim (ratio={ratio:.2f}).")
        print(f"    The manifold is CURVED — genuinely nonlinear structure.")
        results["verdict"] = "curved"
    elif ratio < 0.7:
        print(f"\n  INTERPRETATION: Local dim moderately lower than global (ratio={ratio:.2f}).")
        print(f"    Some nonlinear structure, but partly flat.")
        results["verdict"] = "mixed_curvature"
    else:
        print(f"\n  INTERPRETATION: Local dim ~ global dim (ratio={ratio:.2f}).")
        print(f"    The manifold is approximately FLAT — structure is linear.")
        results["verdict"] = "flat"

    return results


# ============================================================
# Final Verdict
# ============================================================
def final_verdict(all_results):
    """Synthesize all analyses into a final verdict."""
    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)

    evidence_genuine = 0
    evidence_artifact = 0
    evidence_mixed = 0

    # 1. Dimensionality
    pca = all_results.get("intrinsic_dim", {}).get("pca_global", {})
    if pca:
        ratio = pca.get("dims_95", 0) / max(pca.get("total_dims", 1), 1)
        if ratio < 0.15:
            print(f"  [1] Dimensionality: SEVERE collapse ({pca['dims_95']}/{pca['total_dims']})")
            print(f"      -> Most strategies redundant (ARTIFACT evidence)")
            evidence_artifact += 2
        elif ratio < 0.35:
            print(f"  [1] Dimensionality: MODERATE collapse ({pca['dims_95']}/{pca['total_dims']})")
            evidence_mixed += 1
        else:
            print(f"  [1] Dimensionality: MILD collapse ({pca['dims_95']}/{pca['total_dims']})")
            evidence_genuine += 1

    # 2. ICA
    ica = all_results.get("ica", {})
    if ica and "n_independent_components" in ica:
        n_ic = ica["n_independent_components"]
        n_groups = ica["n_strategy_groups"]
        if n_ic < n_groups * 0.5:
            print(f"  [2] ICA: {n_ic} independent sources from {n_groups} groups (ARTIFACT evidence)")
            evidence_artifact += 1
        else:
            print(f"  [2] ICA: {n_ic} independent sources from {n_groups} groups (GENUINE evidence)")
            evidence_genuine += 1

    # 3. Rotation invariance (KEY test)
    rot = all_results.get("rotation", {})
    if rot and "verdict" in rot:
        v = rot["verdict"]
        change = rot.get("relative_change", 1.0)
        if v == "genuine":
            print(f"  [3] Rotation: Structure SURVIVES ({change*100:.1f}% change) (GENUINE evidence) **KEY**")
            evidence_genuine += 3  # Key test, triple weight
        elif v == "mixed":
            print(f"  [3] Rotation: PARTIAL survival ({change*100:.1f}% change) (MIXED)")
            evidence_mixed += 2
        else:
            print(f"  [3] Rotation: Structure DESTROYED ({change*100:.1f}% change) (ARTIFACT evidence) **KEY**")
            evidence_artifact += 3

    # 4. Topology
    topo = all_results.get("topology", {})
    if topo and "verdict" in topo:
        v = topo["verdict"]
        if v == "genuine_topology":
            betti = topo.get("betti_significant", {})
            print(f"  [4] Topology: Non-trivial (b1={betti.get(1,0)}, b2={betti.get(2,0)}) (GENUINE evidence)")
            evidence_genuine += 2
        else:
            print(f"  [4] Topology: Trivial — no persistent loops/voids (NEUTRAL)")

    # 5. Grassmannian
    grass = all_results.get("grassmannian", {})
    if grass and "verdict" in grass:
        v = grass["verdict"]
        n_br = len(grass.get("bridges_lt_15deg", []))
        n_orth = len(grass.get("orthogonal_gt_75deg", []))
        if v == "shared_subspaces":
            print(f"  [5] Grassmannian: {n_br} bridges, {n_orth} orthogonal (ARTIFACT evidence)")
            evidence_artifact += 1
        elif v == "selective_bridges":
            print(f"  [5] Grassmannian: {n_br} bridges, {n_orth} orthogonal (MIXED)")
            evidence_mixed += 1
        else:
            print(f"  [5] Grassmannian: All orthogonal (GENUINE independence)")
            evidence_genuine += 1

    # 6. Curvature
    curv = all_results.get("curvature", {})
    if curv and "verdict" in curv:
        v = curv["verdict"]
        ratio = curv.get("ratio_local_global", 1.0)
        if v == "curved":
            print(f"  [6] Curvature: CURVED manifold (ratio={ratio:.2f}) (GENUINE evidence)")
            evidence_genuine += 1
        elif v == "flat":
            print(f"  [6] Curvature: FLAT manifold (ratio={ratio:.2f}) (ARTIFACT evidence)")
            evidence_artifact += 1
        else:
            print(f"  [6] Curvature: Mixed (ratio={ratio:.2f})")
            evidence_mixed += 1

    # Tally
    total = evidence_genuine + evidence_artifact + evidence_mixed
    print(f"\n  Evidence tally:")
    print(f"    Genuine:  {evidence_genuine}")
    print(f"    Artifact: {evidence_artifact}")
    print(f"    Mixed:    {evidence_mixed}")

    if evidence_genuine > evidence_artifact * 1.5:
        verdict = "genuine structure"
        print(f"\n  >>> The geometry suggests GENUINE STRUCTURE. <<<")
        print(f"      Cross-domain correlations reflect real mathematical relationships,")
        print(f"      not artifacts of the coordinate system.")
    elif evidence_artifact > evidence_genuine * 1.5:
        verdict = "projection artifacts"
        print(f"\n  >>> The geometry suggests PROJECTION ARTIFACTS. <<<")
        print(f"      Most cross-domain correlations are shadows of a low-dimensional")
        print(f"      structure projected into redundant coordinate axes.")
    else:
        verdict = "mixed"
        print(f"\n  >>> The geometry suggests MIXED: some genuine, some artifacts. <<<")
        print(f"      Some cross-domain bridges are geometrically real, but the coordinate")
        print(f"      system inflates the apparent number of independent signals.")

    return verdict


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("TENSOR GEOMETRY ANALYSIS")
    print("Distinguishing genuine structure from projection artifacts")
    print("=" * 60)
    print(f"Device: {DEVICE}")
    if DEVICE.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    np.random.seed(42)
    torch.manual_seed(42)

    # Load tensor
    tensor, mask, labels, domains, domain_indices, strategy_slices, group_slices = load_tensor()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results = {}

    # Analysis 1: Intrinsic Dimensionality
    t0 = time.time()
    all_results["intrinsic_dim"] = analysis_intrinsic_dim(tensor, mask, domain_indices)
    print(f"  [Time: {time.time()-t0:.1f}s]")

    # Analysis 2: ICA
    t0 = time.time()
    all_results["ica"] = analysis_ica(tensor, mask, group_slices)
    print(f"  [Time: {time.time()-t0:.1f}s]")

    # Analysis 3: Rotation Invariance
    t0 = time.time()
    all_results["rotation"] = analysis_rotation_invariance(tensor, mask, group_slices, n_rotations=100)
    print(f"  [Time: {time.time()-t0:.1f}s]")

    # Analysis 4: Persistent Homology
    t0 = time.time()
    all_results["topology"] = analysis_persistent_homology(tensor, mask, n_sample=5000)
    print(f"  [Time: {time.time()-t0:.1f}s]")

    # Analysis 5: Grassmannian
    t0 = time.time()
    all_results["grassmannian"] = analysis_grassmannian(tensor, mask, domain_indices)
    print(f"  [Time: {time.time()-t0:.1f}s]")

    # Analysis 6: Curvature
    t0 = time.time()
    all_results["curvature"] = analysis_curvature(tensor, mask, domain_indices, n_points=1000, k_neighbors=50)
    print(f"  [Time: {time.time()-t0:.1f}s]")

    # Final verdict
    verdict = final_verdict(all_results)
    all_results["verdict"] = verdict

    # Save results
    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    results_path = OUT_DIR / "geometry_analysis.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2, default=convert)
    print(f"\nResults saved to {results_path}")

    return all_results


if __name__ == "__main__":
    main()
