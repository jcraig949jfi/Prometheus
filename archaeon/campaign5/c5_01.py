"""C5-01 -- DEEP NEUTRAL WALK (campaign 5, Phase A). Preregistration: C5-01/DESIGN.md.

    python -m archaeon.campaign5.c5_01 [--walkers 6] [--depth 64] [--E 16] [--procs 12] [--dry-run] [--self-test]

The C4-05 construction unchanged (band, no ratchet, grammar, exaptation rule, separation) at
depth 64 with archives 0/16/32/48/64 and 6 walkers; walkers 1-4 are C4-05's walks (same seeds).
Adds yield-per-evaluation accounting and the three preregistered branches.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign4 import c4_05 as W                                    # noqa: E402
from archaeon.campaign5.c5base import C5, CAMPAIGN_SEED                      # noqa: E402

ID = "C5-01"
DEPTHS = (0, 16, 32, 48, 64)
SINGLE_EDIT_YIELD_PER_EVAL = 0.006 / 5.0        # C4-01 D6 rate per edit / 5 evaluations per edit
W.ARCHIVE_DEPTHS = DEPTHS                        # the C4-05 walk archives at these depths now (read at call time)


def walk_parent(job: dict) -> dict:
    """C4-05's walk_parent with the deeper archive set; adds per-walker evaluation counts."""
    row = W.walk_parent(job)
    # evaluation accounting: proposals on the parent env (one each) + exposures (5 envs per archived walker)
    props_by_walker: Dict[int, int] = Counter()
    for s in row["steps"]:
        props_by_walker[s["walker"]] += s["proposals"]
    row["proposals_by_walker"] = dict(props_by_walker)
    # C4-05's finish_acceptance bins depths 1-16 only; C5-01 bins its own (aggregate.acceptance)
    row["acceptance"] = {}
    return row


