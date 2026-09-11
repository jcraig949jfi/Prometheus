# Preregistration: DID BRANCHING EVER MAKE A FITTER CHILD? (v0, frozen 2026-09-11)

Operator ruling 2026-09-11 s3. Committed BEFORE any outcome is inspected;
the only quantities read from the specimen before freezing are the
eligibility counts below and the reconstruction's positive control
(roles/Arachne/science/specimen.py: 82 of 82 logged parent_fitness
values reproduced within 0.10, 74 within 0.05, max error 0.093; 124 of
124 death rows' total_edges reproduced exactly). The specimen is
roles/Arachne/archive/run_2026-06-04/ at the hashes in its MANIFEST.md;
no new crawl data enters.

## The mechanism that actually ran (not the corrected one)

crawler.py / swarm.py as of 3b9d9ed15 (the whole archive post-dates the
landscape-escape fix 9cb4602bb; the pre-fix run of 20 ticks was NOT
preserved). Facts of the mechanism, all from the code:

- Fitness f(t) = mean over the last 16 steps of (2*new_nodes + new_edges)
  times (1 - 0.6 * mean null_p over the same window); a step with no
  persisted edge contributes progress 0 and null 0.5.
- A crawler BRANCHES when f < 0.6 for 4 consecutive ticks, the population
  is below 12, and its own cooldown (10 ticks) has expired. Branching is
  therefore triggered ONLY at a trough: every parent's f at the branch
  tick is < 0.6 by construction (logged range 0.0 .. 0.585). This is the
  "inverted selection" of the archaeology: reproduction is a symptom of
  struggling, not of success. It was never removed; 9cb4602bb only
  changed WHERE the child lands.
- The child gets the parent's ruleset with ONE knob mutated (max_neighbors,
  novelty_floor, frontier_mode, hop, or reseed_every) and a fresh seed;
  with probability 0.70 it is moved to the least-populated live landscape
  (hop forced off). 50 of 82 children escaped their parent's landscape,
  32 stayed. The 32 are the historical (pre-fix) behaviour; the 50 are
  the fix. Both arms are analysed and reported separately.
- A child is appended during the tick loop and takes its first step the
  NEXT tick. A crawler dies after 12 consecutive zero-progress steps and
  is reaped at the end of that tick. The per-landscape floor spawns a
  FOUNDING-DEFAULT ruleset whenever a landscape has no live crawler (42
  such births) -- a birth without mutation and without a trough parent,
  which is the natural matched control for "mutated child of a
  struggling parent".

## Units and populations

- Unit: one branch event (segment, tick b, parent P, child C). 82 events:
  79 in segment 2 (ticks 1-700, primary), 3 in segment 1 (45 ticks,
  censored; reported separately, never pooled).
- Age of a crawler = tick - born_tick. A "full window" = 16 ticks alive.
- Lifetime = end_tick - born_tick; end_tick = death tick, or 700 if alive
  at the end (right-censored; the 7 alive-at-end are reported as such).

## Fitness measures (defined here, before inspection)

F1  mechanism fitness f(t): the reconstructed crawler.fitness at tick t.
F2  survival: lifetime in ticks (censored at 700).
F3  productivity rate: null-discounted nodes introduced per tick alive =
    sum over the crawler's edges of new_nodes*(1-null_p) / lifetime, where
    new_nodes is fabric-global novelty in append order (what fabric.add
    saw at the time; no hindsight).
F4  raw persisted edges per tick alive.

## Comparisons (each reported with its eligible count)

C1  MECHANISM VIEW: child F1 at age 16 vs parent F1 at tick b (the logged
    parent_fitness). Eligible: child lifetime >= 16 (65 of 82). Known to be
    biased toward "child fitter" because the parent is at its trough by
    construction; reported, never used as the gate.
C2  AGE-MATCHED (primary): child F1 at age 16 vs parent F1 at the parent's
    own age 16. Eligible: both lived >= 16 ticks. Same function, same age,
    different ruleset and start.
C3  CONTEMPORANEOUS: child F1 at tick b+16 vs parent F1 at tick b+16.
    Eligible: parent alive at b+16 (22 of 82) and child alive at b+16.
    Did the child beat the parent's own recovery from the trough?
C4  MATCHED DEFAULT-BIRTH CONTROL (primary for "is the mutation doing
    anything"): child F3 and F2 vs the floor-revived crawler in the SAME
    landscape born NEAREST in tick within the same segment (one control
    per child, reuse allowed, |delta tick| recorded). Eligible: a control
    exists in that landscape (oeis has no floor revivals: children born
    into oeis have no control and are INDETERMINATE for C4).
C5  SURVIVAL: child F2 vs parent F2 (parent's whole lifetime); child F2 vs
    C4 control F2.
C6  ARM SPLIT: every comparison above stratified by ESCAPED (child
    landscape != parent landscape, n=50) vs STAYED (n=32). The STAYED arm
    is what the inverted-selection mechanism did before the fix.

Ties: |difference| <= 0.05 in F1 (the reconstruction's 90th-percentile
error) counts as a tie and is excluded from the sign statistic; the tie
count is reported; sensitivity at 0.10 is reported.

## Statistics and gates (frozen)

- For each comparison: the fraction of non-tied eligible events with
  child > reference, with a Wilson 95% CI, and a two-sided exact binomial
  test against 0.5. Attainable range [0,1]. At n=65 the SE at 0.5 is
  0.062; at n=22 it is 0.107. A comparison with fewer than 20 non-tied
  eligible events is INDETERMINATE (reported, not read).
- Trajectory rows: for every event, F1 of parent and child at ages 0..32
  in steps of 4, plus F2, F3, F4 for parent, child and control. These rows
  ship in the same commit as the readout.

Readings (the ladder; exactly one fires per question):

  Q1 "did branching EVER make a fitter child" (the operator's literal
      question): YES if at least one eligible event has child > parent
      under C2 AND under C3 AND the child survived >= 32 ticks; NO if
      none; INDETERMINATE if C2 or C3 has < 20 eligible events. (The
      answer is expected to be trivially YES for some event; it is
      reported because it was asked, and it is not the finding.)
  Q2 "did branching SYSTEMATICALLY make fitter children": YES only if the
      C2 fraction's 95% CI excludes 0.5 upward AND the C4 (F3) fraction's
      95% CI excludes 0.5 upward -- children beat their parents at the
      same age AND beat fresh default births. MUTATION_DECORATIVE if C2
      excludes 0.5 upward but C4 does not (a fresh start or a landscape
      change explains the gain, not the mutated knob). NO if C2 does not
      exclude 0.5 upward. INDETERMINATE per the eligibility rule.
  Q3 "what did the inverted-selection mechanism do": the STAYED arm's
      C2/C4/C5 read on the same ladder, separately.

## What would change the reading (falsifiers of this analysis itself)

- If the reconstruction's positive control had failed (it did not), no
  F1 comparison could be read; F2-F4 do not depend on it.
- If the tick mapping were off by more than one tick, F1 at age 16 would
  shift by at most one step of a 16-step window; the 0.05 tie band covers
  that.
- Segment 1's 3 events are censored at tick 45 and never pooled.

## Not done here

No crawler is run. The corrected mechanism is not simulated. No claim
about what a different trigger would have produced.
