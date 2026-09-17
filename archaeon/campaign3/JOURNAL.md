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
