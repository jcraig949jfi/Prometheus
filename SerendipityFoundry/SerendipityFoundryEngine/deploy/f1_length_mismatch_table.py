#!/usr/bin/env python3
"""WP-0a owner-run example: Herakles's F-1 table, before and after.

    python deploy/f1_length_mismatch_table.py

F-1 measured, at target length 32 and seed_root 110663, that a candidate whose
length differs from the declared `length` came back COMPLETED with a plausible
score whose ceiling was silently len(bits)/length:

    len(bits)   status      score    achievable ceiling
           16   COMPLETED    0.250   0.500
            8   COMPLETED    0.125   0.250
           32   COMPLETED    0.531   1.000

This reproduces both columns from one source of truth: the OLD scoring is
recomputed inline exactly as it was written, and the NEW behaviour comes from
the live executor.

ONE HONEST CAVEAT ABOUT THE SCORE COLUMN. F-1 records len(bits) but not the
CANDIDATE, and the score depends on its content. Running all-zeros reproduces
0.125 at n=8 and 0.531 at n=32 exactly, and gives 0.312 at n=16 where F-1
reports 0.250 -- an all-zero 16-bit candidate matches 10 of the first 16 target
bits, not 8, so their row used a different string. That does not touch the
finding: the CEILING column is len(bits)/length, independent of the candidate,
and it reproduces exactly. The ceiling is what the finding was about.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.executors import BitStringExecutor, WorkPackage           # noqa: E402

SEED = 110663
LENGTH = 32


def old_behaviour(bits, target):
    """Exactly the pre-repair path: match over the overlap, divide by the
    TARGET length, and return COMPLETED regardless."""
    if not bits or any(ch not in "01" for ch in bits):
        return "FAILED", None
    n = min(len(bits), len(target))
    score = (sum(1 for i in range(n) if bits[i] == target[i]) / len(target)
             if n else 0.0)
    return "COMPLETED", score


def main():
    ex = BitStringExecutor(length=LENGTH)
    target = ex.target_for(SEED)
    print("F-1 length-mismatch table -- target length %d, seed_root %d"
          % (LENGTH, SEED))
    print("engine: sfe.executors.BitStringExecutor")
    print()
    print("  len(bits) | BEFORE (F-1)            | AFTER (WP-0a)")
    print("            | status     score  ceil  | status     score")
    print("  ----------+-------------------------+------------------")
    ok = True
    for n in (16, 8, 32):
        bits = "0" * n
        ost, osc = old_behaviour(bits, target)
        r = ex.execute(WorkPackage(work_id="f1", world_id="f1", kind=ex.kind,
                                   payload={"bits": bits}, seed_root=SEED))
        ceil = min(n, LENGTH) / LENGTH
        print("  %9d | %-9s %6s %5.3f | %-9s %s"
              % (n, ost, ("%.3f" % osc) if osc is not None else "-", ceil,
                 r.status,
                 ("%.3f" % r.result["score"]) if r.status == "COMPLETED"
                 else "refused"))
        assert abs(ceil - min(n, LENGTH) / LENGTH) < 1e-12
        if n == LENGTH:
            if r.status != "COMPLETED" or abs(r.result["score"] - osc) > 1e-12:
                ok = False
                print("      *** the coherent row CHANGED -- a sealed result "
                      "would have moved ***")
        elif r.status != "FAILED":
            ok = False
            print("      *** still scored -- the finding is not closed ***")
    print()
    print("  the two mismatched rows are now refused on the same error path as")
    print("  a non-binary candidate; the coherent row is unchanged to the digit")
    print()
    print("  ceiling column reproduces F-1 exactly (0.500 / 0.250 / 1.000);")
    print("  the SCORE column is candidate-dependent and F-1 records only")
    print("  len(bits), so n=16 differs here -- see the module docstring")
    print()
    print("  RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
