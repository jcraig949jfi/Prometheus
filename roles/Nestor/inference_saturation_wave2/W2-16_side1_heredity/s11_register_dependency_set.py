"""Step 11: which initial registers does each copier depend on? Own context, own entry, HALT partner; set ONE register
(B,C,D,E,H,L,A) to each of 16 non-zero values (others FRESH 0) and record whether a good copy (>=0.9) is still made.
A register is a dependency if any value breaks the copy. Side-0 (111 DENSE) vs side-1 (17) copiers."""
import json, pathlib, collections, random
from _env import A, ROWS
import p11
from s10_side0_register_dependence import trial

NAMES = "BCDEHL?A"
out = {}
for side in (0, 1):
    sel = [r for r in ROWS if r["P11"]["certified"] and r["P11"]["certified_sides"] == [side] and r["vm"] == "DENSE"]
    dep = collections.Counter(); ndeps = collections.Counter(); per = {}
    for r in sel:
        G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"])
        ds = []
        for ri in (0, 1, 2, 3, 4, 5, 7):
            broke = 0
            for v in (1, 2, 3, 7, 15, 31, 63, 64, 65, 100, 127, 128, 129, 192, 200, 255):
                regs = [0] * 8; regs[ri] = v
                broke += not trial(z, P, G, side, (regs, 0, 0))
            if broke:
                ds.append(NAMES[ri]); dep[NAMES[ri]] += 1
        ndeps[len(ds)] += 1; per[r["key"]] = "".join(ds)
    out["side%d" % side] = {"n": len(sel), "genomes_depending_on_register": dict(dep),
                            "n_dependencies_hist": dict(sorted(ndeps.items())), "per_genome": per}
    print(side, len(sel), dict(dep), dict(sorted(ndeps.items())))
    if side == 1:
        print(per)
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
