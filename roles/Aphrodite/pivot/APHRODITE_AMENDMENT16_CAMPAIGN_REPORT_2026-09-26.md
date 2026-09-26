+==============================================================================+
|  APHRODITE -- AMENDMENT 16 CAMPAIGN REPORT, second execution (AMENDMENT 17) |
|  Author: Aphrodite (RSI seat), host harry1 / M4.  Date: 2026-09-26           |
|  For: James (HITL) and external reviewers. Self-contained.                   |
+==============================================================================+

Prereg: engine/AMENDMENT_17_2026-09-26.md @ 373d7ef28, frozen before any gate run or draw
(T0 13:26:55Z). Code a17.py @ 373d7ef28 (a16.py untouched). Gate @ 9adb83f6c.
AMENDMENT 15 stands: BRSI = NO, INTERPRETATION = UNTESTABLE_CATALOG (not redrawn).
GLOBAL_BEHAVIOR_IDENTITY = FAIL (permanent). Campaign 1 frozen and unrun. No G3.

------------------------------------------------------------------------------
0. DISPOSITIONS
------------------------------------------------------------------------------
  CATALOG_A = CATALOG_TESTABLE  roles {'OBSERVE': 4, 'TRANSFER': 4, 'VALIDATE': 3}  pool sha 82a242902253
    per stratum accepted/evaluated: {'add': '4/20', 'fdiv': '1/32', 'gcd': '2/32', 'mod': '0/32', 'mul': '0/32', 'powr': '0/32', 'sub': '4/28'}
  CATALOG_B = CATALOG_UNTESTABLE  roles {'OBSERVE': 2, 'TRANSFER': 4, 'VALIDATE': 2}  pool sha f681fc5b823c
    per stratum accepted/evaluated: {'add': '4/22', 'fdiv': '0/32', 'gcd': '0/32', 'mod': '0/32', 'mul': '0/32', 'powr': '0/32', 'sub': '4/26'}
  CATALOG_C = draw stream generated and hashed only (sha 13ccd335018d); never qualified (E3 not triggered)

  E1 (catalog A):
  E1_BOUNDED_RSI = NO
    R1: altered-experience replicates [0, 1, 2, 3, 4, 5, 6, 7]; G1 NEW replicates []; P NEW replicates []
        discordant G1-only 0 / P-only 0; sign-test p = 1.0000; R1 PASS = False
    failed link: R1: no SEMANTICALLY_NEW selection by DONOR_G1
    shams: ['({H} - (acc - first))', '(acc % {H})', 'pow(last, {H})', 'pow(1, {H})', '(first % (0 - {H}))', 'pow(0, pow({H}, last))', 'pow(v, (v + {H}))', '(0 % {H})']

    donor traces (observed classes -> candidate schemas [NEW?] -> selected):
      r0 G1 classes=2  cands=['(acc + {H})']  sel=INHERITED  NEW=False  meta=9101536
      r0 P  classes=0  cands=[]  sel=INHERITED  NEW=False  meta=14732052
      r1 G1 classes=2  cands=['(acc + {H})']  sel=INHERITED  NEW=False  meta=9216639
      r1 P  classes=0  cands=[]  sel=INHERITED  NEW=False  meta=14875942
      r2 G1 classes=2  cands=['(acc + {H})']  sel=INHERITED  NEW=False  meta=9201179
      r2 P  classes=1  cands=[]  sel=INHERITED  NEW=False  meta=14933609
      r3 G1 classes=2  cands=['(acc + {H})']  sel=INHERITED  NEW=False  meta=8570564
      r3 P  classes=1  cands=[]  sel=INHERITED  NEW=False  meta=14818643
      r4 G1 classes=2  cands=['(acc + {H})']  sel=INHERITED  NEW=False  meta=9196468
      r4 P  classes=0  cands=[]  sel=INHERITED  NEW=False  meta=15000000
      r5 G1 classes=2  cands=['(acc + {H})']  sel=INHERITED  NEW=False  meta=8902362
      r5 P  classes=1  cands=[]  sel=INHERITED  NEW=False  meta=14760728
      r6 G1 classes=2  cands=['(acc + {H})']  sel=INHERITED  NEW=False  meta=8645968
      r6 P  classes=0  cands=[]  sel=INHERITED  NEW=False  meta=14904514
      r7 G1 classes=2  cands=['(acc + {H})']  sel=INHERITED  NEW=False  meta=8881989
      r7 P  classes=1  cands=[]  sel=INHERITED  NEW=False  meta=14509521
      (* = SEMANTICALLY_NEW)

  E2 (catalog B):
  E2_BOUNDED_RSI = UNTESTABLE
    reason: CATALOG_UNTESTABLE


  REPLICATED_BOUNDED_RSI = NO  (E1 = NO; E2 = UNTESTABLE -- no replication was possible)
  G4_REPRESENTATIONAL_CEILING = UNTESTABLE
    precondition (1) unmet: E2 never reached donor adjudication (CATALOG_B UNTESTABLE). Not NOT_RUN_TIME_CAP -- time was available.

  S1_NECESSITY = SUPPORTED  (WHOLE recovered 3/3, BODY_ONLY 0/3)
    F1/BODY_ONLY derived [] selected INHERITED RECOVERED False
    F1/WHOLE     derived ['(acc + {H})'] selected SCHEMA_0 RECOVERED True
    F2/BODY_ONLY derived [] selected INHERITED RECOVERED False
    F2/WHOLE     derived ['(acc + {H})'] selected SCHEMA_0 RECOVERED True
    F3/BODY_ONLY derived [] selected INHERITED RECOVERED False
    F3/WHOLE     derived ['(acc + {H})'] selected SCHEMA_0 RECOVERED True
    (F3 above is F3*.) F3* substitution: obs 6 ['fold', '0', '(acc + (v * v))', '(acc + last)'] -> ['fold', '0', '(acc - (v * v))', '(last - acc)'] (certificate PASS True)
    note: F1, F2 and F3* all contain a sum-of-squares observation ONLY in its compensating form (acc - (v * v)) with a negating final. BODY_ONLY anti-unification derives nothing on any of them; whole-program member enumeration + certification recovers (acc + {H}) and selects it on all three (paired saving lower95 61,152-70,026 charges on fresh A17-E4-val cells). This supersedes nothing: the 2026-09-24 execution's INCONCLUSIVE stands as the record of THAT execution (its F3 was not fully adversarial -- the seat's prereg flaw); this execution repaired F3 in the frozen AMENDMENT 17 before running.

