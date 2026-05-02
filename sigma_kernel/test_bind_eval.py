"""Tests for sigma_kernel.bind_eval (BIND + EVAL opcodes).

Math-tdd skill rubric: ≥2 tests in each of authority/property/edge/composition.

SQLite-only path; the Postgres path is exercised by demo_bind_eval.py
once Mnemosyne applies migration 002.
"""
from __future__ import annotations

import math
import time

import pytest

from sigma_kernel.sigma_kernel import (
    Capability,
    CapabilityError,
    SigmaKernel,
    Tier,
)
from sigma_kernel.bind_eval import (
    BindEvalExtension,
    Binding,
    BindingError,
    BudgetExceeded,
    CostModel,
    Evaluation,
    EvalError,
)


# ---------------------------------------------------------------------------
# Test fixtures: a couple of import-resolvable callables we can BIND to.
# ---------------------------------------------------------------------------


def _square(x):
    """Test fixture: squares its input. Used as a reproducible callable."""
    return x * x


def _slow(seconds: float):
    """Test fixture: sleeps. Used to validate budget enforcement."""
    time.sleep(seconds)
    return seconds


def _raises():
    """Test fixture: always raises. Used to validate error capture."""
    raise ValueError("test exception")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_kernel():
    return SigmaKernel(":memory:")


def _make_ext():
    k = _make_kernel()
    return k, BindEvalExtension(k)


SQUARE_REF = "sigma_kernel.test_bind_eval:_square"
SLOW_REF = "sigma_kernel.test_bind_eval:_slow"
RAISES_REF = "sigma_kernel.test_bind_eval:_raises"


# ---------------------------------------------------------------------------
# Authority tests — known callables, known outputs
# ---------------------------------------------------------------------------


def test_authority_bind_then_eval_round_trip():
    """BIND a known callable; EVAL it; the result symbol round-trips
    via RESOLVE and the output_repr is the canonical Python repr."""
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[7],
        cap=cap2,
    )
    assert ev.success is True
    assert ev.output_repr == "49"
    # Resolve the eval symbol back through the substrate.
    sym = k.RESOLVE(ev.symbol.name, ev.symbol.version)
    assert sym.def_hash == ev.symbol.def_hash


def test_authority_dilogarithm_bind_eval():
    """Bind pm.numerics_special_dilogarithm.dilogarithm and verify
    Li_2(1) ≈ pi^2/6."""
    pytest.importorskip("scipy")
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref="prometheus_math.numerics_special_dilogarithm:dilogarithm",
        cost_model=CostModel(max_seconds=2.0),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[1.0],
        cap=cap2,
    )
    assert ev.success is True
    val = float(ev.output_repr)
    assert abs(val - math.pi ** 2 / 6.0) < 1e-9


# ---------------------------------------------------------------------------
# Property tests — invariants across the BIND/EVAL surface
# ---------------------------------------------------------------------------


def test_property_eval_provenance_links_to_binding():
    """Every EVAL symbol has a provenance entry linking back to the
    binding's callable_hash."""
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[3],
        cap=cap2,
    )
    assert binding.callable_hash in ev.symbol.provenance


def test_property_actual_cost_within_budget_on_success():
    """When EVAL succeeds without raising BudgetExceeded, actual_cost
    elapsed_seconds is below the cost_model max_seconds."""
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[5],
        cap=cap2,
    )
    assert ev.actual_cost["elapsed_seconds"] < 1.0
    assert ev.actual_cost["elapsed_seconds"] >= 0.0


def test_property_capability_consumed_after_use():
    """A capability passed to BIND can't be used again — even for EVAL."""
    k, ext = _make_ext()
    cap = k.mint_capability("MultiCap")
    ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    # Same cap.cap_id; spent_caps row is now consumed=1.
    with pytest.raises(CapabilityError):
        ext.BIND(
            callable_ref=SQUARE_REF,
            cost_model=CostModel(max_seconds=1.0),
            cap=cap,
            name="bind__square_v2",
            version=2,
        )


