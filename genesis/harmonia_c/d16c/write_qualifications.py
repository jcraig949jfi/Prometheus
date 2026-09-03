"""Phase 0 step 12 helper: assemble D16C_BENCHMARK_QUALIFICATION.json and
D16C_CROSSING_QUALIFICATION.json from the step result files (no new
measurements; every number is read from results/)."""
import json
H = "sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc"
s1 = json.load(open("results/step1_adjudicator.json")); cen = json.load(open("results/step2_4_census.json"))
s6 = json.load(open("results/step6_duplicate_evidence.json")); s7 = json.load(open("results/step7_f10_frontier.json"))
s8 = json.load(open("results/step8_loso_engine.json")); s5 = json.load(open("results/step5_laundering.json"))
bench = {
 "verdict_name": "D16C_BENCHMARK_QUALIFIED", "verdict": "YES",
 "date": "2026-09-02", "benchmark": "LT (lt.py): hidden linear structure over GF(2)^8; components A (a*), B (basis/P2,c2), C (m*); tasks A,B,C,AB,AC,ABC0,ABC1,ABC2",
 "step1_adjudicator": {"worlds": s1["worlds"], "invariant_unique": s1["invariant_unique"], "answers_match_bruteforce": s1["answers_match_bruteforce"],
    "full_knowledge_correct": s1["full_knowledge_correct"], "partial_soundness_checks": s1["partial_soundness_checks"], "partial_unsound": s1["partial_unsound"],
    "portal_preserves_astar_false_positives": s1["portal_preserves_astar"]},
 "step2_census": {"marginal_guess_rate_per_task": cen["marginal_guess_rate"], "answer_entropy_bits": cen["answer_entropy_bits"],
    "prior_a_star_max_share": cen["prior_a_star_max_share"], "prior_m_star_max_share": cen["prior_m_star_max_share"],
    "info_floor_queries": cen["info_floor_queries"], "blind_cost_random": cen["blind_cost_random"],
    "public_data_independent_of_hidden": cen["public_data_independent_of_hidden"],
    "KILLED": {"task": "BC", "empty_answer_rate": 0.885, "defect": "SD-001", "disposition": "removed from INTERACTIVE before any ecology run"}},
 "step3_multi_component_necessity": {"proper_subset_determined_rate": "0.0 for every (task, known-subset) pair (27 pairs, 100 worlds each)",
    "full_set_correct_rate": cen["necessity_full_set_correct_rate"], "partial_missing_component_at_4_queries": cen["necessity_partial_missing_component"],
    "master_key_residual_candidates": cen["master_key_residual_candidates"]},
 "step4_union_vs_composition_offline": dict(cen["union_vs_composition"], note="200/200 interactive cells: LOSO necessary set == design set; UNION alone never suffices; 40/40 ancestor-of-answer cases correctly NOT labelled composition"),
 "Q8_accidental_universal_strategy": {"answer": "ONE FOUND AND KILLED (BC: empty answer 88.5%); after removal max marginal-guess rate 0.02 (A) and 0.015 (AB); no remaining task admits a public-data-only or constant strategy above 2%"},
 "Q9_majority_wrong_vs_one_falsifier": {"answer": "YES under FALSIFIER_FIRST and VERIFY_K (60/60 at 3:1 and 7:1); NO under BLIND (0/60)",
    "consensus_decoy_n60": s6["consensus_decoy_n60"], "defect": "SD-002 (VERIFY_ONE non-decisive -> VERIFY_K)",
    "forged_counter_falsifier_shape": "reading-only FALSIFIER_FIRST abstains 24/60, never wrong; executing VERIFY_K re-runs the contradicting record, drops the forgery, 60/60"},
 "synthesizer_policy_set_for_pilot": ["RAW", "FALSIFIER_FIRST", "VERIFY_K"],
 "evidence_class": "adjudicator/census/necessity are exact enumerations on the generator (deterministic seeds); decoy is binomial n=60",
 "science_defects": ["SD-001", "SD-002"],
 "caveat": "qualification is of the BENCHMARK as a measuring instrument only; it says nothing about whether the engine can host it (see crossing/concurrency)"}
json.dump(bench, open("D16C_BENCHMARK_QUALIFICATION.json", "w"), indent=1)

