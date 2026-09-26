"""Nyx reading of the Ares W4 hidden-regime fossils (comms #518 / #535 / #538).

Deterministic and re-runnable from the repository root:

    PYTHONPATH=. python nyx/readings/ares_w4_reading.py > roles/Nyx/reports/ARES_W4_READING_2026-09-25_run.txt

Parts:
  A  seed-3 organ description by replay, op substitution, reduction, edge cuts,
     loop-gain basin, and a hand-built two-edge equivalent;
  B  the same SCC / latch instrument over the ten cycle-1 W4 champions;
  C  synthetic-drive tests on seed 3 (ignition threshold, resettability, one-step cue);
  D  consequence check: every champion on W16 (variable-delay cue), prediction
     recorded in the reading before the run.
Reads ares/ only; writes nothing. Held-out seeds are each run's own eval_seeds.
"""
from __future__ import annotations

import copy
import json
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from ares import carriers as C  # noqa: E402
from ares import search as R  # noqa: E402
from ares import substrate as S  # noqa: E402

OBS, NOUT = S.OBS_DIM, S.N_OUT
FOSSIL = f"{ROOT}/ares/fossils/W4_activation_memory_s3/FOSSIL.json"


def load_run(s):
    return json.load(open(f"{ROOT}/ares/runs/sweep_c1/W4_present_s{s}.json"))


def fit(genome, seeds, world="W4", mode="present"):
    pop = S.Population.from_genomes([genome], S.Config(**genome["cfg"]))
    return float(R.rollout(pop, R.make_world(world, mode), seeds)[0])


def trace(genome, seed):
    """Per-step node values (after the step's ticks) for one W4 episode."""
    pop = S.Population.from_genomes([genome], S.Config(**genome["cfg"]))
    rt = S.Runtime(pop)
    w = R.make_world("W4", "present")
    rt.reset()
    obs = w.reset(np.random.default_rng(seed), 1)
    rows = []
    for t in range(w.T):
        o1 = float(obs[0, 1])
        a = rt.step(obs)
        rows.append((t, o1, int(a[0]), rt.v[0].copy()))
        obs, r, _, info = w.step(a)
    return w.r, rows


def drive(g, cue_sched, T=40, nodes=(7, 13, 15)):
    """Synthetic episode: obs1 follows cue_sched (step -> value, else 0)."""
    pop = S.Population.from_genomes([g])
    rt = S.Runtime(pop)
    rt.reset()
    out = []
    for t in range(T):
        obs = np.zeros((1, S.OBS_DIM), dtype=np.float32)
        obs[0, 4] = t / T
        obs[0, 5] = 1.0
        obs[0, 1] = cue_sched.get(t, 0.0)
        a = rt.step(obs)
        out.append((t, int(a[0]), [round(float(rt.v[0, n]), 2) for n in nodes]))
    return out


def scc_report(g):
    inv = C.inventory(g)
    A = {(int(s), int(d)): (w1, w2) for s, d, w1, w2, r in g["edges"]}
    out = []
    for comp in inv["scc_nodes"]:
        cs = set(comp)
        out.append(dict(
            nodes=comp, ops=[g["op"][n] for n in comp], keep=[g["keep"][n] for n in comp],
            loop_edges=[(s, d, A[(s, d)]) for (s, d) in A if s in cs and d in cs],
            cue_in=[(s, d, A[(s, d)]) for (s, d) in A if d in cs and s == 1],
            other_in=[(s, d, A[(s, d)]) for (s, d) in A if d in cs and s not in cs and s != 1],
            outputs_in_loop=[n for n in comp if n >= OBS + g["cfg"]["n_hidden"]],
            downstream=[(s, d, A[(s, d)]) for (s, d) in A if s in cs and d not in cs]))
    return inv, out


