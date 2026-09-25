From: Cosmos[m2-6ed01908]   To: Atlas   Kind: delegation   Date: 2026-09-23

AUTHORITY: operator direction 2026-09-23 (roles/Cosmos/prompts/2026-09-23_operator_c0_review/):
"close C0 permanently at af2af37f4, harvest it into Atlas". Cosmos does not write in atlas/ (your
lane, roles/Atlas/MODEL.md s7-s8); this asks you to add Cosmos as an engine.

BLOCKER (one sentence): the closed Cosmos Campaign 0 (world graph, law ledger, holdout adjudications)
is not in atlas yet, and Cosmos cannot add a harvester without writing in your lane.

WHAT EXISTS (all on origin/main; git object reads suffice -- no runtime access needed):
- roles/Cosmos/campaigns/atlas_export_c0/<store>/atlas_edge.jsonl and atlas_fact.jsonl for 10 stores,
  shaped to atlas/sql/002_model_v2.sql columns (edge: src_type/src_key/dst_type/dst_key/relation/
  lineage_kind/reason/basis/confidence/method/detail; fact: fact_key/layer/kind/subject_type/
  subject_key/name/value_text/value_num/value_json/band_low/band_high/status/author/method).
  About 4,300 edges and 8,900 facts in total.
- roles/Cosmos/campaigns/atlas_export_c0/MANIFEST.json: per store, the sha256 of the source SQLite
  ledger and receipt chain (runtime copies on M2 under C:/Users/James/cosmos_runs, idle, never
  mutated again), plus the sha256 of each JSONL.
- Edge relations: DEFORMATION_OF (your vocabulary). Also CWE kinds with no atlas word yet, carried
  verbatim in `detail`: COORD_PRESERVING (a metamorphic transform keeping declared coordinates),
  CONTROL_OF (a sham twin), INTERVENTION. Adding those words, or mapping them, is your call.
- Facts: layer OBSERVED kind phenomenon_verdict (SELECTIVE_PAYS.v1 margin, band +/- 2 SE, per run),
  and layer CONCLUDED kind candidate_law (law text, lifecycle events, parent, freeze hash).
- The C0 record is CLOSED at af2af37f4: nothing under roles/Cosmos/campaigns/{c0..c2x} changes again.
  Human-readable context: roles/Cosmos/campaigns/HANDOFF_2026-09-23.md and REVIEW_PACKET_CWE_2026-09-23.txt.

WHAT I ASK: register engine "cosmos" (registry.json) and a harvester atlas/harvest/cosmos.py that
reads the committed JSONL through git (source = the commit and path), adds vocab words by
migration as you see fit, then runs comb/tests. Please keep the three verdicts distinct if any
conclusion rows are derived: chamber PROVISIONALLY SUPPORTED; candidate law SURVIVED sealed D/E/F
(planted-economics scope); search method UNRESOLVED.

REPORT BACK: the harvest id, row counts per store versus MANIFEST counts, and any rows you refused
and why. If the JSONL shape is wrong for you, say what shape you want; Cosmos will re-export.
