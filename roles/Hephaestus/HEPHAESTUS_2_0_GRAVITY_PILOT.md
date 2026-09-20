# HEPHAESTUS 2.0 — GRAVITY PILOT

**Status:** Proposal (not yet funded/staffed)  
**Authored:** 2026-09-20 (operator)  
**Audience:** Hephaestus seat and review

---

## Premise

Do not resurrect Hephaestus as a forge yet. Resurrect it first as an instrument for measuring:

1. Can modern frontier models produce materially better cross-field mechanistic syntheses than the old Hephaestus generation?
2. When they do, how much gravitational pull toward known human machinery remains?

That gives us a clean Hephaestus 2.0 pilot without committing to a new subsystem.

---

## The Key Change

The output is no longer "write me an algorithm." It is a **mechanism hypothesis with enough causal structure to attack.**

A triplet like `Autopoiesis × Constraint Satisfaction × Fractal Geometry` should not earn points because the model invents an impressive name. It should have to say:

- state variables
- local rules
- information flow
- what each source concept contributes causally
- what behavior should emerge
- what disappears if each contribution is removed
- closest known mechanisms
- one minimal experiment capable of falsifying the synthesis

Then we can ask whether that mechanism is actually more than a metaphor.

---

## The Interesting Experiment

Take only about **1% of the old corpus initially**—roughly 50–60 triplets.

### Stratification

Rather than blind sampling, stratify by:
- old "high potential" specimens
- failures
- cross-field extremes
- combinations whose old Hephaestus implementation collapsed into generic machinery

### Three Artifacts Per Triplet

- **OLD:** original Nous/Hephaestus synthesis
- **NEW:** modern Fable/Astra synthesis
- **BLIND:** mechanism description with concept names removed

### Two Assays

#### Assay A — Synthesis Improvement

Does the modern model give us an actually testable mechanism?

- Can we identify state, operations, causal dependency, intervention and falsifier?
- Does removal of one concept materially alter the mechanism, or are the three labels decorative?

#### Assay B — Gravitational Pull

Give the BLIND mechanism to a different model and ask it to recover known ancestors from any field.

- Don't ask "is this novel?" 
- Ask for the nearest known mechanisms and discriminating experiments.

### Output Format

```
triplet: X × Y × Z
mechanism_specificity:       HIGH
three_way_causal_dependency: MEDIUM
nearest_prior:
    predictive processing / reservoir dynamics
prior_fit:                   0.81
unexplained_residual:        0.14
cross_model_agreement:       HIGH
result:
FAMILIAR_MECHANISM_IN_NEW_CLOTHING
```

versus

```
nearest_priors:
    stigmergy             weak
    autocatalysis         weak
    hysteretic control    weak
no candidate explains:
    delayed distributed inheritance
    intervention response
    persistence after component turnover
result:
LOW_GRAVITY — EXPERIMENT CANDIDATE
```

The second one earns a toy experiment.

---

## The Crucial Conversion

**Hephaestus doesn't decide novelty. It nominates low-gravity mechanisms for empirical testing.**

### Calibration Control

Feed the gravitational detector known mechanisms with the vocabulary stripped off:

- TCP congestion control disguised as ecology
- PID expressed as molecular interactions
- Hebbian learning with anonymous registers
- Kalman filtering represented as population state
- Reaction-diffusion without chemistry terminology
- Stigmergy without ants

If the detector can't recover those, its "I don't recognize this" signal means nothing.

Also give it arbitrary nonsense and weird mixtures of two familiar mechanisms. We want to know whether it falsely hallucinates ancestry for everything.

**Calibration result:**
- known familiar mechanisms → should show HIGH gravity
- renamed familiar mechanisms → should still show HIGH gravity
- random nonsense → should not be confidently mapped
- novel composites → intermediate/uncertain
- Prometheus specimens → unknown

Now we have an actual instrument rather than vibes.

---

## Where Astra Belongs

Do not burn Astra across all 5,000+ triplets.

**Fable 5.1** is probably ideal for the broad regeneration pass. Then Astra gets perhaps the 10–20 strangest survivors plus calibration specimens.

### Crossed-Model Experiment

On perhaps 10 shared triplets:
- Fable generates → Astra detects priors
- Astra generates → Fable detects priors

If Astra-generated mechanisms systematically have larger unexplained residuals—or merely more sophisticated descriptions of familiar mechanisms—that tells us something.

---

## Specification for Implementation

### Do Not Build

- No service, daemon, queue, UI, or production pipeline
- Build the smallest reproducible experiment capable of answering the question

### Historical Source

Locate the committed historical Nous / Hephaestus corpus in the Prometheus repository. Do not modify it.

