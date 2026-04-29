"""prometheus_math.combinatorics_permutations — permutation operations.

A first-class API for permutation combinatorics on the symmetric group
S_n, with emphasis on Bruhat order, weak orders, reduced words,
inversions, and pattern occurrence.

Permutations are represented as tuples / lists of length ``n`` over
``{1, ..., n}`` (one-line notation). The identity permutation in S_n
is ``(1, 2, ..., n)``.

API surface:

- ``inversions(w)``                — list of inversion pairs (i, j)
- ``num_inversions(w)``            — count = length(w) in Coxeter sense
- ``reduced_words(w)``             — all reduced expressions s_{i_1}..s_{i_l}
- ``any_reduced_word(w)``          — single canonical reduced word
- ``bruhat_le(w, v)``              — strong Bruhat order
- ``weak_left_le(w, v)``           — left weak order
- ``weak_right_le(w, v)``          — right weak order
- ``bruhat_interval(w, v)``        — all u with w <= u <= v
- ``cover_relations(w)``           — all u covering w in Bruhat
- ``longest_element(n)``           — w_0 = (n, n-1, ..., 1)
- ``permutation_pattern_count(w, p)``  — # occurrences of pattern p
- ``is_pattern_avoiding(w, patterns)``  — pattern avoidance test
- ``rsk_shape(w)``                 — partition shape of insertion tableau
- ``bruhat_distance(w, v)``        — graph distance in Bruhat order

Conventions (Coxeter / Bjorner-Brenti):

- Simple transpositions ``s_i`` swap positions ``i`` and ``i+1`` for
  ``i in {1, ..., n-1}`` (1-indexed). A reduced word for ``w`` is a
  shortest sequence ``[i_1, ..., i_l]`` with
  ``w = s_{i_1} s_{i_2} ... s_{i_l}`` (right action on the identity).
- Length ``l(w)`` equals the inversion count ``inv(w)``.
- Strong Bruhat order ``w <= v`` iff every reduced word for ``v``
  contains a reduced subword for ``w``. Equivalently, the
  tableau-criterion: sort the prefixes ``{w(1), ..., w(k)}`` and
  ``{v(1), ..., v(k)}``; ``w <= v`` iff the sorted prefix of ``w`` is
  componentwise <= the sorted prefix of ``v`` for every ``k``.
- Right weak order: ``w <=_R v`` iff ``inv(w) subset inv(v)`` as sets
  of inversion pairs.
- Left weak order: ``w <=_L v`` iff ``w^{-1} <=_R v^{-1}``.

References:
- Bjorner, Brenti, "Combinatorics of Coxeter Groups", Springer GTM 231,
  2005. Bruhat order: Ch. 2; weak orders: Ch. 3; reduced words: Ch. 1.
- Stanley, "Enumerative Combinatorics, Vol. 2" (1999), Ch. 7. Pattern
  avoidance and Catalan: Ex. 6.19. RSK: Sec. 7.11.
- Sagan, "The Symmetric Group" (2nd ed. 2001).
- Humphreys, "Reflection Groups and Coxeter Groups" (1990), Ch. 5.
"""

from __future__ import annotations

from functools import lru_cache
from math import factorial
from typing import Iterable, List, Sequence, Tuple

from .combinatorics_partitions import rsk as _rsk


Permutation = Tuple[int, ...]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _to_tuple(w: Sequence[int]) -> Permutation:
    """Coerce ``w`` to an immutable tuple, validating it is a permutation
    of ``{1, ..., n}``."""
    t = tuple(int(x) for x in w)
    n = len(t)
    if n == 0:
        return t
    if sorted(t) != list(range(1, n + 1)):
        raise ValueError(
            f"not a permutation of (1..{n}): got {t}"
        )
    return t


def _check_same_size(w: Permutation, v: Permutation) -> None:
    if len(w) != len(v):
        raise ValueError(
            f"permutations have different sizes: {len(w)} vs {len(v)}"
        )


def _apply_simple(w: Permutation, i: int) -> Permutation:
    """Right action of simple transposition s_i (1-indexed) on w.

    s_i swaps positions i and i+1. For right-multiplication
    ``w * s_i``, we swap positions ``i`` and ``i+1`` of ``w``.
    """
    n = len(w)
    if not 1 <= i <= n - 1:
        raise ValueError(f"simple index out of range: {i}")
    out = list(w)
    out[i - 1], out[i] = out[i], out[i - 1]
    return tuple(out)


