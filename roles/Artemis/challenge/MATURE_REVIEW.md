# MATURE_REVIEW -- adversarial review of the seven MATURE threads

Artemis operator challenge 2026-09-28, item 4 ("Challenge the mature threads").
Reviewer: adversarial reviewer for Artemis (fresh session, not the thread author). Pure ASCII.
Mode: read-only over git. No engines, tests or replays were run. Read-only python over committed JSON
was used to check numbers. Refs: worktree HEAD a9d5f5f23 (artemis/challenge-2026-09-28);
origin/main c2b507e9e. "path@sha" pins the version read. Comms message numbers (#NNN) cannot be checked
from git (comms is a Postgres queue), so they are cited only where a committed file quotes them.

Operator standard: "A MATURE label should mean 'ready to survive attack,' not 'we have written a lot
about it.' Downgrade freely." For each thread this file argues the STRONGEST case for (a) answered,
(b) superseded, (c) badly posed, (d) instrument-limited, (e) split. Only attacks with force are
listed. Each thread ends with a verdict and an execute-now judgement against the challenge's s8
conditions:
- inputs committed;
- no GPU;
- no hidden holdout consumed;
- no other seat owns an active prereg on the same test;
- no more than about 1 CPU-hour on a 4-thread, 7 GB laptop;
- a stop rule that can be written in advance.

## 0. Cross-cutting findings (apply to all seven)

X1. The labels disagree with themselves. All seven thread files still say "State: SHARPENED"
(e.g. roles/Artemis/backlog/threads/FR-010.md:2@a9d5f5f23). INDEX.md:39-201 and FRONTIER.md:30-103
say MATURE. MATURE was assigned in the index because a chop exists (README.md:34 "sharpened + a chop
exists"). That rule measures paperwork, not survival under attack, which is exactly the operator's
complaint.

X2. Every thread went stale inside 24 hours. At least 5 of the 7 have new primary evidence from
2026-09-27/28 that the thread does not know about:
- FR-010: Block D merged to main; Archaeon narrowed point 2 itself.
- FR-011: Nestor ARC3 owns the question; NPE had already run the seeded BYTEWISE replicator.
- FR-035: Ananke W-G closed SI01 for current champions; the LM01 v0.3.2 amendment; M2 is now a
  predicted echo.
- FR-057: the Odysseus I6 catalogue is on main.
- FR-094: Aether and Archaeon blocks merged to main.
A MATURE label needs a "last checked against origin/*" date, and it should expire.

X3. All seven threads are in the frozen prospective cohort S (roles/Artemis/challenge/prospective/
PREREG.md@a9d5f5f23), and S workers are handed "the thread file (+ chop)".
- Any rewrite below changes the treatment, so it must be logged as a dated amendment below that
  file's END line.
- S workers must receive either the frozen version (a9d5f5f23) or the amended one, and the scorer
  must know which.
- If Artemis executes a thread now, it becomes A-RUN and leaves the paired sample.

X4. The belief-move blocks share one recurring defect: one of the two outcomes is forced by how the
unit or the arm is defined. This affects FR-010 step 2, FR-035 B1/B2, FR-057's ruler share and
FR-094's thresholds. The details are in each section.

-----------------------------------------------------------------------------------------------

## FR-010 -- Are the three Z80 builds independent evidence?

### Attacks

(a) ANSWERED (the common-cause half). The thread concedes this, and the evidence is decisive:
- One directive names its donor: "The Z80 experiment is a donor of machinery" and "analogues of the
  paper's phenomena" (roles/Bellerophon/prompts/2026-09-19_z80_atlas_campaign/
  00_OPERATOR_DIRECTIVE_verbatim.md:24,68).
- Atlas catalogued arXiv 2607.09211 the same morning (98972f55a).
- All three builds come from one model family, one operator and one host class, 27 minutes apart.
- PA_origin_of_replication.md:264-275 already rates H-D2-01 "largely ANSWERED".
- Nobody disputes that independence is implementation-level only.

(b) Superseded in part, and the thread's evidence is stale.
- Block D is no longer branch-only. The deep-block branch is an ancestor of origin/main (merge
  d7ff280e7), and the thread's line cite ":48-66 @72923db05" drifted at 4707fed67.
- About 27 minutes after Artemis's pass-1 commit, Archaeon narrowed point 2 itself: "machinery
  conserved as material is granularity- and encoding-dependent, not a law" (594bfd246).
- Archaeon opened owner threads on main for the same recurrences: TH-013 (point 2), TH-014 (point 1,
  still called a "design law", DEEP_BLOCK REPORT.md:53-54 on main) and TH-015.
- The residual question now has an owner who is actively working on it.

(d) INSTRUMENT-LIMITED: step 2 cannot discriminate.
- The decision rule reads "the recurrence vanishes when its entailing factor is removed" as
  DESIGN-BOUND.
- But a genuine necessary-cause law also vanishes when its cause is removed. Remove COPY and copies
  vanish, whether "heredity needs a copy op" is a law or a design choice.
- Both outcomes are therefore explainable either way. The rule separates design from law only if the
  removed factor is arbitrary, and that is exactly what is in dispute.
- The one completed tally (NPE non-pair worlds 0/1,554) reproduces from INDEX.jsonl.gz, but it is
  partly definitional. Nestor FINDINGS C9-D01 says pair-tape replication "is detected by a different
  code path from the ALLOC/BIRTH evidence gate". The factor-removed arm is scored by a different ruler.
- Several recurrences are UNTESTED by construction:
  - Point 1 (harness credited): the shared factor is the builder and directive, and no committed arm
    removes it.
  - Point 3 (acquisition easier than maintenance): no committed arm removes any factor.
  - Point 2: the only listed arm (BEE v3 coupling) is the claim's own "unless paid for" proviso, not
    a factor removal, and its numbers are M2-only.
- Step 2 would return "UNTESTED" for three of the four rows no matter what the world is like.

(e) SPLIT. The only row step 2 can actually decide ("heredity needs the supplied copy op") is
FR-011b. Step 1 (the factor matrix) is an archival audit, useful as a record but not a test.

### Verdict

MARK ANSWERED-IN-PART:
- The common-cause question is answered: Block D's "three independent teams" is design-bound at the
  source.
- The law-versus-design residual is DOWNGRADED to SHARPENED and routed:
  - the copy-op row goes to FR-011b;
  - points 1 and 2 go to Archaeon's TH-013 and TH-014, with a courtesy note.

### Execute now

NO.
- Inputs are committed (now on main), and it needs no GPU and consumes no holdout.
- But the step-2 stop rule cannot discriminate, points 1 and 3 have no arm, and point 2 is M2-only.
- Archaeon owns open threads on the same recurrences. These are not preregs, but they need to be
  consulted first.

### Corrected discriminator (if the residual is kept)

The law-versus-design question can only be separated by a substrate NOT written from the 09-19
directive. Run zff or cubff (arXiv 2406.19108 lineage) through our unchanged rulers (PA T2, about 1
CPU-hour), then ask whether points 1-3 recur there. Factor removal inside our own VMs cannot answer it.

-----------------------------------------------------------------------------------------------

## FR-011 -- Must the program author its unit of inheritance?

### Attacks

(e) SPLIT: two questions are being run as one.
- FR-011a is P-11 SOUNDNESS: does the certificate certify self-painting as copying?
  - This is the step-1 "information criterion" re-tally.
  - It is exactly challenge item 1A (01_OPERATOR_CHALLENGE_verbatim.md:15-48@a9d5f5f23), which
    Artemis is running now.
  - Artemis's own frozen prediction for FR-011 is "ID: P-11 certifies self-painting (A-RUN now)"
    (PREREG.md, S table).
- FR-011b is the ROUTE question: does heredity arise or persist without a supplied copy op, and is
  its absence an ISA gate or a discovery barrier?
- The two have different owners, different stop rules and different consumers.

(c) BADLY POSED criterion (for FR-011a). Step 1 proposes "donor dominant-byte share < 0.8".
- The operator explicitly forbids "a criterion that simply privileges block-copy or conventional
  genomes".
- The operator also demands a positive control "that contains little sequence entropy but genuinely
  transmits a heritable distinction".
- A dominant-byte threshold fails that control by construction. It is the privileged criterion.
- The shuffled-composition fidelity baseline (criterion b) survives, but only as one candidate among
  the adversary set the operator listed.

(a) ANSWERED-IN-PART for NPE (the route question). Step 2's "seed a hand-written byte-loop
replicator" was already done before the NPE campaign launched.
- NPE PREREGISTRATION.md:82 required it.
- CALIBRATION.json on origin/nestor/s1-forensics-2026-09-23 records:
  - `seeded_replicator_BYTEWISE_PRIMITIVE` PASS, 806 endogenous births, fidelity 1.0 (checked);
  - `seeded_replicator_BYTEWISE_PC_RELATIVE` PASS, 1,056 births.
- NPE's VM header already frames it this way (z8.py:29@aa5833488): removing LDIR "makes it longer,
  which is the accessibility question applied to heredity".
- The spontaneous side is also in hand: BYTEWISE certified donors are homopolymers, 10/500, all at
  0.91-0.96 dominant byte. Re-verified: 1,031 rows, BLOCK 47/531 vs BYTEWISE 10/500, five donors are
  0x36, none contains ED B0/B8 (P11_REASSAY.jsonl@d7641744d).
- So NPE already sits in the thread's "discovery barrier" branch. The decision tree has no open branch
  left for NPE.

(b) SUPERSEDED as a program question.
- The 2026-09-27 and 2026-09-28 operator directives give Nestor an endogenous-heredity program
  (roles/Nestor/prompts/2026-09-27_endogenous_heredity_program/DIRECTIVE_VERBATIM.md@f72d69c7f;
  .../2026-09-28_arc3_endogenous_heredity_portfolio/DIRECTIVE_VERBATIM.md@a4ca4d3bf).
- Block F lists "available copying primitives" as environmental scaffolding. Blocks G and H ask
  whether the aids can be endogenized and whether partial copy primitives are stepping stones.
- Nestor's ARC3 backlog holds T-SCAF-1, a scaffold ablation matrix that includes the copy primitive
  (BACKLOG_ARC3.md on the Nestor branch). It is an IDEA, not a prereg, but it has an owner.
- APO-28 ("author it and say so") is now effectively being answered by the operator's own program
  framing.

(d) INSTRUMENT-LIMITED: the three "copy-op-free" arms are different treatments.
- BEE "LDIR off" keeps LDI, which is in COPY_OPS (prometheus/z80atlas/vm.py:35,82,108-109@3efdacf7e).
  BEE has NO copy-op-free arm in committed data.
- Archaeon COPY-off removes an LDI-like one-byte op.
- NPE BYTEWISE removes a block op, and NPE has no LDI and no PUSH.
- A route x engine table therefore compares three different removals, and "the op is the unit in all
  three" cannot be read off it.
- The thread also under-weights BEE's 3 LD (T),A byte-loop origins (POST_CAMPAIGN_FORENSICS.md:109-113
  @3efdacf7e). These are copy-op-free routes that did arise, though with LDIR available in the world.
