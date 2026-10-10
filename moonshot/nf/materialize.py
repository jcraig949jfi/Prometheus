"""Materialize published Moonshot evidence into Pan's lake (C-012-T005; contract moonshot/nf/INTERFACE_CONTRACT.md s6).

Postgres stays authoritative; the lake is DERIVED and append-only, and publication never waits on it. Runs ON M2
only (the lake's data files are M2-local), in Moonshot's lake venv (pyarrow, pyiceberg), calling Pan's public
functions as they are: pan.iceberg.write / last_snapshot_properties / read, namespace "moonshot" (never pan.*).

Six tables, each with an append-only key that orders its watermark:
  epochs           one row per publication                          key publication_id
  trace_lines      one row per line of each published TRACE         key publication_id (+ line_no)
  attempts         one row per classified attempt                   key its classification event_id
  validations      one row per validation                           key validation_id
  contests_opened  one row per contest, as opened                   key contest_id
  resolutions      one row per contest resolution                   key event_id
Recoverable and idempotent: each table's append is ONE Iceberg commit whose snapshot summary carries the table's
watermark (the largest key covered); a run resumes after the CURRENT snapshot's watermark, so a crash anywhere loses
or duplicates nothing. Settle: a row is eligible once older than `settle_s` (server clock), because a transaction
that drew a smaller key could still commit after a larger one; a row that slips behind the watermark anyway is
caught by the oracle (MISSED, with its keys) and restored exactly by `repair=True`. One materializer per (schema,
namespace) at a time (a Postgres advisory lock). Each run's report -- per table: appended, watermark, lake and
Postgres counts, oracle -- is logged in Moonshot's own records (record_materialization), never in pan.run.

    python -m moonshot.nf.materialize --schema moonshot_qual --prefix qual_ [--settle-s 60] [--repair] [--out F]
"""
import datetime
import json
import socket
import time

from moonshot.epoch import canonical as C
from moonshot.nf import pg

SEAT = "Themis"
LOCK_CLASS = 4243
CLASSIFICATIONS = ("published", "duplicate", "disagreement", "stale", "invalid", "refused_unapproved", "halted")
ORDER = ("epochs", "trace_lines", "attempts", "validations", "contests_opened", "resolutions")


class Busy(Exception):
    """Another materializer holds this (schema, namespace)."""


class InjectedCrash(Exception):
    """Test hook: the process 'dies' before a table's commit."""


def lock_key(schema, namespace):
    import hashlib
    return (LOCK_CLASS, int(hashlib.sha256("{}:{}".format(schema, namespace).encode()).hexdigest()[:7], 16))


def _schemas():
    import pyarrow as pa
    ts = pa.timestamp("us", tz="UTC")
    common = [("seat", pa.string()), ("kind", pa.string()), ("record", pa.string()), ("object_sha256", pa.string()),
              ("publication_id", pa.int64()), ("published_at", ts), ("materialized_at", ts),
              ("materializer", pa.string()), ("moonshot_schema", pa.string())]
    own = {
        "epochs": [("chain_id", pa.string()), ("namespace", pa.string()), ("epoch_index", pa.int64()),
                   ("generation", pa.int64()), ("work_id", pa.string()), ("epoch_digest", pa.string()),
                   ("parent_epoch_digest", pa.string()), ("attempt_id", pa.string()), ("published_by", pa.string()),
                   ("spec_sha256", pa.string()), ("trace_sha256", pa.string()), ("checkpoint_sha256", pa.string()),
                   ("trace_bytes", pa.int64()), ("checkpoint_bytes", pa.int64())],
        "trace_lines": [("chain_id", pa.string()), ("epoch_index", pa.int64()), ("line_no", pa.int64())],
        "attempts": [("event_id", pa.int64()), ("attempt_id", pa.string()), ("task_id", pa.string()),
                     ("chain_id", pa.string()), ("epoch_index", pa.int64()), ("outcome", pa.string()),
                     ("expected_generation", pa.int64()), ("expected_parent_digest", pa.string()),
                     ("work_id", pa.string()), ("epoch_digest", pa.string()), ("contest_id", pa.int64()),
                     ("classified_by", pa.string())],
        "validations": [("validation_id", pa.int64()), ("chain_id", pa.string()), ("epoch_index", pa.int64()),
                        ("epoch_digest", pa.string()), ("state", pa.string()), ("checks", pa.string()),
                        ("replay_digest", pa.string()), ("replay_host", pa.string()), ("validator", pa.string())],
        "contests_opened": [("contest_id", pa.int64()), ("chain_id", pa.string()), ("epoch_index", pa.int64()),
                            ("work_id", pa.string()), ("reason", pa.string()), ("published_epoch_digest", pa.string()),
                            ("challenger_epoch_digest", pa.string()), ("opened_by", pa.string())],
        "resolutions": [("event_id", pa.int64()), ("chain_id", pa.string()), ("contest_id", pa.int64()),
                        ("verdict", pa.string()), ("replay_digests", pa.string()), ("resolver", pa.string())],
    }
    return {t: pa.schema(common + cols) for t, cols in own.items()}


