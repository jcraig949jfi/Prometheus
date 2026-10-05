# T05 -- R7 GTC IMPROVER-MUTABILITY PROBE: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 5, TEST window 5. Rung R7 (necessary-condition probe). Program P2 (kept separate
from the compounding dispositions). Evidence tier 2. Spec: beta01/windows/T05_GTC_SPEC.md.

## 1. Dispositions
- **Technical: CLEAN.** 20 two-generation chains (40 donors) + 400 scoring walks; about 15 min on 4 M4 workers.
- **Scientific: INCONCLUSIVE_INSTRUMENT** (frozen rule): the planted overfitter g5 did not show the dev-win /
  unseen-loss pattern. Nothing is read about g2, g3 or g4.

## 2. Data
Solved held-out families (cap 1M), per chain 0-3:

| Genome | gen 1 DEV | gen 1 UNSEEN | gen 2 DEV | gen 2 UNSEEN |
|---|---|---|---|---|
| g0, g2, g3, g4 (identical) | 7, 3, 9, 7 | 4, 2, 5, 6 | 7, 9, 9, 7 | 4, 2, 5, 6 |
| g5 | 6, 3, 5, 6 | 4, 2, 5, 6 | 6, 5, 6, 6 | 4, 2, 5, 6 |
| PRISTINE (reference) | 4, 3, 5, 6 | 4, 2, 5, 6 | (same) | (same) |

Genome variance share (UNSEEN, gen 2) = 0.000. g5: DEV -15, UNSEEN 0.

Reporting defect (non-verdict): the runner's PRISTINE reference rows are duplicated once per genome chain (5x). The
reference values above are de-duplicated. The verdict did not use the reference.

## 3. Diagnosis (why the instrument could not see)
1. **UNSEEN is a transfer floor for every library.** Every genome's UNSEEN value equals PRISTINE's in every chain.
   The only abstraction the improver derives on this supply (the G1 class: (acc +/- {H}), ({H} + v)) never helps
   the UNSEEN-stratum families (top-level *, //, %, gcd, pow). So no genome can show unseen transfer, and an
   overfitter cannot show an unseen LOSS. This is W4's anticipated Step-2 floor, now measured on the unseen
   stratum.
2. **g2, g3 and g4 are output-inert at this resolution.** In all 20 chains they select the same schema as g0 and
   score identically. g2 observes more (9-13 vs 5-7 observations) but selects the same. g3 and g4 change
   ordering/insertion, which affects charges, but the solved-within-1M count cannot see efficiency.
3. **The g5 overfitter loses on DEV** instead of winning. Observed-finals entries miss the held-out DEV families'
   finals, so the planted "dev-win" premise (W4 P-B) does not hold on this supply.

## 4. Reading (bounded; not NO)
- The probe is INCONCLUSIVE, by its frozen rule.
- **A descriptive fact worth recording:** the four content-free improver rules tried change the improver's SELECTIONS
  in 0 of 20 chain-generations relative to I_0, with g5 the exception in 2 chains. In this world, at this escrow,
  what the improver selects is determined by the supply. These rule-level levers do not move it.
- **R7 status:** no evidence of improver change. The available levers are, at best, efficiency-only (unmeasured
  here).

## 5. What a repaired probe needs (DEV-6)
- A charge-based endpoint (D deltas, not solved counts), so efficiency levers are visible.
- An UNSEEN stratum where SOME library can help: unseen-by-construction but reachable by a derivable class. For
  example, held-out families of a different base class that the donor CAN derive, or an unseen seed of the same
  generator. Without it, transfer is unmeasurable.
- An overfitter control whose dev win is demonstrated on the dev supply before freezing (a known-answer check of
  the control itself; T02's lesson).

## 6. Attack questions
1. Is "selection invariant to improver rules" a property of the rules, or of a supply that offers essentially one
   derivable class?
2. Should R7 be probed with a rule that changes PROPOSAL (what can become a candidate) rather than ordering or
   insertion? T52 showed candidacy is the binding limit.
3. Is the LIN supply too narrow (its base class dominates) for any improver-level effect to appear?
