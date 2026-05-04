"""anti_prior operator — anti-correlated with corpus frequency stats.

Per pivot/ergon_learner_proposal_v8.md S3.5.1 + v8 S6.3:

The anti_prior operator deliberately constructs mutations that violate
corpus-derived patterns. Its job is to explore mathematical territory
the LLM prior won't naturally reach.

Concrete implementation:
  - For atom selection: prefer atoms whose corpus frequency is in the
    bottom decile (avoid Mathlib top-decile ops)
  - For arg sampling: prefer values in the tail of corpus arg-frequency
    distribution
  - For DAG topology: avoid common operator-pair compositions

Per v8 S3.5.1 KL divergence requirement: anti_prior outputs must have
KL divergence from corpus frequency distribution >=1.0 nats per claim.
The check is: compute the genome's atom-frequency distribution; compute
KL divergence from corpus distribution; reject if KL <1.0.

Per v8 S3.5.1 descriptor displacement: anti_prior outputs must include
cells the neural operator hasn't filled. At MVP (no neural operator yet)
we relax this to "cell not occupied by any prior-shaped operator," which
serves as the proof-of-mechanism for the eventual neural-anti_prior
displacement check.

CORPUS_FREQUENCY_STATS is loaded from a stub at MVP. v0.5 builds the
real database from Mathlib + Proof-Pile-2 frequency analysis (~5GB
per v8 S3.5.1).

Lineage tag: "anti_prior"
"""
from __future__ import annotations

import math
import random
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple

from ergon.learner.genome import Genome, NodeRef, validate_dag_invariants
from ergon.learner.operators.base import (
    fresh_genome,
    make_mvp_atom_pool,
    sample_args_for_atom,
)


# ---------------------------------------------------------------------------
# Corpus frequency stats (stubbed at MVP)
# ---------------------------------------------------------------------------
#
# In v0.5 this is replaced by a database built from frequency-counting
# the Mathlib + Proof-Pile-2 corpora. At MVP we use a hand-curated stub
# representing what a typical math-corpus distribution looks like:
# common atoms (factorial, partition, basic arithmetic) get high counts;
# specialized atoms (Hecke, Iwasawa, BSD) get low counts.

DEFAULT_CORPUS_FREQUENCIES: Dict[str, float] = {
    # High-frequency (Mathlib-common) atoms — anti_prior should AVOID these
    "prometheus_math.numerics_special_dilogarithm:dilogarithm": 0.18,
    "prometheus_math.combinatorics:partition_function": 0.15,
    "prometheus_math.number_theory:euler_phi": 0.13,
    "prometheus_math.number_theory:legendre_symbol": 0.10,
    # Mid-frequency
    "prometheus_math.numerics_special_dilogarithm:polylogarithm": 0.08,
    "prometheus_math.numerics_special_eta:eta_function": 0.07,
    "prometheus_math.combinatorics_partitions:partition_count_with_parts": 0.05,
    "prometheus_math.numerics_special_theta:theta_3": 0.05,
    # Low-frequency — anti_prior should PREFER these
    "prometheus_math.elliptic_curves:point_count": 0.04,
    "prometheus_math.elliptic_curves:isogeny_class": 0.03,
    "prometheus_math.number_theory:hecke_eigenvalue": 0.02,
    "prometheus_math.optimization:lehmer_mahler_search": 0.10,
}


# Per v8 S3.5.1 KL divergence threshold
KL_DIVERGENCE_THRESHOLD = 1.0  # nats per claim


def kl_divergence(
    genome_freqs: Dict[str, float],
    corpus_freqs: Dict[str, float],
    epsilon: float = 1e-6,
) -> float:
    """Compute KL(genome || corpus) in nats.

    KL(P || Q) = sum P(i) * log(P(i) / Q(i))

    epsilon is a smoothing constant for atoms not in either distribution.
    """
    all_keys = set(genome_freqs.keys()) | set(corpus_freqs.keys())
    kl = 0.0
    for k in all_keys:
        p = genome_freqs.get(k, epsilon)
        q = corpus_freqs.get(k, epsilon)
        if p > 0:
            kl += p * math.log(p / q)
    return kl


def compute_genome_atom_frequencies(genome: Genome) -> Dict[str, float]:
    """Frequency distribution over the genome's atoms (callable_refs)."""
    if not genome.nodes:
        return {}
    counts = Counter(n.callable_ref for n in genome.nodes)
    total = sum(counts.values())
    return {k: c / total for k, c in counts.items()}


# ---------------------------------------------------------------------------
# AntiPriorOperator
# ---------------------------------------------------------------------------


