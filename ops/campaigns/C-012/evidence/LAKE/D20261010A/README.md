# C-012-T005 bounded lake demonstration -- D20261010A (2026-10-10, M2)

What: the qualification evidence of the two-node run (Moonshot schema moonshot_qual, run Q20261010A: 8 chains, 23
publications, 30 attempts, 23 validations, 2 contests) materialized into Pan's lake through Pan's own functions
(pan.iceberg.write / last_snapshot_properties / read / tables, Pan 801e09d6b as merged), namespace `moonshot`,
tables prefixed `qual_` (contract s6, agreed with Pan in #2004; the committed contract and three open points sent
in #2010, Pan's review pending). Interpreter: Moonshot's lake venv C:/Prometheus-data/moonshot/venv (Pan's pins).
The lake's data files are Pan's, on M2's NVMe; the catalogue rows are in M1 Postgres (pan_iceberg).

`LAKE_DEMO.json` holds every step's full report, the table listing after the crash and at the end, the catalogue
view's rows and Moonshot's logged reports. `../run_lake_demo.py` is the driver; `../MUTATION_TABLE.json` the 14/14
mutation table of the materializer and the view (bba336602).

Steps and results (settle 60 s; every source row was older):
1. Crash run (a separate process; dies before the qual_trace_lines commit): exit 3; afterwards the lake held ONE
   table, moonshot.qual_epochs, 23 rows -- one committed table, nothing half-written.
2. Normal run (a fresh process): epochs appended 0 (resumed after its own watermark), trace_lines 69, attempts 30,
   validations 23, contests_opened 2, resolutions 2; oracle OK on every table (lake = Postgres eligible; nothing
   missed, invented or duplicated).
3. Repeat run: appended 0 on every table; oracle OK.
End state: 6 tables, ONE snapshot each (one commit per table carrying its watermark); catalog_v lists 22 live
epochs (23 publications less the one overturned in S4); 2 materializer reports logged in moonshot_qual's events
(the crash run died before logging, as a crash would).

Not established here: scale (all six tables are re-read in full by the oracle on every run, and every source row is
re-mapped; fine at 23 publications, to be measured in T004); a DUPLICATED oracle result is detected but not repaired
(an append-only lake is repaired by rewriting the table: an owner's decision); the settle window bounds -- it does not
eliminate -- the late-commit race, which the MISSED oracle and repair=True cover; Pan's collector for catalog_v is
Pan's to build (pull model), and the production view is moonshot.catalog_v once the production schema exists.
