"""D-R4-4 (ANOM-1789448979514-0): how much of the round 4 screen is the M2 READOUT, not the search?

D-R4-1: the top-16-by-TRAIN mean HELD64 is below abstain in 66/74 cells while the archive holds an elite at
exactly abstain in 309/592 archives. Discriminator (no new QD run): re-read G's 592 saved M2 archives under
other readouts and recompute every screen verdict from the committed floors (worlds_r4.json), rows only.

Readouts per archive (all elites scored on HELD64; VAL64 = seeds 20000..20063, disjoint from TRAIN 9100..9227
and HELD64 30000..30063):
  m2         top-16 by (-TRAIN fit, genome) -> mean HELD64 (G's M2; must reproduce the committed values)
  top1       top-1 by (-TRAIN fit, genome)
  val16      top-16 by (-VAL64, genome)      -> mean HELD64
  val1       top-1 by (-VAL64, genome)
  leak16/1   selected on HELD64 itself (CONTROL: the test-set leak; must be >= its honest counterparts)
Per cell and readout: median over run seeds, M3 median_ci, and all four variant verdicts, with worlds.cell's
PENDING rule for bound floors (screen.needs_learner). Nothing is written to worlds_r4.json.

    python -m primordial.fabric.worker submit D primordial.cohorts.d.r4_4_readouts:job \\
        --exp D-R4-4-readouts --rows primordial/ledger/rows/D/D-R4-4-readouts.jsonl --ttl-cpu-s 1500
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from primordial.metric import floors as F
from primordial.metric import screen as SC
from primordial.metric.ci import median_ci
from primordial.qd import e7_run as E7
from primordial.qd.archive import load_elites
from primordial.soup.b6.fused import FusedRollout

EXP = "D-R4-4-readouts"
ROOT = pathlib.Path(__file__).resolve().parents[3]
WORLDS = ROOT / "primordial" / "ledger" / "qd" / "worlds_r4.json"
VAL64 = np.arange(20000, 20064, dtype=np.int64)
TOP = 16
HONEST = ("m2", "top1", "val16", "val1")
READOUTS = HONEST + ("leak16", "leak1")
EPS = 1e-9


def scores(g7, raw: np.ndarray, seeds) -> np.ndarray:
    return FusedRollout(g7.spec, len(raw), np.asarray(seeds), family="linear").run(g7.unpack(raw))[0] / len(seeds)


def readouts(g7, doc: dict) -> dict:
    el = [(int(f), bytes.fromhex(g)) for _, f, g, *_ in doc["elites"]]
    raw = np.frombuffer(b"".join(g for _, g in el), np.uint8).reshape(-1, doc["glen"])
    held, val = scores(g7, raw, F.HELD64), scores(g7, raw, VAL64)
    by = lambda key: sorted(range(len(el)), key=lambda i: (key(i), el[i][1]))
    tr, va, he = by(lambda i: -el[i][0]), by(lambda i: -val[i]), by(lambda i: -held[i])
    mean = lambda idx: float(held[idx].mean())
    return {"m2": mean(tr[:TOP]), "top1": float(held[tr[0]]), "val16": mean(va[:TOP]), "val1": float(held[va[0]]),
            "leak16": mean(he[:TOP]), "leak1": float(held[he[0]]), "n_elites": len(el)}


def verdicts(cell: dict, lo: float) -> dict:
    """worlds.cell's verdict block from the committed floor, gate and bound flag, at baseline ci95 low `lo`."""
    f, gate = float(cell["floor"]), float(cell["gate_held64"])
    vf = {SC.vkey(*v): SC.variant_floor(f, gate, v[0]) for v in SC.VARIANTS}
    if cell["floor_is_bound"] and SC.needs_learner(f, gate, lo):
        if lo > f:
            return {k: {"verdict": "PENDING", "cull_reason": None, "floor": vf[k]} for k in vf}
        return {SC.vkey(*v): ({"verdict": "PENDING", "cull_reason": None, "floor": vf[SC.vkey(*v)]} if v[1] == "HOLD"
                              else {"verdict": "CULLED", "cull_reason": "PENDING", "floor": vf[SC.vkey(*v)]})
                for v in SC.VARIANTS}
    return SC.verdicts(f, gate, lo)


