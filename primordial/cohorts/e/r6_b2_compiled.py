"""E-R6-2 (SWARM_R6 s5 E (2), SMOKE): compiled/batched B2 rollout -- exactness oracle vs RefB2 first, then throughput,
then a new cost estimate for the round 5 B2 admission pilot (PRODUCTION_CANDIDATE 1789468339986-0, ~746 h single worker).

  O1  per adapter spec (b2.oracle.specs(32)) x stream {random table PCG64([1501, j]), forager (Python batch), random
      linear genome PCG64([1601, j])}: compiled hash == RefB2 hash, charges equal, moving actions equal
  O2  skip_mutation on the random stream: compiled cheat hash != RefB2 honest hash on every spec where a live prey moved,
      and == RefB2's own skip_mutation hash (the cheat is the same cheat)
  O3  batching: planted spec, HELD64 seeds 30000..30063 in ONE call -- table (PCG64([1502, seed])) and linear with 4
      genomes (genome_of_env = e % 4) -- every episode's hash == its own RefB2 episode
If any check fails: one INSTRUMENT_FAIL row, no timing row, no throughput number.

Throughput (only after the oracle): planted spec (G's R5 basis, 64 ticks), train seeds 9100.., every wall term the
median of `reps` timed calls of the same batch (compile excluded, reported apart); episodes/s wall and CPU-s/episode.
Cost: metric.b2_screen.pilot_cost / full_screen_cost, the SAME functions G used, at the measured per-episode seconds.

    python -m primordial.fabric.worker submit E primordial.cohorts.e.r6_b2_compiled:job --exp E-R6-2-b2-compiled-rollout \\
        --rows primordial/ledger/rows/E/E-R6-2-b2-compiled-rollout.jsonl --ttl-cpu-s 900 --kwargs '{}'
"""
from __future__ import annotations

import time

import numpy as np

from primordial.soup.b2 import adapter as AD
from primordial.soup.b2 import compiled as CB
from primordial.soup.b2.oracle import specs

HELD64 = list(range(30000, 30064))
TRAIN0 = 9100
R5_EPISODE_S = 0.0016                     # G's R5 basis (PC 1789468339986-0): RefB2 planted spec, timing only
R5_PC = "1789468339986-0"


def _per_episode(policy):
    return lambda obs, t: np.stack([policy(o, t) for o in obs])


def _same(ref: dict, got: dict, e: int = 0) -> dict:
    return {"equal_hash": got["hashes"][e] == ref["hash"], "equal_charges": got["charges"][e].tolist() == ref["charges"],
            "equal_moving": int(got["moving_actions"][e]) == ref["moving_actions"]}


def oracle_spec(j: int, s) -> list[dict]:
    rows = []
    table = AD.random_table(s, [1501, j])
    W, b = CB.random_linear(1, [1601, j])
    streams = {"random": (AD.table_policy(table), lambda: CB.run_table(s, [s.seed], table, record=True)),
               "forager": (AD.forager, lambda: CB.run_policy(s, [s.seed], _per_episode(AD.forager), record=True)),
               "linear": (CB.linear_ref_policy(W, b), lambda: CB.run_linear(s, [s.seed], W, b, record=True))}
    for name, (pol, run) in streams.items():
        ref = AD.episode("ref", s, pol)
        eq = _same(ref, run())
        rows.append({"kind": "o1", "spec": j, "L": s.L, "n": s.n, "stream": name, **eq, "ok": all(eq.values()),
                     "ref_charge": ref["charge"], "moving_actions": ref["moving_actions"]})
        if name == "random":
            ch = CB.run_table(s, [s.seed], table, cheat="skip_mutation", record=True)
            ref_ch = AD.episode("ref", s, pol, cheat="skip_mutation")
            rows.append({"kind": "o2", "spec": j, "stream": name, "cheat": "skip_mutation",
                         "moved": ref["moving_actions"] > 0, "detected_hash": ch["hashes"][0] != ref["hash"],
                         "equals_ref_cheat": ch["hashes"][0] == ref_ch["hash"]
                         and ch["charges"][0].tolist() == ref_ch["charges"],
                         "charge_differs": int(ch["charge"][0]) != ref["charge"]})
    return rows


