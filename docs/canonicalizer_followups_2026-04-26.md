# Canonicalizer — Followups Captured 2026-04-26
## End-of-session followup list after external review of session summary

**Author:** Harmonia_M2_sessionA, 2026-04-26.
**Status:** captured at session close. Not a plan — a backlog. Each item names what, why it matters, rough cost, and what would gate execution.

This document is the audit-trail companion to:
- `docs/session_summary_2026-04-25_for_review.md` — the summary that went out for review
- `docs/whitepaper_orbit_canonicalization_v4.md` — the v4 whitepaper as it stands at session close
- The frontier-model review embedded in the conversation transcript on 2026-04-26 (substantive critique of the four-subclass stratification, Strategy 4 failure diagnosis, gen_12 product decision, orbit-structure hypothesis, and overclaims)

---

## Tier 1 — Architectural, high-leverage

### F1.1 — gen_12 resolution contract at type level

**What.** Replace label-based variety-vs-orbit dedup in `gen_12` with type-signature enforcement. API surface like:

```python
def novelty(query, resolution: Literal["variety", "orbit", "representative"]) -> NoveltyResult: ...
```

with explicit failure when the requested resolution is unsupported by the registered canonicalizer instance.

**Why it matters.** Reviewer's strongest pragmatic critique: "consumers routinely ignore labels." The current variety-level dedup labeled-as-such is sufficient documentation but insufficient enforcement. Coarse dedup will eventually be mistaken for fine novelty if the API doesn't refuse. Encoding granularity in the type signature prevents the consumer-side error before it happens.

**Cost.** ~2 hours. API change in `gen_12` spec, instance metadata gains a `supported_resolutions` field, registry validates resolution requests against instance capabilities.

**Gate.** None — directly actionable. Reviewer flagged this as the action that "derisks active consumers now" and recommended promoting it ahead of further research experiments.

---

### F1.2 — 2D classification refactor (equivalence × assurance)

**What.** Investigate whether the current four-subclass stratification (`group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint`) is mixing two orthogonal axes:
- **Equivalence type:** group_quotient / partition_refinement / ideal_reduction / deformation_class / moduli_component / model_theoretic / ...
- **Assurance level:** exact_quotient_certified / algorithmically_canonicalized / invariant_fingerprint_heuristic / ...

If true, `variety_fingerprint` is not a peer of `group_quotient` — it's the combination `(constraint_defined_equivalence × invariant_fingerprint_heuristic)`.

**Why it matters.** The reviewer's largest architectural point. Conflating two axes produces a closed-but-wrong taxonomy. Open it up explicitly into a 2D grid and the same instances slot in cleanly without `variety_fingerprint` having to carry the weight of two distinct concerns.

**Cost.** ~4-6 hours. Substantial canonicalizer.md revision (v0.4); requires re-classifying the existing instances along both axes; may surface new design constraints.

**Gate.** James's call: explore now, or hold four-subclass v0.3 as working hypothesis and revisit after instance coverage broadens to ≥3 subclasses with real implementations? Captured at session close as **open**.

---

### F1.3 — `deformation_class` / `moduli_component` candidate subclass

**What.** Add a fifth subclass for equivalence-by-deformation: moduli problems, persistent homology, gauge-equivalence up to deformation, continuation classes, connected-component identity in parameter spaces.

**Why it matters.** Reviewer's observation: the open question on real-orbit structure of 2×2 matmul rank 7 is *already flirting with this category*. If `V_T(7)` over ℝ has multiple connected components, "which component does this decomposition lie in?" is exactly a `moduli_component` question, not a `group_quotient` one. The current taxonomy may be missing the subclass where the open work actually lives.

**Cost.** ~2-3 hours conceptual design + draft sketch in canonicalizer.md.

**Gate.** Probably blocked by F1.2 (do the 2D refactor first; deformation may slot in along the equivalence-axis there).

---

### F1.4 — False-dedup-rate metric operationalization

**What.** Pin per-instance targets for the renamed metric (was "collision budget"; now "declared-limitation false-dedup rate" — C-collision rate where non-equivalent inputs map to the same canonical form because C is incomplete). Build automated calibration that runs as a registered anchor.

**Why it matters.** Reviewer: "converts philosophy into measurable substrate behavior. Huge leverage." Currently a v0.4 deferred item; the reviewer argued it should jump priority and run before more instances ship.

**Cost.** ~2 hours. Requires per-subclass test-set construction (positive: same-class inputs; negative: known-different-class inputs).

**Gate.** None — directly actionable. Should likely run in parallel with F1.1 since both are about making the contract enforce-able rather than aspirational.

---

## Tier 2 — Instance coverage

### F2.1 — `graph_iso@v1` partition_refinement instance

**What.** Implement classical graph canonical form via nauty/Bliss-style partition refinement + lex labeling.

**Why it matters.** Reviewer prioritized this above further matmul work: "more subclass coverage reduces risk of overfitting architecture to one pathological tensor case." `partition_refinement` subclass currently has zero real instances; one shipped instance would stress-test the contract beyond `group_quotient`-only.

**Cost.** ~3-4 hours. Standard algorithms exist (PyNauty, networkx canonical labeling); cost is mostly integration.

**Gate.** None.

---

### F2.2 — `pattern_30_rearrangement@v1` ideal_reduction instance

**What.** Canonical form for algebraic expressions over a declared ring, operationalizing Pattern 30 Level-3 REARRANGEMENT severity. Likely Gröbner-basis normal-form approach via sympy.

**Why it matters.** Currently `ideal_reduction` subclass has zero real instances. Pattern 30 discipline runs in parallel; this instance unifies it with the canonicalizer contract. Convergence of the two frameworks was named in v4 whitepaper but remains conceptual.

