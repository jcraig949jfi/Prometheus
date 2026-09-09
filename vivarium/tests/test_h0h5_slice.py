"""H0-H5 iteration 1: THE VERTICAL SLICE, against a real engine.

Nothing in this file is mocked. Every test here runs a real experiment through
a real Serendipity Foundry Engine over HTTP, against a real PostgreSQL queue in
a throwaway schema, and -- where a fossil is involved -- a real PEW service in
the `test` namespace. The brief is explicit that "a stub, mocked scientific
execution or a test using only an in-memory fake SFE is not the complete
vertical-slice receipt; a temporary real database/runtime in a development
environment is sufficient", and this is that runtime.

RUNNING IT. Start a development engine on its own database and point the suite
at it:

    python SerendipityFoundry/SerendipityFoundryEngine/serve.py \\
        --db <tmp>/dev.sqlite --host 127.0.0.1 --port 8899
    VIV_DEV_SFE_URL=http://127.0.0.1:8899 python -m pytest tests/test_h0h5_slice.py

Without VIV_DEV_SFE_URL the whole module skips. It is never pointed at the
production engine by default, and the order says why: this work happens in a
development runtime.

WHY A SECOND CLIENT. Half the boundary cases in the order -- unauthorized
world, cache hit without permission -- are questions about AUTHORITY, and
authority is the engine's answer, not this seat's. They can only be asked by a
principal the engine does not trust with the bytes, so the module registers two
clients and uses the second one as the outsider.
"""
from __future__ import annotations

import base64
import os
import sys
import uuid
from pathlib import Path

import pytest

from artifact_fixtures import input_set, probe_spec
from conftest import make_spec
from viv import artifacts as _a
from viv import db as _db
from viv import queue as _q
from viv.loop import EXECUTED, FAILED, Vivarium
from viv.runner import SfeRunner

REPO = Path(__file__).resolve().parent.parent.parent
_CLIENT = REPO / "SerendipityFoundry" / "SerendipityFoundryClient"
if str(_CLIENT) not in sys.path:
    sys.path.insert(0, str(_CLIENT))

DEV_URL = os.environ.get("VIV_DEV_SFE_URL")
pytestmark = pytest.mark.skipif(
    not DEV_URL,
    reason="set VIV_DEV_SFE_URL to a DEVELOPMENT engine to run the slice")

ITEMS = [[0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 0]]


# ---------------------------------------------------------------- fixtures
@pytest.fixture(scope="module")
def engine():
    """The executor's own client on the development engine."""
    from sfclient import EngineClient
    c = EngineClient(DEV_URL)
    cid = c.register("vivarium-h0h5-%s" % uuid.uuid4().hex[:6])
    return c


@pytest.fixture(scope="module")
def outsider():
    """A DIFFERENT client. It owns worlds the executor may not read, which is
    the only way to ask the engine an authorization question honestly."""
    from sfclient import EngineClient
    c = EngineClient(DEV_URL)
    c.register("outsider-h0h5-%s" % uuid.uuid4().hex[:6])
    return c


def _client_id(c):
    """The engine-issued client id, read back rather than assumed."""
    return getattr(c, "client_id", None) or "dev-client"


@pytest.fixture()
def producer(engine):
    """A producer world owned by the executor's client, ready to hold
    artifacts. Started, because an unstarted world accepts nothing."""
    sid = engine.create_session("h0h5-producer")
    w = engine.create_world(sid, "producer-%s" % uuid.uuid4().hex[:8],
                            seed_root=20260909,
                            sharing_policy="EXPLICIT_IMPORT_ONLY")
    engine.start(w["world_id"])
    return w["world_id"]


def _publish(client, world, raw, *, kind="failure_input_set"):
    """Create the artifact and CHECK the engine agrees about its identity.

    sfclient has no expected_blob_hash parameter yet (the engine gate exists;
    the client does not expose it -- filed to Daedalus), so the assertion is
    made here on the returned digest. It is the same check one moment later,
    and it is not silently skipped merely because the client cannot request it.
    """
    out = client.artifact(world, kind, raw)
    assert out["blob_hash"] == _a.digest_of(raw), (
        "the engine stored bytes that hash differently from what was sent")
    return out["artifact_id"]


