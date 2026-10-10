# PREREG WTP-05 sub-assay E2 -- WTP-04 two-axis revival (C-014-E2)

Seat: Ensorain[ubu006-4b001784]. Date: 2026-10-10.
Authority: the operator directive of 2026-10-10, s25 (roles/Ensorain/prompts/2026-10-10_wtp05_directive/).
This file and ensorain/wtp5/revival.py are committed before any E2 row.

## Question
Can a coupled two-axis physical change revive the WTP-04 dead families F01, F06 and F11? WTP-04 is not
reinterpreted. Its F11 band=.5 CHEAP_PAYS cell is a recorded single-axis pay and stays one.

## Method
- The frozen WTP-04 harness is reused unchanged:
  - ensorain/wtp4/families.py representatives;
  - axes transforms;
  - habit.unit (immortal-twin earning rates; cheap carriers before structured);
  - habit.classify and score4.cell_label (both seeds must pay).
- Grid: memory band {native, .1, .25, .5, 1.0} crossed with each second axis:
  - change {static, drift .3/p800, drift .3/p200};
  - price {x.01, x.1, x1}, applied to the read/write/probe/rollout prices;
  - noise sd {0, .1, native}.
- 45 points per family. 3 families x 45 points x 2 seeds = 270 units.
- Seeds: 41005001 and 41005002, never used before.
- Envelope: 3 workers, nice 10.
- Expected runtime ~2.2 h. That is the WTP-04 measured rate of 28.7 s wall per unit at 3 workers.
  (Correction to RESULTS_WTP04_MAP.md s5: "~29 s per unit-core" should read "~29 s wall per unit at 3
  workers, ~86 core-s per unit". The WTP-04 file is left as recorded.)

## Labels and verdict per family (revival.score)
- COUPLED_REVIVAL: some cell (m, x) PAYS while neither (m, native second axis) nor (native band, x) pays.
- SINGLE_AXIS_REVIVAL: only cells on a native row or column pay.
- NOT_REVIVED: no cell pays.

## Predictions
- R1 F01 and F06: NOT_REVIVED. WTP-04 found them DEAD at every single-axis level, including band .5 and
  noise 0.
- R2 F11: SINGLE_AXIS_REVIVAL via memory (band .5 and/or 1.0), as WTP-04's band=.5 cell suggests.
- R3 No family shows COUPLED_REVIVAL (p = .7).
- R4 If any coupled revival appears, it is memory x price. Cheaper information plus more memory is the only
  pair whose single axes both moved the paying count in WTP-04's living families.

## Use
A revived world (a COUPLED or SINGLE-axis pay replicated in both seeds) is recorded as an extra WTP-05 test
environment. Only its WTP-04-style label is claimed here. A null is preserved as a null.
