"""Q1 robustness of the NECESSARY call: how hard does competence fall for each necessary knockout?

    python -B ko_rates.py      (after core_map.py)  -> adds per-genome fields to core_map.json

run_de.competent is boolean at a 0.5 threshold, so a genome whose own stage-2 rate is ~0.5 can "lose" competence
from a small perturbation. For every competent sampled genome this computes:
  base_rate  = the genome's own stage-2 rate (run_dd.assay_one, competent()'s exact tag and K2 = 20 seeds);
  per necessary position, for each replacement value that lost competence (same RNG as core_map.knockout):
     stage-1 hits (4 seeds, competent()'s tag); if > 0, the stage-2 rate (20 seeds).
  COLLAPSE = the knockout's rate is <= 0.25 (stage-1 zero counts as collapse). A position is a COLLAPSE position iff
  >= 2 of its tried values lost AND >= 2 of all its tried values collapsed.
"""
from __future__ import annotations

import hashlib
import json
import random

import fsetup as F
import core_map as M


def rates(cell, g, dense):
    r = F.runner(cell, dense)
    tag = ("X-DD-ESTABLISH", hashlib.sha256(g).hexdigest()[:16])
    h1, _ = F.run_dd.assay_one(F.world, r, g, tag + (1,), F.run_dd.K1)
    if not h1:
        return 0, 0.0
    h2, _ = F.run_dd.assay_one(F.world, r, g, tag + (2,), F.run_dd.K2)
    return h1, h2 / F.run_dd.K2


def main():
    d = json.load(open(M.OUT))
    for row in d["rows"]:
        if not row["competent"]:
            continue
        g = bytes.fromhex(row["hex"])
        dense = row["vm"] == "DENSE"
        F.set_vm(dense)
        row["base_rate"] = rates(row["cell"], g, dense)[1]
        collapse, per = [], {}
        for p in row["necessary"]:
            rng = random.Random(int(hashlib.sha256(g + bytes([p])).hexdigest()[:16], 16) ^ M.SEED)
            vals = rng.sample([v for v in range(256) if v != g[p]], 3)
            lost, tried = row["ko_detail"][p]
            rs = []
            for v in vals[:tried]:
                m = bytearray(g)
                m[p] = v
                rs.append(rates(row["cell"], bytes(m), dense)[1])
            per[str(p)] = rs
            if sum(x <= 0.25 for x in rs) >= 2:
                collapse.append(p)
        row["ko_rates"] = per
        row["collapse"] = collapse
        row["n_collapse"] = len(collapse)
    M.OUT.write_text(json.dumps(d))


if __name__ == "__main__":
    main()
