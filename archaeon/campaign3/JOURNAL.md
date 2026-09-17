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
