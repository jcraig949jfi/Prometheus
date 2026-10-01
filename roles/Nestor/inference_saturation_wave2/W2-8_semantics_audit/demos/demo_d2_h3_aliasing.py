"""D2 demonstration. Two parts.

(a) From the frozen C9 record (observatory/bundles_C9.tar.gz, read in memory, nothing extracted): in every H3 bundle,
    arms A (easy niche on) and B (easy niche off) have IDENTICAL trajectory fields; they differ only in competence
    readouts. A vs C (migration off) differ.
(b) Mechanism, with Runners and single methods only: A and B built from the first H3 bundle get the same RNG seed
    (easy_niche_disabled is a kwarg, not a cell factor, so cell_id and the RNG seed are equal); after placement and one
    `_pair_epoch()` + `_pressure_epoch()` + `_migrate()` their arenas are byte-identical; `_validate()` then gives
    different competences for the same bytes.
"""
from __future__ import annotations

import collections
import json
import tarfile

import _paths

import world

traj = ("births_endogenous", "replication_events", "ops", "slices", "p11_events", "migrations", "uniq_final",
        "entropy_final", "max_causal_replication_depth", "lineage_events", "copy_bytes", "deaths")
read = ("held_max_ever", "held_max_final", "n_cross_events", "crossed_ever", "comp_mean", "has_reservoir_certificate")
same_ab = same_ac = 0
diff_read = collections.Counter()
ncross = [0, 0, 0]
n = 0
with tarfile.open(_paths.C9 / "observatory" / "bundles_C9.tar.gz") as t:
    for m in t.getmembers():
        if not m.isfile():
            continue
        b = json.load(t.extractfile(m))
        if b["spec"].get("hypothesis_id") != "H3":
            continue
        n += 1
        R = b["results"]
        A, B, C = (R[k].get("summary", R[k]) for k in ("A_easy_plus_migration", "B_homogeneous_same_migration",
                                                         "C_easy_no_migration"))
        same_ab += all(A.get(f) == B.get(f) for f in traj)
        same_ac += all(A.get(f) == C.get(f) for f in traj)
        for f in read:
            diff_read[f] += A.get(f) != B.get(f)
        for i, x in enumerate((A, B, C)):
            ncross[i] += x.get("n_cross_events", 0)

man = json.loads((_paths.C9 / "MANIFEST_FROZEN.json").read_text())
h3 = next(b for b in man["bundles"] if b["hypothesis_id"] == "H3")
arms = {x["arm"]: x for x in h3["arms"]}


def build(arm):
    x = arms[arm]
    r = world.Runner(x["cell"], x["seed"], tier=x["tier"], max_epochs=1, **x.get("kwargs", {}))
    r.t["epochs"] = 0
    r.run()                                    # placement + the forced validation only (zero epochs)
    return r


rA, rB = build("A_easy_plus_migration"), build("B_homogeneous_same_migration")
same_init = bytes(rA.mem) == bytes(rB.mem)
for r in (rA, rB):
    r._pressure_epoch()
    r._pair_epoch()
    r._migrate()
same_after = bytes(rA.mem) == bytes(rB.mem) and rA.ct == rB.ct
rA._validate(force=True)
rB._validate(force=True)
comp_diff = sum(1 for x, y in zip(rA.orgs, rB.orgs) if (x.held, x.comp) != (y.held, y.comp))
_paths.dump("d2_h3_aliasing.json", {
    "h3_bundles": n, "A_eq_B_on_all_trajectory_fields": same_ab, "A_eq_C_on_all_trajectory_fields": same_ac,
    "A_vs_B_readout_fields_differing_in_n_bundles": dict(diff_read), "cross_events_total_A_B_C": ncross,
    "cells_pressure_environment": sorted({(x["cell"]["pressure"], x["cell"]["environment"])
                                          for b in man["bundles"] if b["hypothesis_id"] == "H3" for x in b["arms"]}),
    "runner_demo": {"cell_id_equal": world.G.cell_id(arms["A_easy_plus_migration"]["cell"]) ==
                                     world.G.cell_id(arms["B_homogeneous_same_migration"]["cell"]),
                    "arena_identical_after_placement": same_init,
                    "arena_and_counters_identical_after_one_epoch_of_physics": same_after,
                    "organisms_with_different_competence_for_identical_bytes": comp_diff,
                    "of": len(rA.orgs)},
})
