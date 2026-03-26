"""
corpus_first.py — Corpus-first experiment: fine-tune before evolve.

Tests the order-of-operations hypothesis:
  If v_proj dual-use means corpus must come BEFORE evolution,
  then fine-tuning on reasoning data should:
  1. Shallow the ejection profile
  2. Improve baseline SR without steering
  3. Enable faster CMA-ES convergence
  4. Produce higher post-evolution SR

Pipeline:
  Stage A: Baseline diagnostic (logit lens + eval)
  Stage B: Fine-tune on self-generated reasoning corpus
  Stage C: Post-corpus diagnostic (measure ejection change)
  Stage D: CMA-ES evolution on fine-tuned seed
  Stage E: Comparison

Usage:
    python corpus_first.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
    python corpus_first.py --skip-baseline  # Skip Stage A if already done
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CORPUS1ST] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.corpus_first")

SRC_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SRC_DIR.parent / "results" / "corpus_first"


def run_stage(name, cmd, stage_dir, timeout=7200):
    """Run a stage as subprocess, log output."""
    stage_dir.mkdir(parents=True, exist_ok=True)
    log_path = stage_dir / "stdout.log"

    log.info(f"\n{'='*60}")
    log.info(f"STAGE {name}")
    log.info(f"{'='*60}")
    log.info(f"  Command: {' '.join(cmd)}")

    start = time.time()
    try:
        with open(log_path, "w") as f:
            result = subprocess.run(
                cmd, stdout=f, stderr=subprocess.STDOUT,
                timeout=timeout, cwd=str(SRC_DIR.parent),
            )
        elapsed = time.time() - start
        log.info(f"  Completed in {elapsed/60:.1f} min (rc={result.returncode})")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log.warning(f"  TIMEOUT after {timeout/60:.0f} min")
        return False
    except Exception as e:
        log.error(f"  FAILED: {e}")
        return False


def check_transformerlens_compat(model_path):
    """Quick check if TransformerLens can load a local model."""
    try:
        from transformer_lens import HookedTransformer
        log.info(f"  Testing TransformerLens load of {model_path}...")
        model = HookedTransformer.from_pretrained(
            str(model_path),
            center_writing_weights=False,
            center_unembed=False,
            fold_ln=False,
            device="cpu",  # Quick test on CPU
        )
        n_layers = model.cfg.n_layers
        d_model = model.cfg.d_model
        del model
        torch.cuda.empty_cache()
        log.info(f"  SUCCESS: {n_layers} layers, d_model={d_model}")
        return True
    except Exception as e:
        log.warning(f"  TransformerLens cannot load fine-tuned model: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Corpus-first experiment")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--skip-baseline", action="store_true",
                        help="Skip Stage A baseline if already done")
    parser.add_argument("--n-attempts", type=int, default=300,
                        help="Number of corpus generation attempts")
    parser.add_argument("--n-generations", type=int, default=500,
                        help="CMA-ES generations for Stage D")
    parser.add_argument("--output-dir", type=str, default=str(RESULTS_DIR))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {"stages": {}}
    t_start = time.time()

    # ===== STAGE A: Baseline diagnostic =====
    stageA_dir = output_dir / "stageA_baseline"
    if args.skip_baseline and stageA_dir.exists() and any(stageA_dir.glob("*.json")):
        log.info("Skipping Stage A (--skip-baseline and results exist)")
        results["stages"]["A"] = "skipped"
    else:
        # Logit lens
        ok_ll = run_stage("A1 - Baseline logit lens", [
            sys.executable, str(SRC_DIR / "logit_lens_backward.py"),
            "--model", args.model, "--device", args.device,
            "--output-dir", str(stageA_dir),
            "--skip-preflight",
        ], stageA_dir, timeout=1800)

        # Eval v2
        ok_ev = run_stage("A2 - Baseline eval_v2", [
            sys.executable, str(SRC_DIR / "eval_v2.py"),
            "--model", args.model, "--device", args.device,
            "--output-dir", str(stageA_dir),
            "--skip-logit-lens",
        ], stageA_dir, timeout=1800)

        results["stages"]["A"] = {"logit_lens": ok_ll, "eval_v2": ok_ev}

    # ===== STAGE B: Fine-tune on reasoning corpus =====
    stageB_dir = output_dir / "stageB_finetune"
    ft_model_path = stageB_dir / "ft_tmp"

    if ft_model_path.exists() and (ft_model_path / "config.json").exists():
        log.info("Stage B already completed (ft_tmp exists). Skipping.")
        results["stages"]["B"] = "already_done"
    else:
        ok_ft = run_stage("B - Fine-tune on reasoning corpus", [
            sys.executable, str(SRC_DIR / "loop_closure.py"),
            "--model", args.model, "--device", args.device,
            "--n-attempts", str(args.n_attempts),
            "--output-dir", str(stageB_dir),
        ], stageB_dir, timeout=3600)
        results["stages"]["B"] = ok_ft

    # Check if fine-tuned model was saved
    ft_exists = ft_model_path.exists() and (ft_model_path / "config.json").exists()
    if not ft_exists:
        log.warning("No fine-tuned model found. Stage B may have failed.")
        log.warning("Cannot proceed with Stages C-E. Saving partial results.")
        results["stages"]["C"] = "skipped_no_model"
        results["stages"]["D"] = "skipped_no_model"
        results["stages"]["E"] = "skipped_no_model"
        _save_summary(output_dir, results, t_start)
        return

    # ===== STAGE C: Post-corpus diagnostic =====
    stageC_dir = output_dir / "stageC_post_corpus"

    # Test TransformerLens compatibility
    tl_ok = check_transformerlens_compat(ft_model_path)

    if tl_ok:
        ok_ll = run_stage("C1 - Post-corpus logit lens", [
            sys.executable, str(SRC_DIR / "logit_lens_backward.py"),
            "--model", str(ft_model_path), "--device", args.device,
            "--output-dir", str(stageC_dir),
            "--skip-preflight",
        ], stageC_dir, timeout=1800)

        ok_ev = run_stage("C2 - Post-corpus eval_v2", [
            sys.executable, str(SRC_DIR / "eval_v2.py"),
            "--model", str(ft_model_path), "--device", args.device,
            "--output-dir", str(stageC_dir),
            "--skip-logit-lens",
        ], stageC_dir, timeout=1800)

        results["stages"]["C"] = {"logit_lens": ok_ll, "eval_v2": ok_ev, "tl_compat": True}
    else:
        log.warning("TransformerLens cannot load fine-tuned model.")
        log.info("Running HF-only eval (no logit lens)...")

        # Still run eval_v2 using loop_closure's eval (HF native)
        ok_ev = run_stage("C2-fallback - Post-corpus eval (HF native)", [
            sys.executable, str(SRC_DIR / "loop_closure.py"),
            "--model", str(ft_model_path), "--device", args.device,
            "--n-attempts", "0",  # 0 attempts = eval only, no corpus gen
            "--output-dir", str(stageC_dir),
        ], stageC_dir, timeout=1800)

        results["stages"]["C"] = {"logit_lens": False, "eval_v2": ok_ev, "tl_compat": False}

    # ===== STAGE D: Evolution on fine-tuned seed =====
    stageD_dir = output_dir / "stageD_evolve"

    if tl_ok:
        ok_evo = run_stage("D - CMA-ES on corpus-trained seed", [
            sys.executable, str(SRC_DIR / "evolve_1_5b.py"),
            "--model", str(ft_model_path), "--device", args.device,
            "--n-generations", str(args.n_generations),
            "--epsilon", "3.0",
            "--layer", "23",
            "--popsize", "32", "--stdev-init", "0.05",
            "--output-dir", str(stageD_dir),
        ], stageD_dir, timeout=14400)  # 4 hours max
        results["stages"]["D"] = ok_evo
    else:
        log.warning("Skipping Stage D — TransformerLens cannot load fine-tuned model.")
        results["stages"]["D"] = "skipped_no_tl"

    # ===== STAGE E: Final comparison =====
    stageE_dir = output_dir / "stageE_comparison"

    genome_path = stageD_dir / "best_genome_1_5b.pt"
    if genome_path.exists() and tl_ok:
        ok_final = run_stage("E - Final eval with genome", [
            sys.executable, str(SRC_DIR / "eval_v2.py"),
            "--model", str(ft_model_path), "--device", args.device,
            "--genome", str(genome_path),
            "--output-dir", str(stageE_dir),
            "--skip-logit-lens",
        ], stageE_dir, timeout=1800)
        results["stages"]["E"] = ok_final
    else:
        log.info("Skipping Stage E (no genome or no TL compat)")
        results["stages"]["E"] = "skipped"

    _save_summary(output_dir, results, t_start)


def _save_summary(output_dir, results, t_start):
    """Save experiment summary."""
    elapsed = time.time() - t_start
    results["elapsed_minutes"] = elapsed / 60
    results["timestamp"] = datetime.now().isoformat()

    summary_path = output_dir / "corpus_first_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    log.info(f"\n{'='*60}")
    log.info("CORPUS-FIRST EXPERIMENT COMPLETE")
    log.info(f"{'='*60}")
    log.info(f"  Total time: {elapsed/60:.1f} min")
    for stage, result in results["stages"].items():
        log.info(f"  Stage {stage}: {result}")
    log.info(f"  Summary: {summary_path}")
    log.info(f"\n  Key comparisons:")
    log.info(f"    Stage A vs C: Did corpus training change ejection profile?")
    log.info(f"    Stage A vs E: Did corpus+evolution beat baseline evolution?")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()
