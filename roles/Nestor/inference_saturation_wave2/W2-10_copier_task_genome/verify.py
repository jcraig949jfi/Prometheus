"""W2-10 static verification. Single-genome VM calls and single world _pair_interact calls on a runner that
is constructed and never .run(). Outputs verify.json.

(ii)  TASK: tasks.competence (the world's scorer) under (a) the cell's nominal spec FORCED_READ/ADD37/NEUTRAL_BRIDGE
      and (b) every spec COEVO_ENV can assign a niche ({XOR1,ADD1,XOR15,XOR5A} x {FORCED_READ,ANSWER_BEFORE_READ},
      bridge NEUTRAL_BRIDGE), over S world-style (seed, held_seed) pairs. Reader per run_xtg: probe >= cell
      cue_index + 1 = 3; also the niche-correct reader probe >= spec.cue_index() + 1.
      Plus the world's own path: Runner._validate(force=True) with env_pop set to each niche spec.
(i)   COMPETENT: run_de.competent (4-seed screen -> 20-seed rate >= 0.5) and an independent 20-seed rate.
(iv)  STATE-FREE: run_fair.fair_assay entry states R1, R2 (20 seeds each) >= 0.5.
(iii) TWO-STEP: world _pair_interact (ffa6, dense VM, ATOMIC runner) of the construct vs a uniform-random
      partner, donor side random, entry registers fresh or random; record P-11 births; each child genome
      (after world mutation) is re-tested for (i)+(ii)+its own conversions; grandchildren likewise.
"""
from __future__ import annotations

import hashlib
import json
import random
import statistics
import sys
import time

from common import *  # noqa: F401,F403
from common import HERE, CELL, runner, tasks, world, run_dd, run_de, run_ds, run_fair
import construct

S = int(sys.argv[1]) if len(sys.argv) > 1 else 400
NI = int(sys.argv[2]) if len(sys.argv) > 2 else 120
r0 = runner()
CI_CELL = r0.spec.cue_index()
COEVO = [(t, ro) for t in ("XOR1", "ADD1", "XOR15", "XOR5A") for ro in tasks.READ_ORDERS]
SPECS = [("ADD37", "FORCED_READ")] + COEVO


def spec(t, ro):
    return tasks.TaskSpec(transform=t, read_order=ro, bridge=r0.cell["bridge"], n_episodes=r0.t["val_episodes"],
                          budget=140, neutral=False)


def task_profile(g, s_n=None):
    s_n = s_n or S
    out = {}
    for t, ro in SPECS:
        sp = spec(t, ro)
        helds, probes, ok_x, ok_n = [], [], 0, 0
        for k in range(s_n):
            seed = (31_000_000 + k) * 7919 + 10 * k
            c = tasks.competence(g, sp, seed=seed, held_seed=seed + 500000)
            helds.append(c["held"])
            probes.append(c["reads_at_answer"])
            ok_x += c["held"] >= 0.5 and c["reads_at_answer"] >= CI_CELL + 1
            ok_n += c["held"] >= 0.5 and c["reads_at_answer"] >= sp.cue_index() + 1
        out["%s/%s" % (t, ro)] = {"held_mean": round(statistics.mean(helds), 4), "held_min": min(helds),
                                  "P_held_ge_0.5": round(sum(h >= 0.5 for h in helds) / s_n, 4),
                                  "probe_min": min(probes), "probe_max": max(probes),
                                  "P_competent_xtg_ruler": round(ok_x / s_n, 4),
                                  "P_competent_niche_reader": round(ok_n / s_n, 4)}
    return out


def _fresh_runner():
    a = run_ds.cells()[run_dd.CELLS[CELL]]
    return run_ds.runner_cls(world)(dict(a["cell"], atlas_axis="NONE"), 31_000_000, tier=a["tier"])


def world_validate(g):
    """Runner._validate(force=True) with env_pop forced to each COEVO spec (fresh runner, so a fresh val_cache,
    as the world clears it whenever env_pop changes). ADD37/FORCED_READ = env_pop None = the cell spec."""
    out = {}
    for t, ro in SPECS:
        r = _fresh_runner()
        o = r._place(g, 0, niche=0)
        r.env_pop = None if t == "ADD37" else [{"transform": t, "read_order": ro, "score": 0, "age": 0, "id": i}
                                               for i in range(r.n_niches)]
        r._validate(force=True)
        out["%s/%s" % (t, ro)] = {"held": o.held, "comp": o.comp, "probe": o.probe,
                                  "xtg_competent": o.held >= 0.5 and o.probe >= r.spec.cue_index() + 1}
    return out


def cache_demo(g):
    """Same genome in niche 0 (ANSWER_BEFORE_READ) and niche 1 (FORCED_READ), validated in one pass: the
    genome-keyed val_cache hands niche 1 the niche-0 result. Compared with niche 1 validated alone."""
    env = [{"transform": "XOR5A", "read_order": ro, "score": 0, "age": 0, "id": i}
           for i, ro in enumerate(("ANSWER_BEFORE_READ", "FORCED_READ", "ANSWER_BEFORE_READ", "FORCED_READ"))]
    r = _fresh_runner()
    o0 = r._place(g, 0, niche=0)
    o1 = r._place(g, 1, niche=1)
    r.env_pop = env
    r._validate(force=True)
    r2 = _fresh_runner()
    p1 = r2._place(g, 1, niche=1)
    r2.env_pop = env
    r2._validate(force=True)
    return {"niche0_ABR_[held,probe]": [o0.held, o0.probe], "niche1_FR_validated_after_niche0": [o1.held, o1.probe],
            "niche1_FR_validated_alone": [p1.held, p1.probe]}


