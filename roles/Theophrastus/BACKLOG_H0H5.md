# Theophrastus backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-13.

| id | item | proof of done | blocker | size |
|---|---|---|---|---|
| THEO-01 | Prior-evidence gate before signal admission (calibration ledger vs signal queue) | signals.jsonl rows carry prior_evidence_class at ADMISSION, not post hoc; a predicted contrast lands in calibration.jsonl | REQ-001 for cross-producer lookups; can start with published_P + C1-e locally | M |
| THEO-02 | Declare interaction families (pressure x world, branch x world = BRANCH_REVERSAL) with their own SE in a new PREREG | PREREG_2 committed before the run; contrasts.jsonl rows with family C-PxW / C-BxW | none | S |
| THEO-03 | Second round: W999 + P_unif (the record is silent), same 4 mechanisms, prereg first | rows at n_cells=999 with fossils | budget: ~40 s per cell at 999 | S |
| THEO-04 | Populate `ecology` on this seat's PEW writes (own encounter body) | encounters read back with ecology.cell_id | none (REQ-001 is the SELECTOR, not the write) | S |
| THEO-05 | Register each contrast as an SFE comparison family with sealed arms | family ids on contrasts.jsonl rows; `GET /v2/families` lists them | none | S |
| THEO-06 | Cross-consumer probe (PREREG s8): one cell into viv queue, created_by=theophrastus | queue row completed by Vivarium with the same result digest | Vivarium daemon alive (Vivarium's call) | S |
| THEO-07 | Player-id convention for recovered specimens | Herakles answer in INBOX; ecology.py uses it | question posted to Herakles | XS |
| THEO-08 | Rule-10 bound + accountable seat + MONITORS.md row before any unattended crawl | row in roles/base-role/MONITORS.md | operator decision on accountable seat (recommend Archaeon, as for Vivarium) | XS/XL |
| THEO-09 | Counterfactual-attack mode with its own budget line and productivity signal | a run in mode=counterfactual revisiting dead.jsonl cells with a receipt | THEO-08 | S |
| THEO-10 | Nyx catalogue as a mechanism source (268 bits, name-blind gate) -- which entries are executable in an existing kind | recon note listing executable Nyx entries per kind | Nyx's catalogue format | M |
