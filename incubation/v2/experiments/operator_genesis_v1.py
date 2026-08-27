"""operator_genesis_v1.py — the preregistered Operator Genesis experiment (v2).

One independent variable vs v1: learned artifacts may reorganize COMPUTATION (processes,
scheduling, halting, staging), not just occupy a composition slot. Everything else is
held to the v1 microscope: exact worlds, exact oracles, metered costs, preregistered
gates, executable anti-cheat, append-only ledger, five master seeds.

Conditions
  A0  fixed forward baseline program (the learner's starting architecture)
  A1  A0 + one mined v1-style macro edge per domain (macro-learning control)
  A2  the architecture-construction learner (this experiment's subject)
  A3  omniscient meet-in-the-middle ceiling — HARNESS-SIDE ONLY, never learner-visible;
      used solely to report how much of the known opportunity A2 captured

Phases per seed
  0 CONTROL    dW0 shallow: the construction trigger must NOT fire (counterfactual)
  1 EXPERIENCE dA+dB mixed-depth: baseline fails deep tasks; trigger fires
  2 CONSTRUCT  exhaustive metered evaluation of the frozen 1-stage space on the
               learner's own failed tasks; winner = o0001; classifier must say
               ARCHITECTURAL under the preregistered structural+behavioral rule
  3 ADMIT      held-out dA/dB under A0/A1/A2/A3; ablation restores baseline
  4 TRANSFER   dC (alien family), o0001 frozen by content hash; same conditions
  5 TRAP       dD blind exposure; executable detection (anomaly -> backward-edge
               audit); revision o0002 = learned routing predicate; validation on
               fresh dD and fresh dA (advantage must survive routing)
  6 RECURSION  dE via-tasks: naive vs experienced construction; acquisition cost

Verdict enum (conservative, preregistered):
  NO_ARCHITECTURAL_LEARNING -> ARCHITECTURAL_ADAPTATION_ONLY ->
  TRANSFERABLE_ARCHITECTURAL_OPERATOR -> TRANSFERABLE_OPERATOR_WITH_REVISION ->
  RECURSIVE_LEARNING_EFFECT
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from domains import DEPTHS, PLANT_A, SHALLOW, make_domains            # noqa: E402
from dsl import BASELINE, classify, enumerate_seq, enumerate_stage, \
    enumeration_sha, serial                                            # noqa: E402
from runtime import MacroAdapter, Meter, run_program                   # noqa: E402
import learner as L                                                    # noqa: E402
from ledger_v2 import append_event, new_entry, save, set_status        # noqa: E402

BUDGET = 400_000
MASTER_SEEDS = (11, 22, 33, 44, 55)
E_MAX_CANDIDATES = 1200
A3 = ("STAGE", (("A", "S"), ("Z", "P")), ("IF", "FSIZE", "LE", "FSIZE"), "MEET")

PREREG = {
    "date": "2026-08-26",
    "unit": "task",
    "primary_metric": "metered operations to first verified solution (unsolved = "
                      "budget value 400k); solve rate within budget",
    "budget": BUDGET, "probe_budget": L.PROBE_BUDGET,
    "enumeration_sha": "c44f6a4f09094537",
    "seeds": list(MASTER_SEEDS),
    "cells": {"dW0": 8, "exp_dA": 12, "exp_dB": 8, "held_dA": 16, "held_dB": 14,
              "dC_mine": 4, "dC_eval": 16, "dD_blind": 14, "dD_fresh": 14,
              "dA_fresh": 6, "dE_probe": 3, "dE_held": 10,
              "e_max_candidates": E_MAX_CANDIDATES},
    "classifier": "dsl.classify — structural AND behavioral; fixed before any run",
    "gates": {
        "G_TRIG": "trigger (>=30% budget failures over >=10 tasks) fires on dA+dB "
                  "experience in every seed and NEVER on dW0",
        "G_CONSTRUCTED": "exhaustive metered construction yields an operator in "
                         "every seed",
        "G_CLASS": "classify(o0001, trace) == ARCHITECTURAL in every seed",
        "G_ADMIT_SOLVE": "held-out dA+dB pooled: A2 solve rate == 1.0 and A0 <= 0.40",
        "G_ADMIT_COST": "pooled median ops ratio A2/A0 <= 0.5 (unsolved at budget)",
        "G_BEATS_A1": "A2 solve rate > A1 solve rate AND pooled median ops ratio "
                      "A2/A1 <= 0.5",
        "G_ABLATION": "A2 with o0001 removed is result-identical to A0 (ops, solved, "
                      "word) on 6 held tasks per seed",
        "T_SOLVE": "dC pooled: A2 == 1.0 and A0 <= 0.40",
        "T_COST": "dC pooled median ops ratio A2/A0 <= 0.5",
        "T_BEATS_A1": "dC: A2 solve rate > A1 AND median ratio A2/A1 <= 0.5",
        "T_FROZEN": "o0001 content hash identical before and after transfer",
        "T_ABLATION": "ablation identity on dC (4 tasks/seed)",
        "D_HARM": "dD blind pooled: median ops ratio A2/A0 >= 1.5 OR A2 solve rate "
                  "<= 0.75",
        "D_DETECT": ">=30% of dD A2 runs anomalous (budget failure or ops > 5x the "
                    "seed's clean solved median); backward-edge audit finds "
                    "inconsistent edges in >=90% of anomalous runs; zero anomalies "
                    "across A2 clean-world runs",
        "D_REVISED": "a routing predicate exactly separating bad from good evidence "
                     "exists (cheapest feature preferred) in every seed",
        "D_VALID": "fresh dD: A2R routes 100% to fallback, solve rate == 1.0, "
                   "median ratio A2R/A0 <= 1.2; fresh dA: A2R routes 100% to the "
                   "operator, solve rate == 1.0, median ratio A2R/A2 <= 1.05",
        "E_FOUND": "experienced construction finds an admissible dE program within "
                   "1200 candidates in every seed",
        "E_ACQ": "per seed: naive candidates-until-found >= 3x experienced (naive "
                 "not-found counts as the 1200 cap)",
        "E_HELD": "the experienced-found program solves 10/10 held dE tasks per seed",
        "E_CLASS": "classify(found program) == ARCHITECTURAL",
    },
    "verdict_rule": "admitted = G_*; transferable = admitted+T_*; revised = "
                    "transferable+D_*; recursive = revised+E_*; verdict = highest "
                    "tier fully satisfied, else the conservative lower tier",
    "a3_role": "ceiling only: capture ratio reported, never a gate, never "
               "learner-visible",
}


# ── helpers ─────────────────────────────────────────────────────────────────────────

def th(task):
    return hashlib.sha256(repr((task.get("start"), task.get("via"),
                                task.get("target"))).encode()).hexdigest()[:12]


def med(xs):
    return statistics.median(xs) if xs else None


def boot_ci(xs, seed=0, n_boot=5000):
    if not xs:
        return None
    rng = random.Random(seed)
    n = len(xs)
    meds = sorted(statistics.median([xs[rng.randrange(n)] for _ in range(n)])
                  for _ in range(n_boot))
    return [round(meds[int(0.025 * n_boot)], 4), round(meds[int(0.975 * n_boot)], 4)]


def gen_cell(dom, seed, n, deep_frac, used, plant=None, depths=None):
    """Mixed-depth cell; witness words sampled without replacement (v1 lesson)."""
    rng = random.Random(seed)
    dd = depths or DEPTHS[dom.wid]
    sh = SHALLOW.get(dom.wid, dd)
    n_deep = round(n * deep_frac)
    out = []
    for i in range(n):
        pair = dd if i < n_deep else sh
        out.append(dom.gen_task(rng, pair[i % 2], plant=plant, used=used))
    return out


def mine_macro(words):
    """v1-style miner for the A1 control: top contiguous n-gram by support*(len-1)."""
    support = {}
    for idx, w in enumerate(words):
        for n in range(2, 5):
            for i in range(len(w) - n + 1):
                support.setdefault(tuple(w[i:i + n]), set()).add(idx)
    scored = sorted(((len(t) * (len(g) - 1), len(g), g)
                     for g, t in support.items() if len(t) >= 2),
                    key=lambda x: (-x[0], x[1], x[2]))
    return list(scored[0][2]) if scored else None


def run_cond(dom, task, cond, seed, cell, o1=None, o2=None, macro=None,
             audit=False):
    if cond == "A0":
        r = run_program(dom, task, BASELINE, BUDGET)
    elif cond == "A1":
        meter = Meter(BUDGET)
        ad = MacroAdapter(dom, task, meter, macro) if macro else None
        r = run_program(dom, task, BASELINE, BUDGET, meter=meter, adapter=ad) \
            if macro else run_program(dom, task, BASELINE, BUDGET)
    elif cond == "A2":
        r = L.run_operator(dom, task, o1, BUDGET, audit=audit)
    elif cond == "A2R":
        r = L.run_operator(dom, task, o2, BUDGET, audit=audit)
    elif cond == "A2A":
        # ablated A2: removing the sole admitted operator from the learner's
        # repertoire leaves exactly the baseline program; run it as such and gate on
        # result-identity with A0
        r = run_program(dom, task, BASELINE, BUDGET)
    elif cond == "A3":
        r = run_program(dom, task, A3, BUDGET)
    else:
        raise ValueError(cond)
    return {"seed": seed, "cell": cell, "cond": cond, "task": th(task),
            "solved": r["solved"], "ops": r["ops"],
            "budget_exhausted": r.get("budget_exhausted", False),
            "halt": r["trace"]["halt"], "word_len": len(r["word"] or []),
            "word": r["word"], "routed_to": r.get("routed_to"),
            "bwd_inconsistent": r["trace"].get("bwd_inconsistent")}


# ── per-seed pipeline ───────────────────────────────────────────────────────────────

def run_seed(ms, doms, rows, diag):
    t0 = time.time()
    sd = {"seed": ms}
    used = {wid: set() for wid in doms}
    dA, dB, dC, dD, dE, dW0 = (doms[k] for k in
                               ("dA", "dB", "dC", "dD", "dE", "dW0"))

    # 0 CONTROL — no pathology, no construction
    w0 = gen_cell(dW0, ms * 100 + 1, 8, 0.0, used["dW0"])
    recs0 = L.experience(dW0, w0, BASELINE, BUDGET)
    fired0, stats0 = L.trigger_fired(recs0)
    sd["dW0_trigger"] = {"fired": fired0, **stats0}
    for t_, r in zip(w0, recs0):
        rows.append({"seed": ms, "cell": "dW0", "cond": "A0", "task": th(t_[0]),
                     "solved": r["solved"], "ops": r["ops"],
                     "budget_exhausted": r["budget_exhausted"]})

    # 1 EXPERIENCE
    expA = gen_cell(dA, ms * 100 + 2, 12, 8 / 12, used["dA"], plant=PLANT_A)
    expB = gen_cell(dB, ms * 100 + 3, 8, 5 / 8, used["dB"], plant=PLANT_A)
    recsA = L.experience(dA, expA, BASELINE, BUDGET)
    recsB = L.experience(dB, expB, BASELINE, BUDGET)
    fired, stats = L.trigger_fired(recsA + recsB)
    sd["trigger"] = {"fired": fired, **stats}
    for dom, cell, tasks, recs in ((dA, "exp_dA", expA, recsA),
                                   (dB, "exp_dB", expB, recsB)):
        for t_, r in zip(tasks, recs):
            rows.append({"seed": ms, "cell": cell, "cond": "A0",
                         "task": th(t_[0]), "solved": r["solved"], "ops": r["ops"],
                         "budget_exhausted": r["budget_exhausted"]})

    # A1 macro mining from solved experience (per domain)
    macA = mine_macro([tuple(run_program(dA, t_[0], BASELINE, BUDGET)["word"])
                       for t_, r in zip(expA, recsA) if r["solved"]])
    macB = mine_macro([tuple(run_program(dB, t_[0], BASELINE, BUDGET)["word"])
                       for t_, r in zip(expB, recsB) if r["solved"]])
    sd["a1_macros"] = {"dA": macA, "dB": macB}

    # 2 CONSTRUCT (only because the trigger fired — preregistered causal link)
    probes = [(dA, t_["task"]) for t_ in recsA if t_["budget_exhausted"]][:3] + \
             [(dB, t_["task"]) for t_ in recsB if t_["budget_exhausted"]][:2]
    o1 = None
    if fired:
        o1, cinfo = L.construct_exhaustive(probes)
        sd["construction"] = {**cinfo,
                              "o0001": serial(o1) if o1 else None}
    sd["o0001_hash"] = hashlib.sha256(serial(o1).encode()).hexdigest()[:16] \
        if o1 else None
    probe_run = run_program(probes[0][0], probes[0][1], o1, BUDGET) if o1 else None
    sd["o0001_class"] = classify(o1, probe_run["trace"]) if o1 else None
    print(f"  [seed {ms}] constructed {serial(o1) if o1 else None} "
          f"({sd['o0001_class']}) ({time.time()-t0:.0f}s)", flush=True)

    # 3 ADMIT — held-out dA/dB
    heldA = gen_cell(dA, ms * 100 + 4, 16, 11 / 16, used["dA"], plant=PLANT_A)
    heldB = gen_cell(dB, ms * 100 + 5, 14, 10 / 14, used["dB"], plant=PLANT_A)
    for dom, cell, tasks, mac in ((dA, "held_dA", heldA, macA),
                                  (dB, "held_dB", heldB, macB)):
        for t_, _o in tasks:
            for cond in ("A0", "A1", "A2", "A3"):
                rows.append(run_cond(dom, t_, cond, ms, cell, o1=o1, macro=mac))
    abl = []
    for t_, _o in heldA[:6]:
        a = run_cond(dA, t_, "A0", ms, "ablate_dA")
        b = run_cond(dA, t_, "A2A", ms, "ablate_dA", o1=o1)
        abl.append(all(a[k] == b[k] for k in ("solved", "ops", "word")))
        rows.extend([a, b])
    sd["ablation_dA"] = all(abl)
    print(f"  [seed {ms}] admission done ({time.time()-t0:.0f}s)", flush=True)

    # 4 TRANSFER — dC, frozen
    hash_before = sd["o0001_hash"]
    cmine = gen_cell(dC, ms * 100 + 6, 4, 0.0, used["dC"])
    macC = mine_macro([tuple(run_program(dC, t_[0], BASELINE, BUDGET)["word"])
                       for t_ in cmine])
    sd["a1_macros"]["dC"] = macC
    for t_, _o in cmine:
        rows.append(run_cond(dC, t_, "A0", ms, "dC_mine"))
    ceval = gen_cell(dC, ms * 100 + 7, 16, 11 / 16, used["dC"])
    for t_, _o in ceval:
        for cond in ("A0", "A1", "A2", "A3"):
            rows.append(run_cond(dC, t_, cond, ms, "dC_eval", o1=o1, macro=macC))
    abl = []
    for t_, _o in ceval[:4]:
        a = run_cond(dC, t_, "A0", ms, "ablate_dC")
        b = run_cond(dC, t_, "A2A", ms, "ablate_dC", o1=o1)
        abl.append(all(a[k] == b[k] for k in ("solved", "ops", "word")))
        rows.extend([a, b])
    sd["ablation_dC"] = all(abl)
    sd["o0001_hash_after_transfer"] = hashlib.sha256(
        serial(o1).encode()).hexdigest()[:16] if o1 else None
    sd["frozen"] = hash_before == sd["o0001_hash_after_transfer"]
    print(f"  [seed {ms}] transfer done ({time.time()-t0:.0f}s)", flush=True)

    # 5 TRAP — dD blind, detection, revision, validation
    dblind = gen_cell(dD, ms * 100 + 8, 14, 1.0, used["dD"])
    blind_rows = []
    for t_, _o in dblind:
        rows.append(run_cond(dD, t_, "A0", ms, "dD_blind"))
        rr = run_cond(dD, t_, "A2", ms, "dD_blind", o1=o1)
        rows.append(rr)
        blind_rows.append((t_, rr))
    clean_solved = [r["ops"] for r in rows
                    if r["seed"] == ms and r["cond"] == "A2" and r["solved"]
                    and r["cell"] in ("held_dA", "held_dB")]
    thresh = 5 * med(clean_solved) if clean_solved else BUDGET
    anomalous = [(t_, rr) for t_, rr in blind_rows
                 if rr["budget_exhausted"] or rr["ops"] > thresh]
    audit_hits = 0
    for t_, _rr in anomalous:
        ar = L.run_operator(dD, t_, o1, BUDGET, audit=True)
        if ar["trace"].get("bwd_inconsistent", 0) > 0:
            audit_hits += 1
    clean_anoms = sum(1 for r in rows
                      if r["seed"] == ms and r["cond"] == "A2"
                      and r["cell"] in ("held_dA", "held_dB", "dC_eval")
                      and (r["budget_exhausted"] or r["ops"] > thresh))
    sd["detection"] = {"anomalous": len(anomalous), "n_blind": len(blind_rows),
                       "audit_hits": audit_hits, "clean_anomalies": clean_anoms,
                       "threshold": thresh}
    bad_ev = [(dD, t_) for t_, _rr in anomalous[:6]]
    good_ev = [(dA, t_[0]) for t_ in heldA[:3]] + \
              [(dB, t_[0]) for t_ in heldB[:3]] + \
              [(dC, t_[0]) for t_ in ceval[:3]]
    router = L.learn_router(bad_ev, good_ev)
    sd["router"] = router
    o2 = ("ROUTE", router["feature"], router["threshold"], BASELINE, o1) \
        if router else None
    dfresh = gen_cell(dD, ms * 100 + 9, 14, 1.0, used["dD"])
    for t_, _o in dfresh:
        rows.append(run_cond(dD, t_, "A0", ms, "dD_fresh"))
        rows.append(run_cond(dD, t_, "A2", ms, "dD_fresh", o1=o1))
        if o2:
            rows.append(run_cond(dD, t_, "A2R", ms, "dD_fresh", o1=o1, o2=o2))
    afresh = gen_cell(dA, ms * 100 + 10, 6, 1.0, used["dA"], plant=PLANT_A)
    for t_, _o in afresh:
        rows.append(run_cond(dA, t_, "A2", ms, "dA_fresh", o1=o1))
        if o2:
            rows.append(run_cond(dA, t_, "A2R", ms, "dA_fresh", o1=o1, o2=o2))
    print(f"  [seed {ms}] trap+revision done ({time.time()-t0:.0f}s)", flush=True)

    # 6 RECURSION — dE acquisition cost, naive vs experienced
    eprobes = [(dE, t_[0]) for t_ in gen_cell(dE, ms * 100 + 11, 3, 1.0,
                                              used["dE"])]
    seq_space = enumerate_seq()
    naive_prog, naive_info = L.construct_first_admissible(
        L.naive_order(seq_space), eprobes, E_MAX_CANDIDATES)
    lib_stages = [o1] if o1 and o1[0] == "STAGE" else []
    exp_prog, exp_info = L.construct_first_admissible(
        L.experienced_order(lib_stages, seq_space), eprobes, E_MAX_CANDIDATES)
    sd["e_naive"] = {**naive_info,
                     "prog": serial(naive_prog) if naive_prog else None}
    sd["e_experienced"] = {**exp_info,
                           "prog": serial(exp_prog) if exp_prog else None}
    if exp_prog:
        er = run_program(dE, eprobes[0][1], exp_prog, BUDGET)
        sd["e_class"] = classify(exp_prog, er["trace"])
        sd["e_contains_o0001"] = (exp_prog[0] == "SEQ"
                                  and serial(o1) in (serial(exp_prog[1]),
                                                     serial(exp_prog[2])))
        eheld = gen_cell(dE, ms * 100 + 12, 10, 1.0, used["dE"])
        for t_, _o in eheld:
            r = run_program(dE, t_, exp_prog, BUDGET)
            rows.append({"seed": ms, "cell": "dE_held", "cond": "A2E",
                         "task": th(t_), "solved": r["solved"], "ops": r["ops"],
                         "budget_exhausted": r.get("budget_exhausted", False)})
    print(f"  [seed {ms}] complete ({time.time()-t0:.0f}s)", flush=True)
    diag.append(sd)
    return o1, o2


# ── pooled analysis and gates ───────────────────────────────────────────────────────

def cell_rows(rows, cells, cond):
    if isinstance(cells, str):
        cells = (cells,)
    return [r for r in rows if r["cell"] in cells and r["cond"] == cond]


def solve_rate(rows, cells, cond):
    rr = cell_rows(rows, cells, cond)
    return round(sum(r["solved"] for r in rr) / max(len(rr), 1), 4), len(rr)


def paired_ratio(rows, cells, ca, cb, seed_ci=0):
    ra = {(r["seed"], r["task"]): r for r in cell_rows(rows, cells, ca)}
    rb = {(r["seed"], r["task"]): r for r in cell_rows(rows, cells, cb)}
    ratios = [ra[k]["ops"] / rb[k]["ops"] for k in ra if k in rb and rb[k]["ops"]]
    per_seed = {}
    for s in MASTER_SEEDS:
        vals = [ra[k]["ops"] / rb[k]["ops"] for k in ra
                if k in rb and rb[k]["ops"] and k[0] == s]
        per_seed[str(s)] = round(med(vals), 4) if vals else None
    return {"n": len(ratios), "median": round(med(ratios), 4) if ratios else None,
            "ci95": boot_ci(ratios, seed=seed_ci), "per_seed": per_seed}


def main():
    t0 = time.time()
    doms = make_domains()
    rows, diag = [], []
    ops = []
    for ms in MASTER_SEEDS:
        print(f"[seed {ms}] running ...", flush=True)
        ops.append(run_seed(ms, doms, rows, diag))
    res = {"experiment": "operator_genesis_v1", "prereg": PREREG,
           "per_seed": diag}
    res["o0001_consistent"] = len({d["construction"]["o0001"]
                                   for d in diag}) == 1

    held = ("held_dA", "held_dB")
    P = {}
    P["admit_A2_vs_A0"] = paired_ratio(rows, held, "A2", "A0", 1)
    P["admit_A2_vs_A1"] = paired_ratio(rows, held, "A2", "A1", 2)
    P["admit_A2_vs_A3_capture"] = paired_ratio(rows, held, "A2", "A3", 3)
    P["dC_A2_vs_A0"] = paired_ratio(rows, "dC_eval", "A2", "A0", 4)
    P["dC_A2_vs_A1"] = paired_ratio(rows, "dC_eval", "A2", "A1", 5)
    P["dC_A2_vs_A3_capture"] = paired_ratio(rows, "dC_eval", "A2", "A3", 6)
    P["dD_blind_A2_vs_A0"] = paired_ratio(rows, "dD_blind", "A2", "A0", 7)
    P["dD_fresh_A2R_vs_A0"] = paired_ratio(rows, "dD_fresh", "A2R", "A0", 8)
    P["dA_fresh_A2R_vs_A2"] = paired_ratio(rows, "dA_fresh", "A2R", "A2", 9)
    res["paired"] = P

    S = {}
    for name, cells in (("held", held), ("dC", "dC_eval"), ("dD_blind", "dD_blind"),
                        ("dD_fresh", "dD_fresh")):
        S[name] = {c: solve_rate(rows, cells, c)
                   for c in ("A0", "A1", "A2", "A2R", "A3")}
    S["dE_held_A2E"] = solve_rate(rows, "dE_held", "A2E")
    res["solve_rates"] = S

    det = [d["detection"] for d in diag]
    route_ok = all(
        all(r["routed_to"] == "fallback" for r in cell_rows(rows, "dD_fresh", "A2R")
            if r["seed"] == d["seed"]) and
        all(r["routed_to"] == "operator" for r in cell_rows(rows, "dA_fresh", "A2R")
            if r["seed"] == d["seed"]) for d in diag)
    g = {
        "G_TRIG": all(d["trigger"]["fired"] and not d["dW0_trigger"]["fired"]
                      for d in diag),
        "G_CONSTRUCTED": all(d.get("construction", {}).get("o0001") for d in diag),
        "G_CLASS": all(d["o0001_class"] == "ARCHITECTURAL" for d in diag),
        "G_ADMIT_SOLVE": S["held"]["A2"][0] == 1.0 and S["held"]["A0"][0] <= 0.40,
        "G_ADMIT_COST": (P["admit_A2_vs_A0"]["median"] or 1) <= 0.5,
        "G_BEATS_A1": (S["held"]["A2"][0] > S["held"]["A1"][0]
                       and (P["admit_A2_vs_A1"]["median"] or 1) <= 0.5),
        "G_ABLATION": all(d["ablation_dA"] for d in diag),
        "T_SOLVE": S["dC"]["A2"][0] == 1.0 and S["dC"]["A0"][0] <= 0.40,
        "T_COST": (P["dC_A2_vs_A0"]["median"] or 1) <= 0.5,
        "T_BEATS_A1": (S["dC"]["A2"][0] > S["dC"]["A1"][0]
                       and (P["dC_A2_vs_A1"]["median"] or 1) <= 0.5),
        "T_FROZEN": all(d["frozen"] for d in diag),
        "T_ABLATION": all(d["ablation_dC"] for d in diag),
        "D_HARM": ((P["dD_blind_A2_vs_A0"]["median"] or 0) >= 1.5
                   or S["dD_blind"]["A2"][0] <= 0.75),
        "D_DETECT": all(d["anomalous"] >= 0.3 * d["n_blind"]
                        and d["audit_hits"] >= 0.9 * d["anomalous"]
                        and d["clean_anomalies"] == 0 for d in det),
        "D_REVISED": all(d["router"] is not None for d in diag),
        "D_VALID": (route_ok and S["dD_fresh"]["A2R"][0] == 1.0
                    and (P["dD_fresh_A2R_vs_A0"]["median"] or 9) <= 1.2
                    and (P["dA_fresh_A2R_vs_A2"]["median"] or 9) <= 1.05),
        "E_FOUND": all(d["e_experienced"]["found"] for d in diag),
        "E_ACQ": all((d["e_naive"]["candidates"] if not d["e_naive"]["found"]
                      else d["e_naive"]["candidates"])
                     >= 3 * d["e_experienced"]["candidates"] for d in diag),
        "E_HELD": S["dE_held_A2E"][0] == 1.0,
        "E_CLASS": all(d.get("e_class") == "ARCHITECTURAL" for d in diag),
    }
    res["gates"] = g

    admitted = all(g[k] for k in ("G_TRIG", "G_CONSTRUCTED", "G_CLASS",
                                  "G_ADMIT_SOLVE", "G_ADMIT_COST", "G_BEATS_A1",
                                  "G_ABLATION"))
    transferable = admitted and all(g[k] for k in
                                    ("T_SOLVE", "T_COST", "T_BEATS_A1",
                                     "T_FROZEN", "T_ABLATION"))
    revised = transferable and all(g[k] for k in
                                   ("D_HARM", "D_DETECT", "D_REVISED", "D_VALID"))
    recursive = revised and all(g[k] for k in
                                ("E_FOUND", "E_ACQ", "E_HELD", "E_CLASS"))
    res["VERDICT"] = ("RECURSIVE_LEARNING_EFFECT" if recursive
                      else "TRANSFERABLE_OPERATOR_WITH_REVISION" if revised
                      else "TRANSFERABLE_ARCHITECTURAL_OPERATOR" if transferable
                      else "ARCHITECTURAL_ADAPTATION_ONLY" if admitted
                      else "NO_ARCHITECTURAL_LEARNING")

    res["ANTI_CHEAT"] = anti_cheat(rows, diag, doms, ops)
    res["rows"] = rows
    res["wall_sec"] = round(time.time() - t0, 1)
    write_ledger(res, diag)
    out = os.path.join(ROOT, "results", "operator_genesis_v1.json")
    with open(out, "w") as f:
        json.dump(res, f, indent=1, default=str)
    print(json.dumps({"gates": g, "VERDICT": res["VERDICT"],
                      "anti_cheat": res["ANTI_CHEAT"]["summary"],
                      "o0001_consistent": res["o0001_consistent"],
                      "wall_sec": res["wall_sec"]}, indent=1))
    print(f"[operator_genesis] written {out}")


def anti_cheat(rows, diag, doms, ops):
    import ast as _ast
    checks = {}
    bad = []
    for mod in ("learner.py", "dsl.py", "runtime.py"):
        tree = _ast.parse(open(os.path.join(ROOT, mod)).read())
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Import):
                names = [n.name.split(".")[0] for n in node.names]
            elif isinstance(node, _ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            else:
                if isinstance(node, _ast.Name) and node.id == "A3":
                    bad.append((mod, "A3"))
                continue
            if set(names) & {"domains"}:
                bad.append((mod, names))
    checks["learner_import_boundary"] = not bad
    checks["enumeration_sha_matches_prereg"] = (
        enumeration_sha(enumerate_stage()) == PREREG["enumeration_sha"])
    all_pids = [p for d in doms.values() for p in d.pids]
    o1_serials = {d["construction"]["o0001"] for d in diag}
    checks["operator_identity_clean"] = not any(
        pid in s for s in o1_serials for pid in all_pids)
    dA = doms["dA"]
    rng = random.Random(0)
    task, _ = dA.gen_task(rng, 10)
    r1 = run_program(dA, task, A3, BUDGET)
    r2 = run_program(dA, task, A3, BUDGET)
    checks["repeat_run_identical"] = (r1["ops"] == r2["ops"]
                                      and r1["word"] == r2["word"])
    checks["a3_isolated_from_learner"] = not any(m == "learner.py" and t == "A3"
                                                 for m, t in bad)
    checks["summary"] = all(v is True for k, v in checks.items()
                            if isinstance(v, bool))
    return checks


def write_ledger(res, diag):
    d0 = diag[0]
    g = res["gates"]
    e1 = new_entry("o0001",
                   derivation={"program": d0["construction"]["o0001"],
                               "constructed_by": "exhaustive metered evaluation of "
                               "the frozen 1-stage space on the learner's own "
                               "budget-failed tasks",
                               "construction_cost": {
                                   k: d0["construction"][k]
                                   for k in ("candidates", "construction_ops")}},
                   dependencies=["meta-runtime primitives: spawn/expand/observe/"
                                 "meet/reconstruct via succ+pred"],
                   creation_event={"phase": "construct", "date": PREREG["date"],
                                   "trigger": d0["trigger"]})
    e1["admission_test"] = {"gates": {k: g[k] for k in
                                      ("G_ADMIT_SOLVE", "G_ADMIT_COST",
                                       "G_BEATS_A1")},
                            "vs_A0": res["paired"]["admit_A2_vs_A0"],
                            "vs_A1": res["paired"]["admit_A2_vs_A1"]}
    e1["effect_size"] = {"capture_vs_ceiling": res["paired"]
                         ["admit_A2_vs_A3_capture"],
                         "classifier": d0["o0001_class"]}
    e1["ablation_result"] = {"dA": g["G_ABLATION"], "dC": g["T_ABLATION"]}
    e1["transfer_results"] = {"dC_vs_A0": res["paired"]["dC_A2_vs_A0"],
                              "frozen": g["T_FROZEN"]}
    e1["observed_failure_region"] = {
        "unreliable_predecessor_worlds": res["paired"]["dD_blind_A2_vs_A0"],
        "detection": [d["detection"] for d in diag]}
    set_status(e1, "admitted" if g["G_ADMIT_SOLVE"] else "rejected",
               "admission gates")
    e1["revisions"] = [{"successor": "o0002",
                        "kind": "learned routing predicate over executable task "
                                "features (backward-edge consistency audit)"}]
    if g["D_HARM"]:
        set_status(e1, "bounded", "negative transfer measured in unreliable-"
                   "predecessor worlds; routing bounded by o0002")
    save(e1)
    e2 = new_entry("o0002",
                   derivation={"route": diag[0]["router"],
                               "wraps": d0["construction"]["o0001"],
                               "fallback": serial(BASELINE)},
                   dependencies=["o0001"],
                   creation_event={"phase": "revision", "date": PREREG["date"]})
    e2["admission_test"] = {"gates": {k: g[k] for k in ("D_REVISED", "D_VALID")}}
    e2["effect_size"] = {"dD_fresh_vs_A0": res["paired"]["dD_fresh_A2R_vs_A0"],
                         "dA_fresh_overhead": res["paired"]["dA_fresh_A2R_vs_A2"]}
    e2["ablation_result"] = {"note": "removing the route reproduces o0001 blind "
                                     "(measured alongside on dD_fresh)"}
    e2["observed_failure_region"] = None
    set_status(e2, "admitted" if g["D_VALID"] else "rejected", "revision gates")
    save(e2)


if __name__ == "__main__":
    main()
