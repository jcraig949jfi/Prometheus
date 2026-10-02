"""A second reader's fire test of the rewritten check_hardening.py, pins off: errors planted one at a time in a scratch mirror."""
import os, pathlib, subprocess, sys
sys.dont_write_bytecode = True
M = pathlib.Path("mirror").resolve()
P = M / "docs/phase3/hardening/FABLE-5.1"
D1, D2, D3, RM = "01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md", "02_HARDENING_DESIGN_v0.2_FABLE.md", "03_TEST_HARNESS_SPEC_FABLE.md", "00_README.md"
ENV = dict(os.environ, HARDENING_GIT_ROOT="F:/Prometheus-worktrees/dionysus-base-role")
def check():
    r = subprocess.run([sys.executable, "-B", str(P / "check_hardening.py"), "--no-fire", "--no-manifests", "--no-pins"],
                       cwd=str(M), capture_output=True, text=True, env=ENV)
    return sorted(l.split(" -- ")[0][:95] for l in r.stdout.splitlines() if l.startswith("FAIL"))
PLANTS = [
 ("headline of D3: 24 ARE PINNED -> 42", D3, "FAULT IT IS KNOWN NOT TO CATCH; 24 ARE PINNED", "FAULT IT IS KNOWN NOT TO CATCH; 42 ARE PINNED"),
 ("D3 s10: group count (14) -> (41)", D3, "THE GATE READS A DECLARATION (14).", "THE GATE READS A DECLARATION (41)."),
 ("D2 s5 table: two row labels swapped", D2,
  "    carries nothing                                  3.48        3.48\n    every table seen, 256 fixed re-indexings         3.43        3.50\n    every way of combining two tables                3.45        3.49\n    all 512 ways of combining three, no label read  13.46        3.48\n    composes the three its label points to          16.00        3.49",
  "    composes the three its label points to           3.48        3.48\n    every table seen, 256 fixed re-indexings         3.43        3.50\n    every way of combining two tables                3.45        3.49\n    all 512 ways of combining three, no label read  13.46        3.48\n    carries nothing                                 16.00        3.49"),
 ("D1 s5: the ruler FAILS at all three -> PASSES", D1, "strong claim the ruler FAILS at all three.", "strong claim the ruler PASSES at all three."),
 ("D2 s12: 'yes to a selector' -> 'no to a selector'", D2, "FAIL          yes to a selector\n                                                     and a fixed builder", "FAIL          no to a selector\n                                                     and a fixed builder "),
 ("D1 s3: a B quotation attributed to the package", D1, 'rejects it. B: "only demonstrated fakes are negatives".', 'rejects it. C: "only demonstrated fakes are negatives".'),
 ("D3 s12: who read it", D3, "Three reads by readers of my own model family.", "Three reads by three outside laboratories.   "),
 ("D3 s3: whose count the 65 of 71 is", D3, "by my count of the labels in its\n      scripts:", "by the reader's own count, in its\n      report: "),
 ("D2 s17: falsifier 6's last clause reversed", D2, "that can happen only if the world leaks.", "that cannot happen at all.              "),
 ("D3 s8: WHAT IT WOULD NOT SHOW -> ALSO SHOW", D3, "WHAT IT WOULD NOT SHOW. How it was combined.", "WHAT IT WOULD ALSO SHOW. How it was combined"),
 ("D2 s12: FOR REUSE NO RULER HAS BEEN CHECKED -> A RULER HAS", D2, "FOR REUSE NO RULER HAS BEEN CHECKED.", "FOR REUSE A RULER HAS BEEN CHECKED. "),
 ("D3 s5 G8: 929 to 1,119 -> 829 to 1,219", D3, "929 to 1,119 right", "829 to 1,219 right"),
 ("README: eight taken, four untested -> twelve taken", RM, "Eight are taken into\n   what runs or into the registration; four are rules nothing yet tests.", "Twelve are taken into\n   what runs or into the registration; none is a rule nothing yet tests."),
 ("D2 s5: who proved the uniformity", D2, "The second\nreader proved this and checked it by enumeration at three symbols.", "The author\nproved this, and checked it by enumeration at sixteen symbols.    "),
 ("D3 s3: 'one of which alters no verdict' -> 'all of which alter one'", D3, "the tests missed 22, one of which alters no verdict.", "the tests missed 22, all of which alter a verdict.  "),
 ("D3 s5 G3: 14 to 47 is NEGATIVE -> POSITIVE", D3, "POSITIVE; 14 to 47 is NEGATIVE", "POSITIVE; 14 to 47 is POSITIVE"),
 ("D2 s5: the class excluded widened to three families", D2, "organism that uses at most two families", "organism that uses at most three families"),
 ("D3 s10: an escape's gate renamed G8.demand -> G6.reset", D3, "  G8.demand     the cue follows the fourth bit of a counter the organism", "  G6.reset      the cue follows the fourth bit of a counter the organism"),
]
base = check()
print("baseline failing checks on the mirror:", len(base))
caught = 0
for what, fname, old, new in PLANTS:
    p = P / fname
    s = p.read_text(encoding="ascii")
    if s.count(old) != 1:
        print("PATTERN(%d)  %s" % (s.count(old), what)); continue
    p.write_text(s.replace(old, new), encoding="ascii", newline="\n")
    got = check()
    p.write_text(s, encoding="ascii", newline="\n")
    new_fails = [g for g in got if g not in base]
    caught += bool(new_fails)
    print("%-7s %s%s" % ("CAUGHT" if new_fails else "passes", what, ("   <- " + new_fails[0][:70]) if new_fails else ""))
print("planted %d, caught %d (pins off)" % (len(PLANTS), caught))
assert check() == base
