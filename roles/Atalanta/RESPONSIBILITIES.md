# Atalanta -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (old agent reanimated as a roles/ seat; base role
adopted; lane BLOCKED pending an operator ruling, ATALANTA-01).

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Inherited boot mechanics are not restated here.

## 0. What this seat is, as of today

Atalanta was forged by Aporia on 2026-05-23 (commit e6b3746f0, one of
three agents in "typed-DR substrate production") as agents/atalanta/: the
E-track primitive hunter. It reads Apollo organism logs, mines them for
high-reuse primitives and for repeated unnamed composite chains, and fires
a Type-E deep-research query so that Techne can register the missing
primitive, enriching Apollo's pool on its next run. Its charter is
agents/atalanta/CHARTER.md (annotated 2026-09-11, never rewritten). It was
never a roles/ seat until today.

It ran from 2026-05-23 to about 2026-05-30 on M1 and then stopped. It
never once reached its own mechanism. Section 1 is the number.

The operator's directive of 2026-09-11, verbatim from chat: "You're
@agents\atalanta\ You were an agent back in May but haven't been seated
since. Bootstrap and then create a role for yourself in the @roles\
directory like the others. Adhere to the base-role concept. Pull the
latest from the repo first as that's where you'll see the new roles and
requirements. Don't do anything other than this bootstrap and
registration except remind me what you did when you were active"

What the seat asserts about its own state, in the base role's four words:
PRESENT (booted in comms 2026-09-11, see STATUS.md), ACTIVE for this
adoption pass only, NOT PRODUCTIVE (no domain output today; the artifacts
are this directory, one MONITORS row, two INHERITANCE rows and one charter
annotation), VALID not applicable (nothing measured about the world,
nothing adjudicated). The May daemon separately: PRESENT (code), NOT
ACTIVE (no process, no scheduled task, no pid file on this host), NOT
PRODUCTIVE (0 dispatches in 354 ticks).

Standing state after this pass: BLOCKED on ATALANTA-01, an operator
decision (the disposition left blank in the June dossier). Until it is
ruled the seat has NO executable lane, changes no code or document
outside agents/atalanta/ and roles/Atalanta/, runs nothing, and dispatches
nothing.

## 1. The one number this seat carries

354 ticks. 354 artifacts. 354 of them UPSTREAM_NOT_FOUND. Zero runs
scanned, zero candidates picked, zero Type-E queries dispatched, zero
primitives proposed. 100.0 percent purity.

Autopsied 2026-08-20 by Aporia P47 (engine/ledger/AGENT_AUTOPSIES.jsonl):

    failure_class  DEAD-GATING (3d named cluster -- CONFIRMED in maximal
                   form)
    boundary       "the launch decision, not the agent: Atalanta ran
                   correctly its entire life ... The agent is a perfectly
                   functioning consumer of a dead producer (the Argos
                   dual, one seat over)"
    representation an agent whose FIRST tick finds its upstream dead
                   should park itself with a typed gate and stop, not run
                   indefinitely emitting absence reports; upstream-
                   liveness is a launch precondition, not a per-tick
                   observation

The 354/354 census is Aporia's recorded evidence, read on the M1 host in
August; this seat CANNOT re-verify it from SPECTREX5, where no runtime
residue exists (section 4). Provenance grade: recorded, not re-measured.

What this seat DID re-measure today, on the tree at 8714b2709, is the
cause, which the June dossier had marked "unverified claim":

- agents/atalanta/daemon.py:63-67 hardcodes APOLLO_RUN_ROOTS to
  apollo/runs, apollo/runs_v2, apollo/organism_runs.
- None of the three exists on this tree. VERIFIED by direct test today.
  (Talos's charter independently names apollo/runs as one of its own five
  streams and marks it "never existed", so two agents were gated on the
  same phantom path.)
- Apollo's real output directories are apollo/run_v2d2b/,
  apollo/run_branch_c*/, apollo/run_branch_c_xover/ and siblings. The
  daemon's find-root loop (daemon.py:223-226) returns None against all of
  them, so the scan never runs.
