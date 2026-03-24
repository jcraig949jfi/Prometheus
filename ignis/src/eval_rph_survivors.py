"""
eval_rph_survivors.py — Background RPH proxy evaluator for existing survivor genomes.

Runs on CPU (or a named device) so it doesn't compete with an active GPU run.
Loads archived best_genome.pt files, runs RPH proxy scoring via SBERT + PCA stats,
and outputs a comparison table across model scales.

Usage:
    # From seti-pipeline_v2/src/ directory:
    python eval_rph_survivors.py

    # Force CPU (safe while 1.5B GPU run is live):
    python eval_rph_survivors.py --device cpu

    # Score only 0.5B and 3B archives (skip 1.5B while it's running):
    python eval_rph_survivors.py --models 0.5B 3B

    # Point at a specific archive directory:
    python eval_rph_survivors.py --archive-dir ../src/results/ignis/archives

This script imports genome.py and rph_metrics.py from the same src/ directory.
It does NOT import ignis_orchestrator, tii_engine, or fitness.py — it's fully standalone.
"""

import argparse
import json
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

import torch
import numpy as np

# Allow imports from this directory
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model registry — maps archive slug → HuggingFace model name
# ---------------------------------------------------------------------------
MODEL_REGISTRY = {
    "qwen_qwen2_5-0_5b-instruct": "Qwen/Qwen2.5-0.5B-Instruct",
    "qwen_qwen2_5-1_5b-instruct": "Qwen/Qwen2.5-1.5B-Instruct",
    "qwen_qwen2_5-3b-instruct":   "Qwen/Qwen2.5-3B-Instruct",
    "qwen_qwen2_5-7b-instruct":   "Qwen/Qwen2.5-7B-Instruct",
    "qwen_qwen3-4b":              "Qwen/Qwen3-4B",
}

SCALE_LABEL = {
    "qwen_qwen2_5-0_5b-instruct": "0.5B",
    "qwen_qwen2_5-1_5b-instruct": "1.5B",
    "qwen_qwen2_5-3b-instruct":   "3B",
    "qwen_qwen2_5-7b-instruct":   "7B",
    "qwen_qwen3-4b":              "Qwen3-4B",
}


def find_best_genomes(archive_dir: Path, model_slugs: list[str]) -> dict:
    """
    Find best_genome.pt files in archive subdirectories for each model slug.
    Returns {slug: [path, ...]} ordered newest-first by archive folder name.
    """
    results = {slug: [] for slug in model_slugs}

    for archive_subdir in sorted(archive_dir.iterdir(), reverse=True):
        if not archive_subdir.is_dir():
            continue
        for slug in model_slugs:
            candidate = archive_subdir / slug / "best_genome.pt"
            if candidate.exists():
                results[slug].append(candidate)

    return results


def load_genome(path: Path):
    """Load a SteeringGenome from a .pt file."""
    from genome import SteeringGenome
    g = SteeringGenome.load(str(path))
    if g is not None:
        g.id = path.parent.parent.name  # use archive folder name as ID
    return g


def run_inference_cpu(model, prompt: str, vector: torch.Tensor, layer: int,
                      alpha: float = 1.0, max_new_tokens: int = 150) -> tuple[str, dict]:
    """
    Run a forward pass on CPU with the steering vector injected.
    Returns (generated_text, residual_cache).
    """
    hook_name = f"blocks.{layer}.hook_resid_pre"
    input_tokens = model.to_tokens(prompt)

    residual_cache = {}

    def _capture_resid_post(value, hook):
        residual_cache[hook.name] = value.detach().cpu()
        return value

    def _inject_and_capture(value, hook):
        # Inject vector at last token position
        seq_len = value.shape[1]
        pos = max(0, seq_len - 1)
        patched = value.clone()
        v_norm = vector.to(value.device).float()
        if v_norm.shape[0] <= value.shape[-1]:
            patched[0, pos, :v_norm.shape[0]] = patched[0, pos, :v_norm.shape[0]] + alpha * v_norm
        return patched

    fwd_hooks = [(hook_name, _inject_and_capture)]
    # Capture resid_post at all layers for MI_step
    for layer_idx in range(model.cfg.n_layers):
        fwd_hooks.append((f"blocks.{layer_idx}.hook_resid_post", _capture_resid_post))

    with model.hooks(fwd_hooks=fwd_hooks):
        with torch.no_grad():
            out_ids = model.generate(
                input_tokens,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                do_sample=True,
            )

    return model.to_string(out_ids[0]), residual_cache


