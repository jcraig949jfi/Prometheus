"""Budget enforcement (backlog F13): CPU-seconds per cohort against the operator's split.

Split, round-versioned (the conductor enforces it and never chooses it):
  SHARES_R2  B 40 / C 25 / D 20 / E 15   operator message 04 s3; replay-round2 always uses it
  SHARES_R4  B 35 / C 25 / D 25 / E 15   operator message 12 (SWARM_R4 s1); default for `report`
A report row records the round and the shares it was judged against.

Source of truth for a live round: builder F's warm worker ledger. Every finished job XADDs
{job_id, status, cpu_s, wall_s, ...} to pm:jobs:<L>:done, and its spec (exp_id, fn,
ttl_cpu_s) sits on pm:jobs:<L>. Jobs are placed in an epoch window by the done entry's
stream-id time. A job that died carries cpu_s null: it is counted, and its CPU is reported
unknown, never guessed.

Verdict per cohort, per epoch:
  OVER            its share of the cohort CPU total exceeds its split share; the cohort
                  (and A) get one bus warning per epoch
  WITHIN          at or under its share
  INDETERMINATE   total cohort CPU < MIN_TOTAL_CPU_S (shares of a few seconds are noise), or
                  some cohort is unmetered (a replay from rows that carry no CPU field)

    python -m primordial.score.budget report --epoch N --since TS [--until TS] [--warn] [--write]
    python -m primordial.score.budget replay-round2 [--write]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

from primordial.score.progress import rows_of
from primordial.score.round2 import ROOT, ROUND2_START

SHARES_R2 = {"B": 0.40, "C": 0.25, "D": 0.20, "E": 0.15}
SHARES_R4 = {"B": 0.35, "C": 0.25, "D": 0.25, "E": 0.15}
SHARES_BY_ROUND = {"r2": SHARES_R2, "r4": SHARES_R4}
DEFAULT_ROUND = "r4"
SHARES = SHARES_BY_ROUND[DEFAULT_ROUND]
MIN_TOTAL_CPU_S = 60.0
JOBS, DONE = "pm:jobs:{}", "pm:jobs:{}:done"
WARNED = "pm:budget:warned:{}:{}"
CPU_FIELDS = ("cpu_s", "client_cpu_s", "train_cpu_s")      # first present per row; wall time is not CPU
OUT = ROOT / "primordial" / "ledger" / "rows" / "H" / "F13-budget.jsonl"
INF = float("inf")


def _id_ts(mid: str) -> float:
    return int(mid.split("-")[0]) / 1000.0


def job_ledger(r, lanes=tuple(SHARES), window=(0.0, INF)) -> dict:
    """Per lane: cpu_s (known), jobs, status counts, jobs with unknown CPU, CPU per exp_id."""
    out = {}
    for lane in lanes:
        specs = {f.get("job_id"): f for _, f in r.xrange(JOBS.format(lane))}
        led = {"cpu_s": 0.0, "jobs": 0, "status": {}, "cpu_unknown_jobs": 0, "by_exp": {}}
        for mid, f in r.xrange(DONE.format(lane)):
            if not window[0] <= _id_ts(mid) < window[1]:
                continue
            d = json.loads(f["json"])
            led["jobs"] += 1
            led["status"][d.get("status")] = led["status"].get(d.get("status"), 0) + 1
            exp = specs.get(d.get("job_id"), {}).get("exp_id", "?")
            if d.get("cpu_s") is None:
                led["cpu_unknown_jobs"] += 1
                continue
            led["cpu_s"] += float(d["cpu_s"])
            led["by_exp"][exp] = round(led["by_exp"].get(exp, 0.0) + float(d["cpu_s"]), 3)
        led["cpu_s"] = round(led["cpu_s"], 3)
        led["metered"] = True
        out[lane] = led
    return out


def rows_ledger(root=ROOT, lanes=tuple(SHARES), window=(ROUND2_START, INF)) -> dict:
    """Replay from committed rows: CPU only where a row recorded it. Unmetered lanes stay unmetered."""
    out = {}
    for lane in lanes:
        rows = rows_of(root, lane, window)
        cpu, n_cpu = 0.0, 0
        for row in rows:
            v = next((row[k] for k in CPU_FIELDS if isinstance(row.get(k), (int, float))
                      and not isinstance(row.get(k), bool)), None)
            if v is not None:
                cpu += float(v)
                n_cpu += 1
        out[lane] = {"cpu_s": round(cpu, 3), "rows": len(rows), "rows_with_cpu": n_cpu, "metered": n_cpu > 0}
    return out


def report(ledger: dict, shares=SHARES, min_total=MIN_TOTAL_CPU_S) -> dict:
    total = round(sum(v["cpu_s"] for v in ledger.values()), 3)
    unmetered = sorted(k for k, v in ledger.items() if not v.get("metered", True))
    if unmetered:
        why = f"unmetered cohorts {unmetered}"
    elif total < min_total:
        why = f"cohort CPU total {total} s < {min_total} s"
    else:
        why = ""
    lanes = {}
    for lane, share in shares.items():
        v = ledger.get(lane, {"cpu_s": 0.0})
        actual = v["cpu_s"] / total if total > 0 else 0.0
        verdict = "INDETERMINATE" if why else ("OVER" if actual > share else "WITHIN")
        lanes[lane] = {"cpu_s": v["cpu_s"], "share": share, "actual": round(actual, 4),
                       "over_cpu_s": round(v["cpu_s"] - share * total, 3), "verdict": verdict}
    return {"total_cpu_s": total, "why_indeterminate": why, "lanes": lanes}


def warn(rep: dict, epoch: int, r=None) -> list[str]:
    """One bus warning per OVER cohort per epoch (deduplicated in Redis). -> lanes warned now."""
    from primordial.bus import bus
    r = r or bus.conn()
    warned = []
    for lane, v in rep["lanes"].items():
        if v["verdict"] != "OVER" or not r.set(WARNED.format(epoch, lane), f"{time.time():.3f}", nx=True, ex=86400):
            continue
        bus.post("note", f"BUDGET WARNING epoch {epoch}: cohort {lane} used {v['actual']:.1%} of cohort CPU "
                         f"(share {v['share']:.0%})",
                 json.dumps({"epoch": epoch, "lane": lane, **v, "total_cpu_s": rep["total_cpu_s"]}),
                 to=f"{lane},A", r=r)
        warned.append(lane)
    return warned


def _write(row: dict) -> None:
    from primordial.fabric.rows import RowWriter
    with RowWriter(OUT, "F13-budget", commit_every_s=10**9) as w:
        w.write({"status": "record", **row})


def _print(rep: dict) -> None:
    print(f"total cohort CPU {rep['total_cpu_s']} s {rep['why_indeterminate']}")
    for lane, v in rep["lanes"].items():
        print(f"  {lane} cpu {v['cpu_s']:10.3f} s  actual {v['actual']:.3f}  share {v['share']:.2f}  {v['verdict']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("report")
    rp.add_argument("--epoch", type=int, required=True)
    rp.add_argument("--since", type=float, required=True)
    rp.add_argument("--until", type=float, default=INF)
    rp.add_argument("--warn", action="store_true")
    rp.add_argument("--write", action="store_true")
    rp.add_argument("--round", choices=sorted(SHARES_BY_ROUND), default=DEFAULT_ROUND)
    r2 = sub.add_parser("replay-round2")
    r2.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "report":
        from primordial.bus import bus
        r = bus.conn()
        shares = SHARES_BY_ROUND[a.round]
        led = job_ledger(r, window=(a.since, a.until))
        rep = report(led, shares)
        print(f"round {a.round}")
        _print(rep)
        warned = warn(rep, a.epoch, r) if a.warn else []
        if warned:
            print("warned", warned)
        if a.write:
            _write({"kind": "budget_report", "source": "worker_done_streams", "epoch": a.epoch, "round": a.round,
                    "shares": shares, "window": [a.since, None if a.until == INF else a.until], "ledger": led,
                    **rep, "warned": warned})
    else:
        led = rows_ledger()
        rep = report(led, SHARES_R2)
        _print(rep)
        if a.write:
            _write({"kind": "budget_report", "source": "round2_rows_replay", "epoch": None, "round": "r2",
                    "shares": SHARES_R2, "window": [ROUND2_START, None], "ledger": led, **rep, "warned": []})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
