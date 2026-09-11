# SEAMS reuse targets as found on the trial branch (RHAD-08)

Measured 2026-09-11 on rhadamanthus/native-trial-2026-09-11 (e17934d9a plus
uncommitted trial files). Counts by wc -l / json parse; last-touch by git
log -1.

| target | exists | rows/lines | last commit | note |
|---|---|---|---|---|
| engine/ledger/AGENT_AUTOPSIES.jsonl | yes | 21 rows | 14ae944bb 2026-08-21 | one row per agent; rows for Erebos, Pollux; NO row for Nous |
| engine/ledger/AUTOPSY_TAXONOMY.md | yes | 157 lines, 5 clusters + 1 singleton + 5 clean nulls | 14ae944bb 2026-08-21 | Pollux in Cluster 2 (LOW-BITS-EMISSION) and Cluster 4 (secondary); Erebos in Cluster 5 (SEAM-BROKEN); Nous absent |
| engine/queues/CONSUMPTION.jsonl | yes | 231 rows, 2026-08-18..2026-09-01 | 232383781 2026-09-01 | keys ts/object/consumed_by/effect/summary; 11 rows mention the trial graves |
| roles/Kairos/necropolis_evidence/ | yes | README.md only (9 lines) | -- | "Empty as of 2026-09-11"; Kairos writes LAW N14 findings here; nothing consumes it yet |
| engine/necropolis/dossiers/ | yes | 4 dossiers (coeus, argos, hephaestus, acheron exemplar) + _TEMPLATE | c7340a6ad 2026-09-10 | acheron is all-NOT_EXAMINED by design |

CONSUMPTION rows that bear on the trial graves (primary observations of a
later date; interpretation status: they are certificates, not evidence):

- 2026-08-19 "DR back-corpus batch 19 (Erebos arc ...)" -> germline lineage
  + kill_pattern taxonomy; 0 new anchors.
- 2026-08-19 "Erebos v2 generator design audits (22 reports ...)" -> probe/
  challenge generator design lane; g16 flagged.
- 2026-08-20 "SALVAGE-NOUS concept-dictionary lift" -> techne/registry/
  concepts_index.jsonl + build script; reading "DICT-LOADABLE as pre-stated;
  95/20/4-mechanism census by execution". This is a prior salvage of Nous
  residue that the Necromancer pass must either find independently or be
  measured against.
- 2026-08-21 "AUTOPSY batch 3 (Eos/Erebos/Harmonia_Loop)" and "AUTOPSY batch
  (Nemesis, Nephele, Pollux)" -> AGENT_AUTOPSIES rows (the certificates
  under review today).
- 2026-08-21 "AUTOPSY TIER COMPLETE 21/21 + dedup/merge" -> AUTOPSY_TAXONOMY.

What no SEAMS target holds: any Necropolis-format consumption row (no row
in CONSUMPTION.jsonl has consumed_by under engine/necropolis/); any row
for Nous in AGENT_AUTOPSIES; any runtime artifact of Pollux or Erebos.
