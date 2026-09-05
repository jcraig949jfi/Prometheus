"""Gates on the meter observable, from T2 (RESULT_METER_FLOOR.json).

T1 proposed adopting the meter vector as the primary observable and noted, correctly, that it
needs no new Proteus code because `Meter.as_dict()` is already recorded per encounter. T2 measured
the thing that instruction leaves out: `as_dict()` CONTAINS `wall_s` and `cpu_s`, which are
timings. Used raw, the meter reproduced on 0 of 40 identical re-runs -- every player would differ
from ITSELF, and any composition result read off it would be noise.

These gates make that impossible to adopt by accident.
"""
from __future__ import annotations

import json
import os

from proteus.compose.run_meter_floor import (CONSTANT, NONDETERMINISTIC, manifest_of,
                                             rand_segment, run_player)
from proteus.foundry.identity import hash_obj
from proteus.foundry.prng import SplitMix64
from proteus.foundry.probes import DEFAULT_ENSEMBLE, build_probes
from proteus.foundry.vm import Meter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULT = os.path.join(ROOT, "proteus", "v0_7", "RESULT_METER_FLOOR.json")


def test_raw_meter_contains_nondeterministic_fields():
    """The trap, asserted as present. If this ever fails, the exclusion list is stale."""
    keys = set(Meter().as_dict().keys())
    assert set(NONDETERMINISTIC) <= keys, (
        f"{NONDETERMINISTIC} no longer in Meter.as_dict(); the projection may be over-filtering")
    assert set(CONSTANT) <= keys


def test_deterministic_meter_projection_reproduces():
    """The same player measured twice must give the same deterministic meter."""
    probes = build_probes(DEFAULT_ENSEMBLE)
    rng = SplitMix64(0xD07E)
    for _ in range(6):
        man = manifest_of(rand_segment(rng), rand_segment(rng))
        a, b = run_player(man, probes), run_player(man, probes)
        assert a["meter_hash"] == b["meter_hash"]
        assert a["transcript_hash"] == b["transcript_hash"]


def test_timing_fields_actually_break_reproduction():
    """Negative control: the exclusion must be load-bearing, not decorative.

    If the full meter reproduced too, filtering would be unnecessary caution. It does not.
    """
    probes = build_probes(DEFAULT_ENSEMBLE)
    rng = SplitMix64(0xD07F)
    differing = 0
    for _ in range(6):
        man = manifest_of(rand_segment(rng), rand_segment(rng))
        a, b = run_player(man, probes), run_player(man, probes)
        differing += (a["meter_full_hash"] != b["meter_full_hash"])
    assert differing > 0, (
        "the full meter including wall_s/cpu_s reproduced on every trial; either the machine is "
        "implausibly quiet or the timing fields stopped being recorded -- re-measure T2 before "
        "trusting the exclusion rationale")


def test_meter_is_not_a_size_artifact():
    """Inert padding must not move the meter, or composition results are length results."""
    with open(RESULT, encoding="utf-8") as f:
        r = json.load(f)
    rates = r["part2_discrimination_floor"]["differs_rate"]
    assert rates["identity"] == 0.0, "a player differed from itself"
    assert rates["size_floor"] == 0.0, (
        "inert NOP padding moved the meter; the size confound the directive names is live and "
        "every A+B result must be re-read against it")
    assert rates["treatment"] > rates["size_floor"]


def test_meter_can_see_order_and_partner():
    """Prerequisites for ordered composition (A->B) and for partner-specific effects."""
    with open(RESULT, encoding="utf-8") as f:
        r = json.load(f)
    rates = r["part2_discrimination_floor"]["differs_rate"]
    assert rates["order"] > 0.0, "the observable cannot distinguish A+B from B+A at all"
    assert rates["partner_identity"] > 0.0, "the observable cannot tell which partner was used"


def test_class_richness_claim_carries_its_null():
    """The 37-class figure must never be cited without the floor beside it."""
    with open(RESULT, encoding="utf-8") as f:
        r = json.load(f)
    p1 = r["part1_population_structure_floor"]
    null = p1["null_distribution_of_distinct_classes"]["ops_by_category"]
    obs = p1["observed_in_closure_pass"]["ops_by_category"]
    assert null["min"] <= obs <= null["max"], (
        "the observed class count now sits OUTSIDE the null range; that is a change worth "
        "adjudicating rather than silently re-baselining")
