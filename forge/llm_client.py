"""LLM client for the Builder — calls LLM APIs to generate tools.

MIGRATED 2026-08-22 to route through `prometheus_llm`. The public surface is
unchanged: `generate_tool()`, `_extract_python()`, `_load_api_key()` and
`PROVIDERS` all still work, so no consumer needed editing.

What changed and why:

  * The old default was PROVIDER="deepseek", which has been HTTP 402
    Insufficient Balance since at least 2026-08-12 — this module could not
    run at all. The default target is now a provider measured LIVE.
  * Provider config, key loading and HTTP now live in `prometheus_llm`
    instead of being reimplemented here.

NOTE FOR MEASUREMENT WORK: the default target changed, so the model that
writes tools changed. That is fine for a builder, but do NOT compare tool
output generated before and after this date without pinning FORGE_LLM_TARGET
to a single value across both sides of the comparison.

Override the target without editing code:

    FORGE_LLM_TARGET="openrouter:stealth/ox-alpha"    # default
    FORGE_LLM_FALLBACK="groq,nvidia"                  # comma-separated
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from keys import get_key as _central_get_key  # noqa: E402
from prometheus_llm import complete  # noqa: E402

# ── Target configuration ───────────────────────────────────────────────
# "provider:model" — colon-delimited, since model ids contain "/".
DEFAULT_TARGET = "openrouter:stealth/ox-alpha"
DEFAULT_FALLBACK = ["groq", "nvidia"]


def _target() -> str:
    return os.environ.get("FORGE_LLM_TARGET", DEFAULT_TARGET)


def _fallback() -> list[str]:
    raw = os.environ.get("FORGE_LLM_FALLBACK")
    if raw is None:
        return list(DEFAULT_FALLBACK)
    return [t.strip() for t in raw.split(",") if t.strip()]


# ── Back-compat shims ──────────────────────────────────────────────────
# forge/v2/hephaestus_t2 imports PROVIDERS and _load_api_key. Kept working;
# prefer prometheus_llm.registry for anything new.

PROVIDERS = {
    "deepseek": {"url": "https://api.deepseek.com/chat/completions",
                 "model": "deepseek-chat", "key_env": "DEEPSEEK_API_KEY",
                 "headers": {}},
    "nvidia": {"url": "https://integrate.api.nvidia.com/v1/chat/completions",
               "model": "meta/llama-3.1-8b-instruct",
               "key_env": "NVIDIA_API_KEY", "headers": {}},
    "openrouter": {"url": "https://openrouter.ai/api/v1/chat/completions",
                   "model": "stealth/ox-alpha",
                   "key_env": "OPENROUTER_API_KEY",
                   "headers": {"HTTP-Referer": "https://github.com/prometheus-forge",
                               "X-Title": "Prometheus Forge Builder"}},
}

PROVIDER = "openrouter"  # deprecated; _target() is what actually routes

_KEY_MAP = {
    "DEEPSEEK_API_KEY": "DEEPSEEK",
    "OPENAI_API_KEY": "OPENAI",
    "NVIDIA_API_KEY": "NVIDIA",
    "OPENROUTER_API_KEY": "OPENROUTER",
    "GROQ_API_KEY": "GROQ",
    "CEREBRAS_API_KEY": "CEREBRAS",
}


def _load_api_key(key_name):
    """Load an API key by env-var name. Deprecated — use keys.get_key().

    keys.py now searches agents/eos/.env itself, so the manual .env scan this
    function used to do is gone.
    """
    friendly = _KEY_MAP.get(key_name)
    if friendly:
        try:
            return _central_get_key(friendly)
        except ValueError:
            pass
    key = os.environ.get(key_name, "")
    if key:
        return key
    raise RuntimeError(f"{key_name} not found in environment or config files")


# ── Public API ─────────────────────────────────────────────────────────

def generate_tool(system_prompt, user_prompt=None, temperature=0.7,
                  max_tokens=4096):
    """Call the configured LLM to generate a tool.

    Returns:
        dict with 'code' (extracted Python), 'raw' (full response),
        'usage' (token counts), 'model' (what actually served the request)

    Raises:
        RuntimeError on API failure, as before.
    """
    if not user_prompt:
        user_prompt = ("Generate the ReasoningTool class now. "
                       "Output ONLY Python code.")

    c = complete(user_prompt, target=_target(), system=system_prompt,
                 temperature=temperature, max_tokens=max_tokens,
                 fallback=_fallback(), timeout=120)

    if not c.ok:
        raise RuntimeError(f"API error: {c.summary()}")

    return {
        "code": _extract_python(c.text),
        "raw": c.text,
        "usage": {"prompt_tokens": c.prompt_tokens,
                  "completion_tokens": c.completion_tokens,
                  "total_tokens": c.total_tokens},
        "model": c.model_served or c.model,
    }


def _extract_python(text):
    """Extract Python code from markdown-wrapped LLM response."""
    # Try ```python ... ``` blocks first
    pattern = r'```python\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        # Return the longest match (likely the full tool)
        return max(matches, key=len).strip()

    # Try ``` ... ``` blocks
    pattern = r'```\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return max(matches, key=len).strip()

    # If no code blocks, check if the entire response is Python
    if "class ReasoningTool" in text:
        # Strip any leading/trailing non-code
        lines = text.split('\n')
        start = next((i for i, l in enumerate(lines)
                      if l.strip().startswith(('import ', 'from ', 'class ',
                                               '#', '"""'))), 0)
        return '\n'.join(lines[start:]).strip()

    return text.strip()


if __name__ == "__main__":
    # Quick test
    result = generate_tool(
        "You are a test. Respond with a simple Python class.",
        "Generate a class Foo with a method bar() that returns 42.",
        temperature=0.0,
        max_tokens=2000,
    )
    print(f"Model: {result['model']}")
    print(f"Usage: {result['usage']}")
    print(f"Code:\n{result['code']}")