def oracle_batch(seeds=HELD64, genomes: int = 4) -> dict:
    s0 = AD.planted(0)
    tables = np.stack([AD.random_table(AD.planted(sd), [1502, sd]) for sd in seeds])
    W, b = CB.random_linear(genomes, [1603])
    goe = np.arange(len(seeds)) % genomes
    tab = CB.run_table(s0, seeds, tables, record=True)
    lin = CB.run_linear(s0, seeds, W, b, goe, record=True)
    bad_t, bad_l = [], []
    for e, sd in enumerate(seeds):
        if not all(_same(AD.episode("ref", AD.planted(sd), AD.table_policy(tables[e])), tab, e).values()):
            bad_t.append(sd)
        if not all(_same(AD.episode("ref", AD.planted(sd), CB.linear_ref_policy(W, b, int(goe[e]))), lin, e).values()):
            bad_l.append(sd)
    return {"kind": "o3", "episodes": len(seeds), "genomes": genomes, "table_mismatch_seeds": bad_t,
            "linear_mismatch_seeds": bad_l, "ok": not bad_t and not bad_l}


def _timed(fn, reps: int) -> dict:
    walls, cpus = [], []
    for _ in range(reps):
        c0, t0 = time.process_time(), time.perf_counter()
        fn()
        walls.append(time.perf_counter() - t0)
        cpus.append(time.process_time() - c0)
    return {"reps": reps, "wall_s_median": float(np.median(walls)), "cpu_s_median": float(np.median(cpus)),
            "wall_s": [round(w, 6) for w in walls]}