def latch_test(g, seeds_r0, seeds_r1, nodes):
    """Post-cue state of `nodes` (sorted) per regime: mean at t=5 and t=39,
    max step-to-step drift after t=10, and whether some node sits at the clip."""
    res = {}
    for label, seeds in (("r0", seeds_r0), ("r1", seeds_r1)):
        vals = []
        for sd in seeds:
            r, rows = trace(g, sd)
            assert r == (0 if label == "r0" else 1), (sd, r)
            vals.append(np.stack([row[3] for row in rows])[:, nodes])
        vals = np.stack(vals)
        drift = float(np.abs(np.diff(vals[:, 10:, :], axis=1)).max())
        res[label] = dict(state_t39=np.round(vals[:, 39, :].mean(0), 3).tolist(),
                          state_t5=np.round(vals[:, 5, :].mean(0), 3).tolist(),
                          drift_after_t10=round(drift, 4),
                          saturated=bool(np.all(np.abs(vals[:, 39, :]).max(-1) >= 7.9)))
    return res


def regime_seeds(seeds, k=4):
    r0, r1 = [], []
    w = R.make_world("W4", "present")
    for sd in seeds:
        w.reset(np.random.default_rng(sd), 1)
        (r1 if w.r else r0).append(sd)
    return r0[:k], r1[:k]


def variant(g, ops=None, remove=(), add_edges=(), scale=None):
    h = copy.deepcopy(g)
    for n, op in (ops or {}).items():
        h["op"][n] = op
    for n in remove:
        h["alive"][n] = 0
        h["edges"] = [e for e in h["edges"] if e[0] != n and e[1] != n]
    for e in add_edges:
        h["edges"].append(list(e))
    for (s, d), k in (scale or {}).items():
        h["edges"] = [[a, b, w1 * (k if (a, b) == (s, d) else 1), w2, r] for a, b, w1, w2, r in h["edges"]]
    return h


def fmt_edges(es):
    return [(a, b, round(w[0], 2), round(w[1], 2)) for a, b, w in es]


def handbuilt(cfg, w_self, w_cue, b14=-1.0, b16=0.0):
    """Zero hidden nodes; output 1 (node 15) with a self-loop and the cue edge."""
    n = OBS + cfg["n_hidden"] + NOUT
    g = dict(cfg=cfg, id=0, parent=-1, alive=[1] * OBS + [0] * cfg["n_hidden"] + [1] * NOUT,
             op=["ADD"] * n, bias=[0.0] * n, keep=[0.0] * n, edges=[[15, 15, w_self, 0, 0], [1, 15, w_cue, 0, 0]])
    g["op"][14] = "CONST"; g["op"][16] = "CONST"
    g["bias"][14] = b14; g["bias"][16] = b16
    return g


