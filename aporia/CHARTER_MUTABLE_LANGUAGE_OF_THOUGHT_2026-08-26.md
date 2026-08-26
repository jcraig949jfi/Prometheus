# APORIA CHARTER — Resurrect the Symbolic Library as a Mutable Language of Thought

**Issued by James, 2026-08-26. Duration: ~one week. Status: research directive, NOT an
architectural commitment.** This supersedes the IQ arc as the primary line. It is written to
survive context resets: a fresh Aporia instance reads this and knows what it is doing.

---

## 0. The one-line version

> Synthetic reasoning may require a **mutable language of thought**: primitive relational symbols
> composed in real time, useful compositions promoted into executable abstractions, those
> abstractions transported imperfectly across domains, and successful ones becoming new operands.

    experience → primitive relations → temporary compositions → reusable abstractions
               → new reasoning vocabulary

**A useful abstraction is not something the system can retrieve or describe. It must change
subsequent computation.** Do not assume the hypothesis is true. Try to break it.

## 1. Why this is not a restart of an old idea

The directive arrives at a moment when the previous arc had **measured itself into a cycle**, and
this is the reason the charter is worth taking seriously rather than treating as a pivot.

The IQ arc established, with proof or exhaustive enumeration:

- `E(C_abstain, T) = 0.8333` exactly — the ceiling is closed.
- ΔS = 0.00%: all 20 unreached tasks lie **outside the operator closure**. No macro, guard or
  search over existing operators reaches any of them (Lexis `fcdc91af`, confirmed independently
  by my SELECTOR pre-flight: 0 of 27 frozen candidates move ΔE for a capability-related reason).
- ΔE measures **extension of the ISA**, not acquisition of an abstraction. The one port gains
  +5/120 on its design route and fires **0/200** across construction routes.

Which produced this dead end:

    SELECTOR needs headroom → headroom needs minted primitives → minting needs a measurable
    target → the only clean target is degenerate → SELECTOR cannot run

**This charter breaks that cycle by construction**, because §18 mandates a *new, deliberately
tiny task world* built to expose abstraction transport — which is exactly the "new task
population with genuine unreached structure and a non-degenerate answer distribution" the cycle
required and the existing battery cannot supply. That is a real reason to proceed, not a
rationalisation, and it should be checked rather than assumed: **if the toy world turns out to
have the same degeneracy as canary `vacuous_truth`, the cycle is not broken and the charter
inherits the block.**

## 2. The central distinction — do not blur it

    solution learning     P → a, or a representation making nearby P's produce useful actions
    abstraction learning  P₁…Pₙ → C, then C + P_novel → useful reasoning

where `P_novel` is **deliberately separated from the distribution that produced C**. Only the
second is the target. The first is not evidence of the second.

## 3. The hierarchy under test

    primitive   typed relational operation with operational semantics where feasible
                (same, different, contains, before, preserves, blocks, splits, merges,
                 increases, decreases, boundary, cycle — ILLUSTRATIVE, not canonical;
                 the English label is not the representation)
    motif       ephemeral composition, M = r₃ ∘ r₇ ∘ r₁₁. Working memory. Most must die.
    macro       a composition that EARNED persistence: C = (S, E, T, I, F, V)
                S symbolic decomposition · E distributed representation · T allowable
                transformations · I invariants · F known failure conditions · V validation history

`C = (S,E,T,I,F,V)` is **a research hypothesis, not a requirement. Attack it.**

## 4. Executability is the property that matters

Compression: `S₀ → S₁ → … → S₅₀` becomes `S₀ —C→ S₅₀`.
Representational widening: `𝓢 → 𝓢 + C` makes expressible what was not.

**Distinguish these experimentally.** The second is far stronger evidence, and the IQ arc has the
instrument for it: where near-exhaustive enumeration makes `max Perf over 𝓛 = x` defensible,
showing `max Perf over 𝓛+C > x` is a clean representational-widening claim.