def aggregate(rows: List[dict]) -> dict:
    """Rates per archived depth, yield per evaluation, marginal yield per step, the branches."""
    viable = [r for r in rows if not r["parent_degenerate"]]
    degenerate = [r for r in rows if r["parent_degenerate"]]
    def rates(rs):
        out = {}
        for d in DEPTHS:
            ws = [w for r in rs if d in r["exposure"] for w in r["exposure"][d]["walkers"]]
            k = sum(1 for w in ws if w["exaptive_on"]); n = len(ws)
            reach = sum(1 for r in rs for wd in r["walker_depths"] if wd >= d)
            out[d] = {"walkers": n, "exaptive": k, "rate": round(k / n, 4) if n else None, "band95": C1.wilson(k, n) if n else (None, None),
                      "walkers_reaching": reach,
                      "structural_diversity": round(sum(r["exposure"][d]["structural_diversity"] or 0 for r in rs if d in r["exposure"]) / max(1, sum(1 for r in rs if d in r["exposure"])), 4),
                      "behavioural_diversity_parent_env": round(sum((r["exposure"][d]["behavioural_diversity"][r["parent_env"]] or 0) for r in rs if d in r["exposure"]) / max(1, sum(1 for r in rs if d in r["exposure"])), 4)}
        return out
    def yields(rs):
        # cumulative evaluations to reach depth d: proposals for steps <= d (all walkers) + 5 exposures per archived walker at depths <= d
        out = {}
        cum_exapt = Counter()
        for d in DEPTHS:
            props = sum(s["proposals"] for r in rs for s in r["steps"] if s["depth"] <= d)
            expo = sum(5 * len(r["exposure"][dd]["walkers"]) for r in rs for dd in DEPTHS if dd <= d and dd in r["exposure"])
            # exaptive walkers found at or before depth d: a walker counts once at the first depth it is exaptive
            found = set()
            for r in rs:
                for dd in DEPTHS:
                    if dd <= d and dd in r["exposure"]:
                        for w in r["exposure"][dd]["walkers"]:
                            if w["exaptive_on"]:
                                found.add((r["parent_id"], w["walker"]))
            ev = props + expo
            out[d] = {"evaluations": ev, "proposals": props, "exposures": expo, "exaptive_walkers_cumulative": len(found),
                      "yield_per_evaluation": round(len(found) / ev, 6) if ev else None}
        return out
    def acceptance(rs):
        bins = {"1-16": [0, 0], "17-32": [0, 0], "33-48": [0, 0], "49-64": [0, 0]}
        for r in rs:
            for s in r["steps"]:
                b = "1-16" if s["depth"] <= 16 else "17-32" if s["depth"] <= 32 else "33-48" if s["depth"] <= 48 else "49-64"
                bins[b][0] += 1; bins[b][1] += s["proposals"]
        return {b: {"accepted": v[0], "proposals": v[1], "rate": round(v[0] / v[1], 4) if v[1] else None} for b, v in bins.items()}
    rv = rates(viable); yv = yields(viable)
    r16, r32, r64 = rv[16]["rate"] or 0.0, rv[32]["rate"] or 0.0, rv[64]["rate"] or 0.0
    lb64 = rv[64]["band95"][0] or 0.0
    continued = (r32 - r16 >= 0.02) and (r64 - r32 >= 0.02) and (lb64 > r16)
    plateau = abs(r64 - r16) < 0.02
    degradation = r64 < r16 - 0.02
    branch = "CONTINUED_GRADIENT" if continued else "PLATEAU" if plateau else "DEGRADATION" if degradation else "MIXED"
    y64 = yv[64]["yield_per_evaluation"] or 0.0
    preserve = continued and y64 >= 2 * SINGLE_EDIT_YIELD_PER_EVAL
    marginal = {"16->32": round((r32 - r16) / 16, 5), "32->48": round(((rv[48]["rate"] or 0) - r32) / 16, 5), "48->64": round((r64 - (rv[48]["rate"] or 0)) / 16, 5)}
    steps = sum(len(r["steps"]) for r in viable); rb = sum(r["ref_break_steps"] for r in viable)
    return {"viable": {"parents": len(viable), "walkers": sum(len(r["walker_depths"]) for r in viable), "rates_by_depth": rv, "yield_by_depth": yv,
                       "acceptance_by_bin": acceptance(viable), "marginal_rate_per_step": marginal, "ref_break_share_of_steps": round(rb / steps, 4) if steps else None,
                       "connected_depth_hist": dict(Counter(r["connected_depth"] for r in viable))},
            "degenerate_gen0": {"parents": len(degenerate), "rates_by_depth": rates(degenerate) if degenerate else {}, "acceptance_by_bin": acceptance(degenerate) if degenerate else {}},
            "by_stratum": {s: {"rates_by_depth": rates([r for r in viable if r["stratum"] == s])} for s in sorted({r["stratum"] for r in viable})},
            "branch": branch, "branch_numbers": {"r16": r16, "r32": r32, "r48": rv[48]["rate"], "r64": r64, "r64_band95": rv[64]["band95"]},
            "preserve_neutral_mechanism": preserve, "yield_64_per_evaluation": y64, "single_edit_yield_per_evaluation": SINGLE_EDIT_YIELD_PER_EVAL}


def replication_check(rows: List[dict]) -> dict:
    """Walkers 1-4 at depth 16 must reproduce C4-05's committed steps (same seeds, same code path)."""
    p = REPO / "archaeon" / "campaign4" / "C4-05" / "attempts" / "a01" / "steps.json.gz"
    if not p.exists():
        return {"status": "NOT_EXAMINED", "reason": "C4-05 steps absent"}
    old = {}
    for s in json.load(gzip.open(p, "rt", encoding="utf-8")):
        if s["depth"] <= 16:
            old[(s["parent_id"], s["walker"], s["depth"])] = s["digest"]
    new = {(r["parent_id"], s["walker"], s["depth"]): s["digest"] for r in rows for s in r["steps"] if s["walker"] <= 4 and s["depth"] <= 16}
    common = set(old) & set(new)
    mism = sum(1 for k in common if old[k] != new[k])
    return {"status": "OK" if (common and mism == 0 and len(common) == len(old)) else "FAILED", "compared": len(common), "mismatches": mism, "c405_steps": len(old)}


