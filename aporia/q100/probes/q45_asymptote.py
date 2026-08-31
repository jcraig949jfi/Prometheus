"""Does the representation-failure class DISSOLVE as the reachable graph grows, or hit a floor?

Operator intuition: "a 5-node graph has no solution, a 1000-node graph has many" -- i.e.
unreachability is an artifact of a small explored structure and evaporates with size.

Competing hypothesis: C\{p} generates a PROPER SUBALGEBRA. Then no amount of depth recovers the
missing behaviours, and the recovery curve hits a hard floor rather than going to zero.

These differ at the limit and the difference is measurable: extend the depth and watch whether
cumulative recovery keeps climbing or plateaus.
"""
import sys, os
sys.path.insert(0, r"F:\Prometheus\aporia\lot")
os.chdir(r"F:\Prometheus")
import world3 as W

probes = W.probe_inputs()
REMOVED = "p05"
i = [j for j, s in enumerate(W.PRIMS) if s["name"] == REMOVED][0]
sub = [s for j, s in enumerate(W.PRIMS) if j != i]

ms_full, _, _, _ = W.build_closure(W.PRIMS, probes, max_size=5, max_candidates=4_000_000)
full_V = {k for k in ms_full if k[0] == W.V}
ms_s5, _, _, _ = W.build_closure(sub, probes, max_size=5, max_candidates=4_000_000)
lost = full_V - {k for k in ms_s5 if k[0] == W.V}
print(f"class labelled at depth 5, {REMOVED} removed: {len(lost):,} targets\n")
print(f"{'depth':>6} {'candidates':>12} {'V-sigs':>10} {'recovered':>10} {'cum %':>7} {'new':>6}")

prev = 0
for K in (6, 7, 8, 9, 10):
    ms_d, _, _, st = W.build_closure(sub, probes, max_size=K,
                                     max_candidates=40_000_000, max_sigs=6_000_000)
    deep_V = {k for k in ms_d if k[0] == W.V}
    rec = len(lost & deep_V)
    print(f"{K:>6} {st['candidates_expanded']:>12,} {len(deep_V):>10,} "
          f"{rec:>10,} {rec/len(lost):>6.1%} {rec-prev:>6,}"
          + ("   [BUDGET EXHAUSTED]" if st["budget_exhausted"] else ""))
    prev = rec

still = lost - deep_V
print(f"\nstill unreachable after depth {K}: {len(still):,} = {len(still)/len(lost):.1%}")
print("\nINTERPRETATION")
print("  if cumulative recovery is still climbing steeply -> the class is a DEPTH artifact")
print("     and the operator's small-graph intuition holds")
print("  if it flattens with a large residue -> C\\{p} is a PROPER SUBALGEBRA and the")
print("     residue is a genuine representation boundary that no search budget crosses")
