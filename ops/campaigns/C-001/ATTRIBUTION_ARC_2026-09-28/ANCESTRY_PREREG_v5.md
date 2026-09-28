# Byte-level ancestry replays -- preregistration v5 = v4 + the replacements below (Archaeon, 2026-09-28)

- **Basis:** adversarial Review 6 (review6/REVIEW_6.md; REVIEW_6_ADJUDICATION.md). It replayed v4's drawn run r025144 exactly
  (92/92 rows) and showed that v4 returns BROKEN on it for reasons unrelated to ancestry. In short: a non-replicating sample; Q8c
  counting the performer and birth suppression; vacuous arms; whole-execution ctrl scope de-identifying ordinary task-performing
  replicators.
- **What stands:** everything in ANCESTRY_PREREG_v4.md (with Amendments A and B1) stands EXCEPT the sections replaced here. Where
  v4 and v5 differ, v5 governs.
- **Freezing:** v5 is frozen at the commit that adds it together with BEE_POPULATION_v5.json.

## R1 (replaces v4 s2.1): identification is INTERVENTIONAL; the label sets are reported, not gating
A written locus is IDENTIFIED iff:
1. **Provenance:** its data label is (ENTITY X, j) MOVE.
2. **Flip:** the path-preserving flip test (s4.1 with B1 and R4) does not FAIL it.
3. **Dependence:** in the single-interaction intervention arms (K = 8 draws each), randomising any source group OUTSIDE {X, the
   performer entity} changes that locus's value in 0 of K draws.
   - The source groups are: every other ENTITY's bytes, the INPUT bytes that were supplied, and (NPE) the persisted registers.
   - A draw in which the write or the birth is suppressed counts toward Q8c-whether, not here.

ctrl_deps (both scopes), addr_deps and exec_deps are still exported and reported. They are a declared over-approximation; they do
not gate identification. Consequence: a task-then-copy replicator whose copy does not depend on the input is identified (Review 6
s1.1).

**NO_MATERIAL class:** births with <= 10% ENTITY-labelled written loci are reported as their own class and excluded from the
identifiability denominator.

**Class key:** the majority performer entity over written loci (self = the executing organism / other entity / none). A class with
0 rule-identified loci is "not gated".

## R2 (replaces v4 Q8c): value dependence outside {donor, performer}
- Q8c per written ENTITY-MOVE locus = Pr over K = 8 draws (randomising the source groups outside {data-label entity, performer})
  that the locus VALUE changes, among draws in which the write occurs.
- Q8c-whether (write/birth suppression) is reported separately and never enters Q8c.
- CONSTANT/COMPUTED loci get their own estimand, Q8c-nonmove: randomising each ENTITY in turn, with the same rules. It is
  reported and does not gate.
- Estimand: the mean over loci, with a birth-clustered bootstrap CI (run-clustered for NPE).

## R3 (replaces v4 s2.4 verdict rules), precedence INSTRUMENT_FAILED > SPEC_DEFECT > BROKEN > INCONCLUSIVE > ALTERED > VALIDATED
- **INSTRUMENT_FAILED, SPEC_DEFECT:** as in v4.
- **BROKEN:** ONLY a named channel absent from s1, reproduced by a fixture, that the policy cannot represent.
- **INCONCLUSIVE:** fewer than 80% of non-NO_MATERIAL births are identifiable (>= 90% of written loci identified) for a by-design
  Q, OR the transmission class (R5) has fewer than 30 births.
- **ALTERED:**
  * DOMINANT if the Q8c lower 95% bound > 50%;
  * WEIGHTED if the lower bound >= 5%;
  * or a prediction with an ALTERED consequence decides so.
  All three name the v0 field required.
- **VALIDATED:** the Q8c upper bound < 5%, AND every by-design Q is expressible in v0 plus the agreed extensions, AND the
  round-trip check passes.

## R4 (amends v4 s4.1): opcode-equivalent flips
- A flip that changes an opcode byte keeps the path "preserved" if the two opcodes are semantically equivalent.
  * In BEE: both undefined (NOP), or both the same defined opcode (this happens only for operand-free bytes).
- The store-address sequence includes OUT stores.
- IN pad bytes (beyond the supplied inputs) are (CONST, "in_pad").

## R5 (replaces v4 s4.2 arms and adds the transmission class)
- **TRANSMISSION class:** births whose written loci are majority IDENTIFIED (ENTITY writer) MOVE. Predictions P1, P2 and P5 are
  evaluated ONLY on this class.
