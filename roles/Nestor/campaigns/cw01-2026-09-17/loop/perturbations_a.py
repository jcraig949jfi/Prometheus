"""Candidate perturbations, batch A: parents already in the pool (e05-e09 and cross-cutting).

Each candidate carries: parent, family, type, delta (what changes), unchanged (what does not),
attacks (which failure surface or uncertainty), why_now, cost, and explicit 0-3 scores per
criterion (see prioritize.py CRITERIA) so the ranking is auditable. Scores are opportunity
judgements made at reconcile time, before any of these runs; they are recorded, not tuned.
Idempotent by id.
"""
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


cand(id="P-A01", parent="T-E08", family="burden_economics", type="break-inconclusive",
     delta="representatives chosen on a DISJOINT held-out selection seed set (30100..30115) instead of train8; minimum competent count derived from the pilot's competent-lineage RATE with margin; lambda unchanged",
     unchanged="world w13, organism, arms, tax coefficient 390, amputation schedule, assay seeds 30000..30063, statistic, randomisation",
     attacks="D066 eligibility surface (train8 selection picks representatives that do not generalise)",
     why_now="the exact failure is known and cheap to remove; 256 fossils and the full pipeline exist; 12 min compute",
     cost_minutes=14,
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=1,
                 regime_newly_reachable=1, information_gain=3, delta_novelty=2, mechanism_discrimination=1, cost_now_lower=2,
                 null_becomes_contrast=0, inconclusive_now_posable=3, underexplored_hard_to_operationalise=0))

cand(id="P-A02", parent="T-X05", family="burden_economics", type="exploratory-mechanism",
     delta="fossil ablation: for each of the 256 e08 representatives, replace the evolved rank profile by a RANDOM profile of identical total bond width (cores re-drawn at the substrate's init), and separately keep ranks but scramble the read mask at equal bit count; assay held64",
     unchanged="fossil genomes, world, assay seeds, burden accounting",
     attacks="whether the 2-3x burden drop is an organisation (which bonds are wide) or only a size; whether low-burden = higher held64 is causal or a selection artefact",
     why_now="the fossils exist and were forbidden to inspect pre-verdict; 2 min compute",
     cost_minutes=3,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-A03", parent="T-E08", family="burden_economics", type="pressure-change",
     delta="lambda 390 -> 48.75 (0.25 x lambda_max, the lowest fraction the Q3 sweep qualified with a gradient of -0.9); everything else as e08",
     unchanged="world, organism, arms, schedule, assay, statistic",
     attacks="D064: the 'largest qualifying' rule froze the harshest tax; is the burden drop pressure-dose dependent?",
     why_now="the attainability curve exists; the only change is one coefficient",
     cost_minutes=12,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=1, independent_intersection=0,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=1, mechanism_discrimination=2, cost_now_lower=2,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=0))

cand(id="P-A04", parent="T-X02", family="substrate_screen", type="search-boundary",
     delta="TT lineages on w13 selected on 8 vs 32 vs 128 train seeds (CONTROL arm only, 4 lineages each); measure the held64 competence rate and its dependence on training breadth",
     unchanged="organism (rank 3 fixed, no tax), world, assay",
     attacks="the assumption behind e08 and e09 that train8 fitness tracks held64 capability (D065, D069)",
     why_now="three organism families now show the decoupling; it gates every future w13 experiment; 10 min",
     cost_minutes=10, anti_gravity=True,
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=3,
                 regime_newly_reachable=1, information_gain=3, delta_novelty=2, mechanism_discrimination=1, cost_now_lower=2,
                 null_becomes_contrast=0, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

cand(id="P-A05", parent="T-X03", family="composition_economics", type="confirmatory-new",
     delta="pre-run composability predictor: draw 48 fresh e05 worlds, compute two candidate predictors from the capability pool alone (coverage overlap; conjunctive-demand spread), preregister a split rule on the 12 existing worlds, then score prediction of superadditivity-clears-null on the 48",
     unchanged="world_e05 generator, contract statistic, null construction",
     attacks="e05's open question whether a world's composability is knowable before evolution; sa==load-bearing 12/12",
     why_now="12 labelled worlds exist as a training set that was never used; seconds per world",
     cost_minutes=8,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=1,
                 regime_newly_reachable=1, information_gain=3, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=2, inconclusive_now_posable=0, underexplored_hard_to_operationalise=1))

cand(id="P-A06", parent="T-E05", family="composition_economics", type="exploratory",
     delta="conjunctive_fraction sweep (declared in e05 WORLD.json, never run) over 5 values x 6 worlds each; composability rate per value",
     unchanged="e05 organism, statistic, null",
     attacks="e05's stated limitation; whether the 7/12 rate is a property of one economics setting",
     why_now="declared and cheap",
     cost_minutes=10,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=1, independent_intersection=0,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=1, mechanism_discrimination=1, cost_now_lower=2,
                 null_becomes_contrast=1, inconclusive_now_posable=0, underexplored_hard_to_operationalise=0))

