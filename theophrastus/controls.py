"""Founding self-controls (charter XV). Every function returns FINDINGS --
typed dicts with a `code` -- and never a verdict. A finding with
`refuse=True` keeps the cell out of execution.

    C1  DUPLICATE_CELL          the same cell_id proposed twice in a batch,
                                or already executed at this engine
    C2  COORDINATE_ALIAS        two different labels, one spec_hash
    C3  WORLD_LABEL_MISMATCH    a world label whose content differs from the
                                registered content for that label
    C4  BRANCH_WITHOUT_EVIDENCE branch.evidence is None
    C5  INTERVENTION_NOOP       an intervention whose spec_hash equals the
                                NONE cell's spec_hash on the same coordinates
    C6  REPLAY_MISMATCH         two rows at one spec_hash, both claiming
                                BIT_DETERMINISTIC, with different digests
    C7  MISSING_PROVENANCE      mechanism.provenance is None
    C8  STALE_RESULT            a cached row from a different engine source
                                hash / instance offered for reuse
    C9  selection is TYPED: `select()` reads coordinates only; a test proves
                                that rationale text cannot reorder it
    C10 BUDGET_EXHAUSTED        the explorer refuses the (N+1)th execution
    CHEAT_SIGNAL                `admit_signal()` refuses a contrast with no
                                stencil / no replication / no rows
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Iterable, List, Optional

from .cell import Cell


BASELINE_INTERVENTION = "NONE"


def _finding(code: str, refuse: bool, **kw) -> dict:
    return {"code": code, "refuse": refuse, **kw}


# ---------------------------------------------------------------- C1-C5, C7
def check_batch(cells: List[Cell], *, registered_worlds: Dict[str, str],
                executed_spec_hashes: Iterable[str] = ()) -> Dict[str, List[dict]]:
    """Static checks on a batch of proposals BEFORE any execution.
    Returns {cell_id: [findings]}; an empty list means clean."""
    executed = set(executed_spec_hashes)
    out: Dict[str, List[dict]] = {c.cell_id: [] for c in cells}
    seen_ids: Dict[str, Cell] = {}
    by_hash: Dict[str, List[Cell]] = {}
    for c in cells:
        cid = c.cell_id
        # C7 / C4: provenance and evidence are required values, not labels
        if c.mechanism.provenance is None:
            out[cid].append(_finding("MISSING_PROVENANCE", True,
                                     mechanism=c.mechanism.name))
        if c.branch.evidence is None:
            out[cid].append(_finding("BRANCH_WITHOUT_EVIDENCE", True,
                                     branch=c.branch.name))
        # C3: the label must mean what the registry says it means
        reg = registered_worlds.get(c.world.label)
        if reg is not None and reg != c.world.identity:
            out[cid].append(_finding("WORLD_LABEL_MISMATCH", True,
                                     label=c.world.label,
                                     registered=reg, offered=c.world.identity,
                                     offered_content=c.world.content()))
        # C1: duplicates within the batch and against the executed record
        if cid in seen_ids:
            out[cid].append(_finding("DUPLICATE_CELL", True, first=seen_ids[cid].short()))
        seen_ids.setdefault(cid, c)
        try:
            h = c.spec_hash
        except Exception as exc:                    # noqa: BLE001
            out[cid].append(_finding("SPEC_INVALID", True, error=str(exc)[:300]))
            continue
        if h in executed:
            out[cid].append(_finding("DUPLICATE_CELL", True, already_executed=h))
        by_hash.setdefault(c.execution_hash, []).append(c)
    # C2: one EXECUTION under two label tuples is an alias (the sealed spec
    # may differ in its pew identity block; the engine executes the same thing)
    for h, group in by_hash.items():
        labels = {json.dumps(c.labels, sort_keys=True) for c in group}
        if len(labels) > 1:
            for c in group:
                out[c.cell_id].append(_finding("COORDINATE_ALIAS", True,
                                               execution_hash=h,
                                               labels=sorted(labels)))
    # C5: an intervention whose LABEL claims a change but whose execution
    # equals the baseline's did nothing
    baseline = {}
    for c in cells:
        if c.intervention.label == BASELINE_INTERVENTION:
            key = (c.mechanism.rule_hex, c.world.identity, c.pressure.identity,
                   c.seed_root)
            baseline[key] = c.execution_hash
    for c in cells:
        if c.intervention.label != BASELINE_INTERVENTION:
            key = (c.mechanism.rule_hex, c.world.identity, c.pressure.identity,
                   c.seed_root)
            if key in baseline and baseline[key] == c.execution_hash:
                out[c.cell_id].append(_finding("INTERVENTION_NOOP", True,
                                               intervention=c.intervention.label))
    return out


# ---------------------------------------------------------------------- C6
def result_digest(work_result: dict) -> str:
    """The digest a replay must reproduce: the per-repeat accuracies and the
    per-repeat mask digests, nothing that carries wall-clock."""
    reps = work_result.get("repeats") or []
    core = [{"i": r.get("repeat_index"), "seed": r.get("seed"),
             "accuracy": (r.get("result") or {}).get("accuracy"),
             "mask": (r.get("result") or {}).get("mask_digest")} for r in reps]
    return "sha256:" + hashlib.sha256(
        json.dumps(core, sort_keys=True).encode()).hexdigest()


def check_replay(rows: List[dict]) -> List[dict]:
    """Rows at ONE spec_hash. A determinism claim with different digests is a
    finding about the instrument, not about the mechanism."""
    out = []
    det = [r for r in rows if r.get("reproducibility") == "BIT_DETERMINISTIC"
           and r.get("status") == "COMPLETED"]
    digests = {r.get("result_digest") for r in det}
    if len(digests) > 1:
        out.append(_finding("REPLAY_MISMATCH", True,
                            digests=sorted(d for d in digests if d),
                            rows=[r.get("row_id") for r in det]))
    elif len(det) >= 2:
        out.append(_finding("REPLAY_OK", False, n=len(det),
                            digest=next(iter(digests))))
    return out


# ---------------------------------------------------------------------- C8
def reusable(row: dict, *, engine_source_hash: str, engine_instance_id: str,
             spec_hash: str) -> dict:
    """May a recorded row stand in for a fresh execution of `spec_hash`?
    Only when the spec, the build AND the ledger identity all match."""
    if row.get("spec_hash") != spec_hash:
        return _finding("STALE_RESULT", True, why="spec_hash differs")
    eng = row.get("engine") or {}
    if eng.get("engine_source_hash") != engine_source_hash:
        return _finding("STALE_RESULT", True, why="engine_source_hash differs",
                        row_build=eng.get("engine_source_hash"))
    if eng.get("engine_instance_id") != engine_instance_id:
        return _finding("STALE_RESULT", True, why="engine_instance_id differs")
    if row.get("status") != "COMPLETED":
        return _finding("STALE_RESULT", True, why="row not COMPLETED")
    return _finding("REUSABLE", False)


# ---------------------------------------------------------------------- C9
def selection_key(c: Cell) -> tuple:
    """Deterministic, TYPED ordering over coordinates only. Proposal text,
    proposer identity and rationale are not inputs; the test in
    tests/test_controls.py mutates them and asserts the order is unchanged."""
    return (c.world.n_cells * c.world.steps,                # cheaper worlds first
            c.pressure.identity, c.mechanism.rule_hex,
            c.intervention.transform, c.seed_root, c.cell_id)


def select(cells: List[Cell], *, dead: Iterable[str] = (),
           mode: str = "coverage") -> List[Cell]:
    """Order a batch for execution. `coverage` skips cells inside dead
    neighbourhoods (the seat consumes its own negative history);
    `counterfactual` visits them deliberately; `expansion` keeps the order."""
    dead = set(dead)
    if mode == "coverage":
        pool = [c for c in cells if c.cell_id not in dead]
    elif mode == "counterfactual":
        pool = [c for c in cells if c.cell_id in dead] or list(cells)
    elif mode == "expansion":
        pool = list(cells)
    else:
        raise ValueError("unknown mode %r" % mode)
    return sorted(pool, key=selection_key)


# --------------------------------------------------------------------- C10
class Budget:
    def __init__(self, max_executions: int, max_wall_s: float):
        self.max_executions = int(max_executions)
        self.max_wall_s = float(max_wall_s)
        self.executions = 0
        self.t0 = time.monotonic()

    def state(self) -> dict:
        return {"executions": self.executions, "max_executions": self.max_executions,
                "wall_s": round(time.monotonic() - self.t0, 1),
                "max_wall_s": self.max_wall_s}

    def charge(self) -> dict:
        """Returns a finding; refuse=True means the execution must not run."""
        if self.executions >= self.max_executions:
            return _finding("BUDGET_EXHAUSTED", True, **self.state())
        if time.monotonic() - self.t0 > self.max_wall_s:
            return _finding("BUDGET_EXHAUSTED", True, **self.state())
        self.executions += 1
        return _finding("BUDGET_OK", False, **self.state())


# ------------------------------------------------------------- CHEAT_SIGNAL
def admit_signal(contrast: dict) -> dict:
    """The gate a contrast must pass before it may be written as a
    THEO-SIGNAL. A fabricated interesting number fails here because it has
    no rows, no stencil and no replication, whatever its magnitude."""
    missing = []
    for key in ("rows_a", "rows_b"):
        if not contrast.get(key):
            missing.append(key)
    if not contrast.get("stencil_cells"):
        missing.append("stencil_cells")
    if not contrast.get("replication"):
        missing.append("replication")
    if contrast.get("disposition") != "REPRODUCIBLE_SIGNAL":
        missing.append("disposition!=REPRODUCIBLE_SIGNAL")
    if missing:
        return _finding("SIGNAL_REFUSED", True, missing=missing,
                        offered_delta=contrast.get("delta"))
    return _finding("SIGNAL_ADMITTED", False)