- **Per-byte completeness:** for a random 20% of sampled births, randomise each single byte NOT named in any of the locus's sets,
  one at a time, K = 4. Share of such bytes that change the locus value with the path and the birth preserved: <= 5% per class.
- **Per-byte precision:** for the same births, randomise each single NAMED base-label byte, K = 4. Share that ever change the
  locus value, the write or the birth: >= 20% per class, else OVER-TAINT -> INSTRUMENT_FAILED (unless a fixture shows it is
  required).
- The whole-entity arms of v4 s4.2 are dropped: Review 6 measured them as vacuous (0.992 for an over-taint mutant).

## R6 (replaces v4 s5 BEE): the run is drawn from the relevance-screened population
- **Population (committed WITH this file):** BEE_POPULATION_v5.json, built by archaeon/attribution/bee_run_population_v5.py.
  * 53 of the 73 v4-cell runs have >= 30 births with row field 8 >= 32 and row field 9 >= 32.
  * This screen is a relevance condition only and never enters a measurement.
- **Draw (a later commit):** seed = this commit's full SHA; index = sha256(seed) mod 53.
- **Pre-committed fallback:** if the drawn run's TRANSMISSION class (R5, computed by the owner's replay) has fewer than 30 births,
  take index + 1 mod 53, and so on, recording every step.
- r025144 is withdrawn (non-replicating; Review 6). There is no second draw.
- NPE is unchanged: all pair interactions in the 11 T-003 runs.

## R7 (amends v4 s6): predictions
- Each prediction names its decision locus set (IDENTIFIED loci of TRANSMISSION-class births), its interval (birth-clustered
  bootstrap 95%), and its treatment of NONE/TIED (excluded from the denominator and counted separately).
- P1 (Q-homology), P2 (Q2) and P5 (Q8c) are evaluated on the TRANSMISSION class only.
- P2 "holds" iff the lower bound >= 10%; it is "certified" iff the upper bound < 10%; otherwise INCONCLUSIVE.

## R8 (amends v4 s3, s1.3)
- Pins are "sha256 prefixes", not git blob ids.
- The per-tick RNG-state hash is a self-consistency record (the preserved runs stored rows only).
- Per birth, export mechanism flags: LDIR entered with C == 0 (wrap), in-window source, budget-ended.
- exec_deps scope is stated: every fetched byte from interaction start UP TO the store (reported), and over the whole
  interaction (also reported).

## Amendment C1 (2026-09-28, found in Archaeon's dry-run smoke test on r025144): the precision arm's scope
- **Inconsistency:** R1 makes ctrl_deps, addr_deps and exec_deps non-gating, declared over-approximations. But R5 still made
  per-byte precision over those sets gate INSTRUMENT_FAILED. On r025144, per-byte precision over the full sets is 0.096 (the
  whole-interaction exec_deps name many bytes that change nothing), so any honest tracer would be INSTRUMENT_FAILED.
- **Change:**
  * per-byte precision over the dependence sets is REPORTED (it measures how over-approximate they are);
  * the gating precision test applies to the DATA label only, and is already the flip test (s4.1);
  * per-byte completeness (<= 5% leak) remains gating.

## Amendment C2 (2026-09-28): readings adopted from the independent reference tracer's SPEC_ISSUES
The reference tracer (reftracer/ref_tracer_bee.py; reftracer/SPEC_ISSUES.md) was written by an isolated worker from the prereg text
alone. Archaeon's tracer initially disagreed with it on addr_deps (0.25% of loci) and ctrl_deps (0.9%). Both disagreements were
genuine text ambiguities. The reference's readings are adopted and are now normative:
- **CHOICE 5:** every value carries an addr set. Pointer dependence is TRANSITIVE through memory and computation. A condition's
  and a fetched byte's dependence includes the value's addr set.
- **CHOICE 3:** CONSTANT labels are not members of dependence sets.
- **CHOICE 9:** input-region bytes beyond the supplied inputs are CONSTANT scratch; IN reads the byte's CURRENT label.
- **IN/OUT counters:** the counter's label is the PC label at that point; it acts as the load pointer (IN) or store pointer (OUT).
- **CHOICE 1/2 (scope):** both are reported. Agreement is measured on the at-store sets and the whole-interaction sets.
After the change the two tracers agree on 100.0% of loci on EVERY field (data, addr, ctrl at store, exec at store, performer,
written) over 33,792 loci: the 29 fixtures, 300 fuzz interactions and 200 mutated replicators (TRACER_AGREEMENT.txt). The
fixture pack still passes.

Limits recorded from the same list:
- **FLIP-8:** the flip test cannot certify control-only recreation (K31). Only the fixture expectation rejects a tracer that
  MOVE-labels it.
