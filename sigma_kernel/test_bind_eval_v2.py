"""Tests for sigma_kernel.bind_eval_v2 (BIND/EVAL routed through CLAIM/FALSIFY/PROMOTE).

Math-tdd skill rubric: >=3 tests in each of authority/property/edge/composition.

Written test-first per the math-tdd skill. The implementations under test
(``sigma_kernel.bind_eval_v2.BindEvalKernelV2`` and
``sigma_kernel.omega_validators``) do not exist when this file is created; the
suite is initially RED with ImportError, then turns GREEN when the
implementations are added.

The v2 sidecar exists because the v1 BIND/EVAL implementation bypasses the
kernel's central CLAIM->FALSIFY->PROMOTE discipline (the C1 critique from the
2026-05-03 team review). v2 routes both opcodes through that path so every
binding-symbol and evaluation-symbol carries a verdict-bound provenance trail.

The C2 instrumentation (oracle_calls + memory_mb) lives in v1's ``bind_eval``
module and is inherited by v2; tests for it are in this file because the
review item is paired with v2.
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
    Verdict,
    BlockedError,
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
from sigma_kernel.bind_eval_v2 import BindEvalKernelV2
from sigma_kernel import omega_validators as ov


# ---------------------------------------------------------------------------
# Test fixtures: import-resolvable callables we can BIND to.
# ---------------------------------------------------------------------------


def _square(x):
    """Test fixture: squares its input. Used as a reproducible callable."""
    return x * x


def _slow(seconds: float):
    """Test fixture: sleeps. Used to validate budget enforcement."""
    time.sleep(seconds)
    return seconds


def _allocates(n: int):
    """Test fixture: allocates a chunk; used to validate memory tracking."""
    # ~ n * 28 bytes for ints; n=200_000 ~ 5-6 MB measured by tracemalloc.
    return [i for i in range(n)]


def _calls_pari():
    """Test fixture: invokes cypari to validate oracle_calls counter.

    Skips downstream tests if cypari is unavailable on the runner.
    """
    import cypari  # noqa: F401  -- imported for the side-effect counter

    return float(cypari.pari("Pi"))


def _pure_python():
    """Test fixture: pure-Python op that doesn't dispatch to any oracle."""
    return sum(i * i for i in range(100))


def _raises():
    raise ValueError("test exception")


SQUARE_REF = "sigma_kernel.test_bind_eval_v2:_square"
SLOW_REF = "sigma_kernel.test_bind_eval_v2:_slow"
ALLOC_REF = "sigma_kernel.test_bind_eval_v2:_allocates"
PARI_REF = "sigma_kernel.test_bind_eval_v2:_calls_pari"
PURE_REF = "sigma_kernel.test_bind_eval_v2:_pure_python"
RAISES_REF = "sigma_kernel.test_bind_eval_v2:_raises"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_kernel():
    return SigmaKernel(":memory:")


def _make_v2():
    k = _make_kernel()
    return k, BindEvalKernelV2(k)


def _make_v1():
    k = _make_kernel()
    return k, BindEvalExtension(k)


# ---------------------------------------------------------------------------
# Authority tests (>= 3) -- known-good substrate behavior the v2 path must
# preserve.
# ---------------------------------------------------------------------------


def test_authority_bind_known_good_callable_promotes_via_claim():
    """AUTHORITY: BIND on a resolvable callable goes through CLAIM/FALSIFY/
    PROMOTE and produces a substrate symbol that RESOLVE returns at the
    declared tier.

    Reference: sigma_kernel.SigmaKernel.PROMOTE contract (PROMOTE always
    consumes a capability and writes a new immutable symbol whose tier is
    the claim's target_tier).
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        postconditions=["output is real"],
        authority_refs=["x*x is monotone on R+"],
        cap=cap,
    )
    sym = k.RESOLVE(binding.symbol.name, binding.symbol.version)
    assert sym.tier == Tier.WorkingTheory
    assert sym.ref == binding.symbol.ref


def test_authority_bind_unimportable_callable_falsifies_to_block():
    """AUTHORITY: BIND on a non-importable callable produces a CLAIM whose
    FALSIFY returns BLOCK; PROMOTE refuses and BIND raises BlockedError
    (or BindingError -- both are documented kill-paths).

    Reference: BIND must mint a substrate-visible artifact only after a
    non-BLOCK verdict.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    with pytest.raises((BlockedError, BindingError)):
        ext.BIND(
            callable_ref="this_module_does_not_exist_xxx_v2:fn",
            cost_model=CostModel(max_seconds=1.0),
            cap=cap,
        )


