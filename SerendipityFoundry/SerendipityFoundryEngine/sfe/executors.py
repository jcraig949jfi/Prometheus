"""Executor adapter contract (section 16) and reference executors.

The Foundry does not care WHO executes work -- Python, an LLM, a solver, a shell
command. An executor receives a well-defined WorkPackage and returns a structured
ExecutorResult; nothing executor-specific leaks into the runtime core. Section 26
boundary: executors EXECUTE and MEASURE; they do not hypothesize or choose
experiments (that is the driver/agent's job) and they do not define the
authoritative history (that is the Foundry's).

Reproducibility is declared HONESTLY per result (section 17): a seed existing is
NOT determinism. An executor that touches wall-clock, external services, or
os.urandom must report NONDETERMINISTIC / PARTIAL, never BIT_DETERMINISTIC.
"""

from __future__ import annotations

import abc
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Optional

REPRO = ("BIT_DETERMINISTIC", "SEMANTIC", "PARTIAL", "NONDETERMINISTIC")


@dataclass(frozen=True)
class WorkPackage:
    work_id: str
    world_id: str
    kind: str
    payload: dict
    seed_root: int


@dataclass
class ExecutorResult:
    status: str                       # COMPLETED | FAILED
    result: dict = field(default_factory=dict)
    artifacts: list = field(default_factory=list)   # list[bytes]
    reproducibility: str = "UNKNOWN"
    error: Optional[str] = None


class Executor(abc.ABC):
    kind: str = "abstract"

    @abc.abstractmethod
    def execute(self, wp: WorkPackage) -> ExecutorResult: ...


# --- reference deterministic executor for the canary ------------------------

def _deterministic_score(bits: str, target: str) -> float:
    """A bounded, fully deterministic scoring problem: fraction of positions
    matching a fixed hidden target (a 'onemax'-style landscape). No wall-clock,
    no randomness -- BIT_DETERMINISTIC by construction."""
    n = min(len(bits), len(target))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if bits[i] == target[i]) / len(target)


class BitStringExecutor(Executor):
    """Evaluates a candidate bitstring against a fixed hidden target. The target
    is derived deterministically from the world's seed so every world shares the
    SAME landscape iff it shares the seed -- the canary's identical-initial-
    conditions requirement."""
    kind = "evaluate_bitstring"

    def __init__(self, length: int = 24):
        self.length = length

    def target_for(self, seed_root: int) -> str:
        h = hashlib.sha256(f"target:{seed_root}:{self.length}".encode()).digest()
        bitseq = "".join(f"{b:08b}" for b in h)
        return bitseq[:self.length]

    def execute(self, wp: WorkPackage) -> ExecutorResult:
        bits = str(wp.payload.get("bits", ""))
        if not bits or any(ch not in "01" for ch in bits):
            return ExecutorResult(status="FAILED", error="invalid candidate",
                                  reproducibility="BIT_DETERMINISTIC")
        target = self.target_for(wp.seed_root)
        score = _deterministic_score(bits, target)
        return ExecutorResult(
            status="COMPLETED",
            result={"bits": bits, "score": score, "solved": score >= 1.0,
                    "length": self.length},
            reproducibility="BIT_DETERMINISTIC")


class NondeterministicExecutor(Executor):
    """Deliberately nondeterministic (uses os.urandom). Exists so tests can
    prove the Foundry does NOT falsely claim deterministic reproduction (T17)."""
    kind = "nondeterministic"

    def execute(self, wp: WorkPackage) -> ExecutorResult:
        import os
        val = int.from_bytes(os.urandom(4), "big")
        return ExecutorResult(status="COMPLETED", result={"noise": val},
                              reproducibility="NONDETERMINISTIC")


# --- worker loop (claim -> heartbeat -> execute -> commit) ------------------

class WorkerLoop:
    """A worker: claims work atomically, executes it via a registered executor,
    heartbeats its lease, and commits the result idempotently. Interchangeable
    and disposable (I1/I3) -- killing it mid-lease leaves the work reclaimable."""

    def __init__(self, foundry, worker_id: str, executors: dict,
                 lease_s: float = 30.0):
        self.f = foundry
        self.worker_id = worker_id
        self.executors = {e.kind: e for e in executors} if isinstance(
            executors, (list, tuple)) else executors
        self.lease_s = lease_s

    def run_once(self, world_id: Optional[str] = None) -> bool:
        claim = self.f.claim_work(self.worker_id, world_id=world_id,
                                  lease_s=self.lease_s)
        if claim is None:
            return False
        wid, work_id = claim["world_id"], claim["work_id"]
        w = self.f.get_world(wid)
        ex = self.executors.get(claim["kind"])
        if ex is None:
            self.f.fail_work(work_id, self.worker_id,
                             f"no executor for kind {claim['kind']!r}",
                             retry=False)
            return True
        self.f.start_work(work_id, self.worker_id)
        wp = WorkPackage(work_id=work_id, world_id=wid, kind=claim["kind"],
                         payload=claim["payload"], seed_root=w["seed_root"])
        try:
            r = ex.execute(wp)
        except Exception as e:                       # noqa: BLE001
            self.f.fail_work(work_id, self.worker_id, f"executor raised: {e}")
            return True
        if r.status == "COMPLETED":
            self.f.complete_work(work_id, self.worker_id,
                                 {**r.result,
                                  "reproducibility": r.reproducibility})
        else:
            self.f.fail_work(work_id, self.worker_id, r.error or "failed")
        return True

    def run_until_idle(self, world_id: Optional[str] = None,
                       max_iterations: int = 100000) -> int:
        n = 0
        while n < max_iterations and self.run_once(world_id):
            n += 1
        return n
