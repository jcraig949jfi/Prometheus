VIVARIUM CURRENT-STATE INVESTIGATIVE REPORT
2026-09-11 18:2x-18:4x local (22:2x-22:4x UTC). Instance m1-416d588d.
Requested by the operator. Read-only: nothing was fixed, restarted or
written to any register while gathering this. Every number below was
measured in this window; where a claim rests on an older artifact it says so.
Scripts that produced the numbers: this session's scratchpad
inspect_queue.py / inspect_sfe2.py / inspect_sfe3.py / inspect_pew2.py
(read-only SELECTs; the SFE ledger was opened with sqlite mode=ro).

============================================================================
1. WHERE THE CODE IS
============================================================================
authoring worktree  F:\Prometheus-worktrees\vivarium-base-role
branch              vivarium/base-role-adopt-2026-09-11, HEAD 90739a7c9
vs origin/main      b95e855b1: HEAD is an ANCESTOR (ahead 0, behind 4);
                    the 4 are Archaeon's (649b9ffe0 grantee id, 8d1e1dcec
                    merge, 6fc3ea619 H5-1 complete + candidate-set fix,
                    b95e855b1 reply to my #181). Not diverged. Dirty: 0.
consumer worktree   F:\Prometheus-worktrees\vivarium-consumer, detached at
                    2f84603e5 (on origin/main), clean. 17 commits behind
                    main; the only vivarium/ delta is cli.py (10 lines:
                    workspace receipt routed through the log). Running code
                    == pinned code (heartbeat build.code.base_sha 2f84603e5,
                    dirty false).
canonical checkout  F:\Prometheus still on the retired branch
                    vivarium/v0-2026-09-05 (741 behind). Untouched by me.

============================================================================
2. PROCESSES ON THIS MACHINE (Get-CimInstance Win32_Process, 18:24:57)
============================================================================
pid 26348  H:\Python312\python.exe -m viv.cli run --worker-id vivarium@m1
           started 17:13:01, parent cmd 11512 <- 3240 (Task Scheduler), the
           ONLY Vivarium consumer. Heartbeat age 0 s at 18:25:32; counters
           ticks 824 / idle 799 / executed 25 / failed 0 / blocked 0.
pid 22940  tail.exe -f consumer-vivarium@m1.log  MINE, an orphan of the
           Monitor I stopped at ~17:5x; harmless; should be killed.
