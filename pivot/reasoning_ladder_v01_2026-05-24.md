# Prometheus Reasoning Ladder v0.1 — Falsification-First Taxonomy

**Date:** 2026-05-24
**Status:** v0.1, internal review draft. Builds on the existing R1-R6 / R7+ / R-final cadence we've been using since 2026-05-17, and absorbs the genuinely-new tier dimensions surfaced in the 2026-05-24 external review.
**Audience:** Anyone working on Hephaestus / Apollo / Ergon / Aporia / future Learner. The ladder is meant to be a shared reference for what we mean when we say a system "reasons" — and specifically, what we mean by "tier N reasoning."
**Why now:** Apollo's gen-3551 falsification produced something useful: a worked example of an evolutionary search apparently reaching a high reasoning tier (compositional!) that turned out, under perturbation tests, to be a lower tier (heuristic + scaffold). That experience makes clear that a ladder is not a labeling scheme — it's a test discipline.

---

## The core doctrine

**A system does not occupy a reasoning tier because its output resembles that tier. It occupies the tier only if the relevant mechanism survives perturbation, beats lower-tier baselines, and fails in the tier-predicted way.**

This is the falsification-first principle applied to reasoning evaluation. Three operational consequences:

1. **Every tier claim requires a falsification test.** "This system reasons compositionally" is meaningless without a test that would break the claim. Apollo's baseline matrix is one such test — random wiring matched the elite, so the elite is not compositional.
2. **Tiers are predictions about failure modes, not just success modes.** A tier-N system should fail in tier-N-shaped ways, not just succeed at tier-N-shaped tasks. Bloom's taxonomy classifies successful behaviors; we classify the kind of failure the system can recover from.
3. **Tier assignments are observation-conditional.** "Tier R5 on substrate X" is meaningful; "Tier R5" alone is not. A system's reasoning level is a function of (gene library × task curriculum × selection geometry × evaluator), and changing any of those changes the reading.

## Why a ladder at all

Reasoning is a bundle (deduction, induction, abduction, analogy, planning, etc.) — but the project still needs to answer concrete questions like:
- "Has Apollo reached compositional reasoning yet?"
- "What's the next reasoning capability Ergon should target?"
- "What does Learner training data need to capture?"

These questions are unanswerable without a shared frame for "reasoning capability at level N." Prior taxonomies exist — Bloom's, modern LLM benchmark surveys, RE-IMAGINE's ladder — but none combine **mechanistic specificity + falsification tests + multi-dimensional structure** the way this project needs.

This is v0.1. It will be wrong in places. Revising as we learn.

---

## The ladder

The ladder has **a primary tier sequence (R0-R12)** that captures the spine of "what kind of reasoning is happening." Each tier carries a **falsification test** — the specific perturbation or comparison that decides whether the system actually occupies it. The ladder also identifies **three orthogonal dimensions** (failure repair depth, representation mobility, epistemic humility) that cut across the primary tiers; these are tier-modifying axes, not replacement tiers.

### Primary tier sequence

```
R0  — Pattern response                — surface form; fails first paraphrase
R1  — Local operation                  — applies one known operation correctly
R2  — Multi-step execution             — chains operations when order is supplied
R3  — Constraint maintenance           — tracks multiple constraints; rejects inconsistent candidates
R4  — Strategy selection               — chooses among methods based on problem structure
R5  — Counterfactual control           — holds branches; answers "what changes if X changes"
R6  — Error detection + local repair   — finds + fixes a wrong step
R7  — Global plan revision             — abandons a failing strategy + picks a new one
R8  — Representation shift             — re-encodes the problem into a better formalism
R9  — Compositional synthesis          — load-bearing composition that beats any individual part
R10 — Epistemic self-modeling          — knows what it knows / lacks / would need to test
R11 — Substrate formation              — extracts reusable structure from solved + failed attempts
R12 — Open-ended research behavior     — generates, tests, repairs, accumulates claims under falsification
```

### Each tier's falsification test