## 5. Analogy as lossy transport, with a ledger

    P —φ→ C      φ = (preserved relations, broken relations, unknown relations)

Analogy need not be an isomorphism. Humans reason effectively with knowingly wrong analogies.
The research question is whether a synthetic reasoner can exploit **partially structure-preserving
transport without confusing it with proof.**

## 6. The ELI5 / surrogate operator

    P —ELI5→ P'    with distortion ledger D(P,P') = {preserved, discarded, approximated}
    P → P' → H' → H → test(H, P)

**The surrogate may generate hypotheses. It may never certify the original claim.** Certification
happens only after transport back and independent checking. This is what makes reasoning with
useful lies epistemically safe.

## 7. Storage: hybrid, with a strict division of labour

    distributed retrieval → symbolic alignment → transport → falsification

**Never** `embedding similarity → truth`. `vᵢ ≠ Cᵢ`. Tensors answer *"what might be relevant?"*;
symbols answer *"what does this license me to do?"* — which is the existing Prometheus principle
that stochastic machinery proposes and deterministic machinery adjudicates.

Tensor trains are **a hypothesis to kill, not a commitment**: `T(i₁..iₙ) = G₁(i₁)…Gₙ(iₙ)`.
Compare against sparse structures, graphs, plain embeddings, tries, FAISS-style retrieval and
explicit symbolic indexing. **If a simpler baseline wins, kill the tensor-train hypothesis.**
Target is functionality, not elegance.

## 8. Failure becomes abstraction-boundary data

Store `(P, C, φ, A, F)` rather than `(P, A, FAIL)`. Over repeated use this yields a **learned
boundary on an abstraction** — `C` valid when `r₂ ∧ r₅ ∧ r₉`, fails when `r₁₄`. This is a
concrete candidate for failure metabolization and is to be **tested as such**, not asserted.

## 9. Promotion must be earned

`utility(C) = f(compression, predictive value, transfer, necessity, robustness)`.
**Interventional necessity is mandatory: removing or corrupting C must destroy the measured
advantage.** Do not promote because an LLM finds a motif meaningful.

## 10. The key experiment — abstraction transplantation

Solver A experiences `D₁`, produces `C`. **Freeze C.** Give it to fresh solver B which never saw
`D₁`. Evaluate on `D₂`, superficially alien but structurally related.

    Perf(D₂ | C)  vs  Perf(D₂ | ∅)

Controls: `C_correct`, `C_scrambled`, `C_label-only`, `C_verbal`, `C_embedding-only`,
`C_wrong-boundary`.

**Leakage defences are not optional** and this arc has already been burned by exactly this class:
no shared terminology, variable names, source-domain hints in prompts, preserved surface topology,
shared templates, or abstraction names that leak behaviour. Rename, permute and re-encode
primitives while preserving relational structure. The target is **structural transfer**, not cue
following.

## 11. The LLM comparison — measure the distinction, don't assume it

    A LLM alone · B LLM + textual description of C · C LLM + retrieved examples
    D LLM + embedding retrieval · E LLM + executable C · F non-LLM symbolic search + executable C

**`E > A` is not the result. Why is the result.** If textual prompting gives the entire gain, the
symbolic architecture has not earned its complexity.

## 12. THE FAILURE MODE THIS CHARTER IS MOST LIKELY TO PRODUCE

§18 of the directive names it, and this repo has the receipts: *schemas, databases, DSLs,
thousands of symbols, embeddings, tensor machinery, beautiful documentation, millions of records,
no demonstrated consumer.* `LOOP_APORIA.md` records 30 paradigm trees with no ingestion path from
exactly this pattern, and "built useful infrastructure" is already disqualified as a continuation
reason without a named waiting consumer.

**Binding constraints, therefore:**

- **10–30 primitives. Not more.**
- Start with a deliberately tiny world; several source families, several structurally related but
  superficially alien target families.
