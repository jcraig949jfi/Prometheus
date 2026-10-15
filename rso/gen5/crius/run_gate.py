"""C-019-T021 gate runner. python -B -m rso.gen5.crius.run_gate rso/gen5/crius/results/gate_results.json
Applies GATE_RULE.md (frozen in the commit before this file ran). One process, no search."""
import json
import sys
import time

from crius import baselines_c1 as bl, evaluate, streams
from rso.gen5.crius import adapt

SEEDS = (19020001, 19020002, 19020003, 19020004, 19020005)
WORLDS = ("W1", "W2", "W3", "W4", "W5b", "W5c")
PLAYERS = ("PROCEDURE_REUSE_C1", "QUIT_C1", "TABLE_MEMO_C1", "PROCEDURE_NOCAL_C1", "ENUMERATE_C1")
CONDS = ("ACCUMULATED", "FRESH", "WORKSPACE_SCRAMBLED")


def S(m):
    return m["successes"]


def run_one(world, seed, name):
    with adapt.world_context(world) as cfg:
        tasks = streams.lifetime(cfg, seed, "gate")
        life = {c: evaluate.run_lifetime(bl.make_baseline(name), tasks, cfg, c, seed=seed) for c in CONDS}
        cc = evaluate.causal_controls(bl.make_baseline(name), tasks, cfg, seed=seed)
        reads = dict(adapt.READS)
    return {
        "T": {c: S(life[c]["metrics"]) for c in CONDS},
        "replay_hash": {c: life[c]["replay_hash"] for c in CONDS},
        "snapshot_index": cc["snapshot_index"],
        "rem": {"ACCUMULATED": S(cc["ACCUMULATED_remainder"]),
                "CODE_ONLY": S(cc["CODE_ONLY"]), "COMPUTE_MATCHED": S(cc["COMPUTE_MATCHED"]),
                "STORAGE_MATCHED": S(cc["STORAGE_MATCHED"]),
                "ARTIFACT_ABLATION_ALL": S(cc["ARTIFACT_ABLATION_ALL"]) if "ARTIFACT_ABLATION_ALL" in cc else None,
                "ARTIFACT_TRANSPLANT": S(cc["ARTIFACT_TRANSPLANT"]),
                "FULL_WORKSPACE_TRANSPLANT": S(cc["FULL_WORKSPACE_TRANSPLANT"])},
        "ablation_each_block": {b: S(m) for b, m in cc["ARTIFACT_ABLATION"].items()},
        "blocks_at_snapshot": cc["blocks_at_snapshot"],
        "label_reads": reads,
    }


def rule(rows, positive="PROCEDURE_REUSE_C1"):
    """GATE_RULE.md s4 P1-P5 for one (world, seed): rows = {player: run_one result}. Returns {P1..P5: bool, detail}."""
    p = rows[positive]
    rem, T = p["rem"], p["T"]
    comp = [rows[n]["rem"]["ACCUMULATED"] for n in PLAYERS if n != positive]
    best = max([rem["CODE_ONLY"], rem["COMPUTE_MATCHED"], rem["STORAGE_MATCHED"]] + comp)
    G = rem["ACCUMULATED"] - rem["CODE_ONLY"]
    each = list(p["ablation_each_block"].values())
    out = {"P1": rem["ACCUMULATED"] - best >= 6,
           "P2": T["ACCUMULATED"] - T["FRESH"] >= 10 and T["ACCUMULATED"] - T["WORKSPACE_SCRAMBLED"] >= 10,
           "P3": (rem["ARTIFACT_ABLATION_ALL"] is not None and rem["ARTIFACT_ABLATION_ALL"] <= rem["CODE_ONLY"] + 0.2 * G
                  and bool(each) and min(each) <= rem["ACCUMULATED"] - 0.5 * G),
           "P4": rem["ARTIFACT_TRANSPLANT"] >= rem["CODE_ONLY"] + 0.8 * G}
    near = []
    for n in ("PROCEDURE_NOCAL_C1", "TABLE_MEMO_C1", "QUIT_C1"):
        r = rows[n]
        near.append(r["T"]["ACCUMULATED"] - r["T"]["FRESH"] <= 3 and r["rem"]["ACCUMULATED"] - r["rem"]["CODE_ONLY"] <= 2)
    out["P5"] = all(near)
    out["lifetime_pass"] = all(out[k] for k in ("P1", "P2", "P3", "P4", "P5"))
    out["detail"] = {"G": G, "best_competitor_rem": best, "ACC_rem": rem["ACCUMULATED"]}
    return out


def main(path):
    t0 = time.time()
    res = {"schema": "prometheus.rso.gen5.crius.gate.v1", "seeds": list(SEEDS), "runs": {}, "rule": {}, "probe_rule": {}}
    for w in WORLDS:
        for s in SEEDS:
            rows = {n: run_one(w, s, n) for n in PLAYERS}
            res["runs"]["%s/%d" % (w, s)] = rows
            res["rule"]["%s/%d" % (w, s)] = rule(rows)
            # falsifiability probe of the RULE: each near-miss / witness substituted as the "positive" (must FAIL)
            res["probe_rule"]["%s/%d" % (w, s)] = {n: rule(rows, positive=n)["lifetime_pass"] for n in
                                                    ("QUIT_C1", "TABLE_MEMO_C1", "PROCEDURE_NOCAL_C1", "ENUMERATE_C1")}
            print(w, s, res["rule"]["%s/%d" % (w, s)]["lifetime_pass"], round(time.time() - t0, 1), flush=True)
    res["wall_seconds"] = round(time.time() - t0, 1)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1])
