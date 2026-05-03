# RESIDUAL Primitive Specification
## Architectural extension of the Σ-kernel for spectral falsification and residual-driven refinement

**Status:** Specification. Not yet implemented. Targets kernel v0.2.
**Date:** 2026-05-02
**Origin:** Synthesis of five-frontier-model adversarial review (ChatGPT, Deepseek, Claude/separate-session, Gemini, Grok) on the residual-signal principle articulated by James. All five reviewers independently proposed essentially this extension; the spec consolidates the convergent shape.
**Companions:**
- [`residual_signal.md`](residual_signal.md) — the foundational principle
- [`sigma_kernel.md`](sigma_kernel.md) — the v0.1 kernel this extends
- [`bottled_serendipity.md`](bottled_serendipity.md) — the explorer thesis the spec serves
- [`/pivot/feedback_binary_thinking_2026-05-02.md`](../../../pivot/feedback_binary_thinking_2026-05-02.md) — verbatim reviews
- [`/pivot/meta_analysis_binary_thinking_2026-05-02.md`](../../../pivot/meta_analysis_binary_thinking_2026-05-02.md) — synthesis and triage

---

## Motivation

The v0.1 kernel's FALSIFY primitive returns one of three boolean-equivalent verdicts: CLEAR, WARN, BLOCK. PROMOTE either fires (on non-BLOCK verdict) or doesn't. This architecture is correct for binary falsification but discards the structure of *how* a claim fails — the residual.

Five frontier models, reviewing the residual-signal principle, converged on the same architectural fix: **make the verdict spectral, make residuals first-class typed objects, link residuals to refined claims with provenance, and provide explicit termination rules so residual-chasing doesn't become indefinite rescue.**

This document specifies the extension. It does not modify v0.1's seven primitives — it adds primitives and extends FALSIFY's semantics. The kernel ships unchanged at v0.1. The extensions are v0.2 work and are conditional on demonstration that the principle pays off in practice (a pilot showing residual-driven refinement produces survivors at higher rate than uniform proposal).

## What changes

### v0.1 kernel (unchanged):
```
RESOLVE(name, version) → Symbol
CLAIM(target, hypothesis, evidence, kill_path, tier) → Claim
FALSIFY(claim, seed) → VerdictResult { CLEAR | WARN | BLOCK }
GATE(verdict) → flow
PROMOTE(claim, capability) → Symbol
ERRATA(prior_name, prior_version, corrected_def, fault, cap) → Symbol
TRACE(symbol) → ProvenanceGraph
```

### v0.2 additions:
```
FALSIFY(claim, seed) → SpectralVerdictResult {
    verdict: CLEAR | WARN | BLOCK,           # v0.1 semantics preserved
    score: float,                            # quantitative metric (e.g., kill rate)
    residual: Residual | None,               # structured residual object if non-trivial
    failure_signature: FailureSignature,     # how the claim broke, not just that it broke
    test_config: TestConfig,                 # full reproduction data
}

RESIDUAL(parent_claim, test, subset, metric, signature) → Residual
    # Typed record of an incomplete kill. Content-addressed.
    # parent_claim: hash of the CLAIM that produced this residual
    # test: hash of the kill-test that emitted it
    # subset: content-addressed sub-population that survived (e.g., the 0.87%)
    # metric: structured score (magnitude, parameter location, covariance)
    # signature: pattern of how the claim broke

REFINE(claim, residual, hypothesis) → Claim
    # Mint a new CLAIM from a residual, preserving provenance.
    # The new claim must point back to (claim, residual) via TRACE.
    # The hypothesis is typically a refinement of the original aimed at
    # explaining only the residual subspace.

META_CLAIM(target_battery_test, observed_metric, predicted_metric, evidence) → Claim
    # A CLAIM about the battery's own behavior on calibration set.
    # If META_CLAIM survives FALSIFY, it's evidence that the battery itself
    # has a defect — triggers Techne to refine or replace the test.

CLUSTER_RESIDUALS(residuals, similarity_metric) → ResidualCluster
    # Aggregate residuals across multiple claims by structural similarity.
    # Output is a typed cluster object that may itself become a CLAIM
    # ("these N claims share residual signature X — what does X represent?").
```

### Augmented v0.1 primitive:

