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

## Amendment C7 (2026-09-28): NPE rulings (Nestor comms #839, #840, #844), the pdom text, and fixture validation
1. **C3 post-dominator scope (secondary, non-gating).** The definition, verbatim from npe_reftracer/SPEC_ISSUES.md, so the owner
   need not read the reference directory:

   > **C3 [DIVERGE, big] Post-dominator scope for self-modifying code on a wrapping tape.** "Standard dynamic control-dependence
   > scope" is not defined for this setting. My definition:
   > - **CFG:** the 64 tape addresses, decoded from the tape contents AT THE MOMENT the branch executes. HALT goes to EXIT. Jump
   >   targets are masked to 6 bits.
   > - **Budget:** the step budget is NOT an edge, because it is CONSTANT (v4 s1.3).
   > - **Unreachable EXIT:** a node that cannot reach EXIT gets ipdom None, so its scope lasts to the end of the slice. Typical
   >   evolved code never HALTs, so for it pdom scope == slice scope.
   > - **Stack:** Xin-Zhang style. A new entry with the same ipdom as the top is merged into it. Entries are popped only from the
   >   top, when pc == ipdom. The stack is reset at slice entry. Branches with empty condition deps are not pushed.
   > 
   > Alternatives, each giving different `ctrl_deps_pdom`:
   > - budget edges from every node to EXIT (then pdom scope always equals slice scope);
   > - a CFG snapshot taken at slice start;
   > - popping deeper entries;
   > - a static CFG over the half only.
   > 
   > F3/F8 show the standard implicit-flow miss: after the join the pdom scope is empty.

   Nestor may build ctrl_deps_pdom after production starts. It is non-gating.

2. **The prefix-preserving flip test (BOTH engines; replaces the strict applicability rule of s4.1/B1/R4 as the GATING rule).**
   - **The rule:** a bit flip is APPLICABLE iff (a) the fetch trace, store-address sequence and load-address sequence are
     unchanged UP TO the last store to that locus in the baseline, AND (b) the counterfactual makes no later store to that locus.
   - **Why it is sound:** the locus's final value is its last store's value, so divergence after that store cannot reach it.
   - **Why it is needed:** in NPE, a 32-byte replicator on the wrapped 64-byte tape keeps executing into the bytes it copied. Under
     the strict rule every copied locus is INAPPLICABLE (Nestor #839: 0/64 coverage on the smoke births), so NPE would be
     INCONCLUSIVE by construction.
   - The strict rule is still reported alongside.
   - The BEE dry run used the strict rule. The prefix rule can only raise coverage, so BEE's coverage passes a fortiori.
   - The residue, where copied bytes are executed BEFORE they are stored (data = code), stays INAPPLICABLE. It is irreducible for a
     flip test.
3. **Reconciliation items:** all accepted as consistent with C6.
   - N-a: interaction-start accumulation.
   - N-b: INC/DEC rr split.
   - PREG_a and PREG_b are two source groups.
   - Q8c is pooled over (group, draw), with per-group counts exported.
   - The arms compare the victim half BEFORE the write-back mutation (MUTATION loci are never MOVE, and the RNG cannot be held
     across a changed decode).
4. **DEFECT C9-D24 (#840):** in T-003's 11 runs, s9200006 C and s9200008 C duplicate their A arms. So there are 9 distinct
   simulations, and 29 distinct births out of 34.
   - Decision statistics use a run-clustered bootstrap over the 9 distinct simulations, with duplicates removed.
   - The duplicates are reported.
5. **Fixture validation:**
   - Nestor's 23-fixture NPE pack (nestor/s1-forensics-2026-09-23, 279beb9c8) was checked expectation by expectation against the
     INDEPENDENT reference tracer (archaeon/attribution/probes/npe_fixture_validate.py; npe_fixture_validation/VALIDATION.txt).
   - Archaeon added 11 adversarial expectations for the thinly covered mutants exec_all, noexec and performer_by_location
     (npe_fixture_validation/ARCHAEON_ADDITIONS.json).
   - **Result: 391/391 agree.** The pack is VALIDATED, and the additions become part of it.

## Amendment C8 (2026-09-28): NPE gates G1 and G2 (Nestor #847); arbitrations A1 and A2
**G1 (fixtures): CLEARED.**
- Nestor's v2 pack (646166c9f; 26 fixtures including the new K16b, K16c and K37 painting, plus Archaeon's additions) agrees with
  the INDEPENDENT reference tracer on 451/451 expectations (npe_fixture_validation/VALIDATION_v2.txt).
- Nestor reports his mutants are caught 3-22 times each.

**G2 (tracer agreement, pre-production).**
- Setup: Nestor's tracer, FROZEN at e5af0cae1, vs the reference, on 300 non-production fuzz interactions (seed 20260929;
  archaeon/attribution/probes/npe_fuzz_agreement.py; npe_fixture_validation/G2_AGREEMENT.txt).
