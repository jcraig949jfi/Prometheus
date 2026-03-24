"""
Logit lens backward pass — L* detection and ejection analysis.

This is the core diagnostic shared between Ignis (microscope) and
Rhea (forge). Ignis uses it to study ejection in frontier models.
Rhea uses it as a fitness signal: we want L* to be ABSENT.

The logit lens applies the model's unembedding matrix at every layer
to read what the residual stream "believes" at each stage of processing.

Key metric: monotonicity of correct-answer probability across layers.
  - Monotonically increasing = reasoning gravity (what we want)
  - Spike then collapse = ejection at L* (what we're eliminating)
"""

import torch
import torch.nn.functional as F
from dataclasses import dataclass


@dataclass
class LogitLensResult:
    """Result of a logit lens backward pass on a single trap."""
    trap_name: str
    layer_probs: list[float]       # P(correct) at each layer
    target_token_id: int
    anti_token_id: int
    l_star: int | None             # layer where ejection occurs (None = no ejection)
    monotonicity: float            # 0.0 = chaotic, 1.0 = perfectly increasing
    survival: bool                 # correct token in top-5 at final layer
    top5_final: list[tuple[int, float]]  # (token_id, prob) top 5 at output


def logit_lens_pass(model, tokenizer, prompt: str,
                    target_token_id: int, anti_token_id: int,
                    trap_name: str = "") -> LogitLensResult:
    """
    Run a forward pass and apply the logit lens at every layer.

    Args:
        model: HuggingFace causal LM (or any model with lm_head and model.layers)
        tokenizer: corresponding tokenizer
        prompt: the trap prompt string
        target_token_id: token ID of the correct answer
        anti_token_id: token ID of the expected wrong answer
        trap_name: label for logging

    Returns:
        LogitLensResult with per-layer probabilities and diagnostics
    """
    device = next(model.parameters()).device
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Collect hidden states at every layer
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)

    hidden_states = outputs.hidden_states  # tuple of (batch, seq, hidden_dim)
    # hidden_states[0] = embedding output, [1..N] = after each transformer layer

    # Get the unembedding matrix (lm_head)
    unembed = model.lm_head.weight  # (vocab_size, hidden_dim)

    layer_probs = []
    for layer_idx, hidden in enumerate(hidden_states):
        last_token_hidden = hidden[0, -1, :]  # (hidden_dim,)

        # Apply unembedding: project hidden state to vocab logits
        logits = last_token_hidden @ unembed.T  # (vocab_size,)
        probs = F.softmax(logits.float(), dim=-1)

        p_target = probs[target_token_id].item()
        layer_probs.append(p_target)

    # Final layer analysis
    final_hidden = hidden_states[-1][0, -1, :]
    final_logits = final_hidden @ unembed.T
    final_probs = F.softmax(final_logits.float(), dim=-1)

    top5_ids = torch.topk(final_probs, 5).indices.tolist()
    top5 = [(tid, final_probs[tid].item()) for tid in top5_ids]
    survival = target_token_id in top5_ids

    # L* detection: find the layer where correct answer probability
    # drops most sharply after reaching its peak
    l_star = _detect_l_star(layer_probs)

    # Monotonicity: fraction of layer transitions where P(correct) increases
    monotonicity = _compute_monotonicity(layer_probs)

    return LogitLensResult(
        trap_name=trap_name,
        layer_probs=layer_probs,
        target_token_id=target_token_id,
        anti_token_id=anti_token_id,
        l_star=l_star,
        monotonicity=monotonicity,
        survival=survival,
        top5_final=top5,
    )


def _detect_l_star(layer_probs: list[float], threshold: float = 0.1) -> int | None:
    """
    Detect L*: the layer where ejection occurs.

    L* is defined as the layer after the peak where probability drops
    by more than `threshold` from the peak value. If no such drop exists,
    returns None (no ejection detected).
    """
    if len(layer_probs) < 3:
        return None

    peak_val = max(layer_probs)
    peak_idx = layer_probs.index(peak_val)

    # Look for a significant drop after the peak
    for i in range(peak_idx + 1, len(layer_probs)):
        if peak_val - layer_probs[i] > threshold:
            return i

    return None


def _compute_monotonicity(layer_probs: list[float]) -> float:
    """
    Compute monotonicity score: fraction of consecutive layer pairs
    where P(correct) is non-decreasing.

    1.0 = perfectly monotonically increasing (ideal reasoning gravity)
    0.0 = every transition is a decrease
    """
    if len(layer_probs) < 2:
        return 1.0

    increases = sum(
        1 for i in range(len(layer_probs) - 1)
        if layer_probs[i + 1] >= layer_probs[i]
    )
    return increases / (len(layer_probs) - 1)


def batch_logit_lens(model, tokenizer, traps, resolve_token_fn=None):
    """
    Run logit lens on an entire trap battery.

    Args:
        model: HuggingFace causal LM
        tokenizer: corresponding tokenizer
        traps: list of Trap objects (from traps.py)
        resolve_token_fn: optional function(token_str) -> token_id
                         defaults to tokenizer.encode

    Returns:
        list of LogitLensResult
    """
    results = []

    def _resolve(token_str):
        if resolve_token_fn:
            return resolve_token_fn(token_str)
        ids = tokenizer.encode(token_str, add_special_tokens=False)
        if len(ids) == 1:
            return ids[0]
        # Try with space prefix (common BPE pattern)
        ids = tokenizer.encode(" " + token_str, add_special_tokens=False)
        if len(ids) == 1:
            return ids[0]
        # Fall back to first token
        return tokenizer.encode(token_str, add_special_tokens=False)[0]

    for trap in traps:
        target_id = _resolve(trap.target_token)
        anti_id = _resolve(trap.anti_token)

        result = logit_lens_pass(
            model=model,
            tokenizer=tokenizer,
            prompt=trap.prompt,
            target_token_id=target_id,
            anti_token_id=anti_id,
            trap_name=trap.name,
        )
        results.append(result)

    return results