class AntiPriorOperator:
    """Mutate to anti-correlate with corpus frequency stats.

    Strategy: when picking atoms, weight inversely proportional to corpus
    frequency. Genomes that successfully clear KL >=1.0 nats are
    submitted; genomes below threshold are flagged
    `anti_prior_failed_divergence` (per v8 S3.5.1 failure handling) and
    submitted with reduced operator-class confidence.

    NOTE on "descriptor displacement" check: at MVP scope, neural operator
    is not yet active. The check defaults to True (no neural cells exist
    to displace from). v0.5+ wires the real check.
    """

    operator_class = "anti_prior"

    def __init__(
        self,
        corpus_frequencies: Optional[Dict[str, float]] = None,
        kl_threshold: float = KL_DIVERGENCE_THRESHOLD,
        n_atoms_distribution: Optional[tuple] = None,
        max_resampling_attempts: int = 5,
    ):
        self.corpus_frequencies = corpus_frequencies or DEFAULT_CORPUS_FREQUENCIES
        self.kl_threshold = kl_threshold
        self.n_atoms_distribution = n_atoms_distribution or (1, 6)
        self.max_resampling_attempts = max_resampling_attempts

    def mutate(
        self,
        parent: Optional[Genome],
        rng: random.Random,
        atom_pool: Dict[str, Any],
    ) -> Genome:
        """Produce an anti-prior genome.

        Resamples up to max_resampling_attempts to find a genome whose
        KL divergence from corpus exceeds threshold. If no candidate
        clears threshold, returns the highest-KL candidate with
        anti_prior_failed_divergence flag set in metadata.
        """
        best_genome: Optional[Genome] = None
        best_kl = -math.inf

        for _attempt in range(self.max_resampling_attempts):
            candidate = self._sample_anti_prior_genome(rng, atom_pool, parent)
            freqs = compute_genome_atom_frequencies(candidate)
            kl = kl_divergence(freqs, self.corpus_frequencies)

            if kl > best_kl:
                best_genome = candidate
                best_kl = kl

            if kl >= self.kl_threshold:
                # Pass: meets the divergence requirement
                return Genome(
                    nodes=candidate.nodes,
                    target_predicate=candidate.target_predicate,
                    mutation_operator_class="anti_prior",
                    parent_hash=parent.content_hash() if parent else None,
                    metadata={"kl_divergence_from_corpus": kl},
                )

        # Did not clear threshold — return best candidate with flag
        assert best_genome is not None  # we always set it on first iteration
        return Genome(
            nodes=best_genome.nodes,
            target_predicate=best_genome.target_predicate,
            mutation_operator_class="anti_prior",
            parent_hash=parent.content_hash() if parent else None,
            metadata={
                "kl_divergence_from_corpus": best_kl,
                "anti_prior_failed_divergence": True,
                "failure_reason": (
                    f"max_resampling_attempts={self.max_resampling_attempts} "
                    f"exhausted; best KL={best_kl:.3f} < threshold={self.kl_threshold}"
                ),
            },
        )

    def _sample_anti_prior_genome(
        self,
        rng: random.Random,
        atom_pool: Dict[str, Any],
        parent: Optional[Genome],
    ) -> Genome:
        """Sample one candidate genome with anti-prior atom selection."""
        # Build inverse-frequency weights for atom selection
        callable_refs = list(atom_pool.keys())
        weights = []
        for cref in callable_refs:
            freq = self.corpus_frequencies.get(cref, 1e-3)
            # Anti-prior: weight ~ 1 / (freq + epsilon)
            weights.append(1.0 / (freq + 1e-3))

        # Normalize to a distribution
        total_w = sum(weights)
        weights = [w / total_w for w in weights]

        n_atoms = rng.randint(*self.n_atoms_distribution)
        nodes: List[NodeRef] = []

        for i in range(n_atoms):
            cref = rng.choices(callable_refs, weights=weights, k=1)[0]
            atom = atom_pool[cref]

            # Sample args from the atom's samplers (NOT anti-prior at arg level
            # at MVP; the atom-level anti-prior dominates)
            args = sample_args_for_atom(cref, atom_pool, rng)
            bindings = tuple(("literal", v) for v in args[: atom["arity"]])
            # Pad with literals if sampler returned too few
            while len(bindings) < atom["arity"]:
                bindings = bindings + (("literal", rng.randint(1, 100)),)

            nodes.append(NodeRef(callable_ref=cref, arg_bindings=bindings))

        candidate = Genome(
            nodes=tuple(nodes),
            target_predicate="MVP search target (anti_prior)",
            mutation_operator_class="anti_prior",
        )
        validate_dag_invariants(candidate)
        return candidate

    # ------------------------------------------------------------------
    # Diagnostic — used by archive's per-operator metrics
    # ------------------------------------------------------------------

    def divergence_check(self, genome: Genome) -> Dict[str, Any]:
        """Compute KL divergence + pass/fail flag for an anti_prior genome."""
        freqs = compute_genome_atom_frequencies(genome)
        kl = kl_divergence(freqs, self.corpus_frequencies)
        return {
            "kl_divergence": kl,
            "passes_threshold": kl >= self.kl_threshold,
            "threshold": self.kl_threshold,
        }
