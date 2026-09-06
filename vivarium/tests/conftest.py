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

# TESTS MUST NOT REACH PRODUCTION. Two separate registers to keep out of:
#
#   the QUEUE  -- VIV_SCHEMA points every connection at a throwaway schema
#                 carrying the identical DDL. Archaeon's suite wrote 245 rows
#                 into the production register on 2026-09-06 for want of
#                 exactly this.
#   PEW        -- vivarium/config.json now defaults pew_namespace to `prod`,
#                 because that is what the autonomous consumer must write and
#                 what ew/fossil.py filters on. A test run inheriting that
#                 default would put fixtures into the scientific record, so the
#                 namespace is forced here. Note `=` and not `setdefault`: an
#                 operator exporting VIV_PEW_NAMESPACE=prod in their shell must
#                 not be able to aim the suite at production by accident.
os.environ["VIV_PEW_NAMESPACE"] = "test"

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
        cur.execute("TRUNCATE %s.register_errata_rows, %s.register_errata, "
                    "%s.research_experiment_events, "
                    "%s.research_experiment_queue, "
                    "%s.worker_heartbeat RESTART IDENTITY"
                    % (schema, schema, schema, schema, schema))
    c.commit()
    try:
        yield c
    finally:
        c.rollback()
        c.close()


DEFAULT_RULE = {"field": "executed", "op": "==", "value": True,
                "if_true": "SURVIVED", "if_false": "FALSIFIED",
                "if_indeterminate": "INCONCLUSIVE"}

BITSTRING_RULE = {"field": "solved", "op": "==", "value": True,
                  "if_true": "SURVIVED", "if_false": "FALSIFIED",
                  "if_indeterminate": "INCONCLUSIVE"}


def make_spec(bits: str = "0" * 24, *, seed_root: int = 424242,
              kind: str = "noop_v0", outcome_rule=None, prediction=None,
              pew=None, hypothesis=None, extra=None) -> dict:
    """A valid spec v2. NOTE the shape: no name, no notes, no experiment_kind
    -- the sealed spec is exactly the execution inputs."""
    if kind == "noop_v0":
        payload = {}
        rule = outcome_rule or DEFAULT_RULE
    else:
        payload = {"bits": bits, "length": len(bits)}
        rule = outcome_rule or BITSTRING_RULE
    spec = {
        "spec_version": 2,
        "world": {"seed_root": seed_root},
        "hypothesis": hypothesis or
                      "a mechanical loop runs what it is given, once",
        "prediction": prediction,
        "work": {"kind": kind, "payload": payload},
        "outcome_rule": rule,
        "pew": pew,
    }
    if extra:
        spec.update(extra)
    return spec
