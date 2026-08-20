"""Boundary case (Harmonia-A soak P2): does the R12 sandbox's pow bound generalize?

test_pow_bound_blocks_resource_exhaustion pins Pow with BOTH a parse-time bound
(exponent in [0,8], |base| <= 10_000) and an eval-time bound. Mult is in the
allowed node set and its eval-time handler (r12_grader.py:269) is an unguarded
`return a * b`.

Same threat, different operator. Probe: compile-only first (no execution), then
evaluate ONLY at deliberately small scale and extrapolate. This never allocates
large memory -- the finding is the ACCEPTANCE, not a demonstration of exhaustion.
"""
import os, sys, time
_HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
sys.path.insert(0, os.path.abspath(_HERE))
from r12_grader import compile_safe_conjecture, UnsafeConjecture  # noqa: E402

CASES = [
    ("pow in band (control, expect ACCEPT)",      "obj['f0'] ** 2 == 1"),
    ("pow out of band (control, expect REJECT)",  "obj['f0'] ** 9 == 0"),
    ("large legal literal via pow exp=8",         "obj['f0'] * (10 ** 8) > 0"),
    ("chained mult of pow-8 literals",            "(10 ** 8) * (10 ** 8) * (10 ** 8) > 0"),
    ("deep mult chain, 12 factors",               " * ".join(["(10 ** 8)"] * 12) + " > 0"),
    ("string literal repetition",                 "'a' * (10 ** 8) == ''"),
    ("string repetition, chained",                "'a' * (10 ** 8) * (10 ** 8) == ''"),
]

print(f"{'case':44s} {'compile':10s} note")
print("-" * 92)
accepted = []
for name, expr in CASES:
    src = "def conjecture(obj):\n    return " + expr
    try:
        p = compile_safe_conjecture(src)
        print(f"{name:44s} {'ACCEPT':10s}")
        accepted.append((name, expr, p))
    except UnsafeConjecture as e:
        print(f"{name:44s} {'REJECT':10s} {e}")
    except Exception as e:
        print(f"{name:44s} {'ERROR':10s} {type(e).__name__}: {e}")

# ---- cost extrapolation at SMALL scale only -------------------------------
print("\ncost extrapolation for integer mult chain (no large allocation):")
for k in (4, 6, 8):
    expr = " * ".join([f"(10 ** {k})"] * 12) + " > 0"
    src = "def conjecture(obj):\n    return " + expr
    try:
        p = compile_safe_conjecture(src)
        t0 = time.time()
        v = p.predicate({"f0": 1, "popcount": 1})
        dt = time.time() - t0
        digits = 12 * k
        print(f"  12 factors of 10^{k}: compiled+evaluated in {dt*1000:.2f} ms, "
              f"result magnitude ~10^{digits}")
    except UnsafeConjecture as e:
        print(f"  12 factors of 10^{k}: REJECT ({e})")

print("\nstring-repetition scale check (bounded, 10^6 not 10^8):")
src = "def conjecture(obj):\n    return len('a' * (10 ** 6)) > 0"
try:
    p = compile_safe_conjecture(src)
    print("  len() form ACCEPTED at compile")
except UnsafeConjecture as e:
    print(f"  len() form REJECT ({e})")
