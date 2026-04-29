"""prometheus_math.combinatorics_partitions — integer partitions, Young
diagrams, and Young tableaux.

This module provides a first-class API for combinatorial structures on
partitions:

- partitions_of, num_partitions  — enumeration and counts
- conjugate                       — partition transposition
- hook_length, hook_length_array  — Young diagram hooks
- num_standard_young_tableaux     — Frame-Robinson-Thrall hook formula
- num_ssyt                        — Stanley hook-content formula
- all_standard_young_tableaux     — brute generation (small lambda)
- all_semi_standard_young_tableaux— brute generation of SSYT
- rsk, inverse_rsk                — Robinson-Schensted-Knuth
- schur_polynomial                — alternant / bialternant formula

References:
- Sagan, "The Symmetric Group" (2nd ed., 2001), Ch. 3.
- Stanley, "Enumerative Combinatorics, Vol. 2" (1999), Ch. 7.
- Macdonald, "Symmetric Functions and Hall Polynomials" (2nd ed., 1995).
- Andrews, "The Theory of Partitions" (1976).
"""

from __future__ import annotations

from functools import lru_cache
from math import factorial
from typing import Iterator, List, Sequence, Tuple

import sympy


Partition = Tuple[int, ...]


# ---------------------------------------------------------------------------
# Enumeration / counting
# ---------------------------------------------------------------------------


