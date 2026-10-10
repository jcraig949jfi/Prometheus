"""TFS-1 typed bottom-up enumeration by size, in a keyed common-random-number order, with exact charges.

ORDER. Candidates of the root type are walked size class by size class (size 1, 2, ...; core.size). Inside a size
class the order is ascending  key(seed, slot, canonical_text)  where

    key = int(blake2b("TFS1/ORDER/v0/<seed>/<slot>/<canonical text>", digest_size=8))

(ties, probability ~n^2/2^65, broken by the canonical text). The key depends only on (seed, slot, term): never on the
library, its entry order, the arm or the generation order. Hence (fair.py's guarantees carried over):
  - byte-identical libraries walk identical sequences;
  - two libraries keep every SHARED term in the same relative order within a size class;
  - permuting library entries changes nothing (ops are sorted by name, entries are content-addressed).

CHARGES. Exactly 1 search charge per candidate program evaluated on dev (evaluation stops at the first wrong/FAIL dev
example; that is still 1 charge). Test-set verification of a dev hit is NOT a search charge (counted separately as
verify_evals). Execution units of every evaluated candidate are summed in both ledgers (core.U).

SPACE. Every well-typed term of the contract (literals 0 1 2 3, xs, lambda variables, all 29 base primitives and every
library entry as an extra typed operator; function arguments are lambdas) is enumerated, with ONE optional
restriction: commutative canonicalisation (comm_canon=True, default). For add mul gcd eq and or only the argument order
with (size, text)(arg0) <= (size, text)(arg1) is generated. Under strict, FAIL-absorbing semantics both orders have
identical value, FAIL behaviour and unit counts, so no behaviour is lost; the canonical choice is library-independent.
No observational-equivalence pruning is performed (OPEN DECISION D4).
"""
import hashlib
import heapq
import itertools
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from . import core as C

CHUNK = 1_000_000        # max candidates materialised at once by the keyed walk


def compositions(n: int, m: int):
    """All m-tuples of positive ints summing to n (lexicographic)."""
    if m == 1:
        if n >= 1:
            yield (n,)
        return
    for first in range(1, n - m + 2):
        for rest in compositions(n - first, m - 1):
            yield (first,) + rest


def order_key(seed, slot: str, text: str) -> int:
    return int.from_bytes(hashlib.blake2b(("TFS1/ORDER/v0/%s/%s/%s" % (seed, slot, text)).encode(),
                                          digest_size=8).digest(), "big")


def canon_comm(t, names: Tuple[str, ...] = ()):
    """Reorder commutative arguments to the enumerator's canonical order ((size, text) ascending)."""
    tag = t[0]
    if tag in ("int", "var", "xs", "hole"):
        return t
    if tag == "lam":
        bn = C.bind_names(t[1], names)
        return ("lam", t[1], canon_comm(t[2], names + bn))
    args = [canon_comm(a, names) for a in t[1:]]
    if tag in C.COMMUTATIVE:
        args.sort(key=lambda a: (C.size(a), C.to_str(a, names)))
    return (tag,) + tuple(args)


