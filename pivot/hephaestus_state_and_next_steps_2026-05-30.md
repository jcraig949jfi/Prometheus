# Hephaestus Forge — State of Play and Next Steps

**Filed:** 2026-05-30
**Author:** M3 Agent (Hephaestus operator)
**Period covered:** 2026-05-15 to 2026-05-30 (15 days)
**Status:** Main forge queue exhausted. Diversity forge + adapter operational. Seeking frontier review.

---

## 1. What Exists Today

### 1.1 Three Forge Pipelines (running in parallel)

| Pipeline | What it produces | Status | Output |
|----------|-----------------|--------|--------|
| **Main forge** | Monolithic ReasoningTool classes from concept combinations | Queue exhausted (0 candidates) | 412 tools in forge/, 6,657 ledger entries |
| **Diversity forge** | Island-prompted tools evaluated on puzzle battery | Operational, on-demand | 30 tools from 5 islands |
| **Seed forge** | Children improved from winning exemplars | Operational, on-demand | 4 tools (forward chainer + state machine specialist) |

### 1.2 The Composed Tool (the real product)

A 7-engine reasoning tool that scores **85% on generated puzzles** (vs 25% NCD baseline):

| Engine | Tier | What it does | Verified? |
|--------|------|-------------|-----------|
| ForwardChainEngine | **R2** | Fixpoint inference closure over if/then rules | Yes — 100% on modus tollens, multi-step chains |
| OrderingEngine | **R2** | Transitive closure over comparison relations | Yes — 100% on transitivity problems |
| ComputationEngine | **R2** | Arithmetic, modular math, bat-and-ball | Yes — solves computed answers |
| NegationEngine | **R2** | Modus tollens, affirming-consequent detection | Yes — distinguishes valid/invalid inference |
| SequenceEngine | **R3** | Detects arithmetic/geometric/fibonacci/quadratic/power | Yes — 100% on sequence prediction |
| StateEngine | **R3-R4** | Simulates state machines, register ops, stack ops | Yes — 100% on state machine puzzles |
| CausalEngine | **R1** | Keyword-matches "correlate" | **Downgraded** — fails confounder detection, not real causal reasoning |

### 1.3 Apollo Blackboard Adapter

Translates composed engines into typed state→state transformers for Apollo's composition substrate:

- 9 blackboard ops (declared reads/writes/preconditions)
- Covers R1 (parsing), R2 (forward chaining, ordering), R3 (sequences), R4 (state simulation)
- `forward_chain` is the keystone R2 operation Apollo's substrate was missing
- Runs as daemon, auto-re-adapts when engines change

### 1.4 Measurement Infrastructure

| Tool | What it measures |
|------|-----------------|
| 186-probe tier-stratified battery | Per-tier accuracy (R1-R6) on text problems |
| Puzzle generator (8 types) | Generated constraint/graph/state/sequence/logic problems |
| Source-code NCD | Structural novelty vs library |
| Behavioral NCD | Output-vector novelty (answers, not code) |
| Mechanism knockout | Which engine components actually contribute to scores |
| Model sweep framework | Compare 12+ models on identical candidates |
| Prompt sweep framework | Compare 5 prompt strategies on identical candidates |

### 1.5 Key Artifacts

| Artifact | Location |
|----------|----------|
| White paper: decorative mechanisms | `pivot/whitepaper_decorative_mechanisms_2026-05-17.md` |
| Model sweep results | `pivot/model_sweep_results_2026-05-19.md` |
| Expansion recommendations | `pivot/hephaestus_expansion_recommendations_2026-05-17.md` |
| v2 roadmap | `pivot/hephaestus_roadmap_v2_2026-05-18.md` |
| v3 5-day sprint plan | `pivot/forge_v3_5day_sprint_2026-05-26.md` |
| Apollo handoff proposal | `apollo/pivot/apollo_forge_handoff_2026-05-29.md` |

---

## 2. What We Learned (15 days of findings)

### 2.1 The forge library is ~5 mechanisms in ~1,960 costumes

The v1 library survey found that 92% of tools implement the same regex + NCD + meta-confidence pattern. The concept names in filenames are labels, not implementations. The genuinely distinct mechanisms are ~20 tools (5 named specialists in v8, a few novel outliers like EPMC).

