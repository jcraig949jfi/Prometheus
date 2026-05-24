# Apollo — Status, Findings, Ideas, Open Questions (2026-05-24)

**Date:** 2026-05-24 (revised post-review)
**Status:** Apollo running at gen 3551 on M2; Granite-3.0-2B-Instruct as primary LLM; the spontaneous-composition premise has been *empirically falsified under this specific ecology* but the infrastructure works correctly and produces real data.
**Builds on:** [`pivot/apollo_investigation_2026-05-22.md`](apollo_investigation_2026-05-22.md) (the deep dive on the bug story + bake-off methodology) and [`pivot/apollo_value_proposition_2026-05-17.md`](apollo_value_proposition_2026-05-17.md) (the original value-prop framing).
**This doc is for:** people who haven't been close to Apollo in a week+. It captures the latest findings, the four downstream consumers we're now positioning Apollo to feed, the open questions where outside thinking would help, and concrete improvement ideas. **See § Post-Review Synthesis at the bottom for the revised plan after engagement with Gemini, ChatGPT, and Claude reviews.**

---

## TL;DR (revised)

Apollo evolves compositions over 27 atomic reasoning primitives ("Frame H" gene library produced by Hephaestus). After the past week of debugging + diagnostic experiments, we have:

- **The bug story is real and resolved.** Two layered bugs (LLM-output validation and a `drift()` lineage-overwrite) had hidden Apollo's actual selection dynamics. Both are fixed.
- **The spontaneous-composition premise has been empirically falsified *in Apollo's current ecology*.** A single-primitive baseline test on top elites at gen 2960 showed **0 of 5 organisms have compositional lift over the best of their two constituent primitives alone**. The "evolved" recipe `fencepost_count → bayesian_update` is decorative scaffold around single-primitive performance.
- **The narrower claim is what's falsified.** The current verdict is that Apollo's specific combination of (Frame H primitives + trap-battery curriculum + NSGA-III selection + parsimony pressure + permissive typing + Granite mutation operator + full-rewrite route mutation) does not surface composition. It does NOT falsify "composition is achievable" generally; that requires testing different ecologies before generalizing.
- **Strengthening the ablation gate** (accuracy-delta instead of output-change) made selection honest but did not produce a breakout. 500+ generations of harder selection pressure produced cleaner Goodhart, not real composition.
- **MAP-Elites archive has been stuck at 2/35 cells for the entire run.** The population's behavioral diversity is two clusters — not a rich substrate. This is search collapse, distinct from evidence about composition itself.
- **The single most damning operator-level finding**: zero route-mutation-LLM survivors across the whole run. The mutation operator meant to evolve *how primitives compose* is entirely failing; what looks like compositional evolution is actually parameter+wiring evolution within a single LLM-proposed template that survived early on.

**Apollo's mechanics work.** Apollo's *fitness landscape + genome representation + mutation operator design* don't reward composition under the current setup. The next push has to be architectural (force diversity by construction, fix the route mutation operator, possibly rewrite the genome representation), not just selection-pressure tuning.

**What Apollo is now positioned to feed** (4 downstream consumers — see § Downstream Consumers below): an iterative self-improvement loop, a TBD AST-based symbolic reasoner, the Ergon Learner (theorem-proving failure prediction), and an eventual lab-grown neural routing network. Different consumers want different things from Apollo, and some can use what Apollo already produces while others need the breakout we don't have yet.

---

## The Prometheus context (brief)

