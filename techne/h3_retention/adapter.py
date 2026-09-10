"""pyribs retention adapter for H3 -- direct insertion of a declared stream, capped.

Spec: techne/h3_retention/STREAM_CONTRACT_V0.md.

The adapter replays ONE stream under ONE archive configuration and returns a full disposition
log. It does not compare retention policies -- that is H3's experiment and Archaeon's to run --
and it does not choose behavioural descriptors, because the descriptor choice IS the experiment.

Three things it refuses to do quietly:

  * inherit the tie policy from the donor. FIRST_WRITER_WINS is DECLARED here and VERIFIED
    against the installed pyribs at both granularities before any replay. A future release that
    changed it would break loudly instead of changing every retention number in silence.
  * drop a candidate. Every disposition is logged with the candidate's result_ref, so an
    evicted or refused candidate stays recoverable -- eviction is not deletion.
  * report a cap it did not exercise. The receipt names which of the three bounds -- count,
    bytes, or the grid's own cell count -- was actually operative, and says plainly when none
    was.
"""
from __future__ import annotations

import gc
from dataclasses import dataclass, field
from typing import Any, Iterable

import numpy as np

from .stream import Row, Stream

TIE_POLICY = "FIRST_WRITER_WINS"
TIE_POLICY_MEANING = (
    "An EXACTLY equal objective does not displace the incumbent of a cell. One-at-a-time: "
    "insertion requires strictly greater than the cell threshold, and the default threshold is "
    "the incumbent's own objective. Batch: among solutions tying for the highest objective in a "
    "cell, the one appearing FIRST in the batch is inserted."
)

DISPOSITIONS = (
    "RETAINED_NEW_CELL",        # occupied an empty cell
    "RETAINED_IMPROVED_CELL",   # beat the incumbent of an occupied cell
    "REJECTED_BY_ARCHIVE",      # did not beat the cell threshold (includes exact ties)
    "CAP_REFUSED_COUNT",        # would have occupied a new cell past max_retained
    "CAP_REFUSED_BYTES",        # its byte delta would have crossed max_bytes
)


class TiePolicyViolation(RuntimeError):
    """The installed pyribs does not implement the declared tie policy."""


class AdapterError(RuntimeError):
    pass


@dataclass
class Caps:
    """Two declared caps. Both required; see the contract for why one is not enough."""

    max_retained: int
    max_bytes: int

    def __post_init__(self) -> None:
        if self.max_retained <= 0 or self.max_bytes <= 0:
            raise AdapterError("both caps must be positive; a cap of zero is a refusal to run, "
                               "not a budget")


@dataclass
class Disposition:
    seq: int
    candidate_id: str
    candidate_digest: str
    disposition: str
    cell_index: int
    objective: float
    payload_bytes: int
    bytes_delta: int
    displaced_candidate_id: str | None
    result_ref: dict
    birth_status: str
    parent_ids: tuple[str, ...]
    reason: str = ""


@dataclass
class ReplayResult:
    stream_id: str
    archive_config: dict
    caps: dict
    tie_policy: dict
    log: list[Disposition]
    retained_ids: list[str]
    retained_bytes: int
    binding_constraint: str
    counts: dict
    emitter_guard: dict
    grid_cells: int
    recoverable: dict
    notes: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- tie verification
def _probe_archive(dims=(2,), ranges=((0.0, 1.0),), seed: int = 20260910):
    from ribs.archives import GridArchive
    return GridArchive(solution_dim=1, dims=list(dims), ranges=[list(r) for r in ranges],
                       seed=seed, extra_fields={"tag": ((), np.int32)})