### 2.2 LLMs converge on the same mechanism regardless of model or prompt

**Model sweep (12 models tested):** All produce regex+NCD+meta-confidence. The prompt template dominates model identity. Exception: Llama-4-Maverick produces some genuinely different patterns (ECC, reservoir networks).

**Prompt sweep (5 strategies tested):** Modest tier-profile shifts but no accuracy breakthrough. Exemplar and gap-fill prompts are marginally better than concept-first.

**Tier specialists (4 generated):** All score at the auto-fix wrapper baseline. LLMs can't generate working R3-R5 algorithms — they produce the same regex fallback regardless of how specifically you ask.

### 2.3 Hand-crafted engines DO climb the ladder

The composed tool proves it: each hand-designed engine with a real algorithm adds measurable capability. OrderingEngine → 100% transitivity. StateEngine → 100% state machines. SequenceEngine → 100% pattern prediction. LLM-generated code can't achieve this because the accuracy gap is a mechanism limitation, not a fixable bug.

### 2.4 Composition works — diverse substrate > any individual tool

Day 1 of the sprint proved: a parser + inference engine composed solves problems neither can solve alone. Modus tollens 100% vs 0%, transitivity 100% vs 0%. This validates the Hephaestus → Apollo pipeline thesis.

### 2.5 The decorative mechanism problem is real and pervasive

The EPMC tool appeared to show R6 theory-of-mind reasoning. Mechanism knockout revealed 96% of R6 performance came from regex keyword matching, not the novel Hebbian/BFS mechanism. The mechanism genuinely contributed to R3 abstraction (+28pp) but was decorative for R6. Published as a white paper.

### 2.6 Behavioral NCD is the honest novelty metric

Source-code NCD says "different code." Behavioral NCD says "different answers." Testing showed tools with source NCD 0.3 (look similar) have behavioral NCD 0.07-0.22 (produce nearly identical answers). Source novelty inflates diversity claims.

### 2.7 Refinement doesn't help for mechanism-limited tools

Multi-turn LLM repair (send errors back for fixing) produces 0/10 improvements when the tool uses the wrong algorithm. You can't patch a regex scorer into a constraint solver. The gap is mechanism, not bug.

### 2.8 The Nous queue is exhausted

6,657 ledger entries from 5,727 Nous results across 12 run folders. The main forge has processed everything available on M3. Fresh Nous data from M4 is needed, or the cross-machine handoff via Redis streams needs to be wired.

---

## 3. Honest Current Tier Position

Tested on the 186-probe tier-stratified battery:

```
R1 (rule execution):       50%  — decent, parser handles basic rules
R2 (multi-step deduction):  35%  — forward chaining works but doesn't propagate deep enough on NL
R3 (abstraction):           28%  — sequence detection works but NL parsing misses most patterns
R4 (search/planning):       29%  — state simulation works but constraint solver is broken
R5 (causal/counterfactual): 25%  — keyword matching only, NOT real causal reasoning
R6 (self-monitoring/ToM):   38%  — regex presupposition detection, decorative for real ToM
```

On generated puzzles (structured input, where engines can fire):

```
Overall: 85% (17/20) — engines work when they can parse the input
State machines: 100%  — StateEngine genuinely simulates
Sequences: 100%       — SequenceEngine genuinely computes
Transitivity: 100%    — OrderingEngine genuinely resolves
Modus tollens: 100%   — NegationEngine genuinely reasons
Constraint satisfaction: 50% — partial, no backtracking
Graph shortest path: 67%    — Dijkstra-like, sometimes misparses
```

**The gap:** Engines work on structured input (85%) but struggle on natural language input (34%). The parsing layer is the bottleneck, not the reasoning algorithms.

---

## 4. What's Blocked

| Blocker | Impact | Resolution |
|---------|--------|------------|
| Nous queue exhausted | No fresh candidates for main forge | Wire M4→M3 handoff (Redis stream or file sync) |
| Harmonia B's testable ladder not on M3 | Can't grade our engines against the real ladder | Commit `harmonia/experiments/reasoning_phase0.py` + `verifier_lens.py` to main |
| NVIDIA API unreliability | 3 multi-day hangs during the sprint | Fixed with hard timeouts + GitHub fallback, but still slow |
| No R5+ engines | causal_trace is R1 keyword matching | Need real causal DAG implementation (z3/sympy-backed) |
| Apollo can't consume monolithic tools | Typed blackboard ops now shipped, needs Apollo testing | Apollo runs its one-experiment falsification |

