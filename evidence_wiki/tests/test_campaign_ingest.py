"""The campaign reader's translation rules, without git or a database.

    T1  campaign identity: known seed wins over the producer stamp and the
        path, and the disagreement is written on the row; an unknown seed
        with a producer stamp keeps the stamp (wse-survey-v01, ssf-c1);
        neither -> the path
    T2  campaign-1 attempts are reconstructed from the file pair and say so
    T3/T4  a missing design or engine identity is UNKNOWN, never inferred
    content addressing: the same producer row from two paths is ONE
        observation; a changed row is a different one; identical copies are
        dropped before writing
    cheat: a receipt whose campaign field lies (every C3 receipt says cmp2)
        does not get to name the campaign
"""
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from ew import campaign_ingest as ci  # noqa: E402


def test_t1_seed_wins_and_disagreement_is_noted():
    notes = []
    assert ci.campaign_from(20260920, "cmp2", notes, stamp="cmp2") == "cmp3"
    assert notes and "seed used" in notes[0]
    notes = []
    assert ci.campaign_from(20260918, "cmp2", notes, stamp="cmp2") == "cmp2" and notes == []


def test_t1_unknown_seed_keeps_producer_stamp_else_path():
    notes = []
    assert ci.campaign_from(20260916, "cmp2", notes, stamp="wse-survey-v01") == "wse-survey-v01"
    assert ci.campaign_from(None, "cmp1", notes, stamp=None) == "cmp1"
    assert notes == []


def _ingest(monkeypatch, files, campaign_n=3):
    """An Ingest over an in-memory 'commit'."""
    monkeypatch.setattr(ci, "git_bytes", lambda commit, path: files.get(path))
    monkeypatch.setattr(ci, "git_blob_sha", lambda commit, path: ("blob-" + path) if path in files else None)
    monkeypatch.setattr(ci, "git_ls", lambda commit, prefix: sorted(p for p in files if p.startswith(prefix)))
    return ci.Ingest(campaign_n, "f" * 40, dry_run=True)


REACH = {"cell": "W2_K2", "knobs": {"K": 2}, "N": 200, "G": 60, "E": 16, "seed": 3, "rng_label": "crn",
         "campaign_seed": 20260920, "foundry": "instr1-16:6528b9dc", "regime": "E0", "kind": "baseline",
         "world_id": "wld_x", "best_train_max": 0.53, "heldout": 0.51, "first_foothold_gen": 41,
         "first_solved_gen": 41, "first_shelf_gen": 41, "summit_candidate_gen": None, "first_summit_gen": None,
         "summit_censored": True, "stopped_on_solve": False, "level": "SHELF", "reached": True,
         "value_bits": 4, "solve_threshold": 0.5, "eval_resolution": 0.0625, "trace_best": [0.1, 0.53],
         "source": {"campaign": "cmp2", "experiment": "C3-SFE-01", "attempt": 4, "arm": "fresh"},
         "recorded_at": "2026-09-17T07:45:49Z"}


def test_reachability_row_translation(monkeypatch):
    line = json.dumps(REACH)
    ing = _ingest(monkeypatch, {"archaeon/campaign2/REACHABILITY.jsonl": (line + "\n").encode()})
    assert ing.ingest_jsonl("archaeon/campaign2/REACHABILITY.jsonl", "reachability") == 1
    d = ing.rows[0]
    assert d["campaign_id"] == "cmp3"                      # seed beats the stamp
    assert d["measured"]["_ingest_notes"]                  # and it says so on the row
    assert d["harness_id"] == "C3-SFE-01" and d["attempt_id"] == "C3-SFE-01/a04" and d["arm"] == "fresh"
    assert d["level_as_written"] == "SHELF" and d["censored"] is True and d["horizon"] == 60
    assert d["foundry_profile"] == "instr1-16:6528b9dc" and d["rng_identity"] == "20260920:3:crn"
    assert d["strata"]["budget_class"] == "N200G60E16" and d["strata"]["row_kind"] == "baseline"
    assert d["definition_version"].startswith("archaeon.wse.reachability@")
    assert d["origin_kind"] == "producer" and d["source_line"] == 1
    assert d["design_id"] is None                          # N/A on a reachability row: NULL, not UNKNOWN


def test_content_addressing_same_row_two_paths_one_observation(monkeypatch):
    line = json.dumps(REACH)
    files = {"archaeon/campaign2/REACHABILITY.jsonl": (line + "\n").encode(),
             "archaeon/campaign3/REACHABILITY.jsonl": (line + "\n").encode()}
    ing = _ingest(monkeypatch, files)
    ing.ingest_jsonl("archaeon/campaign2/REACHABILITY.jsonl", "reachability")
    ing.ingest_jsonl("archaeon/campaign3/REACHABILITY.jsonl", "reachability")
    assert len(ing.rows) == 2 and ing.rows[0]["observation_id"] == ing.rows[1]["observation_id"]
    assert ing.dedupe() == 1 and len(ing.rows) == 1
    changed = dict(REACH); changed["heldout"] = 0.52
    assert ci.observation_id("reachability", changed) != ci.observation_id("reachability", REACH)


C1_RECEIPT = {"campaign_seed": 20260917, "purpose": "of record", "records": {"a/1": {"exp_id": "exp_1", "obs_id": "obs_1"}},
              "errors": [], "artifacts": {}}
