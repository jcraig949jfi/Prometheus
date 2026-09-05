"""Vivarium CLI -- the status surface.

It answers exactly the operational questions and no scientific ones:

    vivarium status        is Vivarium alive? what is running? what is next?
                           what ran most recently? anything stranded?
    vivarium ls            the queue
    vivarium show <id>     one item, its SFE/PEW identities, its full history
    vivarium enqueue       admit a spec file
    vivarium cancel <id>   cancel a QUEUED item
    vivarium stranded      claimed/running rows with no live worker
    vivarium release <id>  the explicit operator recovery for a stranded row
    vivarium run           serve (--once for a single cycle)
    vivarium migrate       apply the (idempotent) schema

Run as:  python -m viv.cli <command>          (from vivarium/)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from . import db as _db
from . import loop as _loop
from . import queue as _q
from . import spec as _spec


def _j(obj) -> str:
    def default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        return str(o)
    return json.dumps(obj, indent=2, default=default)


def _short(row) -> str:
    return ("%s  %-9s p%-4s %s  spec=%s  sfe=%s  pew=%s"
            % (row["experiment_id"], row["status"], row["priority"],
               row["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
               row["spec_hash"][7:19],
               row["sfe_experiment_id"] or "-", row["pew_reference"] or "-"))


def cmd_migrate(args, conn) -> int:
    applied = _db.apply_migrations(conn, target_schema=args.schema)
    print("applied to schema %s: %s" % (args.schema or _db.schema(),
                                        ", ".join(applied)))
    return 0


def cmd_status(args, conn) -> int:
    s = args.schema
    workers = _q.workers(conn, schema=s)
    now = datetime.now(timezone.utc)
    print("== vivarium ==")
    if not workers:
        print("workers:      NONE have ever heartbeated on this schema")
    for w in workers:
        age = (now - w["last_seen"]).total_seconds()
        state = "ALIVE" if age < 60 else ("STALE(%.0fs)" % age)
        print("worker:       %s  %s  host=%s pid=%s  current=%s"
              % (w["worker_id"], state, w["host"], w["pid"],
                 w["current_experiment"] or "-"))

    running = _q.active(conn, schema=s)
    print("running:      %s" % (_short(running) if running else "nothing"))
    nxt = _q.next_eligible(conn, schema=s)
    print("next:         %s" % (_short(nxt) if nxt else "queue empty or all "
                                                        "held by not_before"))
    last = _q.most_recent_finished(conn, schema=s)
    print("most recent:  %s" % (_short(last) if last else "none"))

    c = _q.counts(conn, schema=s)
    print("counts:       %s" % (", ".join("%s=%s" % kv
                                          for kv in sorted(c.items())) or "-"))
    st = _q.stranded(conn, stale_after_s=args.stale_after, schema=s)
    print("stranded:     %d" % len(st))
    for r in st:
        print("   ! %s  %s  claimed_by=%s  last_seen=%s  sfe=%s"
              % (r["experiment_id"], r["status"], r["claimed_by"],
                 r["last_seen"], r["sfe_experiment_id"] or "-"))
    return 1 if st else 0


def cmd_ls(args, conn) -> int:
    for row in _q.listing(conn, status=args.status, limit=args.limit,
                          schema=args.schema):
        print(_short(row))
    return 0


def cmd_show(args, conn) -> int:
    row = _q.get(conn, args.experiment_id, schema=args.schema)
    if row is None:
        print("no such experiment", file=sys.stderr)
        return 1
    print(_j(dict(row)))
    print("\n-- events --")
    for e in _q.events(conn, args.experiment_id, schema=args.schema):
        print("%s  %-22s %-28s %s"
              % (e["occurred_at"].strftime("%Y-%m-%d %H:%M:%S"),
                 e["event_type"], e["actor"],
                 json.dumps(e["payload"])[:160]))
    return 0


def cmd_trace(args, conn) -> int:
    """Which queue item maps to which SFE experiment and PEW record."""
    print("%-38s %-28s %s" % ("experiment_id", "sfe_experiment_id",
                              "pew_reference"))
    for row in _q.listing(conn, status=args.status, limit=args.limit,
                          schema=args.schema):
        print("%-38s %-28s %s" % (row["experiment_id"],
                                  row["sfe_experiment_id"] or "-",
                                  row["pew_reference"] or "-"))
    return 0


def cmd_enqueue(args, conn) -> int:
    spec = json.loads(open(args.file, encoding="utf-8").read())
    try:
        _spec.validate(spec)
    except _spec.SpecError as exc:
        print("specification rejected:", file=sys.stderr)
        for reason in exc.reasons:
            print("  - %s" % reason, file=sys.stderr)
        return 2
    evidence = json.loads(args.source_evidence) if args.source_evidence else {}
    not_before = (datetime.fromisoformat(args.not_before)
                  if args.not_before else None)
    eid = _q.enqueue(conn, created_by=args.by, source_reason=args.reason,
                     experiment_spec=spec, source_evidence=evidence,
                     priority=args.priority, not_before=not_before,
                     schema=args.schema)
    conn.commit()
    print("%s  spec_hash=%s" % (eid, _spec.spec_hash(spec)))
    return 0


def cmd_hash(args, _conn) -> int:
    spec = json.loads(open(args.file, encoding="utf-8").read())
    print(_spec.spec_hash(spec))
    return 0


def cmd_cancel(args, conn) -> int:
    try:
        _q.cancel(conn, args.experiment_id, actor=args.by, reason=args.reason,
                  schema=args.schema)
    except RuntimeError as exc:
        conn.rollback()
        print(str(exc), file=sys.stderr)
        return 1
    conn.commit()
    print("cancelled %s" % args.experiment_id)
    return 0


def cmd_stranded(args, conn) -> int:
    rows = _q.stranded(conn, stale_after_s=args.stale_after, schema=args.schema)
    if not rows:
        print("no stranded experiments")
        return 0
    for r in rows:
        print(_j(dict(r)))
    return 1


def cmd_release(args, conn) -> int:
    """Resolve a stranded row to `failed`. It never returns to `queued`:
    requeueing asserts the experiment did not run, and the queue cannot know
    that -- check SFE and PEW, then enqueue a fresh item if appropriate."""
    try:
        row = _q.release_stranded(conn, args.experiment_id, actor=args.by,
                                  reason=args.reason, schema=args.schema)
    except RuntimeError as exc:
        conn.rollback()
        print(str(exc), file=sys.stderr)
        return 1
    conn.commit()
    print("released %s -> failed (was %s). SFE experiment: %s"
          % (row["experiment_id"], "claimed/running",
             row["sfe_experiment_id"] or "none recorded"))
    return 0


def cmd_run(args, conn) -> int:
    conn.close()
    v = _loop.Vivarium(worker_id=args.worker_id, schema=args.schema)
    return v.serve(interval_s=args.interval,
                   max_cycles=1 if args.once else None)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vivarium",
                                description="Vivarium experiment queue")
    p.add_argument("--schema", default=None,
                   help="override the queue schema (default: config/VIV_SCHEMA)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("migrate").set_defaults(fn=cmd_migrate)

    s = sub.add_parser("status")
    s.add_argument("--stale-after", type=float, default=900.0)
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("ls")
    s.add_argument("--status", default=None)
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(fn=cmd_ls)

    s = sub.add_parser("show")
    s.add_argument("experiment_id")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("trace", help="queue item -> SFE experiment -> PEW")
    s.add_argument("--status", default=None)
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(fn=cmd_trace)

    s = sub.add_parser("enqueue")
    s.add_argument("file")
    s.add_argument("--by", required=True)
    s.add_argument("--reason", required=True)
    s.add_argument("--source-evidence", default=None,
                   help="JSON object recording WHY this was queued")
    s.add_argument("--priority", type=int, default=100)
    s.add_argument("--not-before", default=None, help="ISO-8601 timestamp")
    s.set_defaults(fn=cmd_enqueue)

    s = sub.add_parser("hash")
    s.add_argument("file")
    s.set_defaults(fn=cmd_hash)

    s = sub.add_parser("cancel")
    s.add_argument("experiment_id")
    s.add_argument("--by", required=True)
    s.add_argument("--reason", required=True)
    s.set_defaults(fn=cmd_cancel)

    s = sub.add_parser("stranded")
    s.add_argument("--stale-after", type=float, default=900.0)
    s.set_defaults(fn=cmd_stranded)

    s = sub.add_parser("release")
    s.add_argument("experiment_id")
    s.add_argument("--by", required=True)
    s.add_argument("--reason", required=True)
    s.set_defaults(fn=cmd_release)

    s = sub.add_parser("run")
    s.add_argument("--once", action="store_true")
    s.add_argument("--interval", type=float, default=None)
    s.add_argument("--worker-id", default=None)
    s.set_defaults(fn=cmd_run)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    conn = _db.connect()
    try:
        return args.fn(args, conn)
    finally:
        try:
            conn.close()
        except Exception:                           # noqa: BLE001
            pass


if __name__ == "__main__":
    sys.exit(main())
