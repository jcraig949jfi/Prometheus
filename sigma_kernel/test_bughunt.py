"""sigma_kernel/test_bughunt.py — bug-hunt probes for the kernel-side
pivot stack (bind_eval, bind_eval_v2, residuals).

Each test docstring records:
  * which module + function it probes
  * which of the seven bug-hunt categories it falls in
  * NEW / regression status

Probes are ADDITIVE; they do not modify or supersede existing tests in
this directory. Hypothesis tests use settings(deadline=10000,
max_examples=50) to keep CI fast.

Categories (from the bug-hunt protocol):
  1 = Boundary value analysis
  2 = Equivalence class partitioning
  3 = Property-based fuzzing with Hypothesis
  4 = Adversarial inputs
  5 = State-machine testing
  6 = Differential testing
  7 = Error injection
"""
from __future__ import annotations

import json
import math
import threading
import time

import pytest

try:
    from hypothesis import given, settings, strategies as st
    HAS_HYPOTHESIS = True
except ImportError:  # pragma: no cover
    HAS_HYPOTHESIS = False
    pytest.skip("hypothesis not installed", allow_module_level=True)

from sigma_kernel.sigma_kernel import (
    Capability,
    CapabilityError,
    SigmaKernel,
    Tier,
    Verdict,
)
from sigma_kernel.bind_eval import (
    BindEvalExtension,
    Binding,
    BindingError,
    BudgetExceeded,
    CostModel,
    EvalError,
    Evaluation,
)

# Re-import the bind_eval helpers properly.
from sigma_kernel.bind_eval import BindEvalExtension as _BEX
from sigma_kernel import bind_eval as _be_mod
from sigma_kernel import residuals as _res_mod
from sigma_kernel.residuals import (
    BudgetExceeded as ResBudgetExceeded,
    RefinementBlocked,
    ResidualExtension,
    ResidualValidationError,
)


_HASH_LEN = 8  # sigma_kernel.bind_eval truncates output_repr's hash here


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh_kernel_with_bind() -> tuple[SigmaKernel, BindEvalExtension]:
    k = SigmaKernel(":memory:")
    return k, BindEvalExtension(k)


def _fresh_kernel_with_residuals() -> tuple[SigmaKernel, ResidualExtension]:
    k = SigmaKernel(":memory:")
    return k, ResidualExtension(k)


# ---------------------------------------------------------------------------
# Category 1 — Boundary value analysis
# ---------------------------------------------------------------------------


