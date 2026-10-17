# ROBUST01 S1 RESULT: discovery at G1 under aeth01.op_xor_fold

Freeze c989c09a1 (PREREGISTRATION.md). Disposition by the frozen r01_reduce_s1.py:

**ROBUST_COMPOSITION_DISCOVERABLE, qualifier HELDOUT_NOT_GENERAL.**

k = 4/40 arm-C seeds have a certified candidate that is COMPOSE and AUTONOMOUS (6, 13, 16, 37), against 0/40 under
the contest law. k_gen = 1 (seed 13), short of the frozen bar of 2.

- Runs: plan_s1_search.json 2026-10-17T13:57Z-20:10:25Z, then plan_s1_certify.json 20:35:54Z-21:52:35Z, both on
  spectrex5:gpu0. REDUCTION_S1.json written 22:29:39Z.
- Data: C:/Prometheus-data/aether_robust01/S1/.
- evidence/S1/ holds:
  - REDUCTION_S1.json, both ledgers, and all 80 certificates (certs/);
  - S1_DESCRIBE.json;
  - the determinism recheck (recheck/: plan, ledger, compare script and output);
  - S1_DATA_SHA256.txt, the sha256 of every search unit and combine npz.

## Gates, in frozen order: all passed
- INCOMPLETE: 80/80 search units and 80/80 certificates present. Every rc was 0.
- REDUCER_DEFECT: the reproduction gate passed. The reducer's own counts on REACH01's G1 data are arm C COMBINE /
  COMPOSE / AUTO_COMPOSE / AUTO_ANY = 7 / 3 / 0 / 1 and arm A 0 / 0 / 0 / 0, equal to the published numbers.
- INSTRUMENT_DEFECT: 0 violations. Every unit is stamped aeth01.op_xor_fold with fold_physics sha 50aeee33...
  (= FREEZE.sha256).
  - All 90 certified candidates have seed-identical torus tables and position fraction exactly 1.0. That includes the
    71 that have energy-field contest events, which the gate does not constrain.

## Counts (Wilson 95%), 40 seeds per cell

| | fold C | fold A | contest C | contest A |
|---|---|---|---|---|
| COMBINE | 9 (0.123-0.375) | 0 (0-0.088) | 7 (0.088-0.320) | 0 (0-0.088) |
| COMPOSE | 4 (0.040-0.231) | 0 | 3 (0.026-0.199) | 0 |
| AUTO_COMPOSE (k) | **4** (0.040-0.231) | 0 | **0** (0-0.088) | 0 |
| AUTO_ANY | 9 (0.123-0.375) | 0 | 1 (0.004-0.129) | 0 |
| GEN_COMPOSE (fold only) | 1 (0.004-0.129) | 0 | | |

- Seeds with COMBINE under fold: 6, 13, 16, 24, 26, 29, 33, 37, 39.
- COMPOSE under fold: 6, 13, 16, 37. Each of these is also AUTONOMOUS.
- Fisher exact one-sided, fold C vs contest C (descriptive, not a registered test):
  - AUTO_COMPOSE 4 vs 0: p = 0.058;
  - AUTO_ANY 9 vs 1: p = 0.0072;
  - COMBINE 9 vs 7: p = 0.39.
  - Arm C is not a paired comparison: its search path follows the law's own certificates.

## Predictions (P-S1)

| registered prediction | outcome |
|---|---|
| fold arm C finds COMBINE in more than 7/40 seeds | held, narrowly: 9/40 (intervals overlap heavily) |
| fold arm A finds COMBINE in more than 0/40 seeds, on A's identical candidates | **failed**: 0/40 |
| disposition ROBUST_COMPOSITION_DISCOVERABLE | held: k = 4 |
| instrument gate passes (0 violations) | held |
| not every candidate is autonomous, because energy contests remain | **failed**: 90/90 autonomous, 71 with energy contests |

## Reading
- Under the contest law, discovered composition was never autonomous (0/40). Under the fold law, every composition
  the search found is autonomous: 4/4 COMPOSE seeds and 90/90 certified candidates. They combine at all 256 lattice
  positions and under all three physics seeds.
  - That matches S0: for the designed combiner, arbitration was the whole source of position fragility.
  - S1 extends it to discovered structure.
- The law change does not make composition more common in raw material.
  - Arm A evaluates exactly the same 20,480 patches per seed under both laws, and none combines under either.
  - Every gain is in the certificate-guided arm. COMBINE moves only 7 -> 9; what changes is that the structures found
    become autonomous (AUTO_ANY 1 -> 9).
