"""Localization of the FULL state-robustness step vid 736 -> vid 1005 (bytes 0 and 2), factorial on the parent,
plus block-copy register traces (HL/DE/BC at each LDDR the donor executes) from FRESH, CONST and the donor's own
carried state (k=1), side 0 and side 1, for D0 (vid 211), 736 and 1005. Tag 'F16-LOC2'. Writes localize2.json."""
import itertools
import json
import pathlib
import random
import sys

import measure as M
from kcurve import kcurve

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "npe-p2-endogenous-heredity-2026-09-27" / "delegates" / "corpus"))
import corpus_analysis as ca  # noqa: E402

G = json.loads((HERE / "genealogy2.json").read_text())
R = {r["vid"]: r for r in G["path"]}
par, child = bytes.fromhex(R[736]["g"]), bytes.fromhex(R[1005]["g"])
pos = [i for i in range(64) if par[i] != child[i]]
rows = []
for k in range(len(pos) + 1):
    for sub in itertools.combinations(pos, k):
        g = bytearray(par)
        for i in sub:
            g[i] = child[i]
        g = bytes(g)
        r = M.state_rates(g, 20, ("FRESH", "CONST", "RANDOM"), tag="F16-LOC2")
        r["k"] = kcurve(g, tag="F16-LOC2K")
        rows.append({"applied": list(sub), "hex": g.hex(), "competent": M.competent(g), "rates": r})
        print(sub, rows[-1]["competent"], r, flush=True)

world, r = M.env()
n = r.L
traces = {}
for vid in (211, 736, 1005):
    g = bytes.fromhex(R[vid]["g"])
    for side in (0, 1):
        victim = bytes(random.Random(7).randrange(256) for _ in range(n))
        for cond in ("FRESH", "CONST", "SELF1", "SELF2"):
            st = M.start_state(g, cond, 0, side, "F16-TR")
            ev = ca.trace_blockcopy(world, r, g, side, victim, st=st)
            traces["%d/side%d/%s" % (vid, side, cond)] = {"start": st, "blockcopies": ev}
            print(vid, side, cond, st, ["%s pc%02X HL%04X DE%04X BC%04X" % (e["kind"], e["pc_rel_own"], e["HL"], e["DE"], e["BC"]) for e in ev], flush=True)
(HERE / "localize2.json").write_text(json.dumps({"positions": pos, "rows": rows, "traces": traces}, indent=1))
