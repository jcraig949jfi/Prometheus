# Salvage worker report: scope 6, infrastructure

Deposited by Dionysus[m1-3815a3b9] on 2026-10-01. Extracted by script
(process/deposit_worker_reports.py) from the coordinator's session transcript:
the worker's final message, recorded 2026-10-01T15:32:49.353Z. The text is the worker's,
unchanged except that XML escapes from the notification wrapper are undone
and trailing whitespace is stripped.

Brief: roles/Dionysus/prompts/2026-10-01_salvage_workers/00_COMMON.md and
06_SCOPE_infrastructure.md. Worker model: opus, read-only.
Worker usage as reported by the harness: 610,969 tokens, 222 tool uses, about
36.3 minutes (totals for the worker, all messages).

This is a worker's fact sheet. Its claims are the worker's, graded by its own
VERIFIED BY ME lines. Where SALVAGE_MATRIX.md relies on one, it says so.

----------------------------------------------------------------------

I have characterized the search-integrity issue (counts unchanged under the corrected pattern; a few name-only listings; one case-sensitivity gap; directory-scoped exclusions unreliable on this git build). I'll include that in SURPRISES as instructed. Here is the report.

===BEGIN REPORT===
Salvage fact-finding, scope 6: execution, provenance and institutional infrastructure
Worker: read-only, worktree dionysus-base-role. HEAD at start e3d7c7034; HEAD at end 36924629d. Dionysus committed two P1 prototype commits during the run. No git writes, no DB connections, no service probes.
Read first: REQUIREMENTS.md (section 1 and the named areas), RSE_ARCHITECTURE.md sections 1 to 13, ixion REPORT.md sections 0-7 and A-G, inference_dependency_map.md, dossiers (Odysseus, Daedalus, Vivarium, Bellerophon, Nestor, Mnemosyne, Aporia, Atlas/Achilles via REPORT, Pronoia, Hermes, Metis, Alethelia, Cyclops, Cosmos), engine_index records.
Legend: Y = yes, P = partial, N = no. "Coverage" means the PROV-01 field list: code commit, configuration hash, seeds, component versions, host, row hashes, verdict with ruler hash, cost meters.

----------------------------------------------------------------------
COMPONENT: Agent Fabric v0.2 (store, worker, executors, leases, lease_compat, claude sandbox, promexec)
PATHS: fabric/schema.sql, fabric/store.py, fabric/worker.py, fabric/executors.py, fabric/lease_compat.py, fabric/promexec/, fabric/tests/
OWNER / DATES: Odysseus. 9ff7dd967 2026-09-28 to b36c5a8e4 2026-09-30, 24 commits. The store is live on M1 Postgres. Workers have only ever run on ubu001/ubu002. Last task 2026-09-30, from Ixion's DB read; I did not check it.
WHAT IT REALLY DOES: It is a Postgres job queue.
- Enforced by the DB: one running attempt per task and one unreleased lease per resource (partial unique indexes), idempotent submit, expiry on the DB clock.
- Enforced by code: a claim takes the task and all its leases in one SKIP LOCKED transaction; heartbeat fencing; the reaper requeues; terminal states are immutable.
- Workers run a repo script at a pinned SHA (no shell, env allow-list) or a sandboxed `claude -p`. The runtime, not the executor, uploads outputs as sha256 blobs.
- The fabric lease is the operator-ruled single authority, and the Ananke/Nestor CLIs are shims onto it.
- promexec exists as source only. It is not enabled.
SIZE: 55 files, 3,878 Python lines (store 586, worker 296, executors 204, lease_compat 91). 43 test functions in fabric/tests.
DEMONSTRATED CORRECTNESS:
- Pilot P1-P9 PASS with evidence JSON, including a recorded P1 FAIL before the isolation fix (fabric/README.md s9).
- A legacy-CLI vs fabric-attempt lease race always has exactly one winner (fabric/tests/test_lease_compat.py).
- The tests create throwaway schemas inside the canonical M1 cluster.
- Defects: 23 DEF-ODY rows (roles/Odysseus/fabric_pilot/DEFECTS.md), e.g. 003 model pin not honoured, 021 FIFO starvation, 023 Windows CLI break.
INTERFACE:
- Called as `python -m fabric submit|worker|lease ...` or through the Python API. Usable with no model session: yes (script executor).
- The worker is Linux-only: fabric/worker.py:18 imports fcntl, and executors.py:91 calls os.killpg.
- env_receipt fields: host, agent, instance, base_sha, worktree_head, executor, python/platform, probed package manifest + sha256, start/end, exit_code, killed, model_used, and for claude tasks num_turns, total_cost_usd, duration_ms.
- Coverage: commit Y, config N, seeds N, versions P, host Y, row hashes P (per file), verdict N, cost P (no CPU, no energy).
THROUGHPUT / SCALE: claim latency median 6.02 s / 8.42 s at 5 s polling (fabric/pilot/evidence/P2-crosshost.json). Rescue 37.3 s after SIGKILL (README s9).
COUPLING: imports evidence_wiki.ew.db (credentials from the tracked evidence_wiki/config.json or from env) and comms.identity. Depends on M1 Postgres. Each node needs a clone, the claude CLI and a token file.
FIT TO SLOT: single queue + lease (COMP-04); substrate for the runner.
- Meets: INF-01, PROV-05.
- Partial: COMP-02 (requeues, but has no checkpoint), COMP-05 (wall_s kill only), PROV-07/INF-03 (model and USD only), REPR-06.
- Fails: PROV-01, PROV-03 (artifacts live only in the DB), MEAS-11/ANTI-01 (one shared DB credential), ENRG-01.
MODIFICATION COST:
- M: Windows worker (file lock and process-group kill), CPU/GPU-hour caps, keep token counts, append-only trigger on events.
- L once the kernel gates are added (prereg-ancestor check, receipt validation before completion, batch export).
- Rebuild from scratch: L.
VERIFIED BY ME: schema, store, worker, executors, lease_compat, README, P2 JSON, test counts, dates. From the dossier without checking: DB counts, worker liveness, the defect rows.