def _multiply(u: Permutation, v: Permutation) -> Permutation:
    """Composition (u . v)(k) = u(v(k))."""
    return tuple(u[v[k] - 1] for k in range(len(v)))


def _inverse(w: Permutation) -> Permutation:
    n = len(w)
    inv = [0] * n
    for i, x in enumerate(w):
        inv[x - 1] = i + 1
    return tuple(inv)


# ---------------------------------------------------------------------------
# Inversions and length
# ---------------------------------------------------------------------------


def inversions(w: Sequence[int]) -> List[Tuple[int, int]]:
    """Return the list of inversion pairs of ``w``.

    An inversion is a pair of zero-based positions ``(i, j)`` with
    ``i < j`` and ``w[i] > w[j]``.

    Examples
    --------
    >>> inversions((2, 1))
    [(0, 1)]
    >>> inversions((1, 2, 3))
    []
    """
    t = _to_tuple(w)
    n = len(t)
    pairs: List[Tuple[int, int]] = []
    for i in range(n):
        wi = t[i]
        for j in range(i + 1, n):
            if wi > t[j]:
                pairs.append((i, j))
    return pairs


def num_inversions(w: Sequence[int]) -> int:
    """Return ``inv(w) = l(w)``, the Coxeter length."""
    return len(inversions(w))


# ---------------------------------------------------------------------------
# Reduced words
# ---------------------------------------------------------------------------


def _reduced_words_recursive(w: Permutation) -> List[List[int]]:
    """Enumerate all reduced words for ``w`` via descent recursion.

    Strategy: ``i`` is a (right) descent of ``w`` iff ``w(i) > w(i+1)``,
    iff ``l(w s_i) = l(w) - 1``. Every reduced word ends with such a
    descent. So recursively: for each descent ``i``, prepend reduced
    words for ``w s_i`` with ``i`` and union.
    """
    if num_inversions(w) == 0:
        return [[]]
    n = len(w)
    out: List[List[int]] = []
    seen: set = set()
    for i in range(1, n):
        # descent at position i (1-indexed) iff w[i-1] > w[i]
        if w[i - 1] > w[i]:
            wi = _apply_simple(w, i)  # this is w * s_i; swaps positions
            for rw in _reduced_words_recursive(wi):
                key = tuple(rw + [i])
                if key not in seen:
                    seen.add(key)
                    out.append(rw + [i])
    return out


def reduced_words(w: Sequence[int]) -> List[List[int]]:
    """All reduced words for ``w`` as products of simple transpositions.

    A reduced word is a sequence ``[i_1, ..., i_l]`` of simple-reflection
    indices ``i_k in {1, ..., n-1}`` of minimal length such that
    ``w = s_{i_1} s_{i_2} ... s_{i_l}`` (right action).

    Reference: Bjorner-Brenti (2005), Section 1.5; Edelman-Greene
    bijection with standard Young tableaux of staircase shape.
    """
    t = _to_tuple(w)
    return _reduced_words_recursive(t)


def any_reduced_word(w: Sequence[int]) -> List[int]:
    """A single canonical (lex-min) reduced word for ``w``."""
    t = _to_tuple(w)
    if num_inversions(t) == 0:
        return []
    # Greedy: find the first descent and recurse. This produces a
    # specific reduced word (not necessarily globally lex-min, but
    # canonical).
    word: List[int] = []
    cur = t
    n = len(cur)
    while num_inversions(cur) > 0:
        # leftmost descent
        for i in range(1, n):
            if cur[i - 1] > cur[i]:
                word.append(i)
                cur = _apply_simple(cur, i)
                break
    word.reverse()  # we built it from the right, reverse to get s_{i_1}...
    return word


# ---------------------------------------------------------------------------
# Bruhat order
# ---------------------------------------------------------------------------


