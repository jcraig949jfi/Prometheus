"""KillComponent multi-precision sister-field tests.

Closes T-2026-05-07-T029 implementation per `prometheus_math/MULTIPRECISION_AUDIT.md`
Option B (additive sister fields, contract preserved).

Mini contract-change window 2026-05-10. Two new optional fields on
KillComponent:
  - `margin_high_precision: Optional[str]` — string-serialized
    high-precision margin value (parse with mpmath.mpf when needed)
  - `margin_precision_dps: Optional[int]` — decimal places of precision
    the high-precision string carries

Existing `margin: Optional[float]` contract preserved (always present
as the double-precision approximation). Multi-precision is opt-in;
legacy callers see no change.
"""
from __future__ import annotations

import pytest

from prometheus_math.kill_vector import KillComponent


# ---------------------------------------------------------------------------
# Defaults preserve pre-2026-05-10 behavior
# ---------------------------------------------------------------------------


class TestDefaultsPreservePreContractBehavior:
    def test_defaults_None_for_both_new_fields(self):
        c = KillComponent(falsifier_name="F1", triggered=True, margin=0.5,
                          margin_unit="p_value")
        assert c.margin_high_precision is None
        assert c.margin_precision_dps is None

    def test_legacy_dict_loads_with_defaults(self):
        """A pre-2026-05-10 dict (no new fields) MUST load with both
        new fields defaulting to None. Substrate's additive-evolution
        discipline."""
        legacy = {
            "falsifier_name": "F1", "triggered": True, "margin": 0.5,
            "margin_unit": "p_value", "metadata": {}, "precision_dps": None,
            "method": "legacy", "convergence_status": "n/a",
            "stability": None, "stability_pass": None,
        }
        c = KillComponent.from_dict(legacy)
        assert c.margin_high_precision is None
        assert c.margin_precision_dps is None
        assert c.margin == 0.5
        assert c.margin_unit == "p_value"


# ---------------------------------------------------------------------------
# High-precision payload contract
# ---------------------------------------------------------------------------


class TestHighPrecisionPayload:
    def test_set_string_high_precision(self):
        s = "1.234567890123456789012345678901234567890e-30"
        c = KillComponent(
            falsifier_name="maass_eigenvalue", triggered=True,
            margin=1e-30, margin_unit="absolute",
            margin_high_precision=s, margin_precision_dps=40,
        )
        assert c.margin_high_precision == s
        assert c.margin_precision_dps == 40

    def test_high_precision_parseable_by_mpmath(self):
        """The high-precision string MUST parse with mpmath.mpf and
        equal the original numeric value (modulo string representation
        roundtrip)."""
        try:
            import mpmath
        except ImportError:
            pytest.skip("mpmath not available")
        s = "1.234567890123456789012345678901234567890e-30"
        c = KillComponent(
            falsifier_name="x", triggered=True, margin=1e-30,
            margin_unit="absolute",
            margin_high_precision=s, margin_precision_dps=40,
        )
        mpmath.mp.dps = c.margin_precision_dps
        v = mpmath.mpf(c.margin_high_precision)
        # The mpf MUST agree with the source string at the documented dps
        assert str(v).startswith("1.234567890123456789")

    def test_consumer_can_recover_double_from_high_precision(self):
        """Even when high-precision is set, `margin` (double approximation)
        must remain valid for legacy consumers that don't use the high-
        precision field."""
        c = KillComponent(
            falsifier_name="x", triggered=True, margin=0.5,
            margin_unit="p_value",
            margin_high_precision="0.5000000000000000000000000000000000000000",
            margin_precision_dps=40,
        )
        # Double consumer reads `margin` and gets back the double approx
        assert c.margin == 0.5
        # High-precision consumer reads `margin_high_precision`
        assert c.margin_high_precision.startswith("0.5")


# ---------------------------------------------------------------------------
# Permissive validation (substrate v2.3 §6.2 P3 discipline)
# ---------------------------------------------------------------------------