- **The first objective is ONE defensible observation of** `experience → C → cross-domain
  computational advantage`. Not scale.
- **If it cannot be demonstrated in a toy environment built to expose it, do not scale it.**

## 13. First deliverable — a research assessment, not an implementation plan

Seven parts, per the directive:

**A. Archaeology.** Locate and summarise the shelved Symbolic Library work: intent, architecture,
representations, experiments actually performed, claims supported, failures, reason shelved,
reusable artifacts, and which assumptions are **incompatible** with this hypothesis.
*Leads already located:* `prometheus_math/symbolic.py`, `prometheus_math/symbolic_tensor_decomp.py`,
`aporia/docs/prometheus_pivot_research_batch1/report_05_action_space_typed_symbolic.md`,
`archive/vesta/vesta/registry/models/` (large reasoning-model catalogue, includes neuro-symbolic
entries). Start there; do not assume that is the whole of it.

**B. Ladder reconciliation.** Map the current Reasoning Ladder against the abstraction-operation
model — matches, contradictions, missing capabilities, redundant tiers, measurable transitions.
The provisional tiers R0–R9+ (detect · compose · manipulate · recur · compress · transport ·
counterfactual · boundary · manufacture · re-represent) are **to be tested, not adopted.** The
candidate major transition is **search within a language → search over representations**;
determine where, if anywhere, it belongs.

**C. Minimal formalism** sufficient to test primitive → motif → macro → transport.

**D. Storage/search comparison** — symbolic structures, sparse, embeddings, tensors, tensor
trains. **For each: what it is supposed to accomplish, and what experiment could kill it.**

**E. Three minimal experiments. No more than three.** Each with hypothesis, IV, DV, controls,
leakage defences, predicted positive, interpretable negative, kill criterion. **At least one must
be abstraction transplantation.**

**F. One adversarial experiment** designed to show the apparent cross-domain abstraction is
actually surface leakage, retrieval, or ordinary LLM generalisation.

**G. Recommendation — exactly one:** `REVIVE` · `PROBE ONLY` · `KILL`.

## 14. Success condition

    experience → recurring relational structure → compression → executable abstraction
    → cross-domain transport → measurable reasoning advantage
    → failure-defined applicability boundary → new reasoning vocabulary

**Anything weaker must be labelled accurately.** A database containing abstractions is not
abstraction. An embedding cluster is not abstraction. An LLM naming a pattern is not abstraction.
Retrieving an analogous example is not necessarily abstraction. Improved same-distribution
performance is not cross-domain transfer. A human-written macro is not machine abstraction
formation. A nested data structure is not hierarchical reasoning. A tensor decomposition is not a
language of thought. **The claimed phenomenon must survive intervention.**

## 15. What happens to the IQ arc

**Not discarded — parked, with its state intact** in `aporia/iq/` and summarised in
`ARC_SUMMARY_2026-08-25.md`. Standing dispositions from the external review remain in force:
ADVANCE the expressivity assay as a **microscope**, PARK any **compass** claim, and SELECTOR stays
withdrawn as mis-specified.

**Stays live** (cheap, hardens everything the charter will build): executable preregistration, and
property/metamorphic tests on instruments rather than example tests on outputs.

**Stays blocked:** ABLATION, pending claim-object provenance.

**Carried forward as method, because the charter will need every one of them:** every control
stated with the input that would make it fail · attainable range computed before any threshold ·
a reading that cannot vary is VACUOUS, not a pass · a null result needs a positive control · a
probe that perturbs what it measures produces a confident wrong number · the null for a
firing-but-wrong rule on a k-candidate task is 1/k, not 0.

**The arc's own hardest lesson applies directly here:** five separate times it produced a
confident reading from a probe that did not measure the thing it named. A charter about
abstraction transport is unusually exposed to that failure, because "the abstraction transferred"
is exactly the kind of claim a mis-aimed probe reports cleanly.
