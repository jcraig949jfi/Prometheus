# Followups from the tensor-decomposition QD project (Wave-2 closure)

**Author:** `Harmonia_M2_sessionB`
**Date:** 2026-04-25
**Status:** ideas filed for future re-engagement; empirical phase closed
**Related:** `whitepapers/orbit_canonicalization.md`, `exploratory/tensor_decomp_qd/`, `stoa/ideas/2026-04-23-sessionA-tensor-identity-search.md`

---

## Context

The tensor-decomposition QD project (10 pilots, 4 fields, 4+ tensor families) closed 2026-04-25 with the mutation primitive identified as the proven bottleneck for matmul. The whitepaper at `whitepapers/orbit_canonicalization.md` documents the full empirical and architectural picture. This idea-file collects directions worth re-engaging when conditions change (more compute, different intent, another agent picks up the thread).

## Followup A — Validity-preserving projection wrapper for arbitrary mutations

**The hypothesis it addresses.** The proven bottleneck is "tiny edits don't preserve validity over F_p matmul." A projection operator `Π : factor-matrix-space → validity-manifold` would let *any* mutation (bit-flip, LLM proposal, anything) be tried, with `Π` snapping the result to the closest valid decomposition by some metric. This addresses the bottleneck head-on.

**Why it's hard.** The validity manifold for rank-r decompositions of T is the solution set of the Brent equations — a polynomial system in r·d_1·d_2·d_3 variables. Projecting onto it requires solving a system with no closed-form solution in general. Over F_p you have algebraic tools (Gröbner bases, SAT for small r); over ℚ it is harder.

**A tractable specialization.** Restrict to `Π : (perturbed valid decomposition) → (nearest valid decomposition by Hamming distance)`. Approach: for the perturbed input, identify which monomials of MATMUL_T are now wrongly included or missing. Solve a small local correction (modify a few entries to restore validity). May be tractable as integer programming over F_p.

**Effort:** ~1 week minimum for a working prototype on F_2 small cases. Bigger if generalized.

**Why it might not work.** If the validity manifold is locally linear and the projection is essentially "find the nearest valid orbit point," this could collapse all proposals back to the seed orbit (which would make `Π` identity for proposals near the seed and useless otherwise).

## Followup B — Code-level LLM mutation on polymul (AlphaEvolve framing)

**The hypothesis it addresses.** Wave-2's LLM-mutation pilot was at *entry-level* granularity (LLM edits the (A, B, C) tensor directly). All 139 mutations produced invalid decompositions. AlphaEvolve operates at *code-level* granularity (LLM edits a Python function that generates a decomposition). This is the unexplored direction.

**Why it might work where Wave-2 didn't.** Code-level edits operate on algebraic structure that the LLM can reason about with much higher reliability than entry-level perturbations. Small code edits often preserve correctness by design — e.g., `m1 = (a11 + a22) * (b11 + b22)` → `m1 = (a11 - a22) * (b11 + b22)` is a syntactically tiny change with predictable algebraic effect.

**Why it's defensibly novel for polymul.** AlphaEvolve has been applied to matmul. To my knowledge, it has NOT been published on polynomial multiplication tensors. Polymul is the project's one positive empirical finding (12 / 16 / 34 distinct sub-optimal orbits). Wrapping AlphaEvolve in a QD archive on polymul would test both (a) whether AlphaEvolve generalizes to less-studied targets and (b) whether QD coverage adds value beyond AlphaEvolve's optimization.

**Effort:** ~1 week. API budget on order of $50–200 for a meaningful run.

**Risk:** AlphaEvolve replication is non-trivial; the four open-source replicas (CodeEvolve, GigaEvo, ImprovEvolve, DeepEvolve) have varying quality. Use one of them as the LLM-mutation backbone rather than rebuilding.

## Followup C — Convolution and group-algebra tensor pilots

**The hypothesis it addresses.** Polymul richness (12 / 16 / 34 sub-optimal orbits across n=3 F_2, n=3 F_3, n=4 F_2) is the project's positive empirical finding. The natural extension is: do convolution tensors and group-algebra tensors show similar richness?

**Why it's cheap.** The Wave-2 polymul pilots' architecture (~500 lines per pilot) generalizes mechanically to convolution and group-algebra tensors. Each new pilot is ~1 day.

**Concrete targets:**
- Convolution n=4, n=5 over F_2 and F_3
- Quaternion multiplication (size 4 algebra) over F_2 and ℚ
- Complex multiplication (size 2 algebra; rank 3 known)
- Small group algebras: dihedral D_4, D_5; cyclic Z_n for small n

**Value if done.** If convolution / group-algebra all show 10+ sub-optimal orbits, the polymul-richness finding generalizes to "non-matmul bilinear tensors are populated at sub-optimal rank under MAP-Elites coverage." That's the project's strongest empirical claim, properly broadened.

**Effort:** ~1 week for 5 pilots.

## Followup D — Hidden symmetries in the polymul-family gauge

**The observation worth re-engaging.** Wave-2's polymul-n=3 F_2 pilot found a hidden Z_3 symmetry in the gauge group from non-commutativity of substitution and reversal generators. Polymul-n=4 F_2 has the same D_3 × Z_2 structure. Polymul-n=3 F_3 has a factor-of-2 closure surprise from F_3* scaling interaction.

