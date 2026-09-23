"""C-R7-AP-03 (ANTI_PRIOR, cell assigned by code): small_program / signal_world_d1 / byte_charge / falkordb_cypher /
metered_stream (anti_prior.assign exp_id C-R7-AP-03, round 7).

The experimenter received only the cell; the prior and the arm are unread. signal_world_d1 is not a screened world: no
floor suite, no clause A claim. The definitions below are fixed before any run.

  world     lane D's D1 signal world (primordial.lingua.signal): T = 64 ticks, R in [0, 256) drawn per tick from the
            episode seed (signal.r_stream); slot 1 is right iff act == R >> 5.
  channel   metered_stream = D1's own settlement (signal.NpChannel order, C-R5-01): the credit for last tick's right
            action lands, then a send of k bits is charged alpha_int * k if the sender can pay; an unaffordable send is
            NOT delivered (slot 1 hears silence 0). D1 audit constants alpha_int 2, y_int 3, start 8. Fitness = final
            charge summed over the selection episodes.
  brain     small_program (C-R2-02's representation, adapted to D1's 8-bit register). Genome 24 bytes:
            16 B encoder program = 8 instructions x (op, arg), then 8 B codebook decoder (lane E's form).
              b = R; per instruction op = op_byte % 8, j = arg & 7, v = arg >> 6:
                0 nop            1 set bit j          2 flip bit j        3 set bits j..j+3 (mod 8)
                4 clear bits j..j+3 (mod 8)           5 rotate left by j  6 b ^= rotl(b, j)
                7 flip every bit i with (i - j) % (v + 2) == 0
              sym = b & 7 (3 bits; 0 is D1 silence, so a non-zero symbol sends k = 3 bits); act = cb[sym] % 8.
            The program is target-blind (it reads only R). Init: bytes uniform. Mutation: each of the 16 program bytes
            replaced uniformly with p = 1/16 (C-R2-02's rule); each codebook byte redrawn with p = 1/8 (E7's rule).
  pressure  byte_charge (cell arm, AP-02's rule at D1's scale): selection fitness = SCALE * (summed TRAIN charge)
            - BETA * functional bytes, functional bytes = 2 * (non-nop instructions) + 8 (the codebook),
            SCALE = 100 and BETA = round(0.01 * RANDOM_TOTAL * SCALE), RANDOM_TOTAL = len(TRAIN) * the mean final charge
            per TRAIN episode of 256 uniform genomes (PCG64(5)). The rate is AP-02's 1% of the world's own random
            baseline per byte; the x100 scaling only keeps it in integers. Disclosed, from the no-rows dev check BEFORE
            any predicate: D1's random baseline is ~7.29 charge per episode, so AP-02's unscaled formula
            floor(0.01 * mean) * len(TRAIN) gives BETA = 0 -- a vacuous pressure with the cell arm identical to the
            control (the round 5 D1 vacuity trap). The scaling is what makes the drawn pressure bind at all.
            control arm: no charge (the same SCALE, so the arms differ only by the byte term).
  substrate falkordb_cypher: every settlement tick of every selection evaluation is ONE FalkorDB GRAPH.QUERY on lane C's
            Redis 8 + FalkorDB :6392 (the b1/falkor_world pattern: env state in node properties, one query per tick).
            numpy decodes the program into its 256-entry action table and does the reader arithmetic (disclosed, as
            C-R6-AP-01's numpy Tucker contraction and C-R7-AP-02's numpy decode).
            LOCKSTEP, measured before the design was frozen: all 32 runs of an arm advance inside the SAME tick queries
            (32 runs x 128 genomes x 8 episodes = 32,768 envs per tick). Runs keep their own populations, archives and
            RNG streams, so lockstep is EXACT, not an approximation; it only amortises the query round trip
            (0.652 s per tick for all runs, 41.9 s per generation, against 215 s for 32 separate loops).
            Archive: E's LuaArchive per run (seeded sampler) on :6392, genome 24 bytes (a multiple of 4: C-R7-AP-02's
            defect). Descriptor (C-R5-AP-01): (distinct symbols emitted - 1) * 8 + (distinct actions used - 1), 64 cells.
  arms      cell (byte_charge) vs control (no charge), same GA and sampler streams, same channel, same GENS, batch 128.
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 7401]); sampler [family + 1, run_seed, arm, 7401].
  seeds     TRAIN = episodes 0..7 (selection), HELD = 10,000,000..10,000,255 (the reader), C-R5-01's sets.
  GENS      rule fixed before the dev check, BOTH clauses: the largest of {10, 25, 50, 100} whose projected job wall
            (2 arms x GENS x measured lockstep wall per generation x 1.1) <= 7200 s AND whose per-ARM wall
            (GENS x that measurement x 1.1) <= 1920 s = 80% of the 2400 s checkpointable SEGMENT ceiling -- the job
            checkpoints between arms, so one arm is one uninterruptible segment and a segment overrun is a kill with a
            60 s grace and no mid-arm checkpoint. If 10 fits neither, INFEASIBLE (aborted row + PRODUCTION_CANDIDATE
            with the measured cost). Outcome recorded at GENS below.
  reader    top1_train: the archive elite of that run with the highest selection fitness (ties: lexicographically
            smaller genome bytes); held = its mean final charge per HELD episode under the same metered channel.
  primary   median over the 32 runs of held (cell) >= median (control) - 0.5 * IQR (control). PASS / FAIL only with 32
            runs per arm and oracles clean, else INDETERMINATE.
  oracles   the (4200, run seed 0) slice of each arm, genomes = its top-16 + planted P_SPENDER (a program that emits a
            non-zero symbol on every R with a codebook that never earns: it must go broke, so unaffordable sends are
            guaranteed) + planted P_LAST (a program whose LAST instruction changes the action table):
            world    the Cypher settlement == the numpy NpChannel reference for every env of that slice, in EVERY
                     generation of the run (exact); and EVERY run's top-16 archive fitness == the numpy recount from
                     the STORED genome bytes (exact)
            free     cheat free_unaffordable (the Cypher variant delivers unaffordable sends) changes the final charge
                     on >= 90% of ELIGIBLE envs, >= 1 eligible -- eligible = envs where the numpy reference ITSELF
                     differs under free delivery (C-R7-01 / C-R7-AP-02's form), structural via P_SPENDER. Disclosed:
                     the first draft called an env eligible when it merely had an unaffordable send, which the dev check
                     showed is not the same thing (a codebook can map the symbol to the same action as silence, so 112
                     envs were "eligible" but only 49 could change) -- the gate would have measured the codebook, not
                     the meter.
            brain    a scalar plain-int reference of the program decode (256 R values through the 8 instructions, then
                     the codebook) == the numpy action table on every genome (0 mismatched); cheat skip_last (the 8th
                     instruction not executed) changes the table on >= 90% of ELIGIBLE genomes (the scalar reference
                     itself changes), >= 1 eligible -- structural via P_LAST
            charge   functional bytes == 2 * non-nop + 8, and the cell selection fitness == charge sum - BETA * bytes
                     on the top-16 (exact)
            No oracle's eligibility depends on what evolution picks (the C-R7-AP-01 lesson).
  report    (not judged) RANDOM_MEAN, the hand-code yield, symbols and actions used, non-nop instructions and functional
            bytes of the top1, unaffordable sends per episode, train charge.
  not claimed  clause A (D1 has no floor suite); any mechanism; the prior ledger was not read.

  worker:  job = primordial.cohorts.c.r7_ap03_small_program_d1_bytecharge_falkordb_metered:job
  dev:     python -m primordial.cohorts.c.r7_ap03_small_program_d1_bytecharge_falkordb_metered dev   (no rows)
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time

import numpy as np

from primordial.lingua import signal as S

EXP = "C-R7-AP-03-small-program-d1-bytecharge-falkordb-metered"
PREDICATE_ID = "C-R7-AP-03"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
CELL = {"representation": "small_program", "world": "signal_world_d1", "pressure": "byte_charge",
        "substrate": "falkordb_cypher", "channel": "metered_stream"}
CELL_CTRL = dict(CELL, pressure="byte_charge_off_control")
T = 64
NR, NA, SH = S.N_R, S.N_ACT, S.SHIFT
ALPHA_INT, Y_INT, START = 2, 3, 8
KBITS = 3
N_INSTR, PROG_B, CB_B = 8, 16, 8
GLEN = PROG_B + CB_B                      # 24, a multiple of 4 (C-R7-AP-02's defect)
BATCH, TOP = 128, 16
TRAIN = np.arange(8)
HELD = 10_000_000 + np.arange(256)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
N_RUNS = len(FAMILIES) * RUNS_PER_FAMILY
PORT = 6392
GRAPH = "c_r7_ap03"
STREAM_TAG = 7401
GENS_CHOICES = (10, 25, 50, 100)
WALL_CAP = 7200.0
SCALE = 100                               # selection fitness is SCALE * charge so a 1%-of-baseline byte rate is integral
# No-rows dev check (2 lockstep generations of one arm = 32 runs x 128 genomes x 8 episodes = 32,768 envs per tick):
# 38.613 wall-s per generation -> projected JOB wall 10: 849.5, 25: 2123.7, 50: 4247.5, 100: 8495.0 (cap 7200) and
# per-ARM wall 25: 1062, 50: 2124 (cap 1920 = 80% of the 2400 s segment ceiling). The wall clause alone would allow 50;
# the SEGMENT clause binds and selects 25. BETA 58 (random baseline 7.28515625 charge per TRAIN episode).
# Oracles on 16 random genomes + P_SPENDER + P_LAST: Cypher == numpy (charge and unaffordable counts), world 0,
# free_unaffordable 49/49 eligible (112 envs merely had an unaffordable send), brain 0, skip_last 9/9, charge 0, ok.
GENS = 25
RUNS = [(f, rs) for f in FAMILIES for rs in range(RUNS_PER_FAMILY)]
ARM_INDEX = {"cell": 0, "control": 1}
TRUTH = np.arange(NR) >> SH

TICK_Q = """MATCH (v:Env)
WITH v, $R[v.e] AS r
WITH v, r, $act[v.g][r] AS a_on, $act0[v.g] AS a_off, $sym[v.g][r] AS sym
WITH v, r, a_on, a_off, (CASE WHEN sym <> 0 THEN $k ELSE 0 END) AS bits, v.ch + v.cr AS c
WITH v, r, a_on, a_off, bits, c, $alpha * bits AS cost
WITH v, r, a_on, a_off, bits, c, cost, (bits > 0 AND c >= cost) AS afford
WITH v, r, a_on, a_off, bits, c, cost, afford, ({deliver}) AS ok
WITH v, r, c - (CASE WHEN afford THEN cost ELSE 0 END) AS nch,
     (CASE WHEN ok THEN a_on ELSE a_off END) AS act, (CASE WHEN bits > 0 AND NOT afford THEN 1 ELSE 0 END) AS un