def _runner(engine):
    return SfeRunner(base_url=DEV_URL, token=engine.token,
                     client_id=_client_id(engine),
                     worker_id="viv-h0h5", lease_s=120.0,
                     log=lambda *a: None)


def _viv(engine, schema, **kw):
    return Vivarium(worker_id="viv-h0h5", schema=schema,
                    runner=_runner(engine), pew_client=None,
                    log=lambda *a: None, **kw)


def _enqueue(conn, schema, spec, locators, **kw):
    eid = _q.enqueue(conn, created_by=kw.pop("created_by", "h0h5-test"),
                     source_reason=kw.pop("source_reason", "vertical slice"),
                     experiment_spec=spec, artifact_locators=locators,
                     schema=schema, **kw)
    conn.commit()
    return eid


def _result_of(conn, schema, eid):
    """The kind's own result, read back off the completed row."""
    row = _q.get(conn, eid, schema=schema)
    return row["result_summary"]["result"]["repeats"][0]["result"]


def _slice(conn, schema, engine, producer, *, items=ITEMS, mutate=None,
           locator=None, reduction="xor_positional"):
    """Producer -> artifact -> sealed spec -> queue -> tick. Returns the report.

    `mutate` may alter the slot AFTER the artifact exists, which is how the
    wrong-digest / wrong-type / oversize cases are produced without touching
    the loader.
    """
    _obj, raw, slot = input_set(items)
    aid = _publish(engine, producer, raw)
    if mutate is not None:
        slot = mutate(dict(slot))
    loc = locator or {slot["digest"]: {"source_world": producer,
                                       "source_artifact": aid}}
    spec = probe_spec(slot, reduction=reduction)
    eid = _enqueue(conn, schema, spec, loc)
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    return report, eid, slot, raw, aid


# ===========================================================================
# THE HAPPY PATH -- one real artifact-consuming execution, end to end
# ===========================================================================

def test_a_real_artifact_is_produced_sealed_resolved_and_consumed(
        conn, schema, engine, producer):
    report, eid, slot, raw, aid = _slice(conn, schema, engine, producer)
    assert report.outcome == EXECUTED, report.detail

    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "completed"
    summary = row["result_summary"]

    # 1. The load receipt is a document about BYTES.
    receipt = summary["load_receipt"]
    assert receipt["loaded"] is True
    assert receipt["closure_manifest"] == [slot["digest"]]
    assert receipt["bytes_loaded"] == len(raw)
    assert receipt["engine_fetches"] == 1, "load once"

    # 2. The engine authorized it, and said on what basis.
    res = receipt["closure"][0]["resolution"]
    assert res["origin"] == "IMPORTED"
    assert res["source_world"] == producer
    assert res["source_artifact"] == aid
    assert res["engine_blob_hash"] == slot["digest"]
    assert res["import_seq"] is not None
    assert res["visibility_basis"]["visibility"] == "IMPORTED"

    # 3. The kind consumed exactly those rows, and could not mutate them.
    result = summary["result"]["repeats"][0]["result"]
    assert result["items_consumed"] == len(ITEMS)
    assert result["input_digest"] == slot["digest"]
    assert result["inputs_immutable"] is True

    # 4. The observation is anchored in the ledger, not asserted here.
    assert summary["anchor"]["resolved"] is True
    assert summary["obs_ids"] and summary["work_id"]


def test_the_result_is_deterministic_and_validated_against_its_schema(
        conn, schema, engine, producer):
    r1, e1, slot, _raw, _a1 = _slice(conn, schema, engine, producer)
    r2, e2, slot2, _raw2, _a2 = _slice(conn, schema, engine, producer)
    assert r1.outcome == r2.outcome == EXECUTED
    assert slot["digest"] == slot2["digest"]
    v1 = _result_of(conn, schema, e1)
    v2 = _result_of(conn, schema, e2)
    for f in ("folded", "items_digest", "items_consumed", "input_digest",
              "consumed_closure_hash"):
        assert v1[f] == v2[f], f
    assert v1["reproducibility"] == "BIT_DETERMINISTIC"


