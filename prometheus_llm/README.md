# prometheus_llm

One model API for the whole program — hosted, local, CLI, and (later) MCP.

Replaces seven competing client implementations that grew up independently
across `apollo/`, `forge/`, `cartography/`, `agents/icarus/` and
`agents/_shared/`, plus 59 direct call sites.

**Zero third-party dependencies beyond `requests`.** No provider SDKs, no MCP
bridge, no downloaded agent framework. This was a deliberate trust decision:
the alternative was an npm/pip package exposing 70–80 tools with process-spawn
and code-exec rights over this repo. The whole transport is ~50 lines of
`requests.post` per wire format, so owning it costs less than auditing someone
else's.

## Use

```python
from prometheus_llm import complete, complete_json, council, health

r = complete("Explain X in one line", target="openrouter:stealth/ox-alpha")
print(r.text if r else r.summary())      # summary() gives the failure SHAPE

# survive a dead provider
r = complete("...", target="deepseek", fallback=["groq", "gemini"])

data, r = complete_json('Return {"a": 1} and nothing else', target="groq")

votes = council("Is P=NP?", ["openrouter", "gemini", "groq"])
```

```
python -m prometheus_llm.cli health
python -m prometheus_llm.cli providers
python -m prometheus_llm.cli models openrouter --free
python -m prometheus_llm.cli ask groq "explain X" -f gemini -v
python -m prometheus_llm.cli council "Is P=NP?" -t openrouter -t groq
```

Targets are `provider` or `provider:model`. The separator is a **colon**, not a
slash, because model ids routinely contain slashes (`stealth/ox-alpha`).

## The empty-content trap

Reasoning models emit thinking tokens that **count against `max_tokens`** while
being reported as `reasoning_tokens: 0`. Under-budget the call and you get
**HTTP 200, tokens billed, `finish_reason: "length"`, and empty content.**

Measured on `stealth/ox-alpha`, 2026-08-22. The first harness written against
it scored that as success and exited 0, because `ok` meant "HTTP 200."

Two defences are built in:

- `Completion.ok` means **usable content came back**, never merely HTTP 200.
  `empty_content` is a distinct flag so the shape stays legible.
- `complete(auto_expand=True)` (default) retries once at a 4× budget when it
  sees empty content with `finish_reason="length"`.

This generalizes: any metric whose success condition is "the call returned"
will score a payload-shaped failure as a pass. See
`feedback_measurement_carries_its_answer`.

## Raw model vs agent

Per `feedback_loop_inference_over_api`:

- **RAW-MODEL measurement** → an HTTP provider. No agent harness in the path;
  the harness is otherwise part of what you are measuring.
- **AGENT work** → `claude_cli` (subscription-billed `claude -p`). Never use it
  for raw-model measurement.

## Measured provider state — 2026-08-22

Produced by `python -m prometheus_llm.cli health`. Re-run it rather than
trusting this table; it decays.

| provider     | state | latency | notes |
|--------------|-------|---------|-------|
| `openrouter` | LIVE  | 10.5s   | `stealth/ox-alpha`, 1M ctx, cost 0. 27 free models on this key. |
| `groq`       | LIVE  | 0.55s   | `openai/gpt-oss-120b`. Fastest hosted option. |
| `nvidia`     | LIVE  | 0.45s   | `meta/llama-3.1-8b-instruct`. |
| `gemini`     | LIVE  | 2.1s    | `gemini-3.6-flash`. Bursty free tier — retry is mandatory. |
| `ollama`     | LIVE  | 2.6s    | Local. Only `qwen2.5-coder:14b` pulled; ~48s cold, ~2.6s warm. |
| `claude_cli` | LIVE  | 4.8s    | Subscription. Agent work only. |
| `anthropic`  | DEAD  | —       | HTTP 401 Unauthorized — key invalid/revoked, **not** a credit problem. |
| `openai`     | DEAD  | —       | HTTP 429, no credits. Key valid. |
| `deepseek`   | DEAD  | —       | HTTP 402, insufficient balance. |
| `cerebras`   | DEAD  | —       | HTTP 402, payment required. Key valid, unfunded. |

