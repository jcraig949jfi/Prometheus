"""Candidate perturbations, batch B: parents e01-e04, their anomalies, and cross-trajectory transplants.
Scores are opportunity judgements recorded at reconcile time (0-3 per criterion); idempotent by id."""
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


cand(id="P-B01", parent="T-E01", family="retention_economics", type="preregistered-unrun-intervention",
     delta="I2 SCRAMBLE on e01's evolved treatment population: permute the region's cell contents between steps at zero extra cost, vs the cost-matched sham and I1 ERASE, over the same 32 matched streams",
     unchanged="world, economics, evolved populations (re-evolved from attempt seeds), I1 and sham, the paired Delta ruler",
     attacks="e01's own gap: I2 'would separate HAVING state from FINDING it, which this attempt cannot'",
     why_now="preregistered, never run, one minute of compute; separates two mechanisms inside a COMPLETE result",
     cost_minutes=2,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=1, independent_intersection=0,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=0, underexplored_hard_to_operationalise=0))

cand(id="P-B02", parent="T-X10", family="retention_economics", type="exploratory-map",
     delta="2-D sweep of e01's conditionality: recurrence in {0, 0.15, 0.35, 0.6} x hold price in {0.1, 0.5, 0.85, 1.2}, 2 seeds each; map evolved p_write / persist_steps and the erase-vs-sham dependence across the grid",
     unchanged="organism, search, episode structure, rulers",
     attacks="the free-lunch finding (retention paid at every price) and the zero-recurrence control that evolved away: WHERE does retention stop paying, and does evolution track the h~0.85 crossover?",
     why_now="declared expansion, 32 runs at 7.6 s each",
     cost_minutes=5,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=2, independent_intersection=0,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=0, underexplored_hard_to_operationalise=1))

cand(id="P-B03", parent="T-E07", family="robustness", type="transplant-break-inconclusive",
     delta="e07's damage family transplanted into e01's world, the one where state use DID evolve: between steps delete a uniform random fraction f of the organism's region cells (representation-blind selector, bit-identical sham); arms STATIC vs WEATHER (damage during evolution, f drawn from {0.1,0.2,0.3}) vs SHAMWEATHER; after evolution assay all arms under the same damage on matched streams; rulers rho0 and AURC of info/cost normalised by own intact value; 6 lineages per arm, exact relabelling",
     unchanged="e01 economics, 5-gene organism, episode structure, e07's damage/sham/ruler definitions, lineage as unit",
     attacks="e07's D059 boundary (state use never evolved) by moving the weather question to a substrate where retention is already selected; and e01's I4 destroy-selected gap",
     why_now="both modules exist; the question e07 could not pose is posable here in minutes",
     cost_minutes=6,
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=1, independent_intersection=3,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

cand(id="P-B04", parent="T-X09", family="ratchet", type="break-null-changed-economics",
     delta="e02 with T2 REFUSED unless the payload is normalised (impossible, not expensive, without T1); K1 revert-A actually executed; selection weakened per D028 (elite_fraction 0.5, sigma 0.06); gene fixation order + K1 loss as rulers; 4 replicates",
     unchanged="world otherwise, 9-gene organism, T1/T3/T4 economics, detector calibration procedure",
     attacks="the stated design consequence of e02's NULL; the valley (NORM_ONLY -20.5%) and the never-run knockout",
     why_now="e02 said exactly what a new preregistration must change; 30 s per replicate",
     cost_minutes=3,
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=0,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=3, inconclusive_now_posable=0, underexplored_hard_to_operationalise=0))

cand(id="P-B05", parent="T-E02", family="ratchet", type="serendipity", serendipity=True,
     delta="e02's world under e07's weather: a uniform random fraction of T4-bound region cells deleted between steps during evolution (sham arm matched); does damage change WHICH gene fixes first (foundation-first under weather?) and the neutral-gene drift?",
     unchanged="e02 economics, organism, selection, fixation-order ruler",
     attacks="cross: whether environmental disruption is the missing pressure that makes a foundation load-bearing",
     why_now="both modules exist; never considered together",
     cost_minutes=3,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=1, unexplained_structure=1, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=3, mechanism_discrimination=1, cost_now_lower=3,
                 null_becomes_contrast=2, inconclusive_now_posable=0, underexplored_hard_to_operationalise=1))

