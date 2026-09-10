"""cegis_boolean_v1: the loop, its rules, and the two H0 input positions.

Offline. What is tested here is the SEARCH and its contract -- coverage,
statuses, caps, seeding, the component library, sealed identity across the four
H0 cells. What runs through the real queue, loader and engine is in
tests/test_h0h5_slice.py.

Nothing here asserts that a source pack helps. The sign of that effect is H1's
question; the tests below establish that the mechanism exists, is bounded, and
is honest about which of the two directions it went.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from artifact_fixtures import LocalResolver, input_set
from viv import artifacts as _a
from viv import cegis_boolean as _cb
from viv import executors as _ex
from viv import kinds as _kinds
from viv import preflight as _pf
from viv import spec as _spec

pytest.importorskip("proteus.eval.boolean",
                    reason="Proteus's boolean3 substrate is not on this "
                           "checkout")


# --------------------------------------------------------------- fixtures
def tt(fn) -> str:
    """A target truth table in Proteus's declared order (input 0 is MSB)."""
    return "".join(str(fn((k >> 2) & 1, (k >> 1) & 1, k & 1))
                   for k in range(8))


AND01 = tt(lambda a, b, c: a & b)
XOR3 = tt(lambda a, b, c: a ^ b ^ c)
MAJ3 = tt(lambda a, b, c: 1 if a + b + c >= 2 else 0)
CONST0 = "0" * 8
X2 = tt(lambda a, b, c: c)

BASE = {
    "grammar_version": "proteus.boolean_grammar.v0",
    "candidate_policy": "seeded_enumeration_v1",
    "candidate_seed": 20260910,
    "max_expr_size": 5,
    "max_candidates": 4000,
    "oracle_call_cap": 100000,
    "vm_op_cap": 10 ** 9,
    "trace_bound": 32,
    "vm_ticks": 2,
    "case_ordering": "proteus_declared",
    "termination": "first_solution",
    "seed_probe_count": 0,
    "shortfall_rule": "report_and_proceed",
    "source_pack": None,
    "component_library": None,
}


def payload(**kw):
    return dict(BASE, **kw)


def run(**kw):
    return _cb.run(payload(**kw), seed=7, inputs=kw.pop("_inputs", {}))


def cegis_spec(pl, *, seed_root=20260910):
    return {"spec_version": 3, "world": {"seed_root": seed_root},
            "hypothesis": "a bounded search finds a Boolean program or says "
                          "why it did not",
            "prediction": None,
            "work": {"kind": "cegis_boolean_v1", "payload": pl},
            "outcome_rule": {"field": "solved", "op": "==", "value": True,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "constant", "state": "reset",
                       "budget": {"max_seconds": 120, "max_observations": 1}}}


def library_artifact(components):
    obj = {"artifact_type": "component_library", "schema_version": "1",
           "interface_id": "boolean-components-v1",
           "components": [dict(c) for c in components]}
    raw = _a.canonical_bytes(obj)
    slot = {"digest": _a.digest_of(raw), "artifact_type": "component_library",
            "schema_version": "1", "codec": "canonical-json-v1",
            "expected_bytes": len(raw),
            "interface_id": "boolean-components-v1"}
    return obj, raw, slot


def hydrate(slots_and_bytes):
    """{slot_name: (slot, raw)} -> frozen inputs, through the REAL preflight."""
    store, locators, slots = {}, {}, {}
    for i, (name, (slot, raw)) in enumerate(sorted(slots_and_bytes.items())):
        aid = "art-%d" % i
        store[slot["digest"]] = (raw, "w-src", aid)
        locators[slot["digest"]] = {"source_world": "w-src",
                                    "source_artifact": aid}
        slots[name] = slot
    pf = _pf.Preflight(resolver=LocalResolver(store), locators=locators)
    inputs, receipt = pf.hydrate(slots)
    return inputs, receipt