SET v.ch = nch, v.cr = (CASE WHEN act = r / 32 THEN $y ELSE 0 END), v.un = v.un + un"""


# ------------------------------------------------------------------ genome -> action table (numpy reference)

def _rotl(b, j):
    return ((b << j) | (b >> (8 - j))) & 255 if j else b


def tables(B, skip_last=False):
    """B uint8 [P, GLEN] -> (sym [P, 256], act_on [P, 256], act_silent [P]) by the program + codebook."""
    B = np.asarray(B, np.uint8)
    P = len(B)
    prog = B[:, :PROG_B].astype(np.int64).reshape(P, N_INSTR, 2)
    cb = B[:, PROG_B:PROG_B + CB_B].astype(np.int64)
    b = np.tile(np.arange(NR, dtype=np.int64), (P, 1))
    n = N_INSTR - 1 if skip_last else N_INSTR
    idx = np.arange(8)
    for i in range(n):
        op, arg = prog[:, i, 0] % 8, prog[:, i, 1]
        j, v = (arg & 7), (arg >> 6)
        for p in range(P):
            o, jj, vv = int(op[p]), int(j[p]), int(v[p])
            x = b[p]
            if o == 0:
                continue
            if o == 1:
                b[p] = x | (1 << jj)
            elif o == 2:
                b[p] = x ^ (1 << jj)
            elif o == 3:
                m = sum(1 << ((jj + d) % 8) for d in range(4))
                b[p] = x | m
            elif o == 4:
                m = sum(1 << ((jj + d) % 8) for d in range(4))
                b[p] = x & (255 ^ m)
            elif o == 5:
                b[p] = ((x << jj) | (x >> (8 - jj))) & 255 if jj else x
            elif o == 6:
                r = ((x << jj) | (x >> (8 - jj))) & 255 if jj else x
                b[p] = x ^ r
            else:
                m = sum(1 << i2 for i2 in idx if (i2 - jj) % (vv + 2) == 0)
                b[p] = x ^ m
    sym = b & 7
    act_on = np.take_along_axis(cb, sym, 1) % 8
    act_silent = cb[:, 0] % 8
    return sym, act_on, act_silent


def ref_tables_scalar(g, skip_last=False):
    """Scalar plain-int reference of the decode for ONE genome -> (sym [256], act [256], act_silent)."""
    prog = [(int(g[2 * i]) % 8, int(g[2 * i + 1])) for i in range(N_INSTR)]
    cb = [int(x) for x in g[PROG_B:PROG_B + CB_B]]
    n = N_INSTR - 1 if skip_last else N_INSTR
    sym, act = [0] * NR, [0] * NR
    for r in range(NR):
        b = r
        for i in range(n):
            o, arg = prog[i]
            j, v = arg & 7, arg >> 6
            if o == 0:
                continue
            if o == 1:
                b |= 1 << j
            elif o == 2:
                b ^= 1 << j
            elif o == 3:
                for d in range(4):
                    b |= 1 << ((j + d) % 8)
            elif o == 4:
                for d in range(4):
                    b &= 255 ^ (1 << ((j + d) % 8))
            elif o == 5:
                b = (((b << j) | (b >> (8 - j))) & 255) if j else b
            elif o == 6:
                rr = (((b << j) | (b >> (8 - j))) & 255) if j else b
                b ^= rr
            else:
                for i2 in range(8):
                    if (i2 - j) % (v + 2) == 0:
                        b ^= 1 << i2
        s = b & 7
        sym[r], act[r] = s, cb[s] % 8
    return sym, act, cb[0] % 8


def nonnop(B):
    prog = np.asarray(B, np.uint8)[:, :PROG_B].astype(np.int64).reshape(len(B), N_INSTR, 2)
    return (prog[:, :, 0] % 8 != 0).sum(1)


def functional_bytes(B):
    return 2 * nonnop(B) + CB_B


def init(rng, P):
    return rng.integers(0, 256, (P, GLEN), dtype=np.uint8)


def mutate(rng, B):
    B = B.copy()
    P = len(B)
    mp = rng.random((P, PROG_B)) < 1.0 / PROG_B
    B[:, :PROG_B] = np.where(mp, rng.integers(0, 256, (P, PROG_B), dtype=np.uint8), B[:, :PROG_B])
    mc = rng.random((P, CB_B)) < 1.0 / CB_B
    B[:, PROG_B:] = np.where(mc, rng.integers(0, 256, (P, CB_B), dtype=np.uint8), B[:, PROG_B:])
    return B


# ------------------------------------------------------------------ numpy reference settlement

def ref_charge(B, seeds, cheat_free=False):
    """numpy NpChannel-order settlement -> (final charge [P, E], unaffordable sends [P, E])."""
    sym, act_on, act_off = tables(B)
    R = S.r_stream(np.asarray(seeds), T)
    P, E = len(B), len(seeds)
    charge = np.full((P, E), START, np.int64)
    credit = np.zeros((P, E), np.int64)
    unaff = np.zeros((P, E), np.int64)
    for t in range(T):
        r = R[t]
        s = sym[:, r]
        bits = KBITS * (s != 0)
        c = charge + credit
        cost = ALPHA_INT * bits
        afford = (bits > 0) & (c >= cost)
        unaff += (bits > 0) & ~afford
        charge = c - np.where(afford, cost, 0)
        deliver = (bits > 0) if cheat_free else afford
        a = np.where(deliver, act_on[:, r], act_off[:, None])
        credit = Y_INT * (a == TRUTH[r][None, :])
    return charge + credit, unaff


# ------------------------------------------------------------------ Cypher settlement (lockstep over runs)

class Cypher:
    def __init__(self, port=PORT, graph=GRAPH):
        from falkordb import FalkorDB
        self.db = FalkorDB(host="127.0.0.1", port=port, socket_timeout=600)
        self.name = graph
        self.g = None

    def reset(self, n_env, g_of, e_of):
        try:
            self.db.select_graph(self.name).delete()
        except Exception:
            pass
        self.g = self.db.select_graph(self.name)
        rows = [[i, int(g_of[i]), int(e_of[i]), START, 0, 0] for i in range(n_env)]
        for c in range(0, n_env, 8192):
            self.g.query("UNWIND $rows AS row CREATE (:Env {i: row[0], g: row[1], e: row[2], ch: row[3], "
                         "cr: row[4], un: row[5]})", {"rows": rows[c:c + 8192]})

    def run(self, B, seeds, cheat_free=False):
        """B [P, GLEN] over `seeds`; env i = genome i // E, episode i % E. -> (charge [P, E], unaff [P, E])."""
        sym, act_on, act_off = tables(B)
        P, E = len(B), len(seeds)
        n = P * E
        self.reset(n, np.repeat(np.arange(P), E), np.tile(np.arange(E), P))
        R = S.r_stream(np.asarray(seeds), T)
        q = TICK_Q.format(deliver="bits > 0" if cheat_free else "afford")
        params = {"sym": sym.tolist(), "act": act_on.tolist(), "act0": act_off.tolist(),
                  "k": KBITS, "alpha": ALPHA_INT, "y": Y_INT}
        for t in range(T):
            self.g.query(q, dict(params, R=R[t].tolist()))
        res = self.g.query("MATCH (v:Env) RETURN v.i AS i, v.ch + v.cr AS f, v.un AS u ORDER BY i").result_set
        charge = np.zeros(n, np.int64)
        unaff = np.zeros(n, np.int64)
        for i, f, u in res:
            charge[int(i)], unaff[int(i)] = int(f), int(u)
        return charge.reshape(P, E), unaff.reshape(P, E)