# ---------------------------------------------------------------------------
# Edge tests — malformed inputs and error paths
# ---------------------------------------------------------------------------


def test_edge_bind_missing_capability():
    k, ext = _make_ext()
    with pytest.raises(CapabilityError):
        ext.BIND(
            callable_ref=SQUARE_REF,
            cost_model=CostModel(),
            cap=None,
        )


def test_edge_bind_malformed_callable_ref():
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    with pytest.raises(BindingError):
        ext.BIND(
            callable_ref="not_a_valid_ref_no_colon",
            cost_model=CostModel(),
            cap=cap,
        )


def test_edge_bind_unimportable_module():
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    with pytest.raises(BindingError):
        ext.BIND(
            callable_ref="this_module_does_not_exist_xxx:fn",
            cost_model=CostModel(),
            cap=cap,
        )


def test_edge_eval_unknown_binding():
    k, ext = _make_ext()
    cap = k.mint_capability("EvalCap")
    with pytest.raises(EvalError):
        ext.EVAL(
            binding_name="never_bound",
            binding_version=1,
            args=[1],
            cap=cap,
        )


def test_edge_eval_callable_raises():
    """When the bound callable raises, EVAL captures the error and
    writes a success=False evaluation symbol — does NOT propagate."""
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=RAISES_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[],
        cap=cap2,
    )
    assert ev.success is False
    assert "ValueError" in ev.error_repr


def test_edge_eval_budget_exceeded():
    """If the callable exceeds max_seconds, BudgetExceeded is raised."""
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SLOW_REF,
        cost_model=CostModel(max_seconds=0.05),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    with pytest.raises(BudgetExceeded):
        ext.EVAL(
            binding_name=binding.symbol.name,
            binding_version=binding.symbol.version,
            args=[0.2],
            cap=cap2,
        )


# ---------------------------------------------------------------------------
# Composition tests — interaction with the rest of the kernel
# ---------------------------------------------------------------------------


def test_composition_resolve_eval_symbol_round_trip():
    """An EVAL symbol can be RESOLVE'd from the substrate (closes the
    loop with the v0.1 kernel's RESOLVE opcode)."""
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[6],
        cap=cap2,
    )
    sym = k.RESOLVE(ev.symbol.name, ev.symbol.version)
    assert sym.tier == Tier.Conjecture
    assert sym.ref == ev.symbol.ref


def test_composition_list_evaluations_filters_by_binding():
    """list_evaluations(binding_name=X) returns only X's evaluations."""
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    b1 = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    cap_b2 = k.mint_capability("BindCap")
    b2 = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap_b2,
        name="bind__square_alt",
        version=1,
    )
    # 2 evals on b1, 1 eval on b2.
    for i, args in enumerate([[1], [2]]):
        ext.EVAL(
            b1.symbol.name,
            b1.symbol.version,
            args=args,
            cap=k.mint_capability("EvalCap"),
            eval_version=i + 1,
        )
    ext.EVAL(
        b2.symbol.name,
        b2.symbol.version,
        args=[3],
        cap=k.mint_capability("EvalCap"),
    )
    b1_evals = ext.list_evaluations(binding_name=b1.symbol.name)
    b2_evals = ext.list_evaluations(binding_name=b2.symbol.name)
    assert len(b1_evals) == 2
    assert len(b2_evals) == 1


def test_composition_get_binding_recovers_meta():
    """get_binding returns the same metadata that BIND wrote."""
    k, ext = _make_ext()
    cap = k.mint_capability("BindCap")
    cm = CostModel(max_seconds=2.5, max_memory_mb=128.0, max_oracle_calls=3)
    b = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=cm,
        postconditions=["output >= 0 for real x"],
        authority_refs=["x*x is monotone on R+"],
        cap=cap,
    )
    fetched = ext.get_binding(b.symbol.name, b.symbol.version)
    assert fetched.callable_ref == SQUARE_REF
    assert fetched.cost_model.max_seconds == 2.5
    assert "output >= 0 for real x" in fetched.postconditions
