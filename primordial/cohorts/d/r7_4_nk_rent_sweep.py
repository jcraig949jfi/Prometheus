"""D-R7-4 (ANOM-1789417958280-0, prompts_r7/D.md item 4): C-R2-02 found that decoder_rent at LAMBDA 16384 did NOT shrink
programs -- the best small_program kept 7.5 of 8 active instructions while losing peak net fitness to the bitset control.
The anomaly's own discriminator (b): sweep LAMBDA in {0, 16384, 131072}; does best_active move?

Seen before this predicate: the anomaly text (coverage 0.943 vs 0.774, best net 2.655M vs 3.026M, best_active 7.5/8 at
LAMBDA 16384), C-R2-02's harness and its committed rows' schema and per-run wall (1.2-2.1 s at 300 gens x 128). No
sweep value exists yet.

C-R2-02's archive sampler is UNSEEDED (LuaArchive(..., UNSEEDED)), so its rows are REFERENCES ONLY and are not
reproduced here: D re-runs the program arm with a SEEDED sampler (D-R6-9 precedent) on lane D's Redis :6393 under its
own table key, importing C's Lua evaluator and numpy decoder unchanged (primordial.cohorts.c.r2_02_nk_program_rent:
EVAL_LUA, decode_ref) with LAMBDA as a parameter instead of a module constant.

Per LAMBDA: RNG families (4200, 2101, 3303, 5501) x run seeds 0..7 = runs_total 32, rng_family_count 4,
runs_per_family 8 (EVIDENCE_N_v1). Mutation PCG64([F, 2, rs, 0]) (C's stream prefixed by the family), sampler
PCG64([F + 1, 2, rs, 0]). 300 generations x 128 offers, program arm only (the bitset control carries no rent, so
LAMBDA cannot move it; C's control rows stand).

Readout (C's own): the archive elite with the highest NET fitness; best_active = its non-nop instruction count.

Rule, fixed before any sweep value. m(L) = median best_active over the 32 runs at LAMBDA L; shrink = #(F, rs) streams
whose best_active at 131072 is strictly below its best_active at 0.
  RENT_BINDS   m(131072) <= m(0) - 1 and shrink >= 24        (rent does shrink programs once it is large enough)
  RENT_INERT   m(0) == m(16384) == m(131072) and shrink <= 8 (an 8x rent moves nothing: C's reading generalises)
  MIXED        otherwise
  INDETERMINATE if I1 or a binding control fails.
I1: 32 runs per LAMBDA, 8 per family, every elite exact against the numpy reference (fit and cell) in every run, and
every offer of the first stream of each LAMBDA exact -- else INDETERMINATE.
Binding controls, per LAMBDA, on 1024 fixed random program genomes (C's rule): honest mismatch share == 0;
skip_last (instruction 7 not executed) >= 0.5; half_rent (LAMBDA // 2 charged) >= 0.9 -- EXEMPT at LAMBDA 0, where
half_rent is arithmetically identical to honest and cannot mismatch (stated before the run, not after).
Reported, not judged: median best_net, best_raw_nk, qd_score, coverage and archive cells per LAMBDA; the full
best_active distribution; C-R2-02's reference values.

    worker.submit("D", "primordial.cohorts.d.r7_4_nk_rent_sweep:job", EXP, ROWS, 600, envelope={...PRODUCTION...})
"""
from __future__ import annotations

import time

import numpy as np

from primordial.cohorts.c import r2_02_nk_program_rent as C2
from primordial.qd.stubworld import N_CELLS, NKWorld

EXP = "D-R7-4-nk-rent-sweep"
PREDICATE_ID = EXP
ANOMALY = "1789417958280-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
LAMBDAS = (0, 16384, 131072)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY, GENS, GLEN = 8, 300, 16
PORT, TABLE_KEY = 6393, "pm:d:r7-4:nk"
CHEAT_GENOMES = 1024
BINDS_SHRINK, INERT_SHRINK = 24, 8
REFERENCE = {"exp": "C-R2-02-nk-small-program-decoder-rent", "lambda": 16384, "best_active_median": 8,
             "note": "C's sampler was UNSEEDED: reference only, not reproduced"}


def eval_ref(world: NKWorld, g: np.ndarray, lam: int, cheat: int = 0):
    """C's numpy reference with LAMBDA as a parameter (C2.eval_ref mode 0 reads the module constant)."""
    bits, active = C2.decode_ref(g, cheat)
    fit, cell = world.evaluate(np.packbits(bits, axis=1))
    charged = lam // 2 if cheat == 2 else lam
    return (fit.astype(np.int64) - charged * active).astype(np.int32), cell


