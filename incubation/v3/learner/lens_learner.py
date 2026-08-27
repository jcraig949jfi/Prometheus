"""lens_learner.py — the representation-construction learner (R3) and its revision.

Boundary discipline: this module may import the lens machinery and the v2 runtime
ONLY. It never imports the world families, never references the omniscient block
constants, and never sees witnesses or world identities. Its lens space comes from
`enumerate_lenses(domain.pids)` — the alphabet it can observe — and its evidence is
its own metered execution. tests/ enforce this statically.

TRIGGER (preregistered): representational search is licensed only by experienced
computational pathology — >= 30% budget failures over >= 10 tasks under the
learner's machinery (old representation + its granted search operator). A
no-pathology control world must never fire it.

CONSTRUCTION: exhaustive over the frozen lens enumeration — cheap metered validity
precheck (support disjointness on probe states), then metered probe-solving on the
learner's own FAILED tasks. Winner: solves all probes at minimum total ops (ties:
size, serial). For the recursion phase, exhaustion is impossible (millions of
lenses), so selection is first-admissible-in-order; a naive learner walks the frozen
canonical order, an experienced learner walks EXTENSIONS of its admitted lens first
— prior groups kept, prior exclusions kept excluded, only genuinely-new primitives
assigned — then falls back to the canonical order.

REVISION: anomalies (budget failure, or cost > 5x the clean solved median) trigger
revision; the repair is a TRY-CAP ROUTE learned from the learner's own clean-cost
statistics: attempt the lens under a cap of 10x the clean median; on failure, fall
back to the old representation with the remaining budget. No hidden world identity
is consulted anywhere.
"""
from __future__ import annotations

import os
import sys
from itertools import product

_REP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "representations")
if _REP not in sys.path:
    sys.path.insert(0, _REP)

from lens import Meter, discover_supports, enumerate_lenses, lens_serial, \
    run_program, run_with_lens                                       # noqa: E402

PROBE_BUDGET = 20_000
TRIGGER_MIN_TASKS = 10
TRIGGER_FAIL_FRAC = 0.30


def experience(domain, tasks, prog, budget):
    recs = []
    for task, _omni in tasks:
        r = run_program(domain, task, prog, budget)
        recs.append({"task": task, "solved": r["solved"], "ops": r["ops"],
                     "budget_exhausted": r.get("budget_exhausted", False)})
    return recs


def trigger_fired(recs):
    n = len(recs)
    fails = sum(1 for r in recs if r["budget_exhausted"])
    return (n >= TRIGGER_MIN_TASKS and fails / n >= TRIGGER_FAIL_FRAC,
            {"n": n, "budget_failures": fails, "frac": round(fails / max(n, 1), 4)})


def _precheck(domain, groups, probe_states):
    m = Meter(10 ** 9)
    sup = discover_supports(domain, groups, probe_states, m)
    for i in range(len(sup)):
        for j in range(i + 1, len(sup)):
            if sup[i] & sup[j]:
                return False, m.ops
    return True, m.ops


def evaluate(groups, probes, downstream, probe_budget=PROBE_BUDGET):
    total = 0
    ok = True
    for dom, task in probes:
        r = run_with_lens(dom, task, groups, downstream, probe_budget)
        total += r["ops"]
        if not r["solved"]:
            ok = False
    return ok, total


def construct_exhaustive(alphabet_domain, probes, downstream):
    """Admission construction: meter the ENTIRE frozen lens space on the learner's
    own failed tasks. Returns (winner_groups, info)."""
    lenses = enumerate_lenses(alphabet_domain.pids)
    p_states = [tuple(alphabet_domain.decode(probes[0][1]["start"])),
                tuple(alphabet_domain.decode(probes[0][1]["target"]))]
    best = None
    n_eval = 0
    total_ops = 0
    n_valid = 0
    n_admissible = 0
    for g in lenses:
        ok, pre_ops = _precheck(alphabet_domain, g, p_states)
        total_ops += pre_ops
        if not ok:
            continue
        n_valid += 1
        n_eval += 1
        solved, ops = evaluate(g, probes, downstream)
        total_ops += ops
        if solved:
            n_admissible += 1
            key = (ops, sum(len(x) for x in g) + len(g), lens_serial(g))
            if best is None or key < best[0]:
                best = (key, g)
    info = {"n_lenses": len(lenses), "n_valid": n_valid, "n_evaluated": n_eval,
            "n_admissible": n_admissible, "construction_ops": total_ops,
            "winner_probe_ops": best[0][0] if best else None}
    return (best[1] if best else None), info


def construct_first_admissible(order, probes, downstream, alphabet_domain,
                               probe_states, max_candidates):
    n = 0
    total_ops = 0
    for g in order:
        if n >= max_candidates:
            break
        n += 1
        ok, pre_ops = _precheck(alphabet_domain, g, probe_states)
        total_ops += pre_ops
        if not ok:
            continue
        solved, ops = evaluate(g, probes, downstream)
        total_ops += ops
        if solved:
            return g, {"candidates": n, "construction_ops": total_ops,
                       "found": True}
    return None, {"candidates": n, "construction_ops": total_ops, "found": False}


def extension_order(prior_groups, prior_alphabet, new_alphabet):
    """Extensions of an admitted lens: prior groups kept, prior exclusions kept
    excluded, each genuinely-new primitive assigned to (an existing group | a new
    group | excluded). Size-ordered (fewer retained first), then lexicographic."""
    covered = set(prior_alphabet)
    new_pids = [p for p in new_alphabet if p not in covered]
    n_slots = len(prior_groups) + 1                 # existing groups + one new
    assigns = sorted(product(range(n_slots + 1), repeat=len(new_pids)),
                     key=lambda a: (sum(1 for x in a if x < n_slots), a))
    seen = set()
    out = []
    for assign in assigns:
        groups = [list(g) for g in prior_groups] + [[]]
        for p, a in zip(new_pids, assign):
            if a < n_slots:
                groups[a].append(p)
        g = tuple(sorted(tuple(sorted(x)) for x in groups if x))
        s = lens_serial(g)
        if s not in seen:
            seen.add(s)
            out.append(g)
    return out


# ── revision: try-cap routing ───────────────────────────────────────────────────────

def learn_cap(clean_ops, factor=10):
    """The revision's learned content: a cost cap from the learner's own clean
    experience. clean_ops: lens ops on solved clean tasks."""
    clean_ops = sorted(clean_ops)
    med = clean_ops[len(clean_ops) // 2]
    return factor * med


def run_routed(domain, task, groups, cap, downstream, budget):
    """p0002: try the lens under the learned cap; on failure fall back to the old
    representation with the remaining budget. All on one meter-equivalent account
    (attempt ops + fallback ops are summed)."""
    attempt = run_with_lens(domain, task, groups, downstream, min(cap, budget))
    if attempt["solved"]:
        r = dict(attempt)
        r["routed_to"] = "lens"
        return r
    fb = run_program(domain, task, downstream, budget - attempt["ops"])
    return {"solved": fb["solved"], "ops": attempt["ops"] + fb["ops"],
            "word": fb["word"], "routed_to": "fallback",
            "attempt_ops": attempt["ops"], "why": attempt["why"],
            "budget_exhausted": fb.get("budget_exhausted", False)}
