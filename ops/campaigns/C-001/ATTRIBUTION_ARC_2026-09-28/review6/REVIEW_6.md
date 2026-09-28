# Review 6 -- ANCESTRY_PREREG_v4.md (commit b8275219e)

Reviewer: independent, context-free worker. Date 2026-09-28. Focus: is v4 SATISFIABLE and INFORMATIVE on the real drawn
BEE run (r025144)? All numbers below come from executed scripts in this folder (listed at the end). Everything ran on the
FROZEN harness (git 16fc6c2a; the sha256 prefixes match the s3 pins: world 5b985241, vm 2536b1ac, grammar 3767d73d,
tasks e2c37f76).

## Bottom line

- **The replay is exact.** All 92/92 preserved 20-column birth rows are reproduced bit-for-bit.
- **Satisfiable, but not informative.** Applied as written to r025144's 92 actual births, v4 does NOT force INCONCLUSIVE.
  It returns **BROKEN**: the Q8c lower 95% bound is 0.884, which is > 0.50, and BROKEN outranks INCONCLUSIVE. Even without
  BROKEN, the verdict would be INCONCLUSIVE twice over:
  * only 19/92 births (20.7%) are identifiable, against an 80% gate;
  * the occupant-performed class has 10.9% flip coverage, against a 50% floor.
- **VALIDATED and ALTERED are unreachable** on this run.
- **The verdict says nothing about the question v4 asks.** r025144 contains no replication at all:
  * every one of its 92 births is a memory-wrapping LDIR sweep with RESET registers (C=0 wraps to 255; S, T near 0);
  * the sweep rewrites the window IN PLACE (child = zeros in an EMPTY cell), or SHIFTED BY ONE (child[j] = occupant[j+1]);
  * the run goes extinct at tick 63 of 500.
  The BROKEN verdict, and the ALTERED consequences of P1 and P5, would be driven by that harness artefact, not by
  descent.
- **v4 also has general defects that would bite on any run:**
  * the literal whole-execution ctrl scope identifies 0% of the vm module's own textbook copy-then-task hybrid;
  * Q8c counts the performer's own necessity as dependence;
  * the precision and completeness arms are vacuous: a maximal over-taint tracer scores 0.992 on precision, against a
  0.20 threshold.

## 1. Replay (task 1) -- CONFIRMED

`r6_replay.py` does the following:
- extracts vm/world/grammar/tasks at 16fc6c2a into `scratch/` and checks their sha256 against the s3 pins;
- installs Bellerophon's `traced_replay` with HARNESS repointed to `scratch/`;
- runs r025144.config.json (seed 160446242705, ticks 500, cells 256, budget 256);
- compares the result with r025144.births.jsonl.gz.

Result: `births replayed 92 preserved 92 identical rows 92 ALL EQUAL`. Also: captures 24, null_rewrites 202, refused
writes 54, extinction at tick 63, final_alive 0.

The same script captures each birth interaction's pre-execution state (writer tape, occupant tape or None, inputs). These
are observation-only hooks and do not touch the world RNG.

## 2. v4 applied to the actual births (task 2)

**Implementation (`r6_v4.py`).** A shadow of vm.execute that carries the v4 s1.2/s1.3 labels:
- data labels: MOVE, COMPUTED_FROM, COMPUTED, CONSTANT;
- dependence sets: addr_deps carried with values; ctrl_deps as the PC label, including the DJNZ / JZ / JNZ / JC tests
  and the LDIR C==0 exit; exec_deps.
- **Checked against the frozen vm.execute on every run it performed** (92 baselines, about 9,700 flips, about 3,000
  randomisations). Memory and write map are identical in all of them.
- ctrl/exec are recorded two ways: at the store ("lenient") and over the whole interaction ("strict", the literal s1.3
  wording). On r025144 the two readings give identical results.
- **Q8c arm definition:** each non-data-label ENTITY arm randomises that entity's whole tape, with K=8 draws.
- **Flip-test path condition:** the path is preserved iff the fetched (pc, opcode) sequence AND the store-address
  sequence are unchanged.

### 2.1 What the births are

| group | births | data labels of the 64 written loci |
|---|---|---|
| EMPTY target, native "writer" | 60 | 3835 CONSTANT(empty), 5 CONSTANT(scratch). The child is 64 zero bytes in all 60 |
| OCCUPIED, native "target" | 24 | 1448 MOVE(O), 64 MOVE(W), 24 CONSTANT(scratch) |
| OCCUPIED, native "writer" | 8 | 333 MOVE(O), 128 MOVE(W), 51 CONSTANT(scratch) |

