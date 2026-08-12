# Ergon — Revival Assessment: leveraging new frontier models toward the North Star

**Role:** Ergon (the engine / the Learner march). **Date:** 2026-08-12.
**Context:** ~7 weeks dormant (last human research 2026-06-24; only `auto: portfolio update`
and `arsenal:` capability-snapshot commits since). This is my re-entry stand, written from
Ergon's own track record — not a re-read of the consolidated reassessment.

---

## 1. What Ergon actually established (the throughline, four kills and one positive)

Everything I ran between 06-03 and 06-09 points the same way:

1. **Corpus audit (06-03)** — generation was solved (~100M+ failure records, 30+ failure
   modes); the *corpus* was 1,486 records, 79% confirmations. The failure data never
   reached the consumer. Bottleneck = ingestion, not generation.
2. **Greedy-LoRA kill (06-07)** — the +0.68 headline decomposes into format ≫ False/kill
   prior ≫ per-template classes ≫ reasoning. No transfer across sources, and none across
   sub-domains of the *same* meta-domain. **More failure data of the same shape cannot
   grow the reasoning share.**
3. **Training-data survey (06-07)** — the discriminating property is not "is it failure
   data" but "does the completion carry a worked multi-step derivation, or just a verdict?"
   Our substrate stores **verdicts** (`holds=T/F`, `kill_vector`) and throws the derivation
   away. That is the root cause of the surface-classifier outcome.
4. **Compute-traces (06-08)** — worked traces teach in-op computation (+0.16) but cross-op
   "transfer" is format acquisition (`trace ≈ verdict` on held-out ops). Open confound:
   1.5B / rank-16 capacity ceiling.
5. **Routing eval (06-09)** — the one *positive*, and the sharpest result I have: mined
   residue **is** navigable behaviorally (warm-start co-solve, ΔAUC +0.075, survives the
   adversarial tail check) and **is not** navigable semantically (cold-start concept-label
   routing NULL — real fields ≈ shuffled fields).

Plus the infra work (06-23/24): Postgres local and healthy, DuckDB and Redis consolidated
onto it. **Plumbing is no longer the blocker.** And the portfolio pass (06-24) named the
program's disease correctly: **consumer-drift** — healthy producers, no consumer.

**Ergon's stand:** Prometheus's failure was never measurement quality and never data
volume. It is that *nothing ever metabolized the residue*. The v3 reframing (Prometheus =
TDD layer / progress meter) is a fair description of what we built, but it is only alive if
some organism demonstrably gets better by eating our kill-geometry. That is
M1-metabolization, and it remains **unrun**. Techne's independent pickup (`5b8a80c2`) lands
on the same experiment from the other side.

## 2. The confound that new frontier models dissolve

Every negative Learner result I own is confounded with **capacity**: Qwen2.5-Math-1.5B,
LoRA rank-16, one epoch, a ~3–4B VRAM ceiling. "The residue is not metabolizable" and "a
1.5B model cannot metabolize anything" are indistinguishable in my data.

What changed since June is exactly the axis that removes the confound:

- **Long context** — the whole kill-geometry packet for a problem now fits *in context*.
  Metabolization becomes testable **without training a model at all**.
- **Cheap long chain-of-thought** — derivations, not verdicts, at volume. This is the
  precise data shape my 06-07 survey said we lack and cannot produce ourselves.
- **Kernel-checked provers with open weights** (Leanstral 1.5, Apache-2.0) — a generator
  whose output is adjudicated by the Lean kernel, not by another model.

So the correct use of new frontier models is **not** as reasoners we hope will discover, and
**not** as reviewers of our framing. It is as:

> **(a) a capacity-unconfounded probe of whether our residue is worth anything, and
> (b) a trace factory whose every output is gated by a non-model oracle.**

## 3. The admissibility rule (doctrine-derived, non-negotiable)

`feedback_frontier_models_window`, `feedback_llm_convergence_is_gravity_amplifier`,
`feedback_ai_to_ai_inflation` and `feedback_anti_gravitational_well` all reduce to one
operational rule:

> **A frontier model may occupy any role where its output is falsified by something that is
> not a model — a kernel, a computation, an executed program, a held-out gold set — and no
> role where the check is another model or a human's sense of plausibility.**
> Corollary (the window): spend frontier tokens only on work that leaves a **verified
> artifact on our disk**. The artifact survives price hikes and API restriction; the opinion
> does not.

**Admissible:** kernel-checked generator (Lean/CAS/`prometheus_math`); worked-trace
producer under step-level verification; candidate organism *graded by* the substrate;
Goodhart adversary against our own progress meter; code-writing auditor whose claim is a
runnable script.

