"""Learner-grade enrichment of substrate DiscoveryRecord output.

Per Ergon discussion `ergon/learner/v1_0_plans/substrate_quality_for_learner_discussion.md`
+ Techne reply 2026-05-11. Addresses 4 of the 5 easy-fix quality dims
at the generator level (no contract change to substrate).

This module takes a DiscoveryRecord (substrate-grade output) and produces
a LearnerRecord (Learner-grade enrichment) carrying the additional
fields the v1.0 LoRA pilot needs:

  - Dim 1 + 6 (episode density + boundaries): episode_id + episode_phase
    so the Learner can group records by lifecycle.
  - Dim 4 (verification stratification): verification_tier + chart_id
    propagated from CoordinateChart.canonicalization.decidability_status.
  - Dim 9 (anti-leakage tuple-vs-string): kill_signature derived as a
    structured tuple from the substrate's kill_pattern string, dropping
    the literal polynomial-coefficient leakage.

Dim 7 (null/decoy interleaving) is handled in the sibling
`survivor_seed_pool.py` (it requires changing the candidate stream, not
the per-record enrichment).

The substrate stays untouched — this is purely a downstream-consumer
adapter pattern, exactly the kind of HARD-2 anti-gravitational-well
discipline the Ergon discussion §2 calls for (no new opcodes; no kernel
v3; existing infrastructure consumed honestly).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple


# ---------------------------------------------------------------------------
# LearnerRecord — Learner-grade output (NOT a substrate primitive)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LearnerRecord:
    """Learner-grade enrichment of one substrate DiscoveryRecord.

    Substrate-grade DiscoveryRecord stays in place; this dataclass adds
    the per-record fields the Ergon v1.0 LoRA pilot needs without
    requiring a substrate contract change. Train/eval splits should
    use ``episode_id`` for grouping (anti-leakage).

    Attributes
    ----------
    underlying_record_hash : str
        SHA256 of the substrate's DiscoveryRecord candidate (the
        substrate-side canonical identity).
    episode_id : str
        Equals ``underlying_record_hash`` in Tier-1 (1:1 episode ↔
        candidate). Future tiers may group multiple records into one
        episode.
    episode_phase : str
        One of EPISODE_PHASES. Tier-1 generators emit ``"evaluate"`` for
        all records (single phase per candidate); future tiers will emit
        full claim → falsify → promote chains.
    verification_tier : str
        Decidability tier inherited from CoordinateChart. One of
        VERIFICATION_TIERS or ``"unknown"`` when no chart registered for
        the candidate's region.
    chart_id : str | None
        ``"<domain>:<region_key>"`` if a registered chart applies, else
        None.
    decoy_kind : str | None
        None for naturally-enumerated candidates; ``"seeded_survivor"``
        for injected known-positive examples (Dim 7 decoy interleaving).
    kill_signature : Tuple[str, ...]
        Structured tuple representation of the substrate's kill_pattern
        string. Designed to NOT leak literal polynomial coefficients
        across train/eval splits. See ``derive_kill_signature``.
    outcome_class : str
        One of OUTCOME_CLASSES. Normalized terminal_state for Learner
        consumption.
    """
    underlying_record_hash: str
    episode_id: str
    episode_phase: str
    verification_tier: str
    chart_id: Optional[str]
    decoy_kind: Optional[str]
    kill_signature: Tuple[str, ...]
    outcome_class: str
    # Claim-stack extension (Aporia adjudication 2026-05-12 Mod 2). Splits
    # "verifier said inconclusive" (real Learner signal) from "verifier
    # failed to run" (missing data). Optional + default None so existing
    # Tier-1 enriched-generator call sites that don't run a verifier
    # (Tier-0 generator's brute-force enumeration) don't break.
    # Values: VERIFIER_OUTCOME_CLASSES.
    verifier_outcome_class: Optional[str] = None
    # Claim-stack extension (Day-1 prompt 2026-05-13). Three carry-through
    # fields from the originating CLAIM block, so a Learner consumer can
    # group records by claim_id / stratify by claim_category / compare
    # actual_verdict against expected_verdict without joining back to the
    # source batch. None for non-claim records (Tier-0 enumeration).
    claim_id: Optional[str] = None
    claim_category: Optional[str] = None
    actual_verdict: Optional[str] = None


EPISODE_PHASES: Tuple[str, ...] = (
    "evaluate",   # single-phase per-candidate emit (Tier-1)
    "claim",      # CLAIM opcode emitted (Tier-2+)
    "falsify",    # FALSIFY opcode emitted (Tier-2+)
    "promote",    # PROMOTE opcode emitted (Tier-2+)
    "errata",     # ERRATA opcode emitted (Tier-2+)
)


VERIFICATION_TIERS: Tuple[str, ...] = (
    "decidable", "undecidable", "conditional", "unknown",
)


OUTCOME_CLASSES: Tuple[str, ...] = (
    "rejected",   # any kill_pattern non-empty + terminal_state REJECTED
    "survived",   # full F-gate battery passed; no terminal kill
    "promoted",   # PROMOTE'd to a substrate-grade Symbol
    "errored",    # error during processing (separate from rejection)
)


DECOY_KINDS: Tuple[str, ...] = (
    "seeded_survivor",   # known-survivor injected from survivor_seed_pool
    "known_kill",        # known-kill injected as negative anchor
)


VERIFIER_OUTCOME_CLASSES: Tuple[str, ...] = (
    # Decisive — real Learner signal. Train/eval can use these directly.
    "decisive_verified",          # verifier ran cleanly, returned a confirming verdict
    "decisive_contradicted",      # verifier ran cleanly, returned a refuting verdict
    "decisive_inconclusive",      # verifier ran cleanly, genuine inconclusive (verifier disagreement, open problem)
    # Failure — missing data, NOT signal. Train/eval should mask these.
    "verifier_transient_failure", # network / timeout / 503 — retry once; if still failing, mark this and move on
    "verifier_permanent_failure", # 404 / schema-validation / verifier-not-implemented — decisive failure to verify
)
"""Per Aporia adjudication 2026-05-12 Mod 2. The kernel's three-verdict
vocabulary (verified / contradicted / inconclusive) conflates two
different things at the substrate level: 'verifier ran and concluded'
vs 'verifier failed to run'. The Learner needs to distinguish them.
This enum lives at the LearnerRecord layer (NOT at the kernel verdict
level) so no contract change is required."""


# ---------------------------------------------------------------------------
# Anti-leakage kill_signature derivation (Dim 9)
# ---------------------------------------------------------------------------


def derive_kill_signature(kill_pattern: Optional[str]) -> Tuple[str, ...]:
    """Convert the substrate's kill_pattern string into a structured
    tuple that does NOT leak literal polynomial coefficients.

    Examples
    --------
    >>> derive_kill_signature(None)
    ('survived',)
    >>> derive_kill_signature("out_of_band:M=1.4521_outside_(1.001,1.18)")
    ('out_of_band',)
    >>> derive_kill_signature("reducible:reducible: (x**2 + 1)^1; (x**10 - ...")
    ('reducible', 'n_factors=2')
    >>> derive_kill_signature("F1:permutation_null_failed")
    ('f1_killed',)
    >>> derive_kill_signature("catalog_hit:Mossinghoff")
    ('catalog_hit', 'Mossinghoff')

    Substrate-grade kill_pattern strings carry literal polynomial
    factorization output (e.g. ``"(x**2 + 1)^1"``); train/eval leakage
    risk is real if a Learner sees the same factorization in both
    splits. The signature tuple captures the SHAPE of the kill (what
    kind, structural facts) without the data (specific coefficients).
    """
    if kill_pattern is None or kill_pattern == "":
        return ("survived",)
    pattern = kill_pattern.strip()
    # Prefix-based dispatch: substrate's kill_pattern strings have a
    # canonical "kind:" prefix per discovery_pipeline conventions.
    if pattern.startswith("out_of_band"):
        return ("out_of_band",)
    if pattern.startswith("reducible"):
        # Count factor occurrences as a structural fact (n_factors).
        # Substrate's reducible string format is
        # "reducible:reducible: (factor_1)^k1; (factor_2)^k2; ..."
        # so we can count by ";" separator after the second "reducible:"
        body = pattern.split("reducible:", 2)[-1] if "reducible:" in pattern else pattern
        n_factors = body.count(";") + 1 if body.strip() else 1
        return ("reducible", f"n_factors={n_factors}")
    if pattern.lower().startswith(("f1", "f6", "f9", "f11")):
        # F-gate kills — extract gate name only, drop rationale text
        prefix = pattern.split(":", 1)[0].lower()
        return (f"{prefix}_killed",)
    if pattern.startswith("catalog_hit"):
        # catalog_hit:<source-name> — keep source as label (it's a
        # categorical, not literal coefficient leakage)
        parts = pattern.split(":", 1)
        if len(parts) == 2 and parts[1]:
            return ("catalog_hit", parts[1].split(":")[0].split("_")[0])
        return ("catalog_hit",)
    if pattern.startswith("error"):
        return ("error",)
    # Unknown prefix — emit just the first colon-prefix as the
    # structural label (still doesn't leak literal data)
    label = pattern.split(":", 1)[0]
    return ("other", label)


# ---------------------------------------------------------------------------
# Verification-tier lookup (Dim 4)
# ---------------------------------------------------------------------------


def lookup_verification_tier(
    chart_id: Optional[str],
    chart_registry: Optional[Any] = None,
) -> Tuple[str, Optional[str]]:
    """Return ``(verification_tier, chart_id_used)`` for a candidate.

    Looks up the chart in the substrate's ChartRegistry; reads the
    ``CoordinateChart.canonicalization.decidability_status`` shipped
    fire #64 (test_coordinate_chart_returns.py covers this). Returns
    ``("unknown", None)`` when no chart registered.
    """
    if chart_id is None:
        return ("unknown", None)
    if chart_registry is None:
        # Lazy import — keep enrichment standalone-importable
        try:
            from sigma_kernel.coordinate_chart import (
                ChartRegistry, _split_chart_id,
            )
        except ImportError:
            return ("unknown", None)
        chart_registry = ChartRegistry()
    try:
        from sigma_kernel.coordinate_chart import _split_chart_id
        domain, region_key = _split_chart_id(chart_id)
    except (ValueError, ImportError):
        return ("unknown", None)
    chart = None
    if hasattr(chart_registry, "get"):
        try:
            chart = chart_registry.get(domain, region_key)
        except Exception:  # noqa: BLE001
            chart = None
    if chart is None:
        return ("unknown", None)
    canon = getattr(chart, "canonicalization", None)
    if canon is None:
        return ("unknown", chart_id)
    tier = getattr(canon, "decidability_status", None) or "unknown"
    if tier not in VERIFICATION_TIERS:
        tier = "unknown"
    return (tier, chart_id)


# ---------------------------------------------------------------------------
# Outcome-class normalization (Dim 1 + 6 helpers)
# ---------------------------------------------------------------------------


_TERMINAL_STATE_TO_OUTCOME = {
    "REJECTED": "rejected",
    "SURVIVED": "survived",
    "PROMOTED": "promoted",
    "ERROR": "errored",
}


def normalize_outcome_class(terminal_state: Optional[str]) -> str:
    if terminal_state is None:
        return "errored"
    return _TERMINAL_STATE_TO_OUTCOME.get(
        terminal_state.upper(), terminal_state.lower(),
    )


# ---------------------------------------------------------------------------
# Top-level enrichment function
# ---------------------------------------------------------------------------


def enrich(
    discovery_record: Any,
    *,
    chart_id: Optional[str] = None,
    chart_registry: Optional[Any] = None,
    decoy_kind: Optional[str] = None,
    episode_phase: str = "evaluate",
    verifier_outcome_class: Optional[str] = None,
    claim_id: Optional[str] = None,
    claim_category: Optional[str] = None,
    actual_verdict: Optional[str] = None,
) -> LearnerRecord:
    """Convert a DiscoveryRecord (or claim-runner result) to a LearnerRecord.

    Parameters
    ----------
    discovery_record : DiscoveryRecord
        Substrate-grade record with .candidate_hash, .terminal_state,
        .kill_pattern fields (per prometheus_math.discovery_pipeline).
        For claim-stack consumers, a duck-typed object with the same
        attribute names also works (the claim runner constructs a
        DiscoveryRecord-shaped lite struct from the verifier result).
    chart_id : str | None
        ``"<domain>:<region_key>"`` if a registered chart applies. The
        Tier-1 Lehmer generator passes ``"lehmer:deg12_palindromic"``
        when the chart is registered; future regions will set their own.
    chart_registry : ChartRegistry | None
        Substrate's registered chart set. None defers to a fresh
        registry (which will mostly miss; suitable for Tier-1 baseline).
    decoy_kind : str | None
        None for enumerated candidates; ``"seeded_survivor"`` for
        injected positives from the survivor_seed_pool.
    episode_phase : str
        Tier-1 always uses ``"evaluate"``; the claim runner uses
        ``"claim"`` / ``"falsify"`` / ``"promote"`` per emitted opcode.
    verifier_outcome_class : str | None
        Per Aporia adjudication 2026-05-12 Mod 2 (claim-stack pipeline).
        Splits "verifier said inconclusive" (real signal) from "verifier
        failed to run" (missing data). One of VERIFIER_OUTCOME_CLASSES
        or None for non-verifier-driven records (Tier-0 brute-force
        enumeration). The claim runner classifies its own verifier
        outcome and passes the result here.
    """
    if episode_phase not in EPISODE_PHASES:
        raise ValueError(
            f"episode_phase must be one of {EPISODE_PHASES}; got {episode_phase!r}"
        )
    if decoy_kind is not None and decoy_kind not in DECOY_KINDS:
        raise ValueError(
            f"decoy_kind must be one of {DECOY_KINDS} or None; got {decoy_kind!r}"
        )
    if (verifier_outcome_class is not None
            and verifier_outcome_class not in VERIFIER_OUTCOME_CLASSES):
        raise ValueError(
            f"verifier_outcome_class must be one of "
            f"{VERIFIER_OUTCOME_CLASSES} or None; got {verifier_outcome_class!r}"
        )
    underlying_hash = getattr(discovery_record, "candidate_hash", "")
    terminal_state = getattr(discovery_record, "terminal_state", None)
    kill_pattern = getattr(discovery_record, "kill_pattern", None)
    verification_tier, chart_id_used = lookup_verification_tier(
        chart_id, chart_registry=chart_registry,
    )
    return LearnerRecord(
        underlying_record_hash=underlying_hash,
        episode_id=underlying_hash,  # 1:1 in Tier-1
        episode_phase=episode_phase,
        verification_tier=verification_tier,
        chart_id=chart_id_used,
        decoy_kind=decoy_kind,
        kill_signature=derive_kill_signature(kill_pattern),
        outcome_class=normalize_outcome_class(terminal_state),
        verifier_outcome_class=verifier_outcome_class,
        claim_id=claim_id,
        claim_category=claim_category,
        actual_verdict=actual_verdict,
    )


__all__ = [
    "LearnerRecord",
    "EPISODE_PHASES",
    "VERIFICATION_TIERS",
    "OUTCOME_CLASSES",
    "VERIFIER_OUTCOME_CLASSES",
    "DECOY_KINDS",
    "derive_kill_signature",
    "lookup_verification_tier",
    "normalize_outcome_class",
    "enrich",
]
