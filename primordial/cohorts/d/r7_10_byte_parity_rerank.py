"""D-R7-10 (ANOM-1789415790371-0): E9 ranked the brain families on held-out score as linear > tt_feat > tt_digits
(medians 35.5 / 17.1 / 8.7 on w1, 103.2 / 91.6 / 78.9 on w3, 89.9 / 79.2 / 62.0 on w4) while their genome sizes run the
other way (linear 208-344 B, tt_feat 3004-5316 B, tt_digits 11644-20868 B). The anomaly: richer TT brains should fit at
least as well, so does the fewest-byte family really generalise best -- or is the ranking an artifact of parameter
count? Its discriminator: equalise parameter count across families and re-rank.

What is actually equalisable, checked before this predicate. _TT.rank is a class attribute read by shapes(), so the TT
families can be shrunk by rank; G7 caches pb/glen from fam.nbytes, so rank must be set before those are read (this
module does). Measured on world 4 (D=8): linear 288 B; tt_feat 4716 / 2120 / 548 B at rank 3 / 2 / 1; tt_digits
18540 / 8264 / 2084 B. So tt_feat AT RANK 1 reaches linear's byte scale (548 vs 288, under 2x) and is the matched cell,
while tt_digits BOTTOMS OUT at 2084 B (~7x linear) because its core COUNT (4D = 32 cores x 16 entries) dominates, not
its rank. The anomaly's "equalise parameter count across families" is therefore executable for tt_feat and
structurally impossible for tt_digits by rank alone; tt_digits is run and reported, never used for the verdict.

E9's sampler was UNSEEDED (LuaArchive(..., UNSEEDED)), so its rows are REFERENCES ONLY and are not reproduced. This
experiment re-runs E9's own loop with a SEEDED sampler and generates its own rank-3 baseline (the D-R7-5 / D-R7-4
pattern), on lane E's Redis :6394 under D's own key prefix.

Cells: (linear, -), (tt_feat, 3|2|1), (tt_digits, 3|2|1) x worlds (4, 1, 3) x run seeds 0..7 = 168 runs, E9's budget
(200 generations x batch 128), E9's readout (top-16 by (-fitness, bytes), held64_per_seed and train_per_seed through
fused_score). Streams carry the rank so no two cells share one: mutation PCG64([990, rs, gs, family_index, rank]),
sampler PCG64([991, rs, gs, family_index, rank]).

Rule (fixed before any held-out value is read). med(f, r, w) = median held64_per_seed over the 8 run seeds.
  I1 (binding replication): at rank 3 -- E9's own setting -- med(linear) > med(tt_feat, 3) > med(tt_digits, 3) in at
     least 2 of the 3 worlds. D's seeded harness must reproduce E9's qualitative ranking, or the matched-parameter
     comparison is unreadable -> INDETERMINATE.
  Q  compares linear (288 B) with the matched cell tt_feat at rank 1 (548 B):
     PARITY_REVERSES  med(tt_feat, 1, w) >= med(linear, w) in >= 2 of 3 worlds   (the byte advantage was capacity:
                                                                                  matched on parameters, the TT family
                                                                                  catches or beats linear)
     PARITY_HOLDS     med(linear, w) >  med(tt_feat, 1, w) in >= 2 of 3 worlds   (fewest-byte still wins at matched
                                                                                  parameter count)
     MIXED            otherwise (ties)
  INDETERMINATE if I1 or a binding control fails.
Binding controls, E9's own oracles at run seed 0 of every cell x world: world_oracle_honest 0 failing elites and
world_oracle_skip_lin >= 14/16 caught; brain_oracle_honest 0 mismatched clear rows and brain_oracle_cheat >= 14/16.
Reported, not judged: the full (family, rank, world) grid of median held64 and train; param_bytes per cell; the
tt_digits arm at every rank (parameter parity unreachable); E9's published medians as reference; per-cell wall.

    worker.submit("D", "primordial.cohorts.d.r7_10_byte_parity_rerank:job", EXP, ROWS, 2400, envelope={...})
"""
from __future__ import annotations

import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.qd import e7_run as E7
from primordial.qd import e9_run as E9
from primordial.soup.b6.fused import FusedRollout

EXP = "D-R7-10-byte-parity-rerank"
PREDICATE_ID = EXP
ANOMALY = "1789415790371-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
WORLDS = (4, 1, 3)
RUN_SEEDS = tuple(range(8))
GENS, BATCH, TOP = 200, 128, E9.TOP
PORT = 6394
CELLS = (("linear", None), ("tt_feat", 3), ("tt_feat", 2), ("tt_feat", 1),
         ("tt_digits", 3), ("tt_digits", 2), ("tt_digits", 1))
