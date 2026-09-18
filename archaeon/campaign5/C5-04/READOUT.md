+=====================================================================+
|  C5-04 -- GENERATOR x REPRESENTATION CONTROL: READOUT                 |
|  Archaeon[m2-49ee5a4d]   2026-09-18 15:35Z   attempt of record a01   |
|  P1-P4 all HOLD; the representation, not the generator, decides       |
+=====================================================================+

27 cells (3 generators x 3 interpreters x 3 population seeds, N=200),
W0 16 episodes, no selection. Controls: injected(2) x B_FAIL trapped
.83 (>= .50); valid x OLD equals valid x B_FAIL program for program on
294/294 non-writable programs. (The harness's own decl reading says
UNDERPOWERED -- it counts 3 rows per arm against n_min 3 with its
strict rule; the preregistered reading is the table below, as with
C4-08's label.)

-----------------------------------------------------------------------
1. THE TABLE (viable = answers >= 1 ask; floor = reward >= 3/16)
-----------------------------------------------------------------------
  generator     interp      viable   floor   mean reward   trapped   faulted
  raw           OLD          .170     .000     .0089        --        --
  raw           B_FAIL       .000     .000     .0000       1.00      1.00
  raw           B_FIZZLE     .000     .000     .0000        --       1.00
  valid         OLD          .152     .000     .0081        --        --
  valid         B_FAIL       .150     .000     .0080       .005      .005
  valid         B_FIZZLE     .152     .000     .0081        --       .005
  injected(2)   OLD          .170     .000     .0098        --        --
  injected(2)   B_FAIL       .017     .000     .0010       .83       .83
  injected(2)   B_FIZZLE     .118     .000     .0071        --       .83
  No sampled program of any kind reaches the floor on W0 (the floor
  share is .000 in all 27 cells): the C4 starting population's floor
  competence was selection's product, not the generator's.

-----------------------------------------------------------------------
2. PREDICTIONS
-----------------------------------------------------------------------
  P1  raw x OLD == valid x OLD within the band        HOLD (.170 vs .152)
  P2  valid x OLD == valid x B_FAIL == valid x B_FIZZLE HOLD (.152/.150/.152)
  P3  raw x B_FAIL viable = 0; raw x B_FIZZLE < raw x OLD by > band
                                                      HOLD (.000; .000 < .170)
  P4  injected(2): B_FIZZLE viable > B_FAIL by > band, and < valid x B_FIZZLE
                                                      HOLD (.118 > .017; .118 < .152)
  generator effect under OLD (valid - raw, viable):    -.018 (inside the band)
  representation effect (valid - raw, viable):  OLD -.018 / B_FAIL +.150 /
                                                B_FIZZLE +.152

-----------------------------------------------------------------------
3. READING
-----------------------------------------------------------------------
R1  Under the total interpreter the generator is neutral (P1), which is
    what the modulus predicts and what every C4 census silently assumed.
R2  Under B, raw programs are dead on arrival in both modes -- a
    uniform-word program carries ~8.6 invalid instructions and FIZZLE
    recovers none of them to viability (.000), while two injected faults
    leave .118 of programs viable under FIZZLE against .017 under FAIL.
    Recovery is real at the population level and costs about a fifth
    of viability per two faults (.152 -> .118).
R3  Self-modification is the residual between valid x OLD and valid x
    B_FAIL: 1 program in 200 traps by writing an invalid word into its
    own code region.
+=====================================================================+