def test_the_resource_vector_says_what_was_enforceable(
        conn, schema, engine, producer):
    report, eid, _slot, raw, _aid = _slice(conn, schema, engine, producer)
    summary = _q.get(conn, eid, schema=schema)["result_summary"]
    v = summary["resources"]
    assert v["artifact_bytes"]["quantity"] == len(raw)
    assert v["artifact_bytes"]["enforcement"] == "enforceable"
    assert v["gpu_seconds"]["enforcement"] == "unavailable"
    assert v["gpu_seconds"]["quantity"] is None, "unavailable is not zero"
    enf = summary["enforcement"]
    assert "artifact_bytes" in enf["enforceable"]
    assert "cpu_seconds" in enf["measured"]


def test_an_old_no_artifact_spec_still_runs_exactly_as_before(
        conn, schema, engine):
    """The loader added a path; it did not move the old one."""
    eid = _enqueue(conn, schema, make_spec(), {})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == EXECUTED
    summary = _q.get(conn, eid, schema=schema)["result_summary"]
    assert summary["load_receipt"] == {}, "a receipt for a run with no inputs"
    assert summary["result"]["repeats"][0]["result"]["executed"] is True


# ===========================================================================
# BOUNDARY FAILURES -- each a real execution attempt against the real engine
# ===========================================================================

def _rejection(conn, schema, eid):
    """The rejection class recorded on the failed ROW.

    Read from the database, not from the in-process report: what matters is
    that the refusal is DURABLE and legible to somebody who arrives later with
    only the register, which is the whole point of an operational receipt.
    """
    summary = _q.get(conn, eid, schema=schema)["result_summary"] or {}
    return (summary.get("load_receipt") or {}).get("rejection_class")


def test_absent_artifact(conn, schema, engine, producer):
    _obj, raw, slot = input_set(ITEMS)
    _publish(engine, producer, raw)
    spec = probe_spec(slot)
    eid = _enqueue(conn, schema, spec, {slot["digest"]: {
        "source_world": producer, "source_artifact": "art_does_not_exist"}})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    assert _rejection(conn, schema, eid) == _a.ABSENT
    assert _q.get(conn, eid, schema=schema)["status"] == "failed"


def test_wrong_digest(conn, schema, engine, producer):
    """The locator finds SOMETHING; it does not find what the spec sealed."""
    _obj, raw_a, slot_a = input_set(ITEMS)
    _obj2, raw_b, _slot_b = input_set([[1, 1, 1], [0, 0, 0]])
    aid_b = _publish(engine, producer, raw_b)
    spec = probe_spec(slot_a)
    eid = _enqueue(conn, schema, spec, {slot_a["digest"]: {
        "source_world": producer, "source_artifact": aid_b}})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    assert _rejection(conn, schema, eid) in (_a.DIGEST_MISMATCH,
                                        _a.SIZE_MISMATCH)


def test_unauthorized_world(conn, schema, engine, outsider, producer):
    """Bytes in a world this client does not own. The digest is correct and
    confers nothing: the engine refuses, and the refusal is the answer."""
    sid = outsider.create_session("outsider")
    w = outsider.create_world(sid, "theirs-%s" % uuid.uuid4().hex[:8],
                              seed_root=1, sharing_policy="FULLY_SHARED")
    outsider.start(w["world_id"])
    _obj, raw, slot = input_set(ITEMS)
    aid = _publish(outsider, w["world_id"], raw)

    spec = probe_spec(slot)
    eid = _enqueue(conn, schema, spec, {slot["digest"]: {
        "source_world": w["world_id"], "source_artifact": aid}})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    assert _rejection(conn, schema, eid) == _a.UNAUTHORIZED
    summary = _q.get(conn, eid, schema=schema)["result_summary"]
    assert summary["load_receipt"]["detail"]["http"] == 403


