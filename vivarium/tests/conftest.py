"""Test fixtures.

Every test runs against REAL PostgreSQL in a throwaway schema. Mocking the
database here would test nothing that matters: FOR UPDATE SKIP LOCKED, the
partial unique index that makes double-running impossible, and the plpgsql
transition trigger are the mechanism, and a fake would only prove the fake
works.
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
if str(VIVARIUM) not in sys.path:
    sys.path.insert(0, str(VIVARIUM))

TEST_SCHEMA = "viv_test_" + uuid.uuid4().hex[:8]
os.environ.setdefault("VIV_SCHEMA", TEST_SCHEMA)

from viv import db as _db          # noqa: E402
from viv import queue as _q        # noqa: E402


@pytest.fixture(scope="session")
def schema():
    conn = _db.connect()
    try:
        _db.apply_migrations(conn, target_schema=TEST_SCHEMA)
        yield TEST_SCHEMA
        _db.drop_schema(conn, TEST_SCHEMA)
    finally:
        conn.close()


@pytest.fixture()
def conn(schema):
    """A clean queue for every test: truncate rather than re-migrate, so the
    DDL under test is created exactly once and shared."""
    c = _db.connect()
    with c.cursor() as cur:
        cur.execute("TRUNCATE %s.research_experiment_events, "
                    "%s.research_experiment_queue, "
                    "%s.worker_heartbeat" % (schema, schema, schema))
    c.commit()
    try:
        yield c
    finally:
        c.rollback()
        c.close()


def make_spec(bits: str = "0" * 24, *, name: str = "t-world",
              seed_root: int = 424242, kind: str = "noop_v0",
              outcome_rule=None, extra=None) -> dict:
    spec = {
        "spec_version": 1,
        "experiment_kind": "vivarium_selftest",
        "world": {"name": name, "seed_root": seed_root},
        "hypothesis": "a mechanical loop runs what it is given, once",
        "work": {"kind": kind, "payload": {"bits": bits, "length": len(bits)}},
    }
    if outcome_rule is not None:
        spec["outcome_rule"] = outcome_rule
    if extra:
        spec.update(extra)
    return spec
