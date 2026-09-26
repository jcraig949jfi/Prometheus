"""verify_exact must equal verify_tape()["exact"] on every tape (it only adds an early exit)."""
from __future__ import annotations

import random

from prometheus.z80atlas import vm
from prometheus.z80atlas.tasks import Task, TASKS, verify_tape, verify_exact


def _tapes():
    rng = random.Random(20260926)
    rep = vm.replicator(64)
    out = [rep, vm.hybrid_relocated(rep, vm.witness_inc()), bytes(64)]
    for _ in range(150):
        out.append(bytes(rng.randrange(256) for _ in range(64)))
    base = vm.hybrid_relocated(rep, vm.witness_inc()) + bytes(64 - len(vm.hybrid_relocated(rep, vm.witness_inc())))
    for _ in range(150):                                            # mutants of a competent tape: many pass, many fail late
        m = bytearray(base); m[rng.randrange(64)] = rng.randrange(256); out.append(bytes(m))
    return out


def test_equivalent_on_all_tasks_gates_layouts():
    tapes = _tapes()
    for kind in TASKS:
        t = Task(kind)
        for gate in ("ABR", "FORCED"):
            for layout in ("SHARED", "SEPARATED"):
                for tp in tapes:
                    assert verify_exact(tp, 64, t, gate, 256, layout) == verify_tape(tp, 64, t, gate, 256, layout)["exact"]
