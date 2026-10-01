# Achilles census -- classification rules

Currency: 2026-10-01 (first run). Implemented in achilles/census/classify.py and
achilles/census/build.py; every rule below is exercised by
achilles/census/tests/test_census.py (positive, negative and cheat controls).
The rule id that decided each seat is stored in the snapshot
(docs/fleet/fleet_state.json seats.<Seat>.state_detail.rule) with the reasons
(state_detail.why), every declared state that was considered
(state_detail.declared) and the activity ages used (state_detail.activity).

No model sits in this path. The census is a deterministic function of git,
seat files, ops ledgers and database rows. Achilles observes and reports; it
assigns no work, reprioritises nothing and rules on no science.

## 1. The four things kept apart (charter: ACTIVE STATUS MUST BE EVIDENCE-BASED)

    process alive        presence: comms.agents last_sync_at / last_active_at,
                         agora.agent_heartbeats (legacy), MONITORS.md loop rows.
                         Shown, never sufficient for "active".
    productive work      substantive evidence (section 2, levels 1-3)
    assigned but waiting a task source exists (section 4) but no substantive
                         work since it was assigned -> flag ASSIGNMENT_NO_PROGRESS
    historical only      no substantive evidence within 7 days; or a
                         historical role document / pre-seat agent or tool

