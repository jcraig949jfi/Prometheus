"""C-R8-AP-01 (ANTI_PRIOR, cell assigned by code): pairwise / signal_world_d1 / corruption / graphblas / none
(anti_prior.assign exp_id C-R8-AP-01, round 8, from the G2 binding-eligible candidate list, seed 20260921).

The experimenter received only the cell; the prior, arm, rank and quantile are unread (pm:prior:* never read). No
definition of this cell existed; the definitions below are fixed before any run. signal_world_d1 is not a screened
graphworld world: no floor suite, no clause A claim.

G2 BASIS, disclosed: none of the seven G2-v1 rules has a basis on this cell (the corruption rule is graphworld-only and
the d1 pay-off rule applies only to metered_stream), so the cell entered the pool because no rule PROVED a defect, not
because code verified binding. This job therefore runs anti_prior.binding_precheck(cell, evidence=...) with MEASURED
evidence (intervention magnitude, oracle eligibility) in committed rows before any run, and aborts INELIGIBLE if it fails.

  world     lane D's D1 signal world (primordial.lingua.signal): T = 64 ticks; slot 0 sees R in [0, 256) drawn per tick
            (signal.r_stream(episode seed)); slot 1 hears the channel and acts in [0, 8); right iff act == R >> 5.
  channel   none (C-R5-AP-01's definition): no ledger, no cost. Fitness = right actions summed over the selection
            episodes. The task is a pure function of (R, what is heard), so fitness is exact from the joint histogram
            H[R, x] of registers and channel XOR values x over the episodes' ticks.
  brain     pairwise: an order-2 interaction code over R written as 4 base-4 digits q0..q3 (q0 = R >> 6). Slot 0's
            encoder is 6 byte tables T_ij[4 x 4] for the pairs i < j: s = (sum_ij T_ij[q_i, q_j]) mod 256,
            sym = s >> 5 in [0, 8). Slot 1's decoder is lane E's codebook form (C-R5-AP-01): act = cb[heard] % 8.
            Genome 96 + 8 = 104 bytes. The exact D1 code is expressible (T_01[q0, q1] = 32 * (2 q0 + (q1 >> 1)), other
            tables 0, cb = identity = planted HAND); no target is held by the brain. A pairwise code cannot express an
            arbitrary 3-way function of the digits; the D1 target needs only (q0, q1). Disclosed, not changed.
            Init bytes uniform. Mutation: each byte with p 4/104, half a uniform redraw, half +-1 mod 256 (C-R5-01's
            half-uniform/half-step rule).
  pressure  corruption, receiver side, C-R5-01's rule taken unchanged: at each tick, with p = 1/RATE (RATE 16), the
            heard symbol is XORed with v & 7 (3-bit symbols); flip = r_stream(seed + 2^40) % RATE == 0 and
            v = r_stream(seed + 2^41), a function of the episode seed only (common across genomes). It acts during
            SELECTION. Every arm is SCORED on HELD through its own delivery mechanism WITHOUT the pressure (the clean
            channel for control and cell; silence for the null): a common reference distribution for cell vs control.
  substrate graphblas: every selection fitness is GraphBLAS arithmetic. Per batch: E (P*256 x 8) one-hot encoder
            symbols (numpy computes the pairwise table sum, as numpy did the Tucker contraction in C-R6-AP-01);
            K = E.mxm(X) with X (8 x 64) the XOR map sym -> (x, sym ^ x), lifted per genome; A = K.mxm(D) with D
            (P*64 x 64) the per-genome codebook (x, heard) -> (x, act); fitness = reduce over the (genome, R) rows of
            A.ewise_mult(W) with W[(p, R), x * 8 + (R >> 5)] = H[R, x]. numpy is the reference only.
  search    MAP-Elites, in-process (C-R7-01's archive: replace iff fitness higher, or equal with lexicographically smaller
            bytes; parents uniform over filled cells in sorted order by the sampler stream). Descriptor (C-R5-AP-01):
            (distinct symbols emitted over R - 1) * 8 + (distinct actions over R through the clean channel - 1), 64
            cells; silence for the null. Batch 128.
  arms      control  pressure removed: selection on TRAIN, clean channel (RATE 0)
            null     PLANTED NULL = the cell with its mechanism removed: slot 1 hears silence (symbol 0) every tick
            cell     selection on TRAIN under corruption RATE 16
  order     all 32 control runs; all 32 null runs; NULL_CHECK row; then the 32 cell runs only if the null FAILED (else
            summary PREDICATE_PASSES_PLANTED_NULL and stop).
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 8101]); sampler PCG64([family + 1, run_seed, arm, 8101]).
            TRAIN = episode seeds 0..127 (C-R5-01's), HELD = 10,000,000..10,000,255 (16,384 registers).
  GENS      rule fixed before the dev check: the largest of {100, 200, 400, 800, 1600} whose projected job CPU
            (96 runs x measured CPU per generation per arm + oracles, x 1.25) <= 7200 CPU-s. Checkpointable.
  reader    top1_train: the archive elite with the highest selection fitness (ties: lexicographically smaller bytes);
            held = its right share on HELD through the arm's scoring channel.
  PREDICATE for an arm X in {null, cell} (the same code scores both):
            P1  median held (X) >= median held (control) - 0.5 * IQR (control)
            P2  median held (X) > FLOOR = the best input-invariant yield on HELD (max over a of the share of R >> 5 == a)
            P3  a scrambled channel (a per-episode permutation of the 8 heard symbols, PCG64([8101, family, run_seed,
                arm, 99])) lowers held in >= 17 of the 32 runs of X
            PASS iff P1 and P2 and P3 and oracles clean. The null must FAIL before the cell runs.
  VACUITY   (fixed before any row; SWARM_R8 brief: a PASS whose arms cannot discriminate is VACUOUS). If IQR(control)
            == 0 and IQR(cell) == 0 and median(cell) == median(control), primary = VACUOUS (never PASS or FAIL).
  BINDING   before any run, in committed rows: evidence = {intervention_magnitude: # of 256 random genomes x TRAIN whose
            corrupt-channel fitness differs from the clean-channel fitness, oracle_eligible: min eligible count over the
            two cheat oracles on random + planted genomes}; anti_prior.binding_precheck(CELL, evidence) must be ok, else
            summary INELIGIBLE (status aborted) and no run. Reported per cell run (not judged): whether the top1's
            TRAIN fitness under corruption differs from its clean TRAIN fitness.
  oracles   family 4200 run seed 0 of each arm, genomes = top-16 + planted HAND + planted CB1 (HAND with cb[0] = 1):
            graphblas  GraphBLAS fitness == numpy reference on EVERY offer of that run (exact); EVERY run: top-16
                       archive fitness == numpy recount from the STORED bytes (exact)
            tick       an explicit per-tick closed loop over the selection episodes (r_stream, noise, encoder, XOR,
                       codebook) == the histogram fitness for every oracle genome (exact), all arms
            cheat_cb   GraphBLAS with the decoder reading cb[(heard + 1) & 7] mismatches the reference on >= 90% of
                       ELIGIBLE genomes (the numpy reference itself changes), >= 1 eligible; all arms
            cheat_noise  cell arm only: GraphBLAS fed the noise-free histogram mismatches the reference on >= 90% of
                       ELIGIBLE genomes (the reference fitness differs with and without noise), >= 1 eligible
  report    (not judged) held under the RATE 16 channel for control and cell; hand-code yields; train yield; symbols /
            actions used by the top1; wall and CPU per arm.
  not claimed  clause A (no floor suite); any mechanism; anything about corruption at other rates.

  worker:  job = primordial.cohorts.c.r8_ap01_pairwise_d1_corruption_graphblas:job
  dev:     python -m primordial.cohorts.c.r8_ap01_pairwise_d1_corruption_graphblas dev [gens]   (no rows)
"""
from __future__ import annotations

