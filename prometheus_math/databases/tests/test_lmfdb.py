"""Smoke tests for prometheus_math.databases.lmfdb against the live mirror.

These tests hit ``devmirror.lmfdb.xyz`` over the network. If the mirror is
unreachable (offline laptop, blocked network, mirror outage) every test
in this module is skipped — the failure is environmental, not a
regression.
"""
from __future__ import annotations

import pytest

from prometheus_math.databases import lmfdb


# ---------------------------------------------------------------------------
# Connect-test gate: skip the whole module if the mirror is unreachable.
# ---------------------------------------------------------------------------


def _mirror_online() -> bool:
    try:
        c = lmfdb.connect(timeout=5)
        c.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _mirror_online(),
    reason="devmirror.lmfdb.xyz unreachable from this host",
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_list_tables_returns_many():
    tables = lmfdb.list_tables()
    assert isinstance(tables, list)
    assert len(tables) > 100, f"expected >100 tables, got {len(tables)}"
    # Sanity: a few canonical LMFDB tables are present
    assert "ec_curvedata" in tables
    assert "nf_fields" in tables


def test_list_tables_pattern():
    ec_tables = lmfdb.list_tables(pattern="ec_%")
    assert all(t.startswith("ec_") for t in ec_tables)
    assert "ec_curvedata" in ec_tables
    assert "ec_mwbsd" in ec_tables


def test_count_ec_curvedata_large():
    n = lmfdb.count("ec_curvedata")
    # Estimated row count — LMFDB has well over a million elliptic curves
    assert n > 1_000_000, f"expected >1M rows in ec_curvedata, got {n}"


def test_schema_ec_curvedata():
    cols = lmfdb.schema("ec_curvedata")
    assert isinstance(cols, list)
    assert len(cols) > 20
    names = {c for c, _ in cols}
    for required in ("lmfdb_label", "ainvs", "conductor", "rank", "cm"):
        assert required in names, f"{required} missing from ec_curvedata schema"


def test_elliptic_curves_37a1():
    rows = lmfdb.elliptic_curves(label="37.a1")
    assert len(rows) == 1
    r = rows[0]
    assert r["lmfdb_label"] == "37.a1"
    assert r["conductor"] == 37
    assert r["rank"] == 1
    assert r["cm"] == 0
    # ainvs should be coerced to ints, not Decimal
    assert r["ainvs"] == [0, 0, 1, -1, 0]
    assert all(isinstance(a, int) for a in r["ainvs"])


def test_elliptic_curves_filter_by_conductor():
    rows = lmfdb.elliptic_curves(conductor=11, limit=100)
    assert len(rows) >= 1
    assert all(r["conductor"] == 11 for r in rows)
    # 11.a1, 11.a2, 11.a3 are the canonical conductor-11 curves
    labels = {r["lmfdb_label"] for r in rows}
    assert "11.a1" in labels


def test_ec_mwbsd_37a1():
    row = lmfdb.ec_mwbsd("37.a1")
    assert row is not None
    assert row["lmfdb_label"] == "37.a1"
    # 37.a1 has rank 1 -> exactly one Mordell-Weil generator
    assert row["ngens"] == 1
    # Sha_an = 1 (BSD) for this curve
    assert row["sha_an"] == 1
    assert row["tamagawa_product"] == 1
    # Real period > 0 always
    assert row["real_period"] is not None and row["real_period"] > 0
    # heights of generators present (single generator -> single height)
    assert row["heights"] is not None and len(row["heights"]) == 1


def test_number_fields_2_0_7751_1():
    rows = lmfdb.number_fields(label="2.0.7751.1")
    assert len(rows) == 1
    r = rows[0]
    assert r["label"] == "2.0.7751.1"
    assert r["degree"] == 2
    # Imaginary quadratic: signature (0, 1), so r2 = 1
    assert r["r2"] == 1
    # disc_sign should be -1 for imaginary quadratic
    assert r["disc_sign"] == -1


def test_number_fields_signature_filter():
    # Real quadratic = signature (2, 0); 100 should be plenty
    rows = lmfdb.number_fields(signature=(2, 0), limit=10)
    assert len(rows) > 0
    for r in rows:
        assert r["degree"] == 2
        assert r["r2"] == 0


def test_query_dicts_parameterized():
    rows = lmfdb.query_dicts(
        "SELECT lmfdb_label, conductor FROM ec_curvedata "
        "WHERE conductor = %s ORDER BY lmfdb_label LIMIT %s",
        (37, 5),
    )
    assert len(rows) >= 1
    assert all(r["conductor"] == 37 for r in rows)
    assert all("lmfdb_label" in r for r in rows)
