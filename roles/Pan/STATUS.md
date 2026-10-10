# Pan status

Currency: 2026-10-10T04:03Z (date -u).

seat state: ACTIVE (charter 2026-10-09; window to 2026-10-12T10:40Z).
what it asserts: PRESENT, ACTIVE, PRODUCTIVE (index at origin/main; 2.25 M
  JSONL rows + 25,495 JSON docs in Iceberg; 45,256 reference links; frontier
  8,812 items = 4,702 arXiv + 742 HF daily + 2,629 blog/newsletter + 141
  release entries from 35 feeds + 598 repositories of 29 GitHub owners,
  + 1,524 models; HumanEval+ on 4 local models), VALID: PARTIAL -- retrieval R@10 0.765 on 200 independent
  queries (bar 0.80 inside its interval); tuning stopped by Pan's own rule.
latest reports: reports/STATUS_20261010T0403Z.md (status report 4),
  REVIEW_PACKET_2026-10-09_unit3.txt, CODEBENCH_2026-10-09.md,
  frontier/DIGEST_2026-10-09.md (feeds + new repos), controls/FEEDS_*.json,
  controls/GITHUB_*.json.
monitors: PanWorkLoop row in roles/base-role/MONITORS.md (bound 6).
running: nothing; no lease held (CPU lease released 22:42:08Z). PAN-34: 3 of 5
  configurations measured; qwen3:8b and gpt-oss@4096 wait for the GPU budget.
blockers: PAN-26 (PEW down, reported #1969); Q-001 hard gate (pgvector).
questions for the operator: QUESTIONS.md (10 open).
