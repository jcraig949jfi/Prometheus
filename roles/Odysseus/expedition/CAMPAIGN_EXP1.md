# Expeditionary campaign 1 -- endogenous accumulation without an installed language

Currency: 2026-09-28. Odysseus. Directive s15 (prepare; do not turn into a
huge campaign yet; design and known-answer controls first; do not spend a
terminal holdout). Status: DESIGN. Apparatus: expedition/sandbox/.
Measurement: expedition/accumulation/ACCUMULATION_v0.md with v0.1
amendments A1-A8. Pure ASCII.

## What the first apparatus run changed about this campaign

The plan assumed the interesting boundary would be at R2/R3 (inheritance,
content). The first unplanted run stalled BELOW R0: readers were selected out
(median reader fraction 0.01-0.02) before any convention could form; the
record helped no arm; a frozen random reader made the record harmful
(-0.094). And the cold-start showed the battery could be fooled by a
history-independent constant record (A8). So the campaign now starts at
R-1 (channel formation) with a re-gated battery.

## Phase 0 -- re-gate the battery (known answers only; no unplanted runs)

- Apply A8: the different-history twin and the episode test become
  decisional for R0 and R3.
- Gate = P, N_a, N_b, C (original) + T "nest tag" (the cold-start cheat)
  + two new cheats written by a worker who did not write the battery.
- Pass condition: every known-answer arm scored as specified at n = 20
  independent worlds (A6 salted seeds); the fixture is never overwritten.

Phase 0 RESULT (2026-09-28, sandbox/regate_v01/RESULT.md): PASS -- 13/13
criteria, 11 arms incl. three cheats (T nest tag, CAL calendar tag, DECOY
decoy cell), originals preserved; unplanted still reaches no rung.

## Phase 1 -- receiver closure precheck (A5)

Before asking an ecology to invent a code, show the reader class CAN hold
one: plant a structured code in writers; does one transmission through the
readers' genome/decision rule preserve it? If not, change the reader class
(raid A: an associative learner could not hold a compositional code; a
one-feature-per-position learner could). A null from a class that cannot
hold a code is uninformative and is not run.

## Phase 2 -- channel formation (R-1): what lets readers and writers co-emerge?

Foreign prior art to test against (signalling games; Lewis conventions;
Skyrms' evolution of signals; sender-receiver co-evolution): signals
evolve when sender and receiver interests align, when signalling and
reading are cheap relative to the benefit, and when a reader can profit
from a record before a convention exists (partial information). Manipulations
(each an arm, >= 20 worlds, the apparatus's own controls):
  C1 read cost: 0 vs positive          (does cost kill readers first?)
  C2 write cost: 0 vs positive
  C3 record noise / decay rate
  C4 shared vs private benefit of a successful read (kin/colony structure)
  C5 environment regularity: none / slow / fast (a record must be able to pay)
  C6 scaffolded start: a fraction of lineages begins with a planted reader
     that is then free to drift (territory I: can a lent channel be kept
     after the plant is diluted?)
Observable: reader fraction, writer fraction, record-action mutual
information over time; R-1 awarded when MI exceeds the no-record twin band
in >= X% of worlds (X in the prereg).
Kill: no manipulation produces R-1 above the band -> in this world class a
channel does not form without being installed; the campaign reports that
as its result and stops before the ladder.

## Phase 3 -- the ladder (only if Phase 2 yields R-1)

R0-R5 per ACCUMULATION v0.1, with every control in s5; convention
invariance with the three outcomes and a semantics audit (A2); both
recompute arms (A1). No word ("language", "culture", "knowledge",
"sagacity") is used unless the rung that earns it is awarded.

## Budget and boundaries

Ordinary CPU only (stdlib; the sandbox runs 20 worlds x arm in minutes on a
laptop); every phase preregistered in its own commit before its runs; all
results EXPLORATORY until a frozen experiment repeats them; no holdout
exists or is spent; the world receives nothing an observer recorded
(DESIGN.md s4 guarantees, audited per phase). Phases 0-2 fit a single node
(ubu001-class) in a day.

## Hand-off

Phase 0 is suitable for a fresh worker once sandbox/PACKET.md is updated
with A8 (READY_PROTOCOL ledger: sandbox NOT READY until re-gated).
