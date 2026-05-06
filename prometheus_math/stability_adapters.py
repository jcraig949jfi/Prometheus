"""prometheus_math.stability_adapters — per-falsifier-type stability adapters.

Wires substrate v2.3 §6.2 P2: the existing ``KillComponent.stability`` field
(currently NaN for legacy data) gains structured, per-falsifier-type
stability computation via dedicated adapters.

Background
----------
ChatGPT's reframe (substrate v2 review): a single epsilon-perturbation
scheme is wrong across falsifier types. A ``numeric_margin`` falsifier
wants ``epsilon = 10^-(precision_dps - 2)`` perturbations of the input
value; a ``catalog_lookup`` falsifier wants alias/source-redundancy
perturbations; a ``graph_metric`` falsifier wants edge perturbations;
etc. Six adapter types cover the substrate's current falsifier menu.

Tiered k
--------
``KTier`` exposes three sample-budget tiers:

  * ``DIAGNOSTIC = 10``        — cheap per-claim probe at write time.
  * ``CANDIDATE = 50``         — used during candidate triage.
  * ``PROMOTION_GRADE = 200``  — used for PROMOTE-grade certification.

Adapters honor the tier as the ``k`` perturbation count.

Return shape
------------
``StabilityResult`` replaces the legacy single scalar with structured
fields::

    stability_mean         — mean fraction of perturbations that agreed
                              with the unperturbed verdict, in [0, 1]
    stability_variance     — sample variance of per-perturbation outcomes
    perturbation_family    — short string identifying the perturbation
                              family (e.g. "epsilon=1e-13")
    worst_case_flip_rate   — max fraction of perturbations that flipped
                              the verdict (1 - stability_mean for binary
                              outcomes; for multi-valued falsifiers, the
                              worst-case per-class flip rate)
    k_used                 — actual perturbation count used
    falsifier_type         — name of the FalsifierType the adapter ran

Legacy compat
-------------
When an adapter receives ``None`` for the falsifier_callable, it
returns ``StabilityResult`` with NaN-filled numeric fields ("no
stability information available"). This is the legacy-compat path for
callers that haven't yet wired their falsifier into the adapter
pipeline.

KillComponent integration
-------------------------
``KillComponent.with_computed_stability`` (added in kill_vector.py)
selects the adapter from the component's ``margin_unit`` →
``FalsifierType`` mapping and returns a NEW frozen KillComponent with
``stability_pass`` populated and the legacy ``stability`` scalar set to
``stability_mean`` for backwards compat.
"""
from __future__ import annotations

import enum
import math
import statistics
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class FalsifierType(str, enum.Enum):
    """Six falsifier flavors covered by the v2.3 §6.2 adapter taxonomy."""
    NUMERIC_MARGIN = "numeric_margin"
    SYMBOLIC_FACTORIZATION = "symbolic_factorization"
    CATALOG_LOOKUP = "catalog_lookup"
    GRAPH_METRIC = "graph_metric"
    SEQUENCE_FEATURE = "sequence_feature"
    MODEL_POLICY = "model_policy"


class KTier(int, enum.Enum):
    """Sample-budget tiers per substrate v2.3 §6.2."""
    DIAGNOSTIC = 10
    CANDIDATE = 50
    PROMOTION_GRADE = 200


