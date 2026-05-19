# Model Sweep Results — Who Produces What?

**Filed:** 2026-05-19
**Sweep period:** 2026-05-18 to 2026-05-19
**Candidates:** 100 frozen concept combinations with full provenance
**Models tested:** 12 attempted, 5 produced usable tools
**Total tools generated:** 424 (after deduplication)
**Total scored:** 424 through 186-probe tier-stratified battery

---

## 1. Generation Results

### Models That Worked

| Model | Provider | Generated | Valid | Category |
|-------|----------|-----------|-------|----------|
| **qwen-397B** (control) | NVIDIA | 100/100 | 86 | General MoE |
| **qwen3-coder-480B** | NVIDIA | 95/100 | 87 | Code specialist |
| **llama-3.3-70B** | NVIDIA | 100/100 | 76 | Meta general |
| **llama4-maverick-17B** | NVIDIA | 100/100 | 79 | Llama 4 arch |
| **nemotron-reasoning-30B** | NVIDIA | 27/100 | 1 | Reasoning mode |

### Models That Failed

| Model | Failure Mode | Root Cause |
|-------|-------------|------------|
| deepseek-v4-pro | 19/20 timeouts | NVIDIA endpoint overloaded |
| deepseek-v4-flash | 7/7 timeouts | Same infra issue |
| mistral-675B | 4/4 502 Bad Gateway | Endpoint unstable |
| codestral-22B | 100/100 404 | Endpoint removed/renamed |
| nemotron-ultra-253B | 404 | Endpoint removed |
| gemma4-31B | Timeout on first call | Endpoint slow |
| qwen3-thinking-80B | 99/100 no_code | Thinking mode outputs traces, not code blocks |

**Key finding:** Only 5 of 12 NVIDIA API endpoints reliably serve long code-generation
prompts. The Qwen family and Meta Llama family are stable; DeepSeek, Mistral, and
several NVIDIA-hosted models are not.

---

## 2. The Scoring Matrix

424 tools scored through 186-probe tier-stratified battery (R1-R6):

```
Model                     Tools Valid AccG NovG  Rate  MeanAcc BestAcc    R1     R2     R3     R4     R5     R6  Novelty
-----------------------------------------------------------------------------------------------------------------------
qwen-397B-ctrl              100    86    3    4   7.0%  35.9%   43.5%  36.1%  30.1%  45.1%  26.6%  30.5%  41.5%  0.831
qwen3-coder-480B             95    87    0   37  38.9%  33.6%   41.9%  24.5%  33.1%  37.7%  28.3%  33.4%  39.4%  0.848
llama-3.3-70B               100    76    0   71  71.0%  33.7%   40.9%  18.5%  34.6%  35.6%  30.2%  35.6%  41.6%  0.863
llama4-maverick-17B         100    79    1   59  60.0%  34.5%   43.0%  22.7%  33.7%  39.2%  30.1%  35.2%  40.5%  0.858
nemotron-reasoning-30B       27     1    0    1   3.7%  33.9%   33.9%  16.7%  35.0%  33.3%  32.1%  37.5%  42.9%  0.857
```

AccG = passed accuracy gate (beat NCD baseline). NovG = passed novelty gate (NCD > 0.85).
Rate = total forge rate. R1-R6 = mean tier accuracy. Novelty = mean source-code NCD vs library.

---

## 3. Key Findings

### 3.1 No model beats the accuracy baseline consistently

**Only 4 tools out of 424 (0.9%) passed the accuracy gate** — 3 from qwen-397B, 1 from
maverick. The NCD baseline at 42% is extremely hard for every model. Mean accuracy
across all models is 33-36%. The best tool across the entire sweep (qwen-397B's
`compressed_sensing_x_immune_systems`) scored 43.5%.

This confirms that the accuracy challenge is a property of the TASK, not the model.

### 3.2 Novelty scores are inflated by model-library mismatch

The novelty gate (source-code NCD > 0.85) fired 71% for llama-3.3 vs 4% for qwen-397B.
This is **misleading**: the existing forge library was built by qwen, so any non-qwen
model naturally produces code that looks different from the library. llama-3.3's 71%
novelty rate is largely stylistic divergence (different variable names, formatting,
code structure) not mechanistic divergence.

**The novelty gate needs behavioral NCD** (compare output vectors, not source code) to
fix this model-bias problem.

### 3.3 The prompt template dominates mechanism type

Code review of 15+ tools per model confirmed:

**All models produce the same 3-layer architecture:**
1. Regex structural parsing (negation, comparatives, conditionals, numerics)
2. Weighted score decomposition (structural + computation + NCD tiebreaker)
3. Meta-confidence epistemic honesty checks (same 5-6 presupposition patterns)

This architecture is specified by the prompt template (`build_code_gen_prompt()`), and
every model faithfully implements exactly what the prompt asks for. **Changing the
model is like hiring a different contractor to build from the same blueprint.**

### 3.4 Exception: Llama-4-Maverick shows genuine mechanism diversity

Maverick (Llama 4 architecture, 17B MoE) was the only model that partially escaped the
prompt template's constraint. Its tools include:

- **Hamming (7,4) error-correcting codes** — maps features to codewords, syndrome-based
  scoring (not just weighted sums)
