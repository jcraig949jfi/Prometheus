"""sigma_kernel.exclusion_certificate — P4 Tier 2 primitive for substrate v2.3 §6.3.

Renamed from ExclusionZone (per ChatGPT convergent critique on 2026-05-05):
"zone" implied geometry the substrate doesn't yet have; "certificate" implies
a claim with explicit scope, assumptions, method, and replayability.

What this module provides
-------------------------

* :class:`CertificateType` — five-valued enum naming the *kind* of certificate
  (exhaustive enumeration, theorem-backed reduction, catalog completeness
  under assumptions, probabilistic null, failed search only).
* :class:`CertificateStrength` — five-valued enum naming the *epistemic
  strength* of the certificate. ``COMPLETE`` is the strongest tier and is
  load-bearing: per Aporia's v2.3 tightening, it requires non-empty
  ``triangulation_history`` to construct.
* :class:`RegionSpec`, :class:`ExclusionClaim`, :class:`VerifierSet`,
  :class:`ReplayInfo`, :class:`Boundary`, :class:`TriangulationPathRef` —
  composable value objects forming the certificate body.
* :class:`ExclusionCertificate` — the immutable, content-addressed certificate
  itself. Hard rules:
    1. ``strength == COMPLETE`` requires non-empty ``triangulation_history``
       (raises ValueError otherwise).
    2. Only ``COMPLETE`` and ``BOUNDED_COMPLETE`` certificates feed
       ``EvidenceField.exclusion_distance`` per substrate v2.3 §6.3.
* :class:`CertificateRegistry` + module-level singleton + free-function
  helpers, mirroring the P0 CoordinateChart pattern.

What this module does NOT do
----------------------------

* It does NOT implement TriangulationProtocol (P6 — separate concern).
  ``TriangulationPathRef`` is a structural placeholder / foreign-key into P6.
* It does NOT persist certificates to Postgres. Certificates live in code +
  in-memory registry until the registry shape stabilizes.
* It does NOT validate the ``coordinate_chart_id`` against
  :data:`sigma_kernel.coordinate_chart.DEFAULT_REGISTRY` at certificate
  *construction* time. Certificates are allowed to exist for charts that
  haven't registered yet (e.g. test fixtures, cross-pillar coordination
  windows). Validation happens at *registration* time inside
  :meth:`CertificateRegistry.register`.

Stdlib-only by design (substrate v2.3 §6.3 inherits the no-new-deps rule
from §6.2 P3).
"""
from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple

from sigma_kernel.coordinate_chart import get_chart
from sigma_kernel.method_spec import IndependenceClass, MethodSpec


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class CertificateType(str, enum.Enum):
    """Five-valued kind of exclusion certificate (substrate v2.3 §6.3 P4).

    * ``EXHAUSTIVE_ENUMERATION`` — every object in the region was checked
      (e.g. the Lehmer deg14 ±5 palindromic 97.4M brute force).
    * ``THEOREM_BACKED`` — a theorem reduces the region to a finite or
      already-classified set (e.g. Faltings, Mordell-Weil bounds).
    * ``CATALOG_COMPLETE_UNDER_ASSUMPTIONS`` — a catalog (LMFDB, Mahler,
      OEIS) is treated as complete *under explicit assumptions*. The
      assumptions must be recorded in ``ExclusionClaim.reason``.
    * ``PROBABILISTIC_NULL`` — exclusion is statistical (sampled null at
      level α, not a deterministic claim).
    * ``FAILED_SEARCH_ONLY`` — an unsuccessful search; logged for the
      record but does NOT feed negative-space gradients.
    """

    EXHAUSTIVE_ENUMERATION = "exhaustive_enumeration"
    THEOREM_BACKED = "theorem_backed"
    CATALOG_COMPLETE_UNDER_ASSUMPTIONS = "catalog_complete_under_assumptions"
    PROBABILISTIC_NULL = "probabilistic_null"
    FAILED_SEARCH_ONLY = "failed_search_only"


