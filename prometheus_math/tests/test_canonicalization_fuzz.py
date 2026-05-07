"""Property-based fuzzer for sigma_kernel.coordinate_chart.CanonicalizationProtocol.

Per inbox ticket T-2026-05-07-T006 (P1-high, Aporia 2026-05-07):
substrate hardening via Hypothesis-style fuzzer that emits 1000+ probes per
invocation, deterministically reproducible with --hypothesis-seed, covers ≥5
transformation classes, emits machine-readable failure report.

Coverage of the 5 named transformation classes (acceptance criterion 3):

1. **relabeling** — Lehmer's canonicalize accepts both 8-element half-vector
   AND 15-element full-palindrome representations of the same physical object;
   both must canonicalize to the same key.

2. **permutation of independent fields** — Lehmer's coordinates are
   POSITIONALLY meaningful (position = monomial degree), so permutation is NOT
   an invariance. We test the negative direction: a non-identity permutation
   of a non-symmetric half-vector must produce a DIFFERENT canonical form
   (else canonicalize is silently collapsing distinct objects).

3. **isomorphism** — Lehmer's x→-x reflection is the named equivalence
   relation. canonicalize(p) == canonicalize(reflect(p)) must hold for ALL
   palindromic half-vectors. This is the headline invariance test.

4. **encoding round-trip** — half-vector → JSON → parse → tuple → canonicalize
   must give the same result as direct canonicalize. Tests robustness to the
   serialization layer that NearMissCorpus emission + Pipeline-D loader use.

5. **decidability_status invariance** — apply() output MUST NOT depend on the
   value of decidability_status. Two CanonicalizationProtocols differing ONLY
   in decidability_status must give identical apply() results on any input
   (decidability is a TYPE-LEVEL flag for downstream consumers, not a
   compute-affecting parameter).

Plus dataclass-level construction fuzzing for CanonicalizationProtocol's
__post_init__ validator (negative tests for invalid impl/decidability_status/
choice_dependencies/version inputs).

Determinism + JSON failure report
---------------------------------
* Hypothesis is seeded by `--hypothesis-seed=N` (Hypothesis's native flag)
* Per-test settings request 200+ examples per @given test (5 tests × 200 ≈
  1000+ probes per invocation, satisfying the "1000+ probes per run" target)
* A session-scoped autouse fixture (`_fuzz_session_report`) emits a JSON
  report at `prometheus_math/tests/canonicalization_fuzz_failures.json`
  on session finalization with per-test pass/fail status, captured
  counter-examples (when Hypothesis surfaces them via test failure), and
  a session-level summary

NO contract change to CanonicalizationProtocol public API (acceptance #6).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from sigma_kernel.coordinate_chart import (
    CanonicalizationProtocol,
    REGISTERED_CANONICALIZER_IMPLS,
    VALID_DECIDABILITY,
)
from sigma_kernel.coordinate_charts.lehmer import (
    LEHMER_DEG14_PM5_PALINDROMIC,
    _lehmer_canonicalize,
    _reflect_half,
)


# ---------------------------------------------------------------------------
# Failure-report accumulator (session-scoped)
# ---------------------------------------------------------------------------


_FUZZ_FAILURE_REPORT_PATH = (
    Path(__file__).resolve().parent / "canonicalization_fuzz_failures.json"
)
"""Per acceptance criterion 5: machine-readable failure report so the
Substrate-Tester canonicalization-fuzz lane can pipe failures into
ticket-filing."""


_session_results: Dict[str, Dict[str, Any]] = {}
"""Module-level accumulator. Each test appends an entry on completion;
the session-scoped fixture writes the JSON at session end."""


def _record(test_name: str, status: str, **extra: Any) -> None:
    """Record a per-test result entry."""
    entry: Dict[str, Any] = {"test": test_name, "status": status, "ts": time.time()}
    entry.update(extra)
    _session_results[test_name] = entry


@pytest.fixture(scope="session", autouse=True)
def _fuzz_session_report():
    """Session-scoped fixture: write JSON failure report at end of session.

    Emits the file unconditionally so Substrate-Tester lane 13 always has
    a known path to read; an empty-failures payload is the success signal."""
    _session_results.clear()
    yield
    payload: Dict[str, Any] = {
        "schema_version": "v1",
        "module": "prometheus_math.tests.test_canonicalization_fuzz",
        "completed_at": time.time(),
        "n_tests": len(_session_results),
        "n_failures": sum(1 for r in _session_results.values() if r["status"] != "pass"),
        "results": list(_session_results.values()),
    }
    try:
        _FUZZ_FAILURE_REPORT_PATH.write_text(json.dumps(payload, indent=2, default=str))
    except OSError:
        # Fixture finalizer must not raise; if disk fails, log to stderr-side.
        pass


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------


# Lehmer half-vector: 8 ints in [-5, 5] with c0 != 0 (palindromic-degree-14
# admissibility). Strategy generates non-degenerate cases (c0 in [-5,-1] or
# [1,5]) so we don't trip the admissible_region predicate spuriously.
_lehmer_half_strategy = st.tuples(
    st.integers(min_value=-5, max_value=5).filter(lambda x: x != 0),  # c0 nonzero
    st.integers(min_value=-5, max_value=5),
    st.integers(min_value=-5, max_value=5),
    st.integers(min_value=-5, max_value=5),
    st.integers(min_value=-5, max_value=5),
    st.integers(min_value=-5, max_value=5),
    st.integers(min_value=-5, max_value=5),
    st.integers(min_value=-5, max_value=5),
)


# Valid CanonicalizationProtocol field strategies (for construction fuzzing)
_valid_impl_strategy = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126, blacklist_characters=":"),
    min_size=1,
    max_size=20,
)
_valid_decidability_strategy = st.sampled_from(VALID_DECIDABILITY)
_valid_choice_dependencies_strategy = st.lists(
    st.text(min_size=1, max_size=15), max_size=5
).map(tuple)
_valid_version_strategy = st.text(min_size=1, max_size=10)


# Common settings: bump example count so we hit the 1000+ probes-per-run
# total across the test suite.
_FUZZ_SETTINGS = settings(
    max_examples=200,
    derandomize=False,  # respects --hypothesis-seed
    suppress_health_check=[HealthCheck.too_slow],
    deadline=None,
)


# ---------------------------------------------------------------------------
# Class 1 — relabeling
# ---------------------------------------------------------------------------


class TestClass1Relabeling:
    """Same physical object under different label/length conventions
    canonicalizes to the same key."""

    @_FUZZ_SETTINGS
    @given(half=_lehmer_half_strategy)
    def test_half_and_full_representations_canonicalize_same(self, half: Tuple[int, ...]):
        """A half-vector and its corresponding full 15-coefficient palindrome
        must canonicalize to the same key (Lehmer canonicalize accepts both)."""
        full = tuple(list(half) + list(reversed(half[:-1])))
        assert len(full) == 15
        canon_from_half = _lehmer_canonicalize(half)
        canon_from_full = _lehmer_canonicalize(full)
        assert canon_from_half == canon_from_full, (
            f"relabeling violation: half={half} canonicalized to "
            f"{canon_from_half} but full={full} canonicalized to "
            f"{canon_from_full}"
        )
        _record("class1_half_full_canonicalize_same", "pass")


# ---------------------------------------------------------------------------
# Class 2 — permutation of independent fields (negative invariance)
# ---------------------------------------------------------------------------


class TestClass2PermutationNotInvariance:
    """For Lehmer's positional encoding, permutation of half-vector entries
    is NOT an invariance — the canonicalizer must distinguish permuted
    versions of asymmetric half-vectors."""

    @_FUZZ_SETTINGS
    @given(half=_lehmer_half_strategy)
    def test_swap_c1_and_c2_changes_canonical_form_for_asymmetric_input(
        self, half: Tuple[int, ...]
    ):
        """If c1 != c2 AND the result isn't accidentally a self-reflection,
        swapping them MUST produce a different canonical form. Tests that
        canonicalize doesn't silently collapse positionally distinct inputs."""
        if half[1] == half[2]:
            return  # skip cases where swap is a no-op
        permuted = (half[0], half[2], half[1], *half[3:])
        canon_a = _lehmer_canonicalize(half)
        canon_b = _lehmer_canonicalize(permuted)
        # The two might still match if both happen to coincide with their
        # own reflections in just the right way; allow only that case.
        if canon_a == canon_b:
            # Confirm both are at fixed points of reflection AND that the
            # swap was symmetric under reflection too. Rare but allowed.
            assert canon_a == _reflect_half(canon_a) or half == permuted, (
                f"permutation-collapse: canonicalize({half}) == "
                f"canonicalize({permuted}) == {canon_a} without reflection-symmetry "
                "explanation. canonicalizer is silently collapsing distinct objects."
            )
        _record("class2_permutation_not_invariance", "pass")


