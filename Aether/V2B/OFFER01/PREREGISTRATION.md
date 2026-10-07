# AETH-V2B-OFFER01 preregistration: value-repertoire release (composition experiment)

Order: roles/Aether/prompts/2026-10-07_three_flight (Experiment 1). Seat Aether[m2-95eba442], SPECTREX5, RTX 5060 Ti.
Branch aether/offer01-2026-10-06 from main 013e7ce5e. Window 1: 2026-10-07 00:15Z - 04:15Z.

## Semantic-equivalence audit (order: "read the exact TEST-3 exchange law")
- Source: Aether/observatory/aeth03_variants.py, MOB family (V2-B DEV-3 / TEST-3):
  "x (exchange): a winning template write hands the displaced byte back to the EMITTER's payload";
  implemented as next_payload = where(mob_won & ~payload_winner, mob_disp, next_payload). mob_won and mob_disp
  cover template fields 0-3 only; mob_disp is the target's pre-tick byte.
- The order's displaced-value uptake ("the writer takes the target's pre-write byte as its new payload; a committed
  external payload write wins") is EXACTLY this exchange switch.
- L2 = reaim1 + exchange is therefore a COMPOSITION of two existing mechanisms (AIM01's reaim1 and TEST-3's
  exchange), NOT new physics. It is reported as a composition experiment.
- TEST-3's recoil (r) differs from reaim1: recoil turns direction by the displaced byte (arg0 += d) on template
  wins; reaim1 adds 1 on any win (energy transfers included).
- TEST-3 setting differences: 128^2, perturbation-ON warm-up, a different (P1) ruler. OFFER01 keeps P0 throughout,
  the D50 soup, B_balanced and 512^2.

## Laws (all B_balanced, perturbation OFF, D50, seeds rng 0xE2010000+k / physics 0xE2011000+k)
| id | semantics | rule after the frozen aeth01.v1 tick |
|---|---|---|
| L1 | aeth01.reaim1 | every winning source (any field): arg0 += 1, unless its arg0 was written |
| X | aeth03.mob_r0x1e0 (exact TEST-3 exchange) | every template-winning source: payload := displaced pre-tick target byte, unless its payload was written |
| L2 | aeth01.reaim_offer1 | both. Ordering: (1) v1 commits; (2) re-aim on arg0; (3) uptake on payload. Disjoint fields; each yields to an external write on its field |

Conformance (qual/conformance_n64_t300.json, all_ok):
- X is bit-identical to aeth03_variants.step("mob_r0x1e0") (CPU), seeds 0-1, 30 checkpoints.
- L1 is bit-identical to AIM01 reaim1.
- CPU == GPU for L1, X and L2, including every analysis output.

## Channels (no transformed counters)
- DELIVERED: per site, the payload value last delivered by an ordinary winning write. Direct uptake cannot change
  it. This is the primary channel.
- DOWNSTREAM: opcode and arg1 held values (no rule touches them). Reported.
- RAW payload and writer payload: diagnostic.
- Provenance: an acquired flag is set by uptake and inherited from the source on an ordinary payload write.
  - DELIVERED_CONTENT = winning template writes carrying an acquired byte.
  - DOWNSTREAM_NONPAYLOAD = those landing in opcode/arg1.
  - DIRECT_UPTAKE share = uptake-driven payload changes / all template changes.
- Meter: the AIM02 non-AIM meter, unchanged (8/8 known answers, positive control through a decision rule):
  activity-binned upc, tpc, n16, n64, dr2, return gaps, U histograms.

## Rules (RULES.json)
For each seed k, compare L2 with L1 and with X (same k) on DELIVERED, activity-matched, coverage >= 0.5.
- REPERTOIRE: upc diff >= 0.05 vs BOTH.
- NOVELTY: n64 diff >= 0.05 vs BOTH.
- DISCOVERY: dr2 diff >= 0.05 vs BOTH.
- A family is material in >= 7/8 seeds.
- DELIVERY: L2's DOWNSTREAM_NONPAYLOAD share >= 0.10 in >= 7/8 seeds.
- Disposition:
  - OFFER_REPERTOIRE_SUPPORTED = all three families AND DELIVERY.
  - OFFER_WEAK = any family material, but not all.
  - OFFER_TRIVIAL = none (the A<->B shuttle / fixed-catalogue signature).
- Gates (else MEASUREMENT_FAILED): one table hash; dup_L2_s0 identical; 25/25 rc = 0.

## Disclosure (qualification seen before freezing; qual/REDUCTION.json)
512^2 x 6000, W 2000, seeds 0-1.

| | delivered: U2 share / U4+ share / mean U | downstream mean U | acquired into opcode/arg1 | uptake share of changes |
|---|---|---|---|---|
| L1 | 0.951 / 0.002 / 2.05 | 2.09 | 0 | 0 |
| X | 0.829 / 0.027 / 2.21 | 2.19 | 0.50 | 0.50 |
| L2 | 0.007 / 0.969 / 27.3 | 6.06 | 0.36 | 0.32 |

- L2 minus L1 / minus X: n64 +0.22 / +0.20; upc +0.12; dr2 +0.10; n16 +0.70 / +0.63; return median 5.4x / 4.5-5.0x.
- The margins are AIM02's (0.05), unchanged; delivery 0.10 was chosen for meaning. Observed values clear them 2-4x.
- Runtime: ~350 s per unit at 4 concurrent; CuPy pool 2.1-3.1 GiB.

## Planned attack (reported; not part of the rule)
Exchange makes each win a SWAP (writer payload <-> target byte), so the global byte multiset is approximately
conserved. L2 may be a byte SHUFFLER: values diffuse like particles while re-aim randomizes their direction.
The report will test conservation and diffusion-like spreading descriptively, and will not call a shuffler "rich".

## Production
- 3 laws x 8 seeds + dup_L2_s0 = 25 units, 512^2 x 6000, W 2000. ~40 min at --jobs 4.
- Hashes (LF as in git):
  f69ea0010eea2285048b8a9cfbd7a1ed139aabf0efeb23b982f0935c509d492f production/plan.json
  b902be5fe1d727801a8180081e791207264429b18e4559671f3e71b6283d55fc RULES.json
  8afdde59ed46979d387385b79d22535b2fe082e17598022988a75b43918b8a57 offer01_run.py
  76766362e65bb2fa6c11ff569d01741b1288492012285586750c9a878e072d6e offer01_reduce.py
  6a47440829370ff26c30036b9c790dad09c706da60a4e31c385d668aea1c819d offer01_flight.py
  ef778a7fabc0b242b6d65a6362d4300fadc63d26db0a03e82ea621b6dd07ecd6 ../AIM02/aim02_meter.py
  1e89830d62e50266705ab95250890a80ab45479f336fd5b894e5b6af7f773f65 ../../runpod/aeth01_canary/aeth01_gpu_kernel.py
