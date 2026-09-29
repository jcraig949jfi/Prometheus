REPORT -- are the three Z80-like builds independent evidence? (convergence / design-lineage audit)

1. WHAT I SET OUT TO TEST
-------------------------
A cross-engine synthesis of the program's three Z80-like worlds (Archaeon's 32-opcode VM and its later
environment-gating line, Bellerophon's BEE z80atlas, Nestor's NPE z8 campaign) argues that four phenomena
recur "across three independently written worlds, three independent teams", and that this makes them design
laws, not one team's bugs: (1) harness channels that move material get credited to organisms; (2) replicative
machinery is conserved while cargo erodes unless something pays for the cargo; (3) acquisition is easier than
maintenance/establishment; (4) origins are scaffolded. I added a fifth recurrence that all three builds visibly
share: (0) heredity needs the supplied copy instruction.

The three codebases are genuinely separate, so code independence was not in question. The question was whether
each recurrence follows from a design choice the three builds share. They share one operator directive, one donor
paper, one model family, one operator and one day. For each recurrence I named the shared choice that would
produce it, then looked in committed data for arms of each engine where that choice is absent, to see whether the
recurrence survives there.

The stop rule was fixed in advance. If a recurrence persists in two or more engines with its entailing choice
removed, it is a candidate law. If every recurrence vanishes with its choice, the triplication was an
implementation check, not independent evidence.

2. WHAT I DID
-------------
Inputs: only committed data. I only read the repository clone (git show / git archive). I used no sealed or
holdout data.

Documents read (path@sha):
- The synthesis under audit: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/D_Z80_SYNTHESIS.md@72923db05 (s3,
  lines 48-96). Also the lens files it cites: A0_ARCHAEON_LENS.md, W1_NPE_LENS.md, W2_BEE_LENS.md and
  G_PRIOR_ART.md @origin/archaeon/deep-block-2026-09-27.
- The directive: roles/Bellerophon/prompts/2026-09-19_z80_atlas_campaign/00_OPERATOR_DIRECTIVE_verbatim.md
  @origin/main.
- The three builds at their launch commits:
  * Archaeon: archaeon/z80atlas/{vm.py, CAMPAIGN_CONTRACT.md, campaign/GRAMMAR_FROZEN.json}@c7610ea19.
  * BEE: prometheus/z80atlas/{vm.py, world.py}@98b2149a7, and @a1b066309 (the code pinned for BEE's grounding
    round).
  * NPE: roles/Nestor/campaigns/z80atlas-2026-09-19/{z8.py, grammar.py, PREREGISTRATION.md}@aa5833488.
- archaeon/envgate/engine.py@origin/main. It imports archaeon.z80atlas vm/engine and runs with copy_prim=True
  and ENDOGENOUS_COPY, so the gating line inherits the 09-19 VM and its address frame.
- Archaeon's 09-23 post-campaign directive@a3325b392, lines 39-40 and 92-93 (I checked the quoted text).
- BEE:
  * roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md and receipts/GROUNDING_RESULTS.json@3efdacf7e.
  * The analysis code tools/grounding_analysis.py (identical at 582c42ed2, 3efdacf7e and origin/main).
  * roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md@origin/main.
- NPE:
  * observatory/INDEX.jsonl.gz@origin/main (last changed in 3b407946e; 23,471 rows).
  * roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/P11_REASSAY.jsonl@d7641744d (1,031 rows).
  * roles/Nestor/campaigns/c9x-explore-2026-09-24/{c_core/VERDICT.json, x_content/SUMMARY.json}@origin/main.
- Archaeon copier census: archaeon/z80atlas/census/{RESULTS.json, HITS.json}@c5067fac6.

Scripts and outputs (in my scratch directory; outputs in out/):
- tally_npe.py -> out/npe_tally.txt. Counts NPE spontaneity flags by world, copy primitive, self-location and
  recombination axis, in RANDOM-seeded endogenous runs.
