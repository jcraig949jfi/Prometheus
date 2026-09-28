# Byte-level ancestry replays (BEE, NPE) -- preregistration v3 (Archaeon, 2026-09-28)

**History.** v1 was found UNSOUND by Review 3; v2 was found UNSOUND by Review 4 (review4/REVIEW_4.md; REVIEW_4_ADJUDICATION.md). Both
are superseded before any execution and kept unedited. v3 is frozen at the commit that adds it; later changes are dated
amendments at the end.

**Terminology.**
- "Copy-descent" = where-provenance lineage under the tracer's move set. It is NOT population-genetic identity by descent.
- "Implicit flow" is Denning's term. ctrl-taint here is a tainted-PC policy with no declassification, and it over-approximates.

## 0. Division of labour
- **Owners** (Bellerophon for BEE, Nestor for NPE):
  * build a NEW observation-only shadow tracer implementing s1;
  * reproduce the preserved birth log bit-for-bit;
  * pass the fixture pack (s4.1);
  * run the provenance tests (s4.2) on their production sample;
  * export s3.
  NPE's z8taint niche tags do not satisfy s1.
- **Archaeon:**
  * commits the FIXTURE PACK before production. For BEE: exact memory images, entry, budget, inputs and full expected label
    vectors, each expected vector validated by the per-byte flip test on the frozen VM. For NPE: exact semantics per fixture;
    Nestor writes the Z8 images, and Archaeon validates them with the flip test on NPE's world code before production;
  * writes an INDEPENDENT reference tracer for BEE that re-derives full label vectors on a random 1% of production births from
    the exported pre-execution states, and reports exact per-locus agreement with the owner's labels;
  * writes the synthesis.
- **An independent reviewer (not Archaeon, not the owner)** adjudicates every ALTERED / BROKEN / INSTRUMENT_FAILED trigger.

## 1. Label policy

**1.1 Data labels** (every memory byte, register and flag).
- **Start labels:**
  * executing organism locus i -> (ENTITY w, i, orig_id);
  * partner / occupant locus j -> (ENTITY o, j, orig_id), or EMPTY;
  * input byte k -> (INPUT, k);
  * scratch and other memory -> (OTHER, address);
  * BEE registers and flags -> RESET;
  * NPE registers and flags -> the label persisted from that organism's previous execution.
- **Reads:** the label of a read is the label of the byte read (IN included).
- **Stores:** every store updates labels, including OUT, per-byte sequential LDIR/COPYALL, and the harness's window, input and
  write-back stores.
- **Moves and operands:** moves carry the label. An immediate operand used as a value carries the operand byte's label.
- **Computation:**
  * COMPUTED_FROM(label) applies only to operations whose sole non-constant input is one register and which take no operand byte
    (INC, DEC; in NPE NEG and rotate);
  * ADD n, XOR n and every multi-input or non-bijective operation -> COMPUTED(flattened set of base labels);
  * result-independent idioms (XOR A,A; SUB A,A) -> (CONSTANT, instruction label).
- **NPE world operations:**
  * SELF / GETPC / ALLOC results -> (CONTEXT, op): non-material, reported;
  * SENSE -> (ENV);
  * the BIRTH/SPLIT harness write-back is a store carrying the slot bytes' labels, with mutation labels at the draw;
  * slot residue keeps its persisted ENTITY label.
- **Mutation:** MUTATION(draw index, old_label), assigned at the RNG draw. It is never assigned by diff or by value alignment
  (NPE `_mutated_orig` is forbidden).
- **Structural change:** moves carry labels positionally; an inserted byte is MUTATION.
- **Recombination:** a splice is ENTITY of the splice donor.
- **Persistence:** label vectors persist per organism after EVERY execution, refused write, mutation and migration.

**1.2 Dependence sets** (per child locus), with the scope fixed:
- `ctrl_deps`: base labels of the condition inputs of every conditional branch EVALUATED (taken or not) since execution start.
  This includes DJNZ, the LDIR/COPYALL C==0 exit and the budget stop.
  * Whole-execution scope is the primary.
  * Post-dominator-scoped ctrl_deps are reported as a secondary.
- `addr_deps`: base labels of the pointer registers used for the store to the locus AND for the load that produced its value.
- `exec_deps`: base labels of every opcode and operand byte fetched as an instruction since execution start (the PC-taint
  analogue).

