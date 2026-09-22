"""Redis-free local execution of the standard job contract.

The reuse survey's finding: a job in this codebase is just `fn(ctx, **kwargs)` and
`ctx` is never type-checked (`primordial/fabric/worker.py:374`). The broker, the
worker, the consumer groups and the `pm:rows:<lane>` round trip are all SUPERVISOR
behaviour, not job behaviour. Tests have exploited that for a long time with
throwaway stub ctxs; production does it too (`metric/r16_cells.py:504`,
`cohorts/e/r7_clauseb_calibration.py:48`). What did not exist was a shipped,
reusable version — so every caller rewrote it.

This is that helper. It buys the campaign:
  * no Redis, no broker, no worker, no schtasks, no Claude session
  * durable, git-committed rows via the repo's own RowWriter
  * row-vocabulary enforcement via envelope.prepare_row (the G1 lint)
  * envelope admission as an explicit, auditable step

What it deliberately does NOT provide (supervisor behaviour, absent by design):
CPU-token fairness, enforced ceilings, CPU/wall TTL kills, checkpoint/resume,
`pm:jobs:<L>:done` records, telemetry. If an experiment needs those, it wants the
real fabric — and with it the `F:/Prometheus-worktrees` path table that makes the
fabric unportable (`ops/round_clock.py:45-54`).

Portability note: this module hardcodes no paths, no ports, no drive letters and
no interpreter. It needs a git worktree and PM_TAG, and it says so by failing
closed rather than by guessing.
"""
from __future__ import annotations

import os
import pathlib


class MissingPrerequisite(RuntimeError):
    """Fail closed with an actionable message rather than a deep library traceback."""


class LocalCtx:
    """The five-method ctx the job contract actually uses, plus the optional extras.

    Rows go straight to the writer. `prepare_row` is kept in the path on purpose:
    it is what enforces the status vocabulary, and dropping it is how rows that
    later fail the close sweep get written.
    """

    __slots__ = ("_w", "envelope", "n", "cache", "segment", "job_id", "job_key",
                 "_state", "_pause", "rows")

    def __init__(self, writer, envelope, *, job_key="", segment=0, keep_rows=False):
        self._w = writer
        self.envelope = envelope
        self.n = 0
        self.cache = {}
        self.segment = segment
        self.job_id = job_key or "local"
        self.job_key = job_key
        self._state = None
        self._pause = False
        self.rows = [] if keep_rows else None

    def emit(self, row):
        from primordial.fabric import envelope as EV
        stamped = EV.prepare_row(row, self.n, self.envelope)
        if self._w is not None:
            self._w.write(stamped)
        if self.rows is not None:
            self.rows.append(stamped)
        self.n += 1
        return stamped

    def load_checkpoint(self):
        return self._state

    def checkpoint(self, state):
        self._state = state

    def should_pause(self):
        return self._pause

    def pause(self, state, completed_units=0, remaining_units=0):
        self._state, self._pause = state, True

    def progress(self, *_a, **_kw):
        pass


def check_prerequisites(rows_path):
    """Assert the two things RowWriter needs, with a message that says what to do."""
    tag = os.environ.get("PM_TAG", "")
    if not tag or tag == "untagged":
        raise MissingPrerequisite(
            "PM_TAG must be set and not 'untagged' (primordial/fabric/rows.py:54-58). "
            "Set PM_TAG=<machine>-<8hex> before writing durable rows.")
    p = pathlib.Path(rows_path).resolve()
    for parent in [p] + list(p.parents):
        if (parent / ".git").exists():
            return tag, parent
    raise MissingPrerequisite(
        f"rows path {p} is not inside a git worktree (primordial/fabric/rows.py:104-109). "
        "Durable rows are git-committed; choose a path inside the repo.")


def run_job_locally(fn, rows_path, exp_id, envelope, kwargs=None, *,
                    admit=True, commit=True, keep_rows=False, job_key=""):
    """Run one job function against a durable RowWriter, in this process.

    fn         : callable taking (ctx, **kwargs) — the standard contract
    rows_path  : .jsonl under a git worktree
    exp_id     : experiment id stamped into rows and the commit message
    envelope   : dict from envelope.example(**overrides)
    admit      : call envelope.admit() first and REFUSE on a bad envelope.
                 Admission is pure with clock=None, so this costs nothing and
                 keeps the local path honest about ceilings.

    Returns {"ok", "reasons", "rows_written", "rows_path", "rows": [...]|None}.
    A refusal is a RETURN VALUE, matching envelope.admit's own convention.
    """
    from primordial.fabric import envelope as EV
    from primordial.fabric.rows import RowWriter

    check_prerequisites(rows_path)

    if admit:
        verdict = EV.admit(envelope, kind="cpu", clock=None)
        if not verdict.get("ok"):
            return {"ok": False, "reasons": verdict.get("reasons", []),
                    "rows_written": 0, "rows_path": str(rows_path), "rows": None}

    pathlib.Path(rows_path).parent.mkdir(parents=True, exist_ok=True)
    # commit_every_s=10**9 => exactly one commit, at close. The default 60s would
    # otherwise produce one git commit per minute per writer.
    with RowWriter(str(rows_path), exp_id, commit_every_s=10 ** 9) as w:
        ctx = LocalCtx(w, envelope, job_key=job_key, keep_rows=keep_rows)
        fn(ctx, **(kwargs or {}))
        n = ctx.n

    if commit:
        from primordial.fabric.rows import commit_path
        commit_path(str(rows_path), exp_id, note="local run")

    return {"ok": True, "reasons": [], "rows_written": n,
            "rows_path": str(rows_path), "rows": ctx.rows}
