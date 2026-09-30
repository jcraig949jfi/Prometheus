# HT-321a8fd8e0 / W1 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...3bea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Spec source: program.json experiments[W1], mechanism M3, lens L4.

## Spec field -> code

- hypothesis / mechanism (M3): `world.py` builds the primitive narrow-sense
  BCH(31,16) code over GF(2) from GF(32) with primitive polynomial
  x^5+x^2+1; generator g(x) = lcm of the minimal polynomials of alpha,
  alpha^3, alpha^5 (degree 15). The code checks, before any arm runs, that
  deg g = 15 and that the minimum nonzero weight over all 2^16 codewords is 7
  (asserted; abort otherwise). Encoding is systematic: codeword =
  m(x)x^15 + (m(x)x^15 mod g); message bits are codeword bits 15..30.
  n = 31 agents; agent i holds codeword bit i; honest reports = the codeword.
  Outcome = nearest-codeword decode: syndrome s(r) = r(x) mod g(x) (15 bits,
  kernel = the code); decoded codeword = r XOR leader[s]; outcome = bits
  15..30. The coset-leader table is built by enumerating error patterns in
  increasing weight (itertools.combinations order within a weight); the first
  pattern reaching a syndrome is its leader. This is exact nearest-codeword
  (maximum-likelihood) decoding; ties among equally-near codewords (possible
  only for received words at distance >= 4 from the code) are broken by this
  deterministic enumeration order.
- intervention (L4): for k = 1..8, per seed, sample 200 coalitions = uniform
  random k-subsets of the agents (without replacement within a coalition,
  independently across coalitions), each with a fresh uniform random 16-bit
  true decision. The coalition enumerates ALL 2^k report vectors on its own
  positions (non-members report honestly) and the coalition succeeds iff at
  least one report vector decodes to an outcome different from the true
  decision. "Prefer a different outcome" is read as: ANY outcome different
  from the truth counts (the spec names no specific target outcome).
- control: random-parity rule. A 16x31 GF(2) matrix P, drawn ONCE (fixed,
  rule seed 1001) and resampled until rank 16 so the outcome has 16 bits of
  entropy. Honest reports r0 = uniform random 31 bits per coalition; the true
  decision is defined as P r0 (so honest reports produce the truth);
  outcome(r) = P r. Same coalition search.
- null_twin: same random-parity rule family, but P is redrawn per seed
  (rank 16 enforced) from rng seed 2000+seed: matched report count (31),
  per-report entropy (uniform bits, 1 bit each), outcome entropy (16 bits),
  no minimum distance. The difference from CONTROL is only fixed-vs-per-seed
  matrix; the spec lists both and they describe the same rule family.
- positive_control: direct rule, d = 1. AMBIGUITY: "outcome bits read from
  16 agents". If 31 agents existed and only 16 were read, a single random
  agent would be pivotal only with probability 16/31, and the spec's own
  requirement "k=1 must manipulate in >= 0.99" could not hold for any
  correct implementation. Reading chosen: the direct rule has 16 agents,
  each holding one outcome bit, coalitions are drawn from those 16; outcome =
  the reports. Same search, k = 1..8.
- CHEAT: runs no rule. For each (seed, k) it writes success counts directly:
  0 of 200 for k <= 3, 200 of 200 for k >= 4 -- the pattern the success
  criterion asks for, injected into the observable.
- observable: per (arm, seed, k) the count of the 200 coalitions that can
  change the outcome; rates are computed in evaluate.py.
- success_criterion, as applied (evaluate.py): pooled rate over 20 seeds x
  200 coalitions = 4000 coalitions per k.
  TREATMENT (code rule) rate <= 0.02 for every k in {1,2,3} AND rate >= 0.5
  for every k in {4..8}; AND CONTROL (random-parity null) rate >= 0.5 at
  k = 1. AMBIGUITY: "over 20 seeds x 200 coalitions" read as the pooled rate,
  not per-seed; per-seed min/max are reported alongside, not used.
- failure_criterion: TREATMENT rate > 0.02 at any k <= 3, or CONTROL rate
  < 0.5 at k = 1.
- null_twin_meets_success: the code-rule clause (<= 0.02 for all k <= 3 AND
  >= 0.5 for all k >= 4) applied to NULL_TWIN pooled rates.
- positive_control_detected: POSITIVE_CONTROL pooled rate at k = 1 >= 0.99
  (the spec's own threshold).
- cheat_detected: the code-rule clause applied to CHEAT rates holds.
- outcome (PREREG, in code, in this order): INSTRUMENT_FAIL if either control
  undetected; else CONFOUNDED if null twin meets success; else SIGNAL if the
  success criterion holds and the failure criterion does not; else NULL.

## Parameters (all from the spec)

n = 31, message 16 bits, d = 7 (verified in code), k = 1..8, 200 coalitions
per k, 20 seeds (0..19) per arm, exhaustive 2^k search. Positive control
n = 16. Seeds: coalition RNG per (arm, seed) = numpy default_rng([arm_code,
seed]) with arm_code TREATMENT=1, CONTROL=2, NULL_TWIN=3, POSITIVE_CONTROL=4;
CONTROL matrix rng seed 1001; NULL_TWIN matrix rng seed 2000+seed.
No parameter is chosen from results.

## Compute

Expected well under 1 core-minute (coset table <= ~10^6 patterns; ~2M
decodes per arm, numpy vectorised, single thread). Measured with
time.process_time and written to run_meta.json; attempts counted in
attempts.json.

## Stupid explanations: what this run can and cannot address

All three are out of reach of this spec's arms: (1) a step at d/2 is exactly
the textbook unique-decoding radius, so a SIGNAL would confirm, not refute,
it; (2) coalitions only alter their own symbols by construction; (3) no
repetition/majority arm is in the spec, so it is not run.
