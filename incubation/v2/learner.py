"""learner.py — the architecture-construction learner (A2), the v1-macro control (A1),
and the failure-driven revision machinery.

Everything here operates through the runtime's Adapter interface: tasks, generator
calls, replays. No world identities, no witnesses, no access to the omniscient ceiling.
tests/ enforce the import boundary (this module may import dsl and runtime only).

CONSTRUCTION (A2). The learner starts with the fixed forward baseline. When its own
experience shows the preregistered pathology (budget failures), it evaluates candidate
search programs BY EXECUTION on the very tasks it failed, under a probe meter. For the
admission phase the 1-stage space is exhaustively metered and the cheapest
probe-solving program wins. For the recursion phase (dE) exhaustion is impossible
(401,956 SEQ programs), so selection is first-admissible-in-order — and the ORDER is
the thing prior learning changes: a naive learner walks the frozen canonical
enumeration; an experienced learner walks its library neighborhood first (library
members, SEQ pairs over the library, SEQ pairs over one-token mutants). Acquisition
cost = candidates evaluated + metered ops until the first admissible program.

REVISION. Anomalous runs (budget failure where recent experience predicted success)
trigger a failure audit: replaying claimed backward edges. A routing predicate is then
fitted over cheap executable task features, choosing the cheapest feature that exactly
separates anomalous from clean evidence. The routed operator pays for its own probe.
"""
from __future__ import annotations

from dsl import BASELINE, HALTS, OBS, OPS, SPECS, enumerate_stage, serial, size
from runtime import Adapter, Meter, run_program

PROBE_BUDGET = 20_000
TRIGGER_MIN_TASKS = 10
TRIGGER_FAIL_FRAC = 0.30


# ── A2: experience, trigger, construction ───────────────────────────────────────────

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
    return n >= TRIGGER_MIN_TASKS and fails / n >= TRIGGER_FAIL_FRAC, \
        {"n": n, "budget_failures": fails,
         "frac": round(fails / max(n, 1), 4)}


def evaluate_candidate(prog, probes, probe_budget=PROBE_BUDGET):
    total = 0
    ok = True
    for dom, task in probes:
        r = run_program(dom, task, prog, probe_budget)
        total += r["ops"]
        if not r["solved"]:
            ok = False
    return ok, total


def construct_exhaustive(probes, probe_budget=PROBE_BUDGET):
    """Admission-phase construction: meter EVERY 1-stage program on the learner's own
    failed tasks; the cheapest solver of all probes wins (ties: size, serial)."""
    best = None
    n_cands = 0
    total_ops = 0
    n_admissible = 0
    for prog in enumerate_stage():
        n_cands += 1
        ok, ops = evaluate_candidate(prog, probes, probe_budget)
        total_ops += ops
        if ok:
            n_admissible += 1
            key = (ops, size(prog), serial(prog))
            if best is None or key < best[0]:
                best = (key, prog)
    info = {"candidates": n_cands, "construction_ops": total_ops,
            "n_admissible": n_admissible,
            "winner_probe_ops": best[0][0] if best else None}
    return (best[1] if best else None), info


def construct_first_admissible(order, probes, max_candidates,
                               probe_budget=PROBE_BUDGET):
    """Recursion-phase construction: first admissible candidate in the given order."""
    n_cands = 0
    total_ops = 0
    for prog in order:
        if n_cands >= max_candidates:
            break
        n_cands += 1
        ok, ops = evaluate_candidate(prog, probes, probe_budget)
        total_ops += ops
        if ok:
            return prog, {"candidates": n_cands, "construction_ops": total_ops,
                          "found": True}
    return None, {"candidates": n_cands, "construction_ops": total_ops,
                  "found": False}


def mutants(stage_prog):
    """One-token edits of a STAGE program (deterministic order)."""
    _t, procs, sched, halt = stage_prog
    out = []
    for h in HALTS:
        if h != halt:
            out.append(("STAGE", procs, sched, h))
    scheds = [("ONLY", 0), ("ONLY", 1), ("ALT",)] + \
             [("IF", a, op, b) for a in OBS for op in OPS for b in OBS]
    for s in scheds:
        if s != sched and (len(procs) == 2 or s == ("ONLY", 0)):
            out.append(("STAGE", procs, s, halt))
    if len(procs) == 2:
        for i in range(2):
            for spec in SPECS:
                if spec != procs[i]:
                    np = tuple(sorted([procs[1 - i], spec]))
                    out.append(("STAGE", np, sched, halt))
    seen = set()
    uniq = []
    for p in out:
        s = serial(p)
        if s not in seen:
            seen.add(s)
            uniq.append(p)
    return uniq


def naive_order(seq_space):
    """Canonical order: the frozen 1-stage enumeration, then the SEQ enumeration."""
    return list(enumerate_stage()) + list(seq_space)


def experienced_order(library_stages, seq_space):
    """Library-neighborhood-first order, then the canonical order as fallback."""
    lib = list(library_stages)
    out = list(lib)
    out += [("SEQ", a, b) for a in lib for b in lib]
    pool = []
    for p in lib:
        pool.extend(mutants(p))
    out += [("SEQ", a, b) for a in lib for b in pool[:20]]
    out += [("SEQ", a, b) for a in pool[:20] for b in lib]
    seen = set()
    uniq = []
    for p in out:
        s = serial(p)
        if s not in seen:
            seen.add(s)
            uniq.append(p)
    return uniq + naive_order(seq_space)


# ── revision: failure audit + routed operator ───────────────────────────────────────

ROUTE_FEATURES = ("AUDIT_T", "AUDIT_S", "NPRED_T", "NPRED_S")


def feature_value(domain, task, feat, meter):
    """Cheap executable task feature, paid through the meter."""
    ad = Adapter(domain, task, meter)
    anchor = ad.target if feat.endswith("_T") else ad.start
    cands = ad.pred(anchor)
    if feat.startswith("NPRED"):
        return len(cands)
    bad = 0
    for pid, c in cands:
        if ad.replay([pid], c) != anchor:
            bad += 1
    return bad


def learn_router(bad_evidence, good_evidence):
    """bad/good evidence: lists of (domain, task). Chooses the cheapest feature with a
    threshold that exactly separates bad (route away) from good (keep operator)."""
    for feat in ROUTE_FEATURES:
        m = Meter(10**9)
        bad_vals = [feature_value(d, t, feat, m) for d, t in bad_evidence]
        good_vals = [feature_value(d, t, feat, m) for d, t in good_evidence]
        thr = max(good_vals) if good_vals else 0
        if bad_vals and min(bad_vals) > thr:
            return {"feature": feat, "threshold": thr,
                    "learn_ops": m.ops,
                    "bad_range": [min(bad_vals), max(bad_vals)],
                    "good_range": [min(good_vals) if good_vals else None,
                                   max(good_vals) if good_vals else None]}
    return None


def run_operator(domain, task, op, budget, audit=False):
    """Execute an operator: a plain program, or a ROUTE wrapper that pays for its own
    feature probe and then dispatches."""
    if op[0] != "ROUTE":
        return run_program(domain, task, op, budget, audit=audit)
    _t, feat, thr, prog_bad, prog_good = op
    meter = Meter(budget)
    v = feature_value(domain, task, feat, meter)
    chosen = prog_bad if v > thr else prog_good
    r = run_program(domain, task, chosen, budget, audit=audit, meter=meter)
    r["routed_to"] = "fallback" if v > thr else "operator"
    r["route_feature_value"] = v
    return r
