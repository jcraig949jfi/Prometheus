+=====================================================================+
|  C5-03 -- REPRESENTATION QUALIFICATION: READOUT                       |
|  Archaeon[m2-49ee5a4d]   2026-09-18 14:32Z                            |
|  a01: REPRESENTATION_FAILURE under the original F3/F6 text            |
|  a02: REPRESENTATION_QUALIFIED under the labelled amendment (D5-008)  |
+=====================================================================+

Representation B (archaeon/campaign5/repb): the Proteus table with a
narrow encoding -- opcode word < 25, read register fields < n_regs,
else FAULT; FAIL ends the evaluation, FIZZLE skips and counts. Proteus's
VM digest unchanged before/after both attempts.

-----------------------------------------------------------------------
1. FIXTURES (same numbers in a01 and a02 except where marked)
-----------------------------------------------------------------------
  F1 canonical identity      57/57 parents on parent env, 57/57 on W0:
                             reward, ops, statuses equal; 0 faults      PASS
  F2 static separability     all-valid share raw .00 / valid 1.00 /
                             injected(k) .00 with invalid == k 1.00
                             for k = 1, 2, 4                             PASS
  F3 dynamic, no fitness     trap share raw 1.00 / valid .01 /
                             injected(2) .84
                             fault-COUNT TVD: raw-valid 1.00,
                             valid-inj2 .83, raw-inj2 .42   <- a01 FAIL
                             fault-SITE  TVD: raw-valid .99,
                             valid-inj2 .83, raw-inj2 .785  <- a02 PASS
  F4 FAIL/FIZZLE coherence   trapped(FAIL) iff faults>0(FIZZLE): 100%
                             on all three populations; 10% of
                             injected(2) answer under FIZZLE; 0 trapped
                             evaluations answered                        PASS
  F5 countable recovery      non-writable injected(k): sites <= k in
                             100% for k=1,2,4 (n=108/101/103); writable
                             k=4: 1% exceed (self-modification mints
                             faults at run time)                         PASS
  F6 determinism             a01 FAIL (volatile wall_s/cpu_s compared);
                             a02 PASS with timings stripped
  F7 undefined is undefined  32/200 raw programs answer under the OLD
                             evaluator and trap under B                  PASS
  F8 grammar B crossing      9.3% of 1,200 children of valid parents
                             leave the encoding: operand_perturbation
                             52% of its children, config_perturbation
                             6% (n_regs shrink), every other operator 0
  controls                   hand-made fault program: FAIL traps at
                             episode 0 tick 0, reward 0; FIZZLE 8 faults
                             at 1 site, 8 outputs; cheat control fails
                             as required                                  PASS

-----------------------------------------------------------------------
2. WHAT a01 -> a02 CHANGED, PLAINLY
-----------------------------------------------------------------------
  a01 failed its own preregistration on two clauses. One was a harness
  defect (F6 compared volatile timings; C4-01 precedent, same fix) and
  one was a fixture that measured the wrong quantity (F3's fault COUNT
  histogram: a fault inside a loop executes hundreds of times, so raw
  programs with eight broken sites and injected programs with two look
  alike by count and unlike by site). The a02 rule measures that one
  pair by distinct SITES at the same .50 threshold. This is a post-hoc
  change of statistic, recorded as D5-008, and the operator may
  overrule it, in which case C5-03 is REPRESENTATION_FAILURE on a01 and
  every Phase-B result after it is void.

-----------------------------------------------------------------------
3. READING
-----------------------------------------------------------------------
R1  The three populations are distinguishable without fitness by two
    independent readers (static validity; distinct fault sites), and
    the old programs' meaning survives transcoding exactly (F1).
R2  Under grammar B the boundary is crossed by exactly one operator
    family (arithmetic perturbation of a raw word) in about one child
    in eleven; every structural operator is boundary-preserving. That
    is the crossing rate Phase B's evolution will meet.
R3  Self-modifying programs can create faults that were not in the
    genome (F5 writable rows): the boundary is dynamic as well as
    static, which C5-05's bins must carry.
+=====================================================================+
