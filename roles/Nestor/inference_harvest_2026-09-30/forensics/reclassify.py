"""Recompute the instruction roles of every necessary position in core_map.json with core_map.classify (side-aware:
the trace is taken on the donor side that actually passes the zero-state P-11 assay). Knockout results are not
recomputed. Idempotent.

    python -B reclassify.py
"""
from __future__ import annotations

import collections
import json

import core_map as M


def main():
    d = json.load(open(M.OUT))
    for r in d["rows"]:
        if not r["competent"]:
            continue
        g = bytes.fromhex(r["hex"])
        roles, info = M.classify(g, r["vm"] == "DENSE", r["necessary"])
        r.update({"roles": {str(p): v for p, v in roles.items()}, "role_counts": dict(collections.Counter(roles.values())),
                  "trace": info, "beyond_motif": len([p for p in r["necessary"] if p not in set(info["motif_positions"])])})
    d["meta"]["reclassified"] = True
    M.OUT.write_text(json.dumps(d))


if __name__ == "__main__":
    main()