def verify_tie_policy() -> dict:
    """Two probes, one per granularity. Raises rather than adapting to what it finds.

    The point is not to discover pyribs' behaviour -- that was measured on 2026-09-09 -- but to
    keep the DECLARATION load-bearing. An adapter that silently follows the donor's default has
    no policy, only a dependency.
    """
    from ribs.archives import GridArchive  # noqa: F401  (import guarded here, not at module load)

    out: dict[str, Any] = {"declared": TIE_POLICY, "meaning": TIE_POLICY_MEANING}

    # one-at-a-time: incumbent tag 1, challenger tag 2, identical objective and cell
    a = _probe_archive()
    a.add_single(np.array([1.0]), 5.0, np.array([0.25]), tag=np.int32(1))
    res = a.add_single(np.array([2.0]), 5.0, np.array([0.25]), tag=np.int32(2))
    seq_status = int(np.atleast_1d(res["status"])[0])
    seq_tags = sorted(int(t) for t in a.data()["tag"])
    out["sequential"] = {"challenger_status": seq_status, "retained_tags": seq_tags,
                         "first_writer_won": seq_tags == [1] and seq_status == 0}

    # batch: both in one call, incumbent first in the batch
    b = _probe_archive()
    b.add(np.array([[1.0], [2.0]]), np.array([5.0, 5.0]), np.array([[0.25], [0.25]]),
          tag=np.array([1, 2], dtype=np.int32))
    bat_tags = sorted(int(t) for t in b.data()["tag"])
    out["batch"] = {"retained_tags": bat_tags, "first_writer_won": bat_tags == [1]}

    out["verified"] = out["sequential"]["first_writer_won"] and out["batch"]["first_writer_won"]
    if not out["verified"]:
        raise TiePolicyViolation(
            f"declared {TIE_POLICY} but the installed pyribs did not implement it: "
            f"sequential retained {seq_tags}, batch retained {bat_tags}. The declaration is "
            f"load-bearing for every retention comparison; refusing to replay.")
    return out