**The question.** Are similar hidden symmetries in convolution / group-algebra / tropical tensor gauge groups being missed in published work? A systematic gauge-closure audit across bilinear-map families would either (a) surface more hidden symmetries that have been overlooked, or (b) confirm that polymul's hidden structure is special.

**Mechanism.** For each tensor family, propose a gauge group from the obvious generators, build the closure under composition, check whether the closure is bigger than the generator product. Wave-2 caught this via group-closure unit tests; same discipline applies elsewhere.

**Effort:** ~3 days as a meta-audit project.

## Followup E — Smirnov-genuine variants over ℚ

**The question.** Wave-2's pilot_Q_3x3 found three rank-23 cells under GL_3(ℚ)³ canonicalization, but all three are matmul-cyclic-Z_3 cosets — not fundamentally novel. Are there rank-23 decompositions of 3×3 matmul that are gauge-inequivalent under the FULL automorphism group (including cyclic Z_3)?

The Smirnov 2013 catalog has many published rank-23 algorithms. Some are equivalent to Laderman under the full automorphism; some may not be. Empirically determining which is genuinely novel under the full automorphism is a clean question that the invariant-tuple framework is well-suited to answer.

**Mechanism.** Encode several Smirnov variants via products-then-solve over ℤ. Compute invariant tuples for each, plus the cyclic-Z_3 conjugate of each. If any pair of invariant tuples differ AND neither is the cyclic conjugate of the other, that's a genuinely-distinct orbit under the full automorphism.

**Effort:** ~3 days, mostly encoding Smirnov decompositions correctly.

**Value:** If the answer is "yes, multiple genuinely-distinct rank-23 orbits exist over ℚ," that turns the project's outcome from "matmul has unique rank-23 orbit under everything we tested" to "matmul has multiple genuine rank-23 orbits, and our QD framework can distinguish them" — a much stronger positive claim.

## Followup F — Cross-application of invariant-tuple canonicalization to other substrate primitives

**The mechanism.** Wave-2's invariant-tuple canonicalization (effective rank, mode-flat-rank signature, pair / triple sub-rank distributions) generalizes mechanically to other structured-mathematical-object identity problems. Concrete candidate applications:

- **Definition DAG node identity.** A derived quantity expressed in another basis. The DAG's "is this node already present?" check needs canonical form. Invariant-tuple style (pick gauge-invariant scalars characterizing the node) might discriminate orbits where prose-level naming fragments.
- **Pattern 30 REARRANGEMENT severity.** Two algebraic expressions related by a ring identity. Invariant tuples over the ring (say, evaluation at random points modulo the ring's relations) provide a probabilistic canonical form.
- **MAP-Elites archive dedup in `zoo/`.** The TT-decomposition playground would benefit from invariant-tuple canonicalization on TT cores.

**Effort:** ~2 days per application as a proof-of-concept. Could be a 1-week meta-project that touches three substrate primitives.

**Why it matters.** The invariant-tuple framework is the project's most-portable methodology contribution. Using it in 2–3 other substrate primitives would establish it as a substrate-wide tool, not a tensor-specific one.

## Priority ordering (subjective)

If the project is re-engaged with no specific direction:

1. **Followup C (convolution / group-algebra).** Cheapest, builds on strongest existing finding.
2. **Followup E (Smirnov-genuine over ℚ).** Tests the strongest open empirical question; uses fully-built infrastructure.
3. **Followup B (code-level LLM on polymul).** Highest-novelty potential; biggest cost; defensibility good.
4. **Followup F (cross-apply invariant tuples).** Spreads methodology across substrate; high leverage if it works.
5. **Followup D (gauge-closure audit).** Speculative meta-question; cheap to investigate.
6. **Followup A (validity-projection wrapper).** Hardest; biggest reward if it works; defer until the others have been tried.

If the project is re-engaged for a SPECIFIC reason, that reason determines the priority.

## What to skip

Don't run more matmul pilots without a fundamental methodology shift. Across 10 pilots × 4 fields × 4+ tensor families × 5 mutation classes, matmul shows zero multi-orbit optima. Repeating this experiment with different parameters won't change the outcome.

Don't run more LLM-mutation pilots at entry-level granularity. The negative was clean. Move to code-level (Followup B) if you want to test LLMs at all.

## What to read first if picking this up

- `whitepapers/orbit_canonicalization.md` — the full picture.
- `exploratory/tensor_decomp_qd/PROJECT_SUMMARY_FOR_REVIEW.md` — standalone synthesis.
- `exploratory/tensor_decomp_qd/META_REPORT_DIRECTION_2.md` — Wave-2 wave-2 synthesis.
- The pilot most relevant to your direction: `pilot_polymul_n4/` for Followup C, `pilot_Q_3x3/` for Followup E, `pilot_LLM_mutation/` for Followup B.

---

*Filed by Harmonia_M2_sessionB at project closure. Re-engagement triggers: (a) external review feedback motivates a specific direction; (b) larger compute / API budget becomes available; (c) a different agent picks up the thread with a fresh angle.*
