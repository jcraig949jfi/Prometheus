"""C-R8-AP-03 (ANTI_PRIOR, cell assigned by code): tucker / nk_stub / regime_switching / redis_lua / none
(anti_prior.assign exp_id C-R8-AP-03, round 8, from the G2 binding-eligible candidate list, seed 20260921).

The experimenter received only the cell; the prior, arm, rank and quantile are unread (pm:prior:* never read). No
definition of this cell existed; the definitions below are fixed before any run. nk_stub is not a screened graphworld
world: landscape rows only, no clause A claim.

G2 BASIS, disclosed: G2-v1's regime rule (regime_reaches_payoff) applies only to graphworld worlds, so no rule applies to
this cell. The job re-runs anti_prior.binding_precheck(cell, evidence=...) with MEASURED evidence in committed rows
before any run and aborts INELIGIBLE if it fails (as C-R8-AP-01/02).

  world     lane E's NK stub (N=64, K=4). A seed is a LANDSCAPE (C-R2-09 / C-R6-AP-01): selection on 8 TRAIN landscapes
            (9100..9107); score on 64 HELD landscapes (30000..30063); value = mean NK fitness per landscape.
  brain     tucker, C-R6-AP-01's representation unchanged: locus j's 32-entry contribution row / 65535 is a 2x2x2x2x2
            tensor X_j; W = G x_0 U_0 ... x_4 U_4 (core [2]^5, factors [2, 2]); s_j = <W, X_j> + b; bit_j = [s_j > 0].
            Genome 53 float32 = 212 bytes. Target-blind (the brain reads only the landscape's table). Init N(0, 1);
            mutation gene + N(0, .2) with p 1/8. Planted HAND = greedy own-bit code (U = I, G[idx] = +1 if idx odd else
            -1, b = 0); planted ONES = all zero but b = 1 (every bit 1).
  pressure  regime_switching over the locus axis, C-R7-AP-04's period rule taken unchanged: the world generator emits
            regime_period in {8, 16, 32, 64}; the SMALLEST emitted period with >= 2 flip windows in the axis length
            (64 loci) -> period 8. A locus j with (j // 8) % 2 == 1 is in the switched regime: its contribution row is
            negated, T'[j] = 65535 - T[j]. The switched table is the WORLD: both the NK fitness and the table the brain
            reads are T' (the flip is observable, the condition under which G2's graphworld regime rule accepts a reader).
            It acts during SELECTION. Every arm is SCORED on HELD in the unswitched world (period 0) through its own
            observation mechanism (the table for control and cell; silence for the null): a common reference.
            STRUCTURAL NOTE, stated before any run: X' = 1 - X, so s' = sum(W) + 2b - s; the exact greedy code
            (sum W = 0, b = 0) is regime-equivariant and scores the same selection fitness in both worlds. A code the
            search finds is equivariant only if sum(W) + 2b is small relative to |s|; that is what the pressure selects on.
  substrate redis_lua: NK evaluation (per-landscape TRUE table in Redis; bit decode + neighbourhood index + the regime
            negation by period + sum in Lua; C-R6-AP-02's evaluator plus a period argument) and E's LuaArchive (atomic insert,
            seeded sampler) run inside lane C's Redis :6392. numpy computes the Tucker contraction.
  search    MAP-Elites, batch 128; descriptor (C-R6-AP-01): popcount halves of the bits on TRAIN landscape 0, 33 x 33.
  arms      control  pressure removed: selection on TRAIN in the unswitched world (period 0)
            null     PLANTED NULL = the cell with its mechanism removed: the brain observes nothing (X = 0, s_j = b)
            cell     selection on TRAIN in the switched world (period 8)
  order     all 32 control runs; all 32 null runs; NULL_CHECK row; then the 32 cell runs only if the null FAILED.
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 8301]); sampler [family + 1, run_seed, arm, 8301].
  GENS      rule fixed before the dev check: the largest of {100, 200, 400, 800} whose projected job WALL (96 runs x
            measured wall per generation per arm + oracles, x 1.25) <= 3600 s (wall, because Lua CPU is server-side).
  reader    top1_train: the archive elite with the highest selection fitness (ties: smaller genome bytes); held = its
            mean NK fitness per HELD landscape, unswitched, through the arm's observation.
  PREDICATE for an arm X in {null, cell}:
            P1  median held (X) >= median held (control) - 0.5 * IQR (control)
            P2  median held (X) > FLOOR = max(mean HELD NK of all-zero bits, of all-one bits): exactly the best a brain
                that observes nothing can emit (s_j = b for every locus)
            P3  a scrambled observation (locus j reads row pi(j), a per-landscape permutation of the 64 rows,
                PCG64([8301, family, run_seed, arm, 99])) lowers held in >= 17 of the 32 runs of X
            PASS iff P1 and P2 and P3 and oracles clean. The null must FAIL before the cell runs.
  VACUITY   (fixed before any row) IQR(control) == 0 and IQR(cell) == 0 and median(cell) == median(control) -> VACUOUS.
  BINDING   before any run, in committed rows: evidence = {intervention_magnitude: # of 256 random genomes whose TRAIN
            fitness in the switched world differs from the unswitched one, oracle_eligible: the regime cheat's eligible
            count on those genomes}; binding_precheck(CELL, evidence) must be ok, else INELIGIBLE (aborted), no run.
  oracles   family 4200 run seed 0 of each arm, genomes = top-16 + planted HAND + planted ONES:
            world    Lua fitness and cell == numpy reference (NKWorld tables with the arm's regime, bits from the arm's
                     observation) on EVERY offer of that run (exact); EVERY run: top-16 archive fitness == numpy recount
                     from the STORED bytes (exact)
            k3       Lua with a K=3 window mismatches the numpy reference on >= 90% of eligible (genome, landscape) rows
                     (bits not all zero), >= 1 eligible; all arms
            brain    float64 reference W (explicit loops) == float32 decision bits on the oracle genomes x TRAIN (ties
                     |s| < 1e-5 (sum|W| + |b| + 1) excluded); cheat identity_last_factor mismatches >= 90% of ELIGIBLE
                     rows, >= 1 eligible; control and cell arms. The null is EXEMPT from the cheat by rule (X = 0 makes
                     W irrelevant, so no row is eligible); its honest brain check still binds.
            regime   cell arm only: Lua with period 0 mismatches the switched numpy reference on >= 90% of ELIGIBLE
                     genomes (the reference differs between periods 8 and 0), >= 1 eligible
  report    (not judged) held in the switched world for control and cell; sum(W) + 2b of the top1; HAND and ONES held;
            Redis server CPU delta per run.
  not claimed  clause A; any mechanism; any other period.

  worker:  job = primordial.cohorts.c.r8_ap03_tucker_nk_regime_lua:job
  dev:     python -m primordial.cohorts.c.r8_ap03_tucker_nk_regime_lua dev [gens]   (no rows)
"""
from __future__ import annotations