class Ev:
    """C's Lua evaluator, under D's own table key, with LAMBDA as a parameter."""

    def __init__(self, r, world: NKWorld, lam: int, key: str = TABLE_KEY):
        r.set(key, world.table.astype("<u2").tobytes())
        self.script, self.lam, self.key = r.register_script(C2.EVAL_LUA), int(lam), key

    def __call__(self, g: np.ndarray, cheat: int = 0):
        f, c = self.script(keys=[self.key], args=[0, g.tobytes(), g.shape[1], self.lam, cheat])
        return np.frombuffer(f, "<i4").astype(np.int32), np.frombuffer(c, "<u4").astype(np.uint32)


def run_one(r, ev: Ev, world: NKWorld, lam: int, fam: int, rs: int, gens: int = GENS, audit: bool = False) -> dict:
    """C-R2-02's program arm, family-prefixed streams and a SEEDED sampler."""
    from primordial.qd.archive import LuaArchive
    arch = LuaArchive(r, f"d-r7-4-l{lam}-f{fam}-r{rs}", GLEN, sampler_seed=[fam + 1, 2, rs, 0])
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([fam, 2, rs, 0]))
    t0, offers, bad = time.perf_counter(), 0, 0
    for _ in range(gens):
        par = arch.sample(C2.BATCH)
        if len(par) == 0:
            g = rng.integers(0, 256, (C2.BATCH, GLEN), dtype=np.uint8)
        else:
            m = rng.random(par.shape) < 1.0 / GLEN
            g = np.where(m, rng.integers(0, 256, par.shape, dtype=np.uint8), par)
        fit, cell = ev(g)
        if audit:
            rf, rc = eval_ref(world, g, lam)
            offers += len(g)
            bad += int(((rf != fit) | (rc != cell)).sum())
        arch.insert(cell, fit, g, np.zeros((len(g), 2), np.uint32))
    el = arch.dump()
    arch.clear()
    cells = np.array(sorted(el), np.uint32)
    ef = np.array([el[int(c)][0] for c in cells], np.int64)
    eg = np.frombuffer(b"".join(el[int(c)][1] for c in cells), np.uint8).reshape(-1, GLEN)
    rf, rc = eval_ref(world, eg, lam)
    elite_bad = int(((rf.astype(np.int64) != ef) | (rc != cells)).sum())
    best = int(np.argmax(ef))
    raw = world.evaluate(np.packbits(C2.decode_ref(eg[best:best + 1])[0], axis=1))[0]
    return {"kind": "run", "exp": EXP, "arm": "small_program", "lambda": int(lam), "family": int(fam),
            "run_seed": int(rs), "gens": gens, "offers": gens * C2.BATCH, "genome_bytes": GLEN,
            "best_active": int(C2.decode_ref(eg[best:best + 1])[1][0]), "best_net": int(ef[best]),
            "best_raw_nk": int(raw[0]), "qd_score": int(ef.sum()), "archive_cells": len(el),
            "coverage": round(len(el) / N_CELLS, 4), "elites_audited": len(el), "elites_mismatched": elite_bad,
            "offers_audited": offers, "offers_mismatched": bad, "wall_s": round(time.perf_counter() - t0, 2)}


def cheat_controls(ev_of, world: NKWorld, lam: int) -> dict:
    """C's three controls at this LAMBDA; half_rent is EXEMPT at LAMBDA 0 (it charges LAMBDA // 2 == LAMBDA)."""
    rng = np.random.Generator(np.random.PCG64(777))
    cg = rng.integers(0, 256, (CHEAT_GENOMES, GLEN), dtype=np.uint8)
    out = {}
    for name, cheat in (("honest", 0), ("skip_last", 1), ("half_rent", 2)):
        lf, lc = ev_of(cg, cheat)
        rf, rc = eval_ref(world, cg, lam)
        out[name] = {"mismatch_share": round(float(((lf != rf) | (lc != rc)).mean()), 4)}
    out["honest"]["ok"] = out["honest"]["mismatch_share"] == 0.0
    out["skip_last"]["ok"] = out["skip_last"]["mismatch_share"] >= 0.5
    out["half_rent"]["exempt"] = lam == 0
    out["half_rent"]["ok"] = True if lam == 0 else out["half_rent"]["mismatch_share"] >= 0.9
    return out


