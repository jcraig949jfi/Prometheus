# Agora archaeology of the April queue (2026-09-14)

Currency: 2026-09-14. Booting an old seat is an archaeological event, not
an instruction to resume its last queue (base role, seat states). Every
item the seat held -- in roles/Agora/RESPONSIBILITIES.md (April body, now
under superseded/), SESSION_STATE_20260415.md, SESSION_STATE_20260415_v2.md
and SESSION_JOURNAL_20260415.md, all at be82cdd8b -- is classified here
against the current north star, the current ecology and current
instrumentation doctrine.

NOTHING HERE IS EXECUTED. Only STILL_LIVE would become executable work;
NEEDS_REPREMISE must be re-stated first; the rest are recorded. Nothing
is marked dead: PARKED and SUPERSEDED items keep their residue navigable.

Measurements on this pass are READ-ONLY queries against prometheus_fire
through comms.api.connect, each inside SET TRANSACTION READ ONLY, run
2026-09-14 from worktree agora-base-role at be82cdd8b. Script:
the session scratchpad agora_probe*.py (not committed; the queries are
restated beside each number so they can be re-run).

Tally (26 items): 0 STILL_LIVE, 0 NEEDS_REPREMISE, 8 PARKED,
9 SUPERSEDED, 3 TRANSFERRED, 4 RETIRED, plus 2 already DONE and verified.

## A. The substrate the queue lived on

The April Agora ran on Redis under WSL on M1 (streams + hashes + sets),
mirrored into Postgres agora.messages. Measured: agora.messages holds 196
rows, 2026-04-15 06:13 .. 2026-04-29 07:06 (-04:00)
(`select count(*), min(created_at), max(created_at) from agora.messages`).
Redis was retired 2026-06-24 (roles/Ergon/REDIS_TO_POSTGRES_2026-06-24.md);
the channel was replaced by the comms queue on 2026-09-11 (D-24). The
science items rode the LMFDB-tensor lane, which the program has PARKED
(roles/Kairos/ARCHAEOLOGY_2026-09-11.md s A gives the frame and is not
repeated here). Where Kairos already classified a shared item, this file
agrees with it and points to it rather than re-deciding.

## B. Queue items, classified

Format: item | class | why | what would have to be true to change it

Infrastructure and protocol (RESPONSIBILITIES Phases 1-4, coordination loop)

1. Redis streams agora:main/:challenges/:tasks/:discoveries | RETIRED |
   Redis retired 2026-06-24; channel replaced by comms (D-24) | none.
2. agent:{name} hashes, 60 s heartbeats, 5 min death rule | RETIRED |
   presence is now derived from sync receipts (base role); a heartbeat
   label is a meaning that expired | none.
3. hypotheses:alive / :killed sets, leaderboard:kills | RETIRED |
   "kills are currency" is the 1.0 reward the base role replaced with
   metabolise; the sets lived in retired Redis | none.
4. Agora coordination loop, 5 min cron, poll all streams | RETIRED |
   the channel does not exist; base rules 8-10 forbid a loop with no
   productivity signal, no bound and no accountable seat; no scheduled
   task is created | none.
5. Phase 4 role-based routing | SUPERSEDED | comms messages are
   addressed per seat or broadcast | none.
6. Phase 4 cross-machine task scheduling | SUPERSEDED | comms task queues
   plus `comms claim` with instance tags (D-24 amendment 3) | none.
7. Group decision protocol (when a finding is accepted) | SUPERSEDED |
   acceptance follows executable verifiers and human admission, never a
   vote or model confidence (base role s0, s2) | none.
8. agora/ Python client (client.py, protocol.py, config.py; heartbeat.py
   and cli.py named in April are ABSENT on origin/main) | TRANSFERRED
   (as a record) | the package is Harmonia-lineage client code; its
   README still names the retired Redis address; this seat claims no
   ownership | a seat that imports it names itself owner.
9. Postgres agora schema (messages, decisions, open_questions and 10
   later tables) | TRANSFERRED (as a record) | the schema is LIVE:
   agora.agent_heartbeats last write 2026-09-14 06:51:08 (-04:00), 36 rows
   (`select count(*), max(last_heartbeat) from agora.agent_heartbeats`);
   the writer is Pronoia's pipeline per roles/base-role/MONITORS.md |
   none; not this seat's. NOTE: a table named agora.temp_secrets exists;
   it was NOT read on this pass; reported by name only (journal).

Science coordination items (Phase 3 open, session-state "ready" lists)

10. Adversarial code review of Kairos's gradient_tracker.py ("owed") |
    SUPERSEDED | harmonia/src/gradient_tracker.py has one commit ever
    (05b2b2b95, 2026-04-15); importers are harmonia/src/landscape.py and
    agora/resume_broadcast.py only; the exploration-reform lane it served
    has no current consumer; a same-model review would not supply an
    independent failure mode anyway | a live consumer imports it; then
    Kairos or Nemesis attacks it, not this seat.
11. Open Question #1, spectral tail asymptote (Agora was challenger) |
    PARKED | agrees with Kairos ARCHAEOLOGY item 5: the best-designed April
    item, parked on an unverified, unconsumed substrate | as Kairos item 5.
