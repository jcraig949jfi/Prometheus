"""G-R4-3 stage 2 driver (round 4 P0, builder G): baselines in gate-headroom order, until 8 survivors.

Reads the stage 1 floor_suite rows (committed; never recomputed). For each world x pressure in
screen.order_key order (gate_held64 - floor descending, then gen_seed, then pressure):
  1. the M2 float linear baseline (primordial.metric.baseline, >= 8 run seeds) -> baseline row
  2. the record (primordial.metric.worlds.cell). A train128 bound that could flip a verdict is PENDING;
     the train128 learner runs only for gen_seeds in `learner_train128` (the conductor clears them,
     A 1789433825087-0), otherwise the cell stays PENDING and is reported.
  3. one stage2_cell row: all four variant verdicts, the active one, pending or not.
It stops once the active variant (screen.ACTIVE, gate_in|HOLD) has max_survivors EXACT survivors; a
PENDING cell never counts. Cells after the stop are NOT_REACHED when worlds_r4.json is built.

    python -m primordial.fabric.worker submit G primordial.metric.stage2:job --exp G-R4-3-stage2 \\
        --rows primordial/ledger/rows/G/G-R4-3-stage2.jsonl --ttl-cpu-s S \\
        --kwargs '{"stage1_rows": "primordial/ledger/rows/G/G-R4-3-stage1.jsonl", "learner_train128": [1, 3, 4]}'
"""
from __future__ import annotations

import json
import pathlib

from primordial.metric import baseline as B
from primordial.metric import invariant as I
from primordial.metric import screen as SC
from primordial.metric import worlds as WR

EXP = "G-R4-3-stage2"
ROOT = pathlib.Path(__file__).resolve().parents[2]


def load_suite(path) -> dict:
    """{(gen_seed, pressure): the last floor_suite row} from a stage 1 rows file."""
    p = pathlib.Path(path)
    p = p if p.is_absolute() else ROOT / p
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            x = json.loads(line)
            if x.get("kind") == "floor_suite":
                out[(int(x["gen_seed"]), x["pressure"])] = x
    return out


def order(suite: dict) -> list[tuple]:
    return sorted(suite, key=lambda k: SC.order_key(suite[k]))


def is_pending(rec: dict) -> bool:
    return any(v["verdict"] == WR.PENDING for v in rec["verdicts"].values())


def job(ctx, stage1_rows, learner_train128=(), max_survivors=SC.MAX_SURVIVORS, run_seeds=tuple(range(B.MIN_RUNS)),
        gens=None, batch=None, learner_gens=None, learner_batch=None, archive_url=B.ARCHIVE_URL,
        elites_dir=str(B.ELITES_DIR), learner_elites_dir=str(I.ELITES_DIR), only=None):
    import redis
    r = redis.Redis.from_url(archive_url)
    st = ctx.load_checkpoint() or {"done": {}, "cur": None, "base": {}, "learn": {}, "cells": {}, "stopped": False}
    suite = load_suite(stage1_rows)
    keep = None if only is None else {(int(g), p) for g, p in only}
    active = SC.vkey(*SC.ACTIVE)
    allowed = {int(g) for g in learner_train128}
    survivors = sum(1 for c in st["cells"].values() if c["active"] == "SURVIVED" and not c["pending"])
    for gs, p in order(suite):
        if keep is not None and (gs, p) not in keep:
            continue
        key = f"{gs}|{p}"
        if key in st["cells"]:
            continue
        if survivors >= max_survivors:
            if not st["stopped"]:
                ctx.emit({"kind": "stage2_stop", "survivors": survivors, "variant": active, "next_cell": [gs, p],
                          "status": "control"})
                st["stopped"] = True
            break
        if key not in st["base"]:
            runs = B.baseline_cell(ctx, st, r, gs, p, run_seeds, gens, batch, elites_dir)
            st["base"][key] = B.summary(runs)
            ctx.emit({**st["base"][key], "status": "control"})
        rec = WR.cell(suite[(gs, p)], st["base"][key], st["learn"].get(key))
        if is_pending(rec) and p == "train128_held64" and gs in allowed:
            if key not in st["learn"]:
                runs = I.learner_cell(ctx, st, r, gs, p, run_seeds, learner_gens, learner_batch, learner_elites_dir)
                st["learn"][key] = I.summary(runs)
                ctx.emit({**st["learn"][key], "status": "control"})
            rec = WR.cell(suite[(gs, p)], st["base"][key], st["learn"][key])
        pend = is_pending(rec)
        v = rec["verdicts"][active]["verdict"]
        ctx.emit({"kind": "stage2_cell", "world": rec["world"], "gen_seed": gs, "pressure": p,
                  "floor": rec["floor"], "floor_is_bound": rec["floor_is_bound"], "gate_held64": rec["gate_held64"],
                  "baseline_median": rec["baseline"]["median"], "baseline_ci95": rec["baseline"]["ci95"],
                  "baseline_bytes": rec["baseline"]["bytes"], "verdicts": rec["verdicts"], "active": v,
                  "pending": pend, "status": "control"})
        st["cells"][key] = {"active": v, "pending": pend}
        if v == "SURVIVED" and not pend:
            survivors += 1
        if hasattr(ctx, "checkpoint"):
            ctx.checkpoint(st)
