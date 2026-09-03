"""Microstructure Observatory v0 -- QUALIFICATION CAMPAIGN (offline).

Produces the packet's central deliverables:
  Q1  power curves (effect size x luminosity -> recovery probability) for
      concentrated, diffuse, and memoryful-base plant classes, with the
      Poisson activation bound at every grid point (power above the bound is
      a LEAKAGE ALARM, not good news)
  Q1b realized false-positive rate under a genuinely noisy null (memoryful
      base, eps=0), against the anytime-valid nominal bound
  Q2  the fragility artifact: naive sign test fires on generic perturbation
      of a functional player; the conditional-rank construction does not
  Q3  dead-code operator floor: an inert dP yields exact ties, wealth 1
  Q4  genealogical drift: per-individual blindness vs lineage trend power
  Q5  structure-vs-outcome: the same planted change detected via trajectory
      structure vs via outcome, at equal luminosity
  Q6  pseudo-signal battery: correlated-seed pseudo-replication;
      double-dipping/winner's-curse demonstration
  Q7  SEALED holdout P5 -- evaluated once, last, results reported as-is

Run:  python -m mhc.qualify
"""
from __future__ import annotations

import sys
from fractions import Fraction

from wforge.genome import de_novo
from wforge.world import expand, stream
from wforge import GRAMMAR_VERSION

from .players import (BasePlayer, P1_DelayedDep, P1_Diffuse, EchoBase,
                      P1_Echo, P3_StructureNotOutcome, P4_GenealogicalDrift,
                      P5_Sealed, GreedyM, NoisyWrap)
from .harness import run_recorded, CausalProbe, trajectory_contrast
from .stats import wealth_process, crossed, naive_sign_test_p, trend_consistency

PROBE = CausalProbe(n_anchors=6)
ADMIT_W = 20        # anytime-valid alpha = 1/20 = 0.05
FLAG_W = 5


def world_pool(n=60, min_ticks=40):
    """Qualifying solo worlds reused across blocks (distinct episode seeds
    per block -- world-family reuse mirrors field conditions; references are
    within-block so exchangeability is unaffected)."""
    pool, s = [], 0
    while len(pool) < n:
        g = de_novo(GRAMMAR_VERSION, 90_000 + s)
        s += 1
        m = expand(g)
        if m.n_slots != 1:
            continue
        probe = BasePlayer(1)
        obs, _, out = run_recorded(m, g.world_id, 7, probe)
        if len(obs) >= min_ticks:
            pool.append((m, g.world_id))
    return pool


def area_stat(mech, wid, ep_seed, factory, tag):
    """Clean-stratum causal-depth area for one player on one encounter,
    plus reactivity count and auxiliary streams."""
    player = factory()
    obs, acts, out = run_recorded(mech, wid, ep_seed, player)
    prof = PROBE.profile(factory, obs, acts,
                         stream("anchors", wid, ep_seed, tag))
    return prof, obs, acts, out


def block_cand_refs(mech, wid, ep_seed, plant_f, ctrl_fs, stat_fn):
    """One block: candidate contrast (plant - ctrl0) and reference contrasts
    (ctrl1-ctrl2, ctrl3-ctrl4, ctrl5-ctrl6). All players independent seeded
    draws; identical world and episode seed."""
    vals = []
    for i, f in enumerate([plant_f] + ctrl_fs):
        vals.append(stat_fn(mech, wid, ep_seed, f, i))
    cand = vals[0] - vals[1]
    refs = [vals[2] - vals[3], vals[4] - vals[5]]
    if len(vals) >= 8:
        refs.append(vals[6] - vals[7])
    return cand, refs


def mu2_stat(mech, wid, ep_seed, factory, tag):
    prof, *_ = area_stat(mech, wid, ep_seed, factory, tag)
    return CausalProbe.area(prof)


def experiment(pool, rng, L, plant_cls, eps, rep):
    """One qualification experiment: L blocks -> wealth trajectory.
    Controls are ALWAYS the same class at eps=0 (exchangeable with the
    candidate under H0 by construction, memoryful bases included)."""
    blocks = []
    for b in range(L):
        m, wid = pool[rng.below(len(pool))]
        ep = 1000 + rng.below(1_000_000)
        sb = 1_000_000 * rep + 1000 * b
        plant_f = (lambda s=sb * 8: (lambda: plant_cls(s, eps)))()
        ctrls = [(lambda s=sb * 8 + i: (lambda: plant_cls(s, 0)))()
                 for i in range(1, 8)]
        blocks.append(block_cand_refs(m, wid, ep, plant_f, ctrls, mu2_stat))
    return blocks


