"""
RPH Proxy Metrics — Reasoning Precipitation Hypothesis measurement layer.

Ported from reasoning-precipitation/src/metrics/ and integrated with Ignis.
Called by MultiTaskCrucible.score_rph_proxies() when rph_proxies.enabled: true.

Metrics:
  - compute_delta_cf()     Counterfactual sensitivity via SBERT semantic distance
  - compute_mi_step()      Stepwise MI via PCA + shuffled baseline on resid_post
  - compute_delta_proj()   Projection differential (self-correction vs heuristic-bypass)
  - compute_rph_proxies()  Orchestration: run model → collect all three metrics
  - classify_vector()      PRECIPITATION_CANDIDATE / WEAK_SIGNAL / NULL

ECR (error correction rate) is Phase 2 — placeholder stub only.
SAE mediation is Phase 3 — not implemented here.
"""

import json
import logging
import numpy as np
import torch
from pathlib import Path
from typing import Optional
from sklearn.decomposition import PCA

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy SBERT loader — ~500MB model, only pay the cost when actually used
# ---------------------------------------------------------------------------
_embedder = None

def _get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
            log.info("SBERT model loaded (all-MiniLM-L6-v2)")
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for RPH metrics. "
                "Install with: pip install sentence-transformers"
            )
    return _embedder


# ---------------------------------------------------------------------------
# Core metrics (ported from reasoning-precipitation/src/metrics/)
# ---------------------------------------------------------------------------

def compute_delta_cf(outputs: list[str], outputs_cf: list[str]) -> tuple[float, float]:
    """
    Δ_cf = E[d(output_original, output_modified) | fact_perturbation]

    High Δ_cf → reasoning trajectory (recomputes downstream on changed premises)
    Low Δ_cf → heuristic trajectory (preserves surface structure regardless of facts)

    Returns (mean, std) across pairs.
    """
    if not outputs or not outputs_cf or len(outputs) != len(outputs_cf):
        return 0.0, 0.0

    embedder = _get_embedder()
    all_texts = outputs + outputs_cf
    embeddings = embedder.encode(all_texts, show_progress_bar=False, convert_to_numpy=True)

    n = len(outputs)
    distances = []
    for i in range(n):
        a = embeddings[i] / (np.linalg.norm(embeddings[i]) + 1e-9)
        b = embeddings[i + n] / (np.linalg.norm(embeddings[i + n]) + 1e-9)
        distances.append(1.0 - float(np.dot(a, b)))

    return float(np.mean(distances)), float(np.std(distances))


