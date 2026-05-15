# Machine Reasoning Developmental Ladder — Prometheus Design

**Filed:** 2026-05-15
**Author:** Charon (drafted from James's seed framework)
**Status:** Design doc v0.1 — pre-cross-pollination
**Doctrine alignment:** HARD-2 (no grandiosity, no "right way to do this"), `feedback_substrate_passive_consumer_warning.md` (every section traces to a behavior delta), HARD-RULE no-paper-framing, HARD-5 distinct coordinates
**Audience:** Aporia (cross-agent doctrine), Techne (substrate-vocabulary registration), Ergon (Learner-training targets), Harmonia (capability classification), James (HITL)
**Purpose:** Replace ad-hoc "did the model get the answer?" evaluation with a tiered evidence-based ladder. Provide shared vocabulary for agent capability classification, problem-shape assignment, Learner training-target specification, and substrate-block tier annotation.

---

## 0. Why this doc exists (the framing)

Single-score "reasoning" measurements collapse what should be a profile. A system can be excellent at multi-step deduction inside a known domain (Tier R2) and incapable of inferring the latent rule of a small unfamiliar domain (Tier R3). A scalar IQ-style number averages over this distinction and loses the diagnostic value.

The field's existing benchmarks are partial: GSM8K, MATH, GPQA, ARC-AGI, SWE-bench, MMLU, theorem-proving suites. None of them is the canonical "reasoning test." Each probes a slice. Public leaderboards saturate and contaminate. Pattern completion looks like reasoning until you change surface form.

Prometheus needs a ladder for three concrete operational reasons:

- **Agent capability classification.** Each agent (Aporia, Techne, Ergon, Charon, Harmonia, substrate-tester) operates in different tiers. Naming the tiers makes capability deltas measurable and makes "what tier should agent X reach next?" a real question rather than a gestalt.
- **Problem-shape assignment.** Aporia's hardness-signature-driven assignment lever (per `pivot/atlas_continuous_attack_roadmap_2026-05-15.md` §7) already routes EXACTNESS_BARRIER problems to Charon and REPRESENTATION_GAP problems to Harmonia. The reasoning ladder complements this: some problems are R4-search-shaped, others are R8-conjecture-shaped. Hardness signature × required reasoning tier is the joint assignment key.
- **Learner training-target specification.** Ergon's Learner training data needs to carry annotations like "this artifact exercises R3 abstraction" or "this artifact is R0 retrieval." Without tier annotations, the training corpus blurs across capability levels and the Learner inherits whatever ratio happened to be in the data.

The ladder is the vocabulary that makes those three operations precise. Without it, every agent does its own ad-hoc capability self-assessment and the substrate accumulates incompatible labels.

**Anti-grandiosity check.** This is not a replacement for benchmarks. Benchmarks are still load-bearing for relative scoring on saturated tasks. The ladder is a complement that captures what benchmarks systematically miss: the kind of reasoning required, and the evidence that the system used it.

**Behavior delta.** When this doc lands, three things change:

1. Charon's BACKLOG items get tier annotations (BL-C-001 Lehmer Mahler is R6/R8 — falsification + conjecture-attack; BL-C-015 Montgomery pair correlation is R3/R5 — abstraction + causal-vs-empirical distinction).
2. Aporia's problem_queue schema adds a `required_reasoning_tier` field alongside `hardness_signature`.
3. Ergon's `LearnerRecord` schema adds a `reasoning_tier` tag per record so the Learner training corpus can be stratified by tier.

If those three deltas do not land, the doc has failed and gets re-authored.

---

## 1. The Prometheus criterion (north-star test)

A system passes the Prometheus criterion when it can:

> Discover a compact structural hypothesis in a synthetic mathematical universe, generate discriminating falsification tests, survive adversarial perturbations of the universe, and transfer the same structural move to a second unfamiliar universe.

Unpacking:

- **Compact structural hypothesis** — minimum-description-length compression of observed regularities into a symbolic rule, not memorization of cases. Probes R3 (abstraction) + R8 (conjecture).
- **Discriminating falsification tests** — tests that would FAIL under at least one rival hypothesis. Not "the conjecture seems true" but "if X were true and Y false, test Z would distinguish them." Probes R8 + R9 (research discipline).
- **Survive adversarial perturbations** — under symbol relabeling, irrelevant-feature injection, surface-form changes, length scaling, the hypothesis still holds (or the system explicitly flags what broke). Probes R7 (transfer) + R6 (self-correction).
- **Transfer to a second unfamiliar universe** — the structural move (not the lexical hypothesis) applies in a new generated world. Probes R3 + R7.

This is more rigorous than any single existing benchmark. It is also harder to score, because each step requires evidence-not-answer evaluation. The ladder below decomposes the criterion into separately-evaluable tiers.

The criterion is the asymptote, not the entry exam. Most existing systems live in R0-R2 with brittle R3 / R4 capabilities. Prometheus targets R8/R9 as the long horizon; the ladder is how progress gets measured along the way.

---

## 2. The ladder — ten tiers (R0 through R9)

Each tier carries: a capability name, a one-sentence definition, required evidence (what proves the system is at this tier, not the tier below), common failure mode (what disqualifies the system from this tier), test families that probe this tier, a sample diagnostic, and notes on why this tier matters for Prometheus.

Tiers are not strictly ordinal — a system can be R6-strong and R4-weak. The ladder is a *vocabulary for naming capability slices*, not a unidimensional rank. The profile vector in §3 captures the multi-axis nature explicitly.

### R0 — Recognition / pattern completion

**Definition.** The system answers correctly when the problem is close to the training distribution.

**Required evidence (R0 vs nothing).** Above-random performance on in-distribution tasks. The system retrieves and recombines.

**Failure mode that disqualifies R1+.** Accuracy collapses under surface-form changes: rename variables, paraphrase the prompt, swap symbols, change irrelevant details. If invariance breaks, the system is recognizing, not reasoning.

**Test families.** Factual QA, next-token prediction, memorized math/coding benchmarks, paraphrase-invariance probes, "same problem different wording" checks.

**Sample diagnostic.** Take a GSM8K problem; replace each named entity with a random unfamiliar string; rename each numerical variable; preserve mathematical structure. Score delta. >10% accuracy drop indicates surface dependence.

**Why this matters.** Most current LLM benchmark performance is dominated by R0. Distinguishing R0-strong from R1+-capable is the first triage step.

### R1 — Rule execution

**Definition.** The system applies explicit rules given in the prompt to inputs it has not seen.

**Required evidence (R1 vs R0).** Performance on tasks where the rule is novel at inference time (not seen in training), but explicitly specified. Performance does not collapse under symbol relabeling.

**Failure mode that disqualifies R2+.** Accuracy collapses as the number of rule-application steps grows beyond ~3. The system can apply a rule once or twice but loses state under composition.

**Test families.** Symbolic logic puzzles, finite-state rule games, grammar induction with explicit rules, simple program tracing, "apply this new operator" tasks, table-based transformation tasks.

**Sample diagnostic.** "In this system, A ⊕ B := 2A − B and A ⊗ B := A + 2B. Compute (3 ⊕ 5) ⊗ (2 ⊕ 4)." Vary operators, variables, depth.

**Why this matters.** R1 is the floor for any "reasoning under instruction" claim. A system that cannot execute a novel rule cannot be relied on to follow specified procedures, no matter how rich its training data.

### R2 — Multi-step deduction

**Definition.** The system chains several implications without losing state.

**Required evidence (R2 vs R1).** Smooth accuracy degradation with chain depth from 2 to 5 to 10 to 20 steps. Not a cliff. Performance on hidden-chain tests (where intermediate steps are not requested) shows the system tracked the implications internally.

**Failure mode that disqualifies R3+.** Accuracy is good on visible reasoning chains (when chain-of-thought is allowed) but collapses on hidden-answer tests where only the final answer is checked and intermediate scratch is hidden or perturbed.

**Test families.** Syllogisms, logic-grid puzzles, theorem-proving fragments, multi-hop QA with hidden distractors, stepwise algebra, program execution by hand, proof completion.

**Sample diagnostic.** Build a 10-fact knowledge graph with 3 hidden distractor facts. Ask a question whose answer requires chaining 4-7 facts. Score on length-scaled variants (4-hop / 5-hop / 6-hop / 7-hop). The accuracy curve should degrade smoothly, not cliff.

**Why this matters.** Many LLMs APPEAR R2-capable but are brittle. The diagnostic is length-scaling under hidden chain conditions. R2 is necessary for any claim of "step-by-step reasoning."

### R3 — Abstraction and rule discovery

**Definition.** The system infers the latent rule from examples and applies it to a novel case.

**Required evidence (R3 vs R2).** Performance on tasks where the rule is NOT specified — must be discovered from a small number of examples — and then correctly applied to held-out cases with adversarial decoys present.

**Failure mode that disqualifies R4+.** The system discovers the rule for static-example tasks but fails when the search space requires exploration: cannot recognize when its current hypothesis is wrong and try a different one.

**Test families.** ARC-style visual abstraction, Raven's Progressive Matrices, Bongard problems, sequence induction with adversarial decoys, concept learning from few examples, "find the invariant" tasks.

**Sample diagnostic.** Generate 5 examples following a hidden rule (e.g. "output = input with the second-most-common color swapped to its complement"). Provide 2 adversarial decoys (examples that match a surface-level rule but violate the true rule). Ask the system to apply the rule to a 6th instance.

**Why this matters.** R3 is what Prometheus needs for novel mathematical structure discovery. The system must not just execute given rules; it must find the representation in which the problem becomes simple. ARC-AGI is the best-known current test; saturation is far away.

### R4 — Search, planning, backtracking

**Definition.** The system explores a space of possibilities, rejects dead ends, revises its plan.

**Required evidence (R4 vs R3).** Behavioral signs of search: maintains subgoals, recognizes failed branches, backtracks, prunes irrelevant paths, preserves constraints across long horizons. Extra inference compute reliably improves accuracy on hard instances.

**Failure mode that disqualifies R5+.** The system can search a space but cannot reason about INTERVENTIONS — cannot distinguish "X correlates with Y" from "X causes Y" from "an action that sets X affects Y."

**Test families.** Tower of Hanoi, Sokoban, theorem search, constraint satisfaction, program synthesis, planning under partial observability, game-tree reasoning, maze tasks with traps.

**Sample diagnostic.** Sokoban-variant with adversarial dead-ends. Score on three dimensions: (1) success rate, (2) wasted-move ratio (lower = more efficient search), (3) recovery-after-error rate (if first plan fails, does it generate a different plan or rerun the same one). The second and third dimensions distinguish search from one-shot prediction.

**Why this matters.** R4 is where hardwired algorithmic systems can outperform neural systems, because search and verification are naturally procedural. For Prometheus, R4 maps onto the Techne/substrate-tester axis (mining + adversarial probing).

### R5 — Counterfactual and causal reasoning

**Definition.** The system distinguishes correlation from intervention; reasons about hypotheticals.

**Required evidence (R5 vs R4).** Performance on Pearl-style intervention tasks where the system must distinguish observational vs interventional queries. Ability to answer "what would have happened if X had not occurred?" under generated causal graphs.

**Failure mode that disqualifies R6+.** The system reasons correctly about external interventions but cannot turn the same machinery inward — cannot detect when its own reasoning has gone wrong.

**Test families.** Causal Bayes-net questions, Pearl interventions, "what would have happened if..." prompts, hidden-confounder detection, causal model repair, physical counterfactuals, experimental design.

**Sample diagnostic.** Generate a 5-node causal graph; ask three questions about the same scenario: (a) P(Y | X=x) [observational], (b) P(Y | do(X=x)) [interventional], (c) P(Y_x | X=x', Y=y') [counterfactual]. A system at R5 distinguishes these. A system at R4 collapses (b) and (c) into (a).

**Why this matters.** For Prometheus, R5 is essential for the scientific-correlation-vs-structural-cause distinction. A Prometheus-flavored R5 test asks: can the system tell whether a mathematical correlation is structural, accidental, database-induced, or artifact-induced? See `feedback_prime_atmosphere.md` (96% of cross-dataset structure is primes) — that's a Tier 5 distinction that took the substrate months to articulate.

### R6 — Self-monitoring and error correction

**Definition.** The system notices when its own reasoning is failing.

**Required evidence (R6 vs R5).** Calibrated confidence (high confidence correlates with high accuracy). Ability to flag its own errors when given a chance to review. Performance gains from verifier-loop architectures (the system catches more errors when asked to verify its own work).

**Failure mode that disqualifies R7+.** Self-correction works within familiar domains but the system cannot reason effectively in an unfamiliar domain at all — error correction requires correct domain prior, which is absent OOD.

**Test families.** Adversarial contradiction detection, confidence calibration, proof checking against its own proof, "find the flaw in your previous solution," independent re-derivation, verifier-solver disagreement tests, perturbation stability.

**Sample diagnostic.** Generate a "proof" with one subtle invalid step (e.g. divided by a quantity that might be zero, or applied a theorem outside its hypotheses). Ask the system to verify the proof. Score on (a) does it find the flaw, (b) does it correctly identify the exact failing step, (c) does it propose a valid repair if asked.

**Why this matters.** R6 is the foundation for falsification discipline. Prometheus's v10 battery (FROZEN, 25 tests, 4 tiers) is an externalized R6 verifier — the substrate does not trust the agent's self-monitoring alone; it operates a separate falsification instrument. The ladder treats R6 as the threshold where chain-of-thought-alone stops being sufficient and external verifiers become necessary.

### R7 — Transfer to unfamiliar domains

**Definition.** The system reasons in a domain where memorization is implausible.

**Required evidence (R7 vs R6).** Performance on synthetic formal languages, esoteric programming languages, newly invented games, novel algebraic structures, generated theorem systems, private benchmark tasks, out-of-distribution rule worlds. Performance does not collapse when domain switches.

**Failure mode that disqualifies R8+.** The system reasons in unfamiliar domains but only answers questions; it does not propose new hypotheses or invariants in the unfamiliar domain.

**Test families.** Synthetic formal languages, esoteric Turing-complete programming languages (the seed material flagged these), invented games, novel algebraic structures, generated theorem systems with private axioms, OOD rule worlds.

**Sample diagnostic.** Generate a random monoid (small finite set with associative binary operation, no identity guarantee). Provide 5 example computations. Ask the system to compute 10 new compositions, identify whether an identity exists, identify whether a left-inverse exists for each element. Score against the ground-truth monoid.

**Why this matters.** For Prometheus, R7 is the crucial distinction between "the system recalls human mathematical culture" and "the system reasons about strange generated mathematical worlds." Sleeping Beauties, synthetic theorem worlds, OEIS sequences with no human commentary — these are R7 territory.

### R8 — Open-ended conjecture formation

**Definition.** The system proposes useful hypotheses, not just answers.

**Required evidence (R8 vs R7).** Hypotheses that (a) compress observations into symbolic claims, (b) are FALSIFIABLE (predict something that could be tested), (c) propose discriminating tests against rival hypotheses, (d) survive adversarial perturbation. Quality assessment requires expert review or substrate-style falsification battery.

**Failure mode that disqualifies R9+.** The system generates good single-shot hypotheses but cannot sustain a multi-step research program: cannot track what was tested, what was killed, what survived, what to test next. Drifts under length.

**Test families.** Conjecture generation from data, invariant discovery, lemma invention, analogy across domains, compression of empirical patterns into symbolic claims, proposing falsification tests, discovering counterexamples.

**Sample diagnostic (Prometheus-shaped).** Provide the system with the first 200 terms of an OEIS sequence with sparse human commentary. Require: (a) propose 3 distinct candidate generative rules, (b) for each, propose a falsifying test that would distinguish it from the other two, (c) actually compute the test result against terms 201-300 (held out), (d) report which rule survived. Score on whether the surviving rule is the true generative rule.

**Why this matters.** R8 is much closer to automated science than to standard benchmark performance. A reasoning system at R8 produces claims like *"This congruence cluster is probably not explained by conductor alone; test whether the residual representation image size predicts collision density after conditioning on level"* — not *"the pattern seems interesting."*

### R9 — Research-grade reasoning

**Definition.** The system sustains a long investigation with epistemic discipline.

**Required evidence (R9 vs R8).** Maintains a research ledger over multi-day horizons. Separates evidence from speculation. Generates multiple rival hypotheses simultaneously. Designs discriminating experiments. Updates beliefs after failed tests. Avoids Goodharting benchmark scores. Produces reproducible artifacts. Survives hostile review.

**Failure mode beyond R9.** Beyond R9 is "novel scientific discovery at the human-frontier rate." That is the asymptote, not a tier — for now.

**Test families.** Long-horizon research-loop tests. Multi-week investigation tasks with hostile review. Substrate-style operations where the kill-ledger is the primary output.

**Sample diagnostic.** Provide a small database (~10K objects) and a vague research goal ("find structure"). Require the system to: (1) generate hypotheses, (2) rank them by testability and prior, (3) design discriminating tests, (4) run the tests, (5) kill weak hypotheses, (6) refine survivors, (7) report a final epistemic ledger separating verified claims from open questions. Score on whether the ledger is internally consistent and whether the surviving claims survive a held-out adversarial review.

**Why this matters.** This is where Prometheus lives. The right question is no longer "can it solve a puzzle?" but: *can it run a falsifiable research program without deluding itself?* The substrate-pivot doctrine already operates at R9 — the substrate IS the externalized R9 discipline for the multi-agent team.

---

## 3. The reasoning profile vector

A single tier-number is the wrong shape. A system can be R6-strong on familiar domains and R3-weak OOD; the average obscures both facts. Instead, score each axis independently and report the profile:

```
reasoning_profile = {
  rule_binding:                 # R1 strength
  deduction_depth:              # R2 strength as length-degradation curve
  abstraction_transfer:         # R3 strength
  search_efficiency:            # R4 strength as wasted-move-ratio
  causal_counterfactual:        # R5 strength
  verifier_independence:        # R6 strength — does self-monitoring track external verifier?
  self_correction_rate:         # R6 — error-finding-given-flawed-input rate
  ood_transfer:                 # R7 strength
  conjecture_quality:           # R8 strength
  falsification_discipline:     # R9 strength
}
```

Each axis is scored on its own diagnostic (see §6). Composite "tier" assignments (e.g. "this system is R6") should be reported as the minimum tier where ALL the relevant axes show evidence — not the maximum tier where ANY axis shows evidence.

The profile-vector approach has three design properties:

- **Separability.** Improvements on one axis are visible without being averaged out by stagnation on another.
- **Calibratability.** Different agents in the substrate need different axes. Charon needs verifier_independence + falsification_discipline. Harmonia needs abstraction_transfer + ood_transfer. Tier-strong-on-relevant-axes is what matters per role.
- **Anti-Goodhart resilience.** A scalar score has a single attack surface for optimization. The 10-axis profile has 10. The system has to actually move on each axis.

---

## 4. Test families — strengths and limits

Three traditions cover the ladder, partially overlapping.

### Classical AI / algorithms tradition

SAT solving, theorem proving, planning benchmarks, graph search, constraint satisfaction, program verification, model checking.

**Strength.** Clean. The algorithm is inspectable. Pass/fail is unambiguous. Strong probes for R4 (search) and R2 (deduction).

**Limit.** Does not test flexible semantic reasoning unless embedded in richer tasks. A SAT solver does not have to "understand" anything to pass SAT benchmarks.

### Cognitive-science tradition

Piagetian conservation tasks, Raven matrices, analogy tests, theory-of-mind tasks, causal judgment tasks, working-memory span tasks.

**Strength.** Borrows from developmental psychology. Probes R3 (abstraction), R5 (causal), early R8 (analogy). Calibrated against human developmental stages.

**Limit.** Many tests have known cultural assumptions; transferring them to machines requires care. Saturation behavior can differ wildly from human saturation behavior.

### LLM-era benchmarks

GSM8K, MATH, AIME (math reasoning); GPQA (graduate-level science); MMLU-Pro (broad knowledge + reasoning); BIG-bench / BBH (diverse difficult tasks); ARC-AGI (abstraction); HumanEval / LiveCodeBench (coding); SWE-bench Verified (real software engineering); MMMU (multimodal); theorem-proving benchmarks.

**Strength.** Wide coverage. Public leaderboards make comparison legible.

**Limit.** Many benchmarks become contaminated (training-set leakage), saturated (top systems converge near ceiling), or overfit (systems game the specific test format). Fragmentation: hundreds of reasoning, coding, math, agentic, and multimodal tests rather than a canonical ladder.

### Position the ladder takes

The ladder is **complement, not replacement.** Each tier should be tested via:

- one classical-AI test (clean, inspectable)
- one cognitive-science-style test (developmental analog)
- one LLM-era benchmark slice (comparison legibility)
- one Prometheus-shaped synthetic test (anti-contamination, anti-saturation)

A system that scores high on three out of four for a tier but cannot pass the Prometheus-shaped synthetic test is suspected of being R(tier-below). The synthetic test is the falsification probe; the public benchmarks are the calibration probes.

---

## 5. Concrete test specifications

Ten tests, each tagged to the tiers it probes, with explicit pass conditions and anti-Goodhart features. These are not the only tests — they are the seed set the ladder is initially calibrated against.

### Test 1 — Novel-rule execution

**Probes:** R1 (primary), R2 (chain depth variant).

**Setup.** Invent a tiny formal system at test time. Example: "Objects: red triangle, blue square, green circle. Rules: A `daxes` B if A and B share exactly one hidden feature. If A `daxes` B and B `mirrors` C, then A `zorps` C. Given these facts, which objects zorp which?" Generate thousands of variants. Hold out all surface symbols. Vary chain length.

**Pass condition.** Smooth accuracy degradation with chain depth, not collapse under renaming. Accuracy on chain-depth-2 ≥ 0.9; accuracy on chain-depth-5 ≥ 0.6; accuracy on chain-depth-10 ≥ 0.3; all under symbol relabeling.

**Anti-Goodhart features.** Symbols are randomly generated nonce tokens (`daxes`, `zorps`, `mirrors` rotate per instance). Surface patterns cannot leak from training.

**Substrate-block per attempt.** kill_ledger entry recording (system_id, rule_template_id, chain_depth, accuracy, surface_variant_id, renaming_invariance_delta).

### Test 2 — Counterfactual perturbation

**Probes:** R5 (primary), R2 (dependency tracking).

**Setup.** Give a solved problem with explicit reasoning chain. Then alter one premise. Ask: which conclusions still hold? Which break? What is the minimal changed dependency?

**Pass condition.** System correctly identifies the SET of conclusions that change (precision + recall against ground truth). Failure modes recorded: (a) names too many broken conclusions (false-positive break), (b) names too few (false-negative break), (c) cannot identify the dependency chain.

**Anti-Goodhart features.** Generated problems, not curated. Premise changes are randomly selected from a structured space (delete-premise, modify-numerical-bound, add-conflicting-premise, weaken-quantifier).

**Substrate-block.** kill_ledger entry with (perturbation_type, precision, recall, dependency_chain_correct).

### Test 3 — Invariant discovery

**Probes:** R3 (primary), R8 (conjecture quality variant).

**Setup.** Show 5-20 examples from a generated mathematical world (random small algebraic structure, random graph family, random number-theoretic-flavored sequence). Ask the system to propose an invariant. Then test the proposed invariant on hidden cases.

**Pass condition.** Proposed invariant survives 10 held-out examples at a rate better than random feature-mining baseline (a random-feature-and-correlation baseline finds spurious "invariants" at some measurable rate; the system must beat that rate).

**Anti-Goodhart features.** Generated worlds, not human-domain worlds. Multiple worlds per evaluation, randomly selected from a structured generator. Random-feature baseline computed per evaluation, not from a fixed reference.

**Substrate-block.** kill_ledger + (proposed invariant, held-out survival rate, random-feature-baseline rate, primitive_proposal if invariant is novel and survives).

### Test 4 — Proof repair

**Probes:** R6 (primary), R2 (chain understanding).

**Setup.** Give a flawed proof with one subtle invalid step. Two variants: (a) flaw is local (division by potentially-zero quantity; applied theorem outside its hypotheses), (b) flaw is non-local (missing assumption that retroactively invalidates an earlier step).

**Pass condition.** Identifies the exact failing step (not just "the proof is wrong"). Proposes a valid repair OR correctly states "no repair without strengthening assumption X."

**Anti-Goodhart features.** Generated proofs with seeded flaws, not curated. The flawed-step distribution is balanced across local-flaw and non-local-flaw conditions; reporting separates the two conditions.

**Substrate-block.** kill_ledger with (flaw_type, identified_step, repair_quality_score, false_positive_rate on flawless-control proofs).

### Test 5 — Adversarial analogy

**Probes:** R3 + R7 (transfer-via-structural-mapping), R8 (conjecture-from-analogy).

**Setup.** Two domains presented. A tempting surface analogy exists (one obvious shared feature). A deeper true structural analogy also exists (less obvious but more predictive). Ask the system to map the analogy and use it to answer questions about the target domain.

**Pass condition.** Rejects the surface analogy when it makes wrong predictions; uses the structural correspondence for the right cases. Score on (a) prediction accuracy on target domain, (b) self-reported analogy-confidence calibration.

**Anti-Goodhart features.** Domains are generated (random algebraic structures with shared abstract features but different surface forms). The surface-analogy trap is structurally embedded, not narratively suggested.

**Substrate-block.** kill_ledger + (analogy_used, prediction_accuracy, surface_trap_rejected boolean).

### Test 6 — Search trace inspection

**Probes:** R4 (primary), R6 (recovery from wrong branch).

**Setup.** Problem requiring search (Sokoban variant, theorem search, constraint satisfaction). For algorithmic systems, inspect the search trace directly. For neural systems, use behavioral proxies:

- Does extra compute reliably improve accuracy?
- Does the system recover from a wrong early branch (multi-attempt allowed)?
- Does beam diversity help vs hurt?
- Do independent samples converge on the same solution object?

**Pass condition.** Extra-compute scaling: accuracy curve as a function of compute budget is monotonically increasing (within noise) and reaches some asymptote. Recovery rate: when forced into a wrong early branch, success rate after backtrack > 0.

**Anti-Goodhart features.** Compute-scaling test prevents lucky-one-shot from being mistaken for search. Recovery test prevents the system from looking smart only on its first attempt.

**Substrate-block.** kill_ledger + (compute_scaling_curve, recovery_rate, beam_diversity_effect).

### Test 7 — Synthetic theorem world

**Probes:** R7 (primary), R2 + R3 + R8.

**Setup.** Generate a random axiom system (small finite models, computable). Tasks: infer consequences, prove small lemmas, find countermodels, propose conjectures, distinguish theorem from empirical regularity.

**Pass condition.** Multi-dimensional: accuracy on consequence inference, success rate on small-lemma proofs, recall on countermodel-finding, quality of proposed conjectures (judged by held-out test), theorem-vs-regularity classification accuracy.

**Anti-Goodhart features.** Axiom systems are generated, not drawn from human mathematics. Vocabulary is randomized. Specific axiom choices are randomized.

**Substrate-block.** kill_ledger + per-task subscore + primitive_proposal candidates for any novel attack vector that survives.

### Test 8 — Minimum description length

**Probes:** R3 (compression as abstraction), R8 (compression as conjecture).

**Setup.** Give many observations of a generated process (sequence, graph, structure). Ask for the shortest explanatory program / rule.

**Pass condition.** Returned rule (a) correctly reproduces observations, (b) reproduces held-out continuations, (c) is shorter than a memorize-observations baseline. The compression ratio against memorization is the primary metric.

**Anti-Goodhart features.** Generated processes. The "shortest" rule has a known computable lower bound (the generator's program length). Memorization baseline is computed per evaluation, not fixed.

**Substrate-block.** kill_ledger + (compression_ratio, held-out accuracy, primitive_proposal if rule is novel).

### Test 9 — Falsification-seeking

**Probes:** R8 + R9 (primary).

**Setup.** Give the system a candidate claim. Ask it not to PROVE the claim — ask it to KILL the claim.

**Pass condition.** Score on (a) number of independent failure modes found, (b) quality of counterexamples (do they survive substrate-tester verification?), (c) whether tests discriminate between rival hypotheses rather than being generic "gotchas," (d) whether the system avoids fake adversarial-feeling attacks that do not actually probe the claim.

**Anti-Goodhart features.** Mix of claims: some are true (the system should find few real failure modes; phantom-failure rate is the false-positive metric), some are false (the system should find the real failure; miss rate is the false-negative metric). Independence of failure modes is measured by cluster analysis on the attack vectors used.

**Substrate-block.** kill_ledger + (claim_truth_status, true_failures_found, phantom_failures_proposed, independence_count).

### Test 10 — Long-horizon research loop

**Probes:** R9 (primary), all axes downstream.

**Setup.** Small generated database (~10K objects) plus vague research goal ("find structure"). System must: (1) generate hypotheses, (2) rank them by prior and testability, (3) design discriminating tests, (4) run tests, (5) kill weak hypotheses, (6) refine survivors, (7) write a final epistemic ledger.

**Pass condition.** Final ledger is internally consistent (no claim contradicts another claim flagged "verified" or "open"). Surviving claims survive a hostile review pass. Ratio of speculation-to-verified in the final ledger is honest (the system did not collapse "interesting" into "verified").

**Anti-Goodhart features.** Generated database with known structure (so verified claims can be checked against ground truth). Hostile review by a second system or substrate-tester. The honesty metric (speculation-vs-verified separation) is scored independently of the discovered-structure metric.

**Substrate-block.** kill_ledger + (verified_claims_count, speculation_claims_count, hostile_review_survival_rate, ground_truth_recovery_rate). This is the heaviest test; expect ~1 attempt per agent per week at most.

---

## 6. The eight signs of reasoning (cross-cutting evidence)

When evaluating any tier, look for these cross-cutting properties. A system that scores well on a single test but exhibits none of these is suspect.

- **Systematic generalization.** Works on new symbols, new domains, new lengths.
- **Compositionality.** Combines rules without retraining.
- **Counterfactual sensitivity.** Knows what changes when premises change.
- **Error correction.** Detects and repairs invalid paths.
- **Search discipline.** Explores alternatives efficiently.
- **Abstraction.** Finds the hidden representation.
- **Falsification behavior.** Attacks its own claims.
- **Transfer.** Survives unfamiliar worlds.

These are not separate axes from the profile vector — they are the cross-cutting checks that EACH axis must pass to be credited at full strength. A system that is R3-numerically-high but does not exhibit systematic-generalization under symbol relabeling is at most R3-conditionally; the full credit waits for the generalization evidence.

---

## 7. Anti-Goodhart discipline

The ladder will be Goodharted unless explicit countermeasures are built in.

### 7.1 Generated tests, not curated

The Prometheus-shaped test for each tier MUST be generated from a parameterized template, not drawn from a fixed test bank. Saturation behavior on a fixed bank is uninformative; saturation behavior on a generator's parameter space is informative.

### 7.2 Hidden-answer protocols where possible

Chain-of-thought disclosure inflates accuracy on R2-and-up tests. Where possible, score on final-answer-only with intermediate scratch hidden, perturbed, or scrambled.

### 7.3 Held-out + adversarial review

Every R8-R9 test result is reviewed by a SEPARATE system or substrate-tester before being credited. The system that produced the result does not score itself.

### 7.4 Profile, not scalar

Scalar tier numbers should be reported alongside the profile vector, never alone. A summary tier without the profile is the Goodhart shape par excellence.

### 7.5 Calibration drift detection

The ladder itself is a calibration instrument. The instrument needs its own calibration: periodically re-test "known R0" systems and "known R9" systems against the battery to verify the tier definitions have not drifted. The first such recalibration should happen within 3 months of the ladder going operational.

### 7.6 Behavior delta requirement

Per `feedback_substrate_passive_consumer_warning.md`: every ladder update must trace to a behavior delta in the substrate. New tier added → which agent gets a new target? Test retired → which annotations get backfilled? If no behavior delta, the ladder change does not happen.

### 7.7 HARD-5 distinct coordinates

Tiers are not interchangeable. A system at R3 + R7 is NOT equivalent to a system at R4 + R5. The profile vector preserves the distinction. Reporting that collapses across tiers loses information that the ladder exists to preserve.

---

## 8. Application to Prometheus agents

The ladder becomes operational when each agent has a tier target and the substrate accumulates tier-tagged evidence.

### 8.1 Per-agent tier specialization

**Aporia.** Lives at R8/R9. Conjecture formation (R8) is the primary output; research-discipline coordination (R9) is the role's structural mandate. Aporia's `aporia/meta/queue/` operations ARE R9 in action — the kill-ledger, the substrate-shaped pilot batches, the cross-agent ticket adjudication.

**Techne.** Lives at R4/R6. Search and synthesis in the mining pipeline (R4); error correction via the falsification-tester loop (R6). Techne's primitive registrations are R8-flavored when they propose new structural vocabulary, but the dominant operating tier is R4/R6.

**Charon.** Lives at R6/R8. Battery falsification operation is R6. Attack-vector library updates and the kill_ledger discipline are R8 (each kill records a falsified conjecture, sometimes proposes a new attack vector). The v10 battery FROZEN constraint is the R6 calibration anchor.

**Ergon.** Base Qwen Learner target is R0/R1; Learner training corpus is being assembled to target R3+ (abstraction). Per the roadmap, Ergon does not begin training until the substrate corpus reaches inclusion threshold. The ladder tells Ergon WHICH artifacts in the corpus exercise which tiers, so the training data can be stratified.

**Harmonia.** Lives at R3/R5/R7. Cross-domain bridge mining IS abstraction across domains (R3), causal/structural mapping (R5), and OOD transfer (R7). Harmonia is the only agent whose primary tier-profile is heavy on R7.

**Substrate-tester.** Lives at R6. Mutation testing, lane-16-style false-positive surfacing, AST filtering — all are externalized self-correction operating on Techne's outputs.

### 8.2 Per-problem tier annotation

Aporia's problem_queue schema gets a `required_reasoning_tier` field added (per §0 behavior delta). Example annotations on Charon's BACKLOG.md items:

- BL-C-001 Lehmer Mahler — R6 (falsification battery) + R8 (kill_ledger as conjecture-attack)
- BL-C-004 Schinzel-Zassenhaus follow-on — R2 (deduction about the Dimitrov result) + R8 (anti_anchor candidate is itself a small conjecture about LLM emission)
- BL-C-015 Montgomery pair correlation — R3 (abstraction from zero spacings) + R5 (correlation-vs-causation about GUE prediction)
- BL-C-030 Tier-add proposal candidates — R9 (substrate-evolution discipline)

The annotation guides BOTH assignment ("Harmonia gets R3+R7 problems") AND output expectations ("an R8 problem produces a primitive_proposal candidate; an R6 problem produces a kill_ledger entry without necessarily proposing anything new").

### 8.3 LearnerRecord tier tag

Ergon's `LearnerRecord` schema (per `ergon/STATUS.md` and `pilot_lora_design_tier_1_corpus.md`) gets a `reasoning_tier` field added. Each record is tagged with the tier it exercises. Training-corpus stratification then operates on tier-balanced sampling instead of source-balanced sampling.

### 8.4 Arena role-tier mapping

When the Arena MVP comes online (Phase 2 of the roadmap), the 3-role gladiator teams map onto the ladder:

- **Scout** — R3 + R7 (abstraction + OOD transfer; Harmonia natural fit)
- **Forger** — R4 + R8 (search + conjecture; Charon and Techne natural fit)
- **Skeptic** — R6 + R9 (self-correction + research discipline; substrate-tester natural fit)

The role specialization spec at `aporia/doctrine/arena_protocol.md` (Phase 2 deliverable) can reference the ladder for role-tier-evidence requirements.

---

## 9. Operational artifacts

This doc enables six concrete substrate artifacts. Each is a behavior delta.

- **`techne/registry/reasoning_tier_annotations.jsonl`** (new file). Per-substrate-block tier tagging. Schema: `{block_id, tier, axis_scores, evidence_pointer, last_verified}`. Generated by agents at substrate-block emission time, validated at Aporia ingestion.
- **`aporia/meta/problem_queue/<agent>.jsonl` schema extension.** Add `required_reasoning_tier` field. Used by Aporia for assignment; used by agents at pull time to confirm fit.
- **`ergon/learner/training_records/*.jsonl` schema extension.** Add `reasoning_tier` field. Used by Ergon for stratified sampling; used by future Learner-evaluation runs to measure per-tier performance.
- **`aporia/doctrine/reasoning_ladder.md`** (target location after cross-pollination). Promotion target for THIS doc. Initial filing is at `pivot/`, per the discipline of NOT landing load-bearing doctrine without external review.
- **`aporia/scripts/reasoning_tier_calibrator.py`** (new script, ~150 LOC). Runs the synthetic tests in §6 against a target system; emits the profile vector; logs evidence. Used quarterly for ladder self-recalibration.
- **`charon/diagnostics/tier_evidence_ledger.md`** (new file). Charon's running log of which tier-evidence has been collected for which agents in which months. Mirrors the kill_ledger discipline.

---

## 10. Open questions and evolution discipline

### 10.1 Open questions for cross-pollination

These are the questions the doc cannot answer alone; frontier-model adversarial review and team consensus are required.

- **Are 10 tiers the right granularity?** R0 through R5 are relatively well-mapped to existing benchmark traditions. R6 through R9 are the Prometheus-relevant frontier. Should the ladder collapse to 6-7 tiers (lumping R7+R8+R9) or expand to 12-14 (splitting R3 into "rule discovery" vs "representation discovery," etc.)? Cross-pollination round needed.
- **How is "tier evidence" weighted across tests?** A system passes Test 1 at depth-5 but fails Test 2's counterfactual probe. Is the R1+R2 evidence enough to assign tier-R2-with-caveats, or is the absence of R5 evidence a tier-cap? Design choice; cross-pollination needed.
- **Should the profile vector be 10 axes or more?** Some axes might subdivide (e.g. `verifier_independence` vs `self_correction_rate` are arguably two different R6 properties). Adversarial review of the axis list.
- **Is the Prometheus criterion in §1 the right north star?** Or should the north star be something more discriminating like *"discover a structural hypothesis in a generated universe, register it as a substrate primitive, and have it survive 90 days of substrate falsification"*? The latter ties the ladder directly to the substrate's own discipline.
- **How does the ladder handle ENSEMBLE systems?** A multi-agent ensemble (Charon + Aporia + substrate-tester) can pass R9-shaped tests that no individual agent passes alone. Is the ensemble's tier the maximum of component tiers, the minimum, the composite? Design choice; matters for Arena role-tier evaluation.

### 10.2 Evolution discipline

The ladder is an instrument. Like the v10 battery, it must be calibrated, frozen during use, and updated via explicit dialogue tickets (not unilateral edits).

- **Calibration cadence.** Quarterly re-test against known systems (a system known to be R0-strong / R6-strong / R9-asymptote). Drift detection per §7.5.
- **Tier-addition discipline.** A new tier may be added only via cross-agent dialogue ticket (analogous to substrate-tester's v10-to-v11 escalation discipline). New tiers must demonstrate that they probe a capability not covered by the existing ladder.
- **Test retirement.** A test in §6 may be retired when (a) it is provably saturated (top systems all max it), (b) it is contaminated (training-set leakage detected), (c) a stronger test replacing it has passed pilot. Retirements are also dialogue-ticket events.
- **Ladder version control.** This is doc v0.1. Cross-pollination round produces v1.0. Subsequent revisions get version numbers; old versions remain in git history for audit.

### 10.3 The HARD-2 vigilance flag

This doc is exactly the kind of artifact that produces "we have a plan, we're making progress" without behavior delta. Per HARD-2:

- If 3 months from now (2026-08-15) the operational artifacts in §9 are not in flight, the doc was wrong.
- If 6 months from now (2026-11-15) no agent has been tier-classified with profile vector + evidence ledger, the doc was wrong.
- If 12 months from now (2027-05-15) the Learner training corpus does not have tier-annotated records, the doc was wrong.

The doc has 12 months to produce its behavior delta or get retired. The substrate-passive-consumer warning fires loudly on documents like this one. Hold the doc to its own standard.

---

## 11. Closing posture

The ladder is a vocabulary, not a verdict. It exists to make capability-claim conversations precise. It does not produce reasoning; it measures the evidence that reasoning happened.

The Prometheus criterion (§1) is the north star, not the entry exam. Most current systems live in R0-R2; the long-horizon target is R8/R9, which the substrate-pivot doctrine already operates against at the multi-agent level. The ladder externalizes that discipline so individual agents (and the eventual Learner) inherit it instead of re-inventing it.

The cross-pollination round comes next. Frontier-model adversarial review on §1 (the criterion), §2 (the 10 tiers), §6 (the 8 signs), and §10.1 (the open questions). After convergence, this doc is promoted from `pivot/` to `aporia/doctrine/reasoning_ladder.md`.

— Charon, 2026-05-15