12. BSD parity test | PARKED | agrees with Kairos item 1 | as Kairos item 1.
13. BSD leading_term bypass | PARKED | agrees with Kairos items 2 and 7
    (rank-0 calibration parked; rank >= 2 non-circular design retired as
    designed) | as Kairos.
14. Mahler measure -> EC matching | PARKED | no consumer; LMFDB lane
    parked | a consumer names it.
15. Silent islands P1-P8 | PARKED | agrees with Kairos item 13 | as Kairos.
16. Artin entireness direct test, Brumer-Stark, Lehmer | PARKED | agrees
    with Kairos items 8 and 9 | as Kairos.
17. NF backbone identification (store TT singular vectors) | SUPERSEDED |
    agrees with Kairos item 14: void until its claim is re-established |
    as Kairos.
18. Aporia Bucket A triage "post to agora:discoveries" | SUPERSEDED | the
    channel is gone; aporia/mathematics/triage.jsonl exists on main; the
    routing step is what is superseded, not Aporia's file | none.
19. Ergon "needs session restart with Bash permissions" | SUPERSEDED |
    Ergon is re-chartered on base-role (project memory, Ergon adoption
    commits) | none.
20. "Transfer ergon/results from M2" | TRANSFERRED | Ergon's and
    Mnemosyne's lanes; not verified on this pass | Ergon names it.

Data items (RESPONSIBILITIES "Open Work Log")

21. P-009 rebuild zeros tables (EC done; MF, G2, Dirichlet unfinished) |
    PARKED | measured 2026-09-14: zeros.object_zeros = 2,009,089 rows, ALL
    object_type elliptic_curve, object_id non-null on all 2,009,089
    (Ergon's 2026-06-23 rekey finished), n_zeros 9..43 with 35 distinct
    lengths (the uniform-24 defect is gone for EC), source
    'lfunc.positive_zeros@2026-04-16' on every row
    (`select object_type, count(*), min(n_zeros), max(n_zeros),
    count(distinct n_zeros) from zeros.object_zeros group by 1`);
    zeros.dirichlet_zeros = 0 rows, while
    charon_duckdb.dirichlet_zeros = 184,830 rows (the archive copy,
    roles/Ergon/DUCKDB_RETIREMENT_AUDIT_2026-06-24.md). So the P-009
    acceptance criteria are NOT met: no MF, no G2, no Dirichlet rows.
    Parked because no current seat consumes zeros data (LMFDB lane parked).
    Also: the proposal is Mnemosyne's (thesauros/proposals.md P-009), so
    ownership was never Agora's | a consumer names zeros data it needs;
    then Mnemosyne owns the rebuild, with the named-cursor fix recorded in
    the superseded body.
22. Drop the three *_corrupt_20260416 tables after 30 days | DONE
    (by others; verified) | measured: schema zeros holds exactly
    dirichlet_zeros and object_zeros
    (`select table_name from information_schema.tables where
    table_schema='zeros'`); the _ext copy was dropped 2026-06-24 per Ergon;
    who dropped the other two was not established on this pass | none.
23. P-012 signals.specimens.data_provenance JSONB + GIN index | DONE
    (verified) | measured: column signals.specimens.data_provenance jsonb
    exists and index idx_specimen_provenance exists
    (information_schema.columns, pg_indexes) | none. Whether writers
    populate it was NOT measured.
24. prometheus_sci gaps (pdg charge/spin, groups.is_solvable,
    knots.signature, polytopes.is_simplicial) | PARKED | never started;
    no consumer | a consumer names one.

Standing orders (April)

25. "Challenge everything", "confidence is mandatory", "no consensus
    bias", "divide, don't duplicate" | SUPERSEDED | re-homed and
    strengthened in the base role: controls (negative, positive, cheat),
    eligible counts, independent failure mode, no LLM adjudicates, lane
    discipline. A "confidence 0.0-1.0" field is model self-report, which
    base rule 2 declines to accept as evidence | none.
26. "Kills are currency" | SUPERSEDED | replaced by "failure geometry is
    the product" and metabolise-not-kill (base role, Kairos 2.0) | none.

## C. April conclusions (SESSION_JOURNAL "Key Findings")

None was produced under current doctrine (no preregistration commit, no
eligible count, no cheat control, same-model review). So none carries a
current tier; none is declared false. Kairos ARCHAEOLOGY s C already
withdrew the tiers of the NF-backbone, analysis/algebra-duality and
Megethos claims and is the reference. Two additional April calls were the
coordinator's own and are entered in roles/Agora/calibration/LEDGER.md:
"battery works correctly (CONFIRMED)" and "the adversarial system works".
The Sha circularity observation (LMFDB Sha at rank >= 2 assumes BSD) is a
statement about how a dataset was computed, not a tier; it stands as a
documented data-provenance fact and is what retired Kairos item 7.

## D. Residue a future search can reach

- agora.messages (196), agora.decisions, agora.open_questions: the April
  conversation, in Postgres, untouched.
- The April files in this directory, annotated HISTORICAL, bodies unchanged.
- The P-009 named-server-side-cursor fix, in the superseded body.
- charon_duckdb.dirichlet_zeros (184,830): the only populated copy of
  Dirichlet zeros in Postgres.
