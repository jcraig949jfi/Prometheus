"""sigma_kernel.coordinate_chart — Tier-0 P0 primitive: typed coordinate
charts + canonicalization protocol over falsification evidence.

Joint sprint sync points S5 / T4-T5 (see
``pivot/techne_ergon_joint_sprint_2026-05-05.md``); spec from substrate
v2.3 §6.1 (see ``pivot/substrate_v2_proposal_2026-05-05.md``).

Why this exists
---------------
Per ChatGPT/Gemini convergence and Aporia Study 17, the substrate must
not allow exclusion-distance / neighborhood / negative-space queries
unless the object and the exclusion certificate live in the **same
registered coordinate chart with a registered metric**. Heterogeneous
spaces have no global metric; faking one would silently pollute Ergon's
Learner via leaked geometry.

What this DOES
--------------
* Defines :class:`CanonicalizationProtocol` — typed wrapper around a
  canonicalizer impl (Aporia Study 17). Subsumes Study 07's
  ``cohomological_functor`` recommendation as one registered impl.
* Defines :class:`CoordinateChart` — a (domain, region_key)-scoped
  bundle of (coordinate axes, canonicalization, metric, equivalence
  relations, admissible region, valid operations).
* Defines :class:`ChartRegistry` — substrate-level registry. Charts
  register themselves at import time; downstream consumers
  (ExclusionCertificate, P5 NearMissCorpus, EvidenceField) look up by
  ``(domain, region_key)`` or by ``chart_id``.
* Provides a module-level singleton :data:`DEFAULT_REGISTRY` plus
  free-function :func:`register_chart` / :func:`get_chart` aliases for
  ergonomics.
* Integrates with :mod:`prometheus_math.canonicalizer_observability` —
  :meth:`ChartRegistry.hot_swap_pending` returns True when the observed
  canonicalizer distribution crosses the 70% threshold for any single
  canonicalizer.

What this DOES NOT do
---------------------
* Modify any existing kernel opcode or schema. CoordinateChart is a
  NEW primitive that lives alongside the kernel; it is referenced by
  later primitives (ExclusionCertificate.coordinate_chart_id,
  EvidenceField.exclusion_distance.metric_id) but does not edit them.
* Persist charts to the database. Charts live in code/registry only at
  this tier; a Postgres migration may follow once the registry shape
  stabilizes.
* Implement the actual hot-swap. This module *detects* hot-swap
  imminence; the actual swap-policy is downstream (Tier-1 / Tier-2).

Registry semantics
------------------
* ``chart_id`` format is ``"<domain>:<region_key>"`` (a single colon).
  This format is used both for lookup and for downstream references
  (e.g. ``ExclusionCertificate.coordinate_chart_id``).
* Re-registering a chart with the same ``chart_id`` raises
  :class:`ChartRegistrationError` by default. Pass ``replace=True``
  to override (intended for tests / hot-swap scenarios only).
* Lookup by ``(domain, region_key)`` and by ``chart_id`` are
  equivalent and round-trip.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

from prometheus_math.canonicalizer_observability import (
    HOT_SWAP_THRESHOLD,
    KNOWN_CANONICALIZERS,
    dominant_canonicalizer,
    hot_swap_imminent,
    observed_distribution,
)


# ---------------------------------------------------------------------------
# Decidability + canonicalizer impl enumerations
# ---------------------------------------------------------------------------


DecidabilityStatus = Literal["decidable", "undecidable", "conditional"]
"""Canonicalization decidability flag. Per substrate v2.3 §6.1, the
literature documents canonicalization-undecidable cases (Novikov word
problem, Drozd wild quiver representation type, dim ≥ 4 manifold
homeomorphism). Substrate must flag these explicitly so downstream
consumers do not silently inflate archive coverage."""

VALID_DECIDABILITY = ("decidable", "undecidable", "conditional")
"""Tuple form of :data:`DecidabilityStatus` for runtime validation."""


REGISTERED_CANONICALIZER_IMPLS: Tuple[str, ...] = tuple(KNOWN_CANONICALIZERS) + (
    "reflection_quotient",      # Lehmer chart, Day-3 ship
    "stub",                     # placeholder for future / unspecified
)
"""All canonicalizer impls loadable as :class:`CanonicalizationProtocol`
values. Extends ``prometheus_math.canonicalizer_observability``'s
``KNOWN_CANONICALIZERS`` with the impls registered by Tier-0 (per the
v2.3 §6.1 enumeration). Open-vocabulary in practice; this tuple is
documentation + a soft validation hook."""


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ChartRegistrationError(RuntimeError):
    """Raised on duplicate chart_id registration without ``replace=True``."""


class ChartLookupError(KeyError):
    """Raised when a chart_id does not resolve. (Lookup helpers usually
    return ``None`` instead; this is for the strict form.)"""


# ---------------------------------------------------------------------------
# CanonicalizationProtocol (Aporia Study 17)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CanonicalizationProtocol:
    """Typed interface per Aporia Study 17.

    Subsumes Study 07's ``cohomological_functor`` recommendation as one
    registered impl. The substrate previously had a fixed enum
    ``{group_quotient, partition_refinement, ideal_reduction,
    variety_fingerprint}``; this protocol replaces that enum with an
    extensible interface plus an explicit decidability flag.

    Fields
    ------
    impl
        One of :data:`REGISTERED_CANONICALIZER_IMPLS` or a new
        domain-specific impl name. Open-vocabulary; the tuple is a soft
        documentation hook.
    decidability_status
        One of :data:`VALID_DECIDABILITY`. Critical: literature
        documents canonicalization-undecidable cases. Substrate must
        flag these explicitly.
    choice_dependencies
        Named choices the canonicalization is parameterized by — e.g.
        ``("normal_form_choice",)``, ``("ordering",)``,
        ``("lex_minimization",)``. Used downstream to detect when two
        "canonical forms" disagree because they made different choices
        rather than because the underlying objects differ.
    version
        Semver string; e.g. ``"1.0.0"``. Bumped when the canonicalizer's
        behavior changes (so cached canonical forms can be invalidated).
    canonicalize
        The actual implementation. Optional (registry-only entries can
        omit it for documentation purposes), but required for any chart
        whose ``CoordinateChart.canonicalization`` is actually called.
    """

    impl: str
    decidability_status: DecidabilityStatus
    choice_dependencies: Tuple[str, ...]
    version: str
    canonicalize: Optional[Callable[[Any], Any]] = None

    def __post_init__(self) -> None:
        if self.decidability_status not in VALID_DECIDABILITY:
            raise ValueError(
                f"decidability_status must be one of {VALID_DECIDABILITY}; "
                f"got {self.decidability_status!r}"
            )
        if not isinstance(self.impl, str) or not self.impl:
            raise ValueError(f"impl must be a non-empty string; got {self.impl!r}")
        if not isinstance(self.choice_dependencies, tuple):
            raise TypeError(
                "choice_dependencies must be a tuple (frozen); "
                f"got {type(self.choice_dependencies).__name__}"
            )
        if not isinstance(self.version, str) or not self.version:
            raise ValueError(f"version must be a non-empty semver string; got {self.version!r}")

    def apply(self, point: Any) -> Any:
        """Canonicalize a point. Raises if no implementation is bound."""
        if self.canonicalize is None:
            raise NotImplementedError(
                f"CanonicalizationProtocol(impl={self.impl!r}) has no bound "
                "canonicalize implementation; this is a registry-only entry."
            )
        return self.canonicalize(point)


# ---------------------------------------------------------------------------
# CoordinateChart
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CoordinateChart:
    """A (domain, region_key)-scoped local coordinate chart.

    Substrate v2.3 §6.1: charts are the metric scaffolding without
    which ExclusionCertificate and EvidenceField cannot safely talk
    about distance, neighborhoods, or negative space.

    Fields
    ------
    domain
        Coarse env / dataset id, e.g. ``"lehmer"``, ``"bsd"``,
        ``"mock_theta"``.
    region_key
        Slice id within the domain; e.g.
        ``"deg14:pm5:palindromic"``.
    coordinate_system
        Named coordinate axes — e.g. ``("c0","c1",...,"c7")``.
    canonicalization
        :class:`CanonicalizationProtocol` describing how raw
        coordinates are reduced to a canonical representative under
        the chart's equivalence relations.
    metric
        Distance function over **canonicalized** points. Must be
        symmetric and satisfy ``d(x, x) == 0``; triangle inequality
        is encouraged but not enforced (some substrate metrics are
        pseudo-metrics).
    metric_id
        Named identifier — e.g. ``"L2"``, ``"hamming"``,
        ``"edit_distance"``. Downstream evidence-field consumers use
        this to verify metric compatibility.
    equivalence_relations
        Tuple of relation names (free-text), e.g. ``("x→-x",)`` for
        the Lehmer chart's reflection invariance.
    admissible_region
        Predicate: True iff the input lies in this chart's admissible
        coordinate region (palindromic, reciprocal, degree-bounded,
        etc.).
    valid_operations
        Tuple of operation ids that preserve the chart's structure
        (i.e., map admissible points to admissible points and respect
        the equivalence relations).
    """

    domain: str
    region_key: str
    coordinate_system: Tuple[str, ...]
    canonicalization: CanonicalizationProtocol
    metric: Callable[[Any, Any], float]
    metric_id: str
    equivalence_relations: Tuple[str, ...]
    admissible_region: Callable[[Any], bool]
    valid_operations: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.domain, str) or ":" in self.domain:
            raise ValueError(
                f"domain must be a colon-free non-empty string; got {self.domain!r}"
            )
        if not isinstance(self.region_key, str) or not self.region_key:
            raise ValueError(f"region_key must be a non-empty string; got {self.region_key!r}")
        if not isinstance(self.coordinate_system, tuple):
            raise TypeError("coordinate_system must be a tuple")
        if not isinstance(self.equivalence_relations, tuple):
            raise TypeError("equivalence_relations must be a tuple")
        if not isinstance(self.valid_operations, tuple):
            raise TypeError("valid_operations must be a tuple")

    @property
    def chart_id(self) -> str:
        """Canonical identifier; format ``"<domain>:<region_key>"``."""
        return f"{self.domain}:{self.region_key}"

    def canonicalize(self, point: Any) -> Any:
        """Canonicalize a coordinate point via the chart's protocol."""
        return self.canonicalization.apply(point)

    def distance(self, a: Any, b: Any) -> float:
        """Distance between two coordinate points. **Both inputs are
        canonicalized first** so callers don't have to remember.

        Returns a non-negative float; symmetric in (a, b).
        """
        ca = self.canonicalize(a) if self.canonicalization.canonicalize is not None else a
        cb = self.canonicalize(b) if self.canonicalization.canonicalize is not None else b
        return float(self.metric(ca, cb))

    def admits(self, point: Any) -> bool:
        """True iff ``point`` lies in the chart's admissible region."""
        return bool(self.admissible_region(point))


