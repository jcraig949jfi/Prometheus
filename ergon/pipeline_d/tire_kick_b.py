"""W4.2 — real-labels tire-kick on the synthetic ground-truth env.

Per `pivot/ergon_learner_v0.5_design_2026-05-05.md` §5 W4.2 + James's
2026-05-06 override: W4.0 PASSED (results at
`ergon/pipeline_d/runs/null_gate/null_gate_results.json`), so we are
cleared to run the real-labels tire-kick.

W4.2 is a controlled twin of W4.0 variant B: same env (n_train=1000,
n_heldout=200, snr_db=10, env seed=42), same training config
(max_steps=50, lr=5e-5, LoRA rank=8, max_seq_length=512), three shuffle
seeds for train order (42, 1234, 100), but **labels are NOT shuffled**.
The LSQ closed-form baseline recovers the latent rule at 0.94 on the
held-out; this run measures whether LoRA on Qwen2.5-Math-1.5B can pick
up the same signal end-to-end through next-token classification.

For each seed we report three comparisons:
- vs chance (0.50) via binomial test, alternative='greater', alpha=0.10
- vs base-model zero-shot accuracy (Qwen without LoRA) via binomial
  test, alternative='greater'
- gap to LSQ ceiling (0.94) — the closed-form numpy.linalg.lstsq
  upper bound

Verdict logic (per spec):
- PASS_BEATS_CHANCE_AND_BASE: LoRA accuracy beats chance (p<0.10)
  AND base-model zero-shot in all seeds
- CALIBRATED_FAIL: LoRA does not significantly beat chance OR
  base-model — names what's missing
- CHANCE_PARITY: LoRA at chance ~50% despite real labels — the
  "couldn't learn from this corpus shape at this scale" floor
- ENGINEERING_FAIL: something blocked

Windows note: trl 1.3.0 chat-template files require UTF-8 default
encoding. Run with `python -X utf8 -m ergon.pipeline_d.tire_kick_b` or
set PYTHONUTF8=1 before invoking.
"""
from __future__ import annotations

import gc
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
from scipy.stats import binomtest


# ---------------------------------------------------------------------------
# Constants — controlled-twin of W4.0 spec.
# ---------------------------------------------------------------------------

SHUFFLE_SEEDS: Tuple[int, ...] = (42, 1234, 100)
ALPHA = 0.10
CHANCE = 0.5

MAX_STEPS = 50
LEARNING_RATE = 5e-5
LORA_RANK = 8
MAX_SEQ_LENGTH = 512

ENV_SEED = 42
N_TRAIN = 1000
N_HELDOUT = 200
SNR_DB = 10.0

LSQ_BASELINE_CEILING = 0.94

DEFAULT_OUT = Path("ergon/pipeline_d/runs/tire_kick_b/tire_kick_b_results.json")


# ---------------------------------------------------------------------------
# Corpus construction (real labels — NO shuffle)
# ---------------------------------------------------------------------------


