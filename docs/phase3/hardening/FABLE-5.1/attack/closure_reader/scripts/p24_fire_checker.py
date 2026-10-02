"""Fire test of the SECOND check_hardening.py on the scratch mirror: one planted error at a time."""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE / "mirror" / "root"
PKG = ROOT / "docs" / "phase3" / "hardening" / "FABLE-5.1"
CHK = PKG / "check_hardening.py"
D1 = PKG / "01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md"
D2 = PKG / "02_HARDENING_DESIGN_v0.2_FABLE.md"
D3 = PKG / "03_TEST_HARNESS_SPEC_FABLE.md"
RM = PKG / "00_README.md"
HR = PKG / "harness" / "README.md"
AR = PKG / "attack" / "README.md"
ORIG = {p: p.read_text(encoding="utf-8") for p in (D1, D2, D3, RM, HR, AR)}


def run():
    r = subprocess.run([sys.executable, "-B", str(CHK)], capture_output=True, text=True, cwd=str(ROOT))
    return r.returncode, [ln[5:60] for ln in r.stdout.splitlines() if ln.startswith("FAIL")]


# kind: N = a digit changes (the 33 plants of the first fire test, adapted); W = words change and no digit does
PLANTS = [
    ("N", "bucket table: A's tunnel core 45 -> 40", D1, "    tunnel core                               45     30     35", "    tunnel core                               40     30     35"),
    ("N", "bucket breakdown: B '14 R1/R2' -> '24 R1/R2'", D1, "12 R0 + 14 R1/R2 + 6 R8 + 8 R4", "12 R0 + 24 R1/R2 + 6 R8 + 8 R4"),
    ("W", "a quotation of B altered by one word", D1, '"failure to reject a difference is not', '"failure to detect a difference is not'),
    ("W", "a registered sentence of the PACKAGE put in B's mouth in place of B's", D1,
     'B: "only demonstrated fakes are negatives". My', 'B: "Every clause needs a fixture capable of making it false.". My'),
    ("N", "'85 defects in drafts' -> 95", D1, "85 defects in drafts", "95 defects in drafts"),
    ("N", "'72 checks' -> 27 (doc 1)", D1, "checker with 72 checks", "checker with 27 checks"),
    ("W", "'Ten such cases are rejected' -> Twenty", D1, "Ten such cases are rejected", "Twenty such cases are rejected"),
    ("N", "valley cold reach 0.0000 -> 0.5000 (doc 1)", D1, "reach is 0.0000 and exact", "reach is 0.5000 and exact"),
    ("N", "run 2 figure 313.5 -> 331.5", D1, "313.5 fall to 20.5", "331.5 fall to 20.5"),
    ("N", "commit of my review ff1d7f0f4 -> ff1d7f0f5", D1, "(ff1d7f0f4)", "(ff1d7f0f5)"),
    ("W", "'Eleven known' escapes -> 'None known'", D1, "HARNESS ESCAPES. Eleven known, in eleven", "HARNESS ESCAPES. None known, in eleven"),
    ("W", "headline verdict REPAIR -> BUILD", D1, "NOT REACH ME. VERDICT ON ITS DESIGN: REPAIR.", "NOT REACH ME. VERDICT ON ITS DESIGN: BUILD. "),
    ("W", "kit table: memoriser negative -> POSITIVE", D2, "    memoriser                  negative      negative   2", "    memoriser                  POSITIVE      negative   2"),
    ("N", "allocation: experiments 15% -> 25%", D2, "running and analysing experiments ....................... 15%", "running and analysing experiments ....................... 25%"),
    ("N", "run 4: '2,000 lives' -> '20,000 lives'", D2, "2,000 lives per", "20,000 lives per"),
    ("W", "run 4: 'six families per life' -> 'sixty'", D2, "six families per life", "sixty families per life"),
    ("N", "run 4 bound in doc 2: 3.38 -> 3.83", D2, "an exact bound of 3.38 correct of 16", "an exact bound of 3.83 correct of 16"),
    ("N", "bound in doc 3: 3.38 -> 3.83", D3, "elimination: 3.38 of 16", "elimination: 3.83 of 16"),
    ("N", "'all 62 mutants I wrote' -> 26 (doc 2)", D2, "passed all 62 mutants", "passed all 26 mutants"),
    ("N", "gate table: G8.demand broken 9 -> 8", D3, "at the bound H5     1     9    1".replace("at the bound ", "    G8.demand       every baseline on the list sits    "),
     "    G8.demand       every baseline on the list sits    H5     1     8    1"),
    ("N", "audit table: sham '8 of 24 replicates' -> 18", D3, "                                                8 of 24 replicates;", "                                                18 of 24 replicates;"),
    ("W", "audit table: G9.sham on run 2 FAIL -> PASS", D3, "    G9.sham        run 2          FAIL ", "    G9.sham        run 2          PASS "),
    ("N", "audit table: run 3 '6 of 13' -> '9 of 13'", D3, "UNQUALIFIED   6 of 13; 1 fails by", "UNQUALIFIED   9 of 13; 1 fails by"),
    ("N", "'weakest positive 15/16' -> 13/16", D3, "critical count 51, weakest positive 15/16", "critical count 51, weakest positive 13/16"),
    ("N", "reach table: needle neutral 0.7298 -> 0.7928", D3, "    NEEDLE      neutral        0.7298", "    NEEDLE      neutral        0.7928"),
    ("N", "historical fixtures: 13 mapped to another gate (G12 -> G11)", D3, "13 same-code repeat called replication ...... G12, second", "13 same-code repeat called replication ...... G11, second"),
    ("W", "a 'specified' fixture relabelled as running, no digit", D3, "specified (two adapters)", "GM, two adapters ......."),
    ("N", "README: '(59 unit tests;' -> 95", RM, "(59 unit tests;", "(95 unit tests;"),
    ("N", "README: 'It runs: 21 gates' -> 12", RM, "It runs: 21 gates", "It runs: 12 gates"),
    ("W", "README: 'for eight gaps' -> 'for three gaps'", RM, "REPAIR, for eight gaps", "REPAIR, for three gaps"),
    ("N", "harness README: mutants (148) -> (184)", HR, "registered mutants (148)", "registered mutants (184)"),
    ("N", "attack README: passed 65 -> 56", AR, "............... 65, in 19 of 19", "............... 56, in 19 of 19"),
    ("W", "'nine; seven carry a number' -> 'nine; nine carry a number'", D1, "nine; seven carry a number", "nine; nine carry a number   "),
    # ---- words only
    ("W", "doc 1: 'Verdict of gate G10.ruler: FAIL at all three' -> PASS", D1, "G10.ruler:\nFAIL at all three.", "G10.ruler:\nPASS at all three."),
    ("W", "doc 1 sec 5 table: 'write provenance  not measured' -> 'measured'", D1, "V to U to S write provenance        not measured", "V to U to S write provenance        measured    "),
    ("W", "doc 1 sec 5 table: 'fresh U and S allocations  not built' -> 'built'", D1, "fresh U and S allocations           not built", "fresh U and S allocations           built    "),
    ("W", "doc 1 sec 3: 'Nothing that runs tests it.' -> 'Gate G12 tests it.' (point 5)", D1,
     'adapting during the test "is not a frozen learning rule". TAKEN as\n     a rule in document 2. Nothing that runs tests it.',
     'adapting during the test "is not a frozen learning rule". TAKEN as\n     a rule in document 2. Gate G12 tests it.         '),
    ("W", "doc 1 sec 7: 'search inside the cell  O' -> 'A'", D1, "    4  search inside the cell        O", "    4  search inside the cell        A"),
    ("W", "doc 1 sec 7: second build credited to C instead of O", D1, 'second build chosen by evidence  O: "Choose', 'second build chosen by evidence  C: "Choose'),
    ("W", "doc 1 sec 3: B's sentence attributed to C (quote kept)", D1, 'a ruler rejects it. B: "only demonstrated', 'a ruler rejects it. C: "only demonstrated'),
    ("W", "doc 1 sec 3: one registered B quote swapped for another registered B quote used elsewhere", D1,
     '9. CAPABILITY PROFILES. "Missing capabilities cap claims". B never', '9. CAPABILITY PROFILES. "Neither wins by calendar alone.". B never'),
    ("W", "doc 1 sec 8: 'C does carry' -> 'C does not carry' host cost", D1, "cost (C does carry", "cost (C does not carry"),
    ("W", "doc 1 sec 9: 'C injects faults at every layer' -> 'C injects no faults'", D1, "PASS. C injects faults at every layer and requires that the", "PASS. C injects no faults at any layer and requires that the"),
    ("W", "doc 1 sec 2: 'RUN (A); ARGUED (B)' -> 'RUN (A); RUN (B)'", D1, "RUN (A); ARGUED (B)", "RUN (A); RUN (B)   "),
    ("W", "doc 1 sec 1: R7 'retire' / 'defer' swapped", D1, "    R7             retire                        defer", "    R7             defer                         retire"),
    ("W", "doc 1 READ FIRST: 'NOT\\nVERIFIED' -> 'VERIFIED'", D1, "Its status here is NOT\nVERIFIED.", "Its status here is\nVERIFIED.    "),
    ("W", "doc 1 sec 10: 'INDETERMINATE, is returned by six gates' -> 'sixteen gates'", D1, "is returned by six gates", "is returned by sixteen gates"),
    ("W", "doc 1 sec 4: 'reproduces four of the six lines' -> 'six of the six'", D1, "reproduces four of the six lines", "reproduces six of the six lines "),
    ("W", "doc 2 sec 5: '(RUN, exploratory;' -> '(RUN, preregistered;' for the reader's world", D2,
     "WHAT THE READER SHOWED (RUN, exploratory;", "WHAT THE READER SHOWED (RUN, registered; "),
    ("W", "doc 2 sec 19: 'The two simulations of section 5 are exploratory.' -> 'are registered.'", D2,
     "The two simulations of section 5 are exploratory.", "The two simulations of section 5 are registered. "),
    ("W", "doc 2 kit: genuine learned updater strong POSITIVE -> negative", D2,
     "    genuine learned updater    none          POSITIVE   not built", "    genuine learned updater    none          negative   not built"),
    ("W", "doc 2 kit: world parking 'not built' -> built in runs", D2,
     "    world parking              negative      negative   not built", "    world parking              negative      negative   built    "),
    ("W", "doc 2 sec 12: 'reuse, run 2  UNQUALIFIED' -> PASS", D2, "    reuse, run 2                     UNQUALIFIED", "    reuse, run 2                     PASS       "),
    ("W", "doc 2 sec 6: SELECTION '(No gate\\n yet.)' -> '(Gate G11.)' ... words only", D2, "one unfiltered run is reported beside it. (No gate\n                  yet.)",
     "one unfiltered run is reported beside it. (A gate\n                  now.)"),
    ("W", "doc 2 sec 15: 'None is built for a real runner yet.' -> 'All are built for a real runner.'", D2,
     "None is built for a real runner yet.", "All are built for a real runner.    "),
    ("W", "doc 3 header: 'Eleven gates still have a fault' -> 'No gate still has a fault'", D3,
     "71 WRITTEN BY SOMEONE ELSE. Eleven gates still have a fault", "71 WRITTEN BY SOMEONE ELSE. No gates still have any fault  "),
    ("W", "doc 3 sec 7: 'They do not return:' -> 'They also return:'", D3, "They do not return: a family read", "They also return: a family read  "),
    ("W", "doc 3 sec 3: 'changes a reason text and no verdict' -> 'changes a verdict'", D3,
     "that is not changes a reason text and no verdict.", "that is not changes a verdict.                   "),
    ("W", "doc 3 sec 5: G6.restart 'a runtime that has just\\n run the opposite cue' -> 'a fresh runtime'", D3,
     "restore into a runtime that has just\n  run the opposite cue, continue.", "restore into a runtime that has never\n  run, and then continue.        "),
    ("W", "doc 3 sec 9: 'SIMULATED (300 lives; exploratory;' -> 'REGISTERED AND RUN (...; confirmatory;'", D3,
     "SIMULATED (300 lives; exploratory;", "SIMULATED (300 lives; confirmatory;"),
    ("W", "doc 3 sec 4: kit list of unbuilt members loses 'nested compiler cargo'", D3,
     "world parking, nested compiler cargo, hierarchical", "world parking, hierarchical                       "),
    ("W", "doc 3 sec 11: G8 escape 'second bit' -> 'first bit'", D3, "G8    The cue follows the second bit of a counter", "G8    The cue follows the first bit of a counter "),
    ("W", "doc 3 sec 8: fixture 17 loses '(in part)'", D3, "                                                  (in part)", "                                                           "),
    ("W", "README line 9: 'It certifies retention.' -> 'It certifies nested improvement.'", RM,
     "The reader refuted it by simulation. It certifies retention.", "The reader confirmed it by simulation. It certifies nesting."),
    ("W", "README: 'Simulated here; not registered.' -> 'Simulated here and registered.'", RM, "Simulated here; not registered.", "Simulated here and registered. "),
    ("W", "README: 'I take nine into what runs' -> 'I take twelve'", RM, "I take nine into what\n   runs", "I take twelve into what\n   runs"),
    ("W", "README: 'Eleven\\n   gates have a fault they are known not to catch' -> 'No gates'", RM,
     "148 cases broken on purpose. Eleven\n   gates have a fault", "148 cases broken on purpose. No\n   gates have a fault    "),
    ("W", "harness README: 'Eleven gates have a fault' -> 'No gate has a fault'", HR,
     "Eleven gates have a fault they are known NOT to catch.", "No gates have any fault they are known not to catch.  "),
    ("W", "attack README: 'as it wrote them, with one exception' -> 'with no exception'", AR,
     "as it wrote them, with one exception", "as it wrote them, with no exception "),
]

rows, tally = [], {"N": [0, 0], "W": [0, 0]}
for kind, what, path, old, new in PLANTS:
    text = ORIG[path]
    if text.count(old) != 1:
        rows.append(("PATTERN x%d" % text.count(old), kind, what, ""))
        continue
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
    try:
        rc, failed = run()
    finally:
        path.write_text(text, encoding="utf-8", newline="\n")
    tally[kind][0] += 1
    tally[kind][1] += rc != 0
    rows.append(("caught" if rc != 0 else "NOT CAUGHT", kind, what, "; ".join(failed)[:110]))
    print("%-11s %s %-92s %s" % rows[-1], flush=True)
print()
for r in rows:
    if r[0].startswith("PATTERN"):
        print("%-11s %s %s" % r[:3])
print("digit plants: %d planted, %d caught; word plants: %d planted, %d caught" % (tally["N"][0], tally["N"][1], tally["W"][0], tally["W"][1]))
rc, failed = run()
print("mirror restored: exit %d" % rc)
