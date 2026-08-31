"""Is the 89.6% unreachability floor a property of THE ALGEBRA, or of TINYPROG specifically?

Operator: "the world can vary vastly despite being made of similar parts."

Test: hold the PARTS fixed -- same ten primitive KINDS (rotate, reverse, increment, double,
elementwise add, elementwise multiply, sum, product, scalar-add, scalar-multiply) -- and vary
only the ring the vectors live in, and the width.

The modulus is the sharpest lever available: Z5 and Z7 are FIELDS (every nonzero element
invertible), Z6, Z8 and Z9 have ZERO DIVISORS. That is a categorical algebraic difference
produced by a one-character parameter change, which is exactly the claim under test.

For each world: label the unreachable class at depth 5 with elementwise-multiply removed,
then enumerate the same impoverished set to depth 8 and report the surviving floor.
"""
import sys, os
sys.path.insert(0, r"F:\Prometheus\aporia\lot")
os.chdir(r"F:\Prometheus")
import world3 as W


def make_prims(mod, width):
    def rot(v): return v[1:] + v[:1]
    def rev(v): return tuple(reversed(v))
    def inc(v): return tuple((a + 1) % mod for a in v)
    def dbl(v): return tuple((a * 2) % mod for a in v)
    def vadd(a, b): return tuple((x + y) % mod for x, y in zip(a, b))
    def vmul(a, b): return tuple((x * y) % mod for x, y in zip(a, b))
    def vsum(v): return sum(v) % mod
    def vprod(v):
        p = 1
        for a in v:
            p = (p * a) % mod
        return p
    def sadd(v, s): return tuple((a + s) % mod for a in v)
    def smul(v, s): return tuple((a * s) % mod for a in v)
    V, S = W.V, W.S
    return [
        {"name": "p00", "args": (V,), "ret": V, "fn": rot},
        {"name": "p01", "args": (V,), "ret": V, "fn": rev},
        {"name": "p02", "args": (V,), "ret": V, "fn": inc},
        {"name": "p03", "args": (V,), "ret": V, "fn": dbl},
        {"name": "p04", "args": (V, V), "ret": V, "fn": vadd},
        {"name": "p05", "args": (V, V), "ret": V, "fn": vmul},
        {"name": "p06", "args": (V,), "ret": S, "fn": vsum},
        {"name": "p07", "args": (V,), "ret": S, "fn": vprod},
        {"name": "p08", "args": (V, S), "ret": V, "fn": sadd},
        {"name": "p09", "args": (V, S), "ret": V, "fn": smul},
    ]


def probes_for(mod, width, p=6):
    import random
    rng = random.Random(20260827)
    fixed = [tuple([0] * width), tuple((i + 1) % mod for i in range(width)),
             tuple([(mod - 1)] * width)]
    out = list(fixed)
    while len(out) < p:
        out.append(tuple(rng.randrange(mod) for _ in range(width)))
    return out[:p]


print(f"{'world':>14} {'field?':>7} {'full V':>8} {'lost':>7} {'lost%':>6} "
      f"{'recov@8':>8} {'FLOOR':>7}")
print("-" * 62)
PRIMES = {5, 7, 11, 13}
results = []
for mod, width in [(5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (6, 3), (6, 5), (7, 3)]:
    prims = make_prims(mod, width)
    pr = probes_for(mod, width)
    sub = [s for s in prims if s["name"] != "p05"]
    ms_f, _, _, _ = W.build_closure(prims, pr, max_size=5, max_candidates=6_000_000)
    full_V = {k for k in ms_f if k[0] == W.V}
    ms_s, _, _, _ = W.build_closure(sub, pr, max_size=5, max_candidates=6_000_000)
    lost = full_V - {k for k in ms_s if k[0] == W.V}
    if not lost:
        print(f"  Z{mod}^{width:<10} {'yes' if mod in PRIMES else 'no':>7} "
              f"{len(full_V):>8,} {0:>7} {'--':>6} {'--':>8} {'n/a':>7}")
        continue
    ms_d, _, _, st = W.build_closure(sub, pr, max_size=8, max_candidates=30_000_000,
                                     max_sigs=4_000_000)
    deep_V = {k for k in ms_d if k[0] == W.V}
    rec = len(lost & deep_V)
    floor = 1 - rec / len(lost)
    results.append((mod, width, len(full_V), len(lost), len(lost) / len(full_V),
                    rec / len(lost), floor))
    print(f"  Z{mod}^{width:<10} {'yes' if mod in PRIMES else 'no':>7} "
          f"{len(full_V):>8,} {len(lost):>7,} {len(lost)/len(full_V):>5.1%} "
          f"{rec/len(lost):>7.1%} {floor:>6.1%}"
          + ("  [budget]" if st["budget_exhausted"] else ""))

print()
if results:
    floors = [r[6] for r in results]
    losts = [r[4] for r in results]
    print(f"FLOOR across worlds: min {min(floors):.1%}  max {max(floors):.1%}  "
          f"spread {max(floors)-min(floors):.1%}")
    print(f"LOST-CLASS SIZE:     min {min(losts):.1%}  max {max(losts):.1%}  "
          f"spread {max(losts)-min(losts):.1%}")
    fields = [r for r in results if r[0] in PRIMES]
    rings = [r for r in results if r[0] not in PRIMES]
    if fields and rings:
        fm = sum(r[6] for r in fields) / len(fields)
        rm = sum(r[6] for r in rings) / len(rings)
        print(f"\nmean floor, PRIME modulus (field):     {fm:.1%}  (n={len(fields)})")
        print(f"mean floor, COMPOSITE modulus (ring):  {rm:.1%}  (n={len(rings)})")
