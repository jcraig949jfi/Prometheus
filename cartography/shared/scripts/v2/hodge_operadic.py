"""
hodge_operadic.py — Probing the topology↔algebra threshold in verb space

Uses Fungrim formula index + C12 operadic dynamics to ask:
when does a topological cycle become algebraic, as measured by
the operator (verb) profile of formulas?

Key idea: Fungrim modules naturally partition into "topological"
(integrals, limits, continuity, manifolds) and "algebraic"
(polynomials, rings, groups, number theory). The four universal
operators (Equal, And, Set, For) from C12 give a 4D verb space.
We look for the decision boundary.
"""

import json
import os
import sys
import numpy as np
from collections import defaultdict
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[3]
FUNGRIM_INDEX = REPO_ROOT / "cartography" / "fungrim" / "data" / "fungrim_index.json"
OPERADIC_RESULTS = SCRIPT_DIR / "operadic_dynamics_results.json"
OUT_JSON = SCRIPT_DIR / "hodge_operadic_results.json"

# ── module classification ──────────────────────────────────────
# Topological: modules dominated by integrals, limits, continuity,
# special functions defined by integral representations, analysis
TOPOLOGICAL_MODULES = {
    "integrals", "gaussian_quadrature",
    "gamma", "beta_function",             # defined by integrals
    "error_functions",                     # erf = integral of gaussian
    "airy", "bessel", "coulomb_wave",     # ODE solutions / integral reps
    "confluent_hypergeometric", "gauss_hypergeometric",
    "carlson_elliptic", "legendre_elliptic", "weierstrass_elliptic",
    "complex_plane", "complex_parts",
    "exp", "log", "sine", "sinc", "atan",
    "sqrt", "powers",
    "lambertw",
    "digamma_function", "barnes_g",
    "agm",
}

# Algebraic: modules dominated by discrete structure, number theory,
# polynomial identities, group-theoretic objects
ALGEBRAIC_MODULES = {
    "prime_numbers", "totient", "gcd",
    "factorials", "fibonacci", "bell_numbers", "stirling_numbers",
    "bernoulli_numbers", "integer_sequences", "partitions",
    "chebyshev", "legendre_polynomial",    # polynomial families
    "golden_ratio",
    "numbers", "imaginary_unit",
    "landau_function",
    "multiple_zeta_values",
    "modular_j", "modular_lambda", "modular_transformations",
    "dedekind_eta", "eisenstein",
    "jacobi_theta",
    "dirichlet", "hurwitz_zeta", "riemann_zeta",
    "const_catalan", "const_gamma",
    "pi",                                   # algebraic relations dominate
    "halphen_constant",
}

# Meta / structural modules (excluded from topo/alg classification)
META_MODULES = {
    "logic", "operators", "general_functions",
    "symbolic_expressions",
}


def load_data():
    with open(FUNGRIM_INDEX, "r") as f:
        fungrim = json.load(f)
    with open(OPERADIC_RESULTS, "r") as f:
        operadic = json.load(f)
    return fungrim, operadic


def classify_module(mod):
    if mod in TOPOLOGICAL_MODULES:
        return "topological"
    elif mod in ALGEBRAIC_MODULES:
        return "algebraic"
    elif mod in META_MODULES:
        return "meta"
    else:
        return "unclassified"


def compute_verb_profile(symbols):
    """Score a formula by its verb profile: fraction of symbols in each
    of the four universal operator categories."""
    n = len(symbols) if symbols else 1
    equal_count = symbols.count("Equal")
    and_count = symbols.count("And")
    set_count = symbols.count("Set") + symbols.count("SetMinus") + symbols.count("PowerSet")
    for_count = symbols.count("For")

    # Extended topological verbs: integrals, limits, sums
    topo_verbs = {"Integral", "Limit", "RealLimit", "ComplexLimit",
                  "SequenceLimit", "LeftLimit", "RightLimit",
                  "MeromorphicLimit", "SequenceLimitInferior",
                  "SequenceLimitSuperior", "Sum", "Product",
                  "IndefiniteIntegralEqual", "ComplexIndefiniteIntegralEqual"}
    topo_count = sum(1 for s in symbols if s in topo_verbs)

    return {
        "Equal_frac": equal_count / n,
        "And_frac": and_count / n,
        "Set_frac": set_count / n,
        "For_frac": for_count / n,
        "Topo_verb_frac": topo_count / n,
        "Equal_count": equal_count,
        "And_count": and_count,
        "Set_count": set_count,
        "For_count": for_count,
        "Topo_verb_count": topo_count,
        "n_symbols": n,
    }


