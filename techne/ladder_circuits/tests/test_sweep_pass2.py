"""Second-pass instrument sweep, cycle 022 — R3 resolved, R0 swept, and a limit found.

Rungs built before cycle 018 have never met the standing instruments. This suite sweeps them in
loop-label order and records what each yields. Two results this cycle:

1. **R3's outstanding ledger claim was TOO BROAD and is narrowed, not struck.** The cycle-006
   twins alias the FIFO pipelines and do NOT alias the LIFO ones. FIFO and LIFO views are
   incomparable, so incapacity holds per observation class — exactly the precondition failure
   cycle 019 predicted, now found in the wild.

2. **The aliasing instrument has a blind spot**, found by sweeping R0. It detects merging and is
   silent on splitting, and R0's actual defect is splitting.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from prometheus_math.partition import induced_partition, refines  # noqa: E402
from techne.ladder_circuits.aliasing import (  # noqa: E402
    find_aliasing_witness, verify_factorization, verify_family_incapacity,
)
from techne.ladder_circuits.r0_pattern import (  # noqa: E402
    CanonicalizingCircuit, R0PatternCircuit, ast_key, canonical_key,
)
from techne.ladder_circuits.r3_constraint_store import (  # noqa: E402
    ConstraintStoreCircuit, FixedWidthPipeline, indistinguishable_twins,
)
from techne.ladder_circuits.sweep import (  # noqa: E402
    find_splitting_witness, sweep_projection, twins_for_policy,
)


def _final_answer(circuit, events, query):
    return circuit.run(list(events) + [query])[-1]


# ---- R3 (canon R2): the outstanding ledger claim ------------------------------------------------

def test_R3_the_cycle_006_twins_DO_alias_the_fifo_family():
    """The half of the ledger claim that survives. Under FIFO the flood evicts `xq`, so the two
    histories leave identical bounded state and the queried proposition differs."""
    W = 3
    h_t, h_f, query = indistinguishable_twins(W, policy="fifo")
    instances = [("H_T", h_t, True), ("H_F", h_f, False)]

    projection = lambda inst: tuple(
        sorted(FixedWidthPipeline(width=W, policy="fifo").run(list(inst[1])) or []) +
        sorted(_state_after(inst[1], W, "fifo")))
    truth = lambda inst: inst[2]

    w = find_aliasing_witness(instances, projection, truth,
                              note="width-3 FIFO retained state, the finest view in the family")
    assert w is not None

    result = verify_family_incapacity(
        family=[1, 2, 3],
        evaluate=lambda width, inst: _final_answer(
            FixedWidthPipeline(width=width, policy="fifo"), inst[1], query),
        witness=w,
    )
    assert result["all_members_err"] and result["all_members_aliased"]


def _state_after(events, width, policy):
    p = FixedWidthPipeline(width=width, policy=policy)
    p.run(list(events))
    return list(p._state.keys())


def test_R3_FINDING_the_same_twins_do_NOT_alias_the_lifo_family():
    """**The defect. The ledger's "R3 capacity width" aliasing claim was unqualified and the
    cycle-006 witness is FIFO-specific.**

    LIFO evicts the most recent arrival, so a fact declared FIRST is exactly the one it keeps.
    `xq` is declared first in H_T, survives the flood, and the LIFO pipeline answers correctly
    on both twins — no aliasing at all.
    """
    W = 3
    h_t, h_f, query = indistinguishable_twins(W, policy="fifo")
    lifo = lambda events: _final_answer(
        FixedWidthPipeline(width=W, policy="lifo"), events, query)
    assert lifo(h_t) is True and lifo(h_f) is False       # separates them perfectly
    assert _state_after(h_t, W, "lifo") != _state_after(h_f, W, "lifo")


def test_R3_REPAIR_a_policy_specific_pair_aliases_each_class():
    """The repair is not a cleverer pair — it is one pair per observation class. `xq` must
    arrive LAST to be the fact LIFO evicts."""
    W = 3
    for policy in ("fifo", "lifo"):
        h_t, h_f, query = twins_for_policy(W, policy)
        run = lambda events: _final_answer(
            FixedWidthPipeline(width=W, policy=policy), events, query)
        assert _state_after(h_t, W, policy) == _state_after(h_f, W, policy)   # aliased state
        assert run(h_t) == run(h_f)                                          # same answer
        assert run(h_t) is False                                             # wrong on H_T


def test_R3_FIFO_and_LIFO_VIEWS_ARE_INCOMPARABLE():
    """Why the claim has to be per-class: neither view factors through the other, so there is no
    finest projection for the union of the two policies short of the full history. Exactly the
    situation cycle 019 said to partition rather than paper over."""
    W = 2
    histories = [
        [("declare_nonzero", "a"), ("declare_nonzero", "b"), ("declare_nonzero", "c")],
        [("declare_nonzero", "c"), ("declare_nonzero", "b"), ("declare_nonzero", "a")],
        [("declare_nonzero", "a"), ("declare_nonzero", "b")],
        [("declare_nonzero", "b"), ("declare_nonzero", "a"), ("declare_nonzero", "b")],
    ]
    fifo = lambda h: tuple(sorted(_state_after(h, W, "fifo")))
    lifo = lambda h: tuple(sorted(_state_after(h, W, "lifo")))
    assert not verify_factorization(histories, fifo, lifo)
    assert not verify_factorization(histories, lifo, fifo)
    n = len(histories)
    assert not refines(induced_partition(histories, fifo),
                       induced_partition(histories, lifo), n)
    assert not refines(induced_partition(histories, lifo),
                       induced_partition(histories, fifo), n)


def test_R3_the_unbounded_store_is_correct_on_every_twin_pair():
    """The separation the rung is actually about survives the narrowing: the constraint store
    answers both twins correctly, under both policies' pairs."""
    for policy in ("fifo", "lifo"):
        h_t, h_f, query = twins_for_policy(3, policy)
        assert _final_answer(ConstraintStoreCircuit(), h_t, query) is True
        assert _final_answer(ConstraintStoreCircuit(), h_f, query) is False


