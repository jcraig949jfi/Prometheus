"""C-R6-AP-01 (ANTI_PRIOR, cell assigned by code): tucker / nk_stub / cpu_ttl / graphblas / none
(anti_prior.assign exp_id C-R6-AP-01, round 6).

The experimenter received only the cell; the prior and the arm are unread. nk_stub is not a screened graphworld world:
landscape rows only, no clause A claim. The definitions below are fixed before any run.

  world     lane E's NK stub (N=64, K=4). A seed is a LANDSCAPE (C-R2-09): selection on 8 train landscapes
            (9100..9107); score on 64 held-out landscapes (30000..30063), NK fitness per landscape.
  brain     tucker: locus j's 32-entry contribution row / 65535 is a 2x2x2x2x2 tensor X_j (axis q = neighbourhood bit
            4 - q). Weight tensor W = G x_0 U_0 x_1 ... x_4 U_4 (Tucker, core G [2]^5, factors U_q [2, 2]).
            s_j = <W, X_j> + b; bit_j = [s_j > 0]. Genome 53 float32 (G 32, U 20, b 1) = 212 bytes. Target-blind
            decoder (the brain reads only the landscape's own table). Init N(0, 1); mutation gene + N(0, .2) with p 1/8.
            Core rank 2 on binary modes is not compressive (W has 32 free values); disclosed, not changed.
  substrate graphblas: NK fitness is GraphBLAS arithmetic (C-R2-09's gb_fitness: neighbourhood index by mxm over
            circulant weights, row-sum of one-hot selection ewise_mult table). numpy computes the Tucker contraction.
            Archive: E's LuaArchive (seeded sampler) on lane C's Redis :6392. Descriptor: popcount halves of the bits on
            train landscape 0 (33 x 33).
  pressure  cpu_ttl (C-R2-01's rule): the cell arm's loop stops at the first generation boundary where client process
            CPU (time.process_time, audit CPU excluded) reaches TTL = (loop CPU of the job's FIRST control run) / 5.
            The TTL is set by code inside the job, once, before any cell run, and recorded. Redis server-side Lua CPU
            is NOT charged; its per-run delta is reported (loophole, as in C-R5-AP-01b).
  arms      cell (cpu_ttl) vs control (full budget GENS generations x 128), same GA and sampler streams.
  sample    RNG families (4200, 2101, 3303, 5501) x run seeds 0..7: runs_total 32, rng_family_count 4, runs_per_family
            8 per arm. GA PCG64([family, run_seed, arm, 6101]); sampler [family + 1, run_seed, arm, 6101]. Each
            (family, run_seed) runs control first, then cell.
  reader    top1_train: the archive elite with the highest train fitness (ties: smaller genome bytes); value = its mean
            NK fitness per held-out landscape.
  primary   median over the 32 runs of held (cell) >= median (control) - 0.5 * IQR (control).
  oracles   family 4200 run seed 0, each arm:
            world    numpy NKWorld(seed).evaluate == GraphBLAS on every offer of the run (train landscapes) and, in EVERY
                     run, on every final elite: archive fitness == numpy recount from the STORED genome bytes (exact).
                     Cheat K=3 window mismatches >= 90% of eligible elite x landscape rows (bits not all zero), >= 1.
            brain    float64 reference (W rebuilt by explicit loops over core and factor entries) == numpy decision bits
                     on top-16 elites x train landscapes, ties |s| < 1e-5 * (sum|W| + |b| + 1) excluded and counted;
                     cheat identity_last_factor (U_4 := I in the float32 path) mismatches >= 90% of ELIGIBLE rows (rows
                     where the float64 reference with U_4 := I flips a non-tie bit), >= 1 eligible.
            ttl      cell loop CPU < TTL + the largest single-generation CPU of that run.

  worker:  job = primordial.cohorts.c.r6_ap01_tucker_nk_cpu_ttl_graphblas:job
  dev:     python -m primordial.cohorts.c.r6_ap01_tucker_nk_cpu_ttl_graphblas dev   (no rows)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

from primordial.cohorts.c.r2_09_nk_linear_heldout_graphblas import gb_fitness
from primordial.qd.stubworld import GRID, K, N_BITS, N_CELLS, NKWorld

EXP = "C-R6-AP-01-tucker-nk-cpu-ttl-graphblas"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
CELL = {"representation": "tucker", "world": "nk_stub", "pressure": "cpu_ttl", "substrate": "graphblas",
        "channel": "none"}
CELL_CTRL = dict(CELL, pressure="none_control")
N, M, E, BATCH, TOP = N_BITS, 5, 32, 128, 16
NG, GLEN = 53, 212
TRAIN_SEEDS = np.arange(9100, 9108)
HELD_SEEDS = np.arange(30000, 30064)
FAMILIES = (4200, 2101, 3303, 5501)
RUNS_PER_FAMILY = 8
GENS = 400      # no-rows dev check (control, 10 gens): 0.0406 CPU-s / gen. Rule: largest of {100, 200, 300, 400, 800}
                # whose projection (32 control runs + 32 cell runs at 1/5) stays <= 1200 CPU-s; 800 projects 1247, 400 624
TTL_DIV = 5
PORT = 6392
TIE_REL = 1e-5


class Landscapes:
    def __init__(self, seeds):
        self.worlds = [NKWorld(int(s)) for s in seeds]
        self.tables = np.stack([w.table for w in self.worlds])                     # [L, N, 32] int64
        self.x64 = self.tables / 65535.0                                            # float64 [L, N, 32]
        self.x5 = self.x64.astype(np.float32).reshape(len(seeds), N, 2, 2, 2, 2, 2)


def split(g):
    f = np.frombuffer(np.ascontiguousarray(g).tobytes(), "<f4").reshape(len(g), NG)
    return f[:, :E].reshape(-1, 2, 2, 2, 2, 2), f[:, E:E + 4 * M].reshape(-1, M, 2, 2), f[:, NG - 1]


def join(G, U, b):
    P = len(b)
    f = np.concatenate([G.reshape(P, E), U.reshape(P, 4 * M), b.reshape(P, 1)], 1).astype("<f4")
    return np.frombuffer(f.tobytes(), np.uint8).reshape(P, GLEN).copy()


def scores(g, land, cheat=False):
    """float32 s [P, L, N]."""
    G, U, b = split(g)
    if cheat:
        U = U.copy()
        U[:, M - 1] = np.eye(2, dtype=np.float32)
    s = np.einsum("ljabcde,pak,pbm,pcn,pdo,peq,pkmnoq->plj", land.x5, U[:, 0], U[:, 1], U[:, 2], U[:, 3], U[:, 4], G,
                  optimize=True)
    return s + b[:, None, None]


def evaluate(g, land, window=K + 1):
    bits = (scores(g, land) > 0).astype(np.uint8)
    P, L = bits.shape[:2]
    fit = gb_fitness(bits.reshape(P * L, N), np.tile(land.tables, (P, 1, 1)), window).reshape(P, L)
    cells = (bits[:, 0, :32].sum(1) * GRID + bits[:, 0, 32:].sum(1)).astype(np.uint32)
    return fit, cells, bits


def ref_fit(bits, land):
    """numpy reference: NKWorld(seed).evaluate per landscape -> int64 [P, L]."""
    P, L = bits.shape[:2]
    out = np.empty((P, L), np.int64)
    for l in range(L):
        out[:, l] = land.worlds[l].evaluate(np.packbits(bits[:, l], axis=1))[0]
    return out


def ref_W(G, U, cheat=False):
    """float64 W [32] by explicit loops (flat index a in C order: a_q = bit 4 - q of a)."""
    G = np.asarray(G, np.float64).reshape(-1)
    U = np.asarray(U, np.float64).copy()
    if cheat:
        U[M - 1] = np.eye(2)
    W = np.zeros(E)
    for a in range(E):
        aa = [(a >> (M - 1 - q)) & 1 for q in range(M)]
        tot = 0.0
        for k in range(E):
            kk = [(k >> (M - 1 - q)) & 1 for q in range(M)]
            pr = float(G[k])
            for q in range(M):
                pr *= float(U[q, aa[q], kk[q]])
            tot += pr
        W[a] = tot
    return W


def init(rng, P):
    return np.frombuffer(rng.standard_normal((P, NG)).astype("<f4").tobytes(), np.uint8).reshape(P, GLEN).copy()


def mutate(rng, g):
    f = np.frombuffer(np.ascontiguousarray(g).tobytes(), "<f4").reshape(len(g), NG).copy()
    f += (rng.random(f.shape) < 1.0 / 8) * rng.normal(0, 0.2, f.shape).astype(np.float32)
    return np.frombuffer(f.astype("<f4").tobytes(), np.uint8).reshape(len(g), GLEN).copy()


def server_cpu(r) -> float:
    i = r.info("cpu")
    return float(i["used_cpu_sys"]) + float(i["used_cpu_user"])


def brain_oracle(top, land) -> dict:
    s, sc = scores(top, land), scores(top, land, cheat=True)
    G, U, b = split(top)
    bad = ties = elig = caught = 0
    for p in range(len(top)):
        W, Wc = ref_W(G[p], U[p]), ref_W(G[p], U[p], cheat=True)
        tie = TIE_REL * (np.abs(W).sum() + abs(float(b[p])) + 1.0)
        tie_c = TIE_REL * (np.abs(Wc).sum() + abs(float(b[p])) + 1.0)
        r = land.x64 @ W + float(b[p])                                              # [L, N]
        rc = land.x64 @ Wc + float(b[p])
        t = np.abs(r) < tie
        ties += int(t.sum())
        bad += int((((s[p] > 0) != (r > 0)) & ~t).any(axis=1).sum())
        e = (((rc > 0) != (r > 0)) & ~t & ~(np.abs(rc) < tie_c)).any(axis=1)
        elig += int(e.sum())
        caught += int(((((sc[p] > 0) != (r > 0)) & ~t).any(axis=1) & e).sum())
    return {"rows": int(len(top) * len(land.worlds)), "honest_mismatched_rows": bad, "tie_loci": ties,
            "identity_last_factor_eligible_rows": elig,
            "identity_last_factor_share": round(caught / elig, 4) if elig else 0.0}


def world_cheat(bits, land) -> dict:
    P, L = bits.shape[:2]
    ref = ref_fit(bits, land)
    ch = gb_fitness(bits.reshape(P * L, N), np.tile(land.tables, (P, 1, 1)), K).reshape(P, L)
    el = bits.any(axis=2)
    n = int(el.sum())
    return {"k3_eligible_rows": n, "k3_all_zero_rows": int(el.size - n),
            "k3_share": round(float((ch != ref)[el].mean()), 4) if n else 0.0}


def run(r, family, rs, arm_i, gens, ttl, train, held, track=False):
    from primordial.qd.archive import LuaArchive
    rng = np.random.Generator(np.random.PCG64([family, rs, arm_i, 6101]))
    arch = LuaArchive(r, f"c-r6-ap01-{family}-{rs}-{arm_i}", GLEN, sampler_seed=[family + 1, rs, arm_i, 6101])
    arch.clear()
    s0, c0 = server_cpu(r), time.process_time()
    audit = 0.0
    gen_cpu, done, offers, offer_bad = [], 0, 0, 0
    for _ in range(gens):
        if ttl is not None and time.process_time() - c0 - audit >= ttl:
            break
        g0 = time.process_time()
        par = arch.sample(BATCH)
        g = init(rng, BATCH) if len(par) == 0 else mutate(rng, par)
        fit, cells, bits = evaluate(g, train)
        a0 = time.process_time()
        if track:
            offers += fit.size
            offer_bad += int((ref_fit(bits, train) != fit).sum())
        a1 = time.process_time()
        audit += a1 - a0
        arch.insert(cells, fit.sum(1).astype(np.int32), g, np.zeros((BATCH, 2), np.uint32))
        gen_cpu.append(time.process_time() - g0 - (a1 - a0))
        done += 1
    loop_cpu = time.process_time() - c0 - audit
    srv = server_cpu(r) - s0
    el = arch.dump()
    arch.clear()
    order = sorted(el.values(), key=lambda v: (-v[0], v[1]))
    eg = np.frombuffer(b"".join(v[1] for v in order), np.uint8).reshape(-1, GLEN)
    ef = np.array([v[0] for v in order], np.int64)
    fit_e, _, bits_e = evaluate(eg, train)
    ref_e = ref_fit(bits_e, train)
    elite_bad = int((ref_e.sum(1) != ef).sum()) + int((fit_e != ref_e).sum())
    fh = evaluate(eg[:1], held)[0]
    info = {"gens_done": done, "loop_cpu_s": round(loop_cpu, 4), "max_gen_cpu_s": round(max(gen_cpu or [0.0]), 4),
            "audit_cpu_s": round(audit, 4), "redis_server_cpu_s": round(srv, 4), "archive_cells": len(el),
            "coverage": round(len(el) / N_CELLS, 4), "train_fit_top1": int(ef[0]),
            "train_per_landscape_top1": float(ref_e[0].mean()), "held_per_landscape_top1": float(fh.mean()),
            "elites_audited": int(len(eg)), "elites_mismatched": elite_bad, "offers_audited": offers,
            "offers_mismatched": offer_bad}
    extra = None
    if track:
        extra = {"world_k3": world_cheat(bits_e, train), "brain": brain_oracle(eg[:TOP], train)}
    return info, extra


def random_reference(held) -> float:
    rr = np.random.Generator(np.random.PCG64(5))
    rbits = rr.integers(0, 2, (256, 1, N)).astype(np.uint8).repeat(len(held.worlds), 1)
    return float(ref_fit(rbits, held).mean())


def job(ctx, gens: int = GENS, port: int = PORT, exp_id: str = EXP):
    import redis
    r = redis.Redis(host="127.0.0.1", port=port)
    train, held = Landscapes(TRAIN_SEEDS), Landscapes(HELD_SEEDS)
    arms = {0: ("cell", CELL), 1: ("control", CELL_CTRL)}
    todo = [(f, rs, ai) for f in FAMILIES for rs in range(RUNS_PER_FAMILY) for ai in (1, 0)]
    st = ctx.load_checkpoint() or {"next": 0, "held": {"cell": [], "control": []}, "clean": True, "ref": False,
                                   "ttl": None, "random_mean": None}
    if not st["ref"]:
        st["random_mean"] = random_reference(held)
        ctx.emit({"kind": "reference", "exp_id": exp_id, "gens": gens, "batch": BATCH, "genome_bytes": GLEN,
                  "ttl_rule": f"first control run loop CPU / {TTL_DIV}",
                  "random_bits_mean_per_held_landscape": st["random_mean"], "status": "control",
                  "ts": round(time.time(), 3)})
        st["ref"] = True
    while st["next"] < len(todo):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(todo) - st["next"])
        fam, rs, ai = todo[st["next"]]
        arm, cell = arms[ai]
        first = fam == FAMILIES[0] and rs == 0
        ttl = st["ttl"] if arm == "cell" else None
        t0, c0 = time.perf_counter(), time.process_time()
        info, extra = run(r, fam, rs, ai, gens, ttl, train, held, track=first)
        if arm == "control" and st["ttl"] is None:
            st["ttl"] = round(info["loop_cpu_s"] / TTL_DIV, 4)
        ok = info["elites_mismatched"] == 0 and info["offers_mismatched"] == 0
        row = {"kind": "run", "arm": arm, "cell": cell, "family": fam, "run_seed": rs, "gens": gens,
               "ttl_cpu_s": ttl, "genome_bytes": GLEN, "reader": "top1_train", **info,
               "held_minus_random": info["held_per_landscape_top1"] - st["random_mean"],
               "status": "record" if arm == "cell" else "control"}
        if first:
            o = dict(extra)
            wk, bo = o["world_k3"], o["brain"]
            o["ok"] = bool(ok and wk["k3_eligible_rows"] > 0 and wk["k3_share"] >= 0.9
                           and bo["honest_mismatched_rows"] == 0 and bo["identity_last_factor_eligible_rows"] > 0
                           and bo["identity_last_factor_share"] >= 0.9)
            if arm == "cell":
                o["ttl_ok"] = bool(info["loop_cpu_s"] < ttl + info["max_gen_cpu_s"])
                o["ok"] = o["ok"] and o["ttl_ok"]
            row["oracles"] = o
            ok = o["ok"]
        st["clean"] = st["clean"] and ok
        row["cpu_s"], row["wall_s"] = round(time.process_time() - c0, 3), round(time.perf_counter() - t0, 3)
        row["ts"] = round(time.time(), 3)
        st["held"][arm].append(row["held_per_landscape_top1"])
        ctx.emit(row)
        st["next"] += 1
        ctx.progress(st["next"], len(todo) - st["next"])
    q = {a: [float(x) for x in np.percentile(st["held"][a], [25, 50, 75])] for a in st["held"]}
    bar = q["control"][1] - 0.5 * (q["control"][2] - q["control"][0])
    n = {a: len(st["held"][a]) for a in st["held"]}
    full = all(v == len(FAMILIES) * RUNS_PER_FAMILY for v in n.values())
    primary = "INDETERMINATE" if not (st["clean"] and full) else ("PASS" if q["cell"][1] >= bar else "FAIL")
    ctx.emit({"kind": "summary", "exp_id": exp_id, "cell": CELL, "runs_total": n["cell"],
              "rng_family_count": len(FAMILIES), "runs_per_family": RUNS_PER_FAMILY, "families": list(FAMILIES),
              "ttl_cpu_s": st["ttl"], "random_bits_mean": st["random_mean"],
              "held_median_cell": round(q["cell"][1], 2), "iqr_cell": round(q["cell"][2] - q["cell"][0], 2),
              "held_median_control": round(q["control"][1], 2),
              "iqr_control": round(q["control"][2] - q["control"][0], 2), "bar": round(bar, 2),
              "oracle_clean": st["clean"], "primary": primary,
              "clause_a": "none: nk_stub is not a screened graphworld world",
              "status": "record" if st["clean"] else "cheat", "ts": round(time.time(), 3)})


def dev(gens: int = 10) -> None:
    """No rows: oracle eligibility on random genomes, decode round trip, CPU per control generation."""
    import redis
    r = redis.Redis(host="127.0.0.1", port=PORT)
    train, held = Landscapes(TRAIN_SEEDS), Landscapes(HELD_SEEDS)
    rng = np.random.Generator(np.random.PCG64(77))
    g = init(rng, TOP)
    G, U, b = split(g)
    out = {"roundtrip": bool(np.array_equal(join(G, U, b), g)), "brain_random": brain_oracle(g, train)}
    fit, _, bits = evaluate(g, train)
    out["offers_mismatched_random"] = int((ref_fit(bits, train) != fit).sum())
    out["world_k3_random"] = world_cheat(bits, train)
    c, t = time.process_time(), time.perf_counter()
    info, _ = run(r, 4200, 0, 1, gens, None, train, held)
    out["control_cpu_s_per_gen"] = round(info["loop_cpu_s"] / gens, 4)
    out["wall_s_per_gen"] = round((time.perf_counter() - t) / gens, 4)
    out["run_total_cpu_s"] = round(time.process_time() - c, 3)
    out["info"] = info
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dev(int(sys.argv[2]) if len(sys.argv) > 2 else 10) if sys.argv[1] == "dev" else None
