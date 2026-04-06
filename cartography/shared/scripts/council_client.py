"""
Council Client — Unified API wrapper for research cycle.
=========================================================
Providers:
  - DeepSeek (cheap, fast, no daily limits — primary workhorse)
  - OpenAI GPT-4.1
  - Claude Sonnet 4
  - Gemini 2.5 Flash

Usage:
    from council_client import ask, ask_json, ask_all
    response = ask("question", provider="deepseek")
    structured = ask_json("question expecting JSON")
    all_responses = ask_all("question")  # parallel to all 4 providers
"""

import json
import time
import sys
import threading
from pathlib import Path

# Keys via central keys.py
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from keys import get_key


# ---------------------------------------------------------------------------
# Provider implementations — each returns a standardized dict
# ---------------------------------------------------------------------------

def _call_deepseek(system: str, prompt: str, model: str = "deepseek-chat",
                   max_tokens: int = 4096, temperature: float = 0.3) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=get_key("DEEPSEEK"), base_url="https://api.deepseek.com")
    t0 = time.time()
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    elapsed = time.time() - t0
    return {
        "text": r.choices[0].message.content,
        "model": model,
        "provider": "deepseek",
        "prompt_tokens": r.usage.prompt_tokens if r.usage else 0,
        "completion_tokens": r.usage.completion_tokens if r.usage else 0,
        "elapsed_s": elapsed,
    }


def _call_openai(system: str, prompt: str, model: str = "gpt-4.1",
                 max_tokens: int = 4096, temperature: float = 0.3) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=get_key("OPENAI"))
    t0 = time.time()
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    elapsed = time.time() - t0
    return {
        "text": r.choices[0].message.content,
        "model": model,
        "provider": "openai",
        "prompt_tokens": r.usage.prompt_tokens if r.usage else 0,
        "completion_tokens": r.usage.completion_tokens if r.usage else 0,
        "elapsed_s": elapsed,
    }


def _call_claude(system: str, prompt: str, model: str = "claude-sonnet-4-20250514",
                 max_tokens: int = 4096, temperature: float = 0.3) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=get_key("CLAUDE"))
    t0 = time.time()
    r = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.time() - t0
    return {
        "text": r.content[0].text,
        "model": model,
        "provider": "claude",
        "prompt_tokens": r.usage.input_tokens if r.usage else 0,
        "completion_tokens": r.usage.output_tokens if r.usage else 0,
        "elapsed_s": elapsed,
    }


def _call_gemini(system: str, prompt: str, model: str = "gemini-2.5-flash",
                 max_tokens: int = 4096, temperature: float = 0.3) -> dict:
    from google import genai
    client = genai.Client(api_key=get_key("GEMINI"))
    t0 = time.time()
    r = client.models.generate_content(
        model=model,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=temperature,
        ),
    )
    elapsed = time.time() - t0
    return {
        "text": r.text,
        "model": model,
        "provider": "gemini",
        "prompt_tokens": 0,  # Gemini doesn't always return token counts
        "completion_tokens": 0,
        "elapsed_s": elapsed,
    }


PROVIDERS = {
    "deepseek": _call_deepseek,
    "openai": _call_openai,
    "claude": _call_claude,
    "gemini": _call_gemini,
}

ALL_PROVIDER_NAMES = ["deepseek", "openai", "claude", "gemini"]


# ---------------------------------------------------------------------------
# Single-provider ask
# ---------------------------------------------------------------------------

def ask(prompt: str, system: str = "", provider: str = "deepseek",
        max_tokens: int = 4096, temperature: float = 0.3) -> str:
    """Ask a single council member. Returns raw text.

    Side effect: logs to CycleLogger if one is active.
    """
    if not system:
        system = ("You are a research assistant with expertise in mathematics, "
                  "physics, and data science. Be precise, specific, and quantitative.")
    fn = PROVIDERS.get(provider, _call_deepseek)

    import cycle_logger
    log = cycle_logger.get()

    try:
        result = fn(system, prompt, max_tokens=max_tokens, temperature=temperature)
        if log:
            log.log_api_call(
                provider=result["provider"],
                model=result["model"],
                prompt_tokens=result["prompt_tokens"],
                completion_tokens=result["completion_tokens"],
                elapsed_s=result["elapsed_s"],
                system_msg=system,
                prompt_preview=prompt,
                response_preview=result["text"],
            )
        else:
            print(f"  [{result['provider']}] {result['elapsed_s']:.1f}s | "
                  f"{result['prompt_tokens']}in/{result['completion_tokens']}out")
        return result["text"]
    except Exception as e:
        if log:
            log.error("council", "api_call_failed", {
                "provider": provider, "error": str(e),
                "prompt_preview": prompt[:300],
            }, msg=f"{provider} FAILED: {e}")
        else:
            print(f"  [{provider}] FAILED: {e}")
        if provider != "deepseek":
            return ask(prompt, system=system, provider="deepseek",
                      max_tokens=max_tokens, temperature=temperature)
        raise


