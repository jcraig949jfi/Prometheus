"""G5 / R9 (ADAPT-11): measure the telemetry overhead itself. Ceiling 5%.

A calibration PAIR through the real worker path (Worker.serve -> run_job, RowWriter, done record) on a TEST
database: the same fixed-work CPU job with the per-job resource sampler ON (PM_TELEMETRY=1) and OFF (=0),
interleaved ABBA so drift and neighbour load hit both arms alike. Two sampler intervals:
  production  SAMPLE_EVERY_S = 30 s (what round 8 runs)
  stress      SAMPLE_EVERY_S = 1 s  (30x denser; bounds the cost if the interval is ever tightened)
Metric: the job's own wall inside the child (child_wall_s: what the science pays) and the supervisor wall (wall_s).
overhead_pct = 100 * (median ON / median OFF - 1). Queue fields and beacons are always on in both arms (they are
records written once per grant, not samplers), so the pair isolates the sampler; their per-grant cost is timed
separately (record_cost_ms).

    PM_TEST_DB=15 PM_TAG=... python -c "import sys; from primordial.fabric.telemetry_calibration import main; sys.exit(main(sys.argv[1:]))" --out <json>
(not `-m`: spawned worker children cannot re-import a `-m` __main__ after a respawn -- run 2 died of that)
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import uuid

CEILING_PCT = 5.0


def fixed_work(ctx, units: int = 60, per_unit: int = 120_000):
    """Deterministic pure-Python CPU work; one row per 10 units."""
    acc = 0
    for u in range(units):
        for k in range(per_unit):
            acc = (acc + k * k) % 1_000_003
        if u % 10 == 0:
            ctx.emit({"status": "dev", "kind": "calib", "u": u, "acc": acc})


def _repo() -> pathlib.Path:
    d = pathlib.Path(tempfile.mkdtemp(prefix="pm-calib-"))
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(d), *a], check=True)
    (d / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(d), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(d), "commit", "-q", "-m", "init"], check=True)
    return d


def run(pairs: int, units: int, interval_s: float, url: str) -> dict:
    import redis
    from primordial.fabric import telemetry as TM
    from primordial.fabric import worker as W
    r = redis.Redis.from_url(url, decode_responses=True)
    repo = _repo()
    lane = "Pcal" + uuid.uuid4().hex[:4]
    TM.SAMPLE_EVERY_S = interval_s
    arms = {"on": [], "off": []}
    order = []
    wk = W.Worker(lane, url=url, repo=repo, log=lambda *_: None)
    wk.run_job({"job_id": "warm", "fn": f"{__name__}:fixed_work", "exp_id": "warm", "rows": "rows/w.jsonl",
                "ttl_cpu_s": "600", "kwargs": json.dumps({"units": 5}), "segment": "0", "ts": str(time.time())})
    for p in range(pairs):
        for arm in (("on", "off") if p % 2 == 0 else ("off", "on")):
            os.environ["PM_TELEMETRY"] = "1" if arm == "on" else "0"
            W.submit(lane, f"{__name__}:fixed_work", f"calib-{arm}", "rows/c.jsonl", 600, {"units": units}, r=r)
            (d,) = wk.serve(block_ms=100, max_jobs=1, deadline_s=600)
            assert d["status"] == "ok" and d["telemetry_sampling"] is (arm == "on"), d
            arms[arm].append({"child_wall_s": d["child_wall_s"], "wall_s": d["wall_s"],
                              "samples": len(d["resource_samples"])})
            order.append(arm)
    os.environ.pop("PM_TELEMETRY", None)
    t = time.perf_counter()
    n = 50
    for i in range(n):
        TM.grant(r, lane, {"job_id": f"x{i}"}, TM.queue_fields(0, 1, 0, False), wk.depth())
    record_cost_ms = (time.perf_counter() - t) / n * 1000
    for k in (W.JOBS, W.CONT, W.ROWS, W.DONE, W.WSTATE):
        r.delete(k.format(lane))

    def med(arm, key):
        return statistics.median(x[key] for x in arms[arm])
    out = {"interval_s": interval_s, "pairs": pairs, "units": units, "order": order, "arms": arms,
           "record_cost_ms_per_grant": round(record_cost_ms, 3)}
    for key in ("child_wall_s", "wall_s"):
        on, off = med("on", key), med("off", key)
        out[f"median_on_{key}"], out[f"median_off_{key}"] = round(on, 4), round(off, 4)
        out[f"overhead_pct_{key}"] = round(100 * (on / off - 1), 3)
    return out


def direct_cost(n: int = 200) -> dict:
    """Secondary (reported, not the verdict metric): what one sample costs, timed directly against a busy child,
    and the implied supervisor CPU fraction at the production interval."""
    from primordial.fabric import telemetry as TM
    c = subprocess.Popen([sys.executable, "-c", "while True: pass"])
    time.sleep(0.5)
    t = time.perf_counter()
    got = sum(1 for _ in range(n) if TM.sample_process(c.pid) is not None)
    per = (time.perf_counter() - t) / n
    c.kill()
    assert got == n, f"only {got}/{n} samples succeeded"
    return {"samples": n, "ms_per_sample": round(per * 1000, 4),
            "pct_of_wall_at_30s": round(100 * per / 30.0, 5), "pct_of_wall_at_1s": round(100 * per / 1.0, 4)}


def paired(run_: dict) -> float:
    """Secondary: median over pairs of 100*(on/off - 1), pairs taken in run order (drift-robust)."""
    on, off = run_["arms"]["on"], run_["arms"]["off"]
    return round(statistics.median(100 * (a["child_wall_s"] / b["child_wall_s"] - 1) for a, b in zip(on, off)), 3)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pairs", type=int, default=4)
    ap.add_argument("--units", type=int, default=60)
    a = ap.parse_args(argv)
    from primordial.tests._live import live_url
    url = live_url()
    if url.rstrip("/").endswith("/0"):
        raise SystemExit("refusing db 0 (live bus)")
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    runs = [run(a.pairs, a.units, 30.0, url), run(a.pairs, a.units, 1.0, url)]
    prod = runs[0]
    direct = direct_cost()
    doc = {"what": "R9 telemetry overhead calibration pair (G5 acceptance 4)", "ceiling_pct": CEILING_PCT,
           "code_sha_base": sha, "python": sys.version.split()[0], "host": platform.node(),
           "cpu_count": os.cpu_count(), "measured_at": round(time.time(), 3), "runs": runs,
           "verdict_metric": "overhead_pct_child_wall_s at the production interval (30 s)",
           "production_overhead_pct": prod["overhead_pct_child_wall_s"],
           "within_ceiling": prod["overhead_pct_child_wall_s"] <= CEILING_PCT,
           "direct_cost": direct,
           "paired_median_ratio_pct": {str(x["interval_s"]): paired(x) for x in runs},
           "note": "measured while other builders' test suites shared the host; ABBA interleaving spreads that "
                   "load over both arms. A negative overhead is noise, not a speedup."}
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("production_overhead_pct", "within_ceiling")}),
          [(x["interval_s"], x["overhead_pct_child_wall_s"], x["overhead_pct_wall_s"]) for x in runs])
    return 0


if __name__ == "__main__":
    sys.exit(main())
