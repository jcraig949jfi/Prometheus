"""Is Aporia P44's checkpoint fix PINNED? (soak P28)

P12's whole finding was that a fix landed unpinned and a guard that is only READ
tells you nothing. P26 verified a pin by simulating the regression. Same method
here, applied to the fix for my own P18: strip the guard back to the pre-fix
body and see whether the suite turns red.
"""
import re
import subprocess
import sys
from pathlib import Path

SRC = Path("harmonia/experiments/run_zoo_matrix.py")
original = SRC.read_text(encoding="utf-8")

GUARD = re.search(
    r"\n *# HARMA-P18.*?\n *continue\n", original, re.S)
assert GUARD, "guard block not found — abort without touching the file"

try:
    regressed = original.replace(GUARD.group(0), "\n")
    SRC.write_text(regressed, encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "pytest",
                        "harmonia/experiments/test_zoo_matrix.py", "-q"],
                       capture_output=True, text=True, timeout=100)
    tail = [l for l in r.stdout.splitlines() if l.strip()][-1]
    print("WITH GUARD REMOVED (pre-fix behaviour restored):")
    print("   ", tail)
    print("    exit:", r.returncode)
    pinned = r.returncode != 0
finally:
    SRC.write_text(original, encoding="utf-8")          # always restore
    assert SRC.read_text(encoding="utf-8") == original, "RESTORE FAILED"
    print("\nfile restored byte-identical:", SRC.read_text(encoding='utf-8') == original)

r2 = subprocess.run([sys.executable, "-m", "pytest",
                     "harmonia/experiments/test_zoo_matrix.py", "-q"],
                    capture_output=True, text=True, timeout=100)
print("baseline after restore:", [l for l in r2.stdout.splitlines() if l.strip()][-1])
print()
print(f"VERDICT: P44's fix is {'PINNED — suite goes red on regression' if pinned else 'UNPINNED — suite stays GREEN with the fix removed'}")
