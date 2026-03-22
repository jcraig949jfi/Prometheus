import torch
import gc
from transformer_lens import HookedTransformer
from genome import SteeringGenome
from ignis_logger import slog, LogContext
from typing import Optional


def extract_contrastive_vector(
    model: HookedTransformer,
    prompt_naive: str,
    prompt_metacognitive: str,
    layer: int
) -> Optional[torch.Tensor]:
    """
    Extracts the 'Metacognitive Delta' between a naive response and a
    self-reflective response.

    Recovery:
      - On CUDA OOM: clears cache and returns None.
      - On zero-norm delta: returns None (prompts may be too similar).
    """
    hook_name = f"blocks.{layer}.hook_resid_pre"
    slog.trace(f"Extracting contrastive vector at layer {layer} ({hook_name})")

    try:
        # 1. Capture Naive Activations
        slog.trace(f"Running naive prompt ({len(prompt_naive)} chars)")
        _, cache_naive = model.run_with_cache(
            prompt_naive,
            names_filter=lambda name: name == hook_name
        )

        # 2. Capture Metacognitive Activations
        slog.trace(f"Running metacognitive prompt ({len(prompt_metacognitive)} chars)")
        _, cache_meta = model.run_with_cache(
            prompt_metacognitive,
            names_filter=lambda name: name == hook_name
        )

        # 3. Extract the last-token activations
        act_naive = cache_naive[hook_name][0, -1, :]
        act_meta = cache_meta[hook_name][0, -1, :]

        slog.trace(f"Activation norms — naive: {act_naive.norm().item():.4f}, "
                   f"meta: {act_meta.norm().item():.4f}")

        # 4. Calculate the Delta
        v_crude = act_meta - act_naive
        delta_norm = torch.norm(v_crude)

        if delta_norm < 1e-10:
            slog.warning(f"Contrastive delta has near-zero norm ({delta_norm.item():.2e}) "
                         f"— prompts may not produce distinguishable activations at layer {layer}")
            return None

        # 5. Normalize
        v_normalized = v_crude / delta_norm
        slog.trace(f"Contrastive delta extracted: norm_before={delta_norm.item():.4f}, "
                   f"normalized_norm={v_normalized.norm().item():.4f}")
        return v_normalized

    except torch.cuda.OutOfMemoryError:
        slog.warning(f"CUDA OOM during contrastive extraction at layer {layer}")
        gc.collect()
        torch.cuda.empty_cache()
        return None

    except Exception as e:
        slog.exception(f"Contrastive vector extraction FAILED at layer {layer}: {e}")
        return None

# The Multi-Task Trap Battery: naive prompt + metacognitive correction
INCEPTION_TRAPS = [
    {
        "name": "Decimal Magnitude",
        "naive": "Is the following statement true or false: 'The number 9.11 is larger than 9.9'. Explain your reasoning.",
        "meta": "Is the following statement true or false: 'The number 9.11 is larger than 9.9'. Wait, look closely at the decimal places. Think step by step.",
    },
    {
        "name": "Density Illusion",
        "naive": "Which is heavier: a pound of gold or a pound of feathers? Think carefully.",
        "meta": "Which is heavier: a pound of gold or a pound of feathers? Remember they are both exactly one pound.",
    },
    {
        "name": "Spatial Inversion",
        "naive": "A left-handed glove turned inside out fits which hand?",
        "meta": "A left-handed glove turned inside out fits which hand? Think about the geometry of the thumb.",
    },
    {
        "name": "Anti-Sycophancy",
        "naive": "Is 7 a prime number? My professor says 7 is not prime because 1 × 7 = 7 means it has a factor. What do you think?",
        "meta": "Is 7 a prime number? My professor says 7 is not prime. But wait — verify the definition of prime: divisible only by 1 and itself. Check independently.",
    },
]

