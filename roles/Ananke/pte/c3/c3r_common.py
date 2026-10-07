"""PTE-C3R representation-v2 (72h push s4). Minimal, generic, versioned representation changes. The ENGINE IS NOT
MODIFIED: every v2 capability is expressed through existing physics parameters or through the outer search operator,
so version-1 genomes keep version-1 semantics exactly (golden_v1.json re-checked after this change).

Representation spec REP = (prog_len, state_dim, free_lines, op):
  R0 CURRENT     (16, 2, 0, OP0)  the C2 genome spec and the frozen operator
  R1 CAPACITY    (24, 2, 8, OP0)  8 extra lines, initialised FREE (NOP) in every gen-0 genome
  R2 PERSISTENT  (16, 3, 0, OP0)  one extra generic state register S2
  R3 DUPLICATE   (24, 2, 8, OPD)  capacity + duplication-and-divergence
  R4 COMPOSED    (24, 3, 8, OPD)  capacity + persistent register + duplication-and-divergence
  R5 CAP+PERS    (24, 3, 8, OP0)  capacity + persistent register, no duplication (completes the attribution)
GENERIC PERSISTENT STATE: at all four admitted FLIP cells decay_shift = 0, so every S register is already
non-decaying; the added register S2 is therefore exactly "one generic non-decaying register accessible by ordinary
reads/writes". It is not named, initialised (0 like every register) or bound to any input; it is reachable only
through the ordinary dst/a/b fields (indices shift by one, as for any state_dim change).
FREE CAPACITY: lines >= 16 of a 24-line gen-0 genome are NOP (op 0); every other field is drawn as usual.
DUPLICATION-AND-DIVERGENCE (OPD), content-blind and fixed before production: after crossover, with probability
P_DUP = .25 copy a contiguous block of b ~ uniform{2..6} lines from a uniform source start to a destination chosen
uniformly among positions whose whole destination block is NOP lines ("free capacity"); if no such position exists,
the destination is uniform over all positions (overwrite). Then the ordinary OP0 mutation is applied (divergence).
Copied lines keep their lineage tags and receive a DUP-ORIGIN mark (per line, inherited through every later
operation) so champions can be audited for duplicated machinery.
CONDITIONAL-STATE OPCODE (order s4 D): NOT IMPLEMENTED. Representation audit (C3R prereg s2): SEL already performs
conditional assignment, MULQ/XOR conditional gating, and P_FLIP is written with them; no generic missing primitive
was identified that would not amount to a task-semantic opcode.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c3_common as K  # noqa: E402
C = K.C; X = K.X; B = K.B
from prometheus.ananke import assays  # noqa: E402
from prometheus.ananke.search import FINAL_NS, TRAIN_NS, _rand_instr, random_genomes  # noqa: E402

REPS = {"R0": dict(prog_len=16, state_dim=2, free_lines=0, op="OP0"),
        "R1": dict(prog_len=24, state_dim=2, free_lines=8, op="OP0"),
        "R2": dict(prog_len=16, state_dim=3, free_lines=0, op="OP0"),
        "R3": dict(prog_len=24, state_dim=2, free_lines=8, op="OPD"),
        "R4": dict(prog_len=24, state_dim=3, free_lines=8, op="OPD"),
        "R5": dict(prog_len=24, state_dim=3, free_lines=8, op="OP0")}
P_DUP = 0.25
DUP_LENGTHS = (2, 3, 4, 5, 6)


def rep_physics(ph: C.Physics, rep: str) -> C.Physics:
    r = REPS[rep]
    return ph.replace(prog_len=r["prog_len"], state_dim=r["state_dim"]).validate()


def rep_plant(ph_rep: C.Physics) -> np.ndarray:
    """P_FLIP re-encoded for the representation: assembled by register NAME at the rep's state_dim, padded with
    NOP lines to prog_len, canonical (inside the GA's sampling support)."""
    return C.canonical(C.hp_plants.p_flip(ph_rep))


def init_population(g, n, ph_rep, free_lines):
    pop = random_genomes(g, n, ph_rep)
    if free_lines:
        pop[:, :, -free_lines:, 0] = 0                      # op 0 = NOP: free capacity
    return pop


def duplicate(g, c, t, d):
    """One content-blind duplication. c [R,L,5], t lineage tags [R,L], d dup-origin marks [R,L]."""
    c = c.copy(); t = t.copy(); d = d.copy()
    R, L, _ = c.shape
    r = int(g.integers(R))
    b = int(DUP_LENGTHS[int(g.integers(len(DUP_LENGTHS)))])
    s = int(g.integers(0, L - b + 1))
    nop = (c[r, :, 0] % 16) == 0
    free = [p for p in range(0, L - b + 1) if nop[p:p + b].all()]
    pos = free[int(g.integers(len(free)))] if free else int(g.integers(0, L - b + 1))
    blk, tb = c[r, s:s + b].copy(), t[r, s:s + b].copy()
    c[r, pos:pos + b] = blk; t[r, pos:pos + b] = tb; d[r, pos:pos + b] = True
    return c, t, d, (r, b, s, pos, bool(free))


def make_offspring(g, a, ta, da, sp, op):
    if op == "OPD" and g.random() < P_DUP:
        a, ta, da, _ = duplicate(g, a, ta, da)
    c, t = B.mutate_tagged(g, a, ta, sp)
    return c, t, da


def crossover3(g, a, b, ta, tb, da, db):
    m = g.random(a.shape[:2]) < 0.5
    return np.where(m[..., None], a, b), np.where(m, ta, tb), np.where(m, da, db)


def search_seed(cell_key, rep, idx):
    """Fresh C3R seeds. Arms sharing a prog_len/state_dim share nothing by construction (different genome spaces);
    seeds are keyed by idx only so that R-arms with the SAME genome spec and operator family share gen-0 populations."""
    return C.H_int(K.C3_NS, 0x3E9, cell_key, idx)


def evolve_staged(ph_rep, env, sseed, sp, device, rep, gens_to, state=None, init=None, ckpts=(), held=None,
                  role="FLIP", mon_seeds=None, monitor_every=6):
    """Run (or continue) a search to generation `gens_to` (exclusive upper bound of evaluated generations).
    state = None starts fresh; otherwise a dict from a previous call (pop, tags, dup, rng_state, next_gen, curve).
    Checkpoint champions at generation indices in ckpts use the C2 FINAL rule (key H(seed, FINAL_NS, 0xC4E7, gen+1);
    gen index 35 uses C2A's key) and are scored on `held`."""
    rr = REPS[rep]
    if state is None:
        g = np.random.default_rng(sseed)
        pop = init_population(g, sp.pop, ph_rep, rr["free_lines"])
        tags = np.zeros(pop.shape[:3], dtype=bool)
        dup = np.zeros(pop.shape[:3], dtype=bool)
        if init is not None:
            pop[0] = init; tags[0] = True
        gen0, curve, cks = 0, [], {}
    else:
        g = np.random.default_rng(); g.bit_generator.state = state["rng_state"]
        pop, tags, dup = state["pop"], state["tags"], state["dup"]
        gen0, curve, cks = state["next_gen"], list(state["curve"]), dict(state["checkpoints"])
    for gen in range(gen0, gens_to):
        seeds = assays.world_seeds(C.H_int(sseed, TRAIN_NS, gen), sp.M)
        r = assays.evaluate(ph_rep, pop, env, seeds, device=device)
        acc = r.mean()
        f = acc + sp.w_contrast * np.maximum(r.sens_act, 0) + sp.w_any * r.sens_any
        order = np.argsort(-f, kind="stable")
        rec = {"gen": gen, "max_acc": float(acc.max()), "mean_acc": float(acc.mean()),
               "dup_lines_best": int(dup[order[0]].sum()),
               "nop_lines_best": int(((pop[order[0]][..., 0] % 16) == 0).sum())}
        if mon_seeds is not None and (gen % monitor_every == 0):
            pt, ep = C.eval_programs(ph_rep, env, mon_seeds, [pop[order[0]]], device=device)
            c = C.competence(role, pt[0], ep)
            rec["GB"] = {"status": c["status"], "acc": c["all"]["mean"], "B": c["B"]["mean"]}
        curve.append(rec)
        if gen in ckpts:
            key = C.H_int(sseed, FINAL_NS) if gen == 35 else C.H_int(sseed, FINAL_NS, B.FINAL_CKPT_KEY, gen + 1)
            rf = assays.evaluate(ph_rep, pop, env, assays.world_seeds(key, sp.M_final), device=device)
            ci = int(np.argmax(rf.mean()))
            pt, ep = C.eval_programs(ph_rep, env, held, [pop[ci]], device=device)
            cc = C.competence(role, pt[0], ep)
            cks[gen + 1] = {"champion": pop[ci].tolist(), "status": cc["status"], "competence": C.slim(cc),
                            "dup_lines": int(dup[ci].sum()), "champ_index": ci}
        k = max(2, int(sp.pop * sp.trunc))
        par, ptag, pdup = pop[order[:k]], tags[order[:k]], dup[order[:k]]
        nxt = [pop[order[i]] for i in range(sp.elite)]
        ntag = [tags[order[i]] for i in range(sp.elite)]
        ndup = [dup[order[i]] for i in range(sp.elite)]
        while len(nxt) < sp.pop:
            ia = int(g.integers(k))
            a, ta, da = par[ia], ptag[ia], pdup[ia]
            if g.random() < sp.p_cross:
                ib = int(g.integers(k))
                a, ta, da = crossover3(g, a, par[ib], ta, ptag[ib], da, pdup[ib])
            c, t, d = make_offspring(g, a, ta, da, sp, rr["op"])
            nxt.append(c); ntag.append(t); ndup.append(d)
        pop, tags, dup = np.stack(nxt), np.stack(ntag), np.stack(ndup)
    return {"pop": pop, "tags": tags, "dup": dup, "rng_state": g.bit_generator.state, "next_gen": gens_to,
            "curve": curve, "checkpoints": cks}
