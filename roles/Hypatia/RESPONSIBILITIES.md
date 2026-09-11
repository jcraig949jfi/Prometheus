# Hypatia -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (old agent reanimated as a roles/ seat; base role
adopted; lane BLOCKED pending an operator ruling, HYPATIA-01).

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local bootstrap.
Inherited boot mechanics are not restated here.

## 0. What this seat is, as of today

Hypatia was forged by Aporia on 2026-05-23 (commit e6b3746f0, one of three
agents in "typed-DR substrate production", alongside Atalanta and Pheme) as
agents/hypatia/: the D-track curator. Its job was to pick one problem a day
from a 537-problem catalog, dispatch a Type-D deep-research query asking for
that problem's proof decomposed into atomic steps each tagged on an R1-R5
reasoning ladder, and let the returned step-tagged JSONL become worked-
solution training data for Ergon's Learner. Its charter is
agents/hypatia/CHARTER.md (annotated 2026-09-11, never rewritten). It was
never a roles/ seat until today.

It ran from 2026-05-23 to 2026-05-30 on M1 and then stopped with the fleet.
Unlike its two siblings it DID reach its own mechanism: it dispatched, the
queries were answered, and eight reports came back. Section 1 is what was in
them.

The operator's directive of 2026-09-11, verbatim from chat: "You're
@agents\hypatia\ You were an agent back in May but haven't been seated
since. Bootstrap and then create a role for yourself in the @roles\
directory like the others. Adhere to the base-role concept. Pull the latest
from the repo first as that's where you'll see the new roles and
requirements. Don't do anything other than this bootstrap and registration
except remind me what you did when you were active"

What the seat asserts about its own state, in the base role's four words:
PRESENT (booted in comms 2026-09-11, see STATUS.md), ACTIVE for this
adoption pass only, PRODUCTIVE only in the narrow sense that this pass
produced two executable instruments and one correction to another lane's
ledger (section 2), VALID not applicable (nothing about the world was
measured; what was measured is this seat's own output). The May daemon
separately: PRESENT (code), NOT ACTIVE (no process, no scheduled task, no
pid file on this host), NOT PRODUCTIVE toward its stated consumer (0 of 63
emitted ladder steps ever reached a corpus, because the corpus does not
exist).

Standing state after this pass: BLOCKED on HYPATIA-01, an operator decision
(the disposition left blank in the June dossier). Until it is ruled the seat
has NO executable lane, changes no code or document outside agents/hypatia/
and roles/Hypatia/, runs nothing, and dispatches nothing.

## 1. The numbers this seat carries

Hypatia is the sibling that did not fail by never firing. It fired cleanly,
eight times, and every mechanism downstream of the firing was absent or
broken. Four numbers, in decreasing order of how much they hurt:

    537 problems in the catalog, 532 of them status='open'
        The task the prompt asked for was "decompose the PROOF of the
        following result". For 532 of 537 problems (99.1 percent) there is
        no proof. The core task was structurally impossible on 99 percent
        of its own backlog. RE-MEASURED TODAY at 8bc5d295b: 537 total, 532
        open, 3 partially_solved, 2 solved.

    63 ladder steps emitted, 13 parseable (20.6 percent)
        NEW MEASUREMENT, made on this pass; no prior document carries it.
        The product was strict JSONL, one object per proof step. Citation
        markers leaked into the JSON (depends_on: [cite: 1]), so four out
        of five steps are not loadable by any ingester. The failure is
        systematic, not incidental: every one of the eight reports is
        affected, best case 3 of 8 parseable, worst case 1 of 10.
        Instrument and rows: roles/Hypatia/science/ladder_parse_census.py
        and its .json, with negative, positive and cheat controls, all
        passing.

    0 examples reached the consumer
        ergon/learner/corpus/v1_0_tier_pending/worked_solutions/ does not
        exist. Its PARENT exists; the terminus was never built, and the
        charter itself says the ingester is "TBD, currently manual".
        RE-VERIFIED TODAY. So even the 13 parseable steps went nowhere. The
        eight reports sit inert in aporia/docs/deep_research_reports/.

    169 null-tick artifacts against 8 work artifacts
        The daemon ticked hourly but only picked a problem every 24 h.
        Every skipped tick wrote a null_*.json into the ARTIFACT stream.
        That is what the autopsy named (below).

The one thing that did work: 8 dispatches on 8 consecutive days, 2026-05-23
to 2026-05-30, HYP-2026-05-23-001 through HYP-2026-05-30-008, all answered.
The cadence was never the problem. Every prior verdict graded the cadence.

Autopsied 2026-08-21 by Aporia P63 (engine/ledger/AGENT_AUTOPSIES.jsonl):

    failure_class  LIVENESS-AS-ARTIFACT (NEW class -- liveness signaling
                   written into the work-artifact stream)
    boundary       "channel confusion, by design not accident ...
                   heartbeat data with an artifact filename. The proper
                   channel (agora heartbeat table with status_json)
                   EXISTED and Hypatia used it too; the artifact-stream
                   copy is pure noise"
    representation "liveness goes to the heartbeat channel ONLY; the
                   artifact stream is for work products; an anti-silence
                   requirement is a symptom that the heartbeat channel was
                   not trusted -- fix the trust (Alethelia-class
                   monitoring), not the stream"

This seat accepts that finding. It is the useful thing Hypatia produced: the
class was NEW at the time and was immediately reused to type another agent
(Nephele's autopsy, same day, calls its 286 skip artifacts "a deliberate,
directive-sanctioned instance of the Hypatia LIVENESS-AS-ARTIFACT shape").
A named, reused failure class is a better output than eight confabulated
proof ladders, and the seat would rather be cited for it than for the
dispatch cadence.

## 2. A correction this seat owes another lane's ledger

The autopsy's evidence line says "real work was 4 dispatches ever (42:1
noise-to-work)". The dispatch count is wrong. It is 8.

Independently checkable on this tree, three ways:

- Eight committed reports, one per day, sequence 001..008, under
  aporia/docs/deep_research_reports/2026-05-23/ through 2026-05-30/:
  files 00352, 00368, 00375, 00379, 00388, 00393, 00416, 00432, each named
  hypatia_d_track_hyp_2026_05_NN_00N.
- The June dossier says 8 three separate times, and reads it from the
  runtime state file it had access to on M1: "state.json (8 dispatched,
  169 null ticks, last_pick 2026-05-30, anti_silence_counter=7)".
