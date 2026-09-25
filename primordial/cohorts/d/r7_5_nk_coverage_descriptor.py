"""D-R7-5 (ANOM-1789517158930-0, D's own child of 1789417958280-0): C-R2-02's small_program arm beat the bitset control
on coverage 0.943 vs 0.774 with full separation, and D-R7-4 then showed that coverage stays ~0.94 at every LAMBDA
(0.9472 / 0.9371 / 0.94075) while best_active collapses 7 -> 2. Does the coverage gap rest on the DESCRIPTOR being
sweepable by the program's fill/clear ops?

C-R2-02's descriptor is popcount halves: d0 = popcount(bits 0..31), d1 = popcount(bits 32..63), cell = d0 * 33 + d1.
Ops 3 (set b[k..k+7]) and 4 (clear b[k..k+7]) move a popcount by up to 8 in one instruction, so a short program can
walk the grid. The anomaly's discriminator (a): re-run both arms with a descriptor those ops cannot shortcut.

CONTRIBUTION HALVES (this experiment's descriptor, defined here before any run): the NK fitness loop already sums a
per-locus contribution table[j, idx_j]; c0 = sum over loci 0..31, c1 = sum over 32..63, each bucketed
b = min(32, floor(c / (32 * 65535) * 32)), cell = b0 * 33 + b1. Same 1089-cell grid, so coverage is comparable.
Setting 8 adjacent bits moves c0/c1 by an amount that depends on the table, not by a fixed count.

C-R2-02's sampler was UNSEEDED, so its rows are REFERENCES ONLY and its numbers cannot be compared against seeded runs.
This experiment therefore generates its OWN popcount baseline: 4 cells = {small_program (decoder_rent, LAMBDA 16384),
bitset (no rent)} x {popcount, contribution}, each at RNG families (4200, 2101, 3303, 5501) x run seeds 0..7 =
runs_total 32, rng_family_count 4, runs_per_family 8 (EVIDENCE_N_v1). Mutation PCG64([F, 2, rs, mode]), sampler
PCG64([F + 1, 2, rs, mode]) -- the same streams across descriptors, so popcount and contribution are paired per stream.
300 generations x 128 offers, C's Lua evaluator and numpy decoder imported unchanged except for the descriptor branch,
on lane D's Redis :6393 under D's own table key.

Rule, fixed before any coverage value. gap(desc) = median coverage(program, desc) - median coverage(bitset, desc);
sep(desc) = min coverage(program, desc) > max coverage(bitset, desc).
  I1 (binding replication): gap(popcount) >= 0.10 AND sep(popcount) -- D's seeded harness must reproduce C's
     qualitative coverage gap, else the contribution arm is uninterpretable -> INDETERMINATE.
  GAP_PERSISTS   gap(contribution) >= 0.10 and sep(contribution)   (the gap is not a descriptor artifact)
  GAP_VANISHES   gap(contribution) <= 0.05                          (it was: the ops were sweeping the descriptor)
  MIXED          otherwise
Binding controls: descriptor_equivalence -- the Lua cell equals the numpy cell on 1024 fixed random genomes for BOTH
descriptors and BOTH modes; and C's cheat controls on the program arm (honest mismatch 0, skip_last >= 0.5,
half_rent >= 0.9 at LAMBDA 16384).
Reported, not judged: coverage distributions and archive cells per cell; best_net, best_raw_nk, best_active; the
popcount-vs-contribution coverage difference per stream.

    worker.submit("D", "primordial.cohorts.d.r7_5_nk_coverage_descriptor:job", EXP, ROWS, 900, envelope={...})
"""
from __future__ import annotations

import time

import numpy as np

from primordial.cohorts.c import r2_02_nk_program_rent as C2
from primordial.qd.stubworld import GRID, N_BITS, N_CELLS, NKWorld, mutate as bit_mutate

EXP = "D-R7-5-nk-coverage-descriptor"
PREDICATE_ID = EXP
ANOMALY = "1789517158930-0"
PARENT_ANOMALY = "1789417958280-0"
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY, GENS = 8, 300
LAMBDA = C2.LAMBDA                      # C-R2-02's own rent for the program arm; the bitset arm carries none
PORT, TABLE_KEY = 6393, "pm:d:r7-5:nk"
DESCRIPTORS = ("popcount", "contribution")
MODES = {0: "small_program", 1: "bitset"}
MAX_HALF = 32 * 65535                   # 32 loci x the table's max uint16 contribution
CHEAT_GENOMES = 1024
GAP_PERSISTS, GAP_VANISHES = 0.10, 0.05
REFERENCE = {"exp": "C-R2-02-nk-small-program-decoder-rent", "coverage_program": 0.943, "coverage_bitset": 0.774,
             "note": "C's sampler was UNSEEDED: reference only, not reproduced; D generates its own popcount baseline"}