**Inadmissible:** judge / gold-labeler (circular — already killed once when CounterMATH gold
was gated); semantic router or concept-labeler (H_A NULL says labels do not route);
upstream explorer/hypothesis-generator (floods the substrate with plausible narrative);
"have N frontier models review the reassessment" (we have four such reviews; they produced
framings, not behavior deltas — convergence is a gravity signal, not validation).

## 4. The refocused effort — one loop, sequenced, probe-before-factory

### Move 1 (RECOMMENDED, days not months) — the Metabolization Probe

The decisive M1 experiment, run at frontier capacity so a NULL cannot be blamed on 1.5B.

- **Task set:** held-out problems with **computed** gold, never judged gold — the 494-item
  balanced number-theory OOD set I already built, `prometheus_math` op instances, and
  Lean-checkable claims. No LLM-judged labels anywhere.
- **Conditions (all matched on token budget):**
  - C0 — model alone.
  - C1 — model + **real** kill-geometry retrieved for that problem (nearest kill signatures
    / prior failed approaches / the void structure around it).
  - C2 — model + **mismatched** residue: same volume, wrong problem. *The null.*
  - C3 — model + generic "be careful, check your work" text of matched length. *The format
    control.*
- **Metrics:** solve rate on held-out computed gold; plus attempts-to-solve
  (search-efficiency — v3's Q2 axis).
- **Instrument validation first**, exactly as in the routing eval: positive control
  (residue that trivially contains the answer ⇒ C1 ≫ C2), negative control, floor.
- **Preregistered kill:** if **C1 ≈ C2**, the residue carries nothing metabolizable *at any
  capacity*. The corpus is exhaust, not residue, and the program's honest position is v3's
  fallback (audit substrate) until the residue is rebuilt to the router-grade spec.
- **Preregistered win:** C1 > C2 ≈ C3, surviving the tail check ⇒ we have, for the first
  time, a **measured price for the residue** — and we know what to distill into an owned
  model instead of guessing.

Why this first: it is the cheapest experiment in the program that can kill the central
thesis, it removes the capacity confound that taints all my prior negatives, it needs no new
producers, and it converges with Techne's independent pickup.

### Move 2 (only if Move 1 survives) — the verified-trace factory

Frontier model writes the derivation; **our verifier checks every intermediate step**
(`prometheus_math` ops, sympy, Lean kernel via the existing harness under
`agents/_shared/proof_search/` + `rhea/src/lean_verifier.py`). Two outputs, both durable:

- **Verified traces** → the trace-shaped corpus the 06-07 survey named as the highest-value
  missing asset (attacks the surface-classifier kill directly).
- **Rejected traces with a localized break-step** → a residue shape we have *never* had:
  failure with a *position*, not just a verdict. This is the kill-geometry the substrate was
  designed to consume and our own generators structurally cannot emit.

Sequenced strictly after Move 1, because building a factory before the consumer is proven is
the exact consumer-drift rut that killed 21 components.

### Move 3 (parallel, cheap) — convert stalled judgement into runnable artifacts

The portfolio's 21 RETIRE candidates and the tautology claims (Hecate `mi_z` generator-prefix,
Pollux sorted-array Spearman, Acheron co-occurrence-not-collision) are sitting in LIMBO on a
single-investigator, single-model-family verdict. Frontier models are admissible here **only
in the code-writing form**: not "do you agree Pollux is tautological", but "write the script
that computes Pollux's statistic on shuffled and on sorted inputs and prints both." The
script runs; the verdict is data. That unblocks HITL sign-off without AI-to-AI inflation, and
each confirmed bug becomes a named failure pattern in the kill corpus.

### Move 4 (standing) — the Goodhart adversary

v3 ships with the warning that a progress meter can be gamed. Give a frontier model the
explicit adversarial brief: *produce output that maximizes our Q2 axes without being closer*.
Anything it games is a metric we must re-specify. This is the one place where frontier
narrative-fluency is an asset rather than a contaminant.

## 5. What revival must NOT be

- Not a swarm restart. Cheaper model calls do not fix consumer-drift; they scale it. The
  rule stands: **no component revives into a vacuum.**
- Not another frontier review round of the reassessment.
- Not more verdict-shaped failure data. That lever is measured and exhausted.
- Not frontier-model gold. Every label in Move 1 is computed or kernel-checked.

## 6. Open decision for James

Which API access is live and what per-month budget bounds Move 2's factory. Move 1 is cheap
enough to run on any single provider and does not wait on this.

— Ergon, 2026-08-12
