"""H3 alpha: offline replay of ONE candidate stream through four retention
policies (design v0.1 §5 H3; Track D).

The stream is fixed and policy-independent. Every policy consumes the same
ordered stream under the same caps (items AND bytes); retention never sees
future-query labels; the archives are frozen (digested) before a separately
sealed future-query manifest is replayed. Descriptors, bins, tie order and
capacities are declared up front. Nothing here generates candidates.

Policies
  top_k       keep the best source-objective candidates (ties: earlier wins)
  uniform     reservoir sample of the stream (seeded; Vitter's R by hand)
  behavioral  fixed-descriptor grid archive; one cell one item; a later
              candidate replaces the incumbent only if STRICTLY better on the
              source objective (first-writer-wins on exact ties -- Techne's
              measured pyribs fact, declared here as the policy)
  hybrid      behavioral with `reserve` slots given to a uniform reservoir;
              both halves count against the SAME item and byte caps

Every insertion, eviction and the final retained set are recorded and
digested so a replay can be checked byte for byte. Costs are producer-side
receipts (archaeon.producer.costs).

The stream record (C2 "candidate stream"): stable ordered id, candidate
digest, birth status (evaluated | failed), fixed assay reference, score
(None if failed), descriptor vector, byte size, and a replayable reference.
A queue index alone is not a stream: `stream_manifest()` proves completeness
by hashing every record in order and counting the failed ones explicitly.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from . import costs as C


@dataclass(frozen=True)
class Candidate:
    stream_id: int                     # position in the stream, stable
    candidate_digest: str
    birth_status: str                  # "evaluated" | "failed"
    assay_ref: str
    score: Optional[float]             # None iff failed
    descriptors: Tuple[float, ...]
    byte_size: int
    replay_ref: str

    def __post_init__(self):
        if self.birth_status not in ("evaluated", "failed"):
            raise ValueError("birth_status")
        if (self.score is None) != (self.birth_status == "failed"):
            raise ValueError("a failed candidate has no score; an evaluated one has one")


def stream_manifest(stream: Sequence[Candidate]) -> Dict[str, Any]:
    """Completeness proof: ordered ids contiguous, every record hashed, failed
    ones counted rather than dropped."""
    ids = [c.stream_id for c in stream]
    if ids != list(range(len(stream))):
        raise ValueError("stream ids must be contiguous from 0; a gap is a missing candidate")
    h = hashlib.sha256()
    for c in stream:
        h.update(json.dumps(asdict(c), sort_keys=True).encode())
    return {"schema": "archaeon.h3.stream.v0", "n": len(stream),
            "n_failed": sum(1 for c in stream if c.birth_status == "failed"),
            "stream_digest": "sha256:" + h.hexdigest(),
            "descriptor_dims": len(stream[0].descriptors) if stream else 0}


# --------------------------------------------------------------------------
# Archive with caps and a full event log
# --------------------------------------------------------------------------
@dataclass
class Archive:
    policy_id: str
    cap_items: int
    cap_bytes: int
    items: Dict[str, Candidate] = field(default_factory=dict)      # key -> candidate
    events: List[Dict[str, Any]] = field(default_factory=list)
    bytes_used: int = 0

    def _log(self, kind: str, c: Candidate, **kw):
        self.events.append({"event": kind, "stream_id": c.stream_id,
                            "candidate_digest": c.candidate_digest, **kw})

    def try_insert(self, key: str, c: Candidate, better_than: Callable[[Candidate, Candidate], bool],
                   evict_choice: Callable[["Archive"], Optional[str]]) -> None:
        if c.byte_size > self.cap_bytes:
            self._log("refused_oversize", c); return
        if key in self.items:
            inc = self.items[key]
            if better_than(c, inc):
                self._replace(key, c, reason="strictly_better"); return
            self._log("rejected_incumbent_wins", c, key=key)   # first-writer-wins on ties
            return
        # room?
        while (len(self.items) >= self.cap_items) or (self.bytes_used + c.byte_size > self.cap_bytes):
            victim = evict_choice(self)
            if victim is None:
                self._log("refused_full", c); return
            self._evict(victim, reason="cap")
        self.items[key] = c; self.bytes_used += c.byte_size
        self._log("inserted", c, key=key)

    def _replace(self, key: str, c: Candidate, reason: str):
        old = self.items[key]
        self.bytes_used += c.byte_size - old.byte_size
        if self.bytes_used > self.cap_bytes:
            self.bytes_used -= c.byte_size - old.byte_size
            self._log("refused_bytes_on_replace", c, key=key); return
        self.items[key] = c
        self._log("replaced", c, key=key, evicted=old.candidate_digest, reason=reason)

    def _evict(self, key: str, reason: str):
        old = self.items.pop(key); self.bytes_used -= old.byte_size
        self.events.append({"event": "evicted", "stream_id": old.stream_id,
                            "candidate_digest": old.candidate_digest, "key": key, "reason": reason})

    def retained(self) -> List[Candidate]:
        return sorted(self.items.values(), key=lambda c: c.stream_id)

    def digest(self) -> str:
        blob = json.dumps([asdict(c) for c in self.retained()], sort_keys=True).encode()
        return "sha256:" + hashlib.sha256(blob).hexdigest()


# --------------------------------------------------------------------------
# Policies. Each is replay(stream) -> Archive, deterministic given the seed.
# --------------------------------------------------------------------------
def _score(c: Candidate) -> float:
    return -1.0 if c.score is None else c.score


def top_k(stream: Sequence[Candidate], cap_items: int, cap_bytes: int, **_) -> Archive:
    a = Archive("h3.top_k.v0", cap_items, cap_bytes)
    for c in stream:
        if c.birth_status == "failed":
            a._log("skipped_failed", c); continue
        def evict(arch: Archive) -> Optional[str]:
            worst = min(arch.items.items(), key=lambda kv: (_score(kv[1]), -kv[1].stream_id))
            return worst[0] if _score(worst[1]) < c.score else None
        a.try_insert(c.candidate_digest, c, better_than=lambda n, o: False, evict_choice=evict)
    return a


def uniform(stream: Sequence[Candidate], cap_items: int, cap_bytes: int, seed: int = 0, **_) -> Archive:
    """Reservoir sampling (Algorithm R) over the EVALUATED candidates."""
    a = Archive("h3.uniform.v0#{}".format(seed), cap_items, cap_bytes)
    rng = random.Random(seed)
    seen = 0
    slots: List[str] = []
    for c in stream:
        if c.birth_status == "failed":
            a._log("skipped_failed", c); continue
        seen += 1
        if len(a.items) < cap_items and a.bytes_used + c.byte_size <= cap_bytes:
            a.try_insert(c.candidate_digest, c, better_than=lambda n, o: False, evict_choice=lambda arch: None)
            slots.append(c.candidate_digest)
        else:
            j = rng.randrange(seen)
            if j < cap_items and j < len(slots):
                victim = slots[j]
                if victim in a.items:
                    a._evict(victim, reason="reservoir_replace")
                slots[j] = c.candidate_digest
                a.try_insert(c.candidate_digest, c, better_than=lambda n, o: False, evict_choice=lambda arch: None)
            else:
                a._log("reservoir_skip", c)
    return a


def _cell(c: Candidate, edges: Sequence[Sequence[float]]) -> str:
    idx = []
    for d, es in zip(c.descriptors, edges):
        k = sum(1 for e in es if d >= e)
        idx.append(str(k))
    return "cell:" + ",".join(idx)


def behavioral(stream: Sequence[Candidate], cap_items: int, cap_bytes: int,
               edges: Sequence[Sequence[float]] = (), **_) -> Archive:
    """One item per descriptor cell; a later candidate replaces the incumbent
    only if STRICTLY better (first-writer-wins on exact ties, declared)."""
    a = Archive("h3.behavioral.v0", cap_items, cap_bytes)
    for c in stream:
        if c.birth_status == "failed":
            a._log("skipped_failed", c); continue
        key = _cell(c, edges)
        a.try_insert(key, c, better_than=lambda n, o: _score(n) > _score(o),
                     evict_choice=lambda arch: None)          # full grid: refuse, never evict another cell
    return a


def hybrid(stream: Sequence[Candidate], cap_items: int, cap_bytes: int,
           edges: Sequence[Sequence[float]] = (), reserve: int = 0, seed: int = 0, **_) -> Archive:
    """Behavioral archive on cap_items - reserve slots plus a uniform reservoir
    on `reserve` slots, BOTH counted against the same item and byte caps."""
    if not (0 <= reserve < cap_items):
        raise ValueError("reserve must be in [0, cap_items)")
    b = behavioral(stream, cap_items - reserve, cap_bytes, edges=edges)
    remaining_bytes = cap_bytes - b.bytes_used
    u = uniform(stream, reserve, max(remaining_bytes, 0), seed=seed)
    a = Archive("h3.hybrid.v0#{}".format(seed), cap_items, cap_bytes)
    for key, c in b.items.items():
        a.items["B|" + key] = c; a.bytes_used += c.byte_size
    for key, c in u.items.items():
        if c.candidate_digest in {x.candidate_digest for x in b.items.values()}:
            a.events.append({"event": "duplicate_not_double_counted", "candidate_digest": c.candidate_digest})
            continue
        a.items["U|" + key] = c; a.bytes_used += c.byte_size
    a.events = b.events + u.events + a.events
    assert len(a.items) <= cap_items and a.bytes_used <= cap_bytes
    return a


POLICIES = {"top_k": top_k, "uniform": uniform, "behavioral": behavioral, "hybrid": hybrid}


# --------------------------------------------------------------------------
# The experiment: replay -> freeze -> sealed future queries -> score
# --------------------------------------------------------------------------
def replay_all(stream: Sequence[Candidate], caps: Dict[str, int], edges, reserve: int, seed: int,
               attempt_id: str) -> Dict[str, Any]:
    manifest = stream_manifest(stream)
    out: Dict[str, Any] = {"stream": manifest, "caps": dict(caps), "policies": {}, "cost_events": []}
    for name, fn in POLICIES.items():
        with C.Meter() as m:
            arch = fn(stream, caps["items"], caps["bytes"], edges=edges, reserve=reserve, seed=seed)
        ev = C.CostEvent("retention", attempt_id, m.resources(
            [C.Resource("items", len(arch.items), "count", "retained", "measured"),
             C.Resource("retained_bytes", arch.bytes_used, "bytes", "sum of byte_size", "measured")]),
            source_refs=[manifest["stream_digest"]])
        out["policies"][name] = {"policy_id": arch.policy_id, "retained_n": len(arch.items),
                                 "bytes": arch.bytes_used, "archive_digest": arch.digest(),
                                 "events": len(arch.events),
                                 "event_counts": _counts(arch.events),
                                 "retained_ids": [c.stream_id for c in arch.retained()]}
        out["cost_events"].append(ev.to_json())
    return out


def _counts(events):
    d: Dict[str, int] = {}
    for e in events:
        d[e["event"]] = d.get(e["event"], 0) + 1
    return d


def seal_future_queries(queries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """A future-query manifest sealed BEFORE any archive is examined against
    it. Each query names a task and its mechanical `solves(candidate)` rule
    by id; labels are never stored beside the archives."""
    blob = json.dumps(queries, sort_keys=True).encode()
    return {"schema": "archaeon.h3.future_queries.v0", "n": len(queries),
            "manifest_digest": "sha256:" + hashlib.sha256(blob).hexdigest(), "queries": queries}


def score_archives(archives: Dict[str, List[Candidate]], queries: List[Dict[str, Any]],
                   solves: Callable[[Candidate, Dict[str, Any]], bool]) -> Dict[str, Any]:
    """Direct candidate reuse only (no adaptation in alpha): a query is solved
    by an archive iff some retained candidate solves it. Reports the solve
    fraction per policy with the query count as the denominator."""
    out = {}
    for name, cands in archives.items():
        solved = sum(1 for q in queries if any(solves(c, q) for c in cands))
        out[name] = {"solved": solved, "assigned": len(queries), "solve_fraction": solved / len(queries) if queries else None}
    return out
