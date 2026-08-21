"""R0 straw-man acceptance suite. The unusual part: the KILL TEST is enforced as a test.

An R0 circuit that answers a renamed problem is mislabeled — so the suite asserts the
FAILURE (abstention on isomorphs), per the ladder's falsification-first doctrine. Traps from
the rung notes (§4) are encoded where cheap: hash-collision freeloading, order invariance.
"""
from __future__ import annotations

import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r0_pattern import (  # noqa: E402
    CanonicalizingCircuit,
    R0PatternCircuit,
    ast_key,
    canonical_key,
)

x, y, z = sp.symbols("x y z")


def trained() -> R0PatternCircuit:
    c = R0PatternCircuit()
    c.train(3 * x + 7, sp.Rational(-7, 3))
    c.train(x**2 - 4, [2, -2])
    return c


# ---- recall: the one thing R0 promises ----------------------------------------------------

def test_recalls_identical_problem():
    assert trained().answer(3 * x + 7) == sp.Rational(-7, 3)


def test_recall_is_deterministic():
    c = trained()
    assert c.answer(x**2 - 4) == c.answer(x**2 - 4) == [2, -2]


# ---- the kill test, enforced as a test ----------------------------------------------------

def test_KILL_abstains_on_renamed_isomorph():
    """3y + 7 is the alpha-renamed isomorph of a trained problem. A genuine R0 circuit MUST
    miss it — answering would mean the circuit holds R1-ish invariance and is mislabeled."""
    assert trained().answer(3 * y + 7) is None


def test_KILL_abstains_on_recoefficiented_transfer():
    assert trained().answer(5 * x + 7) is None


def test_abstains_on_never_seen_problem():
    assert trained().answer(sp.sin(x) - 1) is None


# ---- the R0/R1 boundary is the canonicalizer, tested not asserted -------------------------

def test_canonicalizing_circuit_answers_the_rename_and_is_therefore_not_r0():
    c = CanonicalizingCircuit()
    c.train(3 * x + 7, "root=-7/3")
    assert c.answer(3 * y + 7) == "root=-7/3"      # survives the R0 kill test...
    assert c.answer(5 * x + 7) is None             # ...but not the R1 transfer probe


def test_canonical_key_is_alpha_invariant_and_structure_sensitive():
    assert canonical_key(3 * x + 7) == canonical_key(3 * z + 7)
    assert canonical_key(3 * x + 7) != canonical_key(3 * x - 7)


# ---- traps (rung notes §4) ----------------------------------------------------------------

def test_trap_token_multiset_collision_does_not_freeload():
    """(x+2)*3 and x + 2*3 share a token multiset {x,2,3,+,*}; a weak hash could collide.
    Structurally different problems must never share an answer."""
    c = R0PatternCircuit()
    c.train((x + 2) * 3, "A")
    assert c.answer(x + 2 * 3) is None
    assert ast_key((x + 2) * 3) != ast_key(x + 2 * 3)


def test_trap_training_order_is_irrelevant():
    a = R0PatternCircuit()
    a.train(3 * x + 7, "p")
    a.train(x**2 - 4, "q")
    b = R0PatternCircuit()
    b.train(x**2 - 4, "q")
    b.train(3 * x + 7, "p")
    for probe in (3 * x + 7, x**2 - 4, 3 * y + 7):
        assert a.answer(probe) == b.answer(probe)


def test_trap_no_answer_distribution_prior():
    """An untrained circuit answers NOTHING — 0% hit rate, not label-prior hit rate. The
    greedy-LoRA lesson: lift must come from the pattern store, never from a guess policy."""
    c = R0PatternCircuit()
    for probe in (3 * x + 7, x - 1, sp.cos(y), z**3 + z, sp.sqrt(x + 4)):
        assert c.answer(probe) is None


# ---- integration with the real probe generator --------------------------------------------

def test_against_reasoning_phase0_r0_probes_clean_hits_iso_misses():
    """Train on gen_R0 CLEAN probes; the circuit must answer those and abstain on the ISO
    versions of the same battery — reproducing the rung's failure signature on the real
    instrument, not just on hand examples."""
    import random

    from harmonia.experiments.reasoning_phase0 import gen_R0

    probes = gen_R0(random.Random(20260821))
    clean = [p for p in probes if p.version == "clean"]
    iso = [p for p in probes if p.version == "iso"]
    c = R0PatternCircuit()
    for p in clean:
        c.train(p.data["expr"], p.ground_truth)
    clean_hits = sum(c.answer(p.data["expr"]) is not None for p in clean)
    iso_hits = sum(c.answer(p.data["expr"]) is not None for p in iso)
    assert clean_hits == len(clean)
    assert iso_hits <= len(iso) * 0.05  # collapse under isomorphism = the R0 signature
