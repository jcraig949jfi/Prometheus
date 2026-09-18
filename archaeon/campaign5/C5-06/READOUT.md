+=====================================================================+
|  C5-06 -- LOCAL FAILURE VERSUS LOCAL RECOVERY: READOUT                |
|  Archaeon[m2-49ee5a4d]   2026-09-18 16:20Z   attempt of record a02   |
|  REAL_LOCAL_RECOVERY: 229 replicated recoveries vs 154 losses        |
+=====================================================================+

Input: C5-05's matched rows -- crossing children whose fault is
executed under FIZZLE, from the 47 non-degenerate parents: 1,449
children (v0.4 grammar 1,268; grammar B 181). B_FAIL reads DT on all
1,449 (check). a01 failed before any row was read (the C5-05 artifact
was in the slot directory, not the attempt directory; moved, runner
fixed, a01 preserved). a02: 4 records, 0 errors, 14 s.

-----------------------------------------------------------------------
1. MATCHED CLASSES (the same child under OLD and under B_FIZZLE)
-----------------------------------------------------------------------
  grammar     RECOVERY   BOTH_LIVE   INSULATION_LOSS   BOTH_DIE    n
  v0.4          219         508           123            418     1,268
  B              15          83            34             49       181
  RECOVERY = FIZZLE competent (within a band of the parent) while
  reinterpretation was not; INSULATION_LOSS = the reverse.
  Held-out replication (family heldout index 2, rng seeds 1-3, >= 2/3):
    RECOVERY 229 of 234 replicated; INSULATION_LOSS 154 of 157.
  Gate for C5-07: 229 >= 10 and Wilson lower bound .140 > .01 -> REAL.
  "Merely changed how programs die" (loss >= recovery): NO.

-----------------------------------------------------------------------
2. WHO RECOVERS AND WHO LOSES
-----------------------------------------------------------------------
  by fault kind    RECOVERY    INSULATION_LOSS
    opcode word      209             15
    register field    25            142
  by operator (v0.4 + B)   RECOVERY  BOTH_LIVE  LOSS  BOTH_DIE
    insertion                 102       104       0       21
    replacement                52       119       5      127
    randomization              46        70       9      195
    operand_perturbation       25       156      65       82
    reference_redirection       8       121      60       32
    config_perturbation         1        21      18       10
  OLD's label on the recovered children: D2 167, D3 56, D4 11 (under
  reinterpretation they were dead or broken). Recovered children sit
  at displacement .015 from their parent under FIZZLE; the typical
  event reads parent 1.0 / OLD 0.0 / FIZZLE 1.0 with the fault skipped
  on every pass of a loop (192 faults, one site).

-----------------------------------------------------------------------
3. READING
-----------------------------------------------------------------------
R1  The boundary does not merely change how programs die. An
    out-of-range OPCODE word under the total interpreter becomes some
    other instruction and usually kills; skipped, it is a NOP and the
    program keeps its function (209 of 234 recoveries). An out-of-range
    REGISTER field under the total interpreter wraps to a real register
    and usually keeps working; skipping the whole instruction loses its
    effect (142 of 157 losses). The two encodings fail in opposite
    directions, and the opcode direction is the larger one here.
R2  Insertion is the operator the boundary rescues: an inserted raw
    instruction that is invalid is neutral under FIZZLE (102 recoveries,
    0 losses). Under grammar B, whose insertions are valid, the boundary
    is a 15-event effect in 181.
R3  Recovery is bounded variation, not improvement: no recovered child
    beats its parent (D7 = 0 in C5-05), and the recovered set is at
    displacement .015 -- the program that survives is the parent with a
    hole in it. Whether that hole is a foothold or a cost is C5-07's
    question; whether it discovers more is C5-09's.
+=====================================================================+
