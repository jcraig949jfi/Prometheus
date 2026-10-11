"""BEL-RD-72 F5 instrument (prereg s14): a two-phase mutation schedule, OPT-IN (the kernel is unchanged).
PhasedMutWorld(LightHalvesWorld): the configured mutation_rate until tick `switch`, then cfg.mutation_rate = `phase2`
(Config.mut_rate reads it on every mutation call). Before the switch the world is byte-identical to the light census
world (test)."""
from __future__ import annotations

from light_halves import LightHalvesWorld


class PhasedMutWorld(LightHalvesWorld):
    def __init__(self, cfg, seed, switch: int, phase2: str, census_every: int = 100):
        super().__init__(cfg, seed, census_every=census_every)
        self.switch, self.phase2 = switch, phase2

    def step(self):
        if self.tick == self.switch:
            self.cfg.mutation_rate = self.phase2
        return super().step()
