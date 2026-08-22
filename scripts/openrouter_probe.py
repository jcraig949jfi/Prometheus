"""
openrouter_probe.py -- Minimal direct channel to OpenRouter models.

Purpose: raw-model access with no agent harness in the path. Per
`feedback_loop_inference_over_api`, RAW-MODEL measurement must not be routed
through an agent CLI -- the harness is a confound. This is the thinnest
channel that still reports latency and token accounting.

SCOPE WARNING: this is a smoke test, not an instrument. No null, no chance
floor, no repeated seeds, single prompt per task. Its output establishes
"the channel is open and the model responds", nothing further. Do not cite
it as a result.

Usage:
    python scripts/openrouter_probe.py --list-free
    python scripts/openrouter_probe.py --list --grep alpha
    python scripts/openrouter_probe.py --smoke
    python scripts/openrouter_probe.py --model stealth/ox-alpha --prompt "..."

Requires OPENROUTER_API_KEY in environment or .env (see keys.py).

GOTCHA (measured 2026-08-22, stealth/ox-alpha): reasoning models emit
reasoning content that COUNTS AGAINST max_tokens while being reported as
`reasoning_tokens: 0`. Under-budgeting yields HTTP 200 + finish="length" +
EMPTY content -- a silent failure that naive harnesses score as success.
Budget generously and always check `empty_content`.
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
from keys import get_key

BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "stealth/ox-alpha"
TIMEOUT = 180


def _headers():
    return {
        "Authorization": f"Bearer {get_key('OPENROUTER')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/prometheus",
        "X-Title": "Prometheus",
    }


def list_models(grep=None, free_only=False):
    """GET the model catalog. Resolves exact model ids empirically."""
    r = requests.get(f"{BASE}/models", headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    rows = r.json().get("data", [])
    out = []
    for m in rows:
        mid = m.get("id", "")
        pricing = m.get("pricing", {}) or {}
        p_in = str(pricing.get("prompt", "?"))
        p_out = str(pricing.get("completion", "?"))
        is_free = p_in in ("0", "0.0", "-1") and p_out in ("0", "0.0", "-1")
        if free_only and not is_free:
            continue
        if grep and grep.lower() not in mid.lower() and grep.lower() not in str(m.get("name", "")).lower():
            continue
        out.append({
            "id": mid,
            "name": m.get("name"),
            "ctx": m.get("context_length"),
            "max_out": (m.get("top_provider") or {}).get("max_completion_tokens"),
            "in_$/tok": p_in,
            "out_$/tok": p_out,
            "free": is_free,
        })
    return out


def chat(model, messages, max_tokens=1024, temperature=0.0, extra=None):
    """One request. Returns dict with text, usage, latency_s, finish_reason."""
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if extra:
        body.update(extra)
    t0 = time.perf_counter()
    r = requests.post(f"{BASE}/chat/completions", headers=_headers(),
                      json=body, timeout=TIMEOUT)
    dt = time.perf_counter() - t0
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "error": r.text[:2000],
                "latency_s": round(dt, 2)}
    d = r.json()
    if "error" in d:
        return {"ok": False, "status": 200, "error": json.dumps(d["error"])[:2000],
                "latency_s": round(dt, 2)}
    choice = (d.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    text = msg.get("content") or ""
    return {
        # ok means usable content, not merely HTTP 200 -- see GOTCHA above.
        "ok": bool(text.strip()),
        "empty_content": not text.strip(),
        "text": text,
        "reasoning": msg.get("reasoning"),
        "finish_reason": choice.get("finish_reason"),
        "usage": d.get("usage", {}),
        "model_served": d.get("model"),
        "provider": d.get("provider"),
        "latency_s": round(dt, 2),
    }


SMOKE_TASKS = [
    ("reachability", "Reply with exactly the word: PONG", 2000),
    ("instruction_following",
     "Return ONLY a JSON object, no prose, no code fence, with keys "
     "'a' (integer 7) and 'b' (list of the first 3 primes).", 2000),
    ("coding",
     "Write a Python function `dedupe_stable(xs)` that removes duplicates "
     "while preserving first-occurrence order, works on unhashable items, "
     "and is O(n) for hashable ones. Return only code.", 6000),
]


def smoke(model):
    print(f"\n=== SMOKE: {model} ===")
    print("(smoke test -- establishes channel liveness only, not capability)\n")
    results = []
    for name, prompt, mt in SMOKE_TASKS:
        res = chat(model, [{"role": "user", "content": prompt}], max_tokens=mt)
        results.append((name, res))
        if not res["ok"] and not res.get("empty_content"):
            print(f"[{name}] HTTP FAIL status={res['status']} ({res['latency_s']}s)")
            print(f"  {res['error'][:500]}")
            continue
        u = res["usage"] or {}
        print(f"[{name}] {res['latency_s']}s  "
              f"served={res.get('model_served')}  "
              f"provider={res.get('provider')}  "
              f"finish={res.get('finish_reason')}  "
              f"tok in/out={u.get('prompt_tokens')}/{u.get('completion_tokens')}")
        body = (res["text"] or "").strip()
        print("  " + (body[:600].replace("\n", "\n  ") or "<EMPTY>"))
        print()
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--prompt")
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--list-free", action="store_true")
    ap.add_argument("--grep")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        get_key("OPENROUTER")
    except ValueError as e:
        print("NO KEY: " + str(e), file=sys.stderr)
        print("\nGet one at https://openrouter.ai/keys , then add to "
              "D:/Prometheus/.env :\n  OPENROUTER_API_KEY=sk-or-v1-...",
              file=sys.stderr)
        return 2

    if args.list or args.list_free:
        rows = list_models(grep=args.grep, free_only=args.list_free)
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            print(f"{len(rows)} model(s):")
            for m in rows:
                tag = "FREE" if m["free"] else "paid"
                print(f"  [{tag}] {m['id']:<52} ctx={m['ctx']} max_out={m['max_out']}")
        return 0

    if args.smoke:
        res = smoke(args.model)
        return 0 if all(r["ok"] for _, r in res) else 1

    if args.prompt:
        res = chat(args.model, [{"role": "user", "content": args.prompt}],
                   max_tokens=args.max_tokens, temperature=args.temperature)
        print(json.dumps(res, indent=2) if args.json else
              (res["text"] if res["ok"] else f"ERROR {res['status']}: {res['error']}"))
        return 0 if res["ok"] else 1

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