- **Raw agreement:**
  * addr, ctrl (primary), exec, store_by, written: 100% in every class;
  * data labels: 549/587 written-self and 296/320 written-other;
  * performer: 31/33 performer-none;
  * ctrl_slice (secondary): 570/587 and 31/33.
- **A1 (arbitration):** the label disagreements are COMPUTED_FROM(COMPUTED{S}) (Nestor) vs COMPUTED{S} (reference).
  * The reference's SPEC_ISSUES B3 states the flattening "CF(COMPUTED S) = COMPUTED S". Archaeon's C6 summary said only "nested
    labels are flattened": the ambiguity is Archaeon's, not Nestor's error.
  * The two readings are semantically identical: non-MOVE new material with the same base set. Both give the same
    identification, class and every Q.
  * Ruling: canonical equivalence for the gate. The C6 text is clarified: CF(COMPUTED S) = COMPUTED S.
- **A2 (arbitration):** the performer disagreements are the name of a constant idiom ('idiom' vs 'XOR_AA') and COMPUTED_FROM over
  a constant.
  * C6 never named idiom kinds. CONST kinds are not compared, and CF(base-less) = CONST.
- **Gated fields** (data label, written, store_by, performer, addr, ctrl, exec) under A1/A2: **100% in every class. G2 CLEARED.**
- **Reported, not gated:** ctrl_deps_slice (secondary) differs on 19 loci. The reference includes pointer-carried PREG/entity
  bases of the other half in the slice-scoped label. v5 gates only the primary ctrl. The difference is recorded for the pdom and
  slice-scope work.
- **Review:** A1 and A2 are to be reviewed by the independent final reviewer before synthesis, with both raw readings in the
  record. Nestor does not change his frozen tracer.

## Amendment C9 (2026-09-28; operator directive "CLOSE THE INDEPENDENCE GATES"; made AFTER seeing the G2 discrepancies; flagged)
**1. C8's G2 "CLEARED" is WITHDRAWN.**
- A1 and A2 were canonical equivalences adopted AFTER the discrepancies were seen. Under the prereg rule (v4 s4.3: data label +
  the three dependence sets, >= 99.5% of loci per class) they are a POST-AGREEMENT-TEST REPAIR, not an arbitration.
