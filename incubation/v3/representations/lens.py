"""lens.py — the representational transform family for Lens Genesis.

A LENS is a partition of a SUBSET of the primitive alphabet into 1..3 groups; the
remaining primitives are EXCLUDED (that is the information the representation
discards, and it is recorded). Applying a lens to a task changes the problem the
downstream machinery sees:

    original:   one reachability task over the full alphabet
    lensed:     a SEQUENCE of subtasks, one per group — reach the target on that
                group's discovered support, using only that group's primitives —
                solved by the UNCHANGED downstream engine (incubation/v2/runtime),
                solutions concatenated, and the concatenation verified by replay
                on the TRUE domain. The referee never changes.

Supports are DISCOVERED by metered execution (apply each primitive to probe states,
read which slots changed), never supplied. A lens is structurally valid only if its
groups' supports are pairwise disjoint on the probes; validity is a cheap metered
precheck, and even "valid" lenses remain subject to execution: a group that cannot
reach its subgoal exhausts its reachable set or its budget, and a lens whose
exclusions discard needed primitives simply fails its tasks. Aliasing is zero by
construction: no states are merged; soundness rests entirely on final replay.

The lens family deliberately contains qualitatively different transforms: full
factorizations, coarse partial factorizations, alphabet prunings (single-group
lenses = same joint problem over fewer primitives), under-powered groups, and
illegal exclusions. The census measures how rare the useful class is and where it
sits in the frozen canonical enumeration.
"""
from __future__ import annotations

import hashlib
import os
import sys

_V2 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "v2")
if _V2 not in sys.path:
    sys.path.insert(0, _V2)

from runtime import Meter, run_program           # noqa: E402  (v2 engine, unchanged)


# ── lens objects and enumeration ────────────────────────────────────────────────────

def lens_serial(groups):
    return "LENS[" + "|".join(".".join(g) for g in groups) + "]"


def canon(groups):
    return tuple(sorted(tuple(sorted(g)) for g in groups))


def _partitions(items, max_groups):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for part in _partitions(rest, max_groups):
        for i in range(len(part)):
            yield part[:i] + [[first] + part[i]] + part[i + 1:]
        if len(part) < max_groups:
            yield part + [[first]]


def enumerate_lenses(alphabet, max_groups=3):
    """All lenses over the alphabet, canonical (size, serial) order.
    size = number of primitives retained + number of groups."""
    out = []
    n = len(alphabet)
    for mask in range(1, 1 << n):
        subset = [alphabet[i] for i in range(n) if (mask >> i) & 1]
        for part in _partitions(subset, max_groups):
            g = canon(part)
            out.append(g)
    out = sorted(set(out), key=lambda g: (sum(len(x) for x in g) + len(g),
                                          lens_serial(g)))
    return out


def enumeration_sha(lenses):
    h = hashlib.sha256()
    for g in lenses:
        h.update(lens_serial(g).encode())
        h.update(b"\n")
    return h.hexdigest()[:16]


# ── application ─────────────────────────────────────────────────────────────────────

class SubView:
    """The domain as seen through one lens group: same states, filtered alphabet."""

    def __init__(self, domain, allowed):
        self._d = domain
        self._allowed = frozenset(allowed)
        self.pids = tuple(p for p in domain.pids if p in self._allowed)

    def succ(self, s):
        return [(p, t) for p, t in self._d.succ(s) if p in self._allowed]

    def pred(self, s):
        return [(p, t) for p, t in self._d.pred(s) if p in self._allowed]

    def apply(self, pid, s):
        return self._d.apply(pid, s)

    def decode(self, x):
        return tuple(x)


def discover_supports(domain, groups, probes, meter):
    """Executable support discovery: which slots does each group ever change on the
    probe states? Metered like any other execution."""
    sup = []
    for g in groups:
        slots = set()
        for pid in g:
            for s in probes:
                meter.charge(1)
                t = domain.apply(pid, s)
                slots.update(i for i, (a, b) in enumerate(zip(s, t)) if a != b)
        sup.append(frozenset(slots))
    return sup


def run_with_lens(domain, task, groups, downstream_prog, budget,
                  sub_budget_frac=0.45):
    """Solve a task through a lens. Returns a result record; never trusts itself —
    the concatenated word is replayed on the true domain at the end."""
    meter = Meter(budget)
    s = tuple(domain.decode(task["start"]))
    t = tuple(domain.decode(task["target"]))
    probes = [s, t]
    sup = discover_supports(domain, groups, probes, meter)
    for i in range(len(sup)):
        for j in range(i + 1, len(sup)):
            if sup[i] & sup[j]:
                return {"solved": False, "ops": meter.ops, "why": "support_overlap",
                        "sub_halts": []}
    cur = s
    words = []
    sub_halts = []
    for g, slots in zip(groups, sup):
        subgoal = tuple(t[i] if i in slots else cur[i] for i in range(len(cur)))
        if subgoal == cur:
            sub_halts.append("noop")
            continue
        view = SubView(domain, g)
        sub_task = {"start": cur, "target": subgoal}
        # per-subtask share enforced by temporarily lowering the shared meter's cap
        # (run_program honors the meter's budget, not its budget argument, when a
        # meter is supplied)
        cap = min(budget, meter.ops + int(budget * sub_budget_frac))
        if cap <= meter.ops:
            return {"solved": False, "ops": meter.ops, "why": "budget",
                    "sub_halts": sub_halts}
        meter.budget = cap
        r = run_program(view, sub_task, downstream_prog, cap, meter=meter)
        meter.budget = budget
        sub_halts.append(r["trace"]["halt"])
        if not r["solved"]:
            return {"solved": False, "ops": meter.ops,
                    "why": f"sub_failed_{r['trace']['halt']}",
                    "sub_halts": sub_halts}
        words.extend(r["word"])
        cur = subgoal
    if cur != t:
        return {"solved": False, "ops": meter.ops, "why": "residual_mismatch",
                "sub_halts": sub_halts}
    v = s
    for pid in words:
        meter.charge(1)
        v = domain.apply(pid, v)
    ok = v == t and meter.ops <= meter.budget
    return {"solved": ok, "ops": meter.ops, "word": words,
            "why": None if ok else "verify_or_budget", "sub_halts": sub_halts}