import hashlib
import json
import sys
import time

import numpy as np

from primordial.lingua import signal as S

EXP = "C-R8-AP-01-pairwise-d1-corruption-graphblas"
PREDICATE_ID = "C-R8-AP-01"
ROWS = f"primordial/ledger/rows/C/{EXP}.jsonl"
CELL = {"channel": "none", "pressure": "corruption", "representation": "pairwise", "substrate": "graphblas",
        "world": "signal_world_d1"}
CELL_CTRL = dict(CELL, pressure="corruption_rate0_control")
CELL_NULL = dict(CELL, channel="none_silent_planted_null")
T = 64
NR, NA, SH = S.N_R, S.N_ACT, S.SHIFT
NX = 8
RATE = 16
NOISE_FLIP, NOISE_VAL = 1 << 40, 1 << 41
PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
NT = len(PAIRS) * 16
GLEN = NT + NA
MUT_P = 4.0 / GLEN
TRAIN = np.arange(128)
HELD = 10_000_000 + np.arange(256)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
BATCH, TOP = 128, 16
STREAM_TAG = 8101
P3_MIN = 17
GENS_CHOICES = (100, 200, 400, 800, 1600)
CPU_CAP = 7200.0
GENS = 1600     # no-rows dev check (10 gens per arm, family 4200 run 0): CPU/gen control 0.0203, null 0.0203,
                # cell 0.0141 -> projected job CPU 100: 219, 200: 438, 400: 875, 800: 1751, 1600: 3501 (cap 7200)