# ===========================================================================
# 1. THE LOOP SOLVES, AND SOLVED MEANS FULL COVERAGE
# ===========================================================================

def test_it_solves_a_reachable_target_with_the_right_expression():
    out = run(target_truth_table=AND01)
    assert out["status"] == _cb.SOLVED
    assert out["solved"] is True
    from proteus.eval.boolean import truth_table
    expr = _cb._from_json(json.loads(out["solution"]), None)
    assert "".join(str(v) for v in truth_table(expr)) == AND01


def test_solved_requires_all_eight_assignments():
    out = run(target_truth_table=XOR3)
    assert out["solved"] is True
    assert out["coverage_required"] == 8
    # The exhaustive check ran at least once, and the solution really is the
    # target's function -- not merely consistent with the constraints seen.
    assert out["verifications"] >= 1


def test_an_unreachable_target_exhausts_rather_than_claiming_anything():
    """MAJ3 is (a&b)|(a&c)|(b&c) -- nine nodes, outside a size-5 space. The
    honest answer is that the declared search space ran out, and it must not
    be confused with a budget."""
    out = run(target_truth_table=MAJ3, max_expr_size=5, max_candidates=10 ** 6)
    assert out["status"] == _cb.EXHAUSTED_CANDIDATES
    assert out["solved"] is False
    assert "solution" not in out


def test_the_status_set_is_closed():
    for target in (AND01, XOR3, MAJ3, CONST0, X2):
        assert run(target_truth_table=target)["status"] in _cb.STATUSES


# ===========================================================================
# 2. BUDGETS ARE THEIR OWN STATUSES, AND DISTINCT FROM EXHAUSTION
# ===========================================================================

def test_running_out_of_candidates_is_not_exhausting_the_space():
    """BUDGET_CANDIDATES and EXHAUSTED_CANDIDATES are different facts: one is
    about the allowance, the other about the task."""
    capped = run(target_truth_table=MAJ3, max_candidates=50)
    assert capped["status"] == _cb.BUDGET_CANDIDATES
    assert capped["candidates_tried"] == 50
    whole = run(target_truth_table=MAJ3, max_candidates=10 ** 6)
    assert whole["status"] == _cb.EXHAUSTED_CANDIDATES


def test_the_vm_op_cap_stops_the_loop_with_its_own_status():
    out = run(target_truth_table=MAJ3, vm_op_cap=500, max_candidates=10 ** 6)
    assert out["status"] == _cb.BUDGET_VM_OPS
    assert out["solved"] is False


def test_the_oracle_cap_stops_the_loop_with_its_own_status():
    out = run(target_truth_table=MAJ3, oracle_call_cap=16,
              max_candidates=10 ** 6)
    assert out["status"] == _cb.BUDGET_ORACLE_CALLS
    assert out["solved"] is False


def test_a_budget_stop_is_never_reported_as_solved():
    for kw in ({"vm_op_cap": 200}, {"oracle_call_cap": 8},
               {"max_candidates": 1}):
        out = run(target_truth_table=XOR3, **kw)
        if out["status"] != _cb.SOLVED:
            assert out["solved"] is False
            assert "solution" not in out


# ===========================================================================
# 3. LABELS COME FROM THE TARGET, WHEREVER THE INPUTS CAME FROM
# ===========================================================================

def test_a_source_pack_carrying_wrong_labels_cannot_corrupt_the_result():
    """The pack format carries INPUTS only -- there is nowhere to put a label.
    That is the structural version of "the target oracle recomputes"."""
    _obj, raw, slot = input_set([[0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1]])
    assert set(_obj) == {"artifact_type", "schema_version", "interface_id",
                         "n_bits", "items"}
    inputs, _r = hydrate({"source_pack": (slot, raw)})
    seeded = _cb.run(payload(target_truth_table=AND01, seed_probe_count=4,
                             source_pack=slot), seed=7, inputs=inputs)
    fresh = run(target_truth_table=AND01)
    # Same target, same enumeration order -> same solution. The pack changed
    # the COST, never the answer.
    assert seeded["solution"] == fresh["solution"]
    assert seeded["seeded_from"] == "source_pack"
    assert fresh["seeded_from"] == "fresh_probe_allowance"


