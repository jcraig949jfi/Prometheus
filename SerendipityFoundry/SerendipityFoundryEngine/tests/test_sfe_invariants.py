"""Gen-2 adversarial invariant battery (section 24, T1-T18).

Every test provokes a real mechanism -- concurrent threads, process-restart
(dispose+reopen the DB), lease expiry, direct DB tampering -- and asserts the
invariant HOLDS. Negative-path tests assert the system FAILS CLOSED. Nothing is
mocked; the SQLite database is the source of truth throughout.
"""

from __future__ import annotations

import sqlite3
import threading
import time

import pytest

from sfe.errors import (AccessDenied, BudgetExhausted, ConflictError,
                         InvalidTransition, IsolationViolation,
                         LedgerIntegrityError, PredictionOrderingError)
from sfe.executors import (BitStringExecutor, NondeterministicExecutor,
                            WorkerLoop)
from sfe.runtime import Foundry


def _mkworld(f, client_name="c", policy="ISOLATED", start=True, budget=None):
    c = f.create_client(client_name)
    s = f.create_session(c, "s")
    w = f.create_world(s, "w", sharing_policy=policy, budget=budget)
    if start:
        f.start_world(w["world_id"], c)
    return c, w["world_id"]


# ---- T1: two clients, no leakage ------------------------------------------

def test_t1_two_clients_no_leakage(foundry):
    ca, wa = _mkworld(foundry, "A")
    cb, wb = _mkworld(foundry, "B")
    foundry.propose_hypothesis(wa, "A-secret", client_id=ca)
    foundry.propose_hypothesis(wb, "B-secret", client_id=cb)
    # each client sees only its own worlds
    assert {w["world_id"] for w in foundry.list_worlds(client_id=ca)} == {wa}
    assert {w["world_id"] for w in foundry.list_worlds(client_id=cb)} == {wb}
    # cross reads denied
    with pytest.raises(AccessDenied):
        foundry.get_world(wa, cb)
    with pytest.raises(AccessDenied):
        foundry.world_events(wb, client_id=ca)
    # events do not leak across worlds
    ea = [e["event_type"] for e in foundry.world_events(wa, client_id=ca)]
    assert "HYPOTHESIS_PROPOSED" in ea
    assert all(e["world_id"] == wa for e in foundry.world_events(wa, client_id=ca))


# ---- T2: many worlds across sessions --------------------------------------

def test_t2_many_worlds(foundry):
    c = foundry.create_client("c")
    ids = set()
    for si in range(3):
        s = foundry.create_session(c, f"s{si}")
        for _ in range(9):
            w = foundry.create_world(s, "w")
            ids.add(w["world_id"])
    assert len(ids) == 27               # >= 25 required, all unique
    got = {w["world_id"] for w in foundry.list_worlds(client_id=c)}
    assert got == ids
    for wid in ids:                     # every chain verifies
        assert foundry.verify_world(wid)["ok"]


# ---- T3: concurrent mutation of several worlds -----------------------------

def test_t3_concurrent_mutation(db_path):
    setup = Foundry(db_path)
    c = setup.create_client("c")
    s = setup.create_session(c, "s")
    worlds = [setup.create_world(s, f"w{i}")["world_id"] for i in range(6)]
    for wid in worlds:
        setup.start_world(wid, c)
    setup.close()

    errors = []

    def worker(wid):
        f = Foundry(db_path)               # own connection per thread
        try:
            for i in range(20):
                f.propose_hypothesis(wid, f"h{i}", client_id=c)
        except Exception as e:             # noqa: BLE001
            errors.append(e)
        finally:
            f.close()

    threads = [threading.Thread(target=worker, args=(wid,)) for wid in worlds]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, errors
    check = Foundry(db_path)
    try:
        for wid in worlds:
            assert check.verify_world(wid)["ok"]
            n = check.store.read().execute(
                "SELECT COUNT(*) n FROM hypotheses WHERE world_id=?",
                (wid,)).fetchone()["n"]
            assert n == 20, (wid, n)       # no lost or leaked writes
    finally:
        check.close()


# ---- T4: client death, world survives -------------------------------------

