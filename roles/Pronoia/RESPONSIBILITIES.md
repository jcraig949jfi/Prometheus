# Pronoia -- seat file (entry file for this seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (seat created under roles/; base role adopted; the
March-April queue and the May-September queue classified
archaeologically; nothing executed, no loop started, no loop stopped, no
dashboard written, no email sent).

Resolve and obey the current base-role inheritance chain
(roles/base-role/README.md and the files it lists, then
aporia/doctrine/critical_memories.md) BEFORE this seat's local
bootstrap. Inherited boot mechanics are not restated here.

Everything below was read from the repository, the host and the
canonical Postgres at base SHA
363120e08665af062d40810183624fa23ed19698, from the worktree
Prometheus-worktrees/pronoia-base-role on the M2 host (SPECTREX5), on
2026-09-11. Nothing here is recalled. Where a number is a measurement,
the command that produced it is in journal/2026-09-11.md.

## 0. What this seat was -- TWO ERAS UNDER ONE NAME

The single most important fact for anyone reading this seat: "Pronoia"
names two different programs, four months apart, and the repository
record conflates them. Era 1 is dead and deleted. Era 2 is RUNNING
RIGHT NOW and is the subject of this pass's one substantive finding.

### Era 1 -- the Forethought Orchestrator (2026-03-23 to 2026-04-01)