Two of those verdicts were wrong on the first pass and were caused by this
package, not the providers: `nvidia` 404'd because model discovery picked
first-in-list (`01-ai/yi-large`, uninvokable on this account), and `claude_cli`
failed because the resolver demanded a model id the CLI does not need. Both are
fixed and both defaults are now pinned. **Do not trust first-in-list model
discovery** — Groq's catalog mixes chat models with Whisper and prompt-guard
classifiers.

## Adding a provider

Add one `ProviderSpec` to `registry.py`. Nothing else changes. If it speaks
OpenAI-compatible `/chat/completions` — most do, including every local server —
use `kind="openai"` and only `base_url` plus `key_name` are needed.

Keys resolve through the repo-root `keys.py`, which searches both
`D:\Prometheus\.env` and `D:\Prometheus\agents\eos\.env`.

## Cross-machine caveat — `keys.py` is gitignored

`keys.py` is excluded from version control (`.gitignore:9`), so the change that
teaches it to search `agents/eos/.env` **will not propagate by git**. On any
other machine this package will fail to resolve OPENROUTER / GROQ / CEREBRAS /
NVIDIA until `keys.py` there is updated by hand.

The required change, for reproducing it elsewhere:

```python
_ROOT = Path(__file__).resolve().parent
_ENV_FILES = [_ROOT / ".env", _ROOT / "agents" / "eos" / ".env"]
_ENV_FILE = _ENV_FILES[0]          # back-compat for existing callers
```

`_load_env_file()` merges every file in `_ENV_FILES` order, first definition of
a name wins, so the repo-root `.env` keeps precedence. `_KEY_NAMES` also gains
OPENROUTER, GROQ, CEREBRAS, NVIDIA, TAVILY, SERPER, S2, GITHUB, GOOGLE_AI.

A second key loader is deliberately NOT built here — CLAUDE.md makes `keys.py`
the single path for key loading.

**Applied on M1 2026-08-22, confirmed working.** M1 holds **four** `.env` files,
not two. The two extra were deliberately left OUT of `_ENV_FILES`:

* `googleAI/.env` — only `GEMINI_API_KEY`, which the repo-root `.env` already
  defines and wins on by ordering. Adds zero names.
* `archive/bitfrost-core/.../.env` — only `GITHUB_MODELS_KEY`, archived, and it
  has no `_KEY_NAMES` entry.

So `_ENV_FILES` is byte-identical on M1 and M2 — no machine-specific path is
needed, which is the outcome worth preserving. If a future machine needs an
extra path, add it here rather than silently diverging.

On M1 the change took `get_key()` from **6 resolvable keys to 15**. Note that
`NVIDIA` was already declared in `_KEY_NAMES` before the change but its key
lives in `agents/eos/.env`, so `get_key("NVIDIA")` was **failing silently** —
a declared-but-unresolvable name is worse than a missing one, because callers
read the declaration as availability.

## Env overrides

```
PROMETHEUS_LLM_<PROVIDER>_MODEL      pin a model without editing the registry
PROMETHEUS_LLM_<PROVIDER>_BASE_URL   repoint a local endpoint
PROMETHEUS_LLM_LOG=<path.jsonl>      append per-call usage/latency records
PROMETHEUS_LLM_LOG_PROMPTS=1         include prompt text (off by default;
                                     otherwise only a sha1 and char count)
```

## Tests

```
python -m unittest discover -s prometheus_llm/tests -t . -v
```

30 offline tests, no network and no keys required. They caught a real bug on
first run: `result = last or Completion(...)` silently discarded every failure,
because `Completion.__bool__` returns `ok` and a failed completion is falsy.
Keep that hazard in mind when touching this package — `or` and `Completion` do
not mix.

## Not yet done

- MCP transport (`kind="mcp"`) — the registry has room; no adapter yet.
- Streaming. Every call is currently blocking.
- The 59 legacy call sites still use their own clients. Migration is staged,
  not bulk — see the migration plan.
