"""Do two extra lines close P54's pin blind spots? (soak P30)

Runs the SAME four mutations against P54's pin and against harmonia/soak/_patched_pin.py
(P54's pin + json.dumps(None) + {"examinee": "a"}). Aporia's test file is never edited;
the patch is demonstrated as a proposal.

NOTE: v1 of this script generated the patched pin from an embedded string and produced a
SyntaxError. Its baseline assertion caught that before any mutation was applied — the
result was never published and run_zoo_matrix.py was never touched.
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
 "M1 guard removed entirely": "",
 "M2 isinstance dropped":
    '''                if "examinee" not in rec or "probe_id" not in rec:
                    self.n_skipped_malformed = getattr(self, "n_skipped_malformed", 0) + 1
                    continue''',
 "M3 probe_id check dropped":
    '''                if not isinstance(rec, dict) or "examinee" not in rec:
                    self.n_skipped_malformed = getattr(self, "n_skipped_malformed", 0) + 1
                    continue''',
 "M4 counter not kept":
    '''                if not isinstance(rec, dict) or "examinee" not in rec or "probe_id" not in rec:
                    continue''',
}

PINS = {
 "P54 pin":     [sys.executable, "-m", "pytest",
                 "harmonia/experiments/test_checkpoint_robustness.py", "-q"],
 "patched pin": [sys.executable, "harmonia/soak/_patched_pin.py"],
}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.returncode


base = {k: run(c) for k, c in PINS.items()}
print("BASELINE (guard intact):", {k: f"exit {v}" for k, v in base.items()})
assert all(v == 0 for v in base.values()), "a pin is not green at baseline — mutation test is meaningless"

print(f"\n{'mutation':30s} {'P54 pin':>12s} {'patched pin':>14s}")
print("-" * 60)
score = {k: 0 for k in PINS}
try:
    for label, repl in MUTATIONS.items():
        SRC.write_text(original.replace(GUARD, repl), encoding="utf-8")
        row = {}
        for k, c in PINS.items():
            caught = run(c) != 0
            score[k] += caught
            row[k] = "CAUGHT" if caught else "survives"
        print(f"{label:30s} {row['P54 pin']:>12s} {row['patched pin']:>14s}")
finally:
    SRC.write_text(original, encoding="utf-8")
    assert SRC.read_text(encoding="utf-8") == original, "RESTORE FAILED"

print("-" * 60)
n = len(MUTATIONS)
print(f"{'mutation score':30s} {str(score['P54 pin']) + '/' + str(n):>12s} {str(score['patched pin']) + '/' + str(n):>14s}")
print("\nfile restored byte-identical: True")
print("cost of closing the gap: 2 lines, both already implied by HARMA-P18's four shapes.")
