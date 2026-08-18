# Council Prompt: Apollo v2 — Concrete Speedups and Plateau Avoidance

## Context

We are running **Apollo v2**, an evolutionary system that searches over DAGs of 25 fixed reasoning primitives. It's at generation 60, pop=50, 6-objective NSGA-II, with LLM-assisted mutation (local Qwen2.5-Coder-7B). Current throughput: ~10 gens/min on a single RTX 4060 Ti (17GB VRAM, ~4GB used by evaluation, ~9GB by LLM).

**Current results after 60 gens:**
- Best accuracy margin: -0.15 (51.5% vs NCD baseline 51.0%)
- Zero organisms have load-bearing primitives (ablation_delta = 0 everywhere)
- 100% compilation viability
- LLM mutation produces syntactically valid but semantically flat routing code

**We need concrete, actionable answers to these 5 questions. No padding. Name specific libraries, papers, parameter settings, and code patterns.**

---

## Question 1: Is our population too small for 6 objectives?

Pop=50 with 6 Pareto objectives. The many-objective literature suggests Pareto dominance collapses at 4+ objectives — most individuals become non-dominated, and selection degenerates to crowding distance only.

- **At pop=50 and 6 objectives, what fraction of the population is typically non-dominated?**
- **Should we switch from NSGA-II to NSGA-III?** If so, how many reference points for 6 objectives?
- **Or should we reduce objectives?** Which of our 6 are likely redundant? (accuracy, calibration, ablation_delta, generalization, novelty, parsimony)
- **Can pymoo's NSGA-III be dropped in as a replacement, or does it require restructuring?**

## Question 2: Is 7B LLM sufficient for code mutation?

75% of our mutations go through Qwen2.5-Coder-7B (8-bit quantized). The mutations compile but don't produce fitness improvement — they look syntactically valid but semantically flat (e.g., `return sum(outputs) / len(outputs)` regardless of task structure).

- **What's the minimum model size for meaningful Python code mutation (10-30 line functions)?**
- **Would switching to DeepSeek-Coder-V2-Lite (16B) at 4-bit fit in 13GB VRAM and produce better mutations?**
- **Alternatively: should we use a cloud API (DeepSeek-chat at $0.14/1M tokens) for mutations instead of local?** At ~200 mutations/gen × 10 gens/min, what's the daily cost?
- **FunSearch (Romera-Paredes et al.) reports mutation success rates. What do they report, and how does 7B compare to their model sizes?**

## Question 3: What are the known plateau patterns in GP evolution?

We're 60 gens in with essentially zero fitness improvement. The population compiles and runs but every organism scores within ±1% of the NCD baseline.

- **Is this normal for GP at generation 60?** What's the typical timescale for initial fitness emergence in variable-length GP?
- **Known causes of early-generation plateaus in GP:** insufficient mutation diversity, selection pressure too weak, fitness landscape too flat, population too homogeneous?
- **Diagnostic signals:** What should we measure at gen 60 to distinguish "normal warmup" from "stuck in a plateau"?
- **Concrete interventions** if we're genuinely stuck: restart strategies, diversity injection, fitness shaping, population size changes?

## Question 4: Surrogate-assisted evaluation for 15,000 sandbox runs/gen

Each gen evaluates ~150 organisms × 100 tasks = 15,000 sandbox executions. Each takes 7-8ms, totaling ~1.2s/gen. This is manageable now but will become the bottleneck if we increase population size or task battery.

- **Racing algorithms (F-race):** Can we evaluate organisms on 20 tasks first, eliminate the bottom 50%, then fully evaluate survivors? What's the expected speedup vs quality loss?
- **Fitness inheritance:** Can offspring inherit parent fitness with a noise term? How much error can NSGA-II tolerate before Pareto ranking degrades?
- **Behavioral signature surrogates:** Our organisms produce a 50-dimensional behavioral signature (score on each reference task). Can we train a lightweight predictor (e.g., sklearn ridge regression on signatures) to estimate accuracy on the full 100-task battery?

## Question 5: What Python libraries should we be using that we're not?

Current stack: numpy, torch/transformers (LLM only), ast (genome compilation), threading (sandbox), yaml, zlib (NCD baseline). We rolled our own NSGA-II, novelty archive, and sandbox.

- **pymoo** — should we use their NSGA-II/III instead of our custom implementation? Pros/cons?
- **DEAP** — same question, different library
- **Nevergrad** — Facebook's derivative-free optimization. Applicable here?
- **EvoTorch** — GPU-accelerated evolution. Does it handle variable-length genomes?
- **OpenELM** — evolutionary LLM-guided search. How does it compare to our architecture?
- **Any other libraries** for sandboxed code execution, AST mutation, or program synthesis that we should know about?

---

## Response Format

For each question, give:
1. **Direct answer** (1-2 sentences)
2. **Evidence** (specific papers, benchmarks, or experience)
3. **Concrete recommendation** (what to change, with parameter values)
4. **Risk of the recommendation** (what could go wrong)
