"""C-R7-AP-04 (ANTI_PRIOR, cell assigned by code): bitset / w13 / regime_switching / numba_fused / none
(anti_prior.assign exp_id C-R7-AP-04, round 7).

The experimenter received only the cell; the prior and the arm are unread. The definitions below are fixed before any
run.

  world     w13 (E4.Spec(13)), the round 4 screen's SURVIVED world: T = 32, S = 1, W = 1, D = 5, delay 1, stoch_rate 0,
            act_cost 1, step_cost 1, yield reg 5 in [14152, 16200) -> +10, start charge 191.
  pressure  regime_switching. w13 AS SCREENED has regime_period = 0, so the flip does not exist in it and had to be
            defined here. It is TAKEN from the world generator, not tuned: wforge/world.py emits
            regime_period = 0 if r.below(3) else (8 << r.below(4)), so its non-zero values are exactly {8, 16, 32, 64}.
            The horizon is 32, and a flip needs (tick // period) % 2 == 1, so periods 32 and 64 never flip inside an
            episode. RULE fixed before the run: take the SMALLEST emitted period that produces >= 2 flip windows within
            T -> period 8 (ticks 8..15 and 24..31 flipped, 0..7 and 16..23 not). The flip negates every linear
            multiplier (a -> M - a), exactly as b1/np_world, b6/fused and the nv backends implement it.
  arms      cell = w13 with regime_period 8; control = w13 exactly as screened (regime_period 0). Same genomes, same GA
            and sampler streams, same budget. The arms differ only by the world's flip.
  brain     bitset: E4's OWN genome, a per-tick action tape of T x S x W = 32 bytes (a multiple of 4), read straight
            from the genome with no decoder -- a bitset reads no observation (C-R6-AP-02). E4.init_genomes, E4.mutate
            and E4.descriptor (abstain share, action magnitude, 33 x 33) are reused UNCHANGED.
  channel   none: the tape is executed as written; there is no observation path to meter.
  substrate numba_fused: a numba njit kernel (prange over envs) that steps lane B1's world semantics from the tape.
            soup.b6.fused.FusedRollout cannot serve this cell -- it fuses observe + brain + act + step and requires a C4
            brain family, and a tape has no brain -- so the kernel here mirrors b6/fused's step order exactly: intake
            cost and pending writes, ring landing, linear ops with the regime flip, stochastic kick (value drawn before
            index), yield window, step cost, liveness, history ring. It is bound by two independent references
            (below), never trusted on its own. Archive: E's LuaArchive on lane C's :6392, genome 32 bytes.
  budget    selection on TRAIN8 = E4.SEEDS (9100..9107); the reader scores HELD64 (30000..30063), the w13 split used by
            C-R7-AP-01 and C-R4-05. Batch 128.
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 7501]); sampler [family + 1, run_seed, arm, 7501].
  GENS      rule fixed before the dev check: the largest of {100, 200, 400, 800} whose projected job CPU
            (64 runs x GENS x measured CPU per generation x 1.1) <= 3600 CPU-s; the job checkpoints between RUNS, so no
            segment clause is needed (one run is far below the 2400 s segment ceiling). If 100 does not fit,
            INFEASIBLE (aborted row + PRODUCTION_CANDIDATE with the measured cost). Outcome recorded at GENS below.
  reader    top1_train: the archive elite with the highest TRAIN8 fitness (ties: lexicographically smaller genome
            bytes); held = its mean clipped final charge per HELD64 seed, in its own arm's world.
  primary   median over the 32 runs of held (cell) >= median (control) - 0.5 * IQR (control). PASS / FAIL only with 32
            runs per arm and oracles clean, else INDETERMINATE.
  oracles   family 4200 run seed 0 of each arm; genomes = its top-16 + planted P_PUSH (every tick action 7: the
            strongest push into reg5, so the sign flip must change the trajectory) + planted P_ABSTAIN (all zeros):
            fused_eq_numpy  the kernel's per-env final charge == b1 NpEncounter stepping the SAME tape in the same
                            world, for EVERY offer of the run (exact), and for the top-16 of EVERY run
            wforge          E4.wforge_replay of the tape (the world of record) == the kernel's per-episode clipped
                            charge for the top-16 on TRAIN8 (exact); the replay uses the arm's own mech
            regime          cell arm: the kernel with the flip disabled (cheat no_regime_flip) changes the final charge
                            on >= 90% of ELIGIBLE envs, >= 1 eligible, where eligible = envs whose NUMPY reference
                            itself differs with and without the flip (the C-R7-AP-03 correction: eligibility is a
                            property of the reference, never of what evolution picked); structural via P_PUSH
            recount         top-16 archive fitness == the numpy recount from the STORED genome bytes, EVERY run (exact)
  report    (not judged) flip windows per episode, abstain share and magnitude of the top1, train fitness, per-arm
            held distribution, and the control-vs-cell difference on the SAME tape (the flip's raw effect).
  not claimed  clause A (the pressure is not the screen's train128_held64 and the tape is not the 200 B baseline);
            any mechanism; the prior ledger was not read.

  INFEASIBILITY RULE (fixed before any row, after the no-rows dev check; scan_job below decides it in committed rows):
            the drawn pressure can only be tested if it can change what the reader measures. scan_job proves BOTH
            directions on w13:
              applied   the flip demonstrably changes the world: NpEncounter register trajectories under period 8
                        differ from period 0 on the same tapes (else the kernel or the mech override is broken and the
                        result is INDETERMINATE, not INFEASIBLE)
              inert     over SCAN_TAPES random tapes x TRAIN8, the clipped final charge is IDENTICAL between the cell
                        world (period 8) and the control world (period 0), and also at period 16
            If ANY charge difference appears, the cell is feasible and C runs the full 32/4/8 experiment specified
            above. If the flip is applied and no charge difference exists, the cell is INFEASIBLE and C reports it with
            its reason and does NOT redraw.
            The structural reason, read from w13 itself: its lin_ops write registers {0, 1, 3, 4}; the yield register is
            5; act_targets = [5], so reg5 is written ONLY by actions. The regime flip negates lin multipliers, so it
            cannot reach reg5, and the charge depends only on reg5 (yield), action cost and step cost. No genome can
            make the flip matter. The no-rows dev check already showed this (cheat eligibility 0 over 18 genomes
            including the all-7s push tape, and identical held charge in both arms); scan_job puts it in rows.

  worker:  job = primordial.cohorts.c.r7_ap04_bitset_w13_regime_numba:job
  dev:     python -m primordial.cohorts.c.r7_ap04_bitset_w13_regime_numba dev   (no rows)
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import pathlib
import sys
import time

import numpy as np
from numba import njit, prange

from primordial.qd import e4_run as E4
from primordial.soup.b1.common import M, init_regs, stream_state
from primordial.soup.b1.np_world import NpEncounter

EXP = "C-R7-AP-04-bitset-w13-regime-switching-numba-fused"
PREDICATE_ID = "C-R7-AP-04"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
CELL = {"representation": "bitset", "world": "w13", "pressure": "regime_switching", "substrate": "numba_fused",
        "channel": "none"}
CELL_CTRL = dict(CELL, pressure="regime_period_0_control")
GS = 13
SPEC = E4.Spec(GS)
MECH0 = SPEC.mech
GEN_PERIODS = (8, 16, 32, 64)             # wforge world.py: 8 << r.below(4)
FLIP_PERIOD = 8                           # smallest emitted period with >= 2 flip windows in T = 32
MECH_FLIP = dataclasses.replace(MECH0, regime_period=FLIP_PERIOD)
TRAIN = np.asarray(E4.SEEDS, np.int64)
HELD = np.arange(30000, 30064, dtype=np.int64)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
BATCH, TOP = 128, 16
GLEN = SPEC.glen                          # 32
PORT = 6392
STREAM_TAG = 7501
GENS_CHOICES = (100, 200, 400, 800)
CPU_CAP = 3600.0
GENS = 400      # set from the no-rows dev check by the GENS rule
ARMS = {"cell": (0, MECH_FLIP, CELL), "control": (1, MECH0, CELL_CTRL)}


class _SpecView:
    """E4.wforge_replay needs .mech, .wid and .S; the arm supplies its own mech."""

    def __init__(self, mech):
        self.mech, self.wid, self.S, self.T, self.W = mech, SPEC.wid, mech.n_slots, mech.horizon, mech.act_width


@njit(parallel=True, nogil=True, boundscheck=False, cache=True)
def _tape_kernel(T, R, S, W, delay, regime_period, stoch_rate, act_cost, step_cost, yield_reg, ylo, yhi, yield_amt,
                 lin, tgts, regs0, charge0, st_stoch0, acts, genome_of_env, no_flip, fit, done_tick):
    """B1 world semantics stepped from an explicit action tape (b6/fused's step order, no brain)."""
    n = regs0.shape[0]
    L = lin.shape[0]
    D1 = delay + 1
    C64 = np.uint64(0x2545F4914F6CDD1D)
    for e in prange(n):
        p = genome_of_env[e]
        reg = regs0[e].copy()
        charge = charge0[e].copy()
        alive = np.ones(S, dtype=np.bool_)
        pend = np.zeros((D1, R), dtype=np.int64)
        st = st_stoch0[e]
        tick = 0
        while tick < T:
            ps = (tick + delay) % D1
            for s in range(S):
                if alive[s]:
                    m8 = 0
                    for i in range(W):
                        m8 += acts[p, tick, s, i] % 8
                    cost = m8 * act_cost
                    if cost <= charge[s]:
                        charge[s] -= cost
                    for i in range(W):
                        pend[ps, tgts[i]] += (acts[p, tick, s, i] % 8) * 251
            land = tick % D1
            for rr in range(R):
                reg[rr] = (reg[rr] + pend[land, rr]) % M
                pend[land, rr] = 0
            flip = (not no_flip) and regime_period > 0 and (tick // regime_period) % 2 == 1
            for o in range(L):
                a = lin[o, 1]
                if flip:
                    a = (M - a) % M
                reg[lin[o, 0]] = (a * reg[lin[o, 2]] + lin[o, 3] * reg[lin[o, 4]] + lin[o, 5]) % M
            if stoch_rate > 0:
                st ^= st << np.uint64(13)
                st ^= st >> np.uint64(7)
                st ^= st << np.uint64(17)
                o1 = st * C64
                if o1 % np.uint64(stoch_rate) == 0:
                    st ^= st << np.uint64(13)
                    st ^= st >> np.uint64(7)
                    st ^= st << np.uint64(17)
                    o2 = st * C64
                    st ^= st << np.uint64(13)
                    st ^= st >> np.uint64(7)
                    st ^= st << np.uint64(17)
                    o3 = st * C64
                    reg[np.int64(o3 % np.uint64(R))] = np.int64(o2 % np.uint64(M))
            yv = reg[yield_reg]
            if ylo < yhi:
                inw = ylo <= yv and yv < yhi
            else:
                inw = yv >= ylo or yv < yhi
            nl = 0
            for s in range(S):
                if alive[s]:
                    nl += 1
            share = yield_amt // nl if nl > 0 else 0
            any_alive = False
            for s in range(S):
                if alive[s]:
                    charge[s] -= step_cost
                    if inw:
                        charge[s] += share
                    if charge[s] <= 0:
                        alive[s] = False
                    else:
                        any_alive = True
            tick += 1
            if not any_alive:
                break
        done_tick[e] = tick
        tot = 0
        for s in range(S):
            if charge[s] > 0:
                tot += charge[s]
        fit[e] = tot


def kernel_charge(B, seeds, mech, no_flip=False):
    """-> (per-env clipped charge sum [P, k], done_tick [P, k]) from the packed tapes B."""
    acts = SPEC.unpack(np.ascontiguousarray(B)).astype(np.uint8)
    P, k = len(B), len(seeds)
    n = P * k
    env_seeds = np.tile(np.asarray(seeds, np.int64), P)
    regs0 = init_regs(mech, SPEC.wid, env_seeds).astype(np.int64)
    charge0 = np.full((n, mech.n_slots), mech.start_charge, np.int64)
    st0 = np.array([stream_state("stoch", SPEC.wid, int(s)) for s in env_seeds], dtype=np.uint64)
    lin = np.array([[int(v) for v in op] for op in mech.lin_ops], np.int64)
    fit = np.zeros(n, np.int64)
    dt = np.zeros(n, np.int64)
    _tape_kernel(mech.horizon, mech.n_regs, mech.n_slots, mech.act_width, mech.delay, mech.regime_period,
                 mech.stoch_rate, mech.act_cost, mech.step_cost, mech.yield_reg, mech.yield_lo, mech.yield_hi,
                 mech.yield_amt, lin, np.array(list(mech.act_targets), np.int64), regs0, charge0, st0,
                 acts, np.repeat(np.arange(P), k).astype(np.int64), bool(no_flip), fit, dt)
    return fit.reshape(P, k), dt.reshape(P, k)


def numpy_charge(B, seeds, mech, cheat=""):
    """b1 NpEncounter stepping the same tape -> clipped charge sum [P, k] (the exactness reference)."""
    acts = SPEC.unpack(np.ascontiguousarray(B)).astype(np.int32)
    P, k = len(B), len(seeds)
    w = NpEncounter(mech, SPEC.wid, cheat=cheat, with_obs=False)
    w.reset(np.tile(np.asarray(seeds, np.int64), P))
    A = np.repeat(acts, k, axis=0)
    for t in range(mech.horizon):
        _, _, done = w.step(A[:, t])
        if done.all():
            break
    return np.clip(w.charge, 0, None).sum(1).reshape(P, k)


def planted():
    """P_PUSH: every tick pushes 7 (the flip must change the trajectory). P_ABSTAIN: all zeros."""
    push = SPEC.pack(np.full((1, SPEC.T, SPEC.S, SPEC.W), 7, np.uint8))[0]
    abst = SPEC.pack(np.zeros((1, SPEC.T, SPEC.S, SPEC.W), np.uint8))[0]
    return np.stack([push, abst])


def oracles(B_top, mech, arm) -> dict:
    G = np.concatenate([B_top, planted()])
    ker = kernel_charge(G, TRAIN, mech)[0]
    ref = numpy_charge(G, TRAIN, mech)
    o = {"arm": arm, "envs": int(ker.size), "fused_eq_numpy_mismatched": int((ker != ref).sum())}
    bad = 0
    view = _SpecView(mech)
    tapes = SPEC.unpack(np.ascontiguousarray(G))
    for p in range(len(G)):
        for j, sd in enumerate(TRAIN):
            _, ch = E4.wforge_replay(view, tapes[p], int(sd))
            bad += int(int(ch.sum()) != int(ker[p, j]))
    o["wforge_mismatched"] = bad
    if arm == "cell":
        ker_c = kernel_charge(G, TRAIN, mech, no_flip=True)[0]
        ref_c = numpy_charge(G, TRAIN, mech, cheat="no_regime_flip")
        el = ref_c != ref
        caught = int(((ker_c != ref) & el).sum())
        o["regime"] = {"eligible": int(el.sum()), "caught": caught,
                       "share": round(caught / int(el.sum()), 4) if el.any() else 0.0}
    else:
        o["regime"] = "EXEMPT by rule (the control arm has no flip to disable)"
    ok = o["fused_eq_numpy_mismatched"] == 0 and o["wforge_mismatched"] == 0
    if arm == "cell":
        ok = ok and o["regime"]["eligible"] > 0 and o["regime"]["share"] >= 0.9
    o["ok"] = bool(ok)
    return o


def run(r, family, rs, arm, gens):
    from primordial.qd.archive import LuaArchive
    ai, mech, _ = ARMS[arm]
    rng = np.random.Generator(np.random.PCG64([family, rs, ai, STREAM_TAG]))
    arch = LuaArchive(r, f"c-r7-ap04-{family}-{rs}-{ai}", GLEN, sampler_seed=[family + 1, rs, ai, STREAM_TAG])
    arch.clear()
    c0, t0 = time.process_time(), time.perf_counter()
    offers = offer_bad = 0
    audit = family == FAMILIES[0] and rs == 0
    for _ in range(gens):
        par = arch.sample(BATCH)
        if len(par) == 0:
            G = E4.init_genomes(rng, SPEC, BATCH)
        else:
            G = E4.mutate(rng, SPEC, SPEC.unpack(np.asarray(par, np.uint8)))
        B = SPEC.pack(G)
        fit = kernel_charge(B, TRAIN, mech)[0].sum(1)
        if audit:
            offers += int(fit.size)
            offer_bad += int((numpy_charge(B, TRAIN, mech).sum(1) != fit).sum())
        arch.insert(E4.descriptor(G), fit.astype(np.int32), B, np.zeros((BATCH, 2), np.uint32))
    loop_cpu, loop_wall = time.process_time() - c0, time.perf_counter() - t0
    el = arch.dump()
    arch.clear()
    order = sorted(el.values(), key=lambda v: (-v[0], v[1]))
    top = np.frombuffer(b"".join(v[1] for v in order[:TOP]), np.uint8).reshape(-1, GLEN)
    recount = kernel_charge(top, TRAIN, mech)[0].sum(1)
    recount_bad = int(sum(int(x) != int(v[0]) for x, v in zip(recount, order[:TOP])))
    held = kernel_charge(top[:1], HELD, mech)[0]
    held_other = kernel_charge(top[:1], HELD, ARMS["control" if arm == "cell" else "cell"][1])[0]
    g1 = SPEC.unpack(top[:1])
    x = (g1 % 8).astype(np.int64)
    info = {"gens_done": gens, "genomes_evaluated": gens * BATCH, "loop_cpu_s": round(loop_cpu, 4),
            "loop_wall_s": round(loop_wall, 3), "archive_cells": len(el), "train_fit_top1": int(order[0][0]),
            "train_per_seed_top1": float(order[0][0] / len(TRAIN)),
            "held_per_seed_top1": float(held.mean()),
            "held_per_seed_top1_other_arm_world": float(held_other.mean()),
            "top1_abstain_share": float((x.sum(-1) == 0).mean()), "top1_magnitude": float(x.mean() / 7.0),
            "top1_sha256": hashlib.sha256(top[0].tobytes()).hexdigest(),
            "recount_mismatched_top16": recount_bad, "offers_audited": offers, "offers_mismatched": offer_bad}
    return info, top


def score(held, control) -> dict:
    q = np.percentile(held, [25, 50, 75])
    qc = np.percentile(control, [25, 50, 75])
    bar = float(qc[1] - 0.5 * (qc[2] - qc[0]))
    return {"held_median_cell": float(q[1]), "iqr_cell": float(q[2] - q[0]), "held_median_control": float(qc[1]),
            "iqr_control": float(qc[2] - qc[0]), "bar": bar, "parity": bool(q[1] >= bar)}


def job(ctx, gens: int = GENS, port: int = PORT, exp_id: str = EXP):
    import redis
    r = redis.Redis(host="127.0.0.1", port=port)
    todo = [(f, rs, arm) for f in FAMILIES for rs in range(RUNS_PER_FAMILY) for arm in ("control", "cell")]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": []}, "clean": True, "ref": False}
    if not st["ref"]:
        ctx.emit({"kind": "reference", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "gens": gens, "batch": BATCH,
                  "genome_bytes": GLEN, "flip_period": FLIP_PERIOD, "generator_periods": list(GEN_PERIODS),
                  "horizon": int(MECH0.horizon), "flip_windows_in_T": int(sum(
                      1 for t in range(MECH0.horizon) if (t // FLIP_PERIOD) % 2 == 1)),
                  "train_seeds": TRAIN.tolist(), "held_seeds": [int(HELD[0]), int(HELD[-1])],
                  "status": "control", "ts": round(time.time(), 3)})
        st["ref"] = True
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        fam, rs, arm = todo[st["next"]]
        ai, mech, cell = ARMS[arm]
        t0, c0 = time.perf_counter(), time.process_time()
        info, top = run(r, fam, rs, arm, gens)
        ok = info["recount_mismatched_top16"] == 0 and info["offers_mismatched"] == 0
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
               "regime_period": int(mech.regime_period), "genome_bytes": GLEN, "reader": "top1_train", **info,
               "status": "record" if arm == "cell" else "control"}
        if fam == FAMILIES[0] and rs == 0:
            o = oracles(top, mech, arm)
            row["oracles"] = o
            ok = ok and o["ok"]
        st["clean"] = bool(st["clean"] and ok)
        row["cpu_s"], row["wall_s"] = round(time.process_time() - c0, 3), round(time.perf_counter() - t0, 3)
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(info["held_per_seed_top1"])
        ctx.emit(row)
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    sc = score(st["held"]["cell"], st["held"]["control"])
    n = {a: len(st["held"][a]) for a in st["held"]}
    full = all(v == len(FAMILIES) * RUNS_PER_FAMILY for v in n.values())
    primary = "INDETERMINATE" if not (st["clean"] and full) else ("PASS" if sc["parity"] else "FAIL")
    ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL, "runs_total": n["cell"],
              "rng_family_count": len(FAMILIES), "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
              "n_per_family": {str(f): RUNS_PER_FAMILY for f in FAMILIES}, "gens": gens, "flip_period": FLIP_PERIOD,
              **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in sc.items()},
              "oracle_clean": st["clean"], "primary": primary,
              "clause_a": "none: the pressure is not train128_held64 and a 32 B tape is not the 200 B baseline",
              "status": "record" if st["clean"] else "cheat", "ts": round(time.time(), 3)})


SCAN_TAPES = 512
SCAN_STREAM = [4200, STREAM_TAG]


def _regs_trace(B, seeds, mech):
    """NpEncounter register log for the same tapes -> (log_regs [T, n, R], clipped charge sum [n])."""
    acts = SPEC.unpack(np.ascontiguousarray(B)).astype(np.int32)
    n = len(B) * len(seeds)
    w = NpEncounter(mech, SPEC.wid, record=np.arange(n), with_obs=False)
    w.reset(np.tile(np.asarray(seeds, np.int64), len(B)))
    A = np.repeat(acts, len(seeds), axis=0)
    for t in range(mech.horizon):
        _, _, done = w.step(A[:, t])
        if done.all():
            break
    return w.log_regs.copy(), np.clip(w.charge, 0, None).sum(1)


def scan_job(ctx, tapes: int = SCAN_TAPES, exp_id: str = EXP):
    """The INFEASIBILITY RULE in committed rows: is the drawn flip applied, and can it change the reader?"""
    m16 = dataclasses.replace(MECH0, regime_period=16)
    dests = sorted({int(op[0]) for op in MECH0.lin_ops})
    ctx.emit({"kind": "reference", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "world": "w13",
              "lin_ops": [[int(v) for v in op] for op in MECH0.lin_ops], "lin_destinations": dests,
              "yield_reg": int(MECH0.yield_reg), "act_targets": [int(t) for t in MECH0.act_targets],
              "yield_reg_written_only_by_actions": int(MECH0.yield_reg) not in dests,
              "generator_periods": list(GEN_PERIODS), "flip_period": FLIP_PERIOD, "horizon": int(MECH0.horizon),
              "flip_windows_in_T": int(sum(1 for t in range(MECH0.horizon) if (t // FLIP_PERIOD) % 2 == 1)),
              "scan_tapes": tapes, "train_seeds": TRAIN.tolist(), "status": "control", "ts": round(time.time(), 3)})
    rng = np.random.Generator(np.random.PCG64(SCAN_STREAM))
    B = SPEC.pack(E4.init_genomes(rng, SPEC, tapes))
    r0, c0 = _regs_trace(B[:4], TRAIN, MECH0)
    r8, c8 = _regs_trace(B[:4], TRAIN, MECH_FLIP)
    d = r0 != r8
    applied = {"kind": "flip_applied", "exp_id": exp_id, "tapes": 4, "envs": int(c0.size),
               "ticks_with_a_register_difference": int(d.any(axis=(1, 2)).sum()), "ticks": int(r0.shape[0]),
               "registers_that_ever_differ": sorted(np.unique(np.nonzero(d)[2]).tolist()),
               "charge_identical_on_those_envs": bool(np.array_equal(c0, c8)),
               "status": "control", "ts": round(time.time(), 3)}
    applied["flip_is_applied"] = bool(d.any())
    ctx.emit(applied)
    ker_ctrl = kernel_charge(B, TRAIN, MECH0)[0]
    scans = []
    for name, mech in (("period_8", MECH_FLIP), ("period_16", m16)):
        ker_f = kernel_charge(B, TRAIN, mech)[0]
        npy_f = numpy_charge(B, TRAIN, mech)
        row = {"kind": "scan", "exp_id": exp_id, "period": int(mech.regime_period), "tapes": tapes,
               "envs": int(ker_f.size), "charge_differences_vs_control": int((ker_ctrl != ker_f).sum()),
               "kernel_eq_numpy_mismatched": int((ker_f != npy_f).sum()), "status": "control",
               "ts": round(time.time(), 3)}
        scans.append(row)
        ctx.emit(row)
    exact = all(s["kernel_eq_numpy_mismatched"] == 0 for s in scans)
    inert = all(s["charge_differences_vs_control"] == 0 for s in scans)
    if not exact:
        primary, reason = "INDETERMINATE", "the numba kernel and the numpy reference disagree; no claim about the cell"
    elif not applied["flip_is_applied"]:
        primary, reason = "INDETERMINATE", "the flip did not change any register: the mech override or the kernel is broken"
    elif inert:
        primary, reason = "INFEASIBLE", (
            "regime_switching cannot bind on w13 for ANY genome: the flip negates lin multipliers, w13 lin_ops write "
            "registers %s, the yield register is %d and act_targets is %s, so reg %d is written only by actions and the "
            "charge (yield + action cost + step cost) is untouched. Verified: the flip changes registers %s on %d of %d "
            "ticks while the clipped charge is identical over %d tapes x %d train seeds at BOTH generator periods that "
            "can flip within T (8 and 16)." % (dests, int(MECH0.yield_reg), [int(t) for t in MECH0.act_targets],
                                               int(MECH0.yield_reg), applied["registers_that_ever_differ"],
                                               applied["ticks_with_a_register_difference"], applied["ticks"],
                                               tapes, len(TRAIN)))
    else:
        primary, reason = "FEASIBLE_RUN_REQUIRED", "a charge difference exists, so the full 32/4/8 experiment is warranted"
    ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL, "primary": primary,
              "reason": reason, "flip_is_applied": applied["flip_is_applied"], "kernel_eq_numpy": exact,
              "charge_inert": inert, "scans": scans, "evidence_class": "OBSERVATION",
              "clause_a": "none claimed", "no_redraw": "the drawn cell is reported, never replaced",
              "status": "aborted", "ts": round(time.time(), 3)})


def dev(gens: int = 5) -> None:
    """No rows: kernel == numpy == wforge, structural regime eligibility, CPU per generation, GENS by the rule."""
    import redis
    r = redis.Redis(host="127.0.0.1", port=PORT)
    rng = np.random.Generator(np.random.PCG64(77))
    G = SPEC.pack(E4.init_genomes(rng, SPEC, TOP))
    out = {"flip_period": FLIP_PERIOD, "generator_periods": list(GEN_PERIODS), "genome_bytes": GLEN,
           "flip_windows_in_T": int(sum(1 for t in range(MECH0.horizon) if (t // FLIP_PERIOD) % 2 == 1))}
    for arm in ("cell", "control"):
        _, mech, _ = ARMS[arm]
        out["oracles_" + arm] = oracles(G, mech, arm)
    kb = SPEC.pack(E4.init_genomes(rng, SPEC, BATCH))
    kernel_charge(kb, TRAIN, MECH_FLIP)                      # compile
    c = time.process_time()
    for _ in range(gens):
        kb = SPEC.pack(E4.mutate(rng, SPEC, SPEC.unpack(kb)))
        kernel_charge(kb, TRAIN, MECH_FLIP)
    per_gen = (time.process_time() - c) / gens
    out["cpu_s_per_gen"] = round(per_gen, 5)
    proj = {str(Gn): round(64 * Gn * per_gen * 1.1, 1) for Gn in GENS_CHOICES}
    fits = [Gn for Gn in GENS_CHOICES if 64 * Gn * per_gen * 1.1 <= CPU_CAP]
    out["projected_job_cpu_s"] = proj
    out["gens_by_rule"] = max(fits) if fits else "INFEASIBLE"
    c = time.process_time()
    info, _ = run(r, 4200, 0, "cell", 3)
    out["run3_cpu_s"] = round(time.process_time() - c, 3)
    out["run3_info"] = info
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dev(int(sys.argv[2]) if len(sys.argv) > 2 else 5) if sys.argv[1] == "dev" else None
