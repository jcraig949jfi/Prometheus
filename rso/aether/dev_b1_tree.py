"""C-018-T041 s10.6 dev evidence: Pallas's invariant-respecting B1 tamper (challenge/synth.py b1_invariant, run unchanged on
dev RX k=0) against the real per-unit Aether tree replay (confirm.tree_problem). Development seed only.

    python -B -m rso.aether.dev_b1_tree   -> prints JSON (committed as qual/B1_TREE_REPLAY_v1_1_0.json)
"""
import json
import sys

from rso.aether import confirm as C
from rso.aether.challenge import synth as S


def main():
    seen = []
    classify = S.classify
    S.classify = lambda m, a: (seen.append(m), classify(m, a))[1]      # capture the tampered meta b1_invariant builds
    try:
        m0, a0 = S.load_dev("native_RX_0")
        res = S.b1_invariant(m0, a0)
    finally:
        S.classify = classify
    tampered = seen[-1]
    out = {"tamper": {k: res[k] for k in ("before", "after", "problems_after", "invariants_after")},
           "reparented": len(res["reparented"]),
           "tree_problem_genuine": C.tree_problem("RX", 0, m0),
           "tree_problem_tampered": C.tree_problem("RX", 0, tampered)}
    print(json.dumps(out, indent=1, sort_keys=True, default=str))
    return 0 if out["tree_problem_genuine"] is None and out["tree_problem_tampered"] else 1


if __name__ == "__main__":
    sys.exit(main())