- The PUSH arm is circular: no VM has a stack, so "cannot seed a PUSH replicator" is an ISA gate by
  definition.

### Verdict

SPLIT.
- FR-011a (P-11 soundness): fold it into the P-11 falsification packet (challenge 1A) with the
  operator's six adversaries. Retire the dominant-byte criterion. Tell Nestor, and preserve the old
  results.
- FR-011b (route):
  - NPE: MARK ANSWERED-IN-PART (discovery barrier, from the seeded calibration plus 0 informative
    spontaneous heredity). Hand the follow-on to Nestor ARC3 G/H and T-SCAF-1.
  - BEE and Archaeon: DOWNGRADE to SHARPENED.

### Execute now

NO as written:
- Step 1 duplicates the live P-11 attack and uses a disallowed criterion.
- Step 2 is already done for NPE.

The one clean residue is narrow: seed a hand-written LD A,(r)/LD (r),A/DJNZ byte-loop replicator in
Archaeon's z80 substrate with COPY decoded as NOP.
- It is the arm with the strongest spontaneous null: 0 in 1.2e7 (c5067fac6).
- It uses a committed pure-Python VM, needs under 1 CPU-hour, consumes no holdout and overlaps no
  other seat's prereg.
- The stop rule can be written in advance.
- Caveat: only the positive outcome is informative. A hand-written replicator that fails may reflect
  the author, not the ISA.
