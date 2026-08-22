"""Contract retrofit across the whole arsenal — cycle 037.

Twelve instruments, certified with generative fixtures and `draws > 1`. Three were REFUSED on
the first pass, and two of those refusals were real defects in modules I had shipped and trusted
for ten cycles.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.contract_registry import build_registry, certify_all  # noqa: E402


# ---- the retrofit ---------------------------------------------------------------------------

def test_every_instrument_in_the_arsenal_is_certified():
    """Twelve instruments across five modules, after the two defects the first pass exposed."""
    rows = certify_all(draws=4)
    assert len(rows) == 12
    refused = [(n, r.failures) for n, r in rows if not r.admissible]
    assert refused == [], refused


def test_the_registry_uses_factories_not_frozen_values():
    """Cycle 036 showed a memoriser passes on frozen fixtures. Every fixture here is a callable,
    and the certification redraws."""
    for _name, _fn, contract in build_registry():
        for slot in (contract.positive, contract.negative, contract.invalid,
                     contract.sensitivity):
            assert callable(slot)


# ---- defect 1 and 2: no-signal conflated with out-of-domain --------------------------------------

def test_DEFECT_find_aliasing_witness_conflated_no_signal_with_out_of_domain():
    """**The contract's first real catch, on a module I had used for ten cycles.**

    `find_aliasing_witness` returned `None` for "searched every pair and found nothing" AND for
    "there were not two instances to compare". Those are different statements: the first is about
    the projection, the second about the input.

    This is exactly the defect cycle 029 fixed in `structural_constancy` (an all-raising probe
    space reading as constancy). I fixed it there and never propagated the lesson — which is what
    a contract is for.
    """
    from techne.ladder_circuits.aliasing import OutOfDomain, find_aliasing_witness

    assert find_aliasing_witness([1, 2, 3], lambda n: n, lambda n: n > 2) is None   # no signal
    with pytest.raises(OutOfDomain):
        find_aliasing_witness([1], lambda n: n % 2, lambda n: n > 2)
    with pytest.raises(OutOfDomain):
        find_aliasing_witness([], lambda n: n % 2, lambda n: n > 2)


def test_DEFECT_fiber_search_had_the_same_conflation():
    """Same shape, same module: `None` for "no flip in the fiber" and for "nothing ever entered
    the fiber". The second is not a statement about the truth function at all."""
    from techne.ladder_circuits.aliasing import OutOfDomain, fiber_search

    assert fiber_search(1, lambda s: [3, 5], lambda n: n % 2, lambda n: True) is None
    with pytest.raises(OutOfDomain):
        fiber_search(1, lambda s: [], lambda n: n % 2, lambda n: n > 4)
    with pytest.raises(OutOfDomain):        # every candidate leaves the fiber
        fiber_search(1, lambda s: [2, 4, 6], lambda n: n % 2, lambda n: n > 4)


def test_the_genuine_no_signal_answer_still_works_after_the_fix():
    """A defect fix that broke the honest case would be worse than the defect."""
    from techne.ladder_circuits.aliasing import find_aliasing_witness, fiber_search

    w = find_aliasing_witness([1, 3], lambda n: n % 2, lambda n: n > 2)
    assert w is not None and w.projection_value == 1
    s = fiber_search(1, lambda seed: [3, 5, 7], lambda n: n % 2, lambda n: n > 4)
    assert s is not None


# ---- refusal 3: a reach limit rather than a defect -----------------------------------------------

def test_structural_constancy_REACH_LIMIT_source_must_be_available():
    """The third refusal was not a defect. `structural_constancy`'s static tier reads its
    target's SOURCE, and its conservative path reports "reads its parameters" whenever source is
    unavailable — a lambda inside an expression, an exec'd string, a REPL definition.

    That is honest (it never CLAIMS parameter-independence it cannot verify) and it is a real
    limit: the instrument is unusable wherever source cannot be retrieved. The fixtures are now
    module-level functions, which is presenting in-domain input rather than weakening anything.
    """
    from prometheus_math.battery import PARAMETER_INDEPENDENT, reads_its_parameters
    from techne.ladder_circuits.contract_registry import (
        _ignores_its_argument, _reads_its_argument,
    )
    from prometheus_math.battery import structural_constancy

    assert reads_its_parameters(_ignores_its_argument) is False
    assert structural_constancy("m", _ignores_its_argument,
                                [1, 2, 3]).status == PARAMETER_INDEPENDENT
    assert reads_its_parameters(eval("lambda n: True")) is True      # source unavailable
    assert reads_its_parameters(len) is True                          # builtin


# ---- the diffuse-target finding ---------------------------------------------------------------------

def test_SENSITIVITY_IS_NOT_CONSTRUCTIBLE_FOR_A_DIFFUSE_TARGET():
    """**The answer to round 10's open question, and the contract cannot police it.**

    `brier_score` certified SENSITIVITY — but on a pair that does not isolate calibration.
    Decomposed, the two halves differ in reliability (0.0000 vs 0.0100) AND resolution (0.0000 vs
    0.2500). Changing calibration while holding everything else fixed is not possible for an
    aggregate score, so the pair changes two things and the contract accepts it.

    A SENSITIVITY pass on a diffuse target therefore means only "these inputs differ somehow",
    not "this instrument responds to its advertised target".
    """
    from prometheus_math.calibration import murphy_decomposition

    a = murphy_decomposition([0.5, 0.5, 0.5, 0.5], [1, 1, 0, 0])
    b = murphy_decomposition([0.9, 0.9, 0.1, 0.1], [1, 1, 0, 0])
    assert a.reliability != b.reliability
    assert a.resolution != b.resolution           # the pair moved BOTH — no isolation
    assert a.brier != b.brier                     # ...and brier responds, so it "passes"


def test_A_SHARP_COMPONENT_DOES_ADMIT_AN_ISOLATING_PAIR():
    """And the repair is one the literature already made: decompose the diffuse target into
    components each of which admits an isolating pair, then certify the components.

    `murphy_reliability`'s witness holds resolution fixed at 0.0000 and moves reliability from
    0.4225 to 0.0000. Genuine isolation — which is what Murphy's 1973 partition is FOR.
    """
    from prometheus_math.calibration import murphy_decomposition

    c = murphy_decomposition([0.9, 0.9, 0.9, 0.9], [1, 0, 0, 0])
    d = murphy_decomposition([0.25, 0.25, 0.25, 0.25], [1, 0, 0, 0])
    assert c.resolution == pytest.approx(d.resolution) == pytest.approx(0.0)   # held fixed
    assert c.reliability == pytest.approx(0.4225, abs=1e-4)
    assert d.reliability == pytest.approx(0.0, abs=1e-9)                        # varied alone
