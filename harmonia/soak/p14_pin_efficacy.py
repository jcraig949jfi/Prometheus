"""Does Aporia P40's pin for HARMA-P14 actually fire? (soak P29, corrected)

CORRECTION to this script's first version, made before publishing:
  1. It ran test_lattice_void_miner.py under pytest. That file's own docstring
     says `Run: python harmonia/experiments/test_lattice_void_miner.py` -- its
     test_*(spec, ...) signatures are ARGUMENTS filled by its own main(), which
     pytest misreads as missing fixtures. The 7 "errors" were my invocation.
  2. Its verdict compared `regressed exit != 0` instead of baseline-vs-regressed,
     so an already-red suite would have been credited with catching a regression.
     A pin only counts if it goes green -> red.
"""
import subprocess
import sys
from pathlib import Path

SRC = Path("harmonia/primitives/lattice_void_miner.py")
original = SRC.read_text(encoding="utf-8")

GUARDED = """        for v in vals:
            try:
                out.append(op(v))
            except spec.transform_errors:
                dropped += 1
        return out, dropped"""
PREFIX_BEHAVIOUR = """        for v in vals:
            out.append(op(v))
        return out, dropped"""
assert original.count(GUARDED) == 1, "guard block not uniquely located — abort untouched"

SUITES = {
    "test_null_domain_skip (pytest)":
        [sys.executable, "-m", "pytest", "harmonia/primitives/test_null_domain_skip.py", "-q"],
    "test_lattice_void_miner (own runner)":
        [sys.executable, "harmonia/experiments/test_lattice_void_miner.py"],
}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    return r.returncode, (lines[-1][:70] if lines else "(no output)")


base = {k: run(c) for k, c in SUITES.items()}
print("BASELINE (guard present):")
for k, (code, tail) in base.items():
    print(f"  {k:38s} exit {code}  {tail}")

try:
    SRC.write_text(original.replace(GUARDED, PREFIX_BEHAVIOUR), encoding="utf-8")
    reg = {k: run(c) for k, c in SUITES.items()}
    print("\nWITH GUARD REMOVED (pre-fix behaviour restored):")
    for k, (code, tail) in reg.items():
        print(f"  {k:38s} exit {code}  {tail}")
finally:
    SRC.write_text(original, encoding="utf-8")
    assert SRC.read_text(encoding="utf-8") == original, "RESTORE FAILED"
    print("\nfile restored byte-identical: True")

print("\nPER-SUITE VERDICT (green->red is the only thing that counts):")
pinned_any = False
for k in SUITES:
    b, r = base[k][0], reg[k][0]
    if b == 0 and r != 0:
        v, pinned_any = "PINS IT (green -> red)", True
    elif b == 0:
        v = "BLIND (green -> green)"
    else:
        v = f"UNINFORMATIVE (already exit {b} at baseline)"
    print(f"  {k:38s} {v}")
print(f"\nP40's fix is {'PINNED' if pinned_any else 'UNPINNED'}.")
