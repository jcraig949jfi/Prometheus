"""
Mathematical Phonemes — Universal coordinate system for cross-domain structure.

Like the IPA maps all speech sounds to articulatory features (place, manner,
voicing), this maps all mathematical objects to universal invariant coordinates:

  COMPLEXITY  — conductor, discriminant, level, determinant (how "big" is it)
  RANK        — rank, degree, dimension, n_vertices (how "rich" is it)
  SYMMETRY    — point group order, automorphism order, Galois group (how symmetric)
  ARITHMETIC  — torsion, class number, Selmer rank (arithmetic complexity)
  SPECTRAL    — spectral parameter, eigenvalues, zero spacings (analytic fingerprint)

Every domain maps to a subset of these. The scorer measures whether
objects from different domains land in the same region of universal space.
Cross-domain coupling = shared phonemic coordinates.
"""
import torch
import numpy as np
from typing import Optional
from pathlib import Path
from harmonia.src.domain_index import DomainIndex


# ── Universal phoneme definitions ─────────────────────────────────────
# Each phoneme is a named axis. Domain-specific feature indices map to it.

PHONEMES = ["complexity", "rank", "symmetry", "arithmetic", "spectral"]

# Maps: domain_name -> {phoneme_name: (feature_index, sign, weight)}
# sign: +1 if feature increases with phoneme, -1 if inverse
# weight: how directly this feature maps to the phoneme (1.0 = exact, 0.5 = proxy)
DOMAIN_PHONEME_MAP = {
    "elliptic_curves": {
        # features: [log_conductor, rank, analytic_rank, torsion]
        "complexity": [(0, +1, 1.0)],           # log_conductor IS complexity
        "rank":       [(1, +1, 1.0), (2, +1, 0.8)],  # rank + analytic_rank
        "arithmetic": [(3, +1, 1.0)],           # torsion
    },
    "modular_forms": {
        # features: [log_level, weight, dim, char_order, char_parity]
        "complexity": [(0, +1, 1.0)],           # log_level ~ conductor
        "rank":       [(2, +1, 0.8)],           # dim ~ rank proxy
        "symmetry":   [(3, +1, 0.7), (4, +1, 0.5)],  # character order + parity
        "spectral":   [(1, +1, 0.9)],           # weight = spectral weight
    },
    "dirichlet_zeros": {
        # features: [log_conductor, degree, rank, n_zeros, motivic_weight]
        "complexity": [(0, +1, 1.0)],           # conductor
        "rank":       [(1, +1, 0.9), (2, +1, 1.0)],  # degree + rank
        "spectral":   [(3, +1, 0.7), (4, +1, 0.9)],  # n_zeros + motivic_weight
    },
    "number_fields": {
        # features: [degree, disc_sign, log_disc_abs, class_number, regulator, n_class_group]
        "complexity": [(2, +1, 1.0)],           # log_disc_abs ~ conductor
        "rank":       [(0, +1, 1.0)],           # degree
        "arithmetic": [(3, +1, 1.0), (5, +1, 0.7)],  # class_number + class_group
        "spectral":   [(4, +1, 0.8)],           # regulator
    },
    "genus2": {
        # features: [log_conductor, disc_sign, two_selmer_rank, has_square_sha,
        #            locally_solvable, globally_solvable, root_number]
        "complexity": [(0, +1, 1.0)],           # conductor
        "rank":       [(2, +1, 0.9)],           # Selmer rank ~ rank proxy
        "arithmetic": [(2, +1, 0.8), (3, +1, 0.6)],  # Selmer + Sha
        "symmetry":   [(6, +1, 0.5)],           # root_number encodes functional eq symmetry
    },
    "lattices": {
        # features: [dimension, log_determinant, log_level, class_number, min_vector, log_aut_order]
        "complexity": [(1, +1, 0.9), (2, +1, 0.8)],  # determinant + level
        "rank":       [(0, +1, 1.0)],           # dimension
        "symmetry":   [(5, +1, 1.0)],           # automorphism order
        "arithmetic": [(3, +1, 1.0)],           # class_number
    },
    "space_groups": {
        # features: [sg_number, point_group_order, is_symmorphic, crystal_system, lattice_type]
        "symmetry":   [(1, +1, 1.0)],           # point_group_order IS symmetry
        "rank":       [(3, +1, 0.6)],           # crystal_system ~ dimension proxy
        "complexity": [(0, +1, 0.5)],           # sg_number as rough complexity
    },
    "polytopes": {
        # features: [dimension, n_vertices, n_edges, n_facets, n_fvec, sum_fvec]
        "rank":       [(0, +1, 1.0)],           # dimension
        "complexity": [(5, +1, 0.8)],           # f-vector sum
        "symmetry":   [(1, +1, 0.5), (3, +1, 0.5)],  # vertices + facets ~ symmetry proxy
    },
    "materials": {
        # features: [band_gap, formation_energy, sg_number, density, log_volume, nsites]
        "spectral":   [(0, +1, 1.0)],           # band_gap IS spectral
        "complexity": [(4, +1, 0.7), (5, +1, 0.6)],  # volume + nsites
        "symmetry":   [(2, +1, 0.8)],           # sg_number
    },
    "fungrim": {
        # features: [type_idx, n_symbols, module_idx, formula_length]
        "complexity": [(3, +1, 0.7)],           # formula_length
        "rank":       [(1, +1, 0.6)],           # n_symbols ~ expressiveness
    },
    "knots": {
        # features: [crossing_number, determinant, alex_len, jones_len, conway_len,
        #            + alex_coeffs(7) + jones_coeffs(12) + conway_coeffs(4)]
        "complexity": [(0, +1, 1.0)],           # crossing_number
        "arithmetic": [(1, +1, 0.9)],           # determinant
        "spectral":   [(2, +1, 0.5), (3, +1, 0.5)],  # polynomial lengths
    },
    "maass": {
        # features: [level, weight, spectral_parameter, symmetry, fricke_eigenvalue, + 20 coeffs]
        "complexity": [(0, +1, 1.0)],           # level
        "spectral":   [(2, +1, 1.0), (4, +1, 0.7)],  # spectral_parameter + Fricke
        "symmetry":   [(3, +1, 0.8)],           # symmetry type
    },
    "ec_zeros": {
        # features: [log_conductor, rank, analytic_rank, torsion, root_number,
        #            first_zero, mean_spacing, spacing_std, spacing_ratio,
        #            n_zeros, low_zero_avg, high_zero_avg]
        "complexity": [(0, +1, 1.0)],           # conductor
        "rank":       [(1, +1, 1.0), (2, +1, 0.8)],  # rank + analytic
        "arithmetic": [(3, +1, 1.0)],           # torsion
        "symmetry":   [(4, +1, 0.7)],           # root_number
        "spectral":   [(5, +1, 1.0), (6, +1, 1.0), (7, +1, 0.8),
                       (8, +1, 0.7), (10, +1, 0.6), (11, +1, 0.6)],  # all zero stats
    },
    "rmt": {
        # features: [sp_mean, sp_var, sp_skew, sp_kurt,
        #            r_mean, r_var, r_min,
        #            sigma2_1, sigma2_2, sigma2_4,
        #            delta3_1, delta3_2,
        #            unf_mean_sp, unf_var_sp]
        # ALL features are pure spectral/GUE -- maps ONLY to Phasma (spectral)
        "spectral":   [(0, +1, 1.0), (1, +1, 1.0), (2, +1, 1.0), (3, +1, 1.0),
                       (4, +1, 1.0), (5, +1, 1.0), (6, +1, 1.0),
                       (7, +1, 1.0), (8, +1, 1.0), (9, +1, 1.0),
                       (10, +1, 1.0), (11, +1, 1.0),
                       (12, +1, 1.0), (13, +1, 1.0)],
    },
    "battery": {
        # features: [verdict_score, neg_log_p, z_score, real_val, null_mean,
        #            source_round, + 12 domain_involvement dims]
        "spectral":   [(2, +1, 0.9)],           # z_score as discriminant power
        "complexity": [(1, +1, 0.7)],           # neg_log_p as significance
    },
    "dissection": {
        # features: [priority, tractability, gpu, log_time, n_domains, + 12 domain_applicability]
        "complexity": [(3, +1, 0.7)],           # execution time
        "rank":       [(4, +1, 0.6)],           # domain coverage
    },
    "dynamics": {
        # Phasma (spectral): Lyapunov exponent is the spectral fingerprint of a dynamical system
        # features: [lyapunov, orbit_type, period, n_returns, n_terms,
        #            correlation, n_diagonal, unique_pairs, phase_density, log_n_terms]
        "spectral":   [(0, +1, 1.0), (5, +1, 0.7)],  # lyapunov + phase correlation = Phasma
        # Auxesis (growth): orbit complexity and phase space density measure growth/richness
        "complexity": [(8, +1, 0.8), (9, +1, 0.6)],  # phase_density + log_n_terms = Auxesis
        "rank":       [(7, +1, 0.7)],                 # unique_pairs ~ dimensional richness
        "symmetry":   [(1, +1, 0.6), (2, +1, 0.5)],  # orbit_type + period ~ dynamical symmetry
    },
    "metabolism": {
        # features: [n_reactions, n_metabolites, n_genes,
        #            mean_stoich_participants, max_stoich_participants,
        #            frac_reversible, n_compartments, n_subsystems,
        #            connectivity_ratio, gene_coverage, log_n_reactions]
        # Megethos (network size): reaction/metabolite/gene counts dominate
        "complexity": [(10, +1, 1.0), (7, +1, 0.7)],  # log_n_reactions + n_subsystems = network scale
        "rank":       [(6, +1, 0.8), (8, +1, 0.6)],   # n_compartments + connectivity = structural richness
        "symmetry":   [(5, +1, 0.7)],                  # frac_reversible ~ reaction symmetry (forward/backward)
        "arithmetic": [(3, +1, 0.6), (4, +1, 0.5)],   # stoichiometric participation = combinatorial complexity
        "spectral":   [(9, +1, 0.7)],                  # gene_coverage ~ functional coverage fingerprint
    },
    "chemistry": {
        # features: [A, B, C, mu, alpha, homo, lumo, gap,
        #            r2, zpve, cv, u0]
        # Molecular properties map naturally to physics phonemes
        "complexity": [(8, +1, 0.9), (4, +1, 0.7)],   # r2 (spatial extent) + alpha (polarizability) = molecular size
        "spectral":   [(5, +1, 1.0), (6, +1, 1.0), (7, +1, 0.9)],  # homo, lumo, gap = electronic spectrum
        "symmetry":   [(0, +1, 0.6), (1, +1, 0.6), (2, +1, 0.6)],  # rotational constants encode molecular symmetry
        "arithmetic": [(9, +1, 0.7), (10, +1, 0.6)],  # zpve + cv = vibrational/thermal complexity
    },
    "phase_space": {
        # Phasma (spectral): autocorrelation structure and Lyapunov exponent
        # features: [n_terms, autocorr_1, autocorr_2, autocorr_3, mutual_info,
        #            lyapunov, orbit_type, n_fixed_points, period, log_n_terms]
        "spectral":   [(5, +1, 1.0), (1, +1, 0.8), (2, +1, 0.7), (3, +1, 0.6)],  # lyapunov + autocorrs = Phasma
        # Auxesis (growth): mutual information and sequence length measure growth
        "complexity": [(4, +1, 0.8), (9, +1, 0.6)],  # mutual_info + log_n_terms = Auxesis
        "rank":       [(7, +1, 0.7)],                 # n_fixed_points ~ phase space dimension
        "symmetry":   [(6, +1, 0.6), (8, +1, 0.5)],  # orbit_type + period ~ dynamical symmetry
    },
    "spectral_sigs": {
        # Phasma (spectral essence): FFT decomposition of formula structure
        # features: [centroid, bandwidth, entropy, rolloff, + 10 top_magnitudes]
        "spectral":   [(0, +1, 1.0), (1, +1, 0.8), (3, +1, 0.7)],  # centroid + bandwidth + rolloff = Phasma
        "complexity": [(2, +1, 0.9)],              # entropy measures formula complexity
        "rank":       [(4, +1, 0.5), (5, +1, 0.4)],  # top magnitudes ~ spectral richness
    },
    "operadic_sigs": {
        # Taxis (order/structure): compositional skeleton of formulas
        # features: [n_ops, is_symmetric, arity_len, n_distinct_ops, mean_depth, max_depth, depth_spread]
        "symmetry":   [(1, +1, 1.0)],              # is_symmetric IS symmetry
        "complexity": [(0, +1, 0.9), (5, +1, 0.7)],  # n_ops + max_depth = structural complexity = Taxis
        "rank":       [(3, +1, 0.8), (2, +1, 0.6)],  # n_distinct_ops + arity_len ~ compositional richness
        "arithmetic": [(6, +1, 0.5)],              # depth_spread ~ nesting regularity
    },
    "codata": {
        # Megethos (magnitude): physical constants ARE magnitude — their value spans
        # 60+ orders of magnitude. log_abs_value and order_of_magnitude are Megethos.
        # features: [log_abs_value, sign, log_uncertainty, log_relative_unc,
        #            order_of_magnitude, is_dimensionless, unit_category,
        #            is_ratio, is_mass, is_magnetic]
        "complexity": [(0, +1, 1.0), (4, +1, 0.9)],   # log_abs_value + OoM = Megethos
        "spectral":   [(2, +1, 0.8), (3, +1, 0.9)],   # uncertainty structure = measurement spectral fingerprint
        "arithmetic": [(5, +1, 0.7), (7, +1, 0.6)],   # dimensionless + ratio = arithmetic purity
        "symmetry":   [(1, +1, 0.5)],                  # sign symmetry
    },
    "pdg_particles": {
        # Megethos (magnitude): particle mass spans 15+ orders of magnitude.
        # Phasma (spectral): width/lifetime is the spectral fingerprint of decay.
        # features: [log_mass, log_width, relative_mass_err, mass_err_asymmetry,
        #            is_stable, spin_2j+1, nq1, nq2, nq3, n_radial, is_hadron]
        "complexity": [(0, +1, 1.0)],                  # log_mass = Megethos (energy scale)
        "spectral":   [(1, +1, 1.0), (2, +1, 0.7)],   # log_width + rel_err = Phasma (decay spectrum)
        "symmetry":   [(5, +1, 1.0), (3, +1, 0.5)],   # spin = symmetry; err asymmetry = CP proxy
        "rank":       [(6, +1, 0.8), (7, +1, 0.8), (8, +1, 0.8)],  # quark content = compositeness/rank
        "arithmetic": [(9, +1, 0.6), (10, +1, 0.7)],  # radial excitation + hadron flag
    },
    "padic_sigs": {
        # Topos (place/locality): p-adic valuations encode local structure at each prime.
        # features: [n_seg_2, max_val_2, n_seg_3, max_val_3, n_seg_5, max_val_5,
        #            n_seg_7, max_val_7, n_seg_11, max_val_11]  (10 features)
        "arithmetic": [(1, +1, 1.0), (3, +1, 0.9), (5, +1, 0.8),
                       (7, +1, 0.7), (9, +1, 0.6)],   # max_valuation at each prime = p-adic arithmetic
        "complexity": [(0, +1, 0.8), (2, +1, 0.7), (4, +1, 0.6)],  # n_segments = Newton polygon complexity
    },
    "info_theoretic": {
        # Auxesis (growth): entropy and compression measure information growth/density.
        # features: [entropy, compression_ratio, lz_complexity, diff_entropy, n_terms]
        "complexity": [(0, +1, 1.0), (3, +1, 0.9)],   # entropy + diff_entropy = information complexity
        "rank":       [(2, +1, 0.8)],                  # lz_complexity ~ structural richness
        "arithmetic": [(1, +1, 0.7)],                  # compression_ratio = redundancy structure
    },
    "fractional_deriv": {
        # Phasma (spectral): fractional derivatives probe spectral structure at non-integer orders.
        # features: 9 entries of signature_vector (3 alphas x 3 eval points)
        "spectral":   [(0, +1, 1.0), (1, +1, 0.9), (2, +1, 0.8),
                       (3, +1, 0.7), (4, +1, 0.6), (5, +1, 0.5)],  # fractional spectral decomposition
        "complexity": [(6, +1, 0.6), (7, +1, 0.5), (8, +1, 0.4)],  # higher-order fractional features
    },
    "functional_eq": {
        # Symmetria: functional equations ARE symmetry — reflections, shifts, scalings.
        # features: [has_reflection, has_shift, has_scaling, has_multiplicative,
        #            has_duplication, n_reflections, n_shifts, n_scalings]
        "symmetry":   [(0, +1, 1.0), (1, +1, 0.9), (2, +1, 0.8),
                       (3, +1, 0.7), (4, +1, 0.6)],   # all symmetry type flags
        "complexity": [(5, +1, 0.8), (6, +1, 0.7), (7, +1, 0.6)],  # counts of each symmetry type
    },
    "resurgence": {
        # Phasma (spectral): Borel summability and Gevrey order are spectral/analytic invariants.
        # features: [radius_convergence, radius_root, radius_ratio, gevrey_order,
        #            gevrey_fit_r2, is_borel_summable, divergence_rate, growth_rate_tail, n_terms]
        "spectral":   [(0, +1, 1.0), (1, +1, 0.9), (2, +1, 0.8),
                       (3, +1, 1.0)],                  # convergence radii + Gevrey = spectral fingerprint
        "complexity": [(6, +1, 0.8), (7, +1, 0.7)],   # divergence/growth rates = analytic complexity
        "arithmetic": [(5, +1, 0.7)],                  # is_borel_summable = summability arithmetic
    },
    "disagreement": {
        # Disagreement atlas: objects where analysis methods disagree.
        # features: [log_conductor, rank, torsion, cm, jaccard, precision_score,
        #            recall_score, zero_coherence, graph_degree, component_size,
        #            n_zero_nn, n_graph_nn, n_overlap, disagreement_type]
        "complexity": [(0, +1, 1.0)],                  # log_conductor = scale
        "rank":       [(1, +1, 1.0)],                  # rank
        "arithmetic": [(2, +1, 1.0), (3, +1, 0.7)],   # torsion + CM flag
        "spectral":   [(4, +1, 0.9), (5, +1, 0.8), (6, +1, 0.8),
                       (7, +1, 0.9)],                  # jaccard, precision, recall, zero_coherence
        "symmetry":   [(13, +1, 0.5)],                 # disagreement_type as categorical symmetry
    },
    "knowledge_graph": {
        # Knowledge graph per-object summary from graph_edges.
        # features: [log_degree, mean_weight, frac_isogeny, frac_modularity,
        #            frac_twist, log_n_isogeny]
        "complexity": [(0, +1, 1.0)],                  # log_degree = connectivity complexity
        "rank":       [(0, +1, 0.7)],                  # degree also measures structural richness
        "spectral":   [(1, +1, 0.8)],                  # mean_weight = edge spectral fingerprint
        "symmetry":   [(2, +1, 0.7), (4, +1, 0.6)],   # isogeny/twist fractions encode symmetry structure
        "arithmetic": [(3, +1, 0.8)],                  # modularity fraction = arithmetic bridge
    },
    "bridges": {
        # Known cross-domain bridges per source object.
        # features: [log_n_bridges, verified_fraction, modularity_fraction, n_bridges]
        "complexity": [(0, +1, 0.8)],                  # log_n_bridges = bridge complexity
        "arithmetic": [(2, +1, 1.0)],                  # modularity_fraction = arithmetic connection
        "symmetry":   [(1, +1, 0.6)],                  # verified_fraction as quality/symmetry proxy
    },
    "lmfdb_objects": {
        # LMFDB objects with 50-dim invariant vectors.
        # features: [log_conductor, inv_vec(50), coeff_completeness, zeros_completeness, object_type]
        # The invariant vector spans all phoneme axes at once.
        "complexity": [(0, +1, 1.0)],                  # log_conductor = scale
        "spectral":   [(1, +1, 0.5), (2, +1, 0.5), (3, +1, 0.5),
                       (4, +1, 0.5), (5, +1, 0.5)],   # first invariant components as spectral
        "rank":       [(51, +1, 0.7)],                 # coeff_completeness ~ data richness
        "arithmetic": [(52, +1, 0.7)],                 # zeros_completeness ~ analytic depth
    },
}


