"""guard.py — learning an applicability predicate from the concept's own runtime failures.

Evidence: states the solver attempted the concept from, labelled by executable outcome
(ok / failed-at-step-i). No world labels, no strata, no generator access.

Feature language (executable probes): probe words drawn from the concept's own prefixes
plus the single primitives; feature = slot j of the probed state; atoms compare with '<'
or '=='. For '<' atoms only the maximal threshold with zero false positives matters; for
'==' atoms only values never observed in ok states qualify. The learner searches for an
exact cover of the failures by a disjunction of at most 2 atoms, preferring cheaper
probes (fewer executions at guard-evaluation time), and falls back to the best
zero-false-positive partial cover if no exact one exists.

Probe executions during learning are counted through the supplied apply() callable.
"""
from __future__ import annotations

from .concept import Guard


def learn_guard(word, ev_ok, ev_fail, apply_fn, prim_ids):
    """word: concept's word (pids). ev_ok: [state]. ev_fail: [(state, fail_step)].
    apply_fn(pid, state) -> state|None (execution-counting). Returns (Guard|None, info)."""
    probes = [tuple(word[:i]) for i in range(len(word))]        # includes ()
    probes += [(p,) for p in prim_ids if (p,) not in probes]
    ok_states = list(ev_ok)
    fail_states = [s for s, _ in ev_fail]
    n_fail = len(fail_states)
    if not n_fail or not ok_states:
        return None, {"reason": "insufficient evidence",
                      "n_ok": len(ok_states), "n_fail": n_fail}

    execs = 0

    def feats(probe, states):
        nonlocal execs
        out = []
        for s in states:
            v = s
            for pid in probe:
                execs += 1
                v = apply_fn(pid, v)
                if v is None:
                    break
            out.append(None if v is None else v)
        return out

    atoms = []       # (atom, covered_fail_mask, probe_cost)
    full = (1 << n_fail) - 1
    for probe in probes:
        f_ok = feats(probe, ok_states)
        f_fail = feats(probe, fail_states)
        # a probe that fails on ANY ok state is unusable (probe-failure => predict fail)
        if any(v is None for v in f_ok):
            continue
        base_mask = 0
        for i, v in enumerate(f_fail):
            if v is None:                       # probe fails here => covered for free
                base_mask |= 1 << i
        for j in range(len(ok_states[0])):
            ok_vals = [v[j] for v in f_ok]
            c_max = min(ok_vals)
            mask = base_mask
            for i, v in enumerate(f_fail):
                if v is not None and v[j] < c_max:
                    mask |= 1 << i
            if mask:
                atoms.append(((probe, j, "<", c_max), mask, len(probe)))
            ok_set = set(ok_vals)
            fail_only = {v[j] for v in f_fail if v is not None} - ok_set
            for c in sorted(fail_only):
                mask = base_mask
                for i, v in enumerate(f_fail):
                    if v is not None and v[j] == c:
                        mask |= 1 << i
                atoms.append(((probe, j, "==", c), mask, len(probe)))
    atoms.sort(key=lambda a: (a[2], a[0][0], a[0][1], a[0][2], str(a[0][3])))

    info = {"n_ok": len(ok_states), "n_fail": n_fail, "n_atoms": len(atoms),
            "learn_execs": 0}
    # collect ALL exact covers of size 1 and 2, then pick the one with the lowest
    # worst-case evaluation cost (sum of probe lengths), so the guard is not only
    # correct but cheap to consult at search time
    covers = []
    for a, ma, ca in atoms:
        if ma == full:
            covers.append(([a], ca))
    # pair search over a structured pool: per (probe, slot), the threshold atom and the
    # widest equality atom. Equality atoms sharing a failing probe all inherit that
    # probe's base coverage, so a flat top-N by coverage floods with near-duplicates
    # and can evict the atoms every real cover needs.
    pool = {}
    for a, ma, ca in atoms:
        probe, j, op, _c = a
        key = (probe, j, op == "==")
        if key not in pool or bin(ma).count("1") > bin(pool[key][1]).count("1"):
            pool[key] = (a, ma, ca)
    wide = sorted(pool.values(), key=lambda a: (-bin(a[1]).count("1"), a[2]))
    for i, (a, ma, ca) in enumerate(wide):
        for b, mb, cb in wide[i + 1:]:
            if (ma | mb) == full:
                covers.append(([a, b], ca + cb))
    best = None
    if covers:
        covers.sort(key=lambda c: (c[1], len(c[0]),
                                   [(len(x[0]), x[0], x[1], x[2], str(x[3]))
                                    for x in c[0]]))
        best = covers[0][0]
    if best is None:
        # zero-false-positive partial cover: greedy best two
        atoms_by_cov = sorted(atoms, key=lambda a: (-bin(a[1]).count("1"), a[2]))
        if atoms_by_cov:
            a = atoms_by_cov[0]
            rest = sorted(atoms, key=lambda x: (-bin(x[1] & ~a[1]).count("1"), x[2]))
            best = [a[0]] + ([rest[0][0]] if rest and rest[0][1] & ~a[1] else [])
            covered = a[1] | (rest[0][1] if rest else 0)
            info["partial_cover_frac"] = bin(covered).count("1") / n_fail
        else:
            info["reason"] = "no admissible atoms"
            info["learn_execs"] = execs
            return None, info
    info["learn_execs"] = execs
    info["atoms"] = [[list(p), j, op, c] for (p, j, op, c) in best]
    guard = Guard(sorted(best, key=lambda a: len(a[0])))     # cheapest probe first
    return guard, info
