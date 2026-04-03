"""Generate candidate tools via DeepSeek V3.2 for a specific category.

Usage: python forge/generate_candidates.py --tier 2 --category simpson_paradox --count 20
"""
import sys, os, json, random, time, argparse, traceback
os.environ['PYTHONIOENCODING'] = 'utf-8'
from pathlib import Path
from datetime import datetime
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from forge.builder import generate_tool_prompt, save_candidate, SCIENCE_FIELDS
from forge.llm_client import generate_tool


def generate_candidates(tier, category, count, base_seed=42):
    """Generate `count` candidate tools for a category via DeepSeek V3.2."""
    successes = 0
    failures = 0
    results = []

    for i in range(count):
        seed = base_seed + i
        rng = random.Random(seed)
        tool_id = f"t{tier}_{category}_{i:03d}"

        print(f"\n[{i+1}/{count}] Generating {tool_id} (seed={seed})...")

        try:
            # Generate the Builder prompt (no battery content)
            prompt, fields = generate_tool_prompt(tier, category, rng)
            print(f"  Science field(s): {fields}")

            # Call DeepSeek V3.2
            result = generate_tool(
                system_prompt=prompt,
                temperature=0.7,
                max_tokens=4096,
            )

            code = result["code"]
            usage = result.get("usage", {})
            print(f"  Tokens: {usage.get('prompt_tokens', '?')} in, "
                  f"{usage.get('completion_tokens', '?')} out")

            if "class ReasoningTool" not in code:
                print(f"  SKIP: No ReasoningTool class in response")
                failures += 1
                # Save raw for debugging
                debug_path = Path(f"forge/candidates/{tool_id}_FAILED.txt")
                debug_path.write_text(result["raw"], encoding='utf-8')
                continue

            # Save candidate
            tool_path = save_candidate(
                tool_code=code,
                tool_id=tool_id,
                tier=tier,
                category=category,
                fields=fields,
                trace_md=f"# Reasoning Trace: {tool_id}\n\n"
                         f"Science field(s): {', '.join(fields)}\n"
                         f"Category: {category}\n"
                         f"Generated: {datetime.now().isoformat()}\n"
                         f"Model: {result.get('model', 'deepseek/deepseek-v3.2')}\n",
            )

            successes += 1
            results.append({
                "tool_id": tool_id,
                "path": tool_path,
                "fields": fields,
                "tokens_in": usage.get("prompt_tokens", 0),
                "tokens_out": usage.get("completion_tokens", 0),
            })

            # Rate limit: wait between calls
            if i < count - 1:
                time.sleep(1)

        except Exception as e:
            print(f"  ERROR: {e}")
            traceback.print_exc()
            failures += 1
            time.sleep(2)

    print(f"\n{'='*50}")
    print(f"Generation complete: {successes} successes, {failures} failures")
    print(f"Candidates saved to forge/candidates/")

    # Save generation summary
    summary = {
        "tier": tier,
        "category": category,
        "count_requested": count,
        "successes": successes,
        "failures": failures,
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }
    summary_path = Path(f"forge/candidates/generation_summary_{category}.json")
    summary_path.write_text(json.dumps(summary, indent=2))

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate candidate tools via DeepSeek V3.2")
    parser.add_argument("--tier", type=int, required=True)
    parser.add_argument("--category", type=str, required=True)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    generate_candidates(args.tier, args.category, args.count, args.seed)
