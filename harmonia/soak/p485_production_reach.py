"""Is verifier_lens.py:485 on the PRODUCTION path? (soak P33)

NOTE: v1 used p.answer and raised AttributeError. The field is ground_truth --
the SAME confusion HARMA-P19 recorded. A finding logged five passes ago did not
prevent me repeating it; only the crash did.

P32 showed the no-registry abstention is unpinned and reachable by a probe I
hand-built, and logged WITHHELD whether production traffic reaches it. That is
the latent-versus-live line P14 established, and it is measurable: run the REAL
generator and classify every conjecture probe by which abstention it lands on.

The two paths return identical valid and kill_pattern; checks["note"] separates them.
"""
import random
import sys
from collections import Counter

sys.path.insert(0, "harmonia/experiments")
import reasoning_phase0 as rp0            # noqa: E402
from verifier_lens import verify, decide_conjecture  # noqa: E402

print("=== 1. registry status of every cid the generator can emit ===")
for cid, truth, cex, streak in rp0.CONJ:
    d = decide_conjecture(cid)
    status = "NO REGISTRY ENTRY" if d is None else f"registered (valid={d['valid']})"
    print(f"  {cid:24s} truth={str(truth):5s}  {status}")

print("\n=== 2. run the REAL generator and classify each probe's verify() outcome ===")
probes = rp0.gen_R6(random.Random(20260821))
buckets, notes = Counter(), Counter()
for p in probes:
    r = verify(p, p.ground_truth)
    note = (r.get("checks") or {}).get("note", "")
    if "no z3 predicate is registered" in note:
        bucket = "LINE 485 (no registry entry) — UNPINNED"
    elif "z3 could not decide" in note:
        bucket = "line 478 (z3 unknown) — pinned"
    else:
        bucket = f"other (valid={r['valid']}, kill={r['kill_pattern']})"
    buckets[bucket] += 1
    notes[p.data["cid"]] += 1 if "no z3 predicate is registered" in note else 0

total = len(probes)
print(f"  generated conjecture probes: {total}")
for b, n in buckets.most_common():
    print(f"    {n:>4d}  ({100*n/total:5.1f}%)  {b}")

hot = sum(n for b, n in buckets.items() if "485" in b)
print(f"\n  probes landing on the UNPINNED line 485: {hot}/{total} = {100*hot/total:.1f}%")
by_cid = {c: n for c, n in notes.items() if n}
print(f"  cids that route there: {by_cid or 'none'}")
print()
if hot:
    print("LIVE: the unpinned abstention is on the production path, not merely reachable")
    print("by a hand-built probe. A regression there mis-grades this share of R6 traffic.")
else:
    print("LATENT: no generator-produced probe reaches line 485; it is reachable only")
    print("by constructing a cid the generator never emits, like P14's defect.")
