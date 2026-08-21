"""Boundary case of my own design: what does the legality suite assert at a==b? (soak P43, rotation (c))

HARMA-P19 found gen_abs_extra_clean's ground truth incomplete at a==b: the equation
|x-a| = b-x becomes a-x = a-x, true for EVERY x <= a, while the recorded ground
truth is the single point (a+b)/2 = a.

test_abs_extra_clean_ground_truth checks, on every probe:
    len(p.ground_truth) == 1        and     |x-a| == b-x  at that x
Both hold at a==b. So the question is not whether the suite REACHES the degenerate
case -- it is what the suite asserts once it gets there.

Read-only w.r.t. the repo.
"""
import random
import sys
from fractions import Fraction

sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_abs_extra_clean  # noqa: E402

try:
    from test_legality_generators import _SEEDS
except Exception:
    _SEEDS = [0, 1, 2, 3, 4]

print("1. How often does the degenerate case appear in the CHECKED window?")
tot = deg = 0
degenerate = []
for seed in _SEEDS:
    probes = gen_abs_extra_clean(random.Random(seed))
    for p in probes[:60]:                       # the exact window the suite checks
        tot += 1
        if p.data["a"] == p.data["b"]:
            deg += 1
            degenerate.append(p)
print(f"   probes inside the suite's checked window : {tot}")
print(f"   with a == b (degenerate)                 : {deg} ({100*deg/tot:.1f}%)")

if not degenerate:
    print("\n   VACUOUS: no degenerate probe in the window — diagnose before concluding.")
    raise SystemExit(0)

print("\n2. At those probes, is the recorded ground truth the WHOLE solution set?")
p = degenerate[0]
a, b = p.data["a"], p.data["b"]
gt = p.ground_truth
print(f"   specimen: a={a}, b={b}, recorded gt={gt}")
others = [x for x in (a - 1, a - 2, a - 10, Fraction(a) - Fraction(1, 2))
          if abs(x - a) == b - x and x not in gt]
print(f"   other exact solutions found: {others[:4]}")
print(f"   => solution set is the half-line x <= {a}; gt records 1 point of it")

print("\n3. Does the suite's assertion PASS on this probe?")
c1 = len(gt) == 1
x = gt[0]
c2 = abs(x - a) == b - x
print(f"   'gt has exactly 1 root'      -> {c1}")
print(f"   '|x-a| == b-x at that root'  -> {c2}")
print(f"   suite verdict on this probe  -> {'PASSES' if (c1 and c2) else 'FAILS'}")

print("\n4. What would a completeness assertion have caught?")
extra = others[0] if others else None
print(f"   a check of the form 'no OTHER x satisfies the equation' fails immediately")
print(f"   on x={extra}, which satisfies it and is absent from gt.")
print()
print("VERDICT: the suite REACHES the degenerate case and asserts a property that is")
print("true there. It pins that the recorded root IS a solution, never that it is THE")
print("solution set — so a green suite actively certifies the incomplete ground truth")
print("HARMA-P19 reported. This is a soundness check standing in for a completeness one.")
