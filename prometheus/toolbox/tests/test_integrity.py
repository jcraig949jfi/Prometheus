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


# C30: an IR must be pure data -- a lambda, a set or a NaN smuggled into params is a validation defect, not a
# later crash inside a receipt writer.
def test_ir_refuses_values_that_cannot_be_recorded():
    e = Experiment(family="ser", world=ref("world.integer.v1", world_seed=1, hook=lambda x: x), substrate=ref("substrate.flat.v1"), players=[random_statemachine(1).manifest()])
    assert any("serialisable" in d for d in e.validate())
    e2 = Experiment(family="ser", world=ref("world.integer.v1", world_seed=float("nan")), substrate=ref("substrate.flat.v1"), players=[random_statemachine(1).manifest()])
    assert any("serialisable" in d for d in e2.validate())


# C32: the SUMMARY receipt carries the full IR, so a receipts file ALONE can be replayed; replay reports
# per-run divergences as data (never an exception) and the kernel hash difference as information.
def test_receipts_file_alone_replays_and_divergence_is_reported_not_raised(tmp_path):
    p = _write(tmp_path, n_seeds=2)
    from prometheus.toolbox.backends.local import replay_file
    rep = replay_file(p, tmp_path / "replay.jsonl", REG)
    assert rep["runs_compared"] == 2 and rep["divergent"] == [] and rep["kernel_hash_equal"] is True
    # perturb the recorded world semantics through the IR embedded in the summary: replay must DIVERGE, not raise
    import json as J
    lines = p.read_text(encoding="utf-8").splitlines()
    summ = J.loads(lines[-1]); summ["experiment"]["world"]["params"]["world_seed"] = 99
    from prometheus.toolbox.receipt import receipt_id
    summ["receipt_id"] = receipt_id(summ); lines[-1] = J.dumps(summ, sort_keys=True, separators=(",", ":"))
    p2 = tmp_path / "tampered.jsonl"; p2.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rep2 = replay_file(p2, tmp_path / "replay2.jsonl", REG)
    assert rep2["runs_compared"] == 2 and len(rep2["divergent"]) == 2 and rep2["divergent"][0]["field"] == "trace_hashes"


# C37 (directive s8: one episode != one uninterrupted computation): an episode can be CHECKPOINTED at a tick
# (world + every player instance + observers that can snapshot) and RESUMED, in a fresh set of objects, to the
# same observations and actions as the uninterrupted run. The resumed trace hash is honestly PARTIAL (a hash
# cannot be resumed from a digest), so the checkpoint carries the pre-checkpoint hash and the record says so.
def test_episode_checkpoint_and_resume_reproduce_the_uninterrupted_run():
    from prometheus.toolbox.backends.local import run_episode, resume_episode, build_world
    from prometheus.toolbox.ref.players import random_statemachine_v2
    e = Experiment(family="ckpt", world=ref("world.integer.v1", world_seed=4, start_charge=100000, step_cost=0), substrate=ref("substrate.kv.v1", scope="lifetime"),
                   players=[random_statemachine_v2(3).manifest()], budget={"episodes": 1, "horizon": 24})
    def fresh():
        w = build_world(e, REG); sub = REG.make("substrate.kv.v1", scope="lifetime")
        inst = {0: sub.instantiate(random_statemachine_v2(3), 1)}
        return w, sub, inst, [REG.make("observer.trace.v1"), REG.make("observer.series.v1")]
    w, sub, inst, obs = fresh()
    full = run_episode(w, inst, obs, seed=7, horizon=24, substrate=sub, record_actions=True)
    w2, sub2, inst2, obs2 = fresh()
    first = run_episode(w2, inst2, obs2, seed=7, horizon=24, substrate=sub2, checkpoint_at=10, record_actions=True)
    assert first["checkpoint"] is not None and first["ticks"] == 10
    w3, sub3, inst3, obs3 = fresh()                                                   # fresh objects: nothing shared with w2
    rest = resume_episode(first["checkpoint"], w3, inst3, obs3, horizon=24, substrate=sub3, record_actions=True)
    assert first["actions"] + rest["actions"] == full["actions"]
    assert rest["replay_class"] == "PARTIAL" and rest["checkpoint_tick"] == 10 and rest["pre_checkpoint_trace"] == first["trace_hash"]
    assert obs3[1].series_episode() == obs[1].series_episode() and len(obs3[1].series_episode()) == 24   # the whole episode's series survives the checkpoint
    assert obs3[0].measure() == obs[0].measure()


# C44: scan() caught edits, duplicates and truncation -- but DELETING a whole middle line left a file every check
# accepted. Receipts in one file now chain (prev_receipt_id); a missing link is a named defect; a resumed job
# continues the chain from the last valid receipt.
def test_deleting_a_middle_receipt_breaks_the_chain_and_is_reported(tmp_path):
    p = _write(tmp_path); lines = p.read_text(encoding="utf-8").splitlines()
    rs = R.read_all(p)
    assert rs[0]["prev_receipt_id"] is None and all(rs[i]["prev_receipt_id"] == rs[i - 1]["receipt_id"] for i in range(1, len(rs)))
    del lines[1]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    scan = R.scan(p)
    assert scan["valid"] == 3 and any(d["defect"] == "CHAIN_BREAK" and d["line"] == 2 for d in scan["defects"])
    with pytest.raises(R.ReceiptError):
        R.read_all(p)


def test_resumed_job_continues_the_chain(tmp_path, monkeypatch):
    from prometheus.toolbox.backends import local as L
    e = Experiment(family="chain", world=ref("world.integer.v1", world_seed=1), substrate=ref("substrate.flat.v1"), players=[random_statemachine(1).manifest()],
                   seed_policy={"base": 1, "n_seeds": 4}, budget={"episodes": 1, "horizon": 4})
    job = lower(e, REG).job; real = L.run_one; calls = {"n": 0}

    def flaky(spec, registry, receipt_dir=None):
        calls["n"] += 1
        if calls["n"] == 3:
            raise KeyboardInterrupt()
        return real(spec, registry, receipt_dir)
    monkeypatch.setattr(L, "run_one", flaky)
    with pytest.raises(KeyboardInterrupt):
        execute(job, tmp_path / "c.jsonl", REG)
    monkeypatch.setattr(L, "run_one", real)
    execute(job, tmp_path / "c.jsonl", REG, resume=True)
    assert R.scan(tmp_path / "c.jsonl")["defects"] == [] and len(R.read_all(tmp_path / "c.jsonl")) == 5