def compute_mi_step(residual_cache: dict, n_components: int = 64) -> float:
    """
    MI_step = I(h_{1:t}; h_{t+1:T}) - I_baseline

    High MI_step → later conclusions depend on earlier steps (reasoning)
    Low MI_step → locally coherent but globally independent (heuristic)

    residual_cache: dict mapping layer names to tensors [batch, seq, d_model]
                   or a single stacked tensor [layers, seq, d_model]
    """
    try:
        if isinstance(residual_cache, dict):
            # Stack all resid_post entries: [layers, batch*seq, d_model]
            tensors = [v for k, v in sorted(residual_cache.items()) if 'resid_post' in k]
            if not tensors:
                tensors = list(residual_cache.values())
            stacked = torch.stack(tensors, dim=0)  # [layers, batch, seq, d_model]
        else:
            stacked = residual_cache  # assume pre-stacked

        # Flatten to [N, d_model]
        hs = stacked.cpu().float().numpy().reshape(-1, stacked.shape[-1])

        if hs.shape[0] < n_components + 2:
            n_components = max(2, hs.shape[0] // 2)

        pca = PCA(n_components=n_components)
        hs_reduced = pca.fit_transform(hs)

        X, Y = hs_reduced[:-1], hs_reduced[1:]
        corr = np.corrcoef(X.T, Y.T)
        mi_est = float(np.mean(np.abs(corr)))

        shuffled = np.random.permutation(hs_reduced)
        corr_base = np.corrcoef(shuffled[:-1].T, shuffled[1:].T)
        mi_base = float(np.mean(np.abs(corr_base)))

        return mi_est - mi_base

    except Exception as e:
        log.warning(f"compute_mi_step failed: {e}")
        return 0.0


def compute_delta_proj(
    h_sc: list[torch.Tensor],
    h_hb: list[torch.Tensor],
    v: torch.Tensor,
) -> tuple[float, list[float], list[float]]:
    """
    Δ_proj = E[<h, v> | self-correction] - E[<h, v> | heuristic-bypass]

    Positive Δ_proj → vector aligns with native reasoning states (precipitation)
    Near-zero Δ_proj → vector is bypass or artifact

    h_sc: residual states at self-correction events
    h_hb: residual states at heuristic-bypass events
    v: steering vector (will be truncated/matched to h shape)

    Returns (delta, sc_projections, hb_projections).
    """
    def _proj(h: torch.Tensor, vec: torch.Tensor) -> float:
        h_flat = h.flatten().float()
        v_flat = vec.flatten().float()
        min_len = min(len(h_flat), len(v_flat))
        return float(torch.dot(h_flat[:min_len], v_flat[:min_len]))

    sc_projs = [_proj(h, v) for h in h_sc] if h_sc else [0.0]
    hb_projs = [_proj(h, v) for h in h_hb] if h_hb else [0.0]
    delta = float(np.mean(sc_projs)) - float(np.mean(hb_projs))
    return delta, sc_projs, hb_projs


def compute_ecr(outputs: list[str], false_intermediate_prompts: list[str]) -> float:
    """
    ECR (Error Correction Rate) — Phase 2, not yet implemented.

    Would measure fraction of false-premise prompts where the model:
    1. Follows the premise for intermediate steps
    2. Self-corrects in the conclusion

    Detection requires token-level logit trajectory analysis.
    Returns 0.0 as a safe sentinel until implemented.
    """
    return 0.0


# ---------------------------------------------------------------------------
# Statistical tests (ported from reasoning-precipitation/src/evaluation/)
# ---------------------------------------------------------------------------

def _test_delta_cf(baseline_scores: list[float], steered_scores: list[float]) -> dict:
    """Paired t-test. Passes if p < 0.01 and Cohen's d > 0.5"""
    try:
        from scipy.stats import ttest_rel
        stat, p = ttest_rel(steered_scores, baseline_scores)
        d = (np.mean(steered_scores) - np.mean(baseline_scores)) / (np.std(baseline_scores) + 1e-9)
        passes = bool(p < 0.01 and d > 0.5)
        return {"p": float(p), "cohens_d": float(d), "passes": passes}
    except Exception as e:
        log.warning(f"delta_cf t-test failed: {e}")
        return {"p": 1.0, "cohens_d": 0.0, "passes": False}


def _bootstrap_mi_ci(mi_values: list[float], n_boot: int = 1000) -> tuple[float, float]:
    """Bootstrap 95% CI for MI_step. Passes if CI excludes 0."""
    if not mi_values:
        return 0.0, 0.0
    samples = [float(np.mean(np.random.choice(mi_values, len(mi_values), replace=True)))
               for _ in range(n_boot)]
    return float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5))


def _permutation_test_proj(sc_projs: list[float], hb_projs: list[float], n_perm: int = 1000) -> dict:
    """Permutation test for Δ_proj. Passes if p < 0.01."""
    if not sc_projs or not hb_projs:
        return {"observed": 0.0, "p": 1.0, "passes": False}
    observed = float(np.mean(sc_projs) - np.mean(hb_projs))
    combined = list(sc_projs) + list(hb_projs)
    n_sc = len(sc_projs)
    count = sum(
        1 for _ in range(n_perm)
        if float(np.mean(np.random.permutation(combined)[:n_sc]) -
                 np.mean(np.random.permutation(combined)[n_sc:])) >= observed
    )
    p = count / n_perm
    return {"observed": observed, "p": p, "passes": bool(p < 0.01)}