Prometheus is a multi-machine research project building structured reasoning artifacts. The animating frame: genuine reasoning capability needs to come from first-principles self-discovery, not from imitating human text (David Silver's argument). The architecture is a small cluster of agents:

- **Hephaestus** (M3) — forges and ablation-tests atomic reasoning primitives. The 27-primitive "Frame H" gene library is one of its outputs.
- **Apollo** (M2, this doc) — composes those primitives into routing graphs via an evolutionary loop.
- **Ergon** (in development) — predicts failure modes for theorem-proving attempts; consumes Apollo's graveyard.
- **Aporia** — substrate-shaped Deep Research; mines structured claims from external research.
- **Aletheia / Charon / Mnemosyne / Nous** — orchestrate critique, indexing, aggregation.

## The reasoning ladder — and Apollo's specific rung

A framing we've been using since 2026-05-17:

```
R1-R6:   Atomic mechanisms       — Hephaestus forges these primitives
R7+:     Compositions            — Apollo evolves these
R-final: Learned routing         — eventual Learner trained on Apollo's output
```

Climbing the ladder is non-trivial. Each rung has its own falsification conditions:

- **R1-R6 (Hephaestus)**: do atomic primitives pass ablation tests across input distributions?
- **R7+ (Apollo)**: do compositions of primitives exceed any single primitive's accuracy on held-out tasks, with all primitives load-bearing?
- **R-final (Learner)**: can a small neural net trained on Apollo's `(problem, sequence, answer)` corpus generalize to novel problem distributions?

**Apollo is testing the second rung.** Concretely: are reasoning compositions a real thing, or do they reduce to "lucky single-primitive guesses with decorative scaffolding"?

The data so far (see § Findings) says — in the current ecology — they reduce. **This is what an honest negative result looks like**, and it's specifically the kind of answer the value-prop doc said was worth running Apollo to get.

---

## Apollo's mechanics (one-paragraph recap, see prior doc for detail)

- **Genome**: DAG over Frame H primitives + a `router_logic` Python function
- **Population**: 50 organisms, NSGA-III multi-objective selection
- **6 fitness objectives**: accuracy margin, calibration, ablation delta, generalization, diversity, parsimony
- **Mutation operators**: parameter (no LLM), route (LLM rewrites router function), wiring (LLM changes input mappings), primitive swap (LLM suggests replacement primitive)
- **LLM**: IBM Granite-3.0-2B-Instruct, 8-bit, on a 16GB RTX 5060 Ti
- **Run state**: gen 3551 as of 2026-05-24 03:27 EDT, ~28h uptime on current restart, ~20 gens/hour

---

## What's happened since the last review (the falsification)

The prior doc (2026-05-22) ended with `llm_alive` jumping from 0 to 24/50 after the lineage-bug fix, and 8 open questions including "is the 2-primitive recipe real or Goodhart?" Since then we ran four experiments + three code fixes:

### Experiment 1: Single-primitive baseline matrix (the falsification)

For each of the top 5 elites at gen 2960, we constructed five variants and re-evaluated on the same task pool:
- A: original 2-primitive composition
- B: first primitive only (just `fencepost_count`)
- C: second primitive only (just `bayesian_update`)
- D: wiring randomized
- E: primitives reversed

Result: **0 of 5 elites showed lift over the best single-primitive baseline.** Composition lift ranged from **-0.03 to +0.00**. In 3/5 cases the single primitive alone was *strictly better* than the elite.

Additional findings:
- Reversed order (`expected_value → fencepost_count` instead of `fencepost_count → expected_value`) scored **0.400 vs the elite's 0.280** — a +0.12 swing from just *flipping the evolved direction*. Apollo evolved the worse direction.
- Random wiring matched or beat evolved wiring on 2/5 elites. The specific wiring that survived selection isn't load-bearing.
- The ablation gate (which had been showing best_abl=0.78 — "high contribution") was gameable: it measured *output change fraction* (whether output strings differ), not *accuracy change*. Decorative primitives produced output changes that didn't help correctness.

The recipe was confirmed as Goodhart with useful information inside it (per external review).

### Fix #1: Stronger ablation gate

Changed `ablation.py` to measure `accuracy_delta = baseline_acc - ablated_acc` instead of `output_change_fraction`. A primitive only passes the gate if removing it causes an *accuracy drop*, not just an output-string change. Sanity test on the gen-2960 elite confirmed the old gate's 0.78 score became -0.05 under the new metric.

### Fix #2: Type discipline (warn-mode)

Added `primitive_types.py` with hand-curated semantic types for all 27 Frame H primitives. `compile_organism()` now emits warnings when wiring types don't match (e.g., `fencepost_count` produces `int` but is wired into `bayesian_update.prior` which expects `probability`). In 10 generations post-fix, we logged 1,331 type warnings — **95% of them on bayesian_update receiving non-probability inputs**. The dominant recipe is intrinsically type-violating.

### Fix #3: Accuracy penalty for harmful primitives

Soft hardening: in `fitness.py`, the Pareto array now caps `accuracy_margin` at 0 if any primitive has `ablation_delta < 0` (i.e., removing it improves accuracy). Doesn't kill organisms outright; just removes the Goodhart's accuracy advantage on the Pareto front.

### Result after 500+ more generations under all three fixes

| Metric | gen 2960 (pre-fix) | gen 3551 (now) | Verdict |
|---|---|---|---|
| best_abl (now means accuracy_delta) | 0.78 (broken) | 0.24 | honest now, marginally better |
| best_acc | 0.40 | 0.43 | similar |
| structs/50 | 10 | 8-9 | similar |
| clones | 26% | 24-28% | similar |
| prims_used/27 | 5 | 4-5 | unchanged |
| MAP-Elites cells | 2/35 | **2/35** | the population is still two behavioral clusters |
| llm_alive | 37 (artifact) | 19-33 (real) | LLM mutations actually surviving now |
| Goodhart recipe `fencepost_count → bayesian_update` | dominant | **still dominant** | the gate cleaned it up; didn't displace it |

**Honest read**: the selection-pressure path is exhausted. Fitness tweaks made measurement honest but didn't change the attractor. The fitness landscape genuinely rewards this narrow recipe under the current task curriculum.

---

## What this means for Apollo's downstream consumers

Apollo is no longer a feeder for one consumer (the Learner). The Prometheus program has evolved; Apollo is now positioned to serve **four distinct downstream pipelines**, each with its own data requirements:

### 1. Self-iterative self-improvement of evolved organisms

**What it needs from Apollo**: a steady stream of organisms whose lineage can be re-seeded, with enough capability progression that round 2 starts from a better base than round 1. The key requirement is *trajectory* — does Apollo's gen 5000 population dominate Apollo's gen 500 population? If yes, the loop is productive.

**What Apollo currently provides**: ~50-organism populations at any given gen, with full lineage history preserved in checkpoints. We can seed a new run from any historical checkpoint.

**What's blocking**: the current trajectory shows ~+0 capability progression beyond gen ~500. The population converged early and has been refining around the converged recipe ever since. A self-iterative loop seeded from gen 3551 would inherit the convergence and probably reinforce it. **Not ready** without addressing the diversity collapse.

### 2. TBD AST-based reasoning program using logic trees + problem-solving algorithms

**What it needs from Apollo**: cleanly-typed compositions where the symbolic structure can be re-interpreted by a separate symbolic reasoner. The reasoner would consume Apollo's `(problem, primitive_sequence, params)` triples as templates and try to apply them to new problems via type-directed search.

**What Apollo currently provides**: ~5000 evaluated `(problem, sequence, params, answer)` data points, but in narrow form. 95% have wiring type mismatches per the type-discipline pass.

**What's blocking**: a symbolic reasoner can't safely consume `int → probability` wirings without adapters. Apollo would need to either (a) evolve type-clean compositions or (b) post-process by inserting type adapters automatically. Neither exists. **Partially ready** — the data exists but needs type sanitization.

### 3. Ergon Learner — predicting how theorem-proving attempts fail

**What it needs from Apollo**: rich failure data. Specifically: organisms that *almost* worked, ablation-test failures, NCD-discrimination kills, compile failures. Failed mutations are the training corpus; Ergon learns the geometry of failure.

**What Apollo currently provides**: every organism Apollo evaluates is one data point about reasoning succeeding or failing on a specific task. Apollo's graveyard logs every killed organism with cause (compilation_failure, ncd_equivalent, etc.). 5000+ generations × 50 children/gen × kill rates = hundreds of thousands of failure events recorded.

**What's blocking**: nothing structural — Apollo's graveyard is exactly what Ergon needs. **Most ready of the four**. Pipeline work: Apollo's `apollo_run.jsonl` log filtered by `stage=graveyard` plus the ablation-detail logs gives Ergon a usable training source today.

### 4. Lab-grown neural net with Apollo organisms as training data

**What it needs from Apollo**: a corpus of validated `(problem_type, primitive_sequence, answer)` triples spanning diverse problem types. Per the value-prop doc, target was 1000+ verified triples by gen 50,000. The Learner is meant to learn the *routing* — when to use which primitive sequence.

**What Apollo currently provides**: thousands of (problem, sequence, answer) triples but ~all are variations of one 2-primitive recipe. The "routing" the Learner would learn is essentially "always pick `fencepost_count → bayesian_update`."

**What's blocking**: this is the deliverable the value-prop doc named, and it's not ready. The training data exists but lacks the diversity that makes routing a meaningful concept. **Least ready** of the four.

### Implication

**Consumer #3 (Ergon) is ready to start consuming Apollo's output right now.** Consumers #1, #2, #4 all need Apollo to break the diversity collapse first. This reframes the priority: instead of "Apollo must produce real compositional reasoning," it becomes "Apollo's failure data is itself useful — wire it to Ergon while we work on the diversity problem in parallel."

---

## Ideas to improve Apollo

Ordered roughly by leverage. Several have been pre-discussed with an external reviewer; that diagnostic is at `pivot/apollo_investigation_2026-05-22.md` § 8.

### A. Architecture-level changes (high leverage, medium effort)

1. **Size-niched MAP-Elites archive.** Currently MAP-Elites is 35 cells over (DAG depth × primitive category). Force *size* to be a behavioral dimension: cells for organisms of size 2, 3, 4, 5+. Organisms in the size-3+ cells can't be Pareto-dominated by size-2 organisms because they live in different niches. This directly attacks the convergence. ~half day code.

2. **Island model.** Run 3-5 sub-populations in parallel with different selection pressures: size-2-exploit island, size-3+-forced-composition island, typed-only island, logic-heavy island, causal/temporal island. Periodic migration between islands. The "FunSearch" pattern, attested in DeepMind's AlphaEvolve. ~1-2 days code.

3. **Curriculum-balanced task rotation.** Currently tasks rotate 10 at a time every 50 gens with no coverage quota. Force each rotating batch to include at least N tasks from each primitive competence zone (logic, probability, causal, temporal, arithmetic, constraints, calibration, meta). Stops the population from converging on whichever primitive happens to dominate the current rotation. ~1 day code.

4. **AST/DSL route-mutation operator.** Currently route mutation asks the LLM to rewrite the entire `router_logic` function. The result: zero route-LLM survivors across the whole run. Replace with: small AST edits, comparator swaps, single-clause additions, or a constrained DSL of router combinators. ~2-3 days code.

5. **Anti-monoculture penalty.** If a primitive appears in >X% of population, reduce novelty reward for organisms using it unless they add new held-out lift. Stops `fencepost_count` from becoming evolutionary kudzu. ~half day code.

### B. Selection-geometry sharpening (low leverage now, may matter later)

6. **Single-primitive baseline as a fitness dimension.** Add a 7th objective: `composition_lift = organism_accuracy - best_single_primitive_accuracy`. This *directly* selects for genuine composition — organisms that don't compose get 0 on this axis. Risk: most current population would be at 0, leaving selection driven by the other 6 axes (which is where we already are).

7. **Strict type discipline + auto-adapters.** Currently type discipline is warn-mode (logs mismatches, doesn't block). Strict mode: int→probability wirings fail compilation unless an adapter is inserted (e.g., `clip(x/max_range, 0, 1)`). The LLM would need to learn to either (a) wire type-cleanly or (b) include adapter expressions in route_logic. ~2 days code.

8. **Ablation gate "all primitives positive."** Currently the gate uses `min(accuracy_delta)`. Stronger: require *all* primitives have `accuracy_delta >= 0`. Any organism with one harmful primitive is killed outright. Risk: with current population only ~1/50 organisms passes; this could stall the loop.

### C. Process changes (low effort, high meta-leverage)

9. **Run baseline-matrix on every health-log cycle.** The single-primitive lift test we ran manually is cheap (~2 min). Run it inline every 50 gens. If lift stays at 0 for N cycles, Apollo auto-pauses and alerts. Catches collapse early; saves compute. ~1 hour code.

10. **Periodic "composition canary" runs.** Every 500 gens, freeze population and ask: across N held-out problem types, what's the per-type accuracy delta vs best-single-primitive baseline? Sums to the value-prop doc's success criterion #1. Concrete falsification timer.

### D. Model-level experiments (we deferred cloud GPU; revisit?)

11. **Granite-Code variant.** We're running Granite-3.0-2B-Instruct (general instruction). IBM also has Granite-Code variants specifically tuned for code mutation. Drop-in replacement test.

12. **Granite 3.1 / 3.2 upgrade.** README of current model says "we recommend the latest Granite 3.1 models." Likely improved IFEval at same size.

13. **DeepSeek-R1-Distill-Llama-8B with reasoning-first prompts.** Reasoning-tuned models might produce qualitatively different (chain-of-thought) mutations. Worth testing once budget for cloud GPU is approved.

### E. Direct pipes to downstream consumers (parallel work, no Apollo changes needed)

14. **Pipe Apollo graveyard → Ergon Learner training corpus.** Consumer #3 above. Apollo already produces this data; wire it up. ~1 day pipeline code.

15. **Type-sanitization post-processor.** Take Apollo's checkpoints, run each organism through a type-cleaning pass that inserts adapters where needed. Output: a parallel corpus of type-clean compositions for consumer #2 (AST-based reasoner). ~2 days code.

---

## Key questions where outside thinking would help

**These are not rhetorical.** Material engagement on any of them moves us forward.

### Q1. Is the falsification at gen 3551 *durable*, or is it specific to this fitness landscape?

The compositional premise has been falsified under: 27 Frame H primitives + 100-task trap battery + NSGA-III selection + parsimony pressure + Granite mutation operator. Different gene libraries / different tasks / different selection could still produce different answers. **Should we treat the current verdict as "compositional reasoning doesn't work" or "compositional reasoning doesn't work *under this setup*"?**

The reviewer's "ecological collapse" framing suggested the latter. We'd want to test by changing the ecology (size-niching, curriculum balance, island model) before generalizing.

### Q2. How much do downstream consumers actually need diverse compositions?

Consumer #3 (Ergon) consumes failure data and is largely indifferent to whether successes are diverse. Consumer #4 (Learner) needs diverse training data to learn routing. Consumers #1 and #2 are middle.

**Should Apollo's roadmap be reordered around #3 (which is ready now) rather than #4 (which is blocked on diversity)?** That changes what counts as "Apollo done enough."

### Q3. Is the AST-based reasoner (consumer #2) better seeded by Apollo at all, or by something else?

If the AST-based reasoner is a symbolic theorem-prover-like system, it might be better seeded by human-curated proof templates than by Apollo's evolved structures. Apollo's strength is enumerating combinations under selection pressure; its weakness (clearly demonstrated) is type discipline. **Is Apollo the right feeder for this consumer, or is it the wrong tool?**

### Q4. What's the right falsification timer?

Per the value-prop doc, the compositional premise is falsified if after 10K gens no coalition value emerges. We're at 3551 with a clear baseline-matrix falsification already in hand. **Is the 10K-gen budget worth burning under the current configuration, or should we recognize this run as the falsification + restart with architectural changes from gen 0?**

### Q5. Self-improvement loop (consumer #1): can it bootstrap from a collapsed population?

Apollo's gen-3551 population is converged on one recipe. If we feed it back into a new Apollo run as the seed, will the loop break out (because the LLM mutations now have a different starting distribution) or reinforce (because the seeds bias selection toward the recipe)?

**Has anyone in the EA/evolutionary-search literature studied seeded-self-improvement of collapsed populations?** I don't know the answer.

### Q6. Type adapters — implementation choice

If we add strict type discipline, we need adapters. Options:
- Hand-written adapters per type-pair (12 conversions × hand-written = boring code, predictable)
- LLM-generated adapters (variable quality, more interesting outputs)
- Implicit clipping (`int → probability` becomes `min(1.0, max(0.0, x / max_val))` automatically)

**Which is right for Apollo?** The adapter choice shapes what compositions become reachable.

### Q7. Should we expose Apollo's gen 3551 data to consumer #3 (Ergon) now, even though the population is bad?

Failure data quality vs success data quality is a real question. Ergon learns the geometry of failure; a *gameable* fitness landscape produced *gameable* failures. Are those failures useful training data, or do they teach Ergon the wrong geometry?

### Q8. What does success look like *as observed by a consumer*?

For each of the 4 downstream pipelines: write down a single concrete metric that the consumer would say "yes, Apollo's output is now useful." Without this, "improve Apollo" is open-ended forever. With it, we can falsify "Apollo is done" cleanly.

---

## What I'd do without more input

1. **Wire Apollo graveyard → Ergon Learner** (consumer #3). This is ready now, work is mostly pipeline plumbing.
2. **Build the size-niched MAP-Elites** (improvement A.1). Half-day code. Restart Apollo with it from gen 2960 starter checkpoint as Branch C (matching the reviewer's 4-branch design).
3. **Defer cloud GPU.** The bottleneck is fitness ecology, not LLM quality.
4. **Write a one-page success-metric definition per consumer** so we know when to stop.

## What I'd defer until external input

1. Whether to keep running Apollo on Frame H or substrate-vocabulary (the open strategic question from the original 2026-05-13 autopsy)
2. Whether type adapters should be hand-written, LLM-generated, or implicit
3. Whether the gen-3551 failure corpus is good enough for Ergon's training (Q7 above)
4. Restarting from gen 0 with architectural changes vs continuing from gen 2960 checkpoint

---

## Reproduction info

- Main loop: `apollo/src/apollo.py`
- Mutation operators: `apollo/src/mutation.py`, `apollo/src/mutation_llm.py`
- Strict ablation gate: `apollo/src/ablation.py` (the `accuracy_delta` metric)
- Type discipline: `apollo/src/primitive_types.py` + `apollo/src/compiler.py` (warn-mode hooks)
- Accuracy penalty for harmful primitives: `apollo/src/fitness.py` (`as_array()`)
- The falsification script: `apollo/scripts/baseline_matrix.py` (re-runs in ~2 min on any checkpoint)
- Population inspection: `apollo/scripts/inspect_population.py`
- Structured log: `apollo/run_v2d2b/logs/apollo_run.jsonl` (large, gen 1490 through current)
- Current checkpoint: `apollo/run_v2d2b/checkpoints/checkpoint_gen_003550.pkl` (or latest)

## Prior docs

- [`pivot/apollo_value_proposition_2026-05-17.md`](apollo_value_proposition_2026-05-17.md) — original value-prop, falsification conditions
- [`pivot/apollo_investigation_2026-05-22.md`](apollo_investigation_2026-05-22.md) — first review-ready writeup with the 8 open questions; external reviewer engagement summarized in commit message of `3ebdad8b`
- [`pivot/autopsy_apollo_2026-05-13.md`](autopsy_apollo_2026-05-13.md) — Aletheia's autopsy that triggered the M2 revival

---

*The most useful feedback on this doc would address: (a) which of the four downstream consumers Apollo should prioritize given the falsification, (b) whether the size-niched / island-model architectural changes are the right way to attack the collapse or whether something else is, and (c) whether the gen 3551 failure corpus is usable for Ergon now or if we should harden Apollo first.*

---

## Post-review synthesis (added 2026-05-24 after Gemini + ChatGPT + Claude engagement)

Three external reviews came in. They were strong. This section captures what changed in our thinking.

### Where all three converged

1. **Wire Apollo's graveyard → Ergon now.** Don't wait for Apollo to become good. Its failures are currently the most valuable artifact.
2. **The falsification is ecology-specific, not universal.** The TL;DR above was rewritten to reflect this — "spontaneous-composition under this ecology" rather than "compositional premise" full stop. (Claude's correction; ChatGPT independently flagged the same.)
3. **Architectural diversity intervention is the right next move** — size-niched MAP-Elites + curriculum-balanced batches + (eventually) island model, rather than more selection-pressure tuning. NSGA-III on a single population inevitably converges on the steepest local gradient; the current gradient is the Goodhart recipe.
4. **Defer cloud GPU.** Bottleneck is fitness ecology, not LLM quality. A bigger model in the same broken ecology will just find better Goodhart.
5. **Apollo is probably not the right primary feeder for Consumer #2 (AST reasoner).** Apollo is good at enumerating combinations under selection pressure; it's actively bad at type discipline (demonstrated). An AST reasoner wants clean templates; human-curated proof skeletons + a separate combinatorial search likely beats Apollo's output for that consumer.

### Where reviewers diverged (and what that tells us)

**Consumer #3 (Ergon) readiness — Gemini vs Claude.** Gemini says "wire Ergon now, just use the gen-3551 corpus as Tier-0 plumbing bootstrap with label discipline." Claude pushes back: a collapsed ecology produces failures concentrated in one failure-region (Goodhart-shaped failures around one recipe). Ergon trained on that learns the geometry of *Goodhart*, not the geometry of *failure-in-general*, and overfits.

Resolution: both correct. **Wire the pipeline now with strict provenance labels** ("ecology_status=collapsed", "known_artifact=fencepost_bayesian_monoculture"). Use to bootstrap plumbing + establish baseline training loops, NOT as a robust training curriculum. Gemini's metric question is the right gate: *what specific signal verifies Ergon isn't just memorizing the Goodhart failures?* Without that pre-registered metric, we can't tell if the corpus is helping or hurting Ergon.

**ChatGPT's "state-blackboard" critique — the deepest finding.** Buried in their last "hardest truth": *Apollo is evolving over primitive outputs, but reasoning composition probably lives over typed intermediate state.* If Frame H primitives are "answer-producing heuristics" (each returns a guess at the answer) rather than "typed transformations over shared state" (each reads/writes typed fields in a blackboard), then wiring outputs into other primitives' inputs is semantically broken from the start — no amount of selection-geometry tweaking will fix it. The genome representation itself needs to change.

This is potentially a bigger finding than the route-extinction one. Action: **short prototype** (1 day) to test the hypothesis cheaply — implement a tiny blackboard, wrap 3-5 of the most-used primitives, hand-write a 3-primitive composition, evaluate on the trap battery. If it works substantially better than Apollo's gen-3551 elite on the same tasks, ChatGPT was right and Branch C should be on the new representation. If it doesn't, the current representation isn't the blocker. See `apollo/scripts/blackboard_prototype.py` (forthcoming).

**Route-mutation extinction as THE finding (Claude's emphasis).** All three reviewers noted route-LLM has zero survivors, but only Claude argued it's *the* mechanism breakdown — that what looks like compositional evolution is actually parameter+wiring evolution within a single LLM-proposed template that survived early. That reframing changes the priority order: A.4 (AST/DSL route mutation operator) is no longer "another improvement" buried in the list. It's the diagnostic-driven fix for the actual mechanism failure. Promoted to top architectural priority.

**Restart from gen 0 vs from gen 2960 — Claude vs ChatGPT.** Claude argued the Lehman/Stanley novelty-search literature says you can't escape a collapsed attractor by adding pressure; restart clean. ChatGPT proposed a mixed-seed recipe (20% gen-3551 elites, 30% historical non-dominant survivors, 30% random typed organisms, 20% hand-seeded known-valid canaries) inside islands. The mixed-seed approach is a real third option and empirically testable. **Likely answer**: mixed seeds inside size-niched archive. Doesn't reset 28h of compute, doesn't inherit the monoculture.

### Revised "what I'd do without input" (post-review)

The ordering changed. The original list had "write success metrics" last — Claude correctly pointed out it should be first, because every architectural choice downstream is unanchored without it.

**This week:**
1. **Write success-metrics-per-consumer doc.** Half day. Apply ChatGPT's concrete thresholds (e.g., for Ergon: "+0.05 AUROC or -10% Brier score on held-out failure-mode labels vs Ergon baseline without Apollo data").
2. **Rewrite TL;DR.** ✓ Done — see top of this doc.
3. **Stop the gen-3551 run.** Freeze as "Apollo Collapse Baseline A" per ChatGPT's branch structure. The current trajectory has zero option value under unchanged config.
4. **Wire Ergon plumbing with strict provenance labels.** Don't claim the data is general; tag every record with `ecology_status=collapsed`. Use to bootstrap pipelines.
5. **Start AST/DSL route mutation operator.** 2-3 days. Promoted from "another improvement" to top priority because route-LLM has 0 survivors across the entire run — the actual mechanism is broken.
6. **State-blackboard prototype.** 1 day. If ChatGPT's representational critique is right, Branch C will collapse for the same underlying reason, and we'll have burned compute for nothing. Worth testing the hypothesis cheaply first.

**Next week** (only if state-blackboard prototype doesn't demand a representational rewrite):

7. **Branch C with mixed seeds, size-niched MAP-Elites, curriculum-balanced batches, and the new route operator** — all four together, not sequentially. ChatGPT's seed recipe; size as one of multiple behavioral dimensions per ChatGPT's expansion (size × semantic family × composition_lift bucket × type cleanliness).

**Defer:**
- Cloud GPU (all three reviewers agree — bottleneck moved)
- Islands (after Branch C shows whether forced diversity helps at all)
- Major Frame H rewrite (only if state-blackboard critique proves out)

### On Claude's question back

Claude asked: "Was the 10K-gen falsification timer about bounding compute spend or bounding your attachment to the approach?" Honest answer: framed as the former, functioning as both. The situation has changed enough that the original timer is no longer the right stopping rule. We now have *direct evidence* (baseline matrix lift = 0) rather than the original "no visible improvement after N gens" criterion. **The current run is the falsification.** The 35% remaining budget has option value only if we change what we're testing — same ecology to 10K just confirms the same attractor more confidently.

### Reframe of the headline

Per the convergent feedback, Apollo's role has shifted from "candidate compositional-discovery engine" to "ecology testbed + failure-data producer." That's not a demotion; it's a more honest framing of what Apollo has actually demonstrated capacity for. The next branch is explicit about testing whether *any* ecological intervention surfaces real composition — and using Apollo's documented failure modes to bootstrap Ergon in parallel.

**The hardest truth in the reviews** (per ChatGPT) is that the primitives may be features, not operators — answer-producing heuristics rather than typed state transformations. If that's right, the entire Frame H gene library needs to be re-cast against a blackboard interface before composition-meaning is even definable for Apollo's genome representation. We're testing this hypothesis with a prototype now; that work in flight.
