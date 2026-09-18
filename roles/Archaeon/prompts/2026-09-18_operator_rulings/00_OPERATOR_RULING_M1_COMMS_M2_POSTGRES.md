# Operator ruling (verbatim, chat, 2026-09-18 ~01:00Z) -- comms on M1; scope of M2 Postgres

Received by Archaeon[m2-49ee5a4d] in session 49ee5a4d (Claude Code, M2).
Reproduced verbatim. Nothing added, nothing removed.

---

Everyone should be using the postgres database on M1 for the comms channel.  Postgres on m2 is intended for mechanisms that truly need to be duplicated from a sql perspective on both machines.  Machine independence

---

Reading (Archaeon's, not the operator's): (1) restates the 2026-09-17 ruling
already in base-role boot step 1 (Herakles #397): comms = the canonical M1
store, EW_DB_HOST=192.168.1.202 before the first comms call on any non-M1
host. (2) NEW SCOPE: the M2 local Postgres exists for mechanisms that must
be duplicated at the SQL level on both machines for machine independence --
not for queues, registers or stores whose single canonical copy is M1
(comms, viv, ew). A seat that wants a table on M2 says which mechanism
needs SQL-level duplication and why; otherwise the table belongs on M1.
Archaeon's own state: comms, viv queue/register reads, ew ingest all on M1
this session; nothing of Archaeon's on M2 Postgres.
