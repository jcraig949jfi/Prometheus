"""W4.1 — real-labels tire-kick on the 17-entry Lehmer boundary layer.

Cleared by W4.0 PASS (`runs/null_gate/null_gate_results.json`). Runs the
controlled twin of the null gate against REAL labels. Per Aporia's
2026-05-05 closed-loop bias mitigation each seed runs TWICE: once on a
filtered corpus (Charon morphology filter; expected no-op on Lehmer per
W3.7) and once on the unfiltered control. Both evaluate on the same
unfiltered held-out (synthetic_holdout via x->-x reflection).

Statistical discipline (substrate-grade, per task spec)
-------------------------------------------------------
- Held-out accuracy on 2-class post_fold (the cls_post_fold field).
- Binomial test vs. majority-class baseline (15/17 ~ 0.882) with
  alternative='greater', alpha=0.10. The 17-entry post_fold is
  catastrophically imbalanced — testing against 0.5 is theatre. The
  meaningful question is whether LoRA beats "always predict
  cyclotomic_noise."
- Comparison to base-model zero-shot (Qwen without LoRA) — LoRA must
  also beat the base for the lift to be informative.
- 4-way held-out accuracy (the held-out coefficients are reflected
  versions of the training coefficients; if the model overfit on raw
  coeffs it will mispredict the 4-class label).

Verdict logic
-------------
PASS_BEATS_MAJORITY: LoRA significantly beats majority baseline
    (p < 0.10) AND beats base-model zero-shot accuracy.
CALIBRATED_FAIL: LoRA does NOT significantly beat majority OR fails
    to beat base. Names what data/scale would be needed.
MAJORITY_PARITY: LoRA matches majority (e.g. always predicts
    cyclotomic_noise) but doesn't significantly exceed it. Informative:
    names the floor.
ENGINEERING_FAIL: a run errored out.

Windows note: trl 1.3.0 chat templates require UTF-8. Run with
``python -X utf8 -m ergon.pipeline_d.tire_kick_a`` or set
``PYTHONUTF8=1``.
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


SEEDS: Tuple[int, ...] = (42, 1234, 100)
ALPHA = 0.10

MAX_STEPS = 50
LEARNING_RATE = 5e-5
LORA_RANK = 8
MAX_SEQ_LENGTH = 512

DEFAULT_OUT = Path("ergon/pipeline_d/runs/tire_kick_a/tire_kick_a_results.json")


# ---------------------------------------------------------------------------
# Fixture + filter setup (run once; reused across seeds)
# ---------------------------------------------------------------------------


def _load_fixtures_filtered_unfiltered() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, int]]:
    """Load the 17-entry train fixture + 17-entry synthetic held-out, then
    apply the Charon morphology filter to the train set.

    Returns (filtered_train, unfiltered_train, heldout, drop_counts).
    Held-out is always unfiltered per spec (we evaluate on the same
    distribution regardless of training filter).
    """
    from ergon.pipeline_d.boundary_layer_fixture import (
        load_17_entry_fixture,
        load_heldout_fixture,
    )
    from ergon.pipeline_d.data_filter import filter_corpus, load_morphology_classifier

    fixture = load_17_entry_fixture()
    held, _meta = load_heldout_fixture()
    unfiltered_train = [r.to_dict() for r in fixture]
    heldout_recs = [r.to_dict() for r in held]

    clf = load_morphology_classifier()
    filtered_train, _dropped, drop_counts = filter_corpus(unfiltered_train, clf)
    # filter_corpus tags retained records with `morphology_class`; that's
    # fine — the data_loader serializer only reads coeffs/Mahler/factors/
    # class fields, so the extra metadata is harmless.
    return list(filtered_train), unfiltered_train, heldout_recs, drop_counts


# ---------------------------------------------------------------------------
# Per-(variant, seed) trainer
# ---------------------------------------------------------------------------


def _free_gpu() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _eval_block(model, tokenizer, eval_ds, candidate_post_fold, candidate_4way) -> Dict[str, Any]:
    """Run the eval harness twice — once with post_fold candidate set
    (so the parser maps free-form text to one of {cyclotomic_noise,
    lehmer_composite}), once with 4-way candidate set. The post_fold
    eval treats `completion` as the gold post_fold label; the 4-way eval
    builds a parallel dataset whose `completion` is the 4-way `class`.
    """
    from ergon.pipeline_d.eval import evaluate_model

    pf_metrics = evaluate_model(
        model, eval_ds, tokenizer,
        candidate_labels=list(candidate_post_fold),
        log_predictions=False,
    )
    return pf_metrics


def _build_4way_eval_ds(heldout_records: List[Dict[str, Any]], tokenizer) -> Any:
    """Build an eval Dataset whose `completion` field is the 4-way
    `class` label (data_loader's _extract_label prefers
    class_post_fold > class > label, so we strip class_post_fold)."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training

    stripped = []
    for r in heldout_records:
        d = dict(r)
        d.pop("class_post_fold", None)  # force fallback to `class` (4-way)
        stripped.append(d)
    return load_dataset_for_training(stripped, tokenizer, max_seq_length=MAX_SEQ_LENGTH)