# ---------------------------------------------------------------------------
# ChartRegistry
# ---------------------------------------------------------------------------


def _split_chart_id(chart_id: str) -> Tuple[str, str]:
    """Split a ``"<domain>:<region_key>"`` id. Splits on the FIRST colon
    only — region_key may itself contain colons (Lehmer's
    ``"deg14:pm5:palindromic"`` does)."""
    if not isinstance(chart_id, str) or ":" not in chart_id:
        raise ValueError(
            f'chart_id must be of the form "<domain>:<region_key>"; got {chart_id!r}'
        )
    domain, region_key = chart_id.split(":", 1)
    if not domain or not region_key:
        raise ValueError(
            f'chart_id must have non-empty domain and region_key; got {chart_id!r}'
        )
    return domain, region_key


class ChartRegistry:
    """Substrate-level chart registry.

    Charts register themselves at import time (via the module-level
    :func:`register_chart`); downstream consumers
    (ExclusionCertificate, P5 NearMissCorpus, EvidenceField) look them
    up by ``(domain, region_key)`` or by ``chart_id``.
    """

    def __init__(self) -> None:
        # keyed by chart_id; insertion-ordered for deterministic iteration
        self._charts: Dict[str, CoordinateChart] = {}

    # -- Mutation -----------------------------------------------------------

    def register(self, chart: CoordinateChart, *, replace: bool = False) -> None:
        """Register a chart.

        Raises :class:`ChartRegistrationError` if ``chart.chart_id`` is
        already registered and ``replace`` is False.
        """
        if not isinstance(chart, CoordinateChart):
            raise TypeError(f"register expects CoordinateChart; got {type(chart).__name__}")
        cid = chart.chart_id
        if cid in self._charts and not replace:
            raise ChartRegistrationError(
                f"chart_id {cid!r} already registered; pass replace=True to override"
            )
        self._charts[cid] = chart

    def unregister(self, chart_id: str) -> Optional[CoordinateChart]:
        """Remove a chart by id; returns the removed chart or None."""
        return self._charts.pop(chart_id, None)

    def clear(self) -> None:
        """Drop all registered charts. Intended for tests."""
        self._charts.clear()

    # -- Lookup -------------------------------------------------------------

    def lookup(self, domain: str, region_key: str) -> Optional[CoordinateChart]:
        """Look up a chart by ``(domain, region_key)``. Returns None if absent."""
        return self._charts.get(f"{domain}:{region_key}")

    def by_id(self, chart_id: str) -> Optional[CoordinateChart]:
        """Look up a chart by its full ``"<domain>:<region_key>"`` id."""
        return self._charts.get(chart_id)

    def require(self, chart_id: str) -> CoordinateChart:
        """Look up a chart by id; raise :class:`ChartLookupError` if absent.

        Use this in code paths that MUST have a chart (e.g.
        ExclusionCertificate creation per substrate v2.3 §6.1: "queries
        fail loudly if missing")."""
        chart = self._charts.get(chart_id)
        if chart is None:
            raise ChartLookupError(
                f"no chart registered for chart_id={chart_id!r}; "
                f"registered: {sorted(self._charts.keys())}"
            )
        return chart

    def all(self) -> List[CoordinateChart]:
        """Return all registered charts in registration order."""
        return list(self._charts.values())

    def ids(self) -> List[str]:
        """Return all registered chart_ids in registration order."""
        return list(self._charts.keys())

    def __contains__(self, chart_id: str) -> bool:
        return chart_id in self._charts

    def __len__(self) -> int:
        return len(self._charts)

    # -- Hot-swap awareness --------------------------------------------------

    def hot_swap_pending(
        self,
        log_path: Optional[Path] = None,
        *,
        threshold: float = HOT_SWAP_THRESHOLD,
    ) -> bool:
        """True when any single canonicalizer's observed fraction is
        >= ``threshold`` (default 70%, per Ergon's descriptor logic).

        Integrates with
        :mod:`prometheus_math.canonicalizer_observability`. Substrate
        v2.3 §6.1: canonicalizer ``variety_fingerprint`` was at 52% on
        seed=42 / 1K eps and approaching the 70% hot-swap threshold;
        this method is the substrate-side check.
        """
        dist = observed_distribution(log_path=log_path)
        return hot_swap_imminent(dist, threshold=threshold)

    def hot_swap_status(
        self,
        log_path: Optional[Path] = None,
        *,
        threshold: float = HOT_SWAP_THRESHOLD,
    ) -> Dict[str, Any]:
        """Detailed hot-swap status for monitoring dashboards.

        Returns
        -------
        dict with keys:
            pending: bool
            distribution: {canonicalizer → fraction}
            dominant: (name, fraction) or None
            threshold: float
        """
        dist = observed_distribution(log_path=log_path)
        return {
            "pending": hot_swap_imminent(dist, threshold=threshold),
            "distribution": dist,
            "dominant": dominant_canonicalizer(dist),
            "threshold": threshold,
        }


