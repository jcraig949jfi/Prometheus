# AETH-V2B-OFFER01 RESULT: value-repertoire release (composition experiment)

Order: roles/Aether/prompts/2026-10-07_three_flight, Experiment 1 (window 00:15Z-04:15Z; closed 01:15Z).
Freeze 486787beb. Production 00:29Z-01:11Z, 25/25 units rc=0. Reduction production/REDUCTION.json
(offer01_reduce.v1, frozen RULES.json).

## Semantic audit (before any code)
The order's displaced-value uptake IS the V2-B TEST-3 exchange switch (aeth03_variants MOB x=1): a winning template
write hands the displaced byte to the emitter's payload, and an incoming payload write stands. L2 = reaim1 + exchange
is therefore a COMPOSITION of two existing mechanisms (AIM01 reaim1, TEST-3 exchange), not new physics.
TEST-3's recoil differs from reaim1 (arg0 += displaced byte on template wins vs arg0 += 1 on any win).
Conformance: X is bit-identical to aeth03 mob_r0x1e0; L1 is bit-identical to AIM01; CPU == GPU everywhere.

## Technical disposition: PASS
- 25/25 units rc=0.
- One table hash (504acba568bb3a02).
- dup_L2_s0 identical (final digest and delivered analysis).
- Coverage 0.99-1.00.
- ~400 s per 512^2 x 6000-tick unit at 4 concurrent; CuPy pool 2.1-3.1 GiB.

## Preregistered disposition: OFFER_REPERTOIRE_SUPPORTED
L2 vs BOTH reaim1 (L1) and exchange-only (X), activity-matched, on the DELIVERED payload view (direct uptake
excluded by construction):

| family | L2 - L1 | L2 - X | seeds beating both | margin |
|---|---|---|---|---|
| REPERTOIRE (distinct values per change) | +0.119 | +0.116 | 8/8 | 0.05 |
| NOVELTY (N64) | +0.218 | +0.196 | 8/8 | 0.05 |
| DISCOVERY (late-half new values / change) | +0.100 | +0.100 | 8/8 | 0.05 |
| DELIVERY (acquired bytes into opcode/arg1, share of template writes) | 0.366 median | | 8/8 | 0.10 |

Descriptive (medians, 8 seeds, 2000-tick window):

| | delivered: share with exactly 2 values | share with >= 4 values | mean distinct values | writer-payload mean distinct | downstream (opcode/arg1) mean distinct | uptake share of all template changes |
|---|---|---|---|---|---|---|
| L1 reaim1 | 0.944 | 0.001 | 2.06 | 2.07 | 2.09 | 0 |
| X exchange | 0.827 | 0.026 | 2.21 | 2.16 | 2.19 | 0.50 |
| L2 composition | 0.006 | 0.970 | 27.1 (26.1-27.5) | 26.7 | 6.08 | 0.32 |

Further L2 vs L1 / X, delivered channel: N16 +0.70 / +0.64; transitions per change +0.36 / +0.35; return-time median
5.4x / 4.5x. Downstream channel (opcode/arg1, untouched by every rule): N64 +0.12 / +0.10.

Neither part alone escapes the two-value catalogue (L1 2.06, X 2.21). Together they do, at every seed.

## Declared attack: is L2 a byte SHUFFLER? (production/shuffle_attack_s0.json; seed 0; descriptive)
| | template-byte multiset drift over the window (L1/byte) | payload entropy start -> end | rare-value positional persistence |
|---|---|---|---|
| L1 | 0.0060 | 7.996 -> 7.996 | 0.99 |
| X | 0.0001 | 7.938 -> 7.936 | 0.83 |
| L2 | 0.0071 (arg0 re-aim increments) | 7.707 -> 7.706 | 0.68 |

Reading:
- Exchange conserves the byte multiset (X: drift 0.0001). L2 conserves everything except the re-aim counter.
- Payload entropy is flat in every law: no new byte values are created anywhere (P0, copy/swap only).
- What changes under L2 is that tokens TRAVEL: only 68% of rare-value holdings stay in place over 2000 ticks, vs 83%
  (X) and 99% (L1).
- L2's repertoire release is therefore real at the level of each site (27 distinct values pass through a typical
  changing site, and late discovery stays > 0). Its mechanism is circulation/mixing of a conserved byte population:
  exchange makes values move as tokens, and re-aim stops them shuttling back and forth between two fixed partners.
  It is not generation of new values.
- The rule's success gate is met. The claim is runged accordingly:
  - **established:** the value repertoire seen by sites is released, reproducibly, beyond both components;
  - **not established:** that this is anything beyond conserved-token transport/mixing.
  PROP01 now asks whether such tokens carry causal consequences beyond their own movement.

## Answers to the order's primary questions
- More distinct values offered per writer? Yes: writer payload ~26.7 distinct values vs ~2.1.
- More distinct values reaching a target, and more than two per changing target? Yes: 97% of changing targets see
  >= 4 values; mean 27.
- Continued late catalogue growth? Yes: late-half discovery +0.10 per change vs both comparators.
- Material N64? Yes: +0.20-0.22.
- More transition diversity? Yes: +0.35 transitions per change.
- Downstream beyond the direct rule? Yes: 36.6% of winning template writes deliver an acquired byte into
  opcode/arg1, and the opcode/arg1 channel's N64 rises by +0.10-0.12.
- Share of change that is mandatory uptake: 0.32 under L2 (0.50 under X).
- Shuttle signature (two-value catalogue): present in L1 and X, absent in L2.

## Limitations
- One density (D50), B_balanced, P0, 512^2, 6000 ticks.
- The shuffler attack covers one seed and is descriptive.
- The DELIVERED channel counts values delivered by ordinary writes. Those values themselves originate from uptake,
  so "repertoire" here is the repertoire of circulating tokens.
- Margins were frozen after qualification (disclosed). Observed values are 2-4x the margins.

## Next (frozen rule)
OFFER_REPERTOIRE_SUPPORTED, so the PROP01 candidate is L2 (reaim_offer1), with comparators X (exchange-only) and L1
(reaim1).
