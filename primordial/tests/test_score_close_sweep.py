"""H-R6-2 (D10): a rows file committed in the round window without a guarded receipt -> UNRECEIPTED_OBSERVATION."""
from __future__ import annotations

import json
import os
import subprocess

import pytest

from primordial.score import close_sweep as CS

ROWS = "primordial/ledger/rows"


def _commit(repo, path, ts):
    f = repo / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f.read_text(encoding="utf-8") + "x\n" if f.exists() else '{"ts": 1}\n', encoding="utf-8")
    env = {**os.environ, "GIT_COMMITTER_DATE": f"@{int(ts)} +0000", "GIT_AUTHOR_DATE": f"@{int(ts)} +0000"}
    subprocess.run(["git", "-C", str(repo), "add", path], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", f"rows {path}"], check=True, env=env)
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for k, v in (("user.email", "h@test"), ("user.name", "h")):
        subprocess.run(["git", "-C", str(tmp_path), "config", k, v], check=True)
    _commit(tmp_path, f"{ROWS}/B/old-round.jsonl", 500)                       # before the window
    _commit(tmp_path, f"{ROWS}/B/B-R6-cand.jsonl", 1100)                      # guarded receipt cites it
    _commit(tmp_path, f"{ROWS}/E/E-R6-gpu.jsonl", 1200)                       # cited by an UNGUARDED receipt only
    planted = _commit(tmp_path, f"{ROWS}/H/H-R6-planted.jsonl", 1300)          # planted: nobody cites it
    _commit(tmp_path, f"{ROWS}/B/B-R6-cand.jsonl", 1400)                      # a second commit to a cited file
    _commit(tmp_path, "primordial/ledger/qd/draws.jsonl", 1500)               # not a rows file
    _commit(tmp_path, f"{ROWS}/C/after.jsonl", 9000)                          # after the window
    return tmp_path, planted


RECEIPTS = [
    {"exp_id": "B-R6-cand", "campaign_stage": "PRODUCTION", "rows": f"{ROWS}/B/B-R6-cand.jsonl", "ts": 1450},
    {"exp_id": "E-R6-gpu", "rows": f"{ROWS}/E/E-R6-gpu.jsonl", "ts": 1250},          # no campaign_stage: not guarded
]


def test_the_sweep_takes_a_round_id_and_reads_that_rounds_clock(repo, tmp_path):
    root, planted = repo
    clocks = {"r7": {"start_ts": 1000.0, "end_ts": 2000.0}, "r6": {"start_ts": 1250.0, "end_ts": 1350.0}}
    reader = lambda r, rid: clocks.get(rid)
    (tmp_path / "ledger").mkdir()
    (tmp_path / "ledger" / "B.jsonl").write_text(json.dumps(RECEIPTS[0]) + "\n", encoding="utf-8")
    r7 = CS.sweep_round(None, "r7", repo=root, ledger_dir=tmp_path / "ledger", reader=reader)
    assert r7["round"] == "r7" and r7["window"] == [1000.0, 2000.0]
    assert [u["path"] for u in r7["unreceipted"]] == [f"{ROWS}/E/E-R6-gpu.jsonl", f"{ROWS}/H/H-R6-planted.jsonl"]
    r6 = CS.sweep_round(None, "r6", repo=root, ledger_dir=tmp_path / "ledger", reader=reader)
    assert r6["rows_files"] == [f"{ROWS}/H/H-R6-planted.jsonl"]                 # only its own window
    assert CS.sweep_round(None, "r9", repo=root, reader=reader) is None


def test_planted_unreceipted_rows_are_named(repo):
    root, planted = repo
    out = CS.sweep(root, start=1000, end=2000, receipts=RECEIPTS)
    assert out["rows_files"] == [f"{ROWS}/B/B-R6-cand.jsonl", f"{ROWS}/E/E-R6-gpu.jsonl", f"{ROWS}/H/H-R6-planted.jsonl"]
    assert out["cited"] == {f"{ROWS}/B/B-R6-cand.jsonl": ["B-R6-cand"]}
    assert [u["path"] for u in out["unreceipted"]] == [f"{ROWS}/E/E-R6-gpu.jsonl", f"{ROWS}/H/H-R6-planted.jsonl"]
    assert out["unreceipted"][1]["commits"] == [planted]


def test_a_guarded_receipt_citing_every_file_clears_the_sweep(repo):
    root, _ = repo
    receipts = RECEIPTS + [{"exp_id": "E-R6-gpu", "campaign_stage": "PILOT", "rows": f"see {ROWS}/E/E-R6-gpu.jsonl",
                            "ts": 1600},
                           {"exp_id": "H-R6-x", "campaign_stage": "SMOKE",
                            "rows": [f"{ROWS}/H/H-R6-planted.jsonl"], "ts": 1700}]
    assert CS.sweep(root, start=1000, end=2000, receipts=receipts)["unreceipted"] == []


def test_guarded_receipts_are_read_from_the_ledger_mirror(tmp_path):
    (tmp_path / "B.jsonl").write_text("\n".join([json.dumps(RECEIPTS[0]), json.dumps(RECEIPTS[1]), "not json",
                                                 json.dumps({**RECEIPTS[0], "exp_id": "B-old", "ts": 10})]) + "\n",
                                      encoding="utf-8")
    got = CS.guarded_receipts(tmp_path, since=1000)
    assert [r["exp_id"] for r in got] == ["B-R6-cand"]


def test_emit_posts_one_event_per_path_once(repo):
    root, _ = repo

    class R:
        def __init__(self):
            self.keys, self.x = set(), []

        def set(self, k, v, nx=False):
            if nx and k in self.keys:
                return None
            self.keys.add(k)
            return True

        def xadd(self, key, fields):
            self.x.append((key, fields))
            return f"{len(self.x)}-0"

    r = R()
    out = CS.sweep(root, start=1000, end=2000, receipts=RECEIPTS)
    assert CS.emit(r, out, "r6") == [f"{ROWS}/E/E-R6-gpu.jsonl", f"{ROWS}/H/H-R6-planted.jsonl"]
    assert CS.emit(r, out, "r6") == []                                          # idempotent per (round, path)
    key, fields = r.x[1]
    assert key == "pm:events" and fields["event"] == "UNRECEIPTED_OBSERVATION"
    assert json.loads(fields["json"])["path"] == f"{ROWS}/H/H-R6-planted.jsonl"
