"""B-R5-1: the candidate summary reads eligibility + the one judge; PILOT-sized samples are labelled and refused."""
from __future__ import annotations

from primordial.cohorts.b import r5_1_candidate as C

ORC = {"oracle_clean": True}


def _runs(fams, per, value=190.0):
    return [{"rng_family": f, "run_seed": rs, "held64_per_seed": value + 0.01 * rs, "wall_s": 1.0,
             "control_obs_use": {"held64_w_zeroed": 159.0, "input_invariant_selected": 0, "uses_observations": True}}
            for f in fams for rs in range(per)]


def test_candidate_n_sample_reaches_the_judge():
    s = C.summary(_runs(C.FAMILIES, 8), ORC, C.EXP, "PILOT")
    assert (s["runs_total"], s["rng_family_count"], s["runs_per_family"]) == (32, 4, 8)
    assert s["label"] == "CANDIDATE_N"
    assert s["verdict"] == "PASS" and s["bytes"] == 16 < s["baseline_bytes"]
    assert abs(s["progress_above_floor"] - (s["candidate_score"] - s["floor"]) / s["progress_denominator"]) < 1e-12
    assert s["eligibility"]["verdict"] == "SURVIVED" and s["readout"] == "top1_train"


def test_pilot_sample_is_labelled_and_refused():
    s = C.summary(_runs((C.R4_STREAM,), 16), ORC, C.EXP_REREAD, "PILOT")
    assert s["label"] == "PILOT"
    assert (s["runs_total"], s["rng_family_count"], s["runs_per_family"]) == (16, 1, 16)
    assert s["verdict"] == "INELIGIBLE" and s["why"] == "CANDIDATE_N"


def test_below_floor_candidate_is_not_compression():
    s = C.summary(_runs(C.FAMILIES, 8, value=160.0), ORC, C.EXP, "PILOT")
    assert s["verdict"] == "BELOW_FLOOR" and s["progress_above_floor"] < 0


def test_r4_elites_cover_run_seeds_0_to_15():
    assert sorted(C.r4_elites()) == list(range(16))
