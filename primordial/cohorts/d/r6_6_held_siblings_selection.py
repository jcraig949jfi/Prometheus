"""D-R6-6 (ANOM-1789447409536-0 w1 train8, ANOM-1789447409538-0 w1 train128, ANOM-1789447409539-0 w34 train8): the last
three HELD siblings through D-R6-4's 0-QD search / selection / overfit reader (primordial.cohorts.d.r6_4_held_w13_train8_selection,
unchanged since c0ded560f).

These cells have no R16 gate row yet, so the gate is G's round 4 stage 1 suite_cheap row
(primordial/ledger/rows/G/G-R4-3-stage1.jsonl), whose gate_held64 equals worlds_r4 ee86620f4 and the anomaly text:
  w1  train8_held64    feat 1, thr 1, dir -1, act [0, 4, 7]; gate_train 236.25     held64 170.46875  abstain 88.28125
  w1  train128_held64  feat 1, thr 1, dir -1, act [0, 4, 7]; gate_train 271.796875 held64 170.46875  abstain 88.28125
  w34 train8_held64    feat 3, thr 3, dir -1, act [1];       gate_train 76.5       held64 289.328125 abstain 273.328125
Archives: G's saved round 4 M2 runs (v1 stream, rng_family None), every run seed the committed rows list; TRAIN = the
pressure's train seeds (TRAIN8 or TRAIN128).

Rule per cell (fixed before reading; n = runs found):
  I1  gate genome fused TRAIN == gate_train and HELD64 == gate_held64; floors.gate_scores agrees on both; zero genome HELD64
      == abstain; n >= 8; archive fitness == TRAIN recount x len(TRAIN) for every elite -- else INDETERMINATE.
  reach_r = top1_train TRAIN per seed >= gate_train; held_r = >= 1 archive elite with HELD64 per seed >= gate_held64.
  with k_hi = ceil(5n/8), k_lo = floor(3n/8): SEARCH_SHORT reach <= k_lo; SELECTION reach >= k_hi and held >= k_hi;
  OVERFIT_ONLY reach >= k_hi and held <= k_lo; MIXED otherwise. (n = 8 gives D-R6-4's 5 / 3.)
Controls per cell: planted_gate counted n/n, planted_abstain 0/n; else INDETERMINATE.
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import time

import numpy as np

from primordial.cohorts.d import r6_4_held_w13_train8_selection as R4
from primordial.metric import floors as F
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.qd.archive import load_elites

EXP = "D-R6-6-held-siblings-selection"
PREDICATE_ID = EXP
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
CELLS = [
    {"anomaly": "1789447409536-0", "gs": 1, "pressure": "train8_held64",
     "gate": {"feat": 1, "thr": 1, "dir": -1, "act": [0, 4, 7]}, "gate_train": 236.25, "gate_held": 170.46875,
     "abstain": 88.28125},
    {"anomaly": "1789447409538-0", "gs": 1, "pressure": "train128_held64",
     "gate": {"feat": 1, "thr": 1, "dir": -1, "act": [0, 4, 7]}, "gate_train": 271.796875, "gate_held": 170.46875,
     "abstain": 88.28125},
    {"anomaly": "1789447409539-0", "gs": 34, "pressure": "train8_held64",
     "gate": {"feat": 3, "thr": 3, "dir": -1, "act": [1]}, "gate_train": 76.5, "gate_held": 289.328125,
     "abstain": 273.328125},
]


def linear_runs(text: str, gs: int, pressure: str, glen: int) -> list[dict]:
    """The float linear M2 baseline runs only (family 'linear', genome_bytes == G7 glen), last row per run seed.
    D-R6-6 job 4fe3ba1d1c3b crashed because R4.runs_from_rows also indexes w1 train128's input-invariant learner
    archives (g-r4-inv, 384 B, no family) and keeps them as the last row per run seed."""
    out = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        x = json.loads(line)
        if (x.get("kind") == "run" and x.get("gen_seed") == gs and x.get("pressure") == pressure
                and x.get("rng_family") is None and x.get("family") == "linear"
                and int(x.get("genome_bytes") or -1) == glen):
            out[int(x["run_seed"])] = x
    return [out[k] for k in sorted(out)]


def decide_n(i1: bool, controls_ok: bool, reach: list[bool], held: list[bool]) -> str:
    n = len(reach)
    if not (i1 and controls_ok) or n < 8:
        return "INDETERMINATE"
    hi, lo = math.ceil(5 * n / 8), math.floor(3 * n / 8)
    r, h = sum(reach), sum(held)
    if r <= lo:
        return "SEARCH_SHORT"
    if r >= hi and h >= hi:
        return "SELECTION"
    if r >= hi and h <= lo:
        return "OVERFIT_ONLY"
    return "MIXED"


def read_cell(cell: dict, text: str) -> dict:
    gs, pressure = cell["gs"], cell["pressure"]
    train = F.PRESSURES[pressure]
    g7 = E7.G7(gs, "linear")
    runs = linear_runs(text, gs, pressure, g7.glen)
    graw = R4.gate_genome(g7, cell["gate"])
    zraw = np.zeros_like(graw)
    g_tr, g_hd = float(R4.per_seed(g7, graw, train)[0]), float(R4.per_seed(g7, graw, F.HELD64)[0])
    spec = E4.Spec(gs)
    gd = {k: np.asarray([v]) for k, v in cell["gate"].items() if k != "act"}
    gd["act"] = np.asarray([cell["gate"]["act"]])
    fs_tr, fs_hd = float(F.gate_scores(spec, gd, train)[0]), float(F.gate_scores(spec, gd, F.HELD64)[0])
    z_hd = float(R4.per_seed(g7, zraw, F.HELD64)[0])
    per = []
    for x in runs:
        doc = load_elites(x["elites"])
        if int(doc["glen"]) != g7.glen:
            per.append({"run_seed": int(x["run_seed"]), "glen_mismatch": int(doc["glen"]), "archive_fit_recount_ok": False,
                        "reach": False, "held": False, "planted_gate_counted": False, "planted_abstain_counted": False})
            continue
        per.append({"run_seed": int(x["run_seed"]),
                    "elites_sha256": hashlib.sha256(pathlib.Path(x["elites"]).read_bytes()).hexdigest(),
                    **R4.read_run(g7, doc, graw, zraw, cell["gate_train"], cell["gate_held"], train)})
    n = len(per)
    i1 = {"gate_genome_train": g_tr == cell["gate_train"], "gate_genome_held64": g_hd == cell["gate_held"],
          "floors_gate_scores_train": fs_tr == cell["gate_train"], "floors_gate_scores_held64": fs_hd == cell["gate_held"],
          "abstain_genome_held64": z_hd == cell["abstain"], "runs_ge_8": n >= 8,
          "archive_fit_recount_all": n > 0 and all(p["archive_fit_recount_ok"] for p in per)}
    controls = {"planted_gate": {"counted": sum(p["planted_gate_counted"] for p in per)},
                "planted_abstain": {"counted": sum(p["planted_abstain_counted"] for p in per)}}
    controls["planted_gate"]["ok"] = n > 0 and controls["planted_gate"]["counted"] == n
    controls["planted_abstain"]["ok"] = controls["planted_abstain"]["counted"] == 0
    ok = controls["planted_gate"]["ok"] and controls["planted_abstain"]["ok"]
    reach, held = [p["reach"] for p in per], [p["held"] for p in per]
    return {"anomaly": cell["anomaly"], "world": f"w{gs}", "pressure": pressure, "gate": cell["gate"],
            "gate_train": cell["gate_train"], "gate_held64": cell["gate_held"], "genome_bytes": int(g7.glen),
            "runs_total": n, "rng_family_count": 1, "runs_per_family": n,
            "measured": {"gate_genome_train": g_tr, "gate_genome_held64": g_hd, "floors_train": fs_tr,
                         "floors_held64": fs_hd, "abstain_genome_held64": z_hd},
            "checks": {"I1": i1, "controls_ok": bool(ok)}, "controls": controls, "per_run": per,
            "reach_k": sum(reach), "held_k": sum(held), "decision": decide_n(all(i1.values()), ok, reach, held)}


def job(ctx, status="record", exp=EXP, predicate_id=PREDICATE_ID):
    """exp / predicate_id: D-R6-6b re-runs this reader after the index fix under its own predicate and rows file."""
    t0 = time.perf_counter()
    text = (R4.ROOT / R4.SRC_ROWS).read_text(encoding="utf-8")
    cells = [read_cell(c, text) for c in CELLS]
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "status": status, "ts": round(time.time(), 3),
              "qd_runs": 0, "source_rows": R4.SRC_ROWS, "gate_source": "primordial/ledger/rows/G/G-R4-3-stage1.jsonl suite_cheap",
              "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "cells": cells,
              "decisions": {f"{c['world']} {c['pressure']}": c["decision"] for c in cells},
              "wall_s": round(time.perf_counter() - t0, 3)})
