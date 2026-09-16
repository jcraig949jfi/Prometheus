"""D-R8-3 (SWARM_R8 s11 H6, descriptor robustness): does E4b's QD COVERAGE claim survive an alternate descriptor family?

E4b (lane E, PASS, receipt in primordial/ledger/E.jsonl): "QD coverage AND qd_score > an archive filled with the same
number of random genomes, median over 3 run seeds, in >= 4/5 worlds" -- coverage_wins 5/5, qd_score wins 5/5, under
E4's GENOME-INTRINSIC descriptor (abstain-row fraction x mean action magnitude, 33 x 33). Round 8 survey (schema only):
no committed rows file keeps full archives, and E4b's sampler was UNSEEDED, so its rows are REFERENCES ONLY; this job
re-runs E4b's own loop with a SEEDED sampler (D-R7-5 precedent). E4's init and mutation operators act directly on the
genome descriptor's axes (a per-genome abstain probability at init; zero_rows / fill_rows in mutation) -- the same
shortcut shape D-R7-5 found behind C-R2-02's coverage advantage. The question is whether the claim is a property of
the search or of that descriptor.

Seen before this predicate: E4b's receipt claim text, its harness, its rows' schema and per-run QD wall (3.4-8.0 s).
DISCLOSED PARTIAL READ from the no-rows dev check (stub ctx, run seed 0 only): the controls' sampled-elite COUNT, which
equals the behaviour QD archive's cell count when < 32 -- world 2 at 3 gens: 1; world 5 at 100 gens: 2; world 1 at 100
gens: >= 32 -- plus QD walls and control flags. No random-archive value, no qd_score, no genome-descriptor value and no
other world or seed was read. That read is why skip_lin_caught is relative (below).

ALTERNATE FAMILY (ONE, fixed now; no second family is ever tried): BEHAVIOURAL, from the rollout's own per-tick charge
log (NbEncounter log_charge [T, env, S], done_tick). Per episode, c_t = charge summed over slots for t < done_tick:
  peak   = argmax_t c_t / max(done_tick - 1, 1)            (first maximum; WHEN the episode peaks)
  spend  = share of t in 1..done_tick-1 with c_t < c_{t-1}  (how often charge falls)
Per genome: mean over its 8 episodes, cell = rint(peak * 32) * 33 + rint(spend * 32) -- the same 33 x 33 grid. Neither
axis is written by an operator; both are what the world did with the genome. Final charge (fitness) is not an axis.

Per world (gen_seed 1..5) x run seed s in 0..2 x descriptor d in (genome, behaviour):
  QD      E4b's loop: GA stream PCG64([100 + s, gs]) (E4b's), E4b mutation/init, batch 256, 100 generations; SEEDED sampler
          PCG64([811, gs, s, d_index]); archive under descriptor d.
  random  E4b's random archive: the SAME random genomes as E4b (PCG64([101 + s, gs])), inserted under descriptor d.
  Fitness is E4b's nb_evaluate definition (clipped final charge summed over slots and the 8 episode seeds) from the
  same logged rollout that yields the behaviour descriptor.

RULE (fixed before any value). holds(d, w) = median_s cells(QD) > median_s cells(random) AND median_s qd_score(QD) >
median_s qd_score(random).
  I1 BINDING REPLICATION: holds(genome, w) in >= 4 of 5 worlds (E4b's own bar, seeded). Else INDETERMINATE.
  k = #worlds with holds(behaviour, w):
    DESCRIPTOR_ROBUST      k >= 4
    DESCRIPTOR_DEPENDENT   k <= 1   (the claim reverses under the alternate family)
    MIXED                  otherwise (weakened, not reversed)
  INDETERMINATE if I1 or a binding control fails.
BINDING CONTROLS, run seed 0 of every world:
  log_is_the_world   32 sampled behaviour-archive elites x 8 seeds: NbEncounter trace hash (over the SAME
                     log_regs/log_charge/log_alive/done_tick the descriptor reads) == wforge Encounter trace hash on every
                     episode (0 elites failing); and nb fitness == np fitness on 64 fixed random genomes
  skip_lin_caught    the same sampled elites (up to 32) under NbEncounter skip_lin: >= 90% of them mismatch wforge, with
                     >= 1 elite sampled. RELATIVE, not E4b's absolute 30/32: amended in the no-rows dev check BEFORE the
                     predicate, because a behaviour archive can hold fewer than 32 elites (disclosed in the predicate)
REPORTED, NOT JUDGED: coverage-only and qd_score-only win counts per descriptor; best fitness; cells per arm per
world; E4b's published claim text. Grids differ in reachable area, so NO cross-descriptor cell counts are compared.
evidence_class OBSERVATION (5 worlds x 3 run seeds; not a 32/4/8 family sample): no PASS/FAIL. E4b's receipt is NOT
revisited: its sampler was unseeded, so a DESCRIPTOR_DEPENDENT reading applies to the claim, not to E4b's rows.

    worker job = primordial.cohorts.d.r8_3_e4b_descriptor_robustness:job
"""
from __future__ import annotations