class PhonemeProjector:
    """
    Projects domain-specific features into universal phoneme space.

    Each mathematical object gets a 5D phoneme vector:
    [complexity, rank, symmetry, arithmetic, spectral]

    The projection is explicit and interpretable — not learned.
    """

    def __init__(self, domains: list[DomainIndex], device: str = "cpu"):
        self.domains = domains
        self.device = device
        self.n_phonemes = len(PHONEMES)

        # Precompute phoneme vectors for all objects in all domains
        self._phoneme_vecs = []
        for dom in domains:
            pmap = DOMAIN_PHONEME_MAP.get(dom.name, {})
            vecs = torch.zeros(dom.n_objects, self.n_phonemes, device=device)

            for p_idx, phoneme in enumerate(PHONEMES):
                if phoneme in pmap:
                    for feat_idx, sign, weight in pmap[phoneme]:
                        if feat_idx < dom.n_features:
                            vecs[:, p_idx] += sign * weight * dom.features[:, feat_idx].to(device)

            # Normalize each phoneme axis to zero mean, unit variance
            mu = vecs.mean(dim=0)
            sigma = vecs.std(dim=0).clamp(min=1e-8)
            vecs = (vecs - mu) / sigma
            vecs[torch.isnan(vecs)] = 0.0

            self._phoneme_vecs.append(vecs)

    def get_phonemes(self, domain_idx: int, obj_indices: torch.Tensor) -> torch.Tensor:
        """Get phoneme vectors for objects. Returns (batch, 5)."""
        return self._phoneme_vecs[domain_idx][obj_indices]


