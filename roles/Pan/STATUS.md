# Pan status

Currency: 2026-10-09T14:37:39Z.

seat state: ACTIVE (charter 2026-10-09; window to 2026-10-12T10:40Z).
what it asserts: PRESENT, ACTIVE, PRODUCTIVE (index at origin/main; 2.25 M
  JSONL rows + 25,495 JSON docs in Iceberg; 50,079 citation links; frontier
  5,444 papers + 1,524 models; 9 local models smoke-tested), VALID: PARTIAL --
  retrieval R@10 0.765 on 200 independent queries (bar 0.80 sits inside its
  interval); tuning stopped by Pan's own rule.
latest reports: reports/STATUS_20261009T1645Z.md (status report 2),
  REVIEW_PACKET_2026-10-09_unit2.txt, RETRIEVAL_VERDICTS, MODEL_SMOKE_TESTS,
  frontier/DIGEST_2026-10-09.md.
monitors: PanWorkLoop row in roles/base-role/MONITORS.md (bound 6).
running: nothing. No lease held.
blockers: PAN-26 (PEW down, reported #1969); Q-001 hard gate (pgvector).
questions for the operator: QUESTIONS.md (9 open).
