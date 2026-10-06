"""The attempt state machine (CONTRACT s4, s5, s9, s11).

Every step is written to a durable local spool BEFORE it is acted on, so a process death leaves a state
that recover() can finish: STARTED -> EXECUTING -> EXECUTED (result + local commit) -> STAGED (blobs
durable on the remote, exposed to nobody) -> CAS_SENT -> TERMINAL. Classification uses semantic identity
(work_id, epoch_digest), never git SHAs. Leases are hints: publication checks only the chain head."""
import json
import os
import platform
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

from . import model
from . import runtime as R
from .canonical import canonical_bytes
from .gitio import AmbiguousPush, GitError, RemoteUnavailable
from .store import NAME_RE, Contention


class Outcome(str, Enum):
    PUBLISHED = "PUBLISHED"
    DUPLICATE = "DUPLICATE"
    DISAGREEMENT = "DISAGREEMENT"
    STALE = "STALE"
    REFUSED_UNAPPROVED = "REFUSED_UNAPPROVED"
    HALTED = "HALTED"
    AMBIGUOUS = "AMBIGUOUS"                    # transitional
    REMOTE_UNAVAILABLE = "REMOTE_UNAVAILABLE"  # transitional
    ABANDONED_RECOVERED = "ABANDONED_RECOVERED"
    BUSY = "BUSY"                              # a poll, not an attempt
    COMPLETE = "COMPLETE"                      # a poll, not an attempt


POINTS = ("after_head_read", "after_lease", "mid_execute", "after_execute", "after_stage", "cas_ambiguous",
          "after_cas", "after_receipt_spool", "before_lease_release")

CRASH = "CRASH"
APPLY_THEN_LOSE_ACK = "APPLY_THEN_LOSE_ACK"
LOSE_BEFORE_APPLY = "LOSE_BEFORE_APPLY"

PUBLISHABLE = ("EXECUTED", "STAGED", "CAS_SENT", "AMBIGUOUS")
MAX_CAS = 6


class InjectedCrash(Exception):
    """A simulated process death at a fault point: no cleanup runs."""


class FaultPlan:
    def __init__(self, faults=None):
        self.faults = dict(faults or {})
        unknown = set(self.faults) - set(POINTS)
        if unknown:
            raise ValueError("unknown fault points: {}".format(sorted(unknown)))


@dataclass
class AttemptReport:
    attempt_id: str
    chain_id: str
    epoch_index: int
    outcome: Outcome
    flags: frozenset = field(default_factory=frozenset)
    work_id: str = ""
    epoch_digest: str = ""
    commit: str = ""
    receipt: dict = field(default_factory=dict)


_PERSIST = ("attempt_id", "chain_id", "epoch_index", "state", "parent", "commit", "work_id", "epoch_digest",
            "flags", "started_unix", "lease_commit", "lease", "timings", "cas_pushes", "cpu_runner_s", "staged",
            "outcome", "runtime")


class _Attempt:
    def __init__(self, **kw):
        self.attempt_id, self.chain_id, self.epoch_index = "", "", 0
        self.state, self.parent, self.commit, self.work_id, self.epoch_digest = "NEW", "", "", "", ""
        self.flags, self.started_unix, self.lease_commit, self.lease = set(), 0, None, None
        self.timings, self.cas_pushes, self.cpu_runner_s, self.staged, self.outcome = {}, 0, 0.0, False, None
        self.runtime = None
        for k, v in kw.items():
            setattr(self, k, set(v) if k == "flags" else v)
        self.mark, self.contention0, self.t0 = 0, 0, time.monotonic()

    def record(self) -> dict:
        d = {k: getattr(self, k) for k in _PERSIST}
        d["flags"] = sorted(self.flags)
        return d


