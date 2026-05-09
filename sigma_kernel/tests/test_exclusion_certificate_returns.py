"""Return-value coverage for sigma_kernel.exclusion_certificate methods.

Closes ST-fire52-002: substrate-tester fire #52 Lane 16 mutation
testing surfaced `ExclusionCertificate.feeds_negative_space_axis()`
at line 451 as having no return-value test. `return_constant_None`
mutation survived because tests verify which strengths feed gradients
but don't assert the method's return-value contract directly.

This file ships explicit return-value assertions across all five
CertificateStrength values, designed to FAIL when the method body is
mutated to `return None`.

**Sister files (same pattern):**
  - test_method_spec_factory_returns.py (fire #51 closure)
  - test_frozen_baseline_manifest.py (fire #50 closure, expanded fire #53)

**Source ticket:** T-2026-05-08-ST-fire54-001 (Techne; closes
ST-fire52-002).
"""
from __future__ import annotations

import pytest

from sigma_kernel.exclusion_certificate import (
    Boundary, CertificateStrength, CertificateType,
    ExclusionCertificate, ExclusionClaim, RegionSpec,
    ReplayInfo, TriangulationPathRef, VerifierSet,
    NEGATIVE_SPACE_FEEDING_STRENGTHS,
)
from sigma_kernel.method_spec import IndependenceClass, MethodSpec
from sigma_kernel.triangulation_protocol import MethodClass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _spec() -> MethodSpec:
    return MethodSpec(
        engine="mpmath", strategy="polyroots",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        version="1.0.0",
    )


def _make_cert(
    strength: CertificateStrength,
    *,
    region_key: str = "test:fire54",
) -> ExclusionCertificate:
    """Construct a minimal cert. COMPLETE requires non-empty
    triangulation_history per substrate v2.3 §6.3."""
    spec = _spec()
    triangulation_history: tuple = ()
    if strength is CertificateStrength.COMPLETE:
        triangulation_history = (
            TriangulationPathRef(
                path_id="path_fire54",
                method_spec=spec,
                verdict="verified",
                timestamp=0.0,
                summary="fire54 stub triangulation path",
            ),
        )
    return ExclusionCertificate(
        region_spec=RegionSpec(coordinate_chart_id=region_key, constraints={}, bounds=None),
        exclusion_claim=ExclusionClaim(
            excluded_property="probe", result_class="test", reason="fire54_returns",
        ),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=strength,
        verifier_set=VerifierSet(methods=(spec,)),
        replay=ReplayInfo(code_hash="x", data_hash="y", seed=0, environment_hash="z"),
        triangulation_history=triangulation_history,
    )


# ---------------------------------------------------------------------------
# feeds_negative_space_axis return-value contract (line 451 mutation site)
# ---------------------------------------------------------------------------


class TestFeedsNegativeSpaceAxisReturnContract:
    """Each CertificateStrength value gets an explicit return-value
    assertion. Catches `return self.strength in NEGATIVE_SPACE_FEEDING_STRENGTHS`
    -> `return None` mutation."""

    def test_COMPLETE_feeds(self):
        cert = _make_cert(CertificateStrength.COMPLETE)
        result = cert.feeds_negative_space_axis()
        assert result is not None
        assert result is True

    def test_BOUNDED_COMPLETE_feeds(self):
        cert = _make_cert(CertificateStrength.BOUNDED_COMPLETE)
        result = cert.feeds_negative_space_axis()
        assert result is not None
        assert result is True

    def test_CONDITIONAL_does_not_feed(self):
        cert = _make_cert(CertificateStrength.CONDITIONAL)
        result = cert.feeds_negative_space_axis()
        assert result is not None
        assert result is False

    def test_HEURISTIC_does_not_feed(self):
        cert = _make_cert(CertificateStrength.HEURISTIC)
        result = cert.feeds_negative_space_axis()
        assert result is not None
        assert result is False

    def test_DIAGNOSTIC_ONLY_does_not_feed(self):
        cert = _make_cert(CertificateStrength.DIAGNOSTIC_ONLY)
        result = cert.feeds_negative_space_axis()
        assert result is not None
        assert result is False

    def test_return_type_is_bool(self):
        """Belt-and-suspenders: explicit isinstance(bool) check across all
        five strengths. Catches return_constant_None even more directly."""
        for strength in CertificateStrength:
            cert = _make_cert(strength)
            result = cert.feeds_negative_space_axis()
            assert isinstance(result, bool), (
                f"feeds_negative_space_axis() returned {result!r} "
                f"(type {type(result).__name__}) for strength {strength!r}; "
                f"expected bool."
            )

    def test_consistent_with_NEGATIVE_SPACE_FEEDING_STRENGTHS_constant(self):
        """The method's return value must match membership in the module-
        level constant. If the constant changes, this test catches the
        method drifting out of sync."""
        for strength in CertificateStrength:
            cert = _make_cert(strength)
            expected = strength in NEGATIVE_SPACE_FEEDING_STRENGTHS
            actual = cert.feeds_negative_space_axis()
            assert actual == expected, (
                f"feeds_negative_space_axis() returned {actual!r} for "
                f"{strength!r}; expected {expected!r} per "
                f"NEGATIVE_SPACE_FEEDING_STRENGTHS."
            )
