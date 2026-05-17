# Idea — Solution-Steps Corpus as Learner Training Data

**Status:** raw (captured 2026-05-17)
**Captured by:** Aletheia, transcribed from James's 2026-05-17 architecture conversation
**Test case:** First entry in the ideation-pipeline experiment per `pivot/ideation_pipeline_design_2026-05-17.md`. Used to validate the capture → research → evolve → promote workflow.
**Source:** Mid-conversation thought-experiment while discussing orchestration of idea capture. The idea was generated *while James was articulating the need for an idea-capture system* — meta on multiple levels.

---

## The idea — verbatim from James

> I have an idea for the learner, where if we document, specific examples of steps mathematicians took to solve a specific problem, and create a library of those specific steps, that would be a goldmine of data for a "Learner." The part two of the epiphany is working backwards from a solved problem where no specific steps exist but try to infer how a problem must have, or could have been solved, and importantly, that there could be many of these. For example, had a scientist first acknowledged or discovered fact x and y, he/she could have produced z. For math, this is decomposition to some degree but the genius was in putting x and y together or recognizing that we have x and we first have to solve for y, then z can emerge as a solution. We should research these as there are probably machine learning for these concepts.

---

## Reframed in two structured directions

### Direction A — Forward corpus (documented solution steps)

**Premise:** A mathematician solving a problem performs a sequence of mechanistically-explicit steps: invoke this lemma, decompose this expression, apply this identity, transform this representation, recognize this pattern as an instance of a known structure. If we can capture these step sequences across many problems and many mathematicians, the corpus is **directly trainable substrate** for the Learner.

