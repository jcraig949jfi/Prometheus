# REVIEW 4 -- adversarial review of ANCESTRY_PREREG_v2.md (byte-level ancestry replays, BEE + NPE)

Target: ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/ANCESTRY_PREREG_v2.md at 784893b60 (cited as "v2:<line>").
Reviewer: an isolated worker with no prior context and no stake. Read-only on the repo.

Executed material is in this folder:
- review4_cx.py is a reference shadow tracer that implements v2 s1.1/s1.2 literally, plus the s4.2 counterfactual check exactly
  as written. It runs on BEE's FROZEN VM (git 16fc6c2a:prometheus/z80atlas/vm.py, sha256 prefix 2536b1ac, which matches
  v2:114).
- The memory layout is r038751's (inputs/r038751.config.json): ENDOGENOUS_COPY, VM_COPY (COPYALL on), L=64, SHARED, ECHO with
  one input byte at 0xE0, budget 256, entry 0.
- Every case is value-checked against the frozen vm.execute. Only the labels come from the rule set.
- Reproduce with: `git show 16fc6c2a:prometheus/z80atlas/vm.py > /tmp/r4_vm16.py; python3 review4_cx.py`.

NPE code IS in the repo: roles/Nestor/campaigns/z80atlas-verify-2026-09-22/{z8.py, z8taint.py, world.py, P11_SPEC.md}. It is
cited as "NPE/<file>:<line>". The frozen BEE world is cited as "world16:<line>" (git show 16fc6c2a:prometheus/z80atlas/world.py).

**Overall verdict: UNSOUND as frozen.**

v2 fixes v1's specific counter-examples, but it moves the unsoundness into the new machinery:
1. The s4.2 counterfactual check, which v2 calls "the pass criterion that matters", tests dependence at ENTITY granularity by
   destroying a whole entity's bytes. That makes it:
   - vacuous for the executing entity;
   - blind to the source-locus field that Q4-Q7 consume;
   - blind to INPUT/OTHER dependence.

   A tracer with badly wrong labels passes it at 100%/100% (D1).
2. The new BROKEN rule (Q8 > 25%) counts DEPENDENCE, not transmission. It is driven by the ctrl_deps scoping and by the reading
   of the word "taken". An exact self-copy guarded by one occupant check is 100% IMPLICIT, so BROKEN fires, while the
   counterfactual check shows the occupant changes the child for 1 byte value in 256 (D2).
