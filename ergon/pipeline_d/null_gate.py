"""W4.0 — synthetic-null gate (COMMIT-BLOCKING).

Per `pivot/ergon_learner_v0.5_design_2026-05-05.md` §5 W4.0 + substrate-v2
§12 Build Gate 5 ("null-before-claim"). James's 2026-05-06 override made
this an explicit hard rule: if the gate fires (LoRA learns shuffled
labels above chance on either variant), STOP — emit SYNTHETIC_NULL_FIRED
verdict and DO NOT run W4.1 / W4.2.

The gate's job: catch label-leakage / memorization. Train Qwen2.5-Math-1.5B
+ LoRA on a corpus where labels have been randomly shuffled (no
relationship to features). If the model still beats chance on the
shuffled held-out, the tire-kick is measuring memorization rather than
learned structure.

Two variants per design:

Variant A — 17-entry boundary + synthetic_holdout (34 records total):
    Re-split 80/20 (~27 train / ~7 heldout) AFTER shuffling labels.

Variant B — synthetic env (n_train=1000, n_heldout=200, snr_db=10):
    Shuffle labels independently in train and heldout.

For each variant, run K=3 shuffle seeds (42, 1234, 100). Per-seed
binomial test: H0 acc = 0.5, alternative='greater', alpha = 0.10.
Gate fires if ANY (variant, seed) combination shows p < 0.10.

Training config matches the planned W4.1 spec: max_steps=50, lr=5e-5,
LoRA rank=8.

Windows note: trl 1.3.0 chat-template files require UTF-8 default
encoding. Run with `python -X utf8 -m ergon.pipeline_d.null_gate` or
set PYTHONUTF8=1 before invoking.

Outputs the full per-seed result block + overall verdict to
`ergon/pipeline_d/runs/null_gate/null_gate_results.json`.
"""
from __future__ import annotations

import gc
import json
import os
import random
import sys
import time
import traceback
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
from scipy.stats import binomtest


# ---------------------------------------------------------------------------
# Constants — matches W4.1 planned config so the null is a controlled twin.
# ---------------------------------------------------------------------------

SHUFFLE_SEEDS: Tuple[int, ...] = (42, 1234, 100)
ALPHA = 0.10
CHANCE = 0.5

MAX_STEPS = 50
LEARNING_RATE = 5e-5
LORA_RANK = 8
MAX_SEQ_LENGTH = 512
SPLIT_SEED = 7  # used for the post-shuffle 80/20 split in Variant A

DEFAULT_OUT = Path("ergon/pipeline_d/runs/null_gate/null_gate_results.json")


# ---------------------------------------------------------------------------
# Variant A — 17-entry boundary layer + synthetic_holdout
# ---------------------------------------------------------------------------