def _run_one(variant_name: str, seed: int, train_records: List[Dict[str, Any]],
             heldout_records: List[Dict[str, Any]], max_steps: int) -> Dict[str, Any]:
    """Train + eval one (variant, seed) pair. Returns the per-seed result block."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.model import load_qwen_math_15b
    from ergon.pipeline_d.train import TrainingArgs, train_model

    t0 = time.time()
    model, tokenizer = load_qwen_math_15b(use_lora=True, rank=LORA_RANK)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_ds = load_dataset_for_training(train_records, tokenizer, max_seq_length=MAX_SEQ_LENGTH)
    eval_ds_pf = load_dataset_for_training(heldout_records, tokenizer, max_seq_length=MAX_SEQ_LENGTH)
    eval_ds_4w = _build_4way_eval_ds(heldout_records, tokenizer)

    args = TrainingArgs(
        run_name=f"tire_kick_a_{variant_name}_seed{seed}",
        max_steps=max_steps,
        learning_rate=LEARNING_RATE,
        max_seq_length=MAX_SEQ_LENGTH,
        seed=seed,
    )
    train_metrics = train_model(model, tokenizer, train_ds, args=args)

    pf = _eval_block(
        model, tokenizer, eval_ds_pf,
        candidate_post_fold=("cyclotomic_noise", "lehmer_composite"),
        candidate_4way=(
            "standard_quad_factor", "high_degree_reflection_pair",
            "phi_4_singleton", "lehmer_x_phi_n_k_composite",
        ),
    )
    # 4-way eval: candidate set = the four 4-way labels.
    from ergon.pipeline_d.eval import evaluate_model
    fw = evaluate_model(
        model, eval_ds_4w, tokenizer,
        candidate_labels=[
            "standard_quad_factor", "high_degree_reflection_pair",
            "phi_4_singleton", "lehmer_x_phi_n_k_composite",
        ],
        log_predictions=False,
    )

    n_total = int(pf["n"])
    accuracy_pf = float(pf["accuracy"])
    n_correct = int(round(accuracy_pf * n_total))

    # Majority-class baseline: 15/17 = 0.8824 (cyclotomic_noise dominates).
    gold = list(eval_ds_pf["completion"])
    counts: Dict[str, int] = {}
    for g in gold:
        counts[str(g)] = counts.get(str(g), 0) + 1
    majority_rate = max(counts.values()) / n_total if n_total else 0.5
    bt_maj = binomtest(n_correct, n_total, p=majority_rate, alternative="greater")
    p_vs_majority = float(bt_maj.pvalue)

    elapsed = time.time() - t0

    block = {
        "accuracy_post_fold": accuracy_pf,
        "accuracy_4way": float(fw["accuracy"]),
        "n_correct_post_fold": n_correct,
        "n_total": n_total,
        "majority_class_rate": float(majority_rate),
        "p_vs_majority": p_vs_majority,
        "decision_vs_majority": "BEATS" if p_vs_majority < ALPHA else "PARITY_OR_BELOW",
        "per_class_accuracy_post_fold": pf.get("per_class_accuracy"),
        "per_class_accuracy_4way": fw.get("per_class_accuracy"),
        "confusion_matrix_post_fold": pf.get("confusion_matrix"),
        "confusion_matrix_4way": fw.get("confusion_matrix"),
        "heldout_label_dist_post_fold": counts,
        "final_loss": train_metrics.get("final_loss"),
        "trained_steps": int(train_metrics.get("trained_steps", 0)),
        "max_steps_used": int(max_steps),
        "wall_clock_seconds": float(elapsed),
    }

    # Free model + LoRA before next seed (otherwise we OOM across 6 trainings).
    del model, tokenizer, train_ds, eval_ds_pf, eval_ds_4w
    _free_gpu()
    return block


# ---------------------------------------------------------------------------
# Base-model zero-shot baseline (run once)
# ---------------------------------------------------------------------------


def _zero_shot_baseline(heldout_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Load Qwen base (no LoRA) and evaluate on the held-out — the lift LoRA must beat."""
    from ergon.pipeline_d.data_loader import load_dataset_for_training
    from ergon.pipeline_d.eval import evaluate_model
    from ergon.pipeline_d.model import load_qwen_math_15b

    model, tokenizer = load_qwen_math_15b(use_lora=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    eval_ds_pf = load_dataset_for_training(heldout_records, tokenizer, max_seq_length=MAX_SEQ_LENGTH)
    eval_ds_4w = _build_4way_eval_ds(heldout_records, tokenizer)

    pf = evaluate_model(
        model, eval_ds_pf, tokenizer,
        candidate_labels=["cyclotomic_noise", "lehmer_composite"],
        log_predictions=False,
    )
    fw = evaluate_model(
        model, eval_ds_4w, tokenizer,
        candidate_labels=[
            "standard_quad_factor", "high_degree_reflection_pair",
            "phi_4_singleton", "lehmer_x_phi_n_k_composite",
        ],
        log_predictions=False,
    )

    out = {
        "accuracy_post_fold": float(pf["accuracy"]),
        "accuracy_4way": float(fw["accuracy"]),
        "per_class_accuracy_post_fold": pf.get("per_class_accuracy"),
        "per_class_accuracy_4way": fw.get("per_class_accuracy"),
        "confusion_matrix_post_fold": pf.get("confusion_matrix"),
        "n": int(pf["n"]),
    }
    del model, tokenizer
    _free_gpu()
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run_tire_kick_a(out_path: Path | str = DEFAULT_OUT, seeds: Tuple[int, ...] = SEEDS,
                    max_steps: int = MAX_STEPS) -> Dict[str, Any]:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    overall_t0 = time.time()

    filtered_train, unfiltered_train, heldout_recs, drop_counts = (
        _load_fixtures_filtered_unfiltered()
    )
    filter_was_no_op = sum(drop_counts.values()) == 0

    results: Dict[str, Any] = {
        "runs": {},
        "config": {
            "seeds": list(seeds),
            "alpha": ALPHA,
            "max_steps": int(max_steps),
            "learning_rate": LEARNING_RATE,
            "lora_rank": LORA_RANK,
            "max_seq_length": MAX_SEQ_LENGTH,
            "n_train_filtered": len(filtered_train),
            "n_train_unfiltered": len(unfiltered_train),
            "n_heldout": len(heldout_recs),
        },
        "filter_was_no_op": bool(filter_was_no_op),
        "drop_counts_per_seed": {  # filter is deterministic (no seed); same for all
            f"seed_{s}": dict(drop_counts) for s in seeds
        },
        "notes": [],
    }

    # --- Base-model zero-shot baseline (run once before LoRA runs) ---
    try:
        results["base_model_zero_shot"] = _zero_shot_baseline(heldout_recs)
    except Exception as exc:
        tb = traceback.format_exc()
        results["base_model_zero_shot"] = {
            "error_type": type(exc).__name__,
            "error_msg": str(exc),
            "traceback": tb,
        }
        results["notes"].append(f"base-model zero-shot failed: {type(exc).__name__}: {exc}")

    # --- Filtered + unfiltered runs across seeds ---
    for variant_name, train_recs in (("filtered", filtered_train), ("unfiltered", unfiltered_train)):
        for seed in seeds:
            key = f"{variant_name}_seed_{seed}"
            try:
                block = _run_one(variant_name, seed, train_recs, heldout_recs, max_steps)
            except Exception as exc:
                tb = traceback.format_exc()
                block = {
                    "decision_vs_majority": "ENGINEERING_FAIL",
                    "error_type": type(exc).__name__,
                    "error_msg": str(exc),
                    "traceback": tb,
                }
                results["notes"].append(f"{key} failed: {type(exc).__name__}: {exc}")
            results["runs"][key] = block

    # --- Verdict aggregation ---
    base_pf = results.get("base_model_zero_shot", {}).get("accuracy_post_fold")
    any_eng = any(b.get("decision_vs_majority") == "ENGINEERING_FAIL" for b in results["runs"].values())
    if any_eng:
        results["overall_verdict"] = "ENGINEERING_FAIL"
    else:
        # Use median accuracy across all 6 seeds (3 filtered + 3 unfiltered)
        # to set the verdict — single-seed flukes shouldn't drive it.
        accs = sorted(b["accuracy_post_fold"] for b in results["runs"].values())
        median_acc = accs[len(accs) // 2]
        beats_majority = sum(
            1 for b in results["runs"].values() if b.get("p_vs_majority", 1.0) < ALPHA
        )
        beats_base = (
            base_pf is not None and median_acc > base_pf + 1e-9
        )
        majority_rate_global = next(
            iter(results["runs"].values())
        )["majority_class_rate"]
        # PASS = MAJORITY of seeds beat majority (>=4/6) AND beats base.
        if beats_majority >= 4 and beats_base:
            verdict = "PASS_BEATS_MAJORITY"
        elif beats_majority == 0 and abs(median_acc - majority_rate_global) < 1e-6:
            verdict = "MAJORITY_PARITY"
        else:
            verdict = "CALIBRATED_FAIL"
        results["overall_verdict"] = verdict
        results["verdict_summary"] = {
            "median_accuracy_post_fold": float(median_acc),
            "n_seeds_beating_majority_p_lt_alpha": int(beats_majority),
            "beats_base_zero_shot": bool(beats_base),
            "majority_class_rate": float(majority_rate_global),
            "base_zero_shot_accuracy": (None if base_pf is None else float(base_pf)),
        }

    results["wall_clock_total_seconds"] = float(time.time() - overall_t0)

    with out.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    return results


def _print_summary(results: Dict[str, Any]) -> None:
    print("\n=== W4.1 TIRE-KICK A — RESULTS ===")
    base = results.get("base_model_zero_shot", {})
    if "error_type" in base:
        print(f"  base zero-shot: ENGINEERING_FAIL — {base.get('error_type')}: {base.get('error_msg')}")
    else:
        print(
            f"  base zero-shot: post_fold acc={base.get('accuracy_post_fold'):.3f}, "
            f"4way acc={base.get('accuracy_4way'):.3f}"
        )
    print(f"  filter_was_no_op={results['filter_was_no_op']} drop_counts(any seed)="
          f"{next(iter(results['drop_counts_per_seed'].values()), {})}")

    print("\n  per-(variant, seed) blocks:")
    for key, block in results["runs"].items():
        if block.get("decision_vs_majority") == "ENGINEERING_FAIL":
            print(f"  {key}: ENGINEERING_FAIL — {block.get('error_type')}: {block.get('error_msg')}")
            continue
        print(
            f"  {key}: pf_acc={block['accuracy_post_fold']:.3f} "
            f"({block['n_correct_post_fold']}/{block['n_total']}), "
            f"4w_acc={block['accuracy_4way']:.3f}, "
            f"p_vs_maj={block['p_vs_majority']:.4f} ({block['decision_vs_majority']}), "
            f"loss={block.get('final_loss')}, wall={block.get('wall_clock_seconds', 0):.0f}s"
        )

    print(f"\nOVERALL VERDICT: {results.get('overall_verdict')}")
    if results.get("verdict_summary"):
        for k, v in results["verdict_summary"].items():
            print(f"  {k}: {v}")
    print(f"Total wall clock: {results.get('wall_clock_total_seconds', 0):.0f}s")
    if results.get("notes"):
        print("Notes:")
        for n in results["notes"]:
            print(f"  - {n}")


def main() -> int:
    if sys.platform == "win32" and not sys.flags.utf8_mode and os.environ.get("PYTHONUTF8") != "1":
        print(
            "WARN: trl 1.3.0 requires UTF-8 default encoding on Windows. "
            "If imports fail, re-run with `python -X utf8 -m ergon.pipeline_d.tire_kick_a`.",
            file=sys.stderr,
        )

    out_path = Path(os.environ.get("TIRE_KICK_A_OUT", str(DEFAULT_OUT)))
    results = run_tire_kick_a(out_path=out_path)
    _print_summary(results)
    print(f"\nWrote: {out_path.resolve()}")
    verdict = results.get("overall_verdict")
    if verdict == "PASS_BEATS_MAJORITY":
        return 0
    if verdict == "MAJORITY_PARITY":
        return 4
    if verdict == "CALIBRATED_FAIL":
        return 5
    return 3  # ENGINEERING_FAIL or other


if __name__ == "__main__":
    raise SystemExit(main())