- BEE needs an "LDI off" knob that does not exist (a code change), so BEE is not clean.

### Corrected discriminator (FR-011b)

"In Archaeon z80 (COPY=NOP), does a seeded byte-loop replicator self-replicate at fidelity above a
same-composition shuffled baseline? YES + census 0/1.2e7 -> discovery barrier (as NPE). NO after a
documented attempt -> report as UNRESOLVED, not ISA gate."

-----------------------------------------------------------------------------------------------

## FR-035 -- Three memory certificates, no common instrument

### Attacks

(c) BADLY POSED: there are not three certificates. Of the three, only one exists as runnable code.
- Cosmos P1/P2 v3 exists (prometheus/cosmos/c3/certify.py@940b486f2).
- Ensorain LM01 does not run:
  - it is not launched;
  - on 2026-09-28 the operator ordered "Do not launch WTP-LM01 v0.3.1. Amend it to v0.3.2"
    (roles/Ensorain/prompts/2026-09-28_lm01_v032_amend/01_OPERATOR_V032_AMEND_verbatim.md@c2b507e9e);
  - LM01 is queued behind Bellerophon's multi-day campaign;
  - the directive also bars retrofitting ARC3 dev instruments into it.
- Ananke SI01 does not run:
  - it never got a prereg;
  - Ananke W-G closed it for current champions: "NO nontrivial retention regime among these 16
    champions ... Close SI01 for these champions only" (roles/Ananke/research/workers/W-G/REPORT.md
    @b0985cd10).
- What Ananke actually built instead is a PTE-native ruler with known-answer plants:
  - the W-G ladder, L1 PRESENT / L2 DECODABLE / L3 EFFECTIVE / L4 AVAILABLE;
  - plants C-NEG, C-INT, C-EFF, C-AVL and C-CHAOS;
  - carrier swap and temporal reach instruments (bb61f8483).
- Ensorain built its own answer-keyed sufficiency ladder (PKG-S1, bef057f44).
- The question "do the rulers agree?" is still live. Its referents have changed completely.

(d) INSTRUMENT-LIMITED and near-circular: the known answer is known, and the B1/B2 split is set by the
adapter author.
- The known answer is real: C1b's flush_inflight gives 0.82-0.87 -> ~0.50.
- M2 is now a "strict two-hop echo, PREDICTED ... 46/46 unseen curves" by a zero-parameter model
  (roles/Ananke/research/SYNTHESIS_2026-09-28_ARC2.md:9-13@8eabc990b).
