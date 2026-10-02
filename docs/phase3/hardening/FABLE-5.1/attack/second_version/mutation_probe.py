"""Mutation probe of the harness: one change to gate logic per copy; do the unit tests notice?

    python -B mutation_probe.py         about three minutes; writes RECEIPT_mutation_probe.json

Each change is applied to a copy of the harness in a temporary folder and the unit tests are run on
the copy. A change the tests do not notice SURVIVES. The first 25 (R01 to R25) are the changes the
adversarial reader of this package made to the first version of the harness, carried over to the
revised code; 22 of those 25 survived the first version's tests. The rest (A26 onward) are the
author's. Exit code 0 if no change survives other than those listed in EQUIVALENT.
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ENV = dict(os.environ, RSO_COUNTERFEIT=str(HERE.parents[1].parent / "review" / "FABLE-5.1" / "counterfeit"))
# Changes that alter no verdict: the tests cannot notice them and need not.
EQUIVALENT = {"R14": "both branches return FAIL; only the reason text differs"}

M = [
    # ---- the reader's 25, carried over
    ("R01 G6.restart: keep the answer, drop the trajectory and the final state", "torture.py", [
        ('if (whole["answer"], whole["trace"][at + 1:], whole["final"]) != (cut["answer"], cut["trace"][at + 1:],\n'
         '                                                                             cut["final"]):',
         'if whole["answer"] != cut["answer"]:')]),
    ("R02 G6.reset: compare answers only", "torture.py", [
        ('return r["answer"], r["trace"], r["final"][0], r["final"][1]', 'return (r["answer"],)')]),
    ("R03 G1.cell: attainability floor 0.99 -> 0.90", "registration.py", [
        ("def attainability(table, known_answers, floor=stats.POWER_FLOOR):",
         "def attainability(table, known_answers, floor=0.90):")]),
    ("R04 G2.preflight: POWER_FLOOR 0.99 -> 0.50", "stats.py", [("POWER_FLOOR = 0.99 ", "POWER_FLOOR = 0.50 ")]),
    ("R05 G2.preflight: drop the check on the negative's answer", "stats.py", [
        ("    if 1 - alpha < floor:", "    if False:")]),
    ("R06 G7.report: drop the positive-control check", "search.py", [("        if control < 0.99:", "        if False:")]),
    ("R07 G7.report: repeated founders accepted", "search.py", [
        ('if len(set(p["seeds"])) != len(p["seeds"]) or not p["seeds"]:', 'if not p["seeds"]:')]),
    ("R08 G7.calibration: one-sided (only too-low counts are caught)", "stats.py", [
        ("return tail_ge(n, k, p) > alpha / 2 and tail_le(n, k, p) > alpha / 2", "return tail_ge(n, k, p) > alpha / 2")]),
    ("R09 G9.clauses: ignore clauses that can never hold", "audits.py", [
        ("    if cannot_fail or cannot_hold:", "    if cannot_fail:")]),
    ("R10 G1.receipt: a run up to 49 ticks before its registration is accepted", "registration.py", [
        ('if receipt["ran_at"] < cell["registered_at"]:', 'if receipt["ran_at"] < cell["registered_at"] - 49:')]),
    ("R11 G12.render: no cell needed", "claims.py", [
        ('if not setting or not cell or not claim.get("setting_sha256"):',
         'if not setting or not claim.get("setting_sha256"):')]),
    ("R12 G8.demand: only the constant baseline is required", "torture.py", [
        ('REQUIRED_BASELINES = ("CONSTANT", "CLOCK", "KEY_READER", "WORLD_PARKER", "TABLE")',
         'REQUIRED_BASELINES = ("CONSTANT",)')]),
    ("R13 G10.ruler: a ruler with no known negative is accepted", "audits.py", [
        ('    if not seen["NEGATIVE"]:', "    if False:")]),
    ("R14 G10.contrast: cells that do not differ in the named variable pass", "audits.py", [
        ("    if named not in differ:", "    if False:")]),
    ("R15 G1.cell: overlapping rules in a verdict table accepted", "registration.py", [
        ("        if len(got) != 1:", "        if len(got) < 1:")]),
    ("R16 G1.cell: adapter and independent_unit no longer required", "registration.py", [
        ('"adapter", "independent_unit", "registered_seeds",', '"registered_seeds",')]),
    ("R17 G11.custody: the two clock fields no longer required", "claims.py", [
        ('"rule_fixed_at", "confirmation_opened_at", "discovery_custodian"', '"discovery_custodian"')]),
    ("R18 G5.neutrality: declared valid in a physics with no known answer passes", "rulers.py", [
        ("    if outside:", "    if False and outside:")]),
    ("R19 rulers: ALPHA 1e-6 -> 0.4", "rulers.py", [("ALPHA = 1e-6", "ALPHA = 0.4")]),
    ("R20 world: the mark is not cleared between episodes", "retain1.py", [
        ("        if not self.keep_mark:\n            self.mark = None", "        if False:\n            self.mark = None")]),
    ("R21 G9.sham: margin 25% -> 60%", "audits.py", [
        ("def audit_sham(reps, clause_row, margin=0.25, slack=1):", "def audit_sham(reps, clause_row, margin=0.60, slack=1):")]),
    ("R22 G9.arms: arms count as one series only if equal in every replicate", "audits.py", [
        (">= min(same_at, len(reps)):", ">= len(reps):")]),
    ("R23 G12.promote: L2 no longer needs custody and a second implementation", "claims.py", [
        ('L2 = ("exact_null", "attack_round", "custody", "second_implementation")', 'L2 = ("exact_null", "attack_round")')]),
    ("R24 G7.report: any bound is accepted", "search.py", [
        ("        elif not zero_hit_upper(n) - 5e-5 <= bound <= 1:", "        elif False:")]),
    ("R25 rulers: BOUND 0.5 -> 0.7", "rulers.py", [("BOUND = 0.5 ", "BOUND = 0.7 ")]),
    # ---- further changes
    ("A26 classify: the inverted outcome removed", "stats.py", [("    if exact_rate:", "    if False:")]),
    ("A27 rulers: weakest registered positive 15/16 -> 0.99", "rulers.py", [("P_WEAKEST = 15 / 16", "P_WEAKEST = 0.99")]),
    ("A28 rulers: a shared ruler needs two physics, not three", "rulers.py", [("MIN_PHYSICS = 3", "MIN_PHYSICS = 2")]),
    ("A29 G4.entry: the declared physics is not checked", "rulers.py", [
        ('if getattr(cls, "physics", None) != physics]', 'if False]')]),
    ("A30 G6.observer: the final state is not compared", "torture.py", [
        ("else (off == on)", 'else (off["trace"] == on["trace"] and off["answer"] == on["answer"])')]),
    ("A31 equivalence: a rate below the center is never OUTSIDE", "stats.py", [
        ("    if tail_ge(n, k, center) <= alpha / 2 or tail_le(n, k, center) <= alpha / 2:",
         "    if tail_ge(n, k, center) <= alpha / 2:")]),
    ("A32 G8.demand: margin 0.1 -> 0.3", "torture.py", [("MARGIN = 0.1 ", "MARGIN = 0.3 ")]),
    ("A33 G11.custody: a rule fixed at the tick the data was opened is accepted", "claims.py", [
        ('if record["rule_fixed_at"] >= record["confirmation_opened_at"]:',
         'if record["rule_fixed_at"] > record["confirmation_opened_at"]:')]),
    ("A34 G11.custody: tuning exactly at budget is refused", "claims.py", [
        ('if record["tuning_evaluations"] > record["tuning_budget"]:',
         'if record["tuning_evaluations"] >= record["tuning_budget"]:')]),
    ("A35 G12: a facet needs no source", "claims.py", [('    if not f.get("source"):', "    if False:")]),
    ("A36 G12: a nested claim needs only a retention certificate", "claims.py", [
        ('"NESTED": ("retention_at_boundary", "mediation", "cargo_control", "flattened_twin"),',
         '"NESTED": ("retention_at_boundary",),')]),
    ("A37 G7.report: a discovery with nothing found is accepted", "search.py", [("        if total == 0:", "        if False:")]),
    ("A38 G7.report: any two policies make a null", "search.py", [
        ('if len(report["policies"]) < 2 or "CROSSES_NEUTRAL_STEPS" not in kinds:', 'if len(report["policies"]) < 2:')]),
    ("A39 G9.clauses: isolation is not required", "audits.py", [("    if not_isolated:", "    if False:")]),
    ("A40 G10.setting: any probability counts as power", "audits.py", [("0.99 <= v <= 1.0", "0.0 <= v <= 1.0")]),
    ("A41 G1.cell: repeated registered seeds accepted", "registration.py", [
        ("    if len(set(seeds)) != len(seeds):", "    if False:")]),
    ("A42 G1.receipt: the code on hand is not hashed", "registration.py", [
        ('    if sha(source) != cell["source_sha256"]:', "    if False:")]),
    ("A43 G6.restart: restore into a runtime that has never run", "torture.py", [
        ('            World().episode(used, seed, force_bit=1 - whole["bit"])\n', "")]),
    ("A44 G6.restart: cut at step 3 only", "torture.py", [
        ('        for at in range(len(whole["trace"]) - 1):', "        for at in (3,):")]),
    ("A45 G6.reset: only a later episode with no cue is tried", "torture.py", [
        ("        for cue in (None, 0, 1):", "        for cue in (None,):")]),
    ("A46 ladder: the certificate has no margin", "ladder.py", [
        ("threshold = H16 + N * sqrt(log(1 / alpha) / (2 * n))", "threshold = H16")]),
    ("A47 classify: the critical count itself does not exclude", "stats.py", [
        ("    if successes >= hi:", "    if successes > hi:")]),
    ("A48 G9.sham: slack of five tasks", "audits.py", [
        ("def audit_sham(reps, clause_row, margin=0.25, slack=1):", "def audit_sham(reps, clause_row, margin=0.25, slack=5):")]),
    ("A49 G10.ruler: a wrong answer on a kit member is not a failure", "audits.py", [
        ("        elif got != answers[claim]:", "        elif False:")]),
    ("A50 G10.ruler: unbuilt members are ignored", "audits.py", [("    if never:", "    if False:")]),
    ("A51 G3: the weak positive is not needed", "rulers.py", [("    if weak is None or not blocks:", "    if False:")]),
    ("A52 G12.render: the setting need not be the registered one", "claims.py", [
        ('    if setting_hash(setting) != claim["setting_sha256"]:', "    if False:")]),
    ("A53 G1.cell: design seeds may be registered for confirmation", "registration.py", [
        ("    if shared:", "    if False:")]),
    ("A54 G5: an undecided answer counts as agreement", "rulers.py", [
        ('    if got == "UNDECIDED":\n        return Result(what, INDETERMINATE,', '    if got == "UNDECIDED":\n        return Result(what, PASS,')]),
    ("A55 interchange: the sham pairs are skipped", "rulers.py", [
        ("            for sham in (False, True):", "            for sham in (False,):")]),
]


def one(job):
    out, i, (name, fname, edits) = job
    d = out / ("m%02d" % i)
    shutil.copytree(HERE, d, ignore=shutil.ignore_patterns("__pycache__", "RECEIPT_*.json", "mutation_probe.py"))
    p = d / "rso_harness" / fname
    s = p.read_text(encoding="ascii")
    for old, new in edits:
        if s.count(old) != 1:
            return name, "PATTERN_NOT_FOUND"
        s = s.replace(old, new)
    p.write_text(s, encoding="ascii", newline="\n")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover"], cwd=str(d), capture_output=True, text=True,
                       env=ENV)
    return name, "noticed" if r.returncode != 0 else "SURVIVES"


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main():
    out = pathlib.Path(tempfile.mkdtemp(prefix="rso_mutation_"))
    try:
        base = one((out, 0, ("unchanged copy", "stats.py", [])))
        if base[1] != "SURVIVES":
            print("the unchanged copy does not pass its own tests")
            return 1
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(one, [(out, i, m) for i, m in enumerate(M, 1)]))
    finally:
        shutil.rmtree(out, ignore_errors=True)
    survived = [n for n, s in results if s == "SURVIVES"]
    lost = [n for n, s in results if s == "PATTERN_NOT_FOUND"]
    reader = [(n, s) for n, s in results if n.startswith("R")]
    unexplained = [n for n in survived if n[:3] not in EQUIVALENT]
    modules = sorted((HERE / "rso_harness").glob("*.py")) + [HERE / "tests" / "test_harness.py",
                                                             HERE / "mutation_probe.py"]
    receipt = {
        "what": "mutation probe of reference harness v0: one change to gate logic per copy, unit tests run on the copy",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "changes": len(results), "noticed": sum(1 for _, s in results if s == "noticed"), "survived": survived,
        "pattern_not_found": lost,
        "readers_changes": len(reader), "readers_changes_survived": [n for n, s in reader if s == "SURVIVES"],
        "readers_changes_that_survived_the_first_version": 22,
        "equivalent": EQUIVALENT, "results": [{"change": n, "result": s} for n, s in results],
        "source_sha256_lf": {p.relative_to(HERE).as_posix(): sha(p) for p in modules},
    }
    (HERE / "RECEIPT_mutation_probe.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                                                      encoding="ascii", newline="\n")
    for n, s in results:
        print("%-9s %s" % (s, n))
    print("changes %d, noticed %d, survived %d %s, pattern not found %d"
          % (len(results), receipt["noticed"], len(survived), survived, len(lost)))
    return 0 if not unexplained and not lost else 1


if __name__ == "__main__":
    sys.exit(main())
