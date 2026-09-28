+==============================================================================+
| ARTEMIS CHALLENGE PACKET -- make the frontier earn its keep                  |
| Author: Artemis (seat), host ubu002, claude-opus-5-5                         |
| Date:   2026-09-28                                                           |
| For:    the operator; Nestor, Harmonia, Aporia, Cyclops, Archaeon (parts)    |
| Status: 3 bounded experiments executed under committed preregs; 1 test       |
|         frozen; 7 MATURE threads attacked; frontier compressed               |
| Self-contained: evidence in roles/Artemis/challenge/ (paths below).          |
+==============================================================================+

Directive: roles/Artemis/prompts/2026-09-28_operator_challenge/ (verbatim,
MANIFEST). Order of work mattered and is provable from commits: the
prospective test was frozen (a9d5f5f23) before any cohort thread was
executed; every experiment's prereg was committed before its run.

------------------------------------------------------------------------------
1. P-11 FALSIFICATION -- RESULT (challenge/p11/)
------------------------------------------------------------------------------
Prereg d5241a102 (before execution); result 2af325f7b. 17 constructed
specimens (homopolymer and period-2 painters; block, bytewise and
budget-limited copiers incl. NPE's own seeded BYTEWISE replicator;
complement-cycle, guest-in-host and two-tape replication; low-entropy
positive controls carrying exactly 1 and 4 heritable bits) plus the 57
natural P-11 survivors. Gates E0/E1/E2 passed; 17/17 specimens passed
design checks.
 D1  P-11 is UNSOUND FOR HEREDITY (robust): it certified all four zero-bit
     painters at 0.90-1.00 -- including two built in NPE's own z8 VM --
     exactly as readily as real copiers. It is also OVER-STRICT: it
     rejects complement children, host-executed guests, cooperating tapes,
     and any bytewise copier in 96-byte cells.
 A0  Why, in the BYTEWISE arm: one pair slice admits painting (3 steps per
     byte) but not copying (>= 5): same cell, painter passes C2 20/20,
     genuine bytewise copier 0/20 (copies 72 of 96 bytes). P-11 selected
     painters by budget, not by evolution.
 D2  Weakest adequate certificate: CVT-2 (perturb single parental bytes;
     the offspring difference must be consistent AND re-transmitted in
     generation 2). Robust choice: CVT-R (adds a recurrence check), the
     only certificate adequate both before and after the one toy-specimen
     repair. Composition measures (dominant byte, shuffle baseline) stayed
     diagnostics and misclassify 4-6 specimens -- the criterion Artemis
     itself proposed in pass 1 was of the wrong kind.
 Natural donors (new file; nothing rescored): 24/57 survivors are
     near-homopolymers (10/10 BYTEWISE and 14/47 BLOCK; 12 x 0x36). From a
     fresh state only 6/57 re-pass P-11; 4 of the 6 carry 0 bits (three in
     BLOCK cells); 2 are genuine copiers (7ae3, e141, ~7.4 bits).
 Told Nestor: comms #793 (old results preserved; CVT-R offered).

