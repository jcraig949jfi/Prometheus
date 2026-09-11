#!/usr/bin/env python3
"""
Negative / cheat tests for engine/necropolis/validate.py (Rhadamanthus, 2026-09-11).

A validator that only ever sees well-formed dossiers is a decoration. Each case below
takes a validating dossier (coeus), applies ONE mutation that the doctrine says must be
refused (REJECT) or that the doctrine says SHOULD be refused but the validator is not
known to check (CHEAT), copies the necropolis directory to a scratch location, runs
validate.py there, and records whether the mutation was caught.

Runs entirely in a scratch copy: the worktree ORGANS.jsonl / COUNTERFACTUAL_HISTORY.jsonl
are never touched (validate.py regenerates those in place).

Usage: python engine/necropolis/tests/validator_negative_tests.py [--out result.json]
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NECRO = os.path.abspath(os.path.join(HERE, ".."))
BASE_DOSSIER = "coeus.dossier.json"


def mutate_cases():
    """Return list of (name, kind, mutator(d) -> None)."""
    C = []
    def stack(d): return d["autopsy"]["cause_of_death_stack"]

    def m_failed(d): d["disposition"]["classification"] = "FAILED"
    C.append(("classification_FAILED", "REJECT", m_failed))

    def m_tc_unfair(d): d["disposition"]["classification"] = "TRUE_CORPSE"
    C.append(("TRUE_CORPSE_with_UNFAIR", "REJECT", m_tc_unfair))

    def m_strong_unfair(d):
        d["autopsy"]["primary_cause"] = "HYPOTHESIS_FAILURE"
        stack(d)["HYPOTHESIS"]["cause_classes"] = ["HYPOTHESIS_FAILURE"]
    C.append(("HYPOTHESIS_FAILURE_with_UNFAIR", "REJECT", m_strong_unfair))

    def m_fair_but_lb(d): d["autopsy"]["fair_test"]["verdict"] = "FAIR"
    C.append(("FAIR_with_load_bearing_INVALID", "REJECT", m_fair_but_lb))

    def m_ne_cause(d):
        L = stack(d)["ECOSYSTEM"]; L["verdict"] = "NOT_EXAMINED"; L["cause_classes"] = ["ECOSYSTEM_FAILURE"]
    C.append(("NOT_EXAMINED_with_cause_class", "REJECT", m_ne_cause))

    def m_valid_noev(d):
        L = stack(d)["IMPLEMENTATION"]; L["verdict"] = "VALID"; L["evidence"] = []; L["cause_classes"] = []
    C.append(("VALID_with_no_evidence", "REJECT", m_valid_noev))

    def m_pc_orphan(d):
        d["autopsy"]["primary_cause"] = "ECOSYSTEM_FAILURE"
        stack(d)["ECOSYSTEM"]["cause_classes"] = []; stack(d)["ECOSYSTEM"]["verdict"] = "VALID"
    C.append(("primary_cause_not_on_any_layer", "REJECT", m_pc_orphan))

    def m_wrong_layer(d): stack(d)["DESIGN"]["cause_classes"] = ["MEASUREMENT_ERROR"]
    C.append(("cause_class_on_inadmissible_layer", "REJECT", m_wrong_layer))

    def m_overturned_noerr(d): d["autopsy"]["death_certificates"][0]["errors"] = []
    C.append(("OVERTURNED_with_no_errors", "REJECT", m_overturned_noerr))

    def m_agent(d): d["identity"]["agent_id"] = "NotOnRoster"
    C.append(("agent_id_not_in_ROSTER", "REJECT", m_agent))

    def m_premise_noexcl(d):
        d["autopsy"]["fair_test"]["verdict"] = "FAIR"
        for L in ("DESIGN", "IMPLEMENTATION", "CONFIGURATION", "EXECUTION",
                  "INSTRUMENTATION", "MEASUREMENT", "INTERPRETATION", "ECOSYSTEM"):
            stack(d)[L] = {"verdict": "VALID", "finding": "synthetic valid layer",
                           "evidence": ["dossiers/coeus_evidence/coeus_attacks.py"], "cause_classes": []}
        stack(d)["HYPOTHESIS"]["cause_classes"] = ["PREMISE_FAILURE"]
        d["autopsy"]["primary_cause"] = "PREMISE_FAILURE"; d["autopsy"]["contributing_causes"] = []
        d["autopsy"].pop("premise_exclusion", None)
    C.append(("PREMISE_FAILURE_without_premise_exclusion", "REJECT", m_premise_noexcl))

    # ---- CHEATS: doctrine says these should not pass; the validator is not known to check them
    def c_hallucinated_path(d): stack(d)["DESIGN"]["evidence"] = ["dossiers/coeus_evidence/does_not_exist_anywhere.py"]
    C.append(("hallucinated_evidence_path", "CHEAT", c_hallucinated_path))

    def c_empty_kill_boundary(d): d["autopsy"]["kill_boundary"] = ""
    C.append(("empty_kill_boundary", "CHEAT", c_empty_kill_boundary))

    def c_empty_survivors_not_corpse(d): d["autopsy"]["surviving_claims"] = []
    C.append(("empty_surviving_claims_without_TRUE_CORPSE", "CHEAT", c_empty_survivors_not_corpse))

    def c_nonlb_by_assertion(d):
        d["autopsy"]["fair_test"]["verdict"] = "FAIR"
        for name in ("DESIGN", "IMPLEMENTATION", "CONFIGURATION", "EXECUTION", "INSTRUMENTATION", "MEASUREMENT"):
            L = stack(d)[name]
            if L["verdict"] == "INVALID":
                L["load_bearing"] = False; L["evidence"] = ["dossiers/coeus_evidence/README.md"]
            elif L["verdict"] == "NOT_EXAMINED":
                L["verdict"] = "VALID"; L["evidence"] = ["dossiers/coeus_evidence/README.md"]; L["cause_classes"] = []
    C.append(("non_load_bearing_by_assertion_makes_FAIR", "CHEAT", c_nonlb_by_assertion))

    def c_all_not_reviewed(d):
        for dc in d["autopsy"]["death_certificates"]:
            dc["review"] = "NOT_REVIEWED"; dc.pop("errors", None)
    C.append(("every_certificate_NOT_REVIEWED", "CHEAT", c_all_not_reviewed))

    def c_evidence_is_readme_only(d):
        for L in stack(d).values():
            if L["verdict"] in ("VALID", "INVALID"): L["evidence"] = ["dossiers/coeus_evidence/README.md"]
    C.append(("all_evidence_is_prose_README", "CHEAT", c_evidence_is_readme_only))

    def c_fair_scope_missing(d): d["autopsy"]["fair_test"].pop("scope", None)
    C.append(("fair_test_without_scope", "CHEAT", c_fair_scope_missing))

    def c_ne_everything_needs_more(d):
        for L in stack(d).values():
            L["verdict"] = "NOT_EXAMINED"; L["evidence"] = []; L["cause_classes"] = []; L.pop("load_bearing", None)
        d["autopsy"]["fair_test"]["verdict"] = "UNDETERMINED"
        d["autopsy"]["primary_cause"] = "UNDETERMINED"; d["autopsy"]["contributing_causes"] = []
        d["disposition"]["classification"] = "REPRESENTATION_FAILURE"
    C.append(("all_NOT_EXAMINED_but_classified_REPRESENTATION_FAILURE", "CHEAT", c_ne_everything_needs_more))
    return C


def run_case(name, kind, mutator, results):
    tmp = tempfile.mkdtemp(prefix="necro_neg_")
    dst = os.path.join(tmp, "necropolis")
    shutil.copytree(NECRO, dst, ignore=shutil.ignore_patterns("__pycache__", "tests"))
    # keep only the base dossier + its evidence so in-progress files from other passes cannot confound the run
    ddir = os.path.join(dst, "dossiers")
    for f in os.listdir(ddir):
        if f.endswith(".json") and f != BASE_DOSSIER and not f.startswith("_"):
            os.remove(os.path.join(ddir, f))
    # remove monsters so the organ checks do not fire for unrelated reasons (organs come from the pruned dossiers)
    for f in os.listdir(os.path.join(dst, "monsters")):
        if f.startswith("FRANK-"): os.remove(os.path.join(dst, "monsters", f))
    path = os.path.join(ddir, BASE_DOSSIER)
    d = json.load(open(path, encoding="utf-8"))
    if mutator is not None:
        mutator(d)
    json.dump(d, open(path, "w", encoding="utf-8"), indent=1)
    # validate.py regenerates ORGANS.jsonl / COUNTERFACTUAL_HISTORY.jsonl in place and reports STALE on the
    # run that regenerates them; the judgement is the SECOND run, when only the mutation can fail it.
    subprocess.run([sys.executable, os.path.join(dst, "validate.py")], capture_output=True, text=True)
    p = subprocess.run([sys.executable, os.path.join(dst, "validate.py")], capture_output=True, text=True)
    caught = p.returncode != 0
    rel = [l.strip() for l in p.stdout.splitlines() if l.strip().startswith("- [")]
    if kind == "REJECT":
        verdict = "OK" if caught else "MISSED"
    elif kind == "CHEAT":
        verdict = "CAUGHT" if caught else "PASSES_UNCHECKED"
    else:
        verdict = "GREEN" if not caught else "RED"
    results.append({"case": name, "kind": kind, "rejected": caught, "errors": rel[:6], "verdict": verdict})
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    out = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    results = []
    run_case("control_unmutated", "CONTROL", None, results)
    for name, kind, m in mutate_cases():
        run_case(name, kind, m, results)
    summary = {
        "base_dossier": BASE_DOSSIER,
        "reject_cases": sum(1 for r in results if r["kind"] == "REJECT"),
        "reject_caught": sum(1 for r in results if r["kind"] == "REJECT" and r["rejected"]),
        "cheat_cases": sum(1 for r in results if r["kind"] == "CHEAT"),
        "cheat_passes_unchecked": sum(1 for r in results if r["kind"] == "CHEAT" and not r["rejected"]),
        "control_green": [r for r in results if r["kind"] == "CONTROL"][0]["rejected"] is False,
        "results": results,
    }
    print(json.dumps(summary, indent=1))
    if out:
        json.dump(summary, open(out, "w", encoding="utf-8"), indent=1)
    return 0 if summary["control_green"] and summary["reject_caught"] == summary["reject_cases"] else 1


if __name__ == "__main__":
    sys.exit(main())
