"""Checks on the three hardening documents and the three READMEs. Every check can fail.

Run from anywhere:

    python -B docs/phase3/hardening/FABLE-5.1/check_hardening.py
    python -B docs/phase3/hardening/FABLE-5.1/check_hardening.py --pins     prints the pins below

What is checked:
  1. form: ASCII, LF, no tab, at most 80 columns, no code fence, no placeholder, in all six files;
  2. sources: the review by ASTRA-6.0 is read from its commit and its files hash as recorded; the
     copies of the hardening package verify against their manifest;
  3. quotes: every double-quoted string in a document is registered below with one source, and is
     found word for word (whitespace collapsed) in that source. Who the sentence says spoke is
     NOT read;
  4. receipts: the receipts quoted here were written by the code now on disk, and the three kept
     versions of the harness are the code that wrote theirs;
  5. statements: every statement listed in STATEMENTS is built from a receipt or a source and must
     appear in its file; eight tables are parsed and compared row by row with the same data;
  6. pins: the text of each file is hashed as it is, every space and line break included. An edit
     made after pinning fails this check until a person pins the file again. A pin freezes a text;
     it does not verify it. Manifests are checked in the same way and are the same kind of check.

Flags used by fire_test.py: --no-pins skips 6, --no-fire skips the checks on the fire test's own
receipt, --no-manifests skips the manifests. HARDENING_GIT_ROOT names the repository to read git
objects from, and to run the checker of my review in, when the files are a copy.

Exit code 0 only if every check passes. A source that cannot be read fails its check. This does
not test whether the arguments are right, and it cannot check a judgment.
"""
import hashlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
GIT_ROOT = os.environ.get("HARDENING_GIT_ROOT") or str(ROOT)
HARNESS, ATTACK = HERE / "harness", HERE / "attack"
REVIEW = ROOT / "docs" / "phase3" / "review" / "FABLE-5.1"
GIT_REVIEW = pathlib.Path(GIT_ROOT) / "docs" / "phase3" / "review" / "FABLE-5.1"
COUNTERFEIT = REVIEW / "counterfeit"
INPUTS1 = ROOT / "roles" / "Dionysus" / "prompts" / "2026-10-01_review_charter"
INPUTS2 = ROOT / "roles" / "Dionysus" / "prompts" / "2026-10-02_hardening_v0.2"
ASTRA_COMMIT = "f4d9e72d9cf72ee11bc3a4f01171154dc8a5c90e"
REVIEW_COMMIT = "ff1d7f0f4"
ASTRA_DIR = "docs/phase3/reviews/ASTRA-6.0/rso-v0.1/"
ASTRA_FILES = {
    "README.md": "323e9bc3ef421a16960a62d4b387be32a95e12f1271ec8336a19fa10e402d71d",
    "REVIEW_PACKET_2026-10-01.md": "63df251fb11e43786b22631b4dfe789f5f988d0324aa9aa2788c89fd4fbe65e8",
    "VALIDATION.md": "248feb5537325c080476311c65ed4ccd19ebe78ae482b1fe1a9ec42b7ac73702",
    "reports/Wind tunnel charter review.md": "696a0b6e5cf5209edabc44a6d905e5317c4a38928f3bdf430350e7e8fa4df85b",
    "research_notes/Wind tunnel charter review/reviewed_findings.md":
        "5fe6227d5eff250c9d98a76e1fbc6f986fd982403ae73c35224c7e48d05d50ed",
}
D1 = HERE / "01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md"
D2 = HERE / "02_HARDENING_DESIGN_v0.2_FABLE.md"
D3 = HERE / "03_TEST_HARNESS_SPEC_FABLE.md"
RM, HR, AR = HERE / "00_README.md", HARNESS / "README.md", ATTACK / "README.md"
DOCS = [D1, D2, D3]
EVERY = [D1, D2, D3, RM, HR, AR]
NO_PINS, NO_FIRE, NO_MANIFESTS = ("--no-pins" in sys.argv), ("--no-fire" in sys.argv), ("--no-manifests" in sys.argv)

# The text of each file as it is, hashed. Print current values with --pins.
PINS = {
    "01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md": "1cd2b985fea3b4de",
    "02_HARDENING_DESIGN_v0.2_FABLE.md": "698a0bd4f14957a4",
    "03_TEST_HARNESS_SPEC_FABLE.md": "77c591fad4e8093f",
    "00_README.md": "f3cb36b028b76812",
    "harness/README.md": "313574b5bed932b3",
    "attack/README.md": "0e0f5bf6573c75f7",
}

# Every quotation in the three documents and the one source it is registered to.
# A my review; B the review by ASTRA-6.0; C the hardening package; O the original design and portfolio.
QUOTES = {
    "A control's expected verdict is claim-specific.": 'C',
    '30% of authorized engineering/analysis person-hours for the thin tunnel and qualification fixtures': 'B',
    'A clean fixture result qualifies only the tested attack classes.': 'B',
    'A few strong baselines do not bound all cheap policies.': 'B',
    'A good audit system must be able to reject persuasive false accusations.': 'O',
    'A missing positive for a ruler means UNQUALIFIED': 'C',
    'Add at least five deliberate mutants the harness should reject.': 'C',
    'Carry equivalent task-relevant priors in fixed-updater controls where feasible.': 'B',
    'Choose between R3 if the main unresolved question is reachability/continuous plasticity, or R4 '
    'if the main unresolved question is Track-A ontology dependence.': 'O',
    'Define intervention scope, not mandatory buffers.': 'B',
    'Do not infer this from write ancestry or memory size alone.': 'C',
    'Equivalent behavior under relabeling must not gain a claim rung.': 'B',
    'Every clause needs a fixture capable of making it false.': 'C',
    'Expand R8 with nested-compiler cargo and flattening attacks.': 'C',
    'For shared niches the independent unit is the world/ecology': 'B',
    'If only an operational intervention-relative notion survives, adopt it openly and drop '
    'stronger ontological language.': 'B',
    'In-flight messages, optimizer state, external marks, time, RNG streams, allocator IDs and host caches': 'B',
    'Missing capabilities cap claims': 'B',
    'NEXT': 'C',
    'Neither wins by calendar alone.': 'B',
    'No interface should be called substrate-neutral until it has operated correctly on at least '
    'two materially different physical realizations.': 'O',
    'RECURSIVE_SAGACITY_RULER = DETECTION_UNQUALIFIED': 'C',
    'R_cold(budget)': 'C',
    'R_repair(distance, budget)': 'C',
    'The harness prevents rules from living only in prose.': 'C',
    'The reference harness in this package implements a minimal executable form of these rules.': 'C',
    'The tunnel standardizes accountability, not ontology.': 'C',
    'This is a documentary adversarial pass, not an independently reproduced scientific result or '
    'an external expert review.': 'B',
    'Try to make a physics-specific ruler masquerade as shared.': 'C',
    'a selector with many indices is an acquirer': 'A',
    'an executable registration must set target effect, equivalence margins, independent units, '
    'sample size/power, caps, multiplicity/sequential policy and stop rules': 'B',
    'at the tested depth, boundary and task population': 'B',
    'by evidence': 'C',
    'compiler that launders task cargo': 'B',
    'failure to reject a difference is not enough': 'B',
    'is insufficient': 'O',
    'is not a frozen learning rule': 'B',
    'is not defined at a zero denominator': 'B',
    'it does not promise a universal depth detector': 'B',
    'legitimate positive for reuse of built parts': 'A',
    'native resource unit plus host-cost accounting': 'C',
    'nested improvement, order k, setting S, acquired-information estimate I, lifecycle cost C': 'C',
    'only demonstrated fakes are negatives': 'B',
    'persuasive false auditor accusation': 'C',
    'power/attainability preflight': 'C',
    'preferably': 'C',
    'python -m unittest discover -v': 'C',
    'reconstruction alone proves neither new developmental origin nor higher causal order': 'B',
    'small exactly solvable cases and larger related cases': 'B',
    'tunnel core (runner, worlds, rulers)': 'A',
    'typed inconclusive': 'C',
    'vetoes a valid conventional mechanism by pedigree': 'B',
    'where, if anywhere, does development pay?': 'B',
}

WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
         "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print("%-4s %s%s" % ("PASS" if ok else "FAIL", name, (" -- " + detail) if detail else ""))


