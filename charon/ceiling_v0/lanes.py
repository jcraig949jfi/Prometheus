"""Lane preflight. RESTORED 2026-08-23.

Iteration 5 lesson, learned expensively: a lane probe must be the SIZE of the real
workload. A 12-token "say OK" returned 200 OK in 0.7s from a lane whose balance was
negative; the first ~3k-token turn came back 402 and the run was lost. A cheap probe
answers "is the endpoint reachable", which is not the question. The question is
"will it serve MY request".

`min_tps` is purpose-dependent and the distinction is principled, not a moved
goalpost. An ACCURACY run needs throughput because a dropped call breaks LLM-turn
matching and contaminates the arm's whole trajectory. An EMISSION probe scores each
turn independently, so a slow lane costs wall clock and nothing else.
"""
from __future__ import annotations

import json
import time
import urllib.request
from typing import Dict, List, Optional, Tuple

from reasoner import _load_env

MIN_TOK_PER_S = 3.0
MAX_LATENCY_S = 120.0
REQUIRED_COMPLETION_TOKENS = 120

LANES: Dict[str, Dict] = {
    "openrouter": {"url": "https://openrouter.ai/api/v1/chat/completions",
                   "key": "OPENROUTER_API_KEY",
                   "model": "meta-llama/llama-3.3-70b-instruct",
                   "provider": "deepinfra"},
    "nvidia": {"url": "https://integrate.api.nvidia.com/v1/chat/completions",
               "key": "NVIDIA_API_KEY",
               "model": "meta/llama-3.3-70b-instruct"},
    "deepseek": {"url": "https://api.deepseek.com/chat/completions",
                 "key": "DEEPSEEK_API_KEY", "model": "deepseek-chat"},
    "openai": {"url": "https://api.openai.com/v1/chat/completions",
               "key": "OPENAI_API_KEY", "model": "gpt-4o-mini"},
}


def _payload(pad_chars: int = 9_000) -> Tuple[str, str]:
    system = ("You are probing an unfamiliar system. Reply with JSON only. "
              "No prose outside the JSON.")
    filler = "\n".join(
        f"  K{i % 4} A{i % 4} A{(i + 1) % 4} -> q{i % 4} q{(i + 1) % 4}"
        for i in range(pad_chars // 34))
    user = ("RECORDED OUTCOMES:\n" + filler +
            '\n\nReply with JSON, 12 run entries:\n'
            '{"runs": [{"tag": "K0", "seq": "A1 A2"}], "claims": [], "note": ""}')
    return system, user


def probe(name: str, spec: Dict, timeout: float = MAX_LATENCY_S,
          min_tps: float = MIN_TOK_PER_S) -> Dict:
    key = _load_env().get(spec["key"])
    if not key:
        return {"lane": name, "up": False, "why": "no key"}
    system, user = _payload()
    body = {"model": spec["model"],
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": 0, "max_tokens": 900}
    if spec.get("provider"):
        body["provider"] = {"order": [spec["provider"]], "allow_fallbacks": False}
    req = urllib.request.Request(
        spec["url"], data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json",
                 "User-Agent": "python-urllib/3.12"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            r = json.load(resp)
    except Exception as exc:                             # noqa: BLE001
        detail = ""
        try:
            detail = exc.read().decode()[:110]           # type: ignore[attr-defined]
        except Exception:                                # noqa: BLE001
            pass
        return {"lane": name, "up": False,
                "why": f"{type(exc).__name__} {str(exc)[:50]} {detail}".strip(),
                "elapsed": round(time.time() - t, 1)}
    dt = max(1e-6, time.time() - t)
    ct = int((r.get("usage") or {}).get("completion_tokens", 0))
    tps = ct / dt
    ok = ct >= REQUIRED_COMPLETION_TOKENS and tps >= min_tps and dt <= timeout
    why = "ok" if ok else (
        f"completion {ct} tok < {REQUIRED_COMPLETION_TOKENS}"
        if ct < REQUIRED_COMPLETION_TOKENS else f"{tps:.1f} tok/s below {min_tps}")
    return {"lane": name, "up": ok, "why": why, "elapsed": round(dt, 1),
            "completion_tokens": ct, "tok_per_s": round(tps, 1),
            "min_tps_required": min_tps}


def first_usable(order: Optional[List[str]] = None,
                 min_tps: float = MIN_TOK_PER_S) -> Optional[Dict]:
    for name in (order or list(LANES)):
        r = probe(name, LANES[name], min_tps=min_tps)
        print(f"  {name:<12} {'UP  ' if r['up'] else 'down'} {r.get('why','')[:80]}")
        if r["up"]:
            return r
    return None


if __name__ == "__main__":
    print(f"representative-payload probe (needs >={REQUIRED_COMPLETION_TOKENS} "
          f"tok, >={MIN_TOK_PER_S} tok/s, <={MAX_LATENCY_S}s)")
    for name, spec in LANES.items():
        r = probe(name, spec)
        extra = (f"{r.get('elapsed')}s {r.get('completion_tokens')}tok "
                 f"{r.get('tok_per_s')}tok/s" if r["up"] else "")
        print(f"  {name:<12} {'UP  ' if r['up'] else 'down'} {r['why'][:90]} {extra}")
