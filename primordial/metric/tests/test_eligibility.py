"""G-R5-4: w13 train128_held64 eligibility from G's committed R16 rows, without a worlds_r4/v2 file."""
from __future__ import annotations

import pytest

from primordial.metric import eligibility as EL
from primordial.metric import readout as RO
from primordial.metric import worlds as WR
from primordial.ops import qd_ledger as Q

T = "train128_held64"

CAND = dict(rng_family_count=4, runs_per_family=8)          # G-R5-2: a CANDIDATE_N-eligible sample (runs_total 32 passed positionally)


def test_w13_is_survived_from_r16_rows_with_the_posted_numbers():
    e = EL.w13_eligibility()
    assert e["eligible"] and e["verdict"] == "SURVIVED" and e["variant"] == "gate_in|HOLD"
    assert e["floor"] == 166.46875 and e["gate_held64"] == 166.46875
    assert e["floor_parts"]["input_invariant_learner"] == 151.75 and e["floor_parts"]["abstain"] == 159.0
    b = e["baseline"]
    assert b["median"] == 183.90625 and b["ci95"] == [170.953125, 188.5625] and b["bytes"] == 200
    assert b["readout"] == RO.NAME and b["n_runs"] == 32 and b["families"] == [2101, 3303, 4200, 5501]
    assert e["progress_denominator"] == 183.90625 - 166.46875
    assert all(e["rows_commits"].values()) and e["scope"] == EL.SCOPE


def test_doc_holds_only_complete_cells_and_is_never_written(tmp_path, monkeypatch):
    before = WR.WORLDS_R4.read_bytes()
    doc = EL.r16_doc()
    assert [(c["world"], c["pressure"]) for c in doc["cells"]] == [("w13", T)]
    assert doc["schema"] == WR.SCHEMA_V2 and WR.v2_defects(doc) == [] and WR.blocking(doc) == []
    assert WR.WORLDS_R4.read_bytes() == before                         # the committed v1 file is untouched
    with pytest.raises(ValueError, match="no R16 baseline"):
        EL.r16_doc(cells=[(13, "train8_held64")])                        # J2 never reached w13 train8
    with pytest.raises(ValueError, match="without R16 floor rows"):
        EL.r16_doc(cells=[(7, "train8_held64")])                         # J1 parked before w7's floor row


def test_check_judges_a_candidate_on_w13_alone_and_nothing_else():
    doc = EL.r16_doc()
    other = Q.check_r4("w7", "train8_held64", 1e9, 1, 32, **CAND, doc=doc)
    assert other["verdict"] == "INELIGIBLE" and other["why"] == "UNSCREENED"
    got = Q.check_r4("w13", T, 183.90625, 199, 32, **CAND, doc=doc, readout=RO.NAME)
    assert got.get("why") not in ("UNSCREENED", "BASELINE_N")                # the cell is judged, not refused by the screen
    assert got.get("floor") == 166.46875 and got.get("baseline_median") == 183.90625
    legacy = Q.check_r4("w13", T, 183.90625, 199, 32, **CAND, doc=doc)                  # undeclared readout = legacy top-16
    assert legacy["why"] == "READOUT_MISMATCH"
    assert EL.eligibility("w1", "train8_held64", doc)["verdict"] == "UNSCREENED"