def text(path):
    """A file as text. A checkout that turned line ends into CRLF is read as LF; the six files themselves
    are held to LF by the form check and by .gitattributes."""
    return io.open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def lf_sha(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def manifest_sha(data):
    """As comms/manifest.py hashes: text with every line ending as LF, a binary file as it is."""
    if b"\x00" in data[:8192]:
        return hashlib.sha256(data).hexdigest()
    return hashlib.sha256(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", GIT_ROOT] + list(args), capture_output=True)


def section(raw, start, end):
    """The text of a document between two markers."""
    return raw.split(start)[1].split(end)[0]


def pin(path):
    """The text as it is: every space and every line break counts."""
    return lf_sha(io.open(path, "rb").read())[:16]


def count(pattern, s):
    return len(re.findall(pattern, s, flags=re.M))


def word(n):
    return WORDS[n] if 0 <= n < len(WORDS) else str(n)


def cap(s):
    return s[:1].upper() + s[1:]


def tests_in(path):
    return count(r"^    def test_", text(path))


if "--pins" in sys.argv:
    for p in EVERY:
        print('    "%s": "%s",' % (p.relative_to(HERE).as_posix(), pin(p)))
    sys.exit(0)

# ------------------------------------------------------------------ 1. form
for p in EVERY:
    raw = io.open(p, "rb").read()
    problems = []
    if b"\r" in raw:
        problems.append("CR present")
    if b"\t" in raw:
        problems.append("tab present")
    try:
        raw.decode("ascii")
    except UnicodeDecodeError:
        problems.append("non-ASCII")
    body = raw.decode("utf-8", "replace")
    wide = [i + 1 for i, line in enumerate(body.split("\n")) if len(line) > 80]
    if wide:
        problems.append("lines over 80: %s" % wide[:5])
    if p in DOCS and "```" in body:
        problems.append("code fence inside a paste block")
    if p not in DOCS and '"' in body:
        problems.append("a quotation in a README is not checked; remove it")
    if p in DOCS and not (body.startswith("=" * 80 + "\n") and body.rstrip("\n").endswith("=" * 80)):
        problems.append("banner missing")
    check("form %s" % p.relative_to(HERE).as_posix(), not problems, "; ".join(problems))
check("form: no placeholder is left in any file", not any("_PLACE" + "HOLDER" in text(p) for p in EVERY))
for p in DOCS:
    numbers = [int(n) for n in re.findall(r"^-{80}\n(\d+)\. [A-Z]", text(p), flags=re.M)]
    check("form %s: its sections are numbered 1 to %d without a gap" % (p.name[:2], len(numbers)),
          numbers == list(range(1, len(numbers) + 1)) and len(numbers) >= 12, "%s" % numbers)

# --------------------------------------------------------------- 2. sources
astra, astra_ok = [], True
for name, want in ASTRA_FILES.items():
    blob = git("show", "%s:%s%s" % (ASTRA_COMMIT, ASTRA_DIR, name))
    if blob.returncode != 0 or hashlib.sha256(blob.stdout).hexdigest() != want:
        astra_ok = False
    else:
        astra.append(blob.stdout.decode("utf-8"))
check("sources: the ASTRA-6.0 review is readable at its commit and its five files hash as recorded",
      astra_ok and len(astra) == 5)
manifest = text(INPUTS2 / "MANIFEST.md")
package_files = sorted(INPUTS2.glob("chatgpt56_*.md"))
check("sources: five copies of the hardening package verify against their manifest",
      len(package_files) == 5 and all(
          ("%s  sha256:%s" % (p.name, lf_sha(p.read_bytes()))) in manifest for p in package_files))
readme_inputs = text(INPUTS2 / "00_README.md")
check("sources: the inputs README records the ASTRA commit and all five hashes",
      ASTRA_COMMIT in readme_inputs and all(h in readme_inputs for h in ASTRA_FILES.values()))
check("sources: both commits named in the documents exist",
      git("cat-file", "-e", REVIEW_COMMIT + "^{commit}").returncode == 0
      and git("cat-file", "-e", ASTRA_COMMIT + "^{commit}").returncode == 0
      and all(REVIEW_COMMIT in text(p) and ASTRA_COMMIT[:9] in text(p) for p in (D1, RM)))
B_REPORT = astra[3] if astra_ok else ""
B_VALIDATION = astra[2] if astra_ok else ""
C1, C2, C3, C5, C6 = [text(p) for p in package_files] if len(package_files) == 5 else [""] * 5
O1, O2 = text(INPUTS1 / "03_RSO_WIND_TUNNEL_DESIGN_v0.1_as_pasted.md"), text(
    INPUTS1 / "04_RACE_CAR_PORTFOLIO_R0-R9_as_pasted.md")
A1, A2, A3 = [text(p) for p in sorted(REVIEW.glob("RESPONSE_*.md"))]
A_README = text(REVIEW / "00_README.md")
SOURCES = {"A": norm(" ".join([A1, A2, A3])), "B": norm(" ".join(astra)), "C": norm(" ".join([C1, C2, C3, C5, C6])),
           "O": norm(O1 + " " + O2)}

# ---------------------------------------------------------------- 3. quotes
for p in DOCS:
    body = norm(text(p))
    quotes = [norm(q) for q in re.findall(r'"([^"]+)"', body)]
    unregistered = [q[:60] for q in quotes if q not in QUOTES]
    not_found = [q[:60] for q in quotes if q in QUOTES and q not in SOURCES[QUOTES[q]]]
    by = {s: sum(1 for q in quotes if QUOTES.get(q) == s) for s in "ABCO"}
    check("quotes %s" % p.name, body.count('"') % 2 == 0 and not unregistered and not not_found,
          "%d quoted: %s%s%s" % (len(quotes), ", ".join("%d from %s" % (v, k) for k, v in by.items() if v),
                                 ("; NOT REGISTERED: %s" % unregistered) if unregistered else "",
                                 ("; NOT IN ITS SOURCE: %s" % not_found) if not_found else ""))
used = {norm(q) for p in DOCS for q in re.findall(r'"([^"]+)"', norm(text(p)))}
check("quotes: no registered quotation is unused", not (set(QUOTES) - used), "%s" % sorted(set(QUOTES) - used)[:3])

# -------------------------------------------------------------- 4. receipts
rec = json.loads(text(HARNESS / "RECEIPT_harness_v0.json"))
probe = json.loads(text(HARNESS / "RECEIPT_mutation_probe.json"))
att = json.loads(text(ATTACK / "RECEIPT_attack_on_first_version.json"))
second = json.loads(text(ATTACK / "second_version" / "RECEIPT_harness_v0.json"))
second_probe = json.loads(text(ATTACK / "second_version" / "RECEIPT_mutation_probe.json"))
third = json.loads(text(ATTACK / "third_version" / "RECEIPT_harness_v0.json"))
third_probe = json.loads(text(ATTACK / "third_version" / "RECEIPT_mutation_probe.json"))
modules = sorted(p.relative_to(HARNESS).as_posix() for p in (HARNESS / "rso_harness").glob("*.py"))
tests_file = "tests/test_harness.py"


def current(receipt, base, names=None):
    got = receipt["source_sha256_lf"]
    return (names is None or sorted(got) == sorted(names)) and all(
        (base / n).is_file() and lf_sha((base / n).read_bytes()) == h for n, h in got.items())


check("receipts: the harness receipt was written by the code now on disk, all of it",
      current(rec, HARNESS, modules + ["run_harness.py", tests_file]))
check("receipts: the mutation probe's receipt was written against the code now on disk",
      current(probe, HARNESS, modules + [tests_file, "mutation_probe.py", "mutation_sets_final.py"]))
attack_files = sorted(p.relative_to(ATTACK).as_posix() for p in list((ATTACK / "first_version").rglob("*.py")) + list(
    (ATTACK / "reader").glob("*.py")) + [ATTACK / "replay_attack.py"])
check("receipts: the attack receipt was written from the files now on disk, and the first version is the code "
      "that wrote its own receipt", current(att, ATTACK, attack_files)
      and att["first_version"]["is_the_code_that_wrote_its_receipt"] is True
      and att["first_version"]["its_own_tests_pass"] is True)
check("receipts: the kept second version is the code that wrote its two receipts",
      current(second, ATTACK / "second_version") and current(second_probe, ATTACK / "second_version"))
check("receipts: the kept third version is the code that wrote its two receipts",
      current(third, ATTACK / "third_version") and current(third_probe, ATTACK / "third_version"))
check("receipts: the four audited receipts of the review are the ones now on disk",
      len(rec["audited_receipts_sha256_lf"]) == 4
      and all(lf_sha((COUNTERFEIT / n).read_bytes()) == h for n, h in rec["audited_receipts_sha256_lf"].items()))
check("receipts: every gate passes its registered cases and every known escape is still an escape",
      rec["summary"]["all_as_registered"] is True
      and all(g["status"] == "PASS" for g in rec["gates"].values())
      and all(e["verdict"] == "PASS" for e in rec["known_escapes"]))
check("receipts: the mutation probe leaves only changes that alter no verdict",
      probe["pattern_not_found"] == [] and all(s[:3] in probe["equivalent"] for s in probe["survived"]),
      "%s" % [s[:3] for s in probe["survived"]])

# ------------------------------------------------------- data the statements are built from
sys.path.insert(0, str(HARNESS))
from rso_harness import audits, claims, ladder, meta, retain1, rulers, search, stats, torture  # noqa: E402

s, par, aud = rec["summary"], rec["parameters"], rec["audits_of_existing_receipts"]
first, two, three = att["first_version"]["summary"], second["summary"], third["summary"]
mv = s["mutant_verdicts"]
n_tests = tests_in(HARNESS / tests_file)
g2 = json.loads(text(COUNTERFEIT / "RECEIPT_gauntlet2.json"))
g3 = json.loads(text(COUNTERFEIT / "RECEIPT_gauntlet3.json"))
keys = json.loads(text(COUNTERFEIT / "RECEIPT_keys.json"))
med = g2["cells"]["BUILDER"]["medians"]
world_one, world_two = rec["exploratory_world_one_two_nested_boundaries"], rec["exploratory_world_two_unseen_pair"]
one, pairs = world_one["survey"], world_two["survey"]
h16, lives = world_one["exact_nothing_carried_bound"], world_two["lives"]
bracket, reach, attain = rec["bound_bracket"], rec["search"], rec["fixture_attainability"]
escapes = rec["known_escapes"]
esc = {}
for e in escapes:
    esc.setdefault(e["gate"], []).append(e)


def shown(gate, starts):
    """What the receipt shows for the one known escape of a gate whose fault begins so."""
    found = [e for e in escapes if e["gate"] == gate and e["fault"].startswith(starts)]
    return (found[0].get("shown") or {}) if len(found) == 1 else {}


review_checks = subprocess.run([sys.executable, "-B", str(GIT_REVIEW / "check_review.py")], capture_output=True,
                               cwd=GIT_ROOT)
got = re.search(r"(\d+) checks, (\d+) failed", review_checks.stdout.decode("utf-8", "replace"))
n_review, review_failed = (int(got.group(1)), int(got.group(2))) if got else (0, -1)     # how many it makes, not whether they pass
report1 = text(ATTACK / "REPORT_of_the_reader.md")
closure = text(ATTACK / "closure_reader" / "REPORT.md")
report2 = text(ATTACK / "second_reader" / "REPORT.md")
final1 = text(ATTACK / "closure_reader" / "REPORT_final.md")
final2 = text(ATTACK / "second_reader" / "REPORT_final.md")
n_block, n_major = count(r"^- \*\*B\d+ ", report1), count(r"^- \*\*M\d+ ", report1)
closed = {k: count(r"^\| [BM]\d+ \| %s \|" % k, closure) for k in ("CLOSED", "PARTLY", "OPEN")}
new_block = count(r"^- \*\*N\d+", section(closure, "### BLOCKER", "### MAJOR"))
new_major = count(r"^- \*\*N\d+", section(closure, "### MAJOR", "### MINOR"))
block2 = count(r"^\d+\. \*\*", section(report2, "## BLOCKER", "## MAJOR"))
major2 = count(r"^\d+\. \*\*", section(report2, "## MAJOR", "## MINOR"))
# the final round: both readers, on version three
f1_block = count(r"^X\d+ ", section(final1, "\nBLOCKER\n", "\nMAJOR\n"))
f1_major = count(r"^M\d+ ", section(final1, "\nMAJOR\n", "\nMINOR\n"))
f2_block = count(r"^N\d+\. ", section(final2, "**BLOCKER**", "**MAJOR**"))
f2_major = count(r"^N\d+\. ", section(final2, "**MAJOR**", "**MINOR**"))
by_gate = section(final2, "## 4. NEW PASSING FAULTS BY GATE", "## 5. WHAT I DID NOT CHECK")
new_rows = re.findall(r"^\| (G\d+\.[a-z]+) \| ", by_gate, flags=re.M)
new_faults, new_gates, new_world = len(new_rows), len(set(new_rows)), count(r"^\| world two", by_gate)
refused = len(by_gate.split("Sound cases refused:")[1].split("\n")[0].split(";"))
got = re.search(r"chosen after reading the checker: (\d+) planted \([^)]*\), (\d+) caught", final1)
chosen = (int(got.group(2)), int(got.group(1))) if got else (None, None)
got = re.search(r"sampled by rule, fixed seed: (\d+) planted, (\d+) caught", final1)
sampled = (int(got.group(2)), int(got.group(1))) if got else (None, None)
got = re.search(r"With pins off, (\d+) of my (\d+) fresh plants pass", final2)
fresh = (int(got.group(2)) - int(got.group(1)), int(got.group(2))) if got else (None, None)
check("sources: the final round's counts are read from the two final reports",
      (f1_block, f1_major) == (1, 4) and "New: %d blocker, %d majors" % (f2_block, f2_major) in final2
      and new_world == 1 and None not in chosen + sampled + fresh,
      "%d and %d; %d and %d; %d faults in %d gates; %d sound cases refused; plants %s %s %s" % (
          f1_block, f1_major, f2_block, f2_major, new_faults, new_gates, refused, chosen, sampled, fresh))
reports = [ATTACK / "REPORT_of_the_reader.md"] + sorted((ATTACK / "closure_reader").glob("REPORT*.md")) + sorted(
    (ATTACK / "second_reader").glob("REPORT*.md"))
n_mechanical = sum(1 for p in reports if "were replaced mechanically" in text(p)[:700])
n_entities = sum(1 for p in reports if "HTML entities put in by the notification wrapper" in text(p)[:700])

sets = probe["sets"]
sight = {k: (v["unnoticed_at_first_sight"], v["changes_at_first_sight"]) for k, v in sets.items()
         if "unnoticed_at_first_sight" in v}
got = re.search(r"changes (\d+) \| noticed (\d+) \| unnoticed (\d+) \| of the unnoticed, alter no verdict: (\d+)", final2)
y_sight = tuple(int(x) for x in got.groups()) if got else (0, 0, 0, 0)
no_verdict = y_sight[3]
sight_ok = (sorted(sight) == ["C", "F", "H", "R", "X", "Y"]
            and sight["R"] == (att["logic_changes_not_noticed"], att["logic_changes"])
            and "| My one-line logic changes | %d; %d survive" % (sight["C"][1], sight["C"][0]) in closure
            and "%d changes, %d noticed, %d survive" % (sight["F"][1], sight["F"][1] - sight["F"][0], sight["F"][0]) in report2
            and "the fork's, %d changes, %d unnoticed" % (sight["H"][1], sight["H"][0]) in report2
            and "- Fresh one-line changes: %d; %d unnoticed." % (sight["X"][1], sight["X"][0]) in final1
            and y_sight[:3] == (sight["Y"][1], sight["Y"][1] - sight["Y"][0], sight["Y"][0]))
check("sources: the six first-sight figures of the mutation probe are the ones the readers reported", sight_ok,
      "%s" % sorted(sight.items()))
SIGHT4 = "%d of %d, %s%d of %d, %d of %d and %d of %d" % (sight["R"] + ("%s",) + sight["C"] + sight["F"] + sight["H"])
SIGHT2 = "%d of %d and %d of %d" % (sight["X"] + sight["Y"])
bits = ["%.2f" % keys["cells"][c]["certified_bits_carried"] for c in (
    "ELIM", "SELECTOR(64)", "ACQUIRER(4)", "ACQUIRER(8)", "ACQUIRER(12)", "ACQUIRER(16)")]
a_alloc = dict(re.findall(r"^    (.+?) \.{3,} about (\d+)%$", A1, flags=re.M))
b_alloc = dict(re.findall(r"^\| (.+?) \| (\d+)% \|$", B_REPORT, flags=re.M))
c_alloc = {v: k for k, v in re.findall(r"^- (\d+)% (.+)$", C5, flags=re.M)}
try:
    A = {"core": int(a_alloc["tunnel core (runner, worlds, rulers)"]),
         "std": int(a_alloc["calibration standards (isomers, counterfeit kit)"]), "r0": int(a_alloc["R0 learners"]),
         "ker": int(a_alloc["thin candidate kernels (Track A, then R3)"]),
         "second": int(a_alloc["second implementation"]), "census": int(a_alloc["blind census"])}
    B = {"core": int(b_alloc["Thin tunnel, W0 and general qualification fixtures, including the three-node message ring"]),
         "r0": int(b_alloc["R0, including simple overlapping R3 reference"]),
         "ker": int(b_alloc["R1/R2 shared kernel and toggles"]), "r8": int(b_alloc["R8 task-library, updater and cargo controls"]),
         "r4": int(b_alloc["R4 tiny unlike specimen"]), "exp": int(b_alloc["Discriminating experiments and analysis"]),
         "chal": int(b_alloc["Independent challenge/reserve"])}
    C = {"core": int(c_alloc["tunnel core + qualification automation"]), "org": int(c_alloc["candidate runtimes + standards"]),
         "exp": int(c_alloc["discriminating experiments"]), "chal": int(c_alloc["independent challenge/reimplementation"]),
         "census": int(c_alloc["blind/found-physics census"])}
    alloc_ok = sum(A.values()) == sum(B.values()) == sum(C.values()) == 100
except KeyError:
    A = B = C = {}
    alloc_ok = False
check("sources: the three allocations are read from A, B and C, and each sums to 100", alloc_ok)
a_org, b_org = (A["std"] + A["r0"] + A["ker"], B["r0"] + B["ker"] + B["r8"] + B["r4"]) if alloc_ok else (0, 0)
mine = [int(x) for x in re.findall(r"\.{3,} (\d+)%$", text(D2), flags=re.M)]
check("arithmetic: the allocation of document 2 sums to 100", len(mine) == 6 and sum(mine) == 100, "%s" % mine)
mine = mine if len(mine) == 6 else [0] * 6


def rate(x):
    return "%.4f" % x


def run_medians(*names):
    return tuple("%.1f" % med[n] for n in names)


def mean(survey, name, arm):
    return "%.2f" % survey[name][arm]["mean"]


def thousands(n):
    return "{:,}".format(n)


raw1, raw2, raw3 = text(D1), text(D2), text(D3)
indeterminate = sorted({g for g, row in rec["gates"].items() for m in row["mutant_verdicts"]
                        if m["verdict"] == "INDETERMINATE"} - {"G12.promote"})
reset_cases = sum(1 for m in rec["gates"]["G6.reset"]["mutant_verdicts"] if m["mutant"] != "no seeds")
restart_cases = sum(1 for m in rec["gates"]["G6.restart"]["mutant_verdicts"] if m["mutant"] != "no seeds")
hidden = len(esc.get("G6.reset", [])) + len(esc.get("G6.restart", []))
run2c, run3c = aud["run2"]["clauses"]["detail"], aud["run3"]["clauses"]["detail"]
alone2 = len(run2c["table"]) - len(run2c["cannot_fail"]) - len(run2c["not_isolated"])
alone3 = len(run3c["table"]) - len(run3c["cannot_fail"]) - len(run3c["not_isolated"])
control = reach["positive_control_by_budget"]
bits_answered = aud["rulers"]["BITS at BITS@KEYS"]["detail"]["answered"]
reader_world = att["readers_key_world_with_a_second_boundary"]
reader_cache = reader_world["mean_correct_of_16"]["CACHE (one cached family table + fixed 256-way re-indexer)"]["across_epochs"]
eq = [k for k in range(2049) if stats.equivalence(k, 2048, 0.5, torture.MARGIN, torture.DEMAND_ALPHA) == "WITHIN"]
out_low = max(k for k in range(1025) if stats.equivalence(k, 2048, 0.5, torture.MARGIN, torture.DEMAND_ALPHA) == "OUTSIDE")
cal = [k for k in range(257) if stats.consistent(k, 256, search.exact_reach("NEEDLE", "NEUTRAL", 400, "COLD"), search.CAL_ALPHA)]
steps = len(retain1.World().episode(retain1.Register(), 2000)["trace"])
sec3 = section(raw1, "3. WHERE B IS RIGHT", "4. WHAT MY REVIEW ADDS")
points = re.split(r"^ {1,2}(\d{1,2})\. (?=[A-Z])", sec3, flags=re.M)
untested = [int(points[i]) for i in range(1, len(points), 2) if "nothing that runs tests it" in norm(points[i + 1]).lower()]
n_points = len(points) // 2
calib95 = shown("G7.calibration", "an estimator that ran 95%")
reads_bit = shown("G8.demand", "the cue follows the fourth bit")
one_in_five = shown("G4.entry", "an impostor that carries the cue in one episode of five")
fire = None
ORDER = ("number", "pinned number", "quote", "attribution", "table", "word", "form", "whitespace")
if not NO_FIRE:
    try:
        fire = json.loads(text(HERE / "RECEIPT_fire_test.json"))
    except (OSError, ValueError):
        fire = None
    names = ["check_hardening.py", "fire_test.py"] + [p.relative_to(HERE).as_posix() for p in EVERY]
    check("receipts: the fire test's receipt was written against the checker and the six files now on disk",
          fire is not None and current(fire, HERE, names) and fire["unchanged_copy_passes"] is True
          and fire["pattern_not_found"] == [] and sorted(fire["by_kind"]) == sorted(ORDER))
FIRE = None if fire is None or sorted(fire["by_kind"]) != sorted(ORDER) else (
    "Of %d errors I planted, the pins catch %d and the content checks alone catch %d. By kind, with the pins off: %s." % (
        fire["plants"], fire["caught_with_pins"], fire["caught_without_pins"], ", ".join(
            "%s %d of %d" % ("quotation" if k == "quote" else k, fire["by_kind"][k]["caught_without_pins"],
                             fire["by_kind"][k]["plants"]) for k in ORDER)))

# Each statement is built from the data above and must appear in its file. None marks a statement
# whose supporting fact no longer holds.
STATEMENTS = {
    D1: [
        "first read, of the draft ........ %d blocking and %d major defects" % (n_block, n_major),
        "of those %d: %d closed, %d partly, %d open; %d blocking, %d major new" % (
            n_block + n_major, closed["CLOSED"], closed["PARTLY"], closed["OPEN"], new_block, new_major),
        "second read, by a fresh reader .. %d blocking and %d major defects" % (block2, major2),
        "final round, of version three ... both readers again: %d blocking and %d major, new or still open" % (
            f1_block + f2_block, f1_major + f2_major),
        "%d defects in drafts" % (38 + 21 + 26),
        "checker with %d checks" % n_review,
        "its seven concerns each adjudicated" if "seven editorial concerns" in norm(B_VALIDATION)
        and "read-only validation subagent" in norm(B_VALIDATION) else None,
        "45 tunnel core, 45" if alloc_ok and (A["core"], a_org) == (45, 45) else None,
        "%d tunnel, %d candidates," % (B["core"], b_org) if alloc_ok else None,
        "%d experiments, %d" % (B["exp"], B["chal"]) if alloc_ok else None,
        "one cell in days 31 to 55" if "| Days 31-55 | Small two-knob W1 discovery map and one I/E cell" in B_REPORT else None,
        "first gate had power 0.865" if "exact power 0.865" in norm(A2) else None,
        "%s of them (%s and %d) are rules in document 2 that nothing yet tests" % (
            cap(word(len(untested))), ", ".join(str(n) for n in untested[:-1]), untested[-1]) if len(untested) > 1 else None,
        "%s fall to %s" % run_medians("naive_B", "dev_B"),
        "%s, %s and %s" % run_medians("lesion_B", "sham_B", "rescue_B"),
        "a donor's library %s" % run_medians("v_donor_B"),
        "of other parts %s" % run_medians("wrong_history_B"),
        "the 16 pairs of the four parts" if "one of the 16 pairs of the four parts just learned" in norm(A1) else None,
        "medians of %d replicates" % g2["params"]["N_REP"],
        "accepted, with no cut-off; factor 4" if g2["params"]["CONFIRM"] == 8 else None,
        "no content reset, factor %d" % g3["params"]["FACTOR"],
        "every cell of my four receipts, %d in all" % len(audits.RUNS),
        "the ruler FAILS at all three" if {aud["rulers"]["STRONG at %s" % st]["verdict"] for st in (
            "V01@RUN1", "S19@RUN2", "S19@RUN3")} == {"FAIL"} else None,
        "tries %d inherited re-indexings of it" % len(ladder.Cache.moves),
        "scored %.2f of 16 in the reader's run where the bound is %.2f (%s in my re-run" % (
            reader_cache, h16, mean(one, "ROTATION/CACHE", "across_epochs")),
        'A: "tunnel core (runner, worlds, rulers)" %d | %d standards + %d R0 + %d kernels | none | %d | %d' % (
            A["core"], A["std"], A["r0"], A["ker"], A["second"], A["census"]) if alloc_ok else None,
        "B: %d | %d R0 + %d R1/R2 + %d R8 + %d R4 | %d | %d | 0" % (
            B["core"], B["r0"], B["ker"], B["r8"], B["r4"], B["exp"], B["chal"]) if alloc_ok else None,
        "C: %d | %d runtimes and standards | %d | %d | %d" % (
            C["core"], C["org"], C["exp"], C["chal"], C["census"]) if alloc_ok else None,
        "is below both: %d against %d and %d" % (C["org"], a_org, b_org) if alloc_ok else None,
        "rejected all %d broken cases its author wrote. A second reader then wrote %d more, and by my count of that "
        "reader's scripts %d of them got through" % (
            first["mutants"], att["broken_cases_written_by_the_reader"], att["of_which_passed"]),
        "my run 2 has %d of %d clauses that fail in no cell; my run 3 has %d" % (
            len(run2c["cannot_fail"]), len(run2c["table"]), len(run3c["cannot_fail"])),
        "The harness holds %d, and %d sound cases" % (s["mutants"], s["sound_cases"]),
        "%d FAIL, %d BLOCKED, %d UNQUALIFIED, %d INDETERMINATE" % (
            mv["FAIL"], mv["BLOCKED"], mv["UNQUALIFIED"], mv["INDETERMINATE"]),
        "%s such cases are rejected, %s on reset and %s on capture and restore. %s escape" % (
            cap(word(reset_cases + restart_cases)), word(reset_cases), word(restart_cases), cap(word(hidden))),
        "reach is %s and exact repair reach from one flip is %s" % (
            rate(reach["VALLEY/STRICT"]["cold_exact"]), rate(reach["VALLEY/STRICT"]["repair1_exact"])),
        "is computed by %s gates" % word(len(indeterminate)),
        "%d pinned, at least one in each of the %d gates" % (s["known_escapes"], s["gates"])
        if s["gates_with_a_known_escape"] == s["gates"] else None,
        "MUTANTS ADDED. %d." % s["mutants"],
        "TESTS FIT FOR CI. %d, deterministic" % n_tests,
        "they missed " + SIGHT4 % "then " + ", and on version three " + SIGHT2,
        "Organisms %d%%" % (mine[2] + mine[3]),
        "%d tunnel, %d organisms, %d experiments, %d challenge, %d census" % (
            mine[0], mine[2] + mine[3], mine[1], mine[4], mine[5]),
        "a tiny R4 specimen by days 10 to 15" if "Days 10-15" in B_REPORT else None,
        "gates at days 30, 60, 90" if all(g in A1 for g in ("GATE 30", "GATE 60", "GATE 90")) else None,
        "ARRIVES IN DAYS 16 TO 30" if "## Days 16-30" in C5 and "power/attainability preflight" in C5 else None,
        "The first isomer runs are in days 1 to 15" if "## Days 1-15" in C5 else None,
        "C keeps neutrality at day 45" if "Gate 45" in C5 else None,
        "Gate 15 and Gate 45 by name" if "Gate 15" in C5 and "Gate 45" in C5 else None,
        "five of which name the faults to plant" if all(w in C2 for w in (
            "Inject:", "Reject:", "Fixtures:", "Catch holdout access", "Inject defects into")) else None,
        "The numbering skips 04" if not list(INPUTS2.glob("chatgpt56_04*")) else None,
        "O's cell has a selection pressure where C's has exposure"
        if "selection/evolution/lifetime pressure" in O1 and "resources, measurement, exposure)" in C1 else None,
    ],
    D2: [
        "one %d, all mine" % first["mutants"],
        "%d of its %d broken cases got through" % (att["of_which_passed"], att["broken_cases_written_by_the_reader"]),
        "%d of %d one-line changes to the gates'" % sight["R"],
        "two %d" % two["mutants"],
        "%d of %d, %d of %d and %d of %d changes unnoticed" % (sight["C"] + sight["F"] + sight["H"]),
        "three %d by the second reader alone, %s passing faults on no list, in %s gates, and one in the next "
        "experiment; %s changes unnoticed" % (three["mutants"], word(new_faults), word(new_gates), SIGHT2)
        if new_world == 1 else None,
        "three, as %d not read again amended" % s["mutants"],
        "every one of %d gates" % s["gates"] if "Every one of the 21 gates has an escape not on the list" in report2
        else None,
        "A fresh %d-bit key per life" % int(keys["params"]["key_bits"]),
        "an exact bound of %.2f correct of %d" % (keys["params"]["exact_nothing_carried_bound"], keys["params"]["N"]),
        "2,000 lives per organism" if keys["params"]["LIVES"] == 2000 and keys["params"]["F"] == 6 else None,
        "certified at 0, 0, 1.44, 9.46, 23.39 and 38.99 bits" if bits == ["0.00", "0.00", "1.44", "9.46", "23.39", "38.99"]
        else None,
        "where the bound for carrying nothing across epochs is %.2f (my re-run, %d lives" % (h16, world_one["lives"]),
        "carries nothing ................................... %s" % mean(one, "ROTATION/ELIM", "across_epochs"),
        "one cached table, 256 inherited re-indexings ...... %s" % mean(one, "ROTATION/CACHE", "across_epochs"),
        "one cached table, 16 inherited offsets ............ %s" % mean(one, "ROTATION/KEEPER", "across_epochs"),
        "the same, when the epoch adds an offset instead ... %s" % mean(one, "OFFSET/KEEPER", "across_epochs"),
        "at %s lives, gave %.2f for it" % (thousands(reader_world["lives"]), reader_cache),
        "The third organism is NOT_SHOWN at %d lives" % world_one["lives"]
        if one["ROTATION/KEEPER"]["across_epochs"]["answer"] == "NOT_SHOWN"
        and "At 4,000 lives it is CARRIED" in closure else None,
        "Their best expected score is %.2f of %d" % (h16, ladder.N),
        "Scores of 16 on the ninth pair (%d lives)" % lives,
        "trying its %d re-indexings against feedback" % len(ladder.Cache.moves),
        "The life shows eight of the nine pairs" if len(ladder.SHOWN) == 8 else None,
        "probability at least %.2f" % stats.POWER_FLOOR,
        "exact 99% interval" if stats.DESIGN_CONFIDENCE == 0.99 else None,
        "admit any bound from %.3f to %.3f where the truth is %.1f" % (
            bracket["by_organisms"][0], bracket["by_organisms"][1], rulers.BOUND),
        "best block of impostor trials (%d of 64), the upper end by the worst (%d of 64)" % (
            bracket["impostor_scores"][1], bracket["impostor_scores"][0]),
        "to the registered bound within 0.001"
        if 0.499 < bracket["at_registered_thresholds"][0] and bracket["at_registered_thresholds"][1] < 0.501 else None,
        "right 15 times in 16" if rulers.P_WEAKEST == 15 / 16 else None,
        "read from all %d cells of my four receipts" % len(audits.RUNS),
        "right on %d cells: %d yes, %d no" % (sum(bits_answered.values()), bits_answered["POSITIVE"], bits_answered["NEGATIVE"]),
        "In my run 2, %d of %d clauses fail in no cell and only %d fail by themselves" % (
            len(run2c["cannot_fail"]), len(run2c["table"]), alone2),
        "candidate runtimes (R0 12, Track-A kernel 13)" if mine[3] == 12 + 13 else None,
        "Organisms of every kind get %d, where the package gives %d and the two reviews %d and %d" % (
            mine[2] + mine[3], C["org"], a_org, b_org) if alloc_ok else None,
        "the tests missed " + SIGHT4 % "" + " changes at first sight, then " + SIGHT2 + " on version three",
        "lists %d faults they do not catch" % s["known_escapes"],
        "(CATALOGUED, QUALIFICATION_FIXTURE, ACTIVE_RUNTIME)" if all(w in C3 for w in (
            "- CATALOGUED", "- QUALIFICATION_FIXTURE", "- ACTIVE_RUNTIME")) else None,
        "for R3 and R7 are NEXT and RETIRE" if "-- NEXT" in C3 and "-- RETIRE" in C3 else None,
    ],
    D3: [
        "%d gates run today against %d sound cases and %d cases that must not pass" % (
            s["gates"], s["sound_cases"], s["mutants"]),
        "FAULT IT IS KNOWN NOT TO CATCH; %d ARE PINNED" % s["known_escapes"],
        "MISSED " + (SIGHT4 % "").upper() + " ONE-LINE CHANGES TO THE GATES, AND " + SIGHT2.upper() + " ON THE THIRD VERSION",
        "VERSION ONE: %d gates, %d sound cases, %d mutants, all mine" % (
            first["gates"], first["clean_cases"], first["mutants"]),
        "wrote %d broken cases and %d sound ones" % (
            att["broken_cases_written_by_the_reader"], att["sound_cases_written_by_the_reader"]),
        "%d of the %d got through, in %d of %d groups, and all %d sound cases were refused" % (
            att["of_which_passed"], att["broken_cases_written_by_the_reader"], att["sections_with_an_escape"],
            att["sections_probed"], att["of_which_rejected"]),
        "It also made %d one-line changes to the gates' logic; the tests missed %d" % (
            att["logic_changes"], att["logic_changes_not_noticed"]),
        "VERSION TWO: %d sound cases, %d mutants, %d known escapes" % (
            two["clean_cases"], two["mutants"], two["known_escapes"]),
        "found 14 new faults that passed in 11 gates, and 14 of the earlier cases still passing, 6 of them unlisted"
        if "| New attacks this round | 14 distinct unpinned passing faults in 11 gates" in closure
        and "| Still PASS | 14 (was 65): 8 are instances of a pinned escape, 6 are not pinned |" in closure else None,
        "the tests missed %d of %d, %d of %d and %d of %d" % (sight["C"] + sight["F"] + sight["H"]),
        "VERSION THREE: %d sound cases, %d mutants, %d known escapes, %d unit tests" % (
            three["sound_cases"], three["mutants"], three["known_escapes"],
            tests_in(ATTACK / "third_version" / "tests" / "test_harness.py")),
        "The second reader found %s passing faults on no list, in %s gates, and %s sound cases refused" % (
            word(new_faults), word(new_gates), word(refused)),
        "the tests missed %d of the closure reader's %d, and %d of the second reader's %d" % (sight["X"] + sight["Y"]),
        "%s of those %d alter no verdict" % (cap(word(no_verdict)), sight["Y"][0]),
        "VERSION THREE AS AMENDED, this one: %d sound cases, %d mutants, %d known escapes, %d unit tests" % (
            s["sound_cases"], s["mutants"], s["known_escapes"], n_tests),
        "The probe now holds all %d changes of the %s sets. %d could be carried over to this code, %d of them "
        "distinct. The tests notice %d (%d distinct); the %d they miss each alter no verdict" % (
            probe["changes"], word(len(sets)), probe["run"], probe["distinct_changes_run"], probe["noticed"],
            probe.get("distinct_changes_noticed", -1), len(probe["survived"])),
        "%d FAIL, %d BLOCKED, %d UNQUALIFIED, %d INDETERMINATE" % (
            mv["FAIL"], mv["BLOCKED"], mv["UNQUALIFIED"], mv["INDETERMINATE"]),
        "The %s are not broken" % word(mv["INDETERMINATE"]),
        "%s gates compute it here" % cap(word(len(indeterminate))),
        "G1.cell. %s fields present" % cap(word(len(meta.CELL_FIELDS))),
        "below %.2f the run is BLOCKED" % stats.POWER_FLOOR,
        "480 design units is attainable at %s; in 240 of 240, at %s, and blocked; in 466 of 480, at %s" % (
            rate(attain["HOLDS, design 480 of 480"]), rate(attain["HOLDS, design 240 of 240"]),
            rate(attain["HOLDS, design 466 of 480"])),
        "%d episodes, rate 1/2, alpha 1e-6, critical count %d" % (par["episodes"], par["critical_k"])
        if par["alpha"] == 1e-6 and par["exact_bound"] == 0.5 else None,
        "reaches it with probability %.5f" % par["power_at_weakest_positive"],
        "%d or more is POSITIVE; %d to %d is NEGATIVE" % (
            par["critical_k"], par["inverted_at_or_below"] + 1, par["negative_at_or_below"]),
        "%d to %d is undecided; %d or fewer is INVERTED" % (
            par["negative_at_or_below"] + 1, par["critical_k"] - 1, par["inverted_at_or_below"]),
        "four positives (%d of %d), a weak positive (%d), each impostor on nine disjoint blocks of seeds (%d to %d), "
        "and a scripted score at each of the six thresholds" % (
            bracket["positive_scores"][0], par["episodes"], bracket["weak_positive_score"],
            bracket["impostor_scores"][0], bracket["impostor_scores"][1])
        if bracket["positive_scores"] == [par["episodes"]] * 4 and par["impostor_blocks"] == 9
        and len(par["registered_thresholds"]) == 6 else None,
        "in %d pairs with the opposite cue and %d with the same" % (par["interchange_pairs"], par["interchange_pairs"]),
        "for each of the %s organisms of the panel" % word(2 * len(retain1.PANEL) + 1),
        "Capture after each of the %s steps" % word(steps),
        "(%d founders, %d proposals) must be compatible with it at level %s" % (
            par["founders_for_calibration"], par["search_budget"], par["calibration_alpha"]),
        "On five cells" if len(search.CELLS) == 5 else None,
        "Resolution at exact reach %s: counts from %d to %d of %d pass" % (
            rate(reach["NEEDLE/NEUTRAL"]["cold_exact"]), cal[0], cal[-1], par["founders_for_calibration"]),
        "of %s episodes, %d to %s right. At %d or fewer, or %s or more, the world fails" % (
            thousands(par["demand_episodes"]), eq[0], thousands(eq[-1]), out_low, thousands(2048 - out_low)),
        "nine small views" if len(torture.contexts([("DISTRACT", 0, 0, None)] * 6 + [("PROBE", None, 0, None)])) == 9
        else None,
        "Arms equal in at least %d of %d replicates" % (audits.HOLDS_AT, audits.N),
        "This audit and the next two are registered for %d replicates" % audits.N,
        "true in at most %d of its %d replicates, and holds when true in at least %d" % (
            audits.FAILS_AT, audits.N, audits.HOLDS_AT),
        "within 25%% of intact (or one task) in %d of %d replicates" % (audits.HOLDS_AT, audits.N),
        "power is a probability of at least 0.99",
        "%s placeholder words are refused" % word(len(stats.PLACEHOLDERS)),
        "G11.custody. %s fields." % cap(word(len(claims.CUSTODY_FIELDS))),
        "Seven facets at the first level, four more at the second, one each at the third and fourth"
        if (len(claims.L1), len(claims.L2), len(claims.L3), len(claims.L4)) == (7, 4, 1, 1) else None,
        "is reached with probability %s at a budget of 5, %s at 24, %s at 46 and %s at 47" % (
            rate(control["5"]), rate(control["24"]), rate(control["46"]), rate(control["47"])),
        "%d of %d clauses fail in no cell; %d fail by themselves" % (len(run2c["cannot_fail"]), len(run2c["table"]), alone2),
        "%d of 13; %d fails by itself" % (len(run3c["cannot_fail"]), alone3),
        "%d arms give %d series" % (sum(len(g) for g in aud["run3"]["arms_STRATEGIST"]["detail"]),
                                    len(aud["run3"]["arms_STRATEGIST"]["detail"])),
        "8 arms, %d series" % len(aud["run2"]["arms_BUILDER"]["detail"]),
        "within 25%% of intact in %d of %d replicates; faster in %d" % (
            aud["run2"]["sham_BUILDER"]["detail"]["within_margin"], aud["run2"]["sham_BUILDER"]["detail"]["n"],
            aud["run2"]["sham_BUILDER"]["detail"]["sham_faster"]),
        "of %d fields written down %d differ" % (len(set(audits.RUN2) | set(audits.RUN3)),
                                                 len(aud["run2_against_run3"]["detail"])),
        "right on %d cells of %d" % (sum(bits_answered.values()), sum(1 for r in audits.RUNS if "BITS" in r[3])),
        "the measured power of 0.9" if "Of ten blocks of 24 design replicates, one came out indeterminate" in norm(A1)
        else None,
        "a cache with %d inherited re-indexings passes" % len(ladder.Cache.moves),
        "three random permutations of %d symbols" % ladder.N,
        "The life shows eight of the nine pairs" if len(ladder.SHOWN) == 8 else None,
        "the best expected score is elimination: %.2f of %d" % (h16, ladder.N),
        "(%d lives; exploratory; a mean of %.2f or more is called CARRIED at alpha 1e-6)" % (
            lives, pairs["ELIM"]["ninth_pair"]["threshold"]),
        "one hard-wired formula scores 16.00" if "the hard-wired formula 16.00/3.49" in final2 else None,
        "%d faults the harness is known not to catch" % s["known_escapes"],
        "an estimator that ran 95%% of the registered budget (exact reach %s against %s)" % (
            rate(calib95["exact_at_95_percent"]), rate(calib95["exact_at_budget"])) if calib95 else None,
        "that does scores %d of %d" % (reads_bit["a_policy_that_reads_that_bit_scores"], reads_bit["of"])
        if reads_bit else None,
        "five: %d of %d, called a negative" % (one_in_five["it_scores"], one_in_five["of"]) if one_in_five else None,
        "a bound of %.2f where the truth is %.1f" % (0.48, rulers.BOUND)
        if esc["G3.exclusion"][0]["fault"].startswith("a bound of 0.48") else None,
        "%d tests, under a minute" % n_tests,
        "each of their %d cells" % len(audits.RUNS),
        "the positives score %d of %d" % (par["episodes"], par["episodes"]),
        "GM, the %d sound cases" % s["sound_cases"],
        "a null is read from a budget of 47 up" if control["46"] < 0.99 <= control["47"] else None,
        "which of these %d gates" % s["gates"],
    ],
    RM: [
        "Read from my own receipts by code, %d cells" % len(audits.RUNS),
        "ASTRA is right against my review on %s points. %s are taken into what runs or into the registration; %s are "
        "rules nothing yet tests" % (word(n_points), cap(word(n_points - len(untested))), word(len(untested))),
        "At first sight the tests missed " + SIGHT4 % "" + " one-line changes to the gates, and on the third version "
        + SIGHT2,
        "reading: %d gates, %d sound cases, %d cases that must not pass, %d known escapes pinned" % (
            s["gates"], s["sound_cases"], s["mutants"], s["known_escapes"]),
        "(%d unit tests;" % n_tests,
        "%d tests" % n_tests,
        "twelve modules" if len(modules) == 12 else None,
        "First read, of the draft: %d blocking and %d major defects" % (n_block, n_major),
        "%d of its %d broken cases got through and all %d of its sound cases were refused; %d of %d one-line changes" % (
            att["of_which_passed"], att["broken_cases_written_by_the_reader"], att["of_which_rejected"],
            att["logic_changes_not_noticed"], att["logic_changes"]),
        "scores %.2f of 16 where the bound is %.2f" % (reader_cache, h16),
        "22 of 33 errors the reader planted" if "22 of 33 planted errors pass" in report1 else None,
        "one cached table with %d inherited re-indexings" % len(ladder.Cache.moves),
        "of the %d defects, %d closed, %d partly, %d open; and %d blocking and %d major new ones" % (
            n_block + n_major, closed["CLOSED"], closed["PARTLY"], closed["OPEN"], new_block, new_major),
        "(%d of %d fresh ones went unnoticed)" % sight["C"],
        "by a fresh reader with three forks: %d blocking and %d major defects" % (block2, major2),
        "every one of the %d gates" % s["gates"],
        "Final round, of version three, by both readers: %d blocking and %d major defects, new or still open" % (
            f1_block + f2_block, f1_major + f2_major),
        "%s faults on no list passed the gates" % word(new_faults),
        "missed %s fresh one-line changes" % SIGHT2,
        "the checker as it then stood caught %d of %d, %d of %d sampled by rule, and %d of %d" % (chosen + sampled + fresh)
        if None not in chosen + sampled + fresh else None,
    ] + ([] if NO_FIRE else [FIRE]),
    HR: [
        "%d tests, under a minute" % n_tests,
        "its registered sound cases (%d) and rejects its registered mutants (%d)" % (s["sound_cases"], s["mutants"]),
        "%d FAIL, %d BLOCKED, %d UNQUALIFIED, %d INDETERMINATE" % (
            mv["FAIL"], mv["BLOCKED"], mv["UNQUALIFIED"], mv["INDETERMINATE"]),
        "The %s are not broken" % word(mv["INDETERMINATE"]),
        "%d faults are known NOT to be caught" % s["known_escapes"],
        "Mutation probe: %d one-line changes to the gates' logic, in %s sets. %d could be carried over to this "
        "version, %d of them distinct. The tests notice %d (%d distinct). The %d they do not notice alter no verdict" % (
            probe["changes"], word(len(sets)), probe["run"], probe["distinct_changes_run"], probe["noticed"],
            probe.get("distinct_changes_noticed", -1), len(probe["survived"])),
        "one %d %d %d of the reader's %d broken cases got through; %d of %d logic changes unnoticed" % (
            first["clean_cases"], first["mutants"], att["of_which_passed"], att["broken_cases_written_by_the_reader"],
            att["logic_changes_not_noticed"], att["logic_changes"]),
        "two %d %d an unlisted passing fault in every gate; %d of %d, %d of %d, %d of %d unnoticed" % (
            (two["clean_cases"], two["mutants"]) + sight["C"] + sight["F"] + sight["H"]),
        "three %d %d %s passing faults on no list, in %s gates; %s unnoticed" % (
            three["sound_cases"], three["mutants"], word(new_faults), word(new_gates), SIGHT2),
        "three, as %d %d not read amended" % (s["sound_cases"], s["mutants"]),
    ],
    AR: [
        "%d blocking and %d major defects" % (n_block, n_major),
        "%d gates, %d sound cases, %d mutants, 31 tests" % (first["gates"], first["clean_cases"], first["mutants"])
        if tests_in(ATTACK / "first_version" / "tests" / "test_harness.py") == 31 else None,
        "%d sound cases, %d mutants, 59 tests" % (two["clean_cases"], two["mutants"])
        if tests_in(ATTACK / "second_version" / "tests" / "test_harness.py") == 59 else None,
        "%d sound cases, %d mutants, 103 tests" % (three["sound_cases"], three["mutants"])
        if tests_in(ATTACK / "third_version" / "tests" / "test_harness.py") == 103 else None,
        "broken cases written by the reader .......... %d" % att["broken_cases_written_by_the_reader"],
        "passed by the first version ............... %d, in %d of %d parts probed" % (
            att["of_which_passed"], att["sections_with_an_escape"], att["sections_probed"]),
        "sound cases written by the reader ........... %d" % att["sound_cases_written_by_the_reader"],
        "rejected by the first version ............. %d" % att["of_which_rejected"],
        "one-line changes to gate logic .............. %d" % att["logic_changes"],
        "not noticed by the first version's tests .. %d" % att["logic_changes_not_noticed"],
        "(3,000 lives;" if reader_world["lives"] == 3000 else None,
        "carrying nothing is %.2f" % h16,
        "defects of the first read ................... %d" % (n_block + n_major),
        "closed, partly closed, open ............... %d, %d, %d" % (closed["CLOSED"], closed["PARTLY"], closed["OPEN"]),
        "new defects ................................. %d blocking, %d major" % (new_block, new_major),
        "earlier broken cases still passing .......... 14, of which 6 unlisted"
        if "| Still PASS | 14 (was 65): 8 are instances of a pinned escape, 6 are not pinned |" in closure else None,
        "new faults that passed ...................... 14, in 11 gates"
        if "| New attacks this round | 14 distinct unpinned passing faults in 11 gates" in closure else None,
        "one-line changes to gate logic .............. %d not noticed by the tests .................. %d" % (
            sight["C"][1], sight["C"][0]),
        "errors planted in the documents ............. 69 not caught by the checker ................. 35"
        if "| Planted errors in the checker mirror | 69; 35 pass |" in closure else None,
        "defects ..................................... %d blocking, %d major" % (block2, major2),
        "gates with a passing fault on no list ....... %d of %d" % (s["gates"], s["gates"])
        if "Every one of the 21 gates has an escape not on the list" in report2 else None,
        "one-line changes, the reader's set .......... %d, of which %d unnoticed" % (sight["F"][1], sight["F"][0]),
        "one-line changes, a fork's set .............. %d, of which %d unnoticed" % (sight["H"][1], sight["H"][0]),
        "errors planted in the documents ............. 13 not caught by the checker ................. 12"
        if "12 of 13 freshly planted errors also pass" in report2 else None,
        "defects, new or still open .................. %d blocking, %d major" % (f1_block, f1_major),
        "one-line changes to gate logic .............. %d not noticed by the tests .................. %d" % (
            sight["X"][1], sight["X"][0]),
        "errors planted, chosen by the reader ........ %d caught by the checker with its pins off ... %d" % (
            chosen[1], chosen[0]) if None not in chosen else None,
        "errors planted, sampled by rule ............. %d caught by the checker with its pins off ... %d" % (
            sampled[1], sampled[0]) if None not in sampled else None,
        "new defects ................................. %d blocking, %d major" % (f2_block, f2_major),
        "passing faults on no list ................... %d, in %d gates" % (new_faults, new_gates),
        "sound cases refused ......................... %d" % refused,
        "one-line changes to gate logic .............. %d not noticed by the tests .................. %d of which "
        "alter no verdict ................. %d" % (sight["Y"][1], sight["Y"][0], no_verdict),
        "errors planted in the documents ............. %d caught by the checker with its pins off ... %d" % (
            fresh[1], fresh[0]) if None not in fresh else None,
        "replaced mechanically in %d of the reports" % n_mechanical,
        "turned back into their characters in %d" % n_entities,
    ] + ["%s %.2f" % (label, reader_world["mean_correct_of_16"][name]["across_epochs"])
         for label, name in (
             ("carries nothing ..................................", "ELIM (carries nothing)"),
             ("offset-only solver that forgets at the boundary ..",
              "ACQ3 (offset-only solver, drops its table at the epoch boundary)"),
             ("the same, without the forgetting .................", "ACQ3-KEEP (offset-only solver, never drops its table)"),
             ("one cached table, 256 inherited re-indexings .....",
              "CACHE (one cached family table + fixed 256-way re-indexer)"))],
}
n_statements = 0
for p in EVERY:
    body = norm(text(p))
    wanted = STATEMENTS[p]
    n_statements += len(wanted)
    unsupported = [i for i, st in enumerate(wanted) if st is None]
    absent = [st[:70] for st in wanted if st is not None and norm(st) not in body]
    check("statements %s: %d rebuilt from receipts and sources" % (p.relative_to(HERE).as_posix(), len(wanted)),
          not unsupported and not absent,
          ("no longer supported by the data: items %s; " % unsupported if unsupported else "")
          + ("NOT IN THE FILE: %s" % absent if absent else ""))

# -------------------------------------------------------------------- tables
rows = {k: (int(a), int(b), int(c)) for k, a, b, c in re.findall(
    r"^    (tunnel core|organisms of every kind|running experiments, as its own bucket|independent challenge, second|"
    r"blind census)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", raw1, flags=re.M)}
check("table: the allocations of document 1 equal the three sources", alloc_ok and rows == {
    "tunnel core": (A["core"], B["core"], C["core"]), "organisms of every kind": (a_org, b_org, C["org"]),
    "running experiments, as its own bucket": (0, B["exp"], C["exp"]),
    "independent challenge, second": (A["second"], B["chal"], C["chal"]), "blind census": (A["census"], 0, C["census"])},
      "%s" % rows)
gate_rows = {g: (int(a), int(b), int(c)) for g, a, b, c in re.findall(
    r"^    (G\d+\.[a-z]+)\s.*?\s(\d+)\s+(\d+)\s+(\d+)\s*$", raw3, flags=re.M)}
want = {g: (r["clean"], r["mutants"], len(esc.get(g, []))) for g, r in rec["gates"].items()}
totals = re.search(r"^\s{40,}(\d+)\s+(\d+)\s+(\d+)\s*$", section(raw3, "4. THE GATES", "SPECIFIED AND NOT BUILT"), flags=re.M)
check("table: the gate table of document 3 equals the receipt, gate by gate, with its totals",
      gate_rows == want and totals is not None and tuple(int(x) for x in totals.groups()) == (
          s["sound_cases"], s["mutants"], s["known_escapes"]),
      "%d rows; differing: %s" % (len(gate_rows), sorted(set(gate_rows.items()) ^ set(want.items()))[:3]))
ok = True
for ls, rule, names in (("ASCENT", "both", ["ASCENT/STRICT", "ASCENT/NEUTRAL"]), ("NEEDLE", "strict", ["NEEDLE/STRICT"]),
                        ("NEEDLE", "neutral", ["NEEDLE/NEUTRAL"]), ("VALLEY", "strict", ["VALLEY/STRICT"]),
                        ("VALLEY", "neutral", ["VALLEY/NEUTRAL"])):
    got = re.search(r"^    %s\s+%s\s+(\d\.\d{4})\s+(\d\.\d{4})\s*$" % (ls, rule), raw3, flags=re.M)
    ok = ok and got is not None and all(got.groups() == (rate(reach[k]["cold_exact"]), rate(reach[k]["repair1_exact"]))
                                        for k in names)
check("table: the exact reach table of document 3 equals the receipt", ok)
audit_rows = re.findall(r"^    (G\d+\.[a-z]+)\s+(runs? [0-9, and]+?|run 2 against)\s{2,}(PASS|FAIL|UNQUALIFIED|BLOCKED)\s",
                        section(raw3, "7. THE FOURTH PACK", "Two cautions."), flags=re.M)
strong = {aud["rulers"]["STRONG at %s" % st]["verdict"] for st in ("V01@RUN1", "S19@RUN2", "S19@RUN3")}
check("table: the audit table of document 3 equals the receipt, row by row", audit_rows == [
    ("G9.clauses", "run 2", aud["run2"]["clauses"]["verdict"]), ("G9.clauses", "run 3", aud["run3"]["clauses"]["verdict"]),
    ("G9.arms", "run 3", aud["run3"]["arms_STRATEGIST"]["verdict"]), ("G9.arms", "run 2", aud["run2"]["arms_BUILDER"]["verdict"]),
    ("G9.sham", "run 2", aud["run2"]["sham_BUILDER"]["verdict"]), ("G9.sham", "run 3", aud["run3"]["sham_STRATEGIST"]["verdict"]),
    ("G10.setting", "runs 2 and 3", aud["run2"]["setting"]["verdict"]),
    ("G10.contrast", "run 2 against", aud["run2_against_run3"]["verdict"]),
    ("G10.ruler", "runs 1, 2, 3", "FAIL"), ("G10.ruler", "run 4", aud["rulers"]["BITS at BITS@KEYS"]["verdict"])]
    and strong == {"FAIL"} and aud["run2"]["setting"]["verdict"] == aud["run3"]["setting"]["verdict"], "%s" % audit_rows[:2])


def planted(name):
    """The receipt's key for an organism run with a key reuse planted in the harness."""
    found = [k for k in pairs if k.startswith(name + ",")]
    return found[0] if len(found) == 1 else None


def scores(key):
    return (mean(pairs, key, "ninth_pair"), mean(pairs, key, "control"))


FRESH = ["ELIM", "TABLE_CACHE", "TWO_TABLES", "SCHEMA_CACHE", "COMPOSER", "REPEAT_WATCHER"]
PLANTED = [planted("HIDER"), planted("SANDBAGGER"), planted("REPEAT_WATCHER")]
world_ok = (None not in PLANTED and sorted(pairs) == sorted(FRESH + PLANTED)
            and [pairs[k]["answer"] for k in FRESH] == ["NOT_SHOWN"] * 3 + ["COMBINED"] * 2 + ["NOT_SHOWN"]
            and all(pairs[k]["keys_fresh"] is True for k in FRESH)
            and [pairs[k]["arms_alone"] for k in PLANTED] == ["NOT_FROM_THIS_LIFE", "NOT_FROM_THIS_LIFE", "COMBINED"]
            and all(pairs[k]["answer"] == "KEY_REUSED" and pairs[k]["keys_fresh"] is False for k in PLANTED))
sec8 = section(raw3, "8. THE SMALLEST NEXT EXPERIMENT", "9. WHERE THIS HARNESS FAVOURS TRACK A")
pair_rows = re.findall(r"^    (ELIM|TABLE_CACHE|TWO_TABLES|SCHEMA_CACHE|COMPOSER|WATCHER|HIDER|SANDBAGGER)\s.*?(\d+\.\d\d)\s+(\d+\.\d\d)\s*$",
                       sec8, flags=re.M)
check("table: the unseen-pair table of document 3 equals the receipt, row by row, with the answers under it",
      world_ok and pair_rows == [(k.split(",")[0].replace("REPEAT_", ""),) + scores(k) for k in FRESH + PLANTED]
      and "With fresh keys the two arms call the fourth and fifth COMBINED and the others NOT_SHOWN." in norm(sec8)
      and "the arms alone call the hider and the sandbagger NOT_FROM_THIS_LIFE, and the watcher COMBINED" in norm(sec8)
      and "The custody check answers KEY_REUSED for all three." in norm(sec8), "%s" % pair_rows[:2])
LABELS = [("carries nothing", "ELIM"), ("every table seen, 256 fixed re-indexings", "TABLE_CACHE"),
          ("every way of combining two tables", "TWO_TABLES"), ("all 512 ways of combining three, no label read", "SCHEMA_CACHE"),
          ("composes the three its label points to", "COMPOSER"),
          ("hides last life's answer; one key in both arms", PLANTED[0]),
          ("watches for a repeated life; own key reused", PLANTED[2])]
two_cols = re.findall(r"^    ([a-z].+?)\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s*$",
                      section(raw2, "Scores of 16 on the ninth pair", "WHAT A SCORE ABOVE THE BOUND SAYS"), flags=re.M)
check("table: the unseen-pair table of document 2 equals the receipt, row by row and label by label",
      world_ok and two_cols == [(label,) + scores(k) for label, k in LABELS], "%s" % two_cols[:2])
names = {"procedure selector": "PROCEDURE_SELECTOR", "library, fixed builder": "LIBRARY_FIXED_BUILDER",
         "search-order selector": "SEARCH_ORDER_SELECTOR", "maturation": "MATURATION_UNLOCK", "memoriser": "MEMORIZER",
         "world parking": "WORLD_PARKING", "nested compiler cargo": "NESTED_COMPILER_CARGO",
         "hierarchical selector": "HIERARCHICAL_SELECTOR", "flattened twin": "FLATTENED_EQUIVALENT",
         "genuine learned updater": "GENUINE_LEARNED_UPDATER"}
answer_word = {"NEGATIVE": "negative", "POSITIVE": "POSITIVE", "AS_ITS_SOURCE": "as source", None: "none"}
run_no = {"V01@RUN1": "1", "S19@RUN2": "2", "S19@RUN3": "3"}
kit_rows = re.findall(r"^    ([a-z][a-z ,-]+?)\s{2,}(negative|POSITIVE|as source|none)\s{2,}(negative|POSITIVE|as source|none)"
                      r"\s+(no|runs? [0-9, ]+?)\s*$", section(raw2, "12. THE KIT", "WHAT THE RULERS RETURNED"), flags=re.M)
ok = len(kit_rows) == 10 == len(audits.KIT_ANSWERS)
for label, reuse, strong_, built in kit_rows:
    member = names.get(label)
    wanted_answers = audits.KIT_ANSWERS.get(member, {})
    in_runs = [run_no[r[1]] for r in audits.RUNS if r[0] == member and r[1] in run_no]
    wanted_built = "no" if not in_runs else ("run " if len(in_runs) == 1 else "runs ") + ", ".join(in_runs)
    ok = ok and (reuse, strong_, built) == (answer_word[wanted_answers.get("reuse")],
                                            answer_word[wanted_answers.get("strong")],
                                            wanted_built) and (bool(in_runs) != (member in audits.UNBUILT))
check("table: the kit table of document 2 equals the kit registry of the harness", ok, "%d rows" % len(kit_rows))
returned = re.findall(r"^    (strong|bits across families|bits, two boundaries|combination)\s+(run \d|none)\s+"
                      r"(FAIL|UNQUALIFIED|PASS)\s", raw2, flags=re.M)
where = {("strong", "run 1"): "STRONG at V01@RUN1", ("strong", "run 2"): "STRONG at S19@RUN2",
         ("strong", "run 3"): "STRONG at S19@RUN3", ("bits across families", "run 4"): "BITS at BITS@KEYS",
         ("bits, two boundaries", "none"): "BITS_TWO_BOUNDARIES at BITS@TWO", ("combination", "none"): "COMBINATION at BITS@PAIRS"}
check("table: what the rulers returned (document 2) equals the receipt, and no claim in the receipt is left out",
      len(returned) == 6 == len(aud["rulers"]) and all(
          (c, st) in where and aud["rulers"][where[(c, st)]]["verdict"] == v for c, st, v in returned)
      and {c for r in audits.RUNS for c in r[3]} == {"STRONG", "BITS"}, "%s" % returned[:2])
n_tables = sum(1 for name, _, _ in results if name.startswith("table:"))

# --------------------------------------------------- counts and consistency
sec9 = section(raw1, "9. GAPS IN THE PACKAGE", "10. THE THREE ALLOCATIONS")
sec10 = section(raw3, "10. KNOWN ESCAPES", "11. HOW TO RUN")
listed = re.findall(r"^  (G\d+\.[a-z]+)\s", sec10, flags=re.M)
groups = [int(n) for n in re.findall(r"^[A-Z][A-Z ]+ \((\d+)\)\.$", sec10, flags=re.M)]
blocks = re.split(r"^[A-Z][A-Z ]+ \(\d+\)\.$", sec10, flags=re.M)[1:]
fixtures = section(raw3, "APPENDIX: THE PACKAGE'S EIGHTEEN HISTORICAL FIXTURES", "END OF DOCUMENT 3")
check("counts: twelve points and which are untested, eight gaps, the known escapes gate by gate and group by group, "
      "and the fixtures 1 to 32 with four specified",
      n_points == 12 and "Twelve points." in sec3 and untested == [5, 6, 8, 12]
      and count(r"^  G\d\. ", sec9) == 8 and "for eight gaps" in text(RM)
      and sorted(listed) == sorted(e["gate"] for e in escapes) and sum(groups) == len(escapes) == len(listed)
      and set(listed) == set(rec["gates"])
      and [count(r"^  G\d+\.[a-z]+\s", b) for b in blocks] == groups
      and [int(x) for x in re.findall(r"^\s{4,5}(\d+) [a-z]", fixtures, flags=re.M)] == list(range(1, 33))
      and fixtures.count("specified") == 4 + 1,
      "%d points, untested %s; %d escapes listed in groups %s" % (n_points, untested, len(listed), groups))
fault = section(raw1, "B's line of evidence (ARGUED)", "Setting of run 2:")
check("counts: the first-fault table marks two of B's six lines as not reproduced, and the text says four of six",
      count(r"\s{2,}not (measured|built)\s*$", fault) == 2 and "reproduces four of the six lines" in norm(raw1)
      and "It reproduces four of B's six lines" in norm(raw1))
check("counts: the package's acceptance list has eleven conditions and its plan seven outputs",
      count(r"^- ", C1.split("Before calling the system a cross-physics observatory:")[1].split(
          "The reference harness")[0]) == 11
      and count(r"^\d\. ", C5.split("Day-90 outputs:")[1]) == 7
      and "The package's eleven conditions" in raw2 and "seven closing outputs" in raw2)
check("consistency: one verdict on the package's design, in every place it is stated",
      "VERDICT ON ITS DESIGN: REPAIR." in norm(raw1) and "Verdict on the design: REPAIR." in norm(raw1)
      and "Verdict on its design: REPAIR" in norm(text(RM)))
conj = {"SAVINGS": ["SAVINGS"], "LIFECYCLE": ["LIFECYCLE"],
        "U_TRANSFER": ["U_TRANSFER.frozen_U_good_on_C", "U_TRANSFER.frozen_U_good_on_narrower_C",
                       "U_TRANSFER.lesioned_line_bad_on_C"],
        "NESTING": ["NESTING.lesion_hurts", "NESTING.sham_harmless", "NESTING.rescue_restores", "NESTING.donor_V_helps"],
        "PROVENANCE": ["PROVENANCE.wrong_history_no_help", "PROVENANCE.random_store_no_help"],
        "REPEAT": ["REPEAT.D", "REPEAT.E"]}
ok = True
for cells, fn in ((g2["cells"], audits.clauses_run2), (g3["cells"], audits.clauses_run3)):
    for cell in cells.values():
        for name, parts in conj.items():
            ok = ok and sum(1 for o in cell["replicates"] if all(fn(o)[c] for c in parts)) == cell["counts"][name]
check("record: the thirteen clauses and the two effect thresholds reproduce the receipts' own conjunct counts",
      ok and audits.RUN2["effect_threshold"] == 4 and audits.RUN3["effect_threshold"] == g3["params"]["FACTOR"] == 2)
prereg = [text(COUNTERFEIT / n) for n in ("PREREG_gauntlet2.md", "PREREG_gauntlet3.md")]
check("record: the preregistrations of runs 2 and 3 state no power and no amortization horizon",
      all(not re.search(r"amortiz|horizon", p, flags=re.I) for p in prereg)
      and [line.strip()[:19] for p in prereg for line in p.splitlines() if re.search(r"\bpower\b", line, flags=re.I)]
      == ["Power maps commute,"])
check("record: 85 defects in three rounds, as my review states them",
      "They found 38, 21 and 26 defects" in norm(A_README) and "85 defects" in norm(A_README) and n_review == 72,
      "the checker of my review made %d checks, %d failed" % (n_review, review_failed))
check("record: every read is kept with its brief, its report, its scripts and the version it attacked",
      all((ATTACK / n).is_file() for n in (
          "BRIEF_to_the_reader.md", "REPORT_of_the_reader.md", "first_version/rso_harness/meta.py",
          "closure_reader/BRIEF.md", "closure_reader/REPORT.md", "closure_reader/scripts/p22_mutate.py",
          "second_reader/BRIEF.md", "second_reader/REPORT.md", "second_reader/REPORT_fork_fairness.md",
          "second_reader/REPORT_fork_gates_G1_to_G8.md", "second_reader/REPORT_fork_gates_G9_to_G12.md",
          "second_reader/scripts/comp/fresh_probe.py", "second_reader/scripts/h2/q06_my_mutations.py",
          "second_version/rso_harness/meta.py",
          "closure_reader/BRIEF_final.md", "closure_reader/REPORT_final.md",
          "closure_reader/scripts_final/p32_fresh_mutations.py",
          "second_reader/BRIEF_final.md", "second_reader/REPORT_final.md", "second_reader/scripts_final/first_sight.py",
          "third_version/rso_harness/meta.py")))

# ---------------------------------------------------------------- 6. pins
if not NO_PINS:
    for p in EVERY:
        name = p.relative_to(HERE).as_posix()
        check("pins %s: its text is the pinned text" % name, pin(p) == PINS[name], pin(p))
if not NO_PINS and not NO_MANIFESTS:
    line = re.compile(r"^- (\S+)\s+sha256:([0-9a-f]{64})")
    folders = sorted({p.parent for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts})
    missing, bad, unlisted = [], [], []
    for d in folders:
        if not (d / "MANIFEST.md").is_file():
            missing.append(d.relative_to(HERE).as_posix())
            continue
        named = dict(m.groups() for m in map(line.match, text(d / "MANIFEST.md").splitlines()) if m)
        bad += ["%s/%s" % (d.relative_to(HERE).as_posix(), n) for n, h in named.items()
                if not (d / n).is_file() or manifest_sha((d / n).read_bytes()) != h]
        unlisted += ["%s/%s" % (d.relative_to(HERE).as_posix(), p.name) for p in d.iterdir()
                     if p.is_file() and p.name != "MANIFEST.md" and p.name not in named]
    check("manifests: every folder with files has one, every file is listed, and every hash is the file's",
          not missing and not bad and not unlisted,
          "%d folders; missing %s; wrong %s; unlisted %s" % (len(folders), missing[:3], bad[:3], unlisted[:3]))

n_checks = len(results) + 1
if not NO_FIRE:
    check("the README states the number of checks and of tables parsed",
          ("makes %d checks" % n_checks) in text(RM) and ("%s tables are parsed" % word(n_tables)) in text(RM),
          "%d checks, %d tables" % (n_checks, n_tables))
failed = [n for n, ok, _ in results if not ok]
print("\n%d checks, %d failed; %d statements rebuilt" % (len(results), len(failed), n_statements))
sys.exit(1 if failed else 0)