- So B1 FUNCTIONAL and B2 NONE/PASSIVE is the predicted outcome. The execution would reproduce
  already-known facts (KN), which is not consequential under the prospective scoring rule.
- Worse, P2 swaps whatever the adapter author declares as full_state. B1 vs B2 differ only in that
  declaration, so the "agreement" outcome is fixed by the author. That is the very worry (H-D3-28,
  "the author DECLARES full_state") that the thread says it tests.
- The Cosmos harness trains its OWN multinomial-logistic readout on readout_features
  (prometheus/cosmos/c3/system.py:1-15@940b486f2).
  - A certificate on M2 is therefore about the PTE substrate plus a Cosmos-trained readout, not M2's
    evolved readout.
  - C1b's known answer (held acc 0.883) is about the evolved readout.
  - The "known-answer check" compares two different systems.
- Cosmos's task is one cue, k distractors, one query (prometheus/cosmos/c3/task.py). Ananke's HOLD
  episodes are multi-trial PTE worlds, so the adapter makes episode-structure choices that can also
  set the verdict.
- The thread's own prior art already chose the cleaner design. PA_memory_and_sagacity.md T5 (:520-523)
  says "pick ONE specimen visible to all three (a Cosmos planted system is public)". A planted, known-
  answer specimen is what the thread should use, not an evolved one.

(e) SPLIT into:
- FR-035a, ruler semantics: do Cosmos P1/P2 and the Ananke W-G ladder give the same class on each
  other's PLANTS? Known answers come from construction.
- FR-035b, boundary: does a state-interchange certificate's verdict follow the declared boundary
  rather than the system? This is a property of P2, testable on Cosmos's own plants with a
  deliberately mis-declared full_state.

GOVERNANCE (a hard block, not a formality).
- The SI01 directive says: "The scientific value is independent implementation. Agreement between
  PTE-native and Cosmos-native rulers later is stronger than shared code now." It permits a
  consultation only "after Cosmos's current sealed work permits it" (roles/Ananke/prompts/
  2026-09-25_pte_si01_directive/01_STEWARD_DIRECTIVE_verbatim.md:597-608).
- Cosmos's sealed work (holdout D) has NOT run. The D seal commit is not yet on main, and the merge
  was ordered 2026-09-28.
- The operator froze Cosmos: "no methodological change before D" (roles/Cosmos/campaigns/
  REVIEW_PACKET_COSMOS_D_SEAL_2026-09-26.txt s1).
- A third seat that finds "P1 cannot see in-flight code" and reports it before D runs puts pressure on
  a frozen instrument mid-test.