import hashlib
import json
import sys
import time

import numpy as np

from primordial.cohorts.c.r6_ap01_tucker_nk_cpu_ttl_graphblas import E, GLEN, M, NG, TIE_REL, init, join, mutate, \
    ref_W, split
from primordial.qd.stubworld import GRID, K, N_BITS, NKWorld

EXP = "C-R8-AP-03-tucker-nk-regime-lua"
PREDICATE_ID = "C-R8-AP-03"
ROWS = f"primordial/ledger/rows/C/{EXP}.jsonl"
CELL = {"channel": "none", "pressure": "regime_switching", "representation": "tucker", "substrate": "redis_lua",
        "world": "nk_stub"}
CELL_CTRL = dict(CELL, pressure="regime_period0_control")
CELL_NULL = dict(CELL, channel="none_silent_observation_planted_null")
N = N_BITS
PERIOD = 8
TRAIN_SEEDS = np.arange(9100, 9108)
HELD_SEEDS = np.arange(30000, 30064)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
BATCH, TOP = 128, 16
STREAM_TAG = 8301
P3_MIN = 17
GENS_CHOICES = (100, 200, 400, 800)
WALL_CAP = 3600.0
GENS = 800      # no-rows dev check (5 gens per arm, family 4200 run 0): wall/gen control 0.0348, null 0.0340, cell
                # 0.0358 (Redis server CPU ~0.028-0.030/gen) -> projected job wall 100: 419, 200: 837, 400: 1674,
                # 800: 3348 (cap 3600)