| Tier | Falsification test |
|---|---|
| R0 | Re-test on a paraphrased version. If accuracy drops > 50%, you're at R0. |
| R1 | Apply to a structurally-identical problem with variables renamed. R0 fails this; R1 passes. |
| R2 | Insert one irrelevant distractor step. R2 should still complete; R1 may drop. |
| R3 | Inject an inconsistent constraint. R3 should detect; R2 may produce a contradiction. |
| R4 | Give a problem solvable by ≥2 methods. R4 picks a method appropriate to structure; R3 picks arbitrarily. |
| R5 | Ask "what would happen if [premise] were reversed?" R5 maintains branches; R4 collapses to one answer. |
| R6 | Provide a partially-wrong proof and ask for fix. R6 localizes the error; R5 may rewrite the whole thing. |
| R7 | Set a problem where the obvious approach fails partway. R7 abandons + tries new strategy; R6 keeps repairing locally. |
| R8 | Set a problem easier in a non-default representation. R8 switches representation; R7 stays in the original. |
| R9 | **Single-primitive baseline test** (the one we ran on Apollo). R9 organism must beat the best of its constituent primitives by a meaningful margin. R8 produces compositions that don't lift over their parts. |
| R10 | Set a problem with deliberately ambiguous premises. R10 identifies the missing variable + asks; R9 picks an interpretation and proceeds. |
| R11 | Solve a sequence of related problems. R11 produces reusable lemmas / templates / abstractions across the sequence; R10 solves each independently. |
| R12 | Run a sequence of falsification cycles where the system's own claims are challenged. R12 generates new testable claims that survive; R11 may stop at first defensible answer. |

The tests are perturbation-based or comparison-based by design. **Each one is something you can run on a system + record the result.** Tier assignment is the lowest test the system passes consistently.

---

## Three orthogonal dimensions

The primary tier captures depth of reasoning. These three axes capture different qualities at any tier:

### Dimension F — Failure transformation depth

What kind of failure can the system recover from? Adapted from external review (2026-05-24).

```
F0  — Cannot detect failure
F1  — Detects contradiction after being told
F2  — Detects contradiction unaided
F3  — Local repair: fixes one step
F4  — Global repair: revises earlier assumptions
F5  — Strategy repair: changes method
F6  — Ontology repair: changes representation
F7  — Problem repair: reformulates the question
F8  — Epistemic repair: identifies why its own evidence was misleading
```

A system at primary tier R6 + failure dimension F3 is "fixes one step when given a wrong proof." A system at primary tier R8 + F6 is "re-encodes the problem when the current representation has hit its limit."

**This dimension is where Ergon's target lives.** Ergon's near-term north star is roughly F3-F6: detect + classify failures, predict required repair class.

### Dimension M — Representation mobility

Can the system move between representations? Compositional reasoning often requires representation choice that the original problem doesn't suggest.

```
M0 — Uses given representation only
M1 — Translates notation
M2 — Chooses from known representations
M3 — Compares two representations
M4 — Moves between representations mid-solution
M5 — Invents a representation specific to the problem
M6 — Extracts reusable representation schema
```

This dimension matters because most "reasoning" benchmarks fix the representation in the problem statement. A system at M2+ can route problems through better representations; a system at M0 can only solve what's already shaped for it.

**Apollo's gen-3551 is M0** — its organisms operate on whatever the trap battery hands them. The Branch C blackboard genome enables up to M3 (the blackboard *is* a representation that organisms can read/write).

### Dimension H — Epistemic humility

```
H0 — Always answers
H1 — Expresses uncertainty stylistically
H2 — Detects missing information
H3 — Identifies the exact missing variable
H4 — Gives conditional answers by assumption set
H5 — Designs a test to resolve the uncertainty
H6 — Updates after the test
```