# ---------------------------------------------------------------------------
# All-provider parallel ask
# ---------------------------------------------------------------------------

def ask_all(prompt: str, system: str = "", providers: list[str] = None,
            max_tokens: int = 4096, temperature: float = 0.3) -> dict[str, dict]:
    """Ask all council members in parallel. Returns {provider: {text, model, elapsed_s, error}}.

    Each provider runs in its own thread. Failures are caught per-provider
    and returned as error entries rather than killing the whole call.
    """
    if providers is None:
        providers = list(ALL_PROVIDER_NAMES)
    if not system:
        system = ("You are a research assistant with expertise in mathematics, "
                  "physics, and data science. Be precise, specific, and quantitative.")

    import cycle_logger
    log = cycle_logger.get()

    results = {}
    lock = threading.Lock()

    def _worker(provider_name: str):
        fn = PROVIDERS.get(provider_name)
        if not fn:
            with lock:
                results[provider_name] = {"error": f"Unknown provider: {provider_name}"}
            return
        try:
            result = fn(system, prompt, max_tokens=max_tokens, temperature=temperature)
            with lock:
                results[provider_name] = result
            if log:
                log.log_api_call(
                    provider=result["provider"],
                    model=result["model"],
                    prompt_tokens=result["prompt_tokens"],
                    completion_tokens=result["completion_tokens"],
                    elapsed_s=result["elapsed_s"],
                    system_msg=system,
                    prompt_preview=prompt,
                    response_preview=result["text"],
                )
        except Exception as e:
            with lock:
                results[provider_name] = {
                    "error": str(e),
                    "provider": provider_name,
                    "elapsed_s": 0,
                }
            if log:
                log.error("council", "api_call_failed", {
                    "provider": provider_name, "error": str(e),
                }, msg=f"{provider_name} FAILED: {e}")
            else:
                print(f"  [{provider_name}] FAILED: {e}")

    threads = []
    for p in providers:
        t = threading.Thread(target=_worker, args=(p,), name=p)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    if log:
        succeeded = sum(1 for r in results.values() if "text" in r)
        failed = sum(1 for r in results.values() if "error" in r)
        log.info("council", "ask_all_completed", {
            "n_providers": len(providers),
            "succeeded": succeeded,
            "failed": failed,
            "providers": list(results.keys()),
        }, msg=f"Council complete: {succeeded} responded, {failed} failed")

    return results


# ---------------------------------------------------------------------------
# JSON parsing helper
# ---------------------------------------------------------------------------

def _clean_json_text(text: str) -> str:
    """Strip markdown fences and trailing garbage from LLM JSON output."""
    cleaned = text.strip()
    # Strip markdown code fences
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines[1:] if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)
    # Find the outermost JSON structure (array or object) and truncate after it
    # This handles cases where the LLM appends commentary after valid JSON
    if cleaned.startswith("["):
        depth = 0
        for i, ch in enumerate(cleaned):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    cleaned = cleaned[:i+1]
                    break
    elif cleaned.startswith("{"):
        depth = 0
        for i, ch in enumerate(cleaned):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    cleaned = cleaned[:i+1]
                    break
    return cleaned


def ask_json(prompt: str, system: str = "", provider: str = "deepseek",
             max_tokens: int = 4096, retries: int = 2) -> dict | list:
    """Ask a question and parse the response as JSON.

    Strips markdown code fences and trailing garbage. Retries on parse failure.
    """
    import cycle_logger
    log = cycle_logger.get()

    for attempt in range(1 + retries):
        text = ask(prompt, system=system, provider=provider, max_tokens=max_tokens,
                   temperature=0.1)
        cleaned = _clean_json_text(text)
        try:
            parsed = json.loads(cleaned)
            if log:
                log.debug("council", "json_parsed", {
                    "type": type(parsed).__name__,
                    "n_items": len(parsed) if isinstance(parsed, (list, dict)) else 1,
                    "attempt": attempt + 1,
                })
            return parsed
        except json.JSONDecodeError as e:
            if log:
                log.warn("council", "json_parse_failed", {
                    "error": str(e),
                    "attempt": attempt + 1,
                    "raw_text_preview": cleaned[:500],
                }, msg=f"JSON parse failed (attempt {attempt+1}/{1+retries}): {e}")
            if attempt == retries:
                raise


if __name__ == "__main__":
    print("=== Council Client Smoke Test ===")
    r = ask("What is 2+2? Reply in one word.", provider="deepseek")
    print(f"DeepSeek: {r}")
