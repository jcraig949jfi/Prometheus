"""H1 Boolean substrate tests: grammar, compile/evaluate parity, controls, and the five fixtures.

The declared finite correctness scope is EXHAUSTIVE over all 8 assignments for 3-input tasks, for
the expression set enumerated in EXPRESSIONS below. Nothing here is verified for wider arities.
"""
from __future__ import annotations

import itertools
import json
import os

import pytest

from proteus.eval import boolean as B
from proteus.eval import boolean_population as P
from proteus.eval.genome_read import genome_read_report, perturb_genome
from proteus.eval.library import BudgetPolicy, evaluate, make_spec

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY = os.path.join(ROOT, "proteus", "integration", "PLAYER_REGISTRY.json")

I, C, Not, And, Or, Xor = B.I, B.C, B.Not, B.And, B.Or, B.Xor

#: The declared expression set. Every one is verified exhaustively over all 8 assignments.
EXPRESSIONS = {
    "const0": C(0), "const1": C(1),
    "i0": I(0), "i1": I(1), "i2": I(2),
    "not_i0": Not(I(0)), "not_i2": Not(I(2)),
    "and01": And(I(0), I(1)), "or02": Or(I(0), I(2)), "xor12": Xor(I(1), I(2)),
    "xor3": Xor(Xor(I(0), I(1)), I(2)),
    "majority": Or(And(I(0), I(1)), Or(And(I(0), I(2)), And(I(1), I(2)))),
    "nand01": Not(And(I(0), I(1))),
    "implies": Or(Not(I(0)), I(1)),
    "nested": Not(Xor(And(I(0), Not(I(1))), Or(I(2), C(1)))),
    "deep": Xor(And(Or(I(0), I(1)), Not(I(2))), Xor(I(0), And(I(1), I(2)))),
}


# =============================================================== grammar / type fixture

def test_type_fixture_rejects_malformed_expressions():
    for bad in [("nope", 1), (B.AND, I(0)), (B.NOT,), I(0)[0], 42, (),
                (B.INPUT, 7), (B.CONST, 2), (B.AND, I(0), I(1), I(2))]:
        with pytest.raises(B.BooleanError):
            B.check(bad)


def test_type_fixture_constructors_validate_eagerly():
    with pytest.raises(B.BooleanError):
        C(2)
    with pytest.raises(B.BooleanError):
        I(3)
    with pytest.raises(B.BooleanError):
        I(True)          # bool is not an acceptable index


def test_independent_evaluator_stays_in_the_boolean_domain():
    for e in EXPRESSIONS.values():
        assert set(B.truth_table(e)) <= {0, 1}


def test_assignment_order_is_the_declared_one():
    a = B.assignments()
    assert a[0] == [0, 0, 0] and a[7] == [1, 1, 1]
    assert a[1] == [0, 0, 1], "input 0 must be most significant"
    assert B.truth_table(I(0)) == [0, 0, 0, 0, 1, 1, 1, 1]


# =============================================================== compile/evaluate parity

@pytest.mark.parametrize("name", sorted(EXPRESSIONS))
def test_compile_evaluate_parity_exhaustive_over_all_8_inputs(name):
    """THE central H1 claim: the VM agrees with the INDEPENDENT oracle on every assignment."""
    expr = EXPRESSIONS[name]
    man, res = B.run_boolean(expr)
    assert res["cases_total"] == 8
    assert res["all_passed"], f"{name}: witness {res['witness']}"
    observed = [c["outputs"][0][0] for c in res["cases"]]
    assert observed == B.truth_table(expr)


def test_compiler_emits_only_declared_opcodes():
    for expr in EXPRESSIONS.values():
        g = B.compile_boolean(expr)["genome"]
        assert all(w in B.DECLARED_OPCODES for w in g[::4])


def test_not_is_not_the_vm_not_opcode():
    """The VM's NOT is bitwise complement; using it would leave {0,1} on the first negation."""
    g = B.compile_boolean(Not(I(0)))["genome"]
    assert 13 not in g[::4], "compiler emitted the bitwise NOT opcode"
    assert B.run_boolean(Not(I(0)))[1]["all_passed"]


def test_temporary_pressure_depends_on_tree_shape_not_node_count():
    """Codegen emits left at t and right at t+1, so LEFT-deep nesting reuses one temporary.

    Register pressure is therefore a property of the tree SHAPE. A left-leaning chain of 20 ANDs
    compiles fine; the same node count leaning right exhausts the declared 11 temporaries. Both
    are asserted so the bound is understood rather than discovered later by a corrupt result.
    """
    left = I(0)
    for _ in range(20):
        left = And(left, I(1))
    B.compile_boolean(left)                      # must NOT raise

    right = I(0)
    for _ in range(20):
        right = And(I(1), right)
    with pytest.raises(B.BooleanError, match="temporaries"):
        B.compile_boolean(right)


