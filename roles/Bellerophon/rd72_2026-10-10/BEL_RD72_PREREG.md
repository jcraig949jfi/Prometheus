# BEL-RD-72 PREREGISTRATION -- Bellerophon, campaign BEL-RD-72 (Reachability deserts, composition, accumulation)

Directive: roles/Bellerophon/prompts/2026-10-10_rd72/ (verbatim + MANIFEST). Clock 2026-10-10T09:50:44Z ->
2026-10-13T09:50Z. Host ubu005 (8 cores; prometheus-worker service inactive). Branch bellerophon/rd72-2026-10-10 from
main d0eba60f5. Prior evidence: BEL-48H (roles/Bellerophon/bel48h_2026-10-08/). Append-only; amendments dated;
timestamps from the shell clock only.

## 1. Standing rules (carried from the BEL-48H calibration ledger)

- Unit of independence = distinct initial population (distinct seed). Seeds are distinct per run unless a pairing is
  the stated design; pooled claims are reported per seed.
- Every analysis script is committed before its data AND exercised on synthetic rows that drive every predicate to both
  branches (BEL-48H W4-P5 rule).
- A mechanism read from a trace gets an automated falsifiable test before it is written into a report.
- Before freezing a mechanism test, check that the mechanism can operate in the window the endpoint measures (U3 rule).
- Completion markers are matched anchored; processes are selected by exact command line.
- Classes: CAUSALLY_CONFIRMED / REPRODUCED / PROVISIONAL / DETECTOR_ONLY / CONFOUNDED / FALSIFIED / INSTRUMENT_FAILURE.
- Origin (Q1) / Composition (Q2) / Accumulation (Q3) evidence is reported separately; a Q1 result is never cited as Q2/Q3.

## 2. D1 -- functional loss/gain ratio as a frozen prediction of the uptake effect (frozen 2026-10-10T09:53:56Z, before any run)

Plan tools/plan_d1.py: 1,900 runs, sha256 d632cb30180724f6dc0ef8d886c411e41e1906016d3b489940ec3d339cdfdf70. Substrates
NOT used in BEL-48H: S_LOCAL (PARTIAL, GRID LOCAL, budget 256) and S_PAIR320 (PAIR_EXECUTION, GRID WELL_MIXED, budget
320). Per substrate: 150 UF worlds (R = FUNC_LOSS / FUNC_GAIN over uptake events) and 400 seed-pairs normal vs uptake-
blocked (first-origin endpoint, as BEL-48H U). Analysis tools/analyze_d1.py (committed; branch-exercised on synthetic
rows -- which caught and fixed a NO_PREDICTION handling bug before this freeze).
Rule: R >= 1.25 predicts INCREASE (blocked > normal, one-sided sign test p < 0.05); R <= 0.8 predicts NO_INCREASE;
otherwise NO_PREDICTION.
- D1-P1: in every testable substrate the predicted and observed outcomes match.

## 3. K -- composition of two COMPUTATIONAL blocks across a reachability desert (frozen 2026-10-10T10:20:30Z, before any run)

Target: COND_MULTI (x < 128 ? x : (x XOR 0x55) + 3) by a FUNC replicator. Prior: LADDER2 (multi-day, 20,000 ticks,
ENDOGENOUS_COPY + BYTE mutation) INC copiers -> COND_ONE 0/240. Fixtures tools/fixtures_k.py: X (copier + transform
block; correct only on x >= 128), Y (copier + branch block, echoes; correct only on x < 128). ENUMERATED before freezing:
X, Y each FUNC; NEITHER has any single-step route (SUB 0/16,320, self MOVE 0/50,512, INS 0/16,384) to FUNC + COND_MULTI-
competent; one X segment into Y_SH gives 12 routes; Y_NS 0 single cross routes; ALIGNED: Y[0:12] + X[12:] is the
composite (a prefix transfer; a Y whose copy length mutates to 12 writes it but keeps the truncated copier).
Plan tools/plan_k.py: 1260 e05f720ee6d1dd3251e8e2f8b2c52b6a8e30a5c0c274c4f81dc11306d7ee9833; 6 fixture sets x 3 operator regimes x ON, plus XY_AL x OFF per regime; 60 distinct seeds per cell;
physics v3 COMMON + K40, task COND_MULTI, 1,000 ticks, PAIRED init. Analysis tools/analyze_k.py (committed; branch-
exercised on synthetic rows in both directions). Exposure (organism-ticks) recorded per run as the search budget.
Pilot disclosure (4 + 8 runs, seeds 78e6+, excluded): XY_AL 1,000 ticks extinct in 3/3 (one per regime, 25-70 s); at
300 ticks 7/8 alive across LOCAL/WELL_MIXED x K40/K100; no competent organism in any pilot run. Setting kept at the
historical K40 LOCAL; seeds doubled to 60 because of extinction risk.
Endpoints: COMP_ANY = a competent child born to a non-competent writer (any FUNC state: catches prefix-replicator
composites); COMP_SR = a competent FUNC child born. TWO_SOURCE = the competent machine's competence-critical bytes include
founder bytes of both X (transplant0) and Y (transplant1).
- K-P1 (the desert under the historical operators): XY_AL COMP_SR <= 2/60 under COPY_BYTE and under COPY_STRUCT.
- K-P2 (operator-relative crossing): XY_AL COMP_ANY under PARTIAL_BYTE exceeds X_ONLY, Y_ONLY (PARTIAL_BYTE) and XY_AL
  COPY_BYTE (Fisher one-sided p < 0.05 each).
- K-P3 (two-source composition): >= 80% of XY_AL PARTIAL_BYTE runs with COMP_SR are TWO_SOURCE.
- K-P4 (selection): XY_AL PARTIAL_BYTE COMP_ANY ON > OFF (Fisher one-sided p < 0.05).
XY_SH / XY_NS cells are descriptive (operator-distance gradient: 1 donor step vs >= 2).

## 4. A3 stage 1 -- harvest + operator scans (registered 2026-10-10T10:21:40Z; MEASUREMENT ONLY, no outcome observed)

Stage 1a tools/plan_a3.py harvest: 180 fresh worlds (60 x PARTIAL / PAIR / COPY, WELL_MIXED, 500-tick config run to tick
100, distinct seeds 72e12+), <= 20 non-FUNC living tapes each; plan sha256
ba867114a061d7984a25faa709ebcb1308d30d934835e257ca26daf460648a1c. Stage 1b scan: a seeded sample (rng 7203) of <= 200 tapes
per physics; one-step routes to FUNC under SUB / MOVE / INS / DEL (geometry.scan_operators, kernel c83a56063). Stage 2
(the outcome test and the prediction) is frozen in s5 after stage 1 completes and BEFORE any replanting run.