class CertificateStrength(str, enum.Enum):
    """Five-valued epistemic strength of the certificate (substrate v2.3 §6.3).

    * ``COMPLETE`` — strongest tier. Per Aporia's v2.3 tightening, **requires
      non-empty triangulation_history**. Every COMPLETE certificate must have
      earned its strength via independent triangulation paths; legacy / future
      certificates without such history must use BOUNDED_COMPLETE or weaker.
    * ``BOUNDED_COMPLETE`` — complete within an explicitly stated bound, but
      not triangulated. Allowed without triangulation_history.
    * ``CONDITIONAL`` — conditional on stated assumptions (e.g. "assuming
      GRH" or "assuming the catalog is correct").
    * ``HEURISTIC`` — based on heuristic reasoning, not rigorous methods.
    * ``DIAGNOSTIC_ONLY`` — exists for diagnostic / instrumentation purposes;
      should never be treated as evidentially load-bearing.

    Hard rule (substrate v2.3 §6.3 + Aporia 2026-05-05 feedback):
        Only COMPLETE and BOUNDED_COMPLETE certificates feed the
        ``negative_space`` gradient axis on EvidenceField. See
        :meth:`ExclusionCertificate.feeds_negative_space_axis`.
    """

    COMPLETE = "complete"
    BOUNDED_COMPLETE = "bounded_complete"
    CONDITIONAL = "conditional"
    HEURISTIC = "heuristic"
    DIAGNOSTIC_ONLY = "diagnostic_only"


# Set of strengths that feed the negative_space gradient axis (substrate
# v2.3 §6.3 hard rule). Exposed as a module-level constant so callers can
# audit / extend it without mutating the enum.
NEGATIVE_SPACE_FEEDING_STRENGTHS = frozenset({
    CertificateStrength.COMPLETE,
    CertificateStrength.BOUNDED_COMPLETE,
})


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TriangulationPathRef:
    """Foreign-key reference to a TriangulationProtocol path (P6).

    P6 is in flight; this is the structural placeholder. When P6 lands, a
    ``TriangulationPath`` will be the canonical record and this dataclass
    will hold the joinable id / summary tuple.

    Fields
    ------
    path_id
        Stable identifier for the triangulation path (e.g.
        ``"path_a_high_precision_mpmath_dps60"``).
    method_spec
        The :class:`MethodSpec` used by this path. Carries the
        ``independence_class`` that lets the certificate's verifier set
        auto-derive its independence classes.
    verdict
        One of ``"verified"``, ``"contradicted"``, ``"inconclusive"``.
    timestamp
        Unix epoch seconds when the path was executed.
    summary
        One-line human-readable description.
    """

    path_id: str
    method_spec: MethodSpec
    verdict: str
    timestamp: float
    summary: str

    _VALID_VERDICTS = ("verified", "contradicted", "inconclusive")

    def __post_init__(self) -> None:
        if not isinstance(self.path_id, str) or not self.path_id:
            raise ValueError(f"path_id must be a non-empty string; got {self.path_id!r}")
        if not isinstance(self.method_spec, MethodSpec):
            raise TypeError(
                f"method_spec must be a MethodSpec; got {type(self.method_spec).__name__}"
            )
        if self.verdict not in self._VALID_VERDICTS:
            raise ValueError(
                f"verdict must be one of {self._VALID_VERDICTS}; got {self.verdict!r}"
            )
        if not isinstance(self.summary, str):
            raise TypeError(f"summary must be a string; got {type(self.summary).__name__}")


@dataclass(frozen=True)
class RegionSpec:
    """The region the certificate covers.

    The ``coordinate_chart_id`` MUST eventually reference a registered
    CoordinateChart (validated at registry-time, not construction-time —
    see module docstring for rationale).
    """

    coordinate_chart_id: str
    constraints: Mapping[str, Any] = field(default_factory=dict)
    bounds: Optional[Mapping[str, Any]] = None
    normalization: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.coordinate_chart_id, str) or not self.coordinate_chart_id:
            raise ValueError(
                "coordinate_chart_id must be a non-empty string; "
                f"got {self.coordinate_chart_id!r}"
            )


