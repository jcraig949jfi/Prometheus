"""Normalized result and provider types for prometheus_llm.

Every provider, however weird its wire format, is flattened into `Completion`.
Call sites should never branch on provider-specific response shapes.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class Completion:
    """One model response, normalized across every provider.

    `ok` means USABLE CONTENT came back -- not merely HTTP 200. A reasoning
    model that spends its whole token budget thinking returns HTTP 200 with
    empty content; that is a failure and `ok` is False with `empty_content`
    set. See prometheus_llm/README.md "The empty-content trap".
    """

    ok: bool
    text: str = ""
    reasoning: Optional[str] = None

    provider: str = ""
    model: str = ""
    model_served: Optional[str] = None
    upstream_provider: Optional[str] = None

    finish_reason: Optional[str] = None
    empty_content: bool = False

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost: Optional[float] = None

    latency_s: float = 0.0
    attempts: int = 1
    status: Optional[int] = None
    error: Optional[str] = None

    raw: Optional[dict] = field(default=None, repr=False)

    def __bool__(self) -> bool:
        return self.ok

    def to_dict(self, include_raw: bool = False) -> dict:
        d = asdict(self)
        if not include_raw:
            d.pop("raw", None)
        return d

    def summary(self) -> str:
        if self.ok:
            return (f"{self.provider}:{self.model} ok "
                    f"{self.latency_s:.2f}s "
                    f"tok={self.prompt_tokens}/{self.completion_tokens} "
                    f"finish={self.finish_reason}")
        if self.empty_content:
            n = len(self.reasoning or "")
            return (f"{self.provider}:{self.model} EMPTY_CONTENT "
                    f"{self.latency_s:.2f}s finish={self.finish_reason} "
                    f"reasoning_chars={n} (raise max_tokens)")
        return (f"{self.provider}:{self.model} FAIL status={self.status} "
                f"{self.latency_s:.2f}s :: {(self.error or '')[:200]}")


@dataclass
class ProviderSpec:
    """How to reach one provider.

    kind dispatches the adapter:
      "openai"    -- OpenAI-compatible /chat/completions (most providers)
      "gemini"    -- Google generativeLanguage generateContent
      "anthropic" -- Anthropic /v1/messages
      "cli"       -- local subprocess (claude -p, subscription-billed)
    """

    name: str
    kind: str
    base_url: str = ""
    key_name: Optional[str] = None      # friendly name for keys.get_key()
    default_model: str = ""
    requires_key: bool = True
    notes: str = ""
    extra_headers: dict[str, str] = field(default_factory=dict)


class LLMError(RuntimeError):
    """Raised only when a call site opts into raising via require=True."""

    def __init__(self, completion: "Completion"):
        self.completion = completion
        super().__init__(completion.summary())
