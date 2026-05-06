"""prometheus_math.evidence_field — P1 EvidenceField (factual axes only).

Tier 1 primitive per substrate v2.3 §6.2 P1. Joint sprint commitment T9.

Why this exists
---------------
v2.3 splits the original "GradientField" (v1.0 framing) into two
type-separated objects per ChatGPT + Gemini convergent critique:

* **EvidenceField** (this module) — factual axes derived from substrate
  observations. Encodes WHAT IS TRUE about a Claim, with metric/ordinal/
  vector typing. Lives on every Claim that has been through the
  falsification battery.
* **PolicyField** (sister module ``policy_field.py``) — utility / info-gain
  / navigator-output predictions. Lives on the navigator's output, NOT
  on the substrate's evidence ledger. Owned by the navigator pillar.

The split is the load-bearing architectural lock-in from v2.3 §8: evidence
axes vs policy axes never live in the same object. Mixing them invites
downstream models to confuse epistemic confidence with action preference.

The six factual axes
--------------------
1. ``distance_to_target`` — margin from the target region (derived from
   KillComponent margin). Axis type: metric. Already-shipped data path.
2. ``battery_survival_depth`` — how many falsifiers the claim passed.
   Axis type: ordinal (NOT metric — counts of categorical falsifiers do
   not embed in a continuous metric space). Already-shipped data path.
3. ``verification_depth`` — decomposed (precision_dps, method_spec,
   convergence_status, stability_pass). Axis type: vector. NOT collapsed
   to scalar (the Day-5 lesson: dps=30 PASS and dps=100 PASS must never
   look identical).
4. ``exclusion_distance`` — distance to nearest registered ExclusionCertificate.
   Axis type: metric. Populated only when both (a) a CoordinateChart is
   registered for the Claim's region AND (b) an ExclusionCertificate
   with `strength ∈ {complete, bounded_complete}` exists nearby. NULL
   otherwise.
5. ``assumption_load`` — how much the Claim depends on catalog
   completeness, numerical precision, heuristic search bounds,
   normalization choices, theorem imports. Axis type: vector (5
   sub-dimensions). Per ChatGPT v2.3 addition.
6. ``computational_friction`` — wall-clock + oracle-call cost to produce
   the Claim. Axis type: metric. Per Gemini v2.3 addition. Populated by
   the Pre-Tier-0 0b telemetry instrumentation (already shipped).

Each axis carries ``axis_type ∈ {metric, ordinal, categorical, estimate, vector}``
per ChatGPT — no silent scalarization. ``axis_confidence`` is per-axis ∈ [0, 1].

Forward references (DEFERRED until upstream lands)
--------------------------------------------------
* ``CoordinateChart`` import — populated when P0 lands (Agent A in flight).
* ``MethodSpec`` import — populated when P3 lands (Agent B in flight).
* ``ExclusionCertificate`` import — populated when P4 lands (Day 8-12).
* ``StabilityResult`` from stability_adapters — populated when Agent C lands.

This module compiles and tests pass without those imports — defensive
late binding via Optional types and string-typed fields. When the
upstream primitives land, the integration points are clearly marked
``# FORWARD-REF P0/P3/P4/P2`` for ease of wiring.

Bridge_proximity is DEFERRED
----------------------------
Per substrate v2.3 §6.2 P1 + reviewer convergence (ChatGPT, Gemini,
Aporia all flagged): bridge_proximity is too vague without a registered
BridgeGraph primitive. Defer until v3.0. The 6 axes above are the
v2.3 commitment; bridge_proximity is documented in v2.3 §10 as
"explicitly NOT doing this sprint."
"""
from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union


# ---------------------------------------------------------------------------
# Axis typing — no silent scalarization (ChatGPT discipline)
# ---------------------------------------------------------------------------