# C's EVAL_LUA with ONE addition: ARGV[6] selects the descriptor. The fitness, rent, decode and cheat paths are
# byte-identical to C's (the fitness loop already computes each locus's contribution, so the new descriptor reuses it).
EVAL_LUA = C2.EVAL_LUA.replace(
    "local lambda, cheat = tonumber(ARGV[4]), tonumber(ARGV[5])",
    "local lambda, cheat = tonumber(ARGV[4]), tonumber(ARGV[5])\nlocal desc = tonumber(ARGV[6])").replace(
    "  local f, d0, d1 = 0, 0, 0",
    "  local f, d0, d1, c0, c1 = 0, 0, 0, 0, 0").replace(
    "    f = f + lo + hi * 256\n    if j < 32 then d0 = d0 + b[j] else d1 = d1 + b[j] end",
    "    local contrib = lo + hi * 256\n    f = f + contrib\n"
    "    if j < 32 then d0 = d0 + b[j]; c0 = c0 + contrib else d1 = d1 + b[j]; c1 = c1 + contrib end").replace(
    "  cells[gi + 1] = struct.pack('<I4', d0 * 33 + d1)",
    "  if desc == 1 then\n"
    "    local b0 = floor(c0 / 2097120 * 32)\n    local b1 = floor(c1 / 2097120 * 32)\n"
    "    if b0 > 32 then b0 = 32 end\n    if b1 > 32 then b1 = 32 end\n"
    "    cells[gi + 1] = struct.pack('<I4', b0 * 33 + b1)\n"
    "  else\n    cells[gi + 1] = struct.pack('<I4', d0 * 33 + d1)\n  end")


def cells_of(world: NKWorld, bits: np.ndarray, descriptor: str) -> np.ndarray:
    """bits uint8 [B, 64] -> cell uint32 [B] under either descriptor (numpy reference)."""
    b = np.ascontiguousarray(bits, np.int64)
    if descriptor == "popcount":
        return (b[:, :32].sum(1) * GRID + b[:, 32:].sum(1)).astype(np.uint32)
    idx = b[:, world._cols] @ world._w                                  # [B, 64] neighbourhood index per locus
    contrib = world.table[np.arange(N_BITS)[None, :], idx]              # [B, 64] per-locus contribution
    b0 = np.minimum(32, (contrib[:, :32].sum(1) / MAX_HALF * 32).astype(np.int64))
    b1 = np.minimum(32, (contrib[:, 32:].sum(1) / MAX_HALF * 32).astype(np.int64))
    return (b0 * GRID + b1).astype(np.uint32)


def eval_ref(world: NKWorld, g: np.ndarray, mode: int, descriptor: str, cheat: int = 0):
    """C's reference with the descriptor as a parameter; rent applies to the program arm only."""
    if mode == 1:
        bits = np.unpackbits(np.ascontiguousarray(g, np.uint8), axis=1)
        fit = world.evaluate(g)[0].astype(np.int64)
        return fit.astype(np.int32), cells_of(world, bits, descriptor)
    bits, active = C2.decode_ref(g, cheat)
    fit = world.evaluate(np.packbits(bits, axis=1))[0].astype(np.int64)
    charged = LAMBDA // 2 if cheat == 2 else LAMBDA
    return (fit - charged * active).astype(np.int32), cells_of(world, bits, descriptor)


class Ev:
    def __init__(self, r, world: NKWorld, descriptor: str, key: str = TABLE_KEY):
        r.set(key, world.table.astype("<u2").tobytes())
        self.script, self.key = r.register_script(EVAL_LUA), key
        self.desc = 1 if descriptor == "contribution" else 0

    def __call__(self, g: np.ndarray, mode: int, cheat: int = 0):
        f, c = self.script(keys=[self.key], args=[mode, g.tobytes(), g.shape[1], LAMBDA, cheat, self.desc])
        return np.frombuffer(f, "<i4").astype(np.int32), np.frombuffer(c, "<u4").astype(np.uint32)


