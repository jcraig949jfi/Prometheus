"""THE FROZEN CAMPAIGN GRAMMAR.

Every experiment the campaign ever runs is a point in this space. Nothing outside it can
be instantiated, because the producer can only assemble cells from these factors, and
run_campaign refuses to start if the grammar's hash differs from the one recorded in
PREREGISTRATION.md. That is what "no new experiment semantics generated during
execution" means operationally: not a promise, a hash.

WHY DECLARATIVE. Constraints are data, not code, so they hash with the rest. The
functions below interpret the declarations; they cannot add a rule that is not in them.

A CELL is a dict {factor: level}. Its id is a stable short hash. Derived tags (is the
treatment endogenous, is it a spontaneity test, is the constant atomic) are computed,
never stored as free factors, so they cannot drift out of agreement with the cell.

MATCHED CONTROLS. Every cell knows how to produce its own control partner along each
control axis. The scheduler runs pairs; no factor effect is ever read off
scheduler-selected populations alone.
"""
from __future__ import annotations

import hashlib
import json

# ---------------------------------------------------------------- factors
FACTORS = {
    # --- world physics -------------------------------------------------------
    "world": {
        "PAIR_TAPE": "two organisms are concatenated on one arena tape and executed; either may write anywhere in it. Heredity, if any, is whatever the bytes do.",
        "SOUP_MEM": "one shared program memory; organisms are spans, time-sliced round robin; a reaper frees the oldest when memory fills.",
        "GRID": "a discrete torus; one organism per cell; interaction and reproduction reach the von Neumann neighbourhood.",
        "GRAPH": "organisms sit on the nodes of a fixed interaction graph with heterogeneous degree (a GraphWorld-like structure).",
    },
    "environment": {
        "STATIC": "the task distribution and world parameters never change.",
        "NONSTATIONARY_SHIFT": "the task transform and/or regime statistics change at fixed epochs.",
        "COEVO_ENV": "environment parameters are themselves a small evolving population: an environment persists in proportion to how non-trivially it is solved.",
        "RESOURCE_LIMITED": "a finite energy pool refills per epoch; execution costs energy; organisms that cannot pay do not run.",
    },

    # --- organism representation --------------------------------------------
    "representation": {
        "Z8_64": "64-byte Z80-like organisms, byte addressable, variable length instructions.",
        "Z8_32": "32-byte Z80-like organisms: the tightest tape, where copy loops must be short.",
        "Z8_SHARED": "96-byte Z8 organism whose reproductive and task machinery share one tape with no declared boundary.",
        "Z8_SEPARATED": "96-byte Z8 organism with a declared reproduction region and a declared task region; the control for architectural entanglement.",
        "Z8_SLOTTED": "the same bytes in a 4-byte slotted layout, mutated only at slot-aligned positions and never by insertion or deletion, so the reading frame CANNOT shift. This is the fixed-width control for 'mutation alters architecture as well as algorithm'. It stands in for the existing Nestor fixed-width tape organism deliberately: importing another worktree's runtime as a dependency of a 72-hour unattended run would trade the property under test for a fragility, and the property under test is the frame, not the vendor.",
    },

    # --- reproduction physics ------------------------------------------------
    "reproduction": {
        "EXTERNAL": "an ordinary population manager copies selected organisms. The matched exogenous control.",
        "ENDOGENOUS_COPY": "an organism persists only by executing ALLOC + copy + BIRTH itself.",
        "ENDOGENOUS_PARTIAL": "as ENDOGENOUS_COPY, plus SPLIT: a descendant may be declared from an incomplete or asymmetric copy.",
        "OVERWRITE": "reproduction writes over another organism's span; the victim dies.",
        "CONSTRUCTIVE": "reproduction may write only into free substrate.",
        "PAIR_EXECUTION": "two organisms share an arena tape and either may overwrite portions of it; descendants are whatever is read back out.",
    },
    "self_location": {
        "PRIMITIVE": "ED 32 SELF returns the organism's own base and length.",
        "PC_RELATIVE": "no SELF; ED 33 GETPC returns the current pc, so bounds must be computed.",
        "NONE": "neither; the organism must encode or discover its own position.",
    },
    "copy_primitive": {
        "BLOCK": "ED B0 LDIR: a two-byte block copy. A replicator can be four instructions long.",
        "BYTEWISE": "no LDIR; copying requires an explicit loop.",
    },

    # --- pressure coupling ---------------------------------------------------
    "pressure": {
        "NONE_IMPLICIT": "no task coupling at all: survival is implicit in the physics.",
        "TASK_GATED_INTERACTION": "competence raises the probability of being chosen for interaction or of having space to reproduce into.",
        "RESOURCE_GATED": "competence raises energy acquisition; energy pays for execution.",
        "METABOLIC": "every executed instruction costs energy, with no competence coupling.",
        "EXEC_TIME_COST": "the time slice shrinks with genome length.",
        "TAPE_COST": "longer tapes pay a per-epoch survival cost.",
        "EXPLICIT_FITNESS": "an external selector ranks by competence directly (only meaningful with EXTERNAL reproduction).",
        "NOVELTY": "selection or interaction favours behavioural novelty against an archive.",
        "QUALITY_DIVERSITY": "an elite map over (competence, reproductive span) cells.",
        "MINIMAL_CRITERION": "any organism above a low competence bar interacts freely; below it, never.",
        "COMPETITION": "a shared finite resource is divided among organisms by competence share.",
        "PREDATION": "high-competence organisms may consume the span of low-competence neighbours.",
    },

    # --- spatial / ecological structure --------------------------------------
    "structure": {
        "WELL_MIXED": "any organism may interact with any other.",
        "VON_NEUMANN": "interaction only with the four neighbours.",
        "NICHES_ISOLATED": "K sub-populations, no migration.",
        "NICHES_LOW_MIG": "K sub-populations, rare migration.",
        "NICHES_HIGH_MIG": "K sub-populations, frequent migration.",
        "NICHES_PERIODIC_MIG": "migration happens in bursts at fixed epochs.",
        "COMPETENCE_MIG": "only organisms above a competence bar migrate.",
        # P-10, option B: ENV_MIG is REMOVED from the Cycle-9 verification grammar.
        # Its migration gate in the predecessor was `env_difficulty(niche) < 0.5`, but
        # env_difficulty() returns 1.0 for every structure except RESERVOIR, so under
        # ENV_MIG the gate never fired and the level behaved as a plain 0.05 migration
        # rate - semantically inert, and indistinguishable from NICHES_LOW_MIG in its
        # effect on who moves. None of H1-H4 needs it, and a verification campaign
        # should not be repairing a factor it does not use. T-P10 demonstrates the
        # inertness on the predecessor code and asserts the level is absent here.
        #   "ENV_MIG": removed, see T-P10.
        "RESERVOIR": "one persistent easy niche plus harder niches: the easy niche can act as a genetic reservoir.",
    },

    # --- the task and its accessibility topology -----------------------------
    "task_transform": {
        "NEUTRAL": "no task at all; the neutral-task control.",
        "XOR1": "regime 1 expects v XOR 1: one bit, expressible with no literal.",
        "ADD1": "regime 1 expects v + 1: reachable by INC A, no literal at all.",
        "XOR15": "regime 1 expects v XOR 15: needs the literal 0x0F.",
        "XOR5A": "regime 1 expects v XOR 0x5A: needs an awkward literal.",
        "ADD37": "regime 1 expects v + 0x25: needs an awkward literal under a different operator.",
    },
    "read_order": {
        "ANSWER_BEFORE_READ": "the value arrives before the regime, so echoing the first byte scores one half without ever reading the cue: cycle 8's moat.",
        "FORCED_READ": "both regimes' answers depend on a key byte in the input, so the first step toward reading is itself rewarded.",
    },
    "bridge": {
        "VALLEY": "all or nothing scoring: the partial implementation earns nothing.",
        "NEUTRAL_BRIDGE": "the read-and-echo intermediate earns half credit.",
    },
    "seeding": {
        "RANDOM": "the population starts as uniform random bytes. Mandatory for any spontaneous-emergence claim.",
        "SEEDED_REPLICATOR": "a hand-written replicator is seeded. Never evidence for spontaneous origin; used to ask whether replication invades and what it does next.",
        "SEEDED_PLATEAU": "the identity-plateau program is seeded: cycle 8's starting point, in bytes.",
        "SEEDED_READER": "the one-edit ancestor that already reads both inputs is seeded.",
    },

    # --- mutation topology ----------------------------------------------------
    "mutation_operator": {"OPERAND": "only operand bytes are perturbed.",
                          "OPCODE": "only opcode bytes are perturbed.",
                          "BOTH": "any byte may be perturbed."},
    "mutation_locality": {"LOCAL": "point substitution only: the reading frame is preserved.",
                          "STRUCTURAL": "insertion and deletion shift the frame, so downstream bytes decode as different instructions."},
    "mutation_rate": {"LOW": "0.2 percent per byte per copy", "MID": "1 percent", "HIGH": "4 percent"},

    # --- Atlas transplant axes -------------------------------------------------
    # Atlas transplant axes. ONLY axes that are actually implemented appear here. Four of
    # the directive's thirteen ideas are already other factors in this grammar and would
    # have been the same treatment under a second name: drift-versus-selection and
    # implicit-versus-explicit are the `pressure` control axis, equal-compute-elite is
    # EXPLICIT_FITNESS under EXTERNAL, coevolution-versus-curriculum-versus-randomisation
    # is the `environment` factor, and alternative-substrate damage is DAMAGE_CLIFF
    # crossed with `representation`. Declaring them separately would have inflated the
    # campaign map with cells that differ in name only.
    "atlas_axis": {
        "NONE": "no additional instrumented axis.",
        "DAMAGE_CLIFF": "post-run: a qualified scattered Bernoulli damage dose series on sampled organisms, loss curve recorded with its ruler provenance.",
        "LENGTH_ROBUSTNESS": "post-run: damage loss regressed against genome length across sampled organisms.",
        "DELETERIOUS_LOAD": "post-run: competence decay and lethal share under 1..8 accumulated point mutations.",
        "RESIDUE_TRANSPORT": "post-run: sampled organisms re-scored under task variants they never evolved against.",
        "STASIS_ESCAPE": "post-run: longest plateau in the run's own series, and whether it was escaped.",
        "RECOMBINATION": "in-run: a one-point splice operator, with the donated span recorded so dominance is measured.",
        "TRANSITION_DETECTOR": "post-run: change-point detection across the run's metric series.",
    },

    # NOTE: the compute tier is deliberately NOT a factor. It is how much compute a cell
    # gets, not what the experiment means, and putting it in here made cell_id depend on
    # it - so promoting a cell from S to M produced a DIFFERENT family and no family ever
    # accumulated evidence across tiers. The rehearsal showed it plainly: 216 runs, 216
    # families. Tier now travels on the job, beside the cell.
}

