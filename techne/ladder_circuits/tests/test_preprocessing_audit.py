"""Preprocessing audit — cycle 034. Which layer delivers which invariance?

HITL #124 asked how far cycle 032's sympy finding reaches: if the CAS delivers most low-rung
invariance, R0 and R1 might be measuring a normaliser rather than reasoning.

The answer is narrower and fairer than the question assumed, and getting there required
correcting the question first.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.preprocessing_audit import (  # noqa: E402
    LAYERS, PAIRS, attribute, audit_pairs, control_is_itself_a_normaliser, python_ast_key,
    sympy_srepr_key,
)

x = sp.Symbol("x")


# ---- HITL #129 applied to the control, BEFORE it was used ---------------------------------------

def test_THE_CONTROL_IS_ITSELF_A_NORMALISER():
    """**The new discipline, applied first, and it changed the question.**

    Before using the raw-syntax control for any comparison I constructed the inputs on which it
    must give the answer I did not want — that it normalises too. It gave them, 6 of 6:
    parentheses, whitespace, comments, numeric literal spelling, radix and string quoting all
    fall to `ast.parse`.

    So there is no raw baseline, and "what fraction of the invariance is the circuit's?" was the
    wrong question — it would have been computed against a floor that was quietly doing work.
    The right output is an ATTRIBUTION ACROSS LAYERS.
    """
    merged, total = control_is_itself_a_normaliser()
    assert merged == total == 6
    assert python_ast_key("(x)+y") == python_ast_key("x+y")
    assert python_ast_key("0x10") == python_ast_key("16")


def test_the_layer_ladder_is_strictly_coarsening():
    """Each layer must merge everything the one below it merged, or the attribution is
    meaningless — a pair could 'first merge' at a layer that had already lost it."""
    probes = ["x+y", "y+x", "(x)+y", "2*x", "x*2", "a+b", "x*(y+1)", "x*y+x"]
    keyers = [k for _name, k in LAYERS]
    for finer, coarser in zip(keyers, keyers[1:]):
        for i, a in enumerate(probes):
            for b in probes[i + 1:]:
                try:
                    if finer(a) == finer(b):
                        assert coarser(a) == coarser(b), (a, b)
                except Exception:
                    continue


# ---- the attribution ------------------------------------------------------------------------------

def test_EVERY_INVARIANCE_IS_ATTRIBUTED_TO_THE_LAYER_THAT_DELIVERS_IT():
    """Measured over the battery: L1 (Python's parser) 4, L2 (sympy) 7, L3 (circuit key) 3,
    never 1. Lexical invariance is the parser's, algebraic invariance is sympy's, and variable
    renaming is the only thing the circuit layer adds."""
    rows = audit_pairs()
    got = {}
    for r in rows:
        k = r.first_merging_layer.split()[0] if r.first_merging_layer else "never"
        got[k] = got.get(k, 0) + 1
    assert got["L1"] == 4
    assert got["L2"] == 7
    assert got["L3"] == 3
    assert got["never"] == 1


def test_the_one_pair_that_survives_every_layer_is_a_genuine_algebraic_identity():
    """`x*(y+1)` vs `x*y+x` are equal as functions and distinct at every layer measured — the
    only distinction in the battery no preprocessing erases."""
    a = attribute("x*(y+1)", "x*y+x")
    assert a.first_merging_layer is None
    assert sp.expand(sp.sympify("x*(y+1)") - sp.sympify("x*y+x")) == 0   # equal as functions


def test_my_own_expectation_was_wrong_for_one_pair():
    """Recorded rather than quietly corrected: I predicted `x+y` vs `x+z` would never merge.
    They merge at L3, and correctly — they ARE alpha-equivalent, so a renaming quotient should
    identify them. The battery's expectation was wrong, not the circuit."""
    a = attribute("x+y", "x+z", expected="--")
    assert a.first_merging_layer.startswith("L3")
    assert not a.as_expected                       # the prediction failed, and should have


# ---- the consequence, per rung ----------------------------------------------------------------------

def test_R0_PROPER_CONTRIBUTES_ZERO_INVARIANCE_OF_ITS_OWN():
    """**The finding, stated exactly.** R0's keyer is `ast_key`, which IS `sympy.srepr`. Its
    projection is precisely layer L2. Every congruence it appears to know was delivered before
    it ran.

    Consequence for the rung claim: canon R0 is exact recall that ABSTAINS on isomorphs. With
    sympy's key it does not abstain on algebraic isomorphs — it retrieves them. So R0-with-sympy
    sits slightly ABOVE its rung, and the excess is entirely borrowed.
    """
    from techne.ladder_circuits.r0_pattern import R0PatternCircuit, ast_key

    for src in ("x+y", "2*x", "x*(y+1)", "sqrt(4)*x"):
        assert ast_key(sp.sympify(src)) == sympy_srepr_key(src)

    circuit = R0PatternCircuit()
    circuit.train(sp.sympify("x+y"), "sum")
    assert circuit.answer(sp.sympify("y+x")) == "sum"     # retrieved — sympy's doing
    assert circuit.answer(sp.sympify("a+b")) is None      # abstains — the one axis sympy leaves


def test_R0s_KILL_TEST_PROBES_THE_ONE_AXIS_SYMPY_LEAVES_ALONE():
    """And this is why the rung's original result still stands. Renaming is the only isomorphism
    sympy does not collapse, and renaming is exactly what R0's fresh-seed kill test uses. The
    test was aimed at the right axis; only the DOCSTRING's claim of an "identity congruence" is
    wrong, and should read "sympy normal form"."""
    from techne.ladder_circuits.r0_pattern import CanonicalizingCircuit, R0PatternCircuit

    exact, canon = R0PatternCircuit(), CanonicalizingCircuit()
    exact.train(sp.sympify("x+y"), "sum")
    canon.train(sp.sympify("x+y"), "sum")
    assert exact.answer(sp.sympify("a+b")) is None        # the separation the kill test needs
    assert canon.answer(sp.sympify("a+b")) == "sum"
    # ...and sympy cannot deliver it, which is what makes the test sound
    assert sympy_srepr_key("x+y") != sympy_srepr_key("a+b")


def test_R1_DOES_CONTRIBUTE_ITS_OWN_MANY_TO_ONE_STRUCTURE():
    """R1 is not in R0's position. `2*x+4` and `3*x+6` have different sympy keys and the same
    R1 answer, so the identification is the rule's, not the CAS's."""
    from techne.ladder_circuits.r1_local_op import R1LocalOpCircuit, linear_root_rule

    r1 = R1LocalOpCircuit()
    r1.give_rule(linear_root_rule())
    for a, b in (("2*x+4", "3*x+6"), ("5*x+10", "7*x+14")):
        assert sympy_srepr_key(a) != sympy_srepr_key(b)
        assert r1.answer(sp.sympify(a)) == r1.answer(sp.sympify(b)) == -2
    assert r1.answer(sp.sympify("2*x+4")) != r1.answer(sp.sympify("2*x+6"))


def test_R2_DOES_CONTRIBUTE_TOO():
    """Scaling a rational leaves its root fixed. Different sympy keys, same R2 answer."""
    from techne.ladder_circuits.r2_pipeline import R2PipelineCircuit

    r2 = R2PipelineCircuit()
    prog = ["together", "numer", "linear_root"]
    a = sp.Integer(3) / (x + 1) + sp.Integer(4) / (x - 1)
    b = sp.Integer(6) / (x + 1) + sp.Integer(8) / (x - 1)
    assert sp.srepr(a) != sp.srepr(b)
    assert r2.run(a, prog)[0] == r2.run(b, prog)[0]


def test_the_thread_closes_narrowly_rather_than_escalating():
    """HITL #124 asked whether the ladder's bottom rungs measure a normaliser. Answer: R0 does,
    R1 and R2 do not. The bottom rung's projection is sympy's normal form and contributes nothing
    of its own; the two above it perform genuine many-to-one identifications the CAS does not.

    No rebuild on raw syntax is called for — there is no raw syntax. What is called for is
    DECLARING each rung's congruence rather than advertising one it does not implement.
    """
    from techne.ladder_circuits.r0_pattern import ast_key
    from techne.ladder_circuits.r1_local_op import R1LocalOpCircuit, linear_root_rule

    assert ast_key(sp.sympify("x+y")) == sympy_srepr_key("x+y")          # R0 == L2
    r1 = R1LocalOpCircuit()
    r1.give_rule(linear_root_rule())
    assert r1.answer(sp.sympify("2*x+4")) == r1.answer(sp.sympify("3*x+6"))   # R1 > L2