def _real_label_records() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Generate the synthetic env corpus with REAL labels intact.

    Env seed is fixed across shuffle seeds so the corpus stays
    identical between runs; only the train-order shuffle changes.
    """
    from ergon.diagnostic_c.synthetic_env import generate_synthetic_corpus

    train_corpus, _ = generate_synthetic_corpus(
        n_train=N_TRAIN, n_heldout=N_HELDOUT, snr_db=SNR_DB, seed=ENV_SEED
    )
    train_recs = [r.to_dict() for r in train_corpus.train]
    heldout_recs = [r.to_dict() for r in train_corpus.heldout]
    return train_recs, heldout_recs


def _shuffle_train_order(records: List[Dict[str, Any]], seed: int) -> List[Dict[str, Any]]:
    """Shuffle train ORDER only. Labels travel with their records."""
    import random

    rng = random.Random(seed)
    out = list(records)
    rng.shuffle(out)
    return out


# ---------------------------------------------------------------------------
# Free GPU between runs
# ---------------------------------------------------------------------------


def _free_gpu() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


# ---------------------------------------------------------------------------
# Base-model zero-shot baseline (LoRA-must-beat)
# ---------------------------------------------------------------------------


def _run_base_zero_shot(heldout_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Load Qwen2.5-Math-1.5B-Instruct WITHOUT LoRA and evaluate on
    the held-out. Per design doc acceptance-criterion #4: this is the
    baseline LoRA must beat for the tire-kick to be informative."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.eval import evaluate_model
    from ergon.pipeline_d.model import load_qwen_math_15b

    t0 = time.time()
    base_model, tokenizer = load_qwen_math_15b(use_lora=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    eval_ds = load_dataset_for_training(
        heldout_records, tokenizer, max_seq_length=MAX_SEQ_LENGTH
    )
    metrics = evaluate_model(base_model, eval_ds, tokenizer)

    n_total = int(metrics["n"])
    accuracy = float(metrics["accuracy"])
    n_correct = int(round(accuracy * n_total))
    elapsed = time.time() - t0

    # Free the base model — the per-seed LoRA runs each load their own.
    del base_model, tokenizer
    _free_gpu()

    return {
        "accuracy": accuracy,
        "n_correct": n_correct,
        "n_total": n_total,
        "per_class_accuracy": metrics.get("per_class_accuracy"),
        "confusion_matrix": metrics.get("confusion_matrix"),
        "wall_clock_seconds": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Per-seed LoRA run
# ---------------------------------------------------------------------------


def _run_one_seed(
    seed: int,
    train_records: List[Dict[str, Any]],
    heldout_records: List[Dict[str, Any]],
    base_accuracy: float,
    base_n_correct: int,
    base_n_total: int,
    max_steps: int,
) -> Dict[str, Any]:
    """Train + eval one seed. Returns the per-seed result block."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.eval import evaluate_model
    from ergon.pipeline_d.model import load_qwen_math_15b
    from ergon.pipeline_d.train import TrainingArgs, train_model

    t0 = time.time()
    model, tokenizer = load_qwen_math_15b(use_lora=True, rank=LORA_RANK)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    shuffled_train = _shuffle_train_order(train_records, seed)
    train_ds = load_dataset_for_training(
        shuffled_train, tokenizer, max_seq_length=MAX_SEQ_LENGTH
    )
    eval_ds = load_dataset_for_training(
        heldout_records, tokenizer, max_seq_length=MAX_SEQ_LENGTH
    )

    args = TrainingArgs(
        run_name=f"tire_kick_b_seed{seed}",
        max_steps=max_steps,
        learning_rate=LEARNING_RATE,
        max_seq_length=MAX_SEQ_LENGTH,
        seed=seed,
    )
    train_metrics = train_model(model, tokenizer, train_ds, args=args)
    eval_metrics = evaluate_model(model, eval_ds, tokenizer)

    n_total = int(eval_metrics["n"])
    accuracy = float(eval_metrics["accuracy"])
    n_correct = int(round(accuracy * n_total))

    # Test 1: vs chance (0.5)
    bt_chance = binomtest(n_correct, n_total, p=CHANCE, alternative="greater")
    p_vs_chance = float(bt_chance.pvalue)
    beats_chance = p_vs_chance < ALPHA

    # Test 2: vs base-model zero-shot. Compare proportions via binomial
    # test against the base-model's empirical accuracy as null. This is
    # the cleanest check given the held-out is identical for both.
    # If base accuracy is at chance or below, this collapses to the
    # chance comparison; if base is above chance, LoRA must clear the
    # higher bar.
    p_base = max(base_accuracy, 1e-9)
    bt_base = binomtest(n_correct, n_total, p=min(p_base, 1.0 - 1e-9), alternative="greater")
    p_vs_base = float(bt_base.pvalue)
    beats_base = p_vs_base < ALPHA

    # Per-seed decision, used to roll up the overall verdict.
    if beats_chance and beats_base:
        decision = "BEATS_CHANCE_AND_BASE"
    elif (not beats_chance) and abs(accuracy - CHANCE) < 0.05:
        decision = "CHANCE_PARITY"
    else:
        decision = "CALIBRATED_FAIL"

    gap_to_lsq = float(LSQ_BASELINE_CEILING - accuracy)

    elapsed = time.time() - t0
    _free_gpu()

    return {
        "accuracy": accuracy,
        "n_correct": n_correct,
        "n_total": n_total,
        "p_vs_chance": p_vs_chance,
        "beats_chance_alpha_0_10": bool(beats_chance),
        "p_vs_base_model": p_vs_base,
        "beats_base_alpha_0_10": bool(beats_base),
        "base_accuracy": float(base_accuracy),
        "base_n_correct": int(base_n_correct),
        "base_n_total": int(base_n_total),
        "lsq_baseline_ceiling": LSQ_BASELINE_CEILING,
        "gap_to_lsq_ceiling": gap_to_lsq,
        "decision": decision,
        "max_steps_used": int(max_steps),
        "final_loss": train_metrics.get("final_loss"),
        "trained_steps": int(train_metrics.get("trained_steps", 0)),
        "wall_clock_seconds": float(elapsed),
        "per_class_accuracy": eval_metrics.get("per_class_accuracy"),
        "confusion_matrix": eval_metrics.get("confusion_matrix"),
    }


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------


