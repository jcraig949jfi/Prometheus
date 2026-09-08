"""WP-B1 acceptance tests: B1-a, B1-b, B1-c, B1-d, plus the purity property.

The library is the semantic owner's deliverable; these tests are what make it safe for Vivarium
to wrap blind. Fixtures are hand-authored with their expected behaviour written down, so a test
failing here means the VM disagrees with human intent, not that a snapshot moved.
"""
from __future__ import annotations

import ast
import json
import os
import sys

import pytest

from proteus.eval import fixtures as F
from proteus.eval.library import (BudgetPolicy, EvaluationError, evaluate, input_sensitivity,
                                  make_spec, relabel_opcode_aliases)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRY = os.path.join(ROOT, "proteus", "integration", "PLAYER_REGISTRY.json")
LIB = os.path.join(ROOT, "proteus", "eval", "library.py")

if os.path.join(ROOT, "integration") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "integration"))


# =============================================================== B1-a  hand-authored semantics

def test_b1a_echo_passes_every_case():
    r = evaluate(F.ECHO, F.echo_spec((1, 2, 3)))
    assert r["all_passed"] and r["witness"] is None
    assert r["cases_passed"] == 3


def test_b1a_arithmetic_is_correct():
    """20 + 22 = 42, by hand."""
    r = evaluate(F.ADD_20_22, F.constant_spec(42, 2))
    assert r["all_passed"], r["cases"][0]["outputs"]


def test_b1a_input_consumption_order():
    """Two IN instructions consume two values from the same channel, in order."""
    r = evaluate(F.SUM_TWO_INPUTS, F.sum_spec(((1, 2), (10, 20))))
    assert r["all_passed"]


def test_b1a_output_cap_is_enforced():
    """Five OUTs into a channel with out_cap 2 yield exactly 2 values; the rest are dropped."""
    r = evaluate(F.OVERFLOW, F.no_expectation_spec())
    assert [len(ch) for ch in r["cases"][0]["outputs"]] == [2]


def test_b1a_exact_first_counterexample_under_declared_ordering():
    """THE central B1-a claim. CONST_ONE emits 1 always; the echo spec is 1,2,3.

    Case 0 passes (input 1 -> 1). Case 1 MUST be the witness: expected [[2]], observed [[1]].
    Case 2 also fails but is NOT the witness, because the ordering is case index ascending.
    """
    r = evaluate(F.CONST_ONE, F.echo_spec((1, 2, 3)))
    w = r["witness"]
    assert w is not None
    assert w["case_index"] == 1
    assert w["expected"] == [[2]]
    assert w["observed"] == [[1]]
    assert w["reason"] == "output_mismatch"
    assert r["cases_passed"] == 1


def test_b1a_witness_is_the_lowest_failing_index_not_merely_a_failing_one():
    """Reordering the same cases moves the witness, proving order is what selects it."""
    r = evaluate(F.CONST_ONE, F.echo_spec((3, 2, 1)))
    assert r["witness"]["case_index"] == 0          # first case now fails
    r2 = evaluate(F.CONST_ONE, F.echo_spec((1, 3, 2)))
    assert r2["witness"]["case_index"] == 1


def test_b1a_case_without_expectation_can_never_be_the_witness():
    r = evaluate(F.HALT_NOW, F.no_expectation_spec())
    assert r["witness"] is None
    assert r["cases_with_expectation"] == 0


# =============================================================== B1-b  arena parity + blindness

def _specimens():
    with open(REGISTRY, encoding="utf-8") as f:
        return [e["manifest"] for e in json.load(f)["entries"]]


@pytest.mark.parametrize("inputs", [[[1]], [[7, 9]], [[]]])
def test_b1b_all_64_specimens_agree_with_the_arena_path(inputs):
    """The library must reproduce the arena's execution EXACTLY for every committed specimen."""
    import harmonia_arena as arena
    plan = {"inputs": inputs, "n_out": 1, "ticks": 4, "seed": 20260908}
    spec = make_spec([{"inputs": inputs, "expected": None}], n_out=1, ticks=4)
    specimens = _specimens()
    assert len(specimens) == 64
    for man in specimens:
        a = arena.execute(man, plan)
        c = evaluate(man, spec, seed=plan["seed"])["cases"][0]
        assert a["transcript"] == c["outputs_all_ticks"]
        assert a["statuses"] == c["statuses_all_ticks"]
        assert a["ticks_run"] == c["steps"]


