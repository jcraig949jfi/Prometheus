"""Atomic-step stability between two independent decompositions of the same
frozen packet. Preregistration s7.1.

DESCRIPTIVE ONLY, stated in advance and repeated here because it is the
number most likely to be misread: this is a SAME-MODEL, same-session rerun.
A confabulator is also stable. High agreement is evidence of determinism, not
of correctness. The test that would matter is an independent decomposer
against the same packet, and it is not run this season.

Usage:
    python roles/Hypatia/science/season1/stability.py
"""
from __future__ import annotations

import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
LADDERS = HERE / "ladders"
ROWS = HERE / "results"

STOP = {"the", "a", "an", "of", "and", "or", "to", "is", "was", "were", "in",
        "on", "by", "at", "it", "its", "that", "this", "with", "as", "for",
        "so", "not", "but", "which", "are", "be", "from", "than", "then"}

PAIRS = [("POS-1", "atalanta"), ("POS-2", "hypatia"),
         ("POS-3", "nephele"), ("POS-4", "iris")]


def toks(s):
    return {t for t in re.split(r"[^a-z0-9_%:.]+", s.lower()) if t and t not in STOP}


def jac(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b) if (a | b) else 0.0


def load(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def depth(steps):
    by = {s["step"]: s for s in steps}
    memo = {}

    def d(i):
        if i in memo:
            return memo[i]
        deps = by[i].get("depends_on") or []
        memo[i] = 1 + max((d(x) for x in deps if x in by), default=0)
        return memo[i]
    return max((d(s["step"]) for s in steps), default=0)


def compare(a, b):
    """Greedy best-match of run-2 steps onto run-1 steps by token Jaccard."""
    used, matches = set(), []
    for s in a:
        best, bi = 0.0, None
        for t in b:
            if t["step"] in used:
                continue
            j = jac(toks(s["claim"]), toks(t["claim"]))
            if j > best:
                best, bi = j, t["step"]
        if bi is not None:
            used.add(bi)
            matches.append((s, next(t for t in b if t["step"] == bi), best))
    strong = [m for m in matches if m[2] >= 0.5]
    cls_agree = sum(1 for s, t, _ in strong
                    if s["reasoning_class"] == t["reasoning_class"])
    kind_agree = sum(1 for s, t, _ in strong if s["kind"] == t["kind"])
    return {
        "steps_run1": len(a), "steps_run2": len(b),
        "step_count_delta": len(b) - len(a),
        "matched_pairs": len(matches),
        "strong_matches_j>=0.5": len(strong),
        "strong_match_fraction": round(len(strong) / max(len(a), len(b)), 3),
        "mean_jaccard_all_pairs": round(sum(m[2] for m in matches) / len(matches), 3) if matches else 0.0,
        "mean_jaccard_strong": round(sum(m[2] for m in strong) / len(strong), 3) if strong else 0.0,
        "reasoning_class_agreement_on_strong": round(cls_agree / len(strong), 3) if strong else None,
        "kind_agreement_on_strong": round(kind_agree / len(strong), 3) if strong else None,
        "dag_depth_run1": depth(a), "dag_depth_run2": depth(b),
        "terminal_claim_jaccard": round(jac(
            toks(next((s["claim"] for s in a if s["kind"] == "terminal"), "")),
            toks(next((s["claim"] for s in b if s["kind"] == "terminal"), ""))), 3),
    }


def main():
    out = {}
    print("%-10s %5s %5s %6s %8s %8s %8s %7s %7s"
          % ("case", "n1", "n2", "dlt", "strongF", "meanJ_s", "clsAgr", "depth1", "depth2"))
    print("-" * 76)
    for tag, name in PAIRS:
        a = load(LADDERS / ("run1_%s_%s.jsonl" % (tag, name)))
        b = load(LADDERS / ("run2_%s_%s.jsonl" % (tag, name)))
        r = compare(a, b)
        out[name] = r
        print("%-10s %5d %5d %6d %8.3f %8.3f %8s %7d %7d"
              % (name, r["steps_run1"], r["steps_run2"], r["step_count_delta"],
                 r["strong_match_fraction"], r["mean_jaccard_strong"],
                 r["reasoning_class_agreement_on_strong"],
                 r["dag_depth_run1"], r["dag_depth_run2"]))
    print()
    print("terminal-claim agreement (the ruling itself):")
    for name, r in out.items():
        print("  %-10s jaccard %.3f" % (name, r["terminal_claim_jaccard"]))
    print()
    print("READ THIS AS DETERMINISM, NOT CORRECTNESS (preregistration s7.1):")
    print("  same model, same session. A confabulator is also stable.")
    ROWS.mkdir(parents=True, exist_ok=True)
    (ROWS / "stability.json").write_text(
        json.dumps({"note": ("SAME-MODEL same-session rerun; descriptive only; "
                             "high agreement is determinism, not correctness"),
                    "cases": out}, indent=2) + "\n", encoding="utf-8")
    print("rows: %s" % (ROWS / "stability.json").relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    main()
