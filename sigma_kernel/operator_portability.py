"""sigma_kernel.operator_portability — typed encoding of cross-region
operator-signature transports.

Per inbox ticket T-2026-05-07-T030 (P1, Aporia 2026-05-07): the substrate's
first-class encoding of HARD-5's refinement (2026-04-26):

> A "bridge" is just the human-narrative term for "two regions of the
> unified tensor end up close together under some operator." The discovery
> worth promoting is the operator's signature pattern across regions, not
> the bridge story we tell about it.

Without an explicit primitive, the substrate could only assert "operator X
registered against region A" + "operator X registered against region B" as
two separate facts; it could not record the meta-fact "operator X
transports from A to B with evidence Y." That meta-fact IS the substrate's
structural-region-signature finding, and it lives here as a typed object.

Design doc: ``harmonia/memory/architecture/operator_portability_GAP.md``.
"""
from __future__ import annotations

import enum
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TransferMethod(str, enum.Enum):
    """How the operator is transported from source to target chart.

    Per the v2.3 substrate's typed-error discipline (and the
    contract-change window 2026-05-07 ST003+T018 sentinel-hardening): the
    enum is closed; passing an unregistered string raises in the
    consuming function rather than silently falling through.
    """
    DIRECT_APPLICATION = "direct_application"
    EQUIVALENT_OPERATOR = "equivalent_operator"
    STRUCTURAL_LIFT = "structural_lift"
    BOUNDED_FAILURE = "bounded_failure"
    UNKNOWN = "unknown"


class PortabilityVerdict(str, enum.Enum):
    """The substrate's verdict on whether the operator transports."""
    PORTABLE = "portable"
    NOT_PORTABLE = "not_portable"
    INCONCLUSIVE = "inconclusive"
    AWAITING_TRIANGULATION = "awaiting_triangulation"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class PortabilityRegistrationError(RuntimeError):
    """Umbrella error for OperatorPortabilityCertificate registration failures."""


class PortabilityCollisionError(PortabilityRegistrationError):
    """Raised on duplicate certificate id without ``replace=True``.

    Mirrors the CertificateCollisionError pattern from
    sigma_kernel.exclusion_certificate (T-2026-05-07-T020 contract change)."""


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PortabilityEvidence:
    """Operator signature snapshot in one region.

    The substrate's coordinate is the signature_summary content, NOT the
    discipline label. Per HARD-5: discipline metadata lives in the
    ``notes`` field on the parent certificate; this evidence object only
    carries operator-output statistics + sample object_ids for replay.
    """
    n_objects_tested: int
    signature_summary: Mapping[str, Any]
    sample_object_ids: Tuple[str, ...] = ()
    timestamp: float = field(default_factory=lambda: time.time())

    def __post_init__(self) -> None:
        if not isinstance(self.n_objects_tested, int) or self.n_objects_tested < 0:
            raise ValueError(
                f"n_objects_tested must be non-negative int; got "
                f"{self.n_objects_tested!r}"
            )
        if not isinstance(self.signature_summary, Mapping):
            raise TypeError(
                f"signature_summary must be a mapping; got "
                f"{type(self.signature_summary).__name__}"
            )
        if not isinstance(self.sample_object_ids, tuple):
            raise TypeError(
                f"sample_object_ids must be a tuple; got "
                f"{type(self.sample_object_ids).__name__}"
            )