ARM_INDEX = {"cell": 0, "control": 1, "null": 2}
TRUTH = np.arange(NR) >> SH
_R = np.arange(NR)
DIGITS = np.stack([(_R >> 6) & 3, (_R >> 4) & 3, (_R >> 2) & 3, _R & 3], 1)          # [256, 4], q0 = MSD
IDX = np.stack([4 * DIGITS[:, i] + DIGITS[:, j] for i, j in PAIRS])                  # [6, 256]


# ------------------------------------------------------------------ world statistics

def noise(seeds, rate):
    s = np.asarray(seeds, np.uint64)
    flip = (S.r_stream(s + np.uint64(NOISE_FLIP), T) % rate == 0) if rate else np.zeros((T, len(s)), bool)
    return flip, S.r_stream(s + np.uint64(NOISE_VAL), T)


def joint_hist(seeds, rate) -> np.ndarray:
    """int64 [256, 8]: H[R, x] = # ticks with register R whose heard symbol is XORed with x (x = 0: unchanged)."""
    R = S.r_stream(np.asarray(seeds), T)
    fl, nv = noise(seeds, rate)
    x = np.where(fl, nv & 7, 0)
    return np.bincount((R * NX + x).ravel(), minlength=NR * NX).reshape(NR, NX).astype(np.int64)


def collapse(H) -> np.ndarray:
    out = np.zeros_like(H)
    out[:, 0] = H.sum(1)
    return out


def floor_of(H) -> float:
    h = H.sum(1)
    return float(max(h[TRUTH == a].sum() for a in range(NA)) / h.sum())


# ------------------------------------------------------------------ genome (numpy reference)

def split(G):
    G = np.asarray(G, np.uint8)
    return G[:, :NT].reshape(len(G), len(PAIRS), 16).astype(np.int64), G[:, NT:].astype(np.int64) % NA


def encode(G) -> np.ndarray:
    tabs, _ = split(G)
    s = np.take_along_axis(tabs, np.broadcast_to(IDX[None], (len(G), len(PAIRS), NR)), 2).sum(1)
    return (s % 256) >> 5                                                            # [P, 256]


def ref_fit(G, H, silent=False, cheat_cb=False) -> np.ndarray:
    enc = encode(G)
    _, cb = split(G)
    P = len(G)
    heard = np.zeros((P, NR, NX), np.int64) if silent else enc[:, :, None] ^ np.arange(NX)[None, None, :]
    act = np.take_along_axis(cb[:, None, :], ((heard + 1) & 7 if cheat_cb else heard).reshape(P, 1, -1), 2)
    act = act.reshape(P, NR, NX)
    return ((act == TRUTH[None, :, None]) * H[None]).sum((1, 2)).astype(np.int64)


def tick_fit(g, seeds, rate, silent=False) -> int:
    """Explicit closed loop, one genome, tick by tick over every episode (the oracle reference for the histogram)."""
    enc = encode(g[None])[0]
    cb = split(g[None])[1][0]
    R = S.r_stream(np.asarray(seeds), T)
    fl, nv = noise(seeds, rate)
    right = 0
    for t in range(T):
        sym = np.zeros(R.shape[1], np.int64) if silent else enc[R[t]]
        heard = np.where(fl[t], sym ^ (nv[t] & 7), sym) if not silent else sym
        right += int((cb[heard] == (R[t] >> SH)).sum())
    return right


def hand_genome(cb0=None):
    g = np.zeros(GLEN, np.uint8)
    g[:16] = (32 * (2 * np.arange(4)[:, None] + (np.arange(4)[None, :] >> 1))).ravel()   # T_01[q0, q1]
    g[NT:] = np.arange(NA)
    if cb0 is not None:
        g[NT] = cb0
    return g