class Enumerator:
    def __init__(self, library=None, literals: Sequence[int] = C.LITERALS, comm_canon: bool = True):
        self.lib = library if (library is not None and len(library) > 0) else None
        self.literals = tuple(literals)
        self.comm = comm_canon
        ops = [(n, ats, rt) for n, (ats, rt) in sorted(C.PRIM_SIGS.items())]
        if self.lib is not None:
            ops += [(i,) + self.lib.sig(i) for i in self.lib.ids()]
        ops.sort(key=lambda o: o[0])
        self.ops = ops
        self.by_ret = {T: [o for o in ops if o[2] == T] for T in C.VALUE_TYPES}
        self._tab: Dict[Tuple, List] = {}
        self._fn: Dict[Tuple, List] = {}
        self._cnt: Dict[Tuple, int] = {}
        self.cache: Dict[int, object] = {}
        self.swap = self.lib is not None

    # ------------------------------------------------------------ tables
    def terms(self, T: str, ctx: Tuple[str, ...], n: int) -> List[Tuple[tuple, str]]:
        """All canonical terms of type T in context ctx (tuple of in-scope binder names) of size n, as (tree, text),
        sorted by text. Memoised."""
        key = (T, ctx, n)
        r = self._tab.get(key)
        if r is None:
            r = list(self._gen(T, ctx, n))
            r.sort(key=lambda p: p[1])
            self._tab[key] = r
        return r

    def arg_terms(self, at: str, ctx: Tuple[str, ...], n: int) -> List[Tuple[tuple, str]]:
        if at in C.VALUE_TYPES:
            return self.terms(at, ctx, n)
        key = (at, ctx, n)
        r = self._fn.get(key)
        if r is None:
            k, bt = C.FN_SHAPE[at]
            bn = C.bind_names(k, ctx)
            bodies = self.terms(bt, ctx + bn, n)
            if k == 1:
                pre = "(lam %s " % bn[0]
                r = [(("lam", 1, b), pre + s + ")") for b, s in bodies]
            else:
                pre = "(lam %s (lam %s " % bn
                r = [(("lam", 2, b), pre + s + "))") for b, s in bodies]
            self._fn[key] = r
        return r

    def _leaves(self, T, ctx):
        out = []
        if T == C.INT:
            out += [(("int", v), str(v)) for v in self.literals]
            out += [(("var", len(ctx) - 1 - p), ctx[p]) for p in range(len(ctx))]
        elif T == C.LIST:
            out.append((("xs",), "xs"))
        for name, ats, rt in self.by_ret[T]:
            if not ats:
                out.append(((name,), "(%s)" % name))
        return out

    def _gen(self, T: str, ctx: Tuple[str, ...], n: int):
        if n == 1:
            yield from self._leaves(T, ctx)
            return
        rem = n - 1
        for name, ats, rt in self.by_ret[T]:
            m = len(ats)
            if m == 0 or rem < m:
                continue
            comm = self.comm and name in C.COMMUTATIVE
            pre = "(" + name + " "
            for comp in compositions(rem, m):
                if comm and comp[0] > comp[1]:
                    continue
                lists = [self.arg_terms(at, ctx, s) for at, s in zip(ats, comp)]
                if not all(lists):
                    continue
                if m == 1:
                    for a, sa in lists[0]:
                        yield (name, a), pre + sa + ")"
                elif m == 2:
                    l0, l1 = lists
                    if comm and comp[0] == comp[1]:
                        for i in range(len(l0)):
                            a, sa = l0[i]
                            p = pre + sa + " "
                            for b, sb in l1[i:]:
                                yield (name, a, b), p + sb + ")"
                    else:
                        for a, sa in l0:
                            p = pre + sa + " "
                            for b, sb in l1:
                                yield (name, a, b), p + sb + ")"
                else:
                    for combo in itertools.product(*lists):
                        yield (name,) + tuple(c[0] for c in combo), pre + " ".join(c[1] for c in combo) + ")"

    def _gen_trees(self, T: str, ctx: Tuple[str, ...], n: int):
        """Exactly _gen's sequence, trees only (no text): used by the chunked keyed walk (tested equal)."""
        if n == 1:
            for t, _s in self._leaves(T, ctx):
                yield t
            return
        rem = n - 1
        for name, ats, rt in self.by_ret[T]:
            m = len(ats)
            if m == 0 or rem < m:
                continue
            comm = self.comm and name in C.COMMUTATIVE
            for comp in compositions(rem, m):
                if comm and comp[0] > comp[1]:
                    continue
                lists = [self.arg_terms(at, ctx, s) for at, s in zip(ats, comp)]
                if not all(lists):
                    continue
                if m == 1:
                    for a, _sa in lists[0]:
                        yield (name, a)
                elif m == 2:
                    l0 = [a for a, _s in lists[0]]
                    l1 = [b for b, _s in lists[1]]
                    if comm and comp[0] == comp[1]:
                        for i in range(len(l0)):
                            a = l0[i]
                            for b in l1[i:]:
                                yield (name, a, b)
                    else:
                        for a in l0:
                            for b in l1:
                                yield (name, a, b)
                else:
                    for combo in itertools.product(*[[c[0] for c in lst] for lst in lists]):
                        yield (name,) + combo

    def count(self, T: str, ctx: Tuple[str, ...], n: int) -> int:
        """Exact class size by dynamic programming (no materialisation); equals len(terms(T, ctx, n)) (tested)."""
        key = (T, ctx, n)
        r = self._cnt.get(key)
        if r is not None:
            return r
        if n == 1:
            r = len(self._leaves(T, ctx))
        else:
            r = 0
            rem = n - 1
            for name, ats, rt in self.by_ret[T]:
                m = len(ats)
                if m == 0 or rem < m:
                    continue
                comm = self.comm and name in C.COMMUTATIVE
                for comp in compositions(rem, m):
                    if comm and comp[0] > comp[1]:
                        continue
                    cs = [self._arg_count(at, ctx, s) for at, s in zip(ats, comp)]
                    if comm and comp[0] == comp[1]:
                        r += cs[0] * (cs[0] + 1) // 2
                    else:
                        p = 1
                        for c in cs:
                            p *= c
                        r += p
        self._cnt[key] = r
        return r

    def _arg_count(self, at, ctx, n):
        if at in C.VALUE_TYPES:
            return self.count(at, ctx, n)
        k, bt = C.FN_SHAPE[at]
        return self.count(bt, ctx + C.bind_names(k, ctx), n)

    def cumulative(self, T: str, upto: int) -> int:
        return sum(self.count(T, (), n) for n in range(1, upto + 1))

    # ------------------------------------------------------------ keyed order
    def _class_iter(self, T, n):
        key = (T, (), n)
        if key in self._tab:
            return iter(self._tab[key])
        return self._gen(T, (), n)

    def keyed_class(self, T: str, n: int, seed, slot: str, limit: Optional[int] = None) -> List[Tuple[int, tuple]]:
        """The first `limit` members (all if None) of size class n in keyed order, as a list of (key, tree)."""
        return list(self.keyed_iter(T, n, seed, slot, limit))

    def keyed_iter(self, T: str, n: int, seed, slot: str, limit: Optional[int] = None, chunk: int = CHUNK):
        """Lazily yield (key, tree) for size class n in keyed order, at most `limit` items.
        Memory is bounded by `chunk` items: a large class is walked in key-range chunks; each chunk regenerates the
        class (deterministically) and keeps only the members whose key falls in the chunk's range. The ORDER is
        identical to a full sort by (key, text) (tested)."""
        pre = "TFS1/ORDER/v0/%s/%s/" % (seed, slot)
        b2 = hashlib.blake2b
        frombytes = int.from_bytes

        def keyed():
            for t, s in self._class_iter(T, n):
                yield (frombytes(b2((pre + s).encode(), digest_size=8).digest(), "big"), s, t)
        total = self.count(T, (), n)
        m = total if limit is None else min(limit, total)
        if m <= 0:
            return
        if total <= chunk:
            for k, s, t in sorted(keyed(), key=lambda z: (z[0], z[1]))[:m]:
                yield k, t
            return
        if m <= chunk:
            for k, s, t in heapq.nsmallest(m, keyed(), key=lambda z: (z[0], z[1])):
                yield k, t
            return
        import numpy as np
        memo = (T, (), n) in self._tab
        keys = np.fromiter((frombytes(b2((pre + s).encode(), digest_size=8).digest(), "big")
                            for _t, s in self._class_iter(T, n)), dtype=np.uint64, count=total)
        order = np.argsort(keys, kind="stable")          # generation indices in key order
        ks = keys[order]
        if bool(np.any(ks[1:] == ks[:-1])):
            # a 64-bit key collision inside the class (p ~ n^2 / 2^65): fall back to the exact (key, text) order
            del keys, order, ks
            yield from self._keyed_ranges(T, n, keyed, m, chunk)
            return
        del ks

        def trees():
            if memo:
                return (t for t, _s in self._tab[(T, (), n)])
            return self._gen_trees(T, (), n)
        emitted = 0
        for start in range(0, m, chunk):
            idx = order[start:min(start + chunk, m)]
            mask = np.zeros(total, dtype=np.uint8)
            mask[idx] = 1
            picked = list(itertools.compress(trees(), mask.tobytes()))    # generation order
            pos = np.searchsorted(np.sort(idx), idx)                       # key order -> picked position
            for g, p in zip(idx.tolist(), pos.tolist()):
                yield int(keys[g]), picked[p]
                emitted += 1
            del picked, mask

    def _keyed_ranges(self, T, n, keyed, m, chunk):
        """Exact (key, text) order by key-range chunks (collision fallback; regenerates text each chunk)."""
        import numpy as np
        total = self.count(T, (), n)
        keys = np.sort(np.fromiter((z[0] for z in keyed()), dtype=np.uint64, count=total))
        emitted, start, lo = 0, 0, int(keys[0])
        while emitted < m:
            nxt = start + chunk
            hi = int(keys[nxt]) if nxt < total else None
            part = [z for z in keyed() if z[0] >= lo and (hi is None or z[0] < hi)]
            part.sort(key=lambda z: (z[0], z[1]))
            for k, s, t in part:
                yield k, t
                emitted += 1
                if emitted >= m:
                    return
            if hi is None:
                return
            start += len(part)
            lo = hi

    def compile_root(self, t):
        """Compile a root candidate. Children are table objects (alive), so their closures are cached by id; the
        transient root itself is never cached."""
        if t[0] in ("int", "var", "xs", "hole") or len(t) == 1:
            return C.compile_term(t, self.lib, None, self.swap)
        cache = self.cache
        kids = t[1:]
        for a in kids:
            if id(a) not in cache:
                C.compile_term(a, self.lib, cache, self.swap)
        tmp = dict.fromkeys(())  # root compiled with a throwaway view: children found in the shared cache
        return C.compile_term(t, self.lib, _RootCache(cache, tmp), self.swap)

    # ------------------------------------------------------------ search
    def search(self, examples, root_type: str, seed, slot: str, budget: int, max_size: int = 10,
               verify: Optional[Callable] = None, max_hits: int = 1, trace: Optional[list] = None) -> Dict:
        """Walk the keyed order until `max_hits` hits or `budget` charges. A HIT is a candidate correct on every dev
        example and, if verify is given, accepted by verify(tree) (e.g. all test examples); dev-correct candidates
        rejected by verify are recorded as false_hits and the walk continues.
        trace: optional list receiving (charge, text) for every evaluated candidate (tests/diagnostics only)."""
        examples = [(list(i), o) for i, o in examples]
        C.U[0] = C.U[1] = 0
        charges = 0
        verify_evals = 0
        hits, false_hits = [], []
        complete_through = 0
        for n in range(1, max_size + 1):
            remaining = budget - charges
            if remaining <= 0:
                break
            total = self.count(root_type, (), n)
            if total == 0:
                complete_through = n
                continue
            walked = 0
            for _k, t in self.keyed_iter(root_type, n, seed, slot, limit=remaining):
                walked += 1
                fn = self.compile_root(t)
                charges += 1
                if trace is not None:
                    trace.append((charges, C.to_str(t)))
                if C.check_dev(fn, examples):
                    ok = True
                    if verify is not None:
                        verify_evals += 1
                        u = (C.U[0], C.U[1])
                        ok = verify(t)
                        C.U[0], C.U[1] = u
                    rec = {"charge": charges, "program": C.to_str(t), "size": n}
                    if ok:
                        hits.append(rec)
                        if len(hits) >= max_hits:
                            return self._result(True, hits, false_hits, charges, budget, verify_evals,
                                                complete_through, n)
                    else:
                        false_hits.append(rec)
            if walked == total:
                complete_through = n
        return self._result(bool(hits), hits, false_hits, charges, budget, verify_evals, complete_through, None)

    def _result(self, hit, hits, false_hits, charges, budget, verify_evals, complete_through, hit_size):
        return {"hit": hit, "hit_charge": hits[0]["charge"] if hits else None,
                "program": hits[0]["program"] if hits else None, "hits": hits, "false_hits": false_hits,
                "charges": charges, "budget": budget, "censored": not hit,
                "units_expanded": C.U[0], "units_promoted": C.U[1], "verify_evals": verify_evals,
                "complete_through_size": complete_through,
                "library_entries": len(self.lib) if self.lib else 0}

    # ------------------------------------------------------------ static rank
    def rank_of(self, t, root_type: str, seed, slot: str) -> Optional[int]:
        """1-based position of term t (comm-canonicalised) in the keyed walk, or None if t is not in the space."""
        t = canon_comm(t) if self.comm else t
        s = C.to_str(t)
        n = C.size(t)
        k = order_key(seed, slot, s)
        before = self.cumulative(root_type, n - 1)
        pre = "TFS1/ORDER/v0/%s/%s/" % (seed, slot)
        b2 = hashlib.blake2b
        within, found = 0, False
        for _t, s2 in self._class_iter(root_type, n):
            k2 = int.from_bytes(b2((pre + s2).encode(), digest_size=8).digest(), "big")
            if s2 == s:
                found = True
            elif (k2, s2) < (k, s):
                within += 1
        return before + within + 1 if found else None


class _RootCache(dict):
    """Read-through view of the shared closure cache that never stores (so a transient root is never cached)."""

    def __init__(self, shared, _tmp):
        super().__init__()
        self.shared = shared

    def get(self, k, default=None):
        return self.shared.get(k, default)

    def __setitem__(self, k, v):
        pass


def make_verifier(test_examples, lib=None) -> Callable:
    """verify(tree) -> True iff the program is correct on every test example (not a search charge)."""
    ex = [(list(i), o) for i, o in test_examples]

    def verify(t):
        fn = C.compile_term(t, lib, None, swap=C.has_call(t))
        return C.check_dev(fn, ex)
    return verify