----------------------------------------------------------------------
COMPONENT: SFE (Serendipity Foundry Engine): hash-chained ledger, prediction-before-observation, executors, verify_deploy
PATHS: SerendipityFoundry/SerendipityFoundryEngine/sfe/{events.py, runtime.py, store.py, release.py, executors.py}, .../serve.py, .../deploy/verify_deploy.py, .../deploy/DEPLOYED_BUILD.json
OWNER / DATES: Daedalus (silent since 09-18). d332658cf 2026-09-01 to 9cfcd3779 2026-09-18, 98 commits. Production is on M2; the M1 pin is disabled. The M2 service was hung on 2026-09-24 (roles/Vivarium/receipts/INCIDENT_2026-09-24_M2_HOST_EXHAUSTION.md). I did not probe it.
WHAT IT REALLY DOES:
- A FastAPI service over one SQLite file (WAL, BEGIN IMMEDIATE, one writer at a time).
- Each state change appends an event in the same transaction to a per-world sha256 chain over canonical JSON. The chained fields include a float timestamp. verify_world recomputes the chain.
- Predictions are sealed with a content hash and an event sequence number.
- commit_experiment seals spec_hash and the engine source hash. Only predictions with created_seq < committed_seq count as prospective.
- The outcome (FALSIFIED / SURVIVED / INCONCLUSIVE) is supplied by the client.
- verify_deploy.py checks that the served build equals the pinned, LF-normalised file hashes.
SIZE: sfe/ 9,423 lines (runtime 5,125). 436 test functions in 32 files, each on a temporary SQLite. deploy/ has 154 files; verify_deploy.py is 151 lines.
DEMONSTRATED CORRECTNESS: a G1 run of 15,408 s with 0 5xx (e7a699099). Defects at HEAD that I confirmed in code:
- evidence_class ignores config_match (runtime.py:2435-2452).
- Observation content is outside the chain; only outcome, class and prospective are chained.
- Budget enforcement defaults to "measured" (runtime.py:1562, 2810).
- science-profile defaults to warn (serve.py:46-47).
INTERFACE: REST /v2 and a client. Usable without a model: yes. Uses floats. Worlds fork by reference.
- Fields: spec_hash, engine_source_hash, executed_config_hash, measurement_identity_hash, result_hash, the entry_hash chain, and a cost vector {resource, quantity, unit, method, scope}.
- Coverage: commit P, config Y, seeds P, versions P, host N, row hashes Y, verdict N (client verdict), cost Y (supplied by the caller).
THROUGHPUT / SCALE: ~400-900 ledger events/s, ~1.07 KB/event, single writer (docs/campaign_6/SFE_C6_OBSERVATORY_REVIEW_2026-09-18.md s1).
COUPLING: a standalone package. Ledgers, TLS keys and the launcher are off-repo host files. Consumers: Vivarium, Archaeon, PEW fossil anchors.
FIT TO SLOT: ledger.
- Partial: PROV-04, PROV-06 (inside the engine, not in git), REPR-05 (warn by default), MEAS-06 (a measurements registry with implementation_hash, but no STALE marking).
- Fails: PROV-03, PROV-08, MEAS-11, COMP-05, throughput.
MODIFICATION COST:
- As the canonical ledger: XL (the SQLite-to-Postgres move ruled 09-18 was never done, and the verdict model must change).
- S to extract the events.py chain (211 lines), the prediction-window rule, the release.py hash and the verify_deploy pattern.
- Rebuilding the chain itself: S.
VERIFIED BY ME: events.py, ids.py, release.py, the commit/observation/cost code, the schema, serve flags, DEPLOYED_BUILD.json, the C6 numbers. Host and liveness facts are from the dossier.

----------------------------------------------------------------------
COMPONENT: Vivarium data plane (Postgres queue, blind executor, sealed spec, errata, attempts, outbox)
PATHS: vivarium/migrations/001-010, vivarium/viv/{queue.py, loop.py, runner.py, spec.py, deadman.py, outbox.py, attempts.py}, vivarium/tests/test_blinding.py
OWNER / DATES: Vivarium. Code 8b940a165 2026-09-05 to 1db58c264 2026-09-17 (77 commits); last seat commit 8c5a1a23b 2026-09-24. Consumer parked 09-19 and dead-man parked 09-23 (dossier). Runs on M2; the viv schema is on M1.
WHAT IT REALLY DOES: a register of requested experiments, run one at a time against SFE.
- Enforced in the DB by 12 triggers: one active row globally, legal transitions only, frozen terminal rows, an immutable sealed request, append-only events/errata/receipts, and an ordered outbox whose rows are never deleted.
- Provenance stays outside spec_hash. The runner sees only id, spec and hash (the blinding test).
- The spec hash is read back from the SFE ledger before a claim.
- Contamination is quarantined by an enumerated list (view register_clean).
- Attempts and steps are keyed by the design digest so they can be replayed. The dead-man auto-releases stranded rows, bounded at 3 per rolling 24 h.
SIZE: viv/ 13,393 lines. 590 test functions in 49 files.
DEMONSTRATED CORRECTNESS: canary run 11 passed 35/35 with zero human commands (1db58c264). Defects:
- ~85,727 phantom SFE experiments.
- 246 test rows in production.
- The README contradicts migration 010.
- F1/F2 were designed but not built.
- The headers of migrations 006/009 still say DRAFT.
INTERFACE: `python -m viv.cli`. The outcome is the requester's single-field rule. Usable without a model: yes.
- Row fields: spec_hash, created_by, source_reason/evidence, status, claimed_by, sfe_experiment_id, pew_reference, result_summary. Attempt fields: design_digest, bundle_hash, termination, receipt_digest.
- Coverage: commit P, config Y, seeds Y, versions P, host P, row hashes Y, verdict N, cost P.
THROUGHPUT / SCALE: "The science is 0.1s. The row is 95-193s. 98%+ is SFE round-trips" (roles/Vivarium/NOTES_POSTMORTEM_2026-09-08_to_09-11.md:157).
COUPLING: SFE REST and PEW REST on M2; M1 Postgres via the ew credential path; comms.identity; herakles/proteus libraries; M2 scheduled tasks.
FIT TO SLOT: source of patterns for the queue and the ledger.
- Meets: PROV-04 (in the DB), PROV-05, INF-01.
- Partial: REPR-05, COMP-02.
- Fails: COMP-04 throughput (one global slot), PROV-01, MEAS-06, PROV-03.
MODIFICATION COST:
- Keep as is: XL (it is bound to SFE).
- M to port its triggers (sealed request, errata, attempts/steps, outbox) onto the chosen store.
- Rebuild: covered by the fabric work.
VERIFIED BY ME: migrations 001/003/006/009, trigger count, db.py identity path (credentials not opened), blinding test docstring, dead-man bound, counts, dates.