# ---------------------------------------------------------------- constraints
# Declarative: {name, if: {factor: [levels]}, then_require: {factor: [allowed levels]}}
CONSTRAINTS = [
    {"name": "pair_tape_repro", "if": {"world": ["PAIR_TAPE"]},
     "then_require": {"reproduction": ["PAIR_EXECUTION", "EXTERNAL"]},
     "why": "a pair tape has no allocator; its heredity is writing, or the exogenous control."},
    {"name": "pair_execution_world", "if": {"reproduction": ["PAIR_EXECUTION"]},
     "then_require": {"world": ["PAIR_TAPE", "GRID", "GRAPH"]},
     "why": "pair execution needs a pairing rule: a soup of spans has none."},
    {"name": "seeded_replicator_needs_self_location",
     "if": {"seeding": ["SEEDED_REPLICATOR"]},
     "then_require": {"self_location": ["PRIMITIVE", "PC_RELATIVE"],
                      "reproduction": ["ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE",
                                       "CONSTRUCTIVE", "PAIR_EXECUTION"]},
     "why": "with self_location NONE nothing reports an organism's own address, so a hand-written replicator must hardcode one and stops replicating the moment it is placed elsewhere. Seeding a 'replicator' that cannot replicate would mislabel the seed and quietly weaken every comparison that uses it."},
    {"name": "slotted_frame_is_fixed", "if": {"representation": ["Z8_SLOTTED"]},
     "then_require": {"mutation_locality": ["LOCAL"]},
     "why": "the slotted layout exists to remove frame shifts; allowing STRUCTURAL there would be the unslotted treatment under a second name, and the campaign would then compare a factor with itself."},
    {"name": "explicit_fitness_needs_external", "if": {"pressure": ["EXPLICIT_FITNESS"]},
     "then_require": {"reproduction": ["EXTERNAL"]},
     "why": "an external selector that ranks and copies IS exogenous reproduction; calling it anything else would hide a restored operator."},
    {"name": "neutral_task_no_task_pressure", "if": {"task_transform": ["NEUTRAL"]},
     "then_require": {"pressure": ["NONE_IMPLICIT", "METABOLIC", "EXEC_TIME_COST", "TAPE_COST",
                                   "NOVELTY", "COMPETITION", "PREDATION"]},
     "why": "there is no competence to gate on when there is no task."},
    {"name": "task_pressure_needs_task", "if": {"pressure": ["TASK_GATED_INTERACTION", "RESOURCE_GATED",
                                                             "EXPLICIT_FITNESS", "MINIMAL_CRITERION",
                                                             "QUALITY_DIVERSITY"]},
     "then_require": {"task_transform": ["XOR1", "ADD1", "XOR15", "XOR5A", "ADD37"]},
     "why": "these pressures are defined by competence."},
    {"name": "seeded_reader_needs_task", "if": {"seeding": ["SEEDED_READER", "SEEDED_PLATEAU"]},
     "then_require": {"task_transform": ["XOR1", "ADD1", "XOR15", "XOR5A", "ADD37"],
                      "representation": ["Z8_64", "Z8_32", "Z8_SHARED", "Z8_SEPARATED", "Z8_SLOTTED"]},
     "why": "those seeds are task instruments in the byte substrate."},
    {"name": "niches_need_subdivisible_world", "if": {"structure": ["NICHES_ISOLATED", "NICHES_LOW_MIG",
                                                                    "NICHES_HIGH_MIG", "NICHES_PERIODIC_MIG",
                                                                    "COMPETENCE_MIG", "RESERVOIR"]},
     "then_require": {"world": ["SOUP_MEM", "GRID", "GRAPH", "PAIR_TAPE"]},
     "why": "every world in the grammar is subdividable; recorded so the producer cannot invent a niche structure elsewhere."},
    {"name": "von_neumann_needs_grid", "if": {"structure": ["VON_NEUMANN"]},
     "then_require": {"world": ["GRID"]},
     "why": "a soup has no lattice neighbours."},
    {"name": "block_copy_is_z8_only", "if": {"copy_primitive": ["BLOCK"]},
     "then_require": {"representation": ["Z8_64", "Z8_32", "Z8_SHARED", "Z8_SEPARATED", "Z8_SLOTTED"]},
     "why": "LDIR is a Z8 instruction; the slotted layout still executes it, it simply cannot be reframed."},
    {"name": "coevo_env_needs_task", "if": {"environment": ["COEVO_ENV"]},
     "then_require": {"task_transform": ["XOR1", "ADD1", "XOR15", "XOR5A", "ADD37"]},
     "why": "an environment's persistence criterion is defined against how it is solved."},
]