def test_t4_client_death_world_survives(db_path):
    f1 = Foundry(db_path)
    c = f1.create_client("c")
    s = f1.create_session(c, "s")
    wid = f1.create_world(s, "w")["world_id"]
    f1.start_world(wid, c)
    f1.propose_hypothesis(wid, "persisted", client_id=c)
    f1.close()                             # the "client" process dies
    f2 = Foundry(db_path)                  # a new client process
    try:
        w = f2.get_world(wid, c)
        assert w["state"] == "RUNNING"
        assert f2.verify_world(wid)["ok"]
        assert any(e["payload"].get("statement") == "persisted"
                   for e in f2.world_events(wid, client_id=c))
    finally:
        f2.close()


# ---- T5: worker death, work reclaimable -----------------------------------

def test_t5_worker_death_reclaim(foundry):
    c, wid = _mkworld(foundry, "c")
    work = foundry.enqueue_work(wid, "job", {"x": 1}, client_id=c)
    claim = foundry.claim_work("dead-worker", world_id=wid, lease_s=0.05)
    assert claim["work_id"] == work
    time.sleep(0.12)                       # lease expires; worker never returns
    reclaim = foundry.claim_work("live-worker", world_id=wid, lease_s=5.0)
    assert reclaim["work_id"] == work
    assert reclaim["claimed_by"] == "live-worker"
    assert reclaim["attempts"] == 2        # a retry, tracked honestly
    done = foundry.complete_work(work, "live-worker", {"ok": True},
                                 claim_id=reclaim["claim_id"])
    assert done["status"] == "COMPLETED"
    # the dead worker's late completion is rejected: its fencing token went
    # stale at reclaim (H1) -- even presenting it changes nothing
    with pytest.raises(ConflictError):
        foundry.complete_work(work, "dead-worker", {"ok": False},
                              claim_id=claim["claim_id"])


# ---- T6: Foundry restart during active experiment --------------------------

def test_t6_foundry_restart_recovery(db_path):
    f1 = Foundry(db_path)
    c = f1.create_client("c")
    s = f1.create_session(c, "s")
    wid = f1.create_world(s, "w")["world_id"]
    f1.start_world(wid, c)
    w1 = f1.enqueue_work(wid, "job", {"x": 1}, client_id=c)
    w2 = f1.enqueue_work(wid, "job", {"x": 2}, client_id=c)
    done = f1.claim_work("wk", world_id=wid, lease_s=0.05)  # in-flight, short lease
    f1.complete_work(done["work_id"], "wk", {"r": 1},
                     claim_id=done["claim_id"])
    # a second item is left claimed with a short lease, then the Foundry dies
    inflight = f1.claim_work("wk", world_id=wid, lease_s=0.05)
    f1.close()
    time.sleep(0.12)
    f2 = Foundry(db_path)                   # backend restarts
    try:
        assert f2.verify_world(wid)["ok"]                 # ledger intact
        # the in-flight item's lease has expired: it is reclaimable
        reclaim = f2.claim_work("wk2", world_id=wid, lease_s=5.0)
        assert reclaim["work_id"] == inflight["work_id"]
        f2.complete_work(reclaim["work_id"], "wk2", {"r": 2},
                         claim_id=reclaim["claim_id"])
        counts = {r["status"]: r["n"] for r in f2.store.read().execute(
            "SELECT status, COUNT(*) n FROM work_items WHERE world_id=? "
            "GROUP BY status", (wid,)).fetchall()}
        assert counts.get("COMPLETED") == 2 and "CLAIMED" not in counts
    finally:
        f2.close()


# ---- T7: duplicate completion -> exactly one authoritative -----------------

def test_t7_duplicate_completion(foundry):
    c, wid = _mkworld(foundry, "c")
    work = foundry.enqueue_work(wid, "job", {}, client_id=c)
    cl = foundry.claim_work("w1", world_id=wid, lease_s=5.0)
    r1 = foundry.complete_work(work, "w1", {"answer": 1},
                               claim_id=cl["claim_id"])
    with pytest.raises(ConflictError):
        foundry.complete_work(work, "w2", {"answer": 2},
                              claim_id=cl["claim_id"])
    # the authoritative result is w1's, unchanged
    assert foundry.get_work(work)["result"] == {"answer": 1}
    assert foundry.get_work(work)["result_hash"] == r1["result_hash"]


