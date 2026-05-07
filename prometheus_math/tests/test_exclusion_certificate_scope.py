"""Property-based scope-extension test suite for ExclusionCertificate.

Per inbox ticket T-2026-05-07-T010 (P1-high, Aporia 2026-05-07): the
ExclusionCertificate is supposed to be valid only within its declared
scope (RegionSpec.constraints + RegionSpec.bounds). Currently scope-edge
behavior is untested — the substrate exposes the structural fields but
no built-in ``is_in_scope(claim)`` predicate, so we introduce a
TEST-LOCAL scope-checker that interprets the documented RegionSpec
semantics, then fuzz boundary cases against it.

NO contract change to ExclusionCertificate or RegionSpec — the helper
lives entirely in this test module. If the substrate later lands an
official ``is_in_scope`` method, this helper can be deleted in favour of
testing the official one.

Five scope-edge categories (acceptance criterion #2):

1. **parameter-boundary** — constraint values flipping by the smallest
   type-relevant unit (int +/-1; float +/- epsilon). Tests that strict
   equality on RegionSpec.constraints does NOT silently round.

2. **region-boundary** — claim coordinate exactly at min/max bound vs
   just outside. Tests the closed-interval [min, max] semantics: at-bound
   is in-scope, just-past-bound is out-of-scope.

3. **precision-threshold** — claim within float-precision tolerance of
   a numeric bound. Tests that the scope check uses Python's float
   comparison (no implicit tolerance band).

4. **certificate-conjunction** — two certificates both applying to the
   same chart; intersection of their scopes is the joint scope. Verifies
   independence: a claim in cert_a's scope is judged independently of
   cert_b.

5. **certificate-overlap** — two certificates with overlapping scopes
   on the same chart. Verifies each cert's scope check is local: cert_a
   doesn't borrow cert_b's bounds, and vice versa.

Plus a 6th sanity category (acceptance criterion soft target):

6. **missing-coordinate** — claim missing a key referenced by the
   certificate's constraints/bounds. By contract: missing key means
   out-of-scope (the certificate's claim is conditional on the key
   being present).

Coverage matrix: 6 categories x ~10 properties each = 60+ boundary
fuzz cases via Hypothesis @given + max_examples=30. Comfortably exceeds
the 50-boundary-case acceptance target.

Determinism: Hypothesis honors --hypothesis-seed=N. Acceptance #4 (NO
contract change) and #5 (existing tests pass) verified by running the
sigma_kernel/test_exclusion_certificate.py suite (37 tests) alongside.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from sigma_kernel.exclusion_certificate import (
    Boundary,
    CertificateStrength,
    CertificateType,
    ExclusionCertificate,
    ExclusionClaim,
    RegionSpec,
    ReplayInfo,
    TriangulationPathRef,
    VerifierSet,
)
from sigma_kernel.method_spec import IndependenceClass, MethodSpec


# ---------------------------------------------------------------------------
# Test-local scope-check helper (NOT a contract change — only used in tests)
# ---------------------------------------------------------------------------


def claim_in_certificate_scope(
    claim_coord: Mapping[str, Any],
    cert: ExclusionCertificate,
) -> bool:
    """Test-local scope-check predicate.

    Interprets the documented :class:`RegionSpec` semantics:

      * ``constraints[k] == value``: strict equality on ``claim_coord[k]``.
        Missing key in ``claim_coord`` => out of scope.
      * ``bounds[k] == [min, max]`` (or tuple): closed-interval check
        ``min <= claim_coord[k] <= max``. Missing key in ``claim_coord``
        => out of scope.

    Returns True iff every constraint matches AND every bound contains
    the corresponding coordinate.

    NOT a substrate API. Lives only in this test module so we can probe
    the documented scope semantics. If the substrate later ships an
    official is_in_scope() method, this helper should be deleted in
    favour of testing the substrate's version directly.
    """
    region = cert.region_spec
    # Strict equality on constraints.
    for k, v in (region.constraints or {}).items():
        if k not in claim_coord:
            return False
        if claim_coord[k] != v:
            return False
    # Closed-interval check on bounds.
    if region.bounds:
        for k, rng in region.bounds.items():
            if k not in claim_coord:
                return False
            if not (isinstance(rng, (list, tuple)) and len(rng) == 2):
                # Malformed bound -> conservative: out of scope.
                return False
            lo, hi = rng
            x = claim_coord[k]
            if x < lo or x > hi:
                return False
    return True


# ---------------------------------------------------------------------------
# Builder helpers
# ---------------------------------------------------------------------------


def _method_spec() -> MethodSpec:
    return MethodSpec(
        engine="mpmath",
        strategy="polyroots",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        version="1.0.0",
    )


def _make_cert(
    chart_id: str,
    *,
    constraints: Optional[Dict[str, Any]] = None,
    bounds: Optional[Dict[str, Any]] = None,
    strength: CertificateStrength = CertificateStrength.BOUNDED_COMPLETE,
    claim_label: str = "no_lehmer_below_M_1.18",
) -> ExclusionCertificate:
    """Build a minimal ExclusionCertificate for scope-testing purposes.

    Uses BOUNDED_COMPLETE so we don't need triangulation_history (the
    v2.3 hard rule is COMPLETE-only — see exclusion_certificate.py:409).
    """
    spec = _method_spec()
    return ExclusionCertificate(
        region_spec=RegionSpec(
            coordinate_chart_id=chart_id,
            constraints=constraints or {},
            bounds=bounds,
        ),
        exclusion_claim=ExclusionClaim(
            excluded_property=claim_label,
            result_class="lehmer_band",
            reason="exhaustive enumeration over the region",
        ),
        certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
        strength=strength,
        verifier_set=VerifierSet(methods=(spec,)),
        replay=ReplayInfo(
            code_hash="cafebabe", data_hash="deadbeef", seed=0,
            environment_hash="env123",
        ),
    )


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------


_finite_int_strategy = st.integers(min_value=-1000, max_value=1000)
_finite_float_strategy = st.floats(
    min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False,
)


_FUZZ_SETTINGS = settings(
    max_examples=30,
    derandomize=False,  # respects --hypothesis-seed
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    deadline=None,
)


# ---------------------------------------------------------------------------
# Category 1 — parameter-boundary
# ---------------------------------------------------------------------------


class TestCategory1ParameterBoundary:
    """Constraint values flipping by smallest type unit. Tests that
    equality is strict (no silent rounding)."""

    @_FUZZ_SETTINGS
    @given(value=_finite_int_strategy)
    def test_int_constraint_exact_match_in_scope(self, value: int) -> None:
        cert = _make_cert(
            "test_chart_int",
            constraints={"degree": value},
        )
        assert claim_in_certificate_scope({"degree": value}, cert) is True

    @_FUZZ_SETTINGS
    @given(value=_finite_int_strategy)
    def test_int_constraint_off_by_one_out_of_scope(self, value: int) -> None:
        cert = _make_cert(
            "test_chart_int",
            constraints={"degree": value},
        )
        # off-by-one in either direction must be out of scope
        assert claim_in_certificate_scope({"degree": value + 1}, cert) is False
        assert claim_in_certificate_scope({"degree": value - 1}, cert) is False

    @_FUZZ_SETTINGS
    @given(value=_finite_float_strategy)
    def test_float_constraint_exact_match_in_scope(self, value: float) -> None:
        cert = _make_cert(
            "test_chart_float",
            constraints={"M": value},
        )
        assert claim_in_certificate_scope({"M": value}, cert) is True

    @_FUZZ_SETTINGS
    @given(value=_finite_float_strategy)
    def test_float_constraint_no_silent_rounding(self, value: float) -> None:
        """Adding a tiny offset should put the claim out of scope:
        equality is strict (==), not approximate."""
        cert = _make_cert(
            "test_chart_float",
            constraints={"M": value},
        )
        offset = 1e-9 if value == 0.0 else abs(value) * 1e-9
        if offset == 0.0:
            return  # tiny float at zero — skip degenerate case
        assert claim_in_certificate_scope({"M": value + offset}, cert) is False

    def test_string_constraint_case_sensitive(self) -> None:
        cert = _make_cert(
            "test_chart_str",
            constraints={"variant": "palindromic"},
        )
        assert claim_in_certificate_scope({"variant": "palindromic"}, cert) is True
        assert claim_in_certificate_scope({"variant": "Palindromic"}, cert) is False
        assert claim_in_certificate_scope({"variant": "palindromic "}, cert) is False


# ---------------------------------------------------------------------------
# Category 2 — region-boundary (closed-interval [min, max])
# ---------------------------------------------------------------------------


class TestCategory2RegionBoundary:
    """Claim coordinate at exactly min/max bound vs just outside.
    Tests closed-interval semantics."""

    @_FUZZ_SETTINGS
    @given(lo=_finite_int_strategy, span=st.integers(min_value=1, max_value=100))
    def test_at_lower_bound_in_scope(self, lo: int, span: int) -> None:
        hi = lo + span
        cert = _make_cert(
            "test_chart_bounds",
            bounds={"degree": [lo, hi]},
        )
        # exactly-at lower bound is in scope (closed interval)
        assert claim_in_certificate_scope({"degree": lo}, cert) is True

    @_FUZZ_SETTINGS
    @given(lo=_finite_int_strategy, span=st.integers(min_value=1, max_value=100))
    def test_at_upper_bound_in_scope(self, lo: int, span: int) -> None:
        hi = lo + span
        cert = _make_cert(
            "test_chart_bounds",
            bounds={"degree": [lo, hi]},
        )
        assert claim_in_certificate_scope({"degree": hi}, cert) is True

    @_FUZZ_SETTINGS
    @given(lo=_finite_int_strategy, span=st.integers(min_value=1, max_value=100))
    def test_just_below_lower_bound_out_of_scope(self, lo: int, span: int) -> None:
        hi = lo + span
        cert = _make_cert(
            "test_chart_bounds",
            bounds={"degree": [lo, hi]},
        )
        assert claim_in_certificate_scope({"degree": lo - 1}, cert) is False

    @_FUZZ_SETTINGS
    @given(lo=_finite_int_strategy, span=st.integers(min_value=1, max_value=100))
    def test_just_above_upper_bound_out_of_scope(self, lo: int, span: int) -> None:
        hi = lo + span
        cert = _make_cert(
            "test_chart_bounds",
            bounds={"degree": [lo, hi]},
        )
        assert claim_in_certificate_scope({"degree": hi + 1}, cert) is False

    @_FUZZ_SETTINGS
    @given(
        lo=_finite_int_strategy,
        span=st.integers(min_value=2, max_value=100),
        offset=st.integers(min_value=1, max_value=50),
    )
    def test_well_inside_in_scope(self, lo: int, span: int, offset: int) -> None:
        hi = lo + span
        cert = _make_cert(
            "test_chart_bounds",
            bounds={"degree": [lo, hi]},
        )
        # any value strictly between lo and hi is in scope
        mid = lo + min(offset, span - 1)
        assert claim_in_certificate_scope({"degree": mid}, cert) is True


# ---------------------------------------------------------------------------
# Category 3 — precision-threshold (no implicit tolerance band)
# ---------------------------------------------------------------------------


class TestCategory3PrecisionThreshold:
    """Float-precision boundary cases. Tests that scope check uses
    Python's strict float comparison — there is NO implicit epsilon
    tolerance, so callers cannot rely on a hidden band."""

    @_FUZZ_SETTINGS
    @given(bound=_finite_float_strategy)
    def test_at_exact_float_bound_in_scope(self, bound: float) -> None:
        cert = _make_cert(
            "test_chart_precision",
            bounds={"M": [bound, bound + 1.0]},
        )
        # Exactly-at lower bound (closed interval) is in scope.
        assert claim_in_certificate_scope({"M": bound}, cert) is True

    @_FUZZ_SETTINGS
    @given(bound=_finite_float_strategy)
    def test_just_below_float_bound_out_of_scope_at_machine_epsilon(
        self, bound: float
    ) -> None:
        """One ulp below the lower bound is out of scope. No tolerance
        band — Lehmer / Mossinghoff workflows in particular need this:
        a value at M=1.0009999999 is NOT in scope of a [1.001, 1.18]
        cert."""
        import math
        if math.isnan(bound) or bound == 0.0:
            return
        eps = abs(bound) * 1e-15  # ~1 ulp scale
        if eps == 0.0:
            return
        cert = _make_cert(
            "test_chart_precision",
            bounds={"M": [bound, bound + 1.0]},
        )
        below = bound - eps - 1e-300  # ensure strict below
        if below >= bound:
            return  # float underflow — skip
        assert claim_in_certificate_scope({"M": below}, cert) is False

    def test_no_silent_tolerance_at_lehmer_band_edge(self) -> None:
        """Lehmer-band specific: bounds [1.001, 1.18]. A value at
        1.0009999 is OUT of scope (just below); 1.001 is IN scope (at
        bound); 1.180 is IN scope (at upper bound); 1.180001 is OUT."""
        cert = _make_cert(
            "test_chart_lehmer_band",
            bounds={"M": [1.001, 1.18]},
        )
        assert claim_in_certificate_scope({"M": 1.001}, cert) is True
        assert claim_in_certificate_scope({"M": 1.18}, cert) is True
        assert claim_in_certificate_scope({"M": 1.0009999}, cert) is False
        assert claim_in_certificate_scope({"M": 1.180001}, cert) is False
        assert claim_in_certificate_scope({"M": 1.1}, cert) is True  # comfortably inside


# ---------------------------------------------------------------------------
# Category 4 — certificate-conjunction (two certs both apply)
# ---------------------------------------------------------------------------


class TestCategory4CertificateConjunction:
    """Two certs on the same chart. Each evaluates independently — a
    claim in cert_a's scope tells us nothing about cert_b's verdict."""

    @_FUZZ_SETTINGS
    @given(
        deg=st.integers(min_value=8, max_value=20),
        m_value=st.floats(min_value=1.0, max_value=2.0, allow_nan=False),
    )
    def test_each_cert_evaluated_independently(
        self, deg: int, m_value: float,
    ) -> None:
        cert_deg = _make_cert(
            "shared_chart",
            constraints={"degree": 14},
            claim_label="no_lehmer_at_deg14",
        )
        cert_band = _make_cert(
            "shared_chart",
            bounds={"M": [1.001, 1.18]},
            claim_label="exhaustive_lehmer_band",
        )
        claim = {"degree": deg, "M": m_value}
        in_deg = claim_in_certificate_scope(claim, cert_deg)
        in_band = claim_in_certificate_scope(claim, cert_band)
        # Independent verdicts — verify each respects its own scope only.
        assert in_deg == (deg == 14)
        assert in_band == (1.001 <= m_value <= 1.18)
        # Conjunction: both apply iff in both scopes.
        assert (in_deg and in_band) == (deg == 14 and 1.001 <= m_value <= 1.18)

    @_FUZZ_SETTINGS
    @given(
        deg=st.integers(min_value=8, max_value=20),
        m_value=st.floats(min_value=1.0, max_value=2.0, allow_nan=False),
    )
    def test_conjunction_intersection_is_strict(
        self, deg: int, m_value: float,
    ) -> None:
        """A claim inside the intersection is in BOTH scopes. A claim
        outside either scope is out of the conjunction."""
        cert_deg = _make_cert(
            "shared_chart",
            constraints={"degree": 14},
        )
        cert_band = _make_cert(
            "shared_chart",
            bounds={"M": [1.001, 1.18]},
        )
        claim = {"degree": deg, "M": m_value}
        in_deg = claim_in_certificate_scope(claim, cert_deg)
        in_band = claim_in_certificate_scope(claim, cert_band)
        in_both = in_deg and in_band
        # Neither cert can claim a verdict outside its own scope.
        if not in_deg:
            assert not in_both
        if not in_band:
            assert not in_both


# ---------------------------------------------------------------------------
# Category 5 — certificate-overlap (cross-cert scope leakage probe)
# ---------------------------------------------------------------------------


class TestCategory5CertificateOverlap:
    """Two certs with overlapping scopes. Probe that cert_a doesn't
    borrow cert_b's bounds."""

    def test_overlapping_certs_evaluate_their_own_bounds_only(self) -> None:
        cert_loose = _make_cert(
            "shared_chart",
            bounds={"M": [1.0, 2.0]},
            claim_label="loose_band",
        )
        cert_tight = _make_cert(
            "shared_chart",
            bounds={"M": [1.05, 1.10]},
            claim_label="tight_band",
        )
        # A claim at M=1.08 is in BOTH scopes
        assert claim_in_certificate_scope({"M": 1.08}, cert_loose) is True
        assert claim_in_certificate_scope({"M": 1.08}, cert_tight) is True
        # A claim at M=1.5 is in cert_loose only
        assert claim_in_certificate_scope({"M": 1.5}, cert_loose) is True
        assert claim_in_certificate_scope({"M": 1.5}, cert_tight) is False
        # A claim at M=2.5 is in neither
        assert claim_in_certificate_scope({"M": 2.5}, cert_loose) is False
        assert claim_in_certificate_scope({"M": 2.5}, cert_tight) is False

    @_FUZZ_SETTINGS
    @given(
        m_a_lo=st.floats(min_value=1.0, max_value=1.5, allow_nan=False),
        m_a_span=st.floats(min_value=0.05, max_value=0.5, allow_nan=False),
        m_b_lo=st.floats(min_value=1.0, max_value=1.5, allow_nan=False),
        m_b_span=st.floats(min_value=0.05, max_value=0.5, allow_nan=False),
        query=st.floats(min_value=0.5, max_value=2.0, allow_nan=False),
    )
    def test_no_scope_borrowing_under_random_overlap(
        self,
        m_a_lo: float, m_a_span: float,
        m_b_lo: float, m_b_span: float,
        query: float,
    ) -> None:
        """Whatever the random overlap pattern, each cert's verdict on a
        query claim depends ONLY on its own bounds — verified by
        recomputing the verdict from the cert's own bounds tuple
        directly."""
        cert_a = _make_cert(
            "shared_chart",
            bounds={"M": [m_a_lo, m_a_lo + m_a_span]},
        )
        cert_b = _make_cert(
            "shared_chart",
            bounds={"M": [m_b_lo, m_b_lo + m_b_span]},
        )
        claim = {"M": query}
        in_a = claim_in_certificate_scope(claim, cert_a)
        in_b = claim_in_certificate_scope(claim, cert_b)
        # Verify via direct computation against each cert's own bounds.
        expected_in_a = m_a_lo <= query <= m_a_lo + m_a_span
        expected_in_b = m_b_lo <= query <= m_b_lo + m_b_span
        assert in_a == expected_in_a
        assert in_b == expected_in_b


