# PACKET_GAPS -- CAMPAIGN_EXP1 Phase 0 (re-gate), worker regate_v01

Currency: 2026-09-28. Fresh worker; inputs: CAMPAIGN_EXP1.md Phase 0,
ACCUMULATION_v0.md s1/s8, sandbox/ (DESIGN, PREREG, AMENDMENTS, RESULT,
code, fixtures), coldstart_A-001/, READY_PROTOCOL.md, plus the operator's
task message. Pure ASCII. BLOCKING = a literal follower could not finish or
would get a wrong result; MINOR = a judgement call I had to make.

G1 MINOR (nearly BLOCKING) -- "D_episode decisional for R0" is ill-typed.
   D_episode is a CONSUMER statistic (S1 intact - S1 with the old record).
   R0 is, per A3, a DECODER-defined rung with no consumer. Applied
   literally, every arm without a working reader (N_a, P_sigma) loses R0,
   which contradicts the original gate ("N_a: R0 expected") and A3. I
   defined E0 = the R0 decoder applied to the 50-gen-old record, made it
   decisional for R0, and reported the literal consumer reading as a
   sensitivity. Neither A8 nor the campaign says which was meant.

G2 MINOR -- the task's example cheat for "defeats D_episode" ("constant
   symbol cycles with a period EQUAL to the episode lag") would be CAUGHT
   by D_episode: at lag = period the old record equals the current one, so
   D_episode = 0. What defeats it is a tag that DIFFERS at the lag (here: a
   4-phase calendar, epoch length 50 with a 25-gen phase offset so that S*
   is mid-epoch). The phase offset matters: with epoch boundaries on
   multiples of 50, S* = 300 falls on a boundary and the cheat's own
   readers are misled (D1 would collapse, and the cheat would be "caught"
   at R1 for a trivial reason).

G3 MINOR -- A8 does not define the different-history twin operationally.
   I used coldstart_A-001's history_twin() unchanged (restore S*-30, rerun
   under another physics stream vs same stream/different coins, mismatch
   of cells written in the last 20 gens), with its constants (n_alt 4,
   back 30, 20-gen window) and thresholds (delta = .05 on a MISMATCH-RATE
   scale, not a success-rate scale). None of these is justified anywhere;
   the delta was designed for success rates.

G4 MINOR -- whether H_hist is computed over the whole record or the cells
   the consumer uses is unspecified. Over the whole record (as built) it
   is defeated by a decoy cell (cheat DECOY here). ACCUMULATION s1 says X
   is "a declared subset of world state"; the sandbox prereg never
   declared X more narrowly than "the nest record".

G5 MINOR -- "two new cheats written by a worker who did not write the
   battery": may a cheat change the PHYSICS (environment family) and
   install clock-driven genome schedules? The calendar cheat needs both.
   I allowed it (the cold-start did the same for T) and added a positive
   control in each new physics (P_cb, P_cal).

G6 MINOR -- sandbox/PACKET.md was NOT updated with A8 as the campaign's
   Hand-off says it must be before Phase 0 ("Phase 0 is suitable for a
   fresh worker once sandbox/PACKET.md is updated with A8"). It still
   describes the cold-start task. I worked from the operator's message.

G7 MINOR -- budget: the original unplanted run took 16 min on 4 workers
   (~60 CPU-min); the task allows 1 process and 45 min total including
   the gate. The full unplanted configuration cannot fit; the campaign
   does not say which arms matter most. I preregistered an order (1016,
   U_sigma, U_id, U_frozen) and a hard stop.

G8 MINOR -- the campaign says "the fixture is never overwritten" but does
   not say what the new fixture is (my gate_v01.json?) nor where the
   repaired battery should live once gated (still a copy under
   regate_v01/; ../battery.py remains the unrepaired one that
   ../run_battery.py uses).

G9 MINOR -- "PASS only if every arm scores as preregistered" -- whether the
   failing CLAUSE of a cheat is part of "the score" is left to the worker
   (the original C criterion included the clause). I made the clause part
   of the gate where the cheat was aimed (T, CAL: H_hist must fail; DECOY:
   must be stopped AT R3, not below), and left the finer predictions
   non-blocking.

G10 RESOLVED -- coldstart G1 (sandbox untracked) is fixed: sandbox/ is in
   git at d3941cb07 (read-only git log). regate_v01/ itself is untracked
   (I was told not to commit).