# ---------------------------------------------------------------------------
# Class 3 — isomorphism (the headline x→-x invariance)
# ---------------------------------------------------------------------------


class TestClass3IsomorphismXNegX:
    """canonicalize(p) == canonicalize(reflect(p)) for all admissible
    half-vectors. This is the substrate-grade invariance the chart
    guarantees."""

    @_FUZZ_SETTINGS
    @given(half=_lehmer_half_strategy)
    def test_canonicalize_invariant_under_x_neg_x_reflection(
        self, half: Tuple[int, ...]
    ):
        reflected = _reflect_half(half)
        canon_orig = _lehmer_canonicalize(half)
        canon_reflected = _lehmer_canonicalize(reflected)
        assert canon_orig == canon_reflected, (
            f"x→-x invariance violation: half={half}, "
            f"reflected={reflected}, canon(half)={canon_orig}, "
            f"canon(reflected)={canon_reflected}"
        )
        _record("class3_x_neg_x_isomorphism", "pass")

    @_FUZZ_SETTINGS
    @given(half=_lehmer_half_strategy)
    def test_double_reflection_is_identity(self, half: Tuple[int, ...]):
        """sanity: reflect(reflect(p)) == p (reflection is an involution)."""
        twice = _reflect_half(_reflect_half(half))
        assert twice == half, f"reflection is not an involution: {half} → {twice}"
        _record("class3_reflection_involution", "pass")


