"""Tests for sigma_kernel.exclusion_certificate — P4 Tier 2 primitive.

Substrate v2.3 §6.3 + Aporia v2.3 tightening (triangulation_history).
Joint sprint commitment T10. See
``pivot/techne_ergon_joint_sprint_2026-05-05.md``.

Coverage targets:
    * Enum membership invariants
    * ExclusionCertificate construction (full + minimal valid)
    * Hard rule: strength=COMPLETE without triangulation_history -> ValueError
    * Hard rule: strength=COMPLETE WITH triangulation_history -> succeeds
    * BOUNDED_COMPLETE / HEURISTIC / CONDITIONAL succeed without history
    * certificate_id is content-addressed (deterministic + content-sensitive)
    * feeds_negative_space_axis returns True only for COMPLETE / BOUNDED_COMPLETE
    * CertificateRegistry register / lookup / by_chart / round-trip
    * Lehmer prototype registers at import time + lookup-able by chart_id
    * VerifierSet auto-derives independence_classes from MethodSpec
    * TriangulationPathRef construction + verdict validation
"""
from __future__ import annotations

import hashlib

import pytest

from sigma_kernel.coordinate_chart import (
    DEFAULT_REGISTRY as CHART_REGISTRY,
)
# Importing this submodule registers the Lehmer chart at import time, which
# is a prerequisite for any certificate that references chart_id
# "lehmer:deg14:pm5:palindromic".
from sigma_kernel.coordinate_charts.lehmer import (  # noqa: F401
    LEHMER_DEG14_PM5_PALINDROMIC,
)
from sigma_kernel.exclusion_certificate import (
    DEFAULT_REGISTRY,
    NEGATIVE_SPACE_FEEDING_STRENGTHS,
    Boundary,
    CertificateRegistrationError,
    CertificateRegistry,
    CertificateStrength,
    CertificateType,
    ExclusionCertificate,
    ExclusionClaim,
    RegionSpec,
    ReplayInfo,
    TriangulationPathRef,
    VerifierSet,
    certificates_for_chart,
    get_certificate,
    register_certificate,
)
# Importing this submodule registers the Lehmer prototype certificate.
from sigma_kernel.exclusion_certificates.lehmer_deg14 import (  # noqa: F401
    LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION,
)
from sigma_kernel.method_spec import IndependenceClass, MethodSpec


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _placeholder_replay() -> ReplayInfo:
    return ReplayInfo(
        code_hash=hashlib.sha256(b"code").hexdigest(),
        data_hash=hashlib.sha256(b"data").hexdigest(),
        seed=42,
        environment_hash=hashlib.sha256(b"env").hexdigest(),
    )


def _basic_region_spec(chart_id: str = "lehmer:deg14:pm5:palindromic") -> RegionSpec:
    return RegionSpec(
        coordinate_chart_id=chart_id,
        constraints={"degree": 14},
        bounds={"n": 100},
    )


def _basic_claim(label: str = "novel band hit") -> ExclusionClaim:
    return ExclusionClaim(
        excluded_property=label,
        result_class="test_exclusion",
        reason="for unit test fixture",
    )


def _spec(name: str, cls: IndependenceClass) -> MethodSpec:
    return MethodSpec(engine="test", strategy=name, independence_class=cls)


def _path_ref(name: str, cls: IndependenceClass) -> TriangulationPathRef:
    return TriangulationPathRef(
        path_id=f"path_{name}",
        method_spec=_spec(name, cls),
        verdict="verified",
        timestamp=0.0,
        summary=f"Test path {name}",
    )


# ---------------------------------------------------------------------------
# Enum invariants
# ---------------------------------------------------------------------------


def test_certificate_type_has_five_canonical_values():
    expected = {
        "exhaustive_enumeration",
        "theorem_backed",
        "catalog_complete_under_assumptions",
        "probabilistic_null",
        "failed_search_only",
    }
    assert {ct.value for ct in CertificateType} == expected
    assert len(CertificateType) == 5