def screen(g):
    r = runner()
    comp = run_de.competent(world, r, g, {})
    h20, _ = run_dd.assay_one(world, r, g, ("W2-10", hashlib.sha256(g).hexdigest()[:16], 9), run_dd.K2)
    f1 = run_fair.fair_assay(world, r, g, "R1", "SFL" + g.hex(), 20)
    f2 = run_fair.fair_assay(world, r, g, "R2", "SFL" + g.hex(), 20)
    return {"COMPETENT": comp, "rate20_indep": h20 / run_dd.K2, "fair_R1": f1, "fair_R2": f2,
            "STATE_FREE": min(f1, f2) >= 0.5}


class Pair:
    """Two placed organisms in a never-run ffa6 ATOMIC runner; one world _pair_interact per call."""

    def __init__(self, seed):
        a = run_ds.cells()[run_dd.CELLS[CELL]]
        births = self.births = []

        class H(run_ds.runner_cls(world)):
            def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
                births.append((parent, bool(causal)))

        self.r = H(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
        self.d = self.r._place(bytes(64), 0)
        self.p = self.r._place(bytes(64), 1)
        self.k = 0

    def _set(self, o, g, st):
        r = self.r
        r.mem[o.slot:o.slot + r.slot_size] = bytes(r.slot_size)
        r.mem[o.slot:o.slot + 64] = g
        o.length = 64
        o.regs = None if st[0] is None else list(st[0])
        o.fz, o.fc = st[1], st[2]

    def interact(self, g, pg, side, d_st, p_st):
        self._set(self.d, g, d_st)
        self._set(self.p, pg, p_st)
        d_oid, p_oid = self.d.oid, self.p.oid
        del self.births[:]
        self.r.epoch = self.k
        self.k += 1
        a, b = (self.d, self.p) if side == 0 else (self.p, self.d)
        self.r._pair_interact(0, a, b)
        conv = [c for (par, c) in self.births if par == d_oid]
        hij = [c for (par, c) in self.births if par == p_oid]
        return {"conv": bool(conv), "p11": bool(conv and conv[0]), "hijacked": bool(hij),
                "child": self.r._genome(self.p)}


def rand_state(rng):
    return ([rng.randrange(256) for _ in range(8)], rng.randrange(2), rng.randrange(2))


def conversions(g, n, seed, rng):
    pr = Pair(seed)
    out, kids = {}, []
    for mode in ("FRESH", "RANDOM_REGS"):
        c = {"n": n, "converted": 0, "p11": 0, "hijacked": 0}
        for _ in range(n):
            pg = bytes(rng.randrange(256) for _ in range(64))
            if mode == "FRESH":
                ds, ps = (None, 0, 0), (None, 0, 0)
            else:
                ds, ps = rand_state(rng), rand_state(rng)
            res = pr.interact(g, pg, rng.randrange(2), ds, ps)
            c["converted"] += res["conv"]
            c["p11"] += res["p11"]
            c["hijacked"] += res["hijacked"]
            if res["p11"]:
                kids.append(res["child"])
        out[mode] = c
    return out, kids


def child_summary(kids, gen_rng, depth_left):
    rows = []
    for ch in kids:
        tp = task_profile(ch, 60)
        row = {"hex": ch.hex(),
               "nominal_P_competent": tp["ADD37/FORCED_READ"]["P_competent_xtg_ruler"],
               "coevo_FR_min_P_competent": min(v["P_competent_xtg_ruler"] for k, v in tp.items()
                                               if k.endswith("/FORCED_READ") and not k.startswith("ADD37")),
               "coevo_ABR_min_P_held": min(v["P_held_ge_0.5"] for k, v in tp.items() if k.endswith("ANSWER_BEFORE_READ")),
               **screen(ch)}
        if depth_left:
            cv, gk = conversions(ch, 30, 31_700_000, gen_rng)
            row["conversions_vs_random"] = cv
            row["grandchildren"] = child_summary(gk[:4], gen_rng, depth_left - 1)
        rows.append(row)
    return rows


def main():
    t0 = time.time()
    gs = construct.genomes()
    res = {"cell": CELL, "cell_cue_index": CI_CELL, "S_task_seeds": S, "N_interactions_per_mode": NI, "genomes": {}}
    for name, g in gs.items():
        rec = {"hex": g.hex().upper(), "task": task_profile(g), "world_validate": world_validate(g), "screen": screen(g)}
        rng = random.Random("W2-10/" + name)
        cv, kids = conversions(g, NI, 31_500_000, rng)
        rec["conversions_vs_random"] = cv
        if name.startswith("CT_"):
            rec["children"] = child_summary(kids[:6], random.Random("W2-10/kids/" + name), 1)
        res["genomes"][name] = rec
        print(name, json.dumps({"screen": rec["screen"], "conv": cv,
                                "nominal": rec["task"]["ADD37/FORCED_READ"]}), flush=True)
    res["cache_demo_CT_UA"] = cache_demo(gs["CT_UA"])
    res["wall_s"] = round(time.time() - t0, 1)
    (HERE / ("verify.json" if len(sys.argv) < 4 else sys.argv[3])).write_text(json.dumps(res, indent=1))
    print("wall_s", res["wall_s"])


if __name__ == "__main__":
    main()