PORT = 6392
KEY = "pm:c:r8-ap03:nk:{}:{}"      # seed, period
ARM_INDEX = {"cell": 0, "control": 1, "null": 2}

EVAL_LUA = r"""
local gs, win, period = ARGV[1], tonumber(ARGV[2]), tonumber(ARGV[3])
local tb = redis.call('GET', KEYS[1])
local sbyte, floor = string.byte, math.floor
local fits, cells = {}, {}
for gi = 0, #gs / 8 - 1 do
  local b = {}
  for j = 0, 63 do
    local byte = sbyte(gs, gi * 8 + floor(j / 8) + 1)
    b[j] = floor(byte / 2 ^ (7 - j % 8)) % 2
  end
  local f, d0, d1 = 0, 0, 0
  for j = 0, 63 do
    local idx = 0
    for t = 0, win - 1 do idx = idx + b[(j + t) % 64] * 2 ^ t end
    local o = (j * 32 + idx) * 2
    local lo, hi = sbyte(tb, o + 1, o + 2)
    local v = lo + hi * 256
    if period > 0 and floor(j / period) % 2 == 1 then v = 65535 - v end
    f = f + v
    if j < 32 then d0 = d0 + b[j] else d1 = d1 + b[j] end
  end
  fits[gi + 1] = struct.pack('<i4', f)
  cells[gi + 1] = struct.pack('<I4', d0 * 33 + d1)
end
return {table.concat(fits), table.concat(cells)}
"""


