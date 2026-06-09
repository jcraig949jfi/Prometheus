"""TheseusRecord — generalized substrate-grade record format.

Compatible with discovery_pipeline.DiscoveryRecord (Lehmer-specific) but
designed for the full menu of claim types: catalog-cross-product,
conservation-law, mutation, kill-neighborhood, literature-mined, etc.

Substrate-grade properties:
- Content-addressed via record_id = sha256(canonical_claim_form)
- Precision/method/convergence metadata first-class
- Generator provenance preserved (generator_id, batch_id, parent_record_id)
- Append-only schema: new fields added; never removed without migration
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum


class ClaimKind(str, Enum):
    """Top-level taxonomy of claim shapes Theseus emits."""

    INVARIANT_EQUALITY = "invariant_equality"
    STATISTICAL_CORRELATION = "statistical_correlation"
    FUNCTIONAL_IDENTITY = "functional_identity"
    RATIO_INVARIANCE = "ratio_invariance"
    DISTRIBUTION_MATCH = "distribution_match"
    CONSERVATION_LAW = "conservation_law"
    OPERATOR_ROTATION = "operator_rotation"
    COMPOSITION_TEST = "composition_test"
    MUTATION = "mutation"
    KILL_NEIGHBORHOOD = "kill_neighborhood"
    LITERATURE_MINED = "literature_mined"
    SYMMETRY_TRANSFORM = "symmetry_transform"
    BRIDGE_EXTENSION = "bridge_extension"
    # Fire #142 (2026-05-27) — 5 new claim shapes to break the
    # 26-template monoculture ceiling. See
    # pivot/techne_5gen_plan_2026-05-27.md.
    TYPED_BRIDGE = "typed_bridge"
    OBSTRUCTION = "obstruction"
    MINIMAL_COUNTEREXAMPLE = "minimal_counterexample"
    VERIFIER_DISAGREEMENT = "verifier_disagreement"
    CONJECTURE_NEIGHBORHOOD = "conjecture_neighborhood"
    # 2026-05-28 — 15 more shapes from ChatGPT remainder + Sphinx
    # reasoning ontology. See pivot/techne_15gen_plan_2026-05-28.md.
    FORMALIZATION_SKELETON = "formalization_skeleton"   # l2
    CORPUS_COMPRESSION = "corpus_compression"           # m2
    MODUS_PONENS_CHAIN = "modus_ponens_chain"           # p1
    MODULAR_VARYING_P = "modular_varying_p"             # q1
    SUBSET_RELATION = "subset_relation"                 # r1
    TRIANGLE_INEQUALITY = "triangle_inequality"         # s1
    MULTI_HOP_DEDUCTION = "multi_hop_deduction"         # t1
    QUANTIFIER_SWAP = "quantifier_swap"                 # u1
    COUNTERFACTUAL_INVARIANCE = "counterfactual_invariance"  # v1
    CLOSURE_UNDER_OPERATION = "closure_under_operation"  # w1
    PARTIAL_INFORMATION = "partial_information"         # x1
    ANALOGICAL_TRANSFER = "analogical_transfer"         # y1
    ORDER_DEPENDENCE = "order_dependence"               # z1
    CONFIDENCE_CALIBRATION = "confidence_calibration"   # aa1
    FALSE_DICHOTOMY = "false_dichotomy"                 # bb1
    OTHER = "other"


class Verdict(str, Enum):
    """Theseus verdict — superset of discovery_pipeline TerminalState
    plus INCONCLUSIVE (needs triangulation) and UNVERIFIED (emitted but
    not yet routed through sigma)."""

    PROMOTED = "PROMOTED"
    SHADOW_CATALOG = "SHADOW_CATALOG"
    REJECTED = "REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class StepRecord:
    """One step in a multi-step verification path (process supervision).

    Used by triangulation generators (D3) and future MCTS / tree-search
    generators. Each step has its own info-density score; the aggregated
    record's score blends them.

    Pulls from frontier "process supervision" (Lightman et al. OpenAI
    2023 "Let's Verify Step by Step"): step-level reward outperforms
    outcome-only reward for math reasoning. The substrate's analogue:
    info-density-per-step gives finer training signal than terminal-
    verdict-only.
    """

    step_id: str  # e.g. "step_0", "step_1"
    step_kind: str  # "resample", "precision_increase", "method_switch", etc
    step_method: str
    step_input: Dict[str, Any] = field(default_factory=dict)
    step_output: Dict[str, Any] = field(default_factory=dict)
    step_info_density: float = 0.5  # 0..1
    step_precision_dps: Optional[int] = None
    step_convergence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TheseusRecord:
    """A single substrate record emitted by a Theseus generator.

    Fields are append-only. New fields added at end with Optional default;
    existing fields never removed without a migration."""

    # --- Identity & provenance ---
    record_id: str
    generator_id: str
    batch_id: str
    emitted_at: str  # ISO-8601 UTC

    # --- Claim ---
    claim_kind: str  # one of ClaimKind values
    claim_payload: Dict[str, Any]  # generator-specific structured form
    canonical_claim_text: str  # human-readable rendering

    # --- Verification outcome ---
    verdict: str  # one of Verdict values
    kill_pattern: Optional[str] = None
    kill_vector: Optional[Dict[str, Any]] = None  # serialized KillVector

    # --- Precision metadata (per sigma_kernel PRECISION_METADATA_SPEC) ---
    precision_dps: Optional[int] = None
    method: Optional[str] = None
    convergence_status: Optional[str] = None

    # --- Sigma kernel cross-refs ---
    sigma_claim_id: Optional[str] = None
    sigma_symbol_ref: Optional[str] = None

    # --- Generator-graph provenance ---
    parent_record_id: Optional[str] = None  # for mutations / kill-neighborhood

    # --- Yield score axes (logged at emit time; recomputed by scoring) ---
    info_density: Optional[float] = None
    diversity_score: Optional[float] = None
    novelty_estimate: Optional[float] = None
    # Per-record training-value weight (Fire #15). Computed via
    # theseus.scoring.training_weight.training_weight(). May be populated
    # at emit-time (live) or via annotate_corpus (batch). Optional so
    # older records don't need backfill.
    training_weight: Optional[float] = None

    # --- Process supervision (Fire #7) ---
    # Optional list of step-record dicts (StepRecord.to_dict() shape).
    # Triangulation / MCTS generators populate this; old records leave
    # None. info_density_score uses step_info_density mean when present
    # (additive enhancement over terminal-verdict scoring).
    step_trace: Optional[List[Dict[str, Any]]] = None

    # --- Predicate kind (calibration v3c, 2026-06-03) ---
    # Which PREDICATE this record's verdict answers — load-bearing for
    # content-aware F2 promotion, whose raw-value null is only valid for
    # the DIRECT predicate "does relation(value_a, value_b) hold".
    #   "direct"      — verdict = does rel(a, b) hold on the stored values
    #   "invariance"  — verdict = is rel invariant under a transform
    #                   (g4 sign-reflection, g5 scale) — answers a DIFFERENT
    #                   predicate, so the raw-value null is the wrong basis
    #   "transformed" — verdict = does rel(f(a), g(b)) hold (a3)
    # None = un-stamped legacy record; consumers fall back to a generator_id
    # denylist. New records stamp this from the generator's class attribute,
    # so the filter no longer depends on the denylist for stamped records.
    # Does NOT enter record_id (id = hash(text|generator_id)), so adding it
    # is content-address-stable: no churn on existing corpora.
    predicate_kind: Optional[str] = None

    # --- Free-form extras ---
    extras: Dict[str, Any] = field(default_factory=dict)

    def to_jsonl(self) -> str:
        """Serialize to a single JSONL line."""
        return json.dumps(asdict(self), sort_keys=True, default=str)

    @staticmethod
    def compute_record_id(canonical_claim_text: str, generator_id: str) -> str:
        """Content-addressed record id.

        Includes generator_id so the same claim text emitted by different
        generators (e.g. A1 vs C1 mutation that converges to A1's form)
        produces distinct records. De-duplication of cross-generator
        equivalence is a Tier-1 concern handled at the corpus writer.
        """
        h = hashlib.sha256()
        h.update(generator_id.encode("utf-8"))
        h.update(b"|")
        h.update(canonical_claim_text.encode("utf-8"))
        return h.hexdigest()
