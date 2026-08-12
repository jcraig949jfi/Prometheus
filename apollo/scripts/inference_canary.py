"""inference_canary.py — constraint-tracking canary for R2 evolution.

Production generator for multi-hop forward-chaining tasks, factored out so
both the evolve loop and any audit can build the same task family. The
2026-06-09 R2 falsification (scripts/r2_falsification.py) validated this
construct: the correct answer is reachable ONLY by multi-hop forward
chaining (never stated; no ordering/count/length structure), so the R0-R1
substrate sits at chance while parse_rules->forward_chain->score_by_derivability
solves it with derived_facts load-bearing.

Mirrors composition_gauntlet.build_synthetic_canary so evolve() can mix it
into the eval set the same way.
"""
from __future__ import annotations
import random

_ATOMS = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
          "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
          "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]


def gen_inference_chain(rng: random.Random) -> dict:
    """One multi-hop forward-chaining task. See module docstring for the
    construct-validity argument."""
    pool = rng.sample(_ATOMS, 12)
    L = rng.choice([4, 5])
    chain = pool[:L]
    rules = [(chain[i], chain[i + 1]) for i in range(L - 1)]

    d_pool = pool[L:L + 3]
    distractor_rules = [(d_pool[0], d_pool[1])]   # never fired (no asserted fact)
    unmentioned = d_pool[2]

    all_rules = rules + distractor_rules
    rng.shuffle(all_rules)
    rule_text = ". ".join(f"If {a} then {b}" for a, b in all_rules)

    depth = rng.randint(2, L - 1)                 # answer is >= 2 hops deep
    correct = chain[depth]
    base_fact = chain[0]
    prompt = f"{rule_text}. {base_fact} is true. Which of the following can be derived?"

    cands = [correct, d_pool[0], d_pool[1], unmentioned]  # exactly one derivable
    rng.shuffle(cands)
    return {
        "category": "inference_chain",
        "prompt": prompt,
        "candidates": cands,
        "correct": correct,
        "requires_intermediate": "derived_facts",
        "single_primitive_answer": base_fact,  # surface-extraction of the stated fact
    }


def build_inference_canary(n=20, seed=20260609) -> list[dict]:
    rng = random.Random(seed)
    return [gen_inference_chain(rng) for _ in range(n)]


if __name__ == "__main__":
    tasks = build_inference_canary()
    print(f"{len(tasks)} inference tasks; example:")
    print(tasks[0]["prompt"])
    print("candidates:", tasks[0]["candidates"], "correct:", tasks[0]["correct"])
