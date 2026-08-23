"""Permutation null for the wall-signature detector (syntactic-router, step 2).

Step 1 found no single-field LEAK, and a best-of-22 field at 84.6% against a 69.2%
majority floor. But that 84.6% is the maximum over 22 fields x every threshold x
both polarities, on n=26. A selected maximum needs its own null.

THE NULL: shuffle the labels, re-run the IDENTICAL best-of-22 search, record the
best accuracy. Repeat. If shuffled labels routinely reach 84.6%, the lift is a
multiple-comparisons artifact and there is no measured signal.

This is the check that distinguishes "the signature carries the distinction" from
"22 fields and 26 samples will always produce something."
"""
import json
import random

rows = [json.loads(l) for l in open("apollo/wall_corpus/corpus.jsonl", encoding="utf-8")]
walls = [r for r in rows if r["failure_class"] != "control_none"]
ABSENT = {"expressiveness_restricted"}
y_true = [(0 if r["failure_class"] in ABSENT else 1) for r in walls]
n = len(y_true)

scalar = sorted(k for k, v in walls[0]["wall_signature"].items()
                if isinstance(v, (int, float)) and not isinstance(v, bool))
cols = {k: [r["wall_signature"][k] for r in walls] for k in scalar}


def best_over_all_fields(y):
    best = 0.0
    for k in scalar:
        vals = cols[k]
        for t in sorted(set(vals)):
            for pol in (0, 1):
                pred = [(1 if v > t else 0) ^ pol for v in vals]
                acc = sum(p == q for p, q in zip(pred, y)) / n
                if acc > best:
                    best = acc
    return best


observed = best_over_all_fields(y_true)
rng = random.Random(20260823)
N = 2000
null = []
for _ in range(N):
    y = y_true[:]
    rng.shuffle(y)
    null.append(best_over_all_fields(y))

null.sort()
ge = sum(1 for v in null if v >= observed - 1e-9)
p = (ge + 1) / (N + 1)
import statistics
print(f"observed best-of-{len(scalar)}      : {100*observed:.1f}%")
print(f"majority-class floor        : {100*max(sum(y_true), n-sum(y_true))/n:.1f}%")
print()
print(f"PERMUTATION NULL ({N} shuffles), same search:")
print(f"  null mean                 : {100*statistics.mean(null):.1f}%")
print(f"  null median               : {100*statistics.median(null):.1f}%")
print(f"  null 95th percentile      : {100*null[int(.95*N)]:.1f}%")
print(f"  null max                  : {100*null[-1]:.1f}%")
print()
print(f"  p(null >= observed)       : {p:.4f}  ({ge} of {N})")
print()
if p > 0.10:
    print("SELECTION ARTIFACT: shuffled labels reach the observed accuracy routinely.")
    print("The 84.6% is what 22 fields and 26 samples produce by construction.")
    print("=> the signature does NOT demonstrably carry the absent-vs-blocked distinction.")
elif p > 0.01:
    print("MARGINAL: above the null but not decisively, at n=26.")
else:
    print("SIGNAL: the observed separation is not reachable by chance under this search.")