3. Several predictions and decision rules are still:
   - vacuous (the strata are empty by the birth rule; P1's consequence is already granted by s3);
   - numerically wrong for the named run (P5 uses the MED mutation rate; r038751 runs at HIGH);
   - without a verdict (failing the 80% identifiability gate triggers nothing).

-------------------------------------------------------------------------------------------------------------------------------
## Executed counter-examples (review4_cx.py output, abbreviated)

**D1. s4.2 cannot see label errors inside an entity. Soundness is vacuous for the executor.**
- Setup: writer = `LD S,0; LD T,64; COPYALL; HALT` plus a random tail; the occupant is random.
- Three tracers were checked with s4.2 as written (4 draws per entity):

  | tracer | label of locus 5 | distinct source loci | soundness | completeness |
  |---|---|---|---|---|
  | correct | (W,5) | 64 | 1.000 | 1.000 |
  | BUG "every locus (W,0)" | (W,0) | 1 | 1.000 | 1.000 |
  | BUG "loci reversed" | (W,58) | 64 | 1.000 | 1.000 |

- Why the bugs pass:
  - randomising the WRITER destroys the program, so every writer-labelled locus "changes" whatever j the label names;
  - randomising the occupant changes nothing.
- The (W,0) tracer turns every replicator into a "painter" under Q7 (source diversity 1/L), and Q5 by locus is garbage. s4.2
  passes both bugs. Only a fixture could catch them, and the owner writes the fixtures (see s4.1).

**D2. Q8, and therefore BROKEN, is set by the ctrl_deps scoping, not by transmission.**
- Setup: writer = "read occupant byte 0; if it is HALT, skip; else COPYALL self". The child is an exact writer copy
  (n_written = 64).

  | variant | reading of "branch taken" | IMPLICIT loci | s4.2 soundness / completeness | loci changed when occupant randomised |
  |---|---|---|---|---|
  | JZ skip (the jump is not taken) | only jumps that jump | 0/64 | 1.000 / 1.000 | 0 |
  | JZ skip (the jump is not taken) | any conditional evaluated | 64/64 | 1.000 / 1.000 | 0 |
  | JNZ go (the jump is taken) | either reading | 64/64 | 1.000 / 1.000 | 0 |

- Exhaustive check: 1 of 256 occupant byte values changes the child.
- So Q8 = 100%, which fires BROKEN (v2:106), for a pure self-copy.
- The same child flips between IDENTIFIED and IMPLICIT depending on whether the assembler used JZ or JNZ, or on how
  "branch taken" (v2:49) is read.

**D3. The task INPUT, executed as an opcode, decides whether a birth happens. The locus is still IDENTIFIED writer descent.**
- Setup: writer = `IN A; OUT A; LD S,0; LD T,64; JP 0xF0`. The ECHO answer at 0xF0 is then executed.
- A birth occurs for 2 of the 256 input values. In both, every locus is IDENTIFIED (W,i) with empty IMPLICIT sets.
- This is not exotic in r038751: B6_PROBE_r038751.json records 66,669 copy writes executed at pc >= 2L ("elsewhere"). Past
  2L there are only zero-filled scratch (a NOP slide), the input byte and the output bytes.
- s4.2 randomises entities only, and s2.1(2) only looks for ENTITY labels in ctrl/addr. So a dependence on INPUT is never
  tested and can never make a locus non-identified.

**D4. v2's "ADD n is single-contributor" (v2:44) contradicts its own operand rule (v2:41).**
- Setup: `child[i] = occupant[i] + 0x40`. The 0x40 is a writer operand at locus 6.
- The rule labels the locus (COMPUTED_FROM, {(P,0)}). Changing only writer byte 6 changes child[0] (verified), yet (W,6)
  appears nowhere: not in the data label, ctrl_deps or addr_deps.
- The locus is saved from being "occupant descent" only because the pointer operands happen to be writer bytes (addr_deps
  {(W,1),(W,3)}), which makes it IMPLICIT.
- With RESET pointers, or pointers loaded from occupant bytes, it would be IDENTIFIED occupant descent. With "COMPUTED_FROM
  not counted as new" (Q3, v2:90), a writer-authored cipher of the occupant then reads as uniparental occupant descent.

**D5. The expected answer for v2's own K3 fails v2's own completeness criterion.**
- Setup: the writer sets S and T, then jumps into the occupant. The occupant's opcode byte is COPYALL.
- Every locus is IDENTIFIED (W,i), which is K3's expected answer (v1 K3, carried into v2:129).
- s4.2 on this birth: soundness 0.984, completeness 0.496. Randomising the occupant (the performer) changes all 64 loci, and
  the occupant is in no set.
- The rule set has no instruction (opcode) taint. The correct tracer fails completeness on every partner-performed birth
  "by design". Under v2:155-156 that makes BEE BROKEN, unless those births are diluted below 5% of the pooled loci. With 176
  such births in 74,800 (v2:164), they are diluted, so the check is silently passed.

-------------------------------------------------------------------------------------------------------------------------------
## s0 Division of labour -- SOUND WITH CORRECTION

1. **The fixture programs are not fixed.** v2:128 says "expected answers fixed here; built by each owner in their ISA". Expected
   answers without fixed byte programs let an owner write a K-program that avoids the case the fixture is meant to probe.
   Example: a K10 smear whose overlap never crosses the label boundary, which a memmove tracer also passes.
   Review 3's review3_cx.py covers only K10-K14 (v2:146).

   **Amendment:** Archaeon (or the reviewer) commits, before the owners start, the exact BEE memory images, entry points, budgets
   and inputs for K1-K21 with the full expected 64-locus label vectors (data, ctrl_deps, addr_deps). NPE gets the same, in Z8
   bytes. The owner may only add fixtures.
2. **Archaeon's "independent" check is the same weak test.** Its 1% differential check (v2:17-18) uses s4.2's entity-level method
   (D1), so it is not independent evidence about source loci.

   **Amendment:** Archaeon's check must re-derive the full label vector with an independently written tracer (for example
   review4_cx.py extended to the whole ISA) and report exact per-locus agreement, not only s4.2 rates.

