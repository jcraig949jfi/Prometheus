"""Phase 5 step 6: replay historical runs through the REPAIRED harness (this worktree's prometheus/z80atlas, physics
v1 -- the default) and check that every HISTORICAL key of summary.json and of each ticks/events record is unchanged.
New keys (additive measurement) are allowed; config.json gains the new Config fields (physics, ext_mut_mult) and is
therefore compared on its historical keys too.
    python replay_repaired.py --from REPLAY_sample36.json --workers 8
Writes receipts/REPLAY_REPAIRED_<tag>.json."""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

WORKTREE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def _jsonl(p):
    with open(p, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def _one(rid: str) -> dict:
    if WORKTREE not in sys.path:
        sys.path.insert(0, WORKTREE)
    from prometheus.z80atlas.runner import run_spec
    import prometheus.z80atlas as pz
    assert os.path.abspath(pz.__file__).startswith(WORKTREE), pz.__file__
    cfg = Ld.run_file(rid, "config.json"); stored = Ld.run_file(rid, "summary.json")
    with tempfile.TemporaryDirectory(dir=str(Ld.LOCAL)) as td:
        spec = {"id": cfg["id"], "family": cfg["family"], "vec": cfg["vec"], "seed": cfg["seed"], "ticks": cfg["ticks"], "cells": cfg["cells"],
                "budget": cfg["budget"], "parents": cfg["parents"], "reason": cfg["reason"], "stage": cfg["stage"], "workdir": td,
                "init_tapes": cfg["init_tapes"], "geometry_v2": False}
        run_spec(spec)
        new = json.loads(open(os.path.join(td, rid, "summary.json"), encoding="utf-8").read())
        diffs = [k for k in stored if k not in ("wall_s", "config_sha256", "geometry") and stored[k] != new.get(k)]
        gdiff = [k for k in (stored.get("geometry") or {}) if stored["geometry"][k] != (new.get("geometry") or {}).get(k)]
        rec = {}
        for fn in ("ticks.jsonl", "events.jsonl", "snapshots.jsonl"):
            a = _jsonl(Ld.WD / "runs" / rid / fn); b = _jsonl(os.path.join(td, rid, fn))
            rec[fn] = len(a) == len(b) and all({k: y.get(k) for k in x} == x for x, y in zip(a, b))
        for fn in ("specimens.json", "exploits.json", "geometry.json"):
            pa = Ld.WD / "runs" / rid / fn; pb = os.path.join(td, rid, fn)
            if pa.exists():
                a = json.loads(pa.read_text(encoding="utf-8")); b = json.loads(open(pb, encoding="utf-8").read())
                if isinstance(a, dict):
                    rec[fn] = {k: b.get(k) for k in a} == a
                else:
                    rec[fn] = a == b
        c_new = json.loads(open(os.path.join(td, rid, "config.json"), encoding="utf-8").read())
        rec["config.json(historical keys)"] = all(c_new["config"].get(k) == v for k, v in cfg["config"].items())
    return {"run": rid, "historical_summary_keys_equal": not diffs, "diff_keys": diffs, "geometry_summary_diff": gdiff, "files": rec,
            "new_fields": {k: new.get(k) for k in ("self_rep_births", "sr_max_depth", "extinct_tick", "world_copies_under_endogenous")},
            "verified": new.get("verified"), "tail_h": new.get("tail_h"), "first_self_replication": new.get("first_self_replication")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="*")
    ap.add_argument("--from", dest="src", default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--tag", default="sample36")
    a = ap.parse_args()
    ids = list(a.runs)
    if a.src:
        ids += [r["run"] for r in json.loads((Ld.OUT / a.src).read_text(encoding="utf-8"))["rows"]]
    with mp.Pool(a.workers) as pool:
        rows = pool.map(_one, ids, chunksize=1)
    ok = all(r["historical_summary_keys_equal"] and not r["geometry_summary_diff"] and all(r["files"].values()) for r in rows)
    p = Ld.write("REPLAY_REPAIRED_%s.json" % a.tag, {"harness": WORKTREE, "physics": "v1", "n": len(rows), "all_historical_equal": ok, "rows": rows})
    print(p, len(rows), "all_historical_equal", ok)
    for r in rows:
        if not (r["historical_summary_keys_equal"] and not r["geometry_summary_diff"] and all(r["files"].values())):
            print(r["run"], r["diff_keys"], r["geometry_summary_diff"], r["files"])


if __name__ == "__main__":
    main()
