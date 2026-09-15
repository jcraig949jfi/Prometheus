"""G-R7-1: B2 admission rule v2 = EVIDENCE_N_v1 32/4/8, versioned (v1 kept); cost uses E-R7-3's measured overhead."""
from __future__ import annotations

import pytest

from primordial.metric import b2_screen as B2
from primordial.metric import sample as SM
from primordial.metric.tests.test_b2_screen import PILOT, spec

FULL = {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8, "families": [2101, 3303, 4200, 5501],
        "n_per_family": {"2101": 8, "3303": 8, "4200": 8, "5501": 8}}


def test_rules_are_versioned_and_v1_is_kept_unchanged():
    assert B2.RULES[B2.RULE_V1]["sample"] == B2.PILOT_SAMPLE and B2.PILOT_SAMPLE["runs_total"] == 16
    assert B2.RULES[B2.RULE_V2]["sample"] == dict(SM.NEED) and SM.meets(FULL, need=B2.RULES[B2.RULE_V2]["sample"])
    specs = [spec("a", 100.0, 150.0, 160.0), spec("b", 100.0, 10.0, 20.0)]
    assert B2.verdict(specs) == B2.verdict(specs, rule=B2.RULE_V1)                  # the default is still v1, same dict
    assert "rule" not in B2.verdict(specs)
    with pytest.raises(ValueError):
        B2.verdict(specs, rule="B2_ADMISSION_v3")


def test_v2_refuses_a_pilot_sample_and_judges_evidence_n_v1():
    pilot_hi = B2.verdict([spec("a", 100.0, 150.0, 160.0, sample=PILOT)], rule=B2.RULE_V2)
    assert pilot_hi["verdict"] == B2.INDETERMINATE
    assert "BASELINE_BELOW_EVIDENCE_N_v1" in pilot_hi["per_spec"][0]["problems"]
    assert any(p.startswith("FLOOR_PART_BELOW_EVIDENCE_N_v1:") for p in pilot_hi["per_spec"][0]["problems"])
    full_hi = B2.verdict([spec("a", 100.0, 150.0, 160.0, sample=FULL)], rule=B2.RULE_V2)
    assert full_hi["verdict"] == B2.WORTHY and full_hi["rule"] == B2.RULE_V2 and full_hi["sample"]["runs_total"] == 32
    full_lo = B2.verdict([spec("a", 100.0, 10.0, 20.0, sample=FULL)], rule=B2.RULE_V2)
    assert full_lo["verdict"] == B2.UNPROMISING
    for got in (pilot_hi, full_hi, full_lo):
        assert got["verdict"] in B2.VERDICTS and got["verdict"] != "SURVIVED"


def test_v2_cost_adds_the_measured_search_overhead_and_projects_against_the_clock():
    base = B2.full_screen_cost(0.0016, 4, sample=B2.FULL_SAMPLE)
    zero = B2.admission_cost_v2(0.0016, 0.0, n_specs=4, clock_remaining_s=1e12)
    assert zero["total_s_single_worker"] == pytest.approx(base["wall_h_single_worker"] * 3600.0)
    c = B2.admission_cost_v2(0.0016, 0.25, n_specs=4, clock_remaining_s=None)
    assert c["generations_per_run"] == {"linear_baseline": 800, "input_invariant_learner": 800}
    assert c["search_overhead_s"] == pytest.approx(0.25 * 32 * (800 + 800) * 4)
    assert c["total_s_single_worker"] == pytest.approx(c["rollout_s"] + c["search_overhead_s"])
    assert c["outcome"] == "PRODUCTION_CANDIDATE" and not c["fits_clock"]                 # no clock: never admitted
    fits = B2.admission_cost_v2(0.0016, 0.25, n_specs=4, clock_remaining_s=c["total_s_single_worker"] / 4, workers=4)
    assert fits["fits_clock"] and fits["outcome"] == "ADMISSION_SCREEN"
    tight = B2.admission_cost_v2(0.0016, 0.25, n_specs=4, clock_remaining_s=c["total_s_single_worker"] / 4 - 1, workers=4)
    assert not tight["fits_clock"] and tight["outcome"] == "PRODUCTION_CANDIDATE"
    for bad in (None, -0.1):
        with pytest.raises(ValueError):
            B2.admission_cost_v2(0.0016, bad, n_specs=4)


def test_cost_inputs_come_from_the_e_r7_3_row_fields():
    row = {"overhead_s_per_gen": 0.02, "rollout_s_per_gen": 0.1638, "overhead_fraction": 0.109}
    got = B2.cost_inputs_from_e_r7_3(row)
    assert got == {"episode_s": pytest.approx(0.1638 / 16384), "search_overhead_s_per_gen": 0.02}
    c = B2.admission_cost_v2(n_specs=4, clock_remaining_s=3600.0, **got)
    assert c["search_overhead_s_per_gen"] == 0.02 and c["episode_s"] == pytest.approx(0.1638 / 16384)
    with pytest.raises(ValueError):
        B2.cost_inputs_from_e_r7_3({"rollout_s_per_gen": 0.1})
