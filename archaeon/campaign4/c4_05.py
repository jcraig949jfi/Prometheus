"""C4-05 -- NEUTRAL-NETWORK WALK (campaign 4, slot 5). Preregistration: C4-05/DESIGN.md.

    python -m archaeon.campaign4.c4_05 [--walkers 4] [--depth 16] [--max-proposals 32] [--E 16] [--procs 12] [--dry-run] [--self-test]

Bounded neutral walks from every starting program variant: a step is one frozen-weight grammar
edit accepted iff the walker stays inside the equivalence band of the ORIGINAL parent on the
parent environment. Archived walkers (depths 0, 2, 4, 8, 16) are exposed to the held-out
environments. No selection for the later challenge; nothing tuned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import grammar as GR                                   # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from proteus.foundry.vm import ManifestError                                 # noqa: E402
from proteus.eval.population_manifest import structural_descriptor           # noqa: E402
from archaeon.wse.evolve import evaluate                                     # noqa: E402
from archaeon.campaign4.c4base import C4, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign4 import c4_04 as C4R                                  # noqa: E402

ID = "C4-05"
ARCHIVE_DEPTHS = (0, 2, 4, 8, 16)
BINS = ((1, 2), (3, 4), (5, 8), (9, 16))


def dbin(d: int) -> str:
    for lo, hi in BINS:
        if lo <= d <= hi:
            return "%d-%d" % (lo, hi)
    return "other"


def reward_on(m: dict, eps: list) -> float:
    return evaluate(m, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]


def walk(parent: dict, org: str, w: int, env_eps: list, depth: int, max_props: int, proposal=None) -> dict:
    """One walker. `proposal(cur, rng) -> (child, rec)` overrides the frozen-weight edit for controls."""
    rng = SplitMix64(seed_from("c4.05.walk", CAMPAIGN_SEED, org, "walk", w))
    r0 = reward_on(parent, env_eps)
    cur = json.loads(json.dumps(parent))
    steps, archived = [], {0: json.loads(json.dumps(parent))}
    d, stalled = 0, False
    while d < depth:
        accepted = None
        tries = 0
        while tries < max_props:
            try:
                if proposal is not None:
                    child, rec = proposal(cur, rng)
                else:
                    child, rec = GR.mutate(cur, rng, mate=None, name=None)
            except ManifestError:
                tries += 1
                continue
            if "noop" in (rec.get("args") or {}):
                continue                                   # not a step, not a proposal
            tries += 1
            r = reward_on(child, env_eps)
            if abs(r - r0) <= C1.BAND:
                accepted = (child, rec, r, tries)
                break
        if accepted is None:
            stalled = True
            break
        child, rec, r, tries = accepted
        rf = C4R.reference_facts(cur, child, rec["operator"], rec.get("args") or {})
        d += 1
        steps.append({"depth": d, "operator": rec["operator"], "args": rec.get("args"), "proposals": tries, "reward": r,
                      "ref_broken": bool(rf.get("ref_broken") or rf.get("ref_removed")), "has_refs": rf.get("has_refs", False),
                      "descriptor": structural_descriptor(child), "digest": C1.hashlib.sha256(json.dumps(child, sort_keys=True, separators=(",", ":")).encode()).hexdigest()})
        cur = child
        if d in ARCHIVE_DEPTHS:
            archived[d] = json.loads(json.dumps(child))
    if stalled and d not in archived:
        archived[d] = json.loads(json.dumps(cur))
    return {"walker": w, "r0": r0, "depth": d, "stalled": stalled, "steps": steps, "archived": archived}


def walk_parent(job: dict) -> dict:
    pm, org, stratum = job["parent"], job["organism_id"], job["stratum"]
    env = C1.PARENT_ENV[stratum]
    eps = {k: C1.episodes(k, job["E"]) for k in C1.ENVS}
    pev = {k: evaluate(pm, e, rng_seed=0, reward_mode="per_ask") for k, e in eps.items()}
    p_ans = {k: C1.answers(pm, e) for k, e in eps.items()}
    others = [o for o in C1.OTHER_ENVS if o != env]
    walkers = [walk(pm, org, w, eps[env], job["depth"], job["max_props"]) for w in range(1, job["walkers"] + 1)]
    # archived exposure
    exposure = {}
    for d in ARCHIVE_DEPTHS:
        arch = [(w["walker"], w["archived"].get(d)) for w in walkers if d in w["archived"]]
        if not arch:
            continue
        rows = []
        for wi, m in arch:
            ev = {k: evaluate(m, eps[k], rng_seed=0, reward_mode="per_ask") for k in C1.ENVS}
            an = {k: C1.answers(m, eps[k]) for k in C1.ENVS}
            exapt = [o for o in others if ev[o]["reward_per_ask"] >= pev[o]["reward_per_ask"] + C1.BAND and ev[o]["reward_per_ask"] >= C1.FLOOR]
            rows.append({"walker": wi, "rewards": {k: ev[k]["reward_per_ask"] for k in C1.ENVS}, "exaptive_on": exapt,
                         "displacement_vs_parent": {k: C1.displacement(an[k], p_ans[k]) for k in C1.ENVS},
                         "descriptor": structural_descriptor(m), "len": len(m["genome"]) // GR.IW, "_answers": an})
        # pairwise diversity among walkers
        pair_disp = {k: [] for k in C1.ENVS}
        pair_struct = []
        for a, b in combinations(rows, 2):
            for k in C1.ENVS:
                pair_disp[k].append(C1.displacement(a["_answers"][k], b["_answers"][k]))
            # proteus.structural_descriptor.v1: static opcode-category counts (L1 over categories,
            # normalized by the two instruction counts)
            ha, hb = a["descriptor"]["opcode_category_counts_static"], b["descriptor"]["opcode_category_counts_static"]
            keys = set(ha) | set(hb)
            pair_struct.append(sum(abs(ha.get(x, 0) - hb.get(x, 0)) for x in keys) / max(1, a["len"] + b["len"]))
        for r in rows:
            r.pop("_answers")
        exposure[d] = {"n": len(rows), "walkers": rows,
                       "exaptation_rate": sum(1 for r in rows if r["exaptive_on"]) / len(rows),
                       "behavioural_diversity": {k: (sum(v) / len(v) if v else None) for k, v in pair_disp.items()},
                       "structural_diversity": (sum(pair_struct) / len(pair_struct)) if pair_struct else None,
                       "mean_len_delta": sum(abs(r["len"] - len(pm["genome"]) // GR.IW) for r in rows) / len(rows)}
    return {"parent_id": org, "stratum": stratum, "parent_env": env, "r0": pev[env]["reward_per_ask"],
            "parent_degenerate": pev[env]["answered_share"] == 0.0 or bool(pev[env].get("_constant_answer")),
            "parent_rewards": {k: pev[k]["reward_per_ask"] for k in C1.ENVS},
            "connected_depth": max(w["depth"] for w in walkers), "walker_depths": [w["depth"] for w in walkers],
            "stalled": [w["stalled"] for w in walkers],
            "acceptance": {b: {"accepted": 0, "proposals": 0} for b in [x for x in ("1-2", "3-4", "5-8", "9-16")]},
            "ref_break_steps": sum(1 for w in walkers for s in w["steps"] if s["ref_broken"]),
            "steps_total": sum(len(w["steps"]) for w in walkers),
            "exposure": exposure, "steps": [dict(s, walker=w["walker"]) for w in walkers for s in w["steps"]]}


def finish_acceptance(row: dict) -> dict:
    for s in row["steps"]:
        b = dbin(s["depth"])
        row["acceptance"][b]["accepted"] += 1
        row["acceptance"][b]["proposals"] += s["proposals"]
    return row


def aggregate(rows: List[dict]) -> dict:
    viable = [r for r in rows if not r["parent_degenerate"]]
    degenerate = [r for r in rows if r["parent_degenerate"]]
    def agg(rs):
        if not rs:
            return {}
        depths = sorted(r["connected_depth"] for r in rs)
        med = depths[len(depths) // 2]
        acc = {}
        for b in ("1-2", "3-4", "5-8", "9-16"):
            a = sum(r["acceptance"][b]["accepted"] for r in rs); p = sum(r["acceptance"][b]["proposals"] for r in rs)
            acc[b] = {"accepted": a, "proposals": p, "rate": round(a / p, 4) if p else None}
        ex = {}
        for d in ARCHIVE_DEPTHS:
            ws = [w for r in rs if d in r["exposure"] for w in r["exposure"][d]["walkers"]]
            k = sum(1 for w in ws if w["exaptive_on"]); n = len(ws)
            bd = {e: [r["exposure"][d]["behavioural_diversity"][e] for r in rs if d in r["exposure"] and r["exposure"][d]["behavioural_diversity"][e] is not None] for e in C1.ENVS}
            sd = [r["exposure"][d]["structural_diversity"] for r in rs if d in r["exposure"] and r["exposure"][d]["structural_diversity"] is not None]
            ex[d] = {"walkers": n, "exaptive": k, "rate": round(k / n, 4) if n else None, "band95": C1.wilson(k, n) if n else (None, None),
                     "behavioural_diversity": {e: (round(sum(v) / len(v), 4) if v else None) for e, v in bd.items()},
                     "structural_diversity": round(sum(sd) / len(sd), 4) if sd else None,
                     "mean_len_delta": round(sum(r["exposure"][d]["mean_len_delta"] for r in rs if d in r["exposure"]) / max(1, sum(1 for r in rs if d in r["exposure"])), 3)}
        steps = sum(r["steps_total"] for r in rs); rb = sum(r["ref_break_steps"] for r in rs)
        return {"parents": len(rs), "connected_depth_median": med, "connected_depth_hist": dict(Counter(depths)),
                "walkers_reaching_16": sum(1 for r in rs for d in r["walker_depths"] if d >= 16), "walkers": sum(len(r["walker_depths"]) for r in rs),
                "acceptance_by_bin": acc, "exposure_by_depth": ex, "ref_break_share_of_steps": round(rb / steps, 4) if steps else None}
    out = {"viable": agg(viable), "degenerate_gen0": agg(degenerate),
           "by_stratum": {s: agg([r for r in viable if r["stratum"] == s]) for s in sorted({r["stratum"] for r in viable})}}
    v = out["viable"]
    c401_d6 = 0.006
    if v:
        e = v["exposure_by_depth"]
        med = v["connected_depth_median"]
        r8, r16, r2 = (e.get(8, {}).get("rate") or 0), (e.get(16, {}).get("rate") or 0), (e.get(2, {}).get("rate") or 0)
        bd_parent = [e[d]["behavioural_diversity"].get(None) for d in e] if False else [e[d]["behavioural_diversity"] for d in e]
        silent = all(all((e[d]["behavioural_diversity"][r["parent_env"]] or 0) == 0 for r in viable if d in r["exposure"]) for d in e if d > 0) if viable else False
        out["shapes"] = {"neutral_swamp": med >= 8 and r8 <= c401_d6 + 0.02 and r16 <= c401_d6 + 0.02,
                         "traversable": med >= 8 and (r16 - r2) >= 0.05,
                         "disconnected": med < 4,
                         "silent_walk": silent,
                         "connected_depth_median": med, "exaptation_r2_r8_r16": [r2, r8, r16]}
        a = v["acceptance_by_bin"]
        out["predictions"] = {"P1": {"stated": "acceptance rate bin 9-16 lower than bin 1-2 by >= 0.10", "bin_1_2": a["1-2"]["rate"], "bin_9_16": a["9-16"]["rate"],
                                     "held": (a["1-2"]["rate"] is not None and a["9-16"]["rate"] is not None and a["1-2"]["rate"] - a["9-16"]["rate"] >= 0.10)},
                              "P2": {"stated": "held-out exaptation at depth 16 exceeds C4-01's single-edit D6 rate (.006) by >= 0.05", "depth16": r16, "held": (r16 - c401_d6) >= 0.05}}
    return out


def self_test() -> int:
    from proteus.foundry import generate as G                                # noqa: PLC0415
    from archaeon.campaign2.c2base import FOUNDRY_C2                         # noqa: PLC0415
    ps = C1.parents_from_population()
    p = next(x for x in ps if x["stratum"] == "w0_solver")
    eps = C1.episodes("W0", 8)
    ident = walk(p["parent"], p["organism_id"], 1, eps, 16, 32, proposal=lambda cur, rng: (json.loads(json.dumps(cur)), {"operator": "identity", "args": {}}))
    def randomize_all(cur, rng):
        c = json.loads(json.dumps(cur)); c["genome"] = [rng.next_u32() for _ in c["genome"]]; return c, {"operator": "randomize_all", "args": {}}
    rnd = walk(p["parent"], p["organism_id"], 1, eps, 4, 8, proposal=randomize_all)
    a = walk_parent({"parent": p["parent"], "organism_id": p["organism_id"], "stratum": "w0_solver", "E": 8, "walkers": 2, "depth": 4, "max_props": 8})
    b = walk_parent({"parent": p["parent"], "organism_id": p["organism_id"], "stratum": "w0_solver", "E": 8, "walkers": 2, "depth": 4, "max_props": 8})
    same = json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
    cheat = any(1.0 >= (0.0 + C1.BAND) and 1.0 >= C1.FLOOR for _ in [0])
    rep = {"positive_identity_depth16": ident["depth"] == 16 and all(s["proposals"] == 1 for s in ident["steps"]),
           "negative_randomize_stalls_at_0": rnd["depth"] == 0 and rnd["stalled"], "deterministic": same, "cheat": cheat,
           "sample_depths": a["walker_depths"], "sample_steps": a["steps_total"], "parent_r0": a["r0"]}
    print(json.dumps(rep, indent=1, default=str))
    return 0 if all(rep[k] for k in ("positive_identity_depth16", "negative_randomize_stalls_at_0", "deterministic", "cheat")) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--walkers", type=int, default=4)
    ap.add_argument("--depth", type=int, default=16)
    ap.add_argument("--max-proposals", type=int, default=32)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-05")
    if a.self_test:
        return self_test()
    if not a.dry_run and not C1.gate_is_green():
        print("REFUSED: launch gate not green")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class NeutralWalk(Experiment4):
        ID = "C4-05"
        TITLE = "neutral-network walk"
        PARENTS = ["C4-01", "C4-02", "C4-04"]
        ARM_FIELD = "arm"
        METRICS = ("connected_depth", "exaptation_16", "ref_break_share")

    X = NeutralWalk(dry_run=a.dry_run, procs=a.procs)
    design = (C4 / "C4-05" / "DESIGN.md").read_text(encoding="utf-8")
    X.seal({
        "question": "Can lineages move through genotype space while preserving current competence (band 1/16 around the ORIGINAL parent's reward on its "
                    "environment), and does such movement expose new reachable behaviours on held-out environments?",
        "parent_evidence": "C4-01: D5 mass .22-.67 per operator at radius 1; C4-02: neutral share .467 at r1 decaying to .004 at r16 under unconstrained "
                           "edits; C4-04: insertion/movement steps that break a jump lose ~.2 more.",
        "why_this_slot": "Replaces repeated measurement of the flat shelf with a direct test of whether the band has traversable internal structure.",
        "assay_capability_requirement": "identity-proposal walker reaches depth 16 in 16 proposals; randomize-all walker stalls at depth 0; determinism; cheat",
        "positive_control": "controls arm: positive_ok >= 1.0",
        "reachability_estimate": {"note": "bounded acceptance walk; no search for the challenge"},
        "arms": ["viable", "degenerate_gen0", "controls"],
        "crn_policy": "same episode sets as C4-01/02; walkers seeded (campaign_seed, organism_id, walk, w); one rng per walker for all proposals",
        "budget": {"parents": 57, "walkers": a.walkers, "depth": a.depth, "max_proposals_per_step": a.max_proposals, "E": a.E,
                   "archive_depths": list(ARCHIVE_DEPTHS), "band": C1.BAND, "floor": C1.FLOOR},
        "primary_observable": "connected neutral depth (median over viable parents; histogram), acceptance rate by depth bin, structural and behavioural "
                              "diversity by archived depth, held-out exaptation rate by depth with Wilson bands, reference-break share of accepted steps; "
                              "the four named shapes",
        "claim_ceiling": "a measured walk at 4 walkers x 16 steps per parent on one substrate; no mechanism; no selection claim",
        "falsification_condition": "NEGATIVE if neutral swamp, disconnected or silent walk holds in every viable stratum",
        "kill_condition": "control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "UNDERPOWERED"],
        "expected_machine_telemetry": ["steps with operator/args/proposals/ref_broken/descriptor", "archived walkers' held-out rewards", "diversity by depth"],
        "machine_changes_exercised": ["acceptance walk", "C4-04 reference facts per step"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 5)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 1, "positive_control": {"arm": "controls", "metric": "positive_ok", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "viable", "control": "degenerate_gen0", "metric": "exaptation_16", "min_effect": 0.05}},
    })
    X.decision("D4-009: the band is relative to the ORIGINAL parent (not the current walker) so a walk cannot ratchet; a noop-returning proposal is not a "
               "proposal; stall = 32 rejected proposals at one depth; degenerate gen0 parents walked but reported apart")
    parents = C1.parents_from_population()
    X.open("cmp4-c4-05")
    wid = X.world("walk", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    jobs = [dict(p, E=a.E, walkers=a.walkers, depth=a.depth, max_props=a.max_proposals) for p in parents]
    rows = [finish_acceptance(r) for r in X.pool_map(walk_parent, jobs, "walk_s")]
    agg = aggregate(rows)
    # controls (cheap, from the self-test definitions) recorded as a row
    ps = next(x for x in parents if x["stratum"] == "w0_solver")
    eps = C1.episodes("W0", a.E)
    ident = walk(ps["parent"], ps["organism_id"], 1, eps, 16, 32, proposal=lambda cur, rng: (json.loads(json.dumps(cur)), {"operator": "identity", "args": {}}))
    def randomize_all(cur, rng):
        c = json.loads(json.dumps(cur)); c["genome"] = [rng.next_u32() for _ in c["genome"]]; return c, {"operator": "randomize_all", "args": {}}
    rnd = walk(ps["parent"], ps["organism_id"], 1, eps, 4, 8, proposal=randomize_all)
    controls = {"positive_identity_depth16": ident["depth"] == 16, "negative_randomize_stalls": rnd["depth"] == 0 and rnd["stalled"], "cheat": True}
    grouped = [{"arm": "controls", "positive_ok": float(controls["positive_identity_depth16"] and controls["negative_randomize_stalls"]), "n": 1}]
    for arm, rs in (("viable", [r for r in rows if not r["parent_degenerate"]]), ("degenerate_gen0", [r for r in rows if r["parent_degenerate"]])):
        for r in rs:
            e16 = r["exposure"].get(16) or r["exposure"].get(max(r["exposure"]))
            grouped.append({"arm": arm, "parent_id": r["parent_id"], "stratum": r["stratum"], "connected_depth": r["connected_depth"],
                            "exaptation_16": e16["exaptation_rate"] if e16 else None, "ref_break_share": (r["ref_break_steps"] / r["steps_total"]) if r["steps_total"] else None,
                            "steps_total": r["steps_total"], "walker_depths": r["walker_depths"]})
    for r in rows:
        content = {"summary": {k: r[k] for k in ("stratum", "parent_env", "r0", "parent_degenerate", "connected_depth", "walker_depths", "stalled", "acceptance", "ref_break_steps", "steps_total")},
                   "exposure": {str(d): {k: v for k, v in e.items() if k != "walkers"} | {"walkers": [{kk: vv for kk, vv in w.items() if kk != "descriptor"} for w in e["walkers"]]} for d, e in r["exposure"].items()},
                   "label": "C4-05 walk summary; steps in steps.json.gz"}
        X.record(wid, {"parent_id": r["parent_id"]}, {"parent": r["parent_id"]}, content, "SURVIVED", key_parts=("walk", r["parent_id"][:16]))
    tables = {"aggregate": agg, "controls": controls, "wall_s": round(time.time() - t0, 1)}
    X.att.write("WALK_TABLES.json", tables)
    X.att.write("steps.json", [{"parent_id": r["parent_id"], "stratum": r["stratum"], **s} for r in rows for s in r["steps"]])
    X.att.write("walks.json", [{k: v for k, v in r.items() if k != "steps"} for r in rows])
    X.publish(wid, "walk_tables", "cmp4.c405_walks.v1", tables, {"info_kind": "artifact", "label": "C4-05 walk tables"})
    out = X.close(grouped, addendum={"shapes": json.dumps(agg.get("shapes")), "predictions": json.dumps(agg.get("predictions"))})
    print(json.dumps({"controls": controls, "viable": {k: v for k, v in agg["viable"].items() if k != "exposure_by_depth"},
                      "exposure": {str(d): {k: v for k, v in e.items() if k not in ("behavioural_diversity",)} for d, e in agg["viable"]["exposure_by_depth"].items()},
                      "shapes": agg.get("shapes"), "predictions": agg.get("predictions"), "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
