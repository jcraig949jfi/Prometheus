"""9.0.1: one Store per request-in-flight from a checkout/checkin pool, never
one per request and never one shared across concurrent requests.

The thread-local version of this fix handed one connection to two concurrent
requests (FastAPI runs a sync dependency and a sync endpoint on different
threadpool threads) and died at request 1,751 of its first measurement with
"cannot start a transaction within a transaction".

HONEST LIMIT: this test does NOT reproduce that race -- it was run against
the thread-local version and passed (Starlette's TestClient does not
schedule the dependency and the endpoint on different threads the way a
real uvicorn process does). It checks pool CORRECTNESS under in-process
concurrency (zero 5xx, every row exactly once). The regression for the
real shape is the real-process run: deploy/longrun_load.py at 20 x 1,000
with 2 producers + a reader, acceptance 0 5xx and 0 calls over 5 s.
"""
import os
import sys
import threading

from fastapi.testclient import TestClient

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from sfe.api import create_app                                    # noqa: E402

HDR = "X-SFE-Session"


def test_concurrent_requests_never_share_a_connection_and_never_reopen_per_request(tmp_path):
    app = create_app(str(tmp_path / "pool.db"))
    c = TestClient(app)
    tok = c.post("/v2/clients", json={"name": "pool"}).json()["token"]
    h = {"Authorization": "Bearer " + tok}
    sess = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    h[HDR] = sess["session_key"]
    wids = []
    for i in range(4):
        w = c.post("/v2/worlds", json={"session_id": sess["session_id"], "name": "w%d" % i}, headers=h).json()["world_id"]
        c.post("/v2/worlds/%s/start" % w, headers=h)
        wids.append(w)

    statuses, lock = [], threading.Lock()

    def writer(k):
        wid = wids[k % 4]
        for i in range(40):
            r = c.post("/v2/worlds/%s/experiments" % wid, json={"spec": {"k": k, "i": i}}, headers=h)
            with lock:
                statuses.append(r.status_code)
            if r.status_code != 200:
                continue
            e = r.json()["exp_id"]
            r2 = c.post("/v2/worlds/%s/experiments/%s/commit" % (wid, e), json={}, headers=h)
            r3 = c.post("/v2/worlds/%s/observations" % wid,
                        json={"exp_id": e, "content": {"k": k, "i": i}, "outcome": "SURVIVED", "logical_time": i},
                        headers=h)
            with lock:
                statuses.extend([r2.status_code, r3.status_code])

    def reader():
        for _ in range(60):
            for wid in wids:
                r = c.get("/v2/worlds/%s/observations?after_seq=0&limit=50" % wid, headers=h)
                with lock:
                    statuses.append(r.status_code)

    threads = [threading.Thread(target=writer, args=(k,)) for k in range(8)] + [threading.Thread(target=reader)]
    [t.start() for t in threads]; [t.join() for t in threads]
    assert statuses and all(s == 200 for s in statuses), sorted(set(statuses))
    # every row landed exactly once
    total = sum(len(c.get("/v2/worlds/%s/observations" % w, headers=h).json()["observations"]) for w in wids)
    assert total == 8 * 40
    # the pool is bounded by concurrency, not by request count (~1,300 requests here)
    import sqlite3
    cx = sqlite3.connect(str(tmp_path / "pool.db"))
    assert cx.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 320
    cx.close()


def test_generation_bump_retires_pooled_handles(tmp_path):
    app = create_app(str(tmp_path / "g.db"))
    c = TestClient(app)
    assert c.get("/v2/version").status_code == 200
    app.state.foundry_generation += 1
    assert c.get("/v2/version").status_code == 200        # reopened, still answers
    assert c.get("/v2/capabilities").status_code == 200
