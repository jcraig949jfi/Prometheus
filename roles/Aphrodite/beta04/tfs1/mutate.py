"""TFS-1 stochastic local mutator (typed subtree replacement / insertion / hoisting) and a minimal archive driver.

Every child is well-typed by construction (tested). Random subterms are drawn uniformly from the enumerator's typed
tables (size uniform in 1..max_fill among non-empty classes, then a uniform member), so the mutator and the enumerator
share ONE definition of the space, including library entries as extra typed operators.

Determinism: all randomness comes from a random.Random seeded by blake2b("TFS1/MUT/v0/<seed>/<slot>"); the same
(seed, slot, library, start set, policy) gives the same child sequence (tested). Charges: exactly 1 per child evaluated
on dev. A child rejected before evaluation (over max_size) is NOT evaluated and NOT charged; such rejections are
counted in 'rejected'.

The archive POLICY (which parent to expand, what to keep) is deliberately pluggable: the ATLAS lead owns meaningful
target-blind descriptors. Two trivial reference policies are provided: 'fixed' (parents always drawn from the start
set) and 'random' (every evaluated non-FAIL child is appended; parents uniform) -- a random-archive control shape.
"""
import hashlib
import random
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from . import core as C
from .enum import Enumerator


def rng_for(seed, slot: str) -> random.Random:
    h = hashlib.blake2b(("TFS1/MUT/v0/%s/%s" % (seed, slot)).encode(), digest_size=8).digest()
    return random.Random(int.from_bytes(h, "big"))


def replace_at(t, path: Tuple[int, ...], new):
    if not path:
        return new
    i = path[0]
    return t[:i] + (replace_at(t[i], path[1:], new),) + t[i + 1:]


class Mutator:
    OPS = ("replace", "insert", "hoist")

    def __init__(self, enumerator: Enumerator, max_fill: int = 3, max_size: int = 16,
                 weights: Sequence[float] = (1.0, 1.0, 1.0)):
        self.E = enumerator
        self.lib = enumerator.lib
        self.max_fill = max_fill
        self.max_size = max_size
        self.weights = list(weights)

    # ------------------------------------------------------------ sites
    def sites(self, t, T: str) -> List[Tuple[Tuple[int, ...], tuple, str, Tuple[str, ...]]]:
        """(path, subterm, type, ctx-names) for every node; lambda nodes carry their function type."""
        out = []

        def go(u, ty, ctx, path):
            out.append((path, u, ty, ctx))
            tag = u[0]
            if tag in ("int", "var", "xs", "hole"):
                return
            if tag == "lam":
                k, bt = C.FN_SHAPE[ty]
                go(u[2], bt, ctx + C.bind_names(k, ctx), path + (2,))
                return
            if tag == "app":
                ft = C.type_of(u[1], len(ctx), None, self.lib)
                go(u[1], ft, ctx, path + (1,))
                for i, a in enumerate(u[2:], start=2):
                    go(a, C.INT, ctx, path + (i,))
                return
            ats = C.PRIM_SIGS[tag][0] if tag in C.PRIM_SIGS else self.lib.sig(tag)[0]
            for i, (a, at) in enumerate(zip(u[1:], ats), start=1):
                go(a, at, ctx, path + (i,))
        go(t, T, (), ())
        return out

    # ------------------------------------------------------------ random terms
    def random_term(self, T: str, ctx: Tuple[str, ...], rng: random.Random, max_n: Optional[int] = None):
        max_n = max_n or self.max_fill
        sizes = [n for n in range(1, max_n + 1) if self.E._arg_count(T, ctx, n) > 0]
        if not sizes:
            return None
        n = sizes[rng.randrange(len(sizes))]
        lst = self.E.arg_terms(T, ctx, n)
        return lst[rng.randrange(len(lst))][0]

    # ------------------------------------------------------------ operators
    def _replace(self, t, site, rng):
        path, u, ty, ctx = site
        new = self.random_term(ty, ctx, rng)
        return None if new is None else replace_at(t, path, new)

    def _insert(self, t, site, rng):
        path, u, ty, ctx = site
        if ty not in C.VALUE_TYPES:
            return None
        cands = []
        for name, ats, rt in self.E.by_ret[ty]:
            for i, at in enumerate(ats):
                if at == ty:
                    cands.append((name, ats, i))
        if not cands:
            return None
        name, ats, pos = cands[rng.randrange(len(cands))]
        args = []
        for i, at in enumerate(ats):
            if i == pos:
                args.append(u)
            else:
                a = self.random_term(at, ctx, rng, max(1, self.max_fill - 1))
                if a is None:
                    return None
                args.append(a)
        return replace_at(t, path, (name,) + tuple(args))

    def _hoist(self, t, site, rng):
        path, u, ty, ctx = site
        if ty not in C.VALUE_TYPES:
            return None
        desc = []

        def go(v, vty, top):
            if not top and vty == ty:
                desc.append(v)
            tag = v[0]
            if tag in ("int", "var", "xs", "hole", "lam", "app"):
                return                      # never cross a binder: descendants keep the same context
            ats = C.PRIM_SIGS[tag][0] if tag in C.PRIM_SIGS else self.lib.sig(tag)[0]
            for a, at in zip(v[1:], ats):
                if at in C.VALUE_TYPES:
                    go(a, at, False)
        go(u, ty, True)
        if not desc:
            return None
        return replace_at(t, path, desc[rng.randrange(len(desc))])

    def mutate(self, t, T: str, rng: random.Random, tries: int = 20):
        """One child of t (root type T), or None after `tries` failed attempts (oversize / inapplicable)."""
        sites = self.sites(t, T)
        for _ in range(tries):
            op = rng.choices(self.OPS, weights=self.weights)[0]
            site = sites[rng.randrange(len(sites))]
            child = getattr(self, "_" + op)(t, site, rng)
            if child is None or C.size(child) > self.max_size:
                continue
            return child
        return None


