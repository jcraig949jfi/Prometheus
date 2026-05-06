"""Pipeline-D eval harness (W3.5).

Evaluates a (possibly LoRA-adapted) Qwen2.5-Math-1.5B-Instruct on a
held-out boundary-layer / synthetic-env fixture. Per design doc
acceptance-criterion #4: the LoRA-tuned model must beat the base
model for the tire-kick to be informative.

Eval target: classification — given the serialized predicate prompt,
the model emits a class label string. We score:

- per-class accuracy + overall accuracy
- confusion matrix (dict-of-dicts; sparse for unknown labels)
- log of per-row prediction vs ground truth (for the W6.1 evidence
  dossier)

KillVector regression MSE is reserved as a stretch field; v0.5
trains classification-only, so this harness reports MSE only when
the eval set carries a `kill_vector_target` numeric field (None
otherwise).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import torch
from datasets import Dataset


# ---------------------------------------------------------------------------
# Generation utility
# ---------------------------------------------------------------------------


def _resolve_generation_device(model: Any) -> torch.device:
    """Pick a sensible device for generation. peft.PeftModel exposes
    .device via the underlying base; fall back to first param's device."""
    if hasattr(model, "device") and isinstance(model.device, torch.device):
        return model.device
    try:
        return next(model.parameters()).device
    except StopIteration:
        return torch.device("cpu")