class TestBoundaryValues:

    def test_costmodel_zero_max_seconds_rejects_any_real_call(self):
        """bind_eval.CostModel — Cat 1 — NEW. max_seconds=0 should always
        BudgetExceed because any wall-clock work takes > 0s."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        b = ext.BIND(callable_ref="math:sqrt", cost_model=CostModel(max_seconds=0.0), cap=cap)
        cap2 = k.mint_capability("EvalCap")
        with pytest.raises(BudgetExceeded):
            ext.EVAL(b.symbol.name, b.symbol.version, args=[4.0], cap=cap2)

    def test_costmodel_negative_max_seconds_always_fails(self):
        """bind_eval.CostModel — Cat 1 — NEW. Negative max_seconds is
        documented as not validated; EVAL must still fail BudgetExceeded
        rather than silently accept."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        b = ext.BIND(callable_ref="math:sqrt", cost_model=CostModel(max_seconds=-1.0), cap=cap)
        cap2 = k.mint_capability("EvalCap")
        with pytest.raises(BudgetExceeded):
            ext.EVAL(b.symbol.name, b.symbol.version, args=[4.0], cap=cap2)

    def test_costmodel_nan_oracle_calls_rejected_at_construction(self):
        """bind_eval.CostModel.to_dict — Cat 1 — NEW. NaN max_oracle_calls
        is rejected by ValueError at to_dict (cannot int(nan))."""
        cm = CostModel(max_oracle_calls=float("nan"))
        with pytest.raises(ValueError):
            cm.to_dict()

    def test_costmodel_huge_memory_passes_unconstrained(self):
        """bind_eval.CostModel — Cat 1 — NEW. max_memory_mb=1e18 must not
        crash int casting / serialisation."""
        cm = CostModel(max_memory_mb=1e18)
        d = cm.to_dict()
        assert d["max_memory_mb"] == 1e18

    def test_residual_magnitude_zero_classifies_noise(self):
        """residuals._classify_residual — Cat 1 — NEW. magnitude==0.0 must
        short-circuit to 'noise' per Rule 1."""
        k, ext = _fresh_kernel_with_residuals()
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=0.0,
            surviving_subset={"n": 5}, failure_shape={"kind": "x"},
            instrument_id="I", cost_budget=1.0,
        )
        assert r.classification == "noise"

    def test_residual_magnitude_one_is_valid_boundary(self):
        """residuals.record_residual — Cat 1 — NEW. magnitude==1.0 is the
        upper boundary; must be accepted, not rejected."""
        k, ext = _fresh_kernel_with_residuals()
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=1.0,
            surviving_subset={"n": 5}, failure_shape={"kind": "x"},
            instrument_id="I", cost_budget=1.0,
        )
        assert r.magnitude == 1.0

    def test_residual_magnitude_above_one_rejected(self):
        """residuals.record_residual — Cat 1 — NEW. magnitude=1+epsilon
        must raise ResidualValidationError."""
        k, ext = _fresh_kernel_with_residuals()
        with pytest.raises(ResidualValidationError):
            ext.record_residual(
                parent_claim_id="p", test_id="t", magnitude=1.0 + 1e-12,
                surviving_subset={"n": 5}, failure_shape={"kind": "x"},
                instrument_id="I", cost_budget=1.0,
            )

    def test_residual_magnitude_negative_rejected(self):
        """residuals.record_residual — Cat 1 — NEW. -1e-12 magnitude
        rejected."""
        k, ext = _fresh_kernel_with_residuals()
        with pytest.raises(ResidualValidationError):
            ext.record_residual(
                parent_claim_id="p", test_id="t", magnitude=-1e-12,
                surviving_subset={"n": 5}, failure_shape={"kind": "x"},
                instrument_id="I", cost_budget=1.0,
            )

    def test_residual_magnitude_nan_rejected(self):
        """residuals.record_residual — Cat 1 — NEW. NaN magnitude must be
        rejected; the comparison `0.0 <= NaN <= 1.0` is False so the
        guard fires."""
        k, ext = _fresh_kernel_with_residuals()
        with pytest.raises(ResidualValidationError):
            ext.record_residual(
                parent_claim_id="p", test_id="t", magnitude=float("nan"),
                surviving_subset={"n": 5}, failure_shape={"kind": "x"},
                instrument_id="I", cost_budget=1.0,
            )

    def test_residual_magnitude_inf_rejected(self):
        """residuals.record_residual — Cat 1 — NEW."""
        k, ext = _fresh_kernel_with_residuals()
        with pytest.raises(ResidualValidationError):
            ext.record_residual(
                parent_claim_id="p", test_id="t", magnitude=float("inf"),
                surviving_subset={"n": 5}, failure_shape={"kind": "x"},
                instrument_id="I", cost_budget=1.0,
            )

    def test_residual_zero_cost_budget_rejected(self):
        """residuals.record_residual — Cat 1 — NEW. cost_budget=0 must
        raise (boundary)."""
        k, ext = _fresh_kernel_with_residuals()
        with pytest.raises(ResidualValidationError):
            ext.record_residual(
                parent_claim_id="p", test_id="t", magnitude=0.5,
                surviving_subset={"n": 5}, failure_shape={"kind": "x"},
                instrument_id="I", cost_budget=0.0,
            )

    def test_residual_negative_cost_budget_rejected(self):
        """residuals.record_residual — Cat 1 — NEW."""
        k, ext = _fresh_kernel_with_residuals()
        with pytest.raises(ResidualValidationError):
            ext.record_residual(
                parent_claim_id="p", test_id="t", magnitude=0.5,
                surviving_subset={"n": 5}, failure_shape={"kind": "x"},
                instrument_id="I", cost_budget=-0.1,
            )

    def test_refine_budget_exhaustion_at_min_threshold(self):
        """residuals.REFINE — Cat 1 — NEW. Parent budget that halves to
        exactly MIN_USEFUL_BUDGET_SECONDS triggers BudgetExceeded
        (`<` not `<=` in the guard)."""
        k, ext = _fresh_kernel_with_residuals()
        # 2 * 0.1 = 0.2 -> halves to 0.1 == MIN_USEFUL_BUDGET_SECONDS;
        # the check is strict <, so this should NOT raise.
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=0.5,
            surviving_subset={"n": 5},
            failure_shape={"kind": "x", "coeff_variance": 0.9},
            instrument_id="I", cost_budget=0.2,
        )
        cap = k.mint_capability("RefineCap")
        # Build a fake claim with .id attribute.
        class _FakeClaim:
            id = "fake_parent"
            hypothesis = "h"
            target_name = "t"
            target_tier = Tier.Conjecture
            kill_path = "kp"
        claim = _FakeClaim()
        # Need the parent to exist in claims table for FK; use a real CLAIM.
        real = k.CLAIM(
            target_name="t", hypothesis="h", evidence={"e": 1},
            kill_path="kp", target_tier=Tier.Conjecture,
        )
        # halving 0.2 -> 0.1 should be allowed (>= threshold).
        rc = ext.REFINE(real, r, cap=cap)
        assert math.isclose(rc.cost_budget_remaining, 0.1)


