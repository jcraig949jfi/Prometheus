"""Prereg v5 s5 run selection, step 1 of 2 (Review 6 s5: v4's draw had no RELEVANCE condition; r025144's 92 births were
budget-ended LDIR memory sweeps with no writer-material transmission).

Eligibility, computed identically for every run in r038751's cell from the preserved birth rows alone:
- traced AND VM_COPY AND SHARED AND ENDOGENOUS_COPY (the v4 cell); AND
- a MECHANISM screen: >= 30 births with row field 8 (copies whose source address lies in the writer's region) >= L/2 AND
  row field 9 (those performed by writer-region code) >= L/2.
The screen is a relevance condition only. It never enters any ancestry measurement, where address readings remain forbidden
(v4 s1.4).

Step 2 (a LATER commit): seed = the full SHA of the commit that adds this file's output; index = sha256(seed) mod n over the sorted
eligible list.

PRE-COMMITTED FALLBACK: if the drawn run fails the tracer-based transmission check (fewer than 30 births whose written loci are
majority (ENTITY writer) MOVE-labelled under v5 identification), take index + 1 mod n, and so on. Every step is recorded. There is
no birth-weighted second draw (v4's optional one is dropped).
    python -m archaeon.attribution.bee_run_population_v5 OUT.json
"""
import gzip
import json
import os
import sys

BIRTHS = "C:/Users/James/z80atlas_forensics_2026-09-23_local/births"
RUNS = "C:/Users/James/z80atlas_campaign_2026-09-19/runs"
L = 64


def main(out):
    pop = []; screened = {}
    for f in sorted(os.listdir(BIRTHS)):
        if not f.endswith(".jsonl.gz"): continue
        rid = f.split(".")[0]; p = os.path.join(RUNS, rid, "config.json")
        if not os.path.exists(p): continue
        c = json.load(open(p))["config"]
        if not (c.get("representation") == "VM_COPY" and c.get("layout") == "SHARED" and c.get("reproduction") == "ENDOGENOUS_COPY"): continue
        n = 0
        for line in gzip.open(os.path.join(BIRTHS, f), "rt"):
            r = json.loads(line)
            if r[8] >= L // 2 and r[9] >= L // 2: n += 1
        screened[rid] = n
        if n >= 30: pop.append(rid)
    json.dump({"rule": "v4 cell AND >= 30 births with row[8] >= 32 and row[9] >= 32 (relevance screen only)", "cell_runs": len(screened),
               "screen_counts": screened, "eligible": sorted(pop), "n": len(pop)}, open(out, "w"), indent=0)
    print(json.dumps({"cell_runs": len(screened), "n_eligible": len(pop)}))


if __name__ == "__main__":
    main(sys.argv[1])