cand(id="P-B06", parent="T-E03", family="coalitions", type="preregistered-unrun-intervention",
     delta="I3 KNOCKOUT-USED vs KNOCKOUT-RANDOM and I4 TRANSPLANT (same costs, different hidden structure) on e03's evolved treatment populations, 4 replicates, with e04-style sham-vs-sham noise floors over seed blocks",
     unchanged="world, organism, evolved populations, MI ruler",
     attacks="'coalition is knowledge or habit' - the two interventions the preregistration named as distinguishing a result from a story",
     why_now="preregistered, never run; a COMPLETE result whose causal layer was skipped",
     cost_minutes=3,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=1, independent_intersection=0,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=0, underexplored_hard_to_operationalise=0))

cand(id="P-B07", parent="T-E03", family="coalitions", type="serendipity", serendipity=True,
     delta="e08's representational tax laid over e03's activation policy: sel = score - lambda * (number of non-zero weights, |w| > 0.05) with lambda calibrated from the measured headroom; does burden pressure change coalition conditionality (MI excess) at matched score, or only sparsity?",
     unchanged="e03 world, organism, MI ruler, I1 sham",
     attacks="cross: e03 measured sparsity and conditionality separately; e08 measured burden; whether representational burden and behavioural sparsity trade off",
     why_now="both modules exist",
     cost_minutes=4,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=1, unexplained_structure=1, independent_intersection=3,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=0, underexplored_hard_to_operationalise=1))

cand(id="P-B08", parent="T-E04", family="triage", type="break-inconclusive-powered",
     delta="J1 re-posed under the campaign's eligibility rule: a disjoint 4-replicate pilot estimates the rate at which J1 clears the sham-vs-sham floor; production replicate count and minimum clearing count frozen from that rate with margin; then 12 fresh replicates; J2/J4 cost-matched shams added for the generality shocks",
     unchanged="world, organism, MI and J1 rulers, sham construction",
     attacks="the 3/4 failure that was a power failure, not a world failure",
     why_now="D066 gave the rule; 55 s per 4 replicates",
     cost_minutes=6,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=1, independent_intersection=1,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=2, mechanism_discrimination=1, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=3, underexplored_hard_to_operationalise=0))

cand(id="P-B09", parent="T-X08", family="triage", type="exploratory", anti_gravity=True,
     delta="evolve e04 under a TTL DISTRIBUTION (per episode ttl in {7, 15, 30}) vs fixed ttl 15; test both across ttl 7/15/30 with cost-matched sham shocks; is the inverted generality a schedule specialisation that a fluctuating schedule removes?",
     unchanged="world otherwise, organism, MI ruler",
     attacks="the unexplained 'improves under less pressure' phenotype; e07's schedule-generalisation framing applied to e04",
     why_now="e07 preregistered exactly this contrast but could not run it; here the organism evolves in seconds",
     cost_minutes=5,
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

cand(id="P-B10", parent="T-X11", family="coalitions", type="exploratory", anti_gravity=True,
     delta="feature_overlap sweep {0.1, 0.2, 0.35, 0.5} x generations {60, 240} on e03 with a hand-built Bayes-optimal router as the ceiling per overlap; is the precision plateau a world ceiling or a search limit?",
     unchanged="organism, economics, MI ruler",
     attacks="the unexplained 0.58-0.63 routing precision plateau",
     why_now="a residual nobody named; seconds per run",
     cost_minutes=5,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=0,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=0, underexplored_hard_to_operationalise=2))

cand(id="P-B11", parent="T-E02", family="ratchet", type="preregistered-unrun-intervention",
     delta="K1 revert-A executed on e02's evolved populations as recorded (no economics change): revert p_norm to ancestor in evolved genomes and measure the loss vs the gain p_norm gave when it arrived; plus the control arms control_no_T1/no_T2/no_T4 actually evolved",
     unchanged="everything in e02",
     attacks="D024: a conclusion was drawn about a knockout that never ran; the controls were never evolved",
     why_now="cheap; a NULL whose knockout layer is missing",
     cost_minutes=2,
     scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=1, independent_intersection=0,
                 regime_newly_reachable=1, information_gain=1, delta_novelty=1, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=0, underexplored_hard_to_operationalise=0))


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
            c["batch"] = "B"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
    RS.require_ascii_safe(OUT)
    print("appended", added)


if __name__ == "__main__":
    main()
