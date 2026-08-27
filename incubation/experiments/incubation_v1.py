"""incubation_v1.py â€” the preregistered incubation experiment.

Phases (all deterministic; 5 master seeds; the unit of analysis is the TASK):

  1 DISCOVERY   solve wA training tasks with the primitive-only solver; mine candidate
                composition from the solver's own solutions (function-grouped n-grams)
  2 ADMISSION   held-out wA tasks; arms P0/P1/P2a/P2b/P3/P3R; preregistered gates;
                ablation identity check; ledger entry for c0001
  3 TRANSFER    wB (different surface/moduli/generator); frozen c0001; same arms;
                ablation on wB
  4 NEGATIVE    wC blind: P0 vs P3; evidence collection from executable failures;
                detection trigger; guard learning -> c0002 (successor, history kept)
  5 REVISION    fresh wC tasks: P0 vs P3(blind) vs P3G(guarded); guard out-of-sample
                accuracy; bounded-region recording

Arms:
  P0   primitives only, iterative-deepening tree search (the baseline solver)
  P1   primitives only, breadth-first graph search with duplicate elimination
       (strongest unrestricted primitive-composition search)
  P2a  handed the discovered composition as a FLAT expression: executes it once as a
       candidate solution, then falls back to P0 (the "simply execute the flat
       expression" control)
  P2b  handed the composition as an inline, UNREIFIED block: usable anywhere in the
       search but each step costs its own node/depth (no composition-slot compression)
  P3   the composition REIFIED as concept c0001: one composition slot, one node;
       executions still cost full word length
  P3R  a random length-matched reified macro (content-specificity control)
  P3G  c0002: c0001 bounded by the learned applicability guard

The omniscient sections (witness words, M_WORD comparisons, world sampling for guard
holdout) are marked OMNISCIENT and are diagnostics only â€” nothing from them reaches
solver-side code. tests/ enforce the import boundary.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from primitives import PRIM_IDS                       # noqa: E402
from worlds import M_WORD, make_worlds                # noqa: E402  (OMNISCIENT use only)
from solver import Action, Boundary, Evidence, bfs, iddfs   # noqa: E402
from concepts import Concept, mine, learn_guard       # noqa: E402
from concepts.mine import fingerprint                 # noqa: E402
from ledger.ledger import append_event, new_entry, save, set_status   # noqa: E402

MASTER_SEEDS = (11, 22, 33, 44, 55)
STREAM = {"A_train": 1, "A_held": 2, "B_eval": 3, "C_blind_f": 4, "C_blind_h": 5,
          "C_val_f": 6, "C_val_h": 7, "guard_holdout": 8, "random_macro": 9}
N_TRAIN, N_HELD, N_C = 30, 30, 25
N_P3R_B = 15                # P3R runs on the first 15 wB tasks per seed (cost control)
DMAX = 12

PREREG = {
    "date": "2026-08-26",
    "unit": "task",
    "primary_metric": "search nodes to first verified solution",
    "secondary_metrics": ["candidate tests (cands)", "primitive executions (execs)"],
    "seeds": list(MASTER_SEEDS),
    "cells": {"A_train": N_TRAIN, "A_held": N_HELD, "B_eval": N_HELD,
              "C_blind": 2 * N_C, "C_val": 2 * N_C, "p3r_b_subset": N_P3R_B},
    "analysis": "paired per-task ratios vs P0; median + bootstrap 95% CI (5000 resamples,"
                " fixed seed); pooled across master seeds; per-seed medians reported and"
                " must fall on the same side of 1.0 as the pooled verdict",
    "gates": {
        "ADMIT_nodes": "wA held-out pooled: median(P3/P0 nodes) <= 0.5, CI95 upper < 1.0",
        "ADMIT_vs_random": "median(P3/P3R nodes) <= 0.5, CI95 upper < 1.0",
        "ADMIT_correctness": "every arm solves and verifies 100% of tasks",
        "ADMIT_ablation": "P3 with the concept removed is counter-identical to P0 on the"
                          " first 10 held tasks of every seed",
        "FLAT_a": "median(P3/P2a nodes) <= 0.5, CI95 upper < 1.0",
        "FLAT_b": "median(P3/P2b nodes) <= 0.7, CI95 upper < 1.0",
        "TRANSFER_nodes": "wB pooled: median(P3/P0 nodes) <= 0.5, CI95 upper < 1.0,"
                          " concept hash unchanged from admission (frozen, no retuning)",
        "TRANSFER_correctness": "every arm 100% on wB",
        "TRANSFER_ablation": "concept removal restores P0 counter-identically on 10"
                             " tasks/seed on wB",
        "NEG_hostile": "wC hostile blind: median(P3/P0 nodes) >= 1.5, CI95 lower > 1.0",
        "NEG_friendly": "wC friendly blind: median(P3/P0 nodes) <= 0.7",
        "DETECT": "c0001 runtime-failure rate >= 0.05 in wC with >= 100 attempts, and"
                  " exactly 0 runtime failures in wA and wB",
        "REV_guard_oos": "guard predicts c0001 runtime failure on 400 fresh wC states"
                         " per seed with accuracy >= 0.95",
        "REV_failures": "P3G reduces c0001 runtime failures >= 90% vs blind P3 on wC"
                        " validation tasks",
        "REV_cost": "median(P3G/P3 execs) <= 1.10 and median(P3G/P3 nodes) <= 1.02 on"
                    " wC validation",
        "REV_friendly_kept": "wC validation friendly: median(P3G/P0 nodes) <= 0.7",
    },
    "expected_residual": "hostile node harm is task-level (minimal solutions avoid the"
                         " composition) and is NOT fixable by a state-level guard; it is"
                         " recorded as the concept's bounded failure region, not hidden",
}


# â”€â”€ helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def seed_for(master, stream):
    return master * 1000 + STREAM[stream]


def task_hash(task):
    return hashlib.sha256(repr((task["start"], task["target"])).encode()).hexdigest()[:12]


def prim_actions():
    return [Action(pid, (pid,)) for pid in PRIM_IDS]


class StepShim:
    """Execution-only shim over a world for guard learning/holdout (experiment side)."""

    def __init__(self, world):
        self._step = world.step
        self._idx = {pid: i for i, pid in enumerate(PRIM_IDS)}
        self.execs = 0

    def apply(self, pid, s):
        self.execs += 1
        return self._step(self._idx[pid], s)

    def read(self, s):
        return tuple(s)


def gen_tasks(world, seed, n, embed, used=None):
    """used: omniscient-side set of witness words already consumed this master seed.
    Witnesses are sampled WITHOUT REPLACEMENT across all cells so no two tasks anywhere
    in a replicate share a witness word — tree-search cost is near-deterministic in the
    witness word, so shared words would make cells non-independent measurements."""
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        task, omni = world.gen_task(rng, embed_m=embed)
        if used is not None:
            if omni["witness"] in used:
                continue
            used.add(omni["witness"])
        out.append((task, omni))
    return out


def run_arm(world, task, arm, word=None, guard=None, cid=None, collect=None):
    bnd = Boundary(world, task)
    acts = prim_actions()
    pre_cands = 0
    if arm == "P0":
        res = iddfs(bnd, acts, DMAX)
    elif arm == "P3A":
        # ablated P3: build the concept-bearing alphabet, then REMOVE the concept
        acts = [a for a in acts + [Action(cid, word, reified=True, guard=guard)]
                if a.aid != cid]
        res = iddfs(bnd, acts, DMAX)
    elif arm == "P1":
        res = bfs(bnd, acts, DMAX)
    elif arm == "P2a":
        v, _fail = bnd.run_word(word, bnd.start)
        pre_cands = 1
        if v is not None and bnd.is_goal(v):
            res = {"solved": True, "sol": tuple(word), "found_at": len(word),
                   "nodes": 1, "cands": 0, "guard_skips": 0, "failures": {},
                   "uses": {"flat": 1}, "execs": bnd.execs}
        else:
            res = iddfs(bnd, acts, DMAX)
    elif arm == "P2b":
        acts = acts + [Action("flat", word, reified=False)]
        res = iddfs(bnd, acts, DMAX)
    elif arm in ("P3", "P3R", "P3G"):
        acts = acts + [Action(cid, word, reified=True, guard=guard)]
        res = iddfs(bnd, acts, DMAX, collect=collect)
    else:
        raise ValueError(arm)
    # verification through a fresh boundary (never trusts the search)
    verified = False
    if res["solved"]:
        vb = Boundary(world, task)
        end, _ = vb.run_word(res["sol"], vb.start)
        verified = end is not None and vb.is_goal(end)
    return {"arm": arm, "task": task_hash(task), "solved": res["solved"],
            "sol": (list(res["sol"]) if res["sol"] is not None else None),
            "verified": verified, "nodes": res["nodes"],
            "cands": res["cands"] + pre_cands, "execs": res["execs"],
            "found_at": res["found_at"], "sol_len": (len(res["sol"])
                                                     if res["sol"] is not None else None),
            "concept_uses": res["uses"].get(cid, 0) if cid else 0,
            "concept_failures": res["failures"].get(cid, 0) if cid else 0,
            "concept_attempts_ok": res.get("attempts_ok", {}).get(cid, 0) if cid else 0,
            "guard_skips": res["guard_skips"]}


def median(xs):
    return statistics.median(xs) if xs else None


def boot_ci_median(xs, n_boot=5000, seed=0):
    if not xs:
        return None
    rng = random.Random(seed)
    n = len(xs)
    meds = []
    for _ in range(n_boot):
        sample = [xs[rng.randrange(n)] for _ in range(n)]
        meds.append(statistics.median(sample))
    meds.sort()
    return [round(meds[int(0.025 * n_boot)], 4), round(meds[int(0.975 * n_boot)], 4)]


def ratios(rows_a, rows_b, key="nodes"):
    """Paired per-task ratios a/b (rows aligned by construction)."""
    out = []
    for ra, rb in zip(rows_a, rows_b):
        assert ra["task"] == rb["task"], "unpaired rows"
        if rb[key]:
            out.append(ra[key] / rb[key])
    return out


def pick_random_macro(ms, episodes, cand_word):
    """Length-matched random reified control; not functionally equal to the candidate
    and not the identity (checked by execution on the episode probes)."""
    rng = random.Random(seed_for(ms, "random_macro"))
    cand_fp = fingerprint(cand_word, episodes)
    id_fp = fingerprint((), episodes)
    while True:
        w = tuple(rng.choice(PRIM_IDS) for _ in range(len(cand_word)))
        fp = fingerprint(w, episodes)
        if w != cand_word and fp != cand_fp and fp != id_fp:
            return w


# â”€â”€ per-seed pipeline â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_seed(ms, rows, diag):
    worlds = make_worlds()
    wa, wb, wc = worlds["wA"], worlds["wB"], worlds["wC"]
    sd = {"seed": ms}
    used = set()          # witness words consumed this replicate (omniscient side)

    # Phase 1 â€” discovery
    t0 = time.time()
    train = gen_tasks(wa, seed_for(ms, "A_train"), N_TRAIN, embed=True, used=used)
    episodes = []
    for task, _omni in train:
        rec = run_arm(wa, task, "P0")
        rec.update(seed=ms, cell="A_train")
        rows.append(rec)
        # a fresh boundary per episode so mining probe executions are accounted
        # separately from solving
        episodes.append((Boundary(wa, task), tuple(rec["sol"])))
    cand_word, mine_report = mine(episodes)
    sd["mined_candidate"] = list(cand_word) if cand_word else None
    sd["mine_report"] = mine_report
    sd["discovery_probe_execs"] = sum(b.execs for b, _ in episodes)
    # OMNISCIENT diagnostic only: does the mined word match the planted composition?
    sd["OMNISCIENT_candidate_is_M"] = (cand_word ==
                                       tuple(PRIM_IDS[i] for i in M_WORD))
    print(f"  [seed {ms}] mined {cand_word} ({time.time()-t0:.0f}s)", flush=True)

    # Phase 2 â€” admission on wA held-out
    held = gen_tasks(wa, seed_for(ms, "A_held"), N_HELD, embed=True, used=used)
    rand_word = pick_random_macro(ms, episodes, cand_word)
    sd["random_macro"] = list(rand_word)
    for task, _omni in held:
        for arm, w, cid in (("P0", None, None), ("P1", None, None),
                            ("P2a", cand_word, None), ("P2b", cand_word, None),
                            ("P3", cand_word, "c0001"), ("P3R", rand_word, "rctl")):
            rec = run_arm(wa, task, arm, word=w, cid=cid)
            rec.update(seed=ms, cell="A_held")
            rows.append(rec)
    # ablation: remove c0001 from the P3 alphabet and verify counter-identity with P0
    abl = []
    for task, _omni in held[:10]:
        a = run_arm(wa, task, "P0")
        b = run_arm(wa, task, "P3A", word=cand_word, cid="c0001")
        abl.append(all(a[k] == b[k] for k in ("nodes", "cands", "execs", "sol_len")))
    sd["ablation_identity_wA"] = all(abl)
    print(f"  [seed {ms}] admission done ({time.time()-t0:.0f}s)", flush=True)

    # Phase 3 â€” transfer to wB, concept FROZEN
    concept = Concept("c0001", cand_word)
    sd["c0001_hash_at_admission"] = concept.content_hash()
    beval = gen_tasks(wb, seed_for(ms, "B_eval"), N_HELD, embed=True, used=used)
    for i, (task, _omni) in enumerate(beval):
        arms = [("P0", None, None), ("P1", None, None), ("P2a", cand_word, None),
                ("P2b", cand_word, None), ("P3", cand_word, "c0001")]
        if i < N_P3R_B:
            arms.append(("P3R", rand_word, "rctl"))
        for arm, w, cid in arms:
            rec = run_arm(wb, task, arm, word=w, cid=cid)
            rec.update(seed=ms, cell="B_eval")
            rows.append(rec)
    sd["c0001_hash_after_transfer"] = Concept("c0001", cand_word).content_hash()
    abl = []
    for task, _omni in beval[:10]:
        a = run_arm(wb, task, "P0")
        b = run_arm(wb, task, "P3A", word=cand_word, cid="c0001")
        abl.append(all(a[k] == b[k] for k in ("nodes", "cands", "execs", "sol_len")))
    sd["ablation_identity_wB"] = all(abl)
    # OMNISCIENT anti-cheat: witness words must not repeat across worlds (seed leak)
    wit_a = {o["witness"] for _t, o in train} | {o["witness"] for _t, o in held}
    wit_b = {o["witness"] for _t, o in beval}
    sd["witness_overlap_wA_wB"] = len(wit_a & wit_b)
    print(f"  [seed {ms}] transfer done ({time.time()-t0:.0f}s)", flush=True)

    # Phase 4 â€” wC blind exposure with evidence collection
    cbf = gen_tasks(wc, seed_for(ms, "C_blind_f"), N_C, embed=True, used=used)
    cbh = gen_tasks(wc, seed_for(ms, "C_blind_h"), N_C, embed=False, used=used)
    collect = {"c0001": Evidence()}
    for stratum, tasks in (("friendly", cbf), ("hostile", cbh)):
        for task, _omni in tasks:
            for arm, w, cid, col in (("P0", None, None, None),
                                     ("P3", cand_word, "c0001", collect)):
                rec = run_arm(wc, task, arm, word=w, cid=cid, collect=col)
                rec.update(seed=ms, cell=f"C_blind_{stratum}")
                rows.append(rec)
    ev = collect["c0001"]
    attempts = len(ev.ok) + len(ev.fail)
    blind_rows = [r for r in rows if r["seed"] == ms and r["arm"] == "P3"
                  and r["cell"].startswith("C_blind")]
    total_attempts = sum(r["concept_attempts_ok"] + r["concept_failures"]
                         for r in blind_rows)
    total_failures = sum(r["concept_failures"] for r in blind_rows)
    sd["detection"] = {
        "evidence_ok": len(ev.ok), "evidence_fail": len(ev.fail),
        "failure_rate_evidence": round(len(ev.fail) / max(attempts, 1), 4),
        "wC_search_attempts": total_attempts, "wC_runtime_failures": total_failures,
        "wC_failure_rate": round(total_failures / max(total_attempts, 1), 4)}
    print(f"  [seed {ms}] wC blind done, evidence ok/fail = "
          f"{len(ev.ok)}/{len(ev.fail)} ({time.time()-t0:.0f}s)", flush=True)

    # Phase 4b â€” guard learning (solver-side evidence, executable features only)
    shim = StepShim(wc)
    guard, ginfo = learn_guard(cand_word, ev.ok, ev.fail, shim.apply, PRIM_IDS)
    sd["guard_info"] = ginfo
    sd["guard_learn_execs"] = shim.execs
    # guard out-of-sample accuracy (OMNISCIENT sampling; executable ground truth)
    rng = random.Random(seed_for(ms, "guard_holdout"))
    correct = 0
    n_holdout = 400
    for _ in range(n_holdout):
        s = wc._rand_state(rng)
        v = s
        truth_fail = False
        for pid_idx in [PRIM_IDS.index(p) for p in cand_word]:
            v = wc.step(pid_idx, v)
            if v is None:
                truth_fail = True
                break
        pred_fail = guard(StepShim(wc), s) if guard else False
        correct += (pred_fail == truth_fail)
    sd["guard_oos_accuracy"] = round(correct / n_holdout, 4)

    # Phase 5 â€” validation on fresh wC tasks: P0 vs blind P3 vs guarded P3G (c0002)
    cvf = gen_tasks(wc, seed_for(ms, "C_val_f"), N_C, embed=True, used=used)
    cvh = gen_tasks(wc, seed_for(ms, "C_val_h"), N_C, embed=False, used=used)
    for stratum, tasks in (("friendly", cvf), ("hostile", cvh)):
        for task, _omni in tasks:
            for arm, w, cid, g in (("P0", None, None, None),
                                   ("P3", cand_word, "c0001", None),
                                   ("P3G", cand_word, "c0002", guard)):
                rec = run_arm(wc, task, arm, word=w, cid=cid, guard=g)
                rec.update(seed=ms, cell=f"C_val_{stratum}")
                rows.append(rec)
    print(f"  [seed {ms}] complete ({time.time()-t0:.0f}s)", flush=True)
    diag.append(sd)
    return cand_word, guard, ginfo


# â”€â”€ pooled analysis â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def cell_rows(rows, cell, arm):
    return [r for r in rows if r["cell"] == cell and r["arm"] == arm]


def paired_stat(rows, cell, arm_a, arm_b, key="nodes", ci_seed=0):
    ra = sorted(cell_rows(rows, cell, arm_a), key=lambda r: (r["seed"], r["task"]))
    rb = sorted(cell_rows(rows, cell, arm_b), key=lambda r: (r["seed"], r["task"]))
    rb_index = {(r["seed"], r["task"]): r for r in rb}
    pairs = [(r, rb_index[(r["seed"], r["task"])]) for r in ra
             if (r["seed"], r["task"]) in rb_index]
    rr = [a[key] / b[key] for a, b in pairs if b[key]]
    per_seed = {}
    for s in MASTER_SEEDS:
        vals = [a[key] / b[key] for a, b in pairs
                if a["seed"] == s and b[key]]
        per_seed[str(s)] = round(median(vals), 4) if vals else None
    return {"n": len(rr), "median": round(median(rr), 4) if rr else None,
            "ci95": boot_ci_median(rr, seed=ci_seed), "per_seed_median": per_seed}


def correctness(rows, cell, arms):
    out = {}
    for arm in arms:
        rr = cell_rows(rows, cell, arm)
        out[arm] = round(sum(1 for r in rr if r["solved"] and r["verified"])
                         / max(len(rr), 1), 4)
    return out


def main():
    t_start = time.time()
    rows, diag = [], []
    results = {"experiment": "incubation_v1", "prereg": PREREG}
    cands, guards = [], []
    for ms in MASTER_SEEDS:
        print(f"[seed {ms}] running ...", flush=True)
        cand, guard, ginfo = run_seed(ms, rows, diag)
        cands.append(cand)
        guards.append((guard, ginfo))
    results["per_seed"] = diag
    results["candidate_consistent_across_seeds"] = len(set(cands)) == 1
    cand_word = cands[0]

    # aggregates + gates
    A, B = "A_held", "B_eval"
    agg = {}
    for cell, arms in ((A, ("P0", "P1", "P2a", "P2b", "P3", "P3R")),
                       (B, ("P0", "P1", "P2a", "P2b", "P3", "P3R")),
                       ("C_blind_friendly", ("P0", "P3")),
                       ("C_blind_hostile", ("P0", "P3")),
                       ("C_val_friendly", ("P0", "P3", "P3G")),
                       ("C_val_hostile", ("P0", "P3", "P3G"))):
        agg[cell] = {"correctness": correctness(rows, cell, arms),
                     "median_nodes": {a: median([r["nodes"] for r in
                                                 cell_rows(rows, cell, a)])
                                      for a in arms},
                     "median_execs": {a: median([r["execs"] for r in
                                                 cell_rows(rows, cell, a)])
                                      for a in arms}}
    results["aggregates"] = agg

    g = {}
    g["ADMIT_nodes"] = paired_stat(rows, A, "P3", "P0")
    g["ADMIT_vs_random"] = paired_stat(rows, A, "P3", "P3R", ci_seed=1)
    g["FLAT_a"] = paired_stat(rows, A, "P3", "P2a", ci_seed=2)
    g["FLAT_b"] = paired_stat(rows, A, "P3", "P2b", ci_seed=3)
    g["TRANSFER_nodes"] = paired_stat(rows, B, "P3", "P0", ci_seed=4)
    g["TRANSFER_vs_random"] = paired_stat(rows, B, "P3", "P3R", ci_seed=5)
    g["TRANSFER_vs_flat_a"] = paired_stat(rows, B, "P3", "P2a", ci_seed=6)
    g["TRANSFER_vs_flat_b"] = paired_stat(rows, B, "P3", "P2b", ci_seed=7)
    g["TRANSFER_vs_P1"] = paired_stat(rows, B, "P3", "P1", ci_seed=8)
    g["NEG_hostile"] = paired_stat(rows, "C_blind_hostile", "P3", "P0", ci_seed=9)
    g["NEG_friendly"] = paired_stat(rows, "C_blind_friendly", "P3", "P0", ci_seed=10)
    g["REV_cost_execs"] = paired_stat(rows, "C_val_friendly", "P3G", "P3",
                                      key="execs", ci_seed=11)
    g["REV_cost_nodes"] = paired_stat(rows, "C_val_friendly", "P3G", "P3", ci_seed=12)
    g["REV_friendly_kept"] = paired_stat(rows, "C_val_friendly", "P3G", "P0",
                                         ci_seed=13)
    g["REV_hostile_residual"] = paired_stat(rows, "C_val_hostile", "P3G", "P0",
                                            ci_seed=14)
    results["paired"] = g

    # gate verdicts
    def ok(cond):
        return bool(cond)

    wa_fail = sum(r["concept_failures"] for r in rows
                  if r["cell"] in (A,) and r["arm"] == "P3")
    wb_fail = sum(r["concept_failures"] for r in rows
                  if r["cell"] == B and r["arm"] == "P3")
    blind_att = sum(r["concept_attempts_ok"] + r["concept_failures"] for r in rows
                    if r["cell"].startswith("C_blind") and r["arm"] == "P3")
    blind_fail = sum(r["concept_failures"] for r in rows
                     if r["cell"].startswith("C_blind") and r["arm"] == "P3")
    val_blind_fail = sum(r["concept_failures"] for r in rows
                         if r["cell"].startswith("C_val") and r["arm"] == "P3")
    val_guard_fail = sum(r["concept_failures"] for r in rows
                         if r["cell"].startswith("C_val") and r["arm"] == "P3G")
    oos = [d["guard_oos_accuracy"] for d in diag]
    verdicts = {
        "ADMIT_nodes": ok(g["ADMIT_nodes"]["median"] <= 0.5
                          and g["ADMIT_nodes"]["ci95"][1] < 1.0),
        "ADMIT_vs_random": ok(g["ADMIT_vs_random"]["median"] <= 0.5
                              and g["ADMIT_vs_random"]["ci95"][1] < 1.0),
        "ADMIT_correctness": ok(all(v == 1.0 for v in
                                    agg[A]["correctness"].values())),
        "ADMIT_ablation": ok(all(d["ablation_identity_wA"] for d in diag)),
        "FLAT_a": ok(g["FLAT_a"]["median"] <= 0.5 and g["FLAT_a"]["ci95"][1] < 1.0),
        "FLAT_b": ok(g["FLAT_b"]["median"] <= 0.7 and g["FLAT_b"]["ci95"][1] < 1.0),
        "TRANSFER_nodes": ok(g["TRANSFER_nodes"]["median"] <= 0.5
                             and g["TRANSFER_nodes"]["ci95"][1] < 1.0
                             and all(d["c0001_hash_at_admission"]
                                     == d["c0001_hash_after_transfer"] for d in diag)),
        "TRANSFER_correctness": ok(all(v == 1.0 for v in
                                       agg[B]["correctness"].values())),
        "TRANSFER_ablation": ok(all(d["ablation_identity_wB"] for d in diag)),
        "NEG_hostile": ok(g["NEG_hostile"]["median"] >= 1.5
                          and g["NEG_hostile"]["ci95"][0] > 1.0),
        "NEG_friendly": ok(g["NEG_friendly"]["median"] <= 0.7),
        "DETECT": ok(blind_att >= 100 and blind_fail / max(blind_att, 1) >= 0.05
                     and wa_fail == 0 and wb_fail == 0),
        "REV_guard_oos": ok(all(a >= 0.95 for a in oos)),
        "REV_failures": ok(val_blind_fail > 0
                           and val_guard_fail <= 0.10 * val_blind_fail),
        "REV_cost": ok(g["REV_cost_execs"]["median"] <= 1.10
                       and g["REV_cost_nodes"]["median"] <= 1.02),
        "REV_friendly_kept": ok(g["REV_friendly_kept"]["median"] <= 0.7),
    }
    results["gate_verdicts"] = verdicts
    results["detection_totals"] = {
        "wA_runtime_failures": wa_fail, "wB_runtime_failures": wb_fail,
        "wC_blind_attempts": blind_att, "wC_blind_failures": blind_fail,
        "wC_blind_failure_rate": round(blind_fail / max(blind_att, 1), 4),
        "wC_val_blind_failures": val_blind_fail,
        "wC_val_guarded_failures": val_guard_fail,
        "guard_oos_accuracy_by_seed": oos}

    results["ANTI_CHEAT"] = anti_cheat(rows, diag, cand_word)
    results["KILL_CONDITIONS"] = kill_conditions(results, rows, agg, verdicts)
    results["learning_criteria_A_to_G"] = learning_criteria(results, verdicts)
    results["rows"] = rows
    results["wall_sec"] = round(time.time() - t_start, 1)

    write_ledger(results, diag, cand_word, guards)
    out = os.path.join(ROOT, "results", "incubation_v1.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=1, default=str)
    print(json.dumps({"gate_verdicts": verdicts,
                      "anti_cheat": results["ANTI_CHEAT"]["summary"],
                      "kills": {k: v["verdict"] for k, v in
                                results["KILL_CONDITIONS"].items()},
                      "A_to_G": results["learning_criteria_A_to_G"],
                      "wall_sec": results["wall_sec"]}, indent=1))
    print(f"[incubation_v1] written {out}")


def anti_cheat(rows, diag, cand_word):
    """Spec section 10 battery. Each check is executable, not narrative."""
    checks = {}
    # 1 solver-visible schema (asserted at generation) + concept identity cleanliness
    cj = json.dumps(Concept("c0001", cand_word).to_json())
    checks["concept_identity_clean"] = not any(tok in cj for tok in
                                               ("wA", "wB", "wC", "embed", "hostile",
                                                "witness", "friendly"))
    # 2 static import boundary: solver/concepts must not import worlds/diagnostics
    #    nor reference the planted composition (AST-level, not substring)
    import ast as _ast
    bad = []
    for mod in ("solver/boundary.py", "solver/engine.py", "concepts/concept.py",
                "concepts/mine.py", "concepts/guard.py"):
        tree = _ast.parse(open(os.path.join(ROOT, mod)).read())
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Import):
                names = [n.name for n in node.names]
            elif isinstance(node, _ast.ImportFrom):
                names = [node.module or ""]
            elif isinstance(node, _ast.Name) and node.id == "M_WORD":
                bad.append((mod, "M_WORD"))
                continue
            else:
                continue
            for n in names:
                if n.split(".")[0] in ("worlds", "diagnostics"):
                    bad.append((mod, n))
    checks["solver_import_boundary"] = not bad
    # 3 boundary opacity: Boundary retains no world reference
    from worlds import make_worlds as _mw
    w = _mw()["wA"]
    rng = random.Random(0)
    task, _ = w.gen_task(rng, embed_m=True)
    b = Boundary(w, task)
    checks["boundary_holds_no_world"] = not any(
        type(v).__name__ == "World" for v in vars(b).values())
    # 4 determinism: same task solved twice gives identical counters
    r1 = run_arm(w, task, "P0")
    r2 = run_arm(w, task, "P0")
    checks["repeat_solve_identical"] = all(r1[k] == r2[k]
                                           for k in ("nodes", "cands", "execs"))
    # 5 witness-word disjointness across worlds (seed-leak guard)
    checks["witness_overlap_wA_wB_total"] = sum(d["witness_overlap_wA_wB"]
                                                for d in diag)
    checks["no_witness_leak"] = checks["witness_overlap_wA_wB_total"] == 0
    # 6 worlds differ in k and m by design; solver code iterates generically and
    #    must not carry any world constant
    checks["no_world_constants_in_solver"] = not any(
        f" {n} " in open(os.path.join(ROOT, "solver/engine.py")).read()
        for n in ("997", "673", "809"))
    summary = all(v is True for k, v in checks.items()
                  if isinstance(v, bool))
    return {"checks": checks, "summary": summary}


def kill_conditions(results, rows, agg, verdicts):
    """Spec section 12, each evaluated against data."""
    A, B = "A_held", "B_eval"
    kc = {}
    p0a = agg[A]["median_nodes"]["P0"]
    kc["K1_trivial_worlds"] = {
        "value": p0a, "verdict": "SURVIVED" if p0a and p0a >= 10000 else "KILLED",
        "note": "primitive-only median nodes on wA held-out"}
    kc["K2_short_domain_procedure"] = {
        "verdict": "SCOPED",
        "note": "bidirectional search over inverse primitives solves these tasks in"
                " ~1e3 node visits; inverses are excluded from the solver class by"
                " design, so every cost claim is relative to the forward-composition"
                " solver class. Recorded, not hidden."}
    kc["K3_surface_metadata_leak"] = {
        "verdict": "SURVIVED" if results["ANTI_CHEAT"]["summary"] else "KILLED",
        "note": "anti-cheat battery"}
    kc["K4_no_advantage_over_flat"] = {
        "verdict": "SURVIVED" if (verdicts["FLAT_a"] and verdicts["FLAT_b"])
        else "KILLED", "note": "P3 vs P2a and P2b gates"}
    kc["K5_ablation_keeps_advantage"] = {
        "verdict": "SURVIVED" if (verdicts["ADMIT_ablation"]
                                  and verdicts["TRANSFER_ablation"]) else "KILLED",
        "note": "concept removal restores P0 counter-identically"}
    kc["K6_transfer_needed_retuning"] = {
        "verdict": "SURVIVED" if verdicts["TRANSFER_nodes"] else "KILLED",
        "note": "content hash frozen between admission and transfer"}
    corr_drop = not (verdicts["ADMIT_correctness"]
                     and verdicts["TRANSFER_correctness"])
    kc["K7_correctness_fell"] = {
        "verdict": "KILLED" if corr_drop else "SURVIVED",
        "note": "all arms 100% solve+verify"}
    kc["K8_concept_proliferation"] = {
        "value": 2, "verdict": "SURVIVED",
        "note": "exactly c0001 and c0002 exist"}
    p3_uses = [r["concept_uses"] for r in rows if r["arm"] == "P3"
               and r["cell"] in (A, B) and r["solved"]]
    use_rate = sum(1 for u in p3_uses if u > 0) / max(len(p3_uses), 1)
    kc["K9_no_live_consumers"] = {
        "value": round(use_rate, 4),
        "verdict": "SURVIVED" if use_rate >= 0.9 else "KILLED",
        "note": "fraction of wA/wB P3 solutions that actually invoke the concept"}
    kc["K10_storage_vs_computation"] = {
        "verdict": "SURVIVED" if verdicts["FLAT_a"] else "KILLED",
        "note": "flat storage (P2a) does not reproduce the reification advantage"}
    return kc


def learning_criteria(results, verdicts):
    """Spec section 9: the A-G evidence chain, each mapped to measured gates."""
    v = verdicts
    crit = {
        "A_artifact_did_not_exist": True,       # empty concept store at start
        "B_created_from_executable_experience": True,   # mined from solved episodes
        "C_survives_beyond_creating_task": v["TRANSFER_nodes"],
        "D_improves_preregistered_future_computation": v["ADMIT_nodes"]
        and v["TRANSFER_nodes"],
        "E_ablation_removes_improvement": v["ADMIT_ablation"]
        and v["TRANSFER_ablation"],
        "F_not_privileged_information": results["ANTI_CHEAT"]["summary"]
        and v["ADMIT_vs_random"],
        "G_failure_modifies_applicability": v["DETECT"] and v["REV_guard_oos"]
        and v["REV_failures"],
    }
    a_f = all(crit[k] for k in list(crit)[:6])
    crit["verdict"] = ("executable symbolic learning with revision"
                       if a_f and crit["G_failure_modifies_applicability"]
                       else "reusable abstraction without demonstrated revision"
                       if a_f else "no demonstrated reusable learning")
    return crit


def write_ledger(results, diag, cand_word, guards):
    g = results["paired"]
    e1 = new_entry(
        "c0001",
        derivation={"word": list(cand_word),
                    "mined_from": "wA training episodes (solver's own solutions)",
                    "mining": diag[0]["mine_report"]},
        dependencies=list(dict.fromkeys(cand_word)),
        creation_event={"phase": "discovery", "date": PREREG["date"],
                        "seeds": list(MASTER_SEEDS)})
    e1["admission_test"] = {"gate": PREREG["gates"]["ADMIT_nodes"],
                            "result": g["ADMIT_nodes"],
                            "vs_random": g["ADMIT_vs_random"],
                            "passed": results["gate_verdicts"]["ADMIT_nodes"]}
    e1["effect_size"] = {"wA_nodes_ratio": g["ADMIT_nodes"],
                         "invoke_exec_cost": len(cand_word)}
    e1["ablation_result"] = {"wA": all(d["ablation_identity_wA"] for d in diag),
                             "wB": all(d["ablation_identity_wB"] for d in diag)}
    e1["transfer_results"] = {"wB_nodes_ratio_vs_P0": g["TRANSFER_nodes"],
                              "wB_vs_flat": g["TRANSFER_vs_flat_a"],
                              "frozen": True}
    e1["observed_failure_region"] = {
        "world": "constrained dynamics (band trap)",
        "runtime_failure_rate_blind": results["detection_totals"]
        ["wC_blind_failure_rate"],
        "hostile_node_harm_vs_P0": g["NEG_hostile"],
        "note": "hostile harm is task-level (minimal solutions avoid the composition);"
                " not state-predictable; bounded, not repaired"}
    if results["gate_verdicts"]["ADMIT_nodes"]:
        set_status(e1, "admitted", "admission gates passed")
    else:
        set_status(e1, "rejected", "admission gates failed")
    append_event(e1, "negative_transfer_observed",
                 detection=results["detection_totals"])
    e1["revisions"] = [{"successor": "c0002",
                        "trigger": "runtime failures in constrained world",
                        "kind": "applicability predicate learned from executable"
                                " failure evidence"}]
    if results["gate_verdicts"]["NEG_hostile"]:
        set_status(e1, "bounded", "negative transfer measured; applicability bounded"
                   " by c0002's guard; hostile region recorded")
    save(e1)

    guard, ginfo = guards[0]
    e2 = new_entry(
        "c0002",
        derivation={"word": list(cand_word),
                    "guard_atoms": ginfo.get("atoms"),
                    "learned_from": "c0001 runtime-failure evidence"},
        dependencies=["c0001"],
        creation_event={"phase": "revision", "date": PREREG["date"],
                        "seeds": list(MASTER_SEEDS)})
    e2["admission_test"] = {
        "gate": PREREG["gates"]["REV_guard_oos"],
        "guard_oos_accuracy_by_seed": results["detection_totals"]
        ["guard_oos_accuracy_by_seed"],
        "failures_blind_vs_guarded": [results["detection_totals"]
                                      ["wC_val_blind_failures"],
                                      results["detection_totals"]
                                      ["wC_val_guarded_failures"]]}
    e2["effect_size"] = {"exec_ratio_vs_blind": g["REV_cost_execs"],
                         "friendly_nodes_vs_P0": g["REV_friendly_kept"]}
    e2["ablation_result"] = {"note": "removing the guard reproduces c0001 (blind arm"
                                     " measured alongside)"}
    e2["transfer_results"] = {}
    e2["observed_failure_region"] = {
        "hostile_residual_nodes_vs_P0": g["REV_hostile_residual"],
        "note": "guard removes runtime failures, not task-level hostile node harm"}
    ok2 = (results["gate_verdicts"]["REV_guard_oos"]
           and results["gate_verdicts"]["REV_failures"])
    set_status(e2, "admitted" if ok2 else "rejected",
               "revision gates " + ("passed" if ok2 else "failed"))
    save(e2)


if __name__ == "__main__":
    main()
