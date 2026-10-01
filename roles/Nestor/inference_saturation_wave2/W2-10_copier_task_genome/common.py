"""W2-10 shared static setup. Reuses forensics/fsetup.py (runner constructed, never .run()).
STATIC ONLY: single-genome VM calls; no world or evolution runs."""
from __future__ import annotations
import pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
NESTOR = HERE.parents[1]
sys.path.insert(0, str(NESTOR / "inference_harvest_2026-09-30" / "forensics"))
import fsetup  # noqa: E402
from fsetup import world, run_dd, run_de, run_ds, run_fair, DENSE  # noqa: E402
import tasks  # noqa: E402
import z8 as z8_plain  # noqa: E402

CELL = "ffa6"


def runner():
    return fsetup.runner(CELL, dense=True)


def cell_spec():
    r = runner()
    return r.spec
