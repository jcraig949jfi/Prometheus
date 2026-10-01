"""W2-T step 1: population of C1 NULL evolve cells (held lo99 <= .55, == not labels.SIGNAL) in XOR/FLIP/RELAY/MAJ
(+ HOLD NULLs), and a 25% random subsample per family for the FULL guarded replay (held normal + zero_comm in one
guarded() context, plus FINAL-seed ranking evaluation). Rule and seed (0x57325454 "W2TT") fixed before any run.
Every cell (subsample or not) gets the guarded NORMAL held arm (known-answer on acc/lo99/hi99/tel, guards that do
not need a matched control, engagement, wake recomputation) and the analytic checks."""
import gzip, json, pathlib
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
R = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
ev = sorted([r for r in R if r["kind"] == "evolve" and r["result"]["held"]["lo99"] <= 0.55], key=lambda r: r["cell_id"])
assert all(not r["labels"].get("SIGNAL") for r in ev)
g = np.random.default_rng(0x57325454)
out = []
for fam in ("XOR", "FLIP", "RELAY", "MAJ", "HOLD"):
    el = [r["cell_id"] for r in ev if r["env"]["family"] == fam]
    k = int(round(0.25 * len(el)))
    sub = set(g.choice(len(el), size=k, replace=False).tolist())
    for i, c in enumerate(el):
        out.append({"cell": c, "family": fam, "full": i in sub})
    print(fam, len(el), k)
(HERE / "out/cells.json").write_text(json.dumps(out, indent=1))
