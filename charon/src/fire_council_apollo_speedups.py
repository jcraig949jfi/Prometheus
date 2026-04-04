"""
Fire Council Prompts — Apollo Speedups & Plateau Avoidance
==========================================================
Sends tactical Apollo questions to ChatGPT, Claude, DeepSeek, and Gemini.
Saves responses to charon/reports/council_responses/.

Usage:
    python charon/src/fire_council_apollo_speedups.py
"""

import os
import time
import threading
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
REPORT_DIR = ROOT / "reports" / "council_responses"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Keys
_keyfile = (ROOT.parent / "DeepseekKey.txt").read_text(encoding="utf-8").strip().split("\n")
DEEPSEEK_KEY = _keyfile[1].strip()
OPENAI_KEY = _keyfile[4].strip()
CLAUDE_KEY = _keyfile[7].strip()
GOOGLE_KEY = "AIzaSyBODkkNkxm1Xmghk5XR_L7Wb9jS9JnTWvE"

# Prompt
PROMPT = (ROOT / "docs" / "council_prompt_apollo_speedups.md").read_text(encoding="utf-8")

TODAY = datetime.now().strftime("%Y-%m-%d")

SYSTEM_MSG = (
    "You are a world-class expert in evolutionary computation, genetic programming, "
    "program synthesis, and multi-objective optimization. You have deep knowledge of "
    "LLM-guided code generation, quality-diversity algorithms (MAP-Elites, novelty search), "
    "and practical GP systems. You also track the latest AutoML and neural architecture search "
    "literature. Respond with extreme specificity — name papers, authors, venues, library "
    "versions, and GitHub repos. Be practical and actionable. Do not pad your response."
)


def call_openai(prompt_text, output_file, label, model="gpt-4.1"):
    from openai import OpenAI
    print(f"[{label}] Starting request ({model})...")
    t0 = time.time()
    try:
        client = OpenAI(api_key=OPENAI_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=16384,
        )
        elapsed = time.time() - t0
        content = response.choices[0].message.content
        usage = response.usage

        out = f"# {label} Council Response — Apollo Speedups\n"
        out += f"## Model: {model} | Time: {elapsed:.0f}s\n"
        if usage:
            out += f"## Tokens: {usage.prompt_tokens} in / {usage.completion_tokens} out / {usage.total_tokens} total\n"
        out += f"\n## Response\n\n{content}\n"

        output_file.write_text(out, encoding="utf-8")
        print(f"[{label}] Done in {elapsed:.0f}s. Saved to {output_file.name}")
    except Exception as e:
        elapsed = time.time() - t0
        output_file.write_text(f"# {label} FAILED after {elapsed:.0f}s\n\nError: {e}\n", encoding="utf-8")
        print(f"[{label}] FAILED: {e}")


def call_claude(prompt_text, output_file, model="claude-sonnet-4-20250514"):
    import anthropic
    print(f"[Claude] Starting request ({model})...")
    t0 = time.time()
    try:
        client = anthropic.Anthropic(api_key=CLAUDE_KEY)
        response = client.messages.create(
            model=model,
            max_tokens=16384,
            system=SYSTEM_MSG,
            messages=[{"role": "user", "content": prompt_text}],
        )
        elapsed = time.time() - t0
        content = response.content[0].text
        usage = response.usage

        out = f"# Claude Council Response — Apollo Speedups\n"
        out += f"## Model: {model} | Time: {elapsed:.0f}s\n"
        out += f"## Tokens: {usage.input_tokens} in / {usage.output_tokens} out\n"
        out += f"\n## Response\n\n{content}\n"

        output_file.write_text(out, encoding="utf-8")
        print(f"[Claude] Done in {elapsed:.0f}s. Saved to {output_file.name}")
    except Exception as e:
        elapsed = time.time() - t0
        output_file.write_text(f"# Claude FAILED after {elapsed:.0f}s\n\nError: {e}\n", encoding="utf-8")
        print(f"[Claude] FAILED: {e}")


def call_deepseek(prompt_text, output_file, model="deepseek-chat"):
    from openai import OpenAI
    print(f"[DeepSeek] Starting request ({model})...")
    t0 = time.time()
    try:
        client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=8192,
        )
        elapsed = time.time() - t0
        content = response.choices[0].message.content
        usage = response.usage

        out = f"# DeepSeek Council Response — Apollo Speedups\n"
        out += f"## Model: {model} | Time: {elapsed:.0f}s\n"
        if usage:
            out += f"## Tokens: {usage.prompt_tokens} in / {usage.completion_tokens} out / {usage.total_tokens} total\n"
        out += f"\n## Response\n\n{content}\n"

        output_file.write_text(out, encoding="utf-8")
        print(f"[DeepSeek] Done in {elapsed:.0f}s. Saved to {output_file.name}")
    except Exception as e:
        elapsed = time.time() - t0
        output_file.write_text(f"# DeepSeek FAILED after {elapsed:.0f}s\n\nError: {e}\n", encoding="utf-8")
        print(f"[DeepSeek] FAILED: {e}")


def call_gemini(prompt_text, output_file, model="gemini-2.5-flash"):
    from google import genai
    print(f"[Gemini] Starting request ({model})...")
    t0 = time.time()
    try:
        client = genai.Client(api_key=GOOGLE_KEY)
        response = client.models.generate_content(
            model=model,
            contents=prompt_text,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_MSG,
                max_output_tokens=16384,
                temperature=0.2,
            ),
        )
        elapsed = time.time() - t0
        content = response.text

        out = f"# Gemini Council Response — Apollo Speedups\n"
        out += f"## Model: {model} | Time: {elapsed:.0f}s\n"
        out += f"\n## Response\n\n{content}\n"

        output_file.write_text(out, encoding="utf-8")
        print(f"[Gemini] Done in {elapsed:.0f}s. Saved to {output_file.name}")
    except Exception as e:
        elapsed = time.time() - t0
        output_file.write_text(f"# Gemini FAILED after {elapsed:.0f}s\n\nError: {e}\n", encoding="utf-8")
        print(f"[Gemini] FAILED: {e}")


def main():
    print("=== Firing Council — Apollo Speedups & Plateau Avoidance ===")
    print(f"  Prompt length: {len(PROMPT)} chars")
    print(f"  Date: {TODAY}")
    print(f"  Targets: ChatGPT, Claude, DeepSeek, Gemini")
    print()

    targets = [
        ("ChatGPT", lambda: call_openai(
            PROMPT,
            REPORT_DIR / f"chatgpt_apollo_speedups_{TODAY}.md",
            "ChatGPT", "gpt-4.1")),
        ("Claude", lambda: call_claude(
            PROMPT,
            REPORT_DIR / f"claude_apollo_speedups_{TODAY}.md")),
        ("DeepSeek", lambda: call_deepseek(
            PROMPT,
            REPORT_DIR / f"deepseek_apollo_speedups_{TODAY}.md")),
        ("Gemini", lambda: call_gemini(
            PROMPT,
            REPORT_DIR / f"gemini_apollo_speedups_{TODAY}.md")),
    ]

    threads = []
    for name, fn in targets:
        t = threading.Thread(target=fn, name=name)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"\n=== COMPLETE ===")
    for f in sorted(REPORT_DIR.glob(f"*apollo_speedups_{TODAY}.md")):
        print(f"  {f.name} ({f.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
