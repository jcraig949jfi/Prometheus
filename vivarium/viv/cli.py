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

import datetime as _dt
import json as _json

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import db as _db
from . import workspace as _workspace
from . import identity as _identity
from . import kinds as _kinds
from . import daemon as _daemon
from . import loop as _loop
from . import queue as _q
from . import spec as _spec
from . import vardir as _vardir


def _j(obj) -> str:
    def default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        return str(o)
    return json.dumps(obj, indent=2, default=default)


def _short(row) -> str:
    rel = ""
    if row.get("family_id"):
        rel = "  fam=%s/%s" % (row["family_id"], row.get("arm_id") or "-")
    if row.get("candidate_set_id"):
        rel += "  cs=%s" % row["candidate_set_id"]
    if row.get("replication_of"):
        rel += "  repl_of=%s" % str(row["replication_of"])[:8]
    return ("%s  %-9s p%-4s %s  spec=%s  sfe=%s  pew=%s%s"
            % (row["experiment_id"], row["status"], row["priority"],
               row["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
               row["spec_hash"][7:19],
               row["sfe_experiment_id"] or "-", row["pew_reference"] or "-",
               rel))


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
    parked = 0
    for w in workers:
        var = _worker_var_dir(w) or _vardir.resolve(_db.load_config(),
                                                    create=False)
        park = _daemon.read_park(var, w["worker_id"])
        if park is not None:
            parked += 1
            print("PARKED:       %s  %s since %s -- %s  (accountable: %s)"
                  % (w["worker_id"], park.get("kind"), park.get("parked_at"),
                     park.get("reason"), park.get("accountable_seat")))
    for r in st:
        print("   ! %s  %s  claimed_by=%s  last_seen=%s  sfe=%s"
              % (r["experiment_id"], r["status"], r["claimed_by"],
                 r["last_seen"], r["sfe_experiment_id"] or "-"))
    # Non-zero on a park as well as a strand: a parked consumer is visible
    # dormancy (base rule 7), and this command is used as a check.
    return 1 if (st or parked) else 0


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
    """(D-23 guarded: admitting a row is a write to the durable register.)"""
    _workspace.assert_not_canonical("enqueue", allow_override=False)
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
    try:
        eid = _q.enqueue(conn, created_by=args.by, source_reason=args.reason,
                         experiment_spec=spec, source_evidence=evidence,
                         priority=args.priority, not_before=not_before,
                         request_key=args.request_key,
                         replication_of=args.replication_of,
                         family_id=args.family, arm_id=args.arm,
                         candidate_set_id=args.candidate_set,
                         schema=args.schema)
    except _q.DuplicateRequest as exc:
        conn.rollback()
        print(str(exc), file=sys.stderr)
        return 3
    except _q.CandidateSetReused as exc:
        # An APPEND to a registered candidate set. Refused before any write
        # (and by the database if the pre-check is raced); exit 4 so a script
        # can tell it from a duplicate request.
        conn.rollback()
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 4
    conn.commit()
    h = _spec.spec_hash(spec)
    print("%s  spec_hash=%s  world=%s" % (eid, h, _spec.world_name(h)))
    return 0


def cmd_sfe_identity(args, _conn) -> int:
    """The durable SFE identity. Registers ONCE with --ensure."""
    if args.ensure:
        import sys as _sys
        from pathlib import Path as _Path
        cfg = _db.load_config()
        cacert = cfg.get("sfe_cacert")
        if cacert and not _Path(cacert).is_absolute():
            cacert = str(_db.ROOT.parent / cacert)
        _sys.path.insert(0, str(_db.ROOT.parent / "SerendipityFoundry"
                                / "SerendipityFoundryClient"))
        from sfclient import EngineClient          # noqa: PLC0415

        class _Registrar:
            """EngineClient.register() returns only the token and drops the
            client_id, which is the durable identity's actual name in SFE.
            This keeps it, so `sfe-identity` never needs a manual lookup."""

            def __init__(self, ec):
                self.ec, self.client_id = ec, None

            def register(self, name):
                r = self.ec._req("POST", "/v2/clients", {"name": name})  # noqa: SLF001
                self.ec.token = r["token"]
                self.client_id = r.get("client_id")
                return r["token"]

        try:
            _identity.token_for(
                args.role, register_if_missing=True,
                client_factory=lambda: _Registrar(
                    EngineClient(cfg["sfe_base_url"], cafile=cacert)),
                log=print)
        except _identity.IdentityError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    print(_j(_identity.describe()))
    return 0


def cmd_limits(args, _conn) -> int:
    """The alpha resource profile in force, and what each limit IS.

    Deliverable 5 of the H0-H5 loader order. Printed rather than described in a
    document, because a profile that lives only in prose drifts from the one
    the code enforces the first time somebody edits either.
    """
    from . import artifacts as _artifacts
    from . import resources as _res

    lim = _artifacts.ALPHA
    print("ARTIFACT LOADER -- alpha profile (viv/artifacts.py: Limits)")
    for name, value in sorted(lim.as_dict().items()):
        unit = "bytes" if name.endswith("bytes") else ""
        print("  %-22s %12s %s" % (name, value, unit))
    print()
    print("ENFORCEMENT, measured on this host by running the meter:")
    m = _res.Meter().start()
    m.count("artifact_bytes", 0)
    m.count("artifact_fetches", 0)
    vector = m.vector(artifact_bytes_limit=lim.total_bytes, wall_limit=60.0)
    for cls in _res.CLASSES:
        names = _res.enforcement_summary(vector)[cls]
        print("  %-12s %s" % (cls, ", ".join(names) or "(none)"))
    print()
    print("  enforceable = the operation is PREVENTED when the budget is gone")
    print("                (artifact_bytes is debited on the execution world")
    print("                 BEFORE each fetch; the engine blocks and raises).")
    print("  measured    = observed by a real instrument on this run.")
    print("  unavailable = not obtainable here. NOT zero.")
    print()
    peak = vector["peak_memory_bytes"]
    print("  peak_memory_bytes: %s (%s)"
          % (peak["enforcement_class"], peak["method"]))
    print("  Additive quantities (safe to sum across attempts): %s"
          % ", ".join(sorted(_res.ADDITIVE)))
    print("  Everything else must NOT be summed -- peak memory and overlapping")
    print("  wall durations especially.")
    return 0


def cmd_kinds(args, _conn) -> int:
    """The execution-kind contracts. What a spec of each kind must declare."""
    for name in _kinds.known():
        k = _kinds.get(name)
        flags = []
        if k.provisional:
            flags.append("PROVISIONAL")
        if k.stateful:
            flags.append("stateful")
        if k.retired:
            flags.append("RETIRED " + k.retired_at)
        print("%-22s %-13s owner=%-9s params=%s%s"
              % (name, "IMPLEMENTED" if k.implemented else "external",
                 k.owner, sorted(k.params) or "(none)",
                 ("  [" + ", ".join(flags) + "]") if flags else ""))
        if k.retired:
            print("     retired: %s" % k.retired_note[:200])
        # WP-0f: the SAME contract validation uses, printed. A template author
        # reading this and a run being validated must not consult two sources.
        if k.declares_result:
            for line in k.result_lines():
                print("     result  %s" % line)
        else:
            print("     result  (not declared -- the executor lives "
                  "elsewhere and its owner declares its result)")
    print("")
    print("admissible for a NEW spec: %s" % _kinds.admissible())
    print("retired (meaning preserved, new admissions refused): %s"
          % _kinds.retired())
    return 0


def cmd_family(args, conn) -> int:
    """A prospectively declared comparison family, by arm."""
    rows = _q.family(conn, args.family_id, schema=args.schema)
    if not rows:
        print("no rows declare family_id=%s" % args.family_id)
        return 1
    by_arm = {}
    for r in rows:
        by_arm.setdefault(r["arm_id"] or "(no arm)", []).append(r)
    print("family %s: %d rows in %d arms" % (args.family_id, len(rows),
                                             len(by_arm)))
    hashes = {}
    for arm, rs in sorted(by_arm.items()):
        print("  arm %s: %d" % (arm, len(rs)))
        for r in rs:
            hashes.setdefault(r["spec_hash"], []).append(arm)
            print("    " + _short(r))
    shared = {h: a for h, a in hashes.items() if len(set(a)) > 1}
    print("specs shared across arms: %d  (identical science, different arm -- "
          "the sealed spec is not contaminated by the arm label)" % len(shared))
    return 0


def cmd_candidates(args, conn) -> int:
    out = _q.candidate_set(conn, args.candidate_set_id, schema=args.schema)
    if out is None:
        print("no such candidate set")
        return 1
    print(_j(out))
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
    """The daemon entry point. `--once` runs exactly one tick."""
    # D-23. allow_override=False: the consumer holds a single global execution
    # slot and writes to the production register, so there is no reading of
    # "read-only inspection" under which it may run from the canonical
    # checkout. An override that could unlock this would be a hole with a
    # polite name.
    # Rule 2 AND rule 6. assert_not_canonical alone passes a linked worktree
    # under the canonical checkout and a session-temporary path -- both report
    # main_worktree false, and both are places a long-lived process must not
    # live. Techne found that hole in their own copy of this guard.
    ws = _workspace.assert_durable_worktree("run the consumer")
    conn.close()
    # The daemon writes its OWN log, flushed per line. The 2026-09-11 consumer
    # died with a 0-byte stdout file behind it because its output had been
    # shell-redirected by the launcher, so the cause of death is unrecorded.
    # Base role s6: never shell-redirect a background job; write from the
    # program. Opened BEFORE the workspace receipt so the receipt is in it.
    log = _TeeLog(_vardir.resolve(_db.load_config())
                  / ("consumer-%s.log" % _daemon._safe(
                      args.worker_id or _loop.default_worker_id())))
    log("[viv] log file: %s" % log.path)
    log("[viv] workspace %s" % _json.dumps(ws))
    if not ws["detached"]:
        log("[viv] NOTE: rule 6 wants a long-lived process on a DETACHED "
            "pinned SHA; this worktree is on branch %r. The run proceeds "
            "and the receipt records the branch, so what actually executed "
            "is never in doubt." % ws["branch"])
    if ws["dirty"]:
        log("[viv] NOTE: tracked files are modified in this worktree. The "
            "SHA above does not describe what is running.")
    try:
        d = _daemon.Daemon(worker_id=args.worker_id, schema=args.schema,
                           idle_interval_s=args.interval, log=log)
    except _daemon.BoundNotDeclared as exc:
        log("[viv] REFUSING TO START: %s" % exc)
        return _daemon.EXIT_PARKED
    log("[viv] park record would be: %s" % d.park_file)
    try:
        return d.run(max_ticks=1 if args.once else args.max_ticks,
                     stop_when_idle=args.stop_when_idle)
    finally:
        log.close()


class _TeeLog:
    """print() plus an append-only file, flushed on every line."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(path, "a", encoding="utf-8")

    def __call__(self, *parts) -> None:
        line = " ".join(str(x) for x in parts)
        print(line)
        try:
            sys.stdout.flush()
        except Exception:                               # noqa: BLE001, S110
            pass
        try:
            self._fh.write("%s %s\n" % (
                _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                line))
            self._fh.flush()
        except Exception:                               # noqa: BLE001, S110
            pass

    def close(self) -> None:
        try:
            self._fh.close()
        except Exception:                               # noqa: BLE001, S110
            pass


def _worker_row(conn, worker_id, schema):
    for w in _q.workers(conn, schema=schema):
        if w["worker_id"] == worker_id:
            return w
    return None


def _worker_var_dir(row) -> Path | None:
    """The state directory the RUNNING worker reported, if its build did."""
    if not row:
        return None
    b = row.get("build") or {}
    if isinstance(b, str):
        try:
            b = _json.loads(b)
        except ValueError:
            b = {}
    v = b.get("var_dir")
    return Path(v) if v else None


def cmd_stop(args, conn) -> int:
    """Ask a running consumer to stop AFTER its current tick.

    The alternative, and the only one that existed before this, is killing the
    process. A kill mid-attempt strands the row: the queue records it as
    claimed by a worker that is gone, and nothing may adopt it, because
    guessing that a stranded run did not happen is the guess that runs one
    experiment twice. So a restart used to cost either a stranded row or a
    wait, and on 2026-09-10 it cost a campaign both -- 48 rows executed on an
    interpreter four hours older than the fix they needed, because restarting
    to pick it up would have stranded the row in flight.

    This writes a flag the daemon checks BETWEEN ticks. The current attempt
    always finishes; the stop lands where nothing is claimed.
    """
    # C7. The flag used to be written beside THIS checkout's package, and
    # `stop` reported success with the path it had just written -- while the
    # daemon, running from its pinned worktree, read a different directory.
    # Now: the flag goes where the RUNNING worker said its state lives (its
    # heartbeat carries var_dir), and if no live worker can be seen the
    # command REFUSES rather than writing a flag nothing will read.
    row = _worker_row(conn, args.worker_id, args.schema)
    conn.close()
    local = _vardir.resolve(_db.load_config())
    var = _worker_var_dir(row) or local
    path = _daemon.stop_file_for(var, args.worker_id)
    if args.clear:
        if path.exists():
            path.unlink()
            print("cleared %s" % path)
        else:
            print("no stop flag at %s" % path)
        return 0
    now = _dt.datetime.now(_dt.timezone.utc)
    age = (now - row["last_seen"]).total_seconds() if row else None
    if row is None or age > args.stale_after:
        if not args.force:
            print("REFUSING: no live heartbeat for worker %s (%s). A flag "
                  "written now would be read by nothing. If a consumer is "
                  "running under that id and its heartbeat is merely stale "
                  "(a long row; backlog C2), re-issue with --force and the "
                  "flag lands at %s"
                  % (args.worker_id,
                     "no heartbeat row" if row is None
                     else "last seen %.0fs ago, stale after %.0fs"
                          % (age, args.stale_after), path))
            return 1
        print("NOTE: forcing; heartbeat is %s"
              % ("absent" if row is None else "%.0fs stale" % age))
    if _worker_var_dir(row) is None and row is not None:
        print("NOTE: the running worker's build reports no var_dir (a build "
              "before C7); writing beside this checkout at %s. If the daemon "
              "runs from another worktree this flag will not be read." % var)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("requested by %s at %s\n" % (args.by, now.isoformat()),
                    encoding="utf-8")
    print("stop requested for %s (pid %s on %s, heartbeat %.0fs ago)\n"
          "  flag: %s\n"
          "The daemon finishes its current tick and exits with nothing "
          "claimed. It clears the flag on the way out; `--clear` removes it "
          "by hand if the daemon is not running."
          % (args.worker_id, row["pid"] if row else "?",
             row["host"] if row else "?", age or 0.0, path))
    return 0


def cmd_unpark(args, conn) -> int:
    """Record the explicit clearance rule 10 requires, then let `run` start.

    The park record is never deleted: it is renamed to
    park-<worker>.cleared-<utc>.json with the clearance appended, so the
    history of parks and who cleared them stays readable. A restart without
    this command is refused by the daemon."""
    if not (args.reason or "").strip():
        print("REFUSING: --reason is required; a clearance without a reason "
              "is a restart with a nicer name")
        return 1
    row = _worker_row(conn, args.worker_id, args.schema)
    conn.close()
    local = _vardir.resolve(_db.load_config())
    var = _worker_var_dir(row) or local
    rec = _daemon.read_park(var, args.worker_id)
    if rec is None and var != local:
        var = local
        rec = _daemon.read_park(var, args.worker_id)
    path = _daemon.park_file_for(var, args.worker_id)
    if rec is None:
        print("no park record for %s at %s (nothing to clear)"
              % (args.worker_id, path))
        return 0
    now = _dt.datetime.now(_dt.timezone.utc)
    rec["cleared"] = {"by": args.by, "at": now.isoformat(),
                      "reason": args.reason}
    dest = path.with_name("%s.cleared-%s.json"
                          % (path.stem, now.strftime("%Y%m%dT%H%M%SZ")))
    dest.write_text(_json.dumps(rec, indent=2, default=str), encoding="utf-8")
    path.unlink()
    print("unparked %s (%s: %s)\n  clearance recorded at %s\n  by %s: %s"
          % (args.worker_id, rec.get("kind"), rec.get("reason"), dest,
             args.by, args.reason))
    return 0


def cmd_scope_reconcile(args, conn) -> int:
    """B1 recurrence by hand: extend the declared read scopes with this
    owner's newly eligible worlds (add-only, idempotent). Prints the record;
    a receipt lands in var_dir either way."""
    conn.close()
    _workspace.assert_not_canonical("reconcile read scopes", allow_override=False)
    v = _loop.Vivarium(schema=args.schema, log=print)
    rec = v.reconcile_scopes(trigger="cli", dry_run=args.dry_run)
    print(_j(rec))
    if args.receipt:
        Path(args.receipt).write_text(_j(rec) + "\n", encoding="utf-8")
    return 0 if not any("error" in s for s in rec.get("scopes", [])) else 1


def cmd_tick(args, conn) -> int:
    """Exactly one tick, reported as JSON. The unit the daemon drives."""
    _workspace.assert_not_canonical("execute a tick", allow_override=False)
    v = _loop.Vivarium(worker_id=args.worker_id, schema=args.schema,
                       log=(lambda *a: None) if args.quiet else print)
    report = v.tick(conn)
    print(_j(report.as_dict()))
    return 0 if report.outcome != _loop.BLOCKED else 2


def cmd_health(args, conn) -> int:
    """Machine-readable health: is Vivarium alive, and what has it done."""
    workers = _q.workers(conn, schema=args.schema)
    counts = _q.counts(conn, schema=args.schema)
    st = _q.stranded(conn, stale_after_s=args.stale_after, schema=args.schema)
    now = datetime.now(timezone.utc)
    out = {
        "schema": args.schema or _db.schema(),
        "queue": counts,
        "queued_now": counts.get("queued", 0),
        "slot_held_by": None,
        "stranded": [str(r["experiment_id"]) for r in st],
        "workers": [{"worker_id": w["worker_id"],
                     "host": w["host"], "pid": w["pid"],
                     "age_s": round((now - w["last_seen"]).total_seconds(), 1),
                     "alive": (now - w["last_seen"]).total_seconds() < 60,
                     "current": str(w["current_experiment"])
                                if w["current_experiment"] else None,
                     "parked": _daemon.read_park(
                         _worker_var_dir(w) or _vardir.resolve(
                             _db.load_config(), create=False),
                         w["worker_id"]),
                     "build": w["build"]}
                    for w in workers],
    }
    active = _q.active(conn, schema=args.schema)
    if active is not None:
        out["slot_held_by"] = {"experiment_id": str(active["experiment_id"]),
                               "status": active["status"],
                               "claimed_by": active["claimed_by"]}
    out["healthy"] = (not st) and any(w["alive"] for w in out["workers"])
    print(_j(out))
    return 0 if out["healthy"] else 1


def cmd_stalls(args, conn) -> int:
    """Engine-stall episodes, reconstructed from the register."""
    from . import stalls as _stalls
    print(_j(_stalls.episodes(conn, since=args.since, schema=args.schema)))
    return 0


def cmd_orphans(args, conn) -> int:
    """Classify Daedalus's committed-but-unobserved scan against this register.

    Their scan finds the scar and refuses to classify it, because whether a
    queued work item will ever be claimed is a fact about THIS register. Feed
    it in:

        python deploy/orphaned_commits.py --json > scan.txt
        python -m viv.cli orphans --scan scan.txt --ledger <engine.db>

    `--ledger` is READ ONLY and supplies world names only. Without it the scan
    cannot distinguish another producer's orphan from one this runner made with
    no register row behind it -- which is the worse of the two.
    """
    import sqlite3
    from . import stalls as _stalls

    raw = Path(args.scan).read_text(encoding="utf-8", errors="replace")
    # THE SCAN PRINTS A HUMAN HEADER BEFORE ITS JSON, so `json.load` on the
    # whole stream fails. Take the document, not the stream.
    doc = json.loads(raw[raw.index("{"):])
    found = doc["found"]

    names = None
    if args.ledger:
        ids = [f["world_id"] for f in found]
        c = sqlite3.connect("file:%s?mode=ro" % Path(args.ledger).as_posix(),
                            uri=True)
        try:
            names = dict(c.execute(
                "SELECT world_id, name FROM worlds WHERE world_id IN (%s)"
                % ",".join("?" * len(ids)), ids)) if ids else {}
        finally:
            c.close()

    out = _stalls.classify_orphans(found, conn, schema=args.schema,
                                   world_names=names)
    out["scan"] = {"committed": doc.get("committed_experiments"),
                   "unobserved": doc.get("committed_without_observation"),
                   "db": doc.get("db")}
    print(_j(out))
    return 0


def cmd_errata(args, conn) -> int:
    """Declared contamination, and the exclusion it implies."""
    with _db.dict_cur(conn) as cur:
        s = args.schema or _db.schema()
        cur.execute("SELECT erratum_id, declared_at, declared_by, kind, "
                    "reason, detail FROM " + s + ".register_errata "
                    "ORDER BY erratum_id")
        errata = cur.fetchall()
        cur.execute("SELECT count(*) n FROM " + s + ".research_experiment_queue")
        total = cur.fetchone()["n"]
        cur.execute("SELECT count(*) n FROM " + s + ".register_clean")
        clean = cur.fetchone()["n"]
    if not errata:
        print("no errata declared; register_clean == the whole register (%d)"
              % total)
        return 0
    for e in errata:
        with _db.dict_cur(conn) as cur:
            cur.execute("SELECT count(*) n FROM " + (args.schema or _db.schema())
                        + ".register_errata_rows WHERE erratum_id = %s",
                        (e["erratum_id"],))
            n = cur.fetchone()["n"]
        print("erratum %d  %s  %s  rows=%d" % (e["erratum_id"], e["kind"],
                                               e["declared_at"], n))
        print("  " + e["reason"][:400])
        print("  rule: " + str(e["detail"].get("exclusion_rule", ""))[:300])
    print("")
    print("register: %d rows, %d clean, %d excluded"
          % (total, clean, total - clean))
    return 0


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
    s.add_argument("--request-key", default=None,
                   help="idempotency key; a resubmission is refused")
    s.add_argument("--replication-of", default=None,
                   help="experiment_id this deliberately repeats")
    s.add_argument("--family", default=None, help="comparison family id")
    s.add_argument("--arm", default=None, help="arm within the family")
    s.add_argument("--candidate-set", default=None,
                   help="candidate-set id this row belongs to")
    s.set_defaults(fn=cmd_enqueue)

    sub.add_parser("kinds").set_defaults(fn=cmd_kinds)
    sub.add_parser("limits").set_defaults(fn=cmd_limits)
    p_stop = sub.add_parser("stop")
    p_stop.add_argument("--worker-id", default=_loop.default_worker_id())
    p_stop.add_argument("--by", default="operator")
    p_stop.add_argument("--clear", action="store_true",
                        help="remove the flag instead of setting it")
    p_stop.add_argument("--stale-after", type=float, default=900.0,
                        help="refuse if the worker's heartbeat is older (s)")
    p_stop.add_argument("--force", action="store_true",
                        help="write the flag even with no live heartbeat")
    p_stop.set_defaults(fn=cmd_stop)

    s = sub.add_parser("unpark", help="record the clearance a rule-10 park "
                                      "needs before `run` will start")
    s.add_argument("--worker-id", default=_loop.default_worker_id())
    s.add_argument("--by", required=True)
    s.add_argument("--reason", required=True)
    s.set_defaults(fn=cmd_unpark)

    s = sub.add_parser("sfe-identity",
                       help="the DURABLE SFE client identity (one per role)")
    s.add_argument("--ensure", action="store_true",
                   help="register once if absent, and persist it")
    s.add_argument("--role", default=_identity.ROLE_PRODUCTION,
                   choices=[_identity.ROLE_PRODUCTION, _identity.ROLE_TEST])
    s.set_defaults(fn=cmd_sfe_identity)

    s = sub.add_parser("family")
    s.add_argument("family_id")
    s.set_defaults(fn=cmd_family)

    s = sub.add_parser("candidates")
    s.add_argument("candidate_set_id")
    s.set_defaults(fn=cmd_candidates)

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

    s = sub.add_parser("run", help="the daemon: a thin loop around tick()")
    s.add_argument("--once", action="store_true", help="exactly one tick")
    s.add_argument("--max-ticks", type=int, default=None)
    s.add_argument("--stop-when-idle", action="store_true",
                   help="exit 0 the first time the queue is empty")
    s.add_argument("--interval", type=float, default=None)
    s.add_argument("--worker-id", default=None)
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("scope-reconcile", help="B1 recurrence: extend the "
                       "declared read scopes with newly eligible owner worlds")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--receipt", default=None)
    s.set_defaults(fn=cmd_scope_reconcile)

    s = sub.add_parser("tick", help="exactly one tick, reported as JSON")
    s.add_argument("--worker-id", default=None)
    s.add_argument("--quiet", action="store_true")
    s.set_defaults(fn=cmd_tick)

    s = sub.add_parser("health", help="machine-readable health")
    s.add_argument("--stale-after", type=float, default=900.0)
    s.set_defaults(fn=cmd_health)

    s = sub.add_parser("stalls", help="engine-stall episodes from the register")
    s.add_argument("--since", default="2026-09-01")
    s.set_defaults(fn=cmd_stalls)

    s = sub.add_parser("orphans",
                       help="classify a committed-but-unobserved scan")
    s.add_argument("--scan", required=True,
                   help="output of deploy/orphaned_commits.py --json")
    s.add_argument("--ledger", default=None,
                   help="engine.db, READ ONLY, for world names")
    s.set_defaults(fn=cmd_orphans)

    sub.add_parser("errata",
                   help="declared contamination and the exclusion rule"
                   ).set_defaults(fn=cmd_errata)
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
