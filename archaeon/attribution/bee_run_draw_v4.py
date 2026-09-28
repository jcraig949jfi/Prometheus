"""Prereg v4 s5 run selection, step 2 of 2. Seed = the full SHA of the commit that froze BEE_POPULATION_v4.json
(ea1d284ba67ecdcc661be64a0240eb3126af5731, pushed before this file existed). index = int(sha256(seed), 16) % n over the sorted
eligible list.
    python -m archaeon.attribution.bee_run_draw_v4
"""
import hashlib
import json

POP = "ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/BEE_POPULATION_v4.json"
SEED = "ea1d284ba67ecdcc661be64a0240eb3126af5731"

if __name__ == "__main__":
    pop = json.load(open(POP))["eligible"]
    i = int(hashlib.sha256(SEED.encode()).hexdigest(), 16) % len(pop)
    print(json.dumps({"seed": SEED, "n": len(pop), "index": i, "drawn": pop[i]}))
