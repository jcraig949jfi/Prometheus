#!/usr/bin/env python3
"""Restricted expression language + the step-check runner.

This module is deliberately the ONLY thing shared between the two oracles, and
it shares only arithmetic evaluation.  It contains no decision logic about
whether a proposition is true and no decision logic about whether an argument is
valid.  Those live in `templates.py` (native Python enumeration) and
`derivation.py` (string-expression step checks) respectively, and they reach
their verdicts by disjoint routes.  See GENERATOR.md section 2.

Expressions here are authored by the generator, never by a player, so `eval`
against a whitelisted namespace is acceptable.  Nothing in this file may ever be
called on player-supplied input.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Any, Callable

# --------------------------------------------------------------------------
# arithmetic helpers exposed to the expression language
# --------------------------------------------------------------------------

_SUMK_CACHE: dict[int, list[int]] = {}


def sum_k(n: int, p: int = 1) -> int:
    """sum_{k=1}^{n} k**p, memoised as a prefix table per exponent."""
    if n < 0:
        return 0
    table = _SUMK_CACHE.setdefault(p, [0])
    while len(table) <= n:
        table.append(table[-1] + len(table) ** p)
    return table[n]


_FIB_CACHE = [0, 1]


def fib(n: int) -> int:
    if n < 0:
        raise ValueError("fib undefined for negative n")
    while len(_FIB_CACHE) <= n:
        _FIB_CACHE.append(_FIB_CACHE[-1] + _FIB_CACHE[-2])
    return _FIB_CACHE[n]


_STOP_CACHE: dict[int, int] = {1: 0}
_STOP_LIMIT = 4_000_000


def stop_time(n: int) -> int:
    """Collatz total stopping time: steps for n to reach 1."""
    if n < 1:
        raise ValueError("stop_time undefined below 1")
    path: list[int] = []
    x = n
    while x not in _STOP_CACHE:
        path.append(x)
        x = x // 2 if x % 2 == 0 else 3 * x + 1
    base = _STOP_CACHE[x]
    for i, v in enumerate(reversed(path), start=1):
        if v <= _STOP_LIMIT:
            _STOP_CACHE[v] = base + i
    return base + len(path)


def lin_rec(n: int, a0: int, a1: int, p: int, q: int) -> int:
    """a_n for a_n = p*a_(n-1) + q*a_(n-2)."""
    if n == 0:
        return a0
    if n == 1:
        return a1
    prev, cur = a0, a1
    for _ in range(2, n + 1):
        prev, cur = cur, p * cur + q * prev
    return cur


def digit_sum(n: int) -> int:
    return sum(int(c) for c in str(abs(n)))


def mult_order(a: int, m: int) -> int:
    """Multiplicative order of a mod m; requires gcd(a, m) == 1."""
    if math.gcd(a, m) != 1:
        raise ValueError("order undefined when gcd(a, m) != 1")
    d, x = 1, a % m
    while x != 1:
        x = (x * a) % m
        d += 1
    return d


# --- small-graph helpers: a graph on v vertices is an int bitmask over edges --

@lru_cache(maxsize=None)
def edge_list(v: int) -> tuple[tuple[int, int], ...]:
    return tuple((i, j) for i in range(v) for j in range(i + 1, v))


@lru_cache(maxsize=1 << 20)
def graph_degrees(g: int, v: int) -> tuple[int, ...]:
    deg = [0] * v
    for bit, (i, j) in enumerate(edge_list(v)):
        if g >> bit & 1:
            deg[i] += 1
            deg[j] += 1
    return tuple(deg)


def graph_min_degree(g: int, v: int) -> int:
    return min(graph_degrees(g, v))


def graph_edge_count(g: int, v: int) -> int:
    return bin(g).count("1")


@lru_cache(maxsize=1 << 20)
def graph_is_connected(g: int, v: int) -> int:
    adj = [0] * v
    for bit, (i, j) in enumerate(edge_list(v)):
        if g >> bit & 1:
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    seen, stack = 1, [0]
    while stack:
        u = stack.pop()
        nxt = adj[u] & ~seen
        while nxt:
            w = (nxt & -nxt).bit_length() - 1
            seen |= 1 << w
            stack.append(w)
            nxt &= nxt - 1
    return 1 if seen == (1 << v) - 1 else 0



_SHORT_CACHE: dict[int, int] = {1: 0}


def shortcut_time(n: int) -> int:
    """Stopping time under the shortcut map x -> x/2 | (3x+1)/2."""
    if n < 1:
        raise ValueError("shortcut_time undefined below 1")
    path: list[int] = []
    x = n
    while x not in _SHORT_CACHE:
        path.append(x)
        x = x // 2 if x % 2 == 0 else (3 * x + 1) // 2
    base = _SHORT_CACHE[x]
    for i, v in enumerate(reversed(path), start=1):
        if v <= _STOP_LIMIT:
            _SHORT_CACHE[v] = base + i
    return base + len(path)


@lru_cache(maxsize=1 << 20)
def graph_min_component_size(g: int, v: int) -> int:
    adj = [0] * v
    for bit, (i, j) in enumerate(edge_list(v)):
        if g >> bit & 1:
            adj[i] |= 1 << j
            adj[j] |= 1 << i
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


SAFE_NAMESPACE: dict[str, Callable[..., Any] | Any] = {
    "sum_k": sum_k,
    "fib": fib,
    "stop_time": stop_time,
    "shortcut_time": shortcut_time,
    "graph_min_component_size": graph_min_component_size,
    "lin_rec": lin_rec,
    "digit_sum": digit_sum,
    "mult_order": mult_order,
    "graph_min_degree": graph_min_degree,
    "graph_is_connected": graph_is_connected,
    "graph_edge_count": graph_edge_count,
    "graph_degrees": graph_degrees,
    "gcd": math.gcd,
    "isqrt": math.isqrt,
    "abs": abs,
    "min": min,
    "max": max,
    "pow": pow,
    "int": int,
    "len": len,
    "sum": sum,
    "all": all,
    "any": any,
    "range": range,
}


def evaluate(expr: str, bindings: dict[str, Any]) -> Any:
    """Evaluate a generator-authored expression under the safe namespace."""
    env = dict(SAFE_NAMESPACE)
    env.update(bindings)
    return eval(expr, {"__builtins__": {}}, env)  # noqa: S307 - generator-authored only
