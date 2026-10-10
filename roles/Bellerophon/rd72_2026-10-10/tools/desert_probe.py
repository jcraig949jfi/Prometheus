"""BEL-RD-72 composition-desert geometry probe (EXPLORATORY, static, no world is run; post-E1b, disclosed as post hoc).
    python3 desert_probe.py E1B_RESULTS E1B_PLAN OUT.json [N_PATHS]
For every E1b world in which a FUNC LO solver and a FUNC HI solver coexist in one census, take the most common LO and HI
FUNC tapes at the FIRST such census and count one-step routes to a FUNC BOTH tape (both halves of the task, the census
semantics of light_halves.LightHalvesWorld.halves) from each, under SUB / MOVE / INS / DEL and DONOR (segments of the
partner tape; the uptake / partial-overwrite operator), plus a 3-step random-path estimate (geometry.sample_paths) with
the partner as donor. Geometric only: no selection, no population, no rates."""
import json, sys, pathlib
_H = pathlib.Path(__file__).resolve()
for _p in (_H.parent, _H.parents[1].parent / "bel48h_2026-10-08" / "tools", _H.parents[4]):
    sys.path.insert(0, str(_p))
from prometheus.z80atlas import geometry
from prometheus.z80atlas.world import Config
from light_halves import LightHalvesWorld
L = 64


def main(resp, planp, outp, npaths=2000):
    plan = {p["id"]: p for p in json.load(open(planp))}
    out = []
    for line in open(resp):
        r = json.loads(line)
        cen = next((x for x in r["census"] if x["halves_func"].get("LO") and x["halves_func"].get("HI")), None)
        if cen is None:
            continue
        w = LightHalvesWorld(Config(**plan[r["id"]]["cfg"]), 0, census_every=10 ** 9)
        both = lambda t: w.halves(t) == "BOTH" and w.func(t)
        lo = bytes.fromhex(cen["top_func"]["LO"]); hi = bytes.fromhex(cen["top_func"]["HI"])
        assert w.halves(lo) == "LO" and w.halves(hi) == "HI" and w.func(lo) and w.func(hi), r["id"]
        rec = {"id": r["id"], "tick": cen["tick"], "n_LO": cen["halves_func"]["LO"], "n_HI": cen["halves_func"]["HI"],
               "hamming_LO_HI": sum(a != b for a, b in zip(lo, hi))}
        for name, t, partner in (("from_LO", lo, hi), ("from_HI", hi, lo)):
            rec[name] = geometry.scan_operators(t, L, both, donors=(partner,))
            rec[name + "_paths3"] = geometry.sample_paths(t, L, both, ops=("SUB", "MOVE", "INS", "DEL", "DONOR"), depth=3,
                                                         n=npaths, seed=7207, donors=(partner,))
        out.append(rec); print(json.dumps(rec), flush=True)
    json.dump(out, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 2000)