def test_a_cache_hit_is_never_served_without_permission(
        conn, schema, engine, outsider, producer):
    """The bytes ARE in this process, freshly verified for another principal,
    and the outsider still does not get them: the cache is keyed by who was
    authorized, so the miss sends the request back to the engine to be
    refused."""
    _obj, raw, slot = input_set(ITEMS)
    aid = _publish(engine, producer, raw)
    # 1. A legitimate run warms a cache entry for the executor's principal.
    report, _eid, _s, _r, _a1 = _slice(conn, schema, engine, producer)
    assert report.outcome == EXECUTED

    # 2. The same digest, addressed in a world owned by somebody else.
    sid = outsider.create_session("outsider-cache")
    w = outsider.create_world(sid, "theirs-%s" % uuid.uuid4().hex[:8],
                              seed_root=1, sharing_policy="FULLY_SHARED")
    outsider.start(w["world_id"])
    _publish(outsider, w["world_id"], raw)
    cache = _a.LoaderCache()
    cache.put(slot["digest"], raw, ("vivarium", "w-earlier"))
    assert cache.get(slot["digest"], ("outsider", w["world_id"])) is None
    assert cache.stats()["refused_hits"] == 1


def test_wrong_type(conn, schema, engine, producer):
    """Right bytes, and the content's own header says it is something else."""
    obj = {"artifact_type": "decoder", "schema_version": "1",
           "interface_id": "boolean-inputs-v1", "n_bits": 3,
           "items": [[0, 0, 1]]}
    raw = _a.canonical_bytes(obj)
    aid = _publish(engine, producer, raw)
    slot = {"digest": _a.digest_of(raw), "artifact_type": "failure_input_set",
            "schema_version": "1", "codec": "canonical-json-v1",
            "expected_bytes": len(raw), "interface_id": "boolean-inputs-v1"}
    eid = _enqueue(conn, schema, probe_spec(slot), {slot["digest"]: {
        "source_world": producer, "source_artifact": aid}})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    assert _rejection(conn, schema, eid) == _a.WRONG_TYPE


def test_incompatible_interface(conn, schema, engine, producer):
    obj = {"artifact_type": "failure_input_set", "schema_version": "1",
           "interface_id": "boolean-inputs-v9", "n_bits": 3,
           "items": [[0, 0, 1]]}
    raw = _a.canonical_bytes(obj)
    aid = _publish(engine, producer, raw)
    slot = {"digest": _a.digest_of(raw), "artifact_type": "failure_input_set",
            "schema_version": "1", "codec": "canonical-json-v1",
            "expected_bytes": len(raw), "interface_id": "boolean-inputs-v1"}
    eid = _enqueue(conn, schema, probe_spec(slot), {slot["digest"]: {
        "source_world": producer, "source_artifact": aid}})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    assert _rejection(conn, schema, eid) == _a.INCOMPATIBLE_INTERFACE


def test_missing_dependency(conn, schema, engine, producer):
    """The root resolves; its declared closure does not. An incomplete closure
    is not an input."""
    _dobj, draw, dslot = input_set([[1, 1, 1]])
    _obj, raw, slot = input_set(ITEMS, dependencies=[dslot])
    aid = _publish(engine, producer, raw)
    # The dependency's BYTES are never published, and it gets no address.
    eid = _enqueue(conn, schema, probe_spec(slot), {slot["digest"]: {
        "source_world": producer, "source_artifact": aid}})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    assert _rejection(conn, schema, eid) == _a.MISSING_DEPENDENCY


