"""Run the reference harness v0 and write its receipt.

    python -B run_harness.py            writes RECEIPT_harness_v0.json next to this file

Exit code 0 only if every gate passes its sound cases, rejects its mutants with the registered
verdict, and every known escape is still an escape.
"""
import hashlib
import json
import pathlib
import platform
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from rso_harness import audits, ladder, meta, retain1, rulers, search, stats, torture  # noqa: E402
from rso_harness.verdict import PASS  # noqa: E402

RECEIPTS = ("RECEIPT_gauntlet.json", "RECEIPT_gauntlet2.json", "RECEIPT_gauntlet3.json", "RECEIPT_keys.json")
CLAIMS_AT = (("STRONG", "V01@RUN1"), ("STRONG", "S19@RUN2"), ("STRONG", "S19@RUN3"), ("BITS", "BITS@KEYS"),
             ("BITS_TWO_BOUNDARIES", "BITS@TWO"), ("COMBINATION", "BITS@PAIRS"))
LIVES = 300


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def attainable(outcome, hits, n):
    """Probability of a fixture answer at the worse end of the exact interval around hits/n design units."""
    return min(stats.outcome_probability(meta.table(), rate).get(outcome, 0.0)
               for rate in (stats.lower_bound(hits, n), stats.upper_bound(hits, n)))


