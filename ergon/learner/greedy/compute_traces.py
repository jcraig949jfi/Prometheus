"""Tier-1 computation-trace corpus (2026-06-08, v2 with hard negatives).

The 2026-06-07 kill showed the greedy LoRA learns surface classifiers, not
computation. The survey's prescription: shape completions as WORKED multi-step
derivations. This builder does that, in JUDGEMENT format (eval-compatible):

    prompt:     Claim: <op(args) = value>.  Work out any needed computation,
                then end with 'Answer: True' or 'Answer: False'.
    completion: <worked reason-first computation> Answer: True/False.

Two styles (--style) isolate the trace's value:
    trace   — completion contains the reason-first worked computation, verdict last.
    verdict — bare "Answer: True/False." (the no-work ablation).

HARD NEGATIVES (v2): the v1 false-value was correct±small, which leaked a
surface cue — φ(n)/σ(n) are even, so an odd stated value implies False with no
computation (caught in the v1 run: no-work scored 0.80 by parity-cheating). v2
draws each false value as the GENUINE output of the SAME operation on a NEARBY
input, so it has the same parity/magnitude/structure as a true value and cannot
be discriminated without actually computing. The trace always derives the REAL
value for the claimed input.

Gold is computed and INDEPENDENTLY re-checkable. Ops are disjoint from the
substrate corpus and from the held-out OOD domains (summation/inequality/
perfect_square).

Usage:
    python -m ergon.learner.greedy.compute_traces --style trace   --out .../compute_trace.jsonl
    python -m ergon.learner.greedy.compute_traces --style verdict --out .../compute_verdict.jsonl
    python -m ergon.learner.greedy.compute_traces --style trace --seed 999 --per-class 30 \
        --out .../compute_heldout.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Callable, List

import sympy

PROMPT_INSTRUCTION = ("Work out any needed computation, then end with "
                      "'Answer: True' or 'Answer: False'.")


def _jitter(rng, x, lo=1, hi=9, floor=2):
    return max(floor, x + rng.choice([-1, 1]) * rng.randint(lo, hi))


# ---------------------------------------------------------------------------
# Each op is an OpSpec: sample args, compute the value, render a worked trace,
# render the quantity phrase, format a value, and sample a NEARBY input (for a
# same-distribution hard-negative value). value/trace assert gold internally.
# ---------------------------------------------------------------------------

class OpSpec:
    name: str
    def sample(self, rng): ...
    def value(self, args): ...
    def trace(self, args) -> str: ...      # worked steps ending in the computed value
    def qty(self, args) -> str: ...
    def fmt(self, v) -> str: return str(v)
    def neighbor(self, rng, args): ...      # nearby args, for hard negatives


class GCD(OpSpec):
    name = "ct_gcd"
    def sample(self, rng): return (rng.randint(12, 9999), rng.randint(12, 9999))
    def value(self, args): return math.gcd(*args)
    def qty(self, args): return f"gcd({args[0]}, {args[1]})"
    def neighbor(self, rng, args): return (_jitter(rng, args[0]), _jitter(rng, args[1]))
    def trace(self, args):
        a, b = args; steps = []; x, y = a, b
        while y:
            q, r = divmod(x, y); steps.append(f"{x} = {q}·{y} + {r}"); x, y = y, r
        assert x == math.gcd(a, b)
        return "; ".join(steps) + f"; last nonzero remainder, so gcd = {x}"


class ModExp(OpSpec):
    name = "ct_modexp"
    def sample(self, rng): return (rng.randint(2, 50), rng.randint(5, 40), rng.randint(7, 1000))
    def value(self, args): return pow(*args)
    def qty(self, args): return f"{args[0]}^{args[1]} mod {args[2]}"
    def neighbor(self, rng, args):
        a, b, m = args; return (a, _jitter(rng, b, 1, 4), m)
    def trace(self, args):
        a, b, m = args; bits = bin(b)[2:]; res = 1; steps = [f"{b} = binary {bits}"]
        for bit in bits:
            res = (res * res) % m; s = f"square→{res}"
            if bit == "1": res = (res * a) % m; s += f", ×{a}→{res}"
            steps.append(s)
        assert res == pow(a, b, m)
        return f"square-and-multiply mod {m}: " + "; ".join(steps) + f", so the result is {res}"


class Phi(OpSpec):
    name = "ct_phi"
    def sample(self, rng): return (rng.randint(20, 5000),)
    def value(self, args): return int(sympy.totient(args[0]))
    def qty(self, args): return f"Euler's totient φ({args[0]})"
    def neighbor(self, rng, args): return (_jitter(rng, args[0], 1, 12, floor=3),)
    def trace(self, args):
        n = args[0]; f = sympy.factorint(n); val = 1; parts = []
        for p, e in f.items(): val *= (p**e - p**(e-1)); parts.append(f"({p}^{e}−{p}^{e-1})")
        assert val == int(sympy.totient(n))
        fac = "·".join(f"{p}^{e}" for p, e in f.items())
        return f"factor {n} = {fac}; φ = " + "·".join(parts) + f" = {val}"


class Sigma(OpSpec):
    name = "ct_sigma"
    def sample(self, rng): return (rng.randint(12, 3000),)
    def value(self, args): return int(sympy.divisor_sigma(args[0]))
    def qty(self, args): return f"sum of divisors σ({args[0]})"
    def neighbor(self, rng, args): return (_jitter(rng, args[0], 1, 12, floor=2),)
    def trace(self, args):
        n = args[0]; f = sympy.factorint(n); val = 1; parts = []
        for p, e in f.items():
            term = sum(p**i for i in range(e+1)); val *= term; parts.append(f"(1+…+{p}^{e})={term}")
        assert val == int(sympy.divisor_sigma(n))
        fac = "·".join(f"{p}^{e}" for p, e in f.items())
        return f"factor {n} = {fac}; σ = " + "·".join(parts) + f" = {val}"


class DivCount(OpSpec):
    name = "ct_divisor_count"
    def sample(self, rng): return (rng.randint(12, 5000),)
    def value(self, args): return int(sympy.divisor_count(args[0]))
    def qty(self, args): return f"number of divisors d({args[0]})"
    def neighbor(self, rng, args): return (_jitter(rng, args[0], 1, 12, floor=2),)
    def trace(self, args):
        n = args[0]; f = sympy.factorint(n); val = 1; parts = []
        for p, e in f.items(): val *= (e + 1); parts.append(f"({e}+1)")
        assert val == int(sympy.divisor_count(n))
        fac = "·".join(f"{p}^{e}" for p, e in f.items())
        return f"factor {n} = {fac}; d = " + "·".join(parts) + f" = {val}"


class Binomial(OpSpec):
    name = "ct_binomial"
    def sample(self, rng):
        n = rng.randint(6, 30); return (n, rng.randint(2, n-1))
    def value(self, args): return math.comb(*args)
    def qty(self, args): return f"the binomial coefficient C({args[0]}, {args[1]})"
    def neighbor(self, rng, args):
        n, k = args; nk = max(2, min(n-1, _jitter(rng, k, 1, 3, floor=1))); return (n, nk)
    def trace(self, args):
        n, k = args; res = 1; steps = []
        for i in range(1, k+1): res = res * (n - i + 1) // i; steps.append(f"×{n-i+1}/{i}→{res}")
        assert res == math.comb(n, k)
        return f"C({n},{k}) by running product: 1 " + " ".join(steps) + f", so the value is {res}"


class CRT(OpSpec):
    name = "ct_crt"
    def sample(self, rng):
        while True:
            m1 = rng.choice([3, 4, 5, 7, 8, 9, 11]); m2 = rng.choice([13, 16, 17, 19, 23, 25])
            if math.gcd(m1, m2) == 1: break
        return (m1, m2, rng.randint(0, m1-1), rng.randint(0, m2-1))
    def value(self, args):
        m1, m2, a1, a2 = args
        return next(t for t in range(m1*m2) if t % m1 == a1 and t % m2 == a2)
    def qty(self, args):
        m1, m2, a1, a2 = args
        return f"the unique x in [0, {m1*m2}) with x≡{a1} (mod {m1}) and x≡{a2} (mod {m2})"
    def neighbor(self, rng, args):
        m1, m2, a1, a2 = args
        return (m1, m2, rng.randrange(m1), rng.randrange(m2))
    def trace(self, args):
        m1, m2, a1, a2 = args; x = self.value(args)
        return (f"list x≡{a1} (mod {m1}): {a1}, {a1+m1}, {a1+2*m1}, …; "
                f"the first that is ≡{a2} (mod {m2}) is x = {x}")


class ContFrac(OpSpec):
    name = "ct_continued_fraction"
    def sample(self, rng):
        q = rng.randint(3, 60); return (rng.randint(q+1, 200), q)
    def value(self, args):
        p, q = args; cf = []; x, y = p, q
        while y: a = x // y; cf.append(a); x, y = y, x - a*y
        return cf
    def qty(self, args): return f"the continued fraction expansion of {args[0]}/{args[1]}"
    def fmt(self, v): return "[" + ", ".join(map(str, v)) + "]"
    def neighbor(self, rng, args):
        p, q = args; return (_jitter(rng, p, 1, 7, floor=q+1), q)
    def trace(self, args):
        p, q = args; steps = []; x, y = p, q; cf = []
        while y:
            a = x // y; steps.append(f"{x}/{y}: floor={a}"); cf.append(a); x, y = y, x - a*y
        import prometheus_math.number_theory as nt
        assert cf == list(nt.cf_expand(p, q))
        return f"Euclidean CF of {p}/{q}: " + "; ".join(steps) + f" → {self.fmt(cf)}"


OPS: List[OpSpec] = [GCD(), ModExp(), Phi(), Sigma(), DivCount(), Binomial(), CRT(), ContFrac()]


def gen_example(op: OpSpec, rng, make_true: bool):
    args = op.sample(rng)
    true_v = op.value(args)
    if make_true:
        stated = true_v
    else:
        # hard negative: value of the same op on a nearby input, != true value
        for _ in range(50):
            na = op.neighbor(rng, args)
            wv = op.value(na)
            if wv != true_v:
                stated = wv; break
        else:
            return None  # degenerate (couldn't find a distinct neighbor); filtered
    if op.name == "ct_continued_fraction":
        claim = f"{op.qty(args)} is {op.fmt(stated)}."
    else:
        claim = f"{op.qty(args)} = {op.fmt(stated)}."
    body = op.trace(args)
    return {"claim": claim, "gold": make_true, "body": body,
            "stated": op.fmt(stated), "correct": op.fmt(true_v), "source": op.name}


def build(rng, per_class: int):
    rows = []; idx = 0
    for op in OPS:
        for mt in (True, False):
            made = 0
            while made < per_class:
                r = gen_example(op, rng, mt)
                if r is None:
                    continue
                r["idx"] = idx; idx += 1; rows.append(r); made += 1
    rng.shuffle(rows)
    return rows


def to_example(r, style: str) -> dict:
    label = "True" if r["gold"] else "False"
    prompt = f"Claim: {r['claim']}\n{PROMPT_INSTRUCTION}"
    if style == "trace":
        if r["gold"]:
            completion = f"{r['body']}, which matches the claim. Answer: True."
        else:
            completion = f"{r['body']}, but the claim states {r['stated']}. Answer: False."
    else:
        completion = f"Answer: {label}."
    return {"prompt": prompt, "completion": completion, "gold_bool": r["gold"],
            "source": r["source"], "domain": r["source"], "tier": 1,
            "uid": f"{style}-{r['source']}-{r['idx']}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="F:/Prometheus/ergon/learner/greedy/corpus/compute_trace.jsonl")
    ap.add_argument("--style", choices=["trace", "verdict"], default="trace")
    ap.add_argument("--per-class", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260608)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    rows = build(rng, args.per_class)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(to_example(r, args.style), ensure_ascii=False) + "\n")

    from collections import Counter
    n_true = sum(r["gold"] for r in rows)
    print(f"[compute_traces v2] style={args.style} wrote {len(rows)} rows -> {out}")
    print(f"[compute_traces v2] true={n_true} false={len(rows)-n_true}  by_op={dict(Counter(r['source'] for r in rows))}")
    ex = to_example(rows[0], args.style)
    print("SAMPLE P:", ex['prompt'].split(chr(10))[0])
    print("SAMPLE C:", ex['completion'][:200])


if __name__ == "__main__":
    main()