def planted():
    return np.stack([hand_genome(), hand_genome(cb0=1)])


def init(rng, P):
    return rng.integers(0, 256, (P, GLEN), dtype=np.uint8)


def mutate(rng, B):
    B = B.astype(np.int64)
    m = rng.random(B.shape) < MUT_P
    uni = rng.random(B.shape) < 0.5
    step = np.where(rng.random(B.shape) < 0.5, 1, -1)
    new = np.where(uni, rng.integers(0, 256, B.shape), (B + step) % 256)
    return np.where(m, new, B).astype(np.uint8)


def descriptor(G, silent=False):
    enc = encode(G)
    _, cb = split(G)
    heard = np.zeros_like(enc) if silent else enc
    act = np.take_along_axis(cb, heard, 1)
    syms = np.array([len(np.unique(e)) for e in enc])
    acts = np.array([len(np.unique(a)) for a in act])
    return ((syms - 1) * 8 + (acts - 1)).astype(np.int64)


# ------------------------------------------------------------------ GraphBLAS evaluator

class GBEval:
    def __init__(self):
        import graphblas as gb
        self.gb = gb
        xr, xc = [], []
        for s in range(NA):
            for x in range(NX):
                xr.append(s)
                xc.append(x * NX + (s ^ x))
        self.xr, self.xc = np.array(xr), np.array(xc)
        self.mats = {}

    def fit(self, G, H, silent=False, cheat_cb=False) -> np.ndarray:
        gb = self.gb
        Mat = gb.Matrix
        P = len(G)
        rows = np.arange(P * NR)
        p_of_row = np.repeat(np.arange(P), NR)
        enc = encode(G).reshape(-1)
        _, cb = split(G)
        if silent:                                  # heard = 0 whatever x is: (p, R) -> (p, x, 0) for every x
            K = Mat.from_coo(np.repeat(rows, NX), (p_of_row[:, None] * NX * NX + np.arange(NX)[None, :] * NX).ravel(),
                             np.ones(P * NR * NX, np.int64), nrows=P * NR, ncols=P * NX * NX, dtype=gb.dtypes.INT64)
        else:
            # lift X per genome: column p * 64 + (x * 8 + heard) via one row-block per genome
            Ek = Mat.from_coo(rows, p_of_row * NA + enc, np.ones(P * NR, np.int64), nrows=P * NR, ncols=P * NA,
                              dtype=gb.dtypes.INT64)
            pr = np.repeat(np.arange(P), len(self.xr))
            XP = Mat.from_coo(pr * NA + np.tile(self.xr, P), pr * NX * NX + np.tile(self.xc, P),
                              np.ones(P * len(self.xr), np.int64), nrows=P * NA, ncols=P * NX * NX,
                              dtype=gb.dtypes.INT64)
            K = Ek.mxm(XP, gb.semiring.plus_times).new()
        # D: (p, x, heard) -> (x, act)
        heard_idx = np.arange(NX * NX) % NX
        x_idx = np.arange(NX * NX) // NX
        look = (heard_idx + 1) & 7 if cheat_cb else heard_idx
        acts = cb[:, look]                                                              # [P, 64]
        dr = (np.arange(P)[:, None] * NX * NX + np.arange(NX * NX)[None, :]).ravel()
        dc = (x_idx[None, :] * NX + acts).ravel()
        D = Mat.from_coo(dr, dc, np.ones(P * NX * NX, np.int64), nrows=P * NX * NX, ncols=NX * NX,
                         dtype=gb.dtypes.INT64)
        A = K.mxm(D, gb.semiring.plus_times).new()
        key = (P, H.tobytes())
        W = self.mats.get(key)
        if W is None:
            wr = np.repeat(rows, NX)
            wc = (np.arange(NX)[None, :] * NX + TRUTH[:, None]).ravel()
            wc = np.tile(wc, P)
            wv = np.tile(H.reshape(-1), P)
            keep = wv != 0
            W = Mat.from_coo(wr[keep], wc[keep], wv[keep], nrows=P * NR, ncols=NX * NX, dtype=gb.dtypes.INT64)
            self.mats = {key: W}
        ri, rv = A.ewise_mult(W, gb.binary.times).new().reduce_rowwise(gb.monoid.plus).new().to_coo()
        per_row = np.zeros(P * NR, np.int64)
        per_row[ri] = rv
        return per_row.reshape(P, NR).sum(1)


