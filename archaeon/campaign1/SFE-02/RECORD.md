# SFE-02 -- H3 PROSPECTIVE VALUE OF RETAINED DIVERSITY (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-02
- question: when ONE common candidate stream is replayed through bounded
  retention policies (source-performance top-K; uniform reservoir;
  behavioural archive; behavioural archive + reserved random sample) and
  the archives are frozen BEFORE future tasks are exposed, does retained
  diversity produce PROSPECTIVE utility (queries solved by direct reuse of
  a retained candidate) beyond what top-K retains?
- starting commit: the SFE-01 close commit (recorded in B); harness
  archaeon/campaign1/sfe02.py; replay machinery REUSED unmodified from
  archaeon/producer/h3_replay.py (the H3 alpha harness: stream manifest,
  four policies, caps, event ledger, digests, sealed future queries,
  direct-reuse scoring).
- services: engine v2 (artifacts for stream manifest, frozen archives and
  the sealed query manifest; experiment + observation per policy x seed).
- world/spec: stream = every organism evaluated by a short WSE search on
  W1_d1 (4-bit), in evaluation order, N=128 per generation until 1024
  candidates; descriptors = (persist policy code, log2 tape words, ops
  share of budget); source score = training reward. Future queries = five
  other cells of the same grammar (W0, W1_d4, W2_K2, W3_K2, W1_d16), each
  scored on 24 episodes of a family ("future") never used by the stream;
  solves iff held-out reward >= 0.5.
- caps: 32 items, 9600 bytes (both policies see both caps); hybrid
  reserve 8; behavioural grid 4 x 5 x 4 = 80 cells.
- seeds 1,2,3; campaign seed 20260917.
- frozen assumptions: h3_replay's policy semantics (ties: earlier wins;
  behavioural replace only if strictly better; first-writer-wins on exact
  ties); the sealed-queries-before-archives order (the manifest is
  published as an artifact BEFORE any stream is built).
- controls: (1) the whole-stream ceiling per query (best held-out reward
  among the top-64 source scorers of the uncapped stream): prospective
  value is bounded by it and a policy that reaches it has lost nothing to
  the cap; (2) uniform reservoir is the diversity-without-selection
  control; (3) distinct descriptor cells retained, per policy, is the
  diversity measure reported beside the solve fraction (a landscape, not
  a binary): best held-out reward per query per policy is recorded.
- assay capability: the queries' solve threshold 0.5 equals the last-
  value plateau on W2_K2/W3_K2 and is reachable by a single-register
  organism; if the stream contains no organism above 0.5 on ANY query
  (ceiling row all < 0.5) the assay cannot distinguish policies and the
  row is INCONCLUSIVE, not NEGATIVE.
- time budget: stream 1024 evaluations x 16 episodes ~ 20 s per seed;
  scoring <= 32 x 5 x 24 episodes per policy ~ 1 min; total < 10 min.

## B. EXECUTION

- attempts: 1 (stream 1024 = 8 generations at N=128; RECEIPT_attempt1.json;
  21.1 s) and 2 (stream 4096 = 32 generations; RECEIPT.json; 35.2 s; D-009).
- design as executed: per seed one policy-independent stream of every
  organism a WSE search on W1_d1 (4-bit) evaluated, in order, with source
  score and descriptors (persist code, log2 tape, ops share); replayed
  through top_k / uniform / behavioral / hybrid under caps 32 items and
  9600 bytes (hybrid reserve 8; grid 4x5x4); archives digested and
  published as artifacts BEFORE scoring; sealed future-query manifest
  (5 cells, 24 episodes each, threshold 0.5) published BEFORE any stream
  was built; scoring by direct reuse; whole-stream ceiling (best of the
  top-64 source scorers on each query) as the assay-capability control.
- engine objects: 1 session, 1 world (ISOLATED), 1 hypothesis, 16
  artifacts per attempt (1 sealed query manifest, 3 stream manifests, 12
  frozen archives), 12 experiments + 12 observations; timings: startup
  0.91 s, teardown 0.20 s; 0 errors both attempts.
- resource: 3 x 4096 evaluations x 16 episodes + scoring (<= 32 x 5 x 24
  episodes per policy) + 64 x 5 x 24 for the ceiling; ~35 s.