----------------------------------------------------------------------
COMPONENT: prometheus/toolbox receipts and admission (provenance side only)
PATHS: prometheus/toolbox/receipt.py, prometheus/toolbox/admission.py, prometheus/toolbox/backends/local.py, prometheus/toolbox/tests/
OWNER / DATES: Bellerophon. 4c0435544 2026-09-18 to 2026-09-19, 102 commits. Dormant since then.
WHAT IT REALLY DOES:
- receipt.v1 is one record per run with required-key validation. receipt_id = the first 24 hex characters of the sha256 of the canonical body.
- Each receipt carries prev_receipt_id, forming a chain. Records go to append-only JSONL, flushed per record.
- A strict reader names truncation, edits and chain breaks. A forensic scan never raises.
- The engineering and science ledgers must be disjoint. The build block is an LF-normalised hash of the kernel modules.
- execute() refuses a resume that names a different experiment, and enforces budget.wall_s.
- Admission returns ADMITTED or UNAVAILABLE from 8 machine checks, with "no approver".
SIZE: 112 files, 5,962 non-test lines (receipt 188, admission 395, local 883). 231 test functions.
DEMONSTRATED CORRECTNESS: reported, not rerun by me:
- the suite: 1,421 passed, 6 skipped;
- mutants caught: 85/85, later 93;
- cross-platform replay 87/87 (Windows vs WSL).
C70: a wrong twin once passed an action-blind admission probe; repaired.
INTERFACE: Python API. Usable without a model: yes.
- Fields: schema, receipt_id, experiment_id, experiment_digest, arm, sweep_point, seed, status, components, capabilities, replay_class, trace_hashes, events_total, engineering (wall_s, cpu_s, ticks), science, accounting, host, build, started/finished_utc, prev_receipt_id.
- Coverage: commit N, config Y, seeds Y, versions Y, host Y, row hashes P, verdict N, cost P (no energy, no tokens).
THROUGHPUT / SCALE: none recorded in the files I opened.
COUPLING: stdlib, with optional numpy and redis. The only code importer is prometheus/atlas_bee (8 files).
FIT TO SLOT: receipt schema and ledger file format; admission as a pattern for the qualification gate.
- Meets: PROV-02, INF-01.
- Partial: PROV-01, PROV-04, COMP-02, COMP-05, REPR-01, MEAS-02.
- Fails: MEAS-06, ENRG-01, INF-03.
MODIFICATION COST: S-M to add code commit, a verdict block with ruler hash, energy and token fields, and validation-gated completion. Rebuilding receipt.py: S.
VERIFIED BY ME: all of receipt.py, the admission docstring, the budget/resume code, counts, importers, dates.

----------------------------------------------------------------------
COMPONENT: primordial RowWriter (commit-on-write rows)
PATHS: primordial/fabric/rows.py, primordial/tests/test_rows.py
OWNER / DATES: Nestor lanes. 2d3122a5c and 7fa40eec9, both 2026-09-14. There are 1,688 "<lane>[<tag>]: rows" commits across all refs, from 2026-09-14 to 2026-09-18 (`git log --all --grep`), and none after that.
WHAT IT REALLY DOES:
- Appends one JSON line per evaluated item, with status record/dev/aborted/timeout/cheat/control, exp_id and a float ts. Flushes every line.
- Then runs `git add` and `git commit --only` on the file at most every 60 s, and on close or SIGTERM.
- Refuses to start without PM_TAG. Leaves a live-writer marker so the push helper avoids rebasing under it.
- Guarantee: a death loses at most one commit interval of rows. Failure rows are kept.
SIZE: 245 lines, 5 tests. Imported by 60 .py files under primordial/ and roles/Nestor/.
DEMONSTRATED CORRECTNESS: its own tests only. It races any other git write in the same worktree (Nestor dossier).
INTERFACE: Python context manager and a CLI. Usable without a model: yes. A row is the caller's dict plus status, exp_id and ts. Coverage: commit P (the rows commit, not the code), all other fields N.
THROUGHPUT / SCALE: not recorded.
COUPLING: the git CLI, psutil, and the PM_TAG and PM_LANE environment variables.
FIT TO SLOT: "one writer for results". Fails PROV-08 (its check is "no campaign code calls git") and PROV-01.
MODIFICATION COST: retire, S. Rebuilding it as a runner-side content-addressed writer with one batch committer: S.
VERIFIED BY ME: all of rows.py, tests, importer count, commit count.

----------------------------------------------------------------------
COMPONENT: primordial Redis GPU lease and CPU-token broker
PATHS: primordial/bus/bus.py (pm:gpu:lease), primordial/fabric/broker.py, primordial/fabric/worker.py
OWNER / DATES: Nestor lanes. Last changed in 97a1c791f, 2026-09-16. Runtime state unknown.
WHAT IT REALLY DOES: Redis keys with a TTL.
- One GPU lease key: SET NX PX, compare-and-set renew/release in Lua, takeover once `until` has passed.
- CPU broker: k_star token slots from a capacity probe, a FIFO waiter set ordered by original queue time, stale waiters pruned after 10 s.
- The worker kills a job once the child's CPU time passes ttl_cpu_s. This is the only enforced CPU cap I found anywhere.
- Redis state is ephemeral; the durable record is committed JSONL mirrors.
SIZE: broker 142 + bus 438 + worker 930 lines. 20 tests across test_o5_gpu_lease.py, test_r5_f5_capacity_broker.py and test_r8_p_g3_scheduling.py.
DEMONSTRATED CORRECTNESS: tests only.
INTERFACE: Python and Redis Lua. Usable without a model: yes. Lease record: holder, lane, tag, purpose, since, until, token. No receipt.
THROUGHPUT / SCALE: not recorded.
COUPLING: a Redis/FalkorDB container on a local port of M1 (dossier), the PM_* environment variables, RowWriter.
FIT TO SLOT: lease. Fails COMP-04 (it is a second mechanism) and PROV-03 (state only in Redis). Its CPU-time kill is a usable COMP-05 pattern.
MODIFICATION COST: retire, S (the legacy CLIs already left it, per fabric/README.md s5). Porting the CPU-time kill into fabric: S.
VERIFIED BY ME: the broker and bus code, worker docstring, test counts, dates.

----------------------------------------------------------------------
COMPONENT: comms (messages, receipts, task_queue, manifest.py, identity.py)
PATHS: comms/schema.sql, comms/api.py, comms/identity.py, comms/manifest.py, comms/environments.json, comms/tests/
OWNER / DATES: shared (Hermes built identity.py). 7466bd6ac 2026-09-11 to 8216dd3de 2026-09-17, 7 commits. Live on M1: 1,239 messages per Ixion; I did not query.
WHAT IT REALLY DOES:
- A Postgres message board: messages with a closed kind vocabulary and sha256 over subject+body, per-agent and per-instance receipts, a per-agent task_queue of message ids, and a self-declared agents.model. No trigger blocks UPDATE or DELETE.
- identity.py refuses a connection whose system_identifier or db name differs from comms/environments.json. It fails closed, including for an unknown environment.
- manifest.py writes a per-directory MANIFEST of sha256 over LF-normalised bytes (binaries are hashed unchanged).
SIZE: 1,494 lines including tests. 31 tests (identity 18, manifest 2).
DEMONSTRATED CORRECTNESS: the identity tests build a structurally identical database and show it is refused. The manifest test shows CRLF and LF copies hash equal. A residual limit is stated in the code: a physical clone keeps the system_identifier.
INTERFACE: `python -m comms`, and a manifest write/verify CLI that exits 1 on mismatch. Usable without a model: yes. It is not a receipt schema.
THROUGHPUT / SCALE: not recorded.
COUPLING: credentials come through ew/db.py from the tracked config. Imported by fabric, atlas, viv and ew.
FIT TO SLOT:
- manifest.py meets PROV-02 as is. It is the "existing manifest tool" PROV-02's check names, and the CRLF/LF fixture already exists.
- identity.py helps PROV-03 store custody.
- The messaging has no slot (INF-07).
MODIFICATION COST: keep manifest.py and identity.py, S. Freeze messages and task_queue as an archive, S. Rebuilding the manifest tool: S.
VERIFIED BY ME: schema, the api function list, identity.py, manifest.py and its test, environments.json.

