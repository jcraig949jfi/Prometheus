#!/usr/bin/env python3
"""
Ergon Monitor — Watch a running overnight session.

Usage:
    python monitor.py                    # auto-finds latest log
    python monitor.py logs/ergon_*.jsonl # specific log
    python monitor.py --watch            # refresh every 30s
"""
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime


def find_latest_log():
    logs_dir = Path(__file__).parent / "logs"
    logs = sorted(logs_dir.glob("ergon_*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def read_log(path):
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def summarize(events):
    run_started = None
    latest_progress = None
    checkpoints = []
    gen_count = 0

    for e in events:
        ev = e.get("event", "")
        if ev == "run_started":
            run_started = e
        elif ev == "progress":
            latest_progress = e
            gen_count += 1
        elif ev == "checkpoint_saved":
            checkpoints.append(e)
        elif ev == "run_complete":
            latest_progress = e  # final report has same fields

    if not run_started:
        print("  No run_started event found.")
        return

    d = run_started.get("data", {})
    total_gens = d.get("n_generations", "?")
    seed = d.get("seed", "?")

    print(f"  Run ID:  {d.get('run_id', '?')}")
    print(f"  Target:  {total_gens} generations x {d.get('n_per_gen', '?')} hyp/gen")
    print(f"  Seed:    {seed}")
    print()

    if not latest_progress:
        print("  No progress events yet. Still warming up.")
        return

    p = latest_progress.get("data", {})
    gen = p.get("gen", 0)
    tested = p.get("total_tested", 0)
    cells = p.get("cells_filled", 0)
    max_d = p.get("max_depth", 0)
    elapsed = p.get("elapsed_s", 0)
    rate = p.get("overall_rate_hyp_s", 0)
    recent_rate = p.get("recent_rate_hyp_s", 0)
    voids = p.get("void_cells", 0)

    pct = (gen / total_gens * 100) if isinstance(total_gens, int) and total_gens > 0 else 0
    elapsed_hr = elapsed / 3600
    if rate > 0 and isinstance(total_gens, int):
        remaining_gens = total_gens - gen
        # estimate ~13.7 hyp per gen (accounts for validation failures)
        remaining_s = (remaining_gens * 13.7) / rate
        eta_hr = remaining_s / 3600
    else:
        eta_hr = 0

    print(f"  Progress:  gen {gen:,}/{total_gens:,} ({pct:.1f}%)")
    print(f"  Tested:    {tested:,} hypotheses")
    print(f"  Elapsed:   {elapsed_hr:.1f} hr")
    print(f"  ETA:       ~{eta_hr:.1f} hr remaining")
    print(f"  Rate:      {rate:.1f} hyp/s overall, {recent_rate:.1f} hyp/s recent")
    print()
    print(f"  Cells:     {cells} filled, {voids} void")
    print(f"  Max depth: {max_d}")

    # Depth distribution
    depths = p.get("depth_distribution", {})
    if depths:
        alive = sum(v for k, v in depths.items() if int(k) > 0)
        dead = depths.get("0", depths.get(0, 0))
        print(f"  Alive:     {alive:,} ({alive/(alive+dead)*100:.1f}%)")
        deep = sum(v for k, v in depths.items() if int(k) >= 10)
        if deep:
            print(f"  Deep (10+): {deep:,}")

    # Top kills
    kills = p.get("top_kill_modes", {})
    if kills:
        print(f"\n  Top kills:")
        for k, v in list(kills.items())[:5]:
            print(f"    {k:35s} {v:,}")

    # Shadow info
    shadow = p.get("shadow", {})
    if shadow:
        print(f"\n  Shadow archive:")
        print(f"    Cells mapped:    {shadow.get('unique_cells_explored', 0):,}")
        print(f"    Domain pairs:    {shadow.get('domain_pairs_explored', 0)}")
        print(f"    Dead zones:      {shadow.get('confirmed_dead_zones', 0)}")
        print(f"    Gradient zones:  {shadow.get('gradient_zones', 0)}")
        gzones = shadow.get("top_gradient_zones", [])
        if gzones:
            print(f"    Top gradients:")
            for gz in gzones[:3]:
                c = gz["cell"]
                print(f"      {c[0][:12]}x{c[1][:12]} {c[2][:10]}x{c[3][:10]} "
                      f"| score={gz['score']:.3f} depth={gz['best_depth']} n={gz['n_tested']}")

    # Executor stats
    ex = p.get("executor_stats", {})
    if ex:
        print(f"\n  Prefiltered: {ex.get('prefiltered_taxonomy', 0)} taxonomy, "
              f"{ex.get('prefiltered_megethos', 0)} megethos")

    # Checkpoints
    if checkpoints:
        last_ckpt = checkpoints[-1]
        print(f"\n  Last checkpoint: gen {last_ckpt.get('data', {}).get('gen', '?')} "
              f"({len(checkpoints)} total)")

    # Check if run is complete
    if latest_progress.get("event") == "run_complete":
        print(f"\n  *** RUN COMPLETE ***")


def main():
    parser = argparse.ArgumentParser(description="Monitor a running Ergon session")
    parser.add_argument("logfile", nargs="?", help="Path to log JSONL file")
    parser.add_argument("--watch", "-w", action="store_true", help="Refresh every 30s")
    args = parser.parse_args()

    log_path = Path(args.logfile) if args.logfile else find_latest_log()
    if not log_path or not log_path.exists():
        print("No log file found. Is Ergon running?")
        sys.exit(1)

    while True:
        if args.watch:
            # Clear screen on Windows
            import os
            os.system("cls" if os.name == "nt" else "clear")

        print("=" * 60)
        print(f"  ERGON MONITOR  |  {datetime.now().strftime('%H:%M:%S')}")
        print(f"  {log_path.name}")
        print("=" * 60)

        events = read_log(log_path)
        summarize(events)

        if not args.watch:
            break

        print(f"\n  Refreshing in 30s... (Ctrl+C to stop)")
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