# ---------------------------------------------------------------------------
# Category 2 — Equivalence class partitioning
# ---------------------------------------------------------------------------


class TestEquivalenceClasses:

    def test_callable_ref_no_colon_raises_BindingError(self):
        """bind_eval._resolve_callable — Cat 2 — NEW. A callable_ref
        without ':' is in a distinct equivalence class from properly
        formatted refs."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        with pytest.raises(BindingError):
            ext.BIND(callable_ref="math.sqrt", cost_model=CostModel(), cap=cap)

    def test_callable_ref_empty_qualname_raises_BindingError(self):
        """bind_eval._resolve_callable — Cat 2 — NEW. 'module:' (empty
        qualname) cannot resolve."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        with pytest.raises(BindingError):
            ext.BIND(callable_ref="math:", cost_model=CostModel(), cap=cap)

    def test_callable_ref_resolves_to_non_callable_raises(self):
        """bind_eval._resolve_callable — Cat 2 — NEW. A module attribute
        that exists but isn't callable is its own equiv class."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        # math.pi is a float, not callable.
        with pytest.raises(BindingError):
            ext.BIND(callable_ref="math:pi", cost_model=CostModel(), cap=cap)

    def test_callable_ref_none_raises_BindingError(self):
        """bind_eval.BIND — Cat 2 — NEW. callable_ref=None should raise
        BindingError (typed input-validation error), not a generic
        TypeError from string membership check.

        Resolved 2026-05-03 (B-BUGHUNT-001): _resolve_callable now
        rejects None, non-str, and empty/whitespace inputs with
        BindingError before the ':' membership test fires.
        """
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        with pytest.raises(BindingError):
            ext.BIND(callable_ref=None, cost_model=CostModel(), cap=cap)

    def test_callable_ref_empty_string_raises_BindingError(self):
        """bind_eval.BIND — Cat 2 — NEW (B-BUGHUNT-001 companion).

        Empty string formerly hit the ``":" not in ""`` branch and
        produced a misleading "got ''" error; treat it as the same
        equivalence class as None (typed BindingError, explicit
        empty-input rationale).
        """
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        with pytest.raises(BindingError):
            ext.BIND(callable_ref="", cost_model=CostModel(), cap=cap)

    def test_callable_ref_whitespace_only_raises_BindingError(self):
        """bind_eval.BIND — Cat 2 — NEW (B-BUGHUNT-001 companion)."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        with pytest.raises(BindingError):
            ext.BIND(callable_ref="   ", cost_model=CostModel(), cap=cap)

    def test_residual_classification_signal_via_canonicalizer_signature(self):
        """residuals._classify_residual — Cat 2 — NEW. Equiv class:
        failure_shape with any *_signature key."""
        k, ext = _fresh_kernel_with_residuals()
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=0.5,
            surviving_subset={"n": 3},
            failure_shape={"kind": "x", "variety_fingerprint_signature": "v1"},
            instrument_id="I", cost_budget=1.0,
        )
        assert r.classification == "signal"

    def test_residual_classification_signal_via_variance_above_threshold(self):
        """residuals._classify_residual — Cat 2 — NEW. coeff_variance
        > 0.5 path."""
        k, ext = _fresh_kernel_with_residuals()
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=0.5,
            surviving_subset={"n": 3},
            failure_shape={"kind": "x", "coeff_variance": 0.6},
            instrument_id="I", cost_budget=1.0,
        )
        assert r.classification == "signal"

    def test_residual_classification_noise_below_variance_threshold(self):
        """residuals._classify_residual — Cat 2 — NEW. coeff_variance
        below threshold + no signature → noise."""
        k, ext = _fresh_kernel_with_residuals()
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=0.5,
            surviving_subset={"n": 3},
            failure_shape={"kind": "x", "coeff_variance": 0.4},
            instrument_id="I", cost_budget=1.0,
        )
        assert r.classification == "noise"

    def test_residual_classification_drift_dominates_signal(self):
        """residuals._classify_residual — Cat 2 — NEW. Per documented
        order: drift_signature_match precedes signal even when shape
        also has variance + canonicalizer hits."""
        k, ext = _fresh_kernel_with_residuals()
        ext.calibration_signatures = {
            "X": {"kind": "anchor_recovery_drift",
                  "anchor_recovery_rate": {"min": 0.95, "max": 0.999}},
        }
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=0.5,
            surviving_subset={"n": 3},
            failure_shape={
                "kind": "anchor_recovery_drift",
                "anchor_recovery_rate": 0.97,
                "coeff_variance": 0.9,
                "variety_fingerprint_signature": "v",
            },
            instrument_id="I", cost_budget=1.0,
        )
        assert r.classification == "instrument_drift"

    def test_residual_unclassified_when_no_calibration_and_drift_kind(self):
        """residuals._classify_residual — Cat 2 — NEW. Empty calibration
        map + drift-keyword kind → unclassified, not noise."""
        k, ext = _fresh_kernel_with_residuals()
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=0.5,
            surviving_subset={"n": 3},
            failure_shape={"kind": "decile_drift", "coeff_variance": 0.1},
            instrument_id="I", cost_budget=1.0,
        )
        assert r.classification == "unclassified"

    def test_residual_classification_empty_subset_is_noise(self):
        """residuals._classify_residual — Cat 2 — NEW. n==0 short-circuits
        to noise even with strong signal markers."""
        k, ext = _fresh_kernel_with_residuals()
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=0.5,
            surviving_subset={"n": 0},
            failure_shape={"variety_fingerprint_signature": "v",
                           "coeff_variance": 0.99},
            instrument_id="I", cost_budget=1.0,
        )
        assert r.classification == "noise"


