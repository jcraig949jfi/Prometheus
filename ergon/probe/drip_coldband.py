"""Drip-fed second-family cold-band reads on the free lane. Zero spend.

The free NVIDIA lane enforces a small PER-MODEL daily quota on long-output calls (~40/day
measured: nemotron died at 43 ok). Bulk runs collide with it; a scheduled drip does not.
Each invocation sends a SMALL batch per candidate, appends to a persistent ledger, and stops
the moment the lane starts refusing. When a candidate's ledger reaches full coverage
(200 tasks x 2 reps, ok-status), the band read is computed and written atomically.

Candidates and selection rule are PRE-DECLARED (exit reviews, both): order =
[nemotron-super-49b-v1.5, nemotron-super-49b-v1, gpt-oss-120b]; selected = first in order
whose cold-band read on the M30 manifest passes the full band (point in [0.35, 0.60] AND
movable >= 0.30) on its own host pin. Running all three concurrently and applying the order
rule at evaluation is not forking — the rule is fixed before any data.

Schedule:  schtasks /create /tn PrometheusColdbandDrip /tr F:\\Prometheus\\ergon\\run_coldband_drip.cmd /sc HOURLY /mo 8
Remove:    schtasks /delete /tn PrometheusColdbandDrip /f
"""
import json
import math
import os
import pathlib
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ergon.probe.solver import call
from ergon.probe.extract import extract_numeric

CANDIDATES = ("nvidia:nemotron-super-49b-v1.5", "nvidia:nemotron-super-49b-v1",
              "nvidia:gpt-oss-120b")
# Was 12, sized to stay under a presumed ~40/day 429 wall. MEASURED 2026-08-22: across all
# three candidates the drip has logged ZERO 429s and zero 402s — the wall it was throttling
# for never appeared, while the real constraint (HTTP504 timeouts, 83-96% on two candidates)
# went unaddressed. The 429-stop below is already a safe self-limiter, so let the batch probe
# for the real wall instead of assuming one: worst case it stops on the first 429, exactly as
# designed. deepseek-v4-flash on this same lane served 1,058 calls in a day.
BATCH_PER_CANDIDATE = 80
MAX_TOK, TIMEOUT = 8192, 420
BAND, MOVABLE_FLOOR = (0.35, 0.60), 0.30
MAN = ROOT / "ergon/probe/manifests/nearmiss_mix-M30_manifest_n200.jsonl"
DRIP_DIR = ROOT / "ergon/probe/ledgers/coldband_drip"

rows = [json.loads(l) for l in MAN.read_text(encoding="utf-8").splitlines()]
gold = {r["uid"]: r["gold_int"] for r in rows}
# fixed work order: (rep, task) — rep 1 for all tasks, then rep 2
WORK = [(rep, r) for rep in (1, 2) for r in rows]


def _slug(solver):
    return solver.replace(":", "_").replace(".", "")


def done_keys(led_path):
    if not led_path.exists():
        return set()
    return {(r["rep"], r["uid"]) for r in
            (json.loads(l) for l in led_path.read_text(encoding="utf-8").splitlines())
            if r["status"] == "ok"}


# A cheap probe measured the WRONG WORKLOAD. nemotron-v1.5 answers a 256-token call fine and
# then fails 93% of the real 16k-token calls with HTTP504 — so the probe waved through a
# candidate that burned six hours to collect one row. Same error class as every other one this
# week: measure one thing, license another. The fix is not a better probe; it is a circuit
# breaker on the ACTUAL work, which cannot be fooled because it is the work.
MIN_ATTEMPTS_BEFORE_BREAK = 8     # give a candidate a fair sample before judging it
BREAK_OK_RATE = 0.5               # below this, the lane is not serving this model right now


def probe(solver):
    """Kept as a liveness check only — it proves the endpoint answers at all, and costs one
    short call. It deliberately does NOT license the batch: see the circuit breaker in drip(),
    which judges the real workload. A candidate that fails here is certainly down; one that
    passes here may still be unusable, which is exactly what happened.
    """
    r = call(solver, "What is 17 times 23? Answer with just the number.",
             max_tokens=256, timeout=120)
    return r.status == "ok", r.error_type


