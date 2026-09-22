+=====================================================================+
|  REVIEW PACKET -- CAMPAIGN 4 LAUNCH GATE, ITEM G2 (C4-REH-1)        |
|  Archaeon[m2-49ee5a4d]  (Campaign 4 closure lead, M2 / SPECTREX5)   |
|  Date: 2026-09-18 00:35Z                                            |
|  For: the operator (HITL) and external reviewers                    |
|  Status: G2 GREEN; gate RED on G1 (Daedalus) and G5 (Proteus)       |
|  Self-contained: no repository access needed to critique this.      |
+=====================================================================+

-----------------------------------------------------------------------
0. SUMMARY, MANDATE, VERDICT
-----------------------------------------------------------------------

Mandate (operator, 2026-09-17, resume after reset): converge the Campaign 4
launch gate; finish line = campaign started with a green gate, or a
demonstrated blocker no seat can cross. Do not start C4-01 while RED.

What this packet reports: the integration rehearsal C4-REH-1 (gate item
G2), the one item that was mine, executed end to end and closed GREEN.
It carries NO scientific claim: every unit of work is a no-op kind that
exists to exercise the queue -> engine -> observer path.

Verdict, as measured:
  48 program-variant rows admitted, 48 completed; 1,152 observations
  recorded exactly once; 48 distinct engine worlds; engine-side count
  48/48 exact through the campaign identity's read grant; duplicates 0.
  Two deliberate engine kills. Kill 1 landed between rows. Kill 2 cut a
  request inside the engine; the affected row was released to a second
  attempt by the watchdog machinery with no human command and replayed
  what the engine already held. Observer leg 7/7 gates; the final
  receipt re-derives byte-for-byte from committed files.

Gate after this work: G1 RED (owner Daedalus; their long run lands
~03:45Z), G2 GREEN, G3 GREEN, G4 advisory, G5 RED (owner Proteus; one
remint; Proteus offline since 15:25 local). Campaign 4 NOT started.

-----------------------------------------------------------------------
1. WHAT WAS BUILT, AND WHAT EXISTED BEFORE
-----------------------------------------------------------------------

Existed (previous instance, committed before this session): the 48-unit
bundle (S1), its validation against the executing seat's own contract
module (S2-validate), the accounting invariants declared in the bundle
manifest (observations exactly 1,152; one world per unit; duplicates 0;
lost 0; manual repair 0), the identity tuple, the launch gate reader.

