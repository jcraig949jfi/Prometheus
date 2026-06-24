"""dispatch_poc.py — G1 construct-validity for the dispatch/routing capability.

Shows that a SINGLE organism with precondition-guarded multiple scorers
(a "dispatcher") solves a mixed-type battery that NO single-terminal pipeline
can, using only the substrate's existing BlackboardOp.precondition + on_fail=skip
machinery. This is the empirical premise behind the dispatch design
(pivot/dispatch_design_2026-06-22.md).

Run: python apollo/scripts/dispatch_poc.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blackboard import BlackboardState, BlackboardOp, run_pipeline
import blackboard_evolve as ev
from inference_canary import build_inference_canary
from cross_tier_canary import build_cross_tier_canary

R = ev.REGISTRY


def guarded(name, precond):
    """Wrap a registry scorer with a non-trivial precondition; on_fail=skip
    means a non-matching scorer leaves selected_answer untouched."""
    fn, _ = R[name]
    return BlackboardOp(fn.fn, reads=fn.reads, writes=fn.writes,
                        precondition=precond, on_fail="skip", name=name + "__g")


def ops(names):
    return [R[n][0] for n in names]


def run(pl_ops, tagged_tasks):
    per = {}
    for tag, t in tagged_tasks:
        per.setdefault(tag, [0, 0])[1] += 1
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            o = run_pipeline(pl_ops, s)
            if o.selected_answer == t["correct"]:
                per[tag][0] += 1
        except Exception:
            pass
    tot = sum(v[0] for v in per.values()) / max(sum(v[1] for v in per.values()), 1)
    return tot, {k: f"{v[0]}/{v[1]}" for k, v in per.items()}


def main():
    inf = build_inference_canary(n=20)
    xt = build_cross_tier_canary(n=20)
    mixed = [("inf", t) for t in inf] + [("xt", t) for t in xt]

    # disjoint-ish guards keyed on slot population
    g_deriv = guarded("score_by_derivability", lambda s: len(s.derived_facts) > 0 or len(s.facts) > 0)
    g_selnth = guarded("select_nth", lambda s: len(s.ordered) > 0)

    inf_spec = ops(["parse_rules", "forward_chain", "score_by_derivability"])
    xt_spec = ops(["parse_rules", "parse_ordinal", "forward_chain",
                   "relations_from_facts", "op_build_ordering", "select_nth"])
    shared = ops(["parse_rules", "parse_ordinal", "forward_chain",
                  "relations_from_facts", "op_build_ordering"])
    dispatcher = shared + [g_deriv, g_selnth]

    print("=== G1 construct validity: dispatch vs single-terminal (mixed inf+xt) ===")
    print("inference-specialist :", run(inf_spec, mixed))
    print("cross_tier-specialist:", run(xt_spec, mixed))
    print("DISPATCHER           :", run(dispatcher, mixed))

    amb = 0
    for tag, t in mixed:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        for o in shared:
            s = o(s)
        if (len(s.derived_facts) > 0 or len(s.facts) > 0) and len(s.ordered) > 0:
            amb += 1
    print(f"\nGUARD-OVERLAP (fire both): {amb}/{len(mixed)} tasks — "
          f"correctness currently relies on tail-ordering, not exclusivity (design must fix).")


if __name__ == "__main__":
    main()
