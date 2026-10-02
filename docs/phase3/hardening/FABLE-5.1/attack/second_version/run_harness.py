"""Run the reference harness v0 and write its receipt.

    python -B run_harness.py            writes RECEIPT_harness_v0.json next to this file

Exit code 0 only if every gate passes its clean cases, rejects its mutants with the registered
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

from rso_harness import audits, ladder, meta, retain1, rulers, search, stats  # noqa: E402
from rso_harness.verdict import PASS  # noqa: E402

RECEIPTS = ("RECEIPT_gauntlet.json", "RECEIPT_gauntlet2.json", "RECEIPT_gauntlet3.json", "RECEIPT_keys.json")
CLAIMS_AT = (("STRONG", "V01@RUN1"), ("STRONG", "S19@RUN2"), ("STRONG", "S19@RUN3"), ("REUSE", "V01@RUN1"),
             ("REUSE", "S19@RUN2"), ("REUSE", "S19@RUN3"), ("BITS", "BITS@KEYS"), ("BITS_TWO_LEVELS", "BITS@TWO"),
             ("COMPOSITION", "BITS@PAIRS"))


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


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
    }
    panel = {physics: {"positive": retain1.score(pos, meta.SEEDS), "impostor": retain1.score(imp, meta.SEEDS)}
             for physics, (pos, imp) in sorted(retain1.PANEL.items())}
    reach = {"%s/%s" % (ls, pol): {
        "cold_exact": search.exact_reach(ls, pol, meta.BUDGET, "COLD"),
        "repair1_exact": search.exact_reach(ls, pol, meta.BUDGET, "REPAIR", 1),
        "cold_hits_of_%d" % len(meta.FOUNDERS): search.sample_reach(ls, pol, meta.BUDGET, "COLD", meta.FOUNDERS)}
        for ls in sorted(search.LANDSCAPES) for pol in ("STRICT", "NEUTRAL")}
    ok = all(r["status"] == PASS for r in rows.values()) and all(e["verdict"] == PASS for e in escapes)
    verdicts = {}
    for r in rows.values():
        for m in r["mutant_verdicts"]:
            verdicts[m["verdict"]] = verdicts.get(m["verdict"], 0) + 1
    modules = sorted((HERE / "rso_harness").glob("*.py")) + [HERE / "run_harness.py", HERE / "tests" / "test_harness.py"]
    k = stats.critical_k(len(meta.SEEDS), rulers.BOUND, rulers.ALPHA)
    out = {
        "what": "reference harness v0 for the Phase 3 hardening design, FABLE-5.1 version: conformance on toy "
                "fixtures and audits of four existing receipts; it qualifies no science",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": sys.version.split()[0],
        "summary": {"gates": len(rows), "gates_passing_their_registered_cases": sum(
                        1 for r in rows.values() if r["status"] == PASS),
                    "clean_cases": sum(r["clean"] for r in rows.values()),
                    "mutants": sum(r["mutants"] for r in rows.values()), "mutant_verdicts": verdicts,
                    "known_escapes": len(escapes), "gates_with_a_known_escape": len({e["gate"] for e in escapes}),
                    "all_as_registered": ok},
        "parameters": {"episodes": len(meta.SEEDS), "alpha": rulers.ALPHA, "exact_bound": rulers.BOUND,
                       "weakest_registered_positive": rulers.P_WEAKEST, "critical_k": k,
                       "negative_at_or_below": stats.lower_critical(len(meta.SEEDS), rulers.P_WEAKEST, rulers.ALPHA),
                       "inverted_at_or_below": stats.lower_critical(len(meta.SEEDS), rulers.BOUND, rulers.ALPHA),
                       "power_at_weakest_positive": stats.tail_ge(len(meta.SEEDS), k, rulers.P_WEAKEST),
                       "impostor_blocks": 1 + len(meta.BLOCKS), "pairs": len(meta.PAIRS),
                       "founders_for_calibration": len(meta.FOUNDERS), "calibration_alpha": search.CAL_ALPHA,
                       "founders_in_a_report": len(meta.REPORTED), "search_budget": meta.BUDGET,
                       "zero_hit_bound": stats.zero_hit_upper(len(meta.REPORTED)),
                       "demand_episodes": len(meta.DEMAND), "demand_margin": 0.1},
        "gates": rows, "known_escapes": escapes, "panel_scores_of_64": panel,
        "weak_positive_score_of_64": retain1.score(retain1.FadingRegister, meta.SEEDS),
        "bound_bracket": meta.bracket(), "search": reach,
        "audits_of_existing_receipts": audit,
        "exploratory_two_level_key_world": {
            "status": "EXPLORATORY: no registered verdict; written after the adversarial reader's probe",
            "lives": 300, "epochs": 3, "families_per_epoch": 4, "exact_nothing_carried_bound": ladder.H16,
            "survey": ladder.survey(300)},
        "exploratory_unseen_pair_world": {
            "status": "EXPLORATORY: no registered verdict; simulated before being proposed as the next experiment",
            "lives": 300, "pairs_shown": len(ladder.SHOWN), "pairs_in_the_control_history": len(ladder.CONTROL),
            "exact_nothing_carried_bound": ladder.H16, "survey": ladder.survey_pairs(300)},
        "source_sha256_lf": {p.relative_to(HERE).as_posix(): sha(p) for p in modules},
        "audited_receipts_sha256_lf": {n: sha(meta.COUNTERFEIT / n) for n in RECEIPTS},
    }
    (HERE / "RECEIPT_harness_v0.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n",
                                                  encoding="ascii", newline="\n")
    s = out["summary"]
    print("gates %d, passing their registered cases %d; clean cases %d; mutants %d %s; known escapes %d in %d gates; "
          "all as registered: %s" % (s["gates"], s["gates_passing_their_registered_cases"], s["clean_cases"],
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