# ------------------------------------------------------------------ planted genomes (structural oracle eligibility)

def planted():
    """P_SPENDER: sends on every R and never earns (guaranteed unaffordable sends).
    P_LAST: the 8th instruction changes the table (guaranteed skip_last eligibility)."""
    sp = np.zeros(GLEN, np.uint8)
    sp[0], sp[1] = 3, 0                      # set bits 0..3 -> sym != 0 for every R
    sp[PROG_B:] = 7                          # every codebook entry acts 7 (never right for bucket 0..6 mostly)
    la = np.zeros(GLEN, np.uint8)
    la[14], la[15] = 2, 1                    # last instruction: flip bit 1 -> changes sym for every R
    la[PROG_B:] = np.arange(CB_B, dtype=np.uint8)
    return np.stack([sp, la])


def descriptor(B):
    sym, act_on, act_off = tables(B)
    s = np.array([len(np.unique(x)) for x in sym])
    a = np.array([len(np.unique(x)) for x in act_on])
    return ((s - 1) * 8 + (a - 1)).astype(np.uint32)


def random_mean(cy) -> float:
    rng = np.random.Generator(np.random.PCG64(5))
    B = init(rng, 256)
    ch, _ = ref_charge(B, TRAIN)
    return float(ch.mean())


def beta_of(mean_charge) -> int:
    """AP-02's 1% of the world's own random baseline per functional byte, scaled x SCALE to stay in integers."""
    return int(round(0.01 * (mean_charge * len(TRAIN)) * SCALE))


