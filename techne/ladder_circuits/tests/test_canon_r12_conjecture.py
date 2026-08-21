"""CANON R12 acceptance suite — an AUDIT of the grader canon §7 says was never run.

It was run this cycle. `harmonia/experiments/r12_grader.py` exists, its 17 unit tests pass, and
its offline runner discriminates good from overfit from naive exactly as designed. This suite
does not re-grade R12; it points the standing instruments at the grader and records what they
find.

Three findings, all measured:
  1. The two scoring channels are asymmetrically defended — one subtracts a baseline, the other
     does not, and a probe chosen with no reasoning averages 0.443 efficiency.
  2. The canon's own kill test ("a small closed universe") IS an aliasing statement, and the
     witness is unbreakable from inside — R11's shape, not R6/R9/R10's.
  3. Claim v13 at its sharpest: best-of-N inflation grows monotonically with N and nothing in
     the emission reveals N.
"""
from __future__ import annotations

import pathlib
import statistics
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.aliasing import (  # noqa: E402
    find_aliasing_witness, verify_factorization,
)
from techne.ladder_circuits.canon_r12_conjecture import (  # noqa: E402
    CLOSED_UNIVERSE_TWINS, best_of_n_inflation, closed_universe_alias_pair, constant_probe_gain,
    extension_of, informed_probe_gain, small_universe, trials, wide_universe,
)

SEEDS = [20260529, 20260530, 20260531, 20260601, 20260602]


@pytest.fixture(scope="module")
def ts():
    return trials(SEEDS)


# ---- the grader exists, and it works -----------------------------------------------------------

def test_the_grader_canon_says_was_never_run_exists_and_discriminates(ts):
    """FIRST JOB, discharged. The grader is real and it separates the three mock arms on the
    conjecture channel: a correct rule earns positive quality with an exact partition; an
    overfitted enumeration and a constant-true both collapse to zero under the baseline
    penalty."""
    from r12_grader import grade_conjecture
    t = ts[0]
    from r12_universe import pred_to_python
    good = grade_conjecture(t, t.target_sig)
    naive = grade_conjecture(t, extension_of("True", t.universe))
    assert good.quality > 0.0 and good.exact_partition and good.raw_holdout_acc == 1.0
    assert naive.quality == 0.0
    assert naive.most_similar_baseline in naive.baseline_jaccards


# ---- finding 1: the two channels are asymmetrically defended -----------------------------------

def test_FINDING_the_test_quality_channel_subtracts_no_baseline(ts):
    """**The defect running it surfaced.**

    Conjecture-quality is baseline-penalised: it is zeroed when a naive baseline is at least as
    close to the target. Test-quality reports `info_gain / optimal_gain` with nothing subtracted.

    Measured over five seeds, proposing a FIXED universe object chosen without looking at
    anything: efficiencies 0.000, 0.566, 0.647, 1.000, 0.000 — mean 0.443, and full marks on one
    trial. That is what the overfit arm is banking when it scores 0.000 on conjectures and ~0.6
    bits on tests.
    """
    gains = [constant_probe_gain(t) for t in ts]
    assert statistics.fmean(gains) > 0.35
    assert max(gains) == pytest.approx(1.0)          # zero reasoning, full marks, one trial in five
    assert all(informed_probe_gain(t) == pytest.approx(1.0) for t in ts)


def test_the_conjecture_channel_by_contrast_IS_baseline_corrected(ts):
    """The asymmetry, shown on the same trials: the constant-true conjecture is zeroed, while
    the constant probe is not."""
    from r12_grader import grade_conjecture
    for t in ts:
        assert grade_conjecture(t, extension_of("True", t.universe)).quality == 0.0
    assert statistics.fmean(constant_probe_gain(t) for t in ts) > 0.0


# ---- finding 2: the canon's kill test is an aliasing statement -----------------------------------

