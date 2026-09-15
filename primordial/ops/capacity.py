"""F-R5-5 (round 5): the CPU capacity probe. Concurrency is chosen from measurement, by a rule fixed
before data (SWARM_R5 O3, O9).

Workload: a pilot-sized REAL M2 baseline run seed -- metric.baseline.baseline_run on w13
(gen_seed 13, train128_held64, rng_family 4200, batch 128), gens sized by a k=1 calibration to ~TARGET_S.
Each copy is its own process with OMP/NUMBA threads fixed in its environment before import, a distinct
run seed (distinct archive key, per G 1789467858105-0) and a tmp elites dir; it JIT-warms, waits for
the go signal, then runs timed.

Grid k in {1, 2, 3, 4, 6, 8}, threads per worker floor(16 / k) capped at 8. Rule (O3):
  k* = the largest k such that for every grid step j <= k:
       throughput(j) >= 1.15 x throughput(previous step)  AND  p95 wall(j) <= 1.5 x p95 wall(1)
       AND no job errors.
The probe stops at the first failing step (O9). A k=1 error means no profile (INSTRUMENT_FAIL).
Measured per step: aggregate units/s, per-job walls (p95, stdev), CPU utilisation, peak RSS,
context switches, archive-Redis CPU and disk I/O deltas.

Output: rows primordial/ledger/rows/F/NODE_CAPACITY_PROFILE_R5.jsonl, the JSON profile beside it
(both committed), and pm:capacity:profile on the bus (fabric/broker.py reads it).

    python -m primordial.ops.capacity probe          # announce `bus burst` first; <= 15 min wall
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
GRID = (1, 2, 3, 4, 6, 8)
HOST_THREADS = 16
THREAD_CAP = 8
GAIN = 1.15
P95_LIMIT = 1.5
TARGET_S = 20.0
BUDGET_S = 14 * 60.0
GEN_SEED, PRESSURE, FAMILY, BATCH = 13, "train128_held64", 4200, 128
ARCHIVE_URL = "redis://127.0.0.1:6394/0"
PROFILE_KEY = "pm:capacity:profile"
EXP = "NODE_CAPACITY_PROFILE_R5"
OUT = ROOT / "primordial" / "ledger" / "rows" / "F"


def threads_for(k: int) -> int:
    return min(THREAD_CAP, HOST_THREADS // k)


def p95(xs) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, math.ceil(0.95 * len(xs)) - 1)]


def rule(steps: list[dict]) -> dict:
    """steps: grid order, each {k, throughput, p95_wall_s, errors}. -> {k_star, threads, passed, failed_at, why}."""
    if not steps or steps[0]["errors"]:
        return {"k_star": None, "threads": None, "passed": [], "failed_at": steps[0]["k"] if steps else None,
                "why": "INSTRUMENT_FAIL: k=1 missing or errored"}
    base, passed = steps[0], [steps[0]["k"]]
    for prev, s in zip(steps, steps[1:]):
        why = []
        if s["errors"]:
            why.append(f"errors={s['errors']}")
        if not s["throughput"] >= GAIN * prev["throughput"]:
            why.append(f"throughput {s['throughput']:.4g} < {GAIN} x {prev['throughput']:.4g} (k={prev['k']})")
        if not s["p95_wall_s"] <= P95_LIMIT * base["p95_wall_s"]:
            why.append(f"p95 wall {s['p95_wall_s']:.3f} > {P95_LIMIT} x {base['p95_wall_s']:.3f}")
        if why:
            return {"k_star": passed[-1], "threads": threads_for(passed[-1]), "passed": passed,
                    "failed_at": s["k"], "why": "; ".join(why)}
        passed.append(s["k"])
    return {"k_star": passed[-1], "threads": threads_for(passed[-1]), "passed": passed, "failed_at": None,
            "why": "every tested step passed"}


# ------------------------------------------------------------------ one copy (child process)

def copy_main(idx: int, gens: int, go: str, ready: str, warm_gens: int = 2) -> int:
    import psutil
    import redis
    from primordial.metric import baseline as B
    r = redis.Redis.from_url(ARCHIVE_URL)
    with tempfile.TemporaryDirectory() as tmp:
        B.baseline_run(r, GEN_SEED, PRESSURE, 900 + idx, warm_gens, BATCH, tmp, None, None, FAMILY)   # JIT warm
        pathlib.Path(ready).write_text("1", encoding="utf-8")
        while not os.path.exists(go):
            time.sleep(0.005)
        me = psutil.Process()
        c0 = me.cpu_times()
        t0 = time.perf_counter()
        B.baseline_run(r, GEN_SEED, PRESSURE, 100 + idx, gens, BATCH, tmp, None, None, FAMILY)
        wall = time.perf_counter() - t0
        c1 = me.cpu_times()
        mem = me.memory_info().rss
    print(json.dumps({"idx": idx, "wall_s": wall, "cpu_s": (c1.user + c1.system) - (c0.user + c0.system),
                      "gens": gens, "batch": BATCH, "units": gens * BATCH, "rss_mb": round(mem / 2 ** 20, 1),
                      "threads_env": os.environ.get("NUMBA_NUM_THREADS")}))
    return 0


# ------------------------------------------------------------------ one grid step (parent)

def _redis_cpu() -> float | None:
    try:
        import redis
        info = redis.Redis.from_url(ARCHIVE_URL).info("cpu")
        return float(info["used_cpu_sys"]) + float(info["used_cpu_user"])
    except Exception:
        return None


def run_step(k: int, gens: int, timeout_s: float, python: str = sys.executable) -> dict:
    import psutil
    threads = threads_for(k)
    with tempfile.TemporaryDirectory() as sig:
        go = os.path.join(sig, "go")
        env = dict(os.environ, OMP_NUM_THREADS=str(threads), NUMBA_NUM_THREADS=str(threads),
                   MKL_NUM_THREADS=str(threads), PYTHONPATH=str(ROOT))
        procs = []
        for i in range(k):
            ready = os.path.join(sig, f"ready{i}")
            procs.append((subprocess.Popen([python, "-m", "primordial.ops.capacity", "copy", str(i), str(gens), go,
                                            ready], cwd=str(ROOT), env=env, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True), ready))
        t_warm = time.monotonic()
        while not all(os.path.exists(rd) or p.poll() is not None for p, rd in procs):
            if time.monotonic() - t_warm > 180:
                break
            time.sleep(0.05)
        ps = []
        for p, _ in procs:                  # the venv python.exe is a launcher: its child does the work
            try:
                q = psutil.Process(p.pid)
                ps.extend([q] + q.children(recursive=True))
            except psutil.Error:
                pass
        ctx0 = sum(_ctx(q) for q in ps)
        disk0, rcpu0 = psutil.disk_io_counters(), _redis_cpu()
        psutil.cpu_percent(None)
        pathlib.Path(go).write_text("1", encoding="utf-8")
        t0 = time.monotonic()
        utils, rss_peak, ctx1 = [], 0.0, ctx0
        while any(p.poll() is None for p, _ in procs) and time.monotonic() - t0 < timeout_s:
            time.sleep(0.5)
            utils.append(psutil.cpu_percent(None))
            rss = 0.0
            for q in ps:
                try:
                    rss += q.memory_info().rss
                    ctx1 = max(ctx1, 0)
                except psutil.Error:
                    pass
            rss_peak = max(rss_peak, rss)
            cur = sum(_ctx(q) for q in ps)
            ctx1 = max(ctx1, cur)
        elapsed = time.monotonic() - t0
        timed_out = [p for p, _ in procs if p.poll() is None]
        for p in timed_out:
            p.kill()
        disk1, rcpu1 = psutil.disk_io_counters(), _redis_cpu()
        copies, errors = [], []
        for i, (p, _) in enumerate(procs):
            out, err = p.communicate(timeout=30)
            try:
                copies.append(json.loads(out.strip().splitlines()[-1]))
            except (ValueError, IndexError):
                errors.append({"idx": i, "rc": p.returncode, "timeout": p in timed_out, "stderr": (err or "")[-400:]})
    walls = [c["wall_s"] for c in copies]
    units = sum(c["units"] for c in copies)
    span = max(walls) if walls else elapsed
    return {"k": k, "threads": threads, "gens": gens, "batch": BATCH, "copies": copies, "errors": len(errors),
            "error_detail": errors, "throughput": units / span if walls and not errors else 0.0,
            "p95_wall_s": p95(walls) if walls else float("inf"), "mean_wall_s": statistics.fmean(walls) if walls else None,
            "stdev_wall_s": statistics.pstdev(walls) if len(walls) > 1 else 0.0, "elapsed_s": round(elapsed, 3),
            "cpu_util_mean_pct": round(statistics.fmean(utils), 1) if utils else None,
            "cpu_util_max_pct": max(utils) if utils else None, "rss_peak_mb": round(rss_peak / 2 ** 20, 1),
            "ctx_switches": ctx1 - ctx0, "redis_cpu_s": None if rcpu0 is None or rcpu1 is None else round(rcpu1 - rcpu0, 3),
            "disk_read_mb": round((disk1.read_bytes - disk0.read_bytes) / 2 ** 20, 2),
            "disk_write_mb": round((disk1.write_bytes - disk0.write_bytes) / 2 ** 20, 2)}


def _ctx(q) -> int:
    try:
        c = q.num_ctx_switches()
        return c.voluntary + c.involuntary
    except Exception:
        return 0


# ------------------------------------------------------------------ the probe

def probe(step_fn=run_step, grid=GRID, target_s: float = TARGET_S, cal_gens: int = 400, gens: int | None = None,
          budget_s: float = BUDGET_S, log=print) -> dict:
    t_start = time.monotonic()
    cal = None
    if gens is None:
        cal = step_fn(1, cal_gens, 300)
        if cal["errors"] or not cal["copies"]:
            prof = {"exp": EXP, "rule": rule([cal]), "calibration": cal, "steps": [],
                    "profile_status": "INSTRUMENT_FAIL"}
            return prof
        per_gen = cal["copies"][0]["wall_s"] / cal_gens
        gens = max(10, round(target_s / per_gen))
        log(f"[capacity] calibration {cal_gens} gens -> {cal['copies'][0]['wall_s']:.2f}s; gens={gens}")
    steps, untested = [], []
    for k in grid:
        left = budget_s - (time.monotonic() - t_start)
        if left <= 0:
            untested.append(k)
            continue
        base = steps[0]["p95_wall_s"] if steps else target_s
        s = step_fn(k, gens, min(left, max(60.0, 3 * P95_LIMIT * base)))
        steps.append(s)
        log(f"[capacity] k={k} threads={s['threads']} throughput={s['throughput']:.1f} u/s "
            f"p95={s['p95_wall_s']:.2f}s errors={s['errors']} util={s.get('cpu_util_mean_pct')}%")
        verdict = rule(steps)
        if verdict["failed_at"] is not None:                 # O9: stop at the first failing step
            untested = [x for x in grid if x > k]
            break
    verdict = rule(steps)
    return {"exp": EXP, "rule": {"grid": list(grid), "gain": GAIN, "p95_limit": P95_LIMIT,
                                 "threads": "floor(16/k) cap 8", **verdict},
            "k_star": verdict["k_star"], "threads_per_worker": verdict["threads"], "untested": untested,
            "workload": {"fn": "primordial.metric.baseline:baseline_run", "gen_seed": GEN_SEED, "pressure": PRESSURE,
                         "rng_family": FAMILY, "batch": BATCH, "gens": gens, "target_s": target_s,
                         "run_seeds": "100+copy", "warm_run_seeds": "900+copy"},
            "calibration": cal, "steps": steps, "wall_s": round(time.monotonic() - t_start, 1),
            "profile_status": "OK" if verdict["k_star"] else "INSTRUMENT_FAIL", "ts": round(time.time(), 3)}


def from_rows(path, gens_log: dict | None = None) -> dict:
    """Rebuild the profile from committed capacity_step rows (the last run: k=1 starts a run). The rule is
    re-applied to the rows; nothing is re-measured. (06:35: the first probe committed its 3 step rows, then
    crashed writing the profile row -- its `status` key overwrote the row status.)"""
    rows = [json.loads(x) for x in pathlib.Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
    steps = []
    for row in rows:
        if row.get("kind") != "capacity_step":
            continue
        if row["k"] == GRID[0]:
            steps = []
        steps.append({k: v for k, v in row.items() if k not in ("status", "kind", "exp_id")})
    verdict = rule(steps)
    tested = [s["k"] for s in steps]
    untested = [k for k in GRID if k not in tested] if verdict["failed_at"] is not None or len(tested) < len(GRID) else []
    return {"exp": EXP, "rule": {"grid": list(GRID), "gain": GAIN, "p95_limit": P95_LIMIT,
                                 "threads": "floor(16/k) cap 8", **verdict},
            "k_star": verdict["k_star"], "threads_per_worker": verdict["threads"], "untested": untested,
            "workload": {"fn": "primordial.metric.baseline:baseline_run", "gen_seed": GEN_SEED, "pressure": PRESSURE,
                         "rng_family": FAMILY, "batch": BATCH, "gens": steps[0]["gens"] if steps else None,
                         "target_s": TARGET_S, "run_seeds": "100+copy", "warm_run_seeds": "900+copy"},
            "calibration": gens_log, "steps": [], "step_rows_from": str(path), "rebuilt_from_rows": True,
            "profile_status": "OK" if verdict["k_star"] else "INSTRUMENT_FAIL", "ts": round(time.time(), 3)}


def write(prof: dict, r=None, repo=ROOT, host_load=None, out=OUT) -> dict:
    from primordial.fabric.rows import RowWriter, commit_path
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = out / f"{EXP}.jsonl"
    w = RowWriter(rows, EXP, repo=repo)
    for s in prof["steps"]:
        w.write({"kind": "capacity_step", **{k: v for k, v in s.items() if k not in ("copies", "status")},
                 "copy_walls_s": [round(c["wall_s"], 3) for c in s["copies"]],
                 "copy_cpu_s": [round(c["cpu_s"], 3) for c in s["copies"]], "status": "record"})
    w.write({"kind": "capacity_profile", **{k: v for k, v in prof.items() if k not in ("steps", "status")},
             "host_load_before": host_load, "status": "record"})
    w.close(note="(O3 capacity profile)")
    (out / f"{EXP}.json").write_text(json.dumps(dict(prof, host_load_before=host_load), indent=1, sort_keys=True,
                                                default=str) + "\n", encoding="utf-8")
    sha = commit_path(out / f"{EXP}.json", EXP, "(profile JSON)", repo=repo)
    if r is not None and prof.get("k_star"):
        r.set(PROFILE_KEY, json.dumps({"k_star": prof["k_star"], "threads_per_worker": prof["threads_per_worker"],
                                       "exp": EXP, "sha": sha, "ts": prof["ts"]}, sort_keys=True))
    return {"rows": str(rows), "sha": sha}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("copy")
    c.add_argument("idx", type=int)
    c.add_argument("gens", type=int)
    c.add_argument("go")
    c.add_argument("ready")
    p = sub.add_parser("probe")
    p.add_argument("--target-s", type=float, default=TARGET_S)
    p.add_argument("--gens", type=int)
    fr = sub.add_parser("profile-from-rows")
    fr.add_argument("--calibration-json", default="null")
    a = ap.parse_args(argv)
    if a.cmd == "copy":
        return copy_main(a.idx, a.gens, a.go, a.ready)
    from primordial.bus import bus
    r = bus.conn()
    if a.cmd == "profile-from-rows":
        prof = from_rows(OUT / f"{EXP}.jsonl", json.loads(a.calibration_json))
        out = write(prof, r=r)
        print(json.dumps({"k_star": prof["k_star"], "threads": prof["threads_per_worker"],
                          "why": prof["rule"]["why"], **out}, sort_keys=True))
        return 0 if prof["k_star"] else 1
    load = bus.host_load(r)
    prof = probe(target_s=a.target_s, gens=a.gens)
    out = write(prof, r=r, host_load=load)
    print(json.dumps({"k_star": prof.get("k_star"), "threads": prof.get("threads_per_worker"),
                      "why": prof["rule"].get("why"), **out}, sort_keys=True))
    return 0 if prof.get("k_star") else 1


if __name__ == "__main__":
    raise SystemExit(main())
