# Research Brief: Maximizing Throughput in LLM-Guided Evolutionary Program Synthesis

## Context

We are running Apollo, an evolutionary system that evolves routing networks ("organisms") over hand-crafted reasoning primitives. Each organism is a DAG of 5-12 primitives with a neural-style router. We use 6-objective NSGA-III optimization with LLM-guided mutations (route modification, wiring changes, primitive swaps).

**Current hardware:** Single RTX 5060 Ti (16GB VRAM), i7-14700F (20 cores/28 threads).

**Current LLM setup:** Qwen2.5-Coder-7B-Instruct, 8-bit quantized (8.7GB VRAM), served via FastAPI on localhost. Batch generation (up to 8 prompts padded together). Each generation requires ~25 LLM mutations.

**Current performance:** ~2.5 min/gen with batch LLM + racing evaluation (3-stage successive halving that cuts evals by 51%). Dropping to ~1.5 min/gen after fixing a double-evaluation bug.

**Bottleneck breakdown (estimated):**
- LLM mutations: ~60% of gen time (25 prompts, batched in groups of 8)
- Task evaluation: ~30% of gen time (100 tasks × surviving organisms × 0.5s timeout)
- Selection + archiving: ~10%

## Research Questions

1. **LLM serving optimization on consumer GPUs:** What are the best approaches for maximizing throughput of a 7B parameter model on a single 16GB consumer GPU?
   - vLLM vs TGI vs SGLang on Windows/WSL — which has the best throughput for our batch sizes (8-25 prompts)?
   - Is continuous batching with PagedAttention significantly faster than our current pad-and-batch HuggingFace generate()?
   - What about speculative decoding with a smaller draft model (Qwen2.5-Coder-1.5B as draft)?
   - AWQ or GPTQ 4-bit quantization vs our current 8-bit bitsandbytes — what's the throughput/quality tradeoff for code generation tasks?

2. **Mutation model optimization:** Is Qwen2.5-Coder-7B the right model for our mutation operator?
   - Would a smaller model (3B, 1.5B) produce adequate mutations at much higher throughput?
   - What about fine-tuning a small model on our successful mutations (we log every mutation attempt with outcome)?
   - Are there mutation-specific prompting strategies that reduce output token count while maintaining quality?
   - What max_new_tokens should we use? We currently use 1024 but most mutations are <200 tokens.

3. **Evaluation acceleration:** Beyond racing/successive halving, what techniques exist for reducing evaluation cost in GP?
   - Surrogate-assisted evaluation: LightGBM, random forest, or neural surrogates trained on (organism features → fitness vector). At what training set size do they become reliable?
   - Fitness inheritance from parents — can we skip evaluation for organisms with small mutations?
   - Parallel evaluation across CPU cores — our organisms are pure Python, 0.5s timeout each. Can we use ProcessPoolExecutor effectively?
   - Semantic caching — if two organisms produce identical compiled code, reuse fitness?

4. **Population-level parallelism:**
   - Asynchronous steady-state evolution vs generational: can we overlap mutation and evaluation?
   - Pipeline parallelism: stage 1 (mutation) feeds into stage 2 (evaluation) feeds into stage 3 (selection) — can these overlap across generations?
   - Multi-GPU scaling: if we add a second GPU, what's the optimal architecture for splitting work?

5. **Algorithmic efficiency at the evolutionary level:**
   - Lexicase selection vs NSGA-III for program synthesis — recent GP literature suggests lexicase is superior for test-case-based problems. Applicable here?
   - Informed initialization: using static analysis of the primitive library to seed better organisms
   - Semantic awareness in crossover: matching primitives by behavioral similarity rather than structural position

## Key Papers to Start From

- FunSearch (Romera-Paredes et al, Nature 2023) — island model + LLM mutation
- EvoPrompting (Chen et al, NeurIPS 2023) — LLM as mutation operator
- OpenELM (CarperAI, 2024) — LLM + MAP-Elites for code evolution
- vLLM (Kwon et al, SOSP 2023) — PagedAttention for LLM serving
- SGLang (Zheng et al, 2024) — structured generation and batching
- Surrogate-assisted GP (Jin 2011, IEEE TEVC) — fitness approximation

## Desired Outcomes

- Concrete throughput numbers: tokens/sec for various serving frameworks on RTX 5060 Ti
- Recommended model size + quantization + serving stack for our use case
- Practical evaluation acceleration techniques ranked by implementation effort vs speedup
- Architecture recommendation for multi-GPU scaling
