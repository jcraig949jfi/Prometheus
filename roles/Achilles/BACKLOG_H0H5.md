# Achilles backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-10-01. Charter: roles/Achilles/prompts/2026-09-30_charter/.
The first five are today's. Lane for all rows: TOOLS (fleet observability).

ACHILLES-01 | Publish the first census (snapshot, page, email block, run status, receipt) to origin/main | TOOLS | beta | S | none | docs/fleet/fleet_state.json + roles/Achilles/census/runs/2026-10.jsonl on main
ACHILLES-02 | Register PrometheusFleetCensus (every 6 h) on ELSA from a pinned worktree, with its MONITORS.md row | TOOLS | beta | S | none | Get-ScheduledTaskInfo output in the journal; MONITORS row; self-test passes on ELSA
ACHILLES-03 | Land the census section in the existing mailer and verify delivery from the mailer's own receipt | TOOLS | beta | S | M4 loop picking up main | agora.intelligence_outputs email_dispatched summary carrying census=<timestamp>; snapshot mailer.census_included_last true
ACHILLES-04 | Verify the GitHub Pages deployment of docs/fleet/ | TOOLS | beta | S | pages.yml run | pages workflow run id + HTTP 200 for /Prometheus/fleet/ recorded in the journal
ACHILLES-05 | Report the data-quality defects found on the first run to their owners as comms reports | EVIDENCE | beta | S | none | comms ids in the journal (RECONSTRUCTION s5 items)
ACHILLES-06 | Read every run's anomalies and route new cross-lane defects to owners (reports, never delegations) | EVIDENCE | program | S | none | journal entries citing comms ids
ACHILLES-07 | Measure attribution coverage per run and drive unattributed commits below 5 percent by adding evidence-backed alias rows | TOOLS | 1.0 | M | none | stats.unattributed / commits_scanned in run receipts
ACHILLES-08 | Add ops/campaigns/*/E-*/RESULT.md and roles/*/REVIEW_PACKET* as experiment sources beside commit vocabulary | TOOLS | 1.0 | M | none | last_experiment sources in the snapshot; test
ACHILLES-09 | Add Fabric task/attempt rows as activity evidence once the Windows CLI defect (#1135) is fixed | TOOLS | 1.0 | S | Odysseus (#1135) | fabric source in sources_status; test
ACHILLES-10 | Re-verify the seat registry against new role documents each deep pass and flag drift (declared vs observed role) | TOOLS | 1.0 | M | none | REGISTRY_STALE flag + test
ACHILLES-11 | Offer the v2 snapshot to Aporia as the machine-maintained successor of CENSUS.json v1 (Aporia decides) | EVIDENCE | 1.0 | S | Aporia | comms report id; Aporia's answer recorded
ACHILLES-12 | Calibrate the state rules against Aporia's hand census over 7 days and record disagreements | EVIDENCE | 1.0 | M | 7 days of runs | roles/Achilles/calibration/RULES_VS_APORIA.md with the rows
ACHILLES-13 | Add a weekly trend section (state transitions per seat, activity heatmap) from the run receipts | TOOLS | 1.1 | M | 7 days of runs | page section + test
ACHILLES-14 | Report the 0/48 agents-alive TL;DR in the brief email to the producer's owner with the census as the replacement source | EVIDENCE | beta | S | METIS-01R owner | comms report id
ACHILLES-15 | Report stale atlas/registry.json engine paths (Cosmos, Ananke, Ensorain, primordial, crius) to Atlas | EVIDENCE | beta | S | none | comms report id
ACHILLES-16 | Report the INHERITANCE.md duplicate Icarus row and the missing Theophrastus entry-file row to Archaeon | EVIDENCE | beta | S | none | comms report id
ACHILLES-17 | Add an archived per-run snapshot index (docs/fleet/history/) only if the git history of fleet_state.json proves insufficient | TOOLS | 1.1 | S | evidence of need | decision note in the journal
ACHILLES-18 | Make host detection read comms.environments / atlas hosts instead of the built-in map once those carry ELSA, ubu00x, BUCKKEEP | TOOLS | 1.1 | S | atlas/registry.json hosts | test
ACHILLES-19 | Document how a new seat appears in the census within one run (creation pass checklist line) | TOOLS | 1.0 | S | none | line in roles/base-role/README.md proposed to Archaeon
ACHILLES-20 | Decide with the operator whether the census should also run from a second host for redundancy | TOOLS | 1.1 | XL | NEW: second census host for redundancy | operator answer recorded
