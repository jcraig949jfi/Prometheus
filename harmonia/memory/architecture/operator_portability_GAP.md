# Operator-Portability Primitive — Design (T-2026-05-07-T030)

**Date:** 2026-05-07 (contract-change window dispatch)
**Ticket:** T-2026-05-07-T030 (P1 — most foundational Tier-3 capability gap)
**Author:** Techne
**Status:** Design landed; minimal impl shipping in this same dispatch (companion impl ticket).

---

## Why this is the most foundational Tier 3 primitive

Per `aporia/doctrine/critical_memories.md` HARD-5 (refinement, 2026-04-26):

> A "bridge" is just the human-narrative term for "two regions of the unified tensor end up close together under some operator." The discovery worth promoting is the operator's signature pattern across regions, not the bridge story we tell about it.

**Operator-portability is the substrate's first-class encoding of that refinement.** Without an explicit primitive, the substrate can only assert "operator X registered against region A" and "operator X registered against region B" as two separate facts; it cannot record the meta-fact "operator X transports from A to B with evidence Y." That meta-fact IS the substrate's structural-region-signature finding, and it's currently inexpressible as a typed object.

Every other Tier 3 capability gap (Maass form, tropical curve, p-adic L-function, Galois cohomology, large-cardinal consistency, motivic period) ultimately needs operator-portability to make its structural claim. T030 is the prerequisite-of-prerequisites.

---

## Proposed primitive

### `OperatorPortabilityCertificate`

A typed dataclass recording the substrate-grade fact that an operator validated in one CoordinateChart region produces analogous (under some equivalence) signatures in another CoordinateChart region. Lives alongside `ExclusionCertificate` in `sigma_kernel/`.

```python
@dataclass(frozen=True)
class OperatorPortabilityCertificate:
    """A substrate-grade certificate that operator ``operator_id``
    transports from region A to region B under a named transfer method.

    Per HARD-5: the discovery worth promoting is the operator's
    signature pattern across regions, NOT the human-narrative "bridge"
    between A and B. This certificate IS that signature pattern, made
    addressable as a typed object.
    """

    operator_id: str                          # e.g. "mahler_measure", "hecke_eigenvalue_at_p"
    source_chart_id: str                      # registered CoordinateChart id where operator validated
    target_chart_id: str                      # registered CoordinateChart id where operator transports to
    transfer_method: TransferMethod           # see enum below

    evidence_pre: PortabilityEvidence         # signature in source chart
    evidence_post: PortabilityEvidence        # signature in target chart
    equivalence_relation: str                 # e.g. "operator_signature_equivalence", "structural_match"

    verdict: PortabilityVerdict               # see enum below
    rationale: str                            # one-paragraph human-readable
    replay: ReplayInfo                        # standard substrate replay metadata


class TransferMethod(str, enum.Enum):
    DIRECT_APPLICATION = "direct_application"      # apply operator literally; works iff signature matches
    EQUIVALENT_OPERATOR = "equivalent_operator"     # different operator with same signature in target
    STRUCTURAL_LIFT = "structural_lift"              # lift via canonicalization-protocol-aware adapter
    BOUNDED_FAILURE = "bounded_failure"              # operator does NOT transport; this is the negative-space fact
    UNKNOWN = "unknown"                              # explicit cannot-classify (per substrate v2.3 §6.3 hard rule)


class PortabilityVerdict(str, enum.Enum):
    PORTABLE = "portable"                              # signature equivalence holds
    NOT_PORTABLE = "not_portable"                      # signatures genuinely diverge (negative-space fact)
    INCONCLUSIVE = "inconclusive"                      # insufficient evidence
    AWAITING_TRIANGULATION = "awaiting_triangulation"  # need ≥1 proof-bearing path per substrate v2.3 §6.3 P6


@dataclass(frozen=True)
class PortabilityEvidence:
    """Operator signature snapshot in one region. Used as a pair
    (evidence_pre, evidence_post) on the certificate to make the
    transfer fact replayable."""
    n_objects_tested: int
    signature_summary: Mapping[str, Any]    # operator-output statistics in this region
    sample_object_ids: Tuple[str, ...]      # representative object ids in the chart
    timestamp: float
```

### CoordinateChart placement

OperatorPortabilityCertificates do NOT sit inside a single chart — they bridge two charts. They live in a substrate-level registry analogous to `CertificateRegistry`:

```python
class OperatorPortabilityRegistry:
    def register(cert: OperatorPortabilityCertificate, *, replace: bool = False) -> None: ...
    def by_id(cert_id: str) -> Optional[OperatorPortabilityCertificate]: ...
    def by_operator(op_id: str) -> List[OperatorPortabilityCertificate]: ...
    def by_chart_pair(source: str, target: str) -> List[OperatorPortabilityCertificate]: ...
```

