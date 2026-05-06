"""Tests for ergon.pipeline_d (W3.3 + W3.5 + W3.6).

Coverage:
- data_loader: serialization correctness; HF Dataset construction;
  reproducible train/eval split; tolerant to in-flight schema (boundary
  layer + synthetic env shapes both consumable).
- eval: per-class accuracy + confusion matrix on a tiny model + mock
  data; accepts both LoRA and base-model inputs.
- train: 1-epoch smoke run completes without error; loss is recorded;
  LoRA weights save + reload round-trip produces identical eval
  numbers (within numerical noise — bit-exact on greedy decode).

Smoke tests use `sshleifer/tiny-gpt2` (~100K params, ~5MB on disk)
instead of Qwen2.5-Math-1.5B-Instruct so the full test file runs in
seconds. The Qwen loader (W3.4) is exercised in `model.py`'s
`__main__` smoke and is too heavy for unit tests.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


TINY_MODEL_ID = "sshleifer/tiny-gpt2"


def _mock_boundary_layer_records() -> List[Dict[str, Any]]:
    """6 records mimicking the W3.2 boundary-layer fixture schema
    (documented in v0.5 design doc §7.2, provisional version)."""
    return [
        {
            "poly_coefficients": [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            "mahler_measure_dps60": 1.176280818,
            "n_irreducible_factors": 1,
            "cyclotomic_factor_indices": [],
            "non_cyclotomic_factor_present": True,
            "catalog_match_type": "miss",
            "class": "lehmer_x_phi_n_k_composite",
            "class_post_fold": "lehmer_composite",
        },
        {
            "poly_coefficients": [1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            "mahler_measure_dps60": 1.000000000,
            "n_irreducible_factors": 2,
            "cyclotomic_factor_indices": [4],
            "non_cyclotomic_factor_present": False,
            "catalog_match_type": "all_cyclotomic",
            "class": "phi_4_singleton",
            "class_post_fold": "cyclotomic_noise",
        },
        {
            "poly_coefficients": [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
            "mahler_measure_dps60": 1.234,
            "n_irreducible_factors": 2,
            "cyclotomic_factor_indices": [],
            "non_cyclotomic_factor_present": True,
            "catalog_match_type": "composite",
            "class": "high_degree_reflection_pair",
            "class_post_fold": "lehmer_composite",
        },
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
            "poly_coefficients": [1, -1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, -1, 1],
            "mahler_measure_dps60": 1.42,
            "n_irreducible_factors": 1,
            "cyclotomic_factor_indices": [],
            "non_cyclotomic_factor_present": True,
            "catalog_match_type": "miss",
            "class": "lehmer_x_phi_n_k_composite",
            "class_post_fold": "lehmer_composite",
        },
        {
            "poly_coefficients": [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
            "mahler_measure_dps60": 1.0,
            "n_irreducible_factors": 3,
            "cyclotomic_factor_indices": [3, 4, 6],
            "non_cyclotomic_factor_present": False,
            "catalog_match_type": "all_cyclotomic",
            "class": "standard_quad_factor",
            "class_post_fold": "cyclotomic_noise",
        },
    ]


def _mock_synthetic_records() -> List[Dict[str, Any]]:
    """4 records mimicking SyntheticRecord.to_dict() output."""
    return [
        {
            "poly_coefficients": [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
            "height": 6,
            "nnz_free": 2,
            "mahler_proxy": 1.95,
            "label": 0,
            "label_continuous": -0.42,
        },
        {
            "poly_coefficients": [1, -3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -3, 1],
            "height": 10,
            "nnz_free": 3,
            "mahler_proxy": 2.4,
            "label": 1,
            "label_continuous": 0.71,
        },
        {
            "poly_coefficients": [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
            "height": 4,
            "nnz_free": 1,
            "mahler_proxy": 1.4,
            "label": 0,
            "label_continuous": -1.1,
        },
        {
            "poly_coefficients": [1, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 1],
            "height": 8,
            "nnz_free": 3,
            "mahler_proxy": 2.1,
            "label": 1,
            "label_continuous": 0.33,
        },
    ]


@pytest.fixture(scope="module")
def tiny_tokenizer():
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(TINY_MODEL_ID)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


@pytest.fixture(scope="module")
def tiny_base_model():
    from transformers import AutoModelForCausalLM

    return AutoModelForCausalLM.from_pretrained(TINY_MODEL_ID)


@pytest.fixture(scope="module")
def tiny_lora_model(tiny_base_model):
    """Wrap the tiny model with a LoRA adapter on attention. tiny-gpt2's
    attention modules are c_attn / c_proj (Conv1D-based GPT-2)."""
    from peft import LoraConfig, get_peft_model

    cfg = LoraConfig(
        r=4,
        lora_alpha=8,
        target_modules=["c_attn"],
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
    )
    return get_peft_model(tiny_base_model, cfg)


# ===========================================================================
# W3.3 — data_loader
# ===========================================================================


def test_serialize_record_boundary_layer_shape():
    from ergon.pipeline_d.data_loader import serialize_record

    rec = _mock_boundary_layer_records()[0]
    out = serialize_record(rec)
    assert "prompt" in out and "completion" in out and "text" in out
    assert "Predicate:" in out["prompt"]
    assert "Mahler:" in out["prompt"]
    assert "Factors:" in out["prompt"]
    assert "Class:" in out["prompt"]
    assert out["completion"] == "lehmer_composite"  # class_post_fold preferred
    assert out["text"] == out["prompt"] + out["completion"]


def test_serialize_record_synthetic_shape():
    from ergon.pipeline_d.data_loader import serialize_record

    rec = _mock_synthetic_records()[0]
    out = serialize_record(rec)
    assert out["completion"] == "0"  # label fallback
    assert "1.95" in out["prompt"] or "1.950000" in out["prompt"]  # mahler_proxy
    # nnz_free=2 should land in the Factors slot
    assert "Factors: 2" in out["prompt"]


def test_serialize_record_dataclass_input():
    """Accepts SyntheticRecord-style dataclass (has .to_dict())."""
    from ergon.pipeline_d.data_loader import serialize_record
    from ergon.diagnostic_c.synthetic_env import SyntheticRecord

    r = SyntheticRecord(
        poly_coefficients=[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        height=6,
        nnz_free=2,
        mahler_proxy=1.95,
        label=0,
        label_continuous=-0.42,
    )
    out = serialize_record(r)
    assert out["completion"] == "0"


def test_load_dataset_for_training_produces_tokenized_dataset(tiny_tokenizer):
    from ergon.pipeline_d.data_loader import load_dataset_for_training

    records = _mock_boundary_layer_records()
    ds = load_dataset_for_training(records, tiny_tokenizer, max_seq_length=128)
    assert len(ds) == len(records)
    for col in ("prompt", "completion", "text", "input_ids", "attention_mask"):
        assert col in ds.column_names, f"missing column {col}"
    # Tokenization respects max_seq_length
    assert all(len(ids) <= 128 for ids in ds["input_ids"])


def test_load_dataset_handles_mixed_record_shapes(tiny_tokenizer):
    """Boundary-layer + synthetic records can be mixed in one dataset."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training

    records = _mock_boundary_layer_records() + _mock_synthetic_records()
    ds = load_dataset_for_training(records, tiny_tokenizer, max_seq_length=128)
    assert len(ds) == 10


