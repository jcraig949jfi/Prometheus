"""
athena_orchestrator.py — Autonomous GPU experiment orchestrator.

Monitors the current GPU job, and when it finishes, starts the next one
from the experiment queue. Checks every 30 minutes. Logs everything.

Usage:
    python athena_orchestrator.py              # Run orchestrator
    python athena_orchestrator.py --interval 900  # Check every 15 min
    python athena_orchestrator.py --dry-run     # Show queue without running
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

IGNIS_ROOT = Path(__file__).resolve().parent
SRC_DIR = IGNIS_ROOT / "src"
RESULTS_DIR = IGNIS_ROOT / "results"
MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
DEVICE = "cuda"
LOG_FILE = IGNIS_ROOT / "athena_orchestrator.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ATHENA] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode="a"),
    ],
)
log = logging.getLogger("athena")


# ---------------------------------------------------------------------------
# Experiment definitions — each is a dict with:
#   name, cmd (list of args), output_dir, done_marker (file that signals completion)
# ---------------------------------------------------------------------------

def build_experiment_queue():
    """Build the ordered experiment queue. Skip experiments already completed."""
    queue = []

    # --- Experiment 1: L21 evolution (Stage 2a fix) ---
    L21_dir = RESULTS_DIR / "batch4_followup" / "stage2_L21"
    queue.append({
        "name": "L21 evolution (500 gen, eps=3.0)",
        "cmd": [
            sys.executable, str(SRC_DIR / "evolve_1_5b.py"),
            "--model", MODEL, "--device", DEVICE,
            "--n-generations", "500", "--epsilon", "3.0",
            "--layer", "21", "--popsize", "32", "--stdev-init", "0.05",
            "--output-dir", str(L21_dir),
        ],
        "output_dir": L21_dir,
        "done_marker": "best_genome_1_5b.pt",
    })

    # --- Experiment 2: Layer sweep L19 ---
    for layer in [19, 20, 25, 26]:
        layer_dir = RESULTS_DIR / "layer_sweep" / f"L{layer}"
        queue.append({
            "name": f"Layer sweep L{layer} (300 gen)",
            "cmd": [
                sys.executable, str(SRC_DIR / "evolve_1_5b.py"),
                "--model", MODEL, "--device", DEVICE,
                "--n-generations", "300", "--epsilon", "3.0",
                "--layer", str(layer), "--popsize", "32", "--stdev-init", "0.05",
                "--output-dir", str(layer_dir),
            ],
            "output_dir": layer_dir,
            "done_marker": "best_genome_1_5b.pt",
        })

    # --- Experiment 3: Basin escape histograms ---
    for layer in [22, 23, 24]:
        basin_dir = RESULTS_DIR / "basin_escape" / f"L{layer}"
        queue.append({
            "name": f"Basin escape histogram L{layer} (100 dirs)",
            "cmd": [
                sys.executable, str(SRC_DIR / "basin_escape_histogram.py"),
                "--model", MODEL, "--device", DEVICE,
                "--layer", str(layer), "--n-directions", "100",
                "--output-dir", str(basin_dir),
            ],
            "output_dir": basin_dir,
            "done_marker": "basin_escape_histogram.json",
        })

    # --- Experiment 4: Eval L21 genome (after L21 evolves) ---
    L21_genome = L21_dir / "best_genome_1_5b.pt"
    eval_L21_dir = RESULTS_DIR / "eval_L21"
    queue.append({
        "name": "Eval L21 genome (full v2 battery)",
        "cmd": [
            sys.executable, str(SRC_DIR / "eval_v2.py"),
            "--model", MODEL, "--device", DEVICE,
            "--genome", str(L21_genome),
            "--output-dir", str(eval_L21_dir),
            "--tiers", "ABCMS", "--skip-logit-lens",
        ],
        "output_dir": eval_L21_dir,
        "done_marker": None,  # eval_v2 produces timestamped JSON
        "requires": str(L21_genome),  # skip if dependency doesn't exist
    })

    # --- Experiment 5: Forge-augmented evolution at L23 ---
    forge_dir = RESULTS_DIR / "forge_augmented" / "L23"
    forge_consensus = RESULTS_DIR / "forge_eval" / "forge_consensus.json"
    queue.append({
        "name": "Forge-augmented evolution L23 (500 gen)",
        "cmd": [
            sys.executable, str(SRC_DIR / "evolve_forge_augmented.py"),
            "--model", MODEL, "--device", DEVICE,
            "--n-generations", "500", "--epsilon", "3.0",
            "--layer", "23", "--popsize", "32", "--stdev-init", "0.05",
            "--forge-consensus", str(forge_consensus),
            "--output-dir", str(forge_dir),
        ],
        "output_dir": forge_dir,
        "done_marker": "best_genome_1_5b.pt",
        "requires": str(forge_consensus),
    })

    # --- Experiment 6: Multi-layer combination eval ---
    combo_dir = RESULTS_DIR / "multilayer_combo"
    queue.append({
        "name": "Multi-layer combination test (all genome subsets)",
        "cmd": [
            sys.executable, str(SRC_DIR / "multilayer_eval.py"),
            "--model", MODEL, "--device", DEVICE,
            "--epsilon-scales", "0.5", "1.0", "1.5",
            "--output-dir", str(combo_dir),
        ],
        "output_dir": combo_dir,
        "done_marker": None,
    })

    # --- Experiment 7: Cross-arch Qwen-0.5B ---
    qwen05_dir = RESULTS_DIR / "cross_arch" / "qwen05"
    queue.append({
        "name": "Cross-arch: Qwen2.5-0.5B evolution",
        "cmd": [
            sys.executable, str(SRC_DIR / "evolve_1_5b.py"),
            "--model", "Qwen/Qwen2.5-0.5B-Instruct", "--device", DEVICE,
            "--n-generations", "300", "--epsilon", "3.0",
            "--layer", "18", "--popsize", "32", "--stdev-init", "0.05",
            "--output-dir", str(qwen05_dir),
        ],
        "output_dir": qwen05_dir,
        "done_marker": "best_genome_1_5b.pt",
    })

    # --- Experiment 8: Corpus-first pipeline (long, ~6 hours) ---
    corpus_dir = RESULTS_DIR / "corpus_first"
    queue.append({
        "name": "Corpus-first experiment (fine-tune + evolve)",
        "cmd": [
            sys.executable, str(SRC_DIR / "corpus_first.py"),
            "--model", MODEL, "--device", DEVICE,
            "--n-attempts", "300",
            "--n-generations", "500",
            "--output-dir", str(corpus_dir),
        ],
        "output_dir": corpus_dir,
        "done_marker": "corpus_first_summary.json",
    })

    return queue


def is_experiment_done(exp):
    """Check if an experiment has already completed."""
    out_dir = Path(exp["output_dir"])
    if not out_dir.exists():
        return False
    marker = exp.get("done_marker")
    if marker:
        return (out_dir / marker).exists()
    # No marker — check if directory has any JSON output
    return any(out_dir.glob("*.json"))


def check_dependency(exp):
    """Check if experiment's dependency exists."""
    req = exp.get("requires")
    if req is None:
        return True
    return Path(req).exists()