def selection_fit(charge, B, arm, beta):
    s = SCALE * charge.sum(1)
    return s - beta * functional_bytes(B) if arm == "cell" else s


# ------------------------------------------------------------------ oracles

def oracles(cy, top, arm, beta) -> dict:
    G = np.concatenate([top, planted()])
    ch_c, un_c = cy.run(G, TRAIN)
    ch_n, un_n = ref_charge(G, TRAIN)
    world_bad = int((ch_c != ch_n).sum()) + int((un_c != un_n).sum())
    ch_f, _ = cy.run(G, TRAIN, cheat_free=True)
    ch_free_ref, _ = ref_charge(G, TRAIN, cheat_free=True)
    el = ch_free_ref != ch_n                      # the mechanism changes the outcome in the REFERENCE
    free = {"eligible": int(el.sum()), "caught": int(((ch_f != ch_n) & el).sum()),
            "envs_with_unaffordable_send": int((un_n > 0).sum())}
    free["share"] = round(free["caught"] / free["eligible"], 4) if free["eligible"] else 0.0
    sym, act_on, act_off = tables(G)
    sym_s, act_s, brain_bad = None, None, 0
    for p in range(len(G)):
        s_ref, a_ref, a0 = ref_tables_scalar(G[p])
        brain_bad += int(not (np.array_equal(np.array(s_ref), sym[p]) and np.array_equal(np.array(a_ref), act_on[p])
                              and a0 == int(act_off[p])))
    _, act_skip, _ = tables(G, skip_last=True)
    elig = caught = 0
    for p in range(len(G)):
        _, a_ref_skip, _ = ref_tables_scalar(G[p], skip_last=True)
        if not np.array_equal(np.array(a_ref_skip), act_on[p]):
            elig += 1
            caught += int(not np.array_equal(act_skip[p], act_on[p]))
    fb = functional_bytes(top)
    charge_bad = int((fb != 2 * nonnop(top) + CB_B).sum())
    sel = selection_fit(ch_c[:len(top)], top, arm, beta)
    sel_ref = SCALE * ch_n[:len(top)].sum(1) - (beta * fb if arm == "cell" else 0)
    charge_bad += int((sel != sel_ref).sum())
    o = {"arm": arm, "envs": int(ch_c.size), "world_mismatched": world_bad,
         "free_unaffordable": free, "brain_mismatched": brain_bad,
         "skip_last_eligible": elig, "skip_last_share": round(caught / elig, 4) if elig else 0.0,
         "charge_mismatched": charge_bad}
    o["ok"] = bool(world_bad == 0 and free["eligible"] > 0 and free["share"] >= 0.9 and brain_bad == 0
                   and elig > 0 and caught / max(elig, 1) >= 0.9 and charge_bad == 0)
    return o