Built this session, committed BEFORE any verdict was read:
  archaeon/campaign4/rehearsal_full.py -- stages S2-enqueue .. S8:
    enqueue (paced), go (posts the restart request), wait (state file
    flushed every 5 s), verify (register + both restart receipts read
    from origin/main + engine read), publish (S6 artifacts), s7 (runs
    the observer seat's one-command leg), s8 (re-derive the receipt),
    receipt (the file the gate reads).
  Timing decision recorded in the driver docstring before the first row:
    a no-op row runs ~0.5-0.7 s, so 48 back-to-back rows drain in under
    a minute, faster than a restart requested by message can meet. Rows
    were therefore admitted with a staggered not-before column (a queue
    column, outside the sealed hash; invariants untouched), and later
    held/lifted through the executing seat's own hold command.

Two defects in MY checks, found and fixed before the verdict, both in
the committed code with comments:
  (a) The engine seat's receipt flag `a6_degraded` is healthy when FALSE.
      My first rule required every flag TRUE and read a healthy receipt
      as failed.
  (b) A REPLAYED observe step re-yields the id the first attempt minted.
      My first "duplicates minted" figure summed replays (it read 7). The
      corrected figure -- distinct ids beyond the declared 24, on the
      register and on the engine -- is 0.

-----------------------------------------------------------------------
2. THE CLAIM AND WHY IT MATTERS
-----------------------------------------------------------------------

Claim (G2): one exact tuple of frozen surfaces -- engine 9.0.1
(699ca0f9, instance eng_906356f7, schema 9), executing build 08081c6ed,
identity profile pfp1:625bc70456ebfa20, observer reader 1.4 / schema 5,
campaign seed 20260921 -- carries a Campaign-4-shaped unit of work from
enqueue to a reproduced receipt THROUGH an engine restart, without
losing, duplicating or silently corrupting a fact.

Why it matters: Campaign 4 will run ~10 experiments unattended with no
operator. A restart that forks identity, loses an observation, or mints
a duplicate would poison every downstream count silently. The rehearsal
is cheap; what it buys is that "Campaign 4" names a machine that was
killed and recovered before any science depended on it.

-----------------------------------------------------------------------
3. DESIGN AS EXECUTED (timeline, UTC, 2026-09-18 unless stated)
-----------------------------------------------------------------------

  23:59:52 (09-17)  48 rows admitted, family C4-REH-1, created_by
                    archaeon, not-before paced 10 s from 00:00:22 to
                    00:08:13; every row carries a declared start bundle
                    naming the Proteus population manifest and the
                    campaign rng identity; validated by the executing
                    seat's bundle module (0 problems).
  23:59:53          Restart request posted to the engine seat (comms 401).
  00:00:22-00:00:37 Rows 1-3 executed, 0.6-0.7 s each, 24 observations
                    each; the executing seat's scope reconcile added each
                    new world to my read scope at the batch boundary.
  00:00:38          KILL 1 (engine seat's tool): 68 engine events in the
                    prior 60 s, 0 write intents open at the instant of the
                    kill, port free after 0.64 s. Row 3 had closed 1 s
                    earlier. The consumer's next claim met the dead engine:
                    conformance gate HALT (UNREACHABLE) at 00:01:05, daemon
                    exited. Shape: engine death BETWEEN rows.
  00:02:47          I HELD the 45 remaining rows (not-before 2026-09-19)
                    so recovery would not drain them in ~40 s.
  00:03:39          Asked the engine seat for a second kill armed on an
                    event-density trigger (comms 402): their tool, one
                    flag. They added --wait-for-events 200 --window 20 and
                    a hold for an OPEN intent (a request inside the
                    engine) and reported ARMED at 00:06 (comms 403).
  00:05:04          Engine back (watchdog). The consumer's dead-man had
                    probed at 00:05:03, one second earlier: not relaunched.
  00:09:57          I LIFTED the 45 rows (not-before cleared).
  00:10:03          Dead-man relaunched the consumer; rows ran back-to-back
                    at ~0.5 s each (7 in 3 s).
  00:10:06          KILL 2: trigger fired; open intent at the kill = POST
                    /v2/worlds/wld_d1940e75.../observations, which did NOT
                    take effect; port free after 0.79 s; 9 requests had
                    been effected after T0 within that 0.79 s.
  00:10:08          Row a/s10 attempt 1 FAILED ENGINE_TRANSPORT
                    ("RemoteDisconnected after the experiment was
                    committed"; 0 observations recorded by the consumer).
                    Consumer PARKED (halt class ENGINE_TRANSPORT), paged the
                    engine seat, exited.
  00:15:04          Engine back (298.5 s after T0, per the engine seat's
                    receipt; identity 8/8 checks equal; chain 55/55
                    events; no duplicate world index). Dead-man probe at
                    00:15:03 again one second early: park not cleared.
  00:20:03          Dead-man cleared the transport park, released a/s10 to
                    attempt 2, relaunched the consumer.
  00:20:36          All 48 rows terminal.
  00:21-00:22       S6 published + committed (87ab74a1a); S7 run against
                    that commit; S8 re-derived the receipt; gate run.
  00:2x             Merged origin/main by named SHA, tests on the merged
                    tree, pushed a4cf33724 (verified ancestor of origin/main).

-----------------------------------------------------------------------
4. RESULTS -- EXACT NUMBERS
-----------------------------------------------------------------------

Register (viv schema on the canonical store; raw dump committed as
archaeon/campaign4/rehearsal/REGISTER_C4-REH-1.json):

  rows admitted / completed / failed        48 / 48 / 0
  distinct engine experiment ids            48
  distinct engine world ids                 48   (expected 48: 1 per unit)
  observations recorded (sum of attempts
    that closed COMPLETED)                  1,152 (declared 1,152)
  units with > 1 attempt                    1  (a/s10: FAILED, COMPLETED)
  step status census, all attempts          NEW 2,544  RECOMPUTED 25
                                            REPLAYED 10  REUSED 1  FAILED 1
  observe steps total / replayed            1,159 / 10
  distinct observation ids beyond 24
    on any unit                             0
  units violating any invariant             0

Engine (read as cmp4-archaeon through grant gnt_2006a1ac, scope
archaeon-campaigns; 77 worlds in scope at read time):

  worlds examined                           48 / 48 (none unreadable)
  worlds with exactly 24 observations
    whose ids equal the register's          48 / 48
  engine instance / source / schema         eng_906356f7 / 699ca0f9 / 9
                                            (unchanged across both kills)
  duplicates minted (engine)                0

The resumed unit a/s10 in detail:
  attempt 1: validate, build, world, experiment, claim NEW; run x24 NEW;
             7 observe NEW; 1 observe FAILED (the cut request);
             closed FAILED / ENGINE_TRANSPORT, observations_recorded 0.
  attempt 2: validate REUSED; build RECOMPUTED; world REPLAYED (same
             world id); experiment REPLAYED (same experiment id); claim
             RECOMPUTED; run x23 RECOMPUTED; observe: 8 REPLAYED (the
             engine had accepted 8 while attempt 1's responses were
             lost), 16 NEW; closed COMPLETED / COMPLETED_ALL_REPEATS,
             observations_recorded 24, censored false.
  engine:    24 observations on that world, ids equal to the register's.

Observer leg (S7; the observer seat's one-command script, run by me with
their written consent, comms 391), at commit 87ab74a1a:
  I1 ingest: 1,517 seen, 97 new (49 from RECEIPT.json, 48 from rows.json),
     0 conflicts       PASS
  I2 second ingest: 0 new, 0 conflicts                          PASS
  I3 campaign-4 rows present: 97 (1 harness, 2 attempts)        PASS
  R1 rebuild x3 equal AND equal to the frozen digests
     (reach_level v1 e7625bfb..., v0 7037fbc4...,
      corridor_edge v1 719fa5a1...)                             PASS
  C1 release check                                              PASS
  F1 frozen surface test                                        PASS
  X1 executing-seat outbox checkpoint: last_seq 184, gaps [],
     duplicate_seqs [] (reported, not gated)                    PASS

Reproduction (S8): RECEIPT.json re-derived from the committed rows.json,
bundle manifest and identity file at 87ab74a1a; sha256 identical,
79a93209...; bytes equal; canonical form equal.

Restart receipts (engine seat, on main 0dfd7bd6f; hashes are sha256 over
the LF git blob):
  k1  restart_C4-REH-1.json     82ec9d5d...  result PASS, between rows,
                                 recovery 266.0 s, invariants ok
  k2  restart_C4-REH-1-k2.json  90097325...  result PASS, MID-REQUEST,
                                 recovery 298.5 s, invariants ok
  The engine seat quoted 79b56b6e... and 4e68cdcf... in chat; those do
  not match the blobs. Most likely CRLF working-copy bytes. Recorded;
  not adjudicated; the blob is the identity by the program's rule.

Tests on the merged tree (origin/main 66f90c39a merged by SHA):
  452 passed, 2 skipped, 1 failed. The failure,
  test_the_configured_sfe_ledger_exists_on_this_host, fails BY DESIGN in
  a linked worktree with no configured ledger path (its docstring says
  so): it flags that the Archaeon tick is not deployed on this host
  (open item ARCH-51). Pre-existing; not caused here; not masked.
  A second test failed once at 00:04Z and passed 16/16 at 00:10Z: a
  row stamped six minutes earlier fell on the previous UTC day. The
  known midnight window; not chased.

-----------------------------------------------------------------------
5. INCIDENTS AND WHAT THEY VALIDATED
-----------------------------------------------------------------------

I-1  Kill 1 missed a live request. A no-op row is ~0.6 s; the engine
     seat's tool fires within a second of its check. Validated: the
     conformance-gate halt path (a consumer that finds a dead engine at
     claim time stops, cleanly, and is relaunched by its dead-man). Did
     NOT validate the keyed retry. Fix: a density trigger (their tool)
     plus my hold/lift of the queue to make the traffic dense.

I-2  Dead-man / watchdog phase. Both recoveries lost a full 5-minute tick
     because the dead-man probed one second before the engine answered
     (00:05:03 vs 00:05:04; 00:15:03 vs 00:15:04). Within the executing
     seat's written bound; reported to them for judgment. In a campaign,
     each engine restart costs ~10 min of consumer time at this phase.

I-3  Engine accepted requests after T0. Nine requests were effected in
     the 0.79 s between the kill signal and the port closing; eight of
     them were observations the consumer never saw acknowledged. This is
     exactly the "landed but unacknowledged" case the keyed retry exists
     for, and attempt 2 REPLAYED all eight rather than minting new ones.
     Validated the plan's central invariant on a real instance.

I-4  My own check defects (section 1, a and b). Both would have produced
     a FALSE verdict (S4 failed, duplicates 7) had I trusted the first
     output. Caught by reading the rows beside the verdict.

I-5  Hash discrepancy on the engine seat's quoted receipt digests
     (section 4). A reviewer verifying from chat would fail to match.

-----------------------------------------------------------------------
6. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------------------------------------

Establishes (n = 1 mid-request cut, n = 1 between-rows cut):
  the tuple carries work through an engine restart with exact-once
  observations, one world per unit, identity unchanged, chain intact,
  observer projections stable, receipt reproducible.

Does NOT establish:
  - behaviour under a restart while the executing seat is mid-WORLD
    creation or mid-EXPERIMENT creation (the cut here was mid-observation;
    the earlier canary covered consumer death, not engine death, at
    other steps);
  - behaviour at campaign rate over hours (that is G1, the engine seat's
    long run, still owed);
  - anything about the science: the work kind is a no-op; the population
    manifest is referenced, not executed;
  - that a real Campaign 4 row (minutes of compute, real artifacts) would
    show the same replay accounting; the replay path was exercised on
    observations only.

Claim ceiling: G2 as written in the plan -- "the seams" -- and no more.

-----------------------------------------------------------------------
7. DECISION / RECOMMENDATION
-----------------------------------------------------------------------

G2 is GREEN by measurement and the receipt the gate reads says so. The
gate still refuses (G1, G5). My lean:
  - G5: wait for the Proteus remint (one field, content unchanged). I
    do not edit another seat's minted artifact. If Proteus stays offline
    past G1 landing, the operator's one-line wake of Proteus is the only
    remaining move; that would be the "blocker no seat can cross" of the
    mandate, and I will say so rather than reach across the lane.
  - G1: nothing to do but read the receipt when it lands.
  - Start C4-01 the moment the gate is green; not before.
Stop is a first-class answer: if a reviewer holds that a single
mid-request cut is too thin a sample for a ten-experiment unattended
campaign, the cheap response is a second density-triggered kill during
C4-01's first real rows, with the same accounting, before C4-02.

-----------------------------------------------------------------------
8. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----------------------------------------------------------------------

Q1  Is one mid-request cut on a no-op kind sufficient evidence for G2, or
    should the gate require the cut to land at each of world / experiment
    / observation creation? What is the cost of the extra rehearsal
    against the cost of a silent fork in C4-03?
Q2  The between-rows halt path costs ~10 min per restart at the observed
    dead-man phase. Is that acceptable for a campaign that may see
    several restarts, or should the launch wait for a tighter probe?
Q3  I ran the observer seat's leg myself under their written consent.
    Does that weaken S7 as independent evidence?
Q4  The pacing (staggered not-before, hold, lift) is a queue-column
    manipulation by the producer. Is there any way it could have altered
    what the invariants measure?
Q5  My two check defects were caught by me. What would have caught them
    if I had not read the rows?

-----------------------------------------------------------------------
9. ARTIFACTS (paths on main; SHAs)
-----------------------------------------------------------------------

  archaeon/campaign4/REHEARSAL_RECEIPT.json          S1..S8, P1..P5
  archaeon/campaign4/LAUNCH_GATE_RECEIPT.json        gate at a4cf33724
  archaeon/campaign4/rehearsal_full.py               the driver
  archaeon/campaign4/rehearsal/STATE_C4-REH-1.json   driver state
  archaeon/campaign4/rehearsal/REGISTER_C4-REH-1.json raw register rows
  archaeon/campaign4/rehearsal/S7_RESULTS_C4-REH-1.json observer leg
  archaeon/campaign4/C4-REH-1/{rows.json,RECEIPT.json,RECORD.md}  S6
  SerendipityFoundry/SerendipityFoundryEngine/deploy/REHEARSAL_RESTART_2026-09/
    restart_C4-REH-1.json, restart_C4-REH-1-k2.json  (engine seat)
  roles/Archaeon/prompts/2026-09-17_c4_convergence/  the four seat asks
  roles/Archaeon/journal/2026-09-17_m2-49ee5a4d.md   the journal
  Commits: cd7f8565c, be82e5a4e, 87ab74a1a (S6), 83568a0a7 (receipt),
           a4cf33724 (merge, pushed), 7d5750fd0 (report + journal).
  Comms: 400 (Proteus G5), 401 (GO), 402 (second kill ask), 403/405
         (engine seat armed / PASS), 407 (G2 GREEN report).

+=====================================================================+
|  END. "Not worth continuing" remains a first-class answer: if the    |
|  reviewer judges one mid-request cut insufficient, say so and the    |
|  next rehearsal runs before C4-02, not after.                        |
+=====================================================================+
