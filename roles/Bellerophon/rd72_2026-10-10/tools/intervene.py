"""BEL-RD-72 C2 / C3 instrument: causal interventions on a running light-census world (measurement + one intervention).

InterveneWorld(LightHalvesWorld) runs the SAME world as the light census (identical dynamics up to `at`; the intervention
RNG is separate from the world RNG) and at tick `at` applies ONE action, then continues:
  REMOVE_CLASS  kill every living organism whose tape is in `classes` (subset of LO / HI / BOTH, FUNC or not)  -> source
                removal (C2) or mechanism ablation (C3)
  REMOVE_SHAM   kill the same NUMBER of organisms drawn uniformly from those whose tape is NONE                 -> sham
  IMPLANT       replace `n_implant` random living NONE organisms by copies of `tapes` (hex, round-robin)       -> transplant
  IMPLANT_SHAM  the same replacement with copies of NONE FUNC tapes drawn from this world                      -> sham
  NONE          no action (the continuation control)
The record keeps the action, the number affected and the census before / after. The count for REMOVE_SHAM is the count
REMOVE_CLASS would have removed at the same tick in the same world (computed here, so the arms are matched)."""
from __future__ import annotations

import random

from light_halves import LightHalvesWorld

ACTIONS = ("NONE", "REMOVE_CLASS", "REMOVE_SHAM", "IMPLANT", "IMPLANT_SHAM")


class InterveneWorld(LightHalvesWorld):
    def __init__(self, cfg, seed, at: int, action: str, classes=("LO", "BOTH"), tapes=(), n_implant: int = 16,
                 census_every: int = 100, irng: int = 0):
        if action not in ACTIONS:
            raise ValueError(action)
        super().__init__(cfg, seed, census_every=census_every)
        self.at, self.action, self.classes = at, action, tuple(classes)
        self.tapes = [bytes.fromhex(h) for h in tapes]; self.n_implant = n_implant
        self.irng = random.Random(irng); self.intervention = None

    def step(self):
        if self.tick == self.at and self.intervention is None:
            self._intervene()
        return super().step()

    def _kill(self, i):
        o = self.cells[i]
        if getattr(self, "ledger", None) is not None:                 # v3: the held copy resource leaves through the ledger
            self.ledger.on_death(o)
        self.cells[i] = None

    def _intervene(self):
        alive = [i for i, o in enumerate(self.cells) if o is not None]
        cls = {i: self.halves(bytes(self.cells[i].tape)) for i in alive}
        target = [i for i in alive if cls[i] in self.classes]
        none = [i for i in alive if cls[i] == "NONE"]
        rec = {"tick": self.tick, "action": self.action, "alive_before": len(alive), "class_count": len(target), "affected": 0}
        if self.action == "REMOVE_CLASS":
            for i in target:
                self._kill(i)
            rec["affected"] = len(target)
        elif self.action == "REMOVE_SHAM":
            pick = self.irng.sample(none, min(len(target), len(none)))
            for i in pick:
                self._kill(i)
            rec["affected"] = len(pick)
        elif self.action in ("IMPLANT", "IMPLANT_SHAM"):
            src = self.tapes
            if self.action == "IMPLANT_SHAM":
                nf = sorted({bytes(self.cells[i].tape) for i in none if self.func(bytes(self.cells[i].tape))})
                src = [nf[self.irng.randrange(len(nf))] for _ in range(max(1, len(self.tapes)))] if nf else []
            pick = self.irng.sample(none, min(self.n_implant, len(none))) if src else []
            for k, i in enumerate(pick):
                t = bytearray(self.L); s = src[k % len(src)]; t[:len(s)] = s[:self.L]
                self._kill(i)
                self._spawn(i, t, None, "implant")
            rec["affected"] = len(pick)
        self.intervention = rec
