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
from typing import Any, Dict, Optional
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