# ---------------------------------------------------------------------------
# Module-level singleton + free-function aliases
# ---------------------------------------------------------------------------


DEFAULT_REGISTRY = ChartRegistry()
"""Module-level singleton registry. Charts shipped under
``sigma_kernel.coordinate_charts.*`` register against this at import
time, so downstream code can do
``get_chart("lehmer:deg14:pm5:palindromic")`` without instantiating
its own registry."""


def register_chart(chart: CoordinateChart, *, replace: bool = False) -> None:
    """Register ``chart`` against :data:`DEFAULT_REGISTRY`. Convenience
    alias for ``DEFAULT_REGISTRY.register(chart, replace=replace)``."""
    DEFAULT_REGISTRY.register(chart, replace=replace)


def get_chart(chart_id: str) -> Optional[CoordinateChart]:
    """Look up a chart by ``"<domain>:<region_key>"`` id against
    :data:`DEFAULT_REGISTRY`. Returns None if absent."""
    return DEFAULT_REGISTRY.by_id(chart_id)


def lookup_chart(domain: str, region_key: str) -> Optional[CoordinateChart]:
    """Look up a chart by ``(domain, region_key)`` against
    :data:`DEFAULT_REGISTRY`. Returns None if absent."""
    return DEFAULT_REGISTRY.lookup(domain, region_key)


def all_charts() -> List[CoordinateChart]:
    """Return all charts registered against :data:`DEFAULT_REGISTRY`."""
    return DEFAULT_REGISTRY.all()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


__all__ = [
    # types
    "CanonicalizationProtocol",
    "CoordinateChart",
    "ChartRegistry",
    # enumerations
    "DecidabilityStatus",
    "VALID_DECIDABILITY",
    "REGISTERED_CANONICALIZER_IMPLS",
    # errors
    "ChartRegistrationError",
    "ChartLookupError",
    # singleton + helpers
    "DEFAULT_REGISTRY",
    "register_chart",
    "get_chart",
    "lookup_chart",
    "all_charts",
]
