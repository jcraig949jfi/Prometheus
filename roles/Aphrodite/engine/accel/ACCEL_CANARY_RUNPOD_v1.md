# ACCEL_CANARY_RUNPOD_v1 -- frozen equivalence canary for the RunPod acceleration track

Status: FROZEN at commit time, BEFORE any accelerated evaluator exists on this branch.
Track: RunPod acceleration (engineering + conformance only). Branch
`aphrodite/accel-runpod-2026-09-23`, forked from clean science SHA `cf601fa3e`.

Operator ruling (2026-09-23): no accelerated backend may contribute scientific
results until it reproduces the M4 reference with ZERO unexplained semantic/charge
mismatches. This canary makes that operational and stricter: ANY mismatch = FAIL.
An explained mismatch is still not equivalence.

## Pinned reference (M4, science SHA cf601fa3e)

| file | sha256 |
|---|---|
| basis_v4.py | 221d4c62a20939a5e1d5e4ca8e31006a8e0d04917e801a328675c02e1b8c40aa |
| run_tier3c.py | 9f4912474b68842416c401a54e65ba1127877c4f4a7302ea6ee350e5a386e751 |
| tier3c.py | 38647cae5f8e3868683c252706e0c40c49a93aadd84c1a497402f3c5ba4ace93 |
| conformance.py | ab04d1ebe0098a2d0fda741d481420e72cc1c159cbb01fe244683af3f78840bc |
| engine.py | cb3e91ebf4e4d30e9a52d58d72d8859a30deeb015771e6d7a9e683954f74764c |
| meta_tribunal.py | 3a7dcfedc5bd2eda9650b08dbc0bdddc642f8941051c48c8b709c30e1f20549d |
| semantics.py | 5312f052cc7d19861d598825efd3565ac0d3697efa202ba6bf73e2e709674f94 |
| TIER3C_RESULTS_2026-09-22.json | bdeb3ad831d25fca53b7297a6b8ecee450726e419f119177c3076c6ed9321bbd |
| TIER3C_ARTIFACT_2026-09-22.json | afe040e960a0ee056160347c633553606a1bb848a611721699c928c1b7eb075e |

The runner MUST verify these hashes before running and report NOT_EQUIVALENT
(reason `reference_drift`) if any differs. No existing engine file may be modified;
the accelerated backend lives only in `roles/Aphrodite/engine/accel/`.

Reference evaluator = `basis_v4.run_program`. Reference search =
`run_tier3c.search_collect`. Reference end-to-end = the committed
`TIER3C_RESULTS_2026-09-22.json` / `TIER3C_ARTIFACT_2026-09-22.json` (serial
runtime 1196.7 s on M4).

## (a) EVALUATOR DIFFERENTIAL

The accelerated single-program evaluator must return EXACTLY `run_program`'s
value -- same type and same value, `None` included -- on every pair below.
Comparison is `type(a) is type(b) and a == b` (or both `None`).

A1. Conformance shapes. Programs: every `('fold', init, body, final)` over
`conformance.INITS x conformance.BODIES x conformance.FINALS` (900 programs), plus
`('expr', e)` for every e in `conformance.FINALS + conformance.BODIES`. Inputs: every
`xs + [m]` for xs in `conformance.SEQ_SHAPES`, m in `conformance.TRAILING`, with
`trailing=True` AND `trailing=False`, plus the extra boundary/extreme shapes built
from `conformance.NORMAL/BOUNDARY/EXTREME` (zero, negative, single-element,
10**12 elements; declared in the runner as `EXTRA_SHAPES`).

A2. Real candidate streams. At least 200,000 (candidate program, dev instance)
pairs drawn from the actual Tier-3C candidate streams: for every transplant
family x arm (EVOLVED, PRISTINE, SHAM_0..7) the recipient-0 stream
(`Lib.candidates(rng)` with the exact recipient rng) is walked and a
deterministic subset of candidates (a head prefix plus a fixed stride through the
first 250,000 positions) is evaluated on EVERY dev instance of that recipient
(no early exit). Required: zero mismatches.

## (b) SEARCH EQUIVALENCE

For every Tier-3C transplant recipient cell (3 usable families x 10 arms x 16
recipients = 480 cells, each with its exact dev set, rng, `Escrow(250000)`,
cap 250000, max_hits 5) the accelerated `search_collect` must return an
IDENTICAL hit list -- same programs, same coordinates, same charges, same order
-- and leave the escrow with an IDENTICAL `spent`. The meta-stage searches
(OBSERVE and VALIDATE, max_hits 1) are covered by (c) through the artifact file.

## (c) END-TO-END

The full Tier-3C pipeline (`run_tier3c.main` logic: conformance gate, generator
qualification, positive controls, shams, meta-development, transplant) executed
with the accelerated search substituted must reproduce:

- `TIER3C_ARTIFACT_2026-09-22.json`: every field, byte-for-byte after canonical
  JSON (sorted keys);
- `TIER3C_RESULTS_2026-09-22.json`: every field except the two wall-clock fields
  `written_utc` and `total_seconds` -- including all 480 `detail` rows
  (escrow_spent, qualified, charges, coordinate, solution_body, artifact_bytes,
  false_positives, recipient, arm, family), `per_family` summaries,
  `generator_qualification`, `meta_charges`, `evolved_sha256`,
  `selected_operator`, `conformance_gate`.

The run must write to a scratch/output directory, never over the committed files.

## Verdict

`EQUIVALENT` iff (a) mismatches == 0 AND (b) mismatches == 0 AND (c) mismatches == 0
AND the pinned hashes match. Otherwise `NOT_EQUIVALENT`, with every mismatch listed.
The verdict is written to `ACCEL_EQUIVALENCE_<backend>_<host>.json`
(this track: `ACCEL_EQUIVALENCE_runpod-backend_M4.json` locally, and
`ACCEL_EQUIVALENCE_runpod-backend_<pod>.json` on the pod).

## Timing (non-gating)

Speedup is reported as candidates/second (accelerated vs reference search over
the same (b) cells, same host, same moment) and end-to-end wall-clock versus the
reference's 1196.7 s. On M4 the science seat shares the CPU and the runner is
limited to <= 2 worker processes, so M4 timings are INDICATIVE ONLY.
Timing never affects the verdict; equivalence does.
