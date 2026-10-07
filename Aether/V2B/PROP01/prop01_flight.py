"""PROP01 flight driver (copy of OFFER01/offer01_flight.py with PROP01 unit fields): run a frozen plan of units on the local GPU.

Plan = JSON list of {"id", "regime", "pert", "seed_index", "n", "ticks",
"bin", "late"}. Runs up to --jobs units concurrently as separate processes
(the aeth01 kernel is launch-bound on one RTX 5060 Ti, so concurrent worlds
raise throughput). Skips units whose result file exists (resume). Writes a
JSONL ledger of launches/completions with UTC times. Hard wall cap: no new
unit starts after --wall-cap seconds; running units are allowed to finish
only if --drain, else terminated and recorded INCOMPLETE.

    python er01_flight.py PLAN.json OUTDIR --jobs 4 --wall-cap 3300 [--not-before ISO]
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
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("outdir")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--wall-cap", type=float, required=True)
    ap.add_argument("--not-before", default=None)
    ap.add_argument("--drain", action="store_true")
    a = ap.parse_args(argv)

    if a.not_before:
        nb = dt.datetime.fromisoformat(a.not_before.replace("Z", "+00:00"))
        if dt.datetime.now(dt.timezone.utc) < nb:
            print("not_before %s not reached; refusing to start" % a.not_before, file=sys.stderr)
            return 2

    plan = json.load(open(a.plan, encoding="utf-8"))
    os.makedirs(a.outdir, exist_ok=True)
    ledger = open(os.path.join(a.outdir, "ledger.jsonl"), "a", encoding="utf-8")

    def log(**kw):
        kw["utc"] = now()
        ledger.write(json.dumps(kw) + "\n")
        ledger.flush()
        print(json.dumps(kw), file=sys.stderr, flush=True)

    log(event="flight_start", plan=a.plan, units=len(plan), jobs=a.jobs, wall_cap=a.wall_cap)
    t0 = time.time()
    queue = [u for u in plan
             if not os.path.exists(os.path.join(a.outdir, u["id"] + ".json"))]
    running = {}
    while queue or running:
        while queue and len(running) < a.jobs and time.time() - t0 < a.wall_cap:
            u = queue.pop(0)
            out = os.path.join(a.outdir, u["id"] + ".json")
            cmd = [sys.executable, os.path.join(HERE, "prop01_run.py"),
                   "--law", u["law"],
                   "--seed-index", str(u["seed_index"]), "--n", str(u["n"]),
                   "--warm", str(u["warm"]), "--H", str(u["H"]),
                   "--out", out]
            if u.get("cut_from"):
                cmd += ["--cut-from", os.path.join(a.outdir, u["cut_from"])]
            if u.get("digest_every"):
                cmd += ["--digest-every", str(u["digest_every"])]
            errf = open(os.path.join(a.outdir, u["id"] + ".stderr"), "w")
            running[u["id"]] = (subprocess.Popen(cmd, stderr=errf, stdout=errf), errf, time.time())
            log(event="launch", id=u["id"])
        if not queue and not running:
            break
        if time.time() - t0 >= a.wall_cap and not a.drain:
            for uid, (p, f, st) in running.items():
                p.terminate()
                f.close()
                log(event="terminated_wall_cap", id=uid)
            running = {}
            break
        done = [uid for uid, (p, f, st) in running.items() if p.poll() is not None]
        for uid in done:
            p, f, st = running.pop(uid)
            f.close()
            log(event="done", id=uid, rc=p.returncode, seconds=round(time.time() - st, 1))
        time.sleep(2)
    skipped = len(queue)
    log(event="flight_end", seconds=round(time.time() - t0, 1), not_started=skipped)
    return 0


if __name__ == "__main__":
    sys.exit(main())