# ------------------------------------------------------------------ one arm, all runs in lockstep

def run_arm(r, cy, arm, gens, beta, ctx=None, st=None):
    """All 32 runs of `arm` advance together; each keeps its own archive, GA stream and sampler stream."""
    from primordial.qd.archive import LuaArchive
    ai = ARM_INDEX[arm]
    rngs = [np.random.Generator(np.random.PCG64([f, rs, ai, STREAM_TAG])) for f, rs in RUNS]
    arch = [LuaArchive(r, f"c-r7-ap03-{f}-{rs}-{ai}", GLEN, sampler_seed=[f + 1, rs, ai, STREAM_TAG])
            for f, rs in RUNS]
    for a in arch:
        a.clear()
    audited = {"offers": 0, "mismatched": 0}
    for gen in range(gens):
        B = []
        for i, a in enumerate(arch):
            par = a.sample(BATCH)
            B.append(init(rngs[i], BATCH) if len(par) == 0 else mutate(rngs[i], np.asarray(par, np.uint8)))
        Ball = np.concatenate(B)
        charge, _ = cy.run(Ball, TRAIN)
        ref = ref_charge(Ball[:BATCH], TRAIN)[0]                     # the (4200, 0) slice, every generation
        audited["offers"] += int(ref.size)
        audited["mismatched"] += int((charge[:BATCH] != ref).sum())
        cells = descriptor(Ball)
        for i, a in enumerate(arch):
            sl = slice(i * BATCH, (i + 1) * BATCH)
            a.insert(cells[sl], selection_fit(charge[sl], Ball[sl], arm, beta).astype(np.int32), Ball[sl],
                     np.zeros((BATCH, 2), np.uint32))
        if ctx is not None:
            ctx.progress(gen + 1, gens - gen - 1)
    out = []
    for i, (f, rs) in enumerate(RUNS):
        el = arch[i].dump()
        arch[i].clear()
        order = sorted(el.values(), key=lambda v: (-v[0], v[1]))
        top = np.frombuffer(b"".join(v[1] for v in order[:TOP]), np.uint8).reshape(-1, GLEN)
        rec = selection_fit(ref_charge(top, TRAIN)[0], top, arm, beta)
        recount_bad = int(sum(int(x) != int(v[0]) for x, v in zip(rec, order[:TOP])))
        held, unaff = ref_charge(top[:1], HELD)
        out.append({"family": f, "run_seed": rs, "archive_cells": len(el), "train_fit_top1": int(order[0][0]),
                    "held_charge_per_episode": float(held.mean()),
                    "held_unaffordable_per_episode": float(unaff.mean()),
                    "top1_nonnop": int(nonnop(top[:1])[0]), "top1_functional_bytes": int(functional_bytes(top[:1])[0]),
                    "top1_sha256": hashlib.sha256(top[0].tobytes()).hexdigest(),
                    "recount_mismatched_top16": recount_bad,
                    "top16": top})
    return out, audited


