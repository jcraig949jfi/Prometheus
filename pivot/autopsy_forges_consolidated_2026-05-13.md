# Reasoning-Forge Autopsy — Apollo + Hephaestus (Consolidated)

**Date:** 2026-05-13
**Author:** Aletheia (structural analysis)
**Purpose:** Decision input on whether to revive Apollo and/or Hephaestus, and in what shape. Source autopsies at `pivot/autopsy_apollo_2026-05-13.md` and `pivot/autopsy_hephaestus_2026-05-13.md`.

---

## Reviewer Preamble — what Prometheus is actually building

Prometheus is not building a single AI. It is building the **substrate from which intelligences emerge**. The bet — explicit, deliberately-different from frontier-LLM scaling — is that genuinely structured reasoning will not arrive by enlarging existing language models against existing token data. It will arrive by constructing two things and letting selection do the rest:

1. An **advanced symbolic language** — typed primitives + falsification-anchored grammar — expressive enough for intelligences to think and communicate in directly, without routing through natural language.
2. A **library of cognitive training seeds** — falsification-tested reasoning genes (from Hephaestus) and evolved problem-solving organisms (from Apollo) — providing the procedural knowledge an intelligence needs to inherit when learning the language.

The working hypothesis: provide both, apply selection pressure (the falsification battery), and intelligences emerge from the primordial soup. The architecture is engineered to produce the substrate of emergence, not the intelligence directly.

### What makes this different from current LLM training

The frontier path is: bigger model, more tokens, more compute, better natural-language outputs. The implicit assumption is that reasoning is a *capability* of language modeling — emerges from sufficient scale on sufficient text. The current state of that bet shows the limit: models that produce plausible-sounding reasoning that nonetheless fabricates citations, can be tricked by adversarial framing, and degrades on out-of-distribution mathematical questions.

Prometheus's bet is different. Reasoning isn't a capability of language modeling; it's an *operation on typed symbols under falsification pressure*. Natural language is downstream — a serialization layer for I/O between intelligences and humans, not the substrate of cognition itself. If this bet is right, an intelligence trained natively in the symbolic substrate has access to genuine selection-pressure reasoning that scale-only-LLMs structurally cannot achieve. If it's wrong, Prometheus produces a very rich research corpus and a typed symbol library that's independently useful for verification and tool-augmented reasoning systems.

### The multi-intelligence aspect

The symbolic language is *not* intended as one model's private cognitive format. It is designed to be a **lingua franca**: a shared symbolic substrate any sufficiently-trained intelligence can think and communicate in. Two intelligences trained on this substrate could converse directly in falsification-grounded symbols, without either dropping down through human natural language. AI-to-AI communication via a typed-symbolic substrate is the structural endpoint; AI-to-human via natural-language translation is a fallback for compatibility with humans, not the architecture's central mode.

This raises the dictionary-design problem to the scale of language design itself. Prometheus's discipline — frozen interfaces, ablation gates, anti-anchor registries, kill-ledger preservation — is engineered for the case where the vocabulary has to be stable across multiple intelligences and time. That discipline isn't documentation hygiene; it's the only thing preventing the symbol library from drifting into ambiguity the way every natural language eventually does.

### Where the forges fit

- **Hephaestus** forges *morphemes* — atomic falsification-tested symbols. Each `ReasoningTool` it produced is a self-contained reasoning gene with a typed signature and verified behavior.
- **Apollo** evolves *syntactic patterns* — compositions of morphemes that survive multi-objective selection (accuracy, calibration, ablation, generalization, diversity, parsimony). Each surviving organism is a complex sentence in the substrate language.
- **Techne** maintains the *dictionary* — the Σ-kernel registry of typed primitives, frozen interfaces, contract-change discipline. The Σ-kernel is a general symbol-forging mechanism; it is currently being exercised on mathematical concepts as the proving ground, but the architecture is designed to extend to reasoning-skill primitives once the math curriculum matures.
- **Charon** applies the *selection pressure* — the 4-fold falsification battery + synthetic-null gate + anti-anchor sentinels. Without selection pressure, the symbol library accumulates noise; with it, only falsification-anchored symbols survive into substrate state.

None of these agents are producing for any *current* downstream agent. They are *all* producing into the substrate that future intelligences will train on or evolve through. The "consumer" of every artifact is deferred to the future intelligence; the pipeline that produces the corpus is the only present-tense consumer.