class AxisType(str, enum.Enum):
    """Per ChatGPT: every EvidenceField axis carries axis_type so consumers
    know what mathematical structure the axis has. No mixing scales.
    """

    METRIC = "metric"        # continuous distance, e.g., distance_to_target in margin units
    ORDINAL = "ordinal"      # ordered categorical, e.g., battery_survival_depth (count)
    CATEGORICAL = "categorical"  # unordered categorical (e.g., method enum)
    ESTIMATE = "estimate"    # value with uncertainty (would be policy if from a model — see PolicyField)
    VECTOR = "vector"        # multi-dimensional (e.g., verification_depth's sub-fields)


# ---------------------------------------------------------------------------
# Per-axis dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DistanceToTarget:
    """Axis 1: margin from the target region.

    Derived from a KillComponent's `margin` + `margin_unit` for the
    "out_of_band" or "target_region" falsifier component. When triggered
    (the Claim is INSIDE the target band), the value is 0.0 by
    convention; when not triggered (the Claim is OUTSIDE), the value is
    the positive distance in the named margin_unit.
    """

    value: Optional[float]
    unit: Optional[str]  # one of MARGIN_UNITS from kill_vector.py
    metric_id: str = "margin_unit_native"
    computed_at_dps: Optional[int] = None
    axis_type: AxisType = AxisType.METRIC


@dataclass(frozen=True)
class BatterySurvivalDepth:
    """Axis 2: how many falsifiers the claim passed before any kill.

    Ordinal because falsifiers are categorical and counting them does
    not embed in a continuous metric — F1+F6 surviving is not "twice as
    survived" as F1 alone surviving. Reported as (n_passed, n_total)
    for downstream consumers that want survival fraction.
    """

    n_passed: int
    n_total: int
    falsifiers_passed: Tuple[str, ...] = ()
    falsifiers_failed: Tuple[str, ...] = ()
    axis_type: AxisType = AxisType.ORDINAL

    @property
    def survival_fraction(self) -> Optional[float]:
        if self.n_total == 0:
            return None
        return self.n_passed / self.n_total


@dataclass(frozen=True)
class VerificationDepth:
    """Axis 3: decomposed verification quality.

    Vector axis (NOT collapsed to scalar — this is the Day-5 lesson).
    Sub-fields:
      - min_precision_dps: lowest mpmath dps used across the falsifiers
      - methods_used: sorted tuple of MethodSpec.to_string() values
      - convergence_summary: aggregate convergence status
        ("all_converged" | "some_failed" | "all_failed" | "mixed" | "n/a")
      - stability_pass: aggregate StabilityResult-like dict
        (FORWARD-REF P2 — populated when stability_adapters lands)
    """

    min_precision_dps: Optional[int]
    methods_used: Tuple[str, ...]
    convergence_summary: str
    stability_aggregate: Optional[Mapping[str, Any]] = None  # FORWARD-REF P2
    axis_type: AxisType = AxisType.VECTOR


@dataclass(frozen=True)
class ExclusionDistance:
    """Axis 4: distance to nearest registered ExclusionCertificate.

    Populated ONLY when:
      1. A CoordinateChart is registered for the Claim's region (FORWARD-REF P0)
      2. An ExclusionCertificate with strength in {complete, bounded_complete}
         exists nearby (FORWARD-REF P4)
      3. The Claim's coordinates are admissible in the chart

    Otherwise NULL — anti-fake-topology discipline (no metric without
    chart per substrate v2.3 §8 architectural lock-in).
    """

    value: Optional[float]  # None if no chart+cert pair available
    chart_id: Optional[str] = None  # FORWARD-REF P0
    nearest_certificate_ref: Optional[str] = None  # FORWARD-REF P4
    metric_id: Optional[str] = None  # which chart metric was used
    reason_unpopulated: Optional[str] = None  # human-readable why NULL
    axis_type: AxisType = AxisType.METRIC


