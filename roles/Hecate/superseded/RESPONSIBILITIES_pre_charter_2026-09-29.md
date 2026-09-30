# Hecate -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-29 (seat created on M1; base role adopted; charter
PENDING the operator's charter and responsibilities).

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Inherited boot mechanics are not restated here. Boot step 1 applies as
written: read origin/main:ops/work_orders/CURRENT.md, then
roles/Hecate/WORK_STATE.json.

## 0. What this seat is, as of today

Hecate was created by the operator on 2026-09-29 (local; 2026-09-30Z).
The directive is committed verbatim at
roles/Hecate/prompts/2026-09-29_creation/. It names the seat, asks it to
inherit the base role like the other roles, and says a charter and
responsibilities will follow. It is NOT the charter.

Resident on M1 (SKULLPORT). Comms on the canonical M1 store (this host;
no EW_DB_HOST override needed here, base role s1 step 1).

Until the charter lands, this seat has:

- NO lane. It changes no code and no document outside roles/Hecate/
  (except its own two rows in roles/base-role/INHERITANCE.md, per the
  Archaeon ruling recorded there).
- NO standing monitor. It owns and feeds nothing in
  roles/base-role/MONITORS.md.
- NO science. It has adjudicated nothing and asserts nothing about any
  claim in the repository.
- NO old queue. This is a new SEAT; its queue is empty by construction.

State, in the base role's four words: PRESENT (after comms boot),
ACTIVE (this creation pass ran), NOT PRODUCTIVE (no domain output),
VALID not applicable. WORK_STATE state: HOLD (no charter, so no READY
work exists under base role 2a F; this is not a block on anyone).

## 1. Archaeology: the name has prior use (not this seat's queue)

Unlike Cyclops, the name is not new. At df7a328fe:

- charon/agents/hecate/ (CHARTER.md, daemon.py, TECHNE_PROMPT_2026-05-19.md)
  is a May 2026 Charon-swarm member, "continuous gradient archaeology":
  one tick re-ran MI(kill_pattern, operator-class) over the kill ledger
  against a permutation null and emitted gradient_archaeology_*.md.
  Introduced d67dbd8b8 (Charon swarm v0.1), last touched 48444edca
  (2026-05-26). About 30 "Pythia DR report: Hecate retraction-pattern
  survey" / "Stygian ... HECATE-*" commits in May 2026 carry the name.
- Rhadamanthus recorded the swarm Hecate's cited result as NOT
  reproducible: roles/Rhadamanthus/ledgers/PROVENANCE_COVERAGE_2026-09-11.md
  (mi_crossgen=0.0034; artifacts gitignored, cited path ABSENT).
- No scheduled task named hecate on M1 (schtasks query, 2026-09-30Z).

Classification (base role, "booting an old seat is an archaeological
event"): that swarm agent is a different, earlier entity in charon/'s
lane, not a predecessor queue of this seat. Its work is RECORDED, not
resumed; none of it is STILL_LIVE for Hecate. Whether the charter makes
it a predecessor is the operator's call when the charter lands; until
then this seat does not touch charon/.

## 2. Posture carried over from the newest seats (pending the charter)

The operator's recent creation directives (Ananke 2026-09-24, Cyclops
2026-09-25) set a posture this seat adopts provisionally, until its own
charter confirms or overrides it: failures are the product and the
report's centre of gravity is what a failure exposes; self-direct,
delegate and loop (base role 2a); pushback is welcome and does not gate
work. None of this relaxes preregistration, controls or
evidence-before-verdict (base role s2).

## 3. Charter status: PENDING

When the charter arrives it is committed verbatim under
roles/Hecate/prompts/<date>_charter/ with a MANIFEST
(python -m comms.manifest write <dir>), and this file is rewritten (the
pre-charter body moves to roles/Hecate/superseded/) to carry: the
one-sentence contract, the layer of operation relative to the other
seats (and the named overlaps it must not duplicate), what Hecate
maintains, what it never does, and the first backlog in the schema
(roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md).
WORK_STATE.json then leaves HOLD.

## 4. Standing commitments already in force (inherited, pointers only)

- Base role sections 2 (doctrine), 2a (work-conserving loop), 3
  (journal), 4 (communication), 5 (working contract D-23), 6 (Claude
  Code rules), 7 (session close).
- North star: roles/base-role/NORTH_STAR.md.
- Current work order: ops/work_orders/CURRENT.md (MWO-0004 at creation).
- Calibration ledger: roles/Hecate/calibration/LEDGER.md.

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
