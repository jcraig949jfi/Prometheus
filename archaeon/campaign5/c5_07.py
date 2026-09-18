"""C5-07 -- COST OF INSULATION (campaign 5, Phase B; conditional on C5-06 REAL_LOCAL_RECOVERY).
Preregistration: C5-07/DESIGN.md.

    python -m archaeon.campaign5.c5_07 [--c506 a01] [--c505 a01] [--procs 12] [--dry-run] [--self-test]

K1 compute (ops ratio child FIZZLE / parent OLD), K2 fragility (second-edit neutral share of the
recovered child vs its parent, both under FIZZLE), K3 lost function elsewhere.
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
from typing import List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign5.repb import grammar_b                                # noqa: E402
from archaeon.campaign5.c5_05 import eval_all_b, _interp_row, _digest        # noqa: E402
from archaeon.campaign5.c5_06 import load_rows, load_children_index          # noqa: E402

ID = "C5-07"


def second_edit_neutral(job: dict) -> dict:
    """Neutral share (D5 + DF/D5) of grammar-B single edits of `manifest` under FIZZLE on `env`; C5 seeds keyed by `key`."""
    m, env, key, draws = job["manifest"], job["env"], job["key"], job["draws"]
    eps = {k: C1.episodes(k, C1.E) for k in C1.ENVS}          # all five: the classifier reads the other environments for D6
    pev = eval_all_b(m, eps, "FIZZLE")
    k = n = 0; labels = Counter()
    for op in C1.OPERATORS:
        for r in range(1, draws + 1):
            rng = SplitMix64(seed_from("c5.05.edit", CAMPAIGN_SEED, key, "B", op, r))
            child, rec = grammar_b.mutate_b(m, rng, mate=None, name=op)
            if "noop" in rec["args"]:
                continue
            row = _interp_row(child, eval_all_b(child, eps, "FIZZLE"), pev, env, "B_FIZZLE")
            lab = row["D"] if row["D"] != "DF" else "DF/" + str(row["sub"])
            labels[lab] += 1; n += 1
            k += (row["D"] == "D5") or (row["D"] == "DF" and row["sub"] == "D5")
    return {"key": key, "n": n, "neutral": k, "share": round(k / max(1, n), 4), "labels": dict(labels)}


def costs(job: dict) -> dict:
    """K1 and K3 for one recovered child against its parent."""
    child, parent, env = job["child"], job["parent"], job["env"]
    eps = {k: C1.episodes(k, C1.E) for k in C1.ENVS}
    cz = eval_all_b(child, eps, "FIZZLE"); po = C1.eval_all(parent, eps)
    k1 = cz[env]["ops_per_episode"] / max(1e-9, po[env]["ops_per_episode"])
    lost = [o for o in C1.OTHER_ENVS if po[o]["reward_per_ask"] >= C1.FLOOR and cz[o]["reward_per_ask"] <= po[o]["reward_per_ask"] - C1.BAND]
    return {"digest": job["digest"], "k1_ratio": round(k1, 4), "k3_lost_on": lost, "child_evals": {k: v["reward_per_ask"] for k, v in cz.items()},
            "parent_evals": {k: v["reward_per_ask"] for k, v in po.items()}}


def analyse(k1k3: List[dict], child_neutral: List[dict], parent_neutral: dict) -> dict:
    ratios = sorted(x["k1_ratio"] for x in k1k3)
    med = ratios[len(ratios) // 2] if ratios else None
    gt = sum(1 for r in ratios if r > 1.10) / max(1, len(ratios))
    K1 = {"n": len(ratios), "median_ratio": med, "share_gt_1_10": round(gt, 4), "share_lt_0_90": round(sum(1 for r in ratios if r < 0.90) / max(1, len(ratios)), 4)}
    # K2 pooled: children's second-edit neutral share vs their parents'
    cn = sum(x["neutral"] for x in child_neutral); cN = sum(x["n"] for x in child_neutral)
    pn = sum(parent_neutral[x["parent_key"]]["neutral"] for x in child_neutral); pN = sum(parent_neutral[x["parent_key"]]["n"] for x in child_neutral)
    diff = cn / max(1, cN) - pn / max(1, pN)
    K2 = {"children_neutral": round(cn / max(1, cN), 4), "children_n": cN, "parents_neutral_weighted": round(pn / max(1, pN), 4), "parents_n": pN,
          "diff": round(diff, 4), "wilson_children": C1.wilson(cn, max(1, cN)), "cost": diff < -C1.BAND,
          "per_child_below_parent_by_band": sum(1 for x in child_neutral if x["share"] < parent_neutral[x["parent_key"]]["share"] - C1.BAND),
          "per_child_above_parent_by_band": sum(1 for x in child_neutral if x["share"] > parent_neutral[x["parent_key"]]["share"] + C1.BAND)}
    K3 = {"n": len(k1k3), "lost_elsewhere": sum(1 for x in k1k3 if x["k3_lost_on"]), "share": round(sum(1 for x in k1k3 if x["k3_lost_on"]) / max(1, len(k1k3)), 4),
          "by_env": dict(Counter(o for x in k1k3 for o in x["k3_lost_on"]))}
    reading = "INSULATION_COSTLY" if (K2["cost"] or K1["share_gt_1_10"] >= 0.5) else "INSULATION_CHEAP"
    return {"K1": K1, "K2": K2, "K3": K3, "reading": reading}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--c506", default=None)
    ap.add_argument("--c505", default=None)
    ap.add_argument("--draws", type=int, default=C1.DRAWS)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-07")
    c506 = a.c506 or sorted(d.name for d in (C5 / "C5-06" / "attempts").iterdir() if (d / "RECOVERY.json").exists())[-1]
    c505 = a.c505 or sorted(d.name for d in (C5 / "C5-05" / "attempts").iterdir() if (d / "GEOMETRY_B.json").exists())[-1]
    rec = json.loads((C5 / "C5-06" / "attempts" / c506 / "RECOVERY.json").read_text(encoding="utf-8"))
    if rec["disposition"] != "REAL_LOCAL_RECOVERY":
        print("C5-06 did not read REAL_LOCAL_RECOVERY; C5-07 is skipped by the directive"); return 0
    rows = load_rows(c505); regen = load_children_index(c505)
    by_digest = {r["child_digest"]: r for r in rows if r.get("child_digest")}
    events = [e for e in rec["events"] if e["class"] == "RECOVERY" and e["agree"] >= 2]
    if a.self_test:
        events = events[:3]
    jobs_c = []; jobs_n = []; parent_keys = {}
    for e in events:
        r = by_digest[e["digest"]]; child, parent = regen(r)
        jobs_c.append({"child": child, "parent": parent, "env": r["parent_env"], "digest": e["digest"]})
        jobs_n.append({"manifest": child, "env": r["parent_env"], "key": e["digest"], "draws": a.draws, "parent_key": r["parent_id"]})
        parent_keys[r["parent_id"]] = (parent, r["parent_env"])
    jobs_p = [{"manifest": pm, "env": env, "key": pid, "draws": a.draws} for pid, (pm, env) in parent_keys.items()]
    if a.self_test:
        k1k3 = [costs(j) for j in jobs_c]; cn = [second_edit_neutral(j) | {"parent_key": j["parent_key"]} for j in jobs_n]; pn = {x["key"]: x for x in (second_edit_neutral(j) for j in jobs_p)}
        # control: the parent's second-edit share equals C5-05's grammar-B FIZZLE neutral share for that parent
        ctrl = {}
        for pid, x in pn.items():
            prow = [r for r in rows if r["parent_id"] == pid and r["grammar"] == "B" and r["operator"] in C1.OPERATORS and r["applied"]]
            k = sum(1 for r in prow if r["by"]["B_FIZZLE"]["D"] == "D5" or (r["by"]["B_FIZZLE"]["D"] == "DF" and r["by"]["B_FIZZLE"]["sub"] == "D5"))
            ctrl[pid[:8]] = {"c5_05": (k, len(prow)), "here": (x["neutral"], x["n"]), "equal": (k, len(prow)) == (x["neutral"], x["n"])}
        print(json.dumps({"events": len(events), "analysis": analyse(k1k3, cn, pn), "parent_control": ctrl}, indent=1))
        return 0 if all(v["equal"] for v in ctrl.values()) else 1
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415

    class Cost(harness()):
        ID = "C5-07"
        TITLE = "cost of insulation (K1 compute, K2 second-edit fragility, K3 lost function elsewhere)"
        PARENTS = ["C5-06", "C5-05"]
        ARM_FIELD = "arm"
        METRICS = ("share",)

    X = Cost(dry_run=a.dry_run, procs=a.procs)
    design = (C5 / "C5-07" / "DESIGN.md").read_text(encoding="utf-8")
    X.seal({
        "question": "What does skipping an executed fault cost the recovered program: compute, second-edit fragility, function elsewhere?",
        "parent_evidence": "C5-06 %s: %d replicated recoveries of %d executed-crossing children" % (c506, len(events), rec["input_n"]),
        "why_this_slot": "The directive's conditional cost-of-insulation slot; C5-06 read REAL_LOCAL_RECOVERY.",
        "assay_capability_requirement": "the parent's second-edit neutral share here equals C5-05's grammar-B FIZZLE neutral share for the same parent (same seeds); determinism",
        "positive_control": "controls arm: pass >= 1.0",
        "reachability_estimate": {"note": "not a reach experiment"},
        "arms": ["controls", "children", "parents"],
        "crn_policy": "second edits seeded seed_from('c5.05.edit', 20260922, key, 'B', op, draw) with key = child digest / parent id",
        "budget": {"recovered_children": len(events), "parents": len(parent_keys), "draws": a.draws, "c5_06_attempt": c506, "c5_05_attempt": c505},
        "primary_observable": "K1 median ratio and > 1.10 share; K2 pooled diff and per-child counts; K3 share; reading INSULATION_COSTLY / INSULATION_CHEAP",
        "claim_ceiling": "costs of single-edit recovery on 57 parents' lineages; no evolution",
        "falsification_condition": "K2 cost or K1 > 1.10 share >= .50 -> INSULATION_COSTLY",
        "kill_condition": "parent control mismatch -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID"],
        "expected_machine_telemetry": ["per-child K1/K3", "per-child second-edit label counts"],
        "machine_changes_exercised": ["second_edit_neutral", "costs"],
        "replacement_condition": "none",
        "ancestry": "original (Phase B, slot 5)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 10, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "children", "control": "parents", "metric": "share", "min_effect": -0.0625}},
    })
    X.open("cmp5-c5-07")
    wid = X.world("cost-of-insulation", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    k1k3 = X.pool_map(costs, jobs_c, "k1k3_s")
    cn_raw = X.pool_map(second_edit_neutral, jobs_n, "children_edits_s")
    cn = [x | {"parent_key": j["parent_key"]} for x, j in zip(cn_raw, jobs_n)]
    pn = {x["key"]: x for x in X.pool_map(second_edit_neutral, jobs_p, "parent_edits_s")}
    ctrl_ok = True; ctrl = {}
    for pid, x in pn.items():
        prow = [r for r in rows if r["parent_id"] == pid and r["grammar"] == "B" and r["operator"] in C1.OPERATORS and r["applied"]]
        k = sum(1 for r in prow if r["by"]["B_FIZZLE"]["D"] == "D5" or (r["by"]["B_FIZZLE"]["D"] == "DF" and r["by"]["B_FIZZLE"]["sub"] == "D5"))
        eq = (k, len(prow)) == (x["neutral"], x["n"]); ctrl[pid[:12]] = eq; ctrl_ok = ctrl_ok and eq
    res = analyse(k1k3, cn, pn); res["controls"] = {"parent_equals_c5_05": ctrl_ok, "n_parents": len(pn), "pass": ctrl_ok}; res["wall_s"] = round(time.time() - t0, 1)
    grouped = [{"arm": "controls", "pass": float(ctrl_ok), "n": 1}]
    for x in cn:
        grouped.append({"arm": "children", "key": x["key"][:12], "share": x["share"], "n": x["n"]})
    for pid, x in pn.items():
        grouped.append({"arm": "parents", "key": pid[:12], "share": x["share"], "n": x["n"]})
    X.record(wid, {"arm": "summary"}, {"arm": "summary"}, res, "SURVIVED", key_parts=("summary",))
    X.att.write("COST.json", res | {"k1k3": k1k3, "children_edits": cn, "parent_edits": pn})
    X.publish(wid, "cost", "cmp5.c507_cost.v1", res, {"info_kind": "artifact", "label": "C5-07 cost of insulation"})
    out = X.close(grouped, addendum={"reading": res["reading"], "K1": json.dumps(res["K1"]), "K2": json.dumps(res["K2"]), "K3": json.dumps(res["K3"])})
    print(json.dumps(res | {"close": out["disposition"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
