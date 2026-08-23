"""Is the detector experiment winnable at n=26? (syntactic-router, step 3)

Step 2: 22 scalar fields, observed 84.6%, permutation null 95th pct = 84.6%, p=0.136.
The obvious next move is to featurize the 7 non-scalar fields -- which are exactly
the routing-relevant ones (genuine_routing_final, dispatch_audit_final,
branches_load_bearing_for_nothing). But MORE features raise the null ceiling.

So, before spending the corpus: how high does the null ceiling go as feature count
grows, and how many of the 26 walls must a detector get right to clear it?

This is A2 applied to the experimental DESIGN rather than to an instrument.
"""
import json
import random
import statistics

rows = [json.loads(l) for l in open("apollo/wall_corpus/corpus.jsonl", encoding="utf-8")]
walls = [r for r in rows if r["failure_class"] != "control_none"]
ABSENT = {"expressiveness_restricted"}
y_true = [(0 if r["failure_class"] in ABSENT else 1) for r in walls]
n = len(y_true)

# synthesise k independent NOISE features with the same value-cardinality profile
rng = random.Random(20260823)


def null_ceiling(k, shuffles=600):
    best_per_shuffle = []
    feats = [[rng.gauss(0, 1) for _ in range(n)] for _ in range(k)]
    for _ in range(shuffles):
        y = y_true[:]
        rng.shuffle(y)
        best = 0.0
        for vals in feats:
            for t in sorted(set(vals)):
                for pol in (0, 1):
                    pred = [(1 if v > t else 0) ^ pol for v in vals]
                    acc = sum(p == q for p, q in zip(pred, y)) / n
                    if acc > best:
                        best = acc
        best_per_shuffle.append(best)
    best_per_shuffle.sort()
    return best_per_shuffle[int(.95 * len(best_per_shuffle))]


print(f"n = {n} walls (8 ABSENT / 18 BLOCKED). Majority floor 69.2%.\n")
print(f"{'features searched':>18s} {'null 95th pct':>14s} {'walls needed to clear':>23s}")
print("-" * 60)
for k in (1, 5, 22, 50, 100):
    c = null_ceiling(k)
    need = int(c * n) + 1
    print(f"{k:>18d} {100*c:>13.1f}% {need:>16d} of {n}")
print("-" * 60)
print()
print("Reading: with 22 features a detector must get 23 of 26 right to clear the")
print("null at 5%. Only 8 walls are ABSENT, so it must classify essentially every")
print("one of them correctly AND miss at most 3 elsewhere. Adding the 7 non-scalar")
print("fields raises the bar further.")
print()
print("=> the corpus is a fine LABELLED SET and an underpowered DISCOVERY set.")
print("   It can VALIDATE a detector specified in advance; it cannot be searched.")
