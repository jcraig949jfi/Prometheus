# Campaign 3 journal (Archaeon m2-411504ab; UTC; no operator)

Directive: roles/Archaeon/prompts/2026-09-17_sfe_campaign3/00_OPERATOR_DIRECTIVE.md
Prior: archaeon/campaign2/CAMPAIGN_REPORT.md (main 4d80d4b1d).

## 06:30-06:45 -- campaign open; Phase A begins

- Worktree in sync with origin/main at 4d80d4b1d. Directive saved verbatim.
- Phase A items (directive section 3): A full-solve reachability (levels
  FLOOR/SHELF/SUMMIT, first_shelf/first_summit, shelf histogram, censoring),
  B right-censoring of stopped-on-solve runs, C corridor table, D dense
  transition probes, E client read path (three wrappers into sfclient; GET
  artifacts route requested from Daedalus), F injection cap (dose + offspring
  cap; origin shares per generation already in every trace row).
- Preserved campaign-2 shelf material located: C2-SFE-05 top_k archives on
  world wld_1dbee6094762d1b3bb7e6e98 (seeds 3 and 6 held W2_K2 solvers).

## 06:45-07:10 -- Phase A closed

- Built + tested: three reach levels with held-out-confirmed summits (D3-002,
  D3-006), right-censored stopped runs (D3-003), corridor table populated
  from campaign 2 (73 rows), probe_plan/transition_events, sfclient read
  wrappers (Daedalus asked for the artifact route, comms #325), inject +
  offspring cap + per-ask credit, per-campaign parametrization of the shared
  machine, campaign-3 prereg fields in the sealed body. 47 tests pass.
  MACHINE_READINESS.md: 5 IMPLEMENTED_AND_TESTED, 1 PARTIAL (E).

## 07:15-07:55 -- C3-SFE-01 (dry a01-a03; engine a04 of record; CAPABLE_NEGATIVE: no summit through G300)

- 1235 s; 1 world, 24 records, 24 reachability rows, 12 corridor rows, 0
  errors. Fresh 11/12 on the shelf (13-226), 0/12 summits, 0 candidates; shelf
  arm 12/12 on the shelf from generation 0, 0/12 summits; residence censored
  at 300 everywhere. Held-out per ask ~0.5/0.5: the shelf looks like a
  last-value strategy. C3-SFE-08 replaced (D3-013). Ledger L3-001..L3-004.
  Next: C3-SFE-02 (with a last-value probe added).

## 07:55-08:10 -- C3-SFE-02 (dry a01/a02; engine a03 of record; CAPABLE_NEGATIVE: the shelf is a one-value memory)

- 22 s; 18 records, 0 errors. Shelf reproduced 10/12; strategy first-value
  6/12, last-value 4/12, mixed 2; useful children 1/4800; second-stream gains
  all trade the first (58/58); basin 0/480. E5 6/12, E2 7/12, E3 5/12, E1 0.
  Ledger L3-005..L3-007. Next: C3-SFE-03 (running).

## 08:10-09:05 -- C3-SFE-03 (dry a01; engine a02 POSITIVE_CONTROL_FAILED; machine change; dry a03/a04; engine a05 of record; WEAK_POSITIVE: the corridor is W0 -> d1, then free)

- a02 (fixed 25-generation rungs): rung 0 climbed within its rung in 5/12; the
  ladder moved on before there was anything to carry (L3-008, L3-011).
  Machine change: ladder.rung0_max holds rung 0 until best >= 0.5, then the
  fixed schedule; timings relative to the release. Re-preregistered.
- a05: 233 s; 12 records, 12 reach rows, 12 corridor rows, 0 errors. Hold
  12-97 generations (all by competence); delay-general 11/12 (held-out 1.0 on
  d0/1/2/4), minted at rung 1 in 7/11, abrupt (rise 0 in 8/11), adapt d2/d4
  = 0 in 11/11; in 5/12 the first delay-1 battery promoted an already-general
  organism from the W0 population. Comparator caveat: direct W1_d4 measured
  at G60 only (L3-013 -> C3-SFE-04 runs it at matched budget). L3-011..013.
- C3-SFE-09 dry run fixed (ClampedCA clamp-set bug). C3-SFE-10 harness
  written (dose x quality x cap on W1_d4; permuted-block matched control).

## 09:05-10:35 -- C3-SFE-10 (dry a01/a02; a03 engine 403; a04 of record; CAPABLE_NEGATIVE: takeover is mechanics, not capability)

- Reconnaissance first (6 runs x 20 generations): mature dose 1 of 200 takes
  over by generation 4-5, so the DOSE ladder could not be the ecological
  control parameter. Design changed before sealing: cap ladder added
  (none / 0.25 / 0.05), doses 0/1/4/32, qualities mature / permuted control.
- a03 died on an engine 403: an ISOLATED world cannot import from itself.
  Publish-then-fetch gives the same read-back guarantee (L3-015, B4).
- a04: 1512 s; 228 runs, 228 records, 228 reach rows, 0 errors. Primary
  (mature vs permuted control on takeover, dose 4, no cap) 12/12 vs 12/12,
  effect 0.0: the preregistered falsification fired. Cap 0.05 delays
  takeover to generations 15-57 and is the only setting leaving resident
  lineages alive; nothing prevents takeover. Origin takeover is NOT clonal
  collapse (distinct genomes 0.78-0.99). L3-015..017.
- Machine: evaluate(reward_mode) all-or-nothing episode credit added for the
  C3-SFE-08 replacement; ladder hold wired into C3-SFE-05; harnesses for
  slots 4, 7, 8 written and dry-run. D3-014..D3-020 recorded (D3-020: the
  slots run in DEPENDENCY order, each sealed before its own run).
- Next: C3-SFE-04 (corridor map) running.

## 10:35-11:05 -- C3-SFE-04 (dry a01/a02; a03 of record; WEAK_POSITIVE: the ladder builds delay INVARIANCE)

- 919 s; 66 runs, 66 records, 66 reach rows, 33 corridor rows, 0 errors.
  Cheap-first worked: 0.3 s of direct probes removed 2 of 5 targets from the
  search budget AND produced the main result.
- MAIN: all 11 delay-general elites read W1_d8 and W1_d16 at held-out 1.0,
  cells they never saw; matched direct search gets 0/6 and 1/6. The 4 mature
  W0 solvers score 0.0 on both, so the invariance is the LADDER's product
  (L3-019; closes L3-013's comparator gap).
- Edge types: free (d8/d16), half-free to a dead shelf (W2_K2 0.54, W3_K2
  0.58; 0 summits in 54 K=2 runs), time advantage (W7_K2: foothold median
  generation 20 vs 82, and the permuted control is WORSE than no import at
  2/6 -- L3-020), no corridor (W0 solver -> the delay family).
- Table corrections (L3-021): W7_K2 REACHABLE at G100 (4/6) after
  OBSERVED_UNREACHABLE at G60; W1_d8 OBSERVED_UNREACHABLE (0/6) and W1_d16
  RARE (1/6), both previously UNESTABLISHED.
- Battery: 2 of 3 passed; the failing one (advantage without inherited
  competence: 5/6 vs 4/6 at n=6) is why the record is WEAK.
- Next: C3-SFE-05 (retention break-even) running.

## 11:05-11:25 -- C3-SFE-05 (dry a01/a02; a03 of record; CAPABLE_NEGATIVE on the declared primary, break-even located)

- 684 s; 60 runs, 60 records, 60 reach rows, 0 errors. The rung-0 hold
  released by competence in 60/60 (median 35 generations).
- Mean final rung-0 competence 0.764 / 0.892 / 1.000 / 1.000 at p =
  0 / 0.05 / 0.10 / 0.20; runs below 0.75: 3 / 2 / 0 / 0. The preregistered
  falsification for p0.05 fired: the break-even is in (0.05, 0.10].
- p0.1_then_0: retention 1.0 in 12/12 and the same generality (11/12, same
  seeds and generations) for a MEDIAN of 22 revisit episodes instead of 150
  -- retention is a transient price, not a standing tax (L3-023).
- No adaptation cost at any share up to 0.20 (adapt to the new rung = 0
  generations in 57/58 general runs) -- untested rather than absent, since
  this ladder's adaptation is free after delay 1 (L3-024).
- Instrument check (L3-025): the p0.1 arm reproduces C3-SFE-03's ladder arm
  row for row under CRN, across two sealed preregistrations.
- Next: C3-SFE-06 (basin geometry out-of-family) running; C3-SFE-07 consumes
  its geometry rows.

## 11:25-12:10 -- C3-SFE-06 (a02 POSITIVE_CONTROL_FAILED; a05 of record; INCONCLUSIVE: the pooled primary was confounded)

- a02 (fixed 0.875 threshold): only 9 of 390,625 genotypes reach it on skelA
  (2.3e-05), so a 2,000-3,200 evaluation climb cannot find it; 44 of 48 rows
  censored, identity hit in 1 of 4 cells. Same shape as the fixed first rung
  (L3-031). Fix D3-021: threshold chosen PER TABLE from its own score
  distribution (highest level >= 0.1% of genotypes reach), climbs widened.
- a05: 422 s, 48 records, 0 errors. Pooled rho(basin_share, log evals)
  = -0.568, which would have replicated C2-SFE-08's -0.59 exactly -- and is
  CONFOUNDED: skelB has basin 0.41-0.43 and is trivially easy, skelA has
  basin 0.026-0.034 and is hard, so the pooled statistic has two informative
  points (L3-029). Within table: skelA first-improvement -0.527 (replicates),
  skelA population +0.187, skelB ~0 / undefined.
- Second instrument defect (L3-030): the adaptive rule can pick the CHANCE
  level on a bimodal table. skelB's target came out at 1/16, hit at
  evaluation 1 by every population climb. Fix: require threshold > chance
  and type the table READOUT_CANNOT_EXPRESS.
- Disposition INCONCLUSIVE: the out-of-family test was not delivered.
- D3-022: C3-SFE-07 selects its encodings from skelA only. Selected:
  high perm_7 (basin 0.0338), low identity (0.0256), gap 0.0082, matched on
  accessible variation (1.4450 vs 1.4399); scale pair perm_3 / perm_6 (gap 0).
- Next: C3-SFE-07 running.

## 12:10-12:20 -- C3-SFE-07 (dry a01; a02 of record; CAPABLE_NEGATIVE: the basin line is killed)

- 121 s; 60 runs, 60 records, 60 reach rows, 0 errors. Intervention verified
  (567-573 opcode rewrites per treated run, 0 in grammar; realized operator
  masses within 0.008 across arms).
- Confirmed W0 competence: grammar 8/12, high basin 8/12, low basin 9/12,
  random A 7/12, random B 8/12. Effect -0.083, wrong direction; the two
  RANDOM orderings matched on basin share differ by the same 0.083, so the
  preregistered kill condition fires on its own terms (L3-033).
- Median generation to confirmation: high 24, low 25, randoms 13-15 -- the
  two selected arms are the two slowest.
- Instrument defect recorded (L3-034): a noise-control battery attack coded
  with an absolute 0.1 floor passes exactly when it should fail; the record
  is read from its values, not its flag.
- Read with C3-SFE-06: basin share is measurable, correlates inside one
  exhaustive table under one climber, and predicts nothing when used to
  steer a real evolutionary run. The line dies as the directive allows.
- Next: C3-SFE-08 (replacement: partial-credit removal on W2_K2) running.
