"""pyribs first useful check. Runs INSIDE the isolated env; imports nothing from techne.

    <env>/python techne/acquisition/checks/pyribs_first_check.py

Design requirement: "Direct archive insertion from a frozen stream. Known collision/tie
outcomes and identical retained IDs under the declared adapter. Do not activate
emitters/schedulers in the retention experiment."

The named consumer is H3's retention-policy replay: four retention policies replayed
OFFLINE over ONE frozen candidate stream. For that comparison to mean anything, the
archive's own retention rules have to be MEASURED rather than assumed, because every
difference the experiment reports between policies is confounded by any archive behaviour
the experiment did not pin down.

So this check pins down four behaviours, each with a hand-computed expected answer:

    C1 new cell              a candidate in an empty cell is retained
    C2 collision, higher     a later candidate with a HIGHER objective replaces the incumbent
    C3 collision, lower      a later candidate with a LOWER objective does not
    C4 tie, exact            what happens on an EXACTLY equal objective -- and this differs
                             between WITHIN-batch and ACROSS-batch insertion, which is
                             precisely the kind of thing that silently changes a retention
                             comparison

and then asks whether batch insertion and one-at-a-time insertion of the IDENTICAL stream
retain the IDENTICAL ids. If they do not, H3 must declare its insertion granularity as
part of the policy, not treat it as an implementation detail.

No emitter and no scheduler is constructed. That is asserted against sys.modules at the
end, not merely intended.
"""
from __future__ import annotations

import json
import sys

import numpy as np
from ribs.archives import GridArchive

SOLUTION_DIM = 2
DIMS = (4, 4)
RANGES = [(0.0, 1.0), (0.0, 1.0)]
EXTRA = {"candidate_id": ((), np.int32)}


# ---------------------------------------------------------------- the frozen stream
# Hand-built so every retention rule has a hand-computed expected outcome. Measures are
# chosen to land squarely inside a cell, never on a boundary, so cell assignment is not
# itself a source of ambiguity.
STREAM = [
    # id, objective, measures, why this row exists
    (10, 1.0, (0.125, 0.125), "C1: first candidate in cell (0,0) -- new cell"),
    (11, 5.0, (0.375, 0.125), "C1: first candidate in cell (1,0) -- new cell"),
    (12, 2.0, (0.125, 0.125), "C2 setup: same cell as id 10, HIGHER objective -> replaces 10"),
    (13, 0.5, (0.125, 0.125), "C3: same cell, LOWER objective than incumbent 12 -> rejected"),
    (14, 5.0, (0.375, 0.125), "C4 tie: same cell as id 11, EXACTLY equal objective"),
    (15, 3.0, (0.625, 0.625), "C1: new cell (2,2)"),
    (16, 3.0, (0.875, 0.625), "C1: new cell (3,2) -- equal objective, DIFFERENT cell, both kept"),
]

EXPECTED_CELLS = {
    10: (0, 0), 12: (0, 0), 13: (0, 0),
    11: (1, 0), 14: (1, 0),
    15: (2, 2), 16: (3, 2),
}


def new_archive(seed: int = 20260909) -> GridArchive:
    return GridArchive(solution_dim=SOLUTION_DIM, dims=DIMS, ranges=RANGES,
                       seed=seed, extra_fields=EXTRA)


def _sol(cid: int) -> list[float]:
    # solution content is irrelevant to retention; made distinct so retained rows are
    # traceable even without the explicit id field
    return [float(cid), float(-cid)]


def retained_ids(arc: GridArchive) -> list[int]:
    data = arc.data()
    return sorted(int(x) for x in data["candidate_id"])


def cell_map(arc: GridArchive) -> dict:
    data = arc.data()
    out = {}
    for cid, m in zip(data["candidate_id"], data["measures"]):
        idx = arc.index_of_single(m)
        grid = arc.int_to_grid_index(np.array([idx]))[0]
        out[int(cid)] = tuple(int(g) for g in grid)
    return out


def insert_batch(arc: GridArchive) -> dict:
    sols = np.array([_sol(c) for c, _, _, _ in STREAM], dtype=float)
    objs = np.array([o for _, o, _, _ in STREAM], dtype=float)
    meas = np.array([m for _, _, m, _ in STREAM], dtype=float)
    ids = np.array([c for c, _, _, _ in STREAM], dtype=np.int32)
    res = arc.add(sols, objs, meas, candidate_id=ids)
    return {"status": [int(s) for s in np.atleast_1d(res["status"])],
            "value": [float(v) for v in np.atleast_1d(res["value"])]}


def insert_sequential(arc: GridArchive) -> list[dict]:
    out = []
    for cid, obj, m, why in STREAM:
        res = arc.add_single(np.array(_sol(cid), dtype=float), obj,
                            np.array(m, dtype=float), candidate_id=np.int32(cid))
        out.append({"candidate_id": cid, "objective": obj,
                    "status": int(np.atleast_1d(res["status"])[0]),
                    "value": float(np.atleast_1d(res["value"])[0]), "why": why})
    return out


