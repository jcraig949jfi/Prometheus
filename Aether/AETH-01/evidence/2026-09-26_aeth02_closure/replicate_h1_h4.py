"""H1/H4 replication on additional seeds, 256^2, the 2026-09-24 protocol unchanged."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
AETHER = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [AETHER, os.path.join(AETHER, "test", "reference")]
from observatory import aeth02_falsifiers as F
i = int(sys.argv[1])
seed, rng_seed = F.B_SEED0 + i, F.B_RNG0 + i
out = {"seed_index": i, "seed": seed, "rng_seed": rng_seed, "n": 256,
       "h1": F.h1_repair(256, 2500, 500, seed=seed, rng_seed=rng_seed),
       "h4": F.h4_perturbation(256, 2500, 500, seed=seed, rng_seed=rng_seed)}
with open(os.path.join(HERE, "replicate_h1h4_s%d.json" % i), "w", newline="\n") as fh:
    json.dump(out, fh, indent=1, sort_keys=True, default=float); fh.write("\n")
print("h1 excess_final=%.4f falsified=%s | h4 drop1=%.4f drop_final=%.4f falsified=%s" % (
    out["h1"]["excess_final"], out["h1"]["falsified"], out["h4"]["observed_immediate_drop"],
    out["h4"]["by_horizon"][500]["drop"], out["h4"]["falsified"]))
