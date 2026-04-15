#!/usr/bin/env python3
"""
Constrained Mutation Operators — Domain-aware variants that never produce
hypotheses with mismatched domain/feature pairs.

Drop-in replacements for gene_schema's mutate_single, crossover, and
random_hypothesis. These enforce ACTIVE_FEATURES so the executor never
hits data_unavailable for feature mismatches.
"""
import random
from dataclasses import asdict

import sys
from pathlib import Path
_forge_v3 = str(Path(__file__).resolve().parent.parent / "forge/v3")
if _forge_v3 not in sys.path:
    sys.path.insert(0, _forge_v3)

from gene_schema import (
    Hypothesis, ACTIVE_DOMAINS, ACTIVE_FEATURES,
    COUPLINGS, CONDITIONINGS, NULL_MODELS, RESOLUTIONS,
    PREDICTIONS, PREDICTED_KILLS, NOVELTY_TAGS,
)


def _valid_feature(domain, rng):
    """Pick a random feature that actually exists for this domain."""
    features = ACTIVE_FEATURES.get(domain)
    if features:
        return rng.choice(features)
    # Fallback: shouldn't happen with ACTIVE_DOMAINS
    return "conductor"


def _fix_feature(hypothesis):
    """Ensure features are valid for their domains. Reassign if not."""
    af_a = ACTIVE_FEATURES.get(hypothesis.domain_a, [])
    af_b = ACTIVE_FEATURES.get(hypothesis.domain_b, [])
    if hypothesis.feature_a not in af_a and af_a:
        hypothesis.feature_a = random.choice(af_a)
    if hypothesis.feature_b not in af_b and af_b:
        hypothesis.feature_b = random.choice(af_b)
    return hypothesis


def random_hypothesis(gen, rng=None):
    """Generate a random hypothesis with guaranteed valid domain/feature pairs."""
    if rng is None:
        rng = random.Random()

    dom_a = rng.choice(ACTIVE_DOMAINS)
    dom_b = rng.choice(ACTIVE_DOMAINS)

    return Hypothesis(
        id=f"hyp_g{gen}_{rng.randint(0, 99999):05d}",
        domain_a=dom_a,
        domain_b=dom_b,
        feature_a=_valid_feature(dom_a, rng),
        feature_b=_valid_feature(dom_b, rng),
        coupling=rng.choice(COUPLINGS),
        conditioning=rng.choice(CONDITIONINGS),
        null_model=rng.choice(NULL_MODELS),
        resolution=rng.choice(RESOLUTIONS),
        prediction=rng.choice(PREDICTIONS),
        predicted_kill=rng.choice(PREDICTED_KILLS),
        novelty_tag=rng.choice(NOVELTY_TAGS),
        generation=gen,
    )


def mutate_single(parent, gen, rng=None):
    """Mutate one slot, keeping domain/feature pairs consistent."""
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

    if slot == "domain_a":
        child.domain_a = rng.choice(ACTIVE_DOMAINS)
        # Re-pick feature_a to match new domain
        child.feature_a = _valid_feature(child.domain_a, rng)
    elif slot == "domain_b":
        child.domain_b = rng.choice(ACTIVE_DOMAINS)
        child.feature_b = _valid_feature(child.domain_b, rng)
    elif slot == "feature_a":
        child.feature_a = _valid_feature(child.domain_a, rng)
    elif slot == "feature_b":
        child.feature_b = _valid_feature(child.domain_b, rng)
    elif slot == "coupling":
        child.coupling = rng.choice(COUPLINGS)
    elif slot == "conditioning":
        child.conditioning = rng.choice(CONDITIONINGS)
    elif slot == "null_model":
        child.null_model = rng.choice(NULL_MODELS)
    elif slot == "resolution":
        child.resolution = rng.choice(RESOLUTIONS)

    return child


def crossover(parent_a, parent_b, gen, rng=None):
    """Crossover with domain/feature consistency enforced."""
    if rng is None:
        rng = random.Random()

    # Pick domains from either parent
    dom_a = parent_a.domain_a if rng.random() < 0.5 else parent_b.domain_a
    dom_b = parent_a.domain_b if rng.random() < 0.5 else parent_b.domain_b

    # For features: prefer inheriting from the parent that shares the domain,
    # otherwise pick a valid feature for the chosen domain
    if rng.random() < 0.5 and parent_a.domain_a == dom_a:
        feat_a = parent_a.feature_a
    elif parent_b.domain_a == dom_a:
        feat_a = parent_b.feature_a
    else:
        feat_a = _valid_feature(dom_a, rng)

    if rng.random() < 0.5 and parent_a.domain_b == dom_b:
        feat_b = parent_a.feature_b
    elif parent_b.domain_b == dom_b:
        feat_b = parent_b.feature_b
    else:
        feat_b = _valid_feature(dom_b, rng)

    # Final safety check
    af_a = ACTIVE_FEATURES.get(dom_a, [])
    af_b = ACTIVE_FEATURES.get(dom_b, [])
    if feat_a not in af_a and af_a:
        feat_a = rng.choice(af_a)
    if feat_b not in af_b and af_b:
        feat_b = rng.choice(af_b)

    child = Hypothesis(
        id=f"hyp_g{gen}_{rng.randint(0, 99999):05d}",
        domain_a=dom_a,
        domain_b=dom_b,
        feature_a=feat_a,
        feature_b=feat_b,
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
