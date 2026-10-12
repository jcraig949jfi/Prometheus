"""C-018-T021: executability smoke of the Crius reuse controls (read-only; NOT an experiment, no claim).

    python -m rso.gen5.smoke_crius rso/gen5/smoke_crius_result.json

Runs Crius's own committed baselines and conditions on 3 NEW lifetime seeds (18_021_001..003; Crius registered 1, 201-203,
301-303) on the frozen crius/configs/c1.json. One process, a few seconds. Purpose: show that a known-answer reuse
positive, its identifier-permutation near-miss, and the answer-table / abstention witnesses execute on harry1 CPU.
"""
import json
import sys
import time

from crius import baselines_c1 as bl, evaluate, streams, vm

SEEDS = (18021001, 18021002, 18021003)


def main(out):
    cfg = json.load(open("crius/configs/c1.json"))
    vm.set_substrate(cfg.get("substrate", {}))
    rows = []
    t0 = time.time()
    for seed in SEEDS:
        tasks = streams.lifetime(cfg, seed, "gate")
        row = {"seed": seed, "tasks": len(tasks)}
        for name in ("QUIT_C1", "TABLE_MEMO_C1", "PROCEDURE_NOCAL_C1", "PROCEDURE_REUSE_C1"):
            r = {}
            for cond in ("ACCUMULATED", "FRESH", "WORKSPACE_SCRAMBLED"):
                m = evaluate.run_lifetime(bl.make_baseline(name), tasks, cfg, cond, seed=seed)["metrics"]
                r[cond] = {"successes": m["successes"], "fitness": round(m["fitness"], 3)}
            row[name] = r
        c = evaluate.causal_controls(bl.make_baseline("PROCEDURE_REUSE_C1"), tasks, cfg, seed=seed)
        row["PROCEDURE_REUSE_C1_causal_successes"] = {
            k: v["successes"] for k, v in c.items() if isinstance(v, dict) and "successes" in v}
        row["PROCEDURE_REUSE_C1_causal_successes"]["ARTIFACT_ABLATION_each_block"] = {
            b: m["successes"] for b, m in c["ARTIFACT_ABLATION"].items()}
        rows.append(row)
    json.dump({"schema": "prometheus.rso.gen5.smoke_crius.v1", "config": "crius/configs/c1.json", "rows": rows,
               "wall_seconds": round(time.time() - t0, 1)}, open(out, "w"), indent=1)
    print(json.dumps(rows[0], indent=1)[:2500])


if __name__ == "__main__":
    main(sys.argv[1])