def part_a():
    run3 = load_run(3)
    seeds = run3["eval_seeds"]
    g3 = json.load(open(FOSSIL))["genome"]
    print("== A. SEED 3 (cycle-0 fossil genome) replay on the cycle-1 eval seeds:", fit(g3, seeds))
    print("   cycle-1 final genome identical to the fossil genome:",
          run3["final"]["genome"]["edges"] == g3["edges"] and run3["final"]["genome"]["op"] == g3["op"])
    inv, comps = scc_report(g3)
    print("   inventory:", {k: inv[k] for k in ("n_hidden", "n_edges", "self_loops", "self_loops_on_output", "recurrent_edges", "scc_nodes")})
    for c in comps:
        print("   SCC nodes=%s ops=%s loop_edges=%s cue_in=%s other_in=%s outputs_in_loop=%s" % (
            c["nodes"], c["ops"], fmt_edges(c["loop_edges"]), fmt_edges(c["cue_in"]), fmt_edges(c["other_in"]), c["outputs_in_loop"]))
    r0s, r1s = regime_seeds(seeds)
    print("   regime-0 seeds", r0s, "regime-1 seeds", r1s)
    for sd in (r0s[0], r1s[0]):
        r, rows = trace(g3, sd)
        print(f"   --- episode seed {sd} regime {r} (good action {r + 1}); t obs1 act | v7 v13 v15 | v14 v16")
        for t, o1, a, v in rows:
            if t in (0, 1, 2, 3, 4, 5, 10, 20, 39):
                print(f"   t={t:2d} obs1={o1:+.2f} a={a} | {v[7]:+.3f} {v[13]:+.3f} {v[15]:+.3f} | {v[14]:+.3f} {v[16]:+.3f}")
    print("   latch test on ring nodes [7,13,15]:", json.dumps(latch_test(g3, r0s, r1s, [7, 13, 15])))

    W13_7, W7_15, W15_13 = 2.0519094467163086, 1.7618416547775269, 1.0851777791976929
    print("\n== A. SEED 3 substitutions / reductions (held-out on 32 eval seeds; cap 40, floor ~2.6)")
    tests = [
        ("intact", g3),
        ("node7 GATE->ADD (gate condition is 0 > b = -0.37: always open; ADD adds the bias)", variant(g3, ops={7: "ADD"})),
        ("node15 GATE->ADD (port 2 unwired, always open; ADD adds bias -1.13)", variant(g3, ops={15: "ADD"})),
        ("node13 MAX->ADD (remove the rectifier, keep the clip)", variant(g3, ops={13: "ADD"})),
        ("node13 MAX->TANH (bounded at +-1 instead of the clip)", variant(g3, ops={13: "TANH"})),
        ("node7 GATE->TANH", variant(g3, ops={7: "TANH"})),
        ("remove 8,9,10 together (two constants + a dead end)", variant(g3, remove=[8, 9, 10])),
        ("remove 7,8,9,10; bypass 7 with edge 13->15 w=2.052*1.762 (2-cycle 13<->15)",
         variant(g3, remove=[7, 8, 9, 10], add_edges=[[13, 15, W13_7 * W7_15, 0, 0]])),
        ("remove 7,8,9,10,13; output-15 self-loop w=3.92 (the ring's loop gain)",
         variant(g3, remove=[7, 8, 9, 10, 13], add_edges=[[15, 15, W13_7 * W7_15 * W15_13, 0, 0]])),
        ("cut ring edge 15->13 only", variant(g3, scale={(15, 13): 0.0})),
        ("cut ring edge 13->7 only", variant(g3, scale={(13, 7): 0.0})),
        ("cut cue edge 1->13 only", variant(g3, scale={(1, 13): 0.0})),
        ("cut cue edge 1->15 only", variant(g3, scale={(1, 15): 0.0})),
        ("cut both cue edges into the ring", variant(g3, scale={(1, 15): 0.0, (1, 13): 0.0})),
    ]
    for name, h in tests:
        print(f"   {fit(h, seeds):6.2f}  {name}")

    print("\n== A. SEED 3 loop-gain basin: all three ring weights scaled by s (gain = 3.92 s^3)")
    for s in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.5, 2.0, 3.0):
        h = variant(g3, scale={(13, 7): s, (7, 15): s, (15, 13): s})
        print(f"   s={s:.1f} gain={W13_7 * W7_15 * W15_13 * s ** 3:6.2f} fit={fit(h, seeds):6.2f}")

    print("\n== A. HAND-BUILT two-edge equivalent: zero hidden nodes, output-1 self-loop + cue edge")
    for ws in (1.0, 1.5, 2.0, 3.0, 4.0, 6.0):
        print("   self=%.1f  " % ws + "  ".join(f"cue={wc:+.1f}:{fit(handbuilt(g3['cfg'], ws, wc), seeds):5.2f}" for wc in (-0.5, -1.0, -2.0)))


