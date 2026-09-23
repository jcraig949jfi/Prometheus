"""AETH-01 first light: run several worlds under observation on the GPU.

Imports the FROZEN kernel and never modifies it. Runs the worlds in the
order given, sequentially, writing one JSON line per observatory sample
to the log as it goes -- so if the run is cut short for any reason
(budget ceiling, stall, terminated pod), every world that finished is
already fully recorded rather than lost with the process.

This file measures and records. It applies no HABITABILITY.md label,
runs no claim-ladder detector, and decides nothing.
"""

import json
import os
import sys
import time
import zlib
from base64 import b64encode

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("AETH01_SRC", _HERE))

from aeth01_gpu_kernel import gpu_step, BACKEND, np as xp   # frozen kernel
from observatory import aeth01_run as runner                # noqa: E402
from observatory import aeth01_observatory as obs           # noqa: E402

LOG = os.environ.get("AETH01_FL_LOG", "/app/bench.log")
SIZE = int(os.environ.get("AETH01_FL_SIZE", "4096"))
TICKS = int(os.environ.get("AETH01_FL_TICKS", "5000"))
SAMPLE_EVERY = int(os.environ.get("AETH01_FL_SAMPLE_EVERY", "10"))
DEEP_EVERY = int(os.environ.get("AETH01_FL_DEEP_EVERY", "250"))
MAP_EVERY = int(os.environ.get("AETH01_FL_MAP_EVERY", "500"))
MAP_BLOCKS = int(os.environ.get("AETH01_FL_MAP_BLOCKS", "64"))
# Hard wall-clock stop for the WHOLE run, enforced between worlds and
# between samples. The controller has its own ceiling; this is the
# pod-side one, so a controller that dies cannot make the pod run
# forever doing useful-looking work.
BUDGET_S = float(os.environ.get("AETH01_FL_BUDGET_S", "16200"))
MAX_TICK_S = float(os.environ.get("AETH01_FL_MAX_TICK_S", "60"))


def emit(record):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write("AETH01_FL " + json.dumps(record) + "\n")
        fh.flush()


def round_floats(obj, digits=6):
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def pack_map(array):
    """Quantize a coarse map to uint8 and zlib+base64 it.

    Keeps spatial organization in the record at a few KB per sample
    instead of 84 MB, and carries its own min/max so the quantization
    is invertible rather than lossy in an unrecorded way.
    """
    if array is None:
        return None
    lo, hi = float(array.min()), float(array.max())
    if hi > lo:
        q = ((array - lo) / (hi - lo) * 255.0).astype(np.uint8)
    else:
        q = np.zeros(array.shape, dtype=np.uint8)
    return {"lo": lo, "hi": hi, "shape": list(array.shape),
            "b64": b64encode(zlib.compress(q.tobytes(), 6)).decode("ascii")}


def run_one(index, spec, deadline):
    fields, recipe = runner.build_initial(
        spec["init_regime"], SIZE, SIZE, spec["rng_seed"],
        write_density=spec.get("write_density"),
        energy_mode=spec.get("energy_mode", runner.ENERGY_UNIFORM))
    if not runner.verify_recipe(recipe):
        emit({"kind": "world_abort", "world": index,
              "reason": "recipe does not rebuild its own lattice"})
        return False

    params = dict(spec["params"])
    params.update(h=SIZE, w=SIZE)
    emit({"kind": "world_start", "world": index, "name": spec["name"],
          "size": SIZE, "ticks": TICKS, "params": params,
          "recipe": round_floats(recipe), "backend": BACKEND,
          "started_at": time.time()})

    device = [xp.asarray(f) for f in fields]
    prev = [f.copy() for f in device]
    write_cost = params["write_cost"]
    t_world = time.time()
    stopped = None

    for step in range(TICKS):
        t0 = time.time()
        device = list(gpu_step(SIZE, SIZE, params["seed"], step, write_cost,
                               params["maintenance_cost"],
                               params["replenish_numer"],
                               params["replenish_amount"],
                               params["mut_numer"], *device)[:5])
        dt = time.time() - t0
        if dt > MAX_TICK_S:
            stopped = "tick_over_%gs" % MAX_TICK_S
            break

        last = step == TICKS - 1
        if not (step % SAMPLE_EVERY == 0 or last):
            continue

        want_deep = (step % DEEP_EVERY == 0) or last
        want_maps = (step % MAP_EVERY == 0) or last
        row = obs.sample(xp, device, write_cost,
                         want_compression=want_deep, want_maps=want_maps,
                         map_blocks=MAP_BLOCKS)
        rate, per_field = obs.change_rate(xp, prev, device)
        row["change_rate"] = rate
        row["change_rate_by_field"] = per_field
        maps = row.pop("_maps", None)
        record = {"kind": "sample", "world": index, "tick": step + 1}
        record.update(round_floats(row))
        if want_maps and maps:
            record["maps"] = {k: pack_map(v) for k, v in maps.items()}
        emit(record)
        prev = [f.copy() for f in device]

        if time.time() > deadline:
            stopped = "budget_deadline"
            break

    host = [np.asarray(getattr(f, "get", lambda: f)()) for f in device]
    emit({"kind": "world_end", "world": index, "name": spec["name"],
          "ticks_completed": step + 1, "stopped": stopped,
          "wall_seconds": round(time.time() - t_world, 1),
          "final_state_digest": obs.state_digest(host)})
    del device, prev, host
    free_pool = getattr(getattr(xp, "get_default_memory_pool", lambda: None)(),
                        "free_all_blocks", None)
    if free_pool:
        free_pool()
    return stopped is None


def main():
    worlds = json.loads(os.environ["AETH01_FL_WORLDS"])
    deadline = time.time() + BUDGET_S
    emit({"kind": "run_start", "worlds": len(worlds), "size": SIZE,
          "ticks": TICKS, "backend": BACKEND, "budget_s": BUDGET_S,
          "sample_every": SAMPLE_EVERY, "deep_every": DEEP_EVERY,
          "map_every": MAP_EVERY})
    completed = 0
    for i, spec in enumerate(worlds):
        if time.time() > deadline:
            emit({"kind": "run_truncated", "after_worlds": completed,
                  "reason": "budget_deadline"})
            break
        if run_one(i, spec, deadline):
            completed += 1
    emit({"kind": "run_end", "worlds_completed": completed,
          "worlds_requested": len(worlds)})
    print("AETH01_FL_COMPLETE completed=%d/%d" % (completed, len(worlds)),
          flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write("AETH01_FL_COMPLETE completed=%d/%d\n" % (completed, len(worlds)))
        fh.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
