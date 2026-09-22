"""C-R6-01 (DISTANT_QD): drawn cell cp / w13 / cpu_ttl / graphblas / metered_stream (draw seed 6355500877785897427).

Cohort C builds the drawn cell; it does not choose it (draw posted on the bus, 1789485011356-0). No definition of cp,
cpu_ttl, graphblas or metered_stream on w13 existed; the definitions below are fixed before any run.

Round 5's DISTANT_QD PASS was vacuous (every run learned silence). This harness therefore evaluates its predicate on a
PLANTED NULL first -- the cell with its mechanism removed -- and logs that check in the rows before any cell-arm row. If
the null passes, the job stops (summary primary PREDICATE_PASSES_PLANTED_NULL) and the predicate must be rewritten
before any cell-arm row exists.

  world     w13 (E4.Spec(13)), the round 4 screen's SURVIVED world at train128_held64 (floor gate_in|HOLD 166.46875).
            D=5, S=1, W=1, T=32. Fitness = summed clipped final charge over the selection seeds (E7.rollout's rule).
  brain     cp: CP over the 20 hex digits of the observation (MSD first): v_r = prod_c U[c, digit_c, r], logits = v @ Wo,
            rank R=4; after every 5th mode v is divided by max|v| (argmax is scale invariant). U init 1 + 0.3 N(0,1),
            Wo N(0,1); float genes C4 mutate (p .05, sigma .2). Plus lane E's codebook C[8, W] (row 0 abstain, E7) and
            a 20-bit READ MASK (one bit per digit mode; unread digit -> index 0), mask bits flip p 1/20, init uniform.
            Genome 1312 float32 + 3 mask bytes + 8 codebook bytes -> padded 5260 bytes.
  channel   metered_stream: the observation reaches the brain through a read ledger apart from world charge. Per live
            slot-tick: ledger += CREDIT; cost = ALPHA * 4 * |mask|; if ledger >= cost the masked digits are delivered and
            ledger -= cost, else silence (every digit index 0). ALPHA = 2 (C-R2-08 / C-R4-01), CREDIT = ALPHA * 4 * 10 = 80
            (the stream pays for half of the observation's 20 digits per tick), START = CREDIT. Delivery never costs
            world charge, so silence is never cheaper than reading (the R5 D1 degeneracy cannot recur by construction).
  substrate graphblas: the brain forward is GraphBLAS arithmetic (per mode: row extract of the stacked factor matrix by
            genome*16 + digit, ewise_mult into v; row max-abs normalization; logits by mxm through the stacked Wo). numpy
            runs the world (lane B's NpEncounter) and the ledger; argmax in numpy. Archive: E's LuaArchive (seeded).
  pressure  cpu_ttl (C-R2-01's rule): loop stops at the first generation boundary where client process CPU (audit
            excluded) reaches TTL = (loop CPU of the job's FIRST control run) / 5, set by code before any null or cell run.
  arms      control  same family, full budget GENS, mask forced all-read, every live tick delivered (no meter)
            null     PLANTED NULL = the cell arm with the stream removed: the ledger never delivers (every digit 0), TTL
            cell     metered stream, evolving mask, TTL
  order     all 32 control runs; all 32 null runs; NULL_CHECK row; then the 32 cell runs only if the null FAILED.
  selection TRAIN128 (9100..9227, the survivor's pressure) with the largest GENS in {50, 100, 200, 400} whose projected job
            CPU (32 control + 32 null at 1/5 + 32 cell at 1/5 = 44.8 control runs) <= 2400 CPU-s; if GENS 50 does not
            fit, TRAIN8 (9100..9107) with the same rule; if neither fits the cell is INFEASIBLE this round (aborted row +
            PRODUCTION_CANDIDATE with the measured cost). Rule fixed before the no-rows timing check; outcome below.
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 6301]); sampler [family + 1, run_seed, arm, 6301].
  reader    top1_train: the archive elite with the highest selection fitness (ties: smaller genome bytes);
            held = its HELD64 (30000..30063) mean per-seed charge; held_silenced = the same with the stream forced silent.
  PREDICATE for an arm X in {null, cell} (the same code scores both):
            P1  median held (X) >= median held (control) - 0.5 * IQR (control)
            P2  median held (X) > FLOOR 166.46875 (w13 gate_in|HOLD; floor = max of abstain, best constant, uniform
                random median, input-invariant learner)
            P3  held_silenced < held in >= 17 of the 32 runs of X (the policy uses what the stream delivers)
            PASS iff P1 and P2 and P3 and oracles clean. The null must FAIL before the cell runs.
  oracles   family 4200 run seed 0 of each arm, top-16 on HELD8:
            world  lane B's NpEncounter trace hash + charge == wforge replay of the recorded actions: honest 0 failing;
                   skip_lin cheat >= 14/16 failing
            brain  float64 loop reference (masked + delivered digits) == GraphBLAS argmax on <= 256 sampled live rows per
                   elite, clear rows only (top-2 gap > 1e-4 * max|logit|, fixed for the float32 21-product chain):
                   honest 0 mismatched; cheat skip_odd_modes mismatches >= 90% of ELIGIBLE rows (clear rows where the
                   float64 reference itself changes argmax when odd modes are skipped), >= 1 eligible
            meter  scalar ledger replay from the recorded live mask == recorded delivery table (exact); the replay also
                   flags a free-delivery table on every episode with >= 1 honest silent tick (cell arm; >= 1 required)
            recount EVERY run: archive fitness of the top-16 == rollout from the STORED genome bytes (exact)
            ttl    null and cell: loop CPU < TTL + largest single-generation CPU
  clause A  none claimable: the pressure is cpu_ttl and 5,260 B > the 200 B baseline. Progress above floor reported only.

  worker:  job = primordial.cohorts.c.r6_01_cp_w13_cpu_ttl_graphblas_metered:job
  dev:     python -m primordial.cohorts.c.r6_01_cp_w13_cpu_ttl_graphblas_metered dev   (no rows)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np
from graphblas import Matrix, binary, dtypes, monoid, semiring, unary

from primordial.brain import genomes as gm
from primordial.brain.tt_policy import digits
from primordial.metric import floors as F
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.soup.b1.np_world import NpEncounter

EXP = "C-R6-01-cp-w13-cpu-ttl-graphblas-metered"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
CELL = {"representation": "cp", "world": "w13", "pressure": "cpu_ttl", "substrate": "graphblas",
        "channel": "metered_stream"}
CELL_CTRL = dict(CELL, pressure="none_control", channel="none")
CELL_NULL = dict(CELL, channel="metered_stream_silent_planted_null")
GS, A, R, BATCH, TOP = 13, 8, 4, 128, 16
ALPHA = 2
CREDIT = ALPHA * 4 * 10
START = CREDIT
NORM_EVERY = 5
CLEAR_REL = 1e-4
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
P3_MIN = 17
TTL_DIV = 5
PORT = 6392
# No-rows dev check (2 gens after warm-up, control, force read-all): TRAIN128 1.1328 CPU-s / gen -> GENS 50 projects
# 2537.5 > 2400 (does not fit); TRAIN8 0.1484 CPU-s / gen -> GENS 200 projects 1330.0, GENS 400 2660.0. By the docstring
# rule: TRAIN8, GENS 200. Consequence disclosed before the predicate: the w13 train8_held64 float baseline median is 149.08,
# below FLOOR, so P2 may bind for every arm.
SELECTION = "TRAIN8"
GENS = 200


def screen_floor():
    doc = json.loads((ROOT / "primordial" / "ledger" / "qd" / "worlds_r4.json").read_text(encoding="utf-8"))
    c = [x for x in doc["cells"] if x["world"] == "w13" and x["pressure"] == "train128_held64"][0]
    assert c["verdict"] == "SURVIVED"
    return c["verdicts"]["gate_in|HOLD"]["floor"], c["baseline"]["median"]


FLOOR, BASE_MED = screen_floor()


class CPDigits(gm.Family):
    name = "cp_digits_masked"

    def __init__(self, D, A=8):
        super().__init__(D, A)
        self.nc = 4 * D
        self.mb = (self.nc + 7) // 8

    def shapes(self):
        return [(self.nc, 16, R), (R, self.A)]

    @property
    def nbytes(self) -> int:
        return self.nf * 4 + self.mb

    def init(self, rng, P):
        U = (1.0 + 0.3 * rng.standard_normal((P, self.nc, 16, R))).astype(np.float32)
        Wo = rng.standard_normal((P, R, self.A)).astype(np.float32)
        return U, Wo, rng.random((P, self.nc)) < 0.5

    def mutate(self, rng, g, rate: float = 0.05, sigma: float = 0.2):
        U, Wo = super().mutate(rng, g[:2], rate, sigma)
        return U, Wo, g[2] ^ (rng.random(g[2].shape) < 1.0 / self.nc)

    def pack(self, g) -> np.ndarray:
        P = len(g[0])
        f = np.concatenate([g[0].reshape(P, -1), g[1].reshape(P, -1)], 1).astype("<f4").view(np.uint8)
        m = np.packbits(g[2].astype(np.uint8), axis=1, bitorder="little")[:, :self.mb]
        return np.concatenate([f.reshape(P, self.nf * 4), m], 1)

    def unpack(self, B):
        P, fb = len(B), self.nf * 4
        f = np.ascontiguousarray(B[:, :fb]).view("<f4").reshape(P, self.nf)
        n0 = self.nc * 16 * R
        U = f[:, :n0].reshape(P, self.nc, 16, R).copy()
        Wo = f[:, n0:].reshape(P, R, self.A).copy()
        m = np.unpackbits(np.ascontiguousarray(B[:, fb:fb + self.mb]), axis=1, bitorder="little")[:, :self.nc]
        return U, Wo, m.astype(bool)

    def ref_logits(self, g1, eff, skip_odd=False):
        """float64 loop reference on effective digits eff int [m, nc] -> logits [m, A]."""
        U, Wo = g1[0].astype(np.float64), g1[1].astype(np.float64)
        out = np.zeros((len(eff), self.A))
        for i in range(len(eff)):
            v = np.ones(R)
            for c in range(self.nc):
                if not (skip_odd and c % 2):
                    v = v * U[c, int(eff[i, c])]
                if (c + 1) % NORM_EVERY == 0:
                    v = v / max(float(np.abs(v).max()), 1e-300)
            out[i] = v @ Wo
        return out


class GBBrain:
    """GraphBLAS forward for a population p = (U, Wo, mask)."""

    def __init__(self, p):
        U, Wo = p[0], p[1]
        P, nc = U.shape[:2]
        self.P, self.nc = P, nc
        rows = np.repeat(np.arange(P * 16), R)
        cols = np.tile(np.arange(R), P * 16)
        self.U = [Matrix.from_coo(rows, cols, np.ascontiguousarray(U[:, c]).reshape(-1), nrows=P * 16, ncols=R,
                                  dtype=dtypes.FP32) for c in range(nc)]
        self.Wo = Matrix.from_coo(np.repeat(np.arange(P), R * A), np.tile(np.arange(R * A), P),
                                  np.ascontiguousarray(Wo).reshape(-1), nrows=P, ncols=R * A, dtype=dtypes.FP32)
        self.rep = Matrix.from_coo(np.repeat(np.arange(R), A), np.arange(R * A), np.ones(R * A, np.float32),
                                   nrows=R, ncols=R * A, dtype=dtypes.FP32)
        self.sum = Matrix.from_coo(np.arange(R * A), np.tile(np.arange(A), R), np.ones(R * A, np.float32),
                                   nrows=R * A, ncols=A, dtype=dtypes.FP32)

    @staticmethod
    def _normalize(v, n):
        mx = v.apply(unary.abs).new().reduce_rowwise(monoid.max).new()
        inv = mx.apply(binary.max, right=np.float32(1e-30)).new().apply(unary.minv).new()
        i, x = inv.to_coo()
        Dm = Matrix.from_coo(i, i, x, nrows=n, ncols=n, dtype=dtypes.FP32)
        return Dm.mxm(v, semiring.plus_times).new()

    def logits(self, eff, gidx, skip_odd=False):
        n = len(eff)
        base = np.asarray(gidx, np.int64) * 16
        v = None
        for c in range(self.nc):
            if not (skip_odd and c % 2):
                X = self.U[c][base + eff[:, c], :].new()
                v = X if v is None else v.ewise_mult(X, binary.times).new()
            if (c + 1) % NORM_EVERY == 0 and v is not None:
                v = self._normalize(v, n)
        Wg = self.Wo[np.asarray(gidx, np.int64), :].new()
        Ev = v.mxm(self.rep, semiring.plus_times).new().ewise_mult(Wg, binary.times).new()
        L = Ev.mxm(self.sum, semiring.plus_times).new()
        out = np.zeros((n, A), np.float32)
        ii, jj, xx = L.to_coo()
        out[ii, jj] = xx
        return out


def make_g7():
    g7 = E7.G7(GS, "linear")
    g7.fam = CPDigits(g7.D, A)
    g7.pb = g7.fam.nbytes
    g7.glen = (g7.pb + g7.cb + 3) // 4 * 4
    return g7


def force_read_all(g):
    p, C = g
    return (p[0], p[1], np.ones_like(p[2])), C


def rollout(g7, g, seeds, meter, world_cheat="", skip_odd=False, log=False):
    """meter: 'metered' | 'free' (every live tick delivered) | 'silent' (never). -> dict."""
    p, C = g
    P, k, S, D, W = len(C), len(seeds), g7.S, g7.D, g7.W
    n = P * k
    brain = GBBrain(p)
    w = NpEncounter(g7.spec.mech, g7.spec.wid, record=np.arange(n) if log else None, cheat=world_cheat, with_obs=True)
    obs = w.reset(np.tile(np.asarray(seeds, np.int64), P))
    genv = np.repeat(np.arange(P), k)
    grow = np.repeat(genv, S)
    mask = p[2][grow]
    cost = ALPHA * 4 * p[2].sum(1)[grow].astype(np.int64)
    led = np.full(n * S, START, np.int64)
    abst, mag, cnt, dlv = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
    L = {"acts": np.zeros((g7.T, n, S, W), np.int32), "eff": np.zeros((g7.T, n * S, 4 * D), np.int8),
         "idx": np.zeros((g7.T, n, S), np.int64), "live": np.zeros((g7.T, n, S), bool),
         "deliver": np.zeros((g7.T, n * S), bool)} if log else None
    for t in range(g7.T):
        live = (w.alive & ~w.done[:, None]).reshape(-1)
        if meter == "metered":
            led = led + np.where(live, CREDIT, 0)
            deliver = live & (led >= cost)
            led = led - np.where(deliver, cost, 0)
        elif meter == "free":
            deliver = live.copy()
        else:
            deliver = np.zeros(n * S, bool)
        dig = digits(obs.reshape(n * S, D)).astype(np.int64)
        eff = np.where(mask & deliver[:, None], dig, 0)
        idx = brain.logits(eff, grow, skip_odd).argmax(1).reshape(n, S)
        a = C[genv[:, None], idx].astype(np.int32)
        lv = live.reshape(n, S)
        x = (a % 8).sum(-1)
        abst += ((x == 0) & lv).sum(1); mag += (x * lv).sum(1); cnt += lv.sum(1)
        dlv += (deliver & live).reshape(n, S).sum(1)
        if log:
            L["acts"][t], L["eff"][t], L["idx"][t], L["live"][t], L["deliver"][t] = a, eff, idx, lv, deliver
        obs, _, done = w.step(a)
        if done.all():
            break
    fit = np.clip(w.charge, 0, None).sum(1).reshape(P, k).sum(1).astype(np.int64)
    tot = np.maximum(cnt.reshape(P, k).sum(1), 1)
    ab = abst.reshape(P, k).sum(1) / tot
    mg = mag.reshape(P, k).sum(1) / (tot * W * 7)
    cells = (np.rint(ab * 32) * E4.GRID + np.rint(np.clip(mg, 0, 1) * 32)).astype(np.uint32)
    return {"fit": fit, "cells": cells, "w": w, "L": L, "delivered_share": dlv.reshape(P, k).sum(1) / tot}


def world_oracle(g7, g, seeds, meter, world_cheat=""):
    o = rollout(g7, g, seeds, meter, world_cheat=world_cheat, log=True)
    hashes = [h.decode() for h in o["w"].trace_hashes()]
    k, P = len(seeds), len(g[1])
    ep = np.clip(o["w"].charge, 0, None)
    bad = np.zeros(P, bool)
    for e in range(P * k):
        h, ch = E4.wforge_replay(g7.spec, o["L"]["acts"][:, e], seeds[e % k])
        bad[e // k] |= (h != hashes[e]) or not np.array_equal(ch, ep[e])
    return {"elites": P, "elites_failing": int(bad.sum())}


def brain_oracle(g7, g, seeds, meter, rows_per_elite=256, seed=0):
    o = rollout(g7, g, seeds, meter, log=True)
    L, fam = o["L"], g7.fam
    k, P, S = len(seeds), len(g[1]), g7.S
    rng = np.random.Generator(np.random.PCG64(seed))
    brain = GBBrain(g[0])
    rows = honest_bad = elig = caught = 0
    for q in range(P):
        t_i, e_i, s_i = np.nonzero(L["live"][:, q * k:(q + 1) * k])
        if len(t_i) == 0:
            continue
        pick = np.sort(rng.choice(len(t_i), size=min(rows_per_elite, len(t_i)), replace=False))
        t_i, e_i, s_i = t_i[pick], e_i[pick] + q * k, s_i[pick]
        eff = L["eff"][t_i, e_i * S + s_i].astype(np.int64)
        one = fam.one(g[0], q)
        ref, refs = fam.ref_logits(one, eff), fam.ref_logits(one, eff, skip_odd=True)
        cl = clear(ref)
        honest_bad += int(((L["idx"][t_i, e_i, s_i] != ref.argmax(1)) & cl).sum())
        el = cl & clear(refs) & (refs.argmax(1) != ref.argmax(1))
        ch = brain.logits(eff, np.full(len(eff), q), skip_odd=True).argmax(1)
        rows += len(eff); elig += int(el.sum()); caught += int(((ch != ref.argmax(1)) & el).sum())
    return {"rows": rows, "honest_mismatched_clear_rows": honest_bad, "skip_odd_eligible_rows": elig,
            "skip_odd_share": round(caught / elig, 4) if elig else 0.0}


def clear(ref):
    return gm.clear_rows(ref, rel=CLEAR_REL)


def meter_oracle(g7, g, seeds):
    o = rollout(g7, g, seeds, "metered", log=True)
    L = o["L"]
    k, P, S = len(seeds), len(g[1]), g7.S
    live = L["live"].reshape(L["live"].shape[0], -1)
    cost = ALPHA * 4 * np.repeat(g[0][2].sum(1), k * S).astype(np.int64)
    mism = elig = caught = 0
    for e in range(P * k * S):
        led, ref = START, np.zeros(live.shape[0], bool)
        for t in range(live.shape[0]):
            if live[t, e]:
                led += CREDIT
                if led >= cost[e]:
                    ref[t] = True
                    led -= cost[e]
        mism += int(not np.array_equal(ref, L["deliver"][:, e]))
        silent = live[:, e] & ~ref
        if silent.any():
            elig += 1
            caught += int(not np.array_equal(ref, live[:, e]))
    return {"episodes": P * k * S, "honest_mismatched_episodes": mism, "free_eligible_episodes": elig,
            "free_caught_episodes": caught}


def server_cpu(r) -> float:
    i = r.info("cpu")
    return float(i["used_cpu_sys"]) + float(i["used_cpu_user"])


def selection_seeds(name):
    return F.TRAIN128 if name == "TRAIN128" else F.TRAIN8


def run(r, g7, family, rs, arm_i, arm, gens, ttl, train):
    from primordial.qd.archive import LuaArchive
    meter = {"control": "free", "null": "silent", "cell": "metered"}[arm]
    rng = np.random.Generator(np.random.PCG64([family, rs, arm_i, 6301]))
    arch = LuaArchive(r, f"c-r6-01-{family}-{rs}-{arm_i}", g7.glen, sampler_seed=[family + 1, rs, arm_i, 6301])
    arch.clear()
    s0, c0 = server_cpu(r), time.process_time()
    gen_cpu, done = [], 0
    for _ in range(gens):
        if ttl is not None and time.process_time() - c0 >= ttl:
            break
        g0 = time.process_time()
        par = arch.sample(BATCH)
        g = g7.init(rng, BATCH) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
        if arm == "control":
            g = force_read_all(g)
        o = rollout(g7, g, train, meter)
        arch.insert(o["cells"], o["fit"].astype(np.int32), g7.pack(g), np.zeros((BATCH, 2), np.uint32))
        gen_cpu.append(time.process_time() - g0)
        done += 1
    loop_cpu = time.process_time() - c0
    srv = server_cpu(r) - s0
    el = arch.dump()
    arch.clear()
    order = sorted(el.values(), key=lambda v: (-v[0], v[1]))
    raw = np.frombuffer(b"".join(v[1] for v in order[:TOP]), np.uint8).reshape(-1, g7.glen)
    top = g7.unpack(raw)
    rec = rollout(g7, top, train, meter)["fit"]
    recount_bad = int(sum(int(a) != int(b[0]) for a, b in zip(rec, order[:TOP])))
    one = (tuple(x[:1] for x in top[0]), top[1][:1])
    hd = rollout(g7, one, F.HELD64, meter)
    hs = rollout(g7, one, F.HELD64, "silent")
    held = float(hd["fit"][0] / len(F.HELD64))
    held_sil = float(hs["fit"][0] / len(F.HELD64))
    info = {"gens_done": done, "genomes_evaluated": done * BATCH, "loop_cpu_s": round(loop_cpu, 4),
            "max_gen_cpu_s": round(max(gen_cpu or [0.0]), 4), "redis_server_cpu_s": round(srv, 4),
            "archive_cells": len(el), "train_fit_top1": int(order[0][0]),
            "train_per_seed_top1": float(order[0][0] / len(train)), "held64_per_seed_top1": held,
            "held64_silenced_top1": held_sil, "silencing_lowers": bool(held_sil < held),
            "held_delivered_share_top1": float(hd["delivered_share"][0]),
            "digits_read_top1": int(top[0][2][0].sum()), "recount_mismatched_top16": recount_bad}
    return info, top


def score(held, silenced_lowers, control) -> dict:
    q = np.percentile(held, [25, 50, 75])
    qc = np.percentile(control, [25, 50, 75])
    bar = float(qc[1] - 0.5 * (qc[2] - qc[0]))
    lowers = int(sum(silenced_lowers))
    return {"median": float(q[1]), "iqr": float(q[2] - q[0]), "control_median": float(qc[1]),
            "control_iqr": float(qc[2] - qc[0]), "bar": bar, "floor": FLOOR,
            "P1_parity": bool(q[1] >= bar), "P2_above_floor": bool(q[1] > FLOOR),
            "P3_uses_stream_runs": lowers, "P3_uses_stream": bool(lowers >= P3_MIN), "n": len(held)}


def job(ctx, gens: int = GENS, selection: str = SELECTION, port: int = PORT, exp_id: str = EXP):
    import redis
    r = redis.Redis(host="127.0.0.1", port=port)
    g7 = make_g7()
    train = selection_seeds(selection)
    arm_index = {"cell": 0, "control": 1, "null": 2}
    cells = {"cell": CELL, "control": CELL_CTRL, "null": CELL_NULL}
    runs = [(f, rs) for f in FAMILIES for rs in range(RUNS_PER_FAMILY)]
    todo = [("control", f, rs) for f, rs in runs] + [("null", f, rs) for f, rs in runs] + [("null_check", 0, 0)] \
        + [("cell", f, rs) for f, rs in runs]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": [], "null": []},
                                   "lowers": {"cell": [], "null": []}, "clean": {"control": True, "null": True,
                                                                                  "cell": True},
                                   "ref": False, "ttl": None, "null_check": None}
    if not st["ref"]:
        ctx.emit({"kind": "reference", "exp_id": exp_id, "gens": gens, "selection": selection, "batch": BATCH,
                  "genome_bytes": g7.glen, "floor": FLOOR, "baseline_median_train128": BASE_MED, "alpha": ALPHA,
                  "credit": CREDIT, "start": START, "rank": R, "clear_rel": CLEAR_REL, "p3_min_runs": P3_MIN,
                  "ttl_rule": f"first control run loop CPU / {TTL_DIV}", "order": "control, null, NULL_CHECK, cell",
                  "status": "control", "ts": round(time.time(), 3)})
        st["ref"] = True
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        arm, fam, rs = todo[st["next"]]
        if arm == "null_check":
            sc = score(st["held"]["null"], st["lowers"]["null"], st["held"]["control"])
            passes = bool(sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_stream"]
                          and st["clean"]["null"] and st["clean"]["control"])
            st["null_check"] = {"null_predicate": "PASS" if passes else "FAIL", **sc,
                                "oracle_clean_null": st["clean"]["null"],
                                "oracle_clean_control": st["clean"]["control"]}
            ctx.emit({"kind": "null_check", "exp_id": exp_id, **st["null_check"],
                      "rule": "the planted null must FAIL the predicate before any cell-arm row",
                      "status": "control", "ts": round(time.time(), 3)})
            st["next"] += 1
            if passes:
                ctx.emit({"kind": "summary", "exp_id": exp_id, "cell": CELL, "primary": "PREDICATE_PASSES_PLANTED_NULL",
                          "null_check": st["null_check"], "status": "aborted",
                          "reason": "predicate rewrite required before any cell-arm row", "ts": round(time.time(), 3)})
                return
            continue
        first = fam == FAMILIES[0] and rs == 0
        ttl = None if arm == "control" else st["ttl"]
        t0, c0 = time.perf_counter(), time.process_time()
        info, top = run(r, g7, fam, rs, arm_index[arm], arm, gens, ttl, train)
        if arm == "control" and st["ttl"] is None:
            st["ttl"] = round(info["loop_cpu_s"] / TTL_DIV, 4)
        ok = info["recount_mismatched_top16"] == 0
        row = {"kind": "run", "arm": arm, "cell": cells[arm], "family": fam, "run_seed": rs, "gens": gens,
               "selection": selection, "ttl_cpu_s": ttl, "genome_bytes": g7.glen, "reader": "top1_train", **info,
               "progress_above_floor_report_only": (info["held64_per_seed_top1"] - FLOOR) / (BASE_MED - FLOOR),
               "status": {"cell": "record", "control": "control", "null": "control"}[arm]}
        if first:
            meter = {"control": "free", "null": "silent", "cell": "metered"}[arm]
            h8 = E7.HELD8
            wo = world_oracle(g7, top, h8, meter)
            wc = world_oracle(g7, top, h8, meter, "skip_lin")
            bo = brain_oracle(g7, top, h8, meter)
            o = {"world_honest": wo, "world_skip_lin": wc, "brain": bo}
            o["ok"] = bool(ok and wo["elites_failing"] == 0 and wc["elites_failing"] >= 14
                           and bo["honest_mismatched_clear_rows"] == 0 and bo["skip_odd_eligible_rows"] > 0
                           and bo["skip_odd_share"] >= 0.9)
            if arm == "cell":
                mo = meter_oracle(g7, top, h8)
                o["meter"] = mo
                o["ok"] = o["ok"] and mo["honest_mismatched_episodes"] == 0 and mo["free_eligible_episodes"] > 0 \
                    and mo["free_caught_episodes"] == mo["free_eligible_episodes"]
            if ttl is not None:
                o["ttl_ok"] = bool(info["loop_cpu_s"] < ttl + info["max_gen_cpu_s"])
                o["ok"] = o["ok"] and o["ttl_ok"]
            row["oracles"] = o
            ok = o["ok"]
        st["clean"][arm] = st["clean"][arm] and ok
        row["cpu_s"], row["wall_s"] = round(time.process_time() - c0, 3), round(time.perf_counter() - t0, 3)
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(row["held64_per_seed_top1"])
        if arm != "control":
            st["lowers"][arm].append(info["silencing_lowers"])
        ctx.emit(row)
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    sc = score(st["held"]["cell"], st["lowers"]["cell"], st["held"]["control"])
    clean = st["clean"]["cell"] and st["clean"]["control"]
    full = all(len(st["held"][a]) == len(runs) for a in ("cell", "control"))
    primary = "INDETERMINATE" if not (clean and full) else \
        ("PASS" if sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_stream"] else "FAIL")
    ctx.emit({"kind": "summary", "exp_id": exp_id, "cell": CELL, "runs_total": len(st["held"]["cell"]),
              "rng_family_count": len(FAMILIES), "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
              "ttl_cpu_s": st["ttl"], "selection": selection, "gens": gens, **sc, "null_check": st["null_check"],
              "oracle_clean": clean, "primary": primary,
              "progress_above_floor_report_only": (sc["median"] - FLOOR) / (BASE_MED - FLOOR),
              "clause_a": "none: pressure cpu_ttl, 5,260 B > 200 B baseline",
              "status": "record" if clean else "cheat", "ts": round(time.time(), 3)})


def dev(gens: int = 2) -> None:
    """No rows: pack round trip, GraphBLAS == float64 reference, oracles on random genomes, CPU per control gen."""
    g7 = make_g7()
    rng = np.random.Generator(np.random.PCG64(77))
    g = g7.init(rng, 4)
    rt = g7.unpack(g7.pack(g))
    out = {"glen": g7.glen, "roundtrip": all(np.array_equal(a, b) for a, b in zip(g[0], rt[0][:3]))
           and np.array_equal(g[1], rt[1])}
    out["brain_metered"] = brain_oracle(g7, g, E7.HELD8, "metered", rows_per_elite=64)
    out["meter"] = meter_oracle(g7, g, E7.HELD8)
    out["world_honest"] = world_oracle(g7, g, E7.HELD8, "metered")
    out["world_skip_lin"] = world_oracle(g7, g, E7.HELD8, "metered", "skip_lin")
    for name in ("TRAIN8", "TRAIN128"):
        gg = force_read_all(g7.init(rng, BATCH))
        rollout(g7, gg, selection_seeds(name), "free")
        c, t = time.process_time(), time.perf_counter()
        for _ in range(gens):
            gg = force_read_all(g7.mutate(rng, gg))
            rollout(g7, gg, selection_seeds(name), "free")
        cpg = (time.process_time() - c) / gens
        out[name] = {"control_cpu_s_per_gen": round(cpg, 4), "wall_s_per_gen": round((time.perf_counter() - t) / gens, 4),
                     "projected_job_cpu_s": {str(G): round(44.8 * G * cpg, 1) for G in (50, 100, 200, 400)}}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dev(int(sys.argv[2]) if len(sys.argv) > 2 else 2) if sys.argv[1] == "dev" else None