class PhonemeCoupling:
    """
    Coupling scorer in universal phoneme space.

    Measures whether objects from different domains land in the same
    region of phoneme space. Uses L2 distance in the 5D phoneme space
    transformed to a coupling score.

    This should:
    - PASS when domains share phonemic coordinates (EC conductor ~ MF level)
    - FAIL when domains have no phonemic overlap (knots ~ materials)
    """

    def __init__(self, domains: list[DomainIndex], device: str = "cpu"):
        self.domains = domains
        self.n_domains = len(domains)
        self.device = device
        self.projector = PhonemeProjector(domains, device)

    def __call__(self, *grid_indices) -> torch.Tensor:
        indices = torch.stack(grid_indices, dim=-1)
        return self.score_batch(indices)

    def score_batch(self, indices: torch.Tensor) -> torch.Tensor:
        batch_size = indices.shape[0]

        # Get phoneme vectors for all domains
        phonemes = []
        for d in range(self.n_domains):
            phonemes.append(self.projector.get_phonemes(d, indices[:, d].long()))

        # Coupling score: inverse of mean pairwise L2 distance in phoneme space
        n_pairs = 0
        total_dist = torch.zeros(batch_size, device=self.device)
        for i in range(self.n_domains):
            for j in range(i + 1, self.n_domains):
                dist = ((phonemes[i] - phonemes[j]) ** 2).sum(dim=1).sqrt()
                total_dist += dist
                n_pairs += 1

        mean_dist = total_dist / max(n_pairs, 1)

        # Per-phoneme coupling: which phonemes are BOTH active in both domains?
        # Only count distance on phonemes where both domains have nonzero mapping
        phoneme_active = torch.zeros(batch_size, device=self.device)
        for i in range(self.n_domains):
            for j in range(i + 1, self.n_domains):
                # Per-phoneme squared distance, masked by mutual activity
                per_phoneme = (phonemes[i] - phonemes[j]) ** 2  # (batch, 5)
                # Check if both domains have this phoneme mapped
                for p_idx in range(self.projector.n_phonemes):
                    d1_has = abs(phonemes[i][:, p_idx]).mean() > 0.01
                    d2_has = abs(phonemes[j][:, p_idx]).mean() > 0.01
                    if d1_has and d2_has:
                        phoneme_active += torch.exp(-per_phoneme[:, p_idx])

        # Normalize by number of shared phonemes
        n_shared = 0
        for p_idx in range(self.projector.n_phonemes):
            any_pair_shared = False
            for i in range(self.n_domains):
                for j in range(i + 1, self.n_domains):
                    d1_has = self._phoneme_present(i, p_idx)
                    d2_has = self._phoneme_present(j, p_idx)
                    if d1_has and d2_has:
                        any_pair_shared = True
            if any_pair_shared:
                n_shared += 1

        if n_shared == 0:
            return torch.zeros(batch_size, device=self.device)

        score = phoneme_active / (n_shared * max(n_pairs, 1))
        return score

    def _phoneme_present(self, domain_idx: int, phoneme_idx: int) -> bool:
        """Check if a domain has a nonzero mapping for a phoneme."""
        dom_name = self.domains[domain_idx].name
        pmap = DOMAIN_PHONEME_MAP.get(dom_name, {})
        phoneme = PHONEMES[phoneme_idx]
        return phoneme in pmap and any(w > 0 for _, _, w in pmap[phoneme])


