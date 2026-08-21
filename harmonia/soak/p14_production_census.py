"""Is HARMA-P14's defect LATENT or LIVE in production? (soak P29, v2 — executed)

v1 of this file was DISCARDED before publication: overlapping globs double-counted
files, `raise` statements were counted anywhere in the file rather than inside
operators, and a `/`-counting regex flagged comments and paths. It returned
"5 of 5 exposed", which is what a census returns when it measures nothing.

v2 imports the ACTUAL production operator set and calls each operator on realistic
invariant values. Executing lens, not reading lens.

EXPOSED means: the operator raises on inputs that plausibly appear on a real side,
which pre-fix crashed null_marginal_pairing (P14) because it called f(x) bare.
"""
import sys
from pathlib import Path

sys.path.insert(0, ".")
from theseus.generators.a3_functional_identity import OPERATORS  # noqa: E402

# Values that actually occur in a3 sides: knot/EC invariants incl. 0 and negatives.
PROBES = [0, 1, 2, 3, 5, 12, 100, -1, -3, -12]

print(f"production operators in a3 OPERATORS: {len(OPERATORS)}\n")
print(f"{'operator':22s} {'raises on':>34s}   {'error types':30s}")
print("-" * 92)
raising = {}
for name, op in sorted(OPERATORS.items()):
    bad, errs = [], set()
    for v in PROBES:
        try:
            op(v)
        except Exception as e:
            bad.append(v)
            errs.add(type(e).__name__)
    if bad:
        raising[name] = (bad, errs)
    shown = str(bad) if bad else "-- total on all probes --"
    print(f"{name:22s} {shown:>34s}   {','.join(sorted(errs)) or '-':30s}")

print("-" * 92)
print(f"operators that RAISE on at least one plausible value: {len(raising)} of {len(OPERATORS)}")
for n, (bad, errs) in raising.items():
    print(f"   {n}: raises {','.join(sorted(errs))} on {bad}")

print()
if raising:
    print("=> P14's defect was LIVE, not latent: the shipped a3 operator set contains")
    print("   partial operators, so any a3 cell pairing them would have crashed the")
    print("   null battery pre-fix. P14's withheld claim resolves to LIVE.")
else:
    print("=> P14's defect was LATENT: every shipped a3 operator is total on these")
    print("   probes, so no production cell could reach the crash. P14 claimed")
    print("   existence only, and existence only is what it had.")
