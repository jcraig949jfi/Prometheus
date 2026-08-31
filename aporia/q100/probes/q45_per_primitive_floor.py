"""Is the floor a property of the ALGEBRA, or of WHICH PRIMITIVE was removed?

Varying the ring and width barely moved it (93.4-98.2%, spread 4.8pp). The remaining lever
inside this family is the operator inventory itself: remove each of the ten primitives in turn
and measure its own floor.

Label at depth 5, verify at depth 8, Z6^4 throughout.
"""
import sys, os
sys.path.insert(0, r"F:\Prometheus\aporia\lot")
os.chdir(r"F:\Prometheus")
import world3 as W

probes = W.probe_inputs()
ms_f, _, _, _ = W.build_closure(W.PRIMS, probes, max_size=5, max_candidates=6_000_000)
full_V = {k for k in ms_f if k[0] == W.V}
print(f"full closure depth 5: {len(full_V):,} V-signatures\n")
print(f"{'removed':>8} {'kind':>16} {'lost':>7} {'lost%':>6} {'recov@8':>8} {'FLOOR':>7}")
print("-" * 58)

KIND = {"p00": "rotate", "p01": "reverse", "p02": "increment", "p03": "double",
        "p04": "vec add", "p05": "vec multiply", "p06": "sum->scalar",
        "p07": "product->scalar", "p08": "scalar add", "p09": "scalar multiply"}

rows = []
for i, spec in enumerate(W.PRIMS):
    sub = [s for j, s in enumerate(W.PRIMS) if j != i]
    ms_s, _, _, _ = W.build_closure(sub, probes, max_size=5, max_candidates=6_000_000)
    lost = full_V - {k for k in ms_s if k[0] == W.V}
    if not lost:
        print(f"{spec['name']:>8} {KIND[spec['name']]:>16} {0:>7} {'--':>6} {'--':>8} {'n/a':>7}")
        continue
    ms_d, _, _, st = W.build_closure(sub, probes, max_size=8, max_candidates=30_000_000,
                                     max_sigs=4_000_000)
    rec = len(lost & {k for k in ms_d if k[0] == W.V})
    floor = 1 - rec / len(lost)
    rows.append((spec["name"], len(lost), len(lost) / len(full_V), rec / len(lost), floor))
    print(f"{spec['name']:>8} {KIND[spec['name']]:>16} {len(lost):>7,} "
          f"{len(lost)/len(full_V):>5.1%} {rec/len(lost):>7.1%} {floor:>6.1%}"
          + ("  [budget]" if st["budget_exhausted"] else ""))

print()
fl = [r[4] for r in rows]
lo = [r[2] for r in rows]
print(f"FLOOR      min {min(fl):.1%}  max {max(fl):.1%}  spread {max(fl)-min(fl):.1%}")
print(f"LOST-CLASS min {min(lo):.1%}  max {max(lo):.1%}  spread {max(lo)-min(lo):.1%}")
print()
print("compare: varying ring/width gave a floor spread of 4.8pp")