cross = {
 "verdict_name": "D16C_CROSSING_QUALIFIED", "verdict": "NO",
 "companion_verdict": {"D16C_CAUSAL_AUDIT_QUALIFIED": "YES (mechanically) -- the AVAILABLE/CONSUMED/NECESSARY ladder is computable on-engine and matched design 20/20; but AVAILABLE is only trustworthy when read at the fork/import cutoff seq (ED-003) and CONSUMED is CLIENT_ASSERTED (F1 not ledgered)"},
 "date": "2026-09-02", "engine_hash": H, "instance": "PRIVATE_PINNED http://127.0.0.1:8899 (live engine untouched)",
 "vocabulary": {"AVAILABLE": "engine-certified: F10 knowledge_set of the synthesis world", "CONSUMED": "client-asserted: F1 artifact_bytes read log", "NECESSARY": "counterfactual: fresh LOSO synthesis world flips verdict"},
 "step5_origin_laundering": {"defect": "ED-001 GEN21_ORIGIN_LAUNDERING", "severity": "CRITICAL", "variations_laundered": "6/6",
    "variations": [v["variation"] for v in s5["variations"]],
    "H6_control": "C importing the IMPORTED row of B directly: 403 (holds)",
    "forensic_handle": "byte-identical: content_hash collision inside the F10 of B (1 IMPORTED + 5 NATIVE, same blob_hash) -- visible only to the owner of B or a DB auditor; byte-different semantic equivalent: NO engine-visible trace",
    "reproducer": "repro/GEN21_ORIGIN_LAUNDERING_repro.py (<1 s, standalone)", "owner": "Daedalus",
    "disposition": "BLOCKING: pilot (step 10) and threshold freeze (step 11) HELD; not solved in client code; not reinterpreted as rediscovery (engine has no rediscovery/copy discriminator)"},
 "step6_duplicate_evidence": {"defect": "ED-002 SUBSTRATE_GAP: EVIDENCE_INDEPENDENCE_NOT_REPRESENTABLE", "severity": "MAJOR",
    "constructions": {k: v["engine_verdict"] for k, v in s6["constructions"].items()},
    "C4_separable_from": s6["C4_separable_from"], "indistinguishable_from_C4": s6["indistinguishable_from_C4"],
    "api_only": "NONE separable (get_world/knowledge/events owner-only 403; no auditor role); DB tables needed for C1-C3",
    "consequence": "cells whose inference needs independence of apparently separate evidence are VOID unless independence is established by construction outside the engine"},
 "step7_f10_frontier": {"checks": s7["summary"]["n"], "pass": s7["summary"]["pass"], "fail": s7["summary"]["fail"],
    "held": "checkpoint-boundary inheritance exact; transitive to grandchildren; cutoff fail-closed, monotone, deterministic; import-then-fork inherits import at import seq",
    "defect": "ED-003 F10_PROVENANCE_REWRITE_ON_NATIVE_RECREATION (MAJOR): native re-creation of inherited content flips basis fork_inheritance->native_creation and first_available_seq 202->212 in F10(now); F10(seq=fork) still correct",
    "Q5_answer": "availability SET exact at every merge/fork frontier tested; basis/first_available_seq NOT stable under native re-creation"},
 "step8_loso_on_engine": {"worlds": s8["n_worlds"], "budget": s8["budget"], "summary": s8["summary"],
    "attribution": "20/20 interactive cells: NECESSARY == design set (TRUE_COMPOSITION); 0 UNION_ONLY; 0 UNSOLVED_FULL",
    "budget_exactness": "12/12 lineages: engine consumed == researcher spend (enforceable budget, 409 at cap)",
    "H5_control": "cross-group import denied 3/3",
    "SHUFFLED_SOURCE_CONTROL": {"AB": "WRONG 4/4", "ABC0-2": "WRONG 4/4", "AC": "CORRECT 4/4 (does not depend on B)",
       "shape": "RAW merge treats foreign observations as facts -> WRONG, not abstain; endpoint is source-sensitive (which a composition claim needs), but a wrong source silently poisons rather than being detected"}},
 "Q1": "YES -- targets non-decomposable (proper-subset determinacy 0/100; UNION never suffices offline 200/200)",
 "Q2": "YES -- multi-source necessity by LOSO 200/200 offline, 20/20 on-engine",
 "Q3": "YES, IT LAUNDERS -- 6/6 (CRITICAL, ED-001)",
 "Q4": "NO -- C5 out-of-band copy is state-identical to true independent replication (ED-002)",
 "Q5": "SET yes; PROVENANCE no (ED-003)",
 "Q7": "NOT TESTABLE -- pilot held by the Amendment-2 gate; import cost sensitivity {0,1,HIGH} unrun",
 "Q10": "NO as-is -- a provenance-clean multi-lineage ecology needs ED-001 fixed and ED-002/ED-003 either fixed or designed around by construction",
 "engine_defects": ["ED-001", "ED-002", "ED-003"],
 "evidence_class": "CLIENT_ASSERTED for all LT observations (hidden-world oracle runs client-side); engine-certified for availability, ledger, budget",
 "what_would_flip_the_verdict": "ED-001 closed by Daedalus (create_artifact refuses/marks NATIVE rows whose blob_hash matches a prior IMPORTED row in the same world AND a principled rediscovery/copy discriminator for byte-different content, or a design ruling that laundering is out of scope for D16-C cells) + a read-side fix or workaround for ED-003 (always read F10 at cutoff seq)"}
json.dump(cross, open("D16C_CROSSING_QUALIFICATION.json", "w"), indent=1)
print("ok")
