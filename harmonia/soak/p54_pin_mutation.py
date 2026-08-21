"""Mutation-test Aporia P54's pin for the HARMA-P18 defect (soak P30).

P26, P28 and P29 each verified a pin by ONE regression: remove the guard, look
for red. All three logged the same weakness -- a partial regression is untested.
This closes it. A pin is only as good as the mutations it distinguishes, so this
applies four, each a plausible way the guard could rot.

Every mutation is applied in-place and reverted in a finally block; the file is
asserted byte-identical afterwards.
"""
import subprocess
import sys
from pathlib import Path

SRC = Path("harmonia/experiments/run_zoo_matrix.py")
original = SRC.read_text(encoding="utf-8")

GUARD = '''                if not isinstance(rec, dict) or "examinee" not in rec or "probe_id" not in rec:
                    self.n_skipped_malformed = getattr(self, "n_skipped_malformed", 0) + 1
                    continue'''
assert original.count(GUARD) == 1, "guard not uniquely located — abort untouched"

MUTATIONS = {
 "M1 guard removed entirely (pre-fix)":
    "",
 "M2 isinstance check dropped (keys only)":
    '''                if "examinee" not in rec or "probe_id" not in rec:
                    self.n_skipped_malformed = getattr(self, "n_skipped_malformed", 0) + 1
                    continue''',
 "M3 probe_id check dropped":
    '''                if not isinstance(rec, dict) or "examinee" not in rec:
                    self.n_skipped_malformed = getattr(self, "n_skipped_malformed", 0) + 1
                    continue''',
 "M4 skips silently, counter not kept":
    '''                if not isinstance(rec, dict) or "examinee" not in rec or "probe_id" not in rec:
                    continue''',
}

SUITE = [sys.executable, "-m", "pytest",
         "harmonia/experiments/test_checkpoint_robustness.py", "-q"]


def run():
    r = subprocess.run(SUITE, capture_output=True, text=True, timeout=120)
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    return r.returncode, (lines[-1][:58] if lines else "(none)")


base_code, base_tail = run()
print(f"BASELINE (guard intact): exit {base_code}  {base_tail}\n")
assert base_code == 0, "suite not green at baseline — a mutation test means nothing here"

print(f"{'mutation':42s} {'exit':>4s}  {'result':30s} verdict")
print("-" * 100)
caught = 0
try:
    for label, repl in MUTATIONS.items():
        SRC.write_text(original.replace(GUARD, repl), encoding="utf-8")
        code, tail = run()
        v = "CAUGHT" if code != 0 else "*** SURVIVES (blind spot) ***"
        caught += code != 0
        print(f"{label:42s} {code:>4d}  {tail:30s} {v}")
finally:
    SRC.write_text(original, encoding="utf-8")
    assert SRC.read_text(encoding="utf-8") == original, "RESTORE FAILED"

print("-" * 100)
print(f"mutation score: {caught}/{len(MUTATIONS)} caught")
print("file restored byte-identical: True")
