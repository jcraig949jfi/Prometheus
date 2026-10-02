"""Fire test of check_hardening.py on a scratch mirror: plant one wrong statement at a time, see whether a check fails."""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE / "fire" / "root"
PKG = ROOT / "docs" / "phase3" / "hardening" / "FABLE-5.1"
CHK = PKG / "check_hardening.py"
REAL = r"F:/Prometheus-worktrees/dionysus-base-role"

# the scratch mirror is not a git repository: point the checker's read-only `git show` at the real one
src = CHK.read_text(encoding="utf-8")
if "str(ROOT)] + list(args)" in src:
    CHK.write_text(src.replace('["git", "-C", str(ROOT)] + list(args)', '["git", "-C", r"%s"] + list(args)' % REAL),
                   encoding="utf-8", newline="\n")

D1 = PKG / "01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md"
D2 = PKG / "02_HARDENING_DESIGN_v0.2_FABLE.md"
D3 = PKG / "03_TEST_HARNESS_SPEC_FABLE.md"
RM = PKG / "00_README.md"
HR = PKG / "harness" / "README.md"
ORIG = {p: p.read_text(encoding="utf-8") for p in (D1, D2, D3, RM, HR)}


def run():
    r = subprocess.run([sys.executable, "-B", str(CHK)], capture_output=True, text=True, cwd=str(ROOT))
    failed = [ln[5:75] for ln in r.stdout.splitlines() if ln.startswith("FAIL")]
    return r.returncode, failed


rc, failed = run()
print("baseline on the mirror: exit %d, failed: %s" % (rc, failed))

PLANTS = [
    # (what is planted, file, old, new)
    ("bucket table: A's first row 45 -> 40", D1, "tunnel core, and running experiments      45     50     55", "tunnel core, and running experiments      40     50     55"),
    ("bucket breakdown line: B '14 R1/R2' -> '24 R1/R2'", D1, "12 R0 + 14 R1/R2 + 6 R8 + 8 R4", "12 R0 + 24 R1/R2 + 6 R8 + 8 R4"),
    ("a quotation of B altered by one word", D1, "failure to reject a difference is not\n     enough.", "failure to detect a difference is not\n     enough."),
    ("a sentence of the PACKAGE put in B's mouth", D1, '"Some R8 variants are counterfeits; others could genuinely\n     construct better learning rules."', '"A control\'s expected verdict is\n     claim-specific"'),
    ("'three adversarial readers, 85 defects' -> 95 defects (doc 1)", D1, "85 defects; a checker with", "95 defects; a checker with"),
    ("'72 checks' -> '27 checks' in doc 1 only", D1, "72 checks                     document consistency", "27 checks                     document consistency"),
    ("harness number: 'wrong on three of four physics' -> two", D1, "FAILS (wrong on three of four physics)", "FAILS (wrong on two of four physics)"),
    ("harness number: 'Five such cases are rejected' -> Nine", D1, "Five such cases are rejected", "Nine such cases are rejected"),
    ("harness number: valley cold reach 0.0000 -> 0.5000 (doc 1)", D1, "exact cold reach is 0.0000", "exact cold reach is 0.5000"),
    ("run 2 figure: '660 candidates' -> '66 candidates'", D1, "660 candidates before and after", "66 candidates before and after"),
    ("run 2 figure: 313.5 -> 331.5", D1, "313.5 tasks fall to 20.5", "331.5 tasks fall to 20.5"),
    ("commit of my review ff1d7f0f4 -> ff1d7f0f5", D1, "(ff1d7f0f4)", "(ff1d7f0f5)"),
    ("'two known' escapes -> 'none known'", D1, "two known, pinned by tests", "none known, pinned by tests"),
    ("verdict of the package REPAIR -> BUILD in the headline", D1, "VERDICT ON THE PACKAGE: REPAIR.", "VERDICT ON THE PACKAGE: BUILD. "),
    ("kit table: memoriser negative -> POSITIVE", D2, "    memoriser                  negative    negative  yes", "    memoriser                  POSITIVE    negative  yes"),
    ("allocation: experiments 15% -> 25%", D2, "running and analysing experiments ....................... 15%", "running and analysing experiments ....................... 25%"),
    ("run 4: '2,000 lives' -> '20,000 lives'", D2, "2,000 lives per organism", "20,000 lives per organism"),
    ("run 4: 'six families per life' -> 'sixty'", D2, "six families per life", "sixty families per life"),
    ("run 4 bound in doc 2: 3.38 -> 3.83", D2, "exact bound 3.38 correct of\n16", "exact bound 3.83 correct of\n16"),
    ("run 4 bound in doc 3: 3.38 -> 3.83", D3, "elimination: 3.38 correct of 16", "elimination: 3.83 correct of 16"),
    ("'three readers found 85 defects' -> 58 (doc 2)", D2, "three readers found 85 defects", "three readers found 58 defects"),
    ("gate table: G8.demand broken 4 -> 5", D3, "G8.demand       the world cannot be solved         H5     1     4", "G8.demand       the world cannot be solved         H5     1     5"),
    ("audit table: sham '8 of 24 replicates' -> 18", D3, "8 of 24 replicates;", "18 of 24 replicates;"),
    ("audit table: G9.sham on run 2 FAIL -> PASS", D3, "G9.sham        run 2          FAIL ", "G9.sham        run 2          PASS "),
    ("audit table: G9.clauses run 3 '6 of 13' -> '9 of 13'", D3, "run 3          UNQUALIFIED   6 of 13", "run 3          UNQUALIFIED   9 of 13"),
    ("'(power 0.24)' -> '(power 0.42)'", D3, "(power 0.24)", "(power 0.42)"),
    ("reach table: needle neutral 0.7298 -> 0.7928", D3, "0.7298", "0.7928"),
    ("historical fixtures: 13 mapped to another gate", D3, "13 same-code repeat called replication ...... G7, repeated founder", "13 same-code repeat called replication ...... G1, repeated founder"),
    ("'Fifteen have a running case' kept, one 'specified' row relabelled as running", D3, "specified (two adapters)", "G5, two adapters......."),
    ("README: '31 unit tests' -> '13 unit tests'", RM, "harness/` (31 unit tests;", "harness/` (13 unit tests;"),
    ("README: '21 gates' -> '12 gates'", RM, "The harness runs: 21 gates", "The harness runs: 12 gates"),
    ("README: 'falls outside both on one row' -> 'three rows'", RM, "falls outside both on one row", "falls outside both on three rows"),
    ("harness README: '62 mutants' -> '26 mutants'", HR, "62 mutants are rejected", "26 mutants are rejected"),
]

caught = 0
rows = []
for what, path, old, new in PLANTS:
    text = ORIG[path]
    if text.count(old) != 1:
        rows.append(("PATTERN x%d" % text.count(old), what, ""))
        continue
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
    try:
        rc, failed = run()
    finally:
        path.write_text(text, encoding="utf-8", newline="\n")
    caught += rc != 0
    rows.append(("caught" if rc != 0 else "NOT CAUGHT", what, "; ".join(failed)[:95]))
for r in rows:
    print("%-11s %-72s %s" % r)
n = sum(1 for r in rows if not r[0].startswith("PATTERN"))
print("\n%d of %d planted errors are caught; %d pass the checker" % (caught, n, n - caught))
rc, failed = run()
print("mirror restored: exit %d" % rc)
