# THESEUS-52 verdict: tensor vs supply, pooled over 4 seeds (prereg roles/Theseus/prereg/2026-10-10_tensor_vs_supply_s12/, b911a93aa)

New runs (PYTHONHASHSEED=0, --random-law-gains, flags as 40, --workers 2):
- RANDLAW s1 v0_2t0rg_2026-10-10 (default seed 20260930)
- RANDLAW s2 v0_2t0rg_s2_2026-10-10 (20261009)

Evals: comp_task_s{1,2}_rg_2026-10-10 (vs NOLAW, gate inside; LAW/NOLAW rows copied,
deterministic).
Pooled with 51's seeds 3-4: POOLED_TENSOR_4SEED.json, POOLED_SUPPLY_4SEED.json,
S1_V8_RELEASE_4SEED.json.

GATE (seeds 1, 2): 1-part controls .195-.2025; 2-part controls 1.0. PASSES.

## D solver share (100 per run)

| seed | LAW | RANDLAW | NOLAW |
|---|---|---|---|
| 20260930 | 91 | 82 | 52 |
| 20261009 | 78 | 72 | 66 |
| 20261010 | 75 | 75 | 62 |
| 20261011 | 71 | 72 | 64 |

## Primaries

| hypothesis | CMH z | one-sided p | RD_MH [95% CI] | verdict |
|---|---|---|---|---|
| H-TENSOR-4 (LAW > RANDLAW) | 1.18 | .118 | .035 [-.023, .093] | INDETERMINATE |
| H-SUPPLY-4 (RANDLAW > NOLAW) | 4.31 | 8.0e-6 | .143 [.075, .210] | SUPPORTED |

Per-seed RD for H-TENSOR: .09, .06, .00, -.01. Any tensor contribution is concentrated in
seed 1, the seed that overestimated every effect in this campaign.

## Secondary: generalisation (J >= .6 at V8 k8 among solvers)

| arm | release |
|---|---|
| LAW | 254/315 (81%) |
| RANDLAW | 225/301 (75%) |
| NOLAW | 129/244 (53%) |

| contrast | RD_MH [95% CI] | p |
|---|---|---|
| RANDLAW vs NOLAW | .216 [.128, .303] | 7.9e-8 |
| LAW vs RANDLAW | .059 [-.007, .125] | .039; CI includes 0, descriptive |

Essential-rule provenance, RANDLAW seeds 1-2:

| seed | provenance | solvers with an essential law |
|---|---|---|
| 1 | law 28, mutation edit 15, G0 9, lens 3 | 24/82 |
| 2 | law 31, G0 7, mutation edit 7, lens 3 | 30/72 |

## Reading (4 seeds)

Most of the capability and generalisation effect of collision-generated laws is COUPLING
SUPPLY:
- random-gain laws vs no laws: capability +.143, generalisation +.216
- tensor gains vs random gains: capability +.035 (CI -.023 to .093), generalisation +.059
  (CI -.007 to .125)

A small contribution from the concept tensor's learned content cannot be excluded. Its
point estimates are about a quarter the size of the supply effect, and on capability most of
it comes from seed 1.

Claim, stated at the right size: "in this substrate and task family, the concept tensor's
content contributes at most a small fraction of the law effect; the bulk is the supply of a
k-ary read-back coupling that collisions insert into every child."

## Predictions

| id | prediction | outcome |
|---|---|---|
| U1 | H-TENSOR-4 SUPPORTED, p .25 | did not occur (INDETERMINATE) |
| U2 | H-SUPPLY-4 SUPPORTED | RIGHT |
| U3 | seed-1 RANDLAW >= 80 | 82, RIGHT |
