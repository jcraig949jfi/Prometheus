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
