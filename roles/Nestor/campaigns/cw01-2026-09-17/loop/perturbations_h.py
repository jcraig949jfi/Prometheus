"""Candidate perturbations, batch H (cycle 6): the temporal-response manifold (T-X17 / T-X19 / T-X20) as
the primary object - ruler robustness first (P-G11, amended), then transplants, recombination,
nonstationary lifetime worlds, minimal causal transplantation, two anti-gravity attacks on cycle 6's own
premises, and bounded secondary lanes. D084 and T-R01 are standing metrology, not excavation.
Computational scope: integer programs on a bounded VM; nothing biological."""
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
    C.append(k)


GEOM = "raw response geometry kept: the 30-construction curve set of P-F02 (7 positions x doses 1-4 + 2 order variants), never reduced to a label before the curves are recorded"

cand(id="P-H01", parent="T-X17", family="transplant", axis="representatives x worlds x walks x selection", type="transplant-map", deformation="B", requires=["P-G11"],
     delta="TRANSPLANT MAP of representatives of the four non-immune geometries (START-ANCHORED T-X19, PERIODIC T-X20, ASK-TIME, INPUT-SCHEDULE; 8 each, from P-F02's clusters): into three worlds (W0, W2_K2, W1_d4) under (a) immediate read, (b) a neutral walk (depth 16, archived 4/8/16) in each world, (c) selection (20 generations, 4 representatives per geometry per world). Geometry (%s), reward on all three worlds and ancestry (origin geometry) tracked SEPARATELY. Per geometry x world x condition: distance to the origin curve set and to the world's native tops; transitions named only from the curves." % GEOM,
     unchanged="constructions, walk rules, evolver", attacks="whether the new geometries (T-X19, T-X20) behave like the two known ones under transplant, and whether geometry and reward move together", nonredundant="T-X19/T-X20 were never moved; three-world map never made", cost_minutes=10,
     continuation=["longer neutral windows", "transplant under nonstationary worlds"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

cand(id="P-H02", parent="T-X20", family="recombination", axis="geometry x geometry", type="recombination", deformation="X", requires=["P-G11"], co_parents=["T-X19", "T-X17"],
     delta="RECOMBINATION of representatives from different geometries: one-point splices at 25 / 50 / 75 percent of each parent (both orders), middle-third insertion of one parent into the other, and the frozen grammar's own 'splice' operator with the other parent as mate (4 draws) - for every pair of the four geometries (and same-geometry controls), 4 x 4 representative pairs. Every child: full curve set, reward on W0 / W2_K2 / W1_d4, distance to each parent's curves and to every known centroid. Children are named COMPOSE (both parents' sensitivities present), DOMINATE (one parent), INTERFERE (partial), DISAPPEAR (immune), or NEW (far from both parents and from every known shape); NEW children are clustered and their shapes reported raw. %s" % GEOM,
     unchanged="constructions, VM", attacks="whether temporal geometries are composable organs or whole-genome properties", nonredundant="no recombination across geometries exists", cost_minutes=8,
     continuation=["recombination under selection", "recombination of NEW children"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=3))

cand(id="P-H03", parent="T-ARCH4/W1", family="nonstationary_worlds", axis="lifetime nonstationarity", type="world-deformation", deformation="W", co_parents=["T-X17", "T-X12"],
     delta="NONSTATIONARY LIFETIME WORLDS: the Nestor evolver on W0 with the generation's 16 episodes carrying (i) PHASE SWITCH - delay 0 for a random first block then delay 1 (an idle tick before the ask) for the rest, switch point drawn per generation; (ii) MOVING WINDOW - delay drawn per episode from {0, 1, 2}; (iii) ALTERNATING - delays 0, 1, 0, 1...; (iv) PRICE SWITCH - fitness = reward minus a per-instruction price that is 0 for the first half of the generations and 1/64 after; against STATIONARY-0 and STATIONARY-1; 60 generations, 2 seeds, N 96 from the walkers. Pressures only, no target mechanism. Read: tops' reward on held-out delay-0 / delay-1 / delay-2 episode sets (family index 2), the share of tops that solve BOTH delay 0 and delay 1 above floor (a switch), reward on unseen delay 2 (prediction / generalisation), persistent state words, and the full curve set of the tops; regime x readout table.",
     unchanged="evolver, grammar, VM", attacks="whether fixed temporal response gives way to switching, retained state or prediction when the world's timing relationship changes within a lifetime", nonredundant="every world so far was stationary within an evaluation", cost_minutes=10,
     continuation=["switch point as a dose", "two-phase worlds with K=2", "nonstationary transplants"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=3))

cand(id="P-H04", parent="T-X19", family="causal_transplant", axis="responsible machinery x naive host", type="minimal-causal-transplantation", deformation="C", requires=["P-G11"], co_parents=["T-X17", "T-ARCH4/M1"],
     delta="MINIMAL CAUSAL TRANSPLANTATION: for representatives of the START-ANCHORED (delay_general, competent on W1_d4) and ASK-TIME (w0_solver, competent on W0) geometries, LOCALISE the responsible machinery by per-instruction disable-to-NOP probes (which instructions' disabling destroys the geometry; which destroy reward; the HALT-probe reach map alongside) and by the smallest contiguous span covering the geometry-necessary set; then INSERT that span into NAIVE hosts (gen0_random parents, immune shelf programs, immune W2-evolver tops; at the host's start, middle and end) and read the host's curve set and its reward on the source world before and after. Success = the geometry appears in the host (distance to the source class < .2) AND the host's reward on the source world rises above the floor - competence transferred without the ancestry. Failure modes named: geometry without competence, competence without geometry, neither.",
     unchanged="constructions, VM, hosts' own genomes (the span is added)", attacks="whether a temporal geometry is a transferable computational organ or a whole-genome property", nonredundant="no machinery was ever localised or moved", cost_minutes=8,
     continuation=["span minimisation by deletion", "transplant into hosts under selection"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=3))

cand(id="P-H06", parent="T-ARCH4/M1", family="arch4", axis="reach-weighted damage x floor-conditioned promotion", type="bounded-secondary",
     delta="BOUNDED secondary lane: (a) reach-weighted scattered damage - the qualified ruler applied to REACHED instructions only vs UNREACHED only at f .10 (does loss live entirely in reached code; does the operand-slot ordering hold within reached code); (b) the P-G07 promotion rule re-evaluated on a FLOOR-CONDITIONED held-out family (programs whose held-out baseline is above the floor) - promote the slot ordering only if it holds there in every stratum.",
     unchanged="ruler, hit construction", attacks="P-G07's degenerate held-out cell and the reach x damage question", nonredundant="reach-restricted damage never applied; the rule never floor-conditioned", cost_minutes=4,
     continuation=["reach x slot x category interaction"], scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2, regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=1))

cand(id="P-H07", parent="T-X12", family="temporal_semantics", axis="resource limits as artefact", type="anti-gravity", anti_gravity=True, requires=["P-G11"],
     delta="ARE THE GEOMETRIES RESOURCE ARTEFACTS? Representatives of every geometry re-read with the manifest's tick_budget halved and doubled and its tape_words halved and doubled (within bounds; behaviour identity on the base episodes checked and recorded): if a geometry changes shape when only a resource limit changes, it is a budget / capacity artefact, not a computational organ. Curve distances and reward change per knob.",
     unchanged="genome, worlds, constructions", attacks="cycle 6's premise that the shapes are computational structure", nonredundant="resource knobs were never varied on classified programs", cost_minutes=3,
     continuation=["out_cap and n_regs (semantic knobs) separately"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2, regime_newly_reachable=1, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-H08", parent="T-X17", family="temporal_semantics", axis="heritability vs edit robustness", type="anti-gravity", anti_gravity=True, requires=["P-G11"],
     delta="IS 'HERITABLE ALONG NEUTRAL WALKS' JUST ROBUSTNESS TO A FEW EDITS? For representatives of every geometry: random UNFILTERED mutants at 4 / 8 / 16 grammar operations (no neutrality filter, 8 draws each) vs the neutral walkers at the same depths: the share that keeps the geometry (curve distance < .2) and the share that keeps reward. If unfiltered mutants keep the shape as often as neutral walkers, heritability is edit-robustness; if neutral walkers keep it more, the neutrality filter (function) is what preserves the shape.",
     unchanged="constructions, grammar", attacks="the heritability claim of P-F02", nonredundant="no unfiltered-mutant control exists", cost_minutes=4,
     continuation=["mutants under each operator separately"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2, regime_newly_reachable=1, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-H09", parent="T-X20", family="structure_census", axis="structural correlates of geometry", type="serendipity-census", serendipity=True, co_parents=["T-X19", "T-ARCH4/R1"],
     delta="STRUCTURAL CORRELATES of the six geometries (P-F02 clusters): persist policy, n_regs, tape_words, tick_budget, out_cap, code_writable, length, persistent state words, opcode-category histogram, reach share (HALT probe) - per cluster, against a permutation null over cluster labels (chi-square by simulation for categorical, rank tests for continuous). Which manifest and code features distinguish start-anchored and periodic programs from the rest?",
     unchanged="programs, clusters", attacks="nothing yet: an unexplained association hunt on two new shapes", nonredundant="no structural census of the clusters exists", cost_minutes=2,
     continuation=["the strongest correlate as a causal knob (P-H07 style)"], scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=2, regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3, null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

cand(id="P-H10", parent="T-ARCH5", family="representation", axis="grammar B neutral walks", type="serendipity-representation", serendipity=True, co_parents=["T-X17"],
     delta="REPRESENTATION CHANGE: neutral walks (depth 16, archived 4/8/16, band acceptance in the home world) under Campaign 5's grammar B (archaeon.campaign5.repb.grammar_b.mutate_b; same VM, different operator set) from representatives of every geometry; the share keeping the geometry and reward vs the grammar-v0.4 walkers. If the shapes survive a change of search representation they are properties of the program, not of the operator set; if grammar B destroys or creates shapes, the representation is a coordinate. T-ARCH5 is reactivated through this read.",
     unchanged="VM, constructions, band", attacks="representation invariance of the geometries", nonredundant="grammar B was never applied to classified programs", cost_minutes=4,
     continuation=["evolution under grammar B in nonstationary worlds"], scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))


def main():
    existing = set()
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
            c["batch"] = "H"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
        fh.write(json.dumps({"id": "P-G11", "amend": True, "recorded": ts, "deformation": "R",
                             "delta_addendum": "CYCLE 6 (runs FIRST): rulers {self-displacement, reward change vs expected, answered-share change, normalised output-word distance} x doses 1-4 x sampling conventions {episode family index 1 (CRN), index 2, E 32} x placements (the 7 positions) on parents, walkers, C4-08 tops and P-F02's cluster representatives; the full curves under every ruler kept; cluster assignment (nearest P-F02 centroid) per ruler / convention and their agreement; the manifold SURVIVES if assignments agree above the permutation band under every ruler and convention, BREAKS where they do not (recorded precisely)",
                             "scores": dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2)}, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(OUT)
    print("appended", added, "+ P-G11 amended")


if __name__ == "__main__":
    main()
