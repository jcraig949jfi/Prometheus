"""Lifetimes, the frozen Campaign-0 metric, and the controls of charter section 10.

Every function here is deterministic in (player spec, tasks, cfg, seed).
Metric definitions are DESIGN_C0.md section 4; control definitions are
section 5. Nothing in this module is tuned per Player.
"""

from __future__ import annotations

import hashlib
import json
import random

from . import tasks as tasks_mod
from .artifacts import BlockStore
from .player import run_task
from .workspace import Workspace

CONDITIONS = (
    "FRESH", "ACCUMULATED", "WORKSPACE_RESET", "WORKSPACE_SCRAMBLED",
    "ARTIFACT_ABLATION", "ARTIFACT_TRANSPLANT", "FULL_WORKSPACE_TRANSPLANT",
    "CODE_ONLY", "COMPUTE_MATCHED", "STORAGE_MATCHED",
)


# ---------------------------------------------------------------- metric


def task_cost(r: dict, cfg: dict) -> float:
    k = cfg["costs"]["steps_per_interaction"]
    return r["interactions_used"] + (r["vm_steps_used"] + r["ws_cost_units"]) / float(k)


def lifetime_metrics(results: list, cfg: dict) -> dict:
    cap = cfg["workspace"]["capacity_bytes"]
    n = max(1, len(results))
    competence = sum(max(0.0, r["final_performance"] - r["starting_performance"]) for r in results)
    if cfg["costs"].get("unsolved_charged_full_budget", False):
        # EXPLORATORY variant (configs/c0x.json, post hoc, see DESIGN_C0.md addendum): a task the Player
        # did not solve is charged its whole interaction budget as experience, so abstention is not free.
        experience = sum(1.0 if not r["success"] else r["interactions_used"] / float(r["interaction_budget"]) for r in results)
    else:
        experience = sum(r["interactions_used"] / float(r["interaction_budget"]) for r in results)
    compute = sum((r["vm_steps_used"] + r["ws_cost_units"]) / float(r["step_budget"]) for r in results)
    retained = sum((r["workspace_bytes"] + r["artifact_bytes"]) / float(cap) for r in results) / n
    efficiency = competence / (1.0 + experience + compute + retained)
    curve = [round(task_cost(r, cfg), 4) for r in results]
    by_depth = {}
    for r, c in zip(results, curve):
        by_depth.setdefault(r["depth"], []).append(c)
    late_early = {}
    for d, cs in sorted(by_depth.items()):
        if len(cs) < 2:
            late_early[str(d)] = None
            continue
        h = len(cs) // 2
        early = sum(cs[:h]) / h
        late = sum(cs[h:]) / (len(cs) - h)
        late_early[str(d)] = round(late / early, 4) if early > 0 else None
    by_stage = {}
    for r, c in zip(results, curve):
        s = by_stage.setdefault(r["stage"], {"n": 0, "cost": 0.0, "success": 0, "interactions": 0})
        s["n"] += 1
        s["cost"] += c
        s["success"] += 1 if r["success"] else 0
        s["interactions"] += r["interactions_used"]
    for s in by_stage.values():
        s["mean_cost"] = round(s["cost"] / s["n"], 3)
        s["success_rate"] = round(s["success"] / s["n"], 3)
        del s["cost"]
    return {
        "competence_gained": round(competence, 4),
        "experience": round(experience, 4),
        "compute": round(compute, 4),
        "retained_state": round(retained, 5),
        "C0_EFFICIENCY": round(efficiency, 5),
        "successes": sum(1 for r in results if r["success"]),
        "tasks": len(results),
        "interactions_total": sum(r["interactions_used"] for r in results),
        "vm_steps_total": sum(r["vm_steps_used"] for r in results),
        "ws_cost_total": sum(r["ws_cost_units"] for r in results),
        "artifacts_invoked_total": sum(r["artifacts_invoked"] for r in results),
        "blocks_created_total": sum(r["blocks_created"] for r in results),
        "adaptation_curve": curve,
        "late_early_ratio_by_depth": late_early,
        "by_stage": by_stage,
        "mean_cost": round(sum(curve) / n, 4),
    }


