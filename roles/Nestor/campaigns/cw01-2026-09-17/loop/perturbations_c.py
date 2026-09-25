"""Perturbation lattice, batch C: descendants of T-ARCH4 across independent axes. Every candidate
names PARENT_TRAJECTORY (a scoped node), PERTURBATION_DELTA, WHAT_IS_HELD_FIXED, the OLD BOUNDARY
it attacks and WHY it is non-redundant. Scores are opportunity judgements (0-3), recorded before
any run. Computational scope: integer programs on a bounded VM; see pool_arch4.py."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

OUT = HERE / "PERTURBATIONS.jsonl"
C = []


def cand(**k):
    k.setdefault("family", "arch4")
    C.append(k)


# ---------------- REPRESENTATION (the strongest old boundary: no fault boundary to widen)
cand(id="P-C01", parent="T-ARCH4/R1", axis="representation", type="one-axis-census",
     delta="decode rule R2 TRAP-TO-NOP: parents canonicalised (opcode word := word mod 25, behaviour-identical under the VM); after every edit, any opcode word outside the table decodes as NOP (an insulation event, counted) instead of being re-decoded modulo 25. C4-01's census (57 parents x 12 operators x 8 draws, 5 environments, D0..D7) rerun for BOTH decode rules on the canonical parents in one run",
     unchanged="VM, grammar, weights, parents' behaviour, environments, classification constants, draws (same seeds)",
     attacks="'no fault boundary to widen' (C4-03/07 REPRESENTATION_BLOCKED): the report's own Campaign-5 substrate, built as a decode layer rather than an ISA change",
     nonredundant="C4 never ran any decode rule but modulo; the parents' semantics are preserved so the ONLY change is what a new out-of-table word does",
     cost_minutes=6,
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

cand(id="P-C02", parent="T-ARCH4/R1", axis="representation", type="one-axis-census",
     delta="decode rule R3 TRAP-TO-HALT: as P-C01 but an out-of-table opcode word decodes as HALT (the tick ends there): a genuine execution-fault class D1 becomes possible on this substrate",
     unchanged="as P-C01", attacks="D1 'cannot fire' (D4-002); the cliff-vs-slope question under a fatal boundary",
     nonredundant="differs from P-C01 in one bit: silence vs termination", cost_minutes=6,
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=3, information_gain=2, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

cand(id="P-C03", parent="T-ARCH4/R1", axis="representation x search", type="one-axis-walk",
     delta="C4-05's neutral walk (band 1/16 around the ORIGINAL parent, 32 proposals, archived depths 0/2/4/8/16) under decode R2 (trap-to-NOP) vs modulo, 2 walkers per parent; connectivity, acceptance, structural diversity, held-out exaptation",
     unchanged="walk rules, parents (canonicalised), environments, seeds", attacks="'the neutral network is large, connected, cheap' as a property of modulo decode",
     nonredundant="the walk under R2 sees out-of-table edits as silent NOPs, so its neutral neighbourhood is a different graph", cost_minutes=4,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=1))

# ---------------- MUTATION GEOMETRY
cand(id="P-C04", parent="T-ARCH4/M1", axis="mutation_geometry", type="one-axis-census",
     delta="edit LOCALITY at radius 4: (a) DISTRIBUTED = 4 frozen-weight edits anywhere (C4-02's radius 4); (b) BLOCK = 4 edits confined to one contiguous window of 4 instructions chosen once; (c) SEQUENTIAL-SMALL = 4 radius-1 edits each accepted only if the walker stays viable (>= 3/16) between them; loss, displacement, D-classes on the 47 viable parents x 8 draws",
     unchanged="operators, weights, parents, environments, classification", attacks="'distance predicts P(destruction), not degree' measured only for distributed radius",
     nonredundant="C4-02 varied how MANY edits, never WHERE or in what ORDER", cost_minutes=5,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-C05", parent="T-ARCH4/M1", axis="mutation_geometry", type="one-axis-census",
     delta="OPERAND-only vs OPCODE-only edit families: single-word perturbation restricted to operand words (positions 1..3 of an instruction) vs to the opcode word (position 0), 8 draws per parent per family, same census classification; is the cliff an opcode phenomenon?",
     unchanged="parents, environments, classification, decode", attacks="the cliff's locus: C4-01's operators mix both kinds of word",
     nonredundant="no C4 operator isolates the word kind", cost_minutes=4,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=0,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

cand(id="P-C06", parent="T-ARCH4/M1", axis="mutation_geometry x search", type="one-axis-walk",
     delta="LENGTH-BALANCED proposal weights in the neutral walk: insertion+duplication mass set equal to deletion+splice mass (frozen weights otherwise proportional); depth 16, 2 walkers; does the walk still accumulate length and does exaptation change?",
     unchanged="walk rules, band, parents, environments", attacks="C4-08's 'robustness is length': whether length growth is a property of the operator mixture",
     nonredundant="C4 never varied the weights", cost_minutes=4,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

# ---------------- WORLD GEOMETRY
cand(id="P-C07", parent="T-ARCH4/W1", axis="world_geometry", type="one-axis-census",
     delta="the single-edit census with the parent environment made NOISY (noise_rate 0.10) and INTERFERING (interfere=True), each separately, vs the clean environment; does the neutral band (D5) widen or collapse, and does the parent's own reward survive?",
     unchanged="parents, operators, draws, classification, decode", attacks="the map as a property of clean worlds", nonredundant="C4 never perturbed the environment the census scored on",
     cost_minutes=5,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=1, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=1, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-C08", parent="T-ARCH4/W1", axis="world_geometry", type="reanalysis-new-assay",
     delta="WIDER held-out family for exaptation: the depth-16 walkers (regenerated from C4-05 seeds, digest-verified) exposed to the C4-10 family (W1_d2, W1_d3, W2_K2d1, W0_8b) plus noisy/interfering variants of W0 and W2_K2; exaptation rate vs breadth of the held-out family",
     unchanged="walkers, D6 rule, floor, band", attacks="'exaptation stays under the bars' measured against four worlds only",
     nonredundant="the assay family, not the walk, changes", cost_minutes=4,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=1, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=1))

# ---------------- SEARCH DEPTH
cand(id="P-C09", parent="T-ARCH4/S1", axis="search_depth", type="one-axis-walk",
     delta="DEEPER neutral walk: depth 64 with archived depths 16/32/48/64, 2 walkers per viable parent; exaptation, structural and behavioural diversity, length by depth; the report's own first recommendation",
     unchanged="walk rules, band, proposals, environments", attacks="'exaptation grows with depth but stays under the bar' measured to depth 16 only",
     nonredundant="the gradient's continuation or saturation is unknown", cost_minutes=5,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=1, mechanism_discrimination=1, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=0))

cand(id="P-C10", parent="T-ARCH4/S1", axis="search_dynamics", type="one-axis-walk",
     delta="RATCHET band: acceptance relative to the CURRENT walker's reward (band 1/16 of the last accepted) instead of the original parent's; depth 16, 2 walkers; connectivity, drift of reward, exaptation",
     unchanged="proposals, environments, archive depths", attacks="D4-009's choice (no ratchet) as a determinant of what the walk finds",
     nonredundant="one rule flips; drift may leave the band or climb", cost_minutes=4,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

# ---------------- POPULATION DYNAMICS / DAMAGE-RESCUE (evolver-based; heavier)
cand(id="P-C11", parent="T-ARCH4/D1", axis="damage_rescue", type="reposed-ecology",
     delta="C4-09's lateral ecology on UNSOLVED worlds only (W2_K2, W2_K2d1, W1_d1 checked against the 57 parents at generation 0 FIRST) at equal TOTAL budget (control gets the transfer evaluations as extra generations); 3 seeds",
     unchanged="rescue rule (measured reward >= 3/16 and >= median), B=24, replace-worst, evolver", attacks="C4-09's design defect (3 pre-solved worlds) and unequal budget",
     nonredundant="the report's second recommendation", cost_minutes=15,
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=1, mechanism_discrimination=2, cost_now_lower=1,
                 null_becomes_contrast=1, inconclusive_now_posable=3, underexplored_hard_to_operationalise=0))

cand(id="P-C12", parent="T-ARCH4/P1", axis="population_dynamics", type="one-axis-selection",
     delta="C4-08's ordinary selection regime on W2_K2 (N 200, G 100 from the depth-16 walkers) with 4 DEMES of 50 and one migrant per generation vs panmictic; the fresh single-edit assay on the top-32; does robustness-as-neutrality-and-length still accumulate?",
     unchanged="evolver, mutation, world, assay", attacks="robustness accumulation as a property of panmictic tournament selection; cross with CW01's P-A10 finding (structure sets fixation)",
     nonredundant="C4 never varied population structure", cost_minutes=12,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=2, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=1,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

# ---------------- ANTI-GRAVITY / SERENDIPITY
cand(id="P-C13", parent="T-ARCH4/R1", axis="starting_population x representation", type="exploratory", anti_gravity=True,
     delta="the SWAMP: the 10 fully degenerate gen0_random parents (reported apart in C4-05) walked and single-edit-censused under decode R2 (trap-to-NOP) and R3 (trap-to-HALT) as well as modulo; does any decode rule give the swamp a gradient (any D7/D6, any answered_share > 0)?",
     unchanged="parents, environments, classification", attacks="'a swamp by construction' as a property of the decode rule",
     nonredundant="the degenerate stratum was set aside, never perturbed", cost_minutes=3,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=1, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=3))

cand(id="P-C14", parent="T-ARCH4/W1", axis="world_geometry", type="exploratory", anti_gravity=True,
     delta="SILENT DRIFT made audible: depth-16 W0-solver walkers (regenerated) exposed to a graded delay family W1_d1..W1_d4 and to W0 with noise; displacement vs the original parent as a function of delay; where does silent W0 drift become loud?",
     unchanged="walkers, displacement ruler", attacks="the anomaly 'W0 solvers drift silently on W0 (.002) and loudly elsewhere (.17)'",
     nonredundant="an unnamed phenotype with no ruler beyond displacement", cost_minutes=3,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=1,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=2, mechanism_discrimination=1, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=0, underexplored_hard_to_operationalise=3))

cand(id="P-C15", parent="T-ARCH4/D1", axis="damage x cw01-cross", type="serendipity", serendipity=True,
     delta="e07's damage family on the walkers: between evaluations delete a uniform random fraction f in {.1,.2,.3} of INSTRUCTIONS (whole 4-word units, blind to content) of each depth-16 walker; compare loss and displacement with the grammar's deletion operator at matched instruction count; is 'deletion ~0 reference effect' (C4-04) true for blind multi-instruction deletion?",
     unchanged="walkers, environments, classification", attacks="cross: CW01's damage geometry (representation-blind, fraction-based) against C4's operator geometry",
     nonredundant="a damage family from another trajectory", cost_minutes=4,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=2, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-C16", parent="T-ARCH4/M1", axis="mutation_geometry x cw01-cross", type="serendipity", serendipity=True,
     delta="compound: decode R2 (trap-to-NOP) AND length-balanced weights in one walk (depth 16): do the two changes interact (a walk that is both insulated and length-neutral) - deliberately two axes at once in a protected slot",
     unchanged="walk rules, parents, environments", attacks="whether C4's 'neutrality + length' is one phenomenon or two",
     nonredundant="compound by design", cost_minutes=4,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=1, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))


def main():
    existing = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing.add(json.loads(line)["id"])
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    with OUT.open("a", encoding="utf-8") as fh:
        for c in C:
            if c["id"] in existing:
                continue
            c = dict(c)
            c["recorded"] = ts
            c["batch"] = "C"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
    RS.require_ascii_safe(OUT)
    print("appended", added)


if __name__ == "__main__":
    main()