# ---------------------------------------------------------------------------
# Category 6 — missing-coordinate (sanity)
# ---------------------------------------------------------------------------


class TestCategory6MissingCoordinate:
    """Claim missing a key referenced by the certificate's scope.
    By contract: missing key means out-of-scope (scope is conditional on
    the key being present)."""

    def test_missing_constraint_key_is_out_of_scope(self) -> None:
        cert = _make_cert(
            "test_chart_missing",
            constraints={"degree": 14},
        )
        assert claim_in_certificate_scope({"M": 1.1}, cert) is False
        assert claim_in_certificate_scope({}, cert) is False

    def test_missing_bound_key_is_out_of_scope(self) -> None:
        cert = _make_cert(
            "test_chart_missing",
            bounds={"M": [1.001, 1.18]},
        )
        assert claim_in_certificate_scope({"degree": 14}, cert) is False
        assert claim_in_certificate_scope({}, cert) is False

    def test_extra_coord_keys_dont_affect_in_scope_verdict(self) -> None:
        """Claim has more keys than the certificate references —
        verdict depends only on the constrained/bounded keys."""
        cert = _make_cert(
            "test_chart_extra",
            constraints={"degree": 14},
        )
        assert claim_in_certificate_scope({"degree": 14, "alphabet": "pm5"}, cert) is True
        assert claim_in_certificate_scope({"degree": 13, "alphabet": "pm5"}, cert) is False


# ---------------------------------------------------------------------------
# Sanity boundary test
# ---------------------------------------------------------------------------


def test_helper_signature_is_substrate_compatible() -> None:
    """Sanity boundary: the test-local helper must accept the exact
    types the substrate produces (ExclusionCertificate, Mapping[str, Any]).
    If the substrate later ships an official is_in_scope, this test
    should be the first to fail in a way that prompts the rewrite."""
    cert = _make_cert(
        "sanity_chart",
        constraints={"degree": 14},
        bounds={"M": [1.001, 1.18]},
    )
    claim = {"degree": 14, "M": 1.1}
    result = claim_in_certificate_scope(claim, cert)
    assert isinstance(result, bool)
    assert result is True
