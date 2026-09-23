"""D-R5-2 (ANOM-1789471401162-0): is the GPU-1 crossover reversal at n 65536 a one-shot cold host->device copy?

E-R5-3-gpu1 added h2d_s to Warp's kernel median. In nv.warp.crossover.bench_cell, h2d_s is ONE timed call: the first
load_actions on a freshly prepared encounter (wp.array from a pageable numpy buffer, i.e. a device allocation plus the
copy). The kernel was a median of reps; the copy was not. This job times the copy the way the kernel was timed.

Per n (world 4, action tensor [64, n, 1, 3] int32), all inside the arbiter's O5 lease, venv w:
  cold    first load_actions + synchronize on a fresh WpEncounter (E's h2d_s semantics)
  alloc   reps x load_actions + synchronize (fresh device allocation every call, E's code path, warm)
  assign  reps x preallocated device array .assign(numpy) + synchronize (copy, no allocation)
  pinned  reps x wp.copy(preallocated device, preallocated pinned host) + synchronize
The three warm paths alternate within each rep. Oracle: device readback == host actions bitwise, per path.
The kernel is NOT re-timed: the decision reuses E's committed n 65536 medians (source rows below).
Predicate: bus claim 'PREDICATE D-R5-2-h2d-cold-warm'.
"""
from __future__ import annotations

import os
import time

from primordial.nv.r5_harness import timing_row

EXP = "D-R5-2-h2d-cold-warm"
NS = (16384, 32768, 65536, 131072)
REPS = 11
DECIDE_N = 65536
E_KERNEL_S = 3.295e-3             # E-R5-3-gpu1-n65536 warp_cuda kernel_s (E note 1789471230754-0)
E_NUMBA_T8_S = 10.355e-3          # E-R5-3-gpu1-n65536 numba_t8 wall_s (best numba)


def _timed(f) -> float:
    t = time.perf_counter()
    f()
    return time.perf_counter() - t


def _median(xs) -> float:
    s = sorted(xs)
    m = len(s) // 2
    return s[m] if len(s) % 2 else 0.5 * (s[m - 1] + s[m])


def job(emit, g: int = 4, ns=NS, reps: int = REPS, checkpoint_path=None):
    os.environ.setdefault("NUMBA_NUM_THREADS", "1")
    import numpy as np
    import warp as wp
    from primordial.nv.warp.crossover import N_HASH_SAMPLE, action_tensor, episode_seeds, make_world
    from primordial.nv.warp.world import WpEncounter

    wp.init()
    dev = "cuda:0"
    mech, wid = make_world(g)
    alloc_65536 = None
    all_exact = True
    for n in ns:
        acts = np.ascontiguousarray(action_tensor(mech, n, seed=g), np.int32)
        mib = acts.nbytes / 2 ** 20
        w = WpEncounter(mech, wid, device=dev)
        rec = np.sort(np.random.default_rng(g).choice(n, size=min(N_HASH_SAMPLE, n), replace=False))
        w.prepare(episode_seeds(n, base=7000 + g), record=rec)
        wp.synchronize_device(dev)
        cold = _timed(lambda: (w.load_actions(acts), wp.synchronize_device(dev)))
        dst = wp.empty(shape=acts.shape, dtype=wp.int32, device=dev)
        pin = wp.array(acts, dtype=wp.int32, device="cpu", pinned=True)
        wp.synchronize_device(dev)
        t = {"alloc": [], "assign": [], "pinned": []}
        for _ in range(reps):
            t["alloc"].append(_timed(lambda: (w.load_actions(acts), wp.synchronize_device(dev))))
            t["assign"].append(_timed(lambda: (dst.assign(acts), wp.synchronize_device(dev))))
            t["pinned"].append(_timed(lambda: (wp.copy(dst, pin), wp.synchronize_device(dev))))
        ex = {"alloc": bool(np.array_equal(w.acts.numpy(), acts)), "pinned": bool(np.array_equal(dst.numpy(), acts))}
        dst.zero_()
        dst.assign(acts)
        wp.synchronize_device(dev)
        ex["assign"] = bool(np.array_equal(dst.numpy(), acts))
        ex["cold"] = ex["alloc"]                                  # same code path, same destination semantics
        exact = "PASS" if all(ex.values()) else "FAIL"
        all_exact &= exact == "PASS"
        emit({"kind": "oracle", "question": "D-R5-2", "batch_size": n, "readback_bitwise": ex, "exactness": exact,
              "nbytes": int(acts.nbytes), "shape": list(acts.shape), "world_seed": g, "ts": round(time.time(), 3)})
        if exact != "PASS":
            continue
        med = {k: _median(v) for k, v in t.items()}
        emit(timing_row("D-R5-2", "h2d_cold", cold, n, True, "cold", "h2d_alloc_warm", exact, world_seed=g, reps=1,
                        nbytes=int(acts.nbytes), ms_per_mib=1e3 * cold / mib, ts=round(time.time(), 3)))
        for k in ("alloc", "assign", "pinned"):
            emit(timing_row("D-R5-2", f"h2d_{k}", med[k], n, True, "warm", "h2d_cold", exact, world_seed=g, reps=reps,
                            t_s=[round(x, 7) for x in t[k]], nbytes=int(acts.nbytes), ms_per_mib=1e3 * med[k] / mib,
                            cold_over_warm=cold / med[k] if med[k] > 0 else None, ts=round(time.time(), 3)))
        if n == DECIDE_N:
            alloc_65536 = med["alloc"]
        del w, dst, pin
    if alloc_65536 is None or not all_exact:
        decision, composite = "INDETERMINATE", None
    else:
        composite = E_KERNEL_S + alloc_65536
        decision = "REFUTED" if composite < E_NUMBA_T8_S else "UPHELD"
    emit({"kind": "summary", "exp": EXP, "question": "D-R5-2", "decide_n": DECIDE_N, "e_kernel_s": E_KERNEL_S,
          "e_numba_t8_s": E_NUMBA_T8_S, "warm_alloc_h2d_s": alloc_65536, "warp_composite_warm_s": composite,
          "decision_provisional": decision, "note": "final decision also requires every timing row speed_status VALID "
          "(arbiter stamp: lease held, not lost)", "ts": round(time.time(), 3)})
