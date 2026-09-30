"""PHASE 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN (+ CE reference only). No treatment."""
import json
import sys
import time
import sim

ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
t0 = time.process_time()
with open("pilot_rows.jsonl", "w") as fr, open("ce_reference_rows.jsonl", "w") as fc:
    for seed in sim.SEEDS:
        ce = sim.run_arm(seed, sim.policy_ce)
        nt = sim.run_arm(seed, sim.policy_null_twin, rng_stream=3)
        pc = sim.run_arm(seed, sim.policy_positive)
        cheat = [dict(e, forbidden=0, steps=c["steps"], probe_bits=2 * e["probe_bits"])
                 for e, c in zip(nt, ce)]
        base = dict(seed=seed, attempt=ATTEMPT, params=sim.PARAMS)
        fc.write(json.dumps(dict(base, arm="CE_REFERENCE", role="reference", episodes=ce)) + "\n")
        fc.flush()
        for arm, eps in (("POSITIVE_CONTROL", pc), ("CHEAT", cheat), ("NULL_TWIN", nt)):
            fr.write(json.dumps(dict(base, arm=arm, episodes=eps)) + "\n")
            fr.flush()
        print(seed, "done", round(time.process_time() - t0, 1), flush=True)
cpu = time.process_time() - t0
print("cpu_s", cpu)
with open("cpu_log.txt", "a") as f:
    f.write(f"pilot attempt {ATTEMPT} cpu_s {cpu:.2f}\n")