- The brokered channel the directive names (Aporia) no longer operates: steward management is frozen
  (roles/Ensorain/STATUS.md:12, #732/#733).
- The thread's "neutral seat or Ananke consent" does not address the Cosmos-side sequencing.

### Verdict

DOWNGRADE to SHARPENED, and SPLIT into FR-035a and FR-035b. The "three certificates" framing is
retired: LM01 is off the table until it launches, and SI01 is replaced by the W-G ladder.

### Execute now

NO:
- The Cosmos D sequencing is unresolved (directive and freeze).
- The adapter is about 1 day of seat time.
- The planned specimen gives a known answer.

### Corrected discriminator (after D has run and Cosmos consents)

"Cross-apply on PLANTS only: Cosmos P1/P2 v3 on Ananke C-AVL (latent store; W-G L4 fires, L3 = 0),
C-EFF, C-INT and C-CHAOS; the W-G ladder on Cosmos PV, FX, MC and NZ. Report the class-agreement table.
Any disagreement on a plant is a ruler-semantics finding. Add one mis-declared-boundary run per plant
for FR-035b."

-----------------------------------------------------------------------------------------------

## FR-057 -- Cross-engine failure catalogue and reversal rate

### Attacks

(a)/(b) ANSWERED-IN-PART and SUPERSEDED-IN-PART by Odysseus I6, now on main.
- The catalogue is roles/Odysseus/frontier/poi/raw/I6_failures_reversals.md@e82bf2311 (694 lines).
- It has 80 reversal rows (R01-R80; counted), each with its original claim, what cut it down, shape
  codes and path evidence.
- It uses 13 fixed shape codes:
  - VC 12, PR 10, LP 10, AS 10, DM 8, TB 7, SC 6, HG 5, SO 3, LM 3, WR 2, SA 2, PS 2
    (primary code; my tally).
- Section 2 lists which shapes recur across two or more engines, with independent restatements. VC,
  for example, is stated independently by Nestor, Aether and the base role.
- Its frame is "all 40 calibration ledgers" plus Nestor FINDINGS, FALSE_FRIENDS, packets and errata.
  That is the thread's pilot frame (42 ledgers, Nestor FINDINGS, packet errata).
- The count (80) sits at the top of the thread's pilot estimate (40-80). The cross-engine recurrence
  map exists.
- The operator's challenge item 3 already orders the three-way comparison: Harmonia FP atlas vs
  Artemis clustering vs Odysseus shapes. The "rediscovery" half of FR-057 is that task.
- What I6 lacks: a second coder (its s6 says "a second classifier would likely merge LP/LM"), dated
  t1/t2 latencies, and a per-row prior_doc.

(d) INSTRUMENT-LIMITED and circular: the ruler/substrate split.
- The unit is "claim lowered by a later artifact", and the decision rule codes SUBSTRATE-FACT only
  when "the instrument was unchanged and a new measurement showed the world differs".
- The thread itself admits that such cases "read as 'new result', not 'error'" and are rarely written
  up as reversals.
- In I6, 80 of 80 rows carry only ruler-side shapes; the codebook has no substrate code at all.
- The belief move "ruler share >= 0.7 -> P-measurement-before-mechanism supported" is therefore
  forced by the unit and the frame. The frame is the program's defect ledgers.
- The unit cannot produce the refuting outcome (substrate share >= 0.5) at any realistic rate. That
  is the same unit mismatch the thread charges against Atlas's "218 defects".
- The ruler-share half should be KILLED as posed. Answering it needs a frame of ALL result claims
  (reversed or not) and a follow-up that can find "the world was different".

(c) The rediscovery rate is ill-defined without inter-rater reliability.
- "prior_doc in a different seat that names the same locus+mechanism" depends entirely on how
  coarsely a class is cut.
- The <0.2 / >=0.5 thresholds move with granularity, which is a free parameter.

### Verdict

DOWNGRADE to SHARPENED and rescope.
- KILL the ruler/substrate-share question as posed.
- Mark the catalogue ANSWERED-IN-PART (I6).
- The live residual is reliability: are the shapes real (inter-coder kappa)? Do they predict (a
  forward test on the next 3 launches)? This feeds challenge item 3 directly.

### Execute now

YES, in the reduced form below.
- Inputs are committed (I6 on main), with no compute, no holdout and no prereg by another seat.
  Odysseus owns I6, so send a courtesy note.
- The stop rule can be written in advance.

### Corrected discriminator

"Freeze I6 s0 (13 shape codes @e82bf2311) as the codebook. Draw 30 of R01-R80 with a seed. A fresh
coder who has not read I6 s1-s2 assigns the primary shape blind. Report Cohen's kappa against I6's
primary code. kappa >= 0.6 -> the shapes are real enough to compress on. kappa < 0.6 -> merge codes
once (LP/LM, VC split) and recode. Still < 0.6 -> shapes are not yet real; say so in the
failure-principle map."

-----------------------------------------------------------------------------------------------

## FR-094 -- Where the ecology's evidence lives; can nodes verify?

### Attacks

(c) BADLY POSED as a discriminator: it is an AUDIT.
- "Recompute 12 headlines" tests no hypothesis about any substrate.
- Its belief moves (>= 8/12 means "narrow problem", <= 5/12 means "program standard") are policy cut
  points with no alternative model behind them.
- The auditor also picks the "ONE headline number" per row, which is a forking path that sets the
  score.

(d) The outcome is largely fixed by the row list. At least 3 of the 12 rows cannot score RECOMPUTED
whatever the state of the evidence:
- BEE multi-day is still running, so there is no headline yet.
- Cosmos C3 is WITHHELD BY PROTOCOL. Its results stay on a hash-committed local branch until D
  (REVIEW_PACKET_COSMOS_D_SEAL_2026-09-26.txt). That is by design, not a reachability defect.
- The Archaeon deep block is synthesis prose with no data.

The ">= 8/12" leg therefore needs 8 of the remaining 9 rows.

"Recompute" is also undefined, and this is load-bearing:
- The thread's own example, BEE coupling 29/150 vs 6/150, sits in a SUMMARY receipt (roles/Bellerophon/
  coupling_2026-09-24/receipts/COUPLING_RESULTS.json, 53 KB, on the UNMERGED branch
  origin/bellerophon/coupling-campaign-2026-09-24).
- The per-world rows behind it are on M2 (C:/Users/James/z80atlas_coupling_2026-09-24).
- Reading a number out of a summary JSON is not recomputation. Depending on the definition, the same
  row scores RECOMPUTED or HOST-ONLY.

(b) SUPERSEDED IN PART by ops.
- TH-006 (ops/threads/TH-006.md, owner Odysseus) asks the same portability question.
- Its slice already demonstrated the pack pattern (a 10,970-byte pack; ubu001 verifies T-001 offline;
  roles/Odysseus/th006/REPORT.md@e40904023).
- fd7ca4fde made "large artifacts outside the repo with path+sha256" a platform policy.
- The census is stale: the Aether research block and the Archaeon deep block are now merged to main,
  so two "branch-only" rows moved.
- The remaining question ("should packs be a program standard?") is an ops or operator decision, not
  a research finding.

### Verdict

DOWNGRADE, and reclassify as an OPS AUDIT under TH-006. It is not a research thread and not a
discriminator, so it should not be scored as a research outcome in the prospective test. Flag this to
the scorer.

### Execute now

