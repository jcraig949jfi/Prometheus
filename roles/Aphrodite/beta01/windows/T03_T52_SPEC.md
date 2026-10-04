# T03 -- T52: VALIDATION-MULTIPLICITY DOSE RESPONSE OF A23-GEOMETRY SELECTION (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 3. Frozen in DEV-3, 2026-10-04, before any T03 donor ran. Threads TH-018 (rung R3
SELECTABLE), TH-021. Evidence tier 2. A NEW experiment; A23's label is not changed.

## 1. Question
A23 (E-011) gave each abstraction's VALIDATE 2 instances of its planted motif m_A, and selection then returned
compositions EQUAL to m_A. Is that selection driven by the NUMBER of direct examples of the planted structure? Is it
recovery of the structure shown, rather than abstraction that generalises past the examples?

**Single-factor manipulation (dose d).** In A23's own replicate (same OBSERVE families, the other abstractions'
VALIDATE families, panel, composition move, paired selection, R_VAL, escrow, TAG=A23 cell labels), ONLY abstraction
A's two VALIDATE motif slots change:
- d = 0: 0 m_A instances + 2 spare instances of A's OTHER motif o_A;
- d = 1: 1 m_A instance + 1 o_A spare;
- d = 2: A23 as run.

Spares are qualified A23 foundry rows of source `r|A|OTHER` with p_PRISTINE <= 0.75, never used by A23 as
TRANSFER. Each is screened as extensionally DISTINCT from the kept motif family (supply.interchangeable, T4 v1a).
Arms (held = arm, composition on): G1, SHAM_0, SHAM_1, SHAM_2. Replicates: A23's 10 fillable.

## 2. Frozen identities
- Runner: `engine/v2b/t52_dose.py`, sha256 `e7b6cef22c8eeadf1d1bdf68ba1a0064f44cffcf2739b3f31ce292ef9644a93b`.
- Plan: `beta01/runs/T03_T52/T52_PLAN.json`, sha256 `0eb9e979add72ee363c742f099a548e26f4cb5651d714cda742fb9b8a1d49233`.
  - 86 donor jobs: dose 0 has 37, dose 1 has 39, plus 10 dose-2 G1 continuity jobs.
  - 4 cells are SUPPLY_LIMITED, all SHAM_2: 1|0, 1|1, 2|0, 3|0.
- The donor uses A23's frozen instruments (tribunal T4 v1, ruler v2 inside a18.donor), because the question is about
  A23's selector. The readout classing (RECOVERED = EQUAL under ruler v2.1) is v2b.

## 3. Measurement gate (it can fail)
- CONTINUITY: the dose-2 G1 re-runs must reproduce A23's selected_schema in >= n-1 of the 10. Otherwise
  MEASUREMENT_FAILED (the re-run would not be measuring A23's selector).
- SUPPLY: >= 32 of 40 (rep, arm) cells per dose. Otherwise SUPPLY_LIMITED.
- Technical: up to 3 reruns.

## 4. Frozen readouts
Per arm and pooled (ALL), at each dose:
- SELECTED_COMPOSITION (COMPOSES_held);
- RECOVERED_MOTIF (selection EQUAL m_A);
- RECOVERED_OTHER (selection EQUAL o_A);
- motif_was_candidate (m_A passes the exact hits_any_cell screen on these validation cells);
- chance_recovery = sum over donors of 1 / n_composed_candidates.

Dose 2 comes from A23's own donors, which are identical inputs, continuity-checked on G1.

| Readout | Definition |
|---|---|
| R_RECOVERY_DOSE | the pooled recovery rate at d = 0, 1, 2 |
| R_FOLLOWS_SHOWN_STRUCTURE | the pooled RECOVERED_OTHER rate at d = 0 (the selector picks whichever composition was SHOWN) |
| R_ONE_EXAMPLE_SUFFICES | recovery(1) >= 0.8 x recovery(2) |

## 5. Interpretation table (frozen)

| Pattern | Reading |
|---|---|
| recovery(0) near chance AND R_FOLLOWS_SHOWN_STRUCTURE high | selection reproduces the structure shown in VALIDATE. In A23's geometry the "stepping stone" is selection of a SHOWN composition, not abstraction generalising beyond its examples |
| recovery(0) well above chance | selection reaches the planted motif without direct examples, i.e. evidence of generalisation from OBSERVE/other structure |
| R_ONE_EXAMPLE_SUFFICES true | multiplicity is not what drove A23's selection; one example suffices |
| R_ONE_EXAMPLE_SUFFICES false | A23's selection depended on seeing the planted structure twice |
| motif_was_candidate = 0 at d = 0 | m_A cannot even enter selection without an example (the exact screen requires a hit). The R3 limit is CANDIDACY (R1/R2), not preference. Recorded as such, never as NO |

## 6. Compute
86 donors x about 7 min, so about 10 CPU-h. M4, 4 workers, about 2.5-3 h. Inside R2.