# ---------------------------------------------------------------------------
# Category 3 — Property-based fuzzing with Hypothesis
# ---------------------------------------------------------------------------


class TestPropertyBased:

    @settings(deadline=10000, max_examples=50)
    @given(
        s=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    )
    def test_property_residual_magnitude_in_range_accepted(self, s):
        """residuals.record_residual — Cat 3 — NEW. Any [0,1] magnitude
        is accepted; classification depends on shape."""
        k, ext = _fresh_kernel_with_residuals()
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=s,
            surviving_subset={"n": 3},
            failure_shape={"kind": "x"},
            instrument_id="I", cost_budget=1.0,
        )
        assert 0.0 <= r.magnitude <= 1.0

    @settings(deadline=10000, max_examples=50)
    @given(
        b=st.floats(min_value=1e-9, max_value=10.0, allow_nan=False),
    )
    def test_property_refine_chain_terminates_below_min(self, b):
        """residuals.REFINE — Cat 3 — NEW. Iteratively halving any
        positive budget eventually crosses the min threshold and
        BudgetExceeded fires."""
        k, ext = _fresh_kernel_with_residuals()
        real = k.CLAIM(
            target_name="t", hypothesis="h", evidence={"e": 1},
            kill_path="kp", target_tier=Tier.Conjecture,
        )
        residual = ext.record_residual(
            parent_claim_id=real.id, test_id="t", magnitude=0.5,
            surviving_subset={"n": 3},
            failure_shape={"kind": "x", "coeff_variance": 0.9},
            instrument_id="I", cost_budget=b,
        )
        # If the initial budget is already too small, REFINE raises immediately.
        max_iters = 200
        cur_residual = residual
        cur_claim = real
        for _ in range(max_iters):
            cap = k.mint_capability("RefineCap")
            try:
                refined = ext.REFINE(cur_claim, cur_residual, cap=cap)
            except ResBudgetExceeded:
                return  # property satisfied
            # Build a follow-on residual at the new depth/budget.
            cur_residual = ext.record_residual(
                parent_claim_id=refined.id, test_id="t", magnitude=0.5,
                surviving_subset={"n": 3},
                failure_shape={"kind": "x", "coeff_variance": 0.9},
                instrument_id="I", cost_budget=refined.cost_budget_remaining,
                refinement_depth=refined.refinement_depth,
            )
            cur_claim = refined
        pytest.fail("REFINE chain did not terminate")

    @settings(deadline=10000, max_examples=50)
    @given(
        seconds=st.floats(min_value=0.001, max_value=10.0, allow_nan=False),
        memory=st.floats(min_value=0.001, max_value=10000.0, allow_nan=False),
        oracles=st.integers(min_value=0, max_value=1000),
    )
    def test_property_costmodel_round_trips_to_dict(self, seconds, memory, oracles):
        """bind_eval.CostModel.to_dict — Cat 3 — NEW. The dict
        representation must round-trip exactly."""
        cm = CostModel(max_seconds=seconds, max_memory_mb=memory,
                       max_oracle_calls=oracles)
        d = cm.to_dict()
        cm2 = CostModel(**d)
        assert cm2 == cm

    @settings(deadline=10000, max_examples=50)
    @given(
        kw_keys=st.lists(st.text(min_size=1, max_size=10), min_size=0, max_size=5,
                         unique=True),
    )
    def test_property_args_hash_invariant_under_kwargs_order(self, kw_keys):
        """bind_eval._hash_args — Cat 3 — NEW. The hash must be invariant
        under kwargs order (sort_keys=True is documented)."""
        kwargs1 = {k: i for i, k in enumerate(kw_keys)}
        kwargs2 = {k: kwargs1[k] for k in reversed(kw_keys)}
        h1 = _BEX._hash_args([], kwargs1)
        h2 = _BEX._hash_args([], kwargs2)
        assert h1 == h2


