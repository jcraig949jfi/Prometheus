"""Mutation probe of the harness: one change to gate logic per copy; do the unit tests notice?

    python -B mutation_probe.py         several minutes; writes RECEIPT_mutation_probe.json

Each change is applied to a copy of the harness in a temporary folder and the unit tests are run on
the copy. A change the tests do not notice SURVIVES.

Seven sets of changes, each carried over to the current code:

    R   25   made by the first adversarial reader to the first version of the harness
    A   30   made by the author while rewriting it
    C   44   made by the closure reader to the second version
    F   32   made by the second reader to the second version
    H   36   made by the second reader's fork to the second version
    X   26   made by the closure reader to the third version, in the final round
    Y   54   made by the second reader to the third version, before it had opened the tests

Where the code a change touched no longer exists, the nearest change is made and the entry says so;
where none is possible the entry is listed as GONE and not run.

What the figures mean. FIRST_SIGHT is what each reader measured on the version it attacked, before
any test had been written against its changes. It is copied from the readers' reports and is not
measured again here. It is the only figure in this file that says how good the tests are. The count
this probe prints is taken on changes the tests were then extended to notice, and says only that
those holes are closed. Exit code 0 if no change survives other than those listed in EQUIVALENT.
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
sys.path.insert(0, str(HERE))
from mutation_sets_final import FINAL  # noqa: E402

ENV = dict(os.environ, RSO_COUNTERFEIT=os.environ.get("RSO_COUNTERFEIT") or str(
    HERE.parents[1].parent / "review" / "FABLE-5.1" / "counterfeit"))
SETS = {"R": "first reader, on the first version", "A": "author", "C": "closure reader, on the second version",
        "F": "second reader, on the second version", "H": "second reader's fork, on the second version",
        "X": "closure reader, on the third version", "Y": "second reader, on the third version"}
# Changes written by a reader, and how many of them the tests of the day did not notice.
FIRST_SIGHT = {"R": {"changes": 25, "unnoticed": 22}, "C": {"changes": 44, "unnoticed": 34},
               "F": {"changes": 32, "unnoticed": 20}, "H": {"changes": 36, "unnoticed": 26},
               "X": {"changes": 26, "unnoticed": 12}, "Y": {"changes": 54, "unnoticed": 20}}
# Changes that alter no verdict on any input: the tests cannot notice them and need not.
EQUIVALENT = {
    "R14": "both branches return FAIL; only the reason text differs",
    "C18": "the mark at every step is in the trajectory, and a mark written at the last step is the answer",
    "C36": "each level's requirement includes every lower level's, so no level can be skipped",
    "F22": "the value is already held to one of two words, so the two tests are the same test",
    "H19": "the same change as F22",
    "F32": "the next branch judges an inverted impostor against NEGATIVE and returns FAIL as well",
    "Y03": "a count that excludes the class is never called NEGATIVE either way; the reader proved it and tried "
           "2,730 inputs",
    "Y21": "the same change as C18",
}
SAME_AT = "def coincident(reps, arms, same_at=HOLDS_AT):"
PLACEHOLDERS = 'PLACEHOLDERS = ("", "tbd", "todo", "n/a", "na", "none", "unknown", "not computed", "?")'    # in stats.py
L1 = 'L1 = ("registration", "power", "detection", "demand", "independence", "exposure", "resources")'
L2 = 'L2 = ("exact_null", "attack_round", "custody", "second_implementation")'
RANK = "_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 2, INDETERMINATE: 1, PASS: 0}"
GENERATOR = '    if record["claim"] == "NEW_FAMILY" and d["generator_sha256"] == c["generator_sha256"]:'
IS_COUNT = "    return isinstance(v, int) and not isinstance(v, bool) and v >= 0"
SEEDS_ARE_THE_REGISTERED = 'if sorted(p["seeds"]) != sorted(seeds):'
EXPOSURE = 'is_count(exposure.get("tuning_evaluations"))'

M = [
    # ---- R: the first reader's 25
    ("R01 G6.restart: keep the answer, drop the trajectory and the final state", "torture.py", [
        ('(whole["answer"], whole["trace"][at + 1:], whole["final"]) != (cut["answer"], cut["trace"][at + 1:],',
         '(whole["answer"], 0, 0) != (cut["answer"], 0,'),
        ('cut["final"]):', "0):")]),
    ("R02 G6.reset: compare answers only", "torture.py", [
        ('return r["answer"], r["trace"], r["final"][0], r["final"][1]', 'return (r["answer"],)')]),
    ("R03 G1.cell: attainability floor 0.99 -> 0.90", "registration.py", [
        ("def attainability(table, known_answers, floor=stats.POWER_FLOOR):",
         "def attainability(table, known_answers, floor=0.90):")]),
    ("R04 G2.preflight: POWER_FLOOR 0.99 -> 0.50", "stats.py", [("POWER_FLOOR = 0.99 ", "POWER_FLOOR = 0.50 ")]),
    ("R05 G2.preflight: drop the check on alpha", "stats.py", [("    if 1 - alpha < floor:", "    if False:")]),
    ("R06 G7.report: drop the positive-control check", "search.py", [
        ("            if control < 0.99:", "            if False:")]),
    ("R07 G7.report: the founders reported need not be the founders registered (was: repeated founders accepted)",
     "search.py", [(SEEDS_ARE_THE_REGISTERED, "if False:")]),
    ("R08 G7.calibration: one-sided (only too-low counts are caught)", "stats.py", [
        ("return tail_ge(n, k, p) > alpha / 2 and tail_le(n, k, p) > alpha / 2", "return tail_ge(n, k, p) > alpha / 2")]),
    ("R09 G9.clauses: ignore clauses that can never hold", "audits.py", [
        ("    if cannot_fail or cannot_hold:", "    if cannot_fail:")]),
    ("R10 G1.receipt: a run up to 49 ticks before its registration is accepted", "registration.py", [
        ('if receipt["ran_at"] < cell["registered_at"]:', 'if receipt["ran_at"] < cell["registered_at"] - 49:')]),
    ("R11 G12.render: no cell needed", "claims.py", [
        ('if not setting or not cell or not excluded or not claim.get("setting_sha256"):',
         'if not setting or not excluded or not claim.get("setting_sha256"):')]),
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
        ("def audit_sham(reps, clause_row, margin=0.25, slack=1):",
         "def audit_sham(reps, clause_row, margin=0.60, slack=1):")]),
    ("R22 G9.arms: arms count as one series only if equal in every replicate", "audits.py", [
        (">= same_at:", ">= len(reps):")]),
    ("R23 G12.promote: L2 no longer needs custody and a second implementation", "claims.py", [
        (L2, 'L2 = ("exact_null", "attack_round")')]),
    ("R24 G7.report: any bound is accepted", "search.py", [
        ("        elif not _number(bound) or not zero_hit_upper(n) - 5e-5 <= bound < 1:", "        elif False:")]),
    ("R25 rulers: BOUND 0.5 -> 0.7", "rulers.py", [("BOUND = 0.5 ", "BOUND = 0.7 ")]),
    # ---- A: the author's 30
    ("A26 classify: the inverted outcome removed", "stats.py", [("    if exact_rate:", "    if False:")]),
    ("A27 rulers: weakest registered positive 15/16 -> 0.99", "rulers.py", [("P_WEAKEST = 15 / 16", "P_WEAKEST = 0.99")]),
    ("A28 rulers: a shared ruler needs two physics, not three", "rulers.py", [("MIN_PHYSICS = 3", "MIN_PHYSICS = 2")]),
    ("A29 G4.entry: the declared physics is not checked", "rulers.py", [
        ('if getattr(cls, "physics", None) != physics]', 'if False]')]),
    ("A30 G6.observer: the final state is not compared", "torture.py", [
        ("else (a == b)", 'else (a["trace"] == b["trace"] and a["answer"] == b["answer"])')]),
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
    ("A35 G12: a facet needs no source", "claims.py", [
        ('    if not isinstance(f.get("source"), str) or not f["source"].strip():', "    if False:")]),
    ("A36 G12: a nested claim needs only a retention certificate", "claims.py", [
        ('"NESTED": ("retention_at_boundary", "mediation", "cargo_control", "flattened_twin"),',
         '"NESTED": ("retention_at_boundary",),')]),
    ("A37 G7.report: a discovery with nothing found is accepted", "search.py", [
        ("        if total == 0:", "        if False:")]),
    ("A38 G7.report: any two policies make a null", "search.py", [
        ('if len(report["policies"]) < 2 or "CROSSES_NEUTRAL_STEPS" not in kinds:',
         'if len(report["policies"]) < 2:')]),
    ("A39 G9.clauses: isolation is not required", "audits.py", [("    if not_isolated:", "    if False:")]),
    ("A40 G10.setting: any probability counts as power", "audits.py", [("0.99 <= v <= 1.0", "0.0 <= v <= 1.0")]),
    ("A41 G1.cell: repeated seeds accepted", "registration.py", [
        ("    if len(set(seeds)) != len(seeds) or len(set(design)) != len(design):", "    if False:")]),
    ("A42 G1.receipt: the code on hand is not hashed", "registration.py", [
        ('    if sha(source) != cell["source_sha256"]:', "    if False:")]),
    ("A43 G6.restart: restore into a runtime that has never run", "torture.py", [
        ('            World().episode(used, seed, force_bit=1 - whole["bit"])\n', "")]),
    ("A44 G6.restart: cut at step 3 only", "torture.py", [
        ('        for at in range(len(whole["trace"])):', "        for at in (3,):")]),
    ("A45 G6.reset: only a later episode with no cue is tried", "torture.py", [
        ("        for cue in (None, 0, 1):", "        for cue in (None,):")]),
    ("A46 ladder: the certificate has no margin", "ladder.py", [
        ("threshold = H16 + N * sqrt(log(1 / alpha) / (2 * n))", "threshold = H16")]),
    ("A47 classify: the critical count itself does not exclude", "stats.py", [
        ("    if successes >= hi:", "    if successes > hi:")]),
    ("A48 G9.sham: slack of five tasks", "audits.py", [
        ("def audit_sham(reps, clause_row, margin=0.25, slack=1):",
         "def audit_sham(reps, clause_row, margin=0.25, slack=5):")]),
    ("A49 G10.ruler: a wrong answer on a kit member is not a failure", "audits.py", [
        ("        elif got != answers[claim]:", "        elif False:")]),
    ("A50 G10.ruler: unbuilt members are ignored", "audits.py", [("    if never:", "    if False:")]),
    ("A51 G3: the weak positive, the further blocks and the thresholds are not needed", "rulers.py", [
        ("    if weak is None or not blocks or not edges:", "    if False:")]),
    ("A52 G12.render: the setting need not be the registered one", "claims.py", [
        ('    if setting_hash(setting) != claim["setting_sha256"]:', "    if False:")]),
    ("A53 G1.cell: design seeds may be registered for confirmation", "registration.py", [
        ("    if shared:", "    if False:")]),
    ("A54 G5: an undecided answer counts as agreement", "rulers.py", [
        ('    if got == "UNDECIDED":\n        return Result(what, INDETERMINATE,',
         '    if got == "UNDECIDED":\n        return Result(what, PASS,')]),
    ("A55 interchange: the pairs with the same cue are skipped", "rulers.py", [
        ("            for recipient_bit in (1 - donor_bit, donor_bit):",
         "            for recipient_bit in (1 - donor_bit,):")]),
    # ---- C: the closure reader's 44
    ("C01 classify: a score AT the lower critical count is no longer INVERTED", "stats.py", [
        ("        if low is not None and successes <= low:", "        if low is not None and successes < low:")]),
    ("C02 equivalence: WITHIN needs only one of the two one-sided tests", "stats.py", [
        ('    return "WITHIN" if above and below else "UNDECIDED"',
         '    return "WITHIN" if above or below else "UNDECIDED"')]),
    ("C03 calibration test at alpha, not alpha/2 per side", "stats.py", [
        ("    return tail_ge(n, k, p) > alpha / 2 and tail_le(n, k, p) > alpha / 2",
         "    return tail_ge(n, k, p) > alpha and tail_le(n, k, p) > alpha")]),
    ("C04 design rates used at a 90% lower bound, not 99%", "stats.py", [
        ("DESIGN_CONFIDENCE = 0.99 ", "DESIGN_CONFIDENCE = 0.90 ")]),
    ("C05 G1.cell: design counts need only be integers (was: a rate given as True/False is accepted)",
     "registration.py", [
         ('if outcome not in table["outcomes"] or not is_count(h) or not is_count(n) or n == 0 or h > n:',
          'if outcome not in table["outcomes"] or not isinstance(h, int) or not isinstance(n, int) or n == 0 '
          'or h > n:')]),
    ("C06 G1.cell: a negative count of tuning evaluations is accepted", "registration.py", [
        (EXPOSURE, 'isinstance(exposure.get("tuning_evaluations"), int)')]),
    ("C07 G1.receipt: a receipt need not carry the time it ran", "registration.py", [
        ('missing = [k for k in ("source_sha256", "seeds", "ran_at") if receipt.get(k) in (None, "", [])]',
         'missing = [k for k in ("source_sha256", "seeds") if receipt.get(k) in (None, "", [])]')]),
    ("C08 G1.cell: one known answer is enough", "registration.py", [
        ("    if not isinstance(known_answers, dict) or len(known_answers) < 2:",
         "    if not isinstance(known_answers, dict) or len(known_answers) < 1:")]),
    ("C09 G4.entry: the preflight is not run", "rulers.py", [("    if pre.verdict != PASS:", "    if False:")]),
    ("C10 G5: a ruler declared valid nowhere is not blocked", "rulers.py", [("    if not declared:", "    if False:")]),
    ("C11 interchange: the state is moved at step 5, not 3", "rulers.py", [
        ("def _interchange(make, seeds, grab, put, at=3):", "def _interchange(make, seeds, grab, put, at=5):")]),
    ("C12 G3: impostors are judged on the first further block only", "rulers.py", [
        ("        for i, block in enumerate([seeds] + list(blocks)):",
         "        for i, block in enumerate([seeds] + list(blocks)[:1]):")]),
    ("C13 G5: a shared ruler is judged on the first three physics of the panel", "rulers.py", [
        ("        out = judge(known)", "        out = judge(known[:3])")]),
    ("C14 G4.entry: an impostor that beats the bound is INDETERMINATE, not FAIL", "rulers.py", [
        ('        found.append(Result("impostor", FAIL, "the impostor beats the exact bound: it is no impostor, '
         'or the world leaks"))',
         '        found.append(Result("impostor", INDETERMINATE, "the impostor beats the exact bound"))')]),
    ("C15 G6.observer: only the first seed is compared", "torture.py", [
        ("    for seed, a, b in zip(seeds, off, on):", "    for seed, a, b in list(zip(seeds, off, on))[:1]:")]),
    ("C16 G6.reset: only the first seed is checked", "torture.py", [
        ("    for seed in seeds:\n        for cue in (None, 0, 1):",
         "    for seed in seeds[:1]:\n        for cue in (None, 0, 1):")]),
    ("C17 G6.restart: only the first seed is checked", "torture.py", [
        ("    for seed in seeds:\n        whole = World().episode(make(), seed)",
         "    for seed in seeds[:1]:\n        whole = World().episode(make(), seed)")]),
    ("C18 G6.reset: the mark left on the environment is not compared", "torture.py", [
        ('return r["answer"], r["trace"], r["final"][0], r["final"][1]',
         'return r["answer"], r["trace"], r["final"][0]')]),
    ("C19 G6.restart: the last cut point is not tried", "torture.py", [
        ('        for at in range(len(whole["trace"])):', '        for at in range(len(whole["trace"]) - 1):')]),
    ("C20 G8.demand: alpha 1e-6 -> 1e-3", "torture.py", [
        ("def demand_closure(seeds, train_seeds, baselines=None, alpha=DEMAND_ALPHA, margin=MARGIN, **world):",
         "def demand_closure(seeds, train_seeds, baselines=None, alpha=1e-3, margin=MARGIN, **world):")]),
    ("C21 G8.demand: an UNDECIDED baseline does not stop a PASS", "torture.py", [
        ("    if open_ or unfitted:", "    if unfitted:")]),
    ("C22 G7.report: a report with missing fields is not blocked", "search.py", [("    if missing:", "    if False:")]),
    ("C23 G7.report: the same change as R07 in this version (was: a policy with no founders is accepted)",
     "search.py", [(SEEDS_ARE_THE_REGISTERED, "if False:")]),
    ("C24 G7.report: the positive control need only reach 0.5", "search.py", [
        ("            if control < 0.99:", "            if control < 0.5:")]),
    ("C25 G7.report: a repair claim needs no repair start", "search.py", [
        ('        if law != "REPAIR":', "        if False:")]),
    ("C26 G7.report: the bound is held to the largest founder count among the policies", None,
     "GONE: the gate now counts the registered founders, and there is one list of them"),
    ("C27 G7.report: an unknown claim passes", "search.py", [
        ('        return Result(gate, BLOCKED, "unknown claim or start law: %r, %r" % (claim, laws))',
         '        return Result(gate, PASS, "unknown claim or start law: %r, %r" % (claim, laws))')]),
    ("C28 G7.report: an unregistered landscape is not blocked", "search.py", [
        ("if ls not in LANDSCAPES})", "if False})")]),
    ("C29 G9.clauses: a clause true in exactly 12 of 24 somewhere counts as unable to fail", "audits.py", [
        ("    cannot_fail = sorted(c for c in names if min(table[c].values()) > FAILS_AT)",
         "    cannot_fail = sorted(c for c in names if min(table[c].values()) >= FAILS_AT)")]),
    ("C30 G10.setting: the amortization horizon need not be a count", "audits.py", [
        ('        elif k == "amortization_horizon" and not (_number(v) and v == int(v) and v >= 1):',
         "        elif False:")]),
    ("C31 G10.setting: the effect threshold need not be a number", "audits.py", [
        ('        elif k == "effect_threshold" and not (_number(v) and v > 0):', "        elif False:")]),
    ("C32 G10.ruler: a ruler with no known positive is accepted", "audits.py", [
        ('    if not seen["POSITIVE"]:', "    if False:")]),
    ("C33 G10.setting: 'n/a' and 'unknown' count as registered", "stats.py", [
        (PLACEHOLDERS, 'PLACEHOLDERS = ("", "tbd")')]),
    ("C34 G9.sham: a sham clause is unable to fail only if it holds in every replicate of every cell", "audits.py", [
        ("    if min(clause_row.values()) > FAILS_AT:", "    if min(clause_row.values()) >= N:")]),
    ("C35 G11: a confirmation from the same generator is refused whatever the claim", "claims.py", [
        (GENERATOR, '    if d["generator_sha256"] == c["generator_sha256"]:')]),
    ("C36 G12: a level may be skipped", "claims.py", [
        ("            best = lv\n        else:\n            break", "            best = lv\n        else:\n            continue")]),
    ("C37 G12: an ORIGIN claim needs no cold start and no class bound", "claims.py", [
        ('    "ORIGIN": ("cold_start", "class_bound"),', '    "ORIGIN": (),')]),
    ("C38 G12: a TRANSFER claim needs no new family", "claims.py", [
        ('    "TRANSFER": ("new_family",),', '    "TRANSFER": (),')]),
    ("C39 G12: L1 no longer needs the resources facet", "claims.py", [
        (L1, 'L1 = ("registration", "power", "detection", "demand", "independence", "exposure")')]),
    ("C40 G12: L2 no longer needs an attack round", "claims.py", [
        (L2, 'L2 = ("exact_null", "custody", "second_implementation")')]),
    ("C41 G12: an ECONOMY claim needs no frozen comparators", "claims.py", [
        ('    "ECONOMY": ("lifecycle_cost", "frozen_comparators"),', '    "ECONOMY": ("lifecycle_cost",),')]),
    ("C42 a boolean counts as a clock reading or a count", "stats.py", [
        (IS_COUNT, "    return isinstance(v, int) and v >= 0")]),
    ("C43 combine: nothing checked is PASS, not BLOCKED", "verdict.py", [
        ('        return Result(gate, BLOCKED, "no results to combine")',
         '        return Result(gate, PASS, "no results to combine")')]),
    ("C44 ladder: the certificate's alpha 1e-6 -> 1e-2", "ladder.py", [
        ("def certificate(per_life, alpha=1e-6):", "def certificate(per_life, alpha=1e-2):")]),
    # ---- F: the second reader's 32
    ("F01 G2: design-run lower bound at 50% confidence, not 99%", "stats.py", [
        ("DESIGN_CONFIDENCE = 0.99 ", "DESIGN_CONFIDENCE = 0.50 ")]),
    ("F02 G7.report: zero-hit bound at 50% confidence, not 95%", "stats.py", [
        ("def zero_hit_upper(n, conf=0.95):", "def zero_hit_upper(n, conf=0.50):")]),
    ("F03 G8: WITHIN shown at level 0.5", "stats.py", [
        ("    above = tail_ge(n, k, max(center - margin, 0.0)) <= alpha / 2 ",
         "    above = tail_ge(n, k, max(center - margin, 0.0)) <= 0.5 ")]),
    ("F04 G2: design rate used as a point estimate, not a lower bound", "stats.py", [
        ("max(lower_bound(design_hits, design_n), 1e-12)", "max(design_hits / design_n, 1e-12)")]),
    ("F05 G1.cell: a table that counts fewer units than seeds registered is accepted", "registration.py", [
        ('if seeds and table["n"] != len(seeds):', 'if seeds and table["n"] > len(seeds):')]),
    ("F06 G1.cell: the same change as C06 in this version (negative exposure counts accepted)", "registration.py", [
        (EXPOSURE, 'isinstance(exposure.get("tuning_evaluations"), int)')]),
    ("F07 G1.receipt: a run on a subset of the registered seeds is accepted", "registration.py", [
        ('sorted(receipt["seeds"]) != sorted(cell["registered_seeds"])',
         'set(receipt["seeds"]) - set(cell["registered_seeds"])')]),
    ("F08 G1.cell: attainability floor 0.99 -> 0.97", "registration.py", [
        ("        if p < floor:", "        if p < floor - 0.02:")]),
    ("F09 G6.reset: only one earlier cue is tried", "torture.py", [
        ("            for earlier in (0, 1, None):", "            for earlier in (0,):")]),
    ("F10 G8: equivalence at alpha 1e-3, not 1e-6", "torture.py", [
        ("stats.equivalence(k, n, 0.5, margin, alpha)", "stats.equivalence(k, n, 0.5, margin, alpha * 1000)")]),
    ("F11 G9: a conjunct HOLDS at 20 of 24, not 22", "audits.py", [
        ("N, HOLDS_AT, FAILS_AT = 24, 22, 12", "N, HOLDS_AT, FAILS_AT = 24, 20, 12")]),
    ("F12 G9: a conjunct FAILS at 16 of 24, not 12", "audits.py", [
        ("N, HOLDS_AT, FAILS_AT = 24, 22, 12", "N, HOLDS_AT, FAILS_AT = 24, 22, 16")]),
    ("F13 G10.setting: a horizon of zero later families accepted", "audits.py", [
        ("and v == int(v) and v >= 1):", "and v == int(v) and v >= 0):")]),
    ("F14 G10.setting: only '' and 'tbd' are placeholders", "stats.py", [(PLACEHOLDERS, 'PLACEHOLDERS = ("", "tbd")')]),
    ("F15 G10.setting: a threshold of zero accepted", "audits.py", [
        ("not (_number(v) and v > 0):", "not (_number(v) and v > -1):")]),
    ("F16 G9.clauses: 'the others hold' weakened to 'the others do not fail'", "audits.py", [
        ("all(table[d][cell] >= HOLDS_AT for d in names if d != c)",
         "all(table[d][cell] > FAILS_AT for d in names if d != c)")]),
    ("F17 G10.ruler: a ruler with no known positive is accepted", "audits.py", [
        ('    if not seen["POSITIVE"]:', "    if False:")]),
    ("F18 G12: an ORIGIN claim needs no class bound", "claims.py", [
        ('"ORIGIN": ("cold_start", "class_bound"),', '"ORIGIN": ("cold_start",),')]),
    ("F19 G12: an ECONOMY claim needs no extra facet", "claims.py", [
        ('"ECONOMY": ("lifecycle_cost", "frozen_comparators"),', '"ECONOMY": (),')]),
    ("F20 G12: L3 needs nothing beyond L2", "claims.py", [('L3 = ("reproduced",)', "L3 = ()")]),
    ("F21 G12: L4 needs nothing beyond L3", "claims.py", [('L4 = ("predicted",)', "L4 = ()")]),
    ("F22 G11: any selection_data other than 'confirmation' accepted", "claims.py", [
        ('    if record["selection_data"] != "discovery":', '    if record["selection_data"] == "confirmation":')]),
    ("F23 G12: a LAW claim needs no registered prediction", "claims.py", [
        ('"LAW": ("prediction_registered",),', '"LAW": (),')]),
    ("F24 G7.calibration: level 0.002 -> 0.00002", "search.py", [("CAL_ALPHA = 0.002 ", "CAL_ALPHA = 0.00002 ")]),
    ("F25 G7.report: a null with one hit is accepted", "search.py", [("        if total:", "        if total > 1:")]),
    ("F26 G7.report: a repair claim from a cold start is accepted", "search.py", [
        ('        if law != "REPAIR":', "        if False:")]),
    ("F27 G0: UNQUALIFIED ranked below INDETERMINATE", "verdict.py", [
        (RANK, "_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 1, INDETERMINATE: 2, PASS: 0}")]),
    ("F28 G3: impostors judged on the first block only", "rulers.py", [
        ("        for i, block in enumerate([seeds] + list(blocks)):", "        for i, block in enumerate([seeds]):")]),
    ("F29 G5: a shared ruler is judged on the first known physics only", "rulers.py", [
        ("        out = judge(known)", "        out = judge(known[:1])")]),
    ("F30 G11: identical panels accepted", "claims.py", [
        ('    if d["panel_sha256"] == c["panel_sha256"]:', "    if False:")]),
    ("F31 G12: a claim of unknown kind is treated as EFFECT", "claims.py", [
        ('    if claim.get("kind") not in KIND:\n        return None\n    need = list(L1) + list(KIND[claim["kind"]])',
         '    need = list(L1) + list(KIND.get(claim.get("kind"), ()))')]),
    ("F32 G4.entry: an inverted impostor is not refused", "rulers.py", [
        ('    if on_impostor == "INVERTED":', "    if False:")]),
    # ---- H: the second reader's fork, 36
    ("H01 G9.arms: one series only if equal in 23 of 24 (was 22)", "audits.py", [
        (SAME_AT, "def coincident(reps, arms, same_at=HOLDS_AT + 1):")]),
    ("H02 G9.clauses: GOOD_MAX 3.5 -> 4.5 in the run-2 clauses", "audits.py", [
        ("GOOD_MAX, BAD_MIN = 3.5, 6.0", "GOOD_MAX, BAD_MIN = 4.5, 6.0")]),
    ("H03 G9.clauses: slack 2*dev+4 -> 2*dev+8 in the sham and rescue clauses", "audits.py", [
        ('    slack = 2 * o["dev_B"] + 4', '    slack = 2 * o["dev_B"] + 8')]),
    ("H04 G9.clauses: lesion_hurts 2*lesion >= naive -> 3*lesion >= naive", "audits.py", [
        ('"NESTING.lesion_hurts": 2 * o["lesion_B"] >= o["naive_B"],',
         '"NESTING.lesion_hurts": 3 * o["lesion_B"] >= o["naive_B"],')]),
    ("H05 G9.clauses: a clause counts as able to fail if some cell leaves it undecided", "audits.py", [
        ("    cannot_fail = sorted(c for c in names if min(table[c].values()) > FAILS_AT)",
         "    cannot_fail = sorted(c for c in names if min(table[c].values()) >= HOLDS_AT)")]),
    ("H06 G9.clauses: a clause counts as able to hold if some cell leaves it undecided", "audits.py", [
        ("    cannot_hold = sorted(c for c in names if max(table[c].values()) < HOLDS_AT)",
         "    cannot_hold = sorted(c for c in names if max(table[c].values()) <= FAILS_AT)")]),
    ("H07 G9.clauses: isolation needs the other clauses only not to fail", "audits.py", [
        ("all(table[d][cell] >= HOLDS_AT for d in names if d != c)",
         "all(table[d][cell] > FAILS_AT for d in names if d != c)")]),
    ("H08 G9.sham: a sham clause counts as able to fail if some cell leaves it undecided", "audits.py", [
        ("    if min(clause_row.values()) > FAILS_AT:", "    if min(clause_row.values()) >= HOLDS_AT:")]),
    ("H09 G9.sham: neutral in 12 of 24 replicates is enough (was 22)", "audits.py", [
        ("    if near >= HOLDS_AT:", "    if near >= FAILS_AT:")]),
    ("H10 G10.setting: five placeholders no longer refused (n/a, na, none, unknown, ?)", "stats.py", [
        (PLACEHOLDERS, 'PLACEHOLDERS = ("", "tbd", "todo", "not computed")')]),
    ("H11 G10.setting: a horizon of zero later families accepted", "audits.py", [
        ("and v == int(v) and v >= 1):", "and v == int(v) and v >= 0):")]),
    ("H12 G10.setting: the effect threshold is not type-checked", "audits.py", [
        ('        elif k == "effect_threshold" and not (_number(v) and v > 0):', "        elif False:")]),
    ("H13 G10.contrast: one further difference besides the named variable is allowed", "audits.py", [
        ("    if differ == [named]:", "    if named in differ and len(differ) <= 2:")]),
    ("H14 G10.ruler: a mixed v0.1 verdict counts as NEGATIVE", "audits.py", [
        ('.get(tuple(sorted(answers)), "MIXED")', '.get(tuple(sorted(answers)), "NEGATIVE")')]),
    ("H15 G10.ruler: a ruler with no known positive is accepted", "audits.py", [
        ('    if not seen["POSITIVE"]:', "    if False:")]),
    ("H16 G10.ruler: members run only at another setting are ignored", "audits.py", [
        ("    if elsewhere:", "    if False:")]),
    ("H17 G10.ruler: the two guards of run 4 are ignored (was: a withdrawn label is read as POSITIVE; that "
     "label is no longer read)", "audits.py", [('data["verdicts"][key] in GUARDS', "False")]),
    ("H18 G10.ruler: an unreadable receipt is UNQUALIFIED, not BLOCKED", "audits.py", [
        ('found.append(Result(member, BLOCKED, "no readable verdict for %s in %s" % (source[2], source[0])))',
         'found.append(Result(member, UNQUALIFIED, "no readable verdict for %s in %s" % (source[2], source[0])))')]),
    ("H19 G11.custody: only the literal word confirmation fails the selection check", "claims.py", [
        ('    if record["selection_data"] != "discovery":', '    if record["selection_data"] == "confirmation":')]),
    ("H20 G11.custody: one generator fails whatever the claim says", "claims.py", [
        (GENERATOR, '    if d["generator_sha256"] == c["generator_sha256"]:')]),
    ("H21 G11.custody: the generator check is dropped", "claims.py", [(GENERATOR, "    if False:")]),
    ("H22 G11.custody: the discovery side needs no seeds, panel or generator", "claims.py", [
        ("    if any(not side.get(k) for side in (d, c) for k in part):",
         "    if any(not side.get(k) for side in (c,) for k in part):")]),
    ("H23 G11.custody: booleans count as counts", "stats.py", [(IS_COUNT, "    return isinstance(v, int) and v >= 0")]),
    ("H24 G12: L4 needs nothing more than L3", "claims.py", [('L4 = ("predicted",)', "L4 = ()")]),
    ("H25 G12: L3 needs nothing more than L2", "claims.py", [('L3 = ("reproduced",)', "L3 = ()")]),
    ("H26 G12: an ORIGIN claim needs no cold start and no class bound", "claims.py", [
        ('    "ORIGIN": ("cold_start", "class_bound"),', '    "ORIGIN": (),')]),
    ("H27 G12: an ECONOMY claim needs no lifecycle cost and no frozen comparators", "claims.py", [
        ('    "ECONOMY": ("lifecycle_cost", "frozen_comparators"),', '    "ECONOMY": (),')]),
    ("H28 G12: a LAW claim needs no registered prediction", "claims.py", [
        ('    "LAW": ("prediction_registered",),', '    "LAW": (),')]),
    ("H29 G12: a TRANSFER claim needs no new family", "claims.py", [
        ('    "TRANSFER": ("new_family",),', '    "TRANSFER": (),')]),
    ("H30 G12: a MECHANISM claim needs no intervention", "claims.py", [
        ('    "MECHANISM": ("intervention",),', '    "MECHANISM": (),')]),
    ("H31 G12.render: a claim with no setting hash is rendered", "claims.py", [
        ('    if setting_hash(setting) != claim["setting_sha256"]:',
         '    if claim.get("setting_sha256") and setting_hash(setting) != claim["setting_sha256"]:'),
        ('if not setting or not cell or not excluded or not claim.get("setting_sha256"):',
         "if not setting or not cell or not excluded:")]),
    ("H32 G12: an absent facet is UNQUALIFIED, not BLOCKED", "claims.py", [
        ('        return Result(name, BLOCKED, "absent")', '        return Result(name, UNQUALIFIED, "absent")')]),
    ("H33 verdict: INDETERMINATE outranks UNQUALIFIED", "verdict.py", [
        (RANK, "_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 1, INDETERMINATE: 2, PASS: 0}")]),
    ("H34 GM: a mutant rejected with the wrong verdict is not reported", "meta.py", [
        ("                      if r.verdict not in (PASS, exp)]", "                      if False]")]),
    ("H35 G9.sham: a faster sham counts as neutral", "audits.py", [
        ('abs(o["sham_B"] - o["dev_B"]) <= max(margin * o["dev_B"], slack)',
         'o["sham_B"] - o["dev_B"] <= max(margin * o["dev_B"], slack)')]),
    ("H36 G10.setting: power may be an integer", None,
     "GONE: adopted. The reader was right that a power of 1 is a power; the gate now accepts it"),
] + FINAL


def run_copy(out, tag, fname, edits):
    """Apply one change to a copy and run the unit tests there."""
    d = out / tag
    shutil.copytree(HERE, d, ignore=shutil.ignore_patterns("__pycache__", "RECEIPT_*.json", "mutation_probe.py",
                                                           "mutation_sets_final.py", "MANIFEST.md"))
    if fname:
        p = d / "rso_harness" / fname
        s = p.read_text(encoding="ascii")
        for old, new in edits:
            if s.count(old) != 1:
                return "PATTERN_NOT_FOUND"
            s = s.replace(old, new)
        p.write_text(s, encoding="ascii", newline="\n")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover"], cwd=str(d), capture_output=True, text=True,
                       env=ENV)
    return "noticed" if r.returncode != 0 else "SURVIVES"


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main():
    out = pathlib.Path(tempfile.mkdtemp(prefix="rso_mutation_"))
    live = [(name, fname, edits) for name, fname, edits in M if fname is not None]
    distinct = sorted({(fname, tuple(edits)) for _, fname, edits in live})          # the same change is run once
    try:
        if run_copy(out, "base", None, []) != "SURVIVES":
            print("the unchanged copy does not pass its own tests")
            return 1
        with ThreadPoolExecutor(max_workers=8) as pool:
            done = list(pool.map(lambda job: run_copy(out, "m%03d" % job[0], job[1][0], job[1][1]),
                                 enumerate(distinct)))
    finally:
        shutil.rmtree(out, ignore_errors=True)
    result = dict(zip(distinct, done))
    results = [(name, result[(fname, tuple(edits))]) for name, fname, edits in live]
    gone = [(name, why) for name, fname, why in M if fname is None]
    survived = [n for n, s in results if s == "SURVIVES"]
    lost = [n for n, s in results if s == "PATTERN_NOT_FOUND"]
    unexplained = [n for n in survived if n[:3] not in EQUIVALENT]
    sets = {}
    for key, who in SETS.items():
        mine = [(n, s) for n, s in results if n.startswith(key)]
        sets[key] = {"who": who, "changes": sum(1 for m in M if m[0].startswith(key)), "run": len(mine),
                     "gone": [n for n, _ in gone if n.startswith(key)],
                     "noticed_now": sum(1 for _, s in mine if s == "noticed"),
                     "survive_now": [n for n, s in mine if s == "SURVIVES"]}
        if key in FIRST_SIGHT:
            sets[key]["unnoticed_at_first_sight"] = FIRST_SIGHT[key]["unnoticed"]
            sets[key]["changes_at_first_sight"] = FIRST_SIGHT[key]["changes"]
    modules = sorted((HERE / "rso_harness").glob("*.py")) + [HERE / "tests" / "test_harness.py",
                                                             HERE / "mutation_probe.py", HERE / "mutation_sets_final.py"]
    receipt = {
        "what": "mutation probe of reference harness v0: one change to gate logic per copy, unit tests run on the copy",
        "how_to_read": "unnoticed_at_first_sight is each reader's own measurement on the version it attacked, "
                       "copied from its report. noticed_now is taken after tests were written against these same "
                       "changes: it shows the holes are closed and is not a measure of the tests",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "changes": len(M), "run": len(results), "distinct_changes_run": len(distinct),
        "distinct_changes_noticed": sum(1 for s in done if s == "noticed"),
        "distinct_changes_surviving": sum(1 for s in done if s == "SURVIVES"),
        "gone": [{"change": n, "why": w} for n, w in gone],
        "noticed": sum(1 for _, s in results if s == "noticed"), "survived": survived, "pattern_not_found": lost,
        "equivalent": EQUIVALENT, "sets": sets,
        "results": [{"change": n, "result": s} for n, s in results],
        "source_sha256_lf": {p.relative_to(HERE).as_posix(): sha(p) for p in modules},
    }
    (HERE / "RECEIPT_mutation_probe.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                                                      encoding="ascii", newline="\n")
    for n, s in results:
        print("%-9s %s" % (s, n))
    for n, w in gone:
        print("%-9s %s  [%s]" % ("gone", n, w))
    print("changes %d, run %d (%d distinct), noticed %d (%d distinct), survived %d %s, pattern not found %d"
          % (len(M), len(results), len(distinct), receipt["noticed"], receipt["distinct_changes_noticed"],
             len(survived), [n[:3] for n in survived], len(lost)))
    return 0 if not unexplained and not lost else 1


if __name__ == "__main__":
    sys.exit(main())