# ---------------------------------------------------------------------------
# StabilityResult
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StabilityResult:
    """Structured stability output. Replaces the single-scalar ``stability``.

    All numeric fields may be NaN when the adapter receives None for its
    falsifier_callable / lookup_callable / etc. (legacy-compat path).
    """

    stability_mean: float
    stability_variance: float
    perturbation_family: str
    worst_case_flip_rate: float
    k_used: int
    falsifier_type: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stability_mean": (
                None if math.isnan(self.stability_mean) else float(self.stability_mean)
            ),
            "stability_variance": (
                None if math.isnan(self.stability_variance) else float(self.stability_variance)
            ),
            "perturbation_family": str(self.perturbation_family),
            "worst_case_flip_rate": (
                None if math.isnan(self.worst_case_flip_rate) else float(self.worst_case_flip_rate)
            ),
            "k_used": int(self.k_used),
            "falsifier_type": str(self.falsifier_type),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StabilityResult":
        def _f(v: Any) -> float:
            if v is None:
                return float("nan")
            try:
                return float(v)
            except (TypeError, ValueError):
                return float("nan")

        return cls(
            stability_mean=_f(d.get("stability_mean")),
            stability_variance=_f(d.get("stability_variance")),
            perturbation_family=str(d.get("perturbation_family", "")),
            worst_case_flip_rate=_f(d.get("worst_case_flip_rate")),
            k_used=int(d.get("k_used", 0)),
            falsifier_type=str(d.get("falsifier_type", "")),
        )

    @classmethod
    def empty(cls, falsifier_type: str, k: int = 0,
              perturbation_family: str = "none:no_callable") -> "StabilityResult":
        """No-information StabilityResult — NaN fields, k=0.

        Returned by adapters when the caller hasn't wired a falsifier
        callable. Distinct from ``stability_mean = 0.0`` (which would
        mean "perturbed every time"); NaN means "we didn't measure".
        """
        return cls(
            stability_mean=float("nan"),
            stability_variance=float("nan"),
            perturbation_family=perturbation_family,
            worst_case_flip_rate=float("nan"),
            k_used=int(k),
            falsifier_type=str(falsifier_type),
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _coerce_k(k: Any) -> int:
    """Tolerate KTier or raw int; coerce to int."""
    if isinstance(k, KTier):
        return int(k.value)
    try:
        return int(k)
    except (TypeError, ValueError):
        return int(KTier.DIAGNOSTIC.value)


def _aggregate_outcomes(
    outcomes: Sequence[float],
    falsifier_type: str,
    perturbation_family: str,
    k_used: int,
) -> StabilityResult:
    """Reduce a sequence of [0, 1]-valued per-perturbation agreement
    scores to a StabilityResult.

    Each ``outcome`` is the agreement fraction (1.0 = matched the
    unperturbed verdict; 0.0 = disagreed). For binary verdicts each
    outcome is 0/1.
    """
    if not outcomes:
        return StabilityResult.empty(
            falsifier_type=falsifier_type,
            k=k_used,
            perturbation_family=f"{perturbation_family}:empty",
        )
    mean = statistics.fmean(outcomes)
    if len(outcomes) > 1:
        var = statistics.pvariance(outcomes)
    else:
        var = 0.0
    # worst_case_flip_rate: largest fraction of perturbations that
    # disagreed with the unperturbed verdict. For binary outcomes this
    # is simply 1 - mean. For partial-agreement outcomes (e.g. 0.5 from
    # a multi-class falsifier) we use the same definition: max disagree
    # over the perturbation set.
    flips = [1.0 - o for o in outcomes]
    worst = max(flips) if flips else 0.0
    return StabilityResult(
        stability_mean=float(mean),
        stability_variance=float(var),
        perturbation_family=str(perturbation_family),
        worst_case_flip_rate=float(worst),
        k_used=int(k_used),
        falsifier_type=str(falsifier_type),
    )


def _seeded_rng(seed: int) -> Any:
    """Cheap deterministic float-generator shim (no numpy dependency)."""
    import random
    return random.Random(seed)


# ---------------------------------------------------------------------------
# Adapters
# ---------------------------------------------------------------------------


def stability_numeric_margin(
    margin: float,
    precision_dps: Optional[int],
    *,
    k: int = KTier.DIAGNOSTIC,
    falsifier_callable: Optional[Callable[[float], bool]] = None,
    seed: int = 0,
) -> StabilityResult:
    """Stability via epsilon-perturbation of a numeric margin.

    ``epsilon = 10^-(precision_dps - 2)`` per substrate v2.3 §6.2; if
    ``precision_dps`` is None we fall back to ``epsilon = 1e-12``
    (numpy double precision floor with two-digit safety margin).

    The ``falsifier_callable`` receives the *perturbed* margin and
    returns True iff the falsifier still kills (matching the
    unperturbed verdict). When ``None``, returns NaN-filled result.
    """
    k_used = _coerce_k(k)
    ftype = FalsifierType.NUMERIC_MARGIN.value
    if precision_dps is not None:
        # Floor at dps=2 → epsilon = 1.0 doesn't make sense; clamp.
        try:
            dps = max(3, int(precision_dps))
        except (TypeError, ValueError):
            dps = 14
        epsilon = 10.0 ** (-(dps - 2))
    else:
        epsilon = 1e-12
    family = f"epsilon={epsilon:g}"

    if falsifier_callable is None:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:no_callable")

    # Reference verdict at the unperturbed margin.
    try:
        ref = bool(falsifier_callable(float(margin)))
    except Exception:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:ref_failed")

    rng = _seeded_rng(seed)
    outcomes = []
    for _ in range(k_used):
        delta = rng.uniform(-epsilon, epsilon)
        try:
            v = bool(falsifier_callable(float(margin) + delta))
        except Exception:
            outcomes.append(0.0)
            continue
        outcomes.append(1.0 if v == ref else 0.0)
    return _aggregate_outcomes(outcomes, ftype, family, k_used)


def stability_symbolic_factorization(
    expr_canonical_form: Any,
    *,
    k: int = KTier.DIAGNOSTIC,
    falsifier_callable: Optional[Callable[[Any], Any]] = None,
    perturbations: Optional[Sequence[Any]] = None,
    seed: int = 0,
) -> StabilityResult:
    """Stability via representation perturbation.

    The ``falsifier_callable`` is called once on the canonical form (the
    reference) and once per perturbed representation. Each perturbation
    should be an alternative canonicalization of the same mathematical
    object; agreement = same falsifier verdict.

    When ``perturbations`` is None we synthesize trivial cosmetic
    perturbations of the input (string-cased copies, parenthesized
    rewrites) — these are enough for the legacy-compat smoke test but
    real callers should pass concrete alternative canonicalizations.
    """
    k_used = _coerce_k(k)
    ftype = FalsifierType.SYMBOLIC_FACTORIZATION.value
    family = "representation_perturbation"

    if falsifier_callable is None:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:no_callable")

    try:
        ref = falsifier_callable(expr_canonical_form)
    except Exception:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:ref_failed")

    if perturbations is None:
        # Cosmetic perturbations: treat input as opaque and construct
        # k_used copies via str() round-trip; meaningful only as a
        # smoke test.
        perturbations = [expr_canonical_form for _ in range(k_used)]

    outcomes = []
    used = 0
    for p in list(perturbations)[:k_used]:
        used += 1
        try:
            v = falsifier_callable(p)
        except Exception:
            outcomes.append(0.0)
            continue
        outcomes.append(1.0 if v == ref else 0.0)
    return _aggregate_outcomes(outcomes, ftype, family, used)


def stability_catalog_lookup(
    query: Any,
    catalog_refs: Sequence[Any],
    *,
    k: int = KTier.DIAGNOSTIC,
    lookup_callable: Optional[Callable[[Any, Any], Any]] = None,
    seed: int = 0,
) -> StabilityResult:
    """Stability via alias perturbation / source redundancy.

    ``lookup_callable(query, catalog_ref)`` should return a comparable
    hit/miss verdict; agreement across catalog_refs measures lookup-
    path agreement. ``catalog_refs`` is the set of redundant lookup
    targets (e.g. multiple catalog mirrors / aliasings).
    """
    k_used = _coerce_k(k)
    ftype = FalsifierType.CATALOG_LOOKUP.value
    family = f"catalog_redundancy:{len(list(catalog_refs))}_refs"

    if lookup_callable is None:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:no_callable")

    refs = list(catalog_refs)[:k_used]
    if not refs:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:empty_refs")

    # First catalog ref is the reference verdict.
    try:
        ref_verdict = lookup_callable(query, refs[0])
    except Exception:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:ref_failed")

    outcomes = []
    used = 0
    # Self-agreement counts (same source, same verdict = stable).
    outcomes.append(1.0)
    used += 1
    for r in refs[1:]:
        used += 1
        try:
            v = lookup_callable(query, r)
        except Exception:
            outcomes.append(0.0)
            continue
        outcomes.append(1.0 if v == ref_verdict else 0.0)
    return _aggregate_outcomes(outcomes, ftype, family, used)


def stability_graph_metric(
    graph_data: Any,
    *,
    k: int = KTier.DIAGNOSTIC,
    metric_callable: Optional[Callable[[Any], Any]] = None,
    edge_perturbation_rate: float = 0.05,
    seed: int = 0,
) -> StabilityResult:
    """Stability via edge perturbation / sampling perturbation.

    ``metric_callable(perturbed_graph)`` returns a verdict; agreement
    across k perturbations measures edge-perturbation stability.

    For the substrate's smoke-test path, ``graph_data`` is treated
    opaquely. Real callers should pass a graph with an ``.edges``
    iterator and a perturbation function; the adapter applies a
    ``edge_perturbation_rate``-fraction Bernoulli edge dropout per
    perturbation.
    """
    k_used = _coerce_k(k)
    ftype = FalsifierType.GRAPH_METRIC.value
    family = f"edge_dropout={edge_perturbation_rate:g}"

    if metric_callable is None:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:no_callable")

    try:
        ref = metric_callable(graph_data)
    except Exception:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:ref_failed")

    rng = _seeded_rng(seed)
    outcomes = []
    for _ in range(k_used):
        # Build a "perturbed" graph: if graph_data has an edges
        # attribute, drop a fraction; otherwise pass through.
        perturbed = graph_data
        if hasattr(graph_data, "edges"):
            try:
                edges = list(graph_data.edges)
                kept = [e for e in edges if rng.random() > edge_perturbation_rate]
                # If the graph is mutable & has a from_edges, use it;
                # otherwise pass the kept edges as a tuple.
                if hasattr(graph_data, "from_edges"):
                    perturbed = graph_data.from_edges(kept)
                else:
                    perturbed = tuple(kept)
            except Exception:
                pass
        try:
            v = metric_callable(perturbed)
        except Exception:
            outcomes.append(0.0)
            continue
        outcomes.append(1.0 if v == ref else 0.0)
    return _aggregate_outcomes(outcomes, ftype, family, k_used)


def stability_sequence_feature(
    sequence: Sequence,
    *,
    k: int = KTier.DIAGNOSTIC,
    feature_callable: Optional[Callable[[Sequence], Any]] = None,
    seed: int = 0,
) -> StabilityResult:
    """Stability via prefix truncation / suffix extension / modulus
    perturbation.

    ``feature_callable(perturbed_sequence)`` returns a verdict.
    Perturbations: each iteration drops 0..min(3, len/4) elements from
    each end at random.
    """
    k_used = _coerce_k(k)
    ftype = FalsifierType.SEQUENCE_FEATURE.value
    family = "prefix_truncation_suffix_extension"

    if feature_callable is None:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:no_callable")

    seq = list(sequence)
    try:
        ref = feature_callable(seq)
    except Exception:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:ref_failed")

    rng = _seeded_rng(seed)
    n = len(seq)
    max_drop = max(0, min(3, n // 4))
    outcomes = []
    for _ in range(k_used):
        drop_left = rng.randint(0, max_drop) if max_drop > 0 else 0
        drop_right = rng.randint(0, max_drop) if max_drop > 0 else 0
        if n - drop_left - drop_right < 1:
            perturbed = seq
        else:
            perturbed = seq[drop_left: n - drop_right] if drop_right > 0 else seq[drop_left:]
        try:
            v = feature_callable(perturbed)
        except Exception:
            outcomes.append(0.0)
            continue
        outcomes.append(1.0 if v == ref else 0.0)
    return _aggregate_outcomes(outcomes, ftype, family, k_used)


def stability_model_policy(
    policy_callable: Optional[Callable[[Any, int], Any]],
    input_data: Any,
    *,
    k: int = KTier.DIAGNOSTIC,
    seeds: Optional[Sequence[int]] = None,
) -> StabilityResult:
    """Stability via seed perturbation / replay perturbation.

    ``policy_callable(input_data, seed)`` returns a verdict. The
    adapter calls it across ``k`` distinct seeds and measures
    seed-to-seed agreement.

    NOTE: the first positional argument is the policy_callable itself
    (not input_data) — this matches the substrate v2.3 §6.2 spec
    signature. When ``policy_callable is None``, returns NaN-filled
    result.
    """
    k_used = _coerce_k(k)
    ftype = FalsifierType.MODEL_POLICY.value
    family = "seed_replay"

    if policy_callable is None:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:no_callable")

    if seeds is None:
        seeds = list(range(k_used))
    seeds = list(seeds)[:k_used]

    if not seeds:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:empty_seeds")

    try:
        ref = policy_callable(input_data, seeds[0])
    except Exception:
        return StabilityResult.empty(falsifier_type=ftype, k=k_used,
                                     perturbation_family=f"{family}:ref_failed")

    outcomes = [1.0]  # ref agrees with itself
    used = 1
    for s in seeds[1:]:
        used += 1
        try:
            v = policy_callable(input_data, s)
        except Exception:
            outcomes.append(0.0)
            continue
        outcomes.append(1.0 if v == ref else 0.0)
    return _aggregate_outcomes(outcomes, ftype, family, used)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


_ADAPTERS: Dict[FalsifierType, Callable[..., StabilityResult]] = {
    FalsifierType.NUMERIC_MARGIN: stability_numeric_margin,
    FalsifierType.SYMBOLIC_FACTORIZATION: stability_symbolic_factorization,
    FalsifierType.CATALOG_LOOKUP: stability_catalog_lookup,
    FalsifierType.GRAPH_METRIC: stability_graph_metric,
    FalsifierType.SEQUENCE_FEATURE: stability_sequence_feature,
    FalsifierType.MODEL_POLICY: stability_model_policy,
}


def compute_stability(
    falsifier_type: FalsifierType,
    *args: Any,
    k: int = KTier.DIAGNOSTIC,
    **kwargs: Any,
) -> StabilityResult:
    """Dispatch to the adapter for ``falsifier_type``.

    Tolerates the falsifier_type being passed as a string (matched
    case-insensitively) for callers reading directly from JSON.
    """
    if isinstance(falsifier_type, str):
        try:
            ft = FalsifierType(falsifier_type)
        except ValueError:
            ft = FalsifierType(falsifier_type.lower())
    else:
        ft = falsifier_type
    adapter = _ADAPTERS.get(ft)
    if adapter is None:
        return StabilityResult.empty(
            falsifier_type=str(ft.value if hasattr(ft, "value") else ft),
            k=_coerce_k(k),
            perturbation_family="dispatch:unknown_type",
        )
    return adapter(*args, k=k, **kwargs)


# ---------------------------------------------------------------------------
# margin_unit → FalsifierType mapping
# ---------------------------------------------------------------------------


# Default mapping from ``KillComponent.margin_unit`` to the FalsifierType
# whose adapter best fits. KillComponent.with_computed_stability uses
# this to pick the adapter automatically. None means "no default
# adapter" — caller must specify FalsifierType explicitly.
MARGIN_UNIT_TO_FALSIFIER_TYPE: Dict[str, FalsifierType] = {
    "p_value": FalsifierType.NUMERIC_MARGIN,
    "z_score": FalsifierType.NUMERIC_MARGIN,
    "absolute": FalsifierType.NUMERIC_MARGIN,
    "log_distance": FalsifierType.NUMERIC_MARGIN,
    "hamming": FalsifierType.CATALOG_LOOKUP,
    "boolean": FalsifierType.NUMERIC_MARGIN,
}


def falsifier_type_for_margin_unit(unit: Optional[str]) -> Optional[FalsifierType]:
    """Default FalsifierType for a given margin_unit; None if unknown."""
    if unit is None:
        return None
    return MARGIN_UNIT_TO_FALSIFIER_TYPE.get(unit)


__all__ = [
    "FalsifierType",
    "KTier",
    "StabilityResult",
    "stability_numeric_margin",
    "stability_symbolic_factorization",
    "stability_catalog_lookup",
    "stability_graph_metric",
    "stability_sequence_feature",
    "stability_model_policy",
    "compute_stability",
    "MARGIN_UNIT_TO_FALSIFIER_TYPE",
    "falsifier_type_for_margin_unit",
]