pid 7268   SFE engine serve.py --db F:\Prometheus-data\sfe\engine.db
           :8811, started 13:34:09 (Daedalus's). Its dev twin pid 13428 on
           127.0.0.1:8902 (c9_asdeployed.db) started 18:14:50 -- Daedalus's
           C9 reproduction, not production.
pid 15616  python -m ew.service (PEW, :8377) started 14:44:35.
pid 21848  claude.exe --remote-control Archaeon (14:02).
No second consumer. No stranded-row process. No PEW consumer process.

============================================================================
3. QUEUE (viv.research_experiment_queue, prometheus_fire, 18:25)
============================================================================
status      cancelled 492 | completed 536 | failed 79 | queued/claimed/
            running 0 | stranded 0.
today       created 30 rows: 27 completed (24 eca_rule_eval_v1 = cs-h5-1-r1,
            2 evaluate_bitstring Archaeon tick rows, 1 noop_v0 liveness
            probe), 3 failed (Archaeon tick rows cs-c889.., cs-6a8d..,
            cs-69ac.., all "execution failed" at 10:34-10:36 = engine
            episode 2; 3 of Archaeon's 6 daily autonomous slots lost to it).
outcomes    all 27 completed today: SURVIVED. Lifetime observations in the
            engine: FALSIFIED 592 / SURVIVED 395, so the rule does fire both
            ways historically (C3 campaign); today's set is one-sided.
last event  event_id 3066, 17:19:01, 'completed' on 73958790.
spec reuse  lifetime 721 distinct spec_hash over 1107 rows (cancellations
            are the difference); today 30/30 distinct. Two spec_hashes have
            2 completed executions each (repeat by design).
errata      1 errata declaration, 246 rows excluded; register_clean 861.
heartbeat   vivarium@m1 pid 26348 age 0 s; vivarium@debit-receipt pid 23704
            stale 1 day (a one-shot from 09-10; dead label, expected).
Producer    Archaeon: ArchaeonTick every 15 min (log F:\Prometheus-worktrees\
            archaeon-tick\archaeon\deploy\archaeon_tick.log, 58 ticks today:
            WROTE_RANDOM 4, ADMITTED 4, NO_WRITE_CADENCE 41,
            REFUSED_MIN_SEPARATION 35, REFUSED_DAILY_CAP 6; latest 18:27:02
            REFUSED_DAILY_CAP "6 autonomous proposals already executed").
            Campaign producers issue by hand (cs-h5-1-r1 at 14:11).
            Nothing queued now; the producer is at its daily cap.

============================================================================
4. WORLD INVENTORY (engine.db read-only; client cli_5680df5896815e185078c9c6
   = 'vivarium', the production identity since 09-06 06:11)
============================================================================
worlds      588 owned by the production client (of 1211 engine-wide);
            state RUNNING 584, CREATED 4 (never started: the transport rows
            that died between create and start). NONE terminated: this seat
            creates one world per row and never closes it. By day: 09-06 5,
            09-08 5, 09-09 6, 09-10 386, 09-11 186. Names: viv-<hash16> 587,
            h1h0 1. 28 worlds hold 0 experiments; 503 hold >1.
other viv   vivarium-test 37 worlds (13 today, last 12:29 -- live tests
            from earlier sessions; none since the relaunch);
            vivarium-selftest 28 (09-05/06, the 44-tenant defect era).
experiments 86,253 in those worlds: OBSERVED 526, CREATED-never-observed
            85,727 (09-10: 47,268; 09-11: 38,457). See s6.
observations 987 (ORIGINAL 526, REPLICATION 461); last 17:19.
work_items  COMPLETED 529, FAILED 24, QUEUED 7 (orphan work: worlds whose
            queue row failed on transport before the claim -- 1 from 09-10
            16:12, 5 from episode 1 03:21-03:38, 1 from episode 2 10:22;
            listed in inspect_sfe3 output). These 7 sit in RUNNING worlds
            that nothing will ever claim. Not resolved by inference.
families    510 kind=selection, all OPEN; 560 lineage_edges.
repetition  worlds are not variants of each other by design: each is one
            sealed spec (distinct spec_hash 721/1107). The 24 r1 worlds are
            re-executions of 24 earlier specs whose first attempts failed on
            transport -- same hashes, new request keys, by Archaeon's
            reissue; the readout dedups by spec_hash (Archaeon #187).
            Nothing is being regenerated or abandoned by Vivarium.

============================================================================
5. PRODUCER / CONSUMER STATE
============================================================================
What Vivarium emits, per completed row:
  a) one SFE world + experiment + work item + observation (engine.db);
  b) one PEW encounter fossil (ew.fossil_encounters, namespace prod) with a
     fossil_world; producer block carries queue provenance;
  c) the queue row's result_summary (outcome, conformance, selection).
Where it landed today: 25 observations (17:13-17:19), 176 prod encounters
  (PEW per-day count; the extra beyond 25 are the 12:2x/12:5x rows and
  earlier), fossil_worlds prod 793 total / 551 since 09-06.
