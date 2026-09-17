"""D-R6-5 (ANOM-1789447409534-0): HELD w7 train8_held64 -- the same 0-QD search / selection / overfit reader as D-R6-4
(primordial.cohorts.d.r6_4_held_w13_train8_selection), on w7.

Cell: w7 train8_held64, float linear (E7.G7(7, "linear")), G's 8 saved round 4 M2 archives (200 x 128 on TRAIN8, run
seeds 0..7, v1 stream = family 4200).
Gate (G-R16-floors r16_det, w7 train8_held64): feat 3, thr 2, dir -1, act [7, 7, 7] (W 3); gate_train 1910.875,
gate_held64 1482.5. Abstain floor part 189.1875 (worlds_r4 ee86620f4 floor_parts, anomaly text).

Rule: identical to D-R6-4 with these values -- I1 (gate genome == floor rows on TRAIN8 and HELD64, floors.gate_scores
agrees, zero genome HELD64 == 189.1875, 8 runs, archive fitness recount 8/8); reach_r = top1 TRAIN8 per seed >= 1910.875;
held_r = >= 1 archive elite with HELD64 per seed >= 1482.5; SEARCH_SHORT reach <= 3/8; SELECTION reach >= 5/8 and held
>= 5/8; OVERFIT_ONLY reach >= 5/8 and held <= 3/8; MIXED otherwise. Controls planted_gate 8/8, planted_abstain 0/8.
"""
from __future__ import annotations

import hashlib
import pathlib
import time

import numpy as np

from primordial.cohorts.d import r6_4_held_w13_train8_selection as R4
from primordial.metric import floors as F
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.qd.archive import load_elites

EXP = "D-R6-5-held-w7-train8-selection"
PREDICATE_ID = EXP
ANOMALY = "1789447409534-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
GS, PRESSURE = 7, "train8_held64"
GATE = {"feat": 3, "thr": 2, "dir": -1, "act": [7, 7, 7]}
GATE_TRAIN, GATE_HELD = 1910.875, 1482.5
ABSTAIN_HELD = 189.1875


def job(ctx, status="record"):
    t0 = time.perf_counter()
    g7 = E7.G7(GS, "linear")
    text = (R4.ROOT / R4.SRC_ROWS).read_text(encoding="utf-8")
    runs = R4.runs_from_rows(text, GS, PRESSURE)
    graw = R4.gate_genome(g7, GATE)
    zraw = np.zeros_like(graw)
    g_tr, g_hd = float(R4.per_seed(g7, graw, F.TRAIN8)[0]), float(R4.per_seed(g7, graw, F.HELD64)[0])
    spec = E4.Spec(GS)
    gd = {k: np.asarray([v]) for k, v in GATE.items() if k != "act"}
    gd["act"] = np.asarray([GATE["act"]])
    fs_tr, fs_hd = float(F.gate_scores(spec, gd, F.TRAIN8)[0]), float(F.gate_scores(spec, gd, F.HELD64)[0])
    z_hd = float(R4.per_seed(g7, zraw, F.HELD64)[0])
    per = []
    for x in runs:
        doc = load_elites(x["elites"])
        per.append({"run_seed": int(x["run_seed"]), "elites": x["elites"],
                    "elites_sha256": hashlib.sha256(pathlib.Path(x["elites"]).read_bytes()).hexdigest(),
                    **R4.read_run(g7, doc, graw, zraw, GATE_TRAIN, GATE_HELD)})
    i1 = {"gate_genome_train8": g_tr == GATE_TRAIN, "gate_genome_held64": g_hd == GATE_HELD,
          "floors_gate_scores_train8": fs_tr == GATE_TRAIN, "floors_gate_scores_held64": fs_hd == GATE_HELD,
          "abstain_genome_held64": z_hd == ABSTAIN_HELD, "runs": len(per) == 8,
          "archive_fit_recount_8of8": all(p["archive_fit_recount_ok"] for p in per)}
    controls = {"planted_gate": {"counted": sum(p["planted_gate_counted"] for p in per)},
                "planted_abstain": {"counted": sum(p["planted_abstain_counted"] for p in per)}}
    controls["planted_gate"]["ok"] = controls["planted_gate"]["counted"] == len(per)
    controls["planted_abstain"]["ok"] = controls["planted_abstain"]["counted"] == 0
    ok = controls["planted_gate"]["ok"] and controls["planted_abstain"]["ok"]
    decision = R4.decide(all(i1.values()), ok, [p["reach"] for p in per], [p["held"] for p in per])
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "world": f"w{GS}", "pressure": PRESSURE, "representation": "float linear",
              "genome_bytes": int(g7.glen), "qd_runs": 0, "source_rows": R4.SRC_ROWS,
              "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "runs_total": len(per), "rng_family_count": 1, "runs_per_family": len(per),
              "gate": GATE, "gate_train": GATE_TRAIN, "gate_held64": GATE_HELD,
              "measured": {"gate_genome_train8": g_tr, "gate_genome_held64": g_hd, "floors_train8": fs_tr,
                           "floors_held64": fs_hd, "abstain_genome_held64": z_hd},
              "checks": {"I1": i1, "controls_ok": bool(ok)}, "controls": controls, "per_run": per,
              "reach_k_of_8": sum(p["reach"] for p in per), "held_k_of_8": sum(p["held"] for p in per),
              "decision": decision, "wall_s": round(time.perf_counter() - t0, 3)})