class KosmosCoupling:
    """
    Coupling scorer in the TRUE coordinate system of the Kosmos.

    Instead of measuring distance in the 5 phoneme axes (which are
    51.4% rotated from truth), rotates into the PCA-discovered true
    axes before computing coupling. This should improve both
    sensitivity and specificity.
    """

    def __init__(self, domains: list[DomainIndex], device: str = "cpu"):
        self.domains = domains
        self.n_domains = len(domains)
        self.device = device
        self.projector = PhonemeProjector(domains, device)

        # Load or compute the rotation matrix
        rotation_path = Path(__file__).resolve().parent.parent / "data" / "kosmos_rotation.pt"
        if rotation_path.exists():
            self.rotation = torch.load(rotation_path, weights_only=True).to(device)
        else:
            # Fallback: identity (no rotation)
            self.rotation = torch.eye(self.projector.n_phonemes, device=device)

    def __call__(self, *grid_indices) -> torch.Tensor:
        indices = torch.stack(grid_indices, dim=-1)
        return self.score_batch(indices)

    def score_batch(self, indices: torch.Tensor) -> torch.Tensor:
        batch_size = indices.shape[0]

        # Get phoneme vectors and rotate to true axes
        phonemes = []
        for d in range(self.n_domains):
            raw = self.projector.get_phonemes(d, indices[:, d].long())
            rotated = raw @ self.rotation.T  # (batch, 5) in true coordinates
            phonemes.append(rotated)

        # Weighted distance: Megethos (axis 0) carries 44% of variance,
        # so weight each axis by its explained variance
        axis_weights = torch.tensor([0.468, 0.185, 0.150, 0.108, 0.090],
                                     device=self.device)

        n_pairs = 0
        total_score = torch.zeros(batch_size, device=self.device)
        for i in range(self.n_domains):
            for j in range(i + 1, self.n_domains):
                diff = phonemes[i] - phonemes[j]
                weighted_dist = (diff ** 2 * axis_weights).sum(dim=1).sqrt()
                total_score += torch.exp(-weighted_dist ** 2 / 2.0)
                n_pairs += 1

        return total_score / max(n_pairs, 1)