def main():
    rows = meta.qualify()
    escapes = meta.known_escapes()
    r2, r3 = meta.run2(), meta.run3()
    t2, t3 = audits.clause_table(r2, audits.clauses_run2), audits.clause_table(r3, audits.clauses_run3)
    audit = {
        "run2": {
            "clauses": audits.audit_clauses(r2, audits.clauses_run2).as_dict(),
            "arms_BUILDER": audits.audit_arms(r2["BUILDER"]["replicates"], meta.ARMS2).as_dict(),
            "sham_BUILDER": audits.audit_sham(r2["BUILDER"]["replicates"], t2["NESTING.sham_harmless"]).as_dict(),
            "setting": audits.audit_setting(audits.RUN2).as_dict(),
        },
        "run3": {
            "clauses": audits.audit_clauses(r3, audits.clauses_run3).as_dict(),
            "arms_STRATEGIST": audits.audit_arms(r3["STRATEGIST"]["replicates"], meta.ARMS3).as_dict(),
            "sham_STRATEGIST": audits.audit_sham(r3["STRATEGIST"]["replicates"],
                                                 t3["NESTING.sham_harmless"]).as_dict(),
            "setting": audits.audit_setting(audits.RUN3).as_dict(),
        },
        "run2_against_run3": audits.audit_contrast("parts_shared", audits.RUN2, audits.RUN3).as_dict(),
        "rulers": {"%s at %s" % (c, s): audits.ruler_status(c, s, meta.COUNTERFEIT).as_dict() for c, s in CLAIMS_AT},
        "what_each_ruler_returned": {"%s at %s" % (m, s): audits.returned(meta.COUNTERFEIT, src)
                                     for m, s, src, _ in audits.RUNS},
        "registered_answers": {"%s at %s" % (m, s): a for m, s, _, a in audits.RUNS},
        "registered_and_not_built": audits.UNBUILT,
        "what_a_ruler_for_the_package_kit_would_have_to_return": audits.KIT_ANSWERS,
    }
    positives, weak, impostors = meta.organism_scores()
    panel = {"positives": dict(zip(sorted(retain1.PANEL), positives)), "weak_positive": weak,
             "impostors_on_nine_blocks": impostors,
             "interchange": {p: {"positive": rulers.interchange_ruler(pos, meta.SEEDS),
                                 "impostor": rulers.interchange_ruler(imp, meta.SEEDS)}
                             for p, (pos, imp) in sorted(retain1.PANEL.items())},
             "register_swap": {p: {"positive": rulers.register_swap_ruler(pos, meta.SEEDS),
                                   "impostor": rulers.register_swap_ruler(imp, meta.SEEDS)}
                               for p, (pos, imp) in sorted(retain1.PANEL.items())}}
    reach = {"%s/%s" % (ls, pol): {
        "cold_exact": search.exact_reach(ls, pol, meta.BUDGET, "COLD"),
        "repair1_exact": search.exact_reach(ls, pol, meta.BUDGET, "REPAIR", 1),
        "cold_hits_of_%d" % len(meta.FOUNDERS): search.sample_reach(ls, pol, meta.BUDGET, "COLD", meta.FOUNDERS)}
        for ls in sorted(search.LANDSCAPES) for pol in ("STRICT", "NEUTRAL")}
    reach["positive_control_by_budget"] = {str(b): search.exact_reach(search.CONTROL, "STRICT", b, "COLD")
                                           for b in (5, 24, 46, 47, meta.BUDGET)}
    reach["needle_neutral_hits_of_%d_by_budget" % len(meta.REPORTED)] = {
        str(b): meta.hits("NEEDLE", "NEUTRAL", budget=b) for b in (8, 24, meta.BUDGET)}
    reach["needle_neutral_cold_exact_at_24"] = search.exact_reach("NEEDLE", "NEUTRAL", 24, "COLD")
    ok = all(r["status"] == PASS for r in rows.values()) and all(e["verdict"] == PASS for e in escapes)
    verdicts = {}
    for r in rows.values():
        for m in r["mutant_verdicts"]:
            verdicts[m["verdict"]] = verdicts.get(m["verdict"], 0) + 1
    modules = sorted((HERE / "rso_harness").glob("*.py")) + [HERE / "run_harness.py", HERE / "tests" / "test_harness.py"]
    n, pairs = len(meta.SEEDS), 2 * len(meta.SEEDS)
    k = stats.critical_k(n, rulers.BOUND, rulers.ALPHA)
    demand = torture.demand_closure(meta.DEMAND, meta.TRAIN)
    out = {
        "what": "reference harness v0 for the Phase 3 hardening design, FABLE-5.1 version: conformance on toy "
                "fixtures and audits of four existing receipts; it qualifies no science",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": sys.version.split()[0],
        "summary": {"gates": len(rows), "gates_passing_their_registered_cases": sum(
                        1 for r in rows.values() if r["status"] == PASS),
                    "sound_cases": sum(r["clean"] for r in rows.values()),
                    "mutants": sum(r["mutants"] for r in rows.values()), "mutant_verdicts": verdicts,
                    "known_escapes": len(escapes), "gates_with_a_known_escape": len({e["gate"] for e in escapes}),
                    "all_as_registered": ok},
        "parameters": {"episodes": n, "alpha": rulers.ALPHA, "exact_bound": rulers.BOUND,
                       "weakest_registered_positive": rulers.P_WEAKEST, "critical_k": k,
                       "negative_at_or_below": stats.lower_critical(n, rulers.P_WEAKEST, rulers.ALPHA),
                       "inverted_at_or_below": stats.lower_critical(n, rulers.BOUND, rulers.ALPHA),
                       "power_at_weakest_positive": stats.tail_ge(n, k, rulers.P_WEAKEST),
                       "registered_thresholds": {str(c): a for c, a in sorted(rulers.EDGES.items())},
                       "interchange_pairs": pairs,
                       "interchange_critical_k": stats.critical_k(pairs, 0.5, rulers.ALPHA),
                       "interchange_negative_at_or_below": stats.lower_critical(pairs, rulers.P_WEAKEST, rulers.ALPHA),
                       "interchange_inverted_at_or_below": stats.lower_critical(pairs, 0.5, rulers.ALPHA),
                       "power_floor": stats.POWER_FLOOR, "design_confidence": stats.DESIGN_CONFIDENCE,
                       "impostor_blocks": 1 + len(meta.BLOCKS), "torture_seeds": len(meta.PAIRS),
                       "founders_for_calibration": len(meta.FOUNDERS), "calibration_alpha": search.CAL_ALPHA,
                       "founders_in_a_report": len(meta.REPORTED), "search_budget": meta.BUDGET,
                       "zero_hit_bound": stats.zero_hit_upper(len(meta.REPORTED)),
                       "demand_episodes": len(meta.DEMAND), "demand_margin": torture.MARGIN,
                       "demand_alpha": torture.DEMAND_ALPHA},
        "fixture_attainability": {"HOLDS, design 480 of 480": attainable("HOLDS", 480, 480),
                                  "HOLDS, design 240 of 240": attainable("HOLDS", 240, 240),
                                  "HOLDS, design 466 of 480": attainable("HOLDS", 466, 480),
                                  "FAILS, design 96 of 480": attainable("FAILS", 96, 480),
                                  "FAILS, design 120 of 480": attainable("FAILS", 120, 480)},
        "gates": rows, "known_escapes": escapes, "panel_scores_of_64": panel,
        "bound_bracket": meta.bracket(), "demand_closure_scores_of_2048": demand.detail, "search": reach,
        "audits_of_existing_receipts": audit,
        "exploratory_world_one_two_nested_boundaries": {
            "status": "EXPLORATORY: no registered verdict; written after the first adversarial reader's probe",
            "lives": LIVES, "epochs": 3, "families_per_epoch": 4, "exact_nothing_carried_bound": ladder.H16,
            "survey": ladder.survey(LIVES)},
        "exploratory_world_two_unseen_pair": {
            "status": "EXPLORATORY: no registered verdict. A score above the bound on the ninth pair says that "
                      "information from at least three separately shown families was combined, and nothing about how",
            "lives": LIVES, "pairs_shown": len(ladder.SHOWN), "exact_nothing_carried_bound": ladder.H16,
            "control": "the eight families shown come from another key under the same labels; it guards only "
                       "against a leak that reaches both arms alike",
            "custody": "every life's key is hashed; a run in which one repeats is answered KEY_REUSED",
            "survey": ladder.survey_pairs(LIVES)},
        "source_sha256_lf": {p.relative_to(HERE).as_posix(): sha(p) for p in modules},
        "audited_receipts_sha256_lf": {name: sha(meta.COUNTERFEIT / name) for name in RECEIPTS},
    }
    (HERE / "RECEIPT_harness_v0.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n",
                                                  encoding="ascii", newline="\n")
    s = out["summary"]
    print("gates %d, passing their registered cases %d; sound cases %d; mutants %d %s; known escapes %d in %d gates; "
          "all as registered: %s" % (s["gates"], s["gates_passing_their_registered_cases"], s["sound_cases"],
                                     s["mutants"], s["mutant_verdicts"], s["known_escapes"],
                                     s["gates_with_a_known_escape"], ok))
    for gid, r in rows.items():
        if r["status"] != PASS:
            print("NOT PASS", gid, r["status"], r["false_alarms"], r["escapes"], r["wrong_kind"])
    for e in escapes:
        if e["verdict"] != PASS:
            print("NO LONGER AN ESCAPE", e["gate"], e["verdict"], e["fault"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