def test_train_eval_split_reproducible(tiny_tokenizer):
    from ergon.pipeline_d.data_loader import (
        load_dataset_for_training,
        train_eval_split,
    )

    records = _mock_boundary_layer_records() + _mock_synthetic_records()
    ds = load_dataset_for_training(records, tiny_tokenizer, max_seq_length=128)

    tr1, ev1 = train_eval_split(ds, eval_fraction=0.2, seed=42)
    tr2, ev2 = train_eval_split(ds, eval_fraction=0.2, seed=42)
    assert tr1["text"] == tr2["text"]
    assert ev1["text"] == ev2["text"]
    # 80/20 of 10 → 8/2
    assert len(tr1) == 8 and len(ev1) == 2

    tr3, ev3 = train_eval_split(ds, eval_fraction=0.2, seed=7)
    # Different seed → likely different split (probabilistic but
    # near-certain at n=10)
    assert tr1["text"] != tr3["text"] or ev1["text"] != ev3["text"]


def test_train_eval_split_rejects_bad_inputs(tiny_tokenizer):
    from ergon.pipeline_d.data_loader import (
        load_dataset_for_training,
        train_eval_split,
    )

    records = _mock_boundary_layer_records()
    ds = load_dataset_for_training(records, tiny_tokenizer, max_seq_length=128)

    with pytest.raises(ValueError):
        train_eval_split(ds, eval_fraction=0.0)
    with pytest.raises(ValueError):
        train_eval_split(ds, eval_fraction=1.0)