@dataclass(frozen=True)
class AssumptionLoad:
    """Axis 5 (ChatGPT v2.3 addition): how much the Claim depends on
    external assumptions.

    Sub-dimensions:
      - catalog_dependence: depends on catalog completeness (e.g., Mossinghoff)
      - numeric_dependence: depends on chosen precision_dps
      - heuristic_dependence: depends on heuristic search bounds
      - normalization_dependence: depends on canonicalizer choice
      - theorem_import_dependence: depends on imported theorems (RH, BSD, etc.)

    Each in [0, 1]; aggregate magnitude via L2 or max depending on
    consumer.
    """

    catalog_dependence: float = 0.0
    numeric_dependence: float = 0.0
    heuristic_dependence: float = 0.0
    normalization_dependence: float = 0.0
    theorem_import_dependence: float = 0.0
    axis_type: AxisType = AxisType.VECTOR

    def magnitude(self) -> float:
        """L2 over sub-dimensions. Higher = more assumption load."""
        return math.sqrt(
            self.catalog_dependence**2
            + self.numeric_dependence**2
            + self.heuristic_dependence**2
            + self.normalization_dependence**2
            + self.theorem_import_dependence**2
        )

    def max_dimension(self) -> Tuple[str, float]:
        """Returns (name, value) of the highest sub-dimension."""
        items = [
            ("catalog_dependence", self.catalog_dependence),
            ("numeric_dependence", self.numeric_dependence),
            ("heuristic_dependence", self.heuristic_dependence),
            ("normalization_dependence", self.normalization_dependence),
            ("theorem_import_dependence", self.theorem_import_dependence),
        ]
        return max(items, key=lambda x: x[1])


@dataclass(frozen=True)
class ComputationalFriction:
    """Axis 6 (Gemini v2.3 addition): wall-clock + oracle-call cost to
    produce the Claim.

    Populated by Pre-Tier-0 0b telemetry instrumentation (already
    shipped Day 1-2). Cross-domain envs emit
    info["elapsed_seconds"] + info["oracle_calls"]; this axis aggregates
    them per Claim.
    """

    elapsed_seconds: Optional[float]
    oracle_calls: Optional[int]
    peak_memory_mb: Optional[float] = None  # DEFERRED: psutil dep not justified at v0
    metric_id: str = "wall_clock_oracle_count"
    axis_type: AxisType = AxisType.METRIC


# ---------------------------------------------------------------------------
# EvidenceField — top-level factual evidence object
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceField:
    """Factual axes derived from substrate observations.

    Six axes, type-separated from PolicyField (sister module). Lives on
    every Claim that has been through the falsification battery.

    Per substrate v2.3 §6.2 P1: bridge_proximity is DEFERRED behind a
    future BridgeGraph primitive. The 6 axes here are the v2.3 commitment.
    """

    distance_to_target: DistanceToTarget
    battery_survival_depth: BatterySurvivalDepth
    verification_depth: VerificationDepth
    exclusion_distance: ExclusionDistance
    assumption_load: AssumptionLoad
    computational_friction: ComputationalFriction
    axis_confidence: Mapping[str, float] = field(default_factory=dict)
    """Per-axis confidence ∈ [0, 1]. Keys match axis names."""

    def all_axis_types(self) -> Mapping[str, AxisType]:
        """Map of axis name → AxisType, for consumers that need to know
        which axes are metric vs ordinal vs vector."""
        return {
            "distance_to_target": self.distance_to_target.axis_type,
            "battery_survival_depth": self.battery_survival_depth.axis_type,
            "verification_depth": self.verification_depth.axis_type,
            "exclusion_distance": self.exclusion_distance.axis_type,
            "assumption_load": self.assumption_load.axis_type,
            "computational_friction": self.computational_friction.axis_type,
        }

    def populated_axes(self) -> Tuple[str, ...]:
        """Names of axes whose primary value is not None.
        Useful for downstream filtering."""
        out: List[str] = []
        if self.distance_to_target.value is not None:
            out.append("distance_to_target")
        if self.battery_survival_depth.n_total > 0:
            out.append("battery_survival_depth")
        if self.verification_depth.min_precision_dps is not None or self.verification_depth.methods_used:
            out.append("verification_depth")
        if self.exclusion_distance.value is not None:
            out.append("exclusion_distance")
        if self.assumption_load.magnitude() > 0:
            out.append("assumption_load")
        if (
            self.computational_friction.elapsed_seconds is not None
            or self.computational_friction.oracle_calls is not None
        ):
            out.append("computational_friction")
        return tuple(out)

    def has_metric_axes(self) -> Tuple[str, ...]:
        """Names of axes that are AxisType.METRIC AND populated. For
        consumers (e.g., ExclusionCertificate distance queries) that
        require a metric axis."""
        return tuple(
            name
            for name in self.populated_axes()
            if self.all_axis_types()[name] == AxisType.METRIC
        )


