"""benchmark_attack.py — how much of Apollo's 0.833 is available with no reasoning?

Prescribed by the 2026-08-23 external review (ChatGPT, §9.6): "actively attack the
benchmark with dumb heuristics before doing any architectural work. Not to improve Apollo
— to determine how much of the apparent capability is available without reasoning at all."

Every attacker below is a one-liner over (prompt, candidates). None inspects task
structure, none composes anything, none uses the operator registry. Reported per-subset
so a heuristic that only games one subset is visible as such.

Usage: python benchmark_attack.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "agents" / "hephaestus" / "src"))

NUM = re.compile(r"-?\d+\.?\d*")
WORD = re.compile(r"[a-z]+")


def load_battery():
    canary = json.loads((SRC.parent / "data" / "clean_canary_v01.json")
                        .read_text(encoding="utf-8"))["tasks"]
    from composition_gauntlet import build_synthetic_canary
    from inference_canary import build_inference_canary
    from cross_tier_canary import build_cross_tier_canary
    return [("canary", canary), ("synth", build_synthetic_canary(n_each=15)),
            ("inference", build_inference_canary(n=20)),
            ("cross_tier", build_cross_tier_canary(n=20))]


# ── attackers: (prompt, candidates) -> chosen candidate ────────────────

def a_first(p, c):      return c[0]
def a_last(p, c):       return c[-1]
def a_longest(p, c):    return max(c, key=len)
def a_shortest(p, c):   return min(c, key=len)


def a_lexical_overlap(p, c):
    """Candidate sharing the most word-tokens with the prompt."""
    pw = set(WORD.findall(p.lower()))
    return max(c, key=lambda x: len(pw & set(WORD.findall(x.lower()))))


def a_last_mentioned(p, c):
    """Candidate whose text appears latest in the prompt — recency bias."""
    lo = p.lower()
    return max(c, key=lambda x: lo.rfind(x.strip().lower()[:12]))


def a_first_mentioned(p, c):
    lo = p.lower()
    def pos(x):
        i = lo.find(x.strip().lower()[:12])
        return i if i >= 0 else 10 ** 6
    return min(c, key=pos)


def a_largest_number(p, c):
    def val(x):
        m = NUM.findall(x)
        return float(m[0]) if m else float("-inf")
    return max(c, key=val)


def a_number_in_prompt(p, c):
    """Candidate whose leading number occurs in the prompt."""
    nums = set(NUM.findall(p))
    for x in c:
        m = NUM.findall(x)
        if m and m[0] in nums:
            return x
    return c[0]


def a_not_in_prompt(p, c):
    """Candidate LEAST mentioned in the prompt — the odd-one-out bias."""
    lo = p.lower()
    return min(c, key=lambda x: lo.count(x.strip().lower()[:12]))


def a_always_yes(p, c):
    for x in c:
        if x.strip().lower().startswith("yes"):
            return x
    return c[0]


def a_alphabetical(p, c):   return sorted(c)[0]


def a_rarest_token(p, c):
    """Candidate containing the globally rarest word — a distributional cheat."""
    return min(c, key=lambda x: sum(GLOBAL_FREQ[w] for w in WORD.findall(x.lower())) or 0)


ATTACKERS = [
    ("first candidate", a_first), ("last candidate", a_last),
    ("longest candidate", a_longest), ("shortest candidate", a_shortest),
    ("alphabetically first", a_alphabetical),
    ("max lexical overlap w/ prompt", a_lexical_overlap),
    ("mentioned last in prompt", a_last_mentioned),
    ("mentioned first in prompt", a_first_mentioned),
    ("least mentioned in prompt", a_not_in_prompt),
    ("largest leading number", a_largest_number),
    ("leading number occurs in prompt", a_number_in_prompt),
    ("always answer yes", a_always_yes),
    ("rarest-token candidate", a_rarest_token),
]

GLOBAL_FREQ = Counter()


def main():
    subs = load_battery()
    allt = [t for _, ts in subs for t in ts]
    for t in allt:
        for x in t["candidates"]:
            GLOBAL_FREQ.update(WORD.findall(x.lower()))

    names = [n for n, _ in subs]
    print(f"battery: {len(allt)} tasks  |  mean candidates/task: "
          f"{sum(len(t['candidates']) for t in allt)/len(allt):.2f}  |  chance ~"
          f"{sum(1/len(t['candidates']) for t in allt)/len(allt):.3f}")
    print(f"\n{'heuristic':34s} {'ALL':>6s} " + " ".join(f"{n:>10s}" for n in names))
    print("-" * 34 + "-" * (7 + 11 * len(names)))

    rows = []
    for label, fn in ATTACKERS:
        per, tot = {}, 0
        for name, ts in subs:
            k = 0
            for t in ts:
                try:
                    if fn(t["prompt"], t["candidates"]) == t["correct"]:
                        k += 1
                except Exception:
                    pass
            per[name] = k / max(len(ts), 1)
            tot += k
        overall = tot / len(allt)
        rows.append((overall, label, per))
        print(f"{label:34s} {overall:>6.3f} "
              + " ".join(f"{per[n]:>10.3f}" for n in names))

    rows.sort(reverse=True)
    best, blabel, bper = rows[0]
    print(f"\nBEST TRIVIAL HEURISTIC: {blabel!r} at {best:.3f}")
    print(f"  per-subset: { 'ecdba'[:0] }" + json.dumps({k: round(v, 3) for k, v in bper.items()}))

    # oracle over the whole dumb portfolio: how much is reachable by ANY trivial rule?
    covered = set()
    for i, t in enumerate(allt):
        for _, fn in ATTACKERS:
            try:
                if fn(t["prompt"], t["candidates"]) == t["correct"]:
                    covered.add(i)
                    break
            except Exception:
                pass
    print(f"\nORACLE over all {len(ATTACKERS)} trivial heuristics (best-of, per task): "
          f"{len(covered)/len(allt):.3f}")
    print("  (an upper bound on what a trivial-rule PORTFOLIO could reach — the honest")
    print("   comparator for Apollo's 0.833 portfolio, not the 0.25 chance floor)")

    out = {"n_tasks": len(allt),
           "best_single_heuristic": {"label": blabel, "overall": round(best, 3),
                                     "per_subset": {k: round(v, 3) for k, v in bper.items()}},
           "all_heuristics": [{"label": l, "overall": round(o, 3),
                               "per_subset": {k: round(v, 3) for k, v in p.items()}}
                              for o, l, p in rows],
           "trivial_portfolio_oracle": round(len(covered) / len(allt), 3),
           "apollo_max_acc": 0.833, "apollo_portfolio_coverage": 0.833,
           "generated": "2026-08-23", "generator": "Apollo (M2)"}
    dest = SRC.parent / "pivot" / "benchmark_attack_2026-08-23.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
