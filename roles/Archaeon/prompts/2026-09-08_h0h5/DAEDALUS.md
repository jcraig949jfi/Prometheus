DAEDALUS — H0-H5 ITERATION 1 (from the operator, 2026-09-08)

Read first: roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md
(sections 3, 4 C1/C4/C5, 6). You own SFE: durable worlds, work, artifact
visibility, budget accounting, event identity. Inspect the existing
artifact and resource paths in sfe/runtime.py before adding anything; the
missing work is wiring, complete accounting and qualification, not a
second artifact store or budget engine. Do not restart the production
service; prepare deployment for review. Use a development engine.

DELIVER
1. Authorized artifact resolution for preflight: given (world_id,
   artifact_id) bound to a sealed digest, return immutable bytes only if
   the requesting client may see that world under the existing visibility
   and sharing policy; engine-side digest verification; preserve source
   import provenance and the restrictions on re-exporting imported
   artifacts. A digest alone never authorizes a read. No global
   digest-fetch endpoint, no raw CAS path.
2. Client support (sfclient) for that resolution and for expected-hash
   gates, in every client copy.
3. Cost events on the existing resource mechanism: unique cost_event_id,
   attempt id, stage, source/output artifact refs, environment identity,
   resource vector with per-resource {quantity, unit, method, enforcement
   class (enforceable | measured | estimated | unavailable), scope}.
   Attribution, reservation and reconciliation IDEMPOTENT and compatible
   with existing lineage budgets so a fork cannot multiply an allowance.
   Reserve/debit enforceable counters BEFORE the operation; a post-hoc
   debit is not enforcement. Unavailable is not zero.
4. Fixtures: permission denied; wrong hash; double billing refused; fork
   budget not multiplied; oversized artifact refused at the configured
   limit. One exact end-to-end receipt of a producer-created artifact
   resolved by an authorized reader and charged once.

NOT ASKED: process spawning, a scheduler, any change to spec_hash or the
no-defaults rule, credential reissue (separate item, still open).

REPORT: the brief's iteration receipt JSON with real identifiers; exact
commands; expected vs observed; tests not run marked.
