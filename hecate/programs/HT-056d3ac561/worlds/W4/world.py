"""W4 PHASE 2: TREATMENT (Lasso on sparse faults), CONTROL (min-norm on the
same trials), plus the three pilot arms rerun through the same dispatcher.
Parameters are core.PARAMS, unchanged from the passing pilot (attempt 2)."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import json
import time

import core

HERE = os.path.dirname(os.path.abspath(__file__))
PC_MODE = "oracle_support"   # the repaired positive control that passed the pilot
ARMS = ("POSITIVE_CONTROL", "CHEAT", "NULL_TWIN", "TREATMENT", "CONTROL")


def arm_trials(world, seed, arm, k):
    """Return (Ftrue, Fhat_arm, Y) for any arm."""
    if arm in ("TREATMENT", "CONTROL"):
        Fs = core.sparse_faults(core.stream(seed, core.FAM_SPARSE, k), k, core.PARAMS["trials"])
        Y = core.simulate_y(world, Fs, core.stream(seed, core.FAM_NOISE_TR, k))
        Fh = core.recover_lasso(world, Y) if arm == "TREATMENT" else core.recover_minnorm(world, Y)
        return Fs, Fh, Y
    Ft, Y, Fs = core.arm_data(world, seed, k, arm, PC_MODE)
    if arm == "POSITIVE_CONTROL":
        Fh = core.recover_oracle_support(world, Y, Fs)
    elif arm == "CHEAT":
        Fh = Ft.copy()
    else:
        Fh = core.recover_lasso(world, Y)
    return Ft, Fh, Y


def run_arm(world, seed, arm):
    per_k = {}
    for k in core.PARAMS["sparsity_levels"]:
        Ft, Fh, Y = arm_trials(world, seed, arm, k)
        # "lasso" slot = the arm's own estimate (CONTROL: min-norm); "mn" slot = min-norm
        d = core.summarize(*core.observables(world, Ft, Fh), "lasso")
        d.update(core.summarize(*core.observables(world, Ft, core.recover_minnorm(world, Y)), "mn"))
        per_k[str(k)] = d
    return per_k


def main():
    t0 = time.process_time()
    out = os.path.join(HERE, "rows.jsonl")
    for seed in core.SEEDS:
        world = core.make_world(seed)
        for arm in ARMS:
            per_k = run_arm(world, seed, arm)
            row = core.make_row(arm, seed, world, per_k, 1, PC_MODE, "phase2")
            core.append_row(out, row)
            print(arm, seed, {k: (round(v["lasso_success_rate"], 3), round(v["mn_success_rate"], 3))
                              for k, v in per_k.items()}, flush=True)
    cpu = time.process_time() - t0
    with open(os.path.join(HERE, "cpu_ledger.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"script": "world.py", "attempt": 1, "pc_mode": PC_MODE,
                             "cpu_seconds": cpu}) + "\n")
    print("cpu_seconds", round(cpu, 2))


if __name__ == "__main__":
    main()