# ---------------------------------------------------------------------------
# Builders — construct EvidenceField from substrate observations
# ---------------------------------------------------------------------------


def build_evidence_field(
    *,
    kill_vector: Optional[Any] = None,  # FORWARD-REF: prometheus_math.kill_vector.KillVector
    precision_metadata: Optional[Mapping[str, Any]] = None,
    caveats: Sequence[str] = (),
    elapsed_seconds: Optional[float] = None,
    oracle_calls: Optional[int] = None,
    coordinate_chart_id: Optional[str] = None,
    nearest_exclusion_certificate_ref: Optional[str] = None,
    exclusion_distance_value: Optional[float] = None,
    methods_used: Sequence[str] = (),
    stability_aggregate: Optional[Mapping[str, Any]] = None,
    target_band_name: str = "out_of_band",
    axis_confidence: Optional[Mapping[str, float]] = None,
) -> EvidenceField:
    """Construct an EvidenceField from substrate observations.

    Late-binding to upstream primitives via Optional types — when P0 /
    P3 / P4 / P2 land, callers populate the additional kwargs.

    For the canonical pre-emission usage (in P5 NearMissCorpus), all
    six axes are populated from the corresponding substrate fields.
    For partial usage (e.g., during Pre-Tier-0 testing), unpopulated
    axes default to NULL-like values.
    """

    # Axis 1: distance_to_target — derived from kill_vector
    dtt = _build_distance_to_target(kill_vector, target_band_name)

    # Axis 2: battery_survival_depth — derived from kill_vector
    bsd = _build_battery_survival_depth(kill_vector)

    # Axis 3: verification_depth — derived from precision_metadata + methods_used + stability
    vd = _build_verification_depth(
        precision_metadata=precision_metadata,
        methods_used=methods_used,
        stability_aggregate=stability_aggregate,
        kill_vector=kill_vector,
    )

    # Axis 4: exclusion_distance — populated only with chart+cert
    ed = _build_exclusion_distance(
        coordinate_chart_id=coordinate_chart_id,
        nearest_certificate_ref=nearest_exclusion_certificate_ref,
        value=exclusion_distance_value,
    )

    # Axis 5: assumption_load — derived from caveats + method/precision metadata
    al = _build_assumption_load(
        caveats=caveats,
        precision_metadata=precision_metadata,
        methods_used=methods_used,
    )

    # Axis 6: computational_friction — from telemetry
    cf = ComputationalFriction(
        elapsed_seconds=elapsed_seconds,
        oracle_calls=oracle_calls,
    )

    return EvidenceField(
        distance_to_target=dtt,
        battery_survival_depth=bsd,
        verification_depth=vd,
        exclusion_distance=ed,
        assumption_load=al,
        computational_friction=cf,
        axis_confidence=dict(axis_confidence or {}),
    )


# ---------------------------------------------------------------------------
# Internal builders (per-axis)
# ---------------------------------------------------------------------------