class Worker:
    def __init__(self, store, worker_id, *, code_sha, approved, spool_dir, clock=None, leases=True,
                 respect_leases=True, lease_ttl_s=60, runner=None, faults=None, host_label=None):
        if not NAME_RE.match(worker_id or ""):
            raise ValueError("worker_id must match " + NAME_RE.pattern)
        self.store = store
        self.worker_id = worker_id
        self.code_sha = code_sha
        self.approved = approved
        self.spool_dir = spool_dir
        self.clock = clock or time.time
        self.leases = leases
        self.respect_leases = respect_leases
        self.lease_ttl_s = lease_ttl_s
        self.runner = runner
        self.faults = faults or FaultPlan()
        self.host_label = host_label
        self.executions = 0
        self._verified = set()
        self._cas_fault_used = False
        for d in ("attempts", "receipts"):
            os.makedirs(os.path.join(spool_dir, d), exist_ok=True)

    # -------------------------------------------------------------------------------------------- spool

    def _path(self, kind, name):
        return os.path.join(self.spool_dir, kind, name + ".json")

    def _write_durable(self, path, data: bytes):
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def _save(self, att):
        self._write_durable(self._path("attempts", att.attempt_id),
                            json.dumps(att.record(), sort_keys=True, separators=(",", ":")).encode("utf-8"))

    def _drop(self, att):
        try:
            os.remove(self._path("attempts", att.attempt_id))
        except FileNotFoundError:
            pass

    def _spooled(self) -> list:
        d, out = os.path.join(self.spool_dir, "attempts"), []
        for name in sorted(os.listdir(d)):
            if name.endswith(".json"):
                with open(os.path.join(d, name), "rb") as f:
                    out.append(_Attempt(**json.loads(f.read().decode("utf-8"))))
        return sorted(out, key=lambda a: (a.started_unix, a.attempt_id))

    # -------------------------------------------------------------------------------------------- faults

    def _hook(self, point, ctx=None):
        act = self.faults.faults.get(point)
        if act is None or point == "cas_ambiguous":
            return
        if act == CRASH:
            raise InjectedCrash(point)
        if callable(act):
            act(self, ctx or {})

    def _cas_wrap(self):
        act = self.faults.faults.get("cas_ambiguous")
        if act is None:
            return None

        def wrap(real_push):
            if self._cas_fault_used:
                return real_push()
            self._cas_fault_used = True
            if act == APPLY_THEN_LOSE_ACK:
                real_push()
                raise AmbiguousPush("injected: applied, acknowledgement lost")
            if act == LOSE_BEFORE_APPLY:
                raise AmbiguousPush("injected: lost before it applied")
            if act == CRASH:
                raise InjectedCrash("cas_ambiguous")
            return act(self, {"push": real_push})

        return wrap

    # -------------------------------------------------------------------------------------------- entry points

    def run_attempt(self, chain_id) -> AttemptReport:
        pending = [a for a in self._spooled() if a.chain_id == chain_id and a.state in PUBLISHABLE]
        if pending:                                          # at most one unpublished result per chain (s4)
            att = pending[0]
            att.mark, att.contention0 = self.store.ops.mark(), self.store.contention_retries
            return self._finish(att, resumed=True)
        att = _Attempt(attempt_id=self._new_id(), chain_id=chain_id, started_unix=int(self.clock()))
        att.mark, att.contention0 = self.store.ops.mark(), self.store.contention_retries
        try:
            view, lease_commit, lease = self.store.snapshot(chain_id)
        except (RemoteUnavailable, Contention):
            return AttemptReport("", chain_id, 0, Outcome.REMOTE_UNAVAILABLE, frozenset({"no_attempt"}))
        att.timings["claim_read_s"] = round(time.monotonic() - att.t0, 6)
        self._hook("after_head_read")
        att.epoch_index, att.parent = view.head_index + 1, view.head_commit
        att.runtime = view.genesis_obj.get("runtime")
        if view.halted:
            return self._terminal(att, Outcome.HALTED)
        if view.complete:
            return AttemptReport("", chain_id, view.head_index, Outcome.COMPLETE)
        refusal = self._refusal(view.genesis_obj)
        if refusal:
            att.flags.add("refused:" + refusal)
            return self._terminal(att, Outcome.REFUSED_UNAPPROVED)
        if view.head_index >= 1 and not self._head_is_sound(view):
            return self._terminal(att, Outcome.HALTED)
        att.state = "STARTED"
        self._save(att)
        if self.leases and self.respect_leases and not self._acquire_lease(att, lease_commit, lease):
            self._drop(att)
            return AttemptReport(att.attempt_id, chain_id, att.epoch_index, Outcome.BUSY)
        att.timings["claim_s"] = round(time.monotonic() - att.t0, 6)
        self._hook("after_lease")
        att.state = "EXECUTING"
        self._save(att)
        t, cpu = time.monotonic(), time.process_time()
        result = model.execute(view.genesis_obj, att.epoch_index, self.store.checkpoint(view.head_commit),
                               runner=self.runner or R.lookup(view.genesis_obj["runtime"]))
        self.executions += 1
        att.timings["execute_s"] = round(time.monotonic() - t, 6)
        att.cpu_runner_s = round(time.process_time() - cpu, 6)
        self._hook("mid_execute")
        self._hook("after_execute")
        att.commit = self.store.epoch_commit(result, view.head_commit, att.attempt_id)
        att.work_id, att.epoch_digest, att.state = result.work_id, result.epoch_digest, "EXECUTED"
        self._save(att)
        return self._finish(att, resumed=False)

    def recover(self) -> list:
        """After a restart (or an outage): finish what the spool holds. Each attempt ends exactly once."""
        out = []
        for att in self._spooled():
            att.mark, att.contention0 = self.store.ops.mark(), self.store.contention_retries
            att.flags.add("recovered")
            if att.state in ("STARTED", "EXECUTING"):
                att.flags.add("crashed")
                out.append(self._terminal(att, Outcome.ABANDONED_RECOVERED))
            elif att.state == "TERMINAL":
                self._release_lease(att)                     # its receipt is already spooled
                self._drop(att)
            else:
                out.append(self._finish(att, resumed=True))
        return out

    def run_chain(self, chain_id, max_attempts=50) -> list:
        reports = []
        for _ in range(max_attempts):
            r = self.run_attempt(chain_id)
            reports.append(r)
            if r.outcome not in (Outcome.PUBLISHED, Outcome.DUPLICATE, Outcome.STALE, Outcome.ABANDONED_RECOVERED):
                break
        try:
            self.flush_receipts()
        except GitError:
            pass
        return reports

    def flush_receipts(self) -> int:
        d = os.path.join(self.spool_dir, "receipts")
        names = sorted(n for n in os.listdir(d) if n.endswith(".json"))
        if not names:
            return 0
        batch = {}
        for n in names:
            with open(os.path.join(d, n), "rb") as f:
                batch[n[:-5]] = json.loads(f.read().decode("utf-8"))
        self.store.append_receipts(self.worker_id, batch)
        for n in names:
            os.remove(os.path.join(d, n))
        return len(names)

    # -------------------------------------------------------------------------------------------- publication

    def _finish(self, att, resumed) -> AttemptReport:
        try:
            if att.state == "EXECUTED":
                t = time.monotonic()
                self.store.stage(att.attempt_id, att.commit)
                att.staged, att.state = True, "STAGED"
                att.timings["stage_s"] = round(time.monotonic() - t, 6)
                self._save(att)
                self._hook("after_stage")
            outcome = self._reread(att) if resumed else None
            t = time.monotonic()
            while outcome is None:
                if att.cas_pushes >= MAX_CAS:
                    raise Contention("CAS did not settle after {} pushes".format(att.cas_pushes))
                att.state = "CAS_SENT"
                att.cas_pushes += 1
                self._save(att)
                try:
                    res = self.store.cas_chain(att.chain_id, att.parent, att.commit, wrap=self._cas_wrap())
                except AmbiguousPush:
                    att.flags.add("ambiguous")
                    att.state = "AMBIGUOUS"
                    self._save(att)
                    outcome = self._reread(att)
                    continue
                self._hook("after_cas")
                outcome = Outcome.PUBLISHED if res.applied else self._classify(att)
            att.timings["cas_s"] = round(time.monotonic() - t, 6)
        except (RemoteUnavailable, Contention) as e:
            att.flags.add("contention" if isinstance(e, Contention) else "outage")
            if att.state == "CAS_SENT":
                att.state = "STAGED"                          # the push could not connect: it did not apply
            self._save(att)
            transitional = Outcome.AMBIGUOUS if att.state == "AMBIGUOUS" else Outcome.REMOTE_UNAVAILABLE
            return self._report(att, transitional)
        return self._terminal(att, outcome)

    def _reread(self, att):
        """Resolve by looking, never by pushing again: the attempt's outcome, or None when the head is still
        its parent (the CAS did not apply and may be sent)."""
        view = self.store.chain_view(att.chain_id)
        if view.head_commit == att.commit:
            return Outcome.PUBLISHED
        if self.store.commit_at(view.head_commit, att.epoch_index) == att.commit:
            return Outcome.PUBLISHED                         # applied, and something was built on it
        if view.halted:
            return Outcome.HALTED
        if view.head_commit == att.parent:
            return None
        return self._classify(att, view)

    def _classify(self, att, view=None):
        view = view or self.store.chain_view(att.chain_id)
        head = view.head_commit
        if head == att.commit or self.store.commit_at(head, att.epoch_index) == att.commit:
            return Outcome.PUBLISHED
        if self.store.commit_at(head, att.epoch_index - 1) != att.parent:
            return Outcome.STALE                             # the chain was rewound past this attempt's parent
        on = self.store.commit_at(head, att.epoch_index)
        if on is None:
            return None if head == att.parent else Outcome.STALE
        if view.head_index > att.epoch_index:
            att.flags.add("late")
        pub = self.store.published(on)
        if pub.work_id != att.work_id:
            return Outcome.STALE
        if pub.epoch_digest == att.epoch_digest:
            return Outcome.DUPLICATE
        qref = self.store.quarantine(att.chain_id, att.epoch_index, att.attempt_id, att.commit)
        late = view.head_index > att.epoch_index
        self.store.open_contest(att.chain_id, {
            "schema": "moonshot.epoch.contest.v1", "chain_id": att.chain_id,
            "state": "TAINTED" if late else "CONTESTED", "epoch_index": att.epoch_index,
            "taint_root": att.epoch_index, "work_id": att.work_id, "published_commit": on,
            "published_epoch_digest": pub.epoch_digest, "reason": "DISAGREEMENT",
            "challengers": [{"epoch_digest": att.epoch_digest, "quarantine_ref": qref, "by": self.worker_id,
                             "attempt_id": att.attempt_id}],
            "detected_by": self.worker_id, "head_index_at_detection": view.head_index})
        return Outcome.DISAGREEMENT

    # -------------------------------------------------------------------------------------------- checks

    def _approved_sha(self, sha) -> bool:
        if callable(self.approved) and not isinstance(self.approved, (set, frozenset, list, tuple)):
            return bool(self.approved(sha))
        return sha in self.approved

    def _refusal(self, genesis_obj):
        if not self._approved_sha(self.code_sha):
            return "worker-code-not-approved"
        if R.lookup(genesis_obj.get("runtime")) is None:
            return "runtime-not-registered"
        if not self._approved_sha(genesis_obj.get("approved_code_sha")):
            return "chain-code-not-approved"
        return None

    def _head_is_sound(self, view) -> bool:
        """Never build on bytes that do not verify: corrupt published bytes halt the chain (fail closed)."""
        head = view.head_commit
        if head in self._verified:
            return True
        parent = self.store.commit_at(head, view.head_index - 1)
        prev = view.genesis_obj["initial_checkpoint_sha256"] if view.head_index == 1 else \
            (self.store.manifest(parent) or {}).get("output_checkpoint_sha256")
        files = self.store.epoch_bytes(head)
        errs = model.verify_epoch(files, prev)
        if not errs and files["spec"] != canonical_bytes(model.derive_spec(view.genesis_obj, view.head_index)):
            errs.append("SPEC is not the derived spec")
        if not errs:
            self._verified.add(head)
            return True
        pub = self.store.published(head)
        self.store.open_contest(view.chain_id, {
            "schema": "moonshot.epoch.contest.v1", "chain_id": view.chain_id, "state": "CONTESTED",
            "epoch_index": view.head_index, "taint_root": view.head_index, "work_id": pub.work_id,
            "published_commit": head, "published_epoch_digest": pub.epoch_digest, "reason": "CORRUPT_BYTES",
            "errors": errs, "challengers": [], "detected_by": self.worker_id,
            "head_index_at_detection": view.head_index})
        return False

    # -------------------------------------------------------------------------------------------- leases

    def _acquire_lease(self, att, lease_commit, lease) -> bool:
        now = int(self.clock())
        held_by_other = bool(lease) and lease.get("state") == "HELD" and lease.get("holder") != self.worker_id \
            and lease.get("epoch_index") == att.epoch_index
        if held_by_other and now < lease.get("expires_unix", 0):
            return False
        new = {"schema": "moonshot.epoch.lease.v1", "chain_id": att.chain_id, "epoch_index": att.epoch_index,
               "holder": self.worker_id, "attempt_id": att.attempt_id, "acquired_unix": now,
               "expires_unix": now + int(self.lease_ttl_s), "state": "HELD"}
        c = self.store.write_lease(att.chain_id, lease_commit, new)
        if not c:
            return False
        att.lease_commit, att.lease = c, new
        if held_by_other:
            att.flags.add("lease_stolen")
        self._save(att)
        return True

    def _release_lease(self, att):
        if not att.lease_commit:
            return
        tomb = dict(att.lease, state="RELEASED", released_unix=int(self.clock()))
        try:
            if not self.store.write_lease(att.chain_id, att.lease_commit, tomb):
                att.flags.add("lease_lost")
        except GitError:
            att.flags.add("lease_lost")

    # -------------------------------------------------------------------------------------------- endings

    def _terminal(self, att, outcome) -> AttemptReport:
        att.outcome = outcome.value
        receipt = self._receipt(att, outcome)
        self._write_durable(self._path("receipts", att.attempt_id),
                            json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        att.state = "TERMINAL"
        if os.path.exists(self._path("attempts", att.attempt_id)):
            self._save(att)
        self._hook("after_receipt_spool")
        if att.staged:
            self.store.unstage(att.attempt_id, att.commit)
        self._hook("before_lease_release")
        self._release_lease(att)
        self._drop(att)
        return self._report(att, outcome, receipt)

    def _report(self, att, outcome, receipt=None) -> AttemptReport:
        return AttemptReport(att.attempt_id, att.chain_id, att.epoch_index, outcome, frozenset(att.flags),
                             att.work_id, att.epoch_digest, att.commit, receipt or {})

    def _receipt(self, att, outcome) -> dict:
        ops = self.store.ops.since(att.mark)
        cpu = [o.cpu_s for o in ops if o.cpu_s is not None]
        return {
            "schema": "moonshot.epoch.receipt.v1", "attempt_id": att.attempt_id, "worker_id": self.worker_id,
            "host": self.host_label or platform.node(), "platform": platform.platform(),
            "python": platform.python_version(), "code_sha": self.code_sha, "chain_id": att.chain_id,
            "epoch_index": att.epoch_index, "work_id": att.work_id, "epoch_digest": att.epoch_digest,
            "outcome": outcome.value, "flags": sorted(att.flags), "layout": self.store.layout,
            "namespace": self.store.namespace, "runtime": att.runtime, "started_unix": att.started_unix,
            "ended_unix": int(self.clock()), "timings": dict(att.timings, total_s=round(time.monotonic() - att.t0, 6)),
            "git_ops": len(ops), "push_attempts": sum(1 for o in ops if o.kind == "push"),
            "push_attempts_cas": att.cas_pushes,
            "contention_retries": self.store.contention_retries - att.contention0,
            "bytes_pushed": sum(o.bytes_sent for o in ops), "bytes_fetched": sum(o.bytes_received for o in ops),
            "coordination_wall_s": round(sum(o.wall_s for o in ops), 6), "cpu_runner_s": att.cpu_runner_s,
            "cpu_children_s": round(sum(cpu), 6) if cpu else None, "lease": att.lease,
        }

    def _new_id(self) -> str:
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(self.clock()))
        return "A-{}-{}-{}".format(ts, self.worker_id, uuid.uuid4().hex[:8])
