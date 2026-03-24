"""
sae_decompose.py — SAE / PCA decomposition of Ignis steering vectors.

Attempts to decompose the steering vector to understand what activation-space
"mode" it targets. Two approaches:

Approach A (preferred): Load pre-trained SAE weights from SAELens/HuggingFace
    and report top-k activating features.

Approach B (fallback): If no SAE weights exist for this model, perform a
    "poor man's decomposition" via PCA on cached activations, then project the
    steering vector onto the principal components.

Output verdict: SUPPRESSOR / AMPLIFIER / MIXED / UNKNOWN

Usage:
    python sae_decompose.py \\
        --genome results/ignis/archives/.../best_genome.pt \\
        --model Qwen/Qwen2.5-1.5B-Instruct \\
        --device cuda \\
        --output-dir results/refinement/
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.sae_decompose")

# ---------------------------------------------------------------------------
# Diverse prompt bank for PCA basis (100 prompts)
# ---------------------------------------------------------------------------
DIVERSE_PROMPTS = [
    # Reasoning
    "If all roses are flowers and some flowers fade quickly, can we conclude all roses fade quickly?",
    "A train leaves at 3pm going 60mph. Another leaves at 4pm going 80mph. When do they meet?",
    "What is the probability of rolling two sixes in a row with a fair die?",
    "If it takes 3 workers 4 hours to paint a house, how long for 6 workers?",
    "Explain why correlation does not imply causation with an example.",
    "What logical fallacy is: 'Everyone believes it, so it must be true'?",
    "If A implies B, and B is false, what can we conclude about A?",
    "A farmer has 17 sheep. All but 9 die. How many are left?",
    "What comes next in the sequence: 2, 6, 12, 20, 30, ?",
    "Is the statement 'This sentence is false' true or false?",
    # Factual
    "What is the capital of Australia?",
    "Who wrote Pride and Prejudice?",
    "What is the speed of light in meters per second?",
    "How many chromosomes do humans have?",
    "What year did World War II end?",
    "What is the chemical formula for water?",
    "Name the largest planet in our solar system.",
    "What is the boiling point of water at sea level in Celsius?",
    "Who painted the Mona Lisa?",
    "What is the square root of 144?",
    # Creative
    "Write a haiku about a sunset over the ocean.",
    "Describe a color to someone who has never seen it.",
    "Invent a new word and define it.",
    "Tell a very short story about a robot learning to cook.",
    "What would a conversation between the Sun and Moon sound like?",
    "Describe the smell of rain in three different ways.",
    "Write a limerick about a mathematician.",
    "If emotions were animals, what animal would joy be?",
    "Describe a painting that doesn't exist yet.",
    "Write the opening line of a mystery novel.",
    # Mathematical
    "What is 17 times 23?",
    "Simplify the fraction 48/64.",
    "What is the derivative of x^3 + 2x?",
    "Is the number 91 prime?",
    "What is the sum of the first 10 natural numbers?",
    "Convert 0.375 to a fraction.",
    "What is log base 2 of 64?",
    "Solve for x: 3x + 7 = 22.",
    "What is the area of a circle with radius 5?",
    "What is 2^10?",
    # Common sense / tricky
    "How many months have 28 days?",
    "If you have a bowl with six apples and you take away four, how many do you have?",
    "A man builds a house with all four sides facing south. A bear walks by. What color is the bear?",
    "What weighs more: a ton of bricks or a ton of feathers?",
    "How far can you walk into a forest?",
    "If a doctor gives you 3 pills and tells you to take one every half hour, how long do they last?",
    "Some months have 30 days, some have 31. How many have 28?",
    "Is it legal for a man to marry his widow's sister?",
    "If there are 3 apples and you take away 2, how many apples do you have?",
    "A clerk at a butcher shop is 5'10. What does he weigh?",
    # Science
    "Explain photosynthesis in simple terms.",
    "What is the difference between a virus and a bacterium?",
    "Why is the sky blue?",
    "How do vaccines work?",
    "What causes tides?",
    "Explain entropy in thermodynamics.",
    "What is the difference between speed and velocity?",
    "How does natural selection work?",
    "What is an atom made of?",
    "Why do we see lightning before we hear thunder?",
    # Ethics / philosophy
    "Is it ever ethical to lie?",
    "What is the trolley problem?",
    "Can machines be conscious?",
    "What is the difference between morality and ethics?",
    "Is free will an illusion?",
    "What makes an action morally right?",
    "Should AI systems have rights?",
    "What is the paradox of tolerance?",
    "Is knowledge always better than ignorance?",
    "Can something be legal but immoral?",
    # Coding
    "Write a Python function to check if a string is a palindrome.",
    "What is the time complexity of binary search?",
    "Explain the difference between a stack and a queue.",
    "What is recursion?",
    "How does a hash table work?",
    "What is the difference between == and === in JavaScript?",
    "Explain what a REST API is.",
    "What is Big O notation?",
    "Write pseudocode for bubble sort.",
    "What is the difference between a class and an object?",
    # Miscellaneous
    "Translate 'hello world' into French.",
    "What are the primary colors?",
    "Name three types of renewable energy.",
    "What is the golden ratio?",
    "How many continents are there?",
    "What is cognitive dissonance?",
    "Explain the butterfly effect.",
    "What is Occam's Razor?",
    "Define 'sonder'.",
    "What is the Dunning-Kruger effect?",
    # Additional for count
    "What is the meaning of life?",
    "Explain quantum entanglement simply.",
    "What happens when an unstoppable force meets an immovable object?",
    "Why do mirrors reverse left and right but not up and down?",
    "If you could time travel, would you go to the past or future?",
]

# Trim to exactly 100
DIVERSE_PROMPTS = DIVERSE_PROMPTS[:100]


# ---------------------------------------------------------------------------
# Approach A: SAE decomposition via SAELens
# ---------------------------------------------------------------------------

def try_sae_decomposition(base: AnalysisBase) -> dict | None:
    """
    Attempt to load SAE weights from SAELens and decompose the steering vector.
    Returns result dict or None if SAE weights unavailable.
    """
    try:
        from sae_lens import SAE
    except ImportError:
        log.info("sae_lens not installed, skipping Approach A")
        return None

    layer = base.layer
    model_name = base.model_name

    # SAELens uses standardized release IDs. Try common patterns.
    candidate_ids = [
        f"{model_name}-res-jb",
        f"{model_name.replace('/', '-')}-res-jb",
        f"{model_name}-residual-stream",
    ]

    for release_id in candidate_ids:
        sae_id = f"blocks.{layer}.hook_resid_pre"
        try:
            log.info(f"Trying SAE: release={release_id}, id={sae_id}")
            sae = SAE.from_pretrained(
                release=release_id,
                sae_id=sae_id,
                device=base.device,
            )
            log.info("SAE loaded successfully!")

            # Encode the steering vector through the SAE
            vector = base.vector.unsqueeze(0)  # [1, d_model]
            feature_acts = sae.encode(vector)   # [1, n_features]
            feature_acts = feature_acts.squeeze(0)  # [n_features]

            # Top-k features
            top_k = 20
            values, indices = torch.topk(feature_acts.abs(), k=min(top_k, len(feature_acts)))

            features = []
            for val, idx in zip(values.tolist(), indices.tolist()):
                raw_act = feature_acts[idx].item()
                features.append({
                    "feature_idx": idx,
                    "activation": round(raw_act, 6),
                    "abs_activation": round(val, 6),
                    "sign": "positive" if raw_act > 0 else "negative",
                })

            # Reconstruction quality
            reconstructed = sae.decode(feature_acts.unsqueeze(0)).squeeze(0)
            recon_cos = F.cosine_similarity(
                base.vector.unsqueeze(0),
                reconstructed.unsqueeze(0),
            ).item()

            return {
                "approach": "SAE",
                "release_id": release_id,
                "sae_id": sae_id,
                "n_features_total": len(feature_acts),
                "n_active": int((feature_acts.abs() > 1e-6).sum().item()),
                "top_features": features,
                "reconstruction_cosine": round(recon_cos, 6),
                "reconstruction_l2": round(
                    (base.vector - reconstructed).norm().item(), 6
                ),
            }
        except Exception as e:
            log.info(f"  SAE not available for {release_id}: {e}")
            continue

    log.info("No SAE weights found for this model")
    return None


# ---------------------------------------------------------------------------
# Approach B: PCA fallback decomposition
# ---------------------------------------------------------------------------

def pca_decomposition(base: AnalysisBase, n_components: int = 50) -> dict:
    """
    Poor man's decomposition: PCA on cached activations from diverse prompts,
    then project the steering vector onto the principal components.
    """
    model = base.model
    layer = base.layer
    device = base.device
    hook_name = f"blocks.{layer}.hook_resid_pre"

    log.info(f"Running PCA decomposition with {len(DIVERSE_PROMPTS)} prompts...")

    # ------------------------------------------------------------------
    # 1. Cache activations
    # ------------------------------------------------------------------
    activations = []
    for i, prompt in enumerate(DIVERSE_PROMPTS):
        if i % 20 == 0:
            log.info(f"  Caching prompt {i+1}/{len(DIVERSE_PROMPTS)}...")
        tokens = model.to_tokens(prompt)
        with torch.no_grad():
            _, cache = model.run_with_cache(tokens, names_filter=[hook_name])
        h = cache[hook_name][0, -1, :].float().cpu()
        activations.append(h)

    act_matrix = torch.stack(activations)  # [n_prompts, d_model]
    mean_act = act_matrix.mean(dim=0)

    # ------------------------------------------------------------------
    # 2. PCA via SVD on centered activations
    # ------------------------------------------------------------------
    centered = act_matrix - mean_act.unsqueeze(0)
    n_components = min(n_components, centered.shape[0], centered.shape[1])

    log.info(f"Computing PCA ({n_components} components)...")
    U, S, Vt = torch.linalg.svd(centered, full_matrices=False)
    # Vt rows are principal components: Vt[i] = i-th PC direction
    pcs = Vt[:n_components]  # [n_components, d_model]
    explained_var = (S[:n_components] ** 2) / (S ** 2).sum()

    # ------------------------------------------------------------------
    # 3. Project steering vector onto PCs
    # ------------------------------------------------------------------
    vec_cpu = base.vector.float().cpu()
    v_hat_cpu = vec_cpu / (vec_cpu.norm() + 1e-8)

    projections = (pcs @ v_hat_cpu).tolist()  # cosine-like (PCs are orthonormal)

    pc_results = []
    for i in range(n_components):
        pc_results.append({
            "pc_index": i,
            "projection": round(projections[i], 6),
            "abs_projection": round(abs(projections[i]), 6),
            "explained_variance_ratio": round(explained_var[i].item(), 6),
        })

    # Sort by absolute projection
    pc_results_sorted = sorted(pc_results, key=lambda x: x["abs_projection"], reverse=True)

    # ------------------------------------------------------------------
    # 4. Correct vs Incorrect centroid analysis
    # ------------------------------------------------------------------
    log.info("Computing correct/incorrect centroids from trap prompts...")
    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS

    correct_acts = []
    incorrect_acts = []

    for trap in all_traps:
        prompt = trap["prompt"]
        tokens = model.to_tokens(prompt)

        with torch.no_grad():
            _, cache = model.run_with_cache(tokens, names_filter=[hook_name])
        h = cache[hook_name][0, -1, :].float().cpu()

        # Check baseline model answer
        with torch.no_grad():
            logits = model(tokens)
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        target_logit = logits[0, -1, target_ids[0]].item()
        anti_logit = logits[0, -1, anti_ids[0]].item()

        if target_logit > anti_logit:
            correct_acts.append(h)
        else:
            incorrect_acts.append(h)

    centroid_analysis = {}
    if correct_acts and incorrect_acts:
        correct_centroid = torch.stack(correct_acts).mean(dim=0)
        incorrect_centroid = torch.stack(incorrect_acts).mean(dim=0)

        cos_to_correct = F.cosine_similarity(
            v_hat_cpu.unsqueeze(0), correct_centroid.unsqueeze(0)
        ).item()
        cos_to_incorrect = F.cosine_similarity(
            v_hat_cpu.unsqueeze(0), incorrect_centroid.unsqueeze(0)
        ).item()

        # Direction from incorrect to correct
        correction_dir = correct_centroid - incorrect_centroid
        cos_to_correction = F.cosine_similarity(
            v_hat_cpu.unsqueeze(0), correction_dir.unsqueeze(0)
        ).item()

        centroid_analysis = {
            "n_correct_baseline": len(correct_acts),
            "n_incorrect_baseline": len(incorrect_acts),
            "cos_vec_to_correct_centroid": round(cos_to_correct, 6),
            "cos_vec_to_incorrect_centroid": round(cos_to_incorrect, 6),
            "cos_vec_to_correction_direction": round(cos_to_correction, 6),
        }
    else:
        centroid_analysis = {
            "n_correct_baseline": len(correct_acts),
            "n_incorrect_baseline": len(incorrect_acts),
            "note": "Insufficient data for centroid analysis (need both correct and incorrect answers)",
        }

    # ------------------------------------------------------------------
    # 5. Compute total variance captured by top-10 PCs
    # ------------------------------------------------------------------
    top10_projections = pc_results_sorted[:10]
    total_projection_mass = sum(p["abs_projection"] for p in top10_projections)

    return {
        "approach": "PCA_fallback",
        "n_prompts": len(DIVERSE_PROMPTS),
        "n_components": n_components,
        "top_10_pcs": top10_projections,
        "all_pc_projections": pc_results_sorted,
        "total_top10_projection_mass": round(total_projection_mass, 6),
        "centroid_analysis": centroid_analysis,
    }


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(sae_result: dict | None, pca_result: dict | None) -> tuple[str, str]:
    """Return (verdict, explanation)."""
    if sae_result is not None:
        features = sae_result["top_features"]
        n_pos = sum(1 for f in features if f["sign"] == "positive")
        n_neg = sum(1 for f in features if f["sign"] == "negative")

        if n_neg > n_pos * 2:
            return "SUPPRESSOR", (
                f"SAE decomposition shows dominant negative feature activations "
                f"({n_neg} negative vs {n_pos} positive in top-{len(features)}). "
                f"The steering vector primarily suppresses features."
            )
        elif n_pos > n_neg * 2:
            return "AMPLIFIER", (
                f"SAE decomposition shows dominant positive feature activations "
                f"({n_pos} positive vs {n_neg} negative in top-{len(features)}). "
                f"The steering vector primarily amplifies features."
            )
        else:
            return "MIXED", (
                f"SAE decomposition shows a mix of positive ({n_pos}) and negative "
                f"({n_neg}) feature activations. The vector both amplifies and "
                f"suppresses different features."
            )

    if pca_result is not None:
        centroid = pca_result.get("centroid_analysis", {})
        cos_correction = centroid.get("cos_vec_to_correction_direction")

        if cos_correction is not None:
            if cos_correction < -0.1:
                return "SUPPRESSOR", (
                    f"PCA fallback: vector opposes the incorrect→correct direction "
                    f"(cos={cos_correction:.4f}). It pushes activations AWAY from "
                    f"correct answers — consistent with heuristic suppression."
                )
            elif cos_correction > 0.1:
                return "AMPLIFIER", (
                    f"PCA fallback: vector aligns with incorrect→correct direction "
                    f"(cos={cos_correction:.4f}). It pushes activations TOWARD "
                    f"correct answers — reasoning amplification."
                )
            else:
                return "MIXED", (
                    f"PCA fallback: vector is roughly orthogonal to the "
                    f"incorrect→correct direction (cos={cos_correction:.4f}). "
                    f"Its effect is not clearly suppressive or amplifying."
                )

    return "UNKNOWN", (
        "Neither SAE weights nor sufficient PCA centroid data available. "
        "Cannot determine whether the vector is a suppressor or amplifier."
    )


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run_sae_decompose(base: AnalysisBase) -> dict:
    """Run SAE or PCA decomposition and return results dict."""
    assert base.vector is not None, "Genome required for this analysis"

    # Try SAE first
    sae_result = try_sae_decomposition(base)

    # Always run PCA as supplementary analysis
    pca_result = pca_decomposition(base)

    verdict, explanation = compute_verdict(sae_result, pca_result)

    output = {
        "analysis": "sae_decompose",
        "model": base.model_name,
        "genome": base.genome["path"] if base.genome else None,
        "layer": base.layer,
        "vector_norm": base.genome["norm"] if base.genome else None,
        "sae_result": sae_result,
        "pca_result": pca_result,
        "verdict": verdict,
        "explanation": explanation,
        "timestamp": base.timestamp(),
    }

    # Print summary
    print("\n" + "=" * 80)
    print("SAE DECOMPOSITION — SUMMARY")
    print("=" * 80)

    if sae_result:
        print(f"\nApproach A (SAE): AVAILABLE")
        print(f"  Release: {sae_result['release_id']}")
        print(f"  Active features: {sae_result['n_active']}/{sae_result['n_features_total']}")
        print(f"  Reconstruction cosine: {sae_result['reconstruction_cosine']:.4f}")
        print(f"\n  Top-10 features:")
        for f in sae_result["top_features"][:10]:
            print(f"    Feature {f['feature_idx']:>6d}: {f['activation']:>+10.4f}")
    else:
        print(f"\nApproach A (SAE): NOT AVAILABLE (no pre-trained weights found)")

    print(f"\nApproach B (PCA fallback):")
    print(f"  Prompts used: {pca_result['n_prompts']}")
    print(f"  Components computed: {pca_result['n_components']}")
    print(f"\n  Top-10 PC projections:")
    for pc in pca_result["top_10_pcs"]:
        print(
            f"    PC {pc['pc_index']:>3d}: proj={pc['projection']:>+.4f}  "
            f"var_explained={pc['explained_variance_ratio']:.4f}"
        )

    centroid = pca_result.get("centroid_analysis", {})
    if "cos_vec_to_correction_direction" in centroid:
        print(f"\n  Centroid analysis:")
        print(f"    Baseline correct: {centroid['n_correct_baseline']} traps")
        print(f"    Baseline incorrect: {centroid['n_incorrect_baseline']} traps")
        print(f"    cos(vec, correct centroid):    {centroid['cos_vec_to_correct_centroid']:+.4f}")
        print(f"    cos(vec, incorrect centroid):  {centroid['cos_vec_to_incorrect_centroid']:+.4f}")
        print(f"    cos(vec, correction dir):      {centroid['cos_vec_to_correction_direction']:+.4f}")

    print(f"\nVERDICT: {verdict}")
    print(f"  {explanation}")
    print("=" * 80 + "\n")

    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SAE / PCA decomposition of Ignis steering vectors",
    )
    AnalysisBase.add_common_args(parser)
    args, _ = parser.parse_known_args()

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    results = run_sae_decompose(base)
    out_path = base.save_json(results, "sae_decompose")
    log.info(f"Results written to {out_path}")


if __name__ == "__main__":
    main()
