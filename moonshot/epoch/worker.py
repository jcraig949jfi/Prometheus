"""The attempt state machine (CONTRACT s4, s5, s9, s11)."""
from dataclasses import dataclass, field
from enum import Enum

from .gitio import AmbiguousPush  # noqa: F401  (re-exported for fault callbacks)


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


class InjectedCrash(Exception):
    """A simulated process death at a fault point: no cleanup runs."""


class FaultPlan:
    def __init__(self, faults=None):
        self.faults = dict(faults or {})


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


class Worker:
    def __init__(self, store, worker_id, *, code_sha, approved, spool_dir, clock=None, leases=True,
                 respect_leases=True, lease_ttl_s=60, runner=None, faults=None, host_label=None):
        self.store = store
        self.worker_id = worker_id
        self.code_sha = code_sha
        self.approved = approved
        self.spool_dir = spool_dir
        self.clock = clock
        self.leases = leases
        self.respect_leases = respect_leases
        self.lease_ttl_s = lease_ttl_s
        self.runner = runner
        self.faults = faults or FaultPlan()
        self.host_label = host_label
        self.executions = 0

    def run_attempt(self, chain_id) -> AttemptReport:
        raise NotImplementedError("C-008-T001")

    def recover(self) -> list:
        raise NotImplementedError("C-008-T001")

    def flush_receipts(self) -> int:
        raise NotImplementedError("C-008-T001")

    def run_chain(self, chain_id, max_attempts=50) -> list:
        raise NotImplementedError("C-008-T001")