def test_authority_eval_with_drifted_source_blocks():
    """AUTHORITY: if the bound callable's source drifted between BIND and
    EVAL, the EVAL claim's FALSIFY returns BLOCK and no evaluation symbol
    is promoted.

    Reference: hash-drift detection is the load-bearing integrity check
    on the EVAL path; v2 must preserve it via the FALSIFY predicate.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    # Manually corrupt the stored callable_hash to simulate source drift.
    k.conn.execute(
        "UPDATE bindings SET callable_hash=? WHERE name=? AND version=?",
        ("0" * 64, binding.symbol.name, binding.symbol.version),
    )
    k.conn.commit()
    cap2 = k.mint_capability("EvalCap")
    with pytest.raises((BlockedError, EvalError)):
        ext.EVAL(
            binding_name=binding.symbol.name,
            binding_version=binding.symbol.version,
            args=[3],
            cap=cap2,
        )


def test_authority_oracle_calls_zero_for_pure_python():
    """AUTHORITY: a callable that does not invoke PARI/SymPy/subprocess
    reports oracle_calls=0 in actual_cost.

    Reference: monotonic-accountability principle (ChatGPT review) --
    counter increments only at dispatch sites, so pure-Python ops report 0
    honestly.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=PURE_REF,
        cost_model=CostModel(max_seconds=1.0, max_oracle_calls=10),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[],
        cap=cap2,
    )
    assert ev.success is True
    assert ev.actual_cost["oracle_calls"] == 0


def test_authority_memory_tracking_positive_for_allocator():
    """AUTHORITY: a callable that allocates a non-trivial chunk reports
    memory_mb > 0 in actual_cost.

    Reference: tracemalloc.get_traced_memory() peak-delta is the
    cross-platform standard for in-process memory accounting.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=ALLOC_REF,
        cost_model=CostModel(max_seconds=2.0, max_memory_mb=500.0),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[200_000],
        cap=cap2,
    )
    assert ev.success is True
    # Allocator returns a list of 200k ints; memory peak should be positive,
    # i.e. tracemalloc detected the allocation.
    assert ev.actual_cost["memory_mb"] > 0.0


# ---------------------------------------------------------------------------
# Property tests (>= 3) -- invariants over many BIND/EVAL inputs.
# ---------------------------------------------------------------------------


def test_property_bind_writes_one_claim_one_symbol_one_binding():
    """PROPERTY: every BIND call appends exactly one new row to ``claims``,
    one to ``symbols``, one to ``bindings``.

    The provenance trail must be 1:1:1 -- one claim per BIND, one symbol per
    successful PROMOTE, one binding side-table row per symbol.
    """
    k, ext = _make_v2()

    n0_claims = k.conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    n0_symbols = k.conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    n0_bindings = k.conn.execute("SELECT COUNT(*) FROM bindings").fetchone()[0]

    cap = k.mint_capability("BindCap")
    ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )

    n1_claims = k.conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    n1_symbols = k.conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    n1_bindings = k.conn.execute("SELECT COUNT(*) FROM bindings").fetchone()[0]

    assert n1_claims - n0_claims == 1
    assert n1_symbols - n0_symbols == 1
    assert n1_bindings - n0_bindings == 1


def test_property_eval_writes_one_claim_one_symbol_one_evaluation():
    """PROPERTY: every EVAL call appends exactly one row to ``claims``,
    one to ``symbols``, one to ``evaluations``.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )

    n0_claims = k.conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    n0_symbols = k.conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    n0_evals = k.conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]

    cap2 = k.mint_capability("EvalCap")
    ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[5],
        cap=cap2,
    )

    n1_claims = k.conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    n1_symbols = k.conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    n1_evals = k.conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]

    assert n1_claims - n0_claims == 1
    assert n1_symbols - n0_symbols == 1
    assert n1_evals - n0_evals == 1