# ---- R0 (canon R0): the instrument's blind spot ---------------------------------------------------

def test_R0_HAS_NO_ALIASING_WITNESS_and_that_is_not_a_clean_bill_of_health():
    """Sweeping R0 with the instrument alone reports "sufficient", because exact-AST keys never
    merge two distinct expressions. Every rung swept so far yielded an aliasing defect; this one
    does not, and the reason is that its defect is in the other direction."""
    x, y, a, b = sp.symbols("x y a b")
    exprs = [x + y, a + b, x * y, a * b]
    truth = lambda e: canonical_key(e)                 # the answer depends only on the shape
    assert find_aliasing_witness(exprs, ast_key, truth) is None


def test_R0_FINDING_the_defect_is_SPLITTING_which_aliasing_cannot_see():
    """**The limit found by the sweep.** `x + y` and `a + b` share an answer and receive
    different exact-AST keys. That is over-discrimination: not an impossibility — the circuit can
    be right about both by storing both — but evidence about one does not transfer to the other.

    The dual instrument reports it, and reports explicitly that it proves no impossibility.
    """
    x, y, a, b = sp.symbols("x y a b")
    exprs = [x + y, a + b, x * y, a * b]
    truth = lambda e: canonical_key(e)

    w = find_splitting_witness(exprs, ast_key, truth, note="exact-AST splits renamed twins")
    assert w is not None
    assert w.left_projection != w.right_projection and w.shared_truth is not None
    assert w.proves_impossibility is False

    report = sweep_projection("R0", exprs, ast_key, truth)
    assert not report.incapacity_proved
    assert report.verdict.startswith("SPLIT")
    assert report.n_split_pairs == 2                   # the two renamed pairs


def test_R0_the_canonicalizing_circuit_closes_the_split():
    """And the dual witness dissolves under the repair the rung already had — which is the
    check that the instrument is measuring the right thing."""
    x, y, a, b = sp.symbols("x y a b")
    exprs = [x + y, a + b, x * y, a * b]
    truth = lambda e: canonical_key(e)
    assert find_splitting_witness(exprs, canonical_key, truth) is None

    exact, canon = R0PatternCircuit(), CanonicalizingCircuit()
    exact.train(x + y, "sum")
    canon.train(x + y, "sum")
    assert exact.answer(a + b) is None                 # abstains: no transfer
    assert canon.answer(a + b) == "sum"                # transfers


def test_R0_SECOND_FINDING_the_exact_AST_key_cannot_see_commutative_reordering():
    """A separate defect, of the cycle-013 family: the key measures the CAS, not the circuit.
    `x + y` and `y + x` have IDENTICAL sreprs because sympy normalises commutative arguments at
    construction, so the circuit's advertised "identity congruence" is partly delivered by
    sympy rather than by the circuit. Not fatal — but it is not the circuit's own doing, and a
    claim about the circuit's discrimination should not rest on it.
    """
    x, y = sp.symbols("x y")
    assert ast_key(x + y) == ast_key(y + x)
    assert ast_key(x * y) == ast_key(y * x)
    circuit = R0PatternCircuit()
    circuit.train(x + y, "sum")
    assert circuit.answer(y + x) == "sum"              # retrieval the circuit did not earn


# ---- sweep bookkeeping ------------------------------------------------------------------------

def test_sweep_records_which_rungs_remain_unswept():
    """Honest bookkeeping, so the cap on this sweep is legible. Cycle 022 covered R0 and R3;
    R1, R2, R4, R5, R7 and R8 remain, and cycle 023 is the last sweep cycle before the second
    pass moves to composition or real substrate regardless."""
    swept = {"R0", "R3", "R6", "R9", "R10", "R11", "R12"}
    remaining = {"R1", "R2", "R4", "R5", "R7", "R8"}
    assert not (swept & remaining)
    assert len(swept | remaining) == 13
