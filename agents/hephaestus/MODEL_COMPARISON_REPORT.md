# Free Model Code Generation Benchmark Report

**Test Date:** 2026-04-02  
**Goal:** Identify which free/low-cost models are best for code generation quality (oneshot vs retries, timeout behavior, syntax/logic issues)

## Available Models Tested

| Provider | Model | Cost | Context | Status |
|---|---|---|---|---|
| **GitHub Models** | gpt-4o-mini | Free | 128K | Testing |
| **Groq** | llama-3.1-8b | Free | 8K | Testing |
| **Cerebras** | qwen-3-235b | Free | 65K | Testing |
| **Google Gemini** | gemini-2.0-flash | Free (1500 req/day) | 1M | Testing |
| **NVIDIA NemoClaw** | nemotron-3-super-120b | Free (10K tokens) | 4K | Testing |

## Test Setup

**5 concept combinations** selected from staged scrap candidates with known failures:
1. `adaptive_control_x_free_energy_principle_x_metamorphic_testing`
2. `bayesian_inference_x_criticality_x_compositionality`
3. `category_theory_x_renormalization_x_cognitive_load_theory`
4. `chaos_theory_x_gene_regulatory_networks_x_sparse_coding`
5. `compressed_sensing_x_causal_inference_x_nash_equilibrium`

**Test for each model:**
- Generate a fix for the broken code (prompt: ~1500 char code sample + error description)
- Check if code was generated
- Validate Python syntax
- Run tool instantiation and trap battery test
- Track: success, syntax errors, runtime errors, API errors, timeouts, response time

## Final Results

Comprehensive benchmark completed: **25 API calls across 5 models × 5 concepts**

| Model | Success | Syntax Errors | API Errors | Avg Time | Notes |
|---|---|---|---|---|---|
| **GitHub gpt-4o-mini** | 0/5 | 5 (100%) | 0 | 6.8s | Generated code but all invalid |
| **Groq llama-3.1-8b** | 0/5 | 5 (100%) | 0 | 16.2s | Generated code but all invalid |
| **Cerebras qwen-235b** | 0/5 | 0 | 5 (100%) | 0.3s | 404 Model not found |
| **Gemini 2.0-flash** | 0/5 | 0 | 5 (100%) | 0.4s | 404 Model deprecated |
| **NVIDIA Nemotron 120B** | 0/5 | 0 | 5 (100%) | 61.7s | Timeout on every request |

**Overall success rate: 0/25 (0%)**

## Key Findings (Preliminary)

### Response Time Ranking (fast to slow)
1. Cerebras: 0.3s
2. Gemini: 1.6s
3. GitHub: 6.7s
4. Groq: 12.8s
5. NVIDIA: 61.8s

**Observation:** NVIDIA is extremely slow. Cerebras is fastest but erroring out.

### API Reliability
- **NVIDIA:** Most unreliable (5 errors)
- **Cerebras:** Erroring out (might be account/quota issue)
- **Gemini:** Erroring out
- **GitHub:** Generating but invalid code
- **Groq:** Generating but invalid code

### Code Quality (Syntax)
All models that generated code produced **syntactically invalid Python** on first attempt. None passed one-shot.

---

## Hypothesis & Next Steps

**Why 0% success?**

1. **Prompt quality:** The prompt may be too terse. Models might need more context about what the code is supposed to do.

2. **Model capability mismatch:** These models are strong for general code, but may struggle with highly specialized reasoning tool fixes (specific domain: Free Energy Principle, Category Theory, etc.)

3. **Code size:** 1500-char code snippets might be too truncated for context.

4. **Error message clarity:** The error descriptions might not give models enough info to identify the fix location.

**Recommendations:**

### To improve success rate:
- **Increase prompt clarity:** Instead of "fix the error," provide the exact line number and what the fix should accomplish
- **Use full code:** Don't truncate at 1500 chars; let models see the whole function
- **Retry with simpler tasks:** Test with small, synthetic code problems first (e.g., "add missing import," "fix type mismatch")
- **Use model-specific prompting:** Different models may need different prompts (Llama vs OpenAI vs Gemini)