**Cost.** ~4-6 hours. BSD-ingredient ring needs careful specification; tests need to handle the F043 anchor case.

**Gate.** None directly, but easier after F1.2 (2D classification) settles whether `ideal_reduction` is an equivalence-axis or a combined axis-pair.

---

### F2.3 — `dag_node_identity@v1` group_quotient instance

**What.** Definition DAG node identity under basis change on the input atoms.

**Why it matters.** Definition DAG was promoted to substrate primitive in 2026-04 alongside the canonicalizer; the integration between them was named but not implemented. DAG without canonicalization fragments under basis drift.

**Cost.** ~3 hours.

**Gate.** None directly. Coordinate with whoever owns the DAG primitive.

---

## Tier 3 — Tensor research-mode (orbit-level Type A for matmul)

### F3.1 — Two-anchor Strategy 4 variant

**What.** Same recipe as Strategy 4 attempted 2026-04-25, but pin a SECOND distinguished rank-1 term's `(U, V, W)` simultaneously with the first anchor's. Constraint compatibility between two anchor terms is non-trivial — the system may be over-determined or inconsistent in ways that themselves diagnose orbit structure.

**Why it matters.** Reviewer: "single-anchor failure almost begs for this. I would have tried this before elevating 'failure instructive' much." Highest research-value next experiment per the reviewer.

**Cost.** ~90 min implementation + analysis.

**Gate.** None directly. Demoted from Tier 1 (prior session) to Tier 3 (post-review) because it derisks no active consumer.

---

### F3.2 — Incidence-pattern canonicalization

**What.** Use anchor + relational/incidence structure across all rank-1 terms: singular/full-rank pattern, intersection structure, pairwise determinant signatures, hypergraph of coupling relations. May absorb GL freedom globally rather than locally.

**Why it matters.** Reviewer flagged this approach as "underexplored" relative to single-anchor.

**Cost.** ~4-6 hours. Substantial design work; the right relational invariants are not obvious.

**Gate.** None.

---

### F3.3 — Slice-based normalization

**What.** Fix gauges using flattenings/slices of the full tensor rather than termwise anchors.

**Why it matters.** Reviewer: "sometimes much more robust than rank-1 anchor fixing."

**Cost.** ~3-4 hours.

**Gate.** None.

---

### F3.4 — Cartan moving-frame approach

**What.** Apply Cartan's moving-frame method to the GL action on decomposition space.

**Why it matters.** Reviewer: "smells like Cartan moving frames territory. Could be the right mathematical tool."

**Cost.** Open-ended. Real research-mode.

**Gate.** None, but lowest-priority among the alternates because the math may not converge to a shippable algorithm in bounded time.

---

## Tier 4 — Documentation + audit cleanup

### F4.1 — Soften overclaims in v4 whitepaper

**What.** Revise three specific lines per reviewer:
- "lesson the v2→v3→v4 cycle taught" → "motivated by the v2→v3→v4 cycle"
- "absorbed cleanly" → "did not require architectural rupture"
- Cross-domain validation language → "promising cross-domain evidence"

Also update §4 to call out the verification-story asymmetry (only `group_quotient` has empirical stress; others are aspirational).

**Why it matters.** Reviewer caught these as overclaims. v4 whitepaper as it stands has them.

**Cost.** ~30 min targeted edits.

**Gate.** Should land before any v5 reframing happens, so the audit trail shows the soft-corrected v4 distinct from a future structurally-different v5.

---

### F4.2 — Read sessionB parallel pilot output, integrate findings

**What.** sessionB has been running `F_2`, `F_3`, `Q` matmul pilots in parallel. Their results may speak to the open orbit-structure question on the matmul family.

**Why it matters.** Reviewer + I both agreed: cheap information, potentially large gain on the open Q-Math-1.

**Cost.** ~30 min reading + 30 min integration write-up if anything material lands.

**Gate.** None.

---

### F4.3 — Caveat on orbit-structure language in v4

**What.** Reviewer: "DE failure is suggestive, not classifying." The v4 whitepaper §6 currently uses language that might be read as treating the multi-component hypothesis as established. Soften to "consistent with multi-component hypothesis; not settling evidence." Also consider the alternative: stratification by semialgebraic orbit types / stabilizer types vs. genuine disconnection (different phenomena, both compatible with the data).

**Cost.** ~15 min targeted edits.

**Gate.** Same as F4.1.

---

## Closure

The session that produced this list shipped:
- v3 + v4 whitepapers (`docs/`)
- canonicalizer.md v0.3 with four-subclass stratification + v2 reclassification (`harmonia/memory/architecture/`)
- Two pilot diagnostics confirming v2 is `variety_fingerprint` not `group_quotient` (`harmonia/tmp/`)
- Strategy 4 attempted + diagnosed as insufficient (`harmonia/tmp/`)

The reviewer's headline observation — *"the most valuable thing here may not be the canonicalizer instance but the emerging discipline of equivalence-resolution as typed infrastructure"* — survives as the forward thread. The canonicalizer primitive turned out to be a strong working hypothesis that will need more cross-instance stress before it's a stable substrate grammar. F1.1 (resolution contract), F1.2 (2D classification), F2.1 (graph_iso), and F2.2 (pattern_30 rearrangement) are the highest-leverage moves toward turning the hypothesis into infrastructure.

---

*Closure document by Harmonia_M2_sessionA, 2026-04-26. Followups captured at session close. No item is in flight; all are backlog. The session itself ends here pending direction on which followups, if any, to start in the next session.*
