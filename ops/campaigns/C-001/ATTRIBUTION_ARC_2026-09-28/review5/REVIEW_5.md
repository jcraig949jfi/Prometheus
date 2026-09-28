# REVIEW 5 -- ANCESTRY_PREREG_v3.md (attack as new)

Reviewer: independent, no stake. Checkout ~/Prometheus-worktrees/rev5 at 05ab73917. BEE frozen code extracted from git
16fc6c2a (sha256 prefixes vm 2536b1ac, world 5b985241, grammar 3767d73d: these match prereg s3). NPE code IS in this repo:
roles/Nestor/campaigns/z80atlas-verify-2026-09-22/ (z8.py, z8taint.py, world.py).

Executed evidence: ~/wk/rev5/out/review5_cx.py (run it from the rev5 worktree); its output is in review5_cx_output.txt.
All counter-examples run on the FROZEN vm.execute, not on a re-implementation. The only exception is CX5, which re-traces
the source addresses the same way traced_replay.py:88 does.

## Overall verdict: UNSOUND

The taint policy is now a sound over-approximation inside one vm.execute. The failure has moved. As written, v3
produces INCONCLUSIVE for BOTH engines by construction, whatever the tracers do:
- In BEE, register RESET values and zero scratch are constants, but the prereg treats them as foreign sources.
- In NPE, every birth's pointers and branch conditions come from SELF/ALLOC, which the prereg labels CONTEXT.
- The core flip test excludes exactly the bytes a self-copier copies: its own executed code.

The drawn BEE run is also not what s5 says it is:
- Its layout (SEPARATED) makes most by-design questions degenerate.
- Its dominant replicator is an exact self-copier that the is_sr criterion misses.

---------------------------------------------------------------------------------------------------------------------------

## s0 Division of labour -- SOUND WITH CORRECTION

Feasibility:
- BEE: feasible. vm.execute is a pure 120-line interpreter (vm.py@16fc6c2a:78-201). traced_replay.py:54-180 is already a
  line-for-line copy that owners can extend.
- NPE: feasible. z8taint.run_tainted (z8taint.py:27) is a line-for-line copy of z8.run that carries per-byte tags. It
  already threads register tags (reg_taint) across slices. The owner must replace the niche tag with the s1 label tuple and
  add three dependence sets.

Problems:
1. The prereg never mentions BEE's SEPARATED layout, and the drawn run uses it (see s5). In world.py@16fc6c2a:271-285 one
   interaction is TWO vm.execute calls on the same memory:
   - the first with region (0, L/2), the second with region (L/2, L);
   - registers are re-RESET between the calls, and each call gets budget//2.
   "Per execution" (s3), the RESET start labels and the per-execution ctrl scope are all undefined across the two calls.
   AMENDMENT: define the unit as the interaction (both calls). Memory labels carry across the calls; register labels reset
   at the second entry. The region-exit halt (vm.py:90, `if not (lo <= pc < hi): break`) is a conditional to be listed in
   ctrl_deps next to the budget stop.
2. The "independent reference tracer" (s0) and the "third-party reference tracer" (s2.5) are not the same object. s0 has
   Archaeon write it. Archaeon is also the synthesiser, so Archaeon's tracer then decides BROKEN versus INSTRUMENT_FAILED.
   AMENDMENT: name one reference tracer and its author, who must not be Archaeon or the owner. Gate on its per-locus
   agreement with the owner (see s4.2 item 5).
3. Pinning: world.py imports tasks.py (world.py@16fc6c2a:31), and task.inputs(rng) consumes RNG and sets the input bytes.
   tasks.py is not pinned. AMENDMENT: add tasks.py (sha256 prefix e2c37f76 at 16fc6c2a) to the s3 pin list. Owners must NOT
   import prometheus/z80atlas from the working tree: HEAD vm.py is c15528..., HEAD world.py is e8dacd..., both differ from
   the frozen files.

## s1.1 Data labels -- SOUND WITH CORRECTION

