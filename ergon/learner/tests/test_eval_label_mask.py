"""Tests for E001 v0.5b — evaluate_model_with_label_mask + completion-only loss.

Verifies the new sibling function behaves correctly on a tiny model:
- Returns the right metrics shape (parity with evaluate_model)
- Predicts via forced-decode scoring (no free-form generation, no parsing)
- Adds `decode_protocol` field marking the new path
- Per-row `label_log_probs` table is present when log_predictions=True
- Single-candidate input rejected (≥2 needed)

Plus a smoke test for completion-only training: TrainingArgs with
completion_only_loss=True doesn't crash; default False preserves behaviour.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest


TINY_MODEL_ID = "sshleifer/tiny-gpt2"


def _records() -> List[Dict[str, Any]]:
    return [
        {
            "poly_coefficients": [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            "mahler_measure_dps60": 1.0,
            "n_irreducible_factors": 2,
            "cyclotomic_factor_indices": [3, 6],
            "non_cyclotomic_factor_present": False,
            "catalog_match_type": "all_cyclotomic",
            "class": "standard_quad_factor",
            "class_post_fold": "cyclotomic_noise",
        },
        {
            "poly_coefficients": [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            "mahler_measure_dps60": 1.176,
            "n_irreducible_factors": 1,
            "cyclotomic_factor_indices": [],
            "non_cyclotomic_factor_present": True,
            "catalog_match_type": "miss",
            "class": "lehmer_x_phi_n_k_composite",
            "class_post_fold": "lehmer_composite",
        },
    ]


@pytest.fixture(scope="module")
def tiny_model_and_tokenizer():
    transformers = pytest.importorskip("transformers")
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(TINY_MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(TINY_MODEL_ID)
    return model, tokenizer


@pytest.fixture(scope="module")
def eval_dataset(tiny_model_and_tokenizer):
    _, tokenizer = tiny_model_and_tokenizer
    from ergon.pipeline_d.data_loader import load_dataset_for_training

    return load_dataset_for_training(_records(), tokenizer, max_seq_length=128)


def test_evaluate_model_with_label_mask_returns_full_metrics(
    tiny_model_and_tokenizer, eval_dataset
):
    model, tokenizer = tiny_model_and_tokenizer
    from ergon.pipeline_d.eval import evaluate_model_with_label_mask

    out = evaluate_model_with_label_mask(model, eval_dataset, tokenizer)

    assert out["n"] == len(_records())
    assert "accuracy" in out
    assert "per_class_accuracy" in out
    assert "confusion_matrix" in out
    assert out["decode_protocol"] == "label_mask_forced_decode"
    assert isinstance(out["candidate_labels"], list)
    assert len(out["candidate_labels"]) >= 2


def test_label_mask_predictions_are_in_candidate_set(
    tiny_model_and_tokenizer, eval_dataset
):
    model, tokenizer = tiny_model_and_tokenizer
    from ergon.pipeline_d.eval import evaluate_model_with_label_mask

    out = evaluate_model_with_label_mask(
        model, eval_dataset, tokenizer, log_predictions=True
    )
    candidates = set(out["candidate_labels"])
    for row in out["predictions"]:
        assert row["pred"] in candidates, (
            f"masked-decode pred {row['pred']!r} must be in candidate set"
        )
        assert "label_log_probs" in row
        assert set(row["label_log_probs"].keys()) == candidates


def test_label_mask_rejects_single_candidate(
    tiny_model_and_tokenizer, eval_dataset
):
    model, tokenizer = tiny_model_and_tokenizer
    from ergon.pipeline_d.eval import evaluate_model_with_label_mask

    with pytest.raises(ValueError, match="need .*2 candidate labels"):
        evaluate_model_with_label_mask(
            model, eval_dataset, tokenizer, candidate_labels=["only_one"]
        )


def test_label_mask_does_not_change_evaluate_model_signature(
    tiny_model_and_tokenizer, eval_dataset
):
    """Contract check (E001 acceptance criterion 4): the new sibling
    function lives alongside evaluate_model; signature unchanged."""
    import inspect
    from ergon.pipeline_d.eval import evaluate_model

    sig = inspect.signature(evaluate_model)
    expected_params = {
        "model",
        "eval_dataset",
        "tokenizer",
        "candidate_labels",
        "max_new_tokens",
        "log_predictions",
    }
    assert set(sig.parameters.keys()) == expected_params, (
        f"evaluate_model signature drifted: {sig.parameters.keys()}"
    )


def test_training_args_completion_only_loss_default_false():
    """Contract check: existing TrainingArgs() callers see no behaviour
    change. Default of completion_only_loss is False."""
    from ergon.pipeline_d.train import TrainingArgs

    args = TrainingArgs()
    assert args.completion_only_loss is False
    assert args.completion_response_template == " | Class: "


def test_training_args_completion_only_loss_opt_in():
    from ergon.pipeline_d.train import TrainingArgs

    args = TrainingArgs(completion_only_loss=True)
    assert args.completion_only_loss is True
