#!/usr/bin/env python3
"""Claim templates: statement, derivation, and the TRUTH oracle.

Second of the two independent oracles. `truth_oracle()` on each template decides
the proposition by direct native-Python enumeration over the stated domain. It
never evaluates a derivation step, never imports `derivation.py`, and never sees
the expression strings the step checks use. The duplication between a template's
native closed form and the string form used in its steps is deliberate: it is
what keeps the truth channel and the argument channel from collapsing into one.

Where a claim is exhaustively checkable over a small finite domain, the two
channels necessarily agree — two correct implementations of the same finite
enumeration will. Independence here means independent *implementation*, not
guaranteed disagreement. The class where the channels genuinely diverge is
TRUE_BUT_INVALID_ARGUMENT, and that divergence is asserted in `pilot.py`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Callable

TRUE_VALID = "TRUE_VALID_ARGUMENT"
FALSE_WITNESS = "FALSE_WITH_WITNESS"
TRUE_INVALID = "TRUE_BUT_INVALID_ARGUMENT"
FALSE_HARD = "FALSE_BUT_HARD_WITHIN_BUDGET"
UNRESOLVED = "UNRESOLVED_WITHIN_BUDGET"

ALL_CLASSES = [TRUE_VALID, FALSE_WITNESS, TRUE_INVALID, FALSE_HARD, UNRESOLVED]

EASY_WITNESS_MAX = 5000


@dataclass
class Item:
    template_id: str
    domain_label: str
    params: dict
    proposition: str
    domain_text: str
    quantifiers: str
    hypotheses: list[str]
    steps: list[dict]
    truth: bool
    truth_method: str
    witness: Any = None
    proof_sketch: str | None = None
    min_disposition: dict = field(default_factory=dict)
    difficulty: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def step(sid: str, tag: str, text: str, check: dict, depends_on=()) -> dict:
    return {"id": sid, "tag": tag, "text": text, "check": check,
            "depends_on": list(depends_on)}


def _assemble(rng: random.Random, base: list[dict], engine: list[dict],
              aux: list[dict], conclusion: list[dict]) -> list[dict]:
    """Order steps, shuffling the auxiliary block so position is not a tell."""
    keep = [a for a in aux if rng.random() < 0.75]
    rng.shuffle(keep)
    ordered = base + engine + keep + conclusion
    for i, s in enumerate(ordered, start=1):
        s["id"] = f"s{i}"
    for i, s in enumerate(ordered):
        s["depends_on"] = [ordered[j]["id"] for j in range(i)][-2:]
    engine_id = next((s["id"] for s in ordered if s.get("tag") == "engine"), None)
    for s in ordered:
        if s["check"]["kind"] == "generalization" and s["check"].get("justified"):
            s["check"]["justified_by"] = engine_id
    return ordered


# --------------------------------------------------------------------------
# generic auxiliary steps (pure arithmetic in n; reusable across templates)
# --------------------------------------------------------------------------

def generic_aux(lo: int, hi: int) -> list[dict]:
    hi = max(hi, lo + 3)
    return [
        step("", "aux_inequality",
             f"For every integer n with 2 <= n <= {hi} we have n^2 >= 2n.",
             {"kind": "forall_inequality", "var": "n", "lo": 2, "hi": hi,
              "lhs": "n**2", "rhs": "2*n", "op": ">="}),
        step("", "aux_exists",
             f"There exists an integer n in [{lo}, {hi}] with n^2 > {hi}.",
             {"kind": "exists_pred", "var": "n", "lo": lo, "hi": hi,
              "pred": f"n**2 > {hi}"}),
        step("", "aux_cases",
             f"Every integer n in [{lo}, {hi}] is even or odd, so the two cases "
             "below are exhaustive.",
             {"kind": "case_cover", "var": "n", "lo": lo, "hi": hi,
              "cases": ["n % 2 == 0", "n % 2 == 1"]}),
        step("", "aux_congruence",
             f"For every integer n with {lo} <= n <= {hi}, n^3 is congruent to n "
             "modulo 6.",
             {"kind": "congruence", "var": "n", "lo": lo, "hi": hi,
              "lhs": "n**3", "rhs": "n", "modulus": 6}),
        step("", "aux_implication",
             f"For every integer n with {lo} <= n <= {hi}: if n is divisible by 4 "
             "then n(n+1)/2 is even.",
             {"kind": "forall_implication", "var": "n", "lo": max(lo, 1), "hi": hi,
              "ante": "n % 4 == 0", "cons": "(n*(n+1)//2) % 2 == 0"}),
        step("", "cancellable",
             f"Put H(n) = n^2 + [n = 3]. Then (n-3)n^2 = (n-3)H(n) for every n in "
             f"[{max(lo,1)}, {hi}].",
             {"kind": "forall_identity", "var": "n", "lo": max(lo, 1), "hi": hi,
              "lhs": "(n-3)*(n**2)",
              "rhs": "(n-3)*((n**2) + (1 if n == 3 else 0))"}),
        step("", "worked_value",
             "The identity n^3 - n = 120 is verified directly at n = 5.",
             {"kind": "instantiation", "var": "n", "lo": max(lo, 1), "hi": hi,
              "point": 5, "pred": "n**3 - n == 120"}),
    ]


# ==========================================================================
# T1 - integer sum identities
# ==========================================================================

_SUM_FORMS = {
    1: ("n(n+1)/2", "n*(n+1)//2", lambda n: n * (n + 1) // 2),
    2: ("n(n+1)(2n+1)/6", "n*(n+1)*(2*n+1)//6",
        lambda n: n * (n + 1) * (2 * n + 1) // 6),
    3: ("(n(n+1)/2)^2", "(n*(n+1)//2)**2", lambda n: (n * (n + 1) // 2) ** 2),
}


def build_t1(rng: random.Random, target: str) -> Item | None:
    if target not in (TRUE_VALID, TRUE_INVALID, FALSE_WITNESS):
        return None
    p = rng.choice([1, 2, 3])
    N = rng.choice([30, 40, 50, 60])
    pretty, expr, f = _SUM_FORMS[p]

    if target == FALSE_WITNESS:
        w = rng.randint(4, min(N - 2, 25))
        expr_c = f"({expr}) + (n//{w})"
        f_c = (lambda n, _f=f, _w=w: _f(n) + n // _w)
        pretty_c = f"{pretty} + floor(n/{w})"
    else:
        expr_c, f_c, pretty_c = expr, f, pretty

    # truth oracle: native enumeration, no expression strings
    truth, witness = True, None
    for n in range(1, N + 1):
        if sum(k ** p for k in range(1, n + 1)) != f_c(n):
            truth, witness = False, {"n": n}
            break

    base = [step("", "base",
                 f"The identity holds at n = 1: the left side is 1 and the right "
                 f"side evaluates to {f_c(1)}.",
                 {"kind": "instantiation", "var": "n", "lo": 1, "hi": N, "point": 1,
                  "pred": f"sum_k(n,{p}) == 1"})]
    engine = [step("", "engine",
                   f"Write F(n) = {pretty_c}. For every n with 1 <= n <= {N-1}, "
                   f"F(n+1) - F(n) = (n+1)^{p}, which is exactly the term added "
                   "when the upper limit increases by one.",
                   {"kind": "forall_identity", "var": "n", "lo": 1, "hi": N - 1,
                    "lhs": f"({expr_c.replace('n', '(n+1)')}) - ({expr_c})",
                    "rhs": f"(n+1)**{p}"})]
    aux = generic_aux(1, N)
    if target != FALSE_WITNESS:
        # cancellable step: valid as stated, invalid once (n-3) is divided out
        aux.append(step("", "cancellable",
                        f"Let G(n) = F(n) + [n = 3]. Then (n-3)F(n) = (n-3)G(n) "
                        f"for every n in [1, {N}].",
                        {"kind": "forall_identity", "var": "n", "lo": 1, "hi": N,
                         "lhs": f"(n-3)*({expr_c})",
                         "rhs": f"(n-3)*(({expr_c}) + (1 if n == 3 else 0))"}))
    conclusion = [step("", "conclusion",
                       f"Base case and increment together establish the identity "
                       f"for every n in [1, {N}].",
                       {"kind": "generalization", "established_hi": N,
                        "asserted_hi": N, "justified": True})]

    steps = _assemble(rng, base, engine, aux, conclusion)
    return Item(
        template_id="t1_integer_sum_identity",
        domain_label="integer_identities",
        params={"p": p, "N": N, "formula": pretty_c, "formula_expr": expr_c},
        proposition=f"For every integer n with 1 <= n <= {N}, "
                    f"the sum of k^{p} for k = 1..n equals {pretty_c}.",
        domain_text=f"integers n with 1 <= n <= {N}",
        quantifiers=f"for all n in [1, {N}]",
        hypotheses=["n ranges over integers only", "the sum is empty for n = 0"],
        steps=steps, truth=truth,
        truth_method="native exhaustive enumeration over [1, N]",
        witness=witness,
        proof_sketch=None if not truth else
        f"Base case at n=1 plus the increment identity F(n+1)-F(n)=(n+1)^{p}.",
        min_disposition={"kind": "witness_search" if not truth else "closed_form_proof",
                         "cost_units": witness["n"] if witness else len(steps)},
        difficulty={"domain_size": N, "derivation_length": len(steps)},
    )


# ==========================================================================
# T2 - modular power cycles
# ==========================================================================

def build_t2(rng: random.Random, target: str) -> Item | None:
    if target not in (TRUE_VALID, TRUE_INVALID, FALSE_WITNESS):
        return None
    m = rng.choice([7, 11, 13, 17, 19, 23])
    a = rng.choice([x for x in range(2, m) if math.gcd(x, m) == 1])
    d = 1
    x = a % m
    while x != 1:
        x = (x * a) % m
        d += 1
    N = rng.choice([40, 60, 80])
    d_c = d + rng.choice([1, 2]) if target == FALSE_WITNESS else d

    truth, witness = True, None
    for n in range(0, N + 1):
        if pow(a, n, m) != pow(a, n % d_c, m):
            truth, witness = False, {"n": n}
            break

    base = [step("", "base",
                 f"At n = 0 both sides equal 1 modulo {m}.",
                 {"kind": "instantiation", "var": "n", "lo": 0, "hi": N, "point": 0,
                  "pred": f"pow({a}, n, {m}) == 1"})]
    engine = [step("", "engine",
                   f"The residue {a} has order {d_c} modulo {m}: for every n in "
                   f"[0, {N - d_c}], {a}^(n+{d_c}) is congruent to {a}^n modulo {m}.",
                   {"kind": "congruence", "var": "n", "lo": 0, "hi": N - d_c,
                    "lhs": f"pow({a}, n+{d_c}, {m})", "rhs": f"pow({a}, n, {m})",
                    "modulus": m})]
    aux = generic_aux(1, N) + [
        step("", "aux_cases",
             f"Every n in [0, {N}] falls in exactly one residue class modulo "
             f"{d_c}.",
             {"kind": "case_cover", "var": "n", "lo": 0, "hi": N,
              "cases": [f"n % {d_c} == {r}" for r in range(d_c)]}),
        step("", "aux_implication",
             f"For every n in [0, {N}]: if {d_c} divides n then {a}^n is congruent "
             f"to 1 modulo {m}.",
             {"kind": "forall_implication", "var": "n", "lo": 0, "hi": N,
              "ante": f"n % {d_c} == 0", "cons": f"pow({a}, n, {m}) == 1"}),
    ]
    conclusion = [step("", "conclusion",
                       f"Periodicity plus the base case gives the statement for "
                       f"every n in [0, {N}].",
                       {"kind": "generalization", "established_hi": N,
                        "asserted_hi": N, "justified": True})]

    steps = _assemble(rng, base, engine, aux, conclusion)
    return Item(
        template_id="t2_modular_power_cycle",
        domain_label="modular_arithmetic",
        params={"a": a, "m": m, "d_claimed": d_c, "d_true": d, "N": N},
        proposition=f"For every integer n with 0 <= n <= {N}, "
                    f"{a}^n is congruent to {a}^(n mod {d_c}) modulo {m}.",
        domain_text=f"integers n with 0 <= n <= {N}",
        quantifiers=f"for all n in [0, {N}]",
        hypotheses=[f"gcd({a}, {m}) = 1", "exponents are non-negative"],
        steps=steps, truth=truth,
        truth_method="native enumeration with pow(a, n, m) over [0, N]",
        witness=witness,
        proof_sketch=None if not truth else
        f"{a} has multiplicative order {d} modulo {m}.",
        min_disposition={"kind": "witness_search" if not truth else "closed_form_proof",
                         "cost_units": witness["n"] + 1 if witness else len(steps)},
        difficulty={"domain_size": N + 1, "derivation_length": len(steps)},
    )


# ==========================================================================
# T3 - minimum degree forces connectivity (small graphs)
# ==========================================================================

def _min_component_size(g: int, v: int) -> int:
    adj = [0] * v
    idx = 0
    for i in range(v):
        for j in range(i + 1, v):
            if g >> idx & 1:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    unseen = (1 << v) - 1
    best = v
    while unseen:
        start = (unseen & -unseen).bit_length() - 1
        comp, stack = 1 << start, [start]
        while stack:
            u = stack.pop()
            nxt = adj[u] & ~comp
            while nxt:
                w = (nxt & -nxt).bit_length() - 1
                comp |= 1 << w
                stack.append(w)
                nxt &= nxt - 1
        best = min(best, bin(comp).count("1"))
        unseen &= ~comp
    return best


def _connected(g: int, v: int) -> bool:
    return _min_component_size(g, v) == v


def _degrees(g: int, v: int) -> list[int]:
    deg = [0] * v
    idx = 0
    for i in range(v):
        for j in range(i + 1, v):
            if g >> idx & 1:
                deg[i] += 1
                deg[j] += 1
            idx += 1
    return deg


def build_t3(rng: random.Random, target: str) -> Item | None:
    if target not in (TRUE_VALID, TRUE_INVALID, FALSE_HARD):
        return None
    if target == FALSE_HARD:
        v, d = 6, 2
    else:
        v, d = rng.choice([(5, 2), (6, 3), (5, 3), (6, 4)])
    E = v * (v - 1) // 2
    total = 1 << E

    truth, witness = True, None
    for g in range(total):
        if min(_degrees(g, v)) >= d and not _connected(g, v):
            truth, witness = False, {"graph_bits": g, "v": v,
                                     "degrees": _degrees(g, v)}
            break

    base = [step("", "base",
                 f"At least one graph on {v} vertices has minimum degree at least "
                 f"{d}, so the statement is not vacuous.",
                 {"kind": "exists_pred", "var": "g", "lo": 0, "hi": total - 1,
                  "pred": f"min(graph_degrees(g, {v})) >= {d}"})]
    engine = [step("", "engine",
                   f"If every vertex has degree at least {d} then every connected "
                   f"component contains at least {d + 1} vertices.",
                   {"kind": "forall_implication", "var": "g", "lo": 0,
                    "hi": total - 1,
                    "ante": f"min(graph_degrees(g, {v})) >= {d}",
                    "cons": f"graph_min_component_size(g, {v}) >= {d + 1}"}),
              step("", "engine2",
                   f"A graph on {v} vertices in which every component has at least "
                   f"{d + 1} vertices is connected.",
                   {"kind": "forall_implication", "var": "g", "lo": 0,
                    "hi": total - 1,
                    "ante": f"graph_min_component_size(g, {v}) >= {d + 1}",
                    "cons": f"graph_is_connected(g, {v}) == 1"})]
    aux = [
        step("", "aux_inequality",
             f"Every graph on {v} vertices with minimum degree at least {d} has at "
             f"least {math.ceil(v * d / 2)} edges.",
             {"kind": "forall_implication", "var": "g", "lo": 0, "hi": total - 1,
              "ante": f"min(graph_degrees(g, {v})) >= {d}",
              "cons": f"graph_edge_count(g, {v}) >= {math.ceil(v * d / 2)}"}),
        step("", "aux_cases",
             f"Every graph on {v} vertices either has minimum degree at least {d} "
             "or it does not.",
             {"kind": "case_cover", "var": "g", "lo": 0, "hi": total - 1,
              "cases": [f"min(graph_degrees(g, {v})) >= {d}",
                        f"min(graph_degrees(g, {v})) < {d}"]}),
        step("", "aux_congruence",
             f"Handshake lemma: in every graph on {v} vertices the sum of the "
             "degrees is even.",
             {"kind": "congruence", "var": "g", "lo": 0, "hi": total - 1,
              "lhs": f"sum(graph_degrees(g, {v}))", "rhs": "0", "modulus": 2}),
        step("", "worked_value",
             "The graph at index 1 of the enumeration has exactly one edge; it is "
             "checked directly.",
             {"kind": "instantiation", "var": "g", "lo": 0, "hi": total - 1,
              "point": 1, "pred": f"graph_edge_count(g, {v}) == 1"}),
    ]
    conclusion = [step("", "conclusion",
                       f"Combining the two implications gives the statement for "
                       f"all {total} labelled graphs on {v} vertices.",
                       {"kind": "generalization", "established_hi": total - 1,
                        "asserted_hi": total - 1, "justified": True})]

    steps = _assemble(rng, base, engine, aux, conclusion)
    return Item(
        template_id="t3_min_degree_connectivity",
        domain_label="finite_combinatorics",
        params={"v": v, "d": d},
        proposition=f"Every labelled graph on {v} vertices in which every vertex "
                    f"has degree at least {d} is connected.",
        domain_text=f"all {total} labelled graphs on {v} vertices",
        quantifiers=f"for all graphs G on exactly {v} labelled vertices",
        hypotheses=["graphs are simple and undirected",
                    "vertices are labelled 0..v-1"],
        steps=steps, truth=truth,
        truth_method="native exhaustive enumeration of all 2^E labelled graphs",
        witness=witness,
        proof_sketch=None if not truth else
        f"min degree >= {d} forces components of size >= {d+1}; two such "
        f"components would need more than {v} vertices.",
        min_disposition={"kind": "exhaustive" if truth else "witness_search",
                         "cost_units": total if truth else witness["graph_bits"] + 1},
        difficulty={"domain_size": total, "derivation_length": len(steps)},
    )


# ==========================================================================
# T4 - linear recurrence closed form
# ==========================================================================

def build_t4(rng: random.Random, target: str) -> Item | None:
    if target not in (TRUE_VALID, TRUE_INVALID, FALSE_WITNESS):
        return None
    r, s = sorted(rng.sample([2, 3, 4, 5, 6], 2))
    C, D = rng.randint(1, 4), rng.randint(1, 4)
    p, q = r + s, -r * s
    N = rng.choice([20, 25, 30])
    C_c = C + 1 if target == FALSE_WITNESS else C
    A, B = C + D, C * r + D * s          # true initial conditions

    truth, witness = True, None
    a_prev, a_cur = A, B
    for n in range(0, N + 1):
        val = a_prev if n == 0 else (a_cur if n == 1 else None)
        if val is None:
            a_prev, a_cur = a_cur, p * a_cur + q * a_prev
            val = a_cur
        if val != C_c * r ** n + D * s ** n:
            truth, witness = False, {"n": n}
            break

    cf = f"{C_c}*{r}**n + {D}*{s}**n"
    base = [step("", "base",
                 f"At n = 0 the closed form gives {C_c + D}, matching a_0 = {A}.",
                 {"kind": "instantiation", "var": "n", "lo": 0, "hi": N, "point": 0,
                  "pred": f"({cf}) == {A}"}),
            step("", "base2",
                 f"At n = 1 the closed form gives {C_c * r + D * s}, matching "
                 f"a_1 = {B}.",
                 {"kind": "instantiation", "var": "n", "lo": 0, "hi": N, "point": 1,
                  "pred": f"({cf}) == {B}"})]
    engine = [step("", "engine",
                   f"The closed form satisfies the recurrence: for every n in "
                   f"[0, {N - 2}], f(n+2) = {p}*f(n+1) + ({q})*f(n).",
                   {"kind": "forall_identity", "var": "n", "lo": 0, "hi": N - 2,
                    "lhs": cf.replace("n", "(n+2)"),
                    "rhs": f"{p}*({cf.replace('n', '(n+1)')}) + ({q})*({cf})"})]
    aux = generic_aux(1, N)
    conclusion = [step("", "conclusion",
                       f"Two base cases plus the recurrence identity give the "
                       f"closed form for every n in [0, {N}].",
                       {"kind": "generalization", "established_hi": N,
                        "asserted_hi": N, "justified": True})]

    steps = _assemble(rng, base, engine, aux, conclusion)
    return Item(
        template_id="t4_linear_recurrence",
        domain_label="recurrences",
        params={"r": r, "s": s, "C": C_c, "D": D, "p": p, "q": q,
                "a0": A, "a1": B, "N": N},
        proposition=f"Let a_0 = {A}, a_1 = {B} and a_n = {p}*a_(n-1) + ({q})*a_(n-2) "
                    f"for n >= 2. Then for every n with 0 <= n <= {N}, "
                    f"a_n = {C_c}*{r}^n + {D}*{s}^n.",
        domain_text=f"integers n with 0 <= n <= {N}",
        quantifiers=f"for all n in [0, {N}]",
        hypotheses=["the recurrence is applied only for n >= 2"],
        steps=steps, truth=truth,
        truth_method="native iteration of the recurrence, compared termwise",
        witness=witness,
        proof_sketch=None if not truth else
        f"r={r} and s={s} are the characteristic roots; C and D are fixed by the "
        "two initial conditions.",
        min_disposition={"kind": "witness_search" if not truth else "closed_form_proof",
                         "cost_units": (witness["n"] + 1) if witness else len(steps)},
        difficulty={"domain_size": N + 1, "derivation_length": len(steps)},
    )


# ==========================================================================
# T5 / T6 - iterated-map stopping times (the opaque families)
# ==========================================================================

_MAPS: dict[str, dict] = {
    "collatz": {
        "domain_label": "elementary_number_theory",
        "template_id": "t5_collatz_stopping_time",
        "desc": "n -> n/2 when n is even, n -> 3n+1 when n is odd",
        "expr": "stop_time(n)",
    },
    "shortcut": {
        "domain_label": "recurrences",
        "template_id": "t6_shortcut_stopping_time",
        "desc": "n -> n/2 when n is even, n -> (3n+1)/2 when n is odd",
        "expr": "shortcut_time(n)",
    },
}

_RECORD_CACHE: dict[str, tuple[list[int], list[int]]] = {}
MAX_LIMIT = 600_000          # generator-side enumeration ceiling


def _step_map(variant: str, x: int) -> int:
    if x % 2 == 0:
        return x // 2
    return 3 * x + 1 if variant == "collatz" else (3 * x + 1) // 2


def _memo(variant: str) -> tuple[list[int], list[int]]:
    """Stopping times for 1..MAX_LIMIT, computed once per variant.

    Computed at the ceiling and sliced, rather than recomputed per N. Caching
    per exact N was what forced the small fixed menu of N values, and that menu
    is what collapsed the two hard classes to 4 and 5 distinct propositions.
    """
    if variant in _RECORD_CACHE:
        return _RECORD_CACHE[variant]
    limit = MAX_LIMIT
    memo = [-1] * (limit + 1)
    memo[1] = 0
    for n in range(2, limit + 1):
        path, x = [], n
        while x > limit or memo[x] < 0:
            path.append(x)
            x = _step_map(variant, x)
        base = memo[x]
        for i, val in enumerate(reversed(path), start=1):
            if val <= limit and memo[val] < 0:
                memo[val] = base + i
    records, best = [], -1
    for n in range(1, limit + 1):
        if memo[n] > best:
            best = memo[n]
            records.append(n)
    _RECORD_CACHE[variant] = (memo, records)
    return _RECORD_CACHE[variant]


def _stopping_times(variant: str, limit: int) -> list[int]:
    return _memo(variant)[0]


def _records(variant: str, limit: int) -> list[int]:
    return [r for r in _memo(variant)[1] if r <= limit]


def build_iterated(variant: str, rng: random.Random, target: str,
                   player_search_budget: int) -> Item | None:
    cfg = _MAPS[variant]
    memo, all_recs = _memo(variant)

    if target in (TRUE_VALID, TRUE_INVALID):
        N = rng.randint(1200, 6000)
        K = max(memo[1:N + 1]) + 1
        checked_hi, justified = N, True
    elif target == FALSE_WITNESS:
        recs = [r for r in all_recs if 50 < r <= EASY_WITNESS_MAX]
        if not recs:
            return None
        n0 = rng.choice(recs)
        N = rng.randint(n0, max(n0 + 1, EASY_WITNESS_MAX + 2000))
        K = max(memo[1:n0]) + 1
        checked_hi, justified = N, True
    elif target == FALSE_HARD:
        recs = [r for r in all_recs
                if EASY_WITNESS_MAX < r <= player_search_budget]
        if not recs:
            return None
        n0 = rng.choice(recs)
        N = rng.randint(n0, player_search_budget)
        K = max(memo[1:n0]) + 1
        checked_hi, justified = rng.randint(1000, EASY_WITNESS_MAX), False
    elif target == UNRESOLVED:
        make_true = rng.random() < 0.5          # 50/50 so guessing gains nothing
        if make_true:
            N = rng.randint(player_search_budget + 1, MAX_LIMIT)
            K = max(memo[1:N + 1]) + 1
        else:
            recs = [r for r in all_recs
                    if player_search_budget < r <= MAX_LIMIT]
            if not recs:
                return None
            n0 = rng.choice(recs)
            N = rng.randint(n0, MAX_LIMIT)
            K = max(memo[1:n0]) + 1
        checked_hi, justified = rng.randint(1000, EASY_WITNESS_MAX), False
    else:
        return None

    justified = justified and checked_hi >= N   # cannot justify past the sweep

    truth, witness = True, None
    for n in range(1, N + 1):
        if memo[n] >= K:
            truth, witness = False, {"n": n, "stopping_time": memo[n]}
            break

    base = [step("", "base",
                 f"Every n in [1, {min(checked_hi, 50)}] has stopping time below "
                 f"{K}; the smallest values are checked directly.",
                 {"kind": "forall_inequality", "var": "n", "lo": 1,
                  "hi": min(checked_hi, 50), "lhs": cfg["expr"], "rhs": str(K),
                  "op": "<"})]
    engine = [step("", "engine",
                   f"A direct sweep verifies that every n in [1, {checked_hi}] has "
                   f"stopping time below {K}.",
                   {"kind": "forall_inequality", "var": "n", "lo": 1,
                    "hi": checked_hi, "lhs": cfg["expr"], "rhs": str(K),
                    "op": "<"})]
    aux = generic_aux(1, min(N, 2000))
    conclusion = [step("", "conclusion",
                       f"The sweep covers [1, {checked_hi}]; the statement is "
                       f"asserted for every n in [1, {N}].",
                       {"kind": "generalization", "established_hi": checked_hi,
                        "asserted_hi": N, "justified": justified})]

    steps = _assemble(rng, base, engine, aux, conclusion)
    cost = (witness["n"] if witness else N)
    return Item(
        template_id=cfg["template_id"],
        domain_label=cfg["domain_label"],
        params={"variant": variant, "N": N, "K": K, "checked_hi": checked_hi},
        proposition=f"Under the map {cfg['desc']}, every integer n with "
                    f"1 <= n <= {N} reaches 1 in fewer than {K} steps.",
        domain_text=f"integers n with 1 <= n <= {N}",
        quantifiers=f"for all n in [1, {N}]",
        hypotheses=["the stopping time counts steps until the value 1 is reached"],
        steps=steps, truth=truth,
        truth_method="native iteration with an array memo, computed at generation "
                     "time under a budget the player does not have",
        witness=witness,
        proof_sketch=None,
        min_disposition={"kind": "witness_search" if witness else "exhaustive",
                         "cost_units": cost},
        difficulty={"domain_size": N, "derivation_length": len(steps),
                    "witness_position": witness["n"] if witness else None},
        notes=["no closed form is available for this map; the only decision "
               "procedure known to the generator is enumeration"],
    )


def build_t5(rng, target, budget):
    return build_iterated("collatz", rng, target, budget)


def build_t6(rng, target, budget):
    return build_iterated("shortcut", rng, target, budget)


BUILDERS: dict[str, Callable] = {
    "t1_integer_sum_identity": build_t1,
    "t2_modular_power_cycle": build_t2,
    "t3_min_degree_connectivity": build_t3,
    "t4_linear_recurrence": build_t4,
    "t5_collatz_stopping_time": build_t5,
    "t6_shortcut_stopping_time": build_t6,
}

NEEDS_BUDGET = {"t5_collatz_stopping_time", "t6_shortcut_stopping_time"}

SUPPORTS: dict[str, set[str]] = {
    "t1_integer_sum_identity": {TRUE_VALID, TRUE_INVALID, FALSE_WITNESS},
    "t2_modular_power_cycle": {TRUE_VALID, TRUE_INVALID, FALSE_WITNESS},
    # t3's only false instance (v=6, d=2) has its first counterexample at
    # enumeration index 5905, just past EASY_WITNESS_MAX. It is therefore a
    # FALSE_BUT_HARD item, not a FALSE_WITH_WITNESS one — the band decides the
    # class, not the template's intent.
    "t3_min_degree_connectivity": {TRUE_VALID, TRUE_INVALID, FALSE_HARD},
    "t4_linear_recurrence": {TRUE_VALID, TRUE_INVALID, FALSE_WITNESS},
    "t5_collatz_stopping_time": set(ALL_CLASSES),
    "t6_shortcut_stopping_time": set(ALL_CLASSES),
}
