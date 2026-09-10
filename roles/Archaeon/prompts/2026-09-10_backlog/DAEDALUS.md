DAEDALUS -- NEXT WORK (operator 2026-09-10, via Archaeon; schema in
roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md; authority in
roles/Archaeon/prompts/2026-09-10_delegation/00_COMMON.md)

OPEN FROM TODAY, IN ORDER
1. DEPLOY SCHEMA 8 TO M1. Condition (a) is now met: cs-c3-2 is complete
   and cs-h1h0-1-p2 has no queued or running rows (Archaeon cancelled the
   artifact rows). Re-run deploy/preflight_deploy.py, and if it passes,
   deploy per your committed runbook with --max-artifact-bytes 33554432,
   with Vivarium restarting the consumer after and confirming. Report the
   engine instance id before and after and the source hash; Archaeon moves
   its reader guard to 8 on your report. If the gate says no, quote it.
2. READ TIMEOUTS: two rows died today on "The read operation timed out"
   after the experiment was committed (C3-2 random_076; a tick row at
   16:12), and the engine wrote ~3,768 experiments/hour. Profile the write
   path under that load and commit the numbers; say whether the client
   timeout, the engine, or the host is the bound. No tuning without the
   measurement.
3. COST RECONCILIATION, END TO END: with cost_report's by_artifact index
   and Archaeon's reconcile_by_digest (04f8e31c3), reconcile one real run
   (cs-h1h0-1-p1 producer receipts vs engine cost events) and commit the
   join: matched / producer_only / engine_only by digest.
4. ARCHAEON'S READ SCOPE (decision B1, open since 09-08): Archaeon holds no
   engine scope and reads results through the queue projection. Propose the
   smallest grant (read-only, world-scoped or role-scoped) with its
   credential lifecycle, as a committed proposal for the operator; do not
   issue it.
5. HARMONIA'S CONFORMANCE CONTRACT pins schema 6 against a live 7 (your
   finding). Coordinate with her: what the contract must say for 7 and 8,
   as a joint commit.

THEN THE BACKLOG: roles/Daedalus/BACKLOG_H0H5.md, at least 20 items.
Seed it with: the engine features each lane's beta/1.0/1.1 needs (temporal
program interface; encoding_search_v1 support; runtime loader for H3 1.0;
per-artifact ceilings and their read policy; multi-world budget lineage);
engine-side cost events for producer stages (C4-3); a status/health
endpoint; schema-9 candidates and what each would retire; the
v8 reservation semantics under concurrent consumers; a replay harness
that re-executes a sealed spec on a fresh engine and compares the
normalized result projection (design: "scientific replay compares a
declared normalized result projection").

REPORT: SHA on main and path per item; exact commands; the deploy first.
