"""G-R4-4 (round 4 P0, builder G): the screen list primordial/ledger/qd/worlds_r4.json and its JIT guard.

Schema worlds_r4/v1 (H 1789433688592-0, A 1789433714703-0, G 1789433928197-0). One record per
world x pressure:
  floor_parts        abstain, best_constant, uniform_random_median, input_invariant_learner (null = not run)
  floor, floor_kind  max of the parts run; floor_is_bound + bound_parts when the learner was not run
  gate_held64        the gate column
  learner            {status run|not_run, median, iqr, held64_by_run_seed, run_seeds, budget_ok}
  baseline           M2: {median, ci95, bytes, n_runs, held64_by_run_seed, elites} or null (never reached stage 2)
  stage              1 (no baseline) or 2
  verdicts           {"q1|q2": {verdict SURVIVED|CULLED|HELD, cull_reason, floor}} for all four variants
  verdict, cull_reason   the active variant's (top-level q1_floor_policy / q2_policy)
  sources            exp_ids and rows files of every number
Numbers are never recomputed here: records are assembled from the floor_suite, baseline and learner rows.
A record whose floor is a bound that could change a verdict is PENDING_LEARNER, and `write` refuses.

The guard: `guard(doc, world, pressure)` -> None for a SURVIVED cell under the active variant, else an
INELIGIBLE dict (UNSCREENED if absent, else CULLED or HELD). Graphworld worlds are named w<gen_seed>.
"""
from __future__ import annotations

import json
import pathlib
import re

from primordial.metric import screen as SC
from primordial.metric import suite as SU
from primordial.metric.ci import BOOT_SEED, N_BOOT

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORLDS_R4 = ROOT / "primordial" / "ledger" / "qd" / "worlds_r4.json"
SCHEMA = "worlds_r4/v1"
GRAPHWORLD = re.compile(r"^w\d+$")
PENDING = "PENDING_LEARNER"


def is_graphworld(world: str) -> bool:
    return bool(GRAPHWORLD.match(str(world)))


def _learner_block(summary: dict) -> dict:
    return {"status": "run", "median": summary["invariant_held64_median"], "iqr": summary["invariant_held64_iqr"],
            "held64_by_run_seed": summary["held64_by_run_seed"], "run_seeds": summary["run_seeds"],
            "budget_ok": summary["budget_ok"]}


def cell(suite_row: dict, baseline: dict | None = None, learner: dict | None = None, sources: dict | None = None) -> dict:
    """One record from a floor_suite row, the cell's M2 baseline row (or None) and, for a pressure whose suite
    row has no learner, that pressure's own learner summary (or None)."""
    key = (suite_row["gen_seed"], suite_row["pressure"])
    parts, lrn = dict(suite_row["floor_parts"]), dict(suite_row["learner"])
    if learner is not None:
        if (learner["gen_seed"], learner["pressure"]) != key:
            raise ValueError(f"learner {learner['gen_seed']}/{learner['pressure']} is not this cell's {key}")
        parts["input_invariant_learner"] = learner["invariant_held64_median"]
        lrn = _learner_block(learner)
    f = SU.floor_of_parts(parts)
    gate = float(suite_row["gate_held64"])
    rec = {"world": suite_row["world"], "gen_seed": int(suite_row["gen_seed"]), "pressure": suite_row["pressure"],
           "floor_parts": parts, **f, "gate_held64": gate, "learner": lrn, "sources": sources or {}}
    if baseline is None:
        rec.update(stage=1, baseline=None,
                   verdicts={SC.vkey(*v): {"verdict": "CULLED", "cull_reason": "NOT_REACHED"} for v in SC.VARIANTS})
        return rec
    if (baseline["gen_seed"], baseline["pressure"]) != key:
        raise ValueError(f"baseline {baseline['gen_seed']}/{baseline['pressure']} is not this cell's {key}")
    lo = float(baseline["ci95"][0])
    rec.update(stage=2, baseline={k: baseline[k] for k in ("median", "ci95", "bytes", "n_runs", "held64_by_run_seed")}
               | {"elites": baseline.get("elites")})
    if f["floor_is_bound"] and SC.needs_learner(f["floor"], gate, lo):
        rec["verdicts"] = {SC.vkey(*v): {"verdict": PENDING, "cull_reason": None} for v in SC.VARIANTS}
    else:
        rec["verdicts"] = SC.verdicts(f["floor"], gate, lo)
    return rec


def build(records: list[dict], commit: str, active=SC.ACTIVE, max_survivors: int = SC.MAX_SURVIVORS) -> dict:
    cells = SC.apply_stop(records, max_survivors)
    k = SC.vkey(*active)
    for c in cells:
        c["verdict"], c["cull_reason"] = c["verdicts"][k]["verdict"], c["verdicts"][k]["cull_reason"]
    return {"schema": SCHEMA, "commit": commit,
            "bootstrap": {"fn": "primordial.metric.ci.median_ci", "stat": "median", "resamples": N_BOOT,
                          "alpha": 0.05, "rng": "numpy PCG64", "seed": BOOT_SEED},
            "q1_floor_policy": active[0], "q2_policy": active[1], "max_survivors": max_survivors,
            "variants": [SC.vkey(*v) for v in SC.VARIANTS], "cells": cells}


def pending(doc: dict) -> list[tuple]:
    return [(c["world"], c["pressure"]) for c in doc["cells"]
            if any(v["verdict"] == PENDING or (v.get("computed") or {}).get("verdict") == PENDING
                   for v in c["verdicts"].values())]


def write(doc: dict, path=WORLDS_R4) -> pathlib.Path:
    p = pending(doc)
    if p:
        raise ValueError(f"{len(p)} cells still need the learner before a verdict is exact: {p[:5]}")
    path = pathlib.Path(path)                        # an all-culled screen is written too: it is the result
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    return path


def load(path=WORLDS_R4) -> dict | None:
    p = pathlib.Path(path)
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA:
        raise ValueError(f"{p} is not {SCHEMA}")
    return doc


def lookup(doc: dict | None, world: str, pressure: str) -> dict | None:
    if not doc:
        return None
    for c in doc["cells"]:
        if c["world"] == world and c["pressure"] == pressure:
            return c
    return None


def guard(doc: dict | None, world: str, pressure: str) -> dict | None:
    """JIT lookup guard: None iff the cell SURVIVED under the file's active variant. Never recomputes."""
    c = lookup(doc, world, pressure)
    if c is None:
        return {"verdict": "INELIGIBLE", "why": "UNSCREENED", "world": world, "pressure": pressure}
    k = SC.vkey(doc["q1_floor_policy"], doc["q2_policy"])
    v = c["verdicts"][k]
    if v["verdict"] == "SURVIVED":
        return None
    return {"verdict": "INELIGIBLE", "why": v["verdict"], "cull_reason": v.get("cull_reason"),
            "world": world, "pressure": pressure, "variant": k}


def survivor_worlds(doc: dict | None) -> list[str]:
    """Graphworld worlds with >= 1 SURVIVED pressure under the active variant, in gen_seed order."""
    if not doc:
        return []
    k = SC.vkey(doc["q1_floor_policy"], doc["q2_policy"])
    ws = {c["world"]: c["gen_seed"] for c in doc["cells"] if c["verdicts"][k]["verdict"] == "SURVIVED"}
    return sorted(ws, key=ws.get)
