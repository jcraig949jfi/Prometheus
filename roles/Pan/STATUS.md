# Pan status

Currency: 2026-10-10T13:37Z (date -u).

seat state: ACTIVE (charter 2026-10-09; window to 2026-10-12T10:40Z).
what it asserts: PRESENT, ACTIVE, PRODUCTIVE (index at origin/main; 2.25 M
  JSONL rows + 25,495 JSON docs in Iceberg; 45,256 reference links; frontier
  8,812 items = 4,702 arXiv + 742 HF daily + 2,629 blog/newsletter + 141
  release entries from 35 feeds + 598 repositories of 29 GitHub owners,
  + 1,524 models; HumanEval+ on 4 local models), VALID: PARTIAL -- retrieval R@10 0.765 on 200 independent
  queries (bar 0.80 inside its interval); tuning stopped by Pan's own rule.
latest reports: reports/STATUS_20261010T1000Z.md (status report 5),
  REVIEW_PACKET_2026-10-09_unit3.txt, CODEBENCH_2026-10-09.md,
  frontier/DIGEST_2026-10-09.md (feeds + new repos), controls/FEEDS_*.json,
  controls/GITHUB_*.json.
monitors: PanWorkLoop row in roles/base-role/MONITORS.md (bound 6).
running: nothing; no lease held (M1 lease skullport:cpu8 13:09-13:29Z for PAN-28, released). PAN-34: 3 of 5
  configurations measured; qwen3:8b and gpt-oss@4096 wait for the GPU budget.
blockers: PAN-26 (PEW down, reported #1969).
vectors: pgvector 0.8.7 on M1 (Atlas install #2056; Pan migrations 012+013): HNSW on chunk, document and
  paper vectors; off-M2 hosts get vector neighbours from Postgres (pan/pgvec.py); controls
  PGVECTOR_20261010T132524Z 5/5; query-style recall@10 0.94 at ef 200, 0.98 at 400;
  schema pan 2,956 -> 3,590 MB after 013 (3,497 after 012).
atlas copy: Iceberg pan_atlas.* (35 tables, 143,139 rows, harvest_id 1..364), refreshed when Atlas harvests
  (python -m pan atlas snapshot; manifest = pan.run kind atlas-snapshot); controls ATLAS_SNAP_* 6/6.
dashboard: Data Map v4 has tabs; Machines (14) and Pantheon (74 seats) tabs added (PAN-38,
  controls/FLEET_20261010T114620Z.json 7/7); rebuild: python -m pan fleet probe + mk_datamap.py --only fleet.
questions for the operator: QUESTIONS.md (11 open; Q-001 executed via Atlas; Q-012: host keys for ubu004-006).
