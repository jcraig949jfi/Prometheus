"""C9-D14 probe: on the pair tape, does an organism's identity (oid) track its bytes?

The P-1 certificate follows oid through the parent map. On the pair tape an organism is
re-mutated every epoch and its partner can write into it, with no lineage event unless
the predecessor criterion fires. This probe runs H3 arm A of each pinned cell (tier S,
off-manifest seed 9_900_101) and, for organisms alive at the end that were NEVER the
child of any lineage edge (the zero-edge case the certificate accepts), measures byte
identity between the genome at placement and the genome at the end.

Reports fidelity only; no held, crossing or certificate outcome is read.
    python d14_probe.py -> D14_PROBE.json
"""
from __future__ import annotations

import json
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import manifest as M   # noqa: E402
import world           # noqa: E402


def probe(cell, seed=9_900_101):
    r = world.Runner(cell, seed, tier="S")
    orig = r._place
    first = {}

    def place(genome, anc, pid=None, niche=0):
        o = orig(genome, anc, pid, niche)
        if o is not None:
            first[o.oid] = bytes(genome)
        return o
    r._place = place
    r.run()
    children = {e["child"] for e in r.lineage if e["kind"] == "birth"}
    fids = [world._fidelity(first[o.oid], r._genome(o)) for o in r.orgs
            if o.alive and o.oid in first and o.oid not in children]
    return {"zero_edge_alive": len(fids),
            "fidelity_to_own_birth_genome_median": round(statistics.median(fids), 4) if fids else None,
            "share_below_0.50": round(sum(f < 0.5 for f in fids) / len(fids), 4) if fids else None,
            "share_below_0.10": round(sum(f < 0.1 for f in fids) / len(fids), 4) if fids else None,
            "epochs": r.epoch}


def main():
    out = {rid: probe(cell) for rid, cell in M.H3_CELLS}
    (HERE / "D14_PROBE.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