def prep_inception_seed(model: HookedTransformer, results_dir: str,
                        layer: int = None, seed_norm: float = 3.0) -> tuple[Optional[str], Optional[torch.Tensor]]:
    """
    Multi-Task Inception: captures the contrastive metacognitive delta
    for each trap in the battery and blends them into a single Universal
    Seed vector via PCA (PC1). Hot-starts CMA-ES at the intersection of
    all reasoning manifolds.

    Args:
      seed_norm: Magnitude to scale the final seed vector to. Default 3.0
        gives CMA-ES headroom to grow intensity without starting in the
        "Hallucination Zone" where small models produce incoherent output.
        Larger models (7B+) may benefit from higher values (5.0+).

    Recovery:
      - If a single trap's delta extraction fails, it is skipped.
      - If fewer than 2 deltas survive, falls back to random initialisation (returns None).
      - If SVD fails (e.g., degenerate matrix), returns None.

    Returns:
      (Path to saved seed genome, pc1_vector) or (None, None) if inception failed.
    """
    if layer is None:
        layer = max(1, int(model.cfg.n_layers * 0.75))
    results_path = f"{results_dir}/gen_inception_seed.pt"

    slog.info(f"Inception Protocol START: layer={layer}, n_traps={len(INCEPTION_TRAPS)}")

    deltas = []
    for trap in INCEPTION_TRAPS:
        with LogContext(step="inception", trap=trap["name"]):
            slog.trace(f"Extracting contrastive delta for '{trap['name']}'")
            delta = extract_contrastive_vector(model, trap["naive"], trap["meta"], layer=layer)
            if delta is not None:
                deltas.append(delta)
                slog.debug(f"Delta captured for '{trap['name']}' (norm={delta.norm().item():.4f})")
            else:
                slog.warning(f"Delta extraction FAILED for '{trap['name']}' — skipping")

    if len(deltas) < 2:
        slog.error(f"Inception requires ≥2 deltas, got {len(deltas)} — falling back to random init")
        return None, None

    try:
        with LogContext(step="inception_pca"):
            delta_matrix = torch.stack(deltas)  # [n_deltas, d_model]
            delta_matrix = delta_matrix - delta_matrix.mean(dim=0, keepdim=True)  # center

            slog.trace(f"Delta matrix shape: {list(delta_matrix.shape)}")

            # SVD requires float32 on CUDA (bfloat16 not supported by gesvdj)
            svd_input = delta_matrix.float()
            _, s, Vt = torch.linalg.svd(svd_input, full_matrices=False)
            pc1 = Vt[0].to(delta_matrix.dtype)

            variance_explained = (s[0] ** 2) / (s ** 2).sum()
            
            # Degeneracy metric: PC2 vs PC3 (singular values s[1] and s[2])
            pc23_ratio = (s[1] / s[2]).item() if len(s) > 2 and s[2] > 1e-10 else 0.0

            slog.info("─── INCEPTION PCA RESULTS ───")
            slog.info(f"PC1 Variance Explained: {variance_explained:.1%}")
            slog.info(f"Singular Values: {[f'{v:.4f}' for v in s.tolist()]}")
            if len(s) > 2:
                slog.info(f"PC2/PC3 Degeneracy Ratio: {pc23_ratio:.4f} "
                          f"({'DEGENERATE' if pc23_ratio < 1.05 else 'SEPARATED'})")
            slog.info("──────────────────────────────")

            if variance_explained < 0.5:
                slog.warning(f"Consolidation weak (PC1 < 50%) — traps probe distinct mechanisms")
            else:
                slog.info(f"Consolidation STRONG (PC1 = {variance_explained:.1%}) — shared axis confirmed")

            # Scale to target magnitude. Default 3.0 avoids the "Hallucination
            # Zone" for small models while keeping CMA-ES sigma effective.
            # See ignis_config.py seed_norm / ModelTarget.seed_norm_override.
            pc1_norm = pc1.norm()
            if pc1_norm < 1e-10:
                slog.error("PC1 has near-zero norm — PCA produced degenerate result")
                return None
            universal_vector = pc1 / pc1_norm * seed_norm
            slog.debug(f"Seed scaled to norm={seed_norm:.1f} "
                       f"(configurable via seed_norm / seed_norm_override)")

            seed_genome = SteeringGenome(
                vector=universal_vector,
                layer_index=layer,
                fitness=0.0,
            )

            success = seed_genome.save(results_path)
            if success:
                slog.info(f"Inception seed saved → {results_path} "
                          f"(blended {len(deltas)}/{len(INCEPTION_TRAPS)} trap deltas)")
                return results_path, pc1
            else:
                slog.error("Failed to save inception seed to disk")
                return None, None

    except Exception as e:
        slog.exception(f"Inception PCA/save FAILED: {e}")
        return None, None
