"""Liveness = state change, not process aliveness.

The 43-daemon fleet died in 45 minutes and went unnoticed for 24 days while its cron
mailed confabulated status 6x/day. It had PIDs. It had heartbeats. Both lied.

What cannot lie: did anything downstream CHANGE because this worker ran? A worker whose
output nothing consumes is observationally identical to a dead one -- which is exactly why
nobody noticed. So liveness here is defined as consumed output over a window, and a worker
with zero consumed output is DEAD whether or not a process is running.

    python engine/driver/liveness.py --days 7
"""
from __future__ import annotations
import argparse, json, subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def consumption_events(days: int) -> Counter:
    """Count state-changing commits per lane. A commit that only ADDS documents is not
    consumption; a commit that changes a queue, registry, or doctrine file is."""
    since = f"--since={days}.days.ago"
    out = subprocess.run(["git", "log", since, "--name-only", "--pretty=format:%H"],
                         capture_output=True, text=True, cwd=str(ROOT)).stdout
    lanes = Counter()
    for path in out.splitlines():
        p = path.strip()
        if not p or len(p) == 40:  # commit hash line
            continue
        if p.startswith("engine/queues/"):
            lanes["queue_state"] += 1
        elif "registry" in p:
            lanes["registry"] += 1
        elif p.startswith("aporia/doctrine/"):
            lanes["doctrine"] += 1
        elif "/docs/FINDING_" in p or "/FINDING_" in p:
            lanes["findings"] += 1
    return lanes


def emitted(days: int) -> int:
    since = f"--since={days}.days.ago"
    out = subprocess.run(["git", "log", since, "--diff-filter=A", "--name-only",
                          "--pretty=format:"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout
    return len([l for l in out.splitlines() if l.strip()])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    a = ap.parse_args()

    lanes = consumption_events(a.days)
    consumed = sum(lanes.values())
    em = emitted(a.days)
    ratio = consumed / em if em else 0.0

    print(f"window: {a.days}d")
    print(f"emitted (new files):        {em}")
    print(f"consumed (state changes):   {consumed}  {dict(lanes)}")
    print(f"consumed/emitted:           {ratio:.2f}")
    verdict = ("ALIVE" if consumed > 0 else
               "DEAD -- no downstream state changed; a running process would prove nothing")
    print(f"verdict: {verdict}")
    if ratio and ratio < 0.15:
        print("WARNING: production outpacing consumption -- the 442-report shape. "
              "Stop producing until this recovers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
