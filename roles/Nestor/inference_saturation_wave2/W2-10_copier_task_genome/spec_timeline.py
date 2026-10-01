"""W2-10: which task does the ffa6 world actually score? Static: source inspection of Runner._env_epoch plus ONE
_env_epoch() call at epoch 0 on a constructed, never-run runner per seed (that call only draws env_pop).
Outputs spec_timeline.json."""
from __future__ import annotations

import collections
import inspect
import json

from common import HERE, CELL, world, run_dd, run_ds, runner

src = inspect.getsource(world.Runner._env_epoch)
choice_lists = [l.strip() for l in src.splitlines() if "rng.choice([" in l]
a = run_ds.cells()[run_dd.CELLS[CELL]]
dist = collections.Counter()
fr_niches = collections.Counter()
for s in range(200):
    r = run_ds.runner_cls(world)(dict(a["cell"], atlas_axis="NONE"), 31_000_000 + s, tier=a["tier"])
    r._env_epoch()                      # epoch 0: initialises env_pop only
    for e in r.env_pop:
        dist[(e["transform"], e["read_order"])] += 1
    fr_niches[sum(e["read_order"] == "FORCED_READ" for e in r.env_pop)] += 1
r = runner()
out = {"cell_spec": r.spec.as_dict(), "cell_cue_index_used_by_run_xtg": r.spec.cue_index(),
       "env_epoch_transform_choice_lines": choice_lists,
       "ADD37_in_any_choice_list": any("ADD37" in l for l in choice_lists),
       "epoch0_env_pop_distribution_200_seeds_x4_niches": {"%s/%s" % k: v for k, v in sorted(dist.items())},
       "n_FORCED_READ_niches_at_epoch0": dict(sorted(fr_niches.items())),
       "val_cache_key": "blake2b(genome) only (world._competence) - not keyed on spec/niche; cleared only when env_pop updates (epoch % 25 == 0)",
       "note": "run() validates once with env_pop None (cell spec ADD37/FORCED_READ); step() at epoch 0 creates env_pop, "
               "but the genome-keyed cache returns those cell-spec results until the first clear at epoch 25; "
               "from the epoch-30 validation on, every organism is scored under its niche's COEVO spec, never ADD37."}
(HERE / "spec_timeline.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