def main():
    fungrim, operadic = load_data()
    formulas = fungrim["formulas"]

    # ── Step 1: Classify and score ─────────────────────────────
    records = []
    for f in formulas:
        mod = f["module"]
        cls = classify_module(mod)
        if cls == "meta":
            continue
        profile = compute_verb_profile(f["symbols"])
        records.append({
            "id": f["id"],
            "module": mod,
            "class": cls,
            "symbols": f["symbols"],
            **profile,
        })

    n_topo = sum(1 for r in records if r["class"] == "topological")
    n_alg = sum(1 for r in records if r["class"] == "algebraic")
    n_unc = sum(1 for r in records if r["class"] == "unclassified")
    print(f"Classified: {n_topo} topological, {n_alg} algebraic, {n_unc} unclassified")
    print(f"Total formulas (excl meta): {len(records)}")

    # ── Step 2: Aggregate verb profiles by class ───────────────
    class_profiles = defaultdict(lambda: defaultdict(list))
    for r in records:
        cls = r["class"]
        for key in ["Equal_frac", "And_frac", "Set_frac", "For_frac", "Topo_verb_frac"]:
            class_profiles[cls][key].append(r[key])

    class_means = {}
    for cls, profiles in class_profiles.items():
        class_means[cls] = {k: float(np.mean(v)) for k, v in profiles.items()}
        class_means[cls]["count"] = len(profiles["Equal_frac"])
    print("\nClass verb means:")
    for cls, means in sorted(class_means.items()):
        print(f"  {cls}: Equal={means['Equal_frac']:.3f} And={means['And_frac']:.3f} "
              f"Set={means['Set_frac']:.3f} For={means['For_frac']:.3f} "
              f"Topo={means['Topo_verb_frac']:.3f} (n={means['count']})")

    # ── Step 3: Threshold detection in 2D (Set_frac, Equal_frac) ──
    # Compute separation metric between topological and algebraic
    topo_records = [r for r in records if r["class"] == "topological"]
    alg_records = [r for r in records if r["class"] == "algebraic"]

    topo_set = np.array([r["Set_frac"] for r in topo_records])
    topo_eq = np.array([r["Equal_frac"] for r in topo_records])
    alg_set = np.array([r["Set_frac"] for r in alg_records])
    alg_eq = np.array([r["Equal_frac"] for r in alg_records])

    # Fisher's linear discriminant in 2D
    mu_topo = np.array([topo_set.mean(), topo_eq.mean()])
    mu_alg = np.array([alg_set.mean(), alg_eq.mean()])

    # Within-class scatter
    S_w = np.zeros((2, 2))
    for s, e in zip(topo_set, topo_eq):
        d = np.array([s, e]) - mu_topo
        S_w += np.outer(d, d)
    for s, e in zip(alg_set, alg_eq):
        d = np.array([s, e]) - mu_alg
        S_w += np.outer(d, d)

    # Between-class scatter
    diff = mu_topo - mu_alg
    S_b = np.outer(diff, diff)

    # Fisher criterion: ratio of between to within variance along optimal direction
    try:
        S_w_inv = np.linalg.inv(S_w)
        w_fisher = S_w_inv @ diff
        w_fisher = w_fisher / np.linalg.norm(w_fisher)
        fisher_ratio = float(diff @ S_w_inv @ diff)
    except np.linalg.LinAlgError:
        w_fisher = diff / np.linalg.norm(diff)
        fisher_ratio = 0.0

    print(f"\nFisher discriminant direction: Set_w={w_fisher[0]:.4f}, Equal_w={w_fisher[1]:.4f}")
    print(f"Fisher ratio (separation): {fisher_ratio:.6f}")

    # Project all formulas onto Fisher direction and check overlap
    topo_proj = topo_set * w_fisher[0] + topo_eq * w_fisher[1]
    alg_proj = alg_set * w_fisher[0] + alg_eq * w_fisher[1]

    # Overlap: fraction of topo formulas that fall within algebraic range and vice versa
    alg_min, alg_max = alg_proj.min(), alg_proj.max()
    topo_min, topo_max = topo_proj.min(), topo_proj.max()
    overlap_min = max(topo_min, alg_min)
    overlap_max = min(topo_max, alg_max)

    if overlap_max > overlap_min:
        topo_in_overlap = np.mean((topo_proj >= overlap_min) & (topo_proj <= overlap_max))
        alg_in_overlap = np.mean((alg_proj >= overlap_min) & (alg_proj <= overlap_max))
    else:
        topo_in_overlap = 0.0
        alg_in_overlap = 0.0

    boundary_type = "sharp" if (topo_in_overlap < 0.3 and alg_in_overlap < 0.3) else "gradual"
    print(f"Overlap: {topo_in_overlap:.3f} topo, {alg_in_overlap:.3f} alg -> {boundary_type}")

    # ── Step 4: Full 4D verb space analysis ────────────────────
    # Build feature matrix for all classified formulas
    verb_keys = ["Equal_frac", "And_frac", "Set_frac", "For_frac"]
    topo_mat = np.array([[r[k] for k in verb_keys] for r in topo_records])
    alg_mat = np.array([[r[k] for k in verb_keys] for r in alg_records])

    mu4_topo = topo_mat.mean(axis=0)
    mu4_alg = alg_mat.mean(axis=0)

    # Mahalanobis-like separation in 4D
    all_classified = np.vstack([topo_mat, alg_mat])
    cov_pooled = np.cov(all_classified.T)
    try:
        cov_inv = np.linalg.inv(cov_pooled)
        d4 = mu4_topo - mu4_alg
        mahal_dist = float(np.sqrt(d4 @ cov_inv @ d4))
    except np.linalg.LinAlgError:
        mahal_dist = float(np.linalg.norm(mu4_topo - mu4_alg))

    print(f"\n4D Mahalanobis distance: {mahal_dist:.4f}")

    # ── Step 5: Transition matrix T ────────────────────────────
    # T_ij = P(verb_j | module_type_i)
    # Rows: topological, algebraic
    # Cols: Equal, And, Set, For
    verb_names = ["Equal", "And", "Set", "For"]

    # Count total verb occurrences per class
    topo_verb_totals = np.zeros(4)
    alg_verb_totals = np.zeros(4)
    count_keys = ["Equal_count", "And_count", "Set_count", "For_count"]

    for r in topo_records:
        for j, ck in enumerate(count_keys):
            topo_verb_totals[j] += r[ck]
    for r in alg_records:
        for j, ck in enumerate(count_keys):
            alg_verb_totals[j] += r[ck]

    # Normalize to get conditional probabilities
    topo_total = topo_verb_totals.sum()
    alg_total = alg_verb_totals.sum()

    T = np.zeros((2, 4))
    if topo_total > 0:
        T[0] = topo_verb_totals / topo_total
    if alg_total > 0:
        T[1] = alg_verb_totals / alg_total

    print("\nTransition matrix T (rows=class, cols=verb):")
    print(f"  {'':>12s}  {'Equal':>8s}  {'And':>8s}  {'Set':>8s}  {'For':>8s}")
    print(f"  {'topological':>12s}  {T[0,0]:8.4f}  {T[0,1]:8.4f}  {T[0,2]:8.4f}  {T[0,3]:8.4f}")
    print(f"  {'algebraic':>12s}  {T[1,0]:8.4f}  {T[1,1]:8.4f}  {T[1,2]:8.4f}  {T[1,3]:8.4f}")

    # SVD of T
    U, sigma, Vt = np.linalg.svd(T, full_matrices=False)
    print(f"\nSVD singular values: {sigma}")
    print(f"  sigma_1/sigma_2 = {sigma[0]/sigma[1] if sigma[1] > 1e-10 else 'inf'}")
    print(f"  -> {'Sharp divide' if sigma[0]/sigma[1] > 5 else 'Gradual transition'} in verb space")

    # Effective rank
    sigma_norm = sigma / sigma.sum()
    effective_rank = float(np.exp(-np.sum(sigma_norm * np.log(sigma_norm + 1e-15))))
    print(f"  Effective rank: {effective_rank:.3f} (1=sharp, 2=diffuse)")

    # The dominant right singular vector shows which verbs separate the classes
    dominant_verb_direction = Vt[0]
    print(f"\nDominant separating direction in verb space:")
    for name, val in zip(verb_names, dominant_verb_direction):
        print(f"  {name}: {val:+.4f}")

    # ── Step 6: Cross-domain formulas ──────────────────────────
    # Formulas whose symbol sets include verbs from BOTH topological
    # and algebraic signature patterns
    # A formula is "cross-domain" if it appears in a topological module
    # but has algebraic verb signature, or vice versa

    # More precisely: find formulas in topo modules with high Equal_frac
    # and formulas in alg modules with high Topo_verb_frac
    cross_domain = []

    # Method: formulas whose Fisher projection is in the opposite class's territory
    fisher_midpoint = (topo_proj.mean() + alg_proj.mean()) / 2

    for r in topo_records:
        proj = r["Set_frac"] * w_fisher[0] + r["Equal_frac"] * w_fisher[1]
        if (proj - fisher_midpoint) * (topo_proj.mean() - fisher_midpoint) < 0:
            cross_domain.append({**r, "cross_type": "topo_in_alg_territory"})

    for r in alg_records:
        proj = r["Set_frac"] * w_fisher[0] + r["Equal_frac"] * w_fisher[1]
        if (proj - fisher_midpoint) * (alg_proj.mean() - fisher_midpoint) < 0:
            cross_domain.append({**r, "cross_type": "alg_in_topo_territory"})

    print(f"\nCross-domain formulas: {len(cross_domain)}")
    cross_topo = [c for c in cross_domain if c["cross_type"] == "topo_in_alg_territory"]
    cross_alg = [c for c in cross_domain if c["cross_type"] == "alg_in_topo_territory"]
    print(f"  Topological formulas in algebraic territory: {len(cross_topo)}")
    print(f"  Algebraic formulas in topological territory: {len(cross_alg)}")

    # Verb profile of cross-domain formulas
    if cross_domain:
        cross_mat = np.array([[c[k] for k in verb_keys] for c in cross_domain])
        cross_mean = cross_mat.mean(axis=0)
        print(f"\n  Cross-domain mean verb profile:")
        for name, val in zip(verb_names, cross_mean):
            print(f"    {name}: {val:.4f}")
        print(f"  vs Topological: {mu4_topo}")
        print(f"  vs Algebraic:   {mu4_alg}")

        # Are cross-domain formulas intermediate?
        # Distance from cross-domain centroid to topo and alg centroids
        d_to_topo = float(np.linalg.norm(cross_mean - mu4_topo))
        d_to_alg = float(np.linalg.norm(cross_mean - mu4_alg))
        intermediacy = 1.0 - abs(d_to_topo - d_to_alg) / (d_to_topo + d_to_alg + 1e-10)
        print(f"\n  Distance to topo centroid: {d_to_topo:.4f}")
        print(f"  Distance to alg centroid:  {d_to_alg:.4f}")
        print(f"  Intermediacy score: {intermediacy:.4f} (1=perfectly between, 0=on one side)")

        # Module distribution of cross-domain formulas
        cross_modules = defaultdict(int)
        for c in cross_domain:
            cross_modules[c["module"]] += 1
        print(f"\n  Cross-domain module distribution (top 15):")
        for mod, count in sorted(cross_modules.items(), key=lambda x: -x[1])[:15]:
            print(f"    {mod}: {count}")
    else:
        cross_mean = [0, 0, 0, 0]
        d_to_topo = 0
        d_to_alg = 0
        intermediacy = 0

    # ── Step 7: Per-module verb fingerprints ───────────────────
    module_fingerprints = {}
    for mod in set(r["module"] for r in records):
        mod_records = [r for r in records if r["module"] == mod]
        if not mod_records:
            continue
        mat = np.array([[r[k] for k in verb_keys] for r in mod_records])
        module_fingerprints[mod] = {
            "class": classify_module(mod),
            "n_formulas": len(mod_records),
            "Equal_mean": float(mat[:, 0].mean()),
            "And_mean": float(mat[:, 1].mean()),
            "Set_mean": float(mat[:, 2].mean()),
            "For_mean": float(mat[:, 3].mean()),
            "Equal_std": float(mat[:, 0].std()),
            "And_std": float(mat[:, 1].std()),
            "Set_std": float(mat[:, 2].std()),
            "For_std": float(mat[:, 3].std()),
        }

    # ── Step 8: Integration with C12 operadic distances ────────
    # Check if modules that are close in operadic distance also have
    # similar verb profiles
    dist_matrix = operadic.get("distance_matrix", {})
    modules_list = dist_matrix.get("modules", [])
    matrix = dist_matrix.get("matrix", [])

    verb_distance_vs_operadic = []
    if modules_list and matrix:
        for i, mod_i in enumerate(modules_list):
            for j, mod_j in enumerate(modules_list):
                if j <= i:
                    continue
                if mod_i not in module_fingerprints or mod_j not in module_fingerprints:
                    continue
                fp_i = module_fingerprints[mod_i]
                fp_j = module_fingerprints[mod_j]
                verb_dist = np.sqrt(sum(
                    (fp_i[f"{v}_mean"] - fp_j[f"{v}_mean"])**2 for v in verb_names
                ))
                operadic_dist = matrix[i][j]
                verb_distance_vs_operadic.append({
                    "mod_a": mod_i,
                    "mod_b": mod_j,
                    "verb_distance": float(verb_dist),
                    "operadic_distance": float(operadic_dist),
                    "class_a": fp_i["class"],
                    "class_b": fp_j["class"],
                })

    if verb_distance_vs_operadic:
        vd = np.array([x["verb_distance"] for x in verb_distance_vs_operadic])
        od = np.array([x["operadic_distance"] for x in verb_distance_vs_operadic])
        corr = float(np.corrcoef(vd, od)[0, 1])
        print(f"\nVerb distance vs operadic distance correlation: {corr:.4f}")

        # Same-class vs cross-class
        same_class = [(x["verb_distance"], x["operadic_distance"])
                      for x in verb_distance_vs_operadic if x["class_a"] == x["class_b"]]
        diff_class = [(x["verb_distance"], x["operadic_distance"])
                      for x in verb_distance_vs_operadic if x["class_a"] != x["class_b"]]
        if same_class:
            sc = np.array(same_class)
            print(f"  Same-class pairs: verb_d={sc[:,0].mean():.4f}, operadic_d={sc[:,1].mean():.4f}")
        if diff_class:
            dc = np.array(diff_class)
            print(f"  Cross-class pairs: verb_d={dc[:,0].mean():.4f}, operadic_d={dc[:,1].mean():.4f}")
    else:
        corr = 0.0

    # ── Plot ───────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        # Panel 1: Set_frac vs Equal_frac colored by class
        ax = axes[0, 0]
        for cls, color, label in [("topological", "#2196F3", "Topological"),
                                   ("algebraic", "#F44336", "Algebraic")]:
            recs = [r for r in records if r["class"] == cls]
            xs = [r["Set_frac"] for r in recs]
            ys = [r["Equal_frac"] for r in recs]
            ax.scatter(xs, ys, c=color, alpha=0.3, s=8, label=label)
        # Plot cross-domain
        if cross_domain:
            ax.scatter([c["Set_frac"] for c in cross_domain],
                      [c["Equal_frac"] for c in cross_domain],
                      c="#FFD700", edgecolors="k", s=20, alpha=0.7, label="Cross-domain", zorder=5)
        # Fisher direction
        mid = (mu_topo + mu_alg) / 2
        perp = np.array([-w_fisher[1], w_fisher[0]])
        p1 = mid - 0.5 * perp
        p2 = mid + 0.5 * perp
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k--', linewidth=1.5, label="Fisher boundary")
        ax.set_xlabel("Set_fraction")
        ax.set_ylabel("Equal_fraction")
        ax.set_title("Topology↔Algebra in verb space")
        ax.legend(fontsize=8)

        # Panel 2: Fisher projection histograms
        ax = axes[0, 1]
        ax.hist(topo_proj, bins=40, alpha=0.6, color="#2196F3", label="Topological", density=True)
        ax.hist(alg_proj, bins=40, alpha=0.6, color="#F44336", label="Algebraic", density=True)
        ax.axvline(fisher_midpoint, color="k", linestyle="--", label="Decision boundary")
        ax.set_xlabel("Fisher projection")
        ax.set_ylabel("Density")
        ax.set_title(f"Fisher separation (ratio={fisher_ratio:.4f})")
        ax.legend(fontsize=8)

        # Panel 3: Transition matrix heatmap
        ax = axes[1, 0]
        im = ax.imshow(T, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(range(4))
        ax.set_xticklabels(verb_names)
        ax.set_yticks(range(2))
        ax.set_yticklabels(["Topological", "Algebraic"])
        for i in range(2):
            for j in range(4):
                ax.text(j, i, f"{T[i,j]:.3f}", ha="center", va="center",
                       color="white" if T[i,j] > 0.3 else "black", fontsize=10)
        ax.set_title(f"Transition matrix T (σ₁/σ₂={sigma[0]/sigma[1]:.2f})")
        plt.colorbar(im, ax=ax, shrink=0.8)

        # Panel 4: Module fingerprints in 2D
        ax = axes[1, 1]
        for mod, fp in module_fingerprints.items():
            color = {"topological": "#2196F3", "algebraic": "#F44336",
                     "unclassified": "#999999"}.get(fp["class"], "#999999")
            ax.scatter(fp["Set_mean"], fp["Equal_mean"], c=color, s=fp["n_formulas"]*2,
                      alpha=0.6, edgecolors="k", linewidth=0.3)
            if fp["n_formulas"] > 30:
                ax.annotate(mod, (fp["Set_mean"], fp["Equal_mean"]), fontsize=5,
                           alpha=0.7, ha="center", va="bottom")
        ax.set_xlabel("Mean Set_fraction")
        ax.set_ylabel("Mean Equal_fraction")
        ax.set_title("Module centroids (size=formula count)")

        plt.tight_layout()
        plot_path = SCRIPT_DIR / "hodge_operadic_plot.png"
        plt.savefig(str(plot_path), dpi=150)
        print(f"\nPlot saved to {plot_path}")
        plt.close()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")
        plot_path = None

    # ── Assemble results ───────────────────────────────────────
    results = {
        "meta": {
            "timestamp": str(np.datetime64("now")),
            "n_formulas_analyzed": len(records),
            "n_topological": n_topo,
            "n_algebraic": n_alg,
            "n_unclassified": n_unc,
            "n_modules_topo": len(TOPOLOGICAL_MODULES),
            "n_modules_alg": len(ALGEBRAIC_MODULES),
        },
        "class_verb_means": class_means,
        "fisher_discriminant": {
            "direction_Set": float(w_fisher[0]),
            "direction_Equal": float(w_fisher[1]),
            "fisher_ratio": fisher_ratio,
            "topo_overlap_fraction": float(topo_in_overlap),
            "alg_overlap_fraction": float(alg_in_overlap),
            "boundary_type": boundary_type,
            "interpretation": (
                "Sharp boundary: topological and algebraic formulas occupy distinct "
                "regions in verb space" if boundary_type == "sharp" else
                "Gradual transition: significant overlap in verb space between "
                "topological and algebraic formulas"
            ),
        },
        "four_d_analysis": {
            "mahalanobis_distance": mahal_dist,
            "topo_centroid": {n: float(v) for n, v in zip(verb_names, mu4_topo)},
            "alg_centroid": {n: float(v) for n, v in zip(verb_names, mu4_alg)},
        },
        "transition_matrix": {
            "rows": ["topological", "algebraic"],
            "cols": verb_names,
            "matrix": T.tolist(),
            "singular_values": sigma.tolist(),
            "sigma_ratio": float(sigma[0] / sigma[1]) if sigma[1] > 1e-10 else None,
            "effective_rank": effective_rank,
            "dominant_verb_direction": {n: float(v) for n, v in zip(verb_names, dominant_verb_direction)},
            "interpretation": (
                f"σ₁/σ₂ = {sigma[0]/sigma[1]:.2f}: "
                + ("The divide is sharp — one singular value dominates, meaning "
                   "a single direction in verb space separates the classes"
                   if sigma[0]/sigma[1] > 5 else
                   "The divide is diffuse — both singular values contribute, meaning "
                   "the topology↔algebra distinction is spread across multiple verb dimensions")
            ),
        },
        "cross_domain_formulas": {
            "total": len(cross_domain),
            "topo_in_alg_territory": len(cross_topo),
            "alg_in_topo_territory": len(cross_alg),
            "cross_domain_verb_mean": {n: float(v) for n, v in zip(verb_names, cross_mean)} if cross_domain else {},
            "intermediacy_score": float(intermediacy),
            "distance_to_topo": float(d_to_topo),
            "distance_to_alg": float(d_to_alg),
            "interpretation": (
                f"Intermediacy={intermediacy:.3f}: "
                + ("Cross-domain formulas sit between the two classes — they are "
                   "genuine bridges in verb space"
                   if intermediacy > 0.7 else
                   "Cross-domain formulas lean toward one class — they are "
                   "outliers, not bridges")
            ),
            "top_cross_modules": dict(sorted(
                ((c["module"], sum(1 for x in cross_domain if x["module"] == c["module"]))
                 for c in cross_domain),
                key=lambda x: -x[1]
            )[:10]) if cross_domain else {},
            "examples": [
                {"id": c["id"], "module": c["module"], "cross_type": c["cross_type"],
                 "Equal_frac": c["Equal_frac"], "Set_frac": c["Set_frac"]}
                for c in cross_domain[:20]
            ],
        },
        "verb_operadic_correlation": {
            "pearson_r": corr,
            "interpretation": (
                f"r={corr:.3f}: " +
                ("Verb distance tracks operadic distance — the algebra↔topology "
                 "divide is reflected in formula structure"
                 if abs(corr) > 0.3 else
                 "Verb distance is weakly correlated with operadic distance — "
                 "the divide is NOT a simple structural artifact")
            ),
        },
        "module_fingerprints": module_fingerprints,
    }

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_JSON}")

    # ── Summary ────────────────────────────────────────────────
    print("\n" + "="*60)
    print("HODGE-OPERADIC ANALYSIS SUMMARY")
    print("="*60)
    print(f"Question: Is the topology<->algebra boundary sharp or gradual?")
    print(f"  Fisher ratio: {fisher_ratio:.4f}")
    print(f"  4D Mahalanobis: {mahal_dist:.4f}")
    print(f"  Boundary type: {boundary_type}")
    print(f"  Transition matrix s1/s2: {sigma[0]/sigma[1]:.2f}")
    print(f"  Effective rank: {effective_rank:.3f}")
    print(f"  Cross-domain intermediacy: {intermediacy:.3f}")
    print(f"  Verb<->operadic correlation: {corr:.3f}")


if __name__ == "__main__":
    main()
