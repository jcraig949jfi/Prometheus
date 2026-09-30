"""W2 learnability frontier -- shared helpers (read-only use of the frozen engine)."""
import json, os, sys, time
from pathlib import Path
os.environ.setdefault("A17_FASTEVAL", "1")
os.environ.setdefault("A18_TAG", "A19")
os.environ.setdefault("A18_FASTCOST", "1")
ROOT = Path(__file__).resolve().parents[3]          # roles/Aphrodite
ENG = ROOT / "engine"
sys.path.insert(0, str(ENG)); sys.path.insert(0, str(ENG / "accel"))
import a18, a17                                      # noqa
import a18_c1 as C                                   # noqa
from a18 import G, FR                                # noqa
HERE = Path(__file__).resolve().parent
ROWS = ENG / "A19_C2" / "A18_FOUNDRY_ROWS_2026-09-28.jsonl"
N_COV = len(G.H1_SPACE) * len(G.H2_SPACE) * len(G.FINAL_SPACE)   # 151,920


def rows(source=None, t4=True):
    out = [json.loads(l) for l in open(ROWS, encoding="utf-8")]
    if source:
        out = [r for r in out if r["source"].startswith(source)]
    if t4:
        out = [r for r in out if r.get("T4_qualified")]
    return out


def cells(r, arm="PRISTINE"):
    prov = a17.Prov({r["name"]: (r["body"], r["final"], r["init"])})
    return prov, [FR.Cell(prov, r["name"], i, r["Q2_size"], label="%s-pilot-%s" % (a18.TAG, arm)) for i in range(4)]
