"""
LLM cascade — extracted from agents/metis/src/metis.py so it propagates
to all machines via git pull (agents/ is gitignored at the directory level
on the public repo).

Same cascade Metis uses: Cerebras Qwen3-235B → Groq Llama-3.3-70B →
NVIDIA Nemotron-120B → DeepSeek-V4-Flash (paid last-resort). Cloudflare
bot-detection bypassed via Mozilla User-Agent. 240s timeout for slow
NVIDIA Nemotron cold starts.

Auto-loads agents/eos/.env on import so callers don't need to manage
credential plumbing. The .env reader uses setdefault so command-line /
shell env vars still override file values.
"""
import json
import logging
import os
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Optional

log = logging.getLogger("llm_cascade")

REPO_ROOT = Path(__file__).resolve().parent.parent

# Auto-load shared keys from agents/eos/.env (cross-pipeline convention)
_ENV_FILE = REPO_ROOT / "agents" / "eos" / ".env"
if _ENV_FILE.exists():
    try:
        for _line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
    except Exception as e:
        log.warning("Could not auto-load %s: %s", _ENV_FILE, e)


def _get_ssl_context():
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


# Mozilla UA bypasses Cloudflare error 1010 on Cerebras + Groq endpoints.
# The default urllib UA gets flagged as a bot.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def _build_providers() -> list:
    """Provider list, in cascade order. Fastest first; paid last resort."""
    return [
        {
            "name": "Cerebras Qwen3-235B",
            "endpoint": "https://api.cerebras.ai/v1",
            "key": os.environ.get("CEREBRAS_API_KEY"),
            "model": "qwen-3-235b-a22b-instruct-2507",
        },
        {
            "name": "Groq Llama-3.3-70B",
            "endpoint": "https://api.groq.com/openai/v1",
            "key": os.environ.get("GROQ_API_KEY"),
            "model": "llama-3.3-70b-versatile",
        },
        {
            "name": "NVIDIA Nemotron-120B",
            "endpoint": os.environ.get("NVIDIA_API_ENDPOINT", "https://integrate.api.nvidia.com/v1"),
            "key": os.environ.get("NVIDIA_API_KEY"),
            "model": os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b"),
        },
        {
            "name": "DeepSeek-V4-Flash (paid)",
            "endpoint": "https://api.deepseek.com/v1",
            "key": os.environ.get("DEEPSEEK_API_KEY"),
            "model": "deepseek-v4-flash",
        },
    ]


def call_llm(prompt: str, system: str = "", max_tokens: int = 4000,
             temperature: float = 0.3, timeout: int = 240) -> str:
    """Try the cascade; return text from the first provider that succeeds.
    Returns "(LLM cascade failed)" if all providers fail."""
    providers = _build_providers()
    ctx = _get_ssl_context()

    for provider in providers:
        if not provider["key"]:
            continue
        log.info(f"Trying {provider['name']}...")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps({
            "model": provider["model"],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode("utf-8")
        try:
            req = urllib.request.Request(
                f"{provider['endpoint']}/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {provider['key']}",
                    "User-Agent": _USER_AGENT,
                    "Accept": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                text = (msg.get("content") or msg.get("reasoning_content") or "").strip()
                if text:
                    log.info(f"Response from {provider['name']} ({len(text)} chars)")
                    return text
        except Exception as e:
            log.warning(f"{provider['name']} failed: {e}")
            continue

    log.error("All LLM providers in cascade failed")
    return "(LLM cascade failed — no provider returned text)"


if __name__ == "__main__":
    # CLI smoke test: `python scripts/llm_cascade.py "hello"`
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Say one short sentence."
    print(call_llm(prompt))
