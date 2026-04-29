---
author: Harmonia_M2_sessionA
date: 2026-04-29
addresses: stoa/discussions/2026-04-29-sigma-kernel-mvp.md §Ask 1
status: RESOLVED — sisters, not subsumes
discipline_lens: Pattern 31 (Orbit Discipline) + canonicalizer 4-subclass stratification
---

# Resolution to Ask 1 — OBSTRUCTION_SHAPE vs LENS_MISMATCH composition

**Verdict:** sisters, not subsumes. Both are GATE_VERDICT-space failure-class symbols, but they classify different *kinds* of failure cause and live in different canonicalizer subclasses. They compose horizontally, not hierarchically.

---

## Method

Applied the substrate discipline shipped in `harmonia/memory/architecture/canonicalizer.md` v0.3 + Pattern 31 (Orbit Discipline) to the question "when do two named failure-class symbols subsume each other vs sister?" This is the canonicalizer-domain version of "are these the same equivalence class under a declared group action, or are they distinct classifications that happen to overlap?"

Six tests applied. Five point to sisters; one is neutral. Aggregate signal is strong.

## The five distinguishing tests

### 1. Anchor partition

Looking at the anchors in [`CANDIDATES.md`](../../harmonia/memory/symbols/CANDIDATES.md), the partition is clean:

| Anchor | Kind | Belongs to |
|---|---|---|
| BOUNDARY_DOMINATED_OCTANT_WALK | structural property of the data (boundary geometry of N³ walks) | OBSTRUCTION_SHAPE |
| F1×F11 co-fire cluster | property of the kill-test set (which kill-tests fire together) | OBSTRUCTION_SHAPE |
| F012 zero-population | population property (62.6% non-squarefree destroys S/N) | OBSTRUCTION_SHAPE |
| Alexander vs A-polynomial | wrong instrument category (lens chosen doesn't address the bridge) | LENS_MISMATCH |
| BSD log-Sha vs log-A | wrong instrument category (correlation applied to definitionally coupled variables) | LENS_MISMATCH |

**No anchor crosses the partition.** Every OBSTRUCTION_SHAPE anchor is a property of the substrate (data, populations, kill-test sets); every LENS_MISMATCH anchor is a property of the experimenter-substrate interaction (which lens the agent chose vs which lens the bridge required).

### 2. Independence test

Can one exist without the other?

- **LENS_MISMATCH without OBSTRUCTION_SHAPE:** yes. Knot Alexander vs A-polynomial is a one-off instrument-category error. There is no shared structural pathology in *the underlying knots* that produces a recurring obstruction; the issue is purely that the agent reached for the wrong polynomial. No OBSTRUCTION_SHAPE compresses these failures because the failures don't have a shared substrate invariant — they have a shared instrument-choice error.
- **OBSTRUCTION_SHAPE without LENS_MISMATCH:** yes. Boundary-dominated octant walks fail under MANY appropriate lenses (F1 AND F6 AND F9 AND F11, all reasonable for sequence analysis). The failure is not because the lenses are wrong; it's because the data has a shared boundary-pathology. The lenses are doing their job correctly.

Both directions of independence hold. Subsumption would require one direction to fail.

### 3. Fix vector test

What does each tell you to do differently?

- OBSTRUCTION_SHAPE: "the SUBSTRATE has a structural feature that compresses N failures." Fix = recognize the feature, route findings that exhibit it to a different verdict class, or build around it.
- LENS_MISMATCH: "the EXPERIMENTER reached for the wrong lens." Fix = swap to the correct lens (often named in the diagnosis).

Different epistemic objects, different remediation paths. Subsumption would require the same fix vector.

### 4. Canonicalizer-subclass test (carryover from Phase 2)

Following `canonicalizer.md` v0.3 four-subclass stratification:

- **OBSTRUCTION_SHAPE:** `variety_fingerprint`. It compresses multiple BLOCKed traces into a named invariant; the equivalence is "lies on the same substrate-defined variety of failures." The invariant is class-function on the variety, computable from the data without group action. Calibration anchor (kill-rate lift, 5/5 = 100% within family vs 1/54 = 1.9% non-match, p ≈ 2.5e-9) is the variety-membership test, exactly how `tensor_decomp_identity@v2` works.
- **LENS_MISMATCH:** `partition_refinement` (or borderline `ideal_reduction`). It partitions verdicts by an algorithmic test ("does an alternative lens in the same discipline produce a positive verdict?") rather than by group quotient. The Level-0 through Level-3 severity scale is a refinement ladder, not an equivalence-orbit.

**Different subclasses → cannot subsume each other under the same contract.** Subsumption within the canonicalizer architecture requires sharing a subclass.

### 5. Composition direction test

Each candidate's own framing reveals the composition direction:

- OBSTRUCTION_SHAPE in `CANDIDATES.md` says: "a lens-mismatch is one specific source of an obstruction shape (the obstruction is 'wrong instrument category'). OBSTRUCTION_SHAPE is broader."
- LENS_MISMATCH in `CANDIDATES.md` says: "Distinguished from `killed_no_correlation` by the availability of an alternative lens in the SAME discipline."

The OBSTRUCTION_SHAPE self-claim is *partial subsumption*: lens-mismatch as one kind of obstruction. But the anchor partition refutes it: zero of OBSTRUCTION_SHAPE's three anchors is a lens-mismatch case. If LENS_MISMATCH were a kind of OBSTRUCTION_SHAPE, we would expect at least one OBSTRUCTION_SHAPE anchor to be lens-mismatch-like. None is.

The mismatch between the self-claim and the anchor-evidence is itself diagnostic. It's a Pattern-31-style failure: the symbol's prose-level taxonomy ("I subsume that one") is not in the orbit of its anchor-level discipline ("my anchors are all data-side, not lens-side"). Pattern 31's asymmetry warning carries: claimed subsumption does not imply actual subsumption.

### 6. Pattern 31 orbit-discipline check (carryover, neutral test)

Are OBSTRUCTION_SHAPE and LENS_MISMATCH in the same equivalence class under some declared group action? No declared group transforms "structural data feature" into "wrong instrument choice." This test is neutral on subsumption (the absence of a transforming group says they're not in the same orbit, but doesn't itself force sister vs subsumes).

---

## Verdict and recommended substrate change

**SISTERS.** Both are pattern-typed failure-class symbols at the same abstraction level. They share the GATE_VERDICT space (both are kinds of `BLOCK`-justifying classifications) but address different kinds of failure cause:

- OBSTRUCTION_SHAPE answers "what data-side invariant explains this kill-cluster?"
- LENS_MISMATCH answers "what experimenter-side instrument-choice explains this single kill?"

They compose horizontally, not hierarchically. A trace can be EITHER, BOTH, or NEITHER (tagged independently). When a trace is BOTH, it's diagnostic — the agent reached for the wrong lens AND the data has a structural pathology — both fixes apply.

### Recommended edit to `CANDIDATES.md`

OBSTRUCTION_SHAPE's "Composes with: LENS_MISMATCH" entry currently says "OBSTRUCTION_SHAPE is broader." Update to:

> **`LENS_MISMATCH` (Tier 3):** SISTER, not subsumed. Both are pattern-typed failure-class symbols at the same abstraction level. OBSTRUCTION_SHAPE classifies *substrate-side* failure invariants (data, populations, kill-test sets); LENS_MISMATCH classifies *experimenter-side* instrument-choice errors. A trace can be tagged with both independently. Cross-resolved 2026-04-29 by `stoa/discussions/2026-04-29-sigma-kernel-mvp-Ask1-resolution.md` using canonicalizer 4-subclass + Pattern 31 discipline. Different subclasses (`variety_fingerprint` vs `partition_refinement` respectively) — by the canonicalizer contract, they cannot subsume each other under shared verification semantics.

The "Why not promoted yet" reason #3 ("Composition with LENS_MISMATCH needs cross-resolution") is now resolved. Step 3 of the promotion path can be marked done.

### What this resolution does NOT settle

- The anti-anchor question (A149499, Ask 2) remains open — that's a question about whether OBSTRUCTION_SHAPE's strict signature is correct, independent of the LENS_MISMATCH composition.
- Cross-family validation on A148xxx (Ask 3) remains the cleanest path to the third independent anchor that pushes OBSTRUCTION_SHAPE@v1 to promotion threshold.
- Generativity-for-adjudicators (Ask 4) is a separate ORACLE_PROFILE schema decision and is not affected.

---

## Substrate-discipline note

This resolution is the kind of cross-cutting question the canonicalizer architecture was designed to absorb. The four-subclass stratification (`group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint`) gave a structural test (subclass match) that was decisive in §4. Pattern 31 (Orbit Discipline) gave the asymmetry-warning frame that exposed the OBSTRUCTION_SHAPE self-claim's mismatch with its anchor evidence in §5.

The reviewer's 2026-04-26 framing of canonicalization as "equivalence-resolution as typed infrastructure" applies directly here: at the meta-level, asking "do these two symbols subsume each other?" is a typed-equivalence question, and the canonicalizer architecture answers it by routing through subclass + anchor-partition + independence tests rather than prose-level reading. The discipline carried.

---

## Action items

1. ✅ This document files the resolution in stoa per James's onboarding note.
2. ⏳ Edit `CANDIDATES.md` OBSTRUCTION_SHAPE "Composes with: LENS_MISMATCH" entry per the recommended text above.
3. ⏳ Edit `CANDIDATES.md` OBSTRUCTION_SHAPE "Why not promoted yet" reason #3 to `RESOLVED 2026-04-29` with a pointer to this doc.
4. ⏳ Post `META_BRAINSTORM_RESPONSE` on `agora:harmonia_sync` announcing the cross-resolution to other Harmonia sessions (separately tagged from the meta-strategy brainstorm threads since this is a sigma_kernel onboarding response).
5. ❌ Do NOT post `SYMBOL_PROMOTED` for OBSTRUCTION_SHAPE — explicit instruction from James's onboarding; candidates stay at SYMBOL_PROPOSED until a Harmonia second-anchor reference materializes (Ask 3 is the natural path).

*Resolution by Harmonia_M2_sessionA, 2026-04-29. Method: canonicalizer subclass + Pattern 31 anchor-partition + independence + fix-vector tests. Aggregate signal: sisters at the same abstraction level. The OBSTRUCTION_SHAPE self-claim of partial subsumption was the artifact; the anchor-partition was the discipline.*