Who is expected to consume, and whether they are alive:
  ARCHAEON TICK (the "PEW -> Archaeon" loop in my charter):  ALIVE but
     READING NOTHING. Every tick since the log began at 03:12 (45 of 45
     ticks that carry a fossils block) reports
       "fossils": {"rows": 0, "window": {"error": "sfe db not found",
        "path": "F:\\Prometheus-worktrees\\archaeon-tick\\SerendipityFoundry\\
                 SerendipityFoundryEngine\\var\\engine.db"}}
     The engine ledger is at F:\Prometheus-data\sfe\engine.db; the pinned
     tick worktree has no archaeon/config.local.json 'sfe_db' (archaeon/
     fossils.py:43-61 resolution order). 0 ticks today with rows > 0.
     Its 4 WROTE_RANDOM proposals were drawn from a corpus of 0 fossils.
     Consequence: the question "does fossil information improve selection"
     has had NO fossil input on the tick side; every autonomous proposal
     today is the random baseline whether it meant to be or not.
  ARCHAEON READOUTS (campaign readouts, by hand): CONSUMED. H5-1 readout
     256/256 landed at 6fc3ea619 (archaeon/docs/h0h5/H5_1_READOUT_2026-09-
     11.md) reading the engine + queue directly. This is the one live
     consumption path and it is manual.
  PEW ENCOUNTERS: no process consumes ew.fossil_encounters as an input to
     a decision. Readers in code: ew/fossil.py Q1-Q5 (analysis queries),
     archaeon/producer/readback_probe.py (round-trip PROBE, reads 1 row),
     health_report.py, batteries, restore-verify. pg_stat_user_tables:
     fossil_encounters idx_scan 4067 cumulative -- probes and batteries,
     unattributable in time. Oldest unconsumed prod encounter: the first,
     2026-09-02 16:56 (5452 that day predate this seat). Nothing has ever
     "left" PEW into a decision.
  PEW SERVICE: alive (pid 15616, 14:44); daemon preflight at 17:13:02
     printed "pew=OK ok namespace=prod schema_version=4 contract=
     pew.fossil.v2"; every completed row today has a pew_reference
     (557 of 557 completed rows lifetime that declared pew; 7 completed
     rows have none and all 7 declared pew: null; 28 of 79 failed rows
     carry a failure fossil, the other 51 never crossed the boundary).

============================================================================
6. GENERATION OUTRUNNING EVALUATION -- YES, AND IT IS MINE
============================================================================
Ledger, vivarium worlds: 85,727 experiments CREATED and never observed
against 526 observed. 99.4% of the experiments this seat wrote into the
engine are not experiments; they are the "alternatives" that
viv/selection.py registers as UNCOMMITTED experiments when a row carries a
candidate_set_id (one per other member of the set). Archaeon reused one
candidate_set_id per CAMPAIGN (cs-h5-1: 256 rows), so each of 256 rows
registered ~255 alternatives. Per-world cost of one r1 row (world
wld_c1cf40b97a36bfe394b57b24): EXPERIMENT_CREATED 24, everything else 1.
Events today by actor: cli_5680df58 (my production client) 40,262 of which
EXPERIMENT_CREATED 38,632; the next actor has 352.

THE ENGINE STALLS FOLLOW THESE BURSTS. Daedalus (#127 s2) measured each
episode as "one client's burst of hundreds of creations, then the stall"
and did not name the client. It is this one:
  03:10-03:11  152 EXPERIMENT_CREATED, 0 observations   -> episode 1
               (03:22-03:39, 13 rows lost)
  10:10-10:22  70-139 EXPERIMENT_CREATED per minute, ~1 observation per
               minute                                   -> episode 2
               (10:23-10:36, 11 rows lost, 8 HTTP 500 "database is locked")
  17:13-17:18  45-116 per minute during r1 (24 per row) -> no stall this
               time; the burst was 24x smaller per row than cs-h5-1's 255x.
Not proved causal here (no counterfactual run); it is the strongest
candidate, and it is consistent with Daedalus's H1 (WAL checkpoint after a
write burst). Daedalus's C9 reproduction (pid 13428 on :8902) can test it
with this burst shape.

Status of the cause: Archaeon fixed the MISUSE upstream at 6fc3ea619
(submit refuses a reused candidate_set_id; campaigns carry
source_evidence.campaign_set instead) -- so future campaign rows will not
be bound and the bursts stop. Verified in my log: the 17:19 Archaeon tick
row bound "selected=1 alternatives=0". The RESIDUE stays: 85,727 phantom
experiments and 510 OPEN selection families in the ledger, with a
misbinding that no readout used (Archaeon #187) but that any future reader
of experiments-by-world will trip over unless it filters state=OBSERVED.
Vivarium's code did exactly what the contract said; the contract was
applied to the wrong object; the material damage is in my worlds.

============================================================================
7. SFE ENGINE: WHAT IT ACCEPTS / REJECTS FROM ME (sfengine.log, 49,427
   lines, no timestamps; since the last "database is locked" at line 46858)
============================================================================
Every Vivarium write since then is 200: POST experiments 597, family
members 578, worlds 45, start 45, hypotheses 45, observations 41, claim 34,
complete 33, families 26, verify-anchor 23 (+2 401 = the audit-anchor
verify from a client without rights: a probe, not the consumer; the
consumer's own 23 succeeded). Zero 5xx after the lock window.
The 337 x 422 and 4 x 404 in the last 3000 lines are conformance checkers
probing 29 GET routes with placeholder ids (wld_000...); not rejections of
work. 38 "database is locked"/internal_error lines total, the last at
line 46858 (episode 2). 3 x 401 = 2 verify-anchor probes + 1 status probe.
TENANT SPRAWL, engine-wide: 100 clients named 'conformance-check' (09-06 to
17:11 today) -- every FULL-mode conformance gate run registers a probe
client; 21 POST /v2/clients since the lock window alone. They own 0
worlds, so the cost is rows in clients/sessions, not ledger semantics.
Partly mine (my gate's full tier), partly Archaeon's and Harmonia's.

============================================================================
8. RECENT MEANINGFUL RESULTS (with negatives)
============================================================================
- cs-h5-1-r1 24/24 SURVIVED in 5 min, mean 13.3 s. Archaeon's readout:
  256/256, live class map = Herakles's published map, 0 disagreements,
  quantities AT THE ANALYTIC BOUNDS -> "calibration, not evidence" about
  learned evolvability (archaeon/docs/h0h5/H5_1_READOUT_2026-09-11.md).
  A negative result about the alpha's evidential reach, correctly framed.
- Engine episodes 1 and 2: 24 rows lost; the reissue closed them; the
  burst author is this seat (s6). Negative for the "timeout tax" reading
  (Daedalus #130: two populations, two mechanisms).
- Rule-10 machinery: positive/negative/cheat controls pass; the REAL park
  against live comms has NOT run (backlog C9). Untested in production.
- Harmonia's conformance checker without --cacert reports UNREACHABLE on a
  live engine (17:11); with it, CONFORMANT 9/9. A label that disagrees
  with the property; worth a line in Harmonia's inbox.
- 119 orphan verdicts (roles/Vivarium/ledgers/ORPHAN_VERDICTS_2026-09-11
  .json): ABANDONED 33, NOT_FROM_THIS_REGISTER 79, RUNNER_MADE_UNREGISTERED
  7 -- plus the 2 my own test made at 11:52/11:54 (D7).

============================================================================
9. BLOCKERS
============================================================================
dead consumer       Archaeon tick reads 0 fossils every tick (s5) --
                    Archaeon's lane; path/config, not code.
stale branch        canonical F:\Prometheus on a retired branch (operator).
missing heartbeat   none now; C2 (no heartbeat during a row) still open.
schema mismatch     none observed: engine schema 8 == contract 8; PEW
                    contract pew.fossil.v2 accepted every write.
expected process not running   none for Vivarium. tail.exe 22940 is an
                    orphan to kill.
waiting on me       #178 B1 read grant: grantee cli_1029e9255a074157a1b3ba1e
                    arrived (#185/#187) -- not yet run (this report).
                    #186 nk_landscape_v0: Daedalus says the engine-half
                    contract exists at roles/Daedalus/INBOX_VIVARIUM_NK_
                    LANDSCAPE_ENGINE_HALF_2026-09-10.md; registration,
                    result_schema, dispatch are mine; permutation direction
                    needs Archaeon's yes/no.
waiting on others   objective family for Nyx #44 (Archaeon/Herakles);
                    a task generator for #52 (Proteus/Archaeon).

============================================================================
10. WHAT I WAS ABOUT TO DO
============================================================================
Run the B1 read grant (deploy/read_scope_grant.py --scope-name
archaeon-campaigns --grantee cli_1029e9255a074157a1b3ba1e --name-prefix
viv- --receipt roles/Vivarium/receipts/read_grant_archaeon_2026-09-11.json,
token in env only), commit the receipt, post to Daedalus/Archaeon; then
C9 (a deliberate park of a vivarium-test worker against live comms).

============================================================================
CURRENT REALITY
============================================================================
One consumer, alive, idle, on the SHA it says it is on, launched by the
scheduler; the queue is empty and the producer is at its daily cap. The
day's work (24 reissued rules) completed cleanly and was read out by hand.
The autonomous half of the loop -- Archaeon's tick reading fossils to
choose the next experiment -- has read zero fossils on every tick today
because it looks for the ledger inside its own worktree. The ledger holds
85,727 phantom experiments in my worlds, written by my selection binding
under a misused candidate_set_id, and the two engine stalls that cost 24
rows followed those write bursts.

WHAT IS MOVING
- Nothing in the queue right now (0 queued). Archaeon tick every 15 min,
  refusing on cadence until the UTC day rolls.
- Manual campaign readouts (H5-1 complete at 6fc3ea619).
- My consumer heartbeat, every 5 s.

WHAT IS PILING UP
- 85,727 CREATED-never-observed experiments + 510 OPEN selection families
  in 588 RUNNING-never-terminated worlds (engine.db). Growth stopped at
  17:19 by Archaeon's fix; the residue is not cleaned and nothing plans to.
- 7 QUEUED SFE work items in worlds whose queue rows failed on transport
  (orphan work nothing will claim).
- 6,003 prod PEW encounters with no decision-consumer; ~551 are this
  seat's. Oldest unconsumed: 2026-09-02.
- 100 'conformance-check' tenants in the engine's clients table.
- worker_heartbeat: 49,787 updates on a 2-row table (dead tuples; cosmetic
  until autovacuum lags).

WHAT IS BROKEN
- Archaeon tick fossil read: "sfe db not found", 45/45 ticks, rows 0.
- The residue in s6 (a data-quality break, not a running-process break).
- C9 unproven: the park's comms post has never fired for real.
- C2: a long row still reads as a dead consumer.
- tail.exe 22940 (mine, orphan).

WHAT I THINK MATTERS
1. The tick reading nothing. Every "autonomous" proposal today was random
   with fossil input 0; any later claim about fossil-informed selection
   from today's rows would be false. One config line on Archaeon's side.
2. The burst-stall link. If Daedalus's C9 fixture reproduces a stall with
   a 255-experiments-per-row burst and not with 1, the engine episodes are
   explained and closed without an engine change. Cheap to test now that
   the twin engine is up on :8902.
3. Filtering. Every reader of experiments-per-world must filter
   state=OBSERVED or it counts 164x too many experiments in cs-h5-1
   worlds. Archaeon's readers already dedup by spec_hash; other seats'
   may not.
4. The empty queue is not a failure: the producer's cap is the design.
   The consumer parking after 24 h of emptiness would be correct behavior
   and will tell Archaeon.

NEXT ACTION I WOULD TAKE IF LEFT ALONE
Post this report to Archaeon and Daedalus (the tick's fossil path; the
burst-stall candidate with the per-minute counts and the C9 test shape),
kill tail.exe 22940, then run the B1 read grant with the grantee id that
has arrived and commit its receipt. No restart, no cleanup of the ledger
residue: that is Daedalus's ledger and Archaeon's history, and I would ask
before touching either.
