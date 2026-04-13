#!/usr/bin/env python3
"""
Gene Schema: The structured hypothesis format for the autonomous explorer.

Each hypothesis is a fixed-schema JSON object with controlled vocabularies.
A 7B local model fills slots by selection, not reasoning.
Mutation = swapping 1-2 slots between parents.
Validation = schema check against vocabulary.
"""
import json
import random
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional

# ============================================================
# Controlled Vocabularies
# ============================================================

DOMAINS = [
    "elliptic_curves", "modular_forms", "number_fields", "genus2_curves",
    "maass_forms", "knots", "lattices", "isogenies", "oeis", "polytopes",
    "space_groups", "fungrim", "findstat", "metamath", "mathlib", "mmlkg",
    "dirichlet_zeros", "ec_zeros", "materials", "superconductors",
    "chemistry_qm9", "metabolism", "finance_ff", "source_code_scipy",
]

FEATURES = [
    # Arithmetic
    "conductor", "log_conductor", "rank", "analytic_rank", "torsion",
    "class_number", "regulator", "discriminant", "log_discriminant",
    "n_bad_primes", "omega_conductor",
    # Spectral
    "first_zero", "zero_spacing_1_2", "zero_spacing_2_3", "zero_density_tail",
    "spectral_parameter", "nn_spacing_ratio",
    # Coefficient
    "ap_mod2_fingerprint", "ap_mod3_fingerprint", "ap_mod5_fingerprint",
    "ap_compression_lz", "ap_compression_st", "ap_mean_abs", "ap_kurtosis",
    "coefficient_entropy", "coefficient_autocorrelation",
    # Structural
    "crossing_number", "determinant", "alexander_degree", "jones_degree",
    "dimension", "f_vector_sum", "kissing_number",
    # Graph/topology
    "congruence_degree_mod2", "congruence_degree_mod3", "congruence_degree_mod5",
    "isogeny_class_size", "graph_diameter", "graph_clustering",
    # Physics/chemistry
    "homo_lumo_gap", "formation_energy", "band_gap", "density", "volume",
    "n_atoms", "zpve", "polarizability",
    # Meta
    "n_symbols", "module_depth", "proof_length", "import_degree",
]

COUPLINGS = [
    "spearman", "pearson", "mutual_information", "wasserstein",
    "ks_statistic", "ttcross_bond", "cosine_similarity",
]

CONDITIONINGS = [
    "none", "log_conductor", "rank", "torsion", "cm_flag",
    "degree", "level", "weight", "n_atoms", "crossing_number",
]

NULL_MODELS = [
    "permutation", "shuffle_within_group", "block_shuffle",
    "synthetic_gue", "synthetic_poisson", "random_integers",
]

RESOLUTIONS = [100, 500, 2000, 5000, 10000]

PREDICTIONS = [
    "positive_correlation", "negative_correlation", "no_effect",
    "threshold_effect", "nonlinear",
]

PREDICTED_KILLS = [
    "F1_permutation_null", "F3_effect_size", "F5_normalization",
    "F12_partial_correlation", "F17_confound_sensitivity",
    "F24_eta_squared", "F24b_tail_driven", "F25_transportability",
    "F29_distributional", "F30_range_artifact", "F31_prime_mediated",
    "F33_rank_sort", "F34_trivial_baseline", "F35_false_positive",
    "F36_partial_strengthening", "F37_feature_engineering",
    "F38_raw_data", "unknown",
]

NOVELTY_TAGS = [
    "magnitude", "ordinal", "spectral", "topological",
    "information_theoretic", "algebraic", "dynamical", "cross_domain",
]

# Domains with actual data loaded in executor
ACTIVE_DOMAINS = [
    "elliptic_curves", "modular_forms", "number_fields", "genus2_curves",
    "maass_forms", "knots", "superconductors",
]

