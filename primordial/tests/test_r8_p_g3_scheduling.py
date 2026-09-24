"""G3 (round 8): the scheduling cluster D15 + D22 + D30, each test aimed at the round-7 failure it closes.

D30  an epoch requeue landed at the END of pm:jobs:<L>: 4 nearly-finished cells sat behind 44 later jobs.
D22  the CPU broker was not FIFO: a short-job burst starved lane D ~7 min (diagnosed from a complaint).
D15  a non-checkpointable job held every lane 8.8 min; its wall stays capped at 900 s and the drain still completes.
G5   the five queue fields are emitted for every grant.
"""
from __future__ import annotations

import json
import subprocess
import threading
import time
import uuid

import pytest

from primordial.bus import bus
from primordial.fabric import broker as BR
from primordial.fabric import envelope as EV
from primordial.fabric import telemetry as TM
from primordial.fabric import worker as W
from primordial.ops.epoch import EpochController
from primordial.tests._live import live_url

URL = live_url()
SLEEP = "primordial.fabric.selftest_jobs:sleep_rows"
WALK = "primordial.fabric.selftest_jobs:walk"


def _keys(lanes):
    keys = [BR.PROFILE_KEY, BR.WAITERS, BR.WAITER_BEAT, EV.EVENTS, EV.CANDIDATES, TM.QUEUE, TM.WATCH,
            "pm:round:current", W.RESUMABLE] + [BR.TOKEN.format(i) for i in range(8)]
    for L in lanes:
        keys += [W.JOBS.format(L), W.CONT.format(L), W.ROWS.format(L), W.DONE.format(L), W.STOP.format(L),
                 W.WSTATE.format(L)]
    return keys


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    lanes: list = []
    r.delete(*_keys([]))
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r8-g3")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path, lanes
    r.delete(*_keys(lanes))


def lane(lanes, p="g"):
    L = p + uuid.uuid4().hex[:6]
    lanes.append(L)
    return L


def done_recs(r, L):
    return [json.loads(f["json"]) for _, f in r.xrange(W.DONE.format(L))]


# ------------------------------------------------------------------ D30

def test_d30_peek_orders_by_original_queue_entry(env):
    """A continuation beats every job submitted AFTER its original, and never a job queued BEFORE it."""
    r, repo, lanes = env
    L = lane(lanes)
    wk = W.Worker(L, url=URL, repo=repo, log=lambda *_: None)
    t_before = time.time() - 100
    W.submit(L, SLEEP, "fresh-A", "rows/a.jsonl", 30, {"s": 0}, r=r)                   # enters now
    fresh_ts = float(r.xrange(W.JOBS.format(L))[-1][1]["priority_ts"])
    W.submit(L, SLEEP, "cont-late", "rows/c.jsonl", 30, {"s": 0}, r=r, segment=1, priority_ts=fresh_ts + 50)
    assert wk.peek("c")["stream"] == W.JOBS.format(L)                  # queued before the late continuation's origin
    W.submit(L, SLEEP, "cont-early", "rows/c.jsonl", 30, {"s": 0}, r=r, segment=1, priority_ts=t_before)
    # the early continuation is BEHIND cont-late in its stream; the head of :cont is still cont-late
    assert wk.peek("c")["stream"] == W.JOBS.format(L)
    assert r.xlen(W.CONT.format(L)) == 2
    # shadows: every continuation job_id resolves on pm:jobs:<L> (drain sizing, budget, receipt guard)
    shadows = [f for _, f in r.xrange(W.JOBS.format(L)) if f.get("shadow")]
    assert len(shadows) == 2 and all(f["continuation"] == "1" for f in shadows)


def test_d30_requeued_continuation_runs_before_later_jobs(env):
    """Round-7 shape: a checkpointed job is paused at an epoch boundary while later jobs queue behind it; on resume
    the continuation is granted BEFORE every job submitted after the original."""
    r, repo, lanes = env
    L = lane(lanes)
    ck = repo.parent / "ckpt"
    W.submit(L, WALK, "cell", "rows/cell.jsonl", ttl_cpu_s=120, kwargs={"steps": 40, "step_s": 0.05}, r=r,
             job_key="cell-w19")
    wk = W.Worker(L, url=URL, repo=repo, log=lambda *_: None, ckpt_dir=ck)
    out: list = []
    th = threading.Thread(target=lambda: out.extend(wk.serve(block_ms=100, deadline_s=90, max_jobs=6)), daemon=True)
    th.start()
    t = time.monotonic()
    while not r.hget(W.WSTATE.format(L), "state") == "busy" and time.monotonic() - t < 30:
        time.sleep(0.05)
    time.sleep(0.4)
    later = [W.submit(L, SLEEP, f"learner-{i}", "rows/l.jsonl", 30, {"s": 0.05}, r=r) for i in range(4)]
    ec = EpochController([L], r=r, out=repo / "epochs", repo=repo, post=False, log=lambda *_: None,
                         export=lambda out, stamp, r: (out.mkdir(parents=True, exist_ok=True), {})[1])
    rec = ec.boundary(1, resume=False)
    assert rec["stragglers"] == []                                                   # the drain completed
    assert r.xlen(W.CONT.format(L)) == 1                                             # requeued as a continuation
    r.delete(W.STOP.format(L))
    th.join(timeout=90)
    recs = done_recs(r, L)
    order = [(d["job_key"], d["segment"], d["status"]) for d in recs]
    assert order[0] == ("cell-w19", 0, "paused")
    assert order[1] == ("cell-w19", 1, "ok"), order                                 # D30: before all 4 later jobs
    assert [d["job_id"] for d in recs[2:]] == later
    cont = recs[1]
    assert cont["continuation"] is True and recs[0]["continuation"] is False
    assert all(not d["continuation"] for d in recs[2:])
    assert cont["queue_position"] == 0


