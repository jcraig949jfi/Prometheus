"""G7 (BUILD_R8, ADAPT-15, ruling R14): export + cursor. Every pm:jobs:<L>:done stream reaches committed rows; epoch
N exports only rows after epoch N-1's cursor; the cursor is a committed file; the close full dump is byte-identical to
the concatenated deltas; and r7's cost analysis over pm:jobs:G:done is reproducible from committed rows alone.
Live: the per-lane test db (tests._live.live_url()) with unique lanes."""
from __future__ import annotations

import json
import subprocess
import uuid

import pytest

from primordial.bus import bus
from primordial.fabric import worker as W
from primordial.ops import bus_export as BX
from primordial.ops import epoch as EP
from primordial.tests._live import live_url

URL = live_url()


@pytest.fixture
def rr(monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    monkeypatch.setattr(bus, "URL", URL)
    lanes = ["x" + uuid.uuid4().hex[:6], "x" + uuid.uuid4().hex[:6]]
    keys = [W.DONE.format(L) for L in lanes] + [f"pm:telemetry:{lanes[0]}:jobs"]
    yield r, lanes, keys
    r.delete(*keys)


def done(r, L, n, cpu=1.5, wall=2.0, status="ok"):
    for k in range(n):
        r.xadd(W.DONE.format(L), {"json": json.dumps({"job_id": f"{L}-{k}", "cpu_s": cpu, "wall_s": wall,
                                                      "status": status, "granted_threads": 2, "sha": "abc"},
                                                     sort_keys=True)})


def test_done_streams_are_discovered_for_every_lane(rr):
    r, lanes, keys = rr
    done(r, lanes[0], 2)
    r.xadd(keys[2], {"lane": lanes[0], "rss_mb": "12"})
    got = BX.streams(r, lanes=[lanes[1]])                                  # lanes[1]: declared, no rows yet
    assert W.DONE.format(lanes[0]) in got and W.DONE.format(lanes[1]) in got and keys[2] in got
    assert bus.SWARM in got


def test_epoch_deltas_hold_only_rows_after_the_cursor_and_full_equals_concat(rr, tmp_path):
    r, lanes, keys = rr
    L = lanes[0]
    s = W.DONE.format(L)
    cur = tmp_path / BX.CURSOR_NAME
    done(r, L, 3)
    e1 = BX.export_delta(tmp_path / "epoch_1", "e1", cur, r=r, stream_keys=[s])
    ids_1 = [i for i, _ in r.xrange(s)]
    done(r, L, 4, cpu=0.25)
    BX.export_delta(tmp_path / "epoch_2", "e2", cur, r=r, stream_keys=[s])
    BX.export_delta(tmp_path / "epoch_3", "e3", cur, r=r, stream_keys=[s])                 # nothing new: empty delta
    done(r, L, 1, status="error")
    BX.export_delta(tmp_path / "epoch_4", "e4", cur, r=r, stream_keys=[s])
    f = BX.slug(s)
    rows = {n: [json.loads(x) for x in (tmp_path / f"epoch_{n}" / f"{f}_e{n}.jsonl").read_text("utf-8").splitlines()]
            for n in (1, 2, 3, 4)}
    assert e1[f][1] == 3 and [x["id"] for x in rows[1]] == ids_1
    assert len(rows[2]) == 4 and all(BX._id_key(x["id"]) > BX._id_key(ids_1[-1]) for x in rows[2])   # acceptance 2
    assert rows[3] == [] and len(rows[4]) == 1 and rows[4][0]["json"]["status"] == "error"
    state = json.loads(cur.read_text("utf-8"))                                                    # acceptance 3
    parts = [p["streams"][s] for p in state["partitions"]]
    assert [p["rows"] for p in parts] == [3, 4, 0, 1]
    assert parts[1]["from"] == ids_1[-1] and parts[2]["from"] == parts[2]["to"] == parts[1]["to"]
    assert state["cursor"][s] == r.xrevrange(s, count=1)[0][0]
    all_ids = [x["id"] for n in (1, 2, 3, 4) for x in rows[n]]
    assert all_ids == [i for i, _ in r.xrange(s)] and len(set(all_ids)) == 8                  # no gap, no duplicate
    BX.full_dump(tmp_path / "close_full", r=r, stream_keys=[s])                                   # acceptance 4
    full = (tmp_path / "close_full" / f"{f}_full.jsonl").read_bytes()
    assert full == BX.read_stream(tmp_path, s) and full.count(b"\n") == 8
    assert BX.verify_full(tmp_path, tmp_path / "close_full") == {"ok": True, "streams": {s: True}, "mismatched": []}
    with pytest.raises(ValueError):
        BX.export_delta(tmp_path / "epoch_2", "e2", cur, r=r, stream_keys=[s])                   # a partition is written once


def test_verify_full_names_a_stream_that_diverged(rr, tmp_path):
    """A trimmed stream (maxlen aged rows out) or a lost delta must not pass as identical."""
    r, lanes, _ = rr
    s = W.DONE.format(lanes[0])
    done(r, lanes[0], 5)
    BX.export_delta(tmp_path / "epoch_1", "e1", tmp_path / BX.CURSOR_NAME, r=r, stream_keys=[s])
    assert r.xtrim(s, maxlen=2, approximate=False) == 3                       # exact trim: 3 rows aged out
    BX.full_dump(tmp_path / "close_full", r=r, stream_keys=[s])
    v = BX.verify_full(tmp_path, tmp_path / "close_full")
    assert not v["ok"] and v["mismatched"] == [s]


def test_paging_crosses_page_boundaries_without_loss(rr, tmp_path, monkeypatch):
    r, lanes, _ = rr
    s = W.DONE.format(lanes[0])
    monkeypatch.setattr(BX, "PAGE", 3)
    done(r, lanes[0], 7)
    cur = tmp_path / BX.CURSOR_NAME
    BX.export_delta(tmp_path / "epoch_1", "e1", cur, r=r, stream_keys=[s])
    done(r, lanes[0], 6)
    BX.export_delta(tmp_path / "epoch_2", "e2", cur, r=r, stream_keys=[s])
    assert BX.read_stream(tmp_path, s).count(b"\n") == 13
    BX.full_dump(tmp_path / "close_full", r=r, stream_keys=[s])
    assert BX.verify_full(tmp_path, tmp_path / "close_full")["ok"]


def test_r7_cost_analysis_reproducible_from_committed_rows_alone(rr, tmp_path):
    """Regression (acceptance 5): r7's conductor read pm:jobs:G:done from Redis. The same numbers come from the repo."""
    r, lanes, _ = rr
    G = lanes[0]
    done(r, G, 3, cpu=100.25, wall=60.0)
    BX.export_delta(tmp_path / "epoch_1", "e1", tmp_path / BX.CURSOR_NAME, r=r, stream_keys=[W.DONE.format(G)])
    done(r, G, 2, cpu=7.5, wall=9.0, status="error")
    BX.export_delta(tmp_path / "epoch_2", "e2", tmp_path / BX.CURSOR_NAME, r=r, stream_keys=[W.DONE.format(G)])
    live = [json.loads(f["json"]) for _, f in r.xrange(W.DONE.format(G))]
    expect = {"lane": G, "jobs": 5, "cpu_s": round(sum(d["cpu_s"] for d in live), 3),
              "wall_s": round(sum(d["wall_s"] for d in live), 3), "status": {"ok": 3, "error": 2}}
    r.delete(W.DONE.format(G))                                                   # Redis gone: the repo must suffice
    assert BX.done_cost(tmp_path, G) == expect and expect["cpu_s"] == 315.75


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


def test_controller_commits_deltas_cursor_and_close_full_dump(rr, tmp_path, monkeypatch):
    """The epoch controller uses the cursor: boundary files are deltas, export_cursor.json is COMMITTED, and the close
    verifies full == concatenated deltas."""
    r, lanes, _ = rr
    monkeypatch.setenv("PM_TAG", "t-g7")
    monkeypatch.setenv("PM_LANE", "Q")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README").write_text("x", encoding="utf-8")
    git(tmp_path, "add", "README")
    git(tmp_path, "commit", "-q", "-m", "init")
    L = lanes[0]
    s = W.DONE.format(L)
    only = [s]
    real = BX.export
    monkeypatch.setattr(BX, "streams", lambda r, lanes=(): only)                 # isolate from other tests' streams
    ec = EP.EpochController([L], r=r, out=tmp_path / "epochs", repo=tmp_path, drain_timeout_s=0.0, post=False,
                            log=lambda m: None, log_dir=tmp_path.parent / f"log-{uuid.uuid4().hex[:6]}")
    assert ec.export is real and ec._cursored()
    done(r, L, 2)
    ec.boundary(1)
    done(r, L, 3)
    ec.boundary(2)
    c2 = r.xrevrange(s, count=1)[0][0]
    done(r, L, 1)
    v = ec.close_export()
    f = BX.slug(s)
    n = [len((tmp_path / "epochs" / d / f"{f}_{st}.jsonl").read_text("utf-8").splitlines())
         for d, st in (("epoch_1", "e1"), ("epoch_2", "e2"), ("close", "close"))]
    assert n == [2, 3, 1] and v == {"ok": True, "streams": {s: True}, "mismatched": []}
    committed = git(tmp_path, "show", "HEAD:epochs/export_cursor.json")
    assert json.loads(committed)["cursor"][s] == c2                                  # HEAD = epoch 2's cursor
    tracked = git(tmp_path, "ls-files", "epochs")
    assert "epochs/export_cursor.json" in tracked and f"epochs/epoch_2/{f}_e2.jsonl" in tracked
    assert [p["stamp"] for p in json.loads(committed)["partitions"]] == ["e1", "e2"]      # the committed partition
    r.delete(W.STOP.format(L))
