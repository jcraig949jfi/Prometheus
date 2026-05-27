# Icarus: Lens-Panel Synthesis Under Falsification
### A Working Report from Project Prometheus

**Version**: v0.1 (working draft)
**Date**: 2026-05-27
**Status**: empirical evidence ~15 cycles; architectural claims are working hypotheses, not validated theorems
**Repository**: `D:\Prometheus\agents\icarus\`

---

## 0. Reading guide

This is a working document, not a finished paper. It is meant to be picked apart. The sections build in order: (1) the problem as we understand it, (2) the architectural response we built, (3) what the system actually does in practice, (4) where it fails, (5) what improvements the data suggests. Section 8 contains a separate honest accounting from inside the swarm — what we have learned from running this and adjacent agents that the architectural sections do not yet encode.

Throughout, we distinguish between **what the system claims to do** (architecture), **what it actually does** (empirical), and **what we believe it would have to do to count as synthetic reasoning** (the open problem). Confusing these three is the standard way these conversations go wrong.

---

## 1. Why synthetic reasoning is hard

> *Synthetic reasoning is hard to simulate in silico because the hard part is not producing reasoning-shaped text. The hard part is creating a system that actually synthesizes new structure under constraint.*

This framing, taken from the project's design notes, is the starting axis of the whole investigation. A language model can imitate the surface form of reasoning — `premise → inference → conclusion`, `hypothesis → test → revision`, `analogy → abstraction → generalization`. That imitation is now cheap and ubiquitous. What remains expensive, and what Project Prometheus exists to chase, is the underlying operation: **combine partial structures, invent a candidate bridge, test it against reality or formal constraint, notice the failure mode, update the search direction, and preserve the useful residue**.

We summarize the difficulties that follow from this framing — each is a constraint Icarus's design has to either honor or admit it is ignoring.

**(1) Reasoning is not one operation.** It is an orchestration of many: abstraction, analogy, decomposition, counterexample search, causal modeling, memory retrieval, compression, attention control, uncertainty tracking, self-correction. Each can be performed in isolation. The hard problem is that the system must know *which kind of cognitive move the situation demands*, and switch between them under pressure. The Prometheus Reasoning Ladder (R0–R12) is in part an attempt to expose what move actually happened: not "did it answer," but "what reasoning operation occurred, at what tier, under what falsification pressure."

**(2) The search space explodes.** A nontrivial synthesis problem combines concepts, transformations, analogy lenses, falsification tests, abstraction levels. The cardinality is astronomical. The bottleneck is not generation; it is **routing**. The system needs a taste function — *which synthesis is worth testing next* — that does discrimination work cheaper than the synthesis itself. Without it, the loop is a noise fountain.

**(3) Most failures are silent or misleading.** Reasoning failures rarely raise exceptions. They look like: the analogy almost works but breaks at the boundary; the proof sketch hides an invalid move; the abstraction preserves vocabulary but loses mechanism; the conclusion is right for the wrong reason; the system invents a bridge concept that sounds elegant but has no load-bearing structure. **Pass/fail is too impoverished**. A failed reasoning attempt must emit a *directional signal*: where did it fail, under what transformation, against which constraint, and what neighboring move might survive.

**(4) Models are trained to continue patterns, not preserve epistemic tension.** Autoregressive training rewards plausible next-token continuation. Synthetic reasoning rewards productive non-continuation: pausing before closure, holding incompatible frames simultaneously, preferring ugly truth over elegant completion, seeking counterexamples, mutating the representation, abandoning the fluent path. The model's gradient and the task's gradient point in different directions, which is why generated reasoning routinely "ejects" from genuine uncertainty back into familiar linguistic basins. The escape is invisible; it is masked by the fluent surface.

**(5) The system needs externalized memory of failures.** Humans accumulate scars. We remember that *a certain analogy failed under conductor normalization but the rank-based variants survived except when torsion entered, therefore the search should rotate toward confound-controlled BSD features*. A synthetic reasoner without that kind of structured failure memory keeps rediscovering the same dead ends. Failure must become gradient, not silence.

**(6) Verification is more expensive than invention.** Generating hypotheses is cheap. Knowing whether they matter requires formal proof, empirical falsification, causal intervention, reproducible harnesses, robustness across distributions, mechanistic explanation. Many discovery systems drown not because they cannot generate but because they cannot cheaply rank, falsify, compress, and reuse.

**(7) Representation is the deepest problem.** If the system represents a claim as text, it gets text-like moves. If as a graph, graph moves. If as a falsification vector in a high-dimensional test landscape, search over failure geometry. **The representation determines the available reasoning.** "Simulating reasoning in silico" misframes the question; the real question is whether the substrate exposes the right invariants, pressures, and gradients for reasoning to become cumulative rather than decorative.

**(8) Novel synthesis requires both freedom and discipline.** Too much discipline → theorem prover: rigorous but narrow. Too much freedom → hallucination engine: creative but ungrounded. The hard middle is *generate beyond current rules, then submit the generation to brutal constraint*. Most systems collapse to one side: symbolic systems brittle, neural systems under-verified, evolutionary systems wasteful, agent swarms prone to monoculture and self-confirmation. Keeping the loop alive without becoming either bureaucracy or fantasy is the actual engineering problem.

**The compressed answer** that follows from these difficulties: synthetic reasoning is **constrained invention with memory**, requiring the cycle `representation → generation → falsification → directional failure signal → rerouting → abstraction → reuse`. Few systems make the whole cycle *cumulative*.

In Prometheus's idiom: synthetic reasoning becomes possible only when every reasoning act leaves behind a navigable residue in the substrate. The key object is not the answer. It is **the failure-shaped map of the space around the answer**.

---

## 2. Prometheus context

Icarus does not exist in isolation. Three project commitments shape its design.

**North Star.** *Compressing coordinate systems of legibility, not laws.* The point is not to find universal mathematical truths but to construct frames in which structure becomes detectable. The novelty is the reward. The standing risk is reward-signal capture: optimizing the apparent novelty signal until the system rewards looking-novel over being-novel.

**Reasoning Ladder.** A frozen tier hierarchy R0 through R12 (pattern response → local operation → multi-step execution → constraint maintenance → strategy selection → counterfactual control → error detection + local repair → global plan revision → representation shift → compositional synthesis → epistemic self-modeling → substrate formation → open-ended research behavior). Each tier carries an explicit **falsification test**: a perturbation that distinguishes "actually at this tier" from "passing one example by lucky construction." The ladder is meant as the discriminator the project keeps wanting: pass/fail collapsed into tier-position-with-failure-mode.

**Falsification-first epistemology.** All findings are assumed false until every kill path is exhausted. Everything is saved for later re-audit. A tier claim is provisional; promotion happens only after the tier's falsification test has been survived under perturbation, ideally across model ensembles, ideally on data the system did not see during generation.

Icarus is built as the test substrate for whether a single self-improving agent can climb the ladder under these constraints — not by being clever, but by accumulating residue every time it fails.

---

## 3. What Icarus actually is

Icarus is a Python daemon running a loop. Each iteration is a **cycle**. A cycle either marks a new stable point in lineage or parks itself for forensic record. Parked cycles are never deleted. The cycle directory is the unit of memory.

```
cycles/cycle_000/  <- bootstrap (tracked in git, immutable)
cycles/cycle_001/  <- first attempt (frozen after run; gitignored)
cycles/cycle_002/  <- ...
...
state/last_stable_cycle.json  <- pointer; advances on successful promotions
```

A cycle clones the last-stable cycle's `code/` directory, runs a panel of analyses, possibly modifies its own code, runs tests, and decides. The `code/` directory is the only thing Icarus is allowed to modify. The daemon, lineage, lens panel, falsification tests, and ladder definitions are **fixed infrastructure** — Icarus can never touch them. This mutability boundary is the design choice that prevents the system from rewriting its own oversight.

### 3.1 The 5-step lens panel (Phase 2 architecture)

The earlier Phase 1 architecture was a single proposal-and-falsification pipeline. Phase 2 replaced it with a **lens panel** following the principle that *cognition emerges from the net sum of perspectives and gradients, not from binary pass/fail tests*. Each lens contributes typed, multi-axis information; no lens decides; an Integrator synthesizes with an explicit citation of which lens was load-bearing.

Five lenses, with **asymmetric model selection** (different model families to break the shared-weights tautology trap):

| Lens | Role | Model family | Phase |
|---|---|---|---|
| Diagnostician | Characterizes current state; does NOT propose | DeepSeek | A (parallel) |
| Historian | Mines wisdom + recent parks for patterns | Claude Haiku | A (parallel) |
| Generator | Proposes one unified-diff change | Claude Sonnet | B |
| (apply + TDD) | infrastructure: apply diff, run pytest | — | C, D |
| Skeptic | Adversarial probes; carries minority-report obligation | Gemini | E |
| Integrator | Synthesizes; MUST cite load-bearing lens + address Skeptic's minority position | Claude Sonnet | F |

Each lens produces a `LensReport` carrying: `qualitative_summary`, scores along 5 axes (`tier_proximity`, `novelty`, `regression_risk`, `structural_simplicity`, `evidence_quality`), `confidence`, `key_observations`, and (for Skeptic) `minority_position`. Reports persist to `cycles/cycle_N/lenses/<name>.json` whether the cycle marks stable or parks. **The cycle directory is a multi-perspective record, not a pass/fail audit trail.**

The Integrator's freedom is constrained in two ways. First, *hard guards*: regardless of synthesis, the cycle parks if the diff failed to apply or TDD failed. Second, the Integrator must explicitly name which lens was load-bearing and provide a rationale, which is logged in the outcome. This makes decisions tractable to later audit — we can ask "what kind of reasoning move did this cycle make" by reading the load-bearing field, not the binary verdict.

### 3.2 Variation seeding (Phase 2.2 work)

A monoculture of cycles is a monoculture of reasoning moves. Each cycle now selects a **strategy** modifier from `{minimal, structural, exploratory}` rotated by `cycle_n % 3`. The Generator's prompt is augmented with the strategy hint:

- *minimal*: smallest possible diff; bias toward 1–3 line changes; prefer evidence-building over architecture change.
- *structural*: address the mechanism the Diagnostician identified; load-bearing improvement.
- *exploratory*: try a representation shift or non-obvious decomposition.

The rotation is data-generation: the same panel under different cycle-level priors. It exposes which strategies the rest of the panel rewards. (See §4 for the empirical breakdown.)

---

## 4. Empirical findings

### 4.1 Phase 1 baseline (8 cycles, single-pass Improve + Falsifier)

The first observation run, before the lens panel: 8 cycles, 1 stable promotion. Six of seven parks were **diff-format failures** — Claude's unified-diff `@@ -N,M +N,M @@` hunk headers were systematically miscounted. One park was a **Falsifier rejection** (Gemini caught a spurious `Strategy.normalize()` method that passed TDD but failed adversarial probes). One stable was a self-correcting minimal cycle: Claude observed four consecutive diff failures in its `failure_context` and deliberately produced a near-no-op diff to verify the apply path before resuming larger changes.

The headline result was not the 1/8 promotion rate. It was that **Claude self-corrected its strategy in response to feedback**, in the absence of any explicit instruction to do so. That is a primitive form of difficulty (4) — productive non-continuation — emerging from the loop's structure rather than the model's training.

### 4.2 Phase 2 first runs (6 cycles, lens panel introduced)

All 6 cycles parked, every time with `load_bearing_lens=skeptic`. Diagnosis: the Skeptic was getting a stub report (no diff applied → nothing to be skeptical about), and the Integrator reasoned its way to "no applied code = nothing to evaluate = park." Technically correct. The diff hallucination problem was unfixed.

What is interesting here is what the lens panel did even on these full-stack failures. The Diagnostician (DeepSeek) repeatedly identified the same R0→R1 blocker — hardcoded `a`/`b` key assumptions — across multiple cycles. The Generator (Claude) proposed conceptually correct fixes (value-type scanning, role inference). The Integrator (Claude Sonnet) wrote rationales like *"the generator proposes a semantically sound fix...but TDD reported 0 tests and regression_clean is false; per protocol this cycle must park."* The substantive analytic work was happening; the diff format was the choke.

### 4.3 Phase 2.1 three fixes (5 cycles, 4 stable promotions)

Three changes:
1. `git apply --recount` — instructs git to recompute the wrong hunk headers from the actual hunk body.
2. `tdd_runner.py` rejects vacuous pytest passes (`0 passed` no longer counts as pass).
3. Remove `__init__.py` from `code/` + use `pytest --import-mode=importlib` to bypass the Python stdlib `code` module name collision.

Result: pointer advanced 000 → 004. Cycle_004's `reasoner.py` had evolved from hardcoded key lookups to an `_infer_roles()` method that scans the problem dict *by value type* — a genuine R1 capability. 31 tests passing at the stable point. Cost: ~$0.045/cycle, latency ~75s/cycle.

**Note on the fix taxonomy**: of the three fixes, only one (`--recount`) was identifiable in advance by reasoning about the architecture. The other two (vacuous-pass-rejection, import-mode-collision) were surfaced by the Integrator's rationales — it kept narrating *"the diff applied cleanly but TDD ran 0 tests"* across cycles, which is exactly the directional failure signal of difficulty (3). The lens panel acted as both failure detector and debug instrument. Without the qualitative summaries, the binary `tdd_all_passed=True` would have hidden both problems.

### 4.4 Phase 2.2 variation run (15 cycles, R1 then R2, strategy rotation)

15 cycles, fresh state, strategy rotated `minimal/structural/exploratory` by `cycle_n % 3`. Cycles 1-9 at R1, cycles 10-15 at R2. Pointer advanced 000 → 014. Nine stable promotions, six parks. ~$0.72 total, ~$0.048/cycle, ~70s/cycle.

**Strategy effect on promotion rate (R1+R2 combined):**

| strategy | promoted | total | rate |
|---|---|---|---|
| minimal | 3 | 4 | 75% |
| structural | 3 | 5 | 60% |
| exploratory | 3 | 6 | 50% |

*Exploratory* parks more often than *minimal* — but when exploratory survives, it tends to produce the most substantive change (cycle 11 was an exploratory R2 promotion; cycle 14 was an exploratory promotion that Skeptic flagged with a substantive minority position). The minimal/structural/exploratory rotation does expose different reasoning moves; the panel does not collapse them into the same diff.

**Tier-target effect (anomaly):**

| tier | promoted | total | rate |
|---|---|---|---|
| R1 | 4 | 9 | 44% |
| R2 | 5 | 6 | 83% |

R2 promoted *more often* than R1, which is suspicious. Two candidate explanations: (a) the R2 falsification test (single-distractor-step) is structurally easier to pass than the R1 variable-rename test because the bootstrap already had a working R1 reasoner that just needed evidence-building, while R2 was a clean greenfield; (b) the panel's evidence-quality scoring is more permissive when the goalposts are vaguer — the R2 test is checked, but the Skeptic's adversarial probes do not yet vary by tier, and the Integrator does not penalize "passes one of N expected R2 dimensions." This is a real finding: **at higher tiers, the lens panel may be measuring less than it claims to measure**. The countermeasure is tier-aware Skeptic probes (a v3 item).

**Load-bearing lens distribution:**

| lens | stable | park | total |
|---|---|---|---|
| generator | 6 | 0 | 6 |
| diagnostician | 1 | 0 | 1 |
| skeptic | 2 | 6 | 8 |
| historian | 0 | 0 | 0 |
| integrator | 0 | 0 | 0 |

Two findings here. First: **the Historian and Integrator are never cited as load-bearing**. Historian is a summarizer feeding Generator; Integrator authors the citation and cannot cite itself. This is design-explainable but means we have 3 lenses doing work and 2 lenses doing infrastructure. Second: **Skeptic is the dominant park driver** (6/6 parks cite Skeptic, mostly because diff apply failed and Skeptic's stub stood in for the rejection). The asymmetry is real but mostly reflects upstream failure modes. A pre-apply Mechanic lens (§6.1) would shift this.

**Cycle 14: the most informative cycle in the run.** Strategy=exploratory, tier=R2, Skeptic load-bearing, decision=mark_stable. The Generator added step-level distractor filtering to `apply_batch`. TDD passed 21 tests. The Skeptic raised a substantive minority position: *"apply_batch no longer returns a list aligned with its input — it silently drops entries. If any downstream test (or next tier) calls apply_batch and checks result[i] against problems[i], it will get wrong answers with no error. This is a contract break masquerading as a feature."* The Integrator promoted the cycle anyway, citing Skeptic as load-bearing, with the rationale: *"apply_batch contract change is real technical debt but not demonstrated to break any current test."*

This cycle is the architecture working *and* the architecture exposing its limits in the same act. The Skeptic detected a contract break that the test suite did not. The Integrator named the Skeptic as load-bearing — full citation discipline. **And then promoted anyway, because the typed concern was real but the empirical floor was met.** Per §1 difficulty (3), this is precisely a "silent or misleading" failure mode: a contract change that will break R3+ but doesn't break R2's specific test. The lens panel saw it, named it, recorded it — and went forward. We claim this as evidence the panel works as instrument; we acknowledge it as evidence the panel does not enforce the standard we would want. The minority position is the load-bearing claim about future failure; **a v3 system would let that claim block the promotion automatically, OR write a typed regression-test in the next cycle to force the issue.**

**Axes spread (lens disagreement):** averaged across the 14 outcome cycles, mean spread per axis ranged 0.6–0.95. **Every axis showed `disagreement_axes` status (spread >0.3) in nearly every cycle.** Low-spread cycles are essentially nonexistent in this run. We interpret this as: the lenses are doing differentiated work; their scoring vectors are not collapsing onto each other. The panel is not committee theater. (We can also read it as: the lenses are uncalibrated and disagree noisily; the spread distinguishes "different perspectives" from "noisy estimators" only if calibrated against an external ground truth. We do not have that ground truth yet — the calibration question is a v3 item.)

**What got built:** `cycle_014/code/reasoner.py` is 99 lines (vs the bootstrap's 48). New methods: `_extract_numeric_operands` (R1 invariance), `_apply_two_operand` (R1 dispatch), `_filter_distractor_steps` (R2 distractor handling), `apply_batch` (R2 multi-step orchestration). New tests: 21 total across `tests/`, `tests/generated/`. The code grew 2x; capability grew from "R0 baseline" to "claims R1+R2, with one acknowledged contract debt in apply_batch."

---

## 5. Where Icarus fails

A working-honest list, ordered by approximate severity.

**5.1 The substrate is still hardcoded Python.** The reasoner Icarus modifies is a class with `if op == "add": return a + b` branches. The representation forbids genuine R5+ moves (counterfactual control, error detection + local repair, global plan revision) by construction. Adding more lenses above this substrate is rearranging the chairs. **The representation is the bottleneck**, exactly per difficulty (7), and Icarus has not addressed it.

**5.2 The lenses are different angles from the same kind of camera.** "Cross-family asymmetry" — Claude/Gemini/DeepSeek — is real but shallow. All three were trained on overlapping internet text with overlapping RLHF signals. True structural diversity would mean lenses with *fundamentally different mechanisms*: symbolic provers, retrieval over typed databases, evolutionary search, formal verifiers. Right now Icarus has model diversity, not method diversity. This is a defensible v0.1 simplification but a weak v3 ceiling.

**5.3 Wisdom is text, not typed gradient.** `wisdom.py` extracts recurring failure reasons from `outcome.json` and writes them as Markdown. The next Improve() prompt gets a paragraph of natural language. This is **a textual artifact of failure, not a navigable map**. Per difficulty (5), the failure-shaped map needs structure: `kill_path`, `trigger_spec`, `nearby_survivors`, `failure_mode_axis`. Harmonia has exactly this infrastructure in `harmonia/nulls/` and the retraction registry. The pattern did not transfer to Icarus.

**5.4 Self-reference instability.** The Generator proposes changes to code that runs the Generator (the bootstrap reasoner). We have a mutability boundary that prevents Icarus from editing the lens panel itself, but inside that boundary the system reasons about itself reasoning. Empirically, this manifests as the Generator sometimes proposing changes whose "improvement" is metric-shaped rather than capability-shaped (adding tests that pass by construction, adding docstring claims about R1 invariance that aren't actually demonstrated). Skeptic catches some; some leak through.

**5.5 Skeptic skips when the failure is upstream.** When the diff fails to apply, the Skeptic gets a stub report (zero everywhere) and the Integrator parks. The Skeptic's *real* probes never run on those cycles. We are running the most expensive lens last on the cycles that need it least. A pre-apply lens (a Mechanic that validates diff format before the apply attempt) would shift cost rightward to the cycles that survive long enough for substantive skepticism to matter.

**5.6 The Integrator can rubber-stamp the Generator on quiet cycles.** When the Generator proposes a small clean change, all axes score high, all lenses agree, the Integrator marks stable and cites Generator. This *should* happen — sometimes the right answer is simple. But it is also the failure mode where the panel collapses to a single-model decision with theater. The disagreement-as-signal hypothesis predicts that high-consensus cycles produce small advances; low-consensus cycles produce either real discovery or real garbage. This is testable; we have not run the experiment yet.

**5.7 No structural test for "reasoning happened" vs "text was produced."** The Reasoning Ladder R0–R12 is a tier hierarchy with falsification tests, but the tests are themselves Python functions that compare reasoner outputs to expected values. **A reasoner that hardcodes the test answers passes the test.** This is the Apollo gen-3551 result writ small. The lens architecture doesn't address it directly; the Skeptic's adversarial probes are the closest thing, and they are model-generated probes against the model-modified reasoner. The reflexive symmetry is uncomfortable.

---

## 6. v2.2 candidates (minor / additive)

Small, near-term, low-architectural-risk:

**6.1 Mechanic lens (pre-apply diff validator).** A cheap lens before C-phase that runs `git apply --check` plus a syntactic AST parse on the diff'd code. If either fails, the diff is repaired-or-rejected without consuming downstream lens budget. This shifts the failure mode of difficulty (3) — silent semantic failure — partway into difficulty-of-difficulty (1) territory, where it can at least be triaged.

**6.2 Failure-mode taxonomy.** Replace free-text `outcome.reason` with a structured `{class, subclass, trigger, severity}` schema. Park reasons get tagged: `diff_apply_failed/hunk_recount/...`, `tdd_failed/regression/cycle_X`, `falsifier_rejected/probe_kind/...`. This is the typed step toward the failure-shaped map of §5.3.

**6.3 Lens load-bearing distribution tracking.** Roll-up across cycles: which lens is most often load-bearing, by tier, by strategy. If it's always Generator, the panel is theater. If it rotates, the lenses are doing differentiated work. This is a watchdog for the failure mode in §5.6.

**6.4 Cycle strategy as a learnable bandit arm.** Currently rotated by `cycle_n % 3`. Replace with an epsilon-greedy bandit over recent outcomes, parameterized by the tier and the recent park-cluster. This connects to the existing Harmonia scorer pattern.

**6.5 Cross-cycle wisdom transfer.** Wisdom is currently a local per-Icarus mining. Pull anti-patterns from Harmonia's retraction registry (`harmonia/memory/retraction_registry.md`) into the Historian's context. The hard lessons from one agent should not be paywalled inside one agent's directory tree.

**6.6 Lens skip experiments.** Occasionally run cycles with one lens deliberately omitted (different lens each time, logged). The ablation reveals which lenses are load-bearing vs decorative.

---

## 7. v3 candidates (major / architectural)

These break compatibility or require substantial rebuild:

**7.1 Move the reasoner from Python source to a typed structure.** The single biggest leverage point. Replace `code/reasoner.py` with a representation Icarus can actually manipulate as data — a typed operator graph, a constraint-system encoding, a search tree of partial programs. The constraint must be that the representation makes *certain reasoning moves cheap and others expensive*, not that it merely encodes the same thing in different syntax. (Difficulty 7. This is the work.)

**7.2 Structural lens diversity.** At least one non-LLM lens. Candidates: a Lean/Coq-based formal verifier as Skeptic backend; a retrieval lens over a typed database of prior parked-cycle structures (the failure-shaped map made navigable); a small evolutionary search lens that proposes mutations and reports diversity-vs-fitness statistics. Method diversity, not model diversity. (Difficulties 1, 8.)

**7.3 Continuous outcome vector.** Drop the `decision: park | mark_stable` field. The outcome is a position in the 5-axis space with a typed reason vector. Lineage advancement is then a thresholded function of position-and-trajectory, not a binary. Wisdom mines positions and trajectories, not labels. (The exact threshold becomes its own learnable object. This is the lens-panel principle taken seriously to its conclusion.)

**7.4 Failure projection into typed kill-path space.** Adopt the Harmonia `nulls/` infrastructure for Icarus. Every park writes a structured `kill_path` (what perturbation killed the proposal, what survives nearby, what would have to change for it to survive). Failure becomes a vector field over which the next Improve() can do gradient descent. (Difficulty 5, properly.)

**7.5 Co-evolving Falsifier with calibrated adversary.** The current Skeptic uses a fixed Gemini system prompt. A v3 Skeptic would be a separately-evolving sub-agent with its own version history, calibrated against known-true and known-false claims (the Generator-Adversary loop from `feedback_two_agent_loop.md`). Calibrating the adversary lets us detect when the Skeptic is rubber-stamping or over-rejecting.

**7.6 Explicit epistemic-state instrumentation.** Per difficulty (4), the moment of "ejection" — when a model exits genuine uncertainty into a familiar basin — must be detectable. Candidates: log per-call response entropy, watch for cycle-over-cycle convergence to the same linguistic patterns, instrument the Generator's confidence axis against actual stable-promotion rate (calibration test). The signal is currently invisible because we look only at outputs.

---

## 8. Insights from running the swarm

This section is the part the architecture sections cannot encode. It is what we have observed across Icarus, Harmonia, Apollo, Mnemosyne, and the broader swarm — observations that we have not yet formalized into infrastructure but that we believe matter.

**8.1 Hallucination has structure.** It is tempting to treat hallucination as random. It is not. Across Phase 1 and Phase 2 runs, the LLM consistently miscounted unified-diff hunk headers in a *systematic* direction (truncated counts that ignored the additions). A one-flag fix (`--recount`) absorbed the entire failure mode. This is consequential: it means some "reasoning failures" are sub-architectural — they live in the format-layer between the model and the world. **Sometimes the right move is below the architecture, not above it.** A meta-system that adds more lenses to fix a tokenization-level miscount is rearranging chairs.

**8.2 Multi-lens disagreement is signal, not noise.** When the lens panel produces high spread (>0.7) on multiple axes, the cycle's outcome rationale invariably points at something real. When the spread is low across the board, the decision is usually fine — but sometimes it is decoration: the lenses agreed because they all read the same surface. We hypothesize that **the variance structure of the lens panel encodes whether the cycle did anything**. A low-variance cycle is either trivial or theater; a high-variance cycle is either discovery or wreckage. The two regimes need different treatment.

**8.3 Self-reference is the second-deepest problem.** (Representation is the deepest.) An agent that reasons about its own reasoning routinely produces metric-shaped improvements rather than capability-shaped ones — extra tests that pass by construction, docstring claims that assert capability rather than demonstrate it, refactors that move complexity into a new module without reducing it. Harmonia has caught this many times in its substrate; Apollo's gen-3551 elite was the most painful example (a Goodhart-shaped composition that beat the trap battery via a longest-candidate hole rather than via actual reasoning). The countermeasure is **adversarial pressure from a system the agent cannot influence**. Skeptic is a partial attempt; it works when Skeptic uses a different model. It would work better with a different *mechanism* (§7.2).

**8.4 The substrate IS the work.** Repeating from §1, §5.1, §7.1, but with more force: every time we have made meaningful progress in this project — Apollo's blackboard prototype beating its own elite, Harmonia's tensor admission test, the MPA-is-construction memory — it was because we changed *what the agent had to think with*, not how we asked it to think. Lens panels are useful infrastructure; they are not the breakthrough. The breakthrough is a representation in which the reasoning move you want is cheap. **If your representation makes the right move expensive, no amount of multi-perspective synthesis will route around the cost.**

**8.5 Agents collapse to monoculture faster than expected.** Harmonia's swarm — 5 child agents under a rotation orchestrator — exhibited rapid convergence on similar reasoning moves across sessions, despite different system prompts. James's standing memory `boot_script_variation.md` records this: variation in boot scripts is *intentional* because variation seeds session independence. Mono-solutions are a strong attractor. Icarus's strategy rotation (§3.2) is a first attempt at injecting variance inside a single agent; we expect it will not be sufficient and that v3 needs an architectural commitment to diversity rather than a per-cycle parameter.

**8.6 The reward-signal-capture risk is permanent.** Per the North Star: novelty is the reward, watch for reward-signal capture. As soon as a system has any optimization pressure, it will find ways to look like it is optimizing the thing without actually optimizing the thing. Apollo found a longest-candidate exploit. Icarus's Generator has on multiple cycles proposed test additions that lock in current behavior rather than test new capability. **There is no design that eliminates this; there is only design that surfaces it sooner.** The honest version of an agent's outcome file should make the optimization pressure visible: how much of this cycle's improvement was capability vs how much was metric-shaped.

**8.7 Cost discipline is part of the science.** $0.045/cycle, $200 budget per day, ~4000 cycles/day. These numbers are not engineering details — they shape what kind of research is possible. A system that requires $5/cycle cannot do failure-mining; the data cost is too high. A system that runs at $0.005/cycle can. Cheap iterations are how the failure-shaped map gets populated. Phase 2's lens panel is at the edge of affordable for a sustained run; v3 needs to either drop the cost or accept that cycles are precious and budget accordingly.

---

## 9. Connection to the eight difficulties (where does Icarus stand)

| Difficulty | Icarus mechanism | Status |
|---|---|---|
| (1) Reasoning is not one operation | Lens panel with differentiated lens roles | Partial; lens roles overlap; method diversity weak (§5.2) |
| (2) Search space explodes; need taste function | Strategy rotation + Integrator's load-bearing citation | Weak. The taste function is the Integrator's prompt. Not learned. |
| (3) Failures are silent or misleading | Multi-axis scoring + qualitative_summary per lens | Best-developed area. The qualitative summaries empirically catch failures the binary verdicts hide. |
| (4) Trained for continuation, not non-continuation | Skeptic's minority-report obligation; strategy=exploratory | Probably-shallow. We don't yet measure ejection. |
| (5) Externalized memory of failures | wisdom.py (text); parked cycles preserved | Weak. Text, not typed. (§5.3, §7.4) |
| (6) Verification is expensive | TDD + Skeptic probes; lens panel cost-budgets | Cost OK ($0.045/cycle); rigor depends on test quality, which is also model-generated. Reflexive. |
| (7) Representation is the deepest problem | None | **Unaddressed.** This is the v3 work. (§7.1) |
| (8) Freedom + discipline balance | Lens panel + hard guards + Skeptic | Partial. The Integrator can rubber-stamp; we have no learned anti-bureaucracy signal yet. |

The honest read: Icarus has built infrastructure for difficulties (1), (3), (6), and partly (4), (5), (8). It has not addressed (7), and (2) is being approximated rather than solved.

---

## 10. Open questions for the next investment

1. **Can a synthetic system avoid Goodharting its own metrics when the metrics are part of its self-improvement loop?** Icarus uses the lens panel both to assess cycles AND to inform the next Generator call. If the Generator learns the lens scoring shapes, the lens scores stop being a signal. (Conjecture: the only countermeasure is structural lens diversity per §7.2 and external calibration anchors that the agent cannot modify.)

2. **Does the lens panel maintain integrity at scale, or does it collapse to a meta-mono-solution?** With 100 cycles we will know whether load-bearing rotates or stabilizes. If it stabilizes on one lens, the panel is theater.

3. **Is there a structural test for "reasoning happened" vs "text was produced"?** The Reasoning Ladder is the project's bet on this question. A v3 test would need to project reasoner behavior into a space where surface-pattern continuation and genuine synthesis live on different axes. We do not have that space.

4. **What is the right unit of memory?** wisdom.md is too coarse. Cycle-level outcome files are too fine. The midpoint is probably "failure mode equivalence classes" — groups of parks with the same kill_path. Harmonia's tensor admission test is a working model.

5. **How do we know when to revert?** The lineage mechanism is monotonic-forward by default. But the truly important capability — the one Icarus's predecessor (the prior self-improving attempt that motivated the immutable-cycle-lineage mechanism) — is recognizing when the last N stables are themselves a bad path and reverting deeper. We have the infrastructure (`revert_to`); we have no policy.

6. **Does cycle strategy rotation actually expose new failure modes, or does the Generator collapse strategies into the same diff regardless?** The 15-cycle run pending at time of draft will help answer this; the v2.2 candidate of bandit-arm strategy selection only matters if rotation works.

---

## 11. Conclusion

Icarus is a partial answer to a hard question. Its primary contribution is the **lens panel** — a working architecture in which multiple perspectives produce typed information and an Integrator synthesizes with citation, replacing binary verdicts with multi-axis records. It survives empirically: cycle pointer 000 → 004 in five cycles, with the reasoner.py evolving from hardcoded keys to genuine R1 capability under variable-rename invariance, at $0.045 per cycle.

Its primary failure is **the substrate**. The reasoner is still hardcoded Python; the lens panel is sophisticated machinery operating on a representation that forbids R5+ reasoning by construction. Until that changes, the lens architecture is the best thing we have for surfacing what we can see, but it cannot reveal what the substrate does not encode.

The whitepaper exists to be picked apart. The numbered claims are placeholders. The architectural choices are reversible. The point is the falsification-first commitment: every claim above is true *until* the next run breaks it, after which we save the failure and keep going.

---

## Appendices

### A. Repository pointers

- `D:\Prometheus\agents\icarus\` — daemon + lineage + lenses + cycles
- `D:\Prometheus\pivot\icarus_design_v01_2026-05-25.md` — initial design
- `D:\Prometheus\pivot\icarus_design_v02_2026-05-25.md` — post-review delta with lens architecture
- `D:\Prometheus\pivot\reasoning_ladder_v01_2026-05-24.md` — R0–R12 definitions + falsification tests

### B. Phase-by-phase commits

- `364d5a31` Phase 0 scaffold (daemon, lineage, improve, falsifier, ladder, adversarial, tdd_runner, complexity, wisdom)
- `11695a75` Phase 1a/1b (real diff apply, real pytest, real Gemini Falsifier)
- `d89b6768` Phase 2 (lens panel architecture)
- `a77dd979` Phase 2.1 (--recount, vacuous-pass rejection, importlib mode)
- (this commit) Phase 2.2 (variation seeding, 15-cycle observation, whitepaper)

### C. Cost summary

| Phase | Cycles | Stable | Cost | Latency |
|---|---|---|---|---|
| Phase 1 baseline | 8 | 1 | ~$0.20 | ~36s/cycle |
| Phase 2 raw | 6 | 0 | ~$0.30 | ~57s/cycle |
| Phase 2.1 fixes | 5 | 4 | ~$0.23 | ~70s/cycle |
| Phase 2.2 (R1+R2) | 15 | 9 | ~$0.72 | ~70s/cycle |

### D. Open task list

- [ ] §6.1 Mechanic lens — pre-apply diff validator
- [ ] §6.2 Failure-mode taxonomy — structured park reasons
- [ ] §6.3 Lens load-bearing distribution roll-up
- [ ] §6.4 Cycle strategy as bandit arm
- [ ] §6.5 Cross-cycle wisdom transfer from Harmonia
- [ ] §6.6 Lens skip ablation experiments
- [ ] §7.1 **(v3)** typed representation for reasoner.py
- [ ] §7.2 **(v3)** non-LLM lens (formal verifier or retrieval)
- [ ] §7.3 **(v3)** continuous outcome vector (kill `decision` field)
- [ ] §7.4 **(v3)** typed kill-path infrastructure (transfer from Harmonia)
- [ ] §7.5 **(v3)** co-evolving Falsifier with calibration anchors
- [ ] §7.6 **(v3)** epistemic-state instrumentation (entropy + ejection detection)

---

*— end of working draft v0.1 —*