import time

import numpy as np

from primordial.qd import e4_run as E4
from primordial.qd.archive import LuaArchive
from primordial.soup.b1.nb_world import NbEncounter

EXP = "D-R8-3-e4b-descriptor-robustness"
PREDICATE_ID = EXP
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
WORLDS = (1, 2, 3, 4, 5)
RUN_SEEDS = (0, 1, 2)
DESCRIPTORS = ("genome", "behaviour")
GENS, BATCH, GRID = 100, 256, E4.GRID
PORT = 6393
MAJORITY, DEPENDENT_MAX = 4, 1
N_ORACLE, SKIP_LIN_SHARE = 32, 0.9
E4B_CLAIM = ("QD coverage AND qd_score > a random-filled archive at equal evaluations (median over seeds) in >=4/5 "
             "worlds each; published coverage_wins 5/5, qd_score wins 5/5 (UNSEEDED sampler: reference only)")


def behaviour(log_charge: np.ndarray, done_tick: np.ndarray, k: int) -> np.ndarray:
    """log_charge [T, P*k, S], done_tick [P*k] -> cell uint32 [P] (mean over the k episodes of each genome)."""
    T = log_charge.shape[0]
    c = log_charge.sum(2).T.astype(np.int64)                       # [n, T]
    t = np.arange(T)[None, :]
    alive = t < done_tick[:, None]
    masked = np.where(alive, c, np.iinfo(np.int64).min)
    peak = masked.argmax(1) / np.maximum(done_tick - 1, 1)
    fall = (c[:, 1:] < c[:, :-1]) & alive[:, 1:]
    steps = np.maximum(done_tick - 1, 0)
    spend = np.where(steps > 0, fall.sum(1) / np.maximum(steps, 1), 0.0)
    peak, spend = peak.reshape(-1, k).mean(1), spend.reshape(-1, k).mean(1)
    return (np.rint(peak * 32) * GRID + np.rint(spend * 32)).astype(np.uint32)


def rollout(spec: E4.Spec, G: np.ndarray, cheat: str = ""):
    """E4b's nb_evaluate with the log kept: -> (fitness int32 [P], behaviour cell [P], world)."""
    P, k = len(G), len(E4.SEEDS)
    w = NbEncounter(spec.mech, spec.wid, cheat=cheat)
    w.prepare(np.tile(E4.SEEDS, P), log=True)
    acts = np.ascontiguousarray(np.repeat(G, k, axis=0).transpose(1, 0, 2, 3)).astype(np.int32)
    w.run(acts)
    last = w.done_tick - 1
    ep = np.clip(w.log_charge[last, np.arange(P * k)], 0, None)
    return ep.sum(1).reshape(P, k).sum(1).astype(np.int32), behaviour(w.log_charge, w.done_tick, k), w


def cells_of(spec, G, d: str):
    fit, beh, _ = rollout(spec, G)
    return fit, (E4.descriptor(G) if d == "genome" else beh)


def qd(spec, r, gs: int, s: int, d: str, gens: int = GENS, batch: int = BATCH):
    di = DESCRIPTORS.index(d)
    arch = LuaArchive(r, f"d-r8-3-q-{gs}-{s}-{di}", spec.glen, sampler_seed=[811, gs, s, di])
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([100 + s, gs]))
    t0 = time.perf_counter()
    for _ in range(gens):
        par = arch.sample(batch)
        kids = E4.init_genomes(rng, spec, batch) if len(par) == 0 else E4.mutate(rng, spec, spec.unpack(par))
        fit, cell = cells_of(spec, kids, d)
        arch.insert(cell, fit, spec.pack(kids), np.zeros((batch, 2), np.uint32))
    el = arch.dump()
    return arch, {"cells": len(el), "qd_score": int(sum(v[0] for v in el.values())),
                  "best": int(max(v[0] for v in el.values())), "wall_s": round(time.perf_counter() - t0, 2)}


def random_archive(spec, r, gs: int, s: int, d: str, gens: int = GENS, batch: int = BATCH):
    di = DESCRIPTORS.index(d)
    arch = LuaArchive(r, f"d-r8-3-r-{gs}-{s}-{di}", spec.glen, sampler_seed=[812, gs, s, di])
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([101 + s, gs]))
    for _ in range(gens):
        kids = E4.init_genomes(rng, spec, batch)
        fit, cell = cells_of(spec, kids, d)
        arch.insert(cell, fit, spec.pack(kids), np.zeros((batch, 2), np.uint32))
    el = arch.dump()
    arch.clear()
    return {"cells": len(el), "qd_score": int(sum(v[0] for v in el.values())),
            "best": int(max(v[0] for v in el.values()))}


