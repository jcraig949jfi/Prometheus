"""P4: cost of the precision gene on cuda -- wall (under the O5 GPU lease), VRAM, bytes -- per family x precision.

Posted on the bus before the run (P4-precision-cost-cuda):
  kernel   primordial.nv.precision.forward.precision_logits on cuda, END TO END as the closed loop calls it
           (host weights + obs in, float64 logits out), one genome, n obs rows, D = 8 (w4)
  order    exactness oracle first (fp64 ref_logits, clear-row agreement on 512 rows, honest vs skip-odd
           cheat), then timing; a cell whose oracle fails gets no speed number
  timing   warmup 2, reps 7 alternating precisions, torch.cuda.synchronize around each call; median
  VRAM     torch.cuda peak allocated above the pre-call baseline
  VALID    only inside bus.gpu_lease with lease not lost AND nvidia-smi util <= 10% just before timing;
           anything else is INDETERMINATE for speed (bytes and VRAM stand either way)

  python -m primordial.nv.precision.p4_cost [--ns 1024,65536] [--reps 7] [--exp P4-...] [--no-lease]
                                           [--wait-s 300] [--wait-idle-s 300]
"""
from __future__ import annotations

import argparse
import contextlib
import json
import pathlib
import subprocess
import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.nv.precision import forward as pf

EXP = "P4-precision-cost-cuda"
ROOT = pathlib.Path(__file__).resolve().parents[3]
D = 8
IDLE_UTIL = 10


def gpu_util() -> int | None:
    try:
        q = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=5)
        return int(q.stdout.split()[0])
    except Exception:
        return None


def wait_idle(max_s: float, poll_s: float = 5.0) -> tuple[int | None, float]:
    t0 = time.monotonic()
    u = gpu_util()
    while (u is None or u > IDLE_UTIL) and time.monotonic() - t0 < max_s:
        time.sleep(poll_s)
        u = gpu_util()
    return u, round(time.monotonic() - t0, 1)


def _case(family, n, seed=0):
    rng = np.random.default_rng(seed)
    fam = gm.FAMILIES[family](D)
    g1 = fam.one(fam.init(rng, 1), 0)
    obs = rng.integers(0, 65536, (n, D), dtype=np.int64).astype(np.uint16)
    return fam, g1, obs


def oracle(family, precision, seed=0) -> dict:
    fam, g1, obs = _case(family, 512, seed)
    ref = fam.ref_logits(g1, obs)
    honest = pf.exactness(family, g1, obs, precision, "cuda", ref=ref)
    cheat = pf.exactness(family, g1, obs, precision, "cuda", cheat=True, ref=ref)
    ok = honest["agree_clear"] >= 0.95 and cheat["agree_clear"] < honest["agree_clear"] - 0.2
    return {"agree_clear": honest["agree_clear"], "cheat_agree_clear": cheat["agree_clear"], "oracle_ok": bool(ok)}


def time_cells(families, precisions, n, reps, warmup=2) -> dict:
    import torch
    cases = {f: _case(f, n, seed=1) for f in families}
    call = lambda f, p: pf.precision_logits(f, cases[f][1], cases[f][2], p, "cuda")  # noqa: E731
    for _ in range(warmup):
        for f in families:
            for p in precisions:
                call(f, p)
    t = {(f, p): [] for f in families for p in precisions}
    for _ in range(reps):                       # alternate cells every rep: drift hits all cells alike
        for f in families:
            for p in precisions:
                torch.cuda.synchronize()
                t0 = time.perf_counter()
                call(f, p)
                torch.cuda.synchronize()
                t[(f, p)].append(time.perf_counter() - t0)
    vram = {}
    for f in families:
        for p in precisions:
            torch.cuda.synchronize()
            base = torch.cuda.memory_allocated()
            torch.cuda.reset_peak_memory_stats()
            call(f, p)
            torch.cuda.synchronize()
            vram[(f, p)] = int(torch.cuda.max_memory_allocated() - base)
    return {"t_s": t, "vram_peak_bytes": vram}


def speed_status(rec, util_pre, oracle_ok) -> str:
    lost = None if rec is None else bool(rec.get("lost"))
    util_ok = util_pre is not None and util_pre <= IDLE_UTIL
    return "VALID" if (rec is not None and lost is False and util_ok and oracle_ok) else "INDETERMINATE"


def run(ns, reps, exp="", no_lease=False, wait_s=300.0, wait_idle_s=300.0, families=pf.FAMILIES,
        precisions=pf.PRECISIONS, writer=None) -> list[dict]:
    import torch
    torch.set_num_threads(1)
    from primordial.bus import bus
    orc = {(f, p): oracle(f, p) for f in families for p in precisions}       # oracle before any timing
    lease = contextlib.nullcontext(None) if no_lease else bus.gpu_lease(exp or "P4 precision cost", ttl_s=600,
                                                                        wait_s=wait_s)
    rows = []
    with lease as rec:
        for n in ns:
            util_pre, waited = wait_idle(wait_idle_s) if rec is not None else (gpu_util(), 0.0)
            res = time_cells(families, precisions, n, reps)
            util_post = gpu_util()
            hl = bus.host_load()
            for f in families:
                for p in precisions:
                    ts = res["t_s"][(f, p)]
                    o = orc[(f, p)]
                    row = {"kind": "cost_cell", "family": f, "precision": p, "substrate": pf.substrate(f, p, "cuda"),
                           "n_rows": n, "D": D, "path": "e2e_host", "reps": reps, "t_s": ts,
                           "median_s": float(np.median(ts)), "rows_per_s": n / float(np.median(ts)),
                           "vram_peak_bytes": res["vram_peak_bytes"][(f, p)],
                           "param_bytes": pf.nbytes(f, D, p), **o,
                           "lease": rec is not None, "lease_lost": None if rec is None else bool(rec.get("lost")),
                           "gpu_util_pre": util_pre, "gpu_util_post": util_post, "idle_wait_s": waited,
                           "host_load": hl, "threads": 1}
                    row["speed_status"] = speed_status(rec, util_pre, o["oracle_ok"])
                    rows.append(row)
                    if writer:
                        writer.write({"status": "record" if row["speed_status"] == "VALID" else "dev", **row})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="1024,65536")
    ap.add_argument("--reps", type=int, default=7)
    ap.add_argument("--exp", default="")
    ap.add_argument("--no-lease", action="store_true", help="dev only: every cell INDETERMINATE for speed")
    ap.add_argument("--wait-s", type=float, default=300)
    ap.add_argument("--wait-idle-s", type=float, default=300)
    a = ap.parse_args(argv)
    writer = None
    if a.exp:
        from primordial.fabric.rows import RowWriter
        writer = RowWriter(ROOT / "primordial" / "ledger" / "rows" / "P" / f"{a.exp}.jsonl", a.exp,
                           commit_every_s=10**9)
    try:
        rows = run([int(x) for x in a.ns.split(",")], a.reps, a.exp, a.no_lease, a.wait_s, a.wait_idle_s, writer=writer)
    finally:
        if writer:
            writer.close()
    for r in rows:
        print(json.dumps({k: r[k] for k in ("family", "precision", "n_rows", "median_s", "rows_per_s",
                                             "vram_peak_bytes", "param_bytes", "agree_clear", "oracle_ok",
                                             "gpu_util_pre", "speed_status")}), flush=True)
    return 0 if all(r["oracle_ok"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
