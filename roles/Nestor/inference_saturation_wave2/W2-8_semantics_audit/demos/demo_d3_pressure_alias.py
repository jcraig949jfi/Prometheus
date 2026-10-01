"""D3 demonstration: on the pair tape, 7 of the 12 pressure levels are the same physics.

One zero-epoch Runner of the ffa6 cell (native pressure QUALITY_DIVERSITY) is deep-copied once per pressure level, so
every copy holds the same arena, organisms and world-RNG state. Each copy then executes the pressure-dependent parts of
one epoch as single methods (`_pressure_epoch`, `_pair_epoch`, `_migrate`, and the end-of-epoch cap/reap), and the
resulting arenas and population sizes are compared with NONE_IMPLICIT.
"""
from __future__ import annotations

import copy

import _paths
import run_dd
import run_ds
import world

a = run_ds.cells()[run_dd.CELLS["ffa6"]]
base = world.Runner(dict(a["cell"], atlas_axis="NONE"), 5, tier="S", max_epochs=1)
base.t["epochs"] = 0
base.run()
for o in base.orgs:                            # give half the population high competence so comp-reading code paths fire
    o.comp = o.held = 0.9 if o.oid % 2 else 0.1
LEVELS = ["NONE_IMPLICIT", "QUALITY_DIVERSITY", "EXEC_TIME_COST", "RESOURCE_GATED", "METABOLIC", "NOVELTY",
          "COMPETITION", "TAPE_COST", "PREDATION", "TASK_GATED_INTERACTION", "MINIMAL_CRITERION"]
res = {}
for lv in LEVELS:
    r = copy.deepcopy(base)
    r.cell["pressure"] = lv
    r._pressure_epoch()
    r._pair_epoch()
    r._migrate()
    alive_n = sum(o.alive for o in r.orgs)
    reaped = 0
    while alive_n > r.pop_cap:                 # step()'s cap loop, verbatim condition
        r._reap(alive_n - r.pop_cap)
        reaped += 1
        alive_n = sum(o.alive for o in r.orgs)
    res[lv] = (bytes(r.mem), alive_n, r.ct["deaths"], reaped)
ref = res["NONE_IMPLICIT"]
_paths.dump("d3_pressure_alias.json", {
    "pop_cap": base.pop_cap,
    "per_level": {lv: {"arena_equal_to_NONE_IMPLICIT": v[0] == ref[0], "alive_after": v[1], "deaths": v[2],
                       "cap_reaps": v[3]} for lv, v in res.items()},
    "place_call_sites": [ln.strip() for ln in (_paths.C9 / "world.py").read_text().splitlines()
                         if "self._place(" in ln],
})