def q1_power(pool):
    print("Q1. POWER CURVES  (recovery probability; anytime-valid wealth)")
    print("    classes: P1 concentrated | P1 diffuse | P1 on memoryful base")
    print("    eps(milli)  L   conc:flag/admit  diff:flag/admit  echo:flag/admit  activ_bound")
    grid_eps = [500, 200, 100, 50, 0]
    reps = 20
    results = {}
    for L in (8, 32):
        for eps in grid_eps:
            row = []
            for cls in (P1_DelayedDep, P1_Diffuse, P1_Echo):
                flag = admit = 0
                for rep in range(reps):
                    rng = stream("q1", cls.__name__, eps, L, rep)
                    blocks = experiment(pool, rng, L, cls, eps, rep)
                    if crossed(blocks, FLAG_W):
                        flag += 1
                    if crossed(blocks, ADMIT_W):
                        admit += 1
                row.append((flag / reps, admit / reps))
            # Poisson activation bound: per anchor P(hit elem)*eps;
            # avg obs width ~6 -> per-anchor ~eps/6000; anchors=6/enc, 1 plant enc/block
            import math
            p_evt = 1 - math.exp(-6 * L * (eps / 1000.0) / 6.0)
            results[(eps, L)] = row
            print(f"    {eps:>9}  {L:>2}   "
                  f"{row[0][0]:.2f}/{row[0][1]:.2f}        "
                  f"{row[1][0]:.2f}/{row[1][1]:.2f}        "
                  f"{row[2][0]:.2f}/{row[2][1]:.2f}      {p_evt:.3f}")
            for i, r in enumerate(row):
                if r[1] > p_evt + 0.10:
                    print(f"      !! LEAKAGE ALARM class {i}: power {r[1]:.2f} "
                          f"exceeds activation bound {p_evt:.3f}")
    return results


def q2_fragility(pool):
    """OPERATOR MECHANICAL COHERENCE artifact (red-team FATAL, instantiated
    deliberately): DampWrap shifts the economy the same way in nearly every
    world. The rejected sign-test reads that as certified structure; the
    reference-conditioned rank cancels it because every draw from the same
    operator distribution carries the same systematic push."""
    from .players import DampWrap
    print("\nQ2. OPERATOR-COHERENCE ARTIFACT  (rejected sign-test vs rank null)")
    reps, L = 15, 20
    naive_fire = rank_fire = 0
    for rep in range(reps):
        rng = stream("q2", rep)
        deltas, blocks = [], []
        for b in range(L):
            m, wid = pool[rng.below(len(pool))]
            ep = 5000 + rng.below(1_000_000)
            s = 100 * rep + b

            def abst(f):
                p = f()
                _, _, out = run_recorded(m, wid, ep, p)
                return out["per_slot"][0]["abstained"]

            base = abst(lambda: BasePlayer(s))
            cand = abst(lambda: DampWrap(BasePlayer(s), 7000 + s)) - base
            refs = [abst(lambda i=i: DampWrap(BasePlayer(s), 7100 + s * 10 + i)) - base
                    for i in range(3)]
            deltas.append(cand)
            blocks.append((cand, refs))
        if naive_sign_test_p(deltas) < Fraction(1, 20):
            naive_fire += 1
        if crossed(blocks, ADMIT_W):
            rank_fire += 1
    print(f"    naive sign test fires : {naive_fire}/{reps}  "
          f"(certifies operator coherence as 'structure')")
    print(f"    conditional-rank fires: {rank_fire}/{reps}  "
          f"(systematic push common to candidate and references cancels)")
    return naive_fire, rank_fire


def q3_deadcode(pool):
    print("\nQ3. DEAD-CODE OPERATOR FLOOR (inert dP -> exact ties, wealth 1)")
    rng = stream("q3")
    ties = trials = 0
    for b in range(20):
        m, wid = pool[rng.below(len(pool))]
        ep = 9000 + rng.below(1_000_000)
        s = 55 * b
        a1 = mu2_stat(m, wid, ep, lambda: P1_DelayedDep(s, 0), 0)
        a2 = mu2_stat(m, wid, ep, lambda: P1_DelayedDep(s, 0), 1)
        trials += 1
        if a1 == a2:
            ties += 1
    print(f"    inert-perturbation twin agreement: {ties}/{trials} exact "
          f"(pipeline-level exact-null calibration)")
    return ties, trials


