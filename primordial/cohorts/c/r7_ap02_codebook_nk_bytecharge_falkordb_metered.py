"""C-R7-AP-02 (ANTI_PRIOR, cell assigned by code): codebook / nk_stub / byte_charge / falkordb_cypher / metered_stream
(anti_prior.assign exp_id C-R7-AP-02, round 7).

The experimenter received only the cell; the prior and the arm are unread. nk_stub is not a screened graphworld world:
landscape rows only, no clause A claim. The definitions below are fixed before any run.

  world     lane E's NK stub (N=64, K=4). A seed is a LANDSCAPE (C-R2-09 / C-R6-AP-01): selection on TRAIN = 8 train
            landscapes (9100..9107); score on HELD = 64 held-out landscapes (30000..30063), NK fitness per landscape.
  brain     codebook. Genome 6 meaningful bytes [d, m, cb0, cb1, cb2, cb3], STORED in 8 bytes (two zero pad bytes):
              d  = byte0 % 5          hex digits read per table entry, most significant first (entry q = v >> (16 - 4d))
              Ls = 1 + byte1 % 32     code length
              cb = uint32 little-endian from bytes 2..5
            For locus j of a landscape the brain sees that locus's 32-entry contribution row (if delivered):
              sym = argmax_i q_i (ties: lowest i; silence or d = 0: sym 0);  bit_j = (cb >> (sym % Ls)) & 1
            Target-blind (the brain reads only the landscape's own table). Functional bytes = 2 + ceil(Ls / 8) (the
            codebook bytes the code can address; the pad bytes are never charged). Init: the 6 meaningful bytes uniform,
            pad zero. Mutation: d +-1 mod 5 with p 0.2; byte1 +-1 mod 32 with p 0.2; each codebook bit flipped with
            p 1/32; the pad stays zero.
            AMENDMENT (job ec5a36e1c102 aborted after its reference row, before any run row): the stored length was 6.
            LuaArchive's INSERT_LUA tie-break gless() reads the genome in 4-byte words (for p = 1, glen, 4), so an equal
            -fitness tie on a 6-byte genome raises "data string too short" in Redis. The stored length is now 8 with two
            zero pad bytes; nothing else changes -- byte_charge has always counted FUNCTIONAL bytes, not stored length,
            and the decode reads bytes 0..5 as before.
  channel   metered_stream (C-R6-01's half-observation rule applied to this reader): per landscape the loci are read in
            order j = 0..63; before locus j ledger += CREDIT; cost = ALPHA * 32 * d; if ledger >= cost the row is
            delivered and ledger -= cost, else silence. ALPHA = 2; CREDIT = ALPHA * 32 * 2 = 128 (half of the 4-digit
            row), START = CREDIT. Disclosed before the run: the meter binds only for d >= 3; an elite may choose d <= 2
            and never be silenced (C-R7-AP-01's failure mode), so the meter oracle's eligibility is STRUCTURAL (planted
            genomes), never conditional on what evolution picks.
  pressure  byte_charge (cell arm): selection fitness = sum over TRAIN of NK - BETA * functional bytes, BETA = floor(0.01 *
            RANDOM_MEAN) * 8, RANDOM_MEAN = mean NK per TRAIN landscape of 256 uniform bit strings (PCG64(5)). The 1% rate
            is a stated choice, not a derivation (no byte_charge definition exists in the repo). control arm: no charge.
  substrate falkordb_cypher: every NK fitness used by selection is ONE FalkorDB GRAPH.QUERY per generation on lane C's
            Redis 8 + FalkorDB :6392 (bits and tables as parameters; neighbourhood index by integer arithmetic; table
            lookup by list index; sum per (genome, landscape)). numpy computes the codebook decode and the meter (disclosed,
            as C-R6-AP-01's numpy Tucker contraction). Archive: E's LuaArchive (seeded sampler) on the same :6392.
            Descriptor: popcount halves of the bits on train landscape 0 (33 x 33).
  arms      cell (byte_charge) vs control (no charge), same GA and sampler streams, same channel, same GENS, batch 128.
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 7201]); sampler [family + 1, run_seed, arm, 7201]. Each
            (family, run_seed) runs control first, then cell.
  GENS      rule fixed before the no-rows timing check: the largest of {25, 50, 100, 200} whose projected job WALL
            (64 runs x wall per generation measured on the Cypher path x 1.1) <= 5400 s; if 25 does not fit, INFEASIBLE
            (aborted row + PRODUCTION_CANDIDATE with the measured cost). Outcome recorded at GENS below.
  reader    top1_train: the archive elite with the highest selection fitness of its arm (ties: lexicographically smaller
            genome bytes); held = its mean NK per HELD landscape (numpy NKWorld reference, metered decode).
  primary   median over the 32 runs of held (cell) >= median (control) - 0.5 * IQR (control). PASS / FAIL only with 32
            runs per arm and oracles clean, else INDETERMINATE.
  oracles   family 4200 run seed 0 of each arm; genomes = top-16 elites + planted P_ONES (d 4, Ls 32, cb all ones) +
            planted P_METER (d 4, Ls 32, cb 0xA5A5A5A5); rows = genome x TRAIN landscape:
            world    Cypher fitness == numpy NKWorld.evaluate on every offer of the run (exact); EVERY run: the top-16
                     archive fitness == numpy recount from the STORED genome bytes (decode, NK, charge) (exact)
            k3       the Cypher query with a K=3 window mismatches >= 90% of ELIGIBLE rows (bits not all zero), >= 1
                     eligible (P_ONES makes it structural)
            brain    scalar plain-int reference decode (ledger, quantize, argmax, code) == numpy bits on every row: 0
                     mismatched
            meter    cheat free_stream (every row delivered) changes the bits on >= 90% of ELIGIBLE rows (rows where the
                     scalar reference with free delivery differs), >= 1 eligible (P_METER makes it structural; verified in
                     the dev check before any run)
            charge   functional bytes == 2 + ceil(Ls / 8) and the cell selection fitness == NK sum - BETA * bytes on the
                     top-16 (exact)
  report    (not judged) random-bits mean; digits read, code length and bytes of the top1; delivered share; train fitness.
  not claimed  clause A; any mechanism; the prior ledger was not read.

  worker:  job = primordial.cohorts.c.r7_ap02_codebook_nk_bytecharge_falkordb_metered:job
  dev:     python -m primordial.cohorts.c.r7_ap02_codebook_nk_bytecharge_falkordb_metered dev   (no rows)
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time

import numpy as np

from primordial.qd.stubworld import GRID, K, N_BITS, NKWorld

EXP = "C-R7-AP-02-codebook-nk-bytecharge-falkordb-metered"
PREDICATE_ID = "C-R7-AP-02"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
CELL = {"representation": "codebook", "world": "nk_stub", "pressure": "byte_charge", "substrate": "falkordb_cypher",
        "channel": "metered_stream"}
CELL_CTRL = dict(CELL, pressure="byte_charge_off_control")
GLEN, NG, BATCH, TOP, E = 8, 6, 128, 16, 32       # GLEN must be a multiple of 4 (INSERT_LUA gless); NG = meaningful bytes
ALPHA = 2
CREDIT = ALPHA * 32 * 2
START = CREDIT
TRAIN_SEEDS = np.arange(9100, 9108)
HELD_SEEDS = np.arange(30000, 30064)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
PORT = 6392
GRAPH = "c_r7_ap02"
STREAM_TAG = 7201
GENS_CHOICES = (25, 50, 100, 200)
WALL_CAP = 5400.0
# No-rows dev check (3 gens after warm-up, cell path incl. one Cypher query per generation): 1.2806 wall-s / gen, 0.0469
# client CPU-s / gen -> projected job wall 25: 2253.8, 50: 4507.6, 100: 9015.3, 200: 18030.6 (cap 5400) -> GENS 50.
# BETA 169144 (random NK mean per train landscape 2114314.67). Oracles on 16 random genomes + P_ONES + P_METER, both
# arms: world 0/144 mismatched, k3 1.0 of 144 / 128 eligible, brain 0, free_stream 1.0 of 72 / 64 eligible, charge 0.
GENS = 50
P_ONES = np.array([4, 31, 255, 255, 255, 255, 0, 0], np.uint8)
P_METER = np.array([4, 31, 0xA5, 0xA5, 0xA5, 0xA5, 0, 0], np.uint8)

Q_FIT = """UNWIND range(0, size($bits) - 1) AS p
UNWIND range(0, $L - 1) AS l
WITH p, l, $bits[p][l] AS b
UNWIND range(0, 63) AS j
WITH p, l, j, b[j] + 2 * b[(j + 1) % 64] + 4 * b[(j + 2) % 64] + 8 * b[(j + 3) % 64]{k4} AS idx
RETURN p, l, sum($tbl[l][j][idx]) AS f ORDER BY p, l"""


class Landscapes:
    def __init__(self, seeds):
        self.worlds = [NKWorld(int(s)) for s in seeds]
        self.tables = np.stack([w.table for w in self.worlds])                     # int64 [L, 64, 32]
        self.tables_list = self.tables.tolist()


# ------------------------------------------------------------------ genome

def decode(B):
    B = np.asarray(B, np.uint8)
    d = B[:, 0].astype(np.int64) % 5
    Ls = 1 + B[:, 1].astype(np.int64) % 32
    cb = (B[:, 2].astype(np.int64) | (B[:, 3].astype(np.int64) << 8) | (B[:, 4].astype(np.int64) << 16)
          | (B[:, 5].astype(np.int64) << 24))
    return d, Ls, cb


def functional_bytes(B):
    _, Ls, _ = decode(B)
    return 2 + (Ls + 7) // 8


def init(rng, P):
    B = np.zeros((P, GLEN), np.uint8)
    B[:, :NG] = rng.integers(0, 256, (P, NG), dtype=np.uint8)
    return B


def mutate(rng, B):
    B = B.copy()
    P = len(B)
    d, _, cb = decode(B)
    m = rng.random((P, 2)) < 0.2
    pm = rng.choice(np.array([-1, 1]), (P, 2))
    B[:, 0] = np.where(m[:, 0], (d + pm[:, 0]) % 5, d).astype(np.uint8)
    B[:, 1] = np.where(m[:, 1], (B[:, 1].astype(np.int64) % 32 + pm[:, 1]) % 32, B[:, 1].astype(np.int64) % 32) \
        .astype(np.uint8)
    flips = (rng.random((P, 32)) < 1.0 / 32).astype(np.int64)
    cb = cb ^ (flips << np.arange(32)[None, :]).sum(1)
    for i in range(4):
        B[:, 2 + i] = ((cb >> (8 * i)) & 255).astype(np.uint8)
    B[:, NG:] = 0
    return B


# ------------------------------------------------------------------ decode + meter (numpy)

def brain_bits(B, land, meter="metered"):
    """-> bits int64 [P, L, 64], delivered bool [P, L, 64]."""
    d, Ls, cb = decode(B)
    P, L = len(B), len(land.worlds)
    cost = (ALPHA * 32 * d)[:, None]
    shift = (16 - 4 * d)[:, None, None]
    led = np.full((P, L), START, np.int64)
    bits = np.zeros((P, L, N_BITS), np.int64)
    dl = np.zeros((P, L, N_BITS), bool)
    for j in range(N_BITS):
        if meter == "metered":
            led = led + CREDIT
            dj = led >= cost
            led = led - np.where(dj, cost, 0)
        else:
            dj = np.ones((P, L), bool)
        q = land.tables[None, :, j, :] >> shift                                   # [P, L, 32]
        sym = np.where(dj, np.argmax(q, axis=2), 0)
        bits[:, :, j] = (cb[:, None] >> (sym % Ls[:, None])) & 1
        dl[:, :, j] = dj
    return bits, dl


def ref_bits(g, table, meter="metered"):
    """Scalar plain-int reference for one genome on one landscape table (list [64][32]) -> (bits [64], delivered [64])."""
    d, Ls = int(g[0]) % 5, 1 + int(g[1]) % 32
    cb = int(g[2]) | (int(g[3]) << 8) | (int(g[4]) << 16) | (int(g[5]) << 24)
    cost, led = ALPHA * 32 * d, START
    bits, dl = [0] * N_BITS, [False] * N_BITS
    for j in range(N_BITS):
        if meter == "metered":
            led += CREDIT
            ok = led >= cost
            if ok:
                led -= cost
        else:
            ok = True
        sym = 0
        if ok:
            best = -1
            for i in range(E):
                q = int(table[j][i]) >> (16 - 4 * d)
                if q > best:
                    best, sym = q, i
        bits[j], dl[j] = (cb >> (sym % Ls)) & 1, ok
    return bits, dl


# ------------------------------------------------------------------ world (Cypher) + reference

def cypher_fit(graph, bits, land, k3=False):
    q = Q_FIT.format(k4="" if k3 else " + 16 * b[(j + 4) % 64]")
    res = graph.query(q, {"bits": bits.tolist(), "L": len(land.worlds), "tbl": land.tables_list}).result_set
    out = np.zeros(bits.shape[:2], np.int64)
    for p, l, f in res:
        out[int(p), int(l)] = int(f)
    return out


def ref_fit(bits, land):
    P, L = bits.shape[:2]
    out = np.empty((P, L), np.int64)
    for l in range(L):
        out[:, l] = land.worlds[l].evaluate(np.packbits(bits[:, l].astype(np.uint8), axis=1))[0]
    return out


def random_mean(land) -> float:
    rr = np.random.Generator(np.random.PCG64(5))
    rbits = rr.integers(0, 2, (256, 1, N_BITS)).astype(np.int64).repeat(len(land.worlds), 1)
    return float(ref_fit(rbits, land).mean())


def beta_of(train) -> int:
    return int(np.floor(0.01 * random_mean(train))) * len(train.worlds)


def selection_fit(nk, B, arm, beta):
    s = nk.sum(1)
    return s - beta * functional_bytes(B) if arm == "cell" else s


def cells_of(bits):
    b0 = bits[:, 0, :]
    return (b0[:, :32].sum(1) * GRID + b0[:, 32:].sum(1)).astype(np.uint32)


# ------------------------------------------------------------------ oracles

def oracles(graph, top, train, arm, beta) -> dict:
    G = np.concatenate([top, P_ONES[None], P_METER[None]])
    bits, dl = brain_bits(G, train)
    nk = cypher_fit(graph, bits, train)
    ref = ref_fit(bits, train)
    world_bad = int((nk != ref).sum())
    k3 = cypher_fit(graph, bits, train, k3=True)
    el = bits.any(axis=2)
    k3_share = float((k3 != ref)[el].mean()) if el.any() else 0.0
    bad = elig = caught = 0
    freeb, _ = brain_bits(G, train, "free")
    for p in range(len(G)):
        for l in range(len(train.worlds)):
            rb, rd = ref_bits(G[p], train.tables_list[l])
            fb, _ = ref_bits(G[p], train.tables_list[l], "free")
            bad += int(rb != bits[p, l].tolist() or rd != dl[p, l].tolist())
            if fb != rb:
                elig += 1
                caught += int(freeb[p, l].tolist() != rb)
    fbytes = functional_bytes(top)
    _, Ls, _ = decode(top)
    charge_bad = int((fbytes != 2 + (Ls + 7) // 8).sum())
    sel = selection_fit(nk[:len(top)], top, arm, beta)
    sel_ref = ref[:len(top)].sum(1) - (beta * fbytes if arm == "cell" else 0)
    charge_bad += int((sel != sel_ref).sum())
    o = {"arm": arm, "rows": int(bits.shape[0] * bits.shape[1]), "world_mismatched_rows": world_bad,
         "k3_eligible_rows": int(el.sum()), "k3_share": round(k3_share, 4), "brain_mismatched_rows": bad,
         "free_stream_eligible_rows": elig, "free_stream_share": round(caught / elig, 4) if elig else 0.0,
         "charge_mismatched": charge_bad}
    o["ok"] = bool(world_bad == 0 and el.sum() > 0 and k3_share >= 0.9 and bad == 0 and elig > 0
                   and caught / max(elig, 1) >= 0.9 and charge_bad == 0)
    return o


# ------------------------------------------------------------------ one run

def run(r, graph, family, rs, arm_i, arm, gens, train, held, beta, track=False):
    from primordial.qd.archive import LuaArchive
    rng = np.random.Generator(np.random.PCG64([family, rs, arm_i, STREAM_TAG]))
    arch = LuaArchive(r, f"c-r7-ap02-{family}-{rs}-{arm_i}", GLEN, sampler_seed=[family + 1, rs, arm_i, STREAM_TAG])
    arch.clear()
    c0, t0 = time.process_time(), time.perf_counter()
    offers = offer_bad = 0
    for _ in range(gens):
        par = arch.sample(BATCH)
        B = init(rng, BATCH) if len(par) == 0 else mutate(rng, np.asarray(par, np.uint8))
        bits, _ = brain_bits(B, train)
        nk = cypher_fit(graph, bits, train)
        if track:
            offers += nk.size
            offer_bad += int((ref_fit(bits, train) != nk).sum())
        arch.insert(cells_of(bits), selection_fit(nk, B, arm, beta).astype(np.int32), B,
                    np.zeros((BATCH, 2), np.uint32))
    loop_cpu, loop_wall = time.process_time() - c0, time.perf_counter() - t0
    el = arch.dump()
    arch.clear()
    order = sorted(el.values(), key=lambda v: (-v[0], v[1]))
    top = np.frombuffer(b"".join(v[1] for v in order[:TOP]), np.uint8).reshape(-1, GLEN)
    tb, _ = brain_bits(top, train)
    rec = selection_fit(ref_fit(tb, train), top, arm, beta)
    recount_bad = int(sum(int(x) != int(v[0]) for x, v in zip(rec, order[:TOP])))
    hb, hd = brain_bits(top[:1], held)
    d, Ls, cb = decode(top[:1])
    info = {"gens_done": gens, "genomes_evaluated": gens * BATCH, "loop_cpu_s": round(loop_cpu, 4),
            "loop_wall_s": round(loop_wall, 3), "archive_cells": len(el), "train_fit_top1": int(order[0][0]),
            "train_nk_per_landscape_top1": float(ref_fit(tb[:1], train).mean()),
            "held_per_landscape_top1": float(ref_fit(hb, held).mean()),
            "held_delivered_share_top1": float(hd.mean()),
            "top1_program": {"d": int(d[0]), "code_len": int(Ls[0]), "cb": int(cb[0]),
                             "functional_bytes": int(functional_bytes(top[:1])[0])},
            "top1_sha256": hashlib.sha256(top[0].tobytes()).hexdigest(), "recount_mismatched_top16": recount_bad,
            "offers_audited": offers, "offers_mismatched": offer_bad}
    return info, top


def score(held, control) -> dict:
    q = np.percentile(held, [25, 50, 75])
    qc = np.percentile(control, [25, 50, 75])
    bar = float(qc[1] - 0.5 * (qc[2] - qc[0]))
    return {"held_median_cell": float(q[1]), "iqr_cell": float(q[2] - q[0]), "held_median_control": float(qc[1]),
            "iqr_control": float(qc[2] - qc[0]), "bar": bar, "parity": bool(q[1] >= bar)}


def job(ctx, gens: int = GENS, port: int = PORT, exp_id: str = EXP):
    import redis
    from falkordb import FalkorDB
    r = redis.Redis(host="127.0.0.1", port=port)
    graph = FalkorDB(host="127.0.0.1", port=port, socket_timeout=300).select_graph(GRAPH)
    train, held = Landscapes(TRAIN_SEEDS), Landscapes(HELD_SEEDS)
    arms = {0: ("cell", CELL), 1: ("control", CELL_CTRL)}
    todo = [(f, rs, ai) for f in FAMILIES for rs in range(RUNS_PER_FAMILY) for ai in (1, 0)]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": []}, "clean": True, "ref": False,
                                   "beta": None, "random_mean": None}
    if not st["ref"]:
        st["random_mean"], st["beta"] = random_mean(train), beta_of(train)
        ctx.emit({"kind": "reference", "exp_id": exp_id, "predicate_id": PREDICATE_ID, "gens": gens, "batch": BATCH,
                  "genome_bytes": GLEN, "alpha": ALPHA, "credit": CREDIT, "start": START, "beta": st["beta"],
                  "random_mean_per_train_landscape": st["random_mean"],
                  "random_mean_per_held_landscape": random_mean(held), "status": "control",
                  "ts": round(time.time(), 3)})
        st["ref"] = True
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        fam, rs, ai = todo[st["next"]]
        arm, cell = arms[ai]
        first = fam == FAMILIES[0] and rs == 0
        t0, c0 = time.perf_counter(), time.process_time()
        info, top = run(r, graph, fam, rs, ai, arm, gens, train, held, st["beta"], track=first)
        ok = info["recount_mismatched_top16"] == 0 and info["offers_mismatched"] == 0
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
               "genome_bytes": GLEN, "reader": "top1_train", "beta": st["beta"] if arm == "cell" else 0, **info,
               "held_minus_random": info["held_per_landscape_top1"] - st["random_mean"],
               "status": "record" if arm == "cell" else "control"}
        if first:
            o = oracles(graph, top, train, arm, st["beta"])
            row["oracles"] = o
            ok = ok and o["ok"]
        st["clean"] = bool(st["clean"] and ok)
        row["cpu_s"], row["wall_s"] = round(time.process_time() - c0, 3), round(time.perf_counter() - t0, 3)
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(row["held_per_landscape_top1"])
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
              "gens": gens, "beta": st["beta"], "random_mean": st["random_mean"],
              **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in sc.items()},
              "oracle_clean": st["clean"], "primary": primary,
              "clause_a": "none: nk_stub is not a screened graphworld world", "status": "record" if st["clean"] else "cheat",
              "ts": round(time.time(), 3)})


# ------------------------------------------------------------------ dev (no rows)

def dev(gens: int = 3) -> None:
    """No rows: structural oracle eligibility on random + planted genomes, wall per generation, GENS by the rule."""
    import redis
    from falkordb import FalkorDB
    r = redis.Redis(host="127.0.0.1", port=PORT)
    graph = FalkorDB(host="127.0.0.1", port=PORT, socket_timeout=300).select_graph(GRAPH + "_dev")
    train = Landscapes(TRAIN_SEEDS)
    beta = beta_of(train)
    rng = np.random.Generator(np.random.PCG64(77))
    out = {"beta": beta, "random_mean_train": random_mean(train)}
    for arm in ("cell", "control"):
        out[f"oracles_random_{arm}"] = oracles(graph, init(rng, TOP), train, arm, beta)
    B = init(rng, BATCH)
    brain_bits(B, train)
    c, t = time.process_time(), time.perf_counter()
    for _ in range(gens):
        B = mutate(rng, B)
        bits, _ = brain_bits(B, train)
        cypher_fit(graph, bits, train)
    wall_gen = (time.perf_counter() - t) / gens
    out["per_gen"] = {"wall_s": round(wall_gen, 4), "client_cpu_s": round((time.process_time() - c) / gens, 4)}
    proj = {str(G): round(64 * G * wall_gen * 1.1, 1) for G in GENS_CHOICES}
    fits = [G for G in GENS_CHOICES if 64 * G * wall_gen * 1.1 <= WALL_CAP]
    out["projected_job_wall_s"] = proj
    out["gens_by_rule"] = max(fits) if fits else "INFEASIBLE"
    held = Landscapes(HELD_SEEDS)
    t = time.perf_counter()
    info, _ = run(r, graph, 4200, 0, 0, "cell", 2, train, held, beta, track=True)
    out["run2_wall_s"] = round(time.perf_counter() - t, 3)
    out["run2_info"] = info
    try:
        graph.delete()
    except Exception:
        pass
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dev(int(sys.argv[2]) if len(sys.argv) > 2 else 3) if sys.argv[1] == "dev" else None
