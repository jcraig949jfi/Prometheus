"""Run ONE experiment (a worker entry point): build the World from the frozen spec, run it, measure the response
geometry of its top specimens, and leave a complete run directory the observatory and Atlas can re-analyse:

  config.json      the frozen configuration (factor vector, seed, budgets, parents, scheduler reason, stage)
  summary.json     metrics + first-crossing / first-replication genealogy + triggers
  ticks.jsonl      per-tick telemetry
  events.jsonl     copy / migration / env-change / extinction events (capped)
  snapshots.jsonl  population snapshots (periodic + serendipity + final): unique tapes with counts, env, variation
  specimens.json   serendipity-archived organisms (with disassembly)
  exploits.json    anti-cheat records (frozen specimens)
  geometry.json    mutational-topology scans + damage cliffs of the top specimens
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time
from typing import Dict

from prometheus.z80atlas import grammar as G
from prometheus.z80atlas import geometry
from prometheus.z80atlas.world import World, ENDOGENOUS
from prometheus.z80atlas.observatory import write_json, write_jsonl
from prometheus.z80atlas.tasks import Task


def run_spec(spec: Dict) -> Dict:
    """spec: {id, family, vec, seed, ticks, cells, budget, parents, reason, stage, workdir, init_tapes?, geometry?}"""
    t0 = time.time()
    vec = spec["vec"]
    cfg = G.to_config(vec, spec["ticks"], spec["cells"], spec.get("budget", 256), tuple(spec.get("init_tapes") or ()))
    w = World(cfg, spec["seed"])
    summary = w.run()
    # the endogenous guard: the population manager never reproduced under an endogenous treatment
    assert not (vec["reproduction"] in ENDOGENOUS and summary["external_births"] > 0), "external reproduction leaked into an ENDOGENOUS treatment"
    rd = pathlib.Path(spec["workdir"]) / spec["id"]
    rd.mkdir(parents=True, exist_ok=True)
    frozen = {"id": spec["id"], "family": spec["family"], "vec": vec, "seed": spec["seed"], "ticks": spec["ticks"], "cells": spec["cells"],
              "budget": spec.get("budget", 256), "parents": spec.get("parents", []), "reason": spec.get("reason"), "stage": spec.get("stage"),
              "init_tapes": list(spec.get("init_tapes") or []), "config": cfg.to_dict()}
    frozen["config_sha256"] = hashlib.sha256(json.dumps({k: v for k, v in frozen.items() if k != "config_sha256"}, sort_keys=True, default=str).encode()).hexdigest()
    write_json(rd / "config.json", frozen)
    n_t = len(w.ticks_log)                                                        # adaptive interval: every 4th tick + the last 20, every tick
    write_jsonl(rd / "ticks.jsonl", [t for i, t in enumerate(w.ticks_log) if i % 4 == 0 or i >= n_t - 20])
    write_jsonl(rd / "events.jsonl", w.events[:400] + [e for e in w.events[400:] if e["kind"] != "copy"][:200])
    write_jsonl(rd / "snapshots.jsonl", w.snapshots)
    write_json(rd / "specimens.json", w.specimens)
    write_json(rd / "exploits.json", w.exploits)
    # response geometry of the top specimens (bounded)
    geo = {}
    if spec.get("geometry", True) and summary.get("top"):
        task = w.env.task_for(0)
        scans = []
        for k, o in enumerate(summary["top"][:2]):
            tape = bytes.fromhex(o["tape"])
            sc = geometry.scan(tape, cfg, task, spec["seed"] * 31 + k, n=40)
            sc["damage"] = geometry.damage_cliff(tape, cfg, task, spec["seed"] * 37 + k, trials=8)
            sc["id"] = o["id"]; scans.append(sc)
        geo["top"] = scans
        # gain in beneficial density relative to a gen-0 random tape of the same length (the "did reproductive
        # machinery raise the density of future beneficial mutations" ruler)
        import random as _r
        rt = bytes(_r.Random(spec["seed"]).randrange(256) for _ in range(cfg.L))
        base = geometry.scan(rt, cfg, task, spec["seed"] * 41, n=40)
        geo["random_baseline"] = base
        geo["beneficial_density_gain"] = None
        if w.first_replication:
            fr_tape = bytes.fromhex(w.first_replication["tape"])
            geo["first_replicator"] = geometry.scan(fr_tape, cfg, task, spec["seed"] * 43, n=40)
            # did the lineage's reproductive machinery RAISE the density of beneficial neighbours since its first replicator?
            if scans and scans[0]["base_replicates"] and geo["first_replicator"]["base_replicates"]:
                geo["beneficial_density_gain"] = round(scans[0]["beneficial_density"] - geo["first_replicator"]["beneficial_density"], 3)
        # v2 (forensics 2026-09-23, C6/M9): PAIRED scans on the CONFIGURED task, top specimen vs the first
        # SELF_REPLICATION writer (not the first copy event); the v1 fields above are kept for replay only
        if spec.get("geometry_v2", True):
            ctask = w.configured_task()
            g2 = {"task": ctask.to_dict(), "top": geometry.scan_paired(bytes.fromhex(summary["top"][0]["tape"]), cfg, ctask, spec["seed"] * 53)}
            fsr = summary.get("first_self_replication")
            if fsr:
                g2["first_self_replicator"] = geometry.scan_paired(bytes.fromhex(fsr["tape"]), cfg, ctask, spec["seed"] * 53)   # same panel
                g2["beneficial_density_gain_paired"] = round(g2["top"]["beneficial_density"] - g2["first_self_replicator"]["beneficial_density"], 4)
            geo["v2"] = g2
        write_json(rd / "geometry.json", geo)
    summary["geometry"] = {"beneficial_density_gain": geo.get("beneficial_density_gain"),
                           "top_beneficial_density": (geo.get("top") or [{}])[0].get("beneficial_density"),
                           "top_moat_density": (geo.get("top") or [{}])[0].get("moat_density"),
                           "top_damage_k4_replicates": ((geo.get("top") or [{}])[0].get("damage") or {}).get("cliff", {}).get("k4", {}).get("replicates"),
                           "v2_top_beneficial_density_paired": ((geo.get("v2") or {}).get("top") or {}).get("beneficial_density"),
                           "v2_beneficial_density_gain_paired": (geo.get("v2") or {}).get("beneficial_density_gain_paired")}
    summary["wall_s"] = round(time.time() - t0, 2)
    summary["config_sha256"] = frozen["config_sha256"]
    write_json(rd / "summary.json", summary)
    return {"id": spec["id"], "family": spec["family"], "vec": vec, "seed": spec["seed"], "stage": spec.get("stage"), "reason": spec.get("reason"),
            "parents": spec.get("parents", []), "summary": summary, "dir": str(rd)}
