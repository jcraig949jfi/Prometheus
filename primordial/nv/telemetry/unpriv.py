"""Q3: N2 telemetry features without GPU counter access (engineering descriptors, not fitness).

Nsight capture is BLOCKED on this host (Q1/Q2: nsys needs admin; ncu 2025.2.1 hits
ERR_NVGPUCTRPERM; CUPTI INVALID_DEVICE). These features need no privilege:

  wall_s           host wall time of the region
  op_time_s        time inside CUDA-producing ops, each op timed with a synchronize after it
  copy_time_s      the same, for host<->device copies only
  kernel_share     (op_time_s - copy_time_s) / wall_s
  h2d_bytes        bytes moved host -> device (counted at the aten dispatch, exact)
  d2h_bytes        bytes moved device -> host
  peak_mem_bytes   torch.cuda.max_memory_allocated over the region
  memory_bound     copy_time_s > (op_time_s - copy_time_s)  (transfer-dominated region)
  dmon_sm_pct      mean nvidia-smi dmon `sm` utilisation while the region ran (optional)
Counter-derived features (per-kernel CUPTI time, PCIe counters) are BLOCKED(ERR_NVGPUCTRPERM).

Timing each op with a synchronize changes the region's speed. The features describe
where time goes. They are not a throughput number, and any timing claim needs the GPU lease.

Cheats (must move the right feature): host sleep -> kernel_share down, wall up, bytes equal;
extra device copy -> h2d_bytes up by exactly the copied tensor's bytes.

usage: python -m primordial.nv.telemetry.unpriv --out primordial/ledger/rows/Q/Q3-unpriv.jsonl
"""
from __future__ import annotations

import argparse
import subprocess
import threading
import time

import torch
from torch.utils._python_dispatch import TorchDispatchMode

BLOCKED = {"cupti_kernel_time_s": "BLOCKED(ERR_NVGPUCTRPERM)", "pcie_counter_bytes": "BLOCKED(ERR_NVGPUCTRPERM)"}
COPY_OPS = {"aten._to_copy.default", "aten.copy_.default"}


def _dev(x):
    return x.device.type if isinstance(x, torch.Tensor) else None


class _Meter(TorchDispatchMode):
    def __init__(self):
        super().__init__()
        self.op_time = self.copy_time = 0.0
        self.h2d = self.d2h = 0
        self.n_ops = 0

    def __torch_dispatch__(self, func, types, args=(), kwargs=None):
        kwargs = kwargs or {}
        name = str(func)
        t0 = time.perf_counter()
        out = func(*args, **kwargs)
        outs = out if isinstance(out, (tuple, list)) else (out,)
        cuda_out = any(_dev(o) == "cuda" for o in outs)
        src = args[1] if name == "aten.copy_.default" else args[0] if args else None
        dst = args[0] if name == "aten.copy_.default" else outs[0]
        is_copy = name in COPY_OPS and _dev(src) and _dev(dst) and _dev(src) != _dev(dst)
        if cuda_out or is_copy or any(_dev(a) == "cuda" for a in args):
            torch.cuda.synchronize()
            dt = time.perf_counter() - t0
            self.op_time += dt
            self.n_ops += 1
            if is_copy:
                self.copy_time += dt
                nb = src.numel() * src.element_size()
                if _dev(dst) == "cuda":
                    self.h2d += nb
                else:
                    self.d2h += nb
        return out


class _Dmon:
    def __init__(self):
        self.vals, self.p = [], None

    def __enter__(self):
        try:
            self.p = subprocess.Popen(["nvidia-smi", "dmon", "-s", "u", "-d", "1"], stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL, text=True)
            threading.Thread(target=self._read, daemon=True).start()
            time.sleep(1.5)                                    # let nvidia-smi start outside the timed region
        except FileNotFoundError:
            self.p = None
        return self

    def _read(self):
        for line in self.p.stdout:
            f = line.split()
            if f and not line.startswith("#") and len(f) > 1 and f[1].isdigit():
                self.vals.append(int(f[1]))

    def __exit__(self, *exc):
        if self.p:
            self.p.terminate()
        return False


def measure(fn, dmon: bool = False) -> dict:
    """Run fn() once and return the feature row (no status; the caller tags it)."""
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    base = torch.cuda.memory_allocated()
    m = _Meter()
    d = _Dmon() if dmon else None
    if d:
        d.__enter__()
    t0 = time.perf_counter()
    with m:
        fn()
    torch.cuda.synchronize()
    wall = time.perf_counter() - t0
    if d:
        d.__exit__(None, None, None)
    compute = m.op_time - m.copy_time
    return {"wall_s": wall, "op_time_s": m.op_time, "copy_time_s": m.copy_time, "n_cuda_ops": m.n_ops,
            "kernel_share": compute / wall if wall > 0 else 0.0, "h2d_bytes": m.h2d, "d2h_bytes": m.d2h,
            "peak_mem_bytes": int(torch.cuda.max_memory_allocated() - base),
            "memory_bound": bool(m.copy_time > compute),
            "dmon_sm_pct": (sum(d.vals) / len(d.vals)) if d and d.vals else None, **BLOCKED}


def brain_forward(batch: int = 4096, D: int = 9, K: int = 16, sleep_s: float = 0.0, extra_copy: bool = False,
                  seed: int = 0):
    """Torch GPU linear-brain forward (lane C's linear family shape: obs D -> K logits -> argmax), host obs in,
    actions out. Cheat knobs: an injected host sleep, or a redundant second upload of the obs."""
    g = torch.Generator().manual_seed(seed)
    obs = torch.randint(0, 1 << 16, (batch, D), generator=g).to(torch.float32)
    W = torch.randn(K, D, generator=g)
    b = torch.randn(K, generator=g)

    def run():
        Wd, bd = W.cuda(), b.cuda()
        x = obs.cuda()
        if extra_copy:
            x = obs.cuda()                                     # cheat: the same upload twice
        if sleep_s:
            time.sleep(sleep_s)                                # cheat: host stall inside the region
        act = (x @ Wd.T + bd).argmax(1)
        return act.cpu()
    return run, obs.numel() * obs.element_size()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--sleep", type=float, default=0.05)
    a = ap.parse_args(argv)
    from primordial.bus import bus
    from primordial.fabric.rows import RowWriter
    torch.set_num_threads(1)
    arms = {"honest": {}, "cheat_sleep": {"sleep_s": a.sleep}, "cheat_extra_copy": {"extra_copy": True}}
    with RowWriter(a.out, "Q3-unpriv-features", commit_every_s=3600) as w:
        warm, _ = brain_forward()
        warm()
        measure(warm)                                          # Q3 rep0 paid first-use meter cost: 997 ms, share 0.000
        with bus.gpu_lease("Q3 unpriv telemetry features", ttl_s=600, wait_s=300) as lease:
            for rep in range(a.reps):
                for arm, kw in arms.items():
                    fn, obs_bytes = brain_forward(seed=rep, **kw)
                    row = measure(fn, dmon=(rep == 0))
                    row.update(arm=arm, rep=rep, workload="torch_linear_forward_4096x9", obs_bytes=obs_bytes,
                               lease_lost=lease["lost"],
                               status="control" if arm == "honest" else "cheat")
                    w.write(row)
                    print(f"{arm:<17} rep{rep} wall={row['wall_s']*1e3:7.2f}ms share={row['kernel_share']:.3f} "
                          f"h2d={row['h2d_bytes']} d2h={row['d2h_bytes']} peak={row['peak_mem_bytes']} "
                          f"membound={row['memory_bound']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
