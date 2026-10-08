# P-ERASE probe set and P-PRES seed set (C-009-T018; text for PREREG_DRAFT s5, OPEN 2)

Author: Cadmus[m1-a86ec5e4], claude-opus-5-5, 2026-10-07. Preparation only: nothing below was evaluated on a
subject or a registered arm; the plumbing tests use a hand-wired construction (tests/test_ares_client.py
`_leak_construction`). Code: rso/witness/ares_client.py (erase_probe_set, pres_seed_set, p_erase_count,
p_pres_diffs, regime_of).

## 1. P-ERASE (native boundary B2: the episode reset), paired carry-over

Probe set: 64 triples (pre_a, pre_b, probe), generated deterministically by `erase_probe_set()` from seed 800000
upward: pre_a draws r = 0, pre_b draws r = 1, probe alternates r = 0 / r = 1 (32 each). Every seed is used once.
Regimes are read from the world only (`regime_of`, oracle; no organism is run to choose seeds).

Per probe and per arm, two FRESH runtimes run [pre_a, probe] and [pre_b, probe] in W15 "present"; the probe
episode's 40 actions are compared position by position. Statistic: D = total number of differing actions over the
64 probes (an exact count; deterministic; no sampling and no threshold beyond zero).

Gate (registered):
  X        PASS iff D = 0. FAIL names the first probe with a difference.
  X-LEAK   the fire member: D > 0 shows the probe can see a leak through this subject.
  P-ERASE for X is QUALIFIED only if X-LEAK has D > 0. If X-LEAK has D = 0 (for example a subject with no plastic
  edge, so nothing can leak), P-ERASE is DETECTION_UNQUALIFIED for X, which PREREG_DRAFT s6 already maps to that
  outcome class.
What it covers: carry-over of anything episode k wrote into episode k+1 (activations, plastic W1, any other state)
that changes an action. What it does not: a carry that never changes an action within the next episode; leaks
across more than one episode (W1 is not overwritten by a later episode under X-LEAK, so the one-step pair is the
strongest case for this construction, but other leak shapes are not enumerated).

## 2. P-PRES (restart-style twin): fixed seed set

Seed set: 32 pairs (warmup, seed) from `pres_seed_set()`, seed 850000 upward; seeds alternate r = 0 / r = 1 and
each warm-up draws the opposite regime. Per pair: [warmup, seed] on one runtime (correct reset between them) vs
[seed] on a fresh instance of the same genome. Statistic: total differing actions over the 32 seed episodes.
Gate: PASS iff 0. (On the construction, the correct reset gives 0 and the leaky reset gives > 0.)

## 3. Seed hygiene (PREREG_DRAFT s3)

All P-ERASE / P-PRES seeds lie in [800000, 900000): above balanced_seeds_for's scan range (20000-25000) and
EVAL_SEEDS (10000+), below the witness seed floor (900000), so they never coincide with the n = 2048 ruler seeds.
Both generators take `exclude=`: at freeze, the subject GA episode seeds recorded by the driver (C-009-T016) are
passed in, and the final lists are committed with the preregistration. The current lists (no exclusions) span
800000-800194 and 850000-850067.

## 4. Cost

P-ERASE: 64 probes x 2 conditions x 2 episodes = 256 episodes per arm; P-PRES: 32 x (2 + 1) = 96 episodes per arm.
At the smoke rate (0.08 CPU-s per 64 organisms x 16 episodes) both are well under a CPU-second per arm.

## 5. What was run

Unit tests only: the hand-wired construction registers D > 0 under LeakyResetRuntime and D = 0 under the correct
reset; with its plastic rate zeroed even the leaky reset gives D = 0 (the fire case cannot fire); P-PRES likewise.
No subject, no registered arm, no accuracy, reward or retention number.
