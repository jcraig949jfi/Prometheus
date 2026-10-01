"""PHASE 2: TREATMENT (error-scaled) and CONTROL (constant jitter, matched
time-averaged sd per seed), plus the three pilot arms rerun via core."""
import json, time
import numpy as np
import core

def treatment_sd(ema, t, rng, state):
    return core.errscaled_sd(ema)

def main():
    t0 = time.process_time()
    with open("rows.jsonl", "w", encoding="utf-8") as f:
        for seed in core.SEEDS:
            tr = core.run_replicator(seed, treatment_sd, "TREATMENT")
            s_c = tr["mean_sd_applied"]
            ct = core.run_replicator(seed, lambda ema, t, rng, st: np.full(core.N, s_c), "CONTROL")
            ct["constant_sd"] = s_c
            rows = [tr, ct, core.run_null_twin(seed), core.run_positive(seed), core.run_cheat(seed)]
            for r in rows:
                r["attempt"] = 1
                f.write(json.dumps(r) + "\n"); f.flush()
    json.dump({"cpu_seconds": time.process_time() - t0}, open("world_cpu.json", "w"))

if __name__ == "__main__":
    main()
