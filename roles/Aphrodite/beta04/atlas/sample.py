"""Uniform sampling from TFS-1 size classes (no materialisation) and batched static ranks in the keyed CRN walk.

sample_uniform(E, T, ctx, n, rng): a uniformly random member of the enumerator's size-n class of type T (comm-canonical
space, exactly the set E.terms(T, ctx, n) enumerates). Method: pick the (operator, size composition) block with
probability proportional to its exact DP count, then sample arguments recursively. For a commutative operator whose
two argument sizes are equal the class holds unordered pairs {a, b} (a <= b by text, a == b allowed): a and b are drawn
independently and an off-diagonal pair is accepted with probability 1/2 (diagonal always), which makes every unordered
pair equally likely; the pair is then put in canonical (text) order. Tested against the materialised class.

ranks_of(E, terms, T, seed, slot): the 1-based keyed-walk positions of several terms at once (one pass per size class),
equal to Enumerator.rank_of for each term (tested).
"""
import bisect
import hashlib
from typing import Dict, List, Optional, Sequence

from tfs1 import core as C
from tfs1.enum import Enumerator, canon_comm, compositions, order_key


def _arg_sample(E: Enumerator, at: str, ctx, n: int, rng):
    if at in C.VALUE_TYPES:
        return sample_uniform(E, at, ctx, n, rng)
    k, bt = C.FN_SHAPE[at]
    return ("lam", k, sample_uniform(E, bt, ctx + C.bind_names(k, ctx), n, rng))


def sample_uniform(E: Enumerator, T: str, ctx, n: int, rng):
    total = E.count(T, ctx, n)
    if total == 0:
        return None
    if n == 1:
        leaves = E._leaves(T, ctx)
        return leaves[rng.randrange(len(leaves))][0]
    r = rng.randrange(total)
    rem = n - 1
    for name, ats, rt in E.by_ret[T]:
        m = len(ats)
        if m == 0 or rem < m:
            continue
        comm = E.comm and name in C.COMMUTATIVE
        for comp in compositions(rem, m):
            if comm and comp[0] > comp[1]:
                continue
            cs = [E._arg_count(at, ctx, s) for at, s in zip(ats, comp)]
            if comm and comp[0] == comp[1]:
                w = cs[0] * (cs[0] + 1) // 2
            else:
                w = 1
                for c in cs:
                    w *= c
            if r >= w:
                r -= w
                continue
            if comm and comp[0] == comp[1]:
                while True:
                    a = _arg_sample(E, ats[0], ctx, comp[0], rng)
                    b = _arg_sample(E, ats[1], ctx, comp[1], rng)
                    if a == b:
                        return (name, a, b)
                    if rng.random() < 0.5:
                        sa, sb = C.to_str(a, ctx), C.to_str(b, ctx)
                        return (name, a, b) if sa <= sb else (name, b, a)
            return (name,) + tuple(_arg_sample(E, at, ctx, s, rng) for at, s in zip(ats, comp))
    raise AssertionError("sampling fell off the class")


def ranks_of(E: Enumerator, terms: Sequence, T: str, seed, slot: str, max_class: int = 7_000_000) -> List[Dict]:
    """Static 1-based rank of each term in the keyed walk. Classes larger than max_class are not walked: the rank is
    then reported as the bracket (cumulative(n-1), cumulative(n)]."""
    out: List[Optional[Dict]] = [None] * len(terms)
    by_size: Dict[int, List] = {}
    for idx, t in enumerate(terms):
        tc = canon_comm(t) if E.comm else t
        s = C.to_str(tc)
        by_size.setdefault(C.size(tc), []).append((idx, s, order_key(seed, slot, s)))
    pre = "TFS1/ORDER/v0/%s/%s/" % (seed, slot)
    b2 = hashlib.blake2b
    for n, items in sorted(by_size.items()):
        before = E.cumulative(T, n - 1)
        total = E.count(T, (), n)
        if total > max_class:
            for idx, s, k in items:
                out[idx] = {"rank": None, "bracket": [before + 1, before + total], "size": n, "exact": False}
            continue
        targets = sorted((k, s) for _i, s, k in items)
        tset = {s for _i, s, _k in items}
        counts = [0] * len(targets)
        found = set()
        for _t, s2 in E._class_iter(T, n):
            k2 = int.from_bytes(b2((pre + s2).encode(), digest_size=8).digest(), "big")
            if s2 in tset:
                found.add(s2)
            # number of targets strictly greater than (k2, s2): each of them has this term before it
            j = bisect.bisect_right(targets, (k2, s2))
            if j < len(targets):
                counts[j] += 1
        # prefix sums: counts[j] = # class members with key between targets[j-1] and targets[j]
        # prefix sum at target j = class members strictly before targets[j] (a member equal to an earlier target
        # was counted in the next slot by bisect_right, so it is included; the target itself is not)
        acc, rank_by = 0, {}
        for j, (k, s) in enumerate(targets):
            acc += counts[j]
            rank_by[s] = acc
        for idx, s, k in items:
            if s not in found:
                out[idx] = {"rank": None, "size": n, "exact": True, "in_space": False}
            else:
                out[idx] = {"rank": before + rank_by[s] + 1, "size": n, "exact": True, "in_space": True}
    return out
