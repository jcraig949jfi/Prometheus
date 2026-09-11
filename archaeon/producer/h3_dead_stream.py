"""H3 dead-stream negative control + cheat control for the four archive
policies (ARCH-26; Apollo's delegation, comms #20, 2026-09-11).

Three streams of the SAME shape (128-entry rule tables, v1 descriptors
popcount / centre1_ones, v1 edges), same order, same byte sizes:

  live   score = hidden function of the table (agreement with a hidden target
                 on 12 hidden task bits) + small noise.  Organism -> score.
  dead   the live stream with the SCORE COLUMN PERMUTED (seeded).  The score
                 marginal is identical; the descriptor marginal is identical;
                 the only thing removed is the relation organism -> score
                 (feedback: a control must break the selection relation and
                 nothing else; a permutation is the exact-marginal way).
  cheat  score = exact solve count / 12, no noise: the score IS the reuse
                 target, so the direct-reuse channel must see success here or
                 the channel is blind (base role s2: cheat control).

Future queries, sealed BEFORE the run (their own commit):
  family A  the declared v1 manifest shape: score_at_least thresholds and
            occupies_cell (archaeon/docs/h0h5/H3_FUTURE_QUERIES_v1.json).
  family B  12 TASKS: a candidate solves task j iff its table agrees with the
            hidden target on task j's 3 bits.  Sealed as
            archaeon/docs/h0h5/H3_DEAD_STREAM_TASKS_v1.json.

Nothing here touches the engine or Vivarium; it is producer-side arithmetic
on the h3_replay policies.  Predictions live in
archaeon/docs/h0h5/H3_DEAD_STREAM_PREDICTION_2026-09-11.md and were
committed before run_control() was first executed.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from . import h3_replay as H

TABLE_BITS = 128
N_TASKS = 12
BITS_PER_TASK = 3
ASSAY = "assay:h3.dead_stream_control.v0"
EDGES_V1 = ((60.5, 64.5, 68.5), (29.5, 32.5, 35.5))      # H3_DESCRIPTORS_v1.json
CAPS = {"items": 16, "bytes": 16 * 40}                     # 16 slots; byte cap never binds by construction
RESERVE = 4
TASKS_PATH = Path(__file__).resolve().parents[1] / "docs" / "h0h5" / "H3_DEAD_STREAM_TASKS_v1.json"
# v2 (pre-registered addendum, 2026-09-11): v1 sat at the ceiling (top_k live 12/12 every seed,
# uniform floor 10.2/12); 5 bits per task puts a random table at 1/32 per task so 16 random
# tables reach ~4.8/12 and the channel has headroom.
DEFAULT_SEEDS = (1, 2, 3, 4, 5)
TASK_SEED = 20260911
TASKS_V2_PATH = TASKS_PATH.with_name("H3_DEAD_STREAM_TASKS_v2.json")
V2_BITS_PER_TASK = 5
V2_TASK_SEED = TASK_SEED + 1


# ----------------------------------------------------------------------------
# hidden target and tasks (sealed)
# ----------------------------------------------------------------------------
def make_tasks(seed: int = TASK_SEED, bits_per_task: int = BITS_PER_TASK) -> Dict[str, Any]:
    rng = random.Random(seed)
    target = [rng.randrange(2) for _ in range(TABLE_BITS)]
    idx = rng.sample(range(TABLE_BITS), N_TASKS * bits_per_task)
    tasks = []
    for j in range(N_TASKS):
        bits = sorted(idx[j * bits_per_task:(j + 1) * bits_per_task])
        tasks.append({"query_id": "task-%02d" % j, "rule": "agrees_on_bits", "bits": bits,
                      "target": [target[b] for b in bits]})
    sealed = H.seal_future_queries(tasks)
    sealed.update({"schema": "archaeon.h3.dead_stream_tasks.v1", "task_seed": seed, "table_bits": TABLE_BITS,
                   "bits_per_task": bits_per_task, "p_solve_per_random_table": 2.0 ** -bits_per_task,
                   "hidden_target_digest": "sha256:" + hashlib.sha256(bytes(target)).hexdigest()})
    return sealed


def solves(c: H.Candidate, q: Dict[str, Any]) -> bool:
    if q["rule"] == "agrees_on_bits":
        t = table_of(c)
        return all(t[b] == v for b, v in zip(q["bits"], q["target"]))
    if q["rule"] == "score_at_least":
        return c.score is not None and c.score >= q["threshold"]
    if q["rule"] == "occupies_cell":
        return H._cell(c, EDGES_V1) == q["cell"]
    raise ValueError(q["rule"])


def table_of(c: H.Candidate) -> List[int]:
    hexs = c.replay_ref.split("table:", 1)[1]
    n = int(hexs, 16)
    return [(n >> (TABLE_BITS - 1 - i)) & 1 for i in range(TABLE_BITS)]


def descriptors_of(table: Sequence[int]) -> Tuple[float, float]:
    pop = float(sum(table))
    centre1 = float(sum(table[i] for i in range(TABLE_BITS) if (i >> 3) & 1))   # bit 3 of the 7-bit index = centre cell
    return (pop, centre1)


def solve_count(table: Sequence[int], tasks: Sequence[Dict[str, Any]]) -> int:
    return sum(1 for q in tasks if all(table[b] == v for b, v in zip(q["bits"], q["target"])))


# ----------------------------------------------------------------------------
# the three streams
# ----------------------------------------------------------------------------
def make_streams(seed: int, n: int = 200, tasks: Sequence[Dict[str, Any]] | None = None,
                 fail_every: int = 17, noise: float = 0.05) -> Dict[str, List[H.Candidate]]:
    tasks = list(tasks or make_tasks()["queries"])
    rng = random.Random(seed)
    tables, live_scores, cheat_scores, sizes, failed = [], [], [], [], []
    for i in range(n):
        t = [rng.randrange(2) for _ in range(TABLE_BITS)]
        k = solve_count(t, tasks)
        tables.append(t); cheat_scores.append(round(k / N_TASKS, 6))
        live_scores.append(round(min(1.0, max(0.0, k / N_TASKS + rng.gauss(0.0, noise))), 6))
        sizes.append(16 + rng.randrange(0, 8)); failed.append(i % fail_every == 0)
    # permute the score column among the EVALUATED positions only: a failed
    # row has no score in any arm, so its slot must not enter the permutation
    # (found by test_dead_keeps_score_and_descriptor_marginals..., 2026-09-11)
    ev = [i for i in range(n) if not failed[i]]
    perm = list(ev); random.Random(seed * 7919 + 1).shuffle(perm)
    dead_scores = list(live_scores)
    for src, dst in zip(perm, ev):
        dead_scores[dst] = live_scores[src]

    def build(scores):
        out = []
        for i, t in enumerate(tables):
            n_int = int("".join(str(b) for b in t), 2)
            out.append(H.Candidate(stream_id=i, candidate_digest="sha256:" + hashlib.sha256(bytes(t)).hexdigest()[:24],
                                   birth_status="failed" if failed[i] else "evaluated", assay_ref=ASSAY,
                                   score=None if failed[i] else scores[i], descriptors=descriptors_of(t),
                                   byte_size=sizes[i], replay_ref="table:%032x" % n_int))
        return out
    return {"live": build(live_scores), "dead": build(dead_scores), "cheat": build(cheat_scores)}


# ----------------------------------------------------------------------------
# the control run
# ----------------------------------------------------------------------------
def family_a_queries() -> List[Dict[str, Any]]:
    qs = [{"query_id": "score-ge-%d" % i, "rule": "score_at_least", "threshold": th}
          for i, th in enumerate((0.3, 0.4, 0.5, 0.6, 0.7))]
    for cell in ("cell:0,0", "cell:0,3", "cell:3,0", "cell:3,3", "cell:1,1", "cell:2,2"):
        qs.append({"query_id": cell.replace(":", "-").replace(",", "-"), "rule": "occupies_cell", "cell": cell})
    return qs


def coverage(retained: Sequence[H.Candidate]) -> Dict[str, Any]:
    cells = {H._cell(c, EDGES_V1) for c in retained}
    return {"cells_occupied": len(cells), "grid_cells": 16, "coverage": len(cells) / 16.0}


def run_one(seed: int, tasks_sealed: Dict[str, Any]) -> Dict[str, Any]:
    tasks = tasks_sealed["queries"]
    streams = make_streams(seed, tasks=tasks)
    fam_a = family_a_queries()
    out: Dict[str, Any] = {"seed": seed, "arms": {}}
    for arm, s in streams.items():
        r = H.replay_all(s, CAPS, EDGES_V1, reserve=RESERVE, seed=seed, attempt_id="h3-dead-%s-%d" % (arm, seed))
        archives = {name: [c for c in s if c.stream_id in set(r["policies"][name]["retained_ids"])] for name in H.POLICIES}
        a = H.score_archives(archives, fam_a, solves)
        b = H.score_archives(archives, tasks, solves)
        stream_ceiling_b = sum(1 for q in tasks if any(solves(c, q) for c in s if c.birth_status == "evaluated"))
        out["arms"][arm] = {
            "stream_digest": r["stream"]["stream_digest"],
            "score_multiset_digest": "sha256:" + hashlib.sha256(json.dumps(sorted(c.score for c in s if c.score is not None)).encode()).hexdigest()[:16],
            "stream_ceiling_family_b": stream_ceiling_b,
            "policies": {name: {"archive_digest": r["policies"][name]["archive_digest"],
                                "retained_n": r["policies"][name]["retained_n"],
                                **coverage(archives[name]),
                                "family_a_solved": a[name]["solved"], "family_a_assigned": a[name]["assigned"],
                                "family_b_solved": b[name]["solved"], "family_b_assigned": b[name]["assigned"],
                                "retained_mean_score": (sum(c.score for c in archives[name]) / len(archives[name])) if archives[name] else None,
                                "bounds": r["policies"][name]["bounds"]} for name in H.POLICIES}}
    return out


def run_control(seeds: Sequence[int] = DEFAULT_SEEDS, tasks_path: Path = TASKS_PATH) -> Dict[str, Any]:
    tasks_sealed = json.loads(tasks_path.read_text(encoding="utf-8"))
    per_seed = [run_one(s, tasks_sealed) for s in seeds]
    summary: Dict[str, Any] = {}
    for name in H.POLICIES:
        summary[name] = {}
        for arm in ("live", "dead", "cheat"):
            vals = {k: [r["arms"][arm]["policies"][name][k] for r in per_seed]
                    for k in ("coverage", "family_a_solved", "family_b_solved", "retained_mean_score")}
            summary[name][arm] = {k: (sum(v) / len(v) if all(x is not None for x in v) else None) for k, v in vals.items()}
        summary[name]["deltas_dead_minus_live"] = {k: summary[name]["dead"][k] - summary[name]["live"][k]
                                                   for k in ("coverage", "family_a_solved", "family_b_solved")}
        summary[name]["deltas_cheat_minus_live"] = {k: summary[name]["cheat"][k] - summary[name]["live"][k]
                                                    for k in ("family_a_solved", "family_b_solved")}
    return {"schema": "archaeon.h3.dead_stream_control.v1", "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "tasks_manifest_digest": tasks_sealed["manifest_digest"], "tasks_path": tasks_path.name,
            "bits_per_task": tasks_sealed.get("bits_per_task", BITS_PER_TASK), "caps": CAPS, "edges": EDGES_V1, "reserve": RESERVE,
            "seeds": list(seeds), "n_per_stream": 200, "family_b_assigned": N_TASKS, "family_a_assigned": len(family_a_queries()),
            "per_seed": per_seed, "summary": summary}


def main(argv=None) -> int:
    from .. import workspace as _ws
    _ws.assert_not_canonical("run the H3 dead-stream control")          # D-23
    ap = argparse.ArgumentParser(prog="archaeon.producer.h3_dead_stream")
    ap.add_argument("--seal-tasks", action="store_true", help="write the sealed task manifest (refuses to overwrite)")
    ap.add_argument("--seal-tasks-v2", action="store_true", help="write the v2 (5 bits per task) sealed manifest (refuses to overwrite)")
    ap.add_argument("--run", metavar="OUT_JSON")
    ap.add_argument("--tasks", default="v1", choices=("v1", "v2"))
    a = ap.parse_args(argv)
    if a.seal_tasks_v2:
        if TASKS_V2_PATH.exists():
            raise SystemExit("refusing to overwrite the sealed manifest {}".format(TASKS_V2_PATH))
        TASKS_V2_PATH.write_text(json.dumps(make_tasks(V2_TASK_SEED, V2_BITS_PER_TASK), indent=1) + "\n", encoding="utf-8")
        print(TASKS_V2_PATH); return 0
    if a.seal_tasks:
        if TASKS_PATH.exists():
            raise SystemExit("refusing to overwrite the sealed manifest {}".format(TASKS_PATH))
        TASKS_PATH.write_text(json.dumps(make_tasks(), indent=1) + "\n", encoding="utf-8")
        print(TASKS_PATH); return 0
    if a.run:
        res = run_control(tasks_path=TASKS_V2_PATH if a.tasks == "v2" else TASKS_PATH)
        Path(a.run).write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(res["summary"], indent=1)); return 0
    ap.print_help(); return 1


if __name__ == "__main__":
    raise SystemExit(main())