- **NetworkX graph construction** — builds actual directed graphs, computes network
  metrics and criticality measures
- **Category-specific dispatch tables** — named parsers per problem type with explicit
  dispatch (`self.parsers = {"bat_and_ball": self.parse_bat_and_ball, ...}`)
- **Typed Gaussian Belief Filters** — Kalman state estimation over typed propositions
- **Echo State Networks** — 100-dim reservoir state with Lyapunov exponent tuning

These are NOT the standard regex+NCD skeleton. The parsing layer is still regex
(unavoidable for text input), but the scoring mechanisms are genuinely different.

**Hypothesis:** Llama 4's architectural differences (128 experts, different attention
pattern) cause it to reach for different algorithmic patterns than Qwen/Llama-3.
This is the strongest signal that model architecture matters more than model size.

### 3.5 Tier profile differences exist but are modest

| Tier | Best Model | Score | Worst Model | Score |
|------|-----------|-------|-------------|-------|
| R1 (rule execution) | qwen-397B | 36.1% | llama-3.3 | 18.5% |
| R2 (deduction) | nemotron | 35.0% | qwen-397B | 30.1% |
| R3 (abstraction) | qwen-397B | **45.1%** | nemotron | 33.3% |
| R4 (search) | nemotron | 32.1% | qwen-397B | 26.6% |
| R5 (causal) | nemotron | 37.5% | qwen-397B | 30.5% |
| R6 (meta/ToM) | nemotron | 42.9% | qwen3-coder | 39.4% |

qwen-397B is strongest on R1 and R3 (rule execution and abstraction). The Llama/Maverick
models are more balanced across tiers. All models are weak on R4 (search/planning).

---

## 4. Accuracy Distribution

| Model | n | Mean | >=40% | >=35% |
|-------|---|------|-------|-------|
| qwen-397B | 86 | 35.9% | **15** | **44** |
| qwen3-coder-480B | 87 | 33.6% | 8 | 17 |
| llama-3.3-70B | 76 | 33.7% | 3 | 8 |
| llama4-maverick-17B | 79 | 34.5% | 6 | 17 |

**qwen-397B produces the most accurate tools.** 15 tools above 40% vs 3-8 for other
models. The control outperforms all challengers on raw accuracy. This is consistent
with it having the longest, most complete implementations (mean 326 lines vs 130-137
for others).

---

## 5. What This Means for the Next Iteration

### The model is not the bottleneck — the prompt is.

Every model implements the same architecture because the prompt specifies it. The
`build_code_gen_prompt()` function describes the ReasoningTool interface, mentions NCD,
describes structural parsing, and lists the epistemic honesty checks. All models
faithfully implement exactly this.

**Priority 1: Change the prompt strategy.**
- Algorithm-first: "Implement belief propagation to score candidate answers"
- Gap-targeted: "The library lacks R4 search tools. Build one using backtracking."
- Adversarial: "Build a tool that solves problems this existing tool gets wrong"
- Exemplar-based: "Here's a working tool. Build a DIFFERENT approach."

**Priority 2: Try genuinely different providers.**
- DeepSeek R1 (paid, reasoning mode) — different training, extended thinking
- GitHub Models (free) — GPT-4o-mini, Phi-4
- These providers may have better reliability than NVIDIA for large models

**Priority 3: Fix the novelty gate.**
- Replace source-code NCD with behavioral NCD (output vectors on probe battery)
- This removes the model-library bias that inflates scores for non-qwen models

**Priority 4: Maverick warrants deeper investigation.**
- Only model showing genuine mechanism diversity
- Its Hamming/ECC, reservoir, and Kalman patterns are worth mechanism-knockout testing
- If ablation shows these mechanisms contribute, maverick becomes the preferred generator for mechanistic diversity

### What we can drop

- **Model size comparisons within the same family** (qwen-397B vs qwen3-coder-480B):
  different sizes of the same architecture produce the same mechanisms. Size buys
  implementation completeness, not diversity.
- **NVIDIA endpoints for DeepSeek/Mistral/Gemma**: unreliable. Use paid APIs directly.
- **"Reasoning mode" models without code extraction adaptation**: qwen3-thinking and
  nemotron-reasoning both output thinking traces, not code blocks. They need a
  different extraction strategy or a two-turn prompt ("think, then code").

---

## 6. The Honest Summary

We tested whether different models produce different reasoning mechanisms when given
the same prompts. The answer: **mostly no, with one interesting exception.**

The prompt template constrains the solution space so tightly that 4 of 5 model families
converge on the identical regex + NCD + meta-confidence architecture. Llama-4-Maverick
partially escapes this constraint, producing genuinely different scoring mechanisms
(ECC, reservoir networks, Kalman filters) — likely because its 128-expert MoE
architecture reaches for different algorithmic patterns.

No model significantly outperforms qwen-397B on accuracy. qwen remains the best at
producing complete, working implementations. But accuracy isn't the bottleneck —
mechanism diversity is. And mechanism diversity requires changing the prompt, not the
model.

**The sweep was worth running.** It eliminates model choice as the primary lever,
identifies maverick as an interesting outlier, and confirms that the next iteration
must target the prompt template. One sweep, clear answer.
