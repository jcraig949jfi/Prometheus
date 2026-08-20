"""Boundary case for lattice_void_miner (Harmonia-A soak P13).

Pre-committed property, chosen BEFORE running to avoid fishing, and the same one
asked of the two suites probed earlier: does the instrument distinguish
"we looked and found nothing" from "we could not look"?

For a VOID MINER this is the sharpest possible version of that question, because
its entire output is absences. A cell with zero evaluable pairs is vacuously
'always true' -- if the miner calls that an exact void, then a discovery
instrument reports its own blindness as a finding.

Two cases:
  1. empty sides            -> does n_cells distinguish it?
  2. values present, but NO pair evaluable (relation always raises)
                            -> is such a cell classified as an exact void?

Read-only. Touches nothing outside harmonia/soak/.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from harmonia.primitives.lattice_void_miner import LatticeSpec, mine, evaluate_lattice


def rel_ok(a, b, r):
    return a == b


def rel_always_raises(a, b, r):
    raise ValueError("no pair is evaluable in this spec")


print("=== case 1: EMPTY sides (nothing to look at) ===")
spec_empty = LatticeSpec(
    side_a_name="A", side_b_name="B",
    side_a={"x": []}, side_b={"y": []},
    operators={"id": lambda v: v},
    relations=("equal",),
    eval_relation=rel_ok,
)
r1 = mine(spec_empty)
print("  summary:", r1["summary"])

print("\n=== case 2: values present, NO pair evaluable (relation raises) ===")
spec_blind = LatticeSpec(
    side_a_name="A", side_b_name="B",
    side_a={"x": [1, 2, 3, 4, 5]}, side_b={"y": [10, 20, 30]},
    operators={"id": lambda v: v},
    relations=("equal",),
    eval_relation=rel_always_raises,
)
try:
    cells = evaluate_lattice(spec_blind)
    print(f"  cells evaluated: {len(cells)}")
    for c in cells[:3]:
        keys = {k: c.get(k) for k in ("hold_rate", "n_pairs", "n_hold", "is_exact_void")
                if k in c}
        print(f"    {keys}")
    r2 = mine(spec_blind)
    print("  summary:", r2["summary"])
    nv = r2["summary"]["n_exact_voids"]
    print(f"\n  VERDICT: a cell with no evaluable pair is reported as an exact void: {nv > 0}")
    if nv:
        v = r2["voids"][0]
        print(f"    triviality_class = {v['triviality_class']}")
        print(f"    certificate_verified = {v['certificate_verified']}")
except Exception as e:
    print(f"  evaluate_lattice RAISED: {type(e).__name__}: {str(e)[:90]}")
    print("  => the miner fails LOUDLY rather than reporting a vacuous void")