def test_b1b_world_blindness_is_reported_and_no_specimen_is_called_an_agent():
    """Report blindness; refuse to promote the rest to 'responsive agents'."""
    sets = [[[1]], [[2]], [[7, 7]]]
    blind = 0
    for man in _specimens():
        rep = input_sensitivity(man, sets, n_out=1, ticks=4)
        assert set(rep) >= {"world_blind", "distinct_execution_signatures", "claim_boundary"}
        assert "agent" not in rep or rep.get("agent") is None
        assert "not a claim that the program is an agent" in rep["claim_boundary"]
        blind += rep["world_blind"]
    # Harmonia measured ~75% world-blind on this channel. Assert only the direction, because the
    # exact fraction depends on the input sets and is WP-B4's business, not B1's.
    assert blind > 0, "no specimen was world-blind, which contradicts the 09-05 measurement"
    assert blind < 64, "every specimen world-blind would make arena parity vacuous"


# =============================================================== B1-c  defined edge results

def test_b1c_zero_budget_is_defined():
    r = evaluate(F.ECHO, F.echo_spec((1,)), step_budget=0)
    c = r["cases"][0]
    assert c["steps"] == 0 and c["outputs"] == [] and c["status"] == "budget"


def test_b1c_minimum_budget_runs_exactly_one_tick():
    r = evaluate(F.ECHO, F.echo_spec((1,)), step_budget=1)
    assert r["cases"][0]["steps"] == 1


def test_b1c_budget_exhaustion_is_a_status_and_not_a_counterexample_by_default():
    """THE DECLARED CONTRACT. SPIN never halts; it exhausts its op budget every tick."""
    r = evaluate(F.SPIN, F.echo_spec((1, 2, 3)))
    assert r["budget_policy"] == BudgetPolicy.STATUS_ONLY
    assert r["budget_exhaustion_is_counterexample"] is False
    assert r["status_counts"] == {"budget": 3}
    assert r["witness"] is None, "an exhausted case became a witness under the default policy"
    assert r["cases_passed"] == 0


def test_b1c_budget_exhaustion_becomes_a_counterexample_only_when_opted_in():
    r = evaluate(F.SPIN, F.echo_spec((1, 2, 3)), budget_policy=BudgetPolicy.COUNTEREXAMPLE)
    assert r["budget_exhaustion_is_counterexample"] is True
    assert r["witness"]["case_index"] == 0
    assert r["witness"]["reason"] == "budget_exhausted"


def test_b1c_policy_can_only_move_the_witness_earlier():
    """Switching policy may surface an earlier exhausted case; it never picks a different late one."""
    spec = make_spec([{"inputs": [[1]], "expected": [[1]]}], n_out=1, ticks=4)
    a = evaluate(F.SPIN, spec)
    b = evaluate(F.SPIN, spec, budget_policy=BudgetPolicy.COUNTEREXAMPLE)
    assert a["witness"] is None and b["witness"]["case_index"] == 0


def test_b1c_absent_output_is_defined_not_an_error():
    """HALT_NOW emits nothing. That is a normal observation with a witness, not a crash."""
    r = evaluate(F.HALT_NOW, F.echo_spec((1,)))
    c = r["cases"][0]
    assert c["no_output"] is True and c["emitted_any_value"] is False
    assert c["status"] == "halt"
    assert r["witness"]["observed"] == [[]]


def test_b1c_every_word_decodes_so_there_is_no_invalid_opcode():
    """op = word mod 25, so no uint32 is an invalid opcode. Asserted, because it is a contract."""
    prog = F.program([2 ** 32 - 1, 3, 4, 5, F.HALT, 0, 0, 0])
    r = evaluate(prog, F.no_expectation_spec())
    assert r["cases"][0]["status"] in ("halt", "yield", "budget")


def test_b1c_malformed_program_and_spec_fail_closed():
    with pytest.raises(EvaluationError):
        evaluate({"schema_version": "proteus.player_manifest.v0"}, F.echo_spec())
    with pytest.raises(EvaluationError):
        evaluate(F.ECHO, {"schema_version": "nope", "cases": []})
    with pytest.raises(EvaluationError):
        evaluate(F.ECHO, F.echo_spec(), budget_policy="whatever")
    with pytest.raises(EvaluationError):
        make_spec([])
    with pytest.raises(EvaluationError):
        make_spec([{"inputs": [[-1]]}])


