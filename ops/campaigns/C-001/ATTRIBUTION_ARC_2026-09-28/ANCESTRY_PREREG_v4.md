# Byte-level ancestry replays (BEE, NPE) -- preregistration v4 (Archaeon, 2026-09-28)

**History:**
- v1 (Review 3), v2 (Review 4) and v3 (Review 5) were each found UNSOUND and superseded before any production run. All are kept
  unedited, with their reviews and adjudications in this folder.
- v4 is frozen at the commit that adds it. Later changes are dated amendments at the end.

**Terms** (standard names):
- copy-descent = where-provenance (Buneman-Khanna-Tan 2001) under explicit flows;
- ctrl_deps = the program-counter label (Denning; Sabelfeld-Myers), with whole-execution scope and no declassification;
- post-dominator scope = the standard dynamic control-dependence scope;
- exec_deps = code / instruction taint;
- flip test and completeness arms = interventional noninterference tests. They test DEPENDENCE, not label type or precision.

## 0. Roles
- **Owners** (Bellerophon for BEE, Nestor for NPE):
  * implement an observation-only shadow tracer per s1 in their harness;
  * reproduce the preserved run;
  * pass the fixture pack;
  * run the s4 tests on their production sample;
  * export s3.
- **REFERENCE TRACER:** for each engine, written by an isolated, context-free worker from THIS text alone. It is neither Archaeon's
  nor the owner's. Archaeon's own tracer (archaeon/attribution/bee_ref_tracer.py) is a SECOND implementation. The owner's, the
  reference and Archaeon's tracers must agree per locus (s4.3).
- **Archaeon:** questions, fixtures, synthesis.
- **Independent reviewer:** adjudicates every non-VALIDATED trigger.

## 1. Label policy

**1.1 The unit.** The unit is one INTERACTION as the harness performs it.
- BEE SHARED is one vm.execute call. BEE SEPARATED is two calls on shared memory: memory labels carry over, and register labels
  reset at the second entry.
- An NPE birth is the full slice sequence from ALLOC to BIRTH, with other organisms' slices replayed as recorded.
- All counterfactuals are SINGLE-INTERACTION: the frozen harnesses cannot hold the world RNG fixed across ticks (Review 5 CX4).

**1.2 Data labels.**
- **ENTITY:**
  * executing organism locus i -> (ENTITY w, i, orig_id);
  * occupant / partner locus j -> (ENTITY o, j, orig_id);
  * NPE recombination mate locus i -> (ENTITY mate, i, orig_id), taken from the mate's persisted vector.
