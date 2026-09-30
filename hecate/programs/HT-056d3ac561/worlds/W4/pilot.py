"""W4 PHASE 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN only.

usage: python pilot.py <attempt> <pc_mode>   pc_mode in {spec_rowspace, oracle_support}
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import json
import sys
import time

import core

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    attempt = int(sys.argv[1])
    pc_mode = sys.argv[2]
    assert pc_mode in ("spec_rowspace", "oracle_support")
    t0 = time.process_time()
    out = os.path.join(HERE, "pilot_rows.jsonl")
    checks = {}
    for seed in core.SEEDS:
        world = core.make_world(seed)
        checks[seed] = core.check_simulation(world, seed)
        for arm in ("POSITIVE_CONTROL", "CHEAT", "NULL_TWIN"):
            per_k = core.run_control_arm(world, seed, arm, pc_mode)
            row = core.make_row(arm, seed, world, per_k, attempt, pc_mode, "pilot")
            row["sim_check"] = checks[seed]
            core.append_row(out, row)
            print(arm, seed, {k: (round(v["lasso_success_rate"], 3), round(v["mn_success_rate"], 3))
                              for k, v in per_k.items()}, flush=True)
    cpu = time.process_time() - t0
    with open(os.path.join(HERE, "cpu_ledger.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"script": "pilot.py", "attempt": attempt, "pc_mode": pc_mode,
                             "cpu_seconds": cpu}) + "\n")
    print("cpu_seconds", round(cpu, 2))


if __name__ == "__main__":
    main()
