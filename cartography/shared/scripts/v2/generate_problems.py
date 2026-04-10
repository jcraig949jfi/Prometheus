#!/usr/bin/env python3
"""
Problem Generator Pipeline
===========================
Calls frontier models (OpenAI, Gemini, DeepSeek) to generate computational
mathematics problems calibrated to the Charon instrument's current boundary.

Usage:
    python generate_problems.py [--provider openai|gemini|deepseek|all]
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from keys import get_key

PROMPT_FILE = Path(__file__).parent / "problem_generator_prompt_compact.md"
OUT_DIR = Path(__file__).parent / "generated_problems"
OUT_DIR.mkdir(exist_ok=True)

# Load the calibrated prompt
with open(PROMPT_FILE) as f:
    system_prompt = f.read()


def call_openai(prompt, model="gpt-4o"):
    """Call OpenAI API."""
    import openai
    client = openai.OpenAI(api_key=get_key("OPENAI"))
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a research mathematician designing computational experiments."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.8,
    )
    return resp.choices[0].message.content


def call_gemini(prompt):
    """Call Gemini API."""
    import google.generativeai as genai
    genai.configure(api_key=get_key("GEMINI"))
    model = genai.GenerativeModel("gemini-2.0-flash")
    resp = model.generate_content(prompt)
    return resp.text


def call_deepseek(prompt):
    """Call DeepSeek API."""
    import openai
    client = openai.OpenAI(
        api_key=get_key("DEEPSEEK"),
        base_url="https://api.deepseek.com"
    )
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a research mathematician designing computational experiments."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.8,
    )
    return resp.choices[0].message.content


PROVIDERS = {
    "openai": call_openai,
    "gemini": call_gemini,
    "deepseek": call_deepseek,
}


def generate(provider="all"):
    """Generate problems from one or all providers."""
    targets = list(PROVIDERS.keys()) if provider == "all" else [provider]

    results = {}
    for name in targets:
        if name not in PROVIDERS:
            print(f"  Unknown provider: {name}")
            continue

        fn = PROVIDERS[name]
        print(f"\n{'='*60}")
        print(f"  Calling {name}...")
        print(f"{'='*60}")

        try:
            response = fn(system_prompt)
            results[name] = response

            # Save individual response
            out_file = OUT_DIR / f"problems_{name}_{time.strftime('%Y%m%d_%H%M%S')}.md"
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(f"# Generated Problems from {name}\n")
                f.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(response)

            print(f"  Saved to {out_file.name}")
            print(f"  Response length: {len(response)} chars")

        except Exception as e:
            print(f"  ERROR: {e}")
            results[name] = f"ERROR: {e}"

        # Rate limit courtesy
        time.sleep(2)

    # Save combined results
    combined = OUT_DIR / f"all_problems_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(combined, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Combined results saved to {combined.name}")
    print(f"  Providers called: {len(results)}")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="all", choices=["openai", "gemini", "deepseek", "all"])
    args = parser.parse_args()
    generate(args.provider)
