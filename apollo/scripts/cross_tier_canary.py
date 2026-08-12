"""cross_tier_canary.py — tasks that REQUIRE composing R2 with R1.

Built after R2 Run 1 (pivot/r2_run1_findings_2026-06-10.md), which found that
evolution kept R2 as an isolated specialist because (1) no slot bridged R2 output
into R1 input and (2) no task rewarded crossing tiers. The bridge op
`relations_from_facts` fixes (1); this canary fixes (2).

Construct: a total order e0 > e1 > e2 > e3 over 4 entities. The two OUTER
comparisons (e0_gt_e1, e2_gt_e3) are STATED as facts. The MIDDLE link
(e1_gt_e2) — the one that fuses the two fragments into a single chain — is
HIDDEN behind an inference rule and must be DERIVED. The question asks for the
2nd-ranked entity (e1), whose rank depends entirely on the derived link:

  - With the derived link e1_gt_e2: order is e0>e1>e2>e3, 2nd = e1  (correct)
  - Without it: e1 dominates nobody while e2 dominates e3, so e2 outranks e1
    and the 2nd-ranked comes out wrong.

The ONLY pipeline that solves it spans three tiers:
    parse_rules -> parse_ordinal -> forward_chain -> relations_from_facts
                 -> op_build_ordering -> select_nth
R0-R1-only can't parse the rule/fact format; R2-only yields derivability, not
rank. So a correct solver is a genuine multi-tier organism by construction.

Atoms encode comparisons as '<a>_gt_<b>' (valid \\w+ tokens so parse_rules reads
them). Entity names are equal-length so longest-candidate heuristics are useless.
"""
from __future__ import annotations
import random

# equal-length (5-char) names so the terminal-only (longest-candidate) baseline
# is blind and no length heuristic can leak the answer
_ENTITIES = ["alpha", "bravo", "clara", "delta", "felix", "gamma", "hotel",
             "india", "kilos", "limas", "novas", "oscar", "romeo", "tango"]


def gen_cross_tier_rank(rng: random.Random) -> dict:
    """One derive-then-order task. See module docstring for construct validity."""
    ents = rng.sample(_ENTITIES, 4)        # ground-truth order ents[0] > ents[1] > ents[2] > ents[3]
    e0, e1, e2, e3 = ents

    def gt(a, b):
        return f"{a}_gt_{b}"

    # Stated facts: the two OUTER links. The middle link (e1>e2) is withheld.
    stated = [gt(e0, e1), gt(e2, e3)]
    # Inference rule that derives the hidden middle link from a stated fact.
    # "If e2_gt_e3 then e1_gt_e2" — firing it fuses the chain.
    rule_text = f"If {gt(e2, e3)} then {gt(e1, e2)}"
    # A distractor rule that never fires (premise is not asserted/derivable).
    far = rng.sample([e for e in _ENTITIES if e not in ents], 2)
    distractor_rule = f"If {gt(far[0], far[1])} then {gt(far[1], far[0])}"

    clauses = [f"{s} is true" for s in stated] + [rule_text, distractor_rule]
    rng.shuffle(clauses)
    prompt = ". ".join(clauses) + ". Who is the second highest?"

    cands = [e0, e1, e2, e3]
    rng.shuffle(cands)
    return {
        "category": "cross_tier_rank",
        "prompt": prompt,
        "candidates": cands,
        "correct": e1,                      # 2nd in the full order; needs the derived link
        "requires_intermediate": "derived_facts->relations->ordered",
        # what 'pick a subject of a stated comparison' would give (never e1):
        "single_primitive_answer": e0,
    }


def build_cross_tier_canary(n=30, seed=20260610) -> list[dict]:
    rng = random.Random(seed)
    return [gen_cross_tier_rank(rng) for _ in range(n)]


if __name__ == "__main__":
    tasks = build_cross_tier_canary(5)
    for t in tasks:
        print(t["prompt"])
        print("   candidates:", t["candidates"], "correct:", t["correct"])
