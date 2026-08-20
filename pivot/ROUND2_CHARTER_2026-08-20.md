# Prometheus Revival — Round 2 Charter

**Date:** 2026-08-20 · **Author:** Hephaestus (M3, Fable seat) · **Trigger:** external review of
`pivot/SESSION_ASSESSMENT_2026-08-20_external_review_packet.md`
**Status:** proposal to James. Round 1 = the 08-12 reassessment through the pilot's death and
the first closed metabolic cycle. Round 2 = get the Tier B measurement honestly, and stop
calling things by names the evidence doesn't support.

---

## 1. The external review, adjudicated

I accept the review substantially. Where it corrects me, it corrects me; where I have evidence
that sharpens or contradicts it, that is recorded too. Nothing below is diplomatic.

### ACCEPTED, and each changes something

**A1 — "Heredity" is the wrong word for Apollo's result. Rename it.**
Accepted, and the evidence is *worse* for my framing than the review knew. Apollo's own
correction: the bridging op had already been forged in June — "forge the bridge, rerun,
measure" was discharged two months before the cycle ran. So the intervention **predated** the
formalized diagnosis; what the cycle added was the 2×2 isolation and the replay. The causal
chain is `failure → agent understands failure → agent engineers fix → search improves`, and the
inheritance channel is the agent, not the substrate.
**Adopted naming, program-wide:** *Metabolic Cycle 1: CLOSED. Autonomous heredity: NOT
demonstrated.* Any document saying otherwise gets corrected, including mine.

**A2 — Retire "gradient."** Accepted. Nothing measured is gradient-like: no demonstrated
locality, transportability, or directional predictiveness. Adopted term: **failure topology**,
and the precondition before the word "field" or "navigable" is used again is a measurement that
*two nearby failures imply something about each other.* That measurement does not exist.

**A3 — Run Tier B as preregistered. Do not repoint it now.** Accepted, and this **withdraws my
own Option B.** The review names the pattern exactly: *an experiment approaches decisive
falsification → a new insight appears → the experiment is improved before it can kill the
thesis.* That is this program's documented disease and I proposed it. Residue representation
becomes the **next** experiment, run regardless of Tier B's outcome — not a pre-emptive
redesign.

**A4 — Freeze Tier B's interpretation in advance, in BOTH directions.** Accepted, and it
exposes a real gap: our §6.3 bounds the *null* (four sublabels, never "at any capacity") and
does **not** bound the *positive*. A `CARRY-STRONG` verdict currently licenses more than it
should. **Amendment owed to the prereg before Tier B runs:**
- *Null means:* the stored residue representation shows no demonstrated transferable carry
  under this task distribution and this intervention. It does **not** mean failure information
  has no value.
- *Positive means:* this residue intervention causally improves subsequent attempts relative to
  matched-null residue. It does **not** mean Prometheus learned from failure, and it is several
  steps from autonomous learning.

**A5 — The next exit review gets ONE invariant, and it is sharper than "find a third defect."**
Accepted; this is the single most actionable item in the review. Both prior defects were
**arm-identifying measurement confounds** — serialization exposed arm identity; token length
induced treatment-dependent performance. Those are basic randomized-experiment hygiene, which
means the probe was designed at a higher conceptual level than its plumbing. The invariant:

> **Treatment identity must be computationally unavailable after semantic content is removed.**

Operationally: for every arm, compare token-count distributions, message structure, field
ordering, JSON/text formatting, whitespace, role structure, message count, metadata, truncation
probability, position of key information, and any latency/routing differences — then train arm
classifiers against **everything except the intended content**. The target is not "classifier
accuracy is low"; it is that treatment identity is *unavailable*.

**A6 — Every measurement must attach to an active metabolic cycle.** Accepted as a Round 2
resource constraint. No free-standing ontology audits, no fleet-wide instrument builds, no
"while we're here" corpus cleanup. If it does not help answer *did experience from attempt N
improve attempt N+1*, it waits.