----------------------------------------------------------------------
COMPONENT: evidence_wiki/ew (store gates, db.py connector, campaign reader, projections, search)
PATHS: evidence_wiki/ew/{store.py, db.py, campaign_ingest.py, projections.py, search.py}, evidence_wiki/migrations/001-015
OWNER / DATES: Mnemosyne (silent since 09-18). c711c5bf6 2026-09-01 to 0d448387e 2026-09-18, 70 commits. The PEW service on M2 has been down since 09-23 (dossier). db.py is still live as everyone's connector.
WHAT IT REALLY DOES:
- store.py is the only write path. It applies idempotency keys, vocabulary refusal, quarantine of derived URIs and content-addressed ids.
- It has no update or delete function, but no DB trigger enforces append-only: there are 0 triggers in the 15 migrations.
- db.py: a pooled connection with credentials taken from env, then config.local.json, then the tracked config.json, plus the identity guard.
- campaign_ingest reads Archaeon campaigns 1-5 at a given commit into content-addressed rows that carry commit, path, line, blob and reader version.
- Projections are derived tables with a rebuild digest.
- Search is BM25 plus a local MiniLM embedding model. No LLM.
SIZE: 20 modules, 6,278 lines. 45 tests in 20 files, plus 10 integration scripts.
DEMONSTRATED CORRECTNESS: 6,077 write_log rows with reasons; rebuild-digest equality reported 3 times (dossier). Defects:
- register_packet hashes raw host bytes (evidence_wiki/ew/store.py:87).
- Migration 015 was applied from a dirty tree.
- The batteries rewrite tracked receipts.
INTERFACE: REST, client and direct SQL. Usable without a model: yes.
- campaign_observations fields: source_commit/path/line/blob_sha, producer_row_digest, reader_version, seed, engine_source_hash, measured.
- Coverage: commit Y, config P, seeds Y, versions P, host N, row hashes Y, verdict N, cost N.
THROUGHPUT / SCALE: not recorded in the files I opened.
COUPLING: M1 Postgres, credentials in the tracked config (R-1 open), comms.identity, the HF model cache, the M2 service.
FIT TO SLOT: derived index.
- Meets: PROV-05.
- Partial: PROV-04.
- Fails: PROV-01 (the reader is one adapter per producer), PROV-02, MEAS-11.
MODIFICATION COST:
- Keep db.py but move the credentials out of git: S.
- Extract the derived-view quarantine and the rebuild digest: S.
- Retire the service: S.
- A one-schema reader: M.
VERIFIED BY ME: the store gates, db.py logic (not the config), the ingest header, migration 014 columns, projections/search headers, counts. Row counts and service state are from the dossier.