def _build_distance_to_target(
    kill_vector: Optional[Any],
    target_band_name: str,
) -> DistanceToTarget:
    """Find the named target-band component in kill_vector and extract margin."""
    if kill_vector is None:
        return DistanceToTarget(value=None, unit=None)
    components = getattr(kill_vector, "components", None)
    if not components:
        return DistanceToTarget(value=None, unit=None)
    for c in components:
        if getattr(c, "falsifier_name", None) == target_band_name:
            margin = getattr(c, "margin", None)
            triggered = getattr(c, "triggered", False)
            # Convention: triggered (in band) → 0.0; not triggered (out of band) → margin
            value = 0.0 if triggered else (None if margin is None else float(margin))
            return DistanceToTarget(
                value=value,
                unit=getattr(c, "margin_unit", None),
                computed_at_dps=getattr(c, "precision_dps", None),
            )
    return DistanceToTarget(value=None, unit=None)


def _build_battery_survival_depth(kill_vector: Optional[Any]) -> BatterySurvivalDepth:
    if kill_vector is None:
        return BatterySurvivalDepth(n_passed=0, n_total=0)
    components = getattr(kill_vector, "components", None)
    if not components:
        return BatterySurvivalDepth(n_passed=0, n_total=0)
    passed: List[str] = []
    failed: List[str] = []
    for c in components:
        name = getattr(c, "falsifier_name", "?")
        if getattr(c, "triggered", False):
            failed.append(name)
        else:
            passed.append(name)
    return BatterySurvivalDepth(
        n_passed=len(passed),
        n_total=len(passed) + len(failed),
        falsifiers_passed=tuple(passed),
        falsifiers_failed=tuple(failed),
    )


def _build_verification_depth(
    *,
    precision_metadata: Optional[Mapping[str, Any]],
    methods_used: Sequence[str],
    stability_aggregate: Optional[Mapping[str, Any]],
    kill_vector: Optional[Any],
) -> VerificationDepth:
    # min_precision_dps from precision_metadata or aggregated from kill_vector
    min_dps: Optional[int] = None
    if precision_metadata and precision_metadata.get("dps") is not None:
        min_dps = int(precision_metadata["dps"])
    elif kill_vector is not None:
        components = getattr(kill_vector, "components", None) or ()
        dps_values = [
            getattr(c, "precision_dps", None)
            for c in components
            if getattr(c, "precision_dps", None) is not None
        ]
        if dps_values:
            min_dps = int(min(dps_values))

    # methods_used: prefer explicit param; fall back to kill_vector aggregation
    methods: Tuple[str, ...] = tuple(sorted(set(methods_used)))
    if not methods and kill_vector is not None:
        components = getattr(kill_vector, "components", None) or ()
        method_set = {
            str(getattr(c, "method", "unknown"))
            for c in components
            if getattr(c, "method", None)
        }
        methods = tuple(sorted(method_set))

    # convergence_summary
    if precision_metadata and precision_metadata.get("convergence"):
        conv_summary = str(precision_metadata["convergence"])
    elif kill_vector is not None:
        components = getattr(kill_vector, "components", None) or ()
        conv_set = {
            str(getattr(c, "convergence_status", "n/a"))
            for c in components
            if getattr(c, "convergence_status", None)
        }
        if not conv_set:
            conv_summary = "n/a"
        elif conv_set == {"converged"}:
            conv_summary = "all_converged"
        elif "failed_max_steps" in conv_set or "nan_returned" in conv_set:
            conv_summary = "some_failed" if "converged" in conv_set else "all_failed"
        else:
            conv_summary = "mixed"
    else:
        conv_summary = "n/a"

    return VerificationDepth(
        min_precision_dps=min_dps,
        methods_used=methods,
        convergence_summary=conv_summary,
        stability_aggregate=dict(stability_aggregate) if stability_aggregate else None,
    )


