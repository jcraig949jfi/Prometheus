"""W2-O: direct G8 (Ares held-out disjointness) over EVERY recorded C1 evolve row: held seed set vs the union
of all training-generation and final seed sets the row's search used (namespaces from search.py)."""
import os, sys, json, gzip, pathlib, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
from prometheus.ananke import assays
from prometheus.ananke.rng import H_int
from prometheus.ananke.search import TRAIN_NS, FINAL_NS, HELD_NS
t0 = time.process_time()
n = bad = 0
for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    r = json.loads(l)
    if r["kind"] != "evolve":
        continue
    sp, S = r["search"], r["search_seed"]
    sel = set(assays.world_seeds(H_int(S, FINAL_NS), sp["M_final"]))
    for g in range(sp["gens"]):
        sel |= set(assays.world_seeds(H_int(S, TRAIN_NS, g), sp["M"]))
    held = set(assays.world_seeds(H_int(S, HELD_NS), sp["M_held"]))
    n += 1
    bad += bool(sel & held)
res = {"evolve_rows": n, "rows_with_overlap": bad, "cpu_s": round(time.process_time() - t0, 1)}
print(res)
(HERE / "out/g8_all.json").write_text(json.dumps(res))