def job(ctx, n_specs: int = 32, batches=(1024, 16384), reps: int = 5, ref_episodes: int = 256, ref_reps: int = 3,
        seeds_per_genome: int = 128, dev: bool = False, campaign_stage: str = "SMOKE"):
    import numba
    from primordial.metric import b2_screen as BS
    base = {"campaign_stage": campaign_stage, "status": "dev" if dev else "record"}
    st = ctx.load_checkpoint() or {"o12": {}, "o3": None}
    for j, s in enumerate(specs(n_specs)):
        if str(j) in st["o12"]:
            continue
        if ctx.should_pause():
            ctx.pause(st)
        rows = oracle_spec(j, s)
        for r in rows:
            ctx.emit({**base, **r, "status": base["status"] if r["kind"] == "o1" else "cheat"})
        st["o12"][str(j)] = rows
        ctx.checkpoint(st)
    if st["o3"] is None:
        st["o3"] = oracle_batch()
        ctx.emit({**base, **st["o3"]})
        ctx.checkpoint(st)
    rows = [r for v in st["o12"].values() for r in v]
    o1 = {k: {"ok": sum(r["ok"] for r in rows if r["kind"] == "o1" and r["stream"] == k),
              "of": sum(1 for r in rows if r["kind"] == "o1" and r["stream"] == k)} for k in ("random", "forager", "linear")}
    o2 = {"moved_specs": sum(r["moved"] for r in rows if r["kind"] == "o2"),
          "detected_on_moved": sum(r["detected_hash"] for r in rows if r["kind"] == "o2" and r["moved"]),
          "equals_ref_cheat": sum(r["equals_ref_cheat"] for r in rows if r["kind"] == "o2"),
          "specs": sum(1 for r in rows if r["kind"] == "o2")}
    checks = {"O1": all(v["ok"] == v["of"] == n_specs for v in o1.values()),
              "O2": o2["detected_on_moved"] == o2["moved_specs"] > 0 and o2["equals_ref_cheat"] == o2["specs"],
              "O3": st["o3"]["ok"]}
    oracle = {"kind": "oracle_summary", "n_specs": n_specs, "o1": o1, "o2": o2, "o3_ok": st["o3"]["ok"], "checks": checks,
              "oracle_pass": all(checks.values())}
    ctx.emit({**base, **oracle})
    if not oracle["oracle_pass"]:
        ctx.emit({**base, "kind": "verdict", "verdict": "INSTRUMENT_FAIL", "throughput": None,
                  "note": "an exactness check failed: no throughput number is quoted"})
        return

    # ---------------------------------------------------------------- throughput (planted spec, G's R5 basis)
    granted = int(getattr(ctx, "threads", None) or 1)
    threads = sorted({1, max(1, min(granted, numba.config.NUMBA_NUM_THREADS))})
    s0 = AD.planted(0)
    env = {"granted_threads": granted, "numba_threads_max": numba.config.NUMBA_NUM_THREADS, "spec": AD.PLANTED}
    seeds = list(range(TRAIN0, TRAIN0 + ref_episodes))
    tables = np.stack([AD.random_table(AD.planted(sd), [1504, sd]) for sd in seeds])
    ref_tab = _timed(lambda: [AD.episode("ref", AD.planted(sd), AD.table_policy(tables[e])) for e, sd in enumerate(seeds)],
                     ref_reps)
    Wr, br = CB.random_linear(1, [1605])
    n_lin = max(8, ref_episodes // 8)
    ref_lin = _timed(lambda: [AD.episode("ref", AD.planted(sd), CB.linear_ref_policy(Wr, br)) for sd in seeds[:n_lin]],
                     ref_reps)
    timing = [{"backend": "ref_python", "policy": "table", "episodes": ref_episodes, "threads": 1, **ref_tab},
              {"backend": "ref_python", "policy": "linear", "episodes": n_lin, "threads": 1, **ref_lin}]
    c0 = time.perf_counter()
    CB.run_table(s0, seeds[:4], tables[:4])
    CB.run_linear(s0, seeds[:4], Wr, br)
    compile_s = time.perf_counter() - c0
    for B in batches:
        if ctx.should_pause():
            ctx.pause(st)
        G = max(1, B // seeds_per_genome)
        bseeds = [TRAIN0 + (e % seeds_per_genome) for e in range(B)]
        btab = np.random.Generator(np.random.PCG64([1506, B])).integers(0, AD.A, (B, s0.ticks, s0.n_prey))
        W, b = CB.random_linear(G, [1607, B])
        goe = np.arange(B) // seeds_per_genome % G
        for th in threads:
            numba.set_num_threads(th)
            timing.append({"backend": "numba_compiled", "policy": "table", "episodes": B, "threads": th,
                           **_timed(lambda: CB.run_table(s0, bseeds, btab), reps)})
            timing.append({"backend": "numba_compiled", "policy": "linear", "episodes": B, "genomes": G, "threads": th,
                           **_timed(lambda: CB.run_linear(s0, bseeds, W, b, goe), reps)})
        numba.set_num_threads(threads[-1])
    for t in timing:
        t.update(episodes_per_s_wall=t["episodes"] / t["wall_s_median"], episode_s_wall=t["wall_s_median"] / t["episodes"],
                 episode_cpu_s=t["cpu_s_median"] / t["episodes"])
        ctx.emit({**base, "kind": "timing", **env, "compile_s": round(compile_s, 3), **t})

    # ---------------------------------------------------------------- cost estimate (G's functions)
    lin = [t for t in timing if t["backend"] == "numba_compiled" and t["policy"] == "linear" and t["episodes"] == max(batches)]
    basis = {"R5_G_ref_episode_s": R5_EPISODE_S, "ref_python_table_episode_s": timing[0]["episode_s_wall"],
             "ref_python_linear_episode_s": timing[1]["episode_s_wall"]}
    for t in lin:
        basis[f"compiled_linear_t{t['threads']}_episode_s_wall"] = t["episode_s_wall"]
        basis[f"compiled_linear_t{t['threads']}_episode_cpu_s"] = t["episode_cpu_s"]
    cost = {k: {"pilot_wall_h_single_worker": BS.pilot_cost(v)["wall_h_single_worker"],
                "pilot_episodes_total": BS.pilot_cost(v)["episodes_total"],
                "full_screen_wall_h_single_worker": BS.full_screen_cost(v, BS.MAX_SPECS)["wall_h_single_worker"],
                "pilot_per_spec_job_wall_s": BS.pilot_cost(v)["per_spec_job_wall_s"]} for k, v in basis.items()}
    ctx.emit({**base, "kind": "cost_estimate", "production_candidate": R5_PC, "episode_s_basis": basis, "cost": cost,
              "estimator": "episodes_total x per-episode seconds (b2_screen.pilot_cost / full_screen_cost); wall = median of "
                           "reps of one batch call; excludes QD mutation/archive/assembly and oracles, as G's R5 figure did",
              "verdict": "EXACT", "oracle_pass": True})
