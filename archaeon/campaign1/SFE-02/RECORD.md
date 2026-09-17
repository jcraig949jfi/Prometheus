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
