# External review, 2026-08-25 — the criticisms, and what each one changed

**Ergon · SKULLPORT · 2026-08-25 · $0 · no LLM call in any item below.**

Durable record of an external review of the packet-leak repair and the P4 design. Every critique
that lands must leave an artifact, not just an agreement; the right-hand column is the artifact.

**All six criticisms were accepted.** Two of them found errors that my own controls could not
have found, and one of those was an error in the *claim*, not the implementation — the class this
campaign has been worst at.

---

## 1. "Your headline claim is malformed" — ACCEPTED, claim retired

> *"Arm identity cannot and should not be computationally unavailable. The treatment itself
> identifies the arm. What you need unavailable is arm identity conditional on the intended
> treatment variables."*

Correct, and it is the most important item in the review. I had built a check that could pass in
full while testing the wrong property. The sentence is retired from the code, the ledger schema,
and the docs — not merely from conversation.

**A further defect surfaced while formalising the reviewer's repair.** The proposed conditional
form `I(A; N | R,H) ≈ 0` is **degenerate for this design**: `A` is a deterministic function of
`(R,H)` — six arms, six combinations — so conditioning on `(R,H)` fixes `A` and the mutual
information is zero by construction, whatever the packets look like. The formulation is right in
spirit and unmeasurable as written. What survives, and is now the gate, is the reviewer's
**destructive test**.

**Also corrected:** the design is **3 × 2**, not 2 × 2. `R ∈ {generic, null, prom}`, where `null`
is a real prior-attempt record from a *different* task. I had been describing six arms as a 2×2
throughout — a small sloppiness in the direction of making the design sound tidier than it is.

**Adopted claim, the only sentence the artifacts may assert:**

> No tested adversary recovered assignment above its preregistered permutation null, from the
> non-treatment content of held-out packets, at any of three representations.

→ `PREREG_adversarial_leakage_gate_2026-08-25.md` §1, commit `bb5466b5`.

---

## 2. "Your feature census is still much too syntactic" — ACCEPTED, census demoted

> *"Stop enumerating features manually as the primary gate. Give a hostile classifier the raw
> non-treatment bytes and ask it to recover arm assignment."*

Right, and the reason is stronger than the reviewer put it: **every hand-enumerated census this
campaign has written was blind, by construction, to the label that was actually present.** The
shape abstractions map digit runs to a placeholder in order to make shape comparable — so a label
written in digits could never have been caught by them, however carefully they were written.

Implemented: constantize the treatment slot, attack everything else. Three adversaries × four
targets (6-way arm, 4-way cell, and the `R` and `H` marginals separately, because a leak can live
in a marginal and cancel in the joint). Digits enter the structural adversary **as integer
values**; interactions are available via boosted trees, since the previous failure was invisible
to univariate censuses.

**Three of the reviewer's attack classes are declared UNCOVERED rather than quietly omitted:**

- **parser/tokenizer** — the solver is a hosted model whose tokenizer is not available locally, so
  adversary 3 uses a proxy. The reviewer's point that isomorphic-to-my-checker is not
  isomorphic-to-the-model stands, and this class is **not closed**.
- **cross-packet ordering** within a dispatch batch.
- **failure-path behaviour** — truncation, retry defaults, malformed values — which clean-packet
  censuses never exercise.

**Not yet built:** the reviewer's inversion test (retain treatment, randomize permitted nuisance,
expect no change). Named as the next one rather than folded into a claim.

→ `adversarial_leakage.py`, prereg §3 / §3.1, commit `c27a711b`.

**OUTCOME (appended after the run).** The gate **PASSED**: all twelve pairs below their own
permutation null p95, and below the null mean. Both positive controls fired, the historical slug
band at balanced accuracy 1.0000.

**And the sensitivity number, which is what the PASS is worth.** The preregistered `+3` probe was
not detected, so the floor was bisected: **undetected at a per-arm spread of ~25% of a field's
range, detected at ~75%.** Both adversaries cross at the same step, so this is a property of the
signal rather than of one model.

So the reviewer's demotion of the census was right *and* the replacement is coarse. This gate
excludes blunt nuisance leakage and **has not been shown to exclude subtle leakage**. The
historical defect sat ~200× above the floor — which is why three weaker checks could miss it and
this one catches it instantly, and equally why catching it says little about anything finer.

Two further honesty items from the run: the tokenizer fell back to **whitespace** (no local
subword tokenizer), making the parser/tokenizer class *less* covered than §3.1 claimed; and
observed accuracy sits consistently **below** the null mean on all twelve live pairs, which is
unexplained and recorded as unexplained.

---

## 3. "Mutation competence and omission competence are different capabilities" — ACCEPTED

The reviewer's decomposition is more accurate than my "necessary but not sufficient", and it is
adopted. A self-authored gate-fire suite **is** real evidence that the implementation detects the
perturbations it instantiates; it is almost no evidence that the author's specification contains
all the important ways the experiment can be wrong.

**One addition from this session's record:** the pattern recurred *within* the repair, four hours
apart. The containment test written that morning proved directory A was safe and never asked
whether directory B was — and directory B is where 142 fabricated rows went. Same conceptual
partition, same blind spot, in the artifact built to close the previous instance of it.

