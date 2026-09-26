"""Scaling probe (OFF-PLAN, engineering only): wall time and peak RSS of one coupled run vs horizon.

Seeds are in the pilot range 7.6e12.. (disjoint from every campaign stream). The probe measures cost, not science: it
prints no competence or births. Usage (from a checkout root so `prometheus` imports):
    python roles/Bellerophon/multiday_2026-09-26/tools/scale_probe.py --ticks 500 2000 5000 --out <json>
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

SEED = 7_600_000_000_000


def one(ticks: int, workdir: str, q) -> None:
    from prometheus.z80atlas import coupling_campaign as CC
    from prometheus.z80atlas.runner import run_spec
    over = dict(CC.V3, **CC.K["K40"], coupling="ON")
    vec = dict(CC.COMMON, task="ECHO", init="SEEDED_REPLICATOR")
    spec = {"id": "probe_%d" % ticks, "family": "probe", "vec": vec, "seed": SEED + ticks, "ticks": ticks, "cells": CC.CELLS,
            "budget": CC.BUDGET, "parents": [], "reason": "scale probe", "stage": "probe", "workdir": workdir, "init_tapes": [],
            "config_overrides": over, "geometry": False}
    t0 = time.time()
    run_spec(spec)
    q.put(time.time() - t0)


def main() -> None:
    import psutil
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for t in a.ticks:
        with tempfile.TemporaryDirectory() as td:
            q = mp.Queue()
            p = mp.Process(target=one, args=(t, td, q))
            p.start()
            proc = psutil.Process(p.pid); peak = 0
            while p.is_alive():
                try:
                    peak = max(peak, proc.memory_info().rss)
                except psutil.Error:
                    pass
                time.sleep(0.5)
            p.join()
            wall = q.get() if not q.empty() else None
            rows.append({"ticks": t, "wall_s": round(wall, 1) if wall else None, "peak_rss_mb": round(peak / 2 ** 20), "exitcode": p.exitcode})
            pathlib.Path(a.out).write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rows))


if __name__ == "__main__":
    main()
