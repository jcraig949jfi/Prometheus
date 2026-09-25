# Atlas-M2 backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-25 (pre-reboot pass; the live queue in take-order is
roles/Atlas-M2/TODO_2026-09-25.md and this file is the longer horizon.
Fewer than the schema's 20 rows on purpose: rows are added as work is
named, not guessed).

Closed 2026-09-19: AM2-01 (seat created: this directory + INHERITANCE
rows), AM2-02 (comms boot as Atlas-M2 on the M1 store), AM2-03 (Atlas's
BOOT_M2.md read, hash-verified, recorded as not-yet-authorised), AM2-04
(ongoing directive verbatim + MANIFEST), AM2-05 (first report to Atlas,
#499), AM2-06 (SOURCES_M2.md stat-only inventory), AM2-07 (8 host-M2
local_roots rows), AM2-08 (local_files pass: 137 FS:M2 sources, 2378
facts, eng_906356f7 enriched), AM2-09 (frontier_runs_m2/1 and /2: every
runs/ pointer FS:M2, 0 keys minted, 5 controls), AM2-10 (ABSENT vault
recorded as a dated observation). AM2-12 (may the live ledger be opened?)
is carried as TODO item 5, still the stricter practice: point only.
Closed rows are deleted from the body by this commit, as base role s7 asks.

AM2-11 | Write a one-page ROUNDTRIP.md: how a row written from M2 reaches Atlas's report, which fields M2 can fill that M1 cannot, and how a conflict surfaces (field_conflict) | EVIDENCE | beta | S | AM2-08 | file committed; one worked example with real keys
AM2-13 | Ingest the 71 frontier receipts that accumulated during the park (runs/ 230 -> 540 files, newest 2026-09-22T19:07:50Z) and report what moved | TOOLS | alpha | S | none (loop resume is the operator's word, the work is not blocked) | REPORT_<date>_M2.txt with BEFORE/AFTER EXPECTED:M2 vs FS:M2 and matched vs unmatched counts
AM2-14 | Settle de-duplication for run trees that appear under several worktree paths (Ensorain 146 MB/317 files, Ares 51 MB/1,076 files, copies in 5+ worktrees) before any registry row, then register the engines | TOOLS | beta | M | Ensorain and Ares (which path is authoritative) | a rule written in MODEL-terms in RESUME.md s5 + engines in atlas/registry.json with a harvester listed for M2
AM2-15 | Identify the owner of C:/Prometheus-data/evidence (envgate01_2026-09-24, z80atlas_campaign_2026-09-19) and index it only with their answer | TOOLS | beta | S | the owning seat | comms question posted; registry row or a recorded refusal
AM2-16 | Re-run local_files after each of Atlas's ATLAS-28/29/30 changes lands and confirm the M2 rows still behave (granularity, incremental skip, loss tracking) | TOOLS | beta | S | Atlas (his loop parked) | a pass with his new VERSION over the M2 roots with counts in the journal
AM2-17 | Keep the operator's SQLite/DuckDB sighting list current: name any NEW .db/.sqlite/.duckdb file a collector stats, in the tick receipt | EVIDENCE | program | S | none | a line per tick; checked 2026-09-25 (none new)
