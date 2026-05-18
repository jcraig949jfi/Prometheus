"""Model Sweep — Generate reasoning tools from multiple models, evaluate later.

Fast generation pass: for each model, send the same 100 concept prompts,
save raw code outputs. No 5-gate validation, no trap battery. Just generate
and store. Evaluation happens in a separate scoring pass.

Usage:
    # Generate from all models
    python model_sweep.py --generate

    # Generate from one model
    python model_sweep.py --generate --model deepseek-ai/deepseek-v4-pro

    # Score all generated outputs
    python model_sweep.py --score

    # Summary matrix
    python model_sweep.py --matrix
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from openai import OpenAI

# Paths
HEPH_ROOT = Path(__file__).resolve().parent.parent
SWEEP_DIR = HEPH_ROOT / "model_sweep"
CANDIDATES_PATH = SWEEP_DIR / "candidates_100.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompts import build_code_gen_prompt, select_frame
from code_extractor import extract_code
from hephaestus import (
    _inject_missing_imports, _sanitize_unicode, _fix_common_errors,
    _compute_novelty, load_all_nous_results, filter_results, combo_key,
    load_ledger, FORGE_DIR,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SWEEP] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("model_sweep")

# Auto-load .env
_ENV = HEPH_ROOT / ".env"
if _ENV.exists():
    for line in _ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# ---------------------------------------------------------------------------
# Models to sweep
# ---------------------------------------------------------------------------

MODELS = [
    # Control
    {"id": "qwen/qwen3.5-397b-a17b", "tag": "qwen-397B-ctrl", "category": "control"},
    # Code specialists
    {"id": "qwen/qwen3-coder-480b-a35b-instruct", "tag": "qwen3-coder-480B", "category": "code"},
    {"id": "mistralai/codestral-22b-instruct-v0.1", "tag": "codestral-22B", "category": "code"},
    # Reasoning-tuned
    {"id": "qwen/qwen3-next-80b-a3b-thinking", "tag": "qwen3-thinking-80B", "category": "reasoning"},
    {"id": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", "tag": "nemotron-reasoning-30B", "category": "reasoning"},
    # Large general
    {"id": "deepseek-ai/deepseek-v4-pro", "tag": "deepseek-v4-pro", "category": "frontier"},
    {"id": "deepseek-ai/deepseek-v4-flash", "tag": "deepseek-v4-flash", "category": "frontier"},
    {"id": "mistralai/mistral-large-3-675b-instruct-2512", "tag": "mistral-675B", "category": "large"},
    {"id": "nvidia/llama-3.1-nemotron-ultra-253b-v1", "tag": "nemotron-ultra-253B", "category": "large"},
    # Different architectures
    {"id": "meta/llama-4-maverick-17b-128e-instruct", "tag": "llama4-maverick-17B", "category": "arch"},
    {"id": "meta/llama-3.3-70b-instruct", "tag": "llama-3.3-70B", "category": "arch"},
    {"id": "google/gemma-4-31b-it", "tag": "gemma4-31B", "category": "arch"},
]


def _make_client():
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        log.error("NVIDIA_API_KEY not set")
        sys.exit(1)
    return OpenAI(
        base_url=os.environ.get("NVIDIA_API_ENDPOINT", "https://integrate.api.nvidia.com/v1"),
        api_key=api_key,
        timeout=180.0,
    )


# ---------------------------------------------------------------------------
# Step 1: Freeze 100 candidates
# ---------------------------------------------------------------------------

def freeze_candidates(n=100):
    """Select and freeze 100 representative concept combinations."""
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)

    if CANDIDATES_PATH.exists():
        data = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
        log.info("Loaded %d frozen candidates from %s", len(data), CANDIDATES_PATH)
        return data

    # Load all Nous results
    results, sources = load_all_nous_results()
    ledger = load_ledger()
    log.info("Loaded %d Nous results, %d ledger entries", len(results), len(ledger))

    # Separate into buckets based on historical forge outcome
    forged = []
    near_miss = []
    moderate = []
    hard_fail = []

    for entry in results:
        key = combo_key(entry)
        ledger_entry = ledger.get(key)
        if ledger_entry is None:
            moderate.append(entry)  # Never attempted
            continue
        if ledger_entry["status"] == "forged":
            forged.append(entry)
        else:
            reason = ledger_entry.get("reason", "")
            import re
            m = re.search(r"acc=(\d+)%", reason)
            if m:
                acc = int(m.group(1))
                if acc >= 35:
                    near_miss.append(entry)
                elif acc >= 20:
                    moderate.append(entry)
                else:
                    hard_fail.append(entry)
            else:
                hard_fail.append(entry)

    import random
    random.seed(42)

    candidates = []
    # 20 forged (known successes)
    candidates.extend(random.sample(forged, min(20, len(forged))))
    # 30 near-misses
    candidates.extend(random.sample(near_miss, min(30, len(near_miss))))
    # 30 moderate
    candidates.extend(random.sample(moderate, min(30, len(moderate))))
    # 20 hard fails or never-attempted
    candidates.extend(random.sample(hard_fail, min(20, len(hard_fail))))

    # Serialize with full provenance
    frozen = []
    for entry in candidates:
        frozen.append({
            "key": combo_key(entry),
            "concept_names": entry.get("concept_names", []),
            "concept_fields": entry.get("concept_fields", []),
            "composite_score": entry.get("score", {}).get("composite_score", 0),
            "response_text": entry.get("response_text", "")[:2000],
            "ratings": entry.get("score", {}).get("ratings", {}),
        })

    CANDIDATES_PATH.write_text(json.dumps(frozen, indent=2), encoding="utf-8")
    log.info("Froze %d candidates to %s", len(frozen), CANDIDATES_PATH)
    return frozen


# ---------------------------------------------------------------------------
# Step 2: Generate from one model
# ---------------------------------------------------------------------------

def generate_from_model(model_id: str, model_tag: str, candidates: list,
                        max_items: int = 100):
    """Generate reasoning tools from a single model. Store raw code only."""
    output_dir = SWEEP_DIR / model_tag
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.jsonl"

    # Load already-generated to support resume
    done_keys = set()
    if results_path.exists():
        for line in results_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    done_keys.add(json.loads(line)["key"])
                except Exception:
                    pass

    client = _make_client()
    generated = 0
    failed = 0

    for i, cand in enumerate(candidates[:max_items]):
        if cand["key"] in done_keys:
            continue

        names = cand["concept_names"]
        response_text = cand["response_text"]
        ratings = cand["ratings"]

        # Build prompt (same as main forge)
        from hephaestus import load_enrichment
        enrichment = None  # Skip Coeus for speed in sweep
        frame = select_frame()
        prompt = build_code_gen_prompt(names, response_text, ratings,
                                       enrichment=enrichment, frame=frame)

        # Call API
        log.info("[%s] [%d/%d] %s", model_tag, i + 1, len(candidates),
                 " + ".join(names))
        try:
            resp = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=4096,
            )
            raw_response = resp.choices[0].message.content
        except Exception as e:
            log.warning("  API error: %s", str(e)[:100])
            result = {
                "key": cand["key"],
                "concept_names": names,
                "model": model_id,
                "model_tag": model_tag,
                "frame": frame,
                "status": "api_error",
                "error": str(e)[:200],
                "timestamp": datetime.now().isoformat(),
            }
            with open(results_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(result) + "\n")
            failed += 1
            time.sleep(2.0)
            continue

        # Extract code (but don't validate or run battery)
        code, extract_status = extract_code(raw_response)

        if code:
            # Apply fixers
            code = _sanitize_unicode(code)
            code = _inject_missing_imports(code)
            code = _fix_common_errors(code)

            # Save the code file
            from hephaestus import safe_filename
            fname = safe_filename(names)
            code_path = output_dir / f"{fname}.py"
            code_path.write_text(code, encoding="utf-8")

        result = {
            "key": cand["key"],
            "concept_names": names,
            "model": model_id,
            "model_tag": model_tag,
            "frame": frame,
            "status": "generated" if code else "no_code",
            "extract_status": extract_status if not code else "ok",
            "code_length": len(code) if code else 0,
            "raw_response_length": len(raw_response) if raw_response else 0,
            "timestamp": datetime.now().isoformat(),
        }
        with open(results_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result) + "\n")

        if code:
            generated += 1
        else:
            failed += 1

        time.sleep(1.0)

    log.info("[%s] Complete: %d generated, %d failed", model_tag, generated, failed)
    return generated, failed


# ---------------------------------------------------------------------------
# Step 3: Score all generated outputs
# ---------------------------------------------------------------------------

def score_all():
    """Run tier battery + novelty on all generated code across all models."""
    from validator import validate
    from test_harness import run_trap_battery, load_tool_from_code

    scored_path = SWEEP_DIR / "scored_matrix.jsonl"

    for model_dir in sorted(SWEEP_DIR.iterdir()):
        if not model_dir.is_dir():
            continue
        tag = model_dir.name

        for py_file in sorted(model_dir.glob("*.py")):
            code = py_file.read_text(encoding="utf-8")

            result = {"model_tag": tag, "file": py_file.name}

            # Validate
            valid, reason = validate(code)
            result["valid"] = valid
            result["validation_reason"] = reason

            if valid:
                try:
                    tool = load_tool_from_code(code)
                    battery = run_trap_battery(tool)
                    result["accuracy"] = battery["accuracy"]
                    result["calibration"] = battery["calibration"]
                    result["passed"] = battery["passed"]
                    result["tier_breakdown"] = battery.get("tier_breakdown", {})
                    result["ncd_accuracy"] = battery.get("ncd_accuracy", 0)
                except Exception as e:
                    result["runtime_error"] = str(e)[:200]

                # Novelty
                try:
                    novelty = _compute_novelty(code)
                    result["novelty_min_ncd"] = novelty["min_ncd"]
                    result["novelty_nearest"] = novelty["nearest"]
                except Exception:
                    pass

            with open(scored_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(result) + "\n")

            log.info("[%s] %s: valid=%s acc=%s",
                     tag, py_file.name[:40],
                     valid,
                     f"{result.get('accuracy', 0):.0%}" if "accuracy" in result else "N/A")


# ---------------------------------------------------------------------------
# Step 4: Summary matrix
# ---------------------------------------------------------------------------

def print_matrix():
    """Print the comparison matrix from scored results."""
    scored_path = SWEEP_DIR / "scored_matrix.jsonl"
    if not scored_path.exists():
        log.error("No scored results. Run --score first.")
        return

    from collections import defaultdict
    import numpy as np

    models = defaultdict(lambda: {
        "total": 0, "valid": 0, "passed_acc": 0, "passed_novelty": 0,
        "accuracies": [], "tier_profiles": [],
        "novelties": [], "api_errors": 0,
    })

    # Also load generation results for api error counts
    for model_dir in sorted(SWEEP_DIR.iterdir()):
        if not model_dir.is_dir():
            continue
        gen_path = model_dir / "results.jsonl"
        if gen_path.exists():
            for line in gen_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        r = json.loads(line)
                        tag = r.get("model_tag", model_dir.name)
                        models[tag]["total"] += 1
                        if r.get("status") == "api_error":
                            models[tag]["api_errors"] += 1
                    except Exception:
                        pass

    for line in scored_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue

        tag = r["model_tag"]
        if r.get("valid"):
            models[tag]["valid"] += 1
        if r.get("passed"):
            models[tag]["passed_acc"] += 1
        if r.get("novelty_min_ncd", 0) > 0.85 and r.get("accuracy", 0) >= 0.20:
            models[tag]["passed_novelty"] += 1
        if "accuracy" in r:
            models[tag]["accuracies"].append(r["accuracy"])
        if "novelty_min_ncd" in r:
            models[tag]["novelties"].append(r["novelty_min_ncd"])
        if r.get("tier_breakdown"):
            models[tag]["tier_profiles"].append(r["tier_breakdown"])

    # Print matrix
    print()
    print("=" * 120)
    print(f"{'Model':<25} {'Gen':>4} {'Valid':>5} {'AccG':>5} {'NovG':>5} "
          f"{'Rate':>6} {'MeanAcc':>8} {'R1':>5} {'R2':>5} {'R3':>5} "
          f"{'R4':>5} {'R5':>5} {'R6':>5} {'MeanNov':>8} {'Errs':>4}")
    print("-" * 120)

    for tag in sorted(models.keys()):
        m = models[tag]
        accs = m["accuracies"]
        novs = m["novelties"]
        total_pass = m["passed_acc"] + m["passed_novelty"]
        rate = total_pass / m["total"] * 100 if m["total"] > 0 else 0

        # Aggregate tier profiles
        tier_means = {}
        for tier in ["R1", "R2", "R3", "R4", "R5", "R6"]:
            vals = [tp.get(tier, {}).get("accuracy", 0) for tp in m["tier_profiles"]
                    if tier in tp]
            tier_means[tier] = np.mean(vals) if vals else 0

        print(f"{tag:<25} {m['total']:>4} {m['valid']:>5} {m['passed_acc']:>5} "
              f"{m['passed_novelty']:>5} {rate:>5.1f}% "
              f"{np.mean(accs)*100:>7.1f}%" if accs else f"{'N/A':>8}"
              f" {tier_means.get('R1',0)*100:>4.0f}%"
              f" {tier_means.get('R2',0)*100:>4.0f}%"
              f" {tier_means.get('R3',0)*100:>4.0f}%"
              f" {tier_means.get('R4',0)*100:>4.0f}%"
              f" {tier_means.get('R5',0)*100:>4.0f}%"
              f" {tier_means.get('R6',0)*100:>4.0f}%"
              f" {np.mean(novs):>7.3f}" if novs else f"{'N/A':>8}"
              f" {m['api_errors']:>4}")

    print("=" * 120)
    print()
    print("Gen=generated, Valid=passed syntax+imports+interface+runtime,")
    print("AccG=passed accuracy gate, NovG=passed novelty gate,")
    print("Rate=total forge rate, MeanAcc=mean accuracy of valid tools,")
    print("R1-R6=mean tier accuracy, MeanNov=mean source novelty NCD, Errs=API errors")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Model sweep for forge comparison")
    parser.add_argument("--generate", action="store_true",
                        help="Generate from all (or specified) models")
    parser.add_argument("--model", type=str, default=None,
                        help="Generate from one specific model ID")
    parser.add_argument("--score", action="store_true",
                        help="Score all generated outputs through full battery")
    parser.add_argument("--matrix", action="store_true",
                        help="Print comparison matrix from scored results")
    parser.add_argument("--freeze", action="store_true",
                        help="Freeze 100 candidates (auto-runs if not frozen)")
    parser.add_argument("--max", type=int, default=100,
                        help="Max candidates per model (default 100)")
    args = parser.parse_args()

    if args.freeze or args.generate:
        candidates = freeze_candidates(n=args.max)

    if args.generate:
        if args.model:
            # Find model in MODELS list or use raw ID
            tag = args.model.split("/")[-1][:30]
            for m in MODELS:
                if m["id"] == args.model:
                    tag = m["tag"]
                    break
            generate_from_model(args.model, tag, candidates, max_items=args.max)
        else:
            # Run all models
            for m in MODELS:
                log.info("=" * 60)
                log.info("Starting model: %s (%s)", m["tag"], m["id"])
                log.info("=" * 60)
                try:
                    generate_from_model(m["id"], m["tag"], candidates,
                                        max_items=args.max)
                except Exception as e:
                    log.error("Model %s failed: %s", m["tag"], e)
                time.sleep(5.0)

    if args.score:
        score_all()

    if args.matrix:
        print_matrix()


if __name__ == "__main__":
    main()
