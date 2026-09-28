# Byte-level ancestry replays (BEE, NPE) -- preregistration v2 (Archaeon, 2026-09-28)

- v1 (ANCESTRY_PREREG.md) is SUPERSEDED before any execution. Adversarial Review 3 (review3/REVIEW_3.md; adjudication in
  REVIEW_3_ADJUDICATION.md) found it UNSOUND. v1 is kept unedited.
- This v2 is frozen at the commit that adds it. Later changes are dated amendments appended at the end.
- Directive: roles/Archaeon/prompts/2026-09-28_attribution_arc/.

## 0. Division of labour
- **Owners (Bellerophon for BEE, Nestor for NPE):**
  * build a NEW observation-only shadow tracer in their own harness, implementing s1 exactly;
  * pass the fixtures (s4);
  * reproduce the preserved birth log bit-for-bit;
  * export s3.
  NPE's native z8taint niche tags do NOT satisfy s1: they label computed/input/self-location bytes by the executing organism's
  niche, which is execution context. A new shadow with (entity, locus) labels is required.
- **Archaeon:**
  * fixes the questions, fields, fixtures and thresholds (this file);
  * runs an INDEPENDENT differential check (s4.2) on a random 1% of each owner's production births, from the exported
    pre-execution states;
  * writes the synthesis.
- **An independent reviewer (not Archaeon) adjudicates every "alter" and "break" condition.**

## 1. The policy, named
Explicit-flow WHERE-PROVENANCE (dynamic taint tracking, data dependence only), PLUS per-locus IMPLICIT-FLOW dependence sets. "IBD"
in this arc means copy-descent under this policy. It is NOT population-genetic IBD and is mechanism-dependent (a copy made through
a loop counter is not copy-descent; it shows up in ctrl_deps).

**1.1 Data labels (every memory byte and every register and flag):**
- **Start labels:**
  * writer / executing organism locus i -> (ENTITY w, i, orig_id);
  * partner / occupant locus j -> (ENTITY o, j, orig_id), or EMPTY;
  * input region byte k -> (INPUT, k);
  * zero-filled scratch / other memory -> (OTHER, address);
  * BEE registers and flags at execution start -> RESET;
  * NPE registers and flags -> the label persisted from that organism's previous execution (multi-generation ids).
- **The label of a read is the label of the byte read**, including IN reading the input region: that byte may hold organism
  material written earlier.
- **Every store updates labels:** ordinary stores, OUT, LDIR/COPYALL (strictly sequential, per byte, so overlap smears correctly),
  and the harness's own window/input initialisation.
- **Moves** (load, store, register copy, block copy, exchange) carry the label.
- **An immediate operand used as a value** -> the label of the operand byte. So in BEE a "constant" is (ENTITY owner, operand
  locus).
- **Computation:**
  * a single-contributor bijective operation (INC, DEC, ADD n, XOR n, NEG, shifts are NOT bijective) -> (COMPUTED_FROM, label);
  * multi-contributor or non-bijective -> (COMPUTED, flattened set of base labels);
  * idioms whose result is independent of the operand (XOR A,A; SUB A,A) -> (CONSTANT, instruction label).

**1.2 Implicit-flow sets (per child locus):**
- `ctrl_deps`: base labels of every flag, counter or register that decided a branch taken since the last write to that locus in
  this execution. This includes the DJNZ counter and conditional-jump flags; the conservative scoping is intended.
- `addr_deps`: base labels of the pointer registers used for the store to that locus AND for the load that produced its value.

**1.3 Mutation and structural change:**
- MUTATION is assigned at the RNG draw, not by diff.
- Structural moves (BEE STRUCTURAL insert/delete/dup) carry labels positionally: shift and dup are ENTITY, an inserted byte is
  MUTATION.
- NPE in-VM copy noise is labelled at the write and propagates.
- A recombination splice (NPE `_recombine`) is ENTITY of the splice donor.
- No retagging by value alignment. NPE's `_mutated_orig` value alignment is forbidden: Review 3 showed it keeps a deleted byte's
  tag.

**1.4 Persistence:** every organism's per-locus label vector is updated after EVERY execution (birth or not), every refused
write, every mutation and every migration.

**1.5 Forbidden as material evidence:** resemblance, source address, value match, execution context, code location.

## 2. Questions, identifiability, verdicts

**2.1 A child locus is IDENTIFIED iff:**
1. its data label resolves to base labels with no UNKNOWN; AND
2. its ctrl_deps and addr_deps name no ENTITY other than its data label's entity; AND
3. for sampled births, the counterfactual check (s4.2) agrees.

A locus failing only (2) is IMPLICIT: reported as dependence on the named entities, not as descent. Identified share = identified
loci / L, reported over ALL loci and over WRITTEN loci.