def score(held, control) -> dict:
    q = np.percentile(held, [25, 50, 75])
    qc = np.percentile(control, [25, 50, 75])
    bar = float(qc[1] - 0.5 * (qc[2] - qc[0]))
    return {"held_median_cell": float(q[1]), "iqr_cell": float(q[2] - q[0]), "held_median_control": float(qc[1]),
            "iqr_control": float(qc[2] - qc[0]), "bar": bar, "parity": bool(q[1] >= bar)}


def job(ctx, gens: int = GENS, port: int = PORT, exp_id: str = EXP):
    import redis
    r = redis.Redis(host="127.0.0.1", port=port)
    cy = Cypher(port=port)
    st = ctx.load_checkpoint() or {"arms_done": [], "held": {"cell": [], "control": []}, "clean": True, "ref": False,
                                   "beta": None, "random_mean": None}
    if not st["ref"]:
        st["random_mean"] = random_mean(cy)
        st["beta"] = beta_of(st["random_mean"])
        ctx.emit({"kind": "reference", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "gens": gens, "batch": BATCH,
                  "genome_bytes": GLEN, "alpha_int": ALPHA_INT, "y_int": Y_INT, "start": START, "kbits": KBITS,
                  "beta": st["beta"], "random_mean_charge_per_train_episode": st["random_mean"],
                  "lockstep_envs_per_tick": N_RUNS * BATCH * len(TRAIN), "status": "control",
                  "ts": round(time.time(), 3)})
        st["ref"] = True
    for arm in ("control", "cell"):
        if arm in st["arms_done"]:
            continue
        if ctx.should_pause():
            ctx.pause(st, completed_units=len(st["arms_done"]), remaining_units=2 - len(st["arms_done"]))
        t0, c0 = time.perf_counter(), time.process_time()
        res, audited = run_arm(r, cy, arm, gens, st["beta"], ctx=ctx)
        o = oracles(cy, res[0]["top16"], arm, st["beta"])
        o["offers_audited"] = audited["offers"]
        o["offers_mismatched"] = audited["mismatched"]
        o["ok"] = bool(o["ok"] and audited["mismatched"] == 0)
        wall, cpu = time.perf_counter() - t0, time.process_time() - c0
        cell = CELL if arm == "cell" else CELL_CTRL
        for i, row in enumerate(res):
            rec = {k: v for k, v in row.items() if k != "top16"}
            st["clean"] = bool(st["clean"] and rec["recount_mismatched_top16"] == 0)
            ctx.emit({"kind": "run", "arm": arm, "cell": cell, "gens": gens, "genome_bytes": GLEN,
                      "reader": "top1_train", "beta": st["beta"] if arm == "cell" else 0, **rec,
                      "held_minus_random": rec["held_charge_per_episode"] - st["random_mean"],
                      "oracles": o if i == 0 else None,
                      "status": "record" if arm == "cell" else "control", "ts": round(time.time(), 3)})
            st["held"][arm].append(rec["held_charge_per_episode"])
        st["clean"] = bool(st["clean"] and o["ok"])
        ctx.emit({"kind": "arm_end", "exp_id": exp_id, "arm": arm, "wall_s": round(wall, 3), "cpu_s": round(cpu, 3),
                  "oracles": o, "status": "control", "ts": round(time.time(), 3)})
        st["arms_done"].append(arm)
    sc = score(st["held"]["cell"], st["held"]["control"])
    n = {a: len(st["held"][a]) for a in st["held"]}
    full = all(v == N_RUNS for v in n.values())
    primary = "INDETERMINATE" if not (st["clean"] and full) else ("PASS" if sc["parity"] else "FAIL")
    ctx.emit({"kind": "summary", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "cell": CELL, "runs_total": n["cell"],
              "rng_family_count": len(FAMILIES), "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
              "n_per_family": {str(f): RUNS_PER_FAMILY for f in FAMILIES}, "gens": gens, "beta": st["beta"],
              "random_mean": st["random_mean"],
              **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in sc.items()},
              "oracle_clean": st["clean"], "primary": primary,
              "clause_a": "none: signal_world_d1 has no floor suite", "status": "record" if st["clean"] else "cheat",
              "ts": round(time.time(), 3)})