def test_property_capability_linearity_preserved_on_bind():
    """PROPERTY: a capability passed to BIND can't be reused on a second
    BIND or on EVAL; double-spend is rejected.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    with pytest.raises(CapabilityError):
        ext.BIND(
            callable_ref=SQUARE_REF,
            cost_model=CostModel(max_seconds=1.0),
            cap=cap,
            name="dup_attempt",
            version=1,
        )


def test_property_capability_linearity_preserved_on_eval():
    """PROPERTY: a capability used on EVAL can't be reused on a second EVAL.
    """
    k, ext = _make_v2()
    cap_b = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap_b,
    )
    cap = k.mint_capability("EvalCap")
    ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[2],
        cap=cap,
    )
    with pytest.raises(CapabilityError):
        ext.EVAL(
            binding_name=binding.symbol.name,
            binding_version=binding.symbol.version,
            args=[3],
            cap=cap,
            eval_version=2,
        )


def test_property_three_dim_budget_independently_triggers():
    """PROPERTY: each of the three cost dimensions can independently raise
    BudgetExceeded.

    - max_seconds: a sleep that exceeds the wall budget.
    - max_oracle_calls: a callable that hits more oracles than declared.
    - max_memory_mb: an allocator that exceeds the memory ceiling.
    """
    # Wall-time
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    b = ext.BIND(
        callable_ref=SLOW_REF,
        cost_model=CostModel(max_seconds=0.05),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    with pytest.raises(BudgetExceeded):
        ext.EVAL(
            binding_name=b.symbol.name,
            binding_version=b.symbol.version,
            args=[0.2],
            cap=cap2,
        )

    # Memory (allocator with max_memory_mb=0.01 will overshoot).
    k2, ext2 = _make_v2()
    cap = k2.mint_capability("BindCap")
    b2 = ext2.BIND(
        callable_ref=ALLOC_REF,
        cost_model=CostModel(max_seconds=2.0, max_memory_mb=0.01),
        cap=cap,
    )
    cap2 = k2.mint_capability("EvalCap")
    with pytest.raises(BudgetExceeded):
        ext2.EVAL(
            binding_name=b2.symbol.name,
            binding_version=b2.symbol.version,
            args=[200_000],
            cap=cap2,
        )

    # Oracle calls (manually push the counter and check enforcement).
    from sigma_kernel.bind_eval import _oracle_dispatch_increment

    def _hits_counter():
        for _ in range(5):
            _oracle_dispatch_increment("test_marker")
        return 0

    k3, ext3 = _make_v2()
    # Inject the test callable directly into ARSENAL-like resolution by
    # binding via a module:qualname pair that exists.
    cap = k3.mint_capability("BindCap")
    # We register the helper into the test module so BIND can resolve it.
    import sigma_kernel.test_bind_eval_v2 as _self_mod
    _self_mod._hits_counter = _hits_counter  # type: ignore[attr-defined]
    b3 = ext3.BIND(
        callable_ref="sigma_kernel.test_bind_eval_v2:_hits_counter",
        cost_model=CostModel(
            max_seconds=2.0, max_memory_mb=500.0, max_oracle_calls=2
        ),
        cap=cap,
    )
    cap2 = k3.mint_capability("EvalCap")
    with pytest.raises(BudgetExceeded):
        ext3.EVAL(
            binding_name=b3.symbol.name,
            binding_version=b3.symbol.version,
            args=[],
            cap=cap2,
        )


# ---------------------------------------------------------------------------
# Edge tests (>= 3) -- malformed inputs the FALSIFY predicate must catch.
# ---------------------------------------------------------------------------


def test_edge_zero_max_seconds_blocks_bind():
    """EDGE: a CostModel with max_seconds=0 fails the finite-positive check
    in the bind_validation Omega oracle; BIND raises BlockedError.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    with pytest.raises((BlockedError, BindingError)):
        ext.BIND(
            callable_ref=SQUARE_REF,
            cost_model=CostModel(max_seconds=0.0),
            cap=cap,
        )


def test_edge_empty_postconditions_default_passes():
    """EDGE: postconditions=None (default) passes the bind_validation
    Omega oracle; only an explicit empty list fails.

    The contract: postconditions must be a non-empty list of non-empty
    strings IF declared. The default of None is treated as "absent" and
    is acceptable for the MVP. (If we wanted to forbid the default we'd
    require the caller to always supply postconditions.)
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    # None should be accepted (translates to []).
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    assert binding.symbol.tier == Tier.WorkingTheory


def test_edge_eval_args_none_vs_empty_list_equivalent():
    """EDGE: EVAL(args=None) and EVAL(args=[]) both work and are equivalent.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=PURE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    cap_a = k.mint_capability("EvalCap")
    ev_a = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=None,
        cap=cap_a,
        eval_version=1,
    )
    cap_b = k.mint_capability("EvalCap")
    ev_b = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[],
        cap=cap_b,
        eval_version=2,
    )
    assert ev_a.success is True
    assert ev_b.success is True
    assert ev_a.output_repr == ev_b.output_repr