## 2. Evidence levels (lower is stronger; charter ranking)

    1  experiment/result receipt: a seat-attributed commit whose subject
       carries the verdict vocabulary (RESULT, VERDICT, KILL(ED), NULL,
       CLEAN_NULL, CONFIRMED, NOT_CONFIRMED, INDETERMINATE, INCONCLUSIVE,
       FAIL(ED), PASS(ED), RETRACT*, SURVIVED, REFUTED, VALIDATED,
       INADMISSIBLE, NEGATIVE, POSITIVE -- capitals only, so prose "pass" or
       "result" does not count; a following ".md" (FREEZE.md) does not
       count); or an ew.experiments row
    2  any other seat-attributed commit that is not bookkeeping-only
    3  a substantive comms message sent by the seat (report, ruling,
       delegation, prompt, question) that is not a heartbeat
    4  explicit status/progress update: a heartbeat message, a commit that
       touches only WORK_STATE/STATUS/TODO/journal/ledger files, a
       WORK_STATE updated_at
    7  presence only: comms sync/active timestamps, legacy agora heartbeat,
       acknowledgements

    Last active      = newest level 1-3 event (its source is cited)
    Last activity    = what that event was (commit sha + subject, or comms
                       #id kind + recipients + subject)
    Active?  Yes       level 1-3 within 24 h
             Uncertain level 1-3 within 72 h, or only level 4/7 within 24 h
             No        otherwise

Not experiments (charter LAST EXPERIMENT): test-suite runs, lint,
dashboard regeneration, heartbeats, routine sync, WORK_STATE/state-READY
commits, journal-only commits. PREREG / PREREGISTRATION / FROZEN / FREEZE /
SEAL / LAUNCH / RUNNING / AMENDMENT mark an experiment STARTED (shown as
"started/preregistered; no result commit yet"). Non-science seats
(registry domain infrastructure / reporting / coordination / audit) with no
experiment show "N/A (<domain>)".

## 3. Commit attribution (A1-A6; first match wins)

    A1 "auto:" prefix                    -> SYSTEM (the M4 portfolio loop)
    A2 "Seat[instance]:" / "Seat:"       -> Seat (case-insensitive; lane
                                            suffix -X stripped: Nestor-B)
    A3 "Seat <topic>:"                   -> Seat ("Aporia journal ...:")
    A4 "<Name>-Instance: ..." trailer    -> Name (Nestor row commits G[m1-..])
    A5 path majority (> 50%) over roles/<Seat>/ and engine paths with a
       recorded primary seat (roles/Achilles/census/registry/engines.json)
    A6 author name equal to a seat       -> Seat
    otherwise UNATTRIBUTED: counted and sampled in the anomaly
    UNATTRIBUTED_COMMITS, never guessed. Merge commits are excluded.

Host from an instance tag: m1 M1, m2 M2, gandalf M3, harry1 M4, ubu001,
ubu002, elsa ELSA, desktop-ruapvai DESKTOP-RUAPVAI, buckkeep BUCKKEEP.
Host precedence: newest comms.agent_instances machine; else the newest
commit's instance tag; else the registry's documented host. A documented
host that disagrees with the observed one is shown beside it, not hidden.

## 4. Current / last task (charter LAST TASK SET)

Candidates, all kept in seats.<Seat>.task.candidates with their sources:

    rank 1  ops/fleet/QUEUE.json seats.<Seat>.current (fleet order queue),
            ops/fleet/CENSUS.json seats.<Seat>.forward.current_objective
    rank 2  newest operator prompt directory roles/<Seat>/prompts/<date>_*
            whose name or files say charter / creation / operator /
            directive / mission
    rank 3  newest comms prompt or delegation addressed to the seat by name
            (broadcasts to * are not assignments)
    The newest of ranks 1-3 is shown. Only when none exists:
    rank 4  the seat's own WORK_STATE current_objective / current /
            next_actions[0]
    rank 6  STATUS.md "next executable action"
An assignment is never inferred from recent work alone.

## 5. State (S0-S6; first rule that applies wins)

Declared states considered, newest first: WORK_STATE.json (newest across
origin/main and the seat's own origin/<seat>/* branches, MWO-0001), Aporia's
ops/fleet/CENSUS.json forward.state, comms.agents.status when it is parked
/ retired / idle / paused ("active" there only means booted, so it is not
a declaration), STATUS.md "seat state:" line (dated by its last commit).
A declaration is FRESH when younger than 72 h.

    S0 non-seat entity (historical role document, pre-seat agent/tool):
       registry marker RETIRED/PARKED, else ACTIVE if attributed activity
       within 7 d (LOW), else DORMANT
    S1 lifecycle marker RETIRED/CLOSED/DEPRECATED and no fresh working
       declaration -> RETIRED; activity after the marker date ->
       flag ACTIVITY_AFTER_RETIREMENT, confidence LOW
    S2 declared PARKED (or marker PARKED with nothing fresher) -> PARKED;
       substantive work within 24 h -> flag PARKED_BUT_ACTIVE, LOW
    S3 fresh declaration:
         WORKING/ACTIVE + substantive <= 24 h  -> WORKING (HIGH)
         WORKING/ACTIVE + substantive <= 48 h  -> WORKING, VISIBILITY_STALE
         WORKING/ACTIVE + nothing in 48 h      -> IDLE, ACTIVE_NO_WORK_48H
         READY / BLOCKED / HOLD / IDLE         -> as declared
    S4 stale or no declaration, substantive <= 24 h -> ACTIVE (or the stale
       declared BLOCKED/HOLD/READY, LOW); <= 7 d -> IDLE (or stale declared)
    S5 substantive older than 7 d -> DORMANT (stale BLOCKED/HOLD stays, with
       STALE_TASK)
    S6 no attributable evidence anywhere -> UNKNOWN (LOW)

DORMANT and RETIRED are observations and annotations, never verdicts on a
lineage (base role: "nothing is marked dead prematurely").

Confidence: HIGH = a fresh declaration agrees with fresh evidence; MEDIUM =
one source, or an older declaration; LOW = sources conflict, or the state
rests on stale evidence. Fresh declarations that disagree add
CONFLICTING_STATES and cap confidence at MEDIUM; the disagreement is shown.

## 6. Topology and inconsistency flags

    NEW_SEAT / SEAT_DISAPPEARED      roster diff against the previous snapshot
    BRANCH_ONLY_SEAT                 roles/<X>/ only on a branch (Chiron)
    UNKNOWN_COMMS_SENDER / _AGENT    comms names with no roles/ dir or alias
    UNFAMILIAR_SEAT_IN_WORK_ORDER    QUEUE.json / CENSUS.json name not in roster
    NOT_IN_REGISTRY, MISSING_ROLE_DESCRIPTION, NO_ROLE_DOCUMENT
    ENGINE_NO_OWNER                  engine path with commits in 7 d, no
                                     primary seat recorded
    OWNERSHIP_DRIFT                  of the engine's last >= 5 attributed
                                     commits, a majority comes from a seat that
                                     is neither its primary nor a listed seat
    ACTIVE_NO_WORK_48H, ASSIGNMENT_NO_PROGRESS, STALE_TASK,
    VISIBILITY_STALE, CONFLICTING_STATES, PARKED_BUT_ACTIVE,
    ACTIVITY_AFTER_RETIREMENT, UNATTRIBUTED_COMMITS, EMAIL_NOT_SENT_72H

## 7. Freshness of the census itself

docs/fleet/run_status.json carries last_attempted_utc, last_successful_utc,
last_status and last_error. The page reads it in the viewer's browser and
turns its banner red when the last success is older than 7 h or the last
attempt failed -- computed at view time, so a dead scheduler cannot leave
the page looking fresh. The mailer (scripts/send_brief_email.py
build_fleet_census) prints STALE FLEET CENSUS under the same 7 h rule, or
FLEET CENSUS UNAVAILABLE when the block cannot be read. A failed run never
replaces the snapshot or the page.

## 8. Incremental operation

Cursors in the snapshot: origin ref tips (git commits are read with
`--not <previous tips>`), comms max message id, roster hash, registry hash,
last deep pass. A deep pass (all history, about 16 s) runs when there is no
previous snapshot, the roster or registry changed, or 7 days have passed.
Windowed 24 h counts are recomputed every run.