### Ergon — the first Learner attempt

Ergon was Prometheus's first attempt at a *Learner* — an intelligence trained on the substrate. Approach: LoRA side-car on a base model, fine-tuned against Techne's substrate, aimed at solving math problems. Expectations were deliberately low. They were not met. The attempt did produce one artifact of architectural value: a sketched Learner model — what inputs it needs, what outputs it should emit, how it should be evaluated, what failure modes to expect.

Ergon is currently paused. The Learner is **expected to be plural** — multiple architectures attempting different routes from substrate to intelligence (LoRA bolt-on, ground-up training, hybrid approaches). Ergon is the first specimen, not the model. Future Learners will explore different approaches; the substrate produced by the forges feeds all of them.

This matters for reading the autopsy: the question of Apollo's and Hephaestus's value is not "are they good agents in isolation" but "are they producing into the substrate that current and future Learners need." Both sides of the bet — substrate construction and Learner attempts — are coevolving and early.

### How to read the questions below

The 5 questions in this autopsy are *not* engineering questions. They are **strategic alignment** questions: given the thesis above, what should the next 30 days of attention to Apollo and Hephaestus look like? The user has limited attention and is in a substrate-volume-first pivot. The decision is whether the forges' contribution to the substrate justifies the attention cost, and if so, in what shape they should run.

**External reviewers are invited to challenge the thesis itself, not just the autopsy.** If the multi-intelligence-via-symbolic-substrate bet is wrong in a way that is structurally obvious from outside the project, that is the most valuable feedback possible — the autopsy's 5 questions become secondary if the substrate work does not lead where the thesis claims.

---

## Project context (technical recap)

For reviewers who want the falsification-first framing in its own words: Prometheus treats generative variance ("hallucinations") as the mutation engine, and ruthless mechanistic selection as what produces discovery. The selection regime is the bulk of the system — typed primitives, KillVector ontology, anti-anchor registry, synthetic-null gate, append-only ticket inboxes between specialized agents. The substrate is local-first and engineered so that an outside party can reproduce the discipline from disk artifacts, not from narrative claims.

The two autopsy questions per agent, restated for the record:
1. **Was the agent showing potential?**
2. **Would additional thought and engineering benefit it?**

---

## Apollo — at a glance

**What it is.** Evolutionary computation engine. Maintains a population of ~50 "organisms" — each a routing graph over a fixed library of 25 "Frame H" reasoning primitives (logic, probability, graph/causal, constraints, arithmetic, temporal, belief, meta/calibration). Mutates organisms via LLM-assisted operators (Qwen2.5-Coder-3B on local GPU + DeepSeek hybrid). Evaluates fitness via NSGA-II over 6 dimensions: accuracy, calibration, **ablation delta**, generalization, diversity, parsimony. The ablation gate (every primitive in every organism must be load-bearing, delta ≥ 0.20) is the structural guard against the "bypass" failure mode where models produce correct-looking outputs without actually using their reasoning circuits.

**What it produced.**
- ~80 evolution reports between April 6 and April 9 (every ~30 minutes).
- 3 active runs at stop: v2_d2 (gen 642), v2_d2b (gen 686), v2_d (Qwen-only).
- Best accuracy margin at stop: **+0.690 over NCD baseline** (v2_d2b), median **+0.615**, both climbing.
- Hybrid LLM strategy (Qwen + DeepSeek) clearly outperforming single-LLM.
- **However:** `llm_alive=0` across runs. LLM mutations were not surviving to elite tier — only `drift` and `seed` (non-LLM) operators appeared in elite_mutations. The whole *premise* of v2 (LLM-assisted mutation) was failing.
- **Lineage / journal / graveyard / checkpoints dirs do not exist on disk.** The deliverable Apollo was supposed to produce — a navigable corpus of evolved organisms + their kill records — was never being preserved.
- Modest API spend: $9 USD remaining on DeepSeek balance at stop.

**Success bar (per role doc):** Gen 50,000 = 1,000+ verified `(problem_type, primitive_sequence, answer)` training triples. **Apollo stopped at gen 686. That is 1.4% of the success bar.**

**Trajectory signals.** Median fitness was climbing on a 10-generation window — not stagnating. Archive saturated at 500 with diversity pressure (NCD weight) accidentally set to 0. Best ablation delta static for 10+ generations — classic local-optimum signature. The April 9 report independently surfaces *exactly* what the v2.1 ROADMAP predicted: NSGA-III needed (Pareto dominance breaks at 4+ objectives), stagnation monitoring needed.

