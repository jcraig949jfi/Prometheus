"""H-R7-1: EVIDENCE_N_v1 -- one rule; family balance is structural; OBSERVATION cannot carry PASS/FAIL."""
from __future__ import annotations

import json

import pytest

from primordial.score import evidence_n as EN

FAMS = [4200, 2101, 3303, 5501]


def sample(per, runs_per_family="auto"):
    counts = dict(zip(FAMS[:len(per)], per))
    total = sum(per)
    rpf = (per[0] if len(set(per)) == 1 else None) if runs_per_family == "auto" else runs_per_family
    return {"runs_total": total, "rng_family_count": len(per), "runs_per_family": rpf,
            "families": list(counts), "n_per_family": {str(k): v for k, v in counts.items()}}


GOOD = sample([8, 8, 8, 8])
# the E-R6-1 envelope exactly as the job spec carried it (pm:jobs:E 1789485387695-0): no sample block
E_R6_1 = json.loads('{"campaign_stage": "PRODUCTION", "checkpointable": true, "cohort": "E", "cpu_budget_s": 6000, '
                    '"expected_output_rows": 50, "experiment_class": "CLAUSE_B", "gpu_budget_s": 0, '
                    '"predicate_id": "E-R6-1-clauseB-live-w14-w13", "required_controls": ["scratch", "sham_featperm"], '
                    '"required_oracles": ["world", "brain", "fused_eq_numpy", "sham_integrity"], "wall_budget_s": 2400}')


def env(cls="CLAUSE_B", s=None, ec=None):
    """Sample fields at the envelope's top level (F 1789504304514-0)."""
    e = {"experiment_class": cls, **(s or {})}
    if ec is not None:
        e["evidence_class"] = ec
    return e


def test_admission_reasons_is_the_admit_hook_and_a_sample_block_is_also_read():
    assert EN.admission_reasons(env(s=GOOD)) == []
    assert EN.admission_reasons(env(s=sample([16]))) == ["SAMPLE_RULE_MISMATCH"]
    assert EN.admission_reasons({"experiment_class": "CLAUSE_A", "sample": GOOD}) == []
    assert EN.admission_reasons(env("PROBE")) == []


def test_the_rule_is_exactly_32_4_8_balanced():
    assert EN.RULE == "EVIDENCE_N_v1" and EN.NEED == {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8}
    assert EN.VERDICT_CLASSES == {"CLAUSE_A", "CLAUSE_B", "ANTI_PRIOR", "DISTANT_QD", "ROBUSTNESS_LOO", "REPLICATION",
                                  "B2_SCREEN", "R16_SCREEN_CELL"}
    assert EN.failures(GOOD) == [] and EN.admission(env(s=GOOD)) is None


@pytest.mark.parametrize("name,s", [
    ("16/1/16", sample([16])),
    ("32/4/(16,8,4,4)", sample([16, 8, 4, 4])),
    ("32/4/(29,1,1,1)", sample([29, 1, 1, 1])),
    ("40/5/8", {**sample([8, 8, 8, 8]), "runs_total": 40, "rng_family_count": 5}),
    ("32/4/8 declared but families unbalanced", {**sample([16, 8, 4, 4]), "runs_per_family": 8}),
    ("3 declared families", {**GOOD, "families": FAMS[:3]}),
    ("n_per_family keys differ", {**GOOD, "n_per_family": {"4200": 8, "2101": 8, "3303": 8, "9999": 8}}),
    ("duplicate family ids", {**GOOD, "families": [4200, 4200, 3303, 5501]}),
    ("no sample block", None),
])
def test_planted_shapes_are_refused_at_admission(name, s):
    for cls in EN.VERDICT_CLASSES:
        got = EN.admission(env(cls, s))
        assert got is not None and got["reason"] == "SAMPLE_RULE_MISMATCH" and got["rule"] == "EVIDENCE_N_v1", name
        assert got["failures"]


def test_the_e_r6_1_envelope_replayed_is_refused():
    got = EN.admission(E_R6_1)
    assert got["reason"] == "SAMPLE_RULE_MISMATCH" and got["failures"]
    assert EN.admission({**E_R6_1, **sample([16])})["reason"] == "SAMPLE_RULE_MISMATCH"         # its real 16/1/16
    assert EN.admission({**E_R6_1, **GOOD}) is None                                              # the 32/4/8 rerun


def test_observation_is_admitted_at_any_size_and_non_verdict_classes_are_not_checked():
    assert EN.admission(env("CLAUSE_B", sample([16]), ec="OBSERVATION")) is None
    assert EN.admission(env("PROBE", sample([16]))) is None
    assert EN.admission(env("MEASUREMENT")) is None
    bad = EN.admission(env("PROBE", GOOD, ec="maybe"))
    assert bad["reason"] == "SAMPLE_RULE_MISMATCH" and "evidence_class" in bad["failures"][0]


@pytest.mark.parametrize("rec,reasons", [
    ({"evidence_class": "OBSERVATION", "status": "PASS"}, ["OBSERVATION_CARRIES_VERDICT"]),
    ({"envelope": {"evidence_class": "OBSERVATION"}, "status": "INDETERMINATE", "science": {"verdict": "FAIL"}},
     ["OBSERVATION_CARRIES_VERDICT"]),
    ({"evidence_class": "OBSERVATION", "status": "INDETERMINATE", "science": {"reading": "check_b FAIL-like"}}, []),
    ({"evidence_class": "OBSERVATION", "status": "NULL"}, []),
    ({"status": "PASS", "evidence_class": "SOMETIMES"}, ["SAMPLE_RULE_MISMATCH"]),
])
def test_receipt_rules(rec, reasons):
    assert [x["reason"] for x in EN.receipt(rec)] == reasons


def test_the_sample_block_of_a_receipt():
    assert EN.sample_of({"sample": GOOD}) == GOOD
    top = {**GOOD, "status": "PASS"}
    assert EN.sample_of(top) == GOOD
    assert EN.sample_of({"science": GOOD}) == GOOD
