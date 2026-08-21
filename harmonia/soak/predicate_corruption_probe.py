"""What happens when a cid is registered with a WRONG predicate? (soak P35)

P34 logged WITHHELD: its proposed coupling check asserts registry PRESENCE, not
CORRECTNESS, so "a cid registered with a wrong predicate passes silently and
would produce confidently wrong verdicts rather than abstentions." That is the
higher-severity direction and it is testable.

The same fact lives in THREE places -- rp0.CONJ's truth field, the registry's
stated_truth, and the predicate itself -- and stated_truth is never read by any
code. This corrupts the predicate so z3 decides a different question, then asks:
does anything turn red, and what does the harness report?

z3_backend.py is restored in a finally block and asserted byte-identical.
"""
import subprocess
import sys
from pathlib import Path

Z3B = Path("harmonia/experiments/z3_backend.py")
original = Z3B.read_text(encoding="utf-8")

TRUE_PRED = """    # n^2 + n is even, for all integers n.
    return (n * n + n) % 2 == 0"""
WRONG_PRED = """    # CORRUPTED (HARMA-P35): now encodes "n^2 + n is ODD", a FALSE statement,
    # while rp0.CONJ still declares this conjecture TRUE.
    return (n * n + n) % 2 == 1"""
assert original.count(TRUE_PRED) == 1, "predicate not uniquely located — abort untouched"

SUITES = {
 "test_verifier_z3.py":   [sys.executable, "-m", "pytest", "harmonia/experiments/test_verifier_z3.py", "-q"],
 "test_verifier_lens.py": [sys.executable, "-m", "pytest", "harmonia/experiments/test_verifier_lens.py", "-q"],
}
COUPLING = [sys.executable, "harmonia/soak/_coupling_check_proposal.py"]   # P34's proposal


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    return r.returncode, (lines[-1][:46] if lines else "(none)")


HARNESS = (
 "import sys,collections; sys.path.insert(0,'harmonia/experiments')\n"
 "import reasoning_phase0 as rp0; from verifier_lens import verify\n"
 "p=[x for x in rp0.gen_R6(__import__('random').Random(7)) if x.data['cid']=='n2_plus_n_even']\n"
 "c=collections.Counter()\n"
 "for q in p: r=verify(q,q.ground_truth); c[(str(r['valid']),str(r['kill_pattern']))]+=1\n"
 "print('probes:',len(p),'outcomes:',dict(c))")

print("BASELINE (correct predicate):")
base = {n: run(c) for n, c in SUITES.items()}
base["coupling check (P34)"] = run(COUPLING)
for n, (c, t) in base.items():
    print(f"  {n:28s} exit {c}  {t}")
h = subprocess.run([sys.executable, "-c", HARNESS], capture_output=True, text=True, timeout=200)
print(f"  harness on n2_plus_n_even     {h.stdout.strip()[:76]}")

try:
    Z3B.write_text(original.replace(TRUE_PRED, WRONG_PRED), encoding="utf-8")
    print("\nWITH THE PREDICATE CORRUPTED (registry now says n^2+n is ODD):")
    reg = {n: run(c) for n, c in SUITES.items()}
    reg["coupling check (P34)"] = run(COUPLING)
    for n, (c, t) in reg.items():
        moved = "" if c == base[n][0] else "   <-- CHANGED"
        print(f"  {n:28s} exit {c}  {t}{moved}")
    h2 = subprocess.run([sys.executable, "-c", HARNESS], capture_output=True, text=True, timeout=200)
    print(f"  harness on n2_plus_n_even     {h2.stdout.strip()[:76]}")
finally:
    Z3B.write_text(original, encoding="utf-8")
    assert Z3B.read_text(encoding="utf-8") == original, "RESTORE FAILED"

changed = [n for n in base if reg[n][0] != base[n][0]]
print(f"\nturned red on the corrupted predicate: {changed or 'NONE'}")
print("file restored byte-identical: True")
