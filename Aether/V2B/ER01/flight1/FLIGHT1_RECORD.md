# ER01 Flight 1 record (2026-10-05, 10:38:10Z - 10:47:27Z, 557 s; cap 3600 s)

Purpose (order s11): does the regime panel execute correctly and span distinct physical behaviour?
Not interpreted scientifically beyond pathology screening.

Runner er01_run.v1 at commit 1eaa5c6f0 (regime_table_hash recorded per unit). Driver er01_flight.py, 4 concurrent
processes on the RTX 5060 Ti. Plan: flight1/plan.json. Ledger: flight1/ledger.jsonl. Reduction: flight1/REDUCTION.json
(er01_reduce.v1).

## Technical disposition: PASS
- 10/10 units rc=0; no wall-cap termination; results 326 KB total.
- Exact replay / continuity: cont_R0P1_hist (R0, P1, historical seeds 0xA37E01/0x5C011701, 256^2, 2564 ticks)
  gives frozen_net64 = 0.9259185791015625, bit-identical to the CPU `aeth02_falsifiers.py h1b` rerun.
- Conformance for every regime on a reduced fixture: phaseA/conformance_n64_t300.json (all equal).
- Regime identity recorded in every unit (regime, label, energy tuple, table hash).
- Reducer runs.
- VRAM: CuPy pool 60-62 MiB per 512^2 unit; host RSS ~405 MiB per process.
- Throughput: 4 concurrent 512^2 units ~45 ms/tick each (~11 ms per world-tick).

## Pathology screen (P0, n=512, 5000 ticks, 2 paired seeds)
| regime | final energy mean | zero-energy frac | late active density | late starved density | verdict |
|---|---|---|---|---|---|
| R0 B_balanced | 80.3 | 0.247 | 0.202 | 0.240 | reference |
| R1 C_free_compute | 122.7 | 0.101 | 0.442 | 0.000 | valid (historical semantics); activity = all WRITE sites by construction |
| R2 rich_rain_x2 | 189.3 | 0.068 | 0.374 | 0.068 | not dead; saturation fraction not measured in v1 (added in v2, read in Flight 2) |
| R3 scarce_rain_half | 6.3 | 0.599 | 0.101 | 0.341 | not inert (active writers persist) |

Energy distributions differ strongly between regimes, as designed. No regime is dead or mechanically saturated by
construction on this screen, so no replacement is needed. **Regime definitions R0-R3 are frozen for Flight 2 unchanged.**

## Repair cycle (order s12)
One change, made between flights, no physics touched:
- er01_run.v2: per-tick counts kept on device and synced once per bin (v1 synced ~10 times per tick); adds
  `energy_255_frac` (saturation screen requested by s11). Final digest of a 512^2 x 300 R0 P0 unit is unchanged
  (9999cf9dba441a59d563bbae23272974). Conformance re-run on v2: phaseA/conformance_v2_*.json.
- Measured after the change: single process 15 ms/tick at 512^2 and 16.4 ms/tick at 1024^2 (launch-bound);
  8 concurrent 1024^2 processes 150 ms/tick each (~19 ms per world-tick): the GPU is compute-saturated at 1024^2.