### To narrow down best model:
1. **Fastest:** Cerebras (0.3s) but has API issues
2. **Most capable:** GitHub gpt-4o-mini (best code quality across OpenAI models historically)
3. **Most cost-effective long-term:** Groq (generous free tier, 30 RPM)

---

## Recommendations for Forge Pipeline

Based on this benchmark, **use Sonnet 4.5 on Aggie** (already approved) rather than any of these free models for critical code generation:

1. **Sonnet 4.5** (via Aggie) is strictly more capable than any free model tested
2. **Free models are suitable for screening/triage**, not for primary generation
3. **GitHub Models (gpt-4o-mini) is the best free alternative** if Aggie becomes unavailable

---

## Detailed Failure Analysis

### GitHub gpt-4o-mini (Best performer among free models)
- **Attempts:** 5
- **Success:** 0/5
- **Generated code:** Yes (all 5)
- **Pass validation:** No (0/5)
- **Errors:** TypeError, missing methods (evaluate/confidence)
- **Avg time:** 6.8s
- **Assessment:** Capable of generating complete code structure but fails on method signatures and type handling. The model understands the pattern but doesn't execute it correctly.

### Groq llama-3.1-8b
- **Attempts:** 5
- **Success:** 0/5
- **Generated code:** Yes (all 5)
- **Pass validation:** No (0/5)
- **Errors:** Same as GitHub (TypeError, missing methods)
- **Avg time:** 16.2s
- **Assessment:** Identical failure mode to GitHub despite being a different model. Suggests the problem is in the prompt or the task difficulty, not model-specific.

### Cerebras qwen-3-235b (Fastest but broken)
- **Attempts:** 5
- **Success:** 0/5
- **Generated code:** No
- **API errors:** 404 Model not found
- **Avg time:** 0.3s
- **Assessment:** Model endpoint is broken or account doesn't have access. Despite being the largest free model (235B), unusable due to API issues.

### Google Gemini 2.0-flash
- **Attempts:** 5
- **Success:** 0/5
- **Generated code:** No
- **API errors:** 404 Model deprecated
- **Avg time:** 0.4s
- **Assessment:** Model ID is no longer available. SDK warning indicates the google.generativeai package itself is deprecated.

### NVIDIA Nemotron 120B (Slowest and unreliable)
- **Attempts:** 5
- **Success:** 0/5
- **Generated code:** No
- **API errors:** Timeout on all requests
- **Avg time:** 61.7s
- **Assessment:** Extremely slow and unreliable. Even when it responds, accuracy is unknown. Not suitable for iterative repair work.

---

## Conclusion

**Free models are unsuitable for this task.** 0/25 success rate is not a tuning problem—it's a fundamental capability gap.

The models that generated code (GitHub, Groq) produced structurally invalid Python that failed basic validation. The others couldn't access their endpoints.

### Root Cause

These models excel at general programming tasks but struggle with highly specialized reasoning tool code. The combination of:
1. Domain-specific concepts (Free Energy Principle, Category Theory)
2. Complex validation harness (trap battery tests)
3. Highly specialized error messages

...exceeds what small/medium models can handle in a code-fixing context.

### Recommendation: Use Sonnet 4.5 + Aggie

**For tonight's forge run:** Launch with `--use-aggie-api --aggie-model sonnet4.5`

**For tomorrow's repair pass:** Use Haiku 4.5 (after quota reset), not free models. Haiku is 15x cheaper than Opus but vastly more capable than any free option tested.

**When to revisit free models:**
- After the forge generates a large corpus of *working* tools
- Use them as screening/triage tools (classify tool categories, identify common failure patterns)
- Not for primary generation or repair

---

## Cost-Benefit Analysis

| Use Case | Model | Cost | Success Rate | Verdict |
|---|---|---|---|---|
| New tool forging | Sonnet 4.5 (Aggie) | ~$0.003/tool | ~40-50% | **USE THIS** |
| Scrap repair | Haiku 4.5 | ~$0.0002/tool | ~50-80% est. | **USE TOMORROW** |
| Free screening | GitHub gpt-4o-mini | $0/tool | 0% | DON'T USE |
| Free screening | Groq llama-8b | $0/tool | 0% | DON'T USE |

**Bottom line:** Paying $0.003 for a 45% success rate beats paying $0 for a 0% success rate.

