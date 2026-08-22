"""Unified model client for Prometheus.

One entry point -- `complete()` -- across every provider, local or hosted.
No third-party SDKs: raw HTTP via `requests` only. That is deliberate. It
removes the openai / anthropic / google-genai SDK dependencies the existing
call sites carry, and keeps the trust surface to one file we own.

    from prometheus_llm import complete, complete_json, council, health

    r = complete("Explain X", target="openrouter:stealth/ox-alpha")
    if r: print(r.text)
    else: print(r.summary())     # failure SHAPE, not a bare verdict
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import requests

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from keys import get_key  # noqa: E402

from .registry import get_spec, parse_target, all_providers  # noqa: E402
from .types import Completion, LLMError, ProviderSpec  # noqa: E402

DEFAULT_TIMEOUT = 180
DEFAULT_MAX_TOKENS = 4096
RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}
_MAX_AUTO_EXPAND = 32768


# ---------------------------------------------------------------------------
# audit log (opt-in via PROMETHEUS_LLM_LOG=<path>)
# ---------------------------------------------------------------------------

def _audit(c: Completion, prompt_text: str) -> None:
    path = os.environ.get("PROMETHEUS_LLM_LOG")
    if not path:
        return
    rec = c.to_dict()
    rec.pop("raw", None)
    rec["ts"] = time.time()
    rec["prompt_sha1"] = hashlib.sha1(
        prompt_text.encode("utf-8", "replace")).hexdigest()
    rec["prompt_chars"] = len(prompt_text)
    if os.environ.get("PROMETHEUS_LLM_LOG_PROMPTS") == "1":
        rec["prompt"] = prompt_text
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
            fh.flush()
    except OSError:
        pass  # logging must never break a call


def _key_for(spec: ProviderSpec) -> Optional[str]:
    if not spec.requires_key or not spec.key_name:
        return None
    return get_key(spec.key_name)


def _messages(prompt: str, system: str = "",
              messages: Optional[Sequence[dict]] = None) -> list[dict]:
    if messages is not None:
        return list(messages)
    out = []
    if system:
        out.append({"role": "system", "content": system})
    out.append({"role": "user", "content": prompt})
    return out


# ---------------------------------------------------------------------------
# adapters -- each returns a Completion, never raises on HTTP failure
# ---------------------------------------------------------------------------

def _finish(spec, model, t0, **kw) -> Completion:
    return Completion(provider=spec.name, model=model,
                      latency_s=round(time.perf_counter() - t0, 2), **kw)


def _call_openai(spec, model, msgs, max_tokens, temperature, timeout, extra):
    t0 = time.perf_counter()
    headers = {"Content-Type": "application/json", **spec.extra_headers}
    key = _key_for(spec)
    if key:
        headers["Authorization"] = "Bearer " + key
    body = {"model": model, "messages": msgs,
            "max_tokens": max_tokens, "temperature": temperature}
    if extra:
        body.update(extra)
    try:
        r = requests.post(spec.base_url + "/chat/completions",
                          headers=headers, json=body, timeout=timeout)
    except requests.RequestException as e:
        return _finish(spec, model, t0, ok=False,
                       error=f"{type(e).__name__}: {e}")
    if r.status_code != 200:
        return _finish(spec, model, t0, ok=False, status=r.status_code,
                       error=r.text[:2000])
    try:
        d = r.json()
    except ValueError:
        return _finish(spec, model, t0, ok=False, status=200,
                       error="non-JSON body: " + r.text[:500])
    if isinstance(d, dict) and d.get("error"):
        return _finish(spec, model, t0, ok=False, status=200,
                       error=json.dumps(d["error"])[:2000])
    choice = (d.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    text = msg.get("content") or ""
    u = d.get("usage") or {}
    return _finish(spec, model, t0,
                   ok=bool(text.strip()), empty_content=not text.strip(),
                   text=text, reasoning=msg.get("reasoning"),
                   finish_reason=choice.get("finish_reason"),
                   model_served=d.get("model"),
                   upstream_provider=d.get("provider"),
                   prompt_tokens=u.get("prompt_tokens"),
                   completion_tokens=u.get("completion_tokens"),
                   total_tokens=u.get("total_tokens"), cost=u.get("cost"),
                   status=200, raw=d)


def _call_gemini(spec, model, msgs, max_tokens, temperature, timeout, extra):
    t0 = time.perf_counter()
    system = " ".join(m["content"] for m in msgs if m.get("role") == "system")
    contents = [{"role": "model" if m["role"] == "assistant" else "user",
                 "parts": [{"text": m["content"]}]}
                for m in msgs if m.get("role") != "system"]
    body: dict[str, Any] = {
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max_tokens,
                             "temperature": temperature},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if extra:
        body.update(extra)
    url = f"{spec.base_url}/models/{model}:generateContent"
    try:
        r = requests.post(url,
                          headers={"Content-Type": "application/json",
                                   "x-goog-api-key": _key_for(spec)},
                          json=body, timeout=timeout)
    except requests.RequestException as e:
        return _finish(spec, model, t0, ok=False,
                       error=f"{type(e).__name__}: {e}")
    if r.status_code != 200:
        return _finish(spec, model, t0, ok=False, status=r.status_code,
                       error=r.text[:2000])
    d = r.json()
    cands = d.get("candidates") or [{}]
    parts = ((cands[0].get("content") or {}).get("parts") or [])
    text = "".join(p.get("text", "") for p in parts)
    u = d.get("usageMetadata") or {}
    return _finish(spec, model, t0,
                   ok=bool(text.strip()), empty_content=not text.strip(),
                   text=text, finish_reason=cands[0].get("finishReason"),
                   model_served=d.get("modelVersion"),
                   prompt_tokens=u.get("promptTokenCount"),
                   completion_tokens=u.get("candidatesTokenCount"),
                   total_tokens=u.get("totalTokenCount"),
                   status=200, raw=d)


def _call_anthropic(spec, model, msgs, max_tokens, temperature, timeout, extra):
    t0 = time.perf_counter()
    system = " ".join(m["content"] for m in msgs if m.get("role") == "system")
    convo = [m for m in msgs if m.get("role") != "system"]
    body: dict[str, Any] = {"model": model, "max_tokens": max_tokens,
                            "temperature": temperature, "messages": convo}
    if system:
        body["system"] = system
    if extra:
        body.update(extra)
    try:
        r = requests.post(spec.base_url + "/messages",
                          headers={"Content-Type": "application/json",
                                   "x-api-key": _key_for(spec),
                                   "anthropic-version": "2023-06-01"},
                          json=body, timeout=timeout)
    except requests.RequestException as e:
        return _finish(spec, model, t0, ok=False,
                       error=f"{type(e).__name__}: {e}")
    if r.status_code != 200:
        return _finish(spec, model, t0, ok=False, status=r.status_code,
                       error=r.text[:2000])
    d = r.json()
    text = "".join(b.get("text", "") for b in (d.get("content") or [])
                   if b.get("type") == "text")
    u = d.get("usage") or {}
    return _finish(spec, model, t0,
                   ok=bool(text.strip()), empty_content=not text.strip(),
                   text=text, finish_reason=d.get("stop_reason"),
                   model_served=d.get("model"),
                   prompt_tokens=u.get("input_tokens"),
                   completion_tokens=u.get("output_tokens"),
                   status=200, raw=d)


def _call_cli(spec, model, msgs, max_tokens, temperature, timeout, extra):
    """Subscription-billed `claude -p`. Not a metered API call.

    Per feedback_loop_inference_over_api this is for AGENT work; do not use
    it for raw-model measurement -- the harness is part of what you'd measure.
    """
    t0 = time.perf_counter()
    system = " ".join(m["content"] for m in msgs if m.get("role") == "system")
    user = "\n\n".join(m["content"] for m in msgs if m.get("role") == "user")
    prompt = (system + "\n\n" + user).strip() if system else user
    cmd = ["claude", "-p", prompt]
    if model:
        cmd += ["--model", model]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, shell=False)
    except FileNotFoundError:
        return _finish(spec, model, t0, ok=False,
                       error="`claude` CLI not on PATH")
    except subprocess.TimeoutExpired:
        return _finish(spec, model, t0, ok=False,
                       error=f"CLI timeout after {timeout}s")
    text = (proc.stdout or "").strip()
    if proc.returncode != 0:
        return _finish(spec, model, t0, ok=False, status=proc.returncode,
                       error=(proc.stderr or "")[:2000])
    return _finish(spec, model, t0, ok=bool(text), empty_content=not text,
                   text=text, finish_reason="stop",
                   model_served=model or "default")


_ADAPTERS = {"openai": _call_openai, "gemini": _call_gemini,
             "anthropic": _call_anthropic, "cli": _call_cli}


# ---------------------------------------------------------------------------
# model discovery
# ---------------------------------------------------------------------------

def list_models(provider: str, timeout: int = 60) -> list[dict]:
    """List models a provider actually offers. Empirical beats hardcoded."""
    spec = get_spec(provider)
    if spec.kind == "cli":
        return []
    if spec.kind == "gemini":
        r = requests.get(spec.base_url + "/models",
                         headers={"x-goog-api-key": _key_for(spec)},
                         timeout=timeout)
        r.raise_for_status()
        return [{"id": m["name"].split("/")[-1], "ctx": None,
                 "pricing": None, "raw": m}
                for m in r.json().get("models", [])]
    headers = {}
    key = _key_for(spec)
    if spec.kind == "anthropic":
        # Anthropic authenticates with x-api-key, NOT Authorization: Bearer.
        # Sending Bearer here returns 401 for a perfectly valid key, which
        # reads as "key revoked" when it is really a header bug.
        if key:
            headers["x-api-key"] = key
        headers["anthropic-version"] = "2023-06-01"
    elif key:
        headers["Authorization"] = "Bearer " + key
    r = requests.get(spec.base_url + "/models", headers=headers,
                     timeout=timeout)
    r.raise_for_status()
    data = r.json()
    rows = data.get("data", data if isinstance(data, list) else [])
    return [{"id": m.get("id"), "ctx": m.get("context_length"),
             "pricing": m.get("pricing"), "raw": m} for m in rows]


def _resolve_model(spec: ProviderSpec, model: str) -> str:
    if model:
        return model
    if spec.default_model:
        return spec.default_model
    if spec.kind == "cli":
        return ""  # the CLI picks its own default; no model id required

    try:
        models = list_models(spec.name)
    except Exception as e:
        raise ValueError(
            f"provider {spec.name!r} has no default_model and /models "
            f"discovery failed ({type(e).__name__}: {e}). Pass an explicit "
            f"model as 'provider:model'."
        ) from e
    if not models:
        raise ValueError(f"provider {spec.name!r} returned no models")
    return models[0]["id"]


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------

def complete(prompt: str = "", *, target: str = "openrouter",
             system: str = "", messages: Optional[Sequence[dict]] = None,
             max_tokens: int = DEFAULT_MAX_TOKENS, temperature: float = 0.0,
             retries: int = 2, timeout: int = DEFAULT_TIMEOUT,
             fallback: Optional[Sequence[str]] = None,
             auto_expand: bool = True, require: bool = False,
             extra: Optional[dict] = None) -> Completion:
    """Call a model. Returns a Completion; never raises unless require=True.

    target      -- "provider" or "provider:model" (colon, since ids contain "/")
    fallback    -- further targets tried in order if this one fails
    auto_expand -- on empty content + finish_reason "length", retry once with a
                   4x token budget. Reasoning models bill thinking against
                   max_tokens while reporting reasoning_tokens=0, so an
                   under-budgeted call returns HTTP 200 with nothing in it.
    """
    chain = [target, *(fallback or [])]
    last: Optional[Completion] = None
    msgs = _messages(prompt, system, messages)
    probe_text = json.dumps(msgs)[:20000]

    for tgt in chain:
        provider, model = parse_target(tgt)
        try:
            spec = get_spec(provider)
            model = _resolve_model(spec, model)
        except Exception as e:
            last = Completion(ok=False, provider=provider, model=model,
                              error=f"{type(e).__name__}: {e}")
            continue

        adapter = _ADAPTERS[spec.kind]
        budget, attempt = max_tokens, 0
        while attempt <= retries:
            attempt += 1
            c = adapter(spec, model, msgs, budget, temperature, timeout, extra)
            c.attempts = attempt
            last = c
            if c.ok:
                _audit(c, probe_text)
                return c
            # empty content from an exhausted reasoning budget: widen once
            if (auto_expand and c.empty_content
                    and c.finish_reason == "length"
                    and budget < _MAX_AUTO_EXPAND):
                budget = min(budget * 4, _MAX_AUTO_EXPAND)
                continue
            retryable = c.status in RETRY_STATUS or (c.status is None and c.error)
            if retryable and attempt <= retries:
                time.sleep(min(2 ** attempt, 30) * (0.5 + random.random()))
                continue
            break
        if last is not None:
            _audit(last, probe_text)

    # NOT `last or ...`: Completion.__bool__ is `ok`, so a failed completion is
    # falsy and `or` would silently discard the real failure detail.
    result = last if last is not None else Completion(
        ok=False, error="no target attempted")
    if require and not result.ok:
        raise LLMError(result)
    return result


def extract_json(text: str) -> Optional[Any]:
    """Pull a JSON value out of model prose. Returns None if nothing parses."""
    if not text:
        return None
    s = text.strip()
    if s.startswith("```"):
        parts = s.split("```")
        if len(parts) > 1:
            s = parts[1]
        if s.lstrip().lower().startswith("json"):
            s = s.lstrip()[4:]
        s = s.strip()
    try:
        return json.loads(s)
    except ValueError:
        pass
    for opener, closer in (("{", "}"), ("[", "]")):
        start = s.find(opener)
        if start < 0:
            continue
        depth, in_str, esc = 0, False, False
        for i in range(start, len(s)):
            ch = s[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(s[start:i + 1])
                    except ValueError:
                        break
    return None


def complete_json(prompt: str = "", **kw) -> tuple[Optional[Any], Completion]:
    """complete() plus JSON extraction. Returns (parsed_or_None, completion)."""
    c = complete(prompt, **kw)
    return (extract_json(c.text) if c.ok else None), c


def council(prompt: str, targets: Sequence[str], *, max_workers: int = 6,
            **kw) -> dict[str, Completion]:
    """Ask several models the same thing, concurrently.

    Returns {target: Completion} including failures -- a dead provider is a
    data point, not something to silently drop.
    """
    targets = list(targets)
    out: dict[str, Completion] = {}
    if not targets:
        return out
    with ThreadPoolExecutor(max_workers=min(max_workers, len(targets))) as ex:
        futs = {ex.submit(complete, prompt, target=t, **kw): t for t in targets}
        for f in as_completed(futs):
            t = futs[f]
            try:
                out[t] = f.result()
            except Exception as e:
                out[t] = Completion(ok=False, provider=t,
                                    error=f"{type(e).__name__}: {e}")
    return {t: out[t] for t in targets if t in out}


def health(providers: Optional[Iterable[str]] = None, *,
           max_tokens: int = 2000, timeout: int = 60) -> dict[str, Completion]:
    """One real request per provider. Live/dead with evidence, not assumption."""
    names = list(providers) if providers else all_providers()
    return council("Reply with exactly the word: PONG", names,
                   max_tokens=max_tokens, timeout=timeout, retries=0)
