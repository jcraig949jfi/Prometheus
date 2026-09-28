"""Prereg v4 s5 run selection, step 1 of 2: freeze the ELIGIBLE POPULATION before any draw.

Eligibility (no outcome-based condition):
- traced runs in Bellerophon's preserved births directory;
- config representation == VM_COPY AND layout == SHARED AND reproduction == ENDOGENOUS_COPY (r038751's cell);
- the run directory and config exist on M2.
Step 2 (bee_run_draw_v4.py, a LATER commit) uses seed = the full SHA of the commit that adds this population file. That SHA cannot
be known before the commit, so the draw cannot be re-rolled after seeing the population.
    python -m archaeon.attribution.bee_run_population OUT.json
"""
import json
import os
import sys

BIRTHS = "C:/Users/James/z80atlas_forensics_2026-09-23_local/births"
RUNS = "C:/Users/James/z80atlas_campaign_2026-09-19/runs"


def main(out):
    pop = []; seen = 0
    for f in sorted(os.listdir(BIRTHS)):
        if not f.endswith(".jsonl.gz"): continue
        rid = f.split(".")[0]; seen += 1
        p = os.path.join(RUNS, rid, "config.json")
        if not os.path.exists(p): continue
        c = json.load(open(p))["config"]
        if c.get("representation") == "VM_COPY" and c.get("layout") == "SHARED" and c.get("reproduction") == "ENDOGENOUS_COPY":
            pop.append(rid)
    json.dump({"rule": "traced AND VM_COPY AND SHARED AND ENDOGENOUS_COPY (no outcome condition)", "traced_runs": seen,
               "eligible": sorted(pop), "n": len(pop)}, open(out, "w"), indent=0)
    print(json.dumps({"traced_runs": seen, "n_eligible": len(pop)}))


if __name__ == "__main__":
    main(sys.argv[1])