# control axes: flipping one factor to its matched control level
CONTROL_AXES = {
    "reproduction": {"ENDOGENOUS_COPY": "EXTERNAL", "ENDOGENOUS_PARTIAL": "EXTERNAL",
                     "OVERWRITE": "EXTERNAL", "CONSTRUCTIVE": "EXTERNAL",
                     "PAIR_EXECUTION": "EXTERNAL", "EXTERNAL": "EXTERNAL"},
    "pressure": {k: "NONE_IMPLICIT" for k in FACTORS["pressure"]},
    "structure": {k: "WELL_MIXED" for k in FACTORS["structure"]},
    "read_order": {"ANSWER_BEFORE_READ": "FORCED_READ", "FORCED_READ": "ANSWER_BEFORE_READ"},
    "task_transform": {"XOR1": "XOR15", "ADD1": "XOR5A", "XOR15": "XOR1", "XOR5A": "ADD1",
                       "ADD37": "ADD1", "NEUTRAL": "NEUTRAL"},
    "environment": {k: "STATIC" for k in FACTORS["environment"]},
    "mutation_locality": {"LOCAL": "STRUCTURAL", "STRUCTURAL": "LOCAL"},
    "copy_primitive": {"BLOCK": "BYTEWISE", "BYTEWISE": "BLOCK"},
    "self_location": {"PRIMITIVE": "NONE", "PC_RELATIVE": "NONE", "NONE": "PRIMITIVE"},
}