The certificate's content-addressed `id` is `sha256((operator_id, source_chart_id, target_chart_id, transfer_method, evidence_pre.signature_summary, evidence_post.signature_summary))`.

---

## Worked example — Mahler-measure operator across deg14 and deg12 Lehmer slices

Mahler measure operator `M(p)` is registered against the Lehmer chart `lehmer:deg14:pm5:palindromic` (validated through Day-5 sprint's 97M-poly enumeration). Fire #8 ran the same operator against the new chart `lehmer:deg12:pm5:palindromic` (the W3.2 fixture). The cross-chart fact that the operator "works the same" — produces a band candidate distribution with the same structure (mostly cyclotomic noise + small set near Lehmer-depth) — is currently NOT recorded anywhere.

With `OperatorPortabilityCertificate`:

```python
cert = OperatorPortabilityCertificate(
    operator_id="mahler_measure",
    source_chart_id="lehmer:deg14:pm5:palindromic",
    target_chart_id="lehmer:deg12:pm5:palindromic",  # to be registered when chart lands
    transfer_method=TransferMethod.DIRECT_APPLICATION,
    evidence_pre=PortabilityEvidence(
        n_objects_tested=97_435_855,
        signature_summary={
            "n_band_candidates": 43,
            "n_cyclotomic_noise": 0,  # post-triangulation in Day-5
            "n_lehmer_band_proper": 26,
        },
        sample_object_ids=(),  # filled when chart-aware object_ids land
        timestamp=...,
    ),
    evidence_post=PortabilityEvidence(
        n_objects_tested=8_857_805,
        signature_summary={
            "n_band_candidates": 113,
            "n_cyclotomic_noise": 99,
            "n_lehmer_band_proper": 10,
        },
        sample_object_ids=(),
        timestamp=...,
    ),
    equivalence_relation="operator_signature_equivalence:band_candidate_distribution",
    verdict=PortabilityVerdict.AWAITING_TRIANGULATION,
    rationale=(
        "Mahler measure operator transports from deg14 ±5 palindromic to "
        "deg12 ±5 palindromic with directly-applicable semantics. Both regions "
        "produce a band-candidate distribution dominated by cyclotomic noise + "
        "a small set near Lehmer-depth (~10 polys in deg12; 26 verified in deg14 "
        "post-triangulation). Verdict awaits triangulation of the 10 deg12 "
        "Lehmer-band candidates per Day-5 protocol."
    ),
    replay=ReplayInfo(...),  # standard
)
```

This certificate is the substrate's typed encoding of "Mahler measure transports between sister Lehmer subspaces." Charon / Aporia / future cartography agents query the registry by operator or by chart pair instead of relying on prose summaries.

---

## What this primitive does NOT do

- Implement the actual operator transfer logic (that's per-operator caller-side code; the certificate records the FACT, not the mechanism)
- Verify the equivalence relation automatically (the substrate's TriangulationProtocol is the verification path; this primitive records the verdict-pending state and the verified state)
- Replace `ExclusionCertificate` (different scope: ExclusionCertificate is "this region is empty under operator X"; OperatorPortabilityCertificate is "operator X has signature S in regions A and B")
- Encode discipline labels (per HARD-5: source_chart_id and target_chart_id are operator-derived structural region IDs, not "knot theory" / "L-functions" / etc.)

---

## Migration / coordination implications

- New module: `sigma_kernel/operator_portability.py` (within file ownership)
- New tests: `sigma_kernel/test_operator_portability.py`
- `sigma_kernel.md` updated with the new primitive + registry
- Charon coordination ticket queued — Charon's cartography work generates portability evidence; the typed primitive is the canonical handoff
- Ergon coordination ticket queued — KillEmbedding consumption can include portability certificates as edges in its embedded geometry (region pairs with high portability collapse to nearby embeddings; non-portable region pairs separate)

---

## Cross-references

- `aporia/doctrine/critical_memories.md` HARD-5 (refinement: bridges → operator-signature pattern)
- `pivot/substrate_v2_lockins.md` — control-plane vs data-plane separation (this primitive sits at the data-plane edge of typed cross-region facts)
- `sigma_kernel/exclusion_certificate.py` — sister primitive (negative-space typed fact); same `CertificateRegistry` pattern
- T-2026-05-06-ST002 + T-2026-05-07-T018 + T-2026-05-07-T020 (this dispatch) — error-class discipline patterns this module follows

---

*Design landed; minimal impl in companion file. — Techne, 2026-05-07*
