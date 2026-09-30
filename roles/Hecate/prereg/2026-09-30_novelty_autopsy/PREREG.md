# PREREG -- Novelty autopsy (CWO 2026-09-30, Hecate CURRENT)

Frozen: 2026-09-30Z before the detector-reachability run below. Author:
Hecate[m1-dd0c3882]. Order: ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md s3
(comms #1024, #1029; ops/fleet/QUEUE.json). Meta v1 rows are NOT
reinterpreted; this measures the instrument and the flow around them.

## Question

Why did meta v1 report zero UNFAMILIAR mechanisms (0/399)? Discriminate:
C1 never generated; C2 generated then selected out; C3 representation
collapsed distinct mechanisms; C4 ruler mislabelled novelty; C5 familiar
mechanisms had a fitness/economic advantage; C6 the UNFAMILIAR definition
made the target unreachable.

## Part A -- mechanism-flow accounting (deterministic, from committed records)

hecate/autopsy/flow.py counts, per stage, from program.json files and the
probe/Pass 4 reports: generated (interpretations, mechanisms, worlds) ->
admitted (mechanisms behind a probed world) -> survived (valid reading or
SIGNAL; not-testable worlds counted separately) -> flagged (SIGNAL) ->
attacked (Pass 4) -> parked / survived Pass 4. Also: each generator's own
"most likely familiar in disguise" mechanism, and whether the probe
selector (lowest cost) chose worlds built on it more or less often than
chance. No model is called in Part A.

## Part B -- detector reachability (the discriminating experiment)

Input: the NEUTRAL EXACT RULE TEXT (hecate/alien/rules.describe) of the
frozen alien-assay systems whose rule is compact: 20 KNOWN, 32 standard
ALIEN (operationally alien: random tables/polynomials, verified planted
property, passed the mechanical analogue check), 10 DESTROY (compact random
rules without the planted property). 62 items.
Instrument: meta v1's detector UNCHANGED -- hecate/gravity/detector_v1.md,
claude-opus-5-5, isolated call per item, same scrubber, order shuffled with
seed 20260930. No prompt change of any kind.

Decision rules (frozen):
  R1 DETECTOR_CANNOT_REACH_UNFAMILIAR  if UNFAMILIAR rate on ALIEN <= 0.10
     -> meta v1's zero is uninformative about generation; supports C4/C6.
  R2 DETECTOR_DISCRIMINATES            if UNFAMILIAR rate on ALIEN >= 0.50 AND
     on KNOWN <= 0.10 -> meta v1's zero is informative; the cause lies
     upstream (C1/C2/C3/C5).
  R3 PARTIAL                           otherwise; report rates with Wilson
     95% intervals, and the FAMILIAR / COMPOSITE split on ALIEN.
Also reported: nearest-prior names on ALIEN (formalism-level vs mechanism
level is read after scoring and labelled as reading, not verdict).

## Part C -- synthesis

Each cause C1-C6 receives SUPPORTED / WEAKENED / NOT DISCRIMINATED with the
committed rows that bear on it (Parts A, B, the alien pilot REPORT, meta v1
REPORT). A cause with no discriminating data is written NOT DISCRIMINATED
and paired with the smallest experiment that would discriminate it.

## Budget

62 isolated model calls (subscription); no compute to speak of.
