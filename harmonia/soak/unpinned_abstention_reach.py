"""Is the UNPINNED abstention at verifier_lens.py:485 reachable? (soak P32)

Line 478 (z3 returned unknown) is pinned by true_universal_not_rubber_stamped_...
Line 485 (NO z3 predicate registered at all) is caught by no test. P14's discipline:
a defect's severity is existence AND reachability, measured separately.

The two paths return identical valid/kill_pattern and differ only in checks["note"],
which is what discriminates them.
"""
import sys

sys.path.insert(0, "harmonia/experiments")
import reasoning_phase0 as rp0            # noqa: E402
from verifier_lens import verify          # noqa: E402

UNREGISTERED = rp0.Probe("R6", "clean", "conjecture",
                         {"cid": "harma_p32_definitely_not_registered",
                          "truth": True, "cex": None, "delayed": False},
                         True)

r = verify(UNREGISTERED, True)
note = (r.get("checks") or {}).get("note", "")
print("probe: true universal with an UNREGISTERED cid")
print(f"  valid        : {r['valid']}")
print(f"  kill_pattern : {r['kill_pattern']}")
print(f"  note         : {note[:78]}...")
print()
line485 = "no z3 predicate is registered" in note
line478 = "z3 could not decide" in note
print(f"  reached line 485 (no registry entry) : {line485}")
print(f"  reached line 478 (z3 unknown)        : {line478}")
print()
if line485 and r["valid"] is None:
    print("REACHABLE: an ordinary conjecture probe with an unregistered cid lands on the")
    print("unpinned abstention. A regression there marks every such probe REFUTED —")
    print("the same mis-grading the unknown_kind fix exists to prevent, at a sibling site.")
else:
    print("NOT reached by this construction; the gap may be latent.")
