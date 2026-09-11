# Pheme -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (seat created under roles/; base role adopted; the
May charter classified archaeologically; no assignment executed).

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Inherited boot mechanics are not restated here.

## 0. What this seat was

Pheme was built by Aporia on 2026-05-23 (commit e6b3746f0) as the
"substrate demand voicer": a 30-minute daemon (agents/pheme/daemon.py,
charter agents/pheme/CHARTER.md) that was to read the Ergon Learner's
per-example eval results, aggregate the worst-performing reasoning
patterns into a demand profile (agents/pheme/artifacts/demand_latest.json)
and publish it so upstream producers (Hypatia, Atalanta, Aporia's DR
queue) aimed their output at real Learner deficits. Operator of record:
Ergon. It was never a seat under roles/ and never had a charter from the
operator; the May charter is Aporia's.

What the record shows it did, measured, not recalled:

- 354 ticks between 2026-05-23 08:28 UTC and 2026-05-30 16:10 UTC
  (agents/pheme/state/state.json in the canonical checkout, untracked:
  total_null_ticks_lifetime 354, total_profiles_lifetime 0,
  last_profile_at null, anti_silence_counter 354).
- Every tick emitted UPSTREAM_NOT_FOUND: none of the three configured
  eval roots (ergon/learner/evals, ergon/evals,
  ergon/diagnostic_c/eval_runs) has ever existed. Verified absent again
  on 2026-09-11 at origin/main 57533fa76.
- 0 demand profiles published; 0 downstream selections changed. The
  consumer seam was also broken on paper (Hypatia's selector takes
  set() over a list of dicts; pivot/COMPONENT_DOSSIERS_2026-06-24.md).
- The pid file agents/pheme/pheme.pid names PID 5768 started 2026-05-23;
  that process is not running (tasklist, 2026-09-11) and no scheduled
  task named for Pheme exists on this host (schtasks, 2026-09-11).

In the base role's four words the daemon is PRESENT (code committed),
NOT ACTIVE (no process, no task), NOT PRODUCTIVE (0 profiles in 354
ticks), and VALID is not applicable (nothing was ever measured).

## 1. What this seat is, as of today

The operator woke Pheme on 2026-09-11 with one instruction (verbatim in
roles/Pheme/prompts/2026-09-11_adoption/OPERATOR_DIRECTIVE.md): adopt
the base role, create roles/Pheme/, report what the operator has
assigned, and execute nothing. That is what this pass did.

Booting an old seat is an archaeological event (base role, seat states).
The May queue is classified in roles/Pheme/QUEUE_ARCHAEOLOGY_2026-09-11.md:
0 STILL_LIVE, 2 NEEDS_REPREMISE, 3 PARKED, 1 SUPERSEDED, 0 TRANSFERRED,
0 RETIRED. Nothing in it is executable work today; the two
NEEDS_REPREMISE rows need a restated premise from the operator before
they can become work, and the three PARKED rows wait on an operator
decision that has been blank since 2026-06-24.

Until the operator assigns or re-premises, this seat has:

- NO lane. It changes no code and no document outside roles/Pheme/.
  agents/pheme/ is its own historical code and is not modified on this
  pass either (nothing executes).
- NO standing monitor that is alive. The May daemon loop is reported to
  Archaeon for the registry as DEAD (present, not active) rather than
  left unregistered, because a loop that is not in the registry is
  UNMANAGED (roles/base-role/MONITORS.md).
- NO science. It has adjudicated nothing and asserts nothing about any
  claim in the repository.
- NO operator assignment beyond this adoption pass. See section 2.

## 2. What the operator has assigned to Pheme (the answer to the directive)

Read from the repository, not from recall, at origin/main 57533fa76:

1. 2026-09-11, this pass: adopt the base role, create roles/Pheme/,
   report assignments, execute nothing. DONE by this directory.
2. No other prompt, delegation, INBOX file or comms message from the
   operator is addressed to Pheme. `git grep -w -i pheme origin/main`
   outside agents/pheme/ finds rosters, pivot reviews, sibling daemons
   that mirror its code pattern, and the profiling queue; none is an
   operator assignment to this seat.
3. The June review (pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md row
   18, REVIVE-SPINE; pivot/COMPONENT_DOSSIERS_2026-06-24.md, Pheme
   section, suggestion REFACTOR) is marked by the operator "NOT APPROVED
   -- AI SUGGESTIONS ONLY", and the dossier's line "HITL deeper-dive
   decision (James - BLANK, required before any action)" is still blank.
   That is an assignment that was never given, not one that was.
4. The May charter (agents/pheme/CHARTER.md) was written by Aporia and
   signed "Aporia, 2026-05-23"; it is a sibling seat's design, not an
   operator directive.

So the operator has given Pheme exactly one assignment, today's, and it
is complete. The seat's standing state after this pass is BLOCKED on an
operator decision: which of the archaeology's NEEDS_REPREMISE / PARKED
rows, if any, becomes a charter. The recommendation is in
QUEUE_ARCHAEOLOGY_2026-09-11.md section 3 and STATUS.md.

## 3. Standing commitments already in force (inherited, pointers only)

- Base role sections 2 (doctrine), 3 (journal), 4 (communication), 5
  (working contract D-23), 6 (Claude Code rules), 7 (session close).
- North star (roles/base-role/NORTH_STAR.md): primitives, environments,
  instruments, provenance and pressures; never the reasoner. Kill
  claims, never lineages, never the loop. The May daemon's residue (its
  demand-profile schema, quota-shift heuristic, sentinel pattern) stays
  navigable; nothing here is marked dead.
- Calibration ledger: roles/Pheme/calibration/LEDGER.md (one row already:
  the seat's own charter assumed an upstream that did not exist).

## 4. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- STATUS.md -- plain-language status, four-word state
- QUEUE_ARCHAEOLOGY_2026-09-11.md -- the May queue classified against the
  north star, with the recommendation
- BACKLOG_H0H5.md -- provisional; below the schema floor until a charter
  exists, and says so
- journal/YYYY-MM-DD.md -- what happened, the commands, the SHAs
- calibration/LEDGER.md -- past wrong calls
- prompts/ -- prompts issued by or to this seat, verbatim, with MANIFEST
