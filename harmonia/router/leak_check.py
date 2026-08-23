"""Payload-reading null for the wall corpus (syntactic-router thesis, step 1).

THE CLAIM UNDER TEST: "every measured wall is a router in front of a working
semantic engine" -- i.e. when you hit a wall, the capability is usually PRESENT and
something else (interface, measurement, search) blocks it.

The corpus labels each wall:
    expressiveness_restricted -> capability ABSENT   (thesis does NOT apply)
    interface_bug             -> capability present, interface blocks
    measurement_artifact      -> capability present, measurement misreports
    search_operator_removed   -> capability present, search cannot reach

Binary question: ABSENT vs BLOCKED, from wall_signature alone.

BEFORE building any detector: does a SINGLE field trivially separate the label?
HARMA memory: a ladder oracle once shipped `truth` in probe.data and a 3-line
reader tied the top baseline. Every metric needs a payload-reading null and a
published chance floor (feedback_measurement_carries_its_answer).
"""
import json
import collections

rows = [json.loads(l) for l in open("apollo/wall_corpus/corpus.jsonl", encoding="utf-8")]
walls = [r for r in rows if r["failure_class"] != "control_none"]

ABSENT = {"expressiveness_restricted"}
y = [(0 if r["failure_class"] in ABSENT else 1) for r in walls]      # 1 = BLOCKED
n = len(y)
maj = max(sum(y), n - sum(y))
print(f"walls (controls excluded) : {n}")
print(f"  ABSENT  (expressiveness_restricted) : {n - sum(y)}")
print(f"  BLOCKED (interface/measurement/search): {sum(y)}")
print(f"CHANCE FLOOR (majority class)         : {maj}/{n} = {100*maj/n:.1f}%\n")

# scalar fields only
fields = collections.Counter()
for r in walls:
    for k, v in r["wall_signature"].items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            fields[k] += 1
scalar = sorted(k for k, c in fields.items() if c == n)
nonscalar = sorted(set(walls[0]["wall_signature"]) - set(scalar))
print(f"scalar fields usable: {len(scalar)}   non-scalar (skipped): {len(nonscalar)}")
print(f"  skipped: {', '.join(nonscalar)}\n")

def best_threshold(vals, y):
    """Best single-threshold accuracy for this field."""
    cand = sorted(set(vals))
    best = 0.0
    for i in range(len(cand)):
        t = cand[i]
        for polarity in (0, 1):
            pred = [(1 if (v > t) else 0) ^ polarity for v in vals]
            acc = sum(p == t_ for p, t_ in zip(pred, y)) / len(y)
            best = max(best, acc)
    return best

scores = []
for k in scalar:
    vals = [r["wall_signature"][k] for r in walls]
    scores.append((best_threshold(vals, y), k))
scores.sort(reverse=True)

print(f"{'field':44s} best single-threshold accuracy")
print("-" * 78)
for acc, k in scores[:12]:
    flag = "  <-- LEAK" if acc >= 0.97 else ("  <-- strong" if acc >= 0.88 else "")
    print(f"{k:44s} {100*acc:5.1f}%{flag}")
print("-" * 78)
top = scores[0][0]
print(f"chance floor {100*maj/n:.1f}%  |  best single field {100*top:.1f}%  "
      f"|  lift {100*(top - maj/n):+.1f} pts")
print()
if top >= 0.97:
    print("LEAK: a single threshold reads the label. The corpus cannot support a")
    print("detector claim as posed -- report the reader, not a detector.")
elif top >= 0.88:
    print("PARTIAL: one field carries most of the signal. THAT FIELD is the router")
    print("coordinate, and is the finding rather than a nuisance.")
else:
    print("NO SINGLE-FIELD LEAK: the label is not trivially readable. A detector")
    print("experiment is well-posed against this floor.")