# --------------------------------------------------------------------------- replay
def replay(stream: Stream, caps: Caps, *, dims: Iterable[int], granularity: str = "one_at_a_time",
           seed: int = 20260910, verify_ties: bool = True) -> ReplayResult:
    """Insert a validated stream directly into a GridArchive under two caps.

    ONE-AT-A-TIME ONLY, and the restriction is a consequence rather than an omission. A cap is
    a per-candidate admission decision; the archive's batch path resolves every within-batch
    collision internally and returns after the fact, so there is no moment at which a cap could
    be applied to a batch without reimplementing the donor's own tie rule -- which is exactly
    the thing this adapter refuses to do, because then the rule would be ours and a donor
    change would go unnoticed.

    The tie policy is still DECLARED AND TESTED at both granularities: verify_tie_policy()
    probes each directly, and replay_batch_equivalence() measures whether the two agree on
    retention for a given stream. Passing granularity="batch" here raises rather than silently
    running sequentially under a batch label.
    """
    if granularity != "one_at_a_time":
        raise AdapterError(
            f"granularity={granularity!r} is not available in the capped replay. A cap is a "
            f"per-candidate admission decision and the donor's batch path resolves collisions "
            f"before returning, so capping a batch would mean reimplementing its tie rule. Use "
            f"verify_tie_policy() for the batch tie probe and replay_batch_equivalence() for "
            f"the batch-vs-sequential retention comparison.")

    from ribs.archives import GridArchive

    tie = verify_tie_policy() if verify_ties else {"declared": TIE_POLICY, "verified": False,
                                                  "note": "verification SKIPPED by caller"}

    dims = list(dims)
    ranges = [list(r) for r in stream.ranges]
    archive = GridArchive(solution_dim=1, dims=dims, ranges=ranges, seed=seed,
                          extra_fields={"row_seq": ((), np.int32)})
    grid_cells = int(np.prod(dims))

    # cell -> (candidate_id, payload_bytes) for the current incumbent; the archive itself does
    # not carry our byte accounting, so it is kept beside it and reconciled at the end.
    incumbent: dict[int, tuple[str, int]] = {}
    retained_bytes = 0
    log: list[Disposition] = []
    counts = {d: 0 for d in DISPOSITIONS}
    bound_by = {"count": 0, "bytes": 0}

    def cell_of(row: Row) -> int:
        return int(archive.index_of_single(np.array(row.measures, dtype=float)))

    def consider(row: Row) -> Disposition:
        nonlocal retained_bytes
        idx = cell_of(row)
        occupied = idx in incumbent
        displaced_id, displaced_bytes = incumbent.get(idx, (None, 0))

        # count cap binds only on growth in occupancy
        if not occupied and len(incumbent) >= caps.max_retained:
            counts["CAP_REFUSED_COUNT"] += 1
            bound_by["count"] += 1
            return Disposition(
                row.seq, row.candidate_id, row.candidate_digest, "CAP_REFUSED_COUNT", idx,
                row.objective, row.payload_bytes, 0, None, row.result_ref, row.birth_status,
                row.parent_ids,
                reason=f"would occupy a new cell at retained={len(incumbent)} == "
                       f"max_retained={caps.max_retained}; logged with its result_ref so it "
                       f"stays recoverable")

        delta = row.payload_bytes - (displaced_bytes if occupied else 0)
        if retained_bytes + delta > caps.max_bytes:
            counts["CAP_REFUSED_BYTES"] += 1
            bound_by["bytes"] += 1
            return Disposition(
                row.seq, row.candidate_id, row.candidate_digest, "CAP_REFUSED_BYTES", idx,
                row.objective, row.payload_bytes, delta, displaced_id, row.result_ref,
                row.birth_status, row.parent_ids,
                reason=f"byte delta {delta:+d} on retained={retained_bytes} would cross "
                       f"max_bytes={caps.max_bytes}")

        res = archive.add_single(np.array([float(row.seq)]), row.objective,
                                 np.array(row.measures, dtype=float),
                                 row_seq=np.int32(row.seq))
        status = int(np.atleast_1d(res["status"])[0])
        if status == 0:
            counts["REJECTED_BY_ARCHIVE"] += 1
            return Disposition(
                row.seq, row.candidate_id, row.candidate_digest, "REJECTED_BY_ARCHIVE", idx,
                row.objective, row.payload_bytes, 0, displaced_id, row.result_ref,
                row.birth_status, row.parent_ids,
                reason=f"did not beat the cell threshold; under {TIE_POLICY} an exactly equal "
                       f"objective lands here")
        d = "RETAINED_NEW_CELL" if status == 2 else "RETAINED_IMPROVED_CELL"
        counts[d] += 1
        retained_bytes += delta
        incumbent[idx] = (row.candidate_id, row.payload_bytes)
        return Disposition(row.seq, row.candidate_id, row.candidate_digest, d, idx,
                           row.objective, row.payload_bytes, delta,
                           displaced_id if status == 1 else None, row.result_ref,
                           row.birth_status, row.parent_ids)

    for row in stream.rows:
        log.append(consider(row))

    retained_ids = [cid for cid, _ in incumbent.values()]
    live_emitters = _live_emitters()
    binding = _binding_constraint(bound_by, len(incumbent), caps, grid_cells, retained_bytes)

    # Reconcile our byte ledger against the archive's own occupancy -- if these disagree, the
    # accounting is wrong and the caps were enforced against a fiction.
    if len(incumbent) != len(archive):
        raise AdapterError(
            f"byte-ledger occupancy {len(incumbent)} disagrees with archive occupancy "
            f"{len(archive)}; the caps were enforced against an accounting that does not "
            f"match the archive")

    notes = []
    if binding == "NONE":
        notes.append(
            "NEITHER declared cap bound on this run. The caps are therefore implemented but "
            "NOT exercised, and this run is not evidence that they work. Use "
            "techne/h3_retention/fixture/stream_v0_capbind.jsonl or lower the caps.")

    return ReplayResult(
        stream_id=stream.stream_id,
        archive_config={"type": "GridArchive", "dims": dims, "ranges": ranges,
                        "solution_dim": 1, "seed": seed, "extra_fields": ["row_seq"],
                        "learning_rate": "default", "threshold_min": "default (-inf)",
                        "granularity": granularity},
        caps={"max_retained": caps.max_retained, "max_bytes": caps.max_bytes,
              "retained": len(incumbent), "retained_bytes": retained_bytes,
              "refused_for_count": bound_by["count"], "refused_for_bytes": bound_by["bytes"]},
        tie_policy=tie,
        log=log,
        retained_ids=sorted(retained_ids),
        retained_bytes=retained_bytes,
        binding_constraint=binding,
        counts=dict(counts),
        emitter_guard=live_emitters,
        grid_cells=grid_cells,
        recoverable={
            "logged": len(log),
            "not_retained": sum(counts[d] for d in
                                ("REJECTED_BY_ARCHIVE", "CAP_REFUSED_COUNT", "CAP_REFUSED_BYTES")),
            "all_non_retained_carry_a_result_ref": all(
                bool(d.result_ref.get("ref")) for d in log
                if d.disposition != "RETAINED_NEW_CELL" and d.disposition != "RETAINED_IMPROVED_CELL"),
            "rule": "eviction is not deletion -- every disposition keeps its result_ref, so the "
                    "retained set is derivable from the log and the log is not derivable from "
                    "the retained set",
        },
        notes=notes,
    )