- The mutation-testing items "ctrl omits the OUT guard / region-exit" are semantic no-ops in BEE SHARED (the counter's label IS
  the PC label), so they are undetectable there by construction.
- Pins are sha256 prefixes of file contents (git blob of vm.py is 91d8516c).

## Amendment C3 (2026-09-28, made AFTER the BEE dry-run data; flagged): P2's evaluation set
- **Defect:** R7 evaluates P2 on the TRANSMISSION class, which is defined as writer-majority. Every "target"-labelled birth in that
  class therefore disagrees with copy-descent by construction.
- **Change:** P2 is evaluated on ALL identifiable births whose native label is "target" (v4's original wording).
- **This amendment follows the data** (DRYRUN_BEE_r022153.md). It is admissible only because the outcome is the same under both
  readings (HOLDS: 57% vs 100%). It is recorded so that no reader mistakes it for a pre-data choice.

## Amendment C4 (2026-09-28; after Archaeon's BEE dry run and Review 7, BEFORE any production data; flagged)
1. **Q8c-whether is REQUIRED per birth and per class.** It is the share of draws in which randomising a source group, the
   PERFORMER INCLUDED, suppresses the write or the birth. It is exported as a v0 DEPENDENCE entry: intervention "randomise <group>",
   outcome "birth/write occurs", result ceases / persists, with the rate.
   - It does not gate. v0 represents it; a verdict would only change if v0 could NOT represent it.
   - Reports say "Q8c measures value dependence outside {donor, performer}; existence dependence is Q8c-whether".
2. **ALTERED routes must name an attribution-v0 field** (R3). A prediction whose consequence concerns an engine's NATIVE label
   (P2) is reported as an engine-native finding, not as a verdict route.
3. **Label-vs-descent comparisons are never evaluated inside the TRANSMISSION class** (generalising C3). They use all
   identifiable births, and also all births with a W or P copy-descent majority. The transmission class remains for P1 and P5.
4. **Per-class gates** (flip coverage, completeness) use the POINT estimate against the floor, with the 95% CI reported. A class
   whose CI straddles the floor is marked MARGINAL in the report.
5. **Q4 adds a HOST-ASSISTED test:** the child as a writer against 8 random occupants taken from the run's own self-performed
   children (real hosts) x 40 inputs. This separates "incapable" from "capable only with a host". The isolated test stays primary.
6. **Painting guard:** per-birth source diversity is exported. P1 and Q8c are also reported excluding births with source
   diversity < 0.5 (fills and paints).
7. **Pipeline obligations** (production and any dry run):
   - the flip test on every sampled birth's identified loci, with per-class coverage;
   - Q8c-whether computed;
   - the verdict computed in code, from the stated rules;
   - every number in a report traceable to a committed output file.

## Amendment C5 (2026-09-28): NPE cell readings N1-N7 (Nestor comms #832), ACCEPTED before any NPE production
The 11 T-003 runs share one cell: Z8_32 (L = 32), PAIR_TAPE x PAIR_EXECUTION, RESERVOIR, BYTEWISE copy primitive, PC_RELATIVE
self-location, OPCODE/LOCAL mutation, ops mask 0x0C (GETPC and SENSE only). Several v4 NPE clauses assumed a different NPE world.
Adopted:
- **N1 unit:** ONE pair interaction = slice of a + slice of b on the 64-byte tape + the harness write-back of each half (with
  mutation).
  * A "birth" = a P-11 predecessor acceptance of a half.
  * victim = that half's organism (it keeps its slot and its persisted registers); donor/writer = the other organism.
  * This replaces "victim = the slot displaced by ALLOC" (no ALLOC exists in this cell).
- **N2:** SENSE returns the side (0/1), a harness constant -> (CONTEXT, "SENSE_side"), FOREIGN-STRUCTURAL.
- **N3:** no task inputs; IN -> (CONSTANT, "in_exhausted"); the INPUT group is empty; Q-input is INAPPLICABLE.
- **N4:** inapplicable in this cell:
  * K20 (in-VM noise; LDIR/LDDR disabled);
  * mate / recombination labels (no recombination);
  * the OTHER group (the tape holds only the two halves).
  Slot-tail clearing is labelled but never changes a byte.
- **N5:** applicable: persisted registers/flags across interactions; GETPC CONTEXT (K29); write-back mutation with a
  decode-dependence set (K28); residue-only acceptance (K30); performer can be either entity (K21/K25).
- **N6 scale:** the tracer runs on all ~2.8M interactions; full s3 exports go to birth-producing interactions plus the
  P4-eligible non-accepted ones; the intervention arms run on the s4 sample.
- **N7:** Q4 via Odysseus recert; Q5 not built (NPE reports it as omitted).

**NPE fixtures:**
- Nestor drafts the semantics AND the Z8 images (expectations as data).
- Archaeon validates them with the flip test and interventions on NPE's world code, and ADDS adversarial fixtures of its own
  before production.
- An NPE reference tracer is written by an isolated worker from the prereg text (with this amendment) alone. The three-way
  agreement rule (v4 s4.3) applies to NPE as to BEE.

**Pin data:** the full T-003 hashes are committed in NPE_T003_HASHES.txt (result_sha256 efba5535...18bc; per-run lineage_sha256).
Observation for Nestor: in two runs (s9200006, s9200008) the C_reimplant_random arm has the SAME lineage_sha256 as A_in_situ.

## Amendment C6 (2026-09-28): NPE readings, adopted from the independent NPE reference tracer BEFORE Nestor's tracer exists
- **Source:** the reference tracer npe_reftracer/ref_tracer_npe.py was written by an isolated worker from the prereg text + C5
  alone. It reproduces world.Runner._pair_interact exactly (60 real interactions: halves, RNG state, registers, acceptance; plus
  300 fuzz interactions).
- **Why now:** its SPEC_ISSUES.md lists where conforming tracers could legitimately differ. To keep the three-way agreement gate
  (v4 s4.3) from failing on ambiguity rather than error, these readings are NORMATIVE for NPE.
- **Independence:** Nestor implements from THIS TEXT. Nestor should not read the reference code before the first agreement run.

**Entities, performer and class:**
- **A4:** entities are the two organisms, ('ENTITY', 'a'|'b', j, orig_id).
  * Every pre-state byte is re-based to ENTITY(side, j, orig) at interaction start (single-interaction scope).
  * orig_id comes from the persisted per-locus vector (default: the side name).
- **A5:** both are exported: store_by (the slice's organism) and performer (the material data label of the store's opcode byte,
  captured at fetch). The NPE class key = the performer's ENTITY (or none).
- **A6:** persisted registers and flags carry their own base-label kind ('PREG', side, reg).
  * PREG is FOREIGN-INFORMATIVE for identification: it is the "persisted registers" source group of R1.
  * A first interaction after placement gives CONST('reset').

**Label algebra:**
- **B1:** the logic ops' carry flag is CONST('logic_nc').
- **B2:** idioms = XOR A,A; SUB A,A; CP A,A (flags constant).
- **B3:**
  * INC/DEC r -> COMPUTED_FROM;
  * INC/DEC (HL) -> COMPUTED;
  * 16-bit INC/DEC: low byte COMPUTED_FROM, high byte COMPUTED{hi, lo};
  * nested labels are flattened.
- **B4:** COMPUTED with no non-constant base stays ('COMPUTED', {}) (new material, not CONST).
- **B7:** IN -> CONST('in_exhausted'), with addr = the PC label at the IN.
- **B8:** OUT has no locus. OUT events enter the flip test's store sequence as ('OUT', who, k).

**Dependence sets:**
- **C1:** PRIMARY ctrl_deps = the PC label accumulated from INTERACTION start (b's stores inherit a's conditions). Also exported:
  ctrl_deps_slice, ctrl_deps_pdom, ctrl_deps_whole.
- **C2:** exec_deps from interaction start up to the store (inclusive), plus exec_deps_whole.
- **C3:** the post-dominator scope (secondary) as defined in npe_reftracer/SPEC_ISSUES.md C3:
  * CFG decoded at branch time; HALT -> EXIT; no budget edges;
  * a Xin-Zhang-style stack, reset at slice entry.
- **C4:** addr sets are transitive (as C2 CHOICE 5).
- **C5:** pointer labels include both pointer bytes, ignoring the address mask (a declared over-approximation).
- **C6:** CONTEXT IS a member of dependence sets (only CONSTANT is excluded).
- **C7:** fetched bytes = bytes the engine actually reads (the IN/OUT operand is not read; the LD SP,nn operand and a disabled ED
  second byte are read).
- **C8:** written = any store in the interaction; the per-locus record describes the LAST store.

**Performer and mutation:**
- **D1:** the performer is the full data label of the store opcode at fetch. performer_entity = None if it is not ENTITY.
- **E:** write-back mutation per world.py:484-550, labelled MUTATION(draw, old_label) at the draw, with the decode-dependence set
  = the labels of the linear-decode boundaries of the PRE-mutation half.
