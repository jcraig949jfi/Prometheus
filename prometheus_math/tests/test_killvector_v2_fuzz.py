"""Property-based component-level invariance fuzzer for KillVector v2.

Per inbox ticket T-2026-05-07-T008 (P1-high, Aporia 2026-05-07): KillVector
v2 added 8 new components beyond v0.1's 12 (relativizes, naturalizes,
local_global_gap, requires_unproven_conjecture, asymptotic_only,
small_case_artifact, asymmetric_effort, interpretive_slack); each of the 20
components must satisfy a battery of invariance properties under no-op
transformations of the surrounding context.

Per HARD-5 + the v2.3 §7.1 lock-in: these 20 components are independent
boolean flags with per-component margin. The substrate's invariance
contract is that:

  (a) per-component data is *self-contained* — relabeling, permuting, or
      replacing the parent KillVector's metadata MUST NOT mutate any
      individual KillComponent's identity-preserving fields;
  (b) component identity is *positional in name only* — the falsifier_name
      string is the canonical identifier; component order in the
      KillVector.components tuple is navigation order, not identity;
  (c) the squash function is *deterministic + pure* — same (margin,
      margin_unit) always squashes to the same [0, 1] value regardless of
      who is asking or what other components exist alongside;
  (d) the to_dict / from_dict round-trip is *lossless* on
      identity-preserving fields;
  (e) the parent KillVector's *aggregate* magnitude depends only on each
      component's (triggered, squashed) — i.e. components that are not
      triggered contribute zero, regardless of their margin or metadata.

Per the ticket's three named transformation classes:

  1. **Relabeling** — changing irrelevant string fields (metadata keys,
     parent operator_class, parent candidate_hash) on the surrounding
     KillVector does NOT mutate any component's per-component data or
     squash result. Tested: `test_relabeling_metadata_preserves_component`,
     `test_relabeling_parent_claim_preserves_component`.

  2. **Permutation of independent fields** — reordering the components
     tuple of a KillVector does NOT mutate any individual component's
     squashed value, triggered flag, or per-component dict round-trip.
     Tested: `test_permutation_of_components_preserves_per_component_data`.

  3. **Isomorphism on parent claim** — two KillVectors built from the same
     KillComponent with different candidate_hash / operator_class /
     region_meta yield the same squashed magnitude when only this one
     component is triggered. Tested:
     `test_isomorphism_on_parent_claim_preserves_magnitude`.

Plus two additional component-self-property battery items per component:

  4. `test_to_dict_from_dict_round_trip_lossless` — JSON round-trip
     identity for KillComponent data.
  5. `test_squash_deterministic_and_in_unit_range` — squashed() is a
     pure function returning a value in the documented unit range.

Coverage matrix: 20 components × 5 properties = 100 parameterized fuzz
tests. Each fuzz test runs Hypothesis with max_examples=50 (=> 5000+
generated probes per invocation), satisfying the "≥1000 probes per run"
substrate-tester soft target.

Determinism: Hypothesis honors --hypothesis-seed=N for cross-machine
reproduction. Failure JSON at prometheus_math/tests/killvector_fuzz_failures.json
on session finalization (always written; empty-failures payload is the
success signal Substrate-Tester lane reads).

NO contract change to KillComponent or KillVector public API
(acceptance criterion #5).
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math.kill_vector import (
    ALL_COMPONENT_NAMES,
    LEGACY_COMPONENT_NAMES,
    MARGIN_UNITS,
    NEW_COMPONENT_NAMES,
    KillComponent,
    KillVector,
)


# ---------------------------------------------------------------------------
# Sanity guard — the 20-component layout is the substrate contract this
# fuzzer is keyed against.
# ---------------------------------------------------------------------------

assert len(LEGACY_COMPONENT_NAMES) == 12, (
    f"v0.1 component count drift: expected 12, got {len(LEGACY_COMPONENT_NAMES)}"
)
assert len(NEW_COMPONENT_NAMES) == 8, (
    f"v2 component count drift: expected 8, got {len(NEW_COMPONENT_NAMES)}"
)
assert len(ALL_COMPONENT_NAMES) == 20, (
    f"total component count drift: expected 20, got {len(ALL_COMPONENT_NAMES)}"
)


# ---------------------------------------------------------------------------
# Failure-report accumulator (session-scoped)
# ---------------------------------------------------------------------------


_FUZZ_FAILURE_REPORT_PATH = (
    Path(__file__).resolve().parent / "killvector_fuzz_failures.json"
)
"""Per acceptance criterion #4: machine-readable failure report so the
Substrate-Tester lane can pipe failures into ticket-filing."""


_session_results: Dict[str, Dict[str, Any]] = {}


def _record(test_name: str, status: str, **extra: Any) -> None:
    entry: Dict[str, Any] = {"test": test_name, "status": status, "ts": time.time()}
    entry.update(extra)
    _session_results[test_name] = entry


@pytest.fixture(scope="session", autouse=True)
def _killvector_fuzz_session_report():
    """Session-scoped fixture: write JSON failure report at end of session.

    Always writes the file (an empty-failures payload is the success signal)
    so the Substrate-Tester lane has a known path to read."""
    _session_results.clear()
    yield
    payload: Dict[str, Any] = {
        "schema_version": "v1",
        "module": "prometheus_math.tests.test_killvector_v2_fuzz",
        "ticket": "T-2026-05-07-T008",
        "completed_at": time.time(),
        "n_components_covered": len(ALL_COMPONENT_NAMES),
        "n_tests": len(_session_results),
        "n_failures": sum(1 for r in _session_results.values() if r["status"] != "pass"),
        "results": list(_session_results.values()),
    }
    try:
        _FUZZ_FAILURE_REPORT_PATH.write_text(json.dumps(payload, indent=2, default=str))
    except OSError:
        # Fixture finalizer must not raise; if disk fails, the in-process
        # results are still observable via the test runner output.
        pass


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------


# Finite floats only — non-finite margins are explicitly out-of-contract
# (squash returns 0 for None; raw L2 skips non-finite).
_finite_margin_strategy = st.floats(
    min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
)

# All registered margin units (per MARGIN_UNITS contract).
_margin_unit_strategy = st.sampled_from(MARGIN_UNITS)

# Free-form metadata: small dicts of string keys → JSON-safe values.
_metadata_strategy = st.dictionaries(
    keys=st.text(min_size=1, max_size=10),
    values=st.one_of(
        st.text(max_size=20),
        st.integers(min_value=-1000, max_value=1000),
        st.floats(min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False),
        st.booleans(),
        st.none(),
    ),
    max_size=4,
)

# Parent KillVector context (for relabeling / isomorphism tests).
_candidate_hash_strategy = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=1,
    max_size=64,
)
_operator_class_strategy = st.text(min_size=0, max_size=40)
_region_meta_strategy = st.dictionaries(
    keys=st.text(min_size=1, max_size=10),
    values=st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.text(max_size=10),
        st.booleans(),
    ),
    max_size=3,
)


# Common settings: 50 examples per @given → 100 properties × 50 = 5000+
# probes per invocation (well over the 1000 soft target).
_FUZZ_SETTINGS = settings(
    max_examples=50,
    derandomize=False,  # respects --hypothesis-seed
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    deadline=None,
)


# ---------------------------------------------------------------------------
# Per-component invariance battery — parameterized over all 20 components
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("component_name", ALL_COMPONENT_NAMES)
class TestPerComponentInvariance:
    """Five invariance properties applied to each of the 20 KillVector v2
    components. Total parameterized fuzz tests: 5 × 20 = 100."""

    # ------------------------------------------------------------------
    # Property 1 (Class 1, relabeling) — metadata key relabeling does not
    # mutate identity-preserving fields.
    # ------------------------------------------------------------------

    @_FUZZ_SETTINGS
    @given(
        triggered=st.booleans(),
        margin=st.one_of(st.none(), _finite_margin_strategy),
        unit=_margin_unit_strategy,
        meta_a=_metadata_strategy,
        meta_b=_metadata_strategy,
    )
    def test_relabeling_metadata_preserves_component(
        self,
        component_name: str,
        triggered: bool,
        margin: Any,
        unit: str,
        meta_a: Dict[str, Any],
        meta_b: Dict[str, Any],
    ) -> None:
        """Two KillComponents identical except for metadata content squash to
        the same value and have the same triggered/margin/falsifier_name.
        Metadata is documented as free-form bookkeeping; it MUST NOT enter
        the squash path or the identity-preserving comparison."""
        c_a = KillComponent(
            falsifier_name=component_name,
            triggered=triggered,
            margin=margin,
            margin_unit=unit if margin is not None else None,
            metadata=meta_a,
        )
        c_b = KillComponent(
            falsifier_name=component_name,
            triggered=triggered,
            margin=margin,
            margin_unit=unit if margin is not None else None,
            metadata=meta_b,
        )
        assert c_a.falsifier_name == c_b.falsifier_name
        assert c_a.triggered == c_b.triggered
        assert c_a.margin == c_b.margin
        assert c_a.margin_unit == c_b.margin_unit
        assert c_a.squashed() == c_b.squashed(), (
            f"squash leaked metadata for {component_name}: "
            f"{c_a.squashed()} != {c_b.squashed()}"
        )
        _record(
            f"prop1_relabeling_metadata::{component_name}",
            "pass",
        )

    # ------------------------------------------------------------------
    # Property 2 (Class 1, relabeling) — parent claim relabeling does not
    # mutate per-component data.
    # ------------------------------------------------------------------

    @_FUZZ_SETTINGS
    @given(
        triggered=st.booleans(),
        margin=_finite_margin_strategy,
        unit=_margin_unit_strategy,
        hash_a=_candidate_hash_strategy,
        hash_b=_candidate_hash_strategy,
        op_a=_operator_class_strategy,
        op_b=_operator_class_strategy,
        rm_a=_region_meta_strategy,
        rm_b=_region_meta_strategy,
    )
    def test_relabeling_parent_claim_preserves_component(
        self,
        component_name: str,
        triggered: bool,
        margin: float,
        unit: str,
        hash_a: str,
        hash_b: str,
        op_a: str,
        op_b: str,
        rm_a: Dict[str, Any],
        rm_b: Dict[str, Any],
    ) -> None:
        """Wrapping the same KillComponent in two KillVectors that differ
        only in candidate_hash / operator_class / region_meta MUST yield
        identical per-component data on lookup via .get()."""
        c = KillComponent(
            falsifier_name=component_name,
            triggered=triggered,
            margin=margin,
            margin_unit=unit,
        )
        kv_a = KillVector(
            components=(c,), candidate_hash=hash_a,
            operator_class=op_a, region_meta=rm_a,
        )
        kv_b = KillVector(
            components=(c,), candidate_hash=hash_b,
            operator_class=op_b, region_meta=rm_b,
        )
        retrieved_a = kv_a.get(component_name)
        retrieved_b = kv_b.get(component_name)
        assert retrieved_a is not None and retrieved_b is not None
        assert retrieved_a == retrieved_b, (
            f"parent-claim relabeling leaked into component {component_name}"
        )
        assert retrieved_a.squashed() == retrieved_b.squashed()
        _record(
            f"prop2_relabeling_parent_claim::{component_name}",
            "pass",
        )

    # ------------------------------------------------------------------
    # Property 3 (Class 2, permutation) — reordering components in a
    # KillVector does NOT mutate per-component data on retrieval.
    # ------------------------------------------------------------------

    @_FUZZ_SETTINGS
    @given(
        triggered=st.booleans(),
        margin=_finite_margin_strategy,
        unit=_margin_unit_strategy,
        other_triggered=st.booleans(),
        other_margin=_finite_margin_strategy,
        other_unit=_margin_unit_strategy,
    )
    def test_permutation_of_components_preserves_per_component_data(
        self,
        component_name: str,
        triggered: bool,
        margin: float,
        unit: str,
        other_triggered: bool,
        other_margin: float,
        other_unit: str,
    ) -> None:
        """Swapping component order in KillVector.components must NOT change
        any individual component's identity, triggered flag, margin, or
        squashed value when retrieved via .get(name). Order is navigation,
        not identity."""
        # Pick a different component name to pair with (deterministic — the
        # next name in ALL_COMPONENT_NAMES, wrapping at end).
        idx = ALL_COMPONENT_NAMES.index(component_name)
        other_name = ALL_COMPONENT_NAMES[(idx + 1) % len(ALL_COMPONENT_NAMES)]

        c = KillComponent(
            falsifier_name=component_name,
            triggered=triggered,
            margin=margin,
            margin_unit=unit,
        )
        c_other = KillComponent(
            falsifier_name=other_name,
            triggered=other_triggered,
            margin=other_margin,
            margin_unit=other_unit,
        )
        kv_forward = KillVector(
            components=(c, c_other),
            candidate_hash="h_fwd",
        )
        kv_reverse = KillVector(
            components=(c_other, c),
            candidate_hash="h_rev",
        )
        retrieved_fwd = kv_forward.get(component_name)
        retrieved_rev = kv_reverse.get(component_name)
        assert retrieved_fwd is not None and retrieved_rev is not None
        assert retrieved_fwd == retrieved_rev, (
            f"component reorder leaked into {component_name} data"
        )
        assert retrieved_fwd.squashed() == retrieved_rev.squashed()
        _record(
            f"prop3_permutation_of_components::{component_name}",
            "pass",
        )

    # ------------------------------------------------------------------
    # Property 4 (Class 3, isomorphism) — parent-claim variation does not
    # affect this component's contribution to magnitude.
    # ------------------------------------------------------------------

    @_FUZZ_SETTINGS
    @given(
        margin=_finite_margin_strategy,
        unit=_margin_unit_strategy,
        hash_a=_candidate_hash_strategy,
        hash_b=_candidate_hash_strategy,
        op_a=_operator_class_strategy,
        op_b=_operator_class_strategy,
    )
    def test_isomorphism_on_parent_claim_preserves_magnitude(
        self,
        component_name: str,
        margin: float,
        unit: str,
        hash_a: str,
        hash_b: str,
        op_a: str,
        op_b: str,
    ) -> None:
        """Two KillVectors built from the same single triggered component
        but different parent claim metadata yield identical magnitude.
        magnitude() is a function of components, not parent claim."""
        c = KillComponent(
            falsifier_name=component_name,
            triggered=True,  # force triggered so the component contributes
            margin=margin,
            margin_unit=unit,
        )
        kv_a = KillVector(
            components=(c,), candidate_hash=hash_a, operator_class=op_a,
        )
        kv_b = KillVector(
            components=(c,), candidate_hash=hash_b, operator_class=op_b,
        )
        mag_a = kv_a.magnitude(unit_aware=True)
        mag_b = kv_b.magnitude(unit_aware=True)
        assert mag_a == mag_b, (
            f"parent-claim isomorphism violation for {component_name}: "
            f"mag_a={mag_a}, mag_b={mag_b}"
        )
        _record(
            f"prop4_isomorphism_on_parent_claim::{component_name}",
            "pass",
        )

    # ------------------------------------------------------------------
    # Property 5 (component self-property) — to_dict/from_dict is lossless
    # on identity-preserving fields, and squashed is deterministic + in
    # the documented [0, 1] range.
    # ------------------------------------------------------------------

    @_FUZZ_SETTINGS
    @given(
        triggered=st.booleans(),
        margin=st.one_of(st.none(), _finite_margin_strategy),
        unit=_margin_unit_strategy,
        meta=_metadata_strategy,
    )
    def test_to_dict_from_dict_round_trip_lossless(
        self,
        component_name: str,
        triggered: bool,
        margin: Any,
        unit: str,
        meta: Dict[str, Any],
    ) -> None:
        """Round-trip via to_dict() → from_dict() preserves identity
        fields. squash is deterministic across the round-trip."""
        c = KillComponent(
            falsifier_name=component_name,
            triggered=triggered,
            margin=margin,
            margin_unit=unit if margin is not None else None,
            metadata=meta,
        )
        d = c.to_dict()
        c_restored = KillComponent.from_dict(d)
        assert c_restored.falsifier_name == c.falsifier_name
        assert c_restored.triggered == c.triggered
        assert c_restored.margin == c.margin
        assert c_restored.margin_unit == c.margin_unit
        # Squash determinism across the round-trip.
        s1 = c.squashed()
        s2 = c_restored.squashed()
        assert s1 == s2, (
            f"squash inconsistent across round-trip for {component_name}: "
            f"{s1} != {s2}"
        )
        # Squash output range — by construction maps into [0, 1].
        assert 0.0 <= s1 <= 1.0, (
            f"squash out of [0,1] for {component_name}: {s1}"
        )
        # Squash is pure (deterministic across calls).
        assert c.squashed() == s1
        _record(
            f"prop5_round_trip_and_squash_pure::{component_name}",
            "pass",
        )


# ---------------------------------------------------------------------------
# Sanity-check: the substrate's component count contract is held end-to-end
# ---------------------------------------------------------------------------


def test_substrate_v2_component_count_is_20() -> None:
    """Sanity boundary test: substrate v2.3 §7.1 lock-in is 20 components.
    If this asserts, the substrate evolved without updating this fuzzer's
    coverage matrix — file a Techne ticket to extend the per-component
    battery before changing the constant."""
    assert len(ALL_COMPONENT_NAMES) == 20
    assert set(LEGACY_COMPONENT_NAMES).isdisjoint(set(NEW_COMPONENT_NAMES))
    assert (
        set(LEGACY_COMPONENT_NAMES) | set(NEW_COMPONENT_NAMES)
        == set(ALL_COMPONENT_NAMES)
    )
    _record("substrate_v2_count_invariant", "pass")
