"""AETH-02 pod-side runner: worlds under causal-graph observation.

Imports the FROZEN kernel and never modifies it. Attaches the
write-only `observer` side-channel, measures the functional graph with
`observatory.aeth01_graph`, and records the engineering telemetry First
Light lacked: GPU memory over lifetime, tick latency over lifetime, and
artifact growth.

It also records COST as a first-class output, not a footnote: seconds
per tick and dollars per thousand world-ticks at each lattice size, so
the next round can be budgeted from measurement instead of a quote.

Emits one JSON line per sample as it goes, so a run cut short at any
point keeps everything it had already measured.

PHASES are read from the environment, so the same file serves the cheap
economics calibration and the long trajectory:

    AETH02_PHASES  JSON list of {name, size, ticks, params, ...}

Nothing here applies a HABITABILITY.md label, runs a claim-ladder
detector, or adds reward of any kind.
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

from aeth01_gpu_kernel import gpu_step, BACKEND, np as xp      # frozen kernel
from observatory import aeth01_run as runner                   # noqa: E402
from observatory import aeth01_observatory as obs              # noqa: E402
from observatory import aeth01_graph as graph                  # noqa: E402

LOG = os.environ.get("AETH02_LOG", "/app/bench.log")
SAMPLE_EVERY = int(os.environ.get("AETH02_SAMPLE_EVERY", "10"))
GRAPH_EVERY = int(os.environ.get("AETH02_GRAPH_EVERY", "100"))
DEEP_EVERY = int(os.environ.get("AETH02_DEEP_EVERY", "1000"))
WINDOW_EVERY = int(os.environ.get("AETH02_WINDOW_EVERY", "2000"))
WINDOW_SIZE = int(os.environ.get("AETH02_WINDOW_SIZE", "256"))
WINDOW_EDGE_CAP = int(os.environ.get("AETH02_WINDOW_EDGE_CAP", "20000"))
BUDGET_S = float(os.environ.get("AETH02_BUDGET_S", "16200"))
HOURLY = float(os.environ.get("AETH02_HOURLY", "0.49"))
MAX_TICK_S = float(os.environ.get("AETH02_MAX_TICK_S", "60"))


def emit(record):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write("AETH02 " + json.dumps(record) + "\n")
        fh.flush()


def rnd(obj, digits=6):
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: rnd(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [rnd(v, digits) for v in obj]
    return obj


def pack_edges(edges, cap):
    """Compact, compressed edge payload.

    As JSON dicts an edge is ~110 bytes, so a 256x256 window sampled
    through a long run would overrun the 8 MB artifact channel -- and the
    server truncates the FIRST 8 MB, meaning the loss would be the most
    recent and most valuable data. Packed as int32 rows of
    (tr, tc, sr, sc, field, slot, contenders) then zlib+base64, the same
    content costs roughly a tenth as much and stays exactly recoverable.
    """
    kept = edges[:cap]
    if not kept:
        return {"count": 0, "kept": 0, "cols":
                ["tr", "tc", "sr", "sc", "field", "slot", "contenders"],
                "b64": ""}
    rows = np.array([[e["target"][0], e["target"][1], e["source"][0],
                      e["source"][1], e["field"], e["slot"], e["contenders"]]
                     for e in kept], dtype=np.int32)
    return {"count": len(edges), "kept": len(kept),
            "cols": ["tr", "tc", "sr", "sc", "field", "slot", "contenders"],
            "b64": b64encode(zlib.compress(rows.tobytes(), 6)).decode("ascii")}


def gpu_memory():
    """Device and pool memory. The telemetry First Light did not record."""
    out = {}
    try:
        free, total = xp.cuda.runtime.memGetInfo()
        out["device_free_mib"] = round(free / 1048576.0, 1)
        out["device_total_mib"] = round(total / 1048576.0, 1)
        out["device_used_mib"] = round((total - free) / 1048576.0, 1)
    except Exception:
        pass
    try:
        pool = xp.get_default_memory_pool()
        out["pool_used_mib"] = round(pool.used_bytes() / 1048576.0, 1)
        out["pool_total_mib"] = round(pool.total_bytes() / 1048576.0, 1)
    except Exception:
        pass
    return out


def run_phase(index, spec, deadline, t_run0):
    size = int(spec["size"])
    ticks = int(spec["ticks"])
    params = dict(spec["params"])
    params.update(h=size, w=size)

    fields, recipe = runner.build_initial(
        spec.get("init_regime", "sparse_soup"), size, size,
        int(spec["rng_seed"]), write_density=spec.get("write_density"),
        energy_mode=spec.get("energy_mode", "uniform"))
    if not runner.verify_recipe(recipe):
        emit({"kind": "phase_abort", "phase": index,
              "reason": "recipe does not rebuild its own lattice"})
        return False

    # Preregistered windows. WINDOW_A has no selection freedom; WINDOW_B
    # is derived from this world's own physics seed, so both were fixed
    # before any data existed.
    from aeth01_gpu_kernel import mix64_scalar
    win_a = (0, 0)
    win_b = graph.window_origin(mix64_scalar, params["seed"], size, size,
                                WINDOW_SIZE)

    emit({"kind": "phase_start", "phase": index, "name": spec["name"],
          "size": size, "ticks": ticks, "params": params,
          "recipe": rnd(recipe), "backend": BACKEND,
          "window_a": list(win_a), "window_b": list(win_b),
          "window_size": WINDOW_SIZE, "gpu_memory": gpu_memory()})

    device = [xp.asarray(f) for f in fields]
    prev = [f.copy() for f in device]
    state = graph.new_runlengths(xp, size, size)
    write_cost = params["write_cost"]
    latencies = []
    t_phase = time.time()
    stopped = None
    partial_function_max = 0

    for step in range(ticks):
        observer = []
        t0 = time.time()
        device = list(gpu_step(size, size, params["seed"], step, write_cost,
                               params["maintenance_cost"],
                               params["replenish_numer"],
                               params["replenish_amount"],
                               params["mut_numer"], *device,
                               observer=observer)[:5])
        dt = time.time() - t0
        latencies.append(dt)
        if dt > MAX_TICK_S:
            stopped = "tick_over_%gs" % MAX_TICK_S
            break

        persistence = graph.update_runlengths(xp, state, observer)
        last = step == ticks - 1

        if step % SAMPLE_EVERY == 0 or last:
            row = {"kind": "sample", "phase": index, "tick": step + 1}
            row.update(rnd(obs.sample(xp, device, write_cost)))
            rate, per_field = obs.change_rate(xp, prev, device)
            row["change_rate"] = round(rate, 6)
            row["change_rate_by_field"] = rnd(per_field)
            row.update(rnd(graph.edge_aggregates(xp, observer, prev, device)))
            row["persistence"] = rnd(persistence)
            window = latencies[-SAMPLE_EVERY:]
            row["tick_s_median"] = round(float(np.median(window)), 6)
            row["tick_s_max"] = round(float(np.max(window)), 6)
            elapsed = time.time() - t_run0
            row["elapsed_s"] = round(elapsed, 1)
            row["spend_usd"] = round(elapsed / 3600.0 * HOURLY, 5)
            if step % (SAMPLE_EVERY * 10) == 0 or last:
                row["gpu_memory"] = gpu_memory()
            if step % GRAPH_EVERY == 0 or last:
                nxt = graph.realized_map(xp, observer, size, size)
                cycles, doublings = graph.cycle_node_count(xp, nxt)
                row["cycle_nodes"] = cycles
                row["cycle_doublings"] = doublings
                row["mapped_nodes"] = int((nxt >= 0).sum())
                pf = graph.assert_partial_function(xp, observer, size, size)
                partial_function_max = max(partial_function_max, pf)
                row["partial_function_max_outdegree"] = pf
                del nxt
            if step % DEEP_EVERY == 0 or last:
                host = [np.asarray(getattr(f, "get", lambda: f)())
                        for f in device]
                row["state_digest"] = obs.state_digest(host)
                row["compression_ratio"] = round(obs.compression_ratio(host), 6)
                del host
            emit(row)
            prev = [f.copy() for f in device]

        if (step % WINDOW_EVERY == 0 or last) and size >= WINDOW_SIZE:
            for label, origin in (("WINDOW_A", win_a), ("WINDOW_B", win_b)):
                edges = graph.window_edges(observer, size, size,
                                           origin[0], origin[1], WINDOW_SIZE)
                emit({"kind": "window", "phase": index, "tick": step + 1,
                      "label": label, "origin": list(origin),
                      "packed": pack_edges(edges, WINDOW_EDGE_CAP)})

        del observer
        if time.time() > deadline:
            stopped = "budget_deadline"
            break

    host = [np.asarray(getattr(f, "get", lambda: f)()) for f in device]
    med = float(np.median(latencies)) if latencies else 0.0
    world_ticks = (step + 1) * size * size
    emit({"kind": "phase_end", "phase": index, "name": spec["name"],
          "size": size, "ticks_completed": step + 1, "stopped": stopped,
          "wall_seconds": round(time.time() - t_phase, 1),
          "final_state_digest": obs.state_digest(host),
          "partial_function_max_outdegree": partial_function_max,
          "tick_s_median": round(med, 6),
          "tick_s_p95": round(float(np.percentile(latencies, 95)), 6) if latencies else 0.0,
          "sites_per_sec": round(size * size / med, 1) if med else None,
          "usd_per_1k_world_ticks": round(
              (med * HOURLY / 3600.0) * 1000.0 / (size * size) * 1e6, 6),
          "world_ticks": world_ticks,
          "phase_usd": round((time.time() - t_phase) / 3600.0 * HOURLY, 5),
          "gpu_memory": gpu_memory()})
    del device, prev, host, state
    try:
        xp.get_default_memory_pool().free_all_blocks()
    except Exception:
        pass
    return stopped is None


def main():
    phases = json.loads(os.environ["AETH02_PHASES"])
    t_run0 = time.time()
    deadline = t_run0 + BUDGET_S
    emit({"kind": "run_start", "phases": len(phases), "backend": BACKEND,
          "budget_s": BUDGET_S, "hourly_usd": HOURLY,
          "sample_every": SAMPLE_EVERY, "graph_every": GRAPH_EVERY,
          "deep_every": DEEP_EVERY, "window_every": WINDOW_EVERY,
          "window_size": WINDOW_SIZE, "gpu_memory": gpu_memory()})
    done = 0
    for i, spec in enumerate(phases):
        if time.time() > deadline:
            emit({"kind": "run_truncated", "after_phases": done,
                  "reason": "budget_deadline"})
            break
        if run_phase(i, spec, deadline, t_run0):
            done += 1
    elapsed = time.time() - t_run0
    emit({"kind": "run_end", "phases_completed": done,
          "phases_requested": len(phases),
          "elapsed_s": round(elapsed, 1),
          "spend_usd": round(elapsed / 3600.0 * HOURLY, 5)})
    marker = "AETH02_COMPLETE completed=%d/%d" % (done, len(phases))
    print(marker, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(marker + "\n")
        fh.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
