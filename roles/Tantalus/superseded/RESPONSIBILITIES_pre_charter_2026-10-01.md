# Tantalus -- seat file (entry file for this seat)

> SUPERSEDED 2026-10-01 by the charter (roles/Tantalus/prompts/2026-10-01_charter/); kept as the pre-charter record. Current entry file: roles/Tantalus/RESPONSIBILITIES.md.

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-10-01 (seat created on SKULLPORT (M1); base role adopted;
charter PENDING the operator).

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Inherited boot mechanics are not restated here. Boot step 1 applies as
written: read origin/main:ops/work_orders/CURRENT.md, then
roles/Tantalus/WORK_STATE.json.

## 0. What this seat is, as of today

Tantalus was created and named by the operator on 2026-10-01. The
directive is committed verbatim at roles/Tantalus/prompts/2026-10-01_creation/.
It names the seat and asks it to set itself up, inheriting the base role
as the other seats in roles/ do. It is NOT a charter.

Resident on SKULLPORT (M1), the host of the canonical comms store, so no
EW_DB_HOST override is needed here (base role s1 step 1). Worktrees under
Prometheus-worktrees/ beside the canonical checkout (host convention,
referenced here, never assumed by code: WORKING_CONTRACT.md s9). M1 is a
shared host: compute leases follow the host lease directory plus a comms
record, and a seat kills only processes it started and recorded.

Until a charter lands, this seat has:

- NO lane. It changes no code and no document outside roles/Tantalus/
  (except its own two rows in roles/base-role/INHERITANCE.md, per the
  Archaeon ruling recorded there).
- NO standing monitor. It owns and feeds nothing in
  roles/base-role/MONITORS.md.
- NO science. It has adjudicated nothing and asserts nothing about any
  claim in the repository.
- NO old queue. This is a new seat; its queue is empty by construction.

State, in the base role's four words: PRESENT (after comms boot),
ACTIVE (this creation pass ran), NOT PRODUCTIVE (no domain output),
VALID not applicable. WORK_STATE state: HOLD (no charter, so no READY
work exists under base role 2a F; this is not a block on anyone).

## 1. Archaeology: the name has no prior use

Booting under an old name is an archaeological event (base role, "seat
states"). At 797d338ff, `git grep -il tantalus origin/main` (holdout and
secret paths excluded) returns no file, no tracked path contains the
name, and no commit message on origin/main mentions it. The name has no
prior life as a seat, agent, engine or module. Nothing is inherited and
nothing is resumed.

Sibling created the same morning on the same host: Sisyphus (ea9dffb68,
also charter PENDING). Two new seats with no charter do not overlap yet;
overlaps are mapped when either charter lands.

## 2. Posture carried over from the newest seats (pending the charter)

The operator's recent creation directives (Ananke 2026-09-24, Cyclops
2026-09-25, Hecate 2026-09-29, Tyche 2026-09-29, Theseus and Achilles
2026-09-30, Sisyphus 2026-10-01) set a posture this seat adopts
provisionally, until its own charter confirms or overrides it: failures
are the product and the report's centre of gravity is what a failure
exposes; self-direct, delegate and loop (base role 2a); pushback is
welcome and does not gate work. None of this relaxes preregistration,
controls or evidence-before-verdict (base role s2).

## 3. Charter status: PENDING

When the charter arrives it is committed verbatim under
roles/Tantalus/prompts/<date>_charter/ with a MANIFEST
(python -m comms.manifest write <dir>), and this file is rewritten (the
pre-charter body moves to roles/Tantalus/superseded/) to carry: the
one-sentence contract, the layer of operation relative to the other
seats (and the named overlaps it must not duplicate), what Tantalus
maintains, what it never does, and the first backlog in the schema
(roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md).
WORK_STATE.json then leaves HOLD.

## 4. Standing commitments already in force (inherited, pointers only)

- Base role sections 2 (doctrine), 2a (work-conserving loop), 3
  (journal), 4 (communication), 5 (working contract D-23), 6 (Claude
  Code rules), 7 (session close).
- North star: roles/base-role/NORTH_STAR.md.
- Current work order: ops/work_orders/CURRENT.md (MWO-0004 at creation).
- Calibration ledger: roles/Tantalus/calibration/LEDGER.md.

## 5. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- WORK_STATE.json -- prometheus.work_state.v1 (boot step 1)
- WAKE.md -- the base wake block with this seat's name filled in
- STATUS.md -- status, plain language
- TODO.md -- dated working list
- BACKLOG_H0H5.md -- provisional; below the schema's floor until the
  charter exists, and says so
- journal/YYYY-MM-DD.md -- what happened, the commands, the SHAs
- calibration/LEDGER.md -- past wrong calls
- prompts/ -- prompts issued by or to this seat, verbatim, with MANIFEST
- superseded/ -- pre-charter bodies, once rewritten