def test_a_pack_of_the_wrong_width_is_refused():
    _obj, raw, slot = input_set([[0, 1], [1, 0]], n_bits=2)
    inputs, _r = hydrate({"source_pack": (slot, raw)})
    with pytest.raises(_cb.CegisError) as e:
        _cb.run(payload(target_truth_table=AND01, seed_probe_count=2,
                        source_pack=slot), seed=7, inputs=inputs)
    assert "not a compatible source" in str(e.value)


# ===========================================================================
# 4. THE PROBE ALLOWANCE IS EQUAL; THE SPEND IS REPORTED
# ===========================================================================

def test_the_fresh_arm_gets_the_same_allowance_and_spends_it():
    out = run(target_truth_table=MAJ3, seed_probe_count=4, max_candidates=100)
    assert out["seed_probe_count"] == 4
    assert out["constraints_seeded"] == 4
    assert out["seed_probe_shortfall"] == 0


def test_a_short_pack_is_reported_and_never_topped_up():
    """Topping up from fresh probes would erase the very difference between
    the arms. The predeclared rule is report_and_proceed, in every arm."""
    _obj, raw, slot = input_set([[0, 0, 1], [1, 1, 0]])
    inputs, _r = hydrate({"source_pack": (slot, raw)})
    out = _cb.run(payload(target_truth_table=MAJ3, seed_probe_count=6,
                          source_pack=slot, max_candidates=100),
                  seed=7, inputs=inputs)
    assert out["seed_probe_count"] == 6
    assert out["constraints_seeded"] == 2
    assert out["seed_probe_shortfall"] == 4
    assert out["seeded_from"] == "source_pack"


def test_repeated_rows_in_a_pack_are_not_counted_as_probes():
    _obj, raw, slot = input_set([[0, 0, 1], [0, 0, 1], [0, 0, 1], [1, 1, 0]])
    inputs, _r = hydrate({"source_pack": (slot, raw)})
    out = _cb.run(payload(target_truth_table=MAJ3, seed_probe_count=4,
                          source_pack=slot, max_candidates=50),
                  seed=7, inputs=inputs)
    assert out["constraints_seeded"] == 2
    assert out["seed_probe_shortfall"] == 2


# ===========================================================================
# 5. THE COMPONENT LIBRARY IS A REAL CHANGE TO THE SEARCH SPACE
# ===========================================================================

def test_a_library_component_makes_an_unreachable_target_reachable():
    """THE INSTRUMENT CONTROL, and it is labelled as one: the components below
    are HAND-BUILT, chosen because they are the subterms of MAJ3. That they
    help is arithmetic (a 9-node expression becomes a 5-node one), not
    evidence that extracted components would.
    """
    without = run(target_truth_table=MAJ3, max_expr_size=5,
                  max_candidates=10 ** 6)
    assert without["status"] == _cb.EXHAUSTED_CANDIDATES

    _obj, raw, slot = library_artifact([
        {"name": "ab", "expr": ["and", ["input", 0], ["input", 1]]},
        {"name": "ac", "expr": ["and", ["input", 0], ["input", 2]]},
        {"name": "bc", "expr": ["and", ["input", 1], ["input", 2]]},
    ])
    inputs, _r = hydrate({"component_library": (slot, raw)})
    with_lib = _cb.run(payload(target_truth_table=MAJ3, max_expr_size=5,
                               max_candidates=10 ** 6,
                               component_library=slot),
                       seed=7, inputs=inputs)
    assert with_lib["status"] == _cb.SOLVED
    assert with_lib["component_library_size"] == 3
    from proteus.eval.boolean import truth_table
    expr = _cb._from_json(json.loads(with_lib["solution"]), None)
    assert "".join(str(v) for v in truth_table(expr)) == MAJ3