def _binding_constraint(bound_by: dict, retained: int, caps: Caps, grid_cells: int,
                        retained_bytes: int) -> str:
    """Which of the THREE bounds was operative. A run where the grid bound first is not a test
    of the declared caps, and saying so is the difference between a cap and a decoration."""
    hits = []
    if bound_by["count"]:
        hits.append("COUNT")
    if bound_by["bytes"]:
        hits.append("BYTES")
    if retained >= grid_cells:
        hits.append("GRID_CELLS")
    if not hits:
        return "NONE"
    return "+".join(hits)


def _live_emitters() -> dict:
    """Instances, not modules. `import ribs.archives` eagerly imports 28 emitter and scheduler
    modules, so a module-presence gate could not fire on any input."""
    from ribs.emitters import EmitterBase
    from ribs.schedulers import Scheduler
    import sys
    live_e = [type(o).__name__ for o in gc.get_objects() if isinstance(o, EmitterBase)]
    live_s = [type(o).__name__ for o in gc.get_objects() if isinstance(o, Scheduler)]
    modules = sum(1 for m in sys.modules
                  if m.startswith("ribs.emitters") or m.startswith("ribs.schedulers"))
    return {"live_emitter_instances": live_e, "live_scheduler_instances": live_s,
            "modules_imported": modules,
            "gate": "INSTANCE-LEVEL (module presence is unreachable: importing ribs.archives "
                    "eagerly imports the emitters and schedulers packages)",
            "pass": not live_e and not live_s}


def replay_batch_equivalence(stream: Stream, caps: Caps, *, dims: Iterable[int],
                             seed: int = 20260910) -> dict:
    """Insert the identical stream as ONE batch, uncapped, and compare retained ids against the
    one-at-a-time replay under the same caps.

    Uncapped on the batch side is deliberate and stated: the archive's batch path resolves all
    collisions internally before returning, so there is no per-candidate moment at which a cap
    could be applied without reimplementing the donor's rule. This function therefore answers a
    narrower question than the capped replay -- do the two granularities agree on RETENTION when
    the caps are not binding -- and the answer is a fact about THIS stream, not a general
    equivalence.
    """
    from ribs.archives import GridArchive
    import numpy as _np

    dims = list(dims)
    arc = GridArchive(solution_dim=1, dims=dims, ranges=[list(r) for r in stream.ranges],
                      seed=seed, extra_fields={"row_seq": ((), _np.int32)})
    sols = _np.array([[float(r.seq)] for r in stream.rows], dtype=float)
    objs = _np.array([r.objective for r in stream.rows], dtype=float)
    meas = _np.array([list(r.measures) for r in stream.rows], dtype=float)
    seqs = _np.array([r.seq for r in stream.rows], dtype=_np.int32)
    arc.add(sols, objs, meas, row_seq=seqs)
    batch_seqs = sorted(int(s) for s in arc.data()["row_seq"])
    by_seq = {r.seq: r.candidate_id for r in stream.rows}
    batch_ids = sorted(by_seq[s] for s in batch_seqs)

    seq_result = replay(stream, caps, dims=dims, granularity="one_at_a_time", seed=seed,
                        verify_ties=False)
    caps_bound = seq_result.binding_constraint != "NONE"
    return {
        "batch_retained_ids": batch_ids,
        "one_at_a_time_retained_ids": seq_result.retained_ids,
        "identical": batch_ids == seq_result.retained_ids,
        "caps_bound_on_the_sequential_side": caps_bound,
        "comparison_is_meaningful": not caps_bound,
        "scope": "A fact about THIS stream. The two granularities can differ whenever a lower "
                 "candidate precedes a higher one in the same cell, because the batch path "
                 "takes the maximum over the batch while the sequential path applies "
                 "strictly-greater in arrival order. H3 must DECLARE its granularity rather "
                 "than rely on this agreement.",
        "caveat_if_caps_bound": ("The sequential side refused candidates for a cap while the "
                                 "batch side ran uncapped, so a difference here is a cap "
                                 "effect, not a granularity effect."
                                 if caps_bound else None),
    }