BASELINE_RANK = 3                       # E9's own setting
MATCHED = ("tt_feat", 1)                # the only TT cell that reaches linear's byte scale
WORLD_MAJORITY = 2                      # of 3 worlds
E9_PUBLISHED = {"1": {"linear": 35.5, "tt_feat": 17.1, "tt_digits": 8.7},
                "3": {"linear": 103.2, "tt_feat": 91.6, "tt_digits": 78.9},
                "4": {"linear": 89.9, "tt_feat": 79.2, "tt_digits": 62.0},
                "note": "E9's sampler was UNSEEDED: reference only, not reproduced"}


def build(gs: int, fam: str, rank):
    """G7 with the TT rank applied BEFORE pb/glen are read (G7.__init__ caches them from fam.nbytes)."""
    g7 = E7.G7(int(gs), fam)
    if rank is not None:
        g7.fam.rank = int(rank)
        g7.pb = g7.fam.nbytes
        g7.glen = (g7.pb + g7.cb + 3) // 4 * 4
    return g7


def run_one(r, gs: int, fam: str, rank, rs: int, gens: int = GENS, batch: int = BATCH, oracles: bool = False) -> dict:
    """E9's per-run loop, with a SEEDED sampler and the rank folded into both streams."""
    from primordial.qd.archive import LuaArchive
    g7 = build(gs, fam, rank)
    fi = list(gm.FAMILIES).index(fam)
    rk = 0 if rank is None else int(rank)
    t0 = time.perf_counter()
    arch = LuaArchive(r, f"d-r7-10-{gs}-{fam}-{rk}-{rs}", g7.glen, sampler_seed=[991, rs, gs, fi, rk])
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([990, rs, gs, fi, rk]))
    fr = FusedRollout(g7.spec, batch, E9.TRAIN, family=fam)
    t_eval = 0.0
    for _ in range(gens):
        par = arch.sample(batch)
        g = g7.init(rng, batch) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
        s = time.perf_counter()
        fit, cells = fr.run(g)[:2]
        t_eval += time.perf_counter() - s
        arch.insert(cells, fit, g7.pack(g), np.zeros((batch, 2), np.uint32))
    el = arch.dump()
    raw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:TOP]),
                        np.uint8).reshape(-1, g7.glen)
    arch.clear()
    row = {"kind": "run", "exp": EXP, "gen_seed": int(gs), "family": fam, "rank": rk, "run_seed": int(rs),
           "param_bytes": int(g7.pb), "genome_bytes": int(g7.glen), "genomes": gens * batch, "cells": len(el),
           "fused_eval_s": round(t_eval, 2),
           "train_per_seed": E9.fused_score(g7, fam, raw, E9.TRAIN),
           "held64_per_seed": E9.fused_score(g7, fam, raw, E9.HELD64)}
    if oracles:
        top = g7.unpack(raw)
        row["world_oracle_honest"] = E7.world_oracle(g7, top, E9.HELD8)
        row["world_oracle_skip_lin"] = E7.world_oracle(g7, top, E9.HELD8, "skip_lin")
        row["brain_oracle_honest"] = E7.brain_oracle(g7, top, E9.HELD8)
        row["brain_oracle_cheat"] = E7.brain_oracle(g7, top, E9.HELD8, cheat=True)
    row["wall_s"] = round(time.perf_counter() - t0, 2)
    return row


def medians(rows: list[dict]) -> dict:
    """{(family, rank, world): median held64_per_seed over the run seeds}."""
    by = {}
    for x in rows:
        by.setdefault((x["family"], int(x["rank"]), int(x["gen_seed"])), []).append(float(x["held64_per_seed"]))
    return {k: float(np.median(v)) for k, v in by.items()}


def i1_ranking(med: dict) -> dict:
    """E9's qualitative ranking at rank 3, world by world."""
    out = {}
    for w in WORLDS:
        lin = med.get(("linear", 0, w))
        tf = med.get(("tt_feat", BASELINE_RANK, w))
        td = med.get(("tt_digits", BASELINE_RANK, w))
        out[str(w)] = bool(lin is not None and tf is not None and td is not None and lin > tf > td)
    out["worlds_holding"] = sum(1 for w in WORLDS if out[str(w)])
    out["ok"] = out["worlds_holding"] >= WORLD_MAJORITY
    return out


