# AETH-V2B-ROUTE01 preregistration: content-dependent retargeting (Branch B)

Order: roles/Aether/prompts/2026-10-07_three_flight, Experiment 3. Branch B by the frozen rule: PROP01 =
MULTIGENERATION_WEAK, not CAUSAL_PROPAGATION_SUPPORTED. Window 3 opened 02:21Z.

## Laws (B_balanced, P0, D50, 512^2; seeds rng 0xE2010000+k / physics 0xE2011000+k)
| id | semantics | rule after the frozen aeth01.v1 tick (a winner whose own arg0 was written keeps the written value) |
|---|---|---|
| V1 | aeth01.v1 | none |
| L1 | aeth01.reaim1 | winner (any field): arg0 += 1 |
| RT | aeth01.route1 | winner (any field): arg0 := (pre-tick byte at its target, in the field it won) & 3 |
| RN | aeth01.randaim1 (null) | winner (any field): arg0 := keyed-hash(seed, tick, site) >> 62 (2 bits) |

- RT differs from reaim1 in ONE rule. Payload and arg1 are untouched; no memory register; no message primitive.
- RN matches RT's trigger and value range without content: the order's "direction-randomization null".

## Assay
The PROP01 paired-world impulse assay, unchanged: one payload-bit impulse at an rng(0x1A9F+k)-chosen active WRITE
site after a 1000-tick warm-up, 3000 ticks in lockstep, conservative observer attribution, clamp counterfactual on
the earliest generation-1 site with a STRUCT/CARRY child.
- Code: route01_run.py, which is prop01_run.py with the law table and law step replaced.
- Conformance (qual/conformance_n64.json): V1 and L1 identical to PROP01's runner; CPU == GPU for V1/L1/RT/RN.
- The tracer known answers (Aether/test/test_prop01_tracer.py) apply to the shared tracer code.

## Rules (RULES.json; route01_reduce.py and route01_reduce_base.py docstrings are the exact text)
- Per-seed classes as PROP01 (multiply >= 3; clamp <= 0.2 and <= 0.5x the control fraction).
- Routing verdict for RT vs L1 and RN:
  - CONTENT_ROUTING_CAUSAL_REACH: >= 12/16 MULTIGENERATION seeds AND median reach >= 2x both AND median max_gen >
    both.
  - ROUTING_NO_GAIN: RT median ever-divergent sites <= L1's.
  - ROUTING_RANDOMLIKE: else, if RT median reach is within [1/1.5, 1.5] x RN's and RT median max_gen <= RN's + 1.
  - CONTENT_ROUTING_WEAK: otherwise.
- Gates: dup_RT_s0 identical; every unit rc=0.

## Disclosure: qualification seen (qual/, seeds 0-1)
| law | ever-divergent sites | max gen | peak concurrent |
|---|---|---|---|
| RT | 3 / 3 | 1 / 1 | 3 / 3 |
| RN | 10 / 11 | 5 / 3 | 5 / 9 |
| L1 | 2 / 8 | 1 / 2 | 0 / 8 |
| V1 | 2 / 2 | 1 / 1 | 2 / 2 |

Thresholds are PROP01's, unchanged except seeds_min (scaled 6/8 -> 12/16) and the new randomlike band (1.5x, chosen
for meaning).

## Scale and replication
16 seeds each for RT/RN/L1 (chains are rare, so replication is the bottleneck), 8 for V1, plus dup_RT_s0: 57 uncut
units, then 48 clamp units. ~300 s per unit at 4 concurrent, ~2-2.5 h in total.

Hashes (LF as in git):
  e2f461b94efcb66e354e261425ae5186b1b14ef694782f759fe104e94c89329b production/plan_uncut.json
  2a80f74986a6ff91550e5b0a73e02b49152a739629d1a6a000030f4eda84feea production/plan_cut.json
  5241c515db97e96e823ee6b97c32def5857fa3ebe7fb1ae1c69fc1bb99e6978d RULES.json
  0e419226e13fc765628bd8e8305dac4ce521c6adbf7cf767922f1e59f89162f7 route01_run.py
  878914eea310bfec6a01a1ac185163263c0db6d8dfc4b9fc490a5354010fd637 route01_reduce.py
  480cc8564e0b0b37f2ca93d30c7edb1b3ec03b5f1da87ae8b9a4547911f2cc13 route01_reduce_base.py
  9d034fc4c1dddb2e633fe683d60260e5b28b7b958dd8c72ddc2f76fb31c09b3c prop01_tree.py
  83a2ed0c6225fd2343fc38b7ad4cb868ea039cf9289a1d7dd9262cccff9ff296 route01_flight.py
  1e89830d62e50266705ab95250890a80ab45479f336fd5b894e5b6af7f773f65 ../../runpod/aeth01_canary/aeth01_gpu_kernel.py