def part_b():
    print("\n== B. TEN LINEAGES (cycle-1 W4_present_s1..10; champion = the genome whose replay equals the dissect heldout)")
    for s in range(1, 11):
        run = load_run(s)
        sd = run["eval_seeds"]
        dis = json.load(open(f"{ROOT}/ares/runs/sweep_c1/W4_present_s{s}_dissect.json"))
        for key in ("final", "best_ever"):
            g = run[key]["genome"]
            f = fit(g, sd)
            if abs(f - dis["heldout"]) < 1e-6:
                break
        inv, comps = scc_report(g)
        r0s, r1s = regime_seeds(sd)
        alive_h = [n for n in range(OBS, OBS + g["cfg"]["n_hidden"]) if g["alive"][n]]
        scc_nodes = sorted({n for c in comps for n in c["nodes"]})
        non_scc_hidden = [n for n in alive_h if n not in scc_nodes]
        f_min = fit(variant(g, remove=non_scc_hidden), sd) if non_scc_hidden else f
        h = copy.deepcopy(g)
        rec = S.recurrent_edge_mask(S.Population.from_genomes([g]))[0]
        h["edges"] = [e for e in h["edges"] if not rec[e[1], e[0]]]
        f_cut = fit(h, sd)
        lt = latch_test(g, r0s, r1s, scc_nodes) if scc_nodes else None
        outs = [OBS + g["cfg"]["n_hidden"] + k for k in range(NOUT)]
        print(f"\n-- s{s}: key={key} heldout={f:.2f} hidden={alive_h} edges={inv['n_edges']} SCCs={inv['scc_nodes']} "
              f"self_loops={inv['self_loops']} (on output {inv['self_loops_on_output']}) keep_nodes={inv['keep_nodes']}")
        for c in comps:
            print(f"   SCC nodes={c['nodes']} ops={c['ops']} loop_edges={fmt_edges(c['loop_edges'])}")
            print(f"       cue_in={fmt_edges(c['cue_in'])} other_in={fmt_edges(c['other_in'])}")
            print(f"       outputs_in_loop={c['outputs_in_loop']} downstream={fmt_edges(c['downstream'])}")
        print(f"   remove non-SCC hidden {non_scc_hidden}: fit={f_min:.2f} | cut every recurrent edge: fit={f_cut:.2f}")
        print(f"   latch test over sorted SCC nodes {scc_nodes}: {json.dumps(lt)}")
        print(f"   output ops={[g['op'][o] for o in outs]} bias={[round(g['bias'][o], 2) for o in outs]}")


def part_c():
    g3 = json.load(open(FOSSIL))["genome"]
    print("\n== C. SEED 3 ignition threshold: constant cue c on steps 0-2 then 0; ring at t=5 and t=39")
    for c in (0.0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.75, -1.0, +0.5, +1.0):
        o = drive(g3, {0: c, 1: c, 2: c})
        print(f"   c={c:+.2f}  t=5 v(7,13,15)={o[5][2]}  t=39 v={o[39][2]} action={o[39][1]}")
    print("\n== C. resettability: set with c=-1 on 0-2, then opposite cue +r on 20-22")
    for r in (0.5, 1.0, 2.0, 3.0, 4.0, 8.0):
        o = drive(g3, {0: -1, 1: -1, 2: -1, 20: r, 21: r, 22: r})
        print(f"   r={r:+.1f}  t=19 v={o[19][2]}  t=22 v={o[22][2]}  t=39 v={o[39][2]} action={o[39][1]}")
    print("\n== C. late SET from the LOW rest state: cue +1 on 0-2, then -r on 20-22")
    for r in (0.3, 0.5, 1.0):
        o = drive(g3, {0: 1, 1: 1, 2: 1, 20: -r, 21: -r, 22: -r})
        print(f"   r={-r:+.1f}  t=19 v={o[19][2]}  t=22 v={o[22][2]}  t=39 v={o[39][2]} action={o[39][1]}")
    print("\n== C. one-step cue of -1 at step 0: ring values and actions t=30..39")
    o = drive(g3, {0: -1.0})
    print("   actions:", [a for _, a, _ in o[30:]])
    for t in range(30, 36):
        print(f"   t={t} v(7,13,15)={o[t][2]}")


def part_d():
    print("\n== D. every W4 champion on W16 (cue window starts in [0,20], reward in the last 10 steps; cap 10)")
    print("   prediction recorded before the run: all ten near the floor, present ~ shuffled")
    for s in range(1, 11):
        run = load_run(s)
        g = run["final"]["genome"]
        sd = run["eval_seeds"]
        print(f"   s{s:<2d} W4={fit(g, sd):5.2f}  W16 present={fit(g, sd, 'W16', 'present'):5.2f}  "
              f"W16 shuffled={fit(g, sd, 'W16', 'shuffled'):5.2f}")


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    part_d()