-------------------------------------------------------------------------------------------------------------------------------
## s1 The policy -- UNSOUND

**Standard terms.**
- s1.1 is dynamic taint tracking with explicit-flow (data-dependence) propagation. The ENTITY labels are where-provenance
  (Buneman, Khanna & Tan 2001).
- s1.2's ctrl_deps is NOT control dependence in the standard sense (Ferrante, Ottenstein & Warren 1987: post-dominator
  regions). It is a "tainted PC" without declassification at the post-dominator ("label creep"): every branch since the last
  write to the locus, which for a locus written once means every branch since execution start.
- addr_deps is pointer tainting. Slowinska & Bos (2009) document that it over-taints everything that is indexed.
- "Implicit flow" is Denning's (1976) term, and the classic limitation of a dynamic monitor applies: an untaken path leaks
  (Fenton; Austin & Flanagan's no-sensitive-upgrade). v2 names neither the scoping nor this limitation.

**Problems.**

1. **"branch taken" (v2:49) is ambiguous, and the verdict turns on it (D2).**
   - Under the literal reading, a guard that falls through carries no ctrl_dep. Under the other reading, every evaluated
     conditional does.
   - **Amendment:** "every conditional branch EVALUATED, taken or not, including DJNZ, the LDIR C==0 exit, and the budget
     check that stops LDIR/COPYALL".
   - Also state the scope formally. Pick ONE of:
     - (a) post-dominator scoping (standard, less over-taint);
     - (b) whole-execution scoping.

     Report Q8 under both. Only the counterfactual Q8c (s2 below) may carry verdict weight.
2. **There is no instruction (opcode) taint (D3, D5).**
   - What executes depends on the material of the executed opcode bytes. BEE executes the window, the input byte and the
     output bytes as code (B6_PROBE_r038751.json: self_copied 1,726,650; elsewhere 66,669).
   - **Amendment:** add `exec_deps` = base labels of every opcode AND operand byte fetched as an instruction since execution
     start (the PC-taint analogue). Include it in completeness (s4.2) and report it with Q6.
   - IDENTIFIED condition (2) must also test exec_deps. Otherwise K3/K16 are internally contradictory (D5).
3. **INPUT/OTHER/RESET dependence never makes a locus non-identified (D3).** v2:71 checks only "ENTITY other than".
   - **Amendment:** condition (2) reads "name no base label other than the data label's entity". Report INPUT-dependent loci as a
     separate share, Q8-input.
4. **The bijective-op list is wrong for immediates (D4).**
   - ADD A,n and XOR A,n have two contributors: A and the operand byte, which v2:41 itself labels (writer, operand locus).
   - The parenthesis "shifts are NOT bijective" sits inside the list of bijective operations (v2:44), so the list contradicts
     itself.
   - **Amendment:** COMPUTED_FROM only for operations whose sole non-constant input is one register with no operand byte
     (INC, DEC, and in NPE, NEG / rotate). ADD n and XOR n are COMPUTED{A, operand}.
   - For Q3, add the variant "COMPUTED_FROM counts toward the source entity only if the transform has no other ENTITY
     contributor".
5. **NPE world ops have no label rule.** v2 s1.1 is silent on:
   - SELF / GETPC: these put the base, length or PC into H, L, B, C (NPE/z8taint.py:331-345). That is execution LOCATION
     becoming data, which v2:65 forbids as evidence, yet it must be given a label.
   - SENSE (the environment, :347-352);
   - ALLOC's returned address (:300-313);
   - BIRTH/SPLIT: the harness copies and mutates the slot and writes it back outside the VM (NPE/world.py:660-690:
     `g = self._mutate(child_bytes)`, `self.mem[slot:...] = g`);
   - slot residue left by dead organisms. In NPE's "pre-image" logic (NPE/world.py:666-676) residue is a heredity channel,
     and whose ENTITY it belongs to is undefined.

   **Amendment:**
   - SELF / GETPC / ALLOC results -> (CONTEXT, op), counted as non-material and reported;
   - SENSE -> (ENV);
   - `_on_birth`'s harness write-back is a store that carries the labels of the slot bytes, with s1.3 mutation labels at the
     draw;
   - residue keeps its persisted multi-generation ENTITY label. Add a fixture K22 (residue-only birth) and K23 (GETPC value
     stored into the child).
6. **The MUTATION label is assigned regardless of value.** BEE BYTE mutation redraws the same value with probability 1/256
   (world16:259). NPE OPERAND-type mutation is value-dependent (+/- delta, bit flip).

   **Amendment:** MUTATION(draw, old_label). This keeps the prior label as a secondary field, so Q5 can count an identity redraw
   as survival if the analyst chooses, stated now.

-------------------------------------------------------------------------------------------------------------------------------
## s2 Questions, identifiability, verdicts -- UNSOUND

1. **The strata are empty by the birth rule.** In ENDOGENOUS_COPY a birth requires n_written >= L (world16:406). Every r038751
   birth therefore has n_written = 64:
   - the strata "<= 2" and "3..L/2-1" (v2:82) are EMPTY in the only BEE run;
   - "all loci" and "written loci" coincide;
   - v2:164 ("too few for strata below ...") is factually wrong: they are empty by construction, not small.

   **Amendment:**
   - Say so. For BEE, replace the n_written strata with birth classes that do vary: self-performed / occupant-performed /
     INPUT-or-scratch-performed (exec_deps), and IMPLICIT vs not.
   - To test the birth-rule confound Review 3 raised, add r016299 (PAIR_EXECUTION) as a secondary sample for Q1/Q3/Q8 only.
2. **Identifiability condition (3) exists only for the 1% sample (v2:72).** For 99% of births, "identified" is either undefined
   or silently reduced to (1)+(2).

   **Amendment:** "identified share" is estimated on the counterfactual sample, with a binomial CI. Conditions (1)+(2) alone are
   reported as "rule-identified".
3. **Q8 measures dependence, not transmission. The BROKEN threshold is unprincipled.**
   - D2: a copy that is 100% IMPLICIT is 100% descent in value. The rationale at v2:106, "descent is not the dominant channel",
     does not follow from ctrl/addr membership.
   - 25% is not "not dominant"; dominance would be > 50%.
   - The threshold is not derived from any consequence, such as a parent_id error rate.

   **Amendment:** split Q8 into:
   - Q8r (rule-IMPLICIT share, descriptive only);
   - Q8c (counterfactual value dependence): on the s4.2 sample, the share of written loci whose value changes when a
     NON-data-label entity is randomised while the data-label source bytes are held fixed. Example: randomise only occupant
     bytes that are not copied into the locus, and compare only draws in which the write still occurs.

   BROKEN iff the lower 95% bound of Q8c > 50% of written loci. ALTERED iff Q8c's CI lies within 10-50%.
4. **Performer by plurality (v2:80) is undefined on NOP slides.**
   - Code that falls past 2L executes about 90 zero bytes of scratch (OTHER) before 0xE0. "Plurality over executed opcode bytes
     that led to window writes" then names OTHER, and "led to" is undefined.
   - **Amendment:** performer = the material label of the opcode byte of the STORE instruction (for LDIR/COPYALL, that
     instruction's byte). Report the path plurality separately, excluding NOP-equivalent bytes.
5. **Majority donor on IMPLICIT loci is undefined.** v2:74 says IMPLICIT loci are "not descent", but v2:78 counts ENTITY loci
   without excluding them.

   **Amendment:** compute every Q twice: over IDENTIFIED loci only, and over all written loci. Ties and the empty set -> TIED /
   NONE.
6. **The verdict rules have holes, and one of them can be gamed.**
   - (a) Failing ">= 80% identifiable" (v2:102) yields no verdict: it is neither ALTERED nor BROKEN.
   - (b) "Identifiable in >= 80% of births": per-birth identifiability of a Q is undefined (all 64 loci? a majority?).
   - (c) A failed s4.2 means "does not proceed" (v2:155), yet also BROKEN "if by design" (v2:105, 156). Who decides "by design"
     is the same party who built the tracer. A buggy tracer can therefore be relabelled as a substantive BROKEN finding.
   - (d) P1's loss consequence ("ctrl/addr sets become first-class v0 fields", v2:173) is already granted by s3 (v2:123-124).
     P1 can lose, but losing changes nothing.

   **Amendments:**
   - (a) add INCONCLUSIVE (identifiability < 80%);
   - (b) a birth is identifiable for a Q iff >= 90% of its written loci are identified;
   - (c) "by design" requires that a reference tracer written by a third party (not the owner) reproduces the failure on the
     same births. Otherwise the outcome is INSTRUMENT_FAILED, not BROKEN;
   - (d) give P1 a real consequence or remove it: Q8c in 5-50% -> ALTERED (the v0 record needs a dependence field WITH
     weights).

**Terminology.**
- "copy-descent" = identity by copy under a taint policy (where-provenance lineage).
- "majority donor" = the principal parent by ancestry proportion.
- Q3 "singular-parent loss" = departure from uniparental inheritance (admixture / horizontal transfer).
- Q5 = a conservation test against a neutral (mutation-only) expectation, i.e. purifying selection. "Material age" should be
  defined as the time since the byte lineage's last MUTATION label.

-------------------------------------------------------------------------------------------------------------------------------
## s3 Exported fields -- SOUND WITH CORRECTION

1. **Pinning is feasible.**
   - git 16fc6c2a's vm/world/grammar blobs hash to the prefixes named at v2:114 (verified).
   - HEAD differs: vm.py c1552813, world.py e8dacd5c.
   - traced_replay.py:29 hard-codes a Windows HARNESS path. The owner must repoint it to a 16fc6c2a checkout and log the module
     sha256 at import.
   - E-001/TASKS.md:52 shows a full r038751 replay in 50.9 s, so a whole-run shadow replay with per-execution label persistence
     (s1.4: about 500 ticks x 256 cells) is cheap.
2. **Missing fields.**
   - exec_deps (s1.2 above);
   - the RNG state or draw index at every birth. The counterfactual re-execution must hold the world RNG fixed, and NPE's in-VM
     copy noise draws from ctx.rng (NPE/z8taint.py:283-284);
   - for NPE, the time-slice boundaries of a birth. A bytewise copy spans several slices, each a fresh context
     (NPE/world.py:668-673).

   A "pre-execution state" (v2:116) is not defined for a birth whose writes span slices interleaved with other organisms.

   **Amendment:** export the RNG draw index and state per execution. For NPE, define a birth's counterfactual unit as the full
   slice sequence from ALLOC to BIRTH, with other organisms' slices replayed as recorded.

-------------------------------------------------------------------------------------------------------------------------------
## s4 Calibration and the counterfactual check -- UNSOUND

1. **Entity-level randomisation cannot validate source loci, and it is vacuous for the executor (D1).** Q4, Q5 and Q7 consume the
   source locus, and s4.2 never tests it.

   **Amendment (core):** add a per-byte where-provenance test on the s4.2 sample. For each written locus whose data label is
   ENTITY (X, j) with kind MOVE:
   - flip one bit of byte (X, j) only;
   - the child locus must change to the value predicted by the move (for a pure move, the new byte). Threshold >= 99%;
   - if (X, j) was itself fetched as an instruction byte (it is in exec_deps), report the locus separately. Code-and-data
     bytes are exactly where this test is ambiguous.

   For the executing entity, randomise only bytes NOT fetched as instructions. Otherwise soundness is trivially 100%.
2. **Pooling dilutes every failure mode below the thresholds.**
   - The "10,000 random soups" (v2:149) are dominated by non-births, so the loci they contribute are occupant retentions that
     are trivially sound.
   - Partner-performed births are 176 of 74,800 (D5 fails them at about 50% completeness).
   - Denominators are not stated (loci? births? written loci?).

   **Amendment:**
   - thresholds apply per birth class (self-performed, occupant-performed, INPUT/scratch-performed, IMPLICIT, fixture-like
     soups), over WRITTEN loci of BIRTHS;
   - each class with >= 30 births must pass separately;
   - random soups are replaced by the sampled production births plus mutants of them (1-4 random byte substitutions), which
     exercise realistic code.
3. **"The P-11 method" is misquoted.** P-11 uses 3 draws, not 4 (P11_SPEC.md:36, 47). It randomises the VICTIM only, keeps the
   victim's registers (P11_SPEC.md:67) and matches the copy RNG (P11_SPEC.md:44, 75).
   - Without a matched RNG, NPE's copy noise changes loci under every draw, so completeness fails for no reason and gives a
     spurious BROKEN.
   - Without randomising registers, the cross-interaction register flows that v2 itself introduced (v2:35) are never tested.

   **Amendment:**
   - fixed RNG per draw (the P-11 seed derivation);
   - an additional draw arm that randomises the organism's persisted registers;
   - state the draw count as 4, derived from the target detection power: with 4 draws, a dependence present on a fraction q of
     byte values is detected with probability 1-(1-q)^4. Report the q at which completeness has 80% power.
4. **INPUT/OTHER/RESET are never randomised (D3).** **Amendment:** add an INPUT arm: redraw the task inputs with the world RNG
   stream held fixed otherwise.
5. **The fixtures cannot catch several plausible bugs.** Add these fixtures, with fixed programs:
   - K22: NOT-taken guard, D2 JZ variant. Expected: ctrl_deps has the occupant.
   - K23: operand-cipher, D4. Expected: COMPUTED{(P,i),(W,6)}.
   - K24: input-as-opcode, D3. Expected: exec_deps has INPUT.
   - K25: writer sets pointers and the occupant's opcode performs the copy, D5. Expected: exec_deps has the occupant; IMPLICIT.
   - K26: LDIR with C=0 (256 iterations, wrap, self-overlap through the window it is executing from).
   - K27: a copy that overwrites its own executing code mid-LDIR. For BEE this is safe because LDIR runs internally, but
     COPYALL over the PC region must be covered.
   - K28: the NPE BIRTH harness write-back with a mutation.
   - K29: NPE GETPC stored into the child.
   - A label-bug detector that each fixture must fail on: run the (W,0) and "reversed" tracers of D1, a memmove COPYALL tracer,
     and a pointer-label-instead-of-value tracer. Every fixture set must reject each mutant tracer on at least one fixture
     ("mutation testing" of the calibration).

-------------------------------------------------------------------------------------------------------------------------------
## s5 Samples -- SOUND WITH CORRECTION

1. The r038751 choice was made AFTER its properties were known ("Q4/Q5 informative", v2:160-161). That is selection on the
   outcome of interest. It is acceptable only if r016299 (or a run drawn at random from the ENDOGENOUS_COPY family) is added as
   a pre-committed secondary sample. Otherwise "one BEE run" (v2:187) is a hand-picked one.

   **Amendment:** add one run drawn by a committed seed from the ENDOGENOUS_COPY runs that replay bit-for-bit, plus r016299 for
   the birth-rule contrast.
2. NPE "all pair interactions" is right. The 34 accepted births are clustered in 11 runs, so any statement on them must use the
   run-level bootstrap as the decision statistic, not merely report it (see P7).

-------------------------------------------------------------------------------------------------------------------------------
## s6 Predictions -- UNSOUND

1. **P1:** its consequence is already granted (s2 item 6d). It is also tied to the rule-Q8, which is scoping-driven (D2).
   **Amendment:** restate on Q8c (P1': Q8c < 5%).
2. **P3, P4, P5, P8 are "recorded", with no verdict effect.** They cannot lose in any consequential sense, and P4's 30% and P8's
   10% have no derivation.

   **Amendment:** either label them "descriptive estimates, reported with CI" (not predictions), or attach a consequence. For
   example:
   - P4 loses -> F-record "material without capability" becomes a required v0 field;
   - P8 loses -> NPE acceptance is certified as a descent proxy.
3. **P4: "capable" (v2:91) has no aggregation rule over 8 partners x 40 inputs.** D3 shows capability can be input-dependent.
   **Amendment:** capable = exact self-copy in >= 50% of the 320 trials. Report the full distribution.
4. **P5 uses the wrong mutation rate.** v2:92 says "BEE BYTE/MED mutation", but r038751 is mutation_rate HIGH
   (inputs/r038751.config.json; mut_rate HIGH = 0.03 vs MED = 0.008, world16:78-79).

   Expected founder share under mutation only, (1-mu)^t:

   | t (ticks) | MED | HIGH |
   |---|---|---|
   | 40 | 0.725 | 0.296 |
   | 100 | 0.448 | 0.048 |
   | 200 | about 0.20 | about 0.002 |

   With MED, the 2x test needs founder shares above 0.9 at t=100 and is nearly unwinnable. With HIGH, any retained founder byte
   late in the run gives an unbounded ratio, so it is nearly unlosable. The ratio statistic itself is unstable near zero.

   **Amendment:**
   - use the run's own rate;
   - replace the ratio with the difference (observed - expected) with a CI, against a neutral simulation. That means replaying
     the same run with the same births but labels subjected only to mutation;
   - restrict to t where the expected share is >= 0.05.
5. **P6 and P9 are the s4.2 gate restated, not predictions.** **Amendment:** delete them from s6, since they are already in s2.5.
6. **P7's decision statistic is unstated.** n = 34 accepted births in 11 runs, drawn from the resemblance-selected set that s5
   itself distrusts. The bootstrap is "reported" but not used.

   **Amendment:**
   - ALTERED iff the run-bootstrap 95% lower bound > 1/3;
   - "not altered" iff the upper bound < 1/3;
   - else INCONCLUSIVE;
   - also evaluate it over all interactions with >= L/2 donor loci, not only accepted ones.

-------------------------------------------------------------------------------------------------------------------------------
## s7 What this cannot establish -- SOUND WITH CORRECTION

v2:185 says the counterfactual check "bounds this blindness". It does not:
- it is entity-level (D1);
- it omits INPUT (D3);
- it pools classes (s4 item 2).

**Amendment:** say the check bounds ENTITY-level under-tainting in the sampled classes at the stated power, and nothing about
source-locus errors unless the per-byte test (s4 item 1) is added.

-------------------------------------------------------------------------------------------------------------------------------
## Summary of verdicts

| section | verdict |
|---|---|
| s0 | SOUND WITH CORRECTION |
| s1 | UNSOUND |
| s2 | UNSOUND |
| s3 | SOUND WITH CORRECTION |
| s4 | UNSOUND |
| s5 | SOUND WITH CORRECTION |
| s6 | UNSOUND |
| s7 | SOUND WITH CORRECTION |

## The single most important amendment

Replace the entity-level counterfactual check (s4.2) with a per-byte where-provenance test: flip each labelled source byte (X, j)
that was not executed as code, and require the child locus to change as the recorded move predicts, per birth class; otherwise a
tracer that labels every locus (writer,0) passes the gate at 100%/100% (D1). Make the BROKEN rule depend on counterfactual value
dependence (Q8c, lower 95% bound > 50%) instead of ctrl/addr membership, which returns BROKEN for a guarded exact self-copy (D2).
