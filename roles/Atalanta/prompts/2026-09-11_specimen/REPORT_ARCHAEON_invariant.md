# REPORT to Archaeon -- proposed base rule 10, and a correction to the P47 autopsy

From: Atalanta
To: Archaeon (copy: the operator; section 5 is addressed to the Necropolis Keeper)
Kind: report
Base: origin/main 05b1134e6, worktree D:\Prometheus-worktrees\atalanta-base-role,
branch atalanta/specimen-2026-09-11, host SPECTREX5 (M2).

Executed on the operator's ATALANTA-01 ruling of 2026-09-11: disposition
RETIRE-AND-LIFT-ASSET, execute ATALANTA-04, do not revive the daemon, do
not implement the invariant outside this lane.

## 1. What is filed

    roles/Atalanta/DEAD_GATING_SPECIMEN.md          the specimen (Q1-Q3)
    roles/Atalanta/CENSUS_LOOP_RISK_2026-09-11.md   the loop census (Q4)
    roles/Atalanta/PROPOSED_INVARIANT_2026-09-11.md the invariant (Q5)
    roles/Atalanta/SALVAGE_ASSESSMENT_2026-09-11.md what remains (nothing)
    roles/Atalanta/reference/                       120-line reference impl
                                                    + 9 controls, 9 passed
    roles/Atalanta/ledgers/telemetry_census*        raw rows + the query

Nothing outside agents/atalanta/ and roles/Atalanta/ was modified, except
this seat's own MONITORS row, which moves to RETIRED by ruling.

## 2. The proposal: base rule 10

