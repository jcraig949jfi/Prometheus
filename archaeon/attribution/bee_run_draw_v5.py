"""Prereg v5 R6, step 2 of 2. Seed = the full SHA of the commit that froze BEE_POPULATION_v5.json and ANCESTRY_PREREG_v5.md
(0889878aadec958f8d93d4fa356a137ef651034d, pushed before this file existed). index = sha256(seed) mod n over the sorted eligible
list. Pre-committed fallback (v5 R6): index + 1, + 2, ... if the drawn run's transmission class has < 30 births.
    python -m archaeon.attribution.bee_run_draw_v5 [--offset k]
"""
import hashlib
import json
import sys

POP = "ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/BEE_POPULATION_v5.json"
SEED = "0889878aadec958f8d93d4fa356a137ef651034d"

if __name__ == "__main__":
    a = sys.argv[1:]; k = int(a[a.index("--offset") + 1]) if "--offset" in a else 0
    pop = json.load(open(POP))["eligible"]
    i = (int(hashlib.sha256(SEED.encode()).hexdigest(), 16) + k) % len(pop)
    print(json.dumps({"seed": SEED, "n": len(pop), "offset": k, "index": i, "drawn": pop[i]}))
