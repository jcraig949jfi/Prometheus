"""Return-value coverage for sigma_kernel.triangulation_protocol.

Closes ST-fire54-002: substrate-tester fire #54 Lane 16 surfaced 4
surviving mutations on triangulation_protocol.py:
  - Line 149: `INDEPENDENCE_TO_METHOD_CLASS[key]` (return_constant_None)
  - Line 281: `self.method_class == MethodClass.PROOF_BEARING` (comparison_flip)
  - Line 292: `self.method_class != MethodClass.EXPLORATORY` (comparison_flip + return_constant_None)
  - Line 388: `len(paths_tuple) < 3` triangulation threshold (comparison_flip)

This file ships parametrized tests targeting each site, designed to
FAIL when the expressions are mutated.

**Sister files (same pattern):**
  - test_method_spec_factory_returns.py (fire #51 closure)
  - test_exclusion_certificate_returns.py (fire #54 closure)

**Source ticket:** T-2026-05-08-ST-fire55-001 (Techne; closes
ST-fire54-002).
"""
from __future__ import annotations

import pytest

from sigma_kernel.method_spec import IndependenceClass, MethodSpec
from sigma_kernel.triangulation_protocol import (
    INDEPENDENCE_TO_METHOD_CLASS,
    MethodClass,
    TriangulationPath,
    TriangulationProtocol,
    TriangulationVerdict,
    method_class_for_independence_class,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _spec(ic: IndependenceClass = IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION) -> MethodSpec:
    return MethodSpec(
        engine="mpmath", strategy="polyroots",
        independence_class=ic, version="1.0.0",
    )


def _path(
    method_class: MethodClass,
    *,
    path_id: str = "fire55_path",
    verdict: str = "verified",
    ic: IndependenceClass = IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
) -> TriangulationPath:
    return TriangulationPath(
        path_id=path_id,
        method_spec=_spec(ic),
        method_class=method_class,
        verdict=verdict,
        runtime_ms=10,
        rationale="fire55 stub",
        timestamp=0.0,
    )


# ---------------------------------------------------------------------------
# method_class_for_independence_class — line 149 mutation site
# ---------------------------------------------------------------------------


class TestMethodClassForIndependenceClassReturn:
    """Catches `return INDEPENDENCE_TO_METHOD_CLASS[key]` -> `return None`
    mutation on line 149."""

    @pytest.mark.parametrize("ic_value,expected", sorted(INDEPENDENCE_TO_METHOD_CLASS.items()))
    def test_returns_expected_method_class(self, ic_value: str, expected: MethodClass):
        result = method_class_for_independence_class(ic_value)
        assert result is not None
        assert result is expected

    def test_returns_method_class_instance(self):
        """Belt-and-suspenders: every return must be a MethodClass enum."""
        for ic_value in INDEPENDENCE_TO_METHOD_CLASS:
            result = method_class_for_independence_class(ic_value)
            assert isinstance(result, MethodClass)

    def test_unregistered_key_raises_KeyError_not_returns_None(self):
        """Unregistered keys must raise (loud-fail discipline), not
        silently return None per substrate v2.3 + 2026-05-07 contract change."""
        with pytest.raises(KeyError):
            method_class_for_independence_class("definitely_not_registered_xyz")


# ---------------------------------------------------------------------------
# is_proof_bearing — line 281 mutation site
# ---------------------------------------------------------------------------


class TestIsProofBearingReturn:
    """Catches:
      - `self.method_class == MethodClass.PROOF_BEARING` -> `... != ...` flip
      - `return self.method_class == ...` -> `return None`
    """

    @pytest.mark.parametrize("method_class,expected", [
        (MethodClass.PROOF_BEARING, True),
        (MethodClass.NUMERICAL, False),
        (MethodClass.CATALOG, False),
        (MethodClass.ROBUSTNESS, False),
        (MethodClass.EXPLORATORY, False),
    ])
    def test_is_proof_bearing_per_class(self, method_class: MethodClass, expected: bool):
        path = _path(method_class)
        result = path.is_proof_bearing
        assert result is not None
        assert result is expected

    def test_return_type_is_bool(self):
        for mc in MethodClass:
            path = _path(mc)
            assert isinstance(path.is_proof_bearing, bool)


# ---------------------------------------------------------------------------
# can_certify — line 292 mutation site
# ---------------------------------------------------------------------------


class TestCanCertifyReturn:
    """Catches:
      - `self.method_class != MethodClass.EXPLORATORY` -> `... == ...` flip
      - `return self.method_class != ...` -> `return None`
    """

    @pytest.mark.parametrize("method_class,expected", [
        (MethodClass.PROOF_BEARING, True),
        (MethodClass.NUMERICAL, True),
        (MethodClass.CATALOG, True),
        (MethodClass.ROBUSTNESS, True),
        (MethodClass.EXPLORATORY, False),
    ])
    def test_can_certify_per_class(self, method_class: MethodClass, expected: bool):
        path = _path(method_class)
        result = path.can_certify
        assert result is not None
        assert result is expected

    def test_return_type_is_bool(self):
        for mc in MethodClass:
            path = _path(mc)
            assert isinstance(path.can_certify, bool)


# ---------------------------------------------------------------------------
# evaluate threshold (len(paths_tuple) < 3) — line 388 mutation site
# ---------------------------------------------------------------------------


class TestEvaluateThreshold:
    """Catches `len(paths_tuple) < 3` -> `len(paths_tuple) > 3` flip on
    line 388 (substrate v2.3 §6.4 triangulation threshold; load-bearing).

    The threshold separates "INCONCLUSIVE_WAITING" (insufficient paths)
    from the deeper rule evaluation. Crossing the threshold (3 paths)
    must change the verdict; the < operator is the load-bearing comparison."""

    def test_zero_paths_inconclusive_waiting(self):
        protocol = TriangulationProtocol()
        result = protocol.evaluate([])
        assert result.verdict is TriangulationVerdict.INCONCLUSIVE_WAITING

    def test_one_path_inconclusive_waiting(self):
        protocol = TriangulationProtocol()
        result = protocol.evaluate([_path(MethodClass.PROOF_BEARING, path_id="p1")])
        assert result.verdict is TriangulationVerdict.INCONCLUSIVE_WAITING

    def test_two_paths_inconclusive_waiting(self):
        protocol = TriangulationProtocol()
        result = protocol.evaluate([
            _path(MethodClass.PROOF_BEARING, path_id="p1"),
            _path(MethodClass.NUMERICAL, path_id="p2"),
        ])
        assert result.verdict is TriangulationVerdict.INCONCLUSIVE_WAITING

    def test_three_paths_proceeds_past_threshold(self):
        """Crossing the 3-path threshold MUST move past INCONCLUSIVE_WAITING.
        The exact verdict depends on path mix; this test only asserts
        the THRESHOLD COMPARISON fired correctly (NOT INCONCLUSIVE_WAITING)."""
        protocol = TriangulationProtocol()
        # Use 3 distinct independence_classes to ensure independence
        # condition can fire if other rules would upgrade.
        result = protocol.evaluate([
            _path(MethodClass.PROOF_BEARING, path_id="p1",
                  ic=IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION),
            _path(MethodClass.NUMERICAL, path_id="p2",
                  ic=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING),
            _path(MethodClass.CATALOG, path_id="p3",
                  ic=IndependenceClass.LMFDB_CATALOG),
        ])
        assert result.verdict is not TriangulationVerdict.INCONCLUSIVE_WAITING, (
            f"3 paths should proceed past INCONCLUSIVE_WAITING but got "
            f"{result.verdict!r}. The < threshold may have flipped to >."
        )

    def test_summary_text_under_threshold_mentions_path_count(self):
        """Defense-in-depth: the INCONCLUSIVE_WAITING summary should
        reference the actual path count (not None / generic). Catches
        return_constant_None mutations on the summary body."""
        protocol = TriangulationProtocol()
        result = protocol.evaluate([
            _path(MethodClass.PROOF_BEARING, path_id="p1"),
        ])
        assert result.summary is not None
        assert "1" in result.summary or "path" in result.summary.lower()
