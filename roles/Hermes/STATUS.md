# Hermes STATUS

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11T16:09Z. Written at the base-role adoption pass,
updated after the same day's second pass (the identity-guard assignment).
Plain language. Previous machine-readable status: none -- this seat has
never had one. The digests under agents/hermes/digests/ are the old
loop's output, not the seat's status.

## Seat state: ACTIVE

Asserting PRESENT (roles/Hermes exists on this branch; comms boot
recorded 2026-09-11T15:26Z). ACTIVE (the seat has a lane, a backlog and
a first executable action). PRODUCTIVE as of the second pass: an
instrument was built, run against real targets and committed (see
"Second pass" below). The adoption pass executed nothing, by
instruction. VALID: the guard's own claim -- that it accepts the
canonical store and refuses wrong-but-plausible ones -- is supported by
14 tests including a cheat control, and is not yet supported by anything
outside this seat; that is what the routed packet asks for.

## Where the seat is

- workspace: D:\Prometheus-worktrees\hermes-base-role (linked worktree;
  git-dir D:/Prometheus/.git/worktrees/hermes-base-role differs from
  git-common-dir D:/Prometheus/.git; the D-23 guard passes)
- branch: hermes/comms-identity-guard, base_sha 05b1134e6 (second pass;
  the adoption pass ran on hermes/base-role-adopt-2026-09-11 from
  base_sha 8714b2709, merged to main)
- machine: M2 (SPECTREX5)
- base role: read in full at 8714b2709; receipt
  roles/Hermes/BASE_ROLE_ADOPTION_2026-09-11.txt
- comms: booted 2026-09-11T15:26Z, status active, model
  claude-opus-5[1m] (heavy), capabilities TOOLS,any; synced 15:27Z,
  2 messages seen (Archaeon's program broadcast #1 and ruling #39),
  queue length 0, nothing addressed to Hermes
- long-running processes owned: NONE ON THIS HOST. Verified on M2: no
  process and no scheduled task matching intelligence_loop,
  send_brief_email, portfolio_monitor, metis_portfolio or pronoia. The
  machinery this seat owns runs on M3 or M4 and is not observable from
  here (HERMES-XL-3)
- worktrees owned: this one only
- last activity before today: 2026-05-23 (cce4505ed), the mailer's
  TypeError guard. The seat itself was deprecated 2026-05-17

## What is live and what is dormant (base rule 7)

- Hermes portfolio brief mailer (scripts/send_brief_email.py). State
  UNKNOWN from this seat, registered ACTIVE-UNVERIFIED in
  roles/base-role/MONITORS.md with this pass's evidence. It has no
  freshness record, no payload hash and no unchanged-payload check
  (verified by reading the source at 8714b2709). Owner: claimed by
  Hermes on this pass, pending HERMES-XL-1.
- Its input, docs/portfolio_brief.md, produced by
  scripts/intelligence_loop.py on a 4-hour cadence: DORMANT since
  2026-09-09T02:15:15Z. Measured 2026-09-11T15:16Z as 61.0 hours, about
  15 missed cycles. Freshness source, readable without running it:
  `git log -1 --format='%h %aI %s' --grep='auto: portfolio update'`
  (64de18126). Owner UNCLAIMED; registered on this pass; HERMES-XL-2.
- agents/hermes/src/hermes.py, the March digest agent: DEPRECATED
  2026-05-17, not running anywhere, not registered as a monitor
  because it is not a loop any more. Its 60 digests stay as residue.

## Blockers found on this pass, and what was NOT done about them

- comms on M2 resolves to the WRONG DATABASE by name. The Evidence Wiki
  resolver's default sent `python -m comms boot` to localhost
  prometheus_fire on M2, which is the local fork and has only the
  `public` schema; the canonical comms tables are on M1
  prometheus_fire. The failure surfaced as
  `UndefinedTable: relation "comms.agents" does not exist`.
  NOT DONE, deliberately: `python -m comms init` was NOT run. Running
  it would have created a second comms schema on M2 that is correct by
  every name check and is a silently forked program inbox -- the exact
  label-over-capability failure the base role opens with. Resolved
  instead by the documented override EW_DB_HOST=192.168.1.202
  (evidence_wiki/docs/OPERATIONS_V1.md line 39), after which boot and
  sync both succeeded against the canonical store. Filed as HERMES-25;
  the defect belongs to comms and the Evidence Wiki resolver, not to
  this seat, and is reported rather than patched from here.
- `git pull` was run in the canonical checkout as this pass's first
  command, before the working contract had been read. Harmless in fact
  (a no-op fetch, "Already up to date", no tree change) and recorded in
  calibration/CALIBRATION.md row 8 rather than omitted. Every command
  after it ran from the linked worktree.

## Today (2026-09-11)

- worktree created from origin/main 8714b2709; base role read in full
  (README, NORTH_STAR, RESPONSIBILITIES, WORKING_CONTRACT, INHERITANCE,
  MONITORS), plus the backlog schema and comms/README.md
- archaeology completed from the repository record: 11 May commits, the
  deprecation note, three roster/disposition documents, the source of
  both surviving scripts; 12 queue rows classified
- roles/Hermes created: RESPONSIBILITIES (entry file), ARCHAEOLOGY,
  BACKLOG (25 rows, 3 XL), calibration (8 rows), journal, receipt, the
  operator prompt verbatim with MANIFEST
- agents/hermes/README.md annotated HISTORICAL at its top, not rewritten
- INHERITANCE.md: Hermes's own two rows added, per Archaeon's ruling #39
- MONITORS.md: two rows -- the mailer (owner claimed, evidence attached)
  and the brief producer (DORMANT, owner unclaimed)
- comms: booted, synced twice, 2 messages seen, 0 queued
- executed: nothing. No email, no loop started or stopped, no database
  written except the comms boot and sync rows the base role mandates

## Second pass, 2026-09-11 (operator assignment: the wrong database)

Executed this time, and it is the seat's first productive work: an
identity guard for database connections, with 14 adversarial tests green
against the two real clusters plus a constructed target.

- built  roles/Hermes/science/db_identity.py, ENVIRONMENTS.json,
         test_db_identity.py (positive + negative + CHEAT controls)
- found  the discriminator already existed and was never compared to
         anything: evidence_wiki/ew/closure.py service_attestation()
         reads pg_control_system().system_identifier and stamps it on
         every row. The expectation and the refusal were missing, not
         the evidence.
- found  comms was hardened four hours earlier (5f9d8ea7e) with a
         STRUCTURAL check. It closes the fork-the-queue path and it
         cannot discriminate identity: a database given the real
         comms/schema.sql satisfies comms's own predicate (demonstrated
         with a built-and-dropped fixture).
