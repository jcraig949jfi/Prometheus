"""E001 v0.5b — re-run W4.0 / W4.1 / W4.2 under masked-decode eval.

The v0.5 tire-kick (TIRE_KICK_v0.5_RESULT_2026-05-06.md) found the
binding constraint was prompt-format luring numeric continuation after
a colon, not learning capacity. The base + LoRA-tuned model both
emitted literal token "1" for every prompt under greedy decoding.

This re-runner replaces the eval path with forced-decode label scoring
(`evaluate_model_with_label_mask`) — the model picks among candidate
labels by relative conditional log-probability rather than free-form
generating + parsing. Training stays unchanged (default loss); the
intervention is eval-only. If results still pin at majority-class
parity, follow-up fire adds train-time completion-only loss (E001b).

Outputs:
- ergon/pipeline_d/runs/v0_5b_null_gate/null_gate_results.json
- ergon/pipeline_d/runs/v0_5b_tire_kick_a/tire_kick_a_results.json
- ergon/pipeline_d/runs/v0_5b_tire_kick_b/tire_kick_b_results.json

Runner pattern follows null_gate.py + tire_kick_a.py + tire_kick_b.py.
"""
from __future__ import annotations

import gc
import json
import os
import random
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
from scipy.stats import binomtest


SHUFFLE_SEEDS: Tuple[int, ...] = (42, 1234, 100)
ALPHA = 0.10
MAX_STEPS = 50
LEARNING_RATE = 5e-5
LORA_RANK = 8
MAX_SEQ_LENGTH = 512
SPLIT_SEED = 7

OUT_DIR = Path("ergon/pipeline_d/runs")


# ---------------------------------------------------------------------------
# Helpers — fresh model + masked eval per seed
# ---------------------------------------------------------------------------


