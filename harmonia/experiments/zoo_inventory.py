"""Model-zoo reachability inventory (EXPERIMENTAL, CHIP-AWAY).

Probes which OpenAI-compatible models actually respond *right now* with ONE
cheap call each, so the reasoning-ladder basis study can stand up an examinee
zoo (8-40 models, weighted to mid-tier / open-weight) instead of the saturated
3-model frontier trio.

Two credential planes (kept separate on purpose):
  * cascade plane  — scripts/llm_cascade auto-loads agents/eos/.env:
        Cerebras, Groq, GitHub Models, NVIDIA  (open-weight + mid)
  * keys plane     — keys.get_key reads repo .env:
        OpenAI, DeepSeek, Gemini, Claude/Anthropic (frontier + paid)

This file NEVER reads key files and NEVER prints key values. All credentials
flow through os.environ (loaded by llm_cascade) or keys.get_key. We only ever
print the *presence* (bool) of a key, never its content.

Output: a table (model id, provider, plane, reachable y/n, latency, tier,
supports_structured_output) and a machine-readable JSON dump next to it.

Usage:
    python harmonia/experiments/zoo_inventory.py            # probe all
    python harmonia/experiments/zoo_inventory.py --quick    # 1 model/provider
"""
from __future__ import annotations

import json
import os
import ssl
import sys
import time
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"
for _p in (str(_REPO_ROOT), str(_SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Importing llm_cascade auto-loads agents/eos/.env into os.environ.
import llm_cascade  # noqa: E402,F401  (side effect: env load + UA + ssl helpers)
from keys import get_key  # noqa: E402

_UA = llm_cascade._USER_AGENT
_SSL = llm_cascade._get_ssl_context()

# ----------------------------------------------------------------- catalog
# tier buckets: "frontier" | "mid" (~70-235B class) | "open-small" (7-30B)
# "plane": where the credential lives — "cascade" (os.environ) | "keys" (get_key)


@dataclass
class ModelSpec:
    model: str
    provider: str
    endpoint: str
    plane: str          # "cascade" | "keys"
    env_key: str        # os.environ var name (cascade plane)
    get_key_name: str   # keys.get_key friendly name (keys plane)
    tier: str
    structured: bool    # native structured-output / JSON-schema enforcement


# Open-weight + mid models are weighted heavily per the synthesis ("variance
# lives in the weaker models, not the saturated frontier trio"). We list a few
# alternates per provider so the inventory discovers what's actually live.
# NOTE: model IDs below were VERIFIED LIVE via each provider's /models endpoint
# on 2026-05-29 (see zoo_inventory_models_seen_* if regenerated). Provider
# catalogs drift; re-list before a full run. NVIDIA NIM is the deep bench (dozens
# of open-weight chat models, 1B-480B) — a representative size-stratified slice is
# listed here, not the whole catalog.
CATALOG: list[ModelSpec] = [
    # --- Cerebras (very fast open-weight inference) ---
    ModelSpec("gpt-oss-120b", "Cerebras", "https://api.cerebras.ai/v1",
              "cascade", "CEREBRAS_API_KEY", "", "mid", False),
    ModelSpec("zai-glm-4.7", "Cerebras", "https://api.cerebras.ai/v1",
              "cascade", "CEREBRAS_API_KEY", "", "mid", False),
    # --- Groq (fast open-weight inference) ---
    ModelSpec("llama-3.3-70b-versatile", "Groq", "https://api.groq.com/openai/v1",
              "cascade", "GROQ_API_KEY", "", "mid", False),
    ModelSpec("llama-3.1-8b-instant", "Groq", "https://api.groq.com/openai/v1",
              "cascade", "GROQ_API_KEY", "", "open-small", False),
    ModelSpec("meta-llama/llama-4-scout-17b-16e-instruct", "Groq", "https://api.groq.com/openai/v1",
              "cascade", "GROQ_API_KEY", "", "mid", False),
    ModelSpec("qwen/qwen3-32b", "Groq", "https://api.groq.com/openai/v1",
              "cascade", "GROQ_API_KEY", "", "mid", False),
    ModelSpec("openai/gpt-oss-20b", "Groq", "https://api.groq.com/openai/v1",
              "cascade", "GROQ_API_KEY", "", "open-small", False),
    # --- GitHub Models (Azure-hosted, OpenAI-compatible; tight free-tier rate cap) ---
    ModelSpec("gpt-4o-mini", "GitHubModels", "https://models.inference.ai.azure.com",
              "cascade", "GITHUB_TOKEN", "", "mid", False),
    # --- NVIDIA NIM (the deep open-weight bench; some cold-start latency) ---
    ModelSpec("nvidia/nemotron-3-super-120b-a12b", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "mid", False),
    ModelSpec("nvidia/llama-3.3-nemotron-super-49b-v1.5", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "mid", False),
    ModelSpec("meta/llama-3.3-70b-instruct", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "mid", False),
    ModelSpec("meta/llama-3.1-8b-instruct", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "open-small", False),
    ModelSpec("meta/llama-3.2-3b-instruct", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "open-small", False),
    ModelSpec("qwen/qwen3-next-80b-a3b-instruct", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "mid", False),
    ModelSpec("google/gemma-3-12b-it", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "open-small", False),
    ModelSpec("mistralai/mistral-7b-instruct-v0.3", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "open-small", False),
    ModelSpec("microsoft/phi-4-mini-instruct", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "open-small", False),
    ModelSpec("nvidia/nvidia-nemotron-nano-9b-v2", "NVIDIA", "https://integrate.api.nvidia.com/v1",
              "cascade", "NVIDIA_API_KEY", "", "open-small", False),
    # --- DeepSeek (paid; keys plane) ---
    ModelSpec("deepseek-chat", "DeepSeek", "https://api.deepseek.com/v1",
              "keys", "", "DEEPSEEK", "mid", False),
    # --- OpenAI (frontier/mid; keys plane) ---
    ModelSpec("gpt-4o-mini", "OpenAI", "https://api.openai.com/v1",
              "keys", "", "OPENAI", "mid", False),
    ModelSpec("gpt-4.1-mini", "OpenAI", "https://api.openai.com/v1",
              "keys", "", "OPENAI", "mid", False),
    ModelSpec("gpt-4.1-nano", "OpenAI", "https://api.openai.com/v1",
              "keys", "", "OPENAI", "open-small", False),
    ModelSpec("gpt-4o", "OpenAI", "https://api.openai.com/v1",
              "keys", "", "OPENAI", "frontier", False),
    # --- Gemini (frontier/mid; OpenAI-compat endpoint; keys plane; free-tier rate cap) ---
    ModelSpec("gemini-2.0-flash", "Gemini",
              "https://generativelanguage.googleapis.com/v1beta/openai",
              "keys", "", "GEMINI", "mid", False),
]


def _resolve_key(spec: ModelSpec) -> Optional[str]:
    """Return the credential for a spec, or None if unavailable.
    NEVER returns / prints the value to the caller's stdout."""
    if spec.plane == "cascade":
        return os.environ.get(spec.env_key)
    # keys plane
    try:
        return get_key(spec.get_key_name)
    except Exception:
        return None


def probe_one(spec: ModelSpec, timeout: int = 40) -> dict:
    """Single cheap completion. Returns reachability + latency + short note.
    Cost cap: max_tokens=8 — we only need to confirm the model answers."""
    key = _resolve_key(spec)
    rec = {**asdict(spec), "key_present": bool(key),
           "reachable": False, "latency_s": None, "note": ""}
    if not key:
        rec["note"] = "no_key"
        return rec
    payload = json.dumps({
        "model": spec.model,
        "messages": [{"role": "user", "content": "Reply with the single word: ok"}],
        "max_tokens": 8,
        "temperature": 0.0,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{spec.endpoint}/chat/completions", data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}",
                 "User-Agent": _UA, "Accept": "application/json"},
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        rec["latency_s"] = round(time.time() - t0, 2)
        choices = data.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            text = (msg.get("content") or msg.get("reasoning_content") or "").strip()
            rec["reachable"] = bool(text) or True  # 200 + choices == reachable
            rec["note"] = (text[:40] or "empty-content-but-200")
        else:
            rec["note"] = "200-no-choices"
    except urllib.error.HTTPError as e:
        rec["latency_s"] = round(time.time() - t0, 2)
        # Body can carry "model not found" vs "rate limit" — keep it, NO key leak.
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")[:160]
        except Exception:
            pass
        rec["note"] = f"HTTP{e.code}:{body}"
    except Exception as e:
        rec["latency_s"] = round(time.time() - t0, 2)
        rec["note"] = f"{type(e).__name__}:{str(e)[:80]}"
    return rec


def main():
    quick = "--quick" in sys.argv
    specs = CATALOG
    if quick:
        seen = set()
        specs = [s for s in CATALOG if not (s.provider in seen or seen.add(s.provider))]

    print(f"# Model-zoo reachability inventory ({time.strftime('%Y-%m-%d %H:%M')})")
    print(f"# probing {len(specs)} candidate models across "
          f"{len({s.provider for s in specs})} providers\n")

    results = []
    for s in specs:
        r = probe_one(s)
        results.append(r)
        flag = "OK " if r["reachable"] else "-- "
        lat = f"{r['latency_s']}s" if r["latency_s"] is not None else "  -  "
        print(f"  [{flag}] {s.provider:13s} {s.model:42s} {s.tier:11s} "
              f"key={int(r['key_present'])} {lat:>7s}  {r['note'][:60]}")

    reach = [r for r in results if r["reachable"]]
    print(f"\n# reachable: {len(reach)}/{len(results)}  "
          f"providers_live={sorted({r['provider'] for r in reach})}")

    # markdown table for the doc
    print("\n## Inventory table (markdown)\n")
    print("| Model | Provider | Plane | Tier | Reachable | Latency | Structured |")
    print("|---|---|---|---|---|---|---|")
    for r in results:
        print(f"| `{r['model']}` | {r['provider']} | {r['plane']} | {r['tier']} | "
              f"{'yes' if r['reachable'] else 'no'} | "
              f"{r['latency_s'] if r['latency_s'] is not None else '-'} | "
              f"{'yes' if r['structured'] else 'no'} |")

    out = Path(__file__).resolve().parent / "zoo_inventory_result.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n# wrote {out}")
    return results


if __name__ == "__main__":
    main()