# ---------------------------------------------------------------------------
# Category 4 — Adversarial inputs
# ---------------------------------------------------------------------------


class TestAdversarialInputs:

    def test_eval_with_empty_args_succeeds(self):
        """bind_eval.EVAL — Cat 4 — NEW. args=[] (empty) on a zero-arg
        callable must succeed."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        b = ext.BIND(callable_ref="time:time", cost_model=CostModel(max_seconds=1.0), cap=cap)
        cap2 = k.mint_capability("EvalCap")
        ev = ext.EVAL(b.symbol.name, b.symbol.version, args=[], cap=cap2)
        assert ev.success

    def test_eval_args_signature_mismatch_returns_failure(self):
        """bind_eval.EVAL — Cat 4 — NEW. Wrong arity passes through to
        callable; we capture the TypeError as success=False (not raise)."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        b = ext.BIND(callable_ref="math:sqrt", cost_model=CostModel(max_seconds=1.0), cap=cap)
        cap2 = k.mint_capability("EvalCap")
        # math.sqrt expects 1 arg, give it 3.
        ev = ext.EVAL(b.symbol.name, b.symbol.version, args=[1.0, 2.0, 3.0], cap=cap2)
        assert not ev.success
        assert "TypeError" in ev.error_repr or "expected" in ev.error_repr.lower()

    def test_residual_with_unserializable_subset_uses_default_repr(self):
        """residuals.record_residual — Cat 4 — NEW. surviving_subset
        containing a non-JSON-serializable value should not crash;
        json.dumps default=repr handles it."""
        k, ext = _fresh_kernel_with_residuals()
        # Use a set, which json.dumps cannot serialize natively.
        r = ext.record_residual(
            parent_claim_id="p", test_id="t", magnitude=0.3,
            surviving_subset={"n": 3, "items": {1, 2, 3}},
            failure_shape={"kind": "x"},
            instrument_id="I", cost_budget=1.0,
        )
        # Confirm a hash got computed.
        assert len(r.surviving_subset_hash) == 64

    def test_residual_subset_not_dict_raises(self):
        """residuals.record_residual — Cat 4 — NEW."""
        k, ext = _fresh_kernel_with_residuals()
        with pytest.raises(ResidualValidationError):
            ext.record_residual(
                parent_claim_id="p", test_id="t", magnitude=0.5,
                surviving_subset=[1, 2, 3],  # type: ignore
                failure_shape={"kind": "x"},
                instrument_id="I", cost_budget=1.0,
            )

    def test_eval_callable_that_raises_captures_error_does_not_propagate(self):
        """bind_eval.EVAL — Cat 4 — NEW. A callable that raises must NOT
        bubble; the evaluation symbol records success=False."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        b = ext.BIND(callable_ref="math:sqrt", cost_model=CostModel(max_seconds=1.0), cap=cap)
        cap2 = k.mint_capability("EvalCap")
        # math.sqrt(-1) raises ValueError.
        ev = ext.EVAL(b.symbol.name, b.symbol.version, args=[-1.0], cap=cap2)
        assert not ev.success
        assert "ValueError" in ev.error_repr or "math domain" in ev.error_repr


# ---------------------------------------------------------------------------
# Category 5 — State-machine testing
# ---------------------------------------------------------------------------


class TestStateMachine:

    def test_eval_before_bind_raises(self):
        """bind_eval.EVAL — Cat 5 — NEW. Calling EVAL on a binding name
        that doesn't exist must raise EvalError."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("EvalCap")
        with pytest.raises(EvalError):
            ext.EVAL("nonexistent", 1, args=[], cap=cap)

    def test_double_consume_cap_via_bind_then_eval_raises(self):
        """bind_eval — Cat 5 — NEW. The same Capability cannot be used
        for BIND and then again for EVAL."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        b = ext.BIND(callable_ref="math:sqrt", cost_model=CostModel(max_seconds=1.0), cap=cap)
        # Try the same cap for EVAL.
        with pytest.raises(CapabilityError):
            ext.EVAL(b.symbol.name, b.symbol.version, args=[4.0], cap=cap)

    def test_bind_with_already_consumed_cap_via_db_path(self):
        """bind_eval.BIND — Cat 5 — NEW. After a successful BIND consumes
        the cap in the DB, a second BIND with the same cap raises."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        ext.BIND(callable_ref="math:sqrt", cost_model=CostModel(max_seconds=1.0), cap=cap)
        with pytest.raises(CapabilityError):
            ext.BIND(callable_ref="math:cos", cost_model=CostModel(max_seconds=1.0), cap=cap)

    def test_residual_REFINE_requires_signal_classification(self):
        """residuals.REFINE — Cat 5 — NEW. REFINE on a noise residual
        raises RefinementBlocked even with a fresh cap."""
        k, ext = _fresh_kernel_with_residuals()
        real = k.CLAIM(
            target_name="t", hypothesis="h", evidence={"e": 1},
            kill_path="kp", target_tier=Tier.Conjecture,
        )
        # noise classification (no signature, low variance)
        r = ext.record_residual(
            parent_claim_id=real.id, test_id="t", magnitude=0.5,
            surviving_subset={"n": 3},
            failure_shape={"kind": "x", "coeff_variance": 0.1},
            instrument_id="I", cost_budget=1.0,
        )
        assert r.classification == "noise"
        cap = k.mint_capability("RefineCap")
        with pytest.raises(RefinementBlocked):
            ext.REFINE(real, r, cap=cap)

    def test_residual_REFINE_chain_walks_back_to_root(self):
        """residuals.refinement_chain — Cat 5 — NEW. After two REFINEs
        the chain has 3 entries (root + 2 refinements)."""
        k, ext = _fresh_kernel_with_residuals()
        real = k.CLAIM(
            target_name="t", hypothesis="h", evidence={"e": 1},
            kill_path="kp", target_tier=Tier.Conjecture,
        )
        r1 = ext.record_residual(
            parent_claim_id=real.id, test_id="t", magnitude=0.5,
            surviving_subset={"n": 3},
            failure_shape={"variety_fingerprint_signature": "x"},
            instrument_id="I", cost_budget=2.0,
        )
        cap1 = k.mint_capability("RefineCap")
        rc1 = ext.REFINE(real, r1, cap=cap1)
        r2 = ext.record_residual(
            parent_claim_id=rc1.id, test_id="t2", magnitude=0.4,
            surviving_subset={"n": 2},
            failure_shape={"variety_fingerprint_signature": "y"},
            instrument_id="I", cost_budget=rc1.cost_budget_remaining,
            refinement_depth=rc1.refinement_depth,
        )
        cap2 = k.mint_capability("RefineCap")
        rc2 = ext.REFINE(rc1, r2, cap=cap2)
        chain = ext.refinement_chain(rc2.id)
        assert len(chain) == 3


