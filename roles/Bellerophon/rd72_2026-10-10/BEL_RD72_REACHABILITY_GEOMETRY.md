# BEL-RD-72 REACHABILITY GEOMETRY (Workstream A, instrument + static geometry)

STATUS: complete except F1 dynamics (CUMULATIVE_ORGANIZATION s5 / COMPOSITION s4).

## 1. Instrument (kernel commit c83a56063, merged with the campaign; 113/113 kernel tests + 4 new)
prometheus/z80atlas/geometry.py gained pure, opt-in functions (no historical output changes):
- operator_neighbours(tape, op, L, donors, max_seg=16): every one-step neighbour under
  SUB (point substitution, L x 255), MOVE (self segment copy/overwrite, n <= 16, d != s), INS (insert + right shift, last
  byte drops), DEL (delete + left shift, 0 pad), DONOR (segment copy from another tape over self: uptake / partial overwrite
  / multi-source assembly when several donors are given).
- scan_operators(tape, L, predicate, ops, donors): routes per operator = neighbours satisfying the caller's predicate.
- scan_moves (historical-compatible MOVE only); sample_paths(...): random multi-step operator paths (depth k) for
  minimum-construction-path estimates. Neighbourhood sizes for L = 64: SUB 16,320; MOVE 50,512; INS 16,384; DEL 64.
GEOMETRIC reachability (this file) is a property of the tape and operator set. DYNAMICAL accessibility (whether a population
actually takes the route) is measured separately by replanting and by worlds (A3 stage 2, N1 in BEL-48H, E1b, K2).

## 2. Operator deserts in the task family (A1; receipts/B2_trivaudit.json)
One-step routes to a competent FUNC tape: from the bare copier, 0 to every task under every operator. Composite tasks
(COND_ONE, COND_MULTI) and SUM2: 0 routes from every other rung's copier+task hybrid under SUB, MOVE, INS and DEL -- a
desert under ALL single operators. Downward moves are dense (COND_ONE -> ECHO 231 SUB / 260 MOVE; -> INC 468 / 701 /
2,142 INS). Upward: ECHO -> INC 1 route (INS only); CONST -> ECHO 1 (INS only): operator-specific needles -- substitution
alone sees no route where insertion has one.
Historical prior (multi-day LADDER2): INC copiers -> COND_ONE 0/240 worlds at 20,000 ticks under COPY + BYTE mutation.

## 3. Desert depth for COND_MULTI (adversarial review R1)
From X (copier + transform) and Y (copier + branch): 0 competent tapes in all one-step (SUB 16,320 / MOVE 50,512 / INS
16,384 / DEL 64) and two-step neighbourhoods (~3.0e9 per fixture), three-substitution (6.0e9), reduced-alphabet three-step
mixed (2.0e9); minimum distance 4 substitutions (X), 5 (Y). The composite Y[0:12] + X[12:] is ONE prefix transfer away under
a DONOR (two-source) operator: the desert exists for every single-source operator and vanishes for a two-source one.
That is the K2 test: does a population cross it through partial overwrite (operator-relative crossing), and does the
crossing need BOTH sources (strict two-source attribution)?

## 4. Operator-aware prediction (A3; prereg s4, s5, s5-E1; RESULTS_LOG A3; receipt receipts/A3_stage2_analysis.json)
Harvest: 600 non-FUNC tapes from 180 fresh worlds (3 physics), scanned under SUB / MOVE / INS / DEL.
- 584/600 (97%) have NO one-step route to FUNC under any operator.
- 9 have a SUB route, 7 INS / DEL only, and 0 a MOVE-only route.
Frozen prediction in 1,194 unseen replant worlds: the operator-aware score did NOT beat substitution or byte content
(AUC 0.592 / 0.586 / 0.606; A3-P1, P2 and P3 all fail).
Descriptive: one-step SUB-route tapes completed 8/9 and no-route tapes 37/581, which is background level.
Geometry is sharply predictive where it says "one step", and silent elsewhere.

## 5. Operator substitution (A2; K2, prereg s3 / 3-A1; RESULTS_LOG K2; receipt receipts/K2_analysis.json)
The same verified COND_MULTI desert under three copy operators (COPY_BYTE, COPY_STRUCT, PARTIAL_BYTE): 0 competent
replicators in 1,320 worlds. The partial-overwrite operator (the one with a two-source route) produced the only competent
product: 4 non-replicating machines in 1 world. Swapping the operator did not make the desert crossable at 1,000 ticks.

## 6. The COND_ONE composition desert from EVOLVED material (DP; RESULTS_LOG DP; receipt receipts/DESERT_probe.json)
13 E1b worlds where ECHO and INC replicators coexisted, scanned one step from each tape plus a donor splice from the
partner: 0 routes in ~3.9M neighbours, and 0 of 52,000 sampled 3-step paths. A positive control (knockouts of the witness)
finds the routes.

## 7. F1 baseline accessibility (prereg s10 item 3; receipt receipts/F1_baseline_geometry.json)
One-step routes to a FUNC COND_ONE replicator:
| founder | routes |
|---|---|
| 9 single-knockout founders (KO1) | SUB 1-103 each; MOVE 8 and 4 in two of them; INS 1-2 in three |
| 23 double-knockout founders (KO2) | 0 under every operator |
| ECHO hybrid | 0 |
| bare copier | 0 |
Dynamical accessibility from these founders is F1's outcome.
