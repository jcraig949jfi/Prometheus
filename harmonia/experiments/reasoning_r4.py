"""R4 — representation-shift probes (Canon build-debt #1, filled 2026-08-18 by Aporia).

Canon rung semantics (aporia/doctrine/reasoning_ladder.md): operation = representation
shift; kill test = the problem is hard in its given surface form and easy after
re-encoding; artifact = the shift itself.

Grading is fully deterministic (Doctrine #1) and, per Doctrine #2, failure emits a
SIGNATURE: for every probe we precompute `surface_answer` — the well-defined wrong
answer a solver gets by staying in the surface representation — so "did not shift"
is a detectable kill_pattern (`stayed_in_surface`), not an anonymous miss.

Three families, each in the phase0 4-version design (clean/iso/adversarial/transfer):

  R4a  positional re-encoding    — arithmetic on non-decimal digit strings; surface
                                    trap = reading digits as decimal.
  R4b  recurrence -> closed form — a(200)-scale terms; surface trap = short manual
                                    iteration (we precompute the k-step truncation).
  R4c  counting via complement   — "at least one '11' in length-n strings"; surface
                                    trap = the wrong complement (no Fibonacci shift).

Standalone module: imports Probe from reasoning_phase0 but modifies nothing there —
wiring into the suite is Harmonia A's call (consumer named in the commit).
Self-test: python harmonia/experiments/reasoning_r4.py
"""
from __future__ import annotations
import pathlib
import random
import sys
from functools import lru_cache

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from reasoning_phase0 import Probe  # noqa: E402

N_PER = 5


# ---------- R4a: positional re-encoding ----------

def _to_base(n: int, b: int) -> str:
    if n == 0:
        return "0"
    digits = []
    while n:
        digits.append(str(n % b))
        n //= b
    return "".join(reversed(digits))


def gen_R4a(rng: random.Random):
    out = []
    for _ in range(N_PER):
        b = rng.choice([5, 6, 7, 8])
        m, n = rng.randint(30, 200), rng.randint(30, 200)
        sm, sn = _to_base(m, b), _to_base(n, b)
        truth = _to_base(m + n, b)
        surface = _to_base(int(sm) + int(sn), b)
        out.append(Probe("R4", "clean", "rebase",
                         {"prompt": f"In base {b}: {sm} + {sn} = ? (answer in base {b})",
                          "base": b, "surface_answer": surface}, truth))
        b2 = rng.choice([x for x in (5, 6, 7, 8, 9) if x != b])
        m2, n2 = rng.randint(30, 200), rng.randint(30, 200)
        s2, t2 = _to_base(m2, b2), _to_base(n2, b2)
        out.append(Probe("R4", "iso", "rebase",
                         {"prompt": f"In base {b2}: {s2} + {t2} = ? (answer in base {b2})",
                          "base": b2, "surface_answer": _to_base(int(s2) + int(t2), b2)},
                         _to_base(m2 + n2, b2)))
        # adversarial: all digits < 5 so the strings look decimal-plausible
        m3 = int("".join(rng.choice("1234") for _ in range(3)), 5)
        n3 = int("".join(rng.choice("1234") for _ in range(3)), 5)
        s3, t3 = _to_base(m3, 5), _to_base(n3, 5)
        out.append(Probe("R4", "adversarial", "rebase",
                         {"prompt": f"Working entirely in base 5, compute {s3} + {t3}.",
                          "base": 5, "surface_answer": _to_base(int(s3) + int(t3), 5)},
                         _to_base(m3 + n3, 5)))
        m4, n4 = rng.randint(6, 30), rng.randint(6, 30)
        b4 = rng.choice([6, 7, 8])
        out.append(Probe("R4", "transfer", "rebase",
                         {"prompt": f"In base {b4}: {_to_base(m4, b4)} * {_to_base(n4, b4)} = ? (answer in base {b4})",
                          "base": b4, "surface_answer": None}, _to_base(m4 * n4, b4)))
    return out


# ---------- R4b: recurrence -> closed form ----------

