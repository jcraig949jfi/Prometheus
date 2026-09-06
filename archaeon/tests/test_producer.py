"""Producer component tests.

Every component is exercised on its own, then tick(), then the loop. The
session conftest redirects VIV_SCHEMA to a throwaway schema, so nothing here
touches the production register -- a protection added after these tests wrote
245 rows into it and a live Vivarium cycle claimed one.
"""
from __future__ import annotations

import json
import os
import uuid

import pytest

from archaeon import config as cfg
from archaeon.producer import contract, loop, randomgen, readers, specbuild
from archaeon.producer import tick as tickmod

psycopg2 = pytest.importorskip("psycopg2")


def _connect():
    try:
        from evidence_wiki.ew import db as ewdb
        return ewdb.connect()
    except Exception as exc:                       # pragma: no cover
        pytest.skip("PostgreSQL unavailable: {}".format(exc))


@pytest.fixture
def conn():
    c = _connect()
    yield c
    c.close()


@pytest.fixture
def lane(conn):
    name = "test-{}".format(uuid.uuid4().hex[:8])
    yield name
    from archaeon import vivqueue as vq
    cur = conn.cursor()
    cur.execute("DELETE FROM archaeon.cadence_log WHERE lane = %s", (name,))
    cur.execute("DELETE FROM {q} WHERE cadence_lane = %s".format(q=vq.QUEUE),
                (name,))
    cur.execute("DELETE FROM archaeon.cadence_gate WHERE lane = %s", (name,))
    conn.commit()


def _cfg(lane):
    return cfg.ArchaeonConfig(cadence=cfg.CadenceConfig(lane=lane))


# --------------------------------------------------------------------------
# THE PROTECTION ITSELF
# --------------------------------------------------------------------------
def test_tests_do_not_target_the_production_schema():
    """The single most important test in this file."""
    assert os.environ.get("VIV_SCHEMA", "").startswith("viv_archaeon_test_"), \
        "VIV_SCHEMA is not a throwaway schema; these tests would write to the " \
        "production register"


def test_the_writer_resolves_the_test_schema():
    from archaeon import vivqueue as vq
    assert str(vq.QUEUE).startswith(os.environ["VIV_SCHEMA"] + ".")


def test_the_precondition_checks_the_same_schema_it_writes_to(conn):
    """A precondition pinned to 'viv' would report healthy while the writer
    wrote elsewhere -- verifying the wrong object is worse than not checking."""
    from archaeon import vivqueue as vq
    vq.assert_queue_ready(conn)                    # must not raise
    assert os.environ["VIV_SCHEMA"] in str(vq.QUEUE)


# --------------------------------------------------------------------------
# CONTRACT
# --------------------------------------------------------------------------
def test_archaeon_emits_a_kind_vivarium_can_actually_execute():
    r = contract.check_against_vivarium()
    assert r["agrees"], r
    assert r["implemented"] is True


def test_retired_kind_is_not_emitted():
    assert "archaeon.probe.v0" in contract.RETIRED_KINDS
    assert contract.KIND != "archaeon.probe.v0"


# --------------------------------------------------------------------------
# RANDOM GENERATOR
# --------------------------------------------------------------------------
def test_random_draw_is_reproducible_from_its_seed():
    a = randomgen.draw("lane1", "2026-09-06")
    b = randomgen.draw("lane1", "2026-09-06")
    assert a["seed"] == b["seed"] and a["params"] == b["params"]


def test_random_draw_varies_with_lane_day_and_nonce():
    base = randomgen.draw("lane1", "2026-09-06")["seed"]
    assert randomgen.draw("lane2", "2026-09-06")["seed"] != base
    assert randomgen.draw("lane1", "2026-09-07")["seed"] != base
    assert randomgen.draw("lane1", "2026-09-06", nonce="1")["seed"] != base


def test_random_draw_stays_inside_the_declared_space():
    for i in range(40):
        p = randomgen.draw("l", "2026-09-06", nonce=str(i))["params"]
        assert p["length"] in contract.ALLOWED_LENGTHS
        assert len(p["bits"]) == p["length"]
        assert set(p["bits"]) <= {"0", "1"}
        lo, hi = randomgen.SEED_ROOT_RANGE
        assert lo <= p["seed_root"] <= hi


