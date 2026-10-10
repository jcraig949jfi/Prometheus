"""MC-1: the generic search procedure for AR-1 -- a single neutral-acceptance MUTATION CHAIN over tapes.

Fixed before any pilot outcome (AR1_DESIGN.md s4):
  - start: the empty tape (charged 1 like every other candidate);
  - proposal: one mutation of the current tape, the operator drawn uniformly from those applicable:
      SUB  replace one token by a uniform token of the alphabet,
      INS  insert a uniform token at a uniform position (len < MAX_LEN),
      DEL  delete one token,
      DUP  copy a contiguous segment of length 1..3 to a uniform position (len stays <= MAX_LEN);
    the alphabet = the 23 base tokens + the macro tokens of the library given to the search (uniform over all);
    a proposal identical to the current tape is redrawn without a charge;
  - charge: 1 per candidate evaluated on dev (cache hits are charged too);
  - credit (dev only): sum over dev examples of 1 for an exact value-or-FAIL match, else (List outputs only)
    0.5 * (#positions i with out[i] == y[i]) / max(len out, len y, 1); no numeric-closeness credit (E2 O6);
  - acceptance: credit(candidate) >= credit(current) (neutral drift; the atlas chain_neutral rule);
  - HIT: the FIRST candidate that matches every dev example exactly -> the search returns it (no hindsight);
  - restart: after RESTART consecutive charges without a strict credit improvement, the current tape is reset to the
    empty tape (no charge);
  - RNG: random.Random keyed by sha256("AR1|MC1|<slot>|seed=<s>|lib=<library sha16>").
Evaluation of a candidate stops early once it can no longer reach the current credit (exact: the acceptance and the
hit decision are unchanged; a hit always has the maximum credit).
"""
import hashlib
import random
import time
from typing import Dict, List, Optional, Tuple

from alien import machine as M

MAX_LEN = 24
RESTART = 100_000
BUDGET = 1_000_000
CACHE_MAX = 300_000


def _score(v, y) -> float:
    if v == y and type(v) is type(y):
        return 1.0
    if type(v) is list and type(y) is list:
        n = max(len(v), len(y), 1)
        return 0.5 * sum(1 for p, q in zip(v, y) if p == q) / n
    return 0.0


def credit(fn, dev, floor: float = -1.0) -> Tuple[float, bool, bool]:
    """(credit or upper bound, exact on all dev, complete) for a compiled tape fn (xs -> value or FAIL). Stops when
    the credit can no longer reach `floor`."""
    tot = 0.0
    n = len(dev)
    exact = True
    for j, (xs, y) in enumerate(dev):
        s = _score(fn(xs), y)
        tot += s
        if s < 1.0:
            exact = False
            ub = tot + (n - j - 1)
            if ub < floor:
                return ub, False, False
    return tot, exact, True


def lib_sha(macros: Optional[Dict[str, Tuple[str, ...]]]) -> str:
    if not macros:
        return "-"
    s = "|".join("%s=%s" % (k, M.to_str(v)) for k, v in sorted(macros.items()))
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def rng_for(slot: str, seed: int, macros) -> random.Random:
    h = hashlib.sha256(("AR1|MC1|%s|seed=%d|lib=%s" % (slot, seed, lib_sha(macros))).encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def mutate(t: Tuple[str, ...], rng: random.Random, alphabet: List[str]) -> Tuple[str, ...]:
    n = len(t)
    ops = []
    if n:
        ops += ["SUB", "DEL"]
    if n < MAX_LEN:
        ops.append("INS")
    if n and n < MAX_LEN:
        ops.append("DUP")
    op = rng.choice(ops)
    if op == "SUB":
        i = rng.randrange(n)
        return t[:i] + (rng.choice(alphabet),) + t[i + 1:]
    if op == "DEL":
        i = rng.randrange(n)
        return t[:i] + t[i + 1:]
    if op == "INS":
        i = rng.randrange(n + 1)
        return t[:i] + (rng.choice(alphabet),) + t[i:]
    k = rng.randint(1, min(3, n, MAX_LEN - n))
    i = rng.randrange(n - k + 1)
    j = rng.randrange(n + 1)
    return t[:j] + t[i:i + k] + t[j:]


def chain(dev: List, out_type: str, slot: str, seed: int = 0, budget: int = BUDGET,
          macros: Optional[Dict[str, Tuple[str, ...]]] = None, trace_every: int = 0) -> Dict:
    """Run MC-1. Returns {hit, program, hit_charge, charges, best_credit, n_dev, restarts, cpu_s, ...}."""
    macros = dict(macros or {})
    alphabet = list(M.BASE) + sorted(macros)
    rng = rng_for(slot, seed, macros)
    cache: Dict[Tuple[str, ...], Tuple[float, bool, bool]] = {}
    t0 = time.process_time()

    def evaluate(t, floor):
        c = cache.get(t)
        if c is not None and (c[2] or c[0] < floor):
            return c
        c = credit(M.compile_closure(t, out_type, macros), dev, floor)
        if len(cache) >= CACHE_MAX:
            cache.clear()
        cache[t] = c
        return c

    n_dev = len(dev)
    cur: Tuple[str, ...] = ()
    charges = 1
    cc, ex, _ = evaluate(cur, -1.0)
    best = cc
    best_tape = cur
    since = 0
    restarts = 0
    redraws = 0
    trace = []
    if ex:
        return _res(True, cur, 1, 1, cc, n_dev, 0, t0, macros, trace, 0)
    while charges < budget:
        cand = mutate(cur, rng, alphabet)
        if cand == cur:
            redraws += 1
            continue
        charges += 1
        c, ex, _ = evaluate(cand, cc)
        if ex:
            return _res(True, cand, charges, charges, c, n_dev, restarts, t0, macros, trace, redraws)
        if c >= cc:
            if c > cc:
                since = 0
            cur, cc = cand, c
            if c > best:
                best, best_tape = c, cand
        since += 1
        if since >= RESTART:
            cur, since, restarts = (), 0, restarts + 1
            cc = evaluate(cur, -1.0)[0]
        if trace_every and charges % trace_every == 0:
            trace.append([charges, round(cc, 3), round(best, 3), len(cur)])
    r = _res(False, None, None, charges, best, n_dev, restarts, t0, macros, trace, redraws)
    r["best_tape"] = M.to_str(best_tape)
    return r


def _res(hit, tape, hit_charge, charges, best, n_dev, restarts, t0, macros, trace, redraws):
    return {"hit": hit, "program": M.to_str(tape) if tape is not None else None, "hit_charge": hit_charge,
            "charges": charges, "best_credit": round(best, 4), "n_dev": n_dev, "restarts": restarts,
            "redraws": redraws, "cpu_s": round(time.process_time() - t0, 2), "library_sha16": lib_sha(macros),
            "trace": trace}