# Each spec: the key column, its kind, the eligible-rows query (watermark-free; the caller filters), the row mapper.
_ELIGIBLE = "< now() - make_interval(secs => %(settle)s) AS eligible"
SPECS = {
    "epochs": ("publication_id", "epoch", """
        SELECT p.publication_id, p.published_at, p.chain_id, c.namespace, p.epoch_index, p.generation, p.work_id,
               p.epoch_digest, p.parent_epoch_digest, p.attempt_id, p.published_by, r.manifest_sha256, r.spec_sha256,
               r.trace_sha256, r.output_checkpoint_sha256, mo.content, tr.size_bytes, ck.size_bytes,
               p.published_at """ + _ELIGIBLE + """
          FROM {s}.publications p
          JOIN {s}.results r ON r.work_id = p.work_id AND r.epoch_digest = p.epoch_digest
          JOIN {s}.chains c ON c.chain_id = p.chain_id
          JOIN {s}.objects mo ON mo.sha256 = r.manifest_sha256
          JOIN {s}.objects tr ON tr.sha256 = r.trace_sha256
          JOIN {s}.objects ck ON ck.sha256 = r.output_checkpoint_sha256
         ORDER BY p.publication_id"""),
    "trace_lines": ("publication_id", "trace", """
        SELECT p.publication_id, p.published_at, p.chain_id, p.epoch_index, r.trace_sha256, t.content,
               p.published_at """ + _ELIGIBLE + """
          FROM {s}.publications p
          JOIN {s}.results r ON r.work_id = p.work_id AND r.epoch_digest = p.epoch_digest
          JOIN {s}.objects t ON t.sha256 = r.trace_sha256
         ORDER BY p.publication_id"""),
    "attempts": ("event_id", "attempt", """
        SELECT e.event_id, e.at, a.attempt_id, a.task_id, a.chain_id, a.epoch_index, a.outcome, a.expected_generation,
               a.expected_parent_digest, a.work_id, a.epoch_digest, a.publication_id, a.contest_id, a.classified_by,
               a.detail, e.at """ + _ELIGIBLE + """
          FROM {s}.events e JOIN {s}.attempts a ON a.attempt_id = e.attempt_id
         WHERE e.kind IN ('""" + "', '".join(CLASSIFICATIONS) + "') ORDER BY e.event_id"),
    "validations": ("validation_id", "validation", """
        SELECT v.validation_id, v.validated_at, v.publication_id, v.chain_id, v.epoch_index, v.epoch_digest, v.state,
               v.checks, v.replay_digest, v.replay_host, v.validator, v.validated_at """ + _ELIGIBLE + """
          FROM {s}.validations v ORDER BY v.validation_id"""),
    "contests_opened": ("contest_id", "contest", """
        SELECT k.contest_id, k.opened_at, k.chain_id, k.epoch_index, k.work_id, k.reason, k.published_epoch_digest,
               k.challenger_epoch_digest, k.opened_by, k.detail, k.opened_at """ + _ELIGIBLE + """
          FROM {s}.contests k ORDER BY k.contest_id"""),
    "resolutions": ("event_id", "resolution", """
        SELECT e.event_id, e.at, e.chain_id, e.actor, e.detail, e.at """ + _ELIGIBLE + """
          FROM {s}.events e WHERE e.kind = 'resolution' ORDER BY e.event_id"""),
}