@dataclass(frozen=True)
class PortabilityReplay:
    """Standard substrate replay metadata. Mirrors ExclusionCertificate's
    ReplayInfo structure (no shared base class; the duplication is
    intentional — substrate's typed-replay pattern is not yet abstracted)."""
    code_hash: str
    data_hash: str
    seed: int
    environment_hash: str

    def __post_init__(self) -> None:
        for name in ("code_hash", "data_hash", "environment_hash"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v:
                raise ValueError(f"{name} must be a non-empty string; got {v!r}")
        if not isinstance(self.seed, int):
            raise TypeError(f"seed must be int; got {type(self.seed).__name__}")


# ---------------------------------------------------------------------------
# OperatorPortabilityCertificate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OperatorPortabilityCertificate:
    """A typed certificate that operator ``operator_id`` transports from
    ``source_chart_id`` to ``target_chart_id`` under ``transfer_method``.

    Per HARD-5: the discovery worth promoting is the operator's signature
    pattern across regions, not the human-narrative "bridge" between A and
    B. This certificate IS that signature pattern, made addressable as a
    typed object the substrate's downstream consumers
    (Charon cartography, Ergon Learner, NearMissCorpus) can query.

    Content-addressed identity: ``id`` is sha256 over (operator_id,
    source_chart_id, target_chart_id, transfer_method,
    evidence_pre.signature_summary, evidence_post.signature_summary).
    Re-running the operator with different timing produces the SAME id;
    re-running on different objects (different signature_summary)
    produces a DIFFERENT id.
    """
    operator_id: str
    source_chart_id: str
    target_chart_id: str
    transfer_method: TransferMethod
    evidence_pre: PortabilityEvidence
    evidence_post: PortabilityEvidence
    equivalence_relation: str
    verdict: PortabilityVerdict
    rationale: str
    replay: PortabilityReplay
    notes: str = ""  # per HARD-5: discipline metadata lives here, NOT in coords

    def __post_init__(self) -> None:
        for name in ("operator_id", "source_chart_id", "target_chart_id",
                     "equivalence_relation", "rationale"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v:
                raise ValueError(f"{name} must be a non-empty string; got {v!r}")
        if not isinstance(self.transfer_method, TransferMethod):
            raise TypeError(
                f"transfer_method must be TransferMethod enum; got "
                f"{type(self.transfer_method).__name__}"
            )
        if not isinstance(self.verdict, PortabilityVerdict):
            raise TypeError(
                f"verdict must be PortabilityVerdict enum; got "
                f"{type(self.verdict).__name__}"
            )
        if not isinstance(self.evidence_pre, PortabilityEvidence):
            raise TypeError("evidence_pre must be PortabilityEvidence")
        if not isinstance(self.evidence_post, PortabilityEvidence):
            raise TypeError("evidence_post must be PortabilityEvidence")
        if not isinstance(self.replay, PortabilityReplay):
            raise TypeError("replay must be PortabilityReplay")

    @property
    def certificate_id(self) -> str:
        """Content-addressed sha256 over the substrate-grade identity
        fields (operator_id, source/target chart, transfer_method,
        signature_summaries). Excludes runtime metadata (timestamps,
        sample_object_ids) so re-running with different sample sets
        produces the SAME id when the signature_summary is identical."""
        canonical = json.dumps({
            "operator_id": self.operator_id,
            "source_chart_id": self.source_chart_id,
            "target_chart_id": self.target_chart_id,
            "transfer_method": self.transfer_method.value,
            "signature_pre": dict(self.evidence_pre.signature_summary),
            "signature_post": dict(self.evidence_post.signature_summary),
            "equivalence_relation": self.equivalence_relation,
            "verdict": self.verdict.value,
        }, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class OperatorPortabilityRegistry:
    """In-memory registry of OperatorPortabilityCertificate instances.

    Mirrors the ExclusionCertificate registry pattern. Indexed by
    certificate_id, by operator_id, and by (source, target) chart pair.
    """

    def __init__(self) -> None:
        self._certs: Dict[str, OperatorPortabilityCertificate] = {}
        self._by_operator: Dict[str, List[str]] = {}
        self._by_chart_pair: Dict[Tuple[str, str], List[str]] = {}

    def register(
        self,
        cert: OperatorPortabilityCertificate,
        *,
        replace: bool = False,
    ) -> None:
        """Register a portability certificate.

        Raises
        ------
        PortabilityCollisionError
            On duplicate certificate_id without ``replace=True``.
        TypeError
            If ``cert`` is not an OperatorPortabilityCertificate.
        """
        if not isinstance(cert, OperatorPortabilityCertificate):
            raise TypeError(
                f"register expects OperatorPortabilityCertificate; got "
                f"{type(cert).__name__}"
            )
        cid = cert.certificate_id
        if cid in self._certs and not replace:
            raise PortabilityCollisionError(
                f"portability certificate_id {cid!r} already registered; "
                "pass replace=True (explicit supersede) to override."
            )
        # Scrub old indices on replace
        if cid in self._certs:
            old = self._certs[cid]
            if old.operator_id in self._by_operator:
                self._by_operator[old.operator_id] = [
                    x for x in self._by_operator[old.operator_id] if x != cid
                ]
            pair = (old.source_chart_id, old.target_chart_id)
            if pair in self._by_chart_pair:
                self._by_chart_pair[pair] = [
                    x for x in self._by_chart_pair[pair] if x != cid
                ]
        self._certs[cid] = cert
        self._by_operator.setdefault(cert.operator_id, []).append(cid)
        self._by_chart_pair.setdefault(
            (cert.source_chart_id, cert.target_chart_id), []
        ).append(cid)

    def by_id(self, certificate_id: str) -> Optional[OperatorPortabilityCertificate]:
        """Look up by content-addressed id. Returns None if absent."""
        return self._certs.get(certificate_id)

    def by_operator(self, operator_id: str) -> List[OperatorPortabilityCertificate]:
        """Look up all certificates for a given operator. Returns empty
        list if no certificates registered for this operator. Note: this
        is an explicit-Optional pattern (returns empty list, not raise)
        because the empty case is meaningful — operator hasn't been
        portability-tested yet."""
        ids = self._by_operator.get(operator_id, [])
        return [self._certs[c] for c in ids if c in self._certs]

    def by_chart_pair(
        self, source: str, target: str
    ) -> List[OperatorPortabilityCertificate]:
        """Look up all certificates for a (source, target) chart pair."""
        ids = self._by_chart_pair.get((source, target), [])
        return [self._certs[c] for c in ids if c in self._certs]

    def all(self) -> List[OperatorPortabilityCertificate]:
        return list(self._certs.values())

    def __len__(self) -> int:
        return len(self._certs)

    def __contains__(self, certificate_id: str) -> bool:
        return certificate_id in self._certs


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------


DEFAULT_REGISTRY = OperatorPortabilityRegistry()


def register_portability_certificate(
    cert: OperatorPortabilityCertificate,
    *,
    replace: bool = False,
) -> None:
    """Register against ``DEFAULT_REGISTRY``."""
    DEFAULT_REGISTRY.register(cert, replace=replace)


def get_portability_certificate(
    certificate_id: str,
) -> Optional[OperatorPortabilityCertificate]:
    """Look up by id from ``DEFAULT_REGISTRY``. Returns None if absent."""
    return DEFAULT_REGISTRY.by_id(certificate_id)


def portability_certificates_by_operator(
    operator_id: str,
) -> List[OperatorPortabilityCertificate]:
    """Look up all certificates for an operator from ``DEFAULT_REGISTRY``."""
    return DEFAULT_REGISTRY.by_operator(operator_id)


def portability_certificates_by_chart_pair(
    source: str, target: str
) -> List[OperatorPortabilityCertificate]:
    """Look up all certificates for a chart pair from ``DEFAULT_REGISTRY``."""
    return DEFAULT_REGISTRY.by_chart_pair(source, target)


__all__ = [
    "TransferMethod",
    "PortabilityVerdict",
    "PortabilityEvidence",
    "PortabilityReplay",
    "OperatorPortabilityCertificate",
    "OperatorPortabilityRegistry",
    "PortabilityRegistrationError",
    "PortabilityCollisionError",
    "DEFAULT_REGISTRY",
    "register_portability_certificate",
    "get_portability_certificate",
    "portability_certificates_by_operator",
    "portability_certificates_by_chart_pair",
]
