"""C-R7-AP-01 (ANTI_PRIOR, cell assigned by code): affine_plastic / w13 / held_out_seeds / numpy / metered_stream
(anti_prior.assign exp_id C-R7-AP-01, round 7).

The experimenter received only the cell; the prior and the arm are unread. No definition of this cell existed; the
definitions below are fixed before any run.

  world     w13 (E4.Spec(13)), the round 4 screen's SURVIVED world. D=5, S=1, W=1, T=32. Observation (after obs_perm)
            = [reg0, reg1, charge // 32 (max 15), reg5, reg6], world corruption rate 16 (the world's own, both arms).
            An action x adds 251 * (x % 8) to reg5 one tick later; reg5 in [14152, 16200) yields +10 charge per tick.
            Fitness = summed clipped final charge over the selection seeds (E7.rollout's rule).
  brain     affine_plastic (C7b's representation: an affine map whose CONSTANT adapts on surprise, as C-R5-01).
            Genome 16 bytes: [s, k, a_lo, a_hi, c_lo, c_hi, 0, 0] + codebook C[8] (lane E's E7 codebook, W = 1).
              s = byte % 5 (one observed feature), k = byte % 5 (hex digits read, most significant first)
              xe  = delivered feature value masked to its top k digits (k = 0 or not delivered: 0)
              idx = ((a * xe + c + 8192 * shift) mod 65536) >> 13;  action = C[idx]
              plastic: over each window of 8 ticks, support = yielding live ticks / live ticks (yield = reg5 in the
              window after the step); support < SURPRISE_SUPPORT (0.5, brain.affine_plastic) with >= 1 live tick is
              a surprise and refits the constant: shift = (shift + 1) & 7.
            Init: bytes uniform, C[0] = 0 (E7). Mutation (C-R5-01's field rule): each of s, k, a, c with p 0.2
            (s, k: +-1 mod 5; a, c: half uniform 16-bit, half +- 2^j, j uniform in 0..15); each C entry with p 1/8
            replaced uniform in [0, 16) (E7's rate 1 / (A * W)).
  channel   metered_stream (C-R6-01's rule, applied to THIS brain's observation): per live slot-tick ledger += CREDIT;
            cost = ALPHA * 4 * k; if ledger >= cost the k digits are delivered and ledger -= cost, else silence (0).
            ALPHA = 2; CREDIT = ALPHA * 4 * 2 = 16 (the stream pays for half of the reader's 4-digit observation per
            tick, as C-R6-01 paid for half of its 20-digit observation), START = CREDIT. Disclosed: C-R6-01's constant
            (CREDIT 80) can never bind a <= 4-digit reader; the half-observation rule is kept, the constant follows it.
            Delivery never costs world charge.
  substrate numpy: world (lane B's NpEncounter), ledger, brain, all vectorised numpy int64. Archive: E's LuaArchive
            (seeded sampler) on lane C's Redis :6392.
  pressure  held_out_seeds (C-R2-09's definition; the w13 screen's train8 cell): selection sees TRAIN8 (9100..9107);
            the score is HELD64 (30000..30063).
  arms      cell     selection on TRAIN8, scored on HELD64
            control  the pressure removed: selection IN-SAMPLE on HELD64, scored on HELD64
            Same GA, sampler streams, GENS, batch 128 and channel in both arms.
  search    MAP-Elites: LuaArchive, batch 128 per generation; descriptor (abstain share, action magnitude) on the
            selection seeds, E4.GRID x E4.GRID (C-R6-01's descriptor).
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 7101]); sampler [family + 1, run_seed, arm, 7101]. Each
            (family, run_seed) runs control first, then cell.
  GENS      rule fixed before the no-rows timing check: the largest of {100, 200, 400, 800} whose projected job CPU
            (32 cell runs + 32 control runs, CPU per generation measured per arm, x 1.1 for the reader and oracles)
            <= 7200 CPU-s; if 100 does not fit, the cell is INFEASIBLE this round (aborted row + PRODUCTION_CANDIDATE
            with the measured cost). Outcome recorded at GENS below.
  reader    top1_train: the archive elite with the highest selection fitness (ties: smaller genome bytes);
            held = its HELD64 mean per-seed final charge.
  primary   median over the 32 runs of held (cell) >= median (control) - 0.5 * IQR (control). PASS / FAIL only with
            32 runs per arm and oracles clean, else INDETERMINATE.
  report    (not judged) FLOOR 166.46875 (w13 gate_in|HOLD) and progress above floor; held with the stream forced
            silent; delivered share; refits; train - held gap; digits read; genome bytes.
  oracles   family 4200 run seed 0 of each arm, top-16 elites on HELD8 (E7.HELD8):
            world    NpEncounter trace hash + clipped charge == wforge replay of the recorded actions: honest 0
                     failing; skip_lin cheat >= 14/16 failing
            brain    scalar plain-int reference of the closed-loop policy (ledger, delivery, mask, idx, plastic shift)
                     on the recorded observations and reg5 == recorded actions and deliveries: honest 0 mismatched
                     episodes; cheat skip_plastic changes the recorded actions on >= 90% of ELIGIBLE episodes
                     (the reference refit >= 1 time), >= 1 eligible
            meter    cheat free_stream (every live tick delivered) changes the delivery table on >= 90% of eligible
                     episodes (the honest run had >= 1 undelivered live tick), >= 1 eligible
            recount  EVERY run: archive fitness of the top-16 == rollout from the STORED genome bytes (exact)
  not claimed  clause A (an ANTI_PRIOR row); any mechanism; the prior ledger was not read.

  worker:  job = primordial.cohorts.c.r7_ap01_affine_plastic_w13_heldout_metered:job
  dev:     python -m primordial.cohorts.c.r7_ap01_affine_plastic_w13_heldout_metered dev   (no rows)
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time

import numpy as np

from primordial.brain.affine_plastic import SURPRISE_SUPPORT
from primordial.metric import floors as F
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.soup.b1.np_world import NpEncounter

EXP = "C-R7-AP-01-affine-plastic-w13-heldout-metered"
PREDICATE_ID = "C-R7-AP-01"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
CELL = {"representation": "affine_plastic", "world": "w13", "pressure": "held_out_seeds", "substrate": "numpy",
        "channel": "metered_stream"}
CELL_CTRL = dict(CELL, pressure="in_sample_heldout_control")
GS, A, BATCH, TOP = 13, 8, 128, 16
AB, GLEN = 8, 16
ALPHA = 2
CREDIT = ALPHA * 4 * 2
START = CREDIT
WINDOW = 8
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
PORT = 6392
STREAM_TAG = 7101
FLOOR = 166.46875
GENS_CHOICES = (100, 200, 400, 800)
CPU_CAP = 7200.0
# No-rows dev check (3 gens after warm-up per arm, random genomes): cell 0.03125 CPU-s / gen, control 0.19792 CPU-s / gen
# -> projected job CPU 100: 806.7, 200: 1613.4, 400: 3226.7, 800: 6453.4 (cap 7200) -> by the rule GENS 800. Disclosed:
# process_time ticks at 15.6 ms on this host, so the per-gen estimate is coarse; the rule is applied as measured.
# Oracles on 16 random genomes: world 0/16, skip_lin 16/16, brain 0 mismatched, skip_plastic 128/128, free_stream 48/48.
GENS = 800

SPEC = E4.Spec(GS)
MECH = SPEC.mech
D, S, W, T = len(MECH.obs_perm), MECH.n_slots, MECH.act_width, MECH.horizon
assert S == 1 and W == 1


def selection_seeds(arm: str) -> np.ndarray:
    return np.asarray(F.TRAIN8 if arm == "cell" else F.HELD64, np.int64)


def in_window(v):
    lo, hi = MECH.yield_lo, MECH.yield_hi
    return ((lo <= v) & (v < hi)) if lo < hi else ((v >= lo) | (v < hi))


# ------------------------------------------------------------------ genome

def decode(B):
    B = np.asarray(B, np.uint8)
    s = B[:, 0].astype(np.int64) % D
    k = B[:, 1].astype(np.int64) % 5
    a = B[:, 2].astype(np.int64) | (B[:, 3].astype(np.int64) << 8)
    c = B[:, 4].astype(np.int64) | (B[:, 5].astype(np.int64) << 8)
    return s, k, a, c, B[:, AB:AB + A].astype(np.int64)


def digit_mask(k):
    return (0xFFFF << (16 - 4 * np.asarray(k, np.int64))) & 0xFFFF


def init(rng, P):
    B = rng.integers(0, 256, (P, GLEN), dtype=np.uint8)
    B[:, 6:AB] = 0
    B[:, AB:] = rng.integers(0, 16, (P, A), dtype=np.uint8)
    B[:, AB] = 0
    return B


def mutate(rng, B):
    B = B.copy()
    P = len(B)
    s, k, a, c, _ = decode(B)
    m = rng.random((P, 4)) < 0.2
    pm = rng.choice(np.array([-1, 1]), (P, 4))
    coin = rng.random((P, 2)) < 0.5
    step = pm[:, 2:] * (1 << rng.integers(0, 16, (P, 2)))
    uni = rng.integers(0, 1 << 16, (P, 2))
    s2 = np.where(m[:, 0], (s + pm[:, 0]) % D, s)
    k2 = np.where(m[:, 1], (k + pm[:, 1]) % 5, k)
    ac = np.stack([a, c], 1)
    ac2 = np.where(m[:, 2:], np.where(coin, uni, (ac + step) & 0xFFFF), ac)
    B[:, 0], B[:, 1] = s2.astype(np.uint8), k2.astype(np.uint8)
    B[:, 2], B[:, 3] = (ac2[:, 0] & 255).astype(np.uint8), (ac2[:, 0] >> 8).astype(np.uint8)
    B[:, 4], B[:, 5] = (ac2[:, 1] & 255).astype(np.uint8), (ac2[:, 1] >> 8).astype(np.uint8)
    cm = rng.random((P, A)) < 1.0 / (A * W)
    B[:, AB:] = np.where(cm, rng.integers(0, 16, (P, A), dtype=np.uint8), B[:, AB:])
    return B


# ------------------------------------------------------------------ closed loop

def rollout(B, seeds, meter="metered", world_cheat="", skip_plastic=False, log=False) -> dict:
    """B uint8 [P, GLEN] over seeds [k]; env index p * k + e. meter: metered | free | silent."""
    P, kk = len(B), len(seeds)
    n = P * kk
    s, k, a, c, C = decode(B)
    s, k, a, c = (np.repeat(x, kk) for x in (s, k, a, c))
    C = np.repeat(C, kk, axis=0)
    cost = ALPHA * 4 * k
    msk = digit_mask(k)
    w = NpEncounter(MECH, SPEC.wid, record=np.arange(n) if log else None, cheat=world_cheat, with_obs=True)
    obs = w.reset(np.tile(np.asarray(seeds, np.int64), P))
    env = np.arange(n)
    led = np.full(n, START, np.int64)
    shift = np.zeros(n, np.int64)
    win_live, win_y = np.zeros(n, np.int64), np.zeros(n, np.int64)
    refits, abst, mag, cnt, dlv, yl = (np.zeros(n, np.int64) for _ in range(6))
    L = {"acts": np.zeros((T, n, S, W), np.int64), "obs": np.zeros((T, n, D), np.int64),
         "reg5": np.zeros((T, n), np.int64), "live": np.zeros((T, n), bool), "deliver": np.zeros((T, n), bool)} \
        if log else None
    for t in range(T):
        live = (w.alive & ~w.done[:, None]).reshape(n)
        if meter == "metered":
            led = led + np.where(live, CREDIT, 0)
            deliver = live & (led >= cost)
            led = led - np.where(deliver, cost, 0)
        elif meter == "free":
            deliver = live.copy()
        else:
            deliver = np.zeros(n, bool)
        o = obs.reshape(n, D)
        xe = np.where(deliver, o[env, s] & msk, 0)
        idx = ((a * xe + c + 8192 * shift) & 0xFFFF) >> 13
        act = C[env, idx]
        x = act % 8
        abst += (x == 0) & live
        mag += x * live
        cnt += live
        dlv += deliver & live
        if log:
            L["acts"][t, :, 0, 0], L["obs"][t], L["live"][t], L["deliver"][t] = act, o, live, deliver
        obs, _, done = w.step(act.reshape(n, S, W))
        v = w.regs[:, MECH.yield_reg]
        if log:
            L["reg5"][t] = v
        y = live & in_window(v)
        yl += y
        win_live += live
        win_y += y
        if (t + 1) % WINDOW == 0:
            sur = (win_live > 0) & (win_y < win_live * SURPRISE_SUPPORT)
            if not skip_plastic:
                shift = (shift + sur) & 7
                refits += sur
            win_live[:] = 0
            win_y[:] = 0
        if done.all():
            break
    fit = np.clip(w.charge, 0, None).sum(1).reshape(P, kk).sum(1).astype(np.int64)
    tot = np.maximum(cnt.reshape(P, kk).sum(1), 1)
    ab = abst.reshape(P, kk).sum(1) / tot
    mg = mag.reshape(P, kk).sum(1) / (tot * W * 7)
    cells = (np.rint(ab * 32) * E4.GRID + np.rint(np.clip(mg, 0, 1) * 32)).astype(np.uint32)
    return {"fit": fit, "cells": cells, "w": w, "L": L, "delivered_share": dlv.reshape(P, kk).sum(1) / tot,
            "refits": refits.reshape(P, kk).sum(1) / kk, "yield_share": yl.reshape(P, kk).sum(1) / tot}


def ref_episode(g, obs, reg5, live, meter="metered"):
    """Scalar plain-int reference for one genome on one recorded episode -> (actions [T], deliver [T], refits)."""
    s, k, a, c = int(g[0]) % D, int(g[1]) % 5, int(g[2]) | (int(g[3]) << 8), int(g[4]) | (int(g[5]) << 8)
    C = [int(x) for x in g[AB:AB + A]]
    msk = (0xFFFF << (16 - 4 * k)) & 0xFFFF
    led, shift, wl, wy, refits = START, 0, 0, 0, 0
    acts, dl = [0] * T, [False] * T
    lo, hi = MECH.yield_lo, MECH.yield_hi
    for t in range(T):
        lv = bool(live[t])
        if meter == "metered":
            if lv:
                led += CREDIT
            d = lv and led >= ALPHA * 4 * k
            if d:
                led -= ALPHA * 4 * k
        elif meter == "free":
            d = lv
        else:
            d = False
        xe = (int(obs[t][s]) & msk) if d else 0
        idx = ((a * xe + c + 8192 * shift) & 0xFFFF) >> 13
        acts[t], dl[t] = C[idx], d
        v = int(reg5[t])
        y = lv and ((lo <= v < hi) if lo < hi else (v >= lo or v < hi))
        wl += int(lv)
        wy += int(y)
        if (t + 1) % WINDOW == 0:
            if wl > 0 and wy < wl * SURPRISE_SUPPORT:
                shift, refits = (shift + 1) & 7, refits + 1
            wl = wy = 0
    return acts, dl, refits


def _T_of(w, e):
    return int(w.done_tick[e]) if int(w.done_tick[e]) > 0 else T


def world_oracle(B, seeds, meter, world_cheat=""):
    o = rollout(B, seeds, meter, world_cheat=world_cheat, log=True)
    hashes = [h.decode() for h in o["w"].trace_hashes()]
    kk, P = len(seeds), len(B)
    ep = np.clip(o["w"].charge, 0, None)
    bad = np.zeros(P, bool)
    for e in range(P * kk):
        h, ch = E4.wforge_replay(SPEC, o["L"]["acts"][:, e], int(seeds[e % kk]))
        bad[e // kk] |= (h != hashes[e]) or not np.array_equal(ch, ep[e])
    return {"elites": P, "elites_failing": int(bad.sum())}


def brain_oracle(B, seeds, meter) -> dict:
    hon = rollout(B, seeds, meter, log=True)
    chp = rollout(B, seeds, meter, skip_plastic=True, log=True)
    L, Lc, w = hon["L"], chp["L"], hon["w"]
    kk, P = len(seeds), len(B)
    bad = elig = caught = 0
    for e in range(P * kk):
        n_t = _T_of(w, e)
        acts, dl, refits = ref_episode(B[e // kk], L["obs"][:, e], L["reg5"][:, e], L["live"][:, e], meter)
        rec_a = L["acts"][:n_t, e, 0, 0]
        bad += int(not (np.array_equal(np.array(acts[:n_t]), rec_a)
                        and np.array_equal(np.array(dl[:n_t]), L["deliver"][:n_t, e])))
        if refits > 0:
            elig += 1
            m = min(n_t, _T_of(chp["w"], e))
            caught += int(not np.array_equal(Lc["acts"][:m, e, 0, 0], rec_a[:m]) or _T_of(chp["w"], e) != n_t)
    return {"episodes": P * kk, "honest_mismatched_episodes": bad, "skip_plastic_eligible_episodes": elig,
            "skip_plastic_share": round(caught / elig, 4) if elig else 0.0}


def meter_oracle(B, seeds) -> dict:
    hon = rollout(B, seeds, "metered", log=True)
    L = hon["L"]
    kk, P = len(seeds), len(B)
    elig = caught = 0
    for e in range(P * kk):
        n_t = _T_of(hon["w"], e)
        silent = L["live"][:n_t, e] & ~L["deliver"][:n_t, e]
        if silent.any():
            elig += 1
            _, dl, _ = ref_episode(B[e // kk], L["obs"][:, e], L["reg5"][:, e], L["live"][:, e], "free")
            caught += int(not np.array_equal(np.array(dl[:n_t]), L["deliver"][:n_t, e]))
    return {"episodes": P * kk, "free_stream_eligible_episodes": elig,
            "free_stream_share": round(caught / elig, 4) if elig else 0.0}


# ------------------------------------------------------------------ one run

def run(r, family, rs, arm_i, arm, gens):
    from primordial.qd.archive import LuaArchive
    sel = selection_seeds(arm)
    rng = np.random.Generator(np.random.PCG64([family, rs, arm_i, STREAM_TAG]))
    arch = LuaArchive(r, f"c-r7-ap01-{family}-{rs}-{arm_i}", GLEN, sampler_seed=[family + 1, rs, arm_i, STREAM_TAG])
    arch.clear()
    c0 = time.process_time()
    gen_cpu = []
    for _ in range(gens):
        g0 = time.process_time()
        par = arch.sample(BATCH)
        B = init(rng, BATCH) if len(par) == 0 else mutate(rng, np.asarray(par, np.uint8))
        o = rollout(B, sel, "metered")
        arch.insert(o["cells"], o["fit"].astype(np.int32), B, np.zeros((BATCH, 2), np.uint32))
        gen_cpu.append(time.process_time() - g0)
    loop_cpu = time.process_time() - c0
    el = arch.dump()
    arch.clear()
    order = sorted(el.values(), key=lambda v: (-v[0], v[1]))
    top = np.frombuffer(b"".join(v[1] for v in order[:TOP]), np.uint8).reshape(-1, GLEN)
    rec = rollout(top, sel, "metered")["fit"]
    recount_bad = int(sum(int(x) != int(v[0]) for x, v in zip(rec, order[:TOP])))
    held = rollout(top[:1], F.HELD64, "metered")
    sil = rollout(top[:1], F.HELD64, "silent")
    s, k, a, c, C = decode(top[:1])
    info = {"gens_done": gens, "genomes_evaluated": gens * BATCH, "loop_cpu_s": round(loop_cpu, 4),
            "max_gen_cpu_s": round(max(gen_cpu or [0.0]), 4), "archive_cells": len(el),
            "train_fit_top1": int(order[0][0]), "train_per_seed_top1": float(order[0][0] / len(sel)),
            "held64_per_seed_top1": float(held["fit"][0] / len(F.HELD64)),
            "held64_silenced_top1": float(sil["fit"][0] / len(F.HELD64)),
            "held_delivered_share_top1": float(held["delivered_share"][0]),
            "held_yield_share_top1": float(held["yield_share"][0]), "held_refits_top1": float(held["refits"][0]),
            "top1_program": {"s": int(s[0]), "k": int(k[0]), "a": int(a[0]), "c": int(c[0]),
                             "codebook": [int(x) for x in C[0]]},
            "top1_sha256": hashlib.sha256(top[0].tobytes()).hexdigest(), "recount_mismatched_top16": recount_bad}
    return info, top


def oracles(top, arm) -> dict:
    h8 = np.asarray(E7.HELD8, np.int64)
    wo = world_oracle(top, h8, "metered")
    wc = world_oracle(top, h8, "metered", "skip_lin")
    bo = brain_oracle(top, h8, "metered")
    mo = meter_oracle(top, h8)
    o = {"world_honest": wo, "world_skip_lin": wc, "brain": bo, "meter": mo, "arm": arm}
    o["ok"] = bool(wo["elites_failing"] == 0 and wc["elites_failing"] >= 14
                   and bo["honest_mismatched_episodes"] == 0 and bo["skip_plastic_eligible_episodes"] > 0
                   and bo["skip_plastic_share"] >= 0.9
                   and mo["free_stream_eligible_episodes"] > 0 and mo["free_stream_share"] >= 0.9)
    return o


def score(held, control) -> dict:
    q = np.percentile(held, [25, 50, 75])
    qc = np.percentile(control, [25, 50, 75])
    bar = float(qc[1] - 0.5 * (qc[2] - qc[0]))
    return {"held_median_cell": float(q[1]), "iqr_cell": float(q[2] - q[0]), "held_median_control": float(qc[1]),
            "iqr_control": float(qc[2] - qc[0]), "bar": bar, "parity": bool(q[1] >= bar)}


def job(ctx, gens: int = GENS, port: int = PORT, exp_id: str = EXP):
    import redis
    r = redis.Redis(host="127.0.0.1", port=port)
    arms = {0: ("cell", CELL), 1: ("control", CELL_CTRL)}
    todo = [(f, rs, ai) for f in FAMILIES for rs in range(RUNS_PER_FAMILY) for ai in (1, 0)]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": []}, "clean": True, "ref": False}
    if not st["ref"]:
        ctx.emit({"kind": "reference", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "gens": gens, "batch": BATCH,
                  "genome_bytes": GLEN, "alpha": ALPHA, "credit": CREDIT, "start": START, "window": WINDOW,
                  "surprise_support": SURPRISE_SUPPORT, "floor": FLOOR, "selection": {"cell": "TRAIN8",
                                                                                       "control": "HELD64"},
                  "status": "control", "ts": round(time.time(), 3)})
        st["ref"] = True
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        fam, rs, ai = todo[st["next"]]
        arm, cell = arms[ai]
        t0, c0 = time.perf_counter(), time.process_time()
        info, top = run(r, fam, rs, ai, arm, gens)
        ok = info["recount_mismatched_top16"] == 0
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
               "selection": "TRAIN8" if arm == "cell" else "HELD64", "genome_bytes": GLEN, "reader": "top1_train",
               **info, "train_minus_held": info["train_per_seed_top1"] - info["held64_per_seed_top1"],
               "held_above_floor_report_only": info["held64_per_seed_top1"] - FLOOR,
               "status": "record" if arm == "cell" else "control"}
        if fam == FAMILIES[0] and rs == 0:
            o = oracles(top, arm)
            row["oracles"] = o
            ok = ok and o["ok"]
        st["clean"] = bool(st["clean"] and ok)
        row["cpu_s"], row["wall_s"] = round(time.process_time() - c0, 3), round(time.perf_counter() - t0, 3)
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(row["held64_per_seed_top1"])
        ctx.emit(row)
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    sc = score(st["held"]["cell"], st["held"]["control"])
    n = {a: len(st["held"][a]) for a in st["held"]}
    full = all(v == len(FAMILIES) * RUNS_PER_FAMILY for v in n.values())
    primary = "INDETERMINATE" if not (st["clean"] and full) else ("PASS" if sc["parity"] else "FAIL")
    ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL,
              "runs_total": n["cell"], "rng_family_count": len(FAMILIES), "runs_per_family": RUNS_PER_FAMILY,
              "families": list(FAMILIES), "n_per_family": {str(f): RUNS_PER_FAMILY for f in FAMILIES},
              "gens": gens, **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in sc.items()},
              "floor_report_only": FLOOR, "oracle_clean": st["clean"], "primary": primary,
              "clause_a": "none claimed (ANTI_PRIOR row)", "status": "record" if st["clean"] else "cheat",
              "ts": round(time.time(), 3)})


# ------------------------------------------------------------------ dev (no rows)

def dev(gens: int = 3) -> None:
    """No rows: oracle eligibility on random genomes, CPU per generation per arm, GENS by the docstring rule."""
    import redis
    r = redis.Redis(host="127.0.0.1", port=PORT)
    rng = np.random.Generator(np.random.PCG64(77))
    B = init(rng, TOP)
    out = {"oracles_random": oracles(B, "dev")}
    per_gen = {}
    for arm in ("cell", "control"):
        sel = selection_seeds(arm)
        Bb = init(rng, BATCH)
        rollout(Bb, sel)
        c, t = time.process_time(), time.perf_counter()
        for _ in range(gens):
            Bb = mutate(rng, Bb)
            rollout(Bb, sel)
        per_gen[arm] = {"cpu_s_per_gen": round((time.process_time() - c) / gens, 5),
                        "wall_s_per_gen": round((time.perf_counter() - t) / gens, 5)}
    out["per_gen"] = per_gen
    unit = 32 * (per_gen["cell"]["cpu_s_per_gen"] + per_gen["control"]["cpu_s_per_gen"]) * 1.1
    proj = {str(G): round(unit * G, 1) for G in GENS_CHOICES}
    fits = [G for G in GENS_CHOICES if unit * G <= CPU_CAP]
    out["projected_job_cpu_s"] = proj
    out["gens_by_rule"] = max(fits) if fits else "INFEASIBLE"
    c = time.process_time()
    info, _ = run(r, 4200, 0, 0, "cell", 2)
    out["run2_cpu_s"] = round(time.process_time() - c, 3)
    out["run2_info"] = info
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dev(int(sys.argv[2]) if len(sys.argv) > 2 else 3) if sys.argv[1] == "dev" else None
