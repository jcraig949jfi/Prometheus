"""
nullspace_tests.py — Three decisive experiments from Titan Council Round 3.

Test A (ChatGPT): Jacobian finite-difference — is the vector in the logit nullspace?
    If ||quadratic|| >> ||linear||, first-order effect ≈ 0 and behavior is second-order.
    → Nullspace steering confirmed.

Test B (Gemini): RMSNorm suppression — does the vector crash downstream computation?
    If MLP/Attn output norms drop after injection, it's a normalization hack.
    If they stay stable, genuine nullspace steering survives.

Test C (Grok): Random orthogonal baseline — is the vector special in the orthogonal plane?
    If evolved vector is >3σ outlier vs 30 random orthogonal vectors, it's structured.
    If it's in the random cloud, CMA-ES found a lucky perturbation.

Usage:
    python nullspace_tests.py --genome path/to/best_genome.pt --model Qwen/Qwen3-4B --device cuda
    python nullspace_tests.py --test A   # run only Test A
    python nullspace_tests.py --test AB  # run Tests A and B
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
from analysis_base import AnalysisBase, LOGIT_TRAPS, HELD_OUT_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.nullspace_tests")


# ═══════════════════════════════════════════════════════════════════════════
# TEST A: Jacobian Finite-Difference (ChatGPT)
# ═══════════════════════════════════════════════════════════════════════════

def test_a_jacobian(base: AnalysisBase, epsilon: float = 1.0) -> dict:
    """
    Compute linear and quadratic terms of the logit perturbation via
    finite differences. If quadratic >> linear, vector is in logit nullspace.

    f(h + εv) ≈ f(h) + εJv + ½ε² vᵀHv
    linear_term  = (Δ₊ - Δ₋) / 2   ≈ εJv
    quadratic_term = (Δ₊ + Δ₋) / 2  ≈ ½ε² vᵀHv
    """
    print("\n" + "=" * 70)
    print("TEST A: Jacobian Finite-Difference (Logit Nullspace Test)")
    print("=" * 70)
    print(f"  If ||quadratic|| >> ||linear||: vector is in logit nullspace")
    print(f"  If ||linear|| >> ||quadratic||: vector has first-order logit effect")
    print(f"  epsilon = {epsilon}")
    print()

    model = base.model
    v_hat = base.v_hat
    layer = base.layer
    hook_name = f"blocks.{layer}.hook_resid_pre"

    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS
    results = []

    for trap in all_traps:
        prompt = trap["prompt"]
        tokens = model.to_tokens(prompt)

        def make_hook(scale):
            def hook_fn(activation, hook):
                activation[:, -1, :] += scale * v_hat
                return activation
            return hook_fn

        with torch.no_grad():
            # Baseline logits — use run_with_hooks to avoid default caching
            logits_base = model.run_with_hooks(
                tokens, fwd_hooks=[], return_type="logits"
            )[0, -1, :].float().cpu()

            # +ε perturbation
            logits_plus = model.run_with_hooks(
                tokens, fwd_hooks=[(hook_name, make_hook(+epsilon))], return_type="logits"
            )[0, -1, :].float().cpu()

            # -ε perturbation
            logits_minus = model.run_with_hooks(
                tokens, fwd_hooks=[(hook_name, make_hook(-epsilon))], return_type="logits"
            )[0, -1, :].float().cpu()

        delta_plus = logits_plus - logits_base
        delta_minus = logits_minus - logits_base

        linear_term = (delta_plus - delta_minus) / 2.0
        quadratic_term = (delta_plus + delta_minus) / 2.0

        lin_norm = linear_term.norm().item()
        quad_norm = quadratic_term.norm().item()
        ratio = quad_norm / (lin_norm + 1e-8)

        # Also check specific target/anti token effects
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        target_id = target_ids[0].item()
        anti_id = anti_ids[0].item()

        lin_margin = (linear_term[target_id] - linear_term[anti_id]).item()
        quad_margin = (quadratic_term[target_id] - quadratic_term[anti_id]).item()

        entry = {
            "trap": trap["name"],
            "linear_norm": round(lin_norm, 6),
            "quadratic_norm": round(quad_norm, 6),
            "ratio_quad_lin": round(ratio, 4),
            "linear_margin_effect": round(lin_margin, 6),
            "quadratic_margin_effect": round(quad_margin, 6),
        }
        results.append(entry)

        marker = " ← NULLSPACE" if ratio > 2.0 else ""
        print(f"  {trap['name']:<25} ||lin||={lin_norm:.4f}  ||quad||={quad_norm:.4f}  "
              f"ratio={ratio:.2f}{marker}")
        print(f"  {'':25} lin_margin={lin_margin:+.4f}  quad_margin={quad_margin:+.4f}")

    # Aggregate
    mean_ratio = np.mean([r["ratio_quad_lin"] for r in results])
    n_nullspace = sum(1 for r in results if r["ratio_quad_lin"] > 2.0)

    if mean_ratio > 2.0:
        verdict = "NULLSPACE_CONFIRMED"
        explanation = (
            f"Quadratic term dominates across {n_nullspace}/{len(results)} traps "
            f"(mean ratio={mean_ratio:.2f}). The vector lives in or near the logit "
            f"nullspace. Behavioral effects are second-order (Hessian-mediated)."
        )
    elif mean_ratio > 1.0:
        verdict = "PARTIAL_NULLSPACE"
        explanation = (
            f"Mixed: quadratic slightly dominates (mean ratio={mean_ratio:.2f}, "
            f"{n_nullspace}/{len(results)} traps). Vector is near but not in "
            f"the nullspace — some first-order leakage."
        )
    else:
        verdict = "ROWSPACE"
        explanation = (
            f"Linear term dominates (mean ratio={mean_ratio:.2f}). The vector "
            f"has substantial first-order logit effects. Not a nullspace direction."
        )

    print(f"\n  VERDICT: {verdict}")
    print(f"  {explanation}")

    return {
        "test": "A_jacobian_finite_diff",
        "epsilon": epsilon,
        "per_trap": results,
        "mean_ratio": round(mean_ratio, 4),
        "n_nullspace": n_nullspace,
        "verdict": verdict,
        "explanation": explanation,
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEST B: RMSNorm Suppression (Gemini)
# ═══════════════════════════════════════════════════════════════════════════

def test_b_rmsnorm(base: AnalysisBase) -> dict:
    """
    Measure downstream MLP and Attention output norms with and without
    the steering vector. If norms crash after injection, the vector is
    exploiting RMSNorm to suppress heuristic circuits.

    Hooks: resid_pre (to see norm inflation), mlp_out, attn_out at
    layers injection+1 through injection+4.
    """
    print("\n" + "=" * 70)
    print("TEST B: RMSNorm Suppression Test (Downstream Norm Analysis)")
    print("=" * 70)
    print("  If downstream MLP/Attn norms CRASH: RMSNorm hack (Gemini)")
    print("  If downstream norms STABLE or INCREASE: genuine nullspace steering")
    print()

    model = base.model
    vector = base.vector
    layer = base.layer
    hook_name_inject = f"blocks.{layer}.hook_resid_pre"

    # Monitor layers: injection layer through injection+4 (or model end)
    monitor_start = layer
    monitor_end = min(layer + 5, base.n_layers)
    monitor_layers = list(range(monitor_start, monitor_end))

    all_traps = LOGIT_TRAPS[:4]  # Use training traps only for speed
    results = []

    for trap in all_traps:
        prompt = trap["prompt"]
        tokens = model.to_tokens(prompt)

        for condition in ["baseline", "steered"]:
            metrics = {}

            # Build hooks
            hooks = []
            if condition == "steered":
                def inject_hook(activation, hook):
                    activation[:, -1, :] += vector
                    return activation
                hooks.append((hook_name_inject, inject_hook))

            # Add monitoring hooks for each layer
            for ml in monitor_layers:
                # Residual stream norm at this layer
                def make_resid_hook(layer_idx, cond):
                    def hook_fn(activation, hook):
                        norm = activation[0, -1, :].float().norm().item()
                        metrics[f"L{layer_idx}_resid_norm"] = norm
                        return activation
                    return hook_fn

                def make_mlp_hook(layer_idx, cond):
                    def hook_fn(activation, hook):
                        norm = activation[0, -1, :].float().norm().item()
                        metrics[f"L{layer_idx}_mlp_out_norm"] = norm
                        return activation
                    return hook_fn

                def make_attn_hook(layer_idx, cond):
                    def hook_fn(activation, hook):
                        norm = activation[0, -1, :].float().norm().item()
                        metrics[f"L{layer_idx}_attn_out_norm"] = norm
                        return activation
                    return hook_fn

                hooks.append((f"blocks.{ml}.hook_resid_pre", make_resid_hook(ml, condition)))
                hooks.append((f"blocks.{ml}.hook_mlp_out", make_mlp_hook(ml, condition)))
                hooks.append((f"blocks.{ml}.hook_attn_out", make_attn_hook(ml, condition)))

            with torch.no_grad():
                model.run_with_hooks(tokens, fwd_hooks=hooks, return_type="logits")

            results.append({
                "trap": trap["name"],
                "condition": condition,
                "metrics": metrics,
            })

    # Analyze: compare baseline vs steered norms
    print(f"  {'Layer':<8} {'Component':<12} {'Baseline':>10} {'Steered':>10} {'Ratio':>8} {'Effect':>12}")
    print(f"  {'-'*62}")

    layer_effects = []

    for ml in monitor_layers:
        for component in ["resid_norm", "mlp_out_norm", "attn_out_norm"]:
            key = f"L{ml}_{component}"
            baseline_vals = [r["metrics"].get(key, 0) for r in results if r["condition"] == "baseline"]
            steered_vals = [r["metrics"].get(key, 0) for r in results if r["condition"] == "steered"]

            if not baseline_vals or not steered_vals:
                continue

            base_mean = np.mean(baseline_vals)
            steer_mean = np.mean(steered_vals)
            ratio = steer_mean / (base_mean + 1e-8)

            if ratio < 0.8:
                effect = "SUPPRESSED"
            elif ratio > 1.2:
                effect = "AMPLIFIED"
            else:
                effect = "stable"

            comp_short = component.replace("_norm", "").replace("_out", "")
            print(f"  L{ml:<5} {comp_short:<12} {base_mean:>10.3f} {steer_mean:>10.3f} {ratio:>8.3f} {effect:>12}")

            layer_effects.append({
                "layer": ml,
                "component": component,
                "baseline_mean": round(base_mean, 4),
                "steered_mean": round(steer_mean, 4),
                "ratio": round(ratio, 4),
                "effect": effect,
            })

    # Verdict
    suppressed = [e for e in layer_effects if e["effect"] == "SUPPRESSED"]
    amplified = [e for e in layer_effects if e["effect"] == "AMPLIFIED"]

    # Focus on MLP/Attn components at layers after injection
    downstream = [e for e in layer_effects
                  if e["layer"] > layer and e["component"] in ("mlp_out_norm", "attn_out_norm")]
    downstream_suppressed = [e for e in downstream if e["effect"] == "SUPPRESSED"]

    if len(downstream_suppressed) > len(downstream) / 2:
        verdict = "RMSNORM_HACK"
        explanation = (
            f"Downstream MLP/Attn norms crash after injection "
            f"({len(downstream_suppressed)}/{len(downstream)} suppressed). "
            f"The vector inflates residual norm, causing LayerNorm to crush "
            f"downstream computation. Gemini's RMSNorm hack hypothesis confirmed."
        )
    elif len(amplified) > len(downstream) / 2:
        verdict = "DESTABILIZATION"
        explanation = (
            f"Downstream norms INCREASE after injection "
            f"({len(amplified)}/{len(downstream)} amplified). "
            f"The model is working harder to resolve the perturbed state. "
            f"Consistent with genuine destabilization, not normalization suppression."
        )
    else:
        verdict = "STABLE_NULLSPACE"
        explanation = (
            f"Downstream norms are stable after injection "
            f"({len(downstream_suppressed)} suppressed, {len(amplified)} amplified "
            f"out of {len(downstream)} downstream components). "
            f"The vector doesn't suppress or amplify — it operates invisibly "
            f"through the first-order computation. Consistent with nullspace steering."
        )

    print(f"\n  VERDICT: {verdict}")
    print(f"  {explanation}")

    return {
        "test": "B_rmsnorm_suppression",
        "monitor_layers": monitor_layers,
        "layer_effects": layer_effects,
        "n_downstream_suppressed": len(downstream_suppressed),
        "n_downstream_total": len(downstream),
        "verdict": verdict,
        "explanation": explanation,
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEST C: Random Orthogonal Baseline (Grok)
# ═══════════════════════════════════════════════════════════════════════════

def test_c_random_orthogonal(base: AnalysisBase, n_random: int = 30, seed: int = 42) -> dict:
    """
    Sample random vectors in the orthogonal complement of the reasoning
    direction, normalize to the same norm as the evolved vector, and
    measure fitness distribution. If evolved vector is >3σ outlier,
    the nullspace direction is structured.
    """
    print("\n" + "=" * 70)
    print("TEST C: Random Orthogonal Baseline (Structured vs Lucky)")
    print("=" * 70)
    print(f"  Sampling {n_random} random vectors orthogonal to reasoning direction")
    print(f"  All normalized to ||v|| = {base.genome['norm']:.3f}")
    print()

    model = base.model
    vector = base.vector
    v_hat = base.v_hat
    layer = base.layer
    norm_target = base.genome["norm"]
    hook_name = f"blocks.{layer}.hook_resid_pre"

    torch.manual_seed(seed)

    # Compute reasoning direction from CoT delta
    log.info("Computing reasoning direction from CoT delta...")
    reason_dir = torch.zeros_like(vector)
    n_dirs = 0
    for trap in LOGIT_TRAPS:
        prompt_std = trap["prompt"]
        prompt_cot = prompt_std + "\n\nLet's think step by step."

        tokens_std = model.to_tokens(prompt_std)
        tokens_cot = model.to_tokens(prompt_cot)
        cache_hook = f"blocks.{layer}.hook_resid_pre"

        with torch.no_grad():
            _, cache_s = model.run_with_cache(tokens_std, names_filter=[cache_hook])
            h_std = cache_s[cache_hook][0, -1, :].float()

            _, cache_c = model.run_with_cache(tokens_cot, names_filter=[cache_hook])
            h_cot = cache_c[cache_hook][0, -1, :].float()

        reason_dir += (h_cot - h_std)
        n_dirs += 1

    reason_dir /= n_dirs
    reason_dir = reason_dir / (reason_dir.norm() + 1e-8)

    # Verify evolved vector is already ~orthogonal
    cos_evolved = (v_hat @ reason_dir).item()
    log.info(f"Evolved vector cos(v, reasoning_dir) = {cos_evolved:.4f} (should be ~0)")

    # Fitness function: mean logit margin across traps
    def compute_fitness(vec):
        margins = []
        for trap in LOGIT_TRAPS:
            tokens = model.to_tokens(trap["prompt"])
            target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
            anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()

            def hook_fn(activation, hook):
                activation[:, -1, :] += vec
                return activation

            with torch.no_grad():
                logits = model.run_with_hooks(
                    tokens, fwd_hooks=[(hook_name, hook_fn)], return_type="logits"
                )[0, -1, :]
            margin = (logits[target_id] - logits[anti_id]).item()
            margins.append(margin)
        return float(np.mean(margins))

    # Baseline and evolved fitness
    log.info("Computing baseline fitness...")
    baseline_fitness = compute_fitness(torch.zeros_like(vector))
    log.info("Computing evolved vector fitness...")
    evolved_fitness = compute_fitness(vector)

    log.info(f"  Baseline: {baseline_fitness:+.4f}")
    log.info(f"  Evolved:  {evolved_fitness:+.4f}")

    # Random orthogonal vectors
    log.info(f"Testing {n_random} random orthogonal vectors...")
    random_fitnesses = []
    for i in range(n_random):
        rand = torch.randn_like(vector)
        # Project out reasoning direction
        rand = rand - (rand @ reason_dir) * reason_dir
        # Normalize to target norm
        rand = rand / (rand.norm() + 1e-8) * norm_target

        fit = compute_fitness(rand)
        random_fitnesses.append(fit)
        if (i + 1) % 10 == 0:
            log.info(f"  {i+1}/{n_random} done (latest fitness: {fit:+.4f})")

    random_mean = float(np.mean(random_fitnesses))
    random_std = float(np.std(random_fitnesses))
    z_score = (evolved_fitness - random_mean) / (random_std + 1e-8)

    print(f"\n  {'Metric':<30} {'Value':>12}")
    print(f"  {'-'*44}")
    print(f"  {'Baseline fitness':<30} {baseline_fitness:>+12.4f}")
    print(f"  {'Evolved vector fitness':<30} {evolved_fitness:>+12.4f}")
    print(f"  {'Random orthogonal mean':<30} {random_mean:>+12.4f}")
    print(f"  {'Random orthogonal std':<30} {random_std:>12.4f}")
    print(f"  {'Evolved vector Z-score':<30} {z_score:>+12.2f}σ")

    if z_score > 3.0:
        verdict = "STRUCTURED"
        explanation = (
            f"Evolved vector is a {z_score:.1f}σ outlier in the orthogonal plane. "
            f"The nullspace direction is structured, not a lucky random perturbation. "
            f"CMA-ES found a specific, meaningful direction in the logit nullspace."
        )
    elif z_score > 2.0:
        verdict = "MARGINAL"
        explanation = (
            f"Evolved vector is a {z_score:.1f}σ outlier — suggestive but not "
            f"definitive. More random samples may clarify."
        )
    else:
        verdict = "ARTIFACT"
        explanation = (
            f"Evolved vector is only {z_score:.1f}σ from random orthogonal mean. "
            f"Indistinguishable from random high-norm perturbation. The nullspace "
            f"direction is not special — CMA-ES found a lucky perturbation."
        )

    print(f"\n  VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save plot data
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(random_fitnesses, bins=12, alpha=0.7, color="steelblue",
                edgecolor="black", label="Random orthogonal vectors")
        ax.axvline(evolved_fitness, color="red", linewidth=3,
                   label=f"Evolved vector ({z_score:+.1f}σ)")
        ax.axvline(baseline_fitness, color="gray", linewidth=2, linestyle="--",
                   label="Baseline (no vector)")
        ax.set_xlabel("Mean logit margin across 4 traps")
        ax.set_ylabel("Count")
        ax.set_title(f"Test C: Is the evolved vector special in the orthogonal plane?\n"
                     f"Z-score = {z_score:+.1f}σ | Verdict: {verdict}")
        ax.legend()
        plt.tight_layout()

        out_path = base.output_dir / f"test_c_random_orthogonal_{base.timestamp()}.png"
        plt.savefig(str(out_path), dpi=150)
        plt.close()
        log.info(f"Plot saved: {out_path}")
    except ImportError:
        log.info("matplotlib not available, skipping plot")

    return {
        "test": "C_random_orthogonal",
        "n_random": n_random,
        "seed": seed,
        "baseline_fitness": round(baseline_fitness, 6),
        "evolved_fitness": round(evolved_fitness, 6),
        "random_mean": round(random_mean, 6),
        "random_std": round(random_std, 6),
        "z_score": round(z_score, 4),
        "random_fitnesses": [round(f, 6) for f in random_fitnesses],
        "cos_evolved_reasoning": round(cos_evolved, 6),
        "verdict": verdict,
        "explanation": explanation,
    }


# ═══════════════════════════════════════════════════════════════════════════
# SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════

def print_synthesis(results: dict):
    print("\n" + "=" * 70)
    print("PHALANX SYNTHESIS — Three Tests Combined")
    print("=" * 70)

    a = results.get("A")
    b = results.get("B")
    c = results.get("C")

    verdicts = {}
    if a:
        verdicts["nullspace"] = a["verdict"]
    if b:
        verdicts["mechanism"] = b["verdict"]
    if c:
        verdicts["structured"] = c["verdict"]

    print(f"\n  Test A (Jacobian):   {verdicts.get('nullspace', 'NOT RUN')}")
    print(f"  Test B (RMSNorm):    {verdicts.get('mechanism', 'NOT RUN')}")
    print(f"  Test C (Random):     {verdicts.get('structured', 'NOT RUN')}")

    # Decision matrix
    is_nullspace = verdicts.get("nullspace") in ("NULLSPACE_CONFIRMED", "PARTIAL_NULLSPACE")
    is_rmsnorm = verdicts.get("mechanism") == "RMSNORM_HACK"
    is_structured = verdicts.get("structured") == "STRUCTURED"

    print(f"\n  COMBINED INTERPRETATION:")

    if is_nullspace and not is_rmsnorm and is_structured:
        print("  ★ GENUINE NULLSPACE STEERING")
        print("    The vector lives in the logit nullspace, operates through")
        print("    second-order effects, and is structurally specific (not random).")
        print("    This is the ChatGPT/DeepSeek reading: a novel mechanism where")
        print("    CMA-ES discovered that optimal intervention is invisible to")
        print("    the first-order readout but active through nonlinear dynamics.")
        print("\n    NEXT: Run DeepSeek's update subspace SVD + Claude's OC-1/2/3.")

    elif is_nullspace and is_rmsnorm and is_structured:
        print("  ★ STRUCTURED RMSNORM EXPLOITATION")
        print("    The vector is in the logit nullspace AND it crashes downstream")
        print("    norms via RMSNorm. But it's not random — CMA-ES found a specific")
        print("    direction that maximally exploits the normalization vulnerability.")
        print("    Gemini was right about mechanism, but wrong that it's unstructured.")
        print("\n    NEXT: Measure downstream entropy. Does suppression help or hurt?")

    elif is_nullspace and not is_structured:
        print("  ★ NULLSPACE ARTIFACT")
        print("    Vector is in the logit nullspace, but any random orthogonal vector")
        print("    does about as well. The fitness improvement is a generic property")
        print("    of high-norm orthogonal perturbations, not a specific discovery.")
        print("\n    NEXT: Abandon current vector. Evolve for CoT-alignment instead.")

    elif not is_nullspace and is_structured:
        print("  ★ STANDARD STRUCTURED STEERING")
        print("    Vector has real first-order logit effects and is specifically")
        print("    better than random. It's a standard steering vector that happens")
        print("    to be weakly aligned with behavioral probes (probes were too coarse).")
        print("\n    NEXT: Re-run probes with more data. Standard interp applies.")

    else:
        print("  ★ INCONCLUSIVE — run all three tests for full picture")

    print("=" * 70)


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Nullspace Tests — Three decisive experiments from Titan Council Round 3",
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--test", type=str, default="ABC",
                        help="Which tests to run: A, B, C, AB, AC, BC, ABC (default: ABC)")
    parser.add_argument("--n-random", type=int, default=30,
                        help="Number of random vectors for Test C (default: 30)")
    parser.add_argument("--epsilon", type=float, default=1.0,
                        help="Epsilon for Test A finite differences (default: 1.0)")
    args, _ = parser.parse_known_args()

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    # ── Preflight gate (in-process, no double model load) ──
    from preflight import run_preflight_with_base
    preflight_result = run_preflight_with_base(base)
    if not preflight_result.all_passed:
        log.error("PREFLIGHT FAILED — aborting nullspace tests")
        log.error(f"Failed checks: {', '.join(preflight_result.failures)}")
        sys.exit(1)
    print()

    tests_to_run = args.test.upper()
    results = {}

    if "A" in tests_to_run:
        results["A"] = test_a_jacobian(base, epsilon=args.epsilon)
        base.save_json(results["A"], "nullspace_test_A")

    if "B" in tests_to_run:
        results["B"] = test_b_rmsnorm(base)
        base.save_json(results["B"], "nullspace_test_B")

    if "C" in tests_to_run:
        results["C"] = test_c_random_orthogonal(base, n_random=args.n_random)
        base.save_json(results["C"], "nullspace_test_C")

    if len(results) > 1:
        print_synthesis(results)

    # Save combined results
    combined = {
        "analysis": "nullspace_tests_phalanx",
        "model": base.model_name,
        "genome": base.genome["path"] if base.genome else None,
        "layer": base.layer,
        "tests_run": list(results.keys()),
        "verdicts": {k: v["verdict"] for k, v in results.items()},
        "timestamp": base.timestamp(),
    }
    base.save_json(combined, "nullspace_phalanx_summary")

    print(f"\nAll results saved to: {base.output_dir}")


if __name__ == "__main__":
    main()