----------------------------------------------------------------------
COMPONENT: atlas (schema, migrations, harvesters, comb rules, report)
PATHS: atlas/sql/001-013, atlas/harvest/*.py (13 harvesters), atlas/comb.py, atlas/report.py, atlas/classify.py, atlas/policy.py
OWNER / DATES: Atlas. 61c3985fc 2026-09-19 to 244ef7691 2026-09-30, 16 commits. Run by hand; last pass 09-30 (Ixion). No schedule.
WHAT IT REALLY DOES:
- Versioned harvesters read git blobs, SQLite ledgers (read-only) and other schemas.
- Each row cites a harvest_run (harvester, version, atlas_sha, machine, instance, source ref/sha, counts).
- Each fact links through fact_evidence to a source (uri, commit, blob, path, lines, file_sha256, visibility including EXPECTED:<host>).
- Facts are keyed by fact_key and updated in place, not appended.
- comb.py runs 13 SQL rules that write OPEN signals.
- report.py writes an ASCII report 80 columns wide.
- harvest/cosmos.py ingests only after a sha256 MANIFEST check and fails closed.
SIZE: 4,505 non-test lines. 58 tests.
DEMONSTRATED CORRECTNESS: parsed counts matched the source in every sample. Defects: completed maps to POSITIVE; field_conflict has never fired; 31% of commits are unattributed; lag of 8.58 days. All from Ixion.
INTERFACE: `python -m atlas` and SQL. Usable without a model: yes. Coverage: commit Y, config N, seeds N, versions Y, host Y, row hashes P, verdict N, cost N.
THROUGHPUT / SCALE: about 86 s for a full M1 pass (Ixion, from harvest_run rows).
COUPLING: ew.db, M1 Postgres, and M2 files reached by a separate session.
FIT TO SLOT: derived index. Provenance pointers are strong. Fails PROV-01 (one adapter per engine), INF-04 (no scheduler), and INF-01 for its model-authored layers. The cosmos import is the only existing example of a producer emitting in the index's own shape.
MODIFICATION COST: M to reduce it to harvest_run/source/fact with one harvester for the one receipt schema, run on a schedule. Rebuild: M.
VERIFIED BY ME: the DDL, comb rule ids, the report and cosmos headers, counts, dates.

----------------------------------------------------------------------
COMPONENT: achilles/census (rules, registry, render, run receipts)
PATHS: achilles/census/{run.py, build.py, classify.py, sources.py, render.py}, roles/Achilles/census/{registry/, runs/2026-10.jsonl}
OWNER / DATES: Achilles. One code commit, a797beabd, 2026-09-30. Runs every 6 h on ELSA: 4 receipts on 2026-10-01 from 03:46:12Z to 10:35:00Z, all SUCCESS.
WHAT IT REALLY DOES:
- A deterministic rule cascade over git (all origin refs), comms, ew, agora, and a registry that a model wrote once.
- Writes fleet_state.json, index.html, email_census.json and FLEET_CENSUS.md, with source, time and confidence on each field.
- Runs from a pinned worktree, refuses the canonical checkout, and commits and pushes its outputs.
- On failure it keeps the previous page and posts once. It parks after 4 non-productive runs.
SIZE: 2,037 non-test lines. 26 tests.
DEMONSTRATED CORRECTNESS: tests. Ixion found 4 of 14 seat states wrong.
INTERFACE: `python -m achilles.census.run`. Usable without a model: yes.
- Receipt fields: run_id, started/finished_utc, host, code_root, code_sha, publish_root, status, base_sha, mode, commits_scanned, seats, entities, counts, anomalies, sources, productive.
- Coverage: commit Y, host Y, the rest N or not applicable.
THROUGHPUT / SCALE: a deep pass scanned 10,717 commits in 45 s (receipt 20261001T103000Z).
COUPLING: M1 DB; a scheduled task on ELSA under an interactive logon with the operator's git credential.
FIT TO SLOT: dashboard pattern. Partial HUM-02 and INF-04. Its inputs are seats, not receipts, so the census itself has no Phase 3 role.
MODIFICATION COST: extract the receipt, render and failure-banner code, S. Retire the census, S. Rebuild: S-M.
VERIFIED BY ME: run.py, the receipts file, counts, dates.

----------------------------------------------------------------------
COMPONENT: Reporting loop (intelligence_loop, portfolio_monitor, metis_portfolio, send_brief_email)
PATHS: scripts/intelligence_loop.py, scripts/portfolio_monitor.py, scripts/metis_portfolio.py, scripts/send_brief_email.py, scripts/orchestration_logging.py, docs/portfolio_brief.md
OWNER / DATES: the Pronoia/Hermes/Metis lineage. First commit 2026-05-13; last code commit 2026-09-30. Live on M4: newest auto commit a031e6f91 at 2026-10-01 12:14:57Z.
WHAT IT REALLY DOES:
- portfolio_monitor reads Agora heartbeats against a hard-coded EXPECTED_AGENTS roster.
- metis_portfolio is deterministic unless METIS_LLM=1 (metis_portfolio.py:449-461). It adds "parked threads" from engine/queues/*.jsonl.
- send_brief_email sends a plain-text + html email over SMTP and emits an email_dispatched event.
- The cadence is set by flags; 4 h is observed.
SIZE: 3,181 lines. No tests found.
DEMONSTRATED CORRECTNESS: none from tests. The 12:14Z brief lists "Hephaestus @ M3 ... No heartbeat for 178309min" as an action item.
INTERFACE: CLI flags. Usable without a model by default. Event fields: stage, summary, success, output_path, error, agent, cycle_id, duration. No payload hash and no code commit.
THROUGHPUT / SCALE: 0.3-0.5 s per brief (Pronoia dossier).
COUPLING: the M4 host, Agora Redis/Postgres, mail credentials in a gitignored .env on M4 only, git push from M4.
FIT TO SLOT: operator digest.
- Meets: INF-01.
- Partial: HUM-02 (generated by code, has a plain-text part).
- Fails: HUM-02's purpose (its inputs are heartbeats, not receipts) and INF-04.
MODIFICATION COST: keep the mailer (S; weekly delivery is a flag change). Retire the producers, S. Rebuild a digest from receipts: S.
VERIFIED BY ME: the headers, the deterministic switch, the parked-thread source, the MIME/SMTP lines, the latest brief, dates.

----------------------------------------------------------------------
COMPONENT: prometheus_llm (the intended single model-call point)
PATHS: prometheus_llm/{client.py, types.py, registry.py, cli.py}, prometheus_llm/tests/test_offline.py
OWNER / DATES: shared. Every commit is dated 2026-08-22.
WHAT IT REALLY DOES:
- One client for openai-compatible, gemini, anthropic and `claude -p` providers, with fallback, retries and auto-expansion of the token budget when output comes back empty.
- The audit log is written only if PROMETHEUS_LLM_LOG is set (client.py:49-66). No tracked code sets it.
- Logged per call: ok, text, reasoning, provider, model, model_served, upstream_provider, finish_reason, empty_content, prompt/completion/total tokens, cost, latency_s, attempts, status, error, ts, prompt_sha1 (SHA-1 over the first 20,000 characters of the messages JSON), prompt_chars, and the prompt itself only if a second flag is set.
- Not logged: temperature, max_tokens, the fallback chain, the fork type.
- The claude_cli path returns no tokens and no cost.
SIZE: 896 lines. 32 offline tests.
INTERFACE: complete(), complete_json(), council(), and a CLI.
THROUGHPUT / SCALE: latencies from the README, 2026-08-22: groq 0.55 s, nvidia 0.45 s, claude_cli 4.8 s.
COUPLING: requests. Keys come from the repo-root keys.py, which is gitignored and local to each host.
FIT TO SLOT: token meter.
- Partial: INF-03, PROV-07, INF-06.
- Fails: INF-02 (no fork-type field).
- In practice it is not the single choke point: 5 code importers, against 66 .py files that call providers directly.
MODIFICATION COST: M. Make the log default-on and append-only with a sha256 prompt hash, the steering fields and the fork type; capture claude JSON usage; route or ban the bypassing call sites. Rebuild: S-M.
VERIFIED BY ME: the audit and adapter code, types.py, README, the importer and bypass searches.

----------------------------------------------------------------------
COMPONENT: Cosmos holdout broker (code only)
PATHS: prometheus/cosmos/broker.py, prometheus/cosmos/audit.py, prometheus/cosmos/hashing.py, prometheus/cosmos/store.py
OWNER / DATES: Cosmos. broker.py commits 800072c1e and 7c9e0d58f, both 2026-09-23. Holdouts D/E/F were spent by 09-23 (dossier).
WHAT IT REALLY DOES:
- Before revealing anything it checks four things: the law is FROZEN, its freeze hash recomputes, the sealed spec's sha256 equals the preregistered commitment, and the family source still hashes as recorded.
- It writes a receipt for the prediction hash, then runs the sealed worlds in a subprocess with COSMOS_BROKER=1, then writes a receipt for the reveal.
- audit.py re-checks R1-R6: chain, freeze, ordering, seals, prefix.
- So the guarantee is ordering inside a hash-chained receipt file. The sealed files are tracked in the repository and readable by any process, and there is no access log.
SIZE: broker 262, audit 100, store 117 lines. Its test file has "holdout" in its name; not opened.
DEMONSTRATED CORRECTNESS: the audit checks; G5E PASS is reported (Ixion engine index). Weakness R4 is stated in audit.py itself.
INTERFACE: adjudicate(), intervene(), intervene_fresh(). Usable without a model: yes. Receipts: holdout_open, holdout_predictions, holdout_revealed, prescriptions.
THROUGHPUT / SCALE: 720 sealed-world runs (Tantalus dossier, unverified).
COUPLING: numpy, the Cosmos miner; its store is on M2.
FIT TO SLOT: sealed-world broker. Partial PROV-10. Fails PROV-10's check, a log showing no access before reveal.
MODIFICATION COST: M (move the sealed material out of the repo or encrypt it, add a read log, add a process boundary). Rebuild: M.
VERIFIED BY ME: broker.py, the audit docstring, hashing.py, the store header.

----------------------------------------------------------------------
COMPONENT: archaeon/workspace.py (canonical-checkout guard)
PATHS: archaeon/workspace.py, archaeon/tests/test_workspace.py
OWNER / DATES: Archaeon. 2026-09-11 to 2026-09-16.
WHAT IT REALLY DOES: refuses work in the main worktree (git-dir equal to common-dir) and fails closed if git does not answer. receipt() returns base_sha, branch, worktree_path, dirty (untracked files ignored), main_worktree, workspace_known, repo_id. It records a dirty tree but does not refuse one.
SIZE: 103 lines, 6 tests. Imported by 31 .py files outside archaeon/.
DEMONSTRATED CORRECTNESS: its tests; the ARCH-52 fail-closed fix.
INTERFACE: assert_not_canonical(). No model involved.
THROUGHPUT / SCALE: not applicable.
COUPLING: needs git on PATH.
FIT TO SLOT: a runner precondition. Partial REPR-06: it records the tree state but does not refuse, and it ignores untracked files.
MODIFICATION COST: S (refuse dirty trees, including untracked files). Rebuild: S.
VERIFIED BY ME: the whole file, the tests, the importer count.

----------------------------------------------------------------------
COMPONENT: Alethelia v0.1 (truthful reporter)
PATHS: agents/alethelia/alethelia.py, agents/alethelia/test_alethelia.py, stations/REPORT_latest.{md,json}
OWNER / DATES: Alethelia, which has no host. 2026-08-20 to 2026-09-11. Dormant.
WHAT IT REALLY DOES:
- Every field is a value with the query that produced it, or UNKNOWN with a reason.
- 7 rules, each FIRED, CLEAR or INDETERMINATE. The banner reads calm only with nothing fired and nothing indeterminate. Unreachable sources produce a DEGRADED banner.
- Refuses to run from the canonical checkout.
SIZE: 444 lines. Self-test script with 9 checks (positive, negative, cheat, indeterminate, guard); no pytest functions.
DEMONSTRATED CORRECTNESS: the controls in the self-test.
INTERFACE: a CLI. No model involved.
THROUGHPUT / SCALE: not recorded.
COUPLING: agora heartbeats, git, engine/queues, comms on M1.
FIT TO SLOT: a renderer for the digest and alarms (HUM-02, INF-04). Its inputs are institutional.
MODIFICATION COST: S-M to repoint the fields at receipts. Rebuild: S.
VERIFIED BY ME: docstring, rule count, test file.

----------------------------------------------------------------------
COMPONENT: productive_liveness.py and null_bound.py
PATHS: roles/Pronoia/science/productive_liveness.py (+ test), roles/Atalanta/reference/null_bound.py (+ test)
OWNER / DATES: Pronoia and Atalanta. Both 2026-09-11. productive_liveness is imported by scripts/intelligence_loop.py, which is live on M4. null_bound is imported only by its test.
WHAT IT REALLY DOES:
- derive_health() is a pure function of injected timestamps, so a dead work thread degrades on the clock alone.
- null_bound parks a loop after a declared bound of ticks that are non-productive by a declared signal (not by artifacts written), and names an accountable seat.
SIZE: 227 lines with 23 tests; 126 lines with 9 tests (including a cheat control).
DEMONSTRATED CORRECTNESS: their tests.
INTERFACE: pure Python functions. No model involved.
THROUGHPUT / SCALE: not applicable.
COUPLING: none.
FIT TO SLOT: detector responders for INF-04. Partial.
MODIFICATION COST: S. Rebuild: S.
VERIFIED BY ME: the docstrings, tests, importers.

----------------------------------------------------------------------
COMPONENT: Metis compose.py (cheapest partitioning discriminator)
PATHS: roles/Metis/season1/specimen/compose.py, roles/Metis/season1/specimen/test_adversarial.py
OWNER / DATES: Metis. 2026-09-13. Imported only by its own test.
WHAT IT REALLY DOES: set operations over a declared evidence bundle. It groups dependent evidence, applies vetoes (instrument suspect, stale, base-rate confounded), and returns the cheapest discriminator available at the cutoff that splits the surviving explanations. No scalar score, no model.
SIZE: 442 lines. 13 adversarial tests.
DEMONSTRATED CORRECTNESS: its tests. 5 retrospective episodes are reported in the dossier, not rerun.
INTERFACE: compose(bundle) returns a Result. Deterministic.
THROUGHPUT / SCALE: not applicable.
COUPLING: none.
FIT TO SLOT: no kernel slot, but it is INF-05 in kind (pick the cheapest experiment that splits the named rivals). Missing: bundles derived from receipts.
MODIFICATION COST: S-M. Rebuild: S-M.
VERIFIED BY ME: the docstring and constants, the tests, the importer search.

----------------------------------------------------------------------
COMPONENT: Cyclops prepost_check.py
PATHS: programs/selective_irreversibility/probes/prepost_check.py (+ test)
OWNER / DATES: Cyclops/Aporia. 2026-09-25.
WHAT IT REALLY DOES: a 61-line CLI that refuses comms posts to "*" or to seats on DO_NOT_BRIEF.txt, and flags fixed substrings in the body. Advisory only: the caller must choose to run it.
SIZE: 61 lines. 6 tests, including one on a real message.
DEMONSTRATED CORRECTNESS: its tests.
INTERFACE: a CLI; exit 0 means clear, 2 means refused. No model involved.
THROUGHPUT / SCALE: not applicable.
COUPLING: DO_NOT_BRIEF.txt.
FIT TO SLOT: none. At most a leak-check pattern for WLD-06.
MODIFICATION COST: retire, S. Rebuild: S.
VERIFIED BY ME: the whole file and the test count.

----------------------------------------------------------------------
TOKEN, MODEL-IDENTITY AND ENERGY RECORDING (whole scope)

Token use and cost:
- Fabric claude attempts record the model ids actually used and total_cost_usd, num_turns and duration_ms (fabric/executors.py:144-147). These land in attempts.env_receipt and the env_receipt.json artifact. The per-token counts in the CLI's JSON output are discarded.
- prometheus_llm logs tokens and cost per call, but only when PROMETHEUS_LLM_LOG is set, which nothing tracked does.
- hephaestus/xpol_2026/replay.py records input, cache, output and thinking tokens and the list cost, for its own calls only.
- comms.agents.model is self-declared.
- SFE cost events accept any resource, but no producer records tokens by default.

Model identity per call: fabric attempts.model, and prometheus_llm's model, model_served and upstream_provider when it is logging.

Energy:
- Nothing records energy on M1, M2, ELSA or the ubu machines.
- scripts/machine_probe.py samples GPU utilisation and memory, not power.
- Aether/runpod/prometheus_gpu/dryrun.py samples nvidia-smi power.draw, on rented pods only.
- Searched with: git grep for power.draw|kwh|joule|watt|rapl in *.py.

----------------------------------------------------------------------
A. HOSTS

M1 SKULLPORT
- Windows 11 (prometheus_math/COST_MODEL_CALIBRATION_2026-05-04.md:28).
- CPU recorded two ways: "Ryzen 7 5700X3D (AMD64 Family 25 Model 97 Stepping 2)" (same file:27), and "Ryzen 7 7700X, 8 cores / 16 threads, 32 GB, RTX 5060 Ti 16 GB" (docs/phase3/design/FABLE-5.1/REQUIREMENTS.md:42-43).
- RTX 5060 Ti 16GB (aporia/docs/germline_infrastructure_2026-08-17.md:21).
- 192.168.1.202, the canonical Postgres (comms/environments.json).
- Earlier address 192.168.1.176 (pivot/machine_probe_setup_prompts_2026-05-24.md:16).
- Roles: canonical Postgres, comms, the fabric store, the M1 SFE ledger pin (SerendipityFoundry/SerendipityFoundryEngine/deploy/DEPLOYED_BUILD.json), NPE (atlas/registry.json).

M2 SPECTREX5
- 192.168.1.191 (atlas/registry.json).
- "i7-14700F, 20 cores, RTX 5060 Ti 16GB" (apollo/archive/v2-beta/launch_beta.bat:7); "28 cores" (germline doc:26).
- 32,557 MB physical (roles/Vivarium/receipts/INCIDENT_2026-09-24_M2_HOST_EXHAUSTION.md:31).
- Roles: SFE :8811, Vivarium, Archaeon, the PEW service (atlas/registry.json); a quarantined Postgres fork (comms/environments.json).

M3 GANDALF
- "GTX 1070 8 GB" (roles/Hephaestus/FORGE_NEXT_LEVEL_STRATEGY_2026-06-27.md:45).
- "a 2008 i7-920 without AVX" (roles/Nyx/journal/2026-09-19.md:51).
- Roles: Nyx, Techne, Harmonia F (atlas/registry.json).

M4 harry1
- "M4 has 8 cores" (roles/Aphrodite/science/arc3/ARC3_WORKER_BRIEFING.md:44).
- Roles: monitoring and reporting (germline doc:33), the intelligence loop (scripts/intelligence_loop.py:5), Aphrodite.
- Host label harry1 (roles/Achilles/CLASSIFICATION_RULES.md:72).

ELSA
- "Windows 10 Home 19045, 8 logical CPUs, 192.168.1.163" (roles/Achilles/RESPONSIBILITIES.md:95).
- Role: the census scheduled task (same file).

ubu001
- ThinkPad X1 Carbon 5th gen, 4 threads, 8 GB (7.0 GiB usable), 238.5 GB NVMe, Ubuntu 26.04.1, 192.168.1.218 over Wi-Fi (infra/ubuntu_nodes/ubuntu_server_machines.md:8, 51-52).
- "i5-7300U ... 2 cores / 4 threads" (roles/Odysseus/ABOUT.md:35).
- Role: fabric workers.

ubu002
- Same model, 192.168.1.219, battery health 34% (ubuntu_server_machines.md:9, 78).
- Roles: Artemis (roles/Odysseus/RESPONSIBILITIES.md:98), a fabric worker.

BUCKKEEP
- "an i7-1260P laptop ... Windows 11" (Aether/AETHER_ENGINE_CARD.md:197-199); "a throttling laptop" (Aether/pivot/AETHER_REVIEW_2026-09-27.md:493).
- Role: the Aether seat; holds the RunPod key.

DESKTOP-RUAPVAI
- "Windows 11, 4 logical CPUs, 192.168.1.160" (roles/Theseus/RESPONSIBILITIES.md:98).
- Role: Theseus.

Rented GPUs
- RunPod "NVIDIA A40 48 GB, SECURE cloud, $0.49/hr" (Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md:36).
- RunPod pods also used as disposable Linux CPU executors (Aether/AETH-03/RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md:50).

----------------------------------------------------------------------
B. ONE QUEUE, ONE LEDGER, ONE LEASE (least work for deterministic campaigns on M1)

Queue: fabric tasks and attempts.
- Why: its invariants are already in the DB; tasks carry campaign_id, experiment_id and base_sha; the store is on M1; the CLI works on Windows (DEF-ODY-023 fixed).
- Work, M: a Windows worker (replace the fcntl lock and os.killpg, or use WSL, which I did not verify exists on M1); per-campaign CPU and GPU-hour caps (port primordial's CPU-time kill); make submit the only way campaign code can start work.

Lease: fabric leases.
- Why: the lease is taken in the same transaction as the claim, it is token-fenced, and it is already the operator-ruled authority.
- Work, S: cut roles/Aphrodite/leases/lease.py over to it; add an authorisation or campaign id to each lease.

Ledger: toolbox receipt.v1, extended to PROV-01, stored as fabric sha256 blobs, with an append-only trigger on fabric.events and one batch exporter to git that writes hashed pointers.
- Work, M.
- SFE's chain is the stronger tamper-evidence design, but making SFE canonical is XL.

Cost to retire the others:

| mechanism | cost | main work |
|---|---|---|
| SFE ledger + work_items | M | Preserve two off-repo SQLite ledgers with hashes and a custody note. Stop the M2 service. PEW and Atlas keep SFE ids as history. Retiring SFE also retires Vivarium. |
| Vivarium queue | S | Dump it with a hashed pointer; disable the M2 tasks. |
| primordial Redis queue, leases, CPU tokens and RowWriter | S | No RowWriter commit since 09-18. M only if primordial runs must stay re-runnable. |
| comms task_queue | S | Freeze it. |
| agora research_queue and gpu_reservations (DDL in scripts/agora_persist.py) | S | Freeze them. |
| Aphrodite host-file leases | S | Cut over to the fabric lease. |
| engine/queues/*.jsonl (Aporia's August loop) | S | Still read by the M4 brief; repoint the brief first. |
| archaeon file queues | not examined | |

----------------------------------------------------------------------
C. A WEEKLY OPERATOR DIGEST FROM RECEIPTS, WITH NO MODEL

Nothing reads receipts today; every existing digest reads institutional state.

Usable pieces:
- scripts/send_brief_email.py: deterministic SMTP with a plain-text part and an email_dispatched row. Weekly delivery is a flag change. Its credentials exist only on M4.
- Alethelia: fields carry their query or UNKNOWN, rules are tri-state, and there is a DEGRADED banner, all with controls.
- achilles render and run receipts, already scheduled on ELSA.
- atlas/report.py: ASCII, 80 columns wide.
- metis_portfolio _deterministic_brief: live, but it reads heartbeats.
- productive_liveness.derive_health.

Least work: a reader for the one receipt schema, rendered through Alethelia's model and sent by send_brief_email. S-M (1 to 3 days) once the receipt schema exists.

----------------------------------------------------------------------
COMPARISON

```
SLOT                 RANK COMPONENT                  REASON
runner               1    toolbox local.execute      sweep, seed, resume, wall budget, receipt per run; toy scale, no prereg gate
                     2    fabric worker + script     pinned SHA, isolation, retries, artifacts; Linux-only, no campaign notion
                     3    Vivarium loop              sealed spec + replay; one global slot, bound to SFE
queue + lease        1    fabric store               DB-enforced exclusivity, fencing; already the ruled lease authority
                     2    Vivarium queue             strongest triggers; one active row in the whole program
                     3    primordial Redis broker    CPU-time kill, FIFO tokens; ephemeral, Redis on one host
                     4    SFE work_items             per world, SQLite, REST
                     5    comms task_queue           seat message actions, not jobs
ledger + receipt     1    toolbox receipt.v1         smallest validated chained schema; add commit, ruler, energy
                     2    SFE event chain            tamper-evident, prediction window; one writer, client verdicts
                     3    Vivarium attempts/outbox   immutable in the DB; schema tied to SFE/PEW
                     4    RowWriter                  campaign code calls git (anti-pattern)
sealed-world broker  1    Cosmos broker + audit      commitments and ordering; no custody, no access log
                     2    prepost_check              message filter only
derived index        1    atlas                      blob/line provenance; one adapter per engine
                     2    ew reader + projections    content-addressed rows, rebuild digest; Archaeon-specific
dashboard            1    achilles census            scheduled, receipts, failure banner; seat inputs
                     2    Alethelia                  query-carrying fields; dormant
operator digest      1    send_brief_email           live delivery, plain text; credentials on M4 only
                     2    Alethelia renderer         honest UNKNOWN / DEGRADED model
                     3    metis_portfolio            live but stale heartbeat inputs
token/energy meters  1    fabric claude executor     model + USD per attempt, on by default; tokens dropped
                     2    prometheus_llm             tokens + cost per call; opt-in and bypassed
                     3    SFE cost vector            generic; supplied by the caller
                     -    energy                     none outside rented RunPod pods
selection (INF-05)   1    Metis compose.py           deterministic cheapest discriminator; unused
```

----------------------------------------------------------------------
COULD NOT DETERMINE
- No DB connection and no network probe, by rule. So the live row counts (fabric, comms, atlas, viv), worker liveness, the state of PEW, SFE and Vivarium on M2, and the Redis container on M1 are all taken from dossiers. Whether METIS_LLM or PROMETHEUS_LLM_LOG is set on any host: only tracked code was searched.
- Whether Vivarium migrations 006-010 are applied to the live schema: the files say DRAFT, the dossier says they were promoted.
- Not opened because the name contains "holdout": prometheus/cosmos/holdout/*, c3_holdout_D/D2, prometheus/cosmos/tests/test_holdout_isolation.py.
- RAM for M3 and M4, the M4 CPU model, and GPUs on ELSA or DESKTOP-RUAPVAI: git grep for GB, cores and GPU near each host name found only what is listed in A.
- Not opened (outside the nine components): archaeon file queues, agora queue bodies, ops/fleet/fleet_status.py.
- Not read in full: SFE runtime.py beyond the commit, observation and cost sections; api.py; attestation.py; Vivarium runner, loop and deadman bodies; atlas harvesters; achilles build and classify; the portfolio_monitor and mailer bodies; promexec acceptance.py.
- No measured throughput was found for the toolbox, comms or RowWriter.

----------------------------------------------------------------------
SURPRISES

1. Fabric workers cannot run on Windows as written (fabric/worker.py:18 imports fcntl; fabric/executors.py:91 calls os.killpg), and "Windows node worker" is open backlog (fabric/BACKLOG_AFTER_FREEZE.md:8). "No attempts on M1/M2" is a limit of the code, not only of deployment.

2. Inference cost is recorded in one place: fabric claude attempts store the model ids and the USD cost. This contradicts Ixion REPORT s7. The token counts are dropped (fabric/executors.py:145).

3. prometheus_llm is not a choke point. It has 5 code importers against 66 .py files that call providers directly. Its log is opt-in and never enabled, and it has had no commit since 08-22.

4. No store separates write authority at the DB level. fabric, comms, atlas and Vivarium all get credentials through evidence_wiki/ew/db.py from the tracked config (R-1 open). ew's append-only rule has no trigger. Only Vivarium enforces its invariants in the DB. MEAS-11 and ANTI-01 must be built from scratch.

5. In SFE, observation content is outside the hash chain, D6-1 is still present in the code, and the verdict is supplied by the client.

6. ew register_packet hashes raw host bytes (evidence_wiki/ew/store.py:87). This is the PROV-02 failure class inside the evidence store.

7. Queue and lease mechanisms beyond Ixion's 8:
   - engine/queues/*.jsonl, which still feeds the live brief;
   - roles/Aphrodite/leases/lease.py, used on M4 on 09-28 (ops/campaigns/C-003/CAMPAIGN.md:6);
   - primordial's Redis stream job queue.

8. Name collisions (HUM-05):
   - two "fabric" packages: fabric/ and primordial/fabric/;
   - three "broker.py" files: fabric/promexec/, primordial/fabric/, prometheus/cosmos/.

9. fabric's script env allow-list includes COSMOS_BROKER (fabric/executors.py:154), the variable the Cosmos broker sets for its sealed subprocess. This is code-inferred: I did not open the holdout module.

10. The live deterministic brief is stale: docs/portfolio_brief.md at 2026-10-01 12:14:57Z reports Hephaestus dead for 178309 minutes.

11. The M1 CPU is recorded two ways (see A). "AMD64 Family 25 Model 97" is a Zen 4 desktop identifier by my own knowledge, which is consistent with a 7700X and not a 5700X3D. M1 RAM appears as 32 GB in REQUIREMENTS.md and "64GB" in aporia/docs/deep_research_batch10/report_185_erdos_faber_lovasz.md:23, a model-written report.

12. The toolbox's only code importer is prometheus/atlas_bee (8 files). Ixion's "21 external importers" counts mentions, including docs.

13. pivot/m2_apollo_revival_prompt_2026-05-17.md holds a plaintext default DB/Redis credential for a retired host. This is a fourth tracked location beyond Ixion's three. Value not copied.

14. sfe/ is 9,423 lines here, against 9,783 in the Daedalus dossier.

15. Search integrity (the coordinator's correction):
   - Before the correction, `timeout 60 git grep -l "broker" -- 'prometheus/cosmos' ':!**/*holdout*/**' ':!**/nestor_secrets/**'` returned file names only (11), including prometheus/cosmos/tests/test_holdout_isolation.py. No content was printed and the file was not opened.
   - While testing the patterns, `git grep -l "import" -- prometheus/cosmos ':!**/*miner*' ':!**/*holdout*/**' ':!**/*holdout*' | grep -c miner` returned the count 0. Holdout paths may have been scanned, because directory-scoped exclusion proved unreliable (next bullet).
   - Name-only listings printed holdout-named paths: three under evidence_wiki/gold and evidence_wiki/ingest, and roles/Nestor/C3_<H-word>_D_REPORT.md. Name counts: 52 tracked holdout-named paths, 31 of them .py.
   - Every earlier repo-wide search used only the directory pattern. Re-run on the same tree with the corrected pattern, every count-bearing search gives identical counts, so no holdout-named file contributed a number to this report, and no line from one was ever printed.
   - Hazards for other workers:
     - The patterns are case-sensitive and miss roles/Nestor/C3_<H-word>_D_REPORT.md. `:(exclude,icase)` works.
     - On git 2.52.0.windows.1, directory-scoped exclusion misbehaved. `git ls-files -- prometheus/cosmos ':!**/*holdout*/**' ':!**/*holdout*'` returned all 101 paths (42 holdout-named). The same scoped to SerendipityFoundry/SerendipityFoundryEngine returned 0 of 232.
     - A repo-wide exclusion followed by a path-prefix filter was correct in every test.
===END REPORT===
