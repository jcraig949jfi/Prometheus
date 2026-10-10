"""REACH01 generic flight driver (campaign-wide).

Plan: JSON list of {"id": str, "argv": [python-script-relative-to-REACH01, args...], "out": path} where any "{out}"
inside argv is replaced by the unit's out path (relative paths are relative to OUTDIR). Units whose out exists are
skipped (resume-safe). Runs up to --jobs concurrently; no new unit starts after --wall-cap seconds; with --drain,
running units finish. Ledger: OUTDIR/ledger_<plan name>.jsonl. Optional --not-before ISO time and --deadline ISO time
(no unit starts after the campaign deadline).
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def now():
    return dt.datetime.now(dt.timezone.utc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("outdir")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--wall-cap", type=float, required=True)
    ap.add_argument("--drain", action="store_true")
    ap.add_argument("--not-before", default=None)
    ap.add_argument("--deadline", default="2026-10-13T09:23:11+00:00")
    a = ap.parse_args()
    if a.not_before and now() < dt.datetime.fromisoformat(a.not_before.replace("Z", "+00:00")):
        print("not_before not reached", file=sys.stderr)
        return 2
    deadline = dt.datetime.fromisoformat(a.deadline.replace("Z", "+00:00"))
    plan = json.load(open(a.plan))
    os.makedirs(a.outdir, exist_ok=True)
    led = open(os.path.join(a.outdir, "ledger_%s.jsonl" % os.path.splitext(os.path.basename(a.plan))[0]), "a")

    def log(**kw):
        kw["utc"] = now().strftime("%Y-%m-%dT%H:%M:%SZ")
        led.write(json.dumps(kw) + "\n")
        led.flush()

    log(event="flight_start", plan=a.plan, units=len(plan), jobs=a.jobs)
    t0 = time.time()
    q = []
    for u in plan:
        out = u["out"] if os.path.isabs(u["out"]) else os.path.join(a.outdir, u["out"])
        if not os.path.exists(out):
            q.append((u, out))
    run = {}
    while q or run:
        while q and len(run) < a.jobs and time.time() - t0 < a.wall_cap and now() < deadline:
            u, out = q.pop(0)
            argv = [x.replace("{out}", out).replace("{outdir}", a.outdir) for x in u["argv"]]
            argv[0] = os.path.join(HERE, argv[0])
            ef = open(out + ".stderr", "w")
            run[u["id"]] = (subprocess.Popen([sys.executable] + argv, stdout=ef, stderr=ef), ef, time.time())
            log(event="launch", id=u["id"])
        if not run and (time.time() - t0 >= a.wall_cap or now() >= deadline):
            break
        if (time.time() - t0 >= a.wall_cap or now() >= deadline) and not a.drain:
            for uid, (p, f, _s) in run.items():
                p.terminate()
                f.close()
                log(event="terminated_cap", id=uid)
            run = {}
            break
        for uid in [k for k, (p, _f, _s) in run.items() if p.poll() is not None]:
            p, f, st = run.pop(uid)
            f.close()
            log(event="done", id=uid, rc=p.returncode, seconds=round(time.time() - st, 1))
        time.sleep(2)
    log(event="flight_end", seconds=round(time.time() - t0, 1), not_started=len(q))
    return 0


if __name__ == "__main__":
    sys.exit(main())
