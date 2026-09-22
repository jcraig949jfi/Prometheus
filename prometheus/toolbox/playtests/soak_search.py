"""Soak (overnight C102): search above the kernel for many generations under one process, looking for the slow
defects a short test cannot see -- memory growth per generation, wall drift, receipts files that stop scanning
clean, archive markers out of order, elites that stop changing. Writes its result file from Python (never a
shell redirect). Usage: python -m prometheus.toolbox.playtests.soak_search [minutes] [out.json]"""
from __future__ import annotations

import gc
import json
import pathlib
import shutil
import sys
import time
import tracemalloc
from datetime import datetime, timezone

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox import search as SR
from prometheus.toolbox.receipt import scan
from prometheus.toolbox.ref.players import random_statemachine_v2


def template() -> Experiment:
    return Experiment(family="soak_search", world=ref("world.integer.v1", world_seed=41, n_regs=6, start_charge=40, yield_amt=10, regime_period=6, stoch_rate=5),
                      substrate=ref("substrate.kv.v1", scope="lifetime", ttl=6), players=[random_statemachine_v2(1).manifest()],
                      objective=ref("objective.multi.v1", components={"net": ref("objective.yield_net.v1", penalties={"ws_writes": 0.02}), "life": ref("objective.survival.v2")}),
                      observers=[ref("observer.descriptor.v1", action_scale=2, yield_scale=40), ref("observer.series.v1")],
                      controls=[ref("control.replay.v1")], seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 2, "horizon": 32, "batch": 4})


def main(minutes: str = "15", out: str = "roles/Bellerophon/science/SOAK_SEARCH_2026-09-19.json", selector: str = "selector.map_elites.v1", compact: str = "0") -> dict:
    from prometheus.toolbox.registry import default_registry
    reg = default_registry().fork()
    wd = pathlib.Path("prometheus/toolbox/playtests/receipts/soak"); shutil.rmtree(wd, ignore_errors=True); wd.mkdir(parents=True)
    budget_s = float(minutes) * 60; t_start = time.perf_counter(); started = datetime.now(timezone.utc).isoformat()
    tracemalloc.start(); gens = []; gen = 0
    sel = ref(selector, n=8, representation="statemachine.v2", rank="net") if selector != "selector.pareto.v1" else ref(selector, n=8, representation="statemachine.v2")
    compact = compact not in ("0", "", "false", "False")
    stop = None
    while time.perf_counter() - t_start < budget_s:
        t0 = time.perf_counter()
        res = SR.evolve(template(), sel, generations=gen + 1, workdir=wd, seed=77, registry=reg, compact=compact)      # one more generation, RESUMING from the rows
        dt = time.perf_counter() - t0
        if res["generations_done"] != gen + 1:
            stop = {"gen": gen, "res": res}; break
        rows = SR.load_rows(wd / "archive.jsonl"); committed = SR.committed_rows(rows)
        cells = SR.elites_by_cell(committed, rank="net"); front = len(SR.pareto_front(committed))
        files = sorted(wd.glob("gen_*_a*.jsonl")); last = scan(files[-1])
        cur, peak = tracemalloc.get_traced_memory(); gc.collect()
        gens.append({"gen": gen, "wall_s": round(dt, 3), "rows": len(rows), "committed": len(committed), "cells": len(cells), "front": front,
                     "best_net": max((r["objective"]["net"] for r in committed if r["objective"]), default=None),
                     "last_file_clean": last["ok"] if isinstance(last, dict) and "ok" in last else last.get("valid", None) if isinstance(last, dict) else None,
                     "last_file_defects": (last.get("defects") if isinstance(last, dict) else None), "traced_kb": cur // 1024, "peak_kb": peak // 1024,
                     "markers_in_order": [r["gen"] for r in rows if r["kind"] == "GEN_DONE"] == list(range(gen + 1))})
        gen += 1
    result = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "minutes_budget": float(minutes), "generations": gen, "selector": selector, "compact": compact,
              "stopped": stop, "per_gen": gens,
              "memory_growth_kb_per_gen": round((gens[-1]["traced_kb"] - gens[len(gens) // 2]["traced_kb"]) / max(1, len(gens) - len(gens) // 2), 1) if len(gens) > 3 else None,
              "wall_drift": {"first3_mean_s": round(sum(g["wall_s"] for g in gens[:3]) / 3, 3), "last3_mean_s": round(sum(g["wall_s"] for g in gens[-3:]) / 3, 3)} if len(gens) >= 6 else None,
              "all_files_clean": all(g["last_file_defects"] in (None, [], {}) for g in gens), "all_markers_in_order": all(g["markers_in_order"] for g in gens)}
    pathlib.Path(out).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "per_gen"}, indent=1))
    return result


if __name__ == "__main__":
    main(*sys.argv[1:])