def job(ctx, dev=False, only=None):
    cells = json.loads(WORLDS.read_text(encoding="utf-8"))["cells"]
    keep = None if only is None else {(w, p) for w, p in only}
    status = "dev" if dev else "record"
    st = ctx.load_checkpoint() or {"cells": {}}
    for cell in cells:
        key = f"{cell['world']}|{cell['pressure']}"
        if (keep is not None and (cell["world"], cell["pressure"]) not in keep) or key in st["cells"]:
            continue
        if ctx.should_pause():
            ctx.pause(st)
        g7 = E7.G7(int(cell["gen_seed"]), "linear")
        per = {}
        for rs in sorted(int(x) for x in cell["baseline"]["elites"]):
            r = readouts(g7, load_elites(cell["baseline"]["elites"][str(rs)]))
            want = float(cell["baseline"]["held64_by_run_seed"][str(rs)])
            r.update(reproduces_m2=abs(r["m2"] - want) < EPS,
                     leak_ge_honest=bool(r["leak16"] >= max(r["m2"], r["val16"]) - EPS
                                         and r["leak1"] >= max(r["top1"], r["val1"]) - EPS))
            ctx.emit({"kind": "archive", "world": cell["world"], "pressure": cell["pressure"], "run_seed": rs,
                      "status": status, **r})
            per[rs] = r
        out = {"kind": "cell", "world": cell["world"], "gen_seed": cell["gen_seed"], "pressure": cell["pressure"],
               "verdict_r4": cell["verdict"], "floor": cell["floor"], "gate_held64": cell["gate_held64"],
               "floor_is_bound": cell["floor_is_bound"], "committed_verdicts": cell["verdicts"], "readouts": {}}
        for name in READOUTS:
            v = [per[rs][name] for rs in sorted(per)]
            lo, hi = median_ci(v)
            out["readouts"][name] = {"median": float(np.median(v)), "ci95": [lo, hi], "verdicts": verdicts(cell, lo)}
        out["m2_verdicts_reproduce"] = all(out["readouts"]["m2"]["verdicts"][k]["verdict"] == cell["verdicts"][k]["verdict"]
                                           for k in cell["verdicts"])
        out["n_reproduces_m2"] = sum(r["reproduces_m2"] for r in per.values())
        out["n_leak_ge_honest"] = sum(r["leak_ge_honest"] for r in per.values())
        ctx.emit({**out, "status": status})
        st["cells"][key] = out
        ctx.checkpoint(st)
    if keep is None or len(st["cells"]) == len(keep):
        ctx.emit({**verdict(list(st["cells"].values())), "status": status})


def verdict(cs: list[dict]) -> dict:
    """Pre-registered checks (bus predicate D-R4-4)."""
    act = SC.vkey(*SC.ACTIVE)
    vv = lambda c, name, k: c["readouts"][name]["verdicts"][k]["verdict"]
    flips = {name: {SC.vkey(*v): [[c["world"], c["pressure"], vv(c, "m2", SC.vkey(*v)), vv(c, name, SC.vkey(*v))]
                                  for c in cs if vv(c, name, SC.vkey(*v)) != vv(c, "m2", SC.vkey(*v))]
                    for v in SC.VARIANTS} for name in READOUTS if name != "m2"}
    surv = {name: sorted(f"{c['world']}|{c['pressure']}" for c in cs if vv(c, name, act) == "SURVIVED") for name in READOUTS}
    to_surv_fp = lambda name: sum(1 for w, p, a, b in flips[name]["four_policy|HOLD"] if b == "SURVIVED" and a != "SURVIVED")
    w13 = next((c for c in cs if c["world"] == "w13" and c["pressure"] == "train128_held64"), None)
    return {"kind": "summary", "exp": EXP, "n_cells": len(cs),
            "survived_active": surv, "flips": flips,
            "n_flips": {name: {k: len(v) for k, v in fl.items()} for name, fl in flips.items()},
            "median_by_readout": {f"{c['world']}|{c['pressure']}": {n: round(c["readouts"][n]["median"], 3) for n in READOUTS}
                                  for c in cs},
            "checks": {
                "I_m2_reproduces_all": all(c["n_reproduces_m2"] == 8 for c in cs),
                "I_m2_verdicts_reproduce_all": all(c["m2_verdicts_reproduce"] for c in cs),
                "C_leak_ge_honest_all": all(c["n_leak_ge_honest"] == 8 for c in cs),
                "P1_active_survived_set_changes_under_some_honest_readout": any(surv[n] != surv["m2"] for n in HONEST[1:]),
                "P2_four_policy_hold_ge5_to_survived_under_top1_or_val16": max(to_surv_fp("top1"), to_surv_fp("val16")) >= 5,
                "P3_val16_median_ge_m2_in_ge60_cells": sum(c["readouts"]["val16"]["median"] >= c["readouts"]["m2"]["median"] - EPS
                                                           for c in cs) >= 60,
                "P4_w13_train128_survives_all_honest": w13 is not None and all(vv(w13, n, act) == "SURVIVED" for n in HONEST)}}
