"""Middle-case boundary probe for lattice_void_miner (Harmonia-A soak P14).

P13 tested two ARTIFICIAL EXTREMES -- nothing evaluable at all -- and the miner
handled both. P13 logged as its own weakness that the realistic middle was
untested, which is where real failures live.

The sharp question: is the vacuity guard BINARY (n_eval > 0) or GRADED?
A cell whose relation never holds across ONE surviving pair is, on a binary
guard, an "exact void" backed by a single data point. That is not vacuity --
it is thin evidence wearing the same badge as a void established over millions
of pairs, and nothing in the class name distinguishes them.

Construction: an operator that raises ValueError for all but k values per side.
transform_errors defaults to (ValueError, OverflowError), so those are swallowed
as domain skips -- the documented, intended path -- leaving k*k evaluable pairs.

Read-only. Touches nothing outside harmonia/soak/.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from harmonia.primitives.lattice_void_miner import LatticeSpec, mine  # noqa: E402

ALWAYS_HOLDS = lambda a, b, r: True          # noqa: E731  relation ALWAYS holds
# NOTE (P14 self-audit): my first draft used a never-holds relation, giving
# hold_rate 0.0 -- the OPPOSITE polarity. An exact void here is hold_rate 1.0
# (no counterexample), confirmed by the near-void bands 0.999/0.99/0.95 being
# HIGH. The probe was wrong, not the miner. Fixed before drawing any conclusion.
SIDE_VALUES = list(range(1, 101))            # 100 values per side


def keep_only(k):
    """Operator that survives for k values and raises (domain-skip) for the rest."""
    def op(v):
        if v > k:
            raise ValueError("outside this invariant's domain")
        return v
    return op


def probe(k):
    spec = LatticeSpec(
        side_a_name="A", side_b_name="B",
        side_a={"x": list(SIDE_VALUES)}, side_b={"y": list(SIDE_VALUES)},
        operators={"keep": keep_only(k)},
        relations=("always",),
        eval_relation=ALWAYS_HOLDS,
    )
    res = mine(spec)
    cell = res["cells"][0]
    void = res["voids"][0] if res["voids"] else None
    return {
        "k": k,
        "n_eval": cell.get("n_eval"),
        "n_dropped_a": cell.get("n_dropped_a"),
        "hold_rate": cell.get("hold_rate"),
        "is_exact_void": cell.get("is_exact_void"),
        "promoted": bool(void),
        "class": void["triviality_class"] if void else None,
        "cert_ok": void["certificate_verified"] if void else None,
    }


if __name__ == "__main__":
    print("relation NEVER holds; k = surviving values per side (rest domain-skipped)\n")
    print(f"{'k':>4} {'n_eval':>8} {'dropped_a':>10} {'hold_rate':>10} "
          f"{'void?':>6} {'promoted':>9}  class / cert")
    rows = []
    for k in (1, 2, 3, 5, 10, 100):
        r = probe(k)
        rows.append(r)
        print(f"{r['k']:>4} {str(r['n_eval']):>8} {str(r['n_dropped_a']):>10} "
              f"{str(r['hold_rate']):>10} {str(r['is_exact_void']):>6} "
              f"{str(r['promoted']):>9}  {r['class']} / {r['cert_ok']}")

    promoted_thin = [r for r in rows if r["promoted"] and (r["n_eval"] or 0) <= 4]
    print(f"\ncells promoted to EXACT VOID on <=4 evaluable pairs: {len(promoted_thin)}")
    if promoted_thin:
        print("  => the guard is BINARY (n_eval>0), not graded: a 1-pair void carries the")
        print("     same class label as one established over millions of pairs.")
    else:
        print("  => the guard accounts for evidence strength, not merely non-emptiness.")
