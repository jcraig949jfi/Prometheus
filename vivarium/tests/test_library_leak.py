"""Does a component library already contain its own answers?

Techne shipped a library on 2026-09-11 whose three abstractions were each a
complete held-out solution; handed to a search those targets are size-1 leaves,
and the run would have measured the leak and reported it as the library effect.
My own hand-built demo library had the same defect and a label that hid it.

The tests below are in two halves, and the second is the one that matters: a
checker that only ever says CONTAMINATED has not been shown to detect anything.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
REPO = VIVARIUM.parent
for p in (str(VIVARIUM), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

pytest.importorskip("proteus.eval.boolean")

from viv import library_leak as _ll                          # noqa: E402


def tt(fn):
    return "".join(str(fn((k >> 2) & 1, (k >> 1) & 1, k & 1)) for k in range(8))


AND01 = tt(lambda a, b, c: a & b)
XOR3 = tt(lambda a, b, c: a ^ b ^ c)
MAJ3 = tt(lambda a, b, c: 1 if a + b + c >= 2 else 0)
X0NX2 = tt(lambda a, b, c: a & (1 - c))

AB = {"name": "ab", "expr": ["and", ["input", 0], ["input", 1]]}
AC = {"name": "ac", "expr": ["and", ["input", 0], ["input", 2]]}
BC = {"name": "bc", "expr": ["and", ["input", 1], ["input", 2]]}
NAND01 = {"name": "nand01",
          "expr": ["not", ["and", ["input", 0], ["input", 1]]]}


# ===========================================================================
# It fires
# ===========================================================================

def test_a_component_that_IS_a_task_is_caught():
    r = _ll.check([AB], {"and01": AND01})
    assert r["verdict"] == _ll.SOLVES_A_TASK
    assert r["usable_as_a_library_effect"] is False
    assert r["findings"][0]["tasks"] == ["and01"]


def test_it_catches_the_same_function_spelled_differently():
    """The blindness in a string-equality test. `and x1 x0` is `and x0 x1`."""
    flipped = {"name": "ba", "expr": ["and", ["input", 1], ["input", 0]]}
    r = _ll.check([flipped], {"and01": AND01})
    assert r["verdict"] == _ll.SOLVES_A_TASK


def test_it_sees_a_target_that_was_never_solved():
    """The other blindness: a test comparing against SOLVED programs cannot
    see an unsolved held-out target at all. This takes the task truth tables,
    so solved and unsolved are the same to it."""
    r = _ll.check([AB], {"never_solved": AND01})
    assert r["verdict"] == _ll.SOLVES_A_TASK


def test_one_operator_over_the_library_is_caught():
    """`xor(ac, x0)` is `x0 & ~x2`. No single component computes it, so
    SOLVES_A_TASK cannot see it -- and it is the answer in two pieces."""
    r = _ll.check([AC], {"x0nx2": X0NX2})
    assert r["verdict"] == _ll.COMPOSES_TO_A_TASK
    assert r["usable_as_a_library_effect"] is False
    assert any(f["class"] == _ll.COMPOSES_TO_A_TASK for f in r["findings"])


def test_the_demo_library_is_contaminated_and_the_report_is_legible():
    """The real case. Two findings, not nine: tasks already reported as solved
    outright are not restated as compositions."""
    r = _ll.check([AB, AC, BC],
                  {"and01": AND01, "x0nx2": X0NX2, "maj3": MAJ3, "xor3": XOR3})
    assert r["verdict"] == _ll.SOLVES_A_TASK
    classes = sorted(f["class"] for f in r["findings"])
    assert classes == [_ll.COMPOSES_TO_A_TASK, _ll.SOLVES_A_TASK]


# ===========================================================================
# It does NOT fire -- the half that makes the half above mean something
# ===========================================================================

def test_a_clean_library_passes():
    r = _ll.check([NAND01], {"xor3": XOR3, "maj3": MAJ3})
    assert r["verdict"] == _ll.CLEAN
    assert r["usable_as_a_library_effect"] is True
    assert r["findings"] == []


XOR12 = {"name": "xor12", "expr": ["xor", ["input", 1], ["input", 2]]}


def test_a_task_solvable_from_RAW_INPUTS_is_not_blamed_on_the_library():
    """`and01` is `and(x0, x1)` whatever library is present. Requiring a
    library component in the composition is what keeps this a statement about
    the LIBRARY rather than about how easy the task set is.

    The component has to be genuinely unrelated for this to test what it says.
    My first version used NAND01 against `and01` and the checker flagged it --
    correctly, see the test below. That was a bad control, not a false
    positive."""
    r = _ll.check([XOR12], {"and01": AND01})
    assert r["verdict"] == _ll.CLEAN, r["findings"]


def test_the_NEGATION_of_a_target_is_one_step_from_it_and_is_caught():
    """A library holding NOT(target) is one operator from the target, and a
    checker looking only for the target's own truth table sees nothing. Found
    by writing a negative control badly and reading what fired."""
    r = _ll.check([NAND01], {"and01": AND01})
    assert r["verdict"] == _ll.COMPOSES_TO_A_TASK
    assert any(f["component"].startswith("not(") for f in r["findings"])


def test_an_empty_library_is_CLEAN_and_that_is_a_measurement():
    """Techne's point. A null leak field reads as either 'not checked' or
    'nothing to check' and a reader cannot tell which."""
    r = _ll.check([], {"maj3": MAJ3})
    assert r["verdict"] == _ll.CLEAN
    assert r["n_components"] == 0
    assert r["usable_as_a_library_effect"] is True


def test_maj3_subterms_do_not_reach_maj3_in_ONE_step():
    """The cutoff is real and not a rubber stamp. maj3 is
    or(ab, or(ac, bc)) -- depth 2 -- so the depth-1 check does NOT flag it,
    even though the library is literally its three subterms. Whether that
    library makes maj3 easier is the effect under test, and this checker
    declines to rule on it."""
    r = _ll.check([AB, AC, BC], {"maj3": MAJ3})
    assert not any("maj3" in f["tasks"] for f in r["findings"]
                   if f["class"] == _ll.COMPOSES_TO_A_TASK)


def test_the_subterm_warning_is_not_a_verdict():
    """It is reported, and it does not disqualify: making a target easier is
    the effect being measured."""
    r = _ll.check([AC], {"maj3": MAJ3},
                  known_solutions={"maj3": ["or", AB["expr"],
                                            ["or", AC["expr"], BC["expr"]]]})
    assert r["verdict"] == _ll.SUBTERM_OF_SOLUTION
    assert r["usable_as_a_library_effect"] is True
    assert _ll.SUBTERM_OF_SOLUTION not in _ll.DISQUALIFYING
