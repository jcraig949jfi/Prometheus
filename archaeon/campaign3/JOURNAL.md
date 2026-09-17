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
