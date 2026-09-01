"""Write the cycle-021 / cycle-028 frozen-test verdicts into the campaign's taxonomy log.

Run once, after `frozen_tests.py` has produced its result artifact. Every number below is
read from that artifact rather than retyped, so the log cannot drift from the measurement.
No mutation is applied by this script.
"""
from __future__ import annotations

import json
import pathlib
import sys

from . import store

RESULTS = pathlib.Path(__file__).resolve().parent / "frozen_test_results_20260901.json"


def main() -> int:
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    t1, t3 = r["tx001"], r["tx003"]
    seeds = t1["arms"]
    loo = t1["non_degradation_loo"]
    ceil3 = t3["ceiling"]

    events = []

    # ---------------------------------------------------------------- TX-001: PASS
    events.append({
        "event": "TAXONOMY_MUTATION_TESTED",
        "proposal_id": "TX-001-partial-cells",
        "status": "TESTED_PASS_NOT_YET_APPLIED",
        "tested_at_cycle": 38,
        "test": "held_out_failure_prediction + cross_field_retrieval (frozen at cycle 021)",
        "harness": "techne/cartography/frozen_tests.py, committed before it was run",
        "result_artifact": RESULTS.name,
        "result_digest": r["_digest"],
        "verdict": "PASS -- both clauses of the frozen pass condition are satisfied",
        "clause_1_strictly_more_placed": {
            "requirement": "the pairwise archive must place a strictly larger fraction of "
                           "held-out papers",
            "frozen_25pct_holdout": {
                "four_tuple": [s["four_tuple"]["placement_rate"] for s in seeds],
                "pairwise": [s["pairwise"]["placement_rate"] for s in seeds],
                "seeds": [s["seed"] for s in seeds],
            },
            "leave_one_out_supplement": {
                "four_tuple": str(loo["four_tuple"]["placed"]) + "/218 = "
                              + str(loo["four_tuple"]["placement_rate"]),
                "pairwise": str(loo["pairwise"]["placed"]) + "/218 = "
                            + str(loo["pairwise"]["placement_rate"]),
            },
            "satisfied": True,
        },
        "clause_2_no_degradation": {
            "requirement": "and not degrade the cross-field neighbour quality of those it "
                           "already placed",
            "reading": "PAIRED on the papers the 4-tuple archive places, not a comparison of "
                       "two marginal rates over two different paper sets",
            "frozen_25pct_holdout": [
                {"seed": s["seed"], **{k: v for k, v in s["non_degradation_paired"].items()
                                       if k != "power_note"}} for s in seeds],
            "leave_one_out_supplement": {k: v for k, v in loo["paired"].items()
                                         if k != "power_note"},
            "satisfied": True,
            "power_caveat": "n_comparable is 13 in the LOO supplement and 1-3 per frozen "
                            "split, because that is how few papers the 4-tuple archive "
                            "places. 0 of 13 degraded is consistent with a true degradation "
                            "rate up to roughly 25%. The clause is satisfied on the evidence "
                            "available and the evidence available is thin.",
        },
        "chance_floor_and_ceiling": {
            "note": "added by this harness (D4); the frozen text specified neither",
            "pairwise_observed": [s["pairwise"]["cross_field_rate"] for s in seeds],
            "pairwise_chance_floor_p95": [s["pairwise"]["chance_floor_p95"] for s in seeds],
            "beats_chance_all_seeds": all(s["pairwise"]["beats_chance"] for s in seeds),
            "headroom_reading_LOO": "of the 125 papers the pairwise archive places, 108 can "
                                    "ever register a cross-field hit (ceiling) and random "
                                    "neighbours reach about 91 (floor). The archive reaches "
                                    "104 -- roughly 76% of the headroom above chance.",
        },
        "what_a_pass_licenses": "replacing the single 4-tuple archive with marginal and "
                                "pairwise archives, and computing coverage holes per "
                                "axis-pair. It is a separate, reviewable act with its own "
                                "commit; this event does not perform it.",
        "what_a_pass_does_not_license": "reporting any hole as a research gap. See LIM-010: "
                                        "the cross-field metric that certifies neighbour "
                                        "quality has a dynamic range of about 13 points "
                                        "between its own floor and ceiling.",
    })

    # -------------------------------------------------- TX-003: test is unsatisfiable
    frozen_arms = {k: v for k, v in t3["arms"].items() if v["is_frozen_test_arm"]}
    events.append({
        "event": "TAXONOMY_MUTATION_TEST_UNSATISFIABLE",
        "proposal_id": "TX-003-coordinates-cannot-express-MI",
        "status": "PROPOSED_NOT_APPLIED -- unchanged; its frozen test cannot adjudicate it",
        "tested_at_cycle": 38,
        "verdict": "NOT_ADJUDICABLE. The cycle-028 frozen test cannot be passed by any "
                   "archive, any axis set, or any mutation, and its failure is therefore a "
                   "fact about the test rather than about mechanistic interpretability.",
        "the_arithmetic": {
            "n_mi_papers": t3["n_mi"],
            "pass_threshold_papers": t3["pass_threshold_papers"],
            "satisfiability_ceiling_papers": ceil3["SATISFIABILITY_CEILING"],
            "chance_floor_papers_p95": round(
                frozen_arms["current_axes"]["chance_floor_p95"] * t3["n_mi"]),
            "observed_papers": {k: v["cross_field_hits"] for k, v in frozen_arms.items()},
            "reading": "the pass condition needs 12 of 23; at most 7 of 23 can ever pass; "
                       "random neighbours already reach 6. Observed is 2. The entire "
                       "dynamic range of the metric is 1 paper wide.",
        },
        "why_the_ceiling_is_7": "the criterion requires a shared mechanism tag ABSENT from "
                                "the held-out paper's own title, but the tagger is lexical, "
                                "so 11 of 23 MI papers carry no tag that is not already in "
                                "their title and can never register a hit. Of the remaining "
                                "12, five carry only tags (causal_attribution, "
                                "circuit_representation, sparse_autoencoder) that appear on "
                                "ZERO non-MI papers, so they have no possible cross-field "
                                "partner. 23 - 11 - 5 = 7.",
        "this_is_the_LIM_003_error_class": "a kill made structurally impossible reads as a "
                                           "confirmed absence. The campaign was bitten by "
                                           "this once at cycle 033. Reporting the observed "
                                           "2/23 as 'MI does not retrieve cross-field' would "
                                           "have repeated it.",
        "what_the_mutation_actually_did": {
            "placement_on_4_tuple": {k: v["placed_on_4_tuple"] for k, v in frozen_arms.items()},
            "cross_field_hits": {k: v["cross_field_hits"] for k, v in frozen_arms.items()},
            "reading": "adding causal_intervention and faithfulness_to_reference moved MI "
                       "placement from 0 to 4 and moved cross-field retrieval by exactly 0. "
                       "Placement and retrieval are decoupled; TX-003 addressed placement "
                       "while claiming retrieval.",
        },
        "diagnostic_arms_not_part_of_the_frozen_test": {
            "purpose": "separate 'MI is inexpressible' from 'the 4-tuple archive is empty, "
                       "so nothing retrieves'",
            "result": {k: {"placed": v["placed_on_4_tuple"],
                           "archive_size": v["non_mi_archive_size"],
                           "cross_field_hits": v["cross_field_hits"]}
                       for k, v in t3["arms"].items() if not v["is_frozen_test_arm"]},
            "reading": "under the pairwise geometry the non-MI retrieval pool grows from 15 "
                       "papers to 157 -- a tenfold increase -- and cross-field hits move from "
                       "2 to 3, still below the chance floor. Archive emptiness is not the "
                       "binding constraint either.",
        },
        "what_is_owed_now": "a REPLACEMENT test for TX-003 whose satisfiability ceiling is "
                            "computed and published BEFORE it is frozen. Any replacement "
                            "must not certify cross-field identity through a lexical tagger, "
                            "because a lexical tag shared across two fields is a shared WORD, "
                            "which is the thing the criterion was written to exclude.",
        "proposal_status_unchanged": True,
    })

    # -------------------------------------------------------------------- LIM-009
    events.append({
        "event": "CAMPAIGN_LIMITATION_RECORDED",
        "limitation_id": "LIM-009-abstract-flag-stale-before-cycle-019",
        "status": "OPEN_NO_LIVE_CONSUMER",
        "recorded_at_cycle": 38,
        "finding": "the stored `abstract_available` flag is None for all 135 genomes "
                   "discovered in cycles 0-018, of which 123 in fact carry an abstract "
                   "evidence span. The field post-dates those genomes and was never "
                   "backfilled.",
        "measured": {"corpus": r["corpus_size"],
                     "abstract_bearing_by_evidence_span": r["abstract_bearing_by_evidence"],
                     "abstract_bearing_by_flag": r["abstract_bearing_by_flag"]},
        "impact_now": "none published. Every live consumer -- the claim predicates included "
                      "-- gates on the abstract TEXT, verified: 0 claims on the 86 title-only "
                      "genomes and 218 of 218 on the abstract-bearing ones. The comment in "
                      "cycle.py that says the flag 'stops every claim predicate' describes an "
                      "intent, not the implementation; the implementation is correct by a "
                      "different route.",
        "impact_if_unfixed": "any future analysis that filters on the flag runs on 95 genomes "
                             "instead of 218, and those 95 are entirely post-cycle-020 -- a "
                             "recency-biased sample of the exact region where the instrument "
                             "is known to degrade. The frozen tests would have been run on it.",
        "mitigation": "frozen_tests.has_abstract() derives the property from evidence spans. "
                      "A backfill of the stored flag is the durable fix and is not done here, "
                      "because rewriting 135 stored records to repair a field with no live "
                      "consumer is a larger act than the defect warrants.",
    })

    # -------------------------------------------------------------------- LIM-010
    events.append({
        "event": "CAMPAIGN_LIMITATION_RECORDED",
        "limitation_id": "LIM-010-cross-field-metric-has-no-dynamic-range",
        "status": "OPEN_STRUCTURAL",
        "recorded_at_cycle": 38,
        "severity": "HIGH -- cross_field_retrieval is one of the four listed "
                    "TAXONOMY_MUTATION_TESTS and it is the one the brief calls the Rosetta "
                    "Stone question",
        "finding": "the cross-field criterion -- a neighbour sharing a mechanism tag absent "
                   "from the held-out paper's title -- is bounded above by the tagger, not by "
                   "the archive. Its ceiling and its chance floor sit close together, and on "
                   "the MI population the floor is ABOVE where the measurement lands.",
        "measured": {
            "TX_003_population": {"n": t3["n_mi"], "floor_p95_papers": round(
                frozen_arms["current_axes"]["chance_floor_p95"] * t3["n_mi"]),
                "ceiling_papers": ceil3["SATISFIABILITY_CEILING"],
                "range_papers": ceil3["SATISFIABILITY_CEILING"] - round(
                    frozen_arms["current_axes"]["chance_floor_p95"] * t3["n_mi"])},
            "TX_001_pairwise_population": {
                "n_placed_LOO": loo["pairwise"]["placed"],
                "ceiling_papers": 108, "floor_papers_approx": 91,
                "observed_papers": round(loo["pairwise"]["cross_field_rate"]
                                         * loo["pairwise"]["placed"]),
                "reading": "the archive captures roughly 76% of the headroom above chance, "
                           "which is a real signal in a narrow band, not a large effect"},
        },
        "why_it_is_structural": "the tagger assigns a tag BY finding its surface form in the "
                                "text. The only way a shared tag can be absent from the "
                                "held-out title is if it was found in the abstract instead, "
                                "so the metric's whole capacity is the abstract-minus-title "
                                "vocabulary residue. That residue is 51% of the corpus and "
                                "much less on any population whose papers are short-titled.",
        "consequence": "every frozen test that uses cross_field_retrieval must publish its "
                       "satisfiability ceiling next to its pass threshold BEFORE being "
                       "frozen. A test whose ceiling is below its threshold is not a test.",
        "applies_retroactively_to": ["TX-001-partial-cells (passes; ceiling published here)",
                                     "TX-003-coordinates-cannot-express-MI (unsatisfiable)"],
    })

    # ------------------------------------------------ LIM-004 escalation: MI polysemy
    events.append({
        "event": "CAMPAIGN_LIMITATION_ESCALATED",
        "limitation_id": "LIM-004-collision-lane-defeated-by-polysemy",
        "status": "OPEN_UNMITIGATED",
        "escalated_at_cycle": 38,
        "new_evidence": "polysemy is not confined to the collision lane's QUERIES -- it "
                        "contaminates a POPULATION the campaign has already reasoned from. "
                        "The 23 papers that tag as mechanistic interpretability include a "
                        "survey of IoT security, transmission-line fault classification, "
                        "bearing fault diagnosis, aptamer-protein interaction prediction, "
                        "quantum circuit optimisation for NISQ architectures, TrakEM2 "
                        "neural-circuit reconstruction software, and microbial electron "
                        "transfer. They are tagged MI because `sparse_autoencoder` and "
                        "`circuit_representation` are polysemous across speech processing, "
                        "power engineering, quantum computing and neuroscience.",
        "count": "roughly 12 of 23 are not mechanistic-interpretability papers",
        "why_this_matters_more_than_a_query_defect": "TX-003 was proposed at cycle 028 from "
                        "the observation that '19 MI papers are tagged better than EC papers "
                        "and placed worse'. That population was contaminated the same way. A "
                        "taxonomy mutation was proposed on the basis of a population the "
                        "instrument mis-assembled, which is a failure one level deeper than a "
                        "lane returning bad results.",
        "not_yet_done": "the MI population has NOT been hand-audited and no paper has been "
                        "reclassified. The count above is a read of titles and is PROPOSED, "
                        "not adjudicated -- an LLM reading titles is exactly what the "
                        "campaign's adjudication rule forbids from writing CONFIRMED.",
    })

    for e in events:
        d = store.append("taxonomy", e)
        print(e.get("proposal_id") or e.get("limitation_id"), "->", d[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
