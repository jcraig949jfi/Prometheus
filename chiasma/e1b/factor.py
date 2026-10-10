"""Factoring lever (HADES-28): shared abstraction vertices for the positive geometry.

A factored organism stores its cell premises over an extended vertex set: a rule
v = (a, b) names a pair of vertices (primitive or earlier rule) once, and every premise
that contains both a and b stores v instead. Rules nest, so Y = c & f, and then
c & f & u, can each become one vertex. This is Re-Pair grammar compression over the
multiset of premises:

  repeat: count every vertex pair over all premises; take the most frequent
  (ties: smallest pair); if it occurs in k >= MIN_USES premises, add the rule and
  substitute it everywhere; else stop.

Byte ruler (same units as organisms.nbytes): a rule costs 3 bytes (a length byte and
two vertex ids), and a premise costs one byte per stored vertex. A rule used k times
saves k bytes and costs 3, so MIN_USES = 4 is the smallest k that saves.

Factoring is LOSSLESS. Predictions, welds and retractions still use the flat premise
masks; only storage changes. A factored arm can differ from its flat twin only
through the byte cap (fewer evictions). tests/test_e1b.py checks both properties:
uncapped endpoints identical, bytes strictly lower.
"""
from collections import Counter
from itertools import combinations
from typing import Iterable, Tuple

from ..world import bits

MIN_USES = 4
RULE_BYTES = 3


def factorize(premises: Iterable[int]):
    """Return (seqs, rules, ops): the stored vertex sets, {rule_id: (a, b)}, and ops."""
    seqs = [set(bits(p)) for p in premises]
    next_id = 1 << 16                # ids for rules; never collide with primitives
    rules, ops = {}, 0
    while True:
        counts = Counter()
        for s in seqs:
            if len(s) >= 2:
                for pair in combinations(sorted(s), 2):
                    counts[pair] += 1
                    ops += 1
        if not counts:
            break
        (a, b), k = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        if k < MIN_USES:
            break
        for s in seqs:
            ops += 1
            if a in s and b in s:
                s.discard(a)
                s.discard(b)
                s.add(next_id)
        rules[next_id] = (a, b)
        next_id += 1
    return seqs, rules, ops


def expand(seq, rules) -> int:
    """Flatten a stored vertex set back to a primitive mask (the lossless check)."""
    out, stack = 0, list(seq)
    while stack:
        v = stack.pop()
        if v in rules:
            stack.extend(rules[v])
        else:
            out |= 1 << v
    return out


def repair(premises: Iterable[int]) -> Tuple[int, int, int]:
    """Return (stored vertex count, rule count, ops) for the factored premises."""
    seqs, rules, ops = factorize(premises)
    return sum(len(s) for s in seqs), len(rules), ops


class FactorCache:
    """Memoize repair() on the sorted multiset of premises (premises change rarely)."""

    def __init__(self):
        self.key = None
        self.val = (0, 0, 0)

    def get(self, premises) -> Tuple[int, int, int]:
        key = tuple(sorted(premises))
        if key != self.key:
            self.key = key
            self.val = repair(key)
            return self.val
        return (self.val[0], self.val[1], 0)     # cached: no new ops