def partitions_of(
    n: int, k: int | None = None, distinct: bool = False
) -> List[Partition]:
    """All integer partitions of ``n``.

    Parameters
    ----------
    n : int
        Non-negative integer to partition.
    k : int or None
        If given, restrict to partitions with exactly ``k`` parts.
    distinct : bool
        If True, restrict to partitions with all parts distinct.

    Returns
    -------
    list of tuples (each weakly decreasing).
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    if k is not None and k < 0:
        raise ValueError(f"k must be non-negative, got {k}")

    if n == 0:
        # The empty partition has 0 parts; only matches k == 0 (or k is None).
        if k is None or k == 0:
            return [()]
        return []

    out: List[Partition] = []
    for p in _partitions_iter(n, max_part=n, distinct=distinct):
        if k is None or len(p) == k:
            out.append(p)
    return out


def _partitions_iter(
    n: int, max_part: int, distinct: bool
) -> Iterator[Partition]:
    """Yield partitions of n with parts <= max_part."""
    if n == 0:
        yield ()
        return
    for first in range(min(n, max_part), 0, -1):
        nxt_max = first - 1 if distinct else first
        for tail in _partitions_iter(n - first, nxt_max, distinct):
            yield (first,) + tail


@lru_cache(maxsize=None)
def num_partitions(n: int, k: int | None = None) -> int:
    """Count the integer partitions of ``n``.

    With no ``k``, uses Euler's pentagonal number recurrence (Andrews
    1976, Cor. 1.8). With ``k`` given, uses the standard p(n, k)
    recurrence p(n, k) = p(n-1, k-1) + p(n-k, k).
    """
    if n < 0:
        return 0
    if k is None:
        return _p_total(n)
    return _p_with_parts(n, k)


@lru_cache(maxsize=None)
def _p_total(n: int) -> int:
    """Euler pentagonal recurrence:
    p(n) = sum_{k>=1} (-1)^{k+1} (p(n - k(3k-1)/2) + p(n - k(3k+1)/2)).
    """
    if n < 0:
        return 0
    if n == 0:
        return 1
    total = 0
    k = 1
    while True:
        # Generalized pentagonal numbers: g_k = k(3k-1)/2 and k(3k+1)/2.
        g1 = k * (3 * k - 1) // 2
        g2 = k * (3 * k + 1) // 2
        if g1 > n:
            break
        sign = -1 if k % 2 == 0 else 1
        total += sign * _p_total(n - g1)
        if g2 <= n:
            total += sign * _p_total(n - g2)
        k += 1
    return total


@lru_cache(maxsize=None)
def _p_with_parts(n: int, k: int) -> int:
    if n == 0 and k == 0:
        return 1
    if n <= 0 or k <= 0:
        return 0
    if k > n:
        return 0
    return _p_with_parts(n - 1, k - 1) + _p_with_parts(n - k, k)


# ---------------------------------------------------------------------------
# Young diagrams
# ---------------------------------------------------------------------------


def conjugate(partition: Sequence[int]) -> Partition:
    """Conjugate (transpose) partition.

    lambda'_i = #{j : lambda_j >= i}.
    """
    if not partition:
        return ()
    m = max(partition)
    return tuple(sum(1 for x in partition if x >= i) for i in range(1, m + 1))


def hook_length(partition: Sequence[int], i: int, j: int) -> int:
    """Hook length of cell (i, j) (0-indexed) in shape ``partition``.

    h(i, j) = (lambda_i - j) + (lambda'_j - i) - 1
            = arm(i,j) + leg(i,j) + 1.

    Raises
    ------
    ValueError if (i, j) is not a cell of the diagram.
    """
    if i < 0 or i >= len(partition):
        raise ValueError(f"row index {i} out of range for partition {partition}")
    if j < 0 or j >= partition[i]:
        raise ValueError(
            f"col index {j} out of range for partition {partition} row {i}"
        )
    arm = partition[i] - j - 1
    leg = sum(1 for r in range(i + 1, len(partition)) if partition[r] > j)
    return arm + leg + 1


def hook_length_array(partition: Sequence[int]) -> List[List[int]]:
    """Hook lengths for all cells, as a row-major list of lists."""
    return [
        [hook_length(partition, i, j) for j in range(partition[i])]
        for i in range(len(partition))
    ]


# ---------------------------------------------------------------------------
# Tableaux counts
# ---------------------------------------------------------------------------


def num_standard_young_tableaux(partition: Sequence[int]) -> int:
    """Count standard Young tableaux of shape ``partition`` via the
    Frame-Robinson-Thrall hook-length formula:

        f^lambda = n! / prod(hook lengths).

    Reference: Sagan (2001), Thm 3.10.2.
    """
    n = sum(partition)
    if n == 0:
        return 1
    prod = 1
    for row in hook_length_array(partition):
        for h in row:
            prod *= h
    return factorial(n) // prod


def num_ssyt(partition: Sequence[int], max_entry: int) -> int:
    """Count semi-standard Young tableaux of shape ``partition`` with
    entries in [1, max_entry] via Stanley's hook-content formula:

        s_lambda(1, ..., 1) = prod_c (max_entry + content(c)) / hook(c).

    Reference: Stanley (1999), Cor. 7.21.4.
    """
    if not partition:
        # The empty shape has exactly one (empty) tableau, regardless of
        # max_entry (including max_entry = 0).
        return 1
    if max_entry <= 0:
        return 0
    num = 1
    den = 1
    for i, lam_i in enumerate(partition):
        for j in range(lam_i):
            content = j - i
            num *= max_entry + content
            den *= hook_length(partition, i, j)
    # The result is always a positive integer; integer division is exact.
    return num // den


# ---------------------------------------------------------------------------
# Tableaux generation
# ---------------------------------------------------------------------------


def all_standard_young_tableaux(
    partition: Sequence[int],
) -> List[List[List[int]]]:
    """All standard Young tableaux of shape ``partition``.

    Brute force: place 1, 2, ..., n one at a time at any inner corner.
    Limited to small ``partition``.
    """
    n = sum(partition)
    if n == 0:
        return [[]]
    shape = list(partition)
    # Initialize an empty tableau (list of lists) of shape `shape`.
    tab: List[List[int]] = [[0] * row for row in shape]
    out: List[List[List[int]]] = []
    _fill_syt(tab, shape, 1, n, out)
    return out


def _fill_syt(
    tab: List[List[int]],
    shape: List[int],
    next_val: int,
    n: int,
    out: List[List[List[int]]],
) -> None:
    if next_val > n:
        out.append([row[:] for row in tab])
        return
    for i in range(len(shape)):
        for j in range(shape[i]):
            if tab[i][j] != 0:
                continue
            # Cell (i, j) is fillable iff (i-1, j) is filled (or i==0)
            # and (i, j-1) is filled (or j==0).
            if i > 0 and tab[i - 1][j] == 0:
                continue
            if j > 0 and tab[i][j - 1] == 0:
                continue
            # Adding next_val here keeps strict increase along rows
            # (because j-1 has a smaller value, having been placed earlier)
            # and columns (same reason vertically). Place and recurse.
            tab[i][j] = next_val
            _fill_syt(tab, shape, next_val + 1, n, out)
            tab[i][j] = 0
            # Only one cell at a time per row (left-to-right): the next
            # available cell in row i has a fixed column. Break out of
            # the inner loop to move to the next row.
            break


def all_semi_standard_young_tableaux(
    partition: Sequence[int], max_entry: int
) -> List[List[List[int]]]:
    """All semi-standard Young tableaux of shape ``partition`` with
    entries in [1, max_entry]. Brute force, limited to small shapes.
    """
    if not partition:
        return [[]]
    if max_entry <= 0:
        return []
    shape = list(partition)
    tab: List[List[int]] = [[0] * row for row in shape]
    out: List[List[List[int]]] = []
    _fill_ssyt(tab, shape, 0, 0, max_entry, out)
    return out


def _fill_ssyt(
    tab: List[List[int]],
    shape: List[int],
    i: int,
    j: int,
    max_entry: int,
    out: List[List[List[int]]],
) -> None:
    # Advance (i, j) row-by-row.
    if i >= len(shape):
        out.append([row[:] for row in tab])
        return
    if j >= shape[i]:
        _fill_ssyt(tab, shape, i + 1, 0, max_entry, out)
        return
    # Lower bound: weakly increase along the row, strictly along the column.
    lo = 1
    if j > 0:
        lo = max(lo, tab[i][j - 1])
    if i > 0:
        lo = max(lo, tab[i - 1][j] + 1)
    for v in range(lo, max_entry + 1):
        tab[i][j] = v
        _fill_ssyt(tab, shape, i, j + 1, max_entry, out)
        tab[i][j] = 0


# ---------------------------------------------------------------------------
# Robinson-Schensted-Knuth correspondence
# ---------------------------------------------------------------------------


def _row_insert(P: List[List[int]], x: int) -> Tuple[int, int]:
    """Schensted row-insertion of ``x`` into tableau ``P`` (modifies P).

    Returns the (row, col) coordinates of the cell where the bumping
    cascade finally settles.
    """
    r = 0
    while True:
        if r == len(P):
            P.append([x])
            return (r, 0)
        row = P[r]
        # Find the leftmost element in row strictly greater than x.
        idx = None
        for k, val in enumerate(row):
            if val > x:
                idx = k
                break
        if idx is None:
            row.append(x)
            return (r, len(row) - 1)
        # Bump.
        bumped = row[idx]
        row[idx] = x
        x = bumped
        r += 1


def rsk(permutation: Sequence[int]) -> Tuple[List[List[int]], List[List[int]]]:
    """Robinson-Schensted-Knuth correspondence on a permutation.

    Returns
    -------
    (P, Q) : (insertion tableau, recording tableau).

    Reference: Sagan (2001), Section 3.5.
    """
    P: List[List[int]] = []
    Q: List[List[int]] = []
    for step, x in enumerate(permutation, start=1):
        i, j = _row_insert(P, x)
        # Add (step) to Q at the same cell (i, j).
        if i == len(Q):
            Q.append([step])
        else:
            Q[i].append(step)
    return P, Q


def inverse_rsk(
    P: Sequence[Sequence[int]], Q: Sequence[Sequence[int]]
) -> List[int]:
    """Inverse RSK: recover the permutation from (P, Q)."""
    if len(P) != len(Q):
        raise ValueError("P and Q have different number of rows")
    if any(len(p) != len(q) for p, q in zip(P, Q)):
        raise ValueError("P and Q have different shapes")
    # Mutable working copies.
    Pw: List[List[int]] = [list(row) for row in P]
    n = sum(len(row) for row in P)
    out: List[int] = []
    for step in range(n, 0, -1):
        # Find cell containing `step` in Q (uniquely determined).
        cell = None
        for i, row in enumerate(Q):
            for j, val in enumerate(row):
                if val == step:
                    cell = (i, j)
                    break
            if cell is not None:
                break
        if cell is None:
            raise ValueError(f"step {step} missing in Q")
        i, _ = cell
        # Pop the rightmost cell of row i in Pw (which must be at column j).
        j = len(Pw[i]) - 1
        x = Pw[i].pop(j)
        # Reverse-bump x up through rows 0..i-1.
        for r in range(i - 1, -1, -1):
            row = Pw[r]
            # Find rightmost val < x to swap with.
            idx = None
            for k in range(len(row) - 1, -1, -1):
                if row[k] < x:
                    idx = k
                    break
            if idx is None:
                # Shouldn't happen for a valid (P, Q) pair, but be safe.
                raise ValueError("inverse_rsk: invalid tableau pair")
            row[idx], x = x, row[idx]
        out.append(x)
        # Strip empty trailing row from Pw if any.
        if not Pw[i] and i == len(Pw) - 1:
            Pw.pop()
    out.reverse()
    return out


# ---------------------------------------------------------------------------
# Schur polynomials
# ---------------------------------------------------------------------------


def schur_polynomial(partition: Sequence[int], max_var: int):
    """Schur polynomial s_lambda(x_1, ..., x_{max_var}) via the
    bialternant formula:

        s_lambda = a_{lambda + delta} / a_delta,

    where delta = (n-1, n-2, ..., 0) and a_alpha = det(x_i^{alpha_j}).

    Reference: Macdonald (1995), I.3, eqn 3.1.
    """
    # Empty partition: s_() = 1 always.
    if not partition or all(p == 0 for p in partition):
        return sympy.Integer(1)
    if max_var <= 0:
        return sympy.Integer(0)
    # Pad partition to length max_var with zeros.
    lam = list(partition)
    if len(lam) > max_var:
        # Schur polynomial in fewer variables than parts is 0.
        if any(lam[i] > 0 for i in range(max_var, len(lam))):
            return sympy.Integer(0)
        lam = lam[:max_var]
    while len(lam) < max_var:
        lam.append(0)
    n = max_var
    xs = sympy.symbols(f"x_1:{n + 1}")
    delta = list(range(n - 1, -1, -1))
    alpha = [lam[i] + delta[i] for i in range(n)]
    # Numerator: det(x_i^{alpha_j})
    num = sympy.Matrix(
        [[xs[i] ** alpha[j] for j in range(n)] for i in range(n)]
    ).det()
    # Denominator: det(x_i^{delta_j}) = Vandermonde = prod_{i<j} (x_i - x_j)
    den = sympy.Matrix(
        [[xs[i] ** delta[j] for j in range(n)] for i in range(n)]
    ).det()
    quotient = sympy.simplify(num / den)
    return sympy.expand(quotient)


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------


def bulgey(partition: Sequence[int]) -> Tuple[int, int]:
    """Return a (n, length) summary of a partition: (sum, len)."""
    return (sum(partition), len(partition))


__all__ = [
    "partitions_of",
    "num_partitions",
    "conjugate",
    "hook_length",
    "hook_length_array",
    "num_standard_young_tableaux",
    "num_ssyt",
    "all_standard_young_tableaux",
    "all_semi_standard_young_tableaux",
    "rsk",
    "inverse_rsk",
    "schur_polynomial",
    "bulgey",
]
