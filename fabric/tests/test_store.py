"""Integration tests of the durable core against a THROWAWAY schema in the
canonical store (same pattern as comms/tests). Needs EW_DB_HOST pointing at
the canonical cluster; skipped if unreachable."""
import os
import secrets
import threading
import time

import pytest

from fabric import store as S

W1 = dict(agent="worker.t1", instance="t1-aaaa", host="h1")
CAPS = ["repo.read", "research.repo_readonly", "research.synthesis", "compute.cpu.light", "python.stdlib"]
EXE = ["synthetic", "script", "claude"]


@pytest.fixture
def conn(monkeypatch):
    name = "fabric_test_" + secrets.token_hex(4)
    monkeypatch.setenv("FABRIC_SCHEMA", name)
    try:
        c = S.connect(require_schema=False)
    except Exception as e:  # pragma: no cover
        pytest.skip("canonical store unreachable: {}".format(e))
    S.init_schema(c)
    yield c
    cur = c.cursor(); cur.execute("DROP SCHEMA {} CASCADE".format(name)); c.commit(); c.close()


def _sub(conn, **kw):
    kw.setdefault("executor", "synthetic")
    return S.submit(conn, kw.pop("principal", "Tester"), kw.pop("instruction", "do x"), kw.pop("executor"), **kw)


def _claim(conn, caps=CAPS, agent="worker.t1", instance="t1-aaaa", host="h1", **kw):
    return S.claim(conn, agent, instance, host, caps, EXE, **kw)


def test_submit_is_idempotent(conn):
    a = _sub(conn, idempotency_key="k1")
    b = _sub(conn, idempotency_key="k1")
    c = _sub(conn, idempotency_key="k2")
    assert a["created"] and not b["created"] and a["task_id"] == b["task_id"] and c["task_id"] != a["task_id"]
    assert len(S.list_tasks(conn)) == 2


def test_capability_routing(conn):
    t = _sub(conn, required_caps=["research.repo_readonly"])["task_id"]
    assert _claim(conn, caps=["compute.cpu.light"]) is None           # incompatible worker takes nothing
    got = _claim(conn)
    assert got["task"]["task_id"] == t and got["task"]["state"] == "working"


def test_target_agent_and_host_affinity(conn):
    t1 = _sub(conn, target_agent="worker.other")["task_id"]
    t2 = _sub(conn, host_affinity="h9")["task_id"]
    assert _claim(conn) is None
    assert _claim(conn, agent="worker.other", instance="o-1")["task"]["task_id"] == t1
    assert _claim(conn, host="h9")["task"]["task_id"] == t2


def test_atomic_claim_race_many_tasks(conn):
    ids = {_sub(conn, idempotency_key="r%d" % i)["task_id"] for i in range(30)}
    won, lock = [], threading.Lock()

    def worker(n):
        c = S.connect()
        while True:
            g = S.claim(c, "worker.r%d" % n, "r%d" % n, "h%d" % n, CAPS, EXE)
            if g is None:
                break
            with lock:
                won.append(g["task"]["task_id"])
        c.close()

    ths = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
    [t.start() for t in ths]; [t.join() for t in ths]
    assert sorted(won) == sorted(ids)                                # every task claimed exactly once


def test_one_live_attempt_enforced_by_database(conn):
    t = _sub(conn)["task_id"]
    g = _claim(conn)
    cur = conn.cursor()
    with pytest.raises(Exception):
        cur.execute("INSERT INTO {}.attempts (attempt_id, task_id, seq, agent, instance, host, status, expires_at) "
                    "VALUES ('att-x', %s, 9, 'a', 'b', 'c', 'running', now() + interval '1 min')".format(S.schema()), (t,))
    conn.rollback()


def test_resource_busy_worker_takes_other_task(conn):
    hold = S.lease_acquire(conn, "pilot:cpu8", "Someone", "h0", purpose="test hold", ttl_s=600)
    assert hold["result"] == "ACQUIRED"
    heavy = _sub(conn, resources=["pilot:cpu8"], priority=10)["task_id"]
    light = _sub(conn)["task_id"]
    g = _claim(conn)
    assert g["task"]["task_id"] == light                              # researchers don't queue
    assert S.get_task(conn, heavy)["waiting_reason"] == "resource pilot:cpu8 busy"
    assert S.finish_attempt(conn, g["attempt_id"], "succeeded", "w")["task_state"] == "completed"
    assert _claim(conn) is None                                       # heavy still waits
    assert S.lease_release(conn, hold["lease_id"], hold["token"], "Someone")
    g2 = _claim(conn)
    assert g2["task"]["task_id"] == heavy and len(g2["leases"]) == 1


def test_lease_exclusive_and_expiry(conn):
    a = S.lease_acquire(conn, "M9:gpu", "A", "h", ttl_s=1)
    b = S.lease_acquire(conn, "M9:gpu", "B", "h", ttl_s=60)
    assert a["result"] == "ACQUIRED" and b["result"] == "BUSY" and b["held_by"]["holder"] == "A"
    time.sleep(1.5)
    c = S.lease_acquire(conn, "M9:gpu", "C", "h", ttl_s=60)
    assert c["result"] == "ACQUIRED"                                  # expired holder taken over
    assert not S.lease_release(conn, a["lease_id"], a["token"], "A")  # the expired lease cannot release the new one
    assert not S.lease_release(conn, c["lease_id"], "wrong-token", "X")


