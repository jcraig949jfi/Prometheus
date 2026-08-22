"""Domain-sourced anti-cases — cycle 038. Were my hand-written fixtures too easy?

Cycle 037 certified twelve instruments; nine passed first time, and I had written both the
instruments and their anti-cases. This cycle sources anti-cases from stated INVARIANTS over the
input domain instead, so the input comes from the domain rather than from my intuition about
which cases are hard.

**Answer: yes, at least one was too easy** — and the failure is the fourth instance of a single
bug class.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from prometheus_math.adversarial_fixtures import InvariantSpec, search_for_violation  # noqa: E402
from prometheus_math.partition import PartitionError, refinement_multiplicity, refines  # noqa: E402
from prometheus_math.measurement import (  # noqa: E402
    MeasurementError, OUT_OF_DOMAIN,
)
from techne.ladder_circuits.adversarial_registry import build_invariants, hunt_all  # noqa: E402


def _blocks(labels):
    out: dict = {}
    for i, lab in enumerate(labels):
        out.setdefault(lab, []).append(i)
    return tuple(frozenset(v) for v in out.values())


# ---- the finding ------------------------------------------------------------------------------

def test_THE_HAND_WRITTEN_FIXTURE_WAS_TOO_EASY_FOR_refinement_multiplicity():
    """**The measure this cycle was after.**

    `refinement_multiplicity` passed its hand-written anti-case in cycle 037 and fails a
    domain-sourced one. The counterexample the search found: projection `({0,1},)` against truth
    `({0}, {1})` — a projection COARSER than the truth. No projection cell fits inside any truth
    cell, so the old code returned **0**, outside its own advertised range of >= 1, and reading as
    "perfectly efficient" when the projection was in fact losing information.

    My fixture never caught it because I only ever fed the instrument REFINING projections. That
    is precisely the "my anti-cases were too easy" reading, and it is now measured rather than
    worried about.
    """
    proj = (frozenset([0, 1]),)
    truth = (frozenset([0]), frozenset([1]))
    assert not refines(proj, truth, 2)
    # Cycle 041 migrated this measure to the Measurement form: the refusal is now RETURNED, not
    # raised. Same refusal, same reason, different carrier — asserted both ways so the migration
    # cannot silently drop it.
    m = refinement_multiplicity(proj, truth, 2)
    assert m.status == OUT_OF_DOMAIN
    assert "presupposes" in m.reason
    with pytest.raises(MeasurementError):
        _ = m.value                       # and the value is still unreachable


def test_it_is_the_FOURTH_instance_of_one_bug_class():
    """A measure answering on input outside its own domain instead of saying so:

        029  structural_constancy      all-raising probe space read as constancy
        037  find_aliasing_witness     None for "nothing to compare" and for "found nothing"
        037  fiber_search              None for "empty fiber" and for "no flip"
        038  refinement_multiplicity   0 for "does not refine" and for "no fragmentation"

    Four instances across three modules, each found by a different instrument, none found by
    reading the code. That is the argument for a bug-class registry (HITL #151).
    """
    from techne.ladder_circuits.aliasing import OutOfDomain, find_aliasing_witness, fiber_search
    from prometheus_math.battery import INVALID_PROBE, structural_constancy

    def always_raises(_n):
        raise ValueError("out of domain")

    assert structural_constancy("m", always_raises, [1, 2, 3]).status == INVALID_PROBE
    with pytest.raises(OutOfDomain):
        find_aliasing_witness([1], lambda n: n, lambda n: n)
    with pytest.raises(OutOfDomain):
        fiber_search(1, lambda s: [], lambda n: n, lambda n: n)
    assert refinement_multiplicity((frozenset([0, 1]),),
                                   (frozenset([0]), frozenset([1])), 2).status == OUT_OF_DOMAIN


def test_the_repaired_measure_still_works_on_its_honest_case():
    """A fix that broke the honest case would be worse than the defect."""
    shattered = tuple(frozenset([i]) for i in range(4))
    whole = (frozenset(range(4)),)
    assert refinement_multiplicity(shattered, whole, 4).value == 4
    assert refinement_multiplicity(whole, whole, 4).value == 1


# ---- the generator ------------------------------------------------------------------------------

def test_the_hunt_is_clean_after_the_repair():
    """Ten invariants, domain-sourced search. Nine survived on the first pass and the tenth is
    now repaired — so the remaining nine are evidence (not proof) that the arsenal was sound."""
    rows = hunt_all(max_examples=120)
    violations = [(n, v) for n, v in rows if v is not None]
    assert violations == [], violations
    assert len(rows) == 10


def test_the_generator_finds_a_planted_violation():
    """The generator's own POSITIVE control: point it at an instrument that is genuinely wrong
    and it must find the counterexample. Without this the clean sweep above proves nothing about
    the generator."""
    from hypothesis import strategies as st

    def broken_abs(n):
        return n if n >= 0 else n          # forgets to negate: wrong for every negative

    spec = InvariantSpec(
        "planted.broken_abs", "abs(n) >= 0",
        lambda n: broken_abs(n) >= 0,
        lambda d: d.draw(st.integers(min_value=-50, max_value=50)))
    v = search_for_violation(spec, max_examples=200)
    assert v is not None
    assert v.counterexample < 0


def test_the_generator_reports_a_raise_as_a_violation_not_a_pass():
    """An invariant check that raises must be recorded, never swallowed — otherwise a crashing
    instrument reads as a clean one."""
    from hypothesis import strategies as st

    spec = InvariantSpec(
        "planted.raiser", "never raises",
        lambda n: (_ for _ in ()).throw(RuntimeError("boom")),
        lambda d: d.draw(st.integers(0, 5)))
    v = search_for_violation(spec, max_examples=20)
    assert v is not None and "RuntimeError" in v.detail


def test_the_remaining_hole_is_stated_not_hidden():
    """I still write the invariants. An instrument whose advertised semantics I have mis-stated
    is tested against the wrong property and passes.

    That is strictly smaller than hand-picked inputs — an invariant is a universal claim over the
    domain, a fixture is one point — but it is not zero, and closing it needs a second author
    rather than a cleverer generator."""
    specs = build_invariants()
    assert len(specs) == 10
    assert all(s.invariant and s.instrument for s in specs)
