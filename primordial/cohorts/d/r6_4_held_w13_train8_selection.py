"""D-R6-4 (ANOM-1789447409541-0): HELD w13 train8_held64 -- the 2-action gate beats the floor, the float linear baseline
search does not. Is that SEARCH (the search never reaches the gate's train score) or SELECTION (it passes the gate on
TRAIN8 but the train-selected elite generalises worse, while gate-quality policies sit unselected in the archive)?

Zero QD: G's 8 saved round 4 M2 archives (w13 train8_held64, float linear 200 B, 200 x 128 on TRAIN8, run seeds 0..7,
v1 stream = family 4200) re-read. Every elite is scored on TRAIN8 and HELD64 with the fused rollout; the archive's own
fitness is checked against the TRAIN8 recount. The gate is written as a float linear genome (row-1 logit =
dir * (x_feat - t), row 0 abstain at 0, rows 2..7 at -1e3; for dir -1 the strict "obs < thr" is exact because a tie
goes to row 0) and must reproduce the committed floor rows exactly before anything is read.

Gate (G-R16-floors r16_det, w13 train8_held64): feat 3, thr 11040, dir -1, act [7]; gate_train 183.625 (TRAIN8 per
seed), gate_held64 166.46875.

Rule (fixed before reading):
  I1  gate genome fused TRAIN8 == 183.625 and HELD64 == 166.46875; floors.gate_scores agrees; every archive's stored
      fitness == fused TRAIN8 recount x 8 for every elite -- else INDETERMINATE.
  per run r: reach_r = top1_train elite's TRAIN8 per-seed score >= 183.625; held_r = the archive holds >= 1 elite with
      HELD64 per seed >= 166.46875.
  SEARCH_SHORT  reach in <= 3/8 runs.
  SELECTION     reach in >= 5/8 AND held in >= 5/8.
  OVERFIT_ONLY  reach in >= 5/8 AND held in <= 3/8.
  MIXED         otherwise.
Controls: planted_gate (the gate genome added to each archive's elite list must be counted as held-quality in 8/8);
planted_abstain (the all-zero genome, HELD64 159.0, must never be counted).
Reported, not judged: per run top1 TRAIN8 / HELD64, best-HELD64 elite and its TRAIN8 and train rank, number of elites
with HELD64 >= gate, number with TRAIN8 > gate_train.
Sample: runs_total 8, rng_family_count 1, runs_per_family 8 (the saved round 4 archives; no Clause A verdict).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time

import numpy as np

from primordial.metric import floors as F
from primordial.metric import readout as RO
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.qd.archive import load_elites
from primordial.soup.b6.fused import FusedRollout

EXP = "D-R6-4-held-w13-train8-selection"
PREDICATE_ID = EXP
ANOMALY = "1789447409541-0"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
SRC_ROWS = "primordial/ledger/rows/G/G-R4-3-stage2.jsonl"
GS, PRESSURE = 13, "train8_held64"
GATE = {"feat": 3, "thr": 11040, "dir": -1, "act": [7]}
GATE_TRAIN, GATE_HELD = 183.625, 166.46875
ABSTAIN_HELD = 159.0
REACH_MIN, SHORT_MAX = 5, 3


def gate_genome(g7, gate=GATE) -> np.ndarray:
    """The gate as an E7.G7 float linear genome [1, glen]: row 1 logit = dir * (x_f - t), others abstain or -1e3."""
    D, A = g7.D, E7.A
    W = np.zeros((1, D, A), np.float32)
    b = np.full((1, A), -1e3, np.float32)
    b[0, 0] = 0.0
    t = np.float32(gate["thr"]) / np.float32(65535.0) - np.float32(0.5)
    W[0, gate["feat"], 1] = np.float32(gate["dir"])
    b[0, 1] = -np.float32(gate["dir"]) * t
    C = np.zeros((1, A, g7.W), np.uint8)
    C[0, 1] = np.asarray(gate["act"], np.uint8)
    return g7.pack(((W, b), C))


def per_seed(g7, raw: np.ndarray, seeds) -> np.ndarray:
    seeds = np.asarray(seeds)
    return FusedRollout(g7.spec, len(raw), seeds, family="linear").run(g7.unpack(raw))[0] / len(seeds)


def runs_from_rows(text: str) -> list[dict]:
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    out = {}
    for x in rows:
        if x.get("kind") == "run" and x.get("gen_seed") == GS and x.get("pressure") == PRESSURE and x.get("rng_family") is None:
            out[int(x["run_seed"])] = x
    return [out[k] for k in sorted(out)]


def decide(i1: bool, controls_ok: bool, reach: list[bool], held: list[bool]) -> str:
    if not (i1 and controls_ok):
        return "INDETERMINATE"
    r, h = sum(reach), sum(held)
    if r <= SHORT_MAX:
        return "SEARCH_SHORT"
    if r >= REACH_MIN and h >= REACH_MIN:
        return "SELECTION"
    if r >= REACH_MIN and h <= SHORT_MAX:
        return "OVERFIT_ONLY"
    return "MIXED"


def read_run(g7, doc: dict, graw: np.ndarray, zraw: np.ndarray) -> dict:
    elites = RO.elites_of(doc)
    raw = RO.packed(elites, g7.glen)
    fit = np.array([f for f, _ in elites], np.int64)
    tr, hd = per_seed(g7, raw, F.TRAIN8), per_seed(g7, raw, F.HELD64)
    recount_ok = bool(np.array_equal(np.rint(tr * len(F.TRAIN8)).astype(np.int64), fit))
    top = RO.select(elites)[0]
    ti = next(i for i, (f, g) in enumerate(elites) if g == top[1])
    b = int(np.argmax(hd))
    plant = np.concatenate([hd, per_seed(g7, np.concatenate([graw, zraw]), F.HELD64)])
    return {"n_elites": len(elites), "archive_fit_recount_ok": recount_ok,
            "top1_train8": float(tr[ti]), "top1_held64": float(hd[ti]),
            "reach": bool(tr[ti] >= GATE_TRAIN), "held": bool((hd >= GATE_HELD).any()),
            "n_held_ge_gate": int((hd >= GATE_HELD).sum()), "n_train_gt_gate": int((tr > GATE_TRAIN).sum()),
            "best_held64": float(hd[b]), "best_held_train8": float(tr[b]),
            "best_held_train_rank": int((tr > tr[b]).sum()) + 1,
            "planted_gate_counted": bool(plant[-2] >= GATE_HELD), "planted_abstain_counted": bool(plant[-1] >= GATE_HELD)}


def job(ctx, status="record"):
    t0 = time.perf_counter()
    g7 = E7.G7(GS, "linear")
    text = (ROOT / SRC_ROWS).read_text(encoding="utf-8")
    runs = runs_from_rows(text)
    graw = gate_genome(g7)
    zraw = np.zeros_like(graw)
    g_tr, g_hd = float(per_seed(g7, graw, F.TRAIN8)[0]), float(per_seed(g7, graw, F.HELD64)[0])
    spec = E4.Spec(GS)
    gd = {k: np.asarray([v]) for k, v in GATE.items() if k != "act"}
    gd["act"] = np.asarray([GATE["act"]])
    fs_tr, fs_hd = float(F.gate_scores(spec, gd, F.TRAIN8)[0]), float(F.gate_scores(spec, gd, F.HELD64)[0])
    z_hd = float(per_seed(g7, zraw, F.HELD64)[0])
    per = []
    for x in runs:
        doc = load_elites(x["elites"])
        per.append({"run_seed": int(x["run_seed"]), "elites": x["elites"],
                    "elites_sha256": hashlib.sha256(pathlib.Path(x["elites"]).read_bytes()).hexdigest(),
                    **read_run(g7, doc, graw, zraw)})
    i1 = {"gate_genome_train8": g_tr == GATE_TRAIN, "gate_genome_held64": g_hd == GATE_HELD,
          "floors_gate_scores_train8": fs_tr == GATE_TRAIN, "floors_gate_scores_held64": fs_hd == GATE_HELD,
          "abstain_genome_held64": z_hd == ABSTAIN_HELD, "runs": len(per) == 8,
          "archive_fit_recount_8of8": all(p["archive_fit_recount_ok"] for p in per)}
    controls = {"planted_gate": {"counted": sum(p["planted_gate_counted"] for p in per)},
                "planted_abstain": {"counted": sum(p["planted_abstain_counted"] for p in per)}}
    controls["planted_gate"]["ok"] = controls["planted_gate"]["counted"] == len(per)
    controls["planted_abstain"]["ok"] = controls["planted_abstain"]["counted"] == 0
    ok = controls["planted_gate"]["ok"] and controls["planted_abstain"]["ok"]
    decision = decide(all(i1.values()), ok, [p["reach"] for p in per], [p["held"] for p in per])
    ctx.emit({"kind": "summary", "exp": EXP, "predicate_id": PREDICATE_ID, "anomaly": ANOMALY, "status": status,
              "ts": round(time.time(), 3), "world": f"w{GS}", "pressure": PRESSURE, "representation": "float linear 200 B",
              "qd_runs": 0, "source_rows": SRC_ROWS, "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "runs_total": len(per), "rng_family_count": 1, "runs_per_family": len(per),
              "gate": GATE, "gate_train": GATE_TRAIN, "gate_held64": GATE_HELD,
              "measured": {"gate_genome_train8": g_tr, "gate_genome_held64": g_hd, "floors_train8": fs_tr,
                           "floors_held64": fs_hd, "abstain_genome_held64": z_hd},
              "checks": {"I1": i1, "controls_ok": bool(ok)}, "controls": controls, "per_run": per,
              "reach_k_of_8": sum(p["reach"] for p in per), "held_k_of_8": sum(p["held"] for p in per),
              "decision": decision, "wall_s": round(time.perf_counter() - t0, 3)})
