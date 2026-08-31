"""Q045 viability probe: is there a REPRESENTATION-FAILURE class to test at all?

The experiment Q045 needs is ground truth for:
  (a) SEARCH failure        target IS reachable by the solver's primitives, solver missed it
  (c) REPRESENTATION failure target is NOT reachable by the solver's primitives at any size <= K

TINYPROG gives (c) EXACTLY by leave-one-out: build the closure of the full primitive set C,
build the closure of C minus p, and take signatures present in the first and absent from the
second. Those are provably unreachable for the ablated solver within the enumerated bound --
certified by enumeration, not asserted.

This probe asks whether that class is big enough to be a testbed. If removing a primitive costs
almost nothing, there is no representation-failure population and Q045 is untestable here.
"""
import sys, os
sys.path.insert(0, r"F:\Prometheus\aporia\lot")
os.chdir(r"F:\Prometheus")
import world3 as W

K = 5                      # enumeration depth (5 keeps leave-one-out cheap)
probes = W.probe_inputs()

ms_full, od_full, ly_full, st_full = W.build_closure(W.PRIMS, probes, max_size=K,
                                                     max_candidates=4_000_000)
full_V = {k for k in ms_full if k[0] == W.V}
print(f"FULL closure, depth {K}: {st_full['candidates_expanded']:,} candidates, "
      f"{len(ms_full):,} signatures ({len(full_V):,} of type V)")
print(f"  budget exhausted: {st_full['budget_exhausted']}")
print()
print("LEAVE-ONE-OUT: signatures lost when each primitive is removed")
print(f"{'removed':>10}  {'V-sigs':>8}  {'lost':>8}  {'lost %':>7}   verdict")

rows = []
for i, spec in enumerate(W.PRIMS):
    sub = [s for j, s in enumerate(W.PRIMS) if j != i]
    ms_i, _, _, st_i = W.build_closure(sub, probes, max_size=K, max_candidates=4_000_000)
    sub_V = {k for k in ms_i if k[0] == W.V}
    lost = full_V - sub_V
    frac = len(lost) / max(len(full_V), 1)
    verdict = ("NO TESTBED" if len(lost) == 0 else
               "thin" if frac < 0.02 else "USABLE")
    rows.append((spec["name"], len(sub_V), len(lost), frac, verdict))
    print(f"{spec['name']:>10}  {len(sub_V):8,}  {len(lost):8,}  {frac:6.1%}   {verdict}")

usable = [r for r in rows if r[4] == "USABLE"]
print()
print(f"primitives whose removal creates a USABLE representation-failure class: "
      f"{len(usable)} of {len(W.PRIMS)}")
if usable:
    best = max(usable, key=lambda r: r[2])
    print(f"largest class: remove {best[0]} -> {best[2]:,} signatures become unreachable "
          f"({best[3]:.1%} of the space)")
    print()
    print("MINIMAL-SIZE PROFILE of the lost class for that primitive (how deep the")
    print("unreachable targets sit in the FULL closure -- shallow ones make the cleanest tasks):")
    i = [j for j, s in enumerate(W.PRIMS) if s["name"] == best[0]][0]
    sub = [s for j, s in enumerate(W.PRIMS) if j != i]
    ms_i, _, _, _ = W.build_closure(sub, probes, max_size=K, max_candidates=4_000_000)
    sub_V = {k for k in ms_i if k[0] == W.V}
    from collections import Counter
    c = Counter(ms_full[k] for k in (full_V - sub_V))
    for size in sorted(c):
        print(f"    minsize {size}: {c[size]:,} unreachable targets")
