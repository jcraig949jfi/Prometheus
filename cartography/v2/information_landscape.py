"""
Information Landscape Map: Cross-Domain Information Content Comparison

Compiles entropy/information measurements across all 11 datasets from
existing v2 result files. No recomputation -- pure synthesis.

Metrics per dataset:
  - Shannon entropy of key distributions
  - BM recurrence rate (fraction with low-order recurrence)
  - Effective dimensionality (PCA / spectral)
  - Mod-p fingerprint diversity
  - Spectral gap (fingerprint graph geometry)
  - BM compressibility (from compressibility hierarchy)

Output: information_landscape_results.json
"""

import json
import os
from datetime import datetime, timezone

V2 = os.path.dirname(os.path.abspath(__file__))


def load(name):
    path = os.path.join(V2, name)
    with open(path) as f:
        return json.load(f)


def safe_get(d, *keys, default="N/A"):
    """Nested safe get."""
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


def build_landscape():
    # ----------------------------------------------------------------
    # Load all source files
    # ----------------------------------------------------------------
    compress = load("compressibility_hierarchy_results.json")
    spectral = load("spectral_gap_universality_results.json")
    hecke_ent = load("hecke_entropy_rate_results.json")
    theta_ent = load("theta_modp_entropy_results.json")
    oeis_bm = load("oeis_bm_order_results.json")
    jones_bm = load("jones_bm_order_results.json")
    oeis_sign = load("oeis_sign_pattern_results.json")
    oeis_growth = load("oeis_growth_taxonomy_results.json")
    oeis_spec = load("oeis_spectral_dimension_results.json")
    oeis_benford = load("oeis_benford_results.json")
    knot_pca = load("knot_correlation_matrix_results.json")
    knot_modp = load("knot_det_modp_results.json")
    ec_galois = load("conductor_galois_results.json")
    ec_cremona = load("ec_cremona_stats_results.json")
    ec_rank = load("ec_rank_prediction_results.json")
    genus2_rank = load("genus2_rank_distribution_results.json")
    genus2_disc = load("genus2_disc_stats_results.json")
    maass_stats = load("maass_spectral_stats_results.json")
    maass_coeff = load("maass_coefficient_moments_results.json")
    codata_comp = load("codata_compressibility_results.json")
    codata_modp = load("codata_modp_stability_results.json")
    pdg_rec = load("pdg_recurrence_results.json")
    pdg_curv = load("pdg_graph_curvature_results.json")
    pdg_decay = load("pdg_decay_topology_results.json")
    flint_path = load("flint_path_entropy_results.json")
    flint_call = load("flint_call_graph_results.json")
    flint_depth = load("flint_depth_complexity_results.json")
    lean_flint = load("lean_flint_mi_results.json")
    fungrim_clique = load("fungrim_clique_power_law_results.json")
    fungrim_recur = load("fungrim_complexity_recurrence_results.json")
    mf_dim = load("mf_dimension_distribution_results.json")
    mf_weight = load("mf_weight_stats_results.json")
    transport = load("transport_matrix_results.json")
    pipeline = load("pipeline_info_loss_results.json")
    moment_univ = load("moment_universality_results.json")
    decay_spec = load("decay_spectral_dimension_results.json")

    # ----------------------------------------------------------------
    # Helper: compute effective PCA dim (90% variance)
    # ----------------------------------------------------------------
    def pca_eff_dim(cumvar, threshold=0.90):
        for i, v in enumerate(cumvar):
            if v >= threshold:
                return i + 1
        return len(cumvar)

    knot_eff_dim = pca_eff_dim(knot_pca["pca"]["cumulative_variance"])

    # ----------------------------------------------------------------
    # Compressibility hierarchy data
    # ----------------------------------------------------------------
    comp_data = compress["domain_results"]

    # ----------------------------------------------------------------
    # Build per-dataset records
    # ----------------------------------------------------------------
    datasets = {}

    # --- EC (Elliptic Curves) ---
    datasets["EC"] = {
        "full_name": "LMFDB Elliptic Curves",
        "n_objects": safe_get(ec_cremona, "basic_stats", "total_curves"),
        "shannon_entropy": {
            "description": "Hecke eigenvalue distribution entropy (non-CM, 20-bin)",
            "value_bits": safe_get(hecke_ent, "stratified", "non-CM (SU(2))", "mean_entropy"),
            "cm_entropy_bits": safe_get(hecke_ent, "stratified", "CM", "mean_entropy"),
            "fingerprint_entropy_bits": safe_get(ec_galois, "levels", "level1", "h_fingerprint"),
        },
        "bm_recurrence": {
            "compressibility": safe_get(comp_data, "EC", "mean_compressibility"),
            "mean_bm_order": safe_get(comp_data, "EC", "mean_bm_order"),
            "description": "BM on a_p sequences mod 101",
        },
        "effective_dimensionality": {
            "description": "Not directly measured via PCA; rank prediction uses 14 features, RF accuracy 97.2%",
            "n_features_used": 14,
            "prediction_accuracy": safe_get(ec_rank, "summary", "best_binary_accuracy"),
        },
        "modp_fingerprint_diversity": {
            "n_unique_fingerprints": safe_get(ec_galois, "metadata", "n_unique_fingerprints"),
            "n_curves": safe_get(ec_galois, "metadata", "n_curves"),
            "mi_vs_galois_bits": safe_get(ec_galois, "levels", "level1", "mi_bits"),
            "description": "10-prime fingerprint (p=2..29)",
        },
        "spectral_gap": safe_get(spectral, "summary", "gaps", "EC"),
    }

    # --- Genus-2 Curves ---
    datasets["Genus2"] = {
        "full_name": "LMFDB Genus-2 Curves",
        "n_objects": safe_get(genus2_rank, "dataset", "total_curves"),
        "shannon_entropy": {
            "description": "Rank distribution entropy (5 classes: 0-4)",
            "rank_distribution": safe_get(genus2_rank, "rank_distribution"),
            "note": "Higher rank diversity than EC (avg rank 1.21 vs 0.52)",
        },
        "bm_recurrence": "N/A (no BM on genus-2 L-function coefficients in v2)",
        "effective_dimensionality": {
            "description": "Igusa-Clebsch invariants span 4D (I2, I4, I6, I10)",
            "igusa_dimensions": 4,
        },
        "modp_fingerprint_diversity": "N/A (genus-2 mod-p not computed in v2)",
        "spectral_gap": safe_get(spectral, "summary", "gaps", "Genus2"),
    }

    # --- Maass Forms ---
    datasets["Maass"] = {
        "full_name": "LMFDB Maass Newforms",
        "n_objects": safe_get(maass_coeff, "spectral_parameter_statistics", "all_forms", "count"),
        "shannon_entropy": {
            "description": "Spectral parameter spacing -- Poisson distributed",
            "spacing_model": "Poisson",
            "poisson_ks": safe_get(maass_stats, "pooled_spacing_test", "poisson_ks"),
            "std_spacing_normalized": safe_get(maass_stats, "pooled_spacing_test", "std_spacing_normalized"),
            "fricke_entropy": {
                "+1_frac": safe_get(maass_coeff, "fricke_eigenvalue_distribution", "1", "fraction"),
                "-1_frac": safe_get(maass_coeff, "fricke_eigenvalue_distribution", "-1", "fraction"),
                "0_frac": safe_get(maass_coeff, "fricke_eigenvalue_distribution", "0", "fraction"),
            },
            "note": "No Fourier coefficients available in bulk; spectral parameters only",
        },
        "bm_recurrence": "N/A (spectral parameters, not sequences)",
        "effective_dimensionality": {
            "description": "Parameterized by (level, spectral_parameter, symmetry)",
            "unique_levels": 65,
            "spectral_param_range": [
                safe_get(maass_coeff, "spectral_parameter_statistics", "all_forms", "min"),
                safe_get(maass_coeff, "spectral_parameter_statistics", "all_forms", "max"),
            ],
        },
        "modp_fingerprint_diversity": "N/A (no coefficient-level mod-p in v2)",
        "spectral_gap": safe_get(spectral, "summary", "gaps", "MF"),
        "note": "MF spectral gap used (Maass subsumed under modular forms in spectral analysis)",
    }

    # --- Lattices ---
    datasets["Lattices"] = {
        "full_name": "LMFDB Integral Lattices",
        "n_objects": safe_get(theta_ent, "metadata", "n_lattices"),
        "shannon_entropy": {
            "description": "Theta series mod-p entropy (mean across p=3,5,7,11)",
            "by_dimension": {
                dim: {
                    "H_mean": stats["H_mean_mean"],
                    "H_std": stats["H_mean_std"],
                    "n": stats["n"],
                }
                for dim, stats in safe_get(
                    theta_ent, "entropy_distribution_by_dim", default={}
                ).items()
            },
            "overall_H_mean_vs_kissing_rho": safe_get(theta_ent, "summary", "overall_H_mean_vs_kissing_rho"),
        },
        "bm_recurrence": {
            "compressibility": safe_get(comp_data, "Lattices", "mean_compressibility"),
            "mean_bm_order": safe_get(comp_data, "Lattices", "mean_bm_order"),
            "description": "BM on theta coefficients mod 101",
        },
        "effective_dimensionality": {
            "description": "Sparsity model: sparsity = f(dim, log(det))",
            "best_model_R2": safe_get(
                load("lattice_sparsity_results.json"),
                "best_universal_model", "R2",
            ),
        },
        "modp_fingerprint_diversity": {
            "description": "Theta mod-p entropy discriminates kissing number (z=-37.2)",
            "null_z_score": safe_get(theta_ent, "null_test_dim3", "z_score"),
            "knn_accuracy_entropy": safe_get(theta_ent, "g10_comparison", "entropy_knn_accuracy_mean"),
        },
        "spectral_gap": safe_get(spectral, "summary", "gaps", "Lattices"),
    }

    # --- Knots ---
    datasets["Knots"] = {
        "full_name": "KnotInfo Knot Invariants",
        "n_objects": safe_get(knot_pca, "metadata", "n_knots_analyzed"),
        "shannon_entropy": {
            "description": "Jones polynomial coefficient entropy (BM analysis)",
            "bm_frac_recurrent": safe_get(jones_bm, "frac_recurrent"),
            "mean_bm_order": safe_get(jones_bm, "bm_order_stats_recurrent", "mean"),
        },
        "bm_recurrence": {
            "compressibility": safe_get(comp_data, "Knots", "mean_compressibility"),
            "mean_bm_order": safe_get(comp_data, "Knots", "mean_bm_order"),
            "jones_bm_frac_recurrent": safe_get(jones_bm, "frac_recurrent"),
            "jones_enrichment_vs_oeis": safe_get(jones_bm, "enrichment_vs_oeis"),
        },
        "effective_dimensionality": {
            "description": "PCA on 18 knot invariants",
            "pca_90pct_dim": knot_eff_dim,
            "pc1_variance": safe_get(knot_pca, "pca", "explained_variance_ratio")[0],
        },
        "modp_fingerprint_diversity": {
            "description": "Determinant mod-p (always odd, so mod-2 trivial)",
            "max_enrichment_mod7": safe_get(
                knot_modp, "ec_comparison", "knot_max_enrichment_per_prime", "mod_7", "max_enrichment_ratio"
            ),
        },
        "spectral_gap": safe_get(spectral, "summary", "gaps", "Knots"),
    }

    # --- OEIS ---
    datasets["OEIS"] = {
        "full_name": "Online Encyclopedia of Integer Sequences",
        "n_objects": safe_get(oeis_bm, "n_sequences_analyzed"),
        "shannon_entropy": {
            "description": "Sign pattern entropy + growth taxonomy",
            "sign_entropy_mean": safe_get(oeis_sign, "entropy_stats", "mean"),
            "sign_entropy_std": safe_get(oeis_sign, "entropy_stats", "std"),
            "growth_classes": safe_get(oeis_growth, "distribution"),
            "benford_compliance_rate": safe_get(oeis_benford, "per_sequence", "compliance_rate"),
        },
        "bm_recurrence": {
            "compressibility": safe_get(comp_data, "OEIS", "mean_compressibility"),
            "mean_bm_order": safe_get(comp_data, "OEIS", "mean_bm_order"),
            "frac_with_recurrence": safe_get(oeis_bm, "statistics", "fraction_with_recurrence"),
            "bm_mean_order": safe_get(oeis_bm, "statistics", "mean_order"),
        },
        "effective_dimensionality": {
            "description": "Spectral dimension of FFT-based k-NN graph",
            "spectral_dimension": safe_get(oeis_spec, "spectral_dimension", "d_effective"),
            "battery_effective_dim": safe_get(oeis_spec, "comparison_to_battery", "battery_effective_dim"),
        },
        "modp_fingerprint_diversity": {
            "description": "Not directly computed; BM analysis uses GF(p)",
            "bm_growth_correlation": safe_get(
                oeis_bm, "growth_rate_correlation", "spearman_r"
            ),
        },
        "spectral_gap": safe_get(spectral, "summary", "gaps", "OEIS"),
    }

    # --- CODATA ---
    datasets["CODATA"] = {
        "full_name": "CODATA Fundamental Physical Constants",
        "n_objects": safe_get(codata_comp, "codata_summary", "total_analyzed"),
        "shannon_entropy": {
            "description": "Continued fraction BM order distribution",
            "mean_bm_cf": safe_get(codata_comp, "codata_summary", "mean_bm_order_cf"),
            "mean_bm_digits": safe_get(codata_comp, "codata_summary", "mean_bm_order_digits"),
            "cf_compressible_fraction": safe_get(codata_comp, "codata_summary", "cf_compressible_fraction"),
        },
        "bm_recurrence": {
            "cf_compressible_fraction": safe_get(codata_comp, "codata_summary", "cf_compressible_fraction"),
            "mean_bm_order_cf": safe_get(codata_comp, "codata_summary", "mean_bm_order_cf"),
            "description": "BM on continued fraction partial quotients",
        },
        "effective_dimensionality": {
            "description": "93 dimensionless constants across 17 physics domains",
            "n_domains": safe_get(codata_modp, "n_domains"),
        },
        "modp_fingerprint_diversity": {
            "verdict": safe_get(codata_modp, "verdict"),
            "enrichment_ratio": safe_get(codata_modp, "overall", "enrichment_ratio"),
            "description": "No within-domain enrichment -- mod-p residues random",
        },
        "spectral_gap": "N/A (not included in spectral gap universality test)",
    }

    # --- PDG (Particle Data Group) ---
    datasets["PDG"] = {
        "full_name": "Particle Data Group - Particle Masses & Decays",
        "n_objects": safe_get(pdg_curv, "n_particles"),
        "shannon_entropy": {
            "description": "Decay network spectral dimension",
            "spectral_dimension_rw": safe_get(decay_spec, "spectral_dimension", "d_s_random_walk"),
            "spectral_dimension_eigenvalue": safe_get(decay_spec, "spectral_dimension", "d_s_from_eigenvalue_density"),
            "graph_curvature_mean_orc": safe_get(pdg_curv, "overall", "mean_orc"),
        },
        "bm_recurrence": {
            "all_masses_bm_order": safe_get(pdg_rec, "all_masses_sorted", "min_order"),
            "quark_bm_order": safe_get(pdg_rec, "family_quark", "min_order"),
            "meson_bm_order": safe_get(pdg_rec, "family_meson", "min_order"),
            "ratio_order_to_length": safe_get(pdg_rec, "all_masses_sorted", "ratio_order_to_length"),
            "description": "BM order ~0.50 * sequence length -- no recurrence (incompressible)",
        },
        "effective_dimensionality": {
            "spectral_dimension": safe_get(decay_spec, "spectral_dimension", "d_s_random_walk"),
            "n_families": 5,
            "description": "Decay DAG: d_s ~1.19 (fractal)",
        },
        "modp_fingerprint_diversity": "N/A (continuous masses, not integer sequences)",
        "spectral_gap": {
            "decay_graph_lambda1": safe_get(pdg_decay, "spectral_analysis", "lambda_1_spectral_gap"),
            "description": "Dense decay graph (density=0.42), very high spectral gap",
        },
    }

    # --- FLINT ---
    datasets["FLINT"] = {
        "full_name": "FLINT C Library Call Graph",
        "n_objects": safe_get(flint_call, "metadata", "num_function_definitions"),
        "shannon_entropy": {
            "description": "Call graph path entropy (topological + PageRank)",
            "topological_entropy_bits": safe_get(flint_path, "topological_entropy", "h_bits"),
            "pagerank_entropy_bits": safe_get(flint_path, "shannon_entropy_rate", "H_pagerank_intrinsic_bits"),
            "conditional_entropy_bits": safe_get(flint_path, "shannon_entropy_rate", "H_conditional_degweighted_bits"),
            "stationary_entropy_bits": safe_get(flint_path, "stationary_distribution_pagerank", "entropy_of_pi_bits"),
        },
        "bm_recurrence": "N/A (graph structure, not sequences)",
        "effective_dimensionality": {
            "description": "127 modules, 4-tier mathematical complexity hierarchy",
            "n_modules": safe_get(flint_call, "metadata", "num_modules"),
            "power_law_alpha": safe_get(flint_call, "degree_distribution", "power_law_alpha"),
            "spectral_gap": safe_get(flint_call, "spectral", "spectral_gap_lambda1"),
        },
        "modp_fingerprint_diversity": "N/A (code structure, not number-theoretic)",
        "spectral_gap": safe_get(flint_call, "spectral", "spectral_gap_lambda1"),
    }

    # --- Lean (Mathlib) ---
    datasets["Lean"] = {
        "full_name": "Lean 4 Mathlib Import Graph",
        "n_objects": safe_get(lean_flint, "lean_import_graph", "num_files"),
        "shannon_entropy": {
            "description": "Import graph degree distribution",
            "power_law_alpha": safe_get(lean_flint, "lean_import_graph", "power_law_alpha"),
            "mean_in_degree": safe_get(lean_flint, "lean_import_graph", "mean_in_degree"),
            "max_in_degree": safe_get(lean_flint, "lean_import_graph", "max_in_degree"),
        },
        "bm_recurrence": "N/A (graph structure, not sequences)",
        "effective_dimensionality": {
            "description": "Not measured; graph-based",
        },
        "modp_fingerprint_diversity": "N/A (formal proof structure)",
        "spectral_gap": "N/A (not computed)",
        "lean_flint_mi": {
            "mi_bits": safe_get(lean_flint, "mutual_information", "linear_bins", "mi_bits"),
            "z_score": safe_get(lean_flint, "mutual_information", "linear_bins", "z_score"),
            "verdict": "No significant mutual information between Lean and FLINT degree distributions",
        },
    }

    # --- Fungrim ---
    datasets["Fungrim"] = {
        "full_name": "Fungrim Formula Database",
        "n_objects": safe_get(fungrim_clique, "parameters", "n_formulas"),
        "shannon_entropy": {
            "description": "Formula implication graph clique structure",
            "clique_power_law_alpha": safe_get(fungrim_clique, "power_law_fit", "mle", "alpha"),
            "n_maximal_cliques": safe_get(fungrim_clique, "cliques", "n_maximal_cliques"),
            "largest_clique": safe_get(fungrim_clique, "cliques", "largest_clique_size"),
            "graph_density": safe_get(fungrim_clique, "filtered_graph", "density"),
        },
        "bm_recurrence": {
            "description": "Fungrim-OEIS bridging: formula complexity vs OEIS recurrence order",
            "correlation_rho": safe_get(fungrim_recur, "correlations", "complexity_score_vs_mean_recurrence_order", "spearman_rho"),
            "correlation_p": safe_get(fungrim_recur, "correlations", "complexity_score_vs_mean_recurrence_order", "p_value"),
            "verdict": "negligible correlation (rho=0.032, not significant)",
        },
        "effective_dimensionality": {
            "description": "880 connected components, largest=2219 nodes",
            "n_components": safe_get(fungrim_clique, "connected_components", "n_components"),
            "largest_component": safe_get(fungrim_clique, "connected_components", "largest_component"),
        },
        "modp_fingerprint_diversity": "N/A (symbolic formulas, not numeric)",
        "spectral_gap": "N/A (not computed on fingerprint graph)",
    }

    # ----------------------------------------------------------------
    # Composite information scores for ranking
    # ----------------------------------------------------------------
    import math

    scores = {}
    for name, ds in datasets.items():
        score_components = {}

        # 1. Shannon entropy -- extract the primary entropy value per dataset
        se = ds.get("shannon_entropy", {})
        if isinstance(se, dict):
            if "value_bits" in se and se["value_bits"] != "N/A":
                score_components["shannon_primary"] = float(se["value_bits"])
            elif "sign_entropy_mean" in se and se["sign_entropy_mean"] != "N/A":
                score_components["shannon_primary"] = float(se["sign_entropy_mean"])
            elif "topological_entropy_bits" in se and se["topological_entropy_bits"] != "N/A":
                score_components["shannon_primary"] = float(se["topological_entropy_bits"])
            elif "clique_power_law_alpha" in se and se["clique_power_law_alpha"] != "N/A":
                # Use graph density entropy: -p*log2(p) - (1-p)*log2(1-p)
                density = se.get("graph_density", 0.01)
                if isinstance(density, (int, float)) and 0 < density < 1:
                    score_components["shannon_primary"] = -(density * math.log2(density) + (1 - density) * math.log2(1 - density))
            elif "power_law_alpha" in se and se["power_law_alpha"] != "N/A":
                # Lean: use normalized degree distribution entropy
                # H = alpha / (alpha-1) for power-law (approximate)
                alpha = se.get("power_law_alpha", 2.0)
                if isinstance(alpha, (int, float)) and alpha > 1:
                    score_components["shannon_primary"] = alpha / (alpha - 1)
            elif "spectral_dimension_rw" in se and se["spectral_dimension_rw"] != "N/A":
                # PDG: use spectral dimension as entropy proxy
                score_components["shannon_primary"] = float(se["spectral_dimension_rw"])
            elif "mean_bm_cf" in se and se["mean_bm_cf"] != "N/A":
                # CODATA: use mean BM order as complexity proxy (log2)
                score_components["shannon_primary"] = math.log2(float(se["mean_bm_cf"]))

        # For datasets with only rank/distribution entropy, compute it
        if name == "Genus2" and "shannon_primary" not in score_components:
            rd = safe_get(se, "rank_distribution", default={})
            if isinstance(rd, dict):
                total = sum(v.get("count", 0) for v in rd.values() if isinstance(v, dict))
                if total > 0:
                    H = 0
                    for v in rd.values():
                        if isinstance(v, dict):
                            p = v.get("count", 0) / total
                            if p > 0:
                                H -= p * math.log2(p)
                    score_components["shannon_primary"] = H

        if name == "Maass" and "shannon_primary" not in score_components:
            # Use Poisson spacing variance as entropy proxy
            std_n = safe_get(se, "std_spacing_normalized", default=None)
            if isinstance(std_n, (int, float)):
                score_components["shannon_primary"] = float(std_n)

        if name == "Lattices" and "shannon_primary" not in score_components:
            # Use mean theta mod-p entropy across all dims
            by_dim = safe_get(se, "by_dimension", default={})
            if isinstance(by_dim, dict) and by_dim:
                vals = [v["H_mean"] for v in by_dim.values() if isinstance(v, dict) and "H_mean" in v]
                if vals:
                    score_components["shannon_primary"] = sum(vals) / len(vals)

        if name == "Knots" and "shannon_primary" not in score_components:
            bm_frac = safe_get(se, "bm_frac_recurrent", default=None)
            mean_ord = safe_get(se, "mean_bm_order", default=None)
            if isinstance(mean_ord, (int, float)):
                score_components["shannon_primary"] = math.log2(float(mean_ord))

        # 2. BM compressibility (measured)
        bm = ds.get("bm_recurrence", {})
        if isinstance(bm, dict) and "compressibility" in bm and bm["compressibility"] != "N/A":
            score_components["compressibility"] = float(bm["compressibility"])
            score_components["compressibility_measured"] = True
        else:
            score_components["compressibility_measured"] = False

        # 3. Spectral gap
        sg = ds.get("spectral_gap")
        if isinstance(sg, (int, float)):
            score_components["spectral_gap"] = float(sg)

        # 4. Object count (log scale)
        n = ds.get("n_objects")
        if isinstance(n, (int, float)) and n > 0:
            score_components["log_n_objects"] = math.log10(n)

        scores[name] = score_components

    # ----------------------------------------------------------------
    # Summary ranking table
    # ----------------------------------------------------------------
    ranking = []
    for name, sc in scores.items():
        shannon = sc.get("shannon_primary", 0)
        log_n = sc.get("log_n_objects", 0)
        comp_val = sc.get("compressibility")
        comp_measured = sc.get("compressibility_measured", False)
        sg = sc.get("spectral_gap")

        # Information richness = entropy * dataset_scale
        info_richness = shannon * log_n if shannon > 0 and log_n > 0 else 0

        ranking.append({
            "dataset": name,
            "shannon_entropy_bits": round(shannon, 4) if shannon else "N/A",
            "n_objects": datasets[name].get("n_objects", "N/A"),
            "bm_compressibility": round(comp_val, 4) if comp_val is not None else "N/A",
            "bm_compressibility_measured": comp_measured,
            "spectral_gap": round(sg, 4) if sg is not None else "N/A",
            "information_richness_score": round(info_richness, 4) if info_richness else "N/A",
        })

    # Sort by information richness (descending)
    ranking_by_richness = sorted(
        ranking,
        key=lambda x: x["information_richness_score"] if isinstance(x["information_richness_score"], (int, float)) else 0,
        reverse=True,
    )

    # Sort by structure: measured compressibility first, then spectral gap (lower = more clustered)
    # Only rank datasets with actual compressibility measurements for the structure ranking
    ranking_by_structure = sorted(
        ranking,
        key=lambda x: (
            0 if x["bm_compressibility_measured"] else 1,  # measured first
            -(x["bm_compressibility"] if isinstance(x["bm_compressibility"], float) else 0),
        ),
    )

    # ----------------------------------------------------------------
    # Assemble output
    # ----------------------------------------------------------------
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description": "Cross-domain information landscape map across 11 datasets",
        "methodology": {
            "shannon_entropy": "Primary distribution entropy from existing v2 analyses",
            "bm_recurrence": "Berlekamp-Massey compressibility from F29_compressibility_hierarchy",
            "effective_dimensionality": "PCA, spectral dimension, or parameter counts from individual analyses",
            "modp_fingerprint_diversity": "Mod-p residue distribution analysis from individual analyses",
            "spectral_gap": "k-NN fingerprint graph lambda_1 from F28_spectral_gap_universality",
            "information_richness_score": "shannon_entropy * log10(n_objects) -- higher = richer",
            "structure_score": "BM compressibility -- higher = more compressible = more structured",
        },
        "datasets": datasets,
        "ranking_by_information_richness": ranking_by_richness,
        "ranking_by_structure": ranking_by_structure,
        "richest_dataset": {
            "name": ranking_by_richness[0]["dataset"],
            "score": ranking_by_richness[0]["information_richness_score"],
            "reason": "Highest entropy * scale product",
        },
        "most_structured_dataset": {
            "name": ranking_by_structure[0]["dataset"],
            "score": ranking_by_structure[0]["bm_compressibility"],
            "reason": "Highest BM compressibility (most predictable sequences)",
        },
        "least_structured_dataset": {
            "name": ranking_by_structure[-1]["dataset"],
            "score": ranking_by_structure[-1]["bm_compressibility"],
            "reason": "Lowest compressibility or N/A (least predictable / not sequence-based)",
        },
        "cross_domain_findings": {
            "spectral_gap_verdict": safe_get(spectral, "summary", "verdict"),
            "compressibility_hierarchy": [
                {"rank": r["rank"], "domain": r["domain"], "compressibility": r["mean_compressibility"]}
                for r in compress["hierarchy"]
            ],
            "moment_universality": "M4/M2^2 determined by Sato-Tate group: U(1)->1.5, SU(2)->2.0, USp(4)->3.0",
            "pipeline_bottleneck": safe_get(pipeline, "summary", "mechanism"),
            "transport_matrix_note": "Fingerprint transport between domains shows domain-specific geometry",
        },
    }

    return result


