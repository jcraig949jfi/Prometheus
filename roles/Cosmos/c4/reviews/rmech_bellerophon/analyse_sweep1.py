"""Recomputes every number quoted in R-MECH_Bellerophon_INTERIM_2026-09-30.md from sweep1.jsonl (attack_harness.py output).
    python analyse_sweep1.py sweep1.jsonl  -> JSON on stdout
"""
import collections, json, sys

from scipy.stats import binom

E_SYSID, V = 1500, 4


def ba(pred, truth):
    pos = [p for p, t in zip(pred, truth) if t]; neg = [p for p, t in zip(pred, truth) if not t]
    return 0.5 * (sum(pos) / len(pos) + sum(1 - p for p in neg) / len(neg))


def main(path):
    R = [json.loads(l) for l in open(path, encoding="utf-8")]
    thr = binom.isf(0.01, E_SYSID, 1 / V) / E_SYSID                  # zero-parameter: significance of held-out accuracy > 1/V
    det = [r for r in R if r["A_class"] in ("FUNCTIONAL", "PASSIVE", "NONE")]
    truth = [r["A_class"] == "FUNCTIONAL" for r in det]
    rel = [r["REL_at_q"] > thr for r in det]; t3 = [r["T3"] == "FUNCTIONAL" for r in det]; b = [r["B"]["functional"] for r in det]
    idx = {(r["a"], r["sigma"], r["k"]): r for r in R}
    s4 = [{"a": a, "k": k, "sigma": [s, s2], "A": [r["A_class"], r2["A_class"]], "T3": [r["T3"], r2["T3"]],
           "REL_at_q": [r["REL_at_q"], r2["REL_at_q"]], "B": [r["B"]["functional"], r2["B"]["functional"]]}
          for (a, s, k), r in sorted(idx.items()) for s2 in (0.3, 0.8, 1.5)
          if (a, s2, k) in idx and s2 > s and r["A_class"] == "FUNCTIONAL" and idx[(a, s2, k)]["A_class"] == "NONE"
          for r2 in [idx[(a, s2, k)]]]
    g3 = all(len({json.dumps(r["REL"], sort_keys=True) for r in R if (r["a"], r["sigma"]) == w}) == 1 for w in {(r["a"], r["sigma"]) for r in R})
    out = {"rows": len(R), "A_classes": dict(collections.Counter(r["A_class"] for r in R)),
           "T3_classes": dict(collections.Counter(r["T3"] for r in R)), "determinate": len(det), "A_FUNCTIONAL": sum(truth),
           "REL_threshold": thr, "BA": {"REL_at_q_rule": ba(rel, truth), "T3_DOWN": ba(t3, truth), "B_USE": ba(b, truth)},
           "agree_with_A": {"REL_at_q_rule": sum(x == y for x, y in zip(rel, truth)), "B_USE": sum(x == y for x, y in zip(b, truth))},
           "G3_REL_identical_across_k": g3, "excluded_rows": len(R) - len(det), "S4_examples": s4}
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1])