def run_one(r, ev: Ev, world: NKWorld, mode: int, descriptor: str, fam: int, rs: int, gens: int = GENS,
            audit: bool = False) -> dict:
    from primordial.qd.archive import LuaArchive
    glen = 16 if mode == 0 else 8
    arch = LuaArchive(r, f"d-r7-5-{descriptor}-m{mode}-f{fam}-r{rs}", glen, sampler_seed=[fam + 1, 2, rs, mode])
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([fam, 2, rs, mode]))
    t0, offers, bad = time.perf_counter(), 0, 0
    for _ in range(gens):
        par = arch.sample(C2.BATCH)
        if len(par) == 0:
            g = rng.integers(0, 256, (C2.BATCH, glen), dtype=np.uint8)
        elif mode == 1:
            g = bit_mutate(rng, par)
        else:
            m = rng.random(par.shape) < 1.0 / glen
            g = np.where(m, rng.integers(0, 256, par.shape, dtype=np.uint8), par)
        fit, cell = ev(g, mode)
        if audit:
            rf, rc = eval_ref(world, g, mode, descriptor)
            offers += len(g)
            bad += int(((rf != fit) | (rc != cell)).sum())
        arch.insert(cell, fit, g, np.zeros((len(g), 2), np.uint32))
    el = arch.dump()
    arch.clear()
    cells = np.array(sorted(el), np.uint32)
    ef = np.array([el[int(c)][0] for c in cells], np.int64)
    eg = np.frombuffer(b"".join(el[int(c)][1] for c in cells), np.uint8).reshape(-1, glen)
    rf, rc = eval_ref(world, eg, mode, descriptor)
    elite_bad = int(((rf.astype(np.int64) != ef) | (rc != cells)).sum())
    best = int(np.argmax(ef))
    bits_best = C2.decode_ref(eg[best:best + 1])[0] if mode == 0 else np.unpackbits(eg[best:best + 1], axis=1)
    return {"kind": "run", "exp": EXP, "arm": MODES[mode], "descriptor": descriptor, "lambda": LAMBDA if mode == 0 else 0,
            "family": int(fam), "run_seed": int(rs), "gens": gens, "offers": gens * C2.BATCH, "genome_bytes": glen,
            "coverage": round(len(el) / N_CELLS, 4), "archive_cells": len(el),
            "best_net": int(ef[best]), "best_raw_nk": int(world.evaluate(np.packbits(bits_best, axis=1))[0][0]),
            "best_active": int(C2.decode_ref(eg[best:best + 1])[1][0]) if mode == 0 else 0,
            "qd_score": int(ef.sum()), "elites_audited": len(el), "elites_mismatched": elite_bad,
            "offers_audited": offers, "offers_mismatched": bad, "wall_s": round(time.perf_counter() - t0, 2)}


def descriptor_equivalence(ev_of, world: NKWorld, descriptor: str) -> dict:
    """Binding: the Lua cell equals the numpy cell on fixed random genomes, in both modes."""
    rng = np.random.Generator(np.random.PCG64(778))
    out = {}
    for mode in (0, 1):
        g = rng.integers(0, 256, (CHEAT_GENOMES, 16 if mode == 0 else 8), dtype=np.uint8)
        lf, lc = ev_of(g, mode)
        rf, rc = eval_ref(world, g, mode, descriptor)
        out[MODES[mode]] = {"cell_mismatch": int((lc != rc).sum()), "fit_mismatch": int((lf != rf).sum()),
                            "genomes": CHEAT_GENOMES}
    out["ok"] = all(v["cell_mismatch"] == 0 and v["fit_mismatch"] == 0 for v in out.values() if isinstance(v, dict))
    return out


def cheat_controls(ev_of, world: NKWorld, descriptor: str) -> dict:
    """C's program-arm cheats at LAMBDA 16384."""
    rng = np.random.Generator(np.random.PCG64(777))
    cg = rng.integers(0, 256, (CHEAT_GENOMES, 16), dtype=np.uint8)
    out = {}
    for name, cheat in (("honest", 0), ("skip_last", 1), ("half_rent", 2)):
        lf, lc = ev_of(cg, 0, cheat)
        rf, rc = eval_ref(world, cg, 0, descriptor)
        out[name] = {"mismatch_share": round(float(((lf != rf) | (lc != rc)).mean()), 4)}
    out["honest"]["ok"] = out["honest"]["mismatch_share"] == 0.0
    out["skip_last"]["ok"] = out["skip_last"]["mismatch_share"] >= 0.5
    out["half_rent"]["ok"] = out["half_rent"]["mismatch_share"] >= 0.9
    return out


def gap_of(runs: dict, descriptor: str) -> dict:
    prog = [v["coverage"] for (d, m, _, _), v in runs.items() if d == descriptor and m == 0]
    bits = [v["coverage"] for (d, m, _, _), v in runs.items() if d == descriptor and m == 1]
    if not prog or not bits:
        return {"gap": None, "separated": False, "n_program": len(prog), "n_bitset": len(bits)}
    return {"gap": round(float(np.median(prog) - np.median(bits)), 4), "separated": bool(min(prog) > max(bits)),
            "median_program": float(np.median(prog)), "median_bitset": float(np.median(bits)),
            "min_program": float(min(prog)), "max_bitset": float(max(bits)),
            "n_program": len(prog), "n_bitset": len(bits)}


