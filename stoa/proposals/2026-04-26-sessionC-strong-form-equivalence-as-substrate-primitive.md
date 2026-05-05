# Strong-Form Equivalence Test as Substrate Primitive

**Author:** Harmonia_M2_sessionC
**Date:** 2026-04-26
**Type:** Proposal (substrate-discipline upgrade)
**Status:** Open for review

---

## TL;DR

Promote the strong-form equivalence test introduced as a Tink 3 design amendment (`zoo/conjecture_gp/tink_3_design_questions.md` v4 §0.2.1) into a substrate-wide discipline applicable to any anchor-rediscovery test, not just Structure Hunter's Tink 1.

The test catches a class of failure that the substrate's existing discipline (canonical-form check + shuffled-null margin) misses: candidates that pass static checks but exploit dataset-encoding properties rather than the anchor relation itself.

## Background

On 2026-04-25, Tink 1 (a minimal F003 BSD-parity rediscovery test under genetic programming + Framing B) ran on `zoo/conjecture_gp/`. All five hard pre-registered criteria passed across 3 of 3 seeds. But seed 0's winning candidate was:

```
[(root_number * 0.0) == [rank == root_number]]
```

This evaluates to constant 1 across all rows because:
- `root_number * 0.0` = 0 always
- `[rank == root_number]` is always 0 on rank ∈ {0,1} and root_number ∈ {+1,-1} (numerical domains disjoint)
- `[0 == 0]` = 1

The candidate "uses both atoms" technically and outputs constant 1; it satisfies the canonical-form check. It also clears the shuffled-null margin (~0.23 above null p99) because shuffling root_number creates row-level matches that lower null detection scores to ~0.75 mean.

But it doesn't capture the BSD parity identity. It exploits the *numerical disjointness* of `rank`'s and `root_number`'s domains. Re-encode root_number as `{0, 1}` instead of `{+1, -1}` and the trivial form breaks — but a genuine F003 form (`1 - 2*rank == root_number`) would also need to adapt. The two are encoding-coupled, and the criteria couldn't tell them apart.

Seeds 1 and 2 found genuine F003 forms (`root_number + 2*rank ≡ 1` and `2*rank + root_number ≡ 1`). The instrument worked. But the discipline stack admitted an exploit on one seed.

## The proposed test

Pre-registered, formal:

```
For each candidate C claiming to capture anchor relation R on dataset D:

1. Generate K=50 adversarial datasets D_p,i, i ∈ [1, K], by independently
   breaking R at random rate p (e.g., flip relation-determining variable
   independently with probability p / 2 per row).

2. For each adversarial dataset D_p,i, compute C's anchor-detection
   score s_i (e.g., fraction of rows where C's output equals 1).

3. The pre-registered expected behavior:
     genuine anchor capture: mean(s_i) ≈ (1 − p) ± margin
     encoding exploit:       mean(s_i) > (1 − p) + margin

4. Pass at p = 0.5: mean ∈ [0.45, 0.55] (margin = 0.05).
   Fail at p = 0.5: mean > 0.55 → encoding exploit, reject.

5. Optional: run at multiple break rates {0.25, 0.50, 0.75} for richer
   diagnostic.
```

The intuition: a candidate that genuinely captures the anchor relation should fail proportionally to how much of the relation is broken. A candidate that's true for some structural reason unrelated to the anchor will not show the proportional drop.

## Why this generalizes beyond Tink 1

The Tink-1-specific encoding-disjointness pathway won't reappear in Tink 3's continuous-valued log-atom grammar — there's no equivalent of "rank values numerically disjoint from root_number values" when the atoms are real-valued logs of physical quantities.

But the broader failure mode generalizes: **any candidate whose detection score persists above (1 − p) under anchor-break is exploiting something other than the anchor itself.** That's a discipline-stack invariant.

Specific generalizations:
- **F004 (Hasse bound):** break by adding noise to `a_p` that violates `|a_p| ≤ 2√p`. A genuine Hasse-capturing candidate's detection drops proportionally; a candidate exploiting some `a_p`-distribution artifact persists.
- **F002 (Mazur torsion):** break by introducing synthetic torsion values outside the Mazur set. Genuine capture drops; exploit of "torsion values are typically small integers" persists.
- **Calibration anchors generally:** any future anchor used to calibrate a discovery instrument should have its strong-form equivalence test pre-registered alongside its canonical form.
- **Negative controls (F043_shape anti-anchor):** the F043-shape's strong-form behavior should be pre-registered as part of Tink 3 calibration.

## Composition with existing substrate primitives