------------------------------------------------------------------------------
1. CLOUD, TIME, SPEND
------------------------------------------------------------------------------
  RUNPOD_UNAVAILABLE_TO_APHRODITE; AZURE_UNAVAILABLE_TO_APHRODITE (checked at T0 and at stage boundaries).
  Total cloud spend: $0.00. No remote resource created.
  Total elapsed: 0 h 48 min of the 4 h envelope (T0 13:26:55Z; queue finished 14:07:22Z; report ~14:15Z). Reserve never entered.
  Wall-clock under concurrent stages is CONTAMINATED; all endpoints are charges.

------------------------------------------------------------------------------
2. APPARATUS DEFECTS AND DEVIATIONS
------------------------------------------------------------------------------
  - NONE affecting a decision. Prereg said E1 and E2 would run concurrently at 4 workers each; E2 was UNTESTABLE by catalog, so E1 ran alone at 8 workers (throughput only).
  - Prereg is numbered AMENDMENT 17 because AMENDMENT_16_2026-09-24.md was frozen and already executed once; it instantiates the operator's 'AMENDMENT 16 campaign' structure with new seeds and is never pooled with the 2026-09-24 execution.
  - FINDING (task space, not apparatus): the frozen G4 per-stratum sampler is dominated by degenerate draws. Of 416 evaluated draws, Q3 (hostile tribunal on the TRUE witness artifact) rejected 233 and Q2 (generator qualification) 151; Q4 headroom only 12. mul, mod and powr accepted 0/32 in BOTH catalogs; fdiv and gcd 0/32 in B and 1/32, 2/32 in A. Only add and sub are reliably productive. In this execution one of two catalogs met the quotas (A: O4/V3/T4, only because gcd yielded 2 and fdiv 1; B failed at O2/V2). The 2026-09-24 execution showed the same sparsity in its first wave (mul/fdiv/gcd/powr 0/16).
  - E1 is a VALID negative, not an instrument failure: G1 donors solved hA_add_ah and hA_sub_az on every replicate, both through instantiations of the inherited (acc + {H}) (the sub family via the compensating form); both classes certified PASS; the only derivable schema was (acc + {H}) itself, whose SCHEMA_0 candidate saves 0 over INHERITED, so INHERITED was kept. PRISTINE donors observed 0-1 classes and derived nothing. The fdiv and gcd OBSERVE families were solved by NO donor within escrow, so no donor ever saw a success outside G1's mechanism.
  - Search leverage of G1 remains visible and is NOT a recursion claim: G1 donor meta-charges 8.57M-9.22M vs PRISTINE 14.51M-15.00M on the same observation/validation cells.

