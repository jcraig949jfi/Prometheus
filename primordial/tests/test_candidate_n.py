"""G-R5-2 (operator 19 O4): CANDIDATE_N -- the three-field sample rule for Clause A candidates, in the one judge."""
from __future__ import annotations

import json

import pytest

from primordial.metric import eligibility as EL
from primordial.metric import readout as RO
from primordial.ops import qd_ledger as Q
from primordial.tests.test_qd_ledger_r4 import doc  # noqa: F401  (fixture: w7 train8 SURVIVED, floor 100, baseline 200)

S8 = "train8_held64"
OK = dict(rng_family_count=4, runs_per_family=8)


def test_eligible_sample_reaches_progress(doc):
    got = Q.check_r4("w7", S8, 195.0, 200, 32, doc=doc, **OK)
    assert got["verdict"] == "PASS" and got["progress"] == pytest.approx(0.95)


@pytest.mark.parametrize("kw,runs", [
    (dict(rng_family_count=2, runs_per_family=8), 16),                 # the round 5 PILOT sample
    (dict(), 32),                                                        # legacy: a run count only
    (dict(rng_family_count=4, runs_per_family=8), 31),                  # runs_total 31
    (dict(rng_family_count=3, runs_per_family=11), 33),                 # 3 families
    (dict(rng_family_count=4, runs_per_family=None, n_per_family={"4200": 29, "2101": 1, "3303": 1, "5501": 1}), 32),
    (dict(rng_family_count=4, runs_per_family=7), 28),
])
def test_under_sampled_candidates_are_refused_candidate_n_with_the_payload(doc, kw, runs):
    got = Q.check_r4("w7", S8, 195.0, 200, runs, doc=doc, **kw)
    assert got["verdict"] == "INELIGIBLE" and got["why"] == "CANDIDATE_N" and "progress" not in got
    assert got["candidate_runs_total"] == runs and got["candidate_rng_family_count"] == kw.get("rng_family_count")
    assert (got["need_runs_total"], got["need_rng_family_count"], got["need_runs_per_family"]) == (32, 4, 8)
    assert got["floor"] == 100.0 and got["baseline_median"] == 200.0


def test_pilot_refusal_is_the_real_judge_and_does_not_depend_on_stage(doc):
    """Operator 19 s3: no smoke judge -- the same call, whatever campaign stage the caller is in."""
    pilot = [Q.check_r4("w7", S8, 250.0, 1, 16, doc=doc, rng_family_count=2, runs_per_family=8) for _ in ("SMOKE", "PILOT", "PRODUCTION")]
    assert all(p == pilot[0] for p in pilot) and pilot[0]["why"] == "CANDIDATE_N"


def test_order_screen_then_baseline_n_then_candidate_n_then_readout(doc):
    assert Q.check_r4("w99", S8, 1e9, 0, 16, doc=doc, rng_family_count=2, runs_per_family=8)["why"] == "UNSCREENED"
    short = json.loads(json.dumps(doc))
    for c in short["cells"]:
        if c["baseline"]:
            c["baseline"]["n_runs"] = 16
    assert Q.check_r4("w7", S8, 195.0, 200, 16, doc=short, rng_family_count=2, runs_per_family=8)["why"] == "BASELINE_N"
    both = Q.check_r4("w7", S8, 195.0, 200, 16, doc=doc, readout="some_other_readout", rng_family_count=2, runs_per_family=8)
    assert both["why"] == "CANDIDATE_N"                                   # before READOUT_MISMATCH
    assert Q.check_r4("w7", S8, 195.0, 200, 32, doc=doc, readout="some_other_readout", **OK)["why"] == "READOUT_MISMATCH"


def test_check_block_for_f12_carries_candidate_n(doc):
    blk = Q.check([], "w7", S8, 195.0, 0.0, 200, 16, doc=doc, rng_family_count=2, runs_per_family=8)["clause_a_r4"]
    assert blk["verdict"] == "INELIGIBLE" and blk["why"] == "CANDIDATE_N" and blk["screen"] == "SURVIVED"
    assert Q.check([], "w7", S8, 195.0, 0.0, 200, 32, doc=doc, **OK)["clause_a_r4"]["verdict"] == "PASS"


def test_cli_candidate_fields_and_r16_screen(doc, tmp_path, capsys):
    from primordial.metric import worlds as WR
    p = WR.write(doc, tmp_path / "w.json")
    Q.main(["check", "--world", "w7", "--pressure", S8, "--median", "195", "--bytes", "200", "--runs", "16",
            "--rng-family-count", "2", "--runs-per-family", "8", "--worlds", str(p)])
    assert json.loads(capsys.readouterr().out)["why"] == "CANDIDATE_N"
    Q.main(["check", "--world", "w13", "--pressure", "train128_held64", "--median", "183.90625", "--bytes", "16",
            "--runs", "32", "--rng-family-count", "4", "--runs-per-family", "8", "--readout", RO.NAME, "--screen", "r16"])
    out = json.loads(capsys.readouterr().out)
    assert out.get("why") not in ("UNSCREENED", "BASELINE_N", "CANDIDATE_N") and out["floor"] == 166.46875
    assert EL.w13_eligibility()["eligible"]
