# Forge Model Matrix — Who Produces What?

**Filed:** 2026-05-18
**Purpose:** Systematic comparison of code-gen models on identical reasoning tool prompts
**Status:** Ready to execute

---

## The Matrix

### Tier 1: NVIDIA API (free, same key, same interface)

| Model | Size | Type | Why test it |
|-------|------|------|-------------|
| `qwen/qwen3.5-397b-a17b` | 397B MoE | General | **CONTROL** — current forge model |
| `qwen/qwen3-coder-480b-a35b-instruct` | 480B MoE | **Code-specialized** | Larger, code-tuned — should produce cleaner algorithms |
| `qwen/qwen3-next-80b-a3b-thinking` | 80B MoE | **Reasoning/thinking** | Has explicit thinking mode — may produce more deliberate mechanisms |
| `deepseek-ai/deepseek-v4-pro` | Frontier | General | Different training lineage entirely — different mechanistic biases |
| `deepseek-ai/deepseek-v4-flash` | Frontier | Fast | Same lineage as v4-pro, speed tradeoff |
| `mistralai/mistral-large-3-675b-instruct-2512` | 675B | General | Largest available — brute force scale test |
| `mistralai/codestral-22b-instruct-v0.1` | 22B | **Code-specialized** | Small but code-tuned — tests whether specialization beats size |
| `nvidia/llama-3.1-nemotron-ultra-253b-v1` | 253B | NVIDIA-tuned | NVIDIA's own training mix |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | 30B MoE | **Reasoning** | Explicitly reasoning-tuned — small but targeted |
| `meta/llama-3.3-70b-instruct` | 70B | General | Meta's latest general model |
| `meta/llama-4-maverick-17b-128e-instruct` | 17B MoE | Next-gen architecture | Llama 4 architecture — entirely different design |
| `google/gemma-4-31b-it` | 31B | General | Google's latest open model |

### Tier 2: External APIs (separate keys needed)

| Model | Provider | Why test it |
|-------|----------|-------------|
| Claude Opus 4.7 | Anthropic (via Augment) | Strongest structured reasoning — the "careful model" hypothesis |
| GPT-4o / o3 | OpenAI | Different training paradigm, different code style |
| Gemini 2.5 Pro | Google | 1M context, different architecture |

### Tier 3: GitHub Copilot Free Credits

| Model | Access | Why test it |
|-------|--------|-------------|
| GPT-4o-mini | GitHub Models | Free tier, fast — baseline for small models |
| Llama variants | GitHub Models | Free, different access pattern |

---

## Experiment Protocol

### Step 1: Freeze 100 candidates

Select from the current queue with full provenance. Already specified in
`forge_iteration_experiment_design_2026-05-18.md`.

### Step 2: Run each Tier 1 model

All NVIDIA models use the same OpenAI-compatible API. The forge code already
supports `--model` flag. For each model:

```bash
python agents/hephaestus/src/hephaestus.py --runonce --model <model_id> --top-n 100
```

Store results with model tag (already in ledger via the `model` field we added).

### Step 3: Score and compare

For each model's 100 outputs:
- Forge rate (accuracy gate + novelty gate)
- Mechanism family classification (manual on first pass, then automated)
- Tier profile distribution
- Behavioral NCD against v1 control outputs
- New mechanism families (the primary metric)

---

## Expected Outcomes by Model Category

### Code-specialized models (qwen3-coder, codestral)
**Hypothesis:** Cleaner code, fewer syntax errors, higher pass rate on gates 1-4.
May produce more correct implementations of standard algorithms but potentially
LESS mechanistic novelty (code models converge on known patterns).

### Reasoning/thinking models (qwen3-next-thinking, nemotron-reasoning)
**Hypothesis:** More deliberate mechanism design. The "thinking" mode may produce
tools where the stated algorithm more closely matches the actual behavior (less
decorative mechanism). Potentially lower volume but higher mechanism fidelity.