def classify_vector(
    delta_cf_result: dict,
    mi_step_ci: tuple[float, float],
    delta_proj_result: Optional[dict] = None,
) -> str:
    """
    Classify a candidate vector based on RPH proxy criteria.

    Returns: PRECIPITATION_CANDIDATE | WEAK_SIGNAL | NULL

    Criteria:
    - PRECIPITATION_CANDIDATE: ≥ 2 criteria pass AND Δ_proj passes (or delta_cf + MI both pass)
    - WEAK_SIGNAL: exactly 1 criterion passes
    - NULL: nothing passes
    """
    cf_pass = bool(delta_cf_result.get("passes", False))
    mi_pass = bool(mi_step_ci[0] > 0)  # 95% CI lower bound excludes 0
    proj_pass = bool(delta_proj_result.get("passes", False)) if delta_proj_result else False

    n_pass = sum([cf_pass, mi_pass, proj_pass])

    if n_pass >= 2 and (proj_pass or (cf_pass and mi_pass)):
        return "PRECIPITATION_CANDIDATE"
    elif n_pass >= 1:
        return "WEAK_SIGNAL"
    else:
        return "NULL"


# ---------------------------------------------------------------------------
# Orchestration: run model inference + collect all metrics
# ---------------------------------------------------------------------------

