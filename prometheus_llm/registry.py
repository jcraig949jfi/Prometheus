"""Provider registry for prometheus_llm.

Adding a provider = adding one ProviderSpec here. No call site changes.

Defaults are deliberately sparse: where a provider's current model ids are not
known-good, `default_model` is left empty and resolved at runtime from the
provider's own /models endpoint. Inventing model ids that 404 later is worse
than one extra discovery call.

Overrides (env):
    PROMETHEUS_LLM_<PROVIDER>_MODEL      e.g. PROMETHEUS_LLM_GROQ_MODEL
    PROMETHEUS_LLM_<PROVIDER>_BASE_URL   e.g. PROMETHEUS_LLM_OLLAMA_BASE_URL
"""

from __future__ import annotations

import os
from typing import Optional

from .types import ProviderSpec

# ---------------------------------------------------------------------------
# OpenAI-compatible providers. These all speak POST {base}/chat/completions
# with {"model", "messages", "max_tokens", "temperature"}. That covers the
# large majority of the shelf, which is why the layer is thin.
# ---------------------------------------------------------------------------

_SPECS: dict[str, ProviderSpec] = {
    "openrouter": ProviderSpec(
        name="openrouter", kind="openai",
        base_url="https://openrouter.ai/api/v1",
        key_name="OPENROUTER",
        default_model="stealth/ox-alpha",
        notes="Aggregator. 27 zero-cost models on this key as of 2026-08-22.",
        extra_headers={"HTTP-Referer": "https://github.com/prometheus",
                       "X-Title": "Prometheus"},
    ),
    "deepseek": ProviderSpec(
        name="deepseek", kind="openai",
        base_url="https://api.deepseek.com/v1",
        key_name="DEEPSEEK", default_model="deepseek-chat",
        notes="DEAD 2026-08-22: HTTP 402 Insufficient Balance (unchanged since 2026-08-12).",
    ),
    "groq": ProviderSpec(
        name="groq", kind="openai",
        base_url="https://api.groq.com/openai/v1",
        key_name="GROQ", default_model="openai/gpt-oss-120b",
        notes="Fast inference, free tier. Catalog mixes chat with audio "
              "(whisper/orpheus) and classifiers (prompt-guard), so do NOT "
              "trust first-in-list discovery here.",
    ),
    "cerebras": ProviderSpec(
        name="cerebras", kind="openai",
        base_url="https://api.cerebras.ai/v1",
        key_name="CEREBRAS", default_model="",
        notes="DEAD 2026-08-22: HTTP 402 payment_required. Key valid, unfunded.",
    ),
    "nvidia": ProviderSpec(
        name="nvidia", kind="openai",
        base_url="https://integrate.api.nvidia.com/v1",
        key_name="NVIDIA", default_model="meta/llama-3.1-8b-instruct",
        notes="NIM. /models lists 102 ids but most 404 for this account "
              "(per-account function routing). Verified live 2026-08-22: "
              "meta/llama-3.1-8b-instruct (0.5s), "
              "deepseek-ai/deepseek-v4-flash-0731 (7s).",
    ),
    "openai": ProviderSpec(
        name="openai", kind="openai",
        base_url="https://api.openai.com/v1",
        key_name="OPENAI", default_model="",
        notes="DEAD 2026-08-22: HTTP 429 no credits remaining. Key valid, unfunded. Catalog lists 126 models but none are callable.",
    ),
    "ollama": ProviderSpec(
        name="ollama", kind="openai",
        base_url="http://localhost:11434/v1",
        key_name=None, requires_key=False, default_model="",
        notes="LIVE 2026-08-22 via installed tags. Only qwen2.5-coder:14b is pulled. First call is slow (~48s cold load), ~2.6s warm.",
    ),
    # --- non-OpenAI wire formats -------------------------------------------
    "gemini": ProviderSpec(
        name="gemini", kind="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        key_name="GEMINI", default_model="gemini-3.6-flash",
        notes="LIVE 2026-08-22 (gemini-3.6-flash, 2.1s). Free tier is bursty: 503s expected, retry is mandatory.",
    ),
    "anthropic": ProviderSpec(
        name="anthropic", kind="anthropic",
        base_url="https://api.anthropic.com/v1",
        key_name="CLAUDE", default_model="",
        notes="DEAD 2026-08-22, CONFIRMED ON BOTH M1 AND M2: HTTP 400 credit balance too low. The key is VALID and unfunded -- verified with a deliberately-corrupted-key control, which returns 401 while the real key returns 400, so 400-vs-401 discriminates unfunded from revoked. The earlier 401 reading was a header bug in list_models (Bearer instead of x-api-key), NOT a revoked key; the 2026-08-12 low-credit reading was right all along. Two Anthropic accounts exist, but M1 and M2 resolve the SAME credential (matching org id and key fingerprint), so this is one account state, not two -- the second account is configured on neither machine. Use claude_cli for Claude access (separate subscription auth, separate billing).",
    ),
    "claude_cli": ProviderSpec(
        name="claude_cli", kind="cli",
        key_name=None, requires_key=False, default_model="",
        notes="Subscription-billed `claude -p`. Per feedback_loop_inference_"
              "over_api: use for AGENTS, never for raw-model measurement.",
    ),
}


def _env(provider: str, field: str) -> Optional[str]:
    return os.environ.get(f"PROMETHEUS_LLM_{provider.upper()}_{field}")


def get_spec(provider: str) -> ProviderSpec:
    """Return the spec for `provider`, with env overrides applied."""
    key = provider.strip().lower()
    if key not in _SPECS:
        raise ValueError(
            f"Unknown provider {provider!r}. Known: {sorted(_SPECS)}"
        )
    spec = _SPECS[key]
    base = _env(key, "BASE_URL")
    model = _env(key, "MODEL")
    if base or model:
        spec = ProviderSpec(**{**spec.__dict__,
                               "base_url": base or spec.base_url,
                               "default_model": model or spec.default_model})
    return spec


def all_providers() -> list[str]:
    return sorted(_SPECS)


def openai_compatible() -> list[str]:
    return sorted(n for n, s in _SPECS.items() if s.kind == "openai")


def parse_target(target: str) -> tuple[str, str]:
    """Split a "provider:model" target.

    Colon-delimited, because model ids routinely contain "/"
    (e.g. "stealth/ox-alpha"), so "/" cannot be the separator.

        "openrouter:stealth/ox-alpha" -> ("openrouter", "stealth/ox-alpha")
        "groq"                        -> ("groq", "")   # use provider default
    """
    if ":" in target:
        provider, model = target.split(":", 1)
        return provider.strip().lower(), model.strip()
    return target.strip().lower(), ""