LLMs frequently fake H1 (uncertain-sounding language) while failing H3-H6 (no actionable identification of what's missing).

**This is the discipline Aporia's substrate-shaped research needs** — distinguishing "I don't know" from "no one knows" from "I would know if I tested X."

---

## How Prometheus components map to the ladder

| Component | Target primary tier | Failure dim | Repr mobility | Humility |
|---|---|---|---|---|
| **Hephaestus** (atomic primitives) | R1 (each primitive does one operation correctly) | F2 (Hephaestus's ablation tests detect contradictions unaided) | M0 (primitives are fixed-representation) | H2 (forge knows when a primitive fails) |
| **Apollo** (compositions) | R9 (compositional synthesis) | F3 (local repair through mutation) | M0-M3 (Branch C enables M3 via blackboard) | H1 (organisms don't model their own uncertainty) |
| **Ergon** (failure prediction) | R6 (error detection + classification) | F3-F6 (predicts repair class) | M2-M3 (chooses among known failure-mode representations) | H3-H5 (identifies what test would distinguish failure modes) |
| **Aporia** (substrate research) | R10-R11 (epistemic self-modeling, substrate formation) | F5-F7 (strategy and problem repair) | M3-M5 | H3-H6 (designs tests, updates after) |
| **Learner** (eventual neural routing) | R8 (representation shift) at minimum | F2-F3 | M4 (mid-solution representation moves) | H1-H2 |

These are *targets*. Apollo's current actual reading is roughly **R2** with one trick (`fencepost_count → bayesian_update`) that fakes R9. The gap between target and actual is what the next branches address.

---

## Where Apollo's gen-3551 sits (worked example)

Applying the ladder to Apollo's most-recent diagnostic data:

| Tier | Apollo passes? | Evidence |
|---|---|---|
| R0 | ✓ | Produces answers on the trap battery |
| R1 | ✓ | Individual primitives work; ablation shows they perturb output |
| R2 | ✓ | Multi-step chains execute without crashing (compile_success = 100%) |
| R3 | **?** | No clear evidence of constraint maintenance — the 2-primitive recipe doesn't track multiple constraints |
| R4 | ✗ | No evidence of strategy selection — same recipe applied to all categories |
| R5 | ✗ | Doesn't hold counterfactual branches |
| R6 | ✗ | No error detection mechanism inside the organism |
| R9 | **✗ — falsified by single-primitive baseline test** | 0/5 elites lift over best single primitive |

Apollo currently sits at **R2** with one decorative-composition trick that mimics R9 surface. The Branch C blackboard genome is designed to enable R3-R5 (constraint maintenance via typed state, strategy dispatch via meta-pipeline, counterfactual reasoning via held alternatives in the blackboard). Whether it actually reaches those tiers will be measured by the same kind of falsification tests.

This is what the ladder is for: **separating "system that produces R9-shaped output" from "system that occupies R9."** The first is easy. The second is the point.

---

## Practical uses of the ladder (now)

1. **Apollo Branch C success criteria**: targets R3 (constraint maintenance), with explicit falsification tests at each tier. Don't graduate Branch C without passing R3's falsification (inject inconsistent constraint, organism should reject).
2. **Ergon training labels**: every Apollo failure record should carry a tier-prediction (`predicted_tier`) + actual failure dimension reading (`F`). Ergon learns to predict the latter from the former.
3. **Trap battery audit**: the trap battery's "longest candidate" Goodhart hole (52% accuracy from a non-reasoning hack) is itself a tier-R0 system passing the battery. The audit asks: does each battery item have a falsification-test partner that distinguishes tier-N from tier-N-1?
4. **Hephaestus primitive contracts**: each forged primitive should declare the tier it occupies + the falsification test that confirms it. "Tier R1 + F2" makes Hephaestus's typed contracts stronger.

---

## What this ladder does NOT do

- It doesn't dictate model size, training method, or architecture. A 2.5B model could occupy R5 on a small task family; a 70B model could be stuck at R0 on a different one.
- It doesn't replace benchmarks. Benchmarks measure scoring; tiers measure mechanism. Use both.
- It doesn't claim "higher tier = better." Tier appropriateness is task-relative. Many tasks genuinely don't require R9; settling at R3 with strong falsification tests is preferable to faking R9 with no tests.
- It doesn't yet have inter-rater reliability. Two people may classify Apollo as R2 vs R3 today. We'll converge as we accumulate worked examples.

---

## What's missing from v0.1 (TODO for v0.2)

- **Tier R3-R5 falsification tests are vague.** The R9 test (single-primitive baseline matrix) is sharp because we ran it. R3-R5 need similarly concrete instruments.
- **No standard logging schema** for tier readings. Apollo / Ergon / Aporia should emit ladder readings in their structured logs in a unified format.
- **No bridging to safety / interpretability literature.** The dimension-H (epistemic humility) tiers map to existing alignment-evals work that we haven't surveyed.
- **R11-R12 are aspirational, not falsifiable.** "Substrate formation" and "open-ended research behavior" need worked examples before they can carry falsification tests.

---

## Reading list

External review (2026-05-24) sourced several frames worth re-reading:
- Bloom's taxonomy as the educational ladder baseline
- RE-IMAGINE (Microsoft) for benchmark mutation as a tier instrument
- Modern reasoning-model surveys (chain-of-thought scaling, RL verifier training, inference-time scaling) — useful negative space: they organize by method, not by mechanism
- AlphaEvolve / FunSearch (DeepMind) for "evaluator + search ecology" as the engine of compositional discovery — directly relevant to Apollo's Branch C
- Lehman & Stanley (novelty search, MAP-Elites) for diversity-preserving search and the limits of selection pressure on collapsed populations

The doctrine sentence at the top — "occupy the tier only if mechanism survives perturbation, beats lower-tier baselines, fails in tier-predicted way" — is the project's contribution. The rest is synthesis of existing pieces into a shared frame.

---

*v0.1. Will be wrong. Suggestions welcome — particularly on R3-R5 falsification instruments and the dimension-H mapping to existing alignment-evals work.*