def run_tire_kick_b(
    out_path: Path | str = DEFAULT_OUT,
    seeds: Tuple[int, ...] = SHUFFLE_SEEDS,
    max_steps: int = MAX_STEPS,
    per_run_time_budget_seconds: float = 30 * 60,
) -> Dict[str, Any]:
    """Run W4.2 in full and persist results to ``out_path``."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    overall_t0 = time.time()
    current_max_steps = max_steps

    results: Dict[str, Any] = {
        "runs": {},
        "base_model_zero_shot": {},
        "lsq_baseline_ceiling": LSQ_BASELINE_CEILING,
        "config": {
            "shuffle_seeds": list(seeds),
            "alpha": ALPHA,
            "chance": CHANCE,
            "max_steps_initial": int(max_steps),
            "learning_rate": LEARNING_RATE,
            "lora_rank": LORA_RANK,
            "max_seq_length": MAX_SEQ_LENGTH,
            "synthetic_env_seed": ENV_SEED,
            "synthetic_env_n_train": N_TRAIN,
            "synthetic_env_n_heldout": N_HELDOUT,
            "synthetic_env_snr_db": SNR_DB,
            "labels_shuffled": False,
        },
        "notes": [],
    }

    # --- Build corpus once ---
    try:
        train_recs, held_recs = _real_label_records()
    except Exception as exc:
        tb = traceback.format_exc()
        results["overall_verdict"] = "ENGINEERING_FAIL"
        results["error_type"] = type(exc).__name__
        results["error_msg"] = str(exc)
        results["traceback"] = tb
        results["wall_clock_total_seconds"] = float(time.time() - overall_t0)
        with out.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return results

    # --- Base model zero-shot ---
    try:
        base_block = _run_base_zero_shot(held_recs)
        results["base_model_zero_shot"] = base_block
        base_accuracy = float(base_block["accuracy"])
        base_n_correct = int(base_block["n_correct"])
        base_n_total = int(base_block["n_total"])
    except Exception as exc:
        tb = traceback.format_exc()
        results["base_model_zero_shot"] = {
            "error_type": type(exc).__name__,
            "error_msg": str(exc),
            "traceback": tb,
        }
        results["notes"].append(
            f"base zero-shot failed: {type(exc).__name__}: {exc}"
        )
        # Without a base baseline we still try the per-seed runs,
        # using chance as the floor for the vs-base test.
        base_accuracy = CHANCE
        base_n_correct = N_HELDOUT // 2
        base_n_total = N_HELDOUT

    # --- Per-seed LoRA runs ---
    eng_fail_seen = False
    for seed in seeds:
        try:
            block = _run_one_seed(
                seed=seed,
                train_records=train_recs,
                heldout_records=held_recs,
                base_accuracy=base_accuracy,
                base_n_correct=base_n_correct,
                base_n_total=base_n_total,
                max_steps=current_max_steps,
            )
        except Exception as exc:
            eng_fail_seen = True
            tb = traceback.format_exc()
            block = {
                "decision": "ENGINEERING_FAIL",
                "error_type": type(exc).__name__,
                "error_msg": str(exc),
                "traceback": tb,
            }
            results["notes"].append(
                f"seed={seed} failed: {type(exc).__name__}: {exc}"
            )

        results["runs"][f"seed_{seed}"] = block

        # Time-budget watchdog: shrink max_steps if a single run exceeded budget.
        if (
            block.get("wall_clock_seconds", 0.0) > per_run_time_budget_seconds
            and current_max_steps > 20
        ):
            current_max_steps = 20
            results["notes"].append(
                f"Reduced max_steps to 20 after seed={seed} took "
                f"{block['wall_clock_seconds']:.0f}s (>30 min)"
            )

    # --- Verdict aggregation ---
    decisions = [
        results["runs"][f"seed_{s}"].get("decision") for s in seeds
    ]
    if eng_fail_seen and not any(d == "BEATS_CHANCE_AND_BASE" for d in decisions):
        verdict = "ENGINEERING_FAIL"
    elif all(d == "BEATS_CHANCE_AND_BASE" for d in decisions):
        verdict = "PASS_BEATS_CHANCE_AND_BASE"
    elif all(d == "CHANCE_PARITY" for d in decisions):
        verdict = "CHANCE_PARITY"
    else:
        verdict = "CALIBRATED_FAIL"

    results["overall_verdict"] = verdict
    results["wall_clock_total_seconds"] = float(time.time() - overall_t0)

    with out.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _print_summary(results: Dict[str, Any]) -> None:
    print("\n=== W4.2 REAL-LABELS TIRE-KICK — RESULTS ===")
    base = results.get("base_model_zero_shot", {})
    if "accuracy" in base:
        print(
            f"\nBase-model zero-shot: acc={base['accuracy']:.3f} "
            f"({base['n_correct']}/{base['n_total']}), "
            f"wall={base.get('wall_clock_seconds', 0):.0f}s"
        )
    else:
        print(f"\nBase-model zero-shot: FAILED — {base.get('error_type')}: {base.get('error_msg')}")

    print(f"\nLSQ baseline ceiling: {results.get('lsq_baseline_ceiling')}")
    print("\nPer-seed LoRA results:")
    for seed_key, block in results.get("runs", {}).items():
        dec = block.get("decision", "?")
        if dec == "ENGINEERING_FAIL":
            print(f"  {seed_key}: ENGINEERING_FAIL — {block.get('error_type')}: {block.get('error_msg')}")
        else:
            print(
                f"  {seed_key}: acc={block.get('accuracy'):.3f} "
                f"({block.get('n_correct')}/{block.get('n_total')}), "
                f"p_vs_chance={block.get('p_vs_chance'):.4f}, "
                f"p_vs_base={block.get('p_vs_base_model'):.4f}, "
                f"gap_to_lsq={block.get('gap_to_lsq_ceiling'):.3f}, "
                f"decision={dec}, "
                f"wall={block.get('wall_clock_seconds', 0):.0f}s"
            )

    print(f"\nOVERALL VERDICT: {results.get('overall_verdict')}")
    print(f"Total wall clock: {results.get('wall_clock_total_seconds', 0):.0f}s")
    if results.get("notes"):
        print("Notes:")
        for n in results["notes"]:
            print(f"  - {n}")


def main() -> int:
    if sys.platform == "win32" and not sys.flags.utf8_mode and os.environ.get("PYTHONUTF8") != "1":
        print(
            "WARN: trl 1.3.0 requires UTF-8 default encoding on Windows. "
            "If imports fail, re-run with `python -X utf8 -m ergon.pipeline_d.tire_kick_b`.",
            file=sys.stderr,
        )

    out_path = Path(os.environ.get("TIRE_KICK_B_OUT", str(DEFAULT_OUT)))
    results = run_tire_kick_b(out_path=out_path)
    _print_summary(results)
    print(f"\nWrote: {out_path.resolve()}")
    verdict = results.get("overall_verdict")
    return 0 if verdict == "PASS_BEATS_CHANCE_AND_BASE" else (
        2 if verdict in ("CALIBRATED_FAIL", "CHANCE_PARITY") else 3
    )


if __name__ == "__main__":
    raise SystemExit(main())