`TRACE(symbol)` is extended to walk RESIDUAL and REFINE edges in addition to def_hash dependencies. A symbol promoted via REFINE chains can be traced back through every parent claim and every residual that drove the refinement.

## The Residual object — fields and invariants

```
class Residual:
    # Content-addressed identity
    hash: str                          # sha256 of canonical serialization

    # Provenance
    parent_claim: ClaimHash            # which CLAIM produced this residual
    parent_test: TestHash              # which kill-test emitted it
    techne_tool_version: str           # which Techne tool, at which version

    # Quantitative content
    metric: dict                       # structured score
        magnitude: float               # e.g., 0.0087 (the 0.87%)
        domain_slice: DomainSlice      # where in parameter space
        covariance: dict               # correlations with other variables
        confidence_interval: tuple     # statistical bounds on the metric

    # The actual surviving subset
    surviving_subset: SubsetHash       # content-addressed pointer to the data

    # The shape of failure
    failure_signature: FailureSignature
        type: enum                     # uniform_noise | structured | clustered | drifting
        descriptor: dict               # type-specific structural characterization
        confidence: float              # how confident the type label is

    # Lifecycle metadata
    created_at: timestamp
    refinements_attempted: list[ClaimHash]  # claims minted via REFINE from this residual
    instrument_meta_claims: list[ClaimHash] # META_CLAIMs against the battery for this residual
    status: enum                       # OPEN | INVESTIGATED | EXHAUSTED | PROMOTED_AS_REAL
```

### Invariants

1. **Append-only.** A Residual once minted is immutable. Status updates and refinement-attempt links are append-only on a separate index, not mutations to the Residual itself.
2. **Content-addressed.** Two Residuals with identical fields hash to the same value. Re-running the same FALSIFY produces the same Residual hash.
3. **Provenance-complete.** Every Residual must point to a parent_claim and a parent_test that exist in the substrate. Orphan Residuals are rejected at storage layer (foreign-key analog).
4. **Surviving subset is itself substrate.** The `surviving_subset` is content-addressed; future claims can reference it directly without re-deriving.

## The REFINE operation

```
REFINE(claim_hash: str, residual_hash: str, refined_hypothesis: str) → Claim
```

Mints a new CLAIM that:
- Points to the parent claim and residual via TRACE.
- Has a hypothesis that is a refinement of the parent's hypothesis, typically restricted to the residual's domain slice.
- Inherits the parent's tier minus one (refinements start at lower tier than their parents to discourage tier-hopping via REFINE chains).
- Is testable via the same battery as the parent, or a Techne-forged extension specific to the residual's failure signature.

A REFINEd claim can itself produce a residual when falsified, which can be REFINEd again. This is the **refinement chain**. Termination rules apply (next section).

## Termination rules (the Claude discipline)

Without explicit termination rules, residual-chasing becomes indefinite rescue. The architecture must mechanically prevent this. Five rules, all enforced at the kernel layer:

### Rule 1: Magnitude reduction across cycles
A REFINE chain must show **monotonic non-increase** in residual magnitude across cycles, with at least one strict decrease in the first three cycles. A chain where the residual magnitude oscillates or increases is auto-terminated by the kernel; the chain's terminal claim is promoted as `PATTERN_RESIDUAL_RESCUE_FAILURE` (a typed kill-pattern, substrate-grade) and no further REFINE is allowed against any residual in that chain.

### Rule 2: Cross-modality concordance
A residual that survives REFINE for more than 3 cycles must demonstrate cross-modality concordance: the same structural signature must appear in independent implementations (e.g., PARI/GP and SAT-encoded check, or numerical and symbolic, or two different Techne tools). If cross-modality fails, the chain terminates with `PATTERN_SINGLE_MODALITY_RESIDUAL` — likely instrument artifact.

### Rule 3: Maximum depth
REFINE chains have a hard depth limit of 5. A chain that reaches depth 5 without producing a PROMOTE-eligible refined claim or a PATTERN_* terminal pattern is auto-terminated. The depth limit is configurable but capped at 10 even with override.

### Rule 4: Compute budget per claim family
Total compute spent on a CLAIM and all its REFINE descendants is bounded. Default budget is 100x the cost of the original CLAIM's first FALSIFY. If exceeded, the chain terminates with `PATTERN_RESIDUAL_BUDGET_EXHAUSTED`. This prevents the rescue-indefinitely failure mode mechanically.