def replay_hash(results: list) -> str:
    payload = json.dumps([[r["task_index"], a, list(o)] for r in results for a, o in r["trajectory"]])
    return hashlib.sha256(payload.encode("ascii")).hexdigest()[:16]


def strip_trajectories(results: list) -> list:
    out = []
    for r in results:
        r2 = dict(r)
        r2["actions"] = [a for a, _ in r["trajectory"]]
        del r2["trajectory"]
        out.append(r2)
    return out


# ---------------------------------------------------------------- lifetimes


def _reset_points(tasks, cfg) -> list:
    first = tasks_mod.stage_first_indices(tasks)
    return sorted(first[s] for s in cfg["controls"]["reset_points_stages"] if s in first)


def run_lifetime(player, tasks, cfg, condition: str = "ACCUMULATED", seed: int = 0,
                 snapshot_index: int = None, keep_trajectories: bool = False) -> dict:
    """Conditions A-D. Returns task results, metrics, histories, replay hash, optional snapshot."""
    assert condition in ("FRESH", "ACCUMULATED", "WORKSPACE_RESET", "WORKSPACE_SCRAMBLED"), condition
    ws = Workspace.empty(cfg)
    blocks = BlockStore.empty(cfg)
    rng = random.Random("scramble:%d" % seed)
    points = set(_reset_points(tasks, cfg)) if condition in ("WORKSPACE_RESET", "WORKSPACE_SCRAMBLED") else set()
    results = []
    ws_hist = []
    snapshot = None
    for i, task in enumerate(tasks):
        if condition == "FRESH":
            ws = Workspace.empty(cfg)
            blocks = BlockStore.empty(cfg)
        if i in points:
            if condition == "WORKSPACE_RESET":
                ws.clear()
                blocks.clear()
            else:
                ws.scramble(rng)
                blocks.scramble(rng)
        if snapshot_index is not None and i == snapshot_index:
            snapshot = {"index": i, "ws": ws.snapshot(), "blocks": blocks.snapshot()}
        r = run_task(player, task, i, ws, blocks)
        results.append(r)
        ws_hist.append({"task": i, **ws.structure(), "blocks": blocks.structure()})
    out = {
        "condition": condition,
        "seed": seed,
        "metrics": lifetime_metrics(results, cfg),
        "replay_hash": replay_hash(results),
        "task_results": results if keep_trajectories else strip_trajectories(results),
        "workspace_history": ws_hist,
        "artifact_history": {
            "events": list(blocks.events),
            "invocations": {str(k): v for k, v in blocks.invocations.items()},
            "edges": [list(e) for e in blocks.edges],
            "final_blocks": [b.to_dict() for b in blocks.blocks.values()],
        },
        "reset_points": sorted(points),
    }
    if snapshot is not None:
        out["snapshot"] = snapshot
    return out


def run_remainder(player, tasks, cfg, start_index: int, ws_snap=None, blocks_snap=None,
                  step_budgets: dict = None, capacity_mult: float = 1.0) -> dict:
    """Run tasks[start_index:] from a given acquired state (controls E-J)."""
    ws = Workspace.empty(cfg)
    if capacity_mult != 1.0:
        ws.capacity = int(ws.capacity * capacity_mult)
    blocks = BlockStore.empty(cfg)
    if ws_snap is not None:
        ws.restore(ws_snap)
    if blocks_snap is not None:
        blocks.restore(blocks_snap)
    results = []
    for i in range(start_index, len(tasks)):
        sb = step_budgets.get(i) if step_budgets else None
        results.append(run_task(player, tasks[i], i, ws, blocks, step_budget=sb))
    return {
        "start_index": start_index,
        "metrics": lifetime_metrics(results, cfg),
        "replay_hash": replay_hash(results),
        "task_results": strip_trajectories(results),
        "artifact_invocations": {str(k): v for k, v in blocks.invocations.items()},
    }


