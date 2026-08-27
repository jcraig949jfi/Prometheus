"""census_v1.py — FIRST ACTION, second iteration: census of the v1 wA/wB/wC triple.

census v0 (results/census_v0.json) REJECTED the v0 design: r02/r03 commuted, monoid growth
was ~2.8^d, 85% of witnesses were non-minimal, M forced in only ~31% of survivors. v1:
affine r03 + explicit omniscient-side family filters (see worlds.py docstring).

Because the family now filters on forcing, the census's job shifts from "is M forced?" to
"is the filtered family NON-VACUOUS and does it have the cost structure the experiment
needs?" (the v0 lesson in aporia/lot/census.py terms: task-population support).

PASS CRITERIA (stated before running):

  C1 ACCEPTANCE       embed-task filter acceptance >= 0.10 in every world (below that the
                      family is rejection-mining a rare coincidence — redesign, don't mine)
  C2 FILTER-VERIFY    forced_all == 1.0 on accepted embed tasks; null tasks contain no M
                      in any minimal solution (re-verified independently of the generator)
  C3 NO-SHORT-EQUIV   no word of length <= 2 functionally equals M (64-state probe)
  C4 HEADROOM         median live P0 nodes >= 10_000 on wA embed tasks, and
                      median live P3/P0 node ratio <= 0.5
  C5 AMBIENT-M        UNFILTERED M-free tasks: frac(any minimal solution contains M)
                      <= 0.20, and null acceptance >= 0.05 (the null stratum exists)
  C6 ADVERSARIAL      wC: macro runtime-failure rate on random valid states in [0.10, 0.60];
                      EXACT guard as disjunction of <= 2 executable probe atoms exists;
                      live median P3/P0 node ratio on hostile tasks >= 1.5 (real harm);
                      live median P3/P0 node ratio on friendly tasks <= 0.7 (partial support)
  C7 PREVALENCE       report-only: frac of random valid (s,t) pairs with L <= 12
  C8 FEASIBILITY      report-only: wall-clock per generated task and per live solve

Metrics unit (feedback_se_on_the_wrong_unit): the unit everywhere is the TASK.
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from primitives import selfcheck, make_prims          # noqa: E402
from worlds import M_WORD, make_worlds                # noqa: E402
import diagnostics as dx                              # noqa: E402

NODE_BUDGET = 6_000_000


def forcing_record(world, omni):
    s, t, w = omni["s"], omni["t"], omni["witness"]
    L = dx.min_dist(world, s, t)
    rec = {"wlen": len(w), "L": L}
    if L is None:
        rec["unreachable_at_dmax"] = True
        return rec
    rec["collapse"] = L < len(w)
    sols = dx.solutions_at(world, s, t, L)
    n = len(sols)
    nm = sum(1 for x in sols if dx.contains_word(x, M_WORD))
    rec.update(n_min_sols=n, n_with_m=nm,
               forced_all=(n > 0 and nm == n), contains_any=(nm > 0))
    return rec


def m_equivalents(world, max_len=4, probes=64):
    rng = random.Random(0xBEEF)
    P = [tuple(rng.randrange(world.m) for _ in range(world.k)) for _ in range(probes)]
    prims = make_prims(world.k, world.m)

    def fp(word):
        out = []
        for s in P:
            for p in word:
                s = prims[p](s)
            out.append(s)
        return tuple(out)

    target = fp(M_WORD)
    counts = {}
    for ln in range(1, max_len + 1):
        eq = 0
        for idx in range(4 ** ln):
            word, v = [], idx
            for _ in range(ln):
                word.append(v % 4)
                v //= 4
            if fp(tuple(word)) == target:
                eq += 1
        counts[ln] = eq
    return counts


# ── live solver (tree IDDFS — the baseline the framework will use) ───────────────────

def make_actions(world, with_macro):
    acts = []
    for p in range(4):
        def act(s, p=p):
            return world.step(p, s), 1
        acts.append((act, (p,)))
    if with_macro:
        def macro(s):
            ex = 0
            for p in M_WORD:
                ex += 1
                s = world.step(p, s)
                if s is None:
                    return None, ex
            return s, ex
        acts.append((macro, M_WORD))
    return acts


def iddfs(world, s, t, actions, dmax=12):
    nodes = execs = 0
    if s == t:
        return (), {"nodes": 0, "execs": 0, "found_at": 0}
    sys.setrecursionlimit(10000)
    for cap in range(1, dmax + 1):
        path = []

        def rec(state, remaining):
            nonlocal nodes, execs
            if remaining == 0:
                return False
            for ai, (act, _) in enumerate(actions):
                ns, ex = act(state)
                execs += ex
                if ns is None:
                    continue
                nodes += 1
                if nodes > NODE_BUDGET:
                    raise MemoryError("node budget")
                path.append(ai)
                if ns == t or rec(ns, remaining - 1):
                    return True
                path.pop()
            return False

        try:
            if rec(s, cap):
                prim_word = tuple(p for ai in path for p in actions[ai][1])
                return prim_word, {"nodes": nodes, "execs": execs, "found_at": cap}
        except MemoryError:
            return None, {"nodes": nodes, "execs": execs, "found_at": None,
                          "budget_exhausted": True}
    return None, {"nodes": nodes, "execs": execs, "found_at": None}


def live_costs(world, omnis, n):
    p0acts = make_actions(world, with_macro=False)
    p3acts = make_actions(world, with_macro=True)
    rows = []
    for omni in omnis[:n]:
        s, t = omni["s"], omni["t"]
        t0 = time.perf_counter()
        w0, c0 = iddfs(world, s, t, p0acts)
        t1 = time.perf_counter()
        row = {"wlen": len(omni["witness"]), "p0": c0,
               "p0_sec": round(t1 - t0, 3),
               "p0_first_sol_has_m": (dx.contains_word(w0, M_WORD) if w0 else None)}
        t2 = time.perf_counter()
        w3, c3 = iddfs(world, s, t, p3acts)
        row["p3"] = c3
        row["p3_sec"] = round(time.perf_counter() - t2, 3)
        if c0["nodes"] and c3["nodes"]:
            row["p3_over_p0_nodes"] = round(c3["nodes"] / c0["nodes"], 4)
        rows.append(row)
    return rows


def guard_existence(world, n_states=400):
    """wC: does an exact guard exist as a disjunction of <= 2 atoms of the executable
    probe language  comp_j(W(s)) == c,  W in {eps, r00..r03, (r01,r02)}?"""
    rng = random.Random(0xFACE)
    states = [world._rand_state(rng) for _ in range(n_states)]

    def macro_fails(s):
        for p in M_WORD:
            s = world.step(p, s)
            if s is None:
                return True
        return False

    fail_mask = 0
    for i, s in enumerate(states):
        if macro_fails(s):
            fail_mask |= 1 << i
    probe_words = [(), (0,), (1,), (2,), (3,), (1, 2)]
    atoms = []
    for w in probe_words:
        for j in range(world.k):
            for c in range(world.m):
                mask = 0
                for i, s in enumerate(states):
                    v = s
                    ok = True
                    for p in w:
                        v = world.step(p, v)
                        if v is None:
                            ok = False
                            break
                    if ok and v[j] == c:
                        mask |= 1 << i
                if mask:
                    atoms.append(((w, j, c), mask))
    fail_rate = bin(fail_mask).count("1") / n_states
    for (a, ma) in atoms:
        if ma == fail_mask:
            return {"fail_rate": round(fail_rate, 4), "exact_guard": [a], "n_atoms": 1}
    for i, (a, ma) in enumerate(atoms):
        if ma | fail_mask != fail_mask:
            continue
        for b, mb in atoms[i + 1:]:
            if mb | fail_mask == fail_mask and (ma | mb) == fail_mask:
                return {"fail_rate": round(fail_rate, 4), "exact_guard": [a, b],
                        "n_atoms": 2}
    return {"fail_rate": round(fail_rate, 4), "exact_guard": None}


def ambient_m_rate(world, n=30, seed=999):
    """UNFILTERED M-free tasks: how often does a minimal solution contain M anyway?"""
    rng = random.Random(seed)
    hits = usable = 0
    for _ in range(n):
        for _ in range(200):
            lx, ly = rng.choice((2, 3)), rng.choice((2, 3))
            w = world._rand_word(rng, lx + 3 + ly, avoid_m=True)
            s = world._rand_state(rng)
            t, _ = world.run_word(w, s)
            if t is not None and t != s:
                break
        L = dx.min_dist(world, s, t)
        if L is None:
            continue
        sols = dx.solutions_at(world, s, t, L)
        if not sols:
            continue
        usable += 1
        if any(dx.contains_word(x, M_WORD) for x in sols):
            hits += 1
    return {"n": usable, "frac_contains_any": round(hits / max(usable, 1), 4)}


def census_world(world, seeds=(101, 202), n_embed=25, n_null=12):
    t0 = time.time()
    out = {"wid": world.wid, "k": world.k, "m": world.m,
           "state_space": world.m ** world.k,
           "m_equivalents_by_len": m_equivalents(world)}
    embed_recs, null_recs = [], []
    embed_omnis, null_omnis = [], []
    for seed in seeds:
        rng = random.Random(seed)
        for _ in range(n_embed):
            task, omni = world.gen_task(rng, embed_m=True)
            assert set(task) == {"start", "target"}, "solver-visible schema leak"
            embed_recs.append(forcing_record(world, omni))
            embed_omnis.append(omni)
        for _ in range(n_null):
            _, omni = world.gen_task(rng, embed_m=False)
            null_recs.append(forcing_record(world, omni))
            null_omnis.append(omni)
    gs = world.gen_stats
    out["embed_acceptance"] = round(gs["embed_ok"] / max(gs["embed_tries"], 1), 4)
    out["null_acceptance"] = round(gs["null_ok"] / max(gs["null_tries"], 1), 4)
    out["embed_n"] = len(embed_recs)
    out["forced_all_frac"] = round(sum(1 for r in embed_recs if r.get("forced_all"))
                                   / len(embed_recs), 4)
    out["null_contains_any_frac"] = round(sum(1 for r in null_recs
                                              if r.get("contains_any"))
                                          / len(null_recs), 4)
    out["min_sol_count_dist"] = {str(v): [r.get("n_min_sols") for r in embed_recs].count(v)
                                 for v in sorted(set(r.get("n_min_sols")
                                                     for r in embed_recs), key=str)}
    out["ambient_unfiltered"] = ambient_m_rate(world)
    rng = random.Random(7)
    hits = 0
    n_prev = 100
    for _ in range(n_prev):
        if dx.min_dist(world, world._rand_state(rng), world._rand_state(rng)) is not None:
            hits += 1
    out["prevalence_L_le_12"] = round(hits / n_prev, 4)
    out["gen_sec"] = round(time.time() - t0, 1)
    return out, embed_omnis, null_omnis


def main():
    selfcheck(6, 11), selfcheck(8, 7), selfcheck(7, 9)
    t_start = time.time()
    worlds = make_worlds()
    report = {"census": "v1", "date": "2026-08-26", "m_word": list(M_WORD)}
    keep = {}
    for wid, world in worlds.items():
        print(f"[census] {wid} analysis ...", flush=True)
        out, embed, null = census_world(world)
        report[wid] = out
        keep[wid] = (embed, null)
        print(f"  acceptance embed={out['embed_acceptance']} null={out['null_acceptance']}"
              f" gen_sec={out['gen_sec']}", flush=True)

    live = {}
    print("[census] live costs ...", flush=True)
    live["wA_embed"] = live_costs(worlds["wA"], keep["wA"][0], n=8)
    live["wB_embed"] = live_costs(worlds["wB"], keep["wB"][0], n=6)
    live["wC_friendly"] = live_costs(worlds["wC"], keep["wC"][0], n=6)
    live["wC_hostile"] = live_costs(worlds["wC"], keep["wC"][1], n=4)
    report["live"] = live
    report["wC_guard"] = guard_existence(worlds["wC"])

    def med(rows, f):
        vals = [f(r) for r in rows if f(r) is not None]
        return statistics.median(vals) if vals else None

    v = {}
    for wid in ("wA", "wB", "wC"):
        r = report[wid]
        v[f"C1_acceptance_{wid}"] = r["embed_acceptance"] >= 0.10
        v[f"C2_filter_verify_{wid}"] = (r["forced_all_frac"] == 1.0
                                        and r["null_contains_any_frac"] == 0.0)
        v[f"C3_no_short_equiv_{wid}"] = (r["m_equivalents_by_len"][1] == 0
                                         and r["m_equivalents_by_len"][2] == 0)
        v[f"C5_ambient_{wid}"] = (r["ambient_unfiltered"]["frac_contains_any"] <= 0.20
                                  and r["null_acceptance"] >= 0.05)
    p0n = med(live["wA_embed"], lambda r: r["p0"]["nodes"])
    ratio = med(live["wA_embed"], lambda r: r.get("p3_over_p0_nodes"))
    v["C4_headroom_p0_median_nodes"] = p0n
    v["C4_p3_over_p0_median"] = ratio
    v["C4_headroom_pass"] = (p0n or 0) >= 10_000 and (ratio or 1) <= 0.5
    g = report["wC_guard"]
    hostile_ratio = med(live["wC_hostile"], lambda r: r.get("p3_over_p0_nodes"))
    friendly_ratio = med(live["wC_friendly"], lambda r: r.get("p3_over_p0_nodes"))
    v["C6_fail_rate_in_band"] = 0.10 <= g["fail_rate"] <= 0.60
    v["C6_exact_guard_exists"] = g["exact_guard"] is not None
    v["C6_hostile_p3_over_p0_median"] = hostile_ratio
    v["C6_friendly_p3_over_p0_median"] = friendly_ratio
    v["C6_negative_transfer_pass"] = (hostile_ratio or 0) >= 1.5
    v["C6_partial_support_pass"] = (friendly_ratio or 1) <= 0.7
    report["verdicts"] = v
    hard = [k for k, val in v.items() if isinstance(val, bool) and not val]
    report["FAILED_CRITERIA"] = hard
    report["CENSUS_PASSES"] = not hard
    report["wall_sec"] = round(time.time() - t_start, 1)

    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "results", "census_v1.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=1, default=str)
    print(json.dumps({k: report[k] for k in
                      ("verdicts", "FAILED_CRITERIA", "CENSUS_PASSES", "wall_sec")},
                     indent=1, default=str))
    print(f"[census] written {out_path}")


if __name__ == "__main__":
    main()
