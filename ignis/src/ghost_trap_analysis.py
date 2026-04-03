"""
ghost_trap_analysis.py — Mechanistic analysis of the winning steering combo.

For each trap, captures:
  - cos_with_residual: cosine between steering vector and the model's natural
    residual stream direction. High = we're amplifying what the model already
    wants to do. Low = we're injecting an alien signal (bypass).
  - norm_ratio: ||steered_residual|| / ||unsteered_residual||. Near 1.0 = gentle
    nudge. >>1 = brute force override.
  - logit_shift_signature: top-5 most-shifted tokens (steered - unsteered).
    Shows whether the intervention is surgically targeting correct/incorrect
    tokens or broadly disrupting the logit distribution.

Usage:
    python ghost_trap_analysis.py --model results/corpus_first/stageB_finetune/ft_model
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import torch
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import AnalysisBase, LOGIT_TRAPS, HELD_OUT_TRAPS, get_logit_margin, make_steering_hook
from phase_transition_study import ORDINAL_TRAPS
from multilayer_eval import load_genome

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [GHOST] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.ghost")


def capture_residuals(model, prompt, layer_indices, device="cuda"):
    """Run a forward pass and capture residual stream at specified layers."""
    tokens = model.to_tokens(prompt)
    captured = {}

    def make_hook(layer_idx):
        def hook_fn(value, hook):
            captured[layer_idx] = value[0, -1, :].detach().clone()
        return hook_fn

    hooks = [(f"blocks.{li}.hook_resid_post", make_hook(li)) for li in layer_indices]

    with torch.no_grad():
        logits = model.run_with_hooks(tokens, fwd_hooks=hooks)

    return captured, logits[0, -1, :]


def main():
    parser = argparse.ArgumentParser(description="Ghost trap mechanistic analysis")
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--epsilon-scale", type=float, default=1.5)
    parser.add_argument("--top-k-tokens", type=int, default=5)
    parser.add_argument("--genomes", nargs="*", default=None,
                        help="Layer=path pairs, e.g. L8=path/to/genome.pt. "
                             "If omitted, uses default Qwen winning combo.")
    args = parser.parse_args()

    base = AnalysisBase(
        model_name=args.model,
        device=args.device,
        output_dir=args.output_dir or "results/ghost_trap_analysis",
    )
    model = base.model
    output_dir = base.output_dir

    # Load genomes — from --genomes arg or default Qwen winning combo
    if args.genomes:
        genome_specs = []
        for spec in args.genomes:
            name, path = spec.split("=", 1)
            genome_specs.append((name, Path(path)))
    else:
        results_root = Path(__file__).resolve().parent.parent / "results"
        genome_specs = [
            ("L19", results_root / "layer_sweep" / "L19" / "best_genome_1_5b.pt"),
            ("L20", results_root / "layer_sweep" / "L20" / "best_genome_1_5b.pt"),
            ("L21", results_root / "batch4_followup" / "stage2_L21" / "best_genome_1_5b.pt"),
        ]

    steering_vectors = []
    steering_hooks = []
    n_layers = base.n_layers
    d_model = base.d_model
    for name, path in genome_specs:
        vec, layer, eps = load_genome(str(path))
        # Cross-architecture compatibility checks
        if vec.shape[-1] != d_model:
            log.warning(f"  SKIP {name}: d_model mismatch — genome has "
                        f"{vec.shape[-1]}, model has {d_model}")
            continue
        if layer >= n_layers:
            log.warning(f"  SKIP {name}: layer {layer} exceeds target model's "
                        f"{n_layers} layers (0-{n_layers - 1})")
            continue
        v_hat = vec / (vec.norm() + 1e-8)
        v_hat = v_hat.to(args.device)
        steering_vectors.append((name, v_hat, layer, eps * args.epsilon_scale))
        hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=eps * args.epsilon_scale)
        steering_hooks.append((hook_name, hook_fn))
        log.info(f"Loaded {name}: layer={layer}, eps={eps * args.epsilon_scale:.1f}, "
                 f"norm={vec.norm():.2f}")

    layer_indices = [sv[2] for sv in steering_vectors]

    log.info(f"\nAnalyzing {len(ALL_TRAPS)} traps...\n")
    log.info(f"{'Trap':30s}  {'cos_w_resid':>11s}  {'norm_ratio':>10s}  {'margin':>8s}  {'status':>8s}")
    log.info(f"{'-'*30}  {'-'*11}  {'-'*10}  {'-'*8}  {'-'*8}")

    results = []

    for trap in ALL_TRAPS:
        # Unsteered pass: capture residuals and logits
        unsteered_resids, unsteered_logits = capture_residuals(
            model, trap["prompt"], layer_indices, args.device
        )

        # Steered pass: capture residuals and logits
        # We need a custom approach — run with steering hooks AND capture hooks
        tokens = model.to_tokens(trap["prompt"])
        steered_captured = {}

        def make_capture_hook(layer_idx):
            def hook_fn(value, hook):
                steered_captured[layer_idx] = value[0, -1, :].detach().clone()
            return hook_fn

        all_hooks = list(steering_hooks)
        for li in layer_indices:
            # Capture AFTER steering (at resid_post, which is after the hook_resid_pre injection)
            all_hooks.append((f"blocks.{li}.hook_resid_post", make_capture_hook(li)))

        with torch.no_grad():
            steered_logits = model.run_with_hooks(tokens, fwd_hooks=all_hooks)
        steered_logits = steered_logits[0, -1, :]

        # Compute per-layer ghost metrics
        layer_metrics = []
        cos_values = []
        norm_ratios = []

        for name, v_hat, layer, eps in steering_vectors:
            if layer in unsteered_resids and layer in steered_captured:
                u_resid = unsteered_resids[layer]
                s_resid = steered_captured[layer]

                # cos_with_residual: how aligned is the steering direction with the natural residual?
                cos_sim = torch.nn.functional.cosine_similarity(
                    v_hat.unsqueeze(0), u_resid.unsqueeze(0)
                ).item()

                # norm_ratio: how much did we change the magnitude?
                n_ratio = (s_resid.norm() / (u_resid.norm() + 1e-8)).item()

                cos_values.append(cos_sim)
                norm_ratios.append(n_ratio)

                layer_metrics.append({
                    "layer_name": name,
                    "layer_index": layer,
                    "cos_with_residual": cos_sim,
                    "norm_ratio": n_ratio,
                    "unsteered_norm": u_resid.norm().item(),
                    "steered_norm": s_resid.norm().item(),
                })

        # Logit shift signature
        logit_delta = steered_logits - unsteered_logits
        top_k = torch.topk(logit_delta.abs(), args.top_k_tokens)
        shift_sig = []
        for idx, val in zip(top_k.indices.tolist(), top_k.values.tolist()):
            token_str = model.to_str_tokens(torch.tensor([idx]))[0]
            shift_sig.append({
                "token_id": idx,
                "token_str": token_str,
                "delta": logit_delta[idx].item(),
                "abs_delta": val,
            })

        # Get margin
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        target_id = target_ids[0].item()
        anti_id = anti_ids[0].item()
        margin = (steered_logits[target_id] - steered_logits[anti_id]).item()
        baseline_margin = (unsteered_logits[target_id] - unsteered_logits[anti_id]).item()

        flipped = baseline_margin <= 0 and margin > 0

        mean_cos = np.mean(cos_values) if cos_values else 0.0
        mean_norm = np.mean(norm_ratios) if norm_ratios else 1.0

        status = "FLIP" if flipped else ("OK" if margin > 0 else "WRONG")
        log.info(f"  {trap['name']:30s}  {mean_cos:+.4f}      {mean_norm:.4f}     {margin:+.3f}   {status}")

        results.append({
            "name": trap["name"],
            "baseline_margin": baseline_margin,
            "steered_margin": margin,
            "flipped": flipped,
            "correct": margin > 0,
            "mean_cos_with_residual": mean_cos,
            "mean_norm_ratio": mean_norm,
            "layer_metrics": layer_metrics,
            "logit_shift_signature": shift_sig,
        })

    # Summary
    cos_all = [r["mean_cos_with_residual"] for r in results]
    cos_flipped = [r["mean_cos_with_residual"] for r in results if r["flipped"]]
    norm_all = [r["mean_norm_ratio"] for r in results]

    log.info(f"\n{'='*70}")
    log.info("GHOST TRAP SUMMARY")
    log.info(f"{'='*70}")
    log.info(f"  Overall mean cos_with_residual:   {np.mean(cos_all):+.4f}")
    log.info(f"  Flipped traps mean cos_with_resid: {np.mean(cos_flipped):+.4f}" if cos_flipped else "  No flipped traps")
    log.info(f"  Overall mean norm_ratio:           {np.mean(norm_all):.4f}")

    # Quadrant classification
    high_fit_high_cos = sum(1 for r in results if r["correct"] and r["mean_cos_with_residual"] > 0.1)
    high_fit_low_cos = sum(1 for r in results if r["correct"] and r["mean_cos_with_residual"] <= 0.1)
    low_fit_high_cos = sum(1 for r in results if not r["correct"] and r["mean_cos_with_residual"] > 0.1)
    low_fit_low_cos = sum(1 for r in results if not r["correct"] and r["mean_cos_with_residual"] <= 0.1)

    log.info(f"\n  Four-Quadrant Classification (cos threshold=0.1):")
    log.info(f"    Correct + High cos (NATIVE AMPLIFICATION): {high_fit_high_cos}")
    log.info(f"    Correct + Low cos  (BYPASS):               {high_fit_low_cos}")
    log.info(f"    Wrong   + High cos (natural dir unhelpful): {low_fit_high_cos}")
    log.info(f"    Wrong   + Low cos  (noise):                 {low_fit_low_cos}")

    verdict = "NATIVE AMPLIFICATION" if high_fit_high_cos > high_fit_low_cos else "BYPASS"
    log.info(f"\n  VERDICT: Dominant mechanism is {verdict}")

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"ghost_trap_analysis_{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "epsilon_scale": args.epsilon_scale,
            "summary": {
                "mean_cos_all": float(np.mean(cos_all)),
                "mean_cos_flipped": float(np.mean(cos_flipped)) if cos_flipped else None,
                "mean_norm_ratio": float(np.mean(norm_all)),
                "quadrants": {
                    "correct_high_cos": high_fit_high_cos,
                    "correct_low_cos": high_fit_low_cos,
                    "wrong_high_cos": low_fit_high_cos,
                    "wrong_low_cos": low_fit_low_cos,
                },
                "verdict": verdict,
            },
            "traps": results,
        }, f, indent=2)

    log.info(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
