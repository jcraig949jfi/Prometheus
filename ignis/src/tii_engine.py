import torch
import gc
from transformer_lens import HookedTransformer
from typing import Optional
from ignis_logger import slog

# Sentinel returned when generation fails — callers must handle this
TII_GENERATION_FAILED = "[TII_GENERATION_FAILED]"


def get_steering_hook(
    vector: torch.Tensor,
    coeff: float = 1.0,
    position_ratio: float = 1.0,
    capture: Optional[dict] = None,
):
    """
    Creates a hook that injects the genome vector into the residual stream.

    position_ratio controls WHERE in the sequence to inject:
      0.0 = first token, 1.0 = last token (legacy default).
      Values in (0, 1) inject at floor(seq_len * position_ratio).
    This allows CMA-ES to evolve the injection site along the reasoning trace.

    capture: if a dict is provided, four mechanistic snapshot values are written into it
      before/after injection — pre_norm, post_norm, cos_with_residual, norm_ratio.
    """
    def steering_hook(resid, hook):
        # resid shape: [batch, seq_len, d_model]
        seq_len = resid.shape[1]
        pos = min(int(seq_len * position_ratio), seq_len - 1)

        if capture is not None:
            r = resid[0, pos, :].float()
            v = vector.float().reshape(-1)
            pre_norm = r.norm().item()
            cos_sim = (r @ v / (r.norm() * v.norm() + 1e-10)).item()

        resid[:, pos, :] = resid[:, pos, :] + (coeff * vector)

        if capture is not None:
            _post_norm = round(resid[0, pos, :].float().norm().item(), 4)
            capture["pre_norm"] = round(pre_norm, 4)
            capture["post_norm"] = _post_norm
            capture["cos_with_residual"] = round(cos_sim, 4)
            capture["norm_ratio"] = round(_post_norm / max(pre_norm, 1e-10), 4)

        return resid
    return steering_hook


def execute_tii_generation(
    model: HookedTransformer,
    prompt: str,
    genome,
    max_new_tokens: int = 128,
    _retry_count: int = 0,
    _max_retries: int = 1,
) -> str:
    """
    Run steered generation with the genome's vector injected at its target layer.

    Recovery strategy:
      - On CUDA OOM: free cache, retry once with halved max_new_tokens.
      - On any other exception: log and return TII_GENERATION_FAILED sentinel.
        Callers (fitness, probe_runner) treat the sentinel as a floor-score result.
    """
    layer = genome.layer_index
    vector = genome.vector

    slog.trace(f"TII generate: layer={layer}, vec_norm={vector.norm().item():.4f}, "
               f"max_tokens={max_new_tokens}, prompt_len={len(prompt)}")

    try:
        input_tokens = model.to_tokens(prompt)
        hook_name = f"blocks.{layer}.hook_resid_pre"
        pos_ratio = getattr(genome, 'position_ratio', 1.0)

        with model.hooks(fwd_hooks=[(hook_name, get_steering_hook(vector, position_ratio=pos_ratio))]):
            output_tokens = model.generate(
                input_tokens,
                max_new_tokens=max_new_tokens,
                stop_at_eos=True,
                verbose=False,
                prepend_bos=False,
            )

        result = model.to_string(output_tokens[0])
        slog.trace(f"TII output ({len(result)} chars): {result[:120]}...")
        return result

    except torch.cuda.OutOfMemoryError:
        slog.warning(f"CUDA OOM during TII generation (retry={_retry_count}/{_max_retries})")
        gc.collect()
        torch.cuda.empty_cache()

        if _retry_count < _max_retries:
            reduced_tokens = max(16, max_new_tokens // 2)
            slog.info(f"Retrying TII generation with max_new_tokens={reduced_tokens}")
            return execute_tii_generation(
                model, prompt, genome,
                max_new_tokens=reduced_tokens,
                _retry_count=_retry_count + 1,
                _max_retries=_max_retries,
            )
        slog.error("TII generation OOM — retries exhausted, returning failure sentinel")
        return TII_GENERATION_FAILED

    except Exception as e:
        slog.exception(f"TII generation FAILED (unexpected): {e}")
        return TII_GENERATION_FAILED


def _estimate_params_b(model_name: str) -> float:
    """Rough parameter count in billions from model name."""
    import re
    m = re.search(r'(\d+(?:\.\d+)?)[Bb]', model_name)
    return float(m.group(1)) if m else 1.0


def load_tii_model(model_name: str, device: str = "cuda") -> Optional[HookedTransformer]:
    """
    Load a HookedTransformer model.

    Recovery: on OOM, clears VRAM and retries once. On any other failure, returns None
    so the orchestrator can skip this model and continue the cycle.
    """
    slog.info(f"Loading TII model: {model_name} (device={device}, dtype=bfloat16)")

    for attempt in range(2):
        try:
            # For large models (7B+), fold_ln and center_unembed require
            # temporarily holding both original and processed weights in memory,
            # which can cause OS-level OOM kills before Python can catch them.
            # Use no_processing for models that exceed ~60% of total VRAM in bf16.
            n_params_b = _estimate_params_b(model_name)
            if n_params_b >= 7.0:
                slog.info(f"Large model ({n_params_b:.0f}B) — using from_pretrained_no_processing")
                model = HookedTransformer.from_pretrained_no_processing(
                    model_name,
                    device=device,
                    dtype=torch.bfloat16,
                )
            else:
                model = HookedTransformer.from_pretrained(
                    model_name,
                    device=device,
                    fold_ln=True,
                    center_unembed=True,
                    center_writing_weights=False,
                    dtype=torch.bfloat16,
                )
            slog.info(f"Model loaded: d_model={model.cfg.d_model}, n_layers={model.cfg.n_layers}")
            return model

        except torch.cuda.OutOfMemoryError:
            slog.warning(f"CUDA OOM loading {model_name} (attempt {attempt + 1}/2)")
            gc.collect()
            torch.cuda.empty_cache()
            if attempt == 0:
                slog.info("Retrying model load after VRAM cleanup…")
                continue
            slog.error(f"Cannot load {model_name} — insufficient VRAM after cleanup")
            return None

        except Exception as e:
            slog.exception(f"Model load FAILED for {model_name}: {e}")
            return None

    return None  # unreachable, but satisfies type checker