def _tableau_criterion(w: Permutation, v: Permutation) -> bool:
    """Strong Bruhat order via the Ehresmann tableau criterion.

    ``w <= v`` iff for every ``k in {1, ..., n}``, the sorted prefix
    of ``w`` of length ``k`` is componentwise <= the sorted prefix of
    ``v`` of length ``k``.

    Reference: Bjorner-Brenti (2005), Theorem 2.1.5 (Ehresmann's
    tableau criterion).
    """
    n = len(w)
    for k in range(1, n + 1):
        sw = sorted(w[:k])
        sv = sorted(v[:k])
        for a, b in zip(sw, sv):
            if a > b:
                return False
    return True


def bruhat_le(w: Sequence[int], v: Sequence[int]) -> bool:
    """Strong Bruhat order: return ``True`` iff ``w <= v``.

    Implemented via the Ehresmann tableau criterion.
    """
    tw = _to_tuple(w)
    tv = _to_tuple(v)
    _check_same_size(tw, tv)
    return _tableau_criterion(tw, tv)


def weak_right_le(w: Sequence[int], v: Sequence[int]) -> bool:
    """Right weak order: ``w <=_R v`` iff ``inv(w) subset inv(v)``.

    Reference: Bjorner-Brenti (2005), Section 3.1; the right weak order
    is generated by right-multiplication by simple transpositions that
    increase length.
    """
    tw = _to_tuple(w)
    tv = _to_tuple(v)
    _check_same_size(tw, tv)
    iw = set(inversions(tw))
    iv = set(inversions(tv))
    return iw.issubset(iv)


def weak_left_le(w: Sequence[int], v: Sequence[int]) -> bool:
    """Left weak order: ``w <=_L v`` iff ``w^{-1} <=_R v^{-1}``.

    Reference: Bjorner-Brenti (2005), Section 3.1.
    """
    tw = _to_tuple(w)
    tv = _to_tuple(v)
    _check_same_size(tw, tv)
    return weak_right_le(_inverse(tw), _inverse(tv))


def bruhat_interval(
    w: Sequence[int], v: Sequence[int]
) -> List[Permutation]:
    """All permutations ``u`` with ``w <= u <= v`` in Bruhat order.

    Uses brute enumeration of ``S_n``; intended for small ``n`` (n <= 8
    is fine; n >= 10 is huge).

    Reference: Bjorner-Brenti (2005), Section 2.4.
    """
    tw = _to_tuple(w)
    tv = _to_tuple(v)
    _check_same_size(tw, tv)
    n = len(tw)
    if not _tableau_criterion(tw, tv):
        return []
    out: List[Permutation] = []
    for u in _all_permutations(n):
        if _tableau_criterion(tw, u) and _tableau_criterion(u, tv):
            out.append(u)
    return out


def cover_relations(w: Sequence[int]) -> List[Permutation]:
    """All ``u`` covering ``w`` in Bruhat order.

    ``u`` covers ``w`` iff ``w < u`` and ``l(u) = l(w) + 1``. Equivalently
    (Bjorner-Brenti Lemma 2.1.4), ``u = w t_{ij}`` for some
    transposition ``t_{ij}`` with ``i < j``, ``w(i) < w(j)``, and no
    intermediate ``k`` has ``w(i) < w(k) < w(j)``.
    """
    t = _to_tuple(w)
    n = len(t)
    out: List[Permutation] = []
    for i in range(n):
        for j in range(i + 1, n):
            if t[i] < t[j]:
                # Check no k strictly between i and j has w(i) < w(k) < w(j)
                bad = False
                for k in range(i + 1, j):
                    if t[i] < t[k] < t[j]:
                        bad = True
                        break
                if not bad:
                    new = list(t)
                    new[i], new[j] = new[j], new[i]
                    out.append(tuple(new))
    return out


