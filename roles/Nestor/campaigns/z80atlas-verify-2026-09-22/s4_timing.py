"""S4 full-length timing for the candidate manifest. Records WALL TIME ONLY.

Why full length: the 120-epoch smoke scaled linearly cannot see P-11's cost, which is
paid per candidate pair event, and pair events are not uniform in time.

Why no outcomes: these runs precede freeze. Seeds are drawn from a range the manifest
never uses (9_9xx_xxx), and only wall seconds, epochs and slices are kept - no held,
depth, event or verdict field is written - so timing cannot become a pilot of the result.

One of every arm for every H2 specimen, H3 cell and H4 block, plus one H1 bundle, run on
WORKERS processes (the campaign's worker count) so contention matches production.

    python s4_timing.py  -> S4_TIMING.json
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
WORKERS = 6
TIMING_SEED = 9_900_001


def _run(job):
    import world
    kw = dict(job["kwargs"])
    kw.pop("implant_source", None)
    hx = kw.pop("implant_hex", None)
    if hx:
        kw["implant_bytes"] = bytes.fromhex(hx)
    t0 = time.time()
    r = world.run_cell(job["cell"], TIMING_SEED, tier=job["tier"], **kw)
    s = r["summary"]
    return {"h": job["h"], "key": job["key"], "arm": job["arm"], "tier": job["tier"],
            "wall_s": round(time.time() - t0, 2), "epochs_run": s["epochs_run"],
            "slices": s["slices"]}


def jobs():
    import manifest as M
    out = []
    for b in M.h1_bundles(1):
        for a in b["arms"]:
            out.append(dict(a, h="H1", key="H1"))
    h2, _ = M.h2_bundles(1)
    for b in h2:
        for a in b["arms"]:
            out.append(dict(a, h="H2", key=b["specimen"]))
    for b in M.h3_bundles(1):
        for a in b["arms"]:
            out.append(dict(a, h="H3", key=b["source_specimen"]))
    for b in M.h4_bundles(1):
        for a in b["arms"]:
            out.append(dict(a, h="H4", key=b["block"]))
    return out


def main():
    J = jobs()
    # longest-expected first so the pool does not end on a straggler
    order = {"L": 0, "M": 1, "S": 2}
    J.sort(key=lambda j: order[j["tier"]])
    t0 = time.time()
    with mp.Pool(WORKERS) as pool:
        res = pool.map(_run, J, chunksize=1)
    per = {}
    for h in ("H1", "H2", "H3", "H4"):
        rs = [r for r in res if r["h"] == h]
        per[h] = {"runs_timed": len(rs), "mean_wall_s": round(sum(r["wall_s"] for r in rs) / len(rs), 2),
                  "max_wall_s": max(r["wall_s"] for r in rs)}
    out = {"workers": WORKERS, "timing_seed": TIMING_SEED, "elapsed_s": round(time.time() - t0, 1),
           "per_hypothesis": per, "runs": res}
    (HERE / "S4_TIMING.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(per, indent=1), "elapsed", out["elapsed_s"])


if __name__ == "__main__":
    main()