C3_RECEIPT = {"campaign": "cmp2", "campaign_seed": 20260920, "experiment": "C3-SFE-03", "attempt": 5,
              "attempt_id": "C3-SFE-03/a05", "prereg_digest": "sha256:" + "b" * 64,
              "engine": {"engine_instance_id": "eng_906356f7fb1da180131f9290", "engine_source_hash": "4dbcd3fd"},
              "worlds": {"ladder": "wld_65cb"}, "records": {"p0.1/1": {"exp_id": "exp_3e", "obs_id": "obs_a0"}},
              "errors": [], "artifacts": {"matrices": {"artifact_id": "sha256:" + "c" * 64, "blob_hash": "sha256:" + "d" * 64,
                                                       "bytes": 10, "hash_ok": True, "kind": "json"}},
              "disposition_candidate": {"disposition": "WEAK_POSITIVE"}, "typed_states": []}


def test_c3_receipt_lying_campaign_field_is_overruled_by_seed(monkeypatch):
    files = {"archaeon/campaign3/C3-SFE-03/RECEIPT.json": json.dumps(C3_RECEIPT).encode(),
             "archaeon/campaign3/C3-SFE-03/ATTEMPTS.json": json.dumps({"experiment": "C3-SFE-03", "of_record": 5, "attempts": {"5": {"dir": "attempts/a05", "resumed_from": None}}}).encode()}
    ing = _ingest(monkeypatch, files, 3)
    ing.ingest_experiments()
    rec = [d for d in ing.rows if d["kind"] == "receipt"][0]
    assert rec["campaign_id"] == "cmp3"
    assert any("receipt.campaign='cmp2' disagrees" in n for n in rec["measured"]["_ingest_notes"])
    assert rec["attempt_id"] == "C3-SFE-03/a05" and rec["origin_kind"] == "producer"
    assert rec["design_id"] == "sha256:" + "b" * 64 and rec["design_kind"] == "prereg_digest"
    assert rec["engine_instance_id"] == "eng_906356f7fb1da180131f9290" and rec["world_id"] == "wld_65cb"
    assert rec["measured"]["disposition_candidate"] == {"disposition": "WEAK_POSITIVE"}   # producer's label, as written
    kinds = sorted(d["kind"] for d in ing.rows)
    assert kinds == ["artifact_ref", "attempt", "engine_record", "receipt"]
    er = [d for d in ing.rows if d["kind"] == "engine_record"][0]
    assert er["measured"]["exp_id"] == "exp_3e" and er["attempt_id"] == "C3-SFE-03/a05"


def test_c1_receipt_identities_are_unknown_or_reconstructed(monkeypatch):
    files = {"archaeon/campaign1/SFE-07/RECEIPT.json": json.dumps(C1_RECEIPT).encode(),
             "archaeon/campaign1/SFE-07/RECEIPT_attempt1.json": json.dumps(dict(C1_RECEIPT, purpose="a1")).encode()}
    ing = _ingest(monkeypatch, files, 1)
    ing.ingest_experiments()
    recs = {d["measured"]["purpose"]: d for d in ing.rows if d["kind"] == "receipt"}
    of_record, a1 = recs["of record"], recs["a1"]
    assert of_record["campaign_id"] == "cmp1" and of_record["harness_id"] == "SFE-07"
    assert of_record["attempt_id"] == "SFE-07/a02" and of_record["origin_kind"] == "reconstructed"   # T2: the pair
    assert a1["attempt_id"] == "SFE-07/a01" and a1["origin_kind"] == "reconstructed"
    assert of_record["design_id"] == "UNKNOWN" and of_record["engine_instance_id"] == "UNKNOWN"   # T3/T4
    assert of_record["foundry_profile"] == "UNKNOWN"
    assert of_record["world_id"] is None                                                            # no worlds{}: N/A


def test_c1_lone_receipt_is_attempt_one_reconstructed(monkeypatch):
    files = {"archaeon/campaign1/SFE-03/RECEIPT.json": json.dumps(C1_RECEIPT).encode()}
    ing = _ingest(monkeypatch, files, 1)
    ing.ingest_experiments()
    rec = [d for d in ing.rows if d["kind"] == "receipt"][0]
    assert rec["attempt_id"] == "SFE-03/a01" and rec["origin_kind"] == "reconstructed"


def test_rows_json_generation_series_and_series_digests(monkeypatch):
    rows = [{"arm": "fresh", "seed": 1, "engine": {"exp_id": "e", "obs_id": "o"},
             "gen0_provenance": {"campaign_seed": 20260920, "cell_seed": 1, "fill": "wse.gen0", "n": 200, "n_substituted": 0, "verified_common": True},
             "schedule": [{"gen": 0, "rung": 0, "p": 0.1, "best": 0.06, "mean": 0.006, "hold": True},
                          {"gen": 1, "rung": 0, "p": 0.1, "best": 0.0, "mean": 0.0, "hold": True}],
             "transitions": [84, 109], "wall_s": 3.2}]
    files = {"archaeon/campaign3/C3-SFE-03/rows.json": json.dumps(rows).encode(),
             "archaeon/campaign3/C3-SFE-03/ATTEMPTS.json": json.dumps({"experiment": "C3-SFE-03", "of_record": 5, "attempts": {"5": {}}}).encode()}
    ing = _ingest(monkeypatch, files, 3)
    ing.ingest_experiments()
    run = [d for d in ing.rows if d["kind"] == "run"][0]
    gens = [d for d in ing.rows if d["kind"] == "generation"]
    assert run["attempt_id"] == "C3-SFE-03/a05" and run["rng_identity"] == "20260920:1"
    assert "schedule" not in run["measured"] and run["measured"]["_series"]["schedule"]["n"] == 2
    assert run["measured"]["transitions"] == [84, 109]
    assert len(gens) == 2 and gens[1]["generation"] == 1 and gens[1]["strata"]["rung"] == 0