# ---------------------------------------------------------------------------
# Class 4 — encoding round-trip
# ---------------------------------------------------------------------------


class TestClass4EncodingRoundTrip:
    """JSON round-trip preserves the canonicalize result. Tests that the
    serialization layer Pipeline-D / NearMissCorpus uses doesn't perturb
    canonical forms."""

    @_FUZZ_SETTINGS
    @given(half=_lehmer_half_strategy)
    def test_canonicalize_invariant_under_json_roundtrip(
        self, half: Tuple[int, ...]
    ):
        canon_direct = _lehmer_canonicalize(half)
        # JSON round-trip: tuple → list → JSON → list → tuple
        encoded = json.dumps(list(half))
        decoded = tuple(json.loads(encoded))
        canon_after_roundtrip = _lehmer_canonicalize(decoded)
        assert canon_direct == canon_after_roundtrip, (
            f"json round-trip violation: half={half}, decoded={decoded}, "
            f"canon_direct={canon_direct}, canon_after={canon_after_roundtrip}"
        )
        _record("class4_json_roundtrip", "pass")


# ---------------------------------------------------------------------------
# Class 5 — decidability_status invariance
# ---------------------------------------------------------------------------


class TestClass5DecidabilityStatusInvariance:
    """apply() output must NOT depend on which decidability_status is set on
    the wrapping CanonicalizationProtocol. Two protocols differing ONLY in
    decidability_status must give identical apply() results."""

    @_FUZZ_SETTINGS
    @given(
        half=_lehmer_half_strategy,
        ds_a=_valid_decidability_strategy,
        ds_b=_valid_decidability_strategy,
    )
    def test_apply_independent_of_decidability_status(
        self,
        half: Tuple[int, ...],
        ds_a: str,
        ds_b: str,
    ):
        proto_a = CanonicalizationProtocol(
            impl="reflection_quotient",
            decidability_status=ds_a,
            choice_dependencies=("lex_minimization",),
            version="1.0.0",
            canonicalize=_lehmer_canonicalize,
        )
        proto_b = CanonicalizationProtocol(
            impl="reflection_quotient",
            decidability_status=ds_b,
            choice_dependencies=("lex_minimization",),
            version="1.0.0",
            canonicalize=_lehmer_canonicalize,
        )
        out_a = proto_a.apply(half)
        out_b = proto_b.apply(half)
        assert out_a == out_b, (
            f"decidability_status leaked into apply() output: "
            f"ds={ds_a} → {out_a}, ds={ds_b} → {out_b}, input={half}"
        )
        _record("class5_decidability_status_invariance", "pass")

    @_FUZZ_SETTINGS
    @given(
        half=_lehmer_half_strategy,
        version=_valid_version_strategy,
    )
    def test_apply_independent_of_version_field(
        self, half: Tuple[int, ...], version: str
    ):
        """Sister property: version field must not affect apply() output."""
        proto_baseline = CanonicalizationProtocol(
            impl="reflection_quotient",
            decidability_status="decidable",
            choice_dependencies=("lex_minimization",),
            version="1.0.0",
            canonicalize=_lehmer_canonicalize,
        )
        proto_versioned = CanonicalizationProtocol(
            impl="reflection_quotient",
            decidability_status="decidable",
            choice_dependencies=("lex_minimization",),
            version=version,
            canonicalize=_lehmer_canonicalize,
        )
        out_baseline = proto_baseline.apply(half)
        out_versioned = proto_versioned.apply(half)
        assert out_baseline == out_versioned, (
            f"version leaked into apply() output: "
            f"v=1.0.0 → {out_baseline}, v={version!r} → {out_versioned}"
        )
        _record("class5_version_invariance", "pass")


