# V2-B DEV-3 design/repair packet -- first TH-009 mobile-medium law family (mob_r?x?e?)

Cycle 3, DEV window 3 (opened 2026-10-05T03:37Z). Previous TEST: TEST-2 (every current medium FROZEN or COUNTER).

## Limiting layer
The physics. The structural reason for freezing is idempotent writes: a writer keeps writing the same constant
payload through static wiring, so after one write nothing changes. add escapes only by counting. A mobile medium
needs writing to change the WRITER or the WIRING, data-dependently and not by a clock.

## Built
- A bounded enumeration, not a single hand-authored rule. Three binary mechanism switches on the v1 shared path give
  8 laws (Aether/observatory/aeth03_variants.py, `MOB`):
  - r (recoil): a winning write turns its emitter's direction by the displaced byte;
  - x (exchange): a winning write hands the displaced byte back to the emitter's payload;
  - e (energy aim): direction follows energy, as in str.
  - Side effects lose to incoming writes on the same field.
- Each switch has a declared mechanism class and shortcut attack (TEST-3 preregistration).
- Corners: mob_r0x0e0 == v1 and mob_r0x0e1 == str, bit for bit (tests).
- prov0 models the side effects (exchange = COPY node; recoil = ADD node) under the per-tick self-check. The mob laws
  were added to the rich-soup self-check test.
- aeth_mobility gained a warm-up-arm option (review Q4 control).
- Tests: 97 green across the aeth03, provenance and mobility suites.

## Repairs (recorded, not smoothed over)
- **A flag-index bug, caught by hand-worked fixtures.** Both the physics and the shadow read the mechanism switches
  from the wrong character of the law name, so exchange and recoil were never applied, and the per-tick self-check
  PASSED vacuously because both sides agreed on doing nothing.
- Lesson: a shadow self-check proves agreement, not correctness, when the shadow shares the implementer's assumptions.
  The independent, hand-worked fixture tests are what caught it. Fixed in both files; fixtures now pass with the side
  effects active.

## DEV pilot (seed 100; design input only)

| law | P1 class | turnover_late | revisit | counter | active | chain |
|---|---|---|---|---|---|---|
| mob_r0x1e0 / e1 (exchange) | CYCLING | 0.073 / 0.063 | 0.92 | 0.00 | 0.56 / 0.50 | 1.00 |
| mob_r1x0e0 / e1 (recoil) | COUNTER | 0.030 / 0.031 | 0.07 | 0.71 | 0.33 | 0.51 |
| **mob_r1x1e0 / e1 (both)** | **ENDOGENOUSLY_MOBILE** | 0.069 | 0.17 | 0.01 | 0.67 | 0.99 |
| v1, warm-up OFF (Q4) | FROZEN | 0.0006 | 0.78 | 0.00 | 0.013 | 0.08 |

Each switch alone fails exactly where its shortcut attack predicted: exchange cycles, and recoil counts. Together they
pass the P1 ruler. Energy aim changes nothing.

## Frozen next TEST
Aether/V2B/TEST-3/PREREGISTRATION.md.

## Questions for external review
1. Exchange encodes one-hop value movement. Is the P1 mobility of r1x1 nonetheless a legitimate TH-009 result (the
   medium rewrites itself), or does exchange make it a shortcut law for P1 as well?
2. Is "sustained, non-cyclic, non-constant-step, spread-out turnover" enough for P1? Or should P1 require a causal
   test before any law is called mobile?
3. Is chain_share 0.99 (almost every write copies a window-born value) evidence of dynamic structure, or only of
   high turnover?