- **FOREIGN-INFORMATIVE:**
  * input byte k -> (INPUT, k);
  * NPE SENSE -> (ENV);
  * memory that can vary between worlds (NPE slot residue and other organisms' memory) -> (OTHER, addr).
- **FOREIGN-STRUCTURAL (never de-identifying; reported):**
  * BEE fresh zero scratch, zero RESET registers and flags, and EMPTY -> (CONSTANT, kind);
  * IN beyond 16 reads -> (CONSTANT, "in_exhausted");
  * NPE SELF / GETPC / ALLOC results -> (CONTEXT, op);
  * NPE slot-tail clearing at birth -> (CONSTANT, "clear").
- **Propagation:**
  * reads carry the label of the byte read; every store updates labels (OUT, per-byte sequential LDIR/COPYALL, and harness
    stores included);
  * moves carry labels; an immediate operand used as a value carries the operand byte's label;
  * COMPUTED_FROM(label) only for register-only, no-operand bijective operations (INC, DEC; NPE NEG and rotate);
  * everything else that computes -> COMPUTED(flattened base labels, CONSTANT bases dropped);
  * result-independent idioms (XOR A,A; SUB A,A) -> CONSTANT.
- **Hidden VM state:** the IN counter and the OUT counter are registers. Their labels are the ctrl_deps at each IN/OUT. OUT's
  16-output guard is a conditional.
- **Mutation:** MUTATION(draw index, old_label) at the RNG draw. It is never assigned by diff or value alignment.
  * For decode-dependent operators (OPCODE/OPERAND mutation act on linear-decode positions), each event records a
    decode-dependence set: the labels of the bytes that decided the position class.
  * Structural moves carry labels positionally.
- **Persistence:** per-organism label vectors persist after every interaction, refused write, mutation and migration.

**1.3 Dependence sets** (per child locus):
- `ctrl_deps` (primary: whole-execution PC label): the base labels of the condition inputs of every conditional EVALUATED (taken
  or not). This includes DJNZ, the LDIR/COPYALL C==0 exit, the OUT guard and the region-exit halt.
  * The step budget is FOREIGN-STRUCTURAL (CONSTANT, "budget"). A path that ends at the budget is recorded by a flag, not by a
    label.
  * Secondary: post-dominator-scoped ctrl_deps.
- `addr_deps`: the union of the pointer labels of the store AND of every load that contributed to the value.
- `exec_deps`: the base labels of every fetched opcode and operand byte.
- **Birth-existence dependence (per birth):** the base labels the harness's birth test reads. For BEE ENDOGENOUS_COPY that is
  n_written >= L and child != occupant, i.e. the occupant's full tape.

**1.4 Forbidden as material evidence:** resemblance, source address, value match, execution context and code location. CONTEXT
is reported, never used as material.

## 2. Identification, questions, verdicts

**2.1 Identification.**
- **RULE-IDENTIFIED locus:**
  * its data label is ENTITY; AND
  * ctrl_deps, addr_deps and exec_deps contain no FOREIGN-INFORMATIVE label and no ENTITY other than {the data-label entity,
    the performer entity}.
- **Flip coverage** (s4.1): a rule-identified locus is FLIP-CONFIRMED, FLIP-FAILED or FLIP-INAPPLICABLE.
- **IDENTIFIED** = rule-identified AND not FLIP-FAILED.
- **Where it is computed:** identification is computed on ALL births from the rule. The flip-failure rate from the sample (s4)
  is applied as a correction with a CI.
- **Per birth:** a birth is identifiable for a Q iff >= 90% of its written loci are IDENTIFIED.
- **Per class:** a class needs flip coverage (CONFIRMED + FAILED) >= 50% of its rule-identified loci, or it is INCONCLUSIVE.

**2.2 Definitions:**
- **performer** = the material label of the STORE instruction's opcode byte (for LDIR/COPYALL, that byte);
- **majority donor** = the plurality entity over the loci in question; ties -> TIED, empty -> NONE;
- **new material** = MUTATION, CONSTANT or COMPUTED labels CREATED IN THIS INTERACTION. Inherited labels count to their carrier
  entity;
- **birth classes:** self-performed / occupant-performed / INPUT-or-scratch-performed, each split IMPLICIT or not;
- every Q is reported over IDENTIFIED loci and over all written loci.

**2.3 Questions.**

| Q | question |
|---|---|
| Q1 | performer != majority donor |
| Q2 | the native resemblance label (BEE `material`; NPE acceptance and anc/oid) names a different majority donor than copy-descent |
| Q3 | departure from uniparental inheritance (a second donor >= 10%, or new material >= 10%, or performer != donor) |
| Q4 | material without capability. Capable = the child, in isolation (frozen VM, the run's layout), makes an exact copy of its own pre-execution tape by its own stores in >= 50% of 320 trials (8 random occupants x 40 random inputs). The definition is overlap-aware: no source-address criterion. NPE: the Odysseus recert test |
| Q5 | DESCRIPTIVE only: founder (tick-0 organisms) material share of capable children, against a drift-only null (Wright-Fisher / Moran resampling of the observed per-tick birth counts with the run's actual decode-dependent mutation operator). Not a verdict question (multi-tick counterfactuals are impossible, s1.1) |
| Q6 | co-execution by material: the entity composition of exec_deps in window-writing interactions |
| Q7 | source diversity over ENTITY loci; COMPUTED share alongside |
| Q-homology (new) | the share of child loci whose source locus differs from their own index. Also the heritable fraction: the share of the writer's loci that are ever a source (Review 5 CX1: a replicator copying its first half into both halves has a somatic half) |
| Q8c | interventional value dependence. Per written locus: randomise, in turn, each ENTITY other than the data-label entity (every ENTITY, for non-ENTITY data labels), K = 8 draws each, single interaction. A locus "changes" if its FINAL child byte differs from the baseline; a suppressed write or birth counts as a change. The estimand is the mean over loci of Pr_draw(change), with a birth-clustered bootstrap (and run-clustered in NPE). Q8c-whether (the write/birth suppression rate) is reported separately |
| Q8r | rule-IMPLICIT share (descriptive), in both ctrl scopes |
| Q-input | Q8c with the INPUT arm |

**2.4 Verdict per engine, with precedence INSTRUMENT_FAILED > SPEC_DEFECT > BROKEN > INCONCLUSIVE > ALTERED > VALIDATED:**
- **INSTRUMENT_FAILED:**
  * the owner's tracer disagrees with the reference tracer on more than 0.5% of loci in any class, unresolved at arbitration; OR
  * the owner's tracer fails a fixture.
- **SPEC_DEFECT:** s4 thresholds fail, and the failing loci are NOT explained by a named channel absent from s1 with a fixture
  that reproduces it. The run stops, and the prereg is amended.
- **BROKEN:**
  * s4 thresholds fail AND the failure is explained by a named channel absent from s1 (the policy cannot represent it); OR
  * the lower 95% bound of Q8c > 50%.
- **INCONCLUSIVE:**
  * fewer than 80% of births are identifiable for a by-design Q; OR
  * the flip coverage floor fails; OR
  * the Q8c interval neither excludes 5% nor exceeds 50% in the directions below.
- **ALTERED:**
  * the lower 95% bound of Q8c >= 5% (v0 needs a WEIGHTED dependence field: at >= 5% of loci a singular-donor record would
    misstate what the byte depends on); OR
  * a prediction with an ALTERED consequence decides so.
- **VALIDATED:**
  * the upper 95% bound of Q8c < 5%; AND
  * every by-design Q is expressible in attribution-v0 plus the agreed extensions; AND
  * the ROUND-TRIP check passes: each birth's labels are converted into v0 records, which pass schema.check, and every reported Q
    is recomputed from the v0 records alone and matches.
- **Thresholds:** 5% is the share of loci at which a singular-donor record misstates dependence often enough to change a
  parent_id convention (SINGULAR_MATERIAL_PARENT allows <= 10% second-donor share; 5% is half of it). 50% is dominance.

**2.5 By-design Q lists:**
- BEE: Q1-Q3, Q4, Q6, Q7, Q-homology, Q8c, Q-input, with Q5 descriptive.
- NPE: Q1-Q3, Q6, Q7, Q-homology, Q8c, Q-input; Q4 via recert; Q5 only if multi-generation ids are built (the owner states this
  before running).

## 3. Exported fields
- **Pinning:**
  * BEE: the frozen modules world 5b985241, vm 2536b1ac, grammar 3767d73d, tasks e2c37f76 (git 16fc6c2a), never imported from
    the working tree; traced_replay's HARNESS path repointed;
  * NPE: the z80atlas-verify harness files with their sha256.
- **Replay proof:** the preserved birth rows are reproduced bit-for-bit, PLUS a sha256 of every child tape and of the world RNG
  state after every tick.
- **Scope:** only birth-producing interactions are exported in full: their pre-state (memory, registers, flags, entry, budget,
  inputs, RNG draw index), and for NPE the slice sequence.
- **Per birth:**
  * writer pre/post tapes and labels; child tape;
  * per locus: data label, ctrl_deps (both scopes), addr_deps, exec_deps;
  * birth-existence dependence; the window write log; performer; class; mutation events with decode-dependence;
  * native fields verbatim; the Q4 result; test results.
- **Agreed extensions to attribution v0:**
  * source kinds CONSTANT(kind), CONTEXT(op), ENV, OTHER, INPUT(k), COMPUTED(contributors), COMPUTED_FROM,
    MUTATION(draw, old_label);
  * fields orig_id, ctrl_deps, addr_deps, exec_deps, birth_existence_deps, and a weighted dependence field (for an ALTERED
    outcome).

## 4. Tests on the production sample
- **Sample:** stratified by birth class and by Q4 capability: all births up to 200 per engine, else a random stratified sample of
  200. Mutants of births (1-4 substitutions) are reported separately and never gate.

**4.1 Path-preserving flip test.** For every rule-identified locus with an ENTITY MOVE label (X, j), each of the 8 bits:
- flip that bit of (X, j) in the pre-state and re-run the interaction;
- if the fetched-instruction trace (pc, opcode) and the store-address sequence are unchanged, the child locus must equal the
  predicted moved value -> CONFIRMED, else FAILED;
- if the path changed -> INAPPLICABLE for that bit;
- a locus is FAILED if any applicable bit fails, CONFIRMED if >= 1 bit is applicable and none fails, else INAPPLICABLE.
- Thresholds: FAILED <= 1% of flip-covered loci per class; coverage floor per s2.1.

**4.2 Completeness and precision arms** (K = 8 draws, single interaction):
- **Completeness:** randomising each entity's bytes (split executed / non-executed), the INPUT region, and (NPE) the persisted
  registers; every locus that changes must name the source. Threshold >= 95% per class.
- **Precision:** for each named ENTITY dependence, randomise that entity; the share of named dependences that ever change the
  value, the write or the birth is reported. If that share is below 20% in a class of >= 30 loci, the class's tracer
  OVER-TAINTS -> INSTRUMENT_FAILED unless a fixture shows the over-taint is required by s1.

**4.3 Tracer agreement.** Per locus, the owner's, the reference and Archaeon's tracers must agree on the data label and the three
dependence sets for >= 99.5% of loci per class on the sample. Disagreements go to arbitration by the independent reviewer.

**4.4 Fixture pack.** Archaeon commits it for the drawn BEE world and for NPE (semantics; Nestor writes the Z8 images; Archaeon
validates with 4.1/4.2 on NPE's world code). The pack contains:
- K1-K27 as in v3, where applicable;
- K31: a pure control-flow bit-decoder copy (Review 5 CX3). The rule label is COMPUTED/CONSTANT with ctrl_deps holding the
  source; a MOVE-labelling tracer must fail it;
- K32: a RESET-pointer LDIR self-overlap fill (the Review 5 CX1 replicator). Expected: loci L/2..L-1 sourced from 0..L/2-1;
  pointer/count labels CONSTANT; identified;
- K33: a SEPARATED two-call interaction (if the drawn world is SEPARATED);
- K34: IN past 16 and OUT past 16;
- K35: OR/ADD with a zero RESET register (value unchanged, label COMPUTED): an all-8-bit flip must fail a MOVE-keeping tracer;
- NPE K28-K30 (K30 includes slot-tail clearing).

**Mutation testing:** the pack must reject each of these mutant tracers on >= 1 fixture:
- loc0, reverse, memmove (where COPYALL exists), ptrlabel, noexec, noctrl_untaken;
- value-alignment labels;
- implicit copy labelled MOVE;
- positional label instead of overlap chain;
- exec_deps = all memory (over-taint);
- ctrl omits the region-exit / budget / OUT guard.

## 5. Samples (fixed)
**BEE: r025144.** Selection:
1. Population, committed FIRST in ea1d284ba (BEE_POPULATION_v4.json): the 73 traced runs with VM_COPY + SHARED + ENDOGENOUS_COPY
   (r038751's cell), with NO outcome-based condition.
2. Seed = that commit's full SHA. Index = sha256(seed) mod 73 over the sorted list = 34 -> r025144
   (archaeon/attribution/bee_run_draw_v4.py; BEE_DRAW_v4.json).

Declared before any data:
- r025144 has 92 births (rank 7 of 73; median of the cell 29,757), 0 is_sr births and 24 native "target" labels (26%).
- Every birth is in the sample.
- Q4/Q5 are expected to be weakly informative (few capable children).
- Most birth classes fall below the 30-birth gate and are reported with CIs without gating.
- The draw was uniform over RUNS, not over births. Changing that after seeing the result would be a forking path, so it stands.
- If the operator wants a birth-weighted second draw, it is taken with the seed = the SHA of the commit that freezes this v4.

Files (on M2 and copied here): config r025144.config.json; preserved births r025144.births.jsonl.gz (sha256 87133acd...b790).

**NPE:** all pair interactions in the 11 T-003 runs (specimen 4931614d912c52b2).
- "Victim" = the slot whose owner was displaced by the ALLOC.
- Accepted and non-accepted interactions are reported separately; the run-level bootstrap (11 clusters) is the decision
  statistic.

**Compute:** leases per the canonical convention. If busy, queue.

## 6. Predictions (each with its consequence)

| # | Q | prediction | consequence |
|---|---|---|---|
| P1 | Q-homology, BEE r025144 | >= 90% of identified written loci have source locus == own index (positional copying; shifts are rare in this cell) | if it loses: ALTERED (a positional-homology field is REQUIRED in v0 BEE records: fidelity-by-position misreads descent) |
| P2 | Q2, BEE r025144 | the native `material` label disagrees with the copy-descent majority in >= 10% of the births whose label is "target" (the resemblance label overcounts target material) | if it holds: ALTERED (native BEE material labels need an IBD correction field); if the upper bound < 10%: the label is certified for this run |
| P3 | Q1/Q6, NPE accepted births | performer-by-material != copy-descent majority donor in >= 1/3 (run-bootstrap lower bound > 1/3 -> holds; upper bound < 1/3 -> loses; else INCONCLUSIVE) | if it holds: ALTERED (a third role, executing material != donor, is required in NPE records) |
| P4 | Q2, NPE all interactions | >= 10% of interactions whose victim slot gains >= L/2 copy-descent donor loci are NOT accepted (run-bootstrap lower bound) | if it holds: ALTERED (NPE acceptance is not a descent proxy); if the upper bound < 10%: acceptance is certified |
| P5 | Q8c, both engines | upper 95% bound < 5% in the self-performed class | if it loses: ALTERED by s2.4 |

## 7. Limits
- Single-interaction counterfactuals only.
- Explicit where-provenance plus over-approximating dependence sets. The flip tests certify dependence, not label type; fixtures
  certify type.
- One BEE run from one cell (small); one NPE specimen family.
- The pair-execution birth-rule confound (PAIR_EXECUTION) is untested.
- Harness birth-existence flows are recorded but not intervened on.
- In-situ capability is confounded with survival (the isolated test is primary).

## Amendment A (2026-09-28): the BEE fixture pack for r025144's world
- **Content:** archaeon/attribution/bee_fixtures.py (VM_COPY, L = 64, SHARED; frozen VM 16fc6c2a), 29 fixtures:
  * K1/K1b, K2, K3 (= K25: partner-performed copy), K4-K8, K10 and K10c (COPYALL overlap), K11-K17;
  * K22-K24, K26, K27;
  * K31 (bit decoder), K32 (RESET-pointer self-overlap fill), K34, K35, K36 (count from the occupant).
- **Validation** (BEE_FIXTURE_PACK_v4_VALIDATION.txt), on Archaeon's tracer (value-checked on the frozen VM): every expectation met,
  0 FAILED flips, completeness complete. Every one of the 10 mutant tracers is caught by >= 1 fixture:
  * loc0, reverse, memmove, ptrlabel;
  * noexec, noctrl_untaken, noctrl_stops;
  * positional, implicit_move, exec_all.
- **Correction on record:** two hand-written expectations were corrected after the first validation run: K26 (the input region)
  and K36 (the first write precedes the count test). In both cases the tracer was right and the expectation wrong.
- **The owner's and the reference tracer must meet the same expectations.** The images are deterministic; expectations are data in
  bee_fixtures.fixtures().

## Amendment B1 (2026-09-28): the flip test also requires the load-address sequence unchanged (s4.1)
- **Defect found** while validating Amendment A. In the textbook COPYALL replicator (LD S,0; LD T,64; COPYALL), locus 1's source
  byte is ALSO the operand of LD S. Flipping it moves every load while the fetch path and store addresses stay the same. So s4.1 as
  written marks a correctly labelled locus FAILED.
- **Change:** "applicable" requires that the fetched-instruction trace, the store-address sequence AND the load-address sequence
  (every data read: LD A,(r), LDI/LDIR/COPYALL sources, IN reads) are all unchanged. Otherwise the bit is INAPPLICABLE.
- **Found by:** Archaeon while building the pack, not by a reviewer.