def _free_gpu() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _train_then_masked_eval(
    train_records: List[Dict[str, Any]],
    eval_records: List[Dict[str, Any]],
    run_name: str,
    seed: int,
    candidate_labels: List[str],
    max_steps: int = MAX_STEPS,
) -> Dict[str, Any]:
    """Load fresh Qwen + LoRA, train on records, eval via masked decode.

    Returns metrics dict with masked-decode accuracy + base-model masked
    zero-shot for comparison. Raises on any error so caller can mark
    ENGINEERING_FAIL cleanly."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.eval import evaluate_model_with_label_mask
    from ergon.pipeline_d.model import load_qwen_math_15b
    from ergon.pipeline_d.train import TrainingArgs, train_model

    t0 = time.time()
    model, tokenizer = load_qwen_math_15b(use_lora=True, rank=LORA_RANK)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_ds = load_dataset_for_training(train_records, tokenizer, max_seq_length=MAX_SEQ_LENGTH)
    eval_ds = load_dataset_for_training(eval_records, tokenizer, max_seq_length=MAX_SEQ_LENGTH)

    # Base-model masked zero-shot: evaluate BEFORE training so the LoRA
    # adapter is still present-but-untrained. Provides the must-beat baseline.
    base_eval = evaluate_model_with_label_mask(
        model, eval_ds, tokenizer,
        candidate_labels=candidate_labels,
        log_predictions=False,
    )

    args = TrainingArgs(
        run_name=run_name, max_steps=max_steps, learning_rate=LEARNING_RATE,
        max_seq_length=MAX_SEQ_LENGTH, seed=seed,
    )
    train_metrics = train_model(model, tokenizer, train_ds, args=args)

    lora_eval = evaluate_model_with_label_mask(
        model, eval_ds, tokenizer,
        candidate_labels=candidate_labels,
        log_predictions=False,
    )
    elapsed = time.time() - t0
    _free_gpu()

    return {
        "base_zero_shot": {
            "accuracy": float(base_eval["accuracy"]),
            "per_class_accuracy": base_eval["per_class_accuracy"],
            "confusion_matrix": base_eval["confusion_matrix"],
        },
        "lora_post_train": {
            "accuracy": float(lora_eval["accuracy"]),
            "per_class_accuracy": lora_eval["per_class_accuracy"],
            "confusion_matrix": lora_eval["confusion_matrix"],
            "n": int(lora_eval["n"]),
        },
        "decode_protocol": "label_mask_forced_decode",
        "trained_steps": int(train_metrics.get("trained_steps", 0)),
        "final_loss": train_metrics.get("final_loss"),
        "wall_clock_seconds": float(elapsed),
    }


# ---------------------------------------------------------------------------
# W4.0 — synthetic-null gate (re-pass under masked decode)
# ---------------------------------------------------------------------------


def _shuffled_variant_a(seed: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    from ergon.pipeline_d.boundary_layer_fixture import (
        load_17_entry_fixture, load_heldout_fixture,
    )
    fixture = load_17_entry_fixture()
    heldout, _ = load_heldout_fixture()
    all_recs = [r.to_dict() for r in fixture] + [r.to_dict() for r in heldout]
    rng = random.Random(seed)
    labels = [r["class_post_fold"] for r in all_recs]
    rng.shuffle(labels)
    for rec, new_lab in zip(all_recs, labels):
        rec["class_post_fold"] = new_lab
    split_rng = random.Random(SPLIT_SEED)
    indices = list(range(len(all_recs)))
    split_rng.shuffle(indices)
    n_eval = max(1, int(round(0.2 * len(all_recs))))
    eval_idx = set(indices[:n_eval])
    train = [all_recs[i] for i in range(len(all_recs)) if i not in eval_idx]
    held_split = [all_recs[i] for i in range(len(all_recs)) if i in eval_idx]
    cands = sorted({r["class_post_fold"] for r in all_recs})
    return train, held_split, cands


def _shuffled_variant_b(seed: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    from ergon.diagnostic_c.synthetic_env import generate_synthetic_corpus
    corp, _ = generate_synthetic_corpus(n_train=1000, n_heldout=200, snr_db=10.0, seed=42)
    train_recs = [r.to_dict() for r in corp.train]
    held_recs = [r.to_dict() for r in corp.heldout]
    rng = random.Random(seed)
    train_labels = [r["label"] for r in train_recs]
    rng.shuffle(train_labels)
    for r, new_lab in zip(train_recs, train_labels):
        r["label"] = new_lab
    held_labels = [r["label"] for r in held_recs]
    rng.shuffle(held_labels)
    for r, new_lab in zip(held_recs, held_labels):
        r["label"] = new_lab
    cands = sorted({str(r["label"]) for r in train_recs + held_recs})
    return train_recs, held_recs, cands


def run_w4_0_masked() -> Dict[str, Any]:
    out_path = OUT_DIR / "v0_5b_null_gate" / "null_gate_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Any] = {
        "decode_protocol": "label_mask_forced_decode",
        "variant_a_boundary": {},
        "variant_b_synthetic": {},
        "config": {
            "alpha": ALPHA, "chance": 0.5, "shuffle_seeds": list(SHUFFLE_SEEDS),
            "max_steps": MAX_STEPS, "lora_rank": LORA_RANK,
        },
    }
    fired = []

    for seed in SHUFFLE_SEEDS:
        try:
            train_recs, held_recs, cands = _shuffled_variant_a(seed)
            block = _train_then_masked_eval(
                train_recs, held_recs,
                run_name=f"v0_5b_null_a_s{seed}", seed=seed, candidate_labels=cands,
            )
            acc = block["lora_post_train"]["accuracy"]
            n_total = block["lora_post_train"]["n"]
            n_correct = int(round(acc * n_total))
            bt = binomtest(n_correct, n_total, p=0.5, alternative="greater")
            block["accuracy"] = acc
            block["n_correct"] = n_correct
            block["n_total"] = n_total
            block["p_value"] = float(bt.pvalue)
            block["decision"] = "FIRE" if bt.pvalue < ALPHA else "PASS"
        except Exception as exc:
            block = {"decision": "ENGINEERING_FAIL",
                     "error_type": type(exc).__name__,
                     "error_msg": str(exc),
                     "traceback": traceback.format_exc()}
        results["variant_a_boundary"][f"seed_{seed}"] = block
        if block.get("decision") == "FIRE":
            fired.append({"variant": "a", "seed": seed})

    for seed in SHUFFLE_SEEDS:
        try:
            train_recs, held_recs, cands = _shuffled_variant_b(seed)
            block = _train_then_masked_eval(
                train_recs, held_recs,
                run_name=f"v0_5b_null_b_s{seed}", seed=seed, candidate_labels=cands,
            )
            acc = block["lora_post_train"]["accuracy"]
            n_total = block["lora_post_train"]["n"]
            n_correct = int(round(acc * n_total))
            bt = binomtest(n_correct, n_total, p=0.5, alternative="greater")
            block["accuracy"] = acc
            block["n_correct"] = n_correct
            block["n_total"] = n_total
            block["p_value"] = float(bt.pvalue)
            block["decision"] = "FIRE" if bt.pvalue < ALPHA else "PASS"
        except Exception as exc:
            block = {"decision": "ENGINEERING_FAIL",
                     "error_type": type(exc).__name__,
                     "error_msg": str(exc),
                     "traceback": traceback.format_exc()}
        results["variant_b_synthetic"][f"seed_{seed}"] = block
        if block.get("decision") == "FIRE":
            fired.append({"variant": "b", "seed": seed})

    any_fail = any(
        b.get("decision") == "ENGINEERING_FAIL"
        for v in ("variant_a_boundary", "variant_b_synthetic")
        for b in results[v].values()
    )
    if fired:
        results["overall_verdict"] = "FIRE"
    elif any_fail:
        results["overall_verdict"] = "ENGINEERING_FAIL"
    else:
        results["overall_verdict"] = "PASS"
    results["gate_fired_on"] = fired

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    return results


# ---------------------------------------------------------------------------
# W4.1 — 17-entry tire-kick (real labels) with masked decode
# ---------------------------------------------------------------------------


def run_w4_1_masked() -> Dict[str, Any]:
    out_path = OUT_DIR / "v0_5b_tire_kick_a" / "tire_kick_a_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    from ergon.pipeline_d.boundary_layer_fixture import (
        load_17_entry_fixture, load_heldout_fixture,
    )
    from ergon.pipeline_d.data_filter import filter_corpus, load_morphology_classifier

    fixture = load_17_entry_fixture()
    heldout, _ = load_heldout_fixture()
    train_full = [r.to_dict() for r in fixture]
    held_full = [r.to_dict() for r in heldout]
    cands = sorted({r["class_post_fold"] for r in train_full})

    classifier = load_morphology_classifier()
    filtered_train, _, drop_counts = filter_corpus(train_full, classifier)

    results: Dict[str, Any] = {
        "decode_protocol": "label_mask_forced_decode",
        "filter_was_no_op": (len(filtered_train) == len(train_full)),
        "drop_counts": dict(drop_counts) if drop_counts else {},
        "candidate_labels": cands,
        "runs": {},
    }
    for filter_mode, train_recs in (("filtered", filtered_train), ("unfiltered", train_full)):
        for seed in SHUFFLE_SEEDS:
            run_name = f"v0_5b_tk_a_{filter_mode}_s{seed}"
            try:
                block = _train_then_masked_eval(
                    train_recs, held_full,
                    run_name=run_name, seed=seed, candidate_labels=cands,
                )
                acc = block["lora_post_train"]["accuracy"]
                n_total = block["lora_post_train"]["n"]
                n_correct = int(round(acc * n_total))
                # Majority baseline from heldout dist
                gold_counts: Dict[str, int] = {}
                for r in held_full:
                    g = r["class_post_fold"]
                    gold_counts[g] = gold_counts.get(g, 0) + 1
                majority_rate = max(gold_counts.values()) / n_total if n_total else 0.5
                bt_maj = binomtest(n_correct, n_total, p=max(majority_rate, 0.5), alternative="greater")
                block["accuracy_post_fold"] = acc
                block["n_correct"] = n_correct
                block["n_total"] = n_total
                block["majority_class_rate"] = majority_rate
                block["p_vs_majority"] = float(bt_maj.pvalue)
                block["decision_vs_majority"] = "FIRE" if bt_maj.pvalue < ALPHA else "PARITY_OR_BELOW"
            except Exception as exc:
                block = {"decision": "ENGINEERING_FAIL",
                         "error_type": type(exc).__name__,
                         "error_msg": str(exc),
                         "traceback": traceback.format_exc()}
            results["runs"][f"{filter_mode}_seed_{seed}"] = block

    # Verdict
    any_fail = any(b.get("decision") == "ENGINEERING_FAIL" for b in results["runs"].values())
    any_beats_maj = any(
        b.get("decision_vs_majority") == "FIRE" for b in results["runs"].values()
    )
    if any_fail and not any_beats_maj:
        results["overall_verdict"] = "ENGINEERING_FAIL"
    elif any_beats_maj:
        results["overall_verdict"] = "PASS_BEATS_MAJORITY"
    else:
        # Compare to base zero-shot to distinguish CALIBRATED_FAIL from MAJORITY_PARITY
        base_accs = [b["base_zero_shot"]["accuracy"] for b in results["runs"].values() if "base_zero_shot" in b]
        lora_accs = [b.get("accuracy_post_fold", 0.0) for b in results["runs"].values()]
        if base_accs and max(lora_accs) > max(base_accs) + 0.05:
            results["overall_verdict"] = "CALIBRATED_FAIL_LOR_BEATS_BASE_BELOW_MAJORITY"
        else:
            results["overall_verdict"] = "MAJORITY_PARITY"

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    return results


# ---------------------------------------------------------------------------
# W4.2 — synthetic env tire-kick (real labels) with masked decode
# ---------------------------------------------------------------------------


def run_w4_2_masked() -> Dict[str, Any]:
    out_path = OUT_DIR / "v0_5b_tire_kick_b" / "tire_kick_b_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    from ergon.diagnostic_c.synthetic_env import generate_synthetic_corpus

    corp, _ = generate_synthetic_corpus(n_train=1000, n_heldout=200, snr_db=10.0, seed=42)
    train_full = [r.to_dict() for r in corp.train]
    held_full = [r.to_dict() for r in corp.heldout]
    cands = sorted({str(r["label"]) for r in train_full + held_full})

    results: Dict[str, Any] = {
        "decode_protocol": "label_mask_forced_decode",
        "candidate_labels": cands,
        "lsq_baseline_ceiling": 0.94,
        "runs": {},
    }
    for seed in SHUFFLE_SEEDS:
        run_name = f"v0_5b_tk_b_s{seed}"
        try:
            block = _train_then_masked_eval(
                train_full, held_full,
                run_name=run_name, seed=seed, candidate_labels=cands,
            )
            acc = block["lora_post_train"]["accuracy"]
            n_total = block["lora_post_train"]["n"]
            n_correct = int(round(acc * n_total))
            bt_chance = binomtest(n_correct, n_total, p=0.5, alternative="greater")
            block["accuracy"] = acc
            block["n_correct"] = n_correct
            block["n_total"] = n_total
            block["p_vs_chance"] = float(bt_chance.pvalue)
            block["decision_vs_chance"] = "BEATS_CHANCE" if bt_chance.pvalue < ALPHA else "AT_OR_BELOW_CHANCE"
            block["base_zero_shot_accuracy"] = block["base_zero_shot"]["accuracy"]
            block["gap_to_lsq"] = 0.94 - acc
        except Exception as exc:
            block = {"decision": "ENGINEERING_FAIL",
                     "error_type": type(exc).__name__,
                     "error_msg": str(exc),
                     "traceback": traceback.format_exc()}
        results["runs"][f"seed_{seed}"] = block

    any_fail = any(b.get("decision") == "ENGINEERING_FAIL" for b in results["runs"].values())
    any_beats_chance = any(
        b.get("decision_vs_chance") == "BEATS_CHANCE" for b in results["runs"].values()
    )
    if any_fail and not any_beats_chance:
        results["overall_verdict"] = "ENGINEERING_FAIL"
    elif any_beats_chance:
        results["overall_verdict"] = "PASS_BEATS_CHANCE"
    else:
        results["overall_verdict"] = "CHANCE_PARITY"

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if sys.platform == "win32" and not sys.flags.utf8_mode and os.environ.get("PYTHONUTF8") != "1":
        print("WARN: trl 1.3.0 needs UTF-8; re-run with `python -X utf8 ...`", file=sys.stderr)

    t_start = time.time()

    print("\n=== W4.0 masked re-run ===")
    gate = run_w4_0_masked()
    print(f"  verdict: {gate['overall_verdict']}; fired_on: {gate['gate_fired_on']}")

    if gate["overall_verdict"] != "PASS":
        print("Gate did not PASS — skipping W4.1 / W4.2 per substrate-grade discipline.")
        print(f"Total wall: {time.time() - t_start:.0f}s")
        return 2

    print("\n=== W4.1 masked re-run (17-entry boundary, real labels) ===")
    a = run_w4_1_masked()
    print(f"  verdict: {a['overall_verdict']}")

    print("\n=== W4.2 masked re-run (synthetic env, real labels) ===")
    b = run_w4_2_masked()
    print(f"  verdict: {b['overall_verdict']}")

    print(f"\nTotal wall: {time.time() - t_start:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