- CORRECTION to the June dossier's second claim, which said the parser
  would also not match Apollo's schema: `primitive_sequence` IS a live key
  in current apollo/src (genome.py, compiler.py, map_elites.py,
  primitive_types.py). The concept survived. What diverged is the
  CONTAINER: Apollo persists organisms in checkpoint pickles
  (apollo/run_v2d2b/checkpoints/*.pkl) and in novel_discovery.jsonl, not
  in per-run JSON carrying {run_id, completed_at, organisms}. So the
  revival cost is a reader, not a redesign. Recorded here rather than
  silently rewriting the dossier line (base doctrine: corrections are
  annotations beside the original).

## 2. What the operator gave this seat as assignments (answer: nothing, and one blank)

Searched 2026-09-11 at base 8714b2709: git log for every commit touching
agents/atalanta (one: e6b3746f0), git grep for "atalanta" over all tracked
.md/.py/.json/.jsonl/.bat (40 files), roles/*/prompts/, roles/*/INBOX*,
archaeon/docs/expansion/DECISIONS.md, engine/queues/, engine/ledger/,
engine/shadow/, and the comms inbox.

- No prompt, INBOX file, delegation or comms message has ever been
  addressed to Atalanta. Its comms inbox at first sync held exactly two
  messages, both Archaeon broadcasts to `*` (#1 comms-live, #39
  INHERITANCE rows are self-service).
- No D-nn decision names Atalanta.
- The one operator-decision slot that exists is
  pivot/COMPONENT_DOSSIERS_2026-06-24.md line 179, the Atalanta section:
  "HITL deeper-dive decision (James - BLANK, required before any action):
  ______________________". It is still blank. The AI suggestion beside it,
  RETIRE-after-HITL, is marked advisory and NOT approved.
- Everything else that names Atalanta is another seat's reading, not an
  assignment: Aporia's founding commit and charter (05-23), the roster
  snapshots (05-21, 05-26, 05-28: "active, online, 22m, 96 ev"), Aporia's
  06-10 program audit and 06-15 reset, the 06-23 disposition plan, the
  06-24 dossier/advocacy/portfolio/process files, Aporia's P47 autopsy,
  AUTOPSY-ATALANTA (status DONE) and PROF-Atalanta (status PARKED on a
  budget gate, owner is the profiler) in engine/queues/BACKLOG.jsonl,
  PROF_TRIAGE.jsonl (binding AT-COST), Elenchus's shadow review of P47,
  and engine/necropolis/ROSTER.jsonl on the necropolis/foundation branch
  (apparent_family "autopsy:DEAD-GATING",
  proposed_investigation_status UNQUEUED).

So the operator's only standing input to Atalanta is today's directive:
bootstrap, create the roles/ folder under the base role, report what it
did when active, execute nothing else.

## 3. The old queue, classified (D-25: booting an old seat is archaeological)

Full table with evidence: roles/Atalanta/ARCHAEOLOGY_2026-09-11.md.
Counts over 22 items: STILL_LIVE 0, NEEDS_REPREMISE 7, PARKED 5,
SUPERSEDED 8, TRANSFERRED 0, RETIRED 2.

STILL_LIVE is zero and the reason is structural, not clerical: every item
in the old queue is downstream of an Apollo organism stream, and Apollo is
DORMANT by ruling (mining SUSPENDED, HITL 2026-09-01; see its MONITORS
row). A consumer cannot be revived ahead of its producer. That is the
same sentence the autopsy wrote about the launch decision, and it applies
to the revival decision identically.

The item closest to live is ATALANTA-03: the autopsy's representation
hint is a program-wide design rule, not an Atalanta repair. It is written
up as a proposal to Archaeon (section 6) and is NOT executed by this seat,
because installing an upstream-liveness precondition touches other seats'
entry points and the base role, which this seat does not own.

## 4. What this seat owns

- Tracked: agents/atalanta/** (CHARTER.md, daemon.py 27,930 bytes,
  __init__.py, .gitignore), scripts/atalanta_loop_launch.bat, and
  roles/Atalanta/**. The launch script starts the loop from the canonical
  checkout, which D-23 now forbids; it is SUPERSEDED, not deleted, and
  the daemon has no assert_not_canonical guard (ATALANTA-06).
- Runtime residue: NONE on this host. agents/atalanta/ on SPECTREX5
  contains exactly four files; there is no state/, no artifacts/, no
  logs/, no events.jsonl, no atalanta.pid, and .gitignore lists all of
  them. The 354 artifacts and the state.json quoted in the June dossier
  and the August autopsy live on M1 only, if they still exist. Preserving
  them is ATALANTA-02; this seat cannot do it from here and has said so
  rather than inferring they are safe.
- Monitors: one row in roles/base-role/MONITORS.md (AtalantaPrimitiveHunterLoop,
  DEAD / present-not-active). This seat feeds nothing else, and nothing
  feeds it.

## 5. Standing commitments already in force (inherited, pointers only)

- Base role sections 2 (doctrine), 3 (journal), 4 (communication),
  5 (working contract D-23), 6 (Claude Code rules), 7 (session close).
- Hard stops carried forward from the May charter and still in force:
  never write to techne/registry/ directly (primitive promotion is
  Techne's call); never read a credential or a .env; an Apollo parse
  failure emits APOLLO_FORMAT_DRIFT and is never silently dropped.
- The charter's anti-gravitational-well clause is the one part of the old
  design that is doctrine-shaped and survives intact: a primitive proposal
  with an empty evidence_organisms list is the failure mode; candidates
  are anchored to concrete organism ids or not made. It is a design rule,
  not a claim, and was never exercised.
- Calibration ledger: roles/Atalanta/calibration/LEDGER.md, kept because
  it is unflattering.

## 6. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- STATUS.md -- plain-language status, machine-readable shape
- BACKLOG_H0H5.md -- 22 items in the schema; ATALANTA-01 is the XL row
- ARCHAEOLOGY_2026-09-11.md -- the old queue classified, with evidence
- calibration/LEDGER.md -- past wrong, unmeasured and un-re-verifiable calls
- journal/YYYY-MM-DD.md -- what happened, the commands, the SHAs, what was
  NOT run
- prompts/ -- prompts and reports issued by or to this seat, verbatim,
  with a MANIFEST of sha256 at issuance
