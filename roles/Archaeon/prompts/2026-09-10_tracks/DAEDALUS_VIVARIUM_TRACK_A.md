DAEDALUS AND VIVARIUM — TRACK A, PART 1: ONE DEVELOPMENT BUILD (from the
operator, 2026-09-10)

Read: roles/Archaeon/prompts/2026-09-10_tracks/CHIMERA_BRIEF_2026-09-10.md
§2 "Integration" and §3 Track A. Vivarium integrates; Daedalus supplies the
engine/client. Your two iteration-1 receipts were made on DIFFERENT tested
configurations (Vivarium: schema-7 dev engine, cost events absent; Daedalus:
schema-8 candidate with cost events, reservations, read-path digest gate).
Neither is false; they have not been run together. Do that now.

DELIVER, in this order
1. Land/reconcile on ONE development build: Vivarium's loader and
   ca_density_v0 (959d35043, 01376aa87, e43a6c7f2) with Daedalus's
   ef05397f2 engine and client. Preserve unrelated work. Remove Vivarium's
   copy of herakles/evca now that Herakles's library is on main
   (0641c567b); the wrapper imports the canonical one.
2. Daedalus: sfclient.register() RETAINS the engine-issued client_id (it
   currently keeps only the token); the client passes expected_blob_hash
   on the read path. Do not log credentials; do not invent a substitute
   principal. Vivarium: the loader's preflight uses the engine-side digest
   gate rather than comparing in the client.
3. One joint receipt on that build: a producer-created artifact consumed by
   artifact_probe_v1; engine cost events with reservation BEFORE the fetch,
   debit, an interrupted attempt retried once, and reconciliation against
   Archaeon's producer receipts (archaeon/producer/costs.py: match on
   attempt_id and stage; report matched / producer-only / executor-only /
   engine-side); idempotent publication with recorded_in_sfe and
   indexed_in_pew separate; counterfactual attribution under a declared
   reuse horizon. Re-run the ten rejection fixtures only where integration
   changed the guarantee.
4. Daedalus: refresh deploy/CANDIDATE_BUILD.json for the integrated files
   and the measured build: Git commit, runtime source hash, schema, engine
   instance id as DISTINCT identities with an explicit mapping; code-and-
   data rollback; conformance-pin changes. This is for the operator's
   review; it does not authorise a restart.

Keep memory as MEASURED (never labelled enforced); keep the wall guard's
between-repeats limitation stated; logical work bounds live in the kind.

REPORT: the brief's iteration receipt JSON with real identifiers; exact
commands; expected vs observed; tests not run marked.