cand(id="P-A07", parent="T-E06", family="representation_ecology", type="search-boundary",
     delta="variation regime swap holding world and price list fixed: (i) mutation-only, (ii) crossover-heavy (recombination rate x4) for both substrates; measure invasion when rare against evolved residents (the corrected Q16 P3)",
     unchanged="operation-graph generator, sharing, price list, selection",
     attacks="D055: TREE's only plausible advantage is dynamic (subtree crossover) - never given the chance to matter",
     why_now="e07 showed representation change alone did nothing there; the search regime is the untested axis here",
     cost_minutes=8,
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=1, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2,
                 null_becomes_contrast=0, inconclusive_now_posable=2, underexplored_hard_to_operationalise=1))

cand(id="P-A08", parent="T-X04", family="representation_ecology", type="exploratory", anti_gravity=True,
     delta="interpolate target geometry: mix legacy tree-native and operation-graph targets at fractions 0, 0.25, 0.5, 0.75, 1 of items; measure invasion in both directions per fraction and locate any crossing",
     unchanged="both substrates, sharing, price list, selection",
     attacks="the anomaly that a substrate-neutral generator produced the OPPOSITE asymmetry rather than neutrality",
     why_now="both generators exist in world_e06.py; the crossing, if any, is where e06's question becomes posable",
     cost_minutes=10,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=0,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=2,
                 null_becomes_contrast=0, inconclusive_now_posable=3, underexplored_hard_to_operationalise=2))

cand(id="P-A09", parent="T-E07", family="robustness", type="reposed-confirmatory",
     delta="one-gene persistence parametrisation: per cell a_i in [0,1] with input gain tied to (1 - a_i) so the accumulator ridge is a one-gene move; P1 magnitude placed on rho0 with the attainability curve on record; otherwise e07's frozen design",
     unchanged="task, damage family, sham, three arms, AURC/rho0 rulers, relabelling null",
     attacks="D059 (search cannot reach state use) and D058 (P1 unattainable) at once",
     why_now="both defects have a mechanical remedy that does not touch the science",
     cost_minutes=10,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=1, independent_intersection=1,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=1, cost_now_lower=1,
                 null_becomes_contrast=0, inconclusive_now_posable=3, underexplored_hard_to_operationalise=0))

cand(id="P-A10", parent="T-X01", family="population_genetics", type="exploratory", anti_gravity=True,
     delta="neutral fixation time vs population structure in e06's world: elitist tournament (as run) vs no-elitism tournament vs island model (4 demes, migration 1/gen); labels only, one substrate (control A)",
     unchanged="world, substrate, mutation",
     attacks="the unexplained 26-vs-96-generation hitchhiking floor seen in two worlds",
     why_now="lineage.py has the rulers; the effect corrupts every ecological noise floor in the campaign",
     cost_minutes=8,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=2,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

cand(id="P-A11", parent="T-X07", family="composition", type="serendipity", serendipity=True, anti_gravity=True,
     delta="the e09 chain organism (4 digit args, 3 ops) transplanted onto a campaign toy task with held-out draws (e07's accumulate-and-report task, digits of the observation); single-op ceiling vs 3-op chains vs scrambled ops on held-out lifetimes",
     unchanged="chain representation, op tables, GA",
     attacks="e09's boundary: was it the substrate (w13 does not generalise) or the idea (composition does not help)?",
     why_now="both pieces of code exist; 5 min",
     cost_minutes=6,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=1, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=2,
                 null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

cand(id="P-A12", parent="T-E08", family="burden_economics", type="serendipity", serendipity=True,
     delta="e08's tax and amputation applied to e07's linear recurrent organism (memory cells as the burden coordinate: number of cells with non-zero input drive, spectral radius bins); does burden pressure change how much STATE an organism keeps, in the world where state use was hard to evolve?",
     unchanged="e07 task and organism; e08 tax form sel = fit - lambda*scalar(B)",
     attacks="cross: does a burden tax push AWAY from state use (making e07's D059 worse) or prune unused cells only?",
     why_now="both modules exist; the intersection was never considered",
     cost_minutes=8,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=1, unexplained_structure=1, independent_intersection=3,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=3, mechanism_discrimination=1, cost_now_lower=2,
                 null_becomes_contrast=0, inconclusive_now_posable=0, underexplored_hard_to_operationalise=1))


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
            c["batch"] = "A"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
    RS.require_ascii_safe(OUT)
    print("appended", added)


if __name__ == "__main__":
    main()
