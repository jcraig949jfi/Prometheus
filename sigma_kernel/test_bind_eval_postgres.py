"""sigma_kernel/test_bind_eval_postgres.py — live Postgres acceptance.

Runs the full BIND/EVAL discipline against the live ``sigma_proto``
schema in ``prometheus_fire``. Skips cleanly if:

  - thesauros / psycopg2 aren't importable (no DB tooling),
  - ``~/.prometheus/db.toml`` isn't configured,
  - the ``sigma_proto`` schema isn't provisioned,
  - the connecting user lacks privileges on it.

To enable for your machine, ask Mnemosyne to apply::

    psql -h <host> -U <admin> -d prometheus_fire \\
         -v schema=sigma_proto \\
         -f sigma_kernel/migrations/002_create_bind_eval_tables.sql

Then run::

    pytest sigma_kernel/test_bind_eval_postgres.py -v

Each test cleans up its own rows on exit so re-runs are idempotent.
"""
from __future__ import annotations

import os
import time

import pytest

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import (
    BindEvalExtension,
    BudgetExceeded,
    CostModel,
    EvalError,
)


# ---------------------------------------------------------------------------
# Skip guard: only run if the live Postgres path is reachable AND the
# sigma_proto schema is provisioned.
# ---------------------------------------------------------------------------


def _live_kernel_or_skip():
    """Return a (kernel, extension) tuple against sigma_proto, or pytest.skip."""
    try:
        kernel = SigmaKernel(backend="postgres")
    except Exception as e:
        pytest.skip(f"Postgres backend unavailable: {e}")

    try:
        ext = BindEvalExtension(kernel, schema="sigma_proto")
    except ConnectionError as e:
        pytest.skip(f"sigma_proto schema not provisioned: {e}")
    return kernel, ext


# ---------------------------------------------------------------------------
# Test fixture
# ---------------------------------------------------------------------------


def _square(x):
    """Test fixture: squares its input."""
    return x * x


SQUARE_REF = "sigma_kernel.test_bind_eval_postgres:_square"


@pytest.fixture
def live_kernel():
    kernel, ext = _live_kernel_or_skip()
    # Tag this test run so cleanup can find rows we minted.
    test_tag = f"_pgtest_{os.getpid()}_{int(time.time())}"
    yield kernel, ext, test_tag
    # Cleanup: delete bindings/evaluations/symbols/capabilities rows
    # created during this test run. We tag by including ``test_tag`` in
    # binding names.
    try:
        # Delete in FK-order: evaluations -> bindings -> symbols.
        kernel.conn.execute(
            "DELETE FROM evaluations WHERE binding_name LIKE ?",
            (f"%{test_tag}%",),
        )
        kernel.conn.execute(
            "DELETE FROM bindings WHERE name LIKE ?",
            (f"%{test_tag}%",),
        )
        kernel.conn.execute(
            "DELETE FROM symbols WHERE name LIKE ?",
            (f"%{test_tag}%",),
        )
        kernel.conn.commit()
    except Exception:
        # Best-effort cleanup; if a test left state in an unexpected
        # shape, surface that on the next run as a precondition error.
        kernel.conn.rollback()


# ---------------------------------------------------------------------------
# Authority — Postgres path matches SQLite path
# ---------------------------------------------------------------------------


def test_pg_bind_eval_round_trip(live_kernel):
    kernel, ext, tag = live_kernel
    cap = kernel.mint_capability("BindCap")
    b = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
        name=f"bind_square{tag}",
        version=1,
    )
    cap2 = kernel.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=b.symbol.name,
        binding_version=b.symbol.version,
        args=[7],
        cap=cap2,
    )
    assert ev.success is True
    assert ev.output_repr == "49"


def test_pg_resolve_evaluation_symbol(live_kernel):
    """The freshly-written EVAL symbol should be RESOLVE-able through
    the kernel's content-hash check."""
    kernel, ext, tag = live_kernel
    cap = kernel.mint_capability("BindCap")
    b = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
        name=f"bind_square_resolve{tag}",
        version=1,
    )
    cap2 = kernel.mint_capability("EvalCap")
    ev = ext.EVAL(
        binding_name=b.symbol.name,
        binding_version=b.symbol.version,
        args=[3],
        cap=cap2,
    )
    sym = kernel.RESOLVE(ev.symbol.name, ev.symbol.version)
    assert sym.def_hash == ev.symbol.def_hash


# ---------------------------------------------------------------------------
# Edge — discipline holds in Postgres
# ---------------------------------------------------------------------------


def test_pg_double_spend_rejected(live_kernel):
    kernel, ext, tag = live_kernel
    cap = kernel.mint_capability("BindCap")
    ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
        name=f"bind_dbl{tag}",
        version=1,
    )
    # Re-use the same cap_id; should be rejected by the consumed=1 row.
    from sigma_kernel.sigma_kernel import CapabilityError

    with pytest.raises(CapabilityError):
        ext.BIND(
            callable_ref=SQUARE_REF,
            cost_model=CostModel(max_seconds=1.0),
            cap=cap,
            name=f"bind_dbl_again{tag}",
            version=1,
        )


def test_pg_budget_exceeded(live_kernel):
    kernel, ext, tag = live_kernel
    cap = kernel.mint_capability("BindCap")
    b = ext.BIND(
        callable_ref="time:sleep",
        cost_model=CostModel(max_seconds=0.05),
        cap=cap,
        name=f"bind_sleep{tag}",
        version=1,
    )
    cap2 = kernel.mint_capability("EvalCap")
    with pytest.raises(BudgetExceeded):
        ext.EVAL(
            binding_name=b.symbol.name,
            binding_version=b.symbol.version,
            args=[0.2],
            cap=cap2,
        )


# ---------------------------------------------------------------------------
# Composition — substrate state is observable
# ---------------------------------------------------------------------------


def test_pg_substrate_state_visible_after_eval(live_kernel):
    """After 3 EVALs, the bindings/evaluations tables in sigma_proto have
    the expected counts visible via raw SELECT."""
    kernel, ext, tag = live_kernel
    cap = kernel.mint_capability("BindCap")
    b = ext.BIND(
        callable_ref=SQUARE_REF,
        cost_model=CostModel(max_seconds=1.0),
        cap=cap,
        name=f"bind_count{tag}",
        version=1,
    )
    for i in range(3):
        c = kernel.mint_capability("EvalCap")
        ext.EVAL(
            binding_name=b.symbol.name,
            binding_version=b.symbol.version,
            args=[i],
            cap=c,
            eval_version=i + 1,
        )
    # Read directly from the schema.
    cur = kernel.conn.execute(
        "SELECT COUNT(*) FROM evaluations WHERE binding_name=?",
        (b.symbol.name,),
    )
    n = cur.fetchone()[0]
    assert n == 3