class TestPermissiveValidation:
    def test_empty_string_coerced_to_None(self):
        """Empty `margin_high_precision` is treated as 'not present'."""
        c = KillComponent(falsifier_name="x", triggered=False, margin=None,
                          margin_high_precision="")
        assert c.margin_high_precision is None

    def test_negative_dps_coerced_to_None(self):
        c = KillComponent(falsifier_name="x", triggered=False, margin=None,
                          margin_precision_dps=-5)
        assert c.margin_precision_dps is None

    def test_non_int_dps_coerced_to_None(self):
        c = KillComponent(falsifier_name="x", triggered=False, margin=None,
                          margin_precision_dps="garbage")  # type: ignore
        assert c.margin_precision_dps is None

    def test_float_dps_coerced_to_int(self):
        c = KillComponent(falsifier_name="x", triggered=False, margin=None,
                          margin_precision_dps=40.7)  # type: ignore
        assert c.margin_precision_dps == 40

    def test_zero_dps_accepted(self):
        """dps=0 is technically valid (means 'no documented precision'). The
        substrate is permissive at write."""
        c = KillComponent(falsifier_name="x", triggered=False, margin=None,
                          margin_precision_dps=0)
        assert c.margin_precision_dps == 0


# ---------------------------------------------------------------------------
# Roundtrip safety
# ---------------------------------------------------------------------------


class TestRoundtripSafety:
    def test_to_dict_includes_new_fields(self):
        c = KillComponent(
            falsifier_name="x", triggered=True, margin=1.0,
            margin_unit="absolute",
            margin_high_precision="1.0000000000000000000",
            margin_precision_dps=20,
        )
        d = c.to_dict()
        assert d["margin_high_precision"] == "1.0000000000000000000"
        assert d["margin_precision_dps"] == 20

    def test_from_dict_restores_new_fields(self):
        c = KillComponent(
            falsifier_name="x", triggered=True, margin=2.5,
            margin_unit="absolute",
            margin_high_precision="2.500000000000000000000000000000",
            margin_precision_dps=30,
        )
        d = c.to_dict()
        c2 = KillComponent.from_dict(d)
        assert c2.margin_high_precision == c.margin_high_precision
        assert c2.margin_precision_dps == c.margin_precision_dps

    def test_full_roundtrip_equality(self):
        """A KillComponent → to_dict → from_dict roundtrip must produce
        an equal KillComponent (modulo dict mutability of `metadata`)."""
        c = KillComponent(
            falsifier_name="maass_eigen_4", triggered=True,
            margin=3.14159, margin_unit="absolute",
            margin_high_precision="3.14159265358979323846264338327950288",
            margin_precision_dps=35,
            method="mpmath_polyroots", convergence_status="converged",
        )
        c2 = KillComponent.from_dict(c.to_dict())
        # Most fields equal (metadata is dict; KillComponent has eq=True
        # but dict equality works because both are empty / shallow-equal)
        for fname in ("falsifier_name", "triggered", "margin", "margin_unit",
                      "method", "convergence_status",
                      "margin_high_precision", "margin_precision_dps"):
            assert getattr(c2, fname) == getattr(c, fname), (
                f"roundtrip lost field {fname!r}: "
                f"{getattr(c, fname)!r} -> {getattr(c2, fname)!r}"
            )


# ---------------------------------------------------------------------------
# Coherence (no enforcement; documented as caveat in __post_init__)
# ---------------------------------------------------------------------------


class TestCoherenceCaveatNoEnforcement:
    """Per audit Option B + substrate's permissive-at-write discipline,
    we DO NOT enforce that margin_high_precision and margin_precision_dps
    must both be set or both be None. Either alone is valid (with the
    documented caveat that consumers may need to fall back)."""

    def test_high_precision_without_dps_accepted(self):
        c = KillComponent(falsifier_name="x", triggered=False, margin=None,
                          margin_high_precision="3.14159")
        assert c.margin_high_precision == "3.14159"
        assert c.margin_precision_dps is None  # caveat: consumer falls back

    def test_dps_without_high_precision_accepted(self):
        """Edge: dps annotated without high-precision string is unusual
        but the contract permits it (e.g. caller plans to populate
        high-precision later)."""
        c = KillComponent(falsifier_name="x", triggered=False, margin=None,
                          margin_precision_dps=50)
        assert c.margin_precision_dps == 50
        assert c.margin_high_precision is None
