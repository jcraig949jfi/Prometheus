# Artemis backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-27 (charter received: research backlog ecology). These
are the SEAT's own work items; the research frontier itself is
roles/Artemis/backlog/. Lane LIT = literature/prior art; EVIDENCE =
backlog curation. First five are today's.

ARTEMIS-01 | Commit the charter verbatim with a MANIFEST | EVIDENCE | beta | S | none | prompts/2026-09-27_charter_research_backlog_ecology/MANIFEST.md verifies
ARTEMIS-02 | Rewrite RESPONSIBILITIES.md around the charter, pre-charter body to superseded/ | EVIDENCE | beta | S | none | RESPONSIBILITIES.md + superseded/RESPONSIBILITIES_pre-charter_2026-09-27.md
ARTEMIS-03 | Harvest candidate threads from five repository domains with provenance | EVIDENCE | beta | M | none | backlog/harvest/D1..D5 committed
ARTEMIS-04 | Deduplicate, link and sharpen the harvest into FR threads | EVIDENCE | beta | M | ARTEMIS-03 | backlog/INDEX.md + threads/FR-*.md
ARTEMIS-05 | Write the first FRONTIER.md with backlog health | EVIDENCE | beta | S | ARTEMIS-04 | backlog/FRONTIER.md committed and pushed
ARTEMIS-06 | Check prior art for the strongest threads, URLs cited | LIT | beta | M | ARTEMIS-04 | backlog/prior_art/*.md
ARTEMIS-07 | Chop a modest number of mature threads into spikes/experiments/tasks | EVIDENCE | beta | M | ARTEMIS-04 | backlog/chops/FR-*.md
ARTEMIS-08 | Mark threads a bare Linux node can take (HOST FIT) and list them in FRONTIER | EVIDENCE | beta | S | ARTEMIS-04 | FRONTIER.md "any Linux node" section
ARTEMIS-09 | Link every ops/threads TH-### into the index without editing ops/ | EVIDENCE | beta | S | ARTEMIS-04 | INDEX.md rows with ops: TH-nnn
ARTEMIS-10 | Staleness pass: re-read threads older than 7 days against new commits | EVIDENCE | 1.0 | S | ARTEMIS-04 | FRONTIER.md staleness section with what changed
ARTEMIS-11 | Harvest new commits since the last pass (incremental) | EVIDENCE | 1.0 | S | ARTEMIS-05 | harvest/INC_<date>.md
ARTEMIS-12 | Measure backlog health over passes (counts, answered-rate, age) | EVIDENCE | 1.0 | S | ARTEMIS-11 | FRONTIER.md health table with two passes
ARTEMIS-13 | Harvest comms 'question' messages and ew open hypotheses read-only | EVIDENCE | 1.0 | S | none | harvest entries citing comms ids / ew rows
ARTEMIS-14 | Record which threads were picked up and by whom, from commits only | EVIDENCE | 1.0 | S | ARTEMIS-05 | INDEX.md picked-up column from git evidence
ARTEMIS-15 | Offer the frontier to seats via one comms broadcast when the operator agrees | EVIDENCE | 1.0 | S | operator | comms message id
ARTEMIS-16 | Propose promotion of mature FR threads into ops/threads if the operator selects Artemis for the pilot | EVIDENCE | program | XL | NEW: whether Artemis joins the ops pilot | ruling recorded
ARTEMIS-17 | Keep the SFE retrospective's six threads (T1-T6) represented and current | EVIDENCE | beta | S | none | FR rows citing threads/sfe_retrospective/THREADS.md
ARTEMIS-18 | Deepen prior art on the new-lens candidates (questions no engine expresses) | LIT | 1.0 | M | ARTEMIS-06 | prior_art/new_lens_*.md
ARTEMIS-19 | Test the backlog's usefulness: hand one MATURE thread to a fresh worker and record friction | EVIDENCE | 1.0 | M | operator | a handoff report committed by the worker
ARTEMIS-20 | Revise the thread format only if two passes show a field is unused or missing | EVIDENCE | 1.1 | S | ARTEMIS-12 | README.md change with the evidence cited
ARTEMIS-21 | Keep ABOUT.md host facts dated and re-measured at boot | EVIDENCE | beta | S | none | ABOUT.md currency line
