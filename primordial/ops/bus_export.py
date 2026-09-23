"""Export the live bus to committed JSONL (round 2 comms item C4).

The bus is the preregistration record (hypotheses are posted before runs) and
Redis is ephemeral. The conductor runs this every few minutes (liveness.py
--export-every-min does it) and commits the directory.

    python -m primordial.ops.bus_export [--out DIR] [--stamp YYYY-MM-DD]

G7 (round 8, ADAPT-15, ruling R14): THE BUS IS NOT AN ARCHIVE. Before G7 `export()` re-dumped every stream from
the beginning at each boundary (r7: nine near-identical swarm copies) and never exported `pm:jobs:<L>:done` at
all, so cpu_s / wall_s / granted_threads / sha / predicate_id / telemetry lived only in a maxlen-100k stream.

  * every job done stream `pm:jobs:<L>:done` (discovered by SCAN, plus any lane passed explicitly) and every
    telemetry stream (TELEMETRY_PATTERNS) is exported, one file per stream: `<slug>_<stamp>.jsonl`, where
    slug = the key with ':' -> '_' (pm:jobs:G:done -> pm_jobs_G_done);
  * with `cursor_path` (the epoch controller passes one) an export writes ONLY rows with ids after the stream's
    cursor, up to a snapshot of the stream's last id taken at the start of the export, then records the new
    cursor and the (stamp, from, to, rows) partition in the cursor file. The cursor file is committed with the
    epoch, so a reproduction replays the exact partition;
  * `full_dump()` (at close) writes one full dump per stream; `verify_full()` checks each is byte-identical to
    the in-order concatenation of the committed deltas and names every stream that is not (e.g. trimmed by
    maxlen before its delta was taken);
  * `read_stream()` / `done_cost()` rebuild a stream -- and the conductor's r7 cost analysis over pm:jobs:G:done
    -- from committed rows alone, with no Redis.
Without cursor_path, export() keeps its legacy full-dump layout (pm_swarm / pm_results / pm_anomalies) and adds
the done and telemetry streams.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

from primordial.bus import bus

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "roles" / "Nestor" / "sidequests" / "graphworld" / "bus_export"
CURSOR_NAME = "export_cursor.json"
DONE_PATTERN = "pm:jobs:*:done"
# G5 telemetry + G4 watcher beacons. Stream keys only (non-stream keys matching a pattern are skipped).
TELEMETRY_PATTERNS = ("pm:telemetry:*", "pm:watch:*", "pm:why_not_run*")   # P: telemetry:{watch,queue,jobres}
PAGE = 5000


def slug(stream: str) -> str:
    return stream.replace(":", "_")


def _is_stream(r, key) -> bool:
    try:
        return r.type(key) == "stream"
    except Exception:
        return False


def streams(r, lanes=()) -> list[str]:
    """Every stream G7 archives: the bus streams, all job done streams (+ explicit lanes), telemetry streams."""
    keys = {bus.SWARM, bus.RESULTS, bus.ANOMALIES, bus.ANOM_EVENTS}
    keys |= {f"pm:jobs:{L}:done" for L in lanes}
    for pat in (DONE_PATTERN, *TELEMETRY_PATTERNS):
        keys |= {k for k in r.scan_iter(pat) if _is_stream(r, k)}
    return sorted(keys)


def _row(stream: str, i: str, f: dict) -> dict:
    """One committed row: the entry id plus its fields; a `json` field is decoded in place (lossless)."""
    out = {"id": i}
    for k, v in f.items():
        if k == "json":
            try:
                v = json.loads(v)
            except ValueError:
                pass
        out[k] = v
    return out


def _line(row: dict) -> str:
    return json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n"


def _id_key(i: str) -> tuple[int, int]:
    ms, _, seq = str(i).partition("-")
    return int(ms), int(seq or 0)


def _last_id(r, stream) -> str | None:
    top = r.xrevrange(stream, count=1)
    return top[0][0] if top else None


def _range(r, stream, after: str | None, upto: str) -> list[tuple[str, dict]]:
    """Entries with after < id <= upto, paged. Inclusive-min paging with the equal id dropped (no '(' syntax)."""
    rows, lo = [], after or "-"
    while True:
        page = r.xrange(stream, min=lo, max=upto, count=PAGE)
        page = [(i, f) for i, f in page if after is None or _id_key(i) > _id_key(after)]
        rows.extend(page)
        if not page or len(page) < PAGE - 1:
            return rows
        after = lo = page[-1][0]


def _write(p: pathlib.Path, lines) -> int:
    n = 0
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        for s in lines:
            fh.write(s)
            n += 1
    return n


def load_cursor(cursor_path) -> dict:
    p = pathlib.Path(cursor_path)
    if not p.exists():
        return {"version": 1, "cursor": {}, "partitions": []}
    return json.loads(p.read_text(encoding="utf-8"))


def export_delta(out, stamp: str, cursor_path, r=None, lanes=(), stream_keys=None) -> dict:
    """G7: rows after each stream's cursor -> <out>/<slug>_<stamp>.jsonl; cursor + partition -> cursor_path."""
    r = r or bus.conn()
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    state = load_cursor(cursor_path)
    if any(p["stamp"] == stamp for p in state["partitions"]):
        raise ValueError(f"export stamp {stamp!r} already in {cursor_path}: a partition is written once")
    keys = sorted(stream_keys) if stream_keys is not None else streams(r, lanes)
    tops = {s: _last_id(r, s) for s in keys}                     # snapshot first: one consistent cut per export
    written, part = {}, {"stamp": stamp, "dir": out.name, "ts": round(time.time(), 3), "streams": {}}
    for s in keys:
        after = state["cursor"].get(s)
        top = tops[s]
        rows = _range(r, s, after, top) if top and (after is None or _id_key(top) > _id_key(after)) else []
        p = out / f"{slug(s)}_{stamp}.jsonl"
        n = _write(p, (_line(_row(s, i, f)) for i, f in rows))
        new = rows[-1][0] if rows else after
        part["streams"][s] = {"from": after, "to": new, "rows": n, "file": p.name}
        if new is not None:
            state["cursor"][s] = new
        written[slug(s)] = (str(p), n)
    written["state"] = _state_snapshot(r, out, stamp)
    state["partitions"].append(part)
    pathlib.Path(cursor_path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(cursor_path).write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8",
                                         newline="\n")
    return written