1. BEE constants are labelled as sources. world._execute builds `mem = bytearray(256)` fresh for every execution
   (world.py@16fc6c2a:266), and vm.execute starts every register at 0 (vm.py:82-83). So:
   - (OTHER, address) is the constant 0;
   - RESET is the constant 0;
   - EMPTY (a None partner) is the constant 0.
   None of these can vary between worlds, so none can carry information: in standard taint analysis constants are
   untainted. s2.1 nonetheless counts them as foreign base labels (see s2.1).
   AMENDMENT: label them CONSTANT(kind), and exclude CONSTANT from the "other base label" test in s2.1. For NPE, OTHER is
   not constant (slot residue and other organisms' memory) and stays a source.
2. Hidden VM state that the rules do not name:
   - IN reads mem[IN_BASE+ip], where ip is a hidden counter of IN executions. It returns the constant 0 once ip >= 16
     (vm.py:176-180), so in that case no byte is read and "the label of the byte read" is undefined.
   - OUT writes mem[OUT_BASE+len(outputs)] only if len(outputs) < 16 (vm.py:184-186): a hidden address counter plus a
     hidden guard.
   Whole-execution ctrl_deps happens to cover these channels, but the post-dominator secondary and addr_deps do not.
   AMENDMENT:
   - label ip and the output count as registers, with labels = the ctrl labels at each IN/OUT;
   - IN with ip >= 16 gives CONSTANT;
   - OUT's guard is a conditional.
3. Harness flows outside the VM are unlabelled:
   - birth existence requires n_written >= L (world.py:406) and child != occupant tape (world.py:412). This is a whole-tape
     equality test on the OCCUPANT's value, so the set of births is selected on the occupant's material;
   - OPCODE mutation (r004041's operator) mutates only linear-decode opcode positions (world.py:251-259). Whether byte p can
     mutate therefore depends on the values of the bytes before it.
   AMENDMENT:
   - record per birth, as a "birth-existence dependence", the base labels of the occupant (null-rewrite test) and of the
     written-set test;
   - record per mutation event the decode-dependence set, i.e. the labels of the bytes that determined whether p was an
     opcode position.
4. NPE recombination. The splice mate is `alive[rng.randrange(...)]` (NPE world.py:552-566). The mate is NOT in memory at
   execution start, so "ENTITY of the splice donor" has no orig_id source. AMENDMENT: add a start label (ENTITY mate, i,
   orig_id), taken from the mate's persisted vector.
5. NPE birth clears the slot tail: `mem[slot:slot+slot_size] = zeros` before writing g (NPE world.py:686-687). AMENDMENT:
   label the tail CONSTANT and cover it with fixture K30.

## s1.2 Dependence sets -- SOUND WITH CORRECTION

- ctrl_deps with whole-execution scope and no declassification is ordinary PC-taint (Denning 1977; Sabelfeld & Myers 2003,
  "program-counter label"). The post-dominator variant is the standard dynamic implicit-flow scope (Dytan, DTA++).
  exec_deps is "instruction/code taint". The document should use these names.
- The "budget stop" is listed but its condition input (the step counter) has no label rule. vm.py:89 and :140 test
  tr.steps, which is a function of the executed path. AMENDMENT: the step counter's label is the union of ctrl_deps and
  exec_deps at that point, or else declare budget a CONSTANT and state that consequence. Either is fine; leaving it
  undefined is not.
- addr_deps names "the load that produced its value" in the singular. A COMPUTED value has several loads. AMENDMENT: take
  the union over every load that contributed.

## s2.1 Identification -- UNSOUND

1. **BEE is INCONCLUSIVE by construction (CX1, executed).** r004041's dominant tape is TRACED_spontaneous.json top_tape
   1048d948b14ef7bd...fc15, i.e. two identical 16-byte halves. Each half runs:
   `LD A,(S) ; LD T,A ; ... ; LDIR`
   S = 0 and C = 0 come from RESET, so LDIR runs as a self-overlapping fill until the budget stops it. On the frozen VM
   the child is an exact copy of the writer. Consequences:
   - every child locus has RESET in addr_deps (the LDIR source pointer) and in ctrl_deps (the LDIR C == 0 exit);
   - under s2.1 no locus is rule-identified, no birth is identifiable, and INCONCLUSIVE fires.
   Deleting "LD S,0" / "LD C,n" from a replicator is the most obvious evolutionary shortening, so this is the general
   case, not a corner case.
   AMENDMENT: the s1.1(1) CONSTANT correction.
2. **NPE is INCONCLUSIVE by construction.** z8.py:430-443 has ALLOC set DE (the destination pointer) and fz (the success
   flag). z8.py:460-466 has SELF set HL (source) and BC (count). Every seeded replicator is built on these (NPE
   world.py:274-300: `SELF; ALLOC; JRZ go; ...; LDIR`), and _on_birth refuses any birth without a pending ALLOC
   (NPE world.py:661-663). So every copied locus carries:
   - CONTEXT(ALLOC) in addr_deps and in ctrl_deps (through JRZ);
   - CONTEXT(SELF) in addr_deps and in ctrl_deps (through the LDIR count).
   s2.1 lists CONTEXT as disqualifying, so the identified share is 0.
   AMENDMENT: split non-entity labels into:
   - FOREIGN-INFORMATIVE: INPUT, ENV, and OTHER where it varies;
   - FOREIGN-STRUCTURAL: CONTEXT from SELF/GETPC/ALLOC, the budget, CONSTANT.
   Identification should require only that FOREIGN-INFORMATIVE labels and other ENTITY labels are absent. The
   FOREIGN-STRUCTURAL share is reported.
3. **The flip-test conjunction makes the 90% bar unreachable (CX1, CX2, executed).** IDENTIFIED = rule-identified AND
   passes the flip test. The flip test is defined only for MOVE sources that were NOT executed.
   - In the r004041 dominant birth, 32/32 loci have an executed source, so the denominator is empty.
   - Even for the canonical replicator vm.replicator(L) in the SHARED layout, only 24/32 (75.0%) or 56/64 (87.5%) of loci
     are flip-eligible. Both are below the 90% per-birth bar, even for a perfectly labelled textbook self-copy.
   AMENDMENT: add a path-preserving flip test for executed source bytes:
   - flip each bit and re-run;
   - if the fetched-instruction trace (pc, opcode) and the store-address sequence are unchanged, the move prediction must
     hold;
   - otherwise mark the locus FLIP-INAPPLICABLE.
   Define IDENTIFIED = rule-identified AND not flip-FAILED. Report FLIP-INAPPLICABLE coverage and require >= 50% flip
   coverage per class, or the class is INCONCLUSIVE.
4. "A birth is identifiable iff >= 90% of its written loci are IDENTIFIED" contradicts the rule that IDENTIFIED exists only
   on the 1% sample. The INCONCLUSIVE rule ("< 80% of births identifiable") has no defined population. AMENDMENT:
   - identifiability is computed from rule-identification on all births;
   - the sample-estimated flip-failure rate is applied as a correction with a CI;
   - the 80% rule is evaluated on all births.

## s2.4 Questions -- SOUND WITH CORRECTION

- **Q8c conditions on the outcome.** Q8c counts only "draws in which the write still occurs". In an occupant-performed or
  occupant-gated birth, randomising the occupant typically stops the write. Those draws are dropped, so Q8c reads 0 exactly
  where the foreign dependence is total ("whether" dependence). This is selection on the outcome.
  AMENDMENT:
  - Q8c = share of loci whose FINAL child byte differs from baseline (a non-write counts as a change);
  - report the write-suppression and birth-suppression rates as Q8c-whether;
  - fix K, the number of draws per locus;
  - define the estimand as the mean over loci of Pr_draw(change);
  - use a cluster bootstrap by birth (and by run in NPE).
  With the draw count unspecified, the share grows with K, so the 10% and 50% cut-offs are not fixed quantities.
- Q8c is undefined for loci whose data label is not an ENTITY (CONSTANT, COMPUTED, MUTATION, INPUT). "Other than the
  data-label entity" has no referent there. AMENDMENT: for those loci, randomise every ENTITY in turn.
- **Q3 "new material" is ambiguous across generations.** MUTATION(draw, old_label) persists in the parent's vector. If an
  inherited MUTATION label counts as new material in the child, then Q3 (and P2) grow mechanically with lineage depth.
  AMENDMENT: new material = MUTATION or CONSTANT or COMPUTED events created in THIS transmission. Inherited ones count
  to their carrier entity.
- **Missing question: positional homology.** In r004041's dominant replicator, child loci 16..31 descend from writer loci
  0..15. The writer's bytes 16..31 are never material: CX1 flips writer byte 20 and the child is unchanged. BEE fidelity
  and `material` compare positionally (world.py:410; traced_replay.py:219-225). This is precisely where locus-level
  provenance disagrees with resemblance, yet every Q (Q1-Q3, Q6) is entity-level.
  AMENDMENT: add Q-homology, the share of loci whose source locus differs from their own index. Report the heritable
  fraction of the genome (population genetics: the non-transmitted half is effectively somatic). Use it in Q5.
- **Q5 is underspecified.**
  - "Founder" is not defined. r004041 is init RANDOM, so there are 144+ random founders.
  - The neutral replay "at the run's own rate" is wrong for OPCODE mutation, which acts per decoded opcode position
    (world.py:251-255), not per byte.
  - "The same births" is circular for a neutral null: it fixes the genealogy that selection produced.
  AMENDMENT: define founders as the tick-0 organisms. The neutral null should be a Wright-Fisher/Moran resampling of the
  observed per-tick birth counts, with the actual decode-dependent operator.
- Q6 and the occupant-performed and INPUT-performed classes are EMPTY in r004041. SEPARATED confines the PC to the writer's
  own tape (vm.py:90; world.py:273-274), and the TRACED row confirms births_by_partner_code = 0. State this; do not report
  a degenerate Q6 as a finding.

## s2.5 Verdicts -- UNSOUND

1. INCONCLUSIVE is guaranteed for both engines (s2.1 items 1-3). The arc cannot return an informative verdict as written.
2. There is no precedence among BROKEN, ALTERED and INCONCLUSIVE when several fire (for example Q8c > 50% while < 80% of
   births are identifiable). AMENDMENT: precedence INSTRUMENT_FAILED > BROKEN > INCONCLUSIVE > ALTERED > VALIDATED,
   stated explicitly.
3. The Q8c bands are dominated by P1. P1 loses (becomes ALTERED) whenever the Q8c upper bound is >= 5%, so the "CI within
   [10%, 50%]" rule never decides anything. A wide CI (for example [30, 70]) can never be BROKEN and defaults to ALTERED:
   imprecision is rewarded with a softer verdict.
   AMENDMENT: one three-way rule on Q8c:
   - upper bound < 5%: no field needed;
   - lower bound > 50%: BROKEN;
   - lower bound >= 5%: ALTERED;
   - otherwise INCONCLUSIVE.
   Justify 5% and 50% by the v0 decision they change. This review finds no stated derivation for them.
4. "BROKEN if both tracers reproduce the s4.2 failure" conflates a shared SPEC ambiguity with "cannot recover by design".
   Two tracers written from one ambiguous text share its errors. AMENDMENT: BROKEN needs the failing loci to be explained
   by a named channel absent from s1 (with a fixture that reproduces it). Otherwise the verdict is SPEC_DEFECT and the
   run stops.
5. VALIDATED: "attribution-v0 plus s3 hold the results" has no test. AMENDMENT: list the v0 fields each Q must be
   expressible in, and the round-trip check.

## s3 Exported fields -- SOUND WITH CORRECTION

- "Reproduce the preserved birth log bit-for-bit" is weak. The log rows (traced_replay.py:237-240) hold fidelities and
  counts, not tapes, and traced_replay's own divergence check compares only 7 summary keys (traced_replay.py:281-282).
  AMENDMENT: also export and compare a sha256 of every child tape and of the World.rng state after each tick.
- Per-execution pre-state for EVERY execution is large: r004041 has interactions every tick for 256 cells. Nothing says
  whether only birth-producing executions are exported. The 1% resample and Q8c need only birth executions plus their
  pre-states. State this.

## s4.1 Fixture pack -- SOUND WITH CORRECTION

Missing fixtures that expose plausible bugs:
- K31 (CX3, executed): a pure control-flow copy (bit decoder). A 28-byte loop reads occupant byte 5 only through JC and
  rebuilds it with INC into occupant locus 9:
  - the rule label is COMPUTED_FROM/CONSTANT of writer immediates, with ctrl_deps containing (O,5);
  - a WRONG tracer that labels the locus MOVE (O,5) passes the s4.2 flip test on 8/8 bits.
  Only a fixture can catch this.
- K32: RESET-pointer LDIR fill (the r004041 dominant tape), with the expected vector showing loci 16..31 sourced from 0..15
  and CONSTANT pointer and count labels.
- K33: SEPARATED two-call interaction, with register reset at the second entry and the region-exit halt.
- K34: IN past 16 reads (constant 0) and OUT past 16 (no store).
- K35: an OR/ADD with a RESET-zero register (value unchanged, label COMPUTED): a single-bit flip passes if the tracer
  wrongly keeps MOVE.

Mutant tracers to add to the mutation test:
- "value-alignment labels" (the forbidden `_mutated_orig` approach);
- "implicit copy labelled MOVE";
- "positional label instead of overlap chain";
- "exec_deps = all memory";
- "ctrl_deps omits the region-exit/budget stops".
The current six mutants include none of the over-tainting bugs. An over-tainting tracer passes completeness by
construction.

## s4.2 Provenance tests -- UNSOUND

1. **The core test is structurally blind where it matters (CX1/CX2).** The test excludes executed source bytes, and a
   self-copier's executed bytes are what it copies. In the dominant r004041 birth, 32/32 loci are excluded. A
   positional-label bug is invisible:
   - it labels locus 20 as (W,20), whereas the truth is (W,4) through the overlap chain;
   - both are executed bytes;
   - CX1 shows flipping byte 20 leaves the child unchanged.
   There is no minimum coverage. AMENDMENT: the path-preserving flip test (s2.1 item 3), with a coverage floor per class.
2. **The flip test measures dependence, not the label (CX3).** It certifies that the child value moves with the source,
   which a control-flow copy also does. State it as a counterfactual (interventional) dependence test in the sense of
   noninterference testing. Rely on fixtures for label TYPE.
3. "Flip one bit" does not say which bit. AMENDMENT: all 8 bits, or a pre-registered random bit per locus. A single bit
   passes OR-mask mislabels whenever the mask bit is 0 (K35).
4. **Completeness cannot fail for an over-approximating tracer.** Whole-execution PC-taint plus exec_deps names almost
   everything that ran, and there is no precision arm. AMENDMENT: add a precision arm. For each named ENTITY dependence,
   randomise that entity (K draws) and report the share of named dependences that ever change value or write.
   Over-tainting beyond a stated ratio is INSTRUMENT_FAILED, not INCONCLUSIVE.
5. Per-locus agreement of the reference tracer is "reported" but not gated. AMENDMENT: >= 99.5% exact agreement per class,
   and any disagreement goes to arbitration before the verdict.
6. **Sample size.** 1% of 17,309 births is about 173, and expected is_sr births in the sample are 0.76. The mutants "with
   1-4 byte substitutions" are not births. Nothing says whether they count toward the >= 30-per-class gate or the
   thresholds. AMENDMENT: stratify the sample by birth class and Q4 capability. Mutants are reported separately and never
   gate.
7. "Holding the RNG fixed" is only meaningful within one vm.execute (CX4). OPCODE mutation calls rng.random() once per
   opcode position (world.py:254-255), so one flipped byte changes the draw count: 32 vs 31 on the r004041 tape. That
   shifts every later World.rng draw (partners, inputs, other tapes' mutations). Any multi-tick counterfactual (in-situ
   Q4, anything on Q5) cannot hold the RNG fixed on the frozen harness. AMENDMENT: all s4.2 and Q8c counterfactuals are
   single-interaction. The multi-tick ones are dropped or re-specified with per-purpose RNG streams (which is a harness
   change and must be stated).

## s5 Samples -- UNSOUND

1. **No precommitment.** The seed, the eligibility rule, the code and the drawn result are all first committed together in
   05ab73917 (git log on bee_run_draw.py and bee_run_draw.json). Nothing shows that the seed and population were fixed
   before the result was seen, so re-rolling cannot be excluded. AMENDMENT: commit the population and a hash of the seed
   first, then draw in a later commit, or use an external beacon value from after the commit.
2. **The population is not the "family r038751 belongs to".** The only shared factor is reproduction = ENDOGENOUS_COPY:

   | run | representation | layout | mutation | pressure |
   |---|---|---|---|---|
   | r038751 | VM_COPY | SHARED | BYTE HIGH | EXPLOIT |
   | r004041 | BYTECODE32 (L=32) | SEPARATED | OPCODE MED | QD |

   (TRACED_spontaneous.json rows.) The 845 "traced runs" are themselves a union of selected sets
   (traced_replay.py:317-324): spontaneous-replication triggers, a baseline sample, and seeded runs. r004041 is from the
   spontaneous set. "Representative" is therefore of a mixture, not of a family.
   AMENDMENT: stratify the draw by representation and layout, or restrict to r038751's cell (VM_COPY/SHARED), and declare
   the parent selection.
3. **The is_sr eligibility counts a criterion artifact (CX5, executed).**
   - The dominant tape makes EXACT self-copies, but only 16/32 of the window's last writes have a source inside [0, L).
     The rest come from the overlapping fill. So criterion (b) (traced_replay.py:222, >= 0.9L) marks it non-SR.
   - The TRACED row agrees: 3,334 of 3,349 high-fidelity tail births are not SR, alive_end_sr_born = 0, and
     n_origins_alive_at_end = 0.
   - "76 is_sr births" does not measure self-replication in r004041. Q4 and Q5, defined over is_sr, would study an
     extinct side-lineage and miss the replicator that took over the run.
   AMENDMENT: drop is_sr from eligibility. Use an operational definition that is overlap-aware (the child is an exact copy
   of the writer's pre-execution tape and the writer's own code performed the stores).
4. **The layout makes predictions degenerate.** SEPARATED means the writer never executes the occupant, and r004041 has
   material_target = 17 of 17,309 births. So Q1, Q6 and P1 are fixed by the layout, not measured.
5. Replay: the TRACED row shows tracer_diverged = [] on the 7-key check. The births file and run directory are on a
   Windows path (bee_run_draw.py:21-22; traced_replay.py:37) and are not in this repo, so this review could not verify a
   bit-for-bit replay. That remains an owner precondition.

## s6 Predictions -- UNSOUND

- **P1 cannot realistically lose in r004041** (s5 item 4): co-execution is impossible and target material is 0.1%. It also
  dominates the Q8c ALTERED band (s2.5 item 3). AMENDMENT: re-draw the run, or predict on a run where occupant execution
  is possible, and merge P1 into the three-way Q8c rule.
- **P2's outcome depends on how Q3 defines new material** (inherited MUTATION labels; s2.4). AMENDMENT: fix per
  transmission first.
- **P3's 30% has no derivation.** "Writer-majority children" includes about 4,187 births that changed <= 2 bytes of a
  near-identical occupant (TRACED row births_changed_le_2_bytes). Their capability comes from the occupant as much as the
  writer. AMENDMENT: derive the threshold from the v0 decision it changes, and condition on births that changed >= L/2
  loci.
- **P4 is SOUND** (three-way with INCONCLUSIVE). Its threshold of 1/3 needs a stated reason.
- **P5 has no consequence if it holds, and its losing branch certifies.** It can never yield ALTERED, and it is losable
  only by precision. "Victim half" is undefined in NPE, which has slots, not halves (NPE world.py:603-640). AMENDMENT:
  - define victim as the slot whose owner was displaced by the ALLOC;
  - give P5 an ALTERED consequence if it holds;
  - certification needs an upper bound below 10%, not just a failed lower bound.
- None of P1-P5 addresses the one quantity the arc newly measures, locus-level descent (Q-homology). AMENDMENT: add a
  prediction on it.

## s7 Limits -- SOUND WITH CORRECTION

Add these limits:
- single-interaction counterfactuals only (RNG coupling, CX4);
- BEE SEPARATED layout, which excludes co-execution;
- harness-level birth-existence flows (null-rewrite, n_written);
- flip tests certify dependence, not label type.

## Terminology

The document uses these terms; standard names in brackets:
- "copy-descent" [where-provenance (Buneman-Khanna-Tan 2001) under explicit flows];
- "ctrl-taint" [PC label / implicit flow; whole-execution = no declassification];
- "post-dominator scoped" [the standard dynamic control-dependence scope];
- "exec_deps" [code/instruction taint];
- "flip test" and "completeness arms" [interventional noninterference testing; they test dependence, i.e. under-tainting,
  and say nothing about label type or precision];
- "IDENTIFIED" [taint-certified AND counterfactually confirmed];
- "Q8c" [interventional value dependence, a crude quantitative-information-flow measure];
- "departure from uniparental inheritance" [biparental or horizontal transfer plus mutation load];
- "founder-material excess vs NEUTRAL replay" [founder contribution vs a drift-only (Wright-Fisher/Moran) null];
- r004041's untransmitted half [non-heritable / somatic region, which lowers effective genome length].

Misuses:
- RESET, zero scratch and budget are called foreign "base labels"; they are constants.
- CONTEXT is treated as information-bearing for identification, while s1.3 says it is non-material. These contradict each
  other.

## Most important amendment

Treat constants (BEE RESET registers, zero scratch, EMPTY, budget) and structural world values (NPE SELF/GETPC/ALLOC) as
non-disqualifying, and replace "not executed" with a path-preserving flip test that has a coverage floor. As written, s2.1
plus s4.2 make every BEE birth in r004041 and every NPE birth unidentifiable, so both engines are INCONCLUSIVE before any
data exist.