------------------------------------------------------------------------------
2b. GATES
------------------------------------------------------------------------------
  G1 conformance GREEN before the gate, the foundry and E1: 21,600 standard + 602,610 whole-program comparisons, 0 mismatches each time.
  FASTEVAL equivalence: 288,000 (program, input) pairs (G4 + 30% G5 bodies; B1/B1_BOUNDARY + random inputs), 0 value/type mismatches -> admitted for every process.
  FAST-Q2 equivalence on 7 PILOT draws (seed APHRODITE/A17/PILOT/v1, never a catalog seed): target vectors identical; 3,000 sampled reachable programs per draw with 0 vector mismatches and every wrong reference vector in the fast set; 0 survivor-count mismatches on 300 calibration samples per draw.
  Contended fast-Q2 timing: ~18 s per call at 8 workers (solo ~6 s). Foundry: 416 draws evaluated in 20.6 min (vs 112 draws in 62 min on 2026-09-24).

------------------------------------------------------------------------------
3. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------
  DOES: (1) E4 -- on three genuinely adversarial observation sets, whole-program member enumeration + certification recovers and selects (acc + {H}) on all three, while body-only anti-unification recovers it on none -- i.e. in this DSL the S1 whole-program identity step is what makes endogenous derivation possible under compensating factorisations. S1_NECESSITY = SUPPORTED. (2) E0 -- the foundry repair works: exact-fast Q2 and checkpointing turned a campaign-killing 62-min wave into a 20-min complete foundry, with every decision gated equal to the reference.
  DOES: (3) E1 -- a first VALID donor-level test of recursion on a treatment-blind catalog: G1_INHERITED donors did NOT produce a semantically new abstraction. They only met successes their inherited abstraction already explained, and re-derived it. BOUNDED_RSI = NO under AMENDMENT 17 E1 (R1 novelty failure).
  DOES NOT: establish or refute recursion in general. n = one catalog; E2 (replication) was UNTESTABLE by catalog; E3 (representation ceiling) never became eligible. The E1 negative is conditional on this G4 task distribution, in which the only reliably qualifiable families are additive/subtractive folds -- exactly G1's home ground, so the observe set could hardly have shown G1 anything new. That is the most important caveat and it is about the task supply, not the improver.
  Nothing here is Campaign 1 evidence. BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO under AMENDMENT 15 (UNTESTABLE_CATALOG) stands unchanged alongside this result.
  IF CONTINUED (operator's choice; 'stop' is first-class): the binding constraint is now family SUPPLY for non-additive operators, not compute. A foundry whose candidate distribution excludes degenerate witnesses before Q2/Q3 (e.g. division/mod by constant 0, pow with non-positive bases) would be a new preregistered sampler -- a design choice for the operator, not a repair.

------------------------------------------------------------------------------
4. ARTIFACTS
------------------------------------------------------------------------------
  A17_DRAWS / A17_CATALOGS / A17_{A,B}_DONORS / A17_E{1,2,4}_RESULT (roles/Aphrodite/engine/)
  branch aphrodite/a16-campaign-2026-09-26

+==============================================================================+
|  END. 'Not worth continuing' remains a first-class answer.                    |
+==============================================================================+