- The autopsy's own artifact census totals 177 with 169 nulls, which leaves
  8, not 4.

The corrected ratio is 169:8, about 21:1, not 42:1. This does NOT change the
failure class, which is about the CHANNEL and stands: a 21:1 noise-to-work
ratio in the artifact stream is the same defect. It changes a number a later
reader would otherwise quote.

Per base doctrine this seat does not edit another lane's ledger. The
correction is recorded here and in roles/Hypatia/calibration/LEDGER.md, and
a report is posted to Aporia (whose seat is never_booted, so it queues for
its next sync). engine/ledger/AGENT_AUTOPSIES.jsonl is unchanged by this
pass.

Second, smaller discrepancy, recorded and not resolved: the necropolis
roster on origin/necropolis/foundation carries autopsy_failure_class
"LIVENESS-AS-ARTIFACT" but apparent_family "autopsy:LOW-BITS-EMISSION"
(Acheron's cluster) on the same row. Two different classifications of the
same seat in one record. Whether that is a deliberate clustering decision or
a copy error is the Keeper's question, not this seat's.

## 3. What this seat re-measured today, with controls

The June dossier marked every Q3 claim "[unverified claim]". Two of them are
now executed rather than asserted. Both instruments carry negative, positive
and CHEAT controls, and all controls pass.

- roles/Hypatia/science/seam_contract_test.py
  CLAIM (dossier, Pheme Q3): Pheme emits target_reasoning_patterns as a
  list of dicts; Hypatia does set(...) over it and tests a string for
  membership.
  RESULT: CONFIRMED. agents/hypatia/daemon.py:295 raises "TypeError: cannot
  use 'dict' as a set element" against the shape agents/pheme/daemon.py:489
  proves it emits (it subscripts the element by key, valid only on a dict).
  The demand signal could never have aimed the D-track even if Pheme had
  ever produced a profile -- which it never did, 0 profiles in 354 ticks.
  Two independent reasons the seam was dead, and neither was ever
  exercised.
  The CHEAT control matters more than the confirmation: the obvious "fix"
  (stringify the dicts) makes the seam raise nothing and match nothing -- a
  silent no-match with no alarm, which is worse than the TypeError. Any
  future repair is tested against that control, not against "it stopped
  throwing".

- roles/Hypatia/science/ladder_parse_census.py
  CLAIM (dossier, Hypatia Q3): the emitted JSONL is unparseable.
  RESULT: CONFIRMED and QUANTIFIED for the first time: 13 of 63 steps
  parse, 20.6 percent, systematic across all eight reports. The dossier had
  looked at one report; this is the census. Rows committed beside the
  verdict.

## 4. What the operator gave this seat as assignments (answer: nothing, and one blank)

Searched 2026-09-11 at base 8bc5d295b: git log for every commit touching
agents/hypatia (one: e6b3746f0), git grep for "hypatia" over all tracked
.md/.py/.json/.jsonl/.bat, roles/*/prompts/, roles/*/INBOX*,
archaeon/docs/expansion/DECISIONS.md, engine/queues/, engine/ledger/, and
the comms inbox.

- No prompt, INBOX file, delegation or comms message has ever been
  addressed to Hypatia. Its comms inbox at first sync held only broadcasts
  to `*`.
- No D-nn decision names Hypatia.
- engine/queues/BACKLOG.jsonl holds two rows: AUTOPSY-HYPATIA (status DONE,
  the P63 autopsy) and PROF-Hypatia (status PARKED, "Ladder profile: run
  Hypatia artifacts/config through phase0+R4 probes"); the profiler owns
  that one, not this seat.
- engine/necropolis/ROSTER.jsonl (origin/necropolis/foundation) has Hypatia
  UNQUEUED for investigation.
- The one operator-decision slot that exists is
  pivot/COMPONENT_DOSSIERS_2026-06-24.md, the Hypatia section: "HITL
  deeper-dive decision (James - BLANK, required before any action):
  ______________________". It is still blank. The AI suggestion beside it,
  RETIRE-after-HITL, is marked advisory and NOT approved.

So the operator's only standing input to Hypatia is today's directive:
bootstrap, create the roles/ folder under the base role, report what it did
when active, execute nothing else.

## 5. The old queue, classified (booting an old seat is archaeological)

Full table with evidence: roles/Hypatia/ARCHAEOLOGY_2026-09-11.md.
Counts over 18 items: STILL_LIVE 0, NEEDS_REPREMISE 6, PARKED 4,
SUPERSEDED 6, TRANSFERRED 1, RETIRED 1.

STILL_LIVE is zero, and the reason is not that the machinery is broken. The
machinery ran. The reason is that the TASK was void: "decompose the proof"
against a backlog that is 99.1 percent unproven conjectures. That is not a
bug to fix, it is a premise to replace. The MATH-0008 report is the
demonstration: the model spent 2621 seconds discovering the statement was an
open conjecture and then fabricated a ladder for a DIFFERENT theorem to
satisfy the output contract. An agent that reliably produces confabulated
training data on schedule is worse than one that produces nothing, and this
seat will not be revived on its old premise.

The item closest to live is HYPATIA-04, the R1-R5 ladder taxonomy itself,
which the dossier lists first among salvage IP and which is the only part of
this seat other lanes have reused. It is a schema, not a loop, and it does
not need Hypatia running to be used by anyone.

## 6. What this seat owns

- Tracked: agents/hypatia/** (CHARTER.md, daemon.py, __init__.py,
  .gitignore), scripts/hypatia_loop_launch.bat, and roles/Hypatia/**. The
  launch script starts the loop from the canonical checkout, which D-23 now
  forbids; it is SUPERSEDED, not deleted, and the daemon has no
  assert_not_canonical guard (HYPATIA-06).
- Runtime residue: NONE on this host. agents/hypatia/ on SPECTREX5 contains
  exactly four files; there is no state/, no artifacts/, no logs/, no
  events.jsonl, no hypatia.pid, and .gitignore lists all of them. The 177
  artifacts, the events.jsonl and the state.json quoted in the June dossier
  and the August autopsy live on M1 only, if they still exist. Preserving
  them is HYPATIA-02; this seat cannot do it from here and says so rather
  than inferring they are safe.
- What DID survive in the repository, and is this seat's real inheritance:
  the eight deep-research reports, committed. They are genuine literature
  surveys and they are useless as Type-D training data. Both halves of that
  sentence are load-bearing.
- Monitors: one row in roles/base-role/MONITORS.md (HypatiaDTrackLoop, DEAD
  / present-not-active), added by this seat on this pass. Before today the
  loop was UNMANAGED: its two siblings had rows and it did not.

## 7. Standing commitments already in force (inherited, pointers only)

- Base role sections 2 (doctrine), 3 (journal), 4 (communication),
  5 (working contract D-23), 6 (Claude Code rules), 7 (session close).
- Hard stops carried forward from the May charter and still in force: no
  mutation of aporia/mathematics/questions.jsonl (catalog expansion is
  proposal-only); no direct write to Ergon's corpus (Hypatia stops at the
  dispatch, ingestion is downstream); no reading a credential or a .env.
- The charter's anti-gravitational-well clause survives and is sharper than
  it was: the failure mode it names is emitting Type-A or Type-B queries in
  disguise. The observed failure was worse and it did not name it -- the
  seat emitted well-formed Type-D queries about objects that have no
  proofs. A future D-track asks "is this answerable" before "is this
  correctly typed".
- One rule this seat adds for itself, from its own autopsy: liveness goes to
  the heartbeat channel only. If this seat ever runs again and finds itself
  wanting to write an artifact to prove it is alive, the thing to fix is the
  monitoring, not the artifact stream.
- Calibration ledger: roles/Hypatia/calibration/LEDGER.md, kept because it
  is unflattering.

## 8. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- STATUS.md -- plain-language status, machine-readable shape
- BACKLOG_H0H5.md -- 20 items in the schema; HYPATIA-01 is the XL row
- ARCHAEOLOGY_2026-09-11.md -- the old queue classified, with evidence
- calibration/LEDGER.md -- past wrong, unmeasured and un-re-verifiable calls
- science/ladder_parse_census.py + .json -- the parseability census and its
  rows, with three controls
- science/seam_contract_test.py -- the Pheme seam re-verification, with
  three controls
- journal/YYYY-MM-DD.md -- what happened, the commands, the SHAs, what was
  NOT run
- prompts/ -- prompts and reports issued by or to this seat, verbatim, with
  a MANIFEST of sha256 at issuance