def test_certificate_strength_has_five_canonical_values():
    expected = {
        "complete",
        "bounded_complete",
        "conditional",
        "heuristic",
        "diagnostic_only",
    }
    assert {cs.value for cs in CertificateStrength} == expected
    assert len(CertificateStrength) == 5


def test_negative_space_feeding_strengths_set():
    # Only COMPLETE and BOUNDED_COMPLETE per substrate v2.3 §6.3 hard rule.
    assert NEGATIVE_SPACE_FEEDING_STRENGTHS == frozenset({
        CertificateStrength.COMPLETE,
        CertificateStrength.BOUNDED_COMPLETE,
    })


# ---------------------------------------------------------------------------
# Construction — full path
# ---------------------------------------------------------------------------


def test_construct_full_certificate_with_all_fields():
    """Full certificate construction with every field populated."""
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.COMPLETE,
        verifier_set=VerifierSet(
            methods=(
                _spec("a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
                _spec("b", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
            ),
        ),
        replay=_placeholder_replay(),
        triangulation_history=(
            _path_ref("a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
            _path_ref("b", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
        ),
        initial_verdict="INCONCLUSIVE pre-triangulation",
        upgrade_path_summary=("Path A verified", "Path B verified"),
        boundary=Boundary(
            adjacent_regions=("lehmer:deg12:pm5:palindromic",),
            known_escape_hatches=("non-palindromic skipped",),
        ),
    )
    assert cert.strength == CertificateStrength.COMPLETE
    assert len(cert.triangulation_history) == 2
    assert cert.boundary.adjacent_regions == ("lehmer:deg12:pm5:palindromic",)


# ---------------------------------------------------------------------------
# Hard rule: COMPLETE requires triangulation_history
# ---------------------------------------------------------------------------


def test_strength_complete_without_triangulation_raises():
    """v2.3 Aporia tightening: strength=COMPLETE + empty history -> ValueError."""
    with pytest.raises(ValueError, match="triangulation_history"):
        ExclusionCertificate(
            region_spec=_basic_region_spec(),
            exclusion_claim=_basic_claim(),
            certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
            strength=CertificateStrength.COMPLETE,
            verifier_set=VerifierSet(methods=()),
            replay=_placeholder_replay(),
            triangulation_history=(),  # empty -> must raise
        )


def test_strength_complete_with_triangulation_succeeds():
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
        triangulation_history=(
            _path_ref("a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        ),
    )
    assert cert.strength == CertificateStrength.COMPLETE
    assert len(cert.triangulation_history) == 1


def test_strength_bounded_complete_without_triangulation_succeeds():
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
        triangulation_history=(),
    )
    assert cert.strength == CertificateStrength.BOUNDED_COMPLETE
    assert cert.triangulation_history == ()


def test_strength_heuristic_without_triangulation_succeeds():
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.FAILED_SEARCH_ONLY,
        strength=CertificateStrength.HEURISTIC,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    assert cert.strength == CertificateStrength.HEURISTIC


def test_strength_conditional_without_triangulation_succeeds():
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.THEOREM_BACKED,
        strength=CertificateStrength.CONDITIONAL,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    assert cert.strength == CertificateStrength.CONDITIONAL


def test_strength_diagnostic_only_without_triangulation_succeeds():
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.PROBABILISTIC_NULL,
        strength=CertificateStrength.DIAGNOSTIC_ONLY,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    assert cert.strength == CertificateStrength.DIAGNOSTIC_ONLY


# ---------------------------------------------------------------------------
# certificate_id content-addressing
# ---------------------------------------------------------------------------


def test_certificate_id_is_deterministic():
    """Same content -> same id across reconstructions."""
    args = dict(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    cert_a = ExclusionCertificate(**args)
    cert_b = ExclusionCertificate(**args)
    assert cert_a.certificate_id == cert_b.certificate_id
    # Sha256 hex digest length sanity.
    assert len(cert_a.certificate_id) == 64


def test_certificate_id_changes_with_strength():
    """Different strength -> different id (id depends on strength)."""
    base_kwargs = dict(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    cert_bounded = ExclusionCertificate(
        strength=CertificateStrength.BOUNDED_COMPLETE,
        **base_kwargs,
    )
    cert_heuristic = ExclusionCertificate(
        strength=CertificateStrength.HEURISTIC,
        **base_kwargs,
    )
    assert cert_bounded.certificate_id != cert_heuristic.certificate_id


def test_certificate_id_changes_with_claim():
    """Different exclusion claim -> different id."""
    base = dict(
        region_spec=_basic_region_spec(),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    a = ExclusionCertificate(exclusion_claim=_basic_claim("first claim"), **base)
    b = ExclusionCertificate(exclusion_claim=_basic_claim("second claim"), **base)
    assert a.certificate_id != b.certificate_id


def test_certificate_id_is_replay_invariant():
    """Different replay info -> SAME id (id is over claim only, not replay)."""
    common = dict(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=()),
    )
    a = ExclusionCertificate(
        replay=ReplayInfo(code_hash="a" * 64, data_hash="a" * 64, seed=0, environment_hash="a" * 64),
        **common,
    )
    b = ExclusionCertificate(
        replay=ReplayInfo(code_hash="b" * 64, data_hash="b" * 64, seed=99, environment_hash="b" * 64),
        **common,
    )
    assert a.certificate_id == b.certificate_id


# ---------------------------------------------------------------------------
# feeds_negative_space_axis
# ---------------------------------------------------------------------------


def test_feeds_negative_space_axis_for_complete():
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
        triangulation_history=(
            _path_ref("a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        ),
    )
    assert cert.feeds_negative_space_axis() is True


def test_feeds_negative_space_axis_for_bounded_complete():
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    assert cert.feeds_negative_space_axis() is True


@pytest.mark.parametrize(
    "strength",
    [
        CertificateStrength.CONDITIONAL,
        CertificateStrength.HEURISTIC,
        CertificateStrength.DIAGNOSTIC_ONLY,
    ],
)
def test_feeds_negative_space_axis_false_for_weaker(strength):
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim(),
        certificate_type=CertificateType.FAILED_SEARCH_ONLY,
        strength=strength,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    assert cert.feeds_negative_space_axis() is False


# ---------------------------------------------------------------------------
# VerifierSet auto-derivation
# ---------------------------------------------------------------------------


def test_verifier_set_auto_derives_independence_classes():
    vs = VerifierSet(
        methods=(
            _spec("a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
            _spec("b", IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
            _spec("c", IndependenceClass.MAHLER_LOOKUP_CATALOG),
        ),
    )
    assert vs.independence_classes == frozenset({
        IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
        IndependenceClass.MAHLER_LOOKUP_CATALOG,
    })


def test_verifier_set_explicit_classes_preserved():
    """If caller provides independence_classes explicitly, preserve them."""
    explicit = frozenset({IndependenceClass.UNKNOWN})
    vs = VerifierSet(
        methods=(_spec("a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),),
        independence_classes=explicit,
    )
    assert vs.independence_classes == explicit


# ---------------------------------------------------------------------------
# TriangulationPathRef
# ---------------------------------------------------------------------------


def test_triangulation_path_ref_construction():
    ref = TriangulationPathRef(
        path_id="path_a",
        method_spec=_spec("a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
        verdict="verified",
        timestamp=12345.0,
        summary="Test path A",
    )
    assert ref.path_id == "path_a"
    assert ref.verdict == "verified"


def test_triangulation_path_ref_invalid_verdict_raises():
    with pytest.raises(ValueError, match="verdict"):
        TriangulationPathRef(
            path_id="path_a",
            method_spec=_spec("a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
            verdict="bogus",
            timestamp=0.0,
            summary="bad",
        )


def test_triangulation_path_ref_empty_path_id_raises():
    with pytest.raises(ValueError, match="path_id"):
        TriangulationPathRef(
            path_id="",
            method_spec=_spec("a", IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION),
            verdict="verified",
            timestamp=0.0,
            summary="bad",
        )


# ---------------------------------------------------------------------------
# CertificateRegistry round-trip
# ---------------------------------------------------------------------------


def test_certificate_registry_register_and_lookup():
    reg = CertificateRegistry()
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim("registry roundtrip"),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    # require_chart=False because we're using a private registry that doesn't
    # share the chart registry's state path. (The chart IS registered in
    # DEFAULT chart registry, so this would also pass with require_chart=True;
    # but we explicitly test the bypass here.)
    reg.register(cert, require_chart=False)
    assert cert.certificate_id in reg
    assert reg.by_id(cert.certificate_id) is cert
    assert len(reg) == 1


def test_certificate_registry_by_chart_filter():
    reg = CertificateRegistry()
    cert_a = ExclusionCertificate(
        region_spec=_basic_region_spec("lehmer:deg14:pm5:palindromic"),
        exclusion_claim=_basic_claim("chart-a claim"),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    cert_b = ExclusionCertificate(
        region_spec=_basic_region_spec("other:region:key"),
        exclusion_claim=_basic_claim("chart-b claim"),
        certificate_type=CertificateType.FAILED_SEARCH_ONLY,
        strength=CertificateStrength.HEURISTIC,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    reg.register(cert_a, require_chart=False)
    reg.register(cert_b, require_chart=False)
    a_only = reg.by_chart("lehmer:deg14:pm5:palindromic")
    b_only = reg.by_chart("other:region:key")
    assert a_only == [cert_a]
    assert b_only == [cert_b]


def test_certificate_registry_duplicate_raises_without_replace():
    reg = CertificateRegistry()
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec(),
        exclusion_claim=_basic_claim("dup"),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    reg.register(cert, require_chart=False)
    with pytest.raises(CertificateRegistrationError, match="already registered"):
        reg.register(cert, require_chart=False)


def test_certificate_registry_validates_chart_id_at_registration():
    """require_chart=True (default) rejects unregistered chart_ids."""
    reg = CertificateRegistry()
    cert = ExclusionCertificate(
        region_spec=_basic_region_spec("nonexistent:chart:id"),
        exclusion_claim=_basic_claim("missing-chart"),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=CertificateStrength.BOUNDED_COMPLETE,
        verifier_set=VerifierSet(methods=()),
        replay=_placeholder_replay(),
    )
    with pytest.raises(CertificateRegistrationError, match="not registered"):
        reg.register(cert, require_chart=True)


# ---------------------------------------------------------------------------
# Lehmer prototype certificate
# ---------------------------------------------------------------------------


def test_lehmer_prototype_registered_at_import():
    """The Lehmer deg14 ±5 palindromic certificate must auto-register."""
    cert = LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION
    assert cert.certificate_id in DEFAULT_REGISTRY
    fetched = get_certificate(cert.certificate_id)
    assert fetched is cert


def test_lehmer_prototype_lookup_by_chart():
    certs = certificates_for_chart("lehmer:deg14:pm5:palindromic")
    # Must contain the Lehmer prototype (other tests may also register against
    # this chart; assert membership rather than equality).
    assert LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION in certs


def test_lehmer_prototype_has_complete_strength_with_triangulation():
    cert = LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION
    assert cert.strength == CertificateStrength.COMPLETE
    assert len(cert.triangulation_history) == 4
    # All four paths verified.
    assert all(p.verdict == "verified" for p in cert.triangulation_history)


def test_lehmer_prototype_feeds_negative_space():
    assert LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION.feeds_negative_space_axis() is True


def test_lehmer_prototype_independence_classes_diverse():
    """The four Lehmer paths must have four distinct IndependenceClasses."""
    cert = LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION
    classes = cert.verifier_set.independence_classes
    # Auto-derived from the four MethodSpecs; each path uses a distinct class.
    assert len(classes) == 4
    assert IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION in classes
    assert IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION in classes
    assert IndependenceClass.MAHLER_LOOKUP_CATALOG in classes
    assert IndependenceClass.LITERATURE_CROSS_CHECK in classes


def test_lehmer_prototype_chart_id_resolves():
    """The Lehmer prototype's coordinate_chart_id must resolve in the chart registry."""
    chart_id = LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION.region_spec.coordinate_chart_id
    assert chart_id == "lehmer:deg14:pm5:palindromic"
    assert CHART_REGISTRY.by_id(chart_id) is not None