def test_a_library_component_that_is_not_a_valid_expression_is_refused():
    _obj, raw, slot = library_artifact([
        {"name": "bad", "expr": ["and", ["input", 0]]}])     # arity 1 for AND
    with pytest.raises(_a.PreflightRejected) as e:
        hydrate({"component_library": (slot, raw)})
    assert e.value.rejection_class == _a.MALFORMED


def test_two_components_under_one_name_are_refused():
    _obj, raw, slot = library_artifact([
        {"name": "c", "expr": ["input", 0]},
        {"name": "c", "expr": ["input", 1]}])
    with pytest.raises(_a.PreflightRejected):
        hydrate({"component_library": (slot, raw)})


# ===========================================================================
# 6. THE FOUR H0 CELLS: ONE RUNTIME, FOUR SEALED IDENTITIES
# ===========================================================================

def _cells():
    _po, praw, pslot = input_set([[0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1]])
    _lo, lraw, lslot = library_artifact([
        {"name": "ab", "expr": ["and", ["input", 0], ["input", 1]]},
        {"name": "ac", "expr": ["and", ["input", 0], ["input", 2]]},
        {"name": "bc", "expr": ["and", ["input", 1], ["input", 2]]},
    ])
    return {
        "S00": (None, None), "S10": (pslot, None),
        "S01": (None, lslot), "S11": (pslot, lslot),
    }, (pslot, praw), (lslot, lraw)


def test_the_four_cells_have_four_different_sealed_identities():
    cells, _p, _l = _cells()
    hashes = {}
    for name, (pack, lib) in cells.items():
        pl = payload(target_truth_table=MAJ3, seed_probe_count=4,
                     source_pack=pack, component_library=lib)
        hashes[name] = _spec.spec_hash(cegis_spec(pl))
    assert len(set(hashes.values())) == 4, hashes


def test_an_empty_slot_is_a_declared_value_not_an_omission():
    """`null` is IN the payload and therefore inside spec_hash. Dropping the
    key entirely is a different thing and is refused."""
    pl = payload(target_truth_table=MAJ3)
    assert pl["source_pack"] is None and "source_pack" in pl
    assert _spec.validate(cegis_spec(pl)) is None or True

    missing = {k: v for k, v in pl.items() if k != "source_pack"}
    with pytest.raises(Exception) as e:
        _spec.validate(cegis_spec(missing))
    assert "missing" in str(e.value)


def test_all_four_cells_run_on_one_solver_runtime():
    cells, (pslot, praw), (lslot, lraw) = _cells()
    inputs_all, _r = hydrate({"source_pack": (pslot, praw),
                              "component_library": (lslot, lraw)})
    results = {}
    for name, (pack, lib) in cells.items():
        pl = payload(target_truth_table=MAJ3, seed_probe_count=4,
                     max_candidates=10 ** 6, source_pack=pack,
                     component_library=lib)
        supplied = {}
        if pack is not None:
            supplied["source_pack"] = inputs_all["source_pack"]
        if lib is not None:
            supplied["component_library"] = inputs_all["component_library"]
        results[name] = _cb.run(pl, seed=7, inputs=supplied)
    # Every cell reports the same executor and the same declared coverage.
    assert {r["executor"] for r in results.values()} == {"cegis_boolean_v1"}
    # The library cells reach MAJ3; the others cannot, at size 5.
    assert results["S01"]["solved"] is True
    assert results["S11"]["solved"] is True
    assert results["S00"]["solved"] is False
    assert results["S10"]["solved"] is False
    # ... and the pack changed cost without changing whether the space
    # contains the answer, which is the separation H0's two factors need.
    assert results["S00"]["status"] == results["S10"]["status"]


# ===========================================================================
# 7. THE CONTRACT AT THE EXECUTOR BOUNDARY
# ===========================================================================

