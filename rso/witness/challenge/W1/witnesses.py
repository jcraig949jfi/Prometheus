"""Behavioural witnesses for the W1 semantic edits (edits.json). Each takes the module under test `m` (original in
the baseline child, edited in the mutant child) and returns a small JSON-able value; the mutation runner records
repr(value) for both so NOT_EQUIVALENT is witnessed, not assumed. DATA FILE: frozen at the set commit.

No registered subject, arm-on-registered-seed, accuracy or retention number: synthetic traces with known decisions,
hand-wired carriers, seeds >= 5,000,000.
"""
import os
import shutil
import tempfile

import numpy as np

from ares import search as AR
from rso.witness.challenge.W1 import cases as C


def _tmp():
    return tempfile.mkdtemp(prefix="w1-witness-")


def e1(m):
    """m = rso.witness.evaluate. Decisions of 4 mid-window episodes (correct between the first and the last
    interrupt, abstain after the last): the registered rule (LAST interrupt) reads NO_ANSWER (0) for every episode."""
    seeds = C.witness_like()[:4]
    rec, arts = C.ret_node(C.DA, "S", "P-RET", C.mid_window, seeds)
    data = {}
    for listing, b in arts:
        if listing["dtype"] == "json":
            import json
            data[listing["role"]] = json.loads(b)
        else:
            data[listing["role"]] = np.frombuffer(b, dtype=listing["dtype"]).reshape(listing["shape"])
    return [int(d) for _r, d in m.episodes({"receipt": rec, "data": data})]


def e2(m):
    """m = rso.witness.ares_client. Does arm('S-NOPL', subject) leave the SUBJECT's plasticity intact?"""
    sub = C._leak_construction()
    before = bool(np.any(sub.R))
    m.arm("S-NOPL", sub)
    return {"subject_plastic_before": before, "subject_plastic_after": bool(np.any(sub.R))}


def e3(m):
    """m = rso.witness.evaluate. A bundle whose inventory carries one extra COMPLETED RECEIPT row (a node the launch
    ran but the manifest does not present): check_bundle's refusals."""
    root = _tmp()
    try:
        def extra(rows):
            hidden = dict(rows[1], run_id=C.LAUNCH_X + "/hidden-node", node_id="ares:hidden:RECUR:REPORT:W15")
            return rows + [hidden]
        nodes = C.full_plan(C.Spec())
        man, inv = C.write_bundle(os.path.join(root, "b"), nodes, rows_edit=extra)
        out = m.check_bundle(os.path.join(root, "b"), C.keeper((man, inv)), C.FIRST_CHECK)
        return sorted(out["refused"])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def e4(m):
    """m = rso.witness.ares_client. Do the runner's actions still equal ares.search.rollout's for the activation
    carrier on W15 (interrupt timing)? Reward is zeroed in the reference world as the suite does."""
    pop = m.recur_carrier()
    seeds = C.witness_like()[:3]
    w = AR.make_world("W15", "present")
    step = w.step

    def zero_step(a):
        obs, r, alive, info = step(a)
        return obs, np.zeros_like(r), alive, info
    w.step = zero_step
    _fit, traces = AR.rollout(pop, w, seeds, record=True)
    mine = m.run_episodes(pop, m.world("W15", "present"), seeds)
    return bool(np.array_equal(mine["actions"], np.stack(traces["actions"])))


def e5(m):
    """m = rso.witness.evaluate. DA's S/P-ERASE node with its oracle:regimes flipped (re-hashed consistently):
    check_bundle's refusals (the frozen evaluator refuses ORACLE_MISMATCH)."""
    root = _tmp()
    try:
        nodes = C.full_plan(C.Spec())
        idx = next(i for i, (rec, _a) in enumerate(nodes) if rec["arm"] == "S" and rec["predicate"] == "P-ERASE"
                   and rec["subject"]["genome_sha256"] == C.DA)
        rec, arts = nodes[idx]
        regs_listing, regs_bytes = arts[2]
        flipped = (np.frombuffer(regs_bytes, dtype=np.int8) ^ 1).astype(np.int8).reshape(regs_listing["shape"])
        new = C.array_artifact("oracle:regimes", flipped)
        import copy
        rec = copy.deepcopy(rec)
        rec["oracle"][0] = new[0]
        nodes[idx] = (rec, [arts[0], arts[1], new])
        man, inv = C.write_bundle(os.path.join(root, "b"), nodes)
        out = m.check_bundle(os.path.join(root, "b"), C.keeper((man, inv)), C.FIRST_CHECK)
        return sorted(out["refused"])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _exact(k, n=2048):
    """Balanced synthetic episodes [(r, decision)]: the first k correct, the rest wrong."""
    return [(i % 2, (i % 2) + 1 if i < k else 2 - (i % 2)) for i in range(n)]


def e6(m):
    """m = rso.witness.ruler. P-CAL with NULL at 1075 correct (inside the 1074-1077 zone: not shown below bound +
    delta, not POSITIVE), SHUF at 1000, POS at 1500: the registered one-sided margin says FAIL."""
    g = m.p_cal(_exact(1075), _exact(1000), _exact(1500))
    return {"value": g["value"], "witness_arm": (g["witness"] or {}).get("arm")}