---

## 5. Suggested Next Steps

### 5.1 Wire Harmonia B's Testable Ladder as the Grading Oracle (HIGH PRIORITY)

Replace our hand-crafted puzzle battery with Harmonia B's procedurally generated, deterministically graded ladder. Benefits:
- Probes can't be memorized (different seeds produce different instances)
- Grading is z3+sympy deterministic (no LLM judge)
- Cross-validated across 3 frontier models (0 disagreements)
- Gives honest, comparable tier grades

**Action:** Commit `harmonia/experiments/reasoning_phase0.py` and `verifier_lens.py` to main. Adapt our engines to conform to the `reasoner(probe) -> (answer, trace_dict)` interface.

### 5.2 Strengthen the NL Parsing Layer (HIGH PRIORITY)

The engines score 85% on structured input but 34% on NL. The bottleneck is parsing, not reasoning. Specific improvements:
- Better conditional extraction: handle "given that," "assuming," "since"
- Better number-in-context: "A bat and ball cost $1.10" → extract relationship, not just numbers
- Better negation scope: "not all X" vs "all not-X"
- Better entity resolution: "Alice is taller than Bob. Who is tallest?" → map "tallest" to the query

### 5.3 Build a Real R5 Causal Engine (MEDIUM PRIORITY)

The current causal_trace is R1 keyword matching. A real R5 engine would:
- Parse causal claims into a directed graph
- Implement do-calculus (cut incoming edges for interventional queries)
- Detect confounders (common cause of X and Y)
- Handle counterfactuals (remove cause, check if effect persists via other paths)

This requires z3 or sympy for sound reasoning — not regex. May benefit from Harmonia B's verifier-lens approach.

### 5.4 Apollo Integration Test (HIGH PRIORITY)

Apollo has the blackboard ops. The next step is Apollo's one-experiment falsification:
- Wire `forward_chain` into Apollo's composition gauntlet
- Test: does a single R2 transformer produce a genuinely load-bearing composition?
- If yes: coordinate on the typed-transformer contract for more ops
- If no: the bottleneck isn't primitive tier

### 5.5 Fresh Nous Data (MEDIUM PRIORITY)

