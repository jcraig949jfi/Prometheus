# Pan status

Currency: 2026-10-09T20:33Z (date -u).

seat state: ACTIVE (charter 2026-10-09; window to 2026-10-12T10:40Z).
what it asserts: PRESENT, ACTIVE, PRODUCTIVE (index at origin/main; 2.25 M
  JSONL rows + 25,495 JSON docs in Iceberg; 45,256 reference links; frontier
  8,214 items = 4,702 arXiv + 742 HF daily + 2,629 blog/newsletter + 141
  release entries from 35 feeds, + 1,524 models; HumanEval+ on 4 local
  models), VALID: PARTIAL -- retrieval R@10 0.765 on 200 independent
  queries (bar 0.80 inside its interval); tuning stopped by Pan's own rule.
latest reports: reports/STATUS_20261009T1645Z.md (status report 2),
  REVIEW_PACKET_2026-10-09_unit3.txt, CODEBENCH_2026-10-09.md,
  frontier/DIGEST_2026-10-09.md (now with feeds), controls/FEEDS_*.json.
monitors: PanWorkLoop row in roles/base-role/MONITORS.md (bound 6).
running: nothing. No lease held (lse-27b333198cfe released 20:30:18Z).
blockers: PAN-26 (PEW down, reported #1969); Q-001 hard gate (pgvector).
questions for the operator: QUESTIONS.md (10 open).