------------------------------------------------------------------------------
2. SELECTIVE IRREVERSIBILITY -- RESOURCE-MODEL ATTACK (challenge/si/)
------------------------------------------------------------------------------
Model + prereg 1b573ac95 (before simulation); result aabb22779.
Smallest model: online prediction of known unifilar sources (exact
causal states); one register machine where only ERASE/EXPORT are
irreversible; memory, ops/step, ops/query, latency, replay and erasure
priced separately; the axis the law lacked is W -- how much of its own
past the environment keeps readable; three accounting boundaries.
 Mechanical labels: broad N (not K), narrow U.
 What that means:
  - Irreversibility is NOT required for predictive sufficiency: all 87
    full-replay cells -- reversible learner exact, zero erasure, bounded
    persistent memory. Co-unifilar sources need no erasure at any W >= 1.
  - The cost MOVES: into compute (reversible premium ~12x at 4 causal
    states, 134x at 16, 2064x at 64) and into the environment's kept past
    (charging it to the agent flips all 89 full-replay matches).
  - Erasure is forced only in a corner: bounded memory, W = 1, unbounded
    life, merging source (7/7 + proof; garbage growth = predicted
    unrecoverable-merge rate in 387/387 cells). W >= 2: open.
 Verdict for the programme: the "irreversibility law" is dead as stated;
 what survives is a memory x compute x environmental-retention frontier
 with irreversibility as its W-bounded corner. Q1 is not the hinge; W and
 the accounting boundary are. Reported to Harmonia/Aporia/Cyclops/operator
 before the s12 freeze (comms #798).

------------------------------------------------------------------------------
3. IS ARTEMIS USEFUL? -- PROSPECTIVE TEST, FROZEN (challenge/prospective/)
------------------------------------------------------------------------------
Frozen a9d5f5f23 before any execution. S = all 19 sharpened threads (no
selection); B = 19 raw threads drawn by seeded rule within the same
cluster and host class (seed = sha256 of the directive). Fresh workers,
equal budget (4 agent-hours, <= 1 CPU-hour); B workers get the raw
question only. Independent blind scorer; Artemis does not score.
Categories ID/FP/ED/PR/NU/KN/UR; CONSEQUENTIAL = ID/FP/ED/PR or a
state-changing NU. Decision rules: S <= B + 0.10 after >= 10 pairs ->
stop full sharpening; >= B + 0.30 -> keep; Brier on B no better than a
constant -> Artemis's priority labels are dropped. Artemis predicted mean
p(consequential) S 0.49 vs B 0.29 -- an enrichment BELOW what 19 pairs
can detect, so the honest expected outcome is "not shown". Amendment 1:
review-driven splits scored on the parent; A-RUNs (FR-135, FR-101) leave
the paired sample (15 pairs remain).
 First A-RUN outcomes (to be scored independently): FR-011->FR-135
 predicted ID 0.80 -> result ID (P-11 unsound). FR-101 predicted FP 0.55
 -> result FP+ID (C3's closing reason wrong; recorded null a split
 artefact).

------------------------------------------------------------------------------
4. COMPRESSED FAILURE-PRINCIPLE MAP (challenge/FAILURE_PRINCIPLES.md)
------------------------------------------------------------------------------
Bottom-up clustering committed (591209b9e, section 1 only) BEFORE the
other catalogues were read. 88 of 120 open threads are failure-shaped;
5 principles cover 60 (68%), 8 cover 76. Principles rediscovered by all
three catalogues (Harmonia June atlas, Artemis, Odysseus I6), ranked by
distinct engines:
  null without power (~21) | cheap optimum in the score (~18) |
  contrast not isolated (~15) | common-cause pseudo-replication (~14; the
  most independent: Harmonia's June rule "two anchors sharing code are ONE
  observation" = Artemis's September Z80 finding) | inaccessible
  intermediates (~13).
Three of Harmonia's four June classes recur in September engines and no
September seat cites them: rediscovery without transmission. Caveat:
Odysseus I6 read Artemis files, so many Artemis<->Odysseus agreements are
SHARED-SOURCE, not independent.

------------------------------------------------------------------------------
5. ADVERSARIAL REVIEW OF THE SEVEN MATURE THREADS (challenge/MATURE_REVIEW.md)
------------------------------------------------------------------------------
None survived as MATURE. FR-010 answered-in-part (common cause) ->
SHARPENED; FR-011 SPLIT (FR-135 P-11 soundness, now ANSWERED; FR-136
copy-route, NPE part answered by Nestor's own seeded BYTEWISE calibration
before the campaign); FR-035 SPLIT (only one of three certificates exists
as code; the known answer was the adapter-writer's choice); FR-057
SHARPENED (answered-in-part by Odysseus I6; ruler-vs-substrate share
killed -- the unit forced the answer); FR-094 an audit, moved under ops
TH-006; FR-101 executed -> ANSWERED; FR-118 A/B framing retired, the
descriptive answer is already in the data, and its 1e-30 probe could not
fire in float32.

------------------------------------------------------------------------------
6. THE ALIEN QUESTION (challenge/ALIEN_QUESTION.md; FR-139)
------------------------------------------------------------------------------
From dynamical systems, not Prometheus: are the ecology's living regimes
(replicator soups, unfrozen media, packet traffic) stable states or
SUPERTRANSIENTS whose lifetime grows exponentially with world size? Every
Prometheus verdict ("established", "extinct", "frozen") is taken at a
fixed window; none measures how a regime's lifetime scales with size, and
"supertransient" appears nowhere in the repository. Discriminator:
survival curves of time-to-end-event over >= 8x in world size, 100-200
seeds; exponential / flat / power-law readings fixed in advance. It
would turn window verdicts into scaling laws and give a window-free,
cross-engine robustness measure. Not run (host engines' seats active;
cost unknown until a 30-minute timing pilot). Runner-up: scheduler
invariance.

------------------------------------------------------------------------------
7. COLLISION-PROOF THREAD IDENTITY (challenge/identity/)
------------------------------------------------------------------------------
Canonical id thr-<12 hex>: minted before first commit with no
coordination, or derived retroactively from the question's first
appearance in git (not its path). TH-nnn / FR-nnn become aliases,
allocated at integration on main. Lifecycle as typed header edges
(duplicate-of, merged-into, split-into, superseded-by, rediscovers,
retired, answered-by); nothing renamed or deleted. Three pre-merge checks.
Evidence it is needed: git log --follow on ops TH-013 walks back to the
birth of Aether's TH-007 -- git itself conflates the two questions by
path. Applied to Artemis's 133 FR threads; proposed ids for ops TH-001..017
(17/17 distinct) sent to Archaeon (comms #789); ops/ untouched.

------------------------------------------------------------------------------
8. EXPERIMENTS EXECUTED, AND WHY
------------------------------------------------------------------------------
 Ran  P-11 attack (FR-135): an instrument whose output underlies NPE
      heredity claims; committed data; no holdout; minutes. -> UNSOUND.
 Ran  SI resource model: a law about to be frozen; pure simulation;
      stdlib/numpy. -> irreversibility law dead as stated; frontier.
 Ran  FR-101 reduced: adjudicates a closed line's recorded reason;
      committed data; 207 CPU-s. -> reason on record was wrong.
 Declined FR-038 (LM01 is queued and owns the retention prereg; a
      published eviction dose-response could leak into SI blind lanes).
 Declined FR-118, FR-057 (kept for paired execution in the prospective
      test; running them would shrink the sample).
 Declined FR-094 (an audit, not a discriminator). FR-139 (active seats'
      engines; pilot first).

------------------------------------------------------------------------------
9. KILLED, DOWNGRADED, REDUNDANT, AND ARTEMIS'S OWN ERRORS
------------------------------------------------------------------------------
 Killed/closed: "irreversibility is required" (as stated); P-11 as a
   heredity certificate; C3's "position-keyed reset" reading; the Glover
   encoding confound for particle2 (random rules at chance); the recorded
   "reset-only below chance" null (split artefact); FR-057's ruler-vs-
   substrate share as posed; FR-118's A/B framing.
 Downgraded: all 7 MATURE threads (0 remain).
 Redundant: 88 threads -> 15 principles; 60 -> 5. FR-010's independence
   question was answered by a directive the program had committed itself.
 Artemis errors (calibration ledger): pass-1 FR-011 proposed a
   composition criterion (wrong kind) and a step Nestor had already run;
   the FR-101 prereg contained a clause that could not fail to fire;
   pass 1 said no failure catalogue existed (Harmonia's did).

+==============================================================================+
| END. The success test is not this packet. It is whether the next weeks'   |
| experiments differ because of it -- which the frozen prospective test and |
| Nestor's / Harmonia's responses will show.                                 |
+==============================================================================+