def self_test() -> int:
    ps = C1.parents_from_population()
    p = next(x for x in ps if x["stratum"] == "w0_solver")
    eps = C1.episodes("W0", 8)
    ident = W.walk(p["parent"], p["organism_id"], 1, eps, 64, 32, proposal=lambda cur, rng: (json.loads(json.dumps(cur)), {"operator": "identity", "args": {}}))
    a = walk_parent({"parent": p["parent"], "organism_id": p["organism_id"], "stratum": "w0_solver", "E": 8, "walkers": 2, "depth": 32, "max_props": 8})
    b = walk_parent({"parent": p["parent"], "organism_id": p["organism_id"], "stratum": "w0_solver", "E": 8, "walkers": 2, "depth": 32, "max_props": 8})
    same = json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
    rep = {"identity_depth64_in_64": ident["depth"] == 64 and all(s["proposals"] == 1 for s in ident["steps"]), "deterministic": same,
           "archived_depths": sorted(a["exposure"].keys()), "cheat": 1.0 >= C1.FLOOR, "walker_depths": a["walker_depths"]}
    print(json.dumps(rep, indent=1, default=str))
    return 0 if (rep["identity_depth64_in_64"] and same) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--walkers", type=int, default=6)
    ap.add_argument("--depth", type=int, default=64)
    ap.add_argument("--max-proposals", type=int, default=32)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-01")
    if a.self_test:
        return self_test()
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415

    class DeepWalk(harness()):
        ID = "C5-01"
        TITLE = "deep neutral walk (depth 64)"
        PARENTS = ["C4-05"]
        ARM_FIELD = "arm"
        METRICS = ("connected_depth", "exaptation_64", "ref_break_share")

    X = DeepWalk(dry_run=a.dry_run, procs=a.procs)
    design = (C5 / "C5-01" / "DESIGN.md").read_text(encoding="utf-8")
    X.seal({
        "question": "Does held-out exaptation continue increasing materially beyond neutral depth 16, or has the network entered a yield plateau? Marginal "
                    "discovery yield per accepted step and per evaluation, not monotonicity.",
        "parent_evidence": "C4-05: depths 2/4/8/16 = .016/.032/.037/.043 (single edit .006); 188/188 walkers reached 16; acceptance ~.55.",
        "why_this_slot": "Phase A of the substrate-decision campaign: the first of the two live C4 signals, closed cheaply.",
        "assay_capability_requirement": "walkers 1-4 reproduce C4-05's depth-16 steps digest for digest; identity walker depth 64 in 64; randomize-all stalls; determinism; cheat",
        "positive_control": "controls arm: positive_ok >= 1.0",
        "reachability_estimate": {"note": "acceptance walk; no search"},
        "arms": ["viable", "degenerate_gen0", "controls"],
        "crn_policy": "C4-05's episode sets and walker seeds (campaign_seed 20260921 for the walks, so walkers 1-4 ARE C4-05's); walkers 5-6 new draws from the same rule",
        "budget": {"parents": 57, "walkers": a.walkers, "depth": a.depth, "max_proposals": a.max_proposals, "E": a.E, "archive_depths": list(DEPTHS)},
        "primary_observable": "exaptation rate by depth with Wilson bands; yield per evaluation by depth; marginal rate per accepted step between archives; acceptance by bin; "
                              "the three branches; PRESERVE rule (continued gradient AND Y_64 >= 2 x .0012)",
        "claim_ceiling": "a rate curve at 6 walkers x 64 steps per competent parent on one substrate; no mechanism",
        "falsification_condition": "PLATEAU or DEGRADATION or MIXED -> the neutral mechanism is not preserved for Phase A's disposition",
        "kill_condition": "control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "UNDERPOWERED"],
        "expected_machine_telemetry": ["steps with proposals per walker", "archived exposures at 5 depths", "yield table"],
        "machine_changes_exercised": ["C4-05 walk reused with a deeper archive set", "yield-per-evaluation accounting"],
        "replacement_condition": "none",
        "ancestry": "original (Phase A, slot 1)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 1, "positive_control": {"arm": "controls", "metric": "positive_ok", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "viable", "control": "degenerate_gen0", "metric": "exaptation_64", "min_effect": 0.02}},
    })
    X.decision("D5-003 applied: 6 walkers, depth 64, archives 0/16/32/48/64; walkers 1-4 = C4-05's seeds; yield per evaluation counts proposals + 5 exposures per archived walker")
    parents = C1.parents_from_population()
    X.open("cmp5-c5-01")
    wid = X.world("deepwalk", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    jobs = [dict(p, E=a.E, walkers=a.walkers, depth=a.depth, max_props=a.max_proposals) for p in parents]
    rows = X.pool_map(walk_parent, jobs, "walk_s")
    agg = aggregate(rows)
    rep = replication_check(rows)
    ps = next(x for x in parents if x["stratum"] == "w0_solver")
    eps = C1.episodes("W0", a.E)
    ident = W.walk(ps["parent"], ps["organism_id"], 1, eps, 64, 32, proposal=lambda cur, rng: (json.loads(json.dumps(cur)), {"operator": "identity", "args": {}}))
    def randomize_all(cur, rng):
        c = json.loads(json.dumps(cur)); c["genome"] = [rng.next_u32() for _ in c["genome"]]; return c, {"operator": "randomize_all", "args": {}}
    rnd = W.walk(ps["parent"], ps["organism_id"], 1, eps, 4, 8, proposal=randomize_all)
    controls = {"positive_identity_depth64": ident["depth"] == 64, "negative_randomize_stalls": rnd["depth"] == 0 and rnd["stalled"], "cheat": True, "replication": rep}
    grouped = [{"arm": "controls", "positive_ok": float(controls["positive_identity_depth64"] and controls["negative_randomize_stalls"] and rep["status"] == "OK"), "n": 1}]
    for arm, rs in (("viable", [r for r in rows if not r["parent_degenerate"]]), ("degenerate_gen0", [r for r in rows if r["parent_degenerate"]])):
        for r in rs:
            e64 = r["exposure"].get(64) or r["exposure"].get(max(r["exposure"]))
            grouped.append({"arm": arm, "parent_id": r["parent_id"], "stratum": r["stratum"], "connected_depth": r["connected_depth"],
                            "exaptation_64": e64["exaptation_rate"] if e64 else None, "ref_break_share": (r["ref_break_steps"] / r["steps_total"]) if r["steps_total"] else None,
                            "steps_total": r["steps_total"], "walker_depths": r["walker_depths"]})
    for r in rows:
        content = {"summary": {k: r[k] for k in ("stratum", "parent_env", "r0", "parent_degenerate", "connected_depth", "walker_depths", "stalled", "acceptance", "ref_break_steps", "steps_total", "proposals_by_walker")},
                   "exposure": {str(d): {k: v for k, v in e.items() if k != "walkers"} | {"walkers": [{kk: vv for kk, vv in w.items() if kk != "descriptor"} for w in e["walkers"]]} for d, e in r["exposure"].items()},
                   "label": "C5-01 deep walk summary; steps in steps.json.gz"}
        X.record(wid, {"parent_id": r["parent_id"]}, {"parent": r["parent_id"]}, content, "SURVIVED", key_parts=("deepwalk", r["parent_id"][:16]))
    tables = {"aggregate": agg, "controls": controls, "wall_s": round(time.time() - t0, 1)}
    X.att.write("DEEPWALK_TABLES.json", tables)
    X.att.write("steps.json", [{"parent_id": r["parent_id"], "stratum": r["stratum"], **s} for r in rows for s in r["steps"]])
    X.att.write("walks.json", [{k: v for k, v in r.items() if k != "steps"} for r in rows])
    X.publish(wid, "deepwalk_tables", "cmp5.c501_deepwalk.v1", tables, {"info_kind": "artifact", "label": "C5-01 deep walk tables"})
    out = X.close(grouped, addendum={"branch": agg["branch"], "branch_numbers": json.dumps(agg["branch_numbers"]), "preserve_neutral_mechanism": str(agg["preserve_neutral_mechanism"]),
                                     "yield_64_per_evaluation": str(agg["yield_64_per_evaluation"])})
    v = agg["viable"]
    print(json.dumps({"controls": controls, "branch": agg["branch"], "branch_numbers": agg["branch_numbers"], "preserve": agg["preserve_neutral_mechanism"],
                      "rates": {str(d): (x["rate"], x["band95"], x["walkers_reaching"]) for d, x in v["rates_by_depth"].items()},
                      "yield": {str(d): x["yield_per_evaluation"] for d, x in v["yield_by_depth"].items()}, "acceptance": v["acceptance_by_bin"], "marginal": v["marginal_rate_per_step"],
                      "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
