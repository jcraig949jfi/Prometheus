# Campaign 2 journal (Archaeon m2-411504ab; UTC; no operator)

Directive: roles/Archaeon/prompts/2026-09-17_sfe_campaign2/00_OPERATOR_DIRECTIVE.md
Prior: archaeon/campaign1/CAMPAIGN_REPORT.md (blob dc559de117e3f71845bb92b4871b42dd43d00c73, verified at open).

## 02:00-02:30 -- campaign open; Phase A begins

- Verified the handoff blob; worktree clean at f74b5cc5b (campaign 1 closed).
- Read: campaign-1 report, ledger, decisions, every harness (sfe01..sfe10),
  the loop (evolve.py), interventions, the client surface, the survey/SSF row
  schemas, the deploy descriptor. Snapshot of the pre-refactor loop on three
  small cells saved to archaeon/tests/data_evolve_snapshot_pre_c2.json.
- Phase A plan (nine groups -> modules): reachability.py (A), states.py (B),
  evolve.py step API + CRN default + common_fill (C, G, H), campaign2/runner.py
  attempts/resume/engine wrapper (D, F), telemetry.py maturity/summaries (E, H),
  digest.py + engine_descriptor.py (F), campaign2/accounting.py + prereg.py (I).

## 02:30-03:00 -- Phase A closed

- Built and exercised: reachability.py (A), states.py (B), evolve.py step API +
  CRN default + common_fill (C, G, H), campaign2/runner.py attempts/resume/
  engine wrapper (D, F), telemetry.py (E, H), digest.py + engine_descriptor.py
  (F), prereg.py + accounting.py + c2base.py (I). 40 tests pass. Live smoke
  PHASE-A a01 (create+keep) / a02 (resume: 8 steps replayed, 0 new worlds,
  teardown TERMINATED x2). MACHINE_READINESS.md: 8 IMPLEMENTED_AND_TESTED, 1
  PARTIAL (F). Ledger L2-001..L2-011. PLAN.md fixes the ten experiments.
