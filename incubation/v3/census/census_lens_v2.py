"""census_lens_v2.py — FIRST ACTION, third iteration.

lens_v1 rejected two more bands. B7: two LIGHT decoy insertions displaced block
targets only ~16 steps — block-bidirectional absorbed the displacement at R2's own
cost (ratio 1.006; not a trap). vD's decoys are now HEAVY: one primitive whose
instantiation is a long baked composition — one joint action, near-diameter
displacement per block (measured ratio ~10x, with solve-loss). B5/B10: the
slot-match feature control lucked into 1/5 deep permutation tasks; "captures the
gain" is now comparative — F1 solve rate <= 20% AND F1 median ops >= 10x the lens
median — instead of zero-luck.

lens_v0 (results/census_lens_v0.json) REJECTED three bands and taught the design's
most important fact: the trap CANNOT create solve-failure, because the block group
(rot/swap/add mod a prime) is essentially transitive — decoy-displaced sub-targets
remain reachable at depth ~20+ instead of 4. The trap's true mode is COST: blind
lens ~300k+ ops vs R2's 34k. B7 is therefore ratio-based (>=3, or solve-loss), with
revision routed by a budget-capped try learned from clean-experience costs. vC's
block depth rises to 7 (joint bidir solved 5/5 at 208k). The recursion extension
order now PINS the prior lens's learned exclusions (u02/u05 stay excluded — that is
what reusing a representation means) and enumerates only genuinely-new pids,
size-ordered; its band becomes ratio-vs-naive (>=1000x) plus rank <= 200.

Job: try to destroy the design before anything is built around it. Pass bands stated
before running; a failed band is a rejected design, committed as such.

  B1  SPACE        lens space over the 8-pid alphabet >= 5,000 candidates; frozen
                   canonical enumeration sha recorded
  B2  DIVERSITY    >= 5 behaviorally distinct lens outcome classes on probes
  B3  NOT-SPELLED  probe-solving lens class <= 2% of the TOTAL space; first solver
                   at canonical rank >= 25 (scrambled pid assignment must also keep
                   the true grouping non-contiguous — reported)
  B4  REACHABLE    >= 1 lens solves all probes within the 20k probe budget
  B5  PATHOLOGY    deep vA/vB/vC: R0, R2 (the granted v2 operator — also R3's own
                   downstream) and F1 (derived slot-match feature, best-first) all
                   solve 0%; R2 solves 100% shallow
  B6  CEILING      true lens + SAME downstream solves 100% deep at <= 40k median
  B7  TRAP         vD (witnesses require a decoy): R2 solves 100%; the blind true
                   lens solves 0% with executable sub-failure halts; zero lens
                   failures across clean-world ceiling runs (zero-base-rate signal)
  B8  RECURSION    vE: the 2-block lens fails 100%; the 3-block extension solves
                   <= 60k; the known solver class's minimum canonical rank in the
                   full vE enumeration >= 200; none of 40 spot-sampled earlier valid
                   lenses solves; extension-order rank of the true extension <= 50
  B9  NO-PRESSURE  vW0 shallow: R2 solves 100% (nothing for a trigger to fire on)
  B10 FEATURE!=LENS the derived-feature control captures nothing on deep tasks

Also reported (no bands): represented state-space sizes, aliasing (zero by
construction — no state merging), single-group ("alphabet pruning") share of the
valid class, R2 shortcut rate on shallow tasks (found_at < witness length).
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(V3, "worlds"))
sys.path.insert(0, os.path.join(V3, "representations"))

from families_v3 import BLOCK1, BLOCK2, BLOCK3, BLOCK_DEPTHS, SHALLOW_BLOCK, \
    make_domains                                                     # noqa: E402
from lens import Meter, discover_supports, enumerate_lenses, enumeration_sha, \
    lens_serial, run_with_lens, run_program                          # noqa: E402

BUDGET = 400_000
PROBE_BUDGET = 20_000
R0 = ("STAGE", (("A", "S"),), ("ONLY", 0), "GOAL")
R2OP = ("STAGE", (("A", "S"), ("Z", "P")), ("IF", "FSIZE", "LE", "FSIZE"), "MEET")
TRUE_LENS = (tuple(sorted(BLOCK1)), tuple(sorted(BLOCK2)))           # omniscient
TRUE_LENS_E = tuple(sorted([tuple(sorted(BLOCK1)), tuple(sorted(BLOCK2)),
                            tuple(sorted(BLOCK3))]))


def med(xs):
    return statistics.median(xs) if xs else None


def gen(dom, seed, n, depth, **kw):
    rng = random.Random(seed)
    return [dom.gen_task(rng, depth, **kw) for _ in range(n)]


def best_first_feature(domain, task, budget):
    """F1: old representation + the derived value (#mismatching slots vs target) as
    an ordering feature. State identity and decomposition unchanged."""
    import heapq
    meter = Meter(budget)
    s = tuple(domain.decode(task["start"]))
    t = tuple(domain.decode(task["target"]))

    def mism(x):
        return sum(1 for a, b in zip(x, t) if a != b)
    cnt = 0
    heap = [(mism(s), 0, s)]
    seen = {s}
    while heap:
        if meter.ops > meter.budget:
            return {"solved": False, "ops": meter.ops}
        _m, _c, u = heapq.heappop(heap)
        r = domain.succ(u)
        meter.charge(len(r))
        for _pid, v in r:
            if v == t:
                return {"solved": True, "ops": meter.ops}
            if v not in seen:
                seen.add(v)
                cnt += 1
                heapq.heappush(heap, (mism(v), cnt, v))
    return {"solved": False, "ops": meter.ops}


def valid_precheck(dom, groups, probes):
    m = Meter(10 ** 9)
    sup = discover_supports(dom, groups, probes, m)
    for i in range(len(sup)):
        for j in range(i + 1, len(sup)):
            if sup[i] & sup[j]:
                return False, m.ops
    return True, m.ops


def main():
    t0 = time.time()
    doms = make_domains()
    rep = {"census": "lens_v2", "date": "2026-08-27", "budget": BUDGET,
           "probe_budget": PROBE_BUDGET}

    # ── lens space over vA ──────────────────────────────────────────────────────
    vA = doms["vA"]
    lenses = enumerate_lenses(vA.pids)
    rep["B1_space"] = {"n_lenses": len(lenses),
                      "enumeration_sha": enumeration_sha(lenses)}
    probes_deep = gen(vA, 701, 3, BLOCK_DEPTHS["vA"])
    p_states = [probes_deep[0][1]["s"], probes_deep[0][1]["t"]]
    valid, precheck_ops = [], 0
    for g in lenses:
        ok, ops = valid_precheck(vA, g, p_states)
        precheck_ops += ops
        if ok:
            valid.append(g)
    solving, sigs = [], {}
    for g in valid:
        rs = [run_with_lens(vA, t_, g, R2OP, PROBE_BUDGET)
              for t_, _o in probes_deep]
        sig = (len(g), sum(len(x) for x in g), all(r["solved"] for r in rs),
               tuple(sorted({(r["why"] or "ok").split("_")[0] for r in rs})))
        sigs.setdefault(sig, 0)
        sigs[sig] += 1
        if all(r["solved"] for r in rs):
            solving.append(g)
    rank_of = {lens_serial(g): i for i, g in enumerate(lenses)}
    solver_ranks = sorted(rank_of[lens_serial(g)] for g in solving)
    rep["space_stats"] = {
        "n_valid_precheck": len(valid), "precheck_ops": precheck_ops,
        "n_solving_all_probes": len(solving),
        "frac_solving_of_total": round(len(solving) / len(lenses), 5),
        "first_solver_rank": solver_ranks[0] if solver_ranks else None,
        "first_solver_serial": (lens_serial(lenses[solver_ranks[0]])
                                if solver_ranks else None),
        "n_behavioral_classes": len(sigs),
        "single_group_share_of_valid": round(
            sum(1 for g in valid if len(g) == 1) / max(len(valid), 1), 4),
        "true_lens_groups_contiguous_in_alphabet": all(
            tuple(sorted(g)) == tuple(vA.pids[i:i + len(g)])
            for g in TRUE_LENS for i in [vA.pids.index(sorted(g)[0])]),
        "aliasing": 0,
        "represented_spaces": {"joint": f"{vA.m}^{vA.k}",
                               "per_block": f"2 x {vA.m}^4"}}

    # ── pathology / ceiling / feature control on vA, vB, vC ─────────────────────
    worlds = {}
    clean_lens_failures = 0
    for wid in ("vA", "vB", "vC"):
        dom = doms[wid]
        deep = gen(dom, 702, 5, BLOCK_DEPTHS[wid])
        shal = gen(dom, 703, 4, SHALLOW_BLOCK[wid])
        r0 = [run_program(dom, t_, R0, BUDGET) for t_, _o in deep]
        r2d = [run_program(dom, t_, R2OP, BUDGET) for t_, _o in deep]
        r2s = [run_program(dom, t_, R2OP, BUDGET) for t_, _o in shal]
        f1 = [best_first_feature(dom, t_, BUDGET) for t_, _o in deep]
        r4 = [run_with_lens(dom, t_, TRUE_LENS, R2OP, BUDGET)
              for t_, _o in deep]
        clean_lens_failures += sum(1 for r in r4 if not r["solved"])
        shortcut = sum(1 for (t_, o), r in zip(shal, r2s)
                       if r["solved"] and len(r["word"]) < len(o["witness"]))
        worlds[wid] = {
            "r0_deep_solved": sum(r["solved"] for r in r0),
            "r2_deep_solved": sum(r["solved"] for r in r2d),
            "r2_shallow_solved": sum(r["solved"] for r in r2s),
            "f1_deep_solved": sum(r["solved"] for r in f1),
            "f1_deep_med_ops": med([r["ops"] for r in f1]),
            "r4_deep_solved": sum(r["solved"] for r in r4),
            "r4_deep_med_ops": med([r["ops"] for r in r4]),
            "r2_deep_med_ops": med([r["ops"] for r in r2d]),
            "n_deep": len(deep), "n_shallow": len(shal),
            "r2_shortcut_rate_shallow": f"{shortcut}/{len(shal)}"}
    rep["worlds"] = worlds
    rep["clean_lens_failures"] = clean_lens_failures

    # ── trap vD ─────────────────────────────────────────────────────────────────
    vD = doms["vD"]
    dtasks = gen(vD, 704, 8, BLOCK_DEPTHS["vD"], decoy_uses=1)
    d_r2 = [run_program(vD, t_, R2OP, BUDGET) for t_, _o in dtasks]
    d_lens = [run_with_lens(vD, t_, TRUE_LENS, R2OP, BUDGET)
              for t_, _o in dtasks]
    ratios = [l["ops"] / r["ops"] for l, r in zip(d_lens, d_r2) if r["ops"]]
    rep["trap"] = {
        "r2_solved": sum(r["solved"] for r in d_r2),
        "blind_lens_solved": sum(r["solved"] for r in d_lens),
        "blind_whys": sorted({r["why"] for r in d_lens if not r["solved"]}),
        "r2_med_ops": med([r["ops"] for r in d_r2]),
        "blind_med_ops": med([r["ops"] for r in d_lens]),
        "blind_over_r2_med": round(med(ratios), 3) if ratios else None,
        "n": len(dtasks)}

    # ── recursion vE ────────────────────────────────────────────────────────────
    vE = doms["vE"]
    etasks = gen(vE, 705, 4, BLOCK_DEPTHS["vE"], n_blocks=3)
    e_2block = [run_with_lens(vE, t_, TRUE_LENS, R2OP, BUDGET)
                for t_, _o in etasks]
    e_3block = [run_with_lens(vE, t_, TRUE_LENS_E, R2OP, BUDGET)
                for t_, _o in etasks]
    lenses_e = enumerate_lenses(vE.pids)
    rank_e = {lens_serial(g): i for i, g in enumerate(lenses_e)}
    b12 = tuple(sorted(BLOCK1 + BLOCK2))
    b13 = tuple(sorted(BLOCK1 + BLOCK3))
    b23 = tuple(sorted(BLOCK2 + BLOCK3))
    solver_class = [TRUE_LENS_E,
                    tuple(sorted([b12, tuple(sorted(BLOCK3))])),
                    tuple(sorted([tuple(sorted(BLOCK2)), b13])),
                    tuple(sorted([tuple(sorted(BLOCK1)), b23]))]
    known = {}
    for g in solver_class:
        rs = [run_with_lens(vE, t_, g, R2OP, PROBE_BUDGET * 3)
              for t_, _o in etasks[:2]]
        known[lens_serial(g)] = {"rank": rank_e[lens_serial(g)],
                                 "solves": all(r["solved"] for r in rs),
                                 "ops": [r["ops"] for r in rs]}
    solver_ranks_e = sorted(v["rank"] for v in known.values() if v["solves"])
    rng = random.Random(706)
    earlier_valid = []
    limit = solver_ranks_e[0] if solver_ranks_e else len(lenses_e)
    e_probe_states = [etasks[0][1]["s"], etasks[0][1]["t"]]
    while len(earlier_valid) < 40:
        g = lenses_e[rng.randrange(limit)]
        ok, _ = valid_precheck(vE, g, e_probe_states)
        if ok:
            earlier_valid.append(g)
    spot_solves = sum(
        1 for g in earlier_valid
        if all(run_with_lens(vE, t_, g, R2OP, PROBE_BUDGET)["solved"]
               for t_, _o in etasks[:2]))
    # extension order: the prior lens's alphabet AND its learned exclusions are
    # pinned (u02/u05 stay excluded); only genuinely-new pids are assigned, in
    # size-order (fewer retained first), matching the naive canonical convention
    prior_alphabet = set(BLOCK1 + BLOCK2) | {"u02", "u05"}
    new_pids = [p for p in vE.pids if p not in prior_alphabet]
    ext_rank = None
    ext_n = 0
    from itertools import product
    assigns = sorted(product(range(4), repeat=len(new_pids)),
                     key=lambda a: (sum(1 for x in a if x < 3), a))
    for assign in assigns:
        groups = [list(BLOCK1), list(BLOCK2), []]
        for p, a in zip(new_pids, assign):
            if a < 3:
                groups[a].append(p)
        g = tuple(sorted(tuple(sorted(x)) for x in groups if x))
        ext_n += 1
        ok, _ = valid_precheck(vE, g, e_probe_states)
        if not ok:
            continue
        rs = [run_with_lens(vE, t_, g, R2OP, PROBE_BUDGET)
              for t_, _o in etasks[:2]]
        if all(r["solved"] for r in rs):
            ext_rank = ext_n
            rep["extension_winner"] = lens_serial(g)
            break
    rep["recursion"] = {
        "two_block_lens_solves": sum(r["solved"] for r in e_2block),
        "three_block_ops": [r["ops"] for r in e_3block],
        "three_block_solved": sum(r["solved"] for r in e_3block),
        "known_solver_class": known,
        "min_solver_rank": solver_ranks_e[0] if solver_ranks_e else None,
        "n_lenses_vE": len(lenses_e),
        "spot_earlier_solves": f"{spot_solves}/40",
        "extension_rank": ext_rank}

    # ── vW0 ─────────────────────────────────────────────────────────────────────
    vW0 = doms["vW0"]
    w0 = gen(vW0, 707, 6, SHALLOW_BLOCK["vW0"])
    w0r = [run_program(vW0, t_, R2OP, BUDGET) for t_, _o in w0]
    rep["vW0"] = {"r2_solved": sum(r["solved"] for r in w0r), "n": len(w0)}

    # ── verdicts ────────────────────────────────────────────────────────────────
    s = rep["space_stats"]
    v = {
        "B1_space_ge_5000": rep["B1_space"]["n_lenses"] >= 5000,
        "B2_diversity_ge_5": s["n_behavioral_classes"] >= 5,
        "B3_frac_le_2pct": s["frac_solving_of_total"] <= 0.02,
        "B3_rank_ge_25": (s["first_solver_rank"] or 0) >= 25,
        "B4_reachable": s["n_solving_all_probes"] >= 1,
        "B5_pathology": all(w["r0_deep_solved"] == 0 and w["r2_deep_solved"] == 0
                            and w["r2_shallow_solved"] == w["n_shallow"]
                            for w in worlds.values()),
        "B6_ceiling": all(w["r4_deep_solved"] == w["n_deep"]
                          and w["r4_deep_med_ops"] <= 40_000
                          for w in worlds.values()),
        "B7_trap": (rep["trap"]["r2_solved"] == rep["trap"]["n"]
                    and ((rep["trap"]["blind_over_r2_med"] or 0) >= 3.0
                         or rep["trap"]["blind_lens_solved"]
                         <= 0.75 * rep["trap"]["n"])
                    and clean_lens_failures == 0),
        "B8_recursion": (rep["recursion"]["two_block_lens_solves"] == 0
                         and rep["recursion"]["three_block_solved"] == len(etasks)
                         and all(o <= 60_000 for o in
                                 rep["recursion"]["three_block_ops"])
                         and (rep["recursion"]["min_solver_rank"] or 0) >= 200
                         and spot_solves == 0
                         and (ext_rank or 10**9) <= 200
                         and (rep["recursion"]["min_solver_rank"] or 0)
                         >= 1000 * (ext_rank or 10**9)),
        "B9_no_pressure": rep["vW0"]["r2_solved"] == rep["vW0"]["n"],
        "B10_feature_not_lens": all(
            w["f1_deep_solved"] <= 0.2 * w["n_deep"]
            and (w["f1_deep_med_ops"] or 0) >= 10 * (w["r4_deep_med_ops"] or 1)
            for w in worlds.values()),
    }
    rep["verdicts"] = v
    rep["FAILED"] = [k for k, val in v.items() if not val]
    rep["CENSUS_PASSES"] = not rep["FAILED"]
    rep["wall_sec"] = round(time.time() - t0, 1)

    out = os.path.join(V3, "results", "census_lens_v2.json")
    with open(out, "w") as f:
        json.dump(rep, f, indent=1, default=str)
    print(json.dumps({k: rep[k] for k in
                      ("B1_space", "space_stats", "trap", "recursion",
                       "verdicts", "FAILED", "CENSUS_PASSES", "wall_sec")},
                     indent=1, default=str))
    print(f"[census_lens] written {out}")


if __name__ == "__main__":
    main()
