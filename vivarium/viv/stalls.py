"""Engine write-path stalls, reconstructed from the register.

WHY THIS LIVES HERE AND NOT IN THE ENGINE. Daedalus traced the failure path on
2026-09-11 (their backlog A6): when SQLite's `BEGIN IMMEDIATE` exceeds its lock
wait, the engine raises past its own FoundryError handler as an unhandled 500
and writes NOTHING. It cannot write anything -- recording the incident would
need the very lock that just failed, so any fix that logs to the same ledger
through the same lock is circular.

The consequence is that **the engine's hash chain is silent precisely when the
engine is the thing that failed**, and the queue is the only place the episode
is recorded at all. That is not a workaround. Until there is a record outside
SQLite, this register IS the outside record, and it should be readable as one
rather than reconstructed with ad-hoc SQL by whoever happens to look.

WHAT AN EPISODE IS. A run of failures that died in the ENGINE rather than in
the science, clustered in time, with the completions in the same window counted
beside them. Zero completions during a run of failures is the signature of a
stall; failures scattered among successes are something else and are reported
as a weaker episode rather than silently merged.

THE CONTIGUITY CHECK IS THE POINT, and it is generalised deliberately. The 13
rows lost on 2026-09-11 were rules 143-155 of a 256-rule map -- a BLOCK, not a
sample. A contiguous hole in a swept parameter is the shape most likely to be
read as a property of the parameter, because the parameter is the x-axis of
whatever gets plotted. It was contiguous for a boring reason (consecutive in
the issue order, seventeen minutes of stall) and nothing in the resulting map
records that. So this looks for ANY integer payload field whose failed values
form a contiguous run, rather than knowing about `rule_number` -- the next
campaign will sweep something else.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from . import db as _db
from . import queue as _queue

#: Failure text that means the ENGINE did not answer, as distinct from the
#: science failing. Matched on the recorded error because these rows never
#: reach a failure_class -- they die before the boundary is crossed.
_ENGINE_MARKS = (
    ("TIMEOUT", ("timed out", "timeout")),
    ("HTTP_500", ("http 500", "internal_error", "unhandled server error")),
    ("CONN_REFUSED", ("connection refused", "actively refused",
                      "connection aborted")),
)

#: Two failures further apart than this are different episodes. Generous on
#: purpose: the 2026-09-11 stall ran 17 minutes with gaps of minutes between
#: rows, because each failing row spent its timeout before giving up.
GAP_S = 600.0


def _shape(error: str) -> Optional[str]:
    low = (error or "").lower()
    for name, marks in _ENGINE_MARKS:
        if any(m in low for m in marks):
            return name
    return None


def _failing_call(error: str) -> Optional[str]:
    """The sfclient method the run died in -- the LAST client frame.

    WHICH CALL IT WAS IS THE WHOLE QUESTION, because it decides whether an
    experiment exists in the engine that the register does not name. On
    2026-09-11 the 13 lost rows split three ways once this was read correctly:
    8 at `create_world` (nothing created), 1 at `experiment` (the commit call
    itself timed out), and 4 at `audit_envelope` (committed, then the read
    failed). Checking the engine afterwards resolved the ambiguous one --
    rule 146's commit HAD landed server-side -- so five experiments were
    orphaned, not four and not zero.

    I first reported all 13 as `create_world` because the regex below matched
    http.client as well as sfclient and returned `begin`. A record describing
    something other than what happened is the defect this module exists to
    surface, and it was in the module.
    """
    import re
    # MATCH THE PATH, NOT JUST THE FILENAME. `client.py` alone also matches
    # H:\Python312\Lib\http\client.py, so the first version of this reported
    # `begin` and `_read_status` -- http.client internals -- as the failing
    # call, and the real frame never appeared. It is the same defect this
    # module exists to surface: a record describing something other than what
    # happened.
    frames = re.findall(r'File "[^"]*sfclient[^"]*client\.py", line \d+, '
                        r'in (\w+)', error or "")
    for f in reversed(frames):
        if not f.startswith("_"):
            return f
    # THE VIV FRAME BEATS A PRIVATE CLIENT HELPER, and this cost a second
    # wrong answer before it was noticed. The five orphaned h5 runs have
    # exactly one sfclient frame, `_req`, under `audit_envelope` in
    # viv/runner.py -- so returning the last client frame named `_req`, which
    # says only "an HTTP request", when the frame above it says the run had
    # ALREADY COMMITTED and was reading the envelope back. Same defect as the
    # http.client one above: a name that is not the name of what happened.
    ours = re.findall(r'File "[^"]*[\\/]viv[\\/](?:\w+)\.py", line \d+, '
                      r'in (\w+)', error or "")
    for f in reversed(ours):
        if not f.startswith("_"):
            return f
    if ours:
        return ours[-1]
    return frames[-1] if frames else None


def _contiguous_runs(values: List[int]) -> List[List[int]]:
    out, run = [], []
    for v in sorted(set(values)):
        if run and v == run[-1] + 1:
            run.append(v)
        else:
            if run:
                out.append(run)
            run = [v]
    if run:
        out.append(run)
    return out


def _sweep_gaps(rows: List[dict]) -> List[dict]:
    """Integer payload fields whose FAILED values form a contiguous block."""
    fields: Dict[str, List[int]] = {}
    for r in rows:
        payload = ((r.get("experiment_spec") or {}).get("work") or {}
                   ).get("payload") or {}
        for k, v in payload.items():
            if isinstance(v, int) and not isinstance(v, bool):
                fields.setdefault(k, []).append(v)
    out = []
    for k, vals in sorted(fields.items()):
        if len(set(vals)) < 3:
            continue                      # two points are always "contiguous"
        runs = _contiguous_runs(vals)
        longest = max(runs, key=len)
        if len(longest) == len(set(vals)) and len(longest) >= 3:
            out.append({
                "field": k, "contiguous": True,
                "from": longest[0], "to": longest[-1], "n": len(longest),
                "why_it_matters":
                    "a block-shaped hole in a swept parameter is the shape "
                    "most likely to be read as a property of that parameter. "
                    "The readout should name the gap, not just the count."})
    return out


def episodes(conn=None, *, since: str = "2026-09-01", schema=None) -> dict:
    """Engine-stall episodes in the register, newest last."""
    s = schema or _db.schema()
    close = conn is None
    conn = conn or _db.connect()
    try:
        with _db.dict_cur(conn) as cur:
            cur.execute(
                "SELECT experiment_id, finished_at, started_at, error, "
                "candidate_set_id, arm_id, experiment_spec, "
                "experiment_spec #>> '{work,kind}' AS kind "
                "FROM " + s + ".research_experiment_queue "
                "WHERE status='failed' AND finished_at >= %s "
                "ORDER BY finished_at", (since,))
            failed = [dict(r) for r in cur.fetchall()]
            cur.execute(
                "SELECT finished_at FROM " + s + ".research_experiment_queue "
                "WHERE status='completed' AND finished_at >= %s", (since,))
            done = [r["finished_at"] for r in cur.fetchall()]
    finally:
        if close:
            conn.close()

    engine_failed = []
    for r in failed:
        sh = _shape(r.get("error") or "")
        if sh:
            r["shape"] = sh
            r["failing_call"] = _failing_call(r.get("error") or "")
            engine_failed.append(r)

    out: List[dict] = []
    current: List[dict] = []
    for r in engine_failed:
        if current and (r["finished_at"] - current[-1]["finished_at"]
                        ).total_seconds() > GAP_S:
            out.append(current)
            current = []
        current.append(r)
    if current:
        out.append(current)

    episodes_out = []
    for group in out:
        start, end = group[0]["finished_at"], group[-1]["finished_at"]
        inside = [d for d in done if start <= d <= end]
        shapes: Dict[str, int] = {}
        calls: Dict[str, int] = {}
        for r in group:
            shapes[r["shape"]] = shapes.get(r["shape"], 0) + 1
            if r["failing_call"]:
                calls[r["failing_call"]] = calls.get(r["failing_call"], 0) + 1
        episodes_out.append({
            "start_utc": start.isoformat(), "end_utc": end.isoformat(),
            "duration_s": round((end - start).total_seconds(), 1),
            "failed": len(group),
            "completed_in_window": len(inside),
            # A stall is failures with NOTHING succeeding beside them. Failures
            # scattered among successes are a different animal and are said to
            # be one rather than quietly merged into the same word.
            # A SINGLE failure in a zero-width window is not a stall, it is
            # one failure. Claiming "total" there would put an isolated
            # timeout in the same category as seventeen minutes of silence.
            "total_stall": len(inside) == 0 and (len(group) > 1
                                                 or (end - start).total_seconds() > 0),
            "shapes": shapes,
            "failing_calls": calls,
            "candidate_sets": sorted({r["candidate_set_id"] for r in group
                                      if r["candidate_set_id"]}),
            "arms": sorted({r["arm_id"] for r in group if r["arm_id"]}),
            "kinds": sorted({r["kind"] for r in group if r["kind"]}),
            "experiment_ids": [str(r["experiment_id"]) for r in group],
            "sweep_gaps": _sweep_gaps(group),
            "terminal": True,
            "note": "these rows are TERMINAL. This seat never requeues -- "
                    "nothing in the queue can know whether an experiment ran, "
                    "and guessing that a stranded run did not happen is the "
                    "guess that runs one twice. Re-admission is the "
                    "producer's.",
        })
    return {
        "schema": "vivarium.engine_stalls.v1",
        "since": since,
        "n_episodes": len(episodes_out),
        "episodes": episodes_out,
        "why_this_exists":
            "the engine cannot record a lock-wait failure -- writing the "
            "incident needs the lock that failed (Daedalus A6) -- so the "
            "register is the only surviving record of one.",
    }


# ---------------------------------------------------------------------------
# The verdict Daedalus's scan deliberately withholds
# ---------------------------------------------------------------------------
#: States meaning the register will never claim that work again. Imported from
#: the queue rather than restated, because "terminal" is the queue's word and a
#: second copy of it here would be a second definition, free to drift.
_TERMINAL = _queue.TERMINAL
_LIVE = ("queued",) + _queue.ACTIVE

ABANDONED = "ABANDONED"
PENDING = "PENDING"
INCONSISTENT = "INCONSISTENT"
NOT_OURS = "NOT_FROM_THIS_REGISTER"
UNREGISTERED = "RUNNER_MADE_UNREGISTERED"


def _derived_name(spec_hash: str) -> Optional[str]:
    """What `viv/spec.py` would have named the world for that sealed hash."""
    if not (spec_hash or "").startswith("sha256:"):
        return None
    return "viv-" + spec_hash[7:23]


def classify_orphans(found: List[dict], conn=None, *, schema=None,
                     world_names: Optional[Dict[str, str]] = None) -> dict:
    """Decide which committed-but-unobserved SFE experiments are abandoned.

    Daedalus's `deploy/orphaned_commits.py` finds the SCAR a stall leaves -- an
    experiment committed to the ledger with no observation against it -- and
    then REFUSES to classify it. Their first cut did classify, on whether the
    world still held outstanding work, and it returned all five of the runs I
    had already confirmed abandoned as "pending": every one of those worlds
    still holds a QUEUED work item, 0.6-0.9h idle, that nobody will ever claim.
    Holding work is not evidence of progress, and from the ledger alone the two
    cases are indistinguishable.

    So the verdict came here, and correctly: whether a queued work item will
    ever be claimed is a fact about this register. The join is `spec_hash`,
    which their scan reports on every row, and the answer is not a probability
    -- the queue's BEFORE UPDATE trigger freezes a terminal row whole, so a
    terminal row CANNOT be claimed again. ABANDONED is a statement about the
    state machine.

    THE FOURTH VERDICT IS THE HONEST ONE. An orphan whose spec_hash matches no
    row here was not produced by this register -- a probe, a test, another
    producer -- and calling it abandoned would be claiming authority over
    something outside the very boundary this classification exists to respect.

    THE FIFTH IS THE UNCOMFORTABLE ONE, and it only appears if the caller
    supplies `world_names`. The world name is DERIVED, `viv-<spec_hash[7:23]>`,
    so the engine records which orphans came out of this runner whether or not
    a row ever sealed them. On the first real run, 7 of the 86 the register
    could not name were `viv-` worlds: `evaluate_bitstring` and `noop_v0` runs
    from 2026-09-06, when v0 was being brought up by calling the runner
    directly. The register holds 35 rows of those same two kinds and not one of
    these. So they were executed straight against the engine with no queue row
    behind them -- which means this seat can write to the ledger in a way that
    leaves an orphan NOBODY can ever adjudicate, mine or anyone's. Folding that
    into NOT_FROM_THIS_REGISTER would have filed my own unaccountable writes
    under "someone else's problem".

    `world_names` maps world_id -> name and is the CALLER'S to supply. This
    module does not open the engine's ledger: reading another seat's store
    directly to answer a question about my own register is the coupling that
    makes both sides unmovable.
    """
    s = schema or _db.schema()
    close = conn is None
    conn = conn or _db.connect()
    hashes = sorted({r["spec_hash"] for r in found if r.get("spec_hash")})
    rows: Dict[str, List[dict]] = {}
    try:
        with _db.dict_cur(conn) as cur:
            cur.execute(
                "SELECT experiment_id, spec_hash, status, candidate_set_id, "
                "arm_id, sfe_experiment_id, finished_at, "
                "result_summary #>> '{failure_class}' AS failure_class "
                "FROM " + s + ".research_experiment_queue "
                "WHERE spec_hash = ANY(%s)", (hashes,))
            for r in cur.fetchall():
                rows.setdefault(r["spec_hash"], []).append(dict(r))
    finally:
        if close:
            conn.close()

    out: List[dict] = []
    counts: Dict[str, int] = {}
    for orphan in found:
        mine = rows.get(orphan.get("spec_hash")) or []
        named = [m for m in mine if m["sfe_experiment_id"] == orphan["exp_id"]]
        if not mine:
            derived = _derived_name(orphan.get("spec_hash") or "")
            actual = (world_names or {}).get(orphan.get("world_id"))
            if actual is not None and derived is not None and actual == derived:
                verdict = UNREGISTERED
                why = ("the world carries this runner's DERIVED name (%s), so "
                       "this seat made it -- but no row seals the spec, so it "
                       "was executed with no register row behind it. Nobody "
                       "can adjudicate this orphan, including me." % derived)
            elif actual is not None:
                verdict = NOT_OURS
                why = ("world named %r, not this runner's derived %r. Another "
                       "producer's -- not this queue's to judge."
                       % (actual, derived))
            else:
                verdict = NOT_OURS
                why = ("no row in this register seals that spec. Not this "
                       "queue's to judge -- a probe, a test run, or another "
                       "producer. NOTE: without world_names this cannot be "
                       "separated from work THIS runner made outside the "
                       "queue, which is a different and worse thing.")
        elif any(m["status"] in _LIVE for m in mine):
            verdict = PENDING
            why = ("a row for this spec is still live (%s), so the work may "
                   "yet be claimed."
                   % ", ".join(sorted({m["status"] for m in mine
                                       if m["status"] in _LIVE})))
        elif any(m["status"] == "completed" for m in named):
            verdict = INCONSISTENT
            why = ("a row records THIS experiment as completed while the "
                   "ledger holds no observation for it. Both records cannot "
                   "be right and neither is self-evidently wrong.")
        else:
            verdict = ABANDONED
            why = ("every row for this spec is terminal (%s) and a terminal "
                   "row is frozen whole by the queue's trigger, so nothing "
                   "will claim that work again."
                   % ", ".join(sorted({m["status"] for m in mine})))
            if any(m["status"] == "completed" for m in mine):
                why += (" A completed row names a DIFFERENT experiment, so "
                        "this one was abandoned and the spec later re-run.")
        counts[verdict] = counts.get(verdict, 0) + 1
        out.append({
            "exp_id": orphan["exp_id"],
            "world_id": orphan.get("world_id"),
            "spec_hash": orphan.get("spec_hash"),
            "age_hours": orphan.get("age_hours"),
            "unclaimed_work": orphan.get("unclaimed_work"),
            "verdict": verdict,
            "why": why,
            "named_by_a_row": bool(named),
            "rows": [{"experiment_id": str(m["experiment_id"]),
                      "status": m["status"],
                      "candidate_set_id": m["candidate_set_id"],
                      "arm_id": m["arm_id"],
                      "failure_class": m["failure_class"],
                      "names_this_experiment":
                          m["sfe_experiment_id"] == orphan["exp_id"]}
                     for m in mine],
        })
    return {
        "schema": "vivarium.orphan_verdicts.v1",
        "n": len(out),
        "counts": counts,
        "verdicts": out,
        "world_names_supplied": bool(world_names),
        "note": "ABANDONED is a statement about the STATE MACHINE and not an "
                "estimate: a terminal row is frozen whole by the queue's "
                "BEFORE UPDATE trigger, so its work cannot be claimed again. "
                "PENDING means a live row still exists. NOT_FROM_THIS_REGISTER "
                "is not a judgement, it is the boundary -- this seat has no "
                "standing over an orphan it did not produce. "
                "RUNNER_MADE_UNREGISTERED needs world_names and is the one to "
                "read first: work this runner committed with no register row "
                "behind it, which nobody can adjudicate.",
    }
