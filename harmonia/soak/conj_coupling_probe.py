"""Is the CONJ<->registry coupling actually enforced? (soak P34)

P33 claimed the generator's CONJ list and the verifier's cid registry are
"uncoupled literals". Searching first rather than inferring absence (the P25
lesson on P12) turned up test_registry_decides_the_five_cids, which DOES assert
every cid is registered -- but against a HARDCODED five-entry dict, not by
iterating rp0.CONJ. So the claim is half wrong and the mechanism matters.

Decisive test: add a sixth, UNREGISTERED conjecture to CONJ and see whether
anything in the repo turns red. Also measures whether the gap is harmful or
merely degrades to honest abstention.

reasoning_phase0.py is restored in a finally block and asserted byte-identical.
"""
import subprocess
import sys
from pathlib import Path

RP = Path("harmonia/experiments/reasoning_phase0.py")
original = RP.read_text(encoding="utf-8")

ANCHOR = '    ("sum_two_squares", True, None, False),                # true-ish placeholder'
assert original.count(ANCHOR) == 1, "CONJ anchor not unique — abort untouched"
SIXTH = ANCHOR + '\n    ("harma_p34_unregistered_conj", False, 7, False),      # ADDED: no registry entry'

SUITES = {
 "test_verifier_z3.py":     [sys.executable, "-m", "pytest", "harmonia/experiments/test_verifier_z3.py", "-q"],
 "test_verifier_lens.py":   [sys.executable, "-m", "pytest", "harmonia/experiments/test_verifier_lens.py", "-q"],
 "test_reasoning_phase0.py":[sys.executable, "-m", "pytest", "harmonia/experiments/test_reasoning_phase0.py", "-q"],
}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    return r.returncode, (lines[-1][:46] if lines else "(none)")


print("BASELINE (five cids):")
base = {}
for n, c in SUITES.items():
    base[n] = run(c)
    print(f"  {n:28s} exit {base[n][0]}  {base[n][1]}")

try:
    RP.write_text(original.replace(ANCHOR, SIXTH), encoding="utf-8")
    print("\nWITH A SIXTH, UNREGISTERED CONJECTURE ADDED TO CONJ:")
    reg = {}
    for n, c in SUITES.items():
        reg[n] = run(c)
        moved = "" if reg[n][0] == base[n][0] else "   <-- CHANGED"
        print(f"  {n:28s} exit {reg[n][0]}  {reg[n][1]}{moved}")

    # what does the harness DO with the unregistered cid?
    probe = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0,'harmonia/experiments');\n"
         "import reasoning_phase0 as rp0; from verifier_lens import verify\n"
         "p=[x for x in rp0.gen_R6(__import__('random').Random(7)) "
         "if x.data['cid']=='harma_p34_unregistered_conj']\n"
         "print('probes emitted:', len(p))\n"
         "import collections; c=collections.Counter()\n"
         "for q in p:\n"
         "    r=verify(q,q.ground_truth); c[(str(r['valid']),str(r['kill_pattern']))]+=1\n"
         "print('verify outcomes:', dict(c))\n"
         "r=verify(p[0], 'a bogus claimed answer')\n"
         "print('WRONG-ANSWER outcome:', r['valid'], r['kill_pattern'])"],
        capture_output=True, text=True, timeout=200)
    print("\nharness behaviour on the unregistered cid:")
    for l in (probe.stdout + probe.stderr).splitlines():
        if l.strip():
            print("   ", l[:96])
finally:
    RP.write_text(original, encoding="utf-8")
    assert RP.read_text(encoding="utf-8") == original, "RESTORE FAILED"

changed = [n for n in SUITES if reg[n][0] != base[n][0]]
print(f"\nsuites that turned red on the added cid: {changed or 'NONE'}")
print("file restored byte-identical: True")
