"""Re-audit every pin THIS CHANNEL blessed, at the standard it later adopted (soak P31).

P30 established that verifying a pin with ONE regression is inadequate: P54's pin
survived full removal but was blind to two partial rots. But P26 and P29 each
certified a pin using exactly that one-regression method, and both published
"PINNED" as a certain-strength claim. Those verdicts owe a re-test.

Self-dissent, per the doctrine that one attacks one's OWN prior conclusions first.
Every mutation is reverted in a finally block and byte-identity is asserted.
"""
import subprocess
import sys
from pathlib import Path

VL = Path("harmonia/experiments/verifier_lens.py")
LV = Path("harmonia/primitives/lattice_void_miner.py")

GUARD_B = """        for v in vals:
            try:
                out.append(op(v))
            except spec.transform_errors:
                dropped += 1
        return out, dropped"""
EMPTY_SIDE_B = """    if not ta or not tb:
        return {"null": "marginal_pairing", "killed": False, "degenerate": True,
                "perm_rates": [], "n_dropped": [drop_a, drop_b],
                "detail": "no in-domain values on one side; nothing to permute"}"""

GUARD_C = """        return {
            "valid": None,
            "checks": {"kind": probe.kind},
            "kill_pattern": "unknown_kind",
        }"""

PINS = {
 "Pin B — P40 domain-skip (blessed by my P29)": {
   "cmd": [sys.executable, "-m", "pytest", "harmonia/primitives/test_null_domain_skip.py", "-q"],
   "mutations": {
     "N1 try/except removed (what P29 tested)":
        (LV, GUARD_B, GUARD_B.replace("            try:\n                out.append(op(v))\n            except spec.transform_errors:\n                dropped += 1",
                                      "            out.append(op(v))")),
     "N2 catches but does not count drops":
        (LV, GUARD_B, GUARD_B.replace("                dropped += 1", "                pass")),
     "N3 narrows to ValueError (drops OverflowError)":
        (LV, GUARD_B, GUARD_B.replace("except spec.transform_errors:", "except ValueError:")),
     "N4 empty-side guard removed":
        (LV, EMPTY_SIDE_B, ""),
   }},
 "Pin C — P38 unknown_kind (blessed by my P26)": {
   "cmd": [sys.executable, "-m", "pytest", "harmonia/experiments/test_verifier_lens.py", "-q"],
   "mutations": {
     "Q1 valid=False (the P12 regression)":
        (VL, GUARD_C, GUARD_C.replace('"valid": None', '"valid": False')),
     "Q2 valid=True (mis-certifies)":
        (VL, GUARD_C, GUARD_C.replace('"valid": None', '"valid": True')),
     "Q3 kill_pattern renamed":
        (VL, GUARD_C, GUARD_C.replace('"unknown_kind"', '"dispatch_miss"')),
     "Q4 abstention branch removed (falls through)":
        (VL, GUARD_C, "        pass"),
   }},
}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    return r.returncode, (lines[-1][:44] if lines else "(none)")


for name, spec in PINS.items():
    print(f"\n{name}")
    code, tail = run(spec["cmd"])
    print(f"  BASELINE exit {code}  {tail}")
    if code != 0:
        print("  NOT GREEN AT BASELINE — mutation scoring skipped (P29 lesson)")
        continue
    caught = 0
    print(f"  {'mutation':46s} {'exit':>4s}  verdict")
    print("  " + "-" * 74)
    for label, (path, old, new) in spec["mutations"].items():
        src = path.read_text(encoding="utf-8")
        if src.count(old) != 1:
            print(f"  {label:46s} {'--':>4s}  TARGET NOT UNIQUE — skipped")
            continue
        try:
            path.write_text(src.replace(old, new), encoding="utf-8")
            c, _ = run(spec["cmd"])
            v = "CAUGHT" if c != 0 else "*** SURVIVES ***"
            caught += c != 0
            print(f"  {label:46s} {c:>4d}  {v}")
        finally:
            path.write_text(src, encoding="utf-8")
            assert path.read_text(encoding="utf-8") == src, f"RESTORE FAILED {path}"
    print(f"  {'-'*74}\n  mutation score: {caught}/{len(spec['mutations'])}")

print("\nall targets restored byte-identical.")
