"""BEL-RD-72 C1/E1 instrument: accumulation within a composite task (measurement only).

HalvesWorld(CompWorld): for a COMPOSITE task whose input space splits into two halves solved by different sub-mechanisms
(COND_ONE: x < 128 -> x (ECHO-like), x >= 128 -> x + 1 (INC-like); COND_MULTI: x < 128 -> x, x >= 128 -> (x ^ 0x55) + 3),
every `census_every` ticks it classifies each distinct living tape (cached) on a fixed panel (8 inputs per half) as
LO (all low-half inputs right), HI (all high-half right), BOTH, or NONE, and whether it is FUNC; counts are recorded per
census (the trajectory of partial and full capability). For the FIRST tape that is BOTH and FUNC (a full composite
replicator) it records the competence-critical bytes with the ORIGIN TICK of each (heredity tags): TEMPORAL DEPTH =
max - min origin tick among critical bytes, and EPOCHS = number of origin ticks separated by > `epoch_gap` ticks.
A composite whose critical bytes come from several well-separated epochs, with partial capability alive in between,
was built cumulatively; one whose bytes all arose together was assembled at once."""
from __future__ import annotations

from collections import Counter

from comp import CompWorld
from prometheus.z80atlas import vm

LO_PANEL = (0, 9, 37, 64, 90, 101, 120, 127)
HI_PANEL = (128, 140, 166, 192, 200, 222, 240, 255)


def _expected(task_kind, x):
    if task_kind == "COND_ONE":
        return x if x < 128 else (x + 1) & 0xFF
    if task_kind == "COND_MULTI":
        return x if x < 128 else ((x ^ 0x55) + 3) & 0xFF
    raise ValueError(task_kind)


class HalvesWorld(CompWorld):
    def __init__(self, cfg, seed, census_every: int = 250, epoch_gap: int = 200, rows: bool = False):
        self._hw_ready = False
        super().__init__(cfg, seed, rows=rows)
        self.census_every = census_every; self.epoch_gap = epoch_gap
        self._hcache = {}
        self.census = []
        self.first_both = None
        self._hw_ready = True

    def halves(self, tape: bytes) -> str:
        r = self._hcache.get(tape)
        if r is not None:
            return r
        L = self.L; cfg = self.cfg
        def ok(x):
            mem = bytearray(256); mem[:L] = tape
            mem[vm.IN_BASE] = x
            tr = vm.execute(mem, L, 0, cfg.budget, [x], allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1", **cfg.chem)
            return bool(tr.outputs) and tr.outputs[0] == _expected(cfg.task, x)
        lo = all(ok(x) for x in LO_PANEL); hi = all(ok(x) for x in HI_PANEL)
        r = "BOTH" if lo and hi else ("LO" if lo else ("HI" if hi else "NONE"))
        if len(self._hcache) < 200000:
            self._hcache[tape] = r
        return r

    def step(self):
        rec = super().step()
        if self._hw_ready and (self.tick % self.census_every == 0):
            c = Counter(); cf = Counter()
            for o in self.cells:
                if o is None:
                    continue
                t = bytes(o.tape); h = self.halves(t); c[h] += 1
                if self.func(t):
                    cf[h] += 1
            self.census.append({"tick": self.tick, "alive": sum(c.values()), "halves": dict(c), "halves_func": dict(cf)})
            if self.first_both is None and cf.get("BOTH"):                 # arose in place (no birth): take a living carrier
                o = next(o for o in self.cells if o is not None and self.halves(bytes(o.tape)) == "BOTH" and self.func(bytes(o.tape)))
                t = bytes(o.tape); self._record_both(t, self._synced(o.id, t), via="census")
        return rec

    def _record_both(self, t, tags, via):
        a = self.comp_anatomy(t, tags)
        ticks = sorted({o[2] if o[0] != "F" else 0 for o in a["ccrit_origins"]})
        epochs = 1 + sum(1 for x, y in zip(ticks, ticks[1:]) if y - x > self.epoch_gap) if ticks else 0
        self.first_both = {"tick": self.tick, "via": via, "anatomy": a, "origin_ticks": ticks,
                           "temporal_depth": (ticks[-1] - ticks[0]) if ticks else None, "epochs": epochs,
                           "census_before": self.census[-3:]}

    def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
        super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
        if self._hw_ready and self.first_both is None:
            t = bytes(child)
            if self.halves(t) == "BOTH" and self.func(t):
                c = self.cells[j]
                self._record_both(t, self.tags[c.id], via="birth")

    def halves_summary(self) -> dict:
        return {"census": self.census, "first_both": self.first_both}
