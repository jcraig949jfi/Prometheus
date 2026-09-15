"""G-R5-3 (O2): the B2 admission rule -- four verdicts in fixed precedence, pilot sample, never SURVIVED, cost estimate."""
from __future__ import annotations

import pytest

from primordial.metric import b2_screen as B2

PILOT = {"runs_total": 16, "rng_family_count": 2, "runs_per_family": 8, "families": [2101, 4200],
         "n_per_family": {"2101": 8, "4200": 8}}


def spec(sid, floor, lo, hi, oracles=None, sample=PILOT, readout="top1_train", stats=True):
    s = {"spec_id": sid, "oracles": {"O1_forms_agree": True, "O2_cheat_detected": True} if oracles is None else oracles,
         "floor_parts": {"abstain": floor, "best_constant": floor - 1, "uniform_random_median": 0.0,
                         "input_invariant_learner": floor - 2},
         "baseline": {"ci95": [lo, hi], "median": (lo + hi) / 2, "readout": readout, **sample}}
    if stats:
        s["floor_stats"] = {"uniform_random_median": dict(sample), "input_invariant_learner": dict(sample)}
    return s


def test_worthy_needs_one_spec_with_ci_low_above_its_floor():
    got = B2.verdict([spec("a", 100.0, 90.0, 99.0), spec("b", 100.0, 100.5, 120.0)])
    assert got["verdict"] == B2.WORTHY and [r["ci_low_above_floor"] for r in got["per_spec"]] == [False, True]


def test_ci_low_equal_to_floor_is_not_worthy():
    assert B2.verdict([spec("a", 100.0, 100.0, 110.0)])["verdict"] == B2.INDETERMINATE


def test_unpromising_needs_every_spec_ci_high_below_its_floor():
    assert B2.verdict([spec("a", 100.0, 80.0, 99.0), spec("b", 50.0, 10.0, 49.9)])["verdict"] == B2.UNPROMISING
    assert B2.verdict([spec("a", 100.0, 80.0, 99.0), spec("b", 50.0, 10.0, 50.0)])["verdict"] == B2.INDETERMINATE


def test_indeterminate_when_a_ci_straddles_the_floor():
    assert B2.verdict([spec("a", 100.0, 95.0, 105.0)])["verdict"] == B2.INDETERMINATE


def test_instrument_fail_takes_precedence_over_worthy():
    got = B2.verdict([spec("a", 100.0, 150.0, 160.0),
                      spec("b", 100.0, 150.0, 160.0, oracles={"O1_forms_agree": True, "O2_cheat_detected": False})])
    assert got["verdict"] == B2.INSTRUMENT_FAIL and got["per_spec"][1]["oracles_failed"] == ["O2_cheat_detected"]
    assert B2.verdict([spec("a", 100.0, 150.0, 160.0, oracles={})])["verdict"] == B2.INSTRUMENT_FAIL   # oracles not run


@pytest.mark.parametrize("bad", [
    dict(sample={"runs_total": 8, "rng_family_count": 1, "runs_per_family": 8, "families": [4200], "n_per_family": {"4200": 8}}),
    dict(sample={"runs_total": 16, "rng_family_count": 2, "runs_per_family": None, "families": [2101, 4200],
                 "n_per_family": {"2101": 12, "4200": 4}}),
    dict(readout="m2_top16"),
])
def test_a_below_pilot_or_wrong_readout_spec_cannot_be_worthy_or_unpromising(bad):
    kw = {"sample": PILOT, "readout": "top1_train", **bad}
    hi = B2.verdict([spec("a", 100.0, 150.0, 160.0, sample=kw["sample"], readout=kw["readout"])])
    lo = B2.verdict([spec("a", 100.0, 10.0, 20.0, sample=kw["sample"], readout=kw["readout"])])
    assert hi["verdict"] == lo["verdict"] == B2.INDETERMINATE and hi["per_spec"][0]["problems"]


def test_stochastic_floor_parts_below_the_pilot_sample_block_a_verdict():
    s = spec("a", 100.0, 150.0, 160.0)
    s["floor_stats"]["uniform_random_median"] = {"runs_total": 8, "rng_family_count": 1, "runs_per_family": 8}
    got = B2.verdict([s])
    assert got["verdict"] == B2.INDETERMINATE and "FLOOR_PART_BELOW_PILOT_SAMPLE:uniform_random_median" in got["per_spec"][0]["problems"]


def test_never_survived_and_bounded_spec_count():
    names = set()
    for lo, hi, oracles in ((150, 160, None), (10, 20, None), (95, 105, None), (150, 160, {"O1": False})):
        names.add(B2.verdict([spec("a", 100.0, lo, hi, oracles=oracles)])["verdict"])
    assert names == set(B2.VERDICTS) and "SURVIVED" not in names
    with pytest.raises(ValueError):
        B2.verdict([spec(str(i), 1.0, 2.0, 3.0) for i in range(5)])
    with pytest.raises(ValueError):
        B2.verdict([])


def test_floor_is_the_max_of_parts_run_and_the_gate():
    assert B2.floor_of({"abstain": 3.0, "best_constant": 7.0, "uniform_random_median": None}) == 7.0
    assert B2.floor_of({"abstain": 3.0}, gate_held64=9.5) == 9.5 and B2.floor_of({"abstain": 3.0}, gate_held64=1.0) == 3.0
    assert B2.floor_of({}) is None


def test_a_gate_above_the_parts_raises_the_floor_and_can_remove_worthy():
    s = spec("a", 100.0, 105.0, 120.0)
    assert B2.verdict([s])["verdict"] == B2.WORTHY
    s["gate_held64"] = 110.0                                         # gate_in|HOLD floor = max(parts, gate)
    got = B2.verdict([s])
    assert got["verdict"] == B2.INDETERMINATE and got["per_spec"][0]["floor"] == 110.0


def test_full_screen_cost_arithmetic():
    d = B2.full_screen_cost(0.002, n_specs=1)
    assert d["episodes"]["linear_baseline"] == 32 * (102_400 * 128 + 64)                    # train128 defaults
    c = B2.full_screen_cost(0.002, n_specs=4, train_seeds=8, held_seeds=64, baseline_evals=100, learner_evals=50)
    per = {"abstain": 64, "best_constant": 8 * 72, "uniform_random": 32 * 64,
           "input_invariant_learner": 32 * (50 * 8 + 64), "linear_baseline": 32 * (100 * 8 + 64)}
    assert c["episodes"] == {k: 4 * v for k, v in per.items()} and c["cells"] == 4
    assert c["wall_h_single_worker"] == pytest.approx(sum(4 * v for v in per.values()) * 0.002 / 3600)
    assert c["sample"] == {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8}


def test_pilot_cost_uses_the_pilot_sample_and_flags_production_candidate():
    tiny = B2.pilot_cost(1e-6, n_specs=4, train_seeds=8, held_seeds=64, baseline_evals=10, learner_evals=10)
    assert tiny["sample"] == {"runs_total": 16, "rng_family_count": 2, "runs_per_family": 8}
    assert tiny["episodes"]["linear_baseline"] == 4 * 16 * (10 * 8 + 64) and tiny["outcome"] == "PILOT"
    real = B2.pilot_cost(0.0016, n_specs=4)                                                 # train128 budget
    assert real["outcome"] == "PRODUCTION_CANDIDATE" and not real["fits_pilot_ceiling"]
    assert real["per_spec_job_wall_s"] == pytest.approx(real["wall_h_single_worker"] * 3600 / 4)
