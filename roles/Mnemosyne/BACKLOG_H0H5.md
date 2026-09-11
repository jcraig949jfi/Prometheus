BACKLOG -- Mnemosyne / PEW (evidence, references, provenance, durability)
Currency: 2026-09-11. Schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md
Built from 96a22e736513d2323867d1bf587214d4e08ac7f3 in
F:\Prometheus-worktrees\mnemosyne-baserole on mnemosyne/baserole-adopt.

The first five are what I start today.

MNE-01 | Correct the seat file: currency date, drop the drive letters, retire the dead Redis/lmfdb phases, replace the standing "BLOCKED on James" items | EVIDENCE | program | S | operator ruling on the four quoted conflicts | roles/Mnemosyne/RESPONSIBILITIES.md with a currency date and no absolute paths
MNE-02 | DONE 2026-09-11 (5c51e8a0a, kept per pass) | EVIDENCE | program | S | none | roles/Mnemosyne/journal/2026-09-11.md
MNE-03 | DONE 2026-09-11 (75c2f5fcc): prompt to Daedalus committed at roles/Mnemosyne/prompts/2026-09-11_daedalus/01_BINDS_SESSION.md with MANIFEST | EVIDENCE | program | S | Daedalus's answer | the answer, in my inbox
MNE-04 | DONE 2026-09-11 (75c2f5fcc): prompt to Daedalus committed at roles/Mnemosyne/prompts/2026-09-11_daedalus/02_WRITER_LEASE.md with MANIFEST | ENGINE | program | S | Daedalus's answer | the answer, in my inbox
MNE-05 | Re-index cs-c3-2 (150/150 completed as of 2026-09-11 14:15) and commit the delta receipt; folded into MNE-34 | EVIDENCE | alpha | S | none | integration/index_receipt_cs-c3-2.json with rows_completed 150
MNE-06 | Build WP-X5 witness presence index against a real witness | EVIDENCE | beta | M | Vivarium (a witness to index) + operator D-15 | one program-witness and one CA-witness round trip, resolved to authoritative content
MNE-07 | Build the typed lineage edge route (ANCESTOR/MUTATION/TRANSFER with declared mapping) | EVIDENCE | beta | M | operator D-15 ordering with X5 | POST /api/v1/fossil/edges with the idempotent/409 battery green
MNE-08 | Add the off-host prod-view visibility endpoint so a remote writer can check its own namespace hygiene | EVIDENCE | beta | S | none | GET returning objects by agent visible in ew.*_prod, plus a gate
MNE-09 | Bound the connection-pool fallback so exhaustion cannot open unbounded direct connections | ENGINE | beta | S | none | a cap plus a log line, and a test that trips it
MNE-10 | Map the evidence-binding race to a clean 422 instead of a 500 | EVIDENCE | beta | S | none | a concurrent-binding test that observes 422
MNE-11 | Decide and record whether cross-namespace binding (prod evidence to a test fossil) is refused or warned | EVIDENCE | beta | XL | NEW: is a prod/test binding mismatch a hard refusal or a recorded warning | DECISIONS.md row plus the enforcing gate
MNE-12 | Rotate the PEW credentials that lived in git history, simultaneously on M1 and M2 | EVIDENCE | program | XL | operator (R-1) | tracker row moved to CLOSED with the rotation date
MNE-13 | Rotate the archive key prefixes recorded in R-3 | EVIDENCE | program | XL | operator (R-3) | tracker row moved to CLOSED
MNE-14 | Add an engine registry so anchors from any engine can be verified, not only the one configured | ENGINE | 1.0 | M | Daedalus (endpoint/credential per engine) | ew/closure.py resolving engine_instance_id to an endpoint, with a two-engine test
MNE-15 | Key fossil_worlds by (engine_instance_id, world_id) so an engine-local id is never treated as global | EVIDENCE | 1.0 | M | none | migration plus a test that two engines' identical world ids stay distinct
MNE-16 | Publish engine_instance_id on the PEW side of every fossil read so a consumer never infers it | EVIDENCE | beta | S | none | field present in the fossil read payload and asserted by a gate
MNE-17 | Prove a full restore on a DIFFERENT host, not only a scratch database on this one | EVIDENCE | 1.0 | M | a second host with PostgreSQL 17 | a restore receipt naming the other host
MNE-18 | Add off-host backup copy so the dump is not on the same disk as the database | EVIDENCE | 1.0 | M | operator (destination) | a manifest whose path is not on F: |
MNE-19 | Decide the ONTOLOGY_VERSION constant bump (code says 2, the database registry is at 7) | EVIDENCE | program | XL | NEW: does the stamped ontology_version follow the registry, and what does that mean for rows already stamped 2 | DECISIONS.md row plus the migration or the documented divergence
MNE-20 | Give the seat a BOOTSTRAP.md so a restart reads state instead of rediscovering it | EVIDENCE | program | S | none | roles/Mnemosyne/BOOTSTRAP.md naming the entry files in order
MNE-21 | Commit a copy of the review-packet and evidence-wiki skills beside the seat so they survive a machine change | TOOLS | program | S | none | roles/Mnemosyne/skills/ with both
MNE-22 | Record a calibration ledger of my own wrong calls (E12 grading another seat's row; the watchdog with no singleton guard) | EVIDENCE | program | S | none | roles/Mnemosyne/CALIBRATION.md with both entries and what each cost
MNE-23 | Measure PEW write throughput on an idle host and publish the number with its conditions | EVIDENCE | beta | S | a quiet window | a receipt with ev/s, host load and the command
MNE-24 | Retire mnemosyne/STATE.md or fold it into STATUS.md so there is one status file | EVIDENCE | program | S | none | one file, the other deleted with the commit that closed it
MNE-25 | Add a gate proving a refused publication leaves the durable observation intact | EVIDENCE | beta | S | none | a gate that kills the index mid-publication and shows the row survives
MNE-26 | Document the PEW read surface for Archaeon's mining in one page | EVIDENCE | alpha | S | none | roles/Mnemosyne/PEW_READ_SURFACE.md with worked queries
MNE-27 | Add a namespace census endpoint so test/prod separation is checkable remotely | EVIDENCE | beta | S | none | endpoint plus the gate that asserts zero test rows in prod
MNE-28 | Verify the fork witness fires across a real engine restore onto a second host | ENGINE | 1.0 | L | Daedalus plus a second host | a receipt showing 409 split_brain_ledger_fork from a genuine restore
MNE-29 | Decide retention for ledger_fork_events and session_splice_events | EVIDENCE | program | XL | NEW: are refused-contradiction records kept forever | DECISIONS.md row
MNE-30 | Add a machine-readable contract version to every read payload so a consumer can pin | EVIDENCE | beta | S | none | field present and asserted in the h0h5 battery
MNE-31 | DONE 2026-09-11 (0653e64e1, deployed e301547dd): watchdog measures the property; model warmed at startup; E14 | ENGINE | program | S | none | evidence_wiki/scripts/ew_watchdog.ps1, tests/test_watchdog.py 6/6, watchdog.log ok lines
MNE-32 | DONE 2026-09-11 (b08a4f0de): per-agent scoped tokens; Kairos read-only identity issued (R-4) | EVIDENCE | program | S | none | tests/test_agent_identity.py 6/6; tracker R-4; comms reply to Kairos
MNE-33 | DONE 2026-09-11 (a36a8234d): store-identity guard in ew.db (Hermes #69) | EVIDENCE | program | S | none | tests/test_store_identity_guard.py 3/3
MNE-34 | Index cs-c3-2 (150), cs-c3-2-r1, cs-h1h0-1-p2 all statuses, -p2-r1, -p2b, cs-h5-1 as typed refs, with --all-statuses reporting UNRESOLVED for rows without engine digests | EVIDENCE | alpha | M | cs-h5-1-r1 still queued (24 rows) | one index receipt per set under evidence_wiki/integration/
MNE-35 | Port the property probe (authenticated search, last-success line, present-but-dead restart) to ew_watchdog_m2.ps1 | ENGINE | program | S | an M2 session to verify the tick | watchdog_m2.log ok lines on M2
MNE-36 | Enforce the rule-10 BOUND in the watchdog script: after 12 consecutive non-productive ticks park and post to Mnemosyne via comms | ENGINE | program | S | none | the script branch plus a test that trips it
MNE-37 | Move battery result files out of the tracked tree or stop tracking them: a battery run in the pinned worktree dirtied five tracked files | EVIDENCE | program | S | none | results written under derived/ or a ledger table; rule-7 dirtiness cannot recur
MNE-38 | Bind the service on both address families or document 127.0.0.1 everywhere: "localhost" costs ~2 s per call on M1 (::1 tried first) | ENGINE | program | S | none | measured latency under 0.2 s via the documented URL, skill text updated
