import sys, json, time
sys.path.insert(0, '.')
from forge.llm_client import _load_api_key
from urllib import request, error

key = _load_api_key('NVIDIA_API_KEY')

models = [
    "deepseek/deepseek-r1",
    "meta/llama-3.3-70b-instruct",
]

for model in models:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Generate a Python class called ReasoningTool with a method evaluate(self, prompt, candidates) that returns a sorted list of dicts with 'candidate' and 'score' keys. Output only code, no explanation."}],
        "max_tokens": 500,
        "temperature": 0.7,
    }).encode()
    req = request.Request(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    t0 = time.time()
    try:
        with request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        elapsed = time.time() - t0
        content = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})
        has_class = "class ReasoningTool" in content
        print(f"{model}: {elapsed:.1f}s, {usage.get('total_tokens', '?')} tokens, has_class={has_class}")
        print(f"  First 150 chars: {content[:150]}")
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"{model}: FAIL {e.code}: {body}")
    except Exception as e:
        print(f"{model}: ERROR: {e}")
    print()
