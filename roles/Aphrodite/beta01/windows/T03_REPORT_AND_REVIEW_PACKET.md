# T03 -- T52 VALIDATION-MULTIPLICITY DOSE RESPONSE: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 3, TEST window 3. Thread TH-018, rung R3 SELECTABLE. Evidence tier 2 (local
engine). A new experiment; A23's label is unchanged.

## 1. Question
In A23's geometry, is selection of the planted motif driven by the number of direct examples in VALIDATE? Is it
recovery of what was shown, rather than abstraction that generalises past the examples?

The design is a single-factor manipulation: only abstraction A's two VALIDATE slots change. Dose d means d
instances of m_A plus (2 - d) instances of A's other motif o_A. Everything else is A23 (spec:
beta01/windows/T03_T52_SPEC.md; runner e7b6cef2; plan 0eb9e979).

## 2. Dispositions
- **Technical: CLEAN.** 86 / 86 donors; about 3 h 05 m on 4 M4 workers; 0 failures.
- **Measurement gate: PASSED.** CONTINUITY: the dose-2 G1 re-runs reproduced A23's selected schema in 10/10
  replicates. SUPPLY: dose 0 had 37/40 and dose 1 had 39/40, against a threshold of 32. The 4 cells that are
  SUPPLY_LIMITED are all SHAM_2 OTHER spares.
- **Scientific: MEASURED.**

## 3. Results (pooled over G1 + 3 shams; dose 2 = A23's own donors)

| Dose | n | Selected a composition | RECOVERED_MOTIF | RECOVERED_OTHER (the shown o_A) | Motif was a candidate | Summed chance recovery |
|---|---|---|---|---|---|---|
| 0 | 37 | 35 | **4 (0.11)** | **33 (0.89)** | 14 | 10.1 |
| 1 | 39 | 33 | **18 (0.46)** | 12 (0.31) | 39 | 7.0 |
| 2 | 40 | 37 | **35 (0.875)** | 4 (0.10) | 40 | 11.9 |

Per arm, RECOVERED_MOTIF at dose 0 / 1 / 2:

| Arm | Dose 0 | Dose 1 | Dose 2 |
|---|---|---|---|
| G1 | 0/10 | 2/10 | 7/10 |
| SHAM_0 | 2/10 | 6/10 | 9/10 |
| SHAM_1 | 2/10 | 6/10 | 9/10 |
| SHAM_2 | 0/7 | 4/9 | 10/10 |

The dose response has the same shape for G1 and every sham.

Frozen readouts:

| Readout | Value |
|---|---|
| R_RECOVERY_DOSE | 0.11 / 0.46 / 0.875 |
| R_FOLLOWS_SHOWN_STRUCTURE | 0.89 |
| R_ONE_EXAMPLE_SUFFICES | FALSE (0.46 < 0.8 x 0.875 = 0.70) |

## 4. Interpretation (frozen table, spec s5)
1. **Selection reproduces the structure SHOWN in VALIDATE.**
   - With no example of m_A, donors selected the shown o_A in 89% of cases. m_A was recovered in 4/37, which is
     below the summed chance of about 10.
   - m_A passed the exact candidacy screen in only 14/37 dose-0 donors. Without an example, the planted motif
     usually cannot even ENTER selection: the R3 limit at dose 0 is candidacy (R1/R2), not preference.
2. **Multiplicity matters.** Recovery roughly doubles from 1 to 2 examples, and at dose 1 the selector splits
   between the two shown compositions (18 vs 12). It favours the better-supported one.
3. **For A23 (correction-class reading; A23's label unchanged):** A23's "recurrent stepping stone" is, at the
   selection rung, selection of the composition shown twice in validation. It is not abstraction generalising
   beyond its examples. This agrees with the operator's starting position ("the donor frequently recovered the
   planted motif"), now measured with a dose response, and it holds identically for G1 and all three shams.
4. **What this does NOT show.** It does not show that reuse/transfer after selection is spurious: that is a different
   rung (T53 correction: capability is generic and exists only for recovered selections). It also does not show
   that an improver could not generalise. Under THIS improver, whose candidates are compositions screened against
   validation cells, generalising beyond shown structure is structurally hard: unshown structure rarely becomes a
   candidate.

## 5. Ladder position after T01-T03
| Rung | Status in A23 geometry |
|---|---|
| R0-R2 (representable / reachable / findable) | yes, for shown structure; an unshown planted motif is mostly not even a candidate |
| R3 (selectable) | selection = shown-structure recovery, dose-dependent |
| R4-R6 (solved / reused / causal) | generic to inheritance + composition + recurrence; capability only via recovered selections (T53 CORRECTION) |
| R7 (improver changed) | never: the improver is immutable throughout |

## 6. Alternative explanations
- **Spares are easier or harder than motif instances.** Spares are qualified OTHER instances of the same abstraction
  from the same foundry and window, and they are distinctness-screened. If o_A were simply easier to select, that
  would raise RECOVERED_OTHER at dose 0, which is what was observed. This is the shown-structure reading itself, not
  a confound of it.
- **Candidacy, not preference, explains dose 0.** Partly, by design of this improver (the exact screen). Recorded as
  an R1/R2 limit.

## 7. Replay
`python t52_dose.py report`, using the committed plan and donors file. The donor runs are deterministic (continuity
10/10).

## 8. External-review attack questions
1. Would an improver whose candidates are NOT screened against validation cells (e.g. compositions scored on OBSERVE
   only) generalise at dose 0? That would separate candidacy from preference.
2. Is "selection of shown structure" a defect or exactly what a sound selector should do? It argues the
   recursive-improvement question must move up to R7: the improver needs a way to propose structure it was not
   shown.
3. Dose 3 was not run (A23 used 2). Is recovery saturated at 0.875?
