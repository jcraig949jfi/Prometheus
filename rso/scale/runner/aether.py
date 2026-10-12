"""First client: the Aether AETH-01 kernel, used READ ONLY from the RSO lane (C-013-T022).

Nothing in Aether/ is edited or copied. The kernel (Aether/test/reference/gpu_aeth01.py:111 gpu_step), the
initial-state recipe (Aether/observatory/aeth01_run.py:47 build_initial) and the fields digest
(Aether/observatory/aeth01_observatory.py:154 state_digest) are imported from the committed tree. The step loop
is the one Aether's own driver runs (aeth01_run.py:136-142: tick = tick0 + step), so a checkpointed run steps
exactly what run_world steps; tests/test_engine.py checks that against run_world itself.

State = the five H x W uint8 fields + the tick. The kernel is counter-based (splitmix of seed, tick, position,
field; gpu_aeth01.py:83-107), so there is no RNG state to save (CHECKPOINT_REPLAY_SURVEY.md s1 row Aether).
Checkpoint bytes: b"RSOAETH1" + u64be tick + u32be H + u32be W + the five fields, C order.
"""
import hashlib
import importlib.util
import os
import struct
import sys

import numpy as np

from moonshot.epoch import canonical as C
from rso.scale.runner import engine as E

KERNEL = "Aether/test/reference/gpu_aeth01.py"
DRIVER = "Aether/observatory/aeth01_run.py"
OBSERVATORY = "Aether/observatory/aeth01_observatory.py"
PHYSICS = ("seed", "write_cost", "maintenance_cost", "replenish_numer", "replenish_amount", "mut_numer")

_MODULES = None


def aether_modules():
    """(aeth01_run, gpu_aeth01), imported read only. The kernel is loaded by file path under a private name so
    Aether's `test` package never shadows the standard library's; the driver needs Aether/ on sys.path for its
    own `from observatory import ...` (aeth01_run.py:32), which is added for the import and removed after."""
    global _MODULES
    if _MODULES is None:
        spec = importlib.util.spec_from_file_location("rso_runner_aether_gpu_aeth01", os.path.join(E.REPO, KERNEL))
        kernel = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kernel)
        aether_dir = os.path.join(E.REPO, "Aether")
        sys.path.insert(0, aether_dir)
        try:
            import observatory.aeth01_run as driver
        finally:
            sys.path.remove(aether_dir)
        _MODULES = (driver, kernel)
    return _MODULES


class AetherState:
    __slots__ = ("params", "tick", "fields")

    def __init__(self, params, tick, fields):
        self.params, self.tick, self.fields = params, tick, fields


def fields_digest(state):
    """Aether's own state_digest of the five fields (aeth01_observatory.py:154-167; 32 hex chars)."""
    driver, _ = aether_modules()
    return driver.obs.state_digest(state.fields)


class AetherKernelEngine(E.Engine):
    runtime = {"name": "rso.runner.aether_kernel", "version": 1}
    MAGIC = b"RSOAETH1"

    def init(self, params):
        driver, _ = aether_modules()
        fields, _recipe = driver.build_initial(params["regime"], params["h"], params["w"], params["rng_seed"],
                                               energy_mode=params["energy_mode"])
        return AetherState(params, 0, [np.ascontiguousarray(f, dtype=np.uint8) for f in fields])

    def step(self, state, n):
        _, kernel = aether_modules()
        p = state.params
        fields, tick = list(state.fields), state.tick
        for _ in range(n):
            out = kernel.gpu_step(p["h"], p["w"], p["seed"], tick, p["write_cost"], p["maintenance_cost"],
                                  p["replenish_numer"], p["replenish_amount"], p["mut_numer"], *fields)
            fields = list(out[:5])
            tick += 1
        return AetherState(p, tick, fields)

    def save_state(self, state):
        h, w = state.params["h"], state.params["w"]
        body = b"".join(np.ascontiguousarray(f, dtype=np.uint8).tobytes() for f in state.fields)
        if len(body) != 5 * h * w:
            raise ValueError("fields do not match the declared lattice")
        return self.MAGIC + struct.pack(">QII", state.tick, h, w) + body

    def load_state(self, params, data):
        h, w = params["h"], params["w"]
        if not isinstance(data, (bytes, bytearray)) or len(data) != 24 + 5 * h * w or data[:8] != self.MAGIC:
            raise ValueError("not a rso.runner.aether_kernel v1 checkpoint for a {}x{} lattice".format(h, w))
        tick, hh, ww = struct.unpack(">QII", data[8:24])
        if (hh, ww) != (h, w):
            raise ValueError("checkpoint lattice {}x{} != params {}x{}".format(hh, ww, h, w))
        n = h * w
        fields = [np.frombuffer(data, dtype=np.uint8, count=n, offset=24 + i * n).reshape(h, w).copy()
                  for i in range(5)]
        return AetherState(params, tick, fields)

    def digest(self, state):
        body = hashlib.sha256()
        for f in state.fields:
            body.update(np.ascontiguousarray(f, dtype=np.uint8).tobytes())
        return C.tagged_digest("rso.runner.aether.state.v1", {"tick": state.tick, "fields_sha256": body.hexdigest()})

    def probe(self):
        p = E.base_probe(E.RUNNER_FILES + ("rso/scale/runner/aether.py", KERNEL, DRIVER, OBSERVATORY))
        p["numpy"] = np.__version__
        return p