def controls(spec, arch, gs: int) -> dict:
    el = E4.sample_elites(arch, spec, 5)[:N_ORACLE]
    k = len(E4.SEEDS)
    out = {}
    for name, cheat in (("honest", ""), ("skip_lin", "skip_lin")):
        _, _, w = rollout(spec, el, cheat)
        hashes = [h.decode() for h in w.trace_hashes()]
        bad = np.zeros(len(el), bool)
        for e in range(len(el) * k):
            h, _ = E4.wforge_replay(spec, el[e // k], E4.SEEDS[e % k])
            bad[e // k] |= h != hashes[e]
        out[name] = {"elites": len(el), "elites_failing": int(bad.sum())}
    chk = E4.init_genomes(np.random.Generator(np.random.PCG64(gs)), spec, 64)
    out["nb_np_fitness_equal"] = bool(np.array_equal(rollout(spec, chk)[0], E4.evaluate(spec, chk)[0]))
    n = out["honest"]["elites"]
    out["ok"] = bool(n >= 1 and out["honest"]["elites_failing"] == 0
                     and out["skip_lin"]["elites_failing"] >= SKIP_LIN_SHARE * n
                     and out["nb_np_fitness_equal"])
    return out


def holds(rows: list[dict], d: str, gs: int) -> dict:
    xs = [x for x in rows if x["descriptor"] == d and x["gen_seed"] == gs]
    med = lambda arm, key: float(np.median([x[arm][key] for x in xs]))
    cov = med("qd", "cells") > med("random", "cells")
    sco = med("qd", "qd_score") > med("random", "qd_score")
    return {"n": len(xs), "coverage_win": bool(cov), "qd_score_win": bool(sco), "holds": bool(cov and sco and len(xs) == 3)}


def decide(rows: list[dict], controls_ok: bool) -> tuple[str, dict]:
    per = {d: {str(w): holds(rows, d, w) for w in WORLDS} for d in DESCRIPTORS}
    count = {d: sum(v["holds"] for v in per[d].values()) for d in DESCRIPTORS}
    stats = {"per_world": per, "worlds_holding": count,
             "coverage_wins": {d: sum(v["coverage_win"] for v in per[d].values()) for d in DESCRIPTORS},
             "qd_score_wins": {d: sum(v["qd_score_win"] for v in per[d].values()) for d in DESCRIPTORS},
             "i1": count["genome"] >= MAJORITY}
    complete = len(rows) == len(WORLDS) * len(RUN_SEEDS) * len(DESCRIPTORS)
    if not (complete and controls_ok and stats["i1"]):
        return "INDETERMINATE", stats
    k = count["behaviour"]
    if k >= MAJORITY:
        return "DESCRIPTOR_ROBUST", stats
    if k <= DEPENDENT_MAX:
        return "DESCRIPTOR_DEPENDENT", stats
    return "MIXED", stats


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID, gens: int = GENS,
        worlds=WORLDS, run_seeds=RUN_SEEDS, port: int = PORT):
    import redis
    t0 = time.perf_counter()
    r = redis.Redis(host="127.0.0.1", port=port)
    work = [(gs, s, d) for gs in worlds for s in run_seeds for d in DESCRIPTORS]
    st = ctx.load_checkpoint() or {"next": 0, "rows": [], "controls": {}}
    while st["next"] < len(work):
        if ctx.should_pause():
            ctx.pause(st, completed_units=st["next"], remaining_units=len(work) - st["next"])
        gs, s, d = work[st["next"]]
        spec = E4.Spec(gs)
        arch, q = qd(spec, r, gs, s, d, gens)
        rnd = random_archive(spec, r, gs, s, d, gens)
        row = {"kind": "run", "exp": exp, "gen_seed": gs, "world_id": spec.wid, "T": spec.T, "S": spec.S,
               "W": spec.W, "run_seed": s, "descriptor": d, "gens": gens, "batch": BATCH, "qd": q, "random": rnd}
        if s == run_seeds[0] and d == "behaviour":
            c = controls(spec, arch, gs)
            row["controls"] = c
            st["controls"][str(gs)] = c
        arch.clear()
        st["rows"].append(row)
        ctx.emit({**row, "predicate_id": predicate_id, "status": status, "ts": round(time.time(), 3)})
        st["next"] += 1
        ctx.progress(st["next"], len(work) - st["next"])
    ok = len(st["controls"]) == len(worlds) and all(c["ok"] for c in st["controls"].values())
    decision, stats = decide(st["rows"], ok)
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "status": status,
              "evidence_class": "OBSERVATION", "ts": round(time.time(), 3), "worlds": list(worlds),
              "run_seeds": list(run_seeds), "descriptors": list(DESCRIPTORS), "gens": gens, "batch": BATCH,
              "checks": {"I1_genome_descriptor_reproduces_e4b": stats["i1"], "controls_ok": ok},
              "controls": st["controls"], "decision": decision, "stats": stats,
              "reported_not_judged": {"e4b_claim": E4B_CLAIM,
                                      "note": "grids differ in reachable area: no cross-descriptor cell comparison"},
              "wall_s": round(time.perf_counter() - t0, 3)})
