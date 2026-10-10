"""BEL-RD-72 F1 baseline accessibility (prereg s10 item 3; measurement only).   python3 f1_geometry.py F1_PLAN OUT.json
For every DISTINCT founder of cells KO1, KO2, ECHOH and REP: one-step routes to a FUNC BOTH tape (light_halves semantics)
under SUB / MOVE / INS / DEL (geometry.scan_operators). KO4 founders are not scanned (>= 4 substitutions by construction
unless another operator shortcuts; reported as not measured)."""
import json, sys, pathlib
_H = pathlib.Path(__file__).resolve()
for _p in (_H.parent, _H.parents[1].parent / "bel48h_2026-10-08" / "tools", _H.parents[4]):
    sys.path.insert(0, str(_p))
from prometheus.z80atlas import geometry
from prometheus.z80atlas.world import Config
from light_halves import LightHalvesWorld


def main(planp, outp):
    plan = json.load(open(planp)); seen = {}
    w = None
    for p in plan:
        if p["cell"] not in ("KO1", "KO2", "ECHOH", "REP") or p["founder"] in seen:
            continue
        if w is None:
            w = LightHalvesWorld(Config(**p["cfg"]), 0, census_every=10 ** 9)
        both = lambda t: w.halves(t) == "BOTH" and w.func(t)
        r = {"cell": p["cell"], "ko": p.get("ko"), "founder_halves": p.get("founder_halves"),
             "routes": {op: v["routes"] for op, v in geometry.scan_operators(bytes.fromhex(p["founder"]), 64, both, ops=("SUB", "MOVE", "INS", "DEL")).items()}}
        seen[p["founder"]] = r; print(json.dumps(r), flush=True)
    json.dump(seen, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