def main():
    result = build_landscape()

    out_path = os.path.join(V2, "information_landscape_results.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    # Print summary table
    print("=" * 100)
    print("INFORMATION LANDSCAPE MAP -- Cross-Domain Ranking")
    print("=" * 100)
    print()

    print("RANKED BY INFORMATION RICHNESS (entropy * scale):")
    print(f"{'Rank':<5} {'Dataset':<12} {'Shannon H':<12} {'N objects':<12} {'Richness':<12}")
    print("-" * 55)
    for i, r in enumerate(result["ranking_by_information_richness"], 1):
        sh = r["shannon_entropy_bits"]
        sh_str = f"{sh:.3f}" if isinstance(sh, float) else sh
        n_str = str(r["n_objects"])
        rich = r["information_richness_score"]
        rich_str = f"{rich:.3f}" if isinstance(rich, float) else rich
        print(f"{i:<5} {r['dataset']:<12} {sh_str:<12} {n_str:<12} {rich_str:<12}")
    print()

    print("RANKED BY STRUCTURE (BM compressibility, higher = more structured):")
    print(f"{'Rank':<5} {'Dataset':<12} {'Compress.':<12} {'Measured':<10} {'BM order':<12} {'Spec. Gap':<12}")
    print("-" * 65)
    for i, r in enumerate(result["ranking_by_structure"], 1):
        c = r["bm_compressibility"]
        c_str = f"{c:.4f}" if isinstance(c, float) else c
        m_str = "YES" if r.get("bm_compressibility_measured") else "no"
        sg = r["spectral_gap"]
        sg_str = f"{sg:.4f}" if isinstance(sg, float) else sg
        ds = result["datasets"][r["dataset"]]
        bm = ds.get("bm_recurrence", {})
        bm_ord = bm.get("mean_bm_order", "N/A") if isinstance(bm, dict) else "N/A"
        bm_str = f"{bm_ord:.1f}" if isinstance(bm_ord, (int, float)) else bm_ord
        print(f"{i:<5} {r['dataset']:<12} {c_str:<12} {m_str:<10} {bm_str:<12} {sg_str:<12}")
    print()

    print(f"RICHEST (highest entropy):     {result['richest_dataset']['name']}")
    print(f"MOST STRUCTURED (lowest H):    {result['most_structured_dataset']['name']}")
    print(f"LEAST STRUCTURED:              {result['least_structured_dataset']['name']}")
    print()
    print(f"Saved to: {out_path}")


if __name__ == "__main__":
    main()
