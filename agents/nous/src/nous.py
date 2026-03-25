#!/usr/bin/env python3
"""
Nous — Combinatorial Hypothesis Engine

Generates novel hypotheses by combining concepts from diverse fields,
evaluating each triple via NVIDIA's free API, scoring, and ranking.
"""

import argparse
import itertools
import json
import logging
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from concepts import CONCEPTS
from scorer import score_response

NOUS_ROOT = Path(__file__).resolve().parent.parent
log_file = NOUS_ROOT / "nous.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NOUS] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_file), encoding="utf-8"),
    ],
)
log = logging.getLogger("nous")

PROMPT_TEMPLATE = """\
You are a computational engineer designing reasoning evaluation tools.

Three concepts: {c1_name}, {c2_name}, {c3_name}

Descriptions:
- {c1_name}: {c1_desc}
- {c2_name}: {c2_desc}
- {c3_name}: {c3_desc}

A reasoning evaluation tool is a Python class that takes a prompt and candidate \
answers, then scores them using only numpy and the standard library. No neural models, \
no API calls — pure algorithmic reasoning.

In 200-400 words, answer:
1. What specific algorithm emerges from combining these three concepts that could \
score candidate answers to reasoning questions? Describe the data structures, \
operations, and scoring logic — not metaphors.
2. What structural features of text would this approach parse? (e.g., negations, \
comparatives, conditionals, numeric values, causal claims, ordering relations)
3. Is this combination novel, or does it map to existing work?
4. Rate the potential (1-10) for each dimension below.

The tools that succeed in our pipeline use structural parsing (regex extraction of \
logical relationships), constraint propagation (transitivity, modus ponens), and \
numeric evaluation. Tools that rely on hash similarity or bag-of-words fail. \
Be concrete about the algorithm, not the theory.

End your response with exactly these four rating lines (fill in the number and a short justification):
Reasoning: <N>/10 — <why>
Metacognition: <N>/10 — <why>
Hypothesis generation: <N>/10 — <why>
Implementability: <N>/10 — <why>"""


def load_concepts(concept_file: str | None) -> list[dict]:
    """Load concepts from custom file or use built-in dictionary."""
    if concept_file:
        path = Path(concept_file)
        if not path.exists():
            log.error(f"Concept file not found: {concept_file}")
            sys.exit(1)
        with open(path) as f:
            concepts = json.load(f)
        log.info(f"Loaded {len(concepts)} concepts from {concept_file}")
        return concepts
    log.info(f"Using built-in concept dictionary: {len(CONCEPTS)} concepts")
    return CONCEPTS


def _load_coeus_weights(concepts: list[dict]) -> list[float]:
    """Load Coeus concept scores to bias sampling toward forge-productive concepts.

    Returns a weight per concept index. Higher = more likely to be sampled.
    Concepts with 0% forge rate get downweighted (not eliminated — they might
    work in new combinations).
    """
    coeus_path = Path(__file__).resolve().parent.parent.parent / "coeus" / "graphs" / "concept_scores.json"
    if not coeus_path.exists():
        return [1.0] * len(concepts)

    try:
        data = json.loads(coeus_path.read_text(encoding="utf-8"))
        influence = data.get("concept_influence", {})
        adv_survival = data.get("adversarial_survival", {})
        goodhart = data.get("goodhart_indicators", {})

        weights = []
        n_boosted = 0
        n_suppressed = 0
        n_goodhart_adjusted = 0

        for c in concepts:
            name = c["name"]
            info = influence.get(name, {})
            forge_eff = info.get("forge_effect", 0)
            adv_data = adv_survival.get(name, {})
            adv_rate = adv_data.get("survival_rate")

            # Base weight from forge effect
            if forge_eff > 0.3:
                w = 3.0
            elif forge_eff > 0.05:
                w = 2.0
            elif forge_eff < -0.2:
                w = 0.3
            else:
                w = 1.0

            # Adjust for adversarial survival (if data available)
            if adv_rate is not None:
                if name in goodhart and "warning" in goodhart[name]:
                    # Goodhart indicator: demote despite forge success
                    w = max(w * 0.5, 0.5)
                    n_goodhart_adjusted += 1
                elif adv_rate > 0.6 and forge_eff < 0.1:
                    # Undervalued: high adversarial but low forge priority — boost
                    w = max(w, 2.5)

            if w > 1.5:
                n_boosted += 1
            elif w < 0.5:
                n_suppressed += 1
            weights.append(w)

        log.info("Coeus sampling weights: %d boosted, %d suppressed, %d Goodhart-adjusted",
                 n_boosted, n_suppressed, n_goodhart_adjusted)
        return weights

    except Exception as e:
        log.warning("Failed to load Coeus weights: %s", e)
        return [1.0] * len(concepts)