Build a loader that recovers for each usable specimen:
- triplet / concept_names
- concept_fields
- historical synthesis
- historical ratings if present
- forge outcome if joinable without heroic work

**Report exact corpus counts discovered** rather than assuming remembered numbers.

### Pilot Sample

Select approximately 1% of the usable historical corpus, capped around 64 specimens. Use a deterministic seed.

Stratification:
- historical high/low scores
- forged/scrapped if joinable
- strongly cross-field vs less cross-field
- diverse concept families

**Freeze the specimen IDs before any new model output is generated.**

### Modern Synthesis Contract

For each triplet, ask the generator for a mechanism hypothesis, not code.

**Require:**
1. state / representation
2. transition or computational operations
3. information flow
4. causal contribution of each of the three source concepts
5. predicted behavior
6. one knockout for each concept
7. strongest boring/familiar alternative
8. minimal falsifying experiment
9. no novelty score

**Reject outputs** that consist only of analogy, architectural naming, or generic "combine three modules" prose.

Make the prompt and model identity **immutable artifacts.**

### Blind Representation

Produce a second form of every synthesis with:
- concept names removed
- source fields removed
- invented architecture names removed
- explicit novelty claims removed

Preserve actual causal/mechanistic content.

### Gravity Assay

A model different from the generator receives only the blind mechanism.

**Questions:**
- What known mechanisms from science, engineering, mathematics or computation could generate these behaviors?
- Give the three closest known analogues.
- For each analogue, identify which observations it explains and which it does not.
- What intervention would distinguish the proposed mechanism from that familiar analogue?
- Can the mechanism be losslessly described using existing standard terminology?
- What important residual remains unexplained?

**Record structured results:**
- nearest_priors
- prior_fit
- cross_prior_convergence
- vocabulary_compressibility
- unexplained_residual
- discriminating_interventions

Do not collapse these to one authoritative novelty score.

### Calibration Set

Build at least 12 hand-authored controls:
- familiar mechanisms under ordinary names
- the same mechanisms with alien terminology
- composites of two familiar mechanisms
- several intentionally incoherent mechanisms

**Candidate controls:**
- PID control
- TCP-style congestion control
- Hebbian adaptation
- Kalman-like estimation
- reaction-diffusion
- finite-state control
- stigmergy
- autocatalytic cycles

Do not leak their true identity into the blinded detector packet.

The gravity assay is uninterpretable unless it recognizes disguised familiar mechanisms substantially better than chance/controls.

### Historical Comparison

Construct a deterministic rubric measuring only things that can be inspected:
- explicit state
- explicit transitions
- actual three-way causal dependency
- intervention specification
- falsifier specificity
- implementation/testability
- decorative-concept dependence

Apply the same rubric to OLD and NEW synthesis.

Do not let the same model both generate a synthesis and grade it where avoidable.

### Optional Crossed-Model Arm

If access and budget permit, select only ~10 triplets for Fable/Astra crossed synthesis and review.

Keep this separate from the main pilot. Do not spend Astra quota broadly without explicit operator approval.

### Expected Output Structure

```
experiments/hephaestus2_gravity/
    DESIGN.md
    sample.jsonl
    prompts/
    historical/
    generated/
    blind/
    controls/
    results/
    REPORT.md
```

### REPORT.md Should Answer

1. Are modern syntheses measurably more mechanistic/testable than historical ones?
2. Does the gravity detector recover disguised familiar mechanisms?
3. How often do modern syntheses collapse onto recognizable prior machinery?
4. Are there any specimens with both high mechanistic specificity and unusually low prior fit?
5. Which, if any, deserve a cheap toy-world experiment?

### Important

A low-gravity result is **not a novelty claim.**

It means only: "Our calibrated prior-recognition instrument failed to compress this specimen into familiar machinery; investigate."

Do not implement any nominated mechanism yet. Stop after the report.

---

## Why This Matters

This pilot has unusually high upside because even a negative result is informative:

- **If modern models simply produce better prose wrapped around the same five attractors:** Hephaestus stays buried.
- **If Fable/Astra produce much more causally coherent syntheses but nearly everything maps onto established priors:** The models have improved as mechanism articulators, not novelty generators—which is useful in its own way.
- **If a small fraction are simultaneously mechanistically precise, causally irreducible to the labels, and low-gravity under a calibrated detector:** We've got exactly what we need: a machine for finding weird hypotheses worth giving to a Fable agent for a day and seeing whether reality kills them.

That last case is enough to justify a real Hephaestus 2.0 later.

---

## Attribution

Authored by operator, 2026-09-20.

Approved for documentation and exploration; no implementation commitment yet.
