# AETH-V2B-AIM02 RESULT: matched-flicker richness test

Order: roles/Aether/prompts/2026-10-06_aim02. Seat Aether[m2-95eba442], SPECTREX5 (M2), RTX 5060 Ti. Branch
aether/aim02-2026-10-06 (from main 9bffb1f7c, where AIM01 is integrated). Freeze 619dd3b25; code, rules and plan
were unchanged at reduction. Production 2026-10-06 09:33Z - 10:54:20Z (4888 s). Reduction: production/REDUCTION.json
(aim02_reduce.v1, rules sha256 recorded). Post-hoc (descriptive, labelled): production/posthoc_offer_*.json.
AIM01 status carried forward: frozen label REAIM_NONTRIVIAL_CANDIDATE (historical); current disposition
REAIM_SUPPORT_CONFIRMED__NONTRIVIALITY_OPEN, which AIM02 adjudicates.

## Technical disposition: PASS
- 65/65 units rc=0.
- One table hash (e82b8ca05161d8e7).
- Determinism duplicate dup_L1D50_s0 identical (final digest and full primary analysis).
- Activity-matched coverage of L1 columns: 0.90-0.94 against the comparators.
- Instrument qualification (before the freeze):
  - 8/8 known answers pass, including AIM_BOOKKEEPING = exactly 0, and the positive control through the frozen
    decision rule (expanding catalogue -> RICHNESS_SUPPORTED; flicker vs flicker -> FLICKER_EQUIVALENT).
  - Conformance: L0/L1 bit-identical to AIM01, C1/C2 bit-identical to ER01 R1/R2, CPU == GPU.

## Preregistered disposition: RICHNESS_WEAK
At every density, 8/8 seeds against BOTH comparators:
- NOVELTY (N64) 0/8 material: median diff +0.0024 / +0.0025 / +0.0026 vs margin 0.05.
- REPERTOIRE (unique per change) 0/8: +0.0022.
- DISCOVERY (late half) 0/8: 0.0000.
- TRANSITIONS 0/8: +0.0046 / +0.0047 / +0.0049.
- RECURRENCE (return-time median ratio) 8/8 material: 2.0x vs margin 1.5.
- N16 8/8 material: +0.099 to +0.101.

No density is SUPPORTED (NOVELTY not material). RECURRENCE and N16 make it WEAK: richness exists only at a 16-tick
memory and in return timing, and it does not persist with 64-tick memory. That is the order's WEAK clause verbatim.

## What the numbers say (production medians; 8 seeds per condition; non-AIM fields; 2000-tick window)

| | L1D25 | L1D50 | L1D75 | C1FREE | C2RICH | L0D25 | L0D50 | L0D75 |
|---|---|---|---|---|---|---|---|---|
| changing columns (share of sample) | 0.011 | 0.030 | 0.048 | 0.0034 | 0.0030 | 0.0008 | 0.0030 | 0.0059 |
| late non-AIM turnover (site/tick) | 0.0051 | 0.0149 | 0.0247 | 0.0060 | 0.0045 | 0.0005 | 0.0018 | 0.0036 |
| changing site-fields holding exactly 2 values | 0.961 | 0.919 | 0.882 | 0.986 | 0.984 | 0.993 | 0.983 | 0.973 |
| holding >= 4 values | 0.0007 | 0.0030 | 0.0075 | 0.0002 | 0.0002 | 0 | 0.0002 | 0.0007 |
| mean distinct values U | 2.040 | 2.084 | 2.126 | 2.014 | 2.016 | 2.007 | 2.017 | 2.028 |
| N16 (column mean) | 0.109 | 0.112 | 0.115 | 0.001 | 0.002 | 0.083 | 0.086 | 0.088 |
| N64 | 0.0044 | 0.0058 | 0.0070 | 0.0009 | 0.0011 | 0.0031 | 0.0035 | 0.0039 |
| return gaps p10/p50/p90 (dominant activity bin) | 2/4/16 | 2/4/16 | 2/4/16 | 2/2/4 | 2/2/5 | 2/3/14 | 2/3/14 | 2/3/14 |

Activity-matched L1 minus the same-density L0 (Q1): N16 +0.021 to +0.023; N64 +0.0007 to +0.0009; upc +0.0006;
tpc +0.0013 to +0.0016; dr2 0; return median 1.32-1.33x.

Qualification (W 4000 vs W 2000): each site's catalogue is unchanged. The U histograms are identical; not one new
value appears in 2000 extra ticks.

## Post-hoc localization (NOT preregistered; descriptive only)
posthoc_offer_probe.py: seed 0, 512^2, final 500 of 3000 ticks, AIM02 sample grid. Using the frozen kernel's
observer, for each changing non-AIM target field it counts the distinct values offered by WINNING writes and the
distinct winning writers.

| | opcode: held / offered / writers | arg1 | payload | offered <= 2 |
|---|---|---|---|---|
| L1D50 | 2.10 / 2.10 / 2.10 | 2.09 / 2.09 / 2.11 | 2.05 / 2.05 / 2.06 | 0.90-0.95 |
| L0D50 | 2.01 / 2.01 / 1.97 | 2.01 / 2.01 / 1.95 | 2.02 / 2.02 / 1.93 | 0.98-0.99 |
| C1FREE | 2.01 / 2.01 / 1.97 | 2.01 / 2.01 / 1.95 | 2.01 / 2.01 / 1.63 | 0.99 |

