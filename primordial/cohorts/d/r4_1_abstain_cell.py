"""D-R4-1 (ANOM-1789426590583-0): do the QD archives reach the abstain cell, and if they do, where is it lost?

The anomaly (G-M1, conductor-confirmed): always-abstain beats every committed elite on HELD64 and on TRAIN,
so "MAP-Elites never reaches the zero-cost abstain policy". Its discriminator: does the abstain genome
survive insertion; how many genomes abstain on every tick.

No new QD run. The M2 float linear baseline archives that built worlds_r4.json are saved per run seed (C2,
seeded sampler): 74 world x pressure cells x 8 run seeds = 592 full archives. Per archive:

  reach        cell 1056 = abstain row 32, magnitude 0 (E7 descriptor, GRID 33) occupied?
  abstain_elite  that cell's elite: train score (archive fit / k), HELD64 score, == the abstain policy?
  top1         best elite by (-train fit, genome bytes): train and HELD64 score
  top16        M2's readout (baseline.top_raw + per-seed mean on HELD64): must reproduce the committed
               held64_by_run_seed exactly (instrument check, aimed at the number the screen used);
               per genome: HELD64, train ties with abstain, HELD64 == abstain
  rank         the abstain elite's position in the (-fit, genome) order

Abstain scores are recomputed (floors.const_scores, zero action) and checked against worlds_r4 floor_parts.
Cheat control (planted): the abstain elite with every codebook row set to action 1 must NOT score the
abstain HELD64 value. Oracles on run seed 0 per cell: E7.world_oracle (wforge hash + charge, HELD8) and
fused == numpy E7.rollout on the abstain elite and the top-16.

    python -m primordial.fabric.worker submit D primordial.cohorts.d.r4_1_abstain_cell:job \\
        --exp D-R4-1-abstain-cell-reach --rows primordial/ledger/rows/D/D-R4-1-abstain-cell-reach.jsonl \\
        --ttl-cpu-s 3000 --kwargs '{}'
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from primordial.metric import baseline as B
from primordial.metric import floors as F
from primordial.qd import e7_run as E7
from primordial.qd.archive import LuaArchive, load_elites, restore_elites
from primordial.soup.b6.fused import GRID, FusedRollout

EXP = "D-R4-1-abstain-cell-reach"
ROOT = pathlib.Path(__file__).resolve().parents[3]
WORLDS = "primordial/ledger/qd/worlds_r4.json"
ABSTAIN_CELL = 32 * GRID + 0
ARCHIVE_URL = "redis://127.0.0.1:6393/0"          # lane D substrate: scratch archives for the insertion test
EPS = 1e-9


def held_each(g7, raw: np.ndarray, seeds) -> np.ndarray:
    """Per-genome per-seed score [P] (float64)."""
    return FusedRollout(g7.spec, len(raw), np.asarray(seeds), family="linear").run(g7.unpack(raw))[0] / len(seeds)


def planted(g7, raw: np.ndarray) -> np.ndarray:
    """CHEAT: the same genome acting 1 on every codebook row (never abstains)."""
    p, C = g7.unpack(raw)
    C[:] = 1
    return g7.pack((p, C))


def archive_row(g7, cell: dict, rs: int, abst: dict, oracle: bool) -> dict:
    doc = load_elites(cell["baseline"]["elites"][str(rs)])
    tr = F.PRESSURES[cell["pressure"]]
    k = len(tr)
    el = [(int(c), int(f), bytes.fromhex(g)) for c, f, g, *_ in doc["elites"]]
    order = sorted(el, key=lambda v: (-v[1], v[2]))
    top = B.top_raw([(f, g) for _, f, g in el], doc["glen"])
    top_train = np.array([f for _, f, _ in order[:len(top)]]) / k
    h16 = held_each(g7, top, F.HELD64)
    committed = float(cell["baseline"]["held64_by_run_seed"][str(rs)])
    cells = np.array([c for c, _, _ in el])
    ab_rows = cells // GRID
    row = {"kind": "archive", "world": cell["world"], "gen_seed": cell["gen_seed"], "pressure": cell["pressure"],
           "run_seed": rs, "verdict_r4": cell["verdict"], "n_cells": len(el), "max_abstain_row": int(ab_rows.max()),
           "n_row_ge30": int((ab_rows >= 30).sum()),
           "abstain_train": abst["train"], "abstain_held64": abst["held"],
           "top16_mean_held64": float(h16.mean()), "committed_held64": committed,
           "top16_reproduces": abs(float(h16.mean()) - committed) < EPS,
           "top16_held64": [round(float(x), 6) for x in h16], "top16_train": [round(float(x), 6) for x in top_train],
           "top16_n_train_ge_abstain": int((top_train >= abst["train"] - EPS).sum()),
           "top16_n_held_eq_abstain": int((np.abs(h16 - abst["held"]) < EPS).sum()),
           "top16_n_held_ge_abstain": int((h16 >= abst["held"] - EPS).sum()),
           "top1_train": float(top_train[0]), "top1_held64": float(h16[0]),
           "best_held64_in_top16": float(h16.max())}
    hit = [v for v in el if v[0] == ABSTAIN_CELL]
    row["reach"] = bool(hit)
    if hit:
        c, f, g = hit[0]
        raw = np.frombuffer(g, np.uint8).reshape(1, -1)
        pair = np.concatenate([raw, planted(g7, raw)])
        hp = held_each(g7, pair, F.HELD64)
        row.update(abstain_elite_train=f / k, abstain_elite_held64=float(hp[0]),
                   abstain_elite_is_abstain_held=bool(abs(hp[0] - abst["held"]) < EPS),
                   abstain_elite_train_eq=bool(abs(f / k - abst["train"]) < EPS),
                   abstain_elite_rank=int(order.index(hit[0])),
                   abstain_elite_in_top16=bool(order.index(hit[0]) < len(top)),
                   cheat_planted_held64=float(hp[1]),
                   cheat_planted_fails=bool(abs(hp[1] - abst["held"]) >= EPS))
        hc = FusedRollout(g7.spec, 1, F.HELD64, family="linear").run(g7.unpack(raw))[1]
        row.update(abstain_elite_held_cell=int(hc[0]), abstain_elite_held_abstain_row=int(hc[0]) // GRID,
                   train_mimic=bool(row["abstain_elite_train_eq"] and not row["abstain_elite_is_abstain_held"]))
        if oracle:
            s8 = np.asarray(F.HELD64[:8])
            both = np.concatenate([raw, top])
            gg = g7.unpack(both)
            fused = FusedRollout(g7.spec, len(both), s8, family="linear").run(gg)[0]
            row["oracle_held8"] = {"world": E7.world_oracle(g7, g7.unpack(raw), s8),
                                   "fused_eq_numpy": bool(np.array_equal(np.asarray(fused, np.int64),
                                                                         np.asarray(E7.rollout(g7, gg, s8)[0], np.int64)))}
    return row


def zero_insert(r, g7, cell: dict, rs: int, abst: dict) -> dict:
    """The anomaly's own discriminator. The all-zero genome (W = 0, b = 0, codebook 0: every logit ties,
    argmax -> row 0 -> abstain) is scored on TRAIN and HELD64, then inserted with its TRAIN fitness and cell
    into a scratch LuaArchive restored from the saved archive (lane D substrate). Survives iff cell 1056
    then holds it."""
    doc = load_elites(cell["baseline"]["elites"][str(rs)])
    tr = F.PRESSURES[cell["pressure"]]
    zero = np.zeros((1, doc["glen"]), np.uint8)
    fit_t, cell_t = FusedRollout(g7.spec, 1, tr, family="linear").run(g7.unpack(zero))[:2]
    held = float(FusedRollout(g7.spec, 1, F.HELD64, family="linear").run(g7.unpack(zero))[0][0] / len(F.HELD64))
    arch = LuaArchive(r, f"d-r4-1-{cell['world']}-{cell['pressure']}-r{rs}", doc["glen"], [7101, rs])
    arch.clear()
    restore_elites(arch, doc)
    before = arch.dump().get(ABSTAIN_CELL)
    wins = arch.insert(np.asarray(cell_t, np.uint32), np.asarray(fit_t, np.int32), zero, np.zeros((1, 2), np.uint32))
    after = arch.dump().get(ABSTAIN_CELL)
    arch.clear()
    return {"zero_train": float(fit_t[0]) / len(tr), "zero_train_cell": int(cell_t[0]), "zero_held64": held,
            "zero_is_abstain": bool(abs(float(fit_t[0]) / len(tr) - abst["train"]) < EPS
                                    and abs(held - abst["held"]) < EPS and int(cell_t[0]) == ABSTAIN_CELL),
            "zero_insert_wins": int(wins), "zero_survives": bool(after is not None and after[1] == zero.tobytes()),
            "occupant_fit_before": None if before is None else int(before[0])}


def cell_summary(cell: dict, rows: list[dict]) -> dict:
    hit = [x for x in rows if x["reach"]]
    med = lambda key, xs: float(np.median([x[key] for x in xs])) if xs else None
    return {"kind": "cell", "world": cell["world"], "gen_seed": cell["gen_seed"], "pressure": cell["pressure"],
            "verdict_r4": cell["verdict"], "floor_abstain": cell["floor_parts"]["abstain"],
            "abstain_held64": rows[0]["abstain_held64"], "abstain_train": rows[0]["abstain_train"],
            "floor_abstain_matches": abs(cell["floor_parts"]["abstain"] - rows[0]["abstain_held64"]) < EPS,
            "baseline_median": cell["baseline"]["median"], "n_runs": len(rows), "n_reach": len(hit),
            "n_abstain_exact": sum(x["abstain_elite_is_abstain_held"] for x in hit),
            "n_reproduces": sum(x["top16_reproduces"] for x in rows),
            "median_top16_held64": med("top16_mean_held64", rows), "median_top1_held64": med("top1_held64", rows),
            "median_abstain_elite_held64": med("abstain_elite_held64", hit),
            "n_top1_train_ge_abstain": sum(x["top1_train"] >= x["abstain_train"] - EPS for x in rows),
            "n_abstain_elite_in_top16": sum(x["abstain_elite_in_top16"] for x in hit),
            "n_cheat_fails": sum(x["cheat_planted_fails"] for x in hit),
            "n_train_mimic": sum(x["train_mimic"] for x in hit),
            "n_zero_is_abstain": sum(x["zero_is_abstain"] for x in rows),
            "n_zero_survives": sum(x["zero_survives"] for x in rows)}


def job(ctx, worlds_json=WORLDS, only=None, dev=False, archive_url=ARCHIVE_URL):
    import redis
    r = redis.Redis.from_url(archive_url)
    p = pathlib.Path(worlds_json)
    cells = json.loads((p if p.is_absolute() else ROOT / p).read_text(encoding="utf-8"))["cells"]
    keep = None if only is None else {(w, pr) for w, pr in only}
    st = ctx.load_checkpoint() or {"cells": {}}
    status = "dev" if dev else "record"
    for cell in cells:
        key = f"{cell['world']}|{cell['pressure']}"
        if (keep is not None and (cell["world"], cell["pressure"]) not in keep) or key in st["cells"]:
            continue
        if ctx.should_pause():
            ctx.pause(st)
        g7 = E7.G7(int(cell["gen_seed"]), "linear")
        z = np.zeros((1, g7.W), np.int32)
        abst = {"train": float(F.const_scores(g7.spec, z, F.PRESSURES[cell["pressure"]])[0]),
                "held": float(F.const_scores(g7.spec, z, F.HELD64)[0])}
        rows = []
        for rs in sorted(int(x) for x in cell["baseline"]["elites"]):
            row = {**archive_row(g7, cell, rs, abst, oracle=(rs == 0)), **zero_insert(r, g7, cell, rs, abst)}
            if "oracle_held8" in row:
                ctx.emit({**{k: row[k] for k in ("world", "pressure", "run_seed")}, "kind": "oracle",
                          "status": "control", **row["oracle_held8"]})
            if row["reach"]:
                ctx.emit({**{k: row[k] for k in ("world", "pressure", "run_seed")}, "kind": "cheat_planted",
                          "status": "cheat", "held64": row["cheat_planted_held64"],
                          "abstain_held64": abst["held"], "fails": row["cheat_planted_fails"]})
            ctx.emit({**row, "status": status})
            rows.append(row)
        s = cell_summary(cell, rows)
        ctx.emit({**s, "status": status})
        st["cells"][key] = s
        ctx.checkpoint(st)
    if keep is None or len(st["cells"]) == len(keep):
        ctx.emit({**verdict(list(st["cells"].values())), "status": status})


def verdict(cs: list[dict]) -> dict:
    """The pre-registered checks (bus predicate D-R4-1) over the cell summaries."""
    n = sum(c["n_runs"] for c in cs)
    reach = sum(c["n_reach"] for c in cs)
    exact = sum(c["n_abstain_exact"] for c in cs)
    below = [c for c in cs if c["baseline_median"] < c["abstain_held64"] - EPS]
    rescued = [c for c in below if c["median_abstain_elite_held64"] is not None
               and c["median_abstain_elite_held64"] >= c["abstain_held64"] - EPS]
    return {"kind": "summary", "exp": EXP, "n_cells": len(cs), "n_archives": n,
            "checks": {
                "I_top16_reproduces_all": sum(c["n_reproduces"] for c in cs) == n,
                "I_floor_abstain_matches_all": all(c["floor_abstain_matches"] for c in cs),
                "C_cheat_planted_fails_ge90pct": sum(c["n_cheat_fails"] for c in cs) >= 0.9 * reach,
                "P1_reach_ge90pct": reach >= 0.9 * n,
                "P2_abstain_elite_exact_ge90pct_of_reached": exact >= 0.9 * reach,
                "P3_below_cells_rescued_by_abstain_elite_ge90pct": len(rescued) >= 0.9 * len(below),
                "C_zero_genome_is_abstain_all": sum(c["n_zero_is_abstain"] for c in cs) == n,
                "P4_zero_survives_insertion_ge99pct": sum(c["n_zero_survives"] for c in cs) >= 0.99 * n},
            "counts": {"reach": reach, "abstain_exact": exact, "train_mimic": sum(c["n_train_mimic"] for c in cs),
                       "zero_survives": sum(c["n_zero_survives"] for c in cs),
                       "top1_train_ge_abstain": sum(c["n_top1_train_ge_abstain"] for c in cs),
                       "abstain_elite_in_top16": sum(c["n_abstain_elite_in_top16"] for c in cs),
                       "cells_baseline_below_abstain": len(below), "of_which_rescued": len(rescued)},
            "below_cells": [[c["world"], c["pressure"], c["verdict_r4"], round(c["baseline_median"], 3),
                             round(c["abstain_held64"], 3), c["median_abstain_elite_held64"]] for c in below]}
