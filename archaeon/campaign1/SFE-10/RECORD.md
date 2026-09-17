# SFE-10 -- PRODUCER-CONSUMER SPECIALIZATION (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-10
- question: under a MATCHED total resource envelope with EXPLICIT
  communication and storage costs, does a system of producers (searching
  source cells and publishing artifacts) plus a consumer (importing them
  and searching the target) improve later solving over a monolithic
  search of the same total budget?
- starting commit: the SFE-09 close commit; harness sfe10.py.
- services: engine v2 (two producer worlds FULLY_SHARED and one consumer
  world EXPLICIT_IMPORT_ONLY under one topology group; producer elites
  published as info_kind success artifacts; imported and fetched by the
  consumer, which runs with the fetched bytes; experiment + observation
  per arm x seed).
- envelope: N=200, G_total=60 generations, E=16 on target W2_K2 (4-bit).
  mono spends all 60 on the target. pc_p: producers on W0 and W1_d1 spend
  round(60 x p / 2) generations each (p in {0.2, 0.4}: 6+6 and 12+12);
  the consumer pays communication ceil(bytes/4096) generations and
  storage 0.5 generation per artifact held, and spends the remainder on
  the target seeded from the fetched elites (top-4 per producer).
  pc_p_noex: the same producer spend, consumer with random generation 0
  and the remainder (no exchange costs): the artifact effect vs budget
  loss.
- seeds 1,2,3; common random numbers for the consumer arms.
- controls: mono; noex; costs declared before running and recorded per
  arm in the receipt (bytes, artifacts, generations charged).
- assay capability: W2_K2 is reachable from random generation 0 in some
  seeds (SFE-01 00: 1/3 at G=60) and from register seeds (SFE-07/08); if
  mono and every pc arm stay at the floor the row is INCONCLUSIVE.
- time: 12 producer runs (short) + 15 consumer runs; ~3 min on 12 procs.

## B. EXECUTION

- two engine attempts after a dry run (dry run 0.4 s at N=20 G=10).
  Attempt 1 (RECEIPT_attempt1.json, rows_attempt1.json; 66.3 s; 0
  engine errors) ran the design as declared but the harness filled the
  producer-consumer arms' generation 0 (192 random organisms beside the
  8 imported elites) from a foundry seed of its own (1010+seed) while
  mono and the no-exchange arms drew the loop's common generation 0
  (wse.gen0 keyed on the cell seed): common random numbers (D-007) were
  broken for exactly the arms under comparison (L-030). Attempt 2
  (RECEIPT.json, rows.json; 51.5 s: startup 2.31, producers 3.9 on 12
  procs, consumers 36.3 on 12 procs, records 3.98, teardown 0.56; 0
  errors) fills the pc arms from the SAME generation 0, truncated, so
  the only difference between pc_p and pc_p_noex is the 8 imported
  organisms (plus the charged generations).
- engine, each attempt: 1 session, 1 topology group, 3 worlds (two
  producers FULLY_SHARED, one consumer EXPLICIT_IMPORT_ONLY), 1
  hypothesis, 12 success artifacts (cmp1.pc.producer_elites.v0;
  32,243 bytes in total), 12 imports + 12 content fetches (hash_ok 12/12
  against the producer's blob hash, prefix stripped), 15 experiments +
  15 observations. The consumer ran on the fetched bytes, not on the
  in-process manifests.
- costs charged (identical in both attempts; the producers' outputs are
  deterministic): p=0.2: producers 6+6 gens, comm 1-2 gens (3,893-5,301
  bytes), storage 1 gen, consumer 45-46 gens; p=0.4: producers 12+12,
  comm 2 (4,632-7,134 bytes), storage 1, consumer 33; noex consumers
  48 and 36.
- decisions: D-014 (rerun as attempt 2 after fixing the fill rather
  than report attempt 1 with the confound noted). Failures: none on the
  engine path. Restart: attempt 2 re-created worlds and artifacts (L-012
  recurrence 3): 52 s.

## C. SCIENCE

- primary outcomes (attempt 2; held-out competence on W2_K2, 48
  episodes; foothold = train best >= 0.5):
    arm           s1     s2     s3     footholds  first-solved consumer gen
    mono          0.542  0.562  0.521  3/3        54, 50, 48
    pc_0.2        0.031  0.073  0.396  0/3        -
    pc_0.2_noex   0.312  0.281  0.260  0/3        -
    pc_0.4        0.312  0.531  0.062  1/3        -, 3, -
    pc_0.4_noex   0.083  0.344  0.083  0/3        -
  exchange effect (pc_p minus pc_p_noex, same generation 0 apart from
  the 8 imports): p=0.2: -0.281, -0.208, +0.136; p=0.4: +0.229,
  +0.187, -0.021.
  producer elites' rewards on their OWN cells: p=0.2 (6 gens) 0.0-0.125
  in 6/6; p=0.4 (12 gens) 0.0625-0.25 in 5/6 and 1.0 in one (seed 2,
  W0).
- the question as posed (does the producer-consumer system beat a
  monolithic search of the same total budget): NEGATIVE, assay capable.
  mono reached a foothold in 3/3 seeds at generations 48-54 and ends at
  0.52-0.56; the best pc arm reached 1/3 and pc_0.2 0/3. The producer
  spend alone costs the consumer 12-27 of 60 generations, and mono's
  footholds arrive in its last 12 generations, so at this envelope the
  charged generations are exactly the ones mono needed.
- the one exchange that paid: seed 2, p=0.4, where the W0 producer
  SOLVED its own cell (reward 1.0 in 12 generations). Its elite scored
  0.312 on the target at consumer generation 0 and the consumer reached
  a foothold at consumer generation 3, i.e. charged generation 24+2+1+3
  = 30 against mono's 50 on the same seed. In both attempts (different
  random fills) that row solved at consumer generation 5 and 3.
  Immature artifacts (producer elite <= 0.25) gave no benefit in 4/5
  rows and a deficit against the same population without them in 3/5
  (pc_0.2 s1, s2; pc_0.4 s3 is within noise).
