"""Forensic integrity of the receipt file itself (overnight C10): truncation, corruption and edits must be
DETECTED and COUNTED, never silently dropped; a strict read refuses, a scan reports."""
from __future__ import annotations

import json

import pytest

from prometheus.toolbox import receipt as R
from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.backends.local import execute, lower

REG = default_registry()


def _write(tmp_path, n_seeds=3):
    e = Experiment(family="integ", world=ref("world.integer.v1", world_seed=1), substrate=ref("substrate.flat.v1"), players=[random_statemachine(1).manifest()],
                   seed_policy={"base": 1, "n_seeds": n_seeds}, budget={"episodes": 1, "horizon": 8})
    execute(lower(e, REG).job, tmp_path / "r.jsonl", REG)
    return tmp_path / "r.jsonl"


def test_truncated_last_line_is_reported_not_dropped(tmp_path):
    p = _write(tmp_path); raw = p.read_bytes()
    p.write_bytes(raw[:-40])                                   # mid-record truncation (a crash during the last flush)
    with pytest.raises(R.ReceiptError):
        R.read_all(p)
    scan = R.scan(p)
    assert scan["valid"] == 3 and scan["defects"] == [{"line": 4, "defect": "TRUNCATED_OR_MALFORMED_JSON"}]


def test_edited_record_in_the_middle_is_named_by_line(tmp_path):
    p = _write(tmp_path); lines = p.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[1]); rec["seed"] = 999; lines[1] = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    scan = R.scan(p)
    assert scan["valid"] == 3 and scan["defects"][0]["line"] == 2 and scan["defects"][0]["defect"].startswith("RECEIPT_ID_MISMATCH")


def test_duplicate_receipt_ids_are_reported(tmp_path):
    p = _write(tmp_path); lines = p.read_text(encoding="utf-8").splitlines()
    p.write_text("\n".join(lines + [lines[0]]) + "\n", encoding="utf-8")
    scan = R.scan(p)
    assert any(d["defect"] == "DUPLICATE_RECEIPT_ID" for d in scan["defects"]) and scan["valid"] == 4


def test_scan_of_a_clean_file_has_no_defects(tmp_path):
    p = _write(tmp_path)
    assert R.scan(p) == {"path": str(p), "lines": 4, "valid": 4, "defects": [], "receipt_ids": R.scan(p)["receipt_ids"]}


# C22 (playtest C re-run): execute() APPENDED a second run to an existing receipts file, so a reader saw two
# executions interleaved as one and I analysed stale rows as fresh ones. A receipts path is one execution
# unless the caller says otherwise.
def test_execute_refuses_to_append_to_an_existing_receipts_file_unless_asked(tmp_path):
    p = _write(tmp_path)
    e = Experiment(family="integ", world=ref("world.integer.v1", world_seed=1), substrate=ref("substrate.flat.v1"), players=[random_statemachine(1).manifest()],
                   seed_policy={"base": 1, "n_seeds": 1}, budget={"episodes": 1, "horizon": 8})
    with pytest.raises(FileExistsError):
        execute(lower(e, REG).job, p, REG)
    assert R.scan(p)["valid"] == 4                              # untouched
    execute(lower(e, REG).job, p, REG, append=True)
    assert R.scan(p)["valid"] == 6 and R.scan(p)["defects"] == []


# C29: "one experiment implies one uninterrupted computation" is not assumed: a job interrupted after k runs
# resumes into the same receipts file, skips the runs already on disk, and ends with the same scientific record
# (trace hashes, objectives, control outcomes) as an uninterrupted job.
def test_interrupted_job_resumes_from_the_receipts_file(tmp_path, monkeypatch):
    from prometheus.toolbox.backends import local as L
    e = Experiment(family="resume", world=ref("world.integer.v1", world_seed=2), substrate=ref("substrate.flat.v1"), players=[random_statemachine(2).manifest()],
                   seed_policy={"base": 1, "n_seeds": 3}, budget={"episodes": 1, "horizon": 8}, controls=[ref("control.replay.v1"), ref("control.cheat.v1")],
                   objective=ref("objective.survival.v1"), sweep={"world.params.world_seed": [2, 3]})
    job = lower(e, REG).job; assert len(job.runs) == 18
    calls = {"n": 0}; real = L.run_one

    def flaky(spec, registry, receipt_dir=None):
        calls["n"] += 1
        if calls["n"] == 7:
            raise KeyboardInterrupt("simulated interruption")
        return real(spec, registry, receipt_dir)
    monkeypatch.setattr(L, "run_one", flaky)
    with pytest.raises(KeyboardInterrupt):
        execute(job, tmp_path / "j.jsonl", REG)
    assert R.scan(tmp_path / "j.jsonl")["valid"] == 6
    monkeypatch.setattr(L, "run_one", real)
    rep = execute(job, tmp_path / "j.jsonl", REG, resume=True)
    assert rep.n_runs == 18 and rep.resumed_runs == 6 and rep.n_failed == 0
    rs = R.read_all(tmp_path / "j.jsonl"); assert len(rs) == 19 and R.scan(tmp_path / "j.jsonl")["defects"] == []
    clean = execute(lower(e, REG).job, tmp_path / "clean.jsonl", REG)
    key = lambda r: (r["arm"], json.dumps(r["sweep_point"], sort_keys=True), r["seed"])
    a = {key(r): (r["trace_hashes"], r["science"].get("objective", {}).get("value")) for r in rs if r["arm"] not in ("SUMMARY",)}
    b = {key(r): (r["trace_hashes"], r["science"].get("objective", {}).get("value")) for r in R.read_all(tmp_path / "clean.jsonl") if r["arm"] != "SUMMARY"}
    assert a == b and rep.controls == clean.controls
