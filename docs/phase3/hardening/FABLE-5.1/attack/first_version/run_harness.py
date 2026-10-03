"""Run the reference harness v0 and write its receipt.

    python -B run_harness.py            writes RECEIPT_harness_v0.json next to this file

Exit code 0 only if every gate passes its clean cases, rejects its mutants with the registered
verdict, and the two known escapes are still escapes.
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

from rso_harness import audits, meta, retain1, search, stats  # noqa: E402
from rso_harness.verdict import PASS  # noqa: E402


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
        "rulers": {c: audits.ruler_status(c, receipts=meta.COUNTERFEIT).as_dict()
                   for c in ("ORDER3_BITS", "ORDER3_REUSE", "ORDER4_BITS", "STRONG_RECURSION")},
    }
    panel = {physics: {"positive": retain1.score(pos, meta.SEEDS), "impostor": retain1.score(imp, meta.SEEDS)}
             for physics, (pos, imp) in sorted(retain1.PANEL.items())}
    reach = {"%s/%s" % (ls, pol): {
        "cold_exact": search.exact_reach(ls, pol, meta.BUDGET, "COLD"),
        "repair1_exact": search.exact_reach(ls, pol, meta.BUDGET, "REPAIR", 1),
        "cold_hits_of_%d" % len(meta.FOUNDERS): search.sample_reach(ls, pol, meta.BUDGET, "COLD", meta.FOUNDERS)}
        for ls in sorted(search.LANDSCAPES) for pol in sorted(search.POLICIES)}
    ok = all(r["status"] == PASS for r in rows.values()) and all(e["verdict"] == PASS for e in escapes)
    verdicts = {}
    for r in rows.values():
        for m in r["mutant_verdicts"]:
            verdicts[m["verdict"]] = verdicts.get(m["verdict"], 0) + 1
    modules = sorted((HERE / "rso_harness").glob("*.py")) + [HERE / "run_harness.py", HERE / "tests" / "test_harness.py"]
    out = {
        "what": "reference harness v0 for the Phase 3 hardening design, FABLE-5.1 version: conformance on toy "
                "fixtures and audits of four existing receipts; it qualifies no science",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": sys.version.split()[0],
        "summary": {"gates": len(rows), "gates_qualified": sum(1 for r in rows.values() if r["status"] == PASS),
                    "clean_cases": sum(r["clean"] for r in rows.values()),
                    "mutants": sum(r["mutants"] for r in rows.values()), "mutant_verdicts": verdicts,
                    "known_escapes": len(escapes), "all_as_registered": ok},
        "parameters": {"episodes": len(meta.SEEDS), "alpha": 1e-6, "exact_bound": 0.5,
                       "critical_k": stats.critical_k(len(meta.SEEDS), 0.5, 1e-6), "pairs": len(meta.PAIRS),
                       "founders": len(meta.FOUNDERS), "search_budget": meta.BUDGET,
                       "zero_hit_bound": stats.zero_hit_upper(len(meta.FOUNDERS))},
        "gates": rows, "known_escapes": escapes, "panel_scores_of_64": panel, "search": reach,
        "audits_of_existing_receipts": audit,
        "source_sha256_lf": {p.relative_to(HERE).as_posix(): sha(p) for p in modules},
        "audited_receipts_sha256_lf": {n: sha(meta.COUNTERFEIT / n) for n in (
            "RECEIPT_gauntlet.json", "RECEIPT_gauntlet2.json", "RECEIPT_gauntlet3.json", "RECEIPT_keys.json")},
    }
    (HERE / "RECEIPT_harness_v0.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n",
                                                  encoding="ascii", newline="\n")
    s = out["summary"]
    print("gates %d, qualified %d; clean cases %d; mutants %d %s; known escapes %d; all as registered: %s"
          % (s["gates"], s["gates_qualified"], s["clean_cases"], s["mutants"], s["mutant_verdicts"],
             s["known_escapes"], ok))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
