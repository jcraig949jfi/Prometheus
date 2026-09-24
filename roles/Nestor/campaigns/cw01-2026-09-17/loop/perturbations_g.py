"""Candidate perturbations, batch G (cycle 5): rulers, interventions and price functions treated as
candidate mechanisms. Priorities: qualify a dilution-neutral scattered damage ruler; re-read the
fixed-count claims; graded persistence without function destruction; price dose x damage x load;
neutral transplant; the response-geometry census; the operand-slot lane; and four candidates that
attack cycle 5's own assumptions. Scores are opportunity judgements (0-3) recorded before any run.
Computational scope: integer programs on a bounded VM and tree/tape genomes in software worlds."""
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


PROV = "ruler provenance recorded in PREREG: intervention family, geometry, sampling law, normalisation, denominator, price assumptions, viability floor, baseline-function check, qualification evidence"

cand(id="P-G01", parent="T-R01", family="ruler", axis="damage ruler qualification", type="instrument-qualification", deformation="R",
     delta="SCATTERED DAMAGE OPERATOR: each eligible instruction is independently deleted (or disabled to NOP) with probability f; telemetry per draw: n_eligible, n_hit, fraction_hit, executable hits (HALT-probe reach map), persistent-state hits (read_write / indirection category), category distribution of hits, jump-topology effect (reference facts). QUALIFICATION before any scientific use: (1) hit counts over 2000 draws vs Binomial(n, f) (chi-square by simulation); (2) positions not clustered (gap-variance vs the uniform expectation, permutation band); (3) fraction hit independent of program length (slope of fraction_hit on n inside its permutation band); (4) equal seeds reproduce exact masks; (5) a SHAM path draws the mask, applies nothing, and goes through the same evaluation route: displacement 0 and reward identical on every program. Any failure -> INSTRUMENT_FAILURE and the rereads stop.",
     unchanged="programs, worlds, classification constants", attacks="the assumption that a measurement is causally neutral (D084, D085, D086)", nonredundant="no damage ruler in the campaign was ever qualified", cost_minutes=4,
     continuation=["disable vs delete as a geometry axis", "reached-only eligibility"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

cand(id="P-G02", parent="T-ARCH4/M1", family="arch4", axis="reread of fixed-count claims", type="ruler-reread", deformation="A", requires=["P-G01"],
     delta="RE-READ with the qualified scattered ruler (f .05 / .10 / .20, delete and operand-scatter, 4 draws, %s): (a) P-D01 - does loss still fall with log length; are operand hits softer than deletions at equal f; are C4-08 tops more robust than parents and walkers at equal f; (b) P-E05 - the depth-16 vs depth-64 finals of orig|frozen and no_growth|frozen walks (regenerated, deterministic): does loss fall with depth under the original rule and rise under no_growth; (c) P-F06 - the seed 1-6 select / ndrift populations regenerated at G60: do selected tops lose less than their ancestors and than the competent drift control, and does the effect survive length conditioning. Each claim returns SURVIVES_RULER_CHANGE / SHRINKS / REVERSES / DISAPPEARS / UNRESOLVED with the old and new numbers side by side." % PROV,
     unchanged="programs, walks, populations (regenerated from their seeds), worlds", attacks="which of the cycle 2-4 damage coordinates were program properties and which were ruler geometry", nonredundant="the claims were never read on a dilution-neutral ruler", cost_minutes=10,
     continuation=["reread P-C04 / P-C15 (locality law)", "reread P-E09 weather"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

cand(id="P-G03", parent="T-X15", family="carried_state", axis="graded persistence x function window", type="causal-separation", requires=["P-G01"],
     delta="GRADED PERSISTENCE without function destruction: at every tick boundary the persist policy is applied with probability q (else the state is cleared as persist=none would), q in {1, .75, .5, .25, 0}, with the clearing pattern drawn from a seed shared by baseline and damaged evaluations (CRN). Function window: a dose is ELIGIBLE for a program only if its reward stays within the equivalence band of q=1 and above the floor. Then scattered deletion (f .10, 4 draws) at every eligible dose, loss against that dose's own baseline. Readings: STATE_CAUSAL (loss changes with q outside its paired band among programs with >= 2 eligible doses), STATE_CORRELATED (persistent words correlate with loss across programs but q does not move it), STATE_ENTANGLED_WITH_FUNCTION (no program keeps function below q=1), NO_RESIDUAL_STATE_EFFECT. %s" % PROV,
     unchanged="programs, worlds, the scattered ruler", attacks="whether carried state contributes independently once the dilution artefact is removed (D085 made persist=none uninterpretable)", nonredundant="no graded persistence intervention exists", cost_minutes=6,
     continuation=["subset persistence (registers only / tape only)", "bounded persistence duration"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=3, underexplored_hard_to_operationalise=2))

cand(id="P-G04", parent="T-X16", family="representation_ecology", axis="price dose x damage x load over generations", type="parameterized-dose", co_parents=["T-X18", "T-E06"],
     delta="PRICE DOSE {0, .0025, .005, .01, .02} x damage {none, tape, tree, both} (f .1, separate rng) x rate {.6, 1.0} x 3 ids, 160 generations. Per generation and label: structural units (structural load), a DELETERIOUS-LOAD probe (16 sampled bodies: absolute score change under deletion of ONE unit on that generation's items; mean and share positive), reward (raw score), share, lineages; at the end coexistence / extinction. Read: does deletion's benefit grow with accumulated load, track price, depend on representation, vanish near the score ceiling; the pruning signature (tree-damaged minus tape-damaged final share) as a function of price. Absolute ruler throughout (D086). %s" % PROV,
     unchanged="e06 world otherwise, sharing, item streams, mutation", attacks="T-X16's price-mediation as a dose-response and T-X18's load as a generation-tracked quantity", nonredundant="only price 0 vs .01 exists; load was never tracked", cost_minutes=8,
     continuation=["sharing off", "damage geometry (one unit vs fraction)"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=1))

cand(id="P-G05", parent="T-X17", family="temporal_semantics", axis="neutral transplant", type="transplant-without-selection", deformation="B",
     delta="NEUTRAL TRANSPLANT: lineages of distinct temporal classes (W0-plain tops: ask-time bound; W0-idle tops: immune; C4-08 tops: input-schedule bound; W2 evolver tops: immune; 16 programs each from P-F03's tops.json and C4-08) moved into the alternate world under NO selection: a neutral-band walk in the host world (C4-05 rules, depth 16, archived 0/4/8/16) so adaptive change is prevented during the diagnostic interval; the raw 7-vector at each archive; distance to the origin-lineage centroid and to the host-native centroid. Then, separately, selection: the C4-08 schedule-bound lineage under idle-tick selection in W2 (40 gens, 2 seeds) and under plain W0 selection (20 gens). Return TRAVELS_WITH_ORGANISM / CONTEXT_REMAPS_IMMEDIATELY / DECAYS_WITHOUT_SELECTION / REBUILT_BY_SELECTION / MIXED per lineage.",
     unchanged="constructions, walk rules, evolver", attacks="P-F03's conflation of 'travels' with 'not yet re-selected'", nonredundant="no transplant without selection exists", cost_minutes=8,
     continuation=["longer neutral windows", "transplant of damaged programs"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

cand(id="P-G07", parent="T-ARCH4/M1", family="arch4", axis="operand slot x category x reach", type="deformation-lane", deformation="O",
     delta="OPERAND SLOT / OPCODE CATEGORY lane: (1) transfer across lineages - the slot ordering (a > b > c) and the category ordering per stratum (parents, walkers, C4-08 tops) with Wilson bands; (2) HALT-PROBE REACH MAP - every instruction's opcode replaced by HALT in turn; reached = the program's answers change; then the halt_yield category's low loss split by reached / unreached, and every category's loss conditioned on reach; (3) additivity under held-out families - loss on W1_d1 and W2_K2d1 (reward below floor) by slot x category, interaction term against a permutation band. Promotion of a grammar-level mechanism only if the ordering survives the held-out families.",
     unchanged="programs, hit construction (k=2 adjacent), episodes", attacks="whether P-E04's slot / category coordinate is semantic or a reachability artefact", nonredundant="reach was never measured; transfer never split by stratum", cost_minutes=6,
     continuation=["reach-weighted damage dose", "slot map under trap-NOP"], scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2, regime_newly_reachable=2, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

# ---------------------------------------------------------------- anti-gravity: attacks on cycle 5's own assumptions
cand(id="P-G08", parent="T-R01", family="ruler", axis="scattered geometry variants", type="ruler-deformation", anti_gravity=True, requires=["P-G01"],
     delta="DOES THE SCATTERED RULER HAVE ITS OWN GEOMETRY? The same programs under five rulers at f .10: (i) scattered Bernoulli delete; (ii) scattered EXACT count round(f n) without replacement; (iii) contiguous window of round(f n); (iv) scattered restricted to REACHED instructions (HALT-probe map); (v) scattered DISABLE (opcode := NOP; length and jump topology preserved). For each: the log-length coefficient of loss, the set effect (tops vs parents), and the operand/delete ratio. If the conclusions differ across (i), (ii), (iv), (v), 'dilution-neutral' is one geometry among several and the coordinate is RULER_DEPENDENT.",
     unchanged="programs, worlds, f", attacks="cycle 5's own premise that scattered Bernoulli damage is neutral", nonredundant="the ruler variants were never compared", cost_minutes=5,
     continuation=["f dose per ruler"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

cand(id="P-G09", parent="T-X18", family="representation_ecology", axis="load: organism vs population", type="serendipity-cross", serendipity=True, anti_gravity=True, co_parents=["T-X01", "T-E06"],
     delta="IS DELETERIOUS LOAD AN ORGANISM PROPERTY OR A POPULATION ARTEFACT? In e06 solo arms (rates .5 / 1.0, 3 ids, 80 gens, sharing on and OFF): absolute score change under one-unit blind deletion for the ELITE (top 5 percent by fitness), the population mean and random members, at generations 0 / 20 / 40 / 80. If the elite shows no gain while the population does, the load lives in non-elite members (mutation-selection balance under weak selection, T-X01's floor); if the elite gains too, evolved individuals themselves carry harmful structure.",
     unchanged="e06 world, prices", attacks="T-X18 as an organism-level claim", nonredundant="load was read on whole populations only", cost_minutes=4,
     continuation=["load vs recombination rate", "load after price 0"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-G10", parent="T-X16", family="representation_ecology", axis="price decomposition", type="economics-deformation", anti_gravity=True,
     delta="DOES 'PRICE-MEDIATED' HIDE A RESOURCE-ACCOUNTING EFFECT? The price decomposed: {none, units only (.01), registers only (.01), both} x damage {none, tape, tree} x rate .6 x 3 ids, 160 generations: the pruning signature and TREE's dominance under each component. TREE pays per node and nothing per register; TAPE pays both. If the sign of damage follows the REGISTER price alone, the 'pruning' is a register-accounting effect on TAPE, not a structural-price effect on both.",
     unchanged="e06 world otherwise", attacks="the compression PRICE_MEDIATED", nonredundant="the price components were never separated", cost_minutes=4,
     continuation=["price on registers as a dose"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-G11", parent="T-X12", family="temporal_semantics", axis="response ruler", type="ruler-deformation", anti_gravity=True,
     delta="DO THE TEMPORAL CLASSES DISSOLVE UNDER A DIFFERENT RESPONSE RULER? The same idle-tick constructions (W0D1, W0D2, K2) read with four rulers: self-displacement (current), reward change against the episode's expected answers, answered-share change, and normalised output-word distance; the class assignment (immune / ask-time / schedule / other) under each ruler and the agreement between rulers on parents, walkers and C4-08 tops. If assignments disagree beyond a permutation band, the class is RULER_DEPENDENT.",
     unchanged="constructions, programs", attacks="T-X17's classes as ruler-invariant objects", nonredundant="only one response ruler was ever used", cost_minutes=3,
     continuation=["ruler agreement along walks"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2, regime_newly_reachable=1, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-G12", parent="T-X18", family="cross_substrate", axis="deleterious load in Proteus", type="serendipity-cross", serendipity=True, co_parents=["T-ARCH4/M1", "T-X15"],
     delta="DELETERIOUS LOAD READ IN PROTEUS: the P-F06 select and ndrift populations (seeds 1-2, regenerated) at G20 / G40 / G60: absolute reward change under scattered deletion f .05 (the qualified ruler) for every individual; share of individuals whose reward RISES; elite vs population; load vs generation and vs arm. If evolved Proteus programs also improve under blind deletion, load is cross-substrate; if not, it is an e06 (sharing + price) phenomenon.",
     unchanged="evolver, worlds, ruler", attacks="T-X18's portability", nonredundant="no Proteus population was ever read for improvement under deletion", cost_minutes=4, requires=["P-G01"],
     continuation=["load under weather", "load under price (P-F10 populations)"], scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))


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
            c["batch"] = "G"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
        # P-F02 re-posed as a manifold measurement (amendment; the candidate stays, its delta is extended)
        fh.write(json.dumps({"id": "P-F02", "amend": True, "recorded": ts, "delta_addendum": "CYCLE 5 RE-POSE: a MANIFOLD measurement - raw dose-response curves (0-4 idle ticks) at every construction position on W0D1 / W0D2 / K2, order variants, transition positions, lineage and world identity, genome summaries; programs: parents, walkers at 4/8/16, C4-08 tops, P-F03's evolved and transplanted tops; clustering with k chosen by silhouette over 2-6 and cluster shapes reported before any label; an unseen stable geometry is promoted before it is named"}, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(OUT)
    print("appended", added)


if __name__ == "__main__":
    main()
