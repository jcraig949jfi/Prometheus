"""C-R5-AP-01 (ANTI_PRIOR, cell assigned by code): tt_digits / signal_world_d1 / cpu_ttl / redis_lua / none
(anti_prior.assign exp_id C-R5-AP-01, assign seed 4796911454902464105, round 5 pilot).

The experimenter received only the cell; the prior is unread. No definition of this cell existed; the definitions
below are fixed before any run. signal_world_d1 is not a screened world: no floor suite, no clause A claim.

  world     lane D's D1 signal world (primordial.lingua.signal): T = 64 ticks, R in [0, 256) per tick; right iff
            slot 1's act == R >> 5.
  channel   none: slot 0's symbol reaches slot 1 unmetered and uncorrupted (no ledger, no cost). With no charge,
            fitness = right actions summed over episodes.
  brain     tt_digits: C4 TTDigits (rank 3, D = 1: R as a uint16 feature, 4 hex digit cores, MSD first) is slot 0's
            encoder, sym = argmax of 8 logits; slot 1's decoder is lane E's codebook form, 8 bytes, act = cb[sym] % 8.
            Genome 2412 float32 bytes + 8 codebook bytes = 2420 bytes. The task is a pure function of R, so fitness is
            computed from the genome's action table over R = 0..255 weighted by the episode sample histogram (exact).
  substrate redis_lua: E's LuaArchive (atomic insert + seeded sampler, server-side Lua) on lane C's substrate :6392.
            Descriptor cell = (distinct symbols used - 1) * 8 + (distinct actions used - 1), 64 cells. Batch 128.
            Float genes mutate C4 (p .05, sigma .2); each codebook byte is redrawn uniformly with p 1/8.
  pressure  cpu_ttl (C-R2-01's rule): the training loop stops at the first generation boundary where the client process
            CPU time spent in the loop (time.process_time) reaches TTL_CPU_S. TTL_CPU_S = control's full-budget
            per-run CPU / 5, the control CPU taken from a no-rows timing check before any run (disclosed).
            Redis server-side Lua CPU is NOT charged; the redis-server used_cpu delta per run is reported (loophole).
  arms      cell (cpu_ttl) vs control (full budget GENS generations), same GA and sampler streams.
  sample    RNG families (4200, 2101, 3303, 5501), run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 5115]); sampler_seed [family + 1, run_seed, arm, 5115].
            TRAIN = episode seeds 0..15 (1024 registers), HELD = 10,000,000..10,000,255 (16,384 registers).
  reader    top1_train: the archive elite with the highest TRAIN fitness (ties: smaller genome bytes); value = its HELD
            yield (right share).
  primary   median over the 32 runs of HELD yield (cell) >= median (control) - 0.5 * IQR (control).
  oracles   family 4200 run seed 0, each arm:
            brain    float64 reference TT (ref_logits) on R = 0..255 for the top-16 elites: emitted symbol == reference
                     argmax on every clear row (0 mismatched); cheat skip_odd (odd cores skipped) mismatches the
                     reference on >= 90% of ELIGIBLE rows (clear rows where the float64 skip_odd reference itself changes
                     the argmax; >= 1 required)
            fitness  scalar per-register recount over the raw TRAIN samples == archive fitness for the top-16 (exact)
            archive  a client-side serial reference of every offer (same total order) == the Lua archive dump (exact)
            ttl      cell arm loop CPU < TTL_CPU_S + the largest single-generation CPU of that run

  worker:  job = primordial.cohorts.c.r5_ap01_tt_digits_d1_cpu_ttl_lua:job
  dev:     python -m primordial.cohorts.c.r5_ap01_tt_digits_d1_cpu_ttl_lua dev   (no rows)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.lingua import signal as S

EXP = "C-R5-AP-01-tt-digits-d1-cpu-ttl-lua"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
CELL = {"representation": "tt_digits", "world": "signal_world_d1", "pressure": "cpu_ttl", "substrate": "redis_lua",
        "channel": "none"}
CELL_CTRL = dict(CELL, pressure="none_control")
T, A = 64, 8
FAM = gm.TTDigits(1, A)
PB = FAM.nbytes
GLEN = PB + 8
BATCH, TOP = 128, 16
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
GENS = 400      # no-rows dev check (control, 20 gens) 0.0195 CPU-s / 0.0229 wall-s per gen: largest of {100, 200, 400, 800}
                # whose projection (32 control runs + 32 cell runs at TTL) stays <= half the PILOT ceilings; 800 -> 703 wall-s
TTL_CPU_S = 1.56  # C-R2-01 rule: control full-budget per-run CPU / 5 = 400 * 0.0195 / 5
PORT = 6392
R_ALL = np.arange(256)
TRAIN_R = S.r_stream(np.arange(16), T).reshape(-1)
HELD_R = S.r_stream(10_000_000 + np.arange(256), T).reshape(-1)
H_TRAIN = np.bincount(TRAIN_R, minlength=256)
H_HELD = np.bincount(HELD_R, minlength=256)
TRUTH = R_ALL >> S.SHIFT


def unpack(B):
    return FAM.unpack(np.ascontiguousarray(B[:, :PB])), B[:, PB:PB + 8].astype(np.int64) % A


def pack(p, cb):
    return np.concatenate([FAM.pack(p), cb.astype(np.uint8)], 1)


def tables(p, cb, cheat=False):
    """-> sym [P, 256], act [P, 256] over R = 0..255."""
    P = len(cb)
    obs = np.tile(R_ALL, P)[:, None].astype(np.uint16)
    gidx = np.repeat(np.arange(P), 256)
    sym = FAM.forward(p, obs, gidx, cheat).reshape(P, 256)
    # act = cb[sym] % 8 (the declared decoder). init/mutate hand over raw bytes 0..255; before C-R5-AP-01b the
    # reduction happened only in unpack, so offer-time fitness scored bytes >= 8 as never right (C-R5-AP-01 oracle)
    return sym, np.asarray(cb, np.int64)[np.arange(P)[:, None], sym] % A


def evaluate(p, cb):
    sym, act = tables(p, cb)
    right = act == TRUTH[None, :]
    fit = (right * H_TRAIN[None, :]).sum(1).astype(np.int64)
    u_sym = np.array([len(np.unique(s)) for s in sym])
    u_act = np.array([len(np.unique(a)) for a in act])
    cells = ((u_sym - 1) * 8 + (u_act - 1)).astype(np.uint32)
    return fit, cells, right


def mutate(rng, p, cb):
    p = FAM.mutate(rng, p)
    m = rng.random(cb.shape) < 1.0 / 8
    return p, np.where(m, rng.integers(0, 256, cb.shape), cb)


def server_cpu(r) -> float:
    i = r.info("cpu")
    return float(i["used_cpu_sys"]) + float(i["used_cpu_user"])


def _better(f, g, old):
    return old is None or f > old[0] or (f == old[0] and g < old[1])


def run(r, family, rs, arm_i, gens, ttl, track=False):
    from primordial.qd.archive import LuaArchive
    rng = np.random.Generator(np.random.PCG64([family, rs, arm_i, 5115]))
    arch = LuaArchive(r, f"c-r5-ap01-{family}-{rs}-{arm_i}", GLEN, sampler_seed=[family + 1, rs, arm_i, 5115])
    arch.clear()
    ref = {} if track else None
    s0, c0 = server_cpu(r), time.process_time()
    gen_cpu, done = [], 0
    for _ in range(gens):
        if ttl is not None and time.process_time() - c0 >= ttl:
            break
        g0 = time.process_time()
        par = arch.sample(BATCH)
        if len(par) == 0:
            p, cb = FAM.init(rng, BATCH), rng.integers(0, 256, (BATCH, 8))
        else:
            p, cb = mutate(rng, *unpack(par))
        fit, cells, _ = evaluate(p, cb)
        G = pack(p, cb)
        arch.insert(cells, fit.astype(np.int32), G, np.zeros((BATCH, 2), np.uint32))
        if track:
            for c, f, g in zip(cells.tolist(), fit.tolist(), G):
                gb = g.tobytes()
                if _better(f, gb, ref.get(c)):
                    ref[c] = (f, gb)
        gen_cpu.append(time.process_time() - g0)
        done += 1
    loop_cpu = time.process_time() - c0
    el = arch.dump()
    arch.clear()
    order = sorted(el.values(), key=lambda v: (-v[0], v[1]))
    raw = np.frombuffer(b"".join(v[1] for v in order[:TOP]), np.uint8).reshape(-1, GLEN)
    info = {"gens_done": done, "loop_cpu_s": round(loop_cpu, 4), "max_gen_cpu_s": round(max(gen_cpu or [0.0]), 4),
            "redis_server_cpu_s": round(server_cpu(r) - s0, 4), "archive_cells": len(el)}
    if track:
        info["archive_mismatched_cells"] = int(len(set(ref) ^ set(el)) + sum(
            1 for c in set(ref) & set(el) if (ref[c][0], ref[c][1]) != (el[c][0], el[c][1])))
    return raw, [int(v[0]) for v in order[:TOP]], info


def ref_skip_logits(g1, obs):
    al, G, Wo = (x.astype(np.float64) for x in g1)
    idx = FAM.index(obs)
    out = np.zeros((len(obs), A))
    for i in range(len(obs)):
        v = al.copy()
        for c in range(idx.shape[1]):
            if c % 2:
                continue
            v = v @ G[c, idx[i, c]]
            v /= max(np.abs(v).max(), 1e-300)
        out[i] = v @ Wo
    return out


def oracles(raw, archive_fits) -> dict:
    p, cb = unpack(raw)
    sym, act = tables(p, cb)
    cheat_sym, _ = tables(p, cb, cheat=True)
    obs = R_ALL[:, None].astype(np.uint16)
    honest_bad = rows = elig = caught = 0
    for q in range(len(raw)):
        one = FAM.one(p, q)
        ref = FAM.ref_logits(one, obs)
        refs = ref_skip_logits(one, obs)
        clear = gm.clear_rows(ref)
        honest_bad += int(((sym[q] != ref.argmax(1)) & clear).sum())
        e = clear & gm.clear_rows(refs) & (refs.argmax(1) != ref.argmax(1))
        rows += 256
        elig += int(e.sum())
        caught += int(((cheat_sym[q] != ref.argmax(1)) & e).sum())
    fit_bad = 0
    for q in range(len(raw)):
        cnt = sum(1 for x in TRAIN_R.tolist() if int(act[q, x]) == x >> S.SHIFT)
        fit_bad += int(cnt != archive_fits[q])
    out = {"brain": {"rows": rows, "honest_mismatched_clear_rows": honest_bad, "skip_odd_eligible_rows": elig,
                     "skip_odd_share": round(caught / elig, 4) if elig else 0.0},
           "fitness_recount_mismatched_elites": fit_bad}
    out["ok"] = bool(honest_bad == 0 and elig > 0 and caught / elig >= 0.9 and fit_bad == 0)
    return out


def held_row(raw):
    p, cb = unpack(raw[:1])
    sym, act = tables(p, cb)
    right = act[0] == TRUTH
    return {"held_yield": float((right * H_HELD).sum() / H_HELD.sum()),
            "train_yield": float((right * H_TRAIN).sum() / H_TRAIN.sum()),
            "symbols_used_top1": int(len(np.unique(sym[0]))), "actions_used_top1": int(len(np.unique(act[0])))}


def job(ctx, gens: int = GENS, ttl_cpu_s: float = TTL_CPU_S, port: int = PORT):
    import redis
    r = redis.Redis(host="127.0.0.1", port=port)
    arms = (("cell", ttl_cpu_s, CELL), ("control", None, CELL_CTRL))
    todo = [(f, rs, ai) for f in FAMILIES for rs in range(RUNS_PER_FAMILY) for ai in range(2)]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": []}, "clean": True, "ref": False}
    if not st["ref"]:
        ctx.emit({"kind": "reference", "exp_id": EXP, "gens": gens, "batch": BATCH, "ttl_cpu_s": ttl_cpu_s,
                  "genome_bytes": GLEN, "chance_yield": S.CHANCE, "status": "control", "ts": round(time.time(), 3)})
        st["ref"] = True
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        fam, rs, ai = todo[st["next"]]
        arm, ttl, cell = arms[ai]
        first = fam == FAMILIES[0] and rs == 0
        t0, c0 = time.perf_counter(), time.process_time()
        raw, fits, info = run(r, fam, rs, ai, gens, ttl, track=first)
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
               "genome_bytes": GLEN, "reader": "top1_train", "train_fit_top1": fits[0], **info, **held_row(raw),
               "status": "record" if arm == "cell" else "control"}
        if first:
            o = oracles(raw, fits)
            o["archive_mismatched_cells"] = info["archive_mismatched_cells"]
            o["ok"] = o["ok"] and info["archive_mismatched_cells"] == 0
            if arm == "cell":
                o["ttl_ok"] = info["loop_cpu_s"] < ttl + info["max_gen_cpu_s"]
                o["ok"] = o["ok"] and o["ttl_ok"]
            row["oracles"] = o
            st["clean"] = st["clean"] and o["ok"]
        row["cpu_s"], row["wall_s"] = round(time.process_time() - c0, 3), round(time.perf_counter() - t0, 3)
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(row["held_yield"])
        ctx.emit(row)
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    q = {a: [float(x) for x in np.percentile(st["held"][a], [25, 50, 75])] for a in st["held"]}
    bar = q["control"][1] - 0.5 * (q["control"][2] - q["control"][0])
    n = {a: len(st["held"][a]) for a in st["held"]}
    full = all(v == len(FAMILIES) * RUNS_PER_FAMILY for v in n.values())
    primary = "INDETERMINATE" if not (st["clean"] and full) else ("PASS" if q["cell"][1] >= bar else "FAIL")
    ctx.emit({"kind": "summary", "exp_id": EXP, "cell": CELL, "runs_total": n["cell"],
              "rng_family_count": len(FAMILIES), "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
              "held_yield_median_cell": round(q["cell"][1], 5), "iqr_cell": round(q["cell"][2] - q["cell"][0], 5),
              "held_yield_median_control": round(q["control"][1], 5),
              "iqr_control": round(q["control"][2] - q["control"][0], 5), "bar": round(bar, 5),
              "oracle_clean": st["clean"], "primary": primary,
              "clause_a": "none: signal_world_d1 is not a screened world (no floor suite)",
              "status": "record" if st["clean"] else "cheat", "ts": round(time.time(), 3)})


def dev(gens: int = 20) -> None:
    """No rows: full-budget timing (control arm, no TTL) + oracles on a short run."""
    import redis
    r = redis.Redis(host="127.0.0.1", port=PORT)
    c, t = time.process_time(), time.perf_counter()
    raw, fits, info = run(r, 4200, 0, 1, gens, None, track=True)
    out = {"gens": gens, "cpu_s_per_gen": round((time.process_time() - c) / gens, 4),
           "wall_s_per_gen": round((time.perf_counter() - t) / gens, 4), "info": info, "held": held_row(raw),
           "oracles": oracles(raw, fits)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dev(int(sys.argv[2]) if len(sys.argv) > 2 else 20) if sys.argv[1] == "dev" else None
