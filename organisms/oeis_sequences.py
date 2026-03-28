"""
OEIS-Style Integer Sequences as Organisms.

Since OEIS bulk download is behind Cloudflare, we generate well-known
integer sequences from formulas. Each sequence is a callable that maps
n -> a(n). These are lookup-table organisms — they don't compute,
they recall precomputed values.

Output type is 'oeis_integer' (distinct from 'integer') to prevent
the type system from blindly piping OEIS outputs into heavy operations.

We generate the first 200 terms of each sequence, which covers all
standard probe inputs (n up to ~100).
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Callable
import math

# Generate sequences as arrays of precomputed values
MAX_TERMS = 200


def _make_sequence(name: str, func: Callable[[int], int], start: int = 0) -> Dict:
    """Generate a sequence dict with precomputed values."""
    values = []
    for n in range(start, start + MAX_TERMS):
        try:
            v = func(n)
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                values.append(0)
            elif abs(v) > 10**15:
                values.append(int(v) % (10**15))  # cap huge values
            else:
                values.append(int(v))
        except (ValueError, OverflowError, ZeroDivisionError, RecursionError):
            values.append(0)
    return {"name": name, "values": values, "start": start}


def _fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def _catalan(n):
    if n <= 1:
        return 1
    c = 1
    for i in range(n):
        c = c * (4 * i + 2) // (i + 2)
    return c


def _bell(n):
    if n == 0:
        return 1
    bell = [[0] * (n + 1) for _ in range(n + 1)]
    bell[0][0] = 1
    for i in range(1, n + 1):
        bell[i][0] = bell[i - 1][i - 1]
        for j in range(1, i + 1):
            bell[i][j] = bell[i - 1][j - 1] + bell[i][j - 1]
    return bell[n][0]


def _partition_count(n):
    """Number of integer partitions of n."""
    if n < 0:
        return 0
    p = [0] * (n + 1)
    p[0] = 1
    for k in range(1, n + 1):
        for i in range(k, n + 1):
            p[i] += p[i - k]
    return p[n]


def _euler_totient(n):
    if n < 1:
        return 0
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def _motzkin(n):
    if n <= 1:
        return 1
    m = [0] * (n + 1)
    m[0] = m[1] = 1
    for i in range(2, n + 1):
        m[i] = ((2 * i + 1) * m[i - 1] + 3 * (i - 1) * m[i - 2]) // (i + 2)
    return m[n]


def _divisor_count(n):
    if n < 1:
        return 0
    count = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            count += 2 if i != n // i else 1
    return count


def _divisor_sum(n):
    if n < 1:
        return 0
    s = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            s += i
            if i != n // i:
                s += n // i
    return s


def _is_prime(n):
    if n < 2:
        return 0
    if n < 4:
        return 1
    if n % 2 == 0 or n % 3 == 0:
        return 0
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return 0
        i += 6
    return 1


def _prime_pi(n):
    """Count primes up to n."""
    return sum(1 for i in range(2, n + 1) if _is_prime(i))


def _collatz_steps(n):
    if n < 1:
        return 0
    steps = 0
    while n != 1 and steps < 1000:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


SEQUENCES = [
    # Classic combinatorial
    _make_sequence("fibonacci", _fibonacci),
    _make_sequence("catalan", _catalan),
    _make_sequence("bell", _bell, start=0),
    _make_sequence("motzkin", _motzkin),
    _make_sequence("partition", _partition_count),

    # Number theoretic
    _make_sequence("euler_totient", _euler_totient, start=1),
    _make_sequence("divisor_count", _divisor_count, start=1),
    _make_sequence("divisor_sum", _divisor_sum, start=1),
    _make_sequence("prime_indicator", _is_prime),
    _make_sequence("prime_counting", _prime_pi),

    # Powers and arithmetic
    _make_sequence("triangular", lambda n: n * (n + 1) // 2),
    _make_sequence("squares", lambda n: n * n),
    _make_sequence("cubes", lambda n: n ** 3),
    _make_sequence("powers_of_2", lambda n: 2 ** n),
    _make_sequence("factorial", lambda n: math.factorial(min(n, 170))),

    # Figurate numbers
    _make_sequence("pentagonal", lambda n: n * (3 * n - 1) // 2),
    _make_sequence("hexagonal", lambda n: n * (2 * n - 1)),
    _make_sequence("tetrahedral", lambda n: n * (n + 1) * (n + 2) // 6),

    # Dynamics and chaos
    _make_sequence("collatz_steps", _collatz_steps, start=1),

    # Alternating and sign patterns
    _make_sequence("alternating", lambda n: (-1) ** n),
    _make_sequence("central_binomial", lambda n: math.comb(2 * n, n)),

    # Digit-based
    _make_sequence("digit_sum", lambda n: sum(int(d) for d in str(abs(n)))),
    _make_sequence("digit_count", lambda n: len(str(abs(max(n, 1))))),

    # Recurrences
    _make_sequence("tribonacci", lambda n, _c=[0, 0, 1]: (
        _c.append(_c[-1] + _c[-2] + _c[-3]) or _c[n] if n >= len(_c) else _c[n]
    )),
    _make_sequence("lucas", lambda n: (
        2 if n == 0 else 1 if n == 1 else
        round(((1 + 5**0.5) / 2) ** n + ((1 - 5**0.5) / 2) ** n)
    )),
]

# Fix tribonacci (the lambda trick doesn't work well for sequences)
# Recompute properly
_trib = [0, 0, 1]
for i in range(3, MAX_TERMS + 10):
    _trib.append(_trib[-1] + _trib[-2] + _trib[-3])
SEQUENCES[-2] = {"name": "tribonacci", "values": _trib[:MAX_TERMS], "start": 0}


def get_oeis_organisms() -> List[Dict]:
    """
    Return organism operation dicts for all OEIS sequences.
    Each sequence becomes one operation in a single 'oeis' organism.
    """
    operations = {}
    for seq in SEQUENCES:
        name = seq["name"]
        values = seq["values"]
        start = seq["start"]

        # Build code string that does lookup
        values_str = repr(values[:MAX_TERMS])
        code = (
            f'def {name}(n):\n'
            f'    values = {values_str}\n'
            f'    idx = int(n) - {start}\n'
            f'    if 0 <= idx < len(values):\n'
            f'        return values[idx]\n'
            f'    return 0\n'
        )

        operations[name] = {
            "code": code,
            "input_type": "integer",
            "output_type": "oeis_integer",
        }

    return operations


# Generate the organism class
class OeisOrganism:
    """Auto-generated organism wrapping OEIS-style integer sequences."""
    name = "oeis"

    def __init__(self):
        self.operations = get_oeis_organisms()
        self._compiled_cache = {}

    def _compile(self, op_name):
        if op_name in self._compiled_cache:
            return self._compiled_cache[op_name]
        code = self.operations[op_name]["code"]
        local_ns = {"np": np, "math": math}
        exec(compile(code, f"<oeis.{op_name}>", "exec"), local_ns)
        fn = local_ns[op_name]
        self._compiled_cache[op_name] = fn
        return fn

    def execute(self, op_name, *args, **kwargs):
        fn = self._compile(op_name)
        return fn(*args, **kwargs)

    def list_operations(self):
        return [
            {"name": n, "input_type": m["input_type"], "output_type": m["output_type"]}
            for n, m in self.operations.items()
        ]

    def compatible_chains(self, other):
        chains = []
        for s_name, s_meta in self.operations.items():
            for o_name, o_meta in other.operations.items():
                if s_meta["output_type"] == o_meta["input_type"]:
                    chains.append((s_name, o_name))
        return chains


if __name__ == "__main__":
    org = OeisOrganism()
    print(f"OEIS organism: {len(org.operations)} sequences")
    for name in list(org.operations.keys())[:5]:
        vals = [org.execute(name, i) for i in range(10)]
        print(f"  {name:20s}: {vals}")
    print(f"\nAll sequences:")
    for name in org.operations:
        vals = [org.execute(name, i) for i in range(6)]
        print(f"  {name:20s}: {vals}")