# ------------------------------------------------------------------ in-process archive (C-R7-01)

class Archive:
    def __init__(self):
        self.cells: dict[int, tuple[int, bytes]] = {}

    def insert(self, cells, fits, B):
        for c, f, g in zip(cells.tolist(), fits.tolist(), B):
            gbytes = g.tobytes()
            cur = self.cells.get(c)
            if cur is None or f > cur[0] or (f == cur[0] and gbytes < cur[1]):
                self.cells[c] = (int(f), gbytes)

    def sample(self, srng, n):
        keys = sorted(self.cells)
        idx = srng.integers(0, len(keys), n)
        return np.frombuffer(b"".join(self.cells[keys[i]][1] for i in idx), np.uint8).reshape(n, GLEN)

    def top(self, k):
        order = sorted(self.cells.values(), key=lambda v: (-v[0], v[1]))[:k]
        return np.frombuffer(b"".join(v[1] for v in order), np.uint8).reshape(-1, GLEN), \
            np.array([v[0] for v in order], np.int64)


# ------------------------------------------------------------------ probes and oracles

def scrambled_yield(g, seeds, silent, seed):
    enc = encode(g[None])[0]
    cb = split(g[None])[1][0]
    R = S.r_stream(np.asarray(seeds), T)
    E = R.shape[1]
    rng = np.random.Generator(np.random.PCG64(seed))
    perm = np.argsort(rng.random((E, NA)), axis=1)
    sym = np.zeros_like(R) if silent else enc[R]
    heard = perm[np.arange(E)[None, :], sym]
    return float((cb[heard] == (R >> SH)).sum() / R.size)


def cheat_oracle(ev, G, H, silent, kind) -> dict:
    ref = ref_fit(G, H, silent)
    if kind == "cb":
        ref_c = ref_fit(G, H, silent, cheat_cb=True)
        gb_c = ev.fit(G, H, silent, cheat_cb=True)
    else:
        ref_c = ref_fit(G, collapse(H), silent)
        gb_c = ev.fit(G, collapse(H), silent)
    el = ref_c != ref
    caught = int(((gb_c != ref) & el).sum())
    return {"eligible": int(el.sum()), "caught": caught,
            "share": round(caught / int(el.sum()), 4) if el.any() else 0.0}


def tick_oracle(G, seeds, rate, H, silent) -> dict:
    ref = ref_fit(G, H, silent)
    bad = sum(int(tick_fit(g, seeds, rate, silent) != int(f)) for g, f in zip(G, ref))
    return {"genomes": int(len(G)), "mismatched": bad}


def arm_setup(arm, hs):
    silent = arm == "null"
    sel_h = hs["train_corrupt"] if arm == "cell" else hs["train_clean"]
    return silent, sel_h, (RATE if arm == "cell" else 0)


# ------------------------------------------------------------------ one run

def run(ev, family, rs, arm, gens, hs, track=False):
    ai = ARM_INDEX[arm]
    silent, sel_h, _ = arm_setup(arm, hs)
    rng = np.random.Generator(np.random.PCG64([family, rs, ai, STREAM_TAG]))
    srng = np.random.Generator(np.random.PCG64([family + 1, rs, ai, STREAM_TAG]))
    arch = Archive()
    t0, c0 = time.perf_counter(), time.process_time()
    offers = offer_bad = 0
    for _ in range(gens):
        B = init(rng, BATCH) if not arch.cells else mutate(rng, arch.sample(srng, BATCH))
        f = ev.fit(B, sel_h, silent)
        if track:
            offers += len(B)
            offer_bad += int((ref_fit(B, sel_h, silent) != f).sum())
        arch.insert(descriptor(B, silent), f, B)
    wall, cpu = time.perf_counter() - t0, time.process_time() - c0
    top, tf = arch.top(TOP)
    recount_bad = int((ref_fit(top, sel_h, silent) != tf).sum())
    hh = hs["held_clean"]
    held = float(ref_fit(top[:1], hh, silent)[0] / hh.sum())
    held_corrupt = float(ref_fit(top[:1], hs["held_corrupt"], silent)[0] / hh.sum())
    scr = scrambled_yield(top[0], HELD, silent, [STREAM_TAG, family, rs, ai, 99])
    enc = encode(top[:1])[0]
    cb = split(top[:1])[1][0]
    act = cb[np.zeros_like(enc)] if silent else cb[enc]
    tr_clean = int(ref_fit(top[:1], hs["train_clean"], silent)[0])
    tr_corrupt = int(ref_fit(top[:1], hs["train_corrupt"], silent)[0])
    info = {"gens_done": gens, "genomes_evaluated": gens * BATCH, "search_wall_s": round(wall, 3),
            "search_cpu_s": round(cpu, 3), "archive_cells": len(arch.cells), "train_fit_top1": int(tf[0]),
            "train_yield_top1_clean": tr_clean / hs["train_clean"].sum(),
            "train_fit_top1_clean": tr_clean, "train_fit_top1_corrupt": tr_corrupt,
            "pressure_moves_top1_train_fit": bool(tr_clean != tr_corrupt),
            "held_yield_top1": held, "held_yield_top1_under_rate16": held_corrupt,
            "held_scrambled_top1": scr, "scramble_lowers": bool(scr < held),
            "symbols_used_top1": int(len(np.unique(enc))), "actions_used_top1": int(len(np.unique(act))),
            "top1_hex": top[0].tobytes().hex(),
            "top1_sha256": hashlib.sha256(top[0].tobytes()).hexdigest(), "recount_mismatched_top16": recount_bad,
            "offers_audited": offers, "offers_mismatched": offer_bad}
    return info, top


