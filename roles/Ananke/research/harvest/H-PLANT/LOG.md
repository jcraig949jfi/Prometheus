# H-PLANT LOG

Independence note: before PLAN.md I read only the frozen parent plan, COMMON_RULES(_ARC3).md,
engine/env/physics/topology/plants/campaign/assays/c1b code, FREEZE_PTE_C1.json, C1b
FIXTURES_dev.json, and raw C1 rows. A filename grep for "d9cc" listed
harvest/H-SCI/REPORT.md and harvest/INFERENCE_HARVEST_HANDOFF.md (NOT opened) and a W-I raw
output JSON, of which I read 150 characters (cell id + phys_digest d9ccb6a71d986501) to learn
that "d9cc" is a physics digest. No principal synthesis read. No context contamination.

Compute: process CPU seconds (time.process_time, all threads) per run; cap 7200 s.

| # | run | threads | cpu_s | wall_s | cumulative cpu_s |
|---|-----|---------|-------|--------|------------------|
| 1 | gate.py (G1a, G1b, G2) | 8 | 87.3 | 11.3 | 87 |
| 2 | run_xor.py dev (X0, 32 DEV worlds) | 4 | 12.8 | 3.2 | 100 |
| 3 | run_xor.py score (X0, 256 HPLT) | 4 | 15.7 | 4.0 | 116 |
| 4 | run_xor.py mf (X0, 256 HPLT) | 4 | 34.3 | 8.8 | 150 |
| 5 | lightcone.py (4 d9cc cells) | 2 | 2.0 | ~2 | 152 |
| 6 | run_xor.py screen (18 C1 XOR rows, 32 DEV) | 4 | 98.8 | 26.5 | 251 |
| 7 | run_xor.py score_cell 4eeca9f10c514f08 | 4 | 22.3 | 5.9 | 273 |
| 8 | run_xor.py score_cell_literal aa2b8d6805a15ec6 | 4 | 184.9 | 47.0 | 458 |
| 9 | run_flip_mh.py flip dev | 4 | 104.5 | 26.5 | 563 |
| 10 | run_flip_mh.py flip score | 2 | 244.0 | 123.4 | 807 |
| 11 | run_flip_mh.py mh score | 2 | 228.9 | 115.3 | 1036 |
| 12 | lc_census.py (871 evolve rows, analytic) | 2 | 125.6 | 126.2 | 1161 |
| - | row-inspection one-liners (no engine), est. | 1 | ~60 | - | ~1221 |

TOTAL ~1221 CPU s = ~0.34 core-hours of the 2.0 cap. No GPU: CUDA_VISIBLE_DEVICES=-1 in every
engine process, hp_common asserts torch.cuda.is_available() is False, World(device="cpu").

## Attempt 1 -- gate (2026-09-30)
G1a relay_flood C1 row 29b7e63a5fa4a78b: recorded .9609375, reproduced .9609375 (exact).
G1b relay_flood C1b F_DA normal: 1.0 / 1.0. G2 echo_hold C1b F_echo normal: 1.0 / 1.0.
GATE PASS. out/gate.json.

## Attempt 2 -- P-XOR at chosen physics X0 (torus64 r3 all lossless, XOR d3 delta8)
DEV 32: 1.0. SCORE 256 HPLT: 1.000 [1.000, 1.000]. MF-XOR-a (s2 cue zeroed): .500 [.500,.500]
(readout constant +: one flag only). MF-XOR-b (Q zeroed in readout = "+ iff P"): .237
[.221, .252] -- far from .5 as predicted (one-flag readouts correlate with XOR at |.25| under
the env mirror). out/xor_dev.json, xor_score.json, xor_mf.json.

## Attempt 3 -- XOR at d9cc: analytic light-cone bound
d64656f26736d37c and 1b26026fc846d03d (XOR d3 delta16 at d9cc): both sensors' cue can reach the
actuator by readout in only 14.84% of scored trials (fastest transport, no loss/cap) -> any
program's accuracy <= .574 < .60. FLIP 6f82f9c7 and RELAY d5 fac4aaa2 at d9cc: 100% in reach.
out/lightcone_d64656f2_1b26026f_6f82f9c7_fac4aaa2.json. Plant not run at d9cc (needs period 1).

## Attempt 4 -- XOR screen (18 clock-compatible C1 XOR rows, at_specimen struct, 32 DEV)
Top: 4eeca9f10c514f08 .841, 83e9fea69d2e2958 .781, aa2b8d6805a15ec6 .719, two torus rows .57,
rest <= .531. out/xor_screen.json.
Scored top-1 4eeca9f10c514f08 (A0, random64 k6 all, loss .3, lat 1, dup .1; env d3 delta4) with
genome-space override (prog_len 8->16, state_dim 1->4, payload 4->2, channels 2->1, rules 4->1,
setrule/wimm 1->0, adapt_shift 2->4): .805 [.784, .826]; MF-a .4997 [.498,.501]; MF-b .340.
Noticed the override is large -> ADDENDUM A6 written, then:
Scored aa2b8d6805a15ec6 LITERAL C1 dial vector (A0; random144 k6, sample fanout 8, loss .3,
lat 4, dup .1, cap 4/none, economy low, rules 2, setrule 1, wimm 1, plastic_route 1, state_dim
4, payload 4, prog_len 16; env XOR d2 delta16): .663 [.636, .687]; MF-a .500 [.500,.500];
MF-b .412 [.394,.432]. out/xor_score_cell_4eeca9f10c514f08.json,
xor_score_cell_literal_aa2b8d6805a15ec6.json.

## Attempt 5 -- P-FLIP at d9cc (literal C1 physics of cell 6f82f9c7d51bcef1) and lossless
DEV 32: d9cc .979, lossless 1.0. SCORE 256: d9cc .978 [.962, .990]; lossless .997 [.990,
1.000]. MF-FLIP-a (teacher zeroed): .500 [.500,.500] both. MF-FLIP-b (readout ignores m): .499
[.489,.509] / .497 [.491,.500]. out/flip_dev.json, flip_score.json.

## Attempt 6 -- P-MULTIHOP = relay_flood at d9cc (literal, cell fac4aaa23a0bdcb2 env) / lossless
SCORE 256: d9cc d5 .984 [.969, .995]; d9cc d6 .978 [.962, .991]; lossless d5 .999 [.996,1.0];
lossless d6 .999 [.996, 1.0]. MF-MH (relay disabled): .500 [.500,.500] in all four.
out/mh_score.json.

## Attempt 7 -- light-cone census (ADDENDUM A7), C1 evolve rows
XOR 218 rows: 37 (17.0%) have bound < .60. FLIP 247: 24 (9.7%). RELAY 406: 22 (5.4%). Consistency
check: none of the 55 RELAY rows with held lo99 > .55 has bound < .60 (the bound is never
violated). out/lc_census.json.
