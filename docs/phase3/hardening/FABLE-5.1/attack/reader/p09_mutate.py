"""Mutation probe: one small change to gate logic per copy of the patched harness; do the 31 tests notice?"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "harness_run"
OUT = HERE / "mut"
OUT.mkdir(exist_ok=True)

M = [
    ("G6.restart: drop the trajectory comparison, keep the answer", "torture.py",
     'if whole["answer"] != cut["answer"] or whole["trace"][at + 1:] != cut["trace"][at + 1:]:', 'if whole["answer"] != cut["answer"]:'),
    ("G6.reset: compare answers only, not trajectories", "torture.py",
     'seen.append((later["answer"], later["trace"]))', 'seen.append((later["answer"],))'),
    ("G1.cell: power floor 0.99 -> 0.90", "registration.py", "if v < 0.99)", "if v < 0.90)"),
    ("G2.preflight: POWER_FLOOR 0.99 -> 0.50", "stats.py", "POWER_FLOOR = 0.99", "POWER_FLOOR = 0.50"),
    ("G2.preflight: drop the check on the negative's answer (1 - alpha)", "stats.py",
     "    if 1 - alpha < floor:", "    if False:"),
    ("G7.report: drop the check that a positive control is easy to find (0.99)", "search.py",
     'if control["exact_reach"] < 0.99:', "if False:"),
    ("G7.report: drop 'seed count equals n'", "search.py",
     'if len(set(p["seeds"])) != len(p["seeds"]) or len(p["seeds"]) != p["n"]:', 'if len(set(p["seeds"])) != len(p["seeds"]):'),
    ("G7.calibration: one-sided interval (only the lower end is checked)", "search.py",
     "if lo <= exact <= hi:", "if lo <= exact:"),
    ("G9.clauses: ignore clauses that can never hold", "audits.py",
     "if cannot_fail or cannot_hold:", "if cannot_fail:"),
    ("G1.receipt: allow a run at the same clock tick or EARLIER by one (<= -> <)", "registration.py",
     'if receipt["ran_at"] <= cell["registered_at"]:', 'if receipt["ran_at"] < cell["registered_at"] - 49:'),
    ("G12.render: no cell needed", "claims.py",
     'if not conditions or not claim.get("cell"):', "if not conditions:"),
    ("G8.demand: CLOCK, KEY_READER and WORLD_PARKER no longer required baselines", "torture.py",
     'REQUIRED_BASELINES = ("CONSTANT", "CLOCK", "KEY_READER", "WORLD_PARKER")', 'REQUIRED_BASELINES = ("CONSTANT",)'),
    ("G10.ruler: a ruler with no registered negative is accepted", "audits.py",
     "    if not negatives:", "    if False:"),
    ("G10.contrast: two cells that do not differ in the named variable pass", "audits.py",
     "    if named not in differ:", "    if False:"),
    ("G1.cell: overlapping rules in a verdict table are accepted (single-valued half)", "registration.py",
     "        if len(got) != 1:", "        if len(got) < 1:"),
    ("G1.cell: registered_at, adapter, independent_unit, resources no longer required", "registration.py",
     '"adapter", "independent_unit", "design_seeds", "registered_seeds", "verdict_table", "power",',
     '"design_seeds", "registered_seeds", "verdict_table", "power",'),
    ("G11.custody: the claim and both tuning fields no longer required", "claims.py",
     'need = ("discovery", "confirmation", "selection_data", "claim", "tuning_evaluations", "tuning_budget")',
     'need = ("discovery", "confirmation", "selection_data")'),
    ("G5.neutrality: a physics-specific ruler declared valid in a physics with no known answer passes", "rulers.py",
     "    if outside:", "    if False and outside:"),
    ("G4.entry: 51 of 64 -> any score above chance counts (alpha 1e-6 -> 0.4 in the ruler)", "rulers.py",
     "ALPHA = 1e-6", "ALPHA = 0.4"),
    ("world: the environment mark is not cleared between episodes", "retain1.py",
     "        self.draws, self.mark = 0, None", "        self.draws = 0"),
    ("G9.sham: neutrality margin 25% -> 60%", "audits.py", "def audit_sham(reps, clause_row, margin=0.25):", "def audit_sham(reps, clause_row, margin=0.60):"),
    ("G9.arms: arms equal in all but one replicate still count as separate (control: should be noticed?)", "audits.py",
     "if all(o[arm] == o[group[0]] for o in reps):", "if sum(o[arm] == o[group[0]] for o in reps) >= len(reps) - 1:"),
    ("G12.promote: L2 no longer needs custody and a second implementation", "claims.py",
     'L2 = ("exact_null", "attack_round", "custody", "second_implementation")', 'L2 = ("exact_null", "attack_round")'),
    ("G7.report: REACH_BOUNDED bound may be anything not None", "search.py",
     'if report.get("upper_bound") is None or abs(report["upper_bound"] - zero_hit_upper(n)) > 1e-9:', 'if report.get("upper_bound") is None:'),
    ("G3: positive control of the method itself: bound 0.5 -> 0.7 in the ruler", "rulers.py", "BOUND = 0.5 ", "BOUND = 0.7 "),
]

survived = []
for i, (name, fname, old, new) in enumerate(M, 1):
    d = OUT / ("m%02d" % i)
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(SRC, d, ignore=shutil.ignore_patterns("__pycache__", "RECEIPT_harness_v0.json"))
    p = d / "rso_harness" / fname
    s = p.read_text(encoding="utf-8")
    if s.count(old) != 1:
        print("%02d  PATTERN NOT UNIQUE (%d)  %s" % (i, s.count(old), name))
        continue
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover"], cwd=str(d), capture_output=True, text=True)
    tail = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
    killed = r.returncode != 0
    if not killed:
        survived.append(name)
    print("%02d  %-9s %-18s %s" % (i, "noticed" if killed else "SURVIVES", tail[:18], name))
print()
print("%d of %d changes to gate logic are not noticed by the 31 tests (which include all 62 registered mutants):" % (len(survived), len(M)))
for s in survived:
    print("   -", s)