@dataclass(frozen=True)
class ExclusionClaim:
    """The claim being certified."""

    excluded_property: str
    result_class: str
    reason: str

    def __post_init__(self) -> None:
        for name in ("excluded_property", "result_class", "reason"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v:
                raise ValueError(f"{name} must be a non-empty string; got {v!r}")


@dataclass(frozen=True)
class VerifierSet:
    """The set of MethodSpecs that verified the exclusion.

    If ``independence_classes`` is empty (or omitted) at construction time,
    it is auto-derived from the methods' ``independence_class`` fields. This
    means the canonical / recommended construction is::

        VerifierSet(methods=(spec_a, spec_b, spec_c))  # classes auto-derived

    Callers who need to override (e.g. to suppress a misclassified entry
    or to reflect a class registered out-of-band) may pass an explicit
    ``independence_classes`` frozenset.
    """

    methods: Tuple[MethodSpec, ...]
    independence_classes: frozenset = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not isinstance(self.methods, tuple):
            raise TypeError(
                f"methods must be a tuple of MethodSpec; got {type(self.methods).__name__}"
            )
        for m in self.methods:
            if not isinstance(m, MethodSpec):
                raise TypeError(
                    f"every method must be a MethodSpec; got {type(m).__name__}"
                )
        # Auto-derive independence_classes from methods if not supplied.
        if not self.independence_classes:
            derived = frozenset(m.independence_class for m in self.methods)
            # __setattr__ on frozen dataclass: bypass via object.__setattr__.
            object.__setattr__(self, "independence_classes", derived)
        else:
            if not isinstance(self.independence_classes, frozenset):
                # Coerce common iterable inputs (set, tuple, list) into frozenset.
                object.__setattr__(
                    self,
                    "independence_classes",
                    frozenset(self.independence_classes),
                )


@dataclass(frozen=True)
class ReplayInfo:
    """Hashes that make the certificate replayable.

    ``code_hash``, ``data_hash``, ``environment_hash`` are sha256 hex
    digests (best-effort; the substrate does not enforce reproducibility,
    it merely records the fingerprint). ``seed`` is an integer; 0 is a
    valid value.
    """

    code_hash: str
    data_hash: str
    seed: int
    environment_hash: str

    def __post_init__(self) -> None:
        for name in ("code_hash", "data_hash", "environment_hash"):
            v = getattr(self, name)
            if not isinstance(v, str):
                raise TypeError(f"{name} must be a string; got {type(v).__name__}")
        if not isinstance(self.seed, int):
            raise TypeError(f"seed must be an int; got {type(self.seed).__name__}")


@dataclass(frozen=True)
class Boundary:
    """The certificate's edge — adjacent regions and known escape hatches.

    Deliberately permissive: ``adjacent_regions`` is a tuple of
    ``coordinate_chart_id`` strings (each *should* point at a registered
    chart, but isn't validated here — boundaries can refer to charts that
    haven't been registered yet).
    """

    adjacent_regions: Tuple[str, ...] = ()
    known_escape_hatches: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.adjacent_regions, tuple):
            raise TypeError("adjacent_regions must be a tuple of strings")
        if not isinstance(self.known_escape_hatches, tuple):
            raise TypeError("known_escape_hatches must be a tuple of strings")


# ---------------------------------------------------------------------------
# ExclusionCertificate
# ---------------------------------------------------------------------------