Created 2026-03-23 in commit eb17886fa ("agents: add Aletheia, Clymene,
Hermes, Pronoia + wire full pipeline"). Entry point pronoia.py at the
repository root, 872 lines. It was the single entry point for a serial
research-scanning pipeline:

    Eos -> Aletheia -> Skopos -> Metis -> Clymene -> Hermes
    then step 7 AUDIT, step 8 Titan-prompt generation, step 9 publish

Its own audit (step 7) is the part that belongs to this seat rather than
to the six agents it chained. That is what section 0.1 measures.

DELETED from the tree 2026-04-23 in 3b3c74bc0 ("Clean up repo for
external visibility"), in the same commit as 24 other root-level scripts,
and then EXPLICITLY GITIGNORED (.gitignore line 174, `/pronoia.py`).

PRESENT ON THIS HOST ANYWAY: D:\Prometheus\pronoia.py exists on M2
today, untracked and ignored, 32,165 bytes, mtime 2026-04-11. It is
absent from origin/main (`git cat-file -e origin/main:pronoia.py` ->
"exists on disk, but not in origin/main"). It is therefore invisible to
every seat that reads the tree and runnable by anyone with a shell on
this machine. roles/base-role/MONITORS.md is correct that pronoia.py is
not in the tree; it does not record that a runnable copy survives on
disk. That gap is registered as PRON-02 because of what the file does
when run -- see section 0.2.

### Era 2 -- the fleet-visibility loop (2026-05 to today, ALIVE)

scripts/intelligence_loop.py. Its own docstring line 3 reads
"Intelligence Loop -- Pronoia-orchestrator for the multi-machine
reporting pipeline". It keeps `agent:Pronoia` alive on the dashboard via
an Agora heartbeat thread plus a Postgres dual-write. Its last commit is
373d81469, 2026-05-23, titled "Pronoia: dual-write heartbeat to Postgres
(parity with Apollo/Hephaestus)".

It fires three sub-pipelines: hourly (portfolio_monitor.py refresh +
metis_portfolio.py brief), daily (send_brief_email.py), and a 60-second
heartbeat. It pushes docs/state.json and docs/portfolio_brief.md to main
on a four-hour cadence.

MISATTRIBUTION CORRECTED ON THIS PASS. roles/base-role/MONITORS.md
registers this loop as "Portfolio brief producer ... OWNER UNCLAIMED
(Hermes lineage code, May 2026)". The evidence says Pronoia: the file's
docstring, the heartbeat agent name, and the title of its last commit.
Hermes owns the delivery hop (send_brief_email.py) and explicitly
declined to own its input (HERMES-XL-2). This seat CLAIMS that row. The
Hermes annotation was not deleted; the row is annotated beside it, per
the base role's rule that corrections are annotations and never silent
rewrites.

## 0.1 What Era 1's audit actually measured, and what it did not

37 audit reports plus 5 health reports, 2026-03-23 to 2026-04-01, ten
days, all committed under agents/pronoia/logs/. About 40 auto-publish
commits to main in the same window.

THE HEADLINE NUMBER: 0 of 37 audits returned HEALTHY. 27 UNHEALTHY, 10
DEGRADED. A gate that never once returns one of its three values across
its entire operating life is not a gate; it is a constant with a
decorative switch statement.

Detector census, counted over all 37 audits:

    detector           declared in README        times it fired
    ---------------    ----------------------    --------------
    rate_limits        "429 / backoff"                       27
    api_errors         "timeouts, HTTP errors"               31
    zero_output        "agent produced <20 chars"             0
    knowledge_growth   "flat growth -> tune scanner"          0
    vram               "GPU >1GB -> leak"                    27

Four separate instrument failures are visible in that table, and each is
a named base-role defect written months LATER:

1. IT GRADED SELF-REPORTS, NOT PROPERTIES. run_audit() takes the
   captured stdout of each agent and runs regexes over it. It never
   asked whether Eos added a new item, whether the knowledge graph grew,
   or whether the brief differed from yesterday's. Base rule 2, "verify
   the property, never the label", is exactly this failure at the
   orchestration layer, written 2026-09-11 against evidence from three
   other seats. Pronoia is a dated specimen of it from March.

2. THE STATUS WORD WAS NEAR-CONSTANT BY CONSTRUCTION. A single "429"
   substring anywhere in any one of six agents' logs set has_high and
   forced UNHEALTHY for the whole cycle. With five external APIs on free
   tiers, that string was present nearly every cycle. The overall status
   carried almost no information about the pipeline and a great deal
   about the free-tier rate limits of arXiv and Groq.

3. zero_output FIRED 0 TIMES AND COULD NOT HAVE FIRED. This is the
   base role's "nothing fired" versus "nothing could have fired"
   distinction, and it resolves to the second. The check is
   `len(agent_log.strip()) < 20`. Every agent that ran printed a banner
   well over 20 characters; every agent that did NOT run was recorded
   SKIPPED and excluded from the loop before the check. The eligible
   count was approximately zero for all 37 runs. The detector was
   unreachable, not quiet, and nothing in the report said so.

4. knowledge_growth HAS NO PREDICATE AT ALL. The README promises "flat
   growth means scanner needs tuning". The code calls
   _query_entity_counts(), prints the counts, and compares nothing to
   anything. There is no previous value, no threshold, no finding path.
   It is a printer wearing a detector's name.

5. THE VRAM DETECTOR FIRED 27 TIMES AND MEASURED THE WRONG PROCESS.
   The intelligence pipeline is HTTP calls to five external APIs; it
   never allocates GPU memory. The check runs nvidia-smi after the
   pipeline and warns "possible leak" above 1 GB. Observed readings
   include 8909, 8789, 8658 and 8619 MiB -- the Ignis training runs that
   shared the box. So 73 percent of all audits carried a finding that
   attributed another program's memory to this one. A detector that
   fires often, looks like signal, and cannot be caused by the thing it
   audits is worse than an absent detector: it manufactures findings and
   trains its reader to ignore the report.

And the sharpest one, from the five health_intelligence reports rather
than the 37 audits:

6. IT REPORTED HEALTHY FROM SILENCE. The enhanced health report of
   2026-03-31 19:14 contains, verbatim:

       ### PRONOIA
       - **Status**: HEALTHY
       - **Process Running**: Yes
       - **Recent Log Lines**: 0
       - **Errors**: 0
       - **Warnings**: 0

   Zero log lines read as HEALTHY. That is, word for word, the defect
   base rule 7 exists to name -- "silence is never observationally
   equivalent to health; a dead watchdog is itself a failed instrument"
   -- and Pronoia's own committed reports are the earliest dated
   specimen of it in this repository, five months before the rule was
   written.

In the base role's four words, Era 1 was PRESENT, ACTIVE (it fired on
schedule and exited 0), NOT PRODUCTIVE in the sense that matters (its
audit produced two real finding types, both about free-tier rate limits,
and three detectors that could not fire or fired on the wrong process),
and NOT VALID (the status word did not measure pipeline health).

## 0.2 Why the surviving pronoia.py is a live hazard, not a curiosity

publish_reports() at pronoia.py:69 runs `git add` on nine path globs and
then commits and pushes to main, from whatever directory it is launched
in. On this host that directory is the canonical checkout. Under D-23
that is a section 1 violation (no seat performs a mutating git operation
in the canonical checkout), a section 2 violation (no worktree), and a
section 5 violation (pathspec commit without a message file, pushed
straight to main). The file is gitignored, so no seat reading the tree
would ever see it coming.

Nothing was done about it on this pass beyond recording it: deleting an
untracked file on a shared host is a destructive, outward-facing action
and the operator's directive was bootstrap and registration only. It is
PRON-02 in the backlog with the recommendation attached.

## 0.3 The one substantive finding: Era 2 is ALIVE and PRODUCING NOTHING

Measured 2026-09-11 against the canonical Postgres on M1
(EW_DB_HOST=192.168.1.202), at 16:58Z.

The heartbeat says the loop is fine:

    agora.agent_heartbeats where agent_name='Pronoia'
      machine              M4
      status               online
      pid                  9620
      last_heartbeat       2026-09-11 12:58:14-04:00   (seconds old)
      last_work_attempt_at NULL
      last_work_success_at NULL
      health               NULL

The work says it is not. Rows per day in agora.intelligence_outputs, by
stage, across the transition:

    stage                        09-08  09-09  09-10  09-11
    pronoia_portfolio_refresh        6      0      0      0
    pronoia_brief_generated          6      0      0      0
    pronoia_dashboard_pushed         6      0      0      0
    pronoia_email_dispatched         6      0      0      0
    pronoia_cycle_complete           6      0      0      0
    observability_canary            96      6      0      8
    machine_health_m4               24      1      0      2

The git side agrees: the newest "auto: portfolio update" commit on
origin/main is 64de18126 at 2026-09-09T02:15:10Z, 62.6 hours before this
measurement, after a cadence that held at exactly 6 per day for at least
five consecutive days and then stopped dead rather than degrading.

THE DISCRIMINATOR. 2026-09-10 is a total zero day for every stage,
including the canary and the machine-health probe, which implicates the
M4 HOST rather than this loop. But on 09-11 the host is back: the canary
wrote 8 rows, machine_health wrote 2, and one agent_started row landed
at 11:03:40. The heartbeat thread came back with it. All five
pronoia_* cycle stages are still at zero. So the host event explains
09-10 and does not explain 09-11.

INDETERMINATE BRANCH, stated because the base role requires one. At the
time of measurement the restarted process was 1 h 55 m old against an
hourly cadence for two of the five stages. If those stages fire on a
fixed minute rather than at cycle start, one missed hour is within
normal and the honest reading is "suspicious, not established". What is
NOT within normal on any reading: the four-hourly dashboard push has
missed roughly 15 consecutive cycles, and the three heartbeat columns
that would settle the question have never been written at all.

THAT LAST POINT IS THE ACTIONABLE ONE, AND IT IS THIS SEAT'S OWN CODE.
agora.agent_heartbeats already HAS last_work_attempt_at,
last_work_success_at and health. Pronoia's heartbeat writer
(_start_pronoia_pg_heartbeat, scripts/intelligence_loop.py:79) populates
none of them. It writes a liveness beat and a cycles_today counter into
status_json and calls that health. So the loop advertises "online" from
a daemon thread while the work it exists to do has been dead for two and
a half days, and no field anywhere distinguishes the two.

That is Era 1's defect number 6, reproduced exactly, by the same seat,
four months later, in a different language, against a schema that had
already been given the columns to prevent it. This seat considers that
the single most useful thing it learned on this pass, and it is
unflattering: the lesson did not transfer because it was never written
down anywhere a later author would read.

## 1. What this seat is, as of today

The operator woke Pronoia on 2026-09-11 with one instruction (verbatim
in roles/Pronoia/prompts/2026-09-11_adoption/OPERATOR_DIRECTIVE.md):
bootstrap, create a role under roles/ like the others, adhere to the
base-role concept, pull the latest first, and do nothing else except
report what the agent did when it was active. That is what this pass
did.

Booting an old seat is an archaeological event (base role, seat states).
Both queues are classified in
roles/Pronoia/QUEUE_ARCHAEOLOGY_2026-09-11.md: 1 STILL_LIVE, 3
NEEDS_REPREMISE, 1 PARKED, 3 SUPERSEDED, 3 RETIRED.

Until the operator assigns or re-premises, this seat has:

- NO lane. It changes no code and no document outside roles/Pronoia/ and
  its own rows in roles/base-role/INHERITANCE.md and
  roles/base-role/MONITORS.md (added under the Archaeon ruling that a
  seat adds its own rows).
- NO write authority over the running Era 2 loop. It did not restart it,
  stop it, reconfigure it or touch M4. The loop runs on a host this seat
  cannot reach; that is recorded, not worked around.
- NO claim promoted. The Era 2 finding above is a measurement with an
  INDETERMINATE branch stated, not a verdict.
- NO science. It has adjudicated nothing.

Seat state after this pass: BLOCKED on an operator decision, recorded as
PRON-01 (XL) in roles/Pronoia/BACKLOG_H0H5.md.

## 2. The specialisation this seat would carry, if chartered

Stated so the operator has something concrete to rule on, NOT claimed as
a mandate. The north star is the test: supply primitives, environments,
instruments, provenance and pressures; never build the reasoner.

An orchestration seat is a LIVENESS INSTRUMENT, not a scheduler. Era 1
optimised for cycles completed and Era 2 optimises for a heartbeat that
stays green; both are throughput metrics that satisfy themselves, which
is the shape base rule 8 names. The defensible version owns one
property for the whole fleet:

    FOR EVERY STANDING LOOP, THE DISTANCE BETWEEN "IT IS RUNNING" AND
    "IT IS PRODUCING" IS MEASURED AND VISIBLE WITHOUT RUNNING IT.

That is not a new idea in this program -- it is base rules 7, 8 and 9
already adopted -- but MONITORS.md is currently a hand-maintained
markdown table whose rows are written by the seats they describe, and
this pass found two of its rows wrong in opposite directions on the one
loop it looked at closely (owner misattributed; input declared dead when
it is alive and writing). A registry that each seat writes about itself
has the same blind spot as an audit that grades self-reports, which is
the defect this seat is a specimen of.

Two properties this seat would own, both measurable, both currently
failing:

- HEARTBEAT CARRIES WORK STATE. Every heartbeat writer populates
  last_work_attempt_at, last_work_success_at and health, so "alive" and
  "working" are different observable facts. Pronoia's own writer fails
  this today; the columns exist and are NULL.
- REGISTRY ROWS ARE DERIVED, NOT ASSERTED. Where a MONITORS.md row
  names a freshness source that a query can reach, the row is checked
  against it rather than typed. Two of two Pronoia-relevant rows were
  stale on 2026-09-11.

Both are falsifiable and cheap. Neither requires starting a loop, and
the first one is a defect in this seat's own committed code, which is
where the base role says to start.

If the operator wants nothing else from this seat, the honest
recommendation is in STATUS.md section 3, and it includes the option
that this seat is not worth re-chartering.

## 3. Standing commitments already in force (inherited, pointers only)

- Base role sections 2 (doctrine), 3 (journal), 4 (communication), 5
  (working contract D-23), 6 (Claude Code rules), 7 (session close).
- North star (roles/base-role/NORTH_STAR.md). Kill claims, never
  lineages, never the loop. Era 1's residue -- its audit-check schema,
  its capture-and-grade pattern, and above all its six documented
  instrument failures -- stays navigable. Nothing here is marked dead;
  Era 1 is RETIRED with annotation, which is an observation, not a
  verdict on the lineage.
- Credentials: never read, print, commit or paste one. This seat's Era 1
  code reached five API keys through agents/eos/.env; the project
  instruction (CLAUDE.md) is that keys are reached through keys.py and
  never read directly. Nothing in this directory reads a key.
- No hardcoded drive letters in code or committed prompts. Where an
  absolute host path appears in this seat's prose it is evidence about a
  specific machine (the surviving pronoia.py on M2) and is named as
  such, not used as a configuration value.
- Calibration ledger: roles/Pronoia/calibration/LEDGER.md. It opens with
  three rows against this seat.

## 4. Files in this directory

- RESPONSIBILITIES.md -- this file (entry file)
- STATUS.md -- plain-language status, the four-word state, the
  recommendation, the conflict of interest
- QUEUE_ARCHAEOLOGY_2026-09-11.md -- both eras' queues classified
  against the current north star
- BACKLOG_H0H5.md -- provisional; below the schema's 20-item floor until
  a charter exists, and says so
- journal/2026-09-11.md -- what happened, the commands, the SHAs
- calibration/LEDGER.md -- past wrong calls by this seat
- prompts/2026-09-11_adoption/ -- the operator's directive, verbatim,
  with MANIFEST