- **All 92 interactions end at the step budget; none halts.**
- **All 92 have >= 182 stores.** The typical path: a few random-byte NOPs, then an LDIR entered with the RESET C=0, which
  sweeps memory until the budget runs out.
- **In 88/92 births the majority of the child's values came from the window itself** (occupant bytes, or EMPTY zeros).
- Not one child locus is a copy from the writer's tape at its own index. Q-homology is 0/1219 among identified loci and
  1/1973 among all ENTITY loci.
- **Q4:** 0/92 children are capable. The best child succeeds in 12.5% of the 320 trials.
- **ENDOGENOUS_COPY's birth test counts writes, not changes (world.py `_apply_reproduction`).** An in-place
  `mem[T]=mem[S]` sweep with S=T therefore "writes" all 64 window bytes:
  * into an EMPTY cell, it creates an all-zero child;
  * with S=T+1 into an occupied cell, it creates a shifted self-copy of the occupant;
  * with S=T into an occupied cell, it is a null rewrite (202 of them).

### 2.2 v4's verdict inputs

| quantity (v4 section) | r025144 value | v4 consequence |
|---|---|---|
| rule-identified loci (s2.1) | 1219/5888 = 20.7%. Not identified: 3835 data:CONSTANT(empty), 80 data:CONSTANT(scratch), 768 exec foreign entity, 384 ctrl foreign entity; no INPUT anywhere | -- |
| identifiable births (>= 90% of loci IDENTIFIED) | 19/92 = 20.7% (self class 17/79, occupant class 2/13) | INCONCLUSIVE (< 80%) |
| flip test, self-performed class | 1091 CONFIRMED, 0 FAILED, 0 INAPPLICABLE; coverage 1.000 | passes |
| flip test, occupant-performed class | 14 CONFIRMED, 114 INAPPLICABLE; coverage 0.109 | INCONCLUSIVE (< 50% floor) |
| flip FAILED rate | 0/1105 | passes |
| Q8c, all written loci | 0.906, birth-clustered bootstrap 95% [0.884, 0.927] | **BROKEN** (lower bound > 0.50) |
| Q8c, self-performed class (P5) | 0.897 [0.874, 0.921] | P5 loses -> ALTERED consequence |
| Q8c-whether | birth suppressed in 88.0% of W-randomisations and 40.6% of O-randomisations | -- |
| completeness arm | 6211/6211 (self), 2090/2090 (occupant); INPUT arm changed 0 loci | passes (trivially, see s4 below) |
| precision arm | 1.000 (self), 1.000 (occupant) | passes (trivially) |
| P1 (Q-homology >= 90% positional) | 0/1219 | loses -> ALTERED consequence |
| P2 (native "target" != copy-descent majority in >= 10% of target births) | 1/24 over all written loci; 8/24 over identified loci (7 of the 8 are majority NONE) | holds or fails depending on the locus set; no CI rule for "holds" |

**Verdict under v4's precedence:** INSTRUMENT_FAILED no (assuming the tracers agree); SPEC_DEFECT no (the s4 thresholds
pass); **BROKEN yes**.

So v4 is not INCONCLUSIVE-by-construction on this run, but it is BROKEN-by-construction:
- CONSTANT-data loci randomise every entity, including the performer, and the birth dies (0.875);
- performer != donor loci randomise the performer, and the birth dies (0.985).

VALIDATED needs Q8c upper < 5%, and ALTERED is masked by BROKEN. **Neither is reachable.**

The BROKEN label is also semantically wrong. The tracer represented every locus (flip FAILED 0, completeness 100%), yet
BROKEN s2.4 reads "the policy cannot represent it".

## 3. Section verdicts and general attacks

### s0 Roles -- SOUND WITH CORRECTION
The reference tracer is written "from THIS text alone" (l.22). The text is ambiguous on ctrl/exec scope (see s1), so two
honest tracers can disagree through no fault of either, and the 99.5% agreement gate (l.187) turns spec ambiguity into
INSTRUMENT_FAILED. **Amendment:** fix the scope wording before the reference tracer is commissioned.