def decide(i1_ok: bool, controls_ok: bool, med: dict) -> tuple[str, dict]:
    fam, rank = MATCHED
    per_world, rev, hold = {}, 0, 0
    for w in WORLDS:
        lin, m = med.get(("linear", 0, w)), med.get((fam, rank, w))
        if lin is None or m is None:
            per_world[str(w)] = None
            continue
        per_world[str(w)] = {"linear": lin, f"{fam}@{rank}": m, "matched_ge_linear": bool(m >= lin)}
        rev += m >= lin
        hold += lin > m
    stats = {"per_world": per_world, "worlds_matched_ge_linear": rev, "worlds_linear_ahead": hold,
             "matched_cell": f"{fam}@rank{rank}"}
    if not (i1_ok and controls_ok):
        return "INDETERMINATE", stats
    if rev >= WORLD_MAJORITY:
        return "PARITY_REVERSES", stats
    if hold >= WORLD_MAJORITY:
        return "PARITY_HOLDS", stats
    return "MIXED", stats


def oracles_ok(row: dict) -> bool:
    """E9's posted rule: world 0 failing and skip_lin >= 14/16; brain 0 mismatched clear rows and cheat >= 14/16."""
    w, wl = row.get("world_oracle_honest") or {}, row.get("world_oracle_skip_lin") or {}
    b, bc = row.get("brain_oracle_honest") or {}, row.get("brain_oracle_cheat") or {}
    return bool(w.get("elites_failing") == 0 and wl.get("elites_failing", 0) >= 14
                and b.get("mismatched_rows") == 0 and bc.get("elites_mismatching", 0) >= 14)


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID, gens: int = GENS):
    import redis
    t0 = time.perf_counter()
    r = redis.Redis(host="127.0.0.1", port=PORT)
    todo = [(fam, rank, gs, rs) for fam, rank in CELLS for gs in WORLDS for rs in RUN_SEEDS]
    st = ctx.load_checkpoint() or {"next": 0, "rows": []}
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        fam, rank, gs, rs = todo[st["next"]]
        row = run_one(r, gs, fam, rank, rs, gens, BATCH, oracles=(rs == 0))
        st["rows"].append(row)
        ctx.emit({**row, "predicate_id": predicate_id, "status": status, "ts": round(time.time(), 3)})
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    rows = st["rows"]
    med = medians(rows)
    i1r = i1_ranking(med)
    oracle_rows = [x for x in rows if "world_oracle_honest" in x]
    bad = [(x["family"], x["rank"], x["gen_seed"]) for x in oracle_rows if not oracles_ok(x)]
    i1 = {"runs_168": len(rows) == len(todo), "cells_complete": len(med) == len(CELLS) * len(WORLDS),
          "ranking_at_rank3": i1r["ok"], "oracle_rows_21": len(oracle_rows) == len(CELLS) * len(WORLDS)}
    controls = {"e9_oracles_clean": not bad, "failing_cells": bad, "oracle_rows": len(oracle_rows)}
    decision, stats = decide(all(i1.values()), controls["e9_oracles_clean"], med)
    grid = {f"{f}@{rk}|w{w}": {"held64": v, "param_bytes": next((x["param_bytes"] for x in rows
                                                                 if x["family"] == f and x["rank"] == rk), None)}
            for (f, rk, w), v in sorted(med.items(), key=lambda kv: (kv[0][0], -kv[0][1], kv[0][2]))}
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "anomaly": ANOMALY, "status": status,
              "evidence_class": "OBSERVATION", "ts": round(time.time(), 3), "worlds": list(WORLDS),
              "run_seeds": list(RUN_SEEDS), "gens": gens, "batch": BATCH, "cells": [list(c) for c in CELLS],
              "matched_cell": f"{MATCHED[0]}@rank{MATCHED[1]}",
              "checks": {"I1": i1, "i1_ranking_detail": i1r, "controls_ok": controls["e9_oracles_clean"]},
              "controls": controls, "stats": stats, "decision": decision,
              "reported_not_judged": {
                  "grid_median_held64": grid, "e9_published": E9_PUBLISHED,
                  "tt_digits_parity_unreachable": "tt_digits bottoms out at ~2084 B (~7x linear) because its core "
                                                  "count (4D) dominates, not its rank; it is reported at every rank "
                                                  "and never used for the verdict",
                  "median_train_by_cell": {f"{f}@{rk}|w{w}": float(np.median(
                      [x["train_per_seed"] for x in rows if x["family"] == f and x["rank"] == rk and x["gen_seed"] == w]))
                      for f, rk in ((c[0], 0 if c[1] is None else c[1]) for c in CELLS) for w in WORLDS},
                  "wall_by_cell": {f"{f}@{rk}": round(sum(x["wall_s"] for x in rows
                                                          if x["family"] == f and x["rank"] == rk), 1)
                                   for f, rk in ((c[0], 0 if c[1] is None else c[1]) for c in CELLS)}},
              "wall_s": round(time.perf_counter() - t0, 3)})
