# Atlas backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-19 (charter + addendum adopted; first pass landed).
Closed today: ATLAS-01 (charter committed 4fb8c7fc2 + addendum cbe1d149d),
ATLAS-02 (this file), ATLAS-03 (no standing loop created; journal says so).
Closed 2026-09-19: ATLAS-24 by operator ruling (F:/SerendipityD: ignore for now;
engine row marked IGNORED, its local root removed from the registry).
Closed 2026-09-19: ATLAS-27 -- local_files/4 loss tracking (present=false + dated
file.missing fact; flips back on return; host-scoped) and storage_role (primary |
copy | backup; only the root itself is primary; declared engine_instance for live
stores); migration 007 reset two M1 storage_roots set by the old rule.
Closed 2026-09-19: ATLAS-06 -- archaeon_campaigns/3 reads every RECORD.md DISPOSITION
paragraph as a verbatim conclusion (line pointer); cmp1 now 10/10 classed via
classify.science_class (capitalised verdict words only; mixed -> LOW).
Closed 2026-09-19: ATLAS-21 -- AtlasIndexLoop registered in MONITORS.md
(bound 6 non-productive ticks, accountable Atlas-M2) before launch; tick in loop/TICK.md.

ATLAS-04 | Run the M2 Atlas instance from roles/Atlas/prompts/2026-09-19_m2_instance/ and merge its host-local rows (frontier runs/, M2 SFE ledger, M2 logs) into the same keys | ENGINE | beta | M | operator (starts the M2 instance) | harvest_run rows with host_id=M2; EXPECTED:M2 sources drop below 10% of their 2026-09-19 count
ATLAS-05 | Write a git adapter for archaeon/wse/ledgers (wse-survey-v01, ssf-c1..3) so the 4 PEW-only campaigns get receipts, attempts and facts | TOOLS | beta | S | none | archaeon.wse/* experiments with n_attempts > 0 and source links to git
ATLAS-34 | Index Crius (campaign 2: rungs, PARTS donors, takeovers.jsonl, paired streams) as an engine so RA-4 can run and Crius joins the manifest | TOOLS | beta | M | Crius C2 arm complete | crius campaign + experiments in atlas.campaign; RA-4 analysis possible
ATLAS-35 | Index the Nyx mechanism ledger and Techne fossil CATALOG as entities so GEA-4 and RA-5 have machine-readable organ/fossil inventories | TOOLS | beta | M | none | mechanisms and fossils queryable beside experiments; rediscovery dedup possible
ATLAS-36 | Build the reanalysis pipeline the queue depends on (learned behaviour descriptors with a synthetic positive control) and run RA-2 over GraphWorld + CW01 rows | EVIDENCE | 1.0 | M | ATLAS-07 | descriptor pipeline + RA-2 report with controls stated
ATLAS-31 | Re-verify the catalogue's SEARCH_RESULT/UNVERIFIED links (192 of 834) and record which moved or died, as a catalog/2 pass | TOOLS | beta | M | none | url_status transitions per link in harvest counts
ATLAS-32 | Expand the catalogue from its 16 source lists (awesome-open-ended ~101, ALife Encyclopedia platforms, OEE workshops) and the internal herakles/aporia lists, verifying each addition | EVIDENCE | beta | L | none | ECOSYSTEMS.jsonl growth with verified code share reported
ATLAS-33 | Derive ANALOGUE_OF edges between external ecosystems and Prometheus experiments that share world/organism/pressure axes (ATLAS_DERIVED, rule + version) | EVIDENCE | 1.0 | M | none | edges with method; a positive control pair (SFE campaigns ~ Tierra-class soups) and a negative pair
ATLAS-28 | Make local_files scale to dense logs: incremental (skip unchanged size+mtime), no hashing of logs or files > 5 MB, and a per-root "granularity" (file | dir_summary | rotating-log family) so a log tree becomes a handful of pointers, not thousands of rows | TOOLS | beta | M | none | pass time and row count on M1 roots before/after; registry rows declare granularity
ATLAS-29 | Record each log's covered time span (first/last timestamp from a small head/tail read) on source.time_start/time_end, then link logs to attempts on the same host whose run window overlaps (edge basis INFERRED) | TOOLS | beta | M | ATLAS-28 | attempts with log links on M1; same code serves Atlas-M2 on M2
ATLAS-30 | Add a growth/coverage view: bytes and files per host, root and week, and pointers whose files vanished, so the operator can see what exists and what is at risk before culling | ENGINE | beta | S | ATLAS-27 | atlas.v_local_volume + report section
ATLAS-07 | Add an NPE QD-cells collector (primordial/ledger/qd/cells.jsonl, draws.jsonl, world_set_r8.json) as world x pressure x representation descriptors | TOOLS | beta | M | none | facts of kind world_descriptor/pressure_descriptor on graphworld experiments; R10 recomputed
ATLAS-08 | Harvest the remaining local nestor/* branches (r2..r8 lanes, e05-replica, arch4-loop) and record which commits exist only there | TOOLS | beta | S | none | git_commit rows with seen_on_host=M1 per branch; source rows GIT_LOCAL:M1
ATLAS-09 | Map pm-data epoch-logs (527 epochs-<hash> dirs) to rounds/epochs via ROUND_rN.json and epoch_log.jsonl | TOOLS | beta | M | none | file:// sources linked to graphworld campaigns instead of the engine
ATLAS-10 | Index Harmonia rulers and qualification ledgers (roles/Harmonia/science, qualification) as engine harmonia.rulers | TOOLS | beta | M | none | harmonia.rulers experiments with instance tags mapped to hosts (M2/M3)
ATLAS-11 | Index Bellerophon toolbox runs (overnight C-cycles) as a third driver of SFE/NPE backends | TOOLS | beta | M | none | bellerophon.toolbox campaign rows; backend recorded per attempt
ATLAS-12 | Index Herakles EVCA, Proteus and Ludus runs (engines registered, not harvested) | TOOLS | 1.0 | L | none | experiments for each of the three engine ids
ATLAS-13 | Resolve the synthetic NPE engine instances (133 per code sha) into service intervals per host using MACHINE_PROFILE and bus exports | ENGINE | beta | M | none | engine_instance rows with first/last_seen intervals, count reduced with the rule written down
ATLAS-14 | Link Vivarium queue rows to Archaeon experiments beyond C4-REH-1 (candidate_set_id, artifact_locators, pew_reference) | TOOLS | beta | S | none | EXECUTION_OF edges for every family that names a driver experiment
ATLAS-15 | Add SAME_MEASUREMENT_AS derivation: measurement names that recur under different names (effect/advantage/lift) with unit + definition match | EVIDENCE | 1.0 | M | none | ATLAS_DERIVED edges with method + version and a positive control on a known synonym pair
ATLAS-16 | Add rule R14 'reruns whose conclusion changed after a BUG_FIX/INSTRUMENTATION_REPAIR edge' once edge reasons are populated from ledger/decision text | EVIDENCE | 1.0 | M | ATLAS-15 | signals with the fixing defect linked
ATLAS-17 | Add rule R15 'effects by world / organism family' (a measured effect whose sign or size tracks world_family across engines) | EVIDENCE | 1.0 | M | ATLAS-07 | signals grouping by family with counts and eligibility
ATLAS-18 | Compute eligibility counts beside every comb rule (how many subjects COULD fire) so 'nothing fired' and 'nothing could fire' are distinguishable | EVIDENCE | beta | S | none | signal.evidence carries eligible_n; report prints it per rule
ATLAS-19 | Parse CW01 BOUNDARY/CYCLE reports and Archaeon DECISIONS for rerun reasons (bug fix, ruler repair, more telemetry) onto attempt edges | TOOLS | beta | M | none | fraction of RERUN_OF edges with reason UNKNOWN reported before/after
ATLAS-20 | Read the frontier digests (EPOCH_*.json) as campaign-level observations and conclusions | TOOLS | beta | S | none | conclusions on archaeon.frontier/deep-frontier with digest pointers
ATLAS-22 | Publish the manifest as a read-only view set (atlas.v_manifest etc.) documented for seats; no seat is asked to emit data for Atlas | ENGINE | beta | S | none | roles/Atlas/QUERIES.md with 10 tested queries
ATLAS-23 | Report the committed cleartext DB credentials in evidence_wiki/config.json to Mnemosyne if not already tracked (seen while wiring the connection; not Atlas's lane) | ENGINE | program | S | none | comms post id or a line citing the existing tracker entry
ATLAS-25 | Add a per-campaign coverage table (what each adapter extracted vs the files present) so a recomb can target the biggest unextracted shapes first (v_shape_inventory) | TOOLS | beta | S | none | report section listing top 20 unextracted shapes by count
ATLAS-26 | Decide with the operator whether Atlas may ask driving seats for an interface change (e.g. a hostname field in receipts) | ENGINE | program | XL | NEW: may Atlas request receipt fields (hostname, engine_instance) from Archaeon/Nestor? | decision recorded; until then Atlas infers and labels