# =============================================================== positive / negative controls

@pytest.mark.parametrize("name", sorted(P.POSITIVE_CONTROLS))
def test_hand_built_positive_control_output_changes_with_its_input(name):
    """Hand-built, NOT compiled: an independent check that the channel carries three bits."""
    man, j = P.POSITIVE_CONTROLS[name]
    spec = B.boolean_spec(I(j))
    res = evaluate(man, spec)
    assert res["all_passed"], f"{name} does not implement identity on input {j}"
    observed = [c["outputs"][0][0] for c in res["cases"]]
    assert observed == B.truth_table(I(j))
    assert len(set(observed)) == 2, "output never changed; the control is not input-sensitive"


def test_hand_built_controls_agree_with_the_compiler():
    """Two independent routes to the same function must agree."""
    for name, (man, j) in P.POSITIVE_CONTROLS.items():
        spec = B.boolean_spec(I(j))
        hand = [c["outputs"] for c in evaluate(man, spec)["cases"]]
        comp = [c["outputs"] for c in evaluate(B.compile_boolean(I(j)), spec)["cases"]]
        assert hand == comp, name


def test_negative_control_is_input_blind():
    """BLIND never executes IN, so no assignment can change its output."""
    spec = make_spec([{"inputs": [list(a)], "expected": None} for a in B.assignments()],
                     n_out=1, ticks=2)
    outs = [c["outputs"] for c in evaluate(P.BLIND, spec)["cases"]]
    assert len(set(json.dumps(o) for o in outs)) == 1
    assert 21 not in P.BLIND["genome"][::4], "the blind control executes IN"


def test_negative_control_fails_a_task_that_needs_input():
    res = evaluate(P.BLIND, B.boolean_spec(I(0)))
    assert not res["all_passed"] and res["witness"] is not None


# =============================================================== reset fixture

def test_reset_fixture_each_case_starts_from_a_fresh_state():
    """persist='none' and a fresh Player per case: case order must not affect any result."""
    expr = EXPRESSIONS["xor3"]
    fwd = evaluate(B.compile_boolean(expr), B.boolean_spec(expr))
    rev_spec = make_spec(
        [{"inputs": [list(a)], "expected": [[v]]}
         for a, v in zip(reversed(B.assignments()), reversed(B.truth_table(expr)))],
        n_out=1, ticks=2)
    rev = evaluate(B.compile_boolean(expr), rev_spec)
    assert fwd["all_passed"] and rev["all_passed"]
    assert [c["outputs"] for c in fwd["cases"]] == \
           [c["outputs"] for c in reversed(rev["cases"])]


def test_reset_fixture_repeat_evaluation_is_identical():
    expr = EXPRESSIONS["majority"]
    a = evaluate(B.compile_boolean(expr), B.boolean_spec(expr), seed=3)
    b = evaluate(B.compile_boolean(expr), B.boolean_spec(expr), seed=3)
    assert a == b


# =============================================================== budget fixture

def test_budget_fixture_exhaustion_is_a_status_not_a_witness():
    """B1's contract, preserved: a starved run is not a wrong answer."""
    expr = EXPRESSIONS["majority"]
    man = B.compile_boolean(expr)
    starved = dict(man, tick_budget=8)          # too few ops to finish
    res = evaluate(starved, B.boolean_spec(expr))
    assert res["status_counts"].get("budget", 0) > 0
    assert res["witness"] is None, "budget exhaustion produced a witness under the default policy"
    assert res["all_passed"] is False


def test_budget_fixture_opt_in_makes_exhaustion_a_witness():
    expr = EXPRESSIONS["majority"]
    starved = dict(B.compile_boolean(expr), tick_budget=8)
    res = evaluate(starved, B.boolean_spec(expr), budget_policy=BudgetPolicy.COUNTEREXAMPLE)
    assert res["witness"] is not None
    assert res["witness"]["reason"] == "budget_exhausted"


def test_budget_fixture_no_witness_is_never_solved():
    """C3: witness == null does not mean correct. Coverage must be complete."""
    expr = EXPRESSIONS["xor3"]
    starved = dict(B.compile_boolean(expr), tick_budget=8)
    res = evaluate(starved, B.boolean_spec(expr))
    assert res["witness"] is None
    assert not res["all_passed"], "no-witness was mistaken for solved"
    assert res["cases_passed"] < res["cases_with_expectation"]


# =============================================================== output-cap fixture

def test_output_cap_fixture_is_enforced_and_declared():
    HALT, LDC, OUT = 1, 3, 23
    g = [LDC, 0, 1, 0] + [OUT, 0, 15, 0] * 5 + [HALT, 0, 0, 0]
    man = dict(P.BLIND, genome=g, out_cap=2)
    spec = make_spec([{"inputs": [[0, 0, 0]], "expected": None}], n_out=1, ticks=2)
    res = evaluate(man, spec)
    assert [len(ch) for ch in res["cases"][0]["outputs"]] == [2]