- decisions: D-009. Failures: none. Restart: attempt 2 re-created the
  world and all artifacts (L-012 recurrence 1). Repeated work: the
  sealed query manifest was re-published identically (same digest) --
  content-addressed, so the engine deduplicated by hash (artifact ids
  identical across attempts: a correct behaviour worth noting).

## C. SCIENCE

- primary outcome: solve fraction 0.000 for EVERY policy, seed and attempt
  (12 policy-seed rows per attempt). Whole-stream ceiling per query:
    attempt 2  q00(W0)  q01(W1_d4)  q02(W2_K2)  q03(W3_K2)  q04(W1_d16)
    seed 1     0.208    0.167       0.104       0.083       0.083
    seed 2     0.083    0.167       0.063       0.125       0.042
    seed 3     0.042    0.083       0.042       0.083       0.000
  No organism in any stream reaches 0.5 on any query (chance 0.0625); the
  source searches themselves peaked at 0.25-0.31 training reward.
- controls: ceiling (above) says the assay CANNOT detect prospective
  utility at this threshold; uniform reservoir = no-selection control;
  best-per-query per policy (a landscape) is at chance everywhere.
- the measurable landscape: distinct descriptor cells retained under an
  identical cap -- top_k 10-17, uniform 17-20, hybrid 25-28, behavioral
  32 (every slot a distinct cell), stable across seeds and attempts; the
  count cap bound every policy (count_bound 100-970 refusals), the byte
  cap never bound (byte_bound 0).
- evidence: INCONCLUSIVE for the H3 question (prospective utility of
  retained diversity): the assay was incapable (ceiling < threshold).
  ESTABLISHED as instrument facts: the four policies produce the diversity
  ordering the design predicts under one cap; freezing-before-querying
  works end to end with content-addressed artifacts; direct-reuse scoring
  runs.
- confounders: none needed -- nothing was detected. What must NOT be
  claimed: that diversity has no prospective value (untested), or that
  behavioral archives "would have" solved more (their retained items are
  at chance too).

## D. TEARDOWN

- terminate 1 world; state TERMINATED (0.20 s). No session close (L-001).
  Orphans: none. Temp state: attempt-1 world TERMINATED on the ledger;
  logs under D:/Prometheus-data/archaeon/cmp1-sfe02*.log. Clean start for
  SFE-03: yes.

## E. BENCH IMPROVEMENT

BUGS: none new.
FRICTION: L-016 (dry-run smoke writes RECEIPT.json into the experiment dir
and got committed under SFE-02/SFE-03 before the real run).
MISSING TELEMETRY: L-014 (stream competence precondition: a stream whose
source-score maximum is below the query threshold cannot support the
question; compute and print BEFORE freezing; typed STREAM_BELOW_THRESHOLD
outcome). L-015 (no progress output during the run: 35 s silent).
AUTOMATION: the replay + freeze + publish + score path is fully
deterministic (identical artifact ids across attempts for identical
bytes) -- machinery, not policy.
TO MACHINERY: assay-capability check (ceiling vs threshold) as a hard
gate that sets the disposition to INCONCLUSIVE automatically.
KEEP POLICY: descriptor choice, caps, threshold, query set.
MISSING FAILURE STATE: STREAM_BELOW_THRESHOLD (L-014).
MISSING RECOVERY: L-012 (recurrence 1: attempt 2 re-created everything).
PORTABILITY: none new. OBSERVABILITY: L-015.

## F. LANDSCAPE / GRADIENT NOTES

- The solve fraction reduced the experiment to a binary that was 0
  everywhere; the retained-diversity count (10-32 cells) and the
  best-per-query rewards (0.00-0.21) are the landscape that exists. A
  threshold sweep (0.125, 0.1875, 0.25, 0.5) would have shown whether
  diversity-preserving archives hold more of the sub-plateau shelf
  (organisms at 2/16-4/16) than top_k does -- computable from the rows
  already recorded (best_per_query), not done here to keep the prereg.
- The count cap bound every policy (100-970 refusals) while the byte cap
  never did: the caps were mis-proportioned for this candidate size (~140
  bytes each); a cap landscape (items x bytes) is the missing axis.
- Precursor signal to watch in a competent stream: whether the FIRST
  organism to reach a query threshold enters the behavioral archive
  earlier than top_k retains it (entry generation per policy).

DISPOSITION: INCONCLUSIVE (assay incapable: stream ceiling < threshold in
both attempts). Instrument: engine path 0 errors; replay machinery
exercised end to end.
