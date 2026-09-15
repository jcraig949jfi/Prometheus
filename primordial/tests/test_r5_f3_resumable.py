"""F-R5-3: checkpoint -> resumable object -> resume reproduces rows (launch gate item 8). The object carries
all ten operator-19 s4.5 fields; a fresh worker resumes it with no command line reconstructed from prose;
the resumed rows equal an uninterrupted run exactly; the object is removed when the job finishes."""
from __future__ import annotations

import json
import subprocess
import threading
import time

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.tests._live import live_url

URL = live_url()
LANE = "Fr3"
WALK = "primordial.fabric.selftest_jobs:walk"
FIELDS = ("job_key", "function", "kwargs", "checkpoint", "rows", "completed_units", "remaining_units",
          "budget_consumed", "budget_remaining", "code_sha")
VOLATILE = ("ts", "job_id", "exp_id", "segment")


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = [W.JOBS.format(LANE), W.ROWS.format(LANE), W.DONE.format(LANE), W.STOP.format(LANE),
            W.WSTATE.format(LANE), W.RESUMABLE, EV.EVENTS, EV.CANDIDATES]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r5-3")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path
    r.delete(*keys)
    for k in r.scan_iter(W.PROGRESS.format(LANE, "*")):
        r.delete(k)


def rows_of(path):
    return [{k: v for k, v in json.loads(x).items() if k not in VOLATILE}
            for x in path.read_text(encoding="utf-8").splitlines()]


def test_checkpoint_object_resume_reproduces_rows(env):
    r, repo = env
    kw = {"steps": 40, "seed": 5, "step_s": 0.03}
    envl = EV.example(checkpointable=True, expected_output_rows=40, wall_budget_s=120, cpu_budget_s=60)
    ck = repo / "ck"

    W.submit(LANE, WALK, "R5-3-ref", "rows/ref.jsonl", 60, kw, r=r, envelope=envl)
    ref = W.Worker(LANE, url=URL, repo=repo, ckpt_dir=ck, log=lambda *_: None).serve(max_jobs=1, block_ms=500)
    assert ref[0]["status"] == "ok"

    cut_id = W.submit(LANE, WALK, "R5-3-cut", "rows/cut.jsonl", 60, kw, r=r, envelope=envl, job_key="walk-cut")

    def boundary():                                                      # an epoch boundary after 5 rows
        t = time.monotonic()
        while time.monotonic() - t < 20:
            if sum(1 for _, f in r.xrange(W.ROWS.format(LANE)) if f.get("job_id") == cut_id) >= 5:
                r.set(W.STOP.format(LANE), 1)
                return
            time.sleep(0.01)
    threading.Thread(target=boundary, daemon=True).start()
    w1 = W.Worker(LANE, url=URL, repo=repo, ckpt_dir=ck, log=lambda *_: None, auto_requeue=False)
    d1 = w1.serve(max_jobs=1, block_ms=500, deadline_s=20)
    assert d1[0]["status"] == "paused" and d1[0]["resumable"] and "next_job_id" not in d1[0]
    r.delete(W.STOP.format(LANE))

    obj = W.resumables(r)["walk-cut"]
    assert all(obj.get(f) is not None for f in FIELDS), {f: obj.get(f) for f in FIELDS}
    assert obj["function"] == WALK and obj["kwargs"] == kw and obj["rows"] == "rows/cut.jsonl"
    assert 0 < obj["completed_units"] < 40 and obj["completed_units"] + obj["remaining_units"] == 40
    assert obj["budget_consumed"]["cpu_s"] >= 0 and obj["budget_remaining"]["cpu_s"] <= 60
    assert obj["budget_remaining"]["wall_s"] < 120 and obj["segment"] == 1 and obj["envelope"] == envl
    assert len(obj["code_sha"]) == 40 and obj["queued_job_id"] is None
    assert [e["job_key"] for e in EV.events(r, "CHECKPOINTED")] == ["walk-cut"]

    got = W.resume(r, "walk-cut")
    assert got["ok"]
    assert W.resume(r, "walk-cut") == {"ok": False, "reason": "ALREADY_QUEUED", "queued_job_id": got["job_id"]}
    w2 = W.Worker(LANE, url=URL, repo=repo, ckpt_dir=ck, log=lambda *_: None)          # a fresh worker + child
    d2 = w2.serve(max_jobs=1, block_ms=500)
    assert d2[0]["status"] == "ok" and d2[0]["segment"] == 1 and d2[0]["job_key"] == "walk-cut"
    assert d2[0]["cpu_prior"] == pytest.approx(obj["budget_consumed"]["cpu_s"], abs=1e-3)

    cut = [x for x in rows_of(repo / "rows" / "cut.jsonl") if x.get("kind") == "walk"]
    refr = [x for x in rows_of(repo / "rows" / "ref.jsonl") if x.get("kind") == "walk"]
    assert len(cut) == 40 and cut == refr
    assert "walk-cut" not in W.resumables(r) and not (ck / LANE / "walk-cut.pkl").exists()


def test_resume_refusals(env, monkeypatch):
    r, repo = env
    assert W.resume(r, "nope") == {"ok": False, "reason": "NO_OBJECT"}
    ck = repo / "ck" / LANE
    ck.mkdir(parents=True)
    (ck / "k.pkl").write_bytes(b"x")
    base = {"job_key": "k", "function": WALK, "kwargs": {}, "checkpoint": str(ck / "k.pkl"), "rows": "rows/k.jsonl",
            "lane": LANE, "exp_id": "e", "ttl_cpu_s": 10.0, "segment": 1, "envelope": None, "queued_job_id": None,
            "budget_consumed": {"cpu_s": 1.0, "wall_s": 1.0}, "code_file_sha256": "0" * 64}
    r.hset(W.RESUMABLE, "k", json.dumps(base))
    assert W.resume(r, "k")["reason"] == "CODE_CHANGED"
    r.hset(W.RESUMABLE, "k", json.dumps(dict(base, code_file_sha256=W.code_file_sha256(WALK),
                                             checkpoint=str(ck / "gone.pkl"))))
    assert W.resume(r, "k")["reason"] == "NO_CHECKPOINT"


def test_refused_queued_segment_becomes_resumable_again(env):
    """At NO_NEW_WORK a paused job's auto-requeued segment is refused; the object must not stay 'queued'."""
    r, repo = env
    job_id = W.submit(LANE, WALK, "e", "rows/x.jsonl", 10, {}, r=r, job_key="kq", segment=1)
    r.hset(W.RESUMABLE, "kq", json.dumps({"job_key": "kq", "queued_job_id": job_id}))
    job = {"job_id": job_id, "job_key": "kq", "fn": WALK, "exp_id": "e", "segment": "1"}
    w = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None)
    w._refuse(job, {"ok": False, "event": EV.NO_NEW_WORK_REFUSAL, "reasons": ["NO_NEW_WORK"], "stage": "PILOT",
                    "ceiling": None})
    o = W.resumables(r)["kq"]
    assert o["queued_job_id"] is None and o["refused"] == ["NO_NEW_WORK"]
    w.stop()