def test_random_generator_does_not_read_the_corpus():
    """It is the RANDOM control. Coverage bias is a different, named policy."""
    from archaeon.tests.conftest import executable_source
    src = executable_source(randomgen)
    for banned in ("corpus", "fossils", "coverage", "explore"):
        assert banned not in src, \
            "the random policy consults {!r}; it must not".format(banned)


def test_draw_unused_skips_hashes_already_proposed():
    b = tickmod._SpecBuilder()
    first = randomgen.draw_unused("l", "2026-09-06", set(), b)
    again = randomgen.draw_unused("l", "2026-09-06", {first["spec_hash"]}, b)
    assert again is not None
    assert again["spec_hash"] != first["spec_hash"]


def test_draw_unused_gives_up_rather_than_spinning():
    b = tickmod._SpecBuilder()
    seen = set()
    for i in range(16):
        d = randomgen.draw("l", "2026-09-06", nonce=str(i))
        seen.add(b.spec_hash(b(d["params"])))
    assert randomgen.draw_unused("l", "2026-09-06", seen, b) is None


# --------------------------------------------------------------------------
# SPEC BUILDER + VALIDATION
# --------------------------------------------------------------------------
def test_built_spec_passes_vivariums_validator():
    p = randomgen.draw("l", "2026-09-06")["params"]
    specbuild.validate(specbuild.build(p))         # must not raise


def test_spec_carries_no_provenance():
    from archaeon import vivqueue as vq
    p = randomgen.draw("l", "2026-09-06")["params"]
    vq.assert_spec_is_execution_only(specbuild.build(p))


def test_bits_length_mismatch_is_refused():
    with pytest.raises(specbuild.SpecInvalid):
        specbuild.build({"bits": "0101", "length": 24, "seed_root": 1})


def test_spec_has_no_world_name():
    p = randomgen.draw("l", "2026-09-06")["params"]
    assert "name" not in specbuild.build(p)["world"]


def test_encounter_id_is_deterministic_and_not_derived_from_spec_hash():
    p = randomgen.draw("l", "2026-09-06")["params"]
    a, b = specbuild.encounter_id(p), specbuild.encounter_id(dict(p))
    assert a == b and a.startswith("ENC-archaeon-")
    # not circular: changing an unrelated spec field must not change it
    assert specbuild.encounter_id(p) == a


def test_if_indeterminate_is_declared_by_archaeon():
    """Vivarium must never author the indeterminate branch."""
    p = randomgen.draw("l", "2026-09-06")["params"]
    assert specbuild.build(p)["outcome_rule"]["if_indeterminate"]


def test_local_hash_matches_vivariums():
    from viv import spec as vspec
    p = randomgen.draw("l", "2026-09-06")["params"]
    s = specbuild.build(p)
    assert specbuild.spec_hash(s) == vspec.spec_hash(s)


# --------------------------------------------------------------------------
# READERS
# --------------------------------------------------------------------------
def test_fossil_reader_returns_a_corpus_and_a_summary():
    c = readers.recent_fossils(lookback_rows=50)
    s = readers.fossil_summary(c)
    for k in ("chart", "rows", "corpus_hash", "regions", "window"):
        assert k in s


def test_publication_record_sees_only_its_own_lane(conn, lane):
    assert readers.publication_record(conn, lane) == []
    r = tickmod.tick(conn, _cfg(lane))
    assert r["wrote"], r
    h = readers.publication_record(conn, lane)
    assert len(h) == 1 and h[0]["experiment_id"] == r["experiment_id"]
    assert readers.publication_record(conn, lane + "-other") == []


def test_health_reports_publication_not_execution(conn, lane):
    """Fire-and-forget: producer health is publication rate and cadence
    position. Execution state is Vivarium's to report."""
    tickmod.tick(conn, _cfg(lane))
    h = readers.health(conn, lane)
    assert h["lane"] == lane and h["published"] == 1 and h["published_today"] == 1
    for banned in contract.LIFECYCLE_COLUMNS:
        assert banned not in h,             "producer health reports {!r}, which is the experiment's fate".format(banned)