def is_gpu_busy():
    """Check if another heavy Python process is running (likely a model).

    On Windows WDDM, nvidia-smi --query-compute-apps is unreliable.
    Instead, check for Python processes using >2GB RAM (sign of a loaded model).
    Exclude our own orchestrator PID.
    """
    my_pid = os.getpid()
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.strip().split("\n"):
            line = line.strip().strip('"')
            if not line or "python" not in line.lower():
                continue
            # CSV format: "python.exe","PID","Session","#","Mem Usage"
            parts = [p.strip('"') for p in line.split('","')]
            if len(parts) >= 5:
                pid = int(parts[1])
                mem_str = parts[4].replace(",", "").replace("K", "").replace(" ", "")
                try:
                    mem_kb = int(mem_str)
                except ValueError:
                    continue
                # >2GB RAM and not us = model is loaded
                if pid != my_pid and mem_kb > 2_000_000:
                    log.info(f"  GPU busy: PID {pid} using {mem_kb // 1024}MB RAM")
                    return True
    except Exception as e:
        log.warning(f"GPU busy check failed: {e}")
    return False


def run_experiment(exp):
    """Run a single experiment. Returns (success, return_code)."""
    out_dir = Path(exp["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = out_dir / "athena_stdout.log"
    log.info(f"Starting: {exp['name']}")
    log.info(f"  Command: {' '.join(exp['cmd'])}")
    log.info(f"  Output: {out_dir}")
    log.info(f"  Log: {log_path}")

    start = time.time()
    try:
        with open(log_path, "w") as stdout_log:
            proc = subprocess.run(
                exp["cmd"],
                stdout=stdout_log,
                stderr=subprocess.STDOUT,
                timeout=28800,  # 8 hour max per experiment
                cwd=str(IGNIS_ROOT),
            )
        elapsed = time.time() - start
        log.info(f"Finished: {exp['name']} in {elapsed/60:.1f} min (rc={proc.returncode})")
        return proc.returncode == 0, proc.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        log.warning(f"TIMEOUT: {exp['name']} after {elapsed/60:.1f} min")
        return False, -1
    except Exception as e:
        log.error(f"FAILED: {exp['name']} — {e}")
        return False, -2


def write_summary(completed, failed, skipped):
    """Write a human-readable summary of all experiments."""
    summary_path = IGNIS_ROOT / "results" / "athena_session_summary.md"
    with open(summary_path, "w") as f:
        f.write("# Athena Autonomous Session Summary\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        f.write("## Completed\n")
        for name in completed:
            f.write(f"- {name}\n")
        if not completed:
            f.write("- (none)\n")

        f.write("\n## Failed\n")
        for name, rc in failed:
            f.write(f"- {name} (rc={rc})\n")
        if not failed:
            f.write("- (none)\n")

        f.write("\n## Skipped (already done or dependency missing)\n")
        for name, reason in skipped:
            f.write(f"- {name} — {reason}\n")
        if not skipped:
            f.write("- (none)\n")

        f.write(f"\n## Results Directories\n")
        f.write("Check each experiment's output_dir for JSON results.\n")
        f.write("Key files: `best_genome_1_5b.pt`, `final_eval_*.json`, `evolution_log_*.json`\n")

    log.info(f"Summary written to {summary_path}")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Athena GPU experiment orchestrator")
    parser.add_argument("--interval", type=int, default=1800,
                        help="Check interval in seconds (default: 1800 = 30 min)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show queue without running")
    parser.add_argument("--once", action="store_true",
                        help="Run one experiment and exit (no monitoring loop)")
    args = parser.parse_args()

    queue = build_experiment_queue()

    log.info("=" * 60)
    log.info("ATHENA ORCHESTRATOR — Autonomous GPU Experiment Runner")
    log.info(f"Experiments in queue: {len(queue)}")
    log.info(f"Check interval: {args.interval}s ({args.interval/60:.0f} min)")
    log.info("=" * 60)

    if args.dry_run:
        for i, exp in enumerate(queue):
            done = is_experiment_done(exp)
            dep_ok = check_dependency(exp)
            status = "DONE" if done else ("NO DEP" if not dep_ok else "PENDING")
            log.info(f"  [{i+1}] {status} — {exp['name']}")
        return

    completed = []
    failed = []
    skipped = []
    exp_index = 0

    while exp_index < len(queue):
        exp = queue[exp_index]

        # Skip if already done
        if is_experiment_done(exp):
            log.info(f"Skipping (already done): {exp['name']}")
            skipped.append((exp["name"], "already completed"))
            exp_index += 1
            continue

        # Skip if dependency missing
        if not check_dependency(exp):
            log.info(f"Skipping (dependency missing): {exp['name']}")
            skipped.append((exp["name"], f"requires {exp.get('requires')}"))
            exp_index += 1
            continue

        # Wait if GPU is busy (another process)
        if is_gpu_busy():
            log.info(f"GPU busy — waiting {args.interval}s before retry...")
            time.sleep(args.interval)
            continue

        # Run the experiment
        success, rc = run_experiment(exp)
        if success:
            completed.append(exp["name"])
        else:
            failed.append((exp["name"], rc))

        exp_index += 1

        if args.once:
            break

        # Brief cooldown between experiments (let GPU memory free)
        log.info("Cooldown 30s before next experiment...")
        time.sleep(30)

    write_summary(completed, failed, skipped)
    log.info("All experiments processed. Orchestrator exiting.")


if __name__ == "__main__":
    main()
