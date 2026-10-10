# BEL-RD-72 REACHABILITY GEOMETRY (Workstream A, instrument + static geometry)

STATUS: living document; sections marked PENDING are filled when their block completes.

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

## 4. Operator-aware prediction (A3) -- PENDING (stage-1 scan running; stage 2 frozen, prereg s5)
## 5. Operator substitution (A2) -- PENDING (K2 operator regimes: COPY_BYTE vs COPY_STRUCT vs PARTIAL_BYTE)
