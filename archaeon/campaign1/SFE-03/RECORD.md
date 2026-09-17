# SFE-03 -- H1 RELEVANT FAILURE TRANSPORT (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-03
- question: does transporting FAILURE EPISODES (inputs a source population
  failed on, with the source world's own answers) from a structurally
  RELEVANT source raise held-out competence on the target above a fresh
  bounded search at matched budget, and above transport from a
  RANDOM-COMPATIBLE source?
- starting commit: 53e4f485e; harness archaeon/campaign1/sfe03.py.
- services: engine v2 (two source worlds with sharing FAILURES_ONLY, one
  target world EXPLICIT_IMPORT_ONLY under one topology group; failure
  artifacts published by the sources and IMPORTED by the target; the
  target runs with the bytes it fetched back; experiments + observations
  per arm x seed).
- world/spec: target W1_d4 (K=1, D=1, delay 4, 4-bit). Sources: relevant
  = W1_d1 (same K, D, ask_kind, ask_mode, op_mode, topology; delay 1);
  random-compatible = W7_K2 (same grammar/syntax; K=2, ASK2 combine).
  Relevance is a DECLARED structural rule computed from the knobs
  (relevance() in the harness) and recorded in the receipt; it is not a
  post-hoc label.
- transport: k=8 episodes of the source's last training family on which
  the source's final-generation MEDIAN organism failed (a failure INPUT
  set with source answers -- never the target's answers; the target's
  held-out family is untouched). In the target search the k transported
  episodes REPLACE k of the E=16 fresh training episodes each generation:
  matched evaluation budget across arms.
- arms: fresh / relevant / random; seeds 1,2,3; target N=200 G=60 E=16;
  sources N=200 G=60 E=16; common random numbers across arms (one branch
  label; arms differ only by their training episodes).
- primary: held-out competence (48 episodes) per arm x seed; footholds
  (>= 0.5); relevant - fresh, random - fresh, relevant - random.
- controls: fresh (no transport); random-compatible transport (same k,
  same mechanism, structurally unrelated source); the transported
  episodes' provenance (source cell, relevance rule) travels with the
  artifact.
- assay capability: W1_d4 was NOT solved by naive search in the v01
  survey (0/3 at 8-bit, N=200 G=100) nor in SSF cycle 3 (0/3 at 4-bit,
  N=512 G=200). If fresh stays at the floor and neither transport arm
  lifts it, the outcome is NULL-or-INCONCLUSIVE, decided by whether ANY
  arm reaches a foothold (then the assay was capable).
- time budget: 6 source + 9 target searches ~ 4 min on 9 procs.

## B. EXECUTION

- one attempt (RECEIPT.json, rows.json; 127.6 s). Design as planned: 3 arms x
  3 seeds, target N=200 G=60 E=16, k=8 transported failure episodes
  replacing 8 of 16 fresh episodes per generation (matched budget), common
  random numbers across arms; sources N=200 G=60.
- engine: 1 session, 1 topology group, 3 worlds (2 sources FAILURES_ONLY,
  1 target EXPLICIT_IMPORT_ONLY), 6 failure artifacts (info_kind failure),
  6 imports into the target (origin IMPORTED; the target ran with the
  fetched bytes), 9 experiments + 9 observations, 1 hypothesis; timings
  startup 2.43 s, exchange 2.02 s, records 2.37 s, teardown 0.49 s; 0
  errors. Sources 36.8 s (6 procs), targets 83.5 s (9 procs).
- relevance recomputed from knobs and recorded: relevant source W1_d1
  shares K, D, ask_kind, ask_mode, op_mode, topology with the target
  (relevant: true); random source W7_K2 differs on K and ask_kind
  (relevant: false). Failure packs: relevant sources' median organism
  failed 14-15 of 16 last-family episodes (source elite 0.19-0.31);
  random sources failed 16/16 (elite 0.06-0.56).
