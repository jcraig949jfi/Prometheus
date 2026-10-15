"""Recorded limitations a counterfeit is ALLOWED to reach a verdict through (the runner prints LIMITATION <id>, never passes
silently, never fails the build). An id is valid only while its source text still contains its marker: a limitation that was
repaired or reworded must be re-read, not trusted. Add an id here only for a limitation the owner has already recorded."""
import os

from rso.registry.registry import ROOT

LIMITATIONS = {
    "C018-R1c": {
        "source": "rso/aether/RESULT.md",
        "marker": "Clamp arrays (R1c)",
        "summary": "CUT_B / CUT_N first-divergence arrays of the 58 non-sampled Aether units are bound to the record by "
                   "the warm snapshot, the replayed tree and the invariants, not replayed: an invariant-respecting rewrite "
                   "changes a non-sampled unit's class and no check fails (C-018-T042 R1c).",
    },
    "C013-D1-trusts-derived": {
        "source": "rso/registry/entries.py",
        "marker": "tampered certificate/seeded fields survive analyze",
        "summary": "rso.reach.analyze counts the runner-derived row['discovery'] without re-deriving it from certificate "
                   "and seeded_hit (C-013 D1 integration mutation; rso/reach/INTEGRATION_D1.md s2).",
    },
}


def problems(lid):
    """[] if `lid` is registered and its marker is still in its source; else the reasons it cannot be used."""
    if lid not in LIMITATIONS:
        return ["unregistered limitation id %r" % lid]
    rec = LIMITATIONS[lid]
    path = os.path.join(ROOT, rec["source"])
    if not os.path.exists(path):
        return ["%s: source %s is gone" % (lid, rec["source"])]
    with open(path, encoding="utf-8") as f:
        if rec["marker"] not in f.read():
            return ["%s: marker %r no longer in %s" % (lid, rec["marker"], rec["source"])]
    return []
