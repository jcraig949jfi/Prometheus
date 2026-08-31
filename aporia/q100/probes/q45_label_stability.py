"""Q045 microscope: is "representation failure" a property of the TARGET, or of (target, budget)?

Leave-one-out at depth K labels a target REPRESENTATION-FAILURE if its signature is reachable
with the full primitive set but not with C minus p, within depth K.

But "not reachable within depth K" is not "not reachable". A deeper composition without p may
reach the same extensional behaviour. If it does, the label was never about representation --
it was about DEPTH, i.e. search.

This measures the label's instability directly: how many depth-K representation failures are
recovered by simply enumerating deeper with the SAME impoverished primitive set.
"""
import sys, os
from collections import Counter
sys.path.insert(0, r"F:\Prometheus\aporia\lot")
os.chdir(r"F:\Prometheus")
import world3 as W

probes = W.probe_inputs()
REMOVED = "p05"
i = [j for j, s in enumerate(W.PRIMS) if s["name"] == REMOVED][0]
sub = [s for j, s in enumerate(W.PRIMS) if j != i]

K_LABEL = 5
ms_full, _, _, _ = W.build_closure(W.PRIMS, probes, max_size=K_LABEL, max_candidates=4_000_000)
full_V = {k for k in ms_full if k[0] == W.V}

ms_sub5, _, _, _ = W.build_closure(sub, probes, max_size=K_LABEL, max_candidates=4_000_000)
sub5_V = {k for k in ms_sub5 if k[0] == W.V}

lost = full_V - sub5_V
print(f"Labelling depth K={K_LABEL}, removed primitive {REMOVED}")
print(f"  targets labelled REPRESENTATION_FAILURE at depth {K_LABEL}: {len(lost):,}")
print()

for K_DEEP in (6, 7, 8):
    ms_deep, _, _, st = W.build_closure(sub, probes, max_size=K_DEEP,
                                        max_candidates=20_000_000, max_sigs=3_000_000)
    deep_V = {k for k in ms_deep if k[0] == W.V}
    recovered = lost & deep_V
    frac = len(recovered) / max(len(lost), 1)
    print(f"  enumerate C\\{{{REMOVED}}} to depth {K_DEEP}: "
          f"{st['candidates_expanded']:,} candidates, {len(deep_V):,} V-sigs")
    print(f"     RECOVERED {len(recovered):,} of {len(lost):,} = {frac:.1%} "
          f"-> those labels were DEPTH, not representation")
    still = lost - deep_V
    print(f"     still unreachable: {len(still):,} = {len(still)/max(len(lost),1):.1%}")
    if recovered:
        c = Counter(ms_deep[k] for k in recovered)
        prof = "  ".join(f"d{d}:{n}" for d, n in sorted(c.items()))
        print(f"     recovered-at-depth profile: {prof}")
    print()