def _json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _rows(table, r, base):
    """One Postgres row -> lake rows (dicts) carrying its key."""
    if table == "epochs":
        (pid, at, cid, ns, k, gen, wid, dig, parent, aid, by, man, spec, trace, ckpt, content, tbytes, cbytes) = r
        return [dict(base, kind="epoch", record=bytes(content).decode("ascii"), object_sha256=man, publication_id=pid,
                     published_at=at, chain_id=cid, namespace=ns, epoch_index=k, generation=gen, work_id=wid,
                     epoch_digest=dig, parent_epoch_digest=parent, attempt_id=aid, published_by=by, spec_sha256=spec,
                     trace_sha256=trace, checkpoint_sha256=ckpt, trace_bytes=tbytes, checkpoint_bytes=cbytes)]
    if table == "trace_lines":
        pid, at, cid, k, trace, content = r
        lines = bytes(content).split(b"\n")
        if lines and lines[-1] == b"":
            lines = lines[:-1]
        return [dict(base, kind="trace", record=ln.decode("ascii", "replace"), object_sha256=trace, publication_id=pid,
                     published_at=at, chain_id=cid, epoch_index=k, line_no=i) for i, ln in enumerate(lines, 1)]
    if table == "attempts":
        (eid, at, aid, tid, cid, k, outcome, egen, eparent, wid, dig, pid, contest, by, detail) = r
        return [dict(base, kind="attempt", record=_json(detail), object_sha256=None, publication_id=pid,
                     published_at=at, event_id=eid, attempt_id=aid, task_id=tid, chain_id=cid, epoch_index=k,
                     outcome=outcome, expected_generation=egen, expected_parent_digest=eparent, work_id=wid,
                     epoch_digest=dig, contest_id=contest, classified_by=by)]
    if table == "validations":
        vid, at, pid, cid, k, dig, state, checks, replay, host, who = r
        return [dict(base, kind="validation", record=None, object_sha256=None, publication_id=pid, published_at=at,
                     validation_id=vid, chain_id=cid, epoch_index=k, epoch_digest=dig, state=state,
                     checks=",".join(checks or []), replay_digest=replay, replay_host=host, validator=who)]
    if table == "contests_opened":
        kid, at, cid, k, wid, reason, published, challenger, by, detail = r
        return [dict(base, kind="contest", record=_json(detail), object_sha256=None, publication_id=None,
                     published_at=at, contest_id=kid, chain_id=cid, epoch_index=k, work_id=wid, reason=reason,
                     published_epoch_digest=published, challenger_epoch_digest=challenger, opened_by=by)]
    if table == "resolutions":
        eid, at, cid, actor, detail = r
        d = detail or {}
        return [dict(base, kind="resolution", record=_json(detail), object_sha256=None, publication_id=None,
                     published_at=at, event_id=eid, chain_id=cid, contest_id=d.get("contest_id"),
                     verdict=d.get("verdict"), replay_digests=",".join(d.get("replay_digests") or []), resolver=actor)]
    raise KeyError(table)


def _row_key(table, row):
    key = SPECS[table][0]
    return (row[key], row["line_no"]) if table == "trace_lines" else row[key]


class PanLake:
    """Pan's public functions, used as they are (contract s6)."""

    def __init__(self, namespace="moonshot"):
        from pan import iceberg
        self.ice, self.ns = iceberg, namespace

    def _missing(self, e):
        from pyiceberg.exceptions import NoSuchNamespaceError, NoSuchTableError
        return isinstance(e, (NoSuchTableError, NoSuchNamespaceError))

    def watermark(self, name):
        try:
            w = self.ice.last_snapshot_properties(name, namespace=self.ns).get("watermark")
        except Exception as e:
            if self._missing(e):
                return None
            raise
        return int(w) if w not in (None, "") else None

    def append(self, name, table, watermark):
        self.ice.write(name, table, mode="append", namespace=self.ns,
                       snapshot_properties={"watermark": str(watermark), "writer": "moonshot.nf.materialize"})

    def rows(self, name):
        try:
            return self.ice.read(name, namespace=self.ns).to_pylist()
        except Exception as e:
            if self._missing(e):
                return []
            raise


