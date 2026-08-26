# Deliverable A — Archaeology of the shelved Symbolic Library

Charter: `aporia/CHARTER_MUTABLE_LANGUAGE_OF_THOUGHT_2026-08-26.md`.
**Verdict up front: the old library is a specification, not a mechanism, and its promotion rule is
incompatible with the charter's. Two of my four charter-recorded leads were false.**

---

## 1. Where it actually is

**`aporia/doctrine/substrate_vocabulary/`, v0.1.0, 956 lines of markdown across 5 files.**

    Layer 1  primitives.md         NOUNS — 22 typed object/certificate classes
    Layer 2  attacks.md            VERBS — paradigms P00-P33, each with consumes/produces
    Layer 3  patterns.md           failure modes
    Layer 4  anti_anchors.md       do-nots (12 entries)
    Layer 5  composition_rules.md  grammar — 2 confirmed, 5 candidate

Referenced from `docs/NORTH_STAR.md` and
`aporia/docs/frontier_review_substrate_shaped_pipeline_2026-05-11.md`.

**Two of the four leads I recorded in the charter are FALSE — name collisions from a filename
search.** `prometheus_math/symbolic.py` is a sympy CAS facade. `prometheus_math/symbolic_tensor_decomp.py`
is canonical CP/Tucker/TT numerics over tensorly. Neither has any connection to the library. I
flagged in the charter that a filename-only search could be confidently incomplete; it was
confidently *wrong* instead, which is worse and is recorded as such.

**One of them is nonetheless a real reusable artifact, for a different reason:**
`symbolic_tensor_decomp.py` already implements the **Tensor-Train (Oseledets) construction** the
charter wants to test in §10–11. The TT machinery exists and does not need building.

## 2. Answers to the charter's archaeology questions

**What was it intended to do?** Be the action space and training corpus for **Ergon Learner
v2.0** — "the Learner's action vocabulary is exactly Layer 1 + Layer 2. A Learner action is
'produce primitive X via attack Y.' Layers 3–5 act as constraint structure."

**Were the symbols executable?** **No, and the artifact says so in its own words.** Layer 1
entries are *"Techne registration requests"* — Techne would build the dataclass, validation
hooks, serialization. The library is the request, not the code. Non-goals: *"Not the LLM training
step itself. This is a specification."*

**How were symbols created?** Extracted from deep-research report batches (T#1, T#13, T#19, …).

**How were they retrieved?** No retrieval mechanism. Markdown catalogue with back-links.

**Could abstractions become operands?** **Specified, yes — this is the closest thing to the
charter's reification.** Layer 5 Rule 1 outputs *"a composite distributional border-rank
statement — substrate-canonical handle that downstream attacks treat as a **single load-bearing
artifact** rather than two independent witnesses."* That is macro-becomes-operand. It was never
executed.

**What was the tensor decomposition for?** Nothing to do with this library. Separate numerics.

**Was cross-domain transfer ever measured?** **No.** No transfer experiment, no controls, no
solver. Not one measurement of any kind appears in the directory.

**What failed / what was abandoned / what was never tested?** Nothing failed, because nothing
ran. The README states plainly: **"The Learner is not yet built. This vocabulary is the
prerequisite specification."** It was never tested; it was written and shelved when its only
consumer never materialised.

## 3. The two incompatibilities with the charter

**(a) PROMOTION CRITERION — head-on conflict, and this is the important one.**

The old rule: *"Composition rules with two or more independent literature confirmations in a
single batch are promoted from speculation to load-bearing substrate architecture."* Both v0.1.0
confirmed compositions were promoted on **literature co-occurrence in a deep-research batch**.

The charter requires promotion by `f(compression, predictive value, transfer, necessity,
robustness)` with **interventional necessity mandatory** — removing or corrupting `C` must destroy
the measured advantage — and explicitly forbids promotion because a source finds a motif
meaningful.

**Two citations from a research batch is nearer to the forbidden criterion than to the required
one.** Every promoted element of the old library was promoted by a rule the charter rejects.
Nothing in it is grandfathered.

**(b) LAYER 1 IS NOUNS, THE CHARTER NEEDS RELATIONS.**

`TensorNetwork`, `BorderRankWitness`, `MomentPolytope`, `KroneckerInvariant` — object and
certificate *types*. The charter's primitives are typed relations: `same`, `before`, `contains`,
`blocks`, `preserves`, `splits`.

**This repo has already measured that difference and the measurement is unambiguous:**
`feedback_verbs_over_nouns` (operations are deeper bridges than object labels) and
`project_verbs_must_be_native` — **7 generic operators found 0 relations across 295M triples; 1
native verb found 4,476 on the same data.**

Layer 2 *is* verbs, which is the salvageable half — but they are domain paradigms
(`P29_BorderApolarity`), not composable relational atoms, and they are 187 lines of prose with
citations.

## 4. What is reusable

- **The 5-layer shape.** primitive / verb / failure-mode / anti-anchor / grammar is a good
  decomposition and maps onto the charter's primitive → motif → macro plus failure boundaries.
  Take the shape; take none of the contents.
- **Layer 5's reification idea** — a composition becoming a single downstream handle. Exactly the
  charter's macro-as-operand, and worth implementing since it never was.
- **Layer 4 anti-anchors.** The idea of storing *do-nots* as first-class entries is close to the
  charter's abstraction-boundary learning, though the existing 12 are literature corrections
  rather than measured boundaries.
- **`symbolic_tensor_decomp.py`** for the TT arm.

**Not reusable:** all 22 Layer-1 primitives, both confirmed composition rules, the promotion
criterion, and the Learner action-space framing.

## 5. OLD CLAIM ≠ NEW INTERPRETATION

Per the loop directive, keeping these separate rather than retrofitting:

> **OLD CLAIM:** a curated vocabulary of mathematical object types and attack paradigms,
> literature-validated, will serve as a learned action space for a reasoning Learner.
>
> **NEW INTERPRETATION:** typed relational atoms compose in real time into motifs; motifs that
> demonstrably change downstream computation are promoted to executable macros; macros transport
> imperfectly across domains and their failures define their boundaries.

**These are not the same hypothesis and the artifacts do not support continuity.** The old one is
about *cataloguing a domain*; the new one is about *manufacturing vocabulary from experience*.
The old library could be entirely correct and contribute nothing to the new question.

## 6. The finding that matters most for the loop

The old library is the **exact failure mode the charter §12 warns about, already run to
completion**: a beautiful, careful, well-cited specification with a versioning protocol, an
amendment window, and **no consumer that ever existed**. It is not a cautionary analogy — it is
the same repo, the same author role, and 956 lines of evidence that this failure is reachable
from here.

The operational consequence: **the first thing built must be the solver that consumes the
vocabulary, not the vocabulary.** If a primitive cannot be consumed by something that runs on the
day it is written, it should not be written.

## 7. What this changes about the next deliverables

- **B (ladder reconciliation)** — the old Layer 1+2 action-space model is a *different* ladder
  proposal (produce-primitive-X-via-attack-Y) and should be reconciled explicitly rather than
  ignored.
- **C (minimal formalism)** — inherits the 5-layer shape, discards the contents, and must make
  promotion interventional from the first line.
- **D (storage comparison)** — the TT arm has a working implementation already; the baselines it
  must beat still need building.
- **E/F (experiments)** — unaffected; the archaeology supplies no reusable task population, so the
  tiny world is built from scratch as §18 requires.
