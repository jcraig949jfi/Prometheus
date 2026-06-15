"""First cross-agent void audits for the failure-primitive atlas (Stage 4 seed).

Runs the FP detectors against LOCAL ledgers of agents that did not author them:
- FP-003 bounded_menu_wall vs Apollo Branch C evolve logs (archive_cells diffs)
- FP-002 opaque_kill_black_hole vs Icarus training_stream failure_class column

Writes harmonia/experiments/fp_void_audits_20260610.json (per
feedback_background_output_capture: result file written from Python, flushed).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from harmonia.primitives.failure_primitives import (  # noqa: E402
    detect_bounded_menu_wall, detect_opaque_kill_blackhole)

OUT = Path(__file__).with_suffix(".json")
results = []


def record(fp, target, detector_result, context):
    row = {
        "fp": fp,
        "target": target,
        "fired": detector_result.fired,
        "headline": detector_result.headline,
        "evidence": detector_result.evidence,
        "context": context,
    }
    results.append(row)
    OUT.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"[{fp} vs {target}] fired={detector_result.fired} :: {detector_result.headline}")


def apollo_promotions(log_path: Path):
    """archive_cells is cumulative; promotions per gen = positive diffs."""
    cells = []
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                cells.append(json.loads(line)["archive_cells"])
            except (json.JSONDecodeError, KeyError):
                continue
    promos = [max(0, b - a) for a, b in zip(cells, cells[1:])]
    return cells, promos


def apollo_improvements(log_path: Path):
    """Honest promotion series for a capacity-bound archive: 1 iff best_acc
    strictly improved that gen (cell fills saturate by design at 20 cells —
    the capacity confound found in this audit)."""
    accs = []
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                accs.append(json.loads(line)["best_acc"])
            except (json.JSONDecodeError, KeyError):
                continue
    return accs, [1 if b > a else 0 for a, b in zip(accs, accs[1:])]


for run, name in [("run_branch_c", "apollo-branch-c-r1"),
                  ("run_branch_c_r2", "apollo-branch-c-r2")]:
    p = REPO / "apollo" / run / "evolve_log.jsonl"
    if not p.exists():
        record("FP-003", name, type("R", (), {
            "fired": False, "headline": "ledger missing", "evidence": {}})(),
            {"path": str(p), "status": "missing"})
        continue
    cells, promos = apollo_promotions(p)
    r = detect_bounded_menu_wall(promos, min_streak=30)
    record("FP-003", name + "-cellfills", r, {
        "path": str(p), "n_gens": len(cells),
        "first_cells": cells[0] if cells else None,
        "last_cells": cells[-1] if cells else None,
        "caveat": ("CAPACITY CONFOUND: archive bounded at 20 cells by design "
                   "(load-bearing-core keying); cell-fill series saturates "
                   "benignly. Use the -improvements cell for the verdict."),
    })
    accs, improvements = apollo_improvements(p)
    r2 = detect_bounded_menu_wall(improvements, min_streak=30)
    record("FP-003", name + "-improvements", r2, {
        "path": str(p), "n_gens": len(accs),
        "acc_start": accs[0] if accs else None,
        "acc_end": accs[-1] if accs else None,
        "note": ("promotion := strict best_acc improvement (honest series for "
                 "capacity-bound MAP-Elites). Search alive during tail "
                 "(mutation_viability=1.0, llm_used>0): zero-improvement tail "
                 "under fixed op menu. CAUSE ATTRIBUTION (structural ceiling "
                 "vs broken gate/Goodhart) not established here — candidate "
                 "FP-003 anchor pending Apollo-side cause audit."),
    })

ic = REPO / "agents" / "icarus" / "state" / "training_stream.jsonl"
labels = []
if ic.exists():
    with open(ic, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    labels.append(json.loads(line).get("failure_class", "MISSING"))
                except json.JSONDecodeError:
                    continue
r = detect_opaque_kill_blackhole(labels, min_records=1000)
record("FP-002", "icarus-training-stream", r, {
    "path": str(ic), "n": len(labels),
    "note": ("n far below min_records=1000 — cell honestly filled as "
             "RUN_INSUFFICIENT_VOLUME, not RUN_CLEAN; concentration evidence "
             "below threshold volume carries no verdict either way"),
})

# --- Ergon: FP-003 over the 5000-gen run (void-schedule cell FP-003 x ergon) ---
ergon_log = REPO / "ergon" / "logs" / "ergon_20260418_090119.jsonl"
if ergon_log.exists():
    deep, survived = [], []
    with open(ergon_log, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("event") == "generation_complete":
                d = r.get("data", {})
                deep.append(int(d.get("deep", 0)))
                survived.append(int(d.get("survived", 0)))
    for series_name, series in [("deep", deep), ("survived", survived)]:
        r = detect_bounded_menu_wall(series, min_streak=30)
        record("FP-003", f"ergon-20260418-{series_name}", r, {
            "path": str(ergon_log), "n_gens": len(series),
            "total": sum(series),
            "note": (f"promotion := {series_name} per generation; 2026-04-18 run, "
                     "fixed operator menu within run (no fingerprint column). "
                     "Historical run — agent not currently active."),
        })

# --- Icarus: FP-003 over cycle outcomes (void-schedule cell FP-003 x icarus) ---
ic_stream = REPO / "agents" / "icarus" / "state" / "training_stream.jsonl"
cycle_promos = []
if ic_stream.exists():
    with open(ic_stream, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            cycle_promos.append(0 if r.get("blocked_promotion") else 1)
r = detect_bounded_menu_wall(cycle_promos, min_streak=30)
record("FP-003", "icarus-cycle-stream", r, {
    "path": str(ic_stream), "n_cycles": len(cycle_promos),
    "note": ("promotion := cycle not blocked_promotion. n << 30: cell filled "
             "as RUN_INSUFFICIENT volume, no verdict either way."),
})

print(f"\n{len(results)} audit cells written to {OUT}")
