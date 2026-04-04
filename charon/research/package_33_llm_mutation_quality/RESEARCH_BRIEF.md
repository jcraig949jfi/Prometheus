# Deep Research Brief: LLM-Guided Mutation Quality and the 7B Capability Cliff

## Research Question

Apollo uses a local Qwen2.5-Coder-7B model for 75% of its mutations (route rewriting, wiring changes, primitive swaps). This occupies ~8.7GB VRAM and generates ~7 tokens/second. We need to understand: **Is 7B sufficient for meaningful code mutation, or are we below a quality cliff where LLM-assisted mutation degenerates to random noise with extra steps?**

## System Context

Apollo's mutations:
- **Route mutation (40%)**: LLM rewrites the Python router function (10-30 lines of code that combines primitive outputs into a score)
- **Wiring mutation (20%)**: LLM suggests new DAG edge connections between primitives
- **Primitive swap (15%)**: LLM recommends replacing one primitive with another from the library of 25
- **Parameter mutation (25%)**: No LLM — direct AST-level float/int perturbation (fallback)

Current LLM config: Qwen2.5-Coder-7B-Instruct, 8-bit quantization, temperature 0.7, max 512 tokens.

Hardware constraint: 17GB VRAM (RTX 4060 Ti), Apollo needs ~4GB for evaluation, leaving ~13GB for LLM. 7B at 8-bit fits. 14B does not.

## What I Need You to Research

### 1. Code Generation Quality vs Model Size
- Benchmarks (HumanEval, MBPP, SWE-bench) by model size: 1B, 3B, 7B, 14B, 33B, 70B
- Is there a quality cliff between 3B and 7B? Between 7B and 14B?
- Specifically for SHORT code snippets (10-30 lines) — does the cliff shift?
- Code mutation (modifying existing code) vs code generation (writing from scratch) — different quality profiles?

### 2. Qwen2.5-Coder vs Alternatives at 7B
- Compare: Qwen2.5-Coder-7B, CodeLlama-7B, StarCoder2-7B, DeepSeek-Coder-V2-Lite, Phi-3.5-mini
- Which 7B model produces the most syntactically valid Python mutations?
- Fine-tuning on domain-specific code (routing logic over fixed APIs) — does it help at 7B?
- Quantization impact: 8-bit vs 4-bit on code generation quality at 7B

### 3. LLM Mutation Validation and Repair
- FunSearch (Romera-Paredes et al., 2024): how do they handle LLM-generated code failures?
- EvoPrompting (Chen et al.): validation pipeline, rejection sampling, self-repair
- What percentage of LLM mutations typically pass syntax+semantic validation? (Literature benchmarks)
- Cascading repair: can a smaller model (3B) fix mutations from a larger model's failures?

### 4. API-Assisted Mutation as Alternative
- Use a cloud API (DeepSeek, GPT-4o-mini) for high-quality mutations instead of local model
- Latency and cost implications: 100-200ms API call vs 70ms local inference
- Batch mutation: generate N mutations per API call, select best
- Hybrid: local model for fast/simple mutations, API for complex route rewrites
- Rate limiting and reliability concerns for evolution (10,000+ mutations/day)

### 5. Grammar-Guided and Constrained Generation
- Instead of free-form code generation, constrain LLM output to a grammar
- PICARD (constrained decoding for SQL) applied to Python routing code
- Typed holes: generate code with typed placeholders, LLM fills only the holes
- Does constrained generation improve success rate enough to offset reduced diversity?

### 6. Measuring Mutation Quality in Evolutionary Context
- Not just "does the code compile" but "does the mutation produce fitness improvement?"
- Beneficial mutation rate: what fraction of LLM mutations improve fitness vs neutral vs harmful?
- Comparison with random AST mutation: if LLM mutations aren't significantly better than random tree perturbation, we're wasting VRAM
- Operator selection (adaptive): track which mutation types are producing fitness gains and shift allocation

## Output Format

For each area, provide:
- **Key papers** (title, authors, year, venue, 2-3 sentence relevance summary)
- **Practical recommendations** for our system (7B local, 17GB VRAM, routing code mutations)
- **Known pitfalls** to avoid
- **Open questions** the literature hasn't resolved

Prioritize 2022-2026 work. Include seminal older papers where foundational.
