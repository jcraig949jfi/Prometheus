"""Factory-method return-value coverage for sigma_kernel.method_spec.

Closes the second open finding from substrate-tester fire #49 Lane 16
mutation testing: factory-method `return_constant_None` mutations on
`MethodSpec.from_string` (lines 256/267/270) and `MethodSpec.to_string`
(line 280) survived because the contract-change-window test suite
(test_enum_validation_2026_05_08.py) asserts what factories ACCEPT
(input validation) but not what they RETURN (output non-None +
correctly-shaped).

This file ships explicit return-value assertions for each factory
return path, designed to FAIL when a factory body is mutated to
`return None`.

**Sister file:** `test_frozen_baseline_manifest.py` (fire #50 closure
of the OTHER fire #49 finding).

**Source ticket:** T-2026-05-08-ST-fire51-001 (Techne; closes
ST-fire49-001 factory-return-value gap).

**Verification:** harness `charon/diagnostics/substrate_tester_fire_51_harness.py`
empirically confirms each `return X` -> `return None` mutation now
fails this test suite.
"""
from __future__ import annotations

import pytest

from sigma_kernel.method_spec import IndependenceClass, MethodSpec


# ---------------------------------------------------------------------------
# from_string return paths (lines 256/267/270 mutation sites)
# ---------------------------------------------------------------------------


class TestFromStringReturnPaths:
    """Each factory return path is exercised by at least one test that
    asserts the return value is non-None AND has expected structural
    shape. This catches `return cls(...)` -> `return None` mutations."""

    def test_known_engine_prefix_returns_non_None(self):
        """Path 1 (line 256): <known_engine>_<rest> — known engine prefix."""
        spec = MethodSpec.from_string("mpmath_polyroots")
        assert spec is not None
        assert isinstance(spec, MethodSpec)
        assert spec.engine == "mpmath"
        assert spec.strategy == "polyroots"

    def test_known_engine_prefix_with_multipart_strategy(self):
        """Path 1 with multi-token tail."""
        spec = MethodSpec.from_string("magma_factor_first")
        assert spec is not None
        assert isinstance(spec, MethodSpec)
        # Note: substrate's parser prefers the right-anchored multi-token
        # strategy match over the left-anchored single-token one. Per
        # comment at line 259-260: 'magma_factor_first' resolves to
        # engine='magma', strategy='factor_first' (right-anchored
        # _KNOWN_STRATEGIES match).
        assert spec.engine == "magma"
        assert spec.strategy == "factor_first"

    def test_known_strategy_suffix_returns_non_None(self):
        """Path 2 (line 267): <rest>_<known_strategy_suffix> — strategy
        suffix is recognized; engine = whatever the prefix is. The path
        fires when the head is NOT in _KNOWN_ENGINES."""
        spec = MethodSpec.from_string("xyz_symbolic")
        assert spec is not None
        assert isinstance(spec, MethodSpec)
        assert spec.engine == "xyz"
        assert spec.strategy == "symbolic"

    def test_unknown_engine_unknown_strategy_returns_non_None(self):
        """Path 3 (line 270): fallback — entire string becomes engine,
        strategy='direct'. Catches `return cls(engine=norm, strategy="direct")`
        -> `return None` mutation."""
        spec = MethodSpec.from_string("entirely_unknown_thing")
        assert spec is not None
        assert isinstance(spec, MethodSpec)
        assert spec.strategy == "direct"

    def test_default_independence_class_unknown(self):
        """All factory return paths construct with default
        independence_class=UNKNOWN per docstring."""
        for input_str in ("mpmath_polyroots", "xyz_symbolic", "entirely_unknown"):
            spec = MethodSpec.from_string(input_str)
            assert spec is not None
            assert spec.independence_class is IndependenceClass.UNKNOWN, (
                f"from_string({input_str!r}) returned independence_class="
                f"{spec.independence_class!r}; expected UNKNOWN per docstring."
            )

    def test_empty_input_raises_not_returns_None(self):
        """Empty input must raise ValueError, not silently return None."""
        with pytest.raises(ValueError):
            MethodSpec.from_string("")

    def test_non_string_input_raises_not_returns_None(self):
        """Non-string input must raise TypeError, not silently return None."""
        with pytest.raises(TypeError):
            MethodSpec.from_string(12345)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# to_string return value (line 280 mutation site)
# ---------------------------------------------------------------------------


class TestToStringReturnValue:
    """Catches `return f"{self.engine}_{self.strategy}"` -> `return None`
    mutation."""

    def test_to_string_returns_non_None(self):
        spec = MethodSpec(
            engine="mpmath", strategy="polyroots",
            independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
            version="1.0.0",
        )
        result = spec.to_string()
        assert result is not None

    def test_to_string_returns_str_type(self):
        spec = MethodSpec(engine="x", strategy="y")
        assert isinstance(spec.to_string(), str)

    def test_to_string_format_matches_engine_underscore_strategy(self):
        """Format contract: f"{engine}_{strategy}" verbatim."""
        spec = MethodSpec(engine="sympy", strategy="factor_list")
        assert spec.to_string() == "sympy_factor_list"


# ---------------------------------------------------------------------------
# from_string + to_string roundtrip
# ---------------------------------------------------------------------------


class TestFactoryRoundtrip:
    """Roundtrip: known-engine specs survive a `to_string -> from_string`
    cycle (modulo the documented lossiness on independence_class)."""

    def test_known_engine_roundtrips(self):
        spec = MethodSpec(
            engine="mpmath", strategy="polyroots",
            independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
            version="1.0.0",
        )
        s = spec.to_string()
        assert s is not None
        rebuilt = MethodSpec.from_string(s)
        assert rebuilt is not None
        assert rebuilt.engine == spec.engine
        assert rebuilt.strategy == spec.strategy
        # Documented lossiness: independence_class drops to UNKNOWN.
        assert rebuilt.independence_class is IndependenceClass.UNKNOWN