def test_serialize_record_missing_label_raises():
    from ergon.pipeline_d.data_loader import serialize_record

    with pytest.raises(KeyError):
        serialize_record({"poly_coefficients": [1, 2, 3]})


def test_load_records_from_jsonl_roundtrip(tmp_path):
    from ergon.pipeline_d.data_loader import load_records_from_jsonl

    records = _mock_boundary_layer_records()
    p = tmp_path / "records.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    loaded = load_records_from_jsonl(p)
    assert len(loaded) == len(records)
    assert loaded[0]["class_post_fold"] == records[0]["class_post_fold"]


# ===========================================================================
# W3.5 — eval harness
# ===========================================================================


def test_evaluate_model_base_produces_sensible_baseline(
    tiny_base_model, tiny_tokenizer
):
    """Base tiny-gpt2 (untrained for this task) should produce some
    completion; per-class structure should be present even if accuracy
    is ~chance."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.eval import evaluate_model

    records = _mock_boundary_layer_records()
    ds = load_dataset_for_training(records, tiny_tokenizer, max_seq_length=128)
    metrics = evaluate_model(
        tiny_base_model,
        ds,
        tiny_tokenizer,
        max_new_tokens=8,
    )
    assert metrics["n"] == len(records)
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert isinstance(metrics["per_class_accuracy"], dict)
    assert isinstance(metrics["confusion_matrix"], dict)
    assert "predictions" in metrics
    assert len(metrics["predictions"]) == len(records)
    # Each prediction has the expected fields
    pred = metrics["predictions"][0]
    assert {"prompt", "gold", "pred", "raw_completion"} <= set(pred.keys())


def test_evaluate_model_label_parsing_recognizes_candidate(
    tiny_base_model, tiny_tokenizer
):
    """If the candidate label appears in the model's free-form output,
    label parsing should pick it up."""
    from ergon.pipeline_d.eval import _parse_label_from_completion

    candidates = ["cyclotomic_noise", "lehmer_composite"]
    assert _parse_label_from_completion(
        " ... lehmer_composite something else", candidates
    ) == "lehmer_composite"
    assert _parse_label_from_completion(
        "the cyclotomic_noise label", candidates
    ) == "cyclotomic_noise"
    # No candidate hit → returns leading token
    assert _parse_label_from_completion("foo bar", candidates) == "foo"


def test_evaluate_model_requires_prompt_completion_columns(
    tiny_base_model, tiny_tokenizer
):
    from datasets import Dataset

    from ergon.pipeline_d.eval import evaluate_model

    bad_ds = Dataset.from_list([{"text": "x"}, {"text": "y"}])
    with pytest.raises(ValueError):
        evaluate_model(tiny_base_model, bad_ds, tiny_tokenizer)


# ===========================================================================
# W3.6 — training loop
# ===========================================================================


def test_train_loop_one_epoch_smoke(
    tiny_lora_model, tiny_tokenizer, tmp_path
):
    """1-epoch smoke training on mock boundary-layer data completes
    without crash. Loss is recorded."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.train import TrainingArgs, train_model

    records = _mock_boundary_layer_records()
    ds = load_dataset_for_training(records, tiny_tokenizer, max_seq_length=128)

    args = TrainingArgs(
        run_name="test_smoke",
        runs_dir=tmp_path,
        max_steps=4,
        num_train_epochs=1,
        learning_rate=5e-4,
        per_device_train_batch_size=1,
        logging_steps=1,
        bf16=False,  # tiny model on CPU/GPU; bf16 not needed
    )
    metrics = train_model(
        tiny_lora_model,
        tiny_tokenizer,
        ds,
        args=args,
    )
    assert metrics["trained_steps"] >= 1
    assert metrics["final_loss"] is not None
    assert Path(metrics["saved_lora_path"]).exists()
    assert (Path(metrics["saved_lora_path"]) / "training_metrics.json").exists()


