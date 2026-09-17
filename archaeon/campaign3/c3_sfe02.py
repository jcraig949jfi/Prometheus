"""C3-SFE-02 -- ANATOMY OF THE HALF-CREDIT SHELF (campaign 3, slot 2; parent C3-SFE-01).

    python -m archaeon.campaign3.c3_sfe02 [--children 400 --basin-samples 40] [--dry-run]

Mechanism archaeology of the bottleneck, not another long run. The shelf organisms are
C3-SFE-01's final elites at SHELF level (and its summit elites, if any); random generation-0
organisms are the neighbourhood control. For each organism, M one-step children under the
grammar (proteus descend, no mate) are evaluated on a fixed W2_K2 battery with per-ask credit
and classified against the parent:

  neutral        |r - r_parent| < 1/32                useful        r > r_parent
  destructive    r < r_parent                          summit_1step  r >= 0.90
  second_up      the UNSOLVED stream's credit rises >= 0.125 (with the solved stream still >= 0.75)
  first_down     the SOLVED stream's credit falls below 0.5
  tradeoff       second_up AND first_down (solving stream 2 costs stream 1)
  deceptive      r > r_parent but the unsolved stream did not rise (gain on the solved stream's residual)
  valley         second_up children exist ONLY among r < r_parent children

plus a greedy-ascent BASIN probe from K sampled children (best-of-30 for 3 steps: fraction
reaching >= 0.90), the profile of every shelf organism (which stream it solves), a
RECOMBINATION probe between complementary shelf organisms (grammar splice, 200 tries: any
child >= 0.75 on both streams?), and opcode edit distances between shelf and summit elites.
The five explanations are decided by preregistered rules; none is forced.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List, Optional

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.wse import reachability as R
from archaeon.wse.evolve import evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, REPO
from archaeon.campaign3.c3base import CAMPAIGN_SEED, Experiment3

TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
MASK62 = (1 << 62) - 1
EPS = 1.0 / 32
STREAM_SOLVED = 0.75
SECOND_UP = 0.125


def battery():
    return episodes_for(TARGET, CAMPAIGN_SEED, "train", 424242, 16)


def score(m: dict, eps) -> dict:
    e = evaluate(m, eps, rng_seed=5)
    pa = e["per_ask_reward"] + [0.0, 0.0]
    return {"r": e["reward"], "a0": pa[0], "a1": pa[1]}


def classify(parent: dict, child: dict) -> dict:
    solved = 0 if parent["a0"] >= parent["a1"] else 1
    unsolved = 1 - solved
    ps, pu = (parent["a0"], parent["a1"]) if solved == 0 else (parent["a1"], parent["a0"])
    cs, cu = (child["a0"], child["a1"]) if solved == 0 else (child["a1"], child["a0"])
    d = child["r"] - parent["r"]
    second_up = (cu - pu) >= SECOND_UP
    first_down = cs < 0.5 and ps >= 0.5
    return {"neutral": abs(d) < EPS, "useful": d >= EPS, "destructive": d <= -EPS, "summit": child["r"] >= R.SUMMIT_MIN,
            "second_up": second_up, "second_up_keep": second_up and cs >= STREAM_SOLVED, "first_down": first_down, "tradeoff": second_up and first_down,
            "deceptive": d >= EPS and not second_up, "second_up_below": second_up and d <= -EPS}


def neighbourhood(m: dict, eps, M: int, seed: int) -> dict:
    org = G.organism_record(dict(m), None, 0)
    p = score(m, eps)
    counts: Dict[str, int] = {}
    ops: Dict[str, Dict[str, int]] = {}
    best_child = None
    for i in range(M):
        child, rec = descend(org, seed_from("c3.sfe02.nb", seed, i) & MASK62)
        c = score(child["manifest"], eps)
        cl = classify(p, c)
        op = rec["operators"][0]["operator"] if rec["operators"] else "none"
        for k, v in cl.items():
            counts[k] = counts.get(k, 0) + int(v)
            if v:
                ops.setdefault(k, {}); ops[k][op] = ops[k].get(op, 0) + 1
        if best_child is None or c["r"] > best_child["r"]:
            best_child = dict(c, op=op)
    fr = {k: round(v / M, 4) for k, v in counts.items()}
    fr["valley"] = bool(counts.get("second_up", 0) > 0 and counts.get("second_up_keep", 0) == 0)
    return {"parent": p, "fractions": fr, "ops_by_class": {k: dict(sorted(v.items(), key=lambda z: -z[1])[:4]) for k, v in ops.items()}, "best_child": best_child}


def basin(m: dict, eps, K: int, seed: int, steps: int = 3, breadth: int = 30) -> dict:
    """From K sampled one-step children, best-of-`breadth` greedy ascent for `steps` steps."""
    org = G.organism_record(dict(m), None, 0)
    reached = 0; best_end = 0.0; path_r = []
    for i in range(K):
        cur, _ = descend(org, seed_from("c3.sfe02.basin", seed, i) & MASK62)
        r = score(cur["manifest"], eps)["r"]
        for s in range(steps):
            cands = [descend(cur, seed_from("c3.sfe02.basin.step", seed, i, s, j) & MASK62)[0] for j in range(breadth)]
            scored = [(score(c["manifest"], eps)["r"], c) for c in cands]
            br, bc = max(scored, key=lambda z: z[0])
            if br > r:
                cur, r = bc, br
            if r >= R.SUMMIT_MIN:
                break
        reached += int(r >= R.SUMMIT_MIN); best_end = max(best_end, r); path_r.append(round(r, 4))
    return {"basin_share": round(reached / K, 4), "best_end": round(best_end, 4), "end_rewards": path_r}


def recombine(a: dict, b: dict, eps, n: int, seed: int) -> dict:
    """Grammar splice between two complementary shelf organisms (both directions)."""
    oa, ob = G.organism_record(dict(a), None, 0), G.organism_record(dict(b), None, 0)
    joined = 0; best = 0.0; best_pa = None
    for i in range(n):
        p, q = (oa, ob) if i % 2 == 0 else (ob, oa)
        child, _ = descend(p, seed_from("c3.sfe02.recomb", seed, i) & MASK62, mate=q, force_operator="splice")
        c = score(child["manifest"], eps)
        if c["a0"] >= STREAM_SOLVED and c["a1"] >= STREAM_SOLVED:
            joined += 1
        if c["r"] > best:
            best, best_pa = c["r"], (c["a0"], c["a1"])
    return {"tries": n, "joined": joined, "joined_frac": round(joined / n, 4), "best": round(best, 4), "best_per_ask": best_pa}


def edit_distance(g1: List[int], g2: List[int]) -> int:
    a = [w % 25 for w in g1[0::4]]; b = [w % 25 for w in g2[0::4]]
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def strategy_signature(m: dict, eps) -> dict:
    """Per ask: does the organism output the asked stream's value (correct), the LAST PUT value
    (a last-value strategy), some OTHER put value, or nothing? (C3-SFE-01 L3-004.)"""
    from proteus.foundry.prng import SplitMix64 as _SM
    from proteus.foundry.vm import Player
    from archaeon.wse.worlds import K_PUT
    player = Player(m)
    counts = {"correct": 0, "last_value": 0, "first_value": 0, "other_put": 0, "none": 0, "asks": 0}
    for ei, ep in enumerate(eps):
        st = player.fresh_state(); rng = _SM(seed_from("wse.vmrng", 5, ei))
        puts = []
        for ti, words in enumerate(ep.ticks):
            if words and words[0] == K_PUT:
                puts.append(words[2] if len(words) > 2 else None)
            player.begin_tick(st)
            outs, _ = player.run_tick(st, [words], 1, rng)
            if ti in ep.expected:
                counts["asks"] += 1
                o = outs[0][0] if outs and outs[0] else None
                if o is None:
                    counts["none"] += 1
                elif o == ep.expected[ti]:
                    counts["correct"] += 1
                elif puts and o == puts[-1]:
                    counts["last_value"] += 1
                elif puts and o == puts[0]:
                    counts["first_value"] += 1
                elif o in puts:
                    counts["other_put"] += 1
    n = max(1, counts["asks"])
    return {k: round(v / n, 4) for k, v in counts.items() if k != "asks"} | {"asks": counts["asks"]}


def run_org(job: dict) -> dict:
    eps = battery()
    t0 = time.time()
    sig = strategy_signature(job["manifest"], eps)
    nb = neighbourhood(job["manifest"], eps, job["children"], job["seed"])
    bs = basin(job["manifest"], eps, job["basin_samples"], job["seed"])
    p = nb["parent"]
    profile = ("1" if p["a0"] >= STREAM_SOLVED else "0") + ("1" if p["a1"] >= STREAM_SOLVED else "0")
    f = nb["fractions"]
    flags = {"E1_summit_adjacent_rare": (f.get("summit", 0) > 0 or bs["basin_share"] > 0) and f.get("summit", 0) < 0.01,
             "E2_valley": f["valley"], "E3_stream2_destroys_stream1": (f.get("second_up", 0) > 0 and f.get("tradeoff", 0) / max(f.get("second_up", 0), 1e-9) >= 0.8),
             "E5_no_gradient": f.get("second_up", 0) < 0.005 and bs["basin_share"] == 0.0}
    return {"arm": job["arm"], "seed": job["seed"], "source_seed": job.get("source_seed"), "source_arm": job.get("source_arm"), "profile": profile, "parent_r": round(p["r"], 4),
            "sig_correct": sig["correct"], "sig_last_value": sig["last_value"], "sig_first_value": sig["first_value"], "sig_other_put": sig["other_put"], "sig_none": sig["none"],
            "strategy": ("first_value" if sig["first_value"] >= 0.3 and sig["first_value"] + sig["correct"] >= 0.9 else
                         "last_value" if sig["last_value"] >= 0.3 and sig["last_value"] + sig["correct"] >= 0.9 else
                         "keyed" if sig["correct"] >= 0.9 else "mixed"),
            "parent_a0": round(p["a0"], 4), "parent_a1": round(p["a1"], 4), **{"f_" + k: v for k, v in f.items()}, "basin_share": bs["basin_share"], "basin_best_end": bs["best_end"],
            "best_child_r": round(nb["best_child"]["r"], 4), "best_child_op": nb["best_child"]["op"], "ops_by_class": nb["ops_by_class"], **flags,
            "instr": len(job["manifest"]["genome"]) // 4, "persist": job["manifest"]["persist"], "wall_s": round(time.time() - t0, 1)}


class ShelfAnatomy(Experiment3):
    ID = "C3-SFE-02"
    TITLE = "anatomy of the half-credit shelf"
    PARENTS = ["C3-SFE-01"]
    METRICS = ("parent_r", "f_useful", "f_second_up", "f_second_up_keep", "f_tradeoff", "f_deceptive", "f_summit", "basin_share")


def load_c3_sfe01() -> tuple:
    d = REPO / "archaeon" / "campaign3" / "C3-SFE-01"
    rows = json.loads((d / "rows.json").read_text(encoding="utf-8")) if (d / "rows.json").exists() else []
    shelf = [(r["arm"], r["seed"], r["final_elite_manifest"], r["competence_heldout"]) for r in rows if r.get("level") == "SHELF" and r.get("final_elite_manifest")]
    summit = [(r["arm"], r["seed"], r["summit_elite_manifest"], r["competence_heldout"]) for r in rows if r.get("summit") and r.get("summit_elite_manifest")]
    return shelf, summit, rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--children", type=int, default=400)
    ap.add_argument("--basin-samples", type=int, default=40)
    ap.add_argument("--max-orgs", type=int, default=12)
    ap.add_argument("--recomb", type=int, default=200)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = ShelfAnatomy(dry_run=a.dry_run, procs=a.procs)
    shelf, summit, rows01 = load_c3_sfe01()
    if a.dry_run and not shelf:
        shelf = [("dry", i, o["manifest"], 0.5) for i, o in enumerate(G.generate(dict(FOUNDRY_C2, seed=31, n=3)))]
    reach = X.reachability_for([(TARGET, 200, 300, 16, "E0")])
    X.seal({
        "question": "What makes the W2_K2 half-credit shelf hard to leave: is the summit one or two ordinary mutations away but rarely sampled, does it require crossing a "
                    "fitness valley, does solving stream 2 destroy stream 1, do complementary lineages exist that recombination cannot join, or is there no gradient?",
        "parent_evidence": "C3-SFE-01 (this campaign): %d shelf elites and %d confirmed summit elites at G300; campaign-2 L2-025/L2-039." % (len(shelf), len(summit)),
        "why_this_slot": "C3-SFE-01 gives the timescale; only the neighbourhood says why. Five explanations with preregistered rules, one cheap enumeration.",
        "assay_capability_requirement": ">= 3 shelf organisms with a solved stream (per-ask >= %.2f on the battery) and >= 3 random controls; the battery must reproduce "
                                        "the shelf (parent_r in [0.45, 0.90) for shelf organisms) else INSTRUMENT_FAILURE" % STREAM_SOLVED,
        "positive_control": "random generation-0 organisms as the neighbourhood control (their fractions are the null for every class)",
        "reachability_estimate": reach,
        "arms": ["shelf_org", "summit_org", "random_org"],
        "crn_policy": "one fixed 16-episode battery for every organism and child; child seeds keyed on the organism index",
        "budget": {"children": a.children, "basin_samples": a.basin_samples, "basin_steps": 3, "basin_breadth": 30, "recomb_tries": a.recomb, "max_orgs": a.max_orgs, "battery_episodes": 16},
        "primary_observable": "per organism: class fractions (useful, neutral, destructive, second_up, second_up_keep, first_down, tradeoff, deceptive, summit), basin share, valley; "
                              "primary comparison shelf_org vs random_org on f_second_up_keep (a second-stream gradient that keeps the first stream)",
        "claim_ceiling": "a topology map of <= %d shelf organisms; explanations are flagged by rule, not asserted" % a.max_orgs,
        "falsification_condition": "f_second_up_keep(shelf) - f_second_up_keep(random) < 0.01 => no usable second-stream gradient from the shelf (E5 or E2/E3 by their flags)",
        "kill_condition": "if the battery cannot reproduce the shelf for the shelf organisms the enumeration is meaningless (INSTRUMENT_FAILURE)",
        "typed_failure_conditions": ["INSTRUMENT_FAILURE (battery/shelf mismatch)", "UNDERPOWERED (< 3 shelf organisms)"],
        "expected_machine_telemetry": ["class fractions and operator histograms per class", "basin probe end rewards", "recombination joins", "edit distances shelf<->summit"],
        "replacement_condition": "if C3-SFE-01 had produced no shelf organisms at all (impossible per the table) this slot would be replaced by a finer C3-SFE-01 scan",
        "ancestry": "original (queue slot 2)",
        "machine_changes_exercised": ["per_ask credit", "I"],
        "decl": {"n_min": 3, "primary": {"treatment": "shelf_org", "control": "random_org", "metric": "f_second_up_keep", "min_effect": 0.01}},
    })
    X.decision("D3-010: explanation flags E1-E5 are rules on class fractions (E1 summit adjacent but < 1%%; E2 second-stream gains only below the parent; E3 tradeoff >= 80%% of second-stream gains; E4 complementary profiles with 0 joins; E5 second_up < 0.5%% and basin 0)")
    X.open("cmp3-sfe02")
    wid = X.world("anatomy", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    randoms = [o["manifest"] for o in G.generate(dict(FOUNDRY_C2, seed=CAMPAIGN_SEED + 2, n=min(6, a.max_orgs)))]
    jobs = [{"arm": "shelf_org", "seed": i, "source_arm": arm, "source_seed": s, "manifest": m, "children": a.children, "basin_samples": a.basin_samples}
            for i, (arm, s, m, _) in enumerate(shelf[:a.max_orgs])]
    jobs += [{"arm": "summit_org", "seed": 100 + i, "source_arm": arm, "source_seed": s, "manifest": m, "children": a.children, "basin_samples": a.basin_samples}
             for i, (arm, s, m, _) in enumerate(summit[:6])]
    jobs += [{"arm": "random_org", "seed": 200 + i, "manifest": m, "children": a.children, "basin_samples": a.basin_samples} for i, m in enumerate(randoms)]
    rows = X.pool_map(run_org, jobs, "anatomy_s")
    eps = battery()
    # complementary lineages + recombination
    prof = {}
    for r, j in zip(rows, jobs):
        if r["arm"] == "shelf_org":
            prof.setdefault(r["profile"], []).append(j["manifest"])
    recomb = None
    if prof.get("10") and prof.get("01"):
        recomb = recombine(prof["10"][0], prof["01"][0], eps, a.recomb, 1)
    X.receipt["complementary"] = {"profiles": {k: len(v) for k, v in prof.items()}, "recombination": recomb,
                                  "E4_complementary_unjoinable": bool(prof.get("10") and prof.get("01") and recomb and recomb["joined"] == 0)}
    dists = []
    for arm, s, m, _ in summit[:6]:
        for arm2, s2, m2, _ in shelf[:a.max_orgs]:
            dists.append({"summit": (arm, s), "shelf": (arm2, s2), "opcode_edit_distance": edit_distance(m["genome"], m2["genome"])})
    X.receipt["shelf_summit_distances"] = dists[:60]
    X.receipt["shelf_reproduced"] = {"n_shelf": sum(1 for r in rows if r["arm"] == "shelf_org"), "in_band": sum(1 for r in rows if r["arm"] == "shelf_org" and R.SHELF_MIN <= r["parent_r"] < R.SUMMIT_MIN)}
    harness_errors = [] if X.receipt["shelf_reproduced"]["in_band"] >= min(3, X.receipt["shelf_reproduced"]["n_shelf"]) else [{"step": "battery", "error": "shelf organisms not in band on the battery"}]
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "source": {"arm": r.get("source_arm"), "seed": r.get("source_seed")}, "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k != "ops_by_class"}, "SURVIVED" if r.get("f_summit", 0) > 0 or r["basin_share"] > 0 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    summ = {}
    for arm in ("shelf_org", "summit_org", "random_org"):
        rs = [r for r in rows if r["arm"] == arm]
        if rs:
            summ[arm] = {k: round(sum(r.get(k, 0) or 0 for r in rs) / len(rs), 4) for k in ("parent_r", "f_useful", "f_neutral", "f_destructive", "f_second_up", "f_second_up_keep",
                                                                                              "f_first_down", "f_tradeoff", "f_deceptive", "f_summit", "basin_share")}
            summ[arm]["n"] = len(rs); summ[arm]["profiles"] = [r["profile"] for r in rs]
            summ[arm]["flags"] = {f: sum(1 for r in rs if r.get(f)) for f in ("E1_summit_adjacent_rare", "E2_valley", "E3_stream2_destroys_stream1", "E5_no_gradient")}
    X.receipt["summary"] = summ
    out = X.close(rows, meas_extra={"harness_errors": harness_errors})
    print(json.dumps({"summary": summ, "complementary": X.receipt["complementary"], "shelf_reproduced": X.receipt["shelf_reproduced"], **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
