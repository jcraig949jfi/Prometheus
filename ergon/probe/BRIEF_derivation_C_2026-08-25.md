// BRIEF FOR DERIVATION C — hand this file over ALONE

**Do not read** `SPEC_P4_scoring_2026-08-25.md`, `PREREG_P4_neighbourhood_assay_2026-08-25.md`,
or anything under `ergon/probe/`. This brief is deliberately self-contained, and its value
depends entirely on your not having seen how we resolved these questions.

**What you are asked to produce:** the measurement you think *should* exist for the question
below. Not a review of ours — a derivation of yours. We will compare afterwards, and **a
disagreement is a more valuable result than a match.**

**Why this is being asked.** Our failures have not mainly been coding failures. They have been
failures at the earlier joints: question → population → sample → code path → number → prose. An
independent implementation of *our* specification would test whether two people can code the
same spec. It would not test whether the spec measures the right thing. Two flawless
implementations of the wrong estimand give a reproducible mistake, and reproducible mistakes are
the ones we keep making.

An earlier draft of this brief was rejected for containing our own terminology — words like
"margin", "neighbourhood", "improvement", "top-1" quietly carry our answer. They have been
removed. If you find residual vocabulary below that seems to presuppose a design, treat that as
a defect in the brief and say so.

---

## 1. The situation

An automated system generates candidate mathematical statements and checks them. Most are
**rejected** — the statement does not hold. Each rejection is recorded.

Each statement is produced by a small number of explicit choices the generator made. Every choice
is drawn from a finite, enumerable set that we can list exactly. Given any combination of
choices, we can determine the resulting statement's truth **exactly and deterministically**, by
lookup in fixed reference tables. There is no estimation and no model anywhere in this loop.

A recorded rejection also stores some description of the failure. That description is what is at
issue.

## 2. The scientific claim under test

> The stored description of a past failure carries information that helps select a better next
> action — *over and above* everything else knowable at the moment of choosing.

Informally: does recording *why* something failed give us something we would not have had anyway?

The system's designers believe it does. Prior work in this project has repeatedly found that
apparent effects of this kind dissolve into ordinary covariates once suitable comparisons are
built, so the burden is on the positive.

## 3. The decision this measurement must support

Exactly one of four conclusions, and the measurement's job is to distinguish them:

1. Better nearby choices generally exist, and the stored failure description helps identify
   which — **the recording is doing useful work**.
2. Better nearby choices generally exist, but the stored description does not help identify them
   — **the recording is inadequate**.
3. Better nearby choices generally do **not** exist — **the generation process is the problem**,
   and improving the records cannot help.
4. Neither — **both layers need replacing**.

## 4. Observables available to you

- The full record of each rejection, including: which generator produced it, the exact choices
  made, the resulting statement, its recorded failure description, and assorted metadata
  (timestamps, identifiers, some numeric annotations).
- The reference tables, complete and fixed.
- The ability to evaluate any admissible combination of choices exactly.
- Roughly 10⁸ rejected records, very unevenly distributed across ~12 generators: the largest
  contributes ~10⁶ in a sample, the smallest a few hundred.
- Records from one generator share a template and are strongly non-independent.
- Some records reference other records.

## 5. Constraints

- **No language model may appear anywhere** in the measurement, including as a judge or a
  feature extractor.
- Deterministic given inputs and a seed.
- Evaluating a combination of choices is cheap, but the number of combinations reachable from one
  record can be in the thousands, and the corpus is large; some bounding will be necessary.
- Reference values are sometimes **absent** for a given object.
- Different generators assert **different kinds** of relationship, on quantities of wildly
  different magnitude and units.

## 6. What we would like you to specify

Please write down, in whatever form is natural:

1. **Estimand** — what quantity, precisely, answers §2? State it before deciding how to compute
   it.
2. **Unit of analysis** — what is the independent unit, and what follows for §5's
   non-independence?
3. **Scoring rule** — how a single record's outcome becomes a number, and what "better" means
   given §5's heterogeneity.
4. **Aggregation** — how record-level numbers become the estimand, and how the skew in §4 is
   handled.
5. **Uncertainty procedure** — including the exact decision function: what result counts as
   supporting the claim in §2, fixed in advance.
6. **Invalid, abstain and tie semantics** — what happens when a value is absent, a comparison is
   undefined, several options are equally good, or a method declines to answer.
7. **What result would NOT support the claim** — specifically, what comparison could show an
   apparent positive to be something less interesting. We regard this as the most important
   item, and the one our own designs have historically been weakest on.

## 7. Things worth knowing that are not hints

- Whether a statement holds is **binary**, but most rejected records stay rejected under most
  nearby choices. Any design resting only on the binary outcome will find little to measure.
- One quantity here can be many orders of magnitude larger than another it is compared with.
- A one-line procedure that does no reasoning at all outperforms the system on a related task
  (0.5225 vs 0.4900). Please treat "beats nothing in particular" as an inadequate bar.

## 8. What we will do with your answer

Compare it against our frozen specification, item by item. Every difference is triaged as: our
defect, your defect, or a genuine ambiguity in the question. **We expect the third category to be
the largest and we regard it as the most valuable output.** Where you found the brief
underspecified, that underspecification is itself a finding: it is a defect in the class our own
controls cannot catch, because our controls are built from the same understanding that wrote the
brief.

---

*Prometheus / Ergon · 2026-08-25 · hand this file over alone.*
