"""Run R1 of the frozen T004 benchmark: the Arm N points and Arm R, in the preregistered order, each through the
FROZEN harness (../bench.py, unmodified), recording M2's CPU load before every point (the operator started
experiments on M2 at ~09:30Z; Pan's record 140d95927). Arm S is NOT run here: it is deferred until M2 is idle
(DEVIATION recorded in RUN_LOG.jsonl and the receipt). Procedural tooling only; it computes nothing.
    EW_DB_HOST=192.168.1.202 python run_r1.py
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent / "bench.py"
CAL = json.loads((HERE / "calibration.json").read_text(encoding="utf-8"))["iters_for_D"]
POINTS = [("N", 60, 4, 360, 0), ("N", 30, 4, 360, 0), ("N", 10, 4, 360, 0), ("N", 3, 4, 360, 0), ("N", 1, 4, 360, 0),
          ("N", 30, 1, 360, 0), ("N", 30, 2, 360, 0), ("R", 30, 4, 600, 3)]


def m2_cpu():
    ps = ("$c=(Get-Counter '\\Processor(_Total)\\% Processor Time' -SampleInterval 2 -MaxSamples 5).CounterSamples;"
          "($c | Measure-Object -Property CookedValue -Average).Average")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60)
    try:
        return round(float(r.stdout.strip().splitlines()[-1]), 1)
    except Exception:
        return None


def log(entry):
    entry["at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(HERE / "RUN_LOG.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry), flush=True)


def main():
    log({"event": "deviation", "detail": "Arm S deferred until M2 is idle (operator experiments on M2 since ~09:30Z); "
                                         "spectrex5:cpu12 not held during the node arms (M2 footprint: the coordinator "
                                         "loop and validation replays, about one core)"})
    for arm, d, wpn, wall, kills in POINTS:
        log({"event": "point_start", "arm": arm, "D": d, "wpn": wpn, "m2_cpu_pct_before": m2_cpu()})
        cmd = [sys.executable, str(BENCH), "point", "--arm", arm, "--D", str(d), "--wpn", str(wpn), "--wall-s", str(wall),
               "--iters", str(CAL[str(d)]), "--run-id", "R1", "--out", str(HERE)]
        if kills:
            cmd += ["--kills", str(kills)]
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True)
        tail = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()][-3:]
        log({"event": "point_end", "arm": arm, "D": d, "wpn": wpn, "exit": r.returncode,
             "seconds": round(time.time() - t0, 1), "m2_cpu_pct_after": m2_cpu(), "tail": tail})
        if r.returncode != 0:
            log({"event": "stop", "detail": "harness failure at this point; an execution failure, not a result"})
            break


if __name__ == "__main__":
    main()