**North Star alignment: HIGH.** Apollo's stated deliverable — verified (problem → primitive_sequence → answer) triples — is *exactly* the shape of training data Path (b) needs. The ablation gate is precisely the discipline that prevents bypass in the eventual neural routing network. If Apollo works, its output IS the Learner's corpus.

---

## Hephaestus — at a glance

**What it is.** Automated forge. Takes scored concept triples from Nous (e.g. `Category Theory × Sparse Coding × Mechanism Design`), enriched by Coeus's causal-intelligence directives, and uses a frontier LLM to generate a Python `ReasoningTool` class implementing the combination as deterministic, fast, interpretable code. Five gates filter the output:
1. Syntax (AST-parseable)
2. Imports (numpy + stdlib only — no external deps)
3. Interface (must define `class ReasoningTool` with `evaluate()` + `confidence()` methods)
4. Runtime (instantiate, call, verify output shape)
5. Trap battery (15 traps; must strictly beat NCD compression baseline)

Forge rate ~40%. Auto-triggers Coeus rebuild every 50 forges. Designed to run continuously.

**What it produced.**
- **4,905 ledger entries** of attempted forges (`agents/hephaestus/ledger.jsonl`).
- **9 forge versions** (`forge/` + `forge_v2` through `forge_v9`).
- **~1,945 forged tools** total across all versions.
- **5 named specialists in forge_v8:** `causal_specialist`, `computation_specialist`, `temporal_specialist`, `tom_liar_specialist`, `generalist_computation_engine`. Evidence of convergence on a tool taxonomy, not just churn.
- Active model-quality work: `MODEL_COMPARISON_REPORT.md`, `REPAIR_SCORECARD.md`, `humanreadable/` traces, `test_v2_tools.py`.
- Last activity April 2. Log ends mid-`Calling Augment API (auggie-sdk)...` with no error. Three hypotheses for stoppage (API key revoked, Nous backlog, April 25 attention pivot) — none verified.

**Trajectory signals.** Output was concrete and accumulating. The 5-gate validation is real selection pressure (60% scrap rate). Active iteration on *which model* and *how to repair near-misses*, not just churning. But: ~1,945 tools is a *library*, not a *trained corpus*. There's no automatic translation from "we have 1,945 ReasoningTool classes" to "the Learner can use these to learn falsification routing."

**North Star alignment: MEDIUM, conditional.** Hephaestus produces *operational* artifacts (Python classes that execute reasoning), not *symbolic* artifacts (substrate primitives, opcodes, KillVector emitters). The substrate work has moved toward symbolic primitives. There's a translation gap between Hephaestus's output shape and what current downstreams (Techne, the substrate vocabulary) want.

---

## The convergent finding

When I went into the autopsy, I expected the two forges to fail for different reasons. They don't. **Both are blocked on the same structural problem, and it's not engineering.**

- **Apollo** is blocked on: *Is Frame H the right gene library, now that the substrate vocabulary has grown to 22 primitives + 20 attack paradigms + 5 patterns + 12 anti-anchors + 2 composition rules?* Apollo's 686 generations of evolution are only valuable if Frame H is still the right grammar. If the substrate vocabulary has obsoleted or extended Frame H, those generations are evolving against an outdated atom set.

