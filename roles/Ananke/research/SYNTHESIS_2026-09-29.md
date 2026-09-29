# Ananke 2026-09-29: instrument arc under MWO-0001..0004 (W-M .. W-U)

Starting state: SYNTHESIS_2026-09-28_ARC3.md. Nine bounded CPU experiments,
each with a frozen PLAN, known-answer plants with must-fail inputs, a
principal re-run of the worker's tests, and a principal spot-check of the
headline numbers. Reports deposited verbatim (deposit.py). Ids: THREADS.md.
Corrections to earlier records: CORRECTIONS_2026-09-29_SWAP_AUDIT.md (raw
records are not edited).

## 1 What the carrier-swap instrument can and cannot say
- The site_acc + chan_acc ~ 1 sum is forced by the mirror-pair design and is
  not evidence of a mixture, nor of the identity holding (W-M). Use SINGLE-
  trial swaps and the S/C/N pattern census: prometheus/ananke/lens_swap.py
  (promoted, 31 tests).
- "Neither" (N) always needs a site AND a channel component; name WHICH with
  the truth-table method (W-P). 4781b0a1's N is an AND/OR of the site latch
  S1 and payload-1 packets in flight.
- On sync physics with update_period > 1, classes must be indexed by
  update-clock phase (W-R). No pooled mixed reading fully resolves: one phase
  is clean, the other is still mixed.
- Recorded CHANCE verdicts: W-N showed low-accuracy CHANCE can be a sample-size
  artifact, but the full audit (W-O, 733 verdicts at 512 worlds) shows 84%
  stay CHANCE; the effect concentrates in HOLD and W-F site_all/joint arms.
- Low-accuracy specimens need a relative verdict (FLIP_REL etc.). Per-verdict
  attainability (W-Q) certifies the 42 low-accuracy transfers the absolute
  rule cannot call; only ~half are complete transfers (W-U paired z CI: 19
  COMPLETE, 18 PARTIAL, 5 ambiguous). The studentized pair bootstrap is the
  only tested interval holding a 1% false-certificate rate at 32 pairs (W-U);
  it is not yet promoted because its power collapses at normal accuracy ~1
  (T-SWAP-REL4).

## 2 What the mechanism chain found
- In three RELAY cells, the mixed clock phase's S vs C outcome per trial is
  one latency-jitter draw on the source's FIRST cue broadcast (W-S, post hoc,
  then confirmed on fresh worlds). The per-trial "mixture" there is delivery
  randomness, not organism state.
- That rule is exact on a designed direct carrier but reaches no other cell
  (W-T): not MAJ 4781b0a1 (dense multi-sensor traffic), not 78f3b0ec (late
  offsets follow the latest broadcast), not e06701a5's split cases. It is a
  property of specific cells, not a law of the update clock.

## 3 Calibration (predictions that failed)
W-N, W-O, W-P, W-R, W-S and W-U each had at least one frozen prediction fail
(listed in their reports). Two frozen primary predictors failed outright and
were replaced only by post-hoc rules confirmed on fresh worlds (W-S) or not at
all. W-O's frozen proportions missed all three.

## 4 Operations
- Fabric leases for every block; one release quirk (needs --lease) recorded
  in FP-001. No Fabric worker can host PTE compute (no torch); native per
  MWO-0004 R3. Migration report: MIGRATION_REPORT_MWO-0002.json.
- CPU envelope: ~55 core-h estimated since 03:43Z exceeded the MWO-0004 R2
  48/24 h reading; new compute on HOLD until the window clears (WORK_STATE).

## 5 Next (when the window clears)
T-SWAP-REL4 (BOOTT/t hybrid, then promote), T-INS-17 (causal-emission
carrier), T-INS-18 (MAJ per-sensor census). Demotion candidate: further
single-cell mechanism chasing (W-T shows poor transfer across cells); prefer
instrument work that every future census uses.
