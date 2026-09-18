# Operator ruling MNE-D1, received in chat 2026-09-17 (Mnemosyne instance m2-9c10ae00), verbatim

MNEMOSYNE — MNE-D1 OPERATOR RULING

Decision:

O2 — APPROVED NOW
O3 — DEFERRED, WITH EXPLICIT CUTOVER CONDITIONS
O4 — REJECTED
O1 alone — INSUFFICIENT

Campaign 3 is closed, so the active-campaign migration freeze no longer blocks this action.

Proceed with O2:

establish an M2-owned nightly pg_dump of the canonical PostgreSQL
cluster over the LAN;
retain the dumps on M2 under an explicit retention policy;
perform a weekly restore qualification into the M2 PostgreSQL
instance;
verify the restored cluster rather than treating pg_restore exit 0
as sufficient;
record backup identity, source cluster identity, dump digest,
PostgreSQL versions, restore target, row/schema sanity checks,
timestamps, and result;
alert visibly on missed backup or failed restore qualification.

This is resilience work, not a PEW schema migration.

Do not move the canonical database as part of O2.

⸻

M1 STATUS

M1 remains SHARED INFRASTRUCTURE until the canonical PostgreSQL cutover.

It is not yet Nestor-exclusive.

The fact that Nestor is the primary workload intended for M1 does not
override the measured fact that the canonical PostgreSQL cluster still
serves both ecosystems.

Do not create an operational fiction in which M1 has been handed over
while Prometheus still depends on its database.

⸻

O3 — MIGRATION

Do not perform O3 during this immediate point release simply to make the
machine assignment aesthetically clean.

O3 is approved in principle once the following are true:

1. O2 has produced at least two successful backup cycles;
2. at least one full M2 restore qualification has demonstrated that
   the canonical cluster can be recovered independently of M1;
3. every consumer of the canonical PostgreSQL service has been
   enumerated, including both ecosystems and comms;
4. connection strings / service discovery changes are prepared and
   reversible;
5. the backend point-release integration has completed far enough
   that we are not debugging schema changes and a physical database
   migration simultaneously;
6. no scientific campaign is active;
7. a rollback path to the M1 canonical cluster is rehearsed.

Then schedule O3 as one explicit infrastructure cutover.

⸻

PREFERRED DESTINATION

Before executing O3, resolve one additional architectural choice:

If a third machine intended for shared infrastructure
(PostgreSQL / Redis / other central services) is actually going to be
stood up in the near term, prefer migrating the canonical cluster there
rather than:

M1 -> M2 -> central-services host

in two successive moves.

If no central-services host is imminent, migrate the canonical cluster
to M2 after the conditions above are satisfied.

Do not postpone indefinitely waiting for hypothetical hardware.

⸻

PEW POINT RELEASE

Continue Stage 0/1 work now.

Do not block:

campaign reader,
migration-014 design,
ingestion checkpoints,
provenance-envelope design,
projection definitions,
acceptance fixtures

on O3.

Production migration 014 and campaign ingestion should occur only in the
coordinated point-release deploy window after peer review and scope
freeze.

O2 may proceed before that window because it does not change scientific
schema or campaign semantics.

⸻

IMPORTANT PRINCIPLE

Backup ownership and database ownership are separate questions.

We need independent recoverability FIRST.

Physical relocation comes SECOND.

Once M2 can independently prove:

"I possess a current, verified, restorable copy of the canonical
 Prometheus database",

the O3 migration becomes a controlled operational choice rather than a
high-consequence act of faith.

Proceed with O2.
Record the receipts.
Keep M1 canonical and shared for now.
Prepare O3.
Do not split the store.
