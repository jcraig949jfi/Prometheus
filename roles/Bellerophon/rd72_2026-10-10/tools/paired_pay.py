"""BEL-RD-72 F2 instrument (prereg s11): PAIRED-HALVES payment, an OPT-IN payment rule for composite tasks (COND_ONE /
COND_MULTI). Nothing in the kernel changes; the rule lives in this subclass.

Kernel rule (coupling.py, world.py): each interaction draws ONE uniform input; a correct answer is paid. A half-solver
(ECHO / INC) is therefore paid on ~50% of interactions, the composite on 100%.
Paired rule: when an interaction is correct on its drawn input x, the organism's PRE-interaction tape is executed once more
(fresh memory, no partner, the light-census semantics) on one input y from the OTHER half (y < 128 if x >= 128, else
y >= 128), y drawn from a SEPARATE rng (seed-derived; the world rng is never touched). The ledger is told `correct` only
if both are right. A half-solver earns NO bonus; the composite earns the same as under the kernel rule. Base income,
costs, the ledger identity and every other physics are unchanged. Counters: pp_correct (kernel-correct events),
pp_denied (of those, refused by the second check)."""
from __future__ import annotations

import random

from light_halves import LightHalvesWorld, _expected
from prometheus.z80atlas import vm


class PairedPayWorld(LightHalvesWorld):
    def __init__(self, cfg, seed, census_every: int = 100):
        super().__init__(cfg, seed, census_every=census_every)
        self.pp_rng = random.Random(seed ^ 0x5A5A_0F0F)
        self.pp = {"pp_correct": 0, "pp_denied": 0}
        if self.ledger is not None:
            inner = self.ledger.after_interaction

            def wrapped(world, o, task, inputs, outputs, fos, fis, correct):
                if correct:
                    self.pp["pp_correct"] += 1
                    x = inputs[0]
                    y = self.pp_rng.randrange(128) if x >= 128 else 128 + self.pp_rng.randrange(128)
                    if not self._ok(self._pre_tape, y):
                        correct = False; self.pp["pp_denied"] += 1
                return inner(world, o, task, inputs, outputs, fos, fis, correct)
            self.ledger.after_interaction = wrapped

    def _ok(self, tape: bytes, x: int) -> bool:
        L = self.L; cfg = self.cfg
        mem = bytearray(256); mem[:L] = tape[:L]; mem[vm.IN_BASE] = x
        tr = vm.execute(mem, L, 0, cfg.budget, [x], allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1", **cfg.chem)
        return bool(tr.outputs) and tr.outputs[0] == _expected(cfg.task, x)
