"""Test NVIDIA API connectivity and available models."""
import sys, os, time, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_key():
    env_path = ROOT / "agents" / "eos" / ".env"
    for line in env_path.read_text().splitlines():
        if line.startswith("NVIDIA_API_KEY="):
            return line.split("=", 1)[1].strip()
    return None

def test_model(api_key, model):
    from urllib import request, error
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Generate a Python class Foo with a method bar() that returns 42. Output only code."}],
        "temperature": 0.7,
        "max_tokens": 300,
    }).encode()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    req = request.Request("https://integrate.api.nvidia.com/v1/chat/completions",
                          data=payload, headers=headers, method="POST")
    try:
        t0 = time.time()
        with request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
        elapsed = time.time() - t0
        content = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})
        print(f"  OK  {elapsed:.1f}s  {usage.get('total_tokens', '?')} tokens")
        print(f"      Preview: {content[:100]}")
        return True
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"  FAIL {e.code}: {body}")
        return False
    except Exception as e:
        print(f"  FAIL: {e}")
        return False

api_key = load_key()
print(f"Key: {api_key[:15]}...{api_key[-5:]}")

models = [
    "deepseek/deepseek-r1",
    "meta/llama-3.3-70b-instruct",
    "nvidia/llama-3.3-nemotron-super-49b-v1",
    "meta/llama-3.1-405b-instruct",
]

for m in models:
    print(f"\n{m}:")
    test_model(api_key, m)
