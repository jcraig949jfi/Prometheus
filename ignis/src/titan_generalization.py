"""
titan_generalization.py — Generalization tests for steering vectors (Tests 5-9).

Adapted from ChatGPT's Titan Council recommendations. Five probes:
  5 (token): decimal pair generalization   6 (prompt): paraphrase robustness
  7 (multistep): compositional reasoning   8 (kl): distribution shift
  9 (attention): head recruitment patterns

Usage:
    python titan_generalization.py --genome best_genome.pt --test all
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).parent))
from analysis_base import AnalysisBase, LOGIT_TRAPS, HELD_OUT_TRAPS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger("ignis.titan_generalization")

# --- Test batteries --------------------------------------------------------
TOKEN_TRAIN_PROMPTS = [
    {"prompt": "Statement: '9.11 is larger than 9.9'. True or False? Answer:",
     "target": "False", "anti": "True"},
    {"prompt": "Statement: '3.14 is larger than 3.2'. True or False? Answer:",
     "target": "False", "anti": "True"},
]

TOKEN_TEST_PROMPTS = [
    {"prompt": "Statement: '9.101 is larger than 9.99'. True or False? Answer:",
     "target": "False", "anti": "True"},
    {"prompt": "Statement: '8.2 is larger than 8.19'. True or False? Answer:",
     "target": "True", "anti": "False"},
    {"prompt": "Statement: '10.01 is larger than 10.1'. True or False? Answer:",
     "target": "False", "anti": "True"},
    {"prompt": "Statement: '7.005 is larger than 7.05'. True or False? Answer:",
     "target": "False", "anti": "True"},
]

PARAPHRASE_PROMPTS = [
    {"prompt": "Which number is greater: 9.11 or 9.9? Answer 9.11 or 9.9:",
     "target": "9", "anti": "9",  # Handled specially below
     "label": "paraphrase"},
    {"prompt": "9.11 > 9.9 — True or False? Answer:",
     "target": "False", "anti": "True", "label": "noisy_format"},
    {"prompt": "Between the decimals 9.11 and 9.9, which is larger? Answer 9.11 or 9.9:",
     "target": "9", "anti": "9", "label": "verbose"},
    {"prompt": "Pick the bigger value: 9.11 vs 9.9. Answer 9.11 or 9.9:",
     "target": "9", "anti": "9", "label": "casual"},
    {"prompt": "Some say 9.11 > 9.9. True or False? Answer:",
     "target": "False", "anti": "True", "label": "adversarial"},
]


MULTISTEP_PROMPTS = [
    {"prompt": "What is (12 * 3) + 5? Answer with just the number:",
     "target": "41", "anti": "36", "label": "2-step arithmetic"},
    {"prompt": "A train travels 60 miles in 2 hours. Speed in mph? Answer:",
     "target": "30", "anti": "60", "label": "rate problem"},
    {"prompt": "If 9.11 < 9.9 and 8.2 > 8.19, are both correct? Yes or No:",
     "target": "Yes", "anti": "No", "label": "compositional decimal"},
    {"prompt": "All cats are animals. Some animals are fast. Are all cats fast? Yes or No:",
     "target": "No", "anti": "Yes", "label": "syllogism"},
]

# --- Test functions --------------------------------------------------------

def _margin(base: AnalysisBase, prompt: str, target: str, anti: str,
            hooks=None) -> float:
    """Compute logit margin for an arbitrary prompt/token pair."""
    from analysis_base import get_logit_margin
    return get_logit_margin(base.model, prompt, target, anti, hooks=hooks)


def test_token_generalization(base: AnalysisBase) -> dict:
    """Test 5: Does the vector generalise to unseen decimal pairs?"""
    log.info("=== Test 5: Token Generalization ===")
    hooks = base.steering_hooks()
    results = {"train": [], "test": []}

    for split, prompts in [("train", TOKEN_TRAIN_PROMPTS),
                           ("test", TOKEN_TEST_PROMPTS)]:
        for p in prompts:
            m_base = _margin(base, p["prompt"], p["target"], p["anti"])
            m_steer = _margin(base, p["prompt"], p["target"], p["anti"],
                              hooks=hooks)
            entry = {
                "prompt": p["prompt"],
                "margin_base": round(m_base, 4),
                "margin_steered": round(m_steer, 4),
                "delta": round(m_steer - m_base, 4),
            }
            results[split].append(entry)
            log.info(f"  [{split}] delta={entry['delta']:+.4f}  {p['prompt'][:50]}...")

    train_deltas = [e["delta"] for e in results["train"]]
    test_deltas = [e["delta"] for e in results["test"]]
    results["mean_train_delta"] = round(sum(train_deltas) / max(len(train_deltas), 1), 4)
    results["mean_test_delta"] = round(sum(test_deltas) / max(len(test_deltas), 1), 4)
    results["generalizes"] = results["mean_test_delta"] > 0.5 * results["mean_train_delta"]
    verdict = "CONCEPT" if results["generalizes"] else "LEXICAL"
    results["verdict"] = verdict
    log.info(f"  Verdict: {verdict} (train={results['mean_train_delta']:+.4f}, "
             f"test={results['mean_test_delta']:+.4f})")
    return results


def test_prompt_distribution(base: AnalysisBase) -> dict:
    """Test 6: Does the effect survive paraphrasing?"""
    log.info("=== Test 6: Prompt Distribution Shift ===")
    hooks = base.steering_hooks()

    # Baseline: canonical decimal trap
    canonical = LOGIT_TRAPS[0]  # Decimal Magnitude
    m_base_canon = base.get_margin(canonical)
    m_steer_canon = base.get_margin(canonical, hooks=hooks)

    results = {
        "canonical_base": round(m_base_canon, 4),
        "canonical_steered": round(m_steer_canon, 4),
        "canonical_delta": round(m_steer_canon - m_base_canon, 4),
        "paraphrases": [],
    }

    for p in PARAPHRASE_PROMPTS:
        m_base = _margin(base, p["prompt"], p["target"], p["anti"])
        m_steer = _margin(base, p["prompt"], p["target"], p["anti"],
                          hooks=hooks)
        entry = {
            "label": p.get("label", ""),
            "prompt": p["prompt"],
            "margin_base": round(m_base, 4),
            "margin_steered": round(m_steer, 4),
            "delta": round(m_steer - m_base, 4),
        }
        results["paraphrases"].append(entry)
        log.info(f"  [{entry['label']}] delta={entry['delta']:+.4f}")

    deltas = [e["delta"] for e in results["paraphrases"]]
    results["mean_paraphrase_delta"] = round(sum(deltas) / max(len(deltas), 1), 4)
    results["robust"] = results["mean_paraphrase_delta"] > 0.3 * results["canonical_delta"]
    verdict = "ROBUST" if results["robust"] else "BRITTLE"
    results["verdict"] = verdict
    log.info(f"  Verdict: {verdict}")
    return results


def test_multistep(base: AnalysisBase) -> dict:
    """Test 7: Does the vector help on multi-step reasoning?"""
    log.info("=== Test 7: Multi-Step Reasoning ===")
    hooks = base.steering_hooks()
    results = {"prompts": []}

    for p in MULTISTEP_PROMPTS:
        m_base = _margin(base, p["prompt"], p["target"], p["anti"])
        m_steer = _margin(base, p["prompt"], p["target"], p["anti"],
                          hooks=hooks)
        entry = {
            "label": p["label"],
            "prompt": p["prompt"],
            "margin_base": round(m_base, 4),
            "margin_steered": round(m_steer, 4),
            "delta": round(m_steer - m_base, 4),
        }
        results["prompts"].append(entry)
        log.info(f"  [{entry['label']}] base={m_base:+.4f} steered={m_steer:+.4f} "
                 f"delta={entry['delta']:+.4f}")

    deltas = [e["delta"] for e in results["prompts"]]
    results["mean_delta"] = round(sum(deltas) / max(len(deltas), 1), 4)
    results["helps_multistep"] = results["mean_delta"] > 0.0
    verdict = "REASONING" if results["helps_multistep"] else "HEURISTIC"
    results["verdict"] = verdict
    log.info(f"  Verdict: {verdict} (mean_delta={results['mean_delta']:+.4f})")
    return results


def test_kl_divergence(base: AnalysisBase) -> dict:
    """Test 8: KL(steered || base) — mode shift vs amplification."""
    log.info("=== Test 8: KL Divergence ===")
    hooks = base.steering_hooks()
    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS
    results = {"traps": []}

    for trap in all_traps:
        tokens = base.model.to_tokens(trap["prompt"])
        with torch.no_grad():
            logits_base = base.model(tokens)[0, -1, :]
            logits_steer = base.model.run_with_hooks(
                tokens, fwd_hooks=hooks
            )[0, -1, :]

        # KL(base || steered): how much the steered distribution diverges
        log_p = F.log_softmax(logits_steer.float(), dim=-1)
        q = F.softmax(logits_base.float(), dim=-1)
        kl = F.kl_div(log_p, q, reduction="sum").item()

        entry = {
            "name": trap["name"],
            "kl_divergence": round(kl, 4),
        }
        results["traps"].append(entry)
        log.info(f"  {trap['name']}: KL={kl:.4f}")

    kls = [e["kl_divergence"] for e in results["traps"]]
    results["mean_kl"] = round(sum(kls) / max(len(kls), 1), 4)
    # Heuristic threshold: KL > 5 suggests mode shift rather than amplification
    results["mode_shift"] = results["mean_kl"] > 5.0
    verdict = "MODE_SHIFT" if results["mode_shift"] else "AMPLIFICATION"
    results["verdict"] = verdict
    log.info(f"  Verdict: {verdict} (mean_KL={results['mean_kl']:.4f})")
    return results


def test_attention_patterns(base: AnalysisBase) -> dict:
    """Test 9: Compare attention patterns before/after steering."""
    log.info("=== Test 9: Attention Pattern Analysis ===")
    hooks = base.steering_hooks()

    prompt = LOGIT_TRAPS[0]["prompt"]  # Decimal Magnitude
    tokens = base.model.to_tokens(prompt)

    with torch.no_grad():
        _, cache_base = base.model.run_with_cache(tokens)
        _, cache_steer = base.model.run_with_cache(tokens, fwd_hooks=hooks)

    results = {"layers": []}
    diffs = []

    for layer_idx in range(base.n_layers):
        attn_base = cache_base[f"blocks.{layer_idx}.attn.hook_pattern"]
        attn_steer = cache_steer[f"blocks.{layer_idx}.attn.hook_pattern"]
        diff = (attn_base - attn_steer).abs().mean().item()
        diffs.append(diff)
        results["layers"].append({
            "layer": layer_idx,
            "mean_attn_diff": round(diff, 6),
        })

    # Find top-5 most affected layers
    sorted_layers = sorted(results["layers"],
                           key=lambda x: x["mean_attn_diff"], reverse=True)
    top5 = sorted_layers[:5]
    results["top_affected_layers"] = top5
    for entry in top5:
        log.info(f"  Layer {entry['layer']}: diff={entry['mean_attn_diff']:.6f}")

    mean_diff = sum(diffs) / max(len(diffs), 1)
    max_diff = max(diffs) if diffs else 0.0
    results["mean_diff"] = round(mean_diff, 6)
    results["max_diff"] = round(max_diff, 6)
    results["concentration_ratio"] = round(max_diff / (mean_diff + 1e-10), 2)
    # High concentration = specific heads recruited; low = diffuse shift
    results["structured"] = results["concentration_ratio"] > 3.0
    verdict = "STRUCTURED" if results["structured"] else "DIFFUSE"
    results["verdict"] = verdict
    log.info(f"  Verdict: {verdict} (concentration={results['concentration_ratio']:.2f})")
    return results


# --- CLI and main ----------------------------------------------------------

TEST_REGISTRY = {
    "token": test_token_generalization,
    "prompt": test_prompt_distribution,
    "multistep": test_multistep,
    "kl": test_kl_divergence,
    "attention": test_attention_patterns,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Titan generalization tests (Tests 5-9) for steering vectors",
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument(
        "--test", type=str, default="all",
        choices=["all"] + list(TEST_REGISTRY.keys()),
        help="Which test to run (default: all)",
    )
    return parser.parse_args()


def print_summary(all_results: dict):
    """Print a summary table of all test verdicts."""
    metric_keys = {"token": "mean_test_delta", "prompt": "mean_paraphrase_delta",
                   "multistep": "mean_delta", "kl": "mean_kl",
                   "attention": "concentration_ratio"}
    log.info("\n" + "=" * 60)
    log.info("GENERALIZATION SUMMARY")
    log.info("=" * 60)
    log.info(f"  {'Test':<15} {'Verdict':<15} {'Key Metric'}")
    log.info(f"  {'-'*13:<15} {'-'*13:<15} {'-'*20}")
    for name, result in all_results.items():
        mk = metric_keys.get(name, "")
        metric = f"{mk}={result.get(mk, 'N/A')}" if mk else ""
        log.info(f"  {name:<15} {result.get('verdict','N/A'):<15} {metric}")
    log.info("=" * 60)
    precip = sum(1 for r in all_results.values()
                 if r.get("verdict") in ("CONCEPT","ROBUST","REASONING",
                                         "AMPLIFICATION","STRUCTURED"))
    total = len(all_results)
    label = ("Strong precipitation" if precip >= 4
             else "Mixed signal" if precip >= 2 else "Bypass pattern")
    log.info(f"  OVERALL: {label} ({precip}/{total} tests pass)")


def main():
    args = parse_args()

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    tests_to_run = list(TEST_REGISTRY.keys()) if args.test == "all" else [args.test]
    all_results = {}

    for test_name in tests_to_run:
        fn = TEST_REGISTRY[test_name]
        all_results[test_name] = fn(base)

    print_summary(all_results)

    # Save JSON
    output = {
        "metadata": {
            "model": args.model,
            "genome": args.genome,
            "device": args.device,
            "timestamp": base.timestamp(),
        },
        "results": all_results,
    }
    path = base.save_json(output, "titan_generalization")
    log.info(f"Results saved: {path}")


if __name__ == "__main__":
    main()
