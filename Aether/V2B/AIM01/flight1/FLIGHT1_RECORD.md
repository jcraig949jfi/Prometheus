# AIM01 Flight 1 record (2026-10-06, 00:33-00:40Z; units 372 s; cap 3600 s)

Purpose (order s19): qualify semantics and metrics. No scientific reading.

## Qualification (flight1/conformance_n64_t300.json, all_ok = true)
1. reaim1 = smallest law delta: a wrapper on the frozen aeth01.v1 kernel. Winners are read from the kernel's own
   observer channel, and arg0 += 1 (mod 256, so direction += 1 mod 4) is applied to every winning source whose own
   arg0 was not written that tick. The kernel file is unmodified.
2. L0 == ER01: aim01 L0 D50 (with the observer running) vs the ER01 runner R0 P0 (no observer), seeds 0 and 1,
   64^2 x 300 ticks: identical digests at 30 checkpoints plus final; identical late turnover, frozen_strict,
   frozen_net64 and ever_changed. The instrumentation does not change the dynamics.
3. CPU == GPU for L0 and L1 at D25/D50/D75, 2 seeds: 12/12 identical (digests, series, summary).
4. RAW vs EFFECT:
   - L0: RAW == EFFECT exactly in every unit and bin, and the re-aim rate is 0.
   - L1: subset_violations = 0 (no EFFECT change without an executed write onto that site-field). RAW late turnover
     exceeds EFFECT in every unit.
5. Known answers (Aether/test/test_aim01_meter.py, 5/5 pass): STATIC, FIXED_FLICKER (novelty 0, period 2, 2 unique
   states), EXPANDING_SUPPORT (monotone ever_changed, novelty 1, support growth > 0), AIM_BOOKKEEPING_ONLY (RAW
   moves, EFFECT exactly 0), and bookkeeping + a real arg0 write (only the write counts).
6. D25/D50/D75 run at 256^2 x 3000 ticks, 2 seeds, both laws: 12/12 rc = 0.
7. Paired initialization, per seed:
   - non-opcode fields are byte-identical across densities;
   - opcode differs only at sites that are WRITE in the denser world;
   - WRITE sets are nested;
   - realized densities are 0.246-0.258 / 0.505 / 0.750-0.756.
8. reaim changes targeting at all: ever_targeted_site L1 > L0 at every density and seed (C5).

## Technical notes
- 256^2: ~39-41 ms/tick per process at 4 concurrent (launch-bound; the observer path adds kernels). CuPy pool
  176 MiB; 35-37 KB per 3000-tick unit at bin 50.
- 1024^2 single process: ~23 ms/tick (300-tick probe).
- Repair: none needed. Change for Flight 2: bin 50 -> 25, because support saturation already shows in the first
  50-tick bin and needs finer resolution early.
