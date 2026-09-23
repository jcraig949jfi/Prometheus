"""Candidate perturbations, batch D (cycle 2): descendants of cycle-1 and ARCH4 material results.
Each carries a CONTINUATION manifold (the neighbouring dimensions swept if the first evaluation is
material) and, where it descends from a new deformation, a `deformation` tag A/B/C. Scores are
opportunity judgements (0-3) recorded before any run. Computational scope for the ARCH4 items:
integer programs on a bounded VM; nothing biological."""
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


cand(id="P-D01", parent="T-ARCH4/M1", family="arch4", axis="damage_geometry", type="parameterized-dose-surface", deformation="A",
     delta="LOCALITY DOSE SURFACE runner: damage of k instructions (k in 2,4,8) spread over s sites (1,2,4,8; s <= k; sites as equal windows) with spacing {adjacent, max-spread}, kind {delete, opcode-perturb, operand-perturb, move-without-deletion (window rotation)}, decode {modulo, trap-NOP}, on three genotype sets (viable parents, walker-16 descendants, C4-08 ordinary top-32) scored on the parent environment and on the held-out world W2_K2d1; per cell loss, displacement, D-classes; a per-parent regression of loss on log(sites), log(k), kind, spacing, decode",
     unchanged="classification constants, environments' episodes (CRN), programs' behaviour",
     attacks="what quantity controls damage: site count, spacing, word kind, instruction role, or something not represented (P-C04, P-C15 saw only two points)",
     nonredundant="a surface, not another binary comparison", cost_minutes=8,
     continuation=["window width 1/2/4/8", "spacing as a continuous gap", "instruction role (opcode category hit)", "pairwise epistasis of two sites", "other held-out families", "C5 representation B programs"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-D02", parent="T-ARCH4/W1", family="arch4", axis="world_geometry", type="parameterized-switch-probe", deformation="B",
     delta="DELAY SWITCH runner: walker-16 descendants of w0_solver parents, delay_general parents, and C4-08 ordinary tops exposed to a grid: deterministic delay 0/1/2/4; stochastic per-tag delay sets (0,1) / rare (0,0,0,1) / heterogeneous (1,2,3,4); ask_timing interleaved (delay attached to a different computational event); random interleave; noise .10 with delay 0 and 1; per cell displacement vs the original program and reward; plus a per-step trace of W1_d1 displacement along each walk to locate the accepted step at which drift becomes loud and its operator / region / ref_broken",
     unchanged="walk seeds and rules, displacement ruler", attacks="the zero-vs-nonzero delay discontinuity (P-C14): is delay causal, or does any nonzero delay expose a hidden state transition?",
     nonredundant="stochastic, rare, heterogeneous and event-shifted delays were never tried", cost_minutes=6,
     continuation=["revert-and-replay ablation of the loud step", "delay on PUT vs ASK", "longer episodes", "noisy + delayed combined dose", "C5 representation B walkers"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=0, underexplored_hard_to_operationalise=3))

cand(id="P-D03", parent="T-ARCH4/M1", family="arch4", axis="search_dynamics", type="parameterized-mechanism-break", deformation="C",
     delta="ACCEPTANCE-FILTER runner: neutral walks (depth 16, 2 walkers, viable parents) over a grid: acceptance rule {original band; reject length-increasing neutral moves; length-normalised band (band * len0/len); explicit length cost (accept iff |r - r0| <= band AND len <= len0 + 1); symmetrised survivability (a deletion proposal is retried up to 4 times before counting)} x trap semantics {modulo, nop, halt} x proposal distribution {frozen, length-balanced, deletion-heavy (deletion+splice mass x3)}; per cell length delta, acceptance, exaptation, structural diversity; does growth disappear, reverse, relocate (to duplication? to config?) or turn into another accumulation",
     unchanged="parents' behaviour, seeds, environments, band width", attacks="the acceptance-filter mechanism for length growth (P-C16)",
     nonredundant="the mechanism is stated and each cell removes one of its supports", cost_minutes=8,
     continuation=["band width", "depth 32/64 under the winning rule", "explicit per-instruction cost lambda sweep", "C5 representation B"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-D05", parent="T-E06", family="representation_ecology", axis="search_regime", type="replication-confirmatory",
     delta="P-A07's mutual invasibility at recombination rate 1.0 replicated across 6 attempt ids x geometry {operation-graph, legacy tree} x rate {0.5, 1.0}: count of (id, geometry) cells with mutual invasibility per rate; exact relabelling over rate labels",
     unchanged="e06 world, sharing, prices, tournament, invasion protocol", attacks="one attempt id, one target: is the recombination-1.0 mutual invasibility robust?",
     nonredundant="replication IS the question here", cost_minutes=5,
     continuation=["rate 0.75/0.9", "n_org 48/192", "coexistence run (80 gens mixed) at the winning rate"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=1, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=3, underexplored_hard_to_operationalise=0))

cand(id="P-D06", parent="T-X04", family="representation_ecology", axis="world_geometry", type="exploratory-map",
     delta="founder-control separatrix at phi 0.5: mixed populations seeded at TREE frequency {.1,.2,...,.9}, evolved 40 generations (recombination 0.5 as e06 and 1.0), 2 seeds each; final TREE frequency vs seeded frequency; locate the unstable equilibrium",
     unchanged="e06 world, sharing, prices, tournament", attacks="the bistable regime found at phi 0.5/0.75 (P-A08)",
     nonredundant="the separatrix was never located", cost_minutes=4,
     continuation=["phi 0.75", "recombination 1.0 x phi", "population size"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=1,
                 regime_newly_reachable=3, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

cand(id="P-D07", parent="T-E07", family="robustness", axis="damage_severity", type="reposed-confirmatory",
     delta="P-B03 re-posed in e01's world with the ABSOLUTE retained score above floor (S_dmg - F) as the ruler beside the ratio, a severity dose at test {.1,.2,.3,.45}, 8 lineages per arm (STATIC/WEATHER/SHAMWEATHER), exact relabelling on the absolute measure at each severity",
     unchanged="e01 economics and organism, e07 damage family and sham, lineage as unit", attacks="D071 (ill-conditioned ratio) and the dose dependence of the weather effect",
     nonredundant="the ruler and the dose are new; the world and arms are not", cost_minutes=6,
     continuation=["training severity sweep", "I2-style scramble instead of deletion", "damage timing relative to recurrence"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=3, underexplored_hard_to_operationalise=0))

cand(id="P-D08", parent="T-X05", family="burden_economics", axis="mechanism", type="fossil-ablation",
     delta="e08 fossils (256 representatives): for each, (i) rank profile SCRAMBLED at identical total bond width (cores re-drawn at the substrate's init), (ii) read mask scrambled at identical bit count, (iii) both; held64 of original vs each ablation, per arm; is the low-burden/high-capability association carried by WHICH bonds are wide or only by size?",
     unchanged="fossil genomes, world, assay seeds, burden accounting", attacks="the 2-3x burden drop at unchanged capability (T-X05) - organisation or size",
     nonredundant="fossils exist and were forbidden to inspect pre-verdict", cost_minutes=3,
     continuation=["partial scrambles (one bond at a time)", "cross-arm transplant of rank profiles"],
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-D11", parent="T-X01", family="population_genetics", axis="population_structure x search_regime", type="cross-material",
     delta="e06's mixed ecology (TREE vs TAPE) under tournament size 2 (the structure that halved the hitchhiking rate in P-A10) crossed with recombination 1.0 (the rate that gave mutual invasibility in P-A07): 80-generation mixed runs seeded at .5, 4 attempt ids; coexistence at 80 generations, growth advantage, lineage survival",
     unchanged="e06 world, sharing, prices", attacks="whether two material single-axis results compose into coexistence (e06's original question)",
     nonredundant="cross of two independent material findings", cost_minutes=5,
     continuation=["tournament 1", "rate 0.75", "seeded frequencies grid"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=3,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

cand(id="P-D12", parent="T-X05", family="burden_economics", axis="pressure_schedule", type="exploratory-dose", anti_gravity=True,
     delta="amputation ALONE (no tax) at intervals g_amp 2/5/10/20 vs none, 4 lineages each, 200 generations on w13; held64 of the top-8 (train-selected) and burden; does structural pressure alone raise held-out capability (TAX+AMP had the highest held64 in e08)?",
     unchanged="e08 organism, world, selection, assay", attacks="an unexplained association (lowest burden, highest held64) that no rule named",
     nonredundant="amputation interval was never varied; tax removed", cost_minutes=8,
     continuation=["amputation severity (slices per event)", "amputation on the read mask", "held-out selection"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=2,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

cand(id="P-D13", parent="T-E06", family="representation_ecology", axis="damage x representation", type="serendipity", serendipity=True,
     delta="e07's blind deletion family inside e06's ecology: between generations delete a random fraction f=.1 of instructions/nodes from every TAPE and TREE body (blind to content), sham arm matched; does damage change invasion (TREE's subtree structure vs TAPE's register plumbing under blind loss)?",
     unchanged="e06 world, sharing, prices, tournament, recombination 0.5", attacks="cross: representation ecology under representation-blind damage",
     nonredundant="two trajectories that never met", cost_minutes=4,
     continuation=["f dose", "damage only one substrate", "damage timing"],
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=2, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-D14", parent="T-ARCH4/W1", family="arch4", axis="world x cw01-cross", type="serendipity", serendipity=True,
     delta="Campaign 4's walker programs scored under a CW01-style held-out SELECTION rule: choose each parent's best walker by reward on W2_K2d1 (held-out) instead of by the parent environment, then measure exaptation on the remaining held-out worlds; does held-out selection of neutral variants find exaptation the band-walk archive hides?",
     unchanged="walkers, D6 rule", attacks="cross: e08's eligibility surface (train vs held-out selection) applied to C4's neutral archive",
     nonredundant="a selection rule from another trajectory", cost_minutes=3,
     continuation=["selection on each held-out world in turn", "top-k instead of best"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=1, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=1, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))


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
            c["batch"] = "D"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
    RS.require_ascii_safe(OUT)
    print("appended", added)


if __name__ == "__main__":
    main()