def decide(i1: bool, controls_ok: bool, runs: dict) -> tuple[str, dict]:
    """runs: {lambda: {(family, run_seed): row}}."""
    if not (i1 and controls_ok) or sorted(runs) != sorted(LAMBDAS):
        return "INDETERMINATE", {}
    med = {L: float(np.median([r["best_active"] for r in runs[L].values()])) for L in LAMBDAS}
    lo, hi = LAMBDAS[0], LAMBDAS[-1]
    keys = sorted(set(runs[lo]) & set(runs[hi]))
    shrink = int(sum(runs[hi][k]["best_active"] < runs[lo][k]["best_active"] for k in keys))
    stats = {"median_best_active": {str(L): med[L] for L in LAMBDAS}, "shrink_streams": shrink,
             "paired_streams": len(keys)}
    if med[hi] <= med[lo] - 1 and shrink >= BINDS_SHRINK:
        return "RENT_BINDS", stats
    if len({med[L] for L in LAMBDAS}) == 1 and shrink <= INERT_SHRINK:
        return "RENT_INERT", stats
    return "MIXED", stats


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID, gens: int = GENS):
    import redis
    t0 = time.perf_counter()
    r = redis.Redis(host="127.0.0.1", port=PORT)
    world = NKWorld()
    todo = [(L, f, rs) for L in LAMBDAS for f in FAMILIES for rs in range(RUNS_PER_FAMILY)]
    st = ctx.load_checkpoint() or {"next": 0, "runs": {}, "controls": {}}
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        L, fam, rs = todo[st["next"]]
        ev = Ev(r, world, L)
        if str(L) not in st["controls"]:
            ctl = cheat_controls(ev, world, L)
            st["controls"][str(L)] = ctl
            ctx.emit({"kind": "cheat_control", "exp": exp, "lambda": int(L), "genomes": CHEAT_GENOMES,
                      "status": "control", "ts": round(time.time(), 3), **ctl})
        first = (fam, rs) == (FAMILIES[0], 0)
        row = run_one(r, ev, world, L, fam, rs, gens, audit=first)
        st["runs"].setdefault(str(L), {})[f"{fam}|{rs}"] = row
        ctx.emit({**row, "predicate_id": predicate_id, "status": status, "ts": round(time.time(), 3)})
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    runs = {int(L): {tuple(int(x) for x in k.split("|")): v for k, v in d.items()} for L, d in st["runs"].items()}
    per_fam = {str(L): {str(f): sum(k[0] == f for k in runs[L]) for f in FAMILIES} for L in runs}
    i1 = {"runs_32_per_lambda": all(len(runs[L]) == 32 for L in runs),
          "per_family_8": all(v == 8 for d in per_fam.values() for v in d.values()),
          "lambdas": sorted(runs) == sorted(LAMBDAS),
          "elites_exact": all(v["elites_mismatched"] == 0 for d in runs.values() for v in d.values()),
          "first_stream_offers_exact": all(any(v["offers_audited"] > 0 and v["offers_mismatched"] == 0
                                               for v in d.values()) for d in runs.values())}
    ok = all(c["honest"]["ok"] and c["skip_last"]["ok"] and c["half_rent"]["ok"] for c in st["controls"].values())
    decision, stats = decide(all(i1.values()), ok, runs)
    rep = {str(L): {k: float(np.median([v[k] for v in runs[L].values()]))
                    for k in ("best_net", "best_raw_nk", "qd_score", "coverage", "archive_cells")} for L in runs}
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "anomaly": ANOMALY, "status": status,
              "evidence_class": "VERDICT", "ts": round(time.time(), 3), "gens": gens, "batch": C2.BATCH,
              "lambdas": list(LAMBDAS), "runs_total": 32, "rng_family_count": 4, "runs_per_family": 8,
              "families": list(FAMILIES), "n_per_family": {str(f): 8 for f in FAMILIES},
              "runs_total_all_lambdas": sum(len(d) for d in runs.values()),
              "checks": {"I1": i1, "controls_ok": ok}, "controls": st["controls"], "stats": stats,
              "decision": decision,
              "reported_not_judged": {"medians_by_lambda": rep, "reference": REFERENCE,
                                      "best_active_by_lambda": {str(L): sorted(v["best_active"] for v in runs[L].values())
                                                                for L in runs}},
              "wall_s": round(time.perf_counter() - t0, 3)})