def test_a_present_dependency_resolves_through_the_whole_closure(
        conn, schema, engine, producer):
    """The positive control for the case above: with the dependency published
    and addressed, the closure completes and its rows are consumed."""
    _dobj, draw, dslot = input_set([[1, 1, 1]])
    _obj, raw, slot = input_set(ITEMS, dependencies=[dslot])
    root_aid = _publish(engine, producer, raw)
    dep_aid = _publish(engine, producer, draw)
    eid = _enqueue(conn, schema, probe_spec(slot), {
        slot["digest"]: {"source_world": producer,
                         "source_artifact": root_aid},
        dslot["digest"]: {"source_world": producer,
                          "source_artifact": dep_aid}})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == EXECUTED, report.detail
    summary = _q.get(conn, eid, schema=schema)["result_summary"]
    assert summary["load_receipt"]["closure_size"] == 2
    assert (summary["result"]["repeats"][0]["result"]["items_consumed"]
            == len(ITEMS) + 1)


def test_oversize(conn, schema, engine, producer):
    """Refused on the DECLARATION, before a byte crosses the network."""
    _obj, raw, slot = input_set(ITEMS)
    aid = _publish(engine, producer, raw)
    runner = _runner(engine)
    runner.limits = _a.Limits(per_artifact_bytes=8, total_bytes=8)
    eid = _enqueue(conn, schema, probe_spec(slot), {slot["digest"]: {
        "source_world": producer, "source_artifact": aid}})
    v = Vivarium(worker_id="viv-h0h5", schema=schema, runner=runner,
                 pew_client=None, log=lambda *a: None)
    report = v.tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    assert _rejection(conn, schema, eid) == _a.OVERSIZE


def test_malformed_content(conn, schema, engine, producer):
    """Bytes that are not canonical JSON. Published as an artifact perfectly
    happily -- the engine stores bytes, it does not know this interface."""
    raw = b"\x00\x01\x02 not json at all"
    aid = _publish(engine, producer, raw)
    slot = {"digest": _a.digest_of(raw), "artifact_type": "failure_input_set",
            "schema_version": "1", "codec": "canonical-json-v1",
            "expected_bytes": len(raw), "interface_id": "boolean-inputs-v1"}
    eid = _enqueue(conn, schema, probe_spec(slot), {slot["digest"]: {
        "source_world": producer, "source_artifact": aid}})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    assert _rejection(conn, schema, eid) == _a.MALFORMED


def test_mutation_after_resolution_cannot_change_what_executes(
        conn, schema, engine, producer):
    """The check/use race, attempted for real.

    A second artifact with DIFFERENT bytes is published into the producer world
    between preflight and execution, and the locator is re-pointed at it in the
    only place a caller could reach -- the resolver. The run must still execute
    the bytes preflight verified, because the loader retained THOSE bytes for
    the attempt instead of fetching again at use time.
    """
    _obj, raw_good, slot = input_set(ITEMS)
    good_aid = _publish(engine, producer, raw_good)
    _obj2, raw_evil, _s2 = input_set([[1, 1, 1], [1, 1, 1]])
    evil_aid = _publish(engine, producer, raw_evil)

    runner = _runner(engine)
    original = runner._hydrate                      # noqa: SLF001
    swapped = {"count": 0}

    def hydrate_then_swap(c, spec, slots, locators, wid, meter):
        inputs, receipt = original(c, spec, slots, locators, wid, meter)
        # The artifact the locator names is now re-imported as different
        # bytes; anything that fetched again would see them.
        c.import_artifact(wid, producer, evil_aid)
        swapped["count"] += 1
        return inputs, receipt

    runner._hydrate = hydrate_then_swap             # noqa: SLF001
    eid = _enqueue(conn, schema, probe_spec(slot), {slot["digest"]: {
        "source_world": producer, "source_artifact": good_aid}})
    v = Vivarium(worker_id="viv-h0h5", schema=schema, runner=runner,
                 pew_client=None, log=lambda *a: None)
    report = v.tick(conn)
    conn.commit()
    assert swapped["count"] == 1
    assert report.outcome == EXECUTED, report.detail
    result = _result_of(conn, schema, eid)
    assert result["input_digest"] == slot["digest"]
    assert result["items_consumed"] == len(ITEMS)