def test_archaeon_never_reads_experiment_lifecycle_state():
    """The mechanical form of fire-and-forget.

    Tests the real property -- which COLUMNS are selected -- rather than
    scanning for bare tokens. 'status' and 'error' are ordinary English and
    appear legitimately in tick()'s own return record ({"error": ...} is
    tick's report of its own failure, not a queue read), so a token scan
    produces false positives. The unambiguous column names are still scanned,
    because those can only mean the queue.
    """
    from archaeon.tests.conftest import executable_source
    from archaeon.producer import tick as _t

    # 1. the closed read-set contains no lifecycle column
    assert not (set(readers.PUBLICATION_COLUMNS)
                & set(contract.LIFECYCLE_COLUMNS))

    # 2. no unambiguous lifecycle column is named anywhere in the read path
    unambiguous = ("sfe_experiment_id", "pew_reference", "claimed_by",
                   "claimed_at", "started_at", "finished_at",
                   "result_summary")
    for mod in (readers, _t):
        src = executable_source(mod)
        for col in unambiguous:
            assert col not in src, (
                "{} names {!r}; Vivarium owns the experiment from claim onward"
                .format(mod.__name__, col))

    # 3. nothing selects a status
    src = executable_source(readers)
    assert "status" not in src,         "readers selects a status; execution state is Vivarium's to report"


def test_publication_record_carries_no_lifecycle_columns(conn, lane):
    tickmod.tick(conn, _cfg(lane))
    rows = readers.publication_record(conn, lane)
    assert rows
    for col in contract.LIFECYCLE_COLUMNS:
        assert col not in rows[0]


def test_fossil_reader_never_reads_the_queue():
    """A proposal that has not executed is not a fossil. Letting the detector
    see pending work would let Archaeon respond to its own intentions."""
    import ast
    import inspect
    src = inspect.getsource(readers.recent_fossils) + \
        inspect.getsource(readers.fossil_summary)
    assert "research_experiment_queue" not in src


# --------------------------------------------------------------------------
# TICK
# --------------------------------------------------------------------------
def test_tick_writes_exactly_one_row(conn, lane):
    r = tickmod.tick(conn, _cfg(lane))
    assert r["wrote"] and r["experiment_id"]
    assert r["decision"] in (tickmod.WROTE_SIGNAL, tickmod.WROTE_RANDOM)
    from archaeon import vivqueue as vq
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM {q} WHERE cadence_lane = %s"
                .format(q=vq.QUEUE), (lane,))
    assert int(cur.fetchone()[0]) == 1


def test_second_tick_is_refused_by_cadence_not_by_an_exception(conn, lane):
    assert tickmod.tick(conn, _cfg(lane))["wrote"]
    r2 = tickmod.tick(conn, _cfg(lane))
    assert r2["wrote"] is False
    assert r2["decision"] == tickmod.NO_WRITE_CADENCE
    assert "error" not in r2, "an ordinary refusal must not be an error"


def test_tick_is_json_serialisable(conn, lane):
    json.dumps(tickmod.tick(conn, _cfg(lane)), default=str)


def test_dry_run_writes_nothing(conn, lane):
    r = tickmod.tick(conn, _cfg(lane), dry_run=True)
    assert r["wrote"] is False and "spec" in r
    from archaeon import vivqueue as vq
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM {q} WHERE cadence_lane = %s"
                .format(q=vq.QUEUE), (lane,))
    assert int(cur.fetchone()[0]) == 0


def test_tick_records_its_decision_durably(conn, lane):
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM archaeon.cadence_log WHERE lane = %s",
                (lane,))
    before = int(cur.fetchone()[0])
    tickmod.tick(conn, _cfg(lane))
    tickmod.tick(conn, _cfg(lane))                 # refused; must also record
    cur.execute("SELECT count(*) FROM archaeon.cadence_log WHERE lane = %s",
                (lane,))
    assert int(cur.fetchone()[0]) >= before + 2, \
        "a refused cycle and a cycle that never ran must be distinguishable"


