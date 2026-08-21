"""Structural-constancy sweep across the repo's kill batteries — cycle 029, READ-ONLY.

Twelve members across three batteries. The headline is a NEGATIVE result: F9 is the only
structurally-constant member found anywhere, so the substrate does not have a systemic problem —
it has one isolated instance, already reported.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from prometheus_math.battery import (  # noqa: E402
    INVALID_PROBE, PARAMETER_INDEPENDENT, UNSETTLED, VARIES,
)
from techne.ladder_circuits.constancy_sweep import (  # noqa: E402
    half_coeff_probes, polynomial_probes, sweep_all, sweep_discovery_pipeline,
    sweep_lehmer_brute_force, sweep_r6_circuits,
)


@pytest.fixture(scope="module")
def rows():
    return sweep_all()


# ---- the headline is negative ------------------------------------------------------------------

def test_F9_IS_THE_ONLY_STRUCTURALLY_CONSTANT_MEMBER_IN_THE_SWEEP(rows):
    """**A negative result, and the useful kind.** Twelve members across three batteries and the
    only one that provably cannot fire is F9, already reported at cycle 028.

    The substrate does not have a systemic dead-check problem. It has one instance, and the
    sweep is now available to catch the next.
    """
    constant = [r for r in rows if r.status == PARAMETER_INDEPENDENT]
    assert [r.member for r in constant] == ["F9"]
    assert len(rows) >= 12


def test_no_probe_space_came_back_invalid(rows):
    """Guard on the sweep itself: an INVALID_PROBE row means the probes never exercised the
    member, so any verdict about it would be about my inputs rather than its code."""
    assert not [r for r in rows if r.status == INVALID_PROBE]
    assert all(r.n_evaluated > 0 for r in rows)


def test_the_discovery_kill_path_is_otherwise_live(rows):
    """Every other member of the discovery pipeline's kill path flips on some input, including
    the reciprocity and irreducibility gates that were never measured before."""
    dp = {r.member: r.status for r in rows if r.battery == "discovery_pipeline"}
    assert dp["F1"] == dp["F6"] == VARIES
    assert dp["reciprocity"] == dp["irreducibility"] == dp["catalog_miss"] == VARIES
    assert dp["F9"] == PARAMETER_INDEPENDENT


def test_the_lehmer_checks_are_live_once_the_probes_have_the_right_shape(rows):
    """Both `lehmer_brute_force` members flip — but only after the probe shape was fixed. See
    the INVALID_PROBE test below for what they reported before."""
    lb = {r.member: r.status for r in rows if r.battery == "lehmer_brute_force"}
    assert lb["cyclotomic_factor"] == VARIES
    assert lb["mossinghoff_lookup"] == VARIES


# ---- F11 refines the cycle-028 finding rather than contradicting it -------------------------------

def test_F11_VARIES_under_a_hostile_probe_space_and_that_REFINES_cycle_028(rows):
    """Cycle 028 measured F11 at 0.000 bits over well-formed candidates and called it vacuous
    over candidates. Under a HOSTILE probe space — which includes inconsistent `m_value`s — it
    reads VARIES.

    Both are true and they answer different questions. Natural sampling measures REALIZED
    discrimination; mutation testing measures CAPABILITY. F11 is constant on well-formed input
    and not structurally constant, so **a constancy verdict must always be reported with the
    input space it was measured on.**
    """
    f11 = next(r for r in rows if r.member == "F11")
    assert f11.status == VARIES

    from techne.ladder_circuits.battery_chain import check_resolution
    assert check_resolution()["F11"] == pytest.approx(0.0)      # still zero on real candidates


# ---- my own instrument had the defect it was built to detect --------------------------------------

def test_AN_ALL_RAISING_PROBE_SPACE_ONCE_MASQUERADED_AS_UNSETTLED():
    """**The cycle's most useful self-catch, preserved as a test.**

    The first sweep passed full coefficient lists to `lehmer_brute_force`, whose members require
    exactly length-8 HALF coefficients. All 90 calls raised. The probe mapped every exception to
    one sentinel, saw "one distinct value, no flip", and reported UNSETTLED — an instrument fault
    dressed as a finding about the code, which is precisely the confusion the probe exists to
    prevent.

    Reproduced here with the wrong-shaped probes, and it now reports INVALID_PROBE.
    """
    from prometheus_math.battery import structural_constancy
    from prometheus_math.lehmer_brute_force import is_reducible_to_cyclotomic_factor as cyc

    wrong_shape = polynomial_probes(limit=40)                  # full coeff lists: all rejected
    v = structural_constancy("cyclotomic_factor",
                             lambda p: cyc(list(p[0]), p[1])[0], wrong_shape,
                             fn_for_source=cyc)
    assert v.status == INVALID_PROBE
    assert v.n_evaluated == 0

    right_shape = half_coeff_probes()
    v2 = structural_constancy("cyclotomic_factor",
                              lambda p: cyc(list(p[0]), p[1])[0], right_shape,
                              fn_for_source=cyc)
    assert v2.status == VARIES and v2.n_evaluated > 0


# ---- the documented limitation, self-audited ------------------------------------------------------

def test_MY_OWN_R6_TRAPS_LAND_IN_UNSETTLED_AND_THAT_IS_THE_KNOWN_GAP(rows):
    """Self-audit, because a sweep that exempts its author is not a sweep.

    `EagerFalsifier` and `CredulousAsserter` are constant-verdict BY CONSTRUCTION — that is what
    makes them traps. But both read their argument for a non-verdict purpose (the conjecture's
    name), so the static tier declines to call them parameter-independent and they land in
    UNSETTLED.

    Parameter-independence is SUFFICIENT for verdict-constancy, not NECESSARY. Closing the gap
    needs dataflow tracing from the parameter to the returned verdict, not a reference scan.
    """
    r6 = {r.member: r.status for r in rows if r.battery == "canon_r6_falsification"}
    assert r6["BoundedSearcher.judge"] == VARIES
    assert r6["EagerFalsifier.judge"] == UNSETTLED
    assert r6["CredulousAsserter.judge"] == UNSETTLED


def test_unsettled_is_reported_as_unknown_not_as_safe(rows):
    """`can_fire` is None for UNSETTLED — genuinely unknown, never silently 'fine'."""
    from prometheus_math.battery import structural_constancy

    def quiet(n):
        return n > 10 ** 9

    assert structural_constancy("q", quiet, list(range(5))).can_fire is None
    assert all(r.status in (VARIES, PARAMETER_INDEPENDENT, UNSETTLED) for r in rows)
