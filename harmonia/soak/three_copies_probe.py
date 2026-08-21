"""The same fact lives in three places. Which copies are guarded? (soak P35)

  1. rp0.CONJ's truth field        (what the generator tells the model)
  2. CONJECTURE_REGISTRY stated_truth (documentation; grep finds NO reader)
  3. the z3 predicate itself       (what actually gets decided)

P35 showed copy 3 is guarded: corrupting it turns two suites red. This flips
copies 1 and 2 to find which, if any, are unprotected.
"""
import subprocess
import sys
from pathlib import Path

RP = Path("harmonia/experiments/reasoning_phase0.py")
Z3B = Path("harmonia/experiments/z3_backend.py")

CASES = {
 "copy 2: stated_truth flipped (registry doc)":
   (Z3B, '        "stated_truth": True,\n        "predicate": _z3_n2_plus_n_even,',
         '        "stated_truth": False,\n        "predicate": _z3_n2_plus_n_even,'),
 "copy 1: CONJ.truth flipped (generator)":
   (RP,  '    ("n2_plus_n_even", True, None, False),                 # true',
         '    ("n2_plus_n_even", False, None, False),                # true'),
}
SUITES = {
 "test_verifier_z3.py":   [sys.executable, "-m", "pytest", "harmonia/experiments/test_verifier_z3.py", "-q"],
 "test_verifier_lens.py": [sys.executable, "-m", "pytest", "harmonia/experiments/test_verifier_lens.py", "-q"],
 "coupling check (P34)":  [sys.executable, "harmonia/soak/_coupling_check_proposal.py"],
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300).returncode


base = {n: run(c) for n, c in SUITES.items()}
assert all(v == 0 for v in base.values()), f"not green at baseline: {base}"
print("baseline: all green\n")
print(f"{'mutation':46s} {'z3':>4s} {'lens':>5s} {'coupling':>9s}  verdict")
print("-" * 92)
for label, (path, old, new) in CASES.items():
    src = path.read_text(encoding="utf-8")
    if src.count(old) != 1:
        print(f"{label:46s} TARGET NOT UNIQUE — skipped")
        continue
    try:
        path.write_text(src.replace(old, new), encoding="utf-8")
        got = {n: run(c) for n, c in SUITES.items()}
    finally:
        path.write_text(src, encoding="utf-8")
        assert path.read_text(encoding="utf-8") == src, f"RESTORE FAILED {path}"
    caught = any(got[n] != base[n] for n in SUITES)
    print(f"{label:46s} {got['test_verifier_z3.py']:>4d} "
          f"{got['test_verifier_lens.py']:>5d} {got['coupling check (P34)']:>9d}  "
          f"{'CAUGHT' if caught else '*** UNGUARDED — nothing fires ***'}")
print("-" * 92)
print("copy 3 (the predicate) was shown CAUGHT by the previous probe.")
print("all files restored byte-identical: True")