### Rule 5: Adversarial counter-explanation
At each REFINE step, an adversarial agent (Charon, or a future Kairos-class adversarial reviewer) must propose a simpler instrument-error or sampling-noise explanation for the residual. If that counter-explanation survives FALSIFY, the chain terminates with `PATTERN_RESIDUAL_ARTIFACT`. If the counter-explanation is itself falsified, the residual is upgraded to "structurally surviving" and REFINE may continue.

These rules together produce a **bounded discipline** on residual-chasing. A residual either drives toward 100%/0% under refinement (Rule 1 + Rule 2), exhausts the search budget (Rule 4), exhausts the depth limit (Rule 3), or is killed by adversarial counter-explanation (Rule 5). In every case the kernel produces a typed substrate object recording the outcome — either a refined PROMOTE or a typed terminal kill-pattern.

## META_CLAIM — the self-calibration loop

Some residuals are claim error. Some are instrument error. The architecture must allow the latter to surface mechanically.

```
META_CLAIM(
    target_battery_test: TestHash,           # which kill-test is being challenged
    calibration_set: KnownTruthsSet,         # what the test is being challenged against
    observed_metric: float,                  # what the test produced
    predicted_metric: float,                 # what it should have produced
    evidence: ResidualClusterHash,           # aggregate residuals supporting the challenge
) → Claim
```

A META_CLAIM is a regular CLAIM but with target = a battery test rather than a hypothesis about mathematics. It is FALSIFIED by the battery applied to itself: does the battery test in question reliably produce predicted_metric on calibration_set? If observed_metric ≠ predicted_metric is robust under re-running, the META_CLAIM survives, and the battery test is flagged as defective. Techne is then triggered to refine or replace the test.

Surviving META_CLAIMs are **the only mechanism by which the battery itself can be modified.** Battery tests are otherwise frozen (per v0.1 semantics). This preserves the discipline of "don't tweak the instrument to rescue a claim" while still allowing legitimate instrument refinement to flow through the same falsification machinery as everything else.

The asymmetry: a META_CLAIM is an order of magnitude harder to promote than a regular CLAIM, because it must demonstrate consistent battery defect across multiple independent calibration claims. This prevents instrument-doubt from being a cheap escape hatch.

## Cross-claim residual clustering

Aporia's role expands. In addition to scanning open problems, Aporia scans the growing collection of Residuals for structural similarity:

```
CLUSTER_RESIDUALS(residuals: list[ResidualHash], similarity: SimilarityMetric) → ResidualCluster
```

Clusters with high internal similarity and significant size (default: ≥3 residuals from independent claims with cosine-similarity > 0.8 in failure_signature space) are promoted as candidate cross-domain phenomena:

> "Residuals R1, R2, R3 from claims about elliptic curves, character sums, and modular forms all share failure_signature S. What does S represent?"

This becomes a CLAIM in its own right — a hypothesis that the cross-claim residual structure points to a shared underlying mechanism. If the CLAIM survives FALSIFY, it becomes a **residual bridge** — a higher-order substrate symbol that maps regions of the cartography where the universe's noise is suspiciously structured.

Residual bridges are first-class anchors in cartography, distinct from the bridges between known concepts. They mark *suspected* structure rather than known structure. Future work that finds a positive explanation for the residual cluster can promote the bridge from suspected to known.

## Worked example

Hypothetical scenario showing the full pipeline:

1. **CLAIM C1:** "Lehmer's bound is exactly 1.17628 for all non-cyclotomic Mahler measure across LMFDB number fields deg 8-14."
2. **FALSIFY:** Returns `verdict=BLOCK, score=0.9913, residual=R1` where R1 captures: 0.87% of evaluated number fields have Mahler measure < 1.17628 by ε ≈ 1e-6 — within numerical tolerance but persistently below.
3. **R1 inspection:** failure_signature.type = "structured" (the 0.87% concentrate in degree-9 specifically); failure_signature.descriptor records the degree-9 cluster.
4. **REFINE C1 + R1 → C1.1:** "Lehmer's bound is exactly 1.17628 for all non-cyclotomic Mahler measure across LMFDB number fields deg 8-14, *except for the deg-9 sub-family where the bound may be approached more tightly than numerical precision allows.*"
5. **Adversarial counter-explanation:** Charon proposes "the deg-9 cluster is floating-point round-off in the PARI/GP Mahler measure routine." This counter-CLAIM is FALSIFIED via Techne forging a high-precision arbitrary-arithmetic checker (Rule 5 in action).
6. **High-precision check:** The deg-9 residuals persist at 100x precision. Counter-explanation is killed.
7. **Cross-modality verification (Rule 2):** Residual is re-checked using SAT-encoded Mahler-measure bounds. Same deg-9 cluster appears.
8. **REFINE C1.1 + R1.1 → C1.2:** Refined claim now includes specific upper bound on the deg-9 deviation.
9. **PROMOTE C1.2:** The refined claim survives the full battery at 100% under both modalities. Promoted as `lehmer_bound_with_deg9_correction@v1`.
10. **TRACE C1.2:** Recovers the full chain: C1 → R1 → adversarial-test → cross-modality-test → C1.1 → R1.1 → C1.2. Every step content-addressed, every residual preserved.

The original C1 is preserved as a typed object with status `superseded_by=C1.2`. Nothing is overwritten. The substrate grows by one PROMOTEd refined claim plus the chain of evidence that produced it.

## What this spec deliberately does not do

- **Does not modify v0.1 kernel primitives.** RESOLVE, CLAIM, FALSIFY's three-verdict semantics, GATE, PROMOTE, ERRATA, TRACE all unchanged. The new primitives extend the set; they don't replace.
- **Does not require the new primitives for v0.1 use cases.** Existing claims that don't carry residual structure can use the v0.1 boolean-equivalent FALSIFY semantics. Spectral verdicts are opt-in per-test.
- **Does not specify Techne's residual-forging intelligence.** That's a separate spec — what Techne does with a residual to forge a finer instrument depends on the residual's failure_signature and is itself a research problem.
- **Does not specify Aporia's clustering algorithm.** That's a separate spec — what similarity metric Aporia uses, how it weights structural vs. parametric similarity, whether it uses learned embeddings or symbolic features.
- **Does not legislate compute budgets.** Default values are starting points. Real budgets emerge from operational experience.

## Implementation status

Not yet implemented. Spec only.

Implementation order, lowest-risk first:

1. **FALSIFY semantic extension.** Existing FALSIFY callers continue to work; new SpectralVerdictResult is opt-in. Add `score` and `residual` fields with defaults that match v0.1 behavior. ~1 day's work.
2. **Residual storage.** Content-addressed, append-only, mirrors existing CLAIM storage. ~2 days.
3. **REFINE operation.** New top-level primitive. ~1 day for the operation itself; the harder work is the termination rule enforcement (next item).
4. **Termination rules.** Rules 1, 3, 4 are mechanical (count cycles, count depth, count compute). Rules 2 and 5 require adversarial-agent integration. ~1 week for full implementation.
5. **META_CLAIM.** Reuses CLAIM machinery with a different target type. ~2 days.
6. **CLUSTER_RESIDUALS.** Requires clustering algorithm choice. Out of scope for first pass; do it manually until usage patterns indicate the right algorithm. ~separate work.

Total: ~2 weeks of focused engineering work for the kernel-side extensions, not counting Techne's residual-forging intelligence or Aporia's pattern-detection.

## Pilot success criterion

Before committing to the full v0.2 architecture, run a pilot:

- Take the OBSTRUCTION_SHAPE candidate work (`a149_obstruction.py`, `a148_validation.py`).
- Re-run with spectral FALSIFY emitting Residuals.
- For each Residual, attempt one REFINE cycle.
- Measure: does any REFINE produce a survivor that wouldn't have survived under v0.1's binary FALSIFY?

**Pilot success threshold:** at least one REFINE in the pilot produces a survivor, with content-addressed provenance back to a v0.1-killed claim. If yes, the architectural extension is empirically justified and proceeds to full implementation. If no, the principle is correct in spirit but premature in practice; defer until larger sample sizes provide evidence.

This is the honest empirical anchor. The architecture is specced; the principle is articulated; whether the substrate actually compounds via residual-driven refinement is an open empirical question. The pilot resolves it.

---

*The spec exists. The implementation is the next move. The pilot is what tells us whether the principle pays off in practice or remains methodologically right but operationally unconvincing.*

— Charon
