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

## 02:56-03:05 -- C2-SFE-01 (dry run a01; engine a02 of record; CAPABLE_NEGATIVE)

- 144 s; 3 worlds, 12 packs published with maturity, 12/12 imports hash ok,
  18 records, 0 errors, teardown 3/3 TERMINATED. Fresh 2/6 footholds (35, 49);
  relevant transport -0.160 held-out vs fresh (1/6 paired wins, 0/6
  footholds); random transport -0.026 (1/6). Machine disposition
  CAPABLE_NEGATIVE accepted. 30 reachability rows appended (W2_K2 8-bit
  G60 2/6; W7_K2 4-bit 0/6). Ledger L2-012 (auto), L2-013, L2-014. Next: C2-SFE-02.

## 03:04-03:55 -- C2-SFE-02 (dry a01/a02; engine a03 8-bit gate FAILED 1/6; a04 v01 foundry gate FAILED 1/6; a05 4-bit gate PASSED 3/8 but resume replayed a04 records; a06 of record; CAPABLE_NEGATIVE)

- Three shared-machine fixes from one experiment: reachability keyed on the
  generation-0 foundry (L2-017); run identity (campaign_seed + rng_label) with
  dedupe in pooled() (L2-022); design-keyed resume steps (L2-021). Stuck cell
  W1_d4 4-bit: B - A = +0.01, 0/8 vs 0/8 -> CAPABLE_NEGATIVE; C 1/8 exploratory.
  Operator masses within 0.01 across arms. 48 records, 0 errors, 1 world
  TERMINATED per attempt. Next: C2-SFE-03.

## 03:55-04:20 -- C2-SFE-03 (dry a01; engine a02 of record; CAPABLE_NEGATIVE: SFE-01 component effect retired)

- 491 s; 3 worlds, 25 artifacts (maturity on every population set), 25/25
  imports hash ok, 108 records, 0 errors, 132 reachability rows. components -
  random_segments = +0.009 (5/12 paired wins), 6/12 vs 5/12, baseline 6/12;
  kill battery moot (shuffled/opcode_matched/self_segments within 0.06).
  Probe mature_source 11/12 at 0.49 = W0 sub-solution half credit on a K=2
  cell (exploratory). Landscape: W2_K2 half-credit shelf at 0.5 (L2-025);
  W0 4-bit COMMON by ~G35 (10/12); W1_d1 4-bit G100 3/12. Next: C2-SFE-04.