# ------------------------------------------------------------------ dev (no rows)

def dev(gens: int = 2) -> None:
    """No rows: Cypher == numpy, structural oracle eligibility, lockstep wall per generation, GENS by the rule."""
    import redis
    r = redis.Redis(host="127.0.0.1", port=PORT)
    cy = Cypher(port=PORT, graph=GRAPH + "_dev")
    rng = np.random.Generator(np.random.PCG64(77))
    G = np.concatenate([init(rng, TOP), planted()])
    rm = random_mean(cy)
    beta = beta_of(rm)
    out = {"random_mean_charge_per_train_episode": rm, "beta": beta, "genome_bytes": GLEN}
    ch_c, un_c = cy.run(G, TRAIN)
    ch_n, un_n = ref_charge(G, TRAIN)
    out["cypher_eq_numpy"] = bool(np.array_equal(ch_c, ch_n) and np.array_equal(un_c, un_n))
    out["oracles_cell"] = oracles(cy, init(rng, TOP), "cell", beta)
    B = init(rng, N_RUNS * BATCH)
    t = time.perf_counter()
    for _ in range(gens):
        cy.run(B, TRAIN)
        B = mutate(rng, B)
    per_gen = (time.perf_counter() - t) / gens
    out["lockstep_wall_s_per_gen_one_arm"] = round(per_gen, 3)
    proj = {str(Gn): round(2 * Gn * per_gen * 1.1, 1) for Gn in GENS_CHOICES}
    fits = [Gn for Gn in GENS_CHOICES if 2 * Gn * per_gen * 1.1 <= WALL_CAP]
    out["projected_job_wall_s"] = proj
    out["gens_by_rule"] = max(fits) if fits else "INFEASIBLE"
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dev(int(sys.argv[2]) if len(sys.argv) > 2 else 2) if sys.argv[1] == "dev" else None
