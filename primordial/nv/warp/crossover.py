"""W2: crossover table for lane B's open-loop world step, n_envs 1..65536, three forms.

Predicate posted on the bus before any timing (1789426347225-0, W2-warp-numba-crossover):
  forms     numba      primordial/soup/b1/nb_world.run_all (the world core B6 fuses), read-only
            warp_cpu   primordial/nv/warp/world.py on "cpu"
            warp_cuda  the same kernel on "cuda:0"; wall includes synchronize; H2D of the action
                       tensor timed separately (h2d_s), state reset untimed
  gate      per (world, n), before a time counts: 8 sampled envs of the TIMED Warp encounters
            (logged inside the timed run) trace-hash equal to the wforge Encounter; done_tick equal
            across all forms; final charge and registers warp_cpu == warp_cuda, and == numba's log
            where n <= 1024 (numba logs T x n x R, so larger n skip the numba charge/regs check).
            v1 of this gate (done_tick + charge only) PASSED skip_lin at w4 n=64; hence the hash.
  timing    compile excluded; median of `reps` alternating reps; the table runs inside
            bus.gpu_lease; speed_status VALID only when the lease was held and not lost and
            nvidia-smi showed <= 10% utilisation just before the cell, else INDETERMINATE
  B6 fused  adds the brain, so it is context, not the comparator for a world-only kernel

    python -m primordial.nv.warp.crossover --worlds 1,2,3,4,5 --reps 5 --exp W2-warp-numba-crossover
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_k, "1")                             # W's budget (conductor contract)

import argparse
import contextlib
import json
import pathlib
import subprocess
import time

import numpy as np
import warp as wp

from primordial.soup.b1.common import action_tensor, episode_seeds, make_world   # lane B, read-only
from primordial.soup.b1.nb_world import NbEncounter                               # lane B, read-only

from .oracle import wforge_episode
from .world import WpEncounter

NS = [1, 4, 16, 64, 256, 1024, 4096, 16384, 65536]
NUMBA_LOG_MAX = 1024
N_HASH_SAMPLE = 8


def gpu_util() -> int | None:
    try:
        q = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20)
        return int(q.stdout.strip().splitlines()[0])
    except Exception:
        return None


def _timed(fn):
    t = time.perf_counter()
    fn()
    return time.perf_counter() - t


def bench_cell(g: int, n: int, reps: int = 5, warp_cheat: str = "", devices=("cpu", "cuda:0")) -> dict:
    mech, wid = make_world(g)
    seeds = episode_seeds(n, base=7000 + g)
    acts = action_tensor(mech, n, seed=g)
    log = n <= NUMBA_LOG_MAX
    nb = NbEncounter(mech, wid)
    nb.prepare(seeds, log=log)
    rec = np.sort(np.random.default_rng(g).choice(n, size=min(N_HASH_SAMPLE, n), replace=False))
    ws, h2d = {}, None
    for dev in devices:
        w = WpEncounter(mech, wid, cheat=warp_cheat, device=dev)
        w.prepare(seeds, record=rec)                               # the timed kernel logs the sampled envs
        wp.synchronize_device(dev)
        dt = _timed(lambda: (w.load_actions(acts), wp.synchronize_device(dev)))
        if dev.startswith("cuda"):
            h2d = dt
        ws[dev] = w
    nb.run(acts)                                                   # compile / warm, outside timing
    for w in ws.values():
        w.run()
        w.reset()
    # ---- gate
    nb.run(acts)
    dt_nb = nb.done_tick.copy()
    ch, rg, hs = {}, {}, {}
    for dev, w in ws.items():
        w.run()
        ch[dev], rg[dev] = w.final_charge(), w.reg.numpy()
        hs[dev] = [h.decode() for h in w.trace_hashes()]
    ref = [wforge_episode(mech, wid, int(seeds[e]), acts[:, e]) for e in rec]
    gate = {"done_tick_eq": all(np.array_equal(w.done_tick.numpy(), dt_nb) for w in ws.values()),
            # the claim itself: sampled envs of the timed kernel trace-hash equal to wforge (charge alone
            # misses skip_lin in 27/480 W1 episodes)
            "wforge_hash_sample_eq": all(h == [r[0] for r in ref] for h in hs.values())}
    if len(ws) > 1:
        (a, ra), (b, rb) = [(ch[d], rg[d]) for d in list(ws)[:2]]
        gate["charge_cpu_eq_cuda"] = bool(np.array_equal(a, b))
        gate["regs_cpu_eq_cuda"] = bool(np.array_equal(ra, rb))
    if log:
        last = dt_nb - 1
        ch_nb = nb.log_charge[last, np.arange(n)]
        rg_nb = nb.log_regs[last, np.arange(n)]
        gate["charge_eq_numba"] = all(bool(np.array_equal(c, ch_nb)) for c in ch.values())
        gate["regs_eq_numba"] = all(bool(np.array_equal(r, rg_nb)) for r in rg.values())
    gate_ok = all(gate.values())
    # ---- timing: alternating reps
    util_pre = gpu_util()
    t = {"numba": []} | {("warp_cuda" if d.startswith("cuda") else "warp_cpu"): [] for d in ws}
    for _ in range(reps):
        t["numba"].append(_timed(lambda: nb.run(acts)))
        for dev, w in ws.items():
            w.reset()
            t["warp_cuda" if dev.startswith("cuda") else "warp_cpu"].append(_timed(w.run))
    med = {k: float(np.median(v)) for k, v in t.items()}
    steps = int(dt_nb.sum()) * mech.n_slots
    row = {"world_seed": g, "world_id": wid, "n_envs": n, "T": mech.horizon, "S": mech.n_slots,
           "R": mech.n_regs, "L": len(mech.lin_ops), "slot_steps": steps, "warp_cheat": warp_cheat or None,
           "gate": gate, "gate_ok": gate_ok, "reps": reps, "t_s": t, "median_s": med, "h2d_s": h2d,
           "gpu_util_pre": util_pre, "threads": int(os.environ["NUMBA_NUM_THREADS"])}
    for k, v in med.items():
        row[f"{k}_slot_steps_per_s"] = steps / v if v > 0 else None
    if "warp_cuda" in med:
        row["speedup_cuda_vs_numba"] = med["numba"] / med["warp_cuda"]
    if "warp_cpu" in med:
        row["speedup_cpu_vs_numba"] = med["numba"] / med["warp_cpu"]
    return row


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="1,2,3,4,5")
    ap.add_argument("--ns", default=",".join(map(str, NS)))
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--exp", default="")
    ap.add_argument("--no-lease", action="store_true", help="dev only: every cell INDETERMINATE for speed")
    ap.add_argument("--wait-s", type=float, default=300)
    a = ap.parse_args(argv)
    wp.init()
    from primordial.bus import bus
    writer = None
    if a.exp:
        from primordial.fabric.rows import RowWriter
        path = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "W" / f"{a.exp}.jsonl"
        writer = RowWriter(path, a.exp, commit_every_s=10**9)
    lease = contextlib.nullcontext(None) if a.no_lease else bus.gpu_lease(a.exp or "W2 crossover", ttl_s=600,
                                                                         wait_s=a.wait_s)
    n_bad = 0
    try:
        with lease as rec:
            for g in (int(x) for x in a.worlds.split(",")):
                for n in (int(x) for x in a.ns.split(",")):
                    row = bench_cell(g, n, a.reps)
                    lost = None if rec is None else bool(rec.get("lost"))
                    util_ok = row["gpu_util_pre"] is not None and row["gpu_util_pre"] <= 10
                    row["lease"] = rec is not None
                    row["lease_lost"] = lost
                    row["host_load"] = bus.host_load()
                    row["speed_status"] = ("VALID" if rec is not None and lost is False and util_ok and row["gate_ok"]
                                           else "INDETERMINATE")
                    n_bad += not row["gate_ok"]
                    print(json.dumps({k: row[k] for k in ("world_seed", "n_envs", "gate_ok", "median_s", "h2d_s",
                                                         "speedup_cuda_vs_numba", "speedup_cpu_vs_numba",
                                                         "gpu_util_pre", "speed_status")}), flush=True)
                    if writer:
                        writer.write({"status": "record" if not a.no_lease else "dev", **row})
    finally:
        if writer:
            writer.close()
    return 1 if n_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
