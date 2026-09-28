# CENSUS A -- competence acquisition in the Z80-family engines (NPE, BEE, Archaeon) and Crius

Currency: 2026-09-28. Odysseus research worker (disposable), ubu001, worktree odysseus-base-role at
7720539d4. Directive: roles/Odysseus/prompts/2026-09-28_expeditionary/01_OPERATOR_DIRECTIVE_verbatim.md s5
("Produce a table of the strongest surviving cases, not a rhetorical claim that there are none. If you find
one real counterexample, the census succeeds."). Ladder: roles/Odysseus/expedition/accumulation/ACCUMULATION_v0.md.
Brief: roles/Odysseus/frontier/poi/ready/R5_acquisition_census.md. Builds on (does not repeat) Artemis
FR-010 / FR-011 (roles/Artemis/backlog/threads/) and spike S1 (roles/Odysseus/frontier/poi/spikes/S1_copyless_sr/).
Pure ASCII. Read-only census: no campaign run, no verdict of any seat changed. Numbers marked
COMPUTED-HERE are stdlib re-reads of committed rows made for this file (seconds each).

## 0. The test, stated before the rows

A row is one CLAIMED competence (a capability some record says arose). It is classified from what was
done to it (interventions, baselines, assays), never from its name. Q1-Q8 are the directive's questions:

    Q1 already encoded in primitives?          Q5 selection among pre-existing affordances only?
    Q2 task installed (is it the paid task)?   Q6 a new reusable object generated?
    Q3 solution template seeded (byte/func)?   Q7 did the object change the ceiling for a FRESH receiver?
    Q4 representation authored for it?         Q8 could a pristine system reproduce it at matched compute?

Codes: Y yes, N no, P partly, ? not in the record, - not applicable.
SURVIVES = the competence is absent from every seed / fixture / inflow by a functional check (Q3 not Y),
is not the named solution of a paid task (Q2), is more than one supplied primitive (Q1 not Y), is not
shown to be mere sampling of pre-existing material (Q5 not Y), and no pristine / random-sampling baseline
in the record reproduces it (Q8 not Y). This is R5's (a)-(c); R5's (d) replication is reported, and a
survivor with weak replication is marked "narrow" or "provisional".
FAILS(Qn) = the record decides Qn against the claim. UNDECIDABLE = the record cannot decide the deciding Q;
the single cheap check is named.
RUNG: no row in part A has had ACCUMULATION_v0's own controls run (history-ablated twin, record deletion
and permutation, producer destroyed). The rung given is the highest whose FALSIFIER the record's own
controls address; "~" marks that the control is analogous, not the ladder's. R1~ therefore means "the
lineage keeps and reuses the object; no deletion twin was run".

## 1. Search log (mandatory prior-work search)

Commands (read-only):
- all 73 origin refs + HEAD, engine and seat paths (roles/Nestor roles/Bellerophon prometheus/z80atlas
  archaeon ops/campaigns/C-001 roles/Crius roles/Odysseus roles/Artemis):
  `git grep -I -i -l <term> HEAD $(git for-each-ref --format='%(refname)' refs/remotes/origin) -- <paths>`
  distinct files per term: acquire 98; acquisition 127; "de novo" 18; novel 251; emerged 8;
  competen 1,367; C-SWAP-ACQUIRE 12; ECHO 162; transplant 472.
