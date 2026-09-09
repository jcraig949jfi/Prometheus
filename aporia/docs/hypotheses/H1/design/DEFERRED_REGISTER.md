# H1 — refinements to revisit after alpha

**Operator-supplied, verbatim below the rule. Recorded 2026-09-09 by Astra.**
Baseline: Prometheus H0–H5 design packet v0.1, H1 (`cegis_boolean_v1`).

**This document is the current authority on H1 alpha scope and it overrides the
four-arm reading in `ARMS.md`.** Astra's decision is to keep the alpha at THREE
arms and defer the fourth to beta as H1-R01.

---

**Decision:** keep the H1 alpha scope and its three arms unchanged. Record the
proposals below for later phases. These entries are deferred design work, not
new alpha acceptance criteria or evidence that H1 works. This note records no
experiment result and does not amend the baseline execution contract.

Alpha closes when a real source failure-input pack passes through SFE/Vivarium
into the bounded Boolean CEGIS kind, all three arms execute, and the existing
oracle-parity, source-label, budget-exhaustion and resource-accounting checks
pass. A positive transfer effect is not an alpha exit requirement. Correctness,
blinding or accounting defects are fixed in alpha; an inconclusive or saturated
eight-case experiment does not trigger speculative redesign.

## Deferred refinement register

**H1-R01 / beta.** Add an ordinary-source-probe arm: draw probes from the same
relevant source tasks without selecting them for having caused failures. Match
source selection, input count, compatibility, structural properties and
duplicate handling where applicable. Recompute every target label.
*Condition:* after alpha closes, before claiming that a probe's history as a
failure adds value beyond relevant test reuse. Preserve ordinary source probes
when constructing the beta corpus; do not add a new alpha logging dependency.

**H1-R02 / beta.** Add a mechanism analysis with candidate enumeration order
fixed across arms. Measure incorrect candidates rejected before full
verification, full-verification work avoided, and net charged operations.
*Condition:* after alpha traces are available. Reuse their existing information
where sufficient; add only missing measurements to beta. Fixed ordering need not
reduce candidates visited before the first correct program; the possible saving
is verification work.

**H1-R03 / beta.** Calibrate a larger compatible task family on disjoint pilot
tasks, using the existing 4–6 input or bounded bit-vector route. Freeze relevance
features and task splits before confirmation.
*Condition:* if alpha exposes saturation, inadequate search difficulty or an
unusable relevance feature. Expand based on instrument limitations and
predeclared families, not a retrospective search for favorable results.

**H1-R04 / conditional SMT extension.** Add backend-specific checks: paired
solver seeds, input/constraint-order perturbations, structurally matched valid
inputs, and formula/decision/conflict telemetry. Define exactly what each control
preserves.
*Condition:* only if an SMT backend is introduced. An "isomorphic noise" witness
is not assumed to preserve solver behavior or destroy useful information; a
proposed control must establish its bounded meaning before use. No SMT-specific
gate is imposed on the VM experiment.

**H1-R05 / 1.0 protocol review.** Apply the existing confirmation requirements to
the final arm set: solve fraction at matched total resource caps; source
acquisition, retrieval and labeling costs; paired independent replications;
unsolved cases retained; a frozen meaningful-effect threshold and uncertainty
analysis.
*Condition:* before the first confirmation run. These are existing requirements
to recheck after beta changes, not a new measurement framework. Repeated runs of
one task do not become additional independent tasks. Failure to detect
significance does not establish equivalence.

**H1-R06 / 1.1 or later extension.** Test agent-mediated abstraction or candidate
guidance separately from raw input transport. Compare the same fixed model/prompt
with no history, matched control history and relevant failure history; charge
inference and preparation. Any imported hard constraint requires
target-specification verification. Unproved abstractions remain proposal biases.
*Condition:* after the raw-input experiment reaches an interpretable result,
including a null. Reuse the admitted producer/kind boundary and frozen artifacts;
do not silently add live external calls to the blind executor. This extension
tests a different intervention and cannot retrospectively establish the original
H1 claim.

## Interpretation to preserve

- Relevant failures beating fresh probes and random compatible failures supports
  the tested retrieval policy's practical value within the declared family and
  resource caps.
- Also beating matched ordinary probes from the same relevant source tasks
  strengthens the case for failure-specific value.
- Tying ordinary source probes can still support useful test reuse; it does not
  establish that failure origin supplies additional value.
- Solver telemetry supports diagnosis. A reduction in conflicts alone does not
  prove a semantic mechanism, and high variance alone does not establish a null.

At alpha closeout, review this register once against the actual receipts. Promote
only proposals needed for the next experiment, attach them to its versioned
protocol, and leave the rest deferred. A positive alpha signal is not required to
begin a justified beta experiment. Do not reopen alpha merely because another
literature review proposes a stronger control.

## Provenance

This register records the operator/designer discussion of H1 on 2026-09-09. It is
a companion to the existing design packet, not a replacement for it. The
adversarial review assessed a reconstructed hypothesis; future reviews should
receive the exact versioned protocol.

- Aporia 201: evidence audit
- Aporia 202: adversarial review

The reports motivate checks; their agreement, disagreement or severity labels do
not constitute an H1 experimental result.
