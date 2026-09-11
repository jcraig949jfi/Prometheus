# DEAD-GATING: the Atalanta specimen

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. ATALANTA-04, executed on the operator's ruling of
2026-09-11 (disposition RETIRE-AND-LIFT-ASSET: the specimen is the asset;
the daemon is not revived and is not reconnected to Apollo).

Built from origin/main 05b1134e6 in D:\Prometheus-worktrees\atalanta-base-role
on branch atalanta/specimen-2026-09-11. Raw rows:
roles/Atalanta/ledgers/telemetry_census_2026-09-11.md, regenerable with
roles/Atalanta/ledgers/telemetry_census.py.

## 0. Provenance grades, stated before any number is used

    G1  re-measured on this tree or this host today, command recorded
    G2  read today from the canonical store (agora.intelligence_outputs)
    G3  recorded by another seat on another host and NOT re-verifiable
        from here (Aporia P47's August artifact census on M1)
    G4  derived by this seat from G1/G2 by arithmetic, shown as such

The operator's instruction stands and is obeyed: the 354 count keeps its
August M1 attribution and is NOT upgraded to independently verified fact.
What changed today is narrower and is stated precisely in section 1.3.

## 1. The lifecycle, measured

### 1.1 The two recording channels

Aporia's P47 autopsy (2026-08-20) counted 354 artifacts in the agent's
artifacts/ directory on M1, all of them upstream_not_found (G3). That
directory is gitignored and does not exist on this host, so this seat
could not re-read it.

Today a SECOND recording channel was found still intact: the daemon also
wrote every tick into `agora.intelligence_outputs` on the canonical store,
via session_telemetry.log_work (daemon.py:434-445 -> scripts/session_telemetry.py:164
-> agora_persist.log_intelligence_stage). Those rows survive (G2):

    atalanta_upstream_not_found      354 rows
    atalanta_self_audit_null         305 rows   (all success=false)
    atalanta_startup                   3 rows
    atalanta_shutdown                  1 row

### 1.2 What the second channel is and is not

It is an independent RECORD. It is NOT an independent MEASUREMENT. Both
channels were written by the same daemon in the same tick, two statements
by one witness. A fault in the tick loop would corrupt both identically,
and neither observes Apollo; both observe only the daemon's own belief.
So: the 354 is now dual-recorded, single-mechanism, and still carries its
August M1 attribution.

### 1.3 The one number that was genuinely predicted, then checked

Before querying anything, this seat read the control flow at daemon.py:547-552
and predicted the alarm must have fired on every tick from 50 to 354
inclusive, that is 305 times, because the branch has no `return` and no
state change (section 3). The table was then queried: 305 rows (G2,
predicted G4 = 305, observed = 305).

That is a falsifiable prediction about a mechanism, made in advance and
survived. It does not upgrade the 354; it establishes that the counter
never reset, which means every one of the 354 ticks was null.

### 1.4 The timeline, from per-row finished_at (G2)

    launched                  2026-05-23 04:28:00 -04:00
    first alarm row           2026-05-24 04:09:50 -04:00
    last row of any kind      2026-05-30 12:10:49 -04:00
    total operational life    7 d 07:42:48
    time before first alarm     23:41:50
    time spent in alarm state  6 d 08:00:58
    fraction of life alarming        86.5%   (G4)
    ticks per day               48.4        (G4; the 1800 s interval
                                             predicts 48.0 -- the machine
                                             kept perfect time)

    startups 3, clean shutdowns 1: two of three sessions ended without a
    shutdown row. The last upstream_not_found and the last alarm share a
    timestamp to the millisecond, so the process was killed, not stopped.

The agent was not broken. It ticked to schedule for seven days and
three hours, and it spent 86.5 percent of that life correctly and
continuously reporting its own uselessness.

## 2. Question 1: how a correctly functioning consumer accumulated 354 null ticks without ever observing its producer

Four layers, each necessary, none sufficient alone.

### 2.1 The consumer named its producer's output location itself

daemon.py:63-67:

    APOLLO_RUN_ROOTS = [
        REPO_ROOT / "apollo" / "runs",
        REPO_ROOT / "apollo" / "runs_v2",
        REPO_ROOT / "apollo" / "organism_runs",
    ]

Three literal paths, written by the consumer's author, at authoring time,
as an inference about where Apollo ought to write. Apollo never agreed to
them, was never asked, and never wrote to any of them (G1: all three
absent at 05b1134e6). There is no declaration anywhere in the repository
by which Apollo states its output location, so there was nothing to bind
to and nothing to break when the guess was wrong.

The same guess was made independently in the same week by Talos, whose
charter lists apollo/runs as one of its five corpus streams and marks it
"never existed". Two authors, no contact, same phantom address. That is
the signature of a system in which guessing is permitted rather than a
system in which two people made the same mistake.

### 2.2 The liveness test tested a path, not a producer

daemon.py:222-226:

    for root in APOLLO_RUN_ROOTS:
        if root.exists() and root.is_dir():
            return root
    return None

`exists()` answers "is there a directory at this string". The question
that mattered was "is my producer alive and emitting". These are
different questions with the same return type, and the second was never
asked. This is base rule 2 (capability over labels) one layer down from
Techne's `which("gcc")`: a path is a label for a producer, and the label
was checked.

### 2.3 Absence was a legal, handled, non-escalating outcome

Returning None raises nothing. It routes to a branch that creates the
artifacts directory if needed, writes a well-formed JSON artifact naming
all three searched paths and an `ask` field telling a reader how to fix
it, logs a telemetry row, increments two counters, and returns normally.
The tick reports success in every sense the process exposes. Nothing in
the design distinguishes "this tick did the work" from "this tick did
nothing", because both end in a written artifact and a clean return.

### 2.4 The failure was MISLABELLED, and the label accused the wrong party

Every one of the 354 artifacts says `upstream_not_found`, and the
telemetry error string is `apollo_root_not_configured`. A reader of the
artifact stream would conclude Apollo was dead.

Apollo was not dead. During Atalanta's exact operational window Apollo
committed 12 times (G1, git log 2026-05-23..2026-05-31 over apollo/),
including "Composition viability gauntlet PASSES -- substrate admits real
composition" (a5998a139), "LLM mutation dry-run PASSES -- 100/100
type-valid" (979ee8982), and "Phase 1 loop: MAP-Elites over blackboard
compositions" (ad574ef72). Those gauntlets necessarily ran populations of
organisms. It was one of Apollo's most productive weeks.

Stated with its limit: what is established (G1) is that the PRODUCER SEAT
was alive and running organism experiments throughout. What is NOT
established is whether Apollo persisted those runs to any parseable
location on disk that week -- the committed apollo/run_* directories date
from 2026-06-09, after Atalanta was already dead, and run output is
largely gitignored. So the honest form is:

    the consumer reported "my producer is not there" for seven days while
    the producer was demonstrably alive and working, and the consumer had
    no way to tell the difference, because it never asked the producer
    anything -- it asked the filesystem about three strings.

This is the correction the specimen makes to the P47 autopsy, which
localised the boundary as "a perfectly functioning consumer of a dead
producer". The consumer was perfectly functioning; the producer was not
dead in that window. The true boundary is one step earlier: a consumer
that is permitted to invent its producer's address cannot distinguish its
own misconfiguration from its producer's death, and will report the
second while suffering the first. Apollo was suspended later, by HITL
ruling on 2026-09-01, which is where the "shelved" reading comes from;
applied to May it is a back-projection.

## 3. Question 2: why the alarm fired at 50 and still failed to stop or escalate

### 3.1 It did not fire once. It fired 305 times.

daemon.py:547-552, quoted in full:

    if state.get("anti_silence_counter", 0) >= ANTI_SILENCE_ALARM_THRESHOLD:
        _emit_event("self_audit_null_alarm", level="error",
                    consecutive_null=state["anti_silence_counter"])
        emit_log_work("atalanta_self_audit_null",
                      summary=f"ALARM: {state['anti_silence_counter']} consecutive null ticks. Apollo upstream likely dead or thresholds too high.",
                      success=False, error="anti_silence_threshold_exceeded")

    save_state(state)

Three properties of that code are the whole answer:

- The condition is `>=`, not `==`. Once true it is true forever.
- The branch contains no `return`, no `sys.exit`, no raise, and no write
  of a parked flag into state. Control falls through to `save_state` and
  the loop sleeps and ticks again.
- The counter is only ever reset on a successful dispatch (daemon.py:536),
  which could never happen, so nothing could ever clear it.

Measured consequence (G2): 305 rows, every one `success=false`, every one
carrying `error='anti_silence_threshold_exceeded'`, spanning 2026-05-24
04:09:50 to 2026-05-30 12:10:49. The alarm was not missed. It was
delivered 305 times, correctly, with an accurate diagnosis in its own
summary text ("Apollo upstream likely dead or thresholds too high"), over
six days and eight hours.

### 3.2 An alarm that cannot stop anything is a log line with an urgent name

The design treats the threshold as a NOTIFICATION boundary. Nothing in
the program treats it as a CONTROL boundary. The daemon has full
authority to stop itself -- it owns its pid lock, its state file and its
process -- and never uses it. The threshold's only effect is to add a row
to a table.

### 3.3 It escalated to a destination, not to a person

`log_work` writes to `agora.intelligence_outputs`. That is a table. A
table is a place a signal is WRITTEN; it is not a party who is OBLIGED
to read it. No query ran against those rows between 2026-05-24 and
2026-08-20, when Aporia went looking for a different reason. The MONITORS
row for this loop now says NONE ROUTED, and that is the accurate word.

The contemporaneous record shows the signal was not merely unread but
actively dismissed: pivot/orchestration_monitoring_2026-05-24.md, written
the day after launch, records the atalanta and pheme sentinel telemetry
being read as noise.

### 3.4 The fleet-wide number

Every agent built from the same May template has the same
emit-and-fall-through alarm (G1, verified in source): Atalanta
daemon.py:547, Pheme daemon.py:495, Polyhymnia daemon.py:442, Talos
daemon.py:615. All four use the identical constant
ANTI_SILENCE_ALARM_THRESHOLD = 50, the identical `>=`, and none of the
four stops.

Rows those four alarms wrote, all success=false (G2):

    pheme_self_audit_null            305
    atalanta_self_audit_null         305
    polyhymnia_self_audit_null        23
    talos_self_audit_null              8
    TOTAL                            641

641 alarm rows are sitting in the canonical store, every one flagged as a
failure, written between May 23 and May 29, and no seat has ever queried
them. This seat's query today is, as far as it can determine, the first.

A methodological note against this seat's own earlier reasoning: before
querying, it estimated Polyhymnia's firings at about 201 by deriving from
that loop's registry row ("47 integrating ticks then 250 null ticks").
The measured value is 23. The derivation was wrong because the counter
resets on productive ticks and Polyhymnia's nulls were not one
consecutive run. The estimate was never published as a number; it is
recorded here and in the calibration ledger because deriving a count from
a prose row and then measuring it is exactly the discipline this document
is about.

## 4. Question 3: the three independent controls, and what each would have caught

The failure needed all three absences. Any one control, present and
working, bounds it.

### 4.1 Launch-time upstream-liveness / precondition gate

WOULD HAVE CAUGHT IT AT: tick 0, before a single artifact.

What it must check, and this is the part the specimen sharpens: not "does
my configured input exist" but "does my PRODUCER declare this output, and
is that declaration satisfied NOW". Atalanta would have failed a check of
the first kind too, so the first kind is enough for this specimen -- but
the first kind is NOT enough for the class, because a consumer that
guesses an address can guess an address that happens to exist and is
empty, or that belongs to someone else, and then the gate passes and the
silence looks legitimate.

Status: base rule 9 now exists (Archaeon, from this seat's #47 finding)
and covers the launch-time gate. It does not yet require the check to be
against a producer's own declaration. That gap is the subject of
roles/Atalanta/PROPOSED_INVARIANT_2026-09-11.md.

### 4.2 Bounded null-progress / automatic dormancy

WOULD HAVE CAUGHT IT AT: tick 50, converting 305 ignored alarms into one
stopped process and one queued question.

The rule: a loop's consecutive no-op count is BOUNDED. On reaching the
bound the loop parks itself -- writes a typed parked state, releases its
lock, stops ticking -- and does not resume until a human or an explicit
command clears it. The bound is a brake, not a bell.

Cost of its absence here, measured: 304 unnecessary ticks, 304
unnecessary artifacts, 610 unnecessary telemetry rows (305 null + 305
alarm) and six days of an agent that a reader of the roster saw as
"active, online, 96 ev" (pivot/agent_roster_2026-05-28.md). That roster
line was true in every field and false in its implication, which is base
rule 8's case exactly.

Status: NOT COVERED by any base rule. Rule 7 makes dormancy visible after
the fact, rule 8 requires a productivity signal, rule 9 guards the launch.
Nothing bounds a running loop. This is the largest remaining gap.

### 4.3 Alarm route with an accountable recipient and an escalation outcome

WOULD HAVE CAUGHT IT AT: the first alarm, 2026-05-24 04:09:50, about
23 hours in.

The rule has three parts and the third is the one that is always missing:
a NAMED recipient (a seat, not a file); a DELIVERY mechanism that reaches
them without their having to go looking (the comms queue exists now and
did not in May); and a defined ESCALATION OUTCOME -- what changes if the
recipient does nothing. An alarm with no outcome on non-response is a
request for attention, and attention is exactly what a failing agent
cannot compel.

Status of the fleet today (G1, from the 30 rows in
roles/base-role/MONITORS.md): 18 of 30 registered loops have no alarm
route at all. Of the 12 that have one, 9 route to a status file and/or
"the operator" -- a destination, not an obliged recipient. Full census:
roles/Atalanta/CENSUS_LOOP_RISK_2026-09-11.md.

## 5. What the specimen corrects in the standing record

Both corrections are annotations. Neither original is rewritten.

1. P47 autopsy, engine/ledger/AGENT_AUTOPSIES.jsonl, boundary_localization:
   "Apollo was shelved and the prey never existed ... a perfectly
   functioning consumer of a dead producer". The first clause is a
   back-projection of the 2026-09-01 HITL suspension onto May. Apollo
   committed 12 times during Atalanta's operational window, including two
   passing gauntlets over organism populations (G1). The autopsy's
   diagnosis of the CLASS is right and its representation_hint is now
   base rule 9; its localisation of THIS instance is one step too late.
   The failure is not "consumer of a dead producer" but "consumer
   permitted to invent its producer's address, hence unable to
   distinguish its own misconfiguration from its producer's death".

2. pivot/COMPONENT_DOSSIERS_2026-06-24.md, on the parser. Carried forward
   from this seat's adoption pass and reaffirmed by the ruling:
   `primitive_sequence` is still a live key throughout apollo/src
   (genome.py, compiler.py, map_elites.py, primitive_types.py,
   ablation.py, health.py) (G1). Atalanta's organism MODEL was not
   invalidated. What diverged was the CONTAINER and, prior to that, the
   ADDRESS. The distinction matters because it says where the defect
   was: in producer discovery and container assumptions, not in the
   agent's understanding of what an organism is.

## 6. What would falsify this document

- Section 2.4 falls if Apollo's May work can be shown to have produced no
  persisted organism artifacts at all in the window AND no such artifacts
  were producible -- in which case "dead producer" becomes accurate for
  May and only the address argument survives. The discriminating evidence
  is an Apollo-side record of run output between 2026-05-23 and 05-30;
  this seat did not find one and did not manufacture one.
- Section 1.3's prediction falls if the 305 rows can be shown to have a
  source other than the alarm branch. The error field on all 305 is
  `anti_silence_threshold_exceeded`, which that branch alone writes.
- Section 3.4's fleet total falls if `agora.intelligence_outputs` was
  pruned or partially loaded. Table size at read time: 15,495 rows;
  the census script re-runs in seconds and any future run that disagrees
  supersedes this one.
- The whole document is weakened if a seat DID read those 641 rows
  between May and today. This seat searched the repository for a consumer
  of the self_audit_null stages and found none; that is a negative from a
  repository search, not proof that no query was ever run.

## 7. The single sentence

An instrument that is honest, punctual, correctly coded and continuously
alarming for six days is not a working instrument, because it was pointed
at an address it invented, could not tell its own error from its
producer's death, had no authority to stop, and reported to a table
instead of to a person.