- tally_p11.py -> out/p11_tally.txt. Counts P-11 survivors by factor.
- homo.py -> out/p11_homopolymer.txt. Modal-byte share of each P-11 survivor's donor genome.
- out/archaeon_gating.txt. The input values that gate each exact copier in the Archaeon census.
- stats.py -> out/stats.txt. One-sided Fisher exact tests for the factor-removal contrasts.
- bee_null.py and bee_null2.py -> out/bee_null*_s11/12.txt and out/bee_null2_hits_*.json. A new null model:
  * It runs BEE's VM, exported from a1b066309 into src/bee_a1b0663 and run with env -u GIT_*.
  * Input: uniform random 64-byte tapes, 2 x 500,000 of them, 2 processes, default Config (Z80_64, budget 256,
    LDIR on, undefined byte = NOP).
  * Predicate: the world's own SELF_REPLICATION test (world._is_self_copy): at least 90% of the window is moved
    from the writer's own bytes by its own code, the child matches the writer both before and after execution at
    fidelity >= 0.9, and the material is the writer's.
  * recheck_hits.py -> out/recheck_hits.txt re-ran every hit with v2 strict budget and 10 random partner windows.
  * Positive control (vm.replicator): passes.
- out/g6_init_check.txt. Cross-tab of BEE's 160 G6 origin rows: tick of the first self-replicator against
  whether the genealogy had any ancestor.

Factor matrix (T1). The three builds, cited at their build commits:

 factor               Archaeon (c7610ea19, +envgate)   BEE (98b2149a7 / a1b066309)       NPE (aa5833488)
 -------------------  -------------------------------  --------------------------------  -------------------------------
 decode               dense: op=byte&31, every byte    sparse ~51 opcodes, undefined     Z80-style variable length,
                      defined                          byte = NOP (a factor in v2)       undefined byte = NOP
 supplied copy op     COPY 1 byte B->C, ++ (vmcopy     LDI, LDIR (+COPYALL in VM_COPY)   ED B0 LDIR / ED B8 LDDR (BLOCK)
                      substrate only; NOP in z80)                                        or none (BYTEWISE)
 stack / PUSH route   none                             none                              none (LD SP,nn loads nothing)
 self-location        fixed: own [0,G), nbr [128,+G)   fixed: own [0,L), nbr [L,2L)      factor: SELF / GETPC / NONE
 partner executable   yes (pc>=G runs nbr bytes,       yes (SHARED layout; PAIR runs     yes in PAIR_TAPE (one arena);
 in own address space exec_foreign)                    one 2L program)                   no in private-slot worlds
 tape size            32 / 64                          32 / 64                           32 / 64 / 96
 pairing rule         run against one neighbour per    partner by spatial policy; PAIR   PAIR_TAPE concatenation, or
                      input case                       concatenates 2L                   ALLOC/BIRTH into a slot
 descendant predicate write >= 90% of the nbr window   all L window bytes (COPY), >= L/2 BIRTH of an ALLOC slot, or pair
                                                       (PAIR/OVERWRITE/CONSTR), >= 1     overwrite (0.9 fidelity)
 mutation operators   local_byte/operand/opcode/       OPERAND/OPCODE/BYTE/STRUCTURAL    OPERAND/OPCODE/BOTH x LOCAL/
                      structural; copy noise .004,     at .002/.008/.03                  STRUCTURAL at .2/1/4 %
                      background .02
 reproduction physics the directive's six, by name     the directive's six, by name      the directive's six, by name
 pressure list        the directive's list             the directive's list              the directive's list
 material channels    transplant (late verification),  POLLINATION/RESERVOIR copy-       RECOMBINATION splice axis,
 run by the harness   migration, recombination         migration, transplant             implants, reservoir
 task coupling        competence/resource gated etc.;  IMPLICIT default is inert (inflow NONE_IMPLICIT .. PREDATION;
                      envgate line: none               >= cost); v3 copy-resource ledger the task never copies

What these rows share by construction:
- The directive's named physics, pressures, mutation-operator family and material channels (directive
  lines 40-50 and 60).
- A supplied copy instruction and no stack route (all three).
- A partner or neighbour that can execute inside the executor's own address space (Archaeon, BEE, NPE pair tape).
- A fixed absolute own/neighbour frame (Archaeon, BEE).
- The design of the donor paper (Z80 soup, arXiv 2607.09211). The directive calls it "a donor of machinery"
  (line 24) and asks for "analogues of the paper's phenomena" (line 68).

3. RESULT
---------
Each recurrence below is followed by the shared factor that would produce it (T2) and the arms that remove that
factor (T3).