def generate_combinations(
    concepts: list[dict],
    n_combos: int,
    cross_field_bias: float = 0.8,
    seed: int | None = None,
    use_coeus_weights: bool = True,
) -> list[tuple[int, int, int]]:
    """
    Generate random concept triple indices, biased toward cross-field combinations.

    cross_field_bias: probability of requiring at least 2 different fields per triple.
    use_coeus_weights: if True, bias sampling toward concepts with positive forge effects.
    """
    if seed is not None:
        random.seed(seed)

    n = len(concepts)
    all_indices = list(range(n))
    combos = set()

    # Load Coeus weights for forge-aware sampling
    weights = _load_coeus_weights(concepts) if use_coeus_weights else [1.0] * n
    total_weight = sum(weights)
    probs = [w / total_weight for w in weights]

    # Pre-group by field for cross-field sampling
    field_groups = {}
    for i, c in enumerate(concepts):
        field_groups.setdefault(c["field"], []).append(i)
    fields = list(field_groups.keys())

    # Per-field weighted sampling helper
    field_weights = {}
    for field, indices in field_groups.items():
        fw = [weights[i] for i in indices]
        fw_total = sum(fw)
        field_weights[field] = [w / fw_total for w in fw] if fw_total > 0 else None

    attempts = 0
    max_attempts = n_combos * 20

    def _weighted_choice(indices, field=None):
        """Pick one index, weighted by Coeus forge scores."""
        if field and field in field_weights and field_weights[field] is not None:
            return random.choices(field_groups[field],
                                  weights=field_weights[field], k=1)[0]
        return random.choices(indices, weights=[weights[i] for i in indices], k=1)[0]

    while len(combos) < n_combos and attempts < max_attempts:
        attempts += 1

        if random.random() < cross_field_bias and len(fields) >= 2:
            # Pick 2-3 different fields, then one concept from each
            n_fields = random.choice([2, 3])
            chosen_fields = random.sample(fields, min(n_fields, len(fields)))

            selected = []
            for f in chosen_fields:
                selected.append(_weighted_choice(field_groups[f], field=f))

            # Fill remaining slots from any field (weighted)
            while len(selected) < 3:
                idx = _weighted_choice(all_indices)
                if idx not in selected:
                    selected.append(idx)
        else:
            selected = random.choices(all_indices, weights=weights, k=3)

        triple = tuple(sorted(selected))
        if len(set(triple)) == 3:
            combos.add(triple)

    result = sorted(combos)
    log.info(
        f"Generated {len(result)} combinations "
        f"(requested {n_combos}, cross-field bias {cross_field_bias})"
    )

    # Report cross-field stats
    cross_count = sum(
        1
        for a, b, c in result
        if len({concepts[a]["field"], concepts[b]["field"], concepts[c]["field"]}) >= 2
    )
    log.info(f"Cross-field combinations: {cross_count}/{len(result)} ({100*cross_count/max(len(result),1):.0f}%)")

    return result


def build_prompt(concepts: list[dict], triple: tuple[int, int, int]) -> str:
    """Build the evaluation prompt for a concept triple."""
    c1, c2, c3 = [concepts[i] for i in triple]
    return PROMPT_TEMPLATE.format(
        c1_name=c1["name"], c1_desc=c1["short_description"],
        c2_name=c2["name"], c2_desc=c2["short_description"],
        c3_name=c3["name"], c3_desc=c3["short_description"],
    )


def call_api(
    client: OpenAI,
    prompt: str,
    model: str,
    max_retries: int = 5,
    backoff_base: float = 2.0,
) -> str | None:
    """Call the NVIDIA API with exponential backoff on rate limits."""
    for attempt in range(max_retries):
        try:
            log.info(f"  API call (attempt {attempt+1})...")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                wait = backoff_base ** (attempt + 1)
                log.warning(f"Rate limited (attempt {attempt+1}), backing off {wait:.0f}s")
                time.sleep(wait)
            elif "500" in error_str or "502" in error_str or "503" in error_str:
                wait = backoff_base ** attempt
                log.warning(f"Server error (attempt {attempt+1}), retrying in {wait:.0f}s: {error_str[:100]}")
                time.sleep(wait)
            else:
                log.error(f"API error: {error_str[:200]}")
                return None

    log.error(f"Failed after {max_retries} retries")
    return None