def test_heartbeat_expiry_reap_requeue_and_second_worker(conn):
    t = _sub(conn, resources=["pilot:gpu"])["task_id"]
    g = _claim(conn, ttl_s=1)
    time.sleep(1.5)
    r = S.reap(conn)
    assert r["abandoned"] and r["abandoned"][0]["task_state"] == "submitted"
    task = S.get_task(conn, t)
    assert task["attempts"][0]["status"] == "abandoned" and task["state"] == "submitted"
    assert S.leases(conn) == []                                       # its lease was released with it
    late = S.finish_attempt(conn, g["attempt_id"], "succeeded", "late-worker")
    assert late["accepted"] is False                                  # a late worker cannot complete the task
    assert not S.heartbeat(conn, g["attempt_id"], "late-worker")["ok"]
    g2 = _claim(conn, agent="worker.t2", instance="t2-bbbb", host="h2")
    assert g2["task"]["task_id"] == t and g2["task"]["attempts_made"] == 2
    assert S.finish_attempt(conn, g2["attempt_id"], "succeeded", "w2")["task_state"] == "completed"


def test_max_attempts_then_terminal_failed(conn):
    t = _sub(conn, max_attempts=2)["task_id"]
    for i in range(2):
        g = _claim(conn)
        S.finish_attempt(conn, g["attempt_id"], "failed", "w", error="boom %d" % i)
    task = S.get_task(conn, t)
    assert task["state"] == "failed" and task["error_summary"] == "boom 1" and _claim(conn) is None


def test_terminal_states_stay_terminal(conn):
    t = _sub(conn)["task_id"]
    g = _claim(conn)
    S.finish_attempt(conn, g["attempt_id"], "succeeded", "w", result_summary="done")
    with pytest.raises(S.NotCancelable):
        S.cancel(conn, t, "p")
    assert S.get_task(conn, t)["state"] == "completed"


def test_cancel_submitted_and_working(conn):
    a = _sub(conn)["task_id"]
    assert S.cancel(conn, a, "p")["state"] == "canceled"
    b = _sub(conn)["task_id"]
    g = _claim(conn)
    assert S.cancel(conn, b, "p")["cancel_requested"]
    assert S.heartbeat(conn, g["attempt_id"], "w")["cancel_requested"] is True
    assert S.finish_attempt(conn, g["attempt_id"], "canceled", "w")["task_state"] == "canceled"


def test_artifacts_content_addressed_and_verified(conn):
    t = _sub(conn)["task_id"]
    g = _claim(conn)
    a1 = S.add_artifact(conn, t, g["attempt_id"], "report.md", "report", b"hello")
    a2 = S.add_artifact(conn, t, g["attempt_id"], "copy.md", "file", b"hello")
    assert a1["sha256"] == a2["sha256"]
    got = S.artifact_content(conn, a1["artifact_id"])
    assert got["content"] == b"hello" and got["metadata"]["attempt_status_at_upload"] == "running"
    task = S.get_task(conn, t)
    assert {x["name"] for x in task["artifacts"]} == {"report.md", "copy.md"}


def test_event_history_is_complete(conn):
    t = _sub(conn)["task_id"]
    g = _claim(conn)
    S.heartbeat(conn, g["attempt_id"], "w")
    S.add_artifact(conn, t, g["attempt_id"], "r", "report", b"x")
    S.finish_attempt(conn, g["attempt_id"], "succeeded", "w")
    kinds = [e["kind"] for e in S.events(conn, t)]
    assert kinds == ["submitted", "claimed", "attempt_started", "heartbeat", "artifact_added", "completed"]


# ---------------------------------------------------------------- legacy lease detection removed (CWO 2026-09-30)
def test_legacy_records_and_host_files_are_no_longer_consulted(conn, monkeypatch, tmp_path):
    """Regression for the 2026-09-30 removal: the fabric lease row is the only authority. A live-looking ARC3 comms
    record and host file (in throwaway stand-ins, never the live comms table) must not block a fabric lease."""
    import json as _json
    t = "{}.legacy_msgs".format(S.schema())
    cur = conn.cursor()
    cur.execute("CREATE TABLE {} (id BIGSERIAL PRIMARY KEY, subject TEXT NOT NULL, body TEXT NOT NULL DEFAULT '')".format(t))
    cur.execute("INSERT INTO {} (subject) VALUES ('LEASE ACQUIRE SKULLPORT cpu8: X until 2999-01-01 00:00Z')".format(t))
    conn.commit()
    monkeypatch.setenv("FABRIC_LEGACY_LEASE_TABLE", t)
    monkeypatch.setenv("FABRIC_LEGACY_LEASE_DIR", str(tmp_path))
    (tmp_path / "gpu.json").write_text(_json.dumps({"owner": "W-A", "until": 32503680000}))
    assert not hasattr(S, "legacy_holder")
    assert S.lease_acquire(conn, "skullport:cpu8", "Tester", "h1")["result"] == "ACQUIRED"
    assert S.lease_acquire(conn, "h1:gpu", "Tester", "h1")["result"] == "ACQUIRED"
    busy = S.lease_acquire(conn, "h1:gpu", "Other", "h1")
    assert busy["result"] == "BUSY" and busy["held_by"]["holder"] == "Tester"      # the fabric row still arbitrates
