"""
Expanded Ollivier-Ricci Curvature — Math + Science domains in phoneme space.

Measures ORC on the k-NN graph of phoneme-projected vectors from 13 domains
(7 math-only + 6 new cross-disciplinary). Compares curvature of:
  - math-only edges (both endpoints are math domains)
  - cross-category edges (one math, one science/new)
  - new-domain-only edges (both endpoints are new domains)

Key question: do cross-category edges show negative curvature (manifold ridge)?
"""

import json
import sys
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from harmonia.src.domain_index import load_domains
from harmonia.src.phonemes import PhonemeProjector, PHONEMES

# ── Configuration ------------------------------------------──
MATH_DOMAINS = [
    "elliptic_curves", "modular_forms", "number_fields",
    "genus2", "lattices", "ec_zeros", "dirichlet_zeros",
]
NEW_DOMAINS = [
    "rmt", "dynamics", "chemistry",
    "spectral_sigs", "operadic_sigs", "phase_space",
]
ALL_DOMAINS = MATH_DOMAINS + NEW_DOMAINS

SUBSAMPLE = 3000
K = 10
SEED = 42
OUT_PATH = Path(__file__).resolve().parent.parent / "results" / "curvature_expanded.json"

np.random.seed(SEED)


def main():
    t0 = time.time()

    # ── 1. Load domains ------------------------------------──
    print(f"Loading {len(ALL_DOMAINS)} domains...")
    domains_dict = load_domains(*ALL_DOMAINS)
    domain_list = [domains_dict[name] for name in ALL_DOMAINS]
    print(f"  Loaded: {[f'{d.name}({d.n_objects})' for d in domain_list]}")

    # ── 2. Project into phoneme space, subsample ------------─
    print("Projecting into 5D phoneme space...")
    projector = PhonemeProjector(domain_list, device="cpu")

    all_vecs = []
    all_labels = []  # which domain each point belongs to
    import torch

    for i, dom in enumerate(domain_list):
        vecs = projector._phoneme_vecs[i].numpy()
        n = vecs.shape[0]
        if n > SUBSAMPLE:
            idx = np.random.choice(n, SUBSAMPLE, replace=False)
            vecs = vecs[idx]
        all_vecs.append(vecs)
        all_labels.extend([dom.name] * vecs.shape[0])
        print(f"  {dom.name}: {vecs.shape[0]} vectors")

    X = np.vstack(all_vecs).astype(np.float64)
    labels = np.array(all_labels)
    N = X.shape[0]
    print(f"  Combined: {N} points in {X.shape[1]}D phoneme space")

    # ── 3. Build k-NN graph ---------------------------------─
    print(f"Building k-NN graph (k={K})...")
    from scipy.spatial import cKDTree

    tree = cKDTree(X)
    dists, indices = tree.query(X, k=K + 1)  # +1 because self is included
    # Remove self-neighbor (index 0)
    nn_dists = dists[:, 1:]   # (N, K)
    nn_indices = indices[:, 1:]  # (N, K)

    # Collect unique edges
    edge_set = set()
    for i in range(N):
        for j_idx in range(K):
            j = nn_indices[i, j_idx]
            edge = (min(i, j), max(i, j))
            edge_set.add(edge)

    edges = list(edge_set)
    print(f"  {len(edges)} unique edges")

    # ── 4. Compute Ollivier-Ricci curvature ------------------
    print("Computing ORC on all edges...")

    def orc_edge(i, j, nn_indices, X):
        """
        Approximate Ollivier-Ricci curvature for edge (i,j).

        ORC(i,j) = 1 - W1(mu_i, mu_j) / d(i,j)

        where mu_i = uniform distribution on k-NN of i,
              mu_j = uniform distribution on k-NN of j.

        W1 approximated by greedy matching of neighbor sets.
        """
        d_ij = np.linalg.norm(X[i] - X[j])
        if d_ij < 1e-12:
            return 0.0

        ni = nn_indices[i]  # k neighbors of i
        nj = nn_indices[j]  # k neighbors of j

        # Greedy matching: for each neighbor of i, find closest neighbor of j
        # This approximates optimal transport (exact OT is O(k^3), greedy is O(k^2))
        used_j = set()
        total_transport = 0.0

        # Compute pairwise distances between neighbor sets
        Xi = X[ni]  # (K, 5)
        Xj = X[nj]  # (K, 5)
        D = np.linalg.norm(Xi[:, None, :] - Xj[None, :, :], axis=2)  # (K, K)

        # Greedy matching by shortest distance first
        k = len(ni)
        matched = np.zeros(k, dtype=bool)
        matched_j = np.zeros(k, dtype=bool)

        for _ in range(k):
            # Find minimum unmatched entry
            best_d = np.inf
            best_a, best_b = -1, -1
            for a in range(k):
                if matched[a]:
                    continue
                for b in range(k):
                    if matched_j[b]:
                        continue
                    if D[a, b] < best_d:
                        best_d = D[a, b]
                        best_a, best_b = a, b
            if best_a >= 0:
                matched[best_a] = True
                matched_j[best_b] = True
                total_transport += best_d

        w1 = total_transport / k
        return 1.0 - w1 / d_ij

    # Compute ORC for all edges
    n_edges = len(edges)
    orc_values = np.zeros(n_edges)

    # Track category for each edge
    math_set = set(MATH_DOMAINS)
    new_set = set(NEW_DOMAINS)

    edge_categories = []  # 'math', 'cross', 'new'

    for e_idx, (i, j) in enumerate(edges):
        if e_idx % 10000 == 0 and e_idx > 0:
            print(f"  Edge {e_idx}/{n_edges}...")

        orc_values[e_idx] = orc_edge(i, j, nn_indices, X)

        li, lj = labels[i], labels[j]
        i_math = li in math_set
        j_math = lj in math_set

        if i_math and j_math:
            edge_categories.append("math")
        elif not i_math and not j_math:
            edge_categories.append("new")
        else:
            edge_categories.append("cross")

    edge_categories = np.array(edge_categories)

    # ── 5. Analyze results ---------------------------------──
    print("\n=== RESULTS ===")

    def stats(values, name):
        if len(values) == 0:
            return {"name": name, "n_edges": 0}
        return {
            "name": name,
            "n_edges": int(len(values)),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "fraction_positive": float(np.mean(values > 0)),
            "fraction_negative": float(np.mean(values < 0)),
        }

    overall = stats(orc_values, "overall")
    math_only = stats(orc_values[edge_categories == "math"], "math_only")
    cross_cat = stats(orc_values[edge_categories == "cross"], "cross_category")
    new_only = stats(orc_values[edge_categories == "new"], "new_domain_only")

    for s in [overall, math_only, cross_cat, new_only]:
        if s["n_edges"] > 0:
            print(f"  {s['name']:>20}: ORC = {s['mean']:.4f} +/- {s['std']:.4f}  "
                  f"(median {s['median']:.4f}, {s['fraction_positive']*100:.1f}% positive, "
                  f"{s['n_edges']} edges)")
        else:
            print(f"  {s['name']:>20}: no edges")

    # Per-domain pair analysis for cross edges
    print("\n--- Cross-category edge curvature by domain pair ---")
    pair_orcs = {}
    for e_idx, (i, j) in enumerate(edges):
        if edge_categories[e_idx] == "cross":
            li, lj = labels[i], labels[j]
            pair = tuple(sorted([li, lj]))
            if pair not in pair_orcs:
                pair_orcs[pair] = []
            pair_orcs[pair].append(orc_values[e_idx])

    cross_pairs = {}
    for pair, vals in sorted(pair_orcs.items(), key=lambda x: np.mean(x[1])):
        vals = np.array(vals)
        cross_pairs[f"{pair[0]} <->{pair[1]}"] = {
            "mean_orc": float(np.mean(vals)),
            "n_edges": len(vals),
            "frac_positive": float(np.mean(vals > 0)),
        }
        print(f"  {pair[0]:>20}  <-> {pair[1]:<20}: ORC={np.mean(vals):+.4f} ({len(vals)} edges)")

    # Ridge detection: is cross-category curvature significantly different?
    if math_only["n_edges"] > 0 and cross_cat["n_edges"] > 0:
        delta = math_only["mean"] - cross_cat["mean"]
        # Quick significance test (Welch's t)
        from scipy import stats as sp_stats
        math_vals = orc_values[edge_categories == "math"]
        cross_vals = orc_values[edge_categories == "cross"]
        t_stat, p_val = sp_stats.ttest_ind(math_vals, cross_vals, equal_var=False)

        print(f"\n--- Ridge detection ---")
        print(f"  Math-only ORC:      {math_only['mean']:.4f}")
        print(f"  Cross-category ORC: {cross_cat['mean']:.4f}")
        print(f"  Delta:              {delta:+.4f}")
        print(f"  Welch t-test:       t={t_stat:.2f}, p={p_val:.2e}")

        if p_val < 0.001 and delta > 0.05:
            ridge_verdict = "RIDGE DETECTED — cross-category edges are significantly less curved"
        elif p_val < 0.001 and delta < -0.05:
            ridge_verdict = "INVERSE RIDGE — cross-category edges are MORE curved (tighter coupling)"
        else:
            ridge_verdict = "NO RIDGE — curvature is homogeneous across categories"
        print(f"  Verdict: {ridge_verdict}")
    else:
        delta = 0.0
        p_val = 1.0
        t_stat = 0.0
        ridge_verdict = "INSUFFICIENT DATA"

    # Compare with original measurement
    print(f"\n--- Comparison with original 9-domain measurement ---")
    print(f"  Original (9 math-only):  ORC = 0.713")
    print(f"  Expanded (13 mixed):     ORC = {overall['mean']:.4f}")
    change = overall['mean'] - 0.713
    print(f"  Change:                  {change:+.4f}")

    elapsed = time.time() - t0

    # ── 6. Save results ------------------------------------──
    result = {
        "description": "Ollivier-Ricci curvature in expanded 5D phoneme space (13 domains)",
        "domains": {
            "math": MATH_DOMAINS,
            "new": NEW_DOMAINS,
            "total": len(ALL_DOMAINS),
        },
        "parameters": {
            "k": K,
            "subsample_per_domain": SUBSAMPLE,
            "total_points": int(N),
            "total_edges": int(n_edges),
            "seed": SEED,
        },
        "overall": overall,
        "math_only": math_only,
        "cross_category": cross_cat,
        "new_domain_only": new_only,
        "ridge_detection": {
            "delta_orc": float(delta),
            "welch_t": float(t_stat),
            "p_value": float(p_val),
            "verdict": ridge_verdict,
        },
        "cross_pairs": cross_pairs,
        "comparison_with_original": {
            "original_orc": 0.713,
            "expanded_orc": float(overall["mean"]),
            "change": float(change),
        },
        "elapsed_seconds": float(elapsed),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {OUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