YES as an audit, not as a discriminator. It is cheap, read-only and needs no M2 for step 1. Two
conditions:
- The tier definitions must be frozen first:
  - ROWS-RECOMPUTED: derived from committed per-unit rows by a script;
  - SUMMARY-ONLY: the number is copied from a committed summary field;
  - HOST-ONLY;
  - WITHHELD-BY-PROTOCOL;
  - NO-RESULT-YET.
- The headline per row must be the number in the report's abstract or verdict line, not the
  auditor's choice.
- Hand the result to Odysseus / TH-006 instead of applying the 8/12 rule.

-----------------------------------------------------------------------------------------------

## FR-101 -- H2: does the CA compute, or the encoding?

Check of the C2 index-order split claim: CORRECT.
- all_streams puts x[0] as the most significant bit (herakles/ca_stream/core.py:244-249@5a0458fd6).
  Streams 0-127 have x[0]=0 and streams 128-255 have x[0]=1.
- reset_leakage_probe (reset_v2.py:222-248) trains on the first 128 streams and tests on the last 128.
- The target is y[t] = x[t-2] with mask t >= 2 (core.py:273-283). The pooled ridge over t = 2..7
  therefore sees a t=2 target that is always 0 in train and always 1 in test (mean target 0.417 vs
  0.583).
- An input-free readout scores about 0.42-0.46.
- Observed values fit that: 0.42-0.48 for ALL six rules in archaeon/campaign2/C2-SFE-09/rows.json
  @597140ca1 (re-read). This includes rules with no evolved function.
- The probe also ignores cs.partitions, while base_acc uses 64 train / 128 confirmation
  (c2_sfe09.py:86).
- "Below chance" is a split artefact, and it supports neither side.

### Attacks

(a) ANSWERED-IN-PART: arm A already exists on the proper partition.
- C2's input_shuffled_acc feeds the SAME position-keyed reset lattice with target-irrelevant shuffled
  input, keeps the targets and uses the same random partition (c2_sfe09.py:108-112).
- For particle2 this gives 0.505-0.517 in 4/4 seeds, against a base of 0.540-0.611 (rows.json
  re-read).
- The reset lattice plus irrelevant input does not reproduce the margin.
- The "encoding/reset" leg (A >= base - 0.02 in 6/8) is therefore already improbable.

Part of arm D also exists.
- C2 ran six rule tables under the identical port, reset and readout, and base_acc varies by rule:
  - particle2 0.54-0.61;
  - particle1 0.54-0.58;
  - GKL 0.53-0.55;
  - maj 0.52-0.54.
- Hand-designed GKL has a margin >= 0.03 in 5/8 C3 seeds.
- The thread's "no encoding-matched null exists" is wrong for named rules. Only the RANDOM-rule band
  is missing.

(c) Partly badly posed.
- The framing "the only evolved 'computation in a CA substrate' signal" overstates it. particle2 is a
  radius-3 rule evolved for DENSITY classification (herakles/evca/genomes.py:81), so its delayed-recall
  margin is incidental reservoir use.
- Critical sites sit within ring distance 4 of port 0 for particle2 (site 3) and for GKL (28, 30, 2,
  27), which fits geometric transport for any rule.
- ID hazard: "C4-7" and "C4-10" are candidate numbers from archaeon/campaign3/CAMPAIGN_REPORT.md:496-514.
  Campaign 4's real C4-07 and C4-10 are different experiments (d6afb4471). Cite them as "C3-report
  candidate C4-7".

(d) The stop rule is statistically unsound as written.
- Confirmation is 128 streams x 6 steps = 768 scored points, so the binomial SE is about 0.018. The
  seed-to-seed SD of particle2's base is about 0.024.
- The "dynamics" leg requires A and B at 0.50 +/- 0.02 per seed (about 1 SE), and also C >= half the
  margin, and particle2 above D's 95th percentile.
- The chance of all 16 A/B cells landing in band is roughly 0.73^16, about 0.006. The rule would
  almost always return "anything else".
- Arm C (one fixed reset lattice) is well defined (positions=np.full(256,k); reset is keyed per
  position, reset_v2.py:77-81,122-137). It is weak, though: removing reset noise makes margin
  retention the default expectation.
- C3's permuted-reset probe cannot separate the two readings, because positions equal stream integers.

Committed pieces: sufficient, with one correction.
- herakles/ca_stream and herakles/evca are pure numpy.
- The seeds, CAMPAIGN_SEED=20260920 (archaeon/campaign3/c3base.py:18), the partitions, the rule hex and
  the per-seed margins (C3 rows.json@cb9135104) are all committed.
- But `import c3_sfe09` pulls c3base -> c2base -> proteus.foundry and SerendipityFoundryClient
  (c2base.py:22-34). It is NOT pure numpy.
- Copy ClampedCA/feats (about 30 lines, c3_sfe09.py:45-71@fe3c1647c) into the analysis script instead
  of importing.
- No commits have touched herakles/ or archaeon/campaign3 on any origin ref since 2026-09-17, and no
  seat holds a prereg.

### Verdict

