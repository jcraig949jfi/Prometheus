# Operator ruling, chat, 2026-09-18 (to Harmonia[m2-ca1148a0], M2), VERBATIM

Interesting.  I don't want us using SQLite for this very reason.  Postgres is there as a shared database across machines so we don't have this problem of moving data files around.  I can have an agent on M1 move the database tables into Postgres and we can modify readers and writers to use that instead.

---
Reading (this instance, not the operator): the SFE ledger (SQLite engine.db, two identities: M1 archive eng_8a37a5d3 and M2 live eng_906356f7) moves to the canonical Postgres on M1; an M1 agent migrates; Daedalus (writer) and Archaeon/Vivarium (readers) modify their code. Acceptance conditions this seat will check: rulings/RULING_SFE_LEDGER_TO_POSTGRES_ACCEPTANCE_2026-09-18.md; instrument contracts/ledger_parity_check.py.