def test_t7_concurrent_claim_is_exclusive(db_path):
    setup = Foundry(db_path)
    c, wid = _mkworld(setup, "c")
    works = [setup.enqueue_work(wid, "job", {"i": i}, client_id=c)
             for i in range(20)]
    setup.close()
    claimed_by = {}
    lock = threading.Lock()

    def worker(name):
        f = Foundry(db_path)
        try:
            while True:
                cl = f.claim_work(name, world_id=wid, lease_s=30)
                if cl is None:
                    return
                with lock:
                    claimed_by.setdefault(cl["work_id"], []).append(name)
                f.complete_work(cl["work_id"], name, {"i": cl["payload"]["i"]},
                                claim_id=cl["claim_id"])
        finally:
            f.close()

    ts = [threading.Thread(target=worker, args=(f"w{i}",)) for i in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert set(claimed_by) == set(works)                  # all claimed
    assert all(len(v) == 1 for v in claimed_by.values())  # each exactly once


# ---- T8: isolation attack --------------------------------------------------

def test_t8_isolation_attack_fails_closed(foundry):
    ca, wa = _mkworld(foundry, "A")
    cb, _ = _mkworld(foundry, "B")
    # knowing wa's id must not grant client B any access
    for call in (
        lambda: foundry.get_world(wa, cb),
        lambda: foundry.world_events(wa, client_id=cb),
        lambda: foundry.propose_hypothesis(wa, "intrude", client_id=cb),
        lambda: foundry.pause_world(wa, cb),
        lambda: foundry.enqueue_work(wa, "job", {}, client_id=cb),
        lambda: foundry.checkpoint(wa, client_id=cb),
        lambda: foundry.consume_budget(wa, "x", 1, client_id=cb),
    ):
        with pytest.raises(AccessDenied):
            call()


# ---- T9: fork isolation ----------------------------------------------------

def test_t9_fork_isolation(foundry):
    c, wid = _mkworld(foundry, "c")
    foundry.propose_hypothesis(wid, "pre-fork", client_id=c)
    ck = foundry.checkpoint(wid, client_id=c)
    kids = foundry.fork(wid, ck["checkpoint_id"],
                        [{"name": "A"}, {"name": "B"}, {"name": "C"}],
                        client_id=c)
    parent_before = foundry.get_world(wid, c)["next_index"]
    sib_before = {k["world_id"]: k["next_index"] for k in kids}
    # mutate ONLY child A
    a = kids[0]["world_id"]
    foundry.start_world(a, c)
    for i in range(5):
        foundry.propose_hypothesis(a, f"A{i}", client_id=c)
    # parent and untouched siblings are unchanged
    assert foundry.get_world(wid, c)["next_index"] == parent_before
    for k in kids[1:]:
        assert foundry.get_world(k["world_id"], c)["next_index"] == \
            sib_before[k["world_id"]]
    # every chain still verifies, and children share the parent prefix
    for k in kids:
        assert foundry.verify_world(k["world_id"])["ok"]
        hist = foundry.world_history(k["world_id"], client_id=c)
        assert any(e["payload"].get("statement") == "pre-fork" for e in hist)


# ---- T10: artifact provenance ---------------------------------------------

def test_t10_artifact_import_provenance(foundry):
    ca = foundry.create_client("c")
    s = foundry.create_session(ca, "s")
    src = foundry.create_world(s, "src", topology_group="grp")["world_id"]
    dst = foundry.create_world(s, "dst", sharing_policy="SUCCESSES_ONLY",
                               topology_group="grp")["world_id"]
    foundry.start_world(src, ca); foundry.start_world(dst, ca)
    art = foundry.create_artifact(src, "result", b"discovered-here",
                                  client_id=ca)
    assert art["origin"] == "NATIVE"
    imp = foundry.import_artifact(dst, src, art["artifact_id"], client_id=ca)
    assert imp["origin"] == "IMPORTED"
    assert imp["source_world"] == src
    stored = foundry.get_artifact(dst, imp["artifact_id"], client_id=ca)
    # provenance is permanent and the import is NOT indistinguishable from native
    assert stored["origin"] == "IMPORTED"
    assert stored["source_world"] == src
    assert stored["source_artifact"] == art["artifact_id"]
    assert any(e["event_type"] == "ARTIFACT_IMPORTED"
               for e in foundry.world_events(dst, client_id=ca))


# ---- T11: prediction ordering / laundering --------------------------------

def test_t11_prediction_must_precede_observation(foundry):
    c, wid = _mkworld(foundry, "c")
    h = foundry.propose_hypothesis(wid, "H", client_id=c)
    exp = foundry.create_experiment(wid, {"r": 1}, client_id=c, hyp_id=h)
    # observe first (no prediction)
    foundry.record_observation(wid, exp["exp_id"], {"got": 1}, "SURVIVED",
                               client_id=c)
    # NOW register a prediction (after the observation) and try to launder it
    late = foundry.register_prediction(wid, h, {"expect": 1}, client_id=c)
    exp2 = foundry.create_experiment(wid, {"r": 2}, client_id=c, hyp_id=h)
    # a legitimately-later observation citing the late prediction is allowed...
    foundry.record_observation(wid, exp2["exp_id"], {"got": 1}, "SURVIVED",
                               client_id=c, pred_id=late)
    # ...but the temporal record exposes that `late` did NOT precede the first
    cx = foundry.store.read()
    ps = cx.execute("SELECT created_seq FROM predictions WHERE pred_id=?",
                    (late,)).fetchone()["created_seq"]
    first_obs = cx.execute(
        "SELECT MIN(created_seq) m FROM observations WHERE world_id=?",
        (wid,)).fetchone()["m"]
    assert ps > first_obs                  # provably post-hoc, detectable


def test_t11_cannot_attach_future_prediction(foundry):
    c, wid = _mkworld(foundry, "c")
    h = foundry.propose_hypothesis(wid, "H", client_id=c)
    exp = foundry.create_experiment(wid, {"r": 1}, client_id=c, hyp_id=h)
    # Referencing a prediction id that does not exist yet is impossible; a
    # prediction created strictly after the observation event cannot be cited by
    # that observation because the observation is immutable. We assert the
    # ordering guard rejects a prediction that does not precede a new obs by
    # constructing the situation directly against the runtime's check.
    late = foundry.register_prediction(wid, h, {"e": 1}, client_id=c)
    # monkey the prediction's created_seq to be AFTER a fresh observation's
    with foundry.store.write() as w:
        w.execute("UPDATE predictions SET created_seq=999999 WHERE pred_id=?",
                  (late,))
    exp2 = foundry.create_experiment(wid, {"r": 2}, client_id=c, hyp_id=h)
    with pytest.raises(PredictionOrderingError):
        foundry.record_observation(wid, exp2["exp_id"], {"got": 1}, "SURVIVED",
                                   client_id=c, pred_id=late)


# ---- T12: budget exhaustion ------------------------------------------------

def test_t12_budget_exhaustion(foundry):
    c, wid = _mkworld(foundry, "c",
                      budget={"experiments": {"limit": 3,
                                              "enforcement": "enforceable"}})
    for _ in range(3):
        foundry.consume_budget(wid, "experiments", 1, client_id=c)
    with pytest.raises(BudgetExhausted):
        foundry.consume_budget(wid, "experiments", 1, client_id=c)
    assert foundry.budget_status(wid)["exhausted"] is True
    assert any(e["event_type"] == "BUDGET_EXHAUSTED"
               for e in foundry.world_events(wid, client_id=c))


def test_t12_measured_budget_is_not_enforced(foundry):
    c, wid = _mkworld(foundry, "c",
                      budget={"tokens": {"limit": 10, "enforcement": "measured"}})
    # measured resources are recorded but NOT blocked (no fabricated enforcement)
    for _ in range(20):
        foundry.consume_budget(wid, "tokens", 1, client_id=c)
    st = foundry.budget_status(wid)
    assert st["consumed"]["tokens"] == 20 and st["exhausted"] is False


# ---- T13: failure lineage --------------------------------------------------

def test_t13_failure_lineage_chain(foundry):
    c, wid = _mkworld(foundry, "c")
    h1 = foundry.propose_hypothesis(wid, "H1", client_id=c)
    exp = foundry.create_experiment(wid, {"r": 1}, client_id=c, hyp_id=h1)
    fid = foundry.record_failure(wid, failure_type="wrong_answer",
                                 falsifier="oracle", violated="spec",
                                 experiment_id=exp["exp_id"],
                                 hypothesis_id=h1, client_id=c)
    h2 = foundry.propose_hypothesis(wid, "H2 (mutated from F1)", client_id=c)
    foundry.consume_failure(wid, fid, "hypothesis", h2, client_id=c)
    exp2 = foundry.create_experiment(wid, {"r": 2}, client_id=c, hyp_id=h2)
    # the whole chain F1 -> H2 -> E2 is reconstructible from recorded edges
    desc = foundry.descendants(wid, "failure", fid)
    ids = {(d["kind"], d["id"]) for d in desc}
    assert ("hypothesis", h2) in ids
    assert ("experiment", exp2["exp_id"]) in ids
    acc = foundry.epistemic_accounting(wid)
    assert acc["failures_generated"] == 1 and acc["failures_consumed"] == 1
    assert acc["mutations_attributed_to_failure"] == 1


# ---- T14: sharing topology -------------------------------------------------

def test_t14_sharing_topology(foundry):
    c = foundry.create_client("c")
    s = foundry.create_session(c, "s")
    src = foundry.create_world(s, "src", topology_group="g")["world_id"]
    iso = foundry.create_world(s, "iso", sharing_policy="ISOLATED",
                               topology_group="g")["world_id"]
    failonly = foundry.create_world(s, "fo", sharing_policy="FAILURES_ONLY",
                                    topology_group="g")["world_id"]
    for w in (src, iso, failonly):
        foundry.start_world(w, c)
    art = foundry.create_artifact(src, "r", b"x", client_id=c)
    # ISOLATED forbids any import
    with pytest.raises(IsolationViolation):
        foundry.import_artifact(iso, src, art["artifact_id"], client_id=c)
    # FAILURES_ONLY forbids importing an ARTIFACT (only 'failure' may cross)
    with pytest.raises(IsolationViolation):
        foundry.import_artifact(failonly, src, art["artifact_id"], client_id=c)


def test_t14_topology_group_barrier(foundry):
    c = foundry.create_client("c")
    s = foundry.create_session(c, "s")
    src = foundry.create_world(s, "src", topology_group="g1")["world_id"]
    dst = foundry.create_world(s, "dst", sharing_policy="SUCCESSES_ONLY",
                               topology_group="g2")["world_id"]
    foundry.start_world(src, c); foundry.start_world(dst, c)
    art = foundry.create_artifact(src, "r", b"x", client_id=c)
    # policy allows artifacts, but the topology groups differ -> barred
    with pytest.raises(IsolationViolation):
        foundry.import_artifact(dst, src, art["artifact_id"], client_id=c)


# ---- T15: ledger corruption ------------------------------------------------

def test_t15_tamper_is_detected(db_path):
    f = Foundry(db_path)
    c, wid = _mkworld(f, "c")
    f.propose_hypothesis(wid, "original", client_id=c)
    assert f.verify_world(wid)["ok"]
    f.close()
    # tamper directly in the database, bypassing the API
    raw = sqlite3.connect(db_path)
    raw.execute("UPDATE events SET payload=? WHERE event_type=? AND world_id=?",
                ('{"statement":"forged"}', "HYPOTHESIS_PROPOSED", wid))
    raw.commit(); raw.close()
    f2 = Foundry(db_path)
    try:
        with pytest.raises(LedgerIntegrityError):
            f2.verify_world(wid)
    finally:
        f2.close()


def test_t15_deleting_an_event_breaks_chain(db_path):
    f = Foundry(db_path)
    c, wid = _mkworld(f, "c")
    for i in range(3):
        f.propose_hypothesis(wid, f"h{i}", client_id=c)
    f.close()
    raw = sqlite3.connect(db_path)
    # remove a middle event -> the next event's prev_hash no longer matches
    raw.execute("DELETE FROM events WHERE world_id=? AND world_index=2", (wid,))
    raw.commit(); raw.close()
    f2 = Foundry(db_path)
    try:
        with pytest.raises(LedgerIntegrityError):
            f2.verify_world(wid)
    finally:
        f2.close()


# ---- T16: deterministic replay --------------------------------------------

def test_t16_deterministic_replay(foundry):
    ex = BitStringExecutor(length=16)
    c, wid = _mkworld(foundry, "c")
    w = foundry.get_world(wid, c)
    from sfe.executors import WorkPackage
    wp = WorkPackage("wk", wid, ex.kind, {"bits": "0101010101010101"},
                     w["seed_root"])
    r1 = ex.execute(wp)
    r2 = ex.execute(wp)
    assert r1.result == r2.result                 # bit-identical
    assert r1.reproducibility == "BIT_DETERMINISTIC"
    # and idempotent completion returns the same authoritative result hash
    work = foundry.enqueue_work(wid, ex.kind, {"bits": "0101010101010101"},
                                client_id=c)
    cl = foundry.claim_work("w1", world_id=wid, lease_s=30)
    a = foundry.complete_work(work, "w1", r1.result, claim_id=cl["claim_id"])
    b = foundry.complete_work(work, "w1", r1.result, claim_id=cl["claim_id"])
    assert a["result_hash"] == b["result_hash"]


# ---- T17: nondeterministic replay is NOT claimed deterministic -------------

def test_t17_nondeterministic_not_falsely_deterministic(owned_world):
    f, c, wid = owned_world
    ex = NondeterministicExecutor()
    from sfe.executors import WorkPackage
    w = f.get_world(wid, c)
    wp = WorkPackage("wk", wid, ex.kind, {}, w["seed_root"])
    r1 = ex.execute(wp)
    r2 = ex.execute(wp)
    assert r1.result != r2.result                 # genuinely differs
    # the Foundry records the honest label; it never asserts determinism here
    assert r1.reproducibility == "NONDETERMINISTIC"


# ---- T18: load / ceiling ---------------------------------------------------

def test_t18_load_ceiling(db_path):
    N_WORLDS, PER_WORLD, N_WORKERS = 20, 15, 10
    setup = Foundry(db_path)
    c = setup.create_client("c")
    s = setup.create_session(c, "s")
    worlds = []
    for _ in range(N_WORLDS):
        wid = setup.create_world(s, "w")["world_id"]
        setup.start_world(wid, c)
        for i in range(PER_WORLD):
            setup.enqueue_work(wid, BitStringExecutor.kind,
                               {"bits": format(i, "016b")}, client_id=c)
        worlds.append(wid)
    setup.close()
    total = N_WORLDS * PER_WORLD

    completed = []
    lock = threading.Lock()

    def worker(name):
        f = Foundry(db_path)
        loop = WorkerLoop(f, name, [BitStringExecutor(length=16)], lease_s=30)
        try:
            n = loop.run_until_idle()
            with lock:
                completed.append(n)
        finally:
            f.close()

    t0 = time.time()
    ts = [threading.Thread(target=worker, args=(f"w{i}",))
          for i in range(N_WORKERS)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    elapsed = time.time() - t0

    check = Foundry(db_path)
    try:
        done = check.store.read().execute(
            "SELECT COUNT(*) n FROM work_items WHERE status='COMPLETED'"
        ).fetchone()["n"]
        # every unit completed exactly once (no double-commit under contention)
        assert done == total, (done, total)
        assert sum(completed) == total
        throughput = total / elapsed if elapsed else float("inf")
        print(f"\n[T18] {total} units / {N_WORKERS} workers / {N_WORLDS} worlds "
              f"in {elapsed:.2f}s -> {throughput:.0f} units/s (basement ceiling)")
    finally:
        check.close()