MARK ANSWERED-IN-PART (arm A, the named-rule part of D, and the C2 probe artefact confirmed), and
DOWNGRADE to SHARPENED until the stop rule is rewritten. The live discriminator is arm D's random band.

### Execute now

YES, in the reduced form below.
- Inputs are committed, with no GPU.
- The confirmation sets have been reused across three campaigns, so no hidden holdout is consumed.
- No other seat has a prereg, and the runtime is minutes.
- The stop rule can be written in advance on 8-seed means.
- It will be scored A-RUN (X3).

### Corrected discriminator

"particle2's mean confirmation accuracy over the 8 C3 seeds, against the distribution of >= 64 random
radius-3 tables plus the 6 C2 named rules plus identity/shift-1..3, under the identical
port-0 / Bernoulli-0.5 reset / ridge readout. particle2 above the 95th percentile of random tables ->
evolved dynamics add over generic transport (reopen as a narrow claim). Inside the band -> encoding and
geometry; close the CA line. Also report the C2 reset probe re-run on the random partition, so the
record stops citing 'below chance'."

-----------------------------------------------------------------------------------------------

## FR-118 -- W16: which re-armable latch does evolution build?

Governance check: consent is NOT a gate.
- Ares is PARKED and "does not self-authorise cycle 3" (roles/Ares/STATUS.md@3f68be2b9). Its queued
  cycle-3 arms are W4 keep-decoupling (roles/Ares/TODO.md ARES-C3-1..3), not W16.
- Ares exported the cycle-2 package for other seats to read (ares/ARES_CYCLE2_REPORT.md s9), and Nyx
  has already replayed Ares genomes.
- No active Ares or Nyx prereg covers W16. Nyx's only W16 prediction (W4 champions at the floor) held
  10/10 (roles/Nyx/reports/ARES_W4_READING_2026-09-25.md:201-214@bf5073a91), and Nyx has made no
  commit since 44e6bda1b (09-25).
- A courtesy note is enough.
- Replay would be faithful. The runs' code_commit is ab137f52b, and the diff to 1dde117f7 touches only
  mutation (keep_mut_sigma). ares/substrate.py and ares/worlds.py are unchanged since.

Numbers re-verified (sweep_c2 @1dde117f7):
- Clean scores: s201 10, s202 7.06, s203 0.00, s204 9.0, s205 9.19, s206 10, s207 9.38, s208 10,
  s209 8.75, s210 10. That is 9/10 at or above 2.0.
- Shuffled clean max 2.5.
- cut_plasticity collapse in s202, s204, s206, s207, s210.
- s208 KEEP with 0 recurrent edges.
- THRESH on outputs 7/30 present vs 4/30 shuffled.

### Attacks

(a)/(c) ANSWERED descriptively, and BADLY POSED as an either/or.
- Nyx's A/B is a remark ("would have to add either..."), not a registered prediction.
- The committed classes already refute it as exhaustive: RECUR 3, MIXED:plasticity+recurrent 4,
  PLAST 1, KEEP 1, with plasticity load-bearing in 5 of 9 solvers.
- "Which latch does evolution build?" has the descriptive answer "several".
- "Re-armable" is a misnomer. W16 has one cue per episode, and the world resets between episodes.
  The W4 failure was a loop saturating before the cue (Nyx s7b), not a failure to re-arm.

(d) INSTRUMENT-LIMITED, in four ways.
1. WRONG ORGANISM.
   - The discriminator says to use the training-selected genome. That genome exists only as
     snapshots[-1].genome (generation 119), and only for present runs; shuffled runs have 0
     snapshots.
   - All dissect numbers come from final.genome, which is the D1 held-out-selected genome:
     - carrier classes;
     - cut_plasticity;
     - "5/9 plastic";
     - probably the s205 and s208 hand-readings.
   - final.genome differs from snapshots[-1] in 6 of 10 lineages (s202, 203, 204, 205, 207, 209).
   - The thread's evidence and its discriminator describe different organisms.
2. NOT A PORT. nyx/readings/ares_w4_reading.py hardcodes the sweep_c1 W4 world and seed-3 node ids
   (drive(nodes=(7,13,15))). latch_test measures persistence, drift and saturation, not "ignition
   from settled rest" or "rest margin". These are new instruments that need their own known-answer
   check.
3. ARBITRARY CUT. A and B are one continuum: a rest state near threshold still "ignites from rest".
   The "~0.1" cut has no stated units, and it means different things for a THRESH step
   (pre1 > pre2+b) and for TANH/ring nodes. Nyx's own margin was in cue units (about 2x). "Plastic"
   is not exclusive of A either (s206 is a THRESH self-loop plus plasticity), so a collapse at R=0
   does not exclude A.
4. THE s208 TEST CANNOT FIRE.
   - Node 16 has keep 0.509 at 2 ticks per step. From about 1 at the cue it decays to roughly
     1e-16 to 1e-21 by the reward window (my arithmetic, not a replay).
   - The float32 ulp near 1e-21 is about 1e-28, so a +/- 1e-30 perturbation is rounded away. The
     test is null by construction.
   - The correct probe is to clamp |v16| < 1e-6 to 0 (or run flush-to-zero) and re-score.
   - The tie-break reading itself is unverified: with no loop, a THRESH output depends on its current
     compare inputs.