def switched(table, period):
    """[.., 64, 32] true table -> the regime world's table (negated rows in odd windows)."""
    if not period:
        return table
    flip = ((np.arange(N) // period) % 2 == 1)[:, None]
    return np.where(flip, 65535 - table, table)


class Lands:
    def __init__(self, seeds):
        self.seeds = np.asarray(seeds)
        self.worlds = [NKWorld(int(s)) for s in seeds]
        self.table = np.stack([w.table for w in self.worlds]).astype(np.int64)            # [L, 64, 32]
        self.tabs = {0: self.table, PERIOD: switched(self.table, PERIOD)}

    def x5(self, period, silent=False, perm=None):
        t = self.tabs[period]
        if perm is not None:
            t = t[np.arange(len(t))[:, None], perm]
        x = np.zeros_like(t, np.float64) if silent else t / 65535.0
        return x.astype(np.float32).reshape(len(self.seeds), N, 2, 2, 2, 2, 2), x


def scores(g, x5, cheat=False):
    G, U, b = split(g)
    if cheat:
        U = U.copy()
        U[:, M - 1] = np.eye(2, dtype=np.float32)
    s = np.einsum("ljabcde,pak,pbm,pcn,pdo,peq,pkmnoq->plj", x5, U[:, 0], U[:, 1], U[:, 2], U[:, 3], U[:, 4], G,
                  optimize=True)
    return s + b[:, None, None]


def ref_nk(bits, lands, period) -> np.ndarray:
    """numpy reference: NKWorld index rule on the regime table -> int64 [P, L]."""
    cols = (np.arange(N)[:, None] + np.arange(K + 1)[None, :]) % N
    idx = bits.astype(np.int64)[:, :, cols] @ (1 << np.arange(K + 1))
    t = lands.tabs[period]
    L = t.shape[0]
    return t[np.arange(L)[None, :, None], np.arange(N)[None, None, :], idx].sum(2)


class LuaEval:
    def __init__(self, r, lands):
        self.r, self.lands = r, lands
        for s, w in zip(lands.seeds, lands.worlds):
            r.set(KEY.format(int(s), 0), w.table.astype("<u2").tobytes())
        self.script = r.register_script(EVAL_LUA)

    def __call__(self, bits, period, window=K + 1):
        """bits uint8 [P, L, 64] -> (fit int64 [P, L], cells of landscape 0 uint32 [P])."""
        P, L = bits.shape[:2]
        fit = np.zeros((P, L), np.int64)
        cells = None
        for li, s in enumerate(self.lands.seeds):
            packed = np.packbits(bits[:, li], axis=1)
            f, c = self.script(keys=[KEY.format(int(s), 0)], args=[packed.tobytes(), window, period])
            fit[:, li] = np.frombuffer(f, "<i4")
            if li == 0:
                cells = np.frombuffer(c, "<u4").astype(np.uint32)
        return fit, cells


def hand_genome():
    G = np.where(np.arange(E) & 1, 1.0, -1.0).reshape(1, 2, 2, 2, 2, 2)
    U = np.tile(np.eye(2), (1, M, 1, 1))
    return join(G, U, np.zeros(1))[0]


def ones_genome():
    return join(np.zeros((1, E)), np.zeros((1, M, 2, 2)), np.ones(1))[0]


def planted():
    return np.stack([hand_genome(), ones_genome()])


def server_cpu(r) -> float:
    i = r.info("cpu")
    return float(i["used_cpu_sys"]) + float(i["used_cpu_user"])


def arm_setup(arm):
    return (PERIOD if arm == "cell" else 0), arm == "null"


def bits_of(g, lands, period, silent, perm=None):
    x5, _ = lands.x5(period, silent, perm)
    return (scores(g, x5) > 0).astype(np.uint8)


# ------------------------------------------------------------------ oracles

def brain_oracle(G, lands, period, silent) -> dict:
    x5, x64 = lands.x5(period, silent)
    s, sc = scores(G, x5), scores(G, x5, cheat=True)
    Gc, U, b = split(G)
    bad = ties = elig = caught = 0
    for p in range(len(G)):
        W, Wc = ref_W(Gc[p], U[p]), ref_W(Gc[p], U[p], cheat=True)
        tie = TIE_REL * (np.abs(W).sum() + abs(float(b[p])) + 1.0)
        tie_c = TIE_REL * (np.abs(Wc).sum() + abs(float(b[p])) + 1.0)
        rr = x64 @ W + float(b[p])
        rc = x64 @ Wc + float(b[p])
        t = np.abs(rr) < tie
        ties += int(t.sum())
        bad += int((((s[p] > 0) != (rr > 0)) & ~t).any(axis=1).sum())
        e = (((rc > 0) != (rr > 0)) & ~t & ~(np.abs(rc) < tie_c)).any(axis=1)
        elig += int(e.sum())
        caught += int(((((sc[p] > 0) != (rr > 0)) & ~t).any(axis=1) & e).sum())
    return {"rows": int(len(G) * len(lands.seeds)), "honest_mismatched_rows": bad, "tie_loci": ties,
            "cheat_eligible_rows": elig, "cheat_share": round(caught / elig, 4) if elig else 0.0}


def k3_oracle(ev, bits, lands, period) -> dict:
    ref = ref_nk(bits, lands, period)
    ch, _ = ev(bits, period, window=K)
    el = bits.any(axis=2)
    n = int(el.sum())
    return {"eligible": n, "share": round(float((ch != ref)[el].mean()), 4) if n else 0.0}


def regime_oracle(ev, bits, lands) -> dict:
    ref = ref_nk(bits, lands, PERIOD).sum(1)
    el = ref != ref_nk(bits, lands, 0).sum(1)
    ch = ev(bits, 0)[0].sum(1)
    caught = int(((ch != ref) & el).sum())
    return {"eligible": int(el.sum()), "caught": caught, "share": round(caught / int(el.sum()), 4) if el.any() else 0.0}


# ------------------------------------------------------------------ one run

def run(r, ev, family, rs, arm, gens, train, held, track=False):
    from primordial.qd.archive import LuaArchive
    ai = ARM_INDEX[arm]
    period, silent = arm_setup(arm)
    x5, _ = train.x5(period, silent)
    rng = np.random.Generator(np.random.PCG64([family, rs, ai, STREAM_TAG]))
    arch = LuaArchive(r, f"c-r8-ap03-{family}-{rs}-{ai}", GLEN, sampler_seed=[family + 1, rs, ai, STREAM_TAG])
    arch.clear()
    zeros = np.zeros((BATCH, 2), np.uint32)
    s0, t0, c0 = server_cpu(r), time.perf_counter(), time.process_time()
    offers = offer_bad = 0
    for _ in range(gens):
        par = arch.sample(BATCH)
        g = init(rng, BATCH) if len(par) == 0 else mutate(rng, par)
        bits = (scores(g, x5) > 0).astype(np.uint8)
        fit, cells = ev(bits, period)
        if track:
            offers += len(g)
            rc = (bits[:, 0, :32].sum(1) * GRID + bits[:, 0, 32:].sum(1)).astype(np.uint32)
            offer_bad += int(((ref_nk(bits, train, period) != fit).any(1) | (rc != cells)).sum())
        arch.insert(cells, fit.sum(1).astype(np.int32), g, zeros)
    wall, cpu, scpu = time.perf_counter() - t0, time.process_time() - c0, server_cpu(r) - s0
    el = arch.dump()
    arch.clear()
    order = sorted(el.values(), key=lambda v: (-v[0], v[1]))[:TOP]
    top = np.frombuffer(b"".join(v[1] for v in order), np.uint8).reshape(-1, GLEN)
    tf = np.array([v[0] for v in order], np.int64)
    recount_bad = int((ref_nk(bits_of(top, train, period, silent), train, period).sum(1) != tf).sum())
    nh = len(held.seeds)
    held_v = float(ref_nk(bits_of(top[:1], held, 0, silent), held, 0).sum() / nh)
    held_sw = float(ref_nk(bits_of(top[:1], held, PERIOD, silent), held, PERIOD).sum() / nh)
    prng = np.random.Generator(np.random.PCG64([STREAM_TAG, family, rs, ai, 99]))
    perm = np.argsort(prng.random((nh, N)), axis=1)
    scr = float(ref_nk(bits_of(top[:1], held, 0, silent, perm), held, 0).sum() / nh)
    Gc, U, b = split(top[:1])
    W = ref_W(Gc[0], U[0])
    info = {"gens_done": gens, "genomes_evaluated": gens * BATCH, "search_wall_s": round(wall, 3),
            "search_cpu_s": round(cpu, 3), "redis_server_cpu_s": round(scpu, 3), "archive_cells": len(el),
            "train_fit_top1": int(tf[0]), "train_mean_top1": float(tf[0] / len(train.seeds)),
            "held_mean_top1": held_v, "held_mean_top1_switched_world": held_sw, "held_scrambled_top1": scr,
            "scramble_lowers": bool(scr < held_v), "top1_sumW_plus_2b": float(W.sum() + 2 * float(b[0])),
            "top1_abs_W_sum": float(np.abs(W).sum()), "top1_b": float(b[0]),
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


def floor_of(held) -> float:
    z = np.zeros((1, len(held.seeds), N), np.uint8)
    return float(max(ref_nk(z, held, 0).sum(), ref_nk(z + 1, held, 0).sum()) / len(held.seeds))


def binding_evidence(ev, train) -> dict:
    rng = np.random.Generator(np.random.PCG64([STREAM_TAG, 1]))
    G = np.concatenate([init(rng, 256), planted()])
    b_sw = bits_of(G, train, PERIOD, False)
    b_0 = bits_of(G, train, 0, False)
    f_sw = ref_nk(b_sw, train, PERIOD).sum(1)
    f_0 = ref_nk(b_0, train, 0).sum(1)
    ro = regime_oracle(ev, b_sw, train)
    return {"intervention_magnitude": int((f_sw != f_0).sum()), "oracle_eligible": ro["eligible"],
            "genomes": int(len(G)), "regime_cheat": ro}


def job(ctx, gens: int = GENS, port: int = PORT, exp_id: str = EXP):
    import redis
    from primordial.score import anti_prior as AP
    if not gens:
        raise ValueError("GENS not set")
    r = redis.Redis(host="127.0.0.1", port=port)
    train, held = Lands(TRAIN_SEEDS), Lands(HELD_SEEDS)
    ev = LuaEval(r, train)
    floor = floor_of(held)
    runs = [(f, rs) for f in FAMILIES for rs in range(RUNS_PER_FAMILY)]
    todo = [("control", f, rs) for f, rs in runs] + [("null", f, rs) for f, rs in runs] + [("null_check", 0, 0)] + \
        [("cell", f, rs) for f, rs in runs]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": [], "null": []},
                                   "lowers": {"cell": [], "null": []},
                                   "clean": {"cell": True, "control": True, "null": True},
                                   "wall": {"cell": 0.0, "control": 0.0, "null": 0.0}, "null_check": None,
                                   "ref": False}
    if not st["ref"]:
        evid = binding_evidence(ev, train)
        pc = AP.binding_precheck(CELL, evidence={k: evid[k] for k in ("intervention_magnitude", "oracle_eligible")})
        hand, ones = planted()[:1], planted()[1:]
        ctx.emit({"kind": "reference", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "gens": gens, "batch": BATCH,
                  "genome_bytes": GLEN, "period": PERIOD, "floor_held": floor, "p3_min_runs": P3_MIN,
                  "hand_held": float(ref_nk(bits_of(hand, held, 0, False), held, 0).sum() / len(HELD_SEEDS)),
                  "hand_train_unswitched": float(ref_nk(bits_of(hand, train, 0, False), train, 0).sum() / 8),
                  "hand_train_switched": float(ref_nk(bits_of(hand, train, PERIOD, False), train, PERIOD).sum() / 8),
                  "ones_held": float(ref_nk(bits_of(ones, held, 0, False), held, 0).sum() / len(HELD_SEEDS)),
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
        period, silent = arm_setup(arm)
        first = fam == FAMILIES[0] and rs == 0
        t0, c0 = time.perf_counter(), time.process_time()
        info, top = run(r, ev, fam, rs, arm, gens, train, held, track=first)
        ok = info["recount_mismatched_top16"] == 0 and info["offers_mismatched"] == 0
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
               "genome_bytes": GLEN, "reader": "top1_train", "selection_period": period, **info,
               "status": "record" if arm == "cell" else "control"}
        if first:
            G = np.concatenate([top, planted()])
            bits = bits_of(G, train, period, silent)
            o = {"k3": k3_oracle(ev, bits, train, period), "brain": brain_oracle(G, train, period, silent)}
            o["ok"] = bool(ok and o["k3"]["eligible"] > 0 and o["k3"]["share"] >= 0.9
                           and o["brain"]["honest_mismatched_rows"] == 0)
            if arm == "null":
                o["brain_cheat_rule"] = "EXEMPT for the null by rule, fixed before any run (X = 0: W is irrelevant)"
            else:
                o["ok"] = o["ok"] and o["brain"]["cheat_eligible_rows"] > 0 and o["brain"]["cheat_share"] >= 0.9
            if arm == "cell":
                o["regime"] = regime_oracle(ev, bits, train)
                o["ok"] = o["ok"] and o["regime"]["eligible"] > 0 and o["regime"]["share"] >= 0.9
            row["oracles"] = o
            ok = o["ok"]
        st["clean"][arm] = bool(st["clean"][arm] and ok)
        row["wall_s"], row["cpu_s"] = round(time.perf_counter() - t0, 3), round(time.process_time() - c0, 3)
        st["wall"][arm] += row["wall_s"]
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(info["held_mean_top1"])
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
              "arm_wall_s": {a: round(v, 3) for a, v in st["wall"].items()}, "primary": primary,
              "clause_a": "none: nk_stub is not a screened graphworld world", "status": "record" if ok_all else "cheat",
              "ts": round(time.time(), 3)})


# ------------------------------------------------------------------ dev (no rows)

def dev(gens: int = 5) -> None:
    """No rows, no held value computed: Lua == numpy, oracle eligibility, binding evidence, wall/gen, GENS."""
    import redis
    from primordial.score import anti_prior as AP
    r = redis.Redis(host="127.0.0.1", port=PORT)
    train = Lands(TRAIN_SEEDS)
    ev = LuaEval(r, train)
    rng = np.random.Generator(np.random.PCG64(77))
    G = np.concatenate([init(rng, 16), planted()])
    out = {}
    for period in (0, PERIOD):
        for silent in (False, True):
            bits = bits_of(G, train, period, silent)
            out[f"lua_eq_numpy|p{period}|silent={silent}"] = bool(np.array_equal(ev(bits, period)[0],
                                                                                 ref_nk(bits, train, period)))
            out[f"k3|p{period}|silent={silent}"] = k3_oracle(ev, bits, train, period)
            out[f"brain|p{period}|silent={silent}"] = brain_oracle(G, train, period, silent)
    out["regime"] = regime_oracle(ev, bits_of(G, train, PERIOD, False), train)
    evid = binding_evidence(ev, train)
    pc = AP.binding_precheck(CELL, evidence={k: evid[k] for k in ("intervention_magnitude", "oracle_eligible")})
    out["binding_evidence"] = evid
    out["binding_precheck"] = {"ok": pc["ok"], "reasons": pc["reasons"],
                               "basis": {c: pc["checks"][c]["basis"] for c in pc["checks"]}}
    held = Lands(HELD_SEEDS[:2])                 # timing only
    per = {}
    for arm in ("control", "null", "cell"):
        info, _ = run(r, ev, 4200, 0, arm, gens, train, held, track=False)
        per[arm] = {"wall_s_per_gen": round(info["search_wall_s"] / gens, 5),
                    "cpu_s_per_gen": round(info["search_cpu_s"] / gens, 5),
                    "server_cpu_s_per_gen": round(info["redis_server_cpu_s"] / gens, 5),
                    "recount_mismatched": info["recount_mismatched_top16"]}
    out["per_arm"] = per
    t = time.perf_counter()
    bits = bits_of(G, train, PERIOD, False)
    brain_oracle(G, train, PERIOD, False)
    k3_oracle(ev, bits, train, PERIOD)
    regime_oracle(ev, bits, train)
    info, _ = run(r, ev, 4200, 0, "cell", gens, train, held, track=True)
    oracle_wall = (time.perf_counter() - t - info["search_wall_s"] + info["search_wall_s"] * 0.2) * 3
    unit = sum(per[a]["wall_s_per_gen"] for a in per) * 32
    proj = {str(Gn): round((unit * Gn + oracle_wall) * 1.25, 1) for Gn in GENS_CHOICES}
    fits = [Gn for Gn in GENS_CHOICES if (unit * Gn + oracle_wall) * 1.25 <= WALL_CAP]
    out["oracle_wall_s_x3"] = round(oracle_wall, 2)
    out["projected_job_wall_s"] = proj
    out["gens_by_rule"] = max(fits) if fits else "INFEASIBLE"
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        dev(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