def causal_controls(player, tasks, cfg, seed: int = 0) -> dict:
    """Controls E-J around a snapshot at the first task of the configured stage, plus the
    ACCUMULATED remainder for comparison. Returns one entry per condition."""
    first = tasks_mod.stage_first_indices(tasks)
    snap_i = first[cfg["controls"]["snapshot_stage"]]
    acc = run_lifetime(player, tasks, cfg, "ACCUMULATED", seed=seed, snapshot_index=snap_i)
    snap = acc["snapshot"]
    acc_rem = lifetime_metrics(
        [r for r in acc["task_results"] if r["task_index"] >= snap_i], cfg
    )
    out = {"snapshot_index": snap_i, "ACCUMULATED_remainder": acc_rem,
           "blocks_at_snapshot": sorted(snap["blocks"]["blocks"]),
           "workspace_at_snapshot": {"cells": len(snap["ws"]["cells"]), "streams": len(snap["ws"]["streams"]),
                                     "records": len(snap["ws"]["records"]), "links": sum(len(v) for v in snap["ws"]["links"].values())}}
    # E: ablate each block alone
    abl = {}
    for bid in sorted(snap["blocks"]["blocks"]):
        b2 = {"blocks": {k: v for k, v in snap["blocks"]["blocks"].items() if k != bid},
              "next_id": snap["blocks"]["next_id"]}
        abl[str(bid)] = run_remainder(player, tasks, cfg, snap_i, snap["ws"], b2)["metrics"]
    out["ARTIFACT_ABLATION"] = abl
    # E': ablate every block, keep data
    if snap["blocks"]["blocks"]:
        out["ARTIFACT_ABLATION_ALL"] = run_remainder(
            player, tasks, cfg, snap_i, snap["ws"], {"blocks": {}, "next_id": snap["blocks"]["next_id"]})["metrics"]
    # F: blocks only into a fresh copy
    out["ARTIFACT_TRANSPLANT"] = run_remainder(player, tasks, cfg, snap_i, None, snap["blocks"])["metrics"]
    # G: everything into a fresh copy
    out["FULL_WORKSPACE_TRANSPLANT"] = run_remainder(player, tasks, cfg, snap_i, snap["ws"], snap["blocks"])["metrics"]
    # H: code only
    h = run_remainder(player, tasks, cfg, snap_i, None, None)
    out["CODE_ONLY"] = h["metrics"]
    # I: code only with matched compute (2x what ACCUMULATED used per task, at least the config budget)
    used = {r["task_index"]: max(r["step_budget"], 2 * (r["vm_steps_used"] + r["ws_cost_units"]))
            for r in acc["task_results"] if r["task_index"] >= snap_i}
    out["COMPUTE_MATCHED"] = run_remainder(player, tasks, cfg, snap_i, None, None, step_budgets=used)["metrics"]
    # J: code only with doubled storage
    out["STORAGE_MATCHED"] = run_remainder(player, tasks, cfg, snap_i, None, None, capacity_mult=2.0)["metrics"]
    return out


def full_battery(player, tasks, cfg, seed: int = 0) -> dict:
    """Conditions A-D over the whole lifetime plus E-J from the snapshot; used by qualify."""
    out = {}
    for cond in ("ACCUMULATED", "FRESH", "WORKSPACE_RESET", "WORKSPACE_SCRAMBLED"):
        out[cond] = run_lifetime(player, tasks, cfg, cond, seed=seed)
    fresh = out["FRESH"]["task_results"]
    acc = out["ACCUMULATED"]["task_results"]
    out["reuse_gain"] = [round(task_cost(f, cfg) - task_cost(a, cfg), 4) for f, a in zip(fresh, acc)]
    out["causal"] = causal_controls(player, tasks, cfg, seed=seed)
    return out