**2.2 Common definitions:**
- majority donor = the plurality entity over the loci in question (ENTITY and COMPUTED_FROM counted by their base entity; ties
  -> TIED);
- performer = the MATERIAL owner of the executed opcode bytes that led to window writes (the plurality over those bytes); code
  location is reported separately as exec_where;
- every Q is reported by stratum of written loci: n_written <= 2, 3..L/2-1, >= L/2.

**2.3 The questions:**

| Q | question | computed over |
|---|---|---|
| Q1 | producer != majority donor | written loci; performer by material |
| Q2 | the native resemblance label (BEE `material` writer/target; NPE acceptance and anc/oid) names a different majority donor than copy-descent | written loci |
| Q3 | singular-parent loss: a second donor >= 10%, new material (MUTATION, CONSTANT, COMPUTED) >= 10%, or producer != donor. Reported with and without COMPUTED_FROM counted as new | all loci and written loci |
| Q4 | material without capability: majority-donor children that FAIL an ISOLATED capability test | BEE: the child tape vs 8 random partners x 40 random inputs in the frozen VM, "capable" = an exact copy of itself into the partner half; NPE: Odysseus's recert behavioural test (roles/Odysseus/expedition/recert/). In-situ later SR is kept as a secondary field |
| Q5 | founder-material share of capable children, as EXCESS over a mutation-only expectation at the child's material age (BEE BYTE/MED mutation) | capable children |
| Q6 | co-execution by material: the share of window-writing opcode bytes whose ENTITY label is not the majority donor. OTHER/INPUT/RESET opcode bytes are a separate category | executed opcode bytes |
| Q7 | source diversity over ENTITY loci, with the COMPUTED share alongside | written loci |
| Q8 (new) | implicit-flow share: written loci that are IMPLICIT | written loci; the direct measure of the constructor + description route (F13) the explicit policy cannot see |

**2.4 Identifiable-by-design lists, fixed now:**
- BEE: Q1-Q8.
- NPE: Q1, Q2, Q3, Q6, Q7, Q8; Q4 via recert; Q5 only if multi-generation ids are built (the owner says which before running).

**2.5 Verdict per engine (no pooling across engines):**
- **VALIDATED:** the instrument passes s4.2, AND every by-design Q is identifiable in >= 80% of births in stratum
  n_written >= L/2, AND attribution-v0 plus the fields agreed in s3 hold the results.
- **ALTERED:** VALIDATED except that a further field or role is needed, OR a prediction whose "loss implies ALTERED" loses.
- **BROKEN:** the counterfactual check fails its thresholds (the explicit policy plus implicit sets cannot recover what the bytes
  depend on), OR Q8 > 25% of written loci in stratum >= L/2 (descent is not the dominant channel of transmission, so per-event
  copy-descent is the wrong unit for that engine).
- A BROKEN engine gets a substrate-specific record, kept plural.
- The independent reviewer adjudicates each ALTERED/BROKEN trigger.

## 3. Exported fields (one JSON per birth or interaction)
- **Identity and pinning:** ids, run, harness commit and module sha256.
- **Pinning precondition:** the replay reproduces the preserved birth log BIT-FOR-BIT before any label is read.
  * BEE frozen modules: world 5b985241, vm 2536b1ac, grammar 3767d73d (E-001/TASKS.md).
  * BEE's HEAD simulator is NOT the frozen one.