def _stable_repr(obj: Any) -> Any:
    """Return a JSON-friendly representation suitable for stable hashing.

    Frozen dataclasses → dicts of their fields; mappings → sorted-key
    dicts; tuples/lists/sets → lists; enums → their value; everything else
    → ``repr(...)`` (best-effort; collisions are acceptable for the hash
    domain here because content-addressing is for cache-key purposes, not
    cryptographic uniqueness).
    """
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, enum.Enum):
        return obj.value
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _stable_repr(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, Mapping):
        return {str(k): _stable_repr(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, (list, tuple)):
        return [_stable_repr(x) for x in obj]
    if isinstance(obj, (set, frozenset)):
        return sorted(_stable_repr(x) for x in obj)
    return repr(obj)


@dataclass(frozen=True)
class ExclusionCertificate:
    """Per substrate v2.3 §6.3 P4 + v2.3 Aporia tightening.

    Construction rules
    ------------------
    1. ``strength == CertificateStrength.COMPLETE`` requires
       ``triangulation_history`` to be non-empty. Violating this raises
       ``ValueError`` — this is the load-bearing v2.3 Aporia tightening
       and MUST NOT be relaxed.
    2. ``coordinate_chart_id`` is NOT validated at construction time — see
       module docstring rationale (validation occurs at registry time).
    3. The certificate is content-addressed: :attr:`certificate_id` is a
       sha256 over ``(region_spec, exclusion_claim, certificate_type,
       strength)``. Two certificates with the same content yield the same
       id, but differ in any of those four fields → different id.

    Negative-space gradient feed
    ----------------------------
    Per substrate v2.3 §6.3, only ``COMPLETE`` and ``BOUNDED_COMPLETE``
    certificates feed ``EvidenceField.exclusion_distance``. Use
    :meth:`feeds_negative_space_axis` to gate this in downstream consumers.
    """

    region_spec: RegionSpec
    exclusion_claim: ExclusionClaim
    certificate_type: CertificateType
    strength: CertificateStrength
    verifier_set: VerifierSet
    replay: ReplayInfo
    triangulation_history: Tuple[TriangulationPathRef, ...] = ()
    initial_verdict: Optional[str] = None
    upgrade_path_summary: Tuple[str, ...] = ()
    boundary: Boundary = field(default_factory=Boundary)

    def __post_init__(self) -> None:
        # Type-of-field sanity.
        if not isinstance(self.region_spec, RegionSpec):
            raise TypeError(
                f"region_spec must be a RegionSpec; got {type(self.region_spec).__name__}"
            )
        if not isinstance(self.exclusion_claim, ExclusionClaim):
            raise TypeError(
                f"exclusion_claim must be an ExclusionClaim; got {type(self.exclusion_claim).__name__}"
            )
        if not isinstance(self.certificate_type, CertificateType):
            raise TypeError(
                f"certificate_type must be a CertificateType; got {type(self.certificate_type).__name__}"
            )
        if not isinstance(self.strength, CertificateStrength):
            raise TypeError(
                f"strength must be a CertificateStrength; got {type(self.strength).__name__}"
            )
        if not isinstance(self.verifier_set, VerifierSet):
            raise TypeError(
                f"verifier_set must be a VerifierSet; got {type(self.verifier_set).__name__}"
            )
        if not isinstance(self.replay, ReplayInfo):
            raise TypeError(
                f"replay must be a ReplayInfo; got {type(self.replay).__name__}"
            )
        if not isinstance(self.triangulation_history, tuple):
            raise TypeError(
                "triangulation_history must be a tuple of TriangulationPathRef"
            )
        for ref in self.triangulation_history:
            if not isinstance(ref, TriangulationPathRef):
                raise TypeError(
                    "every triangulation_history entry must be a TriangulationPathRef; "
                    f"got {type(ref).__name__}"
                )
        if not isinstance(self.upgrade_path_summary, tuple):
            raise TypeError("upgrade_path_summary must be a tuple of strings")
        if not isinstance(self.boundary, Boundary):
            raise TypeError(
                f"boundary must be a Boundary; got {type(self.boundary).__name__}"
            )

        # Hard rule per Aporia v2.3: strength=complete requires non-empty
        # triangulation_history. This is the load-bearing v2.3 tightening.
        if self.strength == CertificateStrength.COMPLETE and not self.triangulation_history:
            raise ValueError(
                "ExclusionCertificate.strength=complete requires non-empty "
                "triangulation_history. Future certificates without earned "
                "triangulation must use bounded_complete or weaker. Per "
                "substrate v2.3 §6.3 + Aporia 2026-05-05 feedback."
            )

    # ------------------------------------------------------------------
    # Identity / introspection
    # ------------------------------------------------------------------

    @property
    def certificate_id(self) -> str:
        """Content-addressed sha256 over the load-bearing claim fields.

        Hashes the canonical-JSON-ish stable repr of:
            (region_spec, exclusion_claim, certificate_type, strength)

        Why these four: they are the *load-bearing claim* — what was
        excluded, where, of what type, with what strength. Two certificates
        agreeing on these four make the same epistemic statement; two
        differing on any of them make different statements. Verifier set,
        replay info, and triangulation history may evolve while the claim
        stays the same; we deliberately exclude them from the id so that
        e.g. re-running the verifiers with refreshed code doesn't change
        the certificate's identity.
        """
        payload = {
            "region_spec": _stable_repr(self.region_spec),
            "exclusion_claim": _stable_repr(self.exclusion_claim),
            "certificate_type": self.certificate_type.value,
            "strength": self.strength.value,
        }
        blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def feeds_negative_space_axis(self) -> bool:
        """Per substrate v2.3 §6.3 hard rule: only COMPLETE and
        BOUNDED_COMPLETE certificates feed the ``negative_space`` gradient
        axis. HEURISTIC / FAILED_SEARCH_ONLY / DIAGNOSTIC_ONLY certificates
        are logged but do not generate gradients."""
        return self.strength in NEGATIVE_SPACE_FEEDING_STRENGTHS


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class CertificateRegistrationError(RuntimeError):
    """Umbrella error for ExclusionCertificate registration failures. Raised
    on duplicate certificate_id registration without ``replace=True``, or
    when a certificate's ``coordinate_chart_id`` does not resolve at
    registration time. See subclasses for finer-grained dispatch."""


class CertificateCollisionError(CertificateRegistrationError):
    """Raised specifically on duplicate ``certificate_id`` registration
    without ``replace=True`` (the substrate's "explicit-supersede" flag).

    Per the 2026-05-07 contract-change window (T-2026-05-07-T020):
    callers can now narrowly catch the collision case (vs. the broader
    "missing chart" case) by catching this subclass. Existing callers
    catching :class:`CertificateRegistrationError` continue to work
    unchanged — collision still IS a registration error."""


class CertificateRegistry:
    """In-memory registry of :class:`ExclusionCertificate` instances.

    Mirrors the P0 ChartRegistry pattern: register at import time, look up
    by id or by coordinate_chart_id. Validates ``coordinate_chart_id``
    against :data:`sigma_kernel.coordinate_chart.DEFAULT_REGISTRY` at
    registration time (not construction time).
    """

    def __init__(self) -> None:
        # Insertion-ordered for deterministic iteration.
        self._certs: Dict[str, ExclusionCertificate] = {}
        # Secondary index: chart_id → list[certificate_id] for fast by_chart.
        self._by_chart: Dict[str, List[str]] = {}

    # -- Mutation -----------------------------------------------------------

    def register(
        self,
        cert: ExclusionCertificate,
        *,
        replace: bool = False,
        require_chart: bool = True,
    ) -> None:
        """Register a certificate.

        Validates ``cert.region_spec.coordinate_chart_id`` against the chart
        registry by default. Pass ``require_chart=False`` to skip (intended
        for tests / cross-pillar coordination windows where the chart hasn't
        landed yet — but doing so silently weakens the substrate's "no
        exclusion-distance without registered chart" rule, so use sparingly).

        Raises
        ------
        CertificateRegistrationError
            On duplicate id without ``replace=True``, or on missing chart
            when ``require_chart=True``.
        TypeError
            If ``cert`` is not an :class:`ExclusionCertificate`.
        """
        if not isinstance(cert, ExclusionCertificate):
            raise TypeError(
                f"register expects ExclusionCertificate; got {type(cert).__name__}"
            )

        if require_chart:
            chart_id = cert.region_spec.coordinate_chart_id
            if get_chart(chart_id) is None:
                raise CertificateRegistrationError(
                    f"coordinate_chart_id {chart_id!r} is not registered against "
                    "DEFAULT_REGISTRY (sigma_kernel.coordinate_chart). Register "
                    "the chart first, or pass require_chart=False to skip "
                    "validation (not recommended for production substrate)."
                )

        cid = cert.certificate_id
        if cid in self._certs and not replace:
            raise CertificateCollisionError(
                f"certificate_id {cid!r} already registered; pass replace=True "
                "(explicit supersede) to override. Catching "
                "CertificateRegistrationError continues to work since "
                "CertificateCollisionError is a subclass."
            )

        # If we're replacing, scrub the old chart-index entry first.
        if cid in self._certs:
            old_chart = self._certs[cid].region_spec.coordinate_chart_id
            if old_chart in self._by_chart and cid in self._by_chart[old_chart]:
                self._by_chart[old_chart].remove(cid)

        self._certs[cid] = cert
        self._by_chart.setdefault(cert.region_spec.coordinate_chart_id, []).append(cid)

    def unregister(self, certificate_id: str) -> Optional[ExclusionCertificate]:
        """Remove a certificate by id; returns the removed certificate or None."""
        cert = self._certs.pop(certificate_id, None)
        if cert is not None:
            chart = cert.region_spec.coordinate_chart_id
            if chart in self._by_chart and certificate_id in self._by_chart[chart]:
                self._by_chart[chart].remove(certificate_id)
        return cert

    def clear(self) -> None:
        """Drop all registered certificates. Intended for tests."""
        self._certs.clear()
        self._by_chart.clear()

    # -- Lookup -------------------------------------------------------------

    def by_id(self, certificate_id: str) -> Optional[ExclusionCertificate]:
        """Look up a certificate by its content-addressed id. Returns None if absent."""
        return self._certs.get(certificate_id)

    def by_chart(self, coordinate_chart_id: str) -> List[ExclusionCertificate]:
        """Return all certificates registered against the given chart_id,
        in registration order. Empty list if none."""
        ids = self._by_chart.get(coordinate_chart_id, [])
        return [self._certs[i] for i in ids if i in self._certs]

    def all(self) -> List[ExclusionCertificate]:
        """Return all registered certificates in registration order."""
        return list(self._certs.values())

    def ids(self) -> List[str]:
        """Return all registered certificate_ids in registration order."""
        return list(self._certs.keys())

    def __contains__(self, certificate_id: str) -> bool:
        return certificate_id in self._certs

    def __len__(self) -> int:
        return len(self._certs)


# ---------------------------------------------------------------------------
# Module-level singleton + free-function aliases
# ---------------------------------------------------------------------------


DEFAULT_REGISTRY = CertificateRegistry()
"""Module-level singleton registry. Certificates shipped under
``sigma_kernel.exclusion_certificates.*`` register against this at import
time, so downstream code can do
``get_certificate(<sha>)`` / ``certificates_for_chart(<chart_id>)``
without instantiating its own registry."""


def register_certificate(
    cert: ExclusionCertificate,
    *,
    replace: bool = False,
    require_chart: bool = True,
) -> None:
    """Register ``cert`` against :data:`DEFAULT_REGISTRY`. Convenience alias."""
    DEFAULT_REGISTRY.register(cert, replace=replace, require_chart=require_chart)


def get_certificate(certificate_id: str) -> Optional[ExclusionCertificate]:
    """Look up a certificate by id against :data:`DEFAULT_REGISTRY`. Returns
    None if absent."""
    return DEFAULT_REGISTRY.by_id(certificate_id)


def certificates_for_chart(chart_id: str) -> List[ExclusionCertificate]:
    """Return all certificates registered against ``chart_id`` in
    :data:`DEFAULT_REGISTRY`."""
    return DEFAULT_REGISTRY.by_chart(chart_id)


def all_certificates() -> List[ExclusionCertificate]:
    """Return all certificates in :data:`DEFAULT_REGISTRY` in registration order."""
    return DEFAULT_REGISTRY.all()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


__all__ = [
    # enumerations
    "CertificateType",
    "CertificateStrength",
    "NEGATIVE_SPACE_FEEDING_STRENGTHS",
    # value objects
    "TriangulationPathRef",
    "RegionSpec",
    "ExclusionClaim",
    "VerifierSet",
    "ReplayInfo",
    "Boundary",
    # certificate
    "ExclusionCertificate",
    # registry
    "CertificateRegistry",
    "CertificateRegistrationError",
    "CertificateCollisionError",
    "DEFAULT_REGISTRY",
    # free-function aliases
    "register_certificate",
    "get_certificate",
    "certificates_for_chart",
    "all_certificates",
]