- found  the Evidence Wiki path is the open one: `ew` exists in BOTH
         stores (41 tables on M1, 34 on the M2 fork), so a call resolved
         to localhost on M2 succeeds with no error at all.
- routed roles/Hermes/prompts/2026-09-11_comms_identity/ to Archaeon
         (comms) and Mnemosyne (Evidence Wiki), Harmonia copied as
         information only. Hermes modified neither lane's code.
- opened roles/Hermes/incidents/c84e26826cc12217.md -- one file per
         failure SIGNATURE, all five seats' occurrences in it.

Success criterion, updated 2026-09-11 after Archaeon's ruling: for
COMMS it is now mechanically impossible. Archaeon accepted the packet
(#73, D-24 amendment 1) and delegated the move; comms/identity.py is
wired into comms.api.connect() ahead of the structural check, `comms
init` refuses an unregistered environment, 24 comms tests green.
Measured on M2 with no override: comms now refuses by identity and
names the incident signature, where it used to raise UndefinedTable.
For the EVIDENCE WIKI it is still possible and still silent; that half
is open with Mnemosyne (comms #69) and is the one that matters more,
because `ew` exists in both stores.

## Next executable action

HERMES-26 tracks the packet to a ruling. Independent of it:
HERMES-01: write the delivery ledger (last_input_at, last_success_at,
payload sha256, no-op reason) as a committed JSON with its schema, and
prove it with a --dry-run that writes one row. It does not depend on
HERMES-XL-1, because a ledger describing a loop nobody has claimed is
still the thing that would have caught the 2026-05-23 silent-death and
the 61-hour stale payload. HERMES-03 and HERMES-12 are also independent
of every open decision.

Waiting on the operator: HERMES-XL-1 (does Hermes own the mailer;
recommendation yes, as an instrument), HERMES-XL-2 (who owns the dead
producer; recommendation not Hermes), HERMES-XL-3 (which host Hermes is
seated on, given its machinery is on M3 or M4 and it booted on M2).
None of the three blocks the next action.
