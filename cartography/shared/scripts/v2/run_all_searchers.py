"""
Run All Searchers — Launch diverse exploration processes in parallel.
=====================================================================
Kicks off multiple searchers, each exploring different parts of the
mathematical landscape. All feed the shadow tensor. Run and walk away.

Usage:
    python run_all_searchers.py                    # 1 hour default
    python run_all_searchers.py --duration 120     # 2 hours
"""

import argparse
import json
import subprocess
import sys
import time
import os
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).resolve().parent
V2_DIR = SCRIPTS_DIR
SHARED_DIR = SCRIPTS_DIR.parent

# All searcher configs: (name, command, description)
SEARCHERS = [
    (
        "EVOLVER-50gen",
        [sys.executable, str(V2_DIR / "layer4" / "search_evolver.py"),
         "--generations", "50", "--provider", "deepseek"],
        "Evolutionary search function synthesis — 50 generations"
    ),
    (
        "BATTERY-SWEEP",
        [sys.executable, str(V2_DIR / "battery_sweep.py")],
        "Full battery sweep across all v2 layer outputs"
    ),
    (
        "EXPECTED-BRIDGES",
        [sys.executable, str(V2_DIR / "layer2" / "expected_bridges.py")],
        "12 theory-predicted bridges through the battery"
    ),
    (
        "FINDSTAT-PROBE",
        [sys.executable, str(V2_DIR / "layer2" / "findstat_probes.py")],
        "Cold territory: 10 zero-test FindStat pairs"
    ),
    (
        "GRAPH-INVARIANTS",
        [sys.executable, str(V2_DIR / "layer2" / "graph_invariants.py")],
        "53 graphs with degree sequence battery testing"
    ),
    (
        "AST-BRIDGES",
        [sys.executable, str(V2_DIR / "layer2" / "ast_bridge.py")],
        "Formula structural comparison across Fungrim modules"
    ),
    (
        "ROOT-PROBES",
        [sys.executable, str(V2_DIR / "layer2" / "root_probes.py")],
        "Polynomial root distributions: knot vs EC Sato-Tate"
    ),
    (
        "NOVELTY-REFRESH",
        [sys.executable, str(V2_DIR / "layer3" / "novelty_scorer.py"), "--top", "50"],
        "Refresh novelty scores with latest shadow tensor"
    ),
    (
        "ASYMPTOTIC-AUDIT",
        [sys.executable, str(V2_DIR / "layer1" / "asymptotic_auditor.py")],
        "Full audit of 1534 extended sequences"
    ),
]


def main():
    parser = argparse.ArgumentParser(description="Run All Searchers")
    parser.add_argument("--duration", type=int, default=60,
                        help="Max duration in minutes (default: 60)")
    parser.add_argument("--skip", nargs="*", default=[],
                        help="Searcher names to skip")
    args = parser.parse_args()

    print("=" * 70)
    print(f"  CHARON SEARCHER FLEET — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Duration limit: {args.duration} minutes")
    print(f"  Searchers: {len(SEARCHERS)}")
    print("=" * 70)

    # Launch all searchers
    processes = []
    log_dir = SCRIPTS_DIR.parents[2] / "convergence" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    for name, cmd, desc in SEARCHERS:
        if name in args.skip:
            print(f"  SKIP  {name}")
            continue

        log_file = log_dir / f"searcher_{name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        print(f"  START {name:20s} — {desc}")

        try:
            with open(log_file, "w") as lf:
                p = subprocess.Popen(
                    cmd,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    cwd=str(SHARED_DIR),
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                )
                processes.append((name, p, log_file, time.time()))
        except Exception as e:
            print(f"  ERROR {name}: {e}")

    print(f"\n  {len(processes)} searchers launched.")
    print(f"  Logs: {log_dir}")
    print(f"  Max runtime: {args.duration} minutes")
    print(f"  All output goes to log files. This process monitors and reports.")
    print("=" * 70)

    # Monitor loop
    deadline = time.time() + args.duration * 60
    completed = set()

    while time.time() < deadline:
        all_done = True
        for name, p, log_file, t0 in processes:
            if name in completed:
                continue
            ret = p.poll()
            if ret is not None:
                elapsed = time.time() - t0
                status = "OK" if ret == 0 else f"EXIT {ret}"
                print(f"  DONE  {name:20s} [{status}] {elapsed:.0f}s — {log_file.name}")
                completed.add(name)
            else:
                all_done = False

        if all_done:
            break

        time.sleep(30)  # Check every 30 seconds

    # Kill anything still running
    still_running = []
    for name, p, log_file, t0 in processes:
        if name not in completed:
            still_running.append(name)
            p.terminate()

    if still_running:
        print(f"\n  TIMEOUT: killed {len(still_running)} still running: {', '.join(still_running)}")

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  FLEET SUMMARY")
    print(f"  Completed: {len(completed)}/{len(processes)}")
    print(f"  Timed out: {len(still_running)}")
    print(f"  Total time: {(time.time() - processes[0][3]):.0f}s" if processes else "  No processes")

    # Tail the last few lines of each log
    print(f"\n  === Last lines from each searcher ===")
    for name, p, log_file, t0 in processes:
        if log_file.exists():
            try:
                lines = log_file.read_text(errors="ignore").strip().split("\n")
                last = lines[-3:] if len(lines) >= 3 else lines
                print(f"\n  [{name}]")
                for l in last:
                    print(f"    {l[:100]}")
            except Exception:
                print(f"\n  [{name}] (could not read log)")

    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    main()
