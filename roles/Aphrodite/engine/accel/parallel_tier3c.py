"""Parallel CPU backend for the Tier-3C transplant stage (ACCEL_CANARY_v1).

Engineering/conformance only. This module rebuilds the Tier-3C arms EXACTLY as
run_tier3c.py does and farms the independent recipient cells (family, arm, i)
out to a process pool. Every cell is computed by run_tier3c.run_recipient()
UNCHANGED, so semantics and charge accounting are the engine's own. No engine
file is modified or monkey-patched.

Inputs are the committed reference artifacts (never re-derived):
  * EVOLVED   = run_tier3c.Lib(TIER3C_ARTIFACT.evolved_entries)
  * PRISTINE  = run_tier3c.pristine()
  * SHAM_k    = run_tier3c.Lib(run_tier3c.stage_shams()[k])
  * dev size  = TIER3C_RESULTS.generator_qualification[fam].size

The conformance full sweep (conformance.check(), limit_cases=0) runs as one
extra pool task.

Usage:
  python parallel_tier3c.py --workers 3 --out BACKEND_RUN.json
"""
import argparse
import json
import multiprocessing as mp
import os
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ACCEL = Path(__file__).resolve().parent
ENGINE = ACCEL.parent
sys.path.insert(0, str(ENGINE))

RESULTS = ENGINE / "TIER3C_RESULTS_2026-09-22.json"
ARTIFACT = ENGINE / "TIER3C_ARTIFACT_2026-09-22.json"

_ARMS = None     # per-worker: arm name -> Lib
_SIZES = None    # per-worker: family -> qualified dev size


def build_arms():
    """Returns (arms, sizes, families, arm_order, lib_hashes), exactly as
    run_tier3c.main() builds them, from the committed reference inputs."""
    import run_tier3c as R
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    res = json.loads(RESULTS.read_text(encoding="utf-8"))
    evolved = R.Lib(art["evolved_entries"])
    base = R.pristine()
    shams = R.stage_shams()
    arms = [("EVOLVED", evolved), ("PRISTINE", base)]
    arms += [("SHAM_%d" % k, R.Lib(s)) for k, s in enumerate(shams)]
    families = list(res["families"])
    sizes = {f: res["generator_qualification"][f]["size"] for f in families}
    hashes = {name: lib.sha256() for name, lib in arms}
    return dict(arms), sizes, families, [a for a, _ in arms], hashes


def _init_worker():
    global _ARMS, _SIZES
    _ARMS, _SIZES, _f, _o, _h = build_arms()


def _cell(fam, arm, i):
    import run_tier3c as R
    t = time.perf_counter()
    row = R.run_recipient(fam, arm, _ARMS[arm], i, _SIZES[fam])
    return ("cell", (fam, arm, i), row, round(time.perf_counter() - t, 3), os.getpid())


def _conformance():
    import conformance as C
    t = time.perf_counter()
    g = C.check()           # limit_cases=0: the full declared sweep
    return ("conformance", None, g, round(time.perf_counter() - t, 3), os.getpid())


def _git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ENGINE),
                                       text=True).strip()
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default=str(ACCEL / "BACKEND_RUN.json"))
    ap.add_argument("--backend", default="cpu_pool")
    ap.add_argument("--host", default=platform.node())
    ap.add_argument("--skip-conformance", action="store_true",
                    help="debug only; a run without conformance cannot be EQUIVALENT")
    ap.add_argument("--limit-cells", type=int, default=0, help="debug only")
    a = ap.parse_args(argv)

    t0 = time.perf_counter()
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _arms, _sizes, families, arm_order, hashes = build_arms()   # hashes for the record
    cells = [(f, arm, i) for f in families for arm in arm_order for i in range(16)]
    if a.limit_cells:
        cells = cells[:a.limit_cells]

    detail = {f: {arm: [None] * 16 for arm in arm_order} for f in families}
    telemetry, pids, conf = [], set(), None
    ctx = mp.get_context("spawn")          # identical start method on Windows and Linux
    with ProcessPoolExecutor(max_workers=a.workers, mp_context=ctx,
                             initializer=_init_worker) as ex:
        futs = []
        if not a.skip_conformance:
            futs.append(ex.submit(_conformance))
        futs += [ex.submit(_cell, *c) for c in cells]
        done = 0
        for fut in as_completed(futs):
            kind, key, payload, secs, pid = fut.result()
            pids.add(pid)
            if kind == "conformance":
                conf = {"GREEN": payload["GREEN"], "checked": payload["checked"],
                        "programs": payload.get("programs"),
                        "mismatches": payload["mismatches"], "seconds": secs}
                print("[conformance] GREEN=%s checked=%d (%.1fs)"
                      % (conf["GREEN"], conf["checked"], secs), flush=True)
                continue
            f, arm, i = key
            detail[f][arm][i] = payload
            telemetry.append({"family": f, "arm": arm, "recipient": i,
                              "seconds": secs, "pid": pid})
            done += 1
            if done % 20 == 0 or done == len(cells):
                print("[cells] %d/%d  %.0fs" % (done, len(cells), time.perf_counter() - t0),
                      flush=True)

    out = {"backend": a.backend, "host": a.host, "workers": a.workers,
           "start_method": "spawn", "python": sys.version.split()[0],
           "platform": platform.platform(), "cpu_count": os.cpu_count(),
           "head_sha": _git_head(), "started_utc": started,
           "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "wall_clock_seconds": round(time.perf_counter() - t0, 1),
           "lib_sha256": hashes, "sizes": _sizes, "cells": len(cells),
           "conformance": conf, "worker_pids": sorted(pids),
           "detail": detail, "cell_telemetry": telemetry}
    Path(a.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("done in %.1fs -> %s (worker pids %s)" % (out["wall_clock_seconds"], a.out,
                                                    sorted(pids)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
