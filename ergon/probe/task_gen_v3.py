"""Task family v3 — adversarial near-misses on the PROPERTY (Candidate A).

WHY THIS FAMILY, from the measured negatives rather than from taste:

  * v1 (operand magnitude): dead. Non-monotone, 72.6 -> 53.6 -> 64.3 -> 59.5.
  * v2 (compositional depth 1..20): dead. mean 94.4%, r(depth,acc) = +0.394, a 20-step chain
    solved 40/40. **Execution length is not where this solver fails.**

So difficulty must come from where **recognition** fails: instances that look like one thing and
are another. The solver's arithmetic is excellent; the target is its *choice of test*.

THE INSTANCES. Primality, with composites chosen to defeat the cheap test a solver reaches for:

  * `A0` random composites with small factors      — trial division finds them; no deception
  * `A1` semiprimes with both factors > 10^4        — no small-divisor shortcut; real work needed
  * `A2` Fermat pseudoprimes base 2                 — pass `2^(n-1) = 1 mod n` and are composite
  * `A3` Carmichael numbers                         — Fermat-liars for EVERY coprime base

`A2`/`A3` are the point: a solver that applies a Fermat test and stops is *confidently wrong*, and
wrong for a reason a prior attempt could have recorded. That is the difficulty axis, and it is
MEASURED per rung (three axes died from hypothesised effects, so nothing here is assumed).

THE ANSWER SPACE stays wide, which the v2 work established as load-bearing. The task is a COUNT:
"of these five numbers, how many are prime?" — chance is 1/4 = 0.25 over the balanced answer
range {1,2,3,4}, comfortably BELOW the band floor of 0.35, so a coin cannot be `LEVELED`. Partial
reasoning does not earn partial credit: one misjudged element moves the count and the answer is
wrong.

GOLD IS COMPUTED, NEVER JUDGED (R1). Primality is decided by deterministic Miller-Rabin over the
first twelve prime bases, which is exact below 3.3e24 — every n here is far below that. Carmichael
and pseudoprime instances are *verified composite by that same routine* rather than trusted from a
table.

RESIDUE PLAUSIBILITY AT D0 — the requirement that outranks headroom (§3 of the kickoff), and this
family's real argument:

    A prior failed attempt records, per element, the TEST IT APPLIED and the conclusion it drew
    ("8911: 2^(n-1) = 1 mod n, so prime"). Under prereg §4.2 the record carries no gold and no
    correctness flag — so the packet hands the next attempt the *method that was used*, not the
    answer. A next attempt reading "the prior run decided this by a single Fermat base" can
    choose a stronger test without ever being told which element was misjudged.

That is residue about the VERB, not the noun — the failed operation rather than the object label —
and it is informative precisely because the failure is a method failure. On v1 the residue could
only restate the answer; on v2 it localized a step; here it names the fallible procedure. It is
also why this family fits `feedback_verbs_over_nouns`: what transfers is the operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import random
from collections import Counter

SEED_SEQUENCE = (20260817, 20260818, 20260819)

#: Pre-declared, ordered rungs. Effect on accuracy is MEASURED, not assumed.
LEVELS = ("A0", "A1", "A2", "A3")

#: INTERMEDIATE RUNGS, added 2026-08-18 after the clean sweep measured the axis as far steeper
#: than the truncated run suggested: A0 82.5% -> A1 25.0%, a 57.5pp cliff with NOTHING in the
#: band between them. A1/A2/A3 all sit at exactly 25.0%, which IS chance on this task, so they
#: are at the floor rather than merely hard. This is rung re-spacing inside a WORKING axis, not
#: a new axis — the mixing fraction interpolates between two MEASURED endpoints, so an
#: intermediate rung is guaranteed to land between them rather than hoped to.
#:
#: The knob is the fraction of a task's composites drawn as hard (semiprime, A1-style) rather
#: than easy (small-factor, A0-style). Deception is thereby made PARTIAL: some elements of the
#: count are deceptive and some are not, which is exactly the "mixed count" shape.
LEVELS_MIX = ("M20", "M40", "M60", "M80")
#: Bisection rung, PRE-DECLARED 2026-08-19 before measurement. The paid-host decision run put
#: M20 at 0.640 (above band, movable 0.385 PASSES); the free-host curve is monotone in mix
#: fraction; so the in-band region lies between M20 and M40 on the operative host. M30 bisects.
#: Swept together with M40 under Bonferroni k=2 — no sequential stopping.
LEVELS_MIX_PAID = ("M30", "M40")
LEVEL_M30 = ("M30",)
_MIX_FRACTION = {"M20": 0.20, "M30": 0.30, "M40": 0.40, "M60": 0.60, "M80": 0.80}
ALL_LEVELS = LEVELS + LEVELS_MIX + LEVELS_MIX_PAID

#: Elements per task. The answer is how many of them are prime.
K = 5
#: Balanced answer range — 0 and 5 are excluded so a degenerate "none/all" guess cannot score.
ANSWER_RANGE = (1, 2, 3, 4)

_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin — exact for n < 3.3e24, which covers everything generated here."""
    if n < 2:
        return False
    for p in _MR_BASES:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in _MR_BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _rand_prime(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        c = rng.randint(lo, hi) | 1
        if is_prime(c):
            return c


def _fermat_liar_base2(n: int) -> bool:
    return pow(2, n - 1, n) == 1


# ---------------------------------------------------------------------------- composite makers

def _composite_small_factor(rng: random.Random) -> int:
    """A0 — trial division finds it immediately."""
    while True:
        n = rng.choice([3, 5, 7, 11, 13]) * rng.randint(2_000, 200_000)
        if not is_prime(n):
            return n


def _composite_semiprime(rng: random.Random) -> int:
    """A1 — both factors large, so no small-divisor shortcut exists."""
    p = _rand_prime(rng, 10_000, 99_999)
    q = _rand_prime(rng, 10_000, 99_999)
    return p * q


def _pseudoprime_base2(rng: random.Random, cache: list[int]) -> int:
    """A2 — composite that satisfies Fermat base 2. Searched and verified, never tabulated."""
    if not cache:
        n = 340  # first base-2 Fermat pseudoprime is 341
        found = 0
        while found < 400 and n < 3_000_000:
            n += 1
            if n % 2 == 0:
                continue
            if _fermat_liar_base2(n) and not is_prime(n):
                cache.append(n)
                found += 1
    return rng.choice(cache)


def _carmichael(rng: random.Random, cache: list[int]) -> int:
    """A3 — Fermat-liar for every coprime base. Chernick form (6k+1)(12k+1)(18k+1), all prime,
    then VERIFIED composite and verified to satisfy Korselt's criterion."""
    if not cache:
        for k in range(1, 40_000):
            a, b, c = 6 * k + 1, 12 * k + 1, 18 * k + 1
            if is_prime(a) and is_prime(b) and is_prime(c):
                n = a * b * c
                if not is_prime(n) and all((n - 1) % (p - 1) == 0 for p in (a, b, c)):
                    cache.append(n)
            if len(cache) >= 60:
                break
    return rng.choice(cache)


_COMPOSITE_FOR = {
    "A0": lambda rng, c: _composite_small_factor(rng),
    "A1": lambda rng, c: _composite_semiprime(rng),
    "A2": lambda rng, c: _pseudoprime_base2(rng, c["p2"]),
    "A3": lambda rng, c: _carmichael(rng, c["cm"]),
}

def _prime_with_digits(rng: random.Random, digits: int) -> int:
    lo = 10 ** (digits - 1)
    hi = 10 ** digits - 1
    return _rand_prime(rng, max(2, lo), hi)


def _mixed_composites(rng: random.Random, level: str, n_comps: int, cache: dict) -> list[int]:
    """Split a task's composites between hard (semiprime) and easy (small-factor).

    Deterministic count with a stochastic remainder, so the realised fraction is unbiased at the
    manifest level even though a single task holds only 1-4 composites.
    """
    frac = _MIX_FRACTION[level]
    exact = frac * n_comps
    n_hard = int(exact) + (1 if rng.random() < (exact - int(exact)) else 0)
    n_hard = max(0, min(n_comps, n_hard))
    return ([_composite_semiprime(rng) for _ in range(n_hard)]
            + [_composite_small_factor(rng) for _ in range(n_comps - n_hard)])


def _task(rng: random.Random, level: str, n_primes: int, cache: dict) -> dict:
    """Composites FIRST, then primes matched to their DIGIT LENGTHS.

    Caught before any data existed: at A3 the Chernick Carmichaels run 13-17 digits while the
    prime range was 10^8-10^10, so "the long ones are composite" would have answered the task
    without touching primality. That is the uid-index leak's class — an unintended channel
    carrying the answer — and the fix is to remove the channel rather than to hope the solver
    ignores it. Magnitude was already measured dead as a difficulty axis (v1), so nothing is
    lost by matching it exactly.
    """
    n_comps = K - n_primes
    if level in _MIX_FRACTION:
        comps = _mixed_composites(rng, level, n_comps, cache)
    else:
        comps = [_COMPOSITE_FOR[level](rng, cache) for _ in range(n_comps)]
    comp_digits = [len(str(c)) for c in comps]
    primes = [_prime_with_digits(rng, rng.choice(comp_digits)) for _ in range(n_primes)]
    items = primes + comps
    rng.shuffle(items)

    # Gold is recomputed from the items themselves — never carried over from construction.
    gold = sum(1 for x in items if is_prime(x))
    assert gold == n_primes, f"gold recomputation disagrees with construction ({gold} vs {n_primes})"

    listed = "\n".join(f"  ({i+1}) {x}" for i, x in enumerate(items))
    prompt = (
        "Consider the following five integers:\n"
        f"{listed}\n\n"
        "How many of them are prime numbers?\n"
        "Give your final answer on the last line in the form: ANSWER: <count>"
    )
    return {"domain": f"nearmiss_{level}", "level": level, "items": items,
            "prompt": prompt, "gold_int": gold}


def generate(level: str, n: int, seed: int = SEED_SEQUENCE[0]) -> list[dict]:
    """Balanced by construction over the answer range, ASSERTED before return."""
    if level not in ALL_LEVELS:
        raise ValueError(f"unknown level {level!r}; expected one of {ALL_LEVELS}")
    rng = random.Random(f"{seed}:{level}")
    cache = {"p2": [], "cm": []}
    rows = []
    for i in range(n):
        rows.append(_task(rng, level, ANSWER_RANGE[i % len(ANSWER_RANGE)], cache))

    counts = Counter(r["gold_int"] for r in rows)
    per = n // len(ANSWER_RANGE)
    for a in ANSWER_RANGE:
        if not (per <= counts[a] <= per + 1):
            raise AssertionError(f"unbalanced answer cell {a}: {counts[a]} (n={n})")

    # ENFORCE index-answer decorrelation rather than merely assert it. A shuffle makes the
    # correlation zero IN EXPECTATION, but at n=40 the null sd is ~0.16, so a fixed 0.20
    # tolerance fires on clean manifests about a fifth of the time — a guard mis-calibrated
    # against its own null (the same defect as per-pair tolerances hiding a bias). So: re-shuffle
    # deterministically until the realised |rho| is inside a 3-sigma envelope, then assert.
    tol = 3.0 / math.sqrt(len(rows)) if len(rows) >= 12 else 1.0
    for attempt in range(64):
        rng.shuffle(rows)
        if abs(_index_answer_rho(rows)) <= tol:
            break
    else:
        raise AssertionError("could not decorrelate uid index from answer in 64 shuffles")
    for i, r in enumerate(rows):
        r["uid"] = f"nm-{level}-{i:05d}"
    _assert_no_index_leak(rows, tol)
    _assert_no_magnitude_leak(rows)
    return rows


def _index_answer_rho(rows: list[dict]) -> float:
    n = len(rows)
    if n < 3:
        return 0.0
    idx = list(range(n))
    g = [r["gold_int"] for r in rows]
    mi, mg = (n - 1) / 2, sum(g) / n
    num = sum((i - mi) * (x - mg) for i, x in zip(idx, g))
    den = math.sqrt(sum((i - mi) ** 2 for i in idx) * sum((x - mg) ** 2 for x in g))
    return (num / den) if den else 0.0


def _assert_no_index_leak(rows: list[dict], tol: float = 0.20) -> None:
    """v1 shipped a 92.1% answer oracle in the uid index. Structurally excluded here.

    `tol` is 3-sigma against the shuffle null, supplied by the caller — a fixed constant would
    be either too tight at small n (false alarms) or too loose at large n (missed leaks).
    """
    n = len(rows)
    if n < 12:
        return
    if len(set(r["gold_int"] for r in rows[: n // 2])) < 2:
        raise AssertionError("uid index predicts the answer")
    rho = _index_answer_rho(rows)
    if abs(rho) > tol:
        raise AssertionError(f"uid index correlates with the answer (rho={rho:.3f}, tol={tol:.3f})")


def _assert_no_magnitude_leak(rows: list[dict]) -> None:
    """The best single "digit-length >= t => composite" rule must score at chance.

    Measured over every element of every task. If magnitude separated primes from composites,
    the family would score high accuracy for a reason that has nothing to do with recognition —
    and the axis measurement would be meaningless.
    """
    elems: list[tuple[int, bool]] = []
    for r in rows:
        for x in r["items"]:
            elems.append((len(str(x)), is_prime(x)))
    if len(elems) < 40:
        return
    n = len(elems)
    base = max(sum(1 for _, p in elems if p), sum(1 for _, p in elems if not p)) / n
    best = base
    for t in range(1, 25):
        for polarity in (True, False):
            hit = sum(1 for d, p in elems
                      if ((d >= t) == polarity) == (not p))
            best = max(best, hit / n)
    if best > base + 0.10:
        raise AssertionError(
            f"digit-length leaks primality: best threshold rule scores {best:.3f} "
            f"vs majority baseline {base:.3f}")


def manifest_sha256(rows: list[dict]) -> str:
    blob = "\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def generator_sha256() -> str:
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", default="A3", choices=LEVELS)
    ap.add_argument("--n", type=int, default=8)
    args = ap.parse_args()
    rows = generate(args.level, args.n)
    print(f"[task_gen_v3] level={args.level} n={len(rows)} "
          f"answers={dict(Counter(r['gold_int'] for r in rows))}")
    print(f"[task_gen_v3] generator_sha256={generator_sha256()}")
    print("\n--- sample ---")
    print(rows[0]["prompt"])
    print(f"[gold = {rows[0]['gold_int']}]  items={rows[0]['items']}")


if __name__ == "__main__":
    main()