def q4_genealogical(pool):
    print("\nQ4. GENEALOGICAL DRIFT  (per-individual blindness vs lineage trend)")
    reps, gens, Lg = 12, 8, 8
    indiv = trend = 0
    for rep in range(reps):
        rng = stream("q4", rep)
        levels, any_indiv = [], False
        for g in range(gens):
            blocks = []
            for b in range(Lg):
                m, wid = pool[rng.below(len(pool))]
                ep = 3000 + rng.below(1_000_000)
                s = 1000 * rep + 10 * g + b
                plant_f = (lambda s=s, g=g: (lambda: P4_GenealogicalDrift(s * 8, g)))()
                ctrls = [(lambda s=s, i=i: (lambda: P4_GenealogicalDrift(s * 8 + i, 0)))()
                         for i in range(1, 8)]
                blocks.append(block_cand_refs(m, wid, ep, plant_f, ctrls, mu2_stat))
            levels.append(sum(c for c, _ in blocks))
            if crossed(blocks, ADMIT_W):
                any_indiv = True
        if any_indiv:
            indiv += 1
        if trend_consistency(levels, stream("q4perm", rep)) < Fraction(1, 20):
            trend += 1
    print(f"    any single generation admits : {indiv}/{reps}")
    print(f"    lineage increment-trend fires: {trend}/{reps}  "
          f"(class-C machinery sees what per-individual tests cannot)")
    return indiv, trend


def q5_structure_vs_outcome(pool):
    print("\nQ5. STRUCTURE vs OUTCOME  (same plant, two lenses, equal luminosity)")
    reps, L, eps = 15, 16, 300
    s_fire = o_fire = 0
    for rep in range(reps):
        rng = stream("q5", rep)
        sblocks, oblocks = [], []
        for b in range(L):
            m, wid = pool[rng.below(len(pool))]
            ep = 4000 + rng.below(1_000_000)
            s = 200 * rep + 8 * b

            def both(f, tag):
                p = f()
                obs, acts, out = run_recorded(m, wid, ep, p)
                tc = trajectory_contrast(acts, stream("shuf", wid, ep, tag))
                return tc, out["per_slot"][0]["final_charge"]

            vals = [both((lambda ss=s * 8 + i:
                          (lambda: P3_StructureNotOutcome(ss, eps if i == 0 else 0)))(), i)
                    for i in range(8)]
            sblocks.append((vals[0][0] - vals[1][0],
                            [vals[2][0] - vals[3][0], vals[4][0] - vals[5][0],
                             vals[6][0] - vals[7][0]]))
            oblocks.append((abs(vals[0][1] - vals[1][1]),
                            [abs(vals[2][1] - vals[3][1]),
                             abs(vals[4][1] - vals[5][1]),
                             abs(vals[6][1] - vals[7][1])]))
        if crossed(sblocks, ADMIT_W):
            s_fire += 1
        if crossed(oblocks, ADMIT_W):
            o_fire += 1
    print(f"    trajectory-structure lens admits: {s_fire}/{reps}")
    print(f"    outcome lens admits             : {o_fire}/{reps}  "
          f"(what an outcome metric would have called nothing)")
    return s_fire, o_fire


