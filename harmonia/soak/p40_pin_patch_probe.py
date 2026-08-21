"""Does one OverflowError case close Pin B's N3 blind spot? (soak P31)

Scores P40's pin and the patched pin against the SAME four mutations.
Aporia's file is not edited; lattice_void_miner.py is restored byte-identically.
"""
import subprocess
import sys
from pathlib import Path

LV = Path("harmonia/primitives/lattice_void_miner.py")
original = LV.read_text(encoding="utf-8")

GUARD = """        for v in vals:
            try:
                out.append(op(v))
            except spec.transform_errors:
                dropped += 1
        return out, dropped"""
EMPTY_SIDE = """    if not ta or not tb:
        return {"null": "marginal_pairing", "killed": False, "degenerate": True,
                "perm_rates": [], "n_dropped": [drop_a, drop_b],
                "detail": "no in-domain values on one side; nothing to permute"}"""
assert original.count(GUARD) == 1 and original.count(EMPTY_SIDE) == 1

MUT = {
 "N1 try/except removed": (GUARD, GUARD.replace(
    "            try:\n                out.append(op(v))\n            except spec.transform_errors:\n                dropped += 1",
    "            out.append(op(v))")),
 "N2 does not count drops": (GUARD, GUARD.replace("                dropped += 1", "                pass")),
 "N3 narrows to ValueError": (GUARD, GUARD.replace("except spec.transform_errors:", "except ValueError:")),
 "N4 empty-side guard removed": (EMPTY_SIDE, ""),
}

PINS = {
 "P40 pin":     [sys.executable, "-m", "pytest", "harmonia/primitives/test_null_domain_skip.py", "-q"],
 "P40 + 1 case": [sys.executable, "harmonia/soak/_patched_pin_b.py"],
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180).returncode


base = {k: run(c) for k, c in PINS.items()}
print("BASELINE:", {k: f"exit {v}" for k, v in base.items()})
assert all(v == 0 for v in base.values()), "not green at baseline"

print(f"\n{'mutation':30s} {'P40 pin':>10s} {'P40 + 1 case':>14s}")
print("-" * 58)
score = {k: 0 for k in PINS}
try:
    for label, (old, new) in MUT.items():
        LV.write_text(original.replace(old, new), encoding="utf-8")
        row = {}
        for k, c in PINS.items():
            hit = run(c) != 0
            score[k] += hit
            row[k] = "CAUGHT" if hit else "survives"
        print(f"{label:30s} {row['P40 pin']:>10s} {row['P40 + 1 case']:>14s}")
finally:
    LV.write_text(original, encoding="utf-8")
    assert LV.read_text(encoding="utf-8") == original, "RESTORE FAILED"

n = len(MUT)
print("-" * 58)
print(f"{'mutation score':30s} {str(score['P40 pin'])+'/'+str(n):>10s} {str(score['P40 + 1 case'])+'/'+str(n):>14s}")
print("\nNOTE: the patched file covers N3 ALONE, not N1/N2/N4 — it is an ADDITIONAL")
print("case for the existing pin, not a replacement. Union is what matters.")
print("file restored byte-identical: True")
