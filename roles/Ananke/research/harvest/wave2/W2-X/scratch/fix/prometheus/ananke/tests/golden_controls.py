"""Golden digests of the C1 control set, for the C1b switch additions.

Generated ONCE from the engine as frozen for PTE-C1 (code 362f2189b;
engine.py unchanged at generation time) and committed before any C1b
switch was added. test_c1b_switches.py recomputes them with the current
engine: every C1 control, and normal physics, must still give identical
per-world state digests and traces (PREREG_PTE_C1b s5). CPU only.

    python -m prometheus.ananke.tests.golden_controls   # regenerate (do not, after C1b edits)
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np

from prometheus.ananke.engine import Controls, World
from prometheus.ananke.tests.test_conformance import (dense_schedule, forced_emitter_inputs,
                                                      random_physics)

HERE = pathlib.Path(__file__).resolve().parent
GOLDEN = HERE / "golden_c1_controls.json"
SEEDS = list(range(200, 216))
B, T = 3, 20


def c1_controls():
    """Every C1 control constructor, in the form assays.control_battery uses."""
    return {
        "none": Controls(),
        "zero_comm": Controls(zero_comm=True),
        "shuffle_dest": Controls(shuffle_dest=True),
        "shuffle_time": Controls(shuffle_time=True),
        "randomize_payload": Controls(randomize_payload=True),
        "freeze_routing": Controls(freeze_routing=True),
        "no_adapt": Controls(no_adapt=True),
        "reset_state_at": Controls(reset_state_at=(3, 9, 15)),
        "reset_state_masked": None,          # built per physics in run_one (mask is [B, N])
        "drop_packets_at": Controls(drop_packets_at=tuple(range(4, 11))),
        "distractor_chan": Controls(distractor_chan=0),
    }


def run_one(seed: int, name: str, ctrl: Controls) -> dict:
    ph = random_physics(seed)
    if name == "reset_state_masked":
        m = np.zeros((B, ph.n_sites), dtype=bool)
        m[:, ::2] = True
        ctrl = Controls(reset_state_at=(5, 12), reset_state_mask=m)
    gen, ws, sense = forced_emitter_inputs(ph, B, T, seed)
    w = World(ph, gen, ws, device="cpu", ctrl=ctrl, schedule=dense_schedule(sense, B, ph.n_sites))
    w.run(T, graph=False)
    tr = hashlib.sha256(w.trace.cpu().numpy().astype(np.int64).tobytes()).hexdigest()[:16]
    return {"digests": w.digest(per_world=True), "trace": tr}


def compute() -> dict:
    return {f"{s}:{n}": run_one(s, n, c) for s in SEEDS for n, c in c1_controls().items()}


if __name__ == "__main__":
    if GOLDEN.exists():
        raise SystemExit(f"{GOLDEN} exists; golden digests are generated once")
    GOLDEN.write_text(json.dumps(compute(), indent=1, sort_keys=True) + "\n")
    print("wrote", GOLDEN)
