"""PTE-C2B common: namespaces, stepping stones, broken-start construction, lineage-tagged GA.

Operator order: roles/Ananke/prompts/2026-10-05_pte_c2b_directive/ (204a69374). Additive to PTE-C2A: the C2A
instrument (cells, canonical plants, competence rulers, adversaries, held design) is IMPORTED from
roles/Ananke/pte/c2a/ unchanged; no C2A artifact is modified.

Lineage (order s7/s17). Every instruction line of every genome carries an origin tag: True iff the line descends
from the genome injected at gen-0 index 0. Tags follow the GA's own operations exactly:
  * field resampling (p_field) keeps the tag (descent with modification);
  * whole-instruction resampling (p_instr) sets the tag False (a fresh random line);
  * line swap (p_swap) moves tags with the lines;
  * uniform line crossover copies each line's tag from the parent that supplied the line;
  * elites are copied with their tags.
lineage_share(genome) = fraction of lines tagged True. A competent champion is LINEAGE-attributed iff its share
is >= 0.5 (a majority of its lines descend from the injected genome); otherwise it is BACKGROUND.
The tagged operators consume the numpy Generator in EXACTLY the order of prometheus.ananke.search.mutate /
crossover / evolve (tested), so trajectories are identical to the C2A runner's.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "c2a"))
import c2a_common as C  # noqa: E402  (C2A instrument, unchanged)
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.search import _rand_instr  # noqa: E402

A = C.plants.assemble
C2B_NS = 0xC2B01005
BROKEN_QUAL_KEY = 0xB0E1          # C2B_BROKEN_QUAL: brokenness qualification worlds, per cell
BRK_EDIT_KEY = 0xB7E0             # broken-start edit RNG, per (cell, k, idx, attempt)
STEP_QUAL_KEY = 0x57E9            # stepping-stone qualification worlds, per cell
FINAL_CKPT_KEY = 0xC4E7           # B4X checkpoint champion re-evaluation worlds (gens 72/108/144)
LINEAGE_MIN_SHARE = 0.5
QUAL_WORLDS = 128
MAX_BRK_ATTEMPTS = 50
B4X_CHECKPOINTS = (35, 71, 107, 143)  # 0-based generation index at which a champion is taken (gen 36/72/108/144)


# ------------------------------------------------------------------ stepping stones
def relay_step(ph):
    """RELAY-mh stepping stone (declared before search): the C2A plant of record relay_refresh with ONE added
    line that gates emission on the site's own sensor (EMIT := EMIT * SENSE >> 8, nonzero only while sensing).
    Only sensing sites transmit; receivers latch and read out but never forward: a one-hop relay. Removing or
    disabling the gate line restores relay_refresh exactly (one instruction away from multi-hop forwarding)."""
    body = A(ph, [
        ("GT", "T2", "S0", "ZERO", 0), ("GT", "T3", "ZERO", "S0", 0), ("SUB", "S0", "T2", "T3", 0),
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("GT", "T2", "T0", "ZERO", 0), ("GT", "T3", "ZERO", "T0", 0),
        ("SUB", "T1", "T2", "T3", 0), ("MULQ", "T2", "T1", "T1", 0), ("XOR", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T3", 0), ("MULQ", "EMIT", "T2", "T3", 0),
        ("MULQ", "EMIT", "EMIT", "SENSE", 0),                       # the gate (line 11)
        ("MOV", "PAY0", "T1", 0, 0),
        ("SUB", "T3", "T1", "S0", 0), ("MULQ", "T3", "T3", "T2", 0), ("ADD", "S0", "S0", "T3", 0)])
    return C.canonical(np.broadcast_to(body, (ph.rules, *body.shape)).copy())


def relay_step_sense(ph):
    """RELAY-mh stepping stone, candidate 2 (declared at Flight 1 after candidate 1 failed one-hop
    qualification at RELAY-0019 (.54 under loss .3), BEFORE any STEP search): relay_refresh with its emission
    line EMIT := T2*T3 (emit on a sign change of any arrival) replaced by EMIT := SENSE*SENSE (emit on every tick
    the site itself senses). Sensors broadcast every cue tick; receivers latch and read out; nobody forwards.
    Two field edits (operands a, b of line 10) from relay_refresh."""
    body = A(ph, [
        ("GT", "T2", "S0", "ZERO", 0), ("GT", "T3", "ZERO", "S0", 0), ("SUB", "S0", "T2", "T3", 0),
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("GT", "T2", "T0", "ZERO", 0), ("GT", "T3", "ZERO", "T0", 0),
        ("SUB", "T1", "T2", "T3", 0), ("MULQ", "T2", "T1", "T1", 0), ("XOR", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T3", 0), ("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "T1", 0, 0),
        ("SUB", "T3", "T1", "S0", 0), ("MULQ", "T3", "T3", "T2", 0), ("ADD", "S0", "S0", "T3", 0)])
    return C.canonical(np.broadcast_to(body, (ph.rules, *body.shape)).copy())


def flip_step(ph):
    """FLIP stepping stone (declared): RELAY_LATCH (W2-L), canonical encoding. A copy/latch policy: it transports
    the cue and latches the teacher (high same-cue accuracy) but cannot use the mapping change (B ~ .5)."""
    return C.canonical(C.relay_latch(ph))


# Declared candidate order per family; the FIRST candidate that qualifies on ALL four cells of the family is
# the family's stepping stone (one family-wide stone, never a per-cell choice); if none does, STEP is run only
# at cells where that first-all-qualifying rule cannot apply -> see make_plan_c2b.combine.
STEP_CANDIDATES = {"RELAY-mh": [relay_step, relay_step_sense], "FLIP": [flip_step]}
STEPS = {"RELAY-mh": relay_step, "FLIP": flip_step}


def onehop_env(env: envs.EnvSpec, ph) -> envs.EnvSpec:
    """One-hop qualification variant of a RELAY cell: same physics, actuator at transport distance 1."""
    import dataclasses
    return dataclasses.replace(env, d=1)


# ------------------------------------------------------------------ broken starts
def k_edit(plant: np.ndarray, k: int, rng: np.random.Generator):
    """Exactly k DISTINCT (rule, line, field) positions resampled from the GA's per-field distribution
    (search._rand_instr: fields 0-3 uniform 0..255, field 4 uniform -128..127); equal draws are redrawn."""
    x = plant.copy()
    R, L, F = x.shape
    pos = rng.choice(R * L * F, size=k, replace=False)
    edits = []
    for p in pos:
        r, rem = divmod(int(p), L * F)
        line, f = divmod(rem, F)
        old = int(x[r, line, f])
        while True:
            v = int(rng.integers(-128, 128)) if f == 4 else int(rng.integers(0, 256))
            if v != old:
                break
        x[r, line, f] = v
        edits.append([r, line, f, old, v])
    return x, edits


def qual_seeds(cell_key: int, key: int = BROKEN_QUAL_KEY) -> list:
    return assays.world_seeds(C.H_int(C2B_NS, key, cell_key), QUAL_WORLDS)


def broken_start(ph, env, role, plant, k, cell_key, idx, device="cpu", score=None):
    """First qualified broken draw wins (order s6). Attempt a draws an edit set from
    rng(C2B_NS, BRK_EDIT_KEY, cell_key, k, idx, a); it is accepted iff the competence ruler on the
    C2B_BROKEN_QUAL worlds reads FALSE (INDETERMINATE and TRUE are rejected and redrawn). Cap 50 attempts.
    score(genome) -> status may be injected by tests."""
    seeds = qual_seeds(cell_key)
    attempts = []
    for a in range(MAX_BRK_ATTEMPTS):
        rng = np.random.default_rng(C.H_int(C2B_NS, BRK_EDIT_KEY, cell_key, k, idx, a))
        g, edits = k_edit(plant, k, rng)
        if score is None:
            pt, ep = C.eval_programs(ph, env, seeds, [g], device=device)
            comp = C.competence(role, pt[0], ep)
            st, acc = comp["status"], comp["all"]["mean"]
        else:
            st, acc = score(g), None
        attempts.append({"attempt": a, "edits": edits, "status": st, "acc": acc})
        if st == "FALSE":
            return g, attempts
    return None, attempts


# ------------------------------------------------------------------ lineage-tagged GA operators
def mutate_tagged(g, parent, ptag, sp):
    """search.mutate, same RNG consumption order, with line tags."""
    c = parent.copy()
    t = ptag.copy()
    G, L, _ = c.shape
    fresh = _rand_instr(g, (G, L))
    mask = g.random((G, L, 5)) < sp.p_field
    c = np.where(mask, fresh, c)
    if g.random() < sp.p_instr:
        v = _rand_instr(g, ())            # Python evaluates the RHS before the subscript targets
        r, l = g.integers(G), g.integers(L)
        c[r, l] = v
        t[r, l] = False
    if g.random() < sp.p_swap:
        r = g.integers(G)
        i, j = g.integers(L, size=2)
        c[r, [i, j]] = c[r, [j, i]]
        t[r, [i, j]] = t[r, [j, i]]
    return c, t


def crossover_tagged(g, a, b, ta, tb):
    m = g.random(a.shape[:2]) < 0.5
    return np.where(m[..., None], a, b), np.where(m, ta, tb)


def attribute(success: bool, share, arm: str):
    """Success attribution (order s7/s17): a competent champion whose lineage share >= .5 descends from the
    injected genome (BROKEN_LINEAGE_RECOVERY for BRK arms, STEP_LINEAGE_SUCCESS for STEP); any other competent
    champion is BACKGROUND_SUCCESS; a non-competent champion has no attribution (None)."""
    if not success:
        return None
    if share is None or share < LINEAGE_MIN_SHARE:
        return "BACKGROUND_SUCCESS"
    return "BROKEN_LINEAGE_RECOVERY" if arm.startswith("BRK") else "STEP_LINEAGE_SUCCESS"