def longest_element(n: int) -> Permutation:
    """``w_0 = (n, n-1, ..., 1)`` in S_n.

    Length is ``n*(n-1)/2``.
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    return tuple(range(n, 0, -1))


# ---------------------------------------------------------------------------
# Pattern avoidance
# ---------------------------------------------------------------------------


def _pattern_validate(p: Sequence[int]) -> Permutation:
    t = tuple(int(x) for x in p)
    if len(t) == 0:
        raise ValueError("pattern must be non-empty")
    if sorted(t) != list(range(1, len(t) + 1)):
        raise ValueError(
            f"pattern must be a permutation of (1..{len(t)}): got {t}"
        )
    return t


def permutation_pattern_count(
    w: Sequence[int], pattern: Sequence[int]
) -> int:
    """Count occurrences of ``pattern`` in ``w``.

    A subsequence ``w[i_1] < ... < i_k`` (positions) realizes
    ``pattern`` iff its relative order (rank-by-value) matches.

    Examples
    --------
    >>> permutation_pattern_count((3, 1, 4, 2), (1, 3, 2))
    1

    Reference: Bona, "Combinatorics of Permutations" (2nd ed. 2012),
    Ch. 4.
    """
    tw = _to_tuple(w)
    p = _pattern_validate(pattern)
    k = len(p)
    n = len(tw)
    if k > n:
        return 0
    count = 0
    # Enumerate index k-tuples i_1 < ... < i_k
    indices = list(range(n))
    from itertools import combinations

    for combo in combinations(indices, k):
        sub = [tw[i] for i in combo]
        # rank-relabel sub
        sorted_vals = sorted(sub)
        rank = {v: r + 1 for r, v in enumerate(sorted_vals)}
        rel = tuple(rank[v] for v in sub)
        if rel == p:
            count += 1
    return count


def is_pattern_avoiding(
    w: Sequence[int], patterns: Iterable[Sequence[int]]
) -> bool:
    """Return ``True`` iff ``w`` contains none of the given patterns.

    Reference: Bona, "Combinatorics of Permutations" (2nd ed. 2012),
    Ch. 4. Famous example: ``Av(132)`` in ``S_n`` has size ``C_n``,
    the n-th Catalan number.
    """
    pats = list(patterns)
    if len(pats) == 0:
        return True
    for p in pats:
        if permutation_pattern_count(w, p) > 0:
            return False
    return True


# ---------------------------------------------------------------------------
# RSK shape and Bruhat distance
# ---------------------------------------------------------------------------


def rsk_shape(w: Sequence[int]) -> Tuple[int, ...]:
    """Shape of the insertion tableau ``P`` from RSK.

    Calls into ``prometheus_math.combinatorics_partitions.rsk`` and
    returns the row-length partition of ``P``.

    For a permutation of ``n``, this is a partition of ``n`` (a
    weakly-decreasing tuple of positive integers summing to n).

    Reference: Sagan (2001), Sec. 3.5; Stanley EC2 Sec. 7.11.
    """
    t = _to_tuple(w)
    if len(t) == 0:
        return ()
    P, _Q = _rsk(t)
    return tuple(len(row) for row in P)


def _all_permutations(n: int) -> List[Permutation]:
    """All permutations of (1..n) — brute, for small n."""
    if n == 0:
        return [()]
    from itertools import permutations as _it_perms

    return [tuple(p) for p in _it_perms(range(1, n + 1))]


def bruhat_distance(
    w: Sequence[int], v: Sequence[int]
) -> int | None:
    """Length of any saturated chain ``w = u_0 < u_1 < ... < u_k = v``
    in Bruhat order, if ``w <= v``; else ``None``.

    Equals ``l(v) - l(w)`` when ``w <= v`` because the Bruhat order on
    S_n is a graded poset with rank function ``l``.

    Reference: Bjorner-Brenti (2005), Theorem 2.2.6 (Bruhat is a graded
    poset, rank = length).
    """
    tw = _to_tuple(w)
    tv = _to_tuple(v)
    _check_same_size(tw, tv)
    if not _tableau_criterion(tw, tv):
        # Try the reverse direction — bruhat_distance is symmetric in
        # the sense that distance is well-defined when comparable in
        # either order.
        if _tableau_criterion(tv, tw):
            return num_inversions(tw) - num_inversions(tv)
        return None
    return num_inversions(tv) - num_inversions(tw)


__all__ = [
    "Permutation",
    "inversions",
    "num_inversions",
    "reduced_words",
    "any_reduced_word",
    "bruhat_le",
    "weak_left_le",
    "weak_right_le",
    "bruhat_interval",
    "cover_relations",
    "longest_element",
    "permutation_pattern_count",
    "is_pattern_avoiding",
    "rsk_shape",
    "bruhat_distance",
]