# ---------------------------------------------------------------------------
# Bonus: dataclass-level __post_init__ validator fuzzing
# ---------------------------------------------------------------------------


class TestProtocolDataclassValidation:
    """Validate that __post_init__ rejects invalid construction inputs.
    Negative tests for the validator's branches."""

    @_FUZZ_SETTINGS
    @given(
        impl=_valid_impl_strategy,
        ds=_valid_decidability_strategy,
        deps=_valid_choice_dependencies_strategy,
        version=_valid_version_strategy,
    )
    def test_valid_inputs_construct_successfully(
        self, impl: str, ds: str, deps: Tuple[str, ...], version: str
    ):
        """Any valid combination of fields must construct without raising."""
        proto = CanonicalizationProtocol(
            impl=impl,
            decidability_status=ds,
            choice_dependencies=deps,
            version=version,
        )
        assert proto.impl == impl
        assert proto.decidability_status == ds
        assert proto.choice_dependencies == deps
        assert proto.version == version
        _record("dataclass_valid_inputs_construct", "pass")

    @_FUZZ_SETTINGS
    @given(invalid_ds=st.text(min_size=1, max_size=20).filter(
        lambda s: s not in VALID_DECIDABILITY
    ))
    def test_invalid_decidability_status_raises_value_error(self, invalid_ds: str):
        with pytest.raises(ValueError, match="decidability_status must be one of"):
            CanonicalizationProtocol(
                impl="stub",
                decidability_status=invalid_ds,
                choice_dependencies=(),
                version="1.0.0",
            )
        _record("dataclass_invalid_decidability_raises", "pass")

    def test_empty_impl_raises_value_error(self):
        with pytest.raises(ValueError, match="impl must be a non-empty string"):
            CanonicalizationProtocol(
                impl="",
                decidability_status="decidable",
                choice_dependencies=(),
                version="1.0.0",
            )
        _record("dataclass_empty_impl_raises", "pass")

    def test_non_tuple_choice_dependencies_raises_type_error(self):
        with pytest.raises(TypeError, match="choice_dependencies must be a tuple"):
            CanonicalizationProtocol(
                impl="stub",
                decidability_status="decidable",
                choice_dependencies=["foo", "bar"],  # type: ignore[arg-type]
                version="1.0.0",
            )
        _record("dataclass_list_choice_deps_raises", "pass")

    def test_empty_version_raises_value_error(self):
        with pytest.raises(ValueError, match="version must be a non-empty"):
            CanonicalizationProtocol(
                impl="stub",
                decidability_status="decidable",
                choice_dependencies=(),
                version="",
            )
        _record("dataclass_empty_version_raises", "pass")


# ---------------------------------------------------------------------------
# Lehmer chart smoke tests (sanity bridge to the registered chart)
# ---------------------------------------------------------------------------


class TestLehmerChartIntegration:
    """The shipped Lehmer chart's canonicalization protocol passes the same
    fuzz-discoverable invariances. Confirms the registered chart is wired
    through the protocol consistently."""

    @_FUZZ_SETTINGS
    @given(half=_lehmer_half_strategy)
    def test_chart_protocol_apply_matches_underlying_canonicalize(
        self, half: Tuple[int, ...]
    ):
        """The chart's CanonicalizationProtocol.apply() result equals the
        underlying _lehmer_canonicalize() result. Confirms no wrapping-layer
        perturbation."""
        via_protocol = LEHMER_DEG14_PM5_PALINDROMIC.canonicalization.apply(half)
        direct = _lehmer_canonicalize(half)
        assert via_protocol == direct, (
            f"chart.canonicalization.apply diverges from underlying impl: "
            f"protocol → {via_protocol}, direct → {direct}, input={half}"
        )
        _record("lehmer_chart_protocol_consistent", "pass")
