# Pheme calibration ledger

Currency: 2026-09-11. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently.

date | call made | what was true | corrected by | changed practice
2026-05-23 | the May charter (Aporia, for this seat) assumed an Ergon Learner eval root would exist at one of three paths and built a 30-min loop on it | no root ever existed; 354 ticks, 0 profiles, the loop alarmed every 25-30 min for a week and was read as noise (pivot/orchestration_monitoring_2026-05-24.md) | pivot dossier 2026-06-24; this pass | verify the input exists before a loop is started (base rule 8; feedback_verify_signature_exists_before_controls); a loop with no input is registered DEAD, never left running as a sentinel
