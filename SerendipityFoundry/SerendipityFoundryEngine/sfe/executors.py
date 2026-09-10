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


# --- NK landscapes (design packet v2.1, part 1) -----------------------------

#: Table entries are integers in [0, NK_SCALE). Integer accumulation is the
#: point: score is one division at the very end, so "exactly equal" is a
#: question about integers and the permutation guarantee (G1) is exact rather
#: than exact-to-within-a-float.
NK_SCALE = 1 << 20

#: v0 admits 8..20 only. The ceiling is not arbitrary: at length <= 20 the
#: optimum can be CERTIFIED by enumeration, so `solved_status` is a fact. Above
#: it, a success claim would need a separate exact solver's certificate, and
#: the packet declines to admit that in v0 rather than emit "unknown" forever.
NK_MIN_LENGTH, NK_MAX_LENGTH = 8, 20

#: Landscapes are pure functions of (seed_root, length, k), and certifying an
#: optimum at k>0 costs 2**length evaluations. Worth keeping.
_NK_CACHE: dict = {}


def _nk_stream(*parts) -> int:
    """One deterministic integer from a domain-separated label."""
    label = ":".join(str(p) for p in parts)
    return int.from_bytes(hashlib.sha256(label.encode()).digest(), "big")


class NKLandscape:
    """An NK landscape: neighbours per locus, and a table lookup per locus.

    THE TABLES ARE NEVER MATERIALIZED. An entry is a pure function of
    (seed_root, length, k, locus, pattern), so it is hashed on demand and
    memoized. That is not only an optimisation: at the contract's own limits
    (k = length-1 = 19) a materialized table would be 20 x 2**20 integers for
    a landscape most of whose entries are never read.
    """

    def __init__(self, seed_root: int, length: int, k: int):
        self.seed_root, self.length, self.k = seed_root, length, k
        self.neighbours = tuple(self._neighbours(i) for i in range(length))
        self._entries: dict = {}
        self._optimum_int = None

    def _neighbours(self, i: int) -> tuple:
        """Locus i depends on ITSELF and k others drawn uniformly without
        replacement from the other loci.

        Partial Fisher-Yates over the other loci, driven by one hash stream, so
        the draw is uniform and reproducible without a PRNG whose internals
        could change under us. The result is `(i,) + sorted(others)`: the
        neighbour ORDER fixes the table index, so it must be a function of the
        SET and never of the draw order, or two runs that chose the same
        neighbours in a different sequence would index different entries.
        """
        others = [j for j in range(self.length) if j != i]
        stream = _nk_stream("nk:neigh", self.seed_root, self.length, self.k, i)
        for t in range(self.k):
            m = len(others) - t
            stream, r = divmod(stream, m)
            others[t], others[t + r] = others[t + r], others[t]
        return (i,) + tuple(sorted(others[:self.k]))

    def entry(self, locus: int, pattern: int) -> int:
        key = (locus, pattern)
        v = self._entries.get(key)
        if v is None:
            v = _nk_stream("nk:table", self.seed_root, self.length, self.k,
                           locus, pattern) % NK_SCALE
            self._entries[key] = v
        return v

    def _pattern(self, values, locus: int) -> int:
        """Big-endian over this locus's neighbour list, own locus first."""
        p = 0
        for j in self.neighbours[locus]:
            p = (p << 1) | values[j]
        return p

    def contributions(self, values) -> list:
        return [self.entry(i, self._pattern(values, i))
                for i in range(self.length)]

    def optimum_int(self) -> int:
        """The certified optimum, as an integer sum.

        k == 0: each locus is independent, so the optimum is the sum of each
        locus's better entry -- computed DIRECTLY, never enumerated. The
        packet is explicit that k=0 is additive with random per-locus weights
        and NOT onemax.

        k > 0: exhaustive enumeration over 2**length. Certified, not estimated.
        A Gray-code walk would flip one bit at a time, but only the loci whose
        neighbourhood contains that bit change, so the saving is real; it is
        not taken here because the straightforward loop is obviously correct
        and 2**16 is the first corpus.
        """
        if self._optimum_int is not None:
            return self._optimum_int
        if self.k == 0:
            self._optimum_int = sum(max(self.entry(i, 0), self.entry(i, 1))
                                    for i in range(self.length))
            return self._optimum_int
        best = -1
        n = self.length
        for cand in range(1 << n):
            values = [(cand >> (n - 1 - b)) & 1 for b in range(n)]
            s = 0
            for i in range(n):
                s += self.entry(i, self._pattern(values, i))
            if s > best:
                best = s
        self._optimum_int = best
        return best