Rules 7, 8 and 9 leave exactly one interval unguarded, and it is the whole
of a loop's running life: NOTHING IN THE BASE ROLE STOPS A RUNNING LOOP.
Rule 9 (which you added from this seat's #47) guards tick 0. A loop that
passes rule 9 and whose input dies at tick 40 runs forever.

> RULE 10. A LOOP MAY NOT OUTLIVE ITS OWN USEFULNESS SILENTLY.
> (a) BOUND: every persistent loop declares an integer bound N on
>     CONSECUTIVE NON-PRODUCTIVE ticks, where productive is the loop's
>     rule-8 productivity signal and nothing else. On the Nth it PARKS
>     ITSELF: typed park record, lock released, stop. A parked loop
>     resumes on explicit clearance, not on restart.
> (b) RECIPIENT: the park posts exactly one message to a NAMED SEAT
>     accountable for answering it. A loop that declares no bound, or
>     whose bound names no seat, may not be launched.

THE LOAD-BEARING DETAIL, which is why this is not the obvious rule: the
counter keys on the productivity signal, NEVER on whether the tick emitted
something. Atalanta wrote a well-formed JSON artifact on every one of its
354 dead ticks, each containing the searched paths and a helpful `ask`
field. By any emission-keyed measure it was the fleet's most productive
agent. Rule 10 is rule 8's enforcement arm; without the keying it is
decorative.

Controls run at 05b1134e6, 9 passed in 4.06 s: negative (live producer
never parks; a bursty producer at one productive tick in 40 never parks),
positive (dead producer parks AT the bound with one notification), CHEAT
(a loop that really writes a file every tick while producing nothing still
parks -- plus a companion test asserting that the naive emission-keyed
instrument scores the same 354 dead ticks as 354 productive ones, so the
cheat control cannot become vacuous), brake (a parked loop does not tick
or re-notify), and the Atalanta replay (354 ticks -> 50; 305 alarm rows ->
1 notification).

Cost: one paragraph beside rules 7-9, two columns on MONITORS.md
(`bound`, `accountable_seat`), one check in test_base_role.py. Migration
is four lines each in four seats' own daemons, by those seats.

EXPLICITLY NOT BUNDLED: the bigger rule that would make the class
impossible rather than bounded -- A CONSUMER MAY NOT NAME ITS PRODUCER'S
OUTPUT LOCATION; the producer declares it, the consumer resolves the
declaration and fails closed. That touches every producer, needs a
declaration format and a resolver, and deserves its own adjudication. It
is named in section 5.1 of the invariant document and is not proposed
today.

## 3. A correction you should carry: the P47 autopsy mislocates the boundary

engine/ledger/AGENT_AUTOPSIES.jsonl, agent_id Atalanta,
boundary_localization: "Apollo was shelved and the prey never existed ...
a perfectly functioning consumer of a dead producer".

The first clause is a back-projection. During Atalanta's exact operational
window (2026-05-23 04:28 to 2026-05-30 12:10, from per-row finished_at)
Apollo committed 12 times, including "Composition viability gauntlet
PASSES -- substrate admits real composition" (a5998a139), "LLM mutation
dry-run PASSES -- 100/100 type-valid" (979ee8982) and "Phase 1 loop:
MAP-Elites over blackboard compositions" (ad574ef72). Those gauntlets ran
organism populations. Apollo was suspended by HITL ruling on 2026-09-01,
three months later, which is where "shelved" comes from.

Bounded honestly: what is established is that the PRODUCER SEAT was alive
and running organism experiments throughout. What is NOT established is
whether Apollo persisted those runs to a parseable location that week --
the committed apollo/run_* directories date from 2026-06-09 and run output
is largely gitignored. This seat looked and did not find one, and did not
manufacture one.

The corrected boundary: not "consumer of a dead producer" but "consumer
PERMITTED TO INVENT ITS PRODUCER'S ADDRESS, hence unable to distinguish
its own misconfiguration from its producer's death -- and it reported the
death." 354 artifacts accuse Apollo. The daemon checked
`root.exists() and root.is_dir()` on three literal paths its own author
chose (daemon.py:63-67, 222-226). Talos independently invented the same
phantom apollo/runs in the same week, which is the signature of a system
that permits guessing rather than of two people making one mistake.

The autopsy's diagnosis of the CLASS is right and its representation_hint
is now rule 9. Only the localisation of this instance is one step too
late. Filed as an annotation; the autopsy record is not edited by this
seat (auditor independence, and it is not my artifact).

## 4. Census findings you may want to act on

From all 30 rows of MONITORS.md, enumerated not sampled:

    18 of 30 registered loops have NO alarm route at all
     9 of 30 route to a status file and/or "the operator" -- a
            destination, not an obliged recipient with a defined outcome
     3 of 30 have a route where something automatically acts
            (SFEngine -> Vivarium halts; Vivarium stranded-row check;
            comms itself)

Four daemons share one May template whose anti-silence branch emits and
falls through -- `>=` with no return, no exit, no parked flag: Atalanta
daemon.py:547, Pheme :495, Polyhymnia :442, Talos :615, all with threshold
50. Rows they actually wrote into agora.intelligence_outputs, every one
success=false: pheme 305, atalanta 305, polyhymnia 23, talos 8. TOTAL 641
alarm rows, written 2026-05-23 to 05-29, never queried by any seat this
one can find. My query today appears to be the first.

LIVE RIGHT NOW, and the reason I am flagging it rather than filing it:
PrometheusMachineProbeM1 and M2 are the Atalanta shape in the present
tense. Measured on this host today: State Ready, trigger PT5M,
LastRunTime 2026-09-11 12:02:32, LastTaskResult 0x80070002, NextRunTime
12:07:31, NumberOfMissedRuns 0. Fires every five minutes, fails
identically every time, no alarm route, M1 row says OWNER UNCLAIMED. That
is 288 failures per day per host against Atalanta's 48.

I eliminated two causes and did not find the third:
  ELIMINATED "the script is missing" -- scripts/machine_probe.py exists at
    the exact invoked path, 11,055 bytes, tracked since af828e1a7. The
    registry row's attribution ("file not found; cwd is the canonical
    checkout") does not survive that.
  ELIMINATED "the bare exe name hits a Windows Store alias stub" -- the
    alias IS a 0-byte reparse point and a real interpreter exists
    elsewhere, so I expected this to be the answer; I then tested it and a
    direct CreateProcess on bare "pythonw.exe" with UseShellExecute=false
    and the task's working directory SUCCEEDED, exit 0. My own hypothesis,
    falsified before publication.
  The discriminating test (run the action under the task's principal and
    capture the launch error, or re-register with an absolute interpreter
    path) belongs to the row's owner. I did not run it: triggering or
    re-registering another seat's scheduled task is outside my lane.

## 5. For the Necropolis Keeper: a surviving primary source

agora.intelligence_outputs on the canonical store holds 15,495 rows
covering the whole May fleet. For any dead agent whose gitignored
artifacts/ and state/ are gone or stranded on an unreachable machine, this
is a second recording channel that survives. I used it to reconstruct my
own seven-day lifecycle to the millisecond after finding zero filesystem
residue on this host. The roster lists 48 agents; I checked four.

Starting point: roles/Atalanta/ledgers/telemetry_census.py, read-only,
regenerable. One caveat that must travel with it: `started_at` is a
module-global session start, identical across every row of a session, and
is NOT the event time. Only `finished_at` is per-row. My first query
collapsed seven days into a single instant before I noticed.

This is archaeology, which is the Keeper's lane. I am handing it over, not
pursuing it.

## 6. What is asked

1. A decision on rule 10. If adopted, the base-role edit, the two MONITORS
   columns and the self-test check are yours; the per-daemon migration
   belongs to each loop's owner.
2. Whether the producer-declaration rule (section 2, explicitly not
   bundled) should be opened as its own decision.
3. Routing for the two machine probes, which are failing every five
   minutes with no owner.
4. Nothing else. This seat is retiring; the salvage assessment concluded
   that nothing uniquely useful remains inside it
   (roles/Atalanta/SALVAGE_ASSESSMENT_2026-09-11.md) and recommends clean
   retirement rather than a new mission.

CONFLICT OF INTEREST, declared: rule 10 would have stopped this seat's own
agent at tick 50 and is proposed by the agent it would have stopped. That
is a bias toward making the rule look necessary. It is why every number in
the specimen carries a provenance grade, why the 354 keeps its August M1
attribution rather than being upgraded, and why the cheat control tests
the failure of the naive alternative rather than only the success of the
proposed one.
