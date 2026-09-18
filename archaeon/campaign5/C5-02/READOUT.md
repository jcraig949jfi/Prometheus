+=====================================================================+
|  C5-02 -- FAIR LATERAL ECOLOGY: READOUT                               |
|  Archaeon[m2-49ee5a4d]   2026-09-18 14:32Z   attempt of record a01   |
|  Outcome: A_TAKEOVER_WITHOUT_IMPROVEMENT;  PRESERVE_LATERAL: NO      |
+=====================================================================+

Four screened worlds (W2_K2d1 .510, W2_K2_rand .542, W3_K3 .382, W4_K4
.302 best starting parent, all re-measured at run time equal to the
receipt), N=50 from the 57 parents, E=16, six seeds. Lateral arm 100
generations with the C4-09 rescue rule; control arm the SAME worlds and
seeds with NO lateral step, run to the lateral arm's total evaluations
(162-180 generations; every seed within one generation of equal). 12
engine records, 0 errors, 491 s.

-----------------------------------------------------------------------
1. IMPROVEMENT (final held-out of the elite, 48 episodes; band 1/16)
-----------------------------------------------------------------------
  world        lateral mean   control mean   improved seeds   attributable
  W2_K2d1        .531           .531              0/6              0/6
  W2_K2_rand     .530           .545              0/6              0/6
  W3_K3          .368           .372              0/6              0/6
  W4_K4          .305           .300              0/6              0/6
  Twenty-four world x seed cells: the lateral elite never beats the
  control elite by a band, in either direction (largest gap: W2_K2_rand
  seed 4, control .625 vs lateral .531 -- the CONTROL found one more
  step). In 14 of 24 cells the two elites read the same number, and in
  most cells that number is the screen's best STARTING parent (.5417,
  .5104, .3819, .3021): 100-180 generations of selection from these
  lineages do not climb these worlds, with or without lateral entry.

-----------------------------------------------------------------------
2. TAKEOVER
-----------------------------------------------------------------------
  world        rescues (6 seeds)   rescued share of final population
  W2_K2_rand      16 in               .83  (1.00 in 5 seeds)
  W3_K3            9 in               .67
  W4_K4            5 in               .50
  W2_K2d1          3 in               .20
  Rescues per seed 1 / 12 / 24 / 24 / 63 / 9 (133 in all; transfer
  mostly W3_K3 -> W2_K2_rand). Once a rescued lineage enters, it takes
  the population (share 1.0) without moving the elite's held-out. Class
  A's rule (rescued share >= .5 on >= 2 worlds, no world with
  attributable improvement) is met on three worlds.

-----------------------------------------------------------------------
3. THE PREDICTION, LOST
-----------------------------------------------------------------------
  Written before the run: class B on W3_K3 or W4_K4. Neither occurred;
  the attribution test never had an improvement to attribute.

-----------------------------------------------------------------------
4. READING
-----------------------------------------------------------------------
R1  With equal total compute and worlds that provably had headroom, the
    lateral mechanism's only effect is which lineage occupies the
    population. C4-09's "one live world improved in 1 of 3 seeds" does
    not replicate on any of 24 cells.
R2  The stronger fact is the flat elite: the old substrate under the
    frozen grammar does not climb from .38 to anything on K=3, or from
    .30 on K=4, in 180 generations of N=50 -- 36,000 evaluations per
    seed. The screen measured headroom; nothing in Phase A reaches it.
R3  Nothing moved: worlds, rule, seeds, band and outcome classes were
    fixed before the first row (D5-005, DESIGN.md).

For Phase A's disposition: the lateral mechanism is NOT preserved.
+=====================================================================+
