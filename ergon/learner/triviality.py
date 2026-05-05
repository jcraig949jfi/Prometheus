"""ergon.learner.triviality — F_TRIVIAL_BAND_REJECT signature library.

Per pivot/ergon_learner_proposal_v8.md S6.2 + round-6 review:

The trivial-pattern detector runs as a kill-test extension BEFORE the
F1+F6+F9+F11 unanimous battery. It rejects claims whose only structural
signal is a known trivial pattern — small-number coincidences, scale
artifacts, prime-density artifacts, computational noise masquerading as
structure.

V6 specified 4 static signatures. Round-6 review extended to include
2 temporal signatures (recurrence density, novelty decay per lineage).
v8 codified all 6.

Static signatures (frame: pattern matching on a single claim):
  T1 small_number_coincidence
  T2 prime_density_artifact
  T3 scale_rescaling
  T4 cyclotomic_root_of_unity_coincidence

Temporal signatures (frame: pattern matching across recent lineage):
  T5 recurrence_density (Jaccard >=0.9 to >=3 prior in same lineage / 1K window)
  T6 novelty_decay (avg distance decreasing >=30% over 1K-episode window)

Per round-6: signature library is extensible via Techne meta-loop.
New gravitational wells discovered during MVP are added as substrate-
grade T7+ signatures.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple


SignatureMatch = Literal[
    # No trivial pattern detected
    "no_match",
    # Static signatures
    "small_number_coincidence",
    "prime_density_artifact",
    "scale_rescaling",
    "cyclotomic_root_of_unity_coincidence",
    # Temporal signatures (require lineage history)
    "recurrence_density",
    "novelty_decay",
]


@dataclass(frozen=True)
class ClaimDescriptor:
    """The minimal claim metadata the trivial-pattern detector needs.

    A claim's full content is in the substrate; this descriptor carries
    only what the detector inspects. content_hash is the genome's
    content_hash (for recurrence-density check); lineage_id traces the
    operator-class lineage chain; structural_features carries depth /
    width / arithmetic-complexity for trivial pattern matching.
    """
    claim_id: str
    content_hash: str
    lineage_id: str  # operator-class lineage chain (e.g., "structural:abc123:def456")
    output_magnitude: Optional[float]
    output_type_signature: Optional[str]
    structural_features: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrivialMatch:
    """The result of running the trivial-pattern detector on a claim."""
    matched: bool
    signature: SignatureMatch
    rationale: str
    matched_claim_ids: Tuple[str, ...] = ()  # for temporal signatures


# ---------------------------------------------------------------------------
# Static signatures (v6 §6.2)
# ---------------------------------------------------------------------------


def detect_small_number_coincidence(
    claim: ClaimDescriptor,
    *,
    magnitude_threshold: float = 100.0,
    arithmetic_complexity_threshold: int = 3,
) -> Optional[TrivialMatch]:
    """T1: output magnitude <= 100 with low arithmetic complexity.

    Claims whose only signal is a small-integer coincidence (e.g., output
    is 6, 12, 24 — common natural numbers that pop up in many contexts
    via base rate alone) are not real signal. Filtered before they enter
    the kill battery.

    arithmetic_complexity is a feature carried in structural_features:
    typically the number of distinct prime factors, bit length, or
    similar coarse complexity measure. Low complexity (<3) at small
    magnitude triggers this signature.
    """
    mag = claim.output_magnitude
    if mag is None or mag > magnitude_threshold:
        return None

    arith_complexity = claim.structural_features.get("arithmetic_complexity")
    if arith_complexity is None:
        # Fall back to bit length of the magnitude
        try:
            arith_complexity = int(mag).bit_length()
        except (TypeError, ValueError, OverflowError):
            return None

    if arith_complexity < arithmetic_complexity_threshold:
        return TrivialMatch(
            matched=True,
            signature="small_number_coincidence",
            rationale=(
                f"output magnitude {mag} <= {magnitude_threshold} with arithmetic "
                f"complexity {arith_complexity} < {arithmetic_complexity_threshold}; "
                "common-natural-number coincidence"
            ),
        )
    return None


def detect_prime_density_artifact(
    claim: ClaimDescriptor,
    *,
    proportionality_drift_threshold: float = 0.10,
) -> Optional[TrivialMatch]:
    """T2: output is proportional to pi(x) / Li(x) / x/ln(x) for small x with
    unstable proportionality constant.

    Claims that look like 'output ~ k * pi(x)' with k drifting between
    measurements aren't structural; they're prime-density artifacts at
    small x where pi(x) hasn't yet stabilized to its asymptotic.

    structural_features['prime_density_proportionality'] = (k_estimate,
    k_drift) is the diagnostic.
    """
    pdp = claim.structural_features.get("prime_density_proportionality")
    if pdp is None:
        return None

    try:
        k_estimate, k_drift = pdp
    except (TypeError, ValueError):
        return None

    if k_drift > proportionality_drift_threshold:
        return TrivialMatch(
            matched=True,
            signature="prime_density_artifact",
            rationale=(
                f"output ~= {k_estimate:.3f} * pi(x) with drift {k_drift:.3f} "
                f"> threshold {proportionality_drift_threshold}; prime-density artifact"
            ),
        )
    return None


def detect_scale_rescaling(
    claim: ClaimDescriptor,
    *,
    rescaling_correlation_threshold: float = 0.95,
) -> Optional[TrivialMatch]:
    """T3: output is a linear or log-linear function of input magnitude
    with no structural component.

    Claims where 'the output has units' rather than 'the output captures
    a relationship' fall here. structural_features['input_output_corr']
    is the Pearson correlation between input magnitude and output
    magnitude across perturbations; very high correlation (>0.95) means
    the genome is essentially passing through a rescaling factor with
    no novel structure.
    """
    corr = claim.structural_features.get("input_output_corr")
    if corr is None:
        return None

    try:
        corr_val = float(corr)
    except (TypeError, ValueError):
        return None

    if abs(corr_val) > rescaling_correlation_threshold:
        return TrivialMatch(
            matched=True,
            signature="scale_rescaling",
            rationale=(
                f"input-output magnitude correlation {corr_val:.3f} > "
                f"{rescaling_correlation_threshold}; pure scale rescaling, no structure"
            ),
        )
    return None


def detect_cyclotomic_root_of_unity_coincidence(
    claim: ClaimDescriptor,
    *,
    mahler_distance_threshold: float = 1e-3,
) -> Optional[TrivialMatch]:
    """T4: For polynomial outputs, Mahler measure exactly 1 (cyclotomic) or
    within epsilon of 1 (cyclotomic-near-miss).

    structural_features['mahler_measure'] is the Mahler measure of the
    output polynomial. If it's < 1 + mahler_distance_threshold, the
    polynomial is in the cyclotomic neighborhood — trivially M = 1
    (cyclotomic) or computational artifact (cyclotomic-near-miss with
    likely reducibility).
    """
    if claim.output_type_signature != "polynomial":
        return None

    mahler = claim.structural_features.get("mahler_measure")
    if mahler is None:
        return None

    try:
        mahler_val = float(mahler)
    except (TypeError, ValueError):
        return None

    if mahler_val < 1.0 + mahler_distance_threshold:
        irreducible = claim.structural_features.get("is_irreducible", None)
        rationale_extra = (
            ""
            if irreducible is None
            else f"; irreducible={irreducible}"
        )
        return TrivialMatch(
            matched=True,
            signature="cyclotomic_root_of_unity_coincidence",
            rationale=(
                f"polynomial Mahler measure {mahler_val} < "
                f"1 + {mahler_distance_threshold}; cyclotomic neighborhood"
                f"{rationale_extra}"
            ),
        )
    return None


# ---------------------------------------------------------------------------
# Temporal signatures (round-6 extension)
# ---------------------------------------------------------------------------


def detect_recurrence_density(
    claim: ClaimDescriptor,
    *,
    recent_history: Sequence[ClaimDescriptor],
    jaccard_threshold: float = 0.9,
    minimum_recurrence_count: int = 3,
    same_lineage_only: bool = True,
) -> Optional[TrivialMatch]:
    """T5: claim is structurally similar (Jaccard >= threshold) to at least
    minimum_recurrence_count prior claims in the same operator-class lineage
    within the recent_history window.

    Jaccard similarity is computed over content_hash prefixes (a coarse
    proxy for canonical-form similarity at MVP; v0.5 will use full
    canonical-form distance via Techne's canonicalizer).
    """
    if len(recent_history) < minimum_recurrence_count:
        return None

    target_set = set(claim.content_hash[:16])  # 16-char prefix as similarity proxy

    matches: List[str] = []
    for prior in recent_history:
        if same_lineage_only and prior.lineage_id != claim.lineage_id:
            continue
        prior_set = set(prior.content_hash[:16])
        if not target_set or not prior_set:
            continue
        intersection = len(target_set & prior_set)
        union = len(target_set | prior_set)
        jaccard = intersection / union if union > 0 else 0.0
        if jaccard >= jaccard_threshold:
            matches.append(prior.claim_id)

    if len(matches) >= minimum_recurrence_count:
        return TrivialMatch(
            matched=True,
            signature="recurrence_density",
            rationale=(
                f"claim has Jaccard >= {jaccard_threshold} similarity to "
                f"{len(matches)} prior claims in same lineage; "
                f">= {minimum_recurrence_count} threshold met; "
                "trivial pattern repeatedly rediscovered"
            ),
            matched_claim_ids=tuple(matches),
        )
    return None


def detect_novelty_decay(
    *,
    lineage_history: Sequence[ClaimDescriptor],
    distance_decrease_threshold: float = 0.30,
    minimum_window_size: int = 10,
) -> Optional[TrivialMatch]:
    """T6: in a per-lineage 1K-episode window, average claim-to-claim canonical-
    form distance decreases by >= threshold (default 30%).

    A lineage that's converging (each new claim more similar to its
    predecessor than the last) is rediscovering trivial patterns rather
    than genuinely exploring.

    Operates on the lineage as a whole, not per-claim. Returns a match
    that applies to the entire window — when fired, the next claim in
    that lineage is a candidate for F_TRIVIAL_BAND_REJECT.
    """
    n = len(lineage_history)
    if n < minimum_window_size:
        return None

    # Compute consecutive distances using content_hash prefix Jaccard distance
    distances: List[float] = []
    for i in range(1, n):
        a = set(lineage_history[i - 1].content_hash[:16])
        b = set(lineage_history[i].content_hash[:16])
        if not a or not b:
            continue
        intersection = len(a & b)
        union = len(a | b)
        jaccard = intersection / union if union > 0 else 0.0
        # Distance = 1 - similarity
        distances.append(1.0 - jaccard)

    if len(distances) < minimum_window_size // 2:
        return None

    # Compare first half average to second half average
    half = len(distances) // 2
    first_avg = sum(distances[:half]) / half if half > 0 else 0.0
    second_avg = sum(distances[half:]) / (len(distances) - half) if (len(distances) - half) > 0 else 0.0

    if first_avg == 0:
        return None  # can't compute decrease ratio

    decrease_ratio = (first_avg - second_avg) / first_avg

    if decrease_ratio >= distance_decrease_threshold:
        return TrivialMatch(
            matched=True,
            signature="novelty_decay",
            rationale=(
                f"lineage's average claim distance decreased "
                f"{decrease_ratio*100:.1f}% from first half "
                f"({first_avg:.3f}) to second half ({second_avg:.3f}); "
                f">= {distance_decrease_threshold*100:.0f}% threshold; "
                "lineage converging on trivial pattern"
            ),
        )
    return None


# ---------------------------------------------------------------------------
# Top-level dispatcher — F_TRIVIAL_BAND_REJECT
# ---------------------------------------------------------------------------


def f_trivial_band_reject(
    claim: ClaimDescriptor,
    recent_history: Optional[Sequence[ClaimDescriptor]] = None,
) -> TrivialMatch:
    """Run the full trivial-pattern signature library against a claim.

    Returns the first match found (signatures checked in order T1, T2,
    T3, T4, T5, T6). If no signature matches, returns no_match.

    This is the kill-test extension that runs BEFORE F1+F6+F9+F11.
    Trivial-pattern matches are killed with kill_pattern =
    F_TRIVIAL_BAND_REJECT_<signature_name>.
    """
    # Static signatures (single-claim)
    for detector in (
        detect_small_number_coincidence,
        detect_prime_density_artifact,
        detect_scale_rescaling,
        detect_cyclotomic_root_of_unity_coincidence,
    ):
        result = detector(claim)
        if result is not None:
            return result

    # Temporal signatures (require history)
    if recent_history:
        recurrence = detect_recurrence_density(
            claim,
            recent_history=recent_history,
        )
        if recurrence is not None:
            return recurrence

        # novelty_decay operates on the lineage; we filter recent_history
        # to same-lineage entries plus the current claim.
        same_lineage = [c for c in recent_history if c.lineage_id == claim.lineage_id]
        if same_lineage:
            novelty = detect_novelty_decay(
                lineage_history=tuple(same_lineage) + (claim,),
            )
            if novelty is not None:
                return novelty

    return TrivialMatch(
        matched=False,
        signature="no_match",
        rationale="no trivial pattern detected",
    )


# ---------------------------------------------------------------------------
# Trigger-rate diagnostics (per v8 §4 Trial 2 acceptance criterion)
# ---------------------------------------------------------------------------


def compute_trigger_rate(
    matches: Sequence[TrivialMatch],
) -> Dict[str, Any]:
    """Compute F_TRIVIAL_BAND_REJECT trigger rate per signature.

    Per v8 §4 Trial 2 acceptance: F_TRIVIAL_BAND_REJECT trigger rate
    should be 5-30% of all kills (lower bound: detector is doing
    meaningful work; upper bound: detector isn't over-rejecting).
    """
    if not matches:
        return {
            "n_total": 0,
            "n_matched": 0,
            "trigger_rate": 0.0,
            "per_signature_counts": {},
        }

    n_total = len(matches)
    n_matched = sum(1 for m in matches if m.matched)
    trigger_rate = n_matched / n_total

    per_signature: Counter = Counter()
    for m in matches:
        if m.matched:
            per_signature[m.signature] += 1

    return {
        "n_total": n_total,
        "n_matched": n_matched,
        "trigger_rate": trigger_rate,
        "per_signature_counts": dict(per_signature),
    }
