# Model Zoo — Reasoning-Ladder Basis Study (scoping, 2026-05-29)

> **Status: EXPERIMENTAL / CHIP-AWAY.** Inventory + agnostic adapter + smoke only.
> NOT a full run. The four frontier reviewers all named a model zoo as the prerequisite
> to answer **basis-vs-ladder** (the 3-model frontier trio is too saturated — variance
> lives in the weaker models). This doc records what is reachable, the adapter design, the
> measured parse-failure shape, and a concrete plan to build the model × tier matrix.
>
> Files (all under `D:\Prometheus\harmonia\experiments\`):
> - `zoo_inventory.py` — reachability prober (1 cheap call/model), writes `zoo_inventory_result.json`
> - `zoo_reasoner.py` — `make_zoo_reasoner(model, provider, ...)` model-agnostic adapter (now takes `prompt_suffix` for re-ask)
> - `zoo_smoke.py` — adapter smoke across 3 models on R0/R1/R2
> - `run_zoo_matrix.py` — **resumable, rate-limit-aware matrix runner (attacks the §5 blocker).** Per-provider
>   pacing (min-interval + sliding-window RPM), append-only JSONL checkpoint (auto-resume, survives a 429 storm),
>   bounded single re-ask on genuine parse-fail, per-examinee parse-rate gate (flag/`--drop-degraded`), NVIDIA
>   cold-start warm-up. Transport/parse/content cells recorded but EXCLUDED from accuracy (only clean-parse cells
>   scored — same discipline as the other runners). Scheduler is dependency-injected (clock/sleep/factory/grader).
> - `test_zoo_matrix.py` — 38 offline tests (taxonomy, fake-clock pacing, resume, gate, re-ask); no network.
>   Run: `python harmonia/experiments/run_zoo_matrix.py --dry-run` (offline mock) | `--n 3` (LIVE) | `--with-anchors`.
>
> Per the synthesis (`reasoning_ladder_frontier_synthesis_2026-05-29.md` §3): at N=3 a
> CDM/IRT is circular and under-powered; the zoo is what unlocks the decisive test —
> **a multi-axis model predicting HELD-OUT FAMILY performance better than a rank-1 ladder.**

---

## 1. Reachable-model inventory (probed 2026-05-29, 1 call/model)

Two credential planes, kept separate on purpose:
- **cascade plane** — `scripts/llm_cascade` auto-loads `agents/eos/.env`: Cerebras, Groq, GitHub Models, NVIDIA.
- **keys plane** — `keys.get_key` reads repo `.env`: OpenAI, DeepSeek, Gemini, Anthropic.

**18 of 24 candidate models reachable, across 4 live providers** (Cerebras, Groq, NVIDIA,
OpenAI). By tier: **11 mid, 6 open-small, 1 frontier.** No model on any provider exposes a
native structured-output / JSON-schema API on its OpenAI-compatible endpoint — **only the
Anthropic path (`reasoners_llm.make_opus_reasoner`) gets schema-enforced JSON.** The zoo is
therefore entirely on the free-text-JSON path (which is exactly why we measure parse loss).

| Model | Provider | Plane | Tier | Reachable | Latency(s) | Structured |
|---|---|---|---|---|---|---|
| `gpt-oss-120b` | Cerebras | cascade | mid | yes | 1.38 | no |
| `zai-glm-4.7` | Cerebras | cascade | mid | yes | 0.47 | no |
| `llama-3.3-70b-versatile` | Groq | cascade | mid | yes | 0.12 | no |
| `llama-3.1-8b-instant` | Groq | cascade | open-small | yes | 0.23 | no |
| `meta-llama/llama-4-scout-17b-16e-instruct` | Groq | cascade | mid | yes | 0.27 | no |
| `qwen/qwen3-32b` | Groq | cascade | mid | yes | 0.19 | no |
| `openai/gpt-oss-20b` | Groq | cascade | open-small | yes | 0.10 | no |
| `gpt-4o-mini` | GitHubModels | cascade | mid | **no (429)** | 0.22 | no |
| `nvidia/nemotron-3-super-120b-a12b` | NVIDIA | cascade | mid | yes | 1.29 | no |
| `nvidia/llama-3.3-nemotron-super-49b-v1.5` | NVIDIA | cascade | mid | yes | 0.39 | no |
| `meta/llama-3.3-70b-instruct` | NVIDIA | cascade | mid | yes | 15.46 | no |
| `meta/llama-3.1-8b-instruct` | NVIDIA | cascade | open-small | yes | 0.32 | no |
| `meta/llama-3.2-3b-instruct` | NVIDIA | cascade | open-small | yes | 0.20 | no |
| `qwen/qwen3-next-80b-a3b-instruct` | NVIDIA | cascade | mid | yes | 0.36 | no |
| `google/gemma-3-12b-it` | NVIDIA | cascade | open-small | **no (404)** | 0.09 | no |
| `mistralai/mistral-7b-instruct-v0.3` | NVIDIA | cascade | open-small | yes | 0.29 | no |
| `microsoft/phi-4-mini-instruct` | NVIDIA | cascade | open-small | **no (timeout)** | 40.05 | no |
| `nvidia/nvidia-nemotron-nano-9b-v2` | NVIDIA | cascade | open-small | **no (timeout)** | 40.05 | no |
| `deepseek-chat` | DeepSeek | keys | mid | **no (402 balance)** | 0.65 | no |
| `gpt-4o-mini` | OpenAI | keys | mid | yes | 1.62 | no |
| `gpt-4.1-mini` | OpenAI | keys | mid | yes | 0.61 | no |
| `gpt-4.1-nano` | OpenAI | keys | open-small | yes | 0.26 | no |
| `gpt-4o` | OpenAI | keys | frontier | yes | 1.96 | no |
| `gemini-2.0-flash` | Gemini | keys | mid | **no (429)** | 0.16 | no |

### Failure classes (the gradient, not just a verdict)
- **404 / decommissioned IDs** — provider catalogs drift; the FIRST inventory run 404'd on
  *all* Cerebras IDs and several Groq IDs (stale model names). Fix = list `/models` first
  (done; live IDs above). **Always re-list before a full run.** `gemma-3-12b-it` 404s on
  NVIDIA (NIM exposes `gemma-3-4b-it`/`gemma-4-31b-it` instead).
- **Transport (429 / timeout)** — GitHub Models and Gemini free tiers are rate-capped to
  near-zero throughput right now. Two NVIDIA small models timed out at 40s (cold-start /
  capacity), but warm up on retry. **These are infra, NOT adapter, failures** and are
  counted separately from genuine parse failures.
- **402 Insufficient Balance** — DeepSeek key is out of credit (hard blocker, needs top-up).
- **`reasoning_content`-only 200s** — `gpt-oss-120b`/`gpt-oss-20b`/`qwen3-32b` sometimes put
  the whole answer in `reasoning_content` with empty `content`. The adapter reads
  content-OR-reasoning_content (same as the cascade), so these are handled.

**The deep bench is NVIDIA NIM:** its `/models` endpoint lists ~76 models spanning Llama
(1B→90B), Qwen (32B→480B), Gemma, Mistral (7B→675B), Phi, Nemotron (4B→340B), gpt-oss,
DeepSeek — i.e. a full size-stratified open-weight ladder from a single key. **NVIDIA alone
can supply 20–40 examinees** once cold-start timeouts are handled.

---

## 2. Adapter design — `zoo_reasoner.make_zoo_reasoner(model, provider, ...)`

Returns `fn(probe) -> (answer, trace)`, matching the harness interface so
`reasoning_phase0.grade` runs **unchanged**.

**Why a new adapter and not the existing reasoners:**
- `reasoners_llm.make_opus_reasoner` is Anthropic-only (structured outputs) — open-weight
  models can't use it.
- `reasoners_llm.make_llm_reasoner` runs the **cascade with auto-fallback** — it silently
  switches providers on failure, which would mislabel *which examinee answered*. A
  model × tier matrix needs each cell pinned to one model. `make_zoo_reasoner` calls a
  **single OpenAI-compatible endpoint with no fallback.**

**Reuse (the whole point — identical grading to the cascade reasoner):** it imports and
calls, from `reasoners_llm`, the established free-text-JSON path:
`_SYSTEM`, `_prompt_for` (kind-specific NL statement + strict JSON contract),
`parse_json_blob` (```-fence/outermost-`{...}` tolerant parser),
`map_to_answer_and_trace` (deterministic JSON → answer + trace fields). Trace fields are
byte-identical, so the grader's `domain_constraints_detected`, `rejected_extraneous`,
`overgeneralized`, etc. all populate as before. **`reasoning_phase0.py` and
`reasoners_llm.py` are NOT edited — only imported from.**

