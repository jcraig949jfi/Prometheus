# NEXT MULTI-DAY CAMPAIGN -- design proposal (Bellerophon, 2026-09-25)

Written because the frozen readiness rule returned READY_FOR_MULTIDAY (COUPLING_CAMPAIGN_REPORT.md s0). This is a
DESIGN, not a preregistration: nothing here is frozen, nothing is launched. A prereg with hashes, a pilot on
off-plan seeds and the operator's go-ahead come first.

## 1. Target

Evolution of machinery that preserves, improves or reorganizes computation BECAUSE computation now finances
reproduction. The coupling campaign showed the channel works (maintenance of seeded code in 6/6 tasks) and that it
closes the loop at the lowest rung (pure copiers acquire ECHO ~5x more often under ON than OFF, YOKED or SHUFFLED;
7 transplants causally coupled). The multi-day run asks what happens ABOVE that rung. It does not re-measure
maintenance and does not collect more replication events.

## 2. Questions (each with the result that would kill it)

Q1 Task-ladder acquisition. Starting from ECHO-competent copiers (the campaign's own causal de novo tapes, plus a
    fresh REP-only lane), does ON coupling on a ladder (ECHO -> INC -> SUM2 -> COND_ONE) produce de novo acquisition
    of the NEXT task above control rates?
    Kill: next-rung acquisition ON <= max(OFF, YOKED, SHUFFLED) + 2 percentage points at the preregistered horizon.
Q2 Protection / modularization. Does task code become protected from copy damage (task bytes outside the
    mutated/overwritten region, copy_covers_task changes, separate task module) under ON relative to YOKED?
    Metric replaces r_cc (F7): child competence under a raised copy-error load, measured on sampled parents in
    isolation, ON-evolved vs YOKED-evolved lineages at matched generation.
    Kill: no ON > YOKED difference in damage-exposed retention.
Q3 Repair becomes common. E2 conflict repair was 4/60 in 500 ticks (F10). Over a long horizon, does the repair
    rate rise above ~7% and do repaired architectures converge on shared mechanism keys?
    Kill: repair rate at the long horizon not above the 500-tick rate.
Q4 Ecology. Do partner-code executors (1-15% of paid correct outputs, report s2) become a stable parasite class
    whose presence changes the evolution of task code (e.g. selection for window placement)?
    Descriptive in the first campaign; confirmatory only if a pilot shows a rate worth testing.

## 3. Lanes (sketch; allocation fixed at prereg)

L1 ladder from ECHO copiers: ON / OFF / YOKED / RANDOM_REWARD; each rung pays only for the next task.
L2 ladder from REP only (fresh-origin control lane; B-cop style): ON / OFF / YOKED.
L3 protection assay: periodic sampled lineages from L1/L2 frozen and tested in isolation under copy-error load.
L4 long E2: REP + BAD at K16, ON / OFF / YOKED, sized for a 7% rate at 80% power.
K16 and K40 both, as separate arms (K40 is where ECHO acquisition was significant; K16 is where base income
cannot sustain pure copiers).
Horizon: 20,000-50,000 ticks (40-100x the campaign), fixed at prereg from the pilot's throughput.

## 4. Controls kept throughout

YOKED (same bonus per tick, no contingency), RANDOM_REWARD, OFF, SHUFFLED on every acquisition lane; A8-type v2
positive reproducer as an instrument check; a constant-twin baseline for every competence metric (score vs best
constant, not vs zero).

## 5. Instrument repairs required before freezing (from the failure ledger)

- F6/F7: replace r_cc/P3/P5 with damage-exposed, baseline-relative heritability and retention.
- F8: drop the enrichment ratio as a selection statistic; use lineage-level fitness from paid births.
- F9: exploit specimens stratified by lane and arm.
- F10: size repair lanes from the observed rate.
- F11: drop ldir_cost4 and CONSTRUCTIVE from generality claims (or redesign them so the null can fail).
- Memory: keep worker recycling; run detached from Claude Code; declare the host dedicated for the window.
- Checkpointing: a multi-day run must checkpoint mid-run state (current runs are 500-tick pure functions; 20k+
  ticks need resumable world snapshots with hashed replay).

## 6. What would stop the campaign early

An integrity failure (void, ledger imbalance, replay mismatch) halts it. No scientific futility stop: dead worlds
are cheap. No tuning after freeze.
