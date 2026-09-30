"""Shared setup for the functional-core forensics. Read-only on the campaign code.

Reproduces C-A3-INTERNALIZE / X-A3-SFLINEAGE exactly:
  world.z8 = run_dc.dense_z8(); a = run_ds.cells()[run_dd.CELLS[cell]];
  r = run_ds.runner_cls(world)(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
  COMPETENT  = run_de.competent(world, r, g, cache)        (zero-state, 4-seed stage 1, 20-seed stage 2, >= 0.5)
  STATE_FREE = all(run_fair.fair_assay(world, r, g, e, "SFL" + g.hex(), 20) >= 0.5 for e in ("R1", "R2"))
The runner is only constructed (never .run()), so no world/evolution run happens.
Run every script with `python -B` (PYTHONDONTWRITEBYTECODE) so no __pycache__ is written into the campaign dirs.
"""
from __future__ import annotations

import pathlib
import sys

sys.dont_write_bytecode = True
NESTOR = pathlib.Path(__file__).resolve().parents[2]
CAMP = NESTOR / "campaigns"
ARC3 = CAMP / "npe-arc3-2026-09-28"
W1 = CAMP / "npe-w1-donor-discovery-2026-09-26"
for p in (ARC3 / "x_a3_sflineage", ARC3 / "x_a3_fair", W1 / "x_dd_establish", W1 / "x_dd_dense_copy",
          W1 / "x_donor_discovery", CAMP / "c9x-explore-2026-09-24" / "x_donor_swap",
          CAMP / "z80atlas-verify-2026-09-22", NESTOR / "lib"):
    sys.path.insert(0, str(p))

import world  # noqa: E402
import z8 as z8_plain  # noqa: E402
import run_dc  # noqa: E402
import run_dd  # noqa: E402
import run_de  # noqa: E402
import run_ds  # noqa: E402
import run_fair  # noqa: E402

DENSE = run_dc.dense_z8()
_RUNNERS = {}


def set_vm(dense=True):
    world.z8 = DENSE if dense else z8_plain


def runner(cell, dense=True):
    set_vm(dense)
    key = (cell, dense)
    if key not in _RUNNERS:
        a = run_ds.cells()[run_dd.CELLS[cell]]
        _RUNNERS[key] = run_ds.runner_cls(world)(dict(a["cell"], atlas_axis="NONE"), 0, tier=a["tier"])
    return _RUNNERS[key]


def competent(cell, g, cache=None, dense=True):
    r = runner(cell, dense)
    return run_de.competent(world, r, bytes(g), {} if cache is None else cache)


def state_free(cell, g, dense=True):
    r = runner(cell, dense)
    return all(run_fair.fair_assay(world, r, bytes(g), e, "SFL" + bytes(g).hex(), 20) >= 0.5 for e in ("R1", "R2"))


def fair_rates(cell, g, dense=True):
    r = runner(cell, dense)
    return {e: run_fair.fair_assay(world, r, bytes(g), e, "SFL" + bytes(g).hex(), 20) for e in ("R1", "R2")}