### Verdict

DOWNGRADE to SHARPENED. MARK ANSWERED-IN-PART on the descriptive question ("several carriers, not
A-or-B"). Retire the A/B verdict framing.

### Execute now

YES, after a rewrite committed as a prereg first:
- inputs committed; no GPU;
- no holdout (eval seeds 40000+ are already public);
- no other seat's prereg; minutes of CPU;
- a courtesy note to Ares and Nyx;
- the stop rule is writable once it is descriptive.

Run it on a `git archive` copy. It will be scored A-RUN.

### Corrected discriminator

"On the snapshots[-1] (training-selected) genome of each of the 9 solvers:
1. Re-dissect (carriers.py) and report agreement with the final.genome class.
2. From settled rest, apply the cue at start 0, 10 and 20. Record ignition and the cue margin in cue
   units.
3. Re-score at R=0.
4. For s208, clamp |v16| < 1e-6 to 0 and re-score.

Pre-commit a descriptive per-lineage table, not an A/B verdict. Pre-commit one instrument-defect
criterion: s208 collapses under the clamp -> log a float-residue carrier in Ares's substrate."

-----------------------------------------------------------------------------------------------

## Summary table

| thread | verdict | execute now? | why / corrected cheapest discriminator |
|---|---|---|---|
| FR-010 | ANSWERED-IN-PART (common cause); residual DOWNGRADE to SHARPENED, routed to FR-011b and Archaeon TH-013/TH-014 | NO | step-2 rule cannot separate law from design (removing a necessary cause kills a law too); points 1 and 3 have no arm; point 2 is M2-only. Real test = a non-directive substrate (zff/cubff) through our rulers |
| FR-011 | SPLIT: 011a (P-11 soundness) folds into the challenge-1A P-11 packet; 011b (route) ANSWERED-IN-PART for NPE (seeded BYTEWISE PASS; discovery barrier), SHARPENED for BEE/Archaeon | NO as written; YES only for the narrow Archaeon z80 COPY=NOP seeded byte-loop | dominant-byte criterion is the one the operator forbade; NPE step 2 already done; BEE has no copy-op-free arm (LDI kept); PUSH arm circular |
| FR-035 | DOWNGRADE to SHARPENED + SPLIT (035a ruler semantics on plants; 035b boundary dependence of P2) | NO | only 1 of 3 certificates exists (LM01 amended/unlaunched, SI01 closed by W-G); M2 answer already known (echo, 46/46); B1/B2 set by the adapter author; Cosmos trains its own readout; SI01 directive + Cosmos pre-D freeze bar it now |
| FR-057 | DOWNGRADE to SHARPENED; ruler/substrate share KILLED as posed; catalogue ANSWERED-IN-PART by Odysseus I6 (80 rows, 13 shapes) | YES (reduced) | ruler share is forced by the unit (I6: 80/80 ruler shapes); live residual = blind second-coder kappa on 30 seeded I6 rows with I6 s0 as the frozen codebook |
| FR-094 | DOWNGRADE; reclassify as ops AUDIT under TH-006 (not a research discriminator) | YES as audit only | 3 of 12 rows cannot score RECOMPUTED by construction (running / withheld by protocol / no data); "recompute" undefined (29/150 is a summary field; rows on M2); freeze the tiers first, hand to Odysseus |
| FR-101 | ANSWERED-IN-PART (C2 input-shuffle = arm A, named-rule D exists, C2 split artefact confirmed); DOWNGRADE to SHARPENED until the stop rule is fixed | YES (reduced) | per-seed +/-0.02 band is about 1 SE (conjunction nearly never met); import chain is not pure numpy (copy ClampedCA/feats). Run: particle2 8-seed mean vs >= 64 random radius-3 tables + named + transport rules; 95th percentile rule |
| FR-118 | DOWNGRADE to SHARPENED; ANSWERED-IN-PART descriptively ("several carriers") | YES after a descriptive prereg rewrite | wrong genome (final != training-selected in 6/10); Nyx code is not portable; A/B cut arbitrary; s208 1e-30 test null by float32 construction (use a clamp < 1e-6). Consent = courtesy only (Ares PARKED, no Ares/Nyx W16 prereg) |

Result: 0 of 7 keep MATURE as labelled.
- Two are ANSWERED-IN-PART with a routed residual: FR-010 and FR-011 (the latter also SPLIT).
- Two are SPLIT or rescoped: FR-035 and FR-057.
- One is reclassified as ops: FR-094.
- Two keep a clean, cheap discriminator only after rewrite: FR-101 and FR-118.
- Executable now under the s8 conditions, after the rewrites above: FR-101 (reduced), FR-118
  (descriptive), FR-057 (kappa pilot), FR-094 (as an audit), and FR-011b narrowly (Archaeon arm).