ENDOGENOUS = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION")
ATOMIC_TRANSFORMS = ("XOR15", "XOR5A", "ADD37")

# Sized from the rehearsal rather than from a guess: an S run took about two seconds,
# which over 72 hours would have produced several hundred thousand very thin runs.
# Coverage was never going to be the scarce quantity in a space this size; run DEPTH is,
# because an emergence question needs epochs to happen in. These sizes give of order ten
# thousand runs across the campaign, each long enough to be worth indexing.
TIERS = {
    "S": {"pop": 128, "epochs": 600, "slice": 220, "val_episodes": 6, "val_every": 6, "snap_every": 40},
    "M": {"pop": 256, "epochs": 2000, "slice": 300, "val_episodes": 8, "val_every": 10, "snap_every": 100},
    "L": {"pop": 384, "epochs": 4000, "slice": 360, "val_episodes": 12, "val_every": 12, "snap_every": 200},
}

FACTOR_ORDER = tuple(sorted(FACTORS))


# ---------------------------------------------------------------- interpretation
def violations(cell):
    """Which declared constraints this cell breaks. Data in, names out."""
    bad = []
    for c in CONSTRAINTS:
        if all(cell.get(f) in levels for f, levels in c["if"].items()):
            for f, allowed in c["then_require"].items():
                if cell.get(f) not in allowed:
                    bad.append("%s:%s=%s" % (c["name"], f, cell.get(f)))
    return bad