(0) Heredity needs the supplied copy op.
    Entailing factor: a supplied copy instruction and no stack or PUSH route (all three builds).
    Arms that remove it, in all three engines:
    - BEE, LDIR off: spontaneous self-replication 0/300, against 8/300 at base (p = 0.004).
    - BEE, undefined byte = HALT: 0/300 against 8/300 (p = 0.004).
    - Archaeon, z80 substrate (COPY is a NOP): 0 copiers of any grade in 1.2e7 random tapes (95% upper bound
      3.7e-7). The vmcopy32 substrate gives 96 exact copiers per 1e7.
    - NPE, BYTEWISE (no LDIR): 10/500 P-11 survivors, against 47/531 with BLOCK (p = 6e-7).
    - NPE donor genomes: all 10 BYTEWISE donors are homopolymers (modal-byte share 0.91-0.96). 33 of the 47 BLOCK
      donors are not (share < 0.8). Certified copiers that are not homopolymers: 0/500 against 33/531
      (p = 2e-10).
    Verdict: vanishes in 3/3 engines. DESIGN-BOUND. The published soup without a block copy (arXiv 2406.19108,
    BFF) and the real Z80 (PUSH copiers) do not need such an instruction. So the necessity comes from an ISA
    choice the three builds share. It is not a fact about Z80-like soups in general.

