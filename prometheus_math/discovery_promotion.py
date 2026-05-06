"""prometheus_math.discovery_promotion — domain-agnostic DISCOVERY_CANDIDATE → CLAIM.

Pre-Tier-0 deliverable for joint sprint sync point S2 (see
``pivot/techne_ergon_joint_sprint_2026-05-05.md``). This module generalises
``DiscoveryPipeline.process_candidate``'s Phase 3 (CLAIM mint) to a
domain-agnostic promotion adapter that any agent producing
DISCOVERY_CANDIDATEs (Charon's cartography pipelines, Techne's
discovery_env, future agents) can call.

Why this exists
---------------
Charon's substrate cartography (2026-05-05) surfaced that DISCOVERY_CANDIDATE
flows currently route through ``DiscoveryPipeline.process_candidate`` — but
that path is Lehmer-specific in its hypothesis text and evidence shape.
Other domains (BSD, modular forms, knots, genus2, OEIS, mock theta) have
no canonical promotion path; their candidates either get logged as
diagnostic JSON or invoke ad-hoc kernel calls without the unified
discipline. The cartography handle #2 (per ``AVAILABLE_ARTIFACTS_2026-05-05.md``):

> Promote DISCOVERY_CANDIDATE to substrate CLAIM (~1 day) — routes
> Charon's findings into the kernel discipline; precondition for
> everything else.

This module is that promotion adapter. ``DiscoveryCandidate`` is the
generic shape; ``promote_to_claim()`` converts it into a kernel CLAIM
through the same CLAIM/FALSIFY/PROMOTE discipline ``DiscoveryPipeline``
uses for Lehmer.

What this DOES preserve from DiscoveryPipeline
----------------------------------------------
* The CLAIM is minted via ``kernel.CLAIM(...)`` with content-addressed
  evidence (candidate_id, features, survival_evidence dict).
* A synthetic CLEAR verdict is constructed (the caller asserts via
  ``survival_evidence`` that the candidate survived the caller's battery;
  the kernel-side PROMOTE accepts it).
* The verdict's ``input_hash`` is the candidate_id, so PROMOTE's
  provenance walker (which scrapes 64-char-hex strings from evidence)
  picks it up.
* The default terminal state is SHADOW_CATALOG — catalog-miss +
  battery-survived without independent verification puts the candidate
  in the addressable substrate without overclaiming PROMOTED.

What this DOES NOT do
---------------------
* Run any falsification battery itself. The caller asserts survival via
  the ``survival_evidence`` dict; the adapter trusts the assertion. (For
  Lehmer-specific re-verification, callers continue to use
  ``DiscoveryPipeline.process_candidate``.)
* Verify that ``survival_evidence`` is honest. The substrate's discipline
  is verifiability via TRACE — the adapter records what the caller
  claimed; downstream auditors can replay the caller's battery against
  the recorded features.
* Independently verify against external catalogs. That's a domain-specific
  step and stays in domain-specific pipelines.

Adjacent: ``LearnerCorpusEmitter`` (P5 stub) consumes promoted CLAIMs to
build its pre/post/provenance views. Promoting candidates through this
adapter is a precondition for them appearing in NearMissCorpus emissions.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from sigma_kernel.sigma_kernel import (
    Capability,
    Claim,
    SigmaKernel,
    Symbol,
    Tier,
    Verdict,
    VerdictResult,
)


# ---------------------------------------------------------------------------
# DiscoveryCandidate — generic, domain-agnostic shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DiscoveryCandidate:
    """A mathematical object that survived some agent's battery and merits
    substrate-grade CLAIM treatment.

    Generic across domains: Charon's curve cartography, Techne's
    discovery_env, Aporia's void-detection findings all emit this shape.
    The adapter ``promote_to_claim`` converts it into a kernel CLAIM.

    Attributes
    ----------
    domain : str
        Domain identifier — one of ``{"lehmer", "bsd_rank",
        "modular_form", "knot_trace_field", "genus2", "oeis_sleeping",
        "mock_theta", "obstruction_shape"}``, or any other registered
        domain. Used by downstream consumers (e.g.,
        ``learner_corpus.RAW_INVARIANTS_PER_DOMAIN``) to pick per-domain
        feature lists.
    candidate_id : str
        Content-addressed hash of (canonical_form, features). The
        content-addressing makes promotions idempotent — promoting the
        same candidate twice produces the same CLAIM evidence hash, so
        the kernel's UNIQUE constraint catches duplicates.
    candidate_label : str
        Human-readable label. Used as the CLAIM's ``target_name`` prefix.
        For Lehmer: ``"deg14_pm5_palindromic_X"``. For BSD: a Cremona
        label. For OEIS: an A-number.
    features : Mapping[str, Any]
        Domain-specific raw invariants computed BEFORE any falsifier
        touched the candidate. Mirrors P5
        ``ObjectFeatures.raw_invariants``. JSON-serialisable.
    survival_evidence : Mapping[str, Any]
        Caller-asserted record of which battery checks the candidate
        passed. Free-form but conventionally includes a list of check
        names + per-check status. Examples:
            * Lehmer: ``{"reciprocity": True, "irreducibility": True,
                       "catalog_miss": True, "F1": True, ...}``
            * BSD:    ``{"rank_prediction_correct": True,
                       "lmfdb_label_resolved": True}``
        The substrate trusts this assertion (see module docstring); the
        battery is replayable via the ``operator_class`` reference.
    operator_class : str
        Identifier of the agent / pipeline / operator that produced the
        candidate. Used by P5 ``ProvenanceView.operator_that_generated_candidate``.
    timestamp : float
        Unix epoch seconds when the candidate was produced.
    coordinate_chart_id : optional str
        Forward-reference to P0 CoordinateChart (Day 3-4). When populated,
        downstream consumers (Learner, ExclusionCertificate queries) can
        reason about the candidate's region. Until P0 lands, callers
        should pass ``"provisional:<domain>"``.
    notes : optional str
        Free-form caller notes. Persisted in the CLAIM evidence.
    """

    domain: str
    candidate_id: str
    candidate_label: str
    features: Mapping[str, Any] = field(default_factory=dict)
    survival_evidence: Mapping[str, Any] = field(default_factory=dict)
    operator_class: str = ""
    timestamp: float = field(default_factory=lambda: time.time())
    coordinate_chart_id: Optional[str] = None
    notes: Optional[str] = None

    @staticmethod
    def compute_candidate_id(
        canonical_form: Any,
        features: Mapping[str, Any],
    ) -> str:
        """Compute the content-addressed candidate_id.

        Use this to construct candidates with consistent IDs:
            cid = DiscoveryCandidate.compute_candidate_id(canonical, features)
            candidate = DiscoveryCandidate(candidate_id=cid, ...)
        """
        blob = json.dumps(
            {"canonical_form": canonical_form, "features": dict(features)},
            sort_keys=True,
            default=repr,
        )
        return hashlib.sha256(blob.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Terminal state — same as discovery_pipeline.TerminalState
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromotionResult:
    """The outcome of promoting a DiscoveryCandidate through the kernel
    CLAIM/FALSIFY/PROMOTE discipline.
    """

    candidate: DiscoveryCandidate
    claim_id: str  # the kernel claim's id
    symbol_ref: str  # "name@v1" of the promoted Symbol
    terminal_state: str  # "PROMOTED" | "SHADOW_CATALOG" | "REJECTED"
    verdict_status: str  # "CLEAR" | "WARN" | "BLOCK"
    rationale: str
    promoted_at: float


# ---------------------------------------------------------------------------
# The promotion adapter
# ---------------------------------------------------------------------------


def promote_discovery_candidate_to_claim(
    candidate: DiscoveryCandidate,
    *,
    kernel: SigmaKernel,
    terminal_state: str = "SHADOW_CATALOG",
    target_tier: Tier = Tier.Conjecture,
    kill_path_label: str = "discovery_candidate_promotion_v1",
    extra_caveats: Optional[Sequence[str]] = None,
    precision_metadata: Optional[Mapping[str, Any]] = None,
    cap: Optional[Capability] = None,
) -> PromotionResult:
    """Mint a kernel CLAIM from a DiscoveryCandidate; PROMOTE on CLEAR.

    Generalises ``DiscoveryPipeline.process_candidate``'s Phase 3
    (CLAIM mint via ``kernel.CLAIM``) to be domain-agnostic. The caller
    asserts via ``candidate.survival_evidence`` that the candidate
    survived their battery; this adapter trusts the assertion and routes
    the candidate through kernel discipline so it becomes addressable in
    the substrate.

    Parameters
    ----------
    candidate : DiscoveryCandidate
        The candidate to promote. Domain-agnostic; see DiscoveryCandidate
        docstring.
    kernel : SigmaKernel
        The kernel instance.
    terminal_state : str, default "SHADOW_CATALOG"
        One of ``"PROMOTED"``, ``"SHADOW_CATALOG"``, ``"REJECTED"``.
        Default SHADOW_CATALOG matches DiscoveryPipeline's discipline
        for catalog-miss-but-not-externally-verified candidates.
        Callers with independent verification should pass
        ``"PROMOTED"``; callers detecting a kill should pass
        ``"REJECTED"`` (and the verdict will be BLOCK).
    target_tier : Tier, default Tier.Conjecture
        Tier the symbol promotes to. Conjecture is the right default
        for unverified survivors.
    kill_path_label : str, default "discovery_candidate_promotion_v1"
        Used as the CLAIM's ``kill_path``. Versioned to allow future
        adapter revisions.
    extra_caveats : optional sequence of str
        Additional caveats to attach to the CLAIM (e.g., domain-specific
        warnings). Auto-caveats from precision_metadata (if any) are
        added in addition to these.
    precision_metadata : optional mapping
        Per substrate v2.3 precision metadata schema. If provided, gets
        attached to the CLAIM and propagates through TRACE.
    cap : optional Capability
        Pre-minted PromoteCap. If None, the adapter mints a fresh one
        (the standard pattern for adapter-internal capability handling
        mirroring ``DiscoveryPipeline.process_candidate``).

    Returns
    -------
    PromotionResult
        The promoted CLAIM's id + symbol_ref + verdict + terminal_state.

    Raises
    ------
    ValueError
        If ``terminal_state`` is not one of the three valid values.
    sigma_kernel.sigma_kernel.BlockedError
        If terminal_state="REJECTED" and the kernel's GATE rejects the
        BLOCK verdict (the caller's claim that the candidate is
        rejected propagates as a kernel-level BLOCK).
    """
    if terminal_state not in ("PROMOTED", "SHADOW_CATALOG", "REJECTED"):
        raise ValueError(
            f"terminal_state must be PROMOTED/SHADOW_CATALOG/REJECTED, "
            f"got {terminal_state!r}"
        )

    # Build a domain-agnostic hypothesis. Uses candidate_label so the
    # CLAIM's target_name is human-readable; uses features summary so
    # the hypothesis prose carries the candidate's identity.
    feature_summary = ", ".join(
        f"{k}={_short_repr(v)}" for k, v in list(candidate.features.items())[:5]
    )
    if len(candidate.features) > 5:
        feature_summary += f" (+{len(candidate.features) - 5} more)"

    hypothesis = (
        f"discovery candidate {candidate.candidate_label} in domain "
        f"{candidate.domain} survived caller battery; features: "
        f"{feature_summary or '<no features recorded>'}; "
        f"operator: {candidate.operator_class or '<unspecified>'}"
    )

    evidence: Dict[str, Any] = {
        "candidate_id": candidate.candidate_id,
        "domain": candidate.domain,
        "candidate_label": candidate.candidate_label,
        "features": dict(candidate.features),
        "survival_evidence": dict(candidate.survival_evidence),
        "operator_class": candidate.operator_class,
        "timestamp": float(candidate.timestamp),
    }
    if candidate.coordinate_chart_id is not None:
        evidence["coordinate_chart_id"] = candidate.coordinate_chart_id
    if candidate.notes is not None:
        evidence["notes"] = candidate.notes

    # Mint the CLAIM through the kernel.
    target_name = f"discovery_{candidate.domain}_{candidate.candidate_id[:12]}"
    claim = kernel.CLAIM(
        target_name=target_name,
        hypothesis=hypothesis,
        evidence=evidence,
        kill_path=kill_path_label,
        target_tier=target_tier,
    )

    # Attach caveats (legacy + precision_metadata-derived auto-caveats).
    caveats_list: List[str] = list(extra_caveats or ())
    if precision_metadata is not None:
        # Mirror the auto-caveat firing rules from
        # sigma_kernel/PRECISION_METADATA_SPEC.md
        conv = precision_metadata.get("convergence")
        if conv in {"failed_max_steps", "nan_returned"}:
            caveats_list.append("verification_failed")
        dps = precision_metadata.get("dps")
        expected_min = precision_metadata.get("expected_min_dps")
        if dps is not None and expected_min is not None and dps < expected_min:
            caveats_list.append("precision_below_expected")
    if caveats_list:
        claim.caveats = list(set(caveats_list))  # dedup
    if precision_metadata is not None:
        claim.precision_metadata = dict(precision_metadata)

    # Build the verdict. CLEAR for PROMOTED/SHADOW_CATALOG, BLOCK for REJECTED.
    if terminal_state == "REJECTED":
        verdict_status = Verdict.BLOCK
        rationale = (
            f"discovery_candidate_promotion_v1: caller flagged "
            f"{candidate.candidate_label} as REJECTED in domain "
            f"{candidate.domain}"
        )
    else:
        verdict_status = Verdict.CLEAR
        rationale = (
            f"discovery_candidate_promotion_v1: candidate "
            f"{candidate.candidate_label} survived caller battery in "
            f"domain {candidate.domain}; routing to {terminal_state}"
        )

    verdict = VerdictResult(
        status=verdict_status,
        rationale=rationale,
        input_hash=candidate.candidate_id,
        seed=0,
        runtime_ms=0,
    )

    # Persist verdict. This mirrors discovery_pipeline.process_candidate's
    # Phase 4 short-circuit — caller asserts survival via
    # survival_evidence, so we do not re-run a subprocess Ω.
    kernel.conn.execute(
        "UPDATE claims SET verdict_status=?, verdict_rationale=?, "
        "verdict_input_hash=?, verdict_seed=?, verdict_runtime_ms=? "
        "WHERE id=?",
        (
            verdict.status.value,
            verdict.rationale,
            verdict.input_hash,
            verdict.seed,
            verdict.runtime_ms,
            claim.id,
        ),
    )
    # Persist caveats and precision_metadata onto the claim row.
    if caveats_list or precision_metadata is not None:
        # The kernel's claims schema may or may not have these columns
        # depending on which migration the env is at; gracefully handle
        # both.
        try:
            kernel.conn.execute(
                "UPDATE claims SET caveats=? WHERE id=?",
                (json.dumps(claim.caveats), claim.id),
            )
        except Exception:
            pass
        try:
            kernel.conn.execute(
                "UPDATE claims SET precision_metadata=? WHERE id=?",
                (
                    json.dumps(claim.precision_metadata)
                    if claim.precision_metadata is not None
                    else None,
                    claim.id,
                ),
            )
        except Exception:
            pass
    kernel.conn.commit()
    claim.verdict = verdict
    claim.status = "falsified"

    # GATE - BLOCK raises BlockedError; CLEAR proceeds; WARN proceeds with warning.
    kernel.GATE(verdict)

    if terminal_state == "REJECTED":
        # No PROMOTE — the candidate is rejected. Return without symbol.
        return PromotionResult(
            candidate=candidate,
            claim_id=claim.id,
            symbol_ref="",
            terminal_state="REJECTED",
            verdict_status=verdict.status.value,
            rationale=verdict.rationale,
            promoted_at=time.time(),
        )

    # PROMOTE the claim. cap defaults to a freshly-minted PromoteCap.
    if cap is None:
        cap = kernel.mint_capability("PromoteCap")
    sym = kernel.PROMOTE(claim, cap)

    return PromotionResult(
        candidate=candidate,
        claim_id=claim.id,
        symbol_ref=sym.ref,
        terminal_state=terminal_state,
        verdict_status=verdict.status.value,
        rationale=verdict.rationale,
        promoted_at=time.time(),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _short_repr(v: Any, maxlen: int = 30) -> str:
    """Compact repr for hypothesis text. Truncates long strings/lists."""
    s = repr(v)
    if len(s) > maxlen:
        return s[: maxlen - 3] + "..."
    return s


# ---------------------------------------------------------------------------
# Convenience: Lehmer adapter (round-trip with discovery_pipeline)
# ---------------------------------------------------------------------------


def lehmer_candidate_from_pipeline_record(
    coeffs: Sequence[int],
    mahler_measure: float,
    *,
    survival_evidence: Mapping[str, Any],
    operator_class: str = "",
) -> DiscoveryCandidate:
    """Convenience constructor for Lehmer-domain DiscoveryCandidates.

    Useful when migrating callers from
    ``DiscoveryPipeline.process_candidate`` to the generic
    ``promote_discovery_candidate_to_claim`` while preserving the same
    candidate identity.
    """
    canonical = list(coeffs)
    features = {
        "poly_coefficients": canonical,
        "mahler_measure": float(mahler_measure),
    }
    cid = DiscoveryCandidate.compute_candidate_id(canonical, features)
    label = f"lehmer_M{mahler_measure:.6f}_h{cid[:8]}"
    return DiscoveryCandidate(
        domain="lehmer",
        candidate_id=cid,
        candidate_label=label,
        features=features,
        survival_evidence=dict(survival_evidence),
        operator_class=operator_class,
        coordinate_chart_id="provisional:lehmer",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


__all__ = [
    "DiscoveryCandidate",
    "PromotionResult",
    "promote_discovery_candidate_to_claim",
    "lehmer_candidate_from_pipeline_record",
]