def is_valid(cell):
    if set(cell) != set(FACTORS):
        return False
    for f, lvl in cell.items():
        if lvl not in FACTORS[f]:
            return False
    return not violations(cell)


def derived(cell):
    """Tags computed from the cell, never stored beside it."""
    endo = cell["reproduction"] in ENDOGENOUS
    return {
        "endogenous": endo,
        "spontaneity_test": endo and cell["seeding"] == "RANDOM",
        "constant_kind": "ATOMIC" if cell["task_transform"] in ATOMIC_TRANSFORMS else (
            "NONE" if cell["task_transform"] == "NEUTRAL" else "INCREMENTAL"),
        "has_task": cell["task_transform"] != "NEUTRAL",
        "moat": cell["read_order"] == "ANSWER_BEFORE_READ" and cell["bridge"] == "VALLEY",
        "seeded_instrument": cell["seeding"] != "RANDOM",
    }


def cell_id(cell):
    body = json.dumps({k: cell[k] for k in FACTOR_ORDER}, sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()[:16]


def cell_vector(cell):
    return [cell[f] for f in FACTOR_ORDER]


def control_partner(cell, axis):
    """The matched control for this cell along one axis, or None if the flip is a no-op
    or produces an invalid cell (the caller records which, so a missing control is never
    silently a passed one)."""
    if axis not in CONTROL_AXES:
        return None
    lvl = CONTROL_AXES[axis].get(cell[axis])
    if lvl is None or lvl == cell[axis]:
        return None
    out = dict(cell)
    out[axis] = lvl
    if not is_valid(out):
        # try to repair by relaxing the factors the constraint names, once
        for v in violations(out):
            f = v.split(":")[1]
            if f in ("pressure",):
                out["pressure"] = "NONE_IMPLICIT"
            elif f == "world" and out["reproduction"] == "EXTERNAL":
                out["world"] = "GRID"
            elif f == "copy_primitive":
                out["copy_primitive"] = "BYTEWISE"
        if not is_valid(out):
            return None
    return out


def repair(cell):
    """Push an invalid cell to the nearest valid one by applying the declared
    requirements in order. Used by the producer, never to widen the space."""
    out = dict(cell)
    for _ in range(6):
        bad = violations(out)
        if not bad:
            return out
        c = next(c for c in CONSTRAINTS
                 if all(out.get(f) in levels for f, levels in c["if"].items())
                 and any(out.get(f) not in allowed for f, allowed in c["then_require"].items()))
        for f, allowed in c["then_require"].items():
            if out.get(f) not in allowed:
                out[f] = allowed[0]
    return out if is_valid(out) else None


def sample_cell(rng, fixed=None):
    fixed = fixed or {}
    cell = {f: (fixed[f] if f in fixed else rng.choice(sorted(FACTORS[f]))) for f in FACTORS}
    return repair(cell)


def grammar_hash():
    body = json.dumps({"factors": FACTORS, "constraints": CONSTRAINTS, "control_axes": CONTROL_AXES,
                       "tiers": TIERS, "endogenous": ENDOGENOUS, "atomic": ATOMIC_TRANSFORMS},
                      sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


def space_size():
    n = 1
    for f in FACTORS:
        n *= len(FACTORS[f])
    return n


if __name__ == "__main__":
    import random as _r
    rng = _r.Random(0)
    cells = [sample_cell(rng) for _ in range(2000)]
    ok = [c for c in cells if c and is_valid(c)]
    print(json.dumps({"grammar_hash": grammar_hash(), "factors": len(FACTORS),
                      "raw_space": space_size(), "sampled": len(cells), "valid_after_repair": len(ok),
                      "distinct_cells": len({cell_id(c) for c in ok}),
                      "example": ok[0], "example_derived": derived(ok[0]),
                      "example_control": control_partner(ok[0], "reproduction")}, indent=1))
