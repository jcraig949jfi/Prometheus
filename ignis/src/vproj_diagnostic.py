"""
vproj_diagnostic.py — Test whether the ejection mechanism at 1.5B is concentrated
in v_proj (value projections) like Rhea found at 135M, or has migrated to MLP.

Rhea's ablation on 135M showed:
  - v_proj is the ejection circuit (smallest norm, highest impact)
  - Front-loaded (layers 0-14)
  - gate_proj alone gets zero survival

Ignis's decomposition on 1.5B showed:
  - MLP-dominant ejection at L25-27 (10/13 traps)
  - L26.head_7 serial killer on Density Illusion

This script bridges the gap: does v_proj also matter at 1.5B?
If so, the ejection circuit is v_proj at all scales but MIGRATES deeper.
If not, the mechanism genuinely changes architecture with scale.

Method:
  For each failing trap at its L*, ablate v_proj contributions vs MLP contributions
  and measure which ablation restores the correct answer more.

  Specifically:
  1. Run baseline, record margin at output
  2. Hook into L* and zero out the attention output (removing v_proj's contribution)
     → record margin. If it improves, attention (including v_proj) was ejecting.
  3. Hook into L* and zero out the MLP output
     → record margin. If it improves, MLP was ejecting.
  4. Compare: which ablation helps more?

  Also: test at EARLY layers (0-14) to see if v_proj matters there at 1.5B
  like it does at 135M.

Usage:
    python vproj_diagnostic.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    get_logit_margin,
)
from phase_transition_study import ORDINAL_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.vproj_diagnostic")

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS


def ablate_component_at_layer(model, tokens, layer, component, target_id, anti_id):
    """
    Run forward pass with a specific component zeroed at a specific layer.
    component: 'attn' or 'mlp'
    Returns the logit margin.
    """
    hook_name = f"blocks.{layer}.hook_{component}_out"

    def zero_hook(value, hook):
        value[:, -1, :] = 0.0
        return value

    model.add_hook(hook_name, zero_hook)
    with torch.no_grad():
        logits = model(tokens)
    model.reset_hooks()

    margin = (logits[0, -1, target_id] - logits[0, -1, anti_id]).item()
    return margin


def run_layer_range_ablation(model, trap, target_id, anti_id, layer_range, component):
    """
    Ablate a component across a range of layers simultaneously.
    Returns the margin with all those layers' component zeroed.
    """
    tokens = model.to_tokens(trap["prompt"])

    hooks = []
    for L in layer_range:
        hook_name = f"blocks.{L}.hook_{component}_out"

        def make_zero_hook():
            def zero_hook(value, hook):
                value[:, -1, :] = 0.0
                return value
            return zero_hook

        model.add_hook(hook_name, make_zero_hook())

    with torch.no_grad():
        logits = model(tokens)
    model.reset_hooks()

    margin = (logits[0, -1, target_id] - logits[0, -1, anti_id]).item()
    return margin


def main():
    parser = argparse.ArgumentParser(
        description="v_proj diagnostic — does the 1.5B ejection live in attention values?",
    )
    AnalysisBase.add_common_args(parser)
    args = parser.parse_args()

    print("=" * 70)
    print("V_PROJ DIAGNOSTIC — Scale-dependent ejection architecture")
    print("Does the ejection at 1.5B live in v_proj like at 135M?")
    print("=" * 70)

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    model = base.model
    n_layers = base.n_layers

    # Find failing traps
    print("\n  Identifying failing traps...")
    failing_traps = []
    for trap in ALL_TRAPS:
        margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        if margin <= 0:
            failing_traps.append((trap, margin))

    print(f"  {len(failing_traps)} failing traps found\n")

    # ── Test 1: Per-layer attn vs MLP ablation at L* ──
    print("=" * 70)
    print("TEST 1: Attn vs MLP ablation at L* (which component ejects?)")
    print("=" * 70)

    print(f"\n  {'Trap':<30} {'Base':>8} {'No Attn':>8} {'No MLP':>8} {'Attn Δ':>8} {'MLP Δ':>8} {'Ejector':>10}")
    print(f"  {'-'*85}")

    attn_wins = 0
    mlp_wins = 0
    test1_results = []

    for trap, base_margin in failing_traps:
        tokens = model.to_tokens(trap["prompt"])
        target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
        anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()

        # Find L* via logit lens
        W_U = model.W_U
        names_filter = [f"blocks.{L}.hook_resid_post" for L in range(n_layers)]
        with torch.no_grad():
            _, cache = model.run_with_cache(tokens, names_filter=names_filter)

        margins = []
        for L in range(n_layers):
            h = cache[f"blocks.{L}.hook_resid_post"][0, -1, :]
            m = (h @ W_U[:, target_id] - h @ W_U[:, anti_id]).item()
            margins.append(m)

        deltas = [margins[i+1] - margins[i] for i in range(len(margins)-1)]
        l_star = int(np.argmin(deltas)) + 1

        # Ablate attn at L*
        margin_no_attn = ablate_component_at_layer(
            model, tokens, l_star, "attn", target_id, anti_id
        )

        # Ablate MLP at L*
        margin_no_mlp = ablate_component_at_layer(
            model, tokens, l_star, "mlp", target_id, anti_id
        )

        attn_delta = margin_no_attn - base_margin  # positive = attn was hurting
        mlp_delta = margin_no_mlp - base_margin  # positive = MLP was hurting

        if attn_delta > mlp_delta:
            ejector = "ATTN"
            attn_wins += 1
        else:
            ejector = "MLP"
            mlp_wins += 1

        print(f"  {trap['name']:<30} {base_margin:>+8.3f} {margin_no_attn:>+8.3f} "
              f"{margin_no_mlp:>+8.3f} {attn_delta:>+8.3f} {mlp_delta:>+8.3f} {ejector:>10}")

        test1_results.append({
            "trap": trap["name"],
            "l_star": l_star,
            "baseline": base_margin,
            "no_attn": margin_no_attn,
            "no_mlp": margin_no_mlp,
            "attn_delta": attn_delta,
            "mlp_delta": mlp_delta,
            "ejector": ejector,
        })

    print(f"\n  Summary: Attn dominant on {attn_wins}/{len(failing_traps)}, "
          f"MLP dominant on {mlp_wins}/{len(failing_traps)}")

    # ── Test 2: Early vs late layer ablation (does v_proj matter at layers 0-14?) ──
    print(f"\n{'='*70}")
    print("TEST 2: Early (0-14) vs Late (20-27) attn ablation")
    print("Does attention in early layers contribute to ejection at 1.5B?")
    print("=" * 70)

    mid = n_layers // 2  # 14 for 28-layer model
    early_range = list(range(0, mid))
    late_range = list(range(n_layers - 8, n_layers))

    print(f"\n  Early range: layers {early_range[0]}-{early_range[-1]}")
    print(f"  Late range: layers {late_range[0]}-{late_range[-1]}")

    print(f"\n  {'Trap':<30} {'Base':>8} {'No Early Attn':>14} {'No Late Attn':>14} "
          f"{'Early Δ':>8} {'Late Δ':>8} {'Critical':>10}")
    print(f"  {'-'*95}")

    early_critical = 0
    late_critical = 0
    test2_results = []

    for trap, base_margin in failing_traps:
        target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
        anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()

        margin_no_early = run_layer_range_ablation(
            model, trap, target_id, anti_id, early_range, "attn"
        )
        margin_no_late = run_layer_range_ablation(
            model, trap, target_id, anti_id, late_range, "attn"
        )

        early_delta = margin_no_early - base_margin
        late_delta = margin_no_late - base_margin

        if abs(early_delta) > abs(late_delta):
            critical = "EARLY"
            early_critical += 1
        else:
            critical = "LATE"
            late_critical += 1

        print(f"  {trap['name']:<30} {base_margin:>+8.3f} {margin_no_early:>+14.3f} "
              f"{margin_no_late:>+14.3f} {early_delta:>+8.3f} {late_delta:>+8.3f} {critical:>10}")

        test2_results.append({
            "trap": trap["name"],
            "baseline": base_margin,
            "no_early_attn": margin_no_early,
            "no_late_attn": margin_no_late,
            "early_delta": early_delta,
            "late_delta": late_delta,
            "critical_region": critical,
        })

    print(f"\n  Summary: Early-critical on {early_critical}/{len(failing_traps)}, "
          f"Late-critical on {late_critical}/{len(failing_traps)}")

    # ── Interpretation ──
    print(f"\n{'='*70}")
    print("INTERPRETATION")
    print("=" * 70)

    if mlp_wins > attn_wins * 2:
        print(f"\n  MLP dominates at 1.5B ({mlp_wins}/{len(failing_traps)} traps).")
        print("  The ejection CHANGED ARCHITECTURE with scale.")
        print("  135M: v_proj (attention values). 1.5B: MLP (memorization).")
        arch_verdict = "ARCHITECTURE_SHIFT"
    elif attn_wins > mlp_wins * 2:
        print(f"\n  Attention dominates at 1.5B ({attn_wins}/{len(failing_traps)} traps).")
        print("  The ejection mechanism is v_proj at BOTH scales.")
        print("  It migrated deeper (layers 0-14 at 135M → L25-27 at 1.5B) but stayed in attention.")
        arch_verdict = "SAME_ARCHITECTURE_DEEPER"
    else:
        print(f"\n  Mixed: Attn={attn_wins}, MLP={mlp_wins}.")
        print("  The ejection uses both mechanisms at 1.5B, specialized by trap type.")
        arch_verdict = "MIXED"

    if late_critical > early_critical * 2:
        print(f"  Late layers critical ({late_critical}/{len(failing_traps)}).")
        print("  Confirms the ejection migrated to late layers at 1.5B scale.")
        depth_verdict = "LATE"
    elif early_critical > late_critical * 2:
        print(f"  Early layers critical ({early_critical}/{len(failing_traps)}).")
        print("  Surprising — ejection is front-loaded at 1.5B too, like 135M.")
        depth_verdict = "EARLY"
    else:
        print(f"  Mixed depth: Early={early_critical}, Late={late_critical}.")
        depth_verdict = "MIXED"

    print(f"\n  Architecture verdict: {arch_verdict}")
    print(f"  Depth verdict: {depth_verdict}")

    # Save
    if base.output_dir:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = {
            "timestamp": datetime.now().isoformat(),
            "model": base.model_name,
            "n_layers": n_layers,
            "n_failing": len(failing_traps),
            "test1_attn_vs_mlp": {
                "attn_wins": attn_wins,
                "mlp_wins": mlp_wins,
                "results": test1_results,
            },
            "test2_early_vs_late": {
                "early_range": early_range,
                "late_range": late_range,
                "early_critical": early_critical,
                "late_critical": late_critical,
                "results": test2_results,
            },
            "arch_verdict": arch_verdict,
            "depth_verdict": depth_verdict,
        }
        path = base.output_dir / f"vproj_diagnostic_{ts}.json"
        path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
        log.info(f"Saved: {path}")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
