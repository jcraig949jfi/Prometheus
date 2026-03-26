"""
athena_followon.py — Monitor L21 and chain remaining experiments.

Waits for L21 evolution to complete (checks for best_genome_1_5b.pt),
then runs the remaining experiment queue.

Usage:
    python athena_followon.py
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

IGNIS_ROOT = Path(__file__).resolve().parent
SRC_DIR = IGNIS_ROOT / "src"
RESULTS_DIR = IGNIS_ROOT / "results"
MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
DEVICE = "cuda"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ATHENA] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(IGNIS_ROOT / "athena_followon.log", mode="a"),
    ],
)
log = logging.getLogger("athena")


def wait_for_file(path, check_interval=300, timeout=36000):
    """Wait for a file to appear. Returns True if found, False on timeout."""
    start = time.time()
    path = Path(path)
    while time.time() - start < timeout:
        if path.exists():
            log.info(f"Found: {path}")
            return True
        elapsed = int(time.time() - start)
        log.info(f"Waiting for {path.name}... ({elapsed}s elapsed)")
        time.sleep(check_interval)
    log.warning(f"Timeout waiting for {path}")
    return False


def run_experiment(name, cmd, output_dir, timeout=28800):
    """Run experiment, return success bool."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "stdout.log"

    log.info(f"\n{'='*60}")
    log.info(f"Starting: {name}")
    log.info(f"{'='*60}")

    start = time.time()
    try:
        with open(log_path, "w") as f:
            proc = subprocess.run(
                cmd, stdout=f, stderr=subprocess.STDOUT,
                timeout=timeout, cwd=str(IGNIS_ROOT),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
        elapsed = time.time() - start
        log.info(f"Done: {name} ({elapsed/60:.1f} min, rc={proc.returncode})")
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        log.warning(f"TIMEOUT: {name}")
        return False
    except Exception as e:
        log.error(f"FAILED: {name} — {e}")
        return False


def main():
    L21_genome = RESULTS_DIR / "batch4_followup" / "stage2_L21" / "best_genome_1_5b.pt"

    log.info("=" * 60)
    log.info("ATHENA FOLLOW-ON — Waiting for L21, then running queue")
    log.info("=" * 60)

    # Wait for L21 to complete (check every 5 min, timeout 10 hours)
    if not L21_genome.exists():
        log.info(f"L21 evolution running. Waiting for {L21_genome}...")
        found = wait_for_file(L21_genome, check_interval=300, timeout=36000)
        if not found:
            log.warning("L21 did not complete in 10 hours. Proceeding with available genomes.")
    else:
        log.info("L21 genome already exists.")

    # Cooldown after L21 (let GPU memory free)
    log.info("Cooldown 60s...")
    time.sleep(60)

    results = []

    # Layer sweep
    for layer in [19, 20, 25, 26]:
        layer_dir = RESULTS_DIR / "layer_sweep" / f"L{layer}"
        marker = layer_dir / "best_genome_1_5b.pt"
        if marker.exists():
            log.info(f"Skipping L{layer} (already done)")
            continue
        ok = run_experiment(
            f"Layer sweep L{layer} (300 gen)",
            [sys.executable, "-u", str(SRC_DIR / "evolve_1_5b.py"),
             "--model", MODEL, "--device", DEVICE,
             "--n-generations", "300", "--epsilon", "3.0",
             "--layer", str(layer), "--popsize", "32", "--stdev-init", "0.05",
             "--output-dir", str(layer_dir)],
            layer_dir,
        )
        results.append((f"L{layer}", ok))
        time.sleep(30)

    # Basin escape histograms
    for layer in [22, 23, 24]:
        basin_dir = RESULTS_DIR / "basin_escape" / f"L{layer}"
        if any(basin_dir.glob("*.json")) if basin_dir.exists() else False:
            log.info(f"Skipping basin L{layer} (already done)")
            continue
        ok = run_experiment(
            f"Basin escape L{layer} (100 dirs)",
            [sys.executable, "-u", str(SRC_DIR / "basin_escape_histogram.py"),
             "--model", MODEL, "--device", DEVICE,
             "--layer", str(layer), "--n-directions", "100",
             "--output-dir", str(basin_dir)],
            basin_dir,
        )
        results.append((f"basin_L{layer}", ok))
        time.sleep(30)

    # Forge-augmented evolution
    forge_dir = RESULTS_DIR / "forge_augmented" / "L23"
    forge_consensus = RESULTS_DIR / "forge_eval" / "forge_consensus.json"
    if not (forge_dir / "best_genome_1_5b.pt").exists() and forge_consensus.exists():
        ok = run_experiment(
            "Forge-augmented L23 (500 gen)",
            [sys.executable, "-u", str(SRC_DIR / "evolve_forge_augmented.py"),
             "--model", MODEL, "--device", DEVICE,
             "--n-generations", "500", "--epsilon", "3.0",
             "--layer", "23", "--popsize", "32", "--stdev-init", "0.05",
             "--forge-consensus", str(forge_consensus),
             "--output-dir", str(forge_dir)],
            forge_dir,
        )
        results.append(("forge_L23", ok))
        time.sleep(30)

    # Multi-layer combination test
    combo_dir = RESULTS_DIR / "multilayer_combo"
    if not any(combo_dir.glob("*.json")) if combo_dir.exists() else True:
        ok = run_experiment(
            "Multi-layer combination (all subsets)",
            [sys.executable, "-u", str(SRC_DIR / "multilayer_eval.py"),
             "--model", MODEL, "--device", DEVICE,
             "--epsilon-scales", "0.5", "1.0", "1.5",
             "--output-dir", str(combo_dir)],
            combo_dir,
        )
        results.append(("multilayer_combo", ok))
        time.sleep(30)

    # Cross-arch Qwen-0.5B
    qwen05_dir = RESULTS_DIR / "cross_arch" / "qwen05"
    if not (qwen05_dir / "best_genome_1_5b.pt").exists():
        ok = run_experiment(
            "Cross-arch: Qwen-0.5B (300 gen)",
            [sys.executable, "-u", str(SRC_DIR / "evolve_1_5b.py"),
             "--model", "Qwen/Qwen2.5-0.5B-Instruct", "--device", DEVICE,
             "--n-generations", "300", "--epsilon", "3.0",
             "--layer", "18", "--popsize", "32", "--stdev-init", "0.05",
             "--output-dir", str(qwen05_dir)],
            qwen05_dir,
        )
        results.append(("cross_arch_qwen05", ok))

    # Summary
    log.info(f"\n{'='*60}")
    log.info("ATHENA FOLLOW-ON COMPLETE")
    log.info(f"{'='*60}")
    for name, ok in results:
        log.info(f"  {'OK' if ok else 'FAIL'}  {name}")
    log.info(f"Total experiments: {len(results)}")


if __name__ == "__main__":
    main()
