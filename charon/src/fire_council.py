"""
Fire Council Prompts to All Titan APIs
=======================================
Sends the residual signal prompt to ChatGPT, Claude, and Gemini.
(DeepSeek already returned — see deepseek_residual_signal_2026-04-03.md)
Saves responses to charon/reports/council_responses/.
"""

import os
import time
import threading
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPORT_DIR = ROOT / "reports" / "council_responses"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Keys — parsed from DeepseekKey.txt
_keyfile = (ROOT.parent / "DeepseekKey.txt").read_text(encoding="utf-8").strip().split("\n")
DEEPSEEK_KEY = _keyfile[1].strip()
OPENAI_KEY = _keyfile[4].strip()
CLAUDE_KEY = _keyfile[7].strip()
GOOGLE_KEY = "AIzaSyBODkkNkxm1Xmghk5XR_L7Wb9jS9JnTWvE"

# Prompts
RESIDUAL_PROMPT = (ROOT / "docs" / "council_prompt_residual_signal.md").read_text(encoding="utf-8")
LITERATURE_PROMPT = (ROOT / "docs" / "council_prompt_literature_search.md").read_text(encoding="utf-8")

SYSTEM_MSG = ("You are a world-class mathematician and hostile scientific reviewer "
              "specializing in analytic number theory, random matrix theory, and L-functions. "
              "You have deep expertise in the Birch and Swinnerton-Dyer conjecture, Katz-Sarnak "
              "philosophy, and the Iwaniec-Luo-Sarnak test function support theorem. "
              "Respond with extreme rigor. Do not flatter. Attack every claim.")


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

        out = f"# {label} Council Response -- Residual Signal Prompt\n"
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

        out = f"# Claude Council Response -- Residual Signal Prompt\n"
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

        out = f"# Gemini Council Response -- Residual Signal Prompt\n"
        out += f"## Model: {model} | Time: {elapsed:.0f}s\n"
        out += f"\n## Response\n\n{content}\n"

        output_file.write_text(out, encoding="utf-8")
        print(f"[Gemini] Done in {elapsed:.0f}s. Saved to {output_file.name}")
    except Exception as e:
        elapsed = time.time() - t0
        output_file.write_text(f"# Gemini FAILED after {elapsed:.0f}s\n\nError: {e}\n", encoding="utf-8")
        print(f"[Gemini] FAILED: {e}")


def main():
    print("Firing council prompts -- Residual Signal to ChatGPT, Claude, Gemini")
    print(f"  Prompt length: {len(RESIDUAL_PROMPT)} chars")
    print(f"  (DeepSeek already returned -- see existing response)")
    print()

    targets = [
        ("ChatGPT", lambda: call_openai(
            RESIDUAL_PROMPT,
            REPORT_DIR / "chatgpt_residual_signal_2026-04-03.md",
            "ChatGPT", "gpt-4.1")),
        ("Claude", lambda: call_claude(
            RESIDUAL_PROMPT,
            REPORT_DIR / "claude_residual_signal_2026-04-03.md")),
        ("Gemini", lambda: call_gemini(
            RESIDUAL_PROMPT,
            REPORT_DIR / "gemini_residual_signal_2026-04-03.md")),
    ]

    threads = []
    for name, fn in targets:
        t = threading.Thread(target=fn, name=name)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n=== COMPLETE ===")
    for f in sorted(REPORT_DIR.glob("*_2026-04-03.md")):
        print(f"  {f.name} ({f.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