def score(held, lowers, control, floor) -> dict:
    q = np.percentile(held, [25, 50, 75])
    qc = np.percentile(control, [25, 50, 75])
    bar = float(qc[1] - 0.5 * (qc[2] - qc[0]))
    n_low = int(sum(lowers))
    return {"median": float(q[1]), "iqr": float(q[2] - q[0]), "control_median": float(qc[1]),
            "control_iqr": float(qc[2] - qc[0]), "bar": bar, "floor": floor, "P1_parity": bool(q[1] >= bar),
            "P2_above_floor": bool(q[1] > floor), "P3_scramble_lowers_runs": n_low, "P3_uses_channel": n_low >= P3_MIN,
            "n": len(held)}


def hists():
    return {"train_clean": joint_hist(TRAIN, 0), "train_corrupt": joint_hist(TRAIN, RATE),
            "held_clean": joint_hist(HELD, 0), "held_corrupt": joint_hist(HELD, RATE)}


def binding_evidence(ev, hs) -> dict:
    """Measured G2 evidence, before any run: does the pressure move fitness, and can both cheat oracles fire."""
    rng = np.random.Generator(np.random.PCG64([STREAM_TAG, 1]))
    G = np.concatenate([init(rng, 256), planted()])
    clean = ref_fit(G, hs["train_clean"])
    corrupt = ref_fit(G, hs["train_corrupt"])
    cb = cheat_oracle(ev, G, hs["train_corrupt"], False, "cb")
    nz = cheat_oracle(ev, G, hs["train_corrupt"], False, "noise")
    return {"intervention_magnitude": int((clean != corrupt).sum()), "oracle_eligible": min(cb["eligible"],
                                                                                            nz["eligible"]),
            "genomes": int(len(G)), "cheat_cb": cb, "cheat_noise": nz}