**Provider table** mirrors `llm_cascade._build_providers()` + `keys._KEY_NAMES` (endpoints
and env-var names; nothing new invented). `_resolve_key(provider)` returns the credential
from `os.environ` (cascade plane) or `get_key` (keys plane) and **never returns/prints the
value**.

**Robustness choices:**
- `max_tokens` default **1200** (> the cascade reasoner's 900): reasoning models
  (`qwen3-32b`, `gpt-oss`) burn budget on `<think>` before the JSON; too low a cap
  truncates the JSON and inflates the parse-failure rate spuriously.
- Bounded exponential backoff (3 tries, ≤8s) on **429 / 5xx only**; 4xx (auth/not-found) no
  retry.
- **Three-class error taxonomy**, each surfaced separately in `call_log`:
  1. **transport** (`http_error:*`, `call_exception:*`, `no_key`, `unknown_provider`),
  2. **content** (`no_choices`, `empty_content`),
  3. **genuine JSON parse** (`empty_response`, `no_json_object`, `json_decode_error:*`,
     `unbalanced_braces` from `parse_json_blob`).
  Conflating these (the first smoke did) inflates "parse-failure" with rate-limit noise.
  **Only class 3 measures the free-text-vs-structured loss the synthesis cares about.**
- On any failure the reasoner returns the same `(answer, trace)` shape
  `map_to_answer_and_trace` produces for an unparsed response — so the harness grades it as
  a failure SHAPE rather than crashing (consistent with the failure-signature doctrine).

---

## 3. Smoke result + parse-failure rates

`zoo_smoke.py`, 12 probes (R0/R1/R2 × 4 versions), 3 models, same probes for all:

| Model | Tier | Acc | Genuine JSON parse-fail | Transport fail | Content-empty |
|---|---|---|---|---|---|
| `NVIDIA/meta/llama-3.1-8b-instruct` | open-small | 0.50 | **0%** (0/12) | 0 | 0 |
| `NVIDIA/meta/llama-3.3-70b-instruct` | mid | 0.58 | **0%** (0/12) | 0 | 0 |
| `Groq/llama-3.1-8b-instant` | open-small | 0.42 | **8%** (1/12, one `json_decode_error`) | 0 | 0 |

**SMOKE PASS** — the adapter reached, parsed, mapped, and graded all three models;
genuine JSON parse-failure ≤ 8%. Accuracy is incidental (tiny N, deliberately weak models);
the load-bearing numbers are reachability + parse-failure rate.

**Failure-shape note (not a verdict):** all three models scored **R2 = 0/4** — the
sqrt-extraneous-root tier. That is exactly the *execution-discipline-under-legality-pressure*
axis the synthesis flags (these weak models square both sides and keep the extraneous root).
This is the predicted weak-model failure shape, not an adapter bug — and it's the first
hint that the variance the basis study needs is **already visible** at the bottom of the
zoo, where the frontier trio is saturated.

**Quantified parse-loss expectation for the full run:** structured outputs (Anthropic path)
give ~0% parse failure by construction. Free-text JSON on the cleanest open-weight models
here is **0–8%**. The earlier `make_llm_reasoner` cascade note cites ~24% on a mixed run;
expect the weakest zoo models (3B, gpt-oss reasoning models that bury JSON in `<think>`,
gemma) to climb toward that. **Plan: log the per-model genuine-parse rate as a first-class
column of the matrix** — a model with >40% parse loss can't be scored fairly and should be
flagged or dropped (see open problems).

---

## 4. Plan — building the model × tier matrix for the basis factor-analysis

### 4.1 Examinee panel (target 8–40, weighted mid/open per the synthesis)
A concrete reachable-today panel of **~14–18 examinees** stratified by size, before any
NVIDIA-NIM expansion:
- **open-small (≤~12B):** Groq `llama-3.1-8b-instant`, NVIDIA `meta/llama-3.1-8b-instruct`,
  `meta/llama-3.2-3b-instruct`, `mistralai/mistral-7b-instruct-v0.3`, Groq `openai/gpt-oss-20b`.
- **mid (~17B–235B):** Groq `qwen/qwen3-32b`, `meta-llama/llama-4-scout-17b`, NVIDIA
  `nvidia/llama-3.3-nemotron-super-49b-v1.5`, `meta/llama-3.3-70b-instruct`,
  `qwen/qwen3-next-80b-a3b`, `nvidia/nemotron-3-super-120b-a12b`, Cerebras `gpt-oss-120b`,
  `zai-glm-4.7`, OpenAI `gpt-4.1-mini`/`gpt-4.1-nano`.
- **frontier:** OpenAI `gpt-4o` + the existing Anthropic trio (Opus 4.8 / Sonnet 4.6 /
  Haiku 4.5 via `make_opus_reasoner`) — the saturated top, included as anchors.
- **NVIDIA-NIM expansion to 30–40:** add the rest of the NIM size ladder (Llama 1B/3B/90B,
  Qwen 122B/397B/480B, Mistral 675B, Nemotron 4B/30B/49B/340B, Phi, Gemma) once cold-start
  timeouts are handled — this is where the open-weight variance density lives.

### 4.2 Battery to run per examinee
- **The full gradeable ladder R0–R8** (`gen_R0,R1,R2,R3,R5,R6,R7,R8` in `reasoning_phase0`)
  plus the **legality / confound-control battery already in the harness**: `gen_sqrt_label`
  (C-FORMAT control, "CF" tier), `gen_rational_extra` (C-MEMO, "RE" tier). All grade via
  `reasoning_phase0.grade` — no LLM in the selection seat.
- **Same sampled probes across every examinee** (apples-to-apples; reuse the
  `run_model_comparison.sample_probes` pattern, single seed).
- **Procedurally-generated isomorphs (C-MEMO):** the generators already emit
  clean/iso/adversarial/transfer per probe — run all four versions so the matrix carries
  the isomorphism axis, not just canonical instances.
- Frontier anchors run through `make_opus_reasoner` (structured); zoo through
  `make_zoo_reasoner` (free-text). **Same probes, same grader** → comparable cells; the
  parse-failure column flags where the comparison is degraded.

### 4.3 Matrix → factor analysis (the decisive tests, per synthesis §3)
1. **Build `examinee × (tier × version)` accuracy + trace-vector matrix.** Reuse
   `reasoning_phase0.eff_dim` for the trace-vector effective dimensionality already.
2. **Held-out-family prediction (the non-circular decider, all reviewers converge):** fit a
   multi-axis model and a rank-1 monotone ladder; predict performance on a **held-out probe
   family**; a multi-axis win over rank-1 *earns* "basis." This is the primary deliverable.
3. **Double dissociation (honest at any N):** A>B on axis X *and* B>A on axis Y, both
   significant — the small-N logic Opus endorsed. We have a half-confirmed pair
   (Sonnet>Opus on R2/R5; Opus≥Sonnet on R8) but it's format-confounded; the zoo + the
   C-FORMAT 2×2 (CF tier already in harness) lets us re-run it format-controlled.
4. **CDM / MIRT only once examinee count is high enough** (synthesis: ≥8, ideally 20–40),
   and only as a *follow-on* to held-out prediction — not as the primary (a Q-matrix CDM at
   small N is circular). With 30+ NIM examinees, MIRT-vs-unidimensional via LRT +
   participation ratio + profile inspection (DeepSeek's recipe) becomes legitimate.
5. **Report failure SHAPES per (examinee, tier),** not just accuracy (failure-signature
   doctrine) — the `_kill_pattern` field is already emitted by `grade`.

---

## 5. Open problems / blockers

- **BIGGEST BLOCKER — rate limits & throughput, not reachability.** A full run is
  (≈18 examinees) × (12 tiers × 4 versions × N_per probes) ≈ **thousands of calls.** Groq,
  GitHub Models, and Gemini free tiers rate-cap hard (429s seen in the very first 12-probe
  smoke; GitHub & Gemini effectively unusable at volume right now). The run is **gated on
  request budget / pacing**, not on whether models answer.
  **→ STATUS 2026-05-29: this blocker now has a runner — `run_zoo_matrix.py` (built + 38 offline
  tests).** It implements every mitigation named here: per-provider min-interval + sliding-window
  RPM pacing (`DEFAULT_LIMITS`, tunable), examinees interleaved round-robin so no provider is
  bursted, append-only JSONL checkpoint that auto-resumes (a 429 storm costs at most the one
  in-flight call), bounded single re-ask, the parse-rate gate below, and NVIDIA cold-start
  warm-up. **Remaining work is operational, not architectural:** pick `--n`, tune `DEFAULT_LIMITS`
  against observed 429s, and launch when the API rate budget is free (do NOT run it concurrently
  with another heavy Anthropic run — they contend). Lean on NVIDIA NIM + OpenAI (tolerated the smoke).
- **Parse-failure handling for weak models.** Free-text JSON loss is 0–8% on clean models
  but will climb on 3B / reasoning models that bury JSON in `<think>`. Need a policy:
  (a) log genuine-parse rate per model as a matrix column; (b) a single bounded re-ask on a
  genuine parse failure ("return ONLY the JSON object"); (c) drop/flag any examinee with
  >~40% parse loss — it can't be scored fairly and pollutes the factor analysis.
- **Catalog drift.** Provider model IDs change without notice (already bit us: stale
  Cerebras/Groq IDs 404'd on run 1). Always `/models`-list immediately before a full run;
  treat the catalog in `zoo_inventory.py` as a snapshot, not ground truth.
- **DeepSeek out of balance (402)** — a useful mid examinee is blocked until the key is
  topped up.
- **Cold-start timeouts on NVIDIA small models** — `phi-4-mini`, `nemotron-nano-9b` timed
  out at 40s; a longer first-call timeout + warm-up ping likely recovers them (the deep NIM
  bench is too valuable to drop over cold starts).
- **How many examinees can we realistically reach?** Today, comfortably **~14–18** across
  Cerebras/Groq/NVIDIA/OpenAI; **~30–40** if NVIDIA-NIM cold-starts are handled and Groq
  pacing is respected — which crosses the synthesis's CDM/MIRT threshold. The frontier
  Anthropic trio stays as saturated top-anchors.
- **Structured-output asymmetry is a confound to STATE LOUDLY.** Frontier anchors (Anthropic)
  get schema-enforced JSON (~0% parse loss); the entire zoo is free-text (lossy). If the
  basis falls out partly along the structured/free-text line, that's a measurement artifact,
  not a reasoning axis — the parse-failure column must be carried into the factor analysis
  as a control covariate, exactly as C-FORMAT is treated in the synthesis.