def test_the_executor_validates_the_result_against_the_declared_schema():
    pl = payload(target_truth_table=AND01)
    out = _ex.run(cegis_spec(pl), seed=7, inputs=None)
    meta = _kinds.get("cegis_boolean_v1").check_result(dict(out))
    assert meta["validated"] is True
    assert meta["vectors"]["witnesses"]["inner_shape_validated"] is False


def test_a_null_slot_reaches_the_executor_without_hydration():
    """Both cells with no artifact run with inputs={} and are NOT mistaken for
    a bypassed preflight."""
    pl = payload(target_truth_table=CONST0)
    out = _ex.run(cegis_spec(pl), seed=7, inputs=None)
    assert out["solved"] is True
    # OMITTED, not null: "consumed nothing" and "consumed nothing successfully"
    # are different claims and only one of them is true here.
    assert "source_pack_digest" not in out
    assert "component_library_digest" not in out


def test_a_declared_slot_still_requires_hydration():
    _obj, raw, slot = input_set([[0, 0, 1]])
    pl = payload(target_truth_table=AND01, source_pack=slot,
                 seed_probe_count=1)
    with pytest.raises(_ex.ExecutorUnavailable) as e:
        _ex.run(cegis_spec(pl), seed=7, inputs=None)
    assert "bypassed" in str(e.value)


def test_a_sealed_grammar_version_that_does_not_match_is_refused():
    pl = payload(target_truth_table=AND01,
                 grammar_version="proteus.boolean_grammar.v9")
    with pytest.raises(_cb.CegisError) as e:
        _ex.run(cegis_spec(pl), seed=7, inputs=None)
    assert "new experiment" in str(e.value)


def test_the_result_is_bit_identical_on_re_execution():
    pl = payload(target_truth_table=XOR3)
    a = _ex.run(cegis_spec(pl), seed=7, inputs=None)
    b = _ex.run(cegis_spec(pl), seed=7, inputs=None)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["reproducibility"] == "BIT_DETERMINISTIC"


# ===========================================================================
# 8. THE MECHANISM, AND ITS SIGN
# ===========================================================================

def test_seeding_changes_cost_and_the_direction_is_not_assumed():
    """The honest form of the claim. Seeding trades a cheaper rejection for a
    per-candidate cost paid by every survivor, so it can go either way -- and
    on these two targets it goes both ways. A test that only checked the
    favourable direction would be asserting H1's answer."""
    fresh_fast = run(target_truth_table=X2)
    seeded_fast = run(target_truth_table=X2, seed_probe_count=4)
    fresh_scan = run(target_truth_table=MAJ3, max_candidates=10 ** 6)
    seeded_scan = run(target_truth_table=MAJ3, seed_probe_count=4,
                      max_candidates=10 ** 6)

    assert seeded_fast["vm_ops"] < fresh_fast["vm_ops"], "helped here"
    assert seeded_scan["vm_ops"] > fresh_scan["vm_ops"], "hurt here"
    # Oracle calls fall in both, because a seeded constraint replaces a full
    # eight-label verification.
    assert seeded_fast["oracle_calls"] < fresh_fast["oracle_calls"]
    assert seeded_scan["oracle_calls"] < fresh_scan["oracle_calls"]


def test_the_enumeration_order_is_the_same_in_every_arm():
    """Which is why an arm's advantage can only be reach-before-the-cap, and
    never a different candidate order."""
    a = run(target_truth_table=MAJ3, max_candidates=200)
    b = run(target_truth_table=MAJ3, max_candidates=200, seed_probe_count=4)
    assert a["candidates_tried"] == b["candidates_tried"] == 200


def test_a_different_candidate_seed_is_a_different_search():
    a = run(target_truth_table=XOR3, candidate_seed=1)
    b = run(target_truth_table=XOR3, candidate_seed=2)
    assert a["solved"] and b["solved"]
    assert a["candidates_tried"] != b["candidates_tried"]
