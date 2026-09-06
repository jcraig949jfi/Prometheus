"""Archaeon test fixtures.

THE PRODUCTION REGISTER IS NOT A TEST FIXTURE. Before 2026-09-06 these tests
wrote into viv.research_experiment_queue itself -- 245 rows in one run, one of
which a live Vivarium cycle claimed and attempted to execute. Setting
VIV_SCHEMA here redirects archaeon.vivqueue (and Vivarium's own db layer) to a
throwaway schema carrying the identical DDL, so the mechanism under test is the
real one and the register it writes to is not.
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
VIVARIUM = REPO / "vivarium"
for p in (str(REPO), str(VIVARIUM)):
    if p not in sys.path:
        sys.path.insert(0, p)

TEST_SCHEMA = "viv_archaeon_test_" + uuid.uuid4().hex[:8]
os.environ["VIV_SCHEMA"] = TEST_SCHEMA


@pytest.fixture(scope="session", autouse=True)
def _viv_test_schema():
    from viv import db as _vdb
    conn = _vdb.connect()
    try:
        _vdb.apply_migrations(conn, target_schema=TEST_SCHEMA)
        yield TEST_SCHEMA
        _vdb.drop_schema(conn, TEST_SCHEMA)
    finally:
        conn.close()