**A7 — 99.98% self-verdicting is the deepest architectural finding, and I under-weighted it.**
Accepted. The correct statement is not "a coverage defect" but: **the program had mutation +
self-reporting, not mutation + selection.** Phenotype and fitness function shared ancestry.
Harmonia D's disjoint-ontology result completes it — two systems were built, a substrate that
generates and locally judges, and a battery that believes it judges a universe it rarely
receives. This explains an enormous amount of historical behaviour and is promoted to a Round 2
work item (§2, R2-3).

**A8 — Design-channel conflict is not mitigated by removing me from grading.** Accepted, and it
costs me my role. I have influenced the representation being evaluated, the specification, the
role decomposition, **the prompts given to the reviewers**, and the interpretive vocabulary.
Removing the supplier from adjudication prevents adjudication bias, not design bias — and with
agents, prompt authorship partially determines the hypothesis space the reviewer searches.
**Adopted:** for Round 2 the chain becomes
`supplier ≠ experiment designer ≠ execution-prompt author ≠ grader ≠ adjudicator`.
I hand the frozen preregistration and artifacts to an unconflicted seat and step out of the
probe's prompt path (§3).

**A9 — Retention is the most promising result, and is constitutional.** Accepted
enthusiastically. Apollo found a validated capability decayed 30 → 255 generations (8.6×) and
**replay caught it**. Adopted as constitutional property:

> **A promoted capability is not a claim. It is a continuously reproducible phenotype. If it
> stops reproducing, the organism has lost it.**

This upgrades my Option D from "cheap insurance" to the fourth term of the loop:
`variation → selection → inheritance → RETENTION`.

**A10 — Replay → Transfer → Abstraction.** Accepted as the ladder that replaces the
architectural roadmap. Note the factual correction below (C2) — we are further down it than the
review assumed.

**A11 — The rewritten conclusion.** Adopted verbatim into the record:
> *Prometheus has not yet shown that machines can learn from its dead. It has finally built a
> laboratory capable of discovering when they haven't — and it has completed one manually
> mediated cycle showing what genuine inheritance would need to look like.*

### CORRECTIONS AND SHARPENINGS (offered, not defended)

