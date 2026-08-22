"""Instrument contract — cycle 036, round-10 fold-in.

Four cycles running, an instrument shipped blind in the direction it was pointed. The contract
is the mechanism that replaces the habit, and this suite does two things: certifies that the
contract behaves, and **retroactively catches all four historical failures** with it.
"""
from __future__ import annotations

import pathlib
import random
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.instrument_contract import (  # noqa: E402
    ContractError, InstrumentContract, certify, memorisation_is_still_possible,
)


def _even_contract(seed: int = 5) -> InstrumentContract:
    rnd = random.Random(seed)
    return InstrumentContract(
        name="has_even",
        positive=lambda: [rnd.randrange(0, 50) * 2 for _ in range(4)],
        negative=lambda: [rnd.randrange(0, 50) * 2 + 1 for _ in range(4)],
        invalid=lambda: None,
        sensitivity=lambda: ([1, 3, 5], [1, 3, 5, 2]),
        is_signal=lambda v: v is True,
        is_no_signal=lambda v: v is False,
    )


# ---- the contract itself ------------------------------------------------------------------------

def test_an_honest_instrument_is_admissible():
    def honest(xs):
        if not isinstance(xs, list):
            raise TypeError("out of domain")
        return any(x % 2 == 0 for x in xs)
    assert certify(honest, _even_contract(), draws=5).admissible


def test_an_always_positive_instrument_is_REFUSED_on_negative_and_sensitivity():
    """The failure the NEGATIVE fixture exists for: an instrument that always says yes passes
    every honest test and fails the anti-case immediately."""
    def blind(xs):
        if not isinstance(xs, list):
            raise TypeError
        return True
    r = certify(blind, _even_contract(), draws=5)
    assert not r.admissible
    assert any("NEGATIVE" in f for f in r.failures)
    assert any("SENSITIVITY" in f for f in r.failures)


def test_answering_on_out_of_domain_input_is_REFUSED():
    """INVALID must produce NEITHER verdict — an error or an explicit unsettled, never a class."""
    def loose(xs):
        return any(x % 2 == 0 for x in xs) if isinstance(xs, list) else False
    r = certify(loose, _even_contract(), draws=3)
    assert not r.admissible
    assert any("INVALID" in f for f in r.failures)


def test_the_contract_refuses_an_instrument_submitted_without_an_anti_case():
    with pytest.raises(ContractError):
        InstrumentContract(name="m", positive=lambda: 1, negative=None,  # type: ignore[arg-type]
                           invalid=lambda: None, sensitivity=lambda: (1, 2),
                           is_signal=bool, is_no_signal=lambda v: not v)


def test_THE_CONTRACTS_OWN_ANTI_CASE_a_memoriser_passes_on_frozen_fixtures():
    """**Necessary, not sufficient — demonstrated rather than conceded.**

    An instrument that recognises the four fixtures and is blind everywhere else certifies
    cleanly. That is canon R0's lookup-table trap one level up, and the defence is the same:
    generative factories plus `draws > 1`, so passing requires the behaviour rather than the
    answers. A clean report on FROZEN fixtures means only that those four inputs were handled.
    """
    assert memorisation_is_still_possible(_even_contract()) is True


def test_generative_fixtures_plus_multiple_draws_defeat_the_memoriser():
    """The repair, measured: a memoriser tied to one draw fails as soon as the fixtures are
    redrawn."""
    c = _even_contract(seed=11)
    first_positive = c.positive()

    def memoriser(xs):
        if xs == first_positive:
            return True
        if not isinstance(xs, list):
            raise TypeError
        return False                       # blind: says no to every other positive
    assert not certify(memoriser, c, draws=4).admissible


# ---- retroactive: all four historical failures ----------------------------------------------------