def job(ctx, gens: int = GENS, exp_id: str = EXP):
    from primordial.score import anti_prior as AP
    if not gens:
        raise ValueError("GENS not set")
    ev = GBEval()
    hs = hists()
    floor = floor_of(hs["held_clean"])
    runs = [(f, rs) for f in FAMILIES for rs in range(RUNS_PER_FAMILY)]
    todo = [("control", f, rs) for f, rs in runs] + [("null", f, rs) for f, rs in runs] + [("null_check", 0, 0)] + \
        [("cell", f, rs) for f, rs in runs]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": [], "null": []},
                                   "lowers": {"cell": [], "null": []},
                                   "clean": {"cell": True, "control": True, "null": True},
                                   "cpu": {"cell": 0.0, "control": 0.0, "null": 0.0}, "null_check": None,
                                   "ref": False}
    if not st["ref"]:
        evid = binding_evidence(ev, hs)
        pc = AP.binding_precheck(CELL, evidence={k: evid[k] for k in ("intervention_magnitude", "oracle_eligible")})
        hand = hand_genome()
        ctx.emit({"kind": "reference", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "gens": gens, "batch": BATCH,
                  "genome_bytes": GLEN, "rate": RATE, "floor_held": floor, "p3_min_runs": P3_MIN,
                  "hand_yield": {"train_clean": float(ref_fit(hand[None], hs["train_clean"])[0] / hs["train_clean"].sum()),
                                 "train_corrupt": float(ref_fit(hand[None], hs["train_corrupt"])[0]
                                                        / hs["train_clean"].sum()),
                                 "held_clean": float(ref_fit(hand[None], hs["held_clean"])[0] / hs["held_clean"].sum()),
                                 "held_corrupt": float(ref_fit(hand[None], hs["held_corrupt"])[0]
                                                       / hs["held_clean"].sum())},
                  "train_flipped_tick_share": float(hs["train_corrupt"][:, 1:].sum() / hs["train_corrupt"].sum()),
                  "binding_evidence": evid,
                  "binding_precheck": {"ok": pc["ok"], "version": pc["version"], "reasons": pc["reasons"],
                                       "basis": {c: pc["checks"][c]["basis"] for c in pc["checks"]}},
                  "order": "binding precheck, control, null, NULL_CHECK, cell", "status": "control",
                  "ts": round(time.time(), 3)})
        if not pc["ok"]:
            ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL,
                      "primary": "INELIGIBLE", "reasons": pc["reasons"], "status": "aborted",
                      "reason": "measured binding pre-check failed before any run", "ts": round(time.time(), 3)})
            return
        st["ref"] = True
        ctx.checkpoint(st)
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        arm, fam, rs = todo[st["next"]]
        if arm == "null_check":
            sc = score(st["held"]["null"], st["lowers"]["null"], st["held"]["control"], floor)
            passes = bool(sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_channel"]
                          and st["clean"]["null"] and st["clean"]["control"])
            st["null_check"] = {"null_predicate": "PASS" if passes else "FAIL", **sc,
                                "oracle_clean_null": st["clean"]["null"],
                                "oracle_clean_control": st["clean"]["control"]}
            ctx.emit({"kind": "null_check", "exp_id": exp_id, **st["null_check"],
                      "rule": "the planted null must FAIL the predicate before any cell-arm row", "status": "control",
                      "ts": round(time.time(), 3)})
            if passes:
                ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL,
                          "primary": "PREDICATE_PASSES_PLANTED_NULL", "null_check": st["null_check"],
                          "status": "aborted", "reason": "predicate rewrite required before any cell-arm row",
                          "ts": round(time.time(), 3)})
                return
            st["next"] += 1
            ctx.checkpoint(st)
            continue
        cell = {"cell": CELL, "control": CELL_CTRL, "null": CELL_NULL}[arm]
        silent, sel_h, rate = arm_setup(arm, hs)
        first = fam == FAMILIES[0] and rs == 0
        t0, c0 = time.perf_counter(), time.process_time()
        info, top = run(ev, fam, rs, arm, gens, hs, track=first)
        ok = info["recount_mismatched_top16"] == 0 and info["offers_mismatched"] == 0
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
               "genome_bytes": GLEN, "reader": "top1_train", "selection_rate": rate, **info,
               "status": "record" if arm == "cell" else "control"}
        if first:
            G = np.concatenate([top, planted()])
            o = {"cheat_cb": cheat_oracle(ev, G, sel_h, silent, "cb"),
                 "tick": tick_oracle(G, TRAIN, rate, sel_h, silent)}
            o["ok"] = bool(ok and o["cheat_cb"]["eligible"] > 0 and o["cheat_cb"]["share"] >= 0.9
                           and o["tick"]["mismatched"] == 0)
            if arm == "cell":
                o["cheat_noise"] = cheat_oracle(ev, G, sel_h, silent, "noise")
                o["ok"] = o["ok"] and o["cheat_noise"]["eligible"] > 0 and o["cheat_noise"]["share"] >= 0.9
            row["oracles"] = o
            ok = o["ok"]
        st["clean"][arm] = bool(st["clean"][arm] and ok)
        row["wall_s"], row["cpu_s"] = round(time.perf_counter() - t0, 3), round(time.process_time() - c0, 3)
        st["cpu"][arm] += row["cpu_s"]
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(info["held_yield_top1"])
        if arm != "control":
            st["lowers"][arm].append(info["scramble_lowers"])
        ctx.emit(row)
        st["next"] += 1
        ctx.checkpoint(st)
        ctx.progress(st["next"], len(todo) - st["next"])
    sc = score(st["held"]["cell"], st["lowers"]["cell"], st["held"]["control"], floor)
    ok_all = st["clean"]["cell"] and st["clean"]["control"]
    full = all(len(st["held"][a]) == len(runs) for a in ("cell", "control"))
    vacuous = sc["iqr"] == 0 and sc["control_iqr"] == 0 and sc["median"] == sc["control_median"]
    primary = "INDETERMINATE" if not (ok_all and full) else "VACUOUS" if vacuous else \
        ("PASS" if sc["P1_parity"] and sc["P2_above_floor"] and sc["P3_uses_channel"] else "FAIL")
    ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL,
              "runs_total": len(st["held"]["cell"]), "rng_family_count": len(FAMILIES),
              "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
              "n_per_family": {str(f): RUNS_PER_FAMILY for f in FAMILIES}, "gens": gens, **sc,
              "vacuous": bool(vacuous), "null_check": st["null_check"], "oracle_clean": ok_all,
              "arm_cpu_s": {a: round(v, 3) for a, v in st["cpu"].items()}, "primary": primary,
              "clause_a": "none: signal_world_d1 has no floor suite", "status": "record" if ok_all else "cheat",
              "ts": round(time.time(), 3)})