**1.3 Forbidden as material evidence:** resemblance, source address, value match, execution context or code location. CONTEXT
labels are reported, never used as material.

## 2. Questions and verdicts

**2.1 Identification:**
- **RULE-IDENTIFIED locus:** the data label resolves (no UNKNOWN), AND ctrl_deps, addr_deps and exec_deps name no base label
  other than the data label's entity, INPUT/OTHER/RESET/ENV/CONTEXT included.
- **IDENTIFIED share:** estimated on the provenance-test sample (s4.2) as the share of rule-identified loci that ALSO pass the
  per-byte flip test, with a binomial 95% CI. For the other births, "rule-identified" is reported as such.
- **A birth is identifiable for a Q** iff >= 90% of its written loci are identified.

**2.2 Definitions:**
- **performer** = the material label of the opcode byte of the STORE instruction that wrote the locus (for LDIR/COPYALL, that
  instruction's byte). Path plurality is reported separately, excluding NOP-equivalent bytes.
- **majority donor** = the plurality entity over the loci in question. Ties -> TIED; empty -> NONE.
- **Every Q is computed twice:** over IDENTIFIED loci and over all written loci.

**2.3 Birth classes** (they replace the n_written strata; in ENDOGENOUS_COPY every birth writes all L loci):
- self-performed;
- occupant-performed;
- INPUT/scratch-performed (by exec_deps);
- each of these split into IMPLICIT or not.

**2.4 Questions:**

| Q | question |
|---|---|
| Q1 | performer != majority donor |
| Q2 | the native resemblance label (BEE `material`; NPE acceptance and anc/oid) names a different majority donor than copy-descent |
| Q3 | departure from uniparental inheritance: a second donor >= 10%, or new material >= 10% (MUTATION, CONSTANT, COMPUTED; COMPUTED_FROM counted to its source entity only when the transform has no other ENTITY contributor), or performer != donor |
| Q4 | material without capability. Capable = the child makes an exact self-copy in >= 50% of 320 isolated trials (8 random partners x 40 random inputs, frozen VM); the full distribution is reported. In-situ later SR is secondary. NPE: Odysseus recert behavioural test |
| Q5 | founder-material excess: the observed founder share minus the share in a NEUTRAL replay (the same births, with labels subject only to the run's mutation process at the run's own rate), with a CI; only where the expected share >= 0.05 |
| Q6 | co-execution by material: exec_deps entity composition of window-writing executions; OTHER/INPUT/RESET separate |
| Q7 | source diversity over ENTITY loci; COMPUTED share alongside |
| Q8r | rule-IMPLICIT share of written loci (descriptive only) |
| Q8c | counterfactual value dependence: on the s4.2 sample, the share of written loci whose VALUE changes when an entity other than the data-label entity is randomised, holding the data-label source bytes fixed, among draws in which the write still occurs |
| Q-input | the share of written loci whose value changes under the INPUT arm |

**2.5 Verdict per engine** (no pooling):
- **INSTRUMENT_FAILED:** the fixture pack or the s4.2 thresholds fail and a third-party reference tracer does NOT reproduce the
  failure on the same births (a tracer bug, not a finding).
- **BROKEN:**
  * the s4.2 thresholds fail AND the third-party reference tracer reproduces the failure (the policy cannot recover provenance by
    design); OR
  * the lower 95% bound of Q8c > 50% of written loci (value dependence outside copy-descent dominates).
- **ALTERED:** Q8c's 95% CI lies within [10%, 50%] (the v0 record needs a WEIGHTED dependence field), OR any s6 prediction whose
  stated consequence is ALTERED loses.
- **INCONCLUSIVE:** fewer than 80% of births are identifiable for a by-design Q.
- **VALIDATED:** none of the above, AND attribution-v0 plus the agreed extensions (s3) hold the results.

**2.6 By-design Q lists:**
- BEE: Q1-Q8c, Q-input.
- NPE: Q1-Q3, Q6-Q8c, Q-input; Q4 via recert; Q5 only if multi-generation ids are built (the owner states this before running).

## 3. Exported fields
- **Pinning:** the harness commit and module sha256. BEE frozen modules: world 5b985241, vm 2536b1ac, grammar 3767d73d;
  traced_replay's hard-coded Windows HARNESS path must be repointed, with the hashes logged at import. The run must reproduce the
  preserved birth log bit-for-bit.
- **Per execution:**
  * pre-execution state (full memory, registers, flags, entry pc, budget, inputs, RNG draw index and state);
  * for NPE: a birth's unit = the full slice sequence from ALLOC to BIRTH, with other organisms' slices as recorded.
- **Per birth:**
  * writer pre/post tapes and labels; child tape;
  * per child locus: data label, ctrl_deps (both scopes), addr_deps, exec_deps;
  * the full window write log; the performer; birth class; the mutation event list;
  * native fields verbatim; the Q4 result; the provenance-test results.
- **Agreed extensions to attribution v0 (fixed now):**
  * source kinds EMPTY, OTHER, RESET, INPUT(k), ENV, CONTEXT, COMPUTED(contributors), COMPUTED_FROM, MUTATION(draw, old_label);
  * fields orig_id, ctrl_deps, addr_deps, exec_deps.

## 4. Calibration and provenance tests

**4.1 Fixture pack** (Archaeon commits images and expected vectors before production):
- K1-K21 as in v2.
- K22: a guard NOT taken (ctrl_deps has the occupant).
- K23: an operand cipher, COMPUTED{(P,i), (W,op)}.
- K24: an input executed as an opcode (exec_deps has INPUT).
- K25: the writer sets the pointers and the occupant's opcode copies (exec_deps has the occupant; IMPLICIT).
- K26: LDIR with C=0 (256 iterations, wrap, self-overlap).
- K27: COPYALL over its own executing region.
- NPE-specific: K28 the BIRTH write-back with a mutation; K29 GETPC stored into the child; K30 a residue-only birth.
- **Mutation testing of the pack:** it must reject each of these mutant tracers on at least one fixture:
  * "every locus (W,0)";
  * "loci reversed";
  * a memmove (non-sequential) COPYALL;
  * pointer-label-instead-of-value;
  * no-exec_deps;
  * no-ctrl on untaken branches.

**4.2 Provenance tests** on the production sample (a random 1% of births plus mutants of them with 1-4 byte substitutions; no
random soups).
- **Per-byte where-provenance (the core test).** For each written locus with a MOVE data label (X, j), where (X, j) was NOT
  fetched as an instruction:
  * flip one bit of that byte, holding the RNG fixed;
  * the child locus must take the value the move predicts;
  * threshold >= 99%.
  Loci whose source byte was also executed are reported separately (code-and-data bytes).
- **Entity completeness.** Arms, each with 3 draws and the RNG matched per draw (the P-11 method; P11_SPEC.md):
  * each entity's non-executed bytes;
  * each entity's executed bytes;
  * the organism's persisted registers (NPE);
  * the task inputs.
  Every locus that changes must name the randomised source in its data label or dependence sets. Threshold >= 95%.
  * Power: with 3 draws, a dependence present on a fraction q of byte values is detected with probability 1-(1-q)^3. The q at
    which completeness has 80% power is reported.
- Thresholds apply PER BIRTH CLASS (s2.3), over written loci of births. Each class with >= 30 sampled births must pass separately.
  Smaller classes are reported with their CI and do not gate.

## 5. Samples (fixed)
- **BEE: r004041**, drawn by committed seed (archaeon/attribution/bee_run_draw.py; bee_run_draw.json in this folder).
  * Population: the 205 traced ENDOGENOUS_COPY runs with >= 1 is_sr birth, out of 845 traced runs.
  * r004041 has 17,309 births and 76 is_sr births.
  * r038751 (chosen earlier with knowledge of its properties) and r016299 (PAIR_EXECUTION) are OUT of scope.
  * Consequence: the pair-execution birth-rule confound (Review 3 s2.3) is untested, and that is stated as a limit.
- **NPE:** all pair interactions in the 11 T-003 runs (specimen 4931614d912c52b2). Accepted and non-accepted are reported
  separately. Decision statistics use a run-level bootstrap (11 clusters).
- **Compute:** leases per the canonical convention. If busy, queue.

## 6. Predictions (each with its consequence)

| # | Q | prediction | if it loses |
|---|---|---|---|
| P1 | Q8c, BEE | Q8c < 5% of written loci (95% upper bound) | ALTERED: v0 needs a weighted dependence field for BEE |
| P2 | Q3, BEE, identified loci | departure from uniparental inheritance by identified structure in < 5% of births (upper bound) | ALTERED: the parent_id convention is unsafe in BEE; SINGULAR_MATERIAL_PARENT thresholds re-derived |
| P3 | Q4, BEE | among writer-majority children, capable (s2.4) >= 30% (lower bound) | ALTERED: a "material without capability" field becomes REQUIRED in v0 records for BEE |
| P4 | Q1/Q6, NPE accepted births | performer-by-material != copy-descent majority donor in >= 1/3 (run-bootstrap lower bound > 1/3 -> the prediction holds; upper bound < 1/3 -> it loses; else INCONCLUSIVE) | ALTERED if it holds: a third role (executing material != donor) is needed in NPE records |
| P5 | Q2, NPE all interactions | >= 10% of interactions whose victim half gains >= L/2 copy-descent donor loci are NOT accepted (run-bootstrap lower bound) | if it loses: NPE acceptance is certified as a descent proxy for this specimen family |

**Descriptive estimates** (reported with a CI, no verdict effect, not predictions): BEE Q2 and address-reading agreement; BEE Q5
excess; Q7; Q-input; Q8r in both scopes.

## 7. What this cannot establish
- Explicit where-provenance with over-approximating dependence sets.
- The provenance tests bound ENTITY-level under-tainting and source-locus errors for MOVE labels in the sampled classes, at the
  stated power. They say nothing about COMPUTED labels' internal structure.
- One BEE run (seeded draw from one family) and one NPE specimen family.
- The pair-execution confound is untested.
- In-situ capability is confounded with survival; the isolated test is the primary.

## Amendment A (2026-09-28): the BEE fixture pack
- **Content:** archaeon/attribution/bee_fixtures.py, for r004041's world (BYTECODE32, L = 32, SEPARATED, no COPYALL).
  * 17 applicable fixtures; each has an exact memory image and hand-written expected labels.
  * Validated on the frozen VM by the independent reference tracer (archaeon/attribution/bee_ref_tracer.py), by the per-byte
    flip test and by the completeness arms: all pass. Output: BEE_FIXTURE_PACK_VALIDATION.txt.
- **Mutation testing:** the pack catches loc0, reverse, ptrlabel, noexec and noctrl_untaken. The memmove mutant is undetectable
  in this world, because it has no COPYALL and LDIR is sequential by construction.
- **Inapplicable, with reasons:**
  * K3, K16, K24, K25: the PC is confined to the writer's own half-regions in SEPARATED;
  * K10-COPYALL, K27: no COPYALL;
  * K9, K18, K19: world-level, and remain the owner's fixtures;
  * K20, K21, K28-K30: NPE.
- **Consequence for Q6 in this world:** executed code is always the writer's, so co-execution by material is structurally 0.
  Q6 is uninformative for r004041, which is recorded before the data.

## Amendment A2 (2026-09-28): the performer exemption in identification (s2.1)
- **Defect:** as written, s2.1(2) de-identifies a locus whenever exec_deps or ctrl_deps name any entity other than the data
  label's. The performer's entity is always in exec_deps. So every birth in which one entity copies ANOTHER's material, the Q1
  case itself, could never be identified, and Q1 would be INCONCLUSIVE by construction.
- **Change:** the dependence sets are tested against {data-label entity, performer entity}. A third entity, or a non-entity base
  label (INPUT/OTHER/RESET/ENV/CONTEXT), still de-identifies.
- **Effect on fixtures:** K25 (occupant opcode copies the writer's bytes, pointers set by the writer) becomes IDENTIFIED descent
  from the writer with performer = occupant, not IMPLICIT as Review 4 proposed. That is the producer != donor event Q1 exists to
  count. K25 is inapplicable in BEE's SEPARATED world anyway; it stays in force for NPE.
- **Found by:** Archaeon, while writing the reference tracer (not by a reviewer). It is flagged for Review 5's adjudication.

## Dated note 2026-09-28: SUPERSEDED (with Amendments A and A2) before any production run by ANCESTRY_PREREG_v4.md, after adversarial Review 5 (review5/REVIEW_5.md; REVIEW_5_ADJUDICATION.md). The r004041 draw is withdrawn (seed and draw committed together; mixed population; is_sr eligibility artefact). Text above unchanged.
