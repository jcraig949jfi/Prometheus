# ER01 Flight 2 record (2026-10-05, 11:05:29Z - 11:29:28Z, 1438.5 s; cap 3600 s)

Miniature real experiment at production semantics: runner er01_run.v2, reducer er01_reduce.v2, regimes R0-R3 as
frozen after Flight 1, P0, paired seeds k = 0, 1, 1024^2, 8000 ticks, late window 2000, bin 50; plus R0 P1 1024^2
k = 0 (continuity) and R0 P0 512^2 k = 0, 1 (finite size). Plan flight2/plan.json, ledger flight2/ledger.jsonl,
reduction flight2/REDUCTION.json.

## Technical disposition: PASS
- 11/11 units rc=0, no cap termination. Output 1.1 MB total (81-92 KB per unit at 8000 ticks).
- VRAM (CuPy pool): 240-248 MiB per 1024^2 unit, 60 MiB per 512^2. Host RSS ~405 MiB per process.
- GPU temperature 44-58 C during flights.
- Throughput: 2 concurrent 1024^2 units, 274-277 s each for 8000 ticks = 34.5 ms/tick per process = 17.3 ms per
  world-tick aggregate.
- Continuity at production size: R0 P1 1024^2 frozen_net64 = 0.9259 (historical 0.926).
- Finite size: R0 P0 512^2 vs 1024^2: late turnover 0.002386 vs 0.002395, frozen_strict 0.9879 vs 0.9879.
- Energy saturation (fraction at 255, final): R0 0.007, R1 0.05, R2 0.13, R3 0.0. No regime is saturated or dead by
  construction.
- Curves produced: frozen/turnover/active/energy series per 50-tick bin; late-window mobility; attack metrics.

The scientific values are in REDUCTION.json and are not interpreted here; the preregistration discloses that they
were seen before the thresholds were frozen.