- HEAD engine paths only (roles/Nestor roles/Bellerophon prometheus/z80atlas archaeon ops/campaigns/C-001
  roles/Crius crius): acquire 79, acquisition 96, de novo 7, novel 215, emerged 5, competen 1,603,
  C-SWAP-ACQUIRE 6, ECHO 128, transplant 740 files. Branch-only refs that carry unmerged engine content
  (checked with `git rev-list --count HEAD..origin/<b>`): origin/nestor/s1-forensics-2026-09-23 (13 commits,
  NPE ARC3 2026-09-28), origin/artemis/challenge-2026-09-28 (8), origin/bellerophon/multiday-campaign-2026-09-26
  (prereg + launch only). All other nestor/*, archaeon/*, bellerophon/*, worker/W1, worker/W2 refs: 0
  commits beyond HEAD.
- "competen", "novel", "transplant" are dominated by field names and ruler labels (competence share,
  NOVEL_REPRODUCTIVE_MECHANISM_CANDIDATE, transplant arms); they were read only where they sit in a
  claim sentence.

What the search found (claim sentences, each became a row or was ruled out):
- roles/Nestor/FINDINGS.md:337-366 @fdc73636f -- X-SWAP-ANCESTRY, C-SWAP-ACQUIRE NOT CONFIRMED 9/240 vs
  0/240, X-ACQUIRE WEAK_SIGNAL "9-15% ... carry genomes that copy from a fresh state where the founder
  cannot", X-CONTENT caveat. -> row N1.
- roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/W1_REPORT.md @90390a4ef and P2 SYNTHESIS.md
  @fdc73636f -- spontaneous donors, C-DENSE-COPY, X-P2-PLANT, SELF-free copiers. -> rows N2-N4.
- origin/nestor/s1-forensics-2026-09-23 (branch-only) roles/Nestor/FINDINGS.md ARC3 block and
  campaigns/npe-arc3-2026-09-28/ -- "robustness DID arise within D0's lineage ... internalized register
  initialization" (X-A3-FORENSIC-16000006, df0964ef3), X-A3-SFLINEAGE SIGNAL 3/5 (86f929241), C-A3-INTERNALIZE
  frozen, not run; accessibility delegate "no random genome or its 1-2-step mutants is competent (0/6,400)"
  and "a neutral mutation walk reaches competence at about the soup's rate (pilot: ratio 1.75, p = 0.20)"
  (948b3a45f); LOCATOR motif (SELFLOCATION.md). -> rows N3, N5, N6, N2.
- roles/Nestor/campaigns/cw01-2026-09-17/loop/BOUNDARY_REPORT_CYCLE8_2026-09-19.md:32,40 @3af735d67 --
  "ACQUIRED MACHINERY CHANGES WHAT IS REACHABLE - PARTIALLY, AND WITH A FLAG" (seeded XOR-1 routing). -> N11.
  Cycle 3 "the e06 ecology acquired a rate window" is a parameter-sweep description, not a competence: ruled out.
- roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md:47-98 @6a0b9813e -- "Genuine GAIN from a
  population with no task code occurred in one place only ... ECHO K40 ... 29/150 ON vs 6/150", "4
  transplanted de novo acquirers", E2 "repair_emerged". -> rows B2, B3, B4.
- roles/Bellerophon/forensics_2026-09-23/ @3efdacf7e -- spontaneous own-code SR CONFIRMED_CAUSAL, basin,
  HIST ablation. -> B1, B5, B6. Multi-day branch: prereg + launch, no results in any ref. -> B7.
- archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md:223-225 @2b3661444 -- "an EXACT_UNGATED copier ...
  evolved inside the world. Gating DISAPPEARED once a lineage took over"; LINEAGES.json summary
  "gate_change_dominant": {"acquired": 6}. -> row A1 (the strongest case below).
- archaeon/z80atlas/pivot/ (census, post-campaign review), ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/ (A0 lens,
  D synthesis s3 point 3 "acquisition ... easier than maintenance") -> A2-A7.
- roles/Crius/STATUS.md @8ad374ed5 and review packets C0/C1b/C2 -> C1-C3.
- Prior syntheses read, not duplicated: raw/I1_z80_lineage_worlds.md T1, T3, T11, T14-T17 and s3
  reversal table; Artemis FR-010 (convergence is design-bound), FR-011 (heredity = the supplied copy op;
  BYTEWISE certified heredity ~0 bits); Artemis challenge MATURE_REVIEW (branch) FR-011 split into 011a/011b;
  FR-043/FR-044 (fresh-receiver ceiling; non-Z80, part B).

## 2. The table (28 rows)

    ID   engine    claimed competence                          Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8  rung  verdict
    ---- --------  ------------------------------------------  -- -- -- -- -- -- -- --  ----  -----------------------
    A1   Archaeon  input-independent exact self-copying        P  N  N  N  P  Y  ?  N   R1~   SURVIVES
                   (EXACT_UNGATED) in ENVGATE-01 takeovers
    N5   NPE       internalized register initialization       P  N  N  P  P  Y  ?  ?   R1~   SURVIVES (provisional)
                   (state-free copying) within a lineage
    N1   NPE       fresh-state copying in foreign cells the    P  N  P  N  P  Y  ?  N   R1~   SURVIVES (narrow)
                   founder cannot copy in (X-ACQUIRE)
    N2   NPE       spontaneous competent donor, plain VM       P  N  N  N  P  Y  ?  ?   R1~   UNDECIDABLE (Q8)
    B7   BEE       task-ladder acquisition ECHO->INC->COND,    ?  Y  P  N  ?  ?  ?  ?   NONE  UNDECIDABLE (no results)
                   repair (multi-day campaign)
    N3   NPE       donors with the 1-byte copy alias           P  N  N  Y  P  Y  ?  Y*  R1~   FAILS (Q4; Q8 pilot)
    N4   NPE       donors from planted ED B0/B8 (X-P2-PLANT)   P  N  P  N  P  Y  ?  ?   R1~   FAILS (Q3)
    N6   NPE       position-free LOCATOR copier (1 motif)      Y  N  N  P  P  Y  ?  ?   R0~   FAILS (Q1)
    N7   NPE       non-pair spontaneous replication (C-DENSE)  P  N  N  Y  P  Y  ?  ?   R1~   FAILS (Q4)
    N8   NPE       heredity of implanted copiers (C-SELFLOC,    P  N  Y  N  Y  N  N  -   R1~   FAILS (Q3)
                   C-ATOMIC, C-RUNAWAY, C-CORE)
    N9   NPE       72-h "spontaneous replicators"; BYTEWISE    Y  N  N  N  Y  N  N  ?   NONE  FAILS (Q6)
                   certified heredity
    N10  NPE       task competence 0.20 (C9-H1R)               Y  Y  N  N  Y  N  N  ?   NONE  FAILS (Q5)
    N11  NPE       seeded routing opens ADD-1 (cw01 cycle 8)   P  Y  Y  N  Y  N  P  ?   NONE  FAILS (Q3)
    B1   BEE       spontaneous own-code self-replication       Y  N  N  N  Y  Y  ?  P   R1~   FAILS (Q1, Q5)
    B2   BEE       ECHO acquired by pure copiers (B-cop)       Y  Y  P  N  Y  Y  N  Y   R1~   FAILS (Q5, Q8)
    B3   BEE       repair of a self-wrecking copier (E2)       P  Y  Y  N  Y  Y  N  ?   R1~   FAILS (Q3, Q5)
    B4   BEE       CONST acquisition; B-rand origin            -  Y  N  N  -  N  -  -   NONE  FAILS (nothing arose)
    B5   BEE       copy-op re-creation after HIST ablation     Y  N  Y  N  Y  N  -  -   R1~   FAILS (Q3, Q5)
    B6   BEE       72-h flag classes (1,629 flags)             -  -  -  -  -  N  -  -   NONE  FAILS (collapsed)
    A2   Archaeon  random-inflow exact copiers (gated)         Y  N  N  N  Y  Y  ?  Y   R1~   FAILS (Q5, Q8)
    A3   Archaeon  host-mediated reproduction (363 lineages)   P  N  N  N  Y  N  N  ?   NONE  FAILS (Q6)
    A4   Archaeon  Z80xAtlas 26 spontaneous-replication flags  -  N  Y  N  -  N  -  -   NONE  FAILS (Q3)
    A5   Archaeon  DENOVO-01 de novo replication               -  N  N  N  -  N  -  -   NONE  FAILS (0/80)
    A6   Archaeon  task competence carried by transplants      -  Y  Y  N  -  N  N  -   NONE  FAILS (0/39 travels)
    A7   Archaeon  ENVGATE-02 BAND0 establishments             Y  N  N  N  Y  Y  ?  ?   R1~   FAILS (Q5)
    C1   Crius     C0 search products (orders, scripts)        P  Y  P  Y  Y  N  N  ?   NONE  FAILS (Q5)
    C2   Crius     C1/C1b cheaper counter enumerators          P  Y  Y  Y  Y  N  N  ?   NONE  FAILS (Q3)
    C3   Crius     C2 procedure reuse (block / typed control)  N  Y  Y  Y  -  Y  Y  -   R2*   FAILS (Q3, Q4: authored)

    Y* (N3): pilot only, p = 0.20. R2* (C3): the R2-shaped transfer holds for an EXPERIMENTER-BUILT object
    (a planted known answer in ladder terms), and search never reached it (0/36).
    Verdict counts: SURVIVES 3 (A1, N5, N1); UNDECIDABLE 2 (N2, B7); FAILS 23.
    Crius is not a Z80 engine; it is in part A by assignment.

### 2.1 Row evidence (path@sha; COMPUTED-HERE numbers were recomputed for this file)

A1 Archaeon ENVGATE-01 EXACT_UNGATED copier. archaeon/envgate/LINEAGES.json, RESULTS.json @e15e4cde6;
   ENVGATE01_REVIEW_2026-09-24.md:153,221-225 @2b3661444; ADJUDICATION_ADDENDUM_2026-09-24.md:12 @16111cf50.
   - Competence: a 32-byte tape that copies itself exactly at ALL 256 input values. The inflow's copiers
     are gated: they read the copy destination from the input stream and are exact only when the input
     names the neighbour window (census: 94/96 exact at one input; Z80ATLAS_RULINGS_FOLLOWUP_REVIEW:100-116
     @863d34a55).
   - Q3 N: ruler classes over the 33,554,432 arrivals (the same arrivals in every arm): EXACT_GATED 265,
     EXACT_UNGATED 0 (RESULTS.json ruler_counts_per_arm). The block-15 founder was gated at 255.
   - Material (COMPUTED-HERE, opcode level b & 31, best of 32 rotations): the ungated residents differ from
     every copier founder of their block at 26-29 of 32 positions.
   - Where (COMPUTED-HERE): ungated dominant descendants in exactly 6 of 80 world-arms: block 13 BLOCK_128,
     and block 15 in all five arms (U, SHAM, BAND, BLOCK_128, RESCUE). These are the 6 takeover worlds.
     30 distinct ungated tapes, 0 shared between world-arms. Two independent blocks of 16.
   - Q2 N: there is no task; copying is favoured by the physics, but "ignore the input" is not named.
   - Q8 N (random sampling at matched stream): this world's own inflow is a random sampler at larger count
     than its in-world births, and delivered 0 of 3.36e7. A random mutation walk from the gated founders at
     matched compute was NOT run.
   - Q5 P: the CLASS exists in random material at about 1e-7 per tape. The census found 1 "COPY ungated
     input-blind" in 1e7. In ENVGATE-02 (archaeon/envgate2/RESULTS.json @c5ba19571, established_glins;
     I1 T3), two EXACT_UNGATED ARRIVALS (block 13 #541685, block 14 #74051; 24 blocks x 1,048,576 arrivals)
     founded takeovers directly. So A1 is a rare class reached in-world, from gated copiers, far faster than
     sampling would predict (about 0.1 expected in about 1e6 births). It is not a class sampling cannot
     reach.
   - Provenance of the first ungated genome is not recorded. The parent chain is unusable here (block 15's
     many host labels collapse to one resident lineage; ENVGATE_CLOSURE_2026-09-26.md:27). So "mutated out
     of a gated copier" versus "assembled by host-mediated copying" is open.
   - Q7 ?: INERT hosts facing the resident emit exact copies of it (23 of 63). The benefit goes to the
     object, not to the receiver. No fresh-receiver ceiling test exists.
   - Rung R1~: the object persists and dominates its world, is history-specific (not in the other 74
     world-arms), and is not initial. There is no deletion twin.

N5 NPE within-lineage internalization of register initialization (branch-only, 2026-09-28).
   origin/nestor/s1-forensics-2026-09-23 @d2dba36f7: campaigns/npe-arc3-2026-09-28/x_a3_sflineage/SUMMARY.json
   (86f929241), delegates/forensic_16000006/ (df0964ef3), x_a3_fair/ (64e44dcba), c_a3_internalize/run_ci.py.
   - Competence: STATE_FREE copying, i.e. competent from two fixed random register entry states. The
     genome sets the registers it uses instead of taking them from the world's zero reset.
   - Q3 N: random populations. In all 5 tracked runs every first donor (D0) is not state-free.
   - Acquisition: in 3 of 5 (7ae3 16000006, 7ae3 16000021, ffa6 16000030), 100% of the late state-free
     genomes are in D0's replication lineage. These are three independent lineages in two cells.
   - Mechanism (16000006): distributed change (49-54 of 64 bytes, 118-126 replications); the copier fixes
     its own destination (LD DE,3200 before LDDR). Knock-in gives a partial effect (0 -> ~0.33); no single
     change does it.
   - Q4 P: dense VM (a 1-byte LDIR/LDDR alias authored for accessibility). The alias concerns copying, not
     state-freedom.
   - Q8 ? (COMPUTED-HERE from the 48 committed x_a3_fair CARRIED rows): 20 of 49 first-donor genomes are
     competent from both R1 and R2, and all 20 come from ONE of the 22 donor runs. De novo state-free first
     donors are therefore rare (1/22 runs). But no neutral walk from the D0 genomes was run.
   - Replication: post hoc, n = 3. The frozen confirmation C-A3-INTERNALIZE (144 fresh runs, bar >= 4
     events) is PLANNED and not run.
   - Q7 ?. Rung R1~.

N1 NPE X-ACQUIRE / C-SWAP-ACQUIRE. roles/Nestor/campaigns/c9x-explore-2026-09-24/x_acquire/SUMMARY.json,
   c_swap_acquire/VERDICT.json @778f00e90; FINDINGS.md:337-366 @fdc73636f; x_content @5646ade00.
   - Competence: fresh-state P-11 copying in cells 9cba (self_location PC_RELATIVE) and e160 (NONE). There
     the implanted 7ae3 founder's assay rate is 0.0, because its OP_SELF is not in the ops mask.
     Competent shares at the end: 0.090 and 0.148. The top genome's assay rate is 1.0 (9cba) and 0.35 (e160).
   - COMPUTED-HERE (z8.dis): the founder carries SELF (ED 32 at 23) and LDIR (52). The 9cba top genome
     carries LDIR at 55 and no ED 32 / ED 33. The e160 top genome carries LDDR (ED B8) at 52, one operand
     bit away from ED B0. Both copy without the self-location primitive.
   - Q2 N: 9cba pressure NONE_IMPLICIT; e160 QUALITY_DIVERSITY over (task competence, span)
     (MANIFEST_FROZEN.json cells; grammar.py:70-83 @aa5833488).
   - Q3 P: the functional template is absent in these cells (0.0). The founder MATERIAL is required
     (RANDOM implant: 0/240 runaways), and 13-25% founder bytes survive (X-CONTENT). This is re-acquisition
     from a seeded near-template.
   - Q8 N on the runaway endpoint (RANDOM implant 0/240, same cells, matched epochs). The competence assay
     was never run on the RANDOM arm.
   - Replication weak: n = 2 assayed runs (WEAK_SIGNAL). C-SWAP-ACQUIRE missed its bar (9 vs 10).
   - Rung R1~.

N2 NPE spontaneous donor, stock VM. W1 x_donor_discovery/SUMMARY.json @90390a4ef (1/96);
   c_dense_copy/VERDICT.json @a165ce841 (PLAIN 1/64); P2 SYNTHESIS s4.
   - Competence: SELF-free LDIR/LDDR copying that takes HL from never-written zero registers and the fixed
     tape layout (Q1 P).
   - COMPUTED-HERE: the 96 X-DONOR-DISCOVERY runs screened 490,675 distinct genomes at checkpoints
     (244,916 in 7ae3 runs + 245,759 in ffa6 runs) for 1 competent lineage (first at epoch 400).
   - Q8 ?: the random-sampling record is only 0/6,400 (random genomes and their 1-2-step mutants; ARC3
     accessibility delegate, branch). The neutral-walk pilot in PLAIN is 0/12 vs 0/12 (uninformative).
     WP-5 / T-ACQ-4 (uniform and walk hazards) is LIGHT and not run (WP-5_acquisition_rivals.md @9ce37a9d5).

B7 BEE multi-day. origin/bellerophon/multiday-campaign-2026-09-26 @ee7a7d954 (MULTIDAY_PREREG.md, frozen
   12ce26e23).
   - 4,160 runs, launched 2026-09-26T16:40:28Z, "blind until md_analysis.py runs". No result in any ref.
   - Its LADDER1 lane seeds the campaign's own ECHO acquirers and pays INC. It is therefore the first
     R6-SHAPED test in part A ("does an acquired object raise the rate of acquiring a new one"), but only
     if compared against the REP-only lane.

N3 C-DENSE-COPY 39/64 (a165ce841); X-P2-ATTRIB 372/372 through the alias.
   - Q4 Y: the 1-byte alias is authored.
   - Q8 Y*: neutral-walk pilot, soup vs walk ratio 1.75, p = 0.20 (ARC3 compare.json, 948b3a45f). "No
     evidence yet that the soup helps FIRST APPEARANCE".
N4 X-P2-PLANT 32/96 (0a93d8ad1): ED B0/B8 is written into every initial genome, i.e. a byte-level partial
   template.
N6 LOCATOR (SELFLOCATION.md:37-43,150, branch): 2 genomes, 1 motif, 1 seed (16000026), both SELF-dependent.
   The position-freedom comes from the supplied ED 32 SELF.
N7 C-DENSE 13/40 (c_dense_confirm @4309646db): authored 1-byte ALLOC/LDIR/BIRTH encodings. Supplied free
   self-location is necessary (C-ABLATE 15 -> 1).
N8 FINDINGS.md E-6, C-ATOMIC, C-RUNAWAY, C-CRITICAL-MASS, C-CORE @fdc73636f: an implanted copier. C-CORE is
   maintenance of seeded SELF/LDIR under purifying selection (Aporia #621, accepted).
N9 FINDINGS.md:19-41 (1,031 -> 57 P-11, max depth 2); FR-011: all 10 BYTEWISE certified donors are
   near-homopolymers (0x36 self-paints). About 0 bits are inherited.
N10 FINDINGS.md E-9 C9-H1R: ungated competence is carried entirely by answer-before-read guessers, and no
   reader evolves. Gating on the cue drops competence to 0.000.
N11 cw01 BOUNDARY_REPORT_CYCLE8:32,40 @3af735d67: the XOR-1 routing is a seeded witness scaffold, in 1 of 2
   seeds, and the ADD-1 crossing was already standing variation at stage entry. This is the only NPE Q7-type
   claim, and its object is planted.

B1 POST_CAMPAIGN_FORENSICS.md s2.6, GROUNDING_REPORT.md P8 @3efdacf7e.
   - A uniformly random Z80_64 tape self-copies alone with p = 3.0e-5. The minimal copier `LD T,L ; LDIR`
     is 3 bytes behind an 80% NOP slide. LDIR off: 0/300 vs 8/300.
   - Q8 P: initial-population sampling predicts about 0.4% of runs, and about 7% enter the basin. 65% of
     first SRs were built by others' copies. A matched-compute sampling count was not made.
B2 COUPLING_CAMPAIGN_REPORT.md:47-53,89-93 @6a0b9813e; COUPLING_ORIGIN_LEDGER.jsonl; vm.py:233-247 @b2ee19847.
   - ECHO is `IN A ; OUT A` (the fixture witness_echo is those two bytes plus HALT).
   - COMPUTED-HERE: 9 of 29 K40-ON acquirers are within Hamming 2 of the seeded copier's 8-byte head.
     Example: LD T,64 becomes DB 58 + IN_A, and HALT is replaced, with OUT_A after LDIR.
   - Unpaid controls reach it 6/150 each. Real self-copiers among them: OFF 3, YOKED 1, SHUFFLED 3 (S1;
     I1 T14).
   - The transplants move the same tape into fresh worlds: fresh-world transfer of the producer, not a new
     receiver (Q7 N).
B3 E2 (report:57-62; P6 4/60 vs 0/60, p = 0.125). COMPUTED-HERE disassembly of the 5 E2 origins: in 4
   of them the BAD fixture `LD T,64 ; LDIR ; IN A ; INC A ; OUT A ; HALT` becomes `LD T,64 ; DB xx ; IN A ;
   INC A ; OUT A ; LDIR/...`. The leading LDIR is knocked out and the tail is replaced, which is 2 point
   edits. It gives the task-before-copy arrangement that is the seeded HYB fixture in lanes A/C/F/G. The
   5th (c002722, K40) is rearranged beyond the first 9 bytes.
B4 CONST 0-1 of 150; B-rand 0/3,200 (report:51-53).
B5 GROUNDING_REPORT.md:101-109: 126/345 byte-ablated tapes still self-replicate, and 124 of them by a copy
   op re-created at a new position in a wide basin.
B6 POST_CAMPAIGN_FORENSICS headline: 2 FALSIFIED, 1 INSTRUMENT_FAILURE, 2 CONFOUNDED / DETECTOR_ONLY.
A2 ENVGATE RESULTS.json: 265 exact copiers per 33.5M arrivals (7.9/M) vs census 9.6/M. The world receives
   what the random sampler delivers. The same holds for the ENVGATE-02 takeovers founded by EXACT_UNGATED
   arrivals (see A1).
A3 ENVGATE01_REVIEW:39-43: host-mediated reproduction "amplified residents ... It does not originate new
   genomes".
A4 Z80ATLAS_POSTCAMPAIGN_REVIEW_2026-09-23.md:13-19: all 26 flags are transplant verification runs; de
   novo 0 of 101,003.
A5 same review :33-36; A0_ARCHAEON_LENS.md:51 (0/80, controls 21/21).
A6 same review :21-23: 39/39 transplanted lineages persist; task competence travels 0/39.
A7 ENVGATE-02 VERDICT; I1 T3: BAND0 excess explained by window-independent ARRIVALS.
C1 REVIEW_PACKET_C0_2026-09-19.md s0 @ad623954f: enumeration orders and hard-coded scripts; none acquired
   state; all worse than the seed on held-out tasks.
C2 REVIEW_PACKET_C1B_2026-09-19.md s0 @1be65a336: cheaper counter enumerators (the seed's own strategy);
   the record-id clock is an exploit; no ACC > FRESH.
C3 roles/Crius/STATUS.md @8ad374ed5: reuse is executable when BUILT (block control 46.1 vs 20.7; typed
   control transplant 6/6/6 vs 1/1/0; PARTS +15.97). Search reached it 0/36.

## 3. Strongest surviving cases, ranked

1. A1 -- Archaeon ENVGATE-01: input-independent exact self-copying arose inside the world. Rung R1~.
   - It is the cleanest "not given" in part A. The capability is absent from all 3.36e7 random arrivals by
     a functional ruler. No task names it. It appears in 6 world-arms, from 2 independent blocks, as 30
     distinct tapes, none shared. It shares no opcode-level material with the copier founders of its blocks.
   - What is given: the COPY primitive and a fixed own/neighbour frame. The acquisition is ADDRESSING, not
     copying: the copier stops reading its destination from the environment.
   - Qualifier: the class occurs in random material at about 1e-7 per tape (ENVGATE-02 ungated arrivals;
     census). The world reached it from gated copiers faster than sampling would, but did not reach
     something sampling cannot.
   - What is missing: provenance of the first ungated birth, a random-walk baseline from the gated founders,
     any fresh-receiver test.
2. N5 -- NPE (branch, 2026-09-28): a lineage internalizes register initialization. Rung R1~.
   - Donors that copy only from the world's zero reset become, by descent, copiers that set their own
     registers. This happened in 3 independent lineages across 2 cells; the mechanism is traced in one.
   - De novo state-free first donors arise in 1/22 runs (COMPUTED-HERE).
   - Weaknesses: dense-alias VM, post hoc selection, confirmation frozen but not run.
3. N1 -- NPE X-ACQUIRE: descendants of an implanted copier acquire fresh-state copying in cells where the
   founder cannot copy. They drop the supplied SELF primitive and copy from fixed-geometry addressing (one
   switched LDIR to LDDR). Rung R1~.
   - Matched random-implant twin: 0/240 runaways.
   - Narrow: founder material is required, only n = 2 assays, and the confirmation missed by one run.

Pattern across the three survivors (a hypothesis, stated once): each is a lineage replacing a parameter
the environment or designer supplied with one it encodes itself:
- the destination address from the input stream (A1);
- register values from the zero reset (N5);
- self-location from the SELF opcode (N1).
In ladder terms none reaches R2: no object has been handed to a receiver that did not make it.
Every Q7 = Y in part A is an authored object (Crius C3; NPE cw01's seeded routing, N11).

## 4. Decisive cheap checks (ordered by information per CPU)

1. A1 provenance (replay, Archaeon engine is legacy-exact; minutes). Replay ENVGATE-01 block 15 arm U and
   block 13 BLOCK_128. Log the first birth whose tape the frozen ruler classes EXACT_UNGATED, with its
   writer, executor and source material.
   - Decides Q5 for A1: a point-mutant of a gated copier means A1 survives as mutation plus selection;
     assembly by host copying of arrival material means it survives as construction.
   - Add a neutral mutation walk from founder 1212310 (gated 255) at matched births for Q8-walk.
2. N2 / N3 T-ACQ-4 (WP-5 step 3, LIGHT, assay only, no world). Screen uniform-byte genomes and neutral
   mutation walks through the unchanged W1 screen on the stock VM, to about 5e5 evaluations. That is the
   soup's 490,675 checkpoint screens for 1 event, COMPUTED-HERE.
   - More than 1 competent means spontaneous donors are sampling (N2 FAILS Q8).
   - 0 means the soup beats sampling, and N2 joins the survivors.
3. N1 / N5 fresh-receiver and recurrence. First, the frozen C-A3-INTERNALIZE (144 runs, LEASED scale;
   decides N5's replication).
   - Cheaper and first: run the X-ACQUIRE assay on the 9 C-SWAP-ACQUIRE GENOME runaway end populations and
     on a sample of the 240 RANDOM end populations (replays, LIGHT). This decides N1's replication and its
     Q8 at the competence level, not just the runaway level.
4. B7: read md_analysis output when Bellerophon commits it (0 CPU). LADDER1 vs the REP-only lane is part
   A's only preregistered R6-shaped contrast.
5. Q7 anywhere: no Z80 row has a fresh-receiver test. The cheapest to build is A1. Graft the ungated
   resident's address block into a gated arrival (a receiver that did not make it) and score exact inputs,
   against a random-block graft. This is R2/R3 in one step.

## 5. Limits

- No ACCUMULATION_v0 control (history-ablated twin, deletion, permutation, producer destroyed, convention
  relabeling) has been run on any row. Every rung is "~", and no row is above R1~ except C3's authored
  object.
- Classification rests on committed rows and texts. BEE's multi-day and coupling runtime data and some
  Archaeon bundles are M2-only (FR-094). The M2 hosts were not touched.
- Q5 is a judgement at the ISA boundary: every Z80 competence uses supplied opcodes. Q5 = Y was given only
  when the record shows the competence already present in random material, or reachable by <= 3 point
  edits from a seeded tape.
- N5 and the ARC3 numbers are branch-only and less than a day old. C-A3-INTERNALIZE may overturn N5.
- The A1 opcode-distance and world-arm counts use LINEAGES.json's sampled dominant_descendants, not full
  final populations (Archaeon's probe did not record final genomes).
- Crius is not Z80 and is included by assignment. The Archaeon non-Z80 lines (campaign3-6, wse, rie) are
  out of scope for part A.
- One worker, one pass, no second rater. The Q-codes for P rows are the least stable cells of the table.