def _build_exclusion_distance(
    *,
    coordinate_chart_id: Optional[str],
    nearest_certificate_ref: Optional[str],
    value: Optional[float],
) -> ExclusionDistance:
    """Populated only when chart + cert + value all supplied. Otherwise
    NULL with an explanatory reason — anti-fake-topology.

    Order of checks: structural prerequisites first (chart + cert),
    then computed value. The reason_unpopulated message names the
    most-upstream missing piece so consumers know whether to wait for
    P0 / P4 / a real distance computation.
    """
    if coordinate_chart_id is None and nearest_certificate_ref is None:
        reason = (
            "no CoordinateChart registered for region AND no "
            "ExclusionCertificate available (P0 + P4 both not landed for this domain)"
        )
    elif coordinate_chart_id is None:
        reason = "no CoordinateChart registered for region (P0 not landed for this domain)"
    elif nearest_certificate_ref is None:
        reason = "no ExclusionCertificate registered nearby (P4 not landed)"
    elif value is None:
        reason = (
            "chart and certificate both registered but no exclusion distance "
            "value computed yet"
        )
    else:
        return ExclusionDistance(
            value=float(value),
            chart_id=coordinate_chart_id,
            nearest_certificate_ref=nearest_certificate_ref,
            metric_id="chart_native_metric",
        )

    return ExclusionDistance(
        value=None,
        chart_id=coordinate_chart_id,
        nearest_certificate_ref=nearest_certificate_ref,
        reason_unpopulated=reason,
    )


def _build_assumption_load(
    *,
    caveats: Sequence[str],
    precision_metadata: Optional[Mapping[str, Any]],
    methods_used: Sequence[str],
) -> AssumptionLoad:
    """Heuristic mapping from caveats / method / precision to assumption-load
    sub-dimensions. Each ∈ [0, 1]. Conservative defaults; tune as data
    accumulates.
    """
    cv = set(caveats or ())
    catalog_dep = 0.0
    if "catalog_completeness_partial" in cv or "catalog_lookup_only" in cv:
        catalog_dep = 0.7
    if any("catalog" in c.lower() for c in cv):
        catalog_dep = max(catalog_dep, 0.5)

    numeric_dep = 0.0
    if precision_metadata:
        dps = precision_metadata.get("dps")
        expected_min = precision_metadata.get("expected_min_dps")
        if dps is not None and expected_min is not None and dps < expected_min:
            numeric_dep = 0.8
        elif dps is not None and dps < 30:
            numeric_dep = 0.5
        elif "precision_below_expected" in cv:
            numeric_dep = max(numeric_dep, 0.6)

    heuristic_dep = 0.0
    if "heuristic" in str(methods_used).lower():
        heuristic_dep = 0.6
    if any("heuristic" in c.lower() for c in cv):
        heuristic_dep = max(heuristic_dep, 0.5)

    normalization_dep = 0.0
    if "canonicalization_undecidable" in cv or "canonical_form_choice" in cv:
        normalization_dep = 0.7
    if any("normaliz" in c.lower() or "canonical" in c.lower() for c in cv):
        normalization_dep = max(normalization_dep, 0.4)

    theorem_dep = 0.0
    # The KillVector +8 component `requires_unproven_conjecture` would
    # surface here once the kill_vector v2 lands; for now use caveat-text.
    if "requires_unproven_conjecture" in cv or "assumes_rh" in cv or "assumes_bsd" in cv:
        theorem_dep = 0.9

    return AssumptionLoad(
        catalog_dependence=catalog_dep,
        numeric_dependence=numeric_dep,
        heuristic_dependence=heuristic_dep,
        normalization_dependence=normalization_dep,
        theorem_import_dependence=theorem_dep,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


__all__ = [
    "AxisType",
    "DistanceToTarget",
    "BatterySurvivalDepth",
    "VerificationDepth",
    "ExclusionDistance",
    "AssumptionLoad",
    "ComputationalFriction",
    "EvidenceField",
    "build_evidence_field",
]
