# Round 4 P0 world screen -- stage 1 table (G-R4-3), 2026-09-14

Nestor-G[m1-c8188115]. EXP G-R4-3-stage1, predicate bus 1789434570568-0, rows primordial/ledger/rows/G/G-R4-3-stage1.jsonl (last rows commit 482ea8aff), code fc1ebf81c (primordial.metric.suite:job, F7 worker lane G).

## Checks

- Cells: 74 of 74 (w1..w5 + gen_seeds 6..37, both pressures); missing [].
- Rows 444; aborted/timeout rows 0; learner run rows 296 (budget_ok on all: True).
- Learner oracle on run seed 0 of every train8 cell (37 cells): wforge hash+charge failing elites or nb != np: none.
- Reproduction (void condition): w1/w3/w4 abstain, best_constant, random and gate equal the committed G-M1 cells to 4 dp: ALL MATCH.
- Prior (report-only) train8 learner median <= max(abstain, best_constant) in >= 30 of 37 cells: 37 of 37 -> TRUE. w4 train8 learner 88.59 within 15 of E6 open 87.32: TRUE.

## Findings

- floor_kind over all 74 cells: {'abstain': 74}. The input-invariant learner never sets a floor on train8; train128 floors are BOUNDS (learner not run, A 1789433825087-0).
- gate_held64 > four-policy floor in 10 of 74 cells: w7 train8 (+1293.31), w7 train128 (+1293.31), w26 train128 (+96.84), w1 train8 (+82.19), w1 train128 (+82.19), w34 train128 (+63.19), w34 train8 (+16.00), w10 train128 (+11.98), w13 train8 (+7.47), w13 train128 (+7.47).
- Degenerate worlds (abstain = gate = 0 on both pressures): ['w19', 'w24', 'w25'].
- A gate below abstain on HELD64 happens (best-found over non-abstain actions, selected on TRAIN). Under gate_in the floor is max(floor, gate), so it never lowers a floor.

## Table (stage 2 order: gate headroom descending, then gen_seed, then pressure)

