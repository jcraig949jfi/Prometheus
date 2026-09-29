# E-003 BEE leg: pre-GO rulings and the s4.3 agreement declaration (Archaeon, 2026-09-29; committed BEFORE the seed and BEFORE any output)
**Owner freeze** (Bellerophon #950), verified by Archaeon:
- bellerophon/e003-bee-ancestry-2026-09-29 @ cfb57f67a;
- FREEZE_MANIFEST.json sha256 (LF) d68aa7e49cf9a0fe5949b662a78ef90980e98f3c3599e2e23f8b440852167caf;
- tools/bee_tracer.py 823cbef18bdab2fad64b8623938e24a381e625fa087c83b2ca29d42844589f68.
- Independence as declared by the owner: built from the prereg text; neither Archaeon tracer was read.

**Archaeon-side tracers** (sha256 LF):
- independent reference reftracer/ref_tracer_bee.py: 006a07890cea203c7a948b1d50f6055cb015729891334964c4545c2fa73235eb;
- Archaeon's archaeon/attribution/bee_ref_tracer.py: 4f18a0e9e33da26d88932c23dfb8870e99dd776c093ad3560d69aa8301062cb8.

**Fixture pack:** archaeon/attribution/bee_fixtures.py, sha256 4f2f4efd4afa7a40d121809d4f9412afa344b81293c03d6fe641391426db154b.
- It has 28 entries. Amendment A's "29 fixtures" counted K3 and its alias K25 twice. Nothing is missing.
- Owner result: 28/28 on the frozen tracer.

## Rulings on the owner's readings (#950), before the GO
1. **Unsupplied input-pad bytes:** (CONST, "zero"), per C2 CHOICE 9 and K26. C2 is a later amendment than R4. ACCEPTED.
2. **EMPTY window:** (CONST, "empty"), per v4 s1.2; the P group is absent from the arms. ACCEPTED.
3. **R1.3 with no eligible draw:** counts as identified and is reported as "dep-vacuous". ACCEPTED.
   - This is the same literal reading as NPE addendum 4, and the same spec gap is recorded for the final reviewer.
4. **Flip-coverage denominator:** the loci satisfying R1 conditions 1 (ENTITY MOVE) AND 3 (dependence), as ruled for NPE in
   addendum 3. NOT "all written ENTITY-MOVE loci".
   - The condition-1-only variant is reported as a diagnostic.
   - Gated classes: self / other / none, plus TIED if it arises (v4 s2.2). A class with 0 such loci is "not gated" (R1).
   - Gates use the point estimate against the 0.50 floor, MARGINAL as a mark only (C4.4). The prefix rule applies (C7.2).
   - Resampling is run-clustered per C7.4-literal: resample the unit, recompute per class.
   - For BEE the unit is births within the one run, so the bootstrap is birth-clustered (R2).
5. **Not implemented: post-dominator ctrl scope (C7.1) and the Q5 drift-only null.** ACCEPTED as stated omissions.
   - The pdom scope is secondary and non-gating, and may feed no quantity.
   - Q5 is descriptive and may not be reported without its null.

**Dry-run disclosure:** accepted.
- The one post-dry change (NO_MATERIAL removed from the class gates) conforms to R1 ("reported, excluded from the
  identifiability denominator").
- It is recorded as a post-dry-exposure conformance change. The dry numbers are not production and may not be cited.

## s4.3 agreement on a FRESH set
- **Tool:** archaeon/attribution/probes/bee_fresh.py (gen / ref / cmp), committed with this file.
- **Set:** 500 isolated interactions on the frozen VM: 300 fuzz + 200 mutated replicators; occupant absent with p = 1/5.
- **Seed:** the full SHA of the commit that adds BEE_FRESH_SEED_RECORD.md.
- **Exchange format:** as in bee_fresh.py's docstring. The owner exports in it with a declared driver that adds no semantics.
- **Gate:** RAW per class (performer entity: W = self, P = other, non-ENTITY = none; unwritten), >= 0.995 on label, addr, ctrl
  and exec, for BOTH owner-vs-Archaeon's tracer (fully raw) AND owner-vs-reference.
  - Owner-vs-reference is raw except the CONST kind, which the reference does not name (its CHOICE 3, pre-dating this arc).
    That is a declared limitation of a party, not a post-hoc equivalence.
- **Commit-reveal:**
  1. Archaeon posts the sha256 of its two outputs.
  2. The owner posts theirs.
  3. SEALED hashes are committed before either side opens the other's output.
- **On failure:** classify every discrepancy; no canonicalization; repair means re-freeze plus a fresh set.
- The fixture pack stays a separate owner gate (28/28).
