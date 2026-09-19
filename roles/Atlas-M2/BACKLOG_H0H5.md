# Atlas-M2 backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-19 (seat created; every item below the first three is
conditional on the operator's instructions and says so in blocked_on.
Fewer than the schema's 20 rows on purpose: a backlog written before the
charter would be a backlog of guesses; rows are added as the
instructions name work).

Closed today: AM2-01 (seat created: this directory + INHERITANCE rows),
AM2-02 (comms boot as Atlas-M2 on the M1 store), AM2-03 (Atlas's
BOOT_M2.md read, hash-verified, recorded as not-yet-authorised).

AM2-04 | Receive the operator's instructions verbatim under prompts/<date>_<topic>/ with a MANIFEST and restate the seat's authorised scope in RESPONSIBILITIES.md s0 | ENGINE | alpha | S | operator (the instructions) | prompts dir + MANIFEST committed; RESPONSIBILITIES.md currency line updated
AM2-05 | Post the first comms report to Atlas: seat exists, identity differs from BOOT_M2.md's assumption, journal location, what M2 roots are present/absent | ENGINE | alpha | S | none | comms message id in journal/2026-09-19.md
AM2-06 | Survey M2-local evidence roots read-only (SFE data dir, frontier runs/ receipt trees, Vivarium var/, consumer/engine logs, any other engine data root) and commit the inventory as roles/Atlas-M2/SOURCES_M2.md with sizes, mtimes, liveness and owner seat | TOOLS | alpha | S | operator instructions (read scope) | SOURCES_M2.md with one row per root; no file opened for writing; no ledger opened at all
AM2-07 | Add host-M2 rows to atlas/registry.json local_roots (live trees no_hash, live ledgers stat-only) in a change proposed to Atlas, not merged over Atlas's copy | TOOLS | alpha | S | AM2-06, operator instructions | registry diff committed on this seat's branch + comms delegation/report to Atlas
AM2-08 | Run python -m atlas harvest local_files ; comb ; report --out roles/Atlas-M2/reports/REPORT_<date>_M2.txt ; pytest -q atlas/tests, from this worktree against the M1 index, and commit the report with before/after counts of EXPECTED:M2 vs FS:M2 sources | TOOLS | alpha | S | AM2-07, write authorisation to schema atlas | report file; harvest_run rows with host_id=M2; the two counts
AM2-09 | Extend atlas/harvest/frontier.py (bump VERSION) to read RECEIPT.json from the M2 receipt tree and enrich EXPECTED:M2 hostfile:// sources to FS:M2 present=true on the same keys, with a positive and a cheat control in atlas/tests | TOOLS | beta | M | AM2-08, Atlas (owner of atlas/) | tests pass on the merged tree; attempts on archaeon.frontier gain receipts; engine_instance eng_906356f7... gains storage_root and counts
AM2-10 | Record the ABSENT roots BOOT_M2.md expected (C:\Prometheus-vault) as a dated observation for Atlas, not as "did not happen" | EVIDENCE | alpha | S | none | line in SOURCES_M2.md + the comms report
AM2-11 | Write a one-page ROUNDTRIP.md: how a row written from M2 reaches Atlas's report, which fields M2 can fill that M1 cannot, and how a conflict surfaces (field_conflict) | EVIDENCE | beta | S | AM2-08 | file committed; one worked example with real keys
AM2-12 | Decide with the operator whether Atlas-M2 may open the live SFE SQLite ledger read-only+immutable at all while the engine runs on this host, or only point at it (MODEL.md s8 says idle ledgers only) | ENGINE | program | XL | NEW: may Atlas-M2 read the live M2 SFE ledger, or stat only? | decision recorded here and in RESPONSIBILITIES.md s3