# ------------------------------------------------------------------ D22

def test_d22_broker_fifo_unit(env):
    r, _, _ = env
    r.set(BR.PROFILE_KEY, json.dumps({"k_star": 1, "threads_per_worker": 8}))
    now = time.time()
    assert BR.acquire(r, "S", waiter="S:1", priority_ts=now) is not None and BR.free_slots(r) == 0
    for tok in BR.holders(r):
        r.delete(BR.TOKEN.format(tok["slot"]))
    assert BR.acquire(r, "D", waiter="D:1", priority_ts=now - 50) is not None        # D waited longer: granted
    r.delete(BR.TOKEN.format(0))
    assert BR.acquire(r, "D", waiter="D:2", priority_ts=now - 60) is not None
    r.delete(BR.TOKEN.format(0))
    # D:4 has waited longest and is polling (fresh heartbeat); S's fresh job may not jump it
    r.zadd(BR.WAITERS, {"D:4": now - 80})
    r.hset(BR.WAITER_BEAT, "D:4", time.time())
    assert BR.acquire(r, "S", waiter="S:2", priority_ts=now) is None                  # D:4 is ahead: S refused
    tok = BR.acquire(r, "D", waiter="D:4", priority_ts=now - 80)
    assert tok is not None and tok["_queue_position"] == 0 and "D:4" not in dict(BR.waiters(r))
    r.delete(BR.TOKEN.format(0))
    BR.leave(r, "S:2")                                        # S:2 is still queued (refused, not left); drop it
    # a dead waiter (no heartbeat within WAITER_STALE_S) is pruned and cannot block the queue
    r.zadd(BR.WAITERS, {"dead": now - 999})
    r.hset(BR.WAITER_BEAT, "dead", time.time() - BR.WAITER_STALE_S - 1)
    assert BR.acquire(r, "S", waiter="S:3", priority_ts=now) is not None and "dead" not in dict(BR.waiters(r))


def test_d22_short_burst_cannot_starve_the_longest_waiter(env):
    """k*=1, round-7 shape. Lane S has 3 workers and 2 older jobs holding the token; lane D queues ONE job; then S
    floods a burst of short jobs. No S job that entered after D may be granted before D, so D's wait is bounded by
    the work queued before it. (Round-7 first-poller-wins broker: the 3 S pollers re-take the token ahead of D.)"""
    r, repo, lanes = env
    r.set(BR.PROFILE_KEY, json.dumps({"k_star": 1, "threads_per_worker": 8}))
    S, D = lane(lanes, "s"), lane(lanes, "d")
    for i in range(2):
        W.submit(S, SLEEP, f"S-pre{i}", "rows/s.jsonl", 30, {"s": 0.8}, r=r, envelope=EV.example(cohort="S"))
    wss = [W.Worker(S, url=URL, repo=repo, log=lambda *_: None) for _ in range(3)]
    wd = W.Worker(D, url=URL, repo=repo, log=lambda *_: None)
    out = {"S": [], "D": []}
    lock = threading.Lock()

    def serve_s(w):
        got = w.serve(block_ms=100, deadline_s=30, idle_exit_s=3)
        with lock:
            out["S"].extend(got)
    ths = [threading.Thread(target=serve_s, args=(w,), daemon=True) for w in wss]
    td = threading.Thread(target=lambda: out["D"].extend(wd.serve(block_ms=100, deadline_s=30, max_jobs=1)),
                          daemon=True)
    for th in ths + [td]:
        th.start()
    t = time.monotonic()
    while not BR.holders(r) and time.monotonic() - t < 20:
        time.sleep(0.02)
    time.sleep(0.2)
    W.submit(D, SLEEP, "D0", "rows/d.jsonl", 30, {"s": 0.1}, r=r, envelope=EV.example(cohort="D"))
    time.sleep(0.3)                                           # D is queued (the token is busy) before the burst
    for i in range(24):
        W.submit(S, SLEEP, f"S-burst{i}", "rows/s.jsonl", 30, {"s": 0.05}, r=r, envelope=EV.example(cohort="S"))
    for th in ths + [td]:
        th.join(timeout=60)
    (d,) = out["D"]
    assert d["status"] == "ok"
    burst = [s for s in out["S"] if s["queue_enter_ts"] > d["queue_enter_ts"]]
    assert len(burst) == 24 and all(s["status"] == "ok" for s in out["S"])
    jumped = [s for s in burst if s["grant_ts"] < d["grant_ts"]]
    assert jumped == [], f"{len(jumped)} burst jobs that entered after D were granted before it"
    before = [s for s in out["S"] if s["grant_ts"] < d["grant_ts"] and s["ended"] > d["queue_enter_ts"]]
    assert all(s["queue_enter_ts"] < d["queue_enter_ts"] for s in before) and len(before) <= 2
    assert d["wait_s"] <= (len(before) + 1) * (max(s["wall_s"] for s in out["S"]) + 1.0)   # bounded wait