def test_FINDING_small_closed_universe_is_exactly_an_aliasing_witness():
    """Canon's kill for R12 is *"a small closed universe"*. Restated with the cycle-018
    instrument, that is precisely: the projection (extension over the graded universe) is not
    sufficient for the target anyone wants (does the rule hold generally).

    Three conjectures — `True`, `x <= 7`, `s <= 14` — accept all 64 objects of the 0..7 universe.
    Identical to any grader that observes only that universe. Widen to 0..15 and they accept
    256, 128 and 120 of 256. The witness is not subtle; it is the rung's whole hazard.
    """
    small, wide = small_universe(), wide_universe()
    on_small = lambda src: len(extension_of(src, small))
    on_wide = lambda src: len(extension_of(src, wide))

    assert {on_small(s) for s in CLOSED_UNIVERSE_TWINS} == {64}
    assert sorted(on_wide(s) for s in CLOSED_UNIVERSE_TWINS) == [120, 128, 256]

    w = find_aliasing_witness(list(CLOSED_UNIVERSE_TWINS), on_small, on_wide,
                              note="extension over the graded universe vs over a wider one")
    assert w is not None and w.projection_value == 64


def test_the_witness_is_UNBREAKABLE_from_inside_the_universe():
    """R11's shape, not R6/R9/R10's. There is no better projection available to a grader
    confined to the universe it was given: extension over that universe is already everything
    observable there. Widening the universe is not a sharper instrument, it is a different
    experiment — and the canon's kill is the instruction to run it.

    HITL #53 asked whether rungs come in two kinds. R11 and R12 are both the second kind.
    """
    small = small_universe()
    everything_observable = lambda src: extension_of(src, small)
    truth_inside = lambda src: extension_of(src, small)
    assert find_aliasing_witness(list(CLOSED_UNIVERSE_TWINS),
                                 everything_observable, truth_inside) is None


def test_the_factorization_precondition_holds_for_the_widening():
    """Per cycle 019, check before asserting. Agreement on the wide universe implies agreement
    on the small one — the small view is a coarsening — so a witness under the wide view binds
    a grader confined to the small one."""
    small, wide = small_universe(), wide_universe()
    sources = list(CLOSED_UNIVERSE_TWINS) + ["obj['x'] <= 3", "obj['x'] >= 6", "obj['s'] >= 11"]
    coarse = lambda src: len(extension_of(src, small))
    fine = lambda src: tuple(sorted(extension_of(src, wide)))
    assert verify_factorization(sources, coarse, fine)


# ---- finding 3: claim v13 at its sharpest ---------------------------------------------------------

def test_FINDING_best_of_N_inflation_grows_monotonically_and_is_undeclared(ts):
    """**Claim v13 where it bites hardest**, because R12 generates its own candidate list.

    A generator that internally draws N conjectures consistent with the revealed data and
    reports its best publishes a record in which nothing is false: the candidate really is
    consistent, and the score really is that candidate's score. What is missing is the other
    N − 1 attempts, and no function of the emission can recover them.

    Measured mean inflation over five seeds: +0.042 (N=2), +0.098 (4), +0.129 (8), +0.173 (16),
    +0.188 (32) — against honest means near 0.2, so best-of-32 roughly doubles the reported
    score. And the emission carries no N.
    """
    means = {n: statistics.fmean(best_of_n_inflation(t, n=n).inflation for t in ts)
             for n in (2, 4, 8, 16, 32)}
    assert means[2] < means[4] < means[8] < means[16] < means[32]
    assert means[32] > 0.15
    assert all(best_of_n_inflation(t, n=8).declared_n is None for t in ts)


def test_declaring_N_is_the_only_thing_that_makes_the_number_readable(ts):
    """The defence, and it is bookkeeping rather than a metric: the report is interpretable
    exactly when N is declared alongside it. `declared_n` is a field an honest generator fills
    and a selective one cannot be forced to — which is why the ledger must be external."""
    honest = best_of_n_inflation(ts[0], n=8, declared_n=8)
    silent = best_of_n_inflation(ts[0], n=8)
    assert honest.best_of_n == silent.best_of_n          # identical published score
    assert honest.declared_n == 8 and silent.declared_n is None
    assert honest.inflation > 0.0                        # and the inflation is real
