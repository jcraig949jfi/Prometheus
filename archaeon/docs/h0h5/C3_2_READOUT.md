# C3-2 readout (cs-c3-2) -- PARTIAL

Written 2026-09-10T13:20:31+00:00. Numbers only; Harmonia rules. Unit for accuracy: the IC sample (four shared samples, one seed_root). Unit for D3: the rule.

## Progress

- C3-acq: 8 completed, 111 queued, 1 running
- C3-base: 6 completed
- C3-hist: 6 completed
- C3-null: 18 completed

## Exact-symmetry null (C3-null vs its C3-hist twin)

Fields compared per IC sample: accuracy_stable, n_incorrect_stable, mask_digest_stable, accuracy_at_T, n_incorrect_at_T, mask_digest_at_T, misclassified_ic. Spacetime digest excluded by design (declared not an image under a transform).

- checked 18: IDENTICAL 18, NOT_IDENTICAL 0, INDETERMINATE 0

- GKL:complement -> IDENTICAL
- GKL:reflect -> IDENTICAL
- GKL:reflect_complement -> IDENTICAL
- exp:complement -> IDENTICAL
- exp:reflect -> IDENTICAL
- exp:reflect_complement -> IDENTICAL
- maj:complement -> IDENTICAL
- maj:reflect -> IDENTICAL
- maj:reflect_complement -> IDENTICAL
- par:complement -> IDENTICAL
- par:reflect -> IDENTICAL
- par:reflect_complement -> IDENTICAL
- particle1:complement -> IDENTICAL
- particle1:reflect -> IDENTICAL
- particle1:reflect_complement -> IDENTICAL
- particle2:complement -> IDENTICAL
- particle2:reflect -> IDENTICAL
- particle2:reflect_complement -> IDENTICAL

## Per-rule accuracy by IC sample (stable criterion)

- C3-acq random_000: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-acq random_001: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-acq random_002: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-acq random_003: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-acq random_004: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-acq random_005: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-acq random_006: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-acq random_007: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-base all_one: [0.49, 0.54, 0.48, 0.46] mean 0.492
- C3-base all_zero: [0.51, 0.46, 0.52, 0.54] mean 0.508
- C3-base centre_00: [0.51, 0.46, 0.52, 0.54] mean 0.508
- C3-base centre_01: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-base centre_10: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-base centre_11: [0.49, 0.54, 0.48, 0.46] mean 0.492
- C3-hist exp: [0.58, 0.69, 0.58, 0.59] mean 0.61
- C3-hist GKL: [0.79, 0.8, 0.85, 0.81] mean 0.812
- C3-hist maj: [0.0, 0.0, 0.0, 0.0] mean 0.0
- C3-hist par: [0.74, 0.79, 0.87, 0.76] mean 0.79
- C3-hist particle1: [0.69, 0.78, 0.74, 0.67] mean 0.72
- C3-hist particle2: [0.71, 0.8, 0.74, 0.69] mean 0.735

IC-sample column means (all non-null completed rows): [0.2755, 0.293, 0.289, 0.276]

## ICC(1), rule as group, four IC samples as measures

- all rules: {"icc1": 0.9927, "msb": 0.444, "msw": 0.0008, "k": 4, "groups": 20, "dropped": 0, "grand_mean": 0.2834}
- excluding structural zeros (rules with 0.0 on every sample under `stable`): {"icc1": 0.9082, "msb": 0.0731, "msw": 0.0018, "k": 4, "groups": 9, "dropped": 0, "grand_mean": 0.6297}

## D3 over C3

- {"status": "PARTIAL", "reason": "acquisition arm incomplete; D3 needs eight independent rules per descriptor region"}
