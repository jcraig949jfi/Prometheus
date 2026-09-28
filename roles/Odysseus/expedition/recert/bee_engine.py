"""BEE (prometheus/z80atlas) adapter for the recertification harness: run configurations recovered from the frozen
run plans, and one execution exactly as World._execute performs it (SHARED / SEPARATED layout, the run's chemistry,
fresh registers -- BEE carries no register state between executions).

Run configurations are REBUILT from the preregistered plans (grounding.plan / coupling_campaign.plan with their frozen
inputs files); the plan ids and seeds are checked against the committed result rows before use.
"""
from __future__ import annotations

import gzip
import json
import os
import sys

sys.dont_write_bytecode = True
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from prometheus.z80atlas import vm  # noqa: E402
from prometheus.z80atlas import grammar as G  # noqa: E402

GROUNDING_RAW = "roles/Bellerophon/forensics_2026-09-23/receipts/GROUNDING_RESULTS_RAW.jsonl.gz"
GROUNDING_INPUTS = "roles/Bellerophon/forensics_2026-09-23/receipts/grounding_inputs.json"
COUPLING_LEDGER = "roles/Bellerophon/coupling_2026-09-24/COUPLING_ORIGIN_LEDGER.jsonl"
COUPLING_INPUTS = "roles/Bellerophon/coupling_2026-09-24/receipts/coupling_inputs.json"


def _p(rel):
    return os.path.join(REPO, rel)


def config_of(p: dict, ticks: int, cells: int, budget: int):
    cfg = G.to_config(p["vec"], ticks, cells, budget, tuple(p.get("init_tapes") or ()))
    for k, v in (p.get("config_overrides") or {}).items():
        if k == "yoke":
            v = tuple(v)
        setattr(cfg, k, v)
    return cfg


def sig(cfg) -> dict:
    """The execution-relevant part of a run configuration (what a single execution depends on)."""
    return {"L": cfg.L, "allow_copyall": cfg.allow_copyall, "layout": cfg.layout, "ldir": cfg.ldir,
            "undefined": cfg.undefined_op, "strict": cfg.physics != "v1", "budget": cfg.budget,
            "representation": cfg.representation, "reproduction": cfg.reproduction, "read_gate": cfg.read_gate}


def grounding_runs():
    """[(result_row, cfg)] for all 12,130 grounding runs; plan ids/seeds/cells verified against the result rows."""
    from prometheus.z80atlas import grounding as GR
    P = {p["id"]: p for p in GR.plan(json.load(open(_p(GROUNDING_INPUTS))))}
    out = []
    for line in gzip.open(_p(GROUNDING_RAW)):
        r = json.loads(line)
        p = P[r["id"]]
        assert p["seed"] == r["seed"] and p["cell"] == r["cell"] and p["lane"] == r["lane"], r["id"]
        out.append((r, config_of(p, GR.TICKS, GR.CELLS, GR.BUDGET)))
    return out


def coupling_runs():
    """[(ledger_row, cfg, plan_row)] for the 68 coupling-campaign origin-ledger tapes (S1's set)."""
    from prometheus.z80atlas import coupling_campaign as CC
    P = {p["id"]: p for p in CC.plan(json.load(open(_p(COUPLING_INPUTS))))}
    out = []
    for line in open(_p(COUPLING_LEDGER)):
        r = json.loads(line)
        p = P[r["run"]]
        assert p["arm"] == r["arm"] and p["K"] == r["K"] and p["lane"] == r["lane"], r["run"]
        out.append((r, config_of(p, CC.TICKS, CC.CELLS, CC.BUDGET), p))
    return out


def execute(tape: bytes, s: dict, x, window: bytes, trace_pcs: bool = True):
    """One execution as World._execute: tape at [0,L), window at [L,2L), inputs at IN_BASE. Returns (mem, trace)."""
    L = s["L"]
    xs = list(x) if isinstance(x, (list, tuple)) else [x]
    mem = bytearray(256)
    mem[:L] = tape[:L]
    mem[L:2 * L] = window[:L]
    for k, v in enumerate(xs[:16]):
        mem[vm.IN_BASE + k] = v
    kw = dict(allow_copyall=s["allow_copyall"], strict_budget=s["strict"], ldir=s["ldir"], undefined=s["undefined"],
              trace_pcs=trace_pcs)
    if s["layout"] == "SEPARATED":
        t1 = vm.execute(mem, L, 0, s["budget"] // 2, xs, region=(0, L // 2), **kw)
        t2 = vm.execute(mem, L, L // 2, s["budget"] // 2, xs, region=(L // 2, L), **kw)
        t1.win_prov.update(t2.win_prov)
        t1.writes.update(t2.writes)
        if t1.pcs is not None and t2.pcs is not None:
            t1.pcs |= t2.pcs
        fi1, fo1 = t1.first_in_step, t1.first_out_step
        t1.first_in_step = fi1 if fi1 is not None else (None if t2.first_in_step is None else t2.first_in_step + t1.steps)
        t1.first_out_step = fo1 if fo1 is not None else (None if t2.first_out_step is None else t2.first_out_step + t1.steps)
        t1.outputs = t1.outputs + t2.outputs
        t1.steps += t2.steps
        return mem, t1
    return mem, vm.execute(mem, L, 0, s["budget"], xs, **kw)


def copy_ops(s: dict):
    return (vm.LDI, vm.LDIR, vm.COPYALL) if s["allow_copyall"] else (vm.LDI, vm.LDIR)