def test_b1c_unordered_specification_is_refused():
    """'First' is undefined without a total order, so the library refuses rather than guessing."""
    from proteus.eval.library import validate_spec
    spec = F.echo_spec((1, 2, 3))
    spec["cases"] = [spec["cases"][2], spec["cases"][0], spec["cases"][1]]
    with pytest.raises(EvaluationError, match="ascending"):
        validate_spec(spec)


# =============================================================== B1-d  replay, relabelling, trace

def test_b1d_replay_is_exact():
    a = evaluate(F.ECHO, F.echo_spec((1, 2, 3)), seed=7)
    b = evaluate(F.ECHO, F.echo_spec((1, 2, 3)), seed=7)
    assert a == b


def test_b1d_semantic_opcode_relabelling_preserves_execution():
    """w and w + 25 decode to the same instruction. For programs that do not read their own
    code as data, execution must be identical."""
    for prog in (F.ECHO, F.ADD_20_22, F.SUM_TWO_INPUTS, F.HALT_NOW):
        base = evaluate(prog, F.no_expectation_spec())
        for k in (1, 2):
            alt = evaluate(relabel_opcode_aliases(prog, k), F.no_expectation_spec())
            for ca, cb in zip(base["cases"], alt["cases"]):
                assert ca["outputs_all_ticks"] == cb["outputs_all_ticks"]
                assert ca["statuses_all_ticks"] == cb["statuses_all_ticks"]
                assert ca["ops"] == cb["ops"]


def test_b1d_relabelling_changes_bytes_and_therefore_identity():
    """Instruction-identical is NOT byte-identical. Identity must move even though behaviour does not."""
    from proteus.foundry.identity import hash_obj
    assert hash_obj(F.ECHO) != hash_obj(relabel_opcode_aliases(F.ECHO, 1))


def test_b1d_relabelling_overflow_fails_closed():
    with pytest.raises(EvaluationError):
        relabel_opcode_aliases(F.ECHO, 10 ** 9)


def test_b1d_trace_truncation_is_explicit_and_changes_nothing():
    """Trace is passive: limit 0 vs unbounded must agree on everything but the trace."""
    spec = F.echo_spec((1, 2, 3))
    full = evaluate(F.SPIN, spec, trace_limit=10 ** 6)
    none = evaluate(F.SPIN, spec, trace_limit=0)
    for cf, cn in zip(full["cases"], none["cases"]):
        for k in ("outputs", "outputs_all_ticks", "statuses_all_ticks", "status", "steps",
                  "ops", "passed"):
            assert cf[k] == cn[k]
        # limit 0 records nothing, and that IS truncation -- reported, never silent
        assert cn["trace"] == [] and cn["trace_truncated"] is True
        assert cn["trace_events_dropped"] == cn["steps"]
    assert full["witness"] == none["witness"]


def test_b1d_truncation_is_reported_when_it_happens():
    r = evaluate(F.SPIN, F.echo_spec((1,)), step_budget=5, trace_limit=2)
    c = r["cases"][0]
    assert c["trace_truncated"] is True and c["trace_events_dropped"] == 3
    assert len(c["trace"]) == 2


# =============================================================== purity

def test_library_performs_no_io_and_reads_no_registry_or_fossils():
    """Enforced over the module's own AST, not promised in a docstring."""
    with open(LIB, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    banned_calls = {"open", "print", "input", "exec", "eval", "compile", "__import__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in banned_calls, f"library calls {node.func.id}()"
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = (node.module or "") if isinstance(node, ast.ImportFrom) else \
                node.names[0].name
            root = mod.split(".")[0]
            assert root in ("proteus", "__future__"), f"library imports {mod!r}"
    # Scan STRING LITERALS only, never docstrings: the module docstring legitimately says
    # "reads no registry", and a naive text scan would flag its own honesty.
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            d = ast.get_docstring(node, clean=False)
            if d:
                docstrings.add(d)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in docstrings:
                continue
            low = node.value.lower()
            for forbidden in ("player_registry", "fossil", ".json", "http", "/v2/"):
                assert forbidden not in low, f"library embeds {forbidden!r} in a literal"
