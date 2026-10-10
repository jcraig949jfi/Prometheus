"""PAN-07 controls for the Iceberg layer. Runs against the real catalog on M1
and the real lake, in a throwaway namespace that is dropped afterwards.

POSITIVE  rows appended are the rows read back, per snapshot
NEGATIVE  time travel to snapshot 1 does not see snapshot-2 rows
CHEAT     a Parquet file planted in the table's data directory OUTSIDE Iceberg
          is NOT read (reads go through metadata, not a directory listing);
          the same rows appended THROUGH Iceberg are read -- so the channel
          can see rows when they are committed, and only then
EVOLVE    a new column added by schema evolution reads back; old rows are null
"""
import os
import uuid

import pytest

os.environ.setdefault("EW_DB_HOST", "192.168.1.202")
pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")
pytest.importorskip("pyiceberg")

from pan import iceberg  # noqa: E402


@pytest.fixture()
def ns():
    name = "pan_test_" + uuid.uuid4().hex[:8]
    cat = iceberg.catalog()
    cat.create_namespace(name)
    yield name
    for ident in cat.list_tables(name):
        cat.drop_table(ident)
    cat.drop_namespace(name)


def test_append_time_travel_cheat_and_evolution(ns):
    t1 = pa.table({"id": pa.array([1, 2, 3], pa.int64()), "v": pa.array(["a", "b", "c"])})
    tab = iceberg.write("t", t1, namespace=ns)
    s1 = tab.current_snapshot().snapshot_id
    t2 = pa.table({"id": pa.array([4, 5], pa.int64()), "v": pa.array(["d", "e"])})
    tab = iceberg.write("t", t2, namespace=ns)
    s2 = tab.current_snapshot().snapshot_id
    assert s1 != s2
    # POSITIVE
    assert sorted(iceberg.read("t", namespace=ns)["id"].to_pylist()) == [1, 2, 3, 4, 5]
    # NEGATIVE: time travel
    assert sorted(iceberg.read("t", snapshot_id=s1, namespace=ns)["id"].to_pylist()) == [1, 2, 3]
    # CHEAT: plant a parquet file in the data directory without committing it
    loc = tab.location()
    data_dir = loc.replace("file:///", "").replace("file://", "") + "/data"
    os.makedirs(data_dir, exist_ok=True)
    planted = pa.table({"id": pa.array([999], pa.int64()), "v": pa.array(["PLANTED"])})
    pq.write_table(planted, os.path.join(data_dir, "planted-outside-iceberg.parquet"))
    assert 999 not in iceberg.read("t", namespace=ns)["id"].to_pylist()
    tab = iceberg.write("t", planted, namespace=ns)
    assert 999 in iceberg.read("t", namespace=ns)["id"].to_pylist()
    # EVOLVE: add a column
    t3 = pa.table({"id": pa.array([6], pa.int64()), "v": pa.array(["f"]), "w": pa.array([1.5])})
    iceberg.write("t", t3, namespace=ns)
    got = iceberg.read("t", namespace=ns).to_pylist()
    w = {r["id"]: r["w"] for r in got}
    assert w[6] == 1.5 and w[1] is None
