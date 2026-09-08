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
    no randomness -- BIT_DETERMINISTIC by construction.

    ASSUMES len(bits) == len(target); the CALLER enforces it. This function
    divides by len(target), so a short candidate would score against the full
    target and be capped at len(bits)/len(target) -- a silently lowered ceiling
    with `solved` unreachable (WP-0a / Herakles F-1). The guard lives in
    BitStringExecutor.execute rather than here, on the established refusal
    path, because the honest answer to a mismatched candidate is that the
    result does not exist -- not a number with a caveat attached."""
    n = min(len(bits), len(target))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if bits[i] == target[i]) / len(target)


class BitStringExecutor(Executor):
    """Evaluates a candidate bitstring against a fixed hidden target.

    The target is derived deterministically from the seed the CALLER supplies
    as `WorkPackage.seed_root`, and from `length`. Two runs share a landscape
    iff they pass the same seed and the same length.

    THAT SEED IS NOT NECESSARILY THE WORLD'S (corrected 2026-09-08, WP-0a). An
    earlier version of this docstring claimed the target came from "the world's
    seed, so every world shares the SAME landscape iff it shares the seed".
    Vivarium deliberately passes the REPEAT's derived seed instead, and says so
    in its own comment; under a `seed_derivation` of `sha256_index` or
    `linear_index`, repeats of ONE world therefore get DIFFERENT landscapes.
    Both sides are internally consistent -- it was the shared claim between
    them that was stale, and designing against the old wording would give you
    the wrong invariant."""
    kind = "evaluate_bitstring"

    def __init__(self, length: int = 24):
        self.length = length

    def target_for(self, seed_root: int) -> str:
        h = hashlib.sha256(f"target:{seed_root}:{self.length}".encode()).digest()
        bitseq = "".join(f"{b:08b}" for b in h)
        return bitseq[:self.length]

    def execute(self, wp: WorkPackage) -> ExecutorResult:
        bits = str(wp.payload.get("bits", ""))
        # WP-0a (Herakles F-1). A candidate whose length differs from the
        # declared `length` used to be SCORED: _deterministic_score matches
        # over the overlap and divides by the target length, so a short
        # candidate came back COMPLETED with a plausible number whose ceiling
        # was silently len(bits)/length and whose `solved` could never fire.
        # An outcome rule keyed on solved cannot trigger, and the observation
        # reads as weak performance rather than as a broken spec.
        #
        # It is refused here, beside the alphabet check and on the same path,
        # because a length mismatch is not a worse candidate -- it is not a
        # candidate for THIS landscape at all. Returning the mismatch as a
        # result field would be worse: it keeps the bad observation in the
        # record and relies on every downstream reader to notice.
        if not bits or any(ch not in "01" for ch in bits) \
                or len(bits) != self.length:
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
        # H1: the server-issued fencing token for THIS attempt; required on
        # every subsequent call so a stale attempt can never act.
        claim_id = claim["claim_id"]
        w = self.f.get_world(wid)
        ex = self.executors.get(claim["kind"])
        if ex is None:
            self.f.fail_work(work_id, self.worker_id,
                             f"no executor for kind {claim['kind']!r}",
                             retry=False, claim_id=claim_id)
            return True
        self.f.start_work(work_id, self.worker_id, claim_id=claim_id)
        wp = WorkPackage(work_id=work_id, world_id=wid, kind=claim["kind"],
                         payload=claim["payload"], seed_root=w["seed_root"])
        try:
            r = ex.execute(wp)
        except Exception as e:                       # noqa: BLE001
            self.f.fail_work(work_id, self.worker_id, f"executor raised: {e}",
                             claim_id=claim_id)
            return True
        if r.status == "COMPLETED":
            self.f.complete_work(work_id, self.worker_id,
                                 {**r.result,
                                  "reproducibility": r.reproducibility},
                                 claim_id=claim_id)
        else:
            self.f.fail_work(work_id, self.worker_id, r.error or "failed",
                             claim_id=claim_id)
        return True

    def run_until_idle(self, world_id: Optional[str] = None,
                       max_iterations: int = 100000) -> int:
        n = 0
        while n < max_iterations and self.run_once(world_id):
            n += 1
        return n