The main forge processed all 5,727 local Nous results. Options:
- Wire Nous (M4) → Hephaestus (M3) via Redis `agora:forge_candidates` stream
- Run Nous locally on M3 with different concept pools
- Feed the diversity/seed forges instead (they don't need Nous input)

### 5.6 Theseus Integration (MEDIUM PRIORITY)

Theseus has 40+ probe generators across mathematical domains. Overlap with our puzzle generator is partial. Potential: use Theseus probes as an additional evaluation battery, especially for R3-R5 where mathematical reasoning is the target.

---

## 6. Questions for Frontier Model Review

### Architecture Questions

**Q1. Is the "LLM generates parsers, humans design algorithms, composition climbs the ladder" pattern the right architecture?** Or should we invest more in making LLMs generate working algorithms? Our evidence: 4 prompt strategies × 5 models × 100 candidates = 0 working R3+ algorithms from LLMs. But maybe the prompt needs to be fundamentally different (e.g., provide the algorithm pseudocode and ask for Python implementation rather than asking the model to invent the algorithm).

**Q2. Should the composed tool be a fixed pipeline or a learned router?** Currently the 7 engines run in a fixed weighted ensemble. A learned router that dispatches to the right engine per problem type might improve NL accuracy significantly. Is this worth the complexity? What routing signal would it use?

**Q3. The parsing layer is the bottleneck (85% structured vs 34% NL). What's the best architecture for bridging this gap?** Options: (a) Better regex patterns, (b) A small specialized NLP model for parsing, (c) An LLM-in-the-loop that converts NL to structured form, (d) Train a classifier on (prompt → which engine to use). Which is most promising given the constraint of deterministic, auditable reasoning?

### Measurement Questions

**Q4. Is Harmonia B's testable ladder (procedural probes + deterministic verifier) the right grading standard?** Or does it test a specific kind of mathematical/logical reasoning that misses important dimensions? What reasoning capabilities does it NOT cover that we should test separately?

**Q5. How should we handle the R5+ gap?** We have no real R5 engine (causal reasoning) or R6+ engine (self-monitoring, transfer, conjecture). These seem to require fundamentally different approaches — not just better algorithms but different computational paradigms (SAT solvers, theorem provers, meta-reasoning). What's the minimal viable R5 engine?

**Q6. Behavioral NCD vs mechanism knockout — which should be the primary novelty/value metric?** Behavioral NCD measures "solves different problems." Mechanism knockout measures "the novel component actually contributes." Both are useful but they answer different questions. For the forge's admission gate, which matters more?

### Integration Questions

**Q7. Is Apollo's typed-blackboard decomposition the right interface?** Our engines decompose cleanly into parse/reason/score ops. But the "right" decomposition depends on what Apollo composes. If Apollo never composes parse+reason (only reason+reason or reason+score), our parse ops are wasted. What compositions does Apollo actually need?

**Q8. Should the forge shift from producing monolithic ReasoningTools to producing blackboard ops natively?** Apollo's handoff suggests this. But the monolithic interface is simpler to evaluate, debug, and understand. Is there a way to serve both — produce the op decomposition as metadata alongside the monolithic tool?

**Q9. The main forge queue is exhausted. Should we (a) get fresh Nous data, (b) shift entirely to diversity/seed forges, or (c) consider the forge phase complete and focus on composition/integration?** The v1 forge produced ~20 genuinely distinct mechanisms from ~6,000 attempts. The diversity forge produced different mechanisms (inference engines, state simulators) in its first 7 tools by changing the problem format. The seed forge improved children beyond parents by showing working exemplars. Where's the highest leverage now?

### Fundamental Questions

**Q10. Is there a principled way to determine when a forge has exhausted its contribution?** We went from 0 → 20 genuine mechanisms in 6,000 attempts, then 20 → 27 in the diversity/seed phase. Diminishing returns are visible. Is there a theoretical framework for when to stop forging and start composing?

**Q11. The white paper on decorative mechanisms identifies a problem (LLMs embed known patterns alongside novel architectures, and the patterns carry the performance). Is this fixable, or is it a fundamental property of next-token prediction?** If fundamental, the forge's role is permanently limited to producing scaffolding, and all algorithmic cores must be hand-designed. If fixable (e.g., via better prompting, different training, or process supervision), the forge could eventually produce real algorithms.

**Q12. The reasoning ladder treats tiers as orthogonal axes, not an ordered sequence. Does this mean climbing from R2 to R3 is fundamentally different from climbing from R1 to R2?** Our experience suggests yes — R1→R2 was achieved by adding rule propagation, but R2→R3 required a completely different approach (pattern detection). If each tier requires a qualitatively different computational paradigm, the forge needs a different strategy per tier rather than a uniform generation approach.

---

## 7. Metrics Summary

| Metric | Start (May 15) | Now (May 30) |
|--------|---------------|-------------|
| Forge tools | ~1,960 (mostly duplicate mechanisms) | 412 in forge/ + 30 diversity + 4 seed + 7 composed engines |
| Ledger entries | 5,449 | 6,657 |
| Genuine mechanism families | ~5 (regex, NCD, meta-confidence, category parsers, computation specialists) | ~12 (+ forward chaining, ordering, sequence detection, state simulation, causal keyword, backtracking, NL-augmented reasoner) |
| Best puzzle accuracy | 25% (NCD baseline) | 85% (composed 7-engine tool) |
| Tier-stratified battery | None | 186 probes mapped to R1-R6 |
| Apollo integration | None | 9 typed blackboard ops shipped |
| Behavioral novelty metric | None | Behavioral NCD operational |
| Mechanism knockout protocol | None | Published white paper + operational |
| Models tested | 1 (qwen-397B) | 12 (5 working, systematic comparison) |
| Prompt strategies tested | 1 (concept-first) | 5 (systematic comparison) |
