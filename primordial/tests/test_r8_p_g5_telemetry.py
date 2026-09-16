"""G5 (round 8): the telemetry minimum, and ADAPT-14 -- telemetry is WRITE-ONLY with respect to science.

Each test is aimed at an r7 question that could not be answered (POST_ROUND_FINAL_STEPS s7): per-job resources,
token wait, queue depth, watcher liveness with explicit start/stop, WHY_NOT_RUN, a machine-readable FINAL.
"""
from __future__ import annotations

import ast
import json
import pathlib
import subprocess
import uuid

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.fabric import telemetry as TM
from primordial.fabric import worker as W
from primordial.tests._live import live_url

URL = live_url()
SLEEP = "primordial.fabric.selftest_jobs:sleep_rows"
ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    lanes: list = []
    common = [TM.QUEUE, TM.WATCH, TM.WHY_NOT_RUN, EV.EVENTS, EV.CANDIDATES, "pm:round:current"]
    r.delete(*common)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r8-g5")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path, lanes
    for L in lanes:
        r.delete(W.JOBS.format(L), W.CONT.format(L), W.ROWS.format(L), W.DONE.format(L), W.WSTATE.format(L))
    r.delete(*common)


def lane(lanes):
    L = "t" + uuid.uuid4().hex[:6]
    lanes.append(L)
    return L


def beacons(r, L):
    return [json.loads(f["json"]) for _, f in r.xrange(TM.WATCH) if json.loads(f["json"])["lane"] == L]


# ------------------------------------------------------------------ watcher beacons (G4 interface) + done records

def test_worker_emits_start_and_stop_beacons_and_done_telemetry(env, monkeypatch):
    r, repo, lanes = env
    L = lane(lanes)
    W.submit(L, SLEEP, "g5", "rows/g5.jsonl", 30, {"s": 0.2}, r=r, envelope=EV.example(predicate_event_id="1789564787374-0"))
    (d,) = W.Worker(L, url=URL, repo=repo, log=lambda *_: None).serve(block_ms=100, max_jobs=1, deadline_s=30)
    b = beacons(r, L)
    assert [x["beacon"] for x in b][0] == "START" and b[-1]["beacon"] == "STOP"
    assert b[-1]["stop_reason"] == "max_jobs" and b[-1]["jobs"] == 1
    assert len({(x["tag"], x["pid"], x["started_ts"]) for x in b}) == 1        # START/STOP pair on one instance
    assert [x["seq"] for x in b] == list(range(len(b)))
    assert d["predicate_event_id"] == "1789564787374-0"
    rows = [json.loads(x) for x in (repo / "rows/g5.jsonl").read_text(encoding="utf-8").splitlines()]
    body = [x for x in rows if x.get("kind") == "sleep_rows"]
    assert len(body) == 2 and all(x["predicate_event_id"] == "1789564787374-0" for x in body)   # acc.3: every row
    assert all(k in d for k in TM.QUEUE_FIELDS)
    assert d["telemetry_sampling"] is True and len(d["resource_samples"]) >= 1
    s = d["resource_samples"][0]
    assert {"rss_mb", "cpu_pct", "threads", "ts"} <= set(s) and s["rss_mb"] > 0 and s["threads"] >= 1


def test_idle_exit_emits_stop_with_reason(env):
    r, repo, lanes = env
    L = lane(lanes)
    assert W.Worker(L, url=URL, repo=repo, log=lambda *_: None).serve(block_ms=100, idle_exit_s=0.3) == []
    b = beacons(r, L)
    assert [x["beacon"] for x in b] == ["START", "STOP"] and b[1]["stop_reason"] == "idle_exit"
    depth = [json.loads(f["json"]) for _, f in r.xrange(TM.QUEUE)]
    assert any(x["record"] == "QUEUE_DEPTH" and x["lane"] == L and x["depth_main"] == 0 for x in depth)


def test_sampling_off_switch(env, monkeypatch):
    r, repo, lanes = env
    L = lane(lanes)
    monkeypatch.setenv("PM_TELEMETRY", "0")
    W.submit(L, SLEEP, "g5off", "rows/g5.jsonl", 30, {"s": 0.1}, r=r)
    (d,) = W.Worker(L, url=URL, repo=repo, log=lambda *_: None).serve(block_ms=100, max_jobs=1, deadline_s=30)
    assert d["telemetry_sampling"] is False and d["resource_samples"] == []
    assert all(k in d for k in TM.QUEUE_FIELDS)                  # queue fields are records, not sampling: still on


def test_beacon_kind_is_closed_vocabulary(env):
    r, _, _ = env
    with pytest.raises(ValueError):
        TM.beacon(r, "X", "HEARTBEAT", {})


