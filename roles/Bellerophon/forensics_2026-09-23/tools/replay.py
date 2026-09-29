"""Replay identity: re-run a historical run from its config.json alone with the FROZEN harness and compare the
regenerated summary.json (minus wall-clock fields) byte-for-byte against the stored one.

    python replay.py r000001 r012345 ...        # explicit runs
    python replay.py --sample 40 --seed 7       # stratified by kind
Writes receipts/REPLAY_<tag>.json. Never writes into the campaign workdir (the replay's run dir goes to LOCAL)."""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

HARNESS = "C:/Users/James/z80atlas_campaign_2026-09-19/code"      # the frozen copy that actually ran


def _one(rid: str) -> dict:
    if HARNESS not in sys.path:
        sys.path.insert(0, HARNESS)
    from prometheus.z80atlas.runner import run_spec
    cfg = Ld.run_file(rid, "config.json")
    stored = Ld.run_file(rid, "summary.json")
    with tempfile.TemporaryDirectory(dir=str(Ld.LOCAL)) as td:
        spec = {"id": cfg["id"], "family": cfg["family"], "vec": cfg["vec"], "seed": cfg["seed"], "ticks": cfg["ticks"], "cells": cfg["cells"],
                "budget": cfg["budget"], "parents": cfg["parents"], "reason": cfg["reason"], "stage": cfg["stage"], "workdir": td,
                "init_tapes": cfg["init_tapes"], "kind": "replay"}
        res = run_spec(spec)
        new = json.loads(open(os.path.join(td, rid, "summary.json"), encoding="utf-8").read())
        files_equal = {}
        for fn in ("config.json", "ticks.jsonl", "events.jsonl", "snapshots.jsonl", "specimens.json", "exploits.json", "geometry.json"):
            a = Ld.WD / "runs" / rid / fn; b = os.path.join(td, rid, fn)
            if a.exists() and os.path.exists(b):
                files_equal[fn] = a.read_bytes() == open(b, "rb").read()
    strip = lambda d: {k: v for k, v in d.items() if k != "wall_s"}
    diff = sorted(k for k in set(strip(stored)) | set(strip(new)) if strip(stored).get(k) != strip(new).get(k))
    return {"run": rid, "summary_equal": not diff, "summary_diff_keys": diff, "files_equal": files_equal}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="*")
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--tag", default="sample")
    a = ap.parse_args()
    Ld.LOCAL.mkdir(parents=True, exist_ok=True)
    ids = list(a.runs)
    if a.sample:
        R = Ld.runs(); rng = random.Random(a.seed)
        by = collections.defaultdict(list)
        for r in R:
            by[r["kind"]].append(r["id"])
        per = max(1, a.sample // len(by))
        for k in sorted(by):
            ids += rng.sample(by[k], min(per, len(by[k])))
    with mp.Pool(a.workers) as pool:
        out = pool.map(_one, ids)
    rep = {"harness": HARNESS, "n": len(out), "all_summary_equal": all(o["summary_equal"] for o in out),
           "all_files_equal": all(all(o["files_equal"].values()) for o in out), "rows": out}
    p = Ld.write("REPLAY_%s.json" % a.tag, rep)
    print(p, rep["n"], "summary_equal", sum(o["summary_equal"] for o in out), "files_equal", sum(all(o["files_equal"].values()) for o in out))
    for o in out:
        if not o["summary_equal"] or not all(o["files_equal"].values()):
            print(o)


if __name__ == "__main__":
    main()
