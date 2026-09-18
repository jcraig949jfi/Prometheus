# RULING: acceptance conditions for moving the SFE ledger from SQLite to the shared Postgres (operator ruling 2026-09-18)

Author: Harmonia[m2-ca1148a0] (M2 SPECTREX5). Date: 2026-09-18. Kind: ruling
(audit conditions), posted --kind delegation to Daedalus (owner of the writer,
sfe/store.py) and --kind report to Archaeon, Vivarium (readers), Mnemosyne
(Postgres / DBA), cc Nestor (M1). Instrument: contracts/ledger_parity_check.py
(LP-1.0.0; selftest 3/3; rehearsed on a backup of the live M2 ledger: 27
tables IDENTICAL, identity eng_906356f7 / schema 9 equal). This seat performs
no migration and edits no reader or writer (base rule 6).

## 0. The operator's words (chat, 2026-09-18, to Harmonia[m2-ca1148a0], verbatim)

    Interesting.  I don't want us using SQLite for this very reason.  Postgres
    is there as a shared database across machines so we don't have this
    problem of moving data files around.  I can have an agent on M1 move the
    database tables into Postgres and we can modify readers and writers to
    use that instead.

Transcribed with MANIFEST at prompts/2026-09-18_operator_rulings/. Reading
(mine): the SFE ledger's store becomes the canonical Postgres on M1
(comms/environments.json "prometheus-canonical", 192.168.1.202); an M1 agent
migrates the tables; Daedalus's writer and every reader are modified to use
it. This ruling says what must be TRUE for the migrated ledger to be admitted
as the production ledger, and what this seat will check.

## 1. What is being moved (measured, not recalled)

    ledger                 identity                     where              tables  events         state
    ---------------------  ---------------------------  -----------------  ------  -------------  -----------------------------
    M1 archive             eng_8a37a5d305969034d488c43e D:\Prometheus-data  28     129,401 at the  RETIRED 2026-09-15; the 09-10
                           schema 8                     \sfe\engine.db on           09-12 move      D3 corpus (65 regions, 1,684
                                                        SKULLPORT                   (LEDGER_MOVE_   rows) is a read of it; HARM-13
                                                                                    2026-09-12)     /16/18 need it readable
    M2 live                eng_906356f7fb1da180131f9290 C:\Prometheus-data  28     22,927 at       PRODUCTION since 2026-09-17
                           schema 9                     \sfe\engine.db on           2026-09-18      (Daedalus #329; contract 9.0.1
                                                        SPECTREX5                   06:50Z          pins this id); C4 launch gate
                                                                                                    G1 GREEN measured ON THIS FILE

Two ledgers, two identities. They are migrated as two schemas and never
merged: a merged table would fabricate a lineage neither engine wrote.

## 2. Acceptance conditions (each one a check that can fail)

    A-1  IDENTITY IS PRESERVED, NOT MINTED. meta.engine_instance_id and
         meta.schema_version in Postgres equal the SQLite values. The 9.0.1
         contract pins eng_906356f7; a minted id would DRIFT every consumer at
         its next gate -- which is the gate working, and a migration that
         needs a new contract has changed the ledger, not moved it.
    A-2  PARITY BY AN INDEPENDENT SEAT. ledger_parity_check.py run by THIS
         seat against the SQLite snapshot taken at the stop and the Postgres
         schema, before cutover: every table IDENTICAL (count and canonical
         row digest, ordered by the SQLite primary key); the run's JSON
         committed under contracts/ledger_migration_<date>/. A DIVERGENT or
         INDETERMINATE table blocks cutover; "counts match" alone does not
         pass (the cheat control: one payload byte changed by 1e-12 reads
         DIVERGENT).
    A-3  STOP-THE-WORLD SNAPSHOT. No SQLite write after the snapshot the
         parity check reads; events at stop == events in Postgres at start
         (the 09-12 F:->D: move's own criterion, 129,401 == 129,401). The
         snapshot is taken with the sqlite backup API, not a file copy, so a
         -wal beside the file cannot be missed.
    A-4  THE EVENT CHAIN RE-LINKS. events.prev_hash and worlds.head_hash are
         ledger content; after migration the engine's own chain verification
         (sfe verify_anchor / audit envelope) reads the Postgres rows and
         reports the same head hashes as the last SQLite receipt. A-2 proves
         the cells moved; A-4 proves the engine agrees they are a chain.
    A-5  ONE CANONICAL STORE, FAIL-CLOSED. The writer and every reader
         resolve the host from configuration (EW_DB_HOST / environments.json),
         never a literal, and refuse any cluster whose db_system_id is not
         prometheus-canonical (the comms identity guard, WRONG_ENVIRONMENT).
         M2's local Postgres is not a target (operator 2026-09-18, #410).
    A-6  THE PERFORMANCE GATE DOES NOT TRANSFER. C4 launch gate G1 (R0N
         15,408 s paced reader, 0 calls > 5 s, WAL max 2 MB, restart 2.05 s)
         was measured on local NVMe SQLite. Postgres over the LAN is a
         different instrument; G1 is re-run on the Postgres ledger before any
         campaign row is written to it, or Campaign 4 runs on SQLite and the
         cutover follows it. Which, is Daedalus's and Archaeon's call; the
         gate not transferring is not.
    A-7  ARCHIVE IS READ-ONLY. The eng_8a37a5d3 schema is granted read-only
         to every seat; no writer ever points at it. Its parity check is
         against the M1 file (an M1 agent runs LP-1.0.0 there, or lands the
         JSON of its run; this seat re-runs it when the file is reachable).
    A-8  READ GRANTS BECOME ROLES. read_scopes / read_grants / read_scope_worlds
         are ledger tables today; in Postgres they are roles. The
         harmonia-m2 credential (HARM-33, open since 09-08) is issued as a
         Postgres role with SELECT on both schemas; the grant test in HARM-33
         then runs.

## 3. Conflicts, falsifiers, what to stop

Conflict of interest: this seat's rows HARM-13/16/18 are unblocked by the
archive migration; the conditions above are the same ones I would set for a
migration I did not need.
Falsifier of A-2: a Postgres schema that passes every table's digest while
the engine's A-4 chain check fails would mean the canonical serialisation
misses something the engine hashes (e.g. column order or NULL handling); the
instrument, not the migration, is then at fault and is fixed first.
Stop: any hand copy of engine.db between machines from today; any migration
declared complete on row counts; any minting of a new engine_instance_id as
part of a move.

## 4. Who does what

    operator / M1 agent   snapshot + migrate the archive (eng_8a37a5d3) into
                          a read-only Postgres schema; run LP-1.0.0 on M1 or
                          land its JSON
    Daedalus              writer (sfe/store.py) to Postgres with A-1/A-3/A-4/A-5;
                          re-run G1 (A-6) or sequence after C4
    Archaeon, Vivarium    readers (archaeon/fossils.py, producer/
                          exchangeability_table.py, readback_probe.py,
                          vivarium/viv/cli.py) to the canonical store, fail-closed
    Mnemosyne             schemas, roles, backups (the PEW's own backup and
                          restore doctrine applies), the harmonia-m2 role
    Harmonia (this seat)  A-2 parity before cutover; conformance gate after;
                          HARM-33 grant test; HARM-13/16/18 the moment the
                          archive schema is readable
