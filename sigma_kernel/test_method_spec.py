"""Tests for sigma_kernel.method_spec — P3 Tier 1 primitive (substrate v2.3 §6.2).

Covers:
  * MethodSpec construction + defaults
  * from_string / to_string round-tripping for the legacy flat shape
  * is_independent_of triangulation rule (substrate v2.3 §6.2 P3)
  * compute_intensional_hash determinism + whitespace/comment insensitivity
  * compute_behavioural_hash determinism + exception fingerprinting
  * DriftChannel construction
  * IndependenceClass enum membership invariants
"""
from __future__ import annotations

import pytest

from sigma_kernel.method_spec import (
    DriftChannel,
    IndependenceClass,
    MethodSpec,
    compute_behavioural_hash,
    compute_intensional_hash,
)


# ---------------------------------------------------------------------------
# IndependenceClass enum
# ---------------------------------------------------------------------------


def test_independence_class_has_all_canonical_values():
    """v2.3 §6.2 P3 lists 13 canonical independence classes including UNKNOWN."""
    expected = {
        "mpmath_polynomial_factorization",
        "mpmath_numerical_root_finding",
        "sympy_symbolic_factorization",
        "pari_number_field",
        "sage_elliptic_curve",
        "numpy_linear_algebra",
        "mahler_lookup_catalog",
        "lmfdb_catalog",
        "oeis_catalog",
        "literature_cross_check",
        "perturbation_robustness",
        "clustering_boundary",
        "unknown",
    }
    assert {member.value for member in IndependenceClass} == expected
    assert len(IndependenceClass) == 13


def test_independence_class_is_string_compatible():
    """str-mixin → enum members compare equal to their underlying string."""
    assert IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION == "mpmath_polynomial_factorization"
    assert IndependenceClass.UNKNOWN == "unknown"


# ---------------------------------------------------------------------------
# MethodSpec construction + defaults
# ---------------------------------------------------------------------------


def test_method_spec_construction_minimal():
    spec = MethodSpec(engine="mpmath", strategy="factor_first")
    assert spec.engine == "mpmath"
    assert spec.strategy == "factor_first"
    assert spec.precision_dps is None
    assert spec.version == "1.0.0"
    assert spec.parameters == {}
    assert spec.fallback_chain == ()
    assert spec.independence_class is IndependenceClass.UNKNOWN
    assert spec.drift_channel is None


def test_method_spec_construction_full():
    """All fields populated — sanity check for downstream consumers."""
    drift = DriftChannel(
        intensional_hash="a" * 64,
        behavioural_hash="b" * 64,
        fingerprint_inputs=(1, 2, 3),
    )
    fallback = MethodSpec(engine="mpmath", strategy="direct")
    spec = MethodSpec(
        engine="mpmath",
        strategy="factor_first",
        precision_dps=60,
        version="2.0.1",
        parameters={"max_steps": 1000},
        fallback_chain=(fallback,),
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        drift_channel=drift,
    )
    assert spec.precision_dps == 60
    assert spec.version == "2.0.1"
    assert spec.parameters == {"max_steps": 1000}
    assert spec.fallback_chain == (fallback,)
    assert spec.independence_class is IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION
    assert spec.drift_channel is drift


def test_method_spec_is_frozen():
    """Frozen dataclass: mutation must raise."""
    spec = MethodSpec(engine="mpmath", strategy="direct")
    with pytest.raises(Exception):  # FrozenInstanceError, but be tolerant
        spec.engine = "numpy"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# from_string parsing
# ---------------------------------------------------------------------------


def test_from_string_known_engine_multitoken_strategy():
    spec = MethodSpec.from_string("mpmath_factor_first")
    assert spec.engine == "mpmath"
    assert spec.strategy == "factor_first"
    assert spec.independence_class is IndependenceClass.UNKNOWN


def test_from_string_known_engine_simple_strategy():
    spec = MethodSpec.from_string("numpy_eigvals")
    assert spec.engine == "numpy"
    assert spec.strategy == "eigvals"


def test_from_string_unrecognized_engine_with_known_strategy_suffix():
    """`<unknown>_<known_strategy>` → engine=unknown_prefix, strategy=known."""
    spec = MethodSpec.from_string("foobar_factor_first")
    # 'foobar' is not a known engine, so partition-on-first-_ falls through;
    # 'factor_first' matches a known strategy suffix → engine='foobar'.
    assert spec.engine == "foobar"
    assert spec.strategy == "factor_first"