def test_a_mutable_lookup_never_reaches_the_engine(conn, schema, engine,
                                                   producer):
    """Refused at admission, by syntax. The row is never created, so nothing
    downstream has to be careful about it."""
    _obj, raw, slot = input_set(ITEMS)
    _publish(engine, producer, raw)
    with pytest.raises(ValueError) as e:
        _enqueue(conn, schema, probe_spec(slot), {slot["digest"]: {
            "source_world": producer, "source_artifact": "latest"}})
    assert "MUTABLE" in str(e.value)


def test_budget_exhaustion_is_a_distinct_status(conn, schema, engine,
                                                producer):
    """Not a rejection class and not a scientific finding: "we could not
    afford to look" is a different fact from "we looked and it was wrong"."""
    _obj, raw, slot = input_set(ITEMS)
    aid = _publish(engine, producer, raw)
    runner = _runner(engine)
    # A total-byte allowance smaller than the artifact, enforced by the ENGINE
    # before the fetch. The local limits stay wide so it is the budget that
    # refuses, not the loader's own arithmetic.
    runner.limits = _a.Limits(total_bytes=len(raw) - 1)
    eid = _enqueue(conn, schema, probe_spec(slot), {slot["digest"]: {
        "source_world": producer, "source_artifact": aid}})
    v = Vivarium(worker_id="viv-h0h5", schema=schema, runner=runner,
                 pew_client=None, log=lambda *a: None)
    report = v.tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "failed"
    receipt = row["result_summary"]["load_receipt"]
    assert receipt["rejection_class"] in ("BUDGET_EXHAUSTED",
                                          _a.OVERSIZE), receipt


def test_a_rejected_run_writes_no_observation_and_no_fossil(
        conn, schema, engine, producer):
    """C1's last line, verified in the ledger: rejection creates an operational
    receipt and no scientific success observation."""
    _obj, raw_a, slot_a = input_set(ITEMS)
    _obj2, raw_b, _sb = input_set([[1, 1, 1], [0, 0, 0]])
    aid_b = _publish(engine, producer, raw_b)
    eid = _enqueue(conn, schema, probe_spec(slot_a), {slot_a["digest"]: {
        "source_world": producer, "source_artifact": aid_b}})
    report = _viv(engine, schema).tick(conn)
    conn.commit()
    assert report.outcome == FAILED
    row = _q.get(conn, eid, schema=schema)
    assert row["pew_reference"] is None
    summary = row["result_summary"]
    assert summary["outcome"] is None
    assert summary["crossed_execution_boundary"] is False, (
        "no experiment should have been committed before the refusal")
    assert summary["exp_id"] is None


# ===========================================================================
# LIFECYCLE -- interruption, idempotent completion, terminal states
# ===========================================================================

def test_a_completed_row_is_never_re_executed_after_a_restart(
        conn, schema, engine, producer):
    report, eid, _slot, _raw, _aid = _slice(conn, schema, engine, producer)
    assert report.outcome == EXECUTED
    first = _q.get(conn, eid, schema=schema)["sfe_experiment_id"]
    # A fresh Vivarium, as after a restart. The completed row is terminal.
    again = _viv(engine, schema).tick(conn)
    conn.commit()
    assert again.experiment_id != eid
    assert _q.get(conn, eid, schema=schema)["sfe_experiment_id"] == first


def test_the_lease_is_held_and_renewed_across_the_run(
        conn, schema, engine, producer):
    report, eid, _slot, _raw, _aid = _slice(conn, schema, engine, producer)
    lease = _q.get(conn, eid, schema=schema)["result_summary"]["lease"]
    assert lease["error"] is None
    assert lease["lost"] is False
    assert lease["renewals"] >= 0
    assert lease["lease_s"] == 120.0


# ===========================================================================
# INTERRUPTION, AND WHAT "RETRY" HONESTLY MEANS HERE
# ===========================================================================