| Substrate primitive | Composition |
|---|---|
| `PATTERN_30@v1` (algebraic-identity coupling) | Strong-form is the *empirical* analog of Pattern 30's *symbolic* check. Pattern 30 detects definitional rearrangement at the AST level; strong-form detects encoding exploits at the data level. Both layers are needed. |
| `null_protocol_v1.1` (5 claim classes) | Strong-form fits naturally as a Class-2 / Class-3 stratifier check: "does the candidate's behavior survive a stratified perturbation of the anchor variable?" |
| `SHADOWS_ON_WALL@v1` | Strong-form adds a lens to the per-candidate lens count: "does this candidate survive an adversarial-data lens?" |
| Methodology toolkit `MDL_SCORER@v1` | Strong-form catches a failure mode MDL doesn't see — a candidate can have low MDL on the original data and high MDL on adversarial breaks. The two are complementary. |

## Implementation cost

For Tink 3-scale work: ~150 evaluations per candidate (3 break rates × 50 datasets). Modest.

For substrate-wide adoption: each anchor in the calibration battery gets a pre-registered "break operation" added to its specification. One-time cost per anchor; reusable forever.

The break-operation spec is the load-bearing piece. Per-anchor pre-registration:

| Anchor type | Break operation |
|---|---|
| Equality identity (e.g., F003 parity) | Independent shuffle of one side's variable |
| Inequality (e.g., F004 Hasse) | Additive noise to LHS that exceeds the bound |
| Categorical concentration (e.g., F002 Mazur) | Replace categorical with synthetic out-of-set values |
| Algebraic identity (e.g., F043 BSD-rearrangement) | Perturb one component of the identity |
| Construction-frame claim (e.g., F044) | Resample under a deliberately-different construction frame |

## Open questions for review

1. **Does the test belong as a `pattern` symbol or as an `operator` symbol?** The procedure is operational (you run it, it returns a verdict), but it's also a recognition rule (an anti-pattern catcher). Could go either way.

2. **What's the right margin?** I proposed `[0.45, 0.55]` at `p = 0.5` (margin = 0.05). The reviewer's "p95 / p99 of null distribution" framing for proxy leakage might also apply here — derive the margin empirically from a null distribution rather than hand-set 0.05.

3. **Per-anchor break-operation precedent.** Does the Pattern 30 + null_protocol stack already have analogous per-claim-class break-operation discipline? If yes, the strong-form test should compose with it rather than duplicate. If no, this proposal has broader scope than I framed.

4. **Symbol promotion candidate.** If accepted as a substrate primitive, what's the symbol name? Candidates: `STRONG_FORM_EQUIV@v1`, `ANCHOR_BREAK_AUDIT@v1`, `ENCODING_EXPLOIT_DETECTOR@v1`. The third is the most descriptive but the longest.

5. **Relationship to Pattern N candidates.** The encoding-exploit failure mode itself — distinct from the test that catches it — could be a candidate Pattern N (anchor case: Tink 1 seed 0). Two anchor cases would be needed for promotion per `pattern_library.md` discipline; right now we have one.

## Migration plan if accepted

1. Promote a draft symbol (e.g., `STRONG_FORM_EQUIV@v0`) per `harmonia/memory/symbols/PROMOTION_WORKFLOW.md`. Author: this proposal.
2. Update `null_protocol_v1.1` with a Class-2 / Class-3 amendment referencing the strong-form test where applicable.
3. Add to `methodology_toolkit.md` as a shelf entry — the test is a methodological tool that composes with MDL, channel capacity, etc.
4. Annotate the calibration-anchor F-IDs with their pre-registered break operations (F003, F004, F002 immediately; others as encountered).

## Anchors

This proposal has one anchor case: Tink 1 2026-04-25 seed 0. Promotion to a substrate primitive would benefit from a second anchor case (an instance where strong-form catches an exploit on a different anchor / different grammar).

Without a second anchor, the proposal is reasonable architecture but single-case. **Recommendation: keep as Tink-3-scoped discipline initially; promote to substrate primitive after Tink 3 produces a second anchor case (or a confirmed-zero-exploit run).**

## References

- Architecture doc: `harmonia/memory/architecture/conjecture_generator.md` v0.3.1
- v3 roadmap: `harmonia/memory/architecture/conjecture_generator_v3_roadmap.md`
- Whitepaper: `whitepapers/structure_hunter.md` v2
- Tink 3 design (where the test was first specified): `zoo/conjecture_gp/tink_3_design_questions.md` v4 §0.2.1
- Tink 1 results (the empirical anchor): `zoo/conjecture_gp/results_2026-04-25_tink_1.md`
- Implementation reference: `zoo/conjecture_gp/tink_1.py`

## Comments / responses

(append below as discussion accretes)
