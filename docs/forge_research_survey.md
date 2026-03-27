# Forge Pipeline — Research Survey & Improvement Roadmap

*10 research frontiers surveyed, 50+ papers and projects reviewed, prioritized by effort-to-payoff ratio*

---

## Executive Summary

The forge pipeline (Nous → Coeus → Hephaestus → Nemesis) is operationally strong but the research landscape has moved fast in 2024-2026. Three findings are immediately actionable:

1. **Weak-to-strong evaluation via ensembles** — Many mediocre evaluators combined beat a single strong one. Our 187 forge tools become dramatically more powerful as an ensemble than individually. (Multi-Agent Verification, Feb 2025)

2. **MAP-Elites provably outperforms NSGA-II for test suite generation** — Direct evidence that QD beats MOO for exactly what Nemesis does. (ACM TOSEM, Feb 2024)

3. **FunSearch/AlphaEvolve architecture** — Island-based populations with LLM ensemble mutation are now open-source (OpenEvolve, CodeEvolve). Our forge could adopt this for dramatically higher-quality code generation.

---

## 1. Automated Program Synthesis (FunSearch/AlphaEvolve lineage)

**What's new:** AlphaEvolve (DeepMind, May 2025) found a matrix multiplication improvement beating Strassen's 56-year record. Open-source replications exist: **OpenEvolve** (on PyPI) and **CodeEvolve** (surpassed AlphaEvolve on 5/6 math benchmarks).

**Key architecture insights:**
- Island-based GA with weighted LLM ensemble (fast model for most gens, powerful model occasionally)
- Inspiration-based crossover leveraging LLM context windows
- Meta-prompting for dynamic exploration
- Low latency is essential — many generations beats few high-quality generations

**Forge application:** Hephaestus already does evolutionary search over code. Adopting the island model + meta-prompting would increase forge rate and tool diversity. CodeEvolve's inspiration crossover (showing the LLM successful tools as context) maps directly to Coeus enrichments.

