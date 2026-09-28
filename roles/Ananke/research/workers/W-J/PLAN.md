# W-J PLAN: do receiver semantics shape which mechanisms emerge?

Written 2026-09-28 BEFORE any W-J experiment or C1 outcome tabulation.
Namespace 0x5EF. Thresholds below are frozen; they are not changed after
results.

Read before this plan (raw evidence): prometheus/ananke/engine.py, lens.py,
physics.py, envs.py, search.py; Aether AETHER_SPEC (arbitration),
PHYSICS_SPEC_DRAFT, AETH-03 PHYSICS_DESIGN_02/03, RCV_REINTERPRETATION,
RESEARCH_BLOCK_SYNTHESIS (origin/main, read-only). W-C PLAN/NOTES/X4_RESULT
and x4_evolve.py (listed as raw evidence in my brief, but NOTES contains
W-C's interpretation: logged as context contamination in LOG.md). NOT read:
SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD, ARC3_PRIORITIES, any REPORT.md.
I have seen the C1 row counts per (collision, cap) and per family, NOT any
outcome by collision.

## Semantics being compared (from code)
- SUM (PTE collision none, or cap 0): receiver reads per (channel,
  component) Sigma payload and count k. Commutative group op; no source id.
- ALOHA (PTE aloha, cap c): (Sigma, k) if k <= c else nothing (erasure).
- SAT (PTE saturate, cap c): if k > c, Sigma and k rescaled by c/k (mean-like).
- ARB (Aether): hash-lottery winner (content- and timing-independent)
  REPLACES a byte; no count; sender picks the target field (code writable).

## E1. Observational test on existing C1 evolved cells (no new runs)
Population: every C1 row with result.held (evolved champions). Semantics
class per row: SUM if collision none or cap 0; ALOHA if aloha and cap>0;
SAT if saturate and cap>0. Outcomes: CC = "communicating competent" =
held lo99 >= 0.60 AND comm_delta_lo99 > 0; also mean held acc and mean
comm_delta. 99% bootstrap CIs over cells.
Predictions (from the formal statement: aggregation across senders is the
thing SUM makes free and ALOHA destroys):
 E1-P1 MAJ: CC share SUM - ALOHA >= 0.05 (point estimate), with ALOHA the
       lowest of the three.
 E1-P2 Interaction: (SUM - ALOHA) CC gap is larger for MAJ than for RELAY.
 E1-P3 Within ALOHA, CC share (all families) is higher at cap 4 than cap 1.
Caveat declared now: C1 cells vary every other dial; E1 is correlational.
If n per MAJ class < 15, E1 is reported as UNDERPOWERED, not as a result.

## E2. Discriminating evolution experiment (designed here; PLAN addendum
## with the concrete base physics is written before it runs)
Arms differ ONLY in the receiver combine operator, evaluated in a
W-J-local World subclass (engine.py untouched): SUM (native), ALOHA1
(native aloha cap 1), ARB (variant: per (slot, recipient, channel) the
arrival with the largest state-free hash priority wins and REPLACES; count
exposed as presence 0/1). Tasks: MAJ (5 senders must be aggregated) and
RELAY (one sender). Fresh searches, C1 SearchSpec, >= 3 seeds per arm.
Predictions:
 E2-P1 RELAY: |median held acc SUM - ARB| < 0.05 (single source: operator
       irrelevant).
 E2-P2 MAJ: median held acc SUM - ARB >= 0.05.
 E2-P3 ARB MAJ champions above 0.72 held acc (one-shot single-sample bound
       0.70) exist only if the actuator integrates over >= 2 arrival ticks
       (temporal integration replaces spatial summation).
 E2-P4 ALOHA1 champions emit less than SUM champions (held emit_rate
       median lower) on MAJ.
Run only if a GPU lease is free and total wall < 60 min.

## E2 ADDENDUM (written after E1, before any E2 run)
Base physics = C1 cell f6b623cdb23afd2c (ring 100, radius 3, dest all,
fanout 8, loss .3, dup .1, noise 64, lat_base 4, async p .8, P=4, C=4),
chosen because the matched block of E1 lives there. Arms change ONLY the
receiver operator: SUM (collision none), SAT2 (saturate cap 2), ALOHA2
(aloha cap 2), ARB (W-J subclass: per (arrival slot, recipient, channel)
one winner by state-free hash priority keyed on (world seed, tick, sender,
copy); a delivery REPLACES the inbox (Acc_sum, Acc_cnt) of that channel;
count exposed as 0/1). Tasks: MAJ (f6b6's env) and RELAY (same d, delta).
4 search seeds per arm x task (32 searches), C1 SearchSpec of f6b6.
GPU lease, ~30 min.
Added predictions (frozen now):
 E2-P5 MAJ median held acc: SAT2 > SUM (replicates E1 block).
 E2-P6 Semantics transfer matrix: every champion is re-evaluated on the
       same 64 held worlds under all 4 operators. On MAJ, the mean
       own-operator advantage (acc own - mean acc under the 3 others) is
       > 0.03 for at least 3 of 4 arms (codes are adapted to their operator).
 E2-P7 SUM-evolved MAJ champions lose more under ARB than ARB-evolved MAJ
       champions lose under SUM.
 E2-P3 operationalised: actuator amnesia hook (zero actuator S, Acc_sum,
       Acc_cnt after tick ro-2 for every scored trial). "Integrates over >= 2
       arrival ticks" = amnesia drops acc by >= 0.05 (pair CI hi < normal lo).
Competence gate for code-class claims: held lo99 >= 0.55.

## E3 (written 05:15Z, GPU BUSY so E2 queued; before any E3 run)
Existing matched champions: 18 C1 cells with physics/env/SearchSpec
identical to f6b623cd except the operator: SUM 10 (collision none),
ALOHA2 3, SAT2 5. Re-evaluate each champion on 64 held worlds
(world_seeds(H(0x5EF,0xE3),64)) under SUM, SAT2, ALOHA2, ARB (CPU, 2
threads). Own-operator probes: amnesia ro-2, payload/count/inbox/S swaps
at ro-1 (as E2). Predictions:
 E3-P1 SAT-evolved mean drop (own -> SUM) >= 0.03, and larger than the
       SUM-evolved mean drop (own -> SAT2).
 E3-P2 Under ARB every class drops >= 0.03 on mean relative to own operator
       (aggregation is destroyed).
 E3-P3 ALOHA2 champions: |acc under SUM - acc under ALOHA2| < 0.03 (codes that
       survive erasure need no erasure).
 E3-P4 Among competent champions (own lo99 >= .55), the inbox swap at ro-1
       FLIPs or goes to CHANCE more often than the S swap in SUM/SAT
       champions (the bit is in the arrivals, not in stored actuator state)
       -- weak, descriptive.

## E2 ADDENDUM 2 (05:20Z, after A9/A10, before any E2 run)
 E2-P8 On MAJ, median held emit_rate of SAT2 champions > 0.2 and > 5x the
       SUM median (normalisation selects dense relaying / averaging codes;
       raw sums select sparse source-only codes).
 E2-P9 Dense (emit_rate >= .2) MAJ champions from any arm lose >= .05 when
       moved to SUM, if they were evolved under SAT2 (transfer matrix).

## E4 (05:42Z, before running): search-time head start in the randomized census
Data: C1 wave A0 census (5000 cells, levels drawn at random; gen-0 random
genomes only). Per cell gen0 fields: frac_contrast_pos (share of random
genomes whose actuator moves with the target), acc_max, frac_emitting,
collide_frac. Class by operator as E1 (SUM/SAT/ALOHA).
 E4-P1 MAJ and RELAY: mean frac_contrast_pos SAT > SUM (normalisation gives
       random programs a head start), with the SAT - SUM difference's 99%
       CI excluding 0 in at least one of the two families.
 E4-P2 ALOHA < SUM on the same statistic in MAJ (erasure removes signal).
Descriptive only (gen-0 != selection), reported with CIs.
