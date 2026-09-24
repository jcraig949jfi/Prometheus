# Ananke backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-24. PROVISIONAL. The schema requires 20 to 60 items;
this file holds 4 because the seat has no charter yet and inventing more
would be fabrication, not a backlog. It is rewritten to the schema on the
day the mission lands (ANANKE-02).

ANANKE-01 | Commit the operator's mission verbatim under roles/Ananke/prompts/<date>_charter/ with a MANIFEST and rewrite RESPONSIBILITIES.md around it (pre-charter body to superseded/) | ENGINE | program | S | operator (the mission itself) | MANIFEST.md verifying under python -m comms.manifest verify; RESPONSIBILITIES.md with a one-sentence contract
ANANKE-02 | File the 20-60 item backlog in the schema, first five startable today, XL rows naming decision ids | ENGINE | program | S | ANANKE-01 | this file, rewritten, passing a line-count and column-count check
ANANKE-03 | Register every standing loop the charter creates in roles/base-role/MONITORS.md with bound and accountable_seat columns, or record that it creates none | ENGINE | program | S | ANANKE-01 | a MONITORS.md row per loop, or a journal line stating none
ANANKE-04 | Mission-scoped failure census: enumerate (not sample) the closures, defect/kill ledgers, calibration ledgers and nulls relevant to the mission, with the failure SHAPE and the opening each exposes, before any recommendation | ENGINE | program | M | ANANKE-01 | a committed census file with one row per source and a count per ledger, citing SHAs
