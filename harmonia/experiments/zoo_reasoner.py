"""Model-AGNOSTIC reasoner adapter for the reasoning-ladder model zoo (EXPERIMENTAL).

`make_zoo_reasoner(model, provider, ...) -> fn(probe) -> (answer, trace)`,
matching the harness interface that `reasoning_phase0.grade` consumes.

WHY THIS EXISTS (vs `reasoners_llm.make_llm_reasoner` / `make_opus_reasoner`):
  * `make_opus_reasoner` is Anthropic-only and uses STRUCTURED OUTPUTS (JSON
    schema enforced by the API) — not available on the open-weight zoo.
  * `make_llm_reasoner` runs the llm_cascade, which auto-FALLS-BACK across
    providers. For a model x tier matrix we must PIN one model on one provider —
    a fallback silently mislabels which examinee answered. This adapter calls a
    SINGLE OpenAI-compatible endpoint with NO fallback.

It REUSES the established free-text-JSON path from reasoners_llm so grading is
byte-identical to the cascade reasoner:
    _prompt_for           — kind-specific NL statement + strict JSON contract
    parse_json_blob       — tolerant ```-fence / outermost-{...} parser
    map_to_answer_and_trace — deterministic JSON -> (answer, trace) mapping
Trace fields are therefore identical, so harness grade() works unchanged.

Frontier quality is IRRELEVANT here — the zoo's job is COVERAGE across many
models so the basis factor-analysis has examinee variance. Free-text JSON is
lossier than structured outputs; that loss is itself a measured quantity
(per-model parse-failure rate, recorded in the call_log).

SECURITY: credentials flow through os.environ (cascade plane, auto-loaded by
llm_cascade) or keys.get_key (keys plane). This file never reads key files and
never prints/logs key values.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"
_EXPERIMENTS = Path(__file__).resolve().parent
for _p in (str(_REPO_ROOT), str(_SCRIPTS), str(_EXPERIMENTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Side effect: auto-loads agents/eos/.env into os.environ (cascade-plane keys).
import llm_cascade  # noqa: E402,F401
from keys import get_key  # noqa: E402

# Reuse the EXACT prompt + parse + map path the cascade reasoner uses.
from reasoners_llm import (  # noqa: E402
    _SYSTEM,
    _prompt_for,
    parse_json_blob,
    map_to_answer_and_trace,
)

_UA = llm_cascade._USER_AGENT
_SSL = llm_cascade._get_ssl_context()

# ----------------------------------------------------------------- providers
# How to reach each provider over its OpenAI-compatible /chat/completions:
#   endpoint  — base URL (we append /chat/completions)
#   plane     — "cascade" (key in os.environ[env_key]) | "keys" (get_key(name))
# Endpoints/env-var names mirror llm_cascade + keys.py so nothing new is invented.
PROVIDERS: dict[str, dict] = {
    "Cerebras":     {"endpoint": "https://api.cerebras.ai/v1",
                     "plane": "cascade", "env_key": "CEREBRAS_API_KEY"},
    "Groq":         {"endpoint": "https://api.groq.com/openai/v1",
                     "plane": "cascade", "env_key": "GROQ_API_KEY"},
    "GitHubModels": {"endpoint": "https://models.inference.ai.azure.com",
                     "plane": "cascade", "env_key": "GITHUB_TOKEN"},
    "NVIDIA":       {"endpoint": os.environ.get("NVIDIA_API_ENDPOINT",
                                                 "https://integrate.api.nvidia.com/v1"),
                     "plane": "cascade", "env_key": "NVIDIA_API_KEY"},
    "DeepSeek":     {"endpoint": "https://api.deepseek.com/v1",
                     "plane": "keys", "get_key_name": "DEEPSEEK"},
    "OpenAI":       {"endpoint": "https://api.openai.com/v1",
                     "plane": "keys", "get_key_name": "OPENAI"},
    "Gemini":       {"endpoint": "https://generativelanguage.googleapis.com/v1beta/openai",
                     "plane": "keys", "get_key_name": "GEMINI"},
}


def _resolve_key(provider: str) -> Optional[str]:
    """Return the credential for a provider, or None. Never prints the value."""
    cfg = PROVIDERS.get(provider)
    if not cfg:
        return None
    if cfg["plane"] == "cascade":
        return os.environ.get(cfg["env_key"])
    try:
        return get_key(cfg["get_key_name"])
    except Exception:
        return None


def _call_openai_compatible(endpoint: str, key: str, model: str, prompt: str,
                            system: str, max_tokens: int, temperature: float,
                            timeout: int, retries: int = 3) -> tuple[str, Optional[str]]:
    """Single OpenAI-compatible chat call. Returns (text, error).

    `text` is content OR reasoning_content (some open-weight reasoning models —
    gpt-oss, qwen3 — emit only reasoning_content for short answers). `error` is
    None on success, else a short stable tag (no key, no full body).

    Bounded exponential backoff on recoverable TRANSPORT failures (HTTP 429 /
    5xx). NOTE the error taxonomy distinguishes TRANSPORT errors
    (http_error:429, call_exception:TimeoutError) from CONTENT errors
    (no_choices, empty_content) — and neither is the same as a downstream JSON
    PARSE error (those are tagged by parse_json_blob). The scoping doc reports
    these three classes separately; conflating them inflates the apparent
    'parse-failure' rate with rate-limit noise."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode("utf-8")

    last_err = None
    for attempt in range(retries):
        req = urllib.request.Request(
            f"{endpoint}/chat/completions", data=payload,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}",
                     "User-Agent": _UA, "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=_SSL) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = f"http_error:{e.code}"
            if e.code == 429 or 500 <= e.code < 600:   # recoverable: back off
                time.sleep(min(2 ** attempt, 8))
                continue
            return "", last_err                         # 4xx (auth/not-found): no retry
        except Exception as e:
            last_err = f"call_exception:{type(e).__name__}"
            time.sleep(min(2 ** attempt, 8))
            continue
        choices = data.get("choices", [])
        if not choices:
            return "", "no_choices"
        msg = choices[0].get("message", {})
        text = (msg.get("content") or msg.get("reasoning_content") or "").strip()
        if not text:
            return "", "empty_content"
        return text, None
    return "", (last_err or "unknown_transport_error")