def _generate_completion(
    model: Any,
    tokenizer: Any,
    prompt: str,
    max_new_tokens: int = 16,
) -> str:
    """Greedy decode `max_new_tokens` after `prompt`. Returns just
    the newly generated text (no prompt echo)."""
    device = _resolve_generation_device(model)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    pad_id = tokenizer.pad_token_id
    if pad_id is None:
        pad_id = tokenizer.eos_token_id
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            num_beams=1,
            pad_token_id=pad_id,
        )
    new_tokens = out[0, inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


# ---------------------------------------------------------------------------
# Label parsing
# ---------------------------------------------------------------------------


def _parse_label_from_completion(
    completion: str,
    candidate_labels: Sequence[str],
) -> str:
    """Extract a label from the model's free-form completion.

    Strategy: return the first candidate label that appears as a
    substring of the completion (case-insensitive); if no candidate
    matches, return the leading whitespace-stripped token (so the
    confusion matrix still records *something* and we don't silently
    map every unknown to a default class)."""
    stripped = completion.strip()
    lower = stripped.lower()
    for lab in candidate_labels:
        if lab.lower() in lower:
            return lab
    # No candidate hit; return the first whitespace token so the
    # confusion matrix has a real row.
    if not stripped:
        return "<empty>"
    return stripped.split()[0]


# ---------------------------------------------------------------------------
# Public eval entry point
# ---------------------------------------------------------------------------


def evaluate_model(
    model: Any,
    eval_dataset: Dataset,
    tokenizer: Any,
    candidate_labels: Optional[Sequence[str]] = None,
    max_new_tokens: int = 16,
    log_predictions: bool = True,
) -> Dict[str, Any]:
    """Run model on `eval_dataset` and return a metrics dict.

    Expects each row to carry `prompt` and `completion` fields (the
    output of `data_loader.serialize_record`). The gold class is
    `completion`; the model is asked to produce text after `prompt`,
    and we parse the label out of that.

    Returns:
        {
          "n": int,
          "accuracy": float,
          "per_class_accuracy": {label: float},
          "confusion_matrix": {gold_label: {pred_label: count}},
          "predictions": [{"prompt", "gold", "pred", "raw_completion"}, ...]
                         (only if log_predictions=True),
          "candidate_labels": [...],
          "mse": float | None  (regression target if present),
        }
    """
    if "prompt" not in eval_dataset.column_names or "completion" not in eval_dataset.column_names:
        raise ValueError(
            f"eval_dataset must contain 'prompt' and 'completion' columns; "
            f"got {eval_dataset.column_names}"
        )

    if candidate_labels is None:
        # Auto-discover from gold labels in the eval set.
        candidate_labels = sorted({str(c) for c in eval_dataset["completion"]})

    was_training = model.training
    model.eval()

    predictions: List[Dict[str, str]] = []
    confusion: Dict[str, Dict[str, int]] = {}
    per_class_correct: Dict[str, int] = {}
    per_class_total: Dict[str, int] = {}
    correct = 0

    for row in eval_dataset:
        prompt = row["prompt"]
        gold = str(row["completion"])
        raw = _generate_completion(model, tokenizer, prompt, max_new_tokens=max_new_tokens)
        pred = _parse_label_from_completion(raw, candidate_labels)

        per_class_total[gold] = per_class_total.get(gold, 0) + 1
        confusion.setdefault(gold, {})
        confusion[gold][pred] = confusion[gold].get(pred, 0) + 1
        if pred == gold:
            correct += 1
            per_class_correct[gold] = per_class_correct.get(gold, 0) + 1

        if log_predictions:
            predictions.append({
                "prompt": prompt,
                "gold": gold,
                "pred": pred,
                "raw_completion": raw,
            })

    if was_training:
        model.train()

    n = len(eval_dataset)
    overall_acc = correct / n if n > 0 else 0.0
    per_class_acc = {
        lab: per_class_correct.get(lab, 0) / per_class_total[lab]
        for lab in per_class_total
    }

    # Optional regression target — only if eval_dataset carries it.
    mse: Optional[float] = None
    if "kill_vector_target" in eval_dataset.column_names:
        # Stub for v1.0; v0.5 classification-only.
        mse = None

    out: Dict[str, Any] = {
        "n": n,
        "accuracy": overall_acc,
        "per_class_accuracy": per_class_acc,
        "confusion_matrix": confusion,
        "candidate_labels": list(candidate_labels),
        "mse": mse,
    }
    if log_predictions:
        out["predictions"] = predictions
    return out


def evaluate_baseline(
    base_model: Any,
    eval_dataset: Dataset,
    tokenizer: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Convenience wrapper: run the base model (no LoRA) on the eval
    set. Used by W4.1 to establish the lift LoRA must beat per
    acceptance-criterion #4."""
    return evaluate_model(base_model, eval_dataset, tokenizer, **kwargs)


# ---------------------------------------------------------------------------
# E001 — Eval-protocol fix via forced-decode label scoring (v0.5b sub-sprint)
# ---------------------------------------------------------------------------


def _label_log_prob(
    model: Any,
    tokenizer: Any,
    prompt: str,
    label: str,
    device: torch.device,
) -> float:
    """Conditional log-prob of `label` given `prompt`, summed over label tokens.

    Forced-decode scoring: build prompt+label, run a forward pass, then
    sum log P(token_t | token_<t) over the label-token positions only.
    Equivalent to "logit masking on the label-vocabulary subset" but
    uses each candidate's full token sequence (labels like
    "cyclotomic_noise" tokenize to multiple subwords; first-token
    masking would lose that structure)."""
    full_ids = tokenizer(prompt + label, return_tensors="pt").input_ids.to(device)
    prompt_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    n_prompt = int(prompt_ids.shape[1])

    with torch.no_grad():
        logits = model(input_ids=full_ids).logits  # (1, T, V)
    # Position t's logits predict token at position t+1.
    log_probs = torch.log_softmax(logits, dim=-1)

    total = 0.0
    for t in range(n_prompt, int(full_ids.shape[1])):
        target_id = int(full_ids[0, t].item())
        total += float(log_probs[0, t - 1, target_id].item())
    return total


def evaluate_model_with_label_mask(
    model: Any,
    eval_dataset: Dataset,
    tokenizer: Any,
    candidate_labels: Optional[Sequence[str]] = None,
    log_predictions: bool = True,
) -> Dict[str, Any]:
    """Score-based eval that constrains predictions to the label-vocabulary.

    Per E001 v0.5b sub-sprint: the v0.5 tire-kick (TIRE_KICK_v0.5_RESULT_2026-05-06.md)
    found the binding constraint was prompt-format luring numeric continuation
    after a colon, not learning capacity. This eval routes prediction through
    forced-decode scoring of each candidate label rather than free-form
    decoding + substring parsing — i.e., the model picks among candidate
    labels by relative conditional log-probability, never freely generating.

    Returns the same dict shape as `evaluate_model` plus `label_log_probs`
    (per-row, per-label score table) for diagnostic use. NO contract change
    to `evaluate_model`; this is a sibling function.
    """
    if "prompt" not in eval_dataset.column_names or "completion" not in eval_dataset.column_names:
        raise ValueError(
            f"eval_dataset must contain 'prompt' and 'completion' columns; "
            f"got {eval_dataset.column_names}"
        )

    if candidate_labels is None:
        candidate_labels = sorted({str(c) for c in eval_dataset["completion"]})
    candidate_labels = list(candidate_labels)
    if len(candidate_labels) < 2:
        raise ValueError(
            f"need ≥2 candidate labels for masked decoding; got {candidate_labels}"
        )

    device = _resolve_generation_device(model)
    was_training = model.training
    model.eval()

    predictions: List[Dict[str, Any]] = []
    confusion: Dict[str, Dict[str, int]] = {}
    per_class_correct: Dict[str, int] = {}
    per_class_total: Dict[str, int] = {}
    correct = 0

    for row in eval_dataset:
        prompt = row["prompt"]
        gold = str(row["completion"])
        scores = {
            lab: _label_log_prob(model, tokenizer, prompt, lab, device)
            for lab in candidate_labels
        }
        pred = max(scores, key=scores.get)

        per_class_total[gold] = per_class_total.get(gold, 0) + 1
        confusion.setdefault(gold, {})
        confusion[gold][pred] = confusion[gold].get(pred, 0) + 1
        if pred == gold:
            correct += 1
            per_class_correct[gold] = per_class_correct.get(gold, 0) + 1

        if log_predictions:
            predictions.append({
                "prompt": prompt,
                "gold": gold,
                "pred": pred,
                "label_log_probs": scores,
            })

    if was_training:
        model.train()

    n = len(eval_dataset)
    overall_acc = correct / n if n > 0 else 0.0
    per_class_acc = {
        lab: per_class_correct.get(lab, 0) / per_class_total[lab]
        for lab in per_class_total
    }

    out: Dict[str, Any] = {
        "n": n,
        "accuracy": overall_acc,
        "per_class_accuracy": per_class_acc,
        "confusion_matrix": confusion,
        "candidate_labels": list(candidate_labels),
        "decode_protocol": "label_mask_forced_decode",
        "mse": None,
    }
    if log_predictions:
        out["predictions"] = predictions
    return out


__all__ = [
    "evaluate_model",
    "evaluate_baseline",
    "evaluate_model_with_label_mask",
]