- **Pre-execution state** (for Archaeon's independent re-execution): full memory, registers and flags, entry pc, budget, input
  values. Also the writer's pre AND post tapes and labels; the child tape.
- **Per child locus:** data label [kind, entity, source locus, orig_id, contributors], ctrl_deps, addr_deps.
- **The full per-write log for the window** (not only the last writer).
- **Per executed opcode byte:** material label, aggregated per birth; exec_where.
- **n_written;** the mutation-event list with RNG draw indices; native fields verbatim; the Q4 isolated capability result;
  fixture and counterfactual-check results; the output sha256.
- **Agreed extensions to attribution v0:** source kinds EMPTY, OTHER, RESET, INPUT(k), COMPUTED (contributors), COMPUTED_FROM;
  fields orig_id, ctrl_deps, addr_deps, executed-byte material. These count as agreed now, not as "new fields" at verdict time.

## 4. Calibration and the counterfactual check

**4.1 Known-answer fixtures** (expected answers fixed here; built by each owner in their ISA):
- K1-K7 as in v1 (exact copy; scratch copy; partner-executed copy; shifted copy; self-painter; computed byte; retention).
- K8 corrected: a written literal equal to the occupant's byte -> (writer, operand locus) in BEE; (CONSTANT) only where the ISA has
  operand-free constants.
- K9: mutation labelled at the draw.
- K10-K21 from Review 3:
  * K10: overlapping LDIR/COPYALL smear;
  * K11: control-flow copy -> COMPUTED{writer}, ctrl_deps has the partner, locus IMPLICIT;
  * K12: translation table -> addr_deps has the partner, IMPLICIT;
  * K13: input laundering -> writer label;
  * K14: OUT store read back;
  * K15: register start labels / NPE persisted register;
  * K16: self-code executed in the window -> performer = writer by material;
  * K17: address wrap and budget-exhausted LDIR;
  * K18: same-tick birth/overwrite/mutation order;
  * K19: structural delete/dup;
  * K20: NPE in-VM noise then re-copy;
  * K21: NPE interaction rewriting both halves.
- Review 3's executed counter-examples (review3/review3_cx.py, BEE frozen VM) are the reference implementations for K10-K14.

**4.2 Counterfactual agreement check (the pass criterion that matters):**
- **Sample:** 10,000 random soups plus a random 1% of production births, run by the owner AND independently by Archaeon from the
  exported pre-execution states.
- **Procedure:** re-execute each birth with one entity's bytes randomised, 4 draws per entity (the P-11 method).
- **Soundness:** a locus labelled (ENTITY X, j) must change in at least one draw when X is randomised. Threshold >= 99%.
- **Completeness:** every locus that changes when X is randomised must name X in its data label, ctrl_deps or addr_deps.
  Threshold >= 95%.
- **Failure:** fixtures failed, or thresholds missed -> the engine's replay does not proceed to the verdict. If the explicit+implicit
  policy cannot reach the thresholds by design, that engine is BROKEN.

## 5. Samples (fixed; no owner choice)
- **BEE: r038751** (ENDOGENOUS_COPY; 74,800 births; 42,915 is_sr births).
  * Chosen as the representative run: the TH-006 attestation already matched its preserved log bit-for-bit, and Q4/Q5 are
    informative there.
  * r016299 (PAIR_EXECUTION; 18 SR births) is atypical and uninformative for Q4/Q5; it is NOT in scope unless the operator adds
    it.
  * For Q1/Q6 co-execution, r038751 has 176 partner-code births. Too few for strata below n_written >= L/2 is accepted as a limit.
- **NPE: ALL pair interactions** in the 11 T-003 runs (specimen 4931614d912c52b2), not only the 34 accepted births. Q2 is reported on
  accepted and non-accepted interactions separately, by run, with a run-level bootstrap. The 34 births are not independent.
- **Compute:** leases per the canonical convention (comms LEASE ACQUIRE/RELEASE; roles/Ananke/research/lease.py). If busy, queue.

## 6. Predictions (each names its Q, stratum and consequence)

| # | Q | stratum | prediction | if it loses |
|---|---|---|---|---|
| P1 | Q8 | BEE, n_written >= L/2 | implicit-flow loci < 5% of written loci | ALTERED: ctrl/addr sets become first-class v0 fields |
| P2 | Q3 | BEE, n_written >= L/2, written loci | singular-parent loss by identified structure < 5% of births | ALTERED: parent_id convention unsafe in BEE |
| P3 | Q2 (proxy) | BEE, n_written >= L/2 | the address reading (row field 8 >= L/2) agrees with the copy-descent writer-majority in >= 95% of births | recorded: the address reading is not a usable proxy (no verdict effect) |
| P4 | Q4 | BEE, writer-majority children, n_written >= L/2 | isolated capability >= 30% | recorded: capability is rarely transmitted in situ-born BEE children |
| P5 | Q5 | BEE, capable children | founder-material share >= 2x the mutation-only expectation | recorded: no machinery conservation beyond the mutation clock |
| P6 | s4.2 | BEE | soundness >= 99% and completeness >= 95% | BROKEN for BEE |
| P7 | Q1/Q6 | NPE accepted births | >= 1/3 have performer-by-material != copy-descent majority donor (bootstrap interval reported) | ALTERED: a third role (executing material != donor) needed |
| P8 | Q2 | NPE non-accepted interactions | >= 10% of interactions whose victim half gains >= L/2 donor copy-descent loci are NOT accepted (resemblance false negatives) | recorded: acceptance captures descent events |
| P9 | s4.2 | NPE | soundness >= 99% and completeness >= 95% | BROKEN for NPE |

## 7. What this cannot establish
- Explicit-flow where-provenance only, plus coarse implicit-flow sets. It is blind to information transmitted in ways that neither
  the data nor the ctrl/addr sets capture. The counterfactual check bounds this blindness; it does not remove it.
- "Descent" results are conditional on the tracer's move set.
- One BEE run and one NPE specimen family: not engine-wide.
- In-situ capability is confounded with survival; the isolated test is the primary.