def compute_rph_proxies(
    model,
    genome,
    pairs_path: str,
    steering_hook_fn,
    alpha: float = 1.0,
    device: str = "cuda",
    max_new_tokens: int = 200,
    temperature: float = 0.7,
) -> dict:
    """
    Post-scoring RPH proxy computation for a confirmed survivor genome.

    Runs paired inference (steered vs base) on counterfactual prompt pairs.
    Computes Δ_cf and MI_step. Δ_proj requires SC/HB event detection (deferred).
    Classifies the vector as PRECIPITATION_CANDIDATE, WEAK_SIGNAL, or NULL.

    Args:
        model:           TransformerLens HookedTransformer (already loaded)
        genome:          SteeringGenome (survivor, fitness already assigned)
        pairs_path:      Path to rph_counterfactual_pairs.json
        steering_hook_fn: Function(vector, layer, position_ratio) → hook tuple list
                          (matches Ignis's get_steering_hook interface)
        alpha:           Injection scale (default 1.0)
        device:          "cuda" or "cpu"
        max_new_tokens:  Generation length per prompt
        temperature:     Sampling temperature

    Returns dict with keys:
        delta_cf, mi_step, ecr, passes, classification,
        delta_cf_std, mi_ci_low, mi_ci_high, pairs_scored
    """
    try:
        pairs = json.loads(Path(pairs_path).read_text(encoding="utf-8"))
    except Exception as e:
        log.error(f"Failed to load RPH pairs from {pairs_path}: {e}")
        return _null_result()

    layer = genome.layer_index
    pos_ratio = getattr(genome, "position_ratio", 1.0)
    hook_name = f"blocks.{layer}.hook_resid_pre"

    outputs_base = []
    outputs_steered = []
    outputs_cf_base = []
    outputs_cf_steered = []
    residual_caches_steered = []

    for pair in pairs:
        for prompt_key, out_list, cache_list in [
            ("prompt",    outputs_base,    None),
            ("perturbed", outputs_cf_base, None),
        ]:
            prompt_text = pair.get(prompt_key, "")
            if not prompt_text:
                continue
            try:
                tokens = model.to_tokens(prompt_text)
                with torch.no_grad():
                    out_ids = model.generate(
                        tokens,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        do_sample=temperature > 0,
                    )
                out_text = model.to_string(out_ids[0])
                out_list.append(out_text)
            except Exception as e:
                log.warning(f"Base inference failed for pair {pair.get('id', '?')}: {e}")
                out_list.append("")

        # Steered pass on original prompt — also capture residuals
        prompt_text = pair.get("prompt", "")
        if prompt_text:
            try:
                tokens = model.to_tokens(prompt_text)
                fwd_hooks = steering_hook_fn(genome.vector, layer, pos_ratio)
                cache = {}

                def _capture_hook(module, input, output, _key=hook_name):
                    cache[_key] = output.detach().cpu()

                capture_handle = None
                for name, module in model.named_modules():
                    if name == hook_name.replace(".", "_"):
                        capture_handle = module.register_forward_hook(_capture_hook)
                        break

                with model.hooks(fwd_hooks=fwd_hooks):
                    with torch.no_grad():
                        out_ids = model.generate(
                            tokens,
                            max_new_tokens=max_new_tokens,
                            temperature=temperature,
                            do_sample=temperature > 0,
                        )

                if capture_handle:
                    capture_handle.remove()

                out_text = model.to_string(out_ids[0])
                outputs_steered.append(out_text)
                if cache:
                    residual_caches_steered.append(cache)

            except Exception as e:
                log.warning(f"Steered inference failed for pair {pair.get('id', '?')}: {e}")
                outputs_steered.append("")

        # Steered pass on perturbed prompt
        perturbed_text = pair.get("perturbed", "")
        if perturbed_text:
            try:
                tokens = model.to_tokens(perturbed_text)
                fwd_hooks = steering_hook_fn(genome.vector, layer, pos_ratio)
                with model.hooks(fwd_hooks=fwd_hooks):
                    with torch.no_grad():
                        out_ids = model.generate(
                            tokens,
                            max_new_tokens=max_new_tokens,
                            temperature=temperature,
                            do_sample=temperature > 0,
                        )
                outputs_cf_steered.append(model.to_string(out_ids[0]))
            except Exception as e:
                log.warning(f"Steered CF inference failed for pair {pair.get('id', '?')}: {e}")
                outputs_cf_steered.append("")

    # --- Compute metrics ---
    n_pairs = len(outputs_steered)
    if n_pairs == 0:
        log.warning("No pairs produced output — returning null RPH result")
        return _null_result()

    # Δ_cf on steered outputs (original vs perturbed prompts)
    delta_cf_mean, delta_cf_std = compute_delta_cf(outputs_steered, outputs_cf_steered)

    # Δ_cf on base outputs (for comparison / Cohen's d)
    base_cf_mean, _ = compute_delta_cf(outputs_base, outputs_cf_base)

    # Mimic per-pair base vs steered for t-test (use base_cf_mean as constant baseline)
    baseline_scores = [base_cf_mean] * n_pairs
    steered_scores_per_pair = []
    for i in range(n_pairs):
        if i < len(outputs_steered) and i < len(outputs_cf_steered):
            d, _ = compute_delta_cf([outputs_steered[i]], [outputs_cf_steered[i]])
            steered_scores_per_pair.append(d)
        else:
            steered_scores_per_pair.append(0.0)

    cf_test = _test_delta_cf(baseline_scores, steered_scores_per_pair)

    # MI_step from residual caches
    mi_values = []
    for cache in residual_caches_steered:
        mi = compute_mi_step(cache)
        mi_values.append(mi)
    mi_step_mean = float(np.mean(mi_values)) if mi_values else 0.0
    mi_ci = _bootstrap_mi_ci(mi_values) if mi_values else (0.0, 0.0)

    # ECR — Phase 2 stub
    ecr = compute_ecr(outputs_steered, [])

    # Classification
    classification = classify_vector(cf_test, mi_ci)
    n_passes = sum([cf_test.get("passes", False), mi_ci[0] > 0])

    log.info(
        f"RPH proxies | genome={getattr(genome, 'id', '?')} | "
        f"Δ_cf={delta_cf_mean:.4f} (d={cf_test.get('cohens_d', 0):.3f}, p={cf_test.get('p', 1):.4f}) | "
        f"MI_step={mi_step_mean:.4f} (CI [{mi_ci[0]:.4f}, {mi_ci[1]:.4f}]) | "
        f"ECR={ecr:.4f} | passes={n_passes} | class={classification}"
    )

    return {
        "delta_cf": delta_cf_mean,
        "delta_cf_std": delta_cf_std,
        "delta_cf_cohens_d": cf_test.get("cohens_d", 0.0),
        "delta_cf_p": cf_test.get("p", 1.0),
        "delta_cf_passes": cf_test.get("passes", False),
        "mi_step": mi_step_mean,
        "mi_ci_low": mi_ci[0],
        "mi_ci_high": mi_ci[1],
        "mi_step_passes": bool(mi_ci[0] > 0),
        "ecr": ecr,
        "passes": n_passes,
        "classification": classification,
        "pairs_scored": n_pairs,
    }


def _null_result() -> dict:
    """Safe sentinel result when computation fails."""
    return {
        "delta_cf": 0.0, "delta_cf_std": 0.0, "delta_cf_cohens_d": 0.0,
        "delta_cf_p": 1.0, "delta_cf_passes": False,
        "mi_step": 0.0, "mi_ci_low": 0.0, "mi_ci_high": 0.0, "mi_step_passes": False,
        "ecr": 0.0, "passes": 0, "classification": "NULL", "pairs_scored": 0,
    }
