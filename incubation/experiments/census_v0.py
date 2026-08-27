"""census_v0.py — FIRST ACTION: reachability/forcing census of the smallest wA/wB/wC triple.

Run BEFORE building the framework (spec section 13). The lesson this encodes, inherited from
aporia/lot/census.py (2026-08-26): prove the target phenomenon is reachable and non-vacuous in
the population that could generate it — here, that the intended composition M is FORCED in the
minimal-solution population, not merely present in the generator's witness.

PASS CRITERIA (stated before running; a world failing any is redesigned, not rationalised):

  C1 NO-COLLAPSE      frac(L == |witness|) >= 0.80 over embed tasks (else the space is too
                      small or the generator cancels, and witnesses are not minimal — the
                      exact failure world v2 hit: target shape unreachable in population)
  C2 FORCING          among non-collapsed embed tasks: frac(ALL minimal solutions contain M
                      contiguously) >= 0.90, in wA, wB, and wC-friendly
  C3 NO-SHORT-EQUIV   no word of length <= 2 is functionally equal to M (64-state probe)
  C4 HEADROOM         median live P0 nodes >= 10_000 on wA embed tasks, and
                      median live P3/P0 node ratio <= 0.5 (a macro can matter, measurably)
  C5 NULL-CONTRAST    frac(any minimal solution contains M) <= 0.20 on M-free tasks
                      (discovery has a contrast to find; M is not ambient)
  C6 ADVERSARIAL      wC: macro runtime-failure rate on random valid states in [0.10, 0.60];
                      an EXACT guard exists as a disjunction of <= 2 atoms in the executable
                      probe language; hostile tasks: frac(minimal sols contain M) <= 0.20;
                      live median P3/P0 node ratio on hostile tasks >= 1.5 (real harm)
  C7 PREVALENCE       report-only: frac of random valid (s,t) pairs with L <= 12
  C8 FEASIBILITY      report-only: wall-clock per live solve

Metrics unit note (feedback_se_on_the_wrong_unit): the unit everywhere is the TASK.
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from primitives import selfcheck, make_prims  # noqa: E402
from worlds import M_WORD, make_worlds        # noqa: E402

HALF = 6            # meet-in-the-middle half-depth for min-distance (dmax = 12)
NODE_BUDGET = 6_000_000


# ── exact minimal-solution machinery (omniscient diagnostics — never solver-visible) ──

def bfs_side(world, root, half, backward):
    """state -> min depth, from root, to depth `half`. Validity semantics:
    forward: every entered state must be valid; backward: only expand from valid states
    (an invalid state may sit at the meet layer but can never join a forward state)."""
    depth = {root: 0}
    frontier = [root]
    fns = world.invs if backward else world.prims
    for d in range(1, half + 1):
        nxt = []
        for s in frontier:
            if backward and not world.valid(s):
                continue
            for f in fns:
                ns = f(s)
                if not backward and not world.valid(ns):
                    continue
                if ns not in depth:
                    depth[ns] = d
                    nxt.append(ns)
        frontier = nxt
    return depth


def min_dist(world, s, t, half=HALF):
    fw = bfs_side(world, s, half, backward=False)
    bw = bfs_side(world, t, half, backward=True)
    best = None
    for u, df in fw.items():
        db = bw.get(u)
        if db is not None and (best is None or df + db < best):
            best = df + db
    return best        # None means > 2*half


def enum_words(world, root, length, backward):
    """ALL words of exactly `length` (validity-pruned): endpoint-state -> [words].
    Backward words are returned forward-oriented (they run endpoint -> root)."""
    out = {}
    fns = world.invs if backward else world.prims
    word = [0] * length

    def rec(state, i):
        if i == length:
            out.setdefault(state, []).append(tuple(word) if not backward
                                             else tuple(reversed(word)))
            return
        if backward and not world.valid(state):
            return
        for p in range(4):
            ns = fns[p](state)
            if not backward and not world.valid(ns):
                continue
            word[i] = p
            rec(ns, i + 1)

    if length == 0:
        return {root: [()]}
    rec(root, 0)
    return out


def solutions_at(world, s, t, d):
    a = d // 2
    fw = enum_words(world, s, a, backward=False)
    bw = enum_words(world, t, d - a, backward=True)
    sols = []
    for u, ws in fw.items():
        tail = bw.get(u)
        if tail:
            sols.extend(wf + wb for wf in ws for wb in tail)
    return sols


def has_m(word):
    return any(word[i:i + 3] == M_WORD for i in range(len(word) - 2))


def forcing_record(world, omni):
    s, t, w = omni["s"], omni["t"], omni["witness"]
    L = min_dist(world, s, t)
    rec = {"wlen": len(w), "L": L}
    if L is None:
        rec["collapse"] = False
        rec["unreachable_at_dmax"] = True
        return rec
    rec["collapse"] = L < len(w)
    sols = solutions_at(world, s, t, L)
    n = len(sols)
    nm = sum(1 for x in sols if has_m(x))
    rec.update(n_min_sols=n, n_with_m=nm,
               forced_all=(n > 0 and nm == n), contains_any=(nm > 0))
    if rec["forced_all"]:
        margin = None
        for d in (L + 1, L + 2):
            if any(not has_m(x) for x in solutions_at(world, s, t, d)):
                margin = d - L
                break
        rec["mfree_margin"] = margin if margin is not None else ">=3"
    return rec


# ── functional-equivalence audit of M ────────────────────────────────────────────────

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


# ── census proper ────────────────────────────────────────────────────────────────────

def census_world(world, seeds=(101, 202, 303), n_embed=30, n_null=15):
    out = {"wid": world.wid, "k": world.k, "m": world.m,
           "state_space": world.m ** world.k,
           "m_equivalents_by_len": m_equivalents(world)}
    embed_recs, null_recs = [], []
    hostile_omnis, friendly_omnis = [], []
    for seed in seeds:
        rng = random.Random(seed)
        for _ in range(n_embed):
            task, omni = world.gen_task(rng, embed_m=True)
            assert set(task) == {"start", "target"}, "solver-visible schema leak"
            assert "witness" not in task
            embed_recs.append(forcing_record(world, omni))
            friendly_omnis.append(omni)
        for _ in range(n_null):
            _, omni = world.gen_task(rng, embed_m=False)
            null_recs.append(forcing_record(world, omni))
            hostile_omnis.append(omni)

    def frac(recs, key, base=None):
        pool = [r for r in recs if base is None or base(r)]
        return round(sum(1 for r in pool if r.get(key)) / max(len(pool), 1), 4), len(pool)

    nc, _ = frac(embed_recs, "collapse")
    out["embed_n"] = len(embed_recs)
    out["frac_collapse"] = nc
    out["frac_L_eq_wlen"] = round(sum(1 for r in embed_recs
                                      if r["L"] == r["wlen"]) / len(embed_recs), 4)
    noncol = [r for r in embed_recs if not r.get("collapse") and r.get("L") is not None]
    out["forced_all_frac"], out["forced_all_base_n"] = frac(noncol, "forced_all")
    out["contains_any_frac"], _ = frac(noncol, "contains_any")
    margins = [r.get("mfree_margin") for r in noncol if r.get("forced_all")]
    out["mfree_margin_dist"] = {str(v): margins.count(v) for v in set(margins)}
    out["min_sol_count_dist"] = {str(v): [r.get("n_min_sols") for r in noncol].count(v)
                                 for v in set(r.get("n_min_sols") for r in noncol)}
    out["null_n"] = len(null_recs)
    out["null_contains_any_frac"], _ = frac(
        [r for r in null_recs if r.get("L") is not None], "contains_any")
    out["null_frac_L_eq_wlen"] = round(sum(1 for r in null_recs
                                           if r["L"] == r["wlen"]) / len(null_recs), 4)

    # prevalence: random valid pairs
    rng = random.Random(7)
    hits = 0
    n_prev = 120
    for _ in range(n_prev):
        a = world._rand_state(rng)
        b = world._rand_state(rng)
        if min_dist(world, a, b) is not None:
            hits += 1
    out["prevalence_L_le_12"] = round(hits / n_prev, 4)
    return out, friendly_omnis, hostile_omnis


def live_costs(world, omnis, n, with_macro_arms=True):
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
               "p0_first_sol_has_m": (has_m(w0) if w0 else None)}
        if with_macro_arms:
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


def main():
    selfcheck()
    t_start = time.time()
    worlds = make_worlds()
    report = {"census": "v0", "date": "2026-08-26",
              "m_word": list(M_WORD), "half": HALF}
    live = {}
    keep = {}
    for wid, world in worlds.items():
        print(f"[census] {wid} analysis ...", flush=True)
        out, friendly, hostile = census_world(world)
        report[wid] = out
        keep[wid] = (friendly, hostile)

    print("[census] live costs wA ...", flush=True)
    live["wA_embed"] = live_costs(worlds["wA"], keep["wA"][0], n=6)
    print("[census] live costs wB ...", flush=True)
    live["wB_embed"] = live_costs(worlds["wB"], keep["wB"][0], n=4)
    print("[census] live costs wC friendly ...", flush=True)
    live["wC_friendly"] = live_costs(worlds["wC"], keep["wC"][0], n=4)
    print("[census] live costs wC hostile ...", flush=True)
    live["wC_hostile"] = live_costs(worlds["wC"], keep["wC"][1], n=3)
    report["live"] = live
    report["wC_guard"] = guard_existence(worlds["wC"])

    # ── verdicts against the pre-stated criteria ────────────────────────────────
    def med(rows, f):
        vals = [f(r) for r in rows if f(r) is not None]
        return statistics.median(vals) if vals else None

    v = {}
    for wid in ("wA", "wB", "wC"):
        v[f"C1_no_collapse_{wid}"] = report[wid]["frac_L_eq_wlen"] >= 0.80
        v[f"C2_forcing_{wid}"] = report[wid]["forced_all_frac"] >= 0.90
        v[f"C3_no_short_equiv_{wid}"] = (report[wid]["m_equivalents_by_len"][1] == 0
                                         and report[wid]["m_equivalents_by_len"][2] == 0)
        v[f"C5_null_contrast_{wid}"] = report[wid]["null_contains_any_frac"] <= 0.20
    p0n = med(live["wA_embed"], lambda r: r["p0"]["nodes"])
    ratio = med(live["wA_embed"], lambda r: r.get("p3_over_p0_nodes"))
    v["C4_headroom_p0_median_nodes"] = p0n
    v["C4_headroom_pass"] = (p0n or 0) >= 10_000 and (ratio or 1) <= 0.5
    v["C4_p3_over_p0_median"] = ratio
    g = report["wC_guard"]
    hostile_ratio = med(live["wC_hostile"], lambda r: r.get("p3_over_p0_nodes"))
    v["C6_fail_rate_in_band"] = 0.10 <= g["fail_rate"] <= 0.60
    v["C6_exact_guard_exists"] = g["exact_guard"] is not None
    v["C6_hostile_m_ambient"] = report["wC"]["null_contains_any_frac"]
    v["C6_hostile_p3_over_p0_median"] = hostile_ratio
    v["C6_negative_transfer_pass"] = (hostile_ratio or 0) >= 1.5
    report["verdicts"] = v
    hard = [k for k, val in v.items()
            if isinstance(val, bool) and not val]
    report["FAILED_CRITERIA"] = hard
    report["CENSUS_PASSES"] = not hard
    report["wall_sec"] = round(time.time() - t_start, 1)

    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "results", "census_v0.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=1, default=str)
    print(json.dumps({k: report[k] for k in
                      ("verdicts", "FAILED_CRITERIA", "CENSUS_PASSES", "wall_sec")},
                     indent=1, default=str))
    print(f"[census] written {out_path}")


if __name__ == "__main__":
    main()
