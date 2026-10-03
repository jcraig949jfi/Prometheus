"""Fire test of check_hardening.py: plant one error in a scratch copy of the documents, run the checker, count what fails.

The checker copy has ROOT pointed at the real repository (read-only: sources, git show) and HERE at the scratch copy.
"""
import json, pathlib, shutil, subprocess, sys

sys.dont_write_bytecode = True
S = pathlib.Path(__file__).resolve().parent
REAL = pathlib.Path(r"F:/Prometheus-worktrees/dionysus-base-role")
SRC = REAL / "docs" / "phase3" / "hardening" / "FABLE-5.1"
RIG = S / "rig"
D1, D2, D3, RM = ("01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md", "02_HARDENING_DESIGN_v0.2_FABLE.md",
                  "03_TEST_HARNESS_SPEC_FABLE.md", "00_README.md")
REC = "harness/RECEIPT_harness_v0.json"


def fresh():
    if RIG.exists():
        shutil.rmtree(RIG)
    shutil.copytree(SRC, RIG, ignore=shutil.ignore_patterns("__pycache__"))
    p = RIG / "check_hardening.py"
    s = p.read_text(encoding="ascii")
    assert s.count("ROOT = HERE.parents[3]") == 1
    p.write_text(s.replace("ROOT = HERE.parents[3]", 'ROOT = pathlib.Path(r"%s")' % REAL.as_posix()), encoding="ascii", newline="\n")


def run():
    r = subprocess.run([sys.executable, "-B", str(RIG / "check_hardening.py")], capture_output=True, text=True, cwd=str(REAL))
    lines = r.stdout.splitlines()
    return [l[5:90] for l in lines if l.startswith("FAIL")], (lines[-1] if lines else r.stderr[-200:])


def edit(name, old, new, count=1):
    p = RIG / name
    s = p.read_bytes().decode("ascii")
    assert s.count(old) == count, (name, old, s.count(old))
    p.write_bytes(s.replace(old, new).encode("ascii"))


def receipt_edit(fn):
    p = RIG / REC
    d = json.loads(p.read_text(encoding="ascii"))
    fn(d)
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="ascii", newline="\n")


def swap_labels():
    a = "    carries nothing ................................... 3.37\n"
    b = "    composes three seen tables ........................ 16.00\n"
    p = RIG / D2
    s = p.read_bytes().decode("ascii")
    assert s.count(a) == 1 and s.count(b) == 1
    s = s.replace(a, "@@A@@").replace(b, "    carries nothing ................................... 16.00\n").replace(
        "@@A@@", "    composes three seen tables ........................ 3.37\n")
    p.write_bytes(s.encode("ascii"))


def g(d):
    d["gates"]["G9.arms"]["mutant_verdicts"][0]["verdict"] = "PASS"
    d["gates"]["G9.arms"]["escapes"] = ["run 3, STRATEGIST: eight arms"]


PLANTS = [
    ("P00 control: nothing planted", lambda: None),
    ("P01 control: a digit changed (D2: 3.38 correct of 16 -> 3.39)", lambda: edit(D2, "an exact bound of 3.38 correct of 16", "an exact bound of 3.39 correct of 16")),
    ("P02 misattribution in prose: a sentence of B's review attributed to the package (D1 s.3 item 1)",
     lambda: edit(D1, 'a ruler rejects it. B: "only demonstrated fakes are negatives"', 'a ruler rejects it. C: "only demonstrated fakes are negatives"')),
    ("P03 number written as a word (D3 headline: Eleven gates -> Two gates)", lambda: edit(D3, "Eleven gates still have a fault", "Two gates still have a fault")),
    ("P04 number written as a word (D3 s.2: Six gates return it -> Nine gates)", lambda: edit(D3, "Six gates return it here.", "Nine gates return it here.")),
    ("P05 number written as a word (README: right against my review on twelve points -> two points)",
     lambda: edit(RM, "ASTRA is right against my review on twelve points.", "ASTRA is right against my review on two points.")),
    ("P06 two row labels swapped in the composition table of D2 s.5 (carries nothing now scores 16.00)", swap_labels),
    ("P07 verdict word in prose (D1 s.5: FAIL at all three -> PASS at all three)", lambda: edit(D1, "FAIL at all three. No positive", "PASS at all three. No positive")),
    ("P08 reason reversed in a table (D2 s.12: yes to a selector and -> no to a selector and)", lambda: edit(D2, "FAIL          yes to a selector and", "FAIL          no to a selector and")),
    ("P09 unquoted statement about a source reversed (D1 s.8: it plants none -> it plants one)", lambda: edit(D1, "it plants none)", "it plants one)")),
    ("P10 evidence mark changed (D1 s.2 item 2: RUN (A); ARGUED (B) -> RUN (A); RUN (B))", lambda: edit(D1, "RUN (A); ARGUED (B)", "RUN (A); RUN (B)")),
    ("P11 status sentence reversed (D3 s.13: Nobody has attacked version two -> Two readers have attacked version two)",
     lambda: edit(D3, "Nobody has attacked version two.", "Two readers have attacked version two.")),
    ("P12 receipt body edited by hand: a registered mutant of G9.arms now PASSES in the receipt, status left PASS", lambda: receipt_edit(g)),
    ("P13 whose count it is (D2 s.2: An adversarial reader then wrote 71 -> The package's authors then wrote 71)",
     lambda: edit(D2, "An adversarial reader then wrote 71 broken cases", "The package's authors then wrote 71 broken cases")),
    ("P14 ranges kept, meaning reversed (D3 s.5 G3: 51 or more is POSITIVE -> NEGATIVE; 14 to 47 is NEGATIVE -> POSITIVE)",
     lambda: (edit(D3, "51 or more is\n  POSITIVE; 14 to 47 is NEGATIVE", "51 or more is\n  NEGATIVE; 14 to 47 is POSITIVE"))),
]

if __name__ == "__main__":
    caught = 0
    for name, plant in PLANTS:
        fresh()
        try:
            plant()
        except AssertionError as e:
            print("PATTERN PROBLEM %s: %s" % (name, e))
            continue
        failed, last = run()
        caught += bool(failed) and not name.startswith("P00")
        print("%-8s %s\n            %s %s" % ("CAUGHT" if failed else "passes", name, last, failed[:2]))
    shutil.rmtree(RIG, ignore_errors=True)
    print("planted (excluding the two controls): %d; caught: %d" % (len(PLANTS) - 2, caught - 1))
