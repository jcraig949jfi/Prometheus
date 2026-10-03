"""Fire test of check_hardening.py: plant one error at a time in a copy and count what the checker catches.

    python -B docs/phase3/hardening/FABLE-5.1/fire_test.py       about a minute; writes RECEIPT_fire_test.json

A copy of this folder, of my review and of the two input folders is made in a temporary place, and
the checker is run there. Nothing in the repository is changed except the receipt.

Each plant is run twice. With the pins on, any change to a file is caught, a change of spacing
included: that figure says only that the six files are frozen. With the pins off, the figure is what
the content checks catch by themselves, and it is the one to read. The plants that only the pins
catch are listed in the receipt.

The plants are the author's. A figure on plants chosen by the author of the checker is fitted to
the checker. The kinds are: a number the checker rebuilds; a number nothing rebuilds; a quotation;
who is said to have said it; a cell of a parsed table; a word; the form of a file; spacing alone.
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
ROOT = HERE.parents[3]
GIT_ROOT = os.environ.get("HARDENING_GIT_ROOT") or str(ROOT)
REL = HERE.relative_to(ROOT)
COPIED = (REL, pathlib.Path("docs/phase3/review/FABLE-5.1"), pathlib.Path("docs/phase3/design/FABLE-5.1"),
          pathlib.Path("roles/Dionysus/prompts/2026-10-01_review_charter"),
          pathlib.Path("roles/Dionysus/prompts/2026-10-02_hardening_v0.2"))
D1 = "01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md"
D2 = "02_HARDENING_DESIGN_v0.2_FABLE.md"
D3 = "03_TEST_HARNESS_SPEC_FABLE.md"
RM, HR, AR = "00_README.md", "harness/README.md", "attack/README.md"
TEXTS = (D1, D2, D3, RM, HR, AR)
KINDS = ("number", "pinned number", "quote", "attribution", "table", "word", "form", "whitespace")

# (kind, what, file, old, new). Each old must occur exactly once.
PLANTS = [
    # ---- numbers that the checker rebuilds from a receipt or a source
    ("number", "allocation table: A's tunnel core 45 -> 40", D1,
     "    tunnel core                               45     30     35",
     "    tunnel core                               40     30     35"),
    ("number", "breakdown line: B's 14 R1/R2 -> 24", D1, "12 R0 + 14 R1/R2 + 6 R8 + 8 R4", "12 R0 + 24 R1/R2 + 6 R8 + 8 R4"),
    ("number", "85 defects -> 95", D1, "85 defects in drafts", "95 defects in drafts"),
    ("number", "run 2 median 313.5 -> 331.5", D1, "313.5 fall to 20.5", "331.5 fall to 20.5"),
    ("number", "commit of my review altered", D1, "(ff1d7f0f4)", "(ff1d7f0f5)"),
    ("number", "first read: 11 blocking -> 1", D1, "first read, of the draft ........ 11 blocking",
     "first read, of the draft ........ 1 blocking"),
    ("number", "final round: 2 blocking -> 1", D1, "both readers again: 2 blocking", "both readers again: 1 blocking"),
    ("number", "power 0.865 -> 0.965", D1, "power 0.865", "power 0.965"),
    ("number", "closure read: 45 closed -> 55", D1, "45 closed, 11 partly", "55 closed, 1 partly"),
    ("number", "verdict split: 125 FAIL -> 152", D1, "125 FAIL, 99", "152 FAIL, 99"),
    ("number", "first-sight figures: 22 of 25, 34 of 44 -> 2 of 25, 4 of 44", D1, "missed 22 of 25, then 34 of 44",
     "missed 2 of 25, then 4 of 44"),
    ("number", "which of B's points are untested: four -> two", D1, "Four of them\n(5, 6, 8 and 12)",
     "Two of them\n(5, 6, 8 and 12)"),
    ("number", "run 4: 2,000 lives -> 20,000", D2, "2,000 lives per", "20,000 lives per"),
    ("number", "run 4 bound 3.38 -> 3.83", D2, "an exact bound of 3.38 correct of 16", "an exact bound of 3.83 correct of 16"),
    ("number", "what the organisms admit: 0.342 -> 0.442", D2, "0.342 to 0.686", "0.442 to 0.686"),
    ("number", "allocation: experiments 15% -> 25%", D2, "running and analysing experiments ....................... 15%",
     "running and analysing experiments ....................... 25%"),
    ("number", "unseen-pair table of document 2: 16.00 -> 6.00", D2,
     "    composes the three its label points to          16.00        3.49",
     "    composes the three its label points to           6.00        3.49"),
    ("number", "unseen-pair table of document 2: the cache 13.46 -> 3.46", D2,
     "    all 512 ways of combining three, no label read  13.46        3.48",
     "    all 512 ways of combining three, no label read   3.46        3.48"),
    ("number", "the reader's own figure 13.79 -> 13.97", D2, "gave 13.79 for it", "gave 13.97 for it"),
    ("number", "version three at first sight: 12 of 26 -> 2 of 26", D2, "12 of 26 and 20 of 54 changes unnoticed",
     "2 of 26 and 20 of 54 changes unnoticed"),
    ("number", "gate table: G8.demand broken 14 -> 13", D3,
     "G8.demand       every baseline on the list sits    H5     1    14    2",
     "G8.demand       every baseline on the list sits    H5     1    13    2"),
    ("number", "gate table: G6.reset sound 2 -> 3", D3,
     "G6.reset        after a reset a runtime behaves    H3     2     9    2",
     "G6.reset        after a reset a runtime behaves    H3     3     9    2"),
    ("number", "audit table: 8 of 24 -> 18 of 24", D3, "8 of 24 replicates;", "18 of 24 replicates;"),
    ("number", "reach table: 0.7298 -> 0.7928", D3, "    NEEDLE      neutral        0.7298              0.7757",
     "    NEEDLE      neutral        0.7928              0.7757"),
    ("number", "110 unit tests -> 101", D3, "110 unit tests", "101 unit tests"),
    ("number", "mutation probe: 236 noticed -> 244", D3, "notice 236 (211", "notice 244 (211"),
    ("number", "final round: 12 of the closure reader's 26 -> 2", D3, "missed 12 of the closure reader's 26",
     "missed 2 of the closure reader's 26"),
    ("number", "unseen-pair table of document 3: 3.43 -> 9.43", D3,
     "    TABLE_CACHE   every table seen, and 256       3.43        3.50",
     "    TABLE_CACHE   every table seen, and 256       9.43        3.50"),
    ("number", "unseen-pair table of document 3: the watcher's control 3.46 -> 13.46", D3,
     "    WATCHER       as above; the life's key       15.96        3.46",
     "    WATCHER       as above; the life's key       15.96       13.46"),
    ("number", "positive control at budget 46: 0.9896 -> 0.9986", D3, "0.9896 at 46", "0.9986 at 46"),
    ("number", "headline: 34 OF 44 -> 43 OF 44", D3, "22 OF 25, 34 OF", "22 OF 25, 43 OF"),
    ("number", "README: 21 gates -> 12", RM, "reading: 21 gates", "reading: 12 gates"),
    ("number", "README: 110 unit tests -> 101", RM, "(110 unit tests;", "(101 unit tests;"),
    ("number", "README: eight gaps -> nine", RM, "for eight gaps", "for nine gaps"),
    ("number", "README: the readers' own plants, 3 of 26 -> 13 of 26", RM, "stood caught 3 of 26", "stood caught 13 of 26"),
    ("number", "harness README: 258 -> 285", HR, "registered mutants (258)", "registered mutants (285)"),
    ("number", "attack README: 65 -> 56", AR, "passed by the first version ............... 65",
     "passed by the first version ............... 56"),
    ("number", "attack README: closure read, 34 -> 43", AR, "not noticed by the tests .................. 34",
     "not noticed by the tests .................. 43"),
    ("number", "attack README: final round, 15 faults -> 5", AR, "passing faults on no list ................... 15, in 12 gates",
     "passing faults on no list ................... 5, in 12 gates"),
    # ---- numbers that nothing rebuilds
    ("pinned number", "falsifier threshold: 20 registrations -> 2", D2, "at least 20 real", "at least 2 real"),
    ("pinned number", "falsifier threshold: six registered cells -> two", D2, "fewer than six registered cells",
     "fewer than two registered cells"),
    ("pinned number", "the enumeration behind the exact null: three symbols -> thirty", D2,
     "by enumeration at three symbols", "by enumeration at thirty symbols"),
    # ---- quotations
    ("quote", "a quotation of B altered by one word", D1, "failure to reject a difference is not\n     enough",
     "failure to detect a difference is not\n     enough"),
    ("quote", "a sentence that is in no source put in B's mouth", D1, '"only demonstrated fakes are negatives"',
     '"only demonstrated fakes count"'),
    ("quote", "a quotation of the package altered", D2, "standardizes accountability, not ontology",
     "standardizes accounting, not ontology"),
    # ---- who is said to have said it
    ("attribution", "a sentence of the package put in B's mouth; the quotation it displaces has no other use", D1,
     'rejects it. B: "only demonstrated fakes are negatives". My review',
     'rejects it. B: "A missing positive for a ruler\n     means UNQUALIFIED". My review'),
    ("attribution", "a sentence of B given to the package; the quotation is used twice", D2,
     '(B: "Missing capabilities cap claims").', '(the package: "Missing capabilities cap claims").'),
    ("attribution", "the side-by-side table: what A and B said of R7, swapped", D1,
     "    R7             retire                        defer",
     "    R7             defer                         retire"),
    ("attribution", "the synthesis marked as B's reading", D1, "  - MY READING, NOT B'S (ARGUED).", "  - B'S READING (ARGUED).         "),
    # ---- cells of parsed tables
    ("table", "kit table: memoriser negative -> POSITIVE", D2, "    memoriser                  negative      negative   run 2",
     "    memoriser                  POSITIVE      negative   run 2"),
    ("table", "kit table: genuine learned updater not built -> runs 1, 2", D2,
     "    genuine learned updater    none          POSITIVE   no",
     "    genuine learned updater    none          POSITIVE   runs 1, 2"),
    ("table", "what the rulers returned: strong, run 2 FAIL -> PASS", D2, "    strong                   run 2     FAIL ",
     "    strong                   run 2     PASS "),
    ("table", "unseen-pair table of document 2: two row labels swapped", D2,
     "    every table seen, 256 fixed re-indexings         3.43        3.50\n"
     "    every way of combining two tables                3.45        3.49\n",
     "    every way of combining two tables                3.43        3.50\n"
     "    every table seen, 256 fixed re-indexings         3.45        3.49\n"),
    ("table", "audit table: G9.sham on run 2 FAIL -> PASS", D3, "    G9.sham        run 2          FAIL ",
     "    G9.sham        run 2          PASS "),
    ("table", "audit table: the ruler for bits PASS -> FAIL", D3, "    G10.ruler      run 4          PASS ",
     "    G10.ruler      run 4          FAIL "),
    ("table", "historical fixtures: one specified row relabelled as running", D3, "specified (two adapters)",
     "G5, two adapters......."),
    ("table", "known escapes: one removed from the list", D3,
     "  G11.custody   an edited copy of the discovery generator presented as\n"
     "                a new family; generators are compared by hash\n", ""),
    ("table", "known escapes: one moved to another gate", D3, "  G9.arms       arms that are one series", "  G9.sham       arms that are one series"),
    ("table", "first fault table: not built -> built", D1, "    fresh U and S allocations           not built",
     "    fresh U and S allocations           built    "),
    ("table", "first fault table: not measured -> measured", D1, "    V to U to S write provenance        not measured",
     "    V to U to S write provenance        measured    "),
    # ---- words
    ("word", "verdict on the package REPAIR -> BUILD in the headline", D1, "ON ITS DESIGN: REPAIR.", "ON ITS DESIGN: BUILD."),
    ("word", "the package's harness: NOT VERIFIED -> VERIFIED", D1, "Its status here is NOT\nVERIFIED.", "Its status here is\nVERIFIED."),
    ("word", "the ruler for the strong claim: FAILS -> PASSES", D1, "the ruler FAILS at all three", "the ruler PASSES at all three"),
    ("word", "the watcher under the planted fault: COMBINED -> NOT_SHOWN", D3, "and the watcher COMBINED, which",
     "and the watcher NOT_SHOWN, which"),
    ("word", "a simulation called registered", D2, "RUN, exploratory; harness/rso_harness/ladder.py",
     "RUN, registered; harness/rso_harness/ladder.py"),
    ("word", "why the strong ruler failed at run 1: yes -> no", D2,
     "    strong                   run 1     FAIL          yes to a selector",
     "    strong                   run 1     FAIL          no to a selector"),
    ("word", "for reuse no ruler has been checked -> a ruler has", D2, "FOR REUSE NO RULER HAS BEEN CHECKED.",
     "FOR REUSE A RULER HAS BEEN CHECKED."),
    ("word", "falsifier 4: twice in a row -> once", D2, "Twice in a row, a second author's", "Once, a second author's"),
    ("word", "the custody check: no reader has attacked -> a reader has", D2,
     "adds a custody check that no reader has attacked", "adds a custody check that a reader has attacked"),
    ("word", "headline of document 3 reversed", D3, "EVERY GATE HAS AT LEAST ONE", "NO GATE HAS EVEN ONE"),
    ("word", "the list of escapes called complete", D3, "The list is not complete: each read has found",
     "The list is complete: each read has found"),
    ("word", "the mutation figure: fitted -> honest", D3, "The mutation figure for this version is fitted.",
     "The mutation figure for this version is honest."),
    ("word", "README: nobody has read the amendments -> a reader has", RM, "and nobody has read the amendments",
     "and a reader has read the amendments"),
    # ---- form
    ("form", "a line over 80 columns in document 3", D3, "END OF DOCUMENT 3", "END OF DOCUMENT 3" + " x" * 40),
    ("form", "a tab in document 2", D2, "END OF DOCUMENT 2", "END OF DOCUMENT 2\t"),
    ("form", "a section number skipped in document 1", D1, "\n13. LIMITS\n", "\n14. LIMITS\n"),
    # ---- spacing alone: in a two-column table the column says who said it
    ("whitespace", "side-by-side table: a cell of B moved under A", D1,
     "\n                                                 days 10 to 15; the simple\n",
     "\n                   days 10 to 15; the simple\n"),
    ("whitespace", "side-by-side table: both answers on R7 put on A's side", D1,
     "    R7             retire                        defer", "    R7             retire defer"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def run_checker(folder, *flags):
    env = dict(os.environ, HARDENING_GIT_ROOT=GIT_ROOT)
    r = subprocess.run([sys.executable, "-B", str(folder / "check_hardening.py"), "--no-fire", "--no-manifests"] + list(flags),
                       capture_output=True, text=True, env=env)
    failed = [line[5:85] for line in r.stdout.splitlines() if line.startswith("FAIL")]
    return r.returncode, failed


def mirror(tmp, tag):
    root = tmp / tag
    for rel in COPIED:
        shutil.copytree(ROOT / rel, root / rel, ignore=shutil.ignore_patterns("__pycache__"))
    return root / REL


def one(job):
    tmp, i, (kind, what, name, old, new) = job
    folder = mirror(tmp, "p%02d" % i)
    path = folder / name
    s = path.read_text(encoding="ascii")
    if s.count(old) != 1:
        return kind, what, "PATTERN x%d" % s.count(old), "", []
    path.write_bytes(s.replace(old, new).encode("utf-8"))
    with_pins, _ = run_checker(folder)
    without, failed = run_checker(folder, "--no-pins")
    return kind, what, "caught" if with_pins else "MISSED", "caught" if without else "MISSED", failed


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="rso_fire_"))
    try:
        base_rc, base_failed = run_checker(mirror(tmp, "base"))
        if base_rc != 0:
            print("the unchanged copy does not pass:", base_failed)
            return 1
        with ThreadPoolExecutor(max_workers=6) as pool:
            rows = list(pool.map(one, [(tmp, i, p) for i, p in enumerate(PLANTS)]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    lost = [what for _, what, a, _, _ in rows if a.startswith("PATTERN")]
    by_kind = {k: {"plants": 0, "caught_with_pins": 0, "caught_without_pins": 0} for k in KINDS}
    for kind, _, a, b, _ in rows:
        by_kind[kind]["plants"] += 1
        by_kind[kind]["caught_with_pins"] += a == "caught"
        by_kind[kind]["caught_without_pins"] += b == "caught"
    receipt = {
        "what": "fire test of check_hardening.py: one planted error per copy, checker run with and without its pins",
        "how_to_read": "with the pins on every change to a file is caught by construction. caught_without_pins is "
                       "what the content checks catch by themselves. The plants are the author's, so the figure is "
                       "fitted to the checker",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unchanged_copy_passes": base_rc == 0, "plants": len(rows),
        "caught_with_pins": sum(1 for r in rows if r[2] == "caught"),
        "caught_without_pins": sum(1 for r in rows if r[3] == "caught"),
        "by_kind": by_kind, "pattern_not_found": lost,
        "caught_only_by_the_pins": [{"kind": k, "plant": w} for k, w, a, b, _ in rows if a == "caught" and b == "MISSED"],
        "results": [{"kind": k, "plant": w, "with_pins": a, "without_pins": b, "first_check_that_failed": (f or [""])[0]}
                    for k, w, a, b, f in rows],
        "source_sha256_lf": {n: sha(HERE / n) for n in ("check_hardening.py", "fire_test.py") + TEXTS},
    }
    (HERE / "RECEIPT_fire_test.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n", encoding="ascii",
                                                 newline="\n")
    for kind, what, a, b, f in rows:
        print("%-7s %-7s %-14s %s%s" % (a, b, kind, what, ("   [" + f[0][:60] + "]") if f else ""))
    print("plants %d; caught with the pins on %d; caught with the pins off %d; pattern not found %d" % (
        len(rows), receipt["caught_with_pins"], receipt["caught_without_pins"], len(lost)))
    for kind in KINDS:
        print("   %-14s %2d planted, %2d caught without the pins" % (
            kind, by_kind[kind]["plants"], by_kind[kind]["caught_without_pins"]))
    return 1 if lost or receipt["caught_with_pins"] != len(rows) else 0


if __name__ == "__main__":
    sys.exit(main())