def test_from_string_falls_back_gracefully_on_unrecognized_blob():
    spec = MethodSpec.from_string("totallymadeupblob")
    assert spec.engine == "totallymadeupblob"
    assert spec.strategy == "direct"
    assert spec.independence_class is IndependenceClass.UNKNOWN


def test_from_string_normalizes_whitespace_and_case():
    spec = MethodSpec.from_string("  Mpmath_Factor_First  ")
    assert spec.engine == "mpmath"
    assert spec.strategy == "factor_first"


def test_from_string_rejects_empty_and_non_str():
    with pytest.raises(ValueError):
        MethodSpec.from_string("")
    with pytest.raises(TypeError):
        MethodSpec.from_string(123)  # type: ignore[arg-type]


def test_to_string_legacy_round_trip():
    """`to_string()` returns the legacy flat shape; from_string ⊕ to_string
    is a fixed point on the (engine, strategy) projection for recognized
    pairs."""
    for legacy in ("mpmath_factor_first", "numpy_eigvals", "sympy_factor"):
        spec = MethodSpec.from_string(legacy)
        assert spec.to_string() == legacy


def test_to_string_drops_extra_metadata_intentionally():
    spec = MethodSpec(
        engine="mpmath",
        strategy="direct",
        precision_dps=100,
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
    )
    assert spec.to_string() == "mpmath_direct"


# ---------------------------------------------------------------------------
# is_independent_of triangulation rule
# ---------------------------------------------------------------------------


def test_is_independent_same_class_returns_false():
    a = MethodSpec(
        engine="mpmath",
        strategy="factor_first",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
    )
    b = MethodSpec(
        engine="mpmath",
        strategy="direct",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
    )
    assert a.is_independent_of(b) is False
    assert b.is_independent_of(a) is False  # symmetry


def test_is_independent_different_class_returns_true():
    a = MethodSpec(
        engine="mpmath",
        strategy="factor_first",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
    )
    b = MethodSpec(
        engine="sympy",
        strategy="factor",
        independence_class=IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
    )
    assert a.is_independent_of(b) is True
    assert b.is_independent_of(a) is True


def test_is_independent_unknown_with_different_behavioural_hash_returns_true():
    drift_a = DriftChannel(intensional_hash="x" * 64, behavioural_hash="aaa")
    drift_b = DriftChannel(intensional_hash="y" * 64, behavioural_hash="bbb")
    a = MethodSpec(engine="custom", strategy="direct", drift_channel=drift_a)
    b = MethodSpec(engine="custom", strategy="direct", drift_channel=drift_b)
    assert a.is_independent_of(b) is True


def test_is_independent_unknown_with_same_behavioural_hash_returns_false():
    """Same behaviour → same algorithm dressed differently → NOT independent."""
    drift_a = DriftChannel(intensional_hash="x" * 64, behavioural_hash="same")
    drift_b = DriftChannel(intensional_hash="y" * 64, behavioural_hash="same")
    a = MethodSpec(engine="custom", strategy="direct", drift_channel=drift_a)
    b = MethodSpec(engine="custom", strategy="alt", drift_channel=drift_b)
    assert a.is_independent_of(b) is False


def test_is_independent_unknown_without_drift_channel_returns_false():
    """Cannot prove independence → conservative default."""
    a = MethodSpec(engine="custom", strategy="direct")
    b = MethodSpec(engine="custom", strategy="other")
    assert a.is_independent_of(b) is False


def test_is_independent_one_known_one_unknown_falls_back_to_behavioural():
    """If only one side has a class, fall through to behavioural hash check."""
    drift_a = DriftChannel(intensional_hash="x" * 64, behavioural_hash="hashA")
    drift_b = DriftChannel(intensional_hash="y" * 64, behavioural_hash="hashB")
    a = MethodSpec(
        engine="mpmath",
        strategy="direct",
        independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        drift_channel=drift_a,
    )
    b = MethodSpec(engine="custom", strategy="direct", drift_channel=drift_b)
    assert a.is_independent_of(b) is True


def test_is_independent_rejects_non_method_spec():
    a = MethodSpec(engine="mpmath", strategy="direct")
    with pytest.raises(TypeError):
        a.is_independent_of("not a methodspec")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# compute_intensional_hash
# ---------------------------------------------------------------------------


def test_compute_intensional_hash_deterministic_on_string():
    src = "def f(x):\n    return x + 1\n"
    h1 = compute_intensional_hash(src)
    h2 = compute_intensional_hash(src)
    assert h1 == h2
    assert len(h1) == 64  # sha256 hex