### s1 Label policy -- UNSOUND
1. **Whole-execution ctrl scope makes a textbook replicator unidentifiable.** l.10 and l.66 say "every conditional
   EVALUATED", with no declassification. The input label is FOREIGN-INFORMATIVE (l.42). Executed with COND_MULTI inputs
   on an occupied window (`r6_extra.py (c)`, 40 trials each, 40/40 births):
   - `vm.hybrid(replicator_copyall, witness_cond_multi)` (copy, then task): 2560/2560 loci identified at-store, but
     **0/2560 under the literal whole-execution scope**;
   - task-then-copy: **0/2560 under both scopes**, although the copy is unconditional after the branch rejoins (Q-input
     would be 0).

   r025144 escapes only because none of its organisms reads input. Any run whose replicators also do the COND task (the
   cell's task is COND_MULTI) is pushed back to INCONCLUSIVE. That is Review 5's failure, through the INPUT channel.
   **Amendment:** for identification, use the post-dominator-scoped ctrl_deps. Keep whole-execution as the reported
   over-approximation, and cover this with a fixture (K36: task-then-copy, which must be identified).
2. **"Every fetched opcode and operand byte" (l.72) does not say up to the store or whole interaction.** State it.
3. **The pad bytes are unlabelled.** IN bytes beyond len(inputs) are harness zeros; label them CONSTANT("in_pad"), not
   INPUT. The same goes for OUT stores, which bypass the harness W() (vm.py l.184-186) and never enter tr.writes; the
   policy should say whether they count as "stores" in s4.1's store-address sequence.

### s2 Identification, questions, verdicts -- UNSOUND
1. **Q8c conflates performer necessity and non-entity loci with second-donor dependence (l.113).**
   - Q8c randomises "every ENTITY" for non-ENTITY data labels, and "each ENTITY other than the data-label entity"
     otherwise. That includes the PERFORMER, whom s2.1 (l.84) explicitly exempts.
   - Randomising the performer's tape kills the birth, and a killed birth counts as a change. Q8c therefore approximates
     the share of (performer != donor or non-ENTITY) loci. That is Q1 plus a label census, not "a singular-donor record
     misstates dependence".
   - On r025144 this alone yields BROKEN.
   - Worse: P3 predicts performer != donor in >= 1/3 of NPE accepted births. If P3 holds, Q8c's lower bound is about
     1/3 or more, so NPE is at least ALTERED and possibly BROKEN by construction.

   **Amendment:**
   - Q8c randomises only entities outside {data-label entity, performer entity}.
   - Suppression is reported only in Q8c-whether, never as a value change.
   - CONSTANT/COMPUTED loci get a separate estimand.

   Caveat, measured: on r025144 even the amended Q8c is 0.895 over the 829 loci (30 births) that have an arm. These
   sweep births are genuinely two-party, because the writer's path routes the PC into the occupant's code. So the
   amendment fixes the design, not this sample.
2. **BROKEN's second bullet (l.125) mislabels a substantive finding as a policy failure.** "Q8c > 50%" means v0
   singular-donor records are dominantly wrong. That is a strong ALTERED, not "the policy cannot represent it" (l.124).
   **Amendment:** Q8c > 50% -> ALTERED (DOMINANT). Reserve BROKEN for unrepresentable channels.
3. **The 80% identifiable-birth gate (l.127) treats a finding as a failure.** In r025144, 65% of births carry no ENTITY
   material at all: they are all-zero children created by sweeping an EMPTY window. That is a clean, fully explained
   result, and v4 can only call it INCONCLUSIVE.
   **Amendment:** births with <= 10% ENTITY loci are a declared class, "NO_MATERIAL". They are reported, and are
   excluded from the identifiability denominator.
4. **"Class" is undefined (l.91, l.98, l.177, l.181, l.187).** It could be the s2.2 birth classes (performer x
   IMPLICIT) or something else. "IMPLICIT" has no birth-level definition, and a class with 0 rule-identified loci
   gives 0/0 coverage (it does occur: every EMPTY birth).
   **Amendment:** define the class key and the majority-performer rule, and say that 0/0 is "not gated".
5. **The flip-test path condition excludes every executed byte (l.173).** The condition is (pc, opcode), so any executed
   byte is INAPPLICABLE by construction. In r025144's occupant-performed class, the occupant sweeps over the very bytes it
   executes, and coverage is 10.9%.
   **Amendment:** where the flip changes an opcode byte, accept a path-preserving pair if the two opcodes are
   semantically equivalent (both undefined -> NOP; 207/256 byte values execute as NOP). Otherwise, count that locus via the
   per-byte completeness arm (see s4) instead of INAPPLICABLE.

### s3 Exported fields -- SOUND WITH CORRECTION
- The pins are correct: the sha256 prefixes match. They are NOT git blob ids; say "sha256 prefix" (l.149).
- The RNG-state hash per tick (l.152) cannot be checked against the original run, since only rows were preserved. It is
  a self-consistency record; say so.
- Export a per-birth mechanism flag: LDIR entered with C==0 (wrap), in-window source, budget-ended.

### s4 Tests on the production sample -- UNSOUND
1. **The precision arm is vacuous (l.182-184).** It randomises the whole named entity, and that nearly always kills or
   changes the birth.
   - Measured: the "exec_deps = all memory" over-taint mutant, which names W and O on every locus, scores
     **7875/7936 = 0.992** against a 0.20 threshold (`r6_extra.py (a)`).
   - The correct tracer scores 1.000. The arm cannot tell them apart.
2. **The completeness arm is vacuous for the same reason (l.180).** exec_deps always names the performer's entity, and
   whole-entity randomisation always changes something. Measured: 100% in both classes.
   **Amendment for both:**
   - randomise the NAMED BASE LABELS ((entity, index) bytes) for precision, and single unnamed bytes for completeness,
     each with K draws;
   - the pass rules become per-byte: named bytes that ever matter >= 20%; unnamed bytes that ever change the locus
     value (with path and birth preserved) <= 5%.
3. **The flip FAILED gate (l.177) is fine.** 0/1105.

### s5 Samples -- UNSOUND (not informative)
1. **The drawn run cannot answer the questions.**
   - v4 already knew r025144 had "0 is_sr births" (l.217).
   - It has no copy from the writer's tape at all (copied_from_own = 0 in all 92 rows).
   - Q4 is 0/92 capable.
   - All 92 births are budget-ended LDIR sweeps, and it is extinct by tick 63.
   The questions (donor, homology, capability, uniparental inheritance) presuppose transmission of a writer's material.
   Excluding outcome conditions removed Review 5's forking path, but it left no relevance condition either.
   **Amendment:** before any data, add a mechanism-level (not outcome-level) eligibility criterion that applies
   identically to all 73 runs. For example: >= 30 births whose majority child loci are MOVE-labelled from the writer's
   tape (computable by this tracer from the preserved rows' replays). Commit it, then redraw with a seed from that
   commit's SHA. Alternatively, draw uniformly over BIRTHS in the cell.
2. **The birth-weighted second draw is left to the operator (l.222).** It is optional and decided after seeing results,
   so it is a forking path.
   **Amendment:** decide now: either it is mandatory and co-primary, or it is dropped.

### s6 Predictions -- UNSOUND
- **P1 (l.237) and P5 (l.241) both "lose" on r025144** (0/1219 positional; self-class Q8c 0.897). Each triggers an
  ALTERED consequence ("positional-homology field REQUIRED", a weighted field) from shift-by-one memory sweeps. A
  prediction whose loss is guaranteed by a non-replicating sample is not a test of v0.
- **P2 (l.238) has no interval rule for "holds"** (only the upper bound is used for certification), and its value
  depends on the locus set: 1/24 over all written loci versus 8/24 over identified loci, of which 7 have donor NONE.
  s2.2 (l.99) reports "every Q" both ways without saying which one decides.
- **Amendment:** each prediction names its decision locus set, its interval, and the treatment of NONE/TIED. P1, P2 and
  P5 are evaluated only on births in a declared transmission class (writer-sourced MOVE majority).

### s7 Limits -- SOUND WITH CORRECTION
Add these limits:
- harness artefact births (write-count birth test);
- that Q8c/Q-input are entity-level interventions;
- that the BEE sample does not replicate (if it is kept).

## 4. Scripts (all in ~/wk/rev6/out)

| script | what it does | output |
|---|---|---|
| r6_replay.py | frozen-harness replay; row comparison; pre-state capture | r6_births_pre.json |
| r6_v4.py | shadow labelled VM (asserted equal to the frozen vm.execute on every call) plus helpers | -- |
| r6_analyse.py | identification (both scopes), s4.1 flip test, Q8c (K=8), Q4 (320 trials) | r6_results.json |
| r6_summary.py | the section-2 numbers | r6_summary_output.txt |
| r6_arms.py | completeness and precision arms; per-class coverage | r6_arms_output.txt |
| r6_extra.py | over-taint mutant precision, amended Q8c, hybrid scope test, sweep census | r6_extra_output.txt |

Total CPU is under 1 minute, single process.

## 5. Single most important amendment

Before any tracer runs, replace the run sample with one that actually transmits writer material. r025144's 92 births
are all budget-ended LDIR memory sweeps with no copy from the writer, so a mechanism-level eligibility criterion must be
committed first and the draw re-seeded. At the same time, remove the performer and birth suppression from Q8c; as
written it returns BROKEN (lower bound 0.884) on any such sample, whatever the provenance truth.