# ------------------------------------------------------------------ D15

def test_d15_noncheckpointable_wall_capped_at_900(env):
    ok = EV.admit(EV.example(campaign_stage="PRODUCTION", wall_budget_s=900, checkpointable=False))
    over = EV.admit(EV.example(campaign_stage="PRODUCTION", wall_budget_s=901, checkpointable=False))
    ckp = EV.admit(EV.example(campaign_stage="PRODUCTION", wall_budget_s=2400, checkpointable=True))
    assert "NONCHECKPOINTABLE_WALL_OVER_CEILING" not in ok["reasons"]
    assert "NONCHECKPOINTABLE_WALL_OVER_CEILING" in over["reasons"] and not over["ok"]
    assert "NONCHECKPOINTABLE_WALL_OVER_CEILING" not in ckp["reasons"]
    assert EV.CEILINGS["PRODUCTION"]["cpu_wall_noncheckpointable_s"] == 900


def test_d15_drain_sizes_a_continuation_from_its_shadow_and_stop_blocks_the_cont_class(env):
    """The drain's job-wall bound must resolve a continuation's job_id (its spec lives on :cont), and a stop flag
    must hold back the continuation class too -- priority never bypasses a drain."""
    r, repo, lanes = env
    L = lane(lanes)
    env_ = EV.example(wall_budget_s=300, checkpointable=True)
    jid = W.submit(L, SLEEP, "c", "rows/c.jsonl", 30, {"s": 0}, r=r, segment=1, priority_ts=time.time() - 500,
                   envelope=env_, wall_prior=100)
    ec = EpochController([L], r=r, out=repo / "epochs", repo=repo, post=False, log=lambda *_: None,
                         export=lambda out, stamp, r: (out.mkdir(parents=True, exist_ok=True), {})[1])
    assert ec._job_wall_bound(L, jid) == pytest.approx(200.0)                        # not the 900 s fallback
    r.set(W.STOP.format(L), "1")
    wk = W.Worker(L, url=URL, repo=repo, log=lambda *_: None)
    assert wk.serve(block_ms=100, deadline_s=1.5) == []
    assert r.xlen(W.CONT.format(L)) == 1 and wk.depth()["depth_cont"] == 1


# ------------------------------------------------------------------ G5 queue fields on every grant

def test_queue_fields_on_every_done_record_and_grant(env):
    r, repo, lanes = env
    L = lane(lanes)
    W.submit(L, SLEEP, "ok", "rows/q.jsonl", 30, {"s": 0}, r=r)
    W.submit(L, SLEEP, "refused", "rows/q.jsonl", 30, {"s": 0}, r=r,
             envelope=EV.example(campaign_stage="PRODUCTION", wall_budget_s=901, checkpointable=False))
    W.submit(L, SLEEP, "cont", "rows/q.jsonl", 30, {"s": 0}, r=r, segment=1, priority_ts=time.time() + 5)
    recs = W.Worker(L, url=URL, repo=repo, log=lambda *_: None).serve(block_ms=100, max_jobs=3, deadline_s=30)
    assert sorted(d["status"] for d in recs) == ["ok", "ok", "refused"]
    for d in recs + done_recs(r, L):
        assert all(k in d for k in TM.QUEUE_FIELDS), d
        assert d["wait_s"] == pytest.approx(d["grant_ts"] - d["queue_enter_ts"], abs=2e-3) and d["wait_s"] >= 0
        assert isinstance(d["continuation"], bool)
    grants = [json.loads(f["json"]) for _, f in r.xrange(TM.QUEUE)]
    grants = [g for g in grants if g["record"] == "QUEUE_GRANT" and g["lane"] == L]
    assert len(grants) == 3 and all(all(k in g for k in TM.QUEUE_FIELDS) for g in grants)
    assert [g["continuation"] for g in grants] == [False, False, True]