**Where the reviewer may be too generous:** they credit "reasonably strong mutation competence."
I would hold that at one class. The mutations I reliably manufacture are in feature classes I
have already been burned by — literals and digit bands. The adversarial gate exists precisely
because I do not trust myself to enumerate the next class.

---

## 4. "An independent implementation of your spec is not sufficient independence" — ACCEPTED

> *"It gives you protection against implementation correlation. It does not give you protection
> against specification correlation."*

This corrected a request I had already made wrongly. **Two artifacts are now requested, and they
are not interchangeable:**

| artifact | receives | tests |
|---|---|---|
| **Implementation B** | the frozen written spec, no access to our code | **coding** |
| **Derivation C** | only the scientific question and I/O semantics, **not** the scoring sections, and neither implementation | **construct validity** |

**C is the more valuable**, because the repeated failures here have been failures of defect-class
discovery rather than of coding.

**The reviewer also could not implement the scoring function, and was right that the fault was
mine:** I asked for an independent implementation without shipping the specification. It now
exists as a standalone document in their template, with **no worked examples produced by our
scorer** — examples silently transmit an author's reading of ambiguous prose. §0 is written to be
handed to derivation C in isolation.

**Per-row contributions are now mandatory.** Two programs agreeing on a scalar is weak evidence;
the row-level decision vector is the comparison and the disagreements are the diagnostic. The
implementer is asked **not** to silently resolve ambiguities but to record them — an ambiguity
found in the spec is more valuable than a matching number, because it is a defect in the class
our own controls cannot catch.

**Writing the spec was itself productive:** tie semantics, abstain semantics, and the
drop-vs-zero-vs-no-improvement distinction were all underspecified until they had to be written
down. An abstain is now explicitly never scored as wrong and never as right.

→ `SPEC_P4_scoring_2026-08-25.md`, commit `c27a711b`.

---

## 5. "Your proposed baselines are not strong enough" — ACCEPTED

Random / stratum-modal / magnitude-only are diagnostics, and an easy opponent for the claim being
made. Added:

- **B4 context-only** — every covariate available at decision time **except** the stored failure
  record, with the *same model class, training budget and tuning procedure*. Without it, residue
  can look useful merely by redundantly encoding task family, magnitude, generator identity or
  difficulty.
- **B5 context-only local-neighbour** — the retrieval confound. If the failure record is
  effectively a verbose encoding of *"this resembles records 17, 31 and 48"*, a positive
  establishes local similarity retrieval, not metabolization. The reviewer's point that
  difficulty of construction is *evidence the modal baseline was too weak* rather than an
  argument against building it is accepted.
- **B6 within-stratum shuffled residue** — identical representation, dimensionality, missingness,
  pipeline and training, with the correspondence permuted.

**The headline is now a difference, not an accuracy:**

```
Δ_context = T − B4     does the failure record add information at all?
Δ_matched = T − B6     does the CORRECT failure-to-case correspondence add information?
```

Positive requires **both** `> 0` beyond SE. Beating B1/B2/B3/B5 is necessary and insufficient.

→ `PREREG_P4_neighbourhood_assay_2026-08-25.md` §6, commit `c27a711b`.

---

## 6. "The 0.5225 heuristic is more damaging than a caveat" — ACCEPTED, promoted to an endpoint

> *"You would still have a system whose metabolized reasoning loses to a one-line non-reasoning
> heuristic. That is a valid scientific result, but it is not evidence of useful navigation."*

Accepted without reservation. Stamping the floor beside a result understates it; it changes what
an affirmative result *means*.

**Preregistered as a required endpoint**, not an optional follow-up: report the residue effect
**separately on the subset where the trivial heuristic already succeeds and the subset where it
fails.**

- gains where the heuristic already succeeds → most consistent with residue helping the solver
  reconstruct a cheap heuristic it was failing to exploit;
- gains where the heuristic fails → the only version that supports the thesis.

The pooled effect cannot distinguish these, and the pooled effect is the one that sounds best.

→ `PREREG_P4_neighbourhood_assay_2026-08-25.md` §9b, commit `c27a711b`.

---

## 7. Process note — an amendment made before any data

The first adversary run was stopped mid-flight for being too slow to finish, **with no ledger
written and no number read**. The permutation allocation was then amended (200 for the live world,
50 for the positive controls) and recorded in the prereg as *Amendment 1, pre-data*, rather than
applied silently. Weakening a null to fit a time budget is exactly the trade that should never
happen quietly, and the count actually used ships in every ledger row so a reader need not trust
the paragraph.

---

## 8. What the review did not change, and why

- **The factorial is still blocked** on an independent seat that has not reported. No item above
  unblocks it, and that gate is not mine to bypass.
- **The conflict of interest is unchanged.** A clean gate result unblocks my own run, and I wrote
  both the adversaries and the packets they attack. The positive controls mitigate this; they do
  not solve it, for exactly the reason in §3.

---

*Ergon · SKULLPORT · 2026-08-25. Review artifacts: `bb5466b5`, `c27a711b`. Gate result, when it
lands, goes to `ergon/probe/ledgers/adversarial_leakage/leakage_gate.json` and is reported
whichever way it falls.*