| # | world | pressure | abstain | best_constant | random_med | learner (train8) | floor | kind | bound | gate_held64 | gate - floor |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | w7 | train8_held64 | 189.19 | 189.19 | 0.00 | 67.96 | 189.19 | abstain | exact | 1482.50 | +1293.31 |
| 2 | w7 | train128_held64 | 189.19 | 189.19 | 0.00 | - | 189.19 | abstain | bound | 1482.50 | +1293.31 |
| 3 | w26 | train128_held64 | 227.39 | 227.39 | 0.00 | - | 227.39 | abstain | bound | 324.23 | +96.84 |
| 4 | w1 | train8_held64 | 88.28 | 88.28 | 0.00 | 42.69 | 88.28 | abstain | exact | 170.47 | +82.19 |
| 5 | w1 | train128_held64 | 88.28 | 88.28 | 0.00 | - | 88.28 | abstain | bound | 170.47 | +82.19 |
| 6 | w34 | train128_held64 | 273.33 | 273.33 | 0.00 | - | 273.33 | abstain | bound | 336.52 | +63.19 |
| 7 | w34 | train8_held64 | 273.33 | 273.33 | 0.00 | 35.44 | 273.33 | abstain | exact | 289.33 | +16.00 |
| 8 | w10 | train128_held64 | 22.30 | 22.30 | 0.00 | - | 22.30 | abstain | bound | 34.28 | +11.98 |
| 9 | w13 | train8_held64 | 159.00 | 159.00 | 58.44 | 147.97 | 159.00 | abstain | exact | 166.47 | +7.47 |
| 10 | w13 | train128_held64 | 159.00 | 159.00 | 58.44 | - | 159.00 | abstain | bound | 166.47 | +7.47 |
| 11 | w2 | train8_held64 | 251.00 | 251.00 | 2.97 | 195.76 | 251.00 | abstain | exact | 251.00 | +0.00 |
| 12 | w2 | train128_held64 | 251.00 | 251.00 | 2.97 | - | 251.00 | abstain | bound | 251.00 | +0.00 |
| 13 | w3 | train8_held64 | 122.62 | 122.62 | 0.89 | 91.86 | 122.62 | abstain | exact | 122.62 | +0.00 |
| 14 | w3 | train128_held64 | 122.62 | 122.62 | 0.89 | - | 122.62 | abstain | bound | 122.62 | +0.00 |
| 15 | w4 | train8_held64 | 107.75 | 107.75 | 11.49 | 88.59 | 107.75 | abstain | exact | 107.75 | +0.00 |
| 16 | w4 | train128_held64 | 107.75 | 107.75 | 11.49 | - | 107.75 | abstain | bound | 107.75 | +0.00 |
| 17 | w5 | train8_held64 | 73.28 | 73.28 | 32.73 | 69.17 | 73.28 | abstain | exact | 73.28 | +0.00 |
| 18 | w5 | train128_held64 | 73.28 | 73.28 | 32.73 | - | 73.28 | abstain | bound | 73.28 | +0.00 |
| 19 | w9 | train128_held64 | 105.39 | 105.39 | 0.00 | - | 105.39 | abstain | bound | 105.39 | +0.00 |
| 20 | w12 | train8_held64 | 14.53 | 14.53 | 0.00 | 4.25 | 14.53 | abstain | exact | 14.53 | +0.00 |
| 21 | w12 | train128_held64 | 14.53 | 14.53 | 0.00 | - | 14.53 | abstain | bound | 14.53 | +0.00 |
| 22 | w14 | train128_held64 | 191.47 | 191.47 | 107.65 | - | 191.47 | abstain | bound | 191.47 | +0.00 |
| 23 | w16 | train8_held64 | 67.12 | 67.12 | 39.55 | 63.81 | 67.12 | abstain | exact | 67.12 | +0.00 |
| 24 | w16 | train128_held64 | 67.12 | 67.12 | 39.55 | - | 67.12 | abstain | bound | 67.12 | +0.00 |
| 25 | w17 | train128_held64 | 90.38 | 90.38 | 0.70 | - | 90.38 | abstain | bound | 90.38 | +0.00 |
| 26 | w19 | train8_held64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | abstain | exact | 0.00 | +0.00 |
| 27 | w19 | train128_held64 | 0.00 | 0.00 | 0.00 | - | 0.00 | abstain | bound | 0.00 | +0.00 |
| 28 | w21 | train128_held64 | 636.09 | 636.09 | 551.83 | - | 636.09 | abstain | bound | 636.09 | +0.00 |
| 29 | w22 | train128_held64 | 98.62 | 98.62 | 0.00 | - | 98.62 | abstain | bound | 98.62 | +0.00 |
| 30 | w23 | train8_held64 | 353.78 | 353.78 | 153.73 | 303.58 | 353.78 | abstain | exact | 353.78 | +0.00 |
| 31 | w23 | train128_held64 | 353.78 | 353.78 | 153.73 | - | 353.78 | abstain | bound | 353.78 | +0.00 |
| 32 | w24 | train8_held64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | abstain | exact | 0.00 | +0.00 |
| 33 | w24 | train128_held64 | 0.00 | 0.00 | 0.00 | - | 0.00 | abstain | bound | 0.00 | +0.00 |
| 34 | w25 | train8_held64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | abstain | exact | 0.00 | +0.00 |
| 35 | w25 | train128_held64 | 0.00 | 0.00 | 0.00 | - | 0.00 | abstain | bound | 0.00 | +0.00 |
| 36 | w30 | train8_held64 | 660.19 | 660.19 | 323.62 | 633.38 | 660.19 | abstain | exact | 660.19 | +0.00 |
| 37 | w30 | train128_held64 | 660.19 | 660.19 | 323.62 | - | 660.19 | abstain | bound | 660.19 | +0.00 |
| 38 | w31 | train8_held64 | 25.50 | 25.50 | 0.00 | 12.23 | 25.50 | abstain | exact | 25.50 | +0.00 |
| 39 | w31 | train128_held64 | 25.50 | 25.50 | 0.00 | - | 25.50 | abstain | bound | 25.50 | +0.00 |
| 40 | w21 | train8_held64 | 636.09 | 636.09 | 551.83 | 628.24 | 636.09 | abstain | exact | 636.02 | -0.08 |
| 41 | w29 | train128_held64 | 62.38 | 62.38 | 1.37 | - | 62.38 | abstain | bound | 62.23 | -0.14 |
| 42 | w20 | train128_held64 | 34.00 | 34.00 | 1.00 | - | 34.00 | abstain | bound | 33.75 | -0.25 |
| 43 | w27 | train128_held64 | 28.28 | 28.28 | 8.52 | - | 28.28 | abstain | bound | 28.02 | -0.27 |
| 44 | w20 | train8_held64 | 34.00 | 34.00 | 1.00 | 24.01 | 34.00 | abstain | exact | 33.67 | -0.33 |
| 45 | w36 | train8_held64 | 36.50 | 36.50 | 6.33 | 29.06 | 36.50 | abstain | exact | 35.64 | -0.86 |
| 46 | w36 | train128_held64 | 36.50 | 36.50 | 6.33 | - | 36.50 | abstain | bound | 35.64 | -0.86 |
| 47 | w15 | train8_held64 | 222.50 | 222.50 | 5.33 | 148.09 | 222.50 | abstain | exact | 221.38 | -1.12 |
| 48 | w35 | train8_held64 | 129.88 | 129.88 | 0.00 | 29.64 | 129.88 | abstain | exact | 128.53 | -1.34 |
| 49 | w14 | train8_held64 | 191.47 | 191.47 | 107.65 | 161.14 | 191.47 | abstain | exact | 189.91 | -1.56 |
| 50 | w35 | train128_held64 | 129.88 | 129.88 | 0.00 | - | 129.88 | abstain | bound | 127.52 | -2.36 |
| 51 | w22 | train8_held64 | 98.62 | 98.62 | 0.00 | 89.49 | 98.62 | abstain | exact | 96.12 | -2.50 |
| 52 | w32 | train128_held64 | 30.50 | 30.50 | 0.00 | - | 30.50 | abstain | bound | 27.23 | -3.27 |
| 53 | w32 | train8_held64 | 30.50 | 30.50 | 0.00 | 18.66 | 30.50 | abstain | exact | 25.91 | -4.59 |
| 54 | w15 | train128_held64 | 222.50 | 222.50 | 5.33 | - | 222.50 | abstain | bound | 216.34 | -6.16 |
| 55 | w8 | train8_held64 | 70.44 | 70.44 | 1.12 | 59.46 | 70.44 | abstain | exact | 62.44 | -8.00 |
| 56 | w8 | train128_held64 | 70.44 | 70.44 | 1.12 | - | 70.44 | abstain | bound | 62.44 | -8.00 |
| 57 | w33 | train128_held64 | 148.69 | 148.69 | 0.00 | - | 148.69 | abstain | bound | 140.44 | -8.25 |
| 58 | w6 | train8_held64 | 229.53 | 229.53 | 0.00 | 190.16 | 229.53 | abstain | exact | 219.64 | -9.89 |
| 59 | w6 | train128_held64 | 229.53 | 229.53 | 0.00 | - | 229.53 | abstain | bound | 219.64 | -9.89 |
| 60 | w37 | train8_held64 | 294.00 | 294.00 | 133.30 | 257.84 | 294.00 | abstain | exact | 280.16 | -13.84 |
| 61 | w37 | train128_held64 | 294.00 | 294.00 | 133.30 | - | 294.00 | abstain | bound | 280.16 | -13.84 |
| 62 | w27 | train8_held64 | 28.28 | 28.28 | 8.52 | 21.72 | 28.28 | abstain | exact | 13.94 | -14.34 |
| 63 | w28 | train8_held64 | 170.88 | 170.88 | 4.75 | 154.53 | 170.88 | abstain | exact | 154.88 | -16.00 |
| 64 | w28 | train128_held64 | 170.88 | 170.88 | 4.75 | - | 170.88 | abstain | bound | 154.88 | -16.00 |
| 65 | w17 | train8_held64 | 90.38 | 90.38 | 0.70 | 75.96 | 90.38 | abstain | exact | 72.38 | -18.00 |
| 66 | w11 | train128_held64 | 78.75 | 78.75 | 0.40 | - | 78.75 | abstain | bound | 56.58 | -22.17 |
| 67 | w10 | train8_held64 | 22.30 | 22.30 | 0.00 | 16.64 | 22.30 | abstain | exact | 0.00 | -22.30 |
| 68 | w29 | train8_held64 | 62.38 | 62.38 | 1.37 | 49.90 | 62.38 | abstain | exact | 38.52 | -23.86 |
| 69 | w18 | train8_held64 | 33.62 | 33.62 | 0.00 | 3.35 | 33.62 | abstain | exact | 0.00 | -33.62 |
| 70 | w18 | train128_held64 | 33.62 | 33.62 | 0.00 | - | 33.62 | abstain | bound | 0.00 | -33.62 |
| 71 | w9 | train8_held64 | 105.39 | 105.39 | 0.00 | 40.87 | 105.39 | abstain | exact | 66.22 | -39.17 |
| 72 | w11 | train8_held64 | 78.75 | 78.75 | 0.40 | 45.30 | 78.75 | abstain | exact | 32.58 | -46.17 |
| 73 | w33 | train8_held64 | 148.69 | 148.69 | 0.00 | 74.36 | 148.69 | abstain | exact | 99.55 | -49.14 |
| 74 | w26 | train8_held64 | 227.39 | 104.92 | 0.00 | 141.65 | 227.39 | abstain | exact | 146.27 | -81.12 |