def make_zoo_reasoner(model: str, provider: str, temperature: float = 0.0,
                      max_tokens: int = 1200, timeout: int = 120,
                      call_log: Optional[list] = None,
                      prompt_suffix: Optional[str] = None):
    """Return `fn(probe) -> (answer, trace)` PINNED to one model on one provider.

    No cross-provider fallback (that would mislabel the examinee). On any failure
    the reasoner returns the same (answer, trace) shape `map_to_answer_and_trace`
    produces for an unparsed response — so the harness still grades it (as a
    failure SHAPE) instead of crashing.

    `call_log`, if given, gets one dict appended per call:
        {tier, version, kind, model, provider, parse_error}
    where parse_error is None on a clean parse, else a stable tag. This is the
    per-model parse-failure stream the scoping doc quantifies.

    max_tokens default 1200 (> the cascade reasoner's 900): some open-weight
    reasoning models burn budget on <think> before emitting JSON; too low a cap
    truncates the JSON and inflates the parse-failure rate spuriously.

    `prompt_suffix`, if given, is appended to the user prompt (after a blank
    line). Used by run_zoo_matrix for a SINGLE bounded re-ask after a genuine
    JSON parse failure ("return ONLY the JSON object") — it does NOT change the
    statement or the JSON contract, only nudges format compliance. Leaving it
    None reproduces the exact base prompt, so the first attempt is unchanged.
    """
    cfg = PROVIDERS.get(provider)
    endpoint = cfg["endpoint"] if cfg else None
    key = _resolve_key(provider)
    tag = f"{provider}:{model}"

    def _log(p, perr):
        if call_log is not None:
            call_log.append({"tier": p.tier, "version": p.version, "kind": p.kind,
                             "model": model, "provider": provider, "parse_error": perr})

    def reasoner(p):
        if endpoint is None:
            perr = "unknown_provider"
            ans, tr = map_to_answer_and_trace(p, None, perr, "")
            tr["_provider"] = tag
            _log(p, perr)
            return ans, tr
        if not key:
            perr = "no_key"
            ans, tr = map_to_answer_and_trace(p, None, perr, "")
            tr["_provider"] = tag
            _log(p, perr)
            return ans, tr

        prompt = _prompt_for(p)
        if prompt_suffix:
            prompt = prompt + "\n\n" + prompt_suffix
        text, call_err = _call_openai_compatible(
            endpoint, key, model, prompt, _SYSTEM, max_tokens, temperature, timeout)

        if call_err is not None:
            ans, tr = map_to_answer_and_trace(p, None, call_err, text)
            tr["_provider"] = tag
            _log(p, call_err)
            return ans, tr

        parsed, perr = parse_json_blob(text)
        ans, tr = map_to_answer_and_trace(p, parsed, perr, text)
        tr["_provider"] = tag
        _log(p, perr)
        return ans, tr

    return reasoner


# ----------------------------------------------------------------- self-test
if __name__ == "__main__":
    # Tiny offline-safe smoke: build a reasoner for one reachable provider and
    # run a single R0 probe. Skips cleanly if nothing is reachable.
    import random
    from reasoning_phase0 import gen_R0, grade

    rng = random.Random(20260529)
    probe = gen_R0(rng)[0]  # an R0 clean linear probe

    for prov, mdl in [("Groq", "llama-3.1-8b-instant"),
                      ("NVIDIA", "meta/llama-3.1-8b-instruct"),
                      ("OpenAI", "gpt-4o-mini")]:
        if not _resolve_key(prov):
            print(f"[skip] {prov}: no key")
            continue
        log = []
        r = make_zoo_reasoner(mdl, prov, call_log=log)
        ans, tr = r(probe)
        v, ok = grade(probe, ans, tr)
        print(f"[{prov}/{mdl}] ans={ans} ok={ok} parse_err={log[0]['parse_error']}")
        break
