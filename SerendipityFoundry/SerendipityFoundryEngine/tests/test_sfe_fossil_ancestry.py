"""Selection ancestry (deploy/fossil_ancestry.py) on the 2026-09-12 canary
specimen, offline: the PEW rows and the queue row are the specimen's real
values copied into a fake cursor, the SFE rows are written into a temp ledger,
and the committed corpus table is read from git at the preregistration commit
(35a41ce62) -- the same durable blob the live join reads.

Controls:
  positive  the canary resolves ANCESTRY_COMPLETE with the source fossil
            obs_d57501bd / exp_4a36b0ad / ENC-archaeon-f84f653c named
  uniform   a tick row that declares corpus rows 0 and a uniform policy
            resolves ANCESTRY_UNIFORM, not a gap
  cheat 1   a tampered fossil entry_hash -> GAP at fossil->sfe
  cheat 2   a queue row whose spec_hash differs -> GAP at queue->sfe
  cheat 3   a decision that names a region the preregistered rule would not
            pick -> GAP at rule->chosen_region
  cheat 4   a decision with no committed table/commit -> GAP at
            decision->corpus_table
  cheat 5   a fossil whose producer block carries no queue id -> GAP at
            fossil->queue
  no names  the join never consults world NAMES or timestamps for identity
            (asserted by feeding wrong names and shifted timestamps)
"""
from __future__ import annotations

import copy
import json
import os
import sqlite3
import subprocess
import sys

import pytest

_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ENGINE_ROOT, "deploy"))
import fossil_ancestry as fa  # noqa: E402

REPO = os.path.dirname(os.path.dirname(_ENGINE_ROOT))
COMMIT = "35a41ce62"
TABLE = "archaeon/docs/h0h5/_directable_landscapes_2026-09-12.json"
ENC = "ENC-archaeon-4f6625f91b2e304b"
SRC_ENC = "ENC-archaeon-f84f653c25247083"
EXP, WRK, OBS = "exp_8d968652a8a6b0c9885ec716", "wrk_0741fa4c800b927bb1322dd0", "obs_52ac5c2564a0deaf0d3ed303"
WORLD, REGION = "wld_13b3caf41573e37f015bf9ff", "wld_8e73e722b2b2d883d917b5c0"
QROW = "ececfe90-3e20-4dfe-b271-6a9d45d9abb2"
SPEC_HASH = "sha256:3caf3b11e0229257cd5f626bdb0afd9425c815896da7a8f2675bf497ef2e2174"
ENTRY = "sha256:6100e0201ec9ad745c4311a36ef18001ca31fc135bceb1bdaacac132ebb0617d"
SRC_OBS, SRC_EXP = "obs_d57501bd03d010e1c7c12797", "exp_4a36b0ad58fbc0e1de90a6d5"


def _git_available():
    r = subprocess.run(["git", "-C", REPO, "cat-file", "-e", "%s:%s" % (COMMIT, TABLE)], capture_output=True)
    return r.returncode == 0


pytestmark = pytest.mark.skipif(not _git_available(), reason="the preregistration commit is not in this clone")


def specimen():
    fossil = {"encounter_id": ENC, "run_id": "%s:%s" % (EXP, WRK), "sfe_world_id": WORLD, "sfe_event_seq": 129400,
              "sfe_entry_hash": ENTRY, "producer": {"queue": {"experiment_id": QROW, "request_key": "rk-canary-2026-09-12-1"}},
              "resources_used": {"obs_id": OBS, "work_id": WRK, "attempt_id": QROW}}
    src_fossil = {"encounter_id": SRC_ENC, "sfe_world_id": REGION, "run_id": "%s:wrk_13b05b568357cc6aae7083c6" % SRC_EXP}
    qrow = {"experiment_id": QROW, "sfe_experiment_id": EXP, "spec_hash": SPEC_HASH, "candidate_set_id": "cs-40a8239f45904b56",
            "family_id": "fam-canary-2026-09-12", "arm_id": "resample_best", "request_key": "rk-canary-2026-09-12-1",
            "source_reason": "human", "created_by": "archaeon",
            "source_evidence": {"schema": "archaeon.canary.v0", "mode": "human",
                                "corpus": {"rows": 1029, "corpus_hash": "corpus:9ff9b911920024b5f16349bb", "table": TABLE},
                                "chosen_region": REGION, "policy_version": "canary.region_directed_by_hand.v0",
                                "selection_rule": "highest metric; tie -> earliest created_ts",
                                "preregistration": "archaeon/docs/h0h5/CANARY_PREREG_2026-09-12.json (commit %s)" % COMMIT}}
    return fossil, src_fossil, qrow


class FakeCur:
    def __init__(self, fossils, qrows):
        self.fossils, self.qrows, self._r = fossils, qrows, None

    def execute(self, sql, args=()):
        if "fossil_encounters" in sql:
            self._r = self.fossils.get(args[0])
        elif "research_experiment_queue" in sql:
            self._r = self.qrows.get(args[0])
        else:
            raise AssertionError("unexpected query: " + sql)

    def fetchone(self):
        return self._r