def phoneme_profile(domain_name: str) -> dict:
    """
    Show which phonemes a domain maps to.
    Useful for understanding cross-domain compatibility.
    """
    pmap = DOMAIN_PHONEME_MAP.get(domain_name, {})
    profile = {}
    for phoneme in PHONEMES:
        if phoneme in pmap:
            mappings = pmap[phoneme]
            total_weight = sum(w for _, _, w in mappings)
            profile[phoneme] = total_weight
        else:
            profile[phoneme] = 0.0
    return profile


def phoneme_compatibility(d1: str, d2: str) -> dict:
    """
    Compute phonemic compatibility between two domains.
    High overlap = more likely to show real cross-domain structure.
    """
    p1 = phoneme_profile(d1)
    p2 = phoneme_profile(d2)

    shared = {}
    for phoneme in PHONEMES:
        w1 = p1.get(phoneme, 0)
        w2 = p2.get(phoneme, 0)
        shared[phoneme] = min(w1, w2)

    total_shared = sum(shared.values())
    total_possible = sum(max(p1.get(p, 0), p2.get(p, 0)) for p in PHONEMES)
    compatibility = total_shared / max(total_possible, 0.1)

    return {
        "d1": d1, "d2": d2,
        "d1_profile": p1, "d2_profile": p2,
        "shared_phonemes": shared,
        "compatibility": compatibility,
    }


def print_phoneme_table():
    """Print the full phoneme mapping table across all domains."""
    print(f"{'Domain':>18} | {'complex':>8} {'rank':>8} {'symm':>8} {'arith':>8} {'spectral':>8} | total")
    print("-" * 80)
    for domain in DOMAIN_PHONEME_MAP:
        p = phoneme_profile(domain)
        total = sum(p.values())
        print(f"{domain:>18} | {p['complexity']:>8.1f} {p['rank']:>8.1f} "
              f"{p['symmetry']:>8.1f} {p['arithmetic']:>8.1f} {p['spectral']:>8.1f} | {total:.1f}")