def mutation_search(examples, root_type: str, starts: Sequence, budget: int, seed, slot: str,
                    enumerator: Enumerator, policy: str = "fixed", verify: Optional[Callable] = None,
                    on_eval: Optional[Callable] = None, full_outputs: bool = False, max_fill: int = 3,
                    max_size: int = 16, select: Optional[Callable] = None, update: Optional[Callable] = None) -> Dict:
    """Archive-based stochastic local search with exact charges.
    policy 'fixed' | 'random', or pass select(archive, rng) -> parent and update(archive, child, outs) callbacks.
    on_eval(charge, child_tree, outs_or_None, dev_ok) is called after every evaluation (descriptor hook).
    full_outputs=True evaluates every dev example (outputs vector for descriptors); still 1 charge per child."""
    ex = [(list(i), o) for i, o in examples]
    rng = rng_for(seed, slot)
    mut = Mutator(enumerator, max_fill=max_fill, max_size=max_size)
    lib = enumerator.lib
    archive = [s if isinstance(s, tuple) else C.parse(s) for s in starts]
    C.U[0] = C.U[1] = 0
    charges = rejected = verify_evals = 0
    false_hits = []
    while charges < budget:
        parent = select(archive, rng) if select else archive[rng.randrange(len(archive))]
        child = mut.mutate(parent, root_type, rng)
        if child is None:
            rejected += 1
            if rejected > 100 * (budget + 1):
                break
            continue
        fn = C.compile_term(child, lib, None, swap=lib is not None)
        charges += 1
        outs = None
        if full_outputs:
            outs = [C.run(fn, i) for i, _o in ex]
            ok = all(C.same_value(v, o) for v, (_i, o) in zip(outs, ex))
        else:
            ok = C.check_dev(fn, ex)
        if on_eval is not None:
            on_eval(charges, child, outs, ok)
        if ok:
            good = True
            if verify is not None:
                verify_evals += 1
                u = (C.U[0], C.U[1])
                good = verify(child)
                C.U[0], C.U[1] = u
            if good:
                return {"hit": True, "hit_charge": charges, "program": C.to_str(child), "charges": charges,
                        "budget": budget, "censored": False, "units_expanded": C.U[0], "units_promoted": C.U[1],
                        "rejected": rejected, "verify_evals": verify_evals, "false_hits": false_hits,
                        "archive_size": len(archive)}
            false_hits.append({"charge": charges, "program": C.to_str(child)})
        if update is not None:
            update(archive, child, outs)
        elif policy == "random":
            if outs is None or not all(v == C.FAIL for v in outs):
                archive.append(child)
    return {"hit": False, "hit_charge": None, "program": None, "charges": charges, "budget": budget, "censored": True,
            "units_expanded": C.U[0], "units_promoted": C.U[1], "rejected": rejected, "verify_evals": verify_evals,
            "false_hits": false_hits, "archive_size": len(archive)}