def _shuffled_records_variant_a(seed: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build the Variant-A shuffled corpus.

    Loads the 17-entry fixture + 17-entry held-out (34 total), shuffles
    the ``class_post_fold`` labels with the given seed, then re-splits
    80/20 (deterministic via SPLIT_SEED).

    Returns (train_records, heldout_records) — plain dicts, ready for
    `data_loader.load_dataset_for_training`.
    """
    from ergon.pipeline_d.boundary_layer_fixture import (
        load_17_entry_fixture,
        load_heldout_fixture,
    )

    fixture = load_17_entry_fixture()
    heldout, _ = load_heldout_fixture()
    all_recs = [r.to_dict() for r in fixture] + [r.to_dict() for r in heldout]

    # Pull out labels, shuffle in place under a local RNG, write back.
    rng = random.Random(seed)
    labels = [r["class_post_fold"] for r in all_recs]
    rng.shuffle(labels)
    for rec, new_lab in zip(all_recs, labels):
        rec["class_post_fold"] = new_lab

    # Deterministic 80/20 split — different seed from shuffle so the
    # shuffle isn't just undone by the split ordering.
    split_rng = random.Random(SPLIT_SEED)
    indices = list(range(len(all_recs)))
    split_rng.shuffle(indices)
    n_eval = max(1, int(round(0.2 * len(all_recs))))
    eval_idx = set(indices[:n_eval])
    train = [all_recs[i] for i in range(len(all_recs)) if i not in eval_idx]
    heldout_split = [all_recs[i] for i in range(len(all_recs)) if i in eval_idx]
    return train, heldout_split


# ---------------------------------------------------------------------------
# Variant B — synthetic env
# ---------------------------------------------------------------------------


def _shuffled_records_variant_b(
    seed: int,
    n_train: int = 1000,
    n_heldout: int = 200,
    snr_db: float = 10.0,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build the Variant-B shuffled corpus.

    Generates a synthetic corpus (env seed=42, fixed across the gate so
    the corpus stays identical between shuffle seeds), then shuffles the
    binary ``label`` field in train and heldout independently using
    ``seed``.

    SyntheticRecord uses ``label`` (not ``class_post_fold``); the
    data-loader's ``_extract_label`` falls back through
    ``class_post_fold > class > label`` so we serialize it as ``label``.
    """
    from ergon.diagnostic_c.synthetic_env import generate_synthetic_corpus

    train_corpus, _ = generate_synthetic_corpus(
        n_train=n_train, n_heldout=n_heldout, snr_db=snr_db, seed=42
    )
    train_recs = [r.to_dict() for r in train_corpus.train]
    heldout_recs = [r.to_dict() for r in train_corpus.heldout]

    rng = random.Random(seed)

    train_labels = [r["label"] for r in train_recs]
    rng.shuffle(train_labels)
    for r, new_lab in zip(train_recs, train_labels):
        r["label"] = new_lab

    held_labels = [r["label"] for r in heldout_recs]
    rng.shuffle(held_labels)
    for r, new_lab in zip(heldout_recs, held_labels):
        r["label"] = new_lab

    return train_recs, heldout_recs


# ---------------------------------------------------------------------------
# Per-seed gate run
# ---------------------------------------------------------------------------


def _free_gpu() -> None:
    """Release VRAM between seed runs so we don't OOM across 6 trainings."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _run_one_seed(
    variant_name: str,
    seed: int,
    train_records: List[Dict[str, Any]],
    heldout_records: List[Dict[str, Any]],
    max_steps: int,
) -> Dict[str, Any]:
    """Train + eval one (variant, seed) pair. Returns the per-seed result block."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.eval import evaluate_model
    from ergon.pipeline_d.model import load_qwen_math_15b
    from ergon.pipeline_d.train import TrainingArgs, train_model

    t0 = time.time()
    model, tokenizer = load_qwen_math_15b(use_lora=True, rank=LORA_RANK)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_ds = load_dataset_for_training(train_records, tokenizer, max_seq_length=MAX_SEQ_LENGTH)
    eval_ds = load_dataset_for_training(heldout_records, tokenizer, max_seq_length=MAX_SEQ_LENGTH)

    args = TrainingArgs(
        run_name=f"null_gate_{variant_name}_seed{seed}",
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

    # Binomial test: H0 = chance (0.5), alternative='greater' — per spec.
    bt = binomtest(n_correct, n_total, p=CHANCE, alternative="greater")
    p_value = float(bt.pvalue)
    decision = "FIRE" if p_value < ALPHA else "PASS"

    # Sidecar: also test against the empirical majority-class rate of
    # the held-out. With Variant A's 30:4 class imbalance the marginal
    # majority-class baseline is ~0.88, far above 0.5 — testing against
    # chance=0.5 there is dominated by class imbalance, not memorization.
    # The W6.1 dossier should weigh both numbers; the spec-stipulated
    # ``decision`` field uses chance=0.5 as instructed.
    gold_labels = list(eval_ds["completion"])
    counts: Dict[str, int] = {}
    for g in gold_labels:
        counts[str(g)] = counts.get(str(g), 0) + 1
    majority_rate = max(counts.values()) / n_total if n_total > 0 else CHANCE
    bt_maj = binomtest(n_correct, n_total, p=max(majority_rate, CHANCE), alternative="greater")
    p_value_vs_majority = float(bt_maj.pvalue)
    decision_vs_majority = "FIRE" if p_value_vs_majority < ALPHA else "PASS"

    elapsed = time.time() - t0
    _free_gpu()

    return {
        "accuracy": accuracy,
        "n_correct": n_correct,
        "n_total": n_total,
        "p_value": p_value,
        "decision": decision,
        "p_value_vs_majority": p_value_vs_majority,
        "decision_vs_majority": decision_vs_majority,
        "majority_class_rate": float(majority_rate),
        "heldout_label_dist": counts,
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


def run_null_gate(
    out_path: Path | str = DEFAULT_OUT,
    seeds: Tuple[int, ...] = SHUFFLE_SEEDS,
    max_steps: int = MAX_STEPS,
    per_run_time_budget_seconds: float = 30 * 60,
) -> Dict[str, Any]:
    """Run W4.0 in full and persist results to ``out_path``.

    If a per-seed run takes longer than ``per_run_time_budget_seconds``,
    subsequent runs drop max_steps to 20 (per spec) and that's recorded
    in each block.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    overall_t0 = time.time()
    current_max_steps = max_steps
    fired_on: List[Dict[str, Any]] = []

    results: Dict[str, Any] = {
        "variant_a_boundary": {},
        "variant_b_synthetic": {},
        "config": {
            "shuffle_seeds": list(seeds),
            "alpha": ALPHA,
            "chance": CHANCE,
            "max_steps_initial": int(max_steps),
            "learning_rate": LEARNING_RATE,
            "lora_rank": LORA_RANK,
            "max_seq_length": MAX_SEQ_LENGTH,
            "split_seed_variant_a": SPLIT_SEED,
            "synthetic_env_seed": 42,
            "synthetic_env_n_train": 1000,
            "synthetic_env_n_heldout": 200,
            "synthetic_env_snr_db": 10.0,
        },
        "notes": [],
    }

    # --- Variant A ---
    for seed in seeds:
        try:
            train_recs, held_recs = _shuffled_records_variant_a(seed)
            block = _run_one_seed(
                "variant_a", seed, train_recs, held_recs, current_max_steps
            )
        except Exception as exc:
            tb = traceback.format_exc()
            block = {
                "decision": "ENGINEERING_FAIL",
                "error_type": type(exc).__name__,
                "error_msg": str(exc),
                "traceback": tb,
            }
            results["notes"].append(
                f"variant_a seed={seed} failed: {type(exc).__name__}: {exc}"
            )
        results["variant_a_boundary"][f"seed_{seed}"] = block
        if block.get("decision") == "FIRE":
            fired_on.append({"variant": "variant_a_boundary", "seed": int(seed)})

        # Time-budget watchdog: shrink max_steps if a single run exceeded budget.
        if block.get("wall_clock_seconds", 0.0) > per_run_time_budget_seconds and current_max_steps > 20:
            current_max_steps = 20
            results["notes"].append(
                f"Reduced max_steps to 20 after variant_a seed={seed} took "
                f"{block['wall_clock_seconds']:.0f}s (>30 min)"
            )

    # --- Variant B ---
    for seed in seeds:
        try:
            train_recs, held_recs = _shuffled_records_variant_b(seed)
            block = _run_one_seed(
                "variant_b", seed, train_recs, held_recs, current_max_steps
            )
        except Exception as exc:
            tb = traceback.format_exc()
            block = {
                "decision": "ENGINEERING_FAIL",
                "error_type": type(exc).__name__,
                "error_msg": str(exc),
                "traceback": tb,
            }
            results["notes"].append(
                f"variant_b seed={seed} failed: {type(exc).__name__}: {exc}"
            )
        results["variant_b_synthetic"][f"seed_{seed}"] = block
        if block.get("decision") == "FIRE":
            fired_on.append({"variant": "variant_b_synthetic", "seed": int(seed)})

        if block.get("wall_clock_seconds", 0.0) > per_run_time_budget_seconds and current_max_steps > 20:
            current_max_steps = 20
            results["notes"].append(
                f"Reduced max_steps to 20 after variant_b seed={seed} took "
                f"{block['wall_clock_seconds']:.0f}s (>30 min)"
            )

    # --- Verdict aggregation ---
    any_eng_fail = any(
        results["variant_a_boundary"][f"seed_{s}"].get("decision") == "ENGINEERING_FAIL"
        for s in seeds
    ) or any(
        results["variant_b_synthetic"][f"seed_{s}"].get("decision") == "ENGINEERING_FAIL"
        for s in seeds
    )
    if any_eng_fail and not fired_on:
        verdict = "ENGINEERING_FAIL"
    elif fired_on:
        verdict = "FIRE"
    else:
        verdict = "PASS"

    results["overall_verdict"] = verdict
    results["gate_fired_on"] = fired_on
    results["wall_clock_total_seconds"] = float(time.time() - overall_t0)

    with out.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    return results


def _print_summary(results: Dict[str, Any]) -> None:
    print("\n=== W4.0 SYNTHETIC-NULL GATE — RESULTS ===")
    for variant in ("variant_a_boundary", "variant_b_synthetic"):
        print(f"\n[{variant}]")
        for seed_key, block in results[variant].items():
            dec = block.get("decision", "?")
            if dec == "ENGINEERING_FAIL":
                print(f"  {seed_key}: ENGINEERING_FAIL — {block.get('error_type')}: {block.get('error_msg')}")
            else:
                print(
                    f"  {seed_key}: acc={block.get('accuracy'):.3f} "
                    f"({block.get('n_correct')}/{block.get('n_total')}), "
                    f"p={block.get('p_value'):.4f}, decision={dec}, "
                    f"wall={block.get('wall_clock_seconds', 0):.0f}s"
                )
    print(f"\nOVERALL VERDICT: {results['overall_verdict']}")
    if results["gate_fired_on"]:
        print(f"Gate fired on: {results['gate_fired_on']}")
    print(f"Total wall clock: {results.get('wall_clock_total_seconds', 0):.0f}s")
    if results.get("notes"):
        print("Notes:")
        for n in results["notes"]:
            print(f"  - {n}")


def main() -> int:
    if sys.platform == "win32" and not sys.flags.utf8_mode and os.environ.get("PYTHONUTF8") != "1":
        print(
            "WARN: trl 1.3.0 requires UTF-8 default encoding on Windows. "
            "If imports fail, re-run with `python -X utf8 -m ergon.pipeline_d.null_gate`.",
            file=sys.stderr,
        )

    out_path = Path(os.environ.get("NULL_GATE_OUT", str(DEFAULT_OUT)))
    results = run_null_gate(out_path=out_path)
    _print_summary(results)
    print(f"\nWrote: {out_path.resolve()}")
    return 0 if results["overall_verdict"] == "PASS" else (
        2 if results["overall_verdict"] == "FIRE" else 3
    )


if __name__ == "__main__":
    raise SystemExit(main())