# Features that actually extract from active domains
ACTIVE_FEATURES = {
    "elliptic_curves": ["conductor", "log_conductor", "rank", "torsion", "n_bad_primes",
                         "ap_kurtosis", "ap_compression_lz"],
    "modular_forms": ["level", "weight", "dim"],
    "number_fields": ["discriminant", "log_discriminant", "class_number", "regulator", "degree"],
    "genus2_curves": ["conductor", "log_conductor", "discriminant", "torsion", "root_number"],
    "maass_forms": ["level", "spectral_parameter", "coefficient_entropy"],
    "knots": ["crossing_number", "determinant", "alexander_degree", "jones_degree"],
    "superconductors": ["tc"],
}


# ============================================================
# Gene Dataclass
# ============================================================

@dataclass
class Hypothesis:
    """A structured, machine-readable mathematical hypothesis."""
    id: str = ""
    domain_a: str = "elliptic_curves"
    domain_b: str = "modular_forms"
    feature_a: str = "conductor"
    feature_b: str = "level"
    coupling: str = "spearman"
    conditioning: str = "none"
    null_model: str = "permutation"
    resolution: int = 2000
    prediction: str = "positive_correlation"
    predicted_kill: str = "unknown"
    novelty_tag: str = "algebraic"
    generation: int = 0
    parent_a: str = ""
    parent_b: str = ""
    fitness: float = 0.0
    survival_depth: int = 0  # how many F-tests passed before death
    kill_test: str = ""  # which test killed it (empty if survived)
    notes: str = ""

    def to_json(self):
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, s):
        d = json.loads(s) if isinstance(s, str) else s
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def validate(self):
        """Check all fields against controlled vocabularies."""
        errors = []
        if self.domain_a not in DOMAINS:
            errors.append(f"domain_a '{self.domain_a}' not in vocabulary")
        if self.domain_b not in DOMAINS:
            errors.append(f"domain_b '{self.domain_b}' not in vocabulary")
        if self.feature_a not in FEATURES:
            errors.append(f"feature_a '{self.feature_a}' not in vocabulary")
        if self.feature_b not in FEATURES:
            errors.append(f"feature_b '{self.feature_b}' not in vocabulary")
        if self.coupling not in COUPLINGS:
            errors.append(f"coupling '{self.coupling}' not in vocabulary")
        if self.conditioning not in CONDITIONINGS:
            errors.append(f"conditioning '{self.conditioning}' not in vocabulary")
        if self.null_model not in NULL_MODELS:
            errors.append(f"null_model '{self.null_model}' not in vocabulary")
        if self.resolution not in RESOLUTIONS:
            errors.append(f"resolution {self.resolution} not in vocabulary")
        if self.prediction not in PREDICTIONS:
            errors.append(f"prediction '{self.prediction}' not in vocabulary")
        if self.novelty_tag not in NOVELTY_TAGS:
            errors.append(f"novelty_tag '{self.novelty_tag}' not in vocabulary")
        return errors


# ============================================================
# Mutation Operators (no LLM needed)
# ============================================================

def mutate_single(parent: Hypothesis, gen: int, rng=None) -> Hypothesis:
    """Mutate one random slot of a hypothesis."""
    if rng is None:
        rng = random.Random()

    child = Hypothesis(**asdict(parent))
    child.id = f"hyp_g{gen}_{rng.randint(0, 99999):05d}"
    child.generation = gen
    child.parent_a = parent.id
    child.parent_b = ""
    child.fitness = 0.0
    child.survival_depth = 0
    child.kill_test = ""

    slot = rng.choice([
        "domain_a", "domain_b", "feature_a", "feature_b",
        "coupling", "conditioning", "null_model", "resolution",
    ])

    vocabs = {
        "domain_a": DOMAINS, "domain_b": DOMAINS,
        "feature_a": FEATURES, "feature_b": FEATURES,
        "coupling": COUPLINGS, "conditioning": CONDITIONINGS,
        "null_model": NULL_MODELS, "resolution": RESOLUTIONS,
    }

    new_val = rng.choice(vocabs[slot])
    setattr(child, slot, new_val)
    return child