def score_genome_rph(model, genome, pairs: list, alpha: float = 1.0) -> dict:
    """
    Run RPH proxy scoring for a single genome against all prompt pairs.
    Uses CPU inference — safe to run while another GPU process is active.
    """
    from rph_metrics import (
        compute_delta_cf, compute_mi_step, classify_vector,
        _test_delta_cf, _bootstrap_mi_ci
    )

    layer = genome.layer_index
    vector = genome.vector.float().cpu()

    outputs_steered, outputs_cf_steered = [], []
    outputs_base, outputs_cf_base = [], []
    residual_caches = []

    for pair in pairs:
        prompt = pair.get("prompt", "")
        perturbed = pair.get("perturbed", "")
        if not prompt or not perturbed:
            continue

        try:
            # Base (unsteered) passes
            with torch.no_grad():
                base_ids = model.generate(
                    model.to_tokens(prompt), max_new_tokens=100, temperature=0.7, do_sample=True
                )
                cf_base_ids = model.generate(
                    model.to_tokens(perturbed), max_new_tokens=100, temperature=0.7, do_sample=True
                )
            outputs_base.append(model.to_string(base_ids[0]))
            outputs_cf_base.append(model.to_string(cf_base_ids[0]))

            # Steered passes
            s_out, s_cache = run_inference_cpu(model, prompt, vector, layer, alpha)
            cf_out, _ = run_inference_cpu(model, perturbed, vector, layer, alpha)
            outputs_steered.append(s_out)
            outputs_cf_steered.append(cf_out)
            residual_caches.append(s_cache)

            log.info(f"  pair={pair.get('id', '?')} ✓")

        except Exception as e:
            log.warning(f"  pair={pair.get('id', '?')} failed: {e}")
            continue

    n_pairs = len(outputs_steered)
    if n_pairs == 0:
        return {"delta_cf": 0.0, "mi_step": 0.0, "passes": 0,
                "classification": "NULL", "pairs_scored": 0}

    # Δ_cf
    delta_cf_mean, delta_cf_std = compute_delta_cf(outputs_steered, outputs_cf_steered)
    base_cf_mean, _ = compute_delta_cf(outputs_base, outputs_cf_base)

    per_pair_steered = []
    for i in range(n_pairs):
        d, _ = compute_delta_cf([outputs_steered[i]], [outputs_cf_steered[i]])
        per_pair_steered.append(d)

    cf_test = _test_delta_cf([base_cf_mean] * n_pairs, per_pair_steered)

    # MI_step
    mi_values = [compute_mi_step(cache) for cache in residual_caches]
    mi_step_mean = float(np.mean(mi_values)) if mi_values else 0.0
    mi_ci = _bootstrap_mi_ci(mi_values) if len(mi_values) >= 3 else (0.0, 0.0)

    # Classification
    classification = classify_vector(cf_test, mi_ci)
    n_passes = sum([cf_test.get("passes", False), mi_ci[0] > 0])

    return {
        "delta_cf": delta_cf_mean,
        "delta_cf_std": delta_cf_std,
        "delta_cf_cohens_d": cf_test.get("cohens_d", 0.0),
        "delta_cf_p": cf_test.get("p", 1.0),
        "delta_cf_passes": cf_test.get("passes", False),
        "mi_step": mi_step_mean,
        "mi_ci_low": mi_ci[0],
        "mi_ci_high": mi_ci[1],
        "mi_step_passes": mi_ci[0] > 0,
        "passes": n_passes,
        "classification": classification,
        "pairs_scored": n_pairs,
        "base_delta_cf": base_cf_mean,
    }


