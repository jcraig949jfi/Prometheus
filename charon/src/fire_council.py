"""
Fire Council Prompts to All Titan APIs
=======================================
Sends the battery results prompt to ChatGPT, Claude, Gemini, and DeepSeek.
Saves responses to charon/reports/council_responses/.
"""

import os
import time
import threading
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent
REPORT_DIR = ROOT / "reports" / "council_responses"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Keys -- loaded from DeepseekKey.txt (line 1=label, line 2=key, etc.)
_keyfile = (ROOT.parent / "DeepseekKey.txt").read_text(encoding="utf-8").strip().split("\n")
_keys = {}
_current_label = None
for line in _keyfile:
    line = line.strip()
    if not line:
        continue
    if line.lower().startswith("deepseek"):
        _current_label = "deepseek"
    elif line.lower().startswith("openai"):
        _current_label = "openai"
    elif line.lower().startswith("claude"):
        _current_label = "claude"
    elif line.lower().startswith("gemini"):
        _current_label = "gemini"
    elif _current_label and line.startswith(("sk-", "AIza")):
        _keys[_current_label] = line
        _current_label = None

DEEPSEEK_KEY = _keys.get("deepseek", "")
OPENAI_KEY = _keys.get("openai", "")
CLAUDE_KEY = _keys.get("claude", "")
GOOGLE_KEY = _keys.get("gemini", "")

# Prompt -- battery results
PROMPT = (ROOT / "docs" / "council_prompt_battery_results.md").read_text(encoding="utf-8")

SYSTEM_MSG = ("You are a world-class mathematician and hostile scientific reviewer "
              "specializing in analytic number theory, random matrix theory, and L-functions. "
              "You have deep expertise in the Birch and Swinnerton-Dyer conjecture, Katz-Sarnak "
              "philosophy, and the Iwaniec-Luo-Sarnak test function support theorem. "
              "Respond with extreme rigor. Do not flatter. Attack every claim.")

TODAY = str(date.today())


def call_openai(prompt_text, output_file, label, model="gpt-4.1"):
    """Send prompt via OpenAI API."""
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

        out = f"# {label} Council Response -- Battery Results\n"
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
    """Send prompt via Anthropic API."""
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

        out = f"# Claude Council Response -- Battery Results\n"
        out += f"## Model: {model} | Time: {elapsed:.0f}s\n"
        out += f"## Tokens: {usage.input_tokens} in / {usage.output_tokens} out\n"
        out += f"\n## Response\n\n{content}\n"

        output_file.write_text(out, encoding="utf-8")
        print(f"[Claude] Done in {elapsed:.0f}s. Saved to {output_file.name}")
    except Exception as e:
        elapsed = time.time() - t0
        output_file.write_text(f"# Claude FAILED after {elapsed:.0f}s\n\nError: {e}\n", encoding="utf-8")
        print(f"[Claude] FAILED: {e}")


def call_gemini(prompt_text, output_file, model="gemini-2.5-flash"):
    """Send prompt via Google Gemini API."""
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

        out = f"# Gemini Council Response -- Battery Results\n"
        out += f"## Model: {model} | Time: {elapsed:.0f}s\n"
        out += f"\n## Response\n\n{content}\n"

        output_file.write_text(out, encoding="utf-8")
        print(f"[Gemini] Done in {elapsed:.0f}s. Saved to {output_file.name}")
    except Exception as e:
        elapsed = time.time() - t0
        output_file.write_text(f"# Gemini FAILED after {elapsed:.0f}s\n\nError: {e}\n", encoding="utf-8")
        print(f"[Gemini] FAILED: {e}")


def call_deepseek(prompt_text, output_file, model="deepseek-reasoner"):
    """Send prompt via DeepSeek API (OpenAI-compatible)."""
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
            max_tokens=16384,
        )
        elapsed = time.time() - t0
        content = response.choices[0].message.content
        usage = response.usage

        out = f"# DeepSeek Council Response -- Battery Results\n"
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


def main():
    print(f"Firing council prompts -- Battery Results to ChatGPT, Claude, Gemini, DeepSeek")
    print(f"  Prompt length: {len(PROMPT)} chars")
    print(f"  Date: {TODAY}")
    print()

    targets = [
        ("ChatGPT", lambda: call_openai(
            PROMPT,
            REPORT_DIR / f"chatgpt_battery_results_{TODAY}.md",
            "ChatGPT", "gpt-4.1")),
        ("Claude", lambda: call_claude(
            PROMPT,
            REPORT_DIR / f"claude_battery_results_{TODAY}.md")),
        ("Gemini", lambda: call_gemini(
            PROMPT,
            REPORT_DIR / f"gemini_battery_results_{TODAY}.md")),
        ("DeepSeek", lambda: call_deepseek(
            PROMPT,
            REPORT_DIR / f"deepseek_battery_results_{TODAY}.md")),
    ]

    threads = []
    for name, fn in targets:
        t = threading.Thread(target=fn, name=name)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"\n=== COMPLETE ===")
    for f in sorted(REPORT_DIR.glob(f"*_{TODAY}.md")):
        print(f"  {f.name} ({f.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