def load_checkpoint(run_dir: Path) -> set[tuple[int, int, int]]:
    """Load already-processed triples from checkpoint."""
    checkpoint_path = run_dir / "checkpoint.json"
    if not checkpoint_path.exists():
        return set()
    with open(checkpoint_path) as f:
        data = json.load(f)
    processed = {tuple(t) for t in data.get("processed", [])}
    log.info(f"Resumed: {len(processed)} combinations already processed")
    return processed


def save_checkpoint(run_dir: Path, processed: set[tuple[int, int, int]]):
    """Save checkpoint of processed triples."""
    checkpoint_path = run_dir / "checkpoint.json"
    with open(checkpoint_path, "w") as f:
        json.dump({"processed": [list(t) for t in sorted(processed)]}, f)


def save_response(run_dir: Path, entry: dict):
    """Append a single response to the JSONL file."""
    with open(run_dir / "responses.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_all_responses(run_dir: Path) -> list[dict]:
    """Load all responses from JSONL."""
    path = run_dir / "responses.jsonl"
    if not path.exists():
        return []
    results = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def generate_rankings(run_dir: Path, concepts: list[dict], top_n: int = 50, top_full: int = 20):
    """Generate rankings.md from all responses."""
    responses = load_all_responses(run_dir)
    if not responses:
        log.warning("No responses to rank")
        return

    # Sort by composite score descending
    ranked = sorted(responses, key=lambda x: x.get("score", {}).get("composite_score", 0), reverse=True)

    lines = [
        f"# Nous Rankings",
        f"",
        f"**Run**: {run_dir.name}",
        f"**Total combinations evaluated**: {len(ranked)}",
        f"**High potential**: {sum(1 for r in ranked if r.get('score', {}).get('high_potential', False))}",
        f"",
        f"---",
        f"",
        f"## Top {min(top_n, len(ranked))} Combinations",
        f"",
        f"| Rank | Concepts | Composite | R | M | H | I | Novelty | HP |",
        f"|------|----------|-----------|---|---|---|---|---------|----|",
    ]

    for i, entry in enumerate(ranked[:top_n]):
        s = entry.get("score", {})
        r = s.get("ratings", {})
        concepts_str = " + ".join(entry.get("concept_names", []))
        hp = "**YES**" if s.get("high_potential") else ""
        lines.append(
            f"| {i+1} | {concepts_str} | {s.get('composite_score', 0):.1f} "
            f"| {r.get('reasoning', '-')} | {r.get('metacognition', '-')} "
            f"| {r.get('hypothesis_generation', '-')} | {r.get('implementability', '-')} "
            f"| {s.get('novelty', '?')} | {hp} |"
        )

    lines.extend(["", "---", "", f"## Top {min(top_full, len(ranked))} — Full Responses", ""])

    for i, entry in enumerate(ranked[:top_full]):
        s = entry.get("score", {})
        concepts_str = " + ".join(entry.get("concept_names", []))
        lines.extend([
            f"### #{i+1}: {concepts_str}",
            f"",
            f"**Composite**: {s.get('composite_score', 0):.1f} | "
            f"**Novelty**: {s.get('novelty', '?')} | "
            f"**High Potential**: {'Yes' if s.get('high_potential') else 'No'}",
            f"",
            f"**Fields**: {', '.join(entry.get('concept_fields', []))}",
            f"",
            f"```",
            entry.get("response_text", "(no response)"),
            f"```",
            f"",
            f"---",
            f"",
        ])

    with open(run_dir / "rankings.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    log.info(f"Rankings written to {run_dir / 'rankings.md'}")


def find_latest_run(runs_dir: Path) -> Path | None:
    """Find the most recent run directory."""
    if not runs_dir.exists():
        return None
    dirs = sorted(runs_dir.iterdir(), reverse=True)
    for d in dirs:
        if d.is_dir() and (d / "checkpoint.json").exists():
            return d
    return None


def main():
    parser = argparse.ArgumentParser(description="Nous — Combinatorial Hypothesis Engine")
    parser.add_argument("--n-combos", type=int, default=500, help="Number of combinations per batch (ignored with --unlimited)")
    parser.add_argument("--unlimited", action="store_true", help="Run indefinitely, sampling new batches until Ctrl+C")
    parser.add_argument("--model", type=str, default=os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b"), help="NVIDIA model to use")
    parser.add_argument("--concept-file", type=str, default=None, help="Custom concept file (JSON)")
    parser.add_argument("--resume", action="store_true", help="Resume the most recent interrupted run")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between API calls")
    parser.add_argument("--cross-field-bias", type=float, default=0.8, help="Bias toward cross-field triples (0-1)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()

    # Resolve paths relative to the agent root
    runs_dir = NOUS_ROOT / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    # API key
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        log.error("NVIDIA_API_KEY environment variable not set")
        sys.exit(1)

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
        timeout=60.0,
    )

    # Load concepts
    concepts = load_concepts(args.concept_file)

    # Setup run directory
    if args.resume:
        run_dir = find_latest_run(runs_dir)
        if run_dir is None:
            log.error("No previous run found to resume")
            sys.exit(1)
        log.info(f"Resuming run: {run_dir.name}")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = runs_dir / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"New run: {run_dir.name}")

    # Load checkpoint if resuming
    processed = load_checkpoint(run_dir) if args.resume else set()

    # Save meta
    combo_meta = {
        "n_concepts": len(concepts),
        "model": args.model,
        "cross_field_bias": args.cross_field_bias,
        "unlimited": args.unlimited,
    }
    with open(run_dir / "meta.json", "w") as f:
        json.dump(combo_meta, f, indent=2)

    # Process loop — runs once for finite, forever for unlimited
    completed = 0
    batch = 0
    shutdown = False

    def handle_sigint(sig, frame):
        nonlocal shutdown
        log.info("Ctrl+C received — finishing current request and shutting down...")
        shutdown = True

    import signal
    signal.signal(signal.SIGINT, handle_sigint)

    try:
        while not shutdown:
            batch += 1
            batch_size = args.n_combos

            combos = generate_combinations(
                concepts, batch_size,
                cross_field_bias=args.cross_field_bias,
                seed=args.seed if batch == 1 else None,
            )

            # Filter out already-processed
            remaining = [c for c in combos if c not in processed]

            if not remaining:
                if args.unlimited:
                    log.info(f"Batch {batch}: all {len(combos)} combos already seen, sampling fresh...")
                    continue
                else:
                    log.info("All combinations already processed.")
                    break

            log.info(f"Batch {batch}: {len(remaining)} new combinations to process")

            for i, triple in enumerate(remaining):
                if shutdown:
                    break

                c1, c2, c3 = [concepts[idx] for idx in triple]
                concept_names = [c1["name"], c2["name"], c3["name"]]
                concept_fields = [c1["field"], c2["field"], c3["field"]]

                log.info(
                    f"[{completed+1} total] "
                    f"{concept_names[0]} x {concept_names[1]} x {concept_names[2]}"
                )

                prompt = build_prompt(concepts, triple)
                response_text = call_api(client, prompt, args.model)

                if response_text is None:
                    log.warning(f"Skipping failed combination: {concept_names}")
                    continue

                score = score_response(response_text)

                entry = {
                    "triple": list(triple),
                    "concept_names": concept_names,
                    "concept_fields": concept_fields,
                    "response_text": response_text,
                    "score": score,
                    "model": args.model,
                    "timestamp": datetime.now().isoformat(),
                }

                save_response(run_dir, entry)
                processed.add(triple)
                completed += 1

                if score["high_potential"]:
                    log.info(
                        f"  *** HIGH POTENTIAL *** composite={score['composite_score']:.1f} "
                        f"novelty={score['novelty']}"
                    )
                else:
                    log.info(
                        f"  composite={score['composite_score']:.1f} novelty={score['novelty']}"
                    )

                # Checkpoint every 10
                if completed % 10 == 0:
                    save_checkpoint(run_dir, processed)
                    log.info(f"  Checkpoint saved ({completed} done)")

                # Rate limit
                time.sleep(args.delay)

            # End of batch
            if not args.unlimited:
                break

    except Exception as e:
        log.error(f"Unexpected error: {e}")

    # Final save
    save_checkpoint(run_dir, processed)
    log.info(f"Completed {completed} combinations total ({len(processed)} unique in run)")

    # Generate rankings
    generate_rankings(run_dir, concepts)
    log.info("Done.")


if __name__ == "__main__":
    main()
