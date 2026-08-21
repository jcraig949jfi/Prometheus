"""Is Pin C's 4/4 a property of the PIN or of the SUITE? (soak P32)

P31 scored test_verifier_lens.py at 4/4 against four mutations of the unknown_kind
abstention branch, and logged WITHHELD: the score is a suite-level fact, and which
test catches which mutation was never established. If test_unknown_kind_abstains_exactly
carries only one of the four, then P26's verdict -- that the pin is effective -- was
about the suite, and P31 mis-attributed the strength.

For each mutation, run the whole suite and record exactly WHICH tests fail. That
gives full attribution in four runs instead of 21x4.
"""
import re
import subprocess
import sys
from pathlib import Path

VL = Path("harmonia/experiments/verifier_lens.py")
original = VL.read_text(encoding="utf-8")

GUARD = """        return {
            "valid": None,
            "checks": {"kind": probe.kind},
            "kill_pattern": "unknown_kind",
        }"""
assert original.count(GUARD) == 1, "guard not uniquely located — abort untouched"

MUT = {
 "Q1 valid=False":            GUARD.replace('"valid": None', '"valid": False'),
 "Q2 valid=True":             GUARD.replace('"valid": None', '"valid": True'),
 "Q3 kill_pattern renamed":   GUARD.replace('"unknown_kind"', '"dispatch_miss"'),
 "Q4 branch removed":         "        pass",
}
PIN = "test_unknown_kind_abstains_exactly"
CMD = [sys.executable, "-m", "pytest", "harmonia/experiments/test_verifier_lens.py",
       "-q", "--tb=no", "-rf"]


def failing_tests():
    r = subprocess.run(CMD, capture_output=True, text=True, timeout=300)
    # -rf prints "FAILED path::test_name - ..." lines
    return r.returncode, sorted({m.group(1) for m in
                                 re.finditer(r"FAILED \S+::(\w+)", r.stdout)})


code, base_fail = failing_tests()
print(f"BASELINE: exit {code}, failing {base_fail or '(none)'}")
assert code == 0, "suite not green at baseline"

results = {}
try:
    for label, repl in MUT.items():
        VL.write_text(original.replace(GUARD, repl), encoding="utf-8")
        c, fails = failing_tests()
        results[label] = fails
finally:
    VL.write_text(original, encoding="utf-8")
    assert VL.read_text(encoding="utf-8") == original, "RESTORE FAILED"

print(f"\n{'mutation':26s} {'#tests red':>10s}  {'pin red?':>9s}  other tests that caught it")
print("-" * 100)
pin_score = 0
for label, fails in results.items():
    pin_hit = PIN in fails
    pin_score += pin_hit
    others = [f for f in fails if f != PIN]
    print(f"{label:26s} {len(fails):>10d}  {('YES' if pin_hit else 'no'):>9s}  "
          f"{', '.join(others[:3]) + (f' +{len(others)-3}' if len(others) > 3 else '') if others else '— none —'}")

print("-" * 100)
print(f"SUITE score : {sum(1 for f in results.values() if f)}/{len(MUT)}")
print(f"PIN score   : {pin_score}/{len(MUT)}")
solo = [l for l, f in results.items() if f == [PIN]]
print(f"mutations ONLY the pin catches: {solo or 'none'}")
redundant = [l for l, f in results.items() if len(f) > 1]
print(f"mutations caught by >1 test (redundant coverage): {len(redundant)} of {len(MUT)}")
print("\nfile restored byte-identical: True")