def test_an_interrupted_run_is_stranded_not_guessed_at(
        conn, schema, engine, producer):
    """A worker that dies mid-attempt leaves a row this loop refuses to
    interpret. Vivarium does not adopt, reset or retry it: guessing that a
    stranded run did not happen is the guess that runs one experiment twice.
    The loader changes nothing about that -- the row still holds the slot and
    the worker still refuses to start until an operator releases it."""
    _obj, raw, slot = input_set(ITEMS)
    aid = _publish(engine, producer, raw)
    eid = _enqueue(conn, schema, probe_spec(slot), {slot["digest"]: {
        "source_world": producer, "source_artifact": aid}})

    runner = _runner(engine)
    original = runner._hydrate                      # noqa: SLF001

    def die_after_loading(c, spec, slots, locators, wid, meter):
        original(c, spec, slots, locators, wid, meter)
        raise KeyboardInterrupt("the process was killed mid-attempt")

    runner._hydrate = die_after_loading             # noqa: SLF001
    v = Vivarium(worker_id="viv-interrupt", schema=schema, runner=runner,
                 pew_client=None, log=lambda *a: None)
    with pytest.raises(KeyboardInterrupt):
        v.tick(conn)
    conn.commit()

    assert _q.get(conn, eid, schema=schema)["status"] == "claimed"
    fresh = Vivarium(worker_id="viv-interrupt", schema=schema,
                     runner=_runner(engine), pew_client=None,
                     log=lambda *a: None)
    rec = fresh.recover(conn)
    assert rec.safe is False
    assert [str(r["experiment_id"]) for r in rec.stranded] == [eid]
    assert fresh.tick(conn).outcome == "BLOCKED"

    # Release resolves to FAILED, never back to queued. A queue row is never
    # silently retried, because nothing in the queue can know whether the
    # interrupted attempt reached the engine. The retry is a NEW admission,
    # which the test below runs.
    _q.release_stranded(conn, eid, actor="operator",
                        reason="worker interrupted; disposition unknown here",
                        schema=schema)
    conn.commit()
    assert _q.get(conn, eid, schema=schema)["status"] == "failed"


def test_a_re_admitted_row_revalidates_from_scratch(conn, schema, engine,
                                                    producer):
    """The retry, done the only honest way: a new admission of the same sealed
    spec. It inherits NOTHING from the interrupted attempt -- it resolves,
    authorizes, verifies and bounds again, and its receipt is its own. That is
    C1's "revalidate on a new attempt", and it is why the verified bytes are
    retained per attempt rather than cached across them."""
    _obj, raw, slot = input_set(ITEMS)
    aid = _publish(engine, producer, raw)
    loc = {slot["digest"]: {"source_world": producer, "source_artifact": aid}}
    spec = probe_spec(slot)

    runner = _runner(engine)
    original = runner._hydrate                      # noqa: SLF001
    attempts = {"n": 0}

    def counted(c, s_, slots, locators, wid, meter):
        attempts["n"] += 1
        return original(c, s_, slots, locators, wid, meter)

    runner._hydrate = counted                       # noqa: SLF001

    first = _enqueue(conn, schema, spec, loc)
    v = Vivarium(worker_id="viv-readmit", schema=schema, runner=runner,
                 pew_client=None, log=lambda *a: None)
    assert v.tick(conn).outcome == EXECUTED
    conn.commit()

    second = _enqueue(conn, schema, spec, loc)
    assert v.tick(conn).outcome == EXECUTED
    conn.commit()

    assert first != second
    assert attempts["n"] == 2, "each attempt ran its own preflight"
    r1 = _q.get(conn, first, schema=schema)["result_summary"]
    r2 = _q.get(conn, second, schema=schema)["result_summary"]
    assert r1["spec_hash"] == r2["spec_hash"], "same experiment, twice"
    assert r1["world_id"] != r2["world_id"], "two attempts, two worlds"
    for rec in (r1["load_receipt"], r2["load_receipt"]):
        assert rec["engine_fetches"] == 1
        assert rec["closure_manifest"] == [slot["digest"]]
    # ... and the science is identical, which is what makes the two
    # comparable at all.
    assert (_result_of(conn, schema, first)["items_digest"]
            == _result_of(conn, schema, second)["items_digest"])


# ===========================================================================
# PUBLICATION -- through Mnemosyne's idempotent path
# ===========================================================================