- attempt 1 vs attempt 2 (the fill alone changed): pc_0.4 s3 went from
  a foothold (0.510, consumer gen 13) to 0.062; pc_0.2 s3 from 0.052 to
  0.396. Two of fifteen rows crossed the foothold line on the random
  fill alone: at n=3 the seed noise on this cell is as large as the
  effects under test, so the common fill is load-bearing, not
  cosmetic.
- controls: mono (matched total budget); noex (producer spend without
  the artifacts, exchange costs not charged); costs declared before the
  run and recorded per arm; hashes verified on every import.
- assay capability: capable (mono 3/3 above the floor).
- confounders: n=3; producers ran with the same population size as the
  consumer (a producer at N=200 for 6 generations is a random sample,
  not a search); the exchange costs (4096 bytes/gen, 0.5 gen/artifact)
  are declared, not measured against anything; the target is one cell.
- must NOT be claimed: that division of labour does not pay (one
  mature artifact paid, early); that it pays (0/1 arms beat mono).
  What is supported: at this envelope the producer share must be
  large enough for a producer to solve its own cell before its
  artifacts are worth their charge; a share that only buys random
  samples is a pure loss.

## D. TEARDOWN

- 3 worlds TERMINATED in 0.56 s (both attempts; attempt 1's three
  worlds also TERMINATED). Baseline 4 python.exe after the run: no
  orphans. Clean for the campaign report: yes.

## E. BENCH IMPROVEMENT

BUGS: L-030 (harness-side generation-0 fill breaks common random
numbers for the compared arms; the loop's init_pop path takes whatever
it is given and does not check the fill's provenance). FRICTION: L-032
(the stdout summary JSON is a subset of the receipt: a reader keyed on
the receipt schema fails on stdout). MISSING TELEMETRY: L-031 (import
lineage share: the fraction of the consumer's final population and of
its elite's ancestry that descends from imported organisms, so "the
imports poisoned / carried the population" is measured, not inferred
from trace shape). AUTOMATION: the producer -> artifact -> import ->
fetch -> consumer chain ran hands-off in both attempts; costs are
computed from the fetched bytes. TO MACHINERY: the common-fill rule
(any init_pop must be built from the cell's wse.gen0 population plus
the substituted organisms; a helper in evolve.py, with the harness
forbidden from calling the foundry directly for fills). KEEP POLICY:
the cost model (bytes per generation, storage per artifact) and the
producer share ladder are scientific choices. MISSING FAILURE STATES:
IMMATURE_ARTIFACT (a producer publishing an elite below a solving
threshold on its own cell should be labelled so the consumer's row
carries it; L-010 again, on the producer side). MISSING RECOVERY: L-012
recurrence 3 (attempt 2 re-created everything). PORTABILITY: none.
OBSERVABILITY: none new.

## F. LANDSCAPE / GRADIENT NOTES

- mono's traces on W2_K2 show a long flat (best 0.03-0.19 for 45-50
  generations) then a step to 0.5+ within 4-6 generations: the cell is a
  plateau with a narrow exit, reached by all three seeds between
  generations 48 and 54 at N=200. The exit's timing is the whole
  story of this experiment: any spend before it that does not shorten
  the plateau is lost.
- the W0 -> W2_K2 gradient is real and cheap when the W0 solver exists
  (0.312 at generation 0, foothold in 3 generations); the W1_d1
  producers never solved and contributed nothing measurable. Which
  source cell's solvers sit on the target's exit is the reachability
  table's off-diagonal (L-017): the campaign now has three cells of it
  (W0 -> W2_K2 yes; W1_d1 -> W2_K2 not shown; W1_d4 unreached).

DISPOSITION: COMPLETE (attempt 2). Science: NEGATIVE for the system at
this envelope (mono 3/3 vs best pc 1/3); one mature artifact bought a
foothold at charged generation 30 vs 50; immature artifacts are a
loss. Instrument: attempt 1 broke common random numbers (harness bug,
L-030, fixed); 0 engine errors in both attempts.
