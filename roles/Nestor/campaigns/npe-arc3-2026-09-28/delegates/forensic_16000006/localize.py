"""Step 2 localization: full factorial of the 3 byte changes on the step vid 270 -> vid 320 (the first STATE_ROBUST
lineage member), applied to the non-robust parent 270. 20 seeds x 2 sides, seed tag 'F16-LOC' (distinct from the
causal tests' tag). Also the single step D0(vid 63) -> 270 (bytes 0 and 38) is covered by the causal tests.
Writes localize.json."""
import itertools
import json
import pathlib

import measure as M

HERE = pathlib.Path(__file__).resolve().parent
G = json.loads((HERE / "genealogy.json").read_text())
P = {p["vid"]: p for p in G["path"]}
par, child = bytes.fromhex(P[270]["g"]), bytes.fromhex(P[320]["g"])
pos = [i for i in range(64) if par[i] != child[i]]
rows = []
for k in range(len(pos) + 1):
    for sub in itertools.combinations(pos, k):
        g = bytearray(par)
        for i in sub:
            g[i] = child[i]
        g = bytes(g)
        r = M.state_rates(g, 20, ("FRESH", "SELF1", "SELF2", "CONST", "RANDOM"), tag="F16-LOC")
        rows.append({"applied": list(sub), "hex": g.hex(), "competent": M.competent(g), "rates": r,
                     "robust": M.robust(r)})
        print(rows[-1]["applied"], rows[-1]["competent"], r, rows[-1]["robust"], flush=True)
(HERE / "localize.json").write_text(json.dumps({"positions": pos, "rows": rows}, indent=1))