def materialize(schema="moonshot", *, namespace="moonshot", prefix="", settle_s=60, repair=False, materializer=None,
                lake=None, _crash_before=None, _drop_key=None):
    """One materializer pass over every table; returns (and logs) the report."""
    import pyarrow as pa
    lake = lake or PanLake(namespace)
    who = materializer or "{}@{}".format(SEAT, socket.gethostname().lower())
    reader = pg.Moonshot(pg.connect(), schema, "reader", who)
    try:
        got = reader.select("SELECT pg_try_advisory_lock(%s, %s)", lock_key(schema, namespace))[0][0]
        if not got:
            raise Busy("another materializer holds {} -> {}".format(schema, namespace))
        try:
            return _run(pa, reader, lake, schema, namespace, prefix, settle_s, repair, who, _crash_before,
                        _drop_key or {})
        finally:
            reader.select("SELECT pg_advisory_unlock(%s, %s)", lock_key(schema, namespace))
    finally:
        reader.close()


def _run(pa, reader, lake, schema, namespace, prefix, settle_s, repair, who, crash_before, drop_key):
    started = time.time()
    run_at = datetime.datetime.now(datetime.timezone.utc)
    base = {"seat": SEAT, "materialized_at": run_at, "materializer": who, "moonshot_schema": schema}
    schemas = _schemas()
    report = {"schema": "moonshot.nf.materialization.v1", "moonshot_schema": schema, "namespace": namespace,
              "prefix": prefix, "settle_s": settle_s, "repair": repair, "materializer": who,
              "started_at": run_at.strftime("%Y-%m-%dT%H:%M:%SZ"), "tables": {}}
    for table in ORDER:
        t0 = time.time()
        key, kind, sql = SPECS[table]
        name = prefix + table
        every, eligible = [], []
        for r in reader.select(sql, {"settle": settle_s}):
            mapped = _rows(table, r[:-1], base)
            every.extend(mapped)
            if r[-1]:
                eligible.extend(mapped)
        wm = lake.watermark(name)
        have = None
        if repair:
            have = {_row_key(table, x) for x in lake.rows(name)}
            new = [x for x in eligible if _row_key(table, x) not in have]
        else:
            new = [x for x in eligible if wm is None or x[key] > wm]
        new = [x for x in new if x[key] != drop_key.get(table)]          # test hook: an instrument fault
        if crash_before == table:
            raise InjectedCrash("before the {} commit".format(name))
        if new:
            mark = max([x[key] for x in new] + ([wm] if wm is not None else []))
            cols = schemas[table].names
            lake.append(name, pa.Table.from_pylist([{c: x.get(c) for c in cols} for x in new], schema=schemas[table]),
                        mark)
            wm = mark
        # Oracle: every eligible row is in the lake (nothing MISSED), every lake row exists in Postgres (nothing
        # INVENTED), no key twice (nothing DUPLICATED). Rows materialized under a shorter settle stay legitimate.
        lake_keys = [_row_key(table, x) for x in lake.rows(name)]
        pg_keys = [_row_key(table, x) for x in eligible]
        missing = sorted(set(pg_keys) - set(lake_keys))
        invented = sorted(set(lake_keys) - {_row_key(table, x) for x in every})
        dupes = len(lake_keys) - len(set(lake_keys))
        oracle = "DUPLICATED" if dupes else ("INVENTED" if invented else ("MISSED" if missing else "OK"))
        entry = {"appended": len(new), "watermark": wm, "lake": len(lake_keys), "postgres": len(pg_keys),
                 "postgres_all": len(every), "oracle": oracle, "seconds": round(time.time() - t0, 3)}
        if missing:
            entry["missing_keys"] = [list(k) if isinstance(k, tuple) else k for k in missing][:50]
        report["tables"][table] = entry
    report["seconds"] = round(time.time() - started, 3)
    report["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    coord = pg.Moonshot(pg.connect(), schema, "coordinator", who)
    try:
        report["logged_event_id"] = coord.record_materialization(report)
    finally:
        coord.close()
    return report


def main(argv=None):
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog="moonshot.nf.materialize")
    ap.add_argument("--schema", required=True)
    ap.add_argument("--namespace", default="moonshot")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--settle-s", type=float, default=60)
    ap.add_argument("--repair", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rep = materialize(a.schema, namespace=a.namespace, prefix=a.prefix, settle_s=a.settle_s, repair=a.repair)
    text = json.dumps(rep, indent=1, sort_keys=True, default=str)
    print(text)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
    return 0 if all(t["oracle"] == "OK" for t in rep["tables"].values()) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