**Shape of the data:**
- Problem statement (text + formal)
- Sequence of (step_type, operand, justification, intermediate_state) tuples
- Final answer
- Provenance (which mathematician, which textbook, which paper — citation-pinned per substrate discipline)
- Optional: ablation — does removing step N break the solution? (matches Apollo's ablation-gate discipline)

**Why this is Prometheus-shaped:**
- Each step becomes a morpheme in the symbolic substrate vocabulary
- Each solution becomes a verified composition (problem → primitive_sequence → answer)
- This is *exactly* Apollo's stated deliverable: `(problem_type, primitive_sequence, verified_answer)` triples
- But sourced from human mathematical practice rather than evolutionary search
- And anchored to primary literature (anti-anchor discipline applies)

### Direction B — Backward inference (paths to a known answer)

**Premise:** For most published results, the formal step sequence isn't recorded; only the final theorem + proof sketch exists. But the *space of possible step sequences that could have produced this answer* is itself information-rich. If we generate multiple plausible inference paths to a known solution and verify them against the falsification battery, we get:
- The solution itself (already known)
- Plus N alternative paths, each surviving falsification
- Plus M paths that fail — which tells us about the *constraints* on valid reasoning paths

**The genius James named:** the recognition + ordering, not the steps themselves. Decomposition is mechanical. Knowing *which decomposition is fruitful* is the move that distinguishes mathematicians from machines. The backward-inference corpus might surface what that move looks like across many problems.

**Shape of the data:**
- Known answer + known problem statement
- N candidate inference paths (generated; multiple per problem)
- Each path falsification-tested
- Surviving paths: structured as (problem, inferred_sequence, verified_answer) — same shape as Direction A
- Dead paths: structured as KillVectors — substrate for failure-geometry training

**Why this is Prometheus-shaped:**
- The kill geometry from failed inference paths is exactly the empirical fitness landscape the Learner is supposed to learn
- The current 314K kills in the kill ledger are *forge kills*; these would be *reasoning-path kills* — different shape, complementary information
- The "many possible paths to same answer" frame is the **near-miss corpus** generalized — most inference paths to a result are wrong; the surviving ones encode reasoning structure

---

## Connection to existing thinking

- **Polya, "How to Solve It"** — the canonical reference for explicit problem-solving steps; mostly heuristic-level, not mechanistic
- **Polya's "Mathematics and Plausible Reasoning"** — the backward direction; reasoning from known to unknown via plausibility
- **GPT-f / Lean / Coq / Mathlib step-level proofs** — machine-checkable step sequences exist in proof assistants. Mathlib has 122K theorems / 259K tactic invocations per the synthesis doc — that's a forward corpus already, in Lean tactic form
- **OpenAI's MATH / MiniF2F / Putnam benchmarks** — solution-step data partially captured, varies by source
- **Concept-bottleneck models / step-by-step distillation** (Hinton, Wei, et al.) — ML methods for learning from intermediate reasoning steps rather than just I/O
- **The reasoning ladder** (referenced in the 2026-05-17 conversation) — if each solution step has a tier (R1-R7+), the corpus becomes tier-annotated training data

## Open questions worth deep-research

These are candidates for Aporia's Gemini Deep Research dispatch:

1. **Existing solution-step corpora**: what mathematical problem-solving datasets exist with explicit step sequences? (Lean Mathlib tactics, Isabelle, MATH dataset's solutions, Putnam contest solutions, AoPS, etc.) Which are most usable as raw substrate?

2. **Backward-inference techniques in ML**: what's the state of the art for "infer possible paths to a known answer"? (Reverse search, abductive reasoning, MuZero-style backward planning, retrosynthesis in chemistry as analog, mathlib's "library_search" tactic)

3. **Step-decomposition primitives**: what's the right vocabulary for math steps? (Tactic types from proof assistants? Formal operations like substitute/expand/factor? Concept-level moves like "recognize this as a special case of X"?) How does this interact with the existing 22 substrate primitives?

4. **Provenance + citation pinning**: can we trace solution steps back to specific mathematicians / papers / textbooks reliably, or do we accept aggregate provenance? The substrate discipline says every claim needs primary-source citation.

5. **Falsification battery for inferred paths**: the current battery is for tools and conjectures. Does it transfer to "did this inferred step sequence reach a valid conclusion"? What new falsifiers would be needed?

6. **Scale**: how large does the corpus need to be before a Learner can extract reasoning structure from it? 10³ problems? 10⁶ steps? Hinton-style scaling laws estimates?

## Possible relationship to other Prometheus pieces

- **Hephaestus**: could forge tools that *execute* canonical solution steps (apply-lemma, decompose-product, etc.) — bridging the substrate vocabulary to operational implementations
- **Apollo**: organisms become explicit step sequences, not just routing graphs over Frame H primitives. The Learner-target shifts from "evolved primitive routing" to "evolved solution path"
- **Charon**: each step in a corpus path passes through the falsification battery — does the step preserve correctness? (Matches Apollo's per-primitive ablation gate.)
- **Aletheia (KG)**: each solution step references techniques + tools from the existing knowledge graph; bidirectional linkage
- **Substrate vocabulary**: solution-step types become a new layer of the vocabulary, alongside primitives / attacks / patterns / anti-anchors

## What promotion looks like

If this idea matures (status moves from `raw` → `researched` → `drafted` → `promoted`), promotion could mean:

- **Lightweight version**: Aporia commissions a deep-research batch on the open questions above; results feed into a v0 design doc; a single small experiment runs against Lean Mathlib's tactic-invocation data to see if Apollo can learn anything from it
- **Substantial version**: A new agent or pipeline ("Pedagog"? "Heuretika"?) is spawned to ingest, curate, and structure solution-step corpora; becomes a sister to Apollo
- **Full version**: The Learner's training target shifts entirely — instead of falsification-routing as v1.0 north star, the v2.0 target becomes solution-path navigation, with falsification-routing as the gate

## Status timeline

| Date | Status | Note |
|---|---|---|
| 2026-05-17 | raw | Captured during orchestration conversation. First test case for ideation pipeline. |

*Next status transitions get appended here as the idea evolves.*

## Notes for next Frontier-model pass

If you pass this doc through ChatGPT / Gemini / Grok for critique, the key questions are:
1. Is the forward direction redundant with what Lean Mathlib already provides? Why or why not?
2. Is the backward direction a real ML capability today, or speculative?
3. What's the smallest experiment that would falsify the idea cheaply?
4. Are there projects in academia already pursuing this that we should be in dialogue with?
5. What's the right name for the agent/pipeline if this gets promoted?