Reading:
- A flickering target-field, even under re-aim, is reached by about 2 distinct winning writers, each delivering its
  own (nearly fixed) payload. Held = offered exactly.
- Re-aim rotates a writer's DIRECTION, but each writer still writes only the one field its arg1 selects, and few
  neighbours select any given field. Its payload changes only when another writer happens to overwrite that payload.
- So re-aim widens WHERE the flicker happens, and stretches its timing (a rotating writer returns every ~4+ ticks:
  return median 4, p90 16). It does not raise how many different things arrive at a site.

## Answers (order s16)
1. **Does L1 remain richer than L0 when arg0 is excluded?** Barely. Activity-matched against same-density L0:
   N16 +0.02, N64 +0.0008, unique-per-change +0.0006, transitions +0.0015, discovery 0, return time 1.33x. The
   repertoire is the same (U ~2.04-2.13 vs 2.01-2.03).
2. **16 -> 64-tick memory?** The novelty disappears. Against matched flicker, L1's N16 excess of +0.10 becomes N64
   +0.0025 (40x smaller), at every density and seed. AIM01's ~0.10 non-AIM novelty was revisitation just outside a
   16-tick memory.
3. **At matched change counts, more unique states than flicker?** No material difference: +0.002 values per change.
   88-96% of L1's changing site-fields hold exactly 2 values over 2000 ticks with 256+ changes, against 98-99% for
   flicker.
4. **Late acquisition or saturation?** Saturation. Late-half discovery is 0.0000 in every L1 condition. Doubling the
   window adds no value at all.
5. **Broader return times?** Yes: median 4 vs 2, p90 16 vs 4-5, against the flicker comparators. But L0 (B_balanced,
   no re-aim) already shows 3 / 14. The breadth is mostly starvation-gated timing plus rotating-writer period, not
   repertoire.
6. **Transition diversity materially higher?** No: +0.005 transitions per change vs a 0.05 margin. With U ~2, the
   transitions are A->B and B->A.
7. **Reproduces across densities and seeds?** Yes, extremely tightly. Every family's verdict is identical at
   D25/D50/D75 and in 8/8 seeds (N16 diff range 0.097-0.101).
8. **Disposition:** RICHNESS_WEAK by the frozen rule, driven only by N16 and return-time ratio, which fail to persist
   at 64-tick memory. In substance the state repertoire is FLICKER_EQUIVALENT. The order's null reading applies:
   **REAIM_MOBILE_BUT_TRIVIAL**. Fixed aim was a real causal bottleneck for WHERE the medium can change; simple
   deterministic retargeting distributes the old two-state flicker over a larger support, with slower, rotating
   timing.
9. **Strongest alternative explanation.** The comparators are an imperfect match in TIMING. Free-compute and
   rich-rain flicker are fast period-2 alternation, while B_balanced (L0) and L1 alternate slowly and irregularly.
   The RECURRENCE and N16 "excess" is therefore partly a property of the comparators' unusually regular timing, not
   of re-aim. Against L0 at the same density the excess shrinks to N16 +0.02 and 1.33x. The real conclusion
   (bounded ~2-value repertoire, no late discovery) does not depend on the comparator choice; the WEAK label does.
10. **Next: content or richer retargeting?** Neither content propagation (there is no rich medium to carry it) nor
    faster or arg1 re-aim.
    - The measured failure mode places the bound upstream of aim: each target receives about 2 distinct offers,
      because the writers reaching it carry fixed payloads.
    - Any retargeting that only changes WHO writes WHERE, among fixed-payload neighbours, can at best produce
      K <= 4 state flicker.
    - Per the order's s12 ("design the next rule from the measured failure mode"), the next physics must change
      WHAT a writer offers, not where it points.

## Limitations
- Comparator timing mismatch (above): the WEAK label rests on clauses (N16, RECURRENCE) that a timing-matched
  comparator might not trigger.
- Primary repertoire metrics are single-field. A joint (opcode, arg1, payload) state could be richer than each
  field, but each field is ~2-valued and changes are field-local, so the joint catalogue is bounded by about 8 and
  shows the same saturation (AIM01 post-hoc non-AIM novelty ~0.10 at 16 ticks).
- One energy economy for L1 (B_balanced), P0, 512^2. The window starts at tick 4000 (stationary since tick ~50).
- The offer probe covers one seed and 500 ticks and is descriptive.
- Thresholds were frozen with the qualification numbers known (disclosed in full in the prereg).

## Next experiment (one)
**OFFER01: does letting a writer's offer change break the two-value catalogue?**
- One law change, on top of reaim1 (which is kept because it opened the support): when a writer's proposal WINS,
  the writer's own payload becomes the byte it just displaced at the target (a swap of offer and displaced value).
  Everything else is unchanged.
- This targets exactly the measured bound: fixed payloads mean ~2 offers per target.
- Instrument: the AIM02 non-AIM richness meter, as frozen here, plus the offer probe. Compare with reaim1 and the
  same flicker comparators, activity-matched, at N16 and N64.
- Prediction if it works: offered values per target > 2, U rising with window length, late discovery > 0, N64
  material.
- Preregistered falsifier: values merely shuttle between two neighbours (swap 2-cycles). Expect U ~2-3, N64 ~0,
  discovery 0. The cheap attack is a period-2 swap-cycle detector.
- Note: the V2-B TEST-3 "exchange" family is related. It was measured under a different ruler, with recoil, and was
  classed CYCLING. OFFER01 must cite and distinguish it.