### Large general models (mistral-675B, nemotron-ultra-253B, deepseek-v4-pro)
**Hypothesis:** Broader mechanistic vocabulary due to more training data. May
produce mechanism families that qwen-397B doesn't have in its weights. The scale
hypothesis: bigger model = more algorithms to draw on.

### Small models (codestral-22B, nemotron-reasoning-30B, maverick-17B)
**Hypothesis:** More constrained generation = potentially more creative within
constraints. Small models can't rely on brute-force pattern matching — they may
produce simpler but more genuine mechanisms. Or they may just produce broken code.

### Different architectures (deepseek-v4, llama-4-maverick, gemma-4)
**Hypothesis:** Different training data + different architecture = genuinely
different mechanistic biases. This is where new mechanism families are most
likely to emerge.

---

## The Comparison Table (to be filled)

| Model | Forge% | Gate1-4 Pass% | New Mechs | R3 Mean | R4 Mean | R5 Mean | BehavNCD | Best Tool |
|-------|--------|---------------|-----------|---------|---------|---------|----------|-----------|
| qwen-397B (ctrl) | 4.3% | 65% | 0 | 49% | 25% | 30% | 0.432 | — |
| qwen3-coder-480B | ? | ? | ? | ? | ? | ? | ? | ? |
| qwen3-thinking-80B | ? | ? | ? | ? | ? | ? | ? | ? |
| deepseek-v4-pro | ? | ? | ? | ? | ? | ? | ? | ? |
| deepseek-v4-flash | ? | ? | ? | ? | ? | ? | ? | ? |
| mistral-675B | ? | ? | ? | ? | ? | ? | ? | ? |
| codestral-22B | ? | ? | ? | ? | ? | ? | ? | ? |
| nemotron-ultra-253B | ? | ? | ? | ? | ? | ? | ? | ? |
| nemotron-reasoning-30B | ? | ? | ? | ? | ? | ? | ? | ? |
| llama-3.3-70B | ? | ? | ? | ? | ? | ? | ? | ? |
| llama-4-maverick-17B | ? | ? | ? | ? | ? | ? | ? | ? |
| gemma-4-31B | ? | ? | ? | ? | ? | ? | ? | ? |
| claude-opus-4.7 | ? | ? | ? | ? | ? | ? | ? | ? |
| gpt-4o | ? | ? | ? | ? | ? | ? | ? | ? |

**Primary question:** Which models produce mechanism families the others don't?

**Secondary question:** Does the code-specialist vs general vs reasoning-tuned
distinction predict mechanism diversity better than raw model size?

---

## Execution Order (optimized for insight per API call)

### Round 1: High-expected-impact models (run first)
1. `deepseek-ai/deepseek-v4-pro` — different training lineage, frontier scale
2. `qwen/qwen3-coder-480b-a35b-instruct` — code-specialized, same family as control
3. `mistralai/mistral-large-3-675b-instruct-2512` — raw scale test

### Round 2: Architecture diversity
4. `meta/llama-4-maverick-17b-128e-instruct` — different architecture
5. `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` — reasoning-tuned small model
6. `qwen/qwen3-next-80b-a3b-thinking` — thinking mode

### Round 3: Fill the matrix
7-12: Remaining NVIDIA models
13-14: External APIs (Claude, GPT-4o) — if Tier 1 results warrant the spend

### Round 4: Deep analysis
- Mechanism classification across all outputs
- Behavioral clustering
- Tier profile comparison
- The "who produces what" matrix filled

---

## Notes

- All NVIDIA Tier 1 models use the same API key and endpoint — just change the model ID
- The forge code already supports `--model` flag and records model in ledger
- Each 100-candidate run takes ~6-8 hours depending on model latency
- Run overnight: start 2-3 models in parallel on different concept subsets if needed
- The v1 control run continues in parallel (PID 6472, 1,192 candidates remaining)