def gen_R4b(rng: random.Random):
    out = []
    for _ in range(N_PER):
        # a(n) = 2 a(n-1) + c, a(0)=a0  ->  a(n) = (a0 + c) 2^n - c
        c, a0 = rng.randint(1, 5), rng.randint(0, 3)
        big = rng.randint(120, 220)
        k = rng.randint(6, 9)  # surface trap: iterate only k steps
        out.append(Probe("R4", "clean", "recurrence",
                         {"prompt": f"a(0)={a0}, a(n)=2*a(n-1)+{c}. Give a({big}) exactly.",
                          "surface_answer": str((a0 + c) * (2 ** k) - c), "n": big},
                         str((a0 + c) * (2 ** big) - c)))
        c2, a02, big2 = rng.randint(1, 5), rng.randint(0, 3), rng.randint(120, 220)
        k2 = rng.randint(6, 9)
        out.append(Probe("R4", "iso", "recurrence",
                         {"prompt": f"b(0)={a02}, b(n)=2*b(n-1)+{c2}. Give b({big2}) exactly.",
                          "surface_answer": str((a02 + c2) * (2 ** k2) - c2), "n": big2},
                         str((a02 + c2) * (2 ** big2) - c2)))
        # adversarial: tempting off-by-one closed form. c(n)=c(n-1)+n -> a0 + n(n+1)/2;
        # the slip is n(n-1)/2.
        a03, big3 = rng.randint(1, 6), rng.randint(150, 400)
        out.append(Probe("R4", "adversarial", "recurrence",
                         {"prompt": f"c(0)={a03}, c(n)=c(n-1)+n. Give c({big3}) exactly.",
                          "surface_answer": str(a03 + big3 * (big3 - 1) // 2), "n": big3},
                         str(a03 + big3 * (big3 + 1) // 2)))
        a04, big4 = rng.randint(1, 4), rng.randint(60, 120)
        out.append(Probe("R4", "transfer", "recurrence",
                         {"prompt": f"d(0)={a04}, d(n)=3*d(n-1). Give d({big4}) exactly.",
                          "surface_answer": None, "n": big4}, str(a04 * 3 ** big4)))
    return out


# ---------- R4c: counting via complement / bijection ----------

@lru_cache(maxsize=None)
def _fib(n: int) -> int:
    return n if n < 2 else _fib(n - 1) + _fib(n - 2)


def _no_11(n: int) -> int:
    """Number of length-n binary strings with no '11' = F(n+2)."""
    return _fib(n + 2)


def gen_R4c(rng: random.Random):
    out = []
    for _ in range(N_PER):
        n = rng.randint(18, 30)
        out.append(Probe("R4", "clean", "complement",
                         {"prompt": f"How many binary strings of length {n} contain at least one '11'?",
                          "surface_answer": str(2 ** n - _no_11(n - 1)), "n": n},
                         str(2 ** n - _no_11(n))))
        n2 = rng.randint(18, 30)
        out.append(Probe("R4", "iso", "complement",
                         {"prompt": f"How many length-{n2} sequences of H/T contain 'HH' somewhere?",
                          "surface_answer": str(2 ** n2 - _no_11(n2 - 1)), "n": n2},
                         str(2 ** n2 - _no_11(n2))))
        # adversarial: single-complement is WRONG; needs inclusion-exclusion.
        # #(has 11 AND has 00) = 2^n - 2*F(n+2) + 2  (alternating strings counted back in)
        n3 = rng.randint(14, 22)
        no11 = _no_11(n3)
        out.append(Probe("R4", "adversarial", "complement",
                         {"prompt": f"How many binary strings of length {n3} contain at least one '11' AND at least one '00'?",
                          "surface_answer": str(2 ** n3 - no11), "n": n3},
                         str(2 ** n3 - 2 * no11 + 2)))
        # transfer: ternary, no-adjacent-equal = 3*2^(n-1); ask the complement
        n4 = rng.randint(12, 20)
        out.append(Probe("R4", "transfer", "complement",
                         {"prompt": f"How many length-{n4} strings over the alphabet a,b,c have at least one pair of adjacent equal symbols?",
                          "surface_answer": None, "n": n4},
                         str(3 ** n4 - 3 * 2 ** (n4 - 1))))
    return out


# ---------- deterministic grader ----------

def grade_r4(probe: Probe, answer: str) -> dict:
    """{correct, kill_pattern}. stayed_in_surface = matches the precomputed no-shift trap."""
    a = str(answer).strip().lower().replace(",", "").replace(" ", "")
    truth = str(probe.ground_truth).strip().lower()
    if a == truth:
        return {"correct": True, "kill_pattern": None}
    surf = probe.data.get("surface_answer")
    if surf is not None and a == str(surf).strip().lower():
        return {"correct": False, "kill_pattern": "stayed_in_surface"}
    return {"correct": False, "kill_pattern": "wrong_other"}


def generate_all(seed: int = 0):
    rng = random.Random(seed)
    return gen_R4a(rng) + gen_R4b(rng) + gen_R4c(rng)


if __name__ == "__main__":
    probes = generate_all(7)
    n_adv = sum(1 for p in probes if p.version == "adversarial")
    bad = [p for p in probes
           if p.data.get("surface_answer") is not None
           and str(p.data["surface_answer"]) == str(p.ground_truth)]
    assert not bad, f"trap == truth in {len(bad)} probes (undetectable signature)"

    def brute_11(n):
        return sum(1 for i in range(2 ** n) if "11" in format(i, f"0{n}b"))

    for n in (6, 10, 14):
        assert brute_11(n) == 2 ** n - _no_11(n), f"R4c formula wrong at n={n}"

    def brute_both(n):
        return sum(1 for i in range(2 ** n)
                   if "11" in format(i, f"0{n}b") and "00" in format(i, f"0{n}b"))

    for n in (6, 10, 12):
        assert brute_both(n) == 2 ** n - 2 * _no_11(n) + 2, f"inclusion-exclusion wrong at n={n}"

    def brute_ternary(n):
        from itertools import product
        return sum(1 for s in product("abc", repeat=n)
                   if any(s[i] == s[i + 1] for i in range(n - 1)))

    for n in (5, 8):
        assert brute_ternary(n) == 3 ** n - 3 * 2 ** (n - 1), f"ternary transfer wrong at n={n}"

    p = probes[0]
    assert grade_r4(p, str(p.ground_truth))["correct"]
    if p.data.get("surface_answer"):
        assert grade_r4(p, p.data["surface_answer"])["kill_pattern"] == "stayed_in_surface"
    print(f"R4 self-test OK: {len(probes)} probes ({n_adv} adversarial), "
          f"all traps distinct from truth, R4c + inclusion-exclusion + ternary "
          f"verified by brute force, grader emits stayed_in_surface signature")