def drip(solver):
    led_path = DRIP_DIR / f"{_slug(solver)}.jsonl"
    out_path = DRIP_DIR / f"{_slug(solver)}_bandread.json"
    if out_path.exists():
        return "complete"
    ok, err = probe(solver)
    if not ok:
        return f"skipped-transport-down ({err})"
    have = done_keys(led_path)
    todo = [(rep, r) for rep, r in WORK if (rep, r["uid"]) not in have][:BATCH_PER_CANDIDATE]
    if not todo:
        return finalize(solver, led_path, out_path)

    sent = ok = 0
    with led_path.open("a", encoding="utf-8") as fh:
        for rep, r in todo:
            res = call(solver, r["prompt"], max_tokens=MAX_TOK, timeout=TIMEOUT)
            sent += 1
            rec = {"solver": solver, "uid": r["uid"], "rep": rep, "status": res.status,
                   "error_type": res.error_type, "latency_s": res.latency_s,
                   "extracted_int": extract_numeric(res.text if res.status == "ok" else None).value,
                   "attempt_text": (res.text or "").strip()[:4000],
                   "derives_from_gold": False,
                   "ts_utc": res.ts_utc, "host": res.host, "executor": res.executor}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
            if res.status == "ok":
                ok += 1
            elif res.error_type in ("HTTP429", "HTTP402"):
                # quota wall: stop immediately, save the rest of today's batch for the lane
                break
            # circuit breaker on the real workload: abandon a degraded candidate after a fair
            # sample rather than grinding 420s timeouts for hours and starving its siblings.
            if sent >= MIN_ATTEMPTS_BEFORE_BREAK and (ok / sent) < BREAK_OK_RATE:
                print(f"  {solver}: abandoning this firing — {ok}/{sent} ok on the real "
                      f"workload (floor {BREAK_OK_RATE:.0%}); will retry next firing")
                break
            time.sleep(3)
    if not (DRIP_DIR / f"{_slug(solver)}.jsonl").exists():
        return "idle"
    have = done_keys(led_path)
    if len(have) >= len(WORK):
        return finalize(solver, led_path, out_path)
    return f"progress {len(have)}/{len(WORK)} (+{ok}/{sent} this batch)"


def finalize(solver, led_path, out_path):
    recs = [json.loads(l) for l in led_path.read_text(encoding="utf-8").splitlines()]
    best = {}
    for r in recs:              # last ok attempt per (rep, uid)
        if r["status"] == "ok":
            best[(r["rep"], r["uid"])] = r
    r1 = {u: best.get((1, u)) for u in gold}
    r2 = {u: best.get((2, u)) for u in gold}
    n = len(gold)
    succ = [r1[u] is not None and r1[u]["extracted_int"] == gold[u] for u in gold]
    acc = sum(succ) / n
    disc = sum(1 for u in gold if r1[u] and r2[u]
               and (r1[u]["extracted_int"] == gold[u]) != (r2[u]["extracted_int"] == gold[u]))
    movable = disc / n
    z = 1.959964
    se = math.sqrt(max(acc * (1 - acc), 1e-12) / n)
    lo, hi = max(0.0, acc - z * se), min(1.0, acc + z * se)
    band_read = {
        "solver": solver, "n": n,
        "point_estimate": round(acc, 4),
        "manifest_interval_95": [round(lo, 4), round(hi, 4)],
        "point_in_band": BAND[0] <= acc <= BAND[1],
        "movable_share": round(movable, 4),
        "dispersion_term_passes": movable >= MOVABLE_FLOOR,
        "full_band_passes": (BAND[0] <= acc <= BAND[1]) and movable >= MOVABLE_FLOOR,
        "leveling_verdict": ("LEVELED" if (BAND[0] <= acc <= BAND[1]
                                           and movable >= MOVABLE_FLOOR) else "NOT-LEVELED"),
        "collected_by": "drip (quota-respecting; batches of %d)" % BATCH_PER_CANDIDATE,
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    tmp = out_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(band_read, indent=2), encoding="utf-8")
    os.replace(tmp, out_path)
    return "FINALIZED: " + band_read["leveling_verdict"]


def _pid_alive(pid):
    """Windows PID liveness. NEVER os.kill(pid, 0) here -- that terminates on Windows."""
    import ctypes
    h = ctypes.windll.kernel32.OpenProcess(0x1000, 0, pid)
    if not h:
        return False
    code = ctypes.c_ulong()
    ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
    ctypes.windll.kernel32.CloseHandle(h)
    return bool(ok) and code.value == 259


def main():
    DRIP_DIR.mkdir(parents=True, exist_ok=True)
    # With BATCH_PER_CANDIDATE at 80 and ~78s/call, one firing can run for hours -- longer
    # than the 3h schedule. Without a lock, firings overlap and double-spend the very quota
    # the drip exists to conserve. Stale locks (dead holder, or >6h) are taken over.
    lock = DRIP_DIR / "drip.lock"
    if lock.exists():
        age_h = (time.time() - lock.stat().st_mtime) / 3600
        pid = lock.read_text(encoding="utf-8").strip()
        if age_h < 6 and pid.isdigit() and _pid_alive(int(pid)):
            print("another drip firing is still running -- skipped")
            return
    lock.write_text(str(os.getpid()), encoding="utf-8")
    try:
        _drip_all()
    finally:
        lock.unlink(missing_ok=True)


def _drip_all():
    DRIP_DIR.mkdir(parents=True, exist_ok=True)
    log = DRIP_DIR / "drip_log.jsonl"
    for solver in CANDIDATES:
        try:
            status = drip(solver)
        except Exception as e:            # noqa: BLE001 — a drip must never kill its siblings
            status = f"error {type(e).__name__}: {e}"
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                 "solver": solver, "status": status}) + "\n")
        print(solver, "->", status)


if __name__ == "__main__":
    main()
