"""The measurement result type — cycle 039. Making one recurring bug unrepresentable.

Seven instances across four modules, every one found by a different instrument and none by
reading the code. Detection works; prevention did not. This is the prevention attempt, and its
own limits are tested alongside it.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.measurement import (  # noqa: E402
    NO_SIGNAL, OUT_OF_DOMAIN, SIGNAL, Measurement, MeasurementError, measured,
    mistyped_domain_is_still_possible, no_signal, out_of_domain, signal,
)


# ---- the three guarantees, each traced to a past bug --------------------------------------------

def test_GUARANTEE_1_value_raises_on_out_of_domain():
    """You cannot get a number out without having handled the third case — so "there was nothing
    to look at" can never be arithmetic'd as though it were zero. (refinement_multiplicity 038,
    murphy skill 039.)"""
    m = out_of_domain("nothing to compare")
    with pytest.raises(MeasurementError) as exc:
        _ = m.value
    assert "not applicable" in str(exc.value)
    assert signal(7).value == 7 and no_signal(0).value == 0


def test_GUARANTEE_2_bool_raises_always():
    """`if result:` is the single most likely way to treat OUT_OF_DOMAIN as falsy — the shape of
    four of the seven past bugs. Every boolean route must refuse, not just `bool()`."""
    m = out_of_domain("empty fiber")
    for thunk in (lambda: bool(m), lambda: (1 if m else 2), lambda: (not m), lambda: (m and 1),
                  lambda: (m or 1)):
        with pytest.raises(MeasurementError):
            thunk()
    # and the same for the other two statuses: no status may be silently truthy
    for other in (signal(1), no_signal(0)):
        with pytest.raises(MeasurementError):
            bool(other)


def test_GUARANTEE_3_out_of_domain_requires_a_reason():
    """An unexplained refusal is only marginally better than a wrong answer."""
    with pytest.raises(MeasurementError):
        Measurement(OUT_OF_DOMAIN)
    with pytest.raises(MeasurementError):
        Measurement(OUT_OF_DOMAIN, None, "")
    assert out_of_domain("because").reason == "because"


def test_an_unknown_status_is_refused():
    with pytest.raises(MeasurementError):
        Measurement("MAYBE")


def test_explicit_opt_in_to_a_default_is_allowed():
    """Refusing is not the same as being unusable. A caller that has thought about it can say so
    in writing, and `value_or` is that signature."""
    assert out_of_domain("n/a").value_or(0) == 0
    assert signal(5).value_or(0) == 5
    assert out_of_domain("n/a").status is OUT_OF_DOMAIN
    assert not out_of_domain("n/a").is_applicable


# ---- the type's own anti-case ---------------------------------------------------------------------

def test_THE_TYPE_DOES_NOT_MAKE_MEASURES_CORRECT():
    """**HITL #129 applied to the type itself, and the honest limit.**

    A measure that decides wrongly whether its input is in-domain returns a perfectly well-formed
    SIGNAL where OUT_OF_DOMAIN was correct. The type enforces the SHAPE of the answer, not the
    judgement behind it.

    It converts a silent-by-default failure into one requiring an explicit wrong decision — a
    smaller target, not an empty one.
    """
    assert mistyped_domain_is_still_possible() is True


def test_the_adapter_turns_a_bare_measure_into_a_typed_one():
    """`measured` lets the already-repaired sites express their repair in the type without a
    breaking change to their callers."""
    typed = measured(lambda xs: len(xs),
                     applicable=lambda xs: None if xs else "empty input",
                     is_signal=lambda v: v > 0)
    assert typed([1, 2]).status is SIGNAL
    assert typed([]).status is OUT_OF_DOMAIN
    with pytest.raises(MeasurementError):
        _ = typed([]).value


def test_the_adapter_converts_a_raise_into_out_of_domain_not_a_verdict():
    typed = measured(lambda xs: 1 / len(xs),
                     applicable=lambda xs: None,
                     is_signal=lambda v: v > 0)
    r = typed([])
    assert r.status is OUT_OF_DOMAIN and "ZeroDivisionError" in r.reason


# ---- instances 5, 6, 7: found this cycle, before the type was built ---------------------------------

def test_INSTANCE_5_murphy_skill_was_undefined_and_returned_zero():
    """A degenerate battery (every outcome identical) makes the base-rate forecaster perfect, so
    there is nothing to be better than and skill has no value. It used to return 0.0, meaning
    "no skill" and "skill undefined" at once.

    **Its own test asserted `skill == 0.0`** — the bug encoded by the test defending it.
    """
    from prometheus_math.calibration import CalibrationError, murphy_decomposition

    degenerate = murphy_decomposition([0.2, 0.8], [1, 1])
    assert degenerate.uncertainty == 0.0
    with pytest.raises(CalibrationError):
        _ = degenerate.skill
    assert degenerate.skill_or(0.0) == 0.0                 # explicit opt-in still available
    ordinary = murphy_decomposition([1.0, 1.0, 0.0, 0.0], [1, 1, 0, 0])
    assert ordinary.skill == pytest.approx(1.0)            # the honest case is unobstructed


def test_INSTANCE_6_verify_factorization_returned_True_vacuously():
    from techne.ladder_circuits.aliasing import OutOfDomain, verify_factorization

    with pytest.raises(OutOfDomain):
        verify_factorization([], lambda x: x, lambda x: x)
    with pytest.raises(OutOfDomain):
        verify_factorization([1], lambda x: x, lambda x: x)
    assert verify_factorization([1, 2, 3], lambda i: i % 2, lambda i: i) is True


def test_INSTANCE_7_uniform_adversary_reported_a_schema_that_never_ran_as_SURVIVING():
    """The worst-placed of the seven: this module's own docstring warns against concluding
    sufficiency from a failure to enumerate, and its report property did exactly that."""
    from techne.ladder_circuits.aliasing import uniform_adversary

    r = uniform_adversary("empty", [], lambda p: (p, p), lambda p: (lambda v: 0), lambda v: v)
    assert r.n_parameters == 0
    with pytest.raises(ValueError) as exc:
        _ = r.schema_survived
    assert "never" in str(exc.value) or "neither survived nor failed" in str(exc.value)


def test_the_bug_class_now_stands_at_seven_and_all_seven_refuse():
    """The tally, executable. Four modules, seven sites, each found by a different instrument."""
    from prometheus_math.battery import INVALID_PROBE, structural_constancy
    from prometheus_math.calibration import CalibrationError, murphy_decomposition
    from prometheus_math.partition import PartitionError, refinement_multiplicity
    from techne.ladder_circuits.aliasing import (
        OutOfDomain, fiber_search, find_aliasing_witness, verify_factorization,
    )

    def raises(_n):
        raise ValueError("nope")

    assert structural_constancy("m", raises, [1, 2, 3]).status == INVALID_PROBE     # 1
    with pytest.raises(OutOfDomain):
        find_aliasing_witness([1], lambda n: n, lambda n: n)                        # 2
    with pytest.raises(OutOfDomain):
        fiber_search(1, lambda s: [], lambda n: n, lambda n: n)                     # 3
    # 4 — MIGRATED in cycle 041: this one now refuses by returning OUT_OF_DOMAIN rather than by
    # raising. It is the first site to actually use the type this module defines, picked because
    # its refusal fired 96 times from production callers in one suite run — more than the other
    # nine sites combined.
    assert refinement_multiplicity((frozenset([0, 1]),),
                                   (frozenset([0]), frozenset([1])), 2).status == OUT_OF_DOMAIN
    with pytest.raises(CalibrationError):
        _ = murphy_decomposition([0.2, 0.8], [1, 1]).skill                          # 5
    with pytest.raises(OutOfDomain):
        verify_factorization([1], lambda x: x, lambda x: x)                         # 6
    # 7 covered by the test above