def q6_pseudosignals(pool):
    print("\nQ6. PSEUDO-SIGNAL BATTERY")
    # N1: correlated-seed pseudo-replication
    rng = stream("q6n1")
    fake_fires = guarded_fires = 0
    for rep in range(30):
        m, wid = pool[rng.below(len(pool))]
        ep = 6000 + rng.below(1_000_000)
        s = 300 * rep
        plant_f = (lambda s=s: (lambda: EchoBase(s * 8)))()
        ctrls = [(lambda s=s, i=i: (lambda: EchoBase(s * 8 + i)))()
                 for i in range(1, 8)]
        one = block_cand_refs(m, wid, ep, plant_f, ctrls, mu2_stat)
        if crossed([one] * 16, ADMIT_W):     # naive: same block counted 16x
            fake_fires += 1
        if crossed([one], ADMIT_W):          # guard: dedup by block id
            guarded_fires += 1
    print(f"    N1 correlated seeds : naive 16x-replication admits {fake_fires}/30; "
          f"block-id dedup admits {guarded_fires}/30")
    # N3: double-dipping / winner's curse
    rng = stream("q6n3")
    cands = []
    for c in range(24):
        blocks = []
        for b in range(8):
            m, wid = pool[rng.below(len(pool))]
            ep = 6500 + rng.below(1_000_000)
            s = 400 * c + 9 * b
            plant_f = (lambda s=s: (lambda: EchoBase(s * 8)))()
            ctrls = [(lambda s=s, i=i: (lambda: EchoBase(s * 8 + i)))()
                     for i in range(1, 8)]
            blocks.append(block_cand_refs(m, wid, ep, plant_f, ctrls, mu2_stat))
        cands.append((c, wealth_process(blocks)))
    top = sorted(cands, key=lambda x: -x[1])[:5]
    fresh = []
    for c, w1 in top:
        blocks = []
        for b in range(8):
            m, wid = pool[rng.below(len(pool))]
            ep = 6900 + rng.below(1_000_000)
            s = 400 * c + 900 + 9 * b
            plant_f = (lambda s=s: (lambda: EchoBase(s * 8)))()
            ctrls = [(lambda s=s, i=i: (lambda: EchoBase(s * 8 + i)))()
                     for i in range(1, 8)]
            blocks.append(block_cand_refs(m, wid, ep, plant_f, ctrls, mu2_stat))
        fresh.append(wealth_process(blocks))
    print(f"    N3 winner's curse   : top-5 selected stage-1 wealth "
          f"{[f'{float(w):.1f}' for _, w in top]}")
    print(f"                          same candidates, fresh blocks     "
          f"{[f'{float(w):.1f}' for w in fresh]}  (regression to null)")
    return fake_fires, guarded_fires


def q7_sealed(pool):
    print("\nQ7. SEALED HOLDOUT P5")
    print("    (deterministic replay of attempt 1 with BOTH preregistered")
    print("    thresholds reported; recorded as attempt 2 per seal protocol)")
    reps, L, eps = 12, 32, 300
    admits = {"mu2_area": 0, "mu2_r0": 0, "mu4": 0}
    flags = {"mu2_area": 0, "mu2_r0": 0, "mu4": 0}
    for rep in range(reps):
        rng = stream("q7", rep)
        b_area, b_r0, b_mu4 = [], [], []
        for b in range(L):
            m, wid = pool[rng.below(len(pool))]
            ep = 8000 + rng.below(1_000_000)
            s = 500 * rep + 11 * b
            hz = m.horizon

            def stats_for(f, tag):
                p = f()
                obs, acts, out = run_recorded(m, wid, ep, p)
                prof = PROBE.profile(f, obs, acts, stream("anchors", wid, ep, tag))
                tc = trajectory_contrast(acts, stream("shuf", wid, ep, tag))
                return CausalProbe.area(prof), prof["r0_count"], tc

            vals = [stats_for((lambda ss=s * 8 + i, hz=hz:
                               (lambda: P5_Sealed(ss, eps if i == 0 else 0, hz)))(), i)
                    for i in range(8)]

            def mk(idx):
                return (vals[0][idx] - vals[1][idx],
                        [vals[2][idx] - vals[3][idx],
                         vals[4][idx] - vals[5][idx],
                         vals[6][idx] - vals[7][idx]])
            b_area.append(mk(0))
            b_r0.append(mk(1))
            b_mu4.append(mk(2))
        for name, bl in (("mu2_area", b_area), ("mu2_r0", b_r0), ("mu4", b_mu4)):
            if crossed(bl, ADMIT_W):
                admits[name] += 1
            if crossed(bl, FLAG_W):
                flags[name] += 1
    for k in admits:
        print(f"    coordinate {k:<9}: flags {flags[k]:>2}/{reps}   admits {admits[k]:>2}/{reps}")
    return admits


def main():
    print("=" * 74)
    print("MICROSTRUCTURE OBSERVATORY v0 -- QUALIFICATION CAMPAIGN")
    print("=" * 74)
    pool = world_pool()
    print(f"world pool: {len(pool)} qualifying solo worlds\n")
    q1 = q1_power(pool)
    q2 = q2_fragility(pool)
    q3 = q3_deadcode(pool)
    q4 = q4_genealogical(pool)
    q5 = q5_structure_vs_outcome(pool)
    q6 = q6_pseudosignals(pool)
    q7 = q7_sealed(pool)
    print("\n" + "=" * 74)
    print("QUALIFICATION COMPLETE")
    print("=" * 74)


if __name__ == "__main__":
    sys.exit(main())