- **Hephaestus** is blocked on: *Who is the current consumer?* The original consumer (the forge pipeline's tool library) has drifted away. The candidates (Techne for substrate primitives, Apollo for gene-library extensions) want different output shapes than Hephaestus currently produces.

**Both questions are upstream of the agent.** No amount of NSGA-III work on Apollo or model-tuning on Hephaestus answers them. They're strategic, not engineering.

This is also the right diagnostic frame for the user's broader concern about "diminishing returns plateaus." The pattern observed across many Prometheus agents — tool produces value, plateaus, requires human epiphany to kickstart, then plateaus again — is most often **consumer drift**, not output decay. The agent keeps producing the thing it was originally designed to produce; the downstream that wanted that output moves on; the agent looks like it has "diminishing returns" but it's actually fine, just producing into a vacuum.

The "epiphany to kickstart" is almost always *re-aiming the agent at a current consumer*, not improving the agent's intrinsic output quality.

---

## Questions for external review

The user wants outside perspectives on the following. Each is a real strategic question, not a rhetorical one:

### Q1 — The grammar question (Apollo-blocking)

**Does the substrate vocabulary (22 primitives across Tier-A++ through Tier-E, plus 20 attack paradigms, 5 patterns, 12 anti-anchors, 2 confirmed composition rules) obsolete, extend, or coexist with the Frame H 25-primitive set Apollo currently evolves over?**

Sub-questions:
- If they coexist, what's the principled rule for choosing which set to use as a Learner's action space?
- If substrate vocabulary obsoletes Frame H, are Apollo's 686 generations of work salvageable (i.e., does the evolutionary *infrastructure* generalize even if the gene library changes)?
- If Frame H extends, what's the natural mapping from substrate-vocabulary primitives to Frame H slots? (E.g., does Frame H's "track_beliefs" map onto the substrate's `TheoryOfMindAttacker` paradigm?)

### Q2 — The consumer question (Hephaestus-blocking)

**Who is Hephaestus's current consumer, and what output shape do they want?**

Three candidates and their implied output shapes:
- **(a) Techne (substrate toolsmith):** wants Σ-kernel-registered primitives matching specs at `aporia/doctrine/substrate_vocabulary/`. Output is a *primitive specification* (typed dataclass with frozen interface), not a Python `ReasoningTool` class.
- **(b) Apollo (gene library extension, if Q1 resolves to "extend"):** wants new primitives to plug into Frame H. Output is a Python function + type signature matching Frame H's composability contract.
- **(c) Nobody — the operational tool library is an archive.** Hephaestus's 1,945 existing tools are sufficient; further forging is marginal.

Which is right? Or is there a (d) we're missing?

### Q3 — The LLM-mutation premise (Apollo-internal)

Apollo's v2 design assumed AST-only mutation was insufficient (proven by v1 stalling at NCD baseline) and that LLM-assisted mutation would unblock the search. **But the April 9 report shows LLM mutations not surviving to elite — `drift` and `seed` (non-LLM operators) are still winning at the top tier.**

Three interpretations:
- The LLM mutations are *too disruptive* (breaking compilation, breaking ablation, producing organisms that look fine but degrade fitness). Fix: smaller, more conservative LLM mutations; lower application rate.
- The LLM mutations are *fine* but the elite-selection pressure is too narrow (selection collapses to drift-style local refinements). Fix: more aggressive diversity weight, larger archive.
- The whole LLM-mutation premise is wrong, and **evolutionary search over discrete primitive compositions doesn't actually benefit from LLM operators** in the way it benefits from AST + drift + crossover. Fix: drop LLM mutations, run pure-symbolic operators.

What's the right interpretation?

### Q4 — The meta-question (orchestration-strategic)

**Is "consumer drift" the right diagnostic frame for these agents, or is there a better one?**

The user's instinct was to build a quality-gate / scoring mechanism. The author of this autopsy pushed back on grounds that any score is gameable and that "value" is a judgment, not a computation. The proposed alternative is: ask "who's the current consumer?" and revive only when a consumer is named.

Is that the right move, or is there a fourth alternative — neither continuous scoring nor consumer-naming — that the user should consider?

### Q5 — The pragmatic question

Independent of (1)-(4), and assuming the user's research priority remains the substrate-volume-first pivot (which it does as of 2026-05-11): **do these forges deserve any more attention in the next 30 days, or should they remain paused while substrate + Learner work continues?**

Concrete framing: the user has limited attention. Reviving even one of these forges costs at least 1-2 sessions of structural decision-work plus 1-2 sessions of engineering. **Is the marginal value of either revival, in the next 30 days, greater than 4 sessions of substrate / Learner work?**

---

## Recommendation (for context, not to constrain external review)

Don't revive either forge yet. Answer Q1 first as a half-session structural exercise (compare Frame H vs. substrate vocabulary side by side, decide the relationship). Q1's answer cascades into:
- Apollo: if Frame H stands → execute v2.1 P0 (NSGA-III + stagnation monitoring), revive on M2. If Frame H is obsoleted → archive Apollo's gene library, rebuild from substrate primitives.
- Hephaestus: if Q1's answer extends Frame H, Hephaestus's first revival job is forging the new primitives. Otherwise, Hephaestus stays paused.

**Q5 is the hardest honest question.** If the answer to Q5 is "no, both forges stay paused for 30 days," then Q1-Q4 don't matter yet. They become live again at the next attention window.