def crossover(parent_a: Hypothesis, parent_b: Hypothesis, gen: int, rng=None) -> Hypothesis:
    """Crossover: take domain/features from one parent, coupling/conditioning from other."""
    if rng is None:
        rng = random.Random()

    child = Hypothesis(
        id=f"hyp_g{gen}_{rng.randint(0, 99999):05d}",
        domain_a=parent_a.domain_a if rng.random() < 0.5 else parent_b.domain_a,
        domain_b=parent_a.domain_b if rng.random() < 0.5 else parent_b.domain_b,
        feature_a=parent_a.feature_a if rng.random() < 0.5 else parent_b.feature_a,
        feature_b=parent_a.feature_b if rng.random() < 0.5 else parent_b.feature_b,
        coupling=parent_a.coupling if rng.random() < 0.5 else parent_b.coupling,
        conditioning=parent_a.conditioning if rng.random() < 0.5 else parent_b.conditioning,
        null_model=parent_a.null_model if rng.random() < 0.5 else parent_b.null_model,
        resolution=parent_a.resolution if rng.random() < 0.5 else parent_b.resolution,
        prediction=parent_a.prediction,
        predicted_kill=parent_a.predicted_kill,
        novelty_tag=parent_a.novelty_tag if rng.random() < 0.5 else parent_b.novelty_tag,
        generation=gen,
        parent_a=parent_a.id,
        parent_b=parent_b.id,
    )
    return child


def random_hypothesis(gen: int, rng=None, active_only=True) -> Hypothesis:
    """Generate a random hypothesis, biased toward domains with data."""
    if rng is None:
        rng = random.Random()

    if active_only:
        dom_a = rng.choice(ACTIVE_DOMAINS)
        dom_b = rng.choice(ACTIVE_DOMAINS)
        feat_a = rng.choice(ACTIVE_FEATURES.get(dom_a, FEATURES))
        feat_b = rng.choice(ACTIVE_FEATURES.get(dom_b, FEATURES))
    else:
        dom_a = rng.choice(DOMAINS)
        dom_b = rng.choice(DOMAINS)
        feat_a = rng.choice(FEATURES)
        feat_b = rng.choice(FEATURES)

    return Hypothesis(
        id=f"hyp_g{gen}_{rng.randint(0, 99999):05d}",
        domain_a=dom_a,
        domain_b=dom_b,
        feature_a=feat_a,
        feature_b=feat_b,
        coupling=rng.choice(COUPLINGS),
        conditioning=rng.choice(CONDITIONINGS),
        null_model=rng.choice(NULL_MODELS),
        resolution=rng.choice(RESOLUTIONS),
        prediction=rng.choice(PREDICTIONS),
        predicted_kill=rng.choice(PREDICTED_KILLS),
        novelty_tag=rng.choice(NOVELTY_TAGS),
        generation=gen,
    )


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    import random as _random
    rng = _random.Random(42)

    print("Gene Schema Test")
    print("=" * 60)

    # Generate random
    h1 = random_hypothesis(0, rng)
    print(f"Random hypothesis:")
    print(h1.to_json())
    errors = h1.validate()
    print(f"Validation: {'PASS' if not errors else errors}")

    # Mutate
    h2 = mutate_single(h1, 1, rng)
    print(f"\nMutated (1 slot changed):")
    print(h2.to_json())

    # Crossover
    h3 = random_hypothesis(0, rng)
    h4 = crossover(h1, h3, 1, rng)
    print(f"\nCrossover child:")
    print(h4.to_json())

    # Stats
    print(f"\nVocabulary sizes:")
    print(f"  Domains: {len(DOMAINS)}")
    print(f"  Features: {len(FEATURES)}")
    print(f"  Couplings: {len(COUPLINGS)}")
    print(f"  Conditionings: {len(CONDITIONINGS)}")
    print(f"  Null models: {len(NULL_MODELS)}")
    print(f"  Total hypothesis space: ~{len(DOMAINS)**2 * len(FEATURES)**2 * len(COUPLINGS) * len(CONDITIONINGS) * len(NULL_MODELS) * len(RESOLUTIONS):.1e}")