def decide(i1_ok: bool, controls_ok: bool, runs: dict) -> tuple[str, dict]:
    pop, con = gap_of(runs, "popcount"), gap_of(runs, "contribution")
    stats = {"popcount": pop, "contribution": con}
    replicates = bool(pop["gap"] is not None and pop["gap"] >= GAP_PERSISTS and pop["separated"])
    stats["popcount_replicates_C"] = replicates
    if not (i1_ok and controls_ok and replicates) or con["gap"] is None:
        return "INDETERMINATE", stats
    if con["gap"] >= GAP_PERSISTS and con["separated"]:
        return "GAP_PERSISTS", stats
    if con["gap"] <= GAP_VANISHES:
        return "GAP_VANISHES", stats
    return "MIXED", stats


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID, gens: int = GENS):
    import redis
    t0 = time.perf_counter()
    r = redis.Redis(host="127.0.0.1", port=PORT)
    world = NKWorld()
    todo = [(d, m, f, rs) for d in DESCRIPTORS for m in (0, 1) for f in FAMILIES for rs in range(RUNS_PER_FAMILY)]
    st = ctx.load_checkpoint() or {"next": 0, "runs": {}, "controls": {}}
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        d, m, fam, rs = todo[st["next"]]
        ev = Ev(r, world, d)
        if d not in st["controls"]:
            eq, ch = descriptor_equivalence(ev, world, d), cheat_controls(ev, world, d)
            st["controls"][d] = {"descriptor_equivalence": eq, "cheats": ch}
            ctx.emit({"kind": "control", "exp": exp, "descriptor": d, "status": "control",
                      "ts": round(time.time(), 3), "descriptor_equivalence": eq, "cheats": ch})
        row = run_one(r, ev, world, m, d, fam, rs, gens, audit=(fam, rs) == (FAMILIES[0], 0))
        st["runs"][f"{d}|{m}|{fam}|{rs}"] = row
        ctx.emit({**row, "predicate_id": predicate_id, "status": status, "ts": round(time.time(), 3)})
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    runs = {(k.split("|")[0], int(k.split("|")[1]), int(k.split("|")[2]), int(k.split("|")[3])): v
            for k, v in st["runs"].items()}
    i1 = {"runs_32_per_cell": all(sum(1 for k in runs if k[0] == d and k[1] == m) == 32 for d in DESCRIPTORS for m in (0, 1)),
          "per_family_8": all(sum(1 for k in runs if k[0] == d and k[1] == m and k[2] == f) == 8
                              for d in DESCRIPTORS for m in (0, 1) for f in FAMILIES),
          "elites_exact": all(v["elites_mismatched"] == 0 for v in runs.values()),
          "first_stream_offers_exact": all(any(v["offers_audited"] > 0 and v["offers_mismatched"] == 0
                                               for k, v in runs.items() if k[0] == d and k[1] == m)
                                           for d in DESCRIPTORS for m in (0, 1))}
    ok = all(c["descriptor_equivalence"]["ok"] and c["cheats"]["honest"]["ok"] and c["cheats"]["skip_last"]["ok"]
             and c["cheats"]["half_rent"]["ok"] for c in st["controls"].values())
    decision, stats = decide(all(i1.values()), ok, runs)
    paired = [round(runs[("popcount", 0, f, rs)]["coverage"] - runs[("contribution", 0, f, rs)]["coverage"], 4)
              for f in FAMILIES for rs in range(RUNS_PER_FAMILY)
              if ("popcount", 0, f, rs) in runs and ("contribution", 0, f, rs) in runs]
    rep = {f"{d}|{MODES[m]}": {k: float(np.median([v[k] for key, v in runs.items() if key[0] == d and key[1] == m]))
                               for k in ("coverage", "archive_cells", "best_net", "best_raw_nk", "best_active", "qd_score")}
           for d in DESCRIPTORS for m in (0, 1)}
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "anomaly": ANOMALY,
              "parent_anomaly": PARENT_ANOMALY, "status": status, "evidence_class": "VERDICT",
              "ts": round(time.time(), 3), "gens": gens, "batch": C2.BATCH, "lambda_program": LAMBDA,
              "descriptors": list(DESCRIPTORS), "runs_total": 32, "rng_family_count": 4, "runs_per_family": 8,
              "families": list(FAMILIES), "n_per_family": {str(f): 8 for f in FAMILIES},
              "runs_total_all_cells": len(runs), "checks": {"I1": i1, "controls_ok": ok}, "controls": st["controls"],
              "stats": stats, "decision": decision,
              "reported_not_judged": {"medians_by_cell": rep, "reference": REFERENCE,
                                      "paired_popcount_minus_contribution_program": paired,
                                      "coverage_by_cell": {f"{d}|{MODES[m]}": sorted(v["coverage"] for k, v in runs.items()
                                                                                     if k[0] == d and k[1] == m)
                                                           for d in DESCRIPTORS for m in (0, 1)}},
              "wall_s": round(time.perf_counter() - t0, 3)})
