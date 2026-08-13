"""Ergon — live API reachability/latency probe for the Metabolization Probe solver ladder.

Measures what the prereg assumes: does the endpoint answer, how fast, and does it survive a
realistic ~8K-token packet payload (the size F-prom-retrieved packets will be)?

stdlib only (urllib) — no global installs. Never prints key values.
Writes one typed JSONL record per trial.
"""
from __future__ import annotations
import json, os, sys, time, pathlib, urllib.request, urllib.error, socket

ROOT = pathlib.Path("F:/Prometheus")


def load_env_file(p: pathlib.Path) -> dict:
    env = {}
    if not p.exists():
        return env
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


root_env = load_env_file(ROOT / ".env")
eos_env = load_env_file(ROOT / "agents" / "eos" / ".env")


def key(name: str):
    for src in (os.environ, root_env, eos_env):
        v = src.get(name)
        if v:
            return v
    return None


NVIDIA_KEY = key("NVIDIA_API_KEY")
DEEPSEEK_KEY = key("DEEPSEEK_API_KEY")

SMALL_PROMPT = (
    "Claim: 8566 and 907 are coprime (share no common factor greater than 1).\n"
    "Is this claim true? Answer True or False, then justify in one sentence."
)
FILLER_UNIT = (
    "kill_signature: invariant_equality | margin: 0.0031 | falsifier: F17 | "
    "kill_pattern: asserted-equality-without-executing-computation | break_step: null\n"
)
BIG_PROMPT = (
    "The following is prior failure residue from earlier attempts on related problems.\n\n"
    + FILLER_UNIT * 420
    + "\n\n" + SMALL_PROMPT
)

NV = "https://integrate.api.nvidia.com/v1"
DS = "https://api.deepseek.com"

TARGETS = [
    ("nvidia", NV, NVIDIA_KEY, "nvidia/llama-3.3-nemotron-super-49b-v1"),
    ("nvidia", NV, NVIDIA_KEY, "meta/llama-3.3-70b-instruct"),
    ("nvidia", NV, NVIDIA_KEY, "qwen/qwen2.5-coder-32b-instruct"),
    ("nvidia", NV, NVIDIA_KEY, "deepseek-ai/deepseek-r1"),
    ("deepseek", DS, DEEPSEEK_KEY, "deepseek-chat"),
]

TIMEOUT = 90.0
TRIALS_SMALL = 3
OUT = pathlib.Path(__file__).with_name("api_probe_results.jsonl")


def http_json(url: str, api_key: str, payload=None, timeout=TIMEOUT):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
                 "Accept": "application/json"},
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def list_models(base_url, api_key, provider):
    t0 = time.monotonic()
    try:
        j = http_json(f"{base_url}/models", api_key, timeout=30.0)
        ids = [m.get("id") for m in j.get("data", [])]
        print(f"[{provider}] GET /models  OK  {time.monotonic()-t0:5.1f}s — {len(ids)} models")
        return ids
    except Exception as e:
        detail = ""
        if isinstance(e, urllib.error.HTTPError):
            detail = f" HTTP {e.code}"
        print(f"[{provider}] GET /models  FAIL {time.monotonic()-t0:5.1f}s — {type(e).__name__}{detail}: {str(e)[:120]}")
        return None


def trial(provider, base_url, api_key, model, prompt, label, max_tokens=64):
    rec = {"provider": provider, "model": model, "payload": label,
           "prompt_chars": len(prompt), "timeout_s": TIMEOUT}
    body = {"model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0.0, "stream": False}
    t0 = time.monotonic()
    try:
        j = http_json(f"{base_url}/chat/completions", api_key, body)
        dt = time.monotonic() - t0
        msg = (j.get("choices") or [{}])[0].get("message", {}) or {}
        txt = (msg.get("content") or "").strip().replace("\n", " ")
        u = j.get("usage") or {}
        rec.update(status="ok", latency_s=round(dt, 2),
                   prompt_tokens=u.get("prompt_tokens"),
                   completion_tokens=u.get("completion_tokens"),
                   reply=txt[:90])
        print(f"  {provider:9s} {model:40s} {label:5s} OK   {dt:6.1f}s in={u.get('prompt_tokens')} :: {txt[:52]}")
    except Exception as e:
        dt = time.monotonic() - t0
        etype = type(e).__name__
        emsg = str(e)[:180]
        if isinstance(e, urllib.error.HTTPError):
            etype = f"HTTP{e.code}"
            try:
                emsg = e.read().decode("utf-8", "replace")[:180]
            except Exception:
                pass
        elif isinstance(e, (socket.timeout, TimeoutError)):
            etype = "TIMEOUT"
        rec.update(status="error", latency_s=round(dt, 2), error_type=etype, error=emsg)
        print(f"  {provider:9s} {model:40s} {label:5s} FAIL {dt:6.1f}s {etype}: {emsg[:95]}")
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def main():
    print(f"keys: NVIDIA={'present' if NVIDIA_KEY else 'MISSING'} "
          f"DEEPSEEK={'present' if DEEPSEEK_KEY else 'MISSING'}\n")
    if OUT.exists():
        OUT.unlink()

    done = set()
    for provider, base_url, api_key, _ in TARGETS:
        if api_key and provider not in done:
            done.add(provider)
            list_models(base_url, api_key, provider)

    print("\n--- small payload (probe-shaped judgement task) ---")
    results = []
    for provider, base_url, api_key, model in TARGETS:
        if not api_key:
            print(f"  {provider}: no key — skipped")
            continue
        for _ in range(TRIALS_SMALL):
            results.append(trial(provider, base_url, api_key, model, SMALL_PROMPT, "small"))

    print("\n--- ~8K-token payload (realistic residue packet) ---")
    for provider, base_url, api_key, model in TARGETS:
        if not api_key:
            continue
        if not any(r["status"] == "ok" for r in results
                   if r["model"] == model and r["payload"] == "small"):
            print(f"  {provider:9s} {model:40s} big   SKIP (small never succeeded)")
            continue
        results.append(trial(provider, base_url, api_key, model, BIG_PROMPT, "big"))

    print("\n=== SUMMARY ===")
    from statistics import median
    agg = {}
    for r in results:
        agg.setdefault((r["provider"], r["model"], r["payload"]), []).append(r)
    for (prov, model, payload), rs in sorted(agg.items()):
        ok = [r for r in rs if r["status"] == "ok"]
        lat = f"{median([r['latency_s'] for r in ok]):6.1f}s" if ok else "     --"
        errs = sorted({r.get("error_type") for r in rs if r["status"] == "error"} - {None})
        print(f"  {prov:9s} {model:40s} {payload:5s} {len(ok)}/{len(rs)} ok  median {lat}"
              + (f"  errors={errs}" if errs else ""))
    print(f"\nresults -> {OUT}")


if __name__ == "__main__":
    main()