# ---------------------------------------------------------------------------
# Category 6 — Differential testing
# ---------------------------------------------------------------------------


class TestDifferential:

    def test_args_hash_stable_across_calls(self):
        """bind_eval._hash_args — Cat 6 — NEW. The same args yields the
        same hash across two independent calls (no hidden state)."""
        h1 = _BEX._hash_args([1, 2, 3], {"a": 1})
        h2 = _BEX._hash_args([1, 2, 3], {"a": 1})
        assert h1 == h2

    def test_hash_callable_stable_across_imports(self):
        """bind_eval._hash_callable — Cat 6 — NEW. Hashing the same
        callable twice yields the same hex; the documented stability
        contract."""
        import math as _m1
        import math as _m2
        h1 = _BEX._hash_callable(_m1.sqrt)
        h2 = _BEX._hash_callable(_m2.sqrt)
        assert h1 == h2


# ---------------------------------------------------------------------------
# Category 7 — Error injection
# ---------------------------------------------------------------------------


class TestErrorInjection:

    def test_module_global_TABLES_not_mutated_across_extensions_sqlite(self):
        """bind_eval._patch_postgres_tables — Cat 7 — NEW (regression).

        On SQLite (the default backend) the patch must NOT fire — the
        SQL rewrite is postgres-only. If the global mutates anyway,
        unrelated kernels lose isolation.
        """
        from sigma_kernel import sigma_kernel as core
        before = tuple(core._TABLES) if hasattr(core, "_TABLES") else ()
        # Spawn three extensions; none of them should mutate the global
        # because the backend is sqlite.
        for _ in range(3):
            k = SigmaKernel(":memory:")
            BindEvalExtension(k)
        after = tuple(core._TABLES) if hasattr(core, "_TABLES") else ()
        assert before == after, (
            f"_TABLES global mutated by sqlite extension: "
            f"{before} -> {after}"
        )

    def test_bughunt_003_per_instance_table_isolation(self):
        """sigma_kernel._PostgresAdapter / bind_eval / residuals — Cat 7 —
        NEW (regression for B-BUGHUNT-003).

        The postgres SQL rewriter's table list is now bound to the
        adapter instance, never to the module. Two extensions attached
        to two different adapters must end up with disjoint
        ``_extra_tables`` and disjoint translation caches; the
        module-global ``_TABLES`` must remain untouched.

        We avoid spinning up a real Postgres connection by directly
        constructing two stub adapters that mimic ``_PostgresAdapter``
        and exercising ``register_tables`` + ``_translate``.
        """
        from sigma_kernel import sigma_kernel as core

        # Snapshot the module-level _TABLES; assert it is unchanged after
        # this test no matter what register_tables does.
        baseline_tables = tuple(core._TABLES)

        # Build a minimal adapter shaped like _PostgresAdapter without
        # actually connecting. We reuse the real _translate /
        # register_tables to prove they read from per-instance state.
        adapter_cls = core._PostgresAdapter

        def _stub_adapter():
            inst = adapter_cls.__new__(adapter_cls)
            inst._extra_tables = ()
            inst._RE_CACHE = {}
            return inst

        a1 = _stub_adapter()
        a2 = _stub_adapter()

        # Different extensions register different sidecar tables.
        a1.register_tables("bindings", "evaluations")
        a2.register_tables("residuals", "refinements")

        # Per-instance state is disjoint.
        assert set(a1._extra_tables) == {"bindings", "evaluations"}
        assert set(a2._extra_tables) == {"residuals", "refinements"}
        assert a1._RE_CACHE is not a2._RE_CACHE  # different objects

        # Translation pulls from baseline + own extras only.
        sql = "INSERT INTO bindings VALUES (?)"
        out1 = a1._translate(sql)
        out2 = a2._translate(sql)
        assert "sigma.bindings" in out1
        # a2 doesn't know "bindings"; its translation leaves the name bare.
        assert "sigma.bindings" not in out2

        sql_r = "INSERT INTO refinements VALUES (?)"
        assert "sigma.refinements" in a2._translate(sql_r)
        assert "sigma.refinements" not in a1._translate(sql_r)

        # Module-global _TABLES untouched.
        assert tuple(core._TABLES) == baseline_tables

    def test_bughunt_003_register_tables_is_idempotent(self):
        """sigma_kernel._PostgresAdapter.register_tables — Cat 7 — NEW.

        Re-registering a name does not duplicate it in ``_extra_tables``
        and does not invalidate the cache unnecessarily.
        """
        from sigma_kernel import sigma_kernel as core

        adapter_cls = core._PostgresAdapter
        a = adapter_cls.__new__(adapter_cls)
        a._extra_tables = ()
        a._RE_CACHE = {}

        a.register_tables("bindings")
        # Prime the cache by translating once.
        sql = "SELECT * FROM bindings"
        a._translate(sql)
        assert sql in a._RE_CACHE

        # Re-registering the same name is a no-op (no cache invalidation,
        # no duplicate in _extra_tables).
        a.register_tables("bindings")
        assert a._extra_tables == ("bindings",)
        assert sql in a._RE_CACHE  # still cached

        # Registering a NEW name invalidates the cache.
        a.register_tables("evaluations")
        assert set(a._extra_tables) == {"bindings", "evaluations"}
        assert sql not in a._RE_CACHE  # cleared

    def test_callable_source_drift_detected_at_eval(self):
        """bind_eval.EVAL — Cat 7 — NEW. If the live source hash differs
        from the stored hash, EVAL raises EvalError. We simulate this
        by directly patching the bindings table."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        b = ext.BIND(callable_ref="math:sqrt", cost_model=CostModel(max_seconds=1.0), cap=cap)
        # Inject a corrupted hash into the bindings table.
        k.conn.execute(
            "UPDATE bindings SET callable_hash=? WHERE name=? AND version=?",
            ("0" * 64, b.symbol.name, b.symbol.version),
        )
        k.conn.commit()
        cap2 = k.mint_capability("EvalCap")
        with pytest.raises(EvalError):
            ext.EVAL(b.symbol.name, b.symbol.version, args=[4.0], cap=cap2)

    def test_eval_with_broken_cost_model_blob_raises(self):
        """bind_eval.EVAL — Cat 7 — NEW. If the cost_model blob is
        corrupted in the DB, EVAL must raise (not silently no-op)."""
        k, ext = _fresh_kernel_with_bind()
        cap = k.mint_capability("BindCap")
        b = ext.BIND(callable_ref="math:sqrt", cost_model=CostModel(max_seconds=1.0), cap=cap)
        k.conn.execute(
            "UPDATE bindings SET cost_model=? WHERE name=? AND version=?",
            ("not-json", b.symbol.name, b.symbol.version),
        )
        k.conn.commit()
        cap2 = k.mint_capability("EvalCap")
        with pytest.raises((json.JSONDecodeError, EvalError, ValueError, Exception)):
            ext.EVAL(b.symbol.name, b.symbol.version, args=[4.0], cap=cap2)

    def test_record_meta_claim_requires_cap(self):
        """residuals.record_meta_claim — Cat 7 — NEW."""
        k, ext = _fresh_kernel_with_residuals()
        with pytest.raises(CapabilityError):
            ext.record_meta_claim(
                target_battery_id="bat",
                evidence_residuals=[],
                hypothesis="h",
                cap=None,
            )


