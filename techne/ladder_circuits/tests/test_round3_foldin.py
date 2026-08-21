"""Cycle 008: executable versions of all three round-3 items.

1. R5 demotion accepted + the two rescues built: coupled execution (run-twice cannot even
   run) and relational invariants (transient-violation probe kills endpoint comparison).
2. Existential-elimination battery for generative resources: reuse=unsound (caught),
   palette=exhausted, abstain=incomplete, counter/SkolemID=complete+sound; distinctness
   pressure kills the always-aux_1 system.
3. Operator plasticity: the fake-synthesis kill — cache dies on held-out substitutions,
   the induced operator survives; and the vocabulary itself grows (R_t -> R_{t+1}).
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r5_relational import (  # noqa: E402
    CoupledBranches, RelationalExecutor, endpoint_checker, run_twice_attempt,
)
from techne.ladder_circuits.skolem_fresh import (  # noqa: E402
    Context, Unsound, always_aux1_allocator, counter_allocator, eliminate,
    exhaustion_context, palette_allocator, reuse_allocator, skolem_id_allocator,
)
from techne.ladder_circuits.operator_plasticity import (  # noqa: E402
    OperatorSynthesizer, TraceCache,
)


# ---- 1a. coupled execution -----------------------------------------------------------------

def test_coupled_dynamics_run_twice_cannot_even_execute():
    """a' = a + b, b' = b - a: each step of either branch needs the OTHER's current value.
    The pair-stepper computes; the sequential-isolated strategy abstains (and the stale-b0
    liar is provably wrong by step 3)."""
    cb = CoupledBranches(f=lambda a, b: a + b, g=lambda b, a: b - a, a=1.0, b=2.0).step(3)
    assert run_twice_attempt(lambda a, b: a + b, lambda b, a: b - a, 1.0, 2.0, 3) is None
    # the liar: run branch A alone feeding the initial b0 forever
    a_stale, b0 = 1.0, 2.0
    for _ in range(3):
        a_stale = a_stale + b0
    assert a_stale != cb.a  # stale coupling gives the wrong trajectory


# ---- 1b. relational invariants: the transient-violation probe ------------------------------

def _step(s):
    """Dynamics where z diverges mid-run and reconverges: z' = -z when y crosses 0."""
    y, z = s
    y2 = y - 1
    z2 = -z if y2 == 1 else z
    return (y2, z2)


def test_transient_violation_kills_endpoint_comparison():
    """Noninterference claim: 'flipping the premise never changes z'. Start states differ in
    y only. z flips sign mid-run in one branch and flips BACK — endpoints agree (endpoint
    checker certifies the false invariant); the relational executor catches the violation at
    the step it happens."""
    inv = lambda s0, s1: s0[1] == s1[1]
    s0, s1 = (4.0, 1.0), (2.0, 1.0)  # premise flip changed y only
    n = 4
    assert endpoint_checker(s0, s1, _step, n, inv) is True  # fooled
    ex = RelationalExecutor(invariant=inv)
    _f0, _f1, ok = ex.run(s0, s1, _step, n)
    assert ok is False and ex.violations, "relational executor must catch the transient"


# ---- 2. existential elimination -------------------------------------------------------------

def test_reuse_is_caught_unsound():
    with pytest.raises(Unsound):
        eliminate(Context({"a1", "a2"}, ["P"]), reuse_allocator)


def test_palette_dies_exactly_at_exhaustion_generators_do_not():
    palette = ["p1", "p2", "p3"]
    below = Context({"p1"}, ["P"])
    assert eliminate(below, palette_allocator(palette)) is not None
    gamma_n = exhaustion_context(palette)
    assert eliminate(gamma_n, palette_allocator(palette)) is None  # sound abstention
    for gen in (counter_allocator(), skolem_id_allocator):
        out = eliminate(gamma_n, gen)
        assert out is not None and out[0] not in gamma_n.symbols


def test_distinctness_pressure_kills_always_aux1():
    """Two existentials need INDEPENDENTLY fresh witnesses. always-aux_1 passes the single
    probe and is caught unsound on the second generation."""
    single = Context({"a1"}, ["P"])
    assert eliminate(single, always_aux1_allocator) == ["aux_1"]
    double = Context({"a1"}, ["P", "Q"])
    with pytest.raises(Unsound):
        eliminate(double, always_aux1_allocator)


def test_skolem_id_freshness_is_deterministic():
    """Their nicer allocator: same context -> same fresh names, run to run. Freshness needs
    an inexhaustible NAMESPACE, not randomness."""
    ctx = lambda: Context({"a1", "a2"}, ["P", "Q"])
    assert eliminate(ctx(), skolem_id_allocator) == eliminate(ctx(), skolem_id_allocator)


# ---- 3. operator plasticity: the fake-synthesis kill ----------------------------------------

def test_KILL_cache_memorizes_synthesizer_abstracts():
    f = lambda x: 3 * x + 1
    train = [2, 5, 9]
    heldout = [104, -7, 1000]
    cache, synth = TraceCache(), OperatorSynthesizer(f=f)
    for x in train:
        cache.observe_chunk(x, f(f(x)))
        synth.observe_chunk(x, f(f(x)))
    for x in train:  # both perfect on seen substitutions
        assert cache.answer_two_step(x) == synth.answer_two_step(x) == f(f(x))
    for x in heldout:  # the kill: only the induced operator survives unseen theta
        assert cache.answer_two_step(x) is None
        assert synth.answer_two_step(x) == f(f(x))


def test_the_vocabulary_itself_grew():
    """R_t -> R_{t+1}: after installation the rule set contains an operator nobody supplied."""
    f = lambda x: x + 7
    synth = OperatorSynthesizer(f=f)
    assert synth.vocabulary() == ["f"]
    for x in (1, 2, 3):
        synth.observe_chunk(x, f(f(x)))
    assert synth.vocabulary() == ["f", "g"]
    assert synth.rules["g"](10) == 24


def test_synthesizer_audits_observations_not_blind_trust():
    """Corrupted trace evidence must NOT trigger installation — inducing an operator from
    unverified traces would be the metabolization mistake in miniature."""
    f = lambda x: x * 2
    synth = OperatorSynthesizer(f=f)
    for x in (1, 2, 3, 4):
        synth.observe_chunk(x, 999)  # wrong chunks
    assert synth.answer_two_step(5) is None
