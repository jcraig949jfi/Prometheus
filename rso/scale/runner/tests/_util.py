"""Shared fixtures for the runner tests (C-013-T022)."""
import os
import shutil
import tempfile

from rso.scale.runner import run as RUN

TOY = {"name": "rso.runner.toy", "version": 1}
AETHER = {"name": "rso.runner.aether_kernel", "version": 1}


def toy_params(**over):
    p = {"seed": 7, "ticks_per_epoch": 40, "trace_every": 10, "work_per_tick": 3}
    p.update(over)
    return p


def aether_params(**over):
    # B_balanced physics (Aether/observatory/aeth02_falsifiers.py:46-51), a 16x16 lattice for speed.
    p = {"h": 16, "w": 16, "regime": "random_soup", "energy_mode": "uniform", "rng_seed": 0xA37E01,
         "seed": 0x5C011701, "write_cost": 1, "maintenance_cost": 1, "replenish_numer": 536870912,
         "replenish_amount": 8, "mut_numer": 429496730, "ticks_per_epoch": 20, "trace_every": 5}
    p.update(over)
    return p


class TempRun:
    """A run directory that is removed afterwards."""

    def __init__(self, runtime=TOY, params=None, partitions=2, epochs=4, replay_every=10, name="t", retention=None):
        self.tmp = tempfile.mkdtemp(prefix="rso_runner_")
        self.run_dir = os.path.join(self.tmp, "run")
        params = params if params is not None else toy_params()
        parts = [{"partition_id": "p{}".format(i), "params": {"seed": 100 + i}} for i in range(partitions)]
        self.manifest = RUN.create_run(self.run_dir, name=name, runtime=runtime, params=params,
                                       partitions=parts, epochs=epochs, replay_every=replay_every,
                                       **({"retention": retention} if retention else {}))

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
