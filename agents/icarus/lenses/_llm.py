"""
Shared LLM call helpers for lenses. Cross-family dispatch.

Each lens declares a model_preference (claude / gemini / deepseek). This
module abstracts the SDK differences and provides fallback chains.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(r"D:\Prometheus")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def call_llm(
    preference: str,
    system: str,
    user: str,
    max_tokens: int = 2500,
) -> dict:
    """Dispatch an LLM call to the preferred family. Falls back to Claude
    if the preferred family is unavailable.

    Returns:
        {
          "text": str,
          "model_used": str,
          "tokens_used": int,
          "cost_estimate_usd": float,
          "error": Optional[str],
        }
    """
    order = _fallback_chain(preference)
    last_err = None
    for backend in order:
        try:
            result = _CALLERS[backend](system, user, max_tokens)
            if result and result.get("text"):
                return result
        except Exception as e:
            last_err = f"{backend}: {type(e).__name__}: {e}"
            continue
    return {
        "text": "", "model_used": "none",
        "tokens_used": 0, "cost_estimate_usd": 0.0,
        "error": last_err or "all_backends_failed",
    }


def _fallback_chain(preference: str) -> list[str]:
    """Order of backends to try. Always end with claude_haiku as final fallback."""
    if preference == "gemini":
        return ["gemini", "claude_sonnet", "claude_haiku"]
    if preference == "deepseek":
        return ["deepseek", "gemini", "claude_haiku"]
    if preference == "claude_sonnet" or preference == "claude":
        return ["claude_sonnet", "claude_haiku"]
    if preference == "claude_haiku":
        return ["claude_haiku", "gemini"]
    return ["claude_sonnet", "claude_haiku"]


def _call_claude_sonnet(system: str, user: str, max_tokens: int) -> dict:
    return _call_claude(system, user, max_tokens, model="claude-sonnet-4-6")


def _call_claude_haiku(system: str, user: str, max_tokens: int) -> dict:
    return _call_claude(system, user, max_tokens, model="claude-haiku-4-5-20251001")


def _call_claude(system: str, user: str, max_tokens: int, model: str) -> dict:
    from keys import get_key  # type: ignore
    from anthropic import Anthropic
    client = Anthropic(api_key=get_key("CLAUDE"))
    resp = client.messages.create(
        model=model, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = resp.content[0].text if resp.content else ""
    in_tok = getattr(resp.usage, "input_tokens", 0)
    out_tok = getattr(resp.usage, "output_tokens", 0)
    if "opus" in model.lower():
        cost = (in_tok / 1e6) * 15.0 + (out_tok / 1e6) * 75.0
    elif "sonnet" in model.lower():
        cost = (in_tok / 1e6) * 3.0 + (out_tok / 1e6) * 15.0
    else:
        cost = (in_tok / 1e6) * 0.80 + (out_tok / 1e6) * 4.0
    return {
        "text": text, "model_used": model,
        "tokens_used": in_tok + out_tok,
        "cost_estimate_usd": cost, "error": None,
    }


def _call_gemini(system: str, user: str, max_tokens: int) -> dict:
    from keys import get_key  # type: ignore
    import google.generativeai as genai
    genai.configure(api_key=get_key("GEMINI"))
    model_obj = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system,
    )
    resp = model_obj.generate_content(
        user,
        generation_config={"max_output_tokens": max_tokens},
    )
    text = resp.text or ""
    # Token estimation (Gemini doesn't always return usage)
    in_tok = len(system) // 4 + len(user) // 4
    out_tok = len(text) // 4
    # gemini-2.5-flash pricing approx
    cost = (in_tok / 1e6) * 0.30 + (out_tok / 1e6) * 2.50
    return {
        "text": text, "model_used": "gemini-2.5-flash",
        "tokens_used": in_tok + out_tok,
        "cost_estimate_usd": cost, "error": None,
    }


def _call_deepseek(system: str, user: str, max_tokens: int) -> dict:
    from keys import get_key  # type: ignore
    from openai import OpenAI
    client = OpenAI(
        api_key=get_key("DEEPSEEK"),
        base_url="https://api.deepseek.com/v1",
    )
    resp = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    text = resp.choices[0].message.content or ""
    usage = resp.usage
    in_tok = getattr(usage, "prompt_tokens", 0)
    out_tok = getattr(usage, "completion_tokens", 0)
    # deepseek-chat approx pricing
    cost = (in_tok / 1e6) * 0.27 + (out_tok / 1e6) * 1.10
    return {
        "text": text, "model_used": "deepseek-chat",
        "tokens_used": in_tok + out_tok,
        "cost_estimate_usd": cost, "error": None,
    }


_CALLERS = {
    "claude_sonnet": _call_claude_sonnet,
    "claude_haiku": _call_claude_haiku,
    "gemini": _call_gemini,
    "deepseek": _call_deepseek,
}


def extract_json_block(text: str) -> Optional[dict]:
    """Pull a JSON object out of an LLM response. Tries fenced ```json then
    bare object then array.
    """
    if not text:
        return None
    # Try fenced block
    m = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    candidate = m.group(1).strip() if m else text.strip()
    # Try direct parse
    try:
        return json.loads(candidate)
    except Exception:
        pass
    # Try to find first { ... } balanced block
    start = candidate.find("{")
    if start == -1:
        return None
    depth = 0
    end = -1
    for i in range(start, len(candidate)):
        c = candidate[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end > start:
        try:
            return json.loads(candidate[start:end])
        except Exception:
            return None
    return None


def clamp_axis(v) -> float:
    """Coerce LLM-returned axis values into 0.0-1.0 floats."""
    try:
        f = float(v)
        return max(0.0, min(1.0, f))
    except Exception:
        return 0.5