- Energy-field contests remain in 71 of the 90 candidates, but none reaches the output. The prediction that some
  candidates would stay non-autonomous for that reason was wrong.
- Generality is weak.
  - Only seed 13's composition still combines on the held-out alphabet IN_H.
  - On IN_H, seeds 6 and 37 fall to rung 1: the output still varies in some slices, but no longer with each input
    for every value of the other. Seed 16 falls to rung 0, a constant.
  - The discovered functions are coarse: 2-4 distinct outputs over the 16 input pairs, against 7 for the planted
    a ^ b (tables below).
- Small-sample caution: k = 4 clears the frozen DISCOVERABLE bar (>= 2). The contrast with the contest law's 0/40 is
  suggestive, not decisive at n = 40 (one-sided Fisher p = 0.058). A 4x replication would need its own
  preregistration.

## Discovered functions (descriptive, post hoc: r01_s1_describe.py -> evidence/S1/S1_DESCRIBE.json)
- Scope: the first COMPOSE candidate of each composing seed, position-0 tables. Rows are a, columns b. The search
  alphabet IN is (0x0f, 0x33, 0x55, 0xaa); the held-out alphabet IN_H is (0x12, 0x6d, 0xb4, 0xe9). Within a seed,
  the 10 certified candidates share one certificate profile.
- **Separable** means f(a, b) = h1(a) ^ h2(b). Under the fold law, two independent single-input detectors whose writes
  converge on the output cell give exactly this: the law performs the join.

| seed | output values (IN) | separable | depends on a ^ b only | held-out rung | reading |
|---|---|---|---|---|---|
| s13 | {0x00, 0x64} | no | **yes, on both alphabets** | 2 | 0x64 * g(a ^ b), g nonlinear: a law-made XOR followed by a further stage |
| s6 | {0x18, 0xc5, 0xed} | no | no | 1 | an interaction, no simple form |
| s16 | {0x00, 0x12, 0x49, 0x5b} | **yes** | no | 0 | on IN: 0x49 * [a in {0x0f, 0x33}] ^ 0x5b * [b = 0x55]; constant 0 on IN_H |
| s37 | {0x00, 0x30} | **yes** (both alphabets) | no | 1 | on IN: 0x30 * (1 ^ a6 ^ b6 ^ b7); that form does not hold on IN_H |

Four values per input cannot pin down a bitwise formula. The "reading" forms describe IN only. The separability and
a ^ b columns are tested on each alphabet separately.

- Self-dissent: two of the four counted compositions (s16, s37) are separable.
  - The certificate correctly calls them COMPOSE, because each input path is necessary. But the join is the fold
    law's own XOR, not structure the search built.
  - Counting only non-separable compositions gives 2/40 (s6, s13). That still meets the DISCOVERABLE bar, but the
    count is post hoc and does not replace the frozen disposition.
  - Future preregistrations of discovery under an XOR-fold law should register separability as a criterion, in line
    with "attack triviality on fields the law never touches".
- Seed 13 is the composition closest to the planted mechanism. It computes on a ^ b and survives the change of
  alphabet.

## Deviations and incidents (no effect on outputs)
- Operator GPU priority:
  - S1 was stopped and resumed on the shared card several times: at 14:11Z, 14:29Z (on request of the skullport
    session smugglershole-10), 15:36Z, and 17:17Z for ComfyUI.
  - From 16:3xZ the agreed rule was in force: gfx_batch Blender bakes, which run at ~0% GPU on M2, may share the
    card; ComfyUI or skullport GPU > 20% stops the flight.
  - Units are written atomically, so a stopped unit simply reruns.
- Duplicate driver: a supervisor that TaskStop failed to kill started extra flight drivers on the same plan, at
  16:57:15Z and at 18:13:52Z.
  - Up to 4 GPU processes ran, against the lease's <= 2.
  - 25 units completed twice (seeds 27-39, both arms), all writing to the same output paths.
  - Determinism recheck: G1_C_s29, s33, s37 and s39 (double-run, all COMBINE) were rerun into S1_recheck/. All JSON
    fields except wall-clock times, and all combine npz arrays, are identical. The search is deterministic per seed,
    so which copy wrote last cannot change any output.
- The first launch, at 08:48Z, crashed before any unit ran: S1/search/ did not exist. The directory was created; no
  code changed.

## Next
S2a (R4 assisted reuse under fold; 32 units, then the frozen r4_reduce with S0's fold transplant table), then
r01_stage2b.py from this reduction, then S2b.