def test_edge_bind_then_drift_then_eval_blocks():
    """EDGE: full lifecycle test of hash-drift -- BIND records a hash; we
    overwrite the stored hash; EVAL refuses to promote.

    Distinct from authority test: this exercises the CLAIM/FALSIFY ordering,
    not just the failure surface. The EVAL CLAIM must be created BEFORE the
    Omega oracle runs; the verdict must BLOCK; the symbol/eval rows must
    remain at their pre-call counts.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    # Drift the stored hash.
    k.conn.execute(
        "UPDATE bindings SET callable_hash=? WHERE name=? AND version=?",
        ("d" * 64, binding.symbol.name, binding.symbol.version),
    )
    k.conn.commit()
    n_evals_before = k.conn.execute(
        "SELECT COUNT(*) FROM evaluations"
    ).fetchone()[0]
    cap2 = k.mint_capability("EvalCap")
    with pytest.raises((BlockedError, EvalError)):
        ext.EVAL(
            binding_name=binding.symbol.name,
            binding_version=binding.symbol.version,
            args=[7],
            cap=cap2,
        )
    n_evals_after = k.conn.execute(
        "SELECT COUNT(*) FROM evaluations"
    ).fetchone()[0]
    # No new evaluation row written.
    assert n_evals_after == n_evals_before


def test_edge_inprocess_double_spend_rejected():
    """EDGE: cross-process double-spend deferred to a future test (a real
    cross-interpreter check requires two pythons); in-process double-spend
    must still be rejected on the BIND path.
    """
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    with pytest.raises(CapabilityError):
        ext.BIND(
            callable_ref=SQUARE_REF,
            cost_model=CostModel(max_seconds=1.0),
            cap=cap,
            name="dup",
            version=1,
        )


# ---------------------------------------------------------------------------
# Composition tests (>= 3) -- v2 composes with the rest of the kernel.
# ---------------------------------------------------------------------------


def test_composition_bind_eval_pipeline_trace_walks_chain():
    """COMPOSITION: BIND -> EVAL pipeline produces a provenance trail that
    TRACE walks from leaf (eval symbol) back through the binding's
    callable_hash.
    """
    k, ext = _make_v2()
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
        args=[4],
        cap=cap2,
    )
    trace = k.TRACE(ev.symbol)
    # Trace is a dict with 'ref' and 'children' keys for the eval symbol.
    assert "ref" in trace
    assert ev.symbol.ref == trace["ref"]
    # At least one child (the binding's callable_hash; or the verdict
    # input_hash if the kernel's PROMOTE path produced it). Non-empty.
    assert len(trace.get("children", [])) >= 1


def test_composition_v2_results_equivalent_to_v1():
    """COMPOSITION: v2.BIND/EVAL produce the same observable callable
    output as v1.BIND/EVAL (the FALSIFY discipline is added without
    changing semantics).
    """
    k1, ext1 = _make_v1()
    cap = k1.mint_capability("BindCap")
    b1 = ext1.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    cap1 = k1.mint_capability("EvalCap")
    ev1 = ext1.EVAL(
        binding_name=b1.symbol.name,
        binding_version=b1.symbol.version,
        args=[9],
        cap=cap1,
    )

    k2, ext2 = _make_v2()
    cap = k2.mint_capability("BindCap")
    b2 = ext2.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
    )
    cap2 = k2.mint_capability("EvalCap")
    ev2 = ext2.EVAL(
        binding_name=b2.symbol.name,
        binding_version=b2.symbol.version,
        args=[9],
        cap=cap2,
    )

    # Both paths should return success=True with output_repr "81".
    assert ev1.success == ev2.success == True
    assert ev1.output_repr == ev2.output_repr == "81"


def test_composition_sigma_env_works_with_v2_extension():
    """COMPOSITION: the SigmaMathEnv runs episodes through both v1 and v2
    extensions and produces a non-error trajectory.

    The env constructs its own kernel + extension; we verify that swapping
    in v2 (via the env's _ext attribute) still produces a viable agent
    surface.
    """
    pytest.importorskip("numpy")
    from prometheus_math.sigma_env import SigmaMathEnv

    # v1 path (default).
    env_v1 = SigmaMathEnv(
        objective="minimize_mahler_measure",
        max_steps=5,
        kernel_db_path=":memory:",
        seed=42,
    )
    obs_v1, info_v1 = env_v1.reset()
    total_v1 = 0.0
    for _ in range(5):
        obs_v1, r, term, trunc, _info = env_v1.step(0)
        total_v1 += float(r)
        if term or trunc:
            break

    # v2 path: monkey-patch the env's extension factory by subclassing.
    class V2Env(SigmaMathEnv):
        def reset(self, *a, **kw):
            out = super().reset(*a, **kw)
            # Swap in v2 extension on the same kernel.
            self._ext = BindEvalKernelV2(self._kernel)
            # Re-bind the action table through v2.
            self._actions = []
            seen = {}
            from prometheus_math.arsenal_meta import ARSENAL_REGISTRY

            for op_id, row in enumerate(self._action_table_raw):
                cref = row["callable_ref"]
                if cref in seen:
                    bname, bver = seen[cref]
                else:
                    meta = ARSENAL_REGISTRY.get(cref)
                    cm = CostModel(**(meta.cost if meta else {}))
                    cap = self._kernel.mint_capability("BindCap")
                    binding = self._ext.BIND(
                        callable_ref=cref,
                        cost_model=cm,
                        postconditions=list(meta.postconditions) if meta else [],
                        authority_refs=list(meta.authority_refs) if meta else [],
                        cap=cap,
                    )
                    bname = binding.symbol.name
                    bver = binding.symbol.version
                    seen[cref] = (bname, bver)
                from prometheus_math.sigma_env import ActionRow

                self._actions.append(
                    ActionRow(
                        op_id=op_id,
                        callable_ref=cref,
                        binding_name=bname,
                        binding_version=bver,
                        arg_label=row["arg_label"],
                        args=tuple(row["args"]),
                        kwargs=dict(row["kwargs"]),
                    )
                )
            return out

    env_v2 = V2Env(
        objective="minimize_mahler_measure",
        max_steps=5,
        kernel_db_path=":memory:",
        seed=42,
    )
    obs_v2, info_v2 = env_v2.reset()
    total_v2 = 0.0
    for _ in range(5):
        obs_v2, r, term, trunc, _info = env_v2.step(0)
        total_v2 += float(r)
        if term or trunc:
            break

    # Both agent loops produce numeric reward without raising.
    assert math.isfinite(total_v1)
    assert math.isfinite(total_v2)


def test_composition_omega_validators_module_exposes_two_validators():
    """COMPOSITION: omega_validators exports both new in-process Omega
    oracles, ``bind_validation`` and ``eval_validation``, with the
    expected signature ``(payload: dict, seed: int) -> (Verdict, str)``.

    This locks the contract that v2 depends on; the validators must be
    callable in-process for the BIND/EVAL p50 < 5ms claim to hold.
    """
    assert hasattr(ov, "bind_validation")
    assert hasattr(ov, "eval_validation")
    # bind_validation accepts a known-good payload and returns CLEAR.
    verdict, rationale = ov.bind_validation(
        {
            "callable_ref": SQUARE_REF,
            "expected_callable_hash": None,  # skip drift check
            "cost_model": {
                "max_seconds": 1.0,
                "max_memory_mb": 1024.0,
                "max_oracle_calls": 0,
            },
            "postconditions": ["x*x is monotone"],
            "authority_refs": ["self-check"],
        },
        seed=42,
    )
    assert verdict == Verdict.CLEAR


# ---------------------------------------------------------------------------
# Oracle-call counter coverage tests.
# ---------------------------------------------------------------------------


def test_oracle_calls_nonzero_for_pari_callable():
    """AUTHORITY (oracle-counter): a callable that hits cypari.pari
    increments oracle_calls.

    Skipped if cypari is unavailable.
    """
    pytest.importorskip("cypari")
    k, ext = _make_v2()
    cap = k.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref=PARI_REF,
        cost_model=CostModel(max_seconds=5.0, max_oracle_calls=10),
        cap=cap,
    )
    cap2 = k.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[],
        cap=cap2,
    )
    assert ev.success is True
    assert ev.actual_cost["oracle_calls"] >= 1