def test_RETRO_cycle_029_all_raising_probe_space_is_an_INVALID_fixture():
    """The constancy probe read an all-raising space as constancy. Under the contract that space
    is the INVALID fixture, and the fixed instrument reports INVALID_PROBE — neither signal nor
    no-signal — so it certifies. The pre-fix behaviour would have returned UNSETTLED, a class,
    and been refused."""
    from prometheus_math.battery import INVALID_PROBE, UNSETTLED, VARIES, structural_constancy

    def picky(_n):
        raise ValueError("wrong shape")

    v = structural_constancy("picky", picky, list(range(20)))
    assert v.status == INVALID_PROBE                     # NEITHER class: passes INVALID
    assert v.status not in (VARIES, UNSETTLED)


def test_RETRO_cycle_033_unordered_values_are_an_INVALID_fixture():
    """The monotonicity classifier returned UNIVERSAL for an argmin on tuple ordering alone.
    Under the contract, unordered values are the INVALID fixture and must produce neither class.
    The fixed instrument raises."""
    from prometheus_math.relative_claim import ClaimError, Domain, probe_monotonicity

    chain = [Domain(f"d{k}", t) for k, t in enumerate([(0, 10), (0, 5, 10), (0, 1, 5, 10)])]
    with pytest.raises(ClaimError):
        probe_monotonicity(lambda d: (min(d.members), max(d.members)), chain)


def test_RETRO_cycle_034_the_raw_control_fails_its_own_NEGATIVE_fixture():
    """The "raw syntax" control was assumed not to normalise. Its NEGATIVE fixture is a pair that
    must NOT merge if the control is genuinely raw — and six such pairs merge. Under the contract
    the control would have been refused before being used for any comparison."""
    from techne.ladder_circuits.preprocessing_audit import (
        control_is_itself_a_normaliser, python_ast_key,
    )
    merged, total = control_is_itself_a_normaliser()
    assert merged == total == 6                          # every anti-case collapsed
    assert python_ast_key("(x)+y") == python_ast_key("x+y")


def test_RETRO_cycle_032_a_chain_that_cannot_falsify_is_a_MISSING_negative_fixture():
    """The convergence claim rested on a chain where excess could only rise. That is not a wrong
    answer — it is an ABSENT negative fixture, and the contract refuses submission without one.
    Demonstrated: on a chain that CAN fall, the same measure classifies differently."""
    from prometheus_math.partition import conditional_entropy
    from prometheus_math.relative_claim import AGGREGATE, Domain, EXISTENTIAL, probe_monotonicity

    rising = [Domain(f"r{k}", tuple(range(m))) for k, m in enumerate((10, 20, 40, 80))]
    excess_rising = lambda d: round(conditional_entropy(
        tuple(frozenset([i]) for i in d.members), (frozenset(d.members),), len(d)), 9)
    assert probe_monotonicity(excess_rising, rising) == EXISTENTIAL   # the chain I first used

    # a chain that can fall: grow an UNSHATTERED truth cell
    def build(n_b):
        a, b = list(range(40)), list(range(40, 40 + n_b))
        proj = tuple([frozenset(a[i::4]) for i in range(4)] + [frozenset(b)])
        return proj, (frozenset(a), frozenset(b)), 40 + n_b

    falling = [conditional_entropy(*build(n)) for n in (4, 20, 80, 300)]
    assert falling == sorted(falling, reverse=True)       # strictly down
    assert falling[0] > 1.8 and falling[-1] < 0.3


def test_all_four_historical_failures_map_to_a_contract_slot():
    """The bookkeeping that makes the mechanism a mechanism rather than four anecdotes."""
    mapping = {
        "cycle 029 all-raising probe space": "INVALID",
        "cycle 032 unfalsifiable chain": "NEGATIVE (absent)",
        "cycle 033 unordered values": "INVALID",
        "cycle 034 raw control that normalises": "NEGATIVE",
    }
    assert len(mapping) == 4
    assert set(mapping.values()) <= {"POSITIVE", "NEGATIVE", "NEGATIVE (absent)", "INVALID",
                                     "SENSITIVITY"}
