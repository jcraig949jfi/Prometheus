# Pan status

Currency: 2026-10-12T01:58Z (date -u).

seat state: ACTIVE (charter 2026-10-09 + Sagacity Foundation directive 2026-10-11; deliverables due
  2026-10-12T10:40Z; loop extended to 2026-10-16T10:40Z).
what it asserts: PRESENT, ACTIVE, PRODUCTIVE (index at origin/main; 2.25 M
  JSONL rows + 25,495 JSON docs in Iceberg; 45,256 reference links; frontier
  8,812 items = 4,702 arXiv + 742 HF daily + 2,629 blog/newsletter + 141
  release entries from 35 feeds + 598 repositories of 29 GitHub owners,
  + 1,524 models; HumanEval+ on 4 local models), VALID: PARTIAL -- retrieval R@10 0.765 on 200 independent
  queries (bar 0.80 inside its interval); tuning stopped by Pan's own rule.
latest reports: reports/STATUS_20261012T0158Z.md (status report 11, late: loop gap 20:26-01:50Z), prompts/2026-10-12_limits_of_mind_note/ (operator note captured), reports/STATUS_20261011T1608Z.md, REVIEW_PACKET_2026-10-11_PAN44.txt, frontier/DIGEST_2026-10-11.md, REVIEW_PACKET_2026-10-11_PAN43.txt, docs/sagacity/SAGACITY_FOUNDATION_MAP.md, REVIEW_PACKET_2026-10-11_PAN37_REVIEWERS.txt, REPOBENCH_2026-10-11.md,
  REVIEW_PACKET_2026-10-11_PAN34.txt, REVIEW_PACKET_2026-10-10_PAN37_39.txt, REVIEW_PACKET_2026-10-10_PAN27_28.txt,
  REVIEW_PACKET_2026-10-10_PAN38.txt,
  REVIEW_PACKET_2026-10-09_unit3.txt, CODEBENCH_2026-10-09.md,
  frontier/DIGEST_2026-10-09.md (feeds + new repos), controls/FEEDS_*.json,
  controls/GITHUB_*.json.
monitors: PanWorkLoop row in roles/base-role/MONITORS.md (bound 6).
running: nothing; no lease held (M2 lease spectrex5:cpu12 16:39-16:42Z for PAN-39, released). PAN-34: 3 of 5
  configurations measured; qwen3:8b and gpt-oss@4096 wait for the GPU budget.
blockers: PAN-26 (PEW down, reported #1969).
review calibration: set v1 UNFIT (prereg A3): a regex for `return None` / `not (` scores recall 0.45 at
  false-alarm 0.05 without reviewing; floors in controls/REVIEWCAL_FLOORS_20261010T143738Z.json. Set v2 built
  16:42Z under prereg v2 (03b9c37c1): tell gate USABLE (regex floor 0.025); reviewer bar = 0.70 x its
  false-alarm rate (site-density floor); manifest reports/review/CALIBRATION_MANIFEST_V2_*.json.
vectors: pgvector 0.8.7 on M1 (Atlas install #2056; Pan migrations 012+013): HNSW on chunk, document and
  paper vectors; off-M2 hosts get vector neighbours from Postgres (pan/pgvec.py); controls
  PGVECTOR_20261010T132524Z 5/5; query-style recall@10 0.94 at ef 200, 0.98 at 400;
  schema pan 2,956 -> 3,590 MB after 013 (3,497 after 012).
atlas copy: Iceberg pan_atlas.* (35 tables, 143,139 rows, harvest_id 1..364), refreshed when Atlas harvests
  (python -m pan atlas snapshot; manifest = pan.run kind atlas-snapshot); controls ATLAS_SNAP_* 6/6.
dashboard: Data Map v4 has tabs; Machines (14) and Pantheon (74 seats) tabs added (PAN-38,
  controls/FLEET_20261010T114620Z.json 7/7); rebuild: python -m pan fleet probe + mk_datamap.py --only fleet.
negative space (PAN-43): distinctness instrument PROMOTED 2026-10-11T10:18:39Z
  (controls/NEGSPACE_CALIBRATION_20261011T101839Z.json; behavioral known macro 1.000 vs best baseline 0.500,
  symbolic 0.867 vs 0.442; EQ->EQ exactly at its analytic 0.60 floor); generation experiment frozen with
  amendments A1-A4, NOT run (directive: no campaign); protocol + results docs/sagacity/NEGATIVE_SPACE_EVALUATION.md.
mcp (PAN-44): local stdio read-only server pan/mcpserve.py (pan_search, pan_pivot, pan_refs, atlas_lookup);
  clearance fixed at launch (generator|evaluator), REFUSE-rule paths never served, read-only DB session;
  controls/MCP_20261011T104148Z.json 15/15; official SDK client (mcp 2.3.0) conformance PASS; registered nowhere
  (Q-015); contract docs/sagacity/MCP_INTERFACE_PROTOTYPE.md.
SECURITY (17:1xZ): origin github.com/jcraig949jfi/Prometheus is PUBLIC -- PAN-47 credential-shaped files (apollo configs since 2026-04-04,
  evidence_wiki/config.json since 2026-09-01, a committed azure.env since 2026-09-23) are public; rotate first (Q-017, #2129, #2161).
continuity: docs/sagacity/CONTINUITY_HANDOFF.md (standing owner: Pan seat in maintenance mode + Mnemosyne DB
  co-owner + Aporia watcher; Q-016 unattended maintenance, default session-driven).
questions for the operator: QUESTIONS.md (16 open, Q-002..Q-017; Q-017 credential rotation after PAN-47; Q-014 MCP least-privilege role, Q-015 MCP registration; Q-001 executed via Atlas; Q-012: host keys for ubu004-006).