def main():
    parser = argparse.ArgumentParser(description="RPH proxy evaluator for archived survivor genomes")
    parser.add_argument("--device", default="cpu", help="torch device (cpu | cuda)")
    parser.add_argument("--archive-dir", default=None,
                        help="Path to ignis/archives directory")
    parser.add_argument("--pairs", default=None,
                        help="Path to rph_counterfactual_pairs.json")
    parser.add_argument("--models", nargs="+", default=["0.5B", "3B"],
                        help="Which model scales to evaluate (default: 0.5B 3B)")
    parser.add_argument("--output", default=None,
                        help="Save results JSON to this path")
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="Injection scale alpha (default 1.0)")
    args = parser.parse_args()

    # Resolve paths
    src_dir = Path(__file__).parent
    project_root = src_dir.parent

    if args.archive_dir:
        archive_dir = Path(args.archive_dir)
    else:
        archive_dir = src_dir / "results" / "ignis" / "archives"

    if args.pairs:
        pairs_path = Path(args.pairs)
    else:
        pairs_path = project_root / "data" / "rph_counterfactual_pairs.json"

    if not archive_dir.exists():
        log.error(f"Archive directory not found: {archive_dir}")
        sys.exit(1)

    if not pairs_path.exists():
        log.error(f"Pairs file not found: {pairs_path}")
        sys.exit(1)

    pairs = json.loads(pairs_path.read_text(encoding="utf-8"))
    log.info(f"Loaded {len(pairs)} counterfactual pairs from {pairs_path}")

    # Map scale labels to slugs
    scale_to_slug = {v: k for k, v in SCALE_LABEL.items()}
    requested_slugs = [scale_to_slug[m] for m in args.models if m in scale_to_slug]

    if not requested_slugs:
        log.error(f"No valid model slugs found for: {args.models}")
        sys.exit(1)

    # Find genome files
    genome_map = find_best_genomes(archive_dir, requested_slugs)
    all_results = {}

    for slug in requested_slugs:
        genome_paths = genome_map.get(slug, [])
        if not genome_paths:
            log.warning(f"No best_genome.pt found for {SCALE_LABEL[slug]} — skipping")
            continue

        # Use the most recent archive's best genome
        genome_path = genome_paths[0]
        genome = load_genome(genome_path)
        if genome is None:
            log.warning(f"Failed to load genome from {genome_path}")
            continue

        model_name = MODEL_REGISTRY[slug]
        scale = SCALE_LABEL[slug]
        log.info(f"\n{'='*60}")
        log.info(f"Evaluating {scale} ({model_name})")
        log.info(f"  genome: {genome_path}")
        log.info(f"  fitness={genome.fitness:.4f}, layer={genome.layer_index}")
        log.info(f"  device: {args.device}")

        try:
            from transformer_lens import HookedTransformer
            dtype = torch.float32 if args.device == "cpu" else torch.float16
            log.info(f"  Loading model ({dtype})...")
            model = HookedTransformer.from_pretrained(
                model_name, device=args.device, dtype=dtype
            )
            model.eval()
            log.info(f"  Model loaded. Running {len(pairs)} pairs...")
        except Exception as e:
            log.error(f"  Model load failed: {e}")
            continue

        result = score_genome_rph(model, genome, pairs, alpha=args.alpha)
        result["model"] = model_name
        result["scale"] = scale
        result["fitness"] = genome.fitness
        result["layer"] = genome.layer_index
        result["genome_path"] = str(genome_path)
        all_results[scale] = result

        # Free VRAM/RAM before loading next model
        del model
        if args.device == "cuda":
            torch.cuda.empty_cache()

    # Print results table
    print("\n" + "="*80)
    print("RPH PROXY EVALUATION — SCALE GRADIENT RESULTS")
    print("="*80)
    print(f"{'Scale':<8} {'Fitness':<10} {'Δ_cf':<8} {'MI_step':<10} {'Passes':<8} {'Class':<25} {'Layer'}")
    print("-"*80)
    for scale in ["0.5B", "1.5B", "3B", "7B"]:
        if scale not in all_results:
            continue
        r = all_results[scale]
        print(f"{scale:<8} {r['fitness']:<10.4f} {r['delta_cf']:<8.4f} "
              f"{r['mi_step']:<10.4f} {r['passes']:<8} {r['classification']:<25} {r['layer']}")

    print("="*80)
    print("\nNote: Layer 2 claim requires Δ_proj (SC/HB detection) — not yet computed.")
    print("      PRECIPITATION_CANDIDATE classification uses Δ_cf + MI_step only (2/3 criteria).")

    # Save results
    if args.output:
        output_path = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = project_root / "results" / f"rph_eval_{ts}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    log.info(f"\nResults saved → {output_path}")


if __name__ == "__main__":
    main()
