"""W2-O step 1: stratified sample of recorded C1 NULL evolve cells. Rule fixed BEFORE any evaluation.
Strata (family x topology class x light-cone cap); within a stratum one cell drawn by a seeded RNG
(numpy default_rng(0x57324F)) from the cell_id-sorted eligible list. Directed graphs (random/smallworld)
are deliberately represented in every family because the actuator-reachability question lives there.
multi-hop RELAY := d > radius on torus/ring, d >= 2 on random/smallworld (global excluded: 1 hop)."""
import gzip, json, pathlib
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
R = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
lc = {r["cell"]: r for r in json.load(open(ROOT / "roles/Ananke/research/harvest/H-PLANT/out/lc_census.json"))["rows"]}
ev = sorted([r for r in R if r["kind"] == "evolve" and not r["labels"].get("SIGNAL")], key=lambda r: r["cell_id"])
g = np.random.default_rng(0x57324F)
def capped(r):
    b = lc.get(r["cell_id"], {}).get("bound")
    return b is not None and b < 0.60
def mh(r):
    p, d = r["physics"], r["env"]["d"]
    if p["topology"] in ("torus", "ring"): return d > p["radius"]
    if p["topology"] in ("random", "smallworld"): return d >= 2
    return False
DIR = ("random", "smallworld"); SYM = ("ring", "torus", "global")
strata = [
    ("XOR", "uncapped-directed", lambda r: not capped(r) and r["physics"]["topology"] in DIR),
    ("XOR", "uncapped-symmetric", lambda r: not capped(r) and r["physics"]["topology"] in SYM),
    ("XOR", "capped-directed", lambda r: capped(r) and r["physics"]["topology"] in DIR),
    ("XOR", "capped-symmetric", lambda r: capped(r) and r["physics"]["topology"] in SYM),
    ("FLIP", "random", lambda r: r["physics"]["topology"] == "random"),
    ("FLIP", "smallworld", lambda r: r["physics"]["topology"] == "smallworld"),
    ("FLIP", "symmetric", lambda r: r["physics"]["topology"] in SYM and not r["cell_id"].startswith("6f82f9c7")),
    ("RELAY", "mh-random", lambda r: mh(r) and r["physics"]["topology"] == "random"),
    ("RELAY", "mh-smallworld", lambda r: mh(r) and r["physics"]["topology"] == "smallworld"),
    ("RELAY", "mh-ring", lambda r: mh(r) and r["physics"]["topology"] == "ring"),
    ("RELAY", "mh-torus", lambda r: mh(r) and r["physics"]["topology"] == "torus"),
    ("MAJ", "random", lambda r: r["physics"]["topology"] == "random"),
    ("MAJ", "smallworld", lambda r: r["physics"]["topology"] == "smallworld"),
    ("MAJ", "ring", lambda r: r["physics"]["topology"] == "ring"),
    ("MAJ", "torus", lambda r: r["physics"]["topology"] == "torus"),
]
out = [{"family": "FLIP", "stratum": "d9cc-named", "cell": "6f82f9c7d51bcef1", "n_eligible": 1}]
for fam, name, f in strata:
    el = [r for r in ev if r["env"]["family"] == fam and f(r)]
    r = el[int(g.integers(len(el)))]
    out.append({"family": fam, "stratum": name, "cell": r["cell_id"], "n_eligible": len(el)})
for o in out:
    r = next(x for x in ev if x["cell_id"] == o["cell"])
    o.update(wave=r["wave"], topology=r["physics"]["topology"], radius=r["physics"]["radius"], n_sites=r["physics"]["n_sites"],
             d=r["env"]["d"], delta=r["env"]["delta"], update_mode=r["physics"]["update_mode"],
             lc_bound=lc.get(o["cell"], {}).get("bound"), held=r["result"]["held"]["acc"], held_lo99=r["result"]["held"]["lo99"])
    print(o)
(HERE / "out").mkdir(exist_ok=True)
(HERE / "out/sample.json").write_text(json.dumps(out, indent=1))