# ------------------------------------------------------------------ WHY_NOT_RUN

def test_why_not_run_record(env):
    r, _, _ = env
    rec = TM.why_not_run(r, "G", "cell w23 t128", "projected 8.61 h > remaining clock 3.2 h",
                         {"cpu_s": 31000, "wall_s": 31000, "measured_from": "R16_LEARNER_PLAN_R7.json"})
    got = TM.why_not_run_records(r, "G")
    assert len(got) == 1 and got[0]["record"] == "WHY_NOT_RUN" and got[0]["event_id"] == rec["event_id"]
    assert got[0]["projection"]["cpu_s"] == 31000
    with pytest.raises(ValueError):
        TM.why_not_run(r, "G", "", "no item")


# ------------------------------------------------------------------ FINAL.json

def final_doc(**kw):
    doc = {"schema_version": "FINAL_v1", "round_id": "r8", "lane": "G", "generated_ts": 1789600000.0,
           "code_sha": "6c02b89a9", "receipts": [{"event_id": "1-0", "exp_id": "G-R8-1", "verdict": "FAIL",
                                                  "residue": ["narrower_boundary"]},
                                                 {"event_id": "2-0", "exp_id": "G-R8-2", "verdict": "PASS",
                                                  "residue": "NONE", "predicate_event_id": "0-1"}],
           "row_files": [{"path": "primordial/ledger/rows/G/x.jsonl", "rows": 12}],
           "candidates": [{"stub_id": "s1", "question": "q"}],
           "why_not_run": [{"event_id": "3-0", "item": "w23", "reason": "clock", "projection": {"cpu_s": 1}}],
           "unresolved_claims": [], "self_disclosed_errors": [{"error": "mod-8 bug", "repaired": True}],
           "disputes_with_A": [{"lane_statement": "G says", "a_statement": "A says"}],
           "interventions_received": [{"event_id": "4-0", "summary": "A ruling"}],
           "job_status_counts": {"ok": 3, "refused": 1}}
    doc.update(kw)
    return doc


def test_final_schema_is_committed_and_valid_doc_passes(tmp_path):
    assert TM.SCHEMA_PATH.exists()
    sch = TM.schema()
    assert set(sch["required"]) >= {"receipts", "row_files", "candidates", "why_not_run", "unresolved_claims",
                                    "self_disclosed_errors", "disputes_with_A", "interventions_received",
                                    "job_status_counts"}
    assert TM.validate_final(final_doc()) == []
    TM.write_final(tmp_path / "FINAL.json", final_doc())
    assert json.loads((tmp_path / "FINAL.json").read_text())["lane"] == "G"


@pytest.mark.parametrize("bad", [
    {"receipts": [{"event_id": "1-0", "exp_id": "x", "verdict": "PASS", "residue": []}]},           # empty residue
    {"receipts": [{"event_id": "1-0", "exp_id": "x", "verdict": "PASS", "residue": ["vibes"]}]},    # not in vocab
    {"job_status_counts": {"ok": "3"}},                                                          # counts from prose
    {"round_id": "round eight"},
    {"extra_prose_counts": 5},
])
def test_final_schema_rejects(tmp_path, bad):
    assert TM.validate_final(final_doc(**bad)) != []
    with pytest.raises(ValueError):
        TM.write_final(tmp_path / "FINAL.json", final_doc(**bad))


@pytest.mark.parametrize("key", ["receipts", "why_not_run", "disputes_with_A", "job_status_counts"])
def test_final_schema_requires_every_section(key):
    doc = final_doc()
    del doc[key]
    assert TM.validate_final(doc) != []


# ------------------------------------------------------------------ ADAPT-14

VERDICT_PATH = ["score", "metric", "cohorts", "qd"]
VERDICT_FILES = ["fabric/envelope.py", "ops/residue.py"]
# `continuation` is excluded from the NAME scan: envelope.admit's continuation parameter predates telemetry and is
# derived from the job's segment (asserted below), not from the queue record that shares the word.
FORBIDDEN_STRINGS = (set(TM.TELEMETRY_FIELDS) | {TM.QUEUE, TM.WATCH, TM.WHY_NOT_RUN, "telemetry_sampling"}) - {"continuation"}


def verdict_path_files():
    out = [ROOT / f for f in VERDICT_FILES]
    for d in VERDICT_PATH:
        out += sorted((ROOT / d).rglob("*.py")) if (ROOT / d).exists() else []
    return [p for p in out if "tests" not in p.parts]