def test_compute_intensional_hash_ignores_whitespace():
    """Cosmetic whitespace re-flow must not perturb the intensional hash."""
    src_a = "def f(x):\n    return x + 1\n"
    src_b = "def   f(x):\n  return    x  +  1\n"
    assert compute_intensional_hash(src_a) == compute_intensional_hash(src_b)


def test_compute_intensional_hash_ignores_comments():
    """Comment edits are cosmetic — they must not change the hash."""
    src_a = "def f(x):\n    # original\n    return x + 1\n"
    src_b = "def f(x):\n    # rewritten comment, totally different\n    return x + 1\n"
    assert compute_intensional_hash(src_a) == compute_intensional_hash(src_b)


def test_compute_intensional_hash_distinguishes_real_changes():
    """Behavioural rewrites MUST perturb the intensional hash."""
    src_a = "def f(x):\n    return x + 1\n"
    src_b = "def f(x):\n    return x + 2\n"
    assert compute_intensional_hash(src_a) != compute_intensional_hash(src_b)


def test_compute_intensional_hash_accepts_callable():
    def example(x):
        return x * 2

    h = compute_intensional_hash(example)
    assert isinstance(h, str)
    assert len(h) == 64


def test_compute_intensional_hash_rejects_non_str_non_callable():
    with pytest.raises(TypeError):
        compute_intensional_hash(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# compute_behavioural_hash
# ---------------------------------------------------------------------------


def test_compute_behavioural_hash_deterministic():
    def square(x):
        return x * x

    h1, inputs1 = compute_behavioural_hash(square, [1, 2, 3])
    h2, inputs2 = compute_behavioural_hash(square, [1, 2, 3])
    assert h1 == h2
    assert inputs1 == (1, 2, 3)
    assert inputs2 == (1, 2, 3)


def test_compute_behavioural_hash_distinguishes_different_callables():
    def f(x):
        return x + 1

    def g(x):
        return x + 2

    h_f, _ = compute_behavioural_hash(f, [1, 2, 3])
    h_g, _ = compute_behavioural_hash(g, [1, 2, 3])
    assert h_f != h_g


def test_compute_behavioural_hash_same_io_same_hash():
    """Two callables with the same I/O on the probe suite → same hash."""
    def f(x):
        return x * 2

    def g(x):
        return x + x  # mathematically identical on ints

    h_f, _ = compute_behavioural_hash(f, [1, 2, 3])
    h_g, _ = compute_behavioural_hash(g, [1, 2, 3])
    assert h_f == h_g


def test_compute_behavioural_hash_records_exception_class():
    """Methods that raise have the exception class folded into the hash so
    `raises ValueError` is itself a stable, distinguishable behaviour."""
    def raiser(x):
        if x == 0:
            raise ValueError("nope")
        return x

    h1, _ = compute_behavioural_hash(raiser, [0, 1])
    h2, _ = compute_behavioural_hash(raiser, [0, 1])
    assert h1 == h2

    def raiser_other(x):
        if x == 0:
            raise TypeError("different exception")
        return x

    h3, _ = compute_behavioural_hash(raiser_other, [0, 1])
    assert h1 != h3  # exception class change is detectable


def test_compute_behavioural_hash_input_order_matters():
    """Reordering inputs reorders pairs → different hash. This is a
    deliberate choice (probe suites are ordered specifications)."""
    def f(x):
        return x

    h1, _ = compute_behavioural_hash(f, [1, 2, 3])
    h2, _ = compute_behavioural_hash(f, [3, 2, 1])
    assert h1 != h2


def test_compute_behavioural_hash_rejects_non_callable():
    with pytest.raises(TypeError):
        compute_behavioural_hash("not callable", [1, 2])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# DriftChannel
# ---------------------------------------------------------------------------


def test_drift_channel_construction_with_defaults():
    dc = DriftChannel(intensional_hash="a" * 64, behavioural_hash="b" * 64)
    assert dc.intensional_hash == "a" * 64
    assert dc.behavioural_hash == "b" * 64
    assert dc.fingerprint_inputs == ()


def test_drift_channel_with_fingerprint_inputs():
    dc = DriftChannel(
        intensional_hash="a" * 64,
        behavioural_hash="b" * 64,
        fingerprint_inputs=(1, 2, 3),
    )
    assert dc.fingerprint_inputs == (1, 2, 3)


def test_drift_channel_is_frozen():
    dc = DriftChannel(intensional_hash="a", behavioural_hash="b")
    with pytest.raises(Exception):
        dc.intensional_hash = "c"  # type: ignore[misc]
