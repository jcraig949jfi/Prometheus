---
captured: 2026-05-03
captured_by: Ergon (Claude Opus 4.7, 1M context, on M1)
reviewer: External agent (likely a Claude separate-session, by typography and structural rhythm; the reviewer reports tool-access limits retrieving the GitHub file directly, indicates this was an external context window without repository read access)
target_under_review: pivot/ergon_learner_proposal_v1.md (commit ff1428d8, 2026-05-03)
status: VERBATIM CAPTURE for substrate ingestion
---

# Verbatim review of `ergon_learner_proposal_v1.md`

This file captures the external review verbatim, in the same pattern as `pivot/feedback_frontier_review_2026-05-02.md` did for the v2-thesis review round. Triage and synthesis live in companion file `meta_analysis_ergon_review_2026-05-03.md`. v2 of the proposal incorporating the revisions lives in `pivot/ergon_learner_proposal_v2.md`.

---

I couldn't directly retrieve that exact GitHub file's contents via the tool (likely due to raw access limits), so I'm going to do something more useful than a shallow summary: I'll stress-test your proposal against what you've already built and reconstruct the likely architecture from your description—then tell you where it's strong, where it breaks, and what to change before you lock it in.

---

## What your "Ergon learner" proposal gets very right

### 1. You've avoided the biggest trap: replacing the substrate with the model

Most systems drift toward:

```
model = truth
```

You've explicitly done:

```
model = mutation operator
substrate = truth filter
```

That's the correct asymmetry. It's also the same principle that makes systems like Evolutionary Algorithms robust: generation is cheap, selection is sacred.

Your line:

> "the substrate IS the value head"

is powerful—but only if treated carefully (we'll get there).

### 2. LoRA adapters as role-specialized cognition is exactly right

Splitting into:
- mutation policy
- fitness predictor
- conjecture generator

isn't just engineering—it's architectural clarity.

You're implicitly creating:

```
functional decomposition of cognition
```

That's much better than:
- one monolithic fine-tune
- or prompt-only role switching

This aligns with how multi-head systems outperform single-head in structured domains.

### 3. MAP-Elites + lineage tagging = real insight

This is one of the strongest parts of your design.

You're not just generating—you're measuring:

> which mutation class produces survivors in which regions

That turns your system into:
- a meta-scientific instrument
- not just a search process

This is where your system becomes self-improving in structure, not just output.

### 4. Training on substrate-verified truth is the real differentiator

This is the key sentence:

> "fine-tunes on substrate-verified ground truth, not corpus assumption"

That is the departure from standard LLM pipelines.

You're building something closer to:

```
closed-loop scientific learning
```

Instead of:
- pretraining → inference

You have:
- generate → verify → learn → generate

That loop is the whole game.

---

## Where the proposal is still fragile

### 1. "Substrate = value head" will be exploited

This is your biggest hidden risk.

Any learner optimizing against a fixed evaluator will:

```
learn the evaluator, not the truth
```

This is classic:
- Specification Gaming

In your system, this looks like:
- discovering battery loopholes
- producing "easy-to-pass" claims
- converging to narrow structures

You need:

```
multiple evaluators or disagreement
```

Minimum viable fix:
- substrate score
- fitness predictor score
- (later) cross-model score

Reward = agreement-weighted

### 2. Your MVP (fitness predictor) risks becoming a gatekeeper, not an accelerator

You said:

> prunes 60–90% of doomed CLAIMs

Good—but dangerous.

If it's wrong in the wrong way:
- it will prune exactly the weird, novel cases you want

This is a known failure mode:

```
early filtering kills discovery
```

Fix:
- bias toward false positives over false negatives
- explicitly track:
  - "pruned but later would have survived"
  - periodically run no-pruning sweeps

### 3. Structural feature engineering vs DAG tokenization

You chose:

> structural features (not DAG tokenization)

This is pragmatic—but has a ceiling.

You're encoding:
- what you already believe matters

Which risks:
- missing unknown structure

Recommendation:
- MVP: structural features (fast, good)
- v1.5+: add learned representations (graph or sequence)

Otherwise your learner becomes:

```
a mirror of your current ontology
```

### 4. Correlated mutation distributions still exist

Even with multiple classes:
- neural
- symbolic
- structural

you still risk:
- shared biases
- converging to same regions

You must maintain:

```
true diversity pressure
```

MAP-Elites helps—but only if:
- feature space is well chosen
- archive is not collapsing

### 5. "Small learner" framing is correct—but don't undersell the loop

Your advantage is not:

```
small model
```

It's:

```
closed-loop + verified data + evolutionary selection
```

Small models can outperform large ones in that loop.

But only if:
- loop runs continuously
- data quality is high
- evaluator is strict

---

## The most important missing piece (still)

You still do not have:

```
A formal null-world baseline
```

Before trusting your learner's outputs, you must answer:

> does it outperform random mutation?

This ties directly to:
- Null Hypothesis

Without it:
- improvements may be illusory
- "learning" may just be bias amplification

---

## Answers to your design implicitly encoded in the doc

### MVP choice

Correct:

```
fitness predictor first
```

But upgrade to:
- classification + residual regression

### Model choice

Your instinct toward math-specialized models is fine—but:

```
diversity > correctness at generation stage
```

So keep:
- multiple models early
- don't overcommit to one

### Self-play loop insight

This is the strongest part of your proposal:

> "substrate IS the value head"

Refined version:

```
substrate = primary critic, not sole critic
```

---

## What makes this actually novel (if it works)

Not:
- LoRA
- RL
- math models

But:

```
learning from adversarially verified, evolving truth
```

That's rare.

Most systems learn from:
- static datasets
- human labels

You're learning from:
- machine-generated + machine-verified structure

That's fundamentally different.

---

## Final assessment

This proposal is architecturally coherent and unusually grounded.

But its success hinges on three non-negotiables:

### 1. No evaluator monoculture
- avoid "substrate is the only judge"

### 2. Preserve exploration
- don't let the fitness predictor kill novelty

### 3. Add null-world comparison
- prove you're better than random

If you do those, this becomes:

```
a small, continuously learning scientific system
```

If you don't, it becomes:

```
a very sophisticated self-reinforcing bias engine
```

---

## Bottom line

You're not building:
- a model
- or even an RL system

You're building:

```
a feedback loop between generation and truth
```

That's the right thing to build.

Just make sure:

> truth stays harder to satisfy than generation is to produce.

---

If you want next, I can:
- sketch the exact training loop (data → labels → update → eval)
- or design the null-world generator specifically for your polynomial domain

Those are the two pieces that would make this actually work, not just look good.