def full_dump(out, r=None, stamp: str = "full", stream_keys=None, lanes=()) -> dict:
    """G7 close: one full dump per stream, same row encoding as the deltas."""
    r = r or bus.conn()
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    keys = sorted(stream_keys) if stream_keys is not None else streams(r, lanes)
    written = {}
    for s in keys:
        top = _last_id(r, s)
        rows = _range(r, s, None, top) if top else []
        p = out / f"{slug(s)}_{stamp}.jsonl"
        written[slug(s)] = (str(p), _write(p, (_line(_row(s, i, f)) for i, f in rows)))
    return written


def read_stream(root, stream: str, cursor_path=None) -> bytes:
    """A stream rebuilt from COMMITTED deltas alone: the partition files in cursor order, concatenated."""
    root = pathlib.Path(root)
    state = load_cursor(cursor_path or root / CURSOR_NAME)
    buf = b""
    for part in state["partitions"]:
        info = part["streams"].get(stream)
        if info:
            buf += (root / part["dir"] / info["file"]).read_bytes()
    return buf


def verify_full(root, full_dir, cursor_path=None, stamp: str = "full") -> dict:
    """-> {ok, streams: {stream: identical}, mismatched: [...]}: full dump vs concatenated deltas, byte for byte."""
    root, full_dir = pathlib.Path(root), pathlib.Path(full_dir)
    state = load_cursor(cursor_path or root / CURSOR_NAME)
    names = sorted({s for p in state["partitions"] for s in p["streams"]})
    res = {}
    for s in names:
        f = full_dir / f"{slug(s)}_{stamp}.jsonl"
        res[s] = f.exists() and f.read_bytes() == read_stream(root, s, cursor_path)
    bad = [s for s, ok in res.items() if not ok]
    return {"ok": not bad, "streams": res, "mismatched": bad}


def done_cost(root, lane: str, cursor_path=None) -> dict:
    """The r7 conductor cost analysis over pm:jobs:<lane>:done, from committed rows only (G7 acceptance 5)."""
    jobs, cpu, wall, status = 0, 0.0, 0.0, {}
    for line in read_stream(root, f"pm:jobs:{lane}:done", cursor_path).decode("utf-8").splitlines():
        d = json.loads(line).get("json") or {}
        jobs += 1
        cpu += float(d.get("cpu_s") or 0.0)
        wall += float(d.get("wall_s") or 0.0)
        status[d.get("status")] = status.get(d.get("status"), 0) + 1
    return {"lane": lane, "jobs": jobs, "cpu_s": round(cpu, 3), "wall_s": round(wall, 3), "status": status}


def _state_snapshot(r, out: pathlib.Path, stamp: str):
    state = [{"key": k, "zset": r.zrevrange(k, 0, -1, withscores=True)} for k in sorted(r.scan_iter("pm:board:*"))]
    state += [{"key": bus.CLAIMS, "hash": r.hgetall(bus.CLAIMS)}, {"key": bus.TAGS, "hash": r.hgetall(bus.TAGS)},
              {"key": bus.ANOM_STATUS, "hash": r.hgetall(bus.ANOM_STATUS)}]
    p = out / f"pm_boards_claims_{stamp}.jsonl"
    return str(p), _write(p, (_line(row) for row in state))


def export(out=DEFAULT_OUT, stamp: str | None = None, r=None, cursor_path=None, lanes=()) -> dict:
    r = r or bus.conn()
    stamp = stamp or time.strftime("%Y-%m-%d")
    if cursor_path is not None:
        return export_delta(out, stamp, cursor_path, r=r, lanes=lanes)
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)

    def dump(name, rows):
        p = out / f"{name}_{stamp}.jsonl"
        return p, _write(p, (_line(row) for row in rows))

    written = {
        "swarm": dump("pm_swarm", [{"id": i, **f} for i, f in r.xrange(bus.SWARM)]),
        "results": dump("pm_results", [{"id": i, **json.loads(f["json"])} for i, f in r.xrange(bus.RESULTS)]),
        "anomalies": dump("pm_anomalies", [{"id": i, **f} for i, f in r.xrange(bus.ANOMALIES)]
                          + [{"id": i, "event": True, **f} for i, f in r.xrange(bus.ANOM_EVENTS)]),
        "state": _state_snapshot(r, out, stamp),
    }
    legacy = {bus.SWARM, bus.RESULTS, bus.ANOMALIES, bus.ANOM_EVENTS}
    for s in streams(r, lanes):                                   # G7: done + telemetry streams, full in legacy mode
        if s not in legacy:
            top = _last_id(r, s)
            written[slug(s)] = dump(slug(s), [_row(s, i, f) for i, f in (_range(r, s, None, top) if top else [])])
    return {k: (str(p), n) for k, (p, n) in written.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--stamp")
    ap.add_argument("--cursor", default=None, help="G7: cursor file; export only rows after it and advance it")
    a = ap.parse_args(argv)
    for k, (p, n) in export(a.out, a.stamp, cursor_path=a.cursor).items():
        print(f"{k:10s} {n:6d}  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
