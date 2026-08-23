"""prometheus_llm -- one model API for the whole Prometheus program.

Replaces the seven competing llm_client implementations that grew up across
apollo/, forge/, cartography/, agents/icarus/ and agents/_shared/.

Zero third-party dependencies beyond `requests`. No provider SDKs, no MCP
bridge, no downloaded agent framework -- the trust surface is code we own.

Quick start:

    from prometheus_llm import complete, complete_json, council, health

    r = complete("Explain X in one line", target="openrouter:stealth/ox-alpha")
    print(r.text if r else r.summary())

    data, r = complete_json('Return {"a": 1} and nothing else',
                            target="openrouter")

    votes = council("Is P=NP?", ["openrouter", "gemini", "groq"])

    for name, c in health().items():
        print(name, "LIVE" if c else "DEAD", c.summary())

Targets are "provider" or "provider:model" -- colon-delimited, because model
ids routinely contain "/" (e.g. "stealth/ox-alpha").

See README.md in this package for the empty-content trap and the
raw-model vs agent split.
"""

from .client import (
    complete,
    complete_json,
    council,
    extract_json,
    health,
    list_models,
)
from .registry import all_providers, get_spec, openai_compatible, parse_target
from .types import Completion, LLMError, ProviderSpec

__all__ = [
    "complete",
    "complete_json",
    "council",
    "extract_json",
    "health",
    "list_models",
    "all_providers",
    "openai_compatible",
    "get_spec",
    "parse_target",
    "Completion",
    "ProviderSpec",
    "LLMError",
]

__version__ = "0.1.0"
