# RB-4 -- BUDGET CURVES AND EFFICIENCY COMPOUNDING, CHARACTERISED PROPERLY (T16, T17, T18, T22)

Medium, autonomous. Estimated 1-2 days. Read RB-00 first.

WHY
  K4: G1's advantage on its own span is a prior over enumeration order. PRISTINE finds
  all 20 L1-only solutions in its own G4 fallback at 8x-3,527x more charges (median
  ~300x).
  K5 (forensic, 6 draws per regime, no transfer arms): with rich supply, G1 donors derive
  and select G1-built second-generation schemas in 11/18 supplies, e.g.
  (acc + gcd({H}, v)) with 6 instantiations, which beat the G1 library on validation.
  PRISTINE donors do so 0/18. This is EFFICIENCY COMPOUNDING inside G1's span, and it is
  the only positive signal in the recursion line. Turn it into a disposition or kill it.

PART A (V1 vs V2) -- budget curves
  For every K2 pool family (86) and every arm {PRISTINE, L1, L1+SHAM (size-matched random
  schema)}, record the charge of the first dev-consistent AND tribunal-qualified hit on 4
  cells, up to a 100M cap. Plot solved-vs-budget. The arms converge => V1 only.
  Non-convergence at 100M => V2 candidate.

PART B (V3) -- preregistered compounding assay
  Draft an AMENDMENT (for Aphrodite to freeze):
    - supply: the K5 G1_PLUS construction, rebuilt from RB-2's or K2's pool, 8 replicates;
    - arms: DONOR_G1, DONOR_P, DONOR_SHAM (sham schema of equal size), and DONOR_G1_ABLATED
      (G1 present in search, hidden from derivation);
    - verdict COMPOUNDING = YES iff DONOR_G1 selects a G1-built schema more often than
      SHAM and ABLATED (sign test), AND the selected G2 beats L1 on TRANSFER families
      (paired, lower95 > 0), AND beats >= half the shams;
    - report MAINTENANCE vs ACQUISITION columns (T22).

PART C (T18) -- multi-generation rate
  4 lineages x 4 generations, each generation's selected library inherited by the next,
  on a fixed rich supply. Measure charges-to-next-selected-abstraction per generation and
  the semantic span of each generation (RB-1 ruler). Include archive-vs-greedy parent
  choice (DGM ablation).
  Accelerating rate + span growth => report to the operator immediately. Plateau is the
  expected result.

DELIVERABLES
  science/frontier/rb4/ (scripts, JSON, EFFICIENCY_COMPOUNDING.md, AMENDMENT draft for
  Part B).