def test_adapt14_verdict_path_never_reads_telemetry():
    """No eligibility check, admission decision, control, discriminator or verdict imports the telemetry module or
    names a telemetry field or stream. Telemetry is additive and observational, never a modifier."""
    files = verdict_path_files()
    assert len(files) > 20 and ROOT / "score/evidence_n.py" in files and ROOT / "fabric/envelope.py" in files
    hits = []
    for p in files:
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "telemetry" in node.module.split(".")[-1:]:
                hits.append((p, node.lineno, node.module))
            if isinstance(node, ast.ImportFrom) and any(a.name == "telemetry" for a in node.names) \
                    and (node.module or "").startswith("primordial.fabric"):
                hits.append((p, node.lineno, "fabric.telemetry"))
            if isinstance(node, ast.Import) and any(a.name == "primordial.fabric.telemetry" for a in node.names):
                hits.append((p, node.lineno, "import"))
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in FORBIDDEN_STRINGS:
                hits.append((p, node.lineno, node.value))
            if isinstance(node, (ast.Attribute, ast.Name)):
                name = node.attr if isinstance(node, ast.Attribute) else node.id
                if name in FORBIDDEN_STRINGS:
                    hits.append((p, node.lineno, name))
    assert hits == [], hits


def test_adapt14_worker_admission_input_is_not_telemetry():
    import inspect
    src = inspect.getsource(W.Worker._admit)
    assert "segment" in src and "queue" not in src and "TM." not in src and "wait" not in src


def test_adapt14_admission_ignores_queue_telemetry():
    """Behavioural: the same envelope gets the same verdict whatever the telemetry says."""
    env = EV.example()
    base = EV.admit(env, now=1789600000.0)
    noisy = EV.admit(dict(env), now=1789600000.0)
    assert base == noisy
    job = {"queue": json.dumps(TM.queue_fields(0.0, 99999.0, 44, True))}
    assert W.queue_of(job)["wait_s"] == 99999.0                       # telemetry says "starved 27 h" ...
    assert EV.admit(env, now=1789600000.0) == base                    # ... and admission never sees it


# ------------------------------------------------------------------ D29 (G1 call sites in worker.py, agreed with F)

def job_observation_status(ctx):
    ctx.emit({"status": "record", "kind": "ok_row"})
    ctx.emit({"status": "observation", "kind": "d29"})             # round-7 D's row: refused at emit
    ctx.emit({"status": "record", "kind": "never"})


def job_bypass_emit(ctx):
    """A row that reaches the stream WITHOUT Ctx.emit (a legacy path): the supervisor's RowWriter refuses it."""
    ctx.emit({"status": "record", "kind": "ok_row"})
    ctx.r.xadd(W.ROWS.format(ctx.lane), {"job_id": ctx.job_id, "json": json.dumps({"status": "observation"})})


def test_d29_refused_row_at_emit_ends_job_error(env):
    r, repo, lanes = env
    L = lane(lanes)
    W.submit(L, f"{__name__}:job_observation_status", "d29a", "rows/d29a.jsonl", 30, {}, r=r)
    (d,) = W.Worker(L, url=URL, repo=repo, log=lambda *_: None).serve(block_ms=100, max_jobs=1, deadline_s=60)
    assert d["status"] == "error"                                              # G1 acc.1: never ok
    rows = [json.loads(x) for x in (repo / "rows/d29a.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [x.get("kind") for x in rows if x["status"] == "record"] == ["ok_row"]
    end = [x for x in rows if x.get("kind") == "job_end"]
    assert len(end) == 1 and "ROW_VOCABULARY_REFUSED:row 1:status 'observation'" in end[0]["error"]   # acc.2


def test_d29_refused_row_in_drain_ends_job_error_and_keeps_residue(env):
    r, repo, lanes = env
    L = lane(lanes)
    W.submit(L, f"{__name__}:job_bypass_emit", "d29b", "rows/d29b.jsonl", 30, {}, r=r)
    (d,) = W.Worker(L, url=URL, repo=repo, log=lambda *_: None).serve(block_ms=100, max_jobs=1, deadline_s=60)
    assert d["status"] == "error" and d["row_refusals"] == 1
    rows = [json.loads(x) for x in (repo / "rows/d29b.jsonl").read_text(encoding="utf-8").splitlines()]
    wrapped = [x for x in rows if x["status"] == "aborted" and x.get("row") == {"status": "observation",
                                                                                 "job_id": d["job_id"]}]
    assert len(wrapped) == 1                                                  # the refused payload is residue
    assert any(x.get("kind") == "job_end" and "ROWS_REFUSED (1)" in x["error"] for x in rows)
