# THESEUS-53 verdict: bounding the concept tensor's contribution, 6 seeds (prereg roles/Theseus/prereg/2026-10-10_tensor_bound/, 03fc37bf3)

New runs (PYTHONHASHSEED=0, flags as 40, --workers 2):

| seed | LAW | RANDLAW (--random-law-gains) |
|---|---|---|
| 20261012 | v0_2t0_s5_2026-10-10 | v0_2t0rg_s5_2026-10-10 |
| 20261013 | v0_2t0_s6_2026-10-10 | v0_2t0rg_s6_2026-10-10 |

Evals: comp_task_s{5,6}_tensor_2026-10-10 (--a LAW --b RANDLAW, gate inside).
Pooled with 52's seeds 1-4: POOLED_TENSOR_6SEED.json, S_V8_RELEASE_TENSOR_6SEED.json.

Incident: the seed-5 chain (LAW then RANDLAW in one job) hit the 2 h background limit during
RANDLAW (gen 20). The partial RANDLAW output was deleted and the run restarted from scratch.
The result is deterministic and independent of worker count, so there is no scientific
change.

GATE (seeds 5, 6): 1-part controls .195-.2025; 2-part controls 1.0. PASSES.

## Primary: H-TENSOR-6 (D solver share, LAW vs RANDLAW, 100 per run)

| seed | LAW | RANDLAW | RD [95% CI] |
|---|---|---|---|
| 20260930 | 91 | 82 | .09 [-.006, .186] |
| 20261009 | 78 | 72 | .06 [-.060, .178] |
| 20261010 | 75 | 75 | .00 |
| 20261011 | 71 | 72 | -.01 |
| 20261012 | 74 | 82 | -.08 [-.193, .035] |
| 20261013 | 73 | 83 | -.10 [-.212, .015] |

CMH z -.28, one-sided p .61; RD_MH -.007 [-.054, .041].
VERDICT: NOT SUPPORTED (RD_MH <= 0).

BOUND (preregistered rule: the CI upper bound .041 < .10): the concept tensor's content
contributes less than 10 points of deep-solver share (95% CI). The interval caps it at about
4 points, with a point estimate of zero.

## Secondary: generalisation (J >= .6 at V8 k8 among solvers)

| seed | LAW | RANDLAW |
|---|---|---|
| 1 | 77/91 | 59/82 |
| 2 | 59/78 | 55/72 |
| 3 | 58/75 | 52/75 |
| 4 | 60/71 | 59/72 |
| 5 | 51/74 | 64/82 |
| 6 | 55/73 | 64/83 |

CMH one-sided p .22; RD_MH .021 [-.034, .076]. No tensor contribution detected.

Essential-rule provenance, seeds 5-6:

| run | provenance | solvers with an essential law |
|---|---|---|
| RANDLAW s5 | law 39, mutation edit 17, lens 4, G0 1 | 33/82 |
| RANDLAW s6 | law 37, G0 14, mutation edit 9 | 32/83 |
| LAW s5 | law 44, mutation edit 12, lens 6, G0 6 | 36/74 |
| LAW s6 | law 18, mutation edit 13, G0 5, lens 3 | 17/73 |

## Reading (with 51/52)

On the composition-necessary cue-recall task, over 6 master seeds:
- The collision-generated k-ary law matters as a SUPPLY of couplings: random-gain laws vs
  none, 4 seeds, capability RD .143 [.075, .210], generalisation RD .216 [.128, .303].
- The concept tensor's learned gains add NOTHING detectable: capability RD -.007
  [-.054, .041], generalisation .021 [-.034, .076].
- The 4-seed hint of a small tensor effect (.035) came from seed 1, which overestimated every
  effect in this campaign. It reversed on seeds 5-6.

This is the decisive negative for the charter's central object in this substrate and task
family. The concept tensor, as implemented (CP-form gains from parents' latent factors), does
not carry content that matters here. What the recursive ecology contributes is the act of
inserting a new k-ary coupling at every collision.

## Predictions

| id | prediction | outcome |
|---|---|---|
| V1 | H-TENSOR-6 SUPPORTED, p .2 | did not occur |
| V2 | the BOUND is stated | RIGHT (upper .041) |
| V3 | seeds 5-6 RD <= .03 | RIGHT (-.08, -.10) |
