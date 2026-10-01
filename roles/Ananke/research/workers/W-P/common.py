"""Specimen loading exactly as W-M apply.py (c1b_run.load via full cell id)."""
import gzip, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
for p in (str(REPO), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)
from prometheus.ananke import assays, c1b_run  # noqa

SEED_NS = 0x610


def full_ids():
    ids = {}
    with gzip.open(REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt") as f:
        for l in f:
            r = json.loads(l)
            if r["kind"] == "evolve":
                ids[r["cell_id"][:8]] = r["cell_id"]
    return ids


def load(name):
    ph, env, g, row = c1b_run.load(full_ids()[name])
    return ph, env, g, row