def nk_landscape(seed_root: int, length: int, k: int) -> NKLandscape:
    key = (int(seed_root), int(length), int(k))
    L = _NK_CACHE.get(key)
    if L is None:
        L = NKLandscape(*key)
        _NK_CACHE[key] = L
    return L


class NKLandscapeExecutor(Executor):
    """`nk_landscape_v0` -- design packet v2.1 part 1, sections 1.1 to 1.8.

    WHAT THIS IS FOR. Search under interacting contributions: a method-
    evaluation instrument. It scores ONE candidate; the search that produces
    candidates is the caller's, and deliberately so -- an executor that
    searched would be measuring itself.

    THE PERMUTATION IS THE POINT, not a convenience. `permutation` is a locus
    relabelling applied JOINTLY to the neighbour lists, the table indexing, the
    candidate and the contribution vector, which is how the exchangeability
    null (G1) EXECUTES instead of being asserted. The convention is pinned
    here because the packet does not pin it and two readings would silently
    disagree:

        permutation[i] = p  means locus i's value is read from bits[p],
                             and locus i's contribution is REPORTED at
                             position p of the contribution vector.

    Under that reading, for any P: contrib_int comes back P-permuted exactly
    and the integer sum is identical -- which is the guarantee, and is tested
    both ways round (a candidate-only permutation on an asymmetric landscape
    must CHANGE the result, or the test proves nothing).

    NO DEFAULTS. Every payload key is required, `permutation: null` included --
    a null that was DECLARED is inside spec_hash and is a different experiment
    from one where the key was absent. The engine refuses rather than choosing,
    for the same reason `length` became required on evaluate_bitstring.
    """
    kind = "nk_landscape_v0"

    #: Exact key set. Extra keys are refused, not ignored: an unread key inside
    #: a hashed spec is a parameter someone believes is in force.
    PARAMS = frozenset({"bits", "length", "k", "permutation"})

    def execute(self, wp: WorkPackage) -> ExecutorResult:
        p = wp.payload if isinstance(wp.payload, dict) else {}
        bad = self._refuse(p)
        if bad:
            return ExecutorResult(status="FAILED", error=bad,
                                  reproducibility="BIT_DETERMINISTIC")

        length, k = int(p["length"]), int(p["k"])
        bits, perm = str(p["bits"]), p["permutation"]
        L = nk_landscape(wp.seed_root, length, k)

        # Read each locus's value through the relabelling, and report each
        # locus's contribution back through it.
        if perm is None:
            values = [int(c) for c in bits]
            contrib_int = L.contributions(values)
        else:
            perm = [int(x) for x in perm]
            values = [int(bits[perm[i]]) for i in range(length)]
            raw = L.contributions(values)
            contrib_int = [0] * length
            for i in range(length):
                contrib_int[perm[i]] = raw[i]

        total = sum(contrib_int)
        # ONE division, at the very end. Dividing per locus and summing would
        # reintroduce the float error the integer tables exist to avoid.
        score = total / (length * NK_SCALE)
        optimum_int = L.optimum_int()

        return ExecutorResult(
            status="COMPLETED",
            result={
                "score": score,
                "contribution": [c / NK_SCALE for c in contrib_int],
                "contrib_int": contrib_int,
                # length <= 20 is the admitted range precisely so this is
                # always "certified" and solved_status is never a shrug.
                "optimum_status": "certified",
                "optimum_score": optimum_int / (length * NK_SCALE),
                # INTEGER equality. Comparing the divided scores would make
                # "solved" depend on float rounding at the last step.
                "solved_status": "solved" if total == optimum_int
                                 else "unsolved",
                "executor": self.kind,
                "reproducibility": "BIT_DETERMINISTIC",
            },
            reproducibility="BIT_DETERMINISTIC")

    def _refuse(self, p: dict):
        """Every rejection the contract implies, before anything is scored.

        A refusal is the honest answer to a payload that does not describe a
        candidate for THIS landscape; scoring it anyway would put a plausible
        number with no meaning into the record, which is the WP-0a lesson.
        """
        missing = sorted(self.PARAMS - set(p))
        extra = sorted(set(p) - self.PARAMS)
        if missing:
            return "missing payload key(s) %s; there are no defaults" % missing
        if extra:
            return ("unknown payload key(s) %s; the parameter set is exact"
                    % extra)
        length = p["length"]
        if isinstance(length, bool) or not isinstance(length, int) \
                or not NK_MIN_LENGTH <= length <= NK_MAX_LENGTH:
            return ("length must be an integer in %d..%d (v0 admits only "
                    "lengths whose optimum can be certified), got %r"
                    % (NK_MIN_LENGTH, NK_MAX_LENGTH, length))
        k = p["k"]
        if isinstance(k, bool) or not isinstance(k, int) \
                or not 0 <= k <= length - 1:
            return "k must be an integer in 0..length-1, got %r" % (k,)
        bits = p["bits"]
        if not isinstance(bits, str) or len(bits) != length \
                or any(c not in "01" for c in bits):
            return ("bits must be a binary string of exactly length %d; a "
                    "candidate of another width is not a candidate for this "
                    "landscape" % length)
        perm = p["permutation"]
        if perm is not None:
            if not isinstance(perm, (list, tuple)) or len(perm) != length:
                return ("permutation must be null or a list of exactly "
                        "%d loci" % length)
            if any(isinstance(x, bool) or not isinstance(x, int)
                   for x in perm) or sorted(perm) != list(range(length)):
                return ("permutation must be a bijection of 0..%d; a mapping "
                        "that drops or repeats a locus is not a relabelling"
                        % (length - 1))
        return None


