"""W7 instrument hygiene -- shared helpers (read-only use of the frozen engine).
Nothing here modifies an engine file; engine modules are imported as-is."""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("A17_FASTEVAL", "1")
os.environ.setdefault("A18_FASTCOST", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                      # roles/Aphrodite
ENG = ROOT / "engine"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ENG))
sys.path.insert(0, str(ENG / "accel"))
sys.path.insert(0, str(ROOT / "science" / "compounding" / "rb1"))
import a18                                   # noqa: E402
import a17                                   # noqa: E402
import a18_c1 as C                           # noqa: E402
from a18 import G, FR                        # noqa: E402

SETS = {
    "A19": ENG / "A19_C2" / "A18_FOUNDRY_ROWS_2026-09-28.jsonl",
    "A20": ENG / "A20_C3" / "A20_FOUNDRY_ROWS_2026-09-28.jsonl",
}
N_COV = len(G.H1_SPACE) * len(G.H2_SPACE) * len(G.FINAL_SPACE)


def rows(tag, t4=True):
    out = [json.loads(x) for x in open(SETS[tag], encoding="utf-8")]
    for r in out:
        r["_tag"] = tag
    return [r for r in out if r.get("T4_qualified")] if t4 else out


def prov_of(r):
    return a17.Prov({r["name"]: (r["body"], r["final"], r["init"])})


def cells(r, arm, prov=None, size=None):
    prov = prov or prov_of(r)
    size = size or r["Q2_size"]
    return prov, [FR.Cell(prov, r["name"], i, size, label="%s-pilot-%s" % (r["_tag"], arm)) for i in range(4)]


def libs():
    return {"PRISTINE": FR.KLib(FR.pristine().entries), "L1": FR.KLib(a17.L1_entries())}
