# THESEUS-51 verdict: concept-tensor content vs coupling supply (prereg roles/Theseus/prereg/2026-10-10_tensor_vs_supply/, 3674dce8a)

Runs (PYTHONHASHSEED=0, flags as 40, --random-law-gains, --workers 2 each). The law gains
are drawn from an independent RNG instead of the concept tensor; everything else is identical.

| run | master seed |
|---|---|
| RANDLAW s3 v0_2t0rg_s3_2026-10-10 | 20261010 |
| RANDLAW s4 v0_2t0rg_s4_2026-10-10 | 20261011 |

Comparators (existing): LAW v0_2t0_s3/s4, NOLAW v0_2t0nl_s3/s4.
Evals: comp_task_s{3,4}_rg_2026-10-10 (RANDLAW vs NOLAW, gate inside). The LAW and NOLAW
J/KO rows were copied from the s3/s4 law evals (deterministic). Pooled: POOLED_TENSOR.json,
POOLED_SUPPLY.json.

GATE (both seeds): 1-part controls .195-.2025; 2-part controls 1.0. PASSES.

## Primaries (D solver share, 100 per run)

| seed | LAW | RANDLAW | NOLAW |
|---|---|---|---|
| 20261010 | 75 | 75 | 62 |
| 20261011 | 71 | 72 | 64 |

| hypothesis | CMH z | one-sided p | RD_MH [95% CI] | verdict |
|---|---|---|---|---|
| H-TENSOR (LAW > RANDLAW) | -.11 | .54 | -.005 [-.092, .082] | NOT SUPPORTED |
| H-SUPPLY (RANDLAW > NOLAW) | 2.25 | .012 | .105 [.012, .198] | SUPPORTED |

Preregistered reading: the capability effect of collision-generated laws is mostly COUPLING
SUPPLY, not concept-tensor content.

## Secondary

S1 generalisation (J >= .6 at V8 k8 among solvers; S1_V8_RELEASE.json):

| seed | RANDLAW | LAW | NOLAW |
|---|---|---|---|
| 20261010 | 52/75 | 58/75 | 39/62 |
| 20261011 | 59/72 | 60/71 | 17/64 |
| pooled | 111/147 (76%) | | |

| contrast | RD_MH [95% CI] | p |
|---|---|---|
| RANDLAW vs NOLAW | .309 [.174, .443] | 8.5e-8 |
| LAW vs RANDLAW | .053 [-.041, .148] | .13 |

S2 essential-rule provenance of RANDLAW solvers (the random-gain laws keep "law:" provenance):

| seed | provenance | solvers with an essential law | law rules writing ch0 |
|---|---|---|---|
| 3 | law 37, G0 14, mutation edit 12, lens 1 | 31/75 | 16 |
| 4 | law 44, mutation edit 15, G0 8, lens 1 | 36/72 | 15 |

Random-gain laws are used as essential parts about as often as tensor laws are (36: 34/91).

## Reading

On the composition-necessary task, a recursive ecology's collision-generated k-ary laws
matter because they SUPPLY k-ary couplings: on 2 seeds, capability +.105 and generalisation
+.309. Replacing the concept tensor's gains with random gains changes neither capability
(-.005) nor generalisation (.053, n.s.).

The concept tensor's learned latent factors are not detectably doing work in this
capability result. This is the charter-relevant negative of the push. The "concept tensor"
as an object of synthetic content is not supported here. What is supported is that recursive
collision with an inserted generated coupling builds better store/release machinery than
recombination of human-derived rules alone.

Chain of evidence for the supply reading:
- 48: the deficit is at release;
- 49/50: any read-back coupling, even single-source, rescues release;
- 51: gain content does not matter.

Limits:
- 2 seeds, one task family.
- The tensor gains may matter for tasks or rulers not tested here.
- The amp/bias of laws are still drawn as before (not tensor-derived), so this tests the
  tensor's per-source gains, which are its only content in the law.

## Predictions

| id | prediction | outcome |
|---|---|---|
| T1 | H-TENSOR SUPPORTED, p .3 | did not occur |
| T2 | H-SUPPLY SUPPORTED | RIGHT |
| T3 | RANDLAW solvers generalise >= 70% | 76%, RIGHT |