class NKScanDidNotConverge(RuntimeError):
    """The coordinate scan failed to reach a fixed point inside its bound.

    Under the SPECIFIED rule -- keep a flip only on a STRICT increase -- this
    cannot happen: every accepted flip raises a bounded integer, so the scan
    terminates. It is raised rather than looped precisely because the rule that
    would break it (accepting ties) breaks it by NOT TERMINATING, and a check
    that hangs is not a check that fails.
    """


def nk_coordinate_scan(seed_root: int, length: int, k: int, start: str,
                       max_scans: int = 1024):
    """The climber the packet SPECIFIES (1.8), so the kill precondition is
    executable rather than described.

    Deterministic coordinate scan: from `start`, for i = 0..N-1 in fixed order
    flip locus i and keep the flip iff the score strictly increases (a tie
    keeps the original); repeat scans until a full scan changes nothing.
    Query cost is 1 + N per scan. Interface: score_only -- the scan never sees
    the contribution vector, which is what makes it a fair instrument for a
    score_only template.

    Returns (bits, total_int, scans, queries). Integer totals throughout: at
    k=0 reaching the optimum in exactly one scan is a GUARANTEE (G2), and a
    guarantee tested through floats is tested approximately.
    """
    L = nk_landscape(seed_root, length, k)
    cur = [int(c) for c in start]
    total = sum(L.contributions(cur))
    queries, scans = 1, 0
    while scans < max_scans:
        scans += 1
        changed = False
        for i in range(length):
            cur[i] ^= 1
            cand = sum(L.contributions(cur))
            queries += 1
            if cand > total:
                total = cand
                changed = True
            else:
                cur[i] ^= 1                     # strict increase, ties keep
        if not changed:
            return "".join(str(b) for b in cur), total, scans, queries
    raise NKScanDidNotConverge(
        "no fixed point after %d scans; under the specified strict-increase "
        "rule every accepted flip raises a bounded integer, so this means the "
        "acceptance rule is not the specified one" % max_scans)


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