(1) Harness channels get credited to organisms.
    Entailing factors:
    - (a) The directive requires channels that move material: pollination and reservoirs (line 46), residue and
      lineage transport (line 50), recombination (line 50), lineage transplantation (line 60).
    - (b) One model family wrote the first rulers for one operator on the same morning.
    In each engine, the false credit sits only in arms that have such a channel:
    - NPE, PAIR_TAPE random runs: 910/981 flagged spontaneous (93%) with the RECOMBINATION splice, against
      121/654 (18.5%) without it. Share of flagged runs that survive P-11: 35/910 (3.8%) with the splice, against
      22/121 (18%) without.
    - BEE: with POLLINATION copy-migration, spontaneous 20.0% and extinction 0/150. With move-migration on the same
      seeds, spontaneous 1.3% and extinction 148/150. ISOLATED shows no difference (grounding G7P1).
    - Archaeon: all 26 flagged runs were transplant-verification runs. The operator handed Archaeon this defect
      and pointed it to BEE's implementation "as a reference" (a3325b392:39-40, 92-93). So this discovery was not
      independent either.
    Once the channel is removed, the phenomenon is gone by definition. What recurs is a builder blind spot, and
    the builders are correlated.
    Verdict: DESIGN-BOUND and builder-correlated. It is a sound checklist rule ("who else could have copied this,
    including the harness"), not a law.

(2) Core conserved, cargo erodes unless paid.
    Entailing factors: selection sees only copying, and the copy core consists of the supplied primitives.
    - BEE:
      * Under endogenous reproduction, seeded task code erodes (discordant pairs: EXTERNAL-only 178,
        ENDOGENOUS-only 2).
      * Under the default IMPLICIT pressure the task is inert by construction (inflow >= cost).
      * Paying for the cargo (v3, contingent copy resource) removes the erosion: 0.77 of the world stays
        competent, against about 0 in the YOKED and OFF arms (149 vs 0 pairs).
      * This is the claim's own "unless paid" clause. It is the textbook mutation-selection (Spiegelman)
        expectation that the synthesis itself cites.
    - NPE:
      * The conserved "core" is exactly the two supplied world ops: SELF (25-27 of 27 runaways) and LDIR (19-25
        of 27).
      * The "cargo" is founder bytes (founder share 0.134 in the specimen's own cell, 0.253 in a foreign cell),
        not task code.
      * The specimen cells are PAIR_TAPE + BLOCK, with QD or IMPLICIT pressure.
      * Without LDIR (BYTEWISE) there is no non-homopolymer copier at all, so there is no core to conserve.
    - Archaeon: never measured (the synthesis says it is inferred).
    Only BEE has an arm where the cargo is paid, and there the erosion disappears as the textbook predicts. No
    engine shows erosion that persists once its factor is removed.
    Verdict: the "core" half is DESIGN-BOUND. The erosion half reproduces a known result. As a cross-engine law
    it is UNTESTED.

(3) Acquisition is easier than maintenance.
    This claim is badly posed, and the synthesis's own BEE evidence contradicts it.
    - Task competence in BEE runs the other way:
      * De novo acquisition happened only for ECHO: 29/150 at one parameterization, 7/150 at the other.
      * CONST: 0-1/150. Fully random worlds: 0/3,200.
      * Maintenance under coupling holds 149/150.
    - Replication in BEE: acquisition 2.3% per run, and 39.4% of acquisitions are sustained. These numbers have
      different units, so neither ordering follows from them.
    - The "easy acquisition" part comes from the supplied copy op. Removing it drops acquisition to 0 in all
      three engines (see (0)).
    - The Archaeon "establishment barrier" comes from its fixed absolute frame:
      * 81 of 96 exact copiers in the census are gated on input byte 128, the hardcoded neighbour-window base;
        89/96 on 125-129.
      * In vmcopy64, 9/9 exact copiers are gated on 126-128.
      * So 89/96 exact copiers need an input inside 120..135. That is exactly the band whose blocking "suppresses
        establishment", the gating line's strongest finding. The result is the address layout acting through the
        input stream.
    Verdict: DESIGN-BOUND and ill-posed.

(4) Origins are scaffolded.
    Entailing factors: a partner that can execute inside the executor's address space, and a birth definition
    under which every organism after t=0 was written by another. In BEE, lifespan 40 means that after tick 40
    every organism is copy-born.
    - NPE: flagged spontaneous in 1,031/1,635 PAIR_TAPE runs, against 0/1,554 in SOUP_MEM, GRID and GRAPH
      (95% upper bound 0.19%), reproduced from INDEX. Bound to the pair tape.
    - BEE: spontaneous self-replication also appears outside PAIR_EXECUTION (COPY 5/400, CONSTRUCTIVE 6/400,
      OVERWRITE 3/400, PARTIAL 19/400). The claimed 160/160 BUILT_BY_COPY is an INSTRUMENT DEFECT (details
      below).
    - Archaeon: host-mediated reproduction needs the executor to run neighbour bytes (exec_foreign), which the
      shared 256-byte frame provides. Tierra parasites are the known precedent (G_PRIOR_ART).
    Verdict: DESIGN-BOUND in all three. The BEE leg also rests on a misclassification.

    The BEE defect in detail:
    - Initial organisms are spawned with mechanism "init", but world.birth_class is filled only in
      _register_offspring (world.py:494@a1b066309; still world.py:544 on main).
    - So world._genealogy reports mechanism None for an initial organism.
    - grounding_analysis.g6_class tests w["mechanism"] == "init", which can therefore never be true.
    - The CLIFF_AT_INIT and MUTATED_INIT classes are unreachable, and every origin is labelled BUILT_BY_COPY
      whatever the data say.
    Evidence in the committed rows:
    - 24 of the 160 origins have their first self-replicator at tick 0.
    - Exactly those 24, and no others, have a genealogy with no ancestor and a writer whose tape at birth already
      self-copies (steps = None).
    - These 24 are unmodified initial random tapes.
    The new null model predicts this independently:
    - 45 of 1,000,000 uniform random 64-byte tapes (4.5e-5; all 45 hits pass with 10/10 random partners and v2
      strict budget) are world-grade self-replicators on first execution, typically LD T,0x40 ... LDIR over a
      NOP slide.
    - The grounding pool has about 5,100 RANDOM runs x 128 initial tapes, which gives about 29 expected
      initial-tape origins. 24 were observed.
    So at least 15% of BEE origins were not built by anyone. Up to about 13 more may be mutated initial tapes.
    The corrected claim is: "origins after tick 40 are copy-born because every organism then is".

Verdict per recurrence (T4):
    (0) supplied copy op needed       DESIGN-BOUND (vanishes in 3/3 engines when removed)
    (1) harness credited              DESIGN-BOUND + builder-correlated (vanishes with the channel in 3/3)
    (2) core conserved / cargo erodes core: DESIGN-BOUND; erosion: known result; cross-engine law UNTESTED
                                      (1 engine has a paid-cargo arm, and there the erosion vanishes)
    (3) acquisition < maintenance     ILL-POSED; each component DESIGN-BOUND
    (4) origins scaffolded            DESIGN-BOUND; the BEE 160/160 figure is an instrument defect (true figure
                                      <= 136/160)
    Survives in 2 or more engines with its factor removed: none.

Plain conclusion. None of the recurrences in the synthesis's "only because three engines looked" section
survives removing the design choice that produces it, in any engine where committed data include such an arm.
The three builds are three implementations of one directive that paraphrases one published design. They check
each other's implementations. They are not three independent sightings of a law.

4. DID IT RESOLVE THE QUESTION
------------------------------
Mostly yes. The factor matrix and the recurrence-to-factor mapping cover all five recurrences.
- (0), (1) and (4): arms with the factor removed exist in 2-3 engines and were tallied.
- (2): only BEE has a paid-cargo arm, and Archaeon never measured erosion. The recurrence cannot be promoted,
  but it is not refuted as a generic tendency either; it is the textbook expectation.
- (3): could not be tested as stated, because its two sides have no common unit.
Not audited:
- The 09-19 prompts actually given to Archaeon and Nestor (only Bellerophon's copy is committed).
- Whether BEE and NPE were prompted to their harness-channel discoveries (I checked only Archaeon's).
- BEE numbers that exist only on the M2 host (cited from committed reports, not recomputed).
- How many of the 44 non-ramp early BEE origins are mutated initial tapes. That needs the M2-local run records.

5. CONSEQUENCES
---------------
- False premise (main finding). The claim that "three independently written worlds, three independent teams
  ... make it a design law" does not hold. Independence exists only at code level. Every listed recurrence traces
  to a shared choice:
  * the directive's mandated channels and physics;
  * a supplied copy op with no stack route;
  * a partner frame the executor can run;
  * a fixed absolute neighbour address.
  The section should be restated as "three implementations of one published design (via one directive) recover
  that design's phenomena". This agrees with the prior-art reading that the origin-of-replication question is
  largely answered.
- Harness / instrument defect (BEE; Bellerophon should fix). The G6 origin classifier cannot emit its
  initial-tape classes. world._genealogy has no birth_class entry for "init" organisms, and g6_class tests
  mechanism == "init". Result: "160/160 first self-replicators BUILT_BY_COPY (incl. all 87 at tick <= 41)" is
  wrong. At least 24/160 origins are unmodified initial random tapes, in line with a 4.5e-5 per-tape null.
  Fix: record "init" in birth_class at spawn, or test parent is None; then rerun the analysis (seconds on the
  committed rows).
  This also removes the BEE leg of the "origins are scaffolded" recurrence, and it bears on the prior-art note
  that called 160/160 "a stronger scaffolding-of-origins result".
- Internal inconsistency (Archaeon, the synthesis author). Recurrence (3) cites BEE task data showing that
  acquisition is the harder step.
- Small new mechanism result (Archaeon gating line). 89/96 exact copiers are triggered by an input byte in
  125-129, around the hardcoded neighbour base 128. Blocking inputs 120..135 therefore removes the trigger for
  about 93% of copiers. "Environment gates establishment" should be reported as a consequence of the frame.
- For the program:
  * Treat the triplication as an implementation check. For the keep-or-consolidate retrospective, this supports
    consolidating, or running one shared assay on all three engines.
  * Do not pay for runs of the published soup through our rulers, or for a dissimilar substrate, on the strength
    of this section alone.
  * The one open question the Z80 builds cannot answer is whether heredity arises without a supplied copy op. A
    fourth arm that differs only in that choice (a stack/PUSH route or a BFF-style ISA) is where a real law test
    would start.
- Cargo-erosion law thread: downgrade to "reproduces the known Spiegelman / mutation-selection expectation in one
  engine that has a paid-cargo control; untested elsewhere".
- A reusable instrument: the design-lineage table in section 2 (directive -> donor paper -> build factors ->
  which recurrences they entail). A varied=/held= field on every cross-engine claim would make this audit routine.
- Who should know:
  * Bellerophon: the G6 defect and the random-tape null.
  * Archaeon: author of the synthesis; the gating-line entailment.
  * Nestor: the pair-tape and BYTEWISE numbers.
  * The owners of the keep-or-consolidate retrospective and of the cargo-erosion thread.

6. COST
-------
- Time: about 2.5 hours of agent time.
- CPU: about 25 CPU-minutes in total. The two null-model passes were 2 x 500,000 tapes each on 2 processes; the
  tallies took seconds.
- No GPU, no services, no writes to the repository.
- Not done:
  * re-running any engine's campaigns;
  * auditing the 09-19 prompts given to Archaeon and Nestor;
  * recomputing M2-only BEE numbers;
  * measuring cargo erosion in Archaeon or in a task-coupled NPE arm (no such committed data);
  * rerunning BEE's G6 analysis with the fix (the raw rows are M2-local).