def test_tick_returns_error_as_data_not_as_an_exception(conn, lane):
    class Boom:
        def cursor(self):
            raise RuntimeError("database is on fire")

        def rollback(self):
            pass
    r = tickmod.tick(Boom(), _cfg(lane), dry_run=True)
    assert r["decision"] == tickmod.NO_WRITE_ERROR
    assert "database is on fire" in r["error"]


def test_tick_writes_a_spec_vivarium_can_execute(conn, lane):
    from viv import kinds as vk, spec as vspec
    from archaeon import vivqueue as vq
    r = tickmod.tick(conn, _cfg(lane))
    cur = conn.cursor()
    cur.execute("SELECT experiment_spec FROM {q} WHERE experiment_id = %s"
                .format(q=vq.QUEUE), (r["experiment_id"],))
    spec = cur.fetchone()[0]
    vspec.validate(spec)
    k = vk.get(spec["work"]["kind"])
    assert k is not None and k.implemented
    assert k.check(spec["work"]["payload"]) == []


# --------------------------------------------------------------------------
# LOOP
# --------------------------------------------------------------------------
def test_loop_tolerates_no_work_cycles(conn, lane):
    slept = []
    stats = loop.run(interval_s=0.0, config=_cfg(lane), max_cycles=4,
                     connect=_connect, sleep=slept.append)
    assert stats["cycles"] == 4
    assert stats["wrote"] == 1, "cadence should admit exactly one of four"
    assert stats["no_write"] == 3
    assert stats["errors"] == 0


def test_loop_survives_a_failing_connection(lane):
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] <= 2:
            raise RuntimeError("connection refused")
        return _connect()

    stats = loop.run(interval_s=0.0, config=_cfg(lane), max_cycles=4,
                     connect=flaky, sleep=lambda s: None)
    assert stats["cycles"] == 4
    assert stats["errors"] >= 2
    assert stats["consecutive_errors"] == 0, "should recover once the db returns"


def test_loop_backs_off_after_consecutive_errors(lane):
    delays = []

    def always_fail():
        raise RuntimeError("down")

    loop.run(interval_s=1.0, config=_cfg(lane), max_cycles=3,
             connect=always_fail, sleep=delays.append)
    assert delays and max(delays) >= loop.BACKOFF[0]


def test_loop_stops_cleanly_when_signalled(conn, lane):
    stopper = loop.Stopper()
    stopper.stop = True
    # max_cycles=0 exercises the same exit path without a real signal
    stats = loop.run(interval_s=0.0, config=_cfg(lane), max_cycles=0,
                     connect=_connect, sleep=lambda s: None)
    assert stats["cycles"] == 0 and "stopped_at" in stats


def test_loop_has_no_path_to_the_queue_except_tick():
    from archaeon.tests.conftest import executable_source
    src = executable_source(loop)
    assert "research_experiment_queue" not in src
    assert "submit(" not in src


def test_health_and_cadence_agree_on_when_the_last_publication_was(conn, lane):
    """Two numbers describing one fact must not disagree.

    health() counting all rows while cadence counted only quota-bearing rows
    made health report a recent publication where cadence reported none.
    """
    from archaeon import vivqueue as vq
    cur = conn.cursor()
    # a row that did NOT consume quota (a cancelled candidate, say)
    cur.execute(
        "INSERT INTO {q} (created_by, source_reason, experiment_spec, "
        " spec_hash, status, cadence_lane) "
        "VALUES ('archaeon','exploration','{{}}'::jsonb,%s,'cancelled',%s)"
        .format(q=vq.QUEUE), ("sha256:" + "c" * 64, lane))
    conn.commit()
    h = readers.health(conn, lane)
    assert h["last_published_at"] is None, \
        "a cancelled candidate consumed no quota and is not a publication"
    d = vq._evaluate_cadence(conn.cursor(), cfg.CadenceConfig(lane=lane))
    assert d.detail["last_autonomous_at_any_day"] is None
    assert h["seconds_since_last"] == d.detail["seconds_since_last"]