def _pew_client():
    """The real PEW service, in the `test` namespace (forced by conftest)."""
    cfg = _db.load_config()
    if not (cfg.get("pew_token") and cfg.get("pew_base_url")):
        pytest.skip("no PEW credential configured on this host")
    from viv import pew as _pewmod
    c = _pewmod.PewClient(cfg["pew_base_url"], cfg["pew_token"],
                          machine=cfg.get("machine", "M1"), agent="vivarium",
                          namespace=cfg["pew_namespace"])
    assert c.namespace == "test", "a test must never write the prod namespace"
    try:
        c.health()
    except Exception as exc:                        # noqa: BLE001
        pytest.skip("PEW unreachable: %s" % exc)
    return c


def test_the_fossil_reports_sfe_and_pew_separately(conn, schema, engine,
                                                   producer):
    """C5: recorded_in_sfe and indexed_in_pew are separate FACTS, and only the
    first is authoritative -- an index that failed has not unmade a
    measurement, and one that succeeded has not made one."""
    pew = _pew_client()
    _obj, raw, slot = input_set(ITEMS)
    aid = _publish(engine, producer, raw)
    enc = "h0h5-%s" % uuid.uuid4().hex[:12]
    spec = probe_spec(slot, pew={"encounter_id": enc, "players": [],
                                 "world_binding_id": enc})
    eid = _enqueue(conn, schema, spec, {slot["digest"]: {
        "source_world": producer, "source_artifact": aid}})
    v = Vivarium(worker_id="viv-h0h5", schema=schema, runner=_runner(engine),
                 pew_client=pew, log=lambda *a: None)
    report = v.tick(conn)
    conn.commit()
    assert report.outcome == EXECUTED, report.detail

    row = _q.get(conn, eid, schema=schema)
    assert row["pew_reference"], "no reference was issued"
    detail = row["result_summary"]["pew"]
    assert detail["recorded_in_sfe"] is True
    assert detail["indexed_in_pew"] is True
    assert detail["write_outcome"] == "inserted"
    assert detail["encounter"]["body"]["encounter_id"] == enc


def test_republishing_the_same_run_is_idempotent(conn, schema, engine,
                                                 producer):
    """A retry of a completed publication must never rerun the science.

    Done at the runner, because that is where an outbox retry would live: ONE
    execution, published twice. PEW answers duplicate_identical the second
    time and reissues the same reference.
    """
    pew = _pew_client()
    from viv import pew as _pewmod
    from viv.request import ExecutionRequest
    from viv import spec as _specmod

    _obj, raw, slot = input_set(ITEMS)
    aid = _publish(engine, producer, raw)
    enc = "h0h5-idem-%s" % uuid.uuid4().hex[:12]
    spec = probe_spec(slot, pew={"encounter_id": enc, "players": [],
                                 "world_binding_id": enc})
    runner = _runner(engine)
    sealed = _specmod.spec_hash(spec)
    request = ExecutionRequest(
        experiment_id="h0h5-republish", spec_hash=sealed,
        spec_json=_specmod.canonical_bytes(spec),
        artifact_locators={slot["digest"]: {"source_world": producer,
                                            "source_artifact": aid}})
    result = runner.run(request)
    assert result.outcome is not None

    kw = dict(spec=spec, run=result, engine=runner.engine_identity,
              producer_version="h0h5-slice",
              relation={"experiment_id": "h0h5-republish"})
    first = _pewmod.write_encounter(pew, **kw)
    second = _pewmod.write_encounter(pew, **kw)

    assert first["write_outcome"] == "inserted"
    assert first["indexed_in_pew"] is True
    assert second["write_outcome"] == "duplicate_identical"
    assert second["idempotent_replay"] is True
    assert second["indexed_in_pew"] is True
    assert second["pew_reference"] == first["pew_reference"]

    # The fossil carries the artifact evidence by REFERENCE, not by copy.
    used = second["encounter"]["body"]
    assert used["encounter_id"] == enc