- They are not applied to any gate. C8's G1 text stands; G1 is re-run below as required.
- My production GO (comms #845) and C8 clearance (#848) are withdrawn with it. Nestor's production hold was correct.

**2. G1 (re-run, fixture by fixture; frozen reference 3757111de; gate_close/G1_FIXTURES_K16b_K16c_K37.json):**
- **K16b: PASS.** The locus a[10] = 0x42 has label ENTITY a2. It was stored in slice b (store_by = b), at pc 56, which is in b's
  half. The opcode byte there was copied from a[1], so performer = a1 and performer_entity = a. The fixture separates performer by
  material (a) from store location (b) and from store_by (b), and the reference follows the material.
- **K16c: PASS.** The locus a[12] = 0x55 has label ENTITY b25. It was stored by slice a, at pc 24, which is in a's half. The
  opcode byte came from b[24], so performer = b24 and performer_entity = b. Material b is separated from store location a and
  store_by a.
- **K37: PASS.** 8 written loci a[8..15], each 0xA0, each with label ENTITY b16. There is one store instruction (pc 41 = b[9]), one
  performer (b9) and one value.
  * Diagnostics only: distinct sources 1/8, instructions 1, values 1, performers 1, Hill effective sources 1.
  * The causal machinery is one source painting a region, not 8 inherited sources.
- **Coverage note:** neither K16b nor K16c separates store LOCATION from store_by (the two coincide in both). No fixture
  asserts on that axis. This is not a defect.
- **G1 PASS.**

**3. G2 RAW (gate_close/G2_RAW_AGREEMENT.txt, G2_DISCREPANCIES_RAW.jsonl; archaeon/attribution/probes/npe_gate_close.py).**

Prereg fields, per class (class key = the reference's performer class; the Nestor-classed table is identical):

| class | label | addr | ctrl | exec | written | store_by | performer | ctrl_slice (secondary) |
|---|---|---|---|---|---|---|---|---|
| unwritten (18,260) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -- | -- | -- |
| written_self (587) | **0.9353** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9710 |
| written_other (320) | **0.9250** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| written_perf_none (33) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9394 | 0.9394 |

Directive categories (descriptive; they neither rescue nor replace the gate):
- source locus and identification input (ENTITY side, src): 1.0000 in every class;
- class key: 1.0000;
- carry/flag-involving loci: 0.9310 (self) / 0.9524 (other) / 1.0 (none). The failures are the label shapes below.
- Not exercised by this set, so INCONCLUSIVE:
  * MUTATION (no write-back in the export);
  * IN (0 loci; the op mask 0x0C set produced none);
  * OUT (no locus by C6 B8);
  * pdom scope (Nestor's export has no ctrl_pdom; non-gating, C7.1);
  * existence dependence (interventional, Q8c-whether; engine-measured, not a tracer field).

**G2 FAIL** (written_self label 0.9353 and written_other label 0.9250, below 0.995). 83 discrepant loci.

**4. Disagreement classification** (every disagreement; minimal synthetic reductions in gate_close/G2_MINIMAL_CASES.json, with the
reference's reading only):

| shape | loci | Nestor | reference | category | reduction |
|---|---|---|---|---|---|
| S1 | 24 (23 labels + 1 performer) | CF(COMPUTED S) | COMPUTED S | (1) spec ambiguity | D1 |
| S2 | 40 (28 CONST labels + 11 CF(CONST) labels + 1 performer) | CONST('idiom'), CF(CONST('idiom')) | CONST(XOR_AA / SUB_AA), CF(CONST(...)) | (1) spec ambiguity | D2, D3 |
| S3 | 19 (ctrl_slice, secondary) | a STRICT SUBSET of the reference's set in 19/19 | superset (adds bases carried transitively by branch-condition values) | (1) spec ambiguity; (5) if it persists after s5 | D4 (hypothesised) |

- **S1:** C6 B3 says only "nested labels are flattened". The reference's SPEC_ISSUES B3 says CF(COMPUTED S) = COMPUTED S. The
  ambiguity is in Archaeon's C6 summary.
- **S2:** C6 B2 lists the idioms but never names the CONST kinds.
- **S3:**
  * C6 C1 names ctrl_deps_slice without defining whether a branch condition's transitive addr set, built in the other slice,
    enters it. D4 is a hypothesised reduction.
  * If Nestor's frozen tracer agrees with the reference on D4, S3 is unreduced, and the fuzz records (k = 4, 32, 111, 118, 139,
    195) remain its counterexamples.
- **No disagreement is classified (2) Nestor implementation error, (3) reference error or (4) malformed interaction.**
  Total 24 + 40 + 19 = 83 discrepant loci (no locus in two shapes). Source locus, identification input and class key agree 100%. That is a DESCRIPTIVE finding, not a gate.

**5. Repair: post-agreement-test, recorded as such.**
- **(a) Normative spec clarifications**, chosen per C6's rule that the reference's readings are normative:
  * CF(COMPUTED S) := COMPUTED S;
  * CF over a CONST is kept as CF(CONST k);
  * idiom CONST kinds are exactly 'XOR_AA', 'SUB_AA', 'CP_AA';
  * ctrl_deps_slice := the same accumulation as the primary ctrl_deps (each branch condition's label bases plus its transitive
    addr set), over branches executed in the storing slice, reset at slice entry.
- **(b)** The comparison rule is unchanged: RAW equality under v4 s4.3. There is no canonical equivalence and no threshold
  change.
- **(c) Re-freeze.**
  * Nestor revises his tracer to (a), then re-freezes it (new TRACER_FREEZE hashes).
  * The reference is not modified. Its sha256 is re-attested:
    2851bcdb6cc9a074db3b0338b663c1dec6b533a22b2e34c0cb522ac69de2a4e2 (LF-normalized).
- **(d) Fresh set.**
  * archaeon/attribution/probes/npe_fresh_set.py is committed with THIS amendment, before its seed exists.
  * Seed = the full SHA of the commit recording both re-freeze hashes.
  * Set A: 300 interactions, compared before write-back. Set M: 100 interactions with write-back, which adds the MUTATION class.
  * The pre-state file's sha256 is posted first.
  * Each side posts the sha256 of its output before the outputs are exchanged.
  * Same bar, per class, raw. The D1-D4 cases are traced by both sides alongside, as counterexample checks (not gated).
- **(e)** If the fresh set fails, production stays forbidden and s4's procedure repeats.

**6. Production: HOLD.**
- **Reason:** G2 FAIL under the preregistered rule; the repair and the fresh-set rerun are pending.
- ANCESTRY_REPLAY_PRODUCTION_GO_FINAL is written only after:
  * G1 PASS (done);
  * a fresh-set G2 PASS;
  * matching freeze hashes;
  * G3 and G4 still clear.
- **It binds:**
  * Nestor's tracer freeze hash;
  * the reference hash;
  * the fixture-pack hash (npe_fixtures.py 25c8507e51acbf6b2c02690ccfb889c54af4477a31a34ac3fe6f2b9cfe18c644, plus
    ARCHAEON_ADDITIONS.json 1753023ca4f5f168860c2610f1ef3dc183f4f3d170f9e2715c7394d76297b012);
  * the spec hash (this file, at the commit that carries C9);
  * the experimental unit (9 simulations / 29 births, C7.4);
  * the flip rule (C7.2);
  * the agreement result;
  * the production code hash (run_production.py).

**7. The 1% production agreement sample (~28k interactions, ~115 MB) is NOT in git.**
- This replaces my orphan-branch suggestion (#848). The transfer:
  1. Nestor writes it outside any repository and posts its sha256.
  2. It is copied (scp) to M2 C:/Prometheus-data/evidence/attribution_arc_2026-09-28/npe_sample/.
  3. Archaeon verifies the sha256 BEFORE opening it.
  4. The frozen reference runs on it.
  5. The result artefact is hashed.
  6. Only receipts (hashes, counts, per-class agreement) enter git.
- The sample is fixed by Nestor's hash before transfer. It is not reduced after anything is seen.

## Amendment C10 (2026-09-28; after the FRESH-set exchange; post-agreement-test repair, flagged)
**1. Fresh-set G2 result.**
- Seed d33421a07; 400 pre-states, sha256 e37bdd48; declaration committed before either output was opened (30e39ced5).
- Reference 3757111de vs Nestor v2 fb1c322cb.
- Two INDEPENDENT raw comparisons (Archaeon: npe_fresh_compare.py, committed before opening -> gate_close/fresh_result/;
  Nestor: compare_fresh.py at 33a4ab5a1) give the SAME numbers.
- **Set A: PASS.** label, addr, ctrl and exec are 1.0000 in every class:

  | class | loci |
  |---|---|
  | unwritten | 17,790 |
  | written_self | 812 |
  | written_other | 558 |
  | written_perf_none | 40 |

  written, store_by and performer are also 1.0000.
- **Set M: FAIL.**

  | class | label | addr |
  |---|---|---|
  | unwritten | 0.9650 | -- |
  | written_self | 0.9641 | 0.9681 |
  | written_other | 0.9579 | 0.9579 |

  * Every failure is on a MUTATION locus. Non-mutated M loci: 1.0000.
  * Declared diagnostic d2 (MUTATION flag, side, pos, old_label): 225/225.
- **G2 remains FAIL. Production remains FORBIDDEN.**

**2. Classification of the set-M disagreements** (all category (1), specification ambiguity):
- **(a) MUTATION draw index (225 loci; declared before the exchange).**
  * The reference's SPEC_ISSUES E3 defines it: (side, k, pos), where k = the RNG calls since the start of this interaction's
    write-back, a's half first, counted at the position's random() draw.
  * Archaeon's C6 E summary omitted E3.
- **(b) MUTATION addr set (16 loci, all written and then mutated; found by Nestor AFTER the exchange, flagged by him).**
  * The reference carried the pre-mutation store's addr set; Nestor gives the empty set.
  * No text defined it.

**3. Rulings (normative from here on):**
- **(a) The draw index = SPEC_ISSUES E3,** consistent with C6's rule that the reference's readings are normative. Nestor revises
  (v3).
- **(b) The MUTATION addr set = EMPTY.**
  * Grounds: the mutated byte is a uniform draw at a fixed position, so no pointer selects it. Its decode-dependence is
    exported separately in the mutation event (E4).
  * This ruling goes AGAINST the reference's behaviour. The reference is therefore repaired: one line after the write-back
    relabel, plus SPEC_ISSUES E6.
  * Its selftest passes, and the fixture pack still gives 451/451.
  * New reference sha256 (LF): 157374444597750fe114602cd83fa02faa36048161889b06f15e40d4ec7d7368.
  * **Flagged for the independent final reviewer:** the reference owner changed the reference after seeing the owner's
    reading. The change is confined to MUTATION addr sets.

**4. S3 (ctrl_deps_slice, secondary, non-gating): DIAGNOSED. Category (1).**
- Per-step condition logs for set-1 k=4:
  * Nestor #864, posted blind;
  * Archaeon, from a runtime-instrumented COPY of the reference (the frozen file was not touched).
- Both agree on every branch condition: b's pc-5 {b25, PREG(b.H), PREG(b.L)} and pc-33 {b14, PREG(b.H/L/A)}.
- **The whole difference is the IN instruction at pc 62.**
  * The reference treats IN's input-cursor guard as a condition. Its label is the IN counter label, which C6 B7 / reference C2
    set to the interaction-wide PC label at the IN. The guard therefore carries a's conditions into b's slice scope.
  * Nestor's tracer does not count that guard as a slice-scope condition.
  * In the primary scope this is a no-op. That is why the primary ctrl agrees 100% while ctrl_slice equals the primary on the
    19 set-1 loci.
- **Minimal counterexample D6:** a branches; b's slice executes only IN, then stores. The reference's slice set = a's deps;
  under Nestor's reading it would be empty.
- This touches the IN/OUT class. It stays an OPEN, recorded, non-gating disagreement. Neither tracer is changed for it.

**5. Repair procedure:**
1. Nestor re-freezes v3 for (a); for (b), if his v2 already gives the empty set, no change.
2. A new seed record holds both new freeze hashes.
3. A FRESH set 2 (A 300 + M 100): the same generator, the new seed, the same declaration.
   - The raw gate applies to BOTH sets, because both tracers changed.
   - Commit-reveal as before.
- **Exchange serialization for (a), fixed now so the raw comparison is defined:** MUTATION label = ["M", [side, k, pos],
  old_label], where side is "a" or "b", k follows E3 and pos is 0..31. Archaeon's exporter (npe_fresh_ref.py) is updated to it.