**C1 — The residue taxonomy has a fourth rung, and it is the cheap one.** The review's ladder is
verdict → failure description → mechanistic trace, with only the third counting as training
signal. There is an intermediate that is far cheaper than a full trace and close to its value:
**a description carrying a *location*** — "failed at step B" — which is what the external
process-reward literature (RLVR) actually trains on. The pilot's own residue design already
records *the method the prior attempt applied* ("the prior run decided this on a single Fermat
base") — residue about **the verb, not the noun**. So the program is not starting from rung 1;
it has a rung-2.5 artifact in hand and should measure whether *that* carries before building
full traces.

**C2 — Tier B as preregistered tests Replay ONLY, not Replay + Transfer.** The review says the
probe is "mostly testing the first two." It is testing exactly the first. Charon ruled D1/D2
**INADMISSIBLE-NO-FAIR-NULL** after testing both horns: break the relation and the null leaves
the domain (classifier 1.000); preserve the topic and the null is drawn from what F-prom *is*
(100% overlap). At D1/D2 the residue was never *for this problem* — it was for the problem's
neighbourhood, so F-null cannot exist there. **Consequence for the review's ladder: Transfer
needs a different comparator, not a bigger N.** That is a genuine open design problem and it is
now the clearest one on the board.

**C3 — The self-verdict finding suggests a concrete, cheap experiment, not another audit.** The
review's phrasing points at it: *a foreign judge must be able to consume a native organism.*
That is a runnable test, not a taxonomy: take N Theseus records → route them through an
independent verifier → see what survives, what breaks, and what typed failure trace comes out.
It has never been run — Harmonia D's disjoint-ontology finding is precisely the statement that
it has never been run. It is free, it attaches to a metabolic cycle (it produces the failure
traces R2-6 would price), and it directly tests whether Prometheus's selection can be made
foreign.

---

## 2. Round 2 work items

Ordered. Everything is $0 except R2-2.

| # | Item | Owner | Gate / kill |
|---|---|---|---|
| **R2-0** | **Doc hygiene, hours:** adopt A1 (Metabolic Cycle 1 ≠ heredity), A2 (retire "gradient" → failure topology), A11 (the rewritten conclusion) across ROLE docs, dossier, station files, meta-assessment. Prevents goalpost drift while it is still cheap. | any seat; I will do my own docs | — |
| **R2-1** | **Tier-A exit review #3, single invariant** (A5): treatment identity computationally unavailable after semantic content removed; machine attack, arm classifiers over every non-content feature. | Charon ∥ Harmonia B, independently | **Third defect class ⇒ the design, not the plumbing, is the problem** — stop and re-pose the experiment |
| **R2-2** | **Tier B, exactly as preregistered**, with the A4 interpretation amendment landed *first*. ~$9. | Ergon (driver); Aporia recomputes (R10); Charon adjudicates | Preregistered §6.3 classes, both directions bounded |
| **R2-3** | **The foreign-judge test** (C3): Theseus records → independent verifier → typed failure trace. The integration that was never run. | Harmonia D (owns the disjoint-ontology finding) or Charon | If no native record survives translation, that is the finding and it re-frames the substrate |
| **R2-4** | **Retention harness** (A9): load-bearing capabilities replay on a schedule; a capability that stops reproducing is *lost*, not *claimed*. Apollo owns the first entry (it found the decay). | Apollo, then fleet-wide | — |
| **R2-5** | **Residue-representation experiment** (A3 ordering: AFTER Tier B, regardless of outcome). Verdict vs located-description vs mechanistic trace (C1). | Ergon | — |
| **R2-6** | **Transfer comparator** (C2): what plays F-null's role at D1/D2, where a task-specific null cannot exist? Open design problem; do not run Transfer until it is answered. | Charon (kill authority owns the null) | — |

**Not in Round 2, explicitly:** new instruments, ontology audits, corpus cleanup, fleet
reconciliation, architecture proposals. Per A6, they wait for a metabolic cycle to attach to.

---

## 3. The independence handover (A8)

For Round 2's probe track I hand over: the frozen preregistration, the spec, all artifacts, and
the review record — and I do **not** author the execution or review prompts.

**Proposed author: Harmonia A.** It is not a residue supplier, not the driver, not one of the
two exit reviewers, and it owns the meter's non-gameability doctrine — which makes it the
natural author of the A5 invariant. **Fallback: Aporia** (unconflicted on the probe, though
currently loaded with germline work James has ruled theoretical-for-now).

**What I retain:** the forge track, where my conflict does not bind — the R2–R5 typed-transformer
debt under the opened Apollo gate, the ablation card, and my own doc hygiene. And I remain
available as a reviewer of *other* seats' work, which is a different channel from authoring
their instructions.

**Resulting chain for Tier B:** supplier = Hephaestus/Techne · designer = Ergon (prereg) ·
prompt author = Harmonia A · executor = Ergon · grader = the preregistered classes ·
recomputation = Aporia · adjudicator = Charon. Five distinct seats between the residue and the
verdict.

---

## 4. The milestone Round 3 would need

Stated now so it cannot be softened later. From the review, adopted:

> **Failure N causes an automatically derived intervention in descendant N+1; N+1 measurably
> improves under an independent verifier; and the improvement survives later replay.**

No human translating the failure into the fix. No new architecture. No 100M records. Until
that closes, the honest description of this program is the one in A11.

---

*Filed by Hephaestus, M3, 2026-08-20. Three of the review's corrections land on me — the
heredity naming, the pre-emptive redesign, and the design-channel conflict — and all three are
accepted without qualification. The fourth, that the program is productively over-instrumented
but metabolically starved, is the sentence I would put at the top of Round 2.*
