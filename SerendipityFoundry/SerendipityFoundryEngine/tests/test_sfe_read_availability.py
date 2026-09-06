"""D-LOCK-1: a read must not queue behind a writer.

Found 2026-09-06 while onboarding a second and third consumer (Archaeon as a
producer, Vivarium as an executor, alongside Harmonia). `api.get_foundry()`
constructs a Foundry per request and `Store.initialize()` opened
`with self.write()` unconditionally -- BEGIN IMMEDIATE, the exclusive write
lock -- purely to re-read one row of `meta`. Every request in the engine,
including unauthenticated read-only ones, therefore serialized behind every
writer, and the architecture's promise of WAL concurrent readers was false in
practice.

Measured on the live M1 service before the fix, with one ordinary consumer
writing:

    GET /v2/version        22.8s, 17.6s   (has the db dependency)
    GET /v2/openapi.json   0.018s         (same process, same TLS, no db)

against a 30s busy_timeout. These tests are the regression guard: each one
FAILS on the pre-fix code by hanging until the timeout.
"""
import os
import sys
import tempfile
import threading
import time

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.api import create_app                                    # noqa: E402
from sfe.runtime import Foundry                                   # noqa: E402
from sfe.store import SCHEMA_VERSION, Store                       # noqa: E402

# HOLD_S is how long the competing writer keeps BEGIN IMMEDIATE; BUDGET_S is
# what a read is allowed to take. BUDGET_S must sit well BELOW HOLD_S or the
# test passes on the broken code too -- the first cut of this file used a 5s
# budget against a 3s hold and three of these four tests did not bite.
HOLD_S = 4.0
BUDGET_S = 1.5


@pytest.fixture
def db(tmp_path):
    p = str(tmp_path / "avail.db")
    f = Foundry(p)                      # create + migrate once
    c = f.create_client("owner")
    s = f.create_session(c, "s")
    w = f.create_world(s, "w")["world_id"]
    f.start_world(w, c)
    f.close()
    return p, c, w


def _held_write_lock(db_path, hold_s, started):
    """Hold BEGIN IMMEDIATE for hold_s, exactly as a real writer does."""
    st = Store(db_path)
    st.initialize()
    cx = st._conn
    cx.execute("BEGIN IMMEDIATE")
    started.set()
    time.sleep(hold_s)
    cx.execute("ROLLBACK")
    st.close()


def test_opening_a_foundry_does_not_wait_for_the_write_lock(db):
    """The core defect. Constructing a Foundry ran BEGIN IMMEDIATE, so merely
    OPENING the engine blocked on any in-flight writer."""
    path, _c, _w = db
    started = threading.Event()
    t = threading.Thread(target=_held_write_lock, args=(path, HOLD_S, started),
                         daemon=True)
    t.start()
    assert started.wait(5), "writer never took the lock"

    t0 = time.monotonic()
    f = Foundry(path)
    elapsed = time.monotonic() - t0
    f.close()
    assert elapsed < BUDGET_S, (
        "opening a Foundry waited %.1fs for another writer's lock; the "
        "schema check must use a plain read" % elapsed)
    t.join(timeout=10)


def test_read_only_routes_stay_fast_while_a_writer_holds_the_lock(db):
    """GET /v2/version is unauthenticated, takes no arguments and writes
    nothing. It must not be able to reach the busy timeout."""
    path, _c, _w = db
    client = TestClient(create_app(path))
    started = threading.Event()
    t = threading.Thread(target=_held_write_lock, args=(path, HOLD_S, started),
                         daemon=True)
    t.start()
    assert started.wait(5)

    t0 = time.monotonic()
    r = client.get("/v2/version")
    elapsed = time.monotonic() - t0
    assert r.status_code == 200, r.text
    assert r.json()["schema_version"] == SCHEMA_VERSION
    assert elapsed < BUDGET_S, (
        "GET /v2/version took %.1fs behind a writer" % elapsed)
    t.join(timeout=10)


def test_an_authenticated_read_also_stays_fast(db):
    """Not just the unauthenticated one: every consumer's reads were affected,
    which is what turned this from slow into a three-consumer availability
    problem."""
    path, _c, wid = db
    client = TestClient(create_app(path))
    tok = client.post("/v2/clients", json={"name": "reader"}).json()["token"]
    h = {"Authorization": "Bearer " + tok}

    started = threading.Event()
    t = threading.Thread(target=_held_write_lock, args=(path, HOLD_S, started),
                         daemon=True)
    t.start()
    assert started.wait(5)

    t0 = time.monotonic()
    r = client.get("/v2/worlds", headers=h)
    elapsed = time.monotonic() - t0
    assert r.status_code == 200, r.text
    assert elapsed < BUDGET_S, (
        "an authenticated read took %.1fs behind a writer" % elapsed)
    t.join(timeout=10)


def test_a_real_migration_still_takes_the_write_lock(tmp_path):
    """The fast path must not weaken migration safety: a database that is NOT
    at the current version still goes through BEGIN IMMEDIATE, so two engines
    opening an out-of-date ledger cannot migrate it concurrently."""
    p = str(tmp_path / "old.db")
    f = Foundry(p)
    f.close()
    st = Store(p)
    st.initialize()
    with st.write() as cx:                       # pretend it is older
        cx.execute("UPDATE meta SET value='5' WHERE key='schema_version'")
    st.close()

    calls = []
    real = Store.write

    def spy(self):
        calls.append(1)
        return real(self)

    Store.write = spy
    try:
        f2 = Foundry(p)
        f2.close()
    finally:
        Store.write = real
    assert calls, "an out-of-date schema must still be migrated under the lock"

    st = Store(p)
    assert st.read().execute(
        "SELECT value FROM meta WHERE key='schema_version'"
    ).fetchone()["value"] == str(SCHEMA_VERSION)
    st.close()


def test_current_schema_takes_no_write_lock_at_all(db):
    """The positive statement of the fix, asserted directly rather than
    inferred from timing."""
    path, _c, _w = db
    calls = []
    real = Store.write

    def spy(self):
        calls.append(1)
        return real(self)

    Store.write = spy
    try:
        f = Foundry(path)
        f.close()
    finally:
        Store.write = real
    assert calls == [], (
        "opening a Foundry on an already-current schema took the write lock "
        "%d time(s)" % len(calls))


def test_writes_are_still_serialized(db):
    """Guard the property the lock exists for: two concurrent claims of the
    same work item must still produce exactly one winner."""
    path, cid, wid = db
    f = Foundry(path)
    e = f.create_experiment(wid, {"x": 1}, client_id=cid, enqueue=True)
    f.close()

    winners, errors = [], []

    def claim(worker):
        try:
            g = Foundry(path)
            got = g.claim_work(worker, world_id=wid, client_id=cid)
            if got:
                winners.append((worker, got["work_id"]))
            g.close()
        except Exception as exc:                                # noqa: BLE001
            errors.append(exc)

    ts = [threading.Thread(target=claim, args=("w%d" % i,)) for i in range(6)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(timeout=30)

    assert not errors, errors
    assert len(winners) == 1, (
        "exactly one worker may claim work %s; got %r" % (e["work_id"], winners))