def ledger(tmp_path, *, entry_hash=ENTRY, spec_enc=ENC, src_world=REGION):
    db = str(tmp_path / "anc.db")
    c = sqlite3.connect(db)
    c.executescript("""
    CREATE TABLE experiments(exp_id TEXT PRIMARY KEY, world_id TEXT, spec TEXT, spec_hash TEXT, work_id TEXT);
    CREATE TABLE observations(obs_id TEXT PRIMARY KEY, exp_id TEXT, work_id TEXT, world_id TEXT, outcome TEXT, evidence_class TEXT);
    CREATE TABLE events(event_seq INTEGER PRIMARY KEY, entry_hash TEXT, event_type TEXT, world_id TEXT);
    """)
    c.execute("INSERT INTO experiments VALUES (?,?,?,?,?)", (EXP, WORLD, json.dumps({"pew": {"encounter_id": spec_enc}}), SPEC_HASH, WRK))
    c.execute("INSERT INTO observations VALUES (?,?,?,?,?,?)", (OBS, EXP, WRK, WORLD, "SURVIVED", "ENGINE_WORK_RESULT"))
    c.execute("INSERT INTO observations VALUES (?,?,?,?,?,?)", (SRC_OBS, SRC_EXP, "wrk_13b05b568357cc6aae7083c6", src_world, "SURVIVED", "ENGINE_WORK_RESULT"))
    c.execute("INSERT INTO events VALUES (?,?,?,?)", (129400, entry_hash, "OBSERVATION_RECORDED", WORLD))
    c.commit()
    c.close()
    return db


def test_positive_canary_is_ancestry_complete(tmp_path):
    fossil, src, q = specimen()
    ch = fa.trace(ENC, db=ledger(tmp_path), cur=FakeCur({ENC: fossil, SRC_ENC: src}, {QROW: q}))
    assert ch["verdict"] == "ANCESTRY_COMPLETE"
    sf = [e for e in ch["edges"] if e["edge"] == "source_fossil"][0]
    assert (sf["obs_id"], sf["exp_id"], sf["pew"], sf["region"]) == (SRC_OBS, SRC_EXP, SRC_ENC, REGION)
    assert sf["rule_reproduced"] is True and sf["commit"] == COMMIT
    assert [e for e in ch["edges"] if e["edge"] == "sfe"][0]["entry_hash_verified"] is True


def test_uniform_draw_is_not_a_gap(tmp_path):
    fossil, src, q = specimen()
    q = copy.deepcopy(q)
    q["source_evidence"] = {"schema": "archaeon.tick.v0", "mode": "exploration",
                            "corpus": {"rows": 0, "corpus_hash": "corpus:e3b0c44298fc1c149afbf4c8"},
                            "policy": {"name": "menu.uniform.v0", "template_content_hash": "sha256:2eec"}}
    ch = fa.trace(ENC, db=ledger(tmp_path), cur=FakeCur({ENC: fossil}, {QROW: q}))
    assert ch["verdict"] == "ANCESTRY_UNIFORM"


def test_cheat_tampered_entry_hash_is_a_gap(tmp_path):
    fossil, src, q = specimen()
    with pytest.raises(fa.Gap) as g:
        fa.trace(ENC, db=ledger(tmp_path, entry_hash="sha256:0000"), cur=FakeCur({ENC: fossil, SRC_ENC: src}, {QROW: q}))
    assert g.value.edge == "fossil->sfe"


def test_cheat_spec_hash_mismatch_is_a_gap(tmp_path):
    fossil, src, q = specimen()
    q = dict(q, spec_hash="sha256:ffff")
    with pytest.raises(fa.Gap) as g:
        fa.trace(ENC, db=ledger(tmp_path), cur=FakeCur({ENC: fossil, SRC_ENC: src}, {QROW: q}))
    assert g.value.edge == "queue->sfe"


def test_cheat_region_the_rule_would_not_pick_is_a_gap(tmp_path):
    fossil, src, q = specimen()
    rows = json.loads(fa.git_show(COMMIT, TABLE))
    other = [r["region"] for r in rows if r["region"] != REGION][0]
    q = copy.deepcopy(q)
    q["source_evidence"]["chosen_region"] = other
    src2 = dict(src, sfe_world_id=other)
    with pytest.raises(fa.Gap) as g:
        fa.trace(ENC, db=ledger(tmp_path, src_world=other), cur=FakeCur({ENC: fossil, SRC_ENC: src2}, {QROW: q}))
    assert g.value.edge == "rule->chosen_region"


def test_cheat_no_committed_table_is_a_gap(tmp_path):
    fossil, src, q = specimen()
    q = copy.deepcopy(q)
    q["source_evidence"]["preregistration"] = "somewhere, uncommitted"
    with pytest.raises(fa.Gap) as g:
        fa.trace(ENC, db=ledger(tmp_path), cur=FakeCur({ENC: fossil, SRC_ENC: src}, {QROW: q}))
    assert g.value.edge == "decision->corpus_table"


def test_cheat_fossil_without_queue_id_is_a_gap(tmp_path):
    fossil, src, q = specimen()
    fossil = dict(fossil, producer={"queue": {}})
    with pytest.raises(fa.Gap) as g:
        fa.trace(ENC, db=ledger(tmp_path), cur=FakeCur({ENC: fossil, SRC_ENC: src}, {QROW: q}))
    assert g.value.edge == "fossil->queue"


def test_identity_never_rests_on_names_or_timestamps(tmp_path):
    """Feed wrong world names and shifted timestamps everywhere a record has
    them; the join must still resolve, because it never reads them."""
    fossil, src, q = specimen()
    fossil = dict(fossil, created_at="1999-01-01", occurred_ts=0)
    q = copy.deepcopy(q)
    q["created_at"] = "1999-01-01"
    q["source_evidence"]["region_ctx"] = {"world_id": "wld_WRONG", "world": "not-the-name"}
    ch = fa.trace(ENC, db=ledger(tmp_path), cur=FakeCur({ENC: fossil, SRC_ENC: src}, {QROW: q}))
    assert ch["verdict"] == "ANCESTRY_COMPLETE"
