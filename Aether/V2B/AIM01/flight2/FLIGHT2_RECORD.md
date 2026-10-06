# AIM01 Flight 2 record (2026-10-06, 00:40:35Z - 01:14:36Z, 2041 s; cap 3600 s)

Full 2 x 3 factorial at 512^2 x 12,000 ticks, seeds 0-1, bin 25, late window 2000; plus L0/L1 D50 at 1024^2 x 3000
(throughput and finite size). Production runner, reducer and schema. Reduction: flight2/REDUCTION.json.

## Technical disposition: PASS
- 14/14 rc = 0.
- Gates: subset_violations 0 everywhere; L0 RAW == EFFECT; one table hash. The duplicate gate is n/a: there was no
  duplicate in the flight.
- Runtime, 4 concurrent at 512^2: L0 50.5-52.0 ms/tick and L1 54.8-59.0 ms/tick per process, i.e. <= 14.7 ms per
  world-tick.
  - 1024^2 single-ish: 24-32 ms/tick.
  - VRAM: 417-421 MiB per 512^2 unit, ~1.4 GiB per 1024^2 unit.
  - Host RSS ~468 MiB per process.
  - Output: ~290 KB per 12k-tick unit at bin 25.
- Support saturation: ever_changed and ever_targeted reach 99% of their final value within the first 25-tick bin in
  all 6 cells. Persistence 0.999-1.005: nothing is still evolving late.
- Finite size, D50 512^2 vs 1024^2:
  - L1: ever_changed 0.8203 vs 0.8199; frozen_strict 0.8262 vs 0.8264; late EFFECT turnover 0.025662 vs 0.025691.
  - L0: 0.3727 vs 0.3732.
- L0 D50 vs ER01 R0 P0: late turnover 0.002391 vs 0.002393; frozen_strict 0.9879 vs 0.9880.
Scientific values are in REDUCTION.json and are not interpreted here.
