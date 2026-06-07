"""Computable-gold OOD judgement set.

CounterMATH's ground truth is withheld by design (leaderboard-only — see
THUKElab/COUNTERMATH README), so a real authoritative CounterMath accuracy
number is not obtainable offline. This builds an alternative OOD probe whose
gold labels are COMPUTED deterministically (no LLM-judge, no leaked answer),
on elementary number-theory / arithmetic relations that are DISJOINT from the
training corpus (knot x EC invariants, Mahler-measure correlations, concept
forge). It tests the same *skill* the substrate training targets — judge
whether a stated math relation holds, emit True/False — on unseen object/
relation types.

Output rows are schema-compatible with eval_greedy.score() (prompt, gold_bool,
source), so scoring reuses the existing harness:

    python -m ergon.learner.greedy.ood_judgement --out ergon/learner/greedy/corpus/ood_gold.jsonl
    python -m ergon.learner.greedy.eval_greedy --gold ergon/learner/greedy/corpus/ood_gold.jsonl \
        --lora ergon/learner/greedy/runs/ablation/abl_full \
        --out  ergon/learner/greedy/runs/eval_ood.json

Each domain is generated balanced 50/50 true/false with a fixed seed.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import List, Tuple

from .serializers import make_judgement


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def next_prime(n: int) -> int:
    m = n + 1
    while not is_prime(m):
        m += 1
    return m


def _row(claim: str, gold: bool, just: str, domain: str, idx: int) -> dict:
    prompt, completion = make_judgement(claim, gold, just)
    return {"prompt": prompt, "completion": completion, "gold_bool": gold,
            "source": domain, "domain": domain, "tier": 1,
            "uid": f"ood-{domain}-{idx}"}


def gen_primality(rng: random.Random, n_each: int) -> List[dict]:
    rows = []
    primes, comps = [], []
    while len(primes) < n_each or len(comps) < n_each:
        x = rng.randint(100, 50000)
        if is_prime(x) and len(primes) < n_each:
            primes.append(x)
        elif not is_prime(x) and len(comps) < n_each:
            comps.append(x)
    for i, p in enumerate(primes):
        rows.append(_row(f"{p} is a prime number.", True, f"{p} has no divisor other than 1 and itself.", "ood_primality", i))
    for i, c in enumerate(comps):
        d = next(k for k in range(2, c) if c % k == 0)
        rows.append(_row(f"{c} is a prime number.", False, f"{c} is divisible by {d}.", "ood_primality", n_each + i))
    return rows


def gen_divisibility(rng: random.Random, n_each: int) -> List[dict]:
    rows = []
    for i in range(n_each):
        a = rng.randint(2, 97)
        q = rng.randint(2, 500)
        b = a * q  # a | b
        rows.append(_row(f"{a} divides {b}.", True, f"{b} = {a} x {q}.", "ood_divisibility", i))
    for i in range(n_each):
        a = rng.randint(3, 97)
        b = a * rng.randint(2, 500) + rng.randint(1, a - 1)  # not divisible
        rows.append(_row(f"{a} divides {b}.", False, f"{b} mod {a} = {b % a}.", "ood_divisibility", n_each + i))
    return rows


def gen_coprime(rng: random.Random, n_each: int) -> List[dict]:
    rows = []
    made_t = made_f = 0
    i = 0
    while made_t < n_each or made_f < n_each:
        a = rng.randint(6, 9999)
        b = rng.randint(6, 9999)
        g = math.gcd(a, b)
        if g == 1 and made_t < n_each:
            rows.append(_row(f"{a} and {b} are coprime (share no common factor greater than 1).", True,
                             f"gcd({a}, {b}) = 1.", "ood_coprime", i)); made_t += 1; i += 1
        elif g > 1 and made_f < n_each:
            rows.append(_row(f"{a} and {b} are coprime (share no common factor greater than 1).", False,
                             f"gcd({a}, {b}) = {g}.", "ood_coprime", i)); made_f += 1; i += 1
    return rows


def gen_perfect_square(rng: random.Random, n_each: int) -> List[dict]:
    rows = []
    for i in range(n_each):
        k = rng.randint(12, 700)
        rows.append(_row(f"{k*k} is a perfect square.", True, f"{k*k} = {k}^2.", "ood_perfect_square", i))
    for i in range(n_each):
        k = rng.randint(12, 700)
        n = k * k + rng.choice([-1, 1, 2, 3, -2])  # near a square but not one
        if math.isqrt(n) ** 2 == n:
            n += 1
        rows.append(_row(f"{n} is a perfect square.", False,
                         f"{math.isqrt(n)}^2 = {math.isqrt(n)**2} and {math.isqrt(n)+1}^2 = {(math.isqrt(n)+1)**2}, so {n} is between consecutive squares.",
                         "ood_perfect_square", n_each + i))
    return rows


def gen_modular(rng: random.Random, n_each: int) -> List[dict]:
    rows = []
    for i in range(n_each):
        m = rng.randint(3, 50)
        a = rng.randint(50, 9999)
        r = a % m
        rows.append(_row(f"{a} is congruent to {r} modulo {m}.", True, f"{a} mod {m} = {r}.", "ood_modular", i))
    for i in range(n_each):
        m = rng.randint(3, 50)
        a = rng.randint(50, 9999)
        true_r = a % m
        wrong_r = (true_r + rng.randint(1, m - 1)) % m
        rows.append(_row(f"{a} is congruent to {wrong_r} modulo {m}.", False,
                         f"{a} mod {m} = {true_r}, not {wrong_r}.", "ood_modular", n_each + i))
    return rows


def gen_inequality(rng: random.Random, n_each: int) -> List[dict]:
    rows = []
    # sample n relative to 2^k so True/False are balanced by construction
    for i in range(n_each):
        k = rng.randint(5, 22)
        n = rng.randint(2, 2 ** k - 1)  # n < 2^k -> claim True
        rows.append(_row(f"2^{k} is greater than {n}.", True, f"2^{k} = {2**k}.", "ood_inequality", i))
    for i in range(n_each):
        k = rng.randint(5, 22)
        n = rng.randint(2 ** k, 2 ** (k + 2))  # n >= 2^k -> claim False
        rows.append(_row(f"2^{k} is greater than {n}.", False, f"2^{k} = {2**k}.", "ood_inequality", n_each + i))
    return rows


def gen_summation(rng: random.Random, n_each: int) -> List[dict]:
    rows = []
    for i in range(n_each):
        n = rng.randint(5, 400)
        T = n * (n + 1) // 2
        rows.append(_row(f"The sum of the first {n} positive integers equals {T}.", True,
                         f"n(n+1)/2 = {n}*{n+1}/2 = {T}.", "ood_summation", i))
    for i in range(n_each):
        n = rng.randint(5, 400)
        T = n * (n + 1) // 2 + rng.choice([-n, n, 1, -1, n + 1])
        if T == n * (n + 1) // 2:
            T += 1
        rows.append(_row(f"The sum of the first {n} positive integers equals {T}.", False,
                         f"n(n+1)/2 = {n*(n+1)//2}, not {T}.", "ood_summation", n_each + i))
    return rows


GENERATORS = {
    "ood_primality": gen_primality,
    "ood_divisibility": gen_divisibility,
    "ood_coprime": gen_coprime,
    "ood_perfect_square": gen_perfect_square,
    "ood_modular": gen_modular,
    "ood_inequality": gen_inequality,
    "ood_summation": gen_summation,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="F:/Prometheus/ergon/learner/greedy/corpus/ood_gold.jsonl")
    ap.add_argument("--per-class", type=int, default=40, help="items per (domain, label)")
    ap.add_argument("--seed", type=int, default=20260607)
    ap.add_argument("--domains", default="", help="comma list of domains to include (default: all)")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    want = set(d.strip() for d in args.domains.split(",") if d.strip()) or set(GENERATORS)
    rows: List[dict] = []
    for name, fn in GENERATORS.items():
        if name not in want:
            continue
        rows.extend(fn(rng, args.per_class))
    rng.shuffle(rows)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    from collections import Counter
    by_dom = Counter(r["source"] for r in rows)
    n_true = sum(r["gold_bool"] for r in rows)
    print(f"[ood] wrote {len(rows)} rows to {out}")
    print(f"[ood] true={n_true} false={len(rows)-n_true}")
    print(f"[ood] by_domain={dict(by_dom)}")


if __name__ == "__main__":
    main()