def test_boolean_programs_emit_exactly_one_value():
    for expr in EXPRESSIONS.values():
        res = evaluate(B.compile_boolean(expr), B.boolean_spec(expr))
        for c in res["cases"]:
            assert [len(ch) for ch in c["outputs"]] == [1]


# =============================================================== independent-oracle parity fixture

def test_oracle_recomputes_labels_and_never_trusts_a_transferred_one():
    """A witness pack carries INPUTS. Labels are recomputed by the target oracle."""
    expr = EXPRESSIONS["xor3"]
    pack_inputs = [[0, 0, 1], [1, 1, 0], [1, 0, 1]]
    recomputed = B.oracle_labels(expr, pack_inputs)
    assert recomputed == [_ref(expr, a) for a in pack_inputs]
    # a WRONG source label cannot corrupt the target: it is never read
    wrong = [1 - v for v in recomputed]
    assert B.oracle_labels(expr, pack_inputs) == recomputed != wrong


def _ref(expr, a):
    return B.truth_table(expr)[B.assignments().index(list(a))]


def test_oracle_rejects_out_of_domain_inputs():
    with pytest.raises(B.BooleanError):
        B.oracle_labels(I(0), [[0, 1]])
    with pytest.raises(B.BooleanError):
        B.oracle_labels(I(0), [[0, 1, 2]])


def test_correctness_scope_is_stated_and_honest():
    s = B.correctness_scope()
    assert s["arity_exhaustively_verified"] == 3
    assert s["assignments_per_task"] == 8
    assert s["verified_beyond_3_inputs"] is False
    assert s["interface_version"] == B.INTERFACE_VERSION


# =============================================================== genome_read (D-16)

def test_genome_read_is_exposed_in_results():
    expr = EXPRESSIONS["and01"]
    _man, res = B.run_boolean(expr, genome_read=True)
    gr = res["genome_read"]
    assert gr["schema_version"] == "proteus.genome_read.v1"
    assert gr["detected"] is False
    assert gr["covered_word_slots"] == [0, 1] and gr["uncovered_word_slots"] == [2, 3]
    assert "LOWER BOUND" in gr["bound"]


def test_genome_read_detects_a_program_that_reads_its_own_genome():
    """POSITIVE CONTROL. A gate that cannot fire is worthless."""
    HALT, LDC, LD, OUT = 1, 3, 5, 23
    reader = dict(P.BLIND, genome=[LDC, 0, 0, 0, LD, 1, 0, 0, OUT, 1, 15, 0, HALT, 0, 0, 0])
    spec = make_spec([{"inputs": [[0, 0, 0]], "expected": None}], n_out=1, ticks=2)
    assert genome_read_report(reader, spec)["detected"] is True


def test_perturbation_is_instruction_invariant():
    """The differential is only sound if the perturbation cannot change a decoded instruction."""
    from proteus.foundry.affordances import N_OPCODES
    man = B.compile_boolean(EXPRESSIONS["xor3"])
    alt = perturb_genome(man, 2, 3)
    g, h = man["genome"], alt["genome"]
    for i in range(0, len(g), 4):
        assert h[i] % N_OPCODES == g[i] % N_OPCODES          # same opcode
        assert h[i + 1] % man["n_regs"] == g[i + 1] % man["n_regs"]   # same operand a
        assert h[i + 2] == g[i + 2] and h[i + 3] == g[i + 3]          # raw slots untouched


# =============================================================== population isolation

def test_named_population_does_not_mutate_the_frozen_registry():
    with open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)
    assert reg["registry_id"] == \
        "b15e0a7f5f2dcb99b8b28c73a99441d8d53e82b1bae42fddd5e274eeef396917"
    assert len(reg["entries"]) == 64
    frozen = {e["organism_id"] for e in reg["entries"]}
    for m in P.population()["members"]:
        assert m["organism_ref"].split(":", 1)[1] not in frozen


def test_population_declares_its_interface_and_channel_contract():
    pop = P.population()
    assert pop["interface_version"] == "proteus.boolean3.v0"
    assert pop["n_inputs"] == 3
    assert set(pop["channel_contract"]) >= {"inputs", "n_out", "output"}
    roles = {m["role"] for m in pop["members"]}
    assert roles == {"positive_control", "negative_control"}


def test_no_task_truth_reaches_the_player():
    """A candidate's manifest must not contain the truth table it is being tested against."""
    for expr in EXPRESSIONS.values():
        tt = B.truth_table(expr)
        g = B.compile_boolean(expr)["genome"]
        # the compiled genome may hold constants 0/1, but never the ordered 8-vector
        assert not any(g[i:i + 8] == tt for i in range(max(0, len(g) - 8)))