def test_train_loop_loss_is_finite(
    tiny_lora_model, tiny_tokenizer, tmp_path
):
    """Loss should be finite; not nan / inf."""
    import math

    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.train import TrainingArgs, train_model

    records = _mock_boundary_layer_records()
    ds = load_dataset_for_training(records, tiny_tokenizer, max_seq_length=128)

    args = TrainingArgs(
        run_name="test_finite_loss",
        runs_dir=tmp_path,
        max_steps=2,
        num_train_epochs=1,
        learning_rate=5e-4,
        per_device_train_batch_size=1,
        logging_steps=1,
        bf16=False,
    )
    metrics = train_model(tiny_lora_model, tiny_tokenizer, ds, args=args)
    assert metrics["final_loss"] is not None
    assert math.isfinite(metrics["final_loss"])


def test_round_trip_train_save_reload_eval(
    tiny_base_model, tiny_tokenizer, tmp_path
):
    """Full round-trip: build dataset → train LoRA → save → reload onto
    fresh base → eval; numbers should match the in-memory eval (greedy
    decode is bit-exact for the same weights, so accuracy should be
    identical, modulo any floating-point reduction order which doesn't
    apply here at single-batch generation).

    This is a separate fixture (fresh tiny model + fresh LoRA) so the
    previous tests' mutations don't leak in.
    """
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM

    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.eval import evaluate_model
    from ergon.pipeline_d.train import (
        TrainingArgs,
        load_lora_for_eval,
        train_model,
    )

    base_a = AutoModelForCausalLM.from_pretrained(TINY_MODEL_ID)
    cfg = LoraConfig(
        r=4,
        lora_alpha=8,
        target_modules=["c_attn"],
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model_a = get_peft_model(base_a, cfg)

    records = _mock_boundary_layer_records()
    ds = load_dataset_for_training(records, tiny_tokenizer, max_seq_length=128)

    args = TrainingArgs(
        run_name="test_round_trip",
        runs_dir=tmp_path,
        max_steps=3,
        num_train_epochs=1,
        learning_rate=5e-4,
        per_device_train_batch_size=1,
        logging_steps=1,
        bf16=False,
    )
    metrics = train_model(model_a, tiny_tokenizer, ds, args=args)
    metrics_in_mem = evaluate_model(
        model_a, ds, tiny_tokenizer, max_new_tokens=8
    )

    # Reload onto a fresh base and compare.
    base_b = AutoModelForCausalLM.from_pretrained(TINY_MODEL_ID)
    reloaded = load_lora_for_eval(base_b, metrics["saved_lora_path"])
    metrics_reload = evaluate_model(
        reloaded, ds, tiny_tokenizer, max_new_tokens=8
    )

    # Greedy decode + identical weights → identical accuracy. We
    # tolerate small mismatch (some tiny models do non-deterministic
    # cudnn ops) but the difference should be small.
    assert abs(metrics_in_mem["accuracy"] - metrics_reload["accuracy"]) <= 0.01
    assert metrics_in_mem["n"] == metrics_reload["n"]
