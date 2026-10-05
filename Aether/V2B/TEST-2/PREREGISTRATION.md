# V2-B TEST-2 -- P1 mobility census: is the current Aether medium endogenously mobile?

Thread: TH-P2B-AETHER-V2B, cycle 2 (TH-009 axis). Frozen at the end of DEV-2 and pushed BEFORE any TEST-2 unit runs.
Ladder rung: P1 (ENDOGENOUSLY MOBILE), plus P0 for the new observatory.

## Question
The TH-009 premise, "the aeth01.v1-family medium is largely frozen", has been stated but never measured against the
operator's exclusions: injected perturbation, unconditional counters, trivial cycling, and high turnover without
spread. Does a qualified P1 ruler confirm it for every current law?

## Apparatus (pinned)
- Code: 019c303f79e66f11b3a10ef5bc316e0d3b810f60 (Aether/observatory/aeth_mobility.py on prov0; physics unchanged since 1b4fb4523).
- Ruler qualification: Aether/test/test_aeth_mobility.py. Six synthetic known-answer sequences, each classified
  correctly: frozen, decaying, flip-flop -> CYCLING, unconditional counter -> COUNTER, hot row -> LOCALISED, and a
  travelling pattern -> ENDOGENOUSLY_MOBILE (the calibration positive, not physics).
- World: twin-assay construction (n=128, warm-up 1500 ON), followed window 400 ticks.
- Arms:
  - OFF (no injected perturbation) for v1, add, rcv, fwd, rcv_add, rcv_str, rcv_adr;
  - ON for v1 only, an injected-noise contrast that cannot qualify by rule.
- Seeds 4, 5, 6, 7. 32 units.
- DEV calibration: seed 100 only, used to set the thresholds below and never for a verdict. On seed 100 every OFF law
  was FROZEN or COUNTER.

## Rule (fixed now; aeth_mobility.P1_RULE)
- Per unit, the first failing clause names the class:
  - turnover_late < 0.002 -> FROZEN;
  - turnover_late / turnover_early < 0.5 -> DECAYING;
  - revisit_share > 0.25 -> CYCLING;
  - counter_share > 0.5 -> COUNTER;
  - active_site_share < 0.10 -> LOCALISED;
  - otherwise ENDOGENOUSLY_MOBILE.
- Per law: the class held on at least 3 of 4 seeds; otherwise MIXED.

## Decisions
- **Primary (TH-009 premise, P1, OFF arm, 7 laws):**
  - FROZEN_PREMISE_SUPPORTED if no OFF law is ENDOGENOUSLY_MOBILE on 3 or more seeds and none is MIXED-with-mobile
    (that is, mobile on 2 seeds).
  - FROZEN_PREMISE_REFUTED if any OFF law is ENDOGENOUSLY_MOBILE on 3 or more seeds.
  - PARTIAL otherwise.
  - Mapped to the directive's classes: SUPPORTED -> MECHANISM_SUPPORTED (for the frozen-medium claim); REFUTED ->
    NO_EFFECT for the claim; PARTIAL -> PARTIAL.
- **Contrast:** v1 ON is reported with its class but is not admissible as mobility (injected perturbation).
- Technical failures (an exception, including ProvenanceMismatch; a missing unit; a hash mismatch) are rerun up to 3
  times unchanged.

## Limits declared in advance
- A single 400-tick window after one warm-up and one energy regime (B-balanced).
- counter_share detects constant-step counters only; a counter with a varying step would be missed.
- active_site_share counts any template change, including those inside COUNTER hot spots.
- The thresholds are calibrated on one DEV seed.

## Execution
Fabric script Tasks if the workers are live; otherwise MWO-0004 R3 native fallback on BUCKKEEP (lease buckkeep:cpu8).
About 50 s per unit.
