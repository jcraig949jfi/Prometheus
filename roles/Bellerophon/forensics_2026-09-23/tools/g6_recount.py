"""Recount of GROUNDING_REPORT G6a (erratum 2026-09-29). Read-only over the preserved grounding results.

Defect (DEF-BEL-001, found by Artemis R-26): grounding_analysis.g6_class tests genealogy[0]["mechanism"] == "init", but
World._spawn never records birth_class for initial organisms, so World._genealogy reports their mechanism as None and
every origin was classified BUILT_BY_COPY. This recount uses the writer's recorded birth mechanism directly.
    python g6_recount.py C:/Users/James/z80atlas_grounding_2026-09-23/results.jsonl
"""
import collections
import json
import sys

R = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
spont = [r for r in R if r.get("spontaneous") and (r["lane"] in ("G1", "G1T") or (r["lane"] == "G7" and r["cell"].startswith("RANDOM/")))]
mech = collections.Counter(); unmod = 0
for r in spont:
    fsr = r.get("first_self_replication") or {}; gen = fsr.get("genealogy") or []
    w = gen[0] if gen else {}
    m = w.get("mechanism") if gen else "NO_GENEALOGY"
    mech[str(m)] += 1
    if gen and m is None and fsr.get("tape") == w.get("tape_at_birth"):
        unmod += 1
init = mech.get("None", 0)
print(json.dumps({"origins": len(spont), "writer_birth_mechanism": dict(mech), "initial_writers": init,
                  "initial_writers_unmodified": unmod, "built_by_copy": len(spont) - init - mech.get("NO_GENEALOGY", 0)}, indent=1))
