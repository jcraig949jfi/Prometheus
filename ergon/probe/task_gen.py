"""Task manifest generator for the Metabolization Probe (prereg §2, §3).

A hardened fork of `ergon/learner/greedy/ood_judgement.py`. Three things differ, each because
of something measured (prereg §0):

  * **Balanced by construction.** The June file was 80/80/80/80/80/80/14 — `ood_inequality`
    truncated. Here every (domain, label) cell is exactly `per_class`, asserted before write.
  * **A difficulty dial.** L0 reproduces the June ranges; L1–L3 scale operand magnitude by
    10^2 / 10^4 / 10^6 and make the near-miss structure mandatory. The dial exists because a
    frontier solver has no headroom on `gcd(8566, 907)`, and R4 demands >=25pp.
  * **Gold is computed, never judged** (R1). Every label here is decided by Python arithmetic
    on the spot; no LLM, no lookup, no stored answer key.

The near-miss structure is the point: at L2/L3 a raw solver without tools must actually execute
the arithmetic, because the false instances sit one unit away from the true ones. Recognition
of surface form is insufficient by construction.

    python -m ergon.probe.task_gen --level L2 --per-class 60 --out manifest.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import random
from typing import Callable

#: prereg §2 — the frozen seed sequence. Replenishment draws the NEXT unconsumed seed; this is
#: a preregistered branch, not an amendment (meta-synthesis §7.5c).
SEED_SEQUENCE = (20260813, 20260814, 20260815, 20260816, 20260817)

LEVELS = ("L0", "L1", "L2", "L3")

#: Operand magnitude per level. L0 = the June ranges, kept so the dial has a measured anchor.
_SCALE = {"L0": 1, "L1": 10 ** 2, "L2": 10 ** 4, "L3": 10 ** 6}

DOMAINS = (
    "ood_primality",
    "ood_divisibility",
    "ood_coprime",
    "ood_perfect_square",
    "ood_modular",
    "ood_inequality",
    "ood_summation",
)


def _is_prime(n: int) -> bool:
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


def _rand_prime(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        c = rng.randint(lo, hi) | 1
        if _is_prime(c):
            return c


def _row(claim: str, gold: bool, domain: str, level: str, idx: int) -> dict:
    return {
        "uid": f"{domain}-{level}-{idx:05d}",
        "domain": domain,
        "level": level,
        "claim": claim,
        "gold_bool": gold,
        # The frozen prompt. Carries verdict words in two places — which is exactly why the
        # extractor strips both fragments before parsing (extract._PROMPT_FRAGMENTS).
        "prompt": (f"Claim: {claim}\n"
                   "Is this claim true? Answer True or False, then justify in one sentence."),
    }


# --------------------------------------------------------------------------- generators
# Every generator emits `n` True and `n` False instances. False instances are NEAR MISSES.

def gen_primality(rng, n, level, s):
    rows = []
    lo, hi = 100 * s, 50_000 * s
    for i in range(n):
        rows.append(_row(f"{_rand_prime(rng, lo, hi)} is a prime number.", True,
                         "ood_primality", level, i))
    for i in range(n):
        if s == 1:
            c = rng.randint(lo, hi)
            while _is_prime(c):
                c = rng.randint(lo, hi)
        else:  # semiprime with both factors large — no small-divisor shortcut
            c = _rand_prime(rng, 10 ** 3, 10 ** 4) * _rand_prime(rng, lo // 10 ** 4 or 2, hi // 10 ** 3)
        rows.append(_row(f"{c} is a prime number.", False, "ood_primality", level, n + i))
    return rows


def gen_divisibility(rng, n, level, s):
    rows = []
    for i in range(n):
        a = rng.randint(2, 97) * max(1, s // 100)
        q = rng.randint(2, 500) * s
        rows.append(_row(f"{a} divides {a * q}.", True, "ood_divisibility", level, i))
    for i in range(n):
        a = rng.randint(3, 97) * max(1, s // 100)
        b = a * rng.randint(2, 500) * s + rng.randint(1, max(1, a - 1))
        rows.append(_row(f"{a} divides {b}.", False, "ood_divisibility", level, n + i))
    return rows


def gen_coprime(rng, n, level, s):
    rows, made_t, made_f, i = [], 0, 0, 0
    lo, hi = 6 * s, 9999 * s
    while made_t < n or made_f < n:
        a, b = rng.randint(lo, hi), rng.randint(lo, hi)
        g = math.gcd(a, b)
        claim = f"{a} and {b} are coprime (share no common factor greater than 1)."
        if g == 1 and made_t < n:
            rows.append(_row(claim, True, "ood_coprime", level, i)); made_t += 1; i += 1
        elif g > 1 and made_f < n:
            rows.append(_row(claim, False, "ood_coprime", level, i)); made_f += 1; i += 1
    return rows


def gen_perfect_square(rng, n, level, s):
    rows = []
    lo, hi = 12 * s, 700 * s
    for i in range(n):
        k = rng.randint(lo, hi)
        rows.append(_row(f"{k * k} is a perfect square.", True, "ood_perfect_square", level, i))
    for i in range(n):
        k = rng.randint(lo, hi)
        m = k * k + rng.choice([-2, -1, 1, 2, 3])  # off-by-one from a square: near miss
        if math.isqrt(m) ** 2 == m:
            m += 1
        rows.append(_row(f"{m} is a perfect square.", False, "ood_perfect_square", level, n + i))
    return rows


def gen_modular(rng, n, level, s):
    rows = []
    m_hi, a_hi = 50 * s, 9999 * s
    for i in range(n):
        m = rng.randint(3, max(4, m_hi))
        a = rng.randint(50, a_hi)
        rows.append(_row(f"{a} is congruent to {a % m} modulo {m}.", True,
                         "ood_modular", level, i))
    for i in range(n):
        m = rng.randint(3, max(4, m_hi))
        a = rng.randint(50, a_hi)
        wrong = (a % m + rng.randint(1, max(1, m - 1))) % m
        rows.append(_row(f"{a} is congruent to {wrong} modulo {m}.", False,
                         "ood_modular", level, n + i))
    return rows


def gen_inequality(rng, n, level, s):
    rows = []
    k_hi = {1: 22, 100: 60, 10_000: 120, 1_000_000: 200}[s]
    for i in range(n):
        k = rng.randint(5, k_hi)
        # within 1% of 2^k, from below: the comparison cannot be eyeballed by digit count
        n_ = 2 ** k - rng.randint(1, max(1, 2 ** k // 100))
        rows.append(_row(f"2^{k} is greater than {n_}.", True, "ood_inequality", level, i))
    for i in range(n):
        k = rng.randint(5, k_hi)
        n_ = 2 ** k + rng.randint(0, max(1, 2 ** k // 100))
        rows.append(_row(f"2^{k} is greater than {n_}.", False, "ood_inequality", level, n + i))
    return rows


def gen_summation(rng, n, level, s):
    rows = []
    hi = 400 * s
    for i in range(n):
        n_ = rng.randint(5, hi)
        t = n_ * (n_ + 1) // 2
        rows.append(_row(f"The sum of the first {n_} positive integers equals {t}.", True,
                         "ood_summation", level, i))
    for i in range(n):
        n_ = rng.randint(5, hi)
        t = n_ * (n_ + 1) // 2 + rng.choice([-n_, n_, 1, -1, n_ + 1])
        if t == n_ * (n_ + 1) // 2:
            t += 1
        rows.append(_row(f"The sum of the first {n_} positive integers equals {t}.", False,
                         "ood_summation", level, n + i))
    return rows


GENERATORS: dict[str, Callable] = {
    "ood_primality": gen_primality,
    "ood_divisibility": gen_divisibility,
    "ood_coprime": gen_coprime,
    "ood_perfect_square": gen_perfect_square,
    "ood_modular": gen_modular,
    "ood_inequality": gen_inequality,
    "ood_summation": gen_summation,
}


def generate(level: str = "L2", per_class: int = 30, seed: int = SEED_SEQUENCE[0],
             domains=DOMAINS) -> list[dict]:
    """Balanced by construction: every (domain, label) cell is exactly `per_class`."""
    if level not in LEVELS:
        raise ValueError(f"unknown level {level!r}; expected one of {LEVELS}")
    rng = random.Random(f"{seed}:{level}")
    s = _SCALE[level]
    rows: list[dict] = []
    for d in domains:
        rows.extend(GENERATORS[d](rng, per_class, level, s))

    # Assert the balance rather than trusting it — the June manifest's defect was silent.
    from collections import Counter
    cells = Counter((r["domain"], r["gold_bool"]) for r in rows)
    for d in domains:
        for label in (True, False):
            got = cells[(d, label)]
            if got != per_class:
                raise AssertionError(f"unbalanced cell {d}/{label}: {got} != {per_class}")
    rng.shuffle(rows)
    return rows


def manifest_sha256(rows: list[dict]) -> str:
    blob = "\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def generator_sha256() -> str:
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()


def write(rows: list[dict], path: pathlib.Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"n": len(rows),
            "manifest_sha256": manifest_sha256(rows),
            "generator_sha256": generator_sha256()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", default="L2", choices=LEVELS)
    ap.add_argument("--per-class", type=int, default=30)
    ap.add_argument("--seed", type=int, default=SEED_SEQUENCE[0])
    ap.add_argument("--out", default="ergon/probe/manifests/manifest.jsonl")
    args = ap.parse_args()
    rows = generate(args.level, args.per_class, args.seed)
    meta = write(rows, pathlib.Path(args.out))
    from collections import Counter
    print(f"[task_gen] level={args.level} n={meta['n']} "
          f"true={sum(r['gold_bool'] for r in rows)} false={sum(not r['gold_bool'] for r in rows)}")
    print(f"[task_gen] by_domain={dict(Counter(r['domain'] for r in rows))}")
    print(f"[task_gen] manifest_sha256={meta['manifest_sha256']}")
    print(f"[task_gen] generator_sha256={meta['generator_sha256']}")


if __name__ == "__main__":
    main()