# ------------------------------------------------------------------ dev (no rows)

def dev(gens: int = 10) -> None:
    """No rows: GraphBLAS == reference, tick oracle, cheat eligibility, binding evidence, CPU per generation per arm,
    GENS by the rule. Held values are NOT computed here."""
    from primordial.score import anti_prior as AP
    ev = GBEval()
    hs = hists()
    rng = np.random.Generator(np.random.PCG64(77))
    G = np.concatenate([init(rng, TOP), planted()])
    out = {"floor_held": floor_of(hs["held_clean"]),
           "hand_train_clean_yield": float(ref_fit(planted()[:1], hs["train_clean"])[0] / hs["train_clean"].sum()),
           "gb_eq_ref": {f"{k}|silent={s}": bool(np.array_equal(ev.fit(G, hs[k], s), ref_fit(G, hs[k], s)))
                         for k in ("train_clean", "train_corrupt") for s in (False, True)},
           "tick": {"clean": tick_oracle(G, TRAIN, 0, hs["train_clean"], False),
                    "corrupt": tick_oracle(G, TRAIN, RATE, hs["train_corrupt"], False),
                    "silent": tick_oracle(G, TRAIN, 0, hs["train_clean"], True)},
           "cheat_cb": {"clean": cheat_oracle(ev, G, hs["train_clean"], False, "cb"),
                        "silent": cheat_oracle(ev, G, hs["train_clean"], True, "cb")},
           "cheat_noise": cheat_oracle(ev, G, hs["train_corrupt"], False, "noise")}
    evid = binding_evidence(ev, hs)
    pc = AP.binding_precheck(CELL, evidence={k: evid[k] for k in ("intervention_magnitude", "oracle_eligible")})
    out["binding_evidence"] = evid
    out["binding_precheck"] = {"ok": pc["ok"], "reasons": pc["reasons"],
                               "basis": {c: pc["checks"][c]["basis"] for c in pc["checks"]}}
    per = {}
    for arm in ("control", "null", "cell"):
        info, _ = run(ev, 4200, 0, arm, gens, hs, track=True)
        per[arm] = {"cpu_s_per_gen": round(info["search_cpu_s"] / gens, 5),
                    "wall_s_per_gen": round(info["search_wall_s"] / gens, 5),
                    "offers_mismatched": info["offers_mismatched"], "recount_mismatched": info["recount_mismatched_top16"]}
    out["per_arm"] = per
    c = time.process_time()
    cheat_oracle(ev, G, hs["train_corrupt"], False, "cb")
    cheat_oracle(ev, G, hs["train_corrupt"], False, "noise")
    tick_oracle(G, TRAIN, RATE, hs["train_corrupt"], False)
    oracle_cpu = (time.process_time() - c) * 3
    unit = sum(per[a]["cpu_s_per_gen"] for a in per) * 32
    proj = {str(Gn): round((unit * Gn + oracle_cpu) * 1.25, 1) for Gn in GENS_CHOICES}
    fits = [Gn for Gn in GENS_CHOICES if (unit * Gn + oracle_cpu) * 1.25 <= CPU_CAP]
    out["projected_job_cpu_s"] = proj
    out["gens_by_rule"] = max(fits) if fits else "INFEASIBLE"
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        dev(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
