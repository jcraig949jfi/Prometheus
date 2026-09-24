"""Verify a first-light run's replay chain is executable, not documentary.

For every world in a first-light JSONL log: rebuild the initial lattice
FROM THE COMMITTED RECIPE ALONE, advance one tick on this host's NumPy
backend, and compare the resulting digest against the digest the GPU
recorded under CuPy.

A recipe that cannot regenerate its own lattice is a description, not
provenance (EXPERIMENTS.md item 5). A digest that does not reproduce
across backends means the run is not replayable, whatever the receipt
says.

    python Aether/AETH-01/instruments/replay_spotcheck.py <repo-root> <log.jsonl>

Exit 0 = REPLAY_CHAIN_VERIFIED. Exit 1 = broken, and the offending
world is named.

Cost note: this checks tick 1 only. Advancing a 4096^2 world to the next
committed digest (tick 251) costs hours of CPU, so long-run cross-backend
agreement is NOT what this instrument establishes.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1]).resolve()
LOG = Path(sys.argv[2])
sys.path.insert(0, str(ROOT / "Aether"))
sys.path.insert(0, str(ROOT / "Aether" / "test"))

from observatory import aeth01_run as runner         # noqa: E402
from observatory import aeth01_observatory as obs    # noqa: E402
from reference.gpu_aeth01 import gpu_step            # noqa: E402


def load(path):
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("AETH01_FL {"):
                rows.append(json.loads(line[len("AETH01_FL "):]))
    return rows


def main():
    rows = load(LOG)
    starts = {r["world"]: r for r in rows if r["kind"] == "world_start"}
    first = {}
    for r in rows:
        if r["kind"] == "sample" and r["world"] not in first and "state_digest" in r:
            first[r["world"]] = r

    print("%-26s %-14s %-34s %s" % ("world", "recipe", "cpu tick-1 digest", "verdict"))
    ok_all = True
    for i in sorted(starts):
        start = starts[i]
        recipe, params = start["recipe"], start["params"]
        t0 = time.time()
        rebuilt = runner.verify_recipe(recipe)
        fields, _ = runner.build_initial(
            recipe["regime"], recipe["h"], recipe["w"], recipe["rng_seed"],
            write_density=recipe["write_density_requested"],
            energy_mode=recipe["energy_mode"])
        out = gpu_step(params["h"], params["w"], params["seed"], 0,
                       params["write_cost"], params["maintenance_cost"],
                       params["replenish_numer"], params["replenish_amount"],
                       params["mut_numer"], *fields)[:5]
        digest = obs.state_digest(list(out))
        expected = first[i]["state_digest"]
        good = rebuilt and digest == expected
        ok_all &= good
        print("%-26s %-14s %-34s %s (%.0fs)"
              % (start["name"], "OK" if rebuilt else "REBUILD FAIL", digest,
                 "MATCH" if digest == expected else "DIFFER -> " + expected,
                 time.time() - t0))

    print()
    print("REPLAY_CHAIN_VERIFIED" if ok_all else "REPLAY_CHAIN_BROKEN")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