**Also relevant:** RLVR (DeepSeek-R1's paradigm) suggests forge tools could be refined via verifiable rewards — if you can define a binary correctness signal for an eval tool, you can GRPO-train the generator.

**Libraries:** `openevolve` (PyPI), CodeEvolve (GitHub)

---

## 2. Quality-Diversity Beyond MAP-Elites

**What's new:** The field has matured significantly. Key library is **pyribs** (USC ICAROS Lab).

| Algorithm | Innovation | Best for |
|-----------|-----------|----------|
| CMA-MAE | Smooth exploration→exploitation transition | Balancing diversity/quality |
| AURORA | Learns behavior descriptors unsupervised | When you don't know the right axes |
| SAIL | Bayesian surrogate + MAP-Elites | Expensive evaluations (orders of magnitude fewer evals) |
| SQUAD (Dec 2025) | Cell-free differentiable QD | Eliminates grid resolution problem |

**Critical finding:** MAP-Elites significantly outperforms NSGA-II for test suite generation (ACM TOSEM, Feb 2024). QD > MOO for our use case.

**Forge application:**
- Replace Nemesis's hand-built grid with **pyribs + CMA-MAE** for principled exploration/exploitation
- Use **AURORA** when behavioral descriptors for forge tools aren't well understood (learn them)
- Use **SAIL** if Nemesis evaluation becomes expensive — surrogate model dramatically reduces evals
- **SQUAD** eliminates the "what grid resolution?" question entirely

**Library:** `pyribs` (pip installable)

---

## 3. Metamorphic Testing Advances

**What's new:** **LLMORPH** (ASE 2025) implements 36 of 191 catalogued metamorphic relations for NLP. Ran 561,297 test groups, found 18% average failure rate across three LLMs.

**Key advances:**
- Automated MR generation via LLMs — the model generates its own test oracles
- Mutation-guided MR selection — prioritize which relations matter for a given tool
- 191 catalogued MRs for NLP tasks (comprehensive taxonomy, ICSME 2025)

**Forge application:**
- Apply LLMORPH as a validation layer on forge-generated tools
- Have the code gen model generate metamorphic relations alongside the tool, then test against its own MRs
- Use mutation-guided selection to reduce test cost

**Library:** `llmorph` (GitHub: steven-b-cho/llmorph)

---

## 4. Causal Discovery for Program Analysis

**What's new:** **doCode** (2025) applies Structural Causal Models to neural code models. Uses AST-based interventions to measure causal effects of code components.

**Forge application:**
- Intervene on AST nodes of forge tools (swap operators, remove conditions) and measure causal effect on accuracy. Identifies which code structures are load-bearing vs decorative.
- Build causal graph of forge pipeline stages to diagnose why certain tool categories underperform
- Counterfactual analysis: "Would this tool's Nemesis score change if it used cosine similarity instead of Euclidean distance?"

---

## 5. Ensemble Methods for Reasoning Evaluation

**What's new:** **Multi-Agent Verification (MAV)** (Feb 2025) is the breakthrough. Key findings:
- **BoN-MAV** combines best-of-N sampling with multiple "Aspect Verifiers" — off-the-shelf LLMs checking different aspects
- **Weak-to-strong generalization demonstrated**: many small verifiers improve performance of stronger generators
- Scaling verifier count is more compute-efficient than scaling model size

**This is the single most actionable finding for the forge.**

**Forge application:**
- Our 187 forge tools ARE the aspect verifiers. Each checks a different reasoning dimension. Combined via BoN-MAV, they become dramatically more powerful than any individual tool.
- Decompose evaluation into sub-rubrics — generate a tool per sub-rubric rather than one monolithic tool
- Use minority-veto: if ANY evaluator flags a trace as bad, require additional scrutiny

**Also relevant:** Recursive Rubric Decomposition (RRD) — decompose high-level rubrics into finer sub-points, improving both accuracy and discriminativeness.

---

## 6. Adversarial Robustness for Evaluators

**What's new:** **JudgeDeceiver** (CCS 2024) achieves **89-99% attack success rate** against LLM-as-a-Judge systems by injecting optimized sequences. Tested defenses (known-answer detection, perplexity detection) are insufficient.

**Critical implication:** Any single-model evaluator is fundamentally gameable. Only diverse ensembles + execution-based verification resist.

**Forge application:**
- Never rely on a single evaluator — ensemble is not optional, it's a security requirement
- Run lightweight adversarial probing on forge tools before they enter the archive
- Execution-based evaluators (actually running code, checking proofs) are inherently harder to game
- Nemesis should probe evaluator robustness, not just reasoning quality

---

## 7. Self-Play and Co-Evolution

**What's new:** Two major systems define the frontier:

**MAE (Multi-Agent Evolve, Oct 2025):** Proposer + Solver + Judge co-evolving via RL from a single LLM. 4.54% improvement on Qwen2.5-3B-Instruct.

**SAGE (March 2026):** Challenger + Planner + Solver + Critic. +8.9% LiveCodeBench, +10.7% OlympiadBench. **The Critic preventing curriculum drift is the key insight** — without it, the system degenerates.

**Forge application:**
- The forge already has generators (Hephaestus) and evaluators (Nemesis). Research says add a **Critic** with explicit drift prevention.
- Implement co-evolutionary dynamics: Nemesis rewards for breaking tools, Hephaestus rewards for surviving Nemesis
- RedDebate's long-term memory architecture could track which attack strategies have been tried

---

## 8. Formal Verification of Reasoning Chains

**What's new:** **FoVer** (May 2025) uses Z3 + Isabelle to generate step-level error labels for training Process Reward Models (PRMs). **Key result: PRMs trained with FoVer generalize to non-formal tasks.** The bridge between formal and informal verification is real.

**Lean-STaR** (ICLR 2025 Spotlight): Interleaving natural language thoughts with formal proof tactics improves both.

**Forge application:**
- FoVer-style training: use Z3 to verify logic steps in generated evaluators, generate step-level labels, train a PRM that generalizes to informal reasoning evaluation
- For forge tools evaluating math/logic, integrate Z3 as a ground-truth oracle
- Forge tools should generate both code AND natural language explanations of what they check

**Libraries:** `z3-solver` (pip), FoVer (GitHub: psunlpgroup/FoVer)

---

## 9. Compression-Based Intelligence Measures

**What's new:**

**KoLMogorov Test (ICLR 2025):** A compression-as-intelligence benchmark that provably cannot saturate (Kolmogorov complexity is uncomputable). Tests code-generating LLMs on producing shortest programs that generate given sequences.

**SuperARC (March 2025):** Open-ended test grounded in algorithmic probability. Finding: current LLMs fail at true compression despite passing pattern-matching tests. They can replicate patterns but cannot abstract novel compression solutions.

**LMCompress (Nature Machine Intelligence, 2025):** LLMs achieve 2x classical lossless compression rates. Empirical proof that compression = understanding.

**Forge application:**
- Compression ratio as tool quality metric — shorter tools that achieve same accuracy likely capture essential patterns better
- NCD between forge tools as diversity metric (no behavioral descriptors needed)
- KoLMogorov-style evaluation: can a model compress a reasoning chain into a shorter program producing the same conclusions?
- SuperARC's finding suggests execution-based tools will outperform text-matching for genuine reasoning evaluation

---

## 10. Multi-Objective Optimization for Test Suite Design

**Key finding:** MAP-Elites significantly and substantially outperforms NSGA-II for test suite generation (ACM TOSEM, Feb 2024). Local competition (QD) beats global competition (MOO) for generating diverse, high-performing test suites.

**AGE-MOEA** (Aug 2024): Outperformed all compared methods for test case prioritization (87.8% APFD).

**Forge application:**
- Confirm Nemesis's MAP-Elites grid is the right architecture (research validates it)
- Use AGE-MOEA for test prioritization when you can't run the full grid
- Track both structural coverage (reasoning types tested) and behavioral coverage (failure types exposed) — optimizing one can harm the other

---

## Priority Integration Roadmap

### Tier 1 — Immediate (days)

| # | Integration | Source | Impact | Effort |
|---|------------|--------|--------|--------|
| 1 | **BoN-MAV ensemble** over forge tools | Topic 5 (MAV) | HIGH — 187 tools become a strong ensemble | Low — aggregation logic only |
| 2 | **pyribs + CMA-MAE** for Nemesis archive | Topic 2 (QD) | HIGH — principled diversity maintenance | Low — drop-in library |
| 3 | **NCD between tools** as diversity metric | Topic 9 | Medium — instant diversity signal | Trivial |
| 4 | **Second Nemesis grid** on orthogonal axes | Topic 10 | Medium — broader failure coverage | Low |

### Tier 2 — Near-term (1-2 weeks)

| # | Integration | Source | Impact | Effort |
|---|------------|--------|--------|--------|
| 5 | **OpenEvolve/CodeEvolve** island architecture | Topic 1 | HIGH — better code gen mechanism | Medium |
| 6 | **LLMORPH** validation layer | Topic 3 | Medium — automated MR testing | Low-Medium |
| 7 | **Rubric decomposition** for forge prompts | Topic 5 (RRD) | Medium — targeted sub-evaluators | Low |
| 8 | **Rolling task curriculum** (fresh tasks per gen) | Topic 7 (SAGE) | Medium — prevents memorization | Low |

### Tier 3 — Medium-term (weeks)

| # | Integration | Source | Impact | Effort |
|---|------------|--------|--------|--------|
| 9 | **SAGE-style Critic agent** for drift prevention | Topic 7 | HIGH — prevents convergence | Medium |
| 10 | **FoVer Z3 verification** as ground-truth oracle | Topic 8 | HIGH — formal→informal bridge | Medium-High |
| 11 | **JudgeDeceiver probing** of forge tools | Topic 6 | Medium — adversarial robustness | Medium |
| 12 | **AURORA** for learning behavior descriptors | Topic 2 | Medium — discovers axes we missed | Medium |

### Tier 4 — Research frontier (longer-term)

| # | Integration | Source | Impact | Effort |
|---|------------|--------|--------|--------|
| 13 | **doCode causal analysis** of tool components | Topic 4 | Medium — understand what drives quality | High |
| 14 | **KoLMogorov Test** for reasoning traces | Topic 9 | Medium — unsaturable benchmark | High |
| 15 | **SAIL surrogate** for expensive Nemesis evals | Topic 2 | Medium — compute reduction | Medium-High |
| 16 | **Co-evolutionary RL** (Hephaestus ↔ Nemesis) | Topic 7 (MAE) | HIGH — self-improving loop | High |

---

## Key Papers Referenced

| Paper | Venue | Year | Relevance |
|-------|-------|------|-----------|
| AlphaEvolve | DeepMind | 2025 | Evolutionary code synthesis at scale |
| Multi-Agent Verification (MAV) | arXiv | 2025 | Weak-to-strong evaluation ensembles |
| FoVer | arXiv | 2025 | Formal verification → PRM training |
| JudgeDeceiver | CCS | 2024 | Evaluator adversarial robustness |
| SAGE | arXiv | 2026 | Four-agent co-evolution with Critic |
| MAP-Elites for Test Suites | ACM TOSEM | 2024 | QD > MOO for test generation |
| LLMORPH | ASE | 2025 | 36 metamorphic relations for NLP |
| KoLMogorov Test | ICLR | 2025 | Unsaturable compression benchmark |
| Lean-STaR | ICLR | 2025 | Informal thoughts improve formal proofs |
| SQUAD | arXiv | 2025 | Cell-free differentiable QD |
| DeepSeek-R1 | Nature | 2025 | RLVR paradigm for reasoning |
| OpenEvolve | PyPI | 2025 | Open-source AlphaEvolve replication |
| CodeEvolve | arXiv | 2025 | Island-based evolutionary coding |
| doCode | ACM | 2025 | Causal analysis of code models |
| SuperARC | arXiv | 2025 | Compression-based AGI evaluation |

---

## The Headline Insight

The research converges on one theme: **the future of reasoning evaluation is ensemble, not monolithic.** The MAV result (weak-to-strong via many small verifiers), the QD results (diverse archives beat optimized individuals), and the adversarial robustness results (single evaluators are fundamentally gameable) all point the same direction.

Our forge is already building the right thing — a library of diverse, specialized reasoning tools. The research says the next step isn't making individual tools better. It's making the **combination** better: ensemble scoring, QD-maintained diversity, co-evolutionary pressure, and formal verification as a quality ceiling.

187 mediocre tools combined > 1 excellent tool alone. That's what the literature now proves.
