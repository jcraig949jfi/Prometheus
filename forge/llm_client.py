"""LLM client for the Builder — calls LLM APIs to generate tools.

Supports: NVIDIA (Nemotron), OpenRouter (DeepSeek V3.2), configurable via PROVIDER.
Reads API keys from agents/eos/.env or environment.
"""
import os, json, re
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parent.parent

# ── Provider configuration ─────────────────────────────────────────────
PROVIDER = "nvidia"  # "nvidia" or "openrouter"

PROVIDERS = {
    "nvidia": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "meta/llama-3.3-70b-instruct",
        "key_env": "NVIDIA_API_KEY",
        "headers": {},
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "deepseek/deepseek-v3.2",
        "key_env": "OPENROUTER_API_KEY",
        "headers": {
            "HTTP-Referer": "https://github.com/prometheus-forge",
            "X-Title": "Prometheus Forge Builder",
        },
    },
}


def _load_api_key(key_name):
    """Load API key from environment or agents/eos/.env."""
    key = os.environ.get(key_name, "")
    if key:
        return key
    env_path = ROOT / "agents" / "eos" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{key_name}="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(f"{key_name} not found in environment or agents/eos/.env")


def generate_tool(system_prompt, user_prompt=None, temperature=0.7, max_tokens=4096):
    """Call the configured LLM provider to generate a tool.

    Returns:
        dict with 'code' (extracted Python), 'raw' (full response), 'usage' (token counts)
    """
    cfg = PROVIDERS[PROVIDER]
    api_key = _load_api_key(cfg["key_env"])

    messages = [{"role": "system", "content": system_prompt}]
    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})
    else:
        messages.append({"role": "user", "content": "Generate the ReasoningTool class now. Output ONLY Python code."})

    payload = {
        "model": cfg["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    headers.update(cfg["headers"])

    req = request.Request(
        cfg["url"],
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API error {e.code}: {body[:500]}")

    raw_content = result["choices"][0]["message"]["content"]
    usage = result.get("usage", {})

    code = _extract_python(raw_content)

    return {
        "code": code,
        "raw": raw_content,
        "usage": usage,
        "model": result.get("model", cfg["model"]),
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
        start = next((i for i, l in enumerate(lines) if l.strip().startswith(('import ', 'from ', 'class ', '#', '"""'))), 0)
        return '\n'.join(lines[start:]).strip()
    
    return text.strip()


if __name__ == "__main__":
    # Quick test
    result = generate_tool(
        "You are a test. Respond with a simple Python class.",
        "Generate a class Foo with a method bar() that returns 42.",
        temperature=0.0,
        max_tokens=200,
    )
    print(f"Model: {result['model']}")
    print(f"Usage: {result['usage']}")
    print(f"Code:\n{result['code']}")
