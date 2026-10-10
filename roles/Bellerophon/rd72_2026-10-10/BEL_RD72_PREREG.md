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

## 6. E1 -- long-horizon accumulation inside a composite task (DISCOVERY; registered 2026-10-10T12:53:46Z, before any E1 run)

(s5 is reserved for A3 stage 2.) Status: DISCOVERY. Its tests are registered so that they cannot be chosen after the data, but
nothing in E1 is confirmatory; specimens and hypotheses from E1 go to fresh-seed confirmation blocks (C3).
Plan tools/plan_e1.py (80 runs, distinct seeds 72.1e12+), plan sha256 6f95f48756324402edc48a0f97c5177745abc4de8d3e9822705b9e9bf859c789:
seeded self-copiers, v3 K40, WELL_MIXED, lifespan 80, income 40 (pilot log: 4/4 survival, small n), 2,000 ticks, light
census every 100 ticks. Cells C1_ON (COND_ONE, payment ON, 40), C1_OFF (COND_ONE, OFF, 20), CM_ON (COND_MULTI, ON, 20).
Analysis tools/analyze_e1.py (branch-tested on synthetic rows): per run t_LO / t_HI / t_BOTH (first census with a FUNC
LO-or-BOTH / HI-or-BOTH / BOTH tape), LO retention, and the ordering of any BOTH event (LO_FIRST / HI_FIRST / BOTH_PRIOR /
NONE_PRIOR). Survival and exposure are reported per cell; no run is excluded for extinction.
- E1-a: C1_ON runs with LO > C1_OFF (Fisher one-sided, alpha 0.05).
- E1-b: C1_ON runs with BOTH > C1_OFF (same test). No prediction of the direction is made for CM_ON.
- E1-c (descriptive): the ordering distribution of BOTH events. "Cumulative" requires LO_FIRST or HI_FIRST or BOTH_PRIOR AND,
  on replay under HalvesWorld, critical bytes from >= 2 epochs; a NONE_PRIOR event or a single-epoch composite is "assembled at once".
- Every run with a BOTH event is replayed deterministically under HalvesWorld (end-hash must match) for temporal depth.

## 3-A1. K amendment A1 (registered 2026-10-10T12:56:41Z; BEFORE ANY K RUN -- K was held at 0 runs since 10:26:52Z)

Cause: adversarial review of the K design (BEL_RD72_REVIEW_RECORD.md R1). The desert itself SURVIVED (0 competent tapes in
~3.0e9 two-step neighbours per fixture, 6.0e9 three-substitution, 2.0e9 reduced-alphabet three-step mixed, 8.4M short
programs; minimum distance 4 substitutions from X, 5 from Y; 0/300,000 random tapes competent). Defects found and fixed:
(1) TWO_SOURCE leaked: 5 of the composite's 14 competence-critical positions hold identical bytes in X and Y, so their
founder tags do not say which fixture supplied function; reproduced 9/9 single-source machines labelled two-source.
NOW: TWO_SOURCE_STRICT = >= 1 critical position where the fixtures DIFFER carrying fixture 0's byte with a transplant0
tag AND >= 1 carrying fixture 1's byte with a transplant1 tag. (2) Extinction made outcomes trivially null: INFORMATIVE
run = alive at tick 500; every Fisher test is computed on all runs and on informative runs and passes only if both do;
K-P1 is NOT_TESTABLE when a cell has < 30 informative runs. (3) K-P4 confounded selection with parent survival: the
control is now RANDOM_REWARD (same total bonus, no individual link) in every regime; the K-P4 endpoint is COMP_PERSIST
(a competent FUNC organism alive at tick 1,000), where selection can act; COMP_ANY vs RANDOM_REWARD and vs OFF (OFF kept
under PARTIAL_BYTE only) are reported, not tested. (4) Dose: X_ONLY and Y_ONLY now carry 16 fixture + 16 copier (REP)
transplants. (5) XY_SH / XY_NS: under the real physics single-mutation assembly routes are 0 for both (1 for XY_AL);
the "1 vs >= 2 donor steps" gradient is withdrawn; the cells stay descriptive. (6) Every competent machine is re-checked
on all 256 inputs (reported).
Plan tools/plan_k2.py: 1320 727cea06826695868ae7215994ea6599d73470b2623ba9cc7529d11faebbbdc5 (seed base 71.5e12, distinct).
Analysis tools/analyze_k2.py (synthetic tests incl. the reviewer's mislabel specimen, tools/tests/test_analyze_k2.py).
K-P1..K-P3 wording otherwise unchanged; K-P4 now reads: XY_AL PARTIAL_BYTE COMP_PERSIST ON > RANDOM_REWARD. plan_k.py is
superseded and never run.