# ---------------------------------------------------------------- the cases
def main() -> int:
    a_batch = new_archive()
    batch_res = insert_batch(a_batch)
    batch_ids = retained_ids(a_batch)
    batch_cells = cell_map(a_batch)

    a_seq = new_archive()
    seq_res = insert_sequential(a_seq)
    seq_ids = retained_ids(a_seq)
    seq_cells = cell_map(a_seq)

    # determinism: the identical stream into a second fresh archive, same granularity
    a_seq2 = new_archive()
    insert_sequential(a_seq2)
    seq2_ids = retained_ids(a_seq2)
    a_batch2 = new_archive()
    insert_batch(a_batch2)
    batch2_ids = retained_ids(a_batch2)

    # Hand-computed expectations for SEQUENTIAL insertion:
    #   cell (0,0): 10 retained, then 12 (2.0 > 1.0) replaces it, then 13 (0.5) rejected -> 12
    #   cell (1,0): 11 retained, then 14 ties exactly at 5.0. add requires STRICTLY greater
    #               than the cell threshold, which for default learning_rate/threshold_min is
    #               the incumbent objective, so the incumbent 11 survives.
    #   cells (2,2) and (3,2): 15 and 16, both new, both retained
    expected_sequential = sorted([12, 11, 15, 16])

    # Hand-computed expectation for BATCH insertion, from the documented rule:
    #   "If multiple solutions end up in the same cell, we only insert the solution with the
    #    highest objective. If multiple solutions ... tie for the highest objective, we insert
    #    the solution that appears first in the batch."
    #   cell (0,0): max objective among {10:1.0, 12:2.0, 13:0.5} -> 12
    #   cell (1,0): tie at 5.0 between 11 and 14; 11 appears first -> 11
    expected_batch = sorted([12, 11, 15, 16])

    seq_by_id = {r["candidate_id"]: r for r in seq_res}
    cases = [
        {"case": "C1_NEW_CELL",
         "claim": "a candidate landing in an empty cell is retained with status 2 (new cell)",
         "observed_status": {cid: seq_by_id[cid]["status"] for cid in (10, 11, 15, 16)},
         "expected_status": 2,
         "pass": all(seq_by_id[cid]["status"] == 2 for cid in (10, 11, 15, 16))},
        {"case": "C2_COLLISION_HIGHER_OBJECTIVE_REPLACES",
         "claim": "id 12 (obj 2.0) replaces incumbent id 10 (obj 1.0) in cell (0,0)",
         "observed_status_12": seq_by_id[12]["status"], "expected_status": 1,
         "id_10_retained_after": 10 in seq_ids,
         "id_12_retained_after": 12 in seq_ids,
         "pass": seq_by_id[12]["status"] == 1 and 12 in seq_ids and 10 not in seq_ids},
        {"case": "C3_COLLISION_LOWER_OBJECTIVE_REJECTED",
         "claim": "id 13 (obj 0.5) is rejected against incumbent id 12 (obj 2.0)",
         "observed_status_13": seq_by_id[13]["status"], "expected_status": 0,
         "id_13_retained": 13 in seq_ids,
         "pass": seq_by_id[13]["status"] == 0 and 13 not in seq_ids},
        {"case": "C4_EXACT_TIE_ACROSS_SEQUENTIAL_ADDS",
         "claim": "an EXACTLY equal objective does NOT displace the incumbent, because "
                  "insertion requires strictly greater than the cell threshold and the "
                  "default threshold is the incumbent's own objective",
         "incumbent": 11, "challenger": 14, "objective_both": 5.0,
         "observed_status_14": seq_by_id[14]["status"], "expected_status": 0,
         "incumbent_survived": 11 in seq_ids and 14 not in seq_ids,
         "pass": seq_by_id[14]["status"] == 0 and 11 in seq_ids and 14 not in seq_ids,
         "consequence_for_h3": "First-writer-wins on exact ties. Any H3 retention policy that "
                               "expects last-writer-wins on ties is NOT what this archive "
                               "does, and a policy comparison that does not state this is "
                               "measuring the archive's default alongside its own rule."},
        {"case": "C4b_EXACT_TIE_WITHIN_ONE_BATCH",
         "claim": "upstream documents first-in-batch winning an exact tie; measured here",
         "batch_retained_ids": batch_ids,
         "tie_winner_observed": 11 if 11 in batch_ids else (14 if 14 in batch_ids else None),
         "tie_winner_expected_from_docs": 11,
         "pass": (11 in batch_ids) and (14 not in batch_ids)},
        {"case": "CELL_ASSIGNMENT_MATCHES_HAND_COMPUTATION",
         "claim": "every retained candidate sits in the cell computed by hand from the "
                  "measures and the declared 4x4 tessellation over [0,1]^2",
         "observed_cells_sequential": {str(k): list(v) for k, v in seq_cells.items()},
         "expected_cells": {str(k): list(EXPECTED_CELLS[k]) for k in seq_cells},
         "pass": all(seq_cells[k] == EXPECTED_CELLS[k] for k in seq_cells)},
        {"case": "RETAINED_IDS_MATCH_HAND_COMPUTATION",
         "claim": "retained ids under sequential insertion are exactly the hand-computed set",
         "observed": seq_ids, "expected": expected_sequential,
         "pass": seq_ids == expected_sequential},
        {"case": "DETERMINISM_SAME_STREAM_SAME_RETAINED_IDS",
         "claim": "the identical stream inserted into a second fresh archive retains the "
                  "identical ids, for both granularities",
         "sequential": {"run1": seq_ids, "run2": seq2_ids, "identical": seq_ids == seq2_ids},
         "batch": {"run1": batch_ids, "run2": batch2_ids, "identical": batch_ids == batch2_ids},
         "pass": seq_ids == seq2_ids and batch_ids == batch2_ids},
        {"case": "BATCH_VS_SEQUENTIAL_GRANULARITY",
         "claim": "batch and one-at-a-time insertion of the IDENTICAL stream retain the same "
                  "ids on THIS stream -- which is a statement about this stream, not a "
                  "general equivalence",
         "batch_ids": batch_ids, "sequential_ids": seq_ids,
         "identical": batch_ids == seq_ids,
         "expected_batch_from_docs": expected_batch,
         "pass": batch_ids == seq_ids == expected_batch,
         "scope_limit": "The two granularities agree here because every collision in this "
                        "stream resolves the same way under 'max of batch' and under "
                        "'sequential strictly-greater'. A stream where a LOW candidate "
                        "precedes a HIGH one in the same cell could differ in reported "
                        "STATUS even when the retained set matches. H3 should declare its "
                        "granularity rather than rely on this agreement."},
    ]

    # What "no emitters" can actually be checked against.
    #
    # The first version of this gate asserted that no ribs.emitters / ribs.schedulers module
    # appears in sys.modules. MEASURED: `import ribs.archives` eagerly imports the entire
    # emitters and schedulers tree -- 30+ modules -- so that gate could not pass on any input
    # and was testing nothing. Same error class as a threshold placed outside its attainable
    # range. The reachable gate is about INSTANCES: no emitter and no scheduler object exists.
    import gc
    from ribs.emitters import EmitterBase
    from ribs.schedulers import Scheduler

    modules_present = sorted(m for m in sys.modules
                             if m.startswith("ribs.emitters") or m.startswith("ribs.schedulers"))
    live_emitters = [type(o).__name__ for o in gc.get_objects() if isinstance(o, EmitterBase)]
    live_schedulers = [type(o).__name__ for o in gc.get_objects() if isinstance(o, Scheduler)]
    no_emitters = {
        "case": "NO_EMITTER_OR_SCHEDULER_INSTANCE_EXISTS",
        "claim": "the retention check inserts a frozen stream directly; no emitter object and "
                 "no scheduler object is ever constructed",
        "live_emitter_instances": live_emitters,
        "live_scheduler_instances": live_schedulers,
        "n_emitter_or_scheduler_modules_imported": len(modules_present),
        "module_presence_is_not_the_gate": (
            "`import ribs.archives` eagerly imports the emitters and schedulers packages "
            f"({len(modules_present)} modules on ribs 0.12.0). A gate on module presence is "
            "unreachable and was replaced by this instance-level gate after measuring that."),
        "pass": not live_emitters and not live_schedulers,
        "why": "An emitter would GENERATE candidates from the archive's own state, which "
               "would make the stream a function of the retention policy under test -- the "
               "control drawn from the treatment's own selection relation.",
    }
    cases.append(no_emitters)

    out = {
        "check": "pyribs_first_useful_check",
        "tool": "ribs",
        "ribs_version": __import__("ribs").__version__,
        "numpy_version": np.__version__,
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "archive": {"type": "GridArchive", "dims": list(DIMS), "ranges": RANGES,
                    "solution_dim": SOLUTION_DIM, "seed": 20260909,
                    "learning_rate": "default", "threshold_min": "default (-inf)",
                    "extra_fields": ["candidate_id"]},
        "frozen_stream": [{"candidate_id": c, "objective": o, "measures": list(m), "why": w}
                          for c, o, m, w in STREAM],
        "batch_add_result": batch_res,
        "sequential_add_result": seq_res,
        "retained_ids_batch": batch_ids,
        "retained_ids_sequential": seq_ids,
        "cases": cases,
        "n_total": len(cases),
        "n_passed": sum(1 for c in cases if c["pass"]),
        "all_passed": all(c["pass"] for c in cases),
    }
    print(json.dumps(out))
    return 0 if out["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