- decisions: none new. Failures: my hash check compared the fetched bytes
  against artifact_id instead of blob_hash (hash_ok False on 6/6 imports;
  the bytes were correct: every arm ran with k=8 parsed episodes) --
  L-009 recurrence 1. Restart/resume: not needed. Repeated work: none.

## C. SCIENCE

- primary outcome (held-out competence, 48 episodes, W1_d4 4-bit):
    arm       s1     s2     s3     mean   footholds
    fresh     0.062  0.062  0.125  0.083  0/3
    relevant  0.042  0.062  0.062  0.056  0/3
    random    0.042  0.083  0.000  0.042  0/3
  relevant - fresh = -0.028; random - fresh = -0.042; relevant - random =
  +0.014. Every value is at the 1/16 chance floor; no first-solved
  generation anywhere.
- controls: fresh (no transport); random-compatible transport with the
  same k and mechanism; common RNG; transported episodes carry SOURCE
  answers only; the target's held-out family untouched.
- assay capability: NO. W1_d4 was not reached by any arm (as the RECORD's
  section A anticipated from v01 and SSF cycle 3). The transport effect,
  if any, lies below what a search that never leaves the floor can show.
- evidence: INCONCLUSIVE for H1 (relevant vs random vs fresh). What IS
  established: the transport mechanism (failure episodes as first-class
  failure artifacts, FAILURES_ONLY sharing, import into the target, the
  target training on the imported bytes) works end to end.
- confounders: none needed. Must NOT be claimed: that failure transport
  does not help (untested at a reachable target); that relevance as
  declared is the right notion (never exercised).

## D. TEARDOWN

- 3 worlds terminated, all TERMINATED (0.49 s); no session close (L-001);
  no orphans (4 python processes = baseline); logs under
  D:/Prometheus-data/archaeon/cmp1-sfe03.log. Clean start for SFE-04: yes.

## E. BENCH IMPROVEMENT

BUGS: L-009 recurrence (my digest comparison; the mitigation in sfe01 was
not carried into sfe03 -- the shared engine helper should own the check).
FRICTION: transported episodes travel as JSON with string keys for the
expected map (ints coerced on both sides): a schema for episode artifacts
would remove two conversions.
MISSING TELEMETRY: L-017 (the assay-capability precondition -- "the
target is reachable by fresh search at this budget" -- was known from
prior campaigns and still cost a full run; a reachability table per cell
x budget, maintained from every run's first_solved_gen, would let a
harness refuse or resize BEFORE running).
AUTOMATION: the exchange path (publish -> share policy -> import -> fetch
-> run on fetched bytes) took 2.0 s for 6 artifacts; deterministic.
TO MACHINERY: reachability gate (L-017); digest check in the shared helper
(L-009).
KEEP POLICY: the relevance rule; k; replace-vs-append of transported
episodes.
MISSING FAILURE STATE: TARGET_UNREACHABLE_AT_BUDGET (L-017).
MISSING RECOVERY: none new (single attempt).
PORTABILITY / OBSERVABILITY: none new.

## F. LANDSCAPE / GRADIENT NOTES

- All nine rows sit on the chance floor, so the only gradient available
  is train_last per arm (0.04-0.21): the transported-episode arms show
  HIGHER training reward on the mixed set (relevant 0.19/0.06/0.19,
  random 0.21/0.17/0.04, fresh 0.13/0.13/0.06) with no held-out gain --
  the population fits the 8 recurring transported episodes (they are the
  same every generation) rather than the target: a memorisation shelf,
  visible only because train and held-out are both recorded. Telemetry:
  reward split by transported vs fresh training episodes per generation
  would show the shelf forming.
- The dead region is the target itself; the relevant landscape for H1 is
  (target reachability x k x relevance), and the first axis must be
  nonzero before the others mean anything.

DISPOSITION: INCONCLUSIVE (assay incapable: target unreachable by any arm
at this budget). Instrument: engine transport path 0 errors.
